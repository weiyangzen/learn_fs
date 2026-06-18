# sources/distributed-fs/ceph-client/fs/nfs/nfs4sysctl.c

## Purpose
`nfs4sysctl.c` registers NFSv4 tunables under `fs/nfs`. It exposes the callback TCP port and idmapper cache timeout to sysctl userspace.

## Important APIs and Functions
- `nfs4_cb_sysctls[]`: table containing `nfs_callback_tcpport` and `idmap_cache_timeout`.
- `nfs4_register_sysctl()`: calls `register_sysctl("fs/nfs", nfs4_cb_sysctls)` and stores the returned table header.
- `nfs4_unregister_sysctl()`: unregisters the table and clears the global header pointer.

## Control Flow
Module initialization in `nfs4super.c` calls `nfs4_register_sysctl()` after DNS/idmap/xattr setup. If registration fails, initialization unwinds. Module exit calls `nfs4_unregister_sysctl()`. The callback port entry uses `proc_dointvec_minmax` with bounds 0..65535, while the idmap timeout uses `proc_dointvec`.

## State and Persistence
The file stores only `nfs4_callback_sysctl_table`, a pointer to the registered sysctl header. The exposed data lives elsewhere: `nfs_callback_set_tcpport` from callback support and `nfs_idmap_cache_timeout` from idmapping. Sysctl values are runtime kernel state, not persisted by this code.

## Dependencies and Integration Points
It depends on Linux sysctl infrastructure, NFS callback state, and NFS idmapper state. Its lifecycle is tied directly to NFSv4 module registration in `nfs4super.c`.

## Risks
The main risks are registration failure during module init, invalid callback port configuration, and unregister ordering. The table is static, so adding new entries requires ensuring referenced backing variables outlive the sysctl registration.

## Test Signals
Check that `/proc/sys/fs/nfs/nfs_callback_tcpport` accepts 0..65535 and rejects out-of-range values, `idmap_cache_timeout` updates the idmapper timeout, registration failure unwinds module init, and module unload removes both entries cleanly.
