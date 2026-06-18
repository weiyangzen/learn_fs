# Research Group: subset-b-003855

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-rcar.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-rcar.c

Purpose: Renesas R-Car I2C master/slave platform driver for Gen1 through Gen4 controllers. It registers a numbered `i2c_adapter`, supports normal and atomic master transfers, optional slave mode, SMBus host notify on older generations, DMA acceleration, runtime PM, reset control, and bus recovery through generic SCL recovery.

Important APIs/types/functions: `struct rcar_i2c_priv` is the central persistent state: MMIO base, adapter, current `i2c_msg`, wait queue, clock dividers, generation type, DMA channels, reset control, IRQ, slave client, host-notify client, and persistent flag bits. `rcar_i2c_algo` wires `.xfer`, `.xfer_atomic`, `.functionality`, `.reg_slave`, and `.unreg_slave`. Key routines are `rcar_i2c_clock_calculate()`, `rcar_i2c_init()`, `rcar_i2c_bus_barrier()`, `rcar_i2c_master_xfer()`, `rcar_i2c_master_xfer_atomic()`, `rcar_i2c_irq_send()`, `rcar_i2c_irq_recv()`, `rcar_i2c_irq()`, `rcar_i2c_slave_irq()`, and probe/remove/PM callbacks.

Control flow: probe maps registers, gets clock/reset resources, calculates timing from firmware properties, initializes master/slave blocks, selects Gen2 or Gen3 IRQ behavior, registers the adapter, and optionally registers a host-notify slave. Master transfer resumes runtime PM, waits for free SDA or invokes recovery, resets Gen3+ hardware before transfer, initializes registers, lazily requests DMA channels per message, starts the first message, and waits for `ID_DONE`. The IRQ path handles arbitration loss, NACK, STOP, then dispatches to read or write byte/DMA sequencing; Gen2 clears START/STOP immediately because hardware races make lockless interrupt latency important. Atomic transfers poll status and invoke the same IRQ state machine manually.

State and persistence: transient state is in `flags`, `msg`, `msgs_left`, `pos`, `dma_direction`, and wait queue wakeups. Persistent flags include FM+, not-atomic mode, host notify, RXDMA suppression, and PM blocking. DMA state is cleaned on completion or timeout, and Gen3+ RXDMA is limited to one per transfer. Slave registration keeps runtime PM active until unregister.

Dependencies/integration: Linux I2C core, runtime PM, reset controller, DMA engine, firmware timing parser, OF match data, platform resources, and bus recovery callbacks. Hardware timing and generation quirks are encoded in `enum rcar_i2c_type` and compatible table.

Risks: lock-free IRQ sequencing is intentional and fragile; reordering ICMSR/ICMCR writes can create unwanted repeated starts. Clock calculation can underflow if timing assumptions change. DMA needs `I2C_M_DMA_SAFE` and has special read-tail handling. Reset cannot run while slave mode is active. Host notify is disabled on Gen3+ because hard reset would disturb it.

Test signals: exercise Gen1/2 and Gen3/4 transfers, repeated starts after reads, SMBus block reads with `I2C_M_RECV_LEN`, NACK/arbitration/timeout paths, bus recovery, slave read/write/stop events, DMA-safe buffers above `RCAR_MIN_DMA_LEN`, atomic transfers, suspend/resume adapter marking, and multi-master PM-blocked operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-rcar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-riic.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-riic.c

Purpose: Renesas RIIC platform driver. It exposes a full I2C/SMBus-emulation adapter for RIIC variants with different register layouts and interrupt mappings, including fast-mode-plus capable RZ devices and alternate RZ/T2H interrupt aggregation.

Important APIs/types/functions: `struct riic_dev` stores MMIO base, current buffer/message, byte counter, completion, timing data, clock, reset, and variant info. `struct riic_of_data` supplies register-offset tables, IRQ descriptors, IRQ count, and fast-mode-plus capability. The algorithm is `riic_algo` with `riic_xfer()` and `riic_func()`. State-machine interrupts are `riic_tdre_isr()`, `riic_tend_isr()`, `riic_rdrf_isr()`, `riic_stop_isr()`, and `riic_eei_isr()`. Hardware setup and integration are in `riic_init_hw()`, `riic_i2c_probe()`, remove, and PM callbacks.

Control flow: `riic_xfer()` resumes runtime PM, verifies bus free through `riic_bus_barrier()`, clears status, then processes messages in order. Each message starts with TIE enabled and a START or repeated START. `riic_tdre_isr()` writes the address first, then either switches to receive interrupt for reads or streams write bytes until it enables TEIE. `riic_rdrf_isr()` performs the dummy read for reads, controls ACKBT before the last byte, and issues STOP for final reads. `riic_tend_isr()` handles NACK and write completion, either completing for repeated-start continuation or enabling stop interrupt and generating STOP. `riic_stop_isr()` clears status/interrupt enable and completes the message.

State and persistence: `bytes_left == RIIC_INIT_MSG` marks address phase. `err`, `is_last`, `buf`, and `msg` track active transfer state; `msg_done` bridges IRQ completion to the transfer caller. Runtime PM uses autosuspend delay zero by default. Reset is optional and deasserted for operation, asserted during suspend_noirq after disabling output.

Dependencies/integration: I2C core, OF match data, runtime PM, reset controller, firmware timing parser, `i2c_generic_scl_recovery`, platform IRQ resources, and byte-wide MMIO. Register maps are abstracted by indexed offsets, allowing RZ/A-style and RZ/V2H-style layouts.

Risks: transfer correctness depends on IRQ ordering and on using RDRFS/ACKBT for every received byte to avoid races. `riic_init_hw()` timing math must account for rise/fall times and 5-bit BRL/BRH bounds. Suspend/resume deliberately wakes the controller before late suspend because some devices need noirq I2C access. Error paths rely on ACPI-like package-independent IRQ clearing reads to ensure register writes propagate.

Test signals: verify quick/zero-length write behavior, read lengths of 1 and multiple bytes, NACK path through NAKIE/EEI, repeated starts across multi-message transfers, bus recovery when BBSY or pins are stuck low, FMP timing rejection/enablement, RZ/T2H EEI dispatch, runtime autosuspend, and suspend_noirq/resume_noirq reset restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-riic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-rk3x.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-rk3x.c

Purpose: Rockchip RK3xxx-family I2C platform driver. It supports multiple SoCs, normal and atomic/polling transfers, combined register-read acceleration, clock-rate notifier timing updates, and GRF configuration for controllers with selectable new/old interfaces.

Important APIs/types/functions: `struct rk3x_i2c` keeps adapter, device, SoC timing callbacks, MMIO, clocks, notifier, IRQ, parsed timings, spinlock, wait queue, active message, mode, state, processed count, and error. `struct rk3x_i2c_soc_data` selects GRF offset and either `rk3x_i2c_v0_calc_timings()` or `rk3x_i2c_v1_calc_timings()`. `rk3x_i2c_algorithm` exposes `.xfer`, `.xfer_atomic`, and functionality. Transfer control is in `rk3x_i2c_setup()`, `rk3x_i2c_start()`, IRQ handlers for start/write/read/stop, and `rk3x_i2c_xfer_common()`.

Control flow: probe parses firmware timings, configures GRF if needed, gets clocks/IRQ, registers a clock notifier, computes dividers, and adds the adapter. `rk3x_i2c_xfer_common()` enables clocks and loops through messages. `rk3x_i2c_setup()` either lets hardware handle a short write followed by read using MRXADDR/MRXRADDR, or sets plain TX/RX mode per message. The start IRQ disables START and transitions to write or read. Write IRQ fills up to the 32-byte transmit buffer; read IRQ drains up to 32-byte receive chunks and schedules the next chunk. Stop IRQ clears STOP and wakes waiters. Atomic mode disables the IRQ line and polls by calling the IRQ handler.

State and persistence: persistent SoC data chooses timing formula and GRF behavior. Active transfer state is guarded by `lock` and represented by `busy`, `state`, `msg`, `processed`, `is_last_msg`, and `error`. Clock notifier state persists so divider changes track rate transitions pre/post/abort.

Dependencies/integration: Linux I2C core, platform/OF, clk framework including notifiers, syscon/regmap for GRF, spinlocks/wait queues, and MMIO FIFOs. Functionality advertises I2C, SMBus emulation, and protocol mangling.

Risks: hardware cannot do true repeated START; driver approximates it by resetting internal state and issuing a new START. Combined register-read mode only supports writes shorter than four bytes before a read. NACK handling must respect `I2C_M_IGNORE_NAK`. Timing calculations are complex and can silently clamp when target rate is unreachable. Clock notifier updates dividers under lock and enabled pclk; misuse can race with active transfers.

Test signals: test write, read, multi-chunk >32-byte reads/writes, short write-read combined transfers, fallback repeated-start sequencing, NACK with and without ignore flag, timeout forced STOP, atomic polling, GRF setup on rv1126/rk3066/rk3188, v0/v1 timing edge rates, clock rate changes, and suspend/resume divider reprogramming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-rk3x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-robotfuzz-osif.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-robotfuzz-osif.c

Purpose: USB-to-I2C bridge driver for the RobotFuzz OSIF adapter. It registers an I2C adapter over USB vendor control messages and exposes I2C plus SMBus emulation.

Important APIs/types/functions: `struct osif_priv` stores the USB device/interface, I2C adapter, and last status byte. USB helpers are `osif_usb_read()` and `osif_usb_write()`, using vendor interface control requests. `osif_xfer()` implements the adapter transfer loop, `osif_func()` advertises functionality, `osif_probe()` sets bit rate and registers the adapter, and `osif_disconnect()` removes it. `osif_quirks` rejects zero-length reads because they would create invalid control messages.

Control flow: probe allocates private state, binds it to the USB interface, fills adapter fields, sends `OSIFI2C_SET_BIT_RATE` with divider 52 for roughly 100 kHz, registers the adapter, and logs firmware version. Every I2C message is translated to `OSIFI2C_READ` or `OSIFI2C_WRITE`, followed unconditionally by `OSIFI2C_STOP` and a status read through `OSIFI2C_STATUS`. A non-ACK address status or short USB transfer returns `-EREMOTEIO`.

State and persistence: there is no persistent bus state beyond adapter registration, the USB device pointer, and `priv->status`. The firmware owns actual bus sequencing and status. The driver sends STOP after each message, so Linux multi-message repeated-start semantics are not preserved.

Dependencies/integration: USB core, I2C core, control endpoint zero, HWMON class scanning, and the OSIF vendor protocol. It uses managed allocation for private state, while adapter lifetime is explicit through `i2c_add_adapter()`/`i2c_del_adapter()`.

Risks: `osif_probe()` does not check the return value from `i2c_add_adapter()`, so registration failure would still report success. Forced STOP after every message can break clients requiring repeated starts. USB control timeout is fixed at 2000 ms. Status interpretation only accepts `STATUS_ADDRESS_ACK`; all other firmware states collapse to `-EREMOTEIO`.

Test signals: plug/unplug lifecycle, adapter registration failure injection, read/write short USB transfers, address NAK status, bit-rate command failure, zero-length read rejection, SMBus emulation that does not require repeated starts, and behavior on USB disconnect during active transfer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-robotfuzz-osif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-rtl9300.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-rtl9300.c

Purpose: Realtek RTL9300/RTL9310/RTL9607 regmap-backed SMBus controller driver. It creates one I2C adapter per child SDA channel, multiplexes channel selection through SoC registers, and supports SMBus byte/word/block transactions.

Important APIs/types/functions: `struct rtl9300_i2c` stores shared regmap, channel array, regmap fields, base offsets, selected SCL/SDA, mutex, and optional clock. `struct rtl9300_i2c_chan` stores per-adapter bus frequency/SDA/clock divider. Variant behavior is in `struct rtl9300_i2c_drv_data`, including field descriptors, channel config, clock config, init function, data registers, max channels, max data length, and register-address length. Main routines are `rtl9300_i2c_prepare_xfer()`, `rtl9300_i2c_do_xfer()`, `rtl9300_i2c_smbus_xfer()`, `rtl9300_i2c_config_chan()`, `rtl9607_i2c_config_chan()`, and probe.

Control flow: probe obtains the parent syscon regmap, reads `reg` and `realtek,scl`, allocates regmap fields with master/global scoping, enables the optional clock, iterates child nodes into adapters, configures per-channel clock settings, adds each adapter with devm cleanup, then runs variant init. Each SMBus transfer locks the shared controller, selects/configures the requested channel, builds an internal xfer object from SMBus size/read-write, writes device/register/data fields, triggers the hardware, polls `F_BUSY`, checks `F_I2C_FAIL`, and reads back data for read operations.

State and persistence: shared hardware state is serialized by `lock`. `sda_num` caches the selected SDA to avoid redundant channel programming. Per-channel frequency configuration persists in `rtl9300_i2c_chan`. There is no IRQ state; transfers are synchronous polling transactions.

Dependencies/integration: I2C core SMBus algorithm, platform/OF child nodes, syscon/regmap fields, optional clk, unaligned helpers, and adapter quirks. Functionality is SMBus-only; quirks mark no clock stretching, no zero-length transfers, and max read/write lengths of 16.

Risks: block-data handling uses `data->block[0] + 1` for SMBus block writes, so max-length SMBus block data can exceed the 16- or 4-byte hardware limits and is rejected. RTL9607 max data length is only 4. Incorrect child count or SDA numbers can misprogram the mux. `rtl9607_i2c_config_clock()` divides by requested frequency without validation for zero. Errors are reported generically as `-EIO` on fail bit.

Test signals: per-compatible field layout smoke tests, multiple child channels with different clocks, channel switch caching, SMBus byte/byte-data/word/block and I2C-block reads/writes, max-length rejection, busy timeout, fail-bit handling, optional clock absence, RTL9607 4-byte limit, and invalid child-count/device-tree properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-rtl9300.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-rzv2m.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-rzv2m.c

Purpose: Renesas RZ/V2M I2C master platform driver. It provides a synchronous completion-based I2C adapter with 7-bit and 10-bit addressing, standard/fast-mode timing setup, runtime PM, and shared reset deassertion.

Important APIs/types/functions: `struct rzv2m_i2c_priv` holds MMIO base, adapter, clock, selected bus mode, completion, and precomputed low/high width registers. `bitrate_configs` encodes low-period ratio and max data hold time for 100 kHz and 400 kHz. Main routines are `rzv2m_i2c_clock_calculate()`, `rzv2m_i2c_init()`, `rzv2m_i2c_write_with_ack()`, `rzv2m_i2c_read_with_ack()`, `rzv2m_i2c_send_address()`, `rzv2m_i2c_xfer_msg()`, `rzv2m_i2c_xfer()`, probe/remove, and suspend/resume.

Control flow: probe maps resources, gets clock/reset/IRQ, deasserts shared reset, registers the TIA interrupt completion handler, calculates timing, enables runtime PM, initializes hardware, and registers a numbered adapter. `rzv2m_i2c_xfer()` resumes runtime PM, rejects a busy bus via `IICB0SSBS`, then sends each message with START, address bytes, data send/receive, and STOP only on the last message. Writes wait for completion and require ACK. Reads manipulate `IICB0SLWT` and `IICB0SLAC` so the final byte receives NACK and a 9th-clock completion.

State and persistence: transfer state is minimal and stack-driven; completion `msg_tia_done` serializes byte progress. Timing values persist in `iicb0wl/iicb0wh` and are recalculated on resume. Runtime PM autosuspend is used after transfers. Reset is shared and only deasserted because it affects non-Linux hardware.

Dependencies/integration: I2C core, firmware timing parser, platform MMIO/IRQ, clk framework, runtime PM, reset controller, `readl_poll_timeout()`, and numbered adapter registration. Functionality excludes SMBus quick and advertises 10-bit address support.

Risks: only exact 100 kHz and 400 kHz firmware frequencies are accepted. Multi-message transfer issues START for each message and STOP only at the end, which may or may not match repeated-start expectations depending on hardware behavior. Timeout or non-NACK errors reinitialize the controller. Shared reset cannot be asserted for recovery. `rzv2m_i2c_disable()` resumes PM only to clear enable, so PM failures block removal/suspend cleanup.

Test signals: 7-bit write/read, 10-bit address high/low bytes, final-byte NACK behavior, multi-message transfer without intermediate STOP, busy-bus `-EAGAIN`, NACK stop handling, timeout reinitialization, invalid timing rejection, runtime PM resume failure, suspend disable/resume reinitialize, and no-zero-length quirk enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-rzv2m.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-s3c2410.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-s3c2410.c

Purpose: Samsung S3C24xx/S3C2440/Exynos legacy I2C controller driver. It supports platform data and device tree, interrupt and polling variants, atomic transfers, old HDMIPHY quirks, clock divisor setup, and noirq suspend/resume restoration.

Important APIs/types/functions: `struct s3c24xx_i2c` stores wait queue, quirk flags, current message set, IRQ, state, clock, MMIO, adapter, platform data, optional GPIOs/pinctrl, and Exynos sysreg state. The algorithm exposes `s3c24xx_i2c_xfer()`, `s3c24xx_i2c_xfer_atomic()`, and functionality. Core state logic is in `s3c24xx_i2c_message_start()`, `i2c_s3c_irq_nextbyte()`, `s3c24xx_i2c_stop()`, `s3c24xx_i2c_doxfer()`, `s3c24xx_i2c_clockrate()`, and probe/PM callbacks.

Control flow: probe gathers platform/DT timing data, configures GPIO/pinctrl, maps registers, prepares clock, initializes controller, optionally requests IRQ, enables runtime PM, and registers a numbered adapter. Transfer enables the clock, retries on `-EAGAIN`, waits for master ownership, initializes message pointers/state, enables IRQ, emits START/address, and then either waits on IRQ completion or polls `is_ack()` plus `i2c_s3c_irq_nextbyte()` for polling/atomic quirks. The IRQ state machine handles address ACK, read/write byte flow, SMBus block receive length extension, NOSTART write continuation, repeated START between messages, STOP, and error completion.

State and persistence: active transfer state is in `msg`, `msg_num`, `msg_idx`, `msg_ptr`, and `state`. Quirk flags select S3C2440 timing/filter register, HDMIPHY stop workaround, no-GPIO mode, polling mode, and temporary atomic mode. Clock rate and sysreg mux state persist across suspend/resume.

Dependencies/integration: Linux I2C core, platform data `i2c-s3c2410.h`, OF properties, clk, GPIO descriptors, pinctrl, regmap/syscon for Exynos interrupt mux, runtime PM, and subsystem init registration.

Risks: HDMIPHY intentionally skips a normal STOP by disabling serial output to avoid extra transfers. `I2C_M_NOSTART` only works for write-to-write continuation; write-to-read without START returns `-EINVAL`. Arbitration loss is logged but not fully converted into transfer state in the IRQ path. Atomic mode mutates the shared `quirks` field while IRQ is disabled. Timing setup uses older platform properties and can reject unreachable rates.

Test signals: normal interrupt transfers, polling Exynos SATA PHY variant, atomic xfer, zero-length probe write, SMBus block read length validation, NOSTART write chaining and invalid read transition, missing ACK mapping, HDMIPHY stop behavior, bus-id/platform-data path, DT sysreg mux save/restore, and suspend/resume adapter marking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-s3c2410.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-scmi.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-scmi.c

Purpose: ACPI SMBus CMI adapter driver. It exposes an SMBus-only I2C adapter by calling ACPI control methods (`_SBI`, `_SBR`, `_SBW`, or IBM alternate names) on firmware-described SMBus controllers.

Important APIs/types/functions: `struct acpi_smbus_cmi` stores ACPI handle, adapter, read/write/info capability bits, and method-name table. `acpi_smbus_cmi_access()` is the SMBus transfer implementation. `acpi_smbus_cmi_func()` advertises functions based on discovered methods. `acpi_smbus_cmi_add_cap()` evaluates the info method and records method capabilities. `acpi_smbus_cmi_query_methods()` is the namespace walker callback. `smbus_cmi_probe()` and remove manage adapter lifetime.

Control flow: probe allocates state, gets the ACPI match data method table, walks one namespace level for ACPI methods, requires the info method, fills adapter metadata, and registers it. Transfers map Linux SMBus sizes to ACPI protocol constants and method arguments. Reads call the read method with protocol/address/command; writes call the write method with protocol/address/command/length/value-or-buffer. Returned ACPI packages are validated, status is mapped to Linux errno, and read payloads are copied into `union i2c_smbus_data`.

State and persistence: capability bits persist after probe. There is no hardware state in the driver; firmware methods own serialization and controller state. ACPI result buffers are allocated per transfer and freed before return.

Dependencies/integration: ACPI namespace/method evaluation, platform driver ACPI match table, I2C SMBus algorithm, HWMON class scanning, and firmware-specific CMI package contracts.

Risks: correctness depends entirely on firmware package shape and status values. Block-read protocol validates returned length but returns `-EPROTO` before freeing the ACPI buffer in one invalid-length path, which is a leak risk. The expression in functionality setup relies on operator precedence for read/write capability quick support. Unsupported ACPI status codes collapse to `-EIO`. Method discovery tolerates unsupported names but requires the info method.

Test signals: ACPI devices with standard, IBM, and Microsoft HIDs; absent info method; read-only/write-only capability sets; all supported SMBus sizes; malformed package/object types; status mappings for busy/timeout/DNAK/failure; block length zero/overflow; and adapter cleanup after registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-scmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-sh7760.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-sh7760.c

Purpose: SuperH SH7760 I2C controller driver using FIFO and interrupt-driven master transfers. It registers a numbered adapter from platform data and supports I2C plus SMBus emulation except quick.

Important APIs/types/functions: `struct cami2c` holds MMIO base, adapter, current message, transfer flags/status, completion, IRQ, and reserved IO resource. Register helpers are `OUT32()` and `IN32()`. Transfer and IRQ routines are `sh7760_i2c_mrecv()`, `sh7760_i2c_msend()`, `sh7760_i2c_irq()`, `sh7760_i2c_master_xfer()`, `calc_CCR()`, probe, and remove.

Control flow: probe requires `struct sh7760_i2c_platdata`, reserves/remaps MMIO, gets IRQ, initializes registers/FIFOs, calculates CCR from platform speed, requests IRQ, and registers the adapter. Each transfer checks bus busy, iterates messages, sets STOP on the final message, initializes completion, starts receive or send, waits for completion, retries arbitration loss, and cleans master/slave registers after the batch. IRQ handles arbitration loss, NACK with hardware-mandated delays and stop sequencing, STOP completion, address-sent transition, RX FIFO draining with trigger adjustment, and TX FIFO filling until TEND/STOP.

State and persistence: this driver mutates `msg->buf` and `msg->len` while transferring, so active message state is destructive and must not be reused after a partial transfer. `flags` record send/receive/stop, while `status` records done/arbitration/NACK. Completion `xfer_done` serializes IRQ to caller. Static hardware setup persists until removal.

Dependencies/integration: platform resources, legacy `<asm/clock.h>` and `<asm/i2c-sh7760.h>`, I2C core, raw MMIO, IRQs, and manually managed `request_mem_region()`/`ioremap()` resources.

Risks: NACK handling is explicitly timing-sensitive; writing registers too soon can lock the controller, and later transfers require a delay. There is no timeout around `wait_for_completion()`, so a missed IRQ can hang the caller. Destructive mutation of `i2c_msg` fields is unusual and risky. `calc_CCR()` depends on a global `peripheral_clk`. Recovery is limited to register reset after transfer.

Test signals: platform-data absence, invalid speed rejection, send/receive FIFO trigger boundaries around 16 bytes, multi-message no-stop handoff, NACK delay path, arbitration retry exhaustion, stuck/no IRQ behavior, busy bus `-EBUSY`, and resource cleanup on probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-sh7760.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-sh_mobile.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-sh_mobile.c

Purpose: SuperH Mobile/R-Mobile/R-Car IIC controller driver. It supports interrupt and atomic transfers, optional DMA, variant-specific timing setup, R8A7740 erratum workaround, runtime PM, and noirq suspend adapter marking.

Important APIs/types/functions: `struct sh_mobile_i2c_data` stores device, MMIO, adapter, timing, clock, ICIC flags, lock/wait queue, current message position/status, STOP/DMA state, DMA channels, resource, and bounce buffer. `enum sh_mobile_i2c_op` models byte-level operations. Main routines are `sh_mobile_i2c_init()`, `sh_mobile_i2c_v2_init()`, `i2c_op()`, `sh_mobile_i2c_isr_tx()`, `sh_mobile_i2c_isr_rx()`, `sh_mobile_i2c_isr()`, DMA helpers, `start_ch()`, `sh_mobile_xfer()`, probe/remove, and PM callbacks.

Control flow: probe gets clock, hooks one or more IRQs, maps registers, parses `clock-frequency`, detects extra ICIC bits by resource size, initializes timing under runtime PM, initializes DMA channel placeholders, fills adapter, and registers it. Transfer resumes PM, processes messages, decides whether to emit START, prepares channel and optional DMA buffer, kicks START, then waits for IRQ or polls in atomic mode. ISR records status, starts DMA after address preface when applicable, handles arbitration/TACK non-destructively until STOP, dispatches TX/RX byte sequencer, clears WAIT, and wakes on software done. After each message, the caller polls busy or DTE depending on STOP/repeated-start behavior, disables the channel, and drops PM.

State and persistence: state includes `pos` where `-1` is address phase and RX real position is `pos - 2`; `sr` accumulates status flags; `send_stop` controls STOP versus repeated-start; `stop_after_dma` indicates successful DMA completion for buffer sync. DMA channels persist and are released at remove.

Dependencies/integration: I2C core, OF compatible data, clk/runtime PM, DMA engine, scatterlist/dma mapping, platform IRQ resources, wait queues/spinlocks, and `i2c_get_dma_safe_msg_buf()`.

Risks: byte sequencing is tightly coupled to documented WAIT/DTE order. DMA is skipped in atomic mode and only starts after the address preface. Timeout cleanup must terminate DMA if active. Polling for DTE/busy maps TACK to `-ENXIO` and arbitration loss to `-EAGAIN`; missed status accumulation could misreport. R8A7740 workaround directly toggles pads and timing.

Test signals: 0/1/multi-byte writes, 1/2/>3-byte reads, repeated-start multi-message transfer, explicit `I2C_M_STOP`, atomic path, DMA read/write over threshold, NACK/TACK and arbitration loss, timeout with active DMA, variants with ICIC67 timing bits, R8A7740 workaround, multiple IRQ resources, and suspend/resume adapter state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-sh_mobile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-sibyte.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-sibyte.c

Purpose: SiByte board SMBus adapter driver. It registers two fixed numbered SMBus adapters backed by SB1250 CSR registers, one at 100 kHz and one at 400 kHz.

Important APIs/types/functions: `struct i2c_algo_sibyte_data` records private data, bus number, and CSR base. `smbus_xfer()` implements SMBus quick, byte, byte-data, and word-data operations by writing SB1250 command/start/data registers. `bit_func()` advertises functionality. `i2c_sibyte_add_bus()` assigns the algorithm, sets frequency/control registers, and registers the adapter. Static arrays define the two adapters and their CSR bases.

Control flow: module init registers adapter 0, then adapter 1; failure to add the second removes the first. Each transaction busy-waits while `M_SMB_BUSY`, programs command/data fields according to SMBus size and direction, writes `R_SMB_START`, busy-waits again, clears and maps errors, and copies one or two returned bytes from `R_SMB_DATA`.

State and persistence: adapters and algo data are static globals. Hardware base addresses are fixed CKSEG1 CSR addresses. There is no locking, timeout, interrupt handling, or dynamic device discovery in this driver.

Dependencies/integration: MIPS SiByte headers and CSR accessors, Linux I2C SMBus algorithm, HWMON class scanning, and module init/exit.

Risks: busy waits have no timeout and can spin forever if hardware remains busy. Only a subset of SMBus is supported; no block or process-call support. Fixed adapter numbers and static globals assume a narrow board environment. Error mapping depends on `M_SMB_ERROR_TYPE` only.

Test signals: module init/exit cleanup, both bus frequencies, quick/byte/byte-data/word-data read/write, SMBus error and NACK mapping, adapter numbering collisions, and behavior if busy never clears.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-sibyte.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-simtec.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-simtec.c

Purpose: Simtec generic memory-mapped bit-banged I2C bus driver. It exposes a simple two-line GPIO-like hardware register through `i2c-algo-bit`.

Important APIs/types/functions: `struct simtec_i2c_data` stores IO resource, mapped register, adapter, and `i2c_algo_bit_data`. Bit operations are `simtec_i2c_setsda()`, `simtec_i2c_setscl()`, `simtec_i2c_getsda()`, and `simtec_i2c_getscl()`. Probe/remove manage resource reservation, mapping, bit algorithm setup, and adapter registration.

Control flow: probe allocates state, records platform driver data, gets the memory resource, reserves and maps it, fills adapter fields, wires bit callbacks and timing (`udelay = 20`, `timeout = HZ`), then calls `i2c_bit_add_bus()`. The algorithm bit-bangs START/STOP/address/data using callbacks that write `CMD_SET_SDA` or `CMD_SET_SCL` plus desired state bits to the register and read line state bits back. Remove unregisters the adapter and releases IO resources.

State and persistence: all bus state is represented by the external hardware latch/line state and the bit-algo core. Driver state is per-platform-device and manually allocated/freed. There is no interrupt, PM, or transfer-specific state in this file.

Dependencies/integration: platform resources, MMIO byte access, I2C core, `i2c-algo-bit`, and module platform driver registration.

Risks: manual resource management requires all probe failure paths to free the correct resource. There is no device-tree match table or PM handling. The single register protocol assumes writes with command bits atomically update one line without disturbing the other. Bit-banged timing is fixed and may be too slow/fast for some boards.

Test signals: successful bit-bus registration, SDA/SCL set/get line transitions, arbitration/clock-stretch behavior through `i2c-algo-bit`, IO resource conflict, ioremap failure, adapter registration failure cleanup, and remove cleanup after active clients are gone.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-simtec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-sis5595.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-sis5595.c

Purpose: Legacy SiS5595 SMBus driver. It detects the real 5595-compatible PCI function while excluding many later incompatible SiS devices exposing the same PCI ID, reserves indexed ACPI/SMBus IO ports, and registers an SMBus adapter.

Important APIs/types/functions: global `sis5595_base`, `sis5595_pdev`, and static `sis5595_adapter` represent the singleton controller. `sis5595_read()`/`sis5595_write()` access indexed registers through `SMB_INDEX`/`SMB_DAT`. `sis5595_setup()` validates blacklist, base address, ACPI region, force address, and ACPI enable bit. `sis5595_transaction()` runs one SMBus command. `sis5595_access()` maps Linux SMBus operations to hardware protocol constants. Probe/init/exit handle PCI registration and unusual adapter lifetime.

Control flow: module registers a PCI driver for SiS 503. Probe calls setup, fills adapter parent/name, registers the adapter, stores a PCI device reference, then deliberately returns `-ENODEV` so other drivers can bind the PCI function. Transfers program address/command/data registers, write protocol type to control, call transaction, and read byte/word results for read or process-call operations.

State and persistence: singleton global base address and adapter persist until module exit. `force_addr` module parameter can override hardware base programming. The driver does not bind normally to the PCI device; cleanup depends on `sis5595_pdev` being held after the intentionally failing probe.

Dependencies/integration: PCI config access, ACPI region conflict checks, IO port access, I2C SMBus algorithm, HWMON class, module parameters, and manual region release.

Risks: singleton design cannot support multiple devices. Probe’s intentional failure is non-obvious and fragile. The indexed two-port reservation may still interfere with ACPI firmware. Block transfers are not implemented despite hardware support. Bus collision warning says the SMBus may remain locked until hard reset. Force address is explicitly risky.

Test signals: blacklist detection, uninitialized ACPI base with/without `force_addr`, ACPI conflict, ACPI enable bit write/readback, quick/byte/byte-data/word/process-call transfers, busy reset path, timeout, failed transaction, bus collision, intentional probe return semantics, and module exit cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-sis5595.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-sis630.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-sis630.c

Purpose: Legacy SiS630/730/760/964 SMBus driver. It registers a singleton SMBus adapter after locating compatible SiS host hardware, enabling ACPI access, deriving the SMBus IO base, and reserving the IO register range.

Important APIs/types/functions: global `smbus_base` is the active IO base. Module parameters are `high_clock` and `force`. Register helpers are `sis630_read()`/`sis630_write()`. Transactions are split into `sis630_transaction_start()`, `sis630_transaction_wait()`, `sis630_transaction_end()`, and `sis630_transaction()`. `sis630_block_data()` handles multi-stage block reads/writes. `sis630_access()` maps Linux SMBus sizes to hardware protocol constants. `sis630_setup()`, probe, and remove manage PCI/IO integration.

Control flow: setup checks for supported SiS devices or force mode, enables ACPI through PCI BIOS control, reads ACPI base, chooses offset 0xE0 for SiS760 and 0x80 otherwise, checks ACPI conflicts, and reserves 20 IO ports. A transfer writes address/command/data/count registers, then runs transaction. Transaction start kills any busy transaction, saves old clock, optionally selects high clock, clears status, and starts the command. Wait polls status/error/collision/byte-done for block mode. End clears sticky status and restores clock. Block transfer streams data in 8-byte windows using `BYTE_DONE_STS`.

State and persistence: singleton static adapter and `smbus_base` persist while bound. `high_clock` temporarily changes host clock and restores it from `oldclock`; `force` bypasses detection. No IRQs or PM state are used.

Dependencies/integration: PCI, ACPI region checks, IO ports, I2C SMBus algorithm, HWMON class, and module PCI driver lifecycle.

Risks: singleton only. Force mode may operate on unsupported hardware. Block transfer logic is complex and depends on sticky byte-done clearing between 8-byte windows. The supported-chip scan uses global PCI search independent of the probed device. Clock changes are global to the SMBus controller. Timeout and collision recovery are limited.

Test signals: supported-device detection, force mode, SiS760 offset selection, ACPI conflict, high_clock restore, quick/byte/byte-data/word/process-call/block transfers, block lengths over 32 clamping, busy kill failure, timeout, collision `-EAGAIN`, device error `-ENXIO`, probe/remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-sis630.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-sis96x.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-sis96x.c

Purpose: Legacy SiS96x SMBus PCI driver. It exposes one SMBus adapter for PCI devices with SiS SMBus class/resource setup, relying on PCI quirks on many machines to expose the BAR correctly.

Important APIs/types/functions: global `sis96x_smbus_base` and `sis96x_adapter` implement the singleton controller. `sis96x_read()`/`sis96x_write()` access IO registers. `sis96x_transaction()` performs busy reset, clock/timeout setup, command start, polling, error mapping, and status cleanup. `sis96x_access()` maps Linux SMBus quick/byte/byte-data/word/process-call operations to hardware registers. Probe/remove register and tear down the adapter.

Control flow: probe rejects a second device, verifies PCI class `PCI_CLASS_SERIAL_SMBUS`, obtains BAR0, checks ACPI resource conflict, reserves the IO range, fills adapter parent/name, and registers the adapter. Transfers program address/command/data registers, select the protocol size, run the transaction, and read byte/word return data when applicable.

State and persistence: only one adapter/base can exist. There is no interrupt, DMA, PM, or per-transfer persistent state beyond programmed IO registers. Each transaction forces SMBus control to disable timeout interrupts and select fast host clock.

Dependencies/integration: PCI core, ACPI resource conflict checking, IO port access, I2C SMBus algorithm, HWMON class, and module PCI driver registration.

Risks: marked beta and based on SiS630 definitions without datasheet. No block data support despite constants. Busy reset may fail and return `-EBUSY`; collision maps to `-EIO`. Singleton design prevents multiple controllers. BAR setup relies on external PCI quirks for many systems. Status cleanup writes back the observed status and only logs if sticky bits remain.

Test signals: class mismatch rejection, missing BAR, ACPI conflict, IO reservation conflict, duplicate-device rejection, quick/byte/byte-data/word/process-call transfers, timeout, device error, collision, sticky status cleanup, and remove cleanup resetting `sis96x_smbus_base`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-sis96x.c -->
