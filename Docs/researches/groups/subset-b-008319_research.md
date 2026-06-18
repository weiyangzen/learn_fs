# subset-b-008319 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/tests/utils/mock_low_level_api.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/tests/utils/mock_low_level_api.rs

Purpose: test-only mock coverage for the rustfs low-level async filesystem trait. It uses `mockall::mock!` to define `MockAsyncFilesystemLL`, implements every `AsyncFilesystemLL` operation, and gives integration tests a full FUSE-like backend surface without mounting a real filesystem implementation.

Important APIs/types/functions: `MockFilesystem` bundles the mock and an `Event` fired when `init` runs. `make_mock_filesystem()` installs default expectations for `init`, `destroy`, and `async_drop_impl`. The generated mock covers metadata, directory, file I/O, xattr, locking, block mapping, ioctl, allocation, lseek, copy range, and macOS-only operations. The file also manually implements `AsyncFilesystemLL` for `AsyncDropArc<MockAsyncFilesystemLL>` by forwarding every call through `Deref`.

Control flow: tests create a mock, configure expectations, wrap it as needed in `AsyncDropGuard`/`AsyncDropArc`, and pass it to backend adapters. Calls reach either mockall expectations directly or the `AsyncDropArc` forwarding layer. `init` triggers a one-shot event so test harnesses can wait until the filesystem is mounted/ready.

State/persistence: all state is in memory inside mockall expectation state and the readiness `Event`. No persistent data is written here. Async cleanup is enforced by the `AsyncDrop` expectation and by `AsyncDropArc` last-reference semantics.

Dependencies/integration: depends on `async_trait`, `mockall`, `cryfs_utils::async_drop`, `cryfs_utils::event::Event`, `PathComponent`, and rustfs common/low-level reply types. It is re-exported by the test utils module for filesystem-driver and runner tests.

Risks: this file mirrors a wide trait; trait signature drift will require synchronized updates in both the mock definition and the forwarding impl. The forwarding impl is repetitive and can hide missed platform-gated methods. Mock defaults expect exactly one init/destroy/drop; tests that intentionally exercise unusual lifetimes must override or account for those expectations.

Test signals: the file itself is test infrastructure. Its strongest signal is compile-time trait conformance against `AsyncFilesystemLL` plus mockall expectation failures in higher-level tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/tests/utils/mock_low_level_api.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/tests/utils/mod.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/tests/utils/mod.rs

Purpose: module aggregator for rustfs test utilities. It keeps internal utility modules private and re-exports the public helpers used by the test suite.

Important APIs/types/functions: re-exports `FilesystemDriver`, `MockAsyncFilesystemLL`, `make_mock_filesystem`, `Runner`, `MockHelper`, `ROOT_INO`, and `assert_request_info_is_correct`.

Control flow: no runtime logic; compilation wires module boundaries. Tests import through this module instead of individual files.

State/persistence: none.

Dependencies/integration: integrates filesystem driver, mock low-level API, fuser runner, mock helper, and request-info assertion utilities. This is the stable facade for test code.

Risks: re-export omissions break downstream tests even when implementation modules compile. The private module list also means adding a helper requires an explicit re-export decision.

Test signals: compile failures reveal missing modules/re-exports; downstream tests exercise the exported utilities.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/tests/utils/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/tests/utils/request_info.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/tests/utils/request_info.rs

Purpose: small assertion helper validating request metadata attached to filesystem operations in tests.

Important APIs/types/functions: `assert_request_info_is_correct(req: &RequestInfo)` compares `req.uid` to `users::get_current_uid()` and `req.gid` to `users::get_effective_gid()`.

Control flow: direct assertions only. PID validation is present as a TODO and commented out because it did not work reliably.

State/persistence: reads process/user identity via the `users` crate; no storage or mutation.

Dependencies/integration: uses rustfs common `Uid`, `Gid`, and `RequestInfo`. Intended for mock expectation callbacks validating FUSE request context.

Risks: effective gid vs current uid assumptions can be environment-sensitive under sudo, containers, or test runners with changed credentials. PID remains unverified.

Test signals: assertion failures in tests indicate request context propagation regressions.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/tests/utils/request_info.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/tempproject/Cargo.toml -->
# sources/security-integrity/cryfs/crates/tempproject/Cargo.toml

Purpose: manifest for the `tempproject` crate, a workspace utility for creating temporary Cargo projects in tests.

Important APIs/types/functions: declares package metadata inherited from the workspace and dependencies on `anyhow`, `assert_cmd`, `is_executable`, `tempfile`, and `thiserror`. Dev dependencies are `indoc` and `predicates`.

Control flow/state: no runtime code, but dependency choices define the crate behavior: temp directories, process execution/assertion, executable discovery, and structured error derivation.

Dependencies/integration: participates in the workspace with shared version/edition/rust-version metadata. It is likely used by integration tests that need to compile generated Rust crates.

Risks: because it shells out to Cargo, workspace dependency resolution and environment `CARGO` path matter. `is_executable` behavior is platform-sensitive.

Test signals: crate tests in `tests/simple.rs` exercise build/run/error behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/tempproject/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/tempproject/src/builder.rs -->
# sources/security-integrity/cryfs/crates/tempproject/src/builder.rs

Purpose: builder-pattern API for constructing a temporary binary Cargo project on disk.

Important APIs/types/functions: `TempProjectBuilder { folder, cargo, main }`; `new()` creates a prefixed `TempDir`; `cargo()` and `main()` store file contents; `build()` writes `Cargo.toml` and `src/main.rs` and returns `TempProject`.

Control flow: builder methods consume and return `Self`. `build()` calls `_build_cargo_toml()` then `_build_main_rs()`. Missing required content panics with explicit messages.

State/persistence: owns a `TempDir`; build writes files into that temp folder. Cleanup is delegated to `TempDir` after the resulting `TempProject` drops.

Dependencies/integration: uses `anyhow::Result`, `tempfile::TempDir`, and `TempProject::new`. It is the public creation path re-exported by `lib.rs`.

Risks: missing `cargo()` or `main()` is a panic, not a recoverable error. `create_dir` for `src` fails if the directory already exists; no support for extra files or library projects.

Test signals: `tests/simple.rs` covers success and panic cases for missing builder fields.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/tempproject/src/builder.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/tempproject/src/lib.rs -->
# sources/security-integrity/cryfs/crates/tempproject/src/lib.rs

Purpose: crate root and public API documentation for temporary Cargo project creation/build/run utilities.

Important APIs/types/functions: enables `#![forbid(unsafe_code)]` and `#![deny(missing_docs)]`; declares `builder` and `project`; re-exports `TempProjectBuilder`, `ProcessError`, and `TempProject`.

Control flow/state: no runtime logic beyond module loading. Documentation examples show creation, running, and error handling.

Dependencies/integration: makes the crate's ergonomic surface a small set of types from internal modules.

Risks: `deny(missing_docs)` means new public APIs must be documented. Docs claim build caching; actual `build_debug/build_release` methods recompute and only `run_*` reliably uses `OnceLock`.

Test signals: doc examples are `no_run`; behavioral tests live in `tests/simple.rs`.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/tempproject/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/tempproject/src/project.rs -->
# sources/security-integrity/cryfs/crates/tempproject/src/project.rs

Purpose: implements build and run operations for temporary Cargo projects and reports process failures with captured output.

Important APIs/types/functions: `ProcessError` stores exit code plus UTF-8 conversion results for stdout/stderr. `TempProject` owns the `TempDir` and separate `OnceLock<Result<PathBuf, ProcessError>>` slots for debug/release executables. `build_debug`, `build_release`, `run_debug`, and `run_release` are the main APIs. `find_single_binary_in()` locates exactly one executable file under the target profile directory.

Control flow: `_build_debug/_build_release` run `env!("CARGO") build` with an explicit temp `target` directory, inspect `assert_cmd` output, and either locate an executable or build `ProcessError`. `run_*` uses `get_or_init` to reuse a cached build result and returns an `assert_cmd::Command` in the project directory.

State/persistence: writes Cargo build artifacts under the temp project's `target` directory. The temp directory persists while `TempProject` is alive. `run_*` caches build results; `build_*` currently computes a fresh result and then ignores `OnceLock::set` failure, so repeated direct build calls may rebuild.

Dependencies/integration: depends on `assert_cmd`, `is_executable`, `tempfile`, `thiserror`, and standard path/process output handling. Used by tests that need a compiled binary path or command assertion object.

Risks: panics if Cargo produces zero or multiple executable files. `env!("CARGO")` is compile-time environment dependent. UTF-8 conversion errors are stored, not rendered as bytes. Direct `build_*` cache behavior differs from documentation.

Test signals: `tests/simple.rs` covers debug/release build success, build failure, runtime failure, and build-then-run combinations.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/tempproject/src/project.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/tempproject/tests/simple.rs -->
# sources/security-integrity/cryfs/crates/tempproject/tests/simple.rs

Purpose: integration tests for `tempproject` covering success, build-time failure, runtime failure, debug/release profiles, and builder edge cases.

Important APIs/types/functions: fixture constructors create successful, compile-failing, and runtime-failing projects. Expectation helpers validate `build_debug`, `build_release`, `run_debug`, and `run_release` behavior.

Control flow: tests are grouped by operation path: build only, run only, and build then run for both debug and release. Edge cases assert panics when required builder fields are absent.

State/persistence: every fixture creates a temp Cargo project and build artifacts under its temp directory. Cargo execution is real, not mocked.

Dependencies/integration: uses `assert_cmd::Command`, `indoc`, `predicates`, and public crate APIs.

Risks: tests depend on a working Rust toolchain and may be slower/flakier than pure unit tests. Compiler diagnostic assertion for `nonexisting_func` is somewhat tied to rustc wording.

Test signals: strong coverage of the crate's intended workflow, but no direct test that repeated `build_*` calls avoid rebuilding.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/tempproject/tests/simple.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/Cargo.toml -->
# sources/security-integrity/cryfs/crates/utils/Cargo.toml

Purpose: manifest for `cryfs-utils`, a shared utility crate used across the CryFS Rust workspace.

Important APIs/types/functions: declares dependencies for async traits, binary serialization (`binrw`), version checks, derivations, futures/tokio, progress/logging, synchronization, random/hex utilities, and optional test utilities. Feature `testutils` enables optional `divrem` and `dtor`; criterion benchmark `path` is registered.

Control flow/state: no runtime code, but feature flags gate test-only APIs such as async-drop map iter/drain and binary helpers.

Dependencies/integration: central workspace crate. `cryfs-version` is a path dependency used by `lib.rs` to assert Cargo/git version alignment.

Risks: utility crates tend to be high blast-radius. Optional dependencies must remain aligned with feature-gated code paths. Tokio features are broad enough for filesystem/time/runtime use.

Test signals: many modules include unit tests; `benches/path.rs` benchmarks path joining.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/benches/path.rs -->
# sources/security-integrity/cryfs/crates/utils/benches/path.rs

Purpose: criterion benchmark comparing `cryfs_utils::path::path_join` against standard `PathBuf` joining strategies.

Important APIs/types/functions: `bench_join(c: &mut Criterion)` benchmarks `path_join`, chained `PathBuf::join`, `PathBuf::extend`, and repeated `PathBuf::push` over absolute and relative paths with double slashes.

Control flow/state: creates black-boxed path inputs, registers four benchmark functions, and uses criterion macros to define the benchmark main.

Dependencies/integration: depends on `criterion`, `std::hint::black_box`, and `cryfs_utils::path::path_join`.

Risks: benchmark inputs include absolute middle components, so behavior follows `PathBuf::push` reset semantics. Results are performance signals only, not correctness proof.

Test signals: complements unit tests in `path/join.rs` by measuring allocation/performance intent.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/benches/path.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/async_drop/async_drop.rs -->
# sources/security-integrity/cryfs/crates/utils/src/async_drop/async_drop.rs

Purpose: defines the core `AsyncDrop` trait for types that need fallible asynchronous cleanup.

Important APIs/types/functions: `#[async_trait] pub trait AsyncDrop { type Error: Debug; async fn async_drop_impl(&mut self) -> Result<(), Self::Error>; }`.

Control flow: implementors put cleanup in `async_drop_impl`; wrappers such as `AsyncDropGuard`, `AsyncDropArc`, maps, and mutex adapters call it.

State/persistence: no storage in this trait. Cleanup semantics depend on implementors and may release filesystem, network, or task resources.

Dependencies/integration: uses `async_trait` and `Debug`. Re-exported by `async_drop/mod.rs`.

Risks: Rust has no native async destructor, so correctness depends on wrappers enforcing explicit calls. Implementor errors propagate through guard APIs.

Test signals: behavior is indirectly tested by all async-drop wrapper tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/async_drop/async_drop.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/async_drop/async_drop_arc.rs -->
# sources/security-integrity/cryfs/crates/utils/src/async_drop/async_drop_arc.rs

Purpose: shared-ownership wrapper for `AsyncDropGuard<T>` that async-drops the inner value only when the last reference is dropped.

Important APIs/types/functions: `AsyncDropArc<T>` stores `Option<Arc<AsyncDropGuard<T>>>`. `new`, associated `clone`, `strong_count`, `into_inner`, `as_ptr`, and `ptr_eq` expose Arc-like behavior while retaining async-drop discipline. `Deref`/`Borrow` expose `T`.

Control flow: `async_drop_impl` takes the Arc. If `Arc::into_inner` succeeds, it calls the inner guard's `async_drop`; otherwise it returns `Ok(())` because another reference remains.

State/persistence: in-memory reference-counted ownership only. `Option` is used to mark destruction and panic on use after drop.

Dependencies/integration: depends on futures `BoxFuture`, `AsyncDrop`, `AsyncDropGuard`, `Arc`, `Deref`, and `Borrow`. Used by mock filesystem sharing and `AsyncDropShared`.

Risks: cloning is an associated function, not `Clone`, so callers must learn the custom API. `into_inner` bypasses async drop and transfers responsibility. Access after async drop panics.

Test signals: unit tests cover creation, cloning, strong count, into-inner single/multiple references, last-reference cleanup, and deref.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/async_drop/async_drop_arc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/async_drop/async_drop_guard.rs -->
# sources/security-integrity/cryfs/crates/utils/src/async_drop/async_drop_guard.rs

Purpose: RAII-like guard that forces explicit asynchronous cleanup and panics if forgotten.

Important APIs/types/functions: `AsyncDropGuard<T>(Option<T>)`; `new`, `new_invalid`, `into_box`, `map_unsafe`, `unsafe_into_inner_dont_drop`, `is_dropped`, and `async_drop`. Implements `Drop`, `Deref`, and `DerefMut`.

Control flow: `async_drop` takes the value, calls `AsyncDrop::async_drop_impl`, and leaves `None` so `Drop` is quiet. If dropped while still `Some`, `safe_panic!` reports a forgotten async drop.

State/persistence: in-memory option tracks live vs dropped state. The wrapped value's own `Drop` runs after `async_drop_impl` because the taken value is dropped at the end of the async cleanup path.

Dependencies/integration: central to every async-drop utility. Uses `safe_panic!` to avoid double-panic aborts.

Risks: `map_unsafe` and `unsafe_into_inner_dont_drop` bypass cleanup guarantees and require careful callers. Forgotten cleanup panics at drop time, which may appear far from the bug.

Test signals: unit tests verify panic-on-forget, async cleanup, sync drop ordering, error propagation, and cleanup despite async-drop errors.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/async_drop/async_drop_guard.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/async_drop/async_drop_tokio_mutex.rs -->
# sources/security-integrity/cryfs/crates/utils/src/async_drop/async_drop_tokio_mutex.rs

Purpose: wraps an `AsyncDropGuard<T>` in `tokio::sync::Mutex` for async interior mutability with proper cleanup.

Important APIs/types/functions: `AsyncDropTokioMutex<T> { v: Option<Mutex<AsyncDropGuard<T>>> }`; `new`, `lock`, and `into_inner`. Implements `AsyncDrop` by taking the mutex, extracting the inner guard, and async-dropping it.

Control flow: users lock to access/mutate the inner value. During async drop, no lock is awaited because ownership of the mutex is consumed.

State/persistence: in-memory mutex state only. `Option` marks destructed state.

Dependencies/integration: used where async-drop values need shared mutable access inside async tasks. Depends on tokio mutex and async-drop primitives.

Risks: if another task holds a lock when outer cleanup is attempted through shared ownership patterns, higher-level code must avoid races. `into_inner` transfers cleanup responsibility.

Test signals: unit tests cover new/lock, mutation, into-inner, and inner cleanup.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/async_drop/async_drop_tokio_mutex.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/async_drop/flatten.rs -->
# sources/security-integrity/cryfs/crates/utils/src/async_drop/flatten.rs

Purpose: combines two fallible async-drop guard results while cleaning up any successfully created guard when the other result failed.

Important APIs/types/functions: `flatten_async_drop<E, T, E1, U, E2>(first, second)` returns both guards on dual success or an error converted into `E`.

Control flow: four match cases handle both-ok, first-ok/second-err, first-err/second-ok, and both-err. On mixed success/failure it async-drops the successful guard before returning the failure.

State/persistence: no persistent state; cleanup side effects belong to dropped guards.

Dependencies/integration: generic over `AsyncDropGuard` values and error conversions. Useful in constructors that allocate two async resources.

Risks: TODOs note error loss: if cleanup fails while returning another error, only one error is reported. When both inputs are errors, the second error is discarded.

Test signals: unit tests cover all four result combinations and verify cleanup counters.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/async_drop/flatten.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/async_drop/hash_map.rs -->
# sources/security-integrity/cryfs/crates/utils/src/async_drop/hash_map.rs

Purpose: `HashMap` container for async-droppable values that cleans all entries concurrently on drop.

Important APIs/types/functions: `AsyncDropHashMap<K,V>` wraps `HashMap<K, AsyncDropGuard<V>>`; exposes `new`, `try_insert`, `remove`, `get`, `get_mut`, `len`, and feature-gated `drain`/`iter`.

Control flow: insertion uses `HashMapExt::try_insert` and rejects duplicate keys with the rejected guard returned in `OccupiedError`. `async_drop_impl` drains values and runs `for_each_unordered` to drop them concurrently.

State/persistence: in-memory map only. Removed/drained values become caller responsibility.

Dependencies/integration: depends on `anyhow`, `HashMapExt`, `OccupiedError`, and `crate::stream::for_each_unordered`.

Risks: duplicate insertion requires the caller to async-drop the rejected value. Concurrent dropping returns the first encountered error depending on stream behavior.

Test signals: unit tests cover empty map, insert/get, duplicate rejection, remove, drop-all, and mutation.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/async_drop/hash_map.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/async_drop/mod.rs -->
# sources/security-integrity/cryfs/crates/utils/src/async_drop/mod.rs

Purpose: module facade for async-drop utilities.

Important APIs/types/functions: re-exports `AsyncDrop`, `AsyncDropGuard`, `AsyncDropArc`, `AsyncDropTokioMutex`, `SyncDrop`, `AsyncDropHashMap`, `with_async_drop`, `flatten_async_drop`, `AsyncDropShared`, and `AsyncDropResult`.

Control flow/state: no runtime logic; establishes public API organization.

Dependencies/integration: downstream crates import most async cleanup helpers through `cryfs_utils::async_drop`.

Risks: adding a utility without re-exporting may hide it from intended users. Re-export names define semver-facing API.

Test signals: compile-time module wiring plus tests in child modules.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/async_drop/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/async_drop/result.rs -->
# sources/security-integrity/cryfs/crates/utils/src/async_drop/result.rs

Purpose: wraps `Result<AsyncDropGuard<T>, E>` so successful values are cleaned up and errors are no-op during async drop.

Important APIs/types/functions: `AsyncDropResult<T,E>` with `new`, `err`, `ok`, `as_inner`, and `into_inner`.

Control flow: `async_drop_impl` matches the inner result; `Ok` calls the guard cleanup, `Err` returns success.

State/persistence: stores the original result in memory. `into_inner` bypasses wrapper cleanup and transfers responsibility for an `Ok` guard.

Dependencies/integration: useful for APIs that need one guard-like value even when construction failed.

Risks: error variant cleanup is intentionally absent; any partially-created resources must already have been handled before wrapping. `ok()` returns `&T`, hiding guard identity.

Test signals: unit tests cover accessors, into-inner for both variants, ok cleanup, and err no-op cleanup.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/async_drop/result.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/async_drop/shared.rs -->
# sources/security-integrity/cryfs/crates/utils/src/async_drop/shared.rs

Purpose: async-drop-aware equivalent of `futures::future::Shared`, allowing a future that returns `AsyncDropGuard<O>` to be cloned and awaited by multiple consumers.

Important APIs/types/functions: `AsyncDropShared<O,Fut>` stores an `AsyncDropArc<Inner<O,Fut>>` plus a waker key. `Inner` holds `UnsafeCell<FutureOrOutput<O,Fut>>` and a `Notifier`. State constants are `IDLE`, `POLLING`, `COMPLETE`, and `POISONED`. Public APIs include `new`, `new_ready`, `peek`, `strong_count`, `ptr_hash`, `ptr_eq`, and associated `clone`.

Control flow: polling checks completion fast path, records the caller waker, atomically claims polling, polls the inner future with notifier waker, stores output as `AsyncDropArc` on readiness, marks complete, wakes waiters, and returns a cloned output guard. Async drop removes registered wakers and async-drops the shared inner only when the last reference releases it.

State/persistence: all state is in memory: atomic state, slab of wakers, and either future or output. If dropped before completion, `Inner::async_drop_impl` awaits the future to obtain and cleanup any async-drop output.

Dependencies/integration: depends on futures task APIs, `slab`, `UnsafeCell`, atomics, mutexes, and async-drop wrappers. Used where multiple tasks need a shared result with deterministic async cleanup.

Risks: this is concurrency-critical unsafe code. Correctness depends on atomic state transitions guarding `UnsafeCell` access. Panics during poll poison the future. Awaiting an uncompleted future during cleanup can run arbitrary async work during drop.

Test signals: extensive tokio tests cover result/future drop ordering, clone polling, shared output, peek, strong counts, pointer equality/hash, unpolled cleanup, clone after completion, repeated poll, and debug.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/async_drop/shared.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/async_drop/sync_drop.rs -->
# sources/security-integrity/cryfs/crates/utils/src/async_drop/sync_drop.rs

Purpose: synchronous adapter that calls `async_drop` from `Drop`, mainly for test convenience.

Important APIs/types/functions: `SyncDrop<T>(Option<AsyncDropGuard<T>>)` with `new`, `into_inner_dont_drop`, `inner`, `Deref`, and `DerefMut`.

Control flow: on drop, if a guard remains, it blocks on `async_drop`. Inside a multi-threaded Tokio runtime it uses `block_in_place` plus `Handle::block_on`; otherwise it uses `futures::executor::block_on`.

State/persistence: owns one optional guard. `into_inner_dont_drop` transfers cleanup responsibility.

Dependencies/integration: adapts async-drop resources to synchronous tests or scopes.

Risks: documented deadlock risk if cleanup needs tasks that cannot progress. `unwrap()` on cleanup errors panics in `Drop`.

Test signals: unit tests cover deref, mutation, inner access, into-inner transfer, runtime drop, and non-runtime drop.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/async_drop/sync_drop.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/async_drop/with.rs -->
# sources/security-integrity/cryfs/crates/utils/src/async_drop/with.rs

Purpose: helper macros/functions that run user work and then always call `async_drop` on a guard.

Important APIs/types/functions: exported macros `with_async_drop_2!` and `with_async_drop_2_infallible!`; function `with_async_drop(value, f)`.

Control flow: callbacks run first and their result is stored; cleanup runs afterward; cleanup errors are propagated or mapped before returning the callback result.

State/persistence: no storage beyond the owned guard. Cleanup side effects belong to the wrapped type.

Dependencies/integration: uses `AsyncDropGuard`, `AsyncDrop`, futures, and `lockable::InfallibleUnwrap` for infallible macro form.

Risks: if both callback and cleanup fail, cleanup error can mask callback result in some paths. TODOs question macro necessity and note friction for synchronous callbacks.

Test signals: tests cover success, callback error still dropping, macro success, and error mapping.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/async_drop/with.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/at_exit.rs -->
# sources/security-integrity/cryfs/crates/utils/src/at_exit.rs

Purpose: signal-driven exit handler that runs callbacks on termination signals and exits immediately on a quick second signal.

Important APIs/types/functions: `AtExitHandler` owns a signal thread `JoinHandle` and `signal_hook::Handle`. Global `DOUBLE_SIGNAL_HANDLER` tracks last termination signal time with a one-second threshold. `AtExitHandler::new` forces the double-signal handler and registers a user callback.

Control flow: `_new` creates `Signals::new(TERM_SIGNALS)`, spawns a named thread, logs received signals, and invokes the callback for each. `Drop` closes the signal handle and joins the thread.

State/persistence: process-global signal registrations and a background thread. No persistent files.

Dependencies/integration: uses `signal-hook`, `LazyLock`, threads, durations, instants, and logging. Integration signal tests are intentionally outside the unit-test binary.

Risks: signal tests can interfere globally, hence separation. Callback panics and `std::process::exit` behavior are TODOs. Drop can block joining the signal thread.

Test signals: local unit test only checks create/drop without signals; comments point to integration tests for real signal delivery.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/at_exit.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/binary.rs -->
# sources/security-integrity/cryfs/crates/utils/src/binary.rs

Purpose: binary serialization/deserialization helpers around `binrw` with strict stream completion and custom field codecs.

Important APIs/types/functions: `BinaryReadExt` adds `deserialize_from_complete_stream` and `deserialize_from_file`; `BinaryWriteExt` adds `serialize_to_stream` and `serialize_to_file`. Helpers encode/decode bool, `HashMap`, null-terminated nonzero byte strings, `NonZeroU32`, and `SystemTime` via internal `TimeSpec`.

Control flow: reads use little endian, improve unexpected EOF context, and call `ensure_stream_is_complete` to reject trailing bytes. File reads return `Ok(None)` on not-found. Writes create/overwrite files and use buffered writers.

State/persistence: serialization writes files when requested; otherwise operates on caller streams. HashMap serialization order is iteration-dependent.

Dependencies/integration: depends on `anyhow`, `binrw`, `itertools`, std IO/path/time, and test-only helper module.

Risks: strict EOF handling is good for integrity but rejects concatenated streams. `read_null_string` requires a null terminator and rejects EOF-terminated strings. `read_timespec/write_timespec` call `stream_position().unwrap()` when constructing custom errors.

Test signals: broad unit tests cover success and failures for stream length, files, bool validation, hashmap lengths, null strings, nonzero integers, and timespec overflow/short data.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/binary.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/concurrent_task.rs -->
# sources/security-integrity/cryfs/crates/utils/src/concurrent_task.rs

Purpose: wrapper around `tokio::spawn` that makes forgetting to await a spawned task a hard failure.

Important APIs/types/functions: `ConcurrentTask<T>` stores `ManuallyDrop<JoinHandle<T>>`; `spawn` creates it; `await_task(self)` consumes the wrapper and returns the join handle future.

Control flow: consuming `await_task` uses `ManuallyDrop::take` so `Drop` does not run. If the wrapper is dropped directly, its `Drop` implementation contains a const panic message.

State/persistence: holds one Tokio join handle; task state lives in Tokio runtime.

Dependencies/integration: useful for structured concurrency in async code.

Risks: Drop panic is severe and can abort if it occurs during unwinding. The comment says compile-time error, but enforcement is via `#[must_use]` on returned future plus runtime/drop panic behavior.

Test signals: tokio test spawns a task, awaits it, and checks result.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/concurrent_task.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/containers.rs -->
# sources/security-integrity/cryfs/crates/utils/src/containers.rs

Purpose: collection extension traits for fallible insertion into `HashMap` and `HashSet`.

Important APIs/types/functions: `HashMapExt::try_insert` returns `&mut V` or `OccupiedError` containing the existing occupied entry and rejected value. `HashSetExt::try_insert` returns an error if the item already exists.

Control flow: HashMap implementation uses entry API. HashSet implementation checks `contains`, then inserts and asserts success.

State/persistence: mutates caller-owned collections only.

Dependencies/integration: `AsyncDropHashMap` depends on the HashMap extension to avoid replacing existing async-drop guards.

Risks: HashSet check-then-insert hashes twice. `OccupiedError` exposes an occupied entry, which can be useful but extends borrow complexity.

Test signals: unit tests cover new insertion, mutable return, duplicate failure, error contents/display, and hashset duplicate handling.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/containers.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/data/data.rs -->
# sources/security-integrity/cryfs/crates/utils/src/data/data.rs

Purpose: owned byte buffer with a logical region window, enabling copy-free shrinking to subregions while retaining ownership.

Important APIs/types/functions: `Data { storage: Vec<u8>, region: Range<usize> }`; `allocate`, `empty`, `len`, `shrink_to_subregion`, `grow_region`, `grow_region_fail_if_reallocation_necessary`, `reserve`, `append_writer`, prefix/suffix availability, `resize`, `into_vec`; `DataAppendWriter` implements `Write`.

Control flow: shrinking translates bounds relative to current region and updates `region`; growing either reserves/reallocates or fails if slack is insufficient. Accessors expose only `storage[region]`. Append writer extends region then copies bytes into the new suffix.

State/persistence: in-memory byte storage. Subregions keep the original allocation alive, which avoids copies but can retain large buffers.

Dependencies/integration: used for data-block manipulation, likely in filesystem/encryption layers. Tests use `DataFixture`.

Risks: invalid ranges panic via invariant assertions. Retained hidden prefix/suffix may waste memory. Several methods are marked TODO for tests.

Test signals: many unit tests cover empty/full data, range forms, nested subregions, availability counts, and out-of-bounds/inverted range panics.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/data/data.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/data/mod.rs -->
# sources/security-integrity/cryfs/crates/utils/src/data/mod.rs

Purpose: data module facade.

Important APIs/types/functions: declares `data` and `zeroed`; re-exports `Data` and `ZeroedData`.

Control flow/state: no runtime logic.

Dependencies/integration: gives callers a compact import path for byte buffers and zeroed wrappers.

Risks: any new data submodule needs explicit exposure here if public.

Test signals: child module tests validate behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/data/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/data/zeroed.rs -->
# sources/security-integrity/cryfs/crates/utils/src/data/zeroed.rs

Purpose: wrapper guaranteeing a mutable byte buffer has been filled with zeroes.

Important APIs/types/functions: `ZeroedData<D>` stores `data: D`; `ZeroedData<Data>::new(len)` allocates zeroed `Data`; generic `fill_with_zeroes(data)` overwrites an existing buffer; `into_inner` returns the buffer.

Control flow: construction either allocates `vec![0; len]` or mutates the supplied buffer with `fill(0)`.

State/persistence: in-memory buffer only. It does not zero on drop; the guarantee is about contents after construction.

Dependencies/integration: useful for security-sensitive buffers where initialized zero contents matter.

Risks: name could be misread as secure memory wiping on drop; it does not provide that. Consuming `into_inner` lets later code mutate bytes.

Test signals: tests cover new length, empty data, zeroing nonzero vectors, and already-zero vectors.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/data/zeroed.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/event.rs -->
# sources/security-integrity/cryfs/crates/utils/src/event.rs

Purpose: cloneable one-shot async event primitive.

Important APIs/types/functions: `Event` wraps `Arc<EventImpl>` containing `AtomicBool triggered` and `tokio::sync::Notify`. APIs are `new`, `Default`, `trigger`, and `wait`.

Control flow: `trigger` atomically flips the flag and notifies all waiters once. `wait` creates a `notified()` future before checking the flag to avoid missed notifications, then awaits only if not triggered.

State/persistence: one in-memory boolean latch; cannot reset.

Dependencies/integration: used by rustfs test mock initialization and other task synchronization points.

Risks: one-shot semantics only. Notify does not store per-event counts; correctness relies on the pre-check notified future pattern.

Test signals: tokio tests cover trigger-before-wait, wait-before-trigger, multiple waiters, idempotent trigger, clone sharing, and default state.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/event.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/lazy_reclaim.rs -->
# sources/security-integrity/cryfs/crates/utils/src/lazy_reclaim.rs

Purpose: lazily initialized shared value that is reclaimed when no `Arc` references remain and recreated on later demand.

Important APIs/types/functions: `LazyReclaim<T> { inner: Mutex<Weak<T>>, init: fn() -> T }`; `const fn new(init)` and `get_or_init`.

Control flow: `get_or_init` locks the weak pointer, attempts `upgrade`, and if it fails creates a new `Arc`, stores a downgraded weak pointer, and returns the new strong reference.

State/persistence: only a `Weak` is retained by the lazy container; actual value lifetime is controlled by external `Arc` holders.

Dependencies/integration: useful for reclaimable caches, pools, or expensive resources.

Risks: init function is a plain `fn`, not a capturing closure. Mutex poisoning panics. A new instance may be created after all references drop, so identity is not stable forever.

Test signals: unit tests cover value access, same instance while held, reinitialization after drop, partial reference retention, static use, and thread safety.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/lazy_reclaim.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/lib.rs -->
# sources/security-integrity/cryfs/crates/utils/src/lib.rs

Purpose: root module for the `cryfs-utils` crate.

Important APIs/types/functions: exposes modules for async drop, exit handling, binary IO, concurrent tasks, containers, data, events, lazy reclaim, multi-receiver oneshot channels, mutex helpers, path utilities, peekable/periodic/progress/stream/threadpool/tmpfile, and test utilities under cfg. It invokes `cryfs_version::assert_cargo_version_equals_git_version!()`.

Control flow/state: no direct runtime flow beyond compile-time/module initialization and version assertion macro expansion.

Dependencies/integration: central import surface for all workspace utilities.

Risks: `forbid(unsafe_code)` and `deny(missing_docs)` are commented out, so unsafe and undocumented public APIs are currently allowed. Public module exposure has high semver impact.

Test signals: child modules provide tests; version assertion catches package metadata mismatches.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/mr_oneshot_channel.rs -->
# sources/security-integrity/cryfs/crates/utils/src/mr_oneshot_channel.rs

Purpose: multi-receiver one-shot channel: a single sender publishes one cloneable value to any number of receivers.

Important APIs/types/functions: `channel<T>() -> (Sender<T>, Receiver<T>)`; `Sender::send(self, value)`; `Sender::subscribe`; `Receiver::recv` and `try_recv`; `RecvError`. Inner state is `Empty`, `Filled(T)`, or `Closed`.

Control flow: sender consumes itself to send, stores value under mutex, then notifies waiters. Dropping an unsent sender marks `Closed`. Receivers create a notification future before checking state to avoid races, clone the filled value, or return `RecvError` if closed.

State/persistence: in-memory mutex-protected state and Notify. Filled values remain stored as long as channel inner exists.

Dependencies/integration: useful for broadcasting one async initialization result.

Risks: `T: Clone` is required for receiving. Sending after non-empty state panics, though consumption normally prevents reuse. Mutex poisoning panics via unwrap.

Test signals: tokio tests cover basic send/recv, multiple receivers, waiting before send, sender drop, try_recv, concurrent receivers, non-cloneable sender intent, and recv after sent.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/mr_oneshot_channel.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/mutex.rs -->
# sources/security-integrity/cryfs/crates/utils/src/mutex.rs

Purpose: helper for locking two `Arc<Mutex<T>>` values in stable pointer order to avoid deadlock from inconsistent lock ordering.

Important APIs/types/functions: `lock_in_ptr_order(first, second)` returns guards in the same order as arguments.

Control flow: obtains raw Arc allocation pointers, asserts they differ, locks lower-address mutex first, then the other, and returns guards mapped to original argument order.

State/persistence: locks caller-owned mutexes; no storage.

Dependencies/integration: useful wherever pairs of shared objects must be mutated together.

Risks: raw pointer ordering is process-local and only prevents deadlocks when all callers use the same convention. Panics on poisoned mutexes and same mutex.

Test signals: unit tests cover both locks, reverse argument order, mutation, and same-mutex panic.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/mutex.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/panic.rs -->
# sources/security-integrity/cryfs/crates/utils/src/panic.rs

Purpose: defines `safe_panic!`, a panic macro that avoids aborting from double panic during unwinding.

Important APIs/types/functions: exported `safe_panic!` checks `std::thread::panicking()`. If already panicking, it prints to stderr; otherwise it calls `panic!`.

Control flow: macro expands inline at call sites. It is used by `AsyncDropGuard::drop` where panicking during cleanup diagnostics could otherwise double-panic.

State/persistence: no persistent state; may write to stderr.

Dependencies/integration: exported at crate root by `#[macro_export]`, despite module being private in `lib.rs`.

Risks: during unwinding it logs instead of panicking, so tests may need stderr inspection to catch secondary errors. In normal flow it still panics.

Test signals: unit tests cover normal panic, formatting, and no abort during a caught panic with a destructor call.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/panic.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/path/component.rs -->
# sources/security-integrity/cryfs/crates/utils/src/path/component.rs

Purpose: strict path component types for validated single components of absolute paths.

Important APIs/types/functions: borrowed `PathComponent` is a transparent `str` wrapper; owned `PathComponentBuf` stores `String`. APIs include `try_from_str`, `try_from_string`, `as_str`, conversions from/to `str`, `OsStr`, `String`, `OsString`, `Borrow`, `Deref`, `ToOwned`, and `FromStr`.

Control flow: constructors validate invariants: UTF-8, non-empty, no `/`, `\`, or null, and not `.` or `..`. Internal unchecked constructors are used after trusted validation by iterators.

State/persistence: stores or borrows component text only.

Dependencies/integration: used by rustfs APIs and `AbsolutePath` iteration to avoid invalid path names crossing filesystem layers.

Risks: uses unsafe transparent cast from `str` to `PathComponent`; soundness depends on `repr(transparent)` and invariant discipline. `.` and `..` map to `NotAbsolute`, which may be semantically surprising for component parsing.

Test signals: extensive tests cover valid conversions, invalid empty/dot/slash/backslash/null/non-UTF8 cases, special characters, Unicode, unchecked helpers, and owned/borrowed conversions.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/path/component.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/path/error.rs -->
# sources/security-integrity/cryfs/crates/utils/src/path/error.rs

Purpose: shared parse error enum for path and path-component validation.

Important APIs/types/functions: `ParsePathError` variants: `NotAbsolute`, `EmptyComponent`, `NotUtf8`, and `InvalidFormat`; derives `Debug`, `Error`, `PartialEq`, and `Eq`.

Control flow/state: no runtime logic beyond formatting errors via `thiserror`.

Dependencies/integration: consumed by `PathComponent`, `PathComponentBuf`, and likely `AbsolutePath` parsing.

Risks: small variant set may collapse distinct invalid cases, limiting diagnostics. `NotAbsolute` is also used for `.`/`..` components.

Test signals: asserted throughout component and iterator/path tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/path/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/path/iter.rs -->
# sources/security-integrity/cryfs/crates/utils/src/path/iter.rs

Purpose: iterator over components of a validated `AbsolutePath`.

Important APIs/types/functions: `ComponentIter<'a> { path: &'a str }`; implements `Iterator`, `DoubleEndedIterator`, `FusedIterator`, and `ExactSizeIterator`.

Control flow: `new` strips the leading slash. `next` splits on first slash; `next_back` splits on last slash; both use `PathComponent::new_assert_invariants` because the source absolute path should already be valid. `size_hint`, `count`, and `last` are specialized.

State/persistence: iterator mutates its remaining string slice only.

Dependencies/integration: returned by `AbsolutePath::iter()` and feeds filesystem path traversal code.

Risks: relies on `AbsolutePath` invariants to avoid panics in `new_assert_invariants`. Double-ended iteration logic assumes no empty components.

Test signals: parameterized tests cover root, one/multiple components, Unicode, forward/backward iteration, len/count/size_hint, next, next_back, last, and fused behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/path/iter.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/path/join.rs -->
# sources/security-integrity/cryfs/crates/utils/src/path/join.rs

Purpose: allocation-conscious helper to join multiple `Path` components with standard `PathBuf::push` semantics.

Important APIs/types/functions: `path_join(components: &[&Path]) -> PathBuf`.

Control flow: precomputes approximate capacity by summing component OS string lengths plus separators, creates `PathBuf::with_capacity`, then pushes each component in order. Absolute later components reset prior path just like `PathBuf::push`.

State/persistence: returns a new `PathBuf`; no external state.

Dependencies/integration: benchmarked in `benches/path.rs`; public through `path/mod.rs`.

Risks: capacity calculation uses `OsStrExt::len`-like API and is only a performance hint. Semantics intentionally match `PathBuf::join`, including absolute component replacement, which may surprise callers expecting concatenation.

Test signals: exhaustive nested tests compare zero to four components against chained standard joins over empty, root, absolute, relative, and double-slash paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/path/join.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/path/mod.rs -->
# sources/security-integrity/cryfs/crates/utils/src/path/mod.rs

Purpose: public facade for path utilities.

Important APIs/types/functions: declares `component`, `path`, `error`, `iter`, and `join`; re-exports `PathComponent`, `PathComponentBuf`, `AbsolutePath`, `AbsolutePathBuf`, `ParsePathError`, and `path_join`.

Control flow/state: no runtime logic; defines public module surface.

Dependencies/integration: lets callers import validated path types and join helper from `cryfs_utils::path`.

Risks: the unlisted `path.rs` module is an important dependency even though not part of this work item. Public re-exports are semver-sensitive.

Test signals: child modules provide validation and join tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/path/mod.rs -->
