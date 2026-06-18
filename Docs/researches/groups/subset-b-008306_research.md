# subset-b-008306 Research

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/mod.rs -->
## sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/mod.rs

Purpose: defines `DataNodeStore<B>`, the block-backed storage layer for CryFS data nodes. It adapts an arbitrary `BlockStore + AsyncDrop` into typed `DataNode` values (`DataLeafNode` or `DataInnerNode`) with a computed `NodeLayout`, enforcing a minimum usable block size large enough for the node header plus at least two child block IDs.

Important APIs and types: `DataNodeStore::new` computes usable block size from lower-store `Overhead` and wraps the store in `AsyncDropGuard`; `load` parses a lower-level block into a typed node; `create_new_leaf_node`, `try_create_new_leaf_node`, `create_new_inner_node`, and `create_new_node_as_copy_from` serialize typed nodes and reload them as typed handles; `overwrite_with_leaf_node` rewrites an existing block ID as leaf data; `remove`, `remove_by_id`, `num_nodes`, `estimate_space_for_num_blocks_left`, `logical_block_size_bytes`, and `flush_node` expose lower-store behavior through the data-node abstraction. Test-only APIs expose `all_nodes` and cache clearing.

Control flow: construction validates block sizing before returning the guard, and explicitly drops the lower block store if validation fails. Leaf creation allocates a full block-sized data region, shrinks to the payload subregion, copies the caller payload into the prefix, serializes header plus data, creates/try-creates in the lower store, then reloads to verify it is a leaf. Inner-node creation serializes depth and child IDs and similarly reloads to verify the node kind. Copy creation asserts that the source raw block size matches this store layout, creates a raw copy, then reloads it. `flush_node` delegates to `DataNode::flush`, so in-memory mutation of loaded nodes is persisted only when flushed or when lower cache behavior writes through.

State and persistence behavior: the store itself holds only the lower `block_store`, `layout`, and `physical_block_size`; persisted state lives in lower blocks. Physical block size is retained for free-space estimates, while logical block size is the maximum leaf payload. `overwrite_with_leaf_node` can replace an inner node with a leaf at the same block ID, which is intentional for root replacement paths but dangerous if used on arbitrary tree children. Removal is not recursive here; callers must remove child subtrees themselves.

Dependencies and integration points: depends on `cryfs_blockstore` for `BlockId`, block-store traits, `TryCreateResult`, `RemoveResult`, and block ID length; `cryfs_utils` for `Data` and async-drop guards; `binary_layout` and local `layout`/`data_node` modules for serialization. It is consumed by `DataTreeStore`, `DataTree`, traversal logic, and the block-store adapter tests.

Risks: many size violations use panics/assertions rather than recoverable errors, including oversized leaf payloads and mismatched copy layouts. `create_*` APIs create and then reload, adding I/O and a possible inconsistency surface if the lower store behaves unexpectedly. Flush semantics are cache-dependent and not recursive. The minimum block-size rule only guarantees inner nodes can branch; deeper integrity is enforced by `DataNode` parsing and tree traversal.

Test signals: embedded async tests cover valid/invalid construction, overhead-derived layouts, loading leaf/inner nodes, leaf creation at empty/partial/full sizes and too-large panic cases, try-create collision preservation, inner-node creation variants, raw-copy equality, node counts, targeted removal without affecting other nodes, overwriting node kinds, explicit flush of created/loaded leaf and inner nodes, free-space calculations, logical block size, and all-node streaming.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/test_as_blockstore/block_store_adapter.rs -->
## sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/test_as_blockstore/block_store_adapter.rs

Purpose: provides `BlockStoreAdapter`, a test-only wrapper that makes `DataNodeStore<LockingBlockStore<InMemoryBlockStore>>` satisfy the low-level block-store test traits. It lets the standard `cryfs_blockstore` low-level suite validate data-node leaf storage as if it were a block store.

Important APIs and types: `MAX_BLOCK_SIZE` gives the adapter a large physical block size; `BlockStoreAdapter(AsyncDropGuard<DataNodeStore<...>>)` owns the node store; `new` builds an in-memory locking lower store; `clear_cache_slow` supports flush-sensitive fixtures; `load_leaf` loads and rejects inner nodes. Trait implementations cover `BlockStoreReader`, `BlockStoreDeleter`, `BlockStoreWriter`, `Debug`, `AsyncDrop`, `LLBlockStore`, and `LLFixture` through `TestFixtureAdapter<const FLUSH_CACHE_ON_YIELD: bool>`.

Control flow: reads call `load_leaf` and convert leaf payloads back to `Data`; `exists` is a load check; `num_blocks` delegates to `num_nodes`; `all_blocks` delegates to test-only `all_nodes`. Deletion loads the leaf first, then removes its upcast node or reports `NotRemovedBecauseItDoesntExist`. `try_create` performs an existence check before `store`; `store` calls `overwrite_with_leaf_node`, which means a specific ID is written by overwriting that ID as a leaf rather than using random ID allocation.

State and persistence behavior: all storage is in memory under the wrapped `DataNodeStore`; optional fixture yielding can clear the underlying cache to force reload paths. `estimate_num_free_bytes` converts estimated free physical blocks back into logical leaf bytes. The adapter declares overhead equal to the serialized node header offset, matching the leaf payload loss introduced by `DataNodeStore`.

Dependencies and integration points: imports low-level block-store test traits/macros from `cryfs_blockstore::tests::low_level`, the `DataNodeStore` API, local layout constants, and async-drop utilities. It is used by `test_as_blockstore/mod.rs` to instantiate the same block-store conformance suite with and without cache flushing.

Risks: `store` does not check existence and can overwrite existing entries, which is consistent with `BlockStoreWriter::store` but must be distinguished from `try_create`. `load_leaf` panics if an inner node appears, relying on the adapter suite to only create leaves. Capacity and overhead are approximate test translations rather than production allocation logic.

Test signals: the adapter itself is exercised indirectly by the full low-level block-store test suite in two cache modes, giving broad coverage for existence, load, create, overwrite, remove, enumeration, and async drop behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/test_as_blockstore/block_store_adapter.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/test_as_blockstore/mod.rs -->
## sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/test_as_blockstore/mod.rs

Purpose: wires `BlockStoreAdapter` into the reusable low-level block-store test matrix. This is a compact test module whose role is integration, not production behavior.

Important APIs and types: it declares `mod block_store_adapter;` and two nested test modules, `with_flushing` and `without_flushing`. Each invokes `cryfs_blockstore::instantiate_blockstore_tests_for_lowlevel_blockstore!` with `block_store_adapter::TestFixtureAdapter<true>` or `<false>` and the `"multi_thread"` flavor.

Control flow: when compiled for tests, the macro expands a suite of low-level block-store conformance tests. The `with_flushing` variant clears adapter caches on fixture yield; `without_flushing` leaves caches warm. This makes the same behavioral expectations run over both persisted/reloaded and cache-resident paths.

State and persistence behavior: this file owns no state. Its key persistence signal is that all adapter operations must pass with cache flushing enabled, meaning correctness cannot depend solely on in-memory `DataNode` handles.

Dependencies and integration points: depends on the sibling `block_store_adapter` module and the shared `cryfs_blockstore` test macro. It integrates `DataNodeStore` testing with the lower-level block-store contract, complementing the node-store-specific tests in `data_node_store/mod.rs`.

Risks: because behavior is macro-generated, test coverage is less visible from this file alone. The suite only validates the data-node store when used as leaf-only block storage; it does not validate inner-node tree semantics.

Test signals: strong conformance signal for the leaf-as-block behavior across both flushed and unflushed cache modes, with multi-thread flavor selected.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/test_as_blockstore/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/testutils.rs -->
## sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/testutils.rs

Purpose: supplies deterministic constructors and assertions for `DataNodeStore` unit tests. It standardizes physical block size, random data generation, node creation, typed loading, and validation helpers.

Important APIs and types: `PHYSICAL_BLOCK_SIZE` is 1024 bytes. Helpers include `new_full_leaf_node`, `new_empty_leaf_node`, `new_inner_node`, `new_full_inner_node`, `new_full_leaves`, `new_inner_nodes`, `load_node`, `load_inner_node`, `load_leaf_node`, `with_nodestore`, `with_nodestore_with_blocksize`, `half_full_leaf_data`, `full_leaf_data`, `data_fixture`, and `assert_full_inner_node_is_valid`.

Control flow: fixture runners create a `DataNodeStore<LockingBlockStore<InMemoryBlockStore>>`, pass a borrowed store into an async closure, then explicitly `async_drop` it. Node factories create leaves and inner nodes through the public store APIs, often using `future::join_all` or `join!` to create multiple children concurrently. Typed load helpers panic on unexpected node kind, which keeps tests concise and fails loudly on serialization or parsing mistakes.

State and persistence behavior: all helpers use in-memory stores, but they still go through `DataNodeStore` serialization and lower-store APIs. Deterministic data comes from `SmallRng::seed_from_u64`, making expected payloads reproducible. Full/half leaf helpers derive sizes from `NodeLayout`, so tests track header-size changes.

Dependencies and integration points: used by `data_node_store/mod.rs` tests and indirectly by tree test helpers. Depends on `rand`, `futures`, `byte_unit`, local `NodeLayout`, and the in-memory locking block store. It intentionally uses public APIs rather than constructing raw nodes directly, so helper failures reveal public contract regressions.

Risks: panics and unwraps are acceptable in tests but can obscure underlying errors if a helper is reused in broader harnesses. `new_inner_node` creates a depth-1 inner node with two leaves; it does not validate deeper structure. The commented shared-block helper suggests historical/shared-cache test setups were removed or deferred.

Test signals: the helper set enables coverage of empty, half-full, full, and multi-child nodes; deterministic data comparison; and validation that inner nodes have expected depth, child count, and loadable children.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/testutils.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_tree_store/mod.rs -->
## sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_tree_store/mod.rs

Purpose: module facade for the data-tree layer built on `DataNodeStore`. It groups size caching, store-level APIs, traversal algorithms, and the `DataTree` object, then exports the public surface.

Important APIs and types: declares private modules `size_cache`, `store`, `traversal`, and `tree`, plus test-only `testutils`. Public re-exports are `DataTreeStore`, `LoadNodeError`, and `DataTree`.

Control flow: there is no runtime logic in this file. Compile-time organization ensures external users import the tree store and tree type from this module while implementation details remain private, except `LoadNodeError` which is exposed for subtree streaming failures.

State and persistence behavior: none directly. Persistence is delegated to `store.rs` and `tree/mod.rs`, and size/traversal state is encapsulated in private modules.

Dependencies and integration points: parent modules can depend on `data_tree_store::DataTreeStore` and `DataTree` without knowing file layout. Test utilities are available only under `#[cfg(test)]`, while production exports stay narrow.

Risks: the module boundary hides `size_cache` and traversal internals, so external tests must exercise them through `DataTree` and `DataTreeStore`. That is generally good encapsulation but leaves `SizeCache` with a TODO for direct tests in its own file.

Test signals: indirect; it includes test utilities only for unit tests and exposes the modules whose embedded tests cover behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_tree_store/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_tree_store/size_cache.rs -->
## sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_tree_store/size_cache.rs

Purpose: implements `SizeCache`, the lazy cache for a `DataTree`'s number of leaves and total byte count. It uses the tree invariant that all leaves except the rightmost are full, so total bytes can be derived from leaf count plus rightmost leaf size.

Important APIs and types: `SizeCache` has states `SizeUnknown`, `RootIsInnerNodeAndNumLeavesIsKnown { num_leaves, rightmost_leaf_id }`, and `NumBytesIsKnown { num_leaves, rightmost_leaf_num_bytes }`. Main methods are `get_or_calculate_num_leaves`, `get_or_calculate_num_bytes`, `update`, and `_calculate_leaf_size`. Helper `NumLeavesAndRightmostLeafId` and recursive `calculate_num_leaves_and_rightmost_leaf_id` find the right border of an inner-rooted tree.

Control flow: leaf-rooted unknown caches immediately become `NumBytesIsKnown` with one leaf. Inner-rooted unknown caches traverse down the last child chain; for each inner level, all left siblings are assumed full and counted via `layout.num_leaves_per_full_subtree(depth - 1)`, while the last child is loaded recursively until the rightmost leaf ID is found. Byte calculation may then load that rightmost leaf to read its actual size. `update` is called after write/resize operations with authoritative leaf count and byte count, deriving the rightmost leaf size by subtracting full left leaves.

State and persistence behavior: cache state is in-memory only and lives inside `DataTree`. It stores a block ID when only leaf count is known to avoid loading the rightmost leaf until total bytes are requested. A comment notes a deadlock risk if a leaf root were stored as `rightmost_leaf_id` and then loaded while already borrowed, so leaf roots cache byte size directly.

Dependencies and integration points: called by `DataTree::num_bytes`, `num_nodes`, `_traverse_leaves_by_byte_indices`, and `resize_num_bytes`. It depends on `DataNodeStore` loading, `NodeLayout` capacity math, `BlockId`, and `NonZeroU64`.

Risks: correctness depends on the tree being left-packed and all non-rightmost leaves being full. Corrupt depth metadata, missing children, or a leaf where an inner node is expected produce errors. `update` unwraps conversion of computed rightmost size to `u32`; this is safe if layout limits are honored but would panic on violated invariants. The file itself has TODOs for tests.

Test signals: no direct tests in this file. Indirect coverage comes from `DataTree` tests that compare cached and recalculated `num_bytes`/`num_nodes`, write growth, resize shrink/growth, and reload after cache clearing.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_tree_store/size_cache.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_tree_store/store.rs -->
## sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_tree_store/store.rs

Purpose: defines `DataTreeStore<B>`, the high-level store for creating, loading, removing, flushing, and enumerating byte trees backed by `DataNodeStore`.

Important APIs and types: `DataTreeStore` wraps `AsyncDropGuard<AsyncDropArc<DataNodeStore<B>>>` so loaded trees share the node store with async-drop semantics. Public APIs include `new`, `load_tree`, `create_tree`, `try_create_tree`, `remove_tree_by_id`, `num_nodes`, `estimate_space_for_num_blocks_left`, `logical_block_size_bytes`, `load_block_depth`, `into_inner_node_store`, `load_all_nodes_in_subtree_of_id`, `flush_tree_if_cached`, and test-only `all_tree_roots`/cache clearing.

Control flow: construction delegates block-size validation to `DataNodeStore::new`. `create_tree` creates one empty leaf and wraps it as a `DataTree`; `try_create_tree` does the same at a caller-provided root ID and returns `None` on collision. `load_tree` loads a root node and wraps it if present. `remove_tree_by_id` loads a tree and calls `DataTree::remove` for recursive deletion. `flush_tree_if_cached` reloads the entire tree and flushes it because there is no dirty-node index yet.

State and persistence behavior: persistent tree state is the graph of node blocks rooted at a `BlockId`; the store itself holds only the shared node store. Removing a tree deletes the recursive subtree, not just the root. `all_tree_roots` reconstructs candidate roots by loading all nodes and subtracting every child ID, which is intentionally test-only and inefficient. Async drop delegates to the shared node store.

Dependencies and integration points: integrates lower-level `DataNodeStore`, `DataTree`, and traversal subtree streaming. It is the likely external API for blob/file data storage and is used extensively by `data_tree_store/testutils.rs` and `tree/tests.rs`.

Risks: `load_tree` trusts the caller-provided root ID; if it points to an interior node, the returned tree treats that subtree as an independent tree. `flush_tree_if_cached` is expensive and has a TODO noting lack of dirty tracking. `load_block_depth` is marked TODO Test. Shared `AsyncDropArc` requires careful ownership so active trees do not outlive required drops.

Test signals: embedded tests cover invalid/valid construction, tree loading, create and try-create behavior, ID collision, recursive removal including preserving other trees, node counts after add/remove, free-space estimation, and logical block size. `all_tree_roots` supports testing root discovery but is not a production path.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_tree_store/store.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_tree_store/testutils.rs -->
## sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_tree_store/testutils.rs

Purpose: provides fixtures and expected-value calculators for `DataTreeStore`/`DataTree` tests, especially multi-leaf and slow feature-gated tree tests.

Important APIs and types: `PHYSICAL_BLOCK_SIZE` is 128 bytes to force shallow tests into multi-node trees. `TreeFixture` records `root_id`, data seed, and byte length, with constructors `create_tree_with_data` and `create_tree_with_data_and_id` plus `assert_data_is_still_intact`. Other helpers create one-leaf/multi-leaf trees, return root IDs, manually build packed trees from leaves upward, run store fixtures with optional shared node-store access, and compute `expected_num_nodes_for_num_leaves`, `expected_depth_for_num_leaves`, and feature-gated `expected_depth_for_num_bytes`.

Control flow: high-level tree constructors use public `DataTreeStore` APIs and resize/write data through `DataTree`. `manually_create_tree` constructs leaves first, then repeatedly groups child IDs into inner nodes until one root remains, mirroring the expected left-packed tree shape. Fixture runners create in-memory locking stores and explicitly async-drop tree and node stores after the closure.

State and persistence behavior: fixtures use deterministic `DataFixture` bytes and in-memory backing stores. The shared-store helper creates both a `DataTreeStore` and a separate `DataNodeStore` over an `LLSharedBlockStore`, allowing tests to inspect raw node counts and tree structure beneath the public tree API. Cache clearing is used in slow tests to force reload/recalculation.

Dependencies and integration points: used by `store.rs` tests and `tree/tests.rs`. Depends on `DataNodeStore`, `DataTreeStore`, `DataTree`, `LLSharedBlockStore`, `LockingBlockStore`, and `iter_chunks` under slow-test features.

Risks: expected-value functions assume the same left-packed invariant as production, so a shared mistaken invariant could hide bugs. Manual tree construction is feature-gated for slow tests and has many unwraps. Very small physical block sizes are useful for coverage but may not mirror production performance characteristics.

Test signals: enables verification of data preservation, raw node counts, depth calculations, root IDs, and exact tree shape across different block sizes and tree sizes.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_tree_store/testutils.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_tree_store/traversal.rs -->
## sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_tree_store/traversal.rs

Purpose: contains the core recursive traversal and tree-shaping algorithms used by `DataTree` for reading, writing, growing, shrinking, creating subtrees, lowering degenerate roots, and streaming nodes in a subtree.

Important APIs and types: `LeafHandle` abstracts a mutable leaf as borrowed, owned, or not loaded yet; `TraversalCallbacks` receives existing leaves, creates new leaf data, and observes backtracking from inner nodes; `traverse_and_return_new_root` is the main traversal entry point; `LoadNodeError` reports missing/load failures for subtree streaming; `load_all_nodes_in_subtree_of_id` and `load_all_nodes_in_subtree` stream a root and descendants. Private helpers traverse existing subtrees, create new subtrees, increase depth, and collapse single-child roots.

Control flow: traversal first computes the maximum leaves supported by the current root depth. Read-only traversals error if the requested end index would require growth. Write-enabled traversals visit the existing region, then recursively increase tree depth one level at a time if needed, preserving balanced/left-packed shape longer during growth. Existing inner traversal computes child ranges, optionally grows the last existing leaf to full size before creating later leaves, visits existing children, creates gap children and traversed children, then calls back on backtrack. New subtree creation fills gap leaves with max-size zero leaves and traversed leaves via callbacks. After traversal, single-child roots are replaced by their child and the redundant child copy is removed.

State and persistence behavior: traversal mutates loaded `DataInnerNode`/`DataLeafNode` handles and may create or remove persisted blocks via `DataNodeStore`. Growth can copy the old root into a new child and convert the existing root block into a new inner root, preserving the root block ID. Shrink/collapse paths overwrite root contents and remove redundant subtree nodes. On many errors, traversal returns `(error, root)` so `DataTree` can restore `self.root_node`.

Dependencies and integration points: used by `DataTree` byte-index traversal, resize, removal, and block enumeration. It depends on `DataNodeStore`, `NodeLayout`, `DataInnerNode`, `DataLeafNode`, `DataNode`, `BlockId`, `DivCeil`, async recursion via `Box::pin`, and futures streams.

Risks: this is the highest-complexity area. Many invariants use `assert!`, while comments note disk-corruption-facing conditions should become `ensure!`. Crash consistency is nuanced: growth copies/overwrites roots, shrinking removes child IDs before deleting subtrees, and collapse removes old nodes after root overwrite, but TODOs call out incomplete exception safety. Recursive async traversal may be hard to reason about and has TODOs for simplification and tests. `load_all_nodes_in_subtree` uses `select_all`, so descendant stream order is not necessarily deterministic.

Test signals: direct TODO says tests are missing for traversal internals. Indirect coverage comes from `DataTree` read/write/resize/remove/all-block tests, especially slow feature suites across many tree sizes and block sizes.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_tree_store/traversal.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_tree_store/tree/mod.rs -->
## sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_tree_store/tree/mod.rs

Purpose: defines `DataTree<B>`, a mutable file/blob-like byte tree over `DataNodeStore`. It provides size queries, ranged reads, best-effort reads, full reads, ranged writes with growth, explicit flush, resize, recursive removal, and block enumeration.

Important APIs and types: `DataTree` holds `root_node: Option<DataNode<B>>`, shared `node_store`, and `num_bytes_cache: SizeCache`. Public methods include `new`, `num_bytes`, `num_nodes`, `root_node_id`, `read_bytes`, `try_read_bytes`, `read_all`, `write_bytes`, `flush`, `resize_num_bytes`, `remove`, `remove_subtree` test utility, `all_blocks`, and `into_root_node` test utility. It defines private `TraversalByByteIndicesCallbacks` to adapt byte ranges to leaf-index traversal.

Control flow: reads validate requested range (`read_bytes`) or clamp it (`try_read_bytes`), then `_do_read_bytes` traverses leaves and copies selected leaf slices into the target. Writes wrap callbacks that either overwrite a whole leaf directly through `LeafHandle::overwrite_data` or load and mutate a partial leaf, and create new leaves from source slices. `_traverse_leaves_by_byte_indices` computes first/end leaf indices, wraps byte offsets into traversal callbacks, temporarily takes `root_node`, invokes traversal, restores the returned root on success or error, and updates `SizeCache` if traversal grew the blob. `resize_num_bytes` computes new leaf count and last leaf size, traverses only the new right border, resizes or creates the last leaf, removes now-unneeded right-side children on backtrack, then updates the size cache. Removal recursively deletes the root subtree and async-drops the tree guard.

State and persistence behavior: `root_node` is `Option` so ownership can move through traversal without cloning; methods expect it to be `Some` except during internal operations. Root block ID is intended to remain stable during growth/resizing by converting/overwriting root nodes rather than allocating a different root. Writes and resizes mutate cached node objects; `flush` currently only flushes the root node and has a TODO warning it may not flush the whole tree. Size cache is updated after growth and resize but not after pure in-bounds writes.

Dependencies and integration points: used by `DataTreeStore` as the live tree handle. It integrates with `SizeCache`, traversal callbacks, `DataNodeStore`, `DataNode` types, `RemoveResult`, `for_each_unordered`, `DivCeil`, and futures streams.

Risks: exception safety is explicitly TODO; partial traversal failures can leave some persisted changes while restoring only the in-memory root handle. `read_bytes` computes `read_end` with checked addition, but `_traverse_leaves_by_byte_indices` uses `begin_byte + size_bytes` directly. Flush behavior is incomplete for dirty descendants. Many invariant checks are assertions. `write_bytes` with zero-length source does not grow even if offset is beyond EOF, noted as a behavior question.

Test signals: companion tests cover size and node counts, root ID stability, read/try-read/read-all, write growth and data preservation, resize growth/shrink/to-zero, remove, and all-block enumeration. Many broad cases are behind `slow-tests-*` features rather than default tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_tree_store/tree/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_tree_store/tree/tests.rs -->
## sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_tree_store/tree/tests.rs

Purpose: contains the primary behavioral test matrix for `DataTree`, with default smoke tests and extensive feature-gated slow suites for size accounting, root IDs, reads, writes, resizing, removal, and block enumeration.

Important APIs and types: internal `testutils` defines `ParamNum`, `Parameter`, reusable `tree_parameters`, `LeafIndex`, structure assertions (`assert_is_max_data_tree`, `assert_is_left_max_data_tree`, `assert_tree_structure`), data validation (`assert_leaf_data_is_correct`, `for_each_leaf`), and `flush_caches`. The `run_tokio_test!` macro runs async code from regular `#[test]` functions to work around rstest limitations. `instantiate_read_write_tests!` generates range tests for whole tree, single byte, two bytes, one leaf, and across leaves.

Control flow: tests build parameterized trees either manually through `DataNodeStore` or through `DataTree::resize_num_bytes`, then load them through `DataTreeStore`. Read tests compare generated bytes or expected out-of-range errors. Try-read tests assert clamped reads leave the unread target suffix unchanged. Write tests create base data, write a generated subregion at an offset, compute expected bytes including zero-filled gaps when growing, validate cached and reloaded sizes, read all data back, verify tree structure, and check raw node count. Resize tests compare before/after shapes and data preservation. Remove and all-block tests validate recursive deletion and per-tree block sets.

State and persistence behavior: tests frequently flush/drop/reload caches to distinguish cached size results from persisted recalculation. Structure checks assert roots are non-degenerate, left siblings are full, and right-border subtrees are allowed to be partial. Root ID tests verify the root block ID remains stable across growth and reload.

Dependencies and integration points: exercises `DataTree`, `DataTreeStore`, `DataNodeStore`, shared in-memory stores, deterministic `DataFixture`, `rstest`, `rstest_reuse`, and feature flags `slow-tests-1` through `slow-tests-6`.

Risks: most exhaustive coverage is feature-gated, so normal test runs may miss traversal corner cases. The expected structure helpers mirror production invariants, which is useful for regression detection but can share conceptual blind spots. There are explicit TODOs for verifying read operations do not mutate nodes and for testing flush behavior.

Test signals: strong slow-suite coverage across block sizes 40, 64, and 512 and across one-leaf, two-leaf, nearly full, full, three-level, and four-level-minimum tree shapes. Default tests cover new tree sizing, setup sanity, and root ID stability for one-node and multi-node trees.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_tree_store/tree/tests.rs -->
