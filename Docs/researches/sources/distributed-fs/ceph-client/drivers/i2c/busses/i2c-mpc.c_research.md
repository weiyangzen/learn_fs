# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-mpc.c

Purpose: Freescale/MPC I2C adapter driver for MPC107/Tsi107 and MPC52xx/512x/8xxx-style controllers. It provides an interrupt-driven I2C master, bus recovery workarounds, clock divider setup, deprecated timeout bindings, and PM save/restore for divider registers.

Important APIs/types: `struct mpc_i2c` holds MMIO base, IRQ, waitqueue, spinlock, adapter, divider shadows, control bits, action state, active message array, byte counters, result code, ACK expectation, and erratum flag. `enum mpc_i2c_action` drives the transfer state machine. Key functions include `mpc_xfer()`, `mpc_i2c_execute_msg()`, `mpc_i2c_do_action()`, `mpc_i2c_do_intr()`, `mpc_i2c_isr()`, `fsl_i2c_probe()`, and `fsl_i2c_bus_recovery()`.

Control flow: probe maps registers, requests a shared IRQ, enables an optional clock, determines clock setup from OF match data and properties, parses legacy timeout properties, sets bus recovery, and registers a numbered adapter. Transfers install the message array in `i2c->msgs`, initialize action `START`, enable controller interrupts, and write the first address byte. Interrupts clear `MIF`, validate completion/arbitration/ACK status, then advance actions through start/restart, read begin, byte read/write, and stop. Completion wakes the waitqueue; timeout or low-level errors trigger `i2c_recover_bus()` and STOP/bus-free polling.

State and persistence: runtime transfer state is protected by the spinlock and cleared after each `mpc_xfer()`. Persistent adapter state includes selected `real_clk`, timeout, erratum flag, and saved `FDR`/`DFSRR` across suspend/resume. Hardware state includes clock dividers, control/status registers, and bus recovery side effects.

Dependencies and integration: integrates with OF compatibles for MPC5200, MPC5121, MPC8313, MPC8543, MPC8544, and fallback `fsl-i2c`; PowerPC/FSL helper APIs supply bus/sys clock, PVR/SVR, and global utility mappings. It uses the I2C core, IRQs, waitqueues, spinlocks, clock framework, and `i2c_bus_recovery_info`.

Risks: clock-divider tables are selected by SoC-specific code and can silently choose lower actual speeds. Several deprecated timeout properties are still accepted and converted with coarse jiffy granularity. Erratum A004447 and generic nine-pulse recovery manipulate bus lines directly and are hardware timing sensitive. Block-read length mutates `msg->len`, so callers must tolerate SMBus receive-length semantics. The static `mpc_ops` adapter template has mutable timeout shared before assignment into each device.

Test signals: cover OF clock setup across 52xx/512x/8xxx paths, preserve-clocking mode, interrupt-driven read/write/repeated-start transfers, SMBus block reads, arbitration loss/NACK/timeout recovery, erratum A004447 recovery, suspend/resume divider restore, and all legacy timeout property names.
