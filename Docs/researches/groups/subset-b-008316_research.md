# subset-b-008316 research

Grouped research for the subset-b-008316 source files. Each section is wrapped with the reconciliation markers requested by the research cron.

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/rmdir.rs -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/rmdir.rs

## Purpose
This file defines e2e performance counter scenarios for the filesystem `rmdir` operation. It is not the implementation of directory removal; it is a fixture-driven specification of expected blobstore, high-level blockstore, and low-level blockstore activity for removing directories across root, nested, deeply nested, invalid-target, and large-directory cases.

## Important APIs, Types, and Functions
The file registers the `rmdir` test group with `crate::perf_test_macro::perf_test!`, listing sixteen scenario functions. Each scenario accepts `impl TestDriver` and returns `impl TestReady` through the builder chain `create_filesystem().setup(...).test(...).expect_op_counts(...)`.

The scenario set covers `existing_empty_dir_from_rootdir`, missing directory lookup, non-empty directory failure, empty/non-empty/missing children under nested and deeply nested parents, attempts to remove files or symlinks via `rmdir`, and `rmdir_large_directory`. It uses `PathComponent::try_from_str` for child names, `AbsolutePath::try_from_str` for recursive setup paths, and `NUM_BYTES_FOR_THREE_LEVEL_TREE / BLOCKID_LEN` to size the large directory stress case.

## Control Flow
Every scenario creates a fresh filesystem, performs setup that is later excluded from counted operations by the test driver, then runs one counted `fixture.filesystem.rmdir(parent, name)` call or a loop of calls. Successful paths unwrap the result. Error cases use `unwrap_err()` to assert expected failure while still checking the storage actions needed to detect that failure.

The large-directory test first creates a directory and enough subdirectories to force multi-level directory storage. The counted phase removes every subdirectory, then removes the parent directory after it becomes empty.

## State and Persistence Behavior
The scenarios mutate directory metadata and backing blobs through the filesystem abstraction. Successful removals shrink or rewrite parent directory blobs, remove child directory blobs, and flush dirty blocks. Failure cases usually still load and inspect parent or child metadata; several nested failure cases also count parent directory rewrite/resize behavior, reflecting lookup or atime/cache side effects.

## Dependencies and Integration Points
The tests depend on `FilesystemDriver`, `TestDriver`, `TestReady`, `ActionCounts`, `BlobStoreActionCounts`, `HLActionCounts`, `LLActionCounts`, `FixtureType`, `BLOCKID_LEN`, and CryFS path types. They integrate with the generated test matrix from `perf_test_macro.rs`, which runs them against fuser with inode cache, fuser without inode cache, fuse-mt, and multiple atime modes.

## Risks and Notes
Many expected counts carry TODO comments asking whether they are really expected. Several fixture-specific branches document that fuser without inode cache performs more loads than fuse-mt, likely because node handles store paths and force repeated lookup. These numbers are therefore regression-sensitive but may also encode current implementation artifacts. Large-directory constants are tightly coupled to block tree fanout and `BLOCKID_LEN`.

## Test Signals
The strongest signals are exact equality of counted `ActionCounts` and distinct expected values per `FixtureType`. The suite exercises success, ENOENT-like failure, ENOTEMPTY-like failure, type mismatch errors for file/symlink targets, path depth overhead, and block-tree removal costs.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/rmdir.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/statfs.rs -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/statfs.rs

## Purpose
This file defines performance counter tests for `statfs`, validating that filesystem statistics queries use only storage-level capacity and block-count APIs and do not scale with existing directory or file content.

## Important APIs, Types, and Functions
The group is registered as `perf_test!(statfs, [empty_filesystem, with_content])`. `empty_filesystem` calls `fixture.filesystem.statfs()` on a fresh filesystem. `with_content` creates a directory, a root file, and a nested file before the counted `statfs` call.

Expected counts are expressed with `BlobStoreActionCounts`, `HLActionCounts`, and `LLActionCounts`. Both scenarios expect `store_num_nodes`, `store_estimate_space_for_num_blocks_left`, `store_logical_block_size_bytes`, `store_num_blocks`, `store_estimate_num_free_bytes`, `num_blocks`, and `estimate_num_free_bytes` once.

## Control Flow
Each test uses the standard `create_filesystem().setup(...).test(...).expect_op_counts(...)` chain. Setup is either empty or creates representative content. The counted phase only invokes `statfs` and unwraps success.

## State and Persistence Behavior
`statfs` is read-only from the filesystem caller perspective. It should not load file or directory blobs and should not write, resize, remove, or flush data. The identical expected counts for empty and populated filesystems intentionally verify content independence.

## Dependencies and Integration Points
This file uses `FilesystemDriver` as an imported trait, `TestDriver`/`TestReady`, `ActionCounts`, CryFS path components for setup names, and the blobstore/blockstore counter types. It integrates with all fixture and atime combinations produced by the macro, although expected counts do not vary by fixture type or atime behavior.

## Risks and Notes
The main risk is that future `statfs` implementation changes begin walking content or loading metadata, which would invalidate the constant-count assumption. The populated setup is small; it verifies non-empty state but not very large filesystems.

## Test Signals
The tests signal that `statfs` should use aggregate store queries exactly once each and remain free of blob reads and writes regardless of simple filesystem content.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/statfs.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/symlink.rs -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/symlink.rs

## Purpose
This file defines e2e performance counter scenarios for creating symbolic links. It measures creation in root, nested, and deeply nested directories, duplicate-name failure behavior, and a long target path that spans multiple storage nodes.

## Important APIs, Types, and Functions
The file registers `perf_test!(symlink, [...])` with seven scenarios: new and already-existing symlink creation from root, nested directory, and deeply nested directory, plus `long_target`. Scenarios use `fixture.filesystem.create_symlink(parent, name, &target)` with `PathComponent` link names and `AbsolutePath` targets.

Expected counts vary through `FixtureType` for path-depth cases. Long target setup uses `NUM_BYTES_FOR_THREE_LEVEL_TREE` to construct a repeated path string large enough to drive multi-block symlink content storage.

## Control Flow
For non-existing cases, setup prepares the target path and optionally creates the parent directory. The counted phase creates the symlink and unwraps success. Existing-name cases create the symlink during setup, reset cache/counters through the test driver, then attempt the same create again and require an error. The long-target case has no filesystem setup and creates a single symlink with a very large target string.

## State and Persistence Behavior
Successful symlink creation allocates a new blob/node for the symlink, updates the parent directory entry, writes target data, and flushes changed blocks. Duplicate creation attempts still create intermediate state in some paths and then remove it after discovering the name conflict, as shown by `store_create` paired with `store_remove` or `store_remove_by_id`. Long targets create many high-level blocks and low-level stores.

## Dependencies and Integration Points
The file depends on the filesystem test harness, `FixtureType`, `NUM_BYTES_FOR_THREE_LEVEL_TREE`, CryFS path types, and all three action-count structures. It integrates with `perf_test_macro.rs` for fuser/fuse-mt and atime expansion.

## Risks and Notes
Many count blocks are annotated as TODO. The duplicate-name behavior is especially sensitive: creating then removing storage before reporting an existing name may be an implementation detail rather than an inherent requirement. The path-depth branches encode current inode-cache behavior and may need updates if node handles or lookup caching change.

## Test Signals
The file verifies success and duplicate failure paths, root versus nested lookup overhead, deep path traversal costs, and the block allocation profile for long symlink targets. Counts include `exists`, `store_create`, `store_remove`, writes, flushes, and blob data mutations.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/symlink.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/truncate.rs -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/truncate.rs

## Purpose
This file defines performance counter scenarios for path/node based `truncate`. It measures growing and shrinking empty or non-empty files, truncating files in root/nested/deeply nested locations, and expected failures when the target is a directory or symlink.

## Important APIs, Types, and Functions
The `truncate` group lists eleven scenario functions. The counted operation is `fixture.filesystem.truncate(Some(node), NumBytes::from(size))`. Sizes include one byte, 100/101 bytes, 1024 bytes, and `NUM_BYTES_FOR_THREE_LEVEL_TREE` to force multi-level block-tree allocation or removal.

The scenarios use `create_file`, `mkdir`, `mkdir_recursive`, and `create_symlink` during setup. Counts are fixture-specific for lookup depth and cache behavior, using `FixtureType` matches in expected `ActionCounts`.

## Control Flow
Each scenario creates a fresh filesystem and target node. Grow tests truncate an empty or short file upward. Shrink tests first grow a file to the large tree size in setup, then shrink during the counted phase. Location tests create files under root, one nested directory, or a recursive deep path. Error tests create a directory or symlink and assert `expect_err` from `truncate`.

## State and Persistence Behavior
Growing a file resizes file data and may allocate high-level blocks and low-level blocks. Large grows record `store_create` and low-level `exists`/`store` counts. Shrinking a large file removes block tree nodes, including `store_remove` and `store_remove_by_id` counts. Failed directory or symlink truncation should inspect metadata and return without data-block mutation.

## Dependencies and Integration Points
The file depends on `FilesystemDriver`, the test-driver builder, `ActionCounts`, `FixtureType`, `NumBytes`, path types, and the block-size stress constant. It is generated into a broad fixture/atime matrix by `perf_test_macro.rs`.

## Risks and Notes
Expected counts are implementation-coupled, especially around cached node handles and whether metadata loads include `blob_read_all` or `blob_num_bytes`. Large truncate tests encode current block-tree shape; changes to tree layout, allocation granularity, or sparse-file semantics will require count updates.

## Test Signals
The tests cover small versus large growth, small versus large shrink, root/nested/deep lookup overhead, type validation errors, allocation counts, removal counts, and exact low-level blockstore effects for multi-level file data changes.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/truncate.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/unlink.rs -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/unlink.rs

## Purpose
This file defines performance counter scenarios for `unlink`, focusing on removing files and symlinks, missing-name failure, directory-type failure, nested path overhead, and deletion of large file/symlink payloads.

## Important APIs, Types, and Functions
The `unlink` group includes twelve scenarios. Counted operations call `fixture.filesystem.unlink(parent, PathComponent)`. Setup uses `create_file`, `create_symlink`, `mkdir`, `mkdir_recursive`, `create_and_open_file`, `write`, and `release`. Large cases use `NUM_BYTES_FOR_THREE_LEVEL_TREE` and `NumBytes` to write a file or create a long symlink target large enough to span multiple nodes.

## Control Flow
Success cases create a file or symlink in setup and remove it during the counted phase. Missing and directory cases assert errors. Nested and deeply nested cases return the parent node handle from setup, then unlink by child name. Large file setup writes and releases a large file before the counted unlink; large symlink setup creates a long target, then unlinks it.

## State and Persistence Behavior
Successful unlink updates the parent directory blob, flushes changes, and removes the target's backing storage. Large file and large symlink removal also delete subordinate high-level/low-level blocks, shown by `store_remove_by_id` and low-level `remove` counts. Directory unlink failure may still mutate and flush metadata in current behavior, as reflected by write/resize/flush counts in directory failure scenarios.

## Dependencies and Integration Points
The file depends on the filesystem driver abstraction, test driver, path types, `NumBytes`, `FixtureType`, large-tree constants, and blobstore/blockstore action counters. It shares stress constants and behavior expectations with write, truncate, and symlink tests.

## Risks and Notes
Directory failure cases counting writes and flushes are notable risk areas because type-check ordering or atime updates could change them. Large file and long symlink deletion rely on similar block-removal counts, so block-tree layout changes could alter both. Several count blocks are marked TODO.

## Test Signals
The file validates successful file and symlink unlink, ENOENT-like failure, EISDIR-like failure, path-depth overhead for fuser/fuse-mt, and cleanup of multi-block data. Exact count equality acts as a regression signal for storage lifecycle behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/unlink.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/utimens.rs -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/utimens.rs

## Purpose
This file defines performance counter scenarios for updating timestamps with `utimens` on files, directories, and symlinks in root and nested locations.

## Important APIs, Types, and Functions
The `utimens` group includes `file_in_rootdir`, `dir_in_rootdir`, `symlink_in_rootdir`, `file_in_nesteddir`, and `file_in_deeplynesteddir`. Each counted operation calls `fixture.filesystem.utimens(Some(node), Some(atime), Some(mtime))` with fixed `SystemTime` values derived from `UNIX_EPOCH` plus `Duration`.

Setup creates targets through `create_file`, `mkdir`, `create_symlink`, and `mkdir_recursive`. Counts vary by `FixtureType`, especially for nested and deeply nested paths.

## Control Flow
Each scenario creates one target node in setup, then the counted phase constructs deterministic atime and mtime values and calls `utimens`. The test unwraps success and asserts exact storage operation counts.

## State and Persistence Behavior
`utimens` mutates metadata stored in the target node. File cases generally avoid full blob reads with inode cache, while directory and symlink cases read all blob data because their metadata/content access pattern differs. The operation writes and resizes the blob metadata area and stores a low-level block. Nested file cases show additional loads and reads for path reconstruction when no inode cache is available.

## Dependencies and Integration Points
The file depends on `std::time`, CryFS path types, the filesystem driver abstraction, test-driver builder, `FixtureType`, and the action-count structures. It integrates with macro-generated atime behavior variants, although the operation itself supplies explicit atime/mtime values and does not branch on the atime mode.

## Risks and Notes
Counts encode timestamp metadata serialization details and lookup-cache behavior. If timestamp storage moves, metadata blob layout changes, or symlink timestamp semantics change, the expected read/write profile will need revision.

## Test Signals
The tests signal that timestamp updates are one-node metadata mutations, while still distinguishing file, directory, and symlink storage access patterns and root/nested/deep lookup overhead.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/utimens.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/write.rs -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/write.rs

## Purpose
This file defines a large performance counter matrix for file writes. It measures small and large writes to empty, small, and large files; writes in the middle versus beyond end; nested path overhead; repeated writes to the same open handle; and the effect of closing/releasing the file after the write.

## Important APIs, Types, and Functions
The `write` group registers generic scenario instantiations for `<false>` and `<true>` `CLOSE_AFTER` variants. Scenarios call `fixture.filesystem.write(file.clone(), &mut fh, NumBytes::from(offset), data)` and then `maybe_close::<CLOSE_AFTER, _>(fixture, file, fh).await`.

Setup uses `create_and_open_file`, initial `write` calls, `mkdir`, and `mkdir_recursive`. Important constants are `BLOCKSIZE_BYTES` for small multi-block files and `NUM_BYTES_FOR_THREE_LEVEL_TREE` for large block-tree coverage.

## Control Flow
Each scenario opens a file during setup and returns `(node, file_handle)` to the counted phase. The counted phase writes a vector of bytes at a chosen offset, optionally releases the handle, and asserts counts. Large write scenarios allocate or overwrite block-tree regions. `multiple_writes_to_same_file` performs ten one-byte writes around the large-tree offset before optional close.

## State and Persistence Behavior
Writes mutate in-memory/open-handle state and persistent file data. Without `CLOSE_AFTER`, many scenarios avoid flush and resize counts at the blobstore layer, indicating dirty state remains associated with the open file. With close, counts add release-time loads, writes, resizes, blob flushes, and high-level `store_flush_block`. Writes beyond EOF allocate holes/new blocks and record `store_create`; overwrites record `store_overwrite`; repeated writes show high-level repeated loads/data access but only one low-level store unless closed.

## Dependencies and Integration Points
The file depends on `maybe_close` from `utils.rs`, `FilesystemDriver`, `ActionCounts`, `FixtureType`, `NumBytes`, path types, and all storage counter structures. It is closely related to release/fsync/ftruncate performance tests and relies on the test driver to reset setup counts before measuring the write under test.

## Risks and Notes
The expected counts are highly sensitive to cache, writeback, sparse-file, and release semantics. `CLOSE_AFTER` arithmetic is manually encoded in each expected count block and can hide mistakes if release behavior changes. Many TODO comments remain around expected counts, and fuser-without-inode-cache often doubles loads relative to other fixtures.

## Test Signals
The suite covers allocation, overwrite, sparse extension, open-handle writeback, close-triggered flush behavior, nested lookup overhead, and repeated-write cache behavior. Exact counts across false/true close variants are the primary regression signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/write.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/perf_test_macro.rs -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/perf_test_macro.rs

## Purpose
This file provides the macro layer that expands compact performance scenario lists into either counter tests (`cargo test`) or Criterion benchmarks (`feature = "benchmark"`). It centralizes fixture selection, atime behavior variation, and group/benchmark naming.

## Important APIs, Types, and Functions
There are two cfg-gated `#[crabtime::function] fn perf_test_` definitions. In non-benchmark builds, `perf_test_` emits Rust modules and `#[test]` functions for every scenario, filesystem fixture, and atime behavior. In benchmark builds, it emits Criterion benchmark functions and a criterion group.

Public macro exports are `perf_test!`, `perf_test_only_fuser!`, and `perf_test_only_fusemt!`, which call `perf_test_!` with disable flags. `FixtureType` enumerates `FuserWithInodeCache`, `FuserWithoutInodeCache`, and `Fusemt`.

## Control Flow
At compile-time, crabtime receives the group name and list of scenario names. The non-benchmark branch builds a fixture list, iterates each test name, emits a `mod test_<normalized_name>`, and inside it emits one Rust `#[test]` per fixture and atime behavior. Each generated test constructs `TestDriverImpl` with `InMemoryBlockStore`, calls the scenario function, and runs `assert_op_counts`.

The benchmark branch emits one Criterion function per scenario, iterates atime behaviors inside each benchmark group, and conditionally benchmarks fuser or fuse-mt mounting drivers with `TempDirBlockStore`.

## State and Persistence Behavior
The file itself has no runtime persistence, but generated tests determine the blockstore type and fixture lifecycle. Counter tests use in-memory blockstores for deterministic action counts. Benchmarks use temporary directory blockstores and mounting drivers, so they exercise a more realistic persistence layer.

## Dependencies and Integration Points
This file depends on `crabtime`, `criterion`, `cryfs_blockstore`, `cryfs_rustfs::AtimeUpdateBehavior`, filesystem drivers, and `TestDriverImpl`. All operation files in `e2e-perf-tests/src/operations` integrate through these macros.

## Risks and Notes
Because this is compile-time code generation, syntax emitted as strings must remain valid Rust. `normalize_identifier` is duplicated between cfg branches. Fixture and atime matrices are hard-coded; adding a driver or atime behavior requires changing this file. Benchmark mode uses a reduced sample size of 10 with a TODO to revisit.

## Test Signals
The generated tests are the harness for all per-operation count assertions. The file's own signal is indirect: if macro expansion breaks, operation modules fail to compile or generated test names/groups disappear.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/perf_test_macro.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/test_driver.rs -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/test_driver.rs

## Purpose
This file implements the builder-style test harness used by e2e performance tests. It lets operation files describe setup, counted operation, optional cache/counter reset behavior, expected counts, and benchmark execution without duplicating runtime plumbing.

## Important APIs, Types, and Functions
The central traits are `TestDriver` and `TestReady`. `TestDriverImpl` stores a blockstore factory, filesystem driver marker, atime update behavior, and in counter-test builds the `FixtureType`. Builder structs model each stage: `TestDriverWithFs`, `TestDriverWithFsAndSetupOp`, and `TestDriverWithFsAndSetupOpAndTestOp`.

Important methods include `create_filesystem`, `create_uninitialized_filesystem`, `setup`, `setup_noflush`, chained `setup_noflush`, `test`, `test_no_counter_reset`, `test_noflush`, `test_noflush_no_counter_reset`, and `expect_op_counts`.

## Control Flow
`TestDriverImpl::new` captures fixture configuration. `create_filesystem` and `create_uninitialized_filesystem` wrap async fixture constructors. `setup` composes setup work with `reset_cache_after_setup`, while `setup_noflush` leaves caches warm. `test` resets counters before the counted operation and resets cache after it; variants selectively avoid counter reset or cache flush.

`expect_op_counts` resolves expected counts for the active fixture and atime behavior and returns `TestReadyImpl`. In counter-test mode, `assert_op_counts` creates a Tokio runtime, constructs the fixture, runs setup and test, gathers totals, and uses `pretty_assertions::assert_eq`. In benchmark mode, `run_benchmark` uses Criterion `iter_batched_ref` with async execution.

## State and Persistence Behavior
The harness owns fixture lifecycle for each test iteration. It controls when caches are flushed and when action counters are reset, which defines what operation files actually measure. It also controls blockstore creation through the supplied factory, enabling in-memory deterministic counts or tempdir benchmark persistence.

## Dependencies and Integration Points
The file integrates with `FilesystemFixture`, `FilesystemDriver`, `ActionCounts`, `FixtureType`, `LLBlockStore`, `OptimizedBlockStoreWriter`, `AtimeUpdateBehavior`, `AsyncDrop`, `AsyncDropGuard`, Tokio, Criterion, and pretty assertions. Every operation file consumes this API.

## Risks and Notes
The generic async builder API is powerful but subtle: a wrong choice between `test`, `test_noflush`, and `test_no_counter_reset` changes measured counts. Benchmark mode uses `RefCell<Option<...>>` to adapt an effectively FnOnce async test to Criterion's FnMut interface and will panic if reused unexpectedly. Runtime creation per assertion is simple but may hide runtime-level variability.

## Test Signals
This file supplies the canonical equality assertion for `ActionCounts`. It is also the source of cache reset semantics, making it the first place to inspect when count expectations shift globally across operation files.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/test_driver.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/utils.rs -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/utils.rs

## Purpose
This small utility file provides a reusable conditional close helper for performance tests that need both open-handle and release-after-operation variants.

## Important APIs, Types, and Functions
The only API is `pub async fn maybe_close<const CLOSE_AFTER: bool, FS: FilesystemDriver>(...)`. It accepts a mutable `FilesystemFixture`, a filesystem node handle, and a file handle. If the const generic is true, it calls `fixture.filesystem.release(node, file_handle).await.unwrap()`.

## Control Flow
The function branches once on the const generic `CLOSE_AFTER`. The false branch does nothing. The true branch awaits release and panics on error via `unwrap`, matching the style of the performance scenario tests.

## State and Persistence Behavior
When enabled, this helper triggers file-handle release side effects such as flushing dirty file data and metadata through the filesystem driver. When disabled, dirty/open state remains part of the fixture until later fixture teardown and is not included as release-time cost in the counted operation.

## Dependencies and Integration Points
The helper depends on `FilesystemFixture`, `FilesystemDriver`, `LLBlockStore`, `OptimizedBlockStoreWriter`, and `AsyncDrop` trait bounds. It is used by write-like tests to generate `<false>` and `<true>` variants without duplicating release code.

## Risks and Notes
Because release errors are unwrapped, this helper is appropriate for tests that expect release success only. Its generic fixture argument is intentionally broad, which keeps it reusable but makes compile errors verbose if trait bounds drift.

## Test Signals
The helper has no direct tests in this file. Its signal appears in operation tests where `CLOSE_AFTER` changes expected flush, resize, store, and load counts.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/utils.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/Cargo.toml -->
# sources/security-integrity/cryfs/crates/fsblobstore/Cargo.toml

## Purpose
This manifest defines the `cryfs-fsblobstore` crate, the filesystem-backed blobstore layer used by CryFS. It declares shared workspace metadata, local CryFS crate dependencies, external dependencies, and an optional test utility feature.

## Important APIs, Types, and Functions
As a Cargo manifest, it exports no Rust APIs directly. Important package fields inherit `authors`, `edition`, `homepage`, `license`, `readme`, `repository`, `rust-version`, and `version` from the workspace. The crate name is `cryfs-fsblobstore`.

Dependencies include `anyhow`, `async-trait`, `binary-layout`, `binrw`, `byte-unit`, `derive_more`, `futures`, `lockable`, `log`, and local crates `cryfs-blockstore`, `cryfs-blobstore`, `cryfs-concurrent-store`, `cryfs-utils`, and `cryfs-version`.

## Control Flow
Cargo uses this file to resolve and compile the crate. The dependency graph wires fsblobstore to lower block/blob abstractions, concurrent store primitives, utility async-drop support, and versioning/layout crates.

## State and Persistence Behavior
The manifest does not perform persistence itself, but its dependencies indicate that the crate owns persistent blob layout and concurrent access over blockstore/blobstore backends. The `testutils` feature enables `cryfs-blobstore/testutils` for tests without making it part of default builds.

## Dependencies and Integration Points
This crate sits between higher filesystem code and lower block/blob storage crates. Local path dependencies tie it to the CryFS workspace, while `lockable`, `futures`, and `async-trait` support asynchronous/concurrent blob operations.

## Risks and Notes
Dependency version drift is controlled by workspace dependencies. Feature exposure is minimal: `default = []`, so tests needing utilities must opt into `testutils`. Any public API assumptions are in source files, not this manifest.

## Test Signals
The manifest's main test signal is build resolution. Enabling `testutils` should propagate blobstore test helpers; default builds should remain free of that feature.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/src/concurrentfsblobstore/blob.rs -->
# sources/security-integrity/cryfs/crates/fsblobstore/src/concurrentfsblobstore/blob.rs

## Purpose
This file defines `ConcurrentFsBlob`, a concurrency-safe wrapper around a loaded filesystem blob guard. It exposes blob identity, blob type lookup, locked mutable access to the underlying `FsBlob`, explicit removal, and async-drop cleanup.

## Important APIs, Types, and Functions
`ConcurrentFsBlob<B>` is generic over a backend `B` implementing `BlobStore + AsyncDrop<Error = anyhow::Error> + Debug + Send + 'static`, with a concrete blob that is `Send + AsyncDrop`. Its single field is `blob: AsyncDropGuard<LoadedBlobGuard<B>>`.

Important methods are `new`, `blob_id`, `blob_type`, `with_lock`, and associated async `remove`. It implements `AsyncDrop` by delegating to the wrapped loaded blob guard.

## Control Flow
`new` wraps a `LoadedBlobGuard` in `ConcurrentFsBlob` and returns it inside `AsyncDropGuard`. `blob_id` delegates directly. `blob_type` acquires the internal lock and asks the underlying `FsBlob` for its type. `with_lock` is a generic async critical-section helper that passes mutable `FsBlob<B>` access to the caller. `remove` consumes an `AsyncDropGuard<Self>`, extracts the inner wrapper without running its drop, and delegates removal to `LoadedBlobGuard::remove`.

## State and Persistence Behavior
The wrapper coordinates access to a loaded blob and ensures async cleanup is performed when dropped. Mutating operations must go through `with_lock`, preserving serialized access to the underlying `FsBlob`. `remove` is a destructive persistence operation returning `RemoveResult` or shared `Arc<anyhow::Error>`, and it intentionally consumes the guard to avoid later double-drop/double-remove behavior.

## Dependencies and Integration Points
The file depends on `cryfs_blobstore::{BlobId, BlobStore, RemoveResult}`, `cryfs_utils::async_drop::{AsyncDrop, AsyncDropGuard}`, `LoadedBlobGuard`, and `BlobType`. It is part of `concurrentfsblobstore` and bridges public concurrent blob handles to the lower fsblobstore implementation.

## Risks and Notes
The most important risk is `unsafe_into_inner_dont_drop` in `remove`: correctness depends on `LoadedBlobGuard::remove` taking over all cleanup that async drop would otherwise perform. `blob_type` locks instead of caching by design because it is rare; this avoids stale cached metadata but adds lock overhead. Error sharing via `Arc<anyhow::Error>` suggests removal failures may need to be propagated to multiple owners.

## Test Signals
Relevant tests should verify drop delegation, lock serialization, blob ID/type access, successful remove, remove failure propagation, and absence of double cleanup after `remove` consumes the guard.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/src/concurrentfsblobstore/blob.rs -->
