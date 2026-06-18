# subset-b-007100 Research

Grouped research report for the requested GlusterFS thin-arbiter, trash, upcall, utime, libxlator, and meta source files. Each section preserves the source path and is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/thin-arbiter/src/thin-arbiter-messages.h -->
# sources/distributed-fs/glusterfs/xlators/features/thin-arbiter/src/thin-arbiter-messages.h

## Purpose
Defines the thin-arbiter translator message-id namespace. It includes `glfs-message-id.h` and registers the `TA` component with `TA_MSG_INVALID_FOP`, preserving GlusterFS message-id stability rules.

## Important APIs, Types, and Functions
- `GLFS_MSGID(TA, TA_MSG_INVALID_FOP)` exports the only message identifier used by this feature area.
- Include guard `_TA_MESSAGES_H_` prevents duplicate registration.

## Control Flow
There is no runtime control flow. The macro expands during compilation into message-id constants consumed by logging and diagnostics.

## State and Persistence
No mutable state. Stability of the ordered message list is persistent API behavior because IDs must not be removed or reused.

## Dependencies and Integration Points
Depends on GlusterFS global message-id machinery. Integrated by `thin-arbiter.c` through inclusion of this header, though the current file mostly uses generic failure callbacks rather than detailed `gf_msg` calls.

## Risks
Changing order or removing identifiers can break log correlation. Adding messages must append only.

## Test Signals
Compile coverage is the primary signal. Message-id regressions surface through build failures or logging tests that validate component IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/thin-arbiter/src/thin-arbiter-messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/thin-arbiter/src/thin-arbiter.c -->
# sources/distributed-fs/glusterfs/xlators/features/thin-arbiter/src/thin-arbiter.c

## Purpose
Implements the `thin-arbiter` GlusterFS feature translator. Its behavior is intentionally narrow: it only permits `xattrop` and `fxattrop`, validates thin-arbiter source/pending xattr consistency against the child brick, and fails nearly all other filesystem operations with `EINVAL`.

## Important APIs, Types, and Functions
- `ta_prepare_fop()` allocates `ta_fop_t`, copies `loc` or refs `fd`, refs the incoming dict, builds `brick_xattr`, and stores it on `frame->local`.
- `ta_set_incoming_values()` creates zero-filled xattr buffers in `brick_xattr` matching incoming xattr lengths so the child `xattrop` can fetch current brick values.
- `ta_get_incoming_and_brick_values()` compares incoming values and brick values against zero-filled source buffers, setting `fop->on_disk[]`.
- `ta_verify_on_disk_source()` iterates returned brick xattrs and rejects cases where both tracked sources look on disk/nonzero.
- `ta_xattrop()` and `ta_fxattrop()` are the only passed-through operations. They first wind a child xattrop/fxattrop with `brick_xattr`, then on success wind the original xattrop/fxattrop.
- `TA_FAILED_FOP` and numerous `ta_*` fop stubs map unsupported operations to default failure callbacks with `EINVAL`.
- `mem_acct_init()`, `init()`, `reconfigure()`, `fini()`, `fops`, `cbks`, `options`, and `xlator_api` provide translator lifecycle and registration.

## Control Flow
`ta_xattrop()`/`ta_fxattrop()` allocate local state and issue a read-like child xattrop/fxattrop using `fop->brick_xattr`. `ta_get_xattrop_cbk()` receives the child dict, validates on-disk source state, and if valid winds the original xattrop/fxattrop to the child. `ta_set_xattrop_cbk()` finally unwinds the original caller and releases `ta_fop_t`.

All other registered fops immediately invoke `default_<fop>_failure_cbk()`. `init()` requires exactly one child and warns on dangling volume parents.

## State and Persistence
Per-call state lives in `ta_fop_t` on `frame->local`; it owns refs to `fd`, `loc`, incoming dict, and generated `brick_xattr`. Persistent data is the child brick's xattr state, especially thin-arbiter source/pending values. The translator has no private persistent configuration.

## Dependencies and Integration Points
Uses GlusterFS stack winding/unwinding, dict APIs, fd/loc refcounting, and xlator registration. It depends on `thin-arbiter.h` for state/macros and `thin-arbiter-mem-types.h` for allocation classes. It sits above one child translator and is integrated in AFR/thin-arbiter workflows via xattrop/fxattrop.

## Risks
- `ta_get_incoming_and_brick_values()` assumes at most two entries because `on_disk` has length two; unexpected dict sizes can exceed intended indexing.
- Failure-path errno conversion uses negative returns in several places and must remain consistent.
- Unsupported fops fail hard; placing this xlator in the wrong graph position will break normal file access.
- Correctness depends on exact xattr value lengths and zero-fill semantics.

## Test Signals
Useful tests should exercise accepted xattrop/fxattrop cases, both-source rejection, allocation failures, dict length mismatches, and unsupported fop failures. Integration tests should place thin-arbiter in a replica/thin-arbiter graph and validate that only source-state transitions pass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/thin-arbiter/src/thin-arbiter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/thin-arbiter/src/thin-arbiter.h -->
# sources/distributed-fs/glusterfs/xlators/features/thin-arbiter/src/thin-arbiter.h

## Purpose
Declares thin-arbiter constants, stack helper macros, and the per-fop state used by `thin-arbiter.c`.

## Important APIs, Types, and Functions
- `THIN_ARBITER_SOURCE_XATTR` names `trusted.ta.source`; `THIN_ARBITER_SOURCE_SIZE` is `2`.
- `TA_FAILED_FOP()` centralizes unsupported-fop failure callbacks.
- `TA_STACK_UNWIND()` releases `ta_fop_t` from `frame->local` before strict unwind.
- `struct _ta_fop` stores xattrop flags, `loc`, `fd`, incoming dict, generated brick-xattr dict, two on-disk indicators, and an index.

## Control Flow
The header is passive, but `TA_STACK_UNWIND()` shapes callback control flow by guaranteeing local cleanup before returning to the caller.

## State and Persistence
Defines only per-call state. No global state. The `loc`, `fd`, and dict members are refcounted or wiped by `ta_release_fop()`.

## Dependencies and Integration Points
Includes GlusterFS locking, xlator, and list headers. Its macros depend on GlusterFS default callback names and `STACK_UNWIND_STRICT`.

## Risks
The fixed `on_disk[2]` model mirrors thin-arbiter's two-source assumption; future replication layouts or dict sizes need bounds-aware changes. Macro side effects require valid `frame` and `frame->local` conventions.

## Test Signals
Compile-time inclusion plus runtime xattrop/fxattrop tests confirm macro cleanup, refcounts, and state copying.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/thin-arbiter/src/thin-arbiter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/trash/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/trash/Makefile.am

## Purpose
Top-level Automake file for the trash feature translator directory. It delegates all build work to `src`.

## Important APIs, Types, and Functions
- `SUBDIRS = src` makes Automake recurse into the implementation directory.
- `CLEANFILES =` is present but empty.

## Control Flow
Build-system only: configure/make recurses into `src/Makefile.am`.

## State and Persistence
No runtime state. Build output state is controlled by the child makefile.

## Dependencies and Integration Points
Integrated by the broader GlusterFS build tree. It depends on Automake recursion and the `src` directory existing.

## Risks
If recursion is removed, `trash.la` will not be built. Empty `CLEANFILES` is harmless but redundant.

## Test Signals
`make` or `make distcheck` should include `xlators/features/trash/src`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/trash/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/trash/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/trash/src/Makefile.am

## Purpose
Builds the server-side `trash.la` feature translator module.

## Important APIs, Types, and Functions
- `if WITH_SERVER` gates `xlator_LTLIBRARIES = trash.la`.
- Installs under `$(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/features`.
- `trash_la_SOURCES = trash.c`.
- `trash_la_LIBADD` links `libglusterfs.la`.
- `noinst_HEADERS = trash.h trash-mem-types.h`.
- `AM_CPPFLAGS` wires libglusterfs and RPC XDR include paths.

## Control Flow
Automake builds a module with `-module $(GF_XLATOR_DEFAULT_LDFLAGS)` when server support is enabled.

## State and Persistence
No runtime state. It controls build artifacts and installation paths.

## Dependencies and Integration Points
Depends on libglusterfs and GlusterFS build variables. The server gate matches trash's brick-side behavior.

## Risks
Missing RPC/libglusterfs include paths or `WITH_SERVER` misconfiguration prevents module build. `trash.c` includes broad Gluster internals, so header dependency churn can break compilation.

## Test Signals
Build `trash.la`; verify module installation under `xlator/features`; run packaging checks for `noinst_HEADERS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/trash/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/trash/src/trash-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/features/trash/src/trash-mem-types.h

## Purpose
Defines trash translator memory-accounting categories.

## Important APIs, Types, and Functions
- `enum gf_trash_mem_types_` starts at `gf_common_mt_end + 1`.
- Categories include `gf_trash_mt_trash_private_t`, `gf_trash_mt_char`, `gf_trash_mt_uuid`, `gf_trash_mt_trash_elim_path`, and `gf_trash_mt_end`.

## Control Flow
No runtime control flow. Values are consumed by allocation calls and `xlator_mem_acct_init()`.

## State and Persistence
No state. Allocation categories become part of runtime memory accounting output.

## Dependencies and Integration Points
Includes `glusterfs/mem-types.h`. Used by `trash.c` for private state, path strings, UUID storage, and eliminate-path nodes.

## Risks
Changing enum order can confuse memory accounting. New allocation classes should be appended before `gf_trash_mt_end`.

## Test Signals
Compile-time usage and memory-accounting/statedump output should show trash categories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/trash/src/trash-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/trash/src/trash.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/trash/src/trash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/trash/src/trash.h -->
# sources/distributed-fs/glusterfs/xlators/features/trash/src/trash.h

## Purpose
Declares trash translator data structures, constants, and helper macros used by `trash.c`.

## Important APIs, Types, and Functions
- `GF_BLOCK_READV_SIZE` defaults truncate-copy chunks to 128 KiB.
- `GF_DEFAULT_MAX_FILE_SIZE` defaults to 200 MiB if no configured maximum is present in `init()`.
- `trash_local_t` stores per-fop fd/loc/path/offset/PID/link-count state.
- `trash_elim_path` is a singly-linked list of path prefixes excluded from trashing.
- `trash_private_t` stores configured trash paths, brick path, eliminate list, size limit, enable/internal flags, and trash inode table.
- `TRASH_SET_PID()` and `TRASH_UNSET_PID()` temporarily mark internal trash-created fops with `GF_SERVER_PID_TRASH`.
- `TRASH_STACK_UNWIND()` unwinds and then wipes `trash_local_t`.

## Control Flow
Macros directly affect fop callback flow by switching PID identity around internal mkdir/create operations and ensuring local cleanup on unwind.

## State and Persistence
Defines in-memory private and per-call state. The private struct points at persistent filesystem concepts, including the trash inode and configured trash directory.

## Dependencies and Integration Points
Includes GlusterFS core headers, defaults, `inode.c`, `fnmatch.h`, and `libgen.h`. The inclusion of inode implementation exposes internal dentry helpers used by truncate.

## Risks
Macros assume valid `frame`, `frame->root`, and local state. `PATH_MAX` arrays are embedded in `trash_local_t`, so long paths require careful handling. Including `inode.c` can create brittle build/link coupling.

## Test Signals
Compile tests catch signature drift. Runtime trash unlink/truncate tests validate local cleanup, PID restoration, and path buffer behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/trash/src/trash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/upcall/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/upcall/Makefile.am

## Purpose
Top-level Automake file for the upcall feature translator directory.

## Important APIs, Types, and Functions
- `SUBDIRS = src` recurses into implementation.
- `CLEANFILES =` is empty.

## Control Flow
Build-system recursion only.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Integrated by parent GlusterFS Automake tree.

## Risks
Removing `src` recursion would omit the upcall translator.

## Test Signals
`make` should descend into `xlators/features/upcall/src`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/upcall/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/upcall/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/upcall/src/Makefile.am

## Purpose
Builds the server-side `upcall.la` translator.

## Important APIs, Types, and Functions
- `if WITH_SERVER` gates module build.
- `upcall_la_SOURCES = upcall.c upcall-internal.c`.
- Links libglusterfs, gfrpc, and gfxdr.
- Installs under `xlator/features`.
- Headers include `upcall.h`, memory/message headers, and cache-invalidation constants.
- Uses `-fno-strict-aliasing`.

## Control Flow
Automake compiles upcall implementation and internal cache-invalidation support into one module.

## State and Persistence
No runtime state. Build artifacts are module and object files.

## Dependencies and Integration Points
Depends on server builds, libglusterfs, RPC libraries, and generated XDR headers because upcall notifications cross RPC/server boundaries.

## Risks
Missing RPC/XDR links break notification support. `-fno-strict-aliasing` suggests pointer-cast-sensitive code in the translator.

## Test Signals
Build `upcall.la`, package headers, and run server-side cache-invalidation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/upcall/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/upcall/src/upcall-cache-invalidation.h -->
# sources/distributed-fs/glusterfs/xlators/features/upcall/src/upcall-cache-invalidation.h

## Purpose
Defines the default cache invalidation timeout option for upcall.

## Important APIs, Types, and Functions
- `CACHE_INVALIDATION_TIMEOUT "60"` is used as the default value for the `cache-invalidation-timeout` volume option.

## Control Flow
No runtime control flow.

## State and Persistence
No state. The default value influences runtime private configuration at `init()`.

## Dependencies and Integration Points
Included by `upcall.c` when registering volume options.

## Risks
Changing the string alters default cache retention and notification behavior for deployments that do not set the option.

## Test Signals
Option parsing tests should confirm default timeout is 60 seconds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/upcall/src/upcall-cache-invalidation.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/upcall/src/upcall-internal.c -->
# sources/distributed-fs/glusterfs/xlators/features/upcall/src/upcall-internal.c

## Purpose
Implements upcall cache-invalidation state management: per-inode client registries, xattr filtering, notification dispatch, and a reaper thread for expired client entries and destroyed inode contexts.

## Important APIs, Types, and Functions
- `is_upcall_enabled()` and `get_cache_invalidation_timeout()` read private options.
- `__upcall_inode_ctx_set()`, `__upcall_inode_ctx_get()`, and `upcall_inode_ctx_get()` attach `upcall_inode_ctx_t` to inodes and maintain a global list.
- `__add_upcall_client()` creates client entries with UID, access time, and expiry attribute.
- `upcall_cleanup_expired_clients()`, `__upcall_cleanup_inode_ctx_client_list()`, and `upcall_cleanup_inode_ctx()` clean client/inode state and send forget invalidations.
- `upcall_reaper_thread()` and `upcall_reaper_thread_init()` maintain background cleanup.
- `up_filter_xattr()`, `up_filter_unregd_xattr()`, `up_filter_afr_xattr()`, `up_compare_afr_xattr()`, and `up_invalidate_needed()` decide which xattr changes trigger notifications.
- `upcall_cache_invalidate()` is the central access/update/invalidation entry point.
- `upcall_client_cache_invalidate()` builds `gf_upcall`/`gf_upcall_cache_invalidation` payloads and calls `this->notify()`.
- `upcall_cache_forget()` sends `UP_FORGET` notifications during inode context cleanup.

## Control Flow
Most wrapped fop callbacks call `upcall_cache_invalidate()`. That function resolves a valid inode context, handles nameless lookup cases by finding a linked inode from returned stat, updates or adds the current client entry, and notifies other recently active clients unless the operation is only atime. Notifications are synchronous on the fop path through `this->notify(GF_EVENT_UPCALL, ...)`.

The reaper thread loops until `priv->fini`, scans `priv->inode_ctx_list`, removes expired clients, frees contexts marked `destroy`, sleeps for half the current timeout, then repeats. Inode forget calls `upcall_cleanup_inode_ctx()`, which deletes the inode ctx, sends forget notifications, cleans client entries, and marks the ctx for reaper destruction.

## State and Persistence
Runtime state is in `upcall_private_t`: timeout, global inode context list, lock, reaper thread id, registered xattr patterns, fini flag, enable flag, and init flag. Each inode context stores a GFID, a client list, its own mutex, and a destroy marker. Each client entry stores `client_uid`, last access time, and expire time. This is in-memory only and rebuilt as clients access files.

## Dependencies and Integration Points
Depends on GlusterFS inode ctx APIs, list macros, locks, thread helpers, `gf_upcall` structures, dict APIs, AFR xattr prefix handling, fnmatch-style registration matching, and `upcall.h` types. Integrates with the server/client notification path via `GF_EVENT_UPCALL` and `GF_UPCALL_CACHE_INVALIDATION`.

## Risks
- Notifications are sent from the I/O path, with comments noting async delivery would be preferable.
- Lock ordering spans inode locks, private list locks, and client-list mutexes; deadlocks or use-after-free are risks if lifecycle changes.
- Reaper sleeps `timeout / 2`; very small or zero timeout values could cause busy behavior.
- Xattr filtering mutates dictionaries copied into local state; callers must not share mutable dicts incorrectly.
- `this->notify` failure removes a client entry while iterating, so list-safe traversal is essential.

## Test Signals
Tests should cover client registration, same-client suppression, cross-client notification, timeout expiry, inode forget/UP_FORGET, xattr registration and filtering, AFR pending xattr comparison, nameless lookup linked-inode handling, reaper cleanup, and reconfigure timeout changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/upcall/src/upcall-internal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/upcall/src/upcall-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/features/upcall/src/upcall-mem-types.h

## Purpose
Defines memory-accounting categories for upcall.

## Important APIs, Types, and Functions
- `enum gf_upcall_mem_types_` includes `gf_upcall_mt_conf_t`, `gf_upcall_mt_private_t`, `gf_upcall_mt_upcall_inode_ctx_t`, `gf_upcall_mt_upcall_client_entry_t`, and `gf_upcall_mt_end`.

## Control Flow
No runtime control flow.

## State and Persistence
No mutable state. Categories classify allocations in memory accounting.

## Dependencies and Integration Points
Includes `glusterfs/mem-types.h`. Used by `upcall.c` and `upcall-internal.c` allocations and `xlator_mem_acct_init()`.

## Risks
Enum reordering can confuse memory accounting; append new categories before the end marker.

## Test Signals
Compile and statedump/memory-accounting checks for upcall allocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/upcall/src/upcall-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/upcall/src/upcall-messages.h -->
# sources/distributed-fs/glusterfs/xlators/features/upcall/src/upcall-messages.h

## Purpose
Defines message IDs for upcall logging.

## Important APIs, Types, and Functions
- `GLFS_MSGID(UPCALL, UPCALL_MSG_NO_MEMORY, UPCALL_MSG_INTERNAL_ERROR, UPCALL_MSG_NOTIFY_FAILED)` registers three message IDs.

## Control Flow
No runtime control flow.

## State and Persistence
Message ordering is persistent logging ABI and must remain stable.

## Dependencies and Integration Points
Depends on `glfs-message-id.h`. Used by `upcall.c`/`upcall-internal.c` in `gf_msg()` calls.

## Risks
Removing or reordering IDs breaks log-id stability.

## Test Signals
Build and log-format tests for upcall error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/upcall/src/upcall-messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/upcall/src/upcall.c -->
# sources/distributed-fs/glusterfs/xlators/features/upcall/src/upcall.c

## Purpose
Implements the public fop surface and lifecycle for the `upcall` translator. It wraps many filesystem operations, records clients that have touched inodes, and sends cache-invalidation notifications to other clients when data, metadata, dentries, or selected xattrs change.

## Important APIs, Types, and Functions
- `upcall_local_init()` allocates per-call state, refs inode/fd, copies locs, and optionally copies xattrs.
- `UPCALL_STACK_UNWIND()` via `upcall.h` wipes local state after unwinding.
- Read/access fops (`up_lookup`, `up_open`, `up_stat`, `up_readv`, `up_readdirp`, etc.) update client state with `UP_UPDATE_CLIENT`.
- Write fops (`up_writev`, `up_truncate`, `up_ftruncate`, `up_fallocate`, `up_discard`, `up_zerofill`) invalidate with `UP_WRITE_FLAGS`.
- Metadata fops (`up_setattr`, `up_fsetattr`) invalidate attribute flags and include `UP_XATTR` when mode changes may affect ACL-derived xattrs.
- Dentry operations (`up_create`, `up_mkdir`, `up_mknod`, `up_symlink`, `up_unlink`, `up_link`, `up_rmdir`, `up_rename`) invalidate parent and child caches with parent stat buffers.
- Xattr operations (`up_setxattr`, `up_fsetxattr`, `up_removexattr`, `up_fremovexattr`, `up_xattrop`, `up_fxattrop`) filter registered xattrs before notification.
- `up_ipc()` lets clients register xattrs for invalidation through `GF_IPC_TARGET_UPCALL`.
- Lifecycle: `mem_acct_init()`, `init()`, `reconfigure()`, `fini()`, `upcall_forget()`, `notify()`, fops/cbks/options/xlator API.

## Control Flow
Each fop checks `EXIT_IF_UPCALL_OFF()`. When disabled, it winds directly to the child with no local allocation. When enabled, it allocates `upcall_local_t`, winds to the child, then the callback examines success and calls `upcall_cache_invalidate()` with operation-specific flags and stat/xattr data before unwinding.

`readdirp` additionally iterates returned entries and updates client state for each entry inode. `rename` sends invalidations for the renamed inode, old parent, and new parent if distinct. Xattrop handling compares AFR pending xattrs from request and response to notify only when a pending xattr is first set. `up_ipc()` records requested xattr patterns in `priv->xattrs`.

`init()` allocates private state, creates the registered-xattr dict, reads enable/timeout options, initializes locks/lists, creates a local pool, and starts the reaper thread when cache invalidation is enabled. `fini()` stops the reaper, releases the xattr dict, destroys locks/pools, and frees private state.

## State and Persistence
Persistent runtime state is in `upcall_private_t`; per-call state is in `upcall_local_t`. No on-disk state is written by upcall. Client access histories and registered xattrs are memory-only and lost on graph restart.

## Dependencies and Integration Points
Depends on `upcall-internal.c` for invalidation mechanics, GlusterFS stack APIs, client identity, `gf_upcall` notification types, XDR/RPC libraries, and cache-invalidation option parsing. It integrates with clients through `GF_EVENT_UPCALL` notifications and with xattr registration through IPC.

## Risks
- Disabled path relies on the `out` labels being before `STACK_WIND`; accidental local assumptions can break no-op mode.
- Many callback signatures must exactly match child fops; signature drift can silently break compile.
- `up_setxattr_cbk()`/removal callbacks assume `xdata` may contain `GF_POSTSTAT`; null or missing poststat changes flag richness.
- Notification timing is best effort and synchronous in callback path.
- Registered xattr dictionary grows by IPC registration and has no unregister path.

## Test Signals
Exercise disabled passthrough, enabled client registration, read-only updates, write invalidations, rename/link/unlink parent invalidations, readdirp entry updates, xattr registration/filtering, AFR xattrop first-pending detection, reconfigure thread startup, notify failure logging, and fini cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/upcall/src/upcall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/upcall/src/upcall.h -->
# sources/distributed-fs/glusterfs/xlators/features/upcall/src/upcall.h

## Purpose
Declares upcall private/client/inode/local state and the helper APIs shared between `upcall.c` and `upcall-internal.c`.

## Important APIs, Types, and Functions
- `EXIT_IF_UPCALL_OFF()` branches to a label when cache invalidation is disabled.
- `UPCALL_STACK_UNWIND()` and `UPCALL_STACK_DESTROY()` clean `upcall_local_t` around stack unwind/destroy.
- `upcall_private_t` stores timeout, inode context list/lock, reaper thread, registered xattr dict, fini flag, enable flag, and init flag.
- `upcall_client_t` stores client UID and access/expire timing.
- `upcall_inode_ctx_t` stores inode GFID and client list.
- `upcall_local_t` stores per-fop inode, locs, fd, and xattr copy.
- Function prototypes expose cleanup, reaper, enable checks, invalidation, xattr filtering/comparison, and invalidation-needed checks.

## Control Flow
Macros define common branch and cleanup behavior used by nearly every fop wrapper. The local-wipe pattern ensures refs are dropped after unwind.

## State and Persistence
Defines in-memory state only. The client/inode registries are per-graph runtime cache state.

## Dependencies and Integration Points
Depends on GlusterFS client, upcall utils, compat errno, message/memory headers, stack, loc, dict, and inode types.

## Risks
The `upcall_local` comment notes pointer lifetime uncertainty; all stored pointers must be refcounted or copied. Macros hide cleanup side effects and require consistent frame ownership.

## Test Signals
Compile coverage plus runtime leak/refcount tests around fop callbacks and fini/forget paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/upcall/src/upcall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/utime/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/utime/Makefile.am

## Purpose
Top-level Automake recursion file for the utime feature translator.

## Important APIs, Types, and Functions
- `SUBDIRS = src`.
- Empty `CLEANFILES`.

## Control Flow
Build recursion into `src`.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Integrated by GlusterFS feature translator build tree.

## Risks
Without this recursion, `utime.la` and generated fops are omitted.

## Test Signals
`make` should descend into utime `src`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/utime/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/utime/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/utime/src/Makefile.am

## Purpose
Builds the `utime.la` translator and generates its fop wrapper source/header from templates.

## Important APIs, Types, and Functions
- `AUTOMAKE_OPTIONS = subdir-objects`.
- `utime_sources` includes `utime-helpers.c` and `utime.c`.
- `nodist_utime_la_SOURCES = utime-autogen-fops.c utime-autogen-fops.h`.
- `BUILT_SOURCES = utime-autogen-fops.h`.
- Python generators create `.c` and `.h` outputs from templates when `#pragma generate` is encountered.
- Links `libglusterfs.la`, includes `xlators/lib/src`, and removes installed `utime.so` in `uninstall-local`.

## Control Flow
During build, `utime-gen-fops-c.py` and `utime-gen-fops-h.py` expand templates before compiling the module.

## State and Persistence
Generated files are build artifacts and cleaned through `CLEANFILES`.

## Dependencies and Integration Points
Depends on Python, libglusterfs generator module, `libxlator.h`, GlusterFS headers, and build variables. The generated wrappers are required by `utime.c` fops registration.

## Risks
Generator/template drift can cause missing fop symbols. Python path assumes relative location to `libglusterfs/src`.

## Test Signals
Clean build from generated sources, `make clean`, and verifying all fops referenced in `utime.c` are generated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/utime/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/utime/src/utime-autogen-fops-tmpl.c -->
# sources/distributed-fs/glusterfs/xlators/features/utime/src/utime-autogen-fops-tmpl.c

## Purpose
Template C source used to generate `utime-autogen-fops.c`.

## Important APIs, Types, and Functions
- Includes `config.h` defensively and `utime-helpers.h`.
- Contains `#pragma generate`, which the Python generator replaces with generated fop wrappers and callbacks.

## Control Flow
The file itself has no final fop logic until generation. The generator copies surrounding text and replaces the pragma with generated code.

## State and Persistence
No runtime state. It is a source template for generated build artifacts.

## Dependencies and Integration Points
Consumed by `utime-gen-fops-c.py` from `Makefile.am`. Generated code calls `gl_timespec_get()`, `utime_update_attribute_flags()`, and child fops.

## Risks
Removing or misspelling the pragma yields an empty or incomplete generated fops source. Include order affects generated wrappers.

## Test Signals
Generated `utime-autogen-fops.c` should contain `BEGIN GENERATED CODE` and definitions for all selected utime fops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/utime/src/utime-autogen-fops-tmpl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/utime/src/utime-autogen-fops-tmpl.h -->
# sources/distributed-fs/glusterfs/xlators/features/utime/src/utime-autogen-fops-tmpl.h

## Purpose
Template header used to generate prototypes for utime fop wrappers.

## Important APIs, Types, and Functions
- Include guard `_UTIME_AUTOGEN_FOPS_H`.
- Contains `#pragma generate`, expanded by `utime-gen-fops-h.py`.

## Control Flow
No runtime flow. Generator replaces pragma with fop prototypes.

## State and Persistence
No state.

## Dependencies and Integration Points
Used by `Makefile.am` as source for `utime-autogen-fops.h`, included by utime implementation through generated build integration.

## Risks
Missing pragma or guard changes can break symbol declarations or duplicate inclusion.

## Test Signals
Build should generate prototypes matching generated C definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/utime/src/utime-autogen-fops-tmpl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/utime/src/utime-gen-fops-c.py -->
# sources/distributed-fs/glusterfs/xlators/features/utime/src/utime-gen-fops-c.py

## Purpose
Generates C fop wrappers and callbacks for utime from libglusterfs operation metadata and a template file.

## Important APIs, Types, and Functions
- Imports `ops`, `fop_subs`, `cbk_subs`, and `generate` from `libglusterfs/src/generator.py`.
- Template families generate common fops, read fops, write fops, copy-file-range fops, and special setattr/fsetattr logic.
- `gen_defaults()` emits callback then fop implementation for names selected in `utime_ops`, `utime_read_op`, `utime_write_op`, `utime_setattr_ops`, and `utime_copy_file_range_ops`.
- Main loop copies template lines and replaces `#pragma generate` with generated code markers and generated functions.

## Control Flow
At build time, the script reads the template path from `sys.argv[1]`, scans each line, and prints generated C to stdout. Generated fops set `frame->root->ctime`, call `utime_update_attribute_flags()` or special setattr logic, then wind to the child and unwind in generated callbacks.

## State and Persistence
No persistent state. Output is a generated build artifact.

## Dependencies and Integration Points
Depends on Python 3, relative import of GlusterFS generator metadata, and fop name tables matching current GlusterFS APIs. Integrated by `Makefile.am`.

## Risks
Operation list drift can omit new fops or generate stale signatures. Special setattr logic uses `valid` and `stbuf` names from generator substitutions and is sensitive to signature changes. Generated code uses stdout, so build redirection must remain correct.

## Test Signals
Run generator and compile generated output. Inspect that `readv`, `writev`, `setattr`, `fsetattr`, and `copy_file_range` receive their specialized templates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/utime/src/utime-gen-fops-c.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/utime/src/utime-gen-fops-h.py -->
# sources/distributed-fs/glusterfs/xlators/features/utime/src/utime-gen-fops-h.py

## Purpose
Generates declarations for utime fop wrappers.

## Important APIs, Types, and Functions
- Imports `ops`, `fop_subs`, and `generate`.
- `OP_FOP_TEMPLATE` emits an `int32_t gf_utime_<name>(...)` prototype.
- `utime_ops` lists all wrappers requiring declarations.
- `gen_defaults()` iterates `ops.items()` and prints prototypes for selected names.

## Control Flow
Reads a template file from `sys.argv[1]`, replaces `#pragma generate` with generated prototype block, and prints all other lines unchanged.

## State and Persistence
No runtime state. Produces generated header artifact.

## Dependencies and Integration Points
Same generator metadata dependency as the C generator. Integrated by `Makefile.am`.

## Risks
If `utime_ops` diverges from C generator lists, compile can fail with missing declarations or definitions.

## Test Signals
Generated header should declare every function referenced in `utime.c` fops table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/utime/src/utime-gen-fops-h.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/utime/src/utime-helpers.c -->
# sources/distributed-fs/glusterfs/xlators/features/utime/src/utime-helpers.c

## Purpose
Provides shared helpers for utime-generated fop wrappers: current-time capture and mapping fops to metadata-update flags.

## Important APIs, Types, and Functions
- `gl_timespec_get()` uses C11 `timespec_get(TIME_UTC)` when available, otherwise Gluster's `timespec_now_realtime()`.
- `utime_update_attribute_flags()` sets `frame->root->flags` bits such as `MDATA_CTIME`, `MDATA_MTIME`, `MDATA_ATIME`, `MDATA_PAR_CTIME`, and `MDATA_PAR_MTIME` based on `glusterfs_fop_t`.

## Control Flow
Generated wrappers call `gl_timespec_get(&frame->root->ctime)`, then call `utime_update_attribute_flags()`. The switch maps each fop family: xattr changes to ctime, allocation/zero-fill to mtime/atime, open/read/opendir to optional atime, creates to all inode and parent timestamps, deletes to ctime and parent timestamps, writes/truncates to ctime/mtime, and copy-file-range to destination ctime/mtime plus optional source atime.

## State and Persistence
Updates only per-call `frame->root` timestamp and flags. It reads `utime_priv_t.noatime` from `this->private`.

## Dependencies and Integration Points
Depends on `utime.h`, GlusterFS stack/time APIs, and metadata flag definitions. Called by generated utime fops.

## Risks
Default case clears `frame->root->flags`; unexpected fops passed here can erase preexisting flags. Missing null check for `this->private` after `this` validation assumes initialized translator private state.

## Test Signals
Unit or integration tests should assert flags for each generated fop class, especially noatime behavior and copy-file-range dual timestamp semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/utime/src/utime-helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/utime/src/utime-helpers.h -->
# sources/distributed-fs/glusterfs/xlators/features/utime/src/utime-helpers.h

## Purpose
Declares utime helper functions.

## Important APIs, Types, and Functions
- `gl_timespec_get(struct timespec *ts)`.
- `utime_update_attribute_flags(call_frame_t *frame, xlator_t *this, glusterfs_fop_t fop)`.

## Control Flow
No direct control flow; prototypes are used by generated wrappers and `utime-helpers.c`.

## State and Persistence
No state.

## Dependencies and Integration Points
Includes GlusterFS stack and timespec headers plus `<time.h>`.

## Risks
Signature drift breaks generated code.

## Test Signals
Compile generated utime fops against this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/utime/src/utime-helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/utime/src/utime-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/features/utime/src/utime-mem-types.h

## Purpose
Defines memory-accounting categories for utime.

## Important APIs, Types, and Functions
- `enum utime_mem_types_` starts at `gf_common_mt_end + 1`.
- Categories include `utime_mt_utime_t` and `utime_mt_end`.

## Control Flow
No runtime control flow.

## State and Persistence
No state; categories feed memory accounting.

## Dependencies and Integration Points
Includes `glusterfs/mem-types.h`. Used by `utime.c` for private allocation and `mem_acct_init()`.

## Risks
Changing values can affect memory accounting reports.

## Test Signals
Compile and memory-accounting/statedump validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/utime/src/utime-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/utime/src/utime-messages.h -->
# sources/distributed-fs/glusterfs/xlators/features/utime/src/utime-messages.h

## Purpose
Defines message IDs for utime logging.

## Important APIs, Types, and Functions
- `GLFS_MSGID(UTIME, UTIME_MSG_NO_MEMORY, UTIME_MSG_SET_MDATA_FAILED, UTIME_MSG_DICT_SET_FAILED)`.

## Control Flow
No runtime control flow.

## State and Persistence
Message ordering is persistent logging ABI.

## Dependencies and Integration Points
Included by `utime.c` for `gf_msg()` calls.

## Risks
IDs must be appended, not removed or reordered.

## Test Signals
Build and log-path coverage for no-memory, mdata set, and dict set failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/utime/src/utime-messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/utime/src/utime.c -->
# sources/distributed-fs/glusterfs/xlators/features/utime/src/utime.c

## Purpose
Implements the utime translator lifecycle and lookup behavior, while registering generated fop wrappers that set metadata timestamp update flags for ctime/mtime/atime handling.

## Important APIs, Types, and Functions
- Placeholder cbks/dumpops (`gf_utime_invalidate`, `gf_utime_forget`, fd/inode dump helpers, etc.) currently return success/no-op.
- `mem_acct_init()` initializes memory accounting to `utime_mt_end`.
- `gf_utime_lookup()` ensures lookup xdata asks for `GF_XATTR_MDATA_KEY`.
- `gf_utime_set_mdata_lookup_cbk()` checks lookup results and, when missing mdata, builds `struct mdata_iatt`, creates a separate frame, stubs the original lookup callback, and sends a child `setxattr` with `CTIME_MDATA_XDATA_KEY`.
- `gf_utime_set_mdata_setxattr_cbk()` logs but does not fail lookup when mdata setxattr fails, resumes the saved lookup stub, and destroys the helper frame.
- `init()`, `fini()`, and `reconfigure()` manage `utime_priv_t.noatime`.
- `fops` references generated wrappers and the custom lookup wrapper; `cbks`, `dumpops`, `options`, and `xlator_api` register the translator.

## Control Flow
Generated fops set `frame->root->ctime` and metadata flags, then pass through to the child. `gf_utime_lookup()` refs or creates xdata, adds `GF_XATTR_MDATA_KEY`, and winds lookup. If lookup succeeds and the mdata xattr is absent, the callback creates metadata from the returned `iatt`, issues an internal root-owned setxattr with `GF_CLIENT_PID_SET_UTIME`, stores a stub for the original lookup callback in the helper frame, and resumes that stub after the setxattr callback. If mdata already exists or lookup failed, it unwinds normally.

## State and Persistence
`utime_priv_t` stores only `noatime`. Per-call state is mostly xdata and helper-frame stubs. Persistent state is the on-disk metadata xattr written via `CTIME_MDATA_XDATA_KEY`.

## Dependencies and Integration Points
Depends on generated fops, `utime-helpers`, call stubs, metadata xattr helpers (`iatt_to_mdata`, `dict_set_mdata`), GlusterFS stack APIs, and the `ctime` feature. Option `noatime` is client-settable/doc-tagged under `ctime`.

## Risks
- Helper-frame/stub ownership is subtle; allocation failures must destroy frames and unref dicts/inodes.
- Lookup intentionally ignores mdata setxattr failure after logging, so metadata initialization can lag.
- Many dump/callback hooks are no-ops, which may limit observability.
- No child-count validation is present in `init()` in this file; graph correctness may rely on broader xlator conventions.

## Test Signals
Tests should cover lookup with missing/present mdata, internal setxattr pid/uid/gid, failure to allocate dict/mdata/stub/frame, noatime reconfigure, generated fop flag behavior, and build-time generation of all fop symbols in the fops table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/utime/src/utime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/utime/src/utime.h -->
# sources/distributed-fs/glusterfs/xlators/features/utime/src/utime.h

## Purpose
Declares the utime private configuration structure and includes generated fop prototypes.

## Important APIs, Types, and Functions
- `utime_priv_t` contains `gf_boolean_t noatime`.
- Includes `utime-autogen-fops.h` for generated wrapper prototypes.

## Control Flow
No runtime flow.

## State and Persistence
Defines the translator-private in-memory `noatime` flag.

## Dependencies and Integration Points
Depends on `xlator.h`, `defaults.h`, and generated header availability.

## Risks
Generated header must exist before compile. Adding private fields requires lifecycle updates in `init()`, `reconfigure()`, and `fini()`.

## Test Signals
Build generated header and verify noatime option affects generated wrapper behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/utime/src/utime.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/lib/src/libxlator.c -->
# sources/distributed-fs/glusterfs/xlators/lib/src/libxlator.c

## Purpose
Provides shared helper logic for xlator marker xattrs, especially geo-replication marker `xtime` and volume mark aggregation across child subvolumes.

## Important APIs, Types, and Functions
- Default gauges `marker_xtime_default_gauge` and `marker_uuid_default_gauge` define success/failure policies.
- `match_uuid_local()` validates `trusted.glusterfs.<uuid>.xtime` keys.
- `evaluate_marker_results()` maps result counters to errno using gauge policy and `marker_idx_errno_map`.
- `cluster_markerxtime_cbk()` aggregates maximum xtime across children.
- `cluster_markeruuid_cbk()` aggregates/validates volume mark values across children.
- `gf_get_min_stime()` and `gf_get_max_stime()` merge serialized stime values into a dict using network/host time comparison.
- `cluster_handle_marker_getxattr()` validates caller and key, allocates local aggregation state, asks caller-supplied `populate_args()` for subvolumes/gauge overrides, winds getxattr to each selected child, and unwinds with aggregate result.

## Control Flow
`cluster_handle_marker_getxattr()` only handles gsynchronization daemon calls (`GF_CLIENT_PID_GSYNCD`) and marker xattr names. It sets `frame->local` to `xl_marker_local_t`, winds child getxattr requests, and child callbacks decrement `call_count` under `frame->lock`. When the last callback arrives, `cluster_marker_unwind()` restores the caller's previous local state, optionally adds aggregate data to a dict, evaluates counters against the gauge, and uses a specialized unwind callback or default getxattr unwind.

## State and Persistence
Per-aggregation state lives in `xl_marker_local_t`: selected volume UUID, aggregate time buffers or volume mark, result counters, gauge, child call count, and saved caller local. Persistent data being read is marker xattrs on child bricks.

## Dependencies and Integration Points
Depends on dict APIs, GlusterFS stack winding, child xlator lists, marker xattr naming, network byte order helpers, and gsyncd PID conventions. Used by cluster translators that need marker xattr aggregation and supply `populate_args()`.

## Risks
- Uses `alloca(num_subvols * sizeof(*subvols))`; zero or very large child counts deserve scrutiny.
- `cluster_markeruuid_cbk()` allocates/replaces `local->volmark`; failure and cleanup paths must avoid leaks.
- Gauge policy is compact but non-obvious; incorrect custom gauge from `populate_args()` changes error semantics.
- The code assumes callbacks arrive exactly `call_count` times and uses shared `frame->lock`.

## Test Signals
Tests should cover marker key validation, gsyncd-only access, xtime max aggregation, volume mark major/minor mismatch, child ENOENT/ENODATA/ENOTCONN error policies, custom `populate_args()` gauges, and min/max stime dict merges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/lib/src/libxlator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/lib/src/libxlator.h -->
# sources/distributed-fs/glusterfs/xlators/lib/src/libxlator.h

## Purpose
Declares shared marker xattr constants, aggregation structures, gauges, callbacks, and helper APIs for cluster translators.

## Important APIs, Types, and Functions
- Marker constants: `MARKER_XATTR_PREFIX`, `XTIME`, `VOLUME_MARK`, `GF_XATTR_MARKER_KEY`, `MARKER_UUID_TYPE`, and `MARKER_XTIME_TYPE`.
- `xlator_specf_unwind_t` lets callers supply specialized unwind behavior.
- Packed `struct volume_mark` represents serialized volume mark xattr data.
- `marker_result_idx_t` enumerates aggregation result buckets.
- `struct marker_str` (`xl_marker_local_t`) stores aggregation state.
- Prototypes for marker callbacks, `cluster_handle_marker_getxattr()`, `match_uuid_local()`, `gf_get_min_stime()`, and `gf_get_max_stime()`.

## Control Flow
No implementation flow, but comments document the gauge/counter policy consumed by `evaluate_marker_results()`.

## State and Persistence
Defines per-call aggregation state and serialized volume-mark layout. No global mutable state except external default gauge arrays.

## Dependencies and Integration Points
Includes GlusterFS defaults, dict, globals, stack, compat headers. Used by cluster/marker related translators and utime build includes it.

## Risks
The packed `volume_mark` layout is persistent xattr ABI; field changes are incompatible. Gauge semantics must be preserved for callers.

## Test Signals
Compile callers and validate serialized `volume_mark` size/layout and aggregation behavior through `libxlator.c` tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/lib/src/libxlator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/meta/Makefile.am

## Purpose
Top-level Automake recursion file for the meta translator.

## Important APIs, Types, and Functions
- `SUBDIRS = src`.

## Control Flow
Build recursion only.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Integrated by GlusterFS xlator build tree.

## Risks
Removing recursion prevents `meta.la` from building.

## Test Signals
`make` should descend into `xlators/meta/src`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/meta/src/Makefile.am

## Purpose
Builds the `meta.la` xlator, which exposes GlusterFS runtime introspection as a virtual metadata filesystem.

## Important APIs, Types, and Functions
- Installs under `$(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator`.
- `meta_la_SOURCES` enumerates core meta files plus many virtual file/dir/link implementations.
- Links `libglusterfs.la`.
- `noinst_HEADERS` include `meta.h`, `meta-hooks.h`, and `meta-mem-types.h`.
- Include paths cover libglusterfs and RPC XDR headers.

## Control Flow
Automake compiles all listed virtual-node implementations into one module.

## State and Persistence
No direct runtime state; controls build artifacts.

## Dependencies and Integration Points
Depends on libglusterfs and meta source files. The requested source files in this group are entries in `meta_la_SOURCES`.

## Risks
Omitting a virtual node implementation breaks hook references or removes introspection files. Adding a new meta node requires updating this source list.

## Test Signals
Build `meta.la`, load the meta translator, and inspect that listed virtual files/dirs appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/active-link.c -->
# sources/distributed-fs/glusterfs/xlators/meta/src/active-link.c

## Purpose
Implements the `active` symlink in the meta filesystem, pointing at the active graph UUID.

## Important APIs, Types, and Functions
- `active_link_fill()` writes `this->ctx->active->graph_uuid` into the strfd.
- `active_link_ops` exposes `.link_fill`.
- `meta_active_link_hook()` attaches the ops to the inode.

## Control Flow
On lookup/hook, `meta_active_link_hook()` sets inode ops. Later readlink calls invoke `active_link_fill()`.

## State and Persistence
Reads runtime context active graph pointer; no owned state.

## Dependencies and Integration Points
Depends on meta ops helpers and GlusterFS context graph state. Referenced by `graphs-dir.c`.

## Risks
Assumes `this->ctx->active` is valid. Active graph changes should be reflected dynamically because fill reads context at access time.

## Test Signals
Meta filesystem readlink for `graphs/active` should return current active graph UUID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/active-link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/cmdline-file.c -->
# sources/distributed-fs/glusterfs/xlators/meta/src/cmdline-file.c

## Purpose
Implements a meta virtual file exposing the process command line string as JSON-like text.

## Important APIs, Types, and Functions
- `cmdline_file_fill()` writes `this->ctx->cmdlinestr` into a `Cmdlinestr` field when present.
- `cmdline_file_ops` exposes `.file_fill`.
- `meta_cmdline_file_hook()` attaches file ops to the inode.

## Control Flow
Hook sets file ops; read/fill calls serialize the command line.

## State and Persistence
Reads `this->ctx->cmdlinestr`; no owned state.

## Dependencies and Integration Points
Used by meta root or process introspection directories through hook declarations. Depends on strfd formatting.

## Risks
Output is manually formatted and may not escape embedded quotes or control characters in the command line.

## Test Signals
Reading the meta cmdline file should include the process command line when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/cmdline-file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/frames-file.c -->
# sources/distributed-fs/glusterfs/xlators/meta/src/frames-file.c

## Purpose
Implements a meta virtual file that dumps active call stacks/frames in JSON-like text.

## Important APIs, Types, and Functions
- `frames_file_fill()` locks `this->ctx->pool`, iterates `pool->all_frames`, then each stack's `myframes`, printing frame xlator, timing, parent, wind/unwind edges, completion state, stack unique id, fop type, uid/gid, and lock owner.
- `frames_file_ops` exposes `.file_fill`.
- `meta_frames_file_hook()` attaches file ops.

## Control Flow
During file read, the function validates arguments, locks the global call pool, serializes all stacks/frames, and unlocks before returning `strfd->size`.

## State and Persistence
Reads volatile call-pool state. Does not persist anything.

## Dependencies and Integration Points
Depends on call stack/frame structures, `gf_fop_list`, `lkowner_utoa()`, strfd, and meta file-fill plumbing.

## Risks
Manual JSON formatting can produce malformed output if strings contain quotes. Holding the call-pool lock while formatting may be expensive on large active-frame sets.

## Test Signals
Reading the frames meta file during active I/O should show stack counts and frame data without deadlock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/frames-file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/graph-dir.c -->
# sources/distributed-fs/glusterfs/xlators/meta/src/graph-dir.c

## Purpose
Implements a per-graph meta directory that exposes fixed graph files/links and one subdirectory per xlator in the graph.

## Important APIs, Types, and Functions
- `graph_dir_dirents` defines fixed `top` symlink and `volfile` file entries.
- `graph_dir_fill()` gets `glusterfs_graph_t` from inode meta ctx, counts graph xlators, allocates dynamic dirents, and creates one directory entry per xlator.
- `glusterfs_graph_lookup()` scans `this->ctx->graphs` by graph UUID.
- `meta_graph_dir_hook()` sets graph dir ops and stores the graph pointer in inode meta ctx.

## Control Flow
When a graph UUID directory is looked up, the hook resolves the graph and stores it. Directory reads include fixed entries plus dynamic xlator directories.

## State and Persistence
Stores a graph pointer in inode metadata context. Reads live graph list and xlator names.

## Dependencies and Integration Points
Depends on meta ctx helpers, graph list, xlator linked list, and hooks for `top`, `volfile`, and xlator dirs. Used by `graphs-dir.c` dynamic entries.

## Risks
`graph_dir_fill()` allocates `count` entries without an explicit null terminator in the dynamic array; correctness depends on meta core using returned count. Graph pointer lifetime must outlive inode ctx usage.

## Test Signals
Meta graph directory listing should show `top`, `volfile`, and every xlator in the graph.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/graph-dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/graphs-dir.c -->
# sources/distributed-fs/glusterfs/xlators/meta/src/graphs-dir.c

## Purpose
Implements the meta `graphs` directory, exposing the active graph link and one directory per known graph UUID.

## Important APIs, Types, and Functions
- `graphs_dir_dirents` includes `active` symlink.
- `graphs_dir_fill()` counts `this->ctx->graphs`, allocates dirents, and creates graph directory entries named by `graph_uuid` using `meta_graph_dir_hook`.
- `graphs_dir_ops` combines fixed and dynamic dirents.
- `meta_graphs_dir_hook()` attaches ops to the inode.

## Control Flow
Lookup/hook sets directory ops; readdir uses fixed plus dynamic graph entries.

## State and Persistence
Reads runtime graph list; no owned persistent state.

## Dependencies and Integration Points
Depends on active link and graph directory hooks, GlusterFS context graph list, and meta directory machinery.

## Risks
Graph list mutation during directory fill would require safety from surrounding graph/context lifecycle. Allocated dynamic names must be freed by meta core.

## Test Signals
Reading meta graphs directory should show `active` and each graph UUID directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/graphs-dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/history-file.c -->
# sources/distributed-fs/glusterfs/xlators/meta/src/history-file.c

## Purpose
Implements a meta virtual file exposing the GlusterFS log history buffer.

## Important APIs, Types, and Functions
- `history_file_fill()` writes `this->ctx->log.history`.
- `history_file_ops` exposes `.file_fill`.
- `meta_history_file_hook()` attaches ops.

## Control Flow
File read invokes fill, which prints history when present and returns `strfd->size`.

## State and Persistence
Reads in-memory logging history; no state mutation.

## Dependencies and Integration Points
Depends on logging context and strfd. Listed in meta build sources and hook tables elsewhere.

## Risks
Assumes history is a printable string. Large history output can grow strfd.

## Test Signals
Meta history file should reflect recent log history when logging history is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/history-file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/logfile-link.c -->
# sources/distributed-fs/glusterfs/xlators/meta/src/logfile-link.c

## Purpose
Implements a meta symlink exposing the current log file path.

## Important APIs, Types, and Functions
- `logfile_link_fill()` writes `this->ctx->log.filename`.
- `logfile_link_ops` exposes `.link_fill`.
- `meta_logfile_link_hook()` attaches ops.

## Control Flow
Readlink invokes fill after hook attachment.

## State and Persistence
Reads logging filename from runtime context.

## Dependencies and Integration Points
Used by the meta logging directory. Depends on meta symlink support.

## Risks
Assumes log filename is non-null or strprintf tolerates it.

## Test Signals
Meta logging logfile symlink should resolve to the active log path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/logfile-link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/logging-dir.c -->
# sources/distributed-fs/glusterfs/xlators/meta/src/logging-dir.c

## Purpose
Implements the meta logging directory.

## Important APIs, Types, and Functions
- `logging_dir_dirents` defines `logfile` symlink, `loglevel` file, and `history` file.
- `logging_dir_ops` exposes fixed dirents.
- `meta_logging_dir_hook()` attaches ops.

## Control Flow
Directory hook sets fixed entries; readdir exposes logging introspection nodes.

## State and Persistence
No owned state; child entries read logging runtime state.

## Dependencies and Integration Points
Depends on hooks for logfile, loglevel, and history files. Integrated by meta root/view directories.

## Risks
Static directory must stay synchronized with hook implementations and build source list.

## Test Signals
Listing meta logging directory should show `logfile`, `loglevel`, and `history`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/logging-dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/loglevel-file.c -->
# sources/distributed-fs/glusterfs/xlators/meta/src/loglevel-file.c

## Purpose
Implements a readable and writable meta file for the current log level.

## Important APIs, Types, and Functions
- `loglevel_file_fill()` prints `gf_log_get_loglevel()`.
- `loglevel_file_write()` parses a string level with `gf_log_level_from_string()`, rejects invalid values with `EINVAL`, and calls `gf_log_set_loglevel()`.
- `loglevel_file_ops` exposes `.file_fill` and `.file_write`.
- `meta_loglevel_file_hook()` attaches ops.

## Control Flow
Read fills the current level. Write parses user data and updates global log level on success.

## State and Persistence
Mutates process-wide logging verbosity. Persistence beyond process lifetime depends on external configuration, not this file.

## Dependencies and Integration Points
Depends on GlusterFS logging APIs and meta writable-file hooks.

## Risks
Invalid strings must not change log level. Concurrent writes affect global logging immediately.

## Test Signals
Read current level, write valid level, confirm logging level changes, write invalid level and expect `EINVAL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/loglevel-file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/mallinfo-file.c -->
# sources/distributed-fs/glusterfs/xlators/meta/src/mallinfo-file.c

## Purpose
Implements a meta virtual file exposing allocator `mallinfo` information.

## Important APIs, Types, and Functions
- `mallinfo_file_fill()` calls `gf_proc_dump_mallinfo(strfd)`.
- `mallinfo_file_ops` exposes `.file_fill`.
- `meta_mallinfo_file_hook()` attaches ops.

## Control Flow
Read calls the dump helper and returns `strfd->size`.

## State and Persistence
Reads allocator/process memory state; no mutation.

## Dependencies and Integration Points
Depends on GlusterFS proc dump support and strfd.

## Risks
Allocator-specific data may be unavailable or platform-dependent behind `gf_proc_dump_mallinfo()`.

## Test Signals
Reading the meta mallinfo file should produce allocator stats on supported platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/mallinfo-file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/measure-file.c -->
# sources/distributed-fs/glusterfs/xlators/meta/src/measure-file.c

## Purpose
Implements a writable meta control file that starts and stops latency measurement.

## Important APIs, Types, and Functions
- `measure_file_fill()` prints nothing and returns current size.
- `measure_file_write()` interprets `start` and `stop`, calling `gf_latency_toggle(1)` or `gf_latency_toggle(0)`, and rejects other data with `EINVAL`.
- `measure_file_ops` exposes fill and write.
- `meta_measure_file_hook()` attaches ops.

## Control Flow
Write-only control semantics: users write a command string to toggle latency collection.

## State and Persistence
Mutates process-wide latency measurement state. No file content persists.

## Dependencies and Integration Points
Depends on GlusterFS latency instrumentation and meta writable-file plumbing.

## Risks
Simple string comparison requires exact `start` or `stop`; trailing newline behavior depends on write buffer passed by meta core.

## Test Signals
Write `start`/`stop` and verify latency toggles; invalid writes should fail with `EINVAL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/measure-file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/meminfo-file.c -->
# sources/distributed-fs/glusterfs/xlators/meta/src/meminfo-file.c

## Purpose
Implements a meta virtual file exposing GlusterFS memory accounting information.

## Important APIs, Types, and Functions
- `meminfo_file_fill()` calls `gf_proc_dump_mem_info_to_dict(strfd)`.
- `meminfo_file_ops` exposes `.file_fill`.
- `meta_meminfo_file_hook()` attaches ops.

## Control Flow
Read dumps memory accounting into the strfd.

## State and Persistence
Reads process memory accounting state; no mutation.

## Dependencies and Integration Points
Depends on GlusterFS proc dump/memory accounting and meta file-fill support.

## Risks
Output can be large and depends on memory accounting initialization in all translators.

## Test Signals
Reading meta meminfo should include translator allocation categories such as trash/upcall/utime when loaded.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/meta/src/meminfo-file.c -->
