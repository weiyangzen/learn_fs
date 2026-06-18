# Research: subset-b-000308

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/common/error_private.h -->
# sources/compression/zstd/lib/common/error_private.h

## Purpose
`error_private.h` is zstd's private error-code adapter. It maps public `ZSTD_ErrorCode` values into the internal convention where functions returning `size_t` encode errors as negative enum values cast to `size_t`, and it supplies the return/forward macros used throughout the common, compression, and decompression code.

## Important APIs, Types, and Functions
The header aliases `ERR_enum` to `ZSTD_ErrorCode`, defines `ERROR(name)` and `ZSTD_ERROR(name)`, and provides inline helpers `ERR_isError()`, `ERR_getErrorCode()`, and `ERR_getErrorName()`. `CHECK_V_F()` and `CHECK_F()` evaluate a call, return early on error, and preserve the original `size_t` error. `RETURN_ERROR_IF()`, `RETURN_ERROR()`, and `FORWARD_IF_ERROR()` add debug logging via `RAWLOG()` and enforce a non-empty format string through `_FORCE_HAS_FORMAT_STRING()`.

## Control Flow, State, and Persistence
The header has no persistent state. Its control flow is macro-driven: callees return normal sizes below or equal to `ERROR(maxCode)`, while failures are returned immediately. In debug builds the macros log file, line, failed condition or expression, symbolic error, and optional formatted details before returning.

## Dependencies and Integration Points
It depends on `../zstd_errors.h` for the enum namespace, `compiler.h` for inline attributes, `debug.h` for logging, and `zstd_deps.h` for `size_t`. It is included by low-level modules such as FSE, Huffman, bitstream, and zstd frame/block code so they can expose public-compatible error names without exposing this private header as API.

## Risks and Test Signals
The main risk is misuse of the `size_t` error convention: arithmetic on returned sizes before `ERR_isError()` checks can turn failures into bogus capacities or offsets. The variadic logging macros also require call sites to pass a format string that is syntactically valid even when debug logging is disabled. Useful test signals include expected propagation through `CHECK_F()`/`FORWARD_IF_ERROR()`, correct `ZSTD_getErrorName()` strings for failures, and clean strict-C99 builds that reject empty variadic macro payloads.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/common/error_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/common/fse.h -->
# sources/compression/zstd/lib/common/fse.h

## Purpose
`fse.h` declares the Finite State Entropy codec interface used by zstd for compact entropy coding. It exposes the public-ish compression/decompression routines, static allocation macros, workspace sizing rules, repeat-table state enums, and inlined encoder/decoder state transitions used by FSE and Huffman implementations.

## Important APIs, Types, and Functions
The visible API includes version and bounds helpers (`FSE_versionNumber()`, `FSE_compressBound()`), error helpers, count normalization and serialization (`FSE_normalizeCount()`, `FSE_writeNCount()`, `FSE_readNCount()`/`_bmi2()`), table builders (`FSE_buildCTable()`, `FSE_buildDTable_wksp()`), and table-driven compression/decompression (`FSE_compress_usingCTable()`, `FSE_decompress_wksp_bmi2()`). Static-linking declarations define `FSE_CTable`, `FSE_DTable`, sizing macros such as `FSE_CTABLE_SIZE_U32()`, `FSE_DTABLE_SIZE_U32()`, `FSE_DECOMPRESS_WKSP_SIZE_U32()`, and the `FSE_repeat` enum. Inline building blocks include `FSE_CState_t`, `FSE_DState_t`, `FSE_initCState()`, `FSE_initCState2()`, `FSE_encodeSymbol()`, `FSE_flushCState()`, `FSE_initDState()`, `FSE_decodeSymbol()`, `FSE_decodeSymbolFast()`, `FSE_updateState()`, and `FSE_endOfDState()`.

## Control Flow, State, and Persistence
The header documents FSE's two-phase flow. Compression counts symbols, normalizes counts to a power-of-two table, serializes the normalized counts, builds a CTable, then encodes symbols in reverse decode order into a bitstream. Decompression reads the normalized counts, builds a DTable, initializes one or more DStates from the end-oriented bitstream, and decodes symbols while manually reloading the bit container. Runtime state is caller-owned in CTables, DTables, bitstreams, workspaces, and repeat-table flags; nothing is persisted outside caller buffers.

## Dependencies and Integration Points
It depends on `zstd_deps.h` for standard types and, under `FSE_STATIC_LINKING_ONLY`, on `bitstream.h` and `mem.h`-provided integer types. `fse_decompress.c` implements the workspace decompressor, entropy writer/reader code implements the table serializers, and `huf.h` reuses FSE workspace macros for compact Huffman table header decoding. Zstd sequence and literal entropy paths rely on these contracts for exact workspace sizing and table reuse.

## Risks and Test Signals
Risks center on table/workspace sizing and exact bitstream termination. `FSE_decodeSymbolFast()` is explicitly unsafe unless all decoded symbols consume at least one bit, so the DTable `fastMode` flag must be correct. Changing `FSE_MAX_MEMORY_USAGE`, `FSE_MAX_SYMBOL_VALUE`, or table-log limits can invalidate static allocation assumptions. Good tests exercise round trips with repeated tables, low-probability symbols, high-probability symbols that disable fast mode, BMI2 and non-BMI2 reads, malformed normalized counts, too-small workspaces, and exact input-consumption failures.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/common/fse.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/common/fse_decompress.c -->
# sources/compression/zstd/lib/common/fse_decompress.c

## Purpose
`fse_decompress.c` implements FSE decoding table construction and workspace-backed decompression for byte symbols. It is a template-style source that depends on `FSE_FUNCTION_TYPE`, `FSE_FUNCTION_EXTENSION`, and `FSE_DECODE_TYPE` macros so the same logic can be reused for specific symbol types.

## Important APIs, Types, and Functions
The key builder is `FSE_buildDTable_internal()`, exported through `FSE_buildDTable_wksp()`. It lays out low-probability symbols, spreads the remaining symbols across the decode table, and computes each entry's `nbBits` and `newState`. `FSE_decompress_usingDTable_generic()` drives two interleaved `FSE_DState_t` states over a `BIT_DStream_t` and selects normal or fast symbol reads. `FSE_decompress_wksp_body()` reads normalized counts with `FSE_readNCount_bmi2()`, validates `maxLog`, partitions the caller workspace into `FSE_DecompressWksp`, DTable, and scratch space, builds the DTable, reads `fastMode`, and dispatches to the generic decoder. `FSE_decompress_wksp_bmi2()` performs runtime BMI2 dispatch when `DYNAMIC_BMI2` is enabled.

## Control Flow, State, and Persistence
Build flow starts by checking workspace, symbol, and table-log bounds. It initializes the DTable header, reserves high table slots for `-1` low-probability symbols, sets `fastMode` to false when any symbol frequency can decode with zero bits, spreads symbols either through an optimized branchless two-stage path or a slower path that skips the low-probability zone, then derives state transitions from `symbolNext`. Decode flow initializes the bitstream and two states, rejects immediate overflow, emits four symbols per loop while the bitstream is unfinished and there is room, then finishes with a guarded tail loop. State is entirely in caller buffers and stack variables; no global persistence exists.

## Dependencies and Integration Points
The implementation includes `debug.h`, `bitstream.h`, `compiler.h`, `fse.h`, `error_private.h`, `zstd_deps.h`, and `bits.h`. It uses `MEM_write64()` for the spread optimization, `ZSTD_memcpy()` for the DTable header, `ZSTD_highbit32()` for transition bit counts, and `ERROR()`/`CHECK_F()` for zstd-style failures. Huffman table parsing and zstd entropy decompression call through the workspace API, often with CPU BMI2 selection supplied by higher layers.

## Risks and Test Signals
The highest-risk areas are malformed normalized counts that fail to visit every decode table cell, too-small workspaces, table logs above caller policy, and tail-loop output bounds. The optimized spread path intentionally over-writes up to 8 bytes inside scratch space, so its workspace sizing macro must stay in sync. Test signals include corruption errors for bad NCounts, `dstSize_tooSmall` when the destination tail is tight, successful decoding of low-probability symbols, fast-mode and non-fast-mode coverage, BMI2/non-BMI2 parity, and sanitizer coverage for fuzzed compressed streams.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/common/fse_decompress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/common/huf.h -->
# sources/compression/zstd/lib/common/huf.h

## Purpose
`huf.h` declares zstd's Huffman literal entropy API, including compression table construction, table reuse, serialized table reads, and single-stream or four-stream decompression variants. It is the boundary between zstd block logic and the lower-level Huff0/FSE entropy machinery.

## Important APIs, Types, and Functions
The header defines bounds and allocation contracts such as `HUF_BLOCKSIZE_MAX`, `HUF_WORKSPACE_SIZE`, `HUF_CTABLEBOUND`, `HUF_DTABLE_SIZE()`, `HUF_CREATE_STATIC_CTABLE()`, and `HUF_CREATE_STATIC_DTABLEX1/X2()`. Important types include opaque-ish `HUF_CElt`, `HUF_DTable`, `HUF_flags_e`, `HUF_repeat`, and `HUF_CTableHeader`. Compression declarations include `HUF_minTableLog()`, `HUF_cardinality()`, `HUF_optimalTableLog()`, `HUF_buildCTable_wksp()`, `HUF_writeCTable_wksp()`, `HUF_compress1X_repeat()`, `HUF_compress4X_repeat()`, and `HUF_compress*X_usingCTable()`. Decompression declarations include `HUF_readStats[_wksp]()`, `HUF_readCTable()`, `HUF_selectDecoder()`, `HUF_readDTableX1/X2_wksp()`, and the `HUF_decompress*` workspace/table variants.

## Control Flow, State, and Persistence
Compression flow counts input bytes, optionally optimizes the table depth, builds a CTable, serializes the Huffman weights, and emits either one stream or four streams. Repeat mode lets callers validate or reuse a previous CTable based on `HUF_repeat` and flags such as `HUF_flags_preferRepeat`. Decompression flow selects X1 or X2, reads the compact tree through FSE-backed stats parsing, builds a DTable, and decodes one or four segments into caller output. All persistent state is caller-owned in previous Huffman tables and repeat flags.

## Dependencies and Integration Points
It includes `zstd_deps.h`, `mem.h`, and static-linking `fse.h`. Zstd literal block compression/decompression uses this header directly, while FSE provides table-header entropy decoding for Huffman weights. Runtime flags bridge to CPU feature selection (`HUF_flags_bmi2`), assembly policy (`HUF_flags_disableAsm`), and fast-loop policy (`HUF_flags_disableFast`).

## Risks and Test Signals
Risks include workspace alignment and size requirements, repeat-table misuse, choosing an X1/X2 decoder incompatible with a table, and configuration drift in `HUF_TABLELOG_MAX` beyond the absolute maximum. Since compressed literals are security-sensitive parser input, malformed table headers, zero weights, oversized symbol counts, and tiny destination buffers need fuzz coverage. Strong signals are literal-block round trips, repeat-table and no-repeat parity, BMI2 parity, one-stream/four-stream coverage, decoder selection boundaries, and sanitizer-clean handling of corrupted Huffman headers.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/common/huf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/common/mem.h -->
# sources/compression/zstd/lib/common/mem.h

## Purpose
`mem.h` centralizes zstd's fixed-width integer typedefs and unaligned memory access helpers. It gives entropy, block, checksum, and frame code a portable way to read and write native, little-endian, and big-endian integers without scattering aliasing and endian assumptions.

## Important APIs, Types, and Functions
The header defines `BYTE`, `U8`, `S8`, `U16`, `S16`, `U32`, `S32`, `U64`, and `S64`, falling back to limits-based typedefs for older C environments. It declares and implements `MEM_32bits()`, `MEM_64bits()`, `MEM_isLittleEndian()`, native `MEM_read16/32/64/ST()` and `MEM_write16/32/64()`, little-endian `MEM_readLE16/24/32/64/ST()` and `MEM_writeLE16/24/32/64/ST()`, big-endian `MEM_readBE32/64/ST()` and `MEM_writeBE32/64/ST()`, byte swaps `MEM_swap32()`, `MEM_swap64()`, `MEM_swapST()`, and `MEM_check()`.

## Control Flow, State, and Persistence
All helpers are `MEM_STATIC` inline functions with no stored state. Compile-time macro `MEM_FORCE_MEMORY_ACCESS` selects one of three unaligned-access strategies: safe `ZSTD_memcpy()`, compiler-specific packed/aligned(1) typedefs, or direct pointer casts. Endian helpers check compile-time endian macros where possible and fall back to a stack union probe. Read/write functions either use native access directly on little-endian systems or byte-swap/manual byte assembly on big-endian systems.

## Dependencies and Integration Points
It includes `<stddef.h>`, `compiler.h`, `debug.h`, and `zstd_deps.h`, with compiler-specific headers for MSVC and ICC ARM byte-swap intrinsics. `fse.h`, `huf.h`, bitstream code, xxhash, frame parsing, and sequence encoding all rely on these helpers for stable on-wire little-endian formats and fast unaligned loads.

## Risks and Test Signals
The deliberate performance/portability tradeoff around `MEM_FORCE_MEMORY_ACCESS` is the main risk: method 2 can violate the C standard and fault or miscompile on strict-alignment targets. Big-endian and 32-bit paths are easy to regress because most development happens on little-endian 64-bit machines. Test signals include cross-endian frame/header parsing, UBSan/ASan runs with `MEM_FORCE_MEMORY_ACCESS=0`, alignment stress tests on unaligned buffers, 32-bit builds, and checks that 24-bit reads/writes preserve only the expected bytes.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/common/mem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/common/pool.c -->
# sources/compression/zstd/lib/common/pool.c

## Purpose
`pool.c` implements zstd's internal thread pool used by multi-threaded compression. With `ZSTD_MULTITHREAD` enabled it provides a bounded job queue, worker lifecycle management, dynamic thread limits, and custom allocator support. Without multithreading it compiles to a synchronous single-context fallback.

## Important APIs, Types, and Functions
`POOL_job` stores a `POOL_function` and opaque pointer. `POOL_ctx_s` stores custom memory hooks, thread handles, `threadCapacity`, `threadLimit`, circular queue indices and size, busy-count state, mutexes, condition variables, and shutdown flag. Public entry points are `ZSTD_createThreadPool()`, `POOL_create()`, `POOL_create_advanced()`, `POOL_free()`, `POOL_joinJobs()`, `ZSTD_freeThreadPool()`, `POOL_sizeof()`, `POOL_resize()`, `POOL_add()`, and `POOL_tryAdd()`. Internal helpers include the worker `POOL_thread()`, `POOL_join()`, `POOL_resize_internal()`, `isQueueFull()`, and `POOL_add_internal()`.

## Control Flow, State, and Persistence
Creation allocates and zeroes the context, allocates a circular queue of `queueSize + 1` entries, initializes synchronization primitives, allocates thread handles, and starts workers. Worker threads wait while the queue is empty or the busy count has reached `threadLimit`, pop one job under the mutex, signal pushers, execute outside the lock, decrement `numThreadsBusy`, and signal completion. `POOL_add()` blocks while full; `POOL_tryAdd()` returns 0 if full. `POOL_joinJobs()` waits until no queued or running jobs remain. `POOL_free()` sets shutdown, broadcasts both conditions, joins created threads, destroys synchronization objects, and frees allocations. The non-threaded fallback executes jobs immediately through a static `g_poolCtx`.

## Dependencies and Integration Points
The file depends on zstd custom allocation (`allocations.h`, `ZSTD_customCalloc()`, `ZSTD_customFree()`), `zstd_deps.h`, `debug.h`, `pool.h`, and, in threaded builds, `threading.h`. It is used by zstd multi-threaded compression contexts to schedule block compression and related background work while preserving a common API for single-threaded builds.

## Risks and Test Signals
Concurrency risks include blocking forever if jobs never signal completion, resizing to a smaller `threadLimit` while queued work exists, shutdown with non-empty queues, and caller lifetime bugs for `opaque` data because jobs may run asynchronously. `POOL_resize_internal()` can leave `threadLimit` expanded even if creating an additional thread fails. Useful tests cover queue size zero semantics, blocking and nonblocking add behavior, `POOL_joinJobs()` after many jobs, resizing up and down during activity, custom allocator failure injection, `POOL_free(NULL)`, and parity with the non-threaded immediate-execution fallback.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/common/pool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/common/pool.h -->
# sources/compression/zstd/lib/common/pool.h

## Purpose
`pool.h` declares zstd's internal thread-pool API. It hides the concrete `POOL_ctx_s` layout while exposing creation, shutdown, join, resize, size accounting, and job submission functions for multi-threaded compression code.

## Important APIs, Types, and Functions
The header forward-declares `POOL_ctx`, defines `POOL_function` as `void (*)(void*)`, and declares `POOL_create()`, `POOL_create_advanced()`, `POOL_free()`, `POOL_joinJobs()`, `POOL_resize()`, `POOL_sizeof()`, `POOL_add()`, and `POOL_tryAdd()`. `POOL_create_advanced()` accepts `ZSTD_customMem`, so the header enables `ZSTD_STATIC_LINKING_ONLY` before including `../zstd.h`.

## Control Flow, State, and Persistence
This header owns no runtime state. Its comments define the important behavior: `numThreads` must be at least 1, `queueSize` bounds queued jobs before blocking, `POOL_add()` may execute asynchronously and therefore requires `opaque` to outlive job completion, `POOL_tryAdd()` is immediate, and `POOL_resize()` changes only the thread count.

## Dependencies and Integration Points
It includes `zstd_deps.h` and zstd's static-linking declarations for allocator types. `pool.c` implements the API, while zstd multi-threading code uses it either through `POOL_*` names or the public thread-pool aliases exposed elsewhere.

## Risks and Test Signals
The header-level risk is contract mismatch: callers must not pass stack or transient `opaque` data unless they join before it goes out of scope, and callers must treat `POOL_ctx` as opaque. Build tests should cover both `ZSTD_MULTITHREAD` and non-threaded configurations, custom memory creation, and compile-time compatibility for static-linking consumers.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/common/pool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/common/portability_macros.h -->
# sources/compression/zstd/lib/common/portability_macros.h

## Purpose
`portability_macros.h` defines preprocessor-only feature and platform detection shared by C and assembly code. It intentionally contains no C declarations so assembly sources can include the same capability decisions.

## Important APIs, Types, and Functions
The header supplies fallback definitions for `__has_attribute`, `__has_builtin`, and `__has_feature`. It derives sanitizer flags `ZSTD_MEMORY_SANITIZER`, `ZSTD_ADDRESS_SANITIZER`, and `ZSTD_DATAFLOW_SANITIZER`, assembly symbol visibility through `ZSTD_HIDE_ASM_FUNCTION()`, CPU feature flags `STATIC_BMI2` and `DYNAMIC_BMI2`, assembly enablement flags `ZSTD_ASM_SUPPORTED` and `ZSTD_ENABLE_ASM_X86_64_BMI2`, CET marker `ZSTD_CET_ENDBRANCH`, and deterministic-build marker `ZSTD_IS_DETERMINISTIC_BUILD`.

## Control Flow, State, and Persistence
There is no runtime flow or state. The preprocessor evaluates compiler, OS, architecture, sanitizer, and build-option macros to choose whether BMI2 is assumed at compile time, dispatched at runtime, or unavailable; whether GAS-compatible assembly should be enabled; and whether assembly symbols need hidden/private annotations.

## Dependencies and Integration Points
This file is included from common compiler/CPU/assembly-adjacent code and must remain compatible with assemblers. `fse_decompress.c`, Huffman, and other hot paths depend on `DYNAMIC_BMI2`/`STATIC_BMI2` decisions for target attributes and runtime dispatch. Assembly implementations use `ZSTD_HIDE_ASM_FUNCTION()` and `ZSTD_CET_ENDBRANCH`, while release/reproducibility checks can inspect `ZSTD_IS_DETERMINISTIC_BUILD`.

## Risks and Test Signals
Risks are mostly build-matrix related: incorrectly enabling assembly under sanitizers can hide instrumentation, assuming BMI2 on unsupported targets can crash, and using C-only syntax would break assembly inclusion. Test signals include GCC, Clang, MSVC, Apple, Linux, and Windows builds; sanitizer builds confirming assembly disabled where required; x86-64 BMI2 dynamic and static builds; and reproducibility checks when macros that affect compressed output are toggled.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/common/portability_macros.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/common/threading.c -->
# sources/compression/zstd/lib/common/threading.c

## Purpose
`threading.c` implements the nontrivial parts of zstd's pthread compatibility layer. It provides Windows thread creation/join wrappers and debug-mode POSIX mutex/condition allocation wrappers, while emitting a dummy symbol so the translation unit is never empty.

## Important APIs, Types, and Functions
The file defines `g_ZSTD_threading_useless_symbol`. On Windows threaded builds it defines `ZSTD_thread_params_t`, helper thread entry `worker()`, `ZSTD_pthread_create()`, and `ZSTD_pthread_join()`. On POSIX threaded debug builds it implements `ZSTD_pthread_mutex_init()`, `ZSTD_pthread_mutex_destroy()`, `ZSTD_pthread_cond_init()`, and `ZSTD_pthread_cond_destroy()` as heap-allocating wrappers around pthread primitives.

## Control Flow, State, and Persistence
The Windows create path initializes a stack `ZSTD_thread_params_t`, creates a condition and mutex, starts `_beginthreadex()` with the stack object, then waits until the worker copies `start_routine` and `arg` and signals `initialized`. This handshake prevents the parent from returning while the child still depends on stack memory. The worker then calls the user start routine and exits. Join waits indefinitely, closes the handle, and maps wait results to 0, `EINVAL`, or `GetLastError()`. POSIX debug wrappers allocate mutex/condition objects so missing init/destroy becomes visible as crashes or sanitizer leaks.

## Dependencies and Integration Points
It includes `threading.h`. Windows builds also include `<process.h>` and `<errno.h>`. POSIX debug builds request malloc/free from `zstd_deps.h`. `pool.c` consumes the wrapper API without knowing whether it is backed by Windows condition variables, direct pthread objects, debug heap pointers, or no-op non-threaded macros.

## Risks and Test Signals
Windows creation depends on the initialization handshake being correct; removing it would introduce a stack lifetime race. Error paths must destroy any synchronization primitives already initialized. POSIX debug wrappers intentionally change the type shape to pointers, so macros in `threading.h` must dereference consistently. Test signals include thread creation failure injection, Windows join behavior, debug builds under ASan/LSan catching missing destroy paths, and thread pool tests that exercise create, wait, signal, broadcast, and join.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/common/threading.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/common/threading.h -->
# sources/compression/zstd/lib/common/threading.h

## Purpose
`threading.h` abstracts zstd's small pthread-like synchronization surface across Windows, POSIX, and non-threaded builds. It lets `pool.c` use one set of mutex, condition, thread-create, and join names without platform-specific branches.

## Important APIs, Types, and Functions
For Windows threaded builds it configures `WINVER`, `_WIN32_WINNT`, `WIN32_LEAN_AND_MEAN`, includes `windows.h`, maps mutexes to `CRITICAL_SECTION`, conditions to `CONDITION_VARIABLE`, and declares `ZSTD_pthread_create()`/`ZSTD_pthread_join()` over `HANDLE`. For POSIX threaded builds it includes `<pthread.h>` and either maps directly to pthread types/macros in release mode or declares debug heap-backed wrappers when `DEBUGLEVEL >= 1`. For non-threaded builds it typedefs mutex and condition types to `int` and turns all synchronization operations into no-ops.

## Control Flow, State, and Persistence
The header itself has no dynamic state. Its preprocessor flow selects exactly one implementation family based on `ZSTD_MULTITHREAD`, `_WIN32`, and `DEBUGLEVEL`. The selected macros control whether synchronization calls actually block, are direct pthread calls, wrap Windows primitives, or compile away in single-threaded builds.

## Dependencies and Integration Points
It includes `debug.h` for `DEBUGLEVEL` and, on Windows, temporarily undefines and restores `ERROR` around `windows.h` to avoid macro conflicts with zstd's `ERROR(name)` convention. `threading.c` provides Windows thread and POSIX debug wrapper functions, and `pool.c` is the main consumer.

## Risks and Test Signals
Build-configuration drift is the main risk. In non-threaded builds synchronization no-ops are correct only because `pool.c` also executes jobs synchronously. In debug POSIX builds the mutex and condition types are pointers, so any caller that assumes raw pthread layout would fail. Tests should compile and run threaded and non-threaded builds, Windows and POSIX builds, and debug-level builds that exercise every wrapper macro path.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/common/threading.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/common/xxhash.c -->
# sources/compression/zstd/lib/common/xxhash.c

## Purpose
`xxhash.c` is the xxHash implementation-instantiation unit for zstd. The real algorithm code lives in `xxhash.h`; this file defines the macros needed to emit the function bodies into one translation unit.

## Important APIs, Types, and Functions
The file defines `XXH_STATIC_LINKING_ONLY` to expose advanced declarations and `XXH_IMPLEMENTATION` to instantiate definitions, then includes `xxhash.h`. The resulting symbols are the xxHash APIs declared by the header, such as one-shot and streaming XXH32/XXH64 routines and any static-linking-only helpers enabled by the bundled header.

## Control Flow, State, and Persistence
There is no direct control flow in this file beyond preprocessing. Runtime state and behavior are entirely provided by `xxhash.h` after macro expansion, including caller-owned streaming hash states. This source file's role is to ensure those definitions are compiled once rather than as header-only duplicates.

## Dependencies and Integration Points
It depends solely on `xxhash.h`. Zstd tests and frame/block code use xxHash for checksums and verification paths, and build systems include this C file when they need standalone xxHash symbols from the bundled copy.

## Risks and Test Signals
Risks are integration-oriented: defining `XXH_IMPLEMENTATION` in multiple translation units can produce duplicate symbols, while omitting this file can produce unresolved references. Test signals include successful static and shared library links, checksum known-answer tests for XXH32/XXH64, streaming versus one-shot parity, and builds that include zstd with and without separate xxHash linkage.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/common/xxhash.c -->
