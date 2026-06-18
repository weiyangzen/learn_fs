# sources/distributed-fs/ceph-client/drivers/vfio/debugfs.c

## Purpose

`debugfs.c` provides optional VFIO debugfs support, mainly for devices with migration support. It creates a top-level `debugfs/vfio` directory and per-device subdirectories containing migration state and feature files.

## Important APIs, Types, and Functions

`vfio_debugfs_create_root()` and `vfio_debugfs_remove_root()` manage the global root. `vfio_device_debugfs_init()` creates a directory named after the VFIO device's underlying device and, when `vdev->mig_ops` exists, creates a `migration` directory with `state` and `features` seqfiles. `vfio_device_debugfs_exit()` removes the per-device tree. Readers are `vfio_device_state_read()` and `vfio_device_features_read()`.

## Control Flow

The state reader calls `migration_get_state()` and prints one of the known `VFIO_DEVICE_STATE_*` names. The feature reader prints supported migration feature strings based on `migration_flags` and dirty-tracking presence. Debugfs creation is typically called by VFIO core after a device is registered; vendor drivers can add children under the per-device migration directory.

## State and Persistence Behavior

Only debugfs dentries are stored, with each device keeping `vdev->debug_root`. The files reflect live driver state and have no persistence beyond debugfs.

## Dependencies and Integration Points

It depends on `CONFIG_VFIO_DEBUGFS`, debugfs, seq_file, VFIO migration ops, and device-managed seqfile helpers. HiSilicon ACC uses the created `migration` directory for vendor-specific debug files.

## Risks and Edge Cases

State reading assumes `vdev->mig_ops` remains valid while the debugfs file is open. The build-time `BUILD_BUG_ON` catches enum range drift for known migration state names. Debugfs is diagnostic only; user-visible ABI must not rely on it.

## Test Signals

Enable `CONFIG_VFIO_DEBUGFS`, register devices with and without migration ops, read state/features in every migration state, verify dirty-tracking string emission when `log_ops` exists, and confirm recursive removal on unregister.
