# Research Group: subset-b-007078

Work item `subset-b-007078` covers GlusterFS DHT locking and rebalance support files. Each source file below is wrapped in the exact markers expected by the reconciliation lane.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-lock.c -->
# Research: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-lock.c

## Purpose

`dht-lock.c` implements the DHT translator's internal distributed lock orchestration for inode locks, entry locks, and the combined namespace protection sequence used by operations that must avoid racing with layout changes, renames, and migration. It converts arrays of `dht_lock_t` requests into ordered Gluster FOP winds, tracks which subvolume locks were acquired, unwinds partial acquisitions on failure, and provides wrapper helpers for deferred cleanup from higher-level DHT transaction state.

## Important APIs, Types, and Functions

The file operates on types declared in `dht-common.h`: `dht_lock_t`, `dht_lock_wrap_t`, `dht_dir_transaction_t`, `dht_reaction_type_t`, and `dht_lock_type_t`. Public functions exported by `dht-lock.h` are implemented here: `dht_lock_array_free`, `dht_lock_count`, `dht_lock_new`, `dht_unlock_entrylk_wrapper`, `dht_unlock_inodelk`, `dht_unlock_inodelk_wrapper`, `dht_blocking_inodelk`, `dht_unlock_namespace`, and `dht_protect_namespace`.

Key internal helpers include `dht_lock_frame`, which clones the parent frame and assigns a unique lock owner derived from the root frame pointer; `dht_lock_request_cmp` and `dht_lock_order_requests`, which sort lock requests by subvolume name and GFID; `dht_local_entrylk_init` and `dht_local_inodelk_init`, which attach lock arrays and callbacks to `dht_local_t`; and the recursive wind/callback pairs for blocking entry locks and inode locks. `dht_lock_new` allocates from `conf->lock_pool`, duplicates the lock domain and optional basename, and deliberately fills only `loc.inode` plus GFID to avoid path based resolution races after delete and recreate.

## Control Flow

Lock acquisition is serial, not fan-out. For entry locks, `dht_blocking_entrylk` creates a lock frame, stores the sorted request array, copies the lock owner into every lock, and calls `dht_blocking_entrylk_rec` starting at index 0. Each callback marks the request locked or applies its failure policy. On unrecoverable failure it calls `dht_entrylk_cleanup`, which unlocks all already-acquired entry locks before invoking the original callback on the main frame. On success or tolerated ENOENT/ESTALE, it recurses to the next request and finally calls `dht_entrylk_done`.

The inode lock path mirrors the entry lock path with `inodelk` FOPs and `F_SETLKW` for blocking acquisition. `dht_unlock_inodelk` and the entry lock unlock helper issue unlocks only for locks marked `locked`, restore each lock's saved `lk_owner` before winding, and use `local->call_cnt` plus `dht_frame_return` to detect the last callback.

`dht_protect_namespace` composes the two lock types for one subvolume. It builds the parent loc, creates a read `inodelk` on `DHT_LAYOUT_HEAL_DOMAIN`, creates a write `entrylk` on `DHT_ENTRY_SYNC_DOMAIN` for `loc->name`, takes the parent inodelk first, and then takes the entrylk in `dht_blocking_entrylk_after_inodelk`. If entry locking fails after inode locking, it frees the entry request array and unlocks the parent layout lock before invoking the namespace callback.

## State and Persistence Behavior

Lock state is in memory only. `locked`, `lk_owner`, `op_ret`, and `op_errno` fields in `dht_lock_t` and `dht_lock_wrap_t` drive cleanup decisions. The actual locks are persisted only as live locks in lower translators and bricks via `entrylk` and `inodelk`; this file does not write durable metadata. `dht_lock_array_reset` clears ownership of arrays from a wrapper without freeing them, while `dht_lock_array_free` and `dht_lock_free` wipe locs, free duplicated strings, and return lock objects to the configured mem-pool.

## Dependencies and Integration Points

This layer depends on Gluster frame and stack primitives (`copy_frame`, `STACK_WIND_COOKIE`, `DHT_STACK_DESTROY`), DHT local allocation (`dht_local_init`), loc helpers (`dht_build_parent_loc`, `loc_gfid`, `loc_wipe`), lock owner helpers, and lower subvolume FOP tables. It logs using IDs from `dht-messages.h`, including lock allocation, unlock, and inode lock failure IDs. Callers in DHT create, rename, layout heal, and migration paths can store locks in `local->lock` or `local->current->ns` and invoke the wrappers for cleanup.

## Risks and Edge Cases

The deterministic lock ordering is critical. Any caller bypassing it or mixing differently ordered lock paths can reintroduce distributed deadlocks. Cleanup is best effort: if a frame or local cannot be allocated for unlock, the code logs that stale locks might be left. The tolerated failure policy is subtle; `IGNORE_ENOENT_ESTALE` and `IGNORE_ENOENT_ESTALE_EIO` are safe only when the higher-level operation can proceed if a target disappeared or returned EIO.

One suspicious detail is in `dht_blocking_inodelk_cbk`: the final "did any lock succeed" loop checks `!dht_lock->locked` using the current lock pointer rather than `!my_layout->locks[i]->locked`, unlike the entry lock path. That makes the all-failed test depend on the last callback's lock state and is a useful regression-test target.

## Test Signals

Useful tests should cover ordered acquisition across multiple subvolumes, partial acquisition followed by cleanup, wrapper unlock after ownership transfer, namespace protection failure after the parent lock succeeds, and tolerated ENOENT/ESTALE/EIO policy combinations. Log signals include `DHT_MSG_INODELK_FAILED`, `DHT_MSG_ENTRYLK_FAILED_AFT_INODELK`, `DHT_MSG_UNLOCKING_FAILED`, and stale-lock warnings. Runtime validation can assert no remaining brick locks after induced mid-sequence failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-lock.h -->
# Research: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-lock.h

## Purpose

`dht-lock.h` is the public interface for the DHT lock helper implementation. It exposes a small set of functions used by DHT operations that need to allocate lock descriptors, acquire or release inode locks, release entry locks, protect a namespace entry with parent and dentry locks, and count or free lock arrays.

## Important APIs, Types, and Functions

The header includes `dht-common.h`, which supplies all referenced types. `dht_lock_array_free` owns element cleanup for arrays of `dht_lock_t *`. `dht_lock_count` reports how many requests in a `dht_lock_wrap_t` are currently marked locked. `dht_lock_new` constructs one request against a target subvolume, loc, POSIX lock type, lock domain, optional basename, and failure reaction.

The unlock APIs split by lock type. `dht_unlock_entrylk_wrapper` releases entry locks stored in a wrapper and is intentionally wrapper-oriented, while `dht_unlock_inodelk` accepts an explicit callback and `dht_unlock_inodelk_wrapper` provides the cleanup wrapper form. `dht_blocking_inodelk` is the exported acquisition primitive for arrays of inode locks. `dht_unlock_namespace` releases both namespace entry locks and parent layout inode locks from a `dht_dir_transaction_t`. `dht_protect_namespace` is the high-level helper that takes the parent inodelk and then the child entrylk for one loc/subvolume pair.

## Control Flow and Integration

The header makes lock acquisition asynchronous from the caller's perspective: exported functions take callbacks matching Gluster FOP callback types, and implementation callbacks eventually invoke those callbacks on the original frame. Higher-level DHT code builds arrays of requests with `dht_lock_new`, stores them in `dht_lock_wrap_t` or `dht_dir_transaction_t`, and passes them to these helpers. Cleanup code usually calls the wrapper variants after moving arrays out of active transaction state.

## State and Persistence Behavior

No state is declared in this header. The state contract is implicit in the referenced structures: lock arrays contain per-request `locked` flags, callback pointers, request counts, and aggregate error fields. The lower translators persist live lock state while held; this interface itself is an in-memory orchestration boundary.

## Dependencies and Constraints

Because `dht-lock.h` exposes `dht_dir_transaction_t` and `struct dht_namespace`, its ABI is tightly coupled to `dht-common.h`. The lock domains named by callers, such as `DHT_LAYOUT_HEAL_DOMAIN` and `DHT_ENTRY_SYNC_DOMAIN`, must match the synchronization domain used by other DHT paths. Callers must preserve callback lifetime and must not free arrays while acquisition or unlock callbacks are outstanding.

## Risks and Test Signals

The primary risks are misuse risks: calling wrappers with uninitialized `dht_lock_wrap_t`, using mismatched callbacks, or freeing arrays before async completion. API tests should compile paths that include only this header plus `dht-common.h`, and behavioral tests should validate that namespace lock users always pair `dht_protect_namespace` with `dht_unlock_namespace`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-lock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-mem-types.h -->
# Research: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-mem-types.h

## Purpose

`dht-mem-types.h` declares DHT-specific memory accounting IDs. These IDs extend the common Gluster memory type range and let allocations in the DHT translator be tagged by structure family for diagnostics, leak reports, and memory pool/statistics tooling.

## Important APIs, Types, and Functions

The file contains one enum, `gf_dht_mem_types_`, starting at `gf_common_mt_end + 1` and ending with `gf_dht_mt_end`. Tags cover DHT layout and config objects (`gf_dht_mt_dht_conf_t`, `gf_dht_mt_dht_layout_t`), scalar allocations (`gf_dht_mt_char`, `gf_dht_mt_int32_t`, `gf_dht_mt_xlator_t`), rebalance and defrag structures (`gf_defrag_info_mt`, `gf_dht_mt_container_t`, `gf_dht_mt_miginfo_t`), inode/fd context objects, directory entries, locs, and auxiliary arrays such as node UUIDs and return caches.

## Control Flow and Integration

There is no runtime control flow in this header. It is consumed by C files that pass these enum values to `GF_CALLOC`, `GF_MALLOC`, mem-pool setup, or allocation wrappers. For example, the rebalance code uses tags such as `gf_dht_mt_container_t`, `gf_dht_mt_dirent_t`, `gf_dht_mt_loc_t`, and `gf_dht_mt_octx_t` when creating queue containers and directory crawl metadata.

## State and Persistence Behavior

The enum does not allocate or persist anything by itself. Its values become part of runtime memory accounting state in Gluster's allocator. Ordering is effectively persistent at the diagnostics ABI level: changing or reusing IDs can confuse memory reports and tooling that maps numeric IDs back to names.

## Dependencies and Constraints

The header includes `<glusterfs/mem-types.h>` and relies on `gf_common_mt_end` as the base for component-specific IDs. New DHT allocation categories should be appended before `gf_dht_mt_end`; existing values should not be reordered unless the wider project accepts the diagnostic compatibility impact.

## Risks and Test Signals

The main risk is tag drift: allocating a structure under the wrong tag makes leak reports misleading, while adding allocations without a suitable tag reduces observability. Test signals are mostly indirect: memory accounting output should classify DHT rebalance containers, locs, dirents, inode contexts, and fd contexts under the expected DHT tags during translator init, rebalance, and teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-messages.h -->
# Research: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-messages.h

## Purpose

`dht-messages.h` is the DHT translator's structured logging catalog. It declares the stable `DHT_MSG_*` message IDs through `GLFS_MSGID` and defines reusable string constants for many log messages. The file gives DHT code a common vocabulary for layout, lookup, migration, rebalance, lock, and memory failure reporting.

## Important APIs, Types, and Functions

The central macro invocation is `GLFS_MSGID(DHT, ...)`, which registers a long append-only list of message identifiers with the Gluster message ID system. The comments explicitly state the compatibility rule: append new IDs at the end, never delete or reuse old IDs, and keep the component name aligned with `glfs-message-id.h`.

The string macros cover common operational failures and status messages: subvolume selection failures, GFID mismatch or null GFID, invalid disk layout, directory self-heal and layout repair failures, migration start/complete/failure/skipped messages, hardlink migration failures, rebalance status, lock migration errors, lock/unlock failures, dictionary allocation and set failures, and namespace protection errors.

## Control Flow and Integration

There is no executable control flow, but the file is heavily integrated by calls to `gf_msg`, `gf_smsg`, `gf_log`, and debug logging throughout DHT. The researched `dht-lock.c` uses lock-specific IDs such as `DHT_MSG_LK_ARRAY_INFO`, `DHT_MSG_UNLOCKING_FAILED`, `DHT_MSG_INODELK_FAILED`, `DHT_MSG_ENTRYLK_FAILED_AFT_INODELK`, `DHT_MSG_BLOCK_INODELK_FAILED`, and allocation failure IDs. `dht-rebalance.c` uses many migration and rebalance IDs, including `DHT_MSG_MIGRATE_FILE_FAILED`, `DHT_MSG_MIGRATE_FILE_COMPLETE`, `DHT_MSG_MIGRATE_FILE_SKIPPED`, `DHT_MSG_REBALANCE_STATUS`, and `DHT_MSG_REBALANCE_STOPPED`.

## State and Persistence Behavior

Message IDs are source-level constants, but they behave like a persistent interface for logs, support tooling, and alert rules. Once emitted in field logs, ID stability matters. String macros are less rigid than IDs but still affect operator-facing diagnostics and tests that match log text.

## Dependencies and Constraints

The header depends on `<glusterfs/glfs-message-id.h>`. Message definitions must remain unique within the component. New logging sites should prefer existing IDs when semantics match and append IDs when a new failure class needs independent observability. Typos in existing strings are compatibility-sensitive because changing them may affect log consumers, even when the spelling is incorrect.

## Risks and Test Signals

The largest risk is accidental ID reuse or insertion in the middle of the macro list, which can change numeric assignments. Another risk is semantic overload, where unrelated failures reuse a broad ID and become hard to triage. Test signals include build success for all files including this header, structured log output carrying the expected DHT component IDs, and no duplicate or reordered message IDs in generated message catalogs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-rebalance.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-rebalance.c -->
