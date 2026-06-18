<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_debugfs.c

## Purpose
Provides minimal debugfs registration for the Broadcom `bng_re` RoCE driver, creating a driver root and one directory per PCI device.

## Important APIs, Types, And Functions
- `static struct dentry *bng_re_debugfs_root` stores the root debugfs dentry for the module.
- `bng_re_register_debugfs()` creates `/sys/kernel/debug/bng_re`.
- `bng_re_unregister_debugfs()` removes the root dentry.
- `bng_re_debugfs_add_pdev()` creates a child directory named from `dev_name(&pdev->dev)` using `rdev->aux_dev->pdev`.
- `bng_re_debugfs_rem_pdev()` recursively removes the device-specific directory and clears `rdev->dbg_root`.

## Control Flow
Module init calls `bng_re_register_debugfs()` before auxiliary driver registration. Device initialization calls `bng_re_debugfs_add_pdev()` after the firmware channel and stats setup have progressed. Device uninitialization calls `bng_re_debugfs_rem_pdev()`, and module exit removes the global root after unregistering the auxiliary driver.

## State And Persistence
State is in-memory debugfs dentries only. `bng_re_debugfs_root` persists for module lifetime, and `rdev->dbg_root` persists for a probed device lifetime. No files or counters are created under the directories in this implementation.

## Dependencies And Integration Points
Depends on Linux debugfs, PCI device naming, the `bng_re_dev` structure from `bng_re.h`, and module/device lifecycle in `bng_dev.c`. It includes BNGE and firmware/resource headers indirectly because it operates on the full `bng_re_dev`.

## Risks And Edge Cases
`debugfs_create_dir()` failures are not checked, which is common for optional debugfs but means `dbg_root` may be an error pointer or NULL depending on debugfs state. `bng_re_unregister_debugfs()` uses `debugfs_remove()` rather than recursive removal; because device removal should already remove children before module exit, this depends on clean unregister ordering.

## Test Signals
With debugfs mounted and the module loaded, `/sys/kernel/debug/bng_re` should exist. After a compatible device probes, a PCI-device-named child directory should appear and then disappear after device removal or module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_debugfs.c -->
