# sources/compression/zstd/programs/benchfn.h

## Purpose
`benchfn.h` declares a small generic benchmark API for the zstd programs. It lets callers measure arbitrary functions over a set of input/output blocks, optionally initialize state before each benchmark run, detect callback-specific errors, retrieve either timing or failure results through an opaque outcome wrapper, and run adaptive timed benchmark sessions.

## Important APIs and types
- `BMK_runTime_t` stores a measured `nanoSecPerRun` and `sumOfReturn`, where the sum generally represents bytes produced over one pass through all blocks.
- `BMK_runOutcome_t` is a stack-allocatable but logically opaque tagged outcome containing a valid runtime payload or an error result. Field names explicitly warn callers not to access them directly.
- Callback types: `BMK_benchFn_t` benchmarks one source/destination block with a custom payload; `BMK_initFn_t` initializes caller state once per measured run; `BMK_errorFn_t` interprets a `benchFn` return value as success or failure.
- `BMK_benchParams_t` bundles all callback pointers, payloads, block counts, source buffer arrays, source sizes, destination buffer arrays, destination capacities, and optional per-block result storage.
- Fixed-run API: `BMK_benchFunction()`, `BMK_isSuccessful_runOutcome()`, `BMK_extract_runTime()`, and `BMK_extract_errorResult()`.
- Timed-run API: opaque `BMK_timedFnState_t`, `BMK_benchTimedFn()`, `BMK_isCompleted_TimedFn()`, `BMK_createTimedFnState()`, `BMK_resetTimedFnState()`, `BMK_freeTimedFnState()`, `BMK_TIMEDFNSTATE_SIZE`, `BMK_timedFnState_shell`, and `BMK_initStatic_timedFnState()`.

## Control flow and state behavior
Callers construct a fully specified `BMK_benchParams_t`; no default initializer exists because all arrays and callback choices are workload-specific. `BMK_benchFunction()` then runs the benchmark function over every block for a specified number of loops, with `0` loops treated as one. Callers must inspect the returned `BMK_runOutcome_t` with `BMK_isSuccessful_runOutcome()` before extracting the runtime or error result, because the extraction helpers abort on misuse.

Timed benchmarking is stateful. A caller creates or statically initializes `BMK_timedFnState_t`, repeatedly calls `BMK_benchTimedFn()` to get intermediate measurements paced approximately by `run_ms`, and checks `BMK_isCompleted_TimedFn()` to stop when the `total_ms` budget has been spent or exceeded. `BMK_resetTimedFnState()` reuses an existing state for a new benchmark session.

The static-allocation contract is intentionally conservative. `BMK_timedFnState_shell` reserves `BMK_TIMEDFNSTATE_SIZE` bytes and enforces 8-byte alignment, while `BMK_initStatic_timedFnState()` can also accept arbitrary caller buffers and reject those that are too small or incorrectly aligned.

## Dependencies and integration points
The header includes only `<stddef.h>` for `size_t`. It pairs directly with `benchfn.c` and is consumed by benchmark code in the zstd CLI. Its callback shape is generic enough to wrap zstd compression, decompression, or support functions that map one source buffer to one destination buffer and return a `size_t` result with optional error semantics.

## Risks and edge cases
- Direct access to `BMK_runOutcome_t` fields is source-compatible but contractually forbidden; doing so can couple callers to representation details.
- `BMK_benchParams_t` requires all block arrays to be sized to `blockCount`; null or mismatched arrays lead to undefined behavior in the implementation.
- `dstBuffers` and `dstCapacities` are required even for callbacks that do not use them, because the implementation clears destination buffers before measuring.
- `blockResults` is optional, but when provided after an error it contains only results through the failing block; callers must not assume all entries are valid.
- `BMK_errorFn_t` must return `0` for success and nonzero for failure. Inverting this convention would cause valid callbacks to be reported as errors.
- Timed benchmarks only approximate requested durations; very slow single-loop callbacks can exceed `run_ms` and `total_ms`.

## Test signals
Header-level tests should compile consumers in C and C++, verify that `BMK_timedFnState_shell` is large enough for the implementation, exercise fixed and timed benchmark flows through public APIs only, validate optional `blockResults` behavior on success and error, and use sanitizer builds to catch null arrays or invalid buffer capacities in callers. Integration tests should wrap real zstd callbacks and confirm outcome handling, timing extraction, and error extraction are used in the documented order.
