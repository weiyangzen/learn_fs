# sources/distributed-fs/glusterfs/xlators/features/trash/src/trash.c

## Purpose
Implements the `trash` translator, a server-side feature that preserves deleted or truncated file contents by moving or copying them into a configured trash directory. It intercepts `unlink`, `truncate`, and `ftruncate`, protects the trash directory from user operations, and manages trash directory creation/rename during graph events and reconfiguration.

## Important APIs, Types, and Functions
- Path helpers: `get_permission()`, `extract_trash_directory()`, `copy_trash_path()`, `remove_trash_path()`, `append_time_stamp()`, `check_whether_eliminate_path()`, and `check_pathbuf()`.
- State cleanup: `trash_local_wipe()` and `wipe_eliminate_path()`.
- Directory lifecycle: `create_or_rename_trash_directory()`, `rename_trash_directory()`, `create_internalop_directory()`, and associated lookup/mkdir/rename callbacks.
- Unlink flow: `trash_unlink()`, `trash_unlink_stat_cbk()`, `trash_unlink_rename_cbk()`, and `trash_unlink_mkdir_cbk()`.
- Truncate flow: `trash_truncate()`, `trash_ftruncate()`, `trash_truncate_stat_cbk()`, `trash_truncate_create_cbk()`, `trash_truncate_mkdir_cbk()`, `trash_truncate_open_cbk()`, `trash_truncate_readv_cbk()`, `trash_truncate_writev_cbk()`, and `trash_truncate_unlink_cbk()`.
- Guarded user operations: `trash_mkdir()`, `trash_rename()`, and `trash_rmdir()` reject direct operations on fixed trash/internal directories.
- Lifecycle/config: `init()`, `reconfigure()`, `notify()`, `fini()`, `mem_acct_init()`, `fops`, `options`, and `xlator_api`.

## Control Flow
On `init()`, the translator validates it has one child, reads `trash`, `trash-dir`, `trash-eliminate-path`, `trash-max-filesize`, `trash-internal-op`, and `brick-path`, creates a local memory pool, and when enabled creates an inode table for the fixed trash inode.

On `GF_EVENT_CHILD_UP`, `notify()` creates or renames the trash directory using nameless lookup by fixed GFID, then optionally creates the `internal_op` directory. `reconfigure()` updates options, does not allow disabling an already active trash graph, can allocate the trash inode table when turning on, and triggers directory creation/rename.

`trash_unlink()` bypasses when disabled, when an internal pid should not be trashed, when the path is under trash/eliminate paths, when the inode/gfid is invalid, when file size exceeds the limit, or when link count is greater than one. Otherwise it builds `newpath` under the trash directory, appends a timestamp, stats the source, and renames it. Missing trash subdirectories are created recursively before retrying rename. The CTR link-count xdata handshake is preserved when requested.

`trash_truncate()` and `trash_ftruncate()` similarly bypass disabled/internal/excluded cases. For truncation that shrinks a last-link file below the size limit, the code creates a new file in the trash path, opens the source, copies source content in `GF_BLOCK_READV_SIZE` chunks with readv/writev, then performs the original truncate. If any copy step fails, it deletes the partial trash copy and lets the truncate proceed.

`trash_mkdir()`, `trash_rename()`, and `trash_rmdir()` call `check_whether_op_permitted()` to prevent client manipulation of the fixed trash and internal-op directories.

## State and Persistence
`trash_private_t` persists translator configuration: old/new trash directory paths, brick path, eliminate list, maximum trashable size, enable/internal flags, trash inode, and trash inode table. `trash_local_t` tracks each in-flight operation with old/new locs, fds, offsets, original/new paths, parent iatts, PID restoration state, and CTR link-count request state. Persistent filesystem state includes the trash directory with fixed GFID, optional `internal_op` directory, and timestamped preserved files.

## Dependencies and Integration Points
Depends on GlusterFS stack APIs, inode/dentry internals, dict/xdata, syscalls, memory pools, fixed GFIDs, and child translator fops. Integrates with posix/brick storage through `brick-path`, with CTR via `GF_REQUEST_LINK_COUNT_XDATA`/`GF_RESPONSE_LINK_COUNT_XDATA`, and with server internal operations by temporarily setting `frame->root->pid` to `GF_SERVER_PID_TRASH`.

## Risks
- Complex async callback chains have many ownership edges; loc/fd/path leaks or double ownership are plausible if paths change.
- `frame->root->pid` must always be restored by `TRASH_UNSET_PID()`; callback error paths are sensitive.
- Path construction uses fixed `PATH_MAX` buffers and repeated `strncat`; truncation or boundary mistakes can silently bypass trashing.
- Trash disable during reconfigure is intentionally refused because inode-table teardown is unsafe.
- Internal `#include "inode.c"` in the header is unusual and tightly couples to Gluster internals.
- Copy-on-truncate preserves data best-effort; failures intentionally allow the user truncate to proceed without backup.

## Test Signals
Tests should cover enabling/disabling behavior, trash-dir rename on reconfigure, fixed GFID creation, unlink of single-link versus multi-link files, max-size bypass, eliminate paths, internal operation handling, CTR xdata response, recursive trash subdirectory creation, truncate/ftruncate shrink versus extend, copy failures, and protection of trash directories from mkdir/rename/rmdir. Memory and statedump tests should exercise private and local pool accounting.
