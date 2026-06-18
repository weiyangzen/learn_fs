# subset-b-008307 Research

Grouped research for CryFS blobstore and blockstore files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_tree_store/tree/tests_performance.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_tree_store/tree/tests_performance.rs

## Purpose
Defines performance-oriented async tests for the on-blocks `DataTree` implementation. These tests do not measure elapsed time; they assert exact low-level blockstore action counts so tree operations only load, check, or store the structurally necessary nodes.

## APIs, Flow, And State
The file fixes a small `NodeLayout` with 40-byte blocks, `NUM_LEAVES = 100`, and derived `DEPTH`, `NUM_NODES`, and `NUM_BYTES`. `testutils` builds a `DataTreeStore<LockingBlockStore<LLSharedBlockStore<LLTrackingBlockStore<InMemoryBlockStore>>>>`, creates empty/nonempty trees, flushes caches, resets counters, and computes expected tree-node counts with `divrem::DivCeil`. Tests cover `num_nodes`, `num_bytes`, `create_tree`, `try_create_tree`, read variants through `instantiate_read_tests!`, `read_all`, and many `write_bytes` cases.

Control flow repeatedly creates or loads a tree, optionally warms the size cache with `num_bytes`, prunes unloaded cache entries, runs one tree operation, then compares `LLActionCounts` against expected loads/stores/exists calls. Write tests also drop the tree and clear the cache to force dirty node flushes before asserting store counts. State under test is the in-memory blockstore plus the locking block cache and the tree's internal node/size caches.

## Dependencies And Integration
Integrates `DataTreeStore` and `DataTree` with the high-level locking blockstore and low-level tracking/shared/in-memory wrappers from `cryfs_blockstore`. It relies on `pretty_assertions`, Tokio multi-thread tests, `BoxFuture`, and helper functions from the surrounding tree test utilities such as `expected_depth_for_num_leaves`.

## Risks And Test Signals
The file is a strong regression signal for accidental O(tree) or O(file) behavior in tree reads/writes. Several assertions intentionally encode known inefficiencies with TODOs: reads without size cache use hard-coded extra loads, full-leaf writes unexpectedly perform `exists`, and growing writes include unexplained fixed offsets like `+3` stores. Missing areas are called out at the end: `resize_num_bytes`, `remove`, and `all_blocks` performance are not covered here.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_tree_store/tree/tests_performance.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/mod.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/mod.rs

## Purpose
Assembles and re-exports the blobstore implementation that stores blobs as block-backed data trees. It exposes the public on-blocks types and instantiates the generic blobstore test suite for several block sizes.

## APIs, Flow, And State
The module declares `data_node_store`, `data_tree_store`, `blob_on_blocks`, and `blobstore_on_blocks`, then re-exports `BlobOnBlocks`, `BlobStoreOnBlocks`, `DataNodeStore`, node types, `DataTree`, `DataTreeStore`, and `LoadNodeError`. Test fixtures create `BlobStoreOnBlocks<LockingBlockStore<InMemoryBlockStore>>` with block sizes ranging from the minimal node-header-plus-two-IDs size through 1 KiB, 32 KiB, and 4 MiB.

## Dependencies And Integration
This is the integration boundary between `cryfs_blobstore` and `cryfs_blockstore`: the blobstore is backed by a high-level `LockingBlockStore` over an `InMemoryBlockStore`. It uses `byte_unit::Byte`, async fixture construction, and `instantiate_tests_for_blobstore!`, which also tests the blobstore through the low-level blockstore adapter.

## Risks And Test Signals
The minimal block-size fixture protects node layout assumptions, while larger sizes exercise realistic capacities. The TODO notes that the generic blockstore tests need sufficiently large data cases to actually cover the tree structure; otherwise small tests can pass while multi-node behavior regresses.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/shared.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/implementations/shared.rs

## Purpose
Implements `BlobStore` for `AsyncDropArc<B>`, allowing a blobstore to be shared while retaining the same async-drop and trait behavior.

## APIs, Flow, And State
Every `BlobStore` method delegates through `Deref` to the underlying store: create/load/remove, size/capacity queries, cache flushing, test cache clearing, and test-only `all_blobs`. The concrete blob type is unchanged (`B::ConcreteBlob`), so sharing does not wrap individual blobs.

## Dependencies And Integration
Depends on `cryfs_utils::async_drop::{AsyncDrop, AsyncDropArc, AsyncDropGuard}` and the blobstore interface. Its tests wrap `BlobStoreOnBlocks<LockingBlockStore<InMemoryBlockStore>>` in `AsyncDropArc` and instantiate the full blobstore suite.

## Risks And Test Signals
The wrapper is intentionally transparent; risks are missed delegation when the trait grows, or shared lifetime/drop behavior diverging from a direct store. The generic tests verify functional equivalence under a shared wrapper but do not stress concurrent clones beyond normal multi-thread Tokio execution.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/shared.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/tracking/action_counts.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/implementations/tracking/action_counts.rs

## Purpose
Defines `BlobStoreActionCounts`, the counter set used by the blobstore tracking wrapper to record which blob and store APIs were invoked.

## APIs, Flow, And State
The struct contains `u32` counters for blob operations (`num_bytes`, `resize`, reads, writes, flush, node count, remove, all_blocks) and store operations (`create`, `try_create`, `load`, remove, node count, capacity/block-size queries, flush-if-cached). `derive_more` provides addition, add-assign, and sum, and `ZERO` is a constant all-zero baseline. Custom `Debug` omits zero-valued fields for readable assertions.

## Dependencies And Integration
Used by `TrackingBlobStore` and `TrackingBlob` behind an `Arc<Mutex<_>>`. The type is exported under test/testutils from the crate root.

## Risks And Test Signals
Counters are `u32`, so extremely long-running instrumentation could overflow in debug or wrap in release if not guarded by Rust overflow settings. The explicit custom `Debug` must be updated when fields are added. Tracking tests verify zero state, each counter increment, and reset behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/tracking/action_counts.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/tracking/mod.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/implementations/tracking/mod.rs

## Purpose
Collects the blobstore tracking implementation and exposes the public test utility types.

## APIs, Flow, And State
The module owns `action_counts`, `tracking_blob`, and `tracking_blobstore`, and re-exports `BlobStoreActionCounts` plus `TrackingBlobStore`. `tracking_blob` remains internal except where tests reach into it from the child test module.

## Dependencies And Integration
The parent `implementations` module re-exports these types only under `test` or `feature = "testutils"`, so production builds are not coupled to tracking wrappers.

## Risks And Test Signals
The module has little logic itself; risks are visibility drift or forgetting to expose new tracking utilities behind the intended feature gates. Its `tests` child exercises the full wrapper behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/tracking/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/tracking/tests.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/implementations/tracking/tests.rs

## Purpose
Tests `TrackingBlobStore` as both a normal blobstore and a counter-instrumented wrapper.

## APIs, Flow, And State
`TestFixture` wraps `BlobStoreOnBlocks<LockingBlockStore<InMemoryBlockStore>>` in `TrackingBlobStore` and runs `instantiate_tests_for_blobstore!`. Counter tests then create/load/remove blobs, call every blob method, call store metadata methods, collect `all_blocks` streams, and assert exact `BlobStoreActionCounts` snapshots. `change_blob_id` produces a non-existing ID by mutating the first byte.

## Dependencies And Integration
Uses the public blobstore traits, the tracking wrapper, `RemoveResult`, `futures::StreamExt`, and `pretty_assertions`. It reaches `tracking_blob::TrackingBlob` to test the associated `remove` path directly.

## Risks And Test Signals
The test suite is a detailed signal that tracking remains transparent and complete. It checks counters increase on success and on not-found cases for store operations. It does not exercise poisoned mutex handling or very high counter values, and `store_flush_if_cached` is present in the counter type but not covered in the visible counter tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/tracking/tests.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/tracking/tracking_blob.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/implementations/tracking/tracking_blob.rs

## Purpose
Wraps a concrete blob and increments shared action counters before forwarding all `Blob` operations.

## APIs, Flow, And State
`TrackingBlob<B>` stores an `AsyncDropGuard<B::ConcreteBlob>` plus `Arc<Mutex<BlobStoreActionCounts>>`. `new` returns an `AsyncDropGuard<Self>`. Trait methods increment the corresponding counter and delegate to the underlying blob. `remove` consumes the tracking guard with `unsafe_into_inner_dont_drop`, increments `blob_remove`, and calls the underlying concrete blob's associated `remove`.

## Dependencies And Integration
Generic over a `BlobStore + AsyncDrop + Debug + 'static`; used exclusively by `TrackingBlobStore` as its `ConcreteBlob`. It forwards `all_blocks` as a boxed stream of `BlockId` and forwards async drop to the wrapped blob.

## Risks And Test Signals
The mutex lock is held only for the increment, avoiding holding it across awaited underlying calls. The `remove` path is more delicate because it manually unwraps the async-drop guard to transfer ownership. Tests cover every counter path, including `TrackingBlob::remove`.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/tracking/tracking_blob.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/tracking/tracking_blobstore.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/implementations/tracking/tracking_blobstore.rs

## Purpose
Provides a test/testutils blobstore wrapper that records action counts while delegating all storage behavior to an underlying blobstore.

## APIs, Flow, And State
`TrackingBlobStore<B>` owns an `AsyncDropGuard<B>` and shared `Arc<Mutex<BlobStoreActionCounts>>`. Public helpers are `new`, `counts`, and `get_and_reset_counts`. Store methods increment counters then forward to the underlying store; create/load/try_create wrap returned blobs in `TrackingBlob`. Test-only cache clearing and `all_blobs` deliberately pass through without counter fields.

## Dependencies And Integration
Requires the underlying store to implement `BlobStore`, `AsyncDrop`, `Debug`, `Send`, `Sync`, and `'static`. It is re-exported for tests/testutils and used by performance tests and wrapper-specific tests.

## Risks And Test Signals
The wrapper is useful for behavioral cost assertions but can influence scheduling slightly through mutex use. Counter coverage must track trait evolution; newly added trait methods need new fields and tests. Tests verify transparent generic blobstore behavior and exact counts for most methods.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/tracking/tracking_blobstore.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/interface.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/interface.rs

## Purpose
Defines the public high-level blob and blobstore traits for CryFS.

## APIs, Flow, And State
`Blob` exposes identity, byte length, resize, full and partial reads, fallible partial read, write, flush, node count, consuming remove, and `all_blocks`. `BlobStore` exposes create, ID-specific try-create/load/remove, node counts, capacity estimate, logical block size, cache flush by blob ID, and test/testutils cache clearing. `BLOBID_LEN` aliases `cryfs_blockstore::BLOCKID_LEN`.

## Dependencies And Integration
Uses `anyhow`, `async_trait`, `byte_unit`, `futures::BoxStream`, `cryfs_utils::data::Data`, and blockstore `BlockId`/`RemoveResult`. `BlobId` is a thin blob-level identity rooted in block IDs.

## Risks And Test Signals
Several comments mark abstraction leaks: `num_nodes` and `all_blocks` expose block-backed internals, and read-only methods require `&mut self`. These traits are the main contract consumed by on-block implementations, tracking wrappers, async shared wrappers, and blobstore tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/interface.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/lib.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/lib.rs

## Purpose
Crate root for `cryfs_blobstore`, wiring public blobstore identity, traits, implementations, test utilities, and version checks.

## APIs, Flow, And State
The crate forbids unsafe code, defines `blob_id`, `interface`, and `implementations`, and re-exports `BlobId`, `Blob`, `BlobStore`, `BLOBID_LEN`, `BlobOnBlocks`, `BlobStoreOnBlocks`, data-node/tree types, and `RemoveResult`. Under test/testutils it also re-exports `BlobStoreActionCounts` and `TrackingBlobStore`.

## Dependencies And Integration
Depends publicly on `cryfs_blockstore::RemoveResult` and `cryfs_version::assert_cargo_version_equals_git_version!()`. The test module is only compiled under `cfg(test)`.

## Risks And Test Signals
This file controls public API surface and feature-gated test helpers. The version assertion guards release consistency. Since missing docs are only a TODO, API documentation completeness is not currently enforced.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/tests/fixture.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/tests/fixture.rs

## Purpose
Defines the generic fixture trait used to instantiate the blobstore conformance tests for many implementations.

## APIs, Flow, And State
`Fixture` has an associated `ConcreteBlobStore` constrained to `BlobStore + Debug + AsyncDrop<Error = anyhow::Error> + Send + Sync + 'static`. Implementors provide `new`, async `store`, and `yield_fixture`. The fixture is kept alive for the whole test so it can own temporary directories or other RAII resources.

## Dependencies And Integration
Used by `instantiate_tests_for_blobstore!`, implementation-specific fixtures, tracking tests, shared wrapper tests, and the adapter that runs blockstore tests against blobstores.

## Risks And Test Signals
`yield_fixture` is the key hook for forcing flushes or other persistence transitions between test operations. If a fixture leaves it as a no-op, only cached behavior may be tested for stores that require explicit cache clearing.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/tests/fixture.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/tests/mod.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/tests/mod.rs

## Purpose
Collects blobstore test modules and defines the top-level macro that applies the full test suite to a blobstore implementation.

## APIs, Flow, And State
`instantiate_tests_for_blobstore!` creates two test modules: `as_blobstore`, using blobstore-specific tests, and `as_blockstore`, using `cryfs_blockstore::instantiate_blockstore_tests_for_lowlevel_blockstore!` through `TestFixtureAdapter` with flushing enabled and disabled.

## Dependencies And Integration
Bridges blobstore testing to the low-level blockstore test suite, treating each blob as a block through `test_as_blockstore`. The macro accepts optional Tokio test arguments, commonly `(flavor = "multi_thread")`.

## Risks And Test Signals
This macro is the main source of cross-interface regression coverage. It also means blobstores must satisfy blockstore-like semantics through the adapter, so failures can indicate adapter assumptions as well as implementation bugs.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/tests/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/tests/test_as_blockstore/block_store_adapter.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/tests/test_as_blockstore/block_store_adapter.rs

## Purpose
Adapts any `BlobStore` into a low-level `LLBlockStore` so the standard blockstore tests can be reused against blobstore implementations.

## APIs, Flow, And State
`BlockStoreAdapter<B>` owns an `AsyncDropGuard<B>`. `exists`, `load`, `remove`, and `all_blocks` map `BlockId` to `BlobId { root: *id }`. `try_create` creates a blob, resizes it to the block payload length, writes from offset zero, and drops it. `store` loads or creates the blob, resizes if needed, writes the full data, and drops it. `num_blocks` counts test-only `all_blobs`, and `estimate_num_free_bytes` multiplies logical block size by the blobstore's estimated block count.

## Dependencies And Integration
Implements `BlockStoreReader`, `BlockStoreWriter`, `BlockStoreDeleter`, `AsyncDrop`, and marker `LLBlockStore`. It uses blob `read_all`, `resize`, `write`, and async drop to provide blockstore semantics.

## Risks And Test Signals
The adapter has zero overhead from the blockstore perspective even though the blobstore may have internal metadata, so size-related assertions are adapted rather than storage-physical. It unwraps async-drop errors in some cleanup paths, so failures there panic tests. The generic blockstore suite provides broad behavioral coverage through this shim.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/tests/test_as_blockstore/block_store_adapter.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/tests/test_as_blockstore/fixture_adapter.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/tests/test_as_blockstore/fixture_adapter.rs

## Purpose
Converts a blobstore `Fixture` into a low-level blockstore `LLFixture` by wrapping created stores in `BlockStoreAdapter`.

## APIs, Flow, And State
`TestFixtureAdapter<F, FLUSH_CACHE_ON_YIELD>` stores the original blobstore fixture. `store` builds the underlying blobstore then returns an adapter. `yield_fixture` optionally clears the adapter/blobstore cache and then calls the original fixture's `yield_fixture` with the inner blobstore.

## Dependencies And Integration
Used by `instantiate_tests_for_blobstore!` to run blockstore tests against blobstores in both flushing and non-flushing modes.

## Risks And Test Signals
The ordering in `yield_fixture` matters: adapter cache clearing occurs before fixture-specific yielding. This surfaces persistence bugs when flushing is enabled while keeping a cached-mode lane for pure behavior tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/tests/test_as_blockstore/fixture_adapter.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/tests/test_as_blockstore/mod.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/tests/test_as_blockstore/mod.rs

## Purpose
Small module that exposes the blobstore-as-blockstore fixture adapter.

## APIs, Flow, And State
Declares `block_store_adapter` and `fixture_adapter`, and publicly re-exports `TestFixtureAdapter`. No runtime state lives here.

## Dependencies And Integration
Imported by the top-level test macro to instantiate low-level blockstore tests for blobstore implementations.

## Risks And Test Signals
The only risk is module visibility drift. Functional coverage lives in the adapter and in the generic tests that consume it.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/tests/test_as_blockstore/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/tests/tests.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/tests/tests.rs

## Purpose
Defines blobstore-specific conformance tests and macros for instantiating them.

## APIs, Flow, And State
`instantiate_blobstore_specific_tests!` expands into Tokio tests using the supplied `Fixture`. Currently the `load` module verifies that loading a non-existing blob returns `None` for both empty and non-empty stores. The non-empty case first creates a blob with a fixed ID, then loads a different fixed ID.

## Dependencies And Integration
Uses `Fixture`, `BlobId`, `BlobStore`, `AsyncDrop`, and macro indirection through `_instantiate_blobstore_specific_tests!` so implementations can choose Tokio attributes.

## Risks And Test Signals
The direct blobstore-specific suite is currently sparse; most behavioral coverage comes from the blockstore adapter suite. The TODOs explicitly call for more blobstore-level tests, especially beyond loading non-existing blobs.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/tests/tests.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/Cargo.toml -->
# sources/security-integrity/cryfs/crates/blockstore/Cargo.toml

## Purpose
Package manifest for `cryfs-blockstore`, declaring the crate metadata, dependencies, optional test utilities, and platform-specific dependencies.

## APIs, Flow, And State
The package inherits workspace authors, edition, Rust version, homepage, repository, license, readme, and version. Core dependencies include async/runtime libraries, binary encoding, byte sizing, crypto/utils/version crates, futures, locking, compression, random/hex, serialization, system info, and Tokio filesystem/stream support. Optional `mockall` and `tempfile` are enabled by the `testutils` feature.

## Dependencies And Integration
Uses Unix `libc` except wasm/unknown targets and Windows `winapi` with `fileapi`. Dev dependencies add common macros, `cryfs-utils` testutils, `generic-array`, `mockall`, `tempfile`, and `pretty_assertions`.

## Risks And Test Signals
Feature gating is important: production builds should not pull mock/tempfile unless `testutils` is enabled. The crate root also asserts `byte_unit::Byte` size and cargo/git version consistency, which are integration-level signals tied to this manifest.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/block_id.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/block_id.rs

## Purpose
Defines the 16-byte `BlockId` type used as the stable identifier for blocks and blob roots.

## APIs, Flow, And State
`BlockId` wraps `[u8; BLOCKID_LEN]` and derives copy/clone/equality/hash/order traits. Constructors include random generation via `rand::rng().fill`, `zero`, `from_slice`, `from_array`, and `from_hex`; accessors/formatters include `data`, `to_hex`, `to_hex_upper`, `Display`, and `Debug`. `BinRead` and `BinWrite` serialize exactly the 16-byte array.

## Dependencies And Integration
Used throughout high-level and low-level blockstores, blob IDs, integrity errors, and streams. Binary serialization integrates with `binrw` and utility test helpers.

## Risks And Test Signals
`from_slice` fails on non-16-byte inputs via `try_into`. Random collision probability is assumed low but not impossible; `LockingBlockStore::create` still retries on `try_create` collision. Tests cover binary round-trip, display hex, and debug format.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/block_id.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/cache/cache_impl.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/cache/cache_impl.rs

## Purpose
Implements the internal lockable LRU cache used by `LockingBlockStore` to serialize per-block operations, buffer dirty data, and prune/flush cached blocks.

## APIs, Flow, And State
`BlockCacheImpl<B>` owns an optional `Arc<LockableLruCache<BlockId, BlockCacheEntry<B>>>` and an eventually consistent `AtomicU64` count of blocks present only in cache. `async_lock` acquires an owned lock with a soft entry limit of 10,240 and invokes an async eviction callback. `set_entry`, `set_or_overwrite_entry_even_if_dirty`, delete helpers, and `flush_entry` maintain dirty/base-store state and the not-yet-in-base counter. `into_entries_unordered` waits until all other cache references are gone, then consumes the LRU entries.

## Dependencies And Integration
Built on the `lockable` crate, Tokio yielding, `Arc`, atomics, and `BlockCacheEntry`. `BlockCache` wraps it with periodic pruning and async-drop orchestration; `LockingBlockStore` uses it as both cache and per-ID mutex table.

## Risks And Test Signals
The file contains deliberate assertions to catch counter underflow, deleting unset entries, setting over existing entries, and dirty drop mistakes. Busy-wait loops on `Arc::strong_count` can deadlock if a current task holds a guard while waiting on drop. The counter is explicitly eventually consistent during concurrent mutations, so exact counts are reliable only at quiescent points.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/cache/cache_impl.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/cache/entry.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/cache/entry.rs

## Purpose
Defines the cache entry value stored for each locked/cached block and the state enums used to track dirtiness and base-store presence.

## APIs, Flow, And State
`CacheEntryState` is `Dirty` or `Clean`; `BlockBaseStoreState` records whether the block exists in the base store. `BlockCacheEntry<B>` holds the base store guard, dirty flag, `Data`, and base-store state. `data_mut` and `resize` mark the entry dirty. `_flush_to_base_store` writes dirty data to the base store, marks it clean, updates base-store state, and returns a `FlushResult`. `discard` marks dirty data clean so intentional deletion can drop it without panic.

## Dependencies And Integration
Entries are owned by `BlockCacheImpl` and exposed through `BlockCacheEntryGuard` and `LockingBlock`. They call low-level `store` on the base store and use `safe_panic!` in `Drop`.

## Risks And Test Signals
Dropping a dirty entry panics, which is an important safety net but makes correct flush/discard paths critical. `_flush_to_base_store` does not update `BlockCacheImpl`'s counter by itself; callers must use `flush_entry` unless the cache is already being destroyed.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/cache/entry.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/cache/guard.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/cache/guard.rs

## Purpose
Wraps the `lockable` owned guard for a cached block entry and exposes a narrow API to the locking blockstore.

## APIs, Flow, And State
`BlockCacheEntryGuard<B>` holds the owned guard from `LockableLruCache`. It exposes `key`, immutable/mutable `value`, and `insert`, preserving lock ownership for the guarded block ID. Debug prints the underlying guard.

## Dependencies And Integration
Used by `LockingBlock` and `LockingBlockStore` to keep a block locked while it is loaded or being removed. It abstracts the exact lockable guard type from most of the high-level implementation.

## Risks And Test Signals
Correctness depends on guard lifetime: dropping it releases the per-block lock and may allow cache pruning/removal. Tests around removal and cache flushing indirectly validate that locks survive long enough for operations.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/cache/guard.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/cache/mod.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/cache/mod.rs

## Purpose
Provides the public cache wrapper used by `LockingBlockStore`, including periodic pruning, test pruning hooks, block locking, flushing, and async-drop flushing.

## APIs, Flow, And State
`BlockCache<B>` owns a `BlockCacheImpl` and a `PeriodicTask` that prunes entries every 500 ms if they have been unlocked for at least 500 ms. `async_lock` acquires a cache entry and wires eviction to `_prune_blocks`. Test/testutils hooks `prune_unloaded_blocks` and `prune_all_blocks` force cache cleanup. `_prune_block` flushes dirty entries and deletes them. `async_drop_impl` stops the prune task and drains/flushed all remaining entries concurrently.

## Dependencies And Integration
Wraps `BlockCacheImpl`, `BlockCacheEntry`, `BlockCacheEntryGuard`, `PeriodicTask`, `futures::join`, and `cryfs_utils::stream::for_each_unordered`. It is the persistence bridge between high-level dirty block handles and the low-level base store.

## Risks And Test Signals
Comments identify potential deadlocks from arbitrary lock ordering and busy waiting for `Arc` references to disappear. Dirty data persistence relies on async-drop being called; intentional deletion must use discard/delete helpers. Generic high-level blockstore tests exercise normal cache behavior with and without forced flush, but several TODOs request more direct prune tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/cache/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/locking_block.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/locking_block.rs

## Purpose
Defines `LockingBlock`, the loaded high-level block handle returned by `LockingBlockStore`.

## APIs, Flow, And State
`LockingBlock<B>` owns a `BlockCacheEntryGuard<B>`, so holding the block also holds the per-block cache lock. The `Block` implementation returns the guarded `BlockId`, data reference, mutable data reference, and async resize. Mutable data access and resize delegate to `BlockCacheEntry`, marking entries dirty.

## Dependencies And Integration
Used as `LockingBlockStore::Block`. It depends on `BlockCacheEntryGuard`, the high-level `Block` trait, and low-level `LLBlockStore` bounds.

## Risks And Test Signals
Methods assume a loaded block always has a cache value and panic if the guarded entry is `None`. This invariant depends on store load/create/remove control flow. Debug output includes ID and cache entry state for diagnostics.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/locking_block.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/locking_blockstore.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/locking_blockstore.rs

## Purpose
Implements the primary high-level blockstore wrapper that adds per-block locking, write-back caching, random-ID creation, and high-level `Block` handles over a low-level store.

## APIs, Flow, And State
`LockingBlockStore<B>` owns an optional `Arc<AsyncDropGuard<B>>` base store plus a `BlockCache`. `load` locks the ID, loads from base store if absent from cache, inserts a clean cache entry, and returns `LockingBlock`. `try_create` locks the ID, rejects cache/base-store existence, and inserts a dirty entry marked absent from base store. `overwrite` sets or replaces a dirty cache entry, checking base existence only when needed. `_remove` removes cached data and optionally removes from base store depending on known base-store state. `num_blocks` combines base count with dirty cache-only blocks; `all_blocks` merges cache keys with base-store stream while filtering duplicates. `create` loops random IDs until `try_create` succeeds.

## Dependencies And Integration
Bridges high-level `BlockStore` to low-level `LLBlockStore`. It relies on `BlockCache`, `BlockBaseStoreState`, `CacheEntryState`, `futures` stream combinators, `HashSet`, and `RemoveResult`/`TryCreateResult`.

## Risks And Test Signals
Persistence depends on flushing dirty cache entries through explicit `flush_block`, pruning, clear-cache hooks, or async drop. Comments flag dangerous lock lifetime in `_remove`, possible inefficiency from double existence checks on create/flush, uncertain `all_blocks` semantics for locked entries, and exception-safety around drop failures. Tests cover generic high-level semantics, create passthrough, random ID retry, remove-before-flush avoiding base removal, remove-after-flush actually removing, error propagation, and overhead forwarding.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/locking_blockstore.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/mod.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/mod.rs

## Purpose
Module hub for the high-level locking blockstore implementation.

## APIs, Flow, And State
Declares the internal `cache` module, exposes `LockingBlock` and `LockingBlockStore`, and includes locking tests under `cfg(test)`.

## Dependencies And Integration
Re-exported by `high_level::implementations` and ultimately by the crate root as the main high-level blockstore implementation.

## Risks And Test Signals
No runtime logic is present here. The important boundary is keeping cache internals private while exposing only the block and store wrappers.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/tests.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/tests.rs

## Purpose
Tests `LockingBlockStore` with generic high-level blockstore conformance and targeted cache/base-store behavior.

## APIs, Flow, And State
`TestFixture` creates `LockingBlockStore<InMemoryBlockStore>` and runs the generic high-level suite with forced cache flush and without. Targeted tests build `MockBlockStore` expectations for create data passthrough, returned random ID consistency, removing an unflushed newly-created block without touching the base store, removing after flush, retrying random IDs when collisions are reported, propagating `exists` errors, and forwarding overhead.

## Dependencies And Integration
Uses `mockall`, `AtomicUsize`, `Arc<Mutex<_>>`, `Overhead`, `Byte`, and high-level test fixtures. It depends on mock low-level store methods such as `exists`, `store`, `remove`, and `overhead`.

## Risks And Test Signals
Some tests note potential flakiness because background pruning could flush entries unexpectedly; a future deterministic pruning control would strengthen them. The suite is a key signal for cache state transitions, especially the regression where a flushed new block must later be considered present in the base store so removal reaches the base store.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/tests.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/mod.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/mod.rs

## Purpose
Collects high-level blockstore implementations and feature-gated test utility wrappers.

## APIs, Flow, And State
Always declares/re-exports `locking::LockingBlockStore`. Under test/testutils it declares and re-exports `tracking::{ActionCounts, TrackingBlockStore}` and `shared::SharedBlockStore`.

## Dependencies And Integration
Consumed by `high_level::mod.rs` and crate-root re-exports. This is the visibility gate separating production implementation from test instrumentation/shared wrappers.

## Risks And Test Signals
The module is simple but controls public API exposure. Incorrect feature gating could leak test utilities into production or hide them from downstream test crates.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/shared.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/shared.rs

## Purpose
Provides a test/testutils high-level blockstore wrapper that can be cloned by sharing an underlying store through `AsyncDropArc`.

## APIs, Flow, And State
`SharedBlockStore<B>` owns `AsyncDropGuard<AsyncDropArc<B>>`. `new` wraps an underlying async-drop store, and `clone` clones the shared arc into a new async-drop guard. The `BlockStore` implementation delegates all operations, including test cache clearing. `Deref` exposes the underlying store, and `AsyncDrop` delegates to the shared arc.

## Dependencies And Integration
Generic over `BlockStore + AsyncDrop + Debug + Send + Sync` with sendable blocks. Tests instantiate it over `LockingBlockStore<InMemoryBlockStore>` and run generic high-level tests with and without cache flushing.

## Risks And Test Signals
Shared drop semantics are the main concern: clones must not prematurely drop the underlying store, and final async drop must flush/close it exactly when the last guard goes away. The generic suite validates behavior through a shared wrapper but does not exhaustively stress clone lifetimes.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/shared.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/tracking/action_counts.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/tracking/action_counts.rs

## Purpose
Defines high-level blockstore action counters for the test/testutils tracking wrapper.

## APIs, Flow, And State
`ActionCounts` tracks store operations (`load`, `try_create`, `overwrite`, removals, counts, free-space, overhead, all_blocks, create, flush_block) and block operations (`data`, `data_mut`, `resize`, named `blob_*` in the struct). It derives addition/add-assign/sum/equality/copy and provides `ZERO`. Custom `Debug` prints only non-zero fields.

## Dependencies And Integration
Used by `TrackingBlockStore` and `TrackingBlock` behind `Arc<Mutex<_>>`. Re-exported under test/testutils as `HLActionCounts` from the crate root.

## Risks And Test Signals
Field names use `blob_` for block-level actions, which can confuse readers because this is the blockstore crate. Tests verify zero state, each counter, and reset aggregation.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/tracking/action_counts.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/tracking/mod.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/tracking/mod.rs

## Purpose
Module hub for high-level blockstore tracking utilities.

## APIs, Flow, And State
Declares `action_counts`, `tracking_block`, and `tracking_blockstore`, then re-exports `ActionCounts` and `TrackingBlockStore`. Tests are compiled under `cfg(test)`.

## Dependencies And Integration
Enabled only through the parent module's test/testutils gate, making it available for performance and behavior assertions without becoming core production API.

## Risks And Test Signals
Runtime logic lives in child modules. The main risk is incomplete re-exporting when new tracking utilities are added.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/tracking/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/tracking/tests.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/tracking/tests.rs

## Purpose
Tests high-level `TrackingBlockStore` transparency and exact counter behavior.

## APIs, Flow, And State
The fixture wraps `LockingBlockStore<InMemoryBlockStore>` and runs the generic high-level suite in flushing and non-flushing modes. Individual tests assert counters for load, overwrite, remove by ID, remove by loaded block, try-create success/failure, create, block resize, flush, data/data_mut access, block count, free-space estimate, overhead calls, all_blocks stream creation, and `get_and_reset_counts`.

## Dependencies And Integration
Uses high-level `Block`/`BlockStore` traits, `Data`, `BlockId`, `Byte`, futures stream collection, and `pretty_assertions`. It exercises the tracking wrapper on top of the real locking store rather than a mock.

## Risks And Test Signals
The tests are detailed instrumentation signals but mostly sequential; they do not stress concurrent counter updates beyond generic multi-thread execution. The aggregate reset test verifies that counters can be accumulated across mixed operations and reset to zero.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/tracking/tests.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/tracking/tracking_block.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/tracking/tracking_block.rs

## Purpose
Wraps a high-level block and increments shared counters when data is read, data is mutably accessed, or the block is resized.

## APIs, Flow, And State
`TrackingBlock<B>` owns the underlying block and shared `Arc<Mutex<ActionCounts>>`. Public/internal helpers are `new`, `inner_mut`, and `into_inner`. The `Block` implementation forwards `block_id`, increments `blob_data` before `data`, increments `blob_data_mut` before `data_mut`, and increments `blob_resize` before resize.

## Dependencies And Integration
Used as `TrackingBlockStore<B>::Block`. It preserves the underlying block for `remove` and `flush_block` through `into_inner` and `inner_mut`.

## Risks And Test Signals
`block_id` intentionally is not counted. Mutable data access marks the underlying locking cache entry dirty through the wrapped block. Tests cover data, data_mut, resize, remove, and flush paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/tracking/tracking_block.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/tracking/tracking_blockstore.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/tracking/tracking_blockstore.rs

## Purpose
Provides a high-level blockstore wrapper that records action counts while preserving the underlying store's behavior.

## APIs, Flow, And State
`TrackingBlockStore<B>` owns an `AsyncDropGuard<B>` and shared `Arc<Mutex<ActionCounts>>`. `counts` snapshots counters, and `get_and_reset_counts` atomically replaces them with `ZERO`. Most store methods increment before forwarding; `create` increments after successful underlying create, so failed creates are not counted. Loaded blocks are wrapped in `TrackingBlock`. `remove` unwraps the tracking block via `into_inner`; `flush_block` forwards a mutable reference to the underlying block through `inner_mut`.

## Dependencies And Integration
Generic over high-level `BlockStore + AsyncDrop + Debug + Send + Sync`, with blocks that are `Send + Sync`. Test/testutils cache clearing passes through uncounted.

## Risks And Test Signals
Counting after successful `create` differs from methods that count attempts, which matters for interpreting metrics. The mutex is not held across awaited calls except for quick increments. Tests cover counters, generic behavior, and reset.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/tracking/tracking_blockstore.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/interface.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/high_level/interface.rs

## Purpose
Defines the high-level block and blockstore traits used by cache-aware blockstore implementations.

## APIs, Flow, And State
`Block` exposes `block_id`, immutable/mutable `Data`, and async resize. `BlockStore` exposes load, try-create, overwrite, remove by ID, remove by loaded block, count/free-space/overhead queries, `all_blocks`, random-ID create, flush of a loaded block, and test/testutils cache clearing. Stream methods explicitly do not guarantee a consistent snapshot during concurrent mutations.

## Dependencies And Integration
High-level stores sit above low-level `LLBlockStore` implementations and below blobstore data-tree code. The trait uses `BlockId`, `Overhead`, `RemoveResult`, `TryCreateResult`, `Byte`, `Data`, and boxed futures streams.

## Risks And Test Signals
The trait allows mutable block handles to carry dirty state that must be flushed by store implementations. Comments note a future migration opportunity away from direct `LockingBlockStore` use. Generic high-level blockstore tests validate implementors.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/interface.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/mod.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/high_level/mod.rs

## Purpose
High-level blockstore module root.

## APIs, Flow, And State
Declares `interface` and re-exports `Block`/`BlockStore`; declares `implementations` and re-exports `LockingBlockStore`. Test/testutils re-exports include `ActionCounts`, `SharedBlockStore`, and `TrackingBlockStore`.

## Dependencies And Integration
Feeds the crate root public API and separates high-level block abstractions from low-level storage adapters.

## Risks And Test Signals
No runtime logic is present. Feature-gated re-exports must remain aligned with the parent implementations module.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/lib.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/lib.rs

## Purpose
Crate root for `cryfs-blockstore`, exposing block IDs, high-level and low-level storage APIs, implementations, overhead utilities, and test helpers.

## APIs, Flow, And State
The crate re-exports `BlockId`, `BLOCKID_LEN`, `RemoveResult`, `TryCreateResult`, high-level `Block`, `BlockStore`, `LockingBlockStore`, and many low-level implementations such as encrypted, compressed, in-memory, on-disk, integrity, dynamic, read-only, and optimized writer types. Under test/testutils it re-exports high-level and low-level tracking/shared/mock/tempdir utilities and the `tests` module. A static assertion ensures `byte_unit::Byte` has the expected `u64` size.

## Dependencies And Integration
Connects internal modules `block_id`, `utils`, `high_level`, `low_level`, and `overhead`. `cryfs_version::assert_cargo_version_equals_git_version!()` enforces version consistency.

## Risks And Test Signals
The root public surface is broad, so accidental re-export changes can affect downstream crates. The static Byte-size assertion protects storage calculations from feature-induced type-width changes.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/box_dyn.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/box_dyn.rs

## Purpose
Provides `DynBlockStore`, a dynamic-dispatch wrapper around `Box<dyn LLBlockStore + Send + Sync>`.

## APIs, Flow, And State
`DynBlockStore` implements `BlockStoreReader`, `BlockStoreWriter`, `BlockStoreDeleter`, `AsyncDrop`, and marker `LLBlockStore` by forwarding every call to the boxed trait object. It supports existence/load/count/free-space/overhead/all-blocks queries, create/store writes, remove, and async drop.

## Dependencies And Integration
Used where concrete low-level blockstore types need type erasure while preserving the full low-level store interface.

## Risks And Test Signals
The wrapper adds dynamic dispatch and hides concrete type capabilities such as optimized allocation type. It must be updated if low-level traits gain required methods. There are no local tests in this file; coverage is indirect through consumers of dynamic stores.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/box_dyn.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/compressing.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/compressing.rs

## Purpose
Implements a low-level blockstore decorator that LZ4-frame compresses block payloads before storage and decompresses them on load. The file notes it is currently intended for tests rather than optimized production use.

## APIs, Flow, And State
`CompressingBlockStore<B>` owns an underlying async-drop store. Reads delegate `exists`, count, free-space, overhead, and all-blocks; `load` fetches compressed data then `_decompress`es it with `tokio::task::spawn_blocking`. Writes implement `OptimizedBlockStoreWriter` by extracting data, `_compress`ing it with `lzzzz::lz4f`, and forwarding to non-optimized `try_create`/`store` because compressed sizes do not preserve prefix-space assumptions. `AsyncDrop` delegates to the underlying store.

## Dependencies And Integration
Requires underlying reader/deleter/optimized-writer traits as appropriate. It composes with any `LLBlockStore + OptimizedBlockStoreWriter` and participates in generic low-level blockstore tests over `InMemoryBlockStore`.

## Risks And Test Signals
Reported overhead ignores compression and can be inaccurate, especially because compression can reduce physical size. Compression/decompression errors propagate with context on load. Tests run the generic low-level suite and verify overhead conversion with zero added overhead.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/compressing.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/encrypted/mod.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/encrypted/mod.rs

## Purpose
Implements a low-level blockstore decorator that encrypts data before storage and decrypts/authenticates data on load.

## APIs, Flow, And State
`EncryptedBlockStore<C, _B, B>` owns an underlying async-drop store, an `Arc<C>` cipher, and a shared global crypto thread pool. Reads delegate metadata and `exists`; `load` fetches ciphertext, verifies/removes a two-byte `FORMAT_VERSION_HEADER`, then decrypts. `overhead` adds the header plus cipher prefix/suffix overhead to the underlying store's overhead. Optimized writes allocate enough underlying prefix/suffix space, shrink the exposed mutable region to plaintext, then encrypt, prepend the header, and forward underlying optimized writes. `remove` and async drop delegate.

## Dependencies And Integration
Uses `cryfs_crypto::symmetric::CipherDef`, `LazyReclaim<ThreadPool>`, `Data` region growth/shrink APIs, and low-level blockstore reader/deleter/optimized-writer traits. Generic tests instantiate AES-256-GCM, AES-128-GCM, and XChaCha20-Poly1305 over `InMemoryBlockStore`.

## Risks And Test Signals
The header is encoded with `u16::to_ne_bytes`, so it is native-endian and should not be changed lightly for cross-platform persistence. `_check_and_remove_header` slices `data[..FORMAT_VERSION_HEADER.len()]` in the error path, so too-short data can panic rather than return a clean parse error. Tests cover generic low-level behavior, overhead calculations, successful same-key load, wrong-key failure, and tamper failure.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/encrypted/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/inmemory.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/inmemory.rs

## Purpose
Implements a simple in-memory low-level blockstore backed by an `RwLock<HashMap<BlockId, Data>>`.

## APIs, Flow, And State
`InMemoryBlockStore::new` returns an async-drop guard. Reader methods lock the map for `exists`, `load`, `num_blocks`, and `all_blocks`; load clones stored `Data`, and all-blocks snapshots keys into a vector-backed stream. Free-space estimate uses `sysinfo` available memory, and overhead is zero. Writer methods implement optimized allocation with a local `BlockData` wrapper, `try_create_optimized`, and `store_optimized`. Remove deletes from the map and returns `RemoveResult`.

## Dependencies And Integration
Implements `BlockStoreReader`, `BlockStoreDeleter`, `OptimizedBlockStoreWriter`, `AsyncDrop`, and `LLBlockStore`. Used heavily by tests as the base low-level store under locking, encryption, compression, and blobstore implementations.

## Risks And Test Signals
State is process-local and non-persistent; it is appropriate for tests and transient stores. Poisoned lock acquisition is converted into `anyhow` errors. Tests run the generic low-level suite and verify zero-overhead size conversions.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/inmemory.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/integrity/integrity_data/integrity_violation_error.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/integrity/integrity_data/integrity_violation_error.rs

## Purpose
Defines structured errors for integrity violations detected by the low-level integrity blockstore.

## APIs, Flow, And State
`IntegrityViolationError` variants are `RollBack`, `WrongBlockId`, `MissingBlock`, and `MissingBlocks`. Rollback captures the block, source/destination client IDs, last-seen versions, and actual version. Wrong ID records filename/header mismatch. Missing variants record one or many expected block IDs. The enum derives `thiserror::Error`, `Debug`, `PartialEq`, and `Clone`.

## Dependencies And Integration
Uses integrity metadata types `BlockVersion`, `ClientId`, `MaybeClientId`, and crate `BlockId`. These errors are re-exported through the integrity blockstore API and surfaced when tampering, deletion, rename, or rollback is detected.

## Risks And Test Signals
The error messages are security-facing diagnostics and should not lose the block/client/version context needed for incident analysis. `MissingBlocks` owns a `HashSet`, so displayed order is nondeterministic; tests should compare variants structurally rather than strings when possible.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/integrity/integrity_data/integrity_violation_error.rs -->
