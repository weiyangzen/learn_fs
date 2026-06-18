# Research Group: subset-b-008264

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/iam/src/sys.rs -->
# sources/object-store/rustfs/crates/iam/src/sys.rs

Purpose: this is the high-level IAM facade over `IamCache<T: Store>`. It exposes user, group, policy, service-account, temporary-account, cache reload, notification, and authorization operations. It also owns the global OPA authorization plugin slot and role-to-policy map used by STS/service-account role claims.

Important APIs and types: `IamSys<T>` wraps the cache/store and has public CRUD methods such as `set_policy`, `delete_policy`, `create_user`, `delete_user`, `new_service_account`, `update_service_account`, `set_temp_user`, `policy_db_get`, and `policy_db_set`. `PreparedIamAuth` and private `PreparedIamMode` split authorization into a prepare phase and an evaluate phase. `PreparedSessionPolicy` represents absent, invalid/deny-all, or parsed session policy. `NewServiceAccountOpts` and `UpdateServiceAccountOpts` describe service account mutation input. Constants define status strings, JWT claim keys, and `MAX_SVCSESSION_POLICY_SIZE`.

Control flow: construction spawns a Tokio task to load OPA config and install an `AuthZPlugin` in a `OnceLock<Arc<RwLock<Option<_>>>>`. Administrative methods mostly validate inputs, delegate persistence/cache mutation to `self.store`, and notify peers through `rustfs_ecstore::notification_sys` when no watcher is configured. Notifications for user, group, and service-account loads are fire-and-forget tasks to avoid blocking IAM mutations. Authorization flows through `prepare_auth`: owner bypass, OPA mode, service-account lookup, temp-account lookup, then regular-user policy merge. `eval_prepared` reuses merged policies and session policy parsing. STS auth can source policies from role ARN, parent-user policy mappings and groups, or safe JWT `policy` claim names. Service accounts verify the `parent` claim, evaluate parent policy under parent account args, and optionally intersect with embedded session policy.

State and persistence: durable state is handled by the underlying `Store` via `IamCache`: policy docs, mapped policies, users, temp users, service accounts, groups, group memberships, status, SSH keys, and JWT-backed credentials. This file also mutates process-global OPA plugin state. Credential read APIs redact secret keys and session tokens before returning. Service-account creation writes session policy and policy type into JWT metadata and optionally an `exp` claim.

Dependencies and integration: depends on `rustfs_credentials`, `rustfs_policy`, `rustfs_madmin`, `rustfs_ecstore` notifications, `serde_json`, `time`, Tokio locks/tasks, tracing, and local manager/store/cache utilities. `Args` from the policy crate is the authorization contract shared with S3/admin paths.

Risks: the OPA plugin is process-global and initialized asynchronously, so startup races can temporarily evaluate without OPA if callers reach auth before setup completes. `get_temporary_account` has a retry-looking block that returns the first error after the match, so the retry result is not used. Authorization is security-critical and depends on safe parsing of untrusted JWT policy names and base64 session policy text. `roles_map` is only initialized empty here, so role ARN behavior depends on external population not shown in this file. Notification failures are logged but not surfaced.

Test signals: the embedded test module is extensive. It covers prepared policy views, service account expiration claims, STS/service-account authorization, group fallback, JWT claim policy sanitization, deny-only session policies, ExistingObjectTag detection, notification cache updates, deleted-user cleanup, `check_key` load failures, and policy info JSON shape.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/iam/src/sys.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/iam/src/utils.rs -->
# sources/object-store/rustfs/crates/iam/src/utils.rs

Purpose: compact JWT helper module for IAM credentials and session tokens.

Important APIs: `generate_jwt<T: Serialize>` signs arbitrary serializable claims with HS512. `extract_claims<T: DeserializeOwned + Clone>` verifies and decodes HS512 tokens using normal jsonwebtoken validation. `extract_claims_allow_missing_exp<T>` verifies HS512 while clearing `required_spec_claims`, allowing tokens without an expiration claim.

Control flow and state: all functions are pure wrappers around `jsonwebtoken` and keep no local state. Encoding builds a `Header` with `Algorithm::HS512` and an `EncodingKey` from the secret bytes. Decoding builds a `DecodingKey` from the same secret and validates the signature/claims. The missing-exp variant changes validation requirements before calling decode.

Dependencies and integration: used by IAM `sys.rs` and manager utilities to create and parse service-account and STS credential JWTs. It depends on `jsonwebtoken`, `serde`, and `HashSet`.

Risks: secrets are raw shared HMAC keys, so callers must protect secret material and choose sufficient entropy. The missing-exp decoder is intentionally permissive and should only be used for account types that allow non-expiring tokens. Algorithms are fixed to HS512, which is simple but means all issuers/verifiers need symmetric secret access.

Test signals: unit tests cover token shape, different secrets/claims producing different tokens, valid decode, wrong secret failure, invalid token failure, round-trip header algorithm, empty claims, and special characters.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/iam/src/utils.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/Cargo.toml -->
# sources/object-store/rustfs/crates/io-core/Cargo.toml

Purpose: crate manifest for `rustfs-io-core`, described as zero-copy reader and writer implementations for RustFS.

Important configuration: package metadata inherits version, edition, license, repository, rust-version, and homepage from the workspace. The crate disables doctests for the library. Keywords and categories position the crate around zero-copy readers/writers and filesystem tooling.

Dependencies: runtime dependencies are `bytes`, `thiserror`, `tokio` with `io-util`, `fs`, `rt`, and `sync`, `memmap2`, and `rustfs-io-metrics`. A Linux-specific target dependency enables Tokio's `io-uring` feature. Dev dependencies enable Tokio `rt-multi-thread` and `macros` for async tests.

Integration points: this manifest makes `io-core` a low-level crate with limited dependencies, suitable for reuse by storage and object paths without pulling in higher-level RustFS crates. Metrics integration is explicit through `rustfs-io-metrics`.

Risks: Linux `io-uring` is enabled as a target-specific Tokio feature, but the listed researched `direct_io.rs` implementation uses synchronous `FileExt::read_at`, not io-uring. The crate description emphasizes zero-copy, while some implementation paths copy mmap/file data into `Bytes`, so downstream users should rely on concrete APIs rather than the manifest description alone.

Test signals: Tokio async testing support is enabled, and the researched modules contain many unit tests. Doctests are disabled, so example snippets in docs are not compiled by `cargo test --doc`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/examples/scheduler_example.rs -->
# sources/object-store/rustfs/crates/io-core/examples/scheduler_example.rs

Purpose: demonstration binary for the public `rustfs-io-core` scheduler, buffer sizing, backpressure, deadlock detector, and lock optimizer APIs.

Important functions: `main` runs five examples. `io_scheduler_example` constructs an `IoSchedulerConfig`, creates an `IoScheduler`, and prints buffer choices for several file size, sequential/random, and media combinations. `buffer_size_example` demonstrates `calculate_optimal_buffer_size` and `get_buffer_size_for_media`. `backpressure_example` shows `BackpressureMonitor::with_defaults`, state checking, `try_acquire`, `release`, and counters. `deadlock_detection_example` registers locks, records holders and waits, and prints cycle detection. `lock_optimizer_example` records five synthetic lock acquisitions/releases and prints statistics.

Control flow and state: this is synchronous example code with stdout output only. It does not run real I/O; it simulates scenarios and lock events.

Dependencies and integration: imports the crate's public re-exports plus `StorageMedia` from `io_profile`. It validates that the library facade in `lib.rs` is usable from an external crate context.

Risks: examples can imply operational behavior stronger than the modules provide. The deadlock simulation records waits after both locks are held and should demonstrate cycle detection, but it does not model real thread IDs from runtime primitives. The scheduler example relies on functions from `scheduler.rs`, which is outside this work item.

Test signals: no assertions; this is a compile/run smoke example. Useful as API documentation, not correctness coverage.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/examples/scheduler_example.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/src/backpressure.rs -->
# sources/object-store/rustfs/crates/io-core/src/backpressure.rs

Purpose: lightweight concurrency backpressure monitor for I/O operations.

Important APIs/types: `BackpressureConfig` defines `max_concurrent`, high/low water marks, cooldown, and enable flag. `BackpressureState` is `Normal`, `Warning`, or `Critical`. `BackpressureMonitor` exposes `try_acquire`, `release`, counters, rejection rate, state, and `should_apply_backpressure`.

Control flow: `try_acquire` uses a compare-exchange loop on `current` so enabled mode never exceeds `max_concurrent` under contention. It increments processed on successful acquisition and rejected at capacity. State transitions use mutex-protected `state` and `last_state_change`; critical/active is reached near the high threshold, warning near low threshold. `release` decrements `current` and clears active when count drops near the low threshold. Disabled mode bypasses the cap and always increments current/processed.

State and persistence: all state is in memory: atomic counters, an atomic active flag, and mutexes for state and last transition time. There is no RAII permit type, so callers must release manually.

Dependencies and integration: pure standard library plus `thiserror`; re-exported from `lib.rs`. It is demonstrated by the scheduler example.

Risks: manual `release` creates leak/underflow risk if callers forget or double-release; `fetch_sub` on zero would wrap. State updates compare against the pre-increment value, so thresholds can be off by one. `cooldown` is only consulted by `should_apply_backpressure`, not by `try_acquire`, so it is advisory. Disabled mode can grow `current` without capacity bounds.

Test signals: tests validate config thresholds, invalid config, acquire/reject behavior, rejection rate, and disabled always-allow behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/src/backpressure.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/src/bufreader_optimizer.rs -->
# sources/object-store/rustfs/crates/io-core/src/bufreader_optimizer.rs

Purpose: helper for choosing `tokio::io::BufReader` capacities and tracking buffering statistics.

Important APIs/types: `BufReaderConfig` configures max layers and small/large buffer sizes. `BufReaderStats` stores atomic totals for readers, eliminated layers, and buffer size adjustments. `BufReaderOptimizer` provides `optimal_buffer_size`, `optimize`, `stats`, `config`, `is_buffered_source`, and `eliminate_redundant_layers`. `BufferedSource` is a marker trait for sources considered already buffered.

Control flow: `optimal_buffer_size` chooses the large buffer when `data_size >= large_file_threshold`, otherwise the small buffer. `optimize` increments `total_readers` and returns `BufReader::with_capacity`. Redundant-layer removal is currently a no-op that returns the reader unchanged.

State and persistence: only in-memory atomic counters; no persistence. The optimizer is immutable after construction except stats.

Dependencies and integration: uses Tokio `AsyncRead` and `BufReader`, and is re-exported from `lib.rs`. It is intended for data paths deciding whether/how much to buffer around async readers.

Risks: `max_layers`, `buffer_size_adjustments`, and `eliminated_layers` are not functionally used yet, so the module name overstates current behavior. The marker trait can only prove buffering for types that explicitly implement it; there is no runtime detection of existing `BufReader` layers.

Test signals: tests cover default/custom config, small/large/unknown size decisions, actual async read through an optimized reader, and total reader stat tracking.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/src/bufreader_optimizer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/src/config.rs -->
# sources/object-store/rustfs/crates/io-core/src/config.rs

Purpose: central configuration types for scheduler and priority queue behavior.

Important APIs/types: `IoSchedulerConfig` covers concurrent read limits, size-based priority thresholds, per-priority queue capacities, starvation/load timing, feature flags for detection/monitoring/adaptive buffering, and base/min/max buffer sizes. `ConfigError` reports invalid values. `IoPriorityQueueConfig` is a smaller queue-specific projection with capacities and starvation durations.

Control flow: defaults set conservative capacities and enable priority scheduling, storage/sequential detection, bandwidth monitoring, and adaptive buffers. `validate` enforces positive concurrency, high priority size threshold lower than low threshold, and coherent buffer min/base/max. Builder helpers mutate selected groups of fields. Duration helpers convert millisecond/second scalar fields to `Duration`. `IoPriorityQueueConfig::from_scheduler_config` adapts scheduler config into queue config.

State and persistence: plain cloneable structs only; no runtime state or persistence.

Dependencies and integration: standard `Duration` and `thiserror`; consumed by `io_priority_queue`, `scheduler`, examples, and public re-exports.

Risks: validation does not check queue capacities, load sample window, waterline semantics, or zero buffer sizes beyond min/base/max relationships. Builder helpers do not validate immediately, so callers must remember to call `validate`.

Test signals: tests cover default validity, invalid concurrency/threshold/buffer configurations, builder mutation, queue config conversion, and duration helpers.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/src/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/src/deadlock_detector.rs -->
# sources/object-store/rustfs/crates/io-core/src/deadlock_detector.rs

Purpose: in-memory wait-for graph tracker for detecting potential lock deadlocks and long-held locks.

Important APIs/types: `LockType` classifies mutex/rwlock/semaphore locks. `LockInfo` tracks lock id, type, owner thread id, waiters, and acquisition time. `WaitGraphEdge` connects a waiting thread to the thread holding the desired lock. `DeadlockDetectorConfig` controls interval, hold-time warning threshold, and enablement. `DeadlockDetector` registers locks, records acquire/release/wait events, detects cycles, tracks request IDs, and exposes lock/request counts.

Control flow: registered locks receive monotonically increasing IDs under a mutex. `record_acquire` sets owner/acquisition time, removes that waiter from the lock, and removes the wait edge for that lock/thread. `record_wait` adds waiter IDs and, if there is a different owner, pushes a wait graph edge. `detect_deadlock` builds an adjacency map and uses DFS with visited and recursion-stack sets to return a cycle path. `check_long_held` scans registered held locks for durations over `max_hold_time`.

State and persistence: all state is process-local behind `std::sync::Mutex`: locks, graph edges, request map, and next id. It is diagnostic state only.

Dependencies and integration: pure std, re-exported from `lib.rs`, and used in the scheduler example. The caller must instrument real locks with IDs and thread IDs.

Risks: stale wait edges can remain if callers fail to record acquire/release/unregister, causing false positives. Duplicate wait edges are not deduplicated. Poisoned mutex handling is inconsistent: some methods ignore lock failures while `lock_count` recovers poison. No background interval runner exists despite `detection_interval`.

Test signals: tests cover lock registration, acquire/release, request tracking, no-deadlock path, and disabled detector. There is no direct positive cycle test in the unit tests, though the example exercises one.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/src/deadlock_detector.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/src/direct_io.rs -->
# sources/object-store/rustfs/crates/io-core/src/direct_io.rs

Purpose: aligned position-based file reader named `DirectIoReader`; comments explicitly clarify it is aligned `pread`/`read_at`, not true `O_DIRECT`.

Important APIs/types: `DirectIoError` reports unsupported platform/file, I/O string errors, or alignment failures. On Linux, `DirectIoReader::new(file, offset, size)` validates 512-byte offset and size alignment and builds an `AsyncRead` reader over a sync `std::fs::File`. Non-Linux builds expose the same type but constructor always returns `UnsupportedPlatform`.

Control flow: Linux `read_chunk` lazily fills an internal buffer from the requested position using `std::os::unix::fs::FileExt::read_at`, advances `pos` and `remaining`, then copies from internal buffer into caller buffers. `poll_read` repeatedly drains chunks into Tokio's `ReadBuf` and returns ready immediately.

State and persistence: reader state is per-instance file handle, current position, remaining byte count, internal buffer and buffer cursor. It does not mutate the underlying file offset.

Dependencies and integration: uses standard file APIs and Tokio `AsyncRead`; Linux-only re-export in `lib.rs`. It can be consumed wherever an async reader is expected, but it performs blocking reads in `poll_read`.

Risks: despite the type name, it does not open with `O_DIRECT` and does not ensure true direct I/O. `poll_read` performs synchronous disk I/O, which can block an async executor worker. Internal `Vec<u8>` is not guaranteed 512-byte memory-aligned, though comments mention buffer address alignment. Subtracting `remaining -= n` assumes `read_at` never returns more than requested aligned buffer length and remaining. Tests use `/dev/zero`, which is Linux-specific but guarded.

Test signals: unit test checks valid and invalid alignment on Linux and unsupported platform behavior elsewhere.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/src/direct_io.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/src/io_priority_queue.rs -->
# sources/object-store/rustfs/crates/io-core/src/io_priority_queue.rs

Purpose: three-lane I/O request queue with high, normal, and low priorities plus simple starvation prevention.

Important APIs/types: `IoRequest` records id, `IoPriority`, size, queued time, and sequential flag. `IoQueueStatus` reports count, total size, oldest wait, and processed count. `IoPriorityQueue` provides `enqueue`, `dequeue`, `status`, `total_status`, `peek`, `clear`, and config access.

Control flow: `enqueue` increments `next_id`, creates a request, and pushes it to the matching `VecDeque` only if that queue is below capacity. `dequeue` prefers high, then normal, then low unless lower-priority queues are starved based on `last_dequeue` and `starvation_threshold`. Successful dequeue updates `last_dequeue` and processed stats for that priority. Status methods aggregate current queue contents and processed counters.

State and persistence: in-memory queues, ID counter, last-dequeue timestamps, and stats. No persistence or synchronization; callers must wrap it if used across threads.

Dependencies and integration: consumes `IoPriority` from `scheduler` and `IoPriorityQueueConfig` from `config`; re-exported through `lib.rs`.

Risks: `enqueue` returns an ID even if the queue is full and the request was dropped, so callers cannot distinguish accepted vs rejected requests. Starvation detection only starts after a priority has been dequeued once; a never-served low queue can fail to look starved. `total_status.oldest_wait` checks high before normal before low rather than the true oldest across queues. `peek` ignores starvation rules and always returns high before normal before low.

Test signals: tests cover priority order, status aggregation, capacity drop effect, clear, and peek non-removal.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/src/io_priority_queue.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/src/io_profile.rs -->
# sources/object-store/rustfs/crates/io-core/src/io_profile.rs

Purpose: storage-media and access-pattern helpers for adaptive scheduling and buffer sizing.

Important APIs/types: `StorageMedia` parses/prints `Nvme`, `Ssd`, `Hdd`, `Unknown`. `AccessPattern` identifies sequential/random/mixed/unknown with helper predicates. `StorageProfile::for_media` maps media to buffer caps and multipliers. `IoPatternDetector` records `(offset, len)` history and classifies the current access pattern. `detect_storage_media` honors override strings and otherwise uses platform-specific detection.

Control flow: `IoPatternDetector::record` keeps a bounded history. `current_pattern` compares consecutive offsets against previous end plus tolerance and counts sequential versus random transitions. Linux detection checks `/sys/class/nvme` and a small fixed set of `/sys/block/*/queue/rotational` devices. macOS detection shells out to `diskutil info /`; other platforms return unknown.

State and persistence: detector state is in-memory `VecDeque` history. Storage detection reads OS files or command output but does not persist results.

Dependencies and integration: standard library only. The scheduler and example use these types to pick buffer sizes and behavior.

Risks: Linux detection samples only common device names and does not map a specific data path to its backing device, so container/multi-disk systems may be misclassified. macOS defaults to SSD for modern systems if no explicit signal appears. Pattern detection is local and sensitive to chosen history size/tolerance.

Test signals: tests cover override parsing, disabled detection, pattern classifications, helper predicates, storage profile values, and platform detection smoke tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/src/io_profile.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/src/lib.rs -->
# sources/object-store/rustfs/crates/io-core/src/lib.rs

Purpose: crate root and public facade for RustFS I/O core modules.

Important APIs: declares modules for backpressure, buffering, config, deadlock detection, direct I/O, priority queue, profiling, lock optimization, pool, reader, scheduler, shared memory, timeout wrapper, and writer. Re-exports the main public types such as `BytesPool`, `PooledBuffer`, `ZeroCopyObjectReader`, `ZeroCopyObjectWriter`, scheduler types/functions, `BackpressureMonitor`, `DeadlockDetector`, `LockOptimizer`, and timeout helpers. `DirectIoReader` is re-exported only on Linux.

Control flow and state: no runtime logic; this file controls public API shape and documentation.

Dependencies and integration: the module tree shows `io-core` as the shared lower-level I/O support crate. The example imports many items through these re-exports.

Risks: broad re-exports make API compatibility sensitive to internal module changes. Documentation says mmap zero-copy is a feature, but some reader paths copy into `Bytes`; public docs should stay aligned with implementation details.

Test signals: no direct tests. Compile coverage comes from module tests and external example usage.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/src/lock_optimizer.rs -->
# sources/object-store/rustfs/crates/io-core/src/lock_optimizer.rs

Purpose: instrumentation and adaptive spin helper for lock-heavy paths.

Important APIs/types: `LockOptimizeConfig` enables/disables tracking, sets acquire timeout, max hold warning threshold, adaptive spin flag, and max spin iterations. `LockStats` records acquisitions, early releases, total/max hold time, contentions, and spin successes/failures. `LockOptimizer` exposes event hooks, `try_spin`, stats/config access, spin count, hold-time warning check, and reset. `LockGuard` is an RAII helper that records acquire on construction and release on drop.

Control flow: `try_spin` loads current spin count, repeatedly calls a caller-provided nonblocking acquire closure, issues `std::hint::spin_loop` on failure, records success/failure, and doubles/halves future spin count within bounds. Release tracking records duration and counts releases shorter than half the configured acquire timeout as early.

State and persistence: all metrics are in-memory atomics. `current_spin` is per optimizer instance.

Dependencies and integration: pure std; re-exported from `lib.rs` and demonstrated in the scheduler example.

Risks: this module does not acquire locks itself; correctness depends on callers placing hooks accurately. Adaptive spinning can burn CPU if used around locks that are not expected to become available quickly. Early release semantics are based on `acquire_timeout / 2`, which may not represent meaningful lock-hold quality. Average hold time divides total release duration by acquisitions, so unmatched acquire/release calls distort metrics.

Test signals: tests cover stats math, contention and spin rates, RAII guard duration tracking, adaptive spin changes, and disabled optimizer no-op behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/src/lock_optimizer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/src/pool.rs -->
# sources/object-store/rustfs/crates/io-core/src/pool.rs

Purpose: tiered reusable `BytesMut` buffer pool to reduce allocation churn in zero-copy-ish I/O paths.

Important APIs/types: `BytesPool` owns small, medium, large, and xlarge `PoolTier`s plus shared `BytesPoolMetrics`. `BytesPoolConfig` configures per-tier buffer sizes and max concurrent buffers. `PooledBuffer` derefs to `BytesMut` and returns its buffer to the tier on drop. Public methods include `new_tiered`, `with_config`, async `acquire_buffer`, nonblocking `try_acquire_buffer`, `metrics`, `hit_rate`, and `available_buffers`.

Control flow: size selection uses fixed thresholds: <=64 KiB small, <=512 KiB medium, <=4 MiB large, otherwise xlarge. A tier uses a Tokio semaphore to bound concurrent buffers, pops from `available_buffers` when possible, clears/reserves reused buffers, otherwise allocates `BytesMut::with_capacity(max(requested, tier_size))`. Drop takes the `ManuallyDrop<BytesMut>` and returns it to the tier if there is one, retaining it while the available vector is below `max_buffers`; otherwise the buffer is dropped and current allocated byte counters are decremented.

State and persistence: all state is in memory: semaphores, available buffer vectors protected by mutexes, and atomic metrics. Metrics are also emitted through `rustfs_io_metrics`.

Dependencies and integration: uses `bytes::BytesMut`, Tokio semaphore permits, atomics/mutexes, and `rustfs-io-metrics`. Re-exported from `lib.rs`.

Risks: `available_buffers` metric increments on return but is not decremented on take, so it can overstate currently available buffers. Async acquire falls back to an unpooled buffer if the semaphore is closed and does not record normal metrics for that path. Holding the metrics mutex only to unwrap an Arc adds overhead without much protection. Returned buffers keep their capacity, which improves reuse but can retain large memory in a tier.

Test signals: tests cover tier defaults, capacity selection, semaphore-closed fallback, try-acquire capacity failure, metrics presence, hit rate, available buffer count, reuse without additional allocation, allocated byte tracking, and tier hit counters.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/src/pool.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/src/reader.rs -->
# sources/object-store/rustfs/crates/io-core/src/reader.rs

Purpose: `Bytes`-backed async reader for object data, with constructors for in-memory data and file ranges.

Important APIs/types: `ZeroCopyReadError` covers I/O, mmap, and invalid range errors. `ZeroCopyObjectReader` stores a `Bytes` and current position. Constructors are `from_bytes`, Unix `from_file_mmap_path`, Unix/non-Unix `from_file_mmap`, plus accessors `remaining_bytes`, `len`, `is_empty`, and `position`. It implements Tokio `AsyncRead`.

Control flow: `from_bytes` wraps an existing `Bytes` without copying. Unix `from_file_mmap_path` opens a file in `spawn_blocking`, creates a `memmap2` mapping for the requested range, then copies the mapped slice into owned `Bytes`. `from_file_mmap` clones/seeks/reads the Tokio file into a `Vec` and converts it to `Bytes`; the non-Unix fallback does the same. `poll_read` copies from the current `Bytes` slice into `ReadBuf`, advances `pos`, and returns ready.

State and persistence: per-reader immutable bytes plus mutable cursor position. No persistence.

Dependencies and integration: uses `bytes`, Tokio async read/seek/file APIs, and `memmap2` for the path-based Unix constructor. Re-exported from `lib.rs`.

Risks: the file constructors are not truly zero-copy because they copy mapped/read data into `Bytes`; docs partially acknowledge the path-based copy but still advertise mmap zero-copy. `InvalidRange` is defined but not used. Reading exact `size` bytes fails if the file is shorter. `poll_read` assumes `self.pos <= self.data.len()`, which holds internally unless future APIs mutate state.

Test signals: tests cover reading from bytes, remaining bytes, position after read, and empty/non-empty state. File-backed constructors are not covered here.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/src/reader.rs -->
