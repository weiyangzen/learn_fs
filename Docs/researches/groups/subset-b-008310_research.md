# Research: subset-b-008310

This grouped report covers the CryFS check-test fixtures and CLI utility crate files requested for `subset-b-008310`. Each section is source-tree-aligned and wrapped for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/tests/blob_referenced_multiple_times.rs -->
## sources/security-integrity/cryfs/crates/check/tests/blob_referenced_multiple_times.rs

Purpose: parameterized integration tests for blobs referenced by more than one directory entry. They verify both `BlobReferencedMultipleTimesError` and the corresponding root-node `NodeReferencedMultipleTimesError`, including cases where the duplicated blob is readable, unreadable, or missing.

Important APIs and helpers: local `make_file`, `make_dir`, and `make_symlink` create an initial blob in a chosen parent. `add_as_file_entry`, `add_as_dir_entry`, and `add_as_symlink_entry` add a second directory entry to the same blob id while declaring a potentially different entry type. `same_dir` and `different_dirs` parameterize whether duplicate references originate from one directory or two. `BlobStatus` selects normal, corrupted-root, or removed-blob setup.

Control flow and state: the test builds `FilesystemFixture::new_with_some_blobs`, creates one blob, records the root-node depth, adds a second reference, optionally corrupts or removes the blob, constructs expected `BTreeSet` reference sets, runs `run_cryfs_check`, and compares errors unordered. State persists in the in-memory encrypted blockstore through real fsblobstore directory-entry mutations.

Dependencies and integration: depends on `rstest`, `tokio`, `cryfs_check` error types, `BlobId`, `BlobType`, and common fixture APIs. It directly exercises the checker’s cross-index between directory blob references and data-tree root-node references.

Risks and test signals: TODOs document missing cycle-like directory-reference cases and mixed blob/node references. The test signal is strong for duplicate root-node reporting, including the important edge where unreadable or missing blobs still carry multiple logical references.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/tests/blob_referenced_multiple_times.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/tests/blob_unreadable.rs -->
## sources/security-integrity/cryfs/crates/check/tests/blob_unreadable.rs

Purpose: tests blob-level unreadability when individual nodes may still be readable, focusing on corrupt serialized blob metadata rather than missing/corrupted data-tree blocks.

Important APIs and functions: `unreadable_blob_bad_format_version` increments the blob format version via the fixture. `unreadable_file_blob_bad_blob_type` writes an invalid blob type byte. Both are parameterized over file, directory, symlink, and root directory blobs selected from `SomeBlobs`.

Control flow and state: each test creates a populated fixture, collects descendant blobs if the target is a directory, derives expected `NodeUnreferencedError`s for descendants that become unreachable when the directory cannot be decoded, mutates the raw blob header, runs `cryfs_check`, and asserts unordered equality against `BlobUnreadableError` plus descendant-root unreferenced errors.

Dependencies and integration: uses `BlobUnreadableError`, `CorruptedError`, `BlobReferenceWithId`, common `expect_blobs_to_have_unreferenced_root_nodes`, and fixture mutation methods. It integrates with fsblobstore deserialization semantics: bad format version or type makes the blob unreadable even when block integrity succeeds.

Risks and test signals: the tests confirm directory traversal cutoff behavior but do not inspect the precise low-level decode error. The final comment points to `blob_referenced_multiple_times` for unreadable blobs with duplicate references, avoiding duplicated coverage.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/tests/blob_unreadable.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/tests/blob_unreferenced.rs -->
## sources/security-integrity/cryfs/crates/check/tests/blob_unreferenced.rs

Purpose: constructs blobs that exist in the blockstore but have no directory-entry reference from the filesystem root, then verifies that their root data nodes are reported as unreferenced.

Important APIs and functions: `make_single_node_file_blob`, `make_large_file_blob`, `make_single_node_dir_blob`, `make_large_dir_blob`, `make_single_node_symlink_blob`, and `make_large_symlink_blob` create orphan blobs of all blob types and sizes. `make_dir_blob_with_children` creates an unreferenced directory with child entries. Local `parent_id`, `blob_id`, and `data` generate deterministic ids and payloads.

Control flow and state: helper functions use `update_fsblobstore` to create blobs with a fake parent id that is never linked into the root tree. Large helpers write enough data or entries to force multi-node data trees and compute expected root `NodeInfoAsSeenByLookingAtNode` via `DataTree::into_root_node`. The directory-with-children case also gathers descendant blob ids and expects their root nodes to be unreferenced.

Dependencies and integration: uses low-level `BlobOnBlocks`, `DataTree`, `FsBlob::into_raw`, fsblobstore creation APIs, UID/GID/mode metadata, and common descendant expectation helpers. It validates that the checker’s reachability phase starts from root directory references, not from the blobstore inventory alone.

Risks and test signals: coverage spans file, directory, and symlink root-node shapes, including single-leaf and inner-root trees. The risk is sensitivity to constants that force large-node fanout; assertions fail loudly if fixture sizes stop producing enough nodes.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/tests/blob_unreferenced.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/tests/blob_with_wrong_parent_pointer.rs -->
## sources/security-integrity/cryfs/crates/check/tests/blob_with_wrong_parent_pointer.rs

Purpose: validates detection of blobs whose stored parent pointer disagrees with the directory entries that reference them. It also checks interaction with multiple references.

Important APIs and functions: `make_file`, `make_symlink`, `make_empty_dir`, and `make_large_dir` create target blobs and parent directories. `set_parent` loads a blob through `FsBlobStore` and calls `set_parent` to change its embedded parent id. Three tests cover one, two, and four directory references.

Control flow and state: each test creates old parent(s), creates a blob under one old parent, creates an unrelated new parent, mutates the blob parent pointer to the new parent, and expects `WrongParentPointerError`. Multi-reference tests also expect `NodeReferencedMultipleTimesError` for the root node and `BlobReferencedMultipleTimesError` with readable blob info carrying the wrong parent pointer.

Dependencies and integration: integrates directory-entry metadata (`BlobReference` path, parent id, declared `BlobType`) with blob-internal parent pointers. It depends on `NonZeroU8` depth conversion for root-node info and `BTreeSet` to make reference order irrelevant.

Risks and test signals: it is strong for parent-pointer mismatch plus duplicate-reference composition. It intentionally creates references with file, dir, and symlink entry types, testing that the checker reports what the directory says and what the blob header says rather than silently normalizing inconsistencies.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/tests/blob_with_wrong_parent_pointer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/tests/common/console.rs -->
## sources/security-integrity/cryfs/crates/check/tests/common/console.rs

Purpose: provides a deterministic `Console` implementation used only while creating fixture config. It avoids interactive prompts and supplies fixed cryptographic/filesystem parameters.

Important APIs and functions: `FixtureCreationConsole` implements `cryfs_config::config::Console`. Only three methods are expected to be used: `ask_scrypt_settings_for_new_filesystem` returns `ScryptSettings::TEST`, `ask_cipher_for_new_filesystem` returns `aes-256-gcm`, and `ask_blocksize_bytes_for_new_filesystem` returns 104 bytes. Migration, replacement, key-change, single-client, and path-creation prompts panic as unused.

Control flow and state: there is no persistent state. The fixture’s config creation calls this console to obtain repeatable values; every unexpected prompt fails the test immediately.

Dependencies and integration: depends on `anyhow`, `byte_unit::Byte`, `cryfs_crypto::kdf::scrypt`, and `cryfs_version` types required by the `Console` trait. It integrates with `FixtureTempDir::create_config` in `fixture.rs`.

Risks and test signals: the tiny block size is deliberate because corruption tests need many nodes from moderate test payloads. Panicking unused prompts are a useful guard: if config creation starts requiring new user decisions, tests fail rather than silently accepting defaults.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/tests/common/console.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/tests/common/entry_helpers.rs -->
## sources/security-integrity/cryfs/crates/check/tests/common/entry_helpers.rs

Purpose: shared fixture utilities for creating filesystem blobs, forcing multi-node data trees, selecting deterministic nodes, traversing descendants, and constructing expected checker errors.

Important APIs and types: `CreatedDirBlob`, `CreatedFileBlob`, and `CreatedSymlinkBlob` wrap `AsyncDropGuard<FsBlob<B>>` with path metadata and convert into `BlobReferenceWithId`. Creation helpers include `create_empty_dir`, `create_empty_file`, `create_symlink`, `create_large_file`, `create_large_symlink`, `create_large_dir`, and `create_large_dir_with_large_entries`. `SomeBlobs` captures a reusable graph of nested directories, large files, large symlinks, and empty blobs. Node search helpers include `find_leaf_node_*`, `find_inner_node_*`, and large/small blob shortcuts. Expectation helpers build `NodeUnreferencedError`s from live node ids.

Control flow and state: helpers mutate parent directory blobs by adding entries, write deterministic test data, recursively create deep/large structures, and explicitly async-drop guards to flush changes. Random node selection uses `SmallRng::seed_from_u64(0)` to keep tests reproducible.

Dependencies and integration: bridges `cryfs_blobstore`, `cryfs_blockstore`, `cryfs_fsblobstore`, `cryfs_check`, and `cryfs_utils`. It is the central integration layer between high-level test scenarios and low-level node/block operations.

Risks and test signals: assumptions about node depth/fanout are enforced with asserts that explain fixture-size adjustments. Recursive descendant streams can expose cycles or unreadable directories if corruption creates pathological references, so tests using them must account for traversal cutoff errors.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/tests/common/entry_helpers.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/tests/common/fixture.rs -->
## sources/security-integrity/cryfs/crates/check/tests/common/fixture.rs

Purpose: end-to-end filesystem fixture for `cryfs_check` integration tests. It creates a real CryFS config, encrypted/integrity/locking blockstore stack over an in-memory blockstore, a root directory blob, and focused APIs for corrupting or removing blobs and nodes.

Important APIs and types: `FilesystemFixture` owns root blob id, shared blockstore, loaded config, and tempdir. Constructors are `new` and `new_with_some_blobs`. Store accessors include `update_blockstore`, `update_nodestore`, `update_blobstore`, and `update_fsblobstore`. Mutation helpers corrupt blocks, blob header fields, parent pointers, root/inner/leaf nodes, and multi-node subtrees. Result structs (`RemoveInnerNodeResult`, `CorruptInnerNodeResult`, `RemoveLeafNodeResult`, `CorruptLeafNodeResult`, `RemoveSomeNodesResult`, `CorruptSomeNodesResult`) carry expected-reference metadata.

Control flow and state: `new` creates temp config with fixed password, initializes root dir, and all later updates reopen the relevant store stack through `setup_blockstore_stack_dyn`. `run_cryfs_check(self)` consumes the fixture and calls `cryfs_check::check_filesystem`, preserving the shared blockstore but letting tempdir live until after the check.

Dependencies and integration: integrates `cryfs_cli_utils` blockstore setup, config/local state, blockstore integrity settings, fsblobstore, blobstore, nodestore, and common entry helpers.

Risks and test signals: corruption helpers intentionally violate integrity and graph invariants while preserving enough metadata to assert exact checker errors. The fixture panics on unexpected integrity violations in normal setup, so tests distinguish fixture failures from checker findings.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/tests/common/fixture.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/tests/common/mod.rs -->
## sources/security-integrity/cryfs/crates/check/tests/common/mod.rs

Purpose: declares the shared test-support modules for the check integration tests.

Important APIs and functions: it exports `console`, `entry_helpers`, and `fixture` as public submodules. The crate-level `#![allow(dead_code)]` is intentional because parameterized test files consume different subsets of the shared helpers.

Control flow and state: no runtime logic or persistence exists here; it is compile-time module wiring for integration-test crates that declare `mod common`.

Dependencies and integration: each test file imports this module to access `FilesystemFixture`, `SomeBlobs`, blob creation helpers, and error expectation helpers. It centralizes common code without requiring a separate test-support crate.

Risks and test signals: dead-code allowance can hide truly stale helpers, but in this context it avoids noisy warnings from a deliberately broad fixture toolkit. Any missing module declaration would surface immediately as integration test compile failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/tests/common/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/tests/node_missing.rs -->
## sources/security-integrity/cryfs/crates/check/tests/node_missing.rs

Purpose: validates `NodeMissingError` reporting when data-tree nodes referenced by readable structures are removed from the nodestore.

Important APIs and functions: tests cover missing root nodes, inner nodes, leaf nodes, and multiple removed nodes. They use fixture removal methods (`remove_root_node_of_blob`, `remove_an_inner_node_of_a_large_blob`, `remove_a_leaf_node`, `remove_some_nodes_of_a_large_blob`) and common expectation helpers for orphaned nodes/blobs.

Control flow and state: each test creates a populated fixture, selects file/dir/symlink/root blobs, expands the root directory when necessary to ensure large enough depth, collects directory descendants before corruption, removes target nodes, derives expected missing and unreferenced errors, runs `cryfs_check`, and asserts unordered equality.

Dependencies and integration: depends on `BlobType` to add `BlobUnreadableError` expectations for directory blobs whose data cannot be decoded after node loss. It integrates checker traversal semantics with nodestore-level deletion.

Risks and test signals: the tests make a clear distinction between nodes directly referenced by still-reachable parents (`NodeMissing`) and children orphaned by removing an ancestor (`NodeUnreferenced`). A TODO notes missing coverage for `NodeMissing` with multiple references.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/tests/node_missing.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/tests/node_referenced_multiple_times.rs -->
## sources/security-integrity/cryfs/crates/check/tests/node_referenced_multiple_times.rs

Purpose: tests data-tree nodes referenced from multiple parents, including leaf nodes, non-root inner nodes, and blob root nodes referenced as children inside other blobs.

Important APIs and functions: helper mutations replace a child pointer in one parent with an existing node from another tree: `remove_leaf_and_replace_in_parent_with_another_existing_leaf`, `remove_inner_node_and_replace_in_parent_with_another_existing_inner_node`, and `remove_inner_node_and_replace_in_parent_with_root_node`. The `rstest_reuse` template parameterizes source/target blob combinations across file, directory, and symlink blobs.

Control flow and state: helpers select deterministic nodes, update a parent’s child pointer, remove the original subtree to avoid unrelated duplicate/missing noise, and return parent ids for expected references. Tests run the checker, filter a documented set of acceptable flakiness-caused errors from potentially unreadable modified directory blobs, and assert the exact `NodeReferencedMultipleTimesError`.

Dependencies and integration: uses low-level `BlockId` operations, `RemoveResult`, node search helpers, `MaybeBlobReferenceWithId`, and checker reference enums. It stress-tests the checker’s ability to attribute duplicate data nodes to different reachable blobs and depths.

Risks and test signals: comments document disabled cases involving self-referential directories, child/parent directory references, and a flaky directory case where blob ids may still decode. The existing tests still cover core duplicate-node detection across different blob types and root/non-root roles.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/tests/node_referenced_multiple_times.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/tests/node_unreadable.rs -->
## sources/security-integrity/cryfs/crates/check/tests/node_unreadable.rs

Purpose: verifies `NodeUnreadableError` reporting when node blocks exist but fail to decode or pass integrity, and validates secondary effects on blob readability and descendant reachability.

Important APIs and functions: tests cover unreadable single-node blobs, root directory single-node without children, unreadable root nodes, unreadable inner nodes, unreadable leaf nodes, and multiple corrupted nodes. They use fixture corruption methods that flip bytes in stored blocks while preserving expected reference metadata.

Control flow and state: each test prepares a blob, records descendant blobs when target is a directory, corrupts selected node blocks, builds expected `NodeUnreadableError`s plus `BlobUnreadableError` for affected blobs and `NodeUnreferencedError`s for orphaned children, runs the checker, and compares unordered.

Dependencies and integration: depends on `BlobReference`, `BlobReferenceWithId`, `BlobUnreadableError`, `NodeUnreadableError`, `BlobType`, and common helpers. It exercises the blockstore integrity layer through actual encrypted block corruption rather than mocking decode failures.

Risks and test signals: directory blobs produce extra unreadable blob errors because checker traversal attempts to decode them as filesystem directories. The multi-corruption case is a strong signal for de-duplicating references and handling unreachable child references after corrupted ancestors.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/tests/node_unreadable.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/tests/node_unreferenced.rs -->
## sources/security-integrity/cryfs/crates/check/tests/node_unreferenced.rs

Purpose: validates reporting of nodes that exist in the nodestore but are not reachable from any blob rooted at the filesystem root.

Important APIs and functions: `leaf_node_unreferenced` creates an orphan leaf with empty data. `single_inner_node_unreferenced` creates an orphan inner node that references two nonexistent child ids. `inner_node_with_subtree_unreferenced` creates a complete orphan subtree of leaves and inner nodes.

Control flow and state: tests use `update_nodestore` to create raw data nodes outside any blob. Expected errors include `NodeUnreferencedError` for the orphan root node. The single-inner case also expects `NodeMissingError` for its fake child pointers because an unreferenced inner node is still inspected and its children are missing. The complete-subtree case expects only the top unreferenced root because descendants are reachable from that orphan subtree.

Dependencies and integration: depends on `BlockId`, `Data`, `DataFixture`, `NodeInfoAsSeenByLookingAtNode`, `NodeAndBlobReference`, and `MaybeBlobReferenceWithId::UnreachableFromFilesystemRoot`.

Risks and test signals: this file probes checker behavior beyond filesystem-root traversal by requiring inventory scanning of all stored nodes. It clarifies that unreachable subtrees are summarized at their orphan root when internally consistent.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/tests/node_unreferenced.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/tests/valid.rs -->
## sources/security-integrity/cryfs/crates/check/tests/valid.rs

Purpose: baseline tests asserting that healthy fixture filesystems produce no corruption errors.

Important APIs and functions: `fs_with_only_root_dir` uses `FilesystemFixture::new`. `fs_with_some_files_and_directories_and_symlinks` uses `FilesystemFixture::new_with_some_blobs`. Both call `run_cryfs_check` and compare against an empty `Vec<CorruptedError>`.

Control flow and state: these tests create valid encrypted in-memory filesystems, do not mutate them after construction, run the same checker path as corruption tests, and assert exact emptiness.

Dependencies and integration: depends only on common fixture and `cryfs_check::CorruptedError`, making it the sanity check for the entire fixture stack.

Risks and test signals: if these fail, corruption-test failures are hard to interpret because the fixture or blockstore setup itself may be invalid. They provide the clean control group for all subsequent negative tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/check/tests/valid.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cli-utils/Cargo.toml -->
## sources/security-integrity/cryfs/crates/cli-utils/Cargo.toml

Purpose: package manifest for shared command-line utility code used by CryFS executables such as `cryfs` and `cryfs-check`.

Important declarations: package metadata is inherited from the workspace. Dependencies include `clap` with derive support, `clap-logflag`, `human-panic`, `rpassword`, `path-absolutize`, `dirs`, and internal crates `cryfs-config`, `cryfs-blockstore`, `cryfs-version`, `cryfs-utils`, and `cryfs-crypto`. `reqwest` and `serde_json` are optional. The default feature enables `check_for_updates`, which activates those optional network/JSON dependencies.

Control flow and state: no runtime logic exists in the manifest, but feature selection changes whether version display performs HTTP update checks and whether environment variables such as `CRYFS_NO_UPDATE_CHECK` are compiled in.

Dependencies and integration: dev dependencies include CLI assertion, environment mutation, temp project, and test utility crates. This manifest is the dependency boundary for the fixture in `check/tests/common/fixture.rs`, which uses `setup_blockstore_stack_dyn`.

Risks and test signals: default network-update behavior adds privacy and reliability considerations for CLI startup, mitigated by environment/noninteractive checks in code. Version synchronization is guarded in `lib.rs` by a cargo/git version assertion.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cli-utils/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cli-utils/src/application.rs -->
## sources/security-integrity/cryfs/crates/cli-utils/src/application.rs

Purpose: generic CLI runner for CryFS binaries. It coordinates panic handling, environment reading, argument parsing, logging initialization, version/update output, application construction, main execution, and process exit-code mapping.

Important APIs and types: `Application` trait defines `ConcreteArgs`, `NAME`, `VERSION`, `new`, `default_log_config`, `should_show_version`, `defer_logging_init`, and `main`. `run<App>() -> ExitCode` wraps `_run<App>()` and prints `CliError`s. `DEFAULT_LOG_LEVEL` is `Info`. `show_backtrace_on_panic` configures debug backtraces or release `human_panic`.

Control flow and state: `_run` sets panic behavior, reads `Environment`, builds a version-display closure, parses args, handles `--version`, normal app startup, clap exits, and non-clap parse errors. Logging is initialized unless deferred; version output occurs before `main` unless disabled by the app.

Dependencies and integration: depends on `clap`, `clap_logflag`, `cryfs_version`, `human_panic`, environment and error modules, and optional update-check HTTP client. Downstream binaries implement `Application`.

Risks and test signals: clap errors call `err.exit()`, so that branch never returns normally. Version output to stderr can happen before logging initialization. Daemon-style apps can suppress banners and defer logging, which reduces accidental TTY output but shifts responsibility to the application.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cli-utils/src/application.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cli-utils/src/args.rs -->
## sources/security-integrity/cryfs/crates/cli-utils/src/args.rs

Purpose: shared clap argument parsing with special handling for `--version` as an immediate-exit flag that should work even when concrete application args are absent.

Important APIs and types: `ImmediateExitFlags` contains `version`. `CombinedArgs<ConcreteArgs>` flattens immediate flags, concrete args, and `LogArgs`. `ParseArgsResult` distinguishes `ShowVersion` from normal parsed args. `ArgParseError` separates clap display/parse errors from custom `CliError`s.

Control flow and state: `parse_args` first tries to parse only immediate flags. If `--version` is present alone, it returns `ShowVersion`. Help errors are re-parsed against full args so clap can produce full help. Unknown arguments trigger full parse and a custom invalid-argument error if `--version` was combined with normal arguments.

Dependencies and integration: uses `clap` derive/builders, `clap_logflag`, and `CliErrorKind::InvalidArguments`. `clap_style` customizes help colors.

Risks and test signals: parsing depends on clap error-kind behavior; TODOs note unreachable-looking branches. The important security/usability signal is rejecting `--version` mixed with operational arguments so immediate-exit behavior cannot be ambiguous.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cli-utils/src/args.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cli-utils/src/blockstore_setup.rs -->
## sources/security-integrity/cryfs/crates/cli-utils/src/blockstore_setup.rs

Purpose: builds the CryFS blockstore stack around a low-level blockstore using config-selected encryption and integrity settings.

Important APIs and types: `BlockstoreCallback` abstracts work performed after stack construction. `setup_blockstore_stack` performs cipher lookup, key parsing, `EncryptedBlockStore` creation, `IntegrityBlockStore` initialization, and wrapping in `LockingBlockStore`. `setup_blockstore_stack_dyn` returns a dynamic `LockingBlockStore<DynBlockStore>` using `DynCallback`.

Control flow and state: cipher lookup invokes `CipherCallbackForBlockstoreSetup`. The callback parses the hex encryption key, constructs the cipher, computes the local integrity state path under the filesystem id, initializes integrity storage with `my_client_id` and `IntegrityConfig`, then calls the user callback. On key/cipher/local-state errors, it async-drops partially built stores before returning a mapped `CliError`.

Dependencies and integration: integrates `cryfs_config` ciphers and `CryConfig`, `cryfs_crypto` key/cipher types, `cryfs_blockstore` encrypted/integrity/locking layers, local state, and CLI error mapping. The check fixture uses `setup_blockstore_stack_dyn`.

Risks and test signals: this is security-critical because wrong key parsing, local integrity state path handling, or integrity-init error mapping can alter filesystem safety. It maps previous integrity violations to specific CLI error kinds, preserving user-visible safety semantics.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cli-utils/src/blockstore_setup.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cli-utils/src/config.rs -->
## sources/security-integrity/cryfs/crates/cli-utils/src/config.rs

Purpose: formats and prints CryFS filesystem configuration, including old-to-new value transitions after config loading/migration decisions.

Important APIs and functions: `print_config(&ConfigLoadResult)` prints filesystem format version, created-with version, last-opened-with version, cipher, block size, and filesystem id. Nested helpers `print_value`, `format_bytes`, `format_key`, and `format_value` handle changed-value display and terminal styling.

Control flow and state: the function writes directly to stdout. For unchanged values it prints one styled value; for changed values it prints `old -> new`. Byte values are formatted with binary units and raw byte counts.

Dependencies and integration: depends on `byte_unit`, `console::style`, and `cryfs_config::config::ConfigLoadResult`. CLI apps call it after config loading to inform the user about effective filesystem settings.

Risks and test signals: a TODO calls out missing integration tests for output. Since it is display-only, security risk is low, but inaccurate old/new reporting could mislead users during migrations or config mismatch diagnosis.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cli-utils/src/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cli-utils/src/env.rs -->
## sources/security-integrity/cryfs/crates/cli-utils/src/env.rs

Purpose: reads and documents CryFS environment variables that affect frontend interactivity, update checks, and local integrity-state storage.

Important APIs and types: `EnvVarDoc` documents variables. `ENV_VARS_DOCUMENTATION` lists `CRYFS_FRONTEND=noninteractive`, optional `CRYFS_NO_UPDATE_CHECK=true`, and `CRYFS_LOCAL_STATE_DIR=[path]`. `Environment` stores `is_noninteractive`, optional `no_update_check`, and `local_state_dir`. `Environment::read_env` is crate-visible.

Control flow and state: `is_noninteractive` returns true only for exact `noninteractive`. `no_update_check` returns true only for exact `true`. `local_state_dir` canonicalizes an explicitly set path and errors if inaccessible; otherwise it defaults to `dirs::data_local_dir()/cryfs`.

Dependencies and integration: maps local-state errors to `CliErrorKind::InaccessibleLocalStateDir`. `Application::_run` reads this environment before parsing args. Version output uses noninteractive/no-update flags; blockstore setup uses local state later.

Risks and test signals: tests cover unset, exact, empty, other, nonunicode, existing, nonexisting, absolute, and relative local-state cases. The documentation string embeds a hard-coded example default path, which can drift from actual platform-specific defaults.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cli-utils/src/env.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cli-utils/src/error.rs -->
## sources/security-integrity/cryfs/crates/cli-utils/src/error.rs

Purpose: defines structured CLI errors with stable process exit-code mapping and helper traits for converting lower-level errors into `CliError`.

Important APIs and types: `CliError` stores `CliErrorKind` and an `Arc<anyhow::Error>` and displays the inner error. `CliResultExt` maps `Result<T, anyhow::Error>` and `Result<T, Arc<anyhow::Error>>` to a fixed kind. `CliResultExtFn` maps arbitrary error types through a function. `CliErrorKind` enumerates success, argument/config/password/version/path/integrity/filesystem errors.

Control flow and state: `CliErrorKind::exit_code` maps each kind to a fixed `ExitCode`: success is 0, unspecified is 1, and domain-specific errors occupy 10 through 28.

Dependencies and integration: uses `derive_more::Display`, `serde` derives, `anyhow`, and standard `Error`. `Application::run` prints `CliError` and returns `kind.exit_code()`.

Risks and test signals: comments note missing tests for exact shell exit codes and parity with old C++ behavior. Stable numeric codes are operationally important for scripts; adding or changing variants requires care to preserve compatibility.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cli-utils/src/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cli-utils/src/lib.rs -->
## sources/security-integrity/cryfs/crates/cli-utils/src/lib.rs

Purpose: crate root for shared CryFS CLI utilities, defining public module surface and safety policy.

Important APIs and exports: forbids unsafe code. Re-exports `parse_path`, password provider module, environment docs/types, `Application`, `DEFAULT_LOG_LEVEL`, `run`, `print_config`, `CliError` helpers, blockstore setup APIs, and `clap_logflag`. It also exposes `reexports_for_tests` for downstream integration tests needing exact dependency instances.

Control flow and state: no runtime control flow beyond the compile-time `cryfs_version::assert_cargo_version_equals_git_version!()` macro, which ensures package version and git-derived version stay aligned.

Dependencies and integration: module declarations wire `path`, `args`, `password_provider`, `version`, `env`, `application`, `config`, `error`, and `blockstore_setup`. The crate is consumed by multiple binaries and by the check-test fixture.

Risks and test signals: the public re-export surface is a compatibility boundary. `#![forbid(unsafe_code)]` is a meaningful safety signal for CLI glue around cryptographic filesystem operations.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cli-utils/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cli-utils/src/password_provider.rs -->
## sources/security-integrity/cryfs/crates/cli-utils/src/password_provider.rs

Purpose: implements interactive and noninteractive password acquisition for config loading/creation.

Important APIs and types: `InteractivePasswordProvider` and `NoninteractivePasswordProvider` implement `cryfs_config::config::PasswordProvider`. `ask_password_from_console` prompts through `rpassword::prompt_password` with styled indentation. `check_password` rejects empty passwords.

Control flow and state: interactive existing-filesystem flow loops until a nonempty password is entered. Interactive new-filesystem flow also asks for confirmation and loops on mismatch. Noninteractive flows ask once and return an error for empty input without confirmation. Passwords are plain `String`s and are not persisted by this module.

Dependencies and integration: depends on `anyhow::ensure`, `console::style`, `rpassword`, and `cryfs_config`. CLI applications choose provider based on environment/front-end mode.

Risks and test signals: a TODO notes password memory hardening is missing; strings are not mprotected or zeroized. Another TODO notes missing tests. Noninteractive mode intentionally skips confirmation, useful for automation but easier to misuse when creating a new filesystem.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cli-utils/src/password_provider.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cli-utils/src/path.rs -->
## sources/security-integrity/cryfs/crates/cli-utils/src/path.rs

Purpose: provides a clap value parser that converts user-supplied paths into absolute paths.

Important APIs and functions: `parse_path(s: &str) -> Result<PathBuf, String>` calls `Path::new(s).absolutize()`, returns the owned absolute path, and converts path-absolutize errors into strings suitable for clap.

Control flow and state: no persistent state exists. The function resolves relative paths against the process current working directory at parse time.

Dependencies and integration: depends on `path_absolutize` and standard `Path`/`PathBuf`. The doc comment shows use as `#[arg(value_parser=parse_path)]` in clap-derived args.

Risks and test signals: TODO notes missing tests. Absolutization is not canonicalization, so it does not require path existence and does not resolve all symlinks; this is useful for CLI parsing but later code must still validate vault/mount directory accessibility.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cli-utils/src/path.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cli-utils/src/version/http_client.rs -->
## sources/security-integrity/cryfs/crates/cli-utils/src/version/http_client.rs

Purpose: abstraction for HTTP GET requests used by update checking, plus a reqwest implementation and test fake.

Important APIs and types: `HttpClient` trait exposes `get(&self, url, timeout) -> Result<String>`. `ReqwestHttpClient` builds a blocking reqwest client, performs a GET with timeout, and returns response text. Test-only `FakeHttpClient` maps URLs to content and counts requests through an `AtomicUsize`.

Control flow and state: production requests create a fresh reqwest blocking client per call. The fake stores website bodies in a `HashMap` and increments request count for every attempted URL, returning an `anyhow` error when unknown.

Dependencies and integration: depends on optional `reqwest` for production, `anyhow`, `Duration`, and test synchronization primitives. `update_checker` uses the trait; `version.rs` injects `ReqwestHttpClient` from the CLI runner.

Risks and test signals: tests include fake behavior and live reqwest checks against invalid protocols/domains and example.com. Live network tests can be flaky in offline or filtered environments. The abstraction keeps update-check parsing testable without network access.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cli-utils/src/version/http_client.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cli-utils/src/version/mod.rs -->
## sources/security-integrity/cryfs/crates/cli-utils/src/version/mod.rs

Purpose: module hub for version banner and optional update-check support.

Important APIs and exports: always declares `mod version` and re-exports `show_version`. When the `check_for_updates` feature is enabled, it declares `update_checker` and `http_client`, re-exports `ReqwestHttpClient`, and exposes `FakeHttpClient` for tests under `cfg(all(test, feature = "check_for_updates"))`.

Control flow and state: no runtime logic exists. Conditional compilation controls whether network update-check code is part of the crate.

Dependencies and integration: `application.rs` uses `show_version` and, with update checks enabled, `ReqwestHttpClient`. Tests in `version.rs` and `update_checker.rs` use the fake client export.

Risks and test signals: feature gating is the central privacy/reliability switch. Downstream builds that disable default features avoid compiling reqwest/serde_json update-check paths entirely.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cli-utils/src/version/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cli-utils/src/version/update_checker.rs -->
## sources/security-integrity/cryfs/crates/cli-utils/src/version/update_checker.rs

Purpose: fetches and parses CryFS update/security-warning metadata from `https://www.cryfs.org/version_info.json`.

Important APIs and types: `check_for_updates(http_client, current_version)` returns `UpdateCheckResult` containing optional `released_newer_version` and optional `security_warning`. `VersionResponse` deserializes `version_info.current` and optional `warnings`. `parse_warning` selects a warning whose key exactly matches the running version string.

Control flow and state: the function performs a GET with a 2-second timeout, parses JSON with serde, parses the newest version, compares it to the current version, and returns a newer-version string only if the server version is greater. No state is persisted.

Dependencies and integration: uses the `HttpClient` trait, `serde_json`, `cryfs_version::Version`, and `anyhow`. `version.rs` calls it from `_maybe_check_for_updates`.

Risks and test signals: tests cover HTTP errors, invalid JSON, missing fields, invalid versions, newer/older versions, empty warnings, matching warnings, and warnings for other versions. Security warning matching depends on exact version string formatting, including prerelease/build metadata behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cli-utils/src/version/update_checker.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cli-utils/src/version/version.rs -->
## sources/security-integrity/cryfs/crates/cli-utils/src/version/version.rs

Purpose: prints the application version banner, local build warnings, and optional update/security information.

Important APIs and functions: `show_version` writes to stderr through `_show_version`. `warning` formats warning lines. `_maybe_check_for_updates` respects environment flags and calls `update_checker::check_for_updates` when enabled and interactive.

Control flow and state: `_show_version` prints `name version`, then emits warnings for development builds with commits after tag, uncommitted build trees, prerelease versions, and debug builds. With update checks enabled, it skips network access when `CRYFS_NO_UPDATE_CHECK=true` or noninteractive mode is active; otherwise it reports newer releases, server-provided security warnings, or update-check failure messages.

Dependencies and integration: uses `console::style`, `cryfs_version::{VersionInfo, Version}`, `Environment`, `HttpClient`, and `UpdateCheckResult`. `application.rs` invokes it during `--version`, normal startup, and parse-error handling.

Risks and test signals: tests capture output for release/prerelease/git-modified/development/debug scenarios, update-check disablement, newer-version messages, failures, and security warnings. A TODO notes `--version` should likely print to stdout instead of stderr. Network failures are nonfatal and reported as warnings.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cli-utils/src/version/version.rs -->
