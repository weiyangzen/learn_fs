# subset-b-000324 research

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/zstd.h -->
# sources/compression/zstd/lib/zstd.h

## Purpose
`zstd.h` is the primary public C API contract for libzstd. It exposes the stable compression, decompression, streaming, dictionary, parameter, error, version, and object-lifetime interfaces used by applications embedding zstd, and it conditionally exposes a much larger static-linking-only experimental surface behind `ZSTD_STATIC_LINKING_ONLY`. The header is declarative rather than implementing algorithms, but its comments define important control-flow contracts, state transitions, buffer ownership, memory-budget expectations, and compatibility boundaries for the implementation in `lib/`.

## Important APIs, types, and constants
- Visibility and ABI macros: `ZSTDLIB_VISIBLE`, `ZSTDLIB_HIDDEN`, `ZSTDLIB_API`, `ZSTDLIB_STATIC_API`, and `ZSTD_DEPRECATED()` adapt symbol export/import and deprecation annotations across shared-library, static-library, C, and C++ callers.
- Version and format constants: `ZSTD_VERSION_MAJOR/MINOR/RELEASE`, `ZSTD_VERSION_NUMBER`, `ZSTD_VERSION_STRING`, `ZSTD_MAGICNUMBER`, `ZSTD_MAGIC_DICTIONARY`, `ZSTD_MAGIC_SKIPPABLE_START`, `ZSTD_BLOCKSIZE_MAX`, and frame/header size macros define public protocol and build identity.
- Simple APIs: `ZSTD_compress()`, `ZSTD_decompress()`, `ZSTD_compressBound()`, `ZSTD_getFrameContentSize()`, `ZSTD_findFrameCompressedSize()`, `ZSTD_findDecompressedSize()`, and `ZSTD_decompressBound()` cover one-shot buffer workflows and frame sizing. Most `size_t` returns are either byte counts or encoded errors tested by `ZSTD_isError()`, while content-size helpers use `ZSTD_CONTENTSIZE_UNKNOWN` and `ZSTD_CONTENTSIZE_ERROR` sentinels that are explicitly not `ZSTD_isError()` compatible.
- Context APIs: opaque `ZSTD_CCtx`, `ZSTD_DCtx`, `ZSTD_CStream`, and `ZSTD_DStream` model reusable compression/decompression state. `ZSTD_create*()`/`ZSTD_free*()` allocate and release contexts; stream aliases are intentionally the same underlying object type as contexts since v1.3.0.
- Advanced stable parameters: `ZSTD_strategy`, `ZSTD_cParameter`, `ZSTD_dParameter`, `ZSTD_bounds`, and `ZSTD_ResetDirective` define sticky compression/decompression parameters, bounds discovery, pledged source size, and session/parameter reset semantics. Key compression parameters include level, window/hash/chain/search logs, match length, strategy, target compressed block size, long distance matching, frame flags, and multithreaded job controls.
- Streaming APIs: `ZSTD_inBuffer`, `ZSTD_outBuffer`, `ZSTD_EndDirective`, `ZSTD_compressStream2()`, legacy `ZSTD_compressStream()`/`ZSTD_flushStream()`/`ZSTD_endStream()`, `ZSTD_decompressStream()`, and recommended buffer-size helpers implement incremental operation with caller-visible `pos` advancement.
- Dictionary APIs: one-shot dictionary calls (`ZSTD_compress_usingDict()`, `ZSTD_decompress_usingDict()`), digested dictionaries (`ZSTD_CDict`, `ZSTD_DDict`), dictionary ID helpers, sticky dictionary loading/reference APIs, and prefix APIs define copy/reference lifetime tradeoffs and per-frame versus persistent dictionary behavior.
- Memory and sizing APIs: `ZSTD_sizeof_*()`, `ZSTD_estimate*Size*()`, `ZSTD_initStatic*()`, `ZSTD_customMem`, advanced create functions, and thread-pool APIs expose memory accounting, static workspaces, custom allocators, and shared compression worker pools.
- Static-only sequence and experimental APIs: `ZSTD_Sequence`, `ZSTD_compressionParameters`, `ZSTD_frameParameters`, `ZSTD_parameters`, dictionary load/format enums, `ZSTD_generateSequences()`, `ZSTD_compressSequences*()`, skippable frame helpers, experimental compression/decompression parameters, `ZSTD_CCtx_params`, and external `ZSTD_sequenceProducer_F` registration support low-level tuning, external parsers, and bindings.
- Deprecated legacy surfaces: many old advanced streaming, buffer-less streaming, and raw block APIs remain declared with deprecation markers and comments mapping them to newer `ZSTD_CCtx_reset()`, `ZSTD_DCtx_reset()`, parameter setters, and normal streaming APIs.

## Control flow and state behavior
The header describes three main compression/decompression flows. The simple path compresses or decompresses a complete frame in one call, requiring the destination to be sized by an upper bound such as `ZSTD_compressBound()` or by a validated decompressed-size policy. The explicit-context path reuses `ZSTD_CCtx` or `ZSTD_DCtx` across independent operations to amortize allocations, with a strict one-context-per-thread expectation. The streaming path repeatedly calls `ZSTD_compressStream2()` or `ZSTD_decompressStream()` while checking and updating `ZSTD_inBuffer.pos` and `ZSTD_outBuffer.pos`.

Compression parameters are sticky on contexts for `ZSTD_compress2()` and streaming compression, but not for older one-shot `ZSTD_compressCCtx()`, which resets advanced parameters and honors only the requested compression level. `ZSTD_CCtx_reset()` separates session cancellation from parameter reset, so callers can abort an in-progress frame without dropping dictionaries and parameters, or can clear all parameters and dictionary/external sequence producer references between sessions. `ZSTD_CCtx_setPledgedSrcSize()` is single-frame state: it is written into and checked against the next frame and then discarded back to unknown.

Streaming compression has directive-driven control flow. `ZSTD_e_continue` consumes more input, `ZSTD_e_flush` emits all currently available output but leaves the frame open, and `ZSTD_e_end` flushes and writes the frame epilogue. A nonzero return from flush/end means more output remains and the caller must continue flushing before starting a new operation or changing most parameters. In multithreaded mode, `ZSTD_c_nbWorkers >= 1` makes streaming compression asynchronous, with some parameters only taking effect on later jobs after flushing.

Streaming decompression uses the return value as either completion (`0`), an error, or a hint for the next input size / remaining work. It may need repeated calls with no new input to drain internal output if the destination buffer filled. `ZSTD_DCtx_setParameter()` and `ZSTD_DCtx_reset()` set sticky decoder properties such as maximum window log, which is important for bounding memory when reading untrusted frames.

Dictionary and prefix state has carefully defined persistence. Loaded dictionaries are sticky until invalidated or parameters are reset. Referenced `CDict`/`DDict` and prefixes do not copy user memory, so the referenced buffer or prepared dictionary must outlive its use. Prefixes are single-use and are discarded at the end of the next frame, while loaded dictionaries and referenced dictionaries persist across future frames on the same context.

## Dependencies and integration points
The only direct include is `<stddef.h>` plus `zstd_errors.h` for `ZSTD_ErrorCode`; `<limits.h>` is included only for static-linking-only bounds. The header is C++ compatible through `extern "C"`. It is the integration point consumed by CLI code, tests, bindings, and external applications, and it references specification docs such as `doc/zstd_compression_format.md` for low-level sequence validity and frame format details.

The stable/experimental split is a major integration boundary. Stable `ZSTDLIB_API` declarations are appropriate for dynamic linking; static-only declarations require `ZSTD_STATIC_LINKING_ONLY` and are explicitly not ABI-stable. Build systems and bindings must avoid treating experimental enum numeric values, `experimentalParam` placeholders, or deprecated raw block APIs as stable contracts.

## Risks and edge cases
- Untrusted input risks: frame headers can advertise huge decompressed sizes or window sizes. Callers must clamp `ZSTD_getFrameContentSize()`, `ZSTD_findDecompressedSize()`, and streaming `windowLogMax` results to application limits before allocating.
- Error-sentinel risks: not every helper uses the same error convention. `ZSTD_CONTENTSIZE_UNKNOWN`/`ERROR` must not be passed to `ZSTD_isError()` as if they were normal `size_t` error codes.
- State misuse risks: calling streaming APIs after an error without reset is documented as undefined behavior; changing parameters at the wrong phase can fail or have no effect; failing to fully flush `ZSTD_e_end` leaves a frame incomplete.
- Lifetime risks: by-reference dictionaries, prefixes, stable input/output buffer modes, and external sequence producer state rely on caller-owned memory remaining valid and unmodified. Violations can cause data corruption or operation failure.
- Dynamic-linking risks: static-only declarations may change signature or semantics and should not be used with a dynamically linked library.
- Sequence API risks: externally supplied sequences are trusted unless `ZSTD_c_validateSequences` is enabled. Invalid parses can corrupt compressed output; external sequence producers currently have limitations around LDM, dictionaries/history, and multithreading within one compression.
- Compatibility risks: deprecated APIs preserve old behavior such as `ZSTD_resetCStream()` treating pledged size `0` as unknown, which differs from modern `ZSTD_CCtx_setPledgedSrcSize()` where `0` means empty.

## Test signals
Useful tests for this header's contracts include compiling C and C++ consumers with and without `ZSTD_STATIC_LINKING_ONLY`, shared-library import/export builds, deprecated-warning coverage, one-shot round trips using `ZSTD_compressBound()`, streaming round trips that exercise partial input/output and flush/end loops, dictionary copy/reference lifetime tests, parameter-bound tests using `ZSTD_cParam_getBounds()` and `ZSTD_dParam_getBounds()`, large-window refusal tests for untrusted frames, static-workspace alignment/size failures, external-sequence validation/fallback tests, and determinism checks gated by `ZSTD_isDeterministicBuild()`.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/zstd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/zstd_errors.h -->
# sources/compression/zstd/lib/zstd_errors.h

## Purpose
`zstd_errors.h` is the public error-code declaration header shared by `zstd.h` and applications that need to inspect typed zstd failures. It defines the `ZSTD_ErrorCode` enum and a string conversion API, while leaving normal error detection to `ZSTD_isError()` from the main API.

## Important APIs, types, and constants
- Visibility macros `ZSTDERRORLIB_VISIBLE`, `ZSTDERRORLIB_HIDDEN`, and `ZSTDERRORLIB_API` mirror the main library's export/import controls, including backward compatibility for `ZSTDERRORLIB_VISIBILITY` and DLL import/export handling.
- `ZSTD_ErrorCode` enumerates stable errors below `100`, including generic failure, unknown prefix, unsupported version/frame parameters, window too large, corruption/checksum/literals header problems, dictionary errors, unsupported/out-of-bound parameters, table and symbol limits, wrong stage/init/memory/workspace/destination/source-buffer errors, and no-forward-progress cases.
- Values at and above `100` are explicitly marked unstable: frame index, seekable I/O, wrong source/destination buffers, sequence producer failure, invalid external sequences, and `ZSTD_error_maxCode`.
- `ZSTD_getErrorString(ZSTD_ErrorCode code)` maps a typed enum value to a readable string and is documented as equivalent in meaning to `ZSTD_getErrorName()` but taking an enum rather than an encoded function result.

## Control flow and state behavior
This header has no runtime state or control flow beyond declaration-time C/C++ linkage and visibility selection. Its design enforces an error-handling flow in users of libzstd: functions generally return a `size_t` value, callers first detect failure with `ZSTD_isError()`, then may convert to `ZSTD_ErrorCode` using `ZSTD_getErrorCode()` or render the enum with `ZSTD_getErrorString()`.

The comments specify version stability rules. Numeric enum values are pinned down only since v1.3.1, and only values below `100` should be treated as stable. Older or dynamically linked scenarios should prefer enum names and `ZSTD_isError()` rather than numeric constants.

## Dependencies and integration points
The file is self-contained and uses only language linkage/visibility macros. It is included by `zstd.h` and is also useful to embedders that want the enum declarations without relying on internal headers. It integrates with the implementation that encodes errors into `size_t` results and with public conversion helpers declared in `zstd.h`.

## Risks and edge cases
- Code must not persist or compare unstable values at or above `100` as a compatibility promise.
- `ZSTD_error_maxCode` is a sentinel and explicitly should not be used directly.
- `ZSTD_getErrorString()` accepts an enum code; callers with raw function results should first convert through `ZSTD_getErrorCode()` instead of casting arbitrary `size_t` values.
- Dynamic-linking support for the error-list API is called out as not officially supported in the comments, so binary compatibility assumptions should stay conservative.

## Test signals
Test coverage should include mapping representative stable errors to non-null strings, verifying successful operations report `ZSTD_error_no_error` through the normal conversion path, confirming `ZSTD_isError()` remains the primary detector for encoded results, and compiling C++ consumers to validate the `extern "C"` boundary. Compatibility tests should avoid depending on unstable enum values.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/zstd_errors.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/programs/Makefile -->
# sources/compression/zstd/programs/Makefile

## Purpose
`programs/Makefile` builds the zstd command-line utilities from the libzstd sources and CLI sources. It provides default release builds, feature-detected builds with optional compression-format support, variant binaries with reduced capabilities, profile-guided optimization, manpage generation, dependency tracking, install/uninstall targets, and Windows resource handling.

## Important targets, variables, and rules
- Source aggregation imports `../lib/libzstd.mk` and derives `ZSTDLIB_COMMON_SRC`, `ZSTDLIB_COMPRESS_SRC`, `ZSTDLIB_DECOMPRESS_SRC`, `ZDICT_SRC`, `ZSTDLEGACY_SRC`, `ZSTDLIB_FULL_SRC`, local object lists, CLI source/object lists, and `ZSTD_ALL_SRC`/`ZSTD_ALL_OBJ`. Sources are sorted for reproducible builds.
- Platform variables define `EXT`, `RES64_FILE`, `RES32_FILE`, and `RES_FILE` for Windows executables and resources.
- Feature probes create temporary `have_pthread.c`, `have_zlib.c`, `have_lzma.c`, and `have_lz4.c` programs to decide `THREAD_CPP`/`THREAD_LD`, `ZLIBCPP`/`ZLIBLD`, `LZMACPP`/`LZMALD`, and `LZ4CPP`/`LZ4LD`.
- Main targets include `all`, `allVariants`, `zstd`, `zstd-release`, `zstd32`, `zstd-nolegacy`, `zstd-nomt`, `zstd-nogz`, `zstd-noxz`, `zstd-dll`, `zstd-pgo`, `zstd-small`, `zstd-frugal`, `zstd-decompress`, `zstd-compress`, `zstd-dictBuilder`, and `zstdmt`.
- Build caching is controlled by `SET_CACHE_DIRECTORY` and recursive `make`: when `BUILD_DIR` is unset, `zstd` reinvokes make with `BUILD_DIR=obj/$(HASH_DIR)` and a captured flag/source environment; when set, objects are built under that cache directory and then copied to the top-level `zstd` executable only if hash comparison shows the binary differs.
- Pattern rules generate `.d` dependency files with `-MMD -MP`, build `.c` and `.S` files into `$(BUILD_DIR)`, and include generated dependency files when present.
- Maintenance targets include `clean`, `man`, `clean-man`, `preview-man`, `generate_res`, `list`, `install`, and `uninstall`.

## Control flow and state behavior
The default goal is `zstd-release`, which disables backtrace flags and builds `zstd`. A normal `zstd` build first accumulates feature macros and link libraries, then either recursively selects a cache directory or links `$(BUILD_DIR)/zstd` from all objects. After linking, optional hash comparison avoids rewriting the top-level binary if content has not changed, reducing timestamp churn.

The feature-detection flow is side-effectful but short-lived: each probe writes a small C file in the programs directory, compiles it with relevant libraries, removes the executable if successful, echoes `1` or `0`, and removes the probe source. The resulting `HAVE_*` variables drive compile definitions, link flags, and diagnostic messages. Thread detection accepts either a successful pthread probe or Windows.

Variant targets modify `CPPFLAGS`, `CFLAGS`, `LDFLAGS`, source lists, or support macros before depending on a build rule. For example `zstd-small` and `zstd-frugal` compile a minimal source set with `ZSTD_NOBENCH`, `ZSTD_NODICT`, `ZSTD_NOTRACE`, and no legacy support; `zstd-compress` and `zstd-decompress` split compressor-only and decompressor-only source sets; `zstd-nolegacy` removes legacy format support; and `zstd-nomt`, `zstd-nogz`, and `zstd-noxz` override detected support variables before invoking the normal `zstd` target.

Install flow is guarded by an OS whitelist inherited through `INSTALL_OS_LIST`/`UNAME`. It builds `zstd-release` only if `zstd` is absent, creates binary and man directories, installs the binary, script wrappers, symlinks, and man pages, and provides a matching uninstall target.

## Dependencies and integration points
This Makefile depends on variables and source lists from `../lib/libzstd.mk`, compiler/linker variables such as `CC`, `FLAGS`, `CPPFLAGS`, `CFLAGS`, `LDFLAGS`, `LDLIBS`, utility variables such as `GREP`, `CP`, `RM`, `LN`, `HASH`, `HASH_DIR`, and environment/platform variables including `OS`, `UNAME`, `BACKTRACE`, `PROFILE_WITH`, and install paths. Optional external libraries are pthread, zlib, liblzma, and liblz4. Manpage generation depends on `ronn` and `sed`; Windows resource generation depends on `windres`.

The file integrates CLI sources in `programs/` with libzstd implementation sources in `lib/`. It also provides user-facing packaging hooks by installing `zstd`, `zstdcat`, `unzstd`, `zstdmt`, `zstdless`, `zstdgrep`, and manpages.

## Risks and edge cases
- Feature probes write temporary files in the source directory, so interrupted builds can leave probe artifacts. The recipe removes sources after each probe, but `clean` only lists `have_zlib` explicitly and relies on normal cleanup for other tmp/probe files.
- Recursive build caching depends on `HASH_DIR` and flag propagation. Missing or unstable hashing can cause unnecessary rewrites or stale-object confusion if source lists/flags are not represented in the cache key upstream.
- Optional-library detection uses compile/link probes at make-evaluation time. Cross-compilation, unusual sysroots, or compilers that cannot execute the probe assumptions may mis-detect capabilities.
- `zstd32` hardcodes `-m32`, which fails without a 32-bit toolchain.
- Some variant link recipes place flags and libraries differently from the main target; strict linkers may be sensitive to argument order.
- `clean` removes broad patterns such as `tmp*`, `result*`, `dictionary`, and `*.zst` in the programs directory, so users should not keep unrelated artifacts there.
- Install rules rely on symlink behavior and OS whitelist logic; Windows paths and packaging flows use different conventions.

## Test signals
Useful validation includes `make -C sources/compression/zstd/programs zstd-release`, `make allVariants`, targeted builds such as `zstd-small`, `zstd-compress`, `zstd-decompress`, `zstd-nomt`, and `zstd-nolegacy`, dependency-file rebuild checks after touching headers, optional-library detection runs with `HAVE_ZLIB=0`/`HAVE_LZMA=0`/`HAVE_LZ4=0`, `make clean`, `make man` where `ronn` is available, and smoke tests invoking the resulting CLI for compress/decompress round trips and `zstd -b` benchmark execution. Cross-platform signals include Windows resource builds and install/uninstall dry runs under supported Unix-like systems.
<!-- END_FILE_RESEARCH: sources/compression/zstd/programs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/programs/benchfn.c -->
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
<!-- END_FILE_RESEARCH: sources/compression/zstd/programs/benchfn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/programs/benchfn.h -->
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
<!-- END_FILE_RESEARCH: sources/compression/zstd/programs/benchfn.h -->
