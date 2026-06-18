<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/tests/low_level/tests.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/tests/low_level/tests.rs

Purpose: This file is the reusable conformance suite for the low-level `BlockStore` API. It exports `instantiate_lowlevel_blockstore_specific_tests!` and a helper macro that instantiate the same async tests for any implementation satisfying the `LLFixture` contract. The suite validates semantics for `try_create`, `load`, `store`, `remove`, `num_blocks`, `all_blocks`, `exists`, and overhead conversion.

Important APIs and flow: The public macro expands into grouped `tokio::test` modules, while `_instantiate_lowlevel_blockstore_specific_tests!` emits each concrete test function. Tests acquire `f.store().await`, mutate it through low-level reader/writer/deleter traits, call `f.yield_fixture(&store).await` after important state changes, assert exact results such as `TryCreateResult::SuccessfullyCreated` and `RemoveResult::SuccessfullyRemoved`, then explicitly `async_drop()` the store.

State and persistence: The tests exercise block persistence through repeated write/read/remove cycles, duplicate ids, empty data blocks, overwritten blocks, and enumeration after deletion. `yield_fixture` is the integration hook that lets fixtures flush, pause, or validate wrapper-specific durable state between operations.

Dependencies and integration: It uses deterministic helpers from `tests::utils`, the low-level traits from `crate::low_level`, result enums from `crate::utils`, `futures::TryStreamExt` for `all_blocks`, `Byte` for overhead checks, and `assert_unordered_vec_eq` for enumeration order independence. It is pulled into implementation test modules through crate-level macros rather than direct test discovery.

Risks and test signals: The suite gives strong coverage for CRUD and listing contracts but leaves TODO gaps for free-space estimation, optimized writer behavior, and size-changing overwrite behavior. It assumes exact fixture behavior around explicit async drop, so implementations that rely on background flushing need fixture adapters to make those transitions observable.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/tests/low_level/tests.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/tests/mod.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/tests/mod.rs

Purpose: This test module root wires together `high_level`, `low_level`, and `utils`, and exports macros that test blockstore implementations through both native and adapter-wrapped API surfaces. It is the bridge that lets one implementation be validated as low-level, high-level, and round-tripped through adapter layers.

Important APIs and flow: `instantiate_blockstore_tests_for_lowlevel_blockstore!` runs the low-level suite directly, wraps the low-level fixture into high-level fixtures with and without flushing, then double-wraps high-level back to low-level. `instantiate_blockstore_tests_for_highlevel_blockstore!` performs the symmetric high-level-first matrix and then wraps through low-level adapters.

State and persistence: The macros intentionally vary flushing behavior. That makes persistence and buffering semantics testable across adapter boundaries, especially where high-level stores may cache writes or low-level stores may require explicit flush-like transitions.

Dependencies and integration: This file depends on macro exports from the low-level and high-level test modules plus fixture adapters under `tests::low_level` and `tests::high_level`. It integrates implementation crates by letting each implementation invoke one macro and receive a full nested module test tree.

Risks and test signals: The wrapping matrix is valuable for detecting semantic mismatches between APIs, but macro expansion hides the generated test topology and can produce large compile-time output. Failures will surface in nested modules such as `wrapped_in_high_level::with_flushing`, which is useful but requires understanding the adapter path.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/tests/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/tests/utils.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/tests/utils.rs

Purpose: This file provides deterministic test fixtures for blockstore tests. `blockid(seed)` derives a stable 16-byte `BlockId`, and `data(size, seed)` returns reproducible `Data` bytes.

Important APIs and flow: `data` uses `DataFixture::new(seed).get(size).into()`. `blockid` uses the deterministic bytes from `data(16, seed)` and parses them as a `BlockId`.

State and persistence: The helpers are pure and have no persistence. Their role is to make stored block contents and ids stable across runs, implementations, and assertion points.

Dependencies and integration: The module depends on `cryfs_utils::data::Data`, `DataFixture`, and crate `BlockId`. It is used heavily by low-level conformance tests to avoid hand-written byte fixtures.

Risks and test signals: Because ids are generated from pseudo-random fixture bytes, tests cover realistic opaque identifiers while remaining deterministic. Any change in `DataFixture` output would affect many expected block ids indirectly.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/tests/utils.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/utils.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/utils.rs

Purpose: This file defines small result enums shared by blockstore operations. `TryCreateResult` reports whether an atomic create inserted a block or found an existing id, and `RemoveResult` reports whether removal deleted a block or found nothing.

Important APIs and flow: Both enums derive equality/debug traits and are marked `#[must_use]`, encouraging callers and tests to inspect operation outcomes instead of treating the operations as fire-and-forget.

State and persistence: The enums represent persistent state transitions at the API boundary: successful creation/removal changes the backing store, while already-exists/not-found variants leave it unchanged.

Dependencies and integration: These types are imported by low-level implementations and tests, and external crates can match on them through the blockstore crate API. They avoid overloading `Result` errors for expected existence races.

Risks and test signals: The enum names are explicit and stable, but adding variants would require updating exhaustive matches. The low-level conformance tests assert exact values for all core create/remove paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/utils.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/Cargo.toml -->
# sources/security-integrity/cryfs/crates/check/Cargo.toml

Purpose: This manifest defines the `cryfs-check` crate and binary. It is a workspace Rust package for checking CryFS vault integrity and reporting structural corruption.

Important APIs and flow: The `[[bin]]` entry names the executable `cryfs-check`. Runtime dependencies include CryFS block/blob/fsblob/config/CLI/version crates, async/runtime libraries, `clap`, `futures`, `tokio`, `thiserror`, `console`, `itertools`, and logging support.

State and persistence: The crate depends on blockstore, fsblobstore, config, and local-state-aware CLI utilities, but the application wraps the blockstore read-only during checking. Dev dependencies enable fixture-based integration tests that create and corrupt temporary filesystems.

Dependencies and integration: The `check_for_updates` feature forwards to `cryfs-cli-utils/check_for_updates`. Dev dependencies enable `testutils` features on fsblobstore, blockstore, and config crates, plus `rstest`, `pretty_assertions`, `rand`, and `tempfile`.

Risks and test signals: The manifest has broad internal crate coupling, which is expected for an end-to-end checker. Feature forwarding means CLI behavior may change with workspace feature selection, and integration tests rely on the testutils features being available.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/args.rs -->
# sources/security-integrity/cryfs/crates/check/src/args.rs

Purpose: This file defines the command-line argument struct for `cryfs-check`. `CryfsRecoverArgs` currently accepts one positional vault directory path.

Important APIs and flow: The struct derives `clap::Parser` and has `vaultdir: PathBuf` with `value_parser=parse_path`, delegating path parsing behavior to shared CLI utilities.

State and persistence: It stores only user input. The path later determines the on-disk blockstore root and `cryfs.config` path used by the CLI.

Dependencies and integration: It integrates with `cryfs_cli_utils::run::<RecoverCli>()` through the `Application` trait implementation in `cli.rs`.

Risks and test signals: The argument surface is intentionally small; TODOs elsewhere indicate config path customization and noninteractive password handling are not yet exposed here.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/args.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/assertion.rs -->
# sources/security-integrity/cryfs/crates/check/src/assertion.rs

Purpose: This module defines internal assertions that checks and the runner use to verify expected correlated errors are eventually reported. It is a self-checking mechanism for the checker algorithm, not a user-facing corruption type.

Important APIs and flow: `Assertion` has `ExactErrorWasReported(CorruptedError)` and `ErrorMatchingPredicateWasReported(Box<dyn Send + Fn(&CorruptedError) -> bool>, Location)`. Constructors build exact or predicate assertions; `validate` scans the final reported errors and panics if an expected error is absent.

State and persistence: Assertions live in `CheckResult` until finalization. They are in-memory consistency checks that tie partial observations, such as unreadable blobs or duplicate references, to final diagnostic output.

Dependencies and integration: The module depends on `CorruptedError` and `std::panic::Location`. `AllChecks`, `CheckParentPointers`, `CheckUnreferencedNodes`, and the runner add assertions for cases where one subsystem should detect an error discovered indirectly by another.

Risks and test signals: Failed assertions panic, which is appropriate for algorithm invariant violations but not graceful for end users if an edge case is missed. Predicate assertions preserve caller locations, improving debugging of checker implementation defects.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/assertion.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/bin/cryfs-check.rs -->
# sources/security-integrity/cryfs/crates/check/src/bin/cryfs-check.rs

Purpose: This is the binary entrypoint for the `cryfs-check` executable.

Important APIs and flow: `main` returns `ExitCode` and delegates all parsing, setup, logging, and error handling to `cryfs_cli_utils::run::<RecoverCli>()`.

State and persistence: The file has no state. Runtime behavior is owned by `RecoverCli`.

Dependencies and integration: It imports `cryfs_check::RecoverCli`, which is exported by the library crate. This keeps the binary thin and testable logic in `lib.rs` modules.

Risks and test signals: There are no local tests. A TODO notes integration tests for the binary path, while existing crate integration tests call checker helpers through fixtures.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/bin/cryfs-check.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/checks/blobs_readable.rs -->
# sources/security-integrity/cryfs/crates/check/src/checks/blobs_readable.rs

Purpose: This check reports reachable blobs that could not be loaded at all. It does not verify every underlying data node; the file explicitly notes that it only catches whole-blob load failures.

Important APIs and flow: `CheckBlobsReadable` stores `unreadable_blobs: BTreeMap<BlobId, BTreeSet<BlobReference>>`. `process_reachable_blob` records `BlobToProcess::Unreadable`, `process_reachable_blob_again` delegates to the same path so duplicate references are accumulated, node callbacks do nothing, and `finalize` emits one `BlobUnreadableError` per unreadable id.

State and persistence: State is in-memory aggregation keyed by `BlobId`. A `BTreeMap`/`BTreeSet` gives deterministic ordering for errors and display tests.

Dependencies and integration: It implements `FilesystemCheck` and is included in `AllChecks`. It depends on `BlobToProcess`, `BlobReference`, and `BlobUnreadableError`.

Risks and test signals: It relies on the runner to classify unreadable blobs correctly. It intentionally does not inspect partial readability, so node-level unreadability is covered by `unreferenced_nodes` and runner traversal instead.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/checks/blobs_readable.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/checks/check_result.rs -->
# sources/security-integrity/cryfs/crates/check/src/checks/check_result.rs

Purpose: `CheckResult` is the accumulation object for checker errors and internal assertions.

Important APIs and flow: It stores `errors: Vec<CorruptedError>` and `assertions: Vec<Assertion>`. `add_error`, `add_assertion`, and `add_all` merge outputs from individual checks. `peek_errors` allows invariant checks before final ownership is consumed. `finalize` validates every assertion against the final error vector, then returns errors.

State and persistence: All state is in-memory during one checker run. No deduplication is performed here; checks are responsible for deterministic aggregation before adding errors.

Dependencies and integration: It is used by individual `FilesystemCheck` implementations and by `AllChecks::finalize`. The assertion link makes algorithmic self-tests part of normal result finalization.

Risks and test signals: Because assertion validation can panic, a missing correlated error becomes a checker bug rather than a reported corruption. This is useful during development but could be harsh in production for unanticipated corruptions.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/checks/check_result.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/checks/mod.rs -->
# sources/security-integrity/cryfs/crates/check/src/checks/mod.rs

Purpose: This module defines the common filesystem-checking interface and the `AllChecks` fan-out aggregator used by the runner. It centralizes how blob and node observations are delivered to individual checks.

Important APIs and flow: `BlobToProcess` wraps readable `FsBlob` references or unreadable `BlobId`s. `NodeToProcess` wraps readable `DataNode`s or unreadable `BlockId`s. `FilesystemCheck` defines callbacks for reachable blobs, repeated reachable blobs, reachable nodes, unreachable nodes, and finalization. `AllChecks` owns mutex-protected `CheckUnreferencedNodes`, `CheckParentPointers`, `CheckBlobsReadable`, plus `additional_errors`.

State and persistence: Each check accumulates in-memory reference state while the runner traverses concurrently. Mutexes make `AllChecks` safe to call from multiple spawned tasks, but the checks themselves remain sequential critical sections.

Dependencies and integration: This module imports CryFS blobstore/blockstore/fsblobstore types and reexports internal check modules. The runner calls only `AllChecks` methods, keeping traversal separate from corruption-specific logic.

Risks and test signals: Adding a new check requires updating each fan-out method manually; TODO comments call out the risk of forgetting a member. The top-level TODO list documents many future integrity checks that are not yet implemented, including tree balance, cycles, type mismatches, directory-entry validity, zeroed unused space, and integrity block ids.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/checks/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/checks/parent_pointers.rs -->
# sources/security-integrity/cryfs/crates/check/src/checks/parent_pointers.rs

Purpose: This check verifies that each reachable blob's stored parent pointer matches at least one parent blob that references it, and it also detects multiple references to the same blob.

Important APIs and flow: `CheckParentPointers` uses `ReferenceChecker<BlobId, SeenBlobInfo, BlobReference>`. The root blob is initially marked referenced as `BlobReference::root_dir()`. Readable blobs are marked seen with blob type and parent pointer; directory entries mark child blobs referenced with computed paths and entry types. Unreadable blobs are marked seen with the current reference. Finalization reports `BlobReferencedMultipleTimesError`, `WrongParentPointerError`, or adds assertions for unreadable/missing cases expected to be reported elsewhere.

State and persistence: The check builds an in-memory map of observed blob ids, observed parent pointers, and all incoming references. It does not write state and ignores unreachable nodes.

Dependencies and integration: It depends on `FsBlob`, `BlobType`, `EntryType`, `ReferenceChecker`, `BlobReference`, `MaybeBlobInfoAsSeenByLookingAtBlob`, and typed errors. It is called through `AllChecks` for every reachable blob.

Risks and test signals: `process_reachable_blob_again` is still TODO, so duplicate-reference behavior is currently handled mainly by the reference checker state accumulated from directory entries and first processing. Missing blobs are asserted through `NodeMissingError` because a blob's root node absence represents the missing blob at lower layers. It panics on impossible unreferenced reachable blobs.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/checks/parent_pointers.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/checks/unreferenced_nodes.rs -->
# sources/security-integrity/cryfs/crates/check/src/checks/unreferenced_nodes.rs

Purpose: This module checks node graph consistency: existing nodes should be referenced, referenced nodes should exist, unreadable nodes should be reported, and nodes should not be referenced multiple times. It handles reachable and unreachable node sets separately so dangling blob trees can be reported at their roots.

Important APIs and flow: `UnreferencedNodesReferenceChecker` wraps `ReferenceChecker<BlockId, SeenInfo, ReferencedAs>` plus `CheckResult`. Readable nodes are marked seen with leaf/inner depth and inner-node children are marked referenced. Unreadable nodes are marked seen as unreadable and add an assertion for `NodeUnreadableError`. Readable directory blobs mark child blob root nodes referenced. Finalization emits `NodeMissingError`, `NodeUnreadableError`, `NodeReferencedMultipleTimesError`, and `NodeUnreferencedError`.

State and persistence: Two in-memory checkers are kept: one for nodes reachable from the filesystem root and one for unreachable nodes found by scanning all blocks. The reachable checker is seeded with the root blob's root node reference.

Dependencies and integration: It integrates with `FilesystemCheck`, `BlobToProcess`, `NodeToProcess`, `DataNode`, fsblobstore directory entries, and node/blob reference model types. The runner feeds reachable node references with full blob context, while `check_all_unreachable_nodes` passes unreachable nodes without root reachability context.

Risks and test signals: The module has TODOs around unreachable blob processing and invariant panics. It assumes the runner sends reachable nodes consistently; unexpected `NodeUnreferenced` in the reachable checker is treated as an algorithm bug. It is central to integration tests such as missing blob scenarios.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/checks/unreferenced_nodes.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/checks/utils/mod.rs -->
# sources/security-integrity/cryfs/crates/check/src/checks/utils/mod.rs

Purpose: This module exposes utility helpers for checks.

Important APIs and flow: It currently declares only `pub mod reference_checker;`, making the generic reference tracking helper available to sibling check modules.

State and persistence: It owns no state. State lives in `reference_checker.rs` instances.

Dependencies and integration: It is imported by `checks::parent_pointers` and `checks::unreferenced_nodes` through `super::utils::reference_checker::ReferenceChecker`.

Risks and test signals: The module is intentionally minimal. Any future utility exports should remain generic enough to avoid coupling check implementations unnecessarily.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/checks/utils/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/checks/utils/reference_checker.rs -->
# sources/security-integrity/cryfs/crates/check/src/checks/utils/reference_checker.rs

Purpose: `ReferenceChecker` is a generic helper for tree/graph checks where each id may be seen directly and referenced by zero or more parents.

Important APIs and flow: It stores `HashMap<NodeId, (Option<SeenInfo>, Vec<ReferenceInfo>)>`. `mark_as_seen` records direct observation and panics if the same id is seen twice. `mark_as_referenced` appends incoming reference metadata. `finalize` consumes the map and yields `(id, seen_info, references)` for caller-specific error generation.

State and persistence: All state is in memory and scoped to one check instance. It preserves every reference in a `Vec`, so callers can distinguish zero, one, and multiple references.

Dependencies and integration: It is generic over hashable ids and metadata. `CheckParentPointers` uses it for blobs, and `CheckUnreferencedNodes` uses it for nodes.

Risks and test signals: The panic on duplicate seen ids enforces a runner invariant that each node/blob is processed once in the relevant checker. Duplicate references are allowed and intentionally represented for error reporting.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/checks/utils/reference_checker.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/cli.rs -->
# sources/security-integrity/cryfs/crates/check/src/cli.rs

Purpose: This file implements the `cryfs-check` CLI application and the public `check_filesystem` entrypoint used by tests or callers.

Important APIs and flow: `RecoverCli` implements `Application` with name/version/logging, creates a multi-thread Tokio runtime, prints the target vault path, builds an `OnDiskBlockStore`, uses `InteractivePasswordProvider`, calls `check_filesystem`, prints each `CorruptedError`, then prints a count. `check_filesystem` wraps the blockstore in `ReadOnlyBlockStore`, loads config read-only, prints config, sets up the blockstore stack, and invokes `RecoverRunner` as a `BlockstoreCallback`.

State and persistence: The intended blockstore access is read-only, but a TODO notes read-only blockstore may not be sufficient to prevent local-state or integrity-data writes. Config is loaded through `cryfs_config::config::load_readonly` with command-line flags that treat missing blocks as not integrity violations.

Dependencies and integration: It depends heavily on `cryfs_cli_utils`, `cryfs_config`, `cryfs_blockstore`, `cryfs_utils::progress`, and `RecoverRunner`. Integrity config currently allows violations so the checker can continue collecting corruption diagnostics.

Risks and test signals: Noninteractive password handling is not implemented, custom config paths are TODO, integrity violation callback is empty, and exit codes are not specialized. `RecoverConsole` contains TODO methods that can panic if config loading requires migration or other prompts.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/cli.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/console.rs -->
# sources/security-integrity/cryfs/crates/check/src/console.rs

Purpose: `RecoverConsole` implements the `cryfs_config::config::Console` trait for config loading during check operations.

Important APIs and flow: Every prompt-like method currently calls `todo!()`: migration, changed encryption key, replaced filesystem, single-client-mode decisions, new filesystem settings, cipher/blocksize prompts, and creating directories.

State and persistence: The console stores no state. Its methods would normally gate config or local-state decisions, but this check path expects read-only existing filesystems and should not create or migrate vaults.

Dependencies and integration: It is passed to `cryfs_config::config::load_readonly` in `cli.rs`. It depends on `ScryptSettings`, `Byte`, `Version`, `VersionInfo`, and path types required by the trait.

Risks and test signals: Any config load path that asks a question will panic. This is a major operational limitation for vaults requiring migration, changed-key confirmation, replaced-filesystem confirmation, or missing directory creation prompts.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/console.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/error/blob_referenced_multiple_times.rs -->
# sources/security-integrity/cryfs/crates/check/src/error/blob_referenced_multiple_times.rs

Purpose: This file defines the corruption error for a blob id referenced by multiple parent directory entries.

Important APIs and flow: `BlobReferencedMultipleTimesError` contains `blob_id`, `blob_info: MaybeBlobInfoAsSeenByLookingAtBlob`, and `referenced_as: BTreeSet<BlobReference>`. `new` asserts at least two references. `Display` builds a shared `BlobErrorDisplayMessage` with title `BlobReferencedMultipleTimes`.

State and persistence: It is immutable diagnostic data. `BTreeSet` gives deterministic reference ordering for equality and display output.

Dependencies and integration: It is produced by `CheckParentPointers`, included in `CorruptedError`, and displayed through `error/display/blob_error.rs`.

Risks and test signals: Unit tests cover missing, unreadable, file/dir/symlink readable blobs, and many-reference formatting using `strip_ansi_codes`. The constructor invariant protects against malformed single-reference errors.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/error/blob_referenced_multiple_times.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/error/blob_unreadable.rs -->
# sources/security-integrity/cryfs/crates/check/src/error/blob_unreadable.rs

Purpose: This file defines the corruption error for reachable blobs that fail to load.

Important APIs and flow: `BlobUnreadableError` stores `blob_id` and all known `referenced_as` `BlobReference`s. `new` constructs the error, and `Display` renders a blob error message with `MaybeBlobInfoAsSeenByLookingAtBlob::Unreadable`.

State and persistence: Diagnostic state is immutable and uses `BTreeSet` for deterministic output. The underlying load error is not stored yet; a TODO reserves space for an `anyhow::Error`.

Dependencies and integration: It is emitted by `CheckBlobsReadable` and asserted by parent-pointer and runner paths when unreadable blobs are observed.

Risks and test signals: Tests cover file, dir, symlink, and multi-reference display. Missing root-cause error details may limit repair diagnostics because the exact blockstore/blobstore read failure is discarded.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/error/blob_unreadable.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/error/display/blob_error.rs -->
# sources/security-integrity/cryfs/crates/check/src/error/display/blob_error.rs

Purpose: This module provides shared display formatting for blob-related corruption errors.

Important APIs and flow: `BlobErrorDisplayMessage` combines an `ErrorTitle` and `ErrorDisplayBlobInfo`. `display` writes the title, all references, blob id, and blob info. Helper functions render blob references and missing/unreadable/readable blob info including type and parent pointer.

State and persistence: It has no persistent state. It consumes iterator inputs over references and writes to a formatter.

Dependencies and integration: It depends on `console::style`, `BlobId`, `BlobType`, `BlobReference`, and `MaybeBlobInfoAsSeenByLookingAtBlob`. Blob error `Display` implementations compose this type.

Risks and test signals: The reference iterator is consumed exactly once, so callers pass iterators from deterministic sets. ANSI styling is stripped in tests for stable assertions; changes in text shape affect many display tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/error/display/blob_error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/error/display/error_title.rs -->
# sources/security-integrity/cryfs/crates/check/src/error/display/error_title.rs

Purpose: This module centralizes the title line used by corruption error displays.

Important APIs and flow: `ErrorTitle` stores static `error_type` and `error_message`. Its `Display` implementation renders `Error[type]: message` with colored/bold styling through `console::style`.

State and persistence: It is a small value object with no runtime state beyond static strings.

Dependencies and integration: It is used by blob and node display helpers and by every concrete error's `Display` implementation through a local constant.

Risks and test signals: Because all display tests include this first line, changes to wording or ANSI style can ripple across snapshots. Styling is isolated, making text semantics easy to preserve.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/error/display/error_title.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/error/display/mod.rs -->
# sources/security-integrity/cryfs/crates/check/src/error/display/mod.rs

Purpose: This module root exposes shared display utilities for concrete corruption errors.

Important APIs and flow: It declares `error_title`, `blob_error`, and `node_error` submodules and publicly reexports `ErrorTitle`, `BlobErrorDisplayMessage`, `ErrorDisplayBlobInfo`, `NodeErrorDisplayMessage`, and `ErrorDisplayNodeInfo`.

State and persistence: It has no state. It shapes the public-internal display API used by sibling error modules.

Dependencies and integration: Concrete error files import from `super::display` instead of reaching into individual display submodules.

Risks and test signals: This is a narrow facade. Renaming exports would affect every error `Display` implementation.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/error/display/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/error/display/node_error.rs -->
# sources/security-integrity/cryfs/crates/check/src/error/display/node_error.rs

Purpose: This module provides shared display formatting for node-related corruption errors, including how a node is referenced through a blob.

Important APIs and flow: `NodeErrorDisplayMessage` combines an `ErrorTitle` and `ErrorDisplayNodeInfo`. Formatting writes each `NodeAndBlobReference`, the node id, and observed node info. Helpers render root nodes, non-root inner nodes, non-root leaf nodes, reachable blob context, and unreachable blob context.

State and persistence: It owns no persistent state. It formats iterators over reference sets and value enums.

Dependencies and integration: It depends on `BlockId`, `BlobType`, `BlobReferenceWithId`, `MaybeBlobReferenceWithId`, `MaybeNodeInfoAsSeenByLookingAtNode`, and `NodeAndBlobReference`. All node error `Display` implementations use it.

Risks and test signals: Formatting is intentionally detailed and multi-line. Many node error tests assert exact ANSI-stripped output, so display changes require synchronized test updates. Reachable/unreachable blob context is important for diagnosing orphaned trees.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/error/display/node_error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/error/mod.rs -->
# sources/security-integrity/cryfs/crates/check/src/error/mod.rs

Purpose: This module collects all concrete corruption errors and defines the checker's non-corruption operational error type.

Important APIs and flow: `CorruptedError` is an enum with transparent variants for node unreadable, missing, unreferenced, referenced multiple times, blob referenced multiple times, blob unreadable, and wrong parent pointer. `CheckError` currently contains `FilesystemModified { msg }`, representing analysis failure caused by concurrent filesystem changes rather than persistent corruption.

State and persistence: `CorruptedError` values are immutable diagnostics returned to callers. `CheckError` is transient and aborts a checker run.

Dependencies and integration: The module reexports concrete error structs and is reexported by `lib.rs`. Checks add concrete errors into `CheckResult`, and the runner propagates `CheckError` where observations become inconsistent.

Risks and test signals: The TODO asks whether node and blob multiple-reference errors should be unified. The separation between corruption and check failure is important: `FilesystemModified` should not be counted as a found corruption.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/error/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/error/node_missing.rs -->
# sources/security-integrity/cryfs/crates/check/src/error/node_missing.rs

Purpose: This file defines the corruption error for a referenced node id that is absent from the blockstore.

Important APIs and flow: `NodeMissingError` stores `node_id` and `referenced_as: BTreeSet<NodeAndBlobReference>`. `new` asserts at least one reference. `Display` renders a `NodeErrorDisplayMessage` with node info `Missing`.

State and persistence: It is deterministic diagnostic data. References capture whether the missing node was a root node of a blob, an inner node, or a leaf node, and whether the owning blob is reachable or unreachable.

Dependencies and integration: It is emitted by `CheckUnreferencedNodes` and asserted by runner/blob checks when a missing blob root node is observed. It is included in `CorruptedError`.

Risks and test signals: Extensive unit tests cover missing nodes in unreachable blobs, file/dir/symlink root and child nodes, and multiple references. The constructor prevents semantically invalid "missing but unreferenced" errors.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/error/node_missing.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/error/node_referenced_multiple_times.rs -->
# sources/security-integrity/cryfs/crates/check/src/error/node_referenced_multiple_times.rs

Purpose: This file defines the corruption error for a data node id referenced from more than one parent or blob root.

Important APIs and flow: `NodeReferencedMultipleTimesError` stores `node_id`, `node_info: MaybeNodeInfoAsSeenByLookingAtNode`, and `referenced_as: BTreeSet<NodeAndBlobReference>`. `new` asserts at least two references. `Display` delegates to `NodeErrorDisplayMessage`.

State and persistence: It captures both observed node state and all incoming references. The `Maybe` node info allows duplicate references to missing or unreadable nodes to be reported with context.

Dependencies and integration: It is emitted by `CheckUnreferencedNodes` and asserted by the runner when its processed-node tracker sees a node id again with stable observed contents.

Risks and test signals: Tests cover missing, unreadable, inner, leaf, root-node references, reachable/unreachable owners, and many references. Because `BTreeSet` orders enum variants, display order is deterministic but tied to derived ordering.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/error/node_referenced_multiple_times.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/error/node_unreadable.rs -->
# sources/security-integrity/cryfs/crates/check/src/error/node_unreadable.rs

Purpose: This file defines the corruption error for a node block that exists in the enumerated store but cannot be read as a data node.

Important APIs and flow: `NodeUnreadableError` stores `node_id` and a possibly empty `referenced_as` set. `new` constructs the error, and `Display` renders node info `Unreadable` through the shared node display helper.

State and persistence: The error is immutable diagnostic state. Empty references are allowed for unreadable nodes found in unreachable scans with no readable parent references.

Dependencies and integration: It is emitted by `CheckUnreferencedNodes` and used in runner/check assertions. A TODO notes the underlying load error is not yet stored.

Risks and test signals: Tests cover unreferenced unreadable nodes, root references, inner/leaf references, reachable and unreachable owners, and many-reference formatting. Lack of root-cause error details can limit low-level repair guidance.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/error/node_unreadable.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/error/node_unreferenced.rs -->
# sources/security-integrity/cryfs/crates/check/src/error/node_unreferenced.rs

Purpose: This file defines the corruption error for an existing node that is not referenced by any other node or blob.

Important APIs and flow: `NodeUnreferencedError` stores `node_id` and `node_info: NodeInfoAsSeenByLookingAtNode`. `new` constructs the value, and `Display` renders no references plus the observed node info.

State and persistence: It is immutable diagnostic data for orphaned nodes discovered during the all-block scan and unreachable-node checker.

Dependencies and integration: It is emitted by `CheckUnreferencedNodes` finalization when a seen node has an empty reference set. It is part of `CorruptedError`.

Risks and test signals: Unit tests cover unreadable, inner, and leaf node display. In the reachable-node checker this error is treated as an invariant violation, because reachable traversal should never discover a child without also seeing the parent reference.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/error/node_unreferenced.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/error/wrong_parent_pointer.rs -->
# sources/security-integrity/cryfs/crates/check/src/error/wrong_parent_pointer.rs

Purpose: This file defines the corruption error for a readable blob whose stored parent pointer does not match any blob that references it.

Important APIs and flow: `WrongParentPointerError` stores `blob_id`, `blob_type`, `parent_pointer`, and all `referenced_as` paths. `Display` renders a blob display message with readable blob info containing the mismatched parent pointer.

State and persistence: The error captures observed blob metadata and incoming references. It is deterministic through `BTreeSet`.

Dependencies and integration: It is produced by `CheckParentPointers` during finalization and included in `CorruptedError`.

Risks and test signals: Tests cover file, dir, symlink, no references, and many references. The error message text has a minor grammar issue ("blobs parent pointer") but is consistently asserted. It does not yet assert entry type mismatches beyond parent pointer mismatch.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/error/wrong_parent_pointer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/lib.rs -->
# sources/security-integrity/cryfs/crates/check/src/lib.rs

Purpose: This is the library root for `cryfs-check`. It forbids unsafe code, declares internal modules, and reexports the public API used by the binary and tests.

Important APIs and flow: It exports `RecoverCli`, `check_filesystem`, concrete corruption errors, `CorruptedError`, and node/blob info/reference types. Internal modules include args, cli, checks, console, error, node_info, assertion, runner, and task_queue. It asserts Cargo version equals git version through `cryfs_version`.

State and persistence: The root owns no state. It controls API visibility and keeps runner/check internals private while exposing diagnostic data types.

Dependencies and integration: The binary imports `RecoverCli` from here. Integration tests import errors and reference model types from the crate to build exact expected results.

Risks and test signals: Public reexports make diagnostic type shapes part of the crate contract. The TODO for missing docs suggests API documentation is incomplete for external callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/node_info/blob_info_as_seen_by_looking_at_blob.rs -->
# sources/security-integrity/cryfs/crates/check/src/node_info/blob_info_as_seen_by_looking_at_blob.rs

Purpose: This enum describes what was observed when a blob was loaded directly.

Important APIs and flow: `BlobInfoAsSeenByLookingAtBlob` has `Unreadable` and `Readable { blob_type, parent_pointer }`. It derives equality, ordering, hashing, clone, copy, and debug traits.

State and persistence: It is value-only diagnostic state used while classifying blob observations and building errors.

Dependencies and integration: It depends on `BlobId` and fsblobstore `BlobType`. It converts into the `MaybeBlobInfoAsSeenByLookingAtBlob` superset in a sibling module.

Risks and test signals: It cannot represent missing blobs; callers use the `Maybe` wrapper when missing is possible.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/node_info/blob_info_as_seen_by_looking_at_blob.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/node_info/blob_reference.rs -->
# sources/security-integrity/cryfs/crates/check/src/node_info/blob_reference.rs

Purpose: `BlobReference` records how a blob is referenced by a parent directory entry.

Important APIs and flow: The struct contains `blob_type`, `parent_id`, and absolute `path`. `root_dir()` constructs the synthetic root reference as a directory with zero parent id and root path.

State and persistence: It is immutable reference context used in checker state, errors, and display output.

Dependencies and integration: It depends on `BlobId`, `BlobType`, and `AbsolutePathBuf`. It is embedded in `BlobReferenceWithId`, `MaybeBlobReferenceWithId`, blob errors, and parent-pointer checks.

Risks and test signals: Root uses `BlobId::zero()` as a sentinel parent, so consumers must understand that root's parent is synthetic.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/node_info/blob_reference.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/node_info/blob_reference_with_id.rs -->
# sources/security-integrity/cryfs/crates/check/src/node_info/blob_reference_with_id.rs

Purpose: This struct combines a concrete `BlobId` with the path/type/parent context represented by `BlobReference`.

Important APIs and flow: `BlobReferenceWithId` contains `blob_id` and `referenced_as`. Its `Display` renders type, path, blob id, and parent blob id; `Debug` wraps that display text.

State and persistence: It is diagnostic/reference state passed through the runner for reachable blobs and used in errors.

Dependencies and integration: It depends on `BlobId`, `BlobType`, and `BlobReference`. It appears in node references, root-node diagnostics, and conversion into `MaybeBlobReferenceWithId`.

Risks and test signals: Unit tests cover file, dir, and symlink display with ANSI stripping. Formatting is compact and used in debug messages such as runner logs.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/node_info/blob_reference_with_id.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/node_info/maybe_blob_info_as_seen_by_looking_at_blob.rs -->
# sources/security-integrity/cryfs/crates/check/src/node_info/maybe_blob_info_as_seen_by_looking_at_blob.rs

Purpose: This enum extends blob observation info with a `Missing` state for diagnostics where the blob could not be found.

Important APIs and flow: Variants are `Missing`, `Unreadable`, and `Readable { blob_type, parent_pointer }`. The `From<BlobInfoAsSeenByLookingAtBlob>` implementation maps unreadable/readable observations into the superset.

State and persistence: It is immutable error context, commonly used by blob multiple-reference diagnostics and display helpers.

Dependencies and integration: It depends on `BlobId`, `BlobType`, and `BlobInfoAsSeenByLookingAtBlob`.

Risks and test signals: The enum captures high-level load state but not root-cause errors or child lists. That keeps diagnostics compact but may omit repair clues.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/node_info/maybe_blob_info_as_seen_by_looking_at_blob.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/node_info/maybe_blob_reference_with_id.rs -->
# sources/security-integrity/cryfs/crates/check/src/node_info/maybe_blob_reference_with_id.rs

Purpose: This enum records whether a node's owning blob is reachable from the filesystem root.

Important APIs and flow: Variants are `UnreachableFromFilesystemRoot` and `ReachableFromFilesystemRoot { blob_id, referenced_as }`. It implements `From<BlobReferenceWithId>` for reachable context.

State and persistence: It is reference context for node errors, especially orphaned or dangling subtrees discovered outside the root traversal.

Dependencies and integration: It depends on `BlobId`, `BlobReferenceWithId`, and `BlobReference`. `NodeAndBlobReference` uses it for non-root nodes.

Risks and test signals: Unreachable context intentionally lacks a blob id/path, so diagnostics for orphaned child nodes can be less specific than reachable nodes.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/node_info/maybe_blob_reference_with_id.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/node_info/maybe_node_info_as_seen_by_looking_at_node.rs -->
# sources/security-integrity/cryfs/crates/check/src/node_info/maybe_node_info_as_seen_by_looking_at_node.rs

Purpose: This enum extends direct node observation info with a `Missing` state for diagnostics.

Important APIs and flow: Variants are `Missing`, `Unreadable`, `InnerNode { depth }`, and `LeafNode`. `From<NodeInfoAsSeenByLookingAtNode>` maps observed unreadable/inner/leaf values into this superset.

State and persistence: It is immutable diagnostic state included in node errors where the node may be missing.

Dependencies and integration: It depends on `NonZeroU8` and `NodeInfoAsSeenByLookingAtNode`. Display helpers use it to render node info text.

Risks and test signals: Inner-node depth is preserved, but child ids are not included in final diagnostics.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/node_info/maybe_node_info_as_seen_by_looking_at_node.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/node_info/mod.rs -->
# sources/security-integrity/cryfs/crates/check/src/node_info/mod.rs

Purpose: This module root defines the public facade for checker node/blob reference and observation types.

Important APIs and flow: It declares and reexports blob observation, maybe blob observation, blob reference, blob reference with id, maybe blob reference with id, node observation, maybe node observation, node reference, combined node/blob reference, and reachable combined reference modules.

State and persistence: It owns no state. It organizes value types that carry checker traversal context into errors and public APIs.

Dependencies and integration: `lib.rs` reexports these types for tests and callers. The runner, checks, display helpers, and error types all import through this module.

Risks and test signals: These reexports form a stable type vocabulary for expected test errors. Changes to variant names or structure would have broad impact across integration tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/node_info/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/node_info/node_and_blob_reference.rs -->
# sources/security-integrity/cryfs/crates/check/src/node_info/node_and_blob_reference.rs

Purpose: `NodeAndBlobReference` describes how a node is referenced, including the blob context that owns the data tree.

Important APIs and flow: Variants represent root nodes with `BlobReferenceWithId`, non-root inner nodes with maybe-reachable blob context, depth, and parent node id, and non-root leaf nodes with maybe-reachable blob context and parent id. `blob_info(self)` extracts owning blob context. `node_info(&self)` extracts `NodeReference`. The `From<NodeAndBlobReferenceFromReachableBlob>` implementation converts reachable traversal context into the general diagnostic enum.

State and persistence: It is immutable reference metadata stored in error sets and reference checkers.

Dependencies and integration: It depends on `BlockId`, `NonZeroU8`, `BlobReferenceWithId`, `MaybeBlobReferenceWithId`, `NodeReference`, and `NodeAndBlobReferenceFromReachableBlob`. Display helpers render each variant.

Risks and test signals: `blob_info(self)` consumes self, which is appropriate for conversion but requires cloning in callers that need to retain the full value. Unit tests verify conversion preserves both node and blob info.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/node_info/node_and_blob_reference.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/node_info/node_and_blob_reference_from_reachable_blob.rs -->
# sources/security-integrity/cryfs/crates/check/src/node_info/node_and_blob_reference_from_reachable_blob.rs

Purpose: This struct carries node reference context while traversing nodes of a blob known to be reachable from the filesystem root.

Important APIs and flow: It contains `node_info: NodeReference` and `blob_info: BlobReferenceWithId`.

State and persistence: It is transient traversal state passed through runner recursion and converted into `NodeAndBlobReference` for diagnostic storage.

Dependencies and integration: It is used by `RecoverRunner`, `CheckUnreferencedNodes`, and `CheckParentPointers` callback signatures through `FilesystemCheck`.

Risks and test signals: The type assumes root reachability. Unreachable-node scans use `MaybeBlobReferenceWithId::UnreachableFromFilesystemRoot` instead of this type.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/node_info/node_and_blob_reference_from_reachable_blob.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/node_info/node_info_as_seen_by_looking_at_node.rs -->
# sources/security-integrity/cryfs/crates/check/src/node_info/node_info_as_seen_by_looking_at_node.rs

Purpose: This enum describes what was observed when loading a node directly.

Important APIs and flow: Variants are `Unreadable`, `InnerNode { depth: NonZeroU8 }`, and `LeafNode`.

State and persistence: It is value-only diagnostic state used by node checks and `NodeUnreferencedError`.

Dependencies and integration: It depends on `NonZeroU8` for inner depths. It converts into `MaybeNodeInfoAsSeenByLookingAtNode` in a sibling module.

Risks and test signals: It cannot represent missing nodes; callers use the `Maybe` wrapper when absence is possible.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/node_info/node_info_as_seen_by_looking_at_node.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/node_info/node_reference.rs -->
# sources/security-integrity/cryfs/crates/check/src/node_info/node_reference.rs

Purpose: `NodeReference` records how a node is expected to look based on the parent reference that points to it.

Important APIs and flow: Variants are `RootNode`, `NonRootInnerNode { depth, parent_id }`, and `NonRootLeafNode { parent_id }`.

State and persistence: It is traversal/reference metadata, not direct observed node state. The runner derives it when descending data-node trees.

Dependencies and integration: It depends on `BlockId` and `NonZeroU8`, and is embedded in `NodeAndBlobReferenceFromReachableBlob`.

Risks and test signals: Correct depth computation is critical; the runner computes child depth by subtracting one and treating zero as leaf.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/node_info/node_reference.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/runner.rs -->
# sources/security-integrity/cryfs/crates/check/src/runner.rs

Purpose: This file implements the core filesystem checking traversal. `RecoverRunner` is a `BlockstoreCallback` that receives the configured blockstore stack, enumerates all blocks, traverses reachable blobs and nodes, checks unreachable nodes, finalizes all checks, and returns `Vec<CorruptedError>`.

Important APIs and flow: `callback` parses the root blob id from config, lists all node ids via `all_blocks`, creates `AllChecks`, builds an `FsBlobStore` over `BlobStoreOnBlocks`, calls `check_all_reachable_blobs`, then unwraps to `DataNodeStore` and calls `check_all_nodes_of_reachable_blobs`. Finally it removes processed reachable nodes from the all-node set and calls `check_all_unreachable_nodes`. Each phase uses progress bars/spinners and explicit async drops on error or completion.

Traversal details: Reachable blob traversal starts at the root `BlobReferenceWithId` and recursively spawns child blob checks for directory entries through `task_queue::run_to_completion(MAX_CONCURRENCY)`. `ProcessedItems` detects repeated blob ids; if repeated observations differ, the run aborts with `FilesystemModified`, otherwise duplicate-reference assertions are added. Node traversal similarly spawns child data-node tasks from inner nodes, tracks repeated node ids, and asserts duplicate-node diagnostics.

State and persistence: Runtime state is in-memory: `HashSet<BlockId>` for initial block ids, `ProcessedItems` mutex maps for blobs and nodes, `SeenBlobInfo` and `SeenNodeInfo` summaries, and `AllChecks`. The blockstore is wrapped by higher layers outside this file and explicitly dropped asynchronously. No repair or write-back occurs.

Dependencies and integration: The runner integrates blockstore, blobstore, fsblobstore, config, progress UI, async-drop, task queue, and all check modules. It relies on `AllowIntegrityViolations` setup in `cli.rs` so corrupt blocks can be observed and reported rather than aborting too early.

Risks and test signals: TODOs identify function size, concurrency tuning, duplicate code between seen branches, missing blob type checks, possible double-loading of directory nodes, and progress-bar length accuracy. The runner treats mid-run appearance/disappearance or changed summaries as `FilesystemModified`; users must keep vaults unmounted and stable during checks. `MAX_CONCURRENCY` is fixed at 100.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/runner.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/task_queue.rs -->
# sources/security-integrity/cryfs/crates/check/src/task_queue.rs

Purpose: This module provides a small recursive async task queue with bounded concurrent execution. The runner uses it to traverse blob and node trees while allowing tasks to spawn children.

Important APIs and flow: `run_to_completion(max_concurrency, initial_task)` creates an unbounded channel of boxed futures, spawns the initial task, wraps the receiver as a stream, and runs futures with `buffer_unordered(max_concurrency)` until the sender graph drains or an error occurs. `TaskSpawner::spawn` passes a cloned spawner into each future factory and sends the boxed future.

State and persistence: Queue state is in-memory channel state. It has no persistence and no cancellation ledger beyond stream error propagation.

Dependencies and integration: It uses `futures`, `tokio::sync::mpsc::unbounded_channel`, and `tokio_stream::wrappers::UnboundedReceiverStream`. `RecoverRunner` uses it for recursive traversal with `CheckError` or `anyhow::Error` style errors.

Risks and test signals: The channel is unbounded, so very broad trees can enqueue many futures even though execution is bounded. Tests cover spawning 100 direct tasks, 100 recursive tasks, and propagation of an error from a recursive task.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/src/task_queue.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/tests/blob_missing.rs -->
# sources/security-integrity/cryfs/crates/check/tests/blob_missing.rs

Purpose: This integration test verifies that removing whole blobs causes `cryfs-check` to report the missing blob root node and any orphaned descendants correctly.

Important APIs and flow: The parameterized `blob_entirely_missing` test selects file, directory with children, empty directory, symlink, or rootdir-with-children blobs from `SomeBlobs`. It records descendant blobs if the selected blob is a directory, removes the blob by id through `update_fsblobstore`, builds expected `NodeMissingError` plus expected unreferenced-root-node errors for orphaned descendants, runs `run_cryfs_check`, and compares unordered errors. A second test removes an otherwise childless root dir and expects one root `NodeMissingError`.

State and persistence: Tests mutate a temporary filesystem fixture by removing blobs from the fsblobstore, then run the checker over the persisted corrupted state.

Dependencies and integration: It uses `rstest`, `FilesystemFixture`, `SomeBlobs`, entry helper expectations, `RemoveResult`, `BlobReference`, `BlobReferenceWithId`, `NodeAndBlobReference`, and `NodeMissingError`.

Risks and test signals: The tests establish that a missing blob is modeled as a missing root data node (`blob_id.to_root_block_id()`). The file notes that combined blob-missing and referenced-multiple-times coverage lives in the blob referenced multiple times test module.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/tests/blob_missing.rs -->
