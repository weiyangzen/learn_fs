# sources/distributed-fs/ceph-client/drivers/i3c/master/dw-i3c-master.h

Purpose: Shared DesignWare I3C master header for the base driver and platform wrappers.

Important APIs/types/functions: `DW_I3C_MAX_DEVS` caps the DAT mirror. `struct dw_i3c_master_caps` stores FIFO depths. `struct dw_i3c_dat_entry` mirrors address, I2C flag, and IBI device. `struct dw_i3c_master` embeds `i3c_master_controller` and stores device, MMIO, clocks, reset, queue state, timing snapshots, DAT metadata, quirks, platform ops, and hotjoin work. `struct dw_i3c_platform_ops` provides `init` and `set_dat_ibi`. `dw_i3c_common_probe/remove()` are external entry points.

Control flow: No direct runtime flow. The base driver calls `init()` during early bus init and `set_dat_ibi()` while updating DAT entries for IBI enable/disable.

State and persistence: Defines persistent per-controller state. Timing snapshots and DAT mirror support runtime PM restore. `devs_lock` protects IRQ-visible `ibi_dev` pointers.

Dependencies/integration: Clocks, reset, I3C master core, platform devices, Linux types, base DW driver, and AST2600 wrapper.

Risks: Wrappers must embed `struct dw_i3c_master` consistently for `container_of()`. `set_dat_ibi()` runs under a spinlock and must not sleep. Hardware with more than 32 devices would exceed the fixed mirror.

Test signals: Build standalone DW and wrapper drivers; inject platform `init` failure; verify DAT IBI hook execution and runtime PM restore behavior.
