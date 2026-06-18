# Research: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-rebalance.c

## Purpose

`dht-rebalance.c` implements the DHT translator's rebalance, remove-brick migration, layout-fix, and defrag worker machinery. It handles whole-file migration between subvolumes, special file migration, hardlink-aware migration, directory crawling, parallel migration queues, commit-hash/layout updates, progress estimates, status reporting, and stop/completion lifecycle for the defrag process.

## Important APIs, Types, and Functions

The file is centered on `gf_defrag_info_t` and `dht_conf_t` from `dht-common.h`. `gf_defrag_info_t` stores counters, status, root inode, commit hash, queue state, condition variables, throttling counts, and file-counter state. `dht_container_t` carries one queued directory entry plus parent loc and migration dict. `dir_dfmeta` stores per-local-subvolume readdir state, offsets, entry queues, and directory fds.

Important migration functions include `gf_defrag_handle_hardlink`, `__is_file_migratable`, `__dht_rebalance_create_dst_file`, `__dht_check_free_space`, `__dht_rebalance_migrate_data`, `__dht_rebalance_open_src_file`, `migrate_special_files`, `__dht_migration_cleanup_src_file`, and the central `dht_migrate_file`. Task wrappers include `rebalance_task`, `rebalance_task_completion`, and `dht_start_rebalance_task` for client-triggered migration. Full rebalance uses `gf_defrag_start`, `gf_defrag_start_crawl`, `gf_defrag_fix_layout`, `gf_defrag_process_dir`, `gf_defrag_get_entry`, `gf_defrag_task`, and cleanup/status helpers.

## Control Flow

Single-file migration starts in `dht_migrate_file`. It builds a dictionary requesting linkto xattrs and, when lock migration is disabled, POSIX lock counts. It builds the parent loc, takes a blocking inodelk on the cached/source subvolume in `DHT_FILE_MIGRATE_DOMAIN`, then takes an entrylk on the hashed/destination subvolume in `DHT_ENTRY_SYNC_DOMAIN` to synchronize with rename. It looks up the source, rejects directories, handles hardlink policy, and routes non-regular files to `migrate_special_files`.

For regular files, the destination is created or opened with requested GFID and linkto metadata, free space is checked, and the target can be changed to a different subvolume if min-free-disk would be crossed. The source is opened, marked with linkto xattr and sticky/sgid migration mode, xattrs are copied to the destination with ACLs stripped initially, data is copied in one-megabyte chunks, and optional durability fsync is issued. Sparse files use `syncop_seek` with `GF_SEEK_DATA` and `GF_SEEK_HOLE` to copy only data segments.

After data copy, the function performs final metadata and lock work. If lock migration is enabled it uses a metadata lock xattr, `syncop_getactivelk`, and `syncop_setactivelk`; otherwise it tries an exclusive POSIX lock on the source fd. It applies final uid/gid/mode/timestamps, updates linkto if the destination changed, restores POSIX ACLs, converts the source to a linkto-style file, truncates source data, removes linkto from the destination, unlinks the source linkto when GFID still matches, and does a final DHT lookup. The out path releases metadata locks, source/destination cleanup state, inodelk, entrylk, POSIX locks, fds, xattrs, dicts, and locs.

Full rebalance starts through `gf_defrag_start`, which creates a frame with `GF_CLIENT_PID_DEFRAG` and schedules `gf_defrag_start_crawl`. The crawl task builds a synthetic root loc, verifies root lookup, updates disk usage, writes commit-hash and fix-layout xattrs, optionally initializes local subvolume/node UUID data, starts parallel migration worker threads and the estimates thread, then recursively fixes layouts from the root. `gf_defrag_fix_layout` recurses through directories, applies `GF_XATTR_FIX_LAYOUT_KEY`, optionally processes files in each directory, and settles the new commit hash when appropriate. `gf_defrag_process_dir` opens each local subvolume directory, performs round-robin `readdirp`, and queues migratable file containers. `gf_defrag_task` worker threads consume the queue under `dfq_mutex`, honor high and low watermarks, support thread-count reconfiguration, and call `gf_defrag_migrate_single_file`.

## State and Persistence Behavior

The code writes several persistent or externally visible states. Layout repair and commit hash are written through xattrs such as `conf->commithash_xattr_name`, `GF_XATTR_FIX_LAYOUT_KEY`, and `new-commit-hash`. File migration uses `conf->link_xattr_name` to mark linkto targets, uses sticky/sgid mode bits on the source to mark migration in progress, may create linkto files on old targets, truncates migrated source files, removes destination linkto xattrs after successful migration, and migrates POSIX ACLs after the destination is no longer a linkto file. Lock migration uses internal xattrs such as `GF_META_LOCK_KEY`, `GF_META_UNLOCK_KEY`, and status.

In-memory state includes defrag counters (`total_files`, `total_data`, `num_files_lookedup`, `total_failures`, `skipped`, `size_processed`), process status (`GF_DEFRAG_STATUS_*`), queue length, crawl completion, condition variables, current/reconfigured thread counts, and total-size estimates. `gf_defrag_status_get` exposes status into a dict and logs operator-readable progress.

## Dependencies and Integration Points

The file depends on DHT helpers for subvolume selection, layouts, loc building, disk usage, and linkfile detection. It uses synchronous Gluster operations heavily: lookup, setxattr, getxattr, listxattr, open, create, readv, writev, seek, fstat, setattr/fsetattr, truncate/ftruncate, statfs, opendir, readdir/readdirp, unlink, mknod, symlink, link, fsync, inodelk, entrylk, lk, getactivelk, and setactivelk. It integrates with Gluster events through `gf_event`, thread creation through `gf_thread_create`, synctasks through `synctask_new`, and process shutdown through `gf_listener_stop` and `SIGTERM` after defrag completion.

## Risks and Edge Cases

Migration is concurrency-sensitive. The code explicitly guards rename races with entry locks, same-file migration races with inode locks and hardlink `link_lock`, client write races with `GF_AVOID_OVERWRITE` unless force migration is enabled, and file lock races with lock migration or source fd locks. There are still documented windows around lock migration where conflicting locks can be granted across source and destination.

Hardlink migration is especially subtle. `gf_defrag_handle_hardlink` returns `-2` as a success-like "do not migrate this link now" signal so `dht_migrate_file` does not migrate every hardlink independently. Parallel hardlink migration is serialized with `conf->link_lock` because current inodelk owner behavior is not sufficient. Sparse-file migration must handle changing holes/data while users modify the file. Destination target changes cannot be handled for hardlinks and are treated as failure. Cleanup paths are broad and best effort; failures can leave linkto xattrs, zero-length destination stubs, stale source markers, or log-only cleanup warnings.

Directory crawling and queueing also have operational risks. The crawler uses high and low watermarks (`MAX_MIGRATE_QUEUE_COUNT`, `MIN_MIGRATE_QUEUE_COUNT`) and condition variables; missed wakeups or incorrect `crawl_done` handling can stall workers. Remove-brick mode treats some failures more strictly and increments failure counters differently depending on whether the source is a decommissioned brick. Layout commit hash must not be settled after partial directory failures, otherwise lookup optimization could hide unhealed subdirectories.

## Test Signals

High-value tests include file migration with concurrent rename, concurrent writes, open POSIX locks, lock migration enabled and disabled, hardlinks under remove-brick, sparse files, special files, destination GFID mismatch, ENOENT/ESTALE races during source cleanup, min-free-disk target changes, ACL preservation, and force migration behavior. Rebalance-level tests should cover layout-only fix, full rebalance, remove-brick with decommissioned subvolumes, brick down `ENOTCONN`, stop requests, estimates thread lifecycle, thread-count reconfiguration, and queue high/low watermark behavior. Log and status signals include `DHT_MSG_MIGRATE_FILE_COMPLETE`, `DHT_MSG_MIGRATE_FILE_FAILED`, `DHT_MSG_MIGRATE_FILE_SKIPPED`, `DHT_MSG_REBALANCE_STATUS`, `DHT_MSG_REBALANCE_STOPPED`, and event emission for complete, failed, and stopped rebalance statuses.
