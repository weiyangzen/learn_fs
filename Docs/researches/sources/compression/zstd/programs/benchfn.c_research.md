# sources/compression/zstd/programs/benchfn.c

## Purpose
`benchfn.c` implements the generic benchmarking helper declared in `benchfn.h`. It measures arbitrary block-oriented functions, reports per-run nanosecond timings and summed return values, handles caller-provided error detection, and provides a timed benchmarking state that adapts loop counts until each measurement is long enough to be meaningful.

## Important functions and types
- `BMK_isSuccessful_runOutcome()` checks the opaque outcome tag and returns whether a benchmark produced a valid runtime.
- `BMK_extract_runTime()` returns the valid `BMK_runTime_t` payload and aborts through `CONTROL()` if called on an error outcome.
- `BMK_extract_errorResult()` returns the failing function result and aborts if called on a successful outcome.
- `BMK_runOutcome_error()` and `BMK_setValid_runTime()` are internal constructors for the tagged `BMK_runOutcome_t` representation.
- `BMK_benchFunction()` is the core fixed-loop benchmark over `BMK_benchParams_t`.
- `struct BMK_timedFnState_s` stores accumulated time spent, total budget, per-run budget, fastest accepted run, current loop count, and a `coolTime` timestamp.
- `BMK_createTimedFnState()`, `BMK_freeTimedFnState()`, `BMK_initStatic_timedFnState()`, `BMK_resetTimedFnState()`, `BMK_isCompleted_TimedFn()`, and `BMK_benchTimedFn()` manage and use the adaptive timed benchmarking state.

## Control flow and state behavior
`BMK_benchFunction()` normalizes `nbLoops` so `0` becomes `1`, pre-fills each destination buffer with `0xE5` to warm memory and erase prior results, records a start timestamp, optionally runs `initFn` once, and then calls `benchFn` for each block in each loop. On the first loop only, it stores per-block results if requested, checks `errorFn` if provided, returns an error outcome immediately on the first failing block, and accumulates `dstSize` as the sum of first-loop return values. After all loops, it computes elapsed nanoseconds with `UTIL_clockSpanNano()`, divides by `nbLoops` to produce `nanoSecPerRun`, and returns a valid outcome with `sumOfReturn`.

`BMK_benchTimedFn()` drives repeated fixed-loop benchmark passes using `BMK_timedFnState_t`. It starts from the state's current `nbLoops`, calls `BMK_benchFunction()`, returns immediately if the underlying benchmark failed, updates accumulated `timeSpent_ns`, and adapts `nbLoops` for the next pass. If the measured loop duration is more than 1/50 of the run budget, it estimates the next loop count from the fastest observed per-run time; otherwise it multiplies the loop count by 10. Runs shorter than half the per-run budget are discarded as too noisy and retried with the increased loop count. Accepted runs update `fastestRun` when faster and return the best runtime so far.

`BMK_resetTimedFnState()` clamps zero `total_ms` and `run_ms` to `1`, clamps `run_ms` to `total_ms`, resets time spent, converts millisecond budgets to nanoseconds, seeds `fastestRun.nanoSecPerRun` with a very large value, initializes `sumOfReturn` to `(size_t)-1`, starts `nbLoops` at `1`, and records `coolTime`. `BMK_isCompleted_TimedFn()` is a simple budget check and will also become true after an error only if callers continue using a state whose time budget has been exceeded; the function itself does not encode error state.

`BMK_initStatic_timedFnState()` provides stack/static allocation support. It uses a compile-time size assertion against `BMK_timedFnState_shell`, computes an alignment requirement using an internal wrapper struct, rejects null, too-small, or misaligned buffers, then resets the state in-place.

## Dependencies and integration points
The file uses `<stdlib.h>` for allocation/free, `<string.h>` for `memset`, `<assert.h>` for internal invariants, and conditionally `<stdio.h>` for debug output. It depends on `timefn.h` for `UTIL_time_t`, `UTIL_getTime()`, `UTIL_clockSpanNano()`, `PTime`, and time-scale constants, and on `benchfn.h` for public types/prototypes. It is used by zstd program benchmark code to time compression, decompression, or other block functions through uniform callback signatures.

## Risks and edge cases
- Extraction functions intentionally abort if callers ignore `BMK_isSuccessful_runOutcome()` and request the wrong payload.
- `BMK_benchFunction()` sums return values only from the first loop, so `sumOfReturn` describes one full pass over all blocks, not all iterations.
- `dstSize += res` happens after `errorFn` validation, but if no `errorFn` is provided then arbitrary `size_t` return values are treated as successful byte counts and may overflow the sum.
- Destination buffers and capacities are assumed valid for every block; the function always writes `0xE5` over `dstCapacities[i]`, even if the benchmark callback would not otherwise need a destination.
- `BMK_benchTimedFn()` can multiply `nbLoops` by 10 on very short runs; an `assert()` guards overflow, but in release builds with assertions disabled overflow could still be a risk for extremely fast callbacks and very large prior counts.
- Timing can be noisy. The half-run-budget filter reduces rounding error but can make very slow single-loop operations exceed the requested interval because the minimum loop count is one.
- `coolTime` is initialized but not otherwise used in this file, implying either compatibility with other benchmark code or a stale field.

## Test signals
Unit-style tests should cover successful fixed-loop benchmarking, `nbLoops == 0` normalization, `initFn` called once per measured run, per-block result capture, immediate error propagation from `errorFn`, extraction abort preconditions in debug/test harnesses, static state initialization with null, undersized, misaligned, and valid buffers, timed-state budget clamping, adaptive loop growth for very fast functions, accepted fastest-run updates, and integration with real compression/decompression callbacks where `sumOfReturn` matches produced bytes for one block pass.
