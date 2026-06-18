# sources/distributed-fs/ceph-client/drivers/misc/mei/debugfs.c

## Purpose
`debugfs.c` exposes diagnostic MEI state under debugfs: firmware clients, active host clients, device/HBM/power-gating/PXP state, and a writable fixed-address override.

## Important APIs, Types, and Functions
Show functions are `mei_dbgfs_meclients_show()`, `mei_dbgfs_active_show()`, and `mei_dbgfs_devstate_show()`. Lifecycle functions are `mei_dbgfs_register()` and `mei_dbgfs_deregister()`. `mei_dbgfs_write_allow_fa()` wraps bool writes and marks `override_fixed_address`.

## Control Flow
Registration creates a debugfs directory and files `meclients`, `active`, `devstate`, and `allow_fixed_address`. Show callbacks lock either `me_clients_rwsem` or `device_lock`, validate enabled state before dumping volatile lists, and print compact tabular state. Deregistration removes the tree recursively.

## State and Persistence
Debugfs files reflect runtime `mei_device` fields and do not persist. Writing `allow_fixed_address` changes `dev->allow_fixed_address` and sets `override_fixed_address` until device teardown/reset.

## Dependencies and Integration Points
Depends on debugfs, seq_file, MEI device/client structures, HBM state string helpers, power-gating helpers, and client reference helpers.

## Risks
Debugfs is diagnostic and not a stable ABI. Dumps can be inconsistent if state changes outside the protected enabled window. The fixed-address override is a privileged test/debug control.

## Test Signals
Signals include correct file creation/removal, readable tables with active firmware clients, active host-client queue state, devstate feature flags, PXP mode strings, and writable `allow_fixed_address` behavior.
