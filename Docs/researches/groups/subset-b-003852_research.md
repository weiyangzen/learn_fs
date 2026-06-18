# subset-b-003852 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-microchip-corei2c.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-microchip-corei2c.c

Purpose: Microchip CoreI2C platform driver for MPFS hard I2C peripherals and CoreI2C soft FPGA cores. It exposes a normal I2C adapter plus an SMBus emulation path over the same interrupt-driven master state machine.

Important APIs/types: `struct mchp_corei2c_dev` stores MMIO base, clock, active message queue, transfer completion, cached ISR status, current address/buffer/length, and repeated-start state. Main entry points are `mchp_corei2c_probe()`, `mchp_corei2c_xfer()`, `mchp_corei2c_smbus_xfer()`, `mchp_corei2c_isr()`, `mchp_corei2c_handle_isr()`, and the `mchp_corei2c_algo` `i2c_algorithm`.

Control flow: probe maps registers, obtains IRQ and clock, reads `clock-frequency`, programs a CoreI2C divisor, enables the clock, and registers the adapter. Transfers seed `msg_queue`, `total_num`, `current_num`, `addr`, `msg_len`, and `buf`, then set `CTRL_STA`; subsequent progress is driven by interrupt status values. The ISR reads `CORE_I2C_STATUS`, handles start/address/data ACK/NACK/arbitration-lost states, reads or writes `CORE_I2C_DATA`, emits STOP when needed, advances to the next message, and completes the wait.

State and persistence: persistent device state is per-platform-device and held in `struct mchp_corei2c_dev`; runtime transaction state is reused for each transfer and completed through `msg_complete`. Hardware persistence is limited to controller enable/divisor bits and the clock state. Remove disables the clock and unregisters the adapter.

Dependencies and integration: integrates with platform devices, OF compatibles `microchip,mpfs-i2c` and `microchip,corei2c-rtl-v7`, the Linux I2C core, IRQ handling, MMIO byte accessors, and the common clock framework. SMBus operations are translated into `i2c_msg` arrays before using the adapter transfer path.

Risks: the state machine is sensitive to status-code ordering and only marks selected failures, so unexpected status values can silently fall through until timeout. `mchp_corei2c_smbus_xfer()` advertises SMBus emulation but the `I2C_SMBUS_QUICK` case returns without issuing a bus transaction. Shared IRQ handling depends on `idev->buf` being valid to distinguish own interrupts. Timeout recovery returns `-ETIMEDOUT` but does not reset the controller in the transfer path.

Test signals: useful tests include probe with valid and invalid `clock-frequency`, raw I2C write/read/repeated-start transactions, SMBus byte/word/block cases, arbitration loss and NACK status injection, timeout handling, shared IRQ noise, and remove/unbind clock cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-microchip-corei2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-mlxbf.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-mlxbf.c

Purpose: Mellanox/NVIDIA BlueField SMBus/I2C platform driver. It supports BlueField-1, BlueField-2, and BlueField-3 ACPI devices, master SMBus transfers, I2C slave registration, slave interrupt handling, timing programming, shared resource mapping, and chip-specific PLL frequency calculation.

Important APIs/types: `struct mlxbf_i2c_priv` owns the adapter, bus number, chip info, resource pointers for timer/master/slave/cause/coalesce regions, IRQ, core frequency, and registered slave clients. `struct mlxbf_i2c_chip_info` captures chip type, shared resources, PLL callback, and register offsets. `struct mlxbf_i2c_smbus_request` and `struct mlxbf_i2c_smbus_operation` encode master operations. Key functions include `mlxbf_i2c_smbus_xfer()`, `mlxbf_i2c_smbus_start_transaction()`, `mlxbf_i2c_smbus_enable()`, `mlxbf_i2c_irq()`, `mlxbf_i2c_reg_slave()`, `mlxbf_i2c_unreg_slave()`, `mlxbf_i2c_init_timings()`, and `mlxbf_i2c_probe()`.

Control flow: ACPI probe selects chip data and UID bus number. Probe maps either legacy combined SMBus space or split timer/master/slave resources, maps master/slave cause regions, calculates or defaults the core PLL frequency, initializes BlueField-1 GPIO muxing, writes timing registers, initializes slave cause interrupts, requests a shared IRQ, and registers a numbered adapter. Master SMBus calls translate Linux SMBus sizes into one to three internal operations, acquire the hardware gateway lock, wait for the master FSM to be idle, write a data descriptor, run write and/or read phases, poll cause/status bits, copy read data back, reset the read FSM state, and clear the gateway lock.

State and persistence: persistent global state includes shared resource structs, resource mutexes, `mlxbf_i2c_corepll_frequency`, and `mlxbf_i2c_bus_count`. Per-device state tracks resource mappings and slave client slots. Hardware state persists in timing registers, GPIO muxing on BlueField-1, slave address configuration slots, cause masks, and ready bits. Remove releases memory regions and frees shared resources only when the global bus count reaches zero.

Dependencies and integration: depends on ACPI IDs `MLNXBF03`, `MLNXBF23`, and `MLNXBF31`, platform resources, MMIO accessors including big-endian descriptor access, I2C/SMBus core APIs, I2C slave backend callbacks, mutexes, bitfield helpers, and shared BlueField resource layouts. It registers `smbus_xfer`, `functionality`, `reg_slave`, and `unreg_slave` hooks.

Risks: many operations use `readl_poll_timeout_atomic()` without checking its return in some paths, then infer failure from cause/status bits. `mlxbf_i2c_reg_slave()` logs registration failure but returns 0 unconditionally, which can hide a full slave table. Shared resource release is coordinated by bus count and assumes probe/remove ordering remains sane. Descriptor packing uses unaligned casts and endian-swapping assumptions. Slave read handling pre-fills a full 128-byte response regardless of the master's expected byte count. Unsupported or malformed SMBus operation combinations are mostly constrained by the Linux SMBus entry point, not by the internal request builder.

Test signals: cover ACPI matching for all three chip types, legacy versus split resource layouts, PLL fallback, 100/400/1000 kHz timing writes, byte/word/block/process-call SMBus master operations with NACK/timeout/arbitration causes, I2C slave register/unregister capacity and error propagation, shared IRQ filtering, coalesce interrupt source decoding, and multi-adapter probe/remove resource lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-mlxbf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-mlxcpld.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-mlxcpld.c

Purpose: Mellanox CPLD LPC-I2C bridge driver. It exposes a numbered I2C adapter backed by CPLD LPC registers, with optional extended transfer sizes, SMBus block support, and platform-data controlled bus frequency.

Important APIs/types: `struct mlxcpld_i2c_priv` stores adapter, LPC base address, mutex, current transfer descriptor, device, SMBus-block capability, and polling interval. `struct mlxcpld_i2c_curr_xfer` tracks command direction, address width, data length, message count, and message pointer. Main functions are `mlxcpld_i2c_xfer()`, `mlxcpld_i2c_wait_for_free()`, `mlxcpld_i2c_wait_for_tc()`, `mlxcpld_i2c_xfer_msg()`, `mlxcpld_i2c_set_frequency()`, and `mlxcpld_i2c_probe()`.

Control flow: probe initializes the private object, optionally reads platform regmap data to set 100/400/1000 kHz timing, reads the CPLD capability register, selects adapter quirks for normal or extended data windows, enables SMBus block mode if advertised, and adds a numbered adapter. A transfer validates message count, buffers, 7-bit address equality, and combined length, waits for the bridge to be free, soft-resets on stuck busy, records transfer layout, writes data/address counts and payload bytes into the LPC data window, starts by writing the command register, polls status until ACK/NACK/timeout, then copies read data back.

State and persistence: adapter state is per platform device. Transfer state is stored in `priv->xfer` under `priv->lock`. Hardware state persists in CPLD timing/capability/status registers. There is no suspend/resume handling; remove deletes the adapter and destroys the mutex.

Dependencies and integration: depends on LPC `inb/inw/inl` and `outb/outw/outl`, Linux I2C core quirks, platform data from `mlxreg_core_hotplug_platform_data`, and regmap for frequency configuration. It integrates with Mellanox platform code through completion notification after adapter registration.

Risks: LPC bulk helpers cast byte buffers to `u16`/`u32`, so alignment and endian assumptions matter. `comm_len` is an 8-bit sum and relies on adapter quirks to bound message lengths. Polling is the only completion mechanism despite comments mentioning interrupts. Reset only toggles a control bit and may not recover severe bridge faults. The adapter template is static and copied per instance, so probe must fully overwrite instance-specific fields.

Test signals: test normal and extended capability values, SMBus block reads with valid and invalid returned lengths, write-then-read combined messages with address widths up to 4 bytes, busy reset recovery, NACK mapping to `-ENXIO`, frequency platform data, and numbered adapter notification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-mlxcpld.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-mpc.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-mpc.c

Purpose: Freescale/MPC I2C adapter driver for MPC107/Tsi107 and MPC52xx/512x/8xxx-style controllers. It provides an interrupt-driven I2C master, bus recovery workarounds, clock divider setup, deprecated timeout bindings, and PM save/restore for divider registers.

Important APIs/types: `struct mpc_i2c` holds MMIO base, IRQ, waitqueue, spinlock, adapter, divider shadows, control bits, action state, active message array, byte counters, result code, ACK expectation, and erratum flag. `enum mpc_i2c_action` drives the transfer state machine. Key functions include `mpc_xfer()`, `mpc_i2c_execute_msg()`, `mpc_i2c_do_action()`, `mpc_i2c_do_intr()`, `mpc_i2c_isr()`, `fsl_i2c_probe()`, and `fsl_i2c_bus_recovery()`.

Control flow: probe maps registers, requests a shared IRQ, enables an optional clock, determines clock setup from OF match data and properties, parses legacy timeout properties, sets bus recovery, and registers a numbered adapter. Transfers install the message array in `i2c->msgs`, initialize action `START`, enable controller interrupts, and write the first address byte. Interrupts clear `MIF`, validate completion/arbitration/ACK status, then advance actions through start/restart, read begin, byte read/write, and stop. Completion wakes the waitqueue; timeout or low-level errors trigger `i2c_recover_bus()` and STOP/bus-free polling.

State and persistence: runtime transfer state is protected by the spinlock and cleared after each `mpc_xfer()`. Persistent adapter state includes selected `real_clk`, timeout, erratum flag, and saved `FDR`/`DFSRR` across suspend/resume. Hardware state includes clock dividers, control/status registers, and bus recovery side effects.

Dependencies and integration: integrates with OF compatibles for MPC5200, MPC5121, MPC8313, MPC8543, MPC8544, and fallback `fsl-i2c`; PowerPC/FSL helper APIs supply bus/sys clock, PVR/SVR, and global utility mappings. It uses the I2C core, IRQs, waitqueues, spinlocks, clock framework, and `i2c_bus_recovery_info`.

Risks: clock-divider tables are selected by SoC-specific code and can silently choose lower actual speeds. Several deprecated timeout properties are still accepted and converted with coarse jiffy granularity. Erratum A004447 and generic nine-pulse recovery manipulate bus lines directly and are hardware timing sensitive. Block-read length mutates `msg->len`, so callers must tolerate SMBus receive-length semantics. The static `mpc_ops` adapter template has mutable timeout shared before assignment into each device.

Test signals: cover OF clock setup across 52xx/512x/8xxx paths, preserve-clocking mode, interrupt-driven read/write/repeated-start transfers, SMBus block reads, arbitration loss/NACK/timeout recovery, erratum A004447 recovery, suspend/resume divider restore, and all legacy timeout property names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-mpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-mt65xx.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-mt65xx.c

Purpose: MediaTek MT65xx-family I2C master driver covering many SoCs with differing register maps, timing engines, DMA synchronization capabilities, PMIC pin routing, and DMA address widths. It always performs transfers through the APDMA-style engine.

Important APIs/types: `struct mtk_i2c` stores adapter, completion, firmware timings, I2C and DMA MMIO bases, clock bulk array, PMIC/push-pull flags, IRQ status, selected speed, operation type, timing registers, auto-restart state, and compatible data. `struct mtk_i2c_compatible` captures per-SoC quirks, register offsets, timing capabilities, DMA sync flags, and DMA mask width. Main functions are `mtk_i2c_probe()`, `mtk_i2c_transfer()`, `mtk_i2c_do_transfer()`, `mtk_i2c_irq()`, `mtk_i2c_set_speed()`, and `mtk_i2c_init_hw()`.

Control flow: probe maps I2C and DMA resources, obtains IRQ, parses `clock-frequency`, `clock-div`, PMIC and push-pull properties, gets required and optional clocks, computes speed/timing registers from parent clock and AC timing constraints, sets DMA mask when needed, initializes hardware with clocks enabled, requests IRQ, and adds the adapter. Transfer enables optional bus regulator and clocks, decides whether to use auto-restart or combined write-read `WRRD`, configures interrupt masks, transfer lengths, DMA buffers and addresses, starts DMA and I2C, waits for completion, unmaps/copies buffers, checks timeout and ACK errors, and disables clocks/regulator.

State and persistence: per-device compatible data and computed timing state persist after probe. Each transfer resets `irq_stat`, `op`, `auto_restart`, and `ignore_restart_irq`. Hardware is reinitialized on probe, resume, ACK error, and timeout. Suspend marks the adapter suspended and unprepares clocks; resume prepares clocks, reinitializes hardware, disables clocks, and marks the adapter resumed.

Dependencies and integration: integrates with OF compatibles from MT2712 through MT8192, the I2C core, DMA mapping APIs, optional bus regulator, common clock bulk APIs, firmware I2C timing parser, completions, IRQs, and per-SoC adapter quirks such as no-zero-length or combined write-then-read limits.

Risks: DMA is mandatory, so small transfers still depend on DMA-safe buffer allocation and mapping. Timing search can leave registers at the last successful candidate and reports little detail when no candidate is found. Several SoC flags interact in subtle ways (`auto_restart`, `aux_len_reg`, `dma_sync`, `apdma_sync`, `ltiming_adjust`). Timeout and ACK errors reset hardware while clocks are still active, so error paths must preserve the enable/disable balance. `num` is passed into `mtk_i2c_do_transfer()` even when a single message is being processed, which makes the transfer-count programming depend on surrounding auto-restart logic.

Test signals: exercise all compatible data variants at build/probe level, 100 kHz/400 kHz/1 MHz/high-speed timing calculations, regulator enable failures, DMA mapping failures for read/write/WRRD, ACK error and timeout reinitialization, auto-restart multi-message sequences, high-speed ignored restart IRQ behavior, suspend/resume clock reprepare, and no-zero-length quirk behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-mt65xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-mt7621.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-mt7621.c

Purpose: MediaTek/Ralink MT7621 I2C host driver. It implements a simple polling-based master using controller page commands for start, stop, read, write, and 10-bit address support.

Important APIs/types: `struct mtk_i2c` stores MMIO base, device, adapter, requested bus frequency, computed divider, flags, and clock. Important functions are `mtk_i2c_xfer()`, `mtk_i2c_cmd()`, `mtk_i2c_wait_idle()`, `mtk_i2c_check_ack()`, `mtk_i2c_reset()`, `mtk_i2c_init()`, and `mtk_i2c_probe()`.

Control flow: probe maps registers, enables the clock, reads `clock-frequency` with a 100 kHz default, computes/clamps the clock divider, resets the controller, and adds the adapter. A transfer loops over messages, waits idle, emits START, writes 7-bit or 10-bit address bytes, checks address ACK unless `I2C_M_IGNORE_NAK`, then transfers up to eight bytes per page through `SM0D0/SM0D1`. Reads use `READ` or `READ_LAST`; writes copy bytes into two data registers and verify ACK bits. After all messages it emits STOP; timeout paths dump registers and reset hardware.

State and persistence: persistent state is limited to base, clock, bus frequency, divider, and adapter registration. There is no interrupt state or PM state. Hardware reset is used at init and after timeouts.

Dependencies and integration: depends on OF compatible `mediatek,mt7621-i2c`, the common clock framework, reset controller via `device_reset()`, polling I/O helpers, and the I2C core. Functionality advertises I2C, SMBus emulation, and protocol mangling.

Risks: all completion is polling with a 1 second timeout. `memcpy(data, ...)` uses an uninitialized stack `u32 data[2]` for short writes unless the copied bytes cover all transmitted bytes; page length bounds make this usually benign for MMIO writes but still fragile. Multi-message transfers send START for each message and only one final STOP, so repeated-start semantics depend on hardware behavior. Reset failure is logged but not propagated in `mtk_i2c_reset()`.

Test signals: cover default and zero `clock-frequency`, divider clamping, 7-bit and 10-bit addressing, read/write page lengths 1 through 8 and longer multi-page messages, `I2C_M_IGNORE_NAK`, timeout reset/dump paths, and final STOP failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-mt7621.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-mv64xxx.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-mv64xxx.c

Purpose: Marvell mv64xxx/Orion and compatible Allwinner I2C controller driver. It supports interrupt-driven and atomic polling transfers, 10-bit addressing, runtime PM, bus recovery, clock/reset control, register-layout variants, and an optional Marvell transaction-generator offload path.

Important APIs/types: `struct mv64xxx_i2c_data` owns message state, FSM state/action, control bits, register offsets, clock factors, waitqueue, spinlock, adapter, offload flags, errata flags, runtime PM resources, and recovery info. `struct mv64xxx_i2c_regs` describes register layout variants. Key functions are `mv64xxx_i2c_xfer()`, `mv64xxx_i2c_xfer_atomic()`, `mv64xxx_i2c_execute_msg()`, `mv64xxx_i2c_fsm()`, `mv64xxx_i2c_do_action()`, `mv64xxx_i2c_intr()`, `mv64xxx_i2c_offload_xfer()`, `mv64xxx_of_config()`, and runtime PM callbacks.

Control flow: probe maps registers, gets optional clocks and reset, configures baud factors from platform data or OF, initializes optional pinctrl recovery, enables runtime PM, requests IRQ, and registers a numbered adapter. Normal transfer resumes the device, stores the message array, chooses offload for one-message or write-read transactions of 1-8 bytes when allowed, otherwise starts the FSM. The FSM interprets controller status values, chooses actions for address bytes, data bytes, restarts, receive ACK control, STOP, and error recovery. Completion wakes a waitqueue or is polled in atomic mode.

State and persistence: active message pointers and counters exist only during transfer. Runtime PM suspend asserts reset and disables clocks; resume enables clocks, resets hardware, and initializes registers. Persistent configuration includes baud factors, register layout, offload enablement, errata delay, inverted clear semantics, and bus recovery pinctrl.

Dependencies and integration: integrates with OF compatibles for Allwinner sun4i/sun6i and Marvell mv64xxx/mv78230 variants, legacy `mv643xx_i2c` platform data, clocks, resets, pinctrl-based bus recovery, runtime PM, IRQs, and the I2C core including `.xfer_atomic`.

Risks: the FSM is broad and status-code dependent; unexpected status triggers hardware reinit and bus recovery. Timeout abort attempts can still leave `block` set and require full hardware reinit. Offload handles only up to 8 bytes and has separate interrupt/status semantics from the normal FSM. Some cleanup paths manually call runtime suspend based on PM state. Atomic polling re-enters the IRQ handler and relies on a small delay for status-register update ordering.

Test signals: cover normal and atomic transfers, 7-bit and 10-bit addressing, repeated starts, read/write NACKs, arbitration loss, timeout abort and recovery, offloaded single read/write and write-read paths, runtime suspend/resume, Allwinner inverted IFLG clearing, mv78230 errata delay, and probe via OF and legacy platform data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-mv64xxx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-mxs.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-mxs.c

Purpose: Freescale MXS/i.MX23/i.MX28 I2C bus driver. It combines PIO transfers for small messages with DMA engine transfers for larger messages and programs timing registers from a fixed 24 MHz block clock.

Important APIs/types: `struct mxs_i2c_dev` stores device type, MMIO registers, completion, last command error, adapter, timing register values, DMA channel, PIO command/data buffers, scatterlists, and read/write DMA mode. Important functions include `mxs_i2c_xfer()`, `mxs_i2c_xfer_msg()`, `mxs_i2c_pio_setup_xfer()`, `mxs_i2c_dma_setup_xfer()`, `mxs_i2c_isr()`, `mxs_i2c_reset()`, `mxs_i2c_derive_timing()`, and `mxs_i2c_probe()`.

Control flow: probe identifies i.MX23 versus i.MX28, maps registers, requests IRQ, derives timing from `clock-frequency` or 100 kHz default, requests the shared rx-tx DMA channel, resets hardware, and registers a numbered adapter. Each message chooses PIO for reads up to 4 bytes and writes under 7 bytes, otherwise DMA. PIO writes chunk bytes through the data register with optional clock retention; PIO reads issue a select then read command. DMA queues PIO register writes and memory/device SG descriptors, waits on completion from the last descriptor callback, then checks command error.

State and persistence: timing register values persist in software and are restored by `mxs_i2c_reset()`. `cmd_err` is set by ISR or PIO error checks per transfer. DMA scatterlists and command buffers are reused in the device object. Remove unregisters the adapter, releases the DMA channel, and soft-resets the block.

Dependencies and integration: depends on OF compatibles `fsl,imx23-i2c` and `fsl,imx28-i2c`, STMP reset helper, DMA engine and MXS DMA flags, I2C core, completions, IRQs, and DMA-safe I2C message buffers. It registers at `subsys_initcall`, likely to be available early for dependent devices.

Risks: i.MX23 requires reset after every transfer because of documented PIO/DMA residue behavior. DMA setup has several descriptor stages and must unmap the right SG entries on partial failure. PIO read is hard-limited by `BUG_ON(msg->len > 4)` but selection logic should prevent larger PIO reads. Timeout cleanup calls `mxs_i2c_dma_finish()` even after the callback might have raced, so completion ordering matters. Timing derivation clamps out-of-range speeds and may silently run at a different rate with only warnings.

Test signals: cover i.MX23 and i.MX28 compatibles, PIO read/write boundary lengths, DMA read/write paths, NAK and early termination IRQs, DMA timeout reset, timing clamping for high/low requested speeds, no-zero-length quirk, and remove-time DMA release/reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-mxs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-nct6694.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-nct6694.c

Purpose: Nuvoton NCT6694 USB-backed I2C adapter driver. It registers up to six I2C adapters exposed through an MFD parent and sends each I2C message as an NCT6694 USB command payload.

Important APIs/types: `struct nct6694_i2c_deliver` is the packed command payload containing port, baud rate, address, write/read counts, and 64-byte write/read buffers. `struct nct6694_i2c_data` holds the parent `struct nct6694`, adapter, reusable payload, port, and baud setting. Important functions are `nct6694_i2c_xfer()`, `nct6694_i2c_set_baudrate()`, `nct6694_i2c_probe()`, and `nct6694_i2c_ida_free()`.

Control flow: probe allocates per-adapter data, obtains a port from the parent IDA, registers cleanup for the IDA slot, validates the module parameter baud-rate entry for that port, initializes adapter fields and quirks, and uses `devm_i2c_add_adapter()`. Transfer loops through messages, clears the deliver payload, fills port/baud/8-bit address and either read or write count/data, sends the command with `nct6694_write_msg()`, and copies returned read bytes into the I2C message.

State and persistence: port allocation persists until devm cleanup. Baud-rate state comes from the module parameter array `br_reg[]`, defaulting invalid values back to 100 kHz. The reusable deliver payload is per adapter. No hardware state is programmed outside each command payload.

Dependencies and integration: depends on the NCT6694 MFD parent and `nct6694_write_msg()`, IDA allocation in the parent object, Linux platform bus, module parameters, I2C core, and adapter quirks limiting read/write length to 64 bytes.

Risks: no explicit locking protects the reusable payload, relying on I2C core adapter serialization. Each `i2c_msg` is delivered as a separate command, so combined I2C repeated-start semantics are not represented. Only 7-bit `i2c_8bit_addr_from_msg()` addressing is used despite advertising broad SMBus emulation. Read success depends on the parent command both sending and receiving through the same payload object.

Test signals: test port allocation for six adapters and exhaustion, baud-rate parameter validation, 64-byte read/write limits, read and write command payload contents, parent command failure propagation, adapter devm cleanup, and multi-message behavior with devices that require repeated starts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-nct6694.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-nforce2.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-nforce2.c

Purpose: PCI SMBus driver for NVIDIA nForce2/3/4/5xx chipsets. It exposes one or two SMBus adapters using I/O-port register access and supports common SMBus protocol operations, optional block operations, PEC bits, and abort on selected chipsets.

Important APIs/types: `struct nforce2_smbus` contains adapter, I/O base, region size, block-operation support, and abort capability. Main functions are `nforce2_access()`, `nforce2_check_status()`, `nforce2_abort()`, `nforce2_probe_smb()`, `nforce2_probe()`, and `nforce2_remove()`. `smbus_algorithm` provides `.smbus_xfer` and `.functionality`.

Control flow: PCI probe allocates two bus structs, enables block/abort flags for selected device IDs, probes SMBus 1 from BAR4 or legacy config register `0x50`, probes SMBus 2 from BAR5 or `0x54` unless DMI-blacklisted, requests I/O regions, and registers adapters. SMBus access writes command/data/count registers according to requested protocol, writes the target address and protocol register to start, polls status up to 100 ms, optionally aborts on timeout, and reads back byte/word/block data for reads.

State and persistence: adapter state persists per PCI device until remove. There is no interrupt or PM state. I/O regions are reserved while adapters exist. The DMI blacklist disables the second bus for a known unsafe board.

Dependencies and integration: depends on PCI IDs for nForce SMBus devices, ACPI region conflict checking, DMI matching, I/O port accessors, Linux SMBus core, and resource reservation. It registers hardware-monitor class adapters.

Risks: the driver assumes at most one nForce device with two interfaces. Polling status treats any status bits besides DONE as failure without deeper decoding. Block write loops all 32 bytes regardless of requested length after programming the length. Older nonstandard BAR fallback relies on raw PCI config words. The abort mechanism exists only on selected devices and may fail to reset the bus.

Test signals: cover BAR and legacy-base discovery, ACPI region conflicts, DMI second-bus blacklist, quick/byte/byte-data/word/block read and write, PEC protocol bit setting, block length validation, timeout with and without abort support, partial adapter registration where only one bus succeeds, and remove resource release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-nforce2.c -->
