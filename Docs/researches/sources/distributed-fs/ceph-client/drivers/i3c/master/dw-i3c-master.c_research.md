# sources/distributed-fs/ceph-client/drivers/i3c/master/dw-i3c-master.c

Purpose: Synopsys DesignWare MIPI I3C master driver and common implementation for wrappers. It handles queues, DAT management, timing, DAA, CCC/private/I2C transfers, IBI/hotjoin, runtime PM, clock/reset restore, and platform quirks.

Important APIs/types/functions: Private `struct dw_i3c_cmd/xfer` and `dw_i3c_i2c_dev_data` complement `struct dw_i3c_master` from the header. `dw_mipi_i3c_ops` implements all core ops. `dw_i3c_common_probe()` and `dw_i3c_common_remove()` are exported for wrapper drivers.

Control flow: Common probe maps MMIO, enables clocks/reset, initializes queues/locks, requests IRQ, enables PM, reads FIFO/DAT capacities, applies quirks, initializes hotjoin work, and registers the master. Bus init runs platform init, configures timing, assigns master address, sets master info, configures interrupts/IBI rejection, and enables hardware. Transfers allocate xfers, check FIFO depths, preload TX FIFO, program command queues, wait for IRQ completion, and reset on timeout/error. DAA preprograms DAT entries, issues ENTDAA, and adds discovered devices.

State and persistence: Tracks FIFO depths, DAT start/maxdevs, free DAT bitmap, per-slot address/IBI state, SIR reject mask, timing snapshots, PM quirks, and transfer queue. Runtime resume restores timing, addresses, interrupts, and enable state.

Dependencies/integration: I3C core ops, `internals.h`, runtime PM, clk/reset/pinctrl, platform MMIO/IRQ, OF/ACPI match data, and optional platform ops. AST2600 uses the exported common helpers.

Risks: Timeout/error recovery resets queues and resumes controller state. DAA infers new device count from response length. IBI SIR reject bit mapping can collide according to hardware rules. Hotjoin enable holds PM until disabled. Platform DAT hook must not sleep.

Test signals: Pure/mixed timing, ACPI/OF quirks, runtime suspend/resume with DAT entries, CCC get/set, FIFO depth limits, DAA, hotjoin DAA, IBI payload and slot exhaustion, `dev_nack_retry_count`, shutdown IRQ masking, and wrapper probe/remove.
