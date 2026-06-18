# sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-handle.h

## Purpose
`posix-handle.h` declares the POSIX GFID handle API and defines macros for handle path construction, parent-GFID xattr key creation, parent-GFID link-count mutation, and entry handle resolution.

## Important APIs, Types, And Functions
- `HANDLE_ABSPATH_LEN()`, `MAKE_HANDLE_GFID_PATH`, `MAKE_HANDLE_RELPATH`, `MAKE_HANDLE_ABSPATH`, and `MAKE_HANDLE_ABSPATH_FD` construct GFID handle paths.
- `MAKE_PGFID_XATTR_KEY` and the `SET`/`REMOVE`/`LINK_MODIFY`/`UNLINK_MODIFY` pgfid macros manage big-endian 32-bit link-count xattrs.
- `MAKE_ENTRY_HANDLE()` resolves a `loc_t` to backend parent/entry paths and validates names.
- Declares handle, internal-write, disk-space, and writev-xdata helper functions.

## Control Flow
The macros perform substantial caller-side control flow. PGFID macros read/modify/write/remove xattrs and jump to caller labels on errors. `MAKE_ENTRY_HANDLE()` rejects null parent/name data and names containing `/`, handles absolute locs directly, otherwise calls `posix_istat()` and constructs handle paths unless `ELOOP` requires expansion.

## State And Persistence Behavior
PGFID macros mutate durable link-count xattrs using big-endian counters. Handle macros encode the persistent `.glusterfs/<gfid[0]>/<gfid[1]>/<uuid>` layout but do not themselves persist handles.

## Dependencies And Integration Points
Included by entry and handle implementations. Depends on `posix-inode-handle.h`, `posix.h`, UUID helpers, syscall wrappers, Gluster logging, and caller-local variables such as `op_ret` and `op_errno`.

## Risks And Edge Cases
The macros use `alloca` and caller-provided labels, so misuse is easy. Link-count updates require locks to avoid read-modify-write races. `UNLINK_MODIFY_PGFID_XATTR` must avoid underflow and missing-xattr surprises. `MAKE_ENTRY_HANDLE()` communicates through side effects and errno-sensitive control flow.

## Test Signals
Cover pgfid counter create/increment/decrement/remove, endian correctness, absent xattrs, path construction, absolute locs, rejection of slash-containing names, ELOOP paths, and concurrent link/unlink/rename operations under locks.
