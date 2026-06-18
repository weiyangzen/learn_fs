# sources/distributed-fs/ceph-client/fs/nfs/internal.h

## Purpose
`internal.h` is the private integration header for the Linux NFS client implementation. It gathers cross-file declarations, mount/client context structures, inline state helpers, and small protocol-neutral utility routines used by NFSv2, NFSv3, NFSv4, pNFS, localio, direct I/O, page I/O, mount namespace handling, and superblock setup. It is the coordination point between version-specific modules and the common NFS client core.

## Important APIs, Types, And Functions
Key data types are `struct nfs_client_initdata`, which carries client construction inputs such as server address, protocol, timeout parameters, `nconnect`, network namespace, credentials, and transport security; `struct nfs_fs_context`, which stores parsed mount/reconfigure/submount state; `struct nfs_mount_request`, which is consumed by `mount_clnt.c`; `struct nfs_local_dio`, enabled for `CONFIG_NFS_LOCALIO`; and `struct nfs_direct_req`, which tracks direct I/O lifetime, completion, commit state, byte counts, errors, and flags.

The header declares the major common entry points: client/server allocation and lookup, RPC client setup, superblock creation and teardown, root/submount functions, read/write page-IO setup, commit handling, direct I/O helpers, mount namespace helpers, NFSv4 client discovery and trunking hooks, and localio hooks. Inline helpers include `nfs_attr_check_mountpoint()`, `nfs_lookup_is_soft_revalidate()`, `flags_to_mode()`, `nfs_file_block_o_direct()`, `nfs_io_gfp_mask()`, `nfs_should_remove_suid()`, `nfs_igrab_and_active()`, `nfs_block_size()`, `nfs_io_size()`, `nfs_super_set_maxbytes()`, `nfs_folio_length()`, `nfs_stateid_hash()`, and fatal-error classifiers.

## Control Flow And Integration Points
Most files in this work item include `internal.h` to bind into common client behavior. Version modules register through `struct nfs_subversion` from `nfs.h`, then use declarations here to allocate servers, clone submounts, decode directories, and dispatch `nfs_rpc_ops`. `io.c` implements the `nfs_start_io_*` functions declared here. `namespace.c` consumes the path and submount helpers. `mount_clnt.c` consumes `struct nfs_mount_request`. `localio.c` exports local open/read/write/commit helpers through the conditional declarations here. `nfs3proc.c` fills `nfs_v3_clientops` with common function pointers declared here.

## State And Persistence Behavior
The header does not persist state itself, but it defines the shapes and invariants of long-lived client state. `nfs_fs_context` persists mount configuration while a filesystem context is built. `nfs_client_initdata` seeds `struct nfs_client` instances stored in per-net lists. `nfs_direct_req` tracks async direct I/O until all requests and commits complete. Inline helpers mutate inode flags, cache-validity bits, page writeback accounting, and pNFS commit verifier state. `nfs_igrab_and_active()` and `nfs_iput_and_deactive()` couple inode references to superblock activity.

## Dependencies
This header depends on Linux VFS, fs_context, SunRPC, NFS page and XDR types, pNFS commit structures, security labels, user credentials, RCU/list locking, and optional build flags including `CONFIG_PROC_FS`, `CONFIG_NFS_V4`, `CONFIG_NFS_V4_2`, `CONFIG_NFS_V4_SECURITY_LABEL`, `CONFIG_NFS_LOCALIO`, `CONFIG_NFS_FSCACHE`, and `CONFIG_MIGRATION`.

## Risks And Edge Cases
Because this file centralizes declarations, signature drift is high risk across many compilation units. The direct I/O and buffered I/O helpers require correct `i_rwsem` ownership; callers that skip the start/end pairing can deadlock or corrupt cache semantics. Error classification affects retry and failover behavior. Size helpers clamp I/O sizes and superblock limits, so regressions can cap throughput or expose invalid offsets. Localio stubs must preserve behavior when the feature is disabled.

## Test Signals
Useful signals include build coverage across NFSv2, NFSv3 ACL, NFSv4, pNFS, migration, fscache, and localio configurations; xfstests over buffered/direct I/O transitions; mount option parsing and submount tests; pNFS commit verification; and lockdep/KCSAN checks around inode and superblock reference helpers.
