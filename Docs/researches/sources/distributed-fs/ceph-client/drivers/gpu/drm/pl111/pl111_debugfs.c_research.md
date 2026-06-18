# sources/distributed-fs/ceph-client/drivers/gpu/drm/pl111/pl111_debugfs.c

## Purpose
Provides a debugfs register dump for the PL111 DRM driver.

## Important APIs, Types, and Functions
`pl111_reg_defs[]` maps selected CLCD register offsets to names. `pl111_debugfs_regs()` prints each register value with `seq_printf()`. `pl111_debugfs_init()` registers a single `regs` debugfs file through `drm_debugfs_create_files()`.

## Control Flow
When debugfs is enabled and the driver initializes its minor, `pl111_debugfs_init()` creates the file. Reading the file obtains the DRM device from `drm_info_node`, accesses `dev_private`, iterates the static register table, and reads MMIO offsets from `priv->regs`.

## State and Persistence
No persistent state. It exposes a live snapshot of hardware registers including timing, base addresses, control, IRQ enable/status/clear, and cursor registers.

## Dependencies and Integration Points
Depends on DRM debugfs/file helpers, seq_file, MMIO `readl()`, and register/private definitions from `pl111_drm.h`. It is conditionally built by the Makefile under `CONFIG_DEBUG_FS`.

## Risks and Edge Cases
Reads assume `priv->regs` remains valid while debugfs exists, which is tied to DRM device lifetime. Register lists are PL111-oriented and may not include all PL110/Nomadik-specific registers.

## Test Signals
With debugfs enabled, `/sys/kernel/debug/dri/*/regs` should exist for PL111 and show plausible values while modes are enabled/disabled. Build without debugfs should omit the object cleanly.
