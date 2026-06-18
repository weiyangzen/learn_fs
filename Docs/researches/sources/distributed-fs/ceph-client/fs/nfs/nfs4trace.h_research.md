# sources/distributed-fs/ceph-client/fs/nfs/nfs4trace.h

## Purpose
`nfs4trace.h` defines the NFSv4 tracepoint surface. It provides typed trace events for clientid/session operations, callback sequence handling, state manager transitions, XDR errors, open/close/lock state, delegation and stateid validation, namespace operations, idmapping, read/write/commit I/O, pNFS layout/device/data-server activity, flexfiles errors, block layout reservation keys, NFSv4.2 sparse/copy/offload operations, and xattrs.

## Important APIs and Event Families
- Client/session: `nfs4_setclientid`, `nfs4_exchange_id`, `nfs4_create_session`, `nfs4_destroy_session`, `nfs4_bind_conn_to_session`, `nfs4_sequence`, `nfs4_setup_sequence`, `nfs4_sequence_done`, `nfs4_trunked_exchange_id`.
- Callback: `nfs4_cb_sequence`, `nfs4_cb_seqid_err`, `nfs4_cb_offload`, `nfs_cb_no_clp`, `nfs_cb_badprinc`, callback inode/stateid events.
- State manager: `nfs4_state_mgr`, `nfs4_state_mgr_failed`, with `TRACE_DEFINE_ENUM` and `show_nfs4_clp_state()` for `NFS4CLNT_*` bits.
- Open/lock/delegation: `nfs4_open_*`, `nfs4_cached_open`, `nfs4_close`, `nfs4_get_lock`, `nfs4_set_lock`, `nfs4_unlock`, `nfs4_state_lock_reclaim`, delegation set/reclaim/detach/return/test events.
- Filesystem operations: lookup, rename, access, readlink, readdir, ACL/security-label, getattr/fsinfo/root lookup, setattr, delegreturn, layout stateid updates.
- I/O and pNFS: `nfs4_read`, `nfs4_write`, `nfs4_commit`, pNFS read/write/commit DS, layoutget/layoutcommit/layoutreturn/layoutstats, `pnfs_update_layout`, MDS fallback, deviceid, `pnfs_ds_connect`, flexfiles and file-layout events.
- NFSv4.2: llseek, fallocate/deallocate, copy, clone, copy_notify, offload cancel/status, get/set/remove/list xattr.

## Control Flow
The header uses the standard Linux tracepoint pattern: include guards allow multi-read, event classes define common payload schemas, `DEFINE_EVENT` instantiates related events, and the final `#include <trace/define_trace.h>` emits code when included from `nfs4trace.c` with `CREATE_TRACE_POINTS`. Most event classes hash file handles, stateids, session IDs, and device IDs so traces are useful without dumping opaque binary structures.

## State and Persistence
The header itself stores no runtime state. It defines how runtime state is sampled into trace buffers. Trace payloads commonly include error numbers normalized for `show_nfs4_status()`, device/file IDs, file handle hashes, stateid sequence/hash pairs, layout stateid hashes, open flags, fmode, lock ranges, client hostnames, session slot IDs, and pNFS device IDs.

## Dependencies and Integration Points
It depends on Linux tracepoint infrastructure, SUNRPC trace helpers, NFS trace helpers, delegation structures, pNFS structures, NFSv4.2 structures under `CONFIG_NFS_V4_2`, and helper printers such as `show_nfs4_status()`, `show_fs_fmode_flags()`, and `show_pnfs_layout_iomode()`. It is used throughout NFSv4 proc/XDR/state/session/delegation/layout code and instantiated by `nfs4trace.c`.

## Risks
Tracepoints dereference many protocol and VFS structures in `TP_fast_assign`; callers must pass valid objects matching each event's expectations. Because some events include strings from dentries, hostnames, or data-server remote strings, lifetime assumptions matter. Trace schema changes affect userspace tooling that parses tracefs output. Conditional NFSv4.2 sections must remain guarded so non-v4.2 builds do not reference unavailable types.

## Test Signals
Build coverage across NFSv4.0, v4.1 sessions, pNFS, security labels, and NFSv4.2 configurations is essential. Runtime signals include enabling representative tracepoints through tracefs, checking payload fields for stateid/session/file-handle hashes, inducing state-manager failures, callback faults, pNFS fallback, flexfiles errors, block PR key events, sparse/copy/offload operations, and xattr operations.
