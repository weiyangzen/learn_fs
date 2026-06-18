# subset-b-007050 Research

Grouped code research for EOS MGM statistics and the first tape-aware garbage-collector support slice. Each section preserves the source path in its title and is bounded by reconciliation markers for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/stat/Stat.cc -->
# sources/distributed-fs/eos/mgm/stat/Stat.cc

## Purpose
`Stat.cc` implements the MGM statistics accumulator declared in `Stat.hh`. It records per-command counters keyed by UID, GID, and optional FUSE application, tracks rolling request rates and extended sample/min/max aggregates, stores recent execution timings, prints table or monitoring output, and runs a circulation thread that advances circular buckets and optionally samples instrumented namespace/FsView/quota lock timing.

## Important APIs, Types, And Functions
Important methods include `Stat::Add()`, `AddExt()`, `AddExec()`, `GetTotal*()`, `GetExec()`, `GetTotalExec()`, `GetReadContention()`, `GetWriteContention()`, `Clear()`, `PrintOutTotal()`, and `Circulate()`. The implementation relies on `StatAvg` and `StatExt` bucket methods from the header, `TableFormatterBase` for presentation, `common::Statistics` for average/sigma/percentile calculations, and `common::Mapping` for UID/GID name translation.

## Control Flow
`Add()` and `AddExt()` take `mMutex` and update total, rolling-average, or extended maps. Execution timing samples are appended to a per-tag deque and capped at 100 samples. Getter methods assume their caller already holds the mutex except for contention helpers, which lock internally and query global `gOFS->MgmStats`. `PrintOutTotal()` locks, snapshots tags, builds an all-users table, optionally unlocks to translate UID/GID names, relocks, collects user/group/app rows, sorts them, and appends generated tables. `Circulate()` sleeps about 512 ms, optionally samples instrumented mutex counters, then stamps the next bucket of each rolling structure to zero.

## State And Persistence
All state is in memory under `Stat::mMutex`; there is no durable persistence. The class stores sparse maps by tag and identity, execution deques, and cumulative execution time. The circulation thread mutates bucket arrays to age out old samples, so values are time-window approximations rather than audit logs.

## Dependencies And Integration Points
The file integrates with MGM global `gOFS`, `FsView::gFsView`, quota locks, namespace locks, EOS table formatting, UID/GID mapping, and command timing macros in `Stat.hh`. Admin/monitoring code can call `PrintOutTotal()` to expose totals, rates, execution timings, and contention estimates.

## Risks And Edge Cases
Most getters are documented as requiring external locking; accidental unlocked use risks races. Extended weighted-average methods divide by total sample weight without guarding `totw == 0` when a tag exists but has no samples. `Clear()` iterates `StatsUid` and clears associated maps but does not explicitly iterate tags that exist only in extended maps. `Circulate()` stamps `StatExtGid` twice and does not stamp `StatExtUid`, which looks like a copy/paste bug affecting rolling extended UID windows. Manual `mMutex.Lock()`/`UnLock()` in `PrintOutTotal()` makes exception safety more fragile than RAII.

## Test Signals
Useful tests include rate-window aging, extended min/max/average aggregation with empty and non-empty sample sets, execution timing percentile output, monitoring and human table modes, app-only output, UID/GID translation while stats mutate, `Clear()` behavior for all maps, contention reporting under `EOS_INSTRUMENTED_RWMUTEX`, and sanitizer/TSAN coverage of concurrent `Add()` plus `PrintOutTotal()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/stat/Stat.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/stat/Stat.hh -->
# sources/distributed-fs/eos/mgm/stat/Stat.hh

## Purpose
`Stat.hh` declares the MGM statistics data model. It provides fixed-size circular rolling counters (`StatAvg`), extended rolling statistics with sample counts, weighted sums, minima, and maxima (`StatExt`), execution timing macros, and the `Stat` class that owns all per-tag statistics maps and reporting entry points.

## Important APIs, Types, And Functions
`StatAvg` exposes `Add()`, `StampZero()`, and `GetAvg3600()/GetAvg300()/GetAvg60()/GetAvg5()`. `StatExt` exposes `Insert()`, `StampZero()`, `GetN*()`, `GetAvg*()`, `GetMin*()`, and `GetMax*()` for the same windows. `EXEC_TIMING_BEGIN()` and `EXEC_TIMING_END()` wrap elapsed-time measurement and call `gOFS->MgmStats.AddExec()`. `Stat` declares maps for UID/GID/app totals, averages, extended stats, execution samples, cumulative times, and public methods implemented in `Stat.cc`.

## Control Flow
The header implements the bucket-update logic inline. `StatAvg::Add()` and `StatExt::Insert()` map `time(0)` into modulo buckets for 3600, 300, 60, and 5 second windows, zero the next bucket, then accumulate the current bucket. `StampZero()` performs the aging step without adding data. Getter methods scan all buckets to produce totals or derived values.

## State And Persistence
The structures are in-memory circular buffers with one bucket per second for each window length. `StatExt` initializes minima to a large signed value and maxima to the minimum `size_t` value. `Stat` persists process-lifetime sparse hash maps and a mutable XRootD mutex; no content is written to disk by this header.

## Dependencies And Integration Points
The header depends on EOS MGM namespace macros, `ThreadAssistant`, XRootD strings/mutexes, Google sparse hash maps, and the global `gOFS` pointer used by the timing macro. It is included by MGM command, stats, and monitoring code needing to record or expose command metrics.

## Risks And Edge Cases
The rolling buckets use wall-clock `time(0)` rather than monotonic time, so clock jumps can smear or clear buckets unexpectedly. Average methods divide by 3599, 299, 59, and 4 rather than by the array size, which is intentional-looking but should be validated. `StatExt::GetAvg*()` divides by the sample count without a zero guard. The macros require unique IDs and a valid `gOFS`; misuse can create shadowing or missing-stat effects.

## Test Signals
Header-level signals include compile coverage of all inline methods and timing macros. Runtime tests should force controlled timestamps if possible, verify bucket rotation, zero stamping, min/max initialization, zero-sample behavior, and that `EXEC_TIMING_END()` records samples only when `gOFS` exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/stat/Stat.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/AsyncResult.hh -->
# sources/distributed-fs/eos/mgm/tgc/AsyncResult.hh

## Purpose
`AsyncResult.hh` defines a small templated value object used to report the poll result of an asynchronous task that may still be running. It distinguishes pending-without-cache, pending-with-previous-value, successful value, and error states.

## Important APIs, Types, And Functions
`AsyncResult<Value>` contains enum `State`, `stateToStr()`, factory methods `createPendingAndNoPreviousValue()`, `createPendingAndPreviousValue()`, `createValue()`, and `createError()`, plus accessors `getState()`, `getPreviousValue()`, `getValue()`, and `getError()`. Values and errors are stored as `std::optional`.

## Control Flow
Construction is private so callers must use factory methods, which set exactly one state and populate the associated optional when appropriate. Consumers switch on `getState()` and then inspect the matching optional.

## State And Persistence
The object has no external persistence and owns only copied optionals. State is immutable by convention after factory construction, although the fields are not `const`.

## Dependencies And Integration Points
This template is used by `AsyncUint64ShellCmd` and `SmartSpaceStats` to poll an optional `tgc.freebytesscript` without blocking the main stats path. It depends only on EOS namespace macros, `<optional>`, and `<string>`.

## Risks And Edge Cases
The type does not enforce state/optional consistency beyond its factory methods; future direct member changes would be unsafe. Accessors return optionals by value, which is simple but copies large value types if instantiated with non-trivial payloads. The default branch in `stateToStr()` is defensive but should be unreachable.

## Test Signals
Tests should verify each factory's state and optional contents, string conversion for all enum values, and consumer behavior when pending states are returned with or without previous values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/AsyncResult.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/AsyncUint64ShellCmd.cc -->
# sources/distributed-fs/eos/mgm/tgc/AsyncUint64ShellCmd.cc

## Purpose
`AsyncUint64ShellCmd.cc` implements a one-command-at-a-time asynchronous shell-command poller. It starts a command through the `ITapeGcMgm` abstraction, parses stdout as `uint64_t`, and returns an `AsyncResult` describing readiness, cached previous output, or error.

## Important APIs, Types, And Functions
The implementation defines the constructor, `getUint64FromShellCmdStdOut()`, and `runShellCmdAndParseStdOut()`. It uses `std::async(std::launch::async)`, `std::future::wait_for(0s)`, `ITapeGcMgm::getStdoutFromShellCmd()`, and `CtaUtils::toUint64()`.

## Control Flow
`getUint64FromShellCmdStdOut()` locks `m_mutex`, starts a new async task when no future is valid, polls immediately, and returns one of: `VALUE` when the future is ready and parsed successfully, pending with prior result if a previous command succeeded, or pending without prior result. On any exception it clears the previous result and returns `ERROR`.

## State And Persistence
State is process-local: a mutex, MGM reference, optional previous result, and the current future. A successful ready result invalidates the future and makes the parsed value the previous result for later pending calls. Errors reset the previous result.

## Dependencies And Integration Points
The class is used by `SmartSpaceStats` for optional free-byte scripts. It delegates shell execution to `ITapeGcMgm`, so production uses `RealTapeGcMgm::getStdoutFromShellCmd()` and unit tests can use `DummyTapeGcMgm`.

## Risks And Edge Cases
The mutex is held while calling `future.get()`, so if task completion triggers expensive exception construction or cleanup, polling is serialized. The `cmdStr` parameter is only used to start a new command when no command is in flight; callers changing the command while a previous command runs still observe the older task. A parsing or shell error clears the previous result, causing subsequent pending states to fall back to internal stats.

## Test Signals
Tests should cover first pending, ready value, previous-value pending, parse failure, shell timeout/error propagation through the MGM interface, repeated calls while in flight, and command changes while an older future is still valid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/AsyncUint64ShellCmd.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/AsyncUint64ShellCmd.hh -->
# sources/distributed-fs/eos/mgm/tgc/AsyncUint64ShellCmd.hh

## Purpose
`AsyncUint64ShellCmd.hh` declares the asynchronous uint64 shell-command adapter used by tape-GC space statistics. It hides `std::future` management and exposes a poll-style API returning `AsyncResult<std::uint64_t>`.

## Important APIs, Types, And Functions
`AsyncUint64ShellCmd` has constructor `AsyncUint64ShellCmd(ITapeGcMgm&)`, alias `Uint64AsyncResult`, public `getUint64FromShellCmdStdOut(const std::string&)`, and private `runShellCmdAndParseStdOut(std::string)`. Members are `m_mutex`, `m_mgm`, `m_previousResult`, and `m_future`.

## Control Flow
The header-level contract says calls automatically launch a shell command if necessary and otherwise poll the current command. Only one command is active per instance, giving `SmartSpaceStats` stable previous-value semantics for one configured script path.

## State And Persistence
The class stores no durable data; it caches only the last successful integer and the in-flight future. Because the object owns a reference to `ITapeGcMgm`, it must not outlive the MGM adapter.

## Dependencies And Integration Points
It depends on `AsyncResult.hh`, `ITapeGcMgm.hh`, futures, mutexes, and strings. It is constructed inside `SmartSpaceStats`, which supplies the command string based on `SpaceConfig::freeBytesScript` and the space name.

## Risks And Edge Cases
The class is non-copyable by member composition but does not explicitly delete copy/move operations; future/mutex/reference members effectively prevent normal copying. Lifetime of the MGM reference is critical. The command interface is shell-string based, so production security depends on upstream script configuration and quoting.

## Test Signals
Compile tests should verify non-copy behavior. Runtime tests should use `DummyTapeGcMgm` to exercise value, pending, previous value, parse error, and concurrent caller serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/AsyncUint64ShellCmd.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/BlockingFlag.hh -->
# sources/distributed-fs/eos/mgm/tgc/BlockingFlag.hh

## Purpose
`BlockingFlag.hh` defines a simple condition-variable backed boolean flag. It starts false, can be waited on with a timeout, and can be set true to wake all waiters.

## Important APIs, Types, And Functions
`BlockingFlag` provides a constructor, `operator bool() const`, templated `waitForTrue(Duration) noexcept`, and `setToTrue()`. State is protected by `m_mutex` and waiters use `m_cond`.

## Control Flow
Readers lock the mutex and return the current flag. `waitForTrue()` waits for the predicate `m_flag` for the specified duration and catches/logs any exception before returning false. `setToTrue()` locks, sets the flag, and notifies all waiting threads.

## State And Persistence
State is one in-memory boolean. There is no reset API, so the object is a one-way latch from false to true.

## Dependencies And Integration Points
The file uses standard mutex and condition-variable primitives and EOS logging via `eos_static_err`. It is suitable for worker stop signals or test synchronization in the tape-GC subsystem.

## Risks And Edge Cases
`notify_all()` is called while holding the mutex; this is correct but may wake waiters that immediately contend for the lock. Because there is no reset, reusing the same object across lifecycle phases would leave it permanently true. The header relies on logging declarations being available through included namespace context or transitive includes.

## Test Signals
Tests should cover initial false state, timeout returning false, wakeup returning true, bool conversion after setting, multiple waiters, and repeated waits after the flag is already true.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/BlockingFlag.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/CachedValue.hh -->
# sources/distributed-fs/eos/mgm/tgc/CachedValue.hh

## Purpose
`CachedValue.hh` provides a generic time-based cache for a single value. Tape-GC uses it to avoid re-reading per-space configuration from the MGM on every stats or worker iteration.

## Important APIs, Types, And Functions
`CachedValue<ValueType>` has constructor `CachedValue(std::function<ValueType()>, std::time_t maxAgeSecs)` and method `get()`. Members include a mutex, first-use flag, cached value, value getter callback, max age, and last update timestamp.

## Control Flow
`get()` locks, computes age from `time(nullptr) - m_timestamp`, and refreshes the cached value when it has never been set or when age is at least `m_maxAgeSecs`. A max age of zero causes every call to refresh because `age >= 0`.

## State And Persistence
The cache is in-memory only. It stores the last value by copy and the timestamp of the refresh. The callback is invoked while the cache mutex is held, so only one thread refreshes at a time.

## Dependencies And Integration Points
The template depends on standard time, function, and mutex facilities. `SmartSpaceStats` and likely space-specific GC code use it around `ITapeGcMgm::getTapeGcSpaceConfig()`.

## Risks And Edge Cases
The callback runs under lock, so slow MGM reads block all cache readers. Wall-clock rollback can make a value live longer than intended; wall-clock forward jumps can force early refresh. Exceptions from `m_valueGetter` propagate and leave previous cache state unchanged except for any timestamp changes already made.

## Test Signals
Tests should verify first-call refresh, reuse before max age, refresh after max age, zero-age always-refresh behavior, concurrent callers, and exception behavior from the getter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/CachedValue.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/Constants.hh -->
# sources/distributed-fs/eos/mgm/tgc/Constants.hh

## Purpose
`Constants.hh` centralizes tape-aware garbage-collector defaults, limits, and EOS space configuration member names.

## Important APIs, Types, And Functions
Constants include config cache age, freed-byte histogram bin limits and defaults, query-period name and limits, target available bytes name/default, optional free-byte script name/default, and total-bytes name/default. Notable names are `TGC_NAME_QRY_PERIOD_SECS`, `TGC_NAME_AVAIL_BYTES`, `TGC_NAME_FREE_BYTES_SCRIPT`, and `TGC_NAME_TOTAL_BYTES`.

## Control Flow
There is no executable control flow. Other classes use these constants for constructor defaults, validation, config lookup, logging, and error messages.

## State And Persistence
No runtime state is owned. The string constants define the persisted EOS space configuration keys used by `FsSpace` config and admin commands.

## Dependencies And Integration Points
`SpaceConfig`, `FreedBytesHistogram`, `SmartSpaceStats`, `RealTapeGcMgm`, `FsView`, `DevicesCmd`, and `SpaceCmd` use these values. Defaults are written into space config in FsView initialization when missing.

## Risks And Edge Cases
`TGC_DEFAULT_TOTAL_BYTES` is set to 1 exabyte, effectively preventing GC until configured for real deployments. Query-period maximum is derived from histogram depth and max bin width; changes must stay consistent with histogram validation. The comment says "tape-ware" in one place, but the values are functional.

## Test Signals
Tests should assert default `SpaceConfig` values, admin validation of recognized keys, histogram limit enforcement, and behavior when query period approaches maximum allowed depth.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/Constants.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/DummyClock.hh -->
# sources/distributed-fs/eos/mgm/tgc/DummyClock.hh

## Purpose
`DummyClock.hh` provides a controllable `IClock` implementation for deterministic unit tests of time-dependent tape-GC components such as `FreedBytesHistogram`.

## Important APIs, Types, And Functions
`DummyClock` has constructor `DummyClock(std::time_t initialTime)`, override `getTime()`, and setter `setTime(std::time_t)`.

## Control Flow
`getTime()` returns the stored timestamp. Tests move time forward or backward by calling `setTime()`, then exercise consumers.

## State And Persistence
The class stores one in-memory `std::time_t`. There is no locking, so it is intended for single-threaded tests or externally synchronized use.

## Dependencies And Integration Points
It derives from `IClock` and is used by tests for histogram aging and bin-width behavior. Production code uses `RealClock`.

## Risks And Edge Cases
The class does not prevent negative timestamps, backward time movement, or concurrent modification. That is useful for tests but would be unsafe as a production clock.

## Test Signals
Tests should verify construction, `getTime()`, `setTime()`, and consumer behavior when time advances across multiple histogram bins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/DummyClock.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/DummyTapeGcMgm.cc -->
# sources/distributed-fs/eos/mgm/tgc/DummyTapeGcMgm.cc

## Purpose
`DummyTapeGcMgm.cc` implements the test double for the tape-GC MGM interface. It supplies configurable space config/stats, canned shell stdout, simple success responses for namespace/eviction APIs, and call counters for unit-test assertions.

## Important APIs, Types, And Functions
Implemented methods include `getTapeGcSpaceConfig()`, `getSpaceStats()`, `getFileSizeBytes()`, `fileInNamespaceAndNotScheduledForDeletion()`, `evictAsRoot()`, `getFsIdToSpaceMap()`, `getSpaceToDiskReplicasMap()`, `getStdoutFromShellCmd()`, setters for config/stats/stdout, and getter methods for call counters.

## Control Flow
Most methods lock `m_mutex`, update a counter when relevant, and return either configured data or defaults. `getFileSizeBytes()` always returns 1 and `fileInNamespaceAndNotScheduledForDeletion()` always returns true. Replica-map and FS-ID map methods return empty maps, making multi-space population complete quickly in tests.

## State And Persistence
State is in-memory and protected by `m_mutex`: maps from space to config/stats, counters, and shell stdout. No production state is touched.

## Dependencies And Integration Points
The dummy implements `ITapeGcMgm` and is used by unit tests for `CachedValue`, `SmartSpaceStats`, `MultiSpaceTapeGc`, `SpaceToTapeGcMap`, and likely `TapeGc`.

## Risks And Edge Cases
Some methods catch all exceptions and return defaults, which is convenient for tests but can hide test setup errors. `getStdoutFromShellCmd()` ignores `cmdStr` and `maxLen`, so it does not test length limits or command-specific behavior. Empty replica maps mean population tests do not cover large namespace scans unless extended.

## Test Signals
Tests should assert call counters, default fallbacks, configured space stat/config retrieval, stdout injection for async script parsing, and behavior of components when maps are empty.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/DummyTapeGcMgm.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/DummyTapeGcMgm.hh -->
# sources/distributed-fs/eos/mgm/tgc/DummyTapeGcMgm.hh

## Purpose
`DummyTapeGcMgm.hh` declares the in-memory test implementation of `ITapeGcMgm`. It allows tape-GC unit tests to run without a real XRootD MGM, namespace service, FsView, QuarkDB, or shell command.

## Important APIs, Types, And Functions
The class overrides all `ITapeGcMgm` methods and adds setters `setTapeGcSpaceConfig()`, `setSpaceStats()`, `setStdoutFromShellCmd()`, plus counter getters for config, stats, namespace checks, file-size checks, and eviction calls. Copy/move construction and assignment are deleted.

## Control Flow
Header declarations establish a simple fake: callers configure maps and stdout, then production code paths call the same interface methods they would call on `RealTapeGcMgm`.

## State And Persistence
Private state is guarded by a mutable mutex and includes maps for space config/stats, several counters, and a shell-output string. State is reset only by constructing a new dummy.

## Dependencies And Integration Points
The class depends on `ITapeGcMgm`, `SpaceConfig`, `SpaceStats`, standard maps, and mutexes. It is a core test fixture dependency across `unit_tests/mgm/tgc`.

## Risks And Edge Cases
The fake returns successful values for file existence, file size, and eviction by default; tests that need failure behavior require either changes to the fake or a custom mock. The move constructor is declared as `const DummyTapeGcMgm&&`, which is unusual but still deletes moves for practical purposes.

## Test Signals
The fake itself should be covered by tests that verify default values, setter/getter behavior, thread-safe counters, and stdout retrieval used by `AsyncUint64ShellCmd`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/DummyTapeGcMgm.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/FreedBytesHistogram.cc -->
# sources/distributed-fs/eos/mgm/tgc/FreedBytesHistogram.cc

## Purpose
`FreedBytesHistogram.cc` implements a thread-safe circular histogram of bytes freed over time. Tape-GC uses it to estimate space that has been queued for deletion locally but may not yet be reflected in MGM filesystem statistics.

## Important APIs, Types, And Functions
Implemented methods include the constructor, `bytesFreed()`, `getNbBytesFreedInLastNbSecs()`, `getTotalBytesFreed()`, `getFreedBytesInBin()`, `setBinWidthSecs()`, `getBinWidthSecs()`, `getNbBins()`, private `alignHistogramWithNow()`, and `getFreedBytesPerSec()`.

## Control Flow
Construction validates bin count and width. Mutating and query methods lock `m_mutex`, align the histogram to current clock time, then update or total bins. Alignment computes elapsed seconds since last update, converts that to bins, rotates `m_startIndex`, zeroes newly current bins, and updates the timestamp. `setBinWidthSecs()` rebuilds a temporary histogram by sampling old bytes-per-second estimates into new bins.

## State And Persistence
State is an in-memory vector of byte counts, current start index, bin width, clock reference, and last update timestamp. It is protected by a mutex and has finite historical depth of `nbBins * binWidthSecs`.

## Dependencies And Integration Points
The file uses constants from `Constants.hh`, `IClock`/`RealClock` or `DummyClock`, and `CtaUtils` rounding helpers. `SmartSpaceStats` calls `bytesFreed()` and query methods to augment available bytes.

## Risks And Edge Cases
`alignHistogramWithNow()` uses rounded-to-nearest bin movement, not floor, so partial-bin time movement can clear/advance sooner than expected. Negative clock movement converts through unsigned `size_t` after rounding helper behavior, which should be tested. `setBinWidthSecs()` calls `getFreedBytesPerSec()` while already holding the lock, but that helper assumes the lock and does not lock. Totals can overflow `uint64_t` if extremely large byte counts accumulate.

## Test Signals
Tests should cover invalid constructor args, bytes in current and aged bins, too-far-back exceptions, total bytes after full rotation, bin index validation, bin-width changes preserving approximate totals, dummy-clock time jumps, and concurrent access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/FreedBytesHistogram.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/FreedBytesHistogram.hh -->
# sources/distributed-fs/eos/mgm/tgc/FreedBytesHistogram.hh

## Purpose
`FreedBytesHistogram.hh` declares the circular freed-byte histogram abstraction and its validation exceptions.

## Important APIs, Types, And Functions
The class declares exceptions `InvalidNbBins`, `InvalidBinWidth`, `TooFarBackInTime`, and `InvalidBinIndex`; constructor `FreedBytesHistogram(uint32_t nbBins, uint32_t binWidthSecs, IClock&)`; public methods `bytesFreed()`, `getNbBytesFreedInLastNbSecs()`, `getTotalBytesFreed()`, `getFreedBytesInBin()`, `setBinWidthSecs()`, `getBinWidthSecs()`, and `getNbBins()`; private methods `alignHistogramWithNow()` and `getFreedBytesPerSec()`.

## Control Flow
The header defines the contract: callers notify freed bytes, then query finite time windows. Bin 0 is the youngest bin relative to now after alignment. Requests deeper than the histogram capacity throw `TooFarBackInTime`.

## State And Persistence
Private state is a mutex, vector of counters, start index, bin width, clock reference, and last update timestamp. The clock reference must outlive the histogram.

## Dependencies And Integration Points
It depends on EOS namespace macros, `IClock`, standard vectors, mutexes, and time types. `SmartSpaceStats` owns one histogram per space-GC statistics object.

## Risks And Edge Cases
The header documents `getFreedBytesPerSec(0)` as always returning zero. Because the class uses a reference clock and mutable mutex, copy/move semantics would be problematic; they are implicitly disabled by mutex/reference members. Consumers must size query periods to fit finite capacity.

## Test Signals
Header-level tests should compile exception types, public API signatures, and ownership with dummy and real clocks. Runtime tests should validate finite-depth behavior and exception messages used by operator diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/FreedBytesHistogram.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/IClock.cc -->
# sources/distributed-fs/eos/mgm/tgc/IClock.cc

## Purpose
`IClock.cc` provides the out-of-line virtual destructor for the tape-GC clock interface.

## Important APIs, Types, And Functions
The file defines `IClock::~IClock()`.

## Control Flow
There is no runtime behavior beyond allowing polymorphic destruction of `IClock` implementations.

## State And Persistence
No state is owned or persisted.

## Dependencies And Integration Points
This definition supports `DummyClock`, `RealClock`, and any other clock injected into `FreedBytesHistogram`.

## Risks And Edge Cases
If this file is omitted from a build target, users of `IClock` can hit unresolved vtable/destructor symbols. The destructor is empty and intentionally non-throwing by behavior, though not explicitly marked `noexcept`.

## Test Signals
Compile/link tests that construct and delete `IClock` implementations through base pointers are sufficient.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/IClock.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/IClock.hh -->
# sources/distributed-fs/eos/mgm/tgc/IClock.hh

## Purpose
`IClock.hh` declares the minimal clock interface used to decouple time-dependent tape-GC logic from wall-clock time.

## Important APIs, Types, And Functions
`IClock` has a virtual destructor and pure virtual `std::time_t getTime()`.

## Control Flow
Consumers call `getTime()` through the interface. Production and tests supply different implementations.

## State And Persistence
The interface owns no state. Implementations decide how time is sourced or stored.

## Dependencies And Integration Points
`FreedBytesHistogram` depends on `IClock` for current time. `RealClock` wraps `std::time(nullptr)` and `DummyClock` supplies deterministic test time.

## Risks And Edge Cases
The interface uses wall-clock seconds, not monotonic timestamps, so implementations can move backward. Callers need to tolerate clock skew or explicitly use a monotonic implementation if that becomes required.

## Test Signals
Tests should verify base-pointer deletion and correct substitution of dummy and real clocks in histogram code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/IClock.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/ITapeGcMgm.cc -->
# sources/distributed-fs/eos/mgm/tgc/ITapeGcMgm.cc

## Purpose
`ITapeGcMgm.cc` defines the pure virtual destructor for the tape-GC MGM interface.

## Important APIs, Types, And Functions
The file implements `ITapeGcMgm::~ITapeGcMgm()`.

## Control Flow
There is no operational flow. The definition makes the abstract base class safely destructible through base pointers.

## State And Persistence
No state is owned or persisted.

## Dependencies And Integration Points
This destructor supports both `RealTapeGcMgm` and `DummyTapeGcMgm` implementations and any test mocks.

## Risks And Edge Cases
Missing this object file from a target would cause link failures. The destructor is empty and does not clean resources; derived classes own their cleanup.

## Test Signals
Compile/link tests deleting derived MGM adapters through `ITapeGcMgm*` are sufficient.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/ITapeGcMgm.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/ITapeGcMgm.hh -->
# sources/distributed-fs/eos/mgm/tgc/ITapeGcMgm.hh

## Purpose
`ITapeGcMgm.hh` declares the tape-GC subsystem's abstraction over EOS MGM services. It isolates GC logic from concrete FsView, namespace, QuarkDB, shell-command, and eviction implementations.

## Important APIs, Types, And Functions
The interface declares config/stats methods, `FailedToGetFileSize`, file-size and namespace-state methods, `evictAsRoot()`, `getFsIdToSpaceMap()`, `getSpaceToDiskReplicasMap()`, and `getStdoutFromShellCmd()`. Nested `FileIdAndCtime` stores a file ID and creation time and defines ordering by ctime seconds then nanoseconds.

## Control Flow
Space-specific and multi-space GC classes call this interface for all external operations: read config, read space stats, map namespace replicas to spaces, validate files, evict files, and run optional free-byte scripts. The sorted set of `FileIdAndCtime` lets initial population feed LRUs oldest-first.

## State And Persistence
The interface owns no state. Concrete implementations may read live MGM state or test maps. `FileIdAndCtime` is a value type used in temporary maps.

## Dependencies And Integration Points
It depends on EOS filesystem IDs, namespace file metadata IDs, QuarkDB contact details, `SpaceConfig`, and `SpaceStats`. `RealTapeGcMgm`, `DummyTapeGcMgm`, `MultiSpaceTapeGc`, `TapeGc`, `SmartSpaceStats`, and `AsyncUint64ShellCmd` integrate through it.

## Risks And Edge Cases
`FileIdAndCtime::operator<()` ignores file ID when ctime is exactly equal, so two files with identical `timespec` compare equivalent in `std::set` and one can be lost. Interface methods mix throwing and non-throwing expectations; callers need careful error handling to avoid stopping GC on transient namespace failures.

## Test Signals
Tests should cover derived implementation substitution, duplicate ctime ordering behavior, file-size exception propagation, replica-map stop handling, and shell-output length/error semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/ITapeGcMgm.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/Lru.cc -->
# sources/distributed-fs/eos/mgm/tgc/Lru.cc

## Purpose
`Lru.cc` implements the in-memory least-recently-used queue used by tape-GC to choose old disk replicas for eviction.

## Important APIs, Types, And Functions
Implemented methods include constructor validation, `fileAccessed()`, private `newFileHasBeenAccessed()` and `queuedFileHasBeenAccessed()`, `fileDeletedFromNamespace()`, `empty()`, `size()`, `getAndPopFidOfLeastUsedFile()`, `maxQueueSizeExceeded()`, and `toJson()`.

## Control Flow
`fileAccessed()` checks the fid-to-list map. New files are pushed to the front unless max size is already reached, in which case the overflow latch is set. Existing files are erased from their current list position and reinserted at the front. `getAndPopFidOfLeastUsedFile()` removes the back list entry and clears the overflow latch. `toJson()` writes size and fids from MRU to LRU, checking output length after each fid and at the end.

## State And Persistence
State is in-memory and not internally synchronized: max size, overflow latch, `std::list` queue, and hopscotch map from file ID to list iterator. Persistence is indirect only through JSON diagnostics.

## Dependencies And Integration Points
The implementation uses `MaxLenExceeded`, `IFileMD::id_t`, EOS Murmur3 hashing, and `tsl::hopscotch_map`. `TapeGc` owns an `Lru` and `MultiSpaceTapeGc` populates it from QuarkDB through `fileAccessed()` calls.

## Risks And Edge Cases
No mutex is present; callers must serialize access. When full, new fids are ignored rather than evicting an old entry, so max-size pressure can make the queue stale until pops occur. JSON output changes the stream to hex and zero-fill without restoring flags, which can affect later writes to the same stream. `toJson()` can exceed maxLen before throwing by design.

## Test Signals
Existing `LruTests` cover constructor errors, empty pop, ordering, deletion, max-size latch, JSON formatting, maxLen errors, and disabled performance. Additional concurrency tests would need external synchronization expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/Lru.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/Lru.hh -->
# sources/distributed-fs/eos/mgm/tgc/Lru.hh

## Purpose
`Lru.hh` declares the tape-GC file-ID LRU queue abstraction. It maintains the most recently used file at the front and the least recently used file at the back.

## Important APIs, Types, And Functions
The header defines `FidQueue`, exceptions `MaxQueueSizeIsZero` and `QueueIsEmpty`, constructor `Lru(size_type maxQueueSize = 10000000)`, event methods `fileAccessed()` and `fileDeletedFromNamespace()`, query methods `empty()`, `size()`, `maxQueueSizeExceeded()`, pop method `getAndPopFidOfLeastUsedFile()`, JSON method `toJson()`, and private queue update helpers.

## Control Flow
The public contract is event-driven: file open/convert/populate events call `fileAccessed()`, namespace deletion calls `fileDeletedFromNamespace()`, and GC workers pop the least-used fid for eviction attempts.

## State And Persistence
The class stores a max size, overflow latch, list of fids, and map from fid to list iterator. It has no persistence or built-in locks.

## Dependencies And Integration Points
It depends on namespace file IDs, EOS hash helpers, hopscotch map, and standard containers. `TapeGcStats` exposes queue size, and JSON diagnostics are surfaced through FSCTL `tgc`.

## Risks And Edge Cases
Because iterators are stored in a map, every list erase/reinsert must keep the map synchronized. The default max of ten million entries can consume significant memory. Lack of internal locking means misuse from multiple threads can corrupt the list/map pair.

## Test Signals
Compile and runtime tests should cover queue ordering, duplicate access promotion, deletion, overflow behavior, empty pop, JSON max length, and performance/memory at large sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/Lru.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/MaxLenExceeded.cc -->
# sources/distributed-fs/eos/mgm/tgc/MaxLenExceeded.cc

## Purpose
`MaxLenExceeded.cc` implements the exception thrown when a JSON or command-output length limit is exceeded.

## Important APIs, Types, And Functions
It defines `MaxLenExceeded::MaxLenExceeded(const std::string&)`.

## Control Flow
Construction forwards the message to `std::runtime_error`.

## State And Persistence
The exception stores only the runtime-error message and has no external state.

## Dependencies And Integration Points
It is thrown by `Lru::toJson()` and `SpaceToTapeGcMap::toJson()`, and handled by `MultiSpaceTapeGc::handleFSCTL_PLUGIO_tgc()` to return `ERANGE`.

## Risks And Edge Cases
Length-limited writers can intentionally overshoot before throwing, so callers must not assume a partially written stream is bounded after catching. The class itself is straightforward.

## Test Signals
Tests should check message preservation and that JSON callers map this exception to the expected error path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/MaxLenExceeded.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/MaxLenExceeded.hh -->
# sources/distributed-fs/eos/mgm/tgc/MaxLenExceeded.hh

## Purpose
`MaxLenExceeded.hh` declares a typed runtime exception for tape-GC output-length violations.

## Important APIs, Types, And Functions
The file declares `struct MaxLenExceeded : std::runtime_error` with a string constructor.

## Control Flow
There is no behavior beyond typed exception construction.

## State And Persistence
No persistent state is owned beyond the inherited exception message.

## Dependencies And Integration Points
The type is shared by JSON-producing classes and FSCTL handling code so length failures can be distinguished from generic runtime errors.

## Risks And Edge Cases
Callers need to catch this specific type before broader `std::exception` when they want to return range-specific errors. The header includes EOS namespace macros and `<stdexcept>`.

## Test Signals
Compile tests and throw/catch tests are sufficient, plus integration tests for JSON maxLen paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/MaxLenExceeded.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/MultiSpaceTapeGc.cc -->
# sources/distributed-fs/eos/mgm/tgc/MultiSpaceTapeGc.cc

## Purpose
`MultiSpaceTapeGc.cc` implements the coordinator for tape-aware garbage collection across multiple EOS spaces. It enables spaces, starts one population worker, dispatches file access events to per-space GCs, exposes stats and JSON diagnostics, and coordinates shutdown.

## Important APIs, Types, And Functions
Implemented methods include constructor/destructor, `setTapeEnabled()`, `start()`, `stop()`, `isGcActive()`, `fileOpenedForWrite()`, `fileOpenedForRead()`, `fileConverted()`, `dispatchFileAccessedToGc()`, `getStats()`, `handleFSCTL_PLUGIO_tgc()`, `workerThreadEntryPoint()`, and `populateGcsUsingQdb()`.

## Control Flow
`setTapeEnabled()` records configured spaces. `start()` validates enablement and inactive state, creates per-space `TapeGc` objects, starts the multi-space worker, and marks active. The worker scans QuarkDB via `ITapeGcMgm::getSpaceToDiskReplicasMap()`, feeds file IDs into each space GC's LRU, marks population complete, then starts each space GC worker. File-open and conversion callbacks ignore events until tape is enabled and population is complete, then call `gc.fileAccessed()`. `stop()` sets the stop flag, joins the worker, destroys all GCs, and clears active/populated flags.

## State And Persistence
State is process-local: atomic enable/active/stop/populated flags, configured space set, startup mutex, worker thread, and `SpaceToTapeGcMap`. The coordinator rebuilds in-memory LRUs from QuarkDB at startup; it does not persist them itself.

## Dependencies And Integration Points
The coordinator is constructed by `XrdMgmOfs` with `RealTapeGcMgm`. File open paths in `XrdMgmOfsFile`, conversion jobs, admin stats (`NsCmd`), and `cmd=SFS_FSCTL_PLUGIO arg1=tgc` diagnostics integrate with it. It depends on `TapeGc`, `SpaceToTapeGcMap`, `ITapeGcMgm`, XRootD error buffers, and EOS logging.

## Risks And Edge Cases
`fileOpenedForRead()` and `fileConverted()` use `if (!m_tapeEnabled && !m_gcsPopulatedUsingQdb)` while write uses `||`; the read/convert condition allows dispatch when only one flag is false, likely before full readiness. `handleFSCTL_PLUGIO_tgc()` allocates a reply but leaks it on `MaxLenExceeded` before buffer ownership transfer, and uses `strlen(reply + 1)`, apparently skipping the first byte when setting length. `m_stop` is not reset in `start()`, so restarting after stop can make the new worker exit population immediately. Exceptions in the worker leave `m_gcIsActive` true until explicit stop.

## Test Signals
Existing `MultiSpaceTapeGcTests` cover construction and start/stop variants. Additional tests should cover readiness gating for read/convert events, restart after stop, FSCTL unauthorized and maxLen paths, reply length correctness, worker failure states, population stop requests, and event dispatch to unknown spaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/MultiSpaceTapeGc.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/MultiSpaceTapeGc.hh -->
# sources/distributed-fs/eos/mgm/tgc/MultiSpaceTapeGc.hh

## Purpose
`MultiSpaceTapeGc.hh` declares the multi-space tape-aware garbage-collector coordinator. It is the MGM-facing object that receives lifecycle calls, file access notifications, statistics requests, and FSCTL diagnostics.

## Important APIs, Types, And Functions
The class exposes constructor/destructor, deleted copy/assignment, exceptions `GcAlreadyStarted` and `GcIsNotEnabled`, `setTapeEnabled()`, `start()`, `stop()`, `isGcActive()`, file event methods for write/read/convert, `getStats()`, and `handleFSCTL_PLUGIO_tgc()`. Private helpers include `workerThreadEntryPoint()`, `populateGcsUsingQdb()`, and `dispatchFileAccessedToGc()`.

## Control Flow
The header defines a two-stage lifecycle: enable spaces, then start GC. Start creates per-space GC objects and launches population/worker startup; stop joins and destroys them. Event methods are no-ops until tape support is enabled and metadata population is complete.

## State And Persistence
Private state includes atomic flags, an `ITapeGcMgm` reference, `SpaceToTapeGcMap`, stop flag, startup mutex, worker thread, population flag, and configured spaces. All state is in memory and rebuilt on startup.

## Dependencies And Integration Points
The class depends on XRootD FSCTL types, EOS identities, `ITapeGcMgm`, `SpaceToTapeGcMap`, `TapeGcStats`, and namespace file IDs. It is owned by `XrdMgmOfs` and called from MGM file, conversion, and admin-control paths.

## Risks And Edge Cases
Thread lifecycle is sensitive: the coordinator owns one worker while per-space `TapeGc` objects own their own workers. Atomic flags and mutex-protected startup must stay consistent across start/stop/restart. Header comments contain minor typos, but the API contract is clear.

## Test Signals
Tests should cover lifecycle exceptions, idempotent stop/destructor behavior, configured-space accumulation, active flag semantics, and FSCTL behavior with local/non-local identities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/MultiSpaceTapeGc.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/RealClock.cc -->
# sources/distributed-fs/eos/mgm/tgc/RealClock.cc

## Purpose
`RealClock.cc` implements the production clock for tape-GC time calculations.

## Important APIs, Types, And Functions
It defines `RealClock::getTime()`.

## Control Flow
The method returns `std::time(nullptr)` each time it is called.

## State And Persistence
There is no stored state or persistence.

## Dependencies And Integration Points
`SmartSpaceStats` owns a `RealClock` before its `FreedBytesHistogram`, giving the histogram a production wall-clock source.

## Risks And Edge Cases
`std::time()` is wall-clock time and can jump backward or forward due to system time changes. Histogram code must tolerate those jumps.

## Test Signals
Compile/link coverage plus integration with `FreedBytesHistogram` is sufficient; deterministic behavior should use `DummyClock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/RealClock.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/RealClock.hh -->
# sources/distributed-fs/eos/mgm/tgc/RealClock.hh

## Purpose
`RealClock.hh` declares the production `IClock` implementation backed by `std::time()`.

## Important APIs, Types, And Functions
`RealClock` derives from `IClock` and overrides `getTime()`.

## Control Flow
Consumers call the interface method to retrieve current epoch seconds.

## State And Persistence
The class owns no state and is safe to construct cheaply.

## Dependencies And Integration Points
It depends on `IClock` and is used by `SmartSpaceStats`/`FreedBytesHistogram` in production.

## Risks And Edge Cases
It does not provide monotonic semantics. Any component needing duration measurement across clock adjustments should use a different clock implementation.

## Test Signals
Build tests with the real implementation and functional tests of consumers using dummy clocks for deterministic cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/RealClock.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/RealTapeGcMgm.cc -->
# sources/distributed-fs/eos/mgm/tgc/RealTapeGcMgm.cc

## Purpose
`RealTapeGcMgm.cc` implements the production bridge between tape-GC logic and EOS MGM services: FsView config/stats, namespace metadata, eviction command execution, QuarkDB namespace scanning, filesystem-to-space mapping, and shell-command stdout capture.

## Important APIs, Types, And Functions
Implemented methods include `getTapeGcSpaceConfig()`, `getSpaceConfigMemberString()`, `getSpaceConfigMemberUint64()`, `fileInNamespaceAndNotScheduledForDeletion()`, `getSpaceStats()`, `getFileSizeBytes()`, `evictAsRoot()`, `getFsIdToSpaceMap()`, `getSpaces()`, `getSpaceToDiskReplicasMap()`, and `getStdoutFromShellCmd()`.

## Control Flow
Config methods read `FsView::mSpaceView` under read lock and parse values, falling back to defaults on any error. File metadata methods prefetch before taking the namespace lock, then inspect `IFileMD`. `getSpaceStats()` sums free and capacity bytes for a space and scales by layout size factor when a space policy layout exists. Replica-map population builds an FSID-to-space map, scans QuarkDB with `FileScanner`, maps each file location to a space, stores matching fids ordered by ctime, honors a shared stop flag, and warns about FS IDs without spaces. Shell execution waits up to five seconds, handles timeout/signal/non-zero exit, and reads stdout with a maximum length.

## State And Persistence
The class stores only an `XrdMgmOfs&`; all persistent or live state is held by FsView, namespace services, QuarkDB, and admin command infrastructure. It does not cache internally.

## Dependencies And Integration Points
It integrates with `XrdMgmOfs`, `FsView`, `Policy`, `EvictCmd`, `VirtualIdentity::Root`, namespace prefetch/file service, QuarkDB `QClient`, `FileScanner`, `ShellCmd`, and `CtaUtils`. It is constructed by `XrdMgmOfs` and supplied to `MultiSpaceTapeGc`.

## Risks And Edge Cases
Config getters catch all exceptions and silently return defaults, which can mask invalid operational config. `getSpaceStats()` returns zeroed stats if the space is absent rather than throwing. `getFsIdToSpaceMap()` calls `getSpaces()` while already holding `FsView::ViewMutex`; whether this is safe depends on the lock being recursively readable. `FileIdAndCtime` ordering can drop files with identical ctime. Shell command strings are built elsewhere and executed through a shell, so config validation matters.

## Test Signals
Tests should cover config default fallback and parse errors, space stat scaling by layout, missing space behavior, namespace prefetch failures, scheduled-for-deletion container ID zero, eviction command errors, duplicate FSID detection, QuarkDB scan stop behavior, FS IDs without spaces, shell timeout/signal/exit/read-length paths, and integration with `SmartSpaceStats`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/RealTapeGcMgm.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/RealTapeGcMgm.hh -->
# sources/distributed-fs/eos/mgm/tgc/RealTapeGcMgm.hh

## Purpose
`RealTapeGcMgm.hh` declares the production `ITapeGcMgm` implementation backed by a live `XrdMgmOfs`.

## Important APIs, Types, And Functions
The class overrides all MGM interface methods for config, stats, file size, namespace state, eviction, FSID mapping, replica scanning, and shell stdout. Private helpers read string and uint64 space config members and enumerate spaces.

## Control Flow
The header-level contract maps each abstract operation to a real MGM operation. It deletes copy/move operations because it holds an OFS reference and represents a live service adapter.

## State And Persistence
Only `m_ofs` is stored. The adapter reads and mutates external MGM state through referenced services but does not own persistent state.

## Dependencies And Integration Points
It depends on `XrdMgmOfs`, namespace file metadata, and `ITapeGcMgm`. `XrdMgmOfs` creates it and passes it to `MultiSpaceTapeGc`.

## Risks And Edge Cases
Lifetime of the referenced OFS must exceed the adapter and all tape-GC objects using it. The static config helpers are `noexcept` and default on all failures, which is operationally forgiving but less visible.

## Test Signals
Build tests should verify overrides match the interface. Integration tests should use a controlled MGM/FsView fixture or substitute `DummyTapeGcMgm` for unit-level logic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/RealTapeGcMgm.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/SmartSpaceStats.cc -->
# sources/distributed-fs/eos/mgm/tgc/SmartSpaceStats.cc

## Purpose
`SmartSpaceStats.cc` implements per-space stats smoothing for tape-GC. It periodically queries MGM space stats, optionally overrides available bytes with an external script, adjusts the freed-byte histogram to match query period, and adds recently queued-for-deletion bytes to reported available space.

## Important APIs, Types, And Functions
Implemented methods include constructor, `get()`, `getQueryTimestamp()`, and `diskReplicaQueuedForDeletion()`. The core collaborators are `CachedValue<SpaceConfig>`, `AsyncUint64ShellCmd`, `FreedBytesHistogram`, `ITapeGcMgm`, and `CtaUtils`.

## Control Flow
`get()` reads cached config, locks, and refreshes MGM stats when the query period has elapsed. It always calls `m_mgm.getSpaceStats()`, then either keeps internal avail bytes, polls `tgc.freebytesscript`, uses a just-finished script value, uses a previous script value while pending, or logs script errors and falls back. It validates query period, recalculates histogram bin width as `ceil(queryPeriodSecs / nbBins)`, and adds freed bytes from the last query period to `availBytes`.

## State And Persistence
State is in memory: last query timestamp, last MGM stats plus source enum, real clock, freed-byte histogram, async script runner, and config cache reference. There is no durable persistence.

## Dependencies And Integration Points
`TapeGc` uses this class to decide whether eviction is needed and to report stats. `RealTapeGcMgm` supplies production stats/script execution; `DummyTapeGcMgm` supports tests. Config keys come from `Constants.hh`.

## Risks And Edge Cases
The `PENDING_AND_PREVIOUS_VALUE` switch case lacks a `break`, so it falls through to `VALUE`; because `getValue()` is absent, it keeps the previous value, but this fallthrough should be explicit or fixed for clarity. If `getSpaceStats()` throws, the method logs and continues with default/previous state. Invalid query periods are logged but still used later for freed-byte query depth. Adding freed bytes can double-count until MGM stats catch up, as the comment acknowledges.

## Test Signals
Existing `SmartSpaceStatsTests` cover no-script and script paths. Additional tests should cover query-period caching, invalid query periods, script error fallback, previous-value pending behavior, histogram bin-width changes, freed-byte augmentation, `TooFarBackInTime` fallback, and exception paths from `getSpaceStats()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/SmartSpaceStats.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/SmartSpaceStats.hh -->
# sources/distributed-fs/eos/mgm/tgc/SmartSpaceStats.hh

## Purpose
`SmartSpaceStats.hh` declares the per-space statistics helper used by tape-GC workers. It combines MGM space stats, optional external script values, and locally tracked freed-byte history.

## Important APIs, Types, And Functions
The class exposes constructor `SmartSpaceStats(spaceName, mgm, config)`, `diskReplicaQueuedForDeletion()`, enum `Src`, `srcToStr()`, struct `SpaceStatsAndAvailBytesSrc`, `get()`, and `getQueryTimestamp()`. Private members include `AsyncUint64ShellCmd`, space name, MGM reference, mutex, query timestamp, stats payload, `RealClock`, `FreedBytesHistogram`, and cached config reference.

## Control Flow
The public contract is polling-oriented. GC logic calls `get()` for current stats and calls `diskReplicaQueuedForDeletion()` after queuing an eviction so future stats reflect pending local frees.

## State And Persistence
State is protected by `m_mutex`. `m_clock` is intentionally declared before `m_freedBytesHistogram` so the histogram's clock reference remains valid during construction and destruction.

## Dependencies And Integration Points
The header ties together the tape-GC config, MGM abstraction, async shell runner, histogram, and basic `SpaceStats`. `TapeGcStats` reports the `SpaceStats` result from this component.

## Risks And Edge Cases
The config cache reference must outlive `SmartSpaceStats`. The class serializes stats reads and freed-byte notifications under one mutex, so slow `get()` refreshes can block deletion notifications. The source enum is valuable for diagnostics and should remain synchronized with switch handling.

## Test Signals
Tests should validate each `Src` value, query timestamp updates, config cache lifetime/use, freed-byte notification effects, and behavior with dummy MGM/script outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/SmartSpaceStats.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/SpaceConfig.hh -->
# sources/distributed-fs/eos/mgm/tgc/SpaceConfig.hh

## Purpose
`SpaceConfig.hh` defines the configuration values for a tape-aware garbage collector managing one EOS space.

## Important APIs, Types, And Functions
`struct SpaceConfig` contains `queryPeriodSecs`, `availBytes`, `freeBytesScript`, and `totalBytes`. Its default constructor initializes fields from `Constants.hh`.

## Control Flow
There is no behavior beyond default construction. `RealTapeGcMgm` populates instances from space config; tests and dummy MGM can inject custom instances.

## State And Persistence
The struct is a value snapshot of persisted EOS space config keys. It does not persist changes itself.

## Dependencies And Integration Points
It is returned by `ITapeGcMgm::getTapeGcSpaceConfig()`, cached by `CachedValue`, read by `SmartSpaceStats`, and used by space-specific `TapeGc` workers to decide thresholds and query cadence.

## Risks And Edge Cases
Defaults are conservative: `availBytes` is zero and `totalBytes` is 1 exabyte. Invalid operational values are validated elsewhere rather than in this struct, so consumers must check ranges.

## Test Signals
Tests should assert default values, custom assignment, cache refresh behavior with this struct, and consumer validation for invalid periods or thresholds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/SpaceConfig.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/SpaceNotFound.cc -->
# sources/distributed-fs/eos/mgm/tgc/SpaceNotFound.cc

## Purpose
`SpaceNotFound.cc` implements the typed exception thrown when an EOS space cannot be found in tape-GC MGM operations.

## Important APIs, Types, And Functions
It defines `SpaceNotFound::SpaceNotFound(const std::string&)`.

## Control Flow
Construction forwards the message to `std::runtime_error`.

## State And Persistence
The exception stores only its message.

## Dependencies And Integration Points
`RealTapeGcMgm::getFsIdToSpaceMap()` throws this type when FsView lacks a requested space or stores a null space pointer. Higher-level code can distinguish missing-space conditions from generic runtime errors.

## Risks And Edge Cases
Some production methods return defaults for missing spaces instead of throwing `SpaceNotFound`, so callers should not rely on this exception for every absent-space path.

## Test Signals
Tests should throw/catch the type and cover missing/null FsView space paths in `RealTapeGcMgm`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/SpaceNotFound.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/SpaceNotFound.hh -->
# sources/distributed-fs/eos/mgm/tgc/SpaceNotFound.hh

## Purpose
`SpaceNotFound.hh` declares a typed runtime exception for missing EOS spaces in tape-GC code.

## Important APIs, Types, And Functions
The file declares `struct SpaceNotFound : std::runtime_error` with a string constructor.

## Control Flow
There is no behavior beyond exception construction.

## State And Persistence
No persistent state is owned beyond the inherited error message.

## Dependencies And Integration Points
It is used by `RealTapeGcMgm` and can be caught by callers handling configuration or FsView inconsistencies.

## Risks And Edge Cases
The file-level comment names `TapeAwareGcSpaceNotFound.hh`, which no longer matches the actual filename/type. The header itself does not include `mgm/Namespace.hh`, so it relies on namespace macros being visible from prior includes or build context; that can be fragile in isolation.

## Test Signals
Compile the header standalone where possible, and test missing-space throw/catch behavior in production adapter code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/SpaceNotFound.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/SpaceStats.hh -->
# sources/distributed-fs/eos/mgm/tgc/SpaceStats.hh

## Purpose
`SpaceStats.hh` defines the minimal statistics snapshot for an EOS space used by tape-aware garbage collection.

## Important APIs, Types, And Functions
`struct SpaceStats` contains `totalBytes`, `availBytes`, a default constructor initializing both to zero, and equality operator `operator==`.

## Control Flow
There is no complex control flow. Instances are filled by MGM adapters, modified by `SmartSpaceStats`, and copied into `TapeGcStats`.

## State And Persistence
The struct is a transient value object and does not persist anything itself.

## Dependencies And Integration Points
It is used by `ITapeGcMgm`, `RealTapeGcMgm`, `DummyTapeGcMgm`, `SmartSpaceStats`, and admin statistics output.

## Risks And Edge Cases
Only total and available bytes are tracked; used bytes or source timestamps must be derived elsewhere. Zero is both the default and a valid possible value, so consumers need separate error/source information when distinguishing missing data.

## Test Signals
Tests should cover default construction, equality, production stats scaling, dummy stats injection, and `SmartSpaceStats` augmentation of `availBytes`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/SpaceStats.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/SpaceToTapeGcMap.cc -->
# sources/distributed-fs/eos/mgm/tgc/SpaceToTapeGcMap.cc

## Purpose
`SpaceToTapeGcMap.cc` implements a mutex-protected map from EOS space name to per-space `TapeGc` instances. It is the ownership and dispatch container used by `MultiSpaceTapeGc`.

## Important APIs, Types, And Functions
Implemented methods include constructor, `createGc()`, `destroyAllGc()`, `getGc()`, `getStats()`, `getSpaces()`, `toJson()`, and `startGcWorkerThreads()`.

## Control Flow
`createGc()` validates a non-empty space, locks, rejects duplicates, constructs a `TapeGc`, stores it in a `unique_ptr`, and returns a reference. `getGc()` locks and returns the referenced GC or throws `UnknownEOSSpace`. `getStats()` snapshots stats from each non-null GC. `toJson()` locks while serializing each GC's JSON and enforces maxLen after each child. `startGcWorkerThreads()` locks and starts every non-null per-space worker.

## State And Persistence
State is in-memory: MGM interface reference, mutex, and `std::map<std::string, std::unique_ptr<TapeGc>>`. Destroying all GCs clears the map and stops ownership of per-space state.

## Dependencies And Integration Points
The map owns `TapeGc` objects, exposes `TapeGcStats`, throws `MaxLenExceeded`, and is used directly by `MultiSpaceTapeGc` for lifecycle, event dispatch, population, stats, and FSCTL diagnostics.

## Risks And Edge Cases
`getGc()` returns a reference after releasing the mutex, so concurrent `destroyAllGc()` can invalidate that reference unless higher-level lifecycle locking prevents it. `toJson()` holds the map mutex while calling each `TapeGc::toJson()`, which may be expensive and can create lock-order risks if `TapeGc` calls back. Space names are written into JSON without escaping. Returning references to owned objects requires careful start/stop ordering.

## Test Signals
Existing `SpaceToTapeGcMapTests` cover creation, duplicate/unknown errors, stats, JSON, and worker startup. Additional tests should cover empty space names, concurrent get/destroy expectations, JSON escaping for unusual space names, and maxLen propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/SpaceToTapeGcMap.cc -->
