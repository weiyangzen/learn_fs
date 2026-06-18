# subset-b-007098 Research

Grouped source research for GlusterFS shard translator implementation/header files and simple-quota autotools build manifests. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/shard/src/shard.c -->
# sources/distributed-fs/glusterfs/xlators/features/shard/src/shard.c

## Purpose

`sources/distributed-fs/glusterfs/xlators/features/shard/src/shard.c` implements the GlusterFS `features/shard` translator. The translator presents a regular file to callers while storing file data across a base shard and numbered shard files under `/.shard`; it keeps logical size and block count in trusted shard xattrs and hides internal shard metadata from normal clients. The source was read as a complete 7,716-line file for this report.

The implementation owns the full translator lifecycle: fop interception, shard lookup/create/delete, size and block-count accounting, inode-context caching, shard LRU management, pending-fsync tracking, background cleanup of unlinked files, option parsing, statedump, and `xlator_api` registration.

## Important APIs, Types, and Functions

Translator entry points are registered in `struct xlator_fops fops`: `shard_lookup`, `shard_open`, `shard_opendir`, `shard_flush`, `shard_fsync`, `shard_stat`, `shard_fstat`, `shard_getxattr`, `shard_fgetxattr`, `shard_readv`, `shard_writev`, `shard_truncate`, `shard_ftruncate`, `shard_setxattr`, `shard_fsetxattr`, `shard_setattr`, `shard_fsetattr`, `shard_removexattr`, `shard_fremovexattr`, `shard_fallocate`, `shard_discard`, `shard_zerofill`, `shard_readdir`, `shard_readdirp`, `shard_create`, `shard_mknod`, `shard_link`, `shard_unlink`, `shard_rename`, and `shard_seek`. Callback and lifecycle integration is through `shard_forget`, `shard_release`, `shard_releasedir`, `shard_priv_dump`, `mem_acct_init`, `init`, `fini`, and `reconfigure`.

Core helpers include inode-context accessors (`shard_inode_ctx_get`, `shard_inode_ctx_set`, `shard_inode_ctx_fill_iatt_from_cache`, refresh/invalidate helpers), path/name builders (`shard_make_block_bname`, `shard_make_base_path`, `shard_append_index`), internal-directory resolution (`shard_init_internal_dir_loc`, `shard_lookup_internal_dir`, `shard_refresh_internal_dir`, `shard_mkdir_internal_dir`), shard discovery and creation (`shard_common_resolve_shards`, `shard_common_lookup_shards`, `shard_common_resume_mknod`), size accounting (`shard_set_size_attrs`, `shard_modify_size_and_block_count`, `shard_update_file_size`), and unwind helpers (`shard_common_failure_unwind`, `shard_common_inode_write_success_unwind`).

Deletion and cleanup are handled by `shard_unlink`, `shard_rename`, marker-file helpers under `.remove_me`, locking helpers (`shard_acquire_inodelk`, `shard_unlock_inodelk`, `shard_acquire_entrylk`, `shard_unlock_entrylk`), `shard_delete_shards`, `shard_regulated_shards_deletion`, and the `shard_unlink_handler` background thread. Fsync correctness uses `shard_inode_ctx_add_to_fsync_list`, `shard_post_lookup_fsync_handler`, and `shard_fsync_shards_cbk`.

## Control Flow

Fast paths pass through to the child translator when a file is not sharded, when the operation targets directories or symlinks where appropriate, or when the client PID is gsyncd for replication-related access. `lookup` requests shard block-size and file-size xattrs, updates inode context, and triggers background cleanup on the first normal lookup. `stat`, `fstat`, `setattr`, `xattr`, and `readdirp` paths request or rewrite shard size metadata so callers see logical file attributes rather than the base shard's physical size.

Read flow refreshes base metadata, computes first and last participating shard blocks, resolves or looks up shard inodes, allocates one result iobuf, dispatches per-shard `readv` calls on the base fd or anonymous shard fds, and copies returned vectors into the caller-visible buffer. Missing shard files in hole regions are treated as zero-filled data.

Write-like flow is shared by `writev`, supported `fallocate`, `zerofill`, and `discard`. It refreshes base metadata, adjusts append offsets, computes the block range, ensures `/.shard` exists, resolves existing shards, creates missing shard files with generated GFIDs, dispatches per-shard writes or space operations, accumulates bytes written and block deltas, updates pending fsync state for modified non-base shards, then updates `trusted.glusterfs.shard.file-size` through xattrop.

Truncate flow compares requested size against cached logical size. Extending a file only updates size xattrs and cached metadata. Shrinking unlinks higher-numbered shards, truncates the last retained shard when needed, subtracts block counts, and writes the new logical size. Unlink and rename of sharded targets create marker files under `/.shard/.remove_me`, lock the base inode and marker entry, remove or rename the base file, and let background cleanup delete numbered shards later.

## State and Persistence Behavior

Persistent state is stored in backend files and trusted xattrs: `trusted.glusterfs.shard.block-size` marks a sharded file and `GF_XATTR_SHARD_FILE_SIZE` stores logical size and block count as a four-slot big-endian int64 array. Numbered shard files are named `<base-gfid>.<block-number>` under `/.shard`; pending-delete marker files are named by base GFID under `/.shard/.remove_me` and carry enough shard xattrs for later cleanup.

In-memory state lives in `shard_priv_t`, per-call `shard_local_t`, and per-inode `shard_inode_ctx_t`. The private object stores default block size, fixed GFIDs/inodes for internal directories, a global lock, LRU list and count, deletion rate/state, first-lookup flag, LRU limit, and background unlink thread state. Inode context caches the shard block size, logical stat fields, refresh/refreshed flags, shard LRU linkage, base GFID/block number, pending-fsync list membership, fsync counters, and inode references.

The translator uses `priv->lock`, inode locks, frame locks, sync barriers, inodelk, and entrylk to coordinate concurrent shard operations. It temporarily switches frame uid/gid to root for internal directory and shard manipulation, then restores caller credentials.

## Dependencies and Integration Points

Direct includes are `<unistd.h>`, `"shard.h"`, `"shard-mem-types.h"`, `<glusterfs/defaults.h>`, and `<glusterfs/statedump.h>`. The implementation depends heavily on GlusterFS core APIs for frames, stack winding, loc/inode/fd lifetimes, dict/xattr handling, syncop cleanup, pthread-backed helper threads, memory pools, iobuf/iobref, logging, GFID utilities, locks, and volume option parsing.

Primary integration points are the single child translator, GlusterD volume options (`shard`, `shard-block-size`, `shard-deletion-rate`, `shard-lru-limit`), geo-replication and heal client PID exceptions, reserve-space internal fop markers, statedump private reporting, and the global translator API object with identifier `shard`.

## Risks and Edge Cases

Metadata consistency is the main risk: comments explicitly note unresolved races between concurrent writes and truncates while updating size and block-count xattrs. Any error in delta-size, delta-block, or cached timestamp handling can expose wrong logical file attributes or lose block-accounting updates.

Deletion correctness depends on marker files, inodelk/entrylk ordering, background state transitions, and syncop cleanup. Crashes between marker creation and background deletion should be recoverable, but bugs can leak shards or delete shards for a live base file if nameless lookup/link-count checks are wrong. LRU eviction also has a correctness dependency on pending-fsync tracking; evicted shard inodes that need fsync are flushed before in-memory unlink/forget.

Access-control and visibility boundaries are delicate. Normal clients are denied internal shard xattrs and `.shard` entries, while gsyncd is allowed selected bypasses. Readdir must filter `.shard` from the root directory without corrupting offsets. Unsupported or partial behavior is documented by code comments for `seek`, flushing all shards, `open` with `O_TRUNC`, and requesting open-fd counts during unlink/rename.

Memory and reference management is complex because shard inodes are linked into the inode table, LRU list, pending-fsync list, and per-call arrays. Failure paths must unwind frames, unref locs/fds/dicts/iobufs, and destroy barriers exactly once.

## Test Signals

High-value tests include lookup/stat/readdirp showing logical size and block count for sharded files; read/write across block boundaries, sparse reads over absent shards, append writes, direct I/O writes, and writes that create multiple new shards; truncate extend/shrink cases including exact block boundaries and sparse regions; fsync after multi-shard writes and fsync after LRU eviction; unlink/rename with link count one versus multiple links and crash-restart cleanup from `.remove_me`; gsyncd/heal bypass coverage; denial of normal client access to shard xattrs and `/.shard`; readdir root filtering of `.shard`; option parsing/reconfigure bounds for block size, deletion rate, and LRU limit; fault-injection for missing internal directories, ENOENT shard holes, ENOMEM paths, failed xattrop, failed mknod/unlink, and syncop cleanup failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/shard/src/shard.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/shard/src/shard.h -->
# sources/distributed-fs/glusterfs/xlators/features/shard/src/shard.h

## Purpose

`sources/distributed-fs/glusterfs/xlators/features/shard/src/shard.h` is the private interface and shared type definition header for the GlusterFS shard translator. It defines shard directory/xattr constants, valid-bit masks for cached inode attributes, block-index macros, lock/unwind/create/read-metadata helper macros, callback typedefs, and the central private/local/inode-context structures used by `shard.c`. The source was read as a complete 359-line file for this report.

## Important APIs, Types, and Functions

Important constants include `GF_SHARD_DIR` (`.shard`), `GF_SHARD_REMOVE_ME_DIR` (`.remove_me`), `SHARD_MIN_BLOCK_SIZE`, `SHARD_MAX_BLOCK_SIZE`, `SHARD_XATTR_PREFIX`, and `GF_XATTR_SHARD_BLOCK_SIZE`. Attribute mask macros (`SHARD_MASK_BLOCK_SIZE`, `SHARD_MASK_PROT`, `SHARD_MASK_NLINK`, `SHARD_MASK_UID`, `SHARD_MASK_GID`, `SHARD_MASK_SIZE`, `SHARD_MASK_BLOCKS`, `SHARD_MASK_TIMES`, `SHARD_MASK_OTHERS`, `SHARD_MASK_REFRESH_RESET`) compose into `SHARD_INODE_WRITE_MASK`, `SHARD_LOOKUP_MASK`, and `SHARD_ALL_MASK`. `get_lowest_block` and `get_highest_block` map logical byte ranges to shard block numbers.

Externally visible functions declared here are `shard_unlock_inodelk`, `shard_unlock_entrylk`, and the `shard_local_wipe`/`shard_set_size_attrs` functions used by implementation macros. Operational macros include `SHARD_ENTRY_FOP_CHECK`, `SHARD_INODE_OP_CHECK`, `SHARD_STACK_UNWIND`, `SHARD_STACK_DESTROY`, `SHARD_INODE_CREATE_INIT`, `SHARD_MD_READ_FOP_INIT_REQ_DICT`, `SHARD_SET_ROOT_FS_ID`, `SHARD_UNSET_ROOT_FS_ID`, and `SHARD_TIME_UPDATE`.

Key types are `shard_bg_deletion_state_t`, `shard_unlink_thread_t`, `shard_priv_t`, `shard_inodelk_t`, `shard_entrylk_t`, callback typedefs for post-fop stages, `shard_local_t`, `shard_inode_ctx_t`, and `shard_internal_dir_type_t`.

## Control Flow

This header has no standalone runtime flow, but its macros encode important control-flow conventions used throughout `shard.c`. Entry/inode checks jump to caller labels with `EPERM` for protected internal paths. The stack unwind/destroy macros release internal locks and wipe pooled local state before returning to the caller. Create/mknod initialization macros attach block-size and logical-size xattrs to new files. Metadata-read macros request logical size xattrs. FS-id macros temporarily elevate internal operations to uid/gid zero. `SHARD_TIME_UPDATE` preserves monotonic-ish cached timestamp behavior by reconciling seconds and nanoseconds between cached and returned attributes.

## State and Persistence Behavior

The header defines both persistent metadata names and in-memory state layout. Persistent backend state is addressed by `GF_XATTR_SHARD_BLOCK_SIZE`, `GF_XATTR_SHARD_FILE_SIZE` from the included message/xattr ecosystem, and internal directory names. In-memory translator-wide state in `shard_priv_t` persists for the translator lifetime and includes configured block size, internal GFIDs/inodes, shard LRU accounting, background deletion state, first-lookup cleanup trigger, LRU limit, and unlink thread state.

`shard_local_t` is per-call state and carries operation result fields, block range and counts, fop identity, offsets/sizes, xattr dicts, loc/fd references, inode lists, iobufs, lock descriptors, sync barriers, post-stage handlers, deletion parameters, and base GFID. `shard_inode_ctx_t` is attached to GlusterFS inodes and caches block size and logical stat fields; for shard inodes it also carries LRU linkage, base GFID/block number, refresh flags, pending-fsync linkage, fsync counters, and base/shard inode references.

## Dependencies and Integration Points

Direct includes are `<glusterfs/xlator.h>`, `<glusterfs/compat-errno.h>`, `"shard-messages.h"`, and `<glusterfs/syncop.h>`. The header assumes GlusterFS core definitions for `call_frame_t`, `xlator_t`, `loc_t`, `fd_t`, `dict_t`, `inode_t`, `struct iatt`, `gf_lock_t`, `gf_boolean_t`, `syncbarrier_t`, `gf_dirent_t`, `struct list_head`, and fop identifiers.

The header is tightly coupled to `shard.c`, the shard memory-type definitions, GlusterFS xattr constants, translator stack-wind/unwind semantics, syncop APIs, and option/lifecycle registration in the implementation file.

## Risks and Edge Cases

Macro side effects are a key risk because several macros allocate memory, mutate dictionaries, change frame credentials, call unlock functions, jump to caller labels, and free local state. Callers must pass labels and initialized locals consistently. `SHARD_INODE_CREATE_INIT` allocates buffers that become dict-owned only after successful `dict_set_bin`; error paths must not double free or leak them.

Structure layout changes have broad blast radius because `shard_local_t` and `shard_inode_ctx_t` are shared across many asynchronous callbacks. Adding fields without wiping/unref handling in `shard_local_wipe` can leak references. Changing mask semantics can make cached stats stale or incomplete. Any caller of FS-id macros must pair set/unset around all exits to avoid credential leakage on a frame.

## Test Signals

Compile coverage of all shard translator sources is the first signal because this header carries most type contracts. Runtime signals should verify protected path checks, creation xattr initialization, logical metadata read requests, lock release during unwind, timestamp cache updates, fs-id restoration on success and failure, inode-context mask behavior, and local cleanup after error paths that allocate locs/fds/dicts/iobufs or auxiliary lock frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/shard/src/shard.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/simple-quota/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/simple-quota/Makefile.am

## Purpose

`sources/distributed-fs/glusterfs/xlators/features/simple-quota/Makefile.am` is the top-level automake manifest for the GlusterFS `features/simple-quota` translator subtree. The source was read as a complete 3-line file for this report.

## Important APIs, Types, and Functions

There are no C APIs or runtime types. The only build directive is `SUBDIRS = src`, which tells automake to descend into the implementation directory. `CLEANFILES =` is present but empty.

## Control Flow

There is no executable control flow. Build-system flow is a single delegation from the `simple-quota` feature directory into `simple-quota/src`, where the actual translator library is defined.

## State and Persistence Behavior

No runtime state or persistent metadata is owned by this file. Its state is build graph metadata consumed by autotools-generated makefiles.

## Dependencies and Integration Points

The file integrates the `src` subdirectory into the parent GlusterFS build when this subtree is included. It relies on the surrounding automake project to provide recursive make behavior, package variables, and clean target handling.

## Risks and Edge Cases

The main risk is omission: if `SUBDIRS` stops including `src`, the simple-quota translator will not be built or installed even if its source manifest remains correct. The empty `CLEANFILES` is harmless but indicates there are no generated files at this directory level.

## Test Signals

Autotools generation and recursive `make` should enter `xlators/features/simple-quota/src`. Packaging or install tests should confirm the simple-quota xlator is included when the server build enables it. `make clean` should succeed with no directory-level generated artifacts required here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/simple-quota/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/simple-quota/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/simple-quota/src/Makefile.am

## Purpose

`sources/distributed-fs/glusterfs/xlators/features/simple-quota/src/Makefile.am` defines how the GlusterFS `simple-quota` feature translator shared module is built and installed. The source was read as a complete 18-line file for this report.

## Important APIs, Types, and Functions

There are no runtime APIs in this makefile, but the build targets are important: `xlator_LTLIBRARIES = simple-quota.la` is enabled only under `if WITH_SERVER`; `xlatordir = $(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/features` selects the install directory; `simple_quota_la_SOURCES = simple-quota.c`; `simple_quota_la_LIBADD = $(top_builddir)/libglusterfs/src/libglusterfs.la`; and `noinst_HEADERS = simple-quota.h`.

Compiler/linker configuration comes from `simple_quota_la_LDFLAGS = -module $(GF_XLATOR_DEFAULT_LDFLAGS)`, `AM_CPPFLAGS = $(GF_CPPFLAGS) -I$(top_srcdir)/libglusterfs/src`, and `AM_CFLAGS = -Wall $(GF_CFLAGS)`. `CLEANFILES =` is empty.

## Control Flow

There is no executable control flow. Build flow conditionally creates a libtool module from `simple-quota.c` for server builds, links it with `libglusterfs.la`, and installs it in the feature xlator directory for the current package version. The private header participates in compilation but is not installed.

## State and Persistence Behavior

No runtime or file-system metadata state is owned here. The file describes build products and installation paths. The persistent output is the installed `simple-quota.la`/module artifact produced by the build system.

## Dependencies and Integration Points

The manifest depends on the top-level GlusterFS autotools variables `WITH_SERVER`, `PACKAGE_VERSION`, `GF_XLATOR_DEFAULT_LDFLAGS`, `GF_CPPFLAGS`, `GF_CFLAGS`, `top_builddir`, and `top_srcdir`. Its runtime library integration is with `libglusterfs`, and its installation integration is the versioned `xlator/features` module directory used by GlusterFS volume loading.

## Risks and Edge Cases

If `WITH_SERVER` is false, the translator is intentionally not built; packaging expecting the module must set that condition correctly. Incorrect `xlatordir` or package-version variables would install the module where GlusterFS cannot load it. Missing `libglusterfs.la`, stale include paths, or divergence between `simple-quota.c` and `simple-quota.h` will surface as build failures. The makefile does not list extra generated cleanup artifacts.

## Test Signals

Run autotools/configure with server support and verify `simple-quota.la` is built and installed under `$(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/features`. Also test a non-server configuration to ensure the conditional omits the module cleanly. Compile logs should show `simple-quota.c` built with `GF_CPPFLAGS`, `GF_CFLAGS`, `-Wall`, and the libglusterfs include path, and linked as a module against `libglusterfs.la`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/simple-quota/src/Makefile.am -->
