# subset-b-008320 Research

Grouped research for CryFS Rust utility modules, legacy CI/build/package helpers, and old C++ blockstore interfaces/implementations. Each source section preserves the source path in its title and uses deterministic delimiters for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/path/path.rs -->
# sources/security-integrity/cryfs/crates/utils/src/path/path.rs

Purpose: Defines `AbsolutePath` and `AbsolutePathBuf`, CryFS UTF-8-only absolute path types that enforce normalized Unix-style path invariants stronger than `std::path::Path`. The borrowed `AbsolutePath` is a transparent wrapper over `str`; the owned `AbsolutePathBuf` stores a `String` and derefs back to the borrowed type.

Important APIs and types: `AbsolutePath::try_from_str`, `root`, `is_root`, `join`, `as_str`, `is_ancestor_of`, `iter`, `split_last`, and `AbsolutePathBuf::root`, `root_with_capacity`, `try_from_string`, `push`, `push_all` are the main surface. The module implements `TryFrom<&str>`, `TryFrom<&std::path::Path>`, `TryFrom<String>`, `TryFrom<std::path::PathBuf>`, `FromStr`, `Borrow`, `Deref`, `AsRef`, `From`, `ToOwned`, and `IntoIterator`. It depends on `PathComponent`, `ParsePathError`, and `ComponentIter`.

Control flow: Parsing special-cases `/`, then checks the first character for absolute-path syntax and iterates UTF-8 char indices looking for slash, backslash, and NUL. Every component between slashes is validated through `PathComponent::check_invariants_except_contains_slash_or_null`; that delegates rejection of empty, `.`, and `..` components. `join` builds a pre-sized root buffer, appends the existing path with `push_all`, appends one component, and asserts the expected length. `split_last` finds the final slash, handles the single-component root-parent case, and re-wraps parent and child with invariant assertions.

State and persistence behavior: There is no external persistence. State is the path string itself, and most conversions avoid allocation for borrowed paths by using `repr(transparent)` plus unsafe pointer casting after validation. Owned paths can be converted into `String` or `PathBuf`. `push` preserves invariants for valid components, while `push_all` can append another absolute path to a non-root base.

Dependencies and integration points: This file is part of the `cryfs_utils::path` module and is intended as a safer path carrier for filesystem-facing CryFS code. It integrates with Rust standard path conversions for OS boundaries but rejects non-UTF-8 paths. Component iteration is shared with the path iterator module.

Risks: `new_without_invariant_check` and `AbsolutePathBuf::new_without_invariant_check` are unsafe-by-convention escape hatches and must only be called after validation. `is_ancestor_of` deliberately treats a path as not its own ancestor and requires a slash boundary after the prefix. The `push_all_root_onto_path` test expects `/foo/`, which violates the documented no-trailing-slash invariant, so callers should not treat `push_all` as a general invariant-preserving composition operation when the appended path is root. Windows-style paths are intentionally rejected or treated as invalid format when backslashes appear.

Test signals: The in-file tests cover root handling, pushing, all conversion traits, non-UTF-8 OS paths, NUL and backslash rejection, double/trailing slash rejection, dot-dot and dot components, special UTF-8 characters, `split_last`, iterator output, `join`, `is_ancestor_of`, root capacity, and `push_all` behavior.

Source-read signal: Read `sources/security-integrity/cryfs/crates/utils/src/path/path.rs` completely for this pass (1061 lines, 34847 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/path/path.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/peekable.rs -->
# sources/security-integrity/cryfs/crates/utils/src/peekable.rs

Purpose: Adds a tiny readability extension to Rust `std::iter::Peekable` iterators: an `is_empty` method that checks whether more items remain without consuming an item.

Important APIs and types: The public trait is `PeekableExt` with `fn is_empty(&mut self) -> bool`. It is implemented for `Peekable<T>` where `T: Iterator`.

Control flow: `is_empty` calls `self.peek().is_none()`. Because `peek` may fill the peek cache, the method needs `&mut self`, but it leaves the next item available for later `next`.

State and persistence behavior: There is no persistence. Runtime state is only the standard `Peekable` internal cache; repeated calls may keep a peeked value cached but do not advance the iterator.

Dependencies and integration points: The module depends only on `std::iter::Peekable`. It is a utility for parser-style code where checking exhaustion reads better as `iter.is_empty()` than `iter.peek().is_none()`.

Risks: The trait name overlaps conceptually with collection `is_empty`, but the mutable receiver is required by `Peekable::peek`. It cannot be called on arbitrary iterators until they are converted to `peekable()`.

Test signals: Unit tests cover empty iterators, non-empty iterators, exhaustion after consuming all elements, repeated non-consuming checks, and preserving the first element after `is_empty`.

Source-read signal: Read `sources/security-integrity/cryfs/crates/utils/src/peekable.rs` completely for this pass (76 lines, 2027 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/peekable.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/periodic_task.rs -->
# sources/security-integrity/cryfs/crates/utils/src/periodic_task.rs

Purpose: Implements an async periodic background task that runs a user-supplied async closure after each interval while the owning `PeriodicTask` is alive. It integrates with the crate's `AsyncDropGuard` cleanup pattern.

Important APIs and types: `PeriodicTask::spawn(name, interval, task)` returns `AsyncDropGuard<PeriodicTask>`. `PeriodicTask::terminate` cancels future iterations and awaits the join handle. The private `PeriodicTaskImplTerminate` trait type-erases cancellation and task naming; `PeriodicTaskImpl<T, F>` stores the task closure, interval, name, and `CancellationToken`.

Control flow: `spawn` builds an `Arc<PeriodicTaskImpl>`, starts `_run`, and stores the join handle. `_run` loops in a tokio task with `select!` between `CancellationToken::cancelled()` and `tokio::time::sleep(interval)`. On each sleep, it awaits the user task, logs `Err`, and continues. `terminate` cancels the token and awaits the join handle once. `AsyncDrop::async_drop_impl` delegates to `terminate`.

State and persistence behavior: State is in memory only: cancellation token, join handle, task closure, and name. Termination does not abort an already-running iteration; it only prevents future sleeps/tasks after the current await completes. If `terminate` already joined, `join_handle` is `None` and later cleanup is idempotent.

Dependencies and integration points: Uses `tokio` tasks, `tokio::select!`, `tokio_util::sync::CancellationToken`, `anyhow::Result`, `async_trait`, the crate `async_drop` module, and `log`. Consumers must run on a tokio runtime, and docs warn that synchronous drop/blocking async-drop behavior can deadlock on a single-thread runtime.

Risks: Task errors are logged but not surfaced to the owner. A panic inside the spawned task ends the background task; because termination awaits the join handle only when cleanup happens, panics can be delayed or under-tested. Long-running task iterations delay shutdown. The closure is `Fn + Sync` rather than `FnMut`, so mutable periodic state needs interior mutability.

Test signals: Tokio tests cover empty tasks, repeated execution, explicit termination stopping later runs, async drop stopping later runs, and current behavior for erroring or panicking task closures.

Source-read signal: Read `sources/security-integrity/cryfs/crates/utils/src/periodic_task.rs` completely for this pass (263 lines, 9194 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/periodic_task.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/progress.rs -->
# sources/security-integrity/cryfs/crates/utils/src/progress.rs

Purpose: Provides an abstraction over interactive progress indicators so application code can create spinners/progress bars without binding directly to console output. It offers console implementations backed by `indicatif` and silent no-op implementations for tests or non-interactive modes.

Important APIs and types: `ProgressBarManager` creates `Spinner` and `Progress` instances. `ConsoleProgressBarManager` creates `ConsoleSpinner` and `ConsoleProgress`; `SilentProgressBarManager` creates `SilentSpinner` and `SilentProgress`. `Spinner::finish` consumes the spinner, while `Progress` supports `inc`, `inc_length`, and consuming `finish`.

Control flow: Console constructors create an `indicatif::ProgressBar`, set messages and styles, enable steady ticking for spinners, and wrap a `ConsoleProgressImpl` in an outer `Arc`. Increment methods forward to the inner indicatif progress bar. Finishing attempts `Arc::into_inner`, enforcing that no clones remain, then drops the implementation. `ConsoleProgressImpl::drop` calls `finish_with_message`.

State and persistence behavior: Runtime state is the shared progress bar and static message. There is no persistence. The extra `Arc` is load-bearing because `indicatif::ProgressBar` is itself cloneable; the wrapper wants finish/drop side effects only when the final user clone is consumed.

Dependencies and integration points: Depends on `indicatif`, `Arc`, and `Duration`. The manager traits let higher-level CryFS code be generic over console and silent progress behavior.

Risks: `finish` panics if clones still exist, so users must coordinate clone lifetimes. Console styling unwraps template construction, which is acceptable for fixed templates but would panic if changed to invalid templates. Silent implementations intentionally discard all progress information, so tests using them only validate call safety, not display correctness.

Test signals: Unit tests focus on silent spinner/progress behavior, clone/copy behavior, manager factory output, and no-op increments/finish. Console behavior is not directly asserted beyond compile-time integration.

Source-read signal: Read `sources/security-integrity/cryfs/crates/utils/src/progress.rs` completely for this pass (271 lines, 8132 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/progress.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/stream.rs -->
# sources/security-integrity/cryfs/crates/utils/src/stream.rs

Purpose: Supplies async stream helpers that process every item even when failures occur, returning the first error while logging later errors. This is useful for cleanup or batch operations where fail-fast behavior would leave work unattempted.

Important APIs and types: `run_to_completion<E>` accepts a `Stream<Item = Result<(), E>>` and returns `Result<(), E>`. `for_each_unordered<T, E, F>` maps an iterator into a `FuturesUnordered` of async operations and delegates to `run_to_completion`.

Control flow: `run_to_completion` filters successful results out of the stream, pins the resulting error stream, stores the first error, logs subsequent errors, and continues polling until exhaustion. At the end it returns the saved first error or `Ok(())`. `for_each_unordered` collects all futures immediately, so all work can run concurrently, then drains that unordered stream.

State and persistence behavior: There is no persistence. In-memory state is the first error slot and the futures/stream being polled. Later errors are only observable via logs.

Dependencies and integration points: Uses `futures::stream`, `FuturesUnordered`, `StreamExt`, `future::ready`, `anyhow::Result` type naming, and the `log` crate. It fills the niche that `try_for_each_concurrent` does not because it avoids early cancellation.

Risks: Only the first error is returned; subsequent failures are lossy except for logs. `for_each_unordered` has no concurrency limit and collects every future, so very large iterators may create too much pending work. Because all futures are created upfront, side effects can start broadly once polled.

Test signals: Tokio tests cover all-success streams, single and multiple errors, empty streams, unordered iterator processing success, first-error return, and empty iterators.

Source-read signal: Read `sources/security-integrity/cryfs/crates/utils/src/stream.rs` completely for this pass (152 lines, 5013 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/stream.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/testutils/asserts.rs -->
# sources/security-integrity/cryfs/crates/utils/src/testutils/asserts.rs

Purpose: Provides test assertion helpers for unordered vector equality and byte-slice range equality with clearer failure output than raw `assert_eq`.

Important APIs and types: `assert_unordered_vec_eq<T: Eq + Ord + Debug>` sorts both vectors, compares them, and reports `both`, `left only`, and `right only` partitions on mismatch. `assert_data_range_eq` applies a `RangeBounds<usize>` to two byte slices and compares the selected ranges. Private helpers are `difference_partition` and `_apply_bound`.

Control flow: The unordered assertion sorts inputs, then if they differ calls `difference_partition`, which retains only elements absent from the right side while removing matched right-side entries into `both`. Range comparison translates inclusive, exclusive, and unbounded bounds to slice indices, then slices both buffers.

State and persistence behavior: There is no persistence. Both unordered inputs are consumed and sorted, and `difference_partition` destructively removes matching right-hand elements to preserve duplicate-count semantics.

Dependencies and integration points: Used by tests elsewhere in CryFS utilities. It depends only on standard `Debug`, `RangeBounds`, and `Bound`.

Risks: Sorting means `T` must implement `Ord`, even though difference partition itself only needs equality. `_apply_bound` lets normal slice indexing panic on out-of-range or invalid ranges; this is acceptable for assertion helpers but should not be used as validation logic. Duplicate reporting is count-aware but not optimized for large vectors because it linearly searches the right side.

Test signals: Unit tests exercise empty inputs, left-only, right-only, both sides, mixed partitions, and duplicate element accounting. There are no explicit tests for `_apply_bound` range variants in this file.

Source-read signal: Read `sources/security-integrity/cryfs/crates/utils/src/testutils/asserts.rs` completely for this pass (155 lines, 5240 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/testutils/asserts.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/testutils/data_fixture.rs -->
# sources/security-integrity/cryfs/crates/utils/src/testutils/data_fixture.rs

Purpose: Implements `DataFixture`, a reproducible pseudo-random byte stream generator for tests that can efficiently fill arbitrary offsets without generating all preceding bytes.

Important APIs and types: `DataFixture::new(seed)`, `generate(offset, dest)`, and `get(size)` are the public surface. Private helpers include `generate_block` and `subslices`. The fixed block size is 2 KiB.

Control flow: Construction runs the user seed once through `SmallRng` so nearby seeds diverge before block-index arithmetic is used. `generate` computes the start and end block indices for the requested offset/length, splits the destination into a possibly short first slice and full-size following slices, then uses Rayon parallel iteration to fill each slice. `generate_block` seeds `SmallRng` with `self.seed + block_index`, generates enough bytes rounded up to an 8-byte multiple, and copies the requested in-block range. `get` allocates a vector and calls `generate(0, ...)`.

State and persistence behavior: The only persistent object state is the derived seed. Generated data is deterministic for a given seed, offset, and length, regardless of how requests are chunked. No files or global state are touched.

Dependencies and integration points: Depends on `rand::SmallRng`, `SeedableRng`, `Rng`, `divrem::DivCeil`, and `rayon`. It is a test utility for storage, block, stream, and encryption-style tests that need repeatable nontrivial data.

Risks: Parallel fill is deterministic because each block has its own seed, but it still depends on exact `SmallRng` algorithm stability for byte-for-byte fixtures. `generate_block` allocates a temporary vector per block and rounds to 64-bit fill granularity. `subslices` always returns a first slice, including an empty first block when the requested first block size is zero; current callers avoid problematic non-empty zero-first cases. Assertions guard invalid internal offsets.

Test signals: Tests verify different seeds differ, same seeds match, empty and one-byte generation, expected count of zero bytes in 1 MiB, many section sizes producing the same output as one whole generation, `get(0)`, one-byte `get`, and `get` matching `generate`.

Source-read signal: Read `sources/security-integrity/cryfs/crates/utils/src/testutils/data_fixture.rs` completely for this pass (275 lines, 10201 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/testutils/data_fixture.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/testutils/mod.rs -->
# sources/security-integrity/cryfs/crates/utils/src/testutils/mod.rs

Purpose: Exposes the test utility submodules from the `cryfs_utils::testutils` namespace.

Important APIs and types: It declares `pub mod asserts;`, `pub mod data_fixture;`, and `pub mod static_drop;`.

Control flow: There is no runtime control flow; this is a module wiring file.

State and persistence behavior: There is no state or persistence.

Dependencies and integration points: Downstream tests use this module to reach custom assertions, deterministic data fixtures, and static cleanup helpers when the crate's `testutils` feature is enabled.

Risks: Any module added here becomes part of the testutils public module layout. Removing or renaming exports would break tests or external users that depend on the feature.

Test signals: This file has no local tests; coverage comes from each exported module and integration tests that import through `cryfs_utils::testutils`.

Source-read signal: Read `sources/security-integrity/cryfs/crates/utils/src/testutils/mod.rs` completely for this pass (3 lines, 60 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/testutils/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/testutils/static_drop.rs -->
# sources/security-integrity/cryfs/crates/utils/src/testutils/static_drop.rs

Purpose: Implements `StaticDrop<T>`, a test-focused wrapper that runs `Drop` for values stored in Rust statics at process exit. It addresses lazy static resources such as `TempDir` or child-process handles whose destructors would otherwise be skipped.

Important APIs and types: `StaticDrop::new(value)` registers a heap-stable `T`; `Deref` exposes `&T`; `Drop` deregisters normally dropped wrappers. Private global state is `REGISTRY: Mutex<Vec<Entry>>`, where `Entry` stores a type-erased pointer and an unsafe drop function. The `cleanup_leaked_statics` function is registered with `dtor::dtor(unsafe, method = at_binary_exit)`.

Control flow: Construction boxes `T`, stores the raw pointer and a monomorphized drop closure in the registry, and returns the wrapper. Normal `Drop` finds its pointer in the registry, removes it with `swap_remove`, then manually drops the box. At binary exit, the destructor takes the entire registry, iterates remaining entries, and invokes each drop function inside `catch_unwind` so one panicking destructor does not prevent later cleanup.

State and persistence behavior: State is process-global registry memory plus each wrapper's heap allocation. Exit-time cleanup can cause filesystem or process side effects depending on `T::drop`. It is registered through `atexit`, so it runs on normal return and `std::process::exit`, but not abort, `_exit`, or hard signals.

Dependencies and integration points: Uses `dtor`, `Mutex`, `ManuallyDrop`, raw pointers, and lazy-static patterns such as `LazyLock`. It is intentionally in `testutils` and documented as not a production resource ownership pattern.

Risks: The implementation uses unsafe type-erased drop pointers; correctness relies on the boxed allocation remaining stable and each entry being dropped exactly once. There is no ordering guarantee among static drops or with other live threads at process exit. Async cleanup is unsupported. Signal-based exits do not run this destructor.

Test signals: Unit tests validate normal drop, deref behavior through `LazyLock`, move stability, independent registry entries, `Send`/`Sync` bounds, and no double-drop after normal cleanup. Integration tests in this subset verify process-exit behavior and panic isolation.

Source-read signal: Read `sources/security-integrity/cryfs/crates/utils/src/testutils/static_drop.rs` completely for this pass (269 lines, 10588 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/testutils/static_drop.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/threadpool.rs -->
# sources/security-integrity/cryfs/crates/utils/src/threadpool.rs

Purpose: Wraps a Rayon thread pool so CPU-bound closures can be spawned from async code and awaited through a Tokio oneshot channel.

Important APIs and types: `ThreadPool::new(name)`, `new_with_num_threads(name, num_threads)`, and `execute_job<R>(job)` form the public API. Private `num_threads` uses `std::thread::available_parallelism`.

Control flow: Construction builds a Rayon `ThreadPool` with named worker threads. `execute_job` creates a Tokio oneshot channel, spawns a FIFO Rayon job that runs the closure and sends the result, then awaits the receiver. `num_threads` logs detected parallelism or warns and falls back to 2.

State and persistence behavior: State is in memory: the Rayon pool and queued jobs. There is no persistence. Job panics cause sender drop or send failure, and the await path reports `"Thread pool task panicked"`.

Dependencies and integration points: Depends on `rayon`, `tokio::sync::oneshot`, `anyhow::Result`, `futures` in tests, and logging. It supports code paths that cannot use `tokio::task::spawn_blocking`, including tests that call it from `futures::executor::block_on`.

Risks: `execute_job` requires `'static` closures and `Send + Debug` return values. It unwraps `sender.send`, so if the receiver is dropped before completion the Rayon job panics. There is no cancellation or backpressure beyond the Rayon queue. The `Debug` bound is not used by the implementation.

Test signals: Tests cover simple/computed/string/vector returns, captured environment, sequential and concurrent jobs, shared atomics, blocking operations, pool reuse, at least one detected thread, explicit two-thread barrier parallelism, and use from `futures::executor::block_on`.

Source-read signal: Read `sources/security-integrity/cryfs/crates/utils/src/threadpool.rs` completely for this pass (259 lines, 8251 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/threadpool.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/tmpfile.rs -->
# sources/security-integrity/cryfs/crates/utils/src/tmpfile.rs

Purpose: Provides `TempFile`, a minimal RAII wrapper that creates a named temporary file and deletes it when the wrapper is dropped.

Important APIs and types: `TempFile::create(path)`, `TempFile::create_async(path)`, and `path()` are the public methods. The type stores a `PathBuf`.

Control flow: Synchronous creation uses `std::fs::File::create`; async creation uses `tokio::fs::File::create`. Both store the path after successful creation. `Drop` calls `std::fs::remove_file(&self.path).unwrap()`.

State and persistence behavior: The file exists on disk while the wrapper is alive and is removed during drop. The wrapper does not keep the file handle open; it only owns the path cleanup obligation.

Dependencies and integration points: Depends on standard filesystem APIs, `tokio::fs` for async creation, and `anyhow::Result`. Tests use `tempfile::TempDir`.

Risks: Drop panics if the file was already removed, permissions changed, or cleanup otherwise fails. Because no handle is kept open, other code can modify or remove the file behind the wrapper. `File::create` truncates existing files, so callers must avoid passing important paths.

Test signals: Tests verify sync and async creation, `path()` identity, and deletion after drop.

Source-read signal: Read `sources/security-integrity/cryfs/crates/utils/src/tmpfile.rs` completely for this pass (124 lines, 3398 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/src/tmpfile.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/tests/at_exit_signals.rs -->
# sources/security-integrity/cryfs/crates/utils/tests/at_exit_signals.rs

Purpose: Integration-tests `AtExitHandler` behavior for process-wide termination signals (`SIGTERM`, `SIGINT`, and `SIGQUIT`). The test binary isolates signal raising from the rest of the suite.

Important APIs and types: It uses `cryfs_utils::at_exit::AtExitHandler`, `signal_hook` signal constants, `libc::raise`, channels, barriers, and a module-level `LOCK`. `signal_test` serializes each signal scenario and sleeps afterward.

Control flow: Each test acquires the global mutex, installs one or more handlers, raises a signal with `libc::raise`, waits for channel/barrier evidence, then sleeps 1.5 seconds to avoid the double-signal detector threshold in `cryfs_utils::at_exit`. Tests cover individual signals, multiple separated signals, complex callback payloads, multiple handlers, dropping a handler before a later signal, and handler thread naming.

State and persistence behavior: State is process-wide signal handler registration and per-test channel/barrier state. No files are persisted. Because `AtExitHandler` is global/process-affecting, tests are deliberately serialized even within this isolated integration binary.

Dependencies and integration points: This file validates the signal path used by shutdown/cleanup handling in the utilities crate. It complements process-exit tests and any cleanup mechanisms that rely on `AtExitHandler`.

Risks: Signal tests are inherently timing-sensitive and process-global. If another test or library registers competing signal iterators for the same signals in this binary, delivery semantics could change. The explicit sleep makes the suite slower but avoids a hard process exit from the double-signal guard.

Test signals: Evidence is channel receipt within 10 seconds, two receipts for two separated signals, barrier completion for three handlers, absence of callback after drop, and thread name equal to `atexit:my-custom-handler`.

Source-read signal: Read `sources/security-integrity/cryfs/crates/utils/tests/at_exit_signals.rs` completely for this pass (203 lines, 5947 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/tests/at_exit_signals.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/tests/static_drop_process_exit.rs -->
# sources/security-integrity/cryfs/crates/utils/tests/static_drop_process_exit.rs

Purpose: Integration-tests `StaticDrop` behavior that unit tests cannot observe: whether registered static values are dropped when a process exits via `std::process::exit`, whether all entries run, and whether panic in one `Drop` does not stop siblings.

Important APIs and types: Uses `StaticDrop`, `LazyLock`, `TempDir`, `Command`, `Output`, environment variables `STATIC_DROP_PROCESS_EXIT_CHILD` and `STATIC_DROP_SENTINEL_DIR`, plus sentinel helper types `DropSentinel` and `PanicAfterWritingSentinel`.

Control flow: Each test has parent and child roles. The parent creates a temp directory, spawns the same test binary filtered to one exact test with child env vars, and inspects stdout or sentinel files after the child exits. The child initializes one or more lazy statics containing `StaticDrop` wrappers and exits with `process::exit(0)`. The panic test writes a sentinel and panics during one destructor; the parent still expects all sentinels and a successful child status.

State and persistence behavior: Parent-owned temp directories and child-written sentinel files are the observable persistence mechanism. The single-tempdir test prints the child tempdir path before exit, and the parent asserts that directory has been removed by `TempDir::drop`.

Dependencies and integration points: Requires the crate `testutils` feature. It validates the `dtor(at_binary_exit)` path in `static_drop.rs`, especially with libtest-style process exits.

Risks: The tests rely on spawning the current test executable and exact test-name filtering, so harness behavior matters. They assume filesystem side effects are visible after child termination. The child role returns `!` through `process::exit`, so forgetting an early return in parent/child branching would run parent assertions in the child.

Test signals: Child exit success, missing tempdir after process exit, sentinel files `a`, `b`, and `c` existing for multiple entries, and all sentinels still existing when one destructor panics.

Source-read signal: Read `sources/security-integrity/cryfs/crates/utils/tests/static_drop_process_exit.rs` completely for this pass (233 lines, 8110 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/utils/tests/static_drop_process_exit.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/.github/workflows/actions/install_local_dependencies/action.yaml -->
# sources/security-integrity/cryfs/old-cpp/.github/workflows/actions/install_local_dependencies/action.yaml

Purpose: Composite GitHub Action that manually builds and installs legacy C++ dependencies from source on CI when the matrix requests local-system dependency coverage.

Important APIs and types: The action has no inputs. Its bash script determines `NUMCORES`, downloads range-v3 0.11.0, spdlog 1.8.5, and Boost 1.75.0, validates hard-coded SHA-512 sums, builds with CMake or Boost.Build, and installs with `sudo make install` or `sudo ./b2 ... --prefix=/usr install`.

Control flow: The script runs with `set -v`, detects core count using `nproc` with `sysctl` fallback, then performs download, checksum, extraction, build, install, and cleanup for range-v3 and spdlog. It then downloads Boost from SourceForge, verifies checksum, bootstraps selected libraries, and installs shared PIC libraries to `/usr`.

State and persistence behavior: It mutates the CI runner by installing headers/libraries into system locations. Temporary tarballs and source directories are created under `~` and mostly removed. Failed checksum validation exits the job.

Dependencies and integration points: Used by `main.yaml` local-dependencies matrix jobs with `DependenciesFromLocalSystem.cmake`. It assumes `wget`, `sha512sum`, `tar`, CMake, Make, sudo, and compiler toolchains are present.

Risks: Source URLs and checksums are pinned but rely on network availability and SourceForge redirect behavior. Installing into `/usr` can affect later build discovery and cache isolation. The bash test `[ ! -n "$NUMCORES" ]` is old style but functional. Dependencies are not cached despite a TODO, so this path is slow.

Test signals: CI success through this action is the signal: correct checksums, successful configure/build/install, and later CMake local dependency discovery.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/.github/workflows/actions/install_local_dependencies/action.yaml` completely for this pass (76 lines, 2746 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/.github/workflows/actions/install_local_dependencies/action.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/.github/workflows/actions/run_build/action.yaml -->
# sources/security-integrity/cryfs/old-cpp/.github/workflows/actions/run_build/action.yaml

Purpose: Composite action that configures and builds the legacy CryFS C++ tree with CMake and Ninja for Linux/macOS matrix jobs.

Important APIs and types: Inputs are `cc`, `cxx`, `build_type`, `extra_cmake_flags`, and `extra_cxxflags`. Steps show toolchain versions, run CMake, and run Ninja.

Control flow: The first step prints CMake, Ninja, compiler, and ccache info. The configure step appends extra CXX flags, conditionally adds libc++ debug macros for clang Debug builds, creates `build`, and runs `cmake .. -GNinja` with test builds on, compiler launchers set to ccache, build type, and extra flags. The final step runs `ninja` in `build`.

State and persistence behavior: Creates and populates a `build` directory and ccache artifacts. No source files are modified.

Dependencies and integration points: Called by `main.yaml` Linux and macOS jobs after setup/cache/dependency steps. It expects CMake, Ninja, ccache, and selected compilers to be installed.

Risks: The clang Debug libc++ macros are noted as potentially mismatched on Linux because clang may use libstdc++ instead. The action does not define default values for all inputs, so callers must pass required fields; the macOS caller in `main.yaml` omits extra flag inputs even though the action declares them required, which depends on old GitHub Actions behavior or matrix defaults.

Test signals: Successful CMake configure and Ninja build across compiler/build-type matrix rows are the primary signals. Tool version logging helps diagnose failures.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/.github/workflows/actions/run_build/action.yaml` completely for this pass (56 lines, 1993 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/.github/workflows/actions/run_build/action.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/.github/workflows/actions/run_tests/action.yaml -->
# sources/security-integrity/cryfs/old-cpp/.github/workflows/actions/run_tests/action.yaml

Purpose: Composite action that runs the legacy C++ test binaries after a build.

Important APIs and types: Inputs are `gtest_args` and `extra_env_vars`. It invokes the gitversion, cpp-utils, parallelaccessstore, blockstore, blobstore, cryfs, fspp, and cryfs-cli test executables depending on OS and matrix name.

Control flow: The script enters `build`, exports caller-provided env vars, runs core test binaries with the gtest filter arguments, then skips some macOS-only broken tests. On non-macOS it skips fspp under the TSAN matrix and otherwise runs fspp and cryfs-cli tests.

State and persistence behavior: Test execution can create test artifacts under the build tree or temp directories but this action manages no explicit persistence. Environment variables such as sanitizer options affect process behavior.

Dependencies and integration points: Called by `main.yaml` for Linux/macOS jobs where `matrix.run_tests` is true. It assumes build output paths match the Ninja layout.

Risks: `export ${{ inputs.extra_env_vars }}` is fragile if the input is empty or contains shell metacharacters. The action references `matrix.name` directly inside a composite action script, tying it to a specific workflow context. macOS and TSAN exclusions encode known gaps rather than full coverage.

Test signals: Nonzero exit from any test binary fails the CI job. The gtest filter and sanitizer environment are matrix-specific signals for compatibility and race/memory checks.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/.github/workflows/actions/run_tests/action.yaml` completely for this pass (38 lines, 1312 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/.github/workflows/actions/run_tests/action.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/.github/workflows/actions/setup_linux/action.yaml -->
# sources/security-integrity/cryfs/old-cpp/.github/workflows/actions/setup_linux/action.yaml

Purpose: Composite action that prepares Linux GitHub runners with required packages and entropy behavior for legacy CryFS CI.

Important APIs and types: Inputs are `os` and `extra_apt_packages`. It edits APT retry configuration, optionally adds LLVM apt repositories for Ubuntu 18.04/20.04, installs base packages plus the requested compiler package, and replaces `/dev/random` with a copy of `/dev/urandom`.

Control flow: For older Ubuntu versions it downloads the LLVM GPG key, creates `/etc/apt/sources.list.d/clang.list`, writes llvm-toolchain repo lines, then runs `apt-get update` and installs Ninja, libcurl, FUSE dev headers, ccache, and compiler packages. A second step copies `/dev/urandom` to `/dev/random`.

State and persistence behavior: Mutates the runner's apt configuration, installed packages, and device node/file state. These changes are confined to the ephemeral CI VM.

Dependencies and integration points: Used by Linux matrix rows in `main.yaml` before dependency cache and build actions. It assumes sudo, wget, apt, and Ubuntu runner images.

Risks: Uses deprecated `apt-key` and plain HTTP LLVM apt sources. Replacing `/dev/random` is invasive and could hide entropy-related behavior. The repo setup is hard-coded for clang 11 and old Ubuntu releases.

Test signals: Successful package install and later compiler/CMake discovery show setup worked. Faster tests that otherwise block on entropy are the intended secondary signal.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/.github/workflows/actions/setup_linux/action.yaml` completely for this pass (41 lines, 2070 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/.github/workflows/actions/setup_linux/action.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/.github/workflows/actions/setup_macos/action.yaml -->
# sources/security-integrity/cryfs/old-cpp/.github/workflows/actions/setup_macos/action.yaml

Purpose: Composite action that installs macOS dependencies for the legacy C++ CI matrix.

Important APIs and types: Input `extra_homebrew_packages` lets each compiler row request a Homebrew compiler package. The step runs `brew install ninja macfuse libomp ccache md5sha1sum` plus that input.

Control flow: A single bash step invokes Homebrew installation.

State and persistence behavior: Mutates the ephemeral macOS runner by installing packages into Homebrew-managed locations.

Dependencies and integration points: Called by macOS rows in `main.yaml`. It supports CMake/Ninja builds, FUSE integration, OpenMP, ccache, and checksum utilities.

Risks: Homebrew package availability for old compiler versions is unstable, and `main.yaml` already excludes clang 7 because it disappeared. macFUSE installation can be sensitive to runner image policy.

Test signals: Successful brew install and later compiler/test execution in macOS matrix jobs are the only signals.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/.github/workflows/actions/setup_macos/action.yaml` completely for this pass (13 lines, 384 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/.github/workflows/actions/setup_macos/action.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/.github/workflows/actions/setup_windows/action.yaml -->
# sources/security-integrity/cryfs/old-cpp/.github/workflows/actions/setup_windows/action.yaml

Purpose: Composite action that installs Windows dependencies needed for the legacy CryFS build and packaging job.

Important APIs and types: It has no inputs. The bash step calls Chocolatey to install Ninja and Dokany 1.3.0.1000 with developer files.

Control flow: The action sequentially runs two `choco install -y` commands.

State and persistence behavior: Mutates the Windows runner by installing build tooling and the Dokany filesystem driver/development files.

Dependencies and integration points: Used by the Windows job in `main.yaml` before Conan install, Visual Studio CMake build, tests, and WiX CPack packaging.

Risks: Dokany version and installer arguments are pinned to an old stack. Chocolatey availability and driver install behavior can change on hosted images. There is no checksum pinning here.

Test signals: Later CMake configure with `DOKAN_PATH`, Windows test binary execution, and WiX packaging success demonstrate setup correctness.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/.github/workflows/actions/setup_windows/action.yaml` completely for this pass (10 lines, 275 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/.github/workflows/actions/setup_windows/action.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/.github/workflows/main.yaml -->
# sources/security-integrity/cryfs/old-cpp/.github/workflows/main.yaml

Purpose: Defines the legacy CryFS GitHub Actions CI pipeline for Linux, macOS, and Windows builds, tests, sanitizer variants, clang-tidy, dependency caching, and Windows installer artifacts.

Important APIs and types: The workflow triggers on push and pull request. It has `linux_macos` and `windows` jobs. The Linux/macOS matrix spans old macOS/Ubuntu versions, GCC/Clang versions, Debug/Release/RelWithDebInfo, local-dependency builds, Werror, no-compatibility, ASAN, UBSAN, TSAN, and clang-tidy rows. Composite actions in `.github/workflows/actions` provide setup/build/test behavior. The workflow also uses the pinned S3 cache action `leroy-merlin-br/action-s3-cache@8d750...`.

Control flow: Linux/macOS jobs check out code, run OS-specific setup, optionally install local dependencies, upgrade/install pip and Conan 1.59, restore pip/ccache/Conan caches, configure ccache, hash flags, build with composite actions, optionally run clang-tidy with fixes artifact, save caches on push, and run tests. Windows jobs install Dokany/Ninja, install Conan, restore caches, configure/build with Visual Studio 2019 and CMake, run selected test executables, run CPack WiX, and upload MSI artifacts.

State and persistence behavior: CI state includes build directories, ccache, Conan caches under configured homes, pip caches, generated clang-tidy diff artifacts, and MSI artifacts. On push, write-capable cache credentials from secrets save caches; read-only S3 credentials are embedded for PR cache reads.

Dependencies and integration points: Integrates all old C++ build helpers, CMake dependency resolution, Conan 1.x, ccache, sanitizer env vars, Visual Studio, Dokany, WiX packaging, and the test layout. It is the top-level consumer of the setup/build/test composite actions.

Risks: The workflow targets obsolete runner images and toolchain versions (`ubuntu-18.04`, `macos-10.15`, old compiler packages, `actions/checkout@v1`, `actions/upload-artifact@v2`, deprecated `set-output`, deprecated `apt-key`). Public read-only S3 cache credentials are intentionally embedded but still expand the external trust surface. Cache restore is `continue-on-error`, which improves resilience but can hide cache corruption. Several test exclusions mark known platform/sanitizer gaps.

Test signals: Matrix success gives broad compiler/platform coverage. Special signals include Werror build-only rows, ASAN/UBSAN/TSAN test rows with filters, no-compatibility builds, clang-tidy diff artifact on failure, Windows test executable success, and WiX installer upload.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/.github/workflows/main.yaml` completely for this pass (610 lines, 30103 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/.github/workflows/main.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/cmake-utils/DependenciesFromConan.cmake -->
# sources/security-integrity/cryfs/old-cpp/cmake-utils/DependenciesFromConan.cmake

Purpose: Default dependency configuration for the legacy C++ build that resolves range-v3, spdlog, and Boost through Conan.

Important APIs and types: Includes `cmake-utils/conan.cmake`, calls `conan_cmake_autodetect(settings)`, `conan_cmake_install(PATH_OR_REFERENCE ... BUILD missing SETTINGS ${settings})`, includes `${CMAKE_BINARY_DIR}/conanbuildinfo.cmake`, and calls `conan_basic_setup(TARGETS SKIP_STD NO_OUTPUT_DIRS)`. It defines interface targets `CryfsDependencies_range-v3`, `CryfsDependencies_spdlog`, and `CryfsDependencies_boost`.

Control flow: On configure, CMake autodetects Conan settings, installs missing dependencies from `conanfile.py`, imports generated build info, and maps Conan package targets to CryFS-specific dependency targets.

State and persistence behavior: Conan downloads/builds dependency packages into the configured Conan cache and writes generated CMake files into the build tree.

Dependencies and integration points: Included by the main CMake configuration when no custom `DEPENDENCY_CONFIG` is specified. The CryFS targets link against the `CryfsDependencies_*` interface targets instead of direct Conan targets.

Risks: This relies on Conan 1.x behavior and generated `CONAN_PKG::*` targets. `BUILD missing` can compile dependencies during configure, making configure slower and dependent on remote availability. ABI/compiler setting autodetection must match the selected CMake compiler.

Test signals: Successful CMake configure and later linking against range-v3, spdlog, and Boost consumers prove this file works.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/cmake-utils/DependenciesFromConan.cmake` completely for this pass (19 lines, 675 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/cmake-utils/DependenciesFromConan.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/cmake-utils/DependenciesFromLocalSystem.cmake -->
# sources/security-integrity/cryfs/old-cpp/cmake-utils/DependenciesFromLocalSystem.cmake

Purpose: Alternative dependency configuration that finds range-v3, Boost, and spdlog from the local system instead of Conan.

Important APIs and types: Defines `check_target_is_not_from_conan`, uses `find_package(range-v3 REQUIRED)`, `find_package(Boost 1.65.1 REQUIRED COMPONENTS filesystem system thread chrono program_options)`, and `find_package(spdlog REQUIRED)`, then exposes the same `CryfsDependencies_*` interface targets as the Conan config.

Control flow: The file warns if discovered include directories look like Conan paths, creates local dependency interface targets, links Boost components and `rt` on Linux, and leaves version compatibility to the local packages.

State and persistence behavior: No files are written. Configure-time state consists of imported package targets and interface targets.

Dependencies and integration points: Used by CI's local-dependencies matrix rows and by users passing `-DDEPENDENCY_CONFIG=../cmake-utils/DependenciesFromLocalSystem.cmake`. It preserves the same target names as the default dependency file so the rest of the build remains unchanged.

Risks: The comments explicitly state local dependency versions are not officially supported. The Conan-leak warning is heuristic and only inspects include directories. Boost library ABI/version mismatches are a practical risk.

Test signals: CI local-dependency jobs on Ubuntu 18.04 and 20.04 are the primary signal that this configuration remains viable.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/cmake-utils/DependenciesFromLocalSystem.cmake` completely for this pass (61 lines, 2822 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/cmake-utils/DependenciesFromLocalSystem.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/cmake-utils/TargetArch.cmake -->
# sources/security-integrity/cryfs/old-cpp/cmake-utils/TargetArch.cmake

Purpose: Provides a vendored `target_architecture(output_var)` function that detects the target CPU architecture at CMake configure time, including cross-compile scenarios where the generated program cannot be run.

Important APIs and types: The central data is `archdetect_c_code`, a C preprocessor probe that emits `#error cmake_ARCH <arch>`. The public function handles `CMAKE_OSX_ARCHITECTURES` specially on Apple and otherwise writes `arch.c`, enables C, runs `try_run`, and parses compile output.

Control flow: Apple multi-arch settings are normalized and validated manually. Non-Apple detection compiles a deliberately failing C source, captures compiler output, extracts the architecture token with a regex, and falls back to `unknown` if parsing fails.

State and persistence behavior: Writes `${CMAKE_BINARY_DIR}/arch.c` during configure. There is no runtime persistence.

Dependencies and integration points: Included by `cmake-utils/utils.cmake`, which exposes `get_target_architecture`. It supports packaging/build logic that needs architecture names.

Risks: The file is old vendored code and recognizes a limited set of architectures. `try_run` is used for compile-output capture despite no real execution being needed. Apple PowerPC support is disabled unless `ppc_support` is set. Unknown newer architectures become `unknown` and may break downstream packaging.

Test signals: There are no local tests. Configure messages or consumers of `get_target_architecture` are the functional signal.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/cmake-utils/TargetArch.cmake` completely for this pass (145 lines, 6990 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/cmake-utils/TargetArch.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/cmake-utils/conan.cmake -->
# sources/security-integrity/cryfs/old-cpp/cmake-utils/conan.cmake

Purpose: Vendored cmake-conan 0.16.1 helper that bridges CMake configuration to Conan 1.x dependency installation and generated CMake package loading.

Important APIs and types: Key functions/macros include `_get_msvc_ide_version`, `_conan_detect_build_type`, `_conan_check_system_name`, `_conan_check_language`, `_conan_detect_compiler`, `conan_cmake_settings`, `conan_cmake_detect_unix_libcxx`, `conan_cmake_detect_vs_runtime`, `conan_cmake_autodetect`, `conan_cmake_install`, `conan_cmake_run`, `conan_load_buildinfo`, `conan_check`, `conan_add_remote`, and `conan_config_install`.

Control flow: Detection maps CMake compiler/build/os/arch/runtime/libcxx settings into Conan settings. Installation functions parse arguments, construct `conan install` command lines, run Conan in the build directory, and fail or warn based on return code/options. Generated conanfile helpers can write temporary `conanfile.txt`. Loading includes `conanbuildinfo.cmake` or multi-config equivalent and optionally runs `conan_basic_setup`.

State and persistence behavior: Writes generated `conanfile.txt` or temporary copied conanfile markers in the binary dir, runs external Conan commands that populate Conan caches and generated build info, and can add remotes/config to the user Conan configuration.

Dependencies and integration points: Used directly by `DependenciesFromConan.cmake`. It depends on CMake argument parsing, compiler variables, `find_program(conan)`, and Conan CLI version/output formats.

Risks: This is legacy Conan 1.x integration; Conan 2 is not compatible with many options here. Several command builders log full command lines, so env/settings can appear in configure output. Compiler/libcxx autodetection shells out to the compiler preprocessor and can be affected by wrappers/sysroots. Old Visual Studio version mapping stops at VS 2019-era MSVC ranges.

Test signals: Successful configure through `DependenciesFromConan.cmake`, correct dependency target generation, and CI cache reuse are the practical signals. There are no direct unit tests for the vendored helper.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/cmake-utils/conan.cmake` completely for this pass (903 lines, 36216 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/cmake-utils/conan.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/cmake-utils/rust.cmake -->
# sources/security-integrity/cryfs/old-cpp/cmake-utils/rust.cmake

Purpose: Adds a Rust static-library companion to a C++ CMake target, including generated `cxx::bridge` C++ files and link wiring for cross-language calls.

Important APIs and types: The public function is `target_add_rust_companion(TARGET_NAME ...)` with arguments `RUST_LIB_NAME`, `RUST_CRATE_NAME`, `RUST_TARGET_NAME`, `TARGET_NAME`, `RUST_DIR`, and `RUST_BRIDGES`.

Control flow: The function selects `cargo build` or `cargo build --release` based on `CMAKE_BUILD_TYPE`, computes generated bridge `.cc` paths under the binary dir, creates a static bridge-file library and interface companion target, sets include directories, optionally enables clang/lld linker-plugin LTO when the C++ target has IPO and compiler support, globs Rust sources excluding `/target/`, adds a custom command that runs Cargo with `CARGO_TARGET_DIR` and `RUSTFLAGS`, links pthread/dl and the Rust staticlib inside a linker start/end group, links the companion into the target, and registers `cargo test`.

State and persistence behavior: Cargo artifacts and generated cxxbridge files are written under the CMake binary directory's Rust subdirectory. The source tree is not modified.

Dependencies and integration points: Used by `src/blockstore/CMakeLists.txt` for the Rust blockstore bridge. It depends on Cargo, Rust cxx bridge generation, CMake custom commands, clang/lld for optional LTO, and Unix linker flags.

Risks: The function is Unix/linker specific (`pthread`, `dl`, `-Wl,--start-group`) and likely not portable without guards. Release handling only distinguishes Debug from everything else. Source globbing is coarse and can miss dependency changes outside the Rust dir or over-trigger builds. Optional LTO depends on LLVM compatibility between Rust and Clang.

Test signals: Successful CMake target build plus the added `cargo test` CTest entry demonstrate integration. Blockstore bridge compilation is the main consumer signal.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/cmake-utils/rust.cmake` completely for this pass (85 lines, 5293 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/cmake-utils/rust.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/cmake-utils/utils.cmake -->
# sources/security-integrity/cryfs/old-cpp/cmake-utils/utils.cmake

Purpose: Collects legacy CMake utility functions for C++ standard activation, style warnings, static analysis tool integration, Boost linking, compiler version checks, and target architecture detection.

Important APIs and types: Public functions include `target_activate_cpp14`, `target_enable_style_warnings`, `target_add_boost`, `require_gcc_version`, `require_clang_version`, and `get_target_architecture`. It also discovers `clang-tidy` and include-what-you-use when configured.

Control flow: `target_activate_cpp14` sets C++14 except MSVC uses C++17 for range-v3, applies libc++ on Apple Clang, and enables exports for Boost stacktrace. Warning setup adds compiler-specific warning flags, optional `-Werror`, and optional target properties for clang-tidy/IWYU. `target_add_boost` links `CryfsDependencies_boost` and defines `BOOST_THREAD_VERSION=4`. Version checks inspect compiler IDs/versions and fatal on too-old compilers. Architecture detection delegates to `TargetArch.cmake`.

State and persistence behavior: No files are written directly. It mutates CMake target properties and configure variables.

Dependencies and integration points: Included by project CMake files throughout old-cpp. It relies on dependency config files defining `CryfsDependencies_boost`, and on optional tools being available when corresponding flags are enabled.

Risks: MSVC C++17 special-casing means the function name is historical, not literal. Warning sets are incomplete and old. `USE_CLANG_TIDY` and `USE_IWYU` become fatal if tools are missing. Apple-only libc++ handling means Linux clang uses libstdc++ despite some debug macro assumptions elsewhere.

Test signals: Build success across compiler matrix rows, Werror rows, and clang-tidy workflow rows are the practical validation signals.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/cmake-utils/utils.cmake` completely for this pass (141 lines, 6148 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/cmake-utils/utils.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/cpack/CMakeLists.txt -->
# sources/security-integrity/cryfs/old-cpp/cpack/CMakeLists.txt

Purpose: Configures CPack packaging for legacy CryFS, including Linux archive/package generators and Windows WiX installer metadata.

Important APIs and types: Defines `append_build_number`, sets `CPACK_PACKAGE_*`, `CPACK_DEBIAN_*`, `CPACK_RPM_*`, `CPACK_WIX_*`, and includes `CPack`. It calls `get_git_version(GITVERSION_VERSION_STRING)`.

Control flow: For CMake versions below 3.3 it warns and skips package generation. Otherwise it chmods Debian maintainer scripts, sets common package metadata/license/contact, derives the Git version, configures WiX-specific version/GUID/install directory/PATH patch on Windows, or TGZ/DEB/RPM settings on Unix, and registers Debian postinst/postrm control extras.

State and persistence behavior: Mutates maintainer script executable bits in the source tree during configure, writes package configuration into the build system, and later `cpack` emits packages. Windows version may include AppVeyor build number.

Dependencies and integration points: Used by top-level packaging and the Windows CI `cpack -G WIX` step. It integrates with `gitversion`, Debian maintainer scripts, RPM metadata, and WiX patch XML.

Risks: `append_build_number` appears to use `STRIPPED_VERSION_NUMBER` internally rather than its `VERSION_NUMBER` parameter, relying on caller scope behavior. Changing source file permissions at configure time is unusual. Debian packages auto-add an APT source through maintainer scripts, which is a significant install side effect. WiX product GUID is fixed.

Test signals: CPack success for TGZ/DEB/RPM/WIX and Windows MSI upload are the main signals. Package-manager install/purge behavior depends on maintainer scripts.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/cpack/CMakeLists.txt` completely for this pass (72 lines, 3963 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/cpack/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/cpack/debfiles/postinst -->
# sources/security-integrity/cryfs/old-cpp/cpack/debfiles/postinst

Purpose: Debian post-install maintainer script that adds the CryFS APT repository and package signing key after installing the `.deb`.

Important APIs and types: Functions include `containsElement` (unused), `get_repo_url`, `get_apt_config`, `sources_list_dir`, `add_repository`, and `install_key`. It embeds a full PGP public key block and uses `apt-key add`.

Control flow: On `configure`, it installs the embedded key and writes `cryfs.list` into the apt sources parts directory with either Debian/Devuan or Ubuntu repository URL based on `lsb_release`. Unsupported distributions print a warning and exit successfully. Abort cases no-op; unknown arguments fail.

State and persistence behavior: Persists an APT trusted key and a `cryfs.list` package source file under the system apt configuration. It does not run `apt-get update`; it only configures future package source availability.

Dependencies and integration points: Registered through `CPACK_DEBIAN_PACKAGE_CONTROL_EXTRA`. Depends on `bash`, `lsb_release`, `apt-config`, `apt-key`, and Debian-family apt layout.

Risks: Uses HTTP repository URLs and deprecated global `apt-key`, increasing security and modernization concerns. The script writes to apt source parts without quoting all variables. Unsupported distributions leave users on manual updates. The embedded key must be rotated in-package if CryFS repository signing changes.

Test signals: Package install on Debian/Ubuntu should leave a `cryfs.list` with the right codename and a trusted key. Unknown maintainer-script argument should fail.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/cpack/debfiles/postinst` completely for this pass (124 lines, 4814 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/cpack/debfiles/postinst -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/cpack/debfiles/postrm -->
# sources/security-integrity/cryfs/old-cpp/cpack/debfiles/postrm

Purpose: Debian post-remove maintainer script that removes the CryFS APT repository and signing key on package purge.

Important APIs and types: Defines `get_apt_config`, `sources_list_dir`, `remove_repository`, and `remove_key`. It removes key ID `549E65B2` via `apt-key rm`.

Control flow: On `purge`, it deletes `$sources_list_dir/cryfs.list` and removes the apt key while ignoring key-removal failure. Remove/upgrade/abort cases no-op. Unknown arguments fail.

State and persistence behavior: Mutates system apt configuration by deleting CryFS source and key state only during purge, not ordinary remove or upgrade.

Dependencies and integration points: Registered with CPack Debian package control extras. Depends on apt-config and apt-key layout matching the postinst script.

Risks: Uses deprecated `apt-key`. Directory path concatenation differs from postinst (`echo $root$etc$sourceparts` vs slash-separated output), relying on apt-config values carrying separators. Only purge cleans up, so ordinary remove leaves the repository configured.

Test signals: Purging the package should remove `cryfs.list` and key ID `549E65B2`; other maintainer-script actions should exit without changes.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/cpack/debfiles/postrm` completely for this pass (45 lines, 870 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/cpack/debfiles/postrm -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/cpack/wix/change_path_env.xml -->
# sources/security-integrity/cryfs/old-cpp/cpack/wix/change_path_env.xml

Purpose: WiX CPack patch fragment that adds the installed CryFS `bin` directory to the system `PATH` on Windows.

Important APIs and types: Defines a `CPackWiXPatch` with `CPackWiXFragment Id="CM_CP_bin.cryfs.exe"` and an `Environment` element `Id="MyPath"` with `Action="set"`, `Part="first"`, `Name="PATH"`, `Value="[INSTALL_ROOT]bin"`, and `System="yes"`.

Control flow: CPack consumes this XML patch during WiX generation when `CPACK_WIX_PATCH_FILE` points to it. There is no standalone execution.

State and persistence behavior: The resulting MSI mutates the machine-wide Windows PATH by prepending the install bin path.

Dependencies and integration points: Referenced from `cpack/CMakeLists.txt` for Windows packaging.

Risks: System PATH mutation is global and can have ordering/collision effects. The fragment ID must match CPack's generated component ID; if CPack changes component naming, the patch stops applying.

Test signals: Installed MSI should expose `cryfs.exe` on PATH and WiX generation should succeed without missing-fragment errors.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/cpack/wix/change_path_env.xml` completely for this pass (7 lines, 215 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/cpack/wix/change_path_env.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/doc/CMakeLists.txt -->
# sources/security-integrity/cryfs/old-cpp/doc/CMakeLists.txt

Purpose: Builds and installs compressed Unix man pages for `cryfs` and `cryfs-unmount`.

Important APIs and types: Uses `GNUInstallDirs`, `find_program(GZIP gzip)`, two `add_custom_command` calls, two `add_custom_target(... ALL ...)`, and an `install(FILES ... DESTINATION ${CMAKE_INSTALL_MANDIR}/man1 CONFIGURATIONS Release)`.

Control flow: On Windows it logs that man pages are not installed. On other platforms it finds gzip, generates `cryfs.1.gz` and `cryfs-unmount.1.gz` in the binary dir from source man pages, attaches both to the default build, and installs them only for Release configuration.

State and persistence behavior: Writes compressed man pages into the build directory and installs them under the configured man directory during install.

Dependencies and integration points: Added by `src`/top-level documentation build flow. It depends on gzip and the source files under `doc/man`.

Risks: `find_program(GZIP gzip)` does not explicitly fail if gzip is missing before custom command execution. Install is Release-only, so Debug installs omit man pages. Shell redirection in `COMMAND ${GZIP} -c ... > ...` depends on CMake command invocation semantics.

Test signals: Build target `man`/`umountman` generation and package/install contents containing both gzipped man pages are the key signals.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/doc/CMakeLists.txt` completely for this pass (26 lines, 882 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/doc/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/CMakeLists.txt -->
# sources/security-integrity/cryfs/old-cpp/src/CMakeLists.txt

Purpose: Top-level source directory CMake file that adds all legacy C++ subprojects to the build.

Important APIs and types: Calls `include_directories(${CMAKE_CURRENT_SOURCE_DIR})` and `add_subdirectory` for `gitversion`, `cpp-utils`, `fspp`, `parallelaccessstore`, `blockstore`, `blobstore`, `cryfs`, `cryfs-cli`, `cryfs-unmount`, and `stats`.

Control flow: During configure, each subdirectory is added in dependency order close to bottom-up library layering.

State and persistence behavior: No files are written directly. It mutates include directory state globally for descendants.

Dependencies and integration points: This is the source-tree build entry for the old C++ product and libraries. Blockstore in this subset is one of the subdirectories registered here.

Risks: Global `include_directories` is broad and can mask include hygiene issues. Subdirectory order matters because later targets may expect earlier targets.

Test signals: Full CMake configure/build success validates that all subprojects can be discovered and ordered correctly.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/CMakeLists.txt` completely for this pass (12 lines, 333 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/CMakeLists.txt -->
# sources/security-integrity/cryfs/old-cpp/src/blockstore/CMakeLists.txt

Purpose: Defines the legacy `blockstore` static library target and wires it to C++ utilities, Boost, style rules, C++ standard settings, and a Rust companion library.

Important APIs and types: `SOURCES` lists blockstore utilities, test fake, parallel access, caching cache, mock, and rustbridge implementation files. It calls `add_library(blockstore STATIC ...)`, `target_link_libraries(blockstore PUBLIC cpp-utils)`, `target_add_boost`, `target_enable_style_warnings`, `target_activate_cpp14`, includes `rust`, and calls `target_add_rust_companion`.

Control flow: Configure creates the static target from C++ sources, applies common build helper functions, then registers Rust bridge files for `cryfs-cppbridge` with bridges `src/blockstore.rs`, `src/blobstore.rs`, and `src/fsblobstore.rs`.

State and persistence behavior: Build outputs include the C++ static library, generated Rust bridge C++ files, and Cargo artifacts under the build tree.

Dependencies and integration points: This target sits between lower-level `cpp-utils`/`parallelaccessstore` and higher-level blobstore/cryfs code. It includes both legacy C++ blockstore adapters and Rust bridge integration.

Risks: The source list contains several `.cpp` files that only include template headers, so removing them may affect IDE/build source visibility but not logic. Rust companion setup is platform-sensitive. Test fake/mock implementations are compiled into the main static library, not isolated test-only code.

Test signals: `blockstore-test`, rust companion cargo tests, and any higher-level blobstore/cryfs tests validate this target.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/CMakeLists.txt` completely for this pass (39 lines, 1270 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/Cache.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/Cache.cpp

Purpose: Translation unit for the templated caching `Cache` implementation.

Important APIs and types: It includes `Cache.h`; no functions are defined here because the cache is template-heavy and implemented in the header.

Control flow: There is no runtime control flow in this file.

State and persistence behavior: No state is defined here. Cache state lives in template instantiations from `Cache.h`.

Dependencies and integration points: Listed in `src/blockstore/CMakeLists.txt` so the header appears in the target's source set and IDEs.

Risks: Removing the file would likely not change compiled behavior unless the build expects the translation unit. Template implementation risks are in `Cache.h`.

Test signals: Coverage comes from tests that instantiate and exercise `Cache`.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/Cache.cpp` completely for this pass (1 lines, 19 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/Cache.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/Cache.h -->
# sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/Cache.h

Purpose: Implements a bounded, time-purged, addressable cache template used by the legacy caching blockstore layer. Values are evicted by age or capacity, and value destruction can occur in parallel outside the main cache mutex.

Important APIs and types: `Cache<Key, Value, MAX_ENTRIES>` exposes `size`, `push`, `pop`, and `flush`. Constants are `PURGE_LIFETIME_SEC`, `PURGE_INTERVAL`, and `MAX_LIFETIME_SEC`. Internal types include `QueueMap<Key, CacheEntry<Key, Value>>`, `cpputils::LockPool<Key>`, `MutexPoolLock`, and `PeriodicTask`.

Control flow: Construction starts a periodic task that calls `_deleteOldEntriesParallel`. `push` locks, ensures capacity with `_makeSpaceForEntry`, then appends a `CacheEntry`. `pop(key)` locks the cache and a per-key flush lock, removes the entry if present, and releases the wrapped value. `_deleteEntry` peeks the oldest key, locks that key against concurrent pop, removes it, unlocks the cache while the value destructor runs, then re-locks. Flush and age-based deletion fan out `2 * hardware_concurrency` async workers that repeatedly delete matching entries at the queue front.

State and persistence behavior: State is in-memory queue/map entries plus a background purge thread. Persistence behavior is indirect: `Value` destructors may flush dirty blocks or release resources, so eviction timing affects when underlying storage writes happen.

Dependencies and integration points: Depends on `CacheEntry`, `QueueMap`, `PeriodicTask`, Boost optional, futures/async, cpp-utils assertions and lock pools. Used by caching blockstore code to hold recently accessed blocks and flush old entries.

Risks: Eviction is front-only, so only old entries at the beginning are purged; newer front entries can block older-but-later entries if ordering assumptions change. Destructors run outside the mutex for parallelism, which is powerful but concurrency-sensitive. The destructor does not explicitly stop `_timeoutFlusher` before deleting entries, relying on member destruction order after the destructor body; callbacks into a partly destructing object are a risk if `PeriodicTask` does not stop promptly. Duplicate `push` keys throw through `QueueMap`.

Test signals: There are TODOs for flush testing. Effective coverage should assert size bounds, duplicate handling, pop behavior, destructor/flush side effects, age purge, capacity eviction, and concurrent pop/evict safety.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/Cache.h` completely for this pass (181 lines, 7973 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/Cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/CacheEntry.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/CacheEntry.cpp

Purpose: Translation unit for the templated `CacheEntry` wrapper.

Important APIs and types: It includes `CacheEntry.h`; implementation lives in the header because `CacheEntry` is templated.

Control flow: No runtime control flow is present in this file.

State and persistence behavior: No state is defined here. Entry timestamp/value state is described in `CacheEntry.h`.

Dependencies and integration points: Included in the blockstore target source list for build/IDE visibility.

Risks: Behavioral risks are in the header; this file is effectively a placeholder.

Test signals: Tests instantiate `CacheEntry` indirectly through `Cache`.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/CacheEntry.cpp` completely for this pass (1 lines, 24 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/CacheEntry.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/CacheEntry.h -->
# sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/CacheEntry.h

Purpose: Defines the per-entry wrapper for the caching layer, storing a cached value and the time it was inserted/accessed for age-based purging.

Important APIs and types: `CacheEntry<Key, Value>` has a constructor, move constructor, `ageSeconds`, and `releaseValue`. It stores a Boost `ptime` `_lastAccess` and a `Value`.

Control flow: Construction records `currentTime()` and moves in the value. `ageSeconds` subtracts `_lastAccess` from the current local time and converts nanoseconds to seconds. `releaseValue` moves the value out.

State and persistence behavior: State is in memory only. The timestamp controls when `Cache` considers an entry old; there is no refresh on pop/push beyond construction time.

Dependencies and integration points: Depends on Boost posix time, cpp-utils macros, and cache eviction logic in `Cache.h`.

Risks: Uses local wall-clock time instead of a monotonic clock, so system clock changes can affect age. The comment in `Cache.h` notes lifetime is based on last push, not true repeated access lifetime. Moving out leaves the internal value moved-from until the entry is erased.

Test signals: Indirect cache tests should validate age purging and value release. There are no local tests.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/CacheEntry.h` completely for this pass (44 lines, 1050 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/CacheEntry.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/PeriodicTask.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/PeriodicTask.cpp

Purpose: Implements a small synchronous periodic task wrapper used by the legacy C++ cache to call purge functions on a `LoopThread`.

Important APIs and types: `PeriodicTask::PeriodicTask(function<void()>, double intervalSec, string threadName)` and private `_loopIteration` are implemented here. It uses `cpputils::LoopThread` and Boost chrono sleep.

Control flow: The constructor converts the interval seconds to nanoseconds, constructs a loop thread bound to `_loopIteration`, and starts it. Each loop iteration sleeps interruptibly for the interval, invokes the task, and returns true to continue running.

State and persistence behavior: State is the task callback, interval, and background thread. Persistence effects depend on the callback, typically cache eviction and block flush.

Dependencies and integration points: Used by `Cache` to run `_deleteOldEntriesParallel` every purge interval. Depends on cpp-utils logging/thread support and Boost thread sleep because the sleep must be interruptible by `LoopThread`.

Risks: Callback exceptions are not caught here. Lifetime depends on `_thread` being last in the header so it is destroyed first; otherwise a running thread could access destroyed callback/interval state. The first task run occurs only after sleeping.

Test signals: No direct tests in this subset. Cache timeout behavior and thread shutdown are the implied validation points.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/PeriodicTask.cpp` completely for this pass (26 lines, 827 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/PeriodicTask.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/PeriodicTask.h -->
# sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/PeriodicTask.h

Purpose: Declares the legacy C++ cache periodic task helper.

Important APIs and types: `PeriodicTask` stores a `std::function<void()>`, a `boost::chrono::nanoseconds` interval, and a `cpputils::LoopThread`. Copy/assign are disabled.

Control flow: Public construction starts the thread through the implementation file. `_loopIteration` is the repeating callback passed to `LoopThread`.

State and persistence behavior: In-memory only, with side effects determined by the task callback. Member order is explicitly part of lifecycle safety: `_thread` is last so it is destructed first.

Dependencies and integration points: Included by `Cache.h` for automatic cache purging.

Risks: The class has no explicit stop method, relying on `LoopThread` destruction semantics. Users must ensure the callback target outlives the running thread.

Test signals: Validated indirectly by cache construction/destruction and purge behavior.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/PeriodicTask.h` completely for this pass (32 lines, 771 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/PeriodicTask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/QueueMap.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/QueueMap.cpp

Purpose: Translation unit for the templated `QueueMap` addressable queue.

Important APIs and types: It includes `QueueMap.h`; all behavior is implemented in the header.

Control flow: No runtime control flow is present here.

State and persistence behavior: No state is defined here.

Dependencies and integration points: Included in the blockstore target source list for build/IDE visibility.

Risks: Behavioral risks live in `QueueMap.h`.

Test signals: Tests should instantiate `QueueMap` indirectly through `Cache`.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/QueueMap.cpp` completely for this pass (1 lines, 22 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/QueueMap.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/QueueMap.h -->
# sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/QueueMap.h

Purpose: Implements an addressable FIFO queue: entries can be pushed in queue order, popped by key, popped from the front, and peeked from the front.

Important APIs and types: `QueueMap<Key, Value>` exposes `push`, `pop(key)`, `pop()`, `peekKey`, `peek`, and `size`. It stores an `unordered_map<Key, Entry>` plus a sentinel node for a doubly linked list. `Entry` manually stores `Value` in aligned byte storage.

Control flow: `push` emplaces an `Entry` in the map with links at the tail, initializes its key pointer and placement-news the value, then splices it before the sentinel. `pop(key)` finds the map entry, unlinks it, moves/releases its value, erases the map entry, and returns the value. `pop()` removes the sentinel's next entry. Peek methods return optional references to the front key/value.

State and persistence behavior: State is all in-memory. The destructor iterates remaining entries and calls `release` to run value destructors. Map nodes are relied on for stable addresses so linked-list pointers remain valid.

Dependencies and integration points: Used by `Cache` to track insertion/eviction order while supporting keyed lookup. Depends on Boost optional and cpp-utils assertions/macros.

Risks: Manual lifetime management is delicate: `Entry::release` must be called exactly once for initialized entries. `push` throws `logic_error` for duplicate keys. `peekKey` returns a reference wrapped in `boost::optional`, so callers must not outlive the map mutation. No internal locking is provided; synchronization is the caller's responsibility.

Test signals: Direct tests should cover ordering, duplicate key rejection, pop by key, pop empty, value destruction on erase/destructor, and pointer/reference validity under unordered_map growth. Current validation is likely through cache tests.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/QueueMap.h` completely for this pass (122 lines, 3427 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/QueueMap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/mock/MockBlock.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/mock/MockBlock.cpp

Purpose: Implements mutating operations for `MockBlock`, an access-counting wrapper around a real `Block`.

Important APIs and types: Defines `MockBlock::write` and `MockBlock::resize`.

Control flow: `write` records a write for this block ID in the owning `MockBlockStore`, then delegates to the base block. `resize` records a resize and delegates.

State and persistence behavior: Persistent behavior is that writes/resizes affect the base block exactly as before; additional in-memory counters in `MockBlockStore` record access patterns.

Dependencies and integration points: Used by `MockBlockStore` in performance and behavioral tests to assert how many blocks were touched.

Risks: Counter updates happen before delegation, so a failed underlying operation may still be counted. Thread safety depends on `MockBlockStore` locking.

Test signals: Tests should inspect `writtenBlocks` and `resizedBlocks` after operations through loaded/created mock blocks.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/mock/MockBlock.cpp` completely for this pass (18 lines, 494 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/mock/MockBlock.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/mock/MockBlock.h -->
# sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/mock/MockBlock.h

Purpose: Declares `MockBlock`, a `Block` wrapper that forwards data access to a base block while informing `MockBlockStore` about writes and resizes.

Important APIs and types: Constructor takes `unique_ref<Block>` and `MockBlockStore*`. It overrides `data`, `write`, `size`, and `resize`, and exposes `releaseBaseBlock` for removal forwarding.

Control flow: Non-mutating methods forward directly to `_baseBlock`; mutating methods are defined in the `.cpp` to record counters first. `releaseBaseBlock` moves the wrapped block out.

State and persistence behavior: Holds a unique reference to the base block and a raw pointer to the owning store. It does not own persistence itself; the base block does.

Dependencies and integration points: Created by `MockBlockStore::tryCreate` and `load`. Friend access lets the store unwrap during flush/remove.

Risks: The raw store pointer must remain valid for the lifetime of every mock block. `releaseBaseBlock` leaves the wrapper moved-from and should only be used in controlled removal paths.

Test signals: Access-count tests should verify forwarding plus counter vectors for write/resize.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/mock/MockBlock.h` completely for this pass (47 lines, 1310 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/mock/MockBlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/mock/MockBlockStore.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/mock/MockBlockStore.cpp

Purpose: Translation unit for `MockBlockStore`.

Important APIs and types: It includes `MockBlockStore.h`; implementation is inline in the header.

Control flow: No runtime control flow is present here.

State and persistence behavior: No state is defined here. Counter and base-store behavior live in the header.

Dependencies and integration points: Included in the blockstore target source list.

Risks: Behavioral risks are in `MockBlockStore.h`.

Test signals: Access-counting tests instantiate the header-defined class.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/mock/MockBlockStore.cpp` completely for this pass (1 lines, 28 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/mock/MockBlockStore.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/mock/MockBlockStore.h -->
# sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/mock/MockBlockStore.h

Purpose: Implements a `BlockStore` wrapper that counts block operations for tests, especially performance tests that assert a feature only loads/writes/removes a small number of blocks.

Important APIs and types: `MockBlockStore` wraps another `BlockStore`, defaulting to `testfake::FakeBlockStore`. It overrides the full `BlockStore` interface and exposes `resetCounters`, `createdBlocks`, `loadedBlocks`, `removedBlocks`, `resizedBlocks`, `writtenBlocks`, and `distinctWrittenBlocks`.

Control flow: Creation increments created count, delegates to base `tryCreate`, and wraps successful blocks in `MockBlock`. Loading increments loaded count and wraps. `overwrite` increments written count and delegates directly. `remove(id)` increments removed count and delegates. `remove(unique_ref<Block>)` requires a `MockBlock`, unwraps its base block, and delegates. `flushBlock` requires a `MockBlock` and flushes the underlying base block.

State and persistence behavior: Operation counters are protected by a mutex and persist in memory until reset. Actual block data and persistence behavior belong to the base store.

Dependencies and integration points: Uses `FakeBlockStore`, `MockBlock`, cpp-utils `unique_ref`, dynamic pointer moves, assertions, and Boost optional. It is a test double for blockstore users.

Risks: `overwrite` returns the base store's block directly rather than wrapping it, so subsequent writes/resizes through that returned block will not be counted as `MockBlock` operations. Counter increments can occur even if the delegated operation returns none or fails. `distinctWrittenBlocks` sorts by raw block ID bytes and assumes binary length.

Test signals: Tests should verify operation vectors/counts, reset behavior, distinct written block calculation, unwrap/remove paths, and wrong-store assertions in `remove`/`flushBlock`.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/mock/MockBlockStore.h` completely for this pass (163 lines, 6397 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/mock/MockBlockStore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/parallelaccess/BlockRef.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/parallelaccess/BlockRef.cpp

Purpose: Translation unit for `BlockRef`.

Important APIs and types: It includes `BlockRef.h`; all behavior is inline in the header.

Control flow: No runtime control flow is present here.

State and persistence behavior: No state is defined here.

Dependencies and integration points: Included in the blockstore target source list.

Risks: Behavioral risks are in `BlockRef.h`.

Test signals: Parallel access tests instantiate and exercise the header-defined wrapper.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/parallelaccess/BlockRef.cpp` completely for this pass (1 lines, 22 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/parallelaccess/BlockRef.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/parallelaccess/BlockRef.h -->
# sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/parallelaccess/BlockRef.h

Purpose: Defines `BlockRef`, the resource-reference wrapper used by `ParallelAccessBlockStore` to hand out block handles coordinated by `parallelaccessstore::ParallelAccessStore`.

Important APIs and types: `BlockRef` inherits both `blockstore::Block` and `ParallelAccessStore<Block, BlockRef, BlockId>::ResourceRefBase`. It wraps a raw `Block*` `_baseBlock`.

Control flow: Constructor copies the base block ID into the `Block` base and stores the raw pointer. `data`, `write`, `size`, and `resize` simply forward to `_baseBlock`.

State and persistence behavior: `BlockRef` does not own data persistence; it references a base block managed by the parallel access store. Mutations are applied to the base block.

Dependencies and integration points: Used internally by `ParallelAccessBlockStore` and the generic `parallelaccessstore` resource manager.

Risks: Stores the block ID twice, as noted by TODO. The raw pointer must remain valid while the ref exists; lifetime is delegated to `ParallelAccessStore`. There is no additional synchronization in `BlockRef` itself.

Test signals: Parallel access tests should validate forwarded reads/writes/resizes and correct exclusive/shared lifetime behavior through the store.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/parallelaccess/BlockRef.h` completely for this pass (45 lines, 1172 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/parallelaccess/BlockRef.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/parallelaccess/ParallelAccessBlockStore.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/parallelaccess/ParallelAccessBlockStore.cpp

Purpose: Implements a `BlockStore` decorator that coordinates concurrent access to block handles through `parallelaccessstore::ParallelAccessStore`.

Important APIs and types: Implements `createBlockId`, `tryCreate`, `load`, `overwrite`, both `remove` overloads, `numBlocks`, `estimateNumFreeBytes`, `blockSizeFromPhysicalBlockSize`, `forEachBlock`, and `flushBlock`. It uses `ParallelAccessBlockStoreAdapter`, `BlockRef`, `unique_ref`, and Boost optional.

Control flow: Construction owns the base store and creates an adapter for the parallel access store. `tryCreate` refuses creation if the ID is already opened, delegates base creation, then registers the new block with the parallel access store. `load` delegates to `_parallelAccessStore.load`. `overwrite` uses `loadOrAdd`: if a block is already open, resize/write into it; otherwise create/overwrite in the base store. `remove(unique_ref<Block>)` unwraps a `BlockRef` and removes it through the parallel access store; `remove(id)` removes by ID. Read-only metadata methods delegate to base store. `flushBlock` unwraps `BlockRef` and flushes the base block.

State and persistence behavior: The wrapper's runtime state is the base blockstore plus the parallel-access manager's open-resource registry. Persistence remains the base store's responsibility, but overwrite/remove behavior is coordinated with currently open refs.

Dependencies and integration points: Sits between higher blockstore users and any concrete base store to prevent unsafe simultaneous access. It integrates with the separate `parallelaccessstore` library.

Risks: `tryCreate` first checks `isOpened`, but base creation can still fail if the ID exists closed in the base store. The overwrite lambda captures `data` by reference and writes into an already-open block before returning it. Correctness depends on `ParallelAccessStore` enforcing the intended locking/lifetime semantics. Wrong block type in `remove`/`flushBlock` asserts.

Test signals: Parallel access tests should cover duplicate open/create refusal, load sharing/exclusion, overwrite of opened and unopened blocks, removal by ID/ref, base metadata delegation, and flush forwarding.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/parallelaccess/ParallelAccessBlockStore.cpp` completely for this pass (96 lines, 3226 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/parallelaccess/ParallelAccessBlockStore.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/parallelaccess/ParallelAccessBlockStore.h -->
# sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/parallelaccess/ParallelAccessBlockStore.h

Purpose: Declares the parallel-access `BlockStore` wrapper.

Important APIs and types: `ParallelAccessBlockStore` owns `unique_ref<BlockStore> _baseBlockStore` and `ParallelAccessStore<Block, BlockRef, BlockId> _parallelAccessStore`. It implements the full `BlockStore` interface.

Control flow: Public methods are implemented in the `.cpp`; copy and assignment are disabled.

State and persistence behavior: Runtime state tracks opened blocks and delegates durable data to the base store. Removing or overwriting may update currently open block refs.

Dependencies and integration points: Consumers wrap concrete blockstores with this class when they need coordinated concurrent access. It relies on `BlockRef` and `ParallelAccessBlockStoreAdapter`.

Risks: TODO notes uncertainty about allowing parallel destruction of blocks, important because encrypted block destruction/flush may be expensive. Lifetime order between base store and parallel access store must remain valid.

Test signals: Validated by `parallelaccessstore-test` and `blockstore-test` paths using this implementation.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/parallelaccess/ParallelAccessBlockStore.h` completely for this pass (40 lines, 1620 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/parallelaccess/ParallelAccessBlockStore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/parallelaccess/ParallelAccessBlockStoreAdapter.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/parallelaccess/ParallelAccessBlockStoreAdapter.cpp

Purpose: Translation unit for `ParallelAccessBlockStoreAdapter`.

Important APIs and types: It includes `ParallelAccessBlockStoreAdapter.h`; implementation is inline in the header.

Control flow: No runtime control flow is present here.

State and persistence behavior: No state is defined here.

Dependencies and integration points: Included in the blockstore target source list.

Risks: Behavioral risks are in the header.

Test signals: Adapter behavior is tested indirectly through `ParallelAccessBlockStore`.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/parallelaccess/ParallelAccessBlockStoreAdapter.cpp` completely for this pass (1 lines, 45 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/parallelaccess/ParallelAccessBlockStoreAdapter.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/parallelaccess/ParallelAccessBlockStoreAdapter.h -->
# sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/parallelaccess/ParallelAccessBlockStoreAdapter.h

Purpose: Adapts the `BlockStore` interface to the generic `ParallelAccessBaseStore<Block, BlockId>` interface expected by `parallelaccessstore`.

Important APIs and types: `ParallelAccessBlockStoreAdapter` stores a raw `BlockStore*` and implements `loadFromBaseStore`, `removeFromBaseStore(unique_ref<Block>)`, and `removeFromBaseStore(BlockId)`.

Control flow: Each method forwards directly to the underlying base blockstore.

State and persistence behavior: Holds no ownership and no independent persistence. All state changes occur in the base blockstore.

Dependencies and integration points: Constructed by `ParallelAccessBlockStore` with `_baseBlockStore.get()` and used internally by `ParallelAccessStore`.

Risks: The raw pointer must remain valid for the adapter lifetime. There is no null check or synchronization here; the owning wrapper must provide lifetime and concurrency context.

Test signals: Indirect signals are successful parallel access load/remove behavior and base-store side effects.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/parallelaccess/ParallelAccessBlockStoreAdapter.h` completely for this pass (39 lines, 1117 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/parallelaccess/ParallelAccessBlockStoreAdapter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/testfake/FakeBlock.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/testfake/FakeBlock.cpp

Purpose: Implements `FakeBlock`, a strict in-memory test block that works on a private copy and flushes changes back to `FakeBlockStore` only when dirty.

Important APIs and types: Defines constructor, destructor, `data`, `write`, `size`, `resize`, and `flush`. It uses `cpputils::Data`, `DataUtils::resize`, assertions, and `std::memcpy`.

Control flow: Constructor stores the owning store, shared data copy, and dirty flag. Destructor calls `flush`. `write` asserts the write fits within current size, copies bytes into the local data buffer, and marks dirty. `resize` replaces the data with a resized copy and marks dirty. `flush` writes data back to the store via `updateData` if dirty, then clears the flag.

State and persistence behavior: State is local copied block data and dirty flag. Persistence to the backing fake store occurs on flush/destruction; until then, other loads see the old backing data.

Dependencies and integration points: Created by `FakeBlockStore::makeFakeBlockFromData`. Used heavily as a stricter test double than a direct in-memory store.

Risks: Write bounds assertion uses `offset + size`, which can overflow despite the comment saying it checks overflow; the first conjunct only ensures offset is in range. Destructor flush means test failures or exceptions during update can occur at scope exit. Multiple FakeBlocks for the same ID can overwrite each other based on flush order.

Test signals: Tests should verify write bounds, dirty flush, resize behavior, destructor flush, and independent loaded copies.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/testfake/FakeBlock.cpp` completely for this pass (54 lines, 1284 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/testfake/FakeBlock.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/testfake/FakeBlock.h -->
# sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/testfake/FakeBlock.h

Purpose: Declares `FakeBlock`, the block handle returned by `FakeBlockStore`.

Important APIs and types: Inherits `Block`, stores `FakeBlockStore*`, `shared_ptr<cpputils::Data>`, and `_dataChanged`. Public methods are destructor, `data`, `write`, `flush`, `size`, and `resize`.

Control flow: Method bodies are in the `.cpp`; copy and assignment are disabled.

State and persistence behavior: Holds a private data buffer shared only for handle lifetime tracking and flushes dirty data back to the store.

Dependencies and integration points: Used by `FakeBlockStore` and test code through the abstract `Block` interface.

Risks: Raw store pointer lifetime must outlive blocks. Dirty state is per handle, so concurrent handles for the same ID require careful flush ordering in tests.

Test signals: See `FakeBlock.cpp` and `FakeBlockStore` tests for behavior.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/testfake/FakeBlock.h` completely for this pass (39 lines, 841 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/testfake/FakeBlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/testfake/FakeBlockStore.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/testfake/FakeBlockStore.cpp

Purpose: Implements `FakeBlockStore`, a strict in-memory blockstore for unit tests that returns copies of block data and requires flush/destruction to persist modifications.

Important APIs and types: Implements `createBlockId`, `tryCreate`, `overwrite`, `load`, `_load`, `remove`, `makeFakeBlockFromData`, `updateData`, `numBlocks`, `estimateNumFreeBytes`, `blockSizeFromPhysicalBlockSize`, `forEachBlock`, and `flushBlock`.

Control flow: Blocks are stored in `_blocks` under a mutex. `tryCreate` emplaces a new ID and returns `_load`. `overwrite` inserts or replaces data and returns a loaded block. `_load` returns none on missing IDs or creates a `FakeBlock` with copied data. `remove` asserts exactly one entry was removed. `updateData` writes a copy back, inserting if absent. `flushBlock` dynamic-casts to `FakeBlock` and calls `flush`.

State and persistence behavior: Persistence is in-memory map state. Every loaded block receives a copy, and `_used_dataregions_for_blocks` keeps shared pointers to all data buffers ever issued to avoid allocator reuse hiding out-of-bounds bugs in tests. Dirty block flushes update the backing map.

Dependencies and integration points: Default base store for `MockBlockStore` and likely many blockstore/blobstore tests. Uses `BlockId::Random`, cpp-utils data helpers, assertions, memory-size utility, mutex, unordered_map, and Boost optional.

Risks: `forEachBlock` iterates `_blocks` without taking `_mutex`, unlike other methods, which is unsafe under concurrent mutation. `updateData` can reinsert a block that was removed if a stale dirty handle flushes later. `estimateNumFreeBytes` reports total system memory, not remaining fake capacity.

Test signals: Tests should validate create/load/overwrite/remove semantics, copy isolation before flush, flush persistence, numBlocks, wrong-type flush assertion, and stale-handle behavior.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/testfake/FakeBlockStore.cpp` completely for this pass (116 lines, 3380 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/testfake/FakeBlockStore.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/testfake/FakeBlockStore.h -->
# sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/testfake/FakeBlockStore.h

Purpose: Declares the strict in-memory fake blockstore used for tests.

Important APIs and types: `FakeBlockStore` implements `BlockStore` and stores `_blocks: unordered_map<BlockId, Data>`, `_used_dataregions_for_blocks`, and `_mutex`. It exposes `updateData` and `flushBlock` in addition to the abstract interface.

Control flow: Public behavior is implemented in the `.cpp`; helper methods create fake block handles and load optional blocks. Copy and assignment are disabled.

State and persistence behavior: In-memory map acts as backing persistence for fake blocks. The extra vector intentionally keeps old data regions alive to make tests less forgiving of memory misuse.

Dependencies and integration points: Used directly in tests and as the default base for `MockBlockStore`.

Risks: Because fake blocks copy data, behavior differs from a real memory-mapped or direct in-memory store. Tests relying on immediate visibility without flush should fail, by design. Concurrency safety depends on all map access taking `_mutex`; header exposes no guard for callbacks.

Test signals: Blockstore tests should use this to catch missing flushes and out-of-bounds writes.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/testfake/FakeBlockStore.h` completely for this pass (69 lines, 3113 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/testfake/FakeBlockStore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/interface/Block.h -->
# sources/security-integrity/cryfs/old-cpp/src/blockstore/interface/Block.h

Purpose: Defines the abstract block handle interface for the legacy C++ blockstore layer.

Important APIs and types: `Block` declares virtual `data`, `write`, `size`, and `resize`, plus nonvirtual `blockId`. It stores a const `BlockId` initialized by protected constructor.

Control flow: Concrete implementations provide storage-specific data access and mutation. `blockId` returns the immutable ID held by the base.

State and persistence behavior: The base class only stores identity. Persistence and flush semantics are implementation-specific: fake blocks flush on destruction, wrappers forward, real stores may write immediately or lazily.

Dependencies and integration points: All C++ blockstores return `unique_ref<Block>` through `BlockStore`. Higher blob/filesystem layers use this as the unit of encrypted block data.

Risks: `data()` returns a raw pointer with lifetime and mutability semantics defined only by implementations. `write` and `resize` have no base-level bounds/error contract beyond implementation assertions. TODO notes a potential design change to make `Block` non-virtual and store a pointer to its blockstore for write-back.

Test signals: Every concrete block implementation and blockstore test validates this interface indirectly.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/interface/Block.h` completely for this pass (39 lines, 949 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/interface/Block.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/interface/BlockStore.h -->
# sources/security-integrity/cryfs/old-cpp/src/blockstore/interface/BlockStore.h

Purpose: Defines the abstract blockstore interface for creating, loading, overwriting, removing, enumerating, sizing, and flushing blocks.

Important APIs and types: `BlockStore` declares `createBlockId`, `tryCreate`, `load`, `overwrite`, `remove(id)`, `numBlocks`, `estimateNumFreeBytes`, `blockSizeFromPhysicalBlockSize`, `forEachBlock`, `flushBlock`, and provides default `remove(unique_ref<Block>)` and `create(data)`.

Control flow: `create(data)` loops generating IDs and calling `tryCreate` until an unused ID succeeds, copying data for each attempt. Default `remove(unique_ref<Block>)` captures the block ID, destroys the handle with `cpputils::destruct`, then removes by ID. Concrete stores implement all persistence behavior and optional load/create failures.

State and persistence behavior: Interface itself has no state. Implementations decide whether blocks are durable, cached, copied, flushed on destruction, or immediately written. `flushBlock` is the explicit hook for wrappers/caches to persist an open block.

Dependencies and integration points: Uses `Block`, `BlockId`, `boost::optional`, cpp-utils `unique_ref`, and `cpputils::Data`. It is the central contract implemented by fake, mock, parallel access, caching, rustbridge, and real stores.

Risks: `load` TODO says it should use optional semantics, but it already does; comments still mention nullptr. The infinite create loop assumes random ID collisions eventually stop and `tryCreate` failures only indicate existing IDs. Passing `Data` by value can copy unless callers move. Remove-by-handle destroys the block before removing by ID, which matters for implementations whose destructor flushes stale data.

Test signals: Concrete blockstore suites should test ID collision handling, create/load/overwrite/remove semantics, enumeration, free-byte estimates, physical/logical block sizing, and flush behavior.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/interface/BlockStore.h` completely for this pass (57 lines, 2001 bytes).
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/interface/BlockStore.h -->
