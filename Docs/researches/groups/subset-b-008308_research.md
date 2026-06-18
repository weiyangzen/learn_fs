# Research Report: subset-b-008308

Grouped research for CryFS blockstore low-level implementations, integrity state, overhead helpers, and shared high/low-level test fixtures. Each section preserves the original source path for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/integrity/integrity_data/known_block_versions.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/integrity/integrity_data/known_block_versions.rs

## Purpose
This file implements the local integrity ledger used by `IntegrityBlockStore`. It remembers, per block and per client, which block versions have already been observed so that rollback, deletion/reintroduction, and stale-client version attacks can be detected across operations and across process restarts.

## Important APIs, Types, and Functions
- `ClientId` wraps a `NonZeroU32` and is serialized both with `binrw` and `binary_layout`; `0` is reserved for the deleted-block sentinel in `MaybeClientId`.
- `ClientId::generate_random()` creates a random nonzero client id through `rand::rng().random()` into `NonZeroU32`; construction depends on `NonZeroU32` deserialization semantics.
- `MaybeClientId` is either `ClientId(ClientId)` or `BlockWasDeleted`; custom `BinRead`/`BinWrite` encodes `BlockWasDeleted` as integer `0`.
- `BlockVersion` wraps a `u64`, supports `increment()`, and maps to binary-layout `u64`.
- `BlockInfo` is the per-block state: `last_update_client_id` plus `known_block_versions: HashMap<ClientId, BlockVersion>`.
- `BlockInfo::start_increment_version_transaction()` returns `BlockVersionTransaction`, a must-commit-or-cancel RAII transaction used before writes.
- `BlockInfo::check_and_update_version()` validates a read block's `(client_id, version)` against local state and emits `IntegrityViolationError::RollBack` on rollback-like transitions.
- `KnownBlockVersions` owns `integrity_violation_in_previous_run: AtomicBool` and an `Arc<LockableHashMap<BlockId, BlockInfo>>`.
- `KnownBlockVersions::load`, `load_or_default`, and async `save` bridge this live state to `KnownBlockVersionsSerialized`.
- `KnownBlockVersions::lock_block_info()` returns an owned async lock guard for a single block id; callers mutate block integrity state under that guard.

## Control Flow
Write paths call `start_increment_version_transaction()`, derive the next version for the current client from the local map, and later either `commit()` or `cancel()`. Commit updates both `last_update_client_id` and the client-version entry; cancellation drops the pending mutation. The transaction `Drop` panics through `safe_panic!` if neither action was taken, making incomplete write protocol violations visible.

Read paths call `check_and_update_version()`. First observations for a client insert the observed version and set `last_update_client_id`. Existing client observations reject lower versions. When returning to a different previously seen client, equal versions are rejected too, so a client switch must use a strictly newer version than the last version observed for that client. Same-client equal versions remain valid for repeated reads. Deleted blocks behave like switching from `BlockWasDeleted`; reintroducing an old client version must be strictly newer than the remembered version.

## State and Persistence Behavior
`KnownBlockVersions` is persisted only through `save(self, file_path)`, consuming the live state and converting it into `KnownBlockVersionsSerialized`. The persisted data includes the previous-run violation flag, all `(client, block) -> version` entries, and each block's last-update/deleted marker. Missing state files load as default empty ledgers. `existing_blocks()` returns keys with entries or locked entries from the lockable map; notably, its name is broader than `BlockInfo::block_is_expected_to_exist()` and can include deleted entries or currently locked entries.

## Dependencies and Integration Points
This module depends on `lockable` for per-block async locking, `binrw` and `binary_layout` for binary formats, CryFS binary helpers for `NonZeroU32`, and `IntegrityViolationError` for rollback reporting. It is re-exported by `integrity_data/mod.rs` and consumed directly by `IntegrityBlockStore` for load, store, create, remove, and missing-block checks.

## Risks and Edge Cases
- `ClientId::generate_random()` has a TODO questioning zero generation; because `NonZeroU32` cannot hold zero, this must be audited against the `rand` distribution implementation.
- `BlockVersion::increment()` can overflow `u64`; no checked arithmetic is present.
- `KnownBlockVersions::existing_blocks()` uses `keys_with_entries_or_locked()`, and a TODO questions whether locked keys should count as existing. This matters for `IntegrityBlockStore::all_blocks()` missing-block detection.
- The rollback rule intentionally allows first-time observations from new clients with lower versions, because no local prior for that client exists. Security depends on prior observation history.
- Persistence safety depends on callers completing async drop; if `KnownBlockVersions` is not saved, local anti-rollback history is lost.

## Test Signals
The tests cover new/empty blocks, per-client and per-block versions, increasing and decreasing version checks, deletion markers, transaction commit/cancel/panic behavior, same-client versus different-client rollback rules, current version lookup, existing-block listing, save/load round trips, and base64-encoded backward-compatibility fixtures for older serialized state.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/integrity/integrity_data/known_block_versions.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/integrity/integrity_data/mod.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/integrity/integrity_data/mod.rs

## Purpose
`IntegrityData` is the owning wrapper around `KnownBlockVersions`. It represents the local integrity state file for one CryFS client and provides the API used by `IntegrityBlockStore` to lock per-block ledger entries, query previous violations, and save the state on async drop.

## Important APIs, Types, and Functions
- Re-exports `IntegrityViolationError`, `BlockInfo`, `BlockVersion`, `BlockVersionTransaction`, `ClientId`, `KnownBlockVersions`, and `MaybeClientId`.
- `IntegrityData::new(state_file_path, my_client_id)` loads `KnownBlockVersions` from the path or creates a default ledger, returning `AsyncDropGuard<Self>`.
- `my_client_id()` exposes the client id used when writing new block headers.
- `lock_block_info(block_id)` delegates to `KnownBlockVersions::lock_block_info()`.
- `integrity_violation_in_previous_run()` and `set_integrity_violation_in_previous_run()` bridge the persistent violation latch.
- `existing_blocks()` returns the block ids known by the underlying ledger.
- `AsyncDrop::async_drop_impl()` takes the ledger out of `Option` and persists it.

## Control Flow
Construction reads the integrity state before the blockstore wrapper is made usable. Normal operations lock block state through immutable `&self`, relying on interior locking in `KnownBlockVersions`. On destruction, `known_block_versions` is `take()`n so it can be consumed by `save()`. Accessors panic with "Object is currently being destructed" if used after destruction begins.

## State and Persistence Behavior
The state file path and client id are immutable after construction. Ledger persistence happens on async drop, not after every block operation. The module has a TODO noting that file locking is missing, so multiple CryFS processes could open and mutate the same state file concurrently. Another TODO questions whether `IntegrityData` and `KnownBlockVersions` should remain separate serialization layers.

## Dependencies and Integration Points
The module depends on `AsyncDropGuard` for lifecycle-managed persistence, `lockable` guard types for per-block locking, and `KnownBlockVersionsSerialized` indirectly through `KnownBlockVersions`. It is an internal module of `IntegrityBlockStore`.

## Risks and Edge Cases
- State durability is async-drop based; crashes or missed async-drop calls may lose recent integrity updates.
- No OS-level file locking is used, creating possible multi-process races and last-writer-wins corruption.
- During destruction, any lingering lock users can collide with the `Option::take()` lifecycle.

## Test Signals
Tests instantiate `IntegrityData` in a tempdir, use helper `clientid()` and `version()`, set versions under block locks, and assert per-client/per-block version separation plus rejection of decreasing versions.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/integrity/integrity_data/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/integrity/integrity_data/serialization.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/integrity/integrity_data/serialization.rs

## Purpose
This file defines the binary representation of `KnownBlockVersions`. It maps the live lockable per-block state into deterministic serialized fields with a format header, prior-violation flag, known client/block versions, and last-update/deleted state per block.

## Important APIs, Types, and Functions
- `FORMAT_VERSION_HEADER` is `cryfs.integritydata.knownblockversions;1`.
- `KnownBlockVersionsSerialized` derives `BinRead`/`BinWrite` little-endian and contains:
  - `header: Vec<NonZeroU8>` parsed/written as a NUL-terminated string.
  - `integrity_violation_in_previous_run: bool`.
  - `known_block_versions: HashMap<(ClientId, BlockId), BlockVersion>`.
  - `last_update_client_id: HashMap<BlockId, MaybeClientId>`.
- `From<KnownBlockVersionsSerialized> for KnownBlockVersions` reconstructs `LockableHashMap<BlockId, BlockInfo>`.
- `KnownBlockVersionsSerialized::async_from(KnownBlockVersions)` consumes live state and flattens it into the two persisted maps.
- `format_potential_utf8()` improves wrong-header diagnostics for non-UTF-8 bytes.

## Control Flow
Deserialization first validates the exact header, then reads the violation bool and two hash maps. Reconstruction creates block entries from `last_update_client_id` first, then merges client-version entries, creating unknown `BlockInfo` entries if versions exist without a last-update row. Serialization waits until `Arc::strong_count(&data.block_infos) == 1`, then `Arc::into_inner()` consumes the lockable map and iterates entries into the two flat maps.

## State and Persistence Behavior
The serialized model intentionally separates "who last updated this block" from "what versions have we seen for each client". Deleted state is represented by `MaybeClientId::BlockWasDeleted` in the `last_update_client_id` map, encoded as zero by the type's binary implementation. Hash-map order is not stable, and tests accept both entry orders.

## Dependencies and Integration Points
The file relies on CryFS binary helpers for bool/hashmap/NUL-string parsing, `HashMapExt::try_insert()` for duplicate detection, and `lockable::LockableHashMap` for reconstructing live state. It is called by `KnownBlockVersions::load/save`.

## Risks and Edge Cases
- `async_from()` busy-waits with `tokio::task::yield_now()` until all outstanding block-info guards release their `Arc`. The comment notes a possible deadlock if a held guard depends on the current task.
- Duplicate keys in serialized maps panic via `expect`, so malformed duplicate input may abort rather than produce a recoverable error.
- Compatibility with the C++ version is marked as TODO.
- Header mismatch is detected cleanly, but unsupported future formats are hard failures.

## Test Signals
Tests cover wrong UTF-8 and non-UTF-8 headers, invalid booleans, empty/non-empty maps, combined map serialization, extra trailing bytes, and order-insensitive serialized hashmap variants.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/integrity/integrity_data/serialization.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/integrity/mod.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/integrity/mod.rs

## Purpose
`IntegrityBlockStore` wraps a low-level blockstore and adds CryFS integrity checks. It prepends an integrity header to every physical block, updates local anti-rollback state on successful writes/reads/removes, detects wrong block ids, rollbacks, reintroduced deleted blocks, and optionally missing blocks.

## Important APIs, Types, and Functions
- `block_layout` defines the per-block header: `format_version_header: u16`, `block_id`, `last_update_client_id`, `block_version`, then user data.
- `AllowIntegrityViolations` controls whether detected violations are fatal or only logged.
- `MissingBlockIsIntegrityViolation` distinguishes single-client-style stores from multi-client stores where another authorized client may have deleted a block.
- `IntegrityConfig` stores those flags plus an `on_integrity_violation` callback.
- `IntegrityBlockStore::new()` loads `IntegrityData`, checks the persistent prior-violation latch, and may refuse to open.
- `BlockStoreReader` implementation checks headers on `load()` and performs missing-block reconciliation in `all_blocks()`.
- `BlockStoreDeleter::remove()` marks a block deleted after the underlying remove succeeds.
- `OptimizedBlockStoreWriter` implementation allocates prefix-capable data and commits/cancels `BlockVersionTransaction` around underlying writes.
- `_integrity_violation_detected()` centralizes allow/log/fail behavior and latches previous-run violations.
- `_prepend_header()` writes the header and returns the version transaction.
- `_check_and_remove_header()` validates physical data, strips the integrity header, and updates the version ledger.

## Control Flow
Construction first tries to load local integrity data; if that fails, it drops the underlying store and returns `InvalidLocalIntegrityState`. If a previous violation is latched and violations are not allowed, it async-drops both integrity data and underlying store, then returns `IntegrityViolationInPreviousRun`.

`load()` locks the target block's `BlockInfo`, loads from the underlying store, handles missing blocks according to config, creates unknown state for newly seen blocks, validates format and id headers, reads client/version, strips the header, and only then updates the version ledger.

`all_blocks()` either delegates directly or, when missing blocks are violations, collects underlying block ids, snapshots expected block ids from integrity state, removes physically present ids, then re-locks/re-checks each missing candidate with `exists()` to reduce race false positives. Remaining missing ids become an `IntegrityViolationError::MissingBlocks`.

Writes call `_prepend_header()` while holding the block lock. `try_create_optimized()` commits only on `SuccessfullyCreated`, cancels on already-existing or error. `store_optimized()` commits only on successful underlying store. `remove()` marks deleted after the underlying remove call returns without error, regardless of whether the remove result says the block actually existed.

## State and Persistence Behavior
Integrity state is persisted by `IntegrityData` on async drop. Per-block physical state stores the client id and version inside each block file/object. Detected fatal integrity violations set the persistent prior-run latch so future opens fail until the integrity file is deleted or violations are allowed. `overhead()` adds the integrity header size to the underlying store overhead.

## Dependencies and Integration Points
This wrapper composes with any `LLBlockStore + OptimizedBlockStoreWriter`. It uses `binary_layout` for block headers, `byte_unit::Byte` and `Overhead` for size accounting, `futures` for stream and missing-block concurrency, and `IntegrityData` for persistent local state. It is exported by `implementations/mod.rs` and `low_level/mod.rs`.

## Risks and Edge Cases
- Missing-block scanning is collection-based and has documented race-condition TODOs around concurrent remove/update operations.
- `remove()` records deletion after successful call even when `RemoveResult::NotRemovedBecauseItDoesntExist`; this is intentional for anti-reintroduction but can record state for never-seen blocks.
- Violation latching is saved on async drop, so a fatal error followed by crash before drop could lose the latch.
- Header format mismatch is an ordinary error, not routed through `_integrity_violation_detected()`.
- `AllowViolations` still updates local ledger after accepting suspicious data, which can affect later observations.
- Initialization uses `unwrap()` inside async-drop joins for the previous-violation path.

## Test Signals
Generic tests instantiate common low-level tests across allow/missing-block modes and verify overhead conversion. Specialized tests simulate rollback, same-client version decrease, client switching, deleted-block reintroduction, missing block load/listing, and wrong block id headers, checking both fatal and allow-violation configurations.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/integrity/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/mock.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/mock.rs

## Purpose
This testutils-gated module defines a `mockall` low-level blockstore mock that implements the full `LLBlockStore` trait surface. It supports unit tests that need expectations over low-level reads, writes, removes, overhead, and async drop.

## Important APIs, Types, and Functions
- `mock! { pub BlockStore { ... } }` generates `MockBlockStore`.
- Mocked traits: `BlockStoreReader`, `BlockStoreDeleter`, `BlockStoreWriter`, `AsyncDrop`, and marker `LLBlockStore`.
- Each async method is expressed as returning a `BoxFuture` because `mockall` cannot directly mock `async_trait` methods without explicit future signatures.
- Custom `Debug` prints `MockBlockStore`.

## Control Flow
The test-only helper `make_working_mock_block_store()` wires every expectation to an underlying `InMemoryBlockStore` held as `Arc<tokio::sync::Mutex<Option<_>>>`. Methods clone the arc, copy ids/data into owned values for async closures, then delegate to the in-memory implementation. `async_drop_impl()` takes the underlying store out of the `Option` and drops it exactly once.

## State and Persistence Behavior
The mock itself has no persistence; its test backing store is in-memory. The `Option` state prevents reuse after async-drop. Expectations for synchronous methods use blocking locks or `block_in_place`.

## Dependencies and Integration Points
The module depends on `mockall`, `futures::future::BoxFuture`, and CryFS `AsyncDropGuard`. It is exported only under `test` or `testutils` feature from `implementations/mod.rs` and `low_level/mod.rs`.

## Risks and Edge Cases
- The helper uses `blocking_lock()` and `block_in_place()` inside mock implementations; this is acceptable in tests but not a production pattern.
- Expectations must be fully configured or mock calls will fail in test code.
- Because `BlockStoreWriter` rather than optimized writer is mocked, tests that require optimized prefix allocation need other stores.

## Test Signals
The module instantiates the full low-level blockstore test suite against the working mock, demonstrating that the mock can behave like a real store when expectations delegate to `InMemoryBlockStore`.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/mock.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/mod.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/mod.rs

## Purpose
This module is the implementation registry for low-level blockstore backends and wrappers. It declares submodules and re-exports the public implementation types used by the rest of the crate.

## Important APIs, Types, and Functions
- Always exported: `CompressingBlockStore`, `EncryptedBlockStore`, `InMemoryBlockStore`, `IntegrityBlockStore`, `OnDiskBlockStore`, `ReadOnlyBlockStore`, and `DynBlockStore`.
- Integrity configuration/error exports: `AllowIntegrityViolations`, `ClientId`, `IntegrityBlockStoreInitError`, `IntegrityConfig`, `IntegrityViolationError`, `MissingBlockIsIntegrityViolation`.
- Testutils-gated exports: `MockBlockStore`, `SharedBlockStore`, `ActionCounts`, `TrackingBlockStore`, `TempDirBlockStore`.

## Control Flow
There is no runtime control flow; it is compile-time module wiring. Conditional compilation hides mock/shared/tracking/tempdir utilities unless running tests or enabling `testutils`.

## State and Persistence Behavior
No direct state. It controls visibility of stateful modules such as on-disk and integrity implementations.

## Dependencies and Integration Points
This file is consumed by `low_level/mod.rs`, which re-exports these implementation types at the crate low-level API boundary.

## Risks and Edge Cases
Re-export changes here affect downstream imports. Test-only wrappers are intentionally unavailable in normal production builds unless `feature = "testutils"` is enabled.

## Test Signals
No direct tests; coverage is indirect through each implementation's own test modules and common blockstore test macros.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/ondisk/mod.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/ondisk/mod.rs

## Purpose
`OnDiskBlockStore` persists low-level blocks as files under a base directory. It adds a small block-file format header, shards file paths by the first three uppercase hex characters of the block id, and implements the low-level reader/deleter/optimized-writer traits.

## Important APIs, Types, and Functions
- `OnDiskBlockStore::new(basedir)` constructs an async-drop guarded store.
- `FORMAT_VERSION_HEADER_PREFIX` is `cryfs;block;`; `FORMAT_VERSION_HEADER` is `cryfs;block;0\0`.
- `PREFIX_LEN = 3`; `NONPREFIX_LEN = 2 * BLOCKID_LEN - PREFIX_LEN`.
- `exists`, `load`, `num_blocks`, `estimate_num_free_bytes`, `overhead`, and `all_blocks` implement `BlockStoreReader`.
- `remove` deletes a block file and maps `NotFound` to `NotRemovedBecauseItDoesntExist`.
- `allocate`, `try_create_optimized`, and `store_optimized` implement prefix-capable writes.
- `_all_block_files()` streams valid sharded block files while skipping unrelated entries.
- `_blockid_from_filepath()` reconstructs ids from matching paths.
- `_check_and_remove_header()` validates and strips the file-format header.
- `_store()` creates parent directories, prepends the file header, and writes the file.
- `_block_path()` maps ids to uppercase hex `basedir/ABC/DEF...` paths.

## Control Flow
Reads compute the block path, read the whole file with `tokio::fs::read`, map missing files to `Ok(None)`, validate the header, shrink the `Data` region past the header, and return user data. Writes allocate with reserved prefix bytes, grow the region to include the header without reallocation, copy the header, and write the whole file. `try_create_optimized()` performs an existence check before writing; it is not atomic against concurrent creators. Listing reads the base directory, filters three-character uppercase-hex subdirs, flattens their entries, then filters blockfile-name length and uppercase-hex characters.

## State and Persistence Behavior
Each block is a file. Parent sharding directories are created lazily and not removed on delete. The store has no async-drop cleanup and no open file handles. Free-space estimation delegates to the platform-specific `sysinfo` module for the filesystem containing `basedir`.

## Dependencies and Integration Points
The module depends on Tokio filesystem APIs, `tokio_stream::wrappers::ReadDirStream`, `base64` for invalid-block diagnostics, `byte_unit::Byte`, CryFS `Data`, and `path_join`. It is often wrapped by integrity, encryption, compression, or tempdir stores.

## Risks and Edge Cases
- `try_create_optimized()` uses check-then-write and can race under concurrent writers.
- `_blockid_from_filepath()` panics on invalid assumptions; it is only called after stream filters.
- Header errors include base64-encoded block contents, which can be large.
- `_create_dir_if_doesnt_exist()` uses `create_dir` rather than recursive creation; callers assume `basedir` already exists.
- Lowercase hex files are not read; TODO notes possible future lowercase migration with uppercase fallback.
- Windows free-space support lives in `sysinfo.rs` and appears suspicious there.

## Test Signals
Tests instantiate the common low-level suite, validate block path generation, assert header prefix relationship, check overhead conversion, compare physical file size to usable size, verify files appear after store, and verify files disappear after remove.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/ondisk/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/ondisk/sysinfo.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/ondisk/sysinfo.rs

## Purpose
This helper estimates available disk space for `OnDiskBlockStore`. It provides platform-specific implementations around system calls because the desired `sysinfo` crate API was not available when copied.

## Important APIs, Types, and Functions
- `get_available_disk_space(path: &Path) -> Result<u64>` is the public wrapper.
- Unix-like `to_cpath()` converts a path to a NUL-terminated byte vector for C APIs.
- Linux/Android implementation calls `libc::statvfs64` and returns `f_bsize * f_bavail`.
- macOS/iOS implementation calls `libc::statfs` and returns `f_bsize * f_bavail`.
- Windows implementation calls `GetDiskFreeSpaceExW` and returns `*size.QuadPart()`.

## Control Flow
Each platform implementation calls the OS API, checks the success return value with `ensure!`, and converts failure to an `errno` error. The public function simply delegates to the cfg-selected implementation.

## State and Persistence Behavior
No persistent state. It is a synchronous filesystem query used by `OnDiskBlockStore::estimate_num_free_bytes()`.

## Dependencies and Integration Points
Depends on `libc` on Unix-like systems, `winapi` on Windows, `errno`, and `anyhow::ensure`. Integrated only by the on-disk backend.

## Risks and Edge Cases
- The Windows implementation appears broken: it uses `path.as_ptr()` on `Path`, binds `(size, retval)`, but returns `(stat, retval)` where `stat` is not defined. This may be hidden unless compiled for Windows.
- Unix `to_cpath()` does not reject paths containing interior NUL bytes.
- Multiplication may overflow `u64` on unusual platform values.
- The copied sysinfo code has a TODO to replace it with upstream support.

## Test Signals
Tests check that an existing tempdir returns a positive free-space value and a nonexisting path returns `errno` `ENOENT` on supported platforms.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/ondisk/sysinfo.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/readonly.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/readonly.rs

## Purpose
`ReadOnlyBlockStore` wraps a low-level blockstore and forwards read calls while blocking all mutating calls by panicking. It is intended for read-only tools, with a TODO suggesting trait-level read-only APIs might be cleaner.

## Important APIs, Types, and Functions
- `ReadOnlyBlockStore::new(underlying)` returns `AsyncDropGuard<Self>`.
- Implements `BlockStoreReader` by delegating `exists`, `load`, `num_blocks`, `estimate_num_free_bytes`, `overhead`, and `all_blocks`.
- Implements `BlockStoreDeleter::remove()` as `panic!("ReadOnlyBlockStore::remove blocked")`.
- Implements `OptimizedBlockStoreWriter` with delegated `allocate()` but panicking `try_create_optimized()` and `store_optimized()`.
- Async drop delegates to the underlying store.

## Control Flow
Read operations are transparent. Mutating operations fail immediately by panic, not by `Result::Err`. The wrapper still implements `LLBlockStore`, so callers that only have the full trait can compile mutating calls that panic at runtime.

## State and Persistence Behavior
No own persistence. It owns and drops the underlying store.

## Dependencies and Integration Points
Composes over any `LLBlockStore + OptimizedBlockStoreWriter`. Exported from the low-level implementations registry.

## Risks and Edge Cases
- Runtime panics for writes/removes are sharp edges in production paths.
- `allocate()` remains available and delegates to the underlying writer even though writes are blocked.
- No direct tests in this file validate panic behavior.

## Test Signals
No local tests. Behavior is likely exercised only indirectly where read-only wrappers are used by higher-level tools.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/readonly.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/shared.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/shared.rs

## Purpose
`SharedBlockStore` is a testutils wrapper that allows multiple owners to share one async-drop-managed underlying blockstore through `AsyncDropArc`. It supports tests that need one component to mutate the raw underlying store while another wrapper observes integrity/encryption behavior.

## Important APIs, Types, and Functions
- `SharedBlockStore::new(underlying)` wraps an `AsyncDropGuard<B>` in `AsyncDropArc`.
- `SharedBlockStore::clone(&AsyncDropGuard<Self>)` creates another guarded wrapper sharing the same underlying store.
- Implements `BlockStoreReader`, `BlockStoreDeleter`, `OptimizedBlockStoreWriter`, `AsyncDrop`, `LLBlockStore`, and `Deref<Target = B>`.

## Control Flow
All blockstore methods delegate directly to `underlying_store`. Async drop calls `async_drop()` on the `AsyncDropArc`, so actual underlying destruction is coordinated by the shared async-drop mechanism. `Deref` exposes the underlying store for tests.

## State and Persistence Behavior
The wrapper itself stores only the shared async-drop reference. Persistence and state are owned by the underlying blockstore.

## Dependencies and Integration Points
Depends on `cryfs_utils::async_drop::{AsyncDropArc, AsyncDropGuard}`. It is used in integrity specialized tests to inspect and tamper with raw blocks below `IntegrityBlockStore`.

## Risks and Edge Cases
- Intended only for test code; exposing `Deref` to the underlying store can break abstraction boundaries.
- Async-drop correctness depends on all shared wrappers being dropped.

## Test Signals
The module runs the common low-level suite using `SharedBlockStore<InMemoryBlockStore>` and verifies zero overhead conversions.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/shared.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/tempdir.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/tempdir.rs

## Purpose
`TempDirBlockStore` is a testutils helper that runs `OnDiskBlockStore` inside a temporary directory and ties directory cleanup to the store lifetime.

## Important APIs, Types, and Functions
- `TempDirBlockStore::new()` creates a tempdir with prefix `cryfs-tempdir-blockstore` and constructs an `OnDiskBlockStore` at that path.
- Contains `_tempdir: TempDir` and `underlying_store: AsyncDropGuard<OnDiskBlockStore>`.
- Implements all low-level reader/deleter/optimized-writer methods by delegating to the on-disk store.
- Async drop explicitly drops the underlying store before the tempdir field is dropped.

## Control Flow
Construction creates the tempdir, clones its path, and then creates the on-disk backend. Method calls are pass-through. Field order matters: the comment notes the underlying store should drop before the tempdir disappears.

## State and Persistence Behavior
Blocks persist only for the lifetime of the tempdir. Directory cleanup is managed by `tempfile::TempDir` after async-drop completes.

## Dependencies and Integration Points
Wraps `OnDiskBlockStore` and is exported under `test` or `testutils`. Useful for tests that need real filesystem behavior without managing paths.

## Risks and Edge Cases
- `new()` panics if tempdir creation fails.
- If async-drop is not called, underlying store cleanup may be skipped, though `TempDir` still removes the directory on drop.

## Test Signals
Runs the full common low-level blockstore test suite with the tempdir-backed on-disk implementation.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/tempdir.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/tracking.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/tracking.rs

## Purpose
`TrackingBlockStore` is a testutils wrapper that counts low-level operations while delegating behavior to an underlying store. It supports performance-style tests that assert an algorithm touches only expected blockstore APIs.

## Important APIs, Types, and Functions
- `ActionCounts` records counters for `exists`, `load`, `num_blocks`, `estimate_num_free_bytes`, `overhead`, `all_blocks`, `remove`, `try_create`, and `store`.
- `ActionCounts` derives `Add`, `AddAssign`, and `Sum`; `ZERO` is the all-zero constant.
- Custom `Debug` prints only nonzero fields.
- `TrackingBlockStore::new(underlying)` wraps an async-drop guarded store and initializes `Mutex<ActionCounts>`.
- `counts()` returns the current count snapshot.
- `get_and_reset_counts()` returns the snapshot and resets to zero.
- Reader/deleter/writer trait implementations increment the matching counter and then delegate.

## Control Flow
Every public low-level method locks the counter mutex, increments a field, releases the lock at the end of the statement, and calls the underlying store. `allocate()` is static and not counted because no wrapper instance is involved. `store_optimized()` and `try_create_optimized()` count as `store` and `try_create` respectively.

## State and Persistence Behavior
The only wrapper state is the in-memory counter mutex plus the owned underlying store. Async drop delegates to the underlying store; counters are not persisted.

## Dependencies and Integration Points
Composes over any optimized low-level blockstore. Exported only for tests/testutils. Used by tests that need operation counts and by the common low-level test suite to ensure functional pass-through.

## Risks and Edge Cases
- Uses `std::sync::Mutex` in async methods, but only for a short synchronous increment before awaiting.
- `allocate()` calls are invisible to counters.
- Counting begins before delegate success/failure, so failed operations are counted too; tests rely on this.

## Test Signals
Local tests instantiate the common low-level suite and specifically assert counter behavior for each method, failed `try_create`, missing `remove`, optimized writer methods, overhead calls, all-blocks stream creation/collection, and `get_and_reset_counts()`.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/tracking.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/interface.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/low_level/interface.rs

## Purpose
This file defines the low-level blockstore trait contract: asynchronous block reading/listing, writing, deletion, optimized prefix-aware data allocation, and the marker trait tying all pieces together.

## Important APIs, Types, and Functions
- `BlockStoreReader` exposes `exists`, `load`, `num_blocks`, `estimate_num_free_bytes`, `overhead`, and `all_blocks`.
- `BlockStoreDeleter` exposes `remove`.
- `BlockStoreWriter` exposes slice-based `try_create` and `store`.
- `OptimizedBlockStoreWriter` defines associated `BlockData`, static `allocate(size)`, and optimized `try_create_optimized`/`store_optimized`.
- Blanket `impl BlockStoreWriter for B where B: OptimizedBlockStoreWriter + Sync` copies slices into allocated `BlockData` and calls the optimized methods.
- `LLBlockStore` is the marker trait requiring reader, writer, deleter, `AsyncDrop<Error = anyhow::Error>`, `Debug`, and `Any`.
- `block_data::IBlockData` and `create_block_data_wrapper!` provide crate-private wrappers around `Data` that preserve prefix-capacity invariants.

## Control Flow
The non-optimized writer API is layered over optimized allocation. `try_create()` and `store()` allocate exact user length, assert the exposed region length, copy user bytes into that region, and delegate. Implementations that need headers allocate larger physical buffers and shrink the visible region so later prefix growth does not reallocate.

## State and Persistence Behavior
No state here. It defines the behavioral and memory-layout contracts that persistence implementations must respect.

## Dependencies and Integration Points
Depends on `async_trait`, `futures::stream::BoxStream`, `byte_unit::Byte`, `cryfs_utils::data::Data`, and crate result enums. Every low-level implementation and adapter in this subset implements these traits.

## Risks and Edge Cases
- The macro implementation body uses `impl AsRef<[u8]> for BlockData` rather than `$name`; this works for invocations naming the wrapper `BlockData`, but the macro is less general than its parameter suggests.
- `IBlockData::new()` is crate-private and unchecked by design; safety depends on only local implementations constructing valid wrappers.
- The blanket writer copies user slices, so optimized no-copy behavior is only available to callers that use optimized APIs directly.

## Test Signals
No local tests. The common low-level test suite exercises the trait contract through concrete implementations; optimized writer behavior is marked as a TODO in tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/interface.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/mod.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/low_level/mod.rs

## Purpose
This is the public low-level module prelude. It exposes the low-level trait interfaces and selected implementations to the rest of the crate.

## Important APIs, Types, and Functions
- Declares `#[macro_use] mod interface;` so `create_block_data_wrapper!` is available inside implementation modules.
- Re-exports `BlockStoreDeleter`, `BlockStoreReader`, `BlockStoreWriter`, `LLBlockStore`, and `OptimizedBlockStoreWriter`.
- Declares `mod implementations;`.
- Re-exports testutils implementations under `test` or `feature = "testutils"`.
- Re-exports production implementations and integrity config/error types unconditionally.

## Control Flow
No runtime behavior; this file is module wiring and public API shaping.

## State and Persistence Behavior
No state. It controls which stateful backends are available to callers.

## Dependencies and Integration Points
This module is the crate-level import point for `crate::low_level::*` and backs top-level re-exports such as `crate::LLBlockStore`.

## Risks and Edge Cases
Conditional exports mean code using `MockBlockStore`, `SharedBlockStore`, `TrackingBlockStore`, or `TempDirBlockStore` must compile only in test/testutils contexts.

## Test Signals
No direct tests; all low-level implementation and adapter tests depend on this module's re-exports.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/overhead.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/overhead.rs

## Purpose
`Overhead` models the per-block physical bytes not available to callers, allowing layered blockstores to convert between physical block size and usable block size.

## Important APIs, Types, and Functions
- `Overhead { overhead: Byte }` is `Copy`, `Clone`, `PartialEq`, `Eq`, and `Debug`.
- `impl Add for Overhead` sums overheads with `Byte::add().unwrap()`.
- `Overhead::new(overhead)` constructs a wrapper.
- `usable_block_size_from_physical_block_size(physical)` subtracts overhead or returns `InvalidBlockSizeError`.
- `physical_block_size_from_usable_block_size(usable)` adds overhead.
- `InvalidBlockSizeError` is `derive_more::Error + Display` with a message.

## Control Flow
Conversion is straightforward arithmetic. Physical-to-usable uses checked subtraction and produces an explanatory error when physical size is smaller than overhead. Usable-to-physical and overhead addition unwrap `Byte::add()`.

## State and Persistence Behavior
No persistence. The type is a value object returned by blockstore layers such as on-disk and integrity; layered stores add their overheads together.

## Dependencies and Integration Points
Depends on `byte_unit::Byte` and `derive_more`. Called throughout low-level and high-level tests to verify size conversion invariants.

## Risks and Edge Cases
- `Byte::add().unwrap()` can panic on overflow.
- The doc comment says "call sits", likely a typo for "call sites" or "callers".
- `InvalidBlockSizeError` exposes only the formatted message, not structured physical/overhead values.

## Test Signals
Unit tests cover successful subtraction, zero usable size, error when physical is smaller than overhead, usable-to-physical addition, and round-trip conversions in both directions.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/overhead.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/tests/high_level/adapter_for_low_level_tests.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/tests/high_level/adapter_for_low_level_tests.rs

## Purpose
This adapter lets the low-level common test suite run against high-level `BlockStore` implementations by wrapping a high-level store in an `LLBlockStore` facade.

## Important APIs, Types, and Functions
- `BlockStoreToLLBlockStoreAdapter<B>(AsyncDropGuard<B>)` owns a high-level blockstore.
- `new(store)` wraps the high-level store.
- `clear_cache_slow()` forwards to the high-level store for fixtures that flush between assertions.
- Implements `BlockStoreReader`: `exists()` loads and checks `Option`, `load()` extracts block data, `num_blocks`, `estimate_num_free_bytes`, `overhead`, and `all_blocks` delegate.
- Implements `BlockStoreDeleter::remove()` via `remove_by_id`.
- Implements `BlockStoreWriter::try_create()` via high-level `try_create`, and `store()` via `overwrite`.
- Implements `AsyncDrop` and marker `LLBlockStore`.
- `FixtureAdapterForLLTests<F, FLUSH_CACHE_ON_YIELD>` adapts an `HLFixture` to an `LLFixture`.

## Control Flow
The low-level suite calls the adapter's low-level methods. For reads, high-level loaded block objects are converted to cloned `Data`. For writes, `&[u8]` is copied into a `Data` value and submitted to the high-level API. Fixture `yield_fixture()` optionally clears the high-level cache before delegating to the wrapped fixture's yield hook.

## State and Persistence Behavior
State is owned by the wrapped high-level store. The adapter is lifecycle-managed by `AsyncDropGuard` and drops the inner store on async drop.

## Dependencies and Integration Points
Bridges `tests::high_level::HLFixture`, `tests::low_level::LLFixture`, the high-level `BlockStore` trait, and low-level blockstore traits. It is re-exported by `tests/high_level/mod.rs`.

## Risks and Edge Cases
- `exists()` is implemented by loading the full block, which may be heavier than native low-level existence checks.
- `load()` clones block data out of the high-level block, so mutation semantics differ from holding a high-level block guard.
- Adapter writes go through high-level locking/cache behavior, so it tests the high-level facade as a low-level store rather than raw persistence.

## Test Signals
Used by macro-based suites to apply low-level tests to high-level stores. Flush-on-yield variants exercise behavior across cache clears.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/tests/high_level/adapter_for_low_level_tests.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/tests/high_level/fixture.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/tests/high_level/fixture.rs

## Purpose
Defines `HLFixture`, the fixture contract for instantiating the common high-level `BlockStore` test suite against concrete implementations.

## Important APIs, Types, and Functions
- `HLFixture::ConcreteBlockStore` must implement `BlockStore + AsyncDrop + Debug + Send + Sync + 'static`.
- `new()` creates fixture state.
- `store()` asynchronously creates an `AsyncDropGuard` for the concrete store.
- `yield_fixture(&self, store)` is an async hook used between test actions and assertions.

## Control Flow
Test macros construct a fixture, request a store, run operations, call `yield_fixture()` between phases, and explicitly async-drop the store. Implementations can use the fixture object to hold tempdirs or other RAII resources for the whole test.

## State and Persistence Behavior
No state in the trait itself. Fixture implementations decide how long backing resources live. The design keeps the fixture alive for the duration of each test.

## Dependencies and Integration Points
Depends on the crate high-level `BlockStore` trait and `cryfs_utils::async_drop`. Re-exported by `tests/high_level/mod.rs` and consumed by high-level test macros plus adapters.

## Risks and Edge Cases
- Implementors must ensure `yield_fixture()` does not invalidate active block guards unless the test expects that.
- Tests rely on explicit `async_drop()` calls; fixture implementations should make cleanup robust.

## Test Signals
The trait itself has no tests; every high-level common test is parameterized over it.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/tests/high_level/fixture.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/tests/high_level/mod.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/tests/high_level/mod.rs

## Purpose
This module wires together the high-level test fixture, adapter, and test suite exports.

## Important APIs, Types, and Functions
- Declares `adapter_for_low_level_tests` and re-exports `BlockStoreToLLBlockStoreAdapter` and `FixtureAdapterForLLTests`.
- Declares `fixture` and re-exports `HLFixture`.
- Exposes `pub mod tests`.

## Control Flow
No runtime behavior. It is test module organization.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Imported by concrete blockstore tests that need to implement `HLFixture` or instantiate common high-level tests. The adapter re-export also enables running low-level tests against high-level stores.

## Risks and Edge Cases
Changing re-exports here can break test modules that import through `crate::tests::high_level`.

## Test Signals
Indirectly exercised by all high-level test instantiations.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/tests/high_level/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/tests/high_level/tests.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/tests/high_level/tests.rs

## Purpose
This file defines the common high-level `LockingBlockStore`/`BlockStore` behavior suite and macros to instantiate it for concrete high-level fixtures.

## Important APIs, Types, and Functions
- `instantiate_highlevel_blockstore_specific_tests!` creates modules for create, remove, resize, data, overwrite, and overhead tests.
- `_instantiate_highlevel_blockstore_specific_tests!` recursively emits `#[tokio::test]` functions that call the shared async test functions.
- `assert_block_is_usable()` mutates a block's full data region, drops it, reloads it, and checks persistence.
- Test modules:
  - `create`: created block ids differ.
  - `remove`: modified loaded blocks can be removed.
  - `resize`: zero/nonzero blocks can grow, shrink, and become zero while remaining usable.
  - `data`: partial writes over several offsets/counts preserve unaffected ranges.
  - `overwrite`: overwriting while a block is loaded blocks until the guard is dropped, then succeeds.
  - `usable_block_size_from_physical_block_size`: overhead conversions round trip.

## Control Flow
The instantiation macro generates nested modules and per-test Tokio functions. Individual tests use `HLFixture` to create a store, call `yield_fixture()` between mutation and assertion phases, and explicitly async-drop the store. The overwrite blocking test uses `Arc`, `tokio::spawn`, sleeps, and `is_finished()` to assert lock behavior.

## State and Persistence Behavior
Tests assume high-level block guards flush changes on drop or store lifecycle as appropriate. `yield_fixture()` allows implementations to flush caches/reopen state between steps. Data tests validate both immediate in-memory views and reload-after-drop persistence.

## Dependencies and Integration Points
Depends on `HLFixture`, high-level `BlockStore` and `Block` traits, `RemoveResult`, test data helpers, and `assert_data_range_eq`. The comments note that many low-level behaviors are tested by adapting high-level stores to low-level tests.

## Risks and Edge Cases
- The overwrite blocking tests use fixed 100 ms sleeps, which can be timing-sensitive on slow or overloaded systems.
- Several TODOs remain for `Block::block_id()`, `data()` identity, `flush()`, and additional locking behaviors.
- Tests rely on explicit async drops; leaks can hide persistence issues.

## Test Signals
This file is itself the high-level test signal. It covers ids, remove-after-modification, resize data usability, partial write preservation, write persistence after loading, overwrite locking, and overhead arithmetic.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/tests/high_level/tests.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/tests/low_level/adapter_for_high_level_tests.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/tests/low_level/adapter_for_high_level_tests.rs

## Purpose
This adapter lets the high-level common test suite run against low-level `LLBlockStore` implementations by wrapping them in `LockingBlockStore`.

## Important APIs, Types, and Functions
- `FixtureAdapterForHLTests<F, FLUSH_CACHE_ON_YIELD>` stores an `LLFixture`.
- Implements `HLFixture` for any suitable `LLFixture`.
- `ConcreteBlockStore = LockingBlockStore<F::ConcreteBlockStore>`.
- `store()` creates the low-level store through the fixture and wraps it with `LockingBlockStore::new`.
- `yield_fixture()` optionally clears the high-level cache and then delegates to the low-level fixture hook via `store.inner_block_store()`.

## Control Flow
High-level tests call `HLFixture` methods. The adapter builds a low-level store, wraps it in locking/caching high-level semantics, and forwards yield hooks. Cache flushing is controlled by a const generic so tests can be instantiated with or without forced reload behavior.

## State and Persistence Behavior
State belongs to the underlying low-level fixture/store plus `LockingBlockStore` cache state. Flush-on-yield variants test persistence across cache boundaries.

## Dependencies and Integration Points
Bridges `tests::low_level::LLFixture`, high-level `HLFixture`, `LLBlockStore`, and `LockingBlockStore`. Re-exported by `tests/low_level/mod.rs`.

## Risks and Edge Cases
- The adapter tests low-level stores through `LockingBlockStore`, so failures can originate in high-level locking/caching rather than the low-level backend alone.
- `clear_cache_slow().await.unwrap()` panics on cache-clear failure during tests.

## Test Signals
Used to instantiate high-level tests for low-level implementations, ensuring low-level stores can support the high-level locking API contract.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/tests/low_level/adapter_for_high_level_tests.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/tests/low_level/fixture.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/tests/low_level/fixture.rs

## Purpose
Defines `LLFixture`, the fixture contract for instantiating the common low-level blockstore test suite against concrete `LLBlockStore` implementations.

## Important APIs, Types, and Functions
- `LLFixture::ConcreteBlockStore` must implement `LLBlockStore + Send + Sync`.
- `new()` constructs fixture state.
- `store()` asynchronously constructs an `AsyncDropGuard` for the concrete low-level store.
- `yield_fixture(&self, store)` is an async hook between test operations and assertions.

## Control Flow
Low-level test macros create a fixture, request a store, run low-level operations, call the yield hook between phases, and explicitly async-drop the store. Fixture state can own tempdirs, shared stores, or other setup resources.

## State and Persistence Behavior
No state in the trait itself. Implementations define resource lifetime and optional flushing behavior.

## Dependencies and Integration Points
Depends on crate `LLBlockStore` and CryFS `AsyncDropGuard`. Re-exported by `tests/low_level/mod.rs` and consumed by common low-level tests plus high-level adapter tests.

## Risks and Edge Cases
- The TODO asks whether low-level implementations actually need `yield_fixture()`.
- Implementors must preserve backing resources until all stores created for a test are dropped.

## Test Signals
The fixture is the generic entry point for the low-level test macro suite; no direct local tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/tests/low_level/fixture.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/tests/low_level/mod.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/tests/low_level/mod.rs

## Purpose
This module wires together the low-level common test fixture, high-level adapter, and test suite exports.

## Important APIs, Types, and Functions
- Module docs describe common tests for `crate::LLBlockStore` implementations.
- Declares `fixture` and re-exports `LLFixture`.
- Declares `adapter_for_high_level_tests` and re-exports `FixtureAdapterForHLTests`.
- Exposes `pub mod tests`.

## Control Flow
No runtime behavior. It organizes and re-exports test infrastructure.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Imported by concrete low-level implementation tests to implement fixtures or instantiate macro suites. Also supports high-level testing through `FixtureAdapterForHLTests`.

## Risks and Edge Cases
Changing this module's re-exports would affect many implementation test modules that import through `crate::tests::low_level`.

## Test Signals
Indirectly exercised by every low-level blockstore implementation test instantiation.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/tests/low_level/mod.rs -->
