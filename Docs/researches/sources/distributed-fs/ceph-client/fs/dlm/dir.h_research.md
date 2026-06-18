# sources/distributed-fs/ceph-client/fs/dlm/dir.h

## Purpose
`dir.h` declares the small public interface for DLM directory ownership and directory recovery. It separates directory mapping/name-copy routines from `lock.c`, `recover.c`, and RCOM handlers.

## Important APIs
- `dlm_dir_nodeid(struct dlm_rsb *rsb)` returns the directory node id stored in an RSB.
- `dlm_hash2nodeid(struct dlm_ls *ls, uint32_t hash)` maps a resource hash to a node id using the lockspace membership map.
- `dlm_recover_dir_nodeid(struct dlm_ls *ls, const struct list_head *root_list)` recomputes directory node ids for a list of root resources.
- `dlm_recover_directory(struct dlm_ls *ls, uint64_t seq)` rebuilds local directory records from peer master-name dumps during recovery.
- `dlm_copy_master_names(...)` fills an output buffer with length-prefixed names mastered locally for a requesting directory node.

## Control Flow and State
The header itself has no state. Its declarations expose the directory lifecycle: hash mapping during resource lookup, recomputation during recovery, and name dump serving for remote recovery requests. All persistent runtime state remains in `struct dlm_rsb` and `struct dlm_ls`.

## Dependencies and Integration Points
Consumers must already see `struct dlm_ls`, `struct dlm_rsb`, and Linux list types, normally through `dlm_internal.h`. `lock.c` uses the mapping helpers during `find_rsb()` and master lookup. Recovery code and RCOM handling use the directory rebuild/name-copy functions.

## Risks
- The API exposes raw buffers and lengths for `dlm_copy_master_names()`, so callers must pass valid RCOM payload storage and matching buffer lengths.
- Hash mapping depends on lockspace membership fields being initialized before use.

## Test Signals
- Compile coverage should ensure all users include `dlm_internal.h` before `dir.h`.
- Recovery tests should verify each declared function is exercised through directory-enabled lockspaces and skipped or altered appropriately when `LSFL_NODIR` is set.
