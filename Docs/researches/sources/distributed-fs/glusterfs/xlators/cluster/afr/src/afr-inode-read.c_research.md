# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-inode-read.c

## Purpose
Implements AFR inode read-side FOPs and special xattr queries. Normal reads select one readable child and retry through `afr_read_txn()`, while management xattrs may query all children, aggregate results, or trigger heal/split-brain workflows.

## Important APIs, types, and functions
Public FOPs include `afr_access()`, `afr_stat()`, `afr_fstat()`, `afr_readlink()`, `afr_readv()`, `afr_seek()`, `afr_getxattr()`, and `afr_fgetxattr()`. `afr_handle_quota_size()` chooses maximum quota metadata across readable children. `afr_filter_xattrs()` removes internal AFR xattrs from user-visible responses. `afr_is_special_xattr()` maps pathinfo, clear-lock, lockinfo, stime, quota-size, and node-UUID requests to all-subvolume callbacks. `afr_handle_heal_xattrs()` dispatches heal-info, split-brain heal, and split-brain status commands.

## Control flow
Simple reads initialize local state, copy loc/fd/xdata, optionally call `afr_fix_open()`, and invoke `afr_read_txn()` with data or metadata transaction type. Per-child callbacks either unwind on success or store errno and call `afr_read_txn_continue()` on failure. `getxattr` first rejects internal AFR keys, handles marker/heal/special keys, node UUID fallback, and only then uses the normal read transaction path.

## State and persistence behavior
Most state is frame-local reply aggregation. Some commands can trigger persistent side effects indirectly: heal xattrs launch self-heal/split-brain synctasks, clear-lock xattrs affect locks in lower layers, and quota-size aggregation rewrites the response dict to the maximum observed value. Internal AFR xattrs are intentionally filtered before unwind.

## Dependencies and integration points
Depends on AFR read transactions, self-heal and split-brain helpers, marker xattr helpers, quota utilities, libxlator stime aggregation, atomic counters, dict serialization, child `getxattr`/`fgetxattr` FOPs, and fd reopen repair.

## Risks and test signals
Risks include leaking internal xattrs, retrying on errors that should be final, wrong aggregation buffer sizing, lockinfo TODO behavior that can ignore per-reply processing failures, special xattr handling diverging between path and fd variants, and heal command authorization assumptions. Tests should cover normal read failover, split-brain read failure, all special xattr aggregations, internal xattr filtering, quota max selection, node UUID fallback, and fd reopen before fd-based reads.
