# Research: subset-b-007092

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/gfid-access/src/gfid-access.c -->
# sources/distributed-fs/glusterfs/xlators/features/gfid-access/src/gfid-access.c

## Purpose
Implements the `gfid-access` GlusterFS feature translator. It exposes a virtual `/.gfid` directory whose children are canonical GFID names, maps those virtual dentries back to the real inode table, and forwards most normal fops to the child translator after translating virtual locs to real locs. It also handles special FUSE auxiliary setxattr payloads for GFID-addressed new-file creation and heal lookup.

## Important APIs, Types, and Functions
- `ga_valid_inode_loc_copy()` copies a `loc_t` and replaces virtual parent/inode pointers with real inodes stored in inode ctx.
- `ga_newfile_parse_args()` and `ga_heal_parse_args()` decode packed big-endian control payloads from `GF_FUSE_AUX_GFID_NEWFILE` and `GF_FUSE_AUX_GFID_HEAL`.
- `ga_fill_tmp_loc()` builds a temporary child loc under the real parent, creates or finds the target inode, and injects `"gfid-req"` into xdata.
- `ga_lookup()` is the core virtual namespace handler for `/.gfid`, GFID-name lookup, revalidation, and normal lookup forwarding.
- `ga_virtual_lookup_cbk()` rewrites successful directory lookups to return a virtual inode/GFID while retaining inode ctx back-pointers to the real inode.
- `ga_new_entry()` and `ga_heal_entry()` run helper create/lookup flows on copied frames and unwind the original setxattr request.
- Entry and inode fops (`ga_mkdir`, `ga_unlink`, `ga_rename`, `ga_stat`, `ga_getxattr`, etc.) either reject invalid virtual namespace operations or translate locs with `ga_valid_inode_loc_copy()`.

## Control Flow
Normal lookups wind through `ga_lookup_cbk()`, which caches root stat data and manufactures the `.gfid` directory stat by changing the last GFID byte to `GF_AUX_GFID`. A nameless lookup on the auxiliary GFID or a path lookup of `/.gfid` is satisfied locally. A lookup below `/.gfid` validates the basename as a UUID, deletes `"gfid-req"` from xdata, then performs a GFID lookup against the child. For directory targets, the callback links or finds the real inode and stores it in ctx on the virtual inode, then returns a random/virtual GFID to avoid aliasing the real directory inode in the virtual namespace.

The setxattr path first checks for the two auxiliary payload keys. New-file payloads are parsed, converted to a temp loc, and dispatched as mkdir, symlink, or mknod after setting frame uid/gid. Mknod sends a named lookup first so DHT can clean stale linkto files. Heal payloads run a GFID-targeted lookup. Other setxattr/getxattr/stat/setattr/removexattr and removal/link/rename paths copy the loc and substitute real inodes before winding.

## State and Persistence
The translator keeps only in-memory state: `ga_private_t` stores cached root and virtual `.gfid` stat buffers plus mem pools, and inode ctx maps virtual inodes to real inodes. No on-disk metadata is written by this translator directly. Persistence is delegated to lower translators through normal fops and `"gfid-req"` xdata.

## Dependencies and Integration Points
This code depends on GlusterFS inode ctx APIs, `loc_t`, dict/xdata helpers, stack winding/unwinding, mem pools, `gfid_to_ino`, and default callback helpers. It integrates with FUSE auxiliary GFID requests via xattr keys, with DHT via the mknod pre-lookup, and with statedump via `ga_dump_inodectx()`.

## Risks and Edge Cases
Parsing uses packed blobs and pointer casts; malformed lengths, missing NUL bytes, or unaligned data are important risk points. Directory virtual GFIDs are intentionally random, so ctx lifetime and `forget` cleanup are critical. Some error paths initialize `op_errno` to `ENOMEM` even when parse failures are more like `EINVAL`, which may make diagnostics less exact. `init()` destroys `newfile_args_pool` on failure but does not destroy `heal_args_pool` in the same cleanup branch.

## Test Signals
Exercise lookups for `/`, `/.gfid`, valid/invalid `/.gfid/<uuid>`, file and directory revalidation, and ESTALE-to-ENOENT conversion. Cover auxiliary setxattr newfile/heal payloads for mkdir, symlink, mknod, malformed blobs, and DHT stale lookup behavior. Confirm virtual directory fops reject unsupported mutation and that statedump shows real GFIDs for virtual inode ctx.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/gfid-access/src/gfid-access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/gfid-access/src/gfid-access.h -->
# sources/distributed-fs/glusterfs/xlators/features/gfid-access/src/gfid-access.h

## Purpose
Defines constants, payload structures, private state, local frame state, and validation macros for the `gfid-access` translator.

## Important APIs, Types, and Functions
- `GF_FUSE_AUX_GFID_NEWFILE` and `GF_FUSE_AUX_GFID_HEAL` name the control xattrs consumed by `ga_setxattr()`.
- `GF_GFID_DIR` and `GF_AUX_GFID` define the virtual `.gfid` namespace identity.
- `GFID_ACCESS_ENTRY_OP_CHECK` rejects entry creation/removal under `/.gfid` and direct operations on the virtual directory.
- `GFID_ACCESS_INODE_OP_CHECK` rejects inode fops against `.gfid` itself.
- `ga_newfile_args_t` and `ga_heal_args_t` model decoded auxiliary request payloads.
- `ga_private_t` carries cached stat buffers and mem pools; `ga_local_t` carries copied-frame state for async helper creates.

## Control Flow
The macros are used as early guards in `gfid-access.c` fop handlers. The packed structs guide parser layout: uid, gid, GFID string, mode, basename, and type-specific mkdir/symlink/mknod fields for new-file creation; GFID plus basename for heal.

## State and Persistence
Header-defined state is memory-only. `ga_private_t` survives for the translator lifetime; `ga_local_t` exists per helper operation; decoded argument structs come from mem pools.

## Dependencies and Integration Points
Includes GlusterFS logging, dict, defaults, and translator-specific memory accounting definitions. The macros rely on `__is_root_gfid()` from GlusterFS and `__is_gfid_access_dir()` from the C file.

## Risks and Edge Cases
The macro calls `__is_gfid_access_dir()` before a prototype in this header, so its implementation must remain visible in the C translation unit before macro use matters. Packed structs document wire layout but the parser manually walks blobs, so drift between struct and parser would break auxiliary clients.

## Test Signals
Compile coverage should catch macro/function visibility issues. Behavior tests should assert `ENOTSUP` for `/.gfid` itself and `EPERM` for mutation below virtual GFID entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/gfid-access/src/gfid-access.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/index/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/index/Makefile.am

## Purpose
Top-level Automake file for the index feature translator directory.

## Important APIs, Types, and Functions
No C APIs are defined. `SUBDIRS = src` delegates all build logic to the source subdirectory.

## Control Flow
Automake descends into `src` when building this component.

## State and Persistence
No runtime state. `CLEANFILES` is empty.

## Dependencies and Integration Points
Participates in the GlusterFS recursive build and relies on the `src/Makefile.am` for actual library targets.

## Risks and Edge Cases
Risk is limited to build-system omission; if `src` is removed from `SUBDIRS`, the index translator would not build.

## Test Signals
`make` or `make distcheck` should include the `src` target and produce `index.la` when server builds are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/index/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/index/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/index/src/Makefile.am

## Purpose
Builds the server-side `index.la` feature translator module.

## Important APIs, Types, and Functions
Declares `index_la_SOURCES = index.c`, private headers (`index.h`, `index-mem-types.h`, `index-messages.h`), links against `libglusterfs.la`, and installs under the GlusterFS feature xlator directory when `WITH_SERVER` is set.

## Control Flow
Automake conditionally builds the module only for server builds. Compiler flags include libglusterfs and RPC/XDR include paths.

## State and Persistence
No runtime state; it describes build artifacts only.

## Dependencies and Integration Points
Integrates with GlusterFS module loading through `-module` xlator flags and `$(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/features`.

## Risks and Edge Cases
Missing XDR or libglusterfs include paths would break compilation. Since only `index.c` is compiled, helper logic must stay in that file or be added here if split later.

## Test Signals
Server build should generate `index.la` and include all private headers in distribution checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/index/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/index/src/index-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/features/index/src/index-mem-types.h

## Purpose
Defines translator-specific memory accounting IDs for the index translator.

## Important APIs, Types, and Functions
`enum gf_index_mem_types_` reserves IDs for private state, inode ctx, fd ctx, local frame state, and an end sentinel used by `xlator_mem_acct_init()`.

## Control Flow
There is no control flow; `index.c` uses these constants in allocation calls and memory-accounting initialization.

## State and Persistence
No runtime state. Values must remain unique relative to `gf_common_mt_end`.

## Dependencies and Integration Points
Includes `<glusterfs/mem-types.h>` and feeds GlusterFS memory accounting.

## Risks and Edge Cases
Adding new allocated types without extending this enum reduces accounting precision. Reordering values can disturb diagnostics that rely on stable type names.

## Test Signals
Compile and statedump/mem-accounting checks should show index allocations under these categories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/index/src/index-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/index/src/index-messages.h -->
# sources/distributed-fs/glusterfs/xlators/features/index/src/index-messages.h

## Purpose
Declares stable log message IDs for the index translator.

## Important APIs, Types, and Functions
`GLFS_MSGID(INDEX, ...)` assigns message identifiers for directory creation, readdir, index add/delete, dict failures, inode ctx errors, worker creation, invalid args, fd failures, and invalid graph layout.

## Control Flow
No runtime control flow; `index.c` references these symbols in `gf_msg()` calls.

## State and Persistence
No runtime state. The file documents that IDs must be appended, not removed, to avoid reuse.

## Dependencies and Integration Points
Includes `<glusterfs/glfs-message-id.h>` and integrates with GlusterFS structured logging.

## Risks and Edge Cases
Removing or reordering IDs can break log analytics and documentation. New `gf_msg()` sites should append new IDs here instead of reusing unrelated IDs.

## Test Signals
Build should verify all message IDs referenced by `index.c` are declared.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/index/src/index-messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/index/src/index.c -->
# sources/distributed-fs/glusterfs/xlators/features/index/src/index.c

## Purpose
Implements the `index` translator, which tracks files needing heal or other background attention by creating hard-link based index entries under `.glusterfs/indices/{xattrop,dirty,entry-changes}`. It also exposes those index directories through virtual GFIDs returned by special getxattr keys and supports administrative readdir/unlink/rmdir over the virtual namespace.

## Important APIs, Types, and Functions
- `index_get_type_from_vgfid()`, `index_is_virtual_gfid()`, and `index_get_subdir_from_vgfid()` map generated internal virtual GFIDs to index categories.
- `index_inode_ctx_get()` creates per-inode state with `state[]`, queued stubs, `processing`, and `virtual_pargfid`.
- `index_add()`, `index_del()`, `index_entry_create()`, and `index_entry_delete()` maintain hard-link or directory entries in index subdirs.
- `index_xattrop()` and `index_fxattrop()` serialize tracked xattrop operations per inode and update indices both before and after the child fop.
- `index_getxattr()` returns virtual GFIDs and count xattrs such as `GF_XATTROP_INDEX_COUNT`.
- `index_lookup()`, `index_opendir()`, `index_readdir()`, `index_unlink()`, and `index_rmdir()` implement the virtual interface over on-disk index paths.
- `index_worker()` handles asynchronous call stubs on a private worker thread.
- `init()`, `fini()`, `notify()`, and callbacks manage lifecycle, worker drain, and cleanup.

## Control Flow
Tracked xattrop/fxattrop calls are identified by operation flags and configured watchlists. The wrapper stores local inode/xdata, queues a call stub per inode through `index_queue_process()`, pre-adds index entries for non-zero watched xattrs, optionally creates entry-change name indices, winds to the child, then the callback examines returned xattrs and removes index entries whose watched values are all zero.

The virtual namespace starts when clients request index GFIDs via getxattr. Lookups against those GFIDs or children are handled by a worker stub that maps the loc to an on-disk path, lstats it, constructs an iatt, and stores `virtual_pargfid` for entry-change child directories. Readdir opens the corresponding local directory via fd ctx and converts `dirent` records into `gf_dirent_t`; with `"get-gfid-type"` it launches a synctask to resolve each GFID’s actual type. Unlink/rmdir against virtual entries delete index links or directories instead of forwarding to the child.

## State and Persistence
Persistent state is encoded as files, hard links, and directories under the configured `index-base` path. `index_link_to_base()` creates a base file named `<subdir>-<uuid>` and hard-links GFID entries to it; link count is used to approximate pending counts. `entry-changes` uses per-parent-GFID directories with name entries. In-memory state includes generated internal virtual GFIDs, watchlist dicts, a pending-count cache, fd directory handles, inode ctx state, a worker queue, and synchronization primitives.

## Dependencies and Integration Points
Depends on libglusterfs syscall wrappers, syncop/synctask, inode/fd ctx APIs, dict watchlist helpers, gluster XDR dirent structures, statedump, pthreads, and POSIX directory APIs. Integrates with AFR/EC heal machinery through watchlist defaults (`trusted.afr.dirty`, `trusted.ec.dirty`, `trusted.afr.{{ volume.name }}`) and xattrs such as `GF_XATTROP_INDEX_GFID`, `GF_XATTROP_DIRTY_GFID`, `GF_XATTROP_ENTRY_CHANGES_GFID`, and entry in/out keys.

## Risks and Edge Cases
Hard-link count semantics are filesystem dependent and can hit `EMLINK`, forcing index UUID rotation. Stale base files are removed during readdir only when link count is one. Worker-thread drain is important on graph teardown; `notify()` waits on `stub_cnt` and child cleanup. Path building relies on `PATH_MAX`, UUID strings, and basename validation; entry names containing `/` are rejected. Some asynchronous synctask calls pass stack-allocated args and rely on completion timing. Watchlist matching uses prefix-style matching that should be validated for unintended overlaps.

## Test Signals
Tests should cover xattrop add/remove transitions for dirty and pending watchlists, non-zero to zero xattr transitions, entry-change create/delete, index-base creation failures, virtual GFID getxattr/lookup/readdir/unlink/rmdir, stale base-file cleanup, pending link-count xdata on lookup/fstat, and graph teardown with queued work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/index/src/index.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/index/src/index.h -->
# sources/distributed-fs/glusterfs/xlators/features/index/src/index.h

## Purpose
Defines shared enums, private structs, local state, and cleanup macros for the index translator.

## Important APIs, Types, and Functions
- `index_state_t` tracks whether an inode is known in an index.
- `index_xattrop_type_t` names supported index classes: `XATTROP`, `DIRTY`, and `ENTRY_CHANGES`.
- `index_inode_ctx_t` stores queued stubs, virtual parent GFID for entry-change subdirs, state per type, and a processing flag.
- `index_fd_ctx_t` stores a `DIR *` and EOF offset for virtual readdir.
- `index_priv_t` stores base paths, internal virtual GFIDs, watchlists, worker state, pending count cache, and locks.
- `INDEX_STACK_UNWIND` centralizes unwind cleanup for `index_local_t`.

## Control Flow
The header’s structs enable `index.c` to serialize per-inode xattrop work separately from the global worker queue. The unwind macro clears `frame->local`, unwinds, unrefs the held inode/xdata, and returns local memory to the pool.

## State and Persistence
All defined structs are in-memory state. Persistent index entries are managed in `index.c` through filesystem paths stored in `index_priv_t`.

## Dependencies and Integration Points
Includes `call-stub.h` and the translator memory types. Uses GlusterFS list heads, GFID/uuid types, fd/inode types, pthread primitives, dicts, and atomics indirectly through included headers.

## Risks and Edge Cases
`state[XATTROP_TYPE_END]` depends on enum values staying dense and non-negative except `XATTROP_TYPE_UNSET`. `INDEX_STACK_UNWIND` assumes `frame->local` is an `index_local_t` and would be unsafe on unrelated frames.

## Test Signals
Compile coverage should catch enum/array drift. Runtime tests that queue multiple xattrop operations on one inode should verify `processing` and local cleanup are correct.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/index/src/index.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/leases/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/leases/Makefile.am

## Purpose
Top-level Automake file for the leases feature translator.

## Important APIs, Types, and Functions
No C APIs are defined. `SUBDIRS = src` delegates to the source build file.

## Control Flow
Automake descends into `src`.

## State and Persistence
No runtime state. `CLEANFILES` is empty.

## Dependencies and Integration Points
Part of the GlusterFS recursive build.

## Risks and Edge Cases
Removing `src` from `SUBDIRS` would omit the leases translator from builds.

## Test Signals
Server build should visit this directory and build `leases.la` through the child Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/leases/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/leases/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/leases/src/Makefile.am

## Purpose
Builds the server-side `leases.la` feature translator module.

## Important APIs, Types, and Functions
Compiles `leases.c` and `leases-internal.c`, lists private headers, links to `libglusterfs.la`, and adds libglusterfs, XDR/RPC, and timer-wheel include paths.

## Control Flow
The module is built when `WITH_SERVER` is enabled and installed into the feature xlator directory.

## State and Persistence
No runtime state; only build declarations.

## Dependencies and Integration Points
Timer-wheel include path is required because the leases implementation uses GlusterFS timer wheel APIs for recall expiry.

## Risks and Edge Cases
If a new leases source file is added but not listed, it will not be compiled. Missing timer-wheel include support breaks recall timer compilation.

## Test Signals
Build should produce `leases.la` and compile both public fop wrappers and internal lease logic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/leases/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/leases/src/leases-internal.c -->
# sources/distributed-fs/glusterfs/xlators/features/leases/src/leases-internal.c

## Purpose
Contains the internal lease-management engine for the leases translator: per-inode lease state, per-client cleanup lists, conflict detection, recall upcalls, timer expiry, blocked fop replay, and disconnect cleanup.

## Important APIs, Types, and Functions
- `is_leases_enabled()` and `get_recall_lease_timeout()` read translator private options.
- `lease_ctx_get()` creates/fetches a `lease_inode_ctx_t` in inode ctx.
- `process_lease_req()` handles `GF_GET_LEASE`, `GF_SET_LEASE`, and `GF_UNLK_LEASE`.
- `check_lease_conflict()` decides whether an fop winds, blocks, or fails with `EAGAIN`.
- `__recall_lease()` sends `GF_UPCALL_RECALL_LEASE` notifications and arms a timer.
- `do_blocked_fops()` resumes fops queued while a conflicting lease was recalled.
- `cleanup_client_leases()` removes all leases for a disconnected client.
- `expired_recall_cleanup()` consumes recall-expiry work and forcefully removes stale leases.

## Control Flow
A set-lease request validates the lease ID, locks the inode lease ctx, checks open fd and existing lease compatibility, and either records the lease or sends recall notifications and rejects the request. A normal data or metadata fop calls `check_lease_conflict()` with flags indicating write/blocking behavior; conflicts trigger recall. Blocking fops are queued in the inode ctx, while nonblocking fops fail with `EAGAIN`.

Unlock removes counts from both the lease-id entry and aggregate inode state. When the last lease disappears, `blocked_fops_resuming` is set and blocked stubs are resumed outside the lease lock. If clients do not unlock after recall, the timer handler adds the inode to `priv->recall_list`; the cleanup thread later removes all leases on that inode and resumes blocked fops.

## State and Persistence
All lease state is in memory: inode ctx contains lease-id entries, aggregate lease counts, blocked stubs, timer pointer, and recall flags; private state contains client cleanup and recall lists plus timer wheel/thread synchronization. There is no on-disk lease persistence. Client disconnect cleanup relies on the client-to-inode list populated when the first lease for a client is added.

## Dependencies and Integration Points
Depends on GlusterFS upcall utilities, timer wheel, inode/fd ctx, call stubs, list APIs, pthread synchronization, and client UID/lease ID helpers. It integrates with the rest of the translator through `process_lease_req()`, `check_lease_conflict()`, and `cleanup_client_leases()`.

## Risks and Edge Cases
Lock ordering is documented at the top and must be preserved to avoid deadlock. `__is_same_lease_id()` uses `strlen(k1)` on lease IDs that are copied as fixed-size byte arrays, so callers rely on valid string-like lease IDs. Client cleanup list removal has a TODO to remove empty client entries. Timer callbacks free the timer but timer data allocation/freeing is delicate. Open fd conflict checking fails closed if fd ctx is missing. Forceful recall cleanup intentionally revokes leases after timeout, which can surprise slow clients.

## Test Signals
Cover RD/RW lease compatibility, same lease ID reentrancy, open-fd conflicts, blocking and nonblocking fop behavior, recall upcall emission, timer-expiry forced cleanup, client disconnect cleanup, and concurrent unlock while blocked fops are queued.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/leases/src/leases-internal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/leases/src/leases-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/features/leases/src/leases-mem-types.h

## Purpose
Defines leases translator memory accounting IDs.

## Important APIs, Types, and Functions
`enum gf_leases_mem_types_` covers private state, client records, inode records, fd ctx, inode ctx, lease ID entries, blocked fop stubs, timer data, and an end sentinel.

## Control Flow
No control flow. Used by allocation sites and `xlator_mem_acct_init()`.

## State and Persistence
No runtime state; values label allocations.

## Dependencies and Integration Points
Includes GlusterFS common memory type definitions.

## Risks and Edge Cases
New leases allocations should add enum IDs to keep memory diagnostics useful. Values must remain beyond `gf_common_mt_end`.

## Test Signals
Build and memory-accounting reports should include leases allocation classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/leases/src/leases-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/leases/src/leases-messages.h -->
# sources/distributed-fs/glusterfs/xlators/features/leases/src/leases-messages.h

## Purpose
Declares stable structured log IDs for the leases translator.

## Important APIs, Types, and Functions
`GLFS_MSGID(LEASES, ...)` declares IDs for allocation failure, recall failure, invalid lease IDs/unlocks/types, invalid inode/fd ctx, disabled translator, missing timer wheel, and cleanup lookup failures.

## Control Flow
No runtime flow; `leases.c` and `leases-internal.c` reference these IDs in `gf_msg()` calls.

## State and Persistence
No runtime state. IDs are intended to be append-only.

## Dependencies and Integration Points
Includes `<glusterfs/glfs-message-id.h>` and integrates with GlusterFS logging.

## Risks and Edge Cases
Removing/reordering IDs can break log consumers. New log sites should append IDs instead of reusing unrelated ones.

## Test Signals
Compile verifies referenced message IDs exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/leases/src/leases-messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/leases/src/leases.c -->
# sources/distributed-fs/glusterfs/xlators/features/leases/src/leases.c

## Purpose
Implements the public fop surface and lifecycle for the leases translator. It intercepts lease requests and selected file/data/metadata operations, checks them against active leases, blocks or fails conflicting operations, and forwards allowed operations to the child translator.

## Important APIs, Types, and Functions
- `leases_lease()` is the fop for explicit lease get/set/unlock requests and delegates to `process_lease_req()`.
- `leases_open()`, `leases_readv()`, `leases_writev()`, `leases_lk()`, `leases_truncate()`, `leases_setattr()`, `leases_rename()`, `leases_unlink()`, `leases_link()`, `leases_create()`, `leases_fsync()`, `leases_ftruncate()`, `leases_fsetattr()`, `leases_fallocate()`, `leases_discard()`, `leases_zerofill()`, and `leases_flush()` wrap normal fops with lease conflict checks.
- `leases_init_priv()`, `init()`, `reconfigure()`, and `fini()` manage options, timer wheel, recall thread, and private state.
- `leases_release()` frees fd ctx; `leases_clnt_disconnect_cbk()` triggers client cleanup.

## Control Flow
Most fop wrappers follow the same pattern: skip checks when leases are disabled or the operation is internal, extract `"lease-id"` from xdata, compute data-modifying and blocking flags, call `check_lease_conflict()`, then either unwind error, queue a stub with `LEASE_BLOCK_FOP`, or wind the fop to the child. `leases_open()` also creates fd ctx containing client UID and lease ID so later conflict checks can distinguish same-lease opens. `leases_flush()` clears fd ctx as a workaround for release not always arriving after close.

`init()` reads `leases` and `lease-lock-recall-timeout`, initializes lists and mutexes, and starts timer support only when enabled. `reconfigure()` currently only updates recall timeout; enabling/disabling leases dynamically is explicitly not supported. `fini()` stops the recall cleanup thread and releases the timer wheel reference.

## State and Persistence
The file owns translator-private runtime setup and fd ctx lifetime. Lease state itself remains in memory through helpers in `leases-internal.c`; no persistent disk data is written.

## Dependencies and Integration Points
Depends on `leases.h` macros for flag calculation, internal fop bypass, and blocking-stub creation. Integrates with GlusterFS xlator fops/cbks, timer wheel context, client disconnect callbacks, and volume options introduced in op-version 3.8.0.

## Risks and Edge Cases
The wrappers are repetitive, so drift in one fop’s flag calculation can change semantics. `leases_create()` checks `fd->inode`, which may be sensitive during create setup. `leases_flush()` unwinds with the `create` signature on error, likely a bug. Dynamic disable is not supported, so operators changing options must understand existing leases are not recalled. `pthread_cond_broadcast()` is used in `fini()` without an explicit cond init in this file.

## Test Signals
Run lease-enabled and lease-disabled fop tests, conflict tests for all wrapped data-modifying fops, blocking vs nonblocking behavior, lease request get/set/unlock responses, fd ctx setup/release/flush cleanup, client disconnect cleanup, and reconfigure of recall timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/leases/src/leases.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/leases/src/leases.h -->
# sources/distributed-fs/glusterfs/xlators/features/leases/src/leases.h

## Purpose
Defines macros, private structs, lease state structs, and internal function declarations for the leases translator.

## Important APIs, Types, and Functions
- `EXIT_IF_LEASES_OFF`, `EXIT_IF_INTERNAL_FOP`, `GET_LEASE_ID`, `GET_FLAGS`, and `GET_FLAGS_LK` implement common fop wrapper policy.
- `LEASE_BLOCK_FOP` creates a call stub and records it in the inode lease ctx blocked list.
- `leases_private_t` stores client/recall lists, timer wheel, recall thread, locks, timeout, and enabled/fini flags.
- `lease_inode_ctx_t` stores all active lease entries, aggregate lease counts, blocked fops, timer state, and recall flags for one inode.
- `lease_id_entry_t`, `lease_client_t`, `lease_inode_t`, `lease_fd_ctx_t`, and `fop_stub_t` model client, inode, fd, and blocked operation state.
- Declares `is_leases_enabled()`, `lease_ctx_get()`, `process_lease_req()`, `check_lease_conflict()`, `cleanup_client_leases()`, and `expired_recall_cleanup()`.

## Control Flow
Fop wrappers in `leases.c` use the macros to decide whether to bypass, conflict-check, or block. Internal code in `leases-internal.c` fills and drains the structs declared here.

## State and Persistence
All declared state is memory-resident and scoped to translator, inode, client, fd, or timer lifetime. No persistent lease state is modeled.

## Dependencies and Integration Points
Includes GlusterFS call stubs, logging, locking, timer wheel, and leases-specific mem/message headers. Uses GlusterFS lease constants such as `LEASE_ID_SIZE` and `GF_LEASE_MAX_TYPE`.

## Risks and Edge Cases
`LEASE_BLOCK_FOP` has complex allocation and locking behavior embedded in a macro, so caller `ret`/`err` labels must be compatible. `GET_FLAGS_LK` appears to set `BLOCKING_FOP` when nonblocking flags are present for blocking lock commands, which deserves validation. Struct lock ownership and list membership are subtle and must match the documented lock order in the C file.

## Test Signals
Compile all fop wrappers that use `LEASE_BLOCK_FOP`, run conflict tests for flag classification, and use sanitizer or stress tests for blocked-list and timer lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/leases/src/leases.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/locks/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/locks/Makefile.am

## Purpose
Top-level Automake file for the locks feature translator.

## Important APIs, Types, and Functions
No C APIs are defined. `SUBDIRS = src` delegates build work to the source directory.

## Control Flow
Automake descends into `src`.

## State and Persistence
No runtime state. `CLEANFILES` is empty.

## Dependencies and Integration Points
Part of the GlusterFS recursive build.

## Risks and Edge Cases
If `src` is omitted, the locks translator and clear-lock helper would not build.

## Test Signals
Server builds should enter the source directory and build `locks.la`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/locks/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/locks/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/locks/src/Makefile.am

## Purpose
Builds the server-side locks/posix-locks translator module.

## Important APIs, Types, and Functions
Compiles `common.c`, `posix.c`, `entrylk.c`, `inodelk.c`, `reservelk.c`, and `clear.c`; lists private headers; links with `libglusterfs.la`; and installs a `posix-locks.so` symlink to `locks.so`.

## Control Flow
`locks.la` is built only when `WITH_SERVER` is enabled. Install/uninstall hooks manage the compatibility symlink.

## State and Persistence
No runtime state. Build artifacts include the translator shared object and symlink.

## Dependencies and Integration Points
Includes libglusterfs and RPC/XDR headers, and uses `-fno-strict-aliasing`, likely because the locks code uses alias-heavy internal structs.

## Risks and Edge Cases
Symlink install hooks must remain in sync with module naming. Adding/removing locks sources requires updating `locks_la_SOURCES`.

## Test Signals
Build/install tests should verify both `locks.so` and `posix-locks.so` are available for server deployments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/locks/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/locks/src/clear.c -->
# sources/distributed-fs/glusterfs/xlators/features/locks/src/clear.c

## Purpose
Implements administrative clear-lock helpers for the locks translator. It parses clear/interrupted-lock xattr commands and removes matching POSIX byte-range locks, inode locks, or entry locks from granted and/or blocked lists.

## Important APIs, Types, and Functions
- `clrlk_get_kind()` and `clrlk_get_type()` parse textual lock kind/type values.
- `clrlk_get_lock_range()` parses optional byte-range filters into `struct gf_flock`.
- `clrlk_parse_args()` parses command xattr names of the form clear/interrupted prefix plus `.t<type>.k<kind>` and optional type-specific args.
- `clrlk_clear_posixlk()` removes matching POSIX locks and unwinds blocked locks with `EINTR`.
- `clrlk_clear_inodelk()` removes matching blocked/granted inode locks and may emit contention notifications.
- `clrlk_clear_entrylk()` removes matching blocked/granted entry locks by optional basename.
- `clrlk_clear_lks_in_all_domains()` applies inode or entry clear operations across all domains on an inode.

## Control Flow
The parser first strips either the clear-lock or interrupted-lock xattr prefix, then expects ordered keyword tokens for type and kind. POSIX clearing optionally filters by byte range and, for interrupted setlk, by client UID and pid. It removes locks while holding the inode lock, moves blocked locks to local lists, then unwinds blocked frames outside the mutex. Inode and entry clearing follow the same pattern: remove from blocked lists, unwind blocked waiters, optionally remove granted locks, then call grant/notify helpers so newly unblocked locks can proceed.

## State and Persistence
The helpers mutate in-memory lock lists stored under `pl_inode_t` and domain structs. They do not persist state directly; their effects are immediate lock table changes and blocked fop unwinds.

## Dependencies and Integration Points
Depends on `locks.h`, `common.h`, lock-specific ref/unref helpers, grant helpers (`grant_blocked_locks`, `grant_blocked_inode_locks`, `grant_blocked_entry_locks`), trace/unwind helpers, and contention notification functions. Invoked by higher-level locks translator xattr handling.

## Risks and Edge Cases
The public header declares `clrlk_get__kind` with a double underscore while the implementation defines `clrlk_get_kind`, indicating a prototype mismatch risk. `clrlk_parse_args()` allocates `strlen(cmd)` bytes then scans a string into it; exact-size allocation leaves no explicit extra byte for NUL if the scanned suffix length equals `strlen(cmd)`. Removing granted entry locks unrefs inside the mutex after list removal, so ref semantics must be correct. Optional range/basename syntax cannot include `/`, by design.

## Test Signals
Test command parsing for valid/invalid type/kind, POSIX range filters, basename filters, blocked-only/granted-only/all modes, interrupted lock filtering by client/pid, and post-clear granting of waiting locks. Compile should catch the header typo if callers use the declared name.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/locks/src/clear.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/locks/src/clear.h -->
# sources/distributed-fs/glusterfs/xlators/features/locks/src/clear.h

## Purpose
Declares clear-lock argument types and clear helper APIs for the locks translator.

## Important APIs, Types, and Functions
- `clrlk_type` enumerates inode, entry, and POSIX lock clearing.
- `clrlk_kind` selects blocked, granted, or all locks.
- `clrlk_args` carries parsed type, kind, and optional type-specific string.
- Declares parser helpers and clear functions for POSIX, inode, entry, and all-domain lock cleanup.

## Control Flow
This header is consumed by lock xattr handling code and implemented by `clear.c`. Callers parse a command into `clrlk_args`, then dispatch to a type-specific clear function.

## State and Persistence
No state is stored here. The declared functions mutate in-memory lock tables owned by the locks translator.

## Dependencies and Integration Points
Includes GlusterFS errno compatibility and `locks.h`, so it depends on lock structs such as `pl_inode_t`, `pl_dom_list_t`, and GlusterFS lock/fop types.

## Risks and Edge Cases
The declaration `clrlk_get__kind` does not match the implementation name `clrlk_get_kind`, which can cause missing-prototype or linker issues for external callers. The `kind` enum uses bit-like values for blocked and granted, and `CLRLK_ALL` is `3`, so code relies on bitwise checks.

## Test Signals
Build all callers with warnings enabled, especially any direct calls to `clrlk_get_kind`. Runtime tests should dispatch each enum combination to the appropriate clear routine.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/locks/src/clear.h -->
