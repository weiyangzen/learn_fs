# subset-b-003856 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-sprd.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-sprd.c

Purpose: implements the Spreadtrum SC9860 I2C controller as a Linux platform I2C adapter. It maps the controller registers, programs 100 kHz or 400 kHz timing, drives FIFO-based master transfers, and integrates with runtime/system power management.

Important APIs/types/functions: `struct sprd_i2c` holds adapter, MMIO base, clocks, active `i2c_msg`, transfer buffer/count, IRQ, completion, and error state. The public adapter hooks are `sprd_i2c_xfer()` and `sprd_i2c_func()` via `sprd_i2c_algo`. Transfer helpers program count/address/mode/stop, feed or drain FIFOs, and wait on `complete`. `sprd_i2c_isr()` masks FIFO interrupts and wakes the threaded handler; `sprd_i2c_isr_thread()` continues FIFO movement or completes with `0`/`-EIO`. Probe/remove and PM entry points are `sprd_i2c_probe()`, `sprd_i2c_remove()`, runtime suspend/resume, and noirq system suspend/resume.

Control flow: probe allocates private state, maps registers, obtains IRQ and clocks, validates `clock-frequency`, enables the clock, initializes timing/FIFO/interrupts, requests a threaded IRQ, and registers a numbered adapter. Each transfer resumes runtime PM, sends all messages in order, and keeps STOP disabled for intermediate write messages. `sprd_i2c_handle_msg()` resets FIFO, configures address/count/direction, preloads write data or enables RX full interrupts, starts hardware, then waits up to `I2C_XFER_TIMEOUT`. IRQ bottom-half either moves another FIFO chunk or clears ACK/START and completes.

State and persistence: persistent state is only in driver-private memory and controller registers. Runtime suspend disables the enable clock; runtime resume re-enables and reprograms controller timing/FIFO state. System sleep marks the adapter suspended/resumed around runtime force suspend/resume.

Dependencies and integration: depends on platform device resources, OF compatible `sprd,sc9860-i2c`, clocks named `i2c`, `source`, and `enable`, runtime PM, threaded IRQs, and the Linux I2C core. It advertises `I2C_FUNC_I2C | I2C_FUNC_SMBUS_EMUL`.

Risks: only exact 100 kHz and 400 kHz bus rates are accepted. `sprd_i2c_clk_init()` falls back to a hard-coded 26 MHz source when `clk_set_parent()` succeeds, which is easy to misread and should be checked against hardware expectations. Reads always set STOP, while intermediate write messages suppress STOP, so mixed combined-message behavior depends on hardware semantics. Timeout/error recovery is limited to clearing bits and runtime reinitialization.

Test signals: probe with valid/invalid clock-frequency, runtime PM autosuspend/resume, NACK write returning `-EIO`, long read/write FIFO threshold paths, combined transfers, and suspend/resume with active adapters are the useful coverage points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-sprd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-st.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-st.c

Purpose: provides an I2C master adapter for STMicroelectronics SSC communication controllers configured in I2C mode. The driver programs SSC timing/deglitch registers, services FIFO-driven interrupt transfers, and supports bus recovery by temporarily using the SSC block in a clock-generating mode.

Important APIs/types/functions: `struct st_i2c_dev` owns the adapter, MMIO base, IRQ, clock, mode, deglitch timing, active `struct st_i2c_client`, completion, and `busy` flag. `st_i2c_timings` defines standard/fast-mode timing constants. Adapter hooks are `st_i2c_xfer()` and `st_i2c_func()`; recovery is exposed through `st_i2c_recovery_info`. Core helpers include `st_i2c_hw_config()`, `st_i2c_wait_free_bus()`, FIFO fill/drain helpers, `st_i2c_terminate_xfer()`, and threaded ISR `st_i2c_isr_thread()`.

Control flow: probe maps resources, obtains the SSC clock and IRQ, chooses standard or fast mode from `clock-frequency`, reads required deglitch properties, configures pinctrl idle/default states, requests a threaded IRQ, and registers the adapter. `st_i2c_xfer()` sets `busy`, enables the clock, selects active pins, reinitializes hardware, and executes each message with `st_i2c_xfer_msg()`. Message setup writes the 8-bit address, pre-fills write data or dummy read clocks, enables NACK/TX-empty/arbitration interrupts, starts only the first message, and completes on STOP or repeated-start interrupt. The ISR prioritizes enabled status bits, handles TX empty, NACK, arbitration loss, STOP, and repeated start.

State and persistence: transfer progress lives in `client.count`, `client.xfered`, `client.buf`, `client.result`, and `client.stop`. Hardware is reconfigured for each transfer; clocks are enabled only around transfers. Suspend refuses while `busy` is true, then selects sleep pinctrl; resume restores default/idle pin states.

Dependencies and integration: depends on OF compatibles `st,comms-ssc-i2c` and `st,comms-ssc4-i2c`, an `ssc` clock, IRQ, pinctrl states, deglitch DT properties, and the I2C core. It advertises `I2C_FUNC_I2C | I2C_FUNC_SMBUS_EMUL`.

Risks: required deglitch properties return errors only for malformed values, so absent values leave zero pulse widths. Bus recovery intentionally switches out of I2C mode and writes a 9-bit word; regressions here can break stuck-bus recovery. The ISR uses `__fls(sta & ien)`, so interrupt priority follows highest set bit and must match error-first expectations. Timeouts leave recovery to later attempts.

Test signals: standard and fast timing setup, missing/invalid deglitch properties, write/read/multi-message repeated-start transfers, NACK and arbitration paths, `i2c_recover_bus()`, and suspend while `busy` are key tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-st.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-stm32.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-stm32.c

Purpose: supplies shared DMA helper routines for STM32 I2C controller drivers. It requests TX/RX DMA channels, configures slave addresses for the controller data registers, prepares a single DMA transfer, and releases DMA resources.

Important APIs/types/functions: exported helpers are `stm32_i2c_dma_request()`, `stm32_i2c_dma_free()`, and `stm32_i2c_prep_dma_xfer()`. They operate on `struct stm32_i2c_dma` from `i2c-stm32.h`, including TX/RX channels, active channel, mapped DMA address/length, transfer direction, data direction, and completion. The request function accepts physical controller address plus TXDR/RXDR offsets so controller-specific drivers can share the same helper.

Control flow: `stm32_i2c_dma_request()` allocates managed state, requests `"tx"` then `"rx"` DMA channels, configures TX as memory-to-device with one-byte width and RX as device-to-memory with one-byte width, initializes a completion, and returns the helper state. On any failure it releases already acquired channels and frees the managed allocation. `stm32_i2c_prep_dma_xfer()` selects RX or TX channel from the `rd_wr` flag, maps the caller buffer, prepares a slave descriptor with interrupt completion, stores callback metadata, submits it, and issues pending DMA. Errors unmap the buffer before returning.

State and persistence: DMA state persists for the lifetime of the parent controller driver after request. Per-transfer state is `chan_using`, `dma_buf`, `dma_len`, and direction fields. The helper maps buffers for each transfer but leaves unmapping to callback/error handling by the controller driver after successful submission.

Dependencies and integration: depends on Linux DMA engine, DMA mapping, device-managed allocation, and named DMA channels. It is consumed by STM32F7-style controller code and parameterized by that controller's TX/RX register offsets.

Risks: successful transfer preparation requires callers to unmap `dma_buf`; leaks or stale mappings happen if the controller callback path is skipped. `-ENODEV` for absent channels is intentionally quiet to allow PIO fallback, while other failures are logged. TX and RX channels must both exist or the helper fails completely.

Test signals: no-DMA fallback with `-ENODEV`, TX-only request failure cleanup, RX config failure cleanup, DMA mapping failure, descriptor preparation failure, and successful callback/unmap paths from a controller transfer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-stm32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-stm32.h -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-stm32.h

Purpose: declares shared STM32 I2C definitions used by STM32 controller drivers, especially speed identifiers and the DMA helper contract implemented in `i2c-stm32.c`.

Important APIs/types/functions: `enum stm32_i2c_speed` defines standard, fast, fast-plus, and sentinel speed classes. `struct stm32_i2c_dma` carries TX/RX DMA channels, the active channel, DMA address, length, transfer direction, mapping direction, and completion. Function prototypes expose `stm32_i2c_dma_request()`, `stm32_i2c_dma_free()`, and `stm32_i2c_prep_dma_xfer()` to controller-specific drivers.

Control flow: this header has no executable flow. It defines the data and function signatures used by STM32F4/F7-era drivers to share DMA setup and preparation logic. Callers request DMA once at probe time, prepare per-message DMA transfers during master/SMBus transfers, and free channels during remove or probe error unwind.

State and persistence: `struct stm32_i2c_dma` is the persistent shared state object. Its channel pointers persist across the adapter lifetime; per-transfer fields are overwritten for each DMA operation. The completion object allows controller drivers to wait for DMA completion before issuing STOP or moving to the next message.

Dependencies and integration: includes `linux/dma-direction.h`, `linux/dmaengine.h`, and `linux/dma-mapping.h`. It integrates with STM32 controller source files by abstracting DMA channel names and register offsets while leaving controller-specific IRQ and transfer sequencing outside the helper.

Risks: the `rd_wr` argument in `stm32_i2c_prep_dma_xfer()` is a boolean direction selector, so callers must pass the same read/write sense expected by the helper. The structure has no ownership flag; callers must avoid freeing channels twice and must clear or stop active DMA before removal.

Test signals: compile coverage across STM32 controller drivers, static checks that prototypes match implementation, and runtime validation of DMA setup/free plus per-transfer completion in the STM32F7 driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-stm32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-stm32f4.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-stm32f4.c

Purpose: implements the STM32F4 I2C controller master adapter. It programs CR/CCR/TRISE timing, handles event and error IRQs, and supports standard and fast mode master transfers with repeated starts.

Important APIs/types/functions: `struct stm32f4_i2c_dev` stores adapter, device, MMIO, completion, clock, selected speed, parent clock rate, and active `stm32f4_i2c_msg`. `stm32f4_i2c_hw_config()` programs peripheral clock frequency, rise time, speed mode, and enables the peripheral. `stm32f4_i2c_xfer()` and `stm32f4_i2c_func()` provide the I2C algorithm. Event and error handlers are `stm32f4_i2c_isr_event()` and `stm32f4_i2c_isr_error()`.

Control flow: probe maps registers, obtains event/error IRQs, enables clock, resets the controller, derives speed from `clock-frequency`, requests IRQs, configures hardware, registers the adapter, then disables the clock until transfers. A transfer enables the clock and iterates messages through `stm32f4_i2c_xfer_msg()`. Each message sets address/count/buffer/result/stop, enables event/error interrupts, waits for bus-free on the first message, starts hardware, and waits on completion. Event IRQ handles start-bit, address sent, TXE/RXNE, and BTF with special read handling for 1-, 2-, 3-, and N-byte transfers. Error IRQ maps arbitration loss to `-EAGAIN` and ACK/bus errors to `-EIO`.

State and persistence: no runtime PM is used; the clock is manually enabled for probe initialization and each transfer. Active transfer state is held in `msg`. Hardware state persists while clocked, but transfers explicitly enable interrupts and set START/STOP/repeated START.

Dependencies and integration: depends on OF compatible `st,stm32f4-i2c`, MMIO resources, two IRQs, reset controller, clock framework, and the I2C core. Shared STM32 header is included for speed enum values, though this F4 implementation does not use the shared DMA helper.

Risks: parent clock must be in hardware-limited MHz ranges or probe/config fails. Read sequencing is sensitive to ACK/POS/STOP ordering; off-by-one changes can break 1/2/3 byte reads. Timeout path does not perform full controller reset, so later transfers depend on hardware/IRQ state being recoverable.

Test signals: clock-frequency selection, parent-rate boundary checks, 0/1/2/3/N-byte reads, multi-message repeated starts, NACK/arbitration/bus error IRQs, and reset/clock lifecycle during probe/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-stm32f4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-stm32f7.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-stm32f7.c

Purpose: implements the STM32F7/STM32MP I2C controller family. It supports master and atomic master transfers, SMBus protocols with PEC/alert/host-notify, slave mode, optional DMA, Fast Mode Plus configuration, wake IRQs, runtime PM, and suspend register backup/restore.

Important APIs/types/functions: `struct stm32f7_i2c_dev` is the central state object, containing adapter, MMIO, clock, active message sequence, custom `stm32f7_i2c_msg`, timing setup/output, slave slots, DMA state, syscfg Fast Mode Plus data, wake/SMBus/filter state, alert state, and atomic flag. Timing is derived by `stm32f7_i2c_setup_timing()` and `stm32f7_i2c_compute_timing()`. Master paths use `stm32f7_i2c_xfer_core()`, `stm32f7_i2c_xfer_msg()`, IRQ handlers, and optional `stm32_i2c_prep_dma_xfer()`. SMBus uses `stm32f7_i2c_smbus_xfer_msg()`, repeated-start setup, reload, and PEC check. Slave registration and IRQ service are handled by `stm32f7_i2c_reg_slave()`, `stm32f7_i2c_unreg_slave()`, and slave event helpers.

Control flow: probe loads compatible-specific setup, maps registers, resets hardware, requests event and optional error IRQs, computes timing from firmware properties, enables Fast Mode Plus if needed, initializes DMA if available, configures wake IRQ/runtime PM, programs hardware, registers the adapter, and enables SMBus host/alert children when requested. Master transfers runtime-resume, wait for bus-free, initialize CR2 address/direction/NBYTES/reload, choose DMA or RX/TX interrupts, start, then wait via IRQ completion or atomic polling. Event IRQ moves TX/RX bytes in hard IRQ and wakes the thread for NACK/STOP/TC/TCR; threaded handlers reload chunks, chain messages, send STOP, or complete. SMBus builds an internal aligned buffer and may perform a write phase followed by a repeated-start read phase.

State and persistence: runtime PM autosuspends the clock unless slave mode requires it. Suspend backs up CR1/CR2/OAR/TIMINGR and clears Fast Mode Plus bits when not wake-capable, then restores on resume. Slave registrations persist in three slots, and wakeup can remain enabled while slaves are registered.

Dependencies and integration: depends on OF compatibles `st,stm32f7-i2c`, `st,stm32mp15-i2c`, `st,stm32mp13-i2c`, and `st,stm32mp25-i2c`; DMA engine, regmap/syscon for Fast Mode Plus on older MP parts, pinctrl, wakeirq, reset, runtime PM, SMBus helpers, and I2C slave APIs.

Risks: timing computation has many boundary conditions around analog/digital filters, rise/fall times, and downgrade to lower bus rates. DMA and IRQ completion ordering is delicate, especially before TC/STOP and on NACK/error callbacks. SMBus block reads use dynamic reload after receiving count. Slave support shares IRQ paths with master/error handling and must not disable address interrupts incorrectly. Fast Mode Plus cleanup is needed on all probe/remove error paths.

Test signals: timing property matrices, DMA and PIO master transfers above/below threshold, atomic transfers, multi-message reload above 255 bytes, SMBus byte/word/block/proc-call with PEC, SMBus alert and host-notify, slave register/unregister/read/write/stop callbacks, wake-source suspend/resume, and Fast Mode Plus syscfg/CR1 variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-stm32f7.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-sun6i-p2wi.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-sun6i-p2wi.c

Purpose: implements Allwinner SUN6I Push-Pull Two Wire Interface as an I2C/SMBus-style adapter for the AXP221-style PMIC bus. P2WI is not normal SMBus: it supports one target, byte-data transactions, parity bits, and no per-byte ACK.

Important APIs/types/functions: `struct p2wi` contains the adapter, completion, last interrupt status, MMIO base, clock, reset control, and optional fixed target address. `p2wi_smbus_xfer()` is the only transfer hook and supports `I2C_FUNC_SMBUS_BYTE_DATA`. `p2wi_interrupt()` stores/clears status and completes transfers. Probe/remove handle clock/reset/register setup and adapter registration.

Control flow: probe validates requested clock frequency, ensures no more than one child node, optionally captures the target `reg`, maps registers, obtains IRQ/clock/reset, deasserts reset, installs the IRQ, soft-resets the block, programs divider and SDA delay, and registers the adapter. A transfer checks the fixed target address if configured, writes command/data registers, programs read/write data length, ensures no active transfer bit is set, enables interrupts, starts hardware, waits for completion, checks load-busy and transfer-error flags, and returns read data for reads.

State and persistence: persistent state includes target address, clock/reset resources, and register configuration. Per-transfer state is the completion and `status` captured by the IRQ. Remove asserts reset and unregisters the adapter.

Dependencies and integration: depends on OF compatible `allwinner,sun6i-a31-p2wi`, reset and clock frameworks, platform IRQ/MMIO, and I2C core SMBus transfer callbacks. It can be used without a child node for userspace `i2c-dev`, disabling address filtering.

Risks: `wait_for_completion()` has no timeout, so a lost interrupt or wedged controller can hang callers. Protocol support is intentionally narrow and incompatible with normal SMBus devices. Clock divider clamping may silently run at a different rate than requested. Only one child target is supported by design.

Test signals: probe with zero/too-high clock, multiple child nodes, no-child user-space mode, address mismatch, byte read/write success, load-busy and transfer-error interrupt statuses, reset assertion on remove, and interrupt-loss fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-sun6i-p2wi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-synquacer.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-synquacer.c

Purpose: implements the Socionext/Fujitsu SynQuacer I2C controller as an interrupt-driven master adapter with OF and ACPI binding support.

Important APIs/types/functions: `struct synquacer_i2c` tracks completion, current message array, message index/pointer, IRQ/device/MMIO, PCLK rate, selected speed, timeout, state machine, and adapter. The algorithm is `synquacer_i2c_xfer()` plus `synquacer_i2c_functionality()`. Hardware helpers initialize/reset timing registers, start a master transfer, and stop with completion. `synquacer_i2c_isr()` runs the transfer state machine.

Control flow: probe reads bus speed from ACPI or `clock-frequency`, gets PCLK from a clock or property, validates it, maps MMIO, requests IRQ, initializes adapter state, chooses standard or fast mode, programs hardware, and registers a numbered adapter. `synquacer_i2c_xfer()` computes a timeout from message bytes, retries up to adapter retries on `-EAGAIN`, and resets hardware between retries. `synquacer_i2c_doxfer()` initializes hardware, checks bus busy, stores message state, starts the first address, and waits for completion. The ISR handles bus error/arbitration loss, START ACK, WRITE data/next-message repeated starts, READ address/data phases, ACK control, STOP, and completion.

State and persistence: transfer state is explicit in `state`, `msg`, `msg_num`, `msg_idx`, and `msg_ptr`. `synquacer_i2c_stop()` clears BCR, resets state to idle, updates `msg_idx` or error code, and completes. Hardware timing is reinitialized each attempt; reset disables clock registers and waits PCLK cycles.

Dependencies and integration: supports OF compatible `socionext,synquacer-i2c` and ACPI ID `SCX0003`, optional `pclk`, `socionext,pclk-rate`, platform IRQ/MMIO, and Linux I2C core. It advertises `I2C_FUNC_I2C | I2C_FUNC_SMBUS_EMUL`.

Risks: timeout returns `-EAGAIN` and is converted to `-EIO` only after retries, so callers may see retries for multiple fault classes. PCLK must be 14-200 MHz. The read path ignores the first-byte-transfer address echo; state transitions rely on correct BSR flags. Bus recovery is limited to hardware reset, not I2C core bus recovery.

Test signals: OF and ACPI probe, PCLK boundary validation, standard/fast timing, read/write and combined transfers, zero-length last message, NACK, arbitration loss, bus error, timeout/retry behavior, and hardware reset between retries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-synquacer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-taos-evm.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-taos-evm.c

Purpose: exposes TAOS evaluation modules as I2C adapters over an RS232 serio link. The module firmware accepts ASCII commands for SMBus byte and byte-data transactions and can auto-instantiate a TSL2550 client on matching adapter names.

Important APIs/types/functions: `struct taos_data` stores the I2C adapter, optional instantiated client, serial parser state, cached address, command/response buffer, and buffer position. `taos_smbus_xfer()` translates I2C SMBus operations into ASCII protocol. `taos_interrupt()` is the serio receive parser. `taos_connect()` and `taos_disconnect()` bind/unbind serio devices.

Control flow: connect allocates state, opens the serio port, initializes the adapter, sends reset, waits for the module identification string ending in `:`, extracts the adapter name, turns echo off, registers the I2C adapter, and optionally creates a TSL2550 client. Each SMBus transfer encodes address/command/data into the shared buffer, skips resending the same address, writes the ASCII command to serio, starts read/write with `<` or `>`, waits up to 150 ms for a response ending in `]`, and interprets `ACK`, `NAK`, or `xHH` read data. The interrupt parser has states for reset identification, echo-off acknowledgement, and transaction receive.

State and persistence: adapter lifetime is tied to serio connection. The cached `addr` persists across transactions to reduce serial traffic. Parser state and buffer position are mutable global-per-device transfer state, while the wait queue is file-global.

Dependencies and integration: depends on serio RS232 protocol `SERIO_TAOSEVM`, Linux I2C core, wait queues, and optional sensor client instantiation. It advertises only `I2C_FUNC_SMBUS_BYTE | I2C_FUNC_SMBUS_BYTE_DATA`.

Risks: the global wait queue is shared across all devices, so multi-device scenarios rely on per-device state checks after wakeup. Transfers serialize through adapter locking but the driver itself has no explicit buffer lock. Response parsing assumes exactly five received bytes and fixed TAOS strings. Unsupported SMBus operations return `-EOPNOTSUPP`.

Test signals: serio connect/reset/identification, echo-off timeout, adapter-name parsing, byte and byte-data read/write translation, NAK handling, malformed read hex returning `-EPROTO`, timeout with partial response, auto-instantiation of TSL2550, and disconnect cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-taos-evm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-tegra-bpmp.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-tegra-bpmp.c

Purpose: provides an I2C adapter whose transfers are executed by NVIDIA Tegra BPMP firmware rather than directly by Linux-controlled I2C registers. It serializes Linux `i2c_msg` arrays into BPMP MRQ_I2C requests and deserializes firmware read responses.

Important APIs/types/functions: `struct tegra_bpmp_i2c` stores adapter, device, BPMP handle, and firmware bus ID. `tegra_bpmp_xlate_flags()` maps Linux I2C flags to serial-I2C firmware flags. `tegra_bpmp_serialize_i2c_msg()` and `tegra_bpmp_i2c_deserialize()` implement the wire format. `tegra_bpmp_i2c_xfer_common()` is used by normal and atomic hooks.

Control flow: probe gets the parent BPMP object, reads `nvidia,bpmp-bus-id`, initializes adapter fields, and registers the adapter. A transfer first checks serialized TX and expected RX sizes against BPMP ABI buffer limits. It then builds a request with little-endian address/flags/length headers and write payloads, sends it through `tegra_bpmp_transfer()` or `_atomic()`, maps BPMP firmware errors to Linux errno, validates response read length, copies read blocks back into each read message, and returns `num`.

State and persistence: there is almost no controller-local state beyond bus ID and BPMP pointer. Firmware owns actual hardware state, locking, timing, power, and bus recovery. Per-transfer request/response structs are stack-local.

Dependencies and integration: depends on Tegra BPMP ABI headers, parent BPMP device data, OF compatible `nvidia,tegra186-bpmp-i2c`, platform devices, and Linux I2C core. It advertises I2C, SMBus emulation, 10-bit addressing, protocol mangling, and NOSTART.

Risks: message size validation must match BPMP ABI limits; otherwise firmware buffers would be overrun. The deserialize path requires total read length to match firmware response exactly. All bus behavior is delegated to firmware, so Linux-side observability and recovery are limited. Unsupported or newly added Linux flags would need explicit translation.

Test signals: serialization for read/write/mixed messages, every supported flag translation, oversized TX/RX rejection, firmware return mapping for EAGAIN/ETIMEDOUT/ENXIO/unknown errors, atomic transfer path, and probe without parent BPMP or bus ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-tegra-bpmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-tegra.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-tegra.c

Purpose: implements the MMIO Tegra I2C controller family across many SoC generations and variants, including DVC and VI register layouts, packet-mode transfers, PIO/DMA data movement, bus clear recovery, runtime PM, ACPI/OF matching, high-speed mode on newer parts, and hardware mutex support on virtualized/shared systems.

Important APIs/types/functions: `struct tegra_i2c_hw_feature` describes per-SoC capabilities, timing constants, quirks, register map, DMA type, recovery support, and mutex support. `struct tegra_i2c_dev` holds adapter, MMIO, clocks, DMA buffer/channel, completions, transfer state, timings, and mode flags. Adapter hooks are `tegra_i2c_xfer()`, `tegra_i2c_xfer_atomic()`, and `tegra_i2c_func()`. Core helpers include register access wrappers, clock/reset initialization, FIFO flush/fill/drain, DMA setup/submit, packet header construction, IRQ handling, bus clear, error recovery, and PM callbacks.

Control flow: probe matches hardware data, maps registers, requests an IRQ with `IRQ_NOAUTOEN`, parses firmware timings and multi-master mode, prepares clocks, optionally initializes DMA, enables runtime PM, initializes hardware, fills adapter metadata/quirks/recovery, and registers a numbered adapter. Transfers runtime-resume, acquire the optional hardware mutex, walk messages, choose STOP/repeated-start/continue based on following message and `I2C_M_NOSTART`, handle SMBus block read length probing with `I2C_M_RECV_LEN`, and call `tegra_i2c_xfer_msg()`. Each message flushes FIFOs, selects DMA for aligned larger transfers, configures FIFO triggers, pushes packet headers, starts PIO or DMA, waits for DMA and packet completion, masks interrupts, and recovers or maps errors.

State and persistence: hardware feature tables are static. Runtime state includes message buffer pointer/remaining length, DMA mode/read flags, error bitmask, and completions. Runtime PM gates clocks and pinctrl idle/default state; VI controllers reinitialize after power-domain resume. System suspend marks the adapter suspended and balances runtime suspend/resume on resume.

Dependencies and integration: depends on platform MMIO/IRQ, reset, clocks (`div-clk`, optional `fast-clk`/`slow`), DMA engine, pinctrl, runtime PM, ACPI IDs, OF compatibles from Tegra20 through Tegra264/410, I2C adapter quirks, and optional I2C bus recovery.

Risks: many SoC feature combinations make register offsets and timing constants high-risk. DMA uses one coherent buffer and different completion ordering for reads vs writes. Error paths must reset/reinitialize hardware and release the hardware mutex; currently an early mutex-lock failure returns without `pm_runtime_put()`, which is a path worth auditing. SMBus block read mutates `msg.len` after first byte. Atomic mode disables DMA and polls IRQ status, so functions used there must remain atomic-safe.

Test signals: per-compatible probe and timing programming, PIO vs DMA threshold behavior, read/write partial word FIFO handling, repeated-start/NOSTART/RECV_LEN transfers, NACK/arbitration/unknown IRQ/overflow errors, bus clear recovery, mutex lock/unlock contention, VI write workaround, runtime/system PM, and ACPI matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-tegra.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-thunderx-pcidrv.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-thunderx-pcidrv.c

Purpose: binds Cavium ThunderX/OcteonTX TWSI I2C controllers exposed as PCI devices and adapts the shared Octeon I2C core to PCI resources, interrupts, clocks, SMBus alert, and adapter registration.

Important APIs/types/functions: this file uses `struct octeon_i2c` from `i2c-octeon-core.h`. It provides interrupt enable/disable callbacks for core and high-level controller interrupt bits, `thunderx_i2c_functionality()`, the `thunderx_i2c_algo` using `octeon_i2c_xfer`, clock setup helpers, SMBus alert setup/removal, and PCI probe/remove.

Control flow: PCI probe allocates Octeon core state, fills ThunderX register offsets, enables the PCI device, requests BARs, maps BAR0, obtains system clock from DT clock or ACPI properties with defaults, reads `clock-frequency`, initializes the wait queue and interrupt callback hooks, allocates one MSI-X vector, requests `octeon_i2c_isr`, initializes low-level hardware, applies OcteonTX2 reference-clock adjustment for low-speed modes, programs the TWSI clock, configures adapter metadata/recovery, registers it, and optionally creates an SMBus alert responder from OF IRQ data. Remove unregisters alert, disables the clock, and removes the adapter.

State and persistence: persistent controller state is held in the shared `octeon_i2c` object: mapped register base, offsets, clock frequencies, callback hooks, adapter, alert client, and wait queue. Transfer state is managed by the Octeon core rather than this wrapper.

Dependencies and integration: depends on PCI, MSI-X, the shared Octeon I2C core, OF/ACPI firmware properties, Linux clocks, SMBus alert helpers, and I2C bus recovery info from the core. It matches Cavium PCI device ID `0xa012` and advertises I2C plus SMBus emulation except quick, SMBus read block data, and block process call.

Risks: `thunder_i2c_smbus_remove()` unconditionally unregisters `i2c->ara`; if alert setup never created a client, this path depends on unregister handling of a null pointer and should be checked. ACPI SMBus alert is explicitly unsupported. Clock defaults hide missing firmware clock data. Probe error paths disable clocks but rely on devm/pcim for most cleanup.

Test signals: PCI probe/remove, DT and ACPI clock property paths, OcteonTX2 low-speed reference clock selection, MSI-X IRQ delivery, shared-core transfer/recovery paths, SMBus alert present/absent cases, and probe failures after clock enable or IRQ allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-thunderx-pcidrv.c -->
