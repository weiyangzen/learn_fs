# subset-b-008705 research

Grouped research report for RocksDB utility files. Each section preserves the source path in the title and is wrapped for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/mutexlock.h -->
# sources/storage-engines/rocksdb/util/mutexlock.h

## Purpose
Defines small synchronization helpers used throughout RocksDB: RAII wrappers for `port::Mutex` and `port::RWMutex`, a low-overhead `SpinMutex`, cache-line padding helpers, and a reusable `Striped` container for sharded locks or related synchronization objects.

## Important APIs, Types, And Functions
`MutexLock`, `ReadLock`, `WriteLock`, `TryReadLock`, and `TryWriteLock` acquire locks in constructors and release them in destructors; copy and assignment are deleted to preserve single ownership. `ReadUnlock` is a scoped read unlock helper for already-held `RWMutex` read locks. `SpinMutex` exposes `try_lock`, `lock`, and `unlock` with standard lockable naming so it can be used with STL lock guards. `CacheAlignedWrapper<T>` and `Unwrap<T>` support avoiding false sharing while still exposing the wrapped object. `Striped<T, Key, Hash>` allocates an array of stripes and maps keys to stripes using `hash_(key, seed)` and `FastRangeGeneric`.

## Control Flow
RAII lock classes are straight-line acquire/release wrappers. `SpinMutex::lock` repeatedly calls `try_lock`, pauses with `port::AsmVolatilePause`, and yields after 100 unsuccessful tries. `Striped::Get` hashes the key, maps the hash into `[0, stripe_count_)`, unwraps cache-aligned wrappers when needed, and returns the selected stripe object.

## State And Persistence
The lock wrappers store only a raw pointer and do not own lock storage. `SpinMutex` stores an atomic boolean using acquire/release semantics. `Striped` owns its stripe array through `std::unique_ptr<T[]>`, stores stripe count and hasher, and has no persistence or serialization behavior.

## Dependencies And Integration Points
Depends on `port/port.h` for mutex primitives, cache-line constants, alignment macros, and pause/yield support; `util/fastrange.h` and `util/hash.h` for striped hashing; and `SliceNPHasher64` as the default key hasher. It is integrated by concurrency-sensitive RocksDB code that wants scoped locking, striped locks, or cache-line-aligned contention points.

## Risks
The RAII wrappers assume the passed pointer stays valid and points to an unlocked or correctly held mutex for the operation. `SpinMutex` can waste CPU under long contention and is intended for low-contention regions. `Striped` does not validate `stripe_count_ > 0`; zero stripes would make `FastRangeGeneric` invalid. Cache alignment increases memory footprint and assumes `CACHE_LINE_SIZE` matches practical false-sharing boundaries.

## Test Signals
This file has no direct test in the assigned set, but it is exercised indirectly by rate limiter tests (`MutexLock`), repeatable thread tests, and other RocksDB synchronization tests. The debug assertions in dependent tests also exercise expected lock ownership and condition-variable behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/mutexlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/overload.h -->
# sources/storage-engines/rocksdb/util/overload.h

## Purpose
Provides a compact C++ helper for combining several function objects into one overload set, most commonly for `std::visit` over variants.

## Important APIs, Types, And Functions
`template <typename... Ts> struct overload : Ts...` inherits every functor and imports each `operator()` via a pack expansion. The class template argument deduction guide `overload(Ts...) -> overload<Ts...>` lets callers write `overload{lambda1, lambda2}` without naming template parameters.

## Control Flow
There is no runtime control flow beyond normal overload resolution. Construction stores the provided base functors and invocation dispatches to the matching inherited call operator.

## State And Persistence
State is exactly the captured state of the supplied functors. The helper owns that state by value through base subobjects and has no persistence behavior.

## Dependencies And Integration Points
Only depends on RocksDB namespace definition. It integrates with modern C++ code using variants or visitors and avoids writing bespoke visitor structs.

## Risks
Ambiguous overloads or overlapping generic lambdas can still produce compile errors. Since functors are inherited by value, large captures or reference lifetimes remain the caller's responsibility.

## Test Signals
No direct tests in this subset. Compile-time use sites are the primary signal; failures generally appear as overload-resolution or lifetime bugs in callers.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/overload.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/ppc-opcode.h -->
# sources/storage-engines/rocksdb/util/ppc-opcode.h

## Purpose
Defines PowerPC/VSX instruction encoding macros for assemblers that need explicit `.long` encodings of particular PPC vector instructions.

## Important APIs, Types, And Functions
Register-field macros `__PPC_RA`, `__PPC_RB`, `__PPC_XA`, `__PPC_XB`, `__PPC_XS`, and `__PPC_XT` assemble register indices into instruction bit fields. `VSX_XX3` and `VSX_XX1` combine VSX register fields. Opcode constants cover `VPMSUMW`, `VPMSUMD`, `MFVSRD`, and `MTVSRD`. Public instruction macros emit `.long PPC_INST_* | encoded_operands`.

## Control Flow
There is no C++ control flow. These are preprocessor macros consumed inside assembly contexts.

## State And Persistence
No state is stored. The macros affect emitted machine code at compile/assembly time.

## Dependencies And Integration Points
No includes beyond the license guard. This header is intended for PPC-specific optimized code paths, likely hashing/checksum routines that need vector polynomial multiply and VSX register transfer opcodes.

## Risks
Macros are untyped and can be misused with out-of-range register numbers; masking truncates values to field widths. The `.long` expansion is assembler-specific and only valid in the right architecture and inline-assembly context. Incorrect encodings produce illegal instructions or silent data corruption in low-level optimized paths.

## Test Signals
No direct test in this subset. Coverage is expected through PPC builds and tests of optimized checksum/hash code paths that include this header.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/ppc-opcode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/prefix_varint.h -->
# sources/storage-engines/rocksdb/util/prefix_varint.h

## Purpose
Implements a little-endian prefix-varint encoding where the number of trailing zero bits in the first byte determines encoded length. It is designed for callers that can read one byte first and then fetch the remaining bytes, and for potentially faster in-memory decoding than continuation-bit varints.

## Important APIs, Types, And Functions
Constants define maximum lengths: `kMaxPrefixVarint32Length == 5`, `kMaxPrefixVarint64Length == 9`, and the invalid 32-bit additional-byte sentinel. `PrefixVarint32Length` and `PrefixVarint64Length` compute minimal encoded length. `EncodePrefixVarint32`, `EncodePrefixVarint64<kMinimumBytes>`, `PutPrefixVarint32`, and `PutPrefixVarint64` encode values into buffers or strings. `PrefixVarint32AddlByteCount` and `PrefixVarint64AddlByteCount` support split reads. `DecodePrefixVarint32`, `DecodePrefixVarint64`, `GetPrefixVarint32Ptr`, `GetPrefixVarint64Ptr`, `GetPrefixVarint32`, and `GetPrefixVarint64` decode from byte spans or `Slice`.

## Control Flow
Encoding computes the number of bytes from the highest set bit, shifts payload bits left by the encoded length, and sets the prefix marker bit. `PrefixVarint64` switches to a special nine-byte form when the first byte is zero, followed by fixed64 payload bytes. Decoding optimizes the one-byte case, then determines required additional bytes from the first byte, assembles a little-endian encoded word, shifts off the prefix bits, and validates 32-bit overflow where applicable. Slice adapters advance only after successful decoding.

## State And Persistence
All functions are stateless inline helpers. The encoded bytes are durable data format state for any caller that persists them. The format is intentionally distinct from RocksDB's continuation-bit varints; compatibility must be explicit at call sites.

## Dependencies And Integration Points
Depends on `rocksdb/slice.h`, `util/coding_lean.h` for fixed64 encode/decode, `util/math.h` for `FloorLog2` and trailing-zero counts, `util/cast_util.h`, and branch prediction macros. It can integrate with storage or block-format code that wants length-known-after-first-byte reads.

## Risks
Format confusion with existing varint helpers would corrupt decoding. `DecodePrefixVarint64` treats first byte zero as the valid nine-byte form and fails only for insufficient bytes; callers must enforce canonical encoding if needed. Non-minimal 64-bit encodings are possible through `kMinimumBytes`, so consumers should not assume minimality unless the producer contract guarantees it. Inline byte-at-a-time load/store has TODO performance caveats.

## Test Signals
No assigned direct test, but the API is written with explicit boundary checks for truncated inputs, invalid 32-bit prefixes, and uint32 overflow. Future tests should cover canonical lengths, all boundary transitions, the 9-byte uint64 path, Slice no-advance-on-failure behavior, and non-minimal `kMinimumBytes` encoding.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/prefix_varint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/random.cc -->
# sources/storage-engines/rocksdb/util/random.cc

## Purpose
Provides out-of-line implementations for RocksDB's lightweight deterministic random generator string helpers and per-thread random instance.

## Important APIs, Types, And Functions
`Random::GetTLSInstance` constructs a thread-local `Random` in aligned storage using the current thread id hash as seed. `Random::HumanReadableString`, `Random::RandomString`, and `Random::RandomBinaryString` fill strings with lowercase letters, printable ASCII, or binary-ish byte values respectively.

## Control Flow
`GetTLSInstance` checks a `thread_local` pointer and placement-news a `Random` into `thread_local` aligned storage on first use. String methods resize the return string and fill each byte using `Uniform`.

## State And Persistence
State is per-thread process memory: a `thread_local Random*` and backing aligned storage. It is not persisted and intentionally avoids locking. The placement-created `Random` has thread lifetime and no explicit destructor path.

## Dependencies And Integration Points
Depends on `util/random.h`, `port/likely.h`, `util/aligned_storage.h`, and thread id hashing. Used by tests and internal randomized operations needing cheap deterministic-ish randomness without cryptographic guarantees.

## Risks
The TLS seed is derived from `std::hash<std::thread::id>()`, so it is not reproducible across implementations and not secure. `RandomBinaryString` uses `Uniform(CHAR_MAX)`, which excludes `CHAR_MAX` and is not full-byte entropy if `char` has 8 bits. String methods inherit modulo bias from `Random::Uniform`.

## Test Signals
`random_test.cc` covers distribution properties for `Uniform`, `OneIn`, `OneInOpt`, and `PercentTrue`, indirectly validating the generator used by these helpers but not the string helpers or TLS initialization.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/random.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/random.h -->
# sources/storage-engines/rocksdb/util/random.h

## Purpose
Defines several non-cryptographic random utilities: a LevelDB-style deterministic linear congruential generator, wrappers around `std::mt19937` and `std::mt19937_64`, and seeded shuffle helpers.

## Important APIs, Types, And Functions
`Random` exposes `Next`, `Next64`, `Uniform`, `OneIn`, `OneInOpt`, `PercentTrue`, `Skewed`, string generators, `Reset`, and `GetTLSInstance`. `Random32` wraps `std::mt19937` with exact `Next`, uniform distribution, faster approximate `Uniformish`, `OneIn`, `Skewed`, and reseeding. `Random64` wraps `std::mt19937_64`. `RandomShuffle` replaces removed `std::random_shuffle`, either with caller seed or `std::random_device`.

## Control Flow
`Random::Next` computes `(seed * 16807) % (2^31 - 1)` using the Mersenne modulus reduction trick, ensuring seed zero is remapped to one. Higher-level helpers consume `Next` or uniform distributions. `Skewed` first chooses a bit-width then chooses uniformly below `2^width`.

## State And Persistence
`Random` stores a 31-bit seed in memory and can be reset. `Random32` and `Random64` store C++ standard PRNG engines. None persist state except through object lifetime; seeded construction gives reproducible streams within the same algorithm guarantees.

## Dependencies And Integration Points
Depends on `<random>`, `<algorithm>`, and RocksDB namespace. Used broadly in tests, randomized sampling, and helper utilities where speed and repeatability matter more than cryptographic quality.

## Risks
`Random::Uniform(int n)` uses modulo reduction and requires `n > 0`; callers must avoid zero and negative values except through optional helpers. `PercentTrue` calls `Uniform(100)` before comparing with the percentage, so it still consumes randomness for out-of-range percentages. `Random32` and `Random64` use standard distributions whose exact sequence can be less stable across library implementations for higher-level methods. None of these APIs are secure randomness.

## Test Signals
`random_test.cc` statistically checks `Uniform`, `OneIn`, `OneInOpt`, and `PercentTrue` over several seeds and ranges. It does not test `Random32`, `Random64`, `Skewed`, shuffle, string generation, or TLS behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/random.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/random_test.cc -->
# sources/storage-engines/rocksdb/util/random_test.cc

## Purpose
Provides regression tests for selected `Random` distribution helpers.

## Important APIs, Types, And Functions
The tests instantiate `ROCKSDB_NAMESPACE::Random` and exercise `Uniform`, `OneIn`, `OneInOpt`, and `PercentTrue`. `main` installs RocksDB's stack trace handler and runs GoogleTest.

## Control Flow
`Uniform` builds histograms for multiple seeds and ranges and checks counts against a loose variance band. `OneIn` counts hits over `average * range` samples and handles range one as deterministic true. `OneInOpt` includes non-positive inputs and expects zero hits for those. `PercentTrue` samples 10,000 times for percentages from negative through above 100 and compares rounded observed percentage.

## State And Persistence
Test state is local counters and vectors. No files or persistent state are written.

## Dependencies And Integration Points
Depends on `util/random.h` and `test_util/testharness.h`. It validates behavior relied on by RocksDB randomized tests and components such as the rate limiter's fairness randomization.

## Risks
Statistical tests are intentionally loose and could miss subtle bias. The `OneInOpt` loop uses `average * range`; for negative ranges the loop count is negative and therefore zero iterations, which matches the expected zero but does not directly call `OneInOpt` with negative inputs. Tests do not cover newer generators or string helpers.

## Test Signals
The file itself is the assigned test signal: distribution bounds for `Uniform`/`OneIn`, boundary behavior for optional probability, and deterministic always-false/always-true behavior for percentages outside `[1, 99]`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/random_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/rate_limiter.cc -->
# sources/storage-engines/rocksdb/util/rate_limiter.cc

## Purpose
Implements RocksDB's generic token-bucket-style rate limiter for reads and writes with priority queues, fairness randomization, dynamic rate updates, optional auto tuning, and cooperative sleeping/refilling by requester threads.

## Important APIs, Types, And Functions
`RateLimiter::RequestToken` clamps requests to burst size, aligns direct I/O requests, and delegates to `Request`. `GenericRateLimiter::Request` is the main blocking token request path. `SetBytesPerSecond`, `SetSingleBurstBytes`, `GeneratePriorityIterationOrderLocked`, `RefillBytesAndGrantRequestsLocked`, `CalculateRefillBytesPerPeriodLocked`, `TuneLocked`, and `NewGenericRateLimiter` implement configuration, scheduling, accounting, and factory behavior. Internal `Req` tracks original bytes, remaining bytes, and a condition variable.

## Control Flow
Requests first consume `available_bytes_` if present, then enqueue a stack-local `Req` in the priority queue. Queued requester threads coordinate under `request_mutex_`: one waits until `next_refill_us_`, while another performs refill and grants queued requests. Refill resets `available_bytes_`, generates a priority iteration order with `IO_USER` first and randomized fairness among high/mid/low, then grants full or partial requests from queue fronts. Destruction sets `stop_`, signals queued requests, and waits for each blocked request to exit.

## State And Persistence
All limiter state is in memory: atomics for rate, refill bytes, and burst size; counters for requests and bytes-through; queues per `Env::IOPriority`; refill timing; fairness RNG; auto-tune counters; and the injected `SystemClock`. There is no persistence. Accounting totals are guarded by `request_mutex_`.

## Dependencies And Integration Points
Depends on `rocksdb/rate_limiter.h`, `rocksdb/env.h`, `rocksdb/system_clock.h`, `monitoring/statistics_impl.h`, `test_util/sync_point.h`, `util/mutexlock.h`, and `util/random.h`. It integrates with RocksDB Env I/O code through `RateLimiter`, with statistics through `RecordTick(NUMBER_RATE_LIMITER_DRAINS)`, and with tests through sync points and injectable clocks.

## Risks
Correctness depends on every queued `Req` being stack-live while queued and removed before return. Sleep/refill coordination is subtle; missed signals can hang requests. Dynamic rate reductions can make queued requests larger than refill size, so partial grants are required. `RequestToken` may request at least one alignment unit even above burst for direct I/O. Auto tuning uses drain percentage heuristics and can oscillate or underutilize if workload signals are misleading. Destructor wake-up must not race with incoming requests.

## Test Signals
`rate_limiter_test.cc` covers start/stop, overflow-safe refill calculation, total bytes/requests accounting, pending request accounting via sync points, mode filtering, priority iteration order, approximate rate limiting under concurrency, dynamic limit changes, partial available-byte exhaustion, auto tuning increase/decrease, a historical wait-hanging bug, and runtime single-burst changes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/rate_limiter.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/rate_limiter_impl.h -->
# sources/storage-engines/rocksdb/util/rate_limiter_impl.h

## Purpose
Declares `GenericRateLimiter`, the concrete implementation behind RocksDB's public `RateLimiter` factory.

## Important APIs, Types, And Functions
The class overrides `SetBytesPerSecond`, `SetSingleBurstBytes`, `Request`, `GetSingleBurstBytes`, `GetTotalBytesThrough`, `GetTotalRequests`, `GetTotalPendingRequests`, and `GetBytesPerSecond`. `TEST_SetClock` allows tests to replace the clock. Private helpers handle refill/grant, priority ordering, refill-byte calculation, auto tuning, and locked rate updates.

## Control Flow
Public methods acquire `request_mutex_` for shared state except atomic getters. `GetSingleBurstBytes` returns explicit burst size or current refill bytes when raw burst is zero. Aggregate getters sum arrays over all priorities when passed `Env::IO_TOTAL`. `NowMicrosMonotonicLocked` derives monotonic microseconds from the current clock's nanosecond source.

## State And Persistence
The class stores the refill period, atomics for rate/refill/burst, a mutable clock, stop flag, condition variable for destructor exit, per-priority totals and queues, available bytes, next refill time, fairness RNG, wait/refill coordination flag, and auto-tune state. No durable state exists.

## Dependencies And Integration Points
Includes RocksDB Env, RateLimiter, Status, SystemClock, `util/mutexlock.h`, and `util/random.h`. It is included by `rate_limiter.cc` and tests needing direct construction or clock injection.

## Risks
The header exposes many implementation details to tests but not to public API consumers. Atomic values are relaxed because the mutex protects operational state; incorrect future reads outside the mutex could observe stale values. Priority arrays are indexed by `Env::IOPriority` enum values and depend on enum layout. Queue entries are raw pointers to stack objects owned by blocked request calls.

## Test Signals
The direct-construction tests in `rate_limiter_test.cc` validate getters, dynamic setters, pending queue reporting, test clock injection, and behavior under edge conditions such as overflow and custom burst sizing.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/rate_limiter_impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/rate_limiter_test.cc -->
# sources/storage-engines/rocksdb/util/rate_limiter_test.cc

## Purpose
Tests `GenericRateLimiter` behavior across accounting, priority scheduling, timing, dynamic configuration, and historical concurrency bugs.

## Important APIs, Types, And Functions
Test cases include `OverflowRate`, `StartStop`, `GetTotalBytesThrough`, `GetTotalRequests`, `GetTotalPendingRequests`, `Modes`, `GeneratePriorityIterationOrder`, `Rate`, `LimitChangeTest`, `AvailableByteSizeExhaustTest`, `AutoTuneIncreaseWhenFull`, `WaitHangingBug`, and `RuntimeSingleBurstBytesChange`.

## Control Flow
Tests use direct construction and `NewGenericRateLimiter`, invoke `Request` with different `Env::IOPriority` values and op types, spawn writer threads through Env or `std::thread`, and use `SyncPoint` dependencies/callbacks to observe internal states while locks are temporarily released. Mock and special clocks advance refill time deterministically for several tests.

## State And Persistence
State is test-local. The fixture clears sync point callbacks in its destructor to avoid cross-test contamination. No persistent files are written.

## Dependencies And Integration Points
Depends on DB test utilities, mock time env, sync points, RocksDB clock, random generator, and `rate_limiter_impl.h`. It validates integration with statistics in auto-tune tests and with Env thread launching in throughput tests.

## Risks
The `Rate` test is timing-sensitive and explicitly skips minimum-rate assertions under slow CI/valgrind-style environments. Sync-point tests are tightly coupled to internal labels and mutex timing. The coverage is broad but still probabilistic for throughput and fairness behavior.

## Test Signals
The strongest signals are deterministic sync-point checks for pending queues, priority order permutations, limit-change starvation, partial-byte accounting, the wait-hanging regression, and burst-size runtime semantics. Timing tests bound actual throughput to no more than 1.25x target and usually at least 0.80x target.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/rate_limiter_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/repeatable_thread.h -->
# sources/storage-engines/rocksdb/util/repeatable_thread.h

## Purpose
Defines `RepeatableThread`, a small wrapper around `port::Thread` that repeatedly invokes a callback after an initial delay and then at a fixed microsecond interval until cancelled.

## Important APIs, Types, And Functions
The constructor takes a function, thread name suffix, `SystemClock*`, delay, and optional initial delay, then starts the thread. `cancel` stops the loop, wakes the condition variable, and joins the thread. `IsRunning` returns the running flag. In debug builds, `TEST_WaitForRun` lets tests wait until the worker is sleeping, run a callback such as clock advancement, then wait for one callback execution.

## Control Flow
The thread sets a platform thread name where supported, waits for the initial delay, then repeatedly runs `function_` and calls `wait(delay_us_)`. `wait` holds an `InstrumentedMutex`, computes an absolute wake time from `clock_->NowMicros()`, performs timed waits until time has advanced enough or cancellation occurs, and returns whether the loop should continue. Cancellation flips `running_` under the mutex and signals all waiters before joining.

## State And Persistence
Stores callback, thread name, raw clock pointer, delays, instrumented mutex/condition variable, running flag, and debug-only waiting/run counters. There is no persistence; lifetime is tied to the object and destructor cancels automatically.

## Dependencies And Integration Points
Depends on RocksDB instrumented mutex/condition-variable types, `port::Thread`, `SystemClock`, and scoped locks. It integrates with background maintenance tasks that need periodic callbacks, and tests can use mock clocks through `TEST_WaitForRun`.

## Risks
`IsRunning` reads `running_` without locking, which can be a data race if called concurrently with `cancel`. The constructor asserts `delay_us_ > 0` in the thread body despite the class comment saying zero means repeated calls without delay; this mismatch is a behavioral risk. `clock_` is a raw pointer and must outlive the thread. `function_` exceptions are not handled. `cancel` must not be called from the repeatable thread itself because it joins.

## Test Signals
`repeatable_thread_test.cc` validates real-time periodic execution and cancellation, plus deterministic mock-clock execution with debug-only `TEST_WaitForRun`. A macOS debug workaround uses sync points to avoid immediate timed-wait return causing hangs.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/repeatable_thread.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/repeatable_thread_test.cc -->
# sources/storage-engines/rocksdb/util/repeatable_thread_test.cc

## Purpose
Tests periodic callback execution and cancellation behavior for `RepeatableThread`.

## Important APIs, Types, And Functions
`TimedTest` uses a real `SystemClock`, a `port::Mutex`, and a condition variable to wait for three callback executions at roughly one-second spacing. `MockEnvTest` uses `MockSystemClock` and debug-only `TEST_WaitForRun` to advance mocked time and assert exact callback count.

## Control Flow
`TimedTest` increments a counter in the callback, checks elapsed real time between iterations, signals the test once enough iterations have run, then cancels. `MockEnvTest` starts with time zero, waits for the worker to enter timed wait, advances the mock clock before signaling, and repeats for three iterations.

## State And Persistence
All state is local counters, atomics, mutexes, condition variables, and a shared mock clock. No persistent state is written.

## Dependencies And Integration Points
Depends on DB test utilities, mock time env, sync points, and the repeatable thread header. It also exercises `InstrumentedCondVar::TimedWaitInternal` via sync-point callback on macOS debug builds.

## Risks
The real-time test can be slow or flaky on overloaded systems because it waits for seconds. The mock-clock path depends on debug-only APIs and platform-specific timed wait behavior. The tests do not cover zero-delay behavior despite the header comment mentioning it.

## Test Signals
The tests validate callback repetition, fixed-delay waiting, cancellation join behavior, mock-clock integration, and a macOS-specific timed-wait hang avoidance path.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/repeatable_thread_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/ribbon_alg.h -->
# sources/storage-engines/rocksdb/util/ribbon_alg.h

## Purpose
Defines the generic core algorithms for Ribbon PHSFs and Ribbon filters: incremental banding over GF(2), optional backtracking, back-substitution, and query routines for simple and interleaved solution layouts.

## Important APIs, Types, And Functions
Concept-style contracts document required hasher, banding storage, backtrack storage, and solution storage APIs. `BandingAdd` inserts one equation into an upper-triangular band matrix. `BandingAddRange` processes input ranges with optional prefetch and rollback. `SimpleBackSubst`, `SimpleQueryHelper`, `SimplePhsfQuery`, and `SimpleFilterQuery` support row-major solutions. `BackSubstBlock`, `InterleavedBackSubst`, `InterleavedPrepareQuery`, `InterleavedPhsfQuery`, and `InterleavedFilterQuery` support the serialized interleaved layout.

## Control Flow
Banding hashes each input to a start, coefficient row, and result row, then performs on-the-fly Gaussian elimination by XORing with an occupied row at the same leading column until an empty row is found or the equation reduces to zero. On failure, optional backtracking clears rows written during the batch. Back-substitution walks slots backward, maintaining column-major state for the last `kCoeffBits` solution rows. Query paths hash the key, compute start and coefficients, load one or two solution blocks, parity the selected bits, and compare with expected result bits for filters.

## State And Persistence
The algorithms themselves are stateless templates; state lives in caller-provided storage. Banding storage represents an intermediate upper-triangular system. Solution storage represents the final PHSF/filter data and may be persisted by concrete implementations. Backtracking storage is transient and clears rows on failed speculative adds.

## Dependencies And Integration Points
Depends on `util/math128.h` and math/bit primitives such as `CountTrailingZeroBits` and `BitParity`. It is consumed by `ribbon_impl.h`, which supplies standard storage and hasher implementations, and by Ribbon tests. Integration is template-based, so compile-time type compatibility and unsigned integer sizes are enforced through `static_assert`.

## Risks
The algorithms assume coefficient rows are non-zero and storage contracts are honored. If `kFirstCoeffAlwaysOne` is incorrectly declared, banding can misplace equations. Backtracking only works if the backtrack storage can record every row written in the batch. Interleaved query logic is sensitive to block boundaries, start-bit shifts, segment counts, and fractional-column configuration. Homogeneous filters intentionally fill unconstrained rows differently in concrete storage, affecting false positive behavior.

## Test Signals
`ribbon_test.cc` stress-tests these algorithms through many `TypesAndSettings`: construction success/reseed rates, backtracking rollback, false-positive distribution, simple vs interleaved equivalence, PHSF mapping correctness, zero-start behavior, and occupancy exploration tooling.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/ribbon_alg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/ribbon_config.cc -->
# sources/storage-engines/rocksdb/util/ribbon_config.cc

## Purpose
Implements Ribbon configuration lookup tables and interpolation logic that translate between number of slots and number of addable entries for selected construction failure probabilities.

## Important APIs, Types, And Functions
`BandingConfigHelperData<kCfc, kCoeffBits, kUseSmash>` stores known addable-entry counts at powers-of-two slot sizes and factor formulas for larger sizes. Explicit specializations provide data for 64-bit and 128-bit coefficient rows, smash and non-smash variants, and failure chances `kOneIn2`, `kOneIn20`, and `kOneIn1000`. `GetNumToAdd` and `GetNumSlots` implement interpolation and inverse interpolation. The file explicitly instantiates supported combinations with homogeneous and non-homogeneous variants.

## Control Flow
`GetNumToAdd` computes `log2(num_slots)`, interpolates between known power-of-two table entries when within the table, or uses a large-value overhead factor formula. Homogeneous configurations subtract eight from addable count as an empirical correction. `GetNumSlots` reverses this by adjusting homogeneous counts, choosing nearby power-of-two anchors, interpolating required slots, and rounding up.

## State And Persistence
Static lookup tables are compile-time program data. There is no runtime mutable state or persistence.

## Dependencies And Integration Points
Depends on `ribbon_config.h`, `<array>`, and `<cmath>`. The values are consumed by filter construction planning to choose slot counts for a target construction success probability. The data is derived from `FindOccupancy` tooling in `ribbon_test.cc`.

## Risks
The tables are empirical and only supported for 64- and 128-bit coefficient rows. Unsupported instantiations assert if used. Interpolation is approximate and assumes the observed distribution remains valid. Homogeneous correction is explicitly empirical and "mostly affecting small filter configurations." Large `num_to_add` values are documented as needing headroom below uint32 overflow.

## Test Signals
`ribbon_test.cc` uses `BandingConfigHelper` in compactness and construction-success tests and includes `FindOccupancy` tooling that generated the table data. Tests check reseed counts against expected failure rates.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/ribbon_config.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/ribbon_config.h -->
# sources/storage-engines/rocksdb/util/ribbon_config.h

## Purpose
Declares the Ribbon configuration API for estimating addable entries from slots and slots from entries under bounded construction failure probabilities.

## Important APIs, Types, And Functions
`ConstructionFailureChance` enumerates `kOneIn2`, `kOneIn20`, and `kOneIn1000`. `BandingConfigHelper1<kCfc, kCoeffBits, kUseSmash, kHomogeneous>` exposes compile-time failure-chance helpers. `BandingConfigHelper1TS` derives parameters from `TypesAndSettings`. `BandingConfigHelper<TypesAndSettings>` offers runtime selection of failure chance and defaults to `kOneIn1000` for homogeneous filters or `kOneIn20` otherwise.

## Control Flow
The runtime helper switches on `ConstructionFailureChance` and dispatches to the corresponding template instantiation. Unsupported settings inherit an assert-only implementation that returns zero.

## State And Persistence
No mutable state. The API is a pure configuration calculation interface backed by implementation tables in `ribbon_config.cc`.

## Dependencies And Integration Points
Depends on RocksDB namespace, `port/lang.h` for fallthrough annotations, and standard math/array headers. It integrates with `ribbon_impl.h` consumers selecting filter sizes before building `StandardBanding` and solution storage.

## Risks
Only 64- and 128-bit coefficient rows are supported by the data-backed implementation. Callers must still round slots for the chosen solution layout, especially interleaved layout. Failure chance is per seed; total construction failure after reseeding depends on seed count. Homogeneous filters should not use failure chance looser than the target false-positive rate.

## Test Signals
Ribbon tests consume this API across many settings and compare empirical reseed rates and false-positive rates. The `FindOccupancy` test/tool is the source of the data used by the implementation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/ribbon_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/ribbon_impl.h -->
# sources/storage-engines/rocksdb/util/ribbon_impl.h

## Purpose
Provides standard concrete Ribbon hasher, banding storage, and solution storage implementations parameterized by a `TypesAndSettings` concept.

## Important APIs, Types, And Functions
`AddInputSelector` chooses key-only inputs for filters or key/result pairs for PHSFs. `StandardHasher` implements hashing, start selection, coefficient-row generation, result-row derivation, raw/ordinal seed translation, and seed premixing. `StandardRehasherAdapter`/`StandardRehasher` support building filters from existing hashes. `ExpectedCollisionFpRate` estimates hash-collision false positives. `StandardBanding` owns coefficient/result rows, supports `Reset`, `AddRange`, `AddRangeOrRollBack`, `Add`, `GetOccupiedCount`, `ResetAndFindSeedToSolve`, and memory estimation. `InMemSimpleSolution` and `SerializableInterleavedSolution` implement simple row-major and serializable interleaved solution storage.

## Control Flow
`StandardHasher::GetStart` maps hashes to starts using `FastRangeGeneric`, optionally "smashing" some range into front/back slots for better edge utilization. `GetCoeffRow` expands 32- or 64-bit hashes into coefficient rows, using alternate 128-bit multiplication for smash mode and ensuring non-zero or first-bit-one rows. `StandardBanding::ResetAndFindSeedToSolve` loops ordinal seeds, resets storage, and calls `AddRange` until construction succeeds or the seed mask wraps. Solution storage calls generic back-substitution and then answers PHSF/filter queries through simple or interleaved query algorithms.

## State And Persistence
`StandardHasher` stores only `raw_seed_`. `StandardBanding` owns mutable construction arrays and backtrack storage; this is temporary build state. `InMemSimpleSolution` owns in-memory solution rows. `SerializableInterleavedSolution` does not own its external byte buffer, but encodes/decodes little-endian `CoeffRow` segments into it and adjusts effective `data_len_` to the number of usable segments; this buffer is the persistence-ready filter/PHSF payload.

## Dependencies And Integration Points
Depends on `ribbon_alg.h`, `port/port.h` for prefetch/cache constants, and `util/fastrange.h`. It integrates with Ribbon configuration helpers, RocksDB filter construction, and tests. The `IMPORT_RIBBON_IMPL_TYPES` macro gives convenient aliases for template-heavy callers.

## Risks
`TypesAndSettings` must provide compatible unsigned types and a high-quality seeded hash. Seed premixing compensates for some weak sequential-seed behavior but is not a full hash. `SerializableInterleavedSolution` borrows a buffer and assumes it remains valid and suitably sized/aligned for byte access. Zero-start and zero-byte cases intentionally return always false or always true depending on configuration and can surprise callers. Fractional-column FP calculations approximate smash effects. Rehasher mode is not recommended for general PHSFs because original hash collisions can block construction.

## Test Signals
`ribbon_test.cc` exercises a large matrix of settings: coefficient widths, smash, homogeneous mode, result widths, index sizes, 32-bit hashes, string keys, seed widths, no-first-bit mode, zero starts, rehasher variants, and small-key generators. Tests compare simple and interleaved solutions, expected FP rates, raw/ordinal seed reversibility, and PHSF value recovery.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/ribbon_impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/ribbon_test.cc -->
# sources/storage-engines/rocksdb/util/ribbon_test.cc

## Purpose
Provides broad validation and measurement tooling for Ribbon PHSF/filter implementations, configuration tables, seed handling, storage layouts, and false-positive behavior.

## Important APIs, Types, And Functions
The file defines key generators, many `TypesAndSettings` variants, Poisson bound helpers, and tests `CompactnessAndBacktrackAndFpRate`, `Extremes`, `AllowZeroStarts`, `RawAndOrdinalSeeds`, `PhsfBasic`, plus tool-like tests `FindOccupancy` and `OptimizeHomogAtScale`. Optional gflags control thoroughness, occupancy generation, and homogeneous optimization runs.

## Control Flow
The main typed test samples filter sizes, chooses slot counts through `BandingConfigHelper`, builds banding with reseeding, tests rollback by forcing failed adds, optionally adds extra singles/batches, back-substitutes into simple and interleaved solutions, verifies all positives, measures false positives over non-added keys, and compares timing with Bloom queries. Other tests cover zero-key/zero-byte extremes, zero-start behavior, raw/ordinal seed bijection, and general PHSF key-to-value mapping.

## State And Persistence
All state is test-local buffers, counters, generated keys, and optional timing counters. It does not persist artifacts, although `FindOccupancy` prints empirical data used to populate `ribbon_config.cc`.

## Dependencies And Integration Points
Depends on RocksDB hash, coding, Bloom implementation, Ribbon config/impl headers, stopwatch, string utilities, gflags compatibility, and the test harness. It integrates with typed GoogleTest to exercise many compile-time configurations.

## Risks
Many checks are statistical and have configured standard-deviation tolerances, so rare failures are possible. Tool-like tests are bypassed unless flags are set, so occupancy/table regeneration is not part of normal regression runs. Timing output is informational. The test matrix is large but skips full support for coefficient rows smaller than 64 bits in the main compactness test.

## Test Signals
Strong signals include reseed-rate bounds matching configured construction failure chance, rollback leaving occupancy unchanged, no false negatives for added keys, FP counts matching expected simple/interleaved rates with hash-collision correction, interleaved FP rate not lower than simple when it uses a subset of bits, seed translation one-to-one behavior, and correct general PHSF value lookup.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/ribbon_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/semaphore.h -->
# sources/storage-engines/rocksdb/util/semaphore.h

## Purpose
Provides RocksDB wrappers for counting and binary semaphores, defaulting to mutex/condition-variable implementations while allowing opt-in use of C++20 standard semaphores.

## Important APIs, Types, And Functions
`CountingSemaphore` exposes `Acquire`, `TryAcquire`, and `Release(n)`. `BinarySemaphore` exposes `Acquire`, `TryAcquire`, and `Release`. When `ROCKSDB_USE_STD_SEMAPHORES` is defined, they wrap `std::counting_semaphore<INT32_MAX>` and `std::binary_semaphore`; otherwise they use `std::mutex`, `std::condition_variable`, and count/state fields.

## Control Flow
Counting acquire waits until `count_ > 0` then decrements. Try-acquire checks and decrements without blocking. Release validates non-negative `n`, increments count, and notifies one waiter for single release or all waiters for multi-release. Binary acquire waits for `state_` true then sets false; release asserts the semaphore is currently unavailable, sets true, and notifies one.

## State And Persistence
State is in-memory semaphore count or boolean state plus synchronization primitives. `CountingSemaphore` is cache-line aligned to reduce false sharing. No persistence exists.

## Dependencies And Integration Points
Depends on standard mutex/condition-variable and optionally `<semaphore>`, plus RocksDB port alignment/cache constants. Used by internal concurrency code needing semaphore semantics without relying by default on buggy standard library semaphore implementations.

## Risks
The default counting implementation can make `Release` briefly wait if another thread is preempted while holding the mutex. Overflow is guarded only by assertions. `BinarySemaphore::Release` asserts precondition in fallback mode to avoid undefined behavior that standard binary semaphores would have for over-release. The standard semaphore path is opt-in because comments document known indefinite-blocking and timeout bugs in implementations.

## Test Signals
No direct assigned test. Expected coverage is indirect through components using these semaphores, especially parallel compression or bounded worker coordination. Dedicated tests should cover blocking wake-up, try-acquire, multi-release notification, over-release assertions in debug, and std/fallback parity.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/semaphore.h -->
