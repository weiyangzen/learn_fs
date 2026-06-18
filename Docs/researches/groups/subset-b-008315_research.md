# subset-b-008315 research

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/mkdir.rs -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/mkdir.rs

## Purpose
This file defines end-to-end performance counter tests and benchmark cases for CryFS `mkdir` behavior. It exercises successful and failing directory creation from the root directory, from a one-level nested directory, and from a deeply nested directory. The main signal is not functional output alone, but the expected action counts across the tracked blobstore, high-level blockstore, and low-level blockstore layers.

## Important APIs, types, and functions
- Uses `crate::perf_test_macro::perf_test!` to register six test cases: `notexisting_from_rootdir`, `existing_from_rootdir`, `notexisting_from_nesteddir`, `existing_from_nesteddir`, `notexisting_from_deeplynesteddir`, and `existing_from_deeplynesteddir`.
- Each case accepts `impl TestDriver` and returns `impl TestReady`, building a test via `create_filesystem().setup(...).test(...).expect_op_counts(...)`.
- Calls `FilesystemDriver::mkdir`, `FilesystemDriver::mkdir_recursive`, and path constructors `PathComponent::try_from_str` and `AbsolutePath::try_from_str`.
- Expected counts are expressed with `ActionCounts`, `BlobStoreActionCounts`, `HLActionCounts`, `LLActionCounts`, and fixture-specific branches on `FixtureType`.

## Control flow
Every test creates a fresh CryFS filesystem, performs setup, resets setup counters and cache through the shared harness, executes exactly one `mkdir` attempt, then asserts the accumulated counters. Root tests call `mkdir(None, ...)`. Nested tests create or recursively create the parent first and pass the returned node handle as `Some(parent)`. Existing-name tests deliberately call `unwrap_err()` after pre-creating the target name, while non-existing-name tests call `unwrap()`.

## State and persistence behavior
Successful creates allocate a new directory blob and update the parent directory blob. Nested creates also update timestamp metadata in ancestor directories, which is why nested successful cases expect more writes and stores than root creates. Existing-name tests still create a candidate directory blob first, then remove it after the parent insertion fails, so they expect `store_create` plus `store_remove_by_id`/`store_remove`. Setup-created state is persisted into the test filesystem but counters are reset before the measured operation.

## Dependencies and integration points
The file integrates with the generic performance harness in `test_driver.rs`, the fixture stack in `filesystem_fixture.rs`, and both FUSE-facing drivers selected by `perf_test!`. It relies on the fixture's tracking stores to observe logical blob operations and physical block operations. It also depends on the filesystem driver's node-handle semantics: fuser without inode cache repeatedly resolves paths, while fuser with inode cache can reuse setup handles more cheaply.

## Risks and observations
Several expected-count branches are annotated as uncertain. Deep and nested fuser-without-cache paths expect substantially more loads/read-all/read calls than fuse-mt, with comments attributing this to path-only `CryNode` structures that must repeat lookup work. Existing nested cases expect a low-level `store` even when the logical operation fails, which is called out as suspicious. These tests tightly encode current implementation costs, so legitimate cache, timestamp, or rollback changes will require careful count updates.

## Test signals
`cargo test` without the `benchmark` feature expands these cases across fixture types and atime policies, asserting exact counts with `pretty_assertions`. `cargo bench --features benchmark mkdir` expands them as criterion benchmarks. The strongest coverage signals are: successful root create costs one new blob and one parent update; duplicate create rolls back a speculative blob; path depth and fixture type scale read/load counts; and setup counters do not pollute measured operation counts.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/mkdir.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/mod.rs -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/mod.rs

## Purpose
This module file is the registry for all operation-level e2e performance suites in the CryFS performance-test crate. It exposes each operation module so the crate can compile and macro-expand tests and benchmarks for filesystem operations such as `mkdir`, `open`, `read`, `readdir`, `readlink`, `release`, and `rename`.

## Important APIs, types, and functions
- Publicly declares operation modules with `pub mod ...` for chmod/chown/create/open/read/release/write and related filesystem calls.
- It does not define runtime functions or types; its API surface is the module export list.
- Contains cross-suite TODO notes describing desired future improvements to counter attribution, atime expectations, operation-count review, correctness checking, benchmark block sizes, and benchmark deadlock investigation.

## Control flow
There is no executable control flow in this file. Rust module loading makes the listed operation files part of the crate. Each child module owns its own `perf_test!` registration, so adding or removing an entry here directly controls whether that operation suite participates in compilation.

## State and persistence behavior
The file has no mutable state or persistence. Its indirect state impact is structural: exported modules instantiate tests and benchmarks that create isolated CryFS fixtures and tracking stores.

## Dependencies and integration points
This module is consumed by the crate root and by Rust's module system. It aligns operation modules with the `perf_test_macro` harness. The TODOs reference shared harness behavior, especially the fact that many operation measurements include an automatic flush/reset after the operation and currently do not split operation cost from flush cost.

## Risks and observations
The TODOs identify systemic risks across the suite. Atime behavior unexpectedly does not change many counts, even for operations that should update timestamps. Some benchmark runs may deadlock at startup. The file also suggests the suite is currently more performance-counter oriented than correctness oriented and would benefit from an `expect_output()` style harness.

## Test signals
Because this is a registry, its test signal is compile-time inclusion. A missing `pub mod` silently removes that operation suite from the crate. The comments provide important research context for interpreting all operation reports: exact counts may include forced cache flushing, may not fully distinguish atime paths, and may reflect known benchmark deadlock issues.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/open.rs -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/open.rs

## Purpose
This file defines e2e performance counter tests and benchmarks for opening existing files. It measures the cost of `open` in the root directory, a nested directory, and a deeply nested directory, with each case parameterized by whether the file handle is immediately released after opening.

## Important APIs, types, and functions
- Registers six macro-expanded cases through `perf_test!`: `in_rootdir::<false/true>`, `in_nesteddir::<false/true>`, and `in_deeplynesteddir::<false/true>`.
- The const generic `CLOSE_AFTER` controls whether `maybe_close` calls `FilesystemDriver::release` after `FilesystemDriver::open`.
- Setup uses `create_file`, `mkdir`, and `mkdir_recursive` to create the target file and returns the file node handle.
- Expected counts branch on `FixtureType` and use a local `close_after` integer multiplier.

## Control flow
Each test creates a filesystem, creates an existing file at the target depth, resets setup effects, opens the file by node handle, and optionally releases it. The root case uses a file under `None`; nested cases create one or more parent directories and then create the file under the returned parent handle.

## State and persistence behavior
`open` itself should not create or modify file data. When the inode is already cached under `FuserWithInodeCache`, opening without release is expected to require no blobstore or blockstore operations. Fuse-mt and fuser without inode cache load path/file metadata. When `CLOSE_AFTER` is true, release adds flush activity (`blob_flush`, `store_flush_block`, and additional loads/reads), even though no file data was changed.

## Dependencies and integration points
The file depends on `FilesystemDriver` for `open`, setup helpers, and `release` via `maybe_close`. It uses `TestDriver`/`TestReady` for harness composition, `FixtureType` for expected-count selection, and `cryfs_utils::path` for valid path components. It is sensitive to driver implementation details: fuser without inode cache performs more lookup work because its node handles do not retain the resolved node as aggressively.

## Risks and observations
Most comments question whether the counts are expected. The largest risk is that the suite encodes current cache behavior rather than a stable interface contract. Changes to node-handle caching, file-handle release semantics, or flush behavior will break counts even if user-visible open behavior remains correct. The optional release path also means the same test name family measures a mixed cost of open plus close.

## Test signals
The suite verifies that cached fuser opens can be metadata-free, that path depth increases lookup cost for fuse-mt and fuser without cache, and that release consistently adds flush/load overhead. Benchmarks generated under the `benchmark` feature provide timing signals for the same cases.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/open.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/read.rs -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/read.rs

## Purpose
This file defines a broad suite of e2e performance counter tests and benchmarks for file reads. It covers empty files, small files, large multi-block/tree files, reads from the middle, reads past EOF, nested and deeply nested file paths, repeated reads from one file handle, and optional release after read.

## Important APIs, types, and functions
- Registers twenty-two cases via `perf_test!`, each instantiated with `CLOSE_AFTER` false and true.
- Uses `FilesystemDriver::create_and_open_file`, `write`, `read`, and optional `release` through `maybe_close`.
- Uses `BLOCKSIZE_BYTES` and `NUM_BYTES_FOR_THREE_LEVEL_TREE` to construct files that exercise single-block and multi-level blob trees.
- Uses `NumBytes` for offsets and lengths and `AtimeUpdateBehavior` to compute expected timestamp-write costs.
- Expected counts use exact `ActionCounts` values with fixture-specific branches and `close_after`/`expect_atime_update` multipliers.

## Control flow
Each test creates a new filesystem, creates and opens a file during setup, optionally writes initial data, then reads a specific range. EOF tests assert an empty result for at least the small-file beyond-EOF case. Large-file cases create data spanning multiple internal tree levels and read either one byte or a tree-sized region. `multiple_reads_from_same_file` performs ten one-byte reads from adjacent positions. If `CLOSE_AFTER` is true, the file handle is released after reading.

## State and persistence behavior
Read operations generally load file metadata/data but do not modify content. Atime updates are modeled as deferred work that only appears in many cases when the handle is released: expected writes, resizes, stores, and flushes are multiplied by `close_after`. Empty-file reads use a different atime formula than non-empty reads: the file itself notes a TODO asking why its atime calculations differ from other operations. Setup writes are flushed/reset before the measured read unless the shared harness keeps deliberate file handles open.

## Dependencies and integration points
The suite depends heavily on the shared fixture's artificial block sizing. `BLOCKSIZE_BYTES` and `NUM_BYTES_FOR_THREE_LEVEL_TREE` make tree-depth costs deterministic, which lets the expected `HLActionCounts::store_load` and `LLActionCounts::load` values distinguish single-block, multi-block, and beyond-EOF traversals. It integrates with both fuser variants and fuse-mt through `FixtureType`, and with all atime policies expanded by the performance macro.

## Risks and observations
The file contains a top-level TODO warning that atime formulas differ from `readlink` and even among read cases. Many branches attribute fuser-without-cache overhead to repeated path lookup. Since reads optionally include release, some expected counts combine read traversal with close-time flush and atime persistence. The exact high-level counts for large and repeated reads are brittle because they encode the current tree implementation and cache reuse pattern.

## Test signals
The suite validates several important performance contracts: reading an empty file performs minimal data traversal; reading beyond EOF returns no data and avoids full-range traversal; large middle reads load many high-level blocks; repeated small reads reuse some low-level state but still count repeated blob reads; path depth mainly penalizes fuser without inode cache; and atime writes are expected only under the configured policies and mostly when the file is closed.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/read.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/readdir.rs -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/readdir.rs

## Purpose
This file defines performance counter tests and benchmarks for directory listing. It covers an empty root, a populated root, populated nested and deeply nested directories, and a large directory with enough entries to force multi-block directory storage.

## Important APIs, types, and functions
- Registers `empty_rootdir`, `rootdir_with_entries`, `nesteddir`, `deeplynesteddir`, and `large_directory`.
- Uses `FilesystemDriver::readdir` as the measured operation.
- Setup uses `mkdir`, `mkdir_recursive`, `create_file`, and `create_symlink` to populate directories.
- Uses `NUM_BYTES_FOR_THREE_LEVEL_TREE / BLOCKID_LEN` to choose a large directory entry count.
- Computes directory atime updates from `AtimeUpdateBehavior`, where `Noatime`, `NodiratimeRelatime`, and `NodiratimeStrictatime` skip directory atime writes.

## Control flow
Root cases call `readdir(None)`. Nested cases create a parent directory, populate it with a directory, file, and symlink, then call `readdir(Some(handle))`. The large-directory case creates `large_dir`, inserts many files under it, and reads that directory. Expected counts are fixture-specific and add atime write/resize/store costs where directory atime should change.

## State and persistence behavior
Readdir is primarily a read of the directory blob plus loads of child metadata needed to produce entries. For non-root directory reads, some atime policies update the directory blob, adding blob writes/resizes and low-level stores. The large-directory case persists enough entries during setup to require a multi-level backing structure, making the measured read show high `HLActionCounts::store_load` and `LLActionCounts::load` values.

## Dependencies and integration points
The file integrates with the same `TestDriver` harness and all fixture types. It uses `AtimeUpdateBehavior` directly rather than treating atime as uniform. The expected counts also depend on the directory encoding and on whether the filesystem driver caches inode/node resolution.

## Risks and observations
Many expected counts are marked for review. The operation registry notes a broader suspicion that atime behavior does not affect all operations as expected; this file is one of the suites where atime does affect counts for nested directory reads. Large-directory counts are especially brittle because they depend on test constants, block-id length, and directory tree layout.

## Test signals
The suite checks that empty root listing costs one root load/read; populated root listing loads child metadata; nested/deeply nested reads scale with lookup depth and fixture type; directory atime policies add exactly one timestamp write path; and a large directory triggers substantially more high-level and low-level loads.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/readdir.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/readlink.rs -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/readlink.rs

## Purpose
This file defines e2e performance counter tests and benchmarks for reading symlink targets. It measures symlinks in the root directory, a nested directory, a deeply nested directory, and a symlink with a long target string that spans multiple backing nodes.

## Important APIs, types, and functions
- Registers `from_rootdir`, `from_nesteddir`, `from_deeplynesteddir`, and `long_target`.
- Setup uses `FilesystemDriver::create_symlink`, plus `mkdir` or `mkdir_recursive` for parent directories.
- The measured operation is `FilesystemDriver::readlink`.
- Uses `AtimeUpdateBehavior` to decide whether symlink atime should be persisted: `Strictatime` and `NodiratimeStrictatime` update, while `Noatime`, `Relatime`, and `NodiratimeRelatime` do not.
- The long-target case constructs a target by repeating `"/very/long"` based on `NUM_BYTES_FOR_THREE_LEVEL_TREE`.

## Control flow
Each case creates a symlink and returns its node handle from setup. The test body calls `readlink(symlink).await.unwrap()`. Expected counts branch on fixture type, path depth, target length, and atime policy. The long-target case remains rooted at `/` but expects many high-level and low-level loads because the symlink payload spans a larger blob tree.

## State and persistence behavior
Readlink returns symlink target data without changing the link content. Under strict atime modes it writes timestamp metadata, adding a single blob write/resize and low-level store. The long-target setup persists a large symlink target so the measured read has larger tree traversal cost but the same atime update shape.

## Dependencies and integration points
The file depends on the filesystem driver's symlink representation, CryFS path parsing, atime configuration, and fixture-specific caching behavior. It shares the same tracking-store counters as the rest of the operation suite. The expected counts reveal that fuser without inode cache performs extra loads proportional to path depth.

## Risks and observations
The count formulas are annotated with TODOs asking whether they are expected, and the operation registry questions whether atime behavior is consistently represented across operations. The distinction between `Relatime` and `Strictatime` here differs from some read-file cases, so future atime fixes may require coordinated changes.

## Test signals
The suite verifies path-depth scaling for symlink lookup, strict-atime write behavior for symlink reads, and multi-block payload traversal for long symlink targets. It also provides benchmark coverage for readlink latency across fixture drivers and atime policies.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/readlink.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/release.rs -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/release.rs

## Purpose
This file defines e2e performance counter tests and benchmarks for releasing open file handles. It covers unchanged files and files with pending writes, across empty, small, large, nested, deeply nested, overwrite, append/beyond-EOF, and sparse-extension scenarios.

## Important APIs, types, and functions
- Registers fifteen release cases through `perf_test!`.
- Uses `FilesystemDriver::create_and_open_file`, `write`, and `release`.
- Uses `test_noflush` for the measured release so the harness does not add an extra post-test cache reset after release.
- Uses `setup_noflush` for pending-write cases so writes remain dirty and are flushed by the measured release.
- Uses `BLOCKSIZE_BYTES`, `NUM_BYTES_FOR_THREE_LEVEL_TREE`, and `NumBytes` to choose offsets and sizes that exercise direct blocks and larger tree structures.

## Control flow
Unchanged cases create/open a file, sometimes write and flush setup data, then measure only `release(file, fh)`. Dirty cases create/open a file, optionally write initial data in normal setup, then perform a second write in `setup_noflush` so the measured release flushes it. Cases vary whether the write is to an empty file, middle of existing data, beyond EOF, large range, nested path, or deeply nested path.

## State and persistence behavior
Release is the persistence boundary for open file handles. Unchanged releases still flush the open file and may load metadata, but generally do not store new low-level blocks. Dirty releases write blob data, resize metadata, and flush dirty blocks. Writes beyond EOF often expect two low-level stores, reflecting data plus metadata/sparse extension behavior. Nested and deeply nested dirty releases show extra lookup/read-all costs for fuser without inode cache, while fuser with cache and fuse-mt generally keep release costs flat once the file handle is available.

## Dependencies and integration points
The suite is coupled to the file-cache and flush semantics implemented by `FilesystemDriver::release`, to the fixture's `test_noflush` behavior, and to the block/blob tree layout controlled by fixture constants. It integrates with the tracking blobstore/high-level/low-level blockstores to observe flushes and stores, and with fixture types to distinguish cached node handles from repeated path resolution.

## Risks and observations
The file starts with TODOs noting suspicious behavior: some releases load low-level blocks below the cache, simple flushes have many high-level operations, and some release-after-write cases lack expected low-level stores. Individual cases also ask why noatime can still produce two stores. These are high-value regression tests but also brittle: changing writeback, sparse-file, or release flushing logic will invalidate many exact counts.

## Test signals
The suite checks that unchanged release has a minimal flush profile, that large unchanged files load more high-level blocks than small unchanged files, that dirty release persists pending writes, that middle writes are cheaper than beyond-EOF extension in low-level stores, and that fuser without inode cache pays additional path-resolution costs in nested cases. Benchmarks expose release latency for clean and dirty handles.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/release.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/rename.rs -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/rename.rs

## Purpose
This file defines e2e performance counter tests and benchmarks for renaming files, directories, and symlinks. It covers renames within one directory, across root/nested/deeply nested directories, replacing an existing target, and moving between shallow and deep directory trees.

## Important APIs, types, and functions
- Registers the main suite with `perf_test!` for `within_rootdir`, `between_nested_dirs`, `within_nested_dir`, `between_deeply_nested_dirs`, `to_existing_target`, `directory`, `symlink`, `from_nested_to_deeply_nested`, and `from_deeply_nested_to_nested`.
- Registers `from_rootdir_to_nesteddir` and `from_nesteddir_to_rootdir` separately with `perf_test_only_fusemt!` because running them across all fixtures currently deadlocks.
- Uses `FilesystemDriver::rename` as the measured operation, with setup through `create_file`, `mkdir`, `mkdir_recursive`, and `create_symlink`.
- Expected counts branch on `FixtureType` and use `ActionCounts` for blobstore/high-level/low-level effects.

## Control flow
Each test prepares source and destination directory state, then calls `rename(old_parent, old_name, new_parent, new_name)`. Same-directory cases rename within `None` or within one nested handle. Cross-directory cases pass distinct source and destination handles. Existing-target setup creates both source and target names before renaming source onto target. Directory and symlink cases verify metadata-object renames, not just regular files.

## State and persistence behavior
Rename mutates directory entries and sometimes removes/replaces target blobs. Same-directory renames generally load one directory blob and write/resize it once. Cross-directory moves update both source and destination directories and may update parent timestamps or backing blocks, producing multiple writes/stores. Replacing an existing target expects `store_remove_by_id`, high-level removals, and low-level removes. Directory and symlink renames look similar to simple file renames because the directory entry changes while object payloads remain intact.

## Dependencies and integration points
The suite depends on directory entry encoding, parent-handle lookup behavior, replacement semantics, and fixture-driver cache behavior. It integrates with `perf_test_macro` but has special macro handling for two cases due to a known deadlock with all fixtures. The exact counts expose differences between fuser with inode cache, fuser without inode cache, and fuse-mt.

## Risks and observations
The file contains many TODOs questioning counts. Fuse-mt often performs fewer writes/stores than fuser in cross-directory moves. Fuser without inode cache frequently performs more loads/read-all operations due to repeated lookups. `to_existing_target` currently expects success and contains a TODO asking whether it should fail instead, making it a semantic risk as well as a performance test. The two fuse-mt-only cases indicate unresolved fixture-level deadlock risk.

## Test signals
The suite validates simple rename cost, cross-directory update cost, deep path lookup scaling, replacement cleanup/removal behavior, and support for directory and symlink renames. It also marks current benchmark/test instability: some scenarios cannot safely run across all fixture types.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/rename.rs -->
