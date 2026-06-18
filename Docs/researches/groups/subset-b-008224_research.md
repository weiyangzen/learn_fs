# subset-b-008224 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/obj/auditor.py -->
# sources/object-store/openstack-swift/swift/obj/auditor.py

## Purpose
`auditor.py` implements Swift's object-auditor daemon. It walks object hash directories for every configured storage policy, opens each object through the policy-specific diskfile manager, validates object metadata and content, quarantines corrupt objects, removes stale rsync temp files, writes recon metrics, and optionally invokes object audit watcher plugins.

The file is the runtime bridge between low-level object storage in `swift.obj.diskfile` and operator-facing daemon behavior: throttling, process fan-out, progress logging, recon cache reporting, and plugin hooks.

## Important APIs, Types, And Functions
`AuditorWorker` performs the actual scan. Its constructor reads rate limits, object-size-stat buckets, watcher definitions, a `DiskFileRouter`, and a conservative `rsync_tempfile_timeout` default derived from object-replicator config when possible. `audit_all_objects()` builds one audit-location generator per policy and processes them round-robin. `object_audit()` opens a diskfile, validates metadata, streams non-zero objects to verify content, invokes watchers, handles diskfile exceptions, and removes old rsync temp files. `failsafe_object_audit()` wraps each object audit so unexpected failures increment error counters instead of killing the whole pass.

`ObjectAuditor` is the daemon class used by `run_daemon()`. It parses config such as `devices`, `concurrency`, `zero_byte_files_per_second`, `interval`, `recon_cache_path`, and watcher names. `audit_loop()` supports parent-only zero-byte scans, single-process audits, and forked per-device parallel audits. `run_forever()` repeats passes with sleeps; `run_once()` runs a bounded pass with optional device filtering.

`WatcherWrapper` isolates watcher lifecycle calls: `start(audit_type)`, `see_object(object_metadata, data_file_path)`, and `end()`. It marks a watcher unusable after initialization/start/end failures but intentionally does not disable it after a single object-level `see_object` failure. A watcher can raise `QuarantineRequest` to request quarantine of a specific object.

`main()` defines CLI options for zero-byte-only scanning and device filtering, then starts `ObjectAuditor`.

## Control Flow
The daemon begins by loading watcher entry points from `swift.object_audit_watcher` and creating an `AuditorWorker`. For each policy in `POLICIES`, the worker asks the appropriate diskfile manager for an `object_audit_location_generator()`. Those iterators are interleaved with `round_robin_iter()` so one policy cannot monopolize an entire pass.

For each `AuditLocation`, `failsafe_object_audit()` calls `object_audit()`, then the worker records timing and applies file-rate throttling. Periodic logging happens every `log_time` seconds and writes a nested recon entry keyed by auditor type and device set.

Inside `object_audit()`, the diskfile is opened with `modernize=True`, so old metadata can be upgraded by the diskfile layer. The auditor reads metadata, calls `validate_metadata()`, and quarantines if required fields are missing. Non-zero objects are streamed through `df.reader(_quarantine_hook=raise_dfq)`, which lets reader-side checksum or length mismatches propagate as `DiskFileQuarantined`. Zero-byte-only mode skips non-zero body reads and uses its own configured files-per-second rate. Watchers observe successful metadata and data-file paths after the diskfile open/read phase; `QuarantineRequest` from a watcher is converted to a diskfile quarantine.

Deletion and expiration are not fatal. `DiskFileExpired`, `DiskFileDeleted`, and `DiskFileNotExist` are swallowed. Reclaimable tombstones encountered during full audits invalidate the containing suffix hash so replication or cleanup can converge later. Any unexpected files matching the rsync-tempfile pattern are removed if older than `rsync_tempfile_timeout`.

Process orchestration is handled in `ObjectAuditor.audit_loop()`. With `concurrency == 1`, one child scans all devices. With higher concurrency, the device list is shuffled and each child gets a device subset. If zero-byte scanning is enabled, a separate zero-byte scanner child is kept running during forever mode and optionally skipped after it completes in once mode.

## State, Persistence, And Dependencies
Persistent state is indirect. Audit progress is stored by `diskfile.object_audit_location_generator()` in `auditor_status_<type>.json` files under each policy data directory, allowing future passes to resume or avoid repeatedly starting from the same partition. Recon metrics are dumped into the object recon cache file under `RECON_OBJECT_FILE`. Quarantine is delegated to diskfile managers and physically moves corrupt hash or suffix directories under a device's `quarantined` tree. Stale rsync temp files are unlinked from object directories.

Runtime counters include pass-local `passes`, `quarantines`, `errors`, `bytes_processed`, and total counters used for final pass logs. Object-size bucket counts are maintained only for the current pass and emitted as logs when configured.

Dependencies include `swift.obj.diskfile` for audit-location generation and open/read/quarantine behavior, `swift.obj.replicator` only for timeout defaults, `swift.common.storage_policy.POLICIES`, eventlet-aware `Timeout`, rate limiting via `EventletRateLimiter`, recon cache helpers, plugin loading via `load_pkg_resource`, and daemon/config helpers from `swift.common.utils`.

## Integration Points
The object server and replication layers depend on the auditor to detect corrupt local object files and quarantine them so replication/reconstruction can replace data. The diskfile layer supplies policy-specific managers, audit locations, tombstone handling, and suffix invalidation. Recon tooling consumes the emitted object-auditor stats. Watcher plugins add extensibility for site-specific checks without changing the core auditor.

`auditor.py` is also tightly coupled to diskfile exception semantics: `DiskFileQuarantined` increments quarantine counts; `DiskFileDeleted` can trigger hash invalidation; `DiskFileExpired` is ignored because expiration is handled elsewhere; and `DiskFileNotExist` is a benign race or cleanup result.

## Risks
Watcher plugins run in-process and the wrapper notes that it does not isolate hangs or file descriptor leaks. A bad watcher can therefore degrade an audit worker. Process forking assumes POSIX semantics and manually resets `SIGTERM` plus `NOTIFY_SOCKET`; it is not portable outside Swift's expected deployment model.

The progress and recon status paths are best-effort. Corrupt or unreadable status JSON falls back to scanning all partitions, while write failures only warn. Audit throughput depends on correct rate-limit configuration; overly aggressive byte or file rates can create disk pressure, while overly low zero-byte rates can delay detection. The rsync tempfile cleanup heuristic relies on naming and timeout alignment with replicator behavior.

Because `object_audit()` increments `passes` even when it sees deleted, expired, or missing diskfiles, pass counts are "locations audited" rather than "healthy live objects." Tests and operator metrics need to interpret that correctly.

## Test Signals
High-value tests should exercise `AuditorWorker.object_audit()` with diskfiles that are valid, missing, deleted, expired, metadata-invalid, length-mismatched, and reader-checksum-mismatched. Watcher tests should cover successful callbacks, initialization/start/end failure, object-level callback failure, and `QuarantineRequest`. Daemon tests should cover single-process and multi-process audit selection, zero-byte scanner behavior, device filtering, recon cache writes, stale rsync tempfile removal, and status-file clearing after a pass.

Local repository test files were not present under this vendored source tree, so concrete validation signals are inferred from Swift's object-auditor contract and the function boundaries in this file.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/obj/auditor.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/obj/diskfile.py -->
# sources/object-store/openstack-swift/swift/obj/diskfile.py

## Purpose
`diskfile.py` is Swift's reference object-storage backend for POSIX filesystems. It defines the diskfile abstraction used by the object server to create, read, update metadata for, delete, audit, replicate, and reconstruct object data. It also owns the on-disk naming format, extended-attribute metadata format, quarantine mechanics, suffix hashing, async-update persistence, and separate replicated versus erasure-coded policy behavior.

The module's public backend contract is represented by `DiskFile`, `DiskFileWriter`, and `DiskFileReader`. `DiskFileManager` and `ECDiskFileManager` are reference implementation managers that encode policy-specific behavior and are used through storage-policy dispatch.

## Important APIs, Types, And Functions
Directory helpers `get_data_dir()`, `get_async_dir()`, and `get_tmp_dir()` map a policy or policy index to policy-suffixed directory names such as `objects`, `objects-<N>`, `async_pending`, and `tmp`. Metadata helpers `_encode_metadata()`, `_decode_metadata()`, `_read_file_metadata()`, `read_metadata()`, and `write_metadata()` serialize object metadata as pickle protocol 2 in one or more xattrs under `user.swift.metadata*`, with a separate metadata checksum under `user.swift.metadata_checksum`.

Hash and cleanup helpers include `read_hashes()`, `write_hashes()`, `consolidate_hashes()`, `invalidate_hash()`, `valid_suffix()`, and `quarantine_renamer()`. These maintain `hashes.pkl` and `hashes.invalid`, track suffix invalidations for replication, and move corrupt hash or suffix directories to `quarantined/<objects-dir>/...`.

`AuditLocation` and `object_audit_location_generator()` supply auditor scan locations without selecting a specific `.data` file. `get_auditor_status()`, `update_auditor_status()`, and `clear_auditor_status()` persist auditor partition cursors in JSON status files.

`DiskFileRouter` builds one policy-specific manager per configured storage policy. `BaseDiskFileManager` implements shared manager behavior: config parsing, mount checks, suffix hashing, replication and partition locks, async pending pickle writes, diskfile construction, audit-location conversion, hash iteration, and object lookup by hash. Subclasses implement `_process_ondisk_files()`, `_update_suffix_hashes()`, and `_hash_suffix()`.

`BaseDiskFileWriter` manages temporary file creation, allocation/free-space checks, chunk writes, periodic `fdatasync`, metadata xattr writes, `fsync`, buffer-cache dropping, atomic publish via rename or `O_TMPFILE` link, suffix invalidation, obsolete-file cleanup, and partition-power relinking cleanup. `DiskFileWriter.put()` finalizes replicated `.data` writes. `ECDiskFileWriter.put()` writes fragment-index metadata and defers cleanup; `ECDiskFileWriter.commit()` renames a non-durable EC fragment to a durable filename.

`BaseDiskFileReader` provides WSGI-compatible iteration, range iteration, multi-range iteration, optional cooperative yielding, optional zero-copy `splice()` send, cache dropping, length/etag validation, and quarantine on read mismatch or EIO. `ECDiskFileReader` extends it with pyeclib fragment metadata/checksum validation.

`BaseDiskFile` represents one object path or hash directory. It opens the current valid on-disk file set, reads and merges `.data` and fast-POST `.meta` metadata, validates name/hash/content length/expiration, returns metadata and readers, creates data/meta/tombstone files, and raises Swift diskfile exceptions for missing, deleted, expired, corrupt, or colliding objects. `DiskFile` is the replicated-policy subclass. `ECDiskFile` adds fragment preferences, durable-fragment reporting, fragment maps, and `purge()` for reconstructor handoff cleanup.

`DiskFileManager` implements replicated file-set selection and suffix hash updates. `ECDiskFileManager` implements EC filename parsing/formatting, fragment-index validation, durable-fragment selection, fragment preference handling, EC-specific file-set verification, per-fragment suffix hashes, and EC suffix hashing.

## Control Flow
Object writes start with `BaseDiskFile.create()`, which yields a writer. `BaseDiskFileWriter.open()` creates either an unnamed `O_TMPFILE` in the target data directory or a named file in the policy temp directory, then checks/reserves space. `write()` streams bytes, updates the upload md5, and periodically syncs and drops cache. `put()` computes the final policy-specific filename from `X-Timestamp`, optional content-type timestamp, and optional EC fragment index; writes metadata to xattrs; fsyncs file data and metadata; invalidates the suffix hash; atomically publishes the file; optionally hard-links to the next partition-power path; then cleans obsolete files.

For replicated policies, a single newest `.data` file defines object existence, newer `.meta` files define fast-POST metadata, and `.ts` files define deletion when newer than data. For EC policies, `.data` filenames include `#<frag_index>` and may include `#d` to mark durability. EC PUT is two-phase: `put()` writes a non-durable fragment and `commit()` renames it to the durable filename. Legacy `.durable` files are still recognized.

Object reads start with `BaseDiskFile.open()`. It lists the hash directory, asks the subclass manager to choose a valid file set, raises `DiskFileNotExist` or `DiskFileDeleted` when no data file is usable, opens the selected data file, reads xattr metadata, reads any `.meta` files, merges immutable datafile metadata back over fast-POST metadata, validates the object name and directory hash, checks `X-Delete-At`, verifies content length against `fstat()`, and returns itself as a context manager. `reader()` transfers file-handle ownership to a reader object. The reader validates full-object length and optionally etag when a read starts at offset zero and reaches EOF; EC readers also validate fragment metadata at fragment boundaries.

Diskfile cleanup and replication hashing run through `cleanup_ondisk_files()`, `get_ondisk_files()`, and `_hash_suffix_dir()`. `get_ondisk_files()` parses filenames, sorts by timestamp, marks obsolete entries, retains the newest metadata and content-type metadata combinations, delegates policy-specific data-file selection, and returns chosen files plus obsolete or reclaimable candidates. Cleanup removes reclaimable tombstones and obsolete files and removes empty hash directories. Hashing walks suffix directories, cleans object directories, updates md5 state from meaningful object-state timestamps and extensions, and writes stable suffix hashes while using invalidation files and locks to avoid racing with writers.

Audit flow enters through `object_audit_location_generator()` or manager wrappers. It yields hash-directory paths by device, policy datadir, partition, suffix, and object hash, persisting partition progress into `auditor_status_<type>.json`. The auditor later converts each location into a diskfile with `from_hash_dir()`, causing metadata names to be read and checked against the hash directory.

## State, Persistence, And Dependencies
Object data is persisted as files under `<devices>/<device>/<objects-dir>/<partition>/<suffix>/<hash>/<timestamp...>.<ext>`. Replicated policy uses `.data`, `.meta`, and `.ts`. EC policy uses fragment-indexed `.data` files with optional durable markers and may see legacy `.durable` files. Metadata is persisted in extended attributes as pickled dictionaries, with a metadata checksum xattr for corruption detection and optional modernization to add missing checksums. Tombstones are zero-length temp-published files with `X-Timestamp` metadata.

Replication state is persisted in `hashes.pkl` and `hashes.invalid` in each partition. Async container-update retries are pickled under `async_pending[-policy]/<suffix>/<hash>-<timestamp>`. Audit scan state is JSON in policy data directories. Quarantine moves directories into the device's `quarantined` area and invalidates suffix hashes. Temporary writes use the policy temp directory or unnamed temp files linked into place.

Dependencies include POSIX filesystem semantics, xattrs, `fcntl`, `O_TMPFILE`/linkat support when available, Swift utility functions for hashing, locking, timestamp encoding, pickle IO, fsync/fdatasync, fallocate and free-space checks, storage policy definitions, Swift diskfile exception classes, `pyeclib` for EC validation, eventlet `tpool` and trampoline support, and Swift's multi-range response iterator.

## Integration Points
The object server calls manager `get_diskfile()` to service PUT, GET, HEAD, POST, and DELETE. Replicator and reconstructor call `get_hashes()`, `yield_hashes()`, `replication_lock()`, `partition_lock()`, `get_diskfile_from_hash()`, EC `purge()`, and EC fragment/durable metadata properties. The auditor calls `object_audit_location_generator()` and `get_diskfile_from_audit_location()`. Container-update retry code depends on `pickle_async_update()`. Storage policies select `DiskFileManager` versus `ECDiskFileManager`, and the in-memory backend in `mem_diskfile.py` duck-types a smaller version of this contract.

Metadata merge behavior integrates directly with Swift fast-POST semantics: immutable datafile metadata such as content length, deleted marker, etag, object sysmeta, and selected system metadata override user-updated `.meta` values, while content-type timestamp handling allows content type to be replicated independently from other metadata updates.

## Risks
The module relies on subtle filesystem guarantees. Bugs in rename/linkat ordering, fsync coverage, xattr writes, or hash invalidation can surface as lost writes, stale replication hashes, or inconsistent reads. `O_TMPFILE` fallback is global to the manager (`use_linkat`), so one unsupported target disables that path for later writes. Metadata pickle reading must tolerate old Python 2/3 encoding differences while avoiding checksum false positives.

On-disk file-set selection is complex, especially for EC: tombstones, `.meta` files, durable and non-durable fragments, legacy `.durable`, fragment preferences, reclaim age, and commit-window behavior interact. Small changes can cause a node to serve a non-durable fragment, incorrectly hide metadata, or prematurely reclaim data needed by reconstruction. `get_ondisk_files()` explicitly raises if the policy-specific contract is violated, which is good for detection but sensitive to edge-case regressions.

Reader-side quarantine can happen during response iteration or zero-copy send after the object server has begun streaming. Tests must account for exceptions after headers may have been prepared. EC fragment validation warns rather than quarantines for some `ECDriverError` cases, while invalid metadata/checksums quarantine; this distinction affects operational behavior.

Concurrency is lock-based and race-aware but necessarily best-effort. Hash writes compare the current `hashes.pkl` to an original snapshot and recurse on races. Audit and cleanup tolerate disappearing files by translating them to state-change or not-exist errors. Partition-power relinking introduces another path where failed hard links or cleanup can leave duplicate or stale files until later cleanup.

## Test Signals
Strong tests should cover metadata xattr round trips, metadata checksum addition and mismatch quarantine, old encoding decode paths, no-xattr and no-space error translation, policy directory naming, filename parse/format for replicated and EC policies, suffix invalidation consolidation, hash-cache race handling, quarantine moves, audit-location cursor files, and async pending pickle paths.

Diskfile behavior tests should cover PUT/read/delete lifecycles, fast-POST metadata merging, content-type timestamp precedence, tombstone precedence, expired objects with and without `open_expired`, name/hash mismatch collision handling, malformed metadata quarantine, missing/corrupt directories, cleanup of obsolete files after reclaim age, reader length/etag quarantine, range and multi-range iterators, and zero-copy send checksum paths when supported.

EC-specific tests should cover fragment-index validation, non-durable write followed by durable commit, legacy `.durable` recognition, durable fragment set selection, fragment preferences including explicit empty lists, fragment map reporting, suffix hashes by fragment index, EC reader fragment metadata validation, and `purge()` cleanup for handoff fragments and tombstones.

No local tests were present under the vendored source tree, so these signals are derived from the code's contracts and expected Swift upstream test boundaries such as object server, replicator/reconstructor, diskfile, and auditor suites.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/obj/diskfile.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/obj/expirer.py -->
# sources/object-store/openstack-swift/swift/obj/expirer.py

## Purpose
`expirer.py` implements Swift's object-expirer daemon and shared expirer configuration helpers. It scans hidden expiring-object task containers, determines which expiration tasks are due, rate-limits and parallelizes deletion of target objects, and removes completed task entries from the queue. It also supports legacy queue configuration, process sharding, delayed reaping for selected accounts or containers, async-delete task entries, recon reporting, and task-container naming.

## Important APIs, Types, And Functions
`ExpirerConfig` normalizes expirer account and container settings. It handles deprecated `expiring_objects_container_divisor` and `expiring_objects_account_name`, computes deterministic task container names with `get_expirer_container()`, validates task-container timestamps with `is_expected_task_container()`, and returns container-ring nodes with `get_delete_at_nodes()`.

`build_task_obj()` and `parse_task_obj()` encode and decode queue object names in `<timestamp>-<account>/<container>/<object>` format. `extract_expirer_bytes_from_ctype()` and `embed_expirer_bytes_in_ctype()` store object byte counts in task content types for queue monitoring. `read_conf_for_delay_reaping_times()` parses `delay_reaping_<account>` and `delay_reaping_<account>/<container>` config keys, while `get_delay_reaping()` resolves the account/container-specific delay.

`ObjectExpirer` is the daemon. Its constructor reads interval, task rate, concurrency, reclaim age, queue access, internal client, recon paths, and round-robin cache size. `_make_internal_client()` builds an `InternalClient` on the replication network. `read_conf_for_queue_access()` and `_validate_processes_config()` manage legacy queue access and process sharding.

Task discovery APIs include `iter_task_accounts_to_expire()`, `get_task_containers_to_expire()`, `_iter_task_container()`, `iter_task_to_expire()`, `round_robin_order()`, and `hash_mod()`. Execution APIs include `run_once()`, `run_forever()`, `delete_object()`, `delete_actual_object()`, `pop_queue()`, and `report()`. `main()` exposes `--processes` and `--process` CLI overrides.

## Control Flow
On startup, the daemon creates or receives an internal Swift client, determines whether the configured file is legacy `object-expirer.conf`, and decides whether to dequeue from the legacy `.expiring_objects` account. `run_forever()` sleeps a randomized initial offset, then repeatedly calls `run_once()` and sleeps a randomized remainder of `interval`.

`run_once()` validates command-line process overrides, exits early if this node is not configured to dequeue legacy tasks, creates a `GreenPool`, and iterates task accounts. For each task account, it fetches account info. If containers exist, it lists candidate task containers via `get_task_containers_to_expire()`, which stops once task-container timestamps are in the future and logs unexpected container names.

For each due task container, `_iter_task_container()` lists queue objects, parses the task object name, identifies async-delete tasks by content type, applies due-time checks and configured delayed reaping, assigns work to only one process via `hash_mod(task_container/task_object) % divisor`, and yields task dictionaries. Empty task containers are deleted. `iter_task_to_expire()` catches listing errors so one bad container does not abort the pass.

The yielded tasks are passed through `round_robin_order()` to avoid long runs against one target container, then through `RateLimitedIterator` to cap task starts per second. Each task is spawned into the green pool as `delete_object()`. That method calls `delete_actual_object()` with either async-delete headers or normal expiration headers (`X-If-Delete-At` and no queue cleaning by the object server), handles retryable responses, pops the queue entry with `direct_delete_container_entry()` after success or acceptable terminal outcomes, increments metrics, and reports progress.

## State, Persistence, And Dependencies
The expirer queue is persisted as Swift objects under the auto-created `.expiring_objects` account. Task containers are timestamp buckets, with a hash-derived offset to spread load across `EXPIRER_CONTAINER_PER_DIVISOR` shard containers per divisor window. Task object names contain the target path and delete timestamp. Task object content type can distinguish normal expiration from async delete and can embed byte-count metadata.

The daemon itself persists only recon metrics through `dump_recon_cache()` under `RECON_OBJECT_FILE`. It relies on the Swift cluster for queue persistence, target object state, and direct container-entry deletion. Runtime state includes report counters, process-sharding indexes, delay-reaping mappings, and round-robin caches.

Dependencies include `InternalClient`, Swift container-ring direct deletion, `split_path`, normalized timestamps, `RateLimitedIterator`, eventlet `GreenPool` and `sleep`, recon helpers, common HTTP status constants, and Swift config parsing helpers. The queue account prefix comes from `AUTO_CREATE_ACCOUNT_PREFIX`, so operators should not independently change it.

## Integration Points
Proxy and object-server paths that create expiring objects use `ExpirerConfig`, `build_task_obj()`, and task-container calculations to enqueue expiration work consistently. The expirer daemon consumes that queue through `InternalClient`, deletes target objects through normal Swift object DELETE calls, and removes queue entries directly from container servers. Recon tooling reads `object_expiration_pass` and `expired_last_pass`.

The daemon integrates with object-server expiration semantics through headers. Normal expiration sends `X-If-Delete-At` to ensure only the matching scheduled object is deleted and sets `X-Backend-Clean-Expiring-Object-Queue: no` so the object server does not also clean the queue. Async delete uses a different content type and looser acceptable statuses.

## Risks
Queue naming and timestamp normalization must remain compatible across proxy, object server, and expirer. Changing divisor or account settings can orphan tasks; the code warns about deprecated settings but still supports them. `parse_task_obj()` assumes task names contain the expected `-` separator and valid Swift path; malformed tasks are logged and skipped, potentially leaving bad queue entries.

Deletion retry behavior is intentionally conservative. Recent `404` or precondition failures are retried until `reclaim_age` passes, while older failures may allow queue removal. Incorrect handling can either leak queue tasks forever or remove tasks before an object is actually expired. Process sharding depends on consistent md5 modulo inputs; any change can duplicate or skip work during rolling upgrades.

Delayed reaping configuration is path-sensitive and percent-decoded. Invalid keys raise during startup. The round-robin cache can grow up to `round_robin_task_cache_size`, so very large settings trade memory for fairness. Direct queue popping bypasses proxy paths and assumes container-ring access is correct.

## Test Signals
Tests should cover task object build/parse round trips, expirer container calculation and expected-container validation, deprecated config warnings, invalid divisor/account behavior, delay-reaping parsing and lookup, content-type byte embedding/extraction, process-shard assignment, future task/container skipping, async-delete classification, empty-container deletion, round-robin fairness, rate-limited spawning, normal delete headers, async-delete headers, retry behavior for `404`, `409`, and precondition failures, queue popping, recon reporting, and CLI process override validation.

No local tests were present under this vendored source tree, so these signals are inferred from function boundaries and Swift's object-expirer behavior.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/obj/expirer.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/obj/mem_diskfile.py -->
# sources/object-store/openstack-swift/swift/obj/mem_diskfile.py

## Purpose
`mem_diskfile.py` is a sample in-memory implementation of the Swift diskfile interface. It duck-types the core `DiskFile`, `DiskFileWriter`, and `DiskFileReader` behavior needed by the object server, but stores object bytes and metadata in a Python dictionary instead of a POSIX filesystem. It is useful for lightweight testing, demonstration, and the companion in-memory object server.

## Important APIs, Types, And Functions
`InMemoryFileSystem` owns the process-local storage dictionary. `get_object()` returns a `(BytesIO, metadata)` pair or `(None, None)`. `put_object()` stores an object. `del_object()` deletes an object. `get_diskfile()` creates a `DiskFile`. `pickle_async_update()` is a no-op because this backend does not persist async container updates.

`DiskFileWriter` buffers a PUT into a new `io.BytesIO`, updates upload size and md5 in `write()`, reports `(upload_size, etag)` from `chunks_finished()`, stores metadata plus `name` into the in-memory filesystem in `put()`, and has a no-op `commit()`.

`DiskFileReader` wraps a `BytesIO` and implements full-object iteration, single-range iteration, multi-range iteration via `multi_range_iterator`, close-time length and etag validation, and quarantine recording through `was_quarantined`. It does not physically move data on quarantine.

`DiskFile` represents one object name. `open()` fetches the in-memory object, verifies metadata, expiration, content length, and path/name match, and returns itself. `get_metadata()`, `get_datafile_metadata()`, and `get_metafile_metadata()` return the same metadata dictionary. `reader()` transfers the buffer to a `DiskFileReader`. `create()` yields a writer. `write_metadata()` applies fast-POST-like metadata updates while preserving immutable datafile metadata and object sysmeta. `delete()` removes an object if the provided timestamp is newer than stored metadata. Timestamp and content-type properties mirror the disk backend.

## Control Flow
PUT-like flows call `DiskFile.create()`, receive an opened `DiskFileWriter`, write chunks, then call `put(metadata)` to store the completed `BytesIO` and metadata under the full `/account/container/object` name. If `put()` is not called before the context closes, the buffered data is discarded.

GET/HEAD-like flows call `open()`. Missing objects raise `DiskFileDeleted`. Existing objects are checked for required `name` and `Content-Length` metadata, optional integer `X-Delete-At`, name/path collision, expiration, and actual buffer length. `reader()` then returns an iterator that reads the buffer, optionally validates md5 when read from offset zero through EOF, and clears its file pointer on close.

POST-like flows call `write_metadata()`, which fetches existing data and metadata, preserves reserved datafile metadata (`content-length`, `deleted`, `etag`), datafile system metadata, and object sysmeta, sets the canonical `name`, and replaces metadata in the store. DELETE removes the entry only when the existing `X-Timestamp` is older than the delete timestamp; it does not write tombstones.

## State, Persistence, And Dependencies
All state is process-local and volatile in `InMemoryFileSystem._filesystem`. Values are `(BytesIO, metadata)` pairs keyed by full object name. There are no directories, xattrs, hashes, tombstones, async updates, replication locks, recon outputs, or durable EC markers. Expiration is enforced on open by checking `X-Delete-At` against current time.

Dependencies are intentionally narrow: `io.BytesIO`, `time`, `contextmanager`, Swift timestamp and md5 helpers, diskfile metadata constant sets, `is_sys_meta()`, Swift diskfile exceptions, `Timeout`, and `multi_range_iterator`.

## Integration Points
`mem_server.py` uses `InMemoryFileSystem` as the storage backend for an in-memory object server. The class and method names match enough of `swift.obj.diskfile` for object-server code paths to exercise PUT, GET, HEAD, POST, and DELETE behavior without a real device tree.

The backend borrows metadata rules from `diskfile.py` by importing `DATAFILE_SYSTEM_META` and `RESERVED_DATAFILE_META`, so fast-POST immutability rules stay aligned with the reference backend.

## Risks
This implementation is not durable, not thread-safe beyond ordinary Python object behavior, and not semantically complete compared to `diskfile.py`. Deletes remove entries rather than writing tombstones, quarantine deletes the in-memory entry rather than preserving evidence, async updates are dropped, and replication support is absent. `DiskFileReader.app_iter_range()` yields an overlong final chunk using `chunk[:length]` after `length` is negative, matching the file's current logic but requiring careful tests for range truncation.

Because `BytesIO` objects are stored directly and reused, callers that retain references could observe shared mutable state. Metadata dictionaries are also stored by reference unless callers copy them. This is acceptable for a sample/test backend but risky for production-like use.

## Test Signals
Tests should cover create/write/put/read round trips, metadata validation failures, expiration handling, path collision, length mismatch quarantine, etag mismatch quarantine, metadata update preserving immutable keys and sysmeta, timestamp-based delete behavior, missing-object exceptions, range and multi-range iteration, and no-op async update behavior. Tests should also assert that state disappears across new `InMemoryFileSystem` instances because persistence is intentionally absent.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/obj/mem_diskfile.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/obj/mem_server.py -->
# sources/object-store/openstack-swift/swift/obj/mem_server.py

## Purpose
`mem_server.py` provides a minimal in-memory Swift object server WSGI application. It subclasses the normal object server controller and overrides storage setup so object data is backed by `mem_diskfile.InMemoryFileSystem` rather than on-disk devices.

## Important APIs, Types, And Functions
`ObjectController` subclasses `swift.obj.server.ObjectController`. `setup(conf)` creates an `InMemoryFileSystem` and sets `fallocate_reserve` to zero. `get_diskfile()` ignores device and partition storage details and returns a memory-backed diskfile for the account/container/object path. `REPLICATE()` is present but unimplemented. `app_factory()` is the paste.deploy entry point that merges global and local config and returns an `ObjectController`.

## Control Flow
Paste deployment calls `app_factory()`, which builds controller config and instantiates `ObjectController`. The base controller initialization calls `setup()`, which installs the in-memory filesystem. Object-server request handlers inherited from `swift.obj.server.ObjectController` call `get_diskfile()` during normal REST operations; this subclass returns a `mem_diskfile.DiskFile` backed by the shared process-local filesystem.

Replication requests reach `REPLICATE()` but receive no implementation from this module. The method body is `pass`, so replication hash exchange is intentionally unsupported.

## State, Persistence, And Dependencies
Server state is a single `InMemoryFileSystem` instance attached to the controller as `_filesystem`. Object data and metadata live only for the lifetime of the process. There is no device mount checking, partition directory state, async pending persistence, suffix hash persistence, recon state, or replication state. `fallocate_reserve` is set to zero because the memory backend does not reserve disk space.

Dependencies are `swift.obj.mem_diskfile.InMemoryFileSystem` and `swift.obj.server.ObjectController`.

## Integration Points
This module plugs the memory diskfile backend into Swift's WSGI object-server interface. It is aligned with the reference diskfile backend because object operations still go through the inherited object controller, but storage calls are redirected to `mem_diskfile`. It is primarily a test/demo alternative backend rather than a production storage node.

## Risks
All data is volatile and local to one process. Any restart loses objects. REPLICATE is a stub, so replicator-driven consistency, suffix hashes, handoff behavior, and object reconstruction are unavailable. Because device and partition arguments are ignored, code paths that need realistic mount, policy, or partition behavior will not be exercised by this server.

## Test Signals
Tests should confirm the WSGI factory merges config, `setup()` installs a fresh filesystem, inherited object operations can PUT/GET/POST/DELETE through the memory diskfile, data is shared within one controller instance, separate controller instances do not share state, and REPLICATE remains unsupported or returns the base framework's expected empty response behavior.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/obj/mem_server.py -->
