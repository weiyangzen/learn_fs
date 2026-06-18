# subset-b-003850 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-fsi.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-fsi.c

Purpose: FSI-attached IBM/OpenPOWER I2C controller driver. It exposes each hardware port as an `i2c_adapter`, polls the FSI engine status instead of using interrupts, and implements controller reset plus generic SCL/SDA recovery through diagnostic line-control registers.

Important APIs/types/functions: `struct fsi_i2c_ctrl` owns the FSI device, FIFO size, adapter list, and controller mutex. `struct fsi_i2c_port` wraps each adapter and current byte count. Core helpers are `fsi_i2c_dev_init()`, `fsi_i2c_set_port()`, `fsi_i2c_start()`, FIFO read/write helpers, `fsi_i2c_wait()`, `fsi_i2c_abort()`, `fsi_i2c_reset_bus()`, `fsi_i2c_reset_engine()`, and `fsi_i2c_xfer()`. Probe/remove are registered through `module_fsi_driver()`.

Control flow: probe initializes the controller, reads `I2C_STAT_MAX_PORT`, locates per-port OF child nodes, and registers adapters. Transfers serialize on `ctrl->lock`, select the port in `I2C_FSI_MODE`, emit a command with start/address/read/stop/length fields, then poll `I2C_FSI_STAT` until data requests, command completion, or an error. Data movement is chunked into FSI FIFO operations limited to at most four bytes, with three-byte operations reduced to two bytes for FSI alignment.

State and persistence: runtime state is in the controller object, port list, FIFO size, selected hardware port, and per-message `xfrd` byte counter. Hardware state persists in mode, watermark, interrupt mask, status, extended status, and port-busy registers. Reset paths reinitialize the controller and restore the selected port.

Dependencies and integration: depends on the FSI device API, OF child nodes, Linux I2C core, `i2c_bus_recovery_info`, jiffies timeouts, endian conversion, and bitfield helpers. It reports `I2C_FUNC_I2C`, protocol mangling, SMBus emulation, and SMBus block data.

Risks: all transfer completion depends on polling and fixed adapter timeouts. Error handling can reset the engine or the full bus and may issue a final STOP only for selected error classes. FIFO size comes from hardware and is used in watermark math, so bogus extended status would affect thresholds. Timeout subtraction uses adapter timeout minus elapsed jiffies per message. Probe skips unavailable OF ports but continues on adapter registration failures.

Test signals: probe should log the port count and create one adapter per available child node. Useful validation includes read/write across multiple FIFO chunks, repeated-start multi-message transfers, NACK mapping to `-ENXIO`, arbitration loss mapping to `-EAGAIN`, SDA-low recovery, port switching, and remove cleanup of every registered adapter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-fsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-gpio.c

Purpose: platform-independent bit-banged I2C adapter using GPIO descriptors. It wires SDA/SCL GPIOs into `i2c-algo-bit`, supports firmware/platform-data timing and open-drain properties, and optionally exposes debugfs fault-injection controls.

Important APIs/types/functions: `struct i2c_gpio_private_data` stores SDA/SCL descriptors, `i2c_adapter`, `i2c_algo_bit_data`, platform data, and optional SCL IRQ completion state. Key functions are `i2c_gpio_setsda_val()`, `i2c_gpio_setscl_val()`, `i2c_gpio_getsda()`, `i2c_gpio_getscl()`, `i2c_gpio_get_properties()`, `i2c_gpio_get_desc()`, `i2c_gpio_probe()`, and `i2c_gpio_remove()`. Fault-injector entry points create debugfs attributes for line forcing, incomplete transfers, arbitration loss, and induced panic.

Control flow: probe reads firmware properties or platform data, requests SDA and SCL as open-drain/high GPIOs unless board data says external handling is present, configures callbacks and default timing, and registers the numbered bit-bang adapter with `i2c_bit_add_numbered_bus()`. If both GPIOs are fast, atomic bit-bang transfers are enabled. Fault injection locks the root adapter before directly toggling lines or temporarily making SCL an IRQ input.

State and persistence: persistent state is the GPIO descriptors, bit algorithm timing, adapter number/name, and optional fault-injection completion data. No hardware state is stored beyond GPIO output direction/value and debugfs files under the adapter.

Dependencies and integration: depends on gpiod consumer APIs, firmware property APIs, platform data ABI, `i2c-algo-bit`, debugfs, IRQ support for optional tests, OF compatible `i2c-gpio`, and ACPI ID `LOON0005`. It is registered at `subsys_initcall` so GPIO I2C buses appear early.

Risks: GPIOs that sleep can distort bus timing. Output-only SCL disables clock-stretch detection and defaults to slower timing. Properties such as `*-has-no-pullup` use push-pull-style flags and rely on external electrical correctness. Fault injection can intentionally wedge the bus or panic the system, so it must stay behind `CONFIG_I2C_GPIO_FAULT_INJECTOR`.

Test signals: adapter creation, correct line names and descriptor acquisition, `i2cdetect`/SMBus emulation over GPIO, clock stretching when `getscl` is present, atomic transfer availability for non-sleeping GPIOs, debugfs fault-injection behavior, and clean adapter removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-gxp.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-gxp.c

Purpose: HPE GXP platform I2C controller driver supporting interrupt-driven master transfers and optional I2C slave mode. It uses per-engine MMIO registers plus a shared syscon interrupt status/enable block.

Important APIs/types/functions: `struct gxp_i2c_drvdata` holds device/MMIO state, `i2c_timings`, engine number, completion, current message pointers, transfer state, and optional slave client. Important functions are `gxp_i2c_start()`, `gxp_i2c_master_xfer()`, `gxp_i2c_restart()`, address/data ACK handlers, `gxp_i2c_slave_irq_handler()`, `gxp_i2c_irq_handler()`, `gxp_i2c_init()`, `gxp_i2c_probe()`, and slave register/unregister hooks when `CONFIG_I2C_SLAVE` is enabled.

Control flow: probe obtains the global syscon map from `hpe,sysreg`, maps the local engine, derives the engine index from the mapped address, requests a shared IRQ, initializes timing/filter registers, enables the global interrupt bit, and registers an adapter. Master transfers set the current message queue, start with address/RW, and wait for completion. The ISR validates the engine bit in global status, handles errors, dispatches slave events when present, or advances the master address/read/write state machine byte by byte.

State and persistence: transfer state is tracked in `state`, `curr_msg`, `msgs_remaining`, `buf`, `buf_remaining`, and `stopped`. Slave registration persists the own-address register and event masks until unregister. The shared `i2cg_map` is static across instances.

Dependencies and integration: depends on platform resources, `regmap` syscon, MMIO accessors, Linux I2C master/slave APIs, firmware timing parsing, and OF compatible `hpe,gxp-i2c`.

Risks: engine identity is inferred from mapped address low bits, which is fragile if mapping assumptions change. The static global syscon map is initialized once without per-device lifetime management. Error interrupts clear all events and complete the active transfer, but timeout does not explicitly reset hardware. Slave and master events share one ISR and state object, so mixed traffic needs hardware validation.

Test signals: successful probe for all engine indices, global interrupt enable masking on probe/remove, multi-message repeated-start reads and writes, address NACK `-ENXIO`, data NACK `-EIO`, shared IRQ filtering, slave read/write/stop callbacks, and timeout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-gxp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-highlander.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-highlander.c

Purpose: Renesas Highlander FPGA SMBus adapter for R0P7780/R0P7785 boards. It supports a narrow SMBus command set through FPGA registers, with interrupt or polling completion and module parameters for mode, timeout, speed, and read delay workarounds.

Important APIs/types/functions: `struct highlander_i2c_dev` stores MMIO base, adapter, command completion, last read time, IRQ, and active buffer. Core functions are `highlander_i2c_setup()`, `highlander_i2c_reset()`, `highlander_i2c_wait_for_bbsy()`, `highlander_i2c_wait_for_ack()`, `highlander_i2c_read()`, `highlander_i2c_write()`, `highlander_i2c_smbus_xfer()`, and `highlander_i2c_probe()/remove()`.

Control flow: probe maps the resource manually, chooses IRQ or polling, configures fast/normal mode, resets the FPGA controller, and registers a numbered HWMON-class adapter. SMBus transfers accept only byte-data and I2C-block-data forms, select an FPGA mode based on transfer length 1/8/16/32, clear old completion, program address and command bytes, then read or write 16-bit data registers and start the transfer.

State and persistence: active transfer state is the buffer pointer/length and completion object. `last_read_time` enforces an optional inter-read delay for FPGA quirks. Hardware state persists in mode/control/address/data registers. Module parameters are global driver state.

Dependencies and integration: depends on platform MMIO resources, optional IRQ, Linux SMBus algorithm hooks, completions, Renesas board platform devices, and HWMON-class client probing through the I2C core.

Risks: transfer support is intentionally limited; arbitrary I2C messages are not supported. Buffer conversion uses fixed `u16 data[16]`, matching the maximum 32-byte mode, so size validation is essential. Polling can busy-loop until timeout. IRQ wait ignores the return value of `wait_for_completion_timeout()` and relies on later ACK checking. Manual allocation/mapping requires explicit unwind correctness.

Test signals: byte and block transfers at supported lengths, unsupported sizes returning `-EINVAL`, forced polling mode, IRQ completion path, ACK abnormality reset path, read-delay workaround, and remove freeing IRQ/MMIO/adapter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-highlander.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-hisi.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-hisi.c

Purpose: HiSilicon Kunpeng/Ascend I2C controller driver. It programs bus timing, fills command FIFOs for multi-message transfers, drains receive FIFO in interrupts, and reports standard I2C plus 10-bit and SMBus-emulated functionality.

Important APIs/types/functions: `struct hisi_i2c_controller` holds adapter, MMIO, clock, IRQ, transfer indices, target address, error bits, timing data, and spike length. Main functions are `hisi_i2c_configure_bus()`, `hisi_i2c_set_scl()`, `hisi_i2c_start_xfer()`, `hisi_i2c_xfer_msg()`, `hisi_i2c_read_rx_fifo()`, `hisi_i2c_irq()`, `hisi_i2c_xfer()`, and `hisi_i2c_probe()`.

Control flow: probe maps registers, disables interrupts, requests IRQ, obtains a clock or `clk_rate` property, computes timing from firmware, registers the adapter, and logs hardware version. A transfer resets software indices, sets address width/address, clears FIFOs and interrupts, enables all interrupts, then waits for completion. TX-empty interrupts enqueue command words with repeated-start and stop bits; RX-full or completion interrupts drain receive data. Transfer completion disables and clears interrupts.

State and persistence: active state includes message indices, buffer indices, `completion`, `msgs`, `msg_num`, and `xfer_err`. Bus timing, clock rate, spike length, and FIFO thresholds persist in registers after probe. There is no runtime PM or remove hook because devm-managed resources dominate lifetime.

Dependencies and integration: depends on platform MMIO, optional clock framework, OF/ACPI IDs, `i2c_parse_fw_timings()`, bitfield helpers, completions, and Linux I2C algorithm callbacks.

Risks: timeout recovery disables interrupts, synchronizes the IRQ, calls generic recovery, and returns `-EIO`; it does not fully reinitialize timing/FIFO registers. Timing arithmetic subtracts fixed controller offsets and can underflow if bad firmware timing or clock values are supplied. Interrupt masking helpers write mask values directly, so hardware mask polarity must remain understood. Errors are collapsed mostly to `-EIO`.

Test signals: probe with clock and `clk_rate` fallback, standard/fast/high-speed timing, 7-bit and 10-bit addressing, combined read/write messages with repeated starts, FIFO threshold behavior, timeout recovery, FIFO error logging, and hardware version log.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-hisi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-hix5hd2.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-hix5hd2.c

Purpose: Hisilicon Hix5hd2 I2C bus driver. It implements interrupt-driven byte sequencing for a 7-bit-address MMIO controller, clock-rate setup, bus-idle checks, controller reset, and runtime PM autosuspend.

Important APIs/types/functions: `enum hix5hd2_i2c_state` models transfer state. `struct hix5hd2_i2c_priv` stores adapter, active message, completion, byte indexes, stop flag, MMIO, clock, spinlock, error, speed, and state. Key functions are `hix5hd2_i2c_init()`, `hix5hd2_i2c_drv_setrate()`, `hix5hd2_i2c_xfer_msg()`, `hix5hd2_i2c_message_start()`, `hix5hd2_i2c_irq()`, read/write handlers, `hix5hd2_i2c_xfer()`, and runtime suspend/resume.

Control flow: probe reads `clock-frequency` with a 100 kHz default and 400 kHz cap, maps MMIO, enables the clock, initializes registers and IRQ handling, enables runtime PM, and registers an adapter. Each message starts by clearing/enabling interrupts, writing the 8-bit address, and issuing START+WRITE. The ISR handles arbitration and NACK errors, advances read or write bytes on OVER interrupts, optionally emits STOP, disables interrupts, and completes the waiter. The outer transfer iterates messages and uses STOP on final or `I2C_M_STOP`.

State and persistence: active message pointer, `msg_idx`, `msg_len`, `stop`, `err`, and `state` persist during a transfer. Clock frequency, SCL high/low registers, and interrupt mask state persist while runtime active. Runtime suspend disables the clock; resume re-enables and reinitializes the controller.

Dependencies and integration: depends on OF compatible `hisilicon,hix5hd2-i2c`, platform MMIO/IRQ, clock framework, runtime PM, completions, spinlocks, and Linux I2C core.

Risks: only 7-bit addressing is supported. `pm_runtime_get_sync()` return is not checked in transfer. Timeouts reset the controller by clock-cycling it, which may affect a shared bus. Rate calculation is simple and assumes sane clock/frequency values. IRQ is requested with `IRQF_NO_SUSPEND`, so PM interactions need platform validation.

Test signals: transfers at default and configured frequencies, multi-message repeated-start behavior, NACK and arbitration error returns, timeout reset path, runtime autosuspend/resume reinitialization, and bus-idle wait after STOP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-hix5hd2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-hydra.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-hydra.c

Purpose: Apple Hydra Mac I/O PCI I2C adapter using bit-banged access to CachePD lines. It is a small legacy driver that maps the Hydra register block and registers a single `i2c-algo-bit` adapter.

Important APIs/types/functions: global `hydra_bit_data` defines `setsda`, `setscl`, `getsda`, `getscl`, `udelay`, and timeout callbacks. `hydra_adap` is the global adapter. `hydra_probe()` maps PCI BAR 0, reserves the CachePD region, clears output-enable bits, and calls `i2c_bit_add_bus()`. `hydra_remove()` clears lines, unregisters the adapter, unmaps BAR memory, and releases the region.

Control flow: setting SDA/SCL high releases the corresponding output-enable bit; setting low clears the data bit and enables the output driver. Reads sample CachePD data bits. Probe uses the Apple Hydra PCI ID, reserves only the CachePD register window, maps the BAR, initializes line state to released, and publishes the adapter.

State and persistence: state is mostly global: the adapter, algorithm data, and mapped Hydra pointer stored in `hydra_bit_data.data`. Hardware state persists in CachePD output-enable and line bits. There is no per-device allocation, PM, or multi-instance isolation.

Dependencies and integration: depends on PCI device matching for Apple Hydra, `asm/hydra.h`, MMIO accessors, `i2c-algo-bit`, and legacy Mac hardware definitions.

Risks: global adapter/data makes the driver effectively single-instance. It does not call `pci_enable_device()`, which may be acceptable for this legacy platform but is unusual. Resource reservation and BAR mapping are manual. Electrical behavior depends on correct interpretation of output-enable bits as open-drain line release.

Test signals: PCI probe on Apple Hydra hardware, line release after probe/remove, successful bit-bang transfers through `i2c_bit_add_bus()`, timeout behavior from `i2c-algo-bit`, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-hydra.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-i801.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-i801.c

Purpose: Intel I801/ICH/PCH SMBus host driver. It supports many PCI IDs, SMBus PEC, block buffer mode, block process calls, I2C block read/write, optional PCI interrupts, SMBus Host Notify, optional board-specific muxes/SPD probing, ACPI ownership arbitration, runtime PM, and iTCO watchdog platform-device creation.

Important APIs/types/functions: `struct i801_priv` stores adapter/MMIO, original PCI/register state, feature flags, interrupt completion/status, byte-by-byte block state, optional mux/TCO devices, ACPI reservation state, and mutex. Core transfer functions are `i801_access()`, `i801_check_pre()`, `i801_transaction()`, `i801_simple_transaction()`, `i801_smbus_block_transaction()`, `i801_i2c_block_transaction()`, byte-by-byte/block-buffer helpers, `i801_isr()`, and Host Notify helpers. Integration functions include optional target probing, mux setup, TCO setup, ACPI OpRegion handling, probe/remove/shutdown, and PM callbacks.

Control flow: probe enables the PCI device without managed disable, resolves IO/MMIO BARs, installs ACPI address-space handling, saves original registers, enables SMBus host mode, clears special modes, requests IRQ if usable, registers optional TCO and I2C adapter, enables Host Notify, then adds mux and optional clients. SMBus operations lock against ACPI, runtime-resume the PCI device, check/clear stale status, configure PEC, dispatch by SMBus transaction type, postprocess errors, clear INUSE/status, and autosuspend. Interrupt mode completes transactions through `done`; byte-by-byte block operations also service BYTE_DONE interrupts.

State and persistence: persistent state includes feature flags from PCI IDs minus user-disabled bits, saved `SMBHSTCFG/HSTCNT/SLVCMD` for restore, ACPI-reserved latch, mux/TCO children, and runtime PM usage. Active transfer state includes block command, read/write flag, count/length/data pointer, completion, and copied status. Register configuration is restored on remove, shutdown, suspend, and resume.

Dependencies and integration: depends on PCI, ACPI, DMI, runtime PM, I2C/SMBus core, Host Notify helpers, i2c-mux-gpio when enabled, platform watchdog data, P2SB for NO_REBOOT, and board-specific DMI tables.

Risks: BIOS/ACPI may claim the SMBus OpRegion at runtime, after which driver transfers return `-EBUSY` and runtime PM is pinned active. Hardware status semantics differ between HSTSTS and AUXSTS. The driver intentionally avoids `pci_disable_device()` due to historical power-off hangs. Optional DMI clients and muxes depend on platform quirks. Block reads use sentinel length state and have recovery paths that must preserve bus consistency.

Test signals: PCI ID feature selection, user `disable_features`, interrupt and polling transfers, PEC errors, block buffer and byte-by-byte block paths, I2C block reads with SPD write-disable behavior, Host Notify events, ACPI OpRegion inhibition, mux child SPD probing, TCO device creation, suspend/resume register restore, and shutdown register restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-i801.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ibm_iic.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ibm_iic.c

Purpose: IBM PPC 4xx IIC controller driver. It handles OF platform discovery, interrupt or polling completion, hardware byte transfers in up-to-four-byte chunks, 7/10-bit addressing, software reset/bus recovery, and SMBus Quick emulation through direct-control bit banging.

Important APIs/types/functions: driver-private state comes from `struct ibm_iic_private` in `i2c-ibm_iic.h`. Key functions are `iic_dev_init()`, `iic_dev_reset()`, `iic_smbus_quick()`, `iic_handler()`, `iic_wait_for_tc()`, `iic_xfer_result()`, `iic_abort_xfer()`, `iic_xfer_bytes()`, `iic_address()`, `iic_xfer()`, `iic_clckdiv()`, `iic_request_irq()`, `iic_probe()`, and `iic_remove()`.

Control flow: probe maps OF MMIO, optionally requests IRQ unless forced polling, chooses fast mode from module parameter or OF property, reads OPB clock frequency, computes divider, initializes registers, and registers an HWMON-class adapter. Transfers validate that all messages share the same address and have nonzero length except SMBus Quick, reset a stuck bus, load the target address, then process each message in chunks of up to four bytes. Completion waits on IRQ wakeups or polling, then checks transfer counts and hardware error bits.

State and persistence: persistent state includes mapped register pointer, waitqueue, adapter, IRQ number, fast-mode flag, and clock divider. Hardware state includes local/remote addresses, mode control, interrupt mask, transfer count, direct-control lines, and status registers. Reset toggles `XTCNTLSS_SRST`, tries to regain bus control by toggling SCL, then reinitializes.

Dependencies and integration: depends on OF address/IRQ APIs, PowerPC `in_8/out_8`, Linux I2C core, waitqueues, module parameters, and the register definitions in `i2c-ibm_iic.h`.

Risks: all messages in a transfer must share address mode/address, which limits arbitrary combined transfers. SMBus Quick bypasses the hardware engine and depends on timing tables and direct-control line ownership. IRQ request failure silently falls back to polling. Error recovery may soft-reset the controller, potentially affecting an in-progress bus peer. Clock divider uses compatibility fallback for missing OPB frequency.

Test signals: standard and fast mode probing, IRQ and forced-poll transfers, 7-bit and 10-bit addressing, chunked reads/writes larger than four bytes, SMBus Quick ACK/NACK behavior, stuck bus recovery, interrupted waits, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ibm_iic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ibm_iic.h -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ibm_iic.h

Purpose: register-layout and private-state header for the IBM PPC 4xx IIC driver. It defines the MMIO register struct, the per-controller software struct, and named bit masks for all controller control/status registers used by `i2c-ibm_iic.c`.

Important APIs/types/functions: `struct iic_regs` maps the IIC register block, including master data buffer, slave buffer, address registers, control/mode/status registers, clock divider, interrupt mask, transfer count, extended control/status, and direct line control. `struct ibm_iic_private` contains `i2c_adapter`, volatile MMIO pointer, waitqueue, controller index, IRQ, fast-mode flag, and clock divider. Macros cover `CNTL_*`, `MDCNTL_*`, `STS_*`, `EXTSTS_*`, `INTRMSK_*`, `XFRCNT_MTC_MASK`, `XTCNTLSS_*`, `DIRCNTL_*`, and `DIRCTNL_FREE()`.

Control flow: the C file includes this header and uses the register struct with `in_8/out_8` to initialize hardware, program target addresses, start transfers, poll or wake on status bits, check errors, reset the controller, and bit-bang direct-control lines for SMBus Quick and recovery.

State and persistence: this header documents all persistent software and hardware state but performs no work itself. The `volatile __iomem` register view is the stable contract between the driver and hardware.

Dependencies and integration: depends only on `<linux/i2c.h>` for adapter type visibility. It is tightly coupled to `i2c-ibm_iic.c` and the IBM PPC 4xx IIC hardware ABI.

Risks: register layout and bit masks must exactly match the hardware; any packing or offset drift would corrupt all operations. `DIRCTNL_FREE()` encodes bus-free ownership assumptions used during reset and SMBus Quick. The private struct exposes fields with no locking primitives besides the waitqueue, so the C file must maintain transfer serialization through the I2C core.

Test signals: compile-time inclusion by `i2c-ibm_iic.c`, successful MMIO register access on PPC 4xx, correct status/error decoding, clock-divider programming, interrupt-mask behavior, and direct-control recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ibm_iic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-icy.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-icy.c

Purpose: Amiga Zorro ICY card I2C driver for a PCF8584-style adapter. It uses `i2c-algo-pcf` in polling mode and auto-instantiates an LTC2990 sensor on known community board addresses.

Important APIs/types/functions: `struct icy_i2c` stores adapter, PCF register pointers S0/S1, and optional LTC2990 client. PCF callbacks are `icy_pcf_setpcf()`, `icy_pcf_getpcf()`, `icy_pcf_getown()`, `icy_pcf_getclock()`, and `icy_pcf_waitforpin()`. Probe/remove are `icy_probe()` and `icy_remove()` under a Zorro driver.

Control flow: probe allocates adapter and PCF algo data, reserves the four-byte Zorro resource, maps S0 at base and S1 at base+2, fills PCF callbacks, calls `i2c_pcf_add_bus()`, logs that IRQ is not implemented, and scans for an LTC2990 at 0x4c-0x4f with a software node describing measurement mode. Remove unregisters the optional client and deletes the adapter.

State and persistence: state is the Zorro MMIO pointers, adapter/algorithm data, and the created LTC2990 client pointer. PCF own address and clock values are fixed callback constants. No IRQ state is maintained.

Dependencies and integration: depends on Amiga/Zorro APIs, `z_readb/z_writeb`, `i2c-algo-pcf`, software nodes/properties for the LTC2990, and Zorro ID `VMC,15,0`.

Risks: IRQ support is intentionally absent because level-triggered Zorro interrupts do not fit `i2c-algo-pcf` expectations and could storm. The automatic sensor scan may instantiate only one matching client and assumes board conventions. The driver reaches into `../algos/i2c-algo-pcf.h`, coupling it to internal algorithm details.

Test signals: Zorro probe, PCF register read/write callbacks, polling I2C transfers, correct adapter naming, LTC2990 auto-detection and property exposure, and remove cleanup of both client and adapter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-icy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-img-scb.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-img-scb.c

Purpose: Imagination Technologies Serial Control Bus I2C adapter. It supports raw line control, atomic low-level I2C commands, automatic FIFO-driven transfers, reset/stop command sequences, timer-assisted abort detection, runtime PM, and system sleep handling.

Important APIs/types/functions: `struct img_i2c` contains adapter, MMIO, clocks, bitrate, completion, spinlock, active message copy, mode, interrupt mask, line-status accumulator, timer, halt state, atomic/sequence state, and raw timeout. Major functions include `img_i2c_switch_mode()`, raw/atomic operation helpers, `img_i2c_read_fifo()`, `img_i2c_write_fifo()`, `img_i2c_auto()`, `img_i2c_atomic()`, `img_i2c_sequence()`, `img_i2c_isr()`, `img_i2c_reset_bus()`, `img_i2c_xfer()`, `img_i2c_init()`, and PM callbacks.

Control flow: probe maps MMIO, gets `sys` and `scb` clocks, requests IRQ, initializes the check timer, reads `clock-frequency`, enables runtime PM, initializes timing registers, performs a reset sequence, and registers a numbered adapter. Transfers reject zero-length reads, choose atomic mode for zero-length writes or `I2C_M_IGNORE_NAK`, runtime-resume the device, copy each message into driver state, clear stale interrupts/line status, start automatic FIFO or atomic operation, wait for completion, delete the timer, and autosuspend. The ISR clears interrupts, accumulates line status, dispatches by mode, handles fatal SCLK-low timeout, and completes only after register access is finished.

State and persistence: mode, interrupt mask, line status, active message copy, transaction halt, timer state, and atomic sequence cursor persist during a transfer. Timing registers, clock/filter setup, and soft-reset state persist while runtime active. Suspend marks `MODE_SUSPEND`; resume reinitializes hardware.

Dependencies and integration: depends on OF compatible `img,scb-i2c`, platform MMIO/IRQ, clock framework, runtime PM, timers, completions, spinlocks, and I2C core.

Risks: the state machine is complex and mode-dependent. Automatic mode intentionally suppresses some interrupts and relies on a 1 ms timer for abort detection. FIFO status reads need a hardware-specific write/read fence on affected revisions. Fatal clock-low timeout switches to `MODE_FATAL`, permanently rejecting future transfers until reinit. Timing math must remain within hardware constraints.

Test signals: standard/fast timing setup, hardware revision rejection, automatic read/write and repeated-start transfers, atomic zero-byte probe transfers, ignore-NACK behavior, reset and stop sequences, abort detection via timer, fatal timeout path, runtime suspend/resume, and system sleep resume reinitialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-img-scb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-imx-lpi2c.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-imx-lpi2c.c

Purpose: NXP/Freescale i.MX LPI2C adapter driver. It supports master transfers through PIO, atomic PIO, or DMA, SMBus block read, optional target/slave mode, bus recovery pinctrl integration, runtime/system PM, SoC-specific clock/IRQ handling, and multiple speed modes up to ultra-fast.

Important APIs/types/functions: `struct lpi2c_imx_struct` owns adapter, clocks, MMIO, transfer buffers/completion, bitrate/FIFO sizes, recovery info, DMA state, optional target client, IRQ, and SoC hwdata. `struct lpi2c_imx_dma` tracks DMA channels, buffers, burst sizing, mappings, and fallback state. Key functions are `lpi2c_imx_config()`, master enable/disable, start/stop, PIO read/write helpers, DMA setup/submit/cleanup, `lpi2c_imx_xfer_common()`, master/target ISRs, target register/unregister, DMA init/exit, probe/remove, and PM callbacks.

Control flow: probe maps resources, gets clocks, reads bitrate, requests IRQ, enables runtime PM, reads FIFO sizes, initializes optional recovery and DMA, then registers the adapter. Transfers enable the master and runtime-resume, issue START for each message, skip payload for SMBus Quick, choose DMA for sufficiently large non-block-read messages when not suspending, otherwise use PIO, wait for completion/polling, wait for TX FIFO empty on writes, issue STOP, check NACK, and disable the master. DMA RX uses both TX DMA for receive-command words and RX DMA for data.

State and persistence: active state includes RX/TX buffers, delivered count, message length, SMBus block flag, completion, DMA mappings, and target pointer. Persistent configuration includes bitrate mode, clock rate, FIFO sizes, recovery info, DMA availability, and SoC hwdata flags. Runtime suspend may free IRQ and disable/unprepare clocks on selected SoCs; resume restores pinctrl/clocks/IRQ. Target mode is reinitialized after noirq resume.

Dependencies and integration: depends on OF match data for imx7ulp/imx8qxp/imx8qm, clock bulk APIs, DMAengine, runtime PM, pinctrl bus recovery, I2C master/target APIs, completions, and MMIO polling helpers.

Risks: DMA has many failure points and only falls back to PIO before DMA actually starts. SMBus block read mutates message length after reading the length byte and must avoid premature controller NACK. `pm_runtime_get_sync()` style paths in related code are avoided here mostly, but PM sequencing is intricate. Target mode shares the IRQ with master mode. Some SoCs free/re-request IRQ during runtime PM, increasing resume failure surface.

Test signals: PIO and DMA read/write thresholds, DMA fallback before start, long RX requiring multiple command words, SMBus block read length validation, atomic transfers during atomic contexts, NACK/arbitration/timeout recovery, target read/write/stop callbacks, bus recovery pinctrl, runtime suspend/resume with IRQ re-request SoCs, and system suspend/resume target reinit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-imx-lpi2c.c -->
