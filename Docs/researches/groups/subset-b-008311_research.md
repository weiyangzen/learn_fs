# Research: subset-b-008311

Grouped research report for CryFS CLI/config/concurrent-store files. Each section is delimited for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cli-utils/tests/arguments.rs -->
# sources/security-integrity/cryfs/crates/cli-utils/tests/arguments.rs

Purpose: integration-style tests for `cryfs-cli-utils::run` and its clap `Application` wrapper. The file dynamically builds small temporary Rust binaries with `tempproject`, then verifies common argument behavior across empty args, flags, mandatory/optional positionals, mandatory/optional options, help, version, and debug-build warnings.

Important APIs/types/functions: `TestConfig::project` generates a Cargo project and main program using `Application`; `TestProject::expect_help_message` centralizes help assertions; static `PROJECT_*` fixtures are wrapped in `StaticDrop` so temp dirs are cleaned at process exit. Tests use `assert_cmd`, `predicates`, `rstest`, `lazy_static`, and `indoc`.

Control flow: each fixture builds a binary once, then modules run combinations of CLI arguments. Help wins over other args, version is exclusive with other real args, parsing errors still include the version banner, and debug/release builds differ in warning output.

State and persistence: creates temporary Cargo projects and binaries; the explicit cleanup wrapper prevents leaked temp directories from long-lived statics.

Dependencies/integration: exercises `cryfs-cli-utils` through a real generated binary rather than direct unit calls, so it covers clap integration, logging defaults, version emission, and debug-build warning plumbing.

Risks/test signals: tests are broad but expensive because they compile temp projects. They intentionally rely on exact clap error text and may need updates when clap formatting changes. No subcommand coverage yet; a TODO records that gap.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cli-utils/tests/arguments.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/Cargo.toml -->
# sources/security-integrity/cryfs/crates/concurrent-store/Cargo.toml

Purpose: crate manifest for `cryfs-concurrent-store`, the shared async loading/cache/drop coordination crate.

Important APIs/types/functions: declares the package metadata through workspace fields and exposes no binary targets. The code exports `ConcurrentStore`, `LoadedEntryGuard`, `Inserting`, `LoadingOrLoaded`, and `RequestImmediateDropResult` from `src/lib.rs`.

Control flow: build configuration is simple: default features are empty, and a `testutils` feature exists for test-only helpers exposed by dependent code.

State and persistence: no runtime persistence is configured here. The manifest controls dependency linkage and feature gates.

Dependencies/integration: depends on `anyhow`, `async-trait`, `futures`, `lockable`, `tokio`, `log`, `cryfs-utils`, and `cryfs-version`. These dependencies match the implementation's async drop guards, shared futures, mutex-held state machine, and cargo/git version assertion.

Risks/test signals: there are no dev-dependencies or local tests in this crate manifest. Behavioral confidence must come from downstream crate tests or future direct tests for cancellation, immediate drop, and waiter accounting.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/entry/dropping.rs -->
# sources/security-integrity/cryfs/crates/concurrent-store/src/entry/dropping.rs

Purpose: represents the `Dropping` state of a concurrent-store entry while an asynchronous drop or immediate-drop callback is in progress.

Important APIs/types/functions: `EntryStateDropping` wraps a `Shared<BoxFuture<'static, ()>>`. `new` stores a real drop future, `new_dummy` creates an already-ready placeholder for temporary state replacement, `future` borrows the shared future, and `into_future` consumes the state.

Control flow: `store.rs` inserts this state when the last loaded guard is released or when an immediate drop is requested for an unloaded key. Callers that find a `Dropping` entry clone and await the shared future outside the entries mutex before retrying.

State and persistence: in-memory only. The shared future is the synchronization point that keeps future loaders from entering until cleanup/removal completes.

Dependencies/integration: uses `futures::FutureExt` and `Shared`. It is re-exported by `entry/mod.rs` and consumed by `ConcurrentStoreInner`.

Risks/test signals: the dummy constructor is safe only as a short-lived replacement before the real future is installed. If a dropping future is not driven to completion, the map can remain blocked for that key.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/entry/dropping.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/entry/immediate_drop_request.rs -->
# sources/security-integrity/cryfs/crates/concurrent-store/src/entry/immediate_drop_request.rs

Purpose: stores and arbitrates an exclusive "immediate drop" request for an entry that is currently loading or loaded.

Important APIs/types/functions: `ImmediateDropRequest<V>` is either `NotRequested` or `Requested { drop_fn, on_dropped }`. `request_immediate_drop_if_not_yet_requested` installs the callback once and returns `Requested`, or returns a shared future for the earlier request. `immediate_drop_requested` exposes the completion `Event`. `ImmediateDropRequestResponse` communicates the two outcomes.

Control flow: when requested, future loads are blocked by `store.rs`; once all active/unfulfilled readers are gone, the store consumes the loaded entry and invokes `drop_fn` with exclusive access. The wrapper triggers `on_dropped` after the callback finishes so blocked tasks can retry.

State and persistence: state is in memory; the `Event` is a one-shot synchronization primitive. The callback owns the actual persistence side effect, such as deleting underlying storage.

Dependencies/integration: requires `AsyncDropGuard<V>`, `Event`, boxed futures, and `Shared`. `EntryStateLoaded` and `EntryStateLoading` embed it.

Risks/test signals: callback is boxed as `dyn FnOnce`; failure handling is left to the callback and store path. Duplicate requests intentionally do not replace the original callback.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/entry/immediate_drop_request.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/entry/loaded.rs -->
# sources/security-integrity/cryfs/crates/concurrent-store/src/entry/loaded.rs

Purpose: models a successfully loaded entry and tracks live access for unload/drop decisions.

Important APIs/types/functions: `EntryStateLoaded<V>` holds an `AsyncDropArc<V>`, `num_unfulfilled_waiters`, and `ImmediateDropRequest<V>`. Constructors handle just-finished loading and direct insertion. `get_entry` clones access; `get_entry_and_decrease_num_unfulfilled_waiters` finalizes a loading waiter; `num_tasks_with_access` combines unfulfilled waiters plus strong-count minus the map's own reference; `into_inner` extracts the value only when no unfulfilled waiters remain.

Control flow: after loading completes, `store.rs` replaces `EntryStateLoading` with this state and initializes waiter count from the loading state. Dropping starts only when no active or unfulfilled access remains.

State and persistence: in-memory reference accounting only. Immediate-drop callback may later perform persistence-level removal.

Dependencies/integration: uses `AsyncDropArc`, `AsyncDropGuard`, `Event`, and immediate-drop helpers. It is the bridge between shared access guards and exclusive drop.

Risks/test signals: strong-count arithmetic is subtle; leaked or cancelled waiters can keep entries alive. Assertions protect impossible extraction with pending waiters.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/entry/loaded.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/entry/loading.rs -->
# sources/security-integrity/cryfs/crates/concurrent-store/src/entry/loading.rs

Purpose: models an entry whose loader future is in progress and lets multiple callers await the same load.

Important APIs/types/functions: `EntryStateLoading<V,E>` wraps a shared loading-result future, monotonically increasing `num_waiters`, and an `ImmediateDropRequest`. `LoadingResult<E>` is `Loaded`, `NotFound`, or `Error(E)` and is cloneable for shared futures. `add_waiter` increments waiter count and returns an `EntryLoadingWaiter`.

Control flow: `ConcurrentStoreInner::make_loading_future` creates this state. Waiters await the shared future; on `Loaded`, the map has already transitioned to `Loaded`, and the waiter finalizes against the store. Immediate-drop requests can be registered while loading, then carried into `EntryStateLoaded`.

State and persistence: no persistence; tracks in-memory waiting tasks. Waiters are never decremented in loading state, only transferred to loaded-state unfulfilled waiter accounting.

Dependencies/integration: uses `futures::Shared`, `AsyncDropGuard`, `Event`, and `EntryLoadingWaiter`.

Risks/test signals: a top-level TODO in `store.rs` states cancellation is not safe; if a task waiting for loading is cancelled, counts can be wrong. Tests should target cancelled waiters and immediate-drop during loading.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/entry/loading.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/entry/mod.rs -->
# sources/security-integrity/cryfs/crates/concurrent-store/src/entry/mod.rs

Purpose: central module for the per-key state machine used by `ConcurrentStoreInner`.

Important APIs/types/functions: `EntryState<V,E>` has `Loading(EntryStateLoading)`, `Loaded(EntryStateLoaded)`, and `Dropping(EntryStateDropping)` variants. The module re-exports loading, loaded, dropping, immediate-drop, and waiter types used by `store.rs`.

Control flow: all transitions are driven from `store.rs`: absent to loading, loading to loaded or absent, loaded to dropping, dropping to absent. The enum keeps those transitions explicit and type checked.

State and persistence: this module defines in-memory state only. Persistence effects are deferred to value `AsyncDrop` or immediate-drop callbacks.

Dependencies/integration: depends on `cryfs_utils::async_drop::AsyncDrop` to constrain stored values. It is private to the crate but its subtypes are visible within crate modules.

Risks/test signals: the module has no tests of its own; correctness depends on store-level transition tests. Any new state variant must update all exhaustive matches in `store.rs`.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/entry/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/entry/waiter.rs -->
# sources/security-integrity/cryfs/crates/concurrent-store/src/entry/waiter.rs

Purpose: RAII handle for a caller registered as waiting on an entry load.

Important APIs/types/functions: `EntryLoadingWaiter<K,E>` owns `EntryLoadingWaiterInner { key, loading_result }`. It is marked `#[must_use]` and intentionally non-cloneable. `wait_until_loaded` awaits the shared `LoadingResult` and returns `Option<AsyncDropGuard<LoadedEntryGuard<...>>>`.

Control flow: on `Loaded`, the waiter calls `ConcurrentStoreInner::_finalize_waiter`, which decrements loaded-state unfulfilled waiter count and grants a loaded guard. On `NotFound` or `Error`, the loading state has already been removed, so no decrement is required.

State and persistence: no persistence. Its main state behavior is guaranteeing one waiter token is redeemed exactly once.

Dependencies/integration: uses `safe_panic!` on `Drop` if the waiter is discarded without awaiting, because that leaks waiter accounting. Integrated by `EntryStateLoading`, `LoadingOrLoaded`, and `Inserting`.

Risks/test signals: cancellation/drop before awaiting is explicitly unsafe and converted to a safe panic. Tests should exercise waiter misuse and successful finalization.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/entry/waiter.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/guard.rs -->
# sources/security-integrity/cryfs/crates/concurrent-store/src/guard.rs

Purpose: loaded-entry guard that keeps an entry alive while a caller uses it and unloads it when released.

Important APIs/types/functions: `LoadedEntryGuard<K,V,E>` stores the owning store, key, and `AsyncDropArc<V>` guard. Public `key`, `value`, and `request_immediate_drop` expose access and keyed deletion. Its `AsyncDrop` impl removes its value guard and calls `ConcurrentStoreInner::unload`.

Control flow: store methods return this guard wrapped in `AsyncDropGuard`. Dropping a guard decreases the value reference count, then `_drop_if_no_references` may transition the map to `Dropping`.

State and persistence: in-memory RAII. Persistence effects occur through `V::async_drop` or immediate-drop callbacks initiated from the guard.

Dependencies/integration: uses `AsyncDrop`, `AsyncDropArc`, `AsyncDropGuard`, `RequestImmediateDropResult`, and `lockable::Never`.

Risks/test signals: implementation uses `unwrap()` on async-drop results with TODOs. Misordered or missing `async_drop` by consumers may leave entries loaded until store drop panics.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/guard.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/inserting.rs -->
# sources/security-integrity/cryfs/crates/concurrent-store/src/inserting.rs

Purpose: must-use handle returned by `try_insert_loading` for a caller inserting a newly loaded entry.

Important APIs/types/functions: `Inserting<K,V,E>` owns store access and an `EntryLoadingWaiter`. `wait_until_inserted` awaits the load and returns a `LoadedEntryGuard`, asserting the insert loader cannot return `None`.

Control flow: `try_insert_loading` installs a loading state with a loader wrapped to return `Some(entry)` and returns `Inserting`. The caller must drive `wait_until_inserted`, which drives the underlying shared future and finalizes waiter accounting.

State and persistence: no persistence; holds in-memory insertion state until redeemed.

Dependencies/integration: uses `with_async_drop_2_infallible!` to keep the store guard alive while awaiting. `Drop` calls `safe_panic!` if the handle is discarded without waiting.

Risks/test signals: if callers ignore this `#[must_use]` type at runtime, the store can leak loading/waiter state. The invariant that insertion loaders never return `None` is enforced by `expect`.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/inserting.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/lib.rs -->
# sources/security-integrity/cryfs/crates/concurrent-store/src/lib.rs

Purpose: crate root for the unsafe-free concurrent store abstraction.

Important APIs/types/functions: forbids unsafe code, allows private intra-doc links, declares internal modules, and re-exports `LoadedEntryGuard`, `Inserting`, `LoadingOrLoaded`, `ConcurrentStore`, and `RequestImmediateDropResult`.

Control flow: no runtime flow beyond module wiring. The public surface is intentionally small and channels callers through RAII handles.

State and persistence: state lives in `store.rs` and entry modules. The root adds no persistence behavior.

Dependencies/integration: invokes `cryfs_version::assert_cargo_version_equals_git_version!()` to enforce version consistency between Cargo metadata and git-derived versioning.

Risks/test signals: missing-docs is a TODO, so public APIs may be underdocumented for downstream users. Feature `testutils` is configured in Cargo but not surfaced here.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/loading_or_loaded.rs -->
# sources/security-integrity/cryfs/crates/concurrent-store/src/loading_or_loaded.rs

Purpose: must-use result object for "get if present or wait for load" operations.

Important APIs/types/functions: `LoadingOrLoaded<K,V,E>` wraps `NotFound`, `Loading { waiter, store }`, or `Loaded(LoadedEntryGuard)`. `wait_until_loaded` normalizes all cases into `Result<Option<LoadedEntryGuard>, E>`.

Control flow: store methods create this wrapper for already loaded entries, existing loading futures, newly started loads, or not-found states. Awaiting it either returns immediately or redeems an `EntryLoadingWaiter`.

State and persistence: no persistent state. It temporarily owns store/waiter references so accounting can be completed correctly.

Dependencies/integration: uses `AsyncDropArc`, `AsyncDropGuard`, `safe_panic!`, and `with_async_drop_2_infallible!`. It integrates with `ConcurrentStore::get_loaded_or_insert_loading`, `get_if_loading_or_loaded`, and `all_loading_or_loaded`.

Risks/test signals: `Drop` safe-panics if not awaited, with a typo in the message (`wait_for_loaded` vs `wait_until_loaded`). Cancellation before wait completion remains part of the broader store cancellation-safety risk.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/loading_or_loaded.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/store.rs -->
# sources/security-integrity/cryfs/crates/concurrent-store/src/store.rs

Purpose: implements `ConcurrentStore`, a per-key async cache that coalesces concurrent loads, returns shared loaded guards, and asynchronously drops or immediately removes entries when access ends.

Important APIs/types/functions: public methods include `new`, `clone_ref`, `try_insert_loading`, `try_insert_loaded`, `get_loaded_or_insert_loading`, `get_if_loading_or_loaded`, `all_loading_or_loaded`, `is_fully_absent`, test-only `is_empty`, and `request_immediate_drop`. Internal helpers create loading/drop futures, execute immediate drops, remove dropping entries, finalize waiters, and implement `AsyncDrop`.

Control flow: the store map is a `Mutex<HashMap<K, EntryState<V,E>>>`. Absent keys start a loading future; concurrent callers get waiters. Loading futures update the map to `Loaded` or remove entries on not-found/error. Loaded guards call `unload`; when no references or unfulfilled waiters remain, the state becomes `Dropping`, a shared drop future runs outside the lock, and the map entry is removed. Requests during dropping await the shared future and retry. Immediate-drop requests block new access, wait for existing readers, then run a user callback with exclusive access.

State and persistence: all coordination state is in memory. Persistence is delegated to `V::async_drop` or the immediate-drop callback. Store drop panics if loading or loaded entries remain, but waits for dropping futures.

Dependencies/integration: relies on `AsyncDropArc`, `AsyncDropGuard`, `Event`, boxed/shared futures, `for_each_unordered`, `tokio::oneshot`, and `lockable::Never`.

Risks/test signals: a file-level TODO states cancellation is not safe because waiter counts can become wrong. Several async-drop paths use `unwrap()`. Direct tests are absent in this crate, so downstream tests should cover races, immediate drop, failed loads, and store shutdown invariants.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/store.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/Cargo.toml -->
# sources/security-integrity/cryfs/crates/cryfs-cli/Cargo.toml

Purpose: manifest for the `cryfs-cli` package and `cryfs` binary.

Important APIs/types/functions: declares `[[bin]] name = "cryfs"` and package metadata from the workspace. The binary entry is `src/bin/cryfs.rs`, backed by library type `Cli`.

Control flow: feature set includes default empty features and optional `tokio_console`. Tests build both debug and release binaries through `escargot`.

State and persistence: no runtime state; dependency and feature configuration determines CLI, config, runner, and local-state capabilities.

Dependencies/integration: links `cryfs-cli-utils`, `cryfs-config`, `cryfs-runner`, `cryfs-blockstore`, `cryfs-utils`, `cryfs-version`, clap/logging/dialoguer/progress dependencies, and test dependencies such as `assert_cmd`, `escargot`, `lazy_static`, and `predicates`.

Risks/test signals: manifest dependency graph is broad because the CLI orchestrates config, runner, and local state. Cargo-level tests verify command-line behavior, but actual mount flows remain TODO-covered rather than fully tested here.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/args/cryfs_args.rs -->
# sources/security-integrity/cryfs/crates/cryfs-cli/src/args/cryfs_args.rs

Purpose: top-level clap parser for the `cryfs` command.

Important APIs/types/functions: `CryfsArgs` flattens optional `MountArgs`, has `--show-ciphers` in an immediate-exit group conflicting with mounting, and hidden exclusive `--daemon`. `footer` renders environment-variable help from `cryfs_cli_utils::ENV_VARS_DOCUMENTATION`.

Control flow: clap decides whether mount args are present or an immediate-exit path is selected. `--daemon` is hidden and exclusive so normal users cannot combine it with other flags; actual daemon validity is checked later by runner bootstrap.

State and persistence: parser state only. No files are touched.

Dependencies/integration: depends on clap derive, color-print formatting, `MountArgs`, and shared CLI-utils env-var docs. `Cli::main` consumes these parsed fields.

Risks/test signals: tests in `cryfs-cli/tests/args.rs` cover help/version/show-ciphers and daemon flag hiding/exclusivity. Help footer output has TODO coverage gaps.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/args/cryfs_args.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/args/fuse_option/atime_option.rs -->
# sources/security-integrity/cryfs/crates/cryfs-cli/src/args/fuse_option/atime_option.rs

Purpose: parses and normalizes FUSE atime-related mount options into runner-level `AtimeUpdateBehavior`.

Important APIs/types/functions: `AtimeOption` is a clap `ValueEnum` with `atime`, `strictatime`, `noatime`, `relatime`, and `nodiratime`. `to_atime_behavior` folds a slice of options into flags and validates allowed/forbidden combinations.

Control flow: duplicates are accepted. `noatime` dominates `nodiratime`, while `atime` and `relatime` are treated as equivalent and can combine. Conflicts such as `noatime` with `atime`/`relatime`/`strictatime`, or `strictatime` with relatime-style flags, return `anyhow::bail!` errors.

State and persistence: no persistence. Result affects runtime atime update policy passed to `cryfs_runner::Mounter`.

Dependencies/integration: maps directly to `cryfs_runner::AtimeUpdateBehavior` and is selected out of mixed `FuseOption` values by `FuseOption::partition`.

Risks/test signals: local `rstest` coverage exhaustively checks one-flag, duplicate, allowed, and forbidden combinations. Semantics intentionally default to `Noatime` to reduce synchronization conflicts.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/args/fuse_option/atime_option.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/args/fuse_option/mod.rs -->
# sources/security-integrity/cryfs/crates/cryfs-cli/src/args/fuse_option/mod.rs

Purpose: combines supported FUSE mount options into a single clap value enum.

Important APIs/types/functions: `FuseOption` wraps `AtimeOption` or `FusePermissionOption`. Its manual `ValueEnum` implementation returns all variants and delegates possible-value rendering. `partition` splits a mixed slice into atime options and permission options using `itertools::partition_map`.

Control flow: clap parses `-o/--fuse-option` values into this enum. `Cli::run_filesystem` partitions the values, validates atime behavior, and converts permission options for the runner.

State and persistence: no persistence. Values are transient CLI configuration.

Dependencies/integration: ties together local `atime_option` and `permission_option` modules, `clap::ValueEnum`, and `itertools`.

Risks/test signals: an assertion checks the manual variant list matches the sub-enum counts. If a new option is added but not included in `value_variants`, the assertion catches it at runtime when clap queries variants.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/args/fuse_option/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/args/fuse_option/permission_option.rs -->
# sources/security-integrity/cryfs/crates/cryfs-cli/src/args/fuse_option/permission_option.rs

Purpose: defines user-facing FUSE permission options.

Important APIs/types/functions: `FusePermissionOption` is a clap `ValueEnum` with `AllowOther` and `AllowRoot`, both rendered in snake_case.

Control flow: parsed through `FuseOption`, partitioned in `Cli::run_filesystem`, then converted into runner FUSE options via `Into` implementations outside this file.

State and persistence: no state or persistence. These flags affect mount-time access policy.

Dependencies/integration: depends only on clap derive. The help text documents that default access is restricted to the mounting user, and these options relax that behavior.

Risks/test signals: no local tests; coverage is indirect through CLI parsing and runner behavior. Security-sensitive risk is user confusion: `allow_other` broadens filesystem access, so help text should stay explicit.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/args/fuse_option/permission_option.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/args/mod.rs -->
# sources/security-integrity/cryfs/crates/cryfs-cli/src/args/mod.rs

Purpose: argument module facade for the CLI crate.

Important APIs/types/functions: declares `cryfs_args`, `fuse_option`, and `mount_args`, then re-exports `CryfsArgs`, `AtimeOption`, `FuseOption`, and `MountArgs`.

Control flow: no runtime control flow. It provides a stable import surface to `cli.rs`.

State and persistence: none.

Dependencies/integration: keeps parser modules private except for the types consumed by the main CLI orchestration.

Risks/test signals: small facade; any parser type rename or visibility change will break imports at compile time. No separate tests needed beyond parser integration tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/args/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/args/mount_args.rs -->
# sources/security-integrity/cryfs/crates/cryfs-cli/src/args/mount_args.rs

Purpose: clap parser for mount-mode arguments and flags.

Important APIs/types/functions: `MountArgs` includes positional `vaultdir` and `mountdir`, optional config path, foreground/background selection, create-missing flags, integrity-violation flags, filesystem upgrade/replacement allowances, cipher and blocksize expectations, idle unmount duration, and repeated `-o/--fuse-option` values. `parse_byte_amount` parses `byte_unit::Byte`.

Control flow: clap validates required positionals and cipher possible values. `Cli` later maps these flags into config loading and runner mount arguments.

State and persistence: no direct persistence. Flags influence vault/mount directory creation, config rewrite, local-state checks, and mount behavior in other modules.

Dependencies/integration: uses `cryfs_cli_utils::parse_path`, `cryfs_config::config::ALL_CIPHERS`, `humantime`, `byte_unit`, and `FuseOption`.

Risks/test signals: unit tests cover human duration parsing and binary/decimal byte parsing. Several TODOs note defaults should be dynamic and replaced-filesystem scenarios need deeper tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/args/mount_args.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/bin/cryfs.rs -->
# sources/security-integrity/cryfs/crates/cryfs-cli/src/bin/cryfs.rs

Purpose: binary entry point for the `cryfs` executable.

Important APIs/types/functions: `main` returns `ExitCode` and delegates all parsing, setup, panic-hook behavior, and execution to `cryfs_cli_utils::run::<Cli>()`.

Control flow: the runner invokes the `Application` implementation in `Cli`, which handles immediate-exit paths, daemon mode, logging, Tokio runtime initialization, config loading, and mounting.

State and persistence: no direct state. All persistence is handled in library modules.

Dependencies/integration: imports `cryfs_cli::Cli`, making the binary a thin shell over the library crate.

Risks/test signals: the file is intentionally minimal. Integration tests in `cryfs-cli/tests/args.rs` execute the built binary, so this entry path is covered for argument behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/bin/cryfs.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/cli.rs -->
# sources/security-integrity/cryfs/crates/cryfs-cli/src/cli.rs

Purpose: main CLI application implementation that connects parsed args, logging, config/local-state checks, and runner mounting.

Important APIs/types/functions: `Cli` implements `cryfs_cli_utils::Application`. Key methods are `new`, `default_log_config`, `should_show_version`, `defer_logging_init`, `main`, `daemon_default_log_config`, `async_main`, `sanity_checks`, `run_filesystem`, `show_ciphers`, `load_or_create_config`, `config_file_location`, `check_config_integrity`, `mount_args`, `password_provider`, and `console`.

Control flow: `main` first handles hidden daemon mode, then `--show-ciphers`, then selects foreground/background `Mounter`. Background mode resolves daemon logging before runtime startup. Async flow checks directories, loads or creates config, prints config, translates FUSE/atime options, calls `mount_filesystem`, and prints unmount notice for foreground.

State and persistence: may create vault/mount dirs, create/load/rewrite encrypted config files, update local filesystem metadata, and update vaultdir-to-filesystem-id metadata.

Dependencies/integration: integrates `cryfs_config`, `cryfs_runner`, `cryfs_cli_utils`, `cryfs_blockstore`, `clap_logflag`, and `InteractiveConsole`.

Risks/test signals: error mapping is extensive but many TODOs remain for user-facing error messages and mount tests. `allow_replaced_filesystem` parameter is forwarded into config loading and checked again for vaultdir metadata.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/cli.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/console.rs -->
# sources/security-integrity/cryfs/crates/cryfs-cli/src/console.rs

Purpose: interactive terminal implementation of the `cryfs_config::config::Console` trait.

Important APIs/types/functions: `InteractiveConsole` stores an `OnceCell<bool>` for the "use default creation settings" answer. It implements migration, replaced-filesystem, changed-key, single-client-mode, scrypt-settings, cipher, blocksize, vaultdir, and mountdir prompts. Helpers `ask_yes_no`, `ask_multiple_choice`, `format_explanation`, `kb`, and `mb` centralize dialoguer UI.

Control flow: creation settings first ask whether defaults should be used; if yes, later creation prompts return defaults without asking. Otherwise, `dialoguer::Confirm` and `Select` drive terminal interaction.

State and persistence: only transient prompt state in `OnceCell`. Choices affect config creation and local-state acceptance in other modules.

Dependencies/integration: uses `dialoguer`, `byte_unit`, `cryfs_crypto::kdf::scrypt::ScryptSettings`, `cryfs_config::Console`, and version types.

Risks/test signals: TODOs note console appearance and flows need tests. Noninteractive mode still returns `InteractiveConsole`, so caller paths must avoid prompts via flags or dedicated password providers where needed.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/console.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/lib.rs -->
# sources/security-integrity/cryfs/crates/cryfs-cli/src/lib.rs

Purpose: library root for the CLI crate.

Important APIs/types/functions: forbids unsafe code, declares modules `args`, `cli`, `console`, and `sanity_checks`, and re-exports `Cli`.

Control flow: no runtime flow here; `src/bin/cryfs.rs` uses the exported `Cli` as the application type.

State and persistence: none directly.

Dependencies/integration: invokes `cryfs_version::assert_cargo_version_equals_git_version!()` for package/version consistency. Internal modules perform actual config and mount behavior.

Risks/test signals: several crate-level TODOs call out missing mount lifecycle tests, unhelpful error messages, and foreground unmount UX. The root keeps those concerns visible but not enforced.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/sanity_checks.rs -->
# sources/security-integrity/cryfs/crates/cryfs-cli/src/sanity_checks.rs

Purpose: pre-mount filesystem sanity checks for vault and mount directories.

Important APIs/types/functions: `check_dir_accessible` verifies existence, optionally prompts/creates, ensures the path is a directory, and calls `check_dir_writeable_and_readable`. That helper writes and reads a `.cryfs_testfile` through `TempFile`, then scans directory entries via `dir_contains_file`. `check_mountdir_doesnt_contain_vaultdir` rejects vault directories inside the mountpoint.

Control flow: async Tokio filesystem calls avoid blocking. Missing paths use command-line create flags or callback prompts. Errors are contextualized with `anyhow`.

State and persistence: may create directories and a temporary test file, which `TempFile` cleans up. Does not persist CryFS metadata.

Dependencies/integration: called by `Cli::sanity_checks` before config load/mount. Uses `cryfs_utils::tmpfile::TempFile`.

Risks/test signals: TODOs note errors should map to dedicated CLI error codes, and there are no local tests. The mountdir/vaultdir containment check is path-prefix based and may need canonicalization scrutiny.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/sanity_checks.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/tests/args.rs -->
# sources/security-integrity/cryfs/crates/cryfs-cli/tests/args.rs

Purpose: binary-level argument tests for the real `cryfs` executable.

Important APIs/types/functions: lazy statics build current, debug, and release binary paths using `assert_cmd::cargo_bin!` and `escargot::CargoBuild`. Helpers `cryfs_cmd`, `cryfs_cmd_debug`, and `cryfs_cmd_release` construct commands.

Control flow: test modules cover no-args failure, help, version exclusivity, `--show-ciphers`, incomplete foreground invocations, debug-build warning behavior, and hidden/exclusive/manual rejection behavior for `--daemon`.

State and persistence: debug/release builds create Cargo build artifacts. Tests do not create vaults or mount filesystems.

Dependencies/integration: validates the compiled binary, `cryfs_config::CRYFS_VERSION`, `ALL_CIPHERS`, clap output, and `cryfs_runner::run_as_background_daemon` fd checks for manual daemon invocation.

Risks/test signals: strong coverage for immediate CLI parse behavior, but many TODOs remain for successful mounting, update checks, path handling, env-var help, git warnings, and invalid argument usage details. Tests depend on exact clap/error strings.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/tests/args.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/Cargo.toml -->
# sources/security-integrity/cryfs/crates/cryfs-config/Cargo.toml

Purpose: manifest for `cryfs-config`, which owns encrypted config-file serialization, creation/loading policy, and local-state metadata integration.

Important APIs/types/functions: feature set has default empty and optional `testutils`. The crate exports config APIs and local-state APIs from `src/lib.rs`.

Control flow: dependencies enable binary config layouts (`binrw`, `binary-layout`), JSON/serde compatibility, scrypt KDF, symmetric crypto, hashing, byte units, and workspace versioning.

State and persistence: manifest config determines availability of filesystem config persistence, local metadata JSON, and encryption code.

Dependencies/integration: depends on `cryfs-blockstore`, `cryfs-blobstore`, `cryfs-crypto`, `cryfs-utils`, and `cryfs-version`, plus `anyhow`, `serde`, `serde_json`, `serde_with`, `rand`, `hex`, `thiserror`, and `log`.

Risks/test signals: only `tokio` dev-dependency is declared; many source files include TODOs for missing tests. Security-sensitive code relies heavily on unit tests inside ciphers/encryption and future coverage for loader/local-state errors.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/ciphers.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/config/ciphers.rs

Purpose: runtime cipher-name lookup while preserving static cipher types where callers need compile-time specialization.

Important APIs/types/functions: `ALL_CIPHERS` lists `xchacha20-poly1305`, `aes-256-gcm`, and `aes-128-gcm`. `UnknownCipherError` reports unsupported names. `AsyncCipherCallback` and `SyncCipherCallback` let callers dispatch on a name. `lookup_cipher_sync`, `lookup_cipher_async`, `lookup_cipher_dyn`, and `cipher_is_supported` implement lookup variants.

Control flow: string match selects the concrete cipher type and calls the provided callback. Dynamic lookup builds a boxed `dyn Cipher` with an encryption key sized for the selected cipher.

State and persistence: no persistence; names stored in config files are validated through this module.

Dependencies/integration: uses `cryfs_crypto::symmetric` cipher definitions and encryption key handling. Used by config creation and inner config encryption/decryption.

Risks/test signals: tests verify all advertised ciphers resolve, unknown ciphers error, and selected ciphers can decrypt each other's test ciphertext only when expected type matches. TODOs note executable-size concerns and missing lookup variants.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/ciphers.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/configfile.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/config/configfile.rs

Purpose: encrypted config-file wrapper for creating, loading, mutating, and saving `CryConfig`.

Important APIs/types/functions: error enums `CreateConfigFileError`, `SaveConfigFileError`, and `LoadConfigFileError` map filesystem and serialization failures. `Access` distinguishes read-only from read-write. `CryConfigFile` stores path, config, access mode, scrypt params, `ConfigEncryptionKey`, and modified flag.

Control flow: `create_new` opens with `create_new(true)`, generates scrypt params, derives config encryption key, and writes encrypted config. `load` reads and decrypts. `config_mut` marks modified; `save_if_modified_and_has_readwrite_access` rewrites only when needed and allowed.

State and persistence: persists encrypted config files using outer/inner encryption. `save` truncates and rewrites the target path; read-only access refuses writes.

Dependencies/integration: uses `Scrypt`, `ScryptParams`, `ScryptSettings`, progress bars, and `super::encryption`. Called by loader create/load paths.

Risks/test signals: errors are structured but encryption errors collapse into serialization/deserialization wrappers. TODOs call for richer error mapping and tests, including error cases.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/configfile.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/console.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/config/console.rs

Purpose: trait defining all user interactions required by config creation/loading.

Important APIs/types/functions: `Console` asks about filesystem migration, changed encryption key, replaced filesystem id, disabling single-client mode, new-filesystem single-client mode, scrypt settings, cipher, blocksize, and missing vault/mount directory creation.

Control flow: config loader/creator invoke these methods when command-line flags do not preselect behavior or when local-state mismatch needs user acceptance.

State and persistence: trait itself has no state. Implementations influence whether config/local-state is created, migrated, rewritten, or rejected.

Dependencies/integration: returns `anyhow::Result`, `ScryptSettings`, `Byte`, and version metadata. Implemented by `cryfs-cli::InteractiveConsole`.

Risks/test signals: the trait mixes config-specific and CLI-directory prompts; TODOs suggest splitting. Noninteractive implementations must be careful to avoid blocking prompts.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/console.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/creator.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/config/creator.rs

Purpose: creates a new in-memory `CryConfig` and local filesystem metadata before the config file is encrypted and saved.

Important APIs/types/functions: `ConfigCreateError`, `ConfigCreateResult`, and public `create`. Helpers generate an encryption key for the chosen cipher, a random root `BlobId`, and optional exclusive client id for single-client mode.

Control flow: cipher and blocksize come from command-line flags or console prompts. A random filesystem id and encryption key are generated, `FilesystemMetadata::load_or_generate` creates/checks local state, and single-client mode decides whether `exclusive_client_id` is set.

State and persistence: writes local filesystem metadata through `FilesystemMetadata`; the returned config is persisted later by `CryConfigFile::create_new`.

Dependencies/integration: uses cipher lookup callbacks, `rand::rng`, `BlobId`, `ClientId`, `EncryptionKey`, `LocalStateDir`, and current CryFS/filesystem versions.

Risks/test signals: key generation uses `rand::rng()` with a TODO about RNG choice. Blocksize validity is not checked here. Tests are TODO.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/creator.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/cryconfig/cryconfig.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/config/cryconfig/cryconfig.rs

Purpose: core logical representation of a CryFS filesystem config.

Important APIs/types/functions: `FILESYSTEM_FORMAT_VERSION` is `0.10`. `CryConfig` stores root blob id, encryption key hex, cipher name, format/creation/last-opened versions, blocksize, filesystem id, and optional exclusive client id. Methods `serialize`, `deserialize`, and `missing_block_is_integrity_violation` delegate format handling and expose integrity mode.

Control flow: creation populates all fields; loader updates version fields and checks settings. Serialization intentionally goes through `serialization.rs`, not the derived serde impl.

State and persistence: this is the persisted config payload after encryption. Fields encode filesystem identity, block layout, crypto material, and single-client integrity mode.

Dependencies/integration: uses `byte_unit::Byte`, `FilesystemId`, and `cryfs_version::Version`.

Risks/test signals: key and cipher are strings with TODOs to use stronger types and protected memory. Format fields are strings for compatibility, which shifts validation into loader/serialization.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/cryconfig/cryconfig.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/cryconfig/filesystem_id.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/config/cryconfig/filesystem_id.rs

Purpose: fixed-size identifier for a CryFS filesystem.

Important APIs/types/functions: `FilesystemId([u8; 16])` supports `new_random`, `from_bytes`, `to_bytes`, `from_hex`, `to_hex`, serde, equality/hash, and custom `Debug` that prints hex.

Control flow: creation generates random ids; config serialization stores hex; local-state metadata uses ids as directory names and vaultdir mapping values.

State and persistence: persisted in encrypted config JSON and local-state JSON. Also used in local-state directory paths.

Dependencies/integration: uses `rand::random` for generation and `hex` for encoding/decoding.

Risks/test signals: `from_hex` rejects non-16-byte values. No local tests are present; callers rely on serde/local-state tests elsewhere. Path use of hex output is stable and filesystem-safe.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/cryconfig/filesystem_id.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/cryconfig/mod.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/config/cryconfig/mod.rs

Purpose: module facade for core config data structures.

Important APIs/types/functions: declares `cryconfig`, `serialization`, and `filesystem_id`; re-exports `CryConfig`, `FILESYSTEM_FORMAT_VERSION`, and `FilesystemId`.

Control flow: no runtime flow. Keeps serialization internals private while exposing the stable config model.

State and persistence: persistence behavior is implemented in child modules.

Dependencies/integration: consumed by higher config modules, loader, creator, local-state, and CLI.

Risks/test signals: compile-time facade only. Any serialization API change must preserve the `CryConfig::serialize/deserialize` delegation contract.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/cryconfig/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/cryconfig/serialization.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/config/cryconfig/serialization.rs

Purpose: JSON compatibility layer for serialized `CryConfig`, including legacy field names and format-version validation.

Important APIs/types/functions: `DeserializationError` distinguishes too-old, too-new, invalid config, and JSON errors. `serialize` writes a `SerializableCryConfig` wrapper under `cryfs`. `deserialize` reads, checks format/migration markers, validates required fields, parses blocksize and filesystem id, then constructs `CryConfig`.

Control flow: `check_format_version` requires the stored version to equal current `FILESYSTEM_FORMAT_VERSION`; missing version is treated as 0.8 and too old. Migration flags `hasVersionNumbers` and `hasParentPointers` must be present and true for 0.10.

State and persistence: defines on-disk JSON field names before encryption, including string-encoded byte and client-id values for compatibility.

Dependencies/integration: uses serde, serde_with, `Byte`, `Version`, and `FilesystemId`.

Risks/test signals: TODOs request tests for errors and C++ JSON compatibility. One invalid-message path repeats "hasVersionNumbers" for parent-pointer failure, which may confuse diagnostics.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/cryconfig/serialization.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/encryption/inner.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/config/encryption/inner.rs

Purpose: inner layer of config encryption: encrypts the serialized `CryConfig` with the filesystem cipher and records the cipher name.

Important APIs/types/functions: `InnerConfigLayout` stores header, cipher name, and encrypted config bytes. `InnerConfig::encrypt`, `decrypt`, `deserialize`, and `serialize` implement the layer. Header is `cryfs.config.inner;0`, and plaintext is padded to `CONFIG_SIZE` 900 bytes before encryption.

Control flow: encryption selects cipher from `config.cipher`, serializes JSON into a `Data` buffer with room for cipher overhead, pads to fixed size, encrypts, and stores bytes. Decryption looks up the stored cipher, decrypts, removes padding, deserializes `CryConfig`, and ensures the internal config cipher matches the layer cipher.

State and persistence: serialized inside the outer config layer; hides exact JSON length up to 900 bytes.

Dependencies/integration: uses `binrw`, dynamic cipher lookup, `Data`, and padding helpers.

Risks/test signals: config larger than 900 bytes errors and requires increasing `CONFIG_SIZE`. Header error text says "outer config" although this is inner config.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/encryption/inner.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/encryption/mod.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/config/encryption/mod.rs

Purpose: orchestrates two-layer config encryption/decryption and password-derived key splitting.

Important APIs/types/functions: `encrypt` builds `InnerConfig` then `OuterConfig` and serializes it. `decrypt` deserializes outer config, reads KDF parameters, derives `ConfigEncryptionKey`, decrypts outer then inner config, and returns key/params/config. `ConfigEncryptionKey` derives one combined key and exposes `outer_key` and `inner_key`.

Control flow: password KDF derives enough bytes for AES-256-GCM outer key plus maximum inner cipher key. Outer key decrypts KDF-protected wrapper; inner key closure slices bytes according to selected filesystem cipher size.

State and persistence: persists encrypted config to caller-provided writer. During load, returns KDF parameters so subsequent saves can reuse them.

Dependencies/integration: uses `PasswordBasedKDF`, `KDFParameters`, `EncryptionKey`, progress bars, `InnerConfig`, and `OuterConfig`.

Risks/test signals: TODOs mention protecting password/config key material in memory and avoiding double derivation. Tests include backward compatibility with a C++ config blob.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/encryption/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/encryption/outer.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/config/encryption/outer.rs

Purpose: outer config encryption layer that stores KDF parameters and encrypts the inner config with a password-derived AES-256-GCM key.

Important APIs/types/functions: `OuterCipher` is `Aes256Gcm`. `OuterConfigLayout` stores header `cryfs.config;1;scrypt`, KDF parameters, and encrypted inner config. `OuterConfig::encrypt`, `decrypt`, `deserialize`, `serialize`, `kdf_parameters`, and helper `len` implement storage.

Control flow: inner config is serialized, padded to `CONFIG_SIZE` 1024 bytes adjusted for cipher overhead, encrypted with the outer key, and written with KDF parameters. Decryption validates header, decrypts, removes padding, and deserializes `InnerConfig`.

State and persistence: persisted bytes are the top-level `cryfs.config` file format. KDF parameters are plaintext so the password-derived key can be recomputed.

Dependencies/integration: uses `binrw`, `OuterCipher`, padding helpers, `Data`, and KDF parameter serialization.

Risks/test signals: fixed `CONFIG_SIZE` bounds must stay large enough for inner config plus overhead. Header format currently hardcodes scrypt, so adding KDFs changes compatibility surface.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/encryption/outer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/encryption/padding.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/config/encryption/padding.rs

Purpose: fixed-size random padding for config encryption layers.

Important APIs/types/functions: `PADDING_OVERHEAD_PREFIX` is the binary-layout offset for the original-size field. `add_padding` prepends original size and fills remaining bytes with random data. `remove_padding` reads original size, truncates, and returns unpadded data. Errors distinguish too-small targets, missing size header, and invalid original size.

Control flow: callers allocate buffers with prefix room, serialize plaintext, then pad to a target size before encryption. On decrypt, padding is removed before parsing the inner payload.

State and persistence: padding bytes are persisted inside encrypted payloads and hide real config lengths.

Dependencies/integration: uses `binary_layout`, `rand::rng`, and `cryfs_utils::data::Data`.

Risks/test signals: padding randomness is not separately authenticated here; authentication comes from the surrounding AEAD ciphers. No local tests are present in this file, so boundary cases should be covered by encryption tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/encryption/padding.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/loader.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/config/loader.rs

Purpose: high-level config create/load/read-only workflow with version, cipher, blocksize, local-state, and single-client integrity checks.

Important APIs/types/functions: `ConfigLoadError`, `ConfigLoadResult`, `CommandLineFlags`, and public `create`, `load_or_create`, `load_readonly`. Internal `_create`, `_load`, `_check_version`, `_update_version_in_config`, `_check_cipher`, `_check_blocksize`, and `_check_missing_blocks_are_integrity_violations` implement policy.

Control flow: `load_or_create` branches on config file existence. Loading decrypts the file, clones old config, checks/migrates format version, validates expected cipher/blocksize, loads or generates filesystem metadata using the encryption key, enforces single-client mode, saves modified config if read-write, and returns client id.

State and persistence: may create encrypted config files, rewrite version/last-opened/exclusive-client fields, and update local filesystem metadata. Read-only mode suppresses config rewrites.

Dependencies/integration: integrates `CryConfigFile`, `Console`, `PasswordProvider`, `FilesystemMetadata`, `LocalStateDir`, `ClientId`, and current version constants.

Risks/test signals: many error branches are security-sensitive and currently marked TODO for tests. `filename.exists()` races with create/load. Version migration only updates version fields, not data layout beyond supported 0.10 bounds.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/loader.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/mod.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/config/mod.rs

Purpose: public facade for config-related modules.

Important APIs/types/functions: declares `ciphers`, `configfile`, `console`, `creator`, `cryconfig`, `encryption`, `loader`, and `password_provider`. Re-exports `ALL_CIPHERS`, config-file errors/types, `Console`, `ConfigCreateError`, `CryConfig`, `FILESYSTEM_FORMAT_VERSION`, `FilesystemId`, loader APIs, `CommandLineFlags`, `ConfigLoadResult`, and `PasswordProvider`. `FixedPasswordProvider` is re-exported behind `testutils`.

Control flow: no runtime flow; it establishes the public API used by CLI and other crates.

State and persistence: child modules own persistence.

Dependencies/integration: central import point for `cryfs-cli` and tests.

Risks/test signals: facade changes can be breaking across the workspace. Keeping test-only exports feature-gated prevents accidental production dependency on fixed passwords.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/password_provider.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/config/password_provider.rs

Purpose: abstracts password acquisition for existing and new filesystems.

Important APIs/types/functions: `PasswordProvider` has `password_for_existing_filesystem` and `password_for_new_filesystem`. With `testutils`, `FixedPasswordProvider` returns a cloned fixed password for both paths.

Control flow: loader functions call the appropriate method before load or create, then pass the string into config encryption/decryption.

State and persistence: passwords are transient strings; TODO notes they should be protected in memory similarly to encryption keys.

Dependencies/integration: implemented by CLI-utils interactive/noninteractive password providers and used by `loader.rs`.

Risks/test signals: string-based password handling can leave sensitive material in memory. Test provider is correctly feature-gated, reducing risk of accidental production use.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/password_provider.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/lib.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/lib.rs

Purpose: crate root for CryFS config and local-state functionality.

Important APIs/types/functions: forbids unsafe code, exposes `config` and `localstate`, keeps `version` private, and re-exports `config::ALL_CIPHERS` plus `CRYFS_VERSION`.

Control flow: no runtime control flow. Public consumers enter through module APIs.

State and persistence: implemented in submodules.

Dependencies/integration: version assertion enforces Cargo/git consistency. CLI imports `CRYFS_VERSION` and config/local-state APIs from this crate.

Risks/test signals: missing-docs is a TODO. Root-level API is small; detailed risk lives in encryption, loader, and local-state modules.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/localstate/filesystem_metadata.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/localstate/filesystem_metadata.rs

Purpose: local metadata for a known filesystem: this client's id and a salted hash of the filesystem encryption key to detect replacement.

Important APIs/types/functions: `FilesystemMetadataError::EncryptionKeyChanged`, `FilesystemMetadata { my_client_id, encryption_key }`, `load_or_generate`, `_load`, `_generate`, `_save`, `my_client_id`, `SerializedHash`, and client-id serde helpers.

Control flow: `load_or_generate` locates metadata by filesystem id. If present, it hashes the current encryption key with the stored salt and compares. On mismatch, it asks the console unless replacement is allowed; accepted replacements rewrite the stored salted hash. If absent, it generates a new random `ClientId` and salted SHA-512 hash.

State and persistence: stores JSON under `LocalStateDir::for_filesystem_id(...)/metadata`. This is local trust state, not vault data.

Dependencies/integration: uses `Sha512`, `Salt`, `EncryptionKey`, `ClientId`, `FilesystemId`, and `Console`.

Risks/test signals: no atomic write or explicit permissions are used. TODO asks for stronger error typing and tests. Hashing detects changed keys but cannot recover from local-state compromise.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/localstate/filesystem_metadata.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/localstate/local_state_dir.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/localstate/local_state_dir.rs

Purpose: path helper for local CryFS state files.

Important APIs/types/functions: `LocalStateDir { app_dir }`, `new`, `for_filesystem_id`, and `for_vaultdir_metadata`.

Control flow: `for_filesystem_id` creates `<app_dir>/filesystems/<filesystem_id_hex>` and returns it. `for_vaultdir_metadata` creates `<app_dir>` and returns `<app_dir>/vaultdirs_v2.json`.

State and persistence: creates directories as needed. Does not read or write metadata content itself.

Dependencies/integration: used by filesystem metadata and vaultdir metadata modules, and constructed by CLI from the environment local-state directory.

Risks/test signals: directory creation is eager and uses default permissions. TODO notes tests are missing. Path construction relies on stable filesystem-id hex encoding.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/localstate/local_state_dir.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/localstate/mod.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/localstate/mod.rs

Purpose: facade for local-state modules.

Important APIs/types/functions: declares and re-exports `LocalStateDir`, `CheckFilesystemIdError`, `VaultdirMetadata`, and `FilesystemMetadata`.

Control flow: no runtime flow.

State and persistence: child modules persist per-filesystem metadata and vaultdir mappings.

Dependencies/integration: imported by `cryfs-cli` and config loader/creator.

Risks/test signals: small compile-time facade; child modules have the substantive security and persistence risks.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/localstate/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/localstate/vaultdir_metadata.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/localstate/vaultdir_metadata.rs

Purpose: tracks which filesystem id was last seen at each vault directory path, detecting vault replacement at a stable location.

Important APIs/types/functions: `VaultdirMetadata` wraps a flattened `HashMap<PathBuf,VaultdirMetadataEntry>`. Methods `load`, `filesystem_id_for_vaultdir_is_correct`, `update_filesystem_id_for_vaultdir`, and `save` implement persistence. `CheckFilesystemIdError::FilesystemIdIncorrect` reports mismatches.

Control flow: CLI loads metadata, checks the current vault path against the config's filesystem id, optionally asks the user on mismatch, then updates/saves the mapping.

State and persistence: JSON stored at `LocalStateDir::for_vaultdir_metadata()` (`vaultdirs_v2.json`). Writes use `File::create` and pretty JSON.

Dependencies/integration: uses `FilesystemId` hex serde and `LocalStateDir`. The CLI currently performs the check; a TODO suggests config-file based checking in filesystem code may be better.

Risks/test signals: path keys are not canonicalized, so symlinks or relative paths can create separate entries. Writes are non-atomic. Tests are TODO.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/localstate/vaultdir_metadata.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/version.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/version.rs

Purpose: defines this crate's CryFS version constant.

Important APIs/types/functions: `CRYFS_VERSION` is assigned from `cryfs_version::CRYFS_VERSION`.

Control flow: no runtime flow. Loader compares this version against supported filesystem format bounds and CLI displays it.

State and persistence: version string may be written into `created_with_version` and `last_opened_with_version` fields by creator/loader.

Dependencies/integration: re-exported from `lib.rs`, used by `loader.rs` and `cryfs-cli` tests.

Risks/test signals: correctness depends on the `cryfs-version` crate and root version assertion. No direct tests needed beyond version display/config update tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/version.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-filesystem/Cargo.toml -->
# sources/security-integrity/cryfs/crates/cryfs-filesystem/Cargo.toml

Purpose: manifest for `cryfs-filesystem`, the filesystem layer that sits over blob/block stores and `cryfs-rustfs`.

Important APIs/types/functions: package metadata uses workspace fields. Features include default `ancestor_checks_on_move` and `testutils` that enables test utilities in blobstore/rustfs dependencies.

Control flow: manifest dependencies wire async traits, atomic time, blob/block stores, rustfs, fsblobstore, utilities, versioning, futures, libc, maybe-owned, nix user support, log, and tokio sync.

State and persistence: no direct runtime persistence here, but dependencies indicate this crate integrates persisted blob/block storage with filesystem operations.

Dependencies/integration: comments note dependency graph concerns, especially direct blobstore/blockstore dependencies despite fsblobstore. Dev-dependencies enable multi-thread Tokio tests and blobstore testutils.

Risks/test signals: feature-gated ancestor checks are enabled by default, which affects move/rename safety. Manifest TODOs suggest dependency cleanup; no source behavior is visible in this work item.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-filesystem/Cargo.toml -->
