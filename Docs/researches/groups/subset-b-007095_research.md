# subset-b-007095 Research

Grouped source research for GlusterFS feature translators in `marker`, `metadisp`, `namespace`, `quiesce`, and the quota build entry points. Each section is bounded by reconciliation markers and preserves the exact source path in its title.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/marker/src/marker.c -->
# sources/distributed-fs/glusterfs/xlators/features/marker/src/marker.c

## Purpose

`marker.c` implements the GlusterFS marker translator. It sits above one child translator and augments successful filesystem operations with quota accounting metadata and geo-replication xtime markers. It is responsible for maintaining quota xattrs, converting public quota keys to versioned internal keys, filtering internal marker xattrs from ordinary clients and healers, exposing the volume mark timestamp to geo-replication, and driving background or foreground quota transactions after namespace and file-size changes.

## Important APIs, Types, and Functions

The public translator entry points are the `fops` table: `marker_lookup`, `marker_create`, `marker_mkdir`, `marker_writev`, `marker_truncate`, `marker_ftruncate`, `marker_symlink`, `marker_link`, `marker_unlink`, `marker_rmdir`, `marker_rename`, `marker_mknod`, `marker_setxattr`, `marker_fsetxattr`, `marker_setattr`, `marker_fsetattr`, `marker_removexattr`, `marker_getxattr`, `marker_readdirp`, `marker_fallocate`, `marker_discard`, and `marker_zerofill`. Lifecycle hooks are `init`, `reconfigure`, `fini`, `mem_acct_init`, and inode cleanup through `marker_forget`.

Key helpers include `marker_key_replace_with_ver` and `marker_key_set_ver` for quota xattr version mapping, `marker_filter_internal_xattrs` and `marker_filter_gsyncd_xattrs` for response filtering, `marker_xtime_update_marks` and `marker_start_setxattr` for recursive xtime stamping, `marker_do_xattr_cleanup` and `quota_xattr_cleaner` for privileged quota cleanup, and the multi-step rename helpers `marker_get_oldpath_contribution`, `marker_do_rename`, `marker_rename_cbk`, `marker_rename_unwind`, and `marker_rename_done`.

## Control Flow

Most fops follow the same pattern: if marker features are disabled they wind straight to `FIRST_CHILD(this)`; otherwise they allocate `marker_local_t`, copy the relevant `loc_t` or synthesize one from an fd inode, wind the child fop, unwind to the caller in the callback, and only then run quota or xtime side effects. Create-like operations allocate quota inode context and create quota xattrs. Write/truncate/fallocate/discard/zerofill call `mq_initiate_quota_txn` with post-operation stat data. Link and create add contribution xattrs, while unlink and rmdir often run `mq_reduce_parent_size_txn` in the foreground using a callback stub so the caller is not unwound before accounting completes.

Rename is the most complex path. With quota enabled it allocates locals for old and new paths, takes an inode lock on the old parent using a separate root-uid frame, reads the old contribution xattr, performs the rename, removes the old-parent contribution xattr from the renamed inode, unwinds the original rename, releases the old-parent lock, subtracts old and overwritten-destination contributions, and finally creates a new contribution under the destination parent. The in-file comment explicitly documents this ordering to avoid stale parent contribution updates while inode parentage changes.

Xtime flow is asynchronous. After a successful mutation, `marker_xtime_update_marks` skips defrag and ordinary gsyncd calls unless `gsync-force-xtime` is enabled, records current seconds/useconds in network order, refs the local, creates a new frame, sets the marker xattr on the current location, and recursively traverses parent locations until root.

## State and Persistence Behavior

Persistent state is stored as extended attributes under `trusted.glusterfs`, including quota size/limit keys and per-volume xtime keys of the form `trusted.glusterfs.<volume-uuid>.xtime`. The volume mark exposed to geo-replication is derived from the configured `timestamp-file` mtime. `call_from_sp_client_to_reset_tmfile` lets the gsyncd client reset that timestamp by setting `trusted.glusterfs.volume-mark` to empty or `RESET`.

In-memory state includes `marker_conf_t` in `this->private`, the `marker_local_t` pool for inflight fops and nested marker frames, and inode context that stores quota state. `marker_local_unref` owns cleanup of copied locs, held xdata, nested lock frames, and chained operation locals. Quota versioning is controlled by the `quota-version` option; positive versions rewrite external xattr names to versioned internal keys before winding requests and rewrite them back on callback.

## Dependencies and Integration Points

This file integrates tightly with `marker-quota.h`, `marker-quota-helper.h`, `marker-common.h`, `libxlator.h`, syncop helpers, Gluster dict/xattr APIs, call stubs, inode contexts, frame ownership, and default unwind/wind infrastructure. It depends on child translators supporting ordinary fops, `getxattr`/`setxattr`/`removexattr`, `inodelk`, `readdirp`, and syncop list/remove xattr calls. Geo-replication is identified by `GF_CLIENT_PID_GSYNCD`; quota and heal integration use request/response xdata such as link-count keys and internal quota patterns.

## Risks and Edge Cases

The main risks are ordering and ownership bugs around asynchronous side effects. Rename relies on precise lock, xattr-removal, inode-table unwind, and contribution-update ordering. Several paths unwind to the caller before background quota or xtime work, so failures can leave delayed repair needs. `marker_error_handler` treats ENOSPC during marker xattr propagation as indexing corruption and removes the timestamp file, forcing geo-replication revalidation. Root, gsyncd, defrag, DHT linkfile, hardlink, and `GLUSTERFS_MARKER_DONT_ACCOUNT_KEY` cases all alter accounting behavior. Dictionary ownership is also sensitive because requests may be copied, refed, rewritten, or newly allocated.

## Test Signals

Useful tests include translator initialization/reconfigure with quota, inode-quota, xtime, gsync-force-xtime, bad UUID, and quota-version values; create/mkdir/mknod/symlink/link/write/truncate/unlink/rmdir/rename accounting with xattr inspection; rename under concurrent writes and existing destination files; gsyncd volume-mark get/set behavior; non-gsyncd filtering of xtime and internal quota xattrs; quota cleanup command permission checks; ENOSPC and missing-parent fault injection; and readdirp/lookup paths that create inode quota contexts and request versioned xattrs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/marker/src/marker.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/marker/src/marker.h -->
# sources/distributed-fs/glusterfs/xlators/features/marker/src/marker.h

## Purpose

`marker.h` defines the private data structures, flags, xattr names, and local-frame helper macros used by the marker translator.

## Important APIs, Types, and Functions

Important constants are `MARKER_XATTR_PREFIX`, `XTIME`, `VOLUME_MARK`, `VOLUME_UUID`, and `TIMESTAMP_FILE`. Feature bits are `GF_QUOTA`, `GF_XTIME`, `GF_XTIME_GSYNC_FORCE`, and `GF_INODE_QUOTA`. The local-management macros `MARKER_INIT_LOCAL`, `ALLOCATE_OR_GOTO`, `MARKER_SET_UID_GID`, `MARKER_RESET_UID_GID`, and `MARKER_STACK_UNWIND` standardize frame-local initialization, root credential override for privileged xattr operations, and local unref after unwinding.

`marker_local_t` stores per-call path state, uid/gid, locks, callback stubs, quota contribution data, file offsets and sizes, fd/frame pointers, quota inode/contribution context, xdata, and flags. `marker_inode_ctx_t` links marker inode context to quota context. `marker_conf_t` stores enabled features, key strings, volume UUID, timestamp file, marker xattr name, quota lock owner, lock, and quota version.

## Control Flow

The header has no runtime control flow, but its macros are embedded throughout `marker.c`. `MARKER_STACK_UNWIND` is especially important because it detaches `frame->local`, unwinds the caller, then releases marker local state.

## State and Persistence Behavior

The structs describe in-memory state only. Persistent marker state lives in xattrs and timestamp files managed by `marker.c`, with these fields holding the configured names and temporary values used to write them.

## Dependencies and Integration Points

The header includes `marker-quota.h` and Gluster UUID compatibility support, and it aliases `quota_local_t` to `marker_local_t` so quota helper code can operate on marker locals. It assumes Gluster frame, loc, dict, inode, iatt, lock, fd, and quota types are available through the included marker/quota headers.

## Risks and Edge Cases

Changing `marker_local_t` fields can break quota helpers that rely on the alias. The uid/gid macros intentionally switch request credentials to root for internal xattr operations; missing the reset path risks leaking privileged credentials on a frame. `MARKER_INIT_LOCAL` requires valid frame roots and must be used before fields such as the lock or refcount are consumed.

## Test Signals

Compile tests should catch struct and macro drift. Runtime tests should exercise all macro paths: normal unwind with local release, privileged xattr get/remove during rename, nested `oplocal` release, and local cleanup when errors occur before child winding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/marker/src/marker.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/metadisp/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/metadisp/Makefile.am

## Purpose

This top-level Automake fragment makes `metadisp/src` the build subdirectory for the metadisp feature translator.

## Important APIs, Types, and Functions

The only build variables are `SUBDIRS = src` and empty `CLEANFILES`.

## Control Flow

Automake descends into `src` during build, install, clean, and distribution phases.

## State and Persistence Behavior

No runtime state or persistent data is defined here.

## Dependencies and Integration Points

It depends on the parent GlusterFS build system discovering feature translator subdirectories. All actual library, generated-source, include, and clean rules are delegated to `src/Makefile.am`.

## Risks and Edge Cases

If `src` is omitted or renamed, the metadisp translator is not built even though the source remains present. The empty `CLEANFILES` means generated artifacts must be cleaned in the nested makefile.

## Test Signals

Autotools configuration and `make` should recurse into this directory and build `metadisp.la` through the nested makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/metadisp/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/metadisp/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/metadisp/src/Makefile.am

## Purpose

This Automake file builds the `metadisp.la` xlator module and generates `fops.c` from `fops-tmpl.c` plus `gen-fops.py`.

## Important APIs, Types, and Functions

Key build variables are `xlator_LTLIBRARIES = metadisp.la`, `xlatordir`, `nodist_metadisp_la_SOURCES = fops.c`, `BUILT_SOURCES = fops.c`, `metadisp_la_SOURCES`, `metadisp_la_LIBADD`, `noinst_HEADERS`, `AM_CPPFLAGS`, and `AM_CFLAGS`. The generation rule runs `$(PYTHON) $(srcdir)/gen-fops.py $(srcdir)/fops-tmpl.c > $@` with `PYTHONPATH` pointed at libglusterfs generator helpers.

## Control Flow

Build flow first generates `fops.c`, then compiles it together with the hand-written metadisp fop files and links the translator module against `libglusterfs.la`.

## State and Persistence Behavior

`fops.c` is generated build state, listed in `CLEANFILES` through `$(nodist_metadisp_la_SOURCES)`. It is not distributed as source.

## Dependencies and Integration Points

The file integrates with GlusterFS xlator install layout under `$(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/features`, libglusterfs headers, XDR headers, and the shared Python generator in `libglusterfs/src/generator.py`.

## Risks and Edge Cases

Generated and hand-written fop coverage must stay synchronized. Missing `generator.py`, a Python interpreter mismatch, or a broken `#pragma generate` template prevents the xlator from compiling. Because `fops.c` is nodist, source tarball consumers must be able to regenerate it.

## Test Signals

Run the autotools build from a clean tree, verify `fops.c` is generated, compile `metadisp.la`, run `make clean` to ensure generated files are removed, and check that installed xlator path matches other feature translators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/metadisp/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/metadisp/src/backend.c -->
# sources/distributed-fs/glusterfs/xlators/features/metadisp/src/backend.c

## Purpose

`backend.c` contains the metadisp helper for translating a user-visible location into the data-backend namespace. Metadisp stores metadata in one child and file data in another; the data child addresses file data by GFID-style paths.

## Important APIs, Types, and Functions

The single exported function is `build_backend_loc(uuid_t gfid, loc_t *src_loc, loc_t *dst_loc)`. It validates source and destination locs, copies the source loc, overwrites parent GFID with root, builds a `/<gfid>` path string using `uuid_utoa_r`, and updates `path` and `name` in the destination loc.

## Control Flow

The helper copies `src_loc`, frees the copied path because it is replaced, formats the supplied GFID into a newly allocated path, assigns `dst_loc->path`, and derives `dst_loc->name` from the final slash when the source had a name. Validation failure returns `-1`.

## State and Persistence Behavior

The function allocates path memory with `GF_CALLOC`; ownership is transferred to `dst_loc` and expected to be released by `loc_wipe`. It does not persist data beyond the loc structure.

## Dependencies and Integration Points

It depends on `metadisp.h`, Gluster loc helpers, UUID formatting, GFID buffer size constants, and common memory types. It is used by data-child fops such as lookup, open, stat, setattr, create, unlink, and generated dataloc operations.

## Risks and Edge Cases

Allocation failure is not explicitly checked after `GF_CALLOC`, so a null path could be dereferenced. The function assumes the supplied GFID is valid; callers must reject null GFIDs where necessary. Any loc copied into `dst_loc` must be wiped by the caller to avoid leaking references and path memory.

## Test Signals

Tests should verify root parent GFID replacement, expected `/<uuid>` path construction, name extraction, loc cleanup with `loc_wipe`, invalid input handling, and callers' behavior with null or missing GFIDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/metadisp/src/backend.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/metadisp/src/fops-tmpl.c -->
# sources/distributed-fs/glusterfs/xlators/features/metadisp/src/fops-tmpl.c

## Purpose

`fops-tmpl.c` is the template input for generating metadisp's default fop wrappers and fop table.

## Important APIs, Types, and Functions

The file includes `config.h`, `metadisp.h`, and `metadisp-fops.h`, then contains `#pragma generate`, which `gen-fops.py` replaces with generated C.

## Control Flow

There is no standalone runtime flow in the template. During build, lines are copied until the pragma, then generated fop functions and the `struct xlator_fops fops` table are emitted.

## State and Persistence Behavior

No runtime state is owned here. The persistent build artifact is generated `fops.c`.

## Dependencies and Integration Points

The template depends on `gen-fops.py` and libglusterfs's Python generator substitution tables. It also depends on hand-written declarations in `metadisp-fops.h` for fops excluded from generation.

## Risks and Edge Cases

The pragma is a single build-generation anchor. Removing or misspelling it yields a `fops.c` without generated wrappers. Include-order changes can break generated code that relies on metadisp macros and prototypes.

## Test Signals

A clean build should produce `fops.c` containing generated code between the begin/end comments and a complete `fops` table. Compile warnings in generated fops are a strong signal of template or generator drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/metadisp/src/fops-tmpl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/metadisp/src/gen-fops.py -->
# sources/distributed-fs/glusterfs/xlators/features/metadisp/src/gen-fops.py

## Purpose

`gen-fops.py` generates metadisp default fop implementations from libglusterfs fop metadata, routing each operation to either metadata child, data child, or a GFID-rewritten data loc.

## Important APIs, Types, and Functions

The script imports `fop_subs` and `generate` from `generator.py`. Template strings are `FN_METADATA_CHILD_GENERIC`, `FN_GENERIC_TEMPLATE`, `FN_DATAFD_TEMPLATE`, `FN_DATALOC_TEMPLATE`, and `FOPS_LINE_TEMPLATE`. The main function `gen_fops()` emits generated C and the `fops` table. The `skipped` list reserves special fops implemented manually: readdir, readdirp, lookup, fsync, stat, open, create, unlink, setattr, and inodelk as a TODO.

## Control Flow

For each input template line, the script detects `#pragma generate`. At that point it prints a generated-code comment, calls `gen_fops`, and prints an end comment; all other template lines are copied through. Within `gen_fops`, fd-based data operations such as writev/readv/ftruncate/zerofill/discard/seek/fstat are emitted to `DATA_CHILD`, truncate is emitted through `build_backend_loc`, and dentry/metadata/xattr operations such as mkdir/link/rename/opendir/readlink/access and xattr fops are emitted to `METADATA_CHILD`.

## State and Persistence Behavior

The script has no persisted state except stdout, which the makefile redirects to `fops.c`. The `done` list controls which generated table entries appear and must include both skipped manual fops and generated fops.

## Dependencies and Integration Points

It relies on Python execution in the build environment and libglusterfs generator metadata for fop argument substitutions. The generated C depends on metadisp child macros, default callbacks, and `build_backend_loc`.

## Risks and Edge Cases

The script uses Python 2 style shebang but Python 3 compatible print calls are not used; it currently uses `print(...)`, but compatibility still depends on the configured interpreter and `generator.py`. The dataloc template's unwind path hard-codes `STACK_UNWIND_STRICT(lookup, ...)`, which is suspicious for generated non-lookup fops and could report the wrong fop signature if build generation enabled more dataloc operations. The `done = skipped` alias mutates the global skipped list if reused in-process.

## Test Signals

Regenerate `fops.c`, inspect routing for each fop class, compile with all generated prototypes, and exercise generated fd, metadata, and dataloc fops. A regression test should verify truncate error unwinds use the correct fop signature if the generator is repaired.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/metadisp/src/gen-fops.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp-create.c -->
# sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp-create.c

## Purpose

`metadisp-create.c` implements split create semantics: create metadata first, then create the backend data inode addressed by requested GFID.

## Important APIs, Types, and Functions

Functions are `metadisp_create`, `metadisp_create_cbk`, `metadisp_create_resume`, and `metadisp_create_dentry_cbk`. It uses `RESOLVE_GFID_REQ` to fetch `gfid-req`, `build_backend_loc` to create the data child loc, and `fop_create_stub` to defer the data create until metadata create succeeds.

## Control Flow

`metadisp_create` resolves the requested GFID from xdata, builds `backend_loc`, stores a create resume stub, and winds `create` to `METADATA_CHILD`. The metadata callback unwinds on error, destroys poisoned stubs, or resumes the stub. The resume function winds the backend create to `DATA_CHILD`, and the final dentry callback unwinds the original create result.

## State and Persistence Behavior

Metadata and data are persisted in separate children. Temporary state is a call stub containing the backend loc and create arguments. `frame->local = loc` is assigned but not used meaningfully in this file.

## Dependencies and Integration Points

The file depends on Gluster call stubs, xdata `gfid-req`, metadata/data child ordering, and `build_backend_loc`. It assumes metadata child enforces ACLs before data child creation.

## Risks and Edge Cases

If backend creation fails after metadata creation succeeds, the code unwinds the failure but does not roll back the metadata inode. Missing `gfid-req` or backend loc construction failure returns `EINVAL`. Stub poisoning is handled, but backend loc lifetime depends on the stub copying loc data safely.

## Test Signals

Tests should cover create success in both children, metadata ACL denial preventing data creation, missing `gfid-req`, data-child failure after metadata success, and orphan metadata recovery or healing expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp-create.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp-fops.h -->
# sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp-fops.h

## Purpose

`metadisp-fops.h` declares the hand-written metadisp fops that are not generated into `fops.c`.

## Important APIs, Types, and Functions

Declared fops are `metadisp_readdir`, `metadisp_readdirp`, `metadisp_lookup`, `metadisp_create`, `metadisp_open`, `metadisp_stat`, `metadisp_inodelk`, `metadisp_fsync`, `metadisp_unlink`, and `metadisp_setattr`.

## Control Flow

The header has no control flow. It supplies prototypes used by `fops-tmpl.c` and generated `fops.c` so special-case implementations can be referenced in the final fop table.

## State and Persistence Behavior

No state is stored here.

## Dependencies and Integration Points

It includes Gluster dict and core headers plus `sys/types.h`. It is coupled to `gen-fops.py`'s skipped list: every skipped fop should have a matching declaration and implementation.

## Risks and Edge Cases

The header declares `metadisp_inodelk`, but the generator still has inodelk as a TODO and no corresponding implementation appears in this work item, which risks unresolved symbols if the fop table references it or incomplete lock routing if it does not.

## Test Signals

Compile the generated fop table against this header and verify every declared special fop is either linked or intentionally absent from the table. Lock-operation tests should confirm inodelk behavior before enabling that table entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp-fops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp-fsync.c -->
# sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp-fsync.c

## Purpose

`metadisp-fsync.c` implements fsync across both metadisp children, syncing metadata first and data second.

## Important APIs, Types, and Functions

Functions are `metadisp_fsync`, `metadisp_fsync_cbk`, and `metadisp_fsync_resume`. It uses `fop_fsync_stub` and `default_fsync_cbk`.

## Control Flow

`metadisp_fsync` creates a resume stub for the data child and winds fsync to `METADATA_CHILD` with the stub as cookie. If metadata fsync fails, the callback destroys the stub and unwinds the metadata result. If it succeeds, it resumes the stub, which winds fsync to `DATA_CHILD` and unwinds through the default callback.

## State and Persistence Behavior

The only temporary state is the call stub. Persisted effects are whatever fsync guarantees each child provides for metadata and data storage.

## Dependencies and Integration Points

It depends on the child fops implementing fsync and on Gluster call-stub poisoning semantics.

## Risks and Edge Cases

If data fsync fails after metadata fsync succeeds, the final result reflects the data failure but metadata has already been flushed. A null stub is not explicitly guarded before `stub->poison` when the metadata callback succeeds and cookie is absent.

## Test Signals

Tests should inject metadata fsync failure, data fsync failure, stub allocation failure, and successful two-child fsync ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp-fsync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp-lookup.c -->
# sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp-lookup.c

## Purpose

`metadisp-lookup.c` implements two-stage lookup so regular files are verified in both metadata and data children.

## Important APIs, Types, and Functions

Functions are `metadisp_lookup`, `metadisp_lookup_cbk`, `metadisp_backend_lookup_resume`, and `metadisp_backend_lookup_cbk`.

## Control Flow

The top-level fop creates a lookup stub for the backend lookup, then winds lookup to `METADATA_CHILD`. If metadata lookup fails, the callback unwinds immediately. If metadata lookup finds a non-regular object, it also unwinds metadata result only. For regular files, it resumes the backend lookup stub. The backend resume builds a GFID path and winds lookup to `DATA_CHILD`; the backend callback maps backend `ENOENT` to `ENODATA` and unwinds the original lookup.

## State and Persistence Behavior

No long-lived state is stored. The code verifies consistency between persistent metadata and persistent data entries.

## Dependencies and Integration Points

It depends on `IA_ISREG`, `build_backend_loc`, metadata/data child separation, and default lookup unwind signatures.

## Risks and Edge Cases

Backend loc is not wiped in the resume function after winding, so lifetime depends on stack-wind or lower layers copying what they need. Metadata says regular but backend missing becomes `ENODATA`, which callers or healers must understand. The commented GFID copy in the metadata callback suggests earlier uncertainty about where GFID should be sourced.

## Test Signals

Tests should cover directory lookup, regular lookup with data present, metadata missing, data missing producing `ENODATA`, null/invalid GFID producing `EINVAL`, and consistency with stat/open flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp-lookup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp-open.c -->
# sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp-open.c

## Purpose

`metadisp-open.c` opens both the metadata object and the backend data object for a regular file.

## Important APIs, Types, and Functions

Functions are `metadisp_open`, `metadisp_open_cbk`, and `metadisp_open_resume`.

## Control Flow

`metadisp_open` builds a backend loc from `loc->gfid`, creates an open resume stub for that backend loc, and winds open to `METADATA_CHILD`. The callback resumes the stub only if metadata open succeeds; the resume function winds open to `DATA_CHILD` using the same callback with a null cookie, so the second callback unwinds the final result.

## State and Persistence Behavior

Temporary state is the call stub and backend loc. Persistent state is limited to the open state each child associates with the fd.

## Dependencies and Integration Points

It depends on `build_backend_loc`, child open fops, `fd_t` sharing across child opens, and call-stub poison handling.

## Risks and Edge Cases

If metadata open succeeds and data open fails, metadata fd state may remain open without explicit rollback. A successful callback with null cookie on the first stage would unwind without setting an error. Backend loc lifetime and cleanup are implicit through the stub.

## Test Signals

Tests should cover successful dual open, metadata denial, data child missing or denied, null GFID/backend loc failure, and fd cleanup after partial failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp-open.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp-readdir.c -->
# sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp-readdir.c

## Purpose

`metadisp-readdir.c` routes directory reads through the metadata child while requesting enough stat data for callers such as NFS.

## Important APIs, Types, and Functions

Functions are `metadisp_readdir` and `metadisp_readdirp`.

## Control Flow

Both fops ensure an xdata dict exists, set `stat-source-of-truth` to the metadisp translator pointer, and wind `readdirp` to `METADATA_CHILD`. Even plain `readdir` is converted to `readdirp` so entry types and stat fields are initialized.

## State and Persistence Behavior

No state is persisted. The xdata hint tells lower layers how to source stat information while merging metadata and data views.

## Dependencies and Integration Points

The file depends on metadata child readdirp behavior and metadisp stat handling for the `stat-source-of-truth` convention. It also relies on dict allocation and static pointer storage.

## Risks and Edge Cases

When xdata is newly allocated it is not unrefed in this function after winding, so ownership expectations must be confirmed. `dict_set_static_ptr` return is stored in an unused variable, so failure to set the hint does not alter control flow. Always issuing readdirp may be more expensive than readdir.

## Test Signals

Tests should cover NFS-style readdir requiring type data, readdirp xdata propagation, dict allocation failure behavior, and stat-source-of-truth integration with `metadisp_stat`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp-readdir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp-setattr.c -->
# sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp-setattr.c

## Purpose

`metadisp-setattr.c` applies setattr to metadata first and, for regular files, applies corresponding backend attributes to the data child.

## Important APIs, Types, and Functions

Functions are `metadisp_setattr`, `metadisp_setattr_cbk`, `metadisp_backend_setattr_resume`, and `metadisp_backend_setattr_cbk`.

## Control Flow

The top-level fop creates a backend setattr stub, winds setattr to `METADATA_CHILD`, and resumes the backend stub only when metadata setattr succeeds and the resulting type is regular. The backend resume builds a GFID path and winds setattr to `DATA_CHILD`. Backend `ENOENT` is mapped to `ENODATA`.

## State and Persistence Behavior

The persistent effect is attribute mutation in one or both children. Non-regular objects are only updated in metadata.

## Dependencies and Integration Points

It depends on `IA_ISREG`, `build_backend_loc`, child setattr support, and call stubs.

## Risks and Edge Cases

Metadata setattr can succeed while backend setattr fails, leaving divergent attributes. If `statpost` is null on a nominal success, `IA_ISREG(statpost->ia_type)` would dereference null. Backend loc cleanup is implicit.

## Test Signals

Tests should cover regular and directory setattr, backend missing mapped to `ENODATA`, metadata failure, data failure after metadata success, valid mask propagation, and null/invalid stat buffers in fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp-setattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp-stat.c -->
# sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp-stat.c

## Purpose

`metadisp-stat.c` returns authoritative stat data for split metadata/data objects and supports calls initiated by lower metadata layers that request a specific stat source.

## Important APIs, Types, and Functions

Functions are `metadisp_stat`, `metadisp_stat_cbk`, `metadisp_stat_resume`, and `metadisp_stat_backend_cbk`.

## Control Flow

`metadisp_stat` first filters root by winding directly to metadata. If xdata contains `syncop-internal-from-posix` and `stat-source-of-truth`, it treats the call as metadata-layer internal and winds to the data child using the supplied source xlator context. Otherwise it builds a backend loc, creates a stat resume stub, and winds stat to `METADATA_CHILD`. The metadata callback unwinds immediately for non-regular objects or errors, and resumes the backend stat for regular files. Backend `ENOENT` is converted to `ENODATA`, while null GFID produces `EUCLEAN`.

## State and Persistence Behavior

No internal state persists. The fop reconciles persistent stat data between metadata and data children and may signal corruption or missing data through `EUCLEAN` or `ENODATA`.

## Dependencies and Integration Points

The file integrates with `METADISP_FILTER_ROOT`, `build_backend_loc`, xdata keys `syncop-internal-from-posix` and `stat-source-of-truth`, and the readdir path that sets the stat source hint.

## Risks and Edge Cases

The code uses `STACK_UNWIND_STRICT(open, ...)` in some stat error paths, which appears inconsistent with a stat fop and is a compile/runtime risk depending on macro signatures. Missing data after metadata success requires healing behavior outside this file. Internal-from-posix handling depends on raw pointer xdata and must only be used within the process.

## Test Signals

Tests should cover root stat, directory stat, regular file stat through both children, data missing, null GFID, readdirp-triggered stat-source-of-truth, and compile/signature checks around the apparent `open` unwind typo.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp-stat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp-unlink.c -->
# sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp-unlink.c

## Purpose

`metadisp-unlink.c` removes both metadata and data objects while handling cases where the caller arrives without a GFID.

## Important APIs, Types, and Functions

Functions are `metadisp_unlink`, `metadisp_unlink_lookup_cbk`, `metadisp_unlink_cbk`, and `metadisp_unlink_resume`.

## Control Flow

If `loc->gfid` is null, `metadisp_unlink` creates a stub to retry unlink after lookup, winds lookup to `METADATA_CHILD`, and the lookup callback copies `buf->ia_gfid` into `loc->gfid` before resuming. With a GFID present, it filters root, builds a backend loc, creates a data unlink resume stub, and winds unlink to `METADATA_CHILD`. On metadata unlink success it resumes data unlink; backend `ENOENT` is treated as success to allow cleanup of metadata-only objects.

## State and Persistence Behavior

Persistent state is deleted in both children. Temporary state is held in stubs and rewritten loc GFID.

## Dependencies and Integration Points

It depends on root filtering, metadata lookup for GFID resolution, `build_backend_loc`, call stubs, and child unlink semantics.

## Risks and Edge Cases

Metadata unlink success followed by data unlink failure leaves partial deletion. The code mutates the caller's loc by copying GFID during lookup resume. The retry stub uses `metadisp_unlink` itself, so incorrect GFID resolution could loop or reuse stale state. Treating backend ENOENT as success hides missing-data conditions during unlink.

## Test Signals

Tests should cover unlink with and without initial GFID, root unlink filtering, data missing, metadata failure, data failure, and cleanup when lookup returns nonzero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp-unlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp.c -->
# sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp.c

## Purpose

`metadisp.c` provides lifecycle hooks and xlator API registration for the metadisp translator.

## Important APIs, Types, and Functions

Functions are `init`, `fini`, and `reconfigure`. The exported `xlator_api` identifies the translator as `metadisp`, marks it tech preview, and points at externally defined `fops`, empty callback and dumpop structures, lifecycle hooks, and options.

## Control Flow

`init` validates that exactly two child translators are present, logs a dangling-volume warning when there are no parents, and returns success. `fini` and `reconfigure` are no-ops that return immediately.

## State and Persistence Behavior

No private runtime state is allocated by this file. Metadisp behavior is encoded in child topology and fop routing rather than `this->private`.

## Dependencies and Integration Points

It depends on generated or linked `struct xlator_fops fops`, Gluster xlator API registration, and the convention that `FIRST_CHILD` is metadata while `SECOND_CHILD` is data.

## Risks and Edge Cases

The translator has no private config validation beyond child count. Any child ordering mistake changes semantics drastically because metadata/data roles are positional. No reconfigure support exists for runtime behavior changes.

## Test Signals

Tests should load metadisp with zero, one, two, and three children; verify child order in a volfile; and confirm the generated fop table is linked into the API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp.h -->
# sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp.h

## Purpose

`metadisp.h` defines the shared macros and helper prototype used by all metadisp source files.

## Important APIs, Types, and Functions

Macros `METADATA_CHILD(this)` and `DATA_CHILD(this)` identify child roles. `build_backend_loc` is declared for GFID path rewriting. `METADISP_TRACE` wraps `gf_log`. `METADISP_FILTER_ROOT` and `METADISP_FILTER_ROOT_BY_GFID` route root operations directly to metadata. `RESOLVE_GFID_REQ` validates extraction of `gfid-req` from a dict.

## Control Flow

The filter macros inject early-return control flow into fops. Root-path or root-GFID operations are wound to metadata with the default callback and return immediately.

## State and Persistence Behavior

No state is stored here. The macros define routing behavior based on translator child topology and request loc/GFID values.

## Dependencies and Integration Points

It includes Gluster logging and dict headers and assumes core xlator macros such as `FIRST_CHILD`, `SECOND_CHILD`, `STACK_WIND`, and `default_*_cbk` are available through included Gluster headers.

## Risks and Edge Cases

The macros reference local variables such as `frame`, `this`, and `loc`, so misuse in a different lexical context can fail compile or route incorrectly. `RESOLVE_GFID_REQ` assumes xdata is non-null and jumps to a caller-provided label on failure.

## Test Signals

Compile coverage for each macro use, root operation tests, create with missing `gfid-req`, and child ordering tests validate this header's integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/namespace/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/namespace/Makefile.am

## Purpose

This top-level Automake fragment delegates namespace translator builds to `src`.

## Important APIs, Types, and Functions

It defines `SUBDIRS = src` and empty `CLEANFILES`.

## Control Flow

The build system recurses into the `src` directory.

## State and Persistence Behavior

No runtime or persistent state is defined.

## Dependencies and Integration Points

It integrates with the parent feature translator build layout.

## Risks and Edge Cases

If this file is not included by the parent makefile or `src` is removed, `namespace.la` will not be built.

## Test Signals

Autotools build should enter this directory and compile `namespace/src/namespace.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/namespace/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/namespace/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/namespace/src/Makefile.am

## Purpose

This Automake file builds and installs the `namespace.la` feature translator.

## Important APIs, Types, and Functions

It sets `xlator_LTLIBRARIES = namespace.la`, module flags, `namespace_la_SOURCES = namespace.c`, `namespace_la_LIBADD`, `noinst_HEADERS = namespace.h`, include paths for libglusterfs, RPC XDR, and xlators lib, plus standard warning flags.

## Control Flow

Build flow compiles `namespace.c`, links it as a Gluster xlator module, and installs it under the package xlator feature directory.

## State and Persistence Behavior

No generated or persistent runtime state is defined.

## Dependencies and Integration Points

The namespace translator links only against libglusterfs and includes helper headers from `xlators/lib/src`.

## Risks and Edge Cases

Missing `xlators/lib/src` include coverage could break `GET_ANCESTRY_PATH_KEY` or default helper use. Since there is no generated source, clean behavior is simple.

## Test Signals

Clean configure/build should produce `namespace.la`; include-order and warning checks should cover `namespace.h` and namespace fop declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/namespace/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/namespace/src/namespace.c -->
# sources/distributed-fs/glusterfs/xlators/features/namespace/src/namespace.c

## Purpose

`namespace.c` implements a translator that tags each request's root with a namespace hash, derived from the top-level path component, so later translators can throttle, account, log, or otherwise group fops by namespace.

## Important APIs, Types, and Functions

Core helpers are `parse_path`, `ns_inode_ctx_put`, `ns_inode_ctx_get`, `set_ns_from_loc`, `set_ns_from_fd`, `get_path_resume_cbk`, and the `GET_ANCESTRY_PATH_WIND` macro. Nearly every Gluster fop has an `ns_*` wrapper in the `fops` table, including create, lookup, read/write, xattr, lock, directory, fallocate, discard, and zerofill operations. Lifecycle hooks are `init`, `fini`, `reconfigure`, and `ns_forget`.

## Control Flow

Each fop wrapper attempts to populate `frame->root->ns_info`. Loc-based operations call `set_ns_from_loc`; fd-based operations call `set_ns_from_fd`. These helpers reset the namespace info, honor the `tag-namespaces` option, try cached inode context first, then parse a loc path or an `inode_path` result. The parser hashes the first path component after leading slashes with `SuperFastHash`; root hashes `/`. If the path looks like a GFID pseudo-path beginning with `<`, the fop creates a separate privileged frame, builds a call stub for the original operation, winds `getxattr` for `GET_ANCESTRY_PATH_KEY`, parses the returned path in `get_path_resume_cbk`, caches it on the inode, destroys the temporary frame, and resumes the original fop.

After namespace tagging, the original fop is passed to `FIRST_CHILD(this)` with the default callback. `ns_getspec` is the only simple pass-through that does not set namespace information.

## State and Persistence Behavior

Runtime state is `ns_private_t` in `this->private`, holding the `tag_namespaces` boolean. Per-inode cached namespace state is a heap-allocated `ns_info_t` stored through inode context and freed by `ns_forget`. Per-fallback request state is `ns_local_t`, which owns a fake loc and resume stub until `get_path_resume_cbk` resumes the original fop. No disk state is written by this translator.

## Dependencies and Integration Points

The translator depends on `SuperFastHash`, Gluster frame `root->ns_info`, inode contexts, call stubs, default fop callbacks, and the ancestry xattr convention `GET_ANCESTRY_PATH_KEY` supplied by lower layers such as POSIX. It must have exactly one child.

## Risks and Edge Cases

There is a likely bug in `set_ns_from_loc`: after `inode_path` succeeds into local variable `path`, it calls `parse_path(info, loc->path)` instead of `parse_path(info, path)`, so GFID fallback may still parse the GFID-style loc path. `ns_inode_ctx_put` allocates a fresh cached object without checking/replacing an existing context, which could leak if called repeatedly for the same inode. The fallback macro has several `goto wind` paths after partially allocating frames or stubs, which can leak those allocations. Namespace tagging is best effort: disabled config, missing paths, missing inode, or failed ancestry lookup still pass the fop through untagged.

## Test Signals

Tests should cover hashing of root, single-component paths, nested paths, repeated slashes, GFID pseudo-paths, fd-based fops with cached and uncached inode contexts, ancestry lookup fallback, reconfigure toggling `tag-namespaces`, `ns_forget` cleanup, and all fop classes preserving original arguments while setting or clearing `frame->root->ns_info`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/namespace/src/namespace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/namespace/src/namespace.h -->
# sources/distributed-fs/glusterfs/xlators/features/namespace/src/namespace.h

## Purpose

`namespace.h` defines the private types used by the namespace translator.

## Important APIs, Types, and Functions

It defines `GF_NAMESPACE`, `ns_private_t` with `tag_namespaces`, and `ns_local_t` with a fake `loc_t` plus a `call_stub_t *` used while resolving ancestry paths.

## Control Flow

No executable control flow is present.

## State and Persistence Behavior

`ns_private_t` is stored in `this->private`; `ns_local_t` is temporary request state for the fallback getxattr path. Neither is persisted to disk.

## Dependencies and Integration Points

The header includes `config.h` and Gluster call-stub definitions, and it relies on Gluster `loc_t` and boolean types being available through the translation unit includes.

## Risks and Edge Cases

Because `ns_local_t` owns a copied/fake loc and a call stub, cleanup must always wipe the loc and resume or destroy the stub exactly once. Changes to `frame->root->ns_info` layout outside this header affect namespace behavior even though the type is not declared here.

## Test Signals

Compile coverage and fallback ancestry tests validate allocation and cleanup of `ns_local_t`, while init/reconfigure tests validate `ns_private_t` handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/namespace/src/namespace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/quiesce/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/quiesce/Makefile.am

## Purpose

This top-level Automake file delegates quiesce translator builds to `src`.

## Important APIs, Types, and Functions

It defines `SUBDIRS = src` and empty `CLEANFILES`.

## Control Flow

The parent build recurses into `src`.

## State and Persistence Behavior

No runtime state is defined.

## Dependencies and Integration Points

It integrates with the feature translator build tree.

## Risks and Edge Cases

If `src` is not traversed, `quiesce.la` and its generated message/memory type coverage are not built.

## Test Signals

Autotools build should enter this directory and compile `quiesce/src/quiesce.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/quiesce/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/quiesce/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/quiesce/src/Makefile.am

## Purpose

This Automake file builds and installs the `quiesce.la` feature translator.

## Important APIs, Types, and Functions

It defines `xlator_LTLIBRARIES = quiesce.la`, module flags, `quiesce_la_SOURCES = quiesce.c`, `quiesce_la_LIBADD`, `noinst_HEADERS = quiesce.h quiesce-mem-types.h quiesce-messages.h`, include paths, and warning flags.

## Control Flow

Build flow compiles the quiesce source and links a Gluster xlator module against libglusterfs.

## State and Persistence Behavior

No generated build state is produced; clean state is empty.

## Dependencies and Integration Points

The translator depends on libglusterfs headers, RPC XDR include paths, and message/memory type headers in the same directory.

## Risks and Edge Cases

Memory type and message headers must stay in the noinst header list for distribution and compile dependency tracking. Missing timer/thread support in libglusterfs would break the implementation at compile time.

## Test Signals

Clean build of `quiesce.la`, include dependency tracking, and warning checks for `quiesce.c` are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/quiesce/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/quiesce/src/quiesce-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/features/quiesce/src/quiesce-mem-types.h

## Purpose

`quiesce-mem-types.h` registers memory accounting categories for the quiesce translator.

## Important APIs, Types, and Functions

The enum `gf_quiesce_mem_types_` defines `gf_quiesce_mt_priv_t`, `gf_quiesce_mt_failover_hosts`, and `gf_quiesce_mt_end`, starting after `gf_common_mt_end`.

## Control Flow

There is no runtime control flow; `quiesce.c` passes `gf_quiesce_mt_end` to `xlator_mem_acct_init` and uses the specific types in allocations.

## State and Persistence Behavior

No state is persisted. The enum enables memory accounting for private state and failover host records.

## Dependencies and Integration Points

It includes Gluster common memory type definitions and must stay synchronized with allocation sites in `quiesce.c`.

## Risks and Edge Cases

Adding allocations without memory types reduces accounting visibility. Renumbering can collide with other components if not based on `gf_common_mt_end`.

## Test Signals

Memory accounting initialization and leak reports should categorize quiesce private and failover host allocations correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/quiesce/src/quiesce-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/quiesce/src/quiesce-messages.h -->
# sources/distributed-fs/glusterfs/xlators/features/quiesce/src/quiesce-messages.h

## Purpose

`quiesce-messages.h` defines structured log message IDs for the quiesce translator.

## Important APIs, Types, and Functions

It declares the `QUIESCE` GLFS component and two messages: `QUIESCE_MSG_INVAL_HOST` for invalid failover host addresses and `QUIESCE_MSG_FAILOVER_FAILED` for failed failover initiation.

## Control Flow

No direct control flow exists. `quiesce.c` uses these message macros when parsing failover hosts and when failover setxattr submission fails.

## State and Persistence Behavior

No runtime state is stored. Message IDs are part of the logging ABI and should remain stable.

## Dependencies and Integration Points

It includes `glfs-message-id.h` and uses `GLFS_COMPONENT` and `GLFS_NEW` macros.

## Risks and Edge Cases

The comment notes that message IDs should not be removed or reused. The closing guard comment names `__NL_CACHE_MESSAGES_H__`, which is stale but harmless.

## Test Signals

Compile structured logging and verify logs include host and errno fields for invalid failover host and failover submission failure cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/quiesce/src/quiesce-messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/quiesce/src/quiesce.c -->
# sources/distributed-fs/glusterfs/xlators/features/quiesce/src/quiesce.c

## Purpose

`quiesce.c` implements a translator that temporarily queues filesystem operations while its child is unavailable or not in pass-through mode, optionally tries failover hosts, and drains queued operations when connectivity returns or failover attempts are exhausted.

## Important APIs, Types, and Functions

Core queue/failover helpers are `gf_quiesce_enqueue`, `gf_quiesce_dequeue`, `gf_quiesce_dequeue_start`, `gf_quiesce_timeout`, `__gf_quiesce_start_timer`, `gf_quiesce_populate_failover_hosts`, `__gf_quiesce_perform_failover`, `gf_quiesce_failover_cbk`, and `gf_quiesce_local_wipe`. Lifecycle and event hooks are `mem_acct_init`, `init`, `reconfigure`, `fini`, and `notify`.

The `fops` table covers modifying fops, lock/xattr state-changing fops, writev, and a retransmittable group including lookup, stat, fstat, access, readlink, getxattr, fgetxattr, open, readv, flush, fsync, statfs, opendir, readdir, readdirp, fsyncdir, and seek.

## Control Flow

When `priv->pass_through` is false, fop wrappers create a `call_stub_t` for the corresponding default resume function and append it to `priv->req` under lock. Enqueue also starts a timer if one is not active. When the child reports `GF_EVENT_CHILD_UP`, `notify` starts a dequeue thread and marks pass-through true, causing queued stubs to resume and new fops to wind to the child. When the child reports down, pass-through is set false and the timer is started.

On timer expiry, `gf_quiesce_timeout` tries failover if pass-through is still false. `__gf_quiesce_perform_failover` picks the first untried configured failover host and sends a child `setxattr` with `CLIENT_CMD_CONNECT`; the failover callback restarts the timer. If all failover hosts have been tried or setup fails, pass-through is set true and the queue is drained, allowing operations to complete rather than remain quiesced indefinitely.

For selected read-like or idempotent fops, pass-through mode uses custom callbacks that save enough request state in `quiesce_local_t`. If the child returns `-1/ENOTCONN`, the callback creates a default resume stub and queues it for later retry. Many state-changing fops do not use retransmit callbacks; they are either queued before winding or directly wound while pass-through is true.

## State and Persistence Behavior

All state is in memory: `quiesce_priv_t` stores the timer, pass-through flag, queue lock, request list and size, dequeue thread, local mem pool, timeout, failover host string, and parsed failover list. `quiesce_local_t` stores copied loc/fd/name/dict/vector/iobref/offset/flags needed to retry a fop after ENOTCONN. There is no disk persistence; queued operations are lost if the process exits.

## Dependencies and Integration Points

The translator depends on Gluster timers, pthread creation, call stubs, default resume/callback functions, list and lock primitives, dicts, mem pools, `valid_internet_address`, child notify events, and the client command `CLIENT_CMD_CONNECT` sent through setxattr. It requires exactly one child.

## Risks and Edge Cases

Queue growth is unbounded except by memory, and `queue_size` is only informational. Some pass-through paths allocate `quiesce_local_t` without checking allocation failure before dereferencing. `gf_quiesce_populate_failover_hosts` calls `continue` on invalid host tokens without advancing `addr_tok`, which can loop indefinitely on an invalid first token. `fini` does not clean queued stubs, failover list entries, or active timers, so shutdown during queued state can leak or leave callbacks racing. Retransmission is intentionally disabled or not implemented for many state-changing fops; nevertheless, queued pre-wind operations will run later and may observe changed application context.

## Test Signals

Tests should cover child-down queueing for every fop class, child-up dequeue thread behavior, timer expiry with no failover hosts, failover host parsing including invalid entries, failover setxattr success/failure, ENOTCONN retransmit for lookup/stat/read/open/readdir/seek paths, memory cleanup of locals, O_APPEND stripping in create/open, reconfigure of timeout and failover hosts, and process shutdown with nonempty queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/quiesce/src/quiesce.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/quiesce/src/quiesce.h -->
# sources/distributed-fs/glusterfs/xlators/features/quiesce/src/quiesce.h

## Purpose

`quiesce.h` defines the private queue, failover, and per-fop retry state used by the quiesce translator.

## Important APIs, Types, and Functions

`GF_FOPS_EXPECTED_IN_PARALLEL` sizes the local pool. `quiesce_failover_hosts_t` stores failover host list nodes, host address strings, and a `tried` flag. `quiesce_priv_t` stores timer/pass-through/lock/queue/thread/mem-pool/timeout/failover-list state. `quiesce_local_t` stores fd, name, volname, loc, offsets, mode, flags, stat buffer, iovec/iobref, dict, flock, entrylock fields, xattrop flags, write-behind flags, io flags, fallocate length, and seek type.

## Control Flow

The header has no executable flow. Its fields are consumed by enqueue/dequeue, pass-through callbacks, retransmit callbacks, failover, and cleanup code in `quiesce.c`.

## State and Persistence Behavior

All types are in-memory only. `quiesce_priv_t` lasts for the translator lifetime; `quiesce_local_t` is per-inflight fop and must be wiped after unwind or requeue.

## Dependencies and Integration Points

It includes quiesce memory/message headers and Gluster timer definitions, and it relies on Gluster list, lock, fd, loc, dict, iobuf, flock, xattrop, and seek types.

## Risks and Edge Cases

Because `quiesce_local_t` stores many borrowed or copied pointer types, each fop wrapper must ref/copy exactly the fields its callback will use. Missing cleanup for any populated field risks leaks, while storing borrowed pointers for queued retries risks use-after-free.

## Test Signals

Compile coverage plus fop-specific retry tests should validate that every populated `quiesce_local_t` field is cleaned and that failover list entries are allocated, marked tried, and freed correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/quiesce/src/quiesce.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/quota/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/quota/Makefile.am

## Purpose

This top-level Automake fragment delegates quota translator builds to `src`.

## Important APIs, Types, and Functions

It defines `SUBDIRS = src` and an empty `CLEANFILES` variable with trailing whitespace.

## Control Flow

The build system descends into `src` to build quota and quotad modules.

## State and Persistence Behavior

No runtime state is defined.

## Dependencies and Integration Points

It integrates with the GlusterFS feature translator build layout.

## Risks and Edge Cases

If recursion is broken, quota and quotad translators are omitted from the build. The trailing whitespace in `CLEANFILES = ` is harmless.

## Test Signals

Autotools build should recurse into `quota/src` and apply its `WITH_SERVER` gated build rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/quota/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/quota/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/quota/src/Makefile.am

## Purpose

This Automake file builds the server-side quota and quotad translator modules when server support is enabled.

## Important APIs, Types, and Functions

Under `if WITH_SERVER`, it defines `xlator_LTLIBRARIES = quota.la quotad.la`. It sets module flags for both libraries, source lists for `quota_la_SOURCES = quota.c quota-enforcer-client.c` and `quotad_la_SOURCES = quotad.c quotad-helpers.c quotad-aggregator.c`, library dependencies on libglusterfs, XDR, and RPC libraries, quota headers, include paths, and warning flags.

## Control Flow

Configure-time `WITH_SERVER` controls whether quota modules are built. When enabled, the build compiles quota enforcement/client support and quotad helper/aggregator code and links the two xlator modules.

## State and Persistence Behavior

The makefile does not define runtime state. It determines which quota binaries are produced and installed.

## Dependencies and Integration Points

Quota links against libglusterfs, `libgfxdr`, and `libgfrpc`, includes RPC headers and DHT headers, and installs into the standard Gluster xlator feature directory.

## Risks and Edge Cases

Client-only builds will not produce these modules because of `WITH_SERVER`. Source/header lists must stay synchronized with quota implementation files; missing RPC or DHT include paths break compile. Marker's quota integration depends on these quota components at runtime even though marker has its own helper code.

## Test Signals

Build with `WITH_SERVER` enabled and disabled, verify both `quota.la` and `quotad.la` link when enabled, and run clean builds to catch source/header dependency drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/quota/src/Makefile.am -->
