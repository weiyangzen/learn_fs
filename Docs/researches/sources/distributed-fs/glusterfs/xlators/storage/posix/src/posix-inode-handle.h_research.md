# sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-inode-handle.h

## Purpose

This header declares POSIX inode-handle path construction and ancestry APIs used by the storage translator to resolve Gluster GFIDs to backend paths. It also defines macros that convert a Gluster `loc_t` into either an export-root-relative real path or a handle path under the brick's internal GFID handle hierarchy.

## Important APIs, Types, and Functions

Key constants are `TRASH_DIR`, `UUID0_STR`, `POSIX_ANCESTRY_PATH`, and `POSIX_ANCESTRY_DENTRY`. `LOC_HAS_ABSPATH` and `LOC_IS_DIR` classify locs. `MAKE_REAL_PATH` prefixes `POSIX_BASE_PATH(this)` unless the constructed path would exceed `POSIX_PATH_MAX(this)`, in which case it falls back to an alloca buffer containing the path without a leading slash. `MAKE_HANDLE_PATH` calls `posix_handle_path`. `MAKE_INODE_HANDLE` is the main macro used by fops: it validates translator private state and GFID, prefers the real absolute path for directory locs with absolute paths, otherwise calls `posix_istat` and builds a GFID handle path unless the inode resolution returned `ELOOP`.

Declared functions are `posix_handle_path`, `posix_make_ancestryfromgfid`, `posix_handle_init`, and `posix_handle_trash_init`.

## Control Flow

The header's macros inline control flow into call sites. Most fops declare `op_ret`, call `MAKE_INODE_HANDLE`, then check whether it set `op_ret` to `-1`. This means callers must use the expected local variable names and must treat `errno` from the macro as authoritative. Ancestry reconstruction walks from a GFID handle to parents and optionally fills a path or `gf_dirent_t` list.

## State and Persistence Behavior

The header itself persists nothing, but its APIs define how persistent handle directories and trash/landfill layout are initialized and addressed. The path macros allocate temporary stack buffers with `alloca`; call sites must not retain those pointers beyond the current stack frame.

## Dependencies and Integration Points

It depends on `limits.h`, `sys/types.h`, `gf-dirent.h`, `posix_handle_path`, `posix_istat`, `posix_pstat`, translator private path macros, GFID helpers, and message ID `P_MSG_INODE_HANDLE_CREATE`. It is consumed throughout lookup, inode, fd, xattr, metadata, and ancestry code.

## Risks

The macro style is fragile because it mutates caller variables such as `op_ret` and `errno`, assumes local names, and uses stack allocation sized from paths. Path-length fallback behavior deserves review because it strips a leading slash instead of failing, relying on later handle or syscall behavior. Null GFIDs, missing private state during fini, stale handles, and symlink `ELOOP` handling are the main failure cases.

## Test Signals

Exercise absolute directory locs, non-directory GFID handle resolution, null GFID rejection, path-length boundary behavior, stale GFID handles, symlink loop handling, handle initialization, trash initialization, and ancestry path/dentry reconstruction.
