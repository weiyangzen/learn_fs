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
