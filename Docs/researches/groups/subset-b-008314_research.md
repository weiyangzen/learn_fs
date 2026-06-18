# Research Group subset-b-008314

This grouped report covers CryFS e2e performance-test operation modules under `sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations`. Each section is delimited for reconciliation into a source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/chown.rs -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/chown.rs

## Purpose
This module defines the `chown` performance counter suite. It measures ownership-change behavior for files, directories, symlinks, and files under increasingly deep parent directories. The operation under test is `fixture.filesystem.chown(Some(node), Some(Uid::from(1000)), Some(Gid::from(1000)))`.

## Important APIs, Types, And Functions
The module registers five cases with `crate::perf_test_macro::perf_test!(chown, [...])`: `file_in_rootdir`, `dir_in_rootdir`, `symlink_in_rootdir`, `file_in_nesteddir`, and `file_in_deeplynesteddir`. Each case accepts `impl TestDriver` and returns `impl TestReady`, chaining `create_filesystem()`, `setup`, `test`, and `expect_op_counts`.

It depends on `FilesystemDriver` for async filesystem calls, `ActionCounts` for expected aggregate counters, `FixtureType` for backend-specific expectations, and `Uid`/`Gid` from `cryfs_rustfs`. `PathComponent` and `AbsolutePath` build test names and symlink/deep-directory paths.

## Control Flow
Each case creates a fresh filesystem fixture, creates the target object during setup, runs exactly one `chown` in the measured phase, and asserts expected blobstore, high-level blockstore, and low-level blockstore actions. Root file, directory, and symlink cases differ only in setup object type. Nested and deeply nested cases first create parent directories with `mkdir` or `mkdir_recursive`, then create a child file and chown that returned node.

## State And Persistence Behavior
`chown` mutates metadata for an existing node. Expected counters consistently include one blob write and resize plus one low-level store, indicating persisted metadata update. Directory and symlink targets require full blob reads because their metadata/content layout differs from simple cached root files. Deeper paths increase loads and reads for `Fusemt` and especially `FuserWithoutInodeCache`, reflecting path lookup and inode-cache effects.

## Dependencies And Integration Points
The suite is generated across fixture drivers and atime modes by `perf_test!`. It integrates with `FilesystemFixture` through `fixture.filesystem` and with blockstore instrumentation through `BlobStoreActionCounts`, `HLActionCounts`, and `LLActionCounts`. It is sensitive to fixture backend semantics: `FuserWithInodeCache`, `Fusemt`, and `FuserWithoutInodeCache` have separate expected count branches.

## Risks And Edge Cases
Many expected counts are marked with TODO comments questioning correctness, especially why no-cache fuser performs more work than fuse-mt. The tests only cover setting both uid and gid to concrete values; they do not cover uid-only, gid-only, clearing values, permission failures, missing nodes, or chown on root. Since all calls unwrap, any behavior change fails hard but does not classify errors.

## Test Signals
Strong signals are fixed expected `store_load`, `blob_read_all`, `blob_read`, `blob_write`, `blob_resize`, `blob_num_bytes`, `blob_data`, `blob_data_mut`, `load`, and `store` counts per fixture type. Regressions in metadata persistence, path traversal cost, or inode-cache behavior should appear as counter mismatches.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/chown.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/create_file.rs -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/create_file.rs

## Purpose
This module defines the `create_file` performance counter suite. It measures creating files from the root directory, a nested directory, and a deeply nested directory, for both absent and already-existing names.

## Important APIs, Types, And Functions
The registered cases are `notexisting_from_rootdir`, `existing_from_rootdir`, `notexisting_from_nesteddir`, `existing_from_nesteddir`, `notexisting_from_deeplynesteddir`, and `existing_from_deeplynesteddir`. They use `filesystem.create_file(parent, PathComponent)` as the operation under test. Setup helpers include `mkdir`, `mkdir_recursive`, and an initial `create_file` for existing-name cases.

The file imports `ActionCounts`, `FixtureType`, `TestDriver`, `TestReady`, `BlobStoreActionCounts`, `HLActionCounts`, `LLActionCounts`, `AbsolutePath`, and `PathComponent`.

## Control Flow
Absent-name cases set up only the parent directory, then call `create_file` and unwrap success. Existing-name cases create the file during setup, then call `create_file` again during measurement and intentionally ignore the returned `Result`; this measures the failed/rollback path without requiring success.

## State And Persistence Behavior
Successful creation allocates a new store object and updates the parent directory. Expected counters include `store_create`, parent `store_load`, `blob_resize`, parent and child `blob_write`, `blob_flush`, high-level `store_flush_block`, low-level `exists`, and low-level `store`. Existing-name attempts still show `store_create` followed by `store_remove_by_id` / `store_remove`, implying speculative creation is rolled back when the name collision is detected.

Path depth affects load/read counts. Root creation has constant counts; nested and deep cases branch on `FixtureType`, with no-cache fuser carrying extra parent-path traversal work.

## Dependencies And Integration Points
`perf_test!` expands the cases for all fixture types and atime modes. The test driver supplies an instrumented in-memory blockstore in normal test mode. These tests integrate with path parsing through `PathComponent::try_from_str` and `AbsolutePath::try_from_str`.

## Risks And Edge Cases
The existing-name tests discard the error and therefore only assert performance side effects, not the exact error type. The module does not cover invalid names, root-as-file conflicts, permission failures, or concurrent creation. TODOs indicate uncertainty about expected counts, particularly what root or parent blocks are loaded and why no-cache fuser differs.

## Test Signals
Important signals are successful creation counters (`store_create`, `blob_write`, `blob_flush`, `exists`, `store`) and rollback counters (`store_remove_by_id`, `store_remove`, `remove`). Counter differences across root, nested, and deep paths indicate lookup and parent-directory update cost.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/create_file.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/fchmod.rs -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/fchmod.rs

## Purpose
This module defines the `fchmod` performance counter suite for changing permissions through an open file handle. It covers root, nested, and deeply nested files, with and without releasing the file handle after the operation.

## Important APIs, Types, And Functions
The `perf_test!(fchmod, [...])` registration expands six cases: each of `file_in_rootdir`, `file_in_nesteddir`, and `file_in_deeplynesteddir` is instantiated for `CLOSE_AFTER = false` and `true`. Each case uses `create_and_open_file`, then calls `filesystem.fchmod(file.clone(), &file_handle, Mode::from(0o644).add_file_flag())`.

The generic helper `maybe_close::<CLOSE_AFTER, _>` conditionally calls `release`. The module depends on `Mode`, `AbsolutePath`, `PathComponent`, the fixture driver traits, and the three action-count types.

## Control Flow
Setup creates a file and retains both the node handle and file handle. Nested cases create parent directories first. The measured phase updates permissions through `fchmod`, then optionally releases the open handle. Expected counts derive a local `close_after` integer so release-related persistence and flush work can be folded into the same expectation expression.

## State And Persistence Behavior
The permission update is a metadata mutation associated with an open handle. Without close, the expected `blob_write`, `blob_resize`, `blob_flush`, `blob_data_mut`, `store_flush_block`, and low-level `store` are often zero, indicating much of the dirty state may remain buffered. With close, release adds resize/write/flush/store work. Path depth only materially changes no-cache fuser lookup/read counts.

## Dependencies And Integration Points
This suite validates both fuser and fuse-mt implementations through `perf_test!`. It specifically exercises the file-handle API surface rather than path-only chmod. It integrates with `maybe_close`, which is shared across other open-handle operation tests.

## Risks And Edge Cases
Only a file mode is tested; directory modes, symlinks, invalid mode bits, closed handles, and permission failures are absent. The expectations assume release is the only close-related persistence point. Several TODO comments flag uncertainty around fuser without inode cache doing additional work.

## Test Signals
The main signals are the delta between `CLOSE_AFTER=false` and `true`, and fixture-specific load/read multipliers. A regression in open-handle metadata caching, release flush behavior, or inode-cache path reuse should change these counters.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/fchmod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/fchown.rs -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/fchown.rs

## Purpose
This module defines the `fchown` performance counter suite for changing owner and group through an open file handle. It mirrors the `fchmod` matrix but uses uid/gid metadata instead of mode bits.

## Important APIs, Types, And Functions
The six registered cases instantiate `file_in_rootdir`, `file_in_nesteddir`, and `file_in_deeplynesteddir` for both close behaviors. Each setup creates and opens a file, then the test calls `filesystem.fchown(file.clone(), &file_handle, Some(Uid::from(1000)), Some(Gid::from(1000)))` and optionally `maybe_close`.

Imports include `Uid`, `Gid`, `AbsolutePath`, `PathComponent`, `FixtureType`, and the instrumented action counters.

## Control Flow
The measured operation always runs against an existing open file. Parent directory setup varies by path depth. Expected count closures compute `close_after` and branch on `FixtureType`. Deep no-cache fuser cases have the highest load/read counts because resolving stored path-backed node handles traverses more ancestors.

## State And Persistence Behavior
`fchown` mutates file metadata. Like `fchmod`, most write/resize/flush/store counts are tied to optional release, suggesting dirty metadata is retained on the open handle until close in these measured scenarios. The call itself still loads and reads the file metadata. `blob_num_bytes` is used as a size/header signal and increases for no-cache fuser plus close.

## Dependencies And Integration Points
The suite is part of the generated `perf_test!` infrastructure and uses shared `maybe_close`. It is a direct consumer of the `FilesystemDriver` file-handle ownership API and the CryFS RustFS uid/gid wrapper types.

## Risks And Edge Cases
Only setting both uid and gid is tested. The suite does not cover `None` uid/gid combinations, unchanged ownership, invalid handles, root, symlink semantics, or authorization errors. The many TODO comments mean expected counts are empirical and may need redesign if the driver caching model changes.

## Test Signals
Useful signals are release-driven persistence counters, fixture-specific metadata loads, and depth-driven no-cache overhead. Any change to ownership update durability or handle release flushing should alter `blob_write`, `blob_resize`, `blob_flush`, `blob_data_mut`, `store_flush_block`, and low-level `store`.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/fchown.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/fgetattr.rs -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/fgetattr.rs

## Purpose
This module defines the `fgetattr` performance counter suite for reading attributes through an open file handle. It measures root, nested, and deeply nested files, both leaving the handle open and releasing it after the attribute read.

## Important APIs, Types, And Functions
The registered cases are `file_in_rootdir`, `file_in_nesteddir`, and `file_in_deeplynesteddir`, each instantiated with `CLOSE_AFTER=false` and `true`. The operation under test is `filesystem.fgetattr(file_ino.clone(), &file_fh)`. The optional close path uses `maybe_close`.

The module depends on `FilesystemDriver`, `ActionCounts`, `FixtureType`, `TestDriver`, `TestReady`, `BlobStoreActionCounts`, `HLActionCounts`, `LLActionCounts`, `AbsolutePath`, and `PathComponent`.

## Control Flow
Each setup creates and opens a file. The test phase reads attributes from the open file handle and optionally releases the handle. Expected counts compute `close_after` and branch by fixture type. Unlike mutation tests, no `blob_data_mut` is expected for the read itself.

## State And Persistence Behavior
`fgetattr` is read-only, but optional release can flush the file handle. Expected `blob_flush` and high-level `store_flush_block` equal `close_after`, while low-level stores remain absent. The operation loads metadata and reads blob data; no-cache fuser costs grow with path depth.

## Dependencies And Integration Points
This file exercises the open-handle attribute API rather than path-based `getattr`. It integrates with the same generated test matrix as write-like handle operations and with shared close behavior.

## Risks And Edge Cases
The suite does not verify returned attribute contents, only counters and success. It does not cover closed/invalid handles, directories, symlinks, root attributes, or atime-specific expectation differences even though the macro runs all atime modes. TODOs question expected counter values.

## Test Signals
Key signals are absence of mutation counters during `fgetattr`, presence of release flush counters when `CLOSE_AFTER=true`, and fixture/path-depth differences in loads and reads. This should catch accidental writes or cache regressions in attribute lookup.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/fgetattr.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/fsync.rs -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/fsync.rs

## Purpose
This module defines the largest fsync-related performance suites. It registers both `fsync_datasync` and `fsync_fullsync`, measuring `filesystem.fsync(file, &mut fh, DATASYNC)` across clean files, dirty small writes, dirty large writes, in-place writes, beyond-end writes, path depths, and optional release after sync.

## Important APIs, Types, And Functions
Two `perf_test!` invocations instantiate the same scenario list with `DATASYNC=true` and `DATASYNC=false`. Every scenario is also instantiated with `CLOSE_AFTER=false` and `true`. Important functions include `unchanged_empty_file_in_rootdir`, `unchanged_file_with_data_in_rootdir`, `unchanged_large_file_in_rootdir`, `unchanged_file_in_nested_dir`, `unchanged_file_in_deeply_nested_dir`, `after_small_write_to_empty_file`, `after_small_write_to_middle_of_small_file`, `after_small_write_beyond_end_of_small_file`, `after_small_write_to_middle_of_large_file`, `after_small_write_beyond_end_of_large_file`, `after_large_write_to_empty_file`, `after_large_write_to_middle_of_large_file`, `after_large_write_beyond_end_of_large_file`, `after_write_to_file_in_nested_dir`, and `after_write_to_file_in_deeply_nested_dir`.

The module uses `test_noflush` and `setup_noflush` to preserve dirty state until the measured `fsync`, `NumBytes` for offsets and sizes, `BLOCKSIZE_BYTES`, `NUM_BYTES_FOR_THREE_LEVEL_TREE`, and `maybe_close`.

## Control Flow
Clean-file scenarios create/open a file and sometimes pre-write data in setup, then run `fsync` without an automatic fixture flush. Dirty scenarios create/open a file, use `setup_noflush` to perform a write that remains unflushed, then measure `fsync`. The write matrix covers one-byte writes, block-middle writes, writes beyond EOF, large writes of `NUM_BYTES_FOR_THREE_LEVEL_TREE`, and nested/deep parent paths. After `fsync`, the test may release the handle.

Expected counters derive both `datasync` and `close_after` as integers. Many expressions subtract metadata writes when datasync is true and the handle is not closed, while close-after adds release flush work.

## State And Persistence Behavior
`fsync` persists dirty file data and sometimes metadata, with datasync expected to avoid some metadata persistence when the handle remains open. Clean files mostly flush already-open stores and show load/read/flush counters without resize/write. Dirty writes introduce `blob_resize`, `blob_write`, `blob_data_mut`, low-level `store`, and high-level `store_flush_block`. Large file scenarios load and flush more high-level blocks. Nested and deep cases add path traversal overhead, especially for no-cache fuser.

The explicit TODO block at the top flags uncertainty around flush operations loading low-level blocks and some flush-after-write paths not storing low-level data.

## Dependencies And Integration Points
This suite is tightly coupled to the filesystem fixture's no-flush phases and to the blockstore instrumentation model. It exercises `FilesystemDriver::write`, `fsync`, `release`, `mkdir`, `mkdir_recursive`, and `create_and_open_file`. It is generated across all fixture types and atime behaviors, making it a broad integration signal for fuser, fuse-mt, cache, and persistence layers.

## Risks And Edge Cases
The module contains many empirical counter formulas, making it sensitive to legitimate storage-layout or cache changes. It does not assert file contents after sync, crash recovery, or exact datasync/fullsync durability semantics outside counters. It covers files only, not directory fsync. The arithmetic formulas can obscure intended behavior and are vulnerable to off-by-one mistakes when close and datasync interact.

## Test Signals
Primary signals are differences between datasync and fullsync, clean and dirty files, small and large file trees, in-place and beyond-EOF writes, and close/no-close release behavior. Counter mismatches in `blob_flush`, `blob_resize`, `blob_write`, `store_flush_block`, `blob_data_mut`, low-level `store`, and load counts point to persistence or cache behavior changes.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/fsync.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/ftruncate.rs -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/ftruncate.rs

## Purpose
This module defines the `ftruncate` performance counter suite for resizing open files. It measures small and large growth, small and large shrink, growth of nonempty files, and ordinary truncate-to-1024 behavior at root, nested, and deeply nested paths. Every scenario is run with and without closing the handle afterward.

## Important APIs, Types, And Functions
The registered functions are `grow_empty_file_small`, `grow_empty_file_large`, `shrink_file_small`, `shrink_file_large`, `grow_nonempty_file_small`, `grow_nonempty_file_large`, `file_in_rootdir`, `file_in_nesteddir`, and `file_in_deeplynesteddir`, all parameterized by `const CLOSE_AFTER: bool`. The operation under test is `filesystem.ftruncate(file.clone(), &file_handle, NumBytes::from(...))`.

The suite uses `NUM_BYTES_FOR_THREE_LEVEL_TREE` to force multi-block tree allocation/removal, `NumBytes` for sizes, `maybe_close` for optional release, and the usual fixture/action-count types.

## Control Flow
Each case creates and opens a file. Growth cases truncate empty or pre-sized files to a larger value. Shrink cases first grow a file to `NUM_BYTES_FOR_THREE_LEVEL_TREE` in setup, then shrink to either one byte less or one byte. Nonempty growth cases pre-truncate to 100 bytes, then grow slightly or to the large tree size. Path-depth cases create parent directories and truncate to 1024 bytes.

Expected counts are computed from `close_after` and fixture type. Large growth expects many high-level `store_create` and low-level `exists`/`store` operations; large shrink expects removal counts.

## State And Persistence Behavior
`ftruncate` changes file size and can allocate or remove block-tree nodes. Small growth/shrink mainly resize metadata/data blobs. Large growth creates many stores and mutates many high-level blob-data entries. Large shrink removes high-level and low-level blocks (`store_remove`, `store_remove_by_id`, `remove`). Optional close adds flush and store work. Path depth mostly changes lookup cost; file tree size changes allocation/removal cost.

## Dependencies And Integration Points
The suite exercises open-file resize semantics in the `FilesystemDriver`, storage tree sizing constants in the fixture, and release behavior through `maybe_close`. It integrates with both fuser and fuse-mt generated tests and all atime behaviors.

## Risks And Edge Cases
There are no tests for truncating directories, invalid handles, permission failures, sparse holes beyond the covered write-free growth, or zero-size shrink from nonempty file except indirectly through small sizes. The large-tree constants tightly couple expected counts to internal tree fanout. TODOs flag uncertainty about no-cache fuser overhead.

## Test Signals
Strong signals are allocation counts for large growth (`store_create`, `exists`, high-level `blob_data_mut`), removal counts for large shrink, and close-driven flush/store counters. The suite should catch changes in file tree representation, sparse resize policy, and release durability.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/ftruncate.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/futimens.rs -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/futimens.rs

## Purpose
This module defines the `futimens` performance counter suite for updating atime and mtime through an open file handle. It covers root, nested, and deeply nested files, each with optional release after the timestamp update.

## Important APIs, Types, And Functions
The registered cases are `file_in_rootdir`, `file_in_nesteddir`, and `file_in_deeplynesteddir` for `CLOSE_AFTER=false` and `true`. The test constructs deterministic timestamps from `SystemTime::UNIX_EPOCH + Duration::from_secs(1000/2000)` and calls `filesystem.futimens(file.clone(), &file_handle, Some(atime), Some(mtime))`.

The module imports `FilesystemDriver as _` to bring trait methods into scope, `maybe_close`, `SystemTime`, `Duration`, path types, and the standard action-count types.

## Control Flow
Setup creates and opens a file, optionally under parent directories. The measured phase computes atime and mtime, updates them through `futimens`, and conditionally releases the handle. Expected counts use `close_after` and fixture type branches.

## State And Persistence Behavior
Timestamp update is a metadata mutation on an open file. Without close, expected write/resize/flush/store counters are mostly absent, suggesting dirty metadata remains buffered. With close, release adds blob resize/write/flush, high-level `blob_data_mut` and `store_flush_block`, and low-level `store`. Path depth affects no-cache fuser load/read counts.

## Dependencies And Integration Points
This suite interacts with open-handle timestamp update semantics and the shared release helper. Although the macro runs all atime behavior modes, the expected counts ignore `_atime_behavior`, so any atime mode-specific timestamp side effect is expected not to change these counters.

## Risks And Edge Cases
Only both atime and mtime set to concrete values are covered. The suite does not test `None` values, ctime behavior, directories, symlinks, invalid handles, time precision, or values before epoch. Expected counts include TODO uncertainty about fuser no-cache work.

## Test Signals
Signals are the absence/presence of persistence counters around `CLOSE_AFTER`, deterministic metadata update loads, and path-depth overhead. Regressions in timestamp buffering or release flushing should change `blob_write`, `blob_resize`, `blob_flush`, `blob_data_mut`, `store_flush_block`, or low-level `store`.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/futimens.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/getattr.rs -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/getattr.rs

## Purpose
This module defines the path/node-handle `getattr` performance counter suite. It measures attributes for root, files, directories, symlinks, and files under nested/deep paths.

## Important APIs, Types, And Functions
Registered cases are `rootdir`, `file_in_rootdir`, `dir_in_rootdir`, `symlink_in_rootdir`, `file_in_nesteddir`, and `file_in_deeplynesteddir`. The operation is `fixture.filesystem.getattr(None)` for root or `getattr(Some(node))` for created objects.

Setup uses `create_file`, `mkdir`, `create_symlink`, and `mkdir_recursive`. The module relies on `AbsolutePath` for symlink targets and deep paths, plus the usual perf-test and action-count types.

## Control Flow
Each non-root case creates the object in setup, then reads its attributes during measurement. Root has no setup and calls `getattr(None)`. Expected counts branch by fixture type for all non-root cases; root expects all zero counters because root attributes are not stored in blobs.

## State And Persistence Behavior
`getattr` is read-only. File, directory, and symlink attribute reads load stores and read blob data but do not write, resize, flush, or store. Directories and symlinks require full reads in root cases; file root with inode cache can avoid `blob_read_all`. Deeper paths add traversal loads for fuse-mt and no-cache fuser.

## Dependencies And Integration Points
The suite compares path/inode cache behavior across generated fixture types. It is the path-handle counterpart to `fgetattr.rs`, and its zero-root expectation documents a special root metadata path in the filesystem implementation.

## Risks And Edge Cases
The tests do not assert returned attributes, only counters. They do not cover missing nodes, stale handles, permission errors, or atime-specific differences. Several expected counts are marked as needing confirmation.

## Test Signals
Key signals are zero root storage access, read-only counters for non-root objects, object-type differences (`blob_read_all` for dir/symlink), and path-depth cache behavior. Any accidental metadata write during `getattr` should be caught.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/getattr.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/init.rs -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/init.rs

## Purpose
This module defines the `init` performance counter suite for initializing a previously uninitialized filesystem.

## Important APIs, Types, And Functions
The suite registers one case, `init`, with `perf_test!(init, [init,])`. It uses `test_driver.create_uninitialized_filesystem()`, then calls `fixture.filesystem.init().await.unwrap()` in `test_no_counter_reset`. Expected counters include root blob creation and sanity-check reads.

Imports are limited to `FilesystemDriver`, `ActionCounts`, `TestDriver`, `TestReady`, and the three action-count types.

## Control Flow
Setup intentionally does nothing. Unlike most operation tests, the measured phase uses `test_no_counter_reset`, so initialization counters include work performed from the uninitialized fixture state rather than being reset immediately before the operation. The test then asserts a single fixed counter set.

## State And Persistence Behavior
Initialization creates the root directory blob, writes and flushes it, then loads and reads it for filesystem sanity checking. Low-level counts include `exists`, `store`, and `overhead`; high-level counts include `store_try_create`, `store_load`, `store_flush_block`, and `store_overhead`.

## Dependencies And Integration Points
This is the bootstrap performance signal for the filesystem fixture and blockstore stack. It exercises root creation through blobstore, high-level blockstore, and low-level blockstore layers before normal file operations can run.

## Risks And Edge Cases
The test only covers successful initialization of a fresh uninitialized filesystem. It does not cover reinitialization, corrupt root blobs, existing incompatible stores, or initialization failures. A TODO questions why root data is written after creation rather than created with data directly.

## Test Signals
Important signals are exactly one root `store_try_create`, one root low-level `store`, sanity-check load/read counts, and overhead accounting. Changes here indicate bootstrap layout or initialization validation changes.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/init.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/lookup.rs -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/lookup.rs

## Purpose
This module defines the `lookup` performance counter suite for resolving child names under parent nodes. It tests existing and missing children from root, nested, and deeply nested directories.

## Important APIs, Types, And Functions
The module uses `perf_test_only_fuser!` because fuse-mt does not expose a lookup operation. Registered cases are `existing_from_rootdir`, `notexisting_from_rootdir`, `existing_from_nesteddir`, `notexisting_from_nesteddir`, `existing_from_deeplynesteddir`, and `notexisting_from_deeplynesteddir`. The operation is `filesystem.lookup(parent, PathComponent)` with `unwrap()` for existing cases and `unwrap_err()` for missing cases.

The code imports `FixtureType` but uses `unreachable!` for `Fusemt` branches in expectations as an additional guard.

## Control Flow
Existing cases create the target file in setup, returning the parent node when needed, then look up the child by name. Missing cases create only the parent directory, then look up a missing name and require an error. Expected counts branch between fuser with and without inode cache.

## State And Persistence Behavior
Lookup is read-only. Existing lookups load the parent directory and the child metadata, so they have more loads than missing lookups, which stop after reading the parent directory. Deep parent nodes add traversal reads for no-cache fuser. No blob writes, resizes, flushes, or stores are expected.

## Dependencies And Integration Points
This suite exercises fuser-specific lookup behavior and validates the perf macro's ability to disable fuse-mt. It integrates with directory creation and file creation setup but measures only lookup. It is a direct signal for inode cache and path resolution behavior.

## Risks And Edge Cases
The missing-name tests assert only that an error exists, not the exact error code. The suite does not cover directories or symlinks as lookup targets, invalid names, root lookup by special names, case sensitivity, or permission-denied lookup. Expected counts have TODO uncertainty.

## Test Signals
Signals include existing-vs-missing load deltas, root-vs-nested-vs-deep traversal costs, and fuser inode-cache effects. Any accidental mutation or fuse-mt registration would be caught by counters or unreachable branches.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/lookup.rs -->
