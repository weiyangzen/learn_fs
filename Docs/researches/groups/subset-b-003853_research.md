# subset-b-003853 Research

Grouped research for the listed Linux I2C bus driver files under `sources/distributed-fs/ceph-client`. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-nomadik.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-nomadik.c

## Purpose
Implements the AMBA Nomadik/Ux500 I2C master adapter, with Mobileye EyeQ5/EyeQ6H compatibility hooks. It exposes a kernel `i2c_adapter` for Nomadik-family controllers, programs the controller clock/FIFO thresholds, drives interrupt-based master transfers, and handles runtime/system power transitions.

## Important APIs, Types, And Functions
Core state is held in `struct nmk_i2c_dev`, which owns AMBA device metadata, MMIO base, clock, current `i2c_nmk_client`, FIFO thresholds, transfer wait queue, timeout, result, and 32-bit-bus access mode. `nmk_i2c_xfer()` is the adapter `.xfer` implementation; `nmk_i2c_xfer_one()`, `read_i2c()`, and `write_i2c()` program `I2C_MCR`, `I2C_CR`, and interrupt masks for each message. `i2c_irq_handler()` drains/fills FIFOs and completes transfers. Probe/remove are `nmk_i2c_probe()` and `nmk_i2c_remove()`, registered through `amba_driver`.

## Control Flow
Probe reads firmware properties, applies EyeQ OLB speed setup when matched, maps registers, requests IRQ, enables the clock, initializes hardware, builds the adapter, and registers it. A transfer runtime-resumes the device, retries the message list up to three times, calls `setup_i2c_controller()`, loads per-message client state, executes read/write, and waits on `xfer_wq`. The IRQ handler processes one pending interrupt source, moves bytes through TX/RX FIFOs, records errors on arbitration/bus/FIFO conditions, disables/clears interrupts on transaction done, and wakes the waiter.

## State And Persistence
Persistent runtime state is device-local in `struct nmk_i2c_dev`; no on-disk state exists. Hardware state spans CR/MCR/BRCR/FIFO/interrupt registers and is reset by `init_hw()`. Runtime PM gates the controller clock and restores default hardware state on resume. EyeQ5 speed-mode selection persists in an external syscon regmap until changed by firmware or another driver.

## Dependencies And Integration Points
Depends on AMBA, Linux I2C core, runtime PM, clocks, pinctrl PM states, device tree properties, syscon/regmap for EyeQ5, and IRQ delivery. It advertises `I2C_FUNC_I2C`, SMBus emulation, and 10-bit addressing. It integrates early with `subsys_initcall()` because I2C can be needed during platform bring-up.

## Risks
Timeout handling and FIFO accounting are critical: stale `cli.count`, missed `MTD/MTDWS`, or an unhandled interrupt can leave the bus stuck. The IRQ handler processes only the first set bit in `MISR`, so simultaneous status bits rely on later interrupts. EyeQ 32-bit access mode and OLB speed masks must match the actual SoC. Runtime PM failures can leave clocks disabled while callers expect transfers.

## Test Signals
Useful signals are successful `i2cdetect`/SMBus transfers across 100 kHz, 400 kHz, fast-plus, and high-speed modes; repeated-start write-read transactions; 10-bit address smoke tests; timeout injection with absent targets; suspend/resume and runtime autosuspend cycles; IRQ error logging for arbitration/bus errors; and EyeQ5/EyeQ6H boot tests that confirm the correct MMIO access width and OLB speed selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-nomadik.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-npcm7xx.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-npcm7xx.c

## Purpose
Provides the Nuvoton NPCM7xx/NPCM8xx I2C/SMBus controller driver. It supports master transfers, optional slave mode, FIFO and non-FIFO operation, SMBus block/PEC behavior, timing-table clock programming, debugfs counters, and bus recovery using the controller's SCL toggle capability.

## Important APIs, Types, And Functions
`struct npcm_i2c` is the central state container: adapter, MMIO registers, chip data, spinlock, completion, active messages, indices, FIFO flags, master/slave state, PEC/block flags, recovery info, and diagnostic counters. `npcm_i2c_master_xfer()` implements `.xfer`; `npcm_i2c_bus_irq()` dispatches master or slave IRQ handling. Master control is split across `npcm_i2c_master_start_xmit()`, `npcm_i2c_int_master_handler()`, `npcm_i2c_irq_handle_sda()`, read/write subhandlers, and error handlers. Slave support is behind `CONFIG_I2C_SLAVE` through `.reg_slave` and `.unreg_slave`.

## Control Flow
Probe obtains match data, clock rate, sys-manager regmap, MMIO, IRQ, initializes adapter fields, requests the IRQ, initializes timing and hardware, installs recovery callbacks, registers a numbered adapter, and creates debugfs counters. Master transfer normalizes one-message reads/writes and two-message write-read pairs into write/read buffer sizes, waits briefly for bus free, stores the destination address for recovery, resets/recovers on busy or BER state, arms completion and interrupts, starts the transaction, then waits with an adaptive timeout. IRQs move the state machine through address stall, write FIFO fill, repeated-start read, block-length handling, STOP/EOB completion, NACK, BER, and recovery.

## State And Persistence
The driver keeps rich in-memory state for active transfer progress and diagnostics. Debugfs exposes monotonically increasing counters for bus error, NACK, recovery success/failure, timeout, and completion counts. Hardware state includes two register banks, FIFO threshold/configuration, own slave addresses, PEC/block flags, and module timing. There is no durable storage.

## Dependencies And Integration Points
Depends on platform device/OF matching for `nuvoton,npcm750-i2c` and `nuvoton,npcm845-i2c`, clocks, syscon regmap, I2C core, optional I2C slave framework, debugfs, completions, and generic bus recovery. `npcm_i2c_data` supplies generation-specific FIFO masks and segment-control initialization.

## Risks
This is a highly stateful IRQ machine; race boundaries around `bus->msgs`, completion, master/slave mode switching, and slave-address masking are sensitive. FIFO `LAST`/PEC/block-read handling has hardware workaround comments and can require module reset after errors. Recovery relies on toggling SCL rather than direct line driving. Long transfer limits are large, so timeout estimation and FIFO index arithmetic need stress coverage. Warm-reset stale interrupt status is explicitly guarded in probe.

## Test Signals
Coverage should include standard/fast/fast-plus clock configurations, write-only, read-only, write-read, SMBus block read with `I2C_M_RECV_LEN`, PEC reads, NACK and bus-error injection, busy-bus recovery, FIFO-capable and FIFO-disabled hardware, multi-master contention, debugfs counter increments, slave read/write callbacks when enabled, and repeated module remove/probe or warm reset scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-npcm7xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-nvidia-gpu.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-nvidia-gpu.c

## Purpose
Implements a PCI I2C master for NVIDIA GPU cards with USB Type-C/UCSI support. The adapter is primarily used to instantiate and communicate with the Cypress CCGx UCSI client behind NVIDIA GPU I2C registers.

## Important APIs, Types, And Functions
`struct gpu_i2c_dev` stores the PCI device, MMIO registers, adapter, and CCGx client. `gpu_i2c_xfer()` is the I2C algorithm transfer function; `gpu_i2c_read()`, `gpu_i2c_write()`, `gpu_i2c_start()`, `gpu_i2c_stop()`, and `gpu_i2c_check_status()` implement register-level cycles. `gpu_i2c_probe()` maps BAR0, allocates MSI, configures the bus, registers the adapter, creates the CCGx UCSI I2C client, and enables runtime PM.

## Control Flow
Probe matches NVIDIA devices with the unknown serial class, maps controller registers, enables pad/timing configuration for 100 kHz I2C, registers an adapter with quirks, and attaches the CCGx/UCSI client using software-node properties. Transfers runtime-resume the device, process each I2C message, use an implicit-start hardware read for reads, manually emit START/address/data for writes, then emit STOP and autosuspend.

## State And Persistence
State is limited to adapter registration, MMIO configuration, runtime PM state, and the child UCSI client. The driver reprograms pad control and timing on resume. It has no filesystem persistence.

## Dependencies And Integration Points
Depends on PCI, MSI allocation, I2C core, runtime PM, power-supply property definitions, and `i2c_new_ccgx_ucsi()` from `i2c-ccgx-ucsi.h`. The adapter advertises `I2C_FUNC_I2C | I2C_FUNC_SMBUS_EMUL` but quirks limit reads to four bytes and combined write-then-read second messages to four bytes.

## Risks
Hardware imposes a maximum four-byte read because the controller sends STOP after each read. Device matching by vendor plus unknown class is intentionally broad and relies on transfer/UCSI failures to reject unexpected devices. `pm_runtime_get_sync()` return handling is not used in the transfer path. STOP error handling is best effort after failures.

## Test Signals
Signals include CCGx UCSI probe success, connector-change handling after runtime resume, bounded read behavior through adapter quirks, NACK returning `-ENXIO`, hardware timeout returning `-ETIMEDOUT`, remove path freeing IRQ vectors, and suspend/resume tests confirming timing/pad registers are restored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-nvidia-gpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ocores.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ocores.c

## Purpose
Implements an I2C adapter for the OpenCores I2C controller and GRLIB variant. It supports MMIO or I/O port resources, multiple register widths and endianness, interrupt-driven and polling transfers, platform-data device creation, and noirq suspend/resume.

## Important APIs, Types, And Functions
`struct ocores_i2c` stores register accessors, clocks, bus/core rates, transfer state, wait queue, and process lock. `ocores_process()` is the byte-level state machine. `ocores_xfer_core()` starts a transfer and waits via IRQ or polling; `ocores_xfer()` and `ocores_xfer_polling()` expose normal and atomic paths. `ocores_init()` programs the prescaler and enables the core. Probe configures accessors, resources, OF/platform data, IRQ mode, and adapter registration.

## Control Flow
Probe maps resources, derives clock and register layout from platform data or OF, selects accessors, optionally disables IRQ use for broken FU540 hardware, requests the IRQ if needed, initializes the controller, then registers the adapter. Transfers set the interrupt enable bit according to mode, seed state with the first address byte, issue START, and either wait on `wait` or repeatedly poll status and invoke the ISR path. `ocores_process()` handles NACK/arbitration loss, repeated starts, read ACK/NACK decisions, writes, STOP, and final wakeup.

## State And Persistence
All transfer state is in `struct ocores_i2c`: current message pointer, byte position, remaining message count, and state enum. Hardware state is the prescaler/control/command/status register set. No durable state is persisted.

## Dependencies And Integration Points
Depends on platform device resources, optional clocks, OF bindings (`opencores,i2c-ocores`, GRLIB, SiFive compatibles), `i2c-ocores` platform data, I2C core, and IRQ or polling support. Platform data can instantiate known child devices after adapter registration.

## Risks
The file mutates the global `ocores_algorithm.xfer` when one probed device needs polling, which can affect later adapters using the same static algorithm. Timing depends on accurate `ip_clock_khz` and `bus_clock_khz`; unsupported clock error threshold is strict. Broken IRQ handling and polling mode must not race with `ocores_process_timeout()`, hence the process lock. OF clock fallback includes deprecated properties and must avoid drift.

## Test Signals
Test by probing OpenCores and GRLIB variants with 8/16/32-bit and big/little-endian registers, transfer with and without IRQs, exercise atomic polling transfers, inject NACK and arbitration loss, validate prescaler output against requested bus rate, suspend/resume with clock changes, and confirm FU540-compatible devices operate in polling mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ocores.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-octeon-core.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-octeon-core.c

## Purpose
Contains the shared Cavium/Marvell OCTEON/ThunderX TWSI I2C implementation used by platform and PCI glue. It implements low-level controller transfers, high-level-controller optimized transfers, block FIFO transfers, clock programming, interrupt/poll waits, status translation, and bus recovery.

## Important APIs, Types, And Functions
Exports `octeon_i2c_isr()`, `octeon_i2c_xfer()`, `octeon_i2c_init_lowlevel()`, `octeon_i2c_set_clock()`, and `octeon_i2c_recovery_info`. Low-level helpers include `octeon_i2c_start()`, `octeon_i2c_stop()`, `octeon_i2c_read()`, and `octeon_i2c_write()`. HLC paths include pure read/write, composite read/write, and block composite functions. `octeon_i2c_check_status()` maps TWSI status codes to Linux errors.

## Control Flow
The transfer path first tries HLC for low-speed messages that match supported shapes: single messages up to eight bytes, two-message same-address internal-address operations up to eight bytes, or block operations up to 1024 bytes when block registers exist. Otherwise it falls back to low-level START, address, byte-by-byte read/write, STOP sequencing. Wait helpers use interrupts unless broken IRQ detection switches the device to polling.

## State And Persistence
State lives in the shared `struct octeon_i2c` supplied by the glue driver: wait queue, adapter, register offsets, IRQ hooks, frequency, MMIO base, HLC/block flags, and broken-IRQ flags. The code toggles hardware HLC/block modes and clock divisors but persists nothing outside device registers.

## Dependencies And Integration Points
Depends on the definitions in `i2c-octeon-core.h`, Linux I2C core, PCI helper for OcteonTX2 clock behavior, generic SCL bus recovery, and glue-provided interrupt enable/disable callbacks. The exported recovery info is attached by platform glue.

## Risks
HLC status is read from a different register than low-level status, so mode transitions must be clean. Broken IRQ fallback is runtime-detected and changes wait behavior. Block FIFO paths require correct byte ordering and length limits. Watchdog timeout handling resets the bus monitor. Low-level fallback rejects zero-length messages and may return `-EOPNOTSUPP` when the core is addressed as a slave.

## Test Signals
Exercise HLC pure and composite transfers at <=400 kHz, block composite reads/writes above eight bytes, high-speed fallback, `I2C_M_RECV_LEN`, NACK/arbitration/watchdog status paths, broken IRQ polling fallback, clock divisor calculation on OcteonTX2 and older platforms, and generic SCL recovery after a forced stuck bus.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-octeon-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-octeon-core.h -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-octeon-core.h

## Purpose
Defines the shared OCTEON TWSI register model, status constants, `struct octeon_i2c`, inline MMIO accessors, chip-identification helper, and exported function prototypes used by OCTEON I2C glue drivers.

## Important APIs, Types, And Functions
`struct octeon_i2c_reg_offset` abstracts register layout differences. `struct octeon_i2c` carries adapter, clock, IRQs, MMIO, frequency, feature flags, callback hooks, atomic IRQ enable counters, and SMBus alert fields. Inline helpers implement indirect core register access through `SW_TWSI`, TWSI interrupt register access, and write flushing. Prototypes expose ISR, transfer, low-level init, clock setup, and recovery info.

## Control Flow
The header does not execute standalone control flow, but it shapes all core operations. Indirect register reads/writes set `SW_TWSI_V`, poll until hardware clears it, and optionally signal `-EIO` on read timeout. Glue code fills register offsets and interrupt callbacks before invoking the shared core.

## State And Persistence
The header defines in-memory and MMIO state only. Atomic counters are used by glue drivers to balance IRQ enable/disable calls on hardware where interrupts are explicitly enabled via Linux IRQ lines. No persistent storage is involved.

## Dependencies And Integration Points
Includes Linux atomic, bitfield, clk, I2C, SMBus alert, PCI, and raw IO facilities. `octeon_i2c_is_otx2()` inspects PCI subsystem bits for OcteonTX2-specific clock programming. `octeon_i2c_recovery_info` integrates with the Linux I2C bus recovery framework.

## Risks
The inline indirect accessors use bounded spin loops and silently return from writes when hardware never clears `SW_TWSI_V`, making caller-side status checks important. Register-offset macros assume glue initialized all used offsets. Raw 64-bit MMIO and endianness must match the platform. The struct includes both platform and PCI-oriented fields, so glue must initialize only valid combinations.

## Test Signals
Compile coverage from both platform and any PCI glue, static analysis for initialized offsets/callbacks, recovery callback use, timeout paths in indirect reads, OcteonTX2 detection, and IRQ counter balancing on CN7890-style dual-interrupt hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-octeon-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-octeon-platdrv.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-octeon-platdrv.c

## Purpose
Provides the platform-device glue for Cavium OCTEON TWSI I2C controllers. It maps device-tree resources, wires interrupts into the shared OCTEON core, initializes clocks/registers, and registers the I2C adapter.

## Important APIs, Types, And Functions
`octeon_i2c_probe()` is the main setup function. Interrupt helpers include standard CSR interrupt enable/disable, CN7890-style Linux IRQ enable/disable wrappers, and a separate HLC ISR for the secondary interrupt. The adapter algorithm calls `octeon_i2c_xfer()` from the shared core and reports functionality through `octeon_i2c_functionality()`.

## Control Flow
Probe detects CN7890-compatible hardware, selects IRQ numbers and callback implementations, allocates `struct octeon_i2c`, maps MMIO, reads `clock-frequency` or legacy `clock-rate`, gets IO clock rate, requests interrupts, initializes low-level hardware, programs clock divisors, attaches recovery info, and registers the adapter. Remove unregisters the adapter.

## State And Persistence
This file initializes the shared `struct octeon_i2c` with platform-specific offsets, IRQs, callbacks, `twsi_freq`, `sys_freq`, adapter timeout/retries, and OF node. Persistent state is only hardware register configuration during device lifetime.

## Dependencies And Integration Points
Depends on OF compatibles `cavium,octeon-3860-twsi` and `cavium,octeon-7890-twsi`, platform IRQ/resource APIs, `octeon_get_io_clock_rate()`, shared `i2c-octeon-core` exports, and the I2C core. The adapter supports I2C, SMBus emulation except quick, SMBus read block, and block process call.

## Risks
CN7890 uses separate HLC and core IRQ lines with manual `IRQ_NOAUTOEN` and atomic disable balancing; incorrect IRQ ordering or counts can deadlock waits. Missing clock properties fail probe. Adapter timeout is very short at 2 ms, so slow or clock-stretched devices may expose timing issues. OF register layout assumptions are fixed in probe.

## Test Signals
Boot/probe tests on both legacy and CN7890 compatibles, IRQ enable/disable balance under repeated transfers, fallback polling when shared core detects broken IRQs, clock-frequency and legacy clock-rate bindings, adapter functionality enumeration, and bus recovery after simulated stuck SCL/SDA.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-octeon-platdrv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-omap.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-omap.c

## Purpose
Implements the TI OMAP I2C bus adapter for multiple OMAP IP revisions. It handles revision-specific register maps, clock/FIFO programming, interrupt-threaded and polling transfers, hardware errata, bus-busy validation, generic SCL recovery, runtime PM, mux state, and system suspend/resume.

## Important APIs, Types, And Functions
`struct omap_i2c_dev` contains the adapter, MMIO base, revision flags, FIFO settings, transfer buffers, completion, saved PM register state, errata flags, and recovery state. `omap_i2c_xfer_irq()` and `omap_i2c_xfer_polling()` call `omap_i2c_xfer_common()`. `omap_i2c_xfer_msg()` programs a single transaction; `omap_i2c_xfer_data()` is the IRQ/poll data pump. Probe identifies revision scheme, initializes clocks/FIFOs/errata, requests IRQ, and registers a numbered adapter.

## Control Flow
Probe maps MMIO, obtains speed from OF/platform data, enables runtime PM, detects register scheme/revision, derives errata and FIFO size, selects optional mux state, initializes the controller, requests old-style or threaded IRQ, and registers the adapter with recovery info. Transfer resumes the device, waits until the BB bit is valid and bus is free, optionally sets MPU latency, performs each message, waits for bus free, and autosuspends. IRQ-thread or polling code drains/fills RX/TX, handles ARDY/NACK/AL/overrun/underflow, and completes the command.

## State And Persistence
Runtime state includes active buffer pointer/length, receiver flag, command errors, saved interrupt and clock registers, FIFO threshold, and BB validity. Hardware state is restored in runtime resume via `__omap_i2c_init()`. There is no on-disk persistence.

## Dependencies And Integration Points
Depends on platform/OF matching (`ti,omap2420-i2c` through `ti,omap4-i2c`), runtime PM, pinctrl, mux state, clocks, I2C core, and generic bus recovery. It uses `subsys_initcall()` because I2C may be needed early. Platform data can provide clock rate and MPU wake latency hooks.

## Risks
The BB bit is unreliable after reset on newer revisions, requiring careful validation to avoid corrupting multi-master transfers. Errata I207 and I462 alter interrupt handling and TX timing. FIFO threshold sizing affects latency and overrun/underflow risk. Runtime PM must save/restore interrupt state correctly. NACK with `I2C_M_IGNORE_NAK` deliberately returns success.

## Test Signals
Signals include transfers on OMAP1/2/3/4-compatible revisions, FIFO and no-FIFO modes, high-speed and standard/fast timing, threaded IRQ and atomic polling paths, NACK/arbitration/overrun/underflow injection, BB-valid recovery in multi-master scenarios, SCL recovery through SYSTEST mode, autosuspend/resume, and suspend_noirq/resume_noirq availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-omap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-opal.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-opal.c

## Purpose
Implements an IBM OPAL-backed I2C adapter for Power systems. Linux I2C and SMBus requests are converted into OPAL firmware asynchronous I2C requests instead of driving hardware registers directly.

## Important APIs, Types, And Functions
`i2c_opal_xfer()` implements raw I2C transfers for one-message or simple two-message operations. `i2c_opal_smbus_xfer()` maps supported SMBus operations to `struct opal_i2c_request`. `i2c_opal_send_request()` obtains an OPAL async token, submits the request, waits for completion, translates OPAL return codes, and releases the token. Probe registers an adapter using the `ibm,opal-id` property.

## Control Flow
Module init first checks `FW_FEATURE_OPAL`. Probe reads the firmware bus ID, allocates/configures an adapter, names it from `ibm,port-name` when available, and registers it. Transfers build big-endian OPAL request fields, pass physical buffer addresses through `__pa()`, and block until OPAL asynchronous completion.

## State And Persistence
Adapter state is minimal: the OPAL bus ID is stored in `adapter->algo_data`. OPAL firmware owns actual bus transaction state. The driver keeps no persistent local transaction state or durable data.

## Dependencies And Integration Points
Depends on Power firmware interfaces in `asm/opal.h`, OPAL async token APIs, OF platform devices compatible with `ibm,opal-i2c`, and the Linux I2C/SMBus core. Adapter quirks restrict two-message operations to write-first, same-address combined transfers with a first message length up to four bytes.

## Risks
Buffers are passed by physical address, so callers must provide memory suitable for OPAL access. Functionality is intentionally limited to simple raw and SMBus transactions. OPAL error translation is broad for unknown failures. Async-token acquisition can be interrupted. Firmware behavior is a major external dependency.

## Test Signals
Test on OPAL firmware with raw reads/writes, write-then-read register access, SMBus quick/byte/byte-data/word/I2C-block operations, OPAL NACK/timeout/arbitration error mapping, interrupted token acquisition, adapter naming from device tree, and module init refusal when OPAL is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-opal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-owl.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-owl.c

## Purpose
Implements the Actions Semiconductor Owl SoC I2C controller driver for S500/S700/S900. It supports normal interrupt transfers and atomic polling transfers, repeated-start write-read operations, FIFO management, basic bus-busy checks, and clock-divider programming.

## Important APIs, Types, And Functions
`struct owl_i2c_dev` stores adapter, active message, completion, clock, spinlock, MMIO base, bus frequency, buffer index, and error. `owl_i2c_xfer_common()` implements the shared transfer path. `owl_i2c_xfer_data()` handles FIFO byte movement and error detection. `owl_i2c_interrupt()` completes interrupt-driven transactions. Probe maps resources, validates clock frequency, enables clock, requests IRQ, and registers the adapter.

## Control Flow
Each transfer resets the controller, sets frequency, resets FIFO, checks bus busy, clears arbitration-lost state, programs command flags, optionally writes internal address bytes for repeated-start transactions, preloads write data, configures NACK ignore, starts the command, and waits either for completion or by polling FIFO status. Errors send STOP/release bus and disable the controller at exit.

## State And Persistence
Transfer state is transient in `msg`, `msg_ptr`, and `err`. Hardware state is reset at each transfer and disabled afterward. The driver persists only adapter registration, clock rate, and selected bus frequency.

## Dependencies And Integration Points
Depends on platform/OF matching, clocks, IRQs, completions, spinlocks, I2C adapter quirks, and `readl_poll_timeout_atomic()` for atomic transfers. Adapter quirks allow combined write-first messages with first leg up to six bytes and message lengths up to 240 bytes.

## Risks
The FIFO read loop tests `RFE` as written by the hardware definition, so read semantics must match the controller documentation. Reset and bus-busy checks sleep, requiring lock release/reacquire boundaries. Atomic mode bypasses IRQ completion and depends on polling `CECB`/NACK bits. Only 100 kHz and 400 kHz are accepted.

## Test Signals
Exercise 100 kHz and 400 kHz transfers, single read/write, combined write-read with up to six address bytes, atomic transfers from contexts that require polling, NACK and bus-error handling, arbitration-lost return `-EAGAIN`, FIFO reset timeout, bus busy timeout, and probe validation for invalid clock-frequency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-owl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-parport.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-parport.c

## Purpose
Implements bit-banged I2C over legacy parallel-port adapters. It supports several historical adapter wiring types, optional SMBus Alert for one board type, and binds selected parport numbers through module parameters.

## Important APIs, Types, And Functions
`struct adapter_parm` describes per-adapter SDA/SCL set/get/init line operations. `struct i2c_par` stores the parport device, I2C adapter, bit-bang algorithm data, optional alert client, and list node. `line_set()` and `line_get()` abstract parallel-port register bits. `i2c_parport_attach()` claims a parport and registers an `i2c_bit_add_bus()` adapter; `i2c_parport_detach()` tears it down.

## Control Flow
The parport core calls `match_port` for each port. Attach validates `type` and configured port numbers, allocates state, registers an exclusive parport device, claims the port, sets SDA/SCL high, runs optional init/power line setup, registers the bit-bang I2C bus, optionally creates an SMBus Alert Response Address client and enables parport IRQs, then adds the adapter to a protected list. Detach finds matching adapters, unregisters alert/client and I2C adapter, powers down optional init line, releases parport, and frees state.

## State And Persistence
Module parameters `parport[]` and `type` configure binding. Runtime state is held in a global adapter list protected by `adapter_list_lock`. No durable state exists.

## Dependencies And Integration Points
Depends on parport, `i2c-algo-bit`, I2C core, SMBus alert handling, module parameters, and legacy hardware adapter wiring. It marks adapters as `I2C_CLASS_HWMON`.

## Risks
Wrong `type` can drive incorrect parallel-port pins. Some adapters cannot read SCL, forcing slower timing and reducing clock-stretching visibility. Exclusive parport claiming may fail when another driver owns the port. SMBus Alert depends on parport IRQ support and ARA client registration.

## Test Signals
Test each adapter type with an electrical loopback or known I2C device, verify SDA/SCL idle high and optional init line behavior, scan/read HWMON devices, detach/re-attach ports, module parameter filtering for up to four ports, no-SCL-read slow mode, and SMBus Alert interrupt handling on type 4.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-parport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-pasemi-core.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-pasemi-core.c

## Purpose
Provides the shared PA Semi PWRficient SMBus/I2C controller implementation. It handles FIFO programming, controller reset/clear, optional IRQ completion, raw I2C messages, SMBus protocol operations, functionality reporting, and common adapter registration for glue drivers.

## Important APIs, Types, And Functions
The file operates on `struct pasemi_smbus` from the header. `pasemi_i2c_common_probe()` initializes the adapter and controller and is exported to glue. `pasemi_i2c_xfer()` and `pasemi_i2c_xfer_msg()` implement raw I2C transfers. `pasemi_smb_xfer()` implements SMBus quick, byte, byte/word data, block, process call, and block process call. `pasemi_irq_handler()` completes IRQ-driven waits.

## Control Flow
Before each transfer, `pasemi_smb_clear()` waits for idle and resets FIFOs on stale error/data conditions. Raw I2C writes address/data commands into `REG_MTXFIFO`, waits at STOP for completion, and reads data from `REG_MRXFIFO` for reads. SMBus transfer constructs protocol-specific FIFO sequences, waits for completion, then pulls response data as required. Error paths reset the controller.

## State And Persistence
State is contained in glue-owned `struct pasemi_smbus`: MMIO base, clock divisor, hardware revision, IRQ-use flag, and completion. Hardware status flags in `REG_SMSTA` are cleared after use. There is no durable state.

## Dependencies And Integration Points
Depends on Linux I2C/SMBus core, MMIO accessors, polling helpers, completions, and exported symbols for glue modules. The adapter advertises both I2C and a broad SMBus capability set.

## Risks
FIFO command ordering is protocol-sensitive, especially block reads where the length byte is read before issuing the remaining read count. `use_irq` defaults to false in common probe, so glue must opt in if IRQ completion is desired. Hardware timeout assumptions are based on a documented 25 ms controller timeout but use a 100 ms software timeout. Empty RX FIFO after completion maps to `-ENODATA`.

## Test Signals
Exercise all advertised SMBus protocols, raw multi-message I2C with and without repeated starts, NACK/timeout/arbitration status handling, block length clamping, reset after error, polling and IRQ completion modes, and common-probe reuse from PCI or other glue.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-pasemi-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-pasemi-core.h -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-pasemi-core.h

## Purpose
Defines the PA Semi SMBus shared state and exported entry points for glue drivers.

## Important APIs, Types, And Functions
`PASEMI_HW_REV_PCI` marks original PCI controllers that lack a hardware revision register. `struct pasemi_smbus` contains the parent device, I2C adapter, MMIO base, clock divisor, hardware revision, IRQ mode flag, and IRQ completion. `pasemi_i2c_common_probe()` and `pasemi_irq_handler()` are declared for shared use.

## Control Flow
This header has no standalone runtime flow. Glue drivers allocate/fill `struct pasemi_smbus`, then call `pasemi_i2c_common_probe()`; IRQ-capable glue can route interrupts to `pasemi_irq_handler()`.

## State And Persistence
It defines in-memory state only. Adapter registration and controller state are managed by the core implementation using this struct.

## Dependencies And Integration Points
Includes Linux atomic, clock, I2C, SMBus alert, IO, device, completion, and kernel headers. It is included by the shared core and PCI wrapper.

## Risks
Glue must initialize `dev`, `ioaddr`, `clk_div`, and `hw_rev` correctly before common probe. If `use_irq` is set without a requested IRQ and handler, transfers may wait forever until timeout. The header does not enforce ownership or lifecycle rules.

## Test Signals
Compile tests for all glue users, probe tests confirming initialized fields, IRQ handler linkage if IRQ mode is enabled, and static analysis for missing `ioaddr` or invalid clock divisors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-pasemi-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-pasemi-pci.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-pasemi-pci.c

## Purpose
Provides the PCI wrapper for PA Semi PWRficient SMBus controllers. It claims the PCI I/O BAR, maps it, initializes shared PA Semi SMBus state, and delegates adapter setup to `i2c-pasemi-core.c`.

## Important APIs, Types, And Functions
`pasemi_smb_pci_probe()` is the only probe path. It allocates `struct pasemi_smbus`, checks BAR0 is I/O space, sets the 100 kHz clock divisor, marks the hardware revision as PCI legacy, requests the I/O region, maps the BAR with `pcim_iomap()`, sets the HWMON class, and calls `pasemi_i2c_common_probe()`.

## Control Flow
The PCI driver matches device ID `0x1959:0xa003`. On probe it validates resources, initializes state, calls the common core, and stores driver data. There is no explicit remove hook because devm/pcim cleanup and devm adapter registration handle teardown.

## State And Persistence
State is the allocated `struct pasemi_smbus` tied to the PCI device. It persists for the device lifetime only. No durable state exists.

## Dependencies And Integration Points
Depends on PCI core, I/O port resource management, `pcim_iomap()`, I2C core through the shared PA Semi implementation, and HWMON class scanning expectations.

## Risks
Only 100 kHz is selected even though a 400 kHz divider constant exists, so higher-speed capability is unused here. Probe requires BAR0 I/O space and fails on memory BAR variants. Lack of an IRQ request means the shared core remains in polling mode unless changed by future glue.

## Test Signals
Probe the matching PCI device, verify BAR claim/map failures return expected errors, confirm adapter appears as HWMON-class I2C, run SMBus transactions through the shared core, and hot-unplug/unbind to validate managed cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-pasemi-pci.c -->
