# subset-b-008424 Research

Grouped code research for the requested FoundationDB stacktrace, transaction profiling analyzer, and documentation build/tutorial files. Each section is bounded for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/stacktrace/stacktrace.amalgamation.cpp -->
# sources/storage-engines/foundationdb/contrib/stacktrace/stacktrace.amalgamation.cpp

## Purpose
This file is an amalgamated Abseil-derived stacktrace implementation used by FoundationDB's contrib stacktrace library. It packages public stack capture APIs, platform selection, low-level frame unwinders, readable-address probing, ELF/VDSO symbol lookup, and dynamic-annotation stubs into a single translation unit. Its primary public surface is `absl::GetStackFrames`, `absl::GetStackFramesWithContext`, `absl::GetStackTrace`, `absl::GetStackTraceWithContext`, `absl::SetStackUnwinder`, and `absl::DefaultStackUnwinder`.

## Important APIs, Types, And Functions
The top-level stack API dispatches through a file-local atomic `custom` unwinder. `SetStackUnwinder` installs a process-wide custom unwinder and `DefaultStackUnwinder` bypasses it. `ABSL_STACKTRACE_INL_HEADER` is selected by architecture and frame-pointer availability, mapping to the included `stacktrace_*` implementation. `absl::debug_internal::AddressIsReadable` probes arbitrary pointers without intentionally faulting; on Linux it uses a cached pipe and `syscall(SYS_write)` to test whether one byte can be read. `ElfMemImage` models in-memory ELF dynamic tables and exposes symbol iteration, `LookupSymbol`, and `LookupSymbolByAddress`. `VDSOSupport` locates the Linux VDSO from `/proc/self/auxv`, caches it in `vdso_base_`, resolves `__vdso_getcpu`, and exposes `GetCPU`.

## Control Flow
Stack capture calls enter `Unwind<IS_STACK_FRAMES, IS_WITH_CONTEXT>`, select either the default `UnwindImpl` template or a custom unwinder, adjust `skip_count`, and return captured PCs and optional frame sizes. Platform unwinders walk frame pointers or delegate to OS/glibc helpers. With signal context, supported unwinders use `ucontext_t` to recover pre-signal frame pointers. VDSO setup runs early through `VDSOInitHelper`, then later symbol lookups iterate ELF tables using dynamic-section pointers and version metadata.

## State And Persistence
Persistent state is process-local only: atomic custom unwinder, Linux readable-address pipe descriptors packed with the current pid, VDSO base cache, and cached getcpu function pointer. There is no file/database persistence. The Linux pipe probe can intentionally leak a small number of file descriptors across fork edge cases, which the comments treat as acceptable for crash-path usage.

## Dependencies And Integration Points
The file depends on compiler builtins, platform ABI frame layout, Linux `ucontext`, `link.h`, ELF dynamic tables, `/proc/self/auxv`, low-level syscalls, Windows `RtlCaptureStackBackTrace`, and optional sanitizer/Valgrind annotations. It integrates with FoundationDB where stack traces are needed without a wider Abseil dependency and with architecture-specific `.inc` files selected by preprocessor macros.

## Risks
Correctness is highly ABI-sensitive. Frame-pointer omission routes several platforms to the unimplemented or generic path, and the generic glibc path may allocate, which is risky in malloc/crash handlers. `SetStackUnwinder` is global and can race with threads still executing a previous unwinder. Some code uses `assert`/raw checks in low-level paths, so malformed ELF/VDSO state may abort in debug builds. The amalgamation must stay synchronized with its included architecture files and the public header.

## Test Signals
This file has no direct local test in the subset. Useful signals would be architecture-specific stack capture tests, signal-handler stack capture with `ucontext_t`, `max_depth == 0`, custom unwinder installation/removal, VDSO symbol lookup on Linux, and sanitizer/Valgrind builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/stacktrace/stacktrace.amalgamation.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/stacktrace/stacktrace_internal/stacktrace_aarch64-inl.inc -->
# sources/storage-engines/foundationdb/contrib/stacktrace/stacktrace_internal/stacktrace_aarch64-inl.inc

## Purpose
This inline implementation provides the AArch64 frame-pointer unwinder used by the amalgamated stacktrace code when `__aarch64__` is selected and frame pointers are available. It walks the standard AArch64 frame chain and can use Linux signal context to unwind across signal frames.

## Important APIs, Types, And Functions
`GetKernelRtSigreturnAddress` memoizes the VDSO `__kernel_rt_sigreturn` address using `VDSOSupport`. `ComputeStackFrameSize` computes byte distance between two frame pointers and returns `kUnknownFrameSize` when ordering is invalid. `NextStackFrame<STRICT_UNWINDING, WITH_CONTEXT>` validates the next frame pointer, including 16-byte alignment and frame-size limits. `UnwindImpl<IS_STACK_FRAMES, IS_WITH_CONTEXT>` captures PCs and optional frame sizes for the public stacktrace API.

## Control Flow
`UnwindImpl` starts from `__builtin_frame_address(0)`, skips itself, and repeatedly calls `NextStackFrame`. AArch64 frames store the previous frame pointer in word 0 and return address in word 1; the implementation records the previous return address after stepping. In Linux signal-context mode, if the current return address is `__kernel_rt_sigreturn`, the unwinder reads register 29 from `ucontext_t` as the pre-signal frame pointer and skips normal frame-size checks for that transition.

## State And Persistence
The only retained state is a static atomic memoized VDSO signal-return address. No durable persistence exists.

## Dependencies And Integration Points
It depends on GCC frame-address builtin, AArch64 ABI frame layout, Linux `ucontext_t` register naming, `AddressIsReadable`, and optional VDSO support. It is included through `ABSL_STACKTRACE_INL_HEADER` and must match the common `UnwindImpl` template signature.

## Risks
The unwinder requires reliable frame pointers; `NO_FRAME_POINTER` selects an unimplemented path for AArch64 elsewhere. Bad or corrupt frame chains can still yield incomplete or bogus traces, though alignment and size checks reduce the blast radius. Signal unwinding is Linux-specific and assumes VDSO symbols and `uc_mcontext.regs[29]` semantics.

## Test Signals
Relevant tests include ordinary call-stack capture on AArch64, capture from a signal handler, alternate signal stacks, strict frame-size reporting via `GetStackFrames`, and `min_dropped_frames` behavior when depth is capped.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/stacktrace/stacktrace_internal/stacktrace_aarch64-inl.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/stacktrace/stacktrace_internal/stacktrace_arm-inl.inc -->
# sources/storage-engines/foundationdb/contrib/stacktrace/stacktrace_internal/stacktrace_arm-inl.inc

## Purpose
This file implements stack unwinding for 32-bit ARM builds that retain frame pointers. It is a compact frame-chain walker designed for the common single-instruction-set case.

## Important APIs, Types, And Functions
`NextStackFrame<STRICT_UNWINDING>` reads the previous stack frame from `old_sp[-1]`, validates ordering, maximum frame size, and pointer alignment, and returns `nullptr` on implausible transitions. `StacktraceArmDummyFunction` is a noinline assembly barrier that forces the link register to be saved. `UnwindImpl<IS_STACK_FRAMES, IS_WITH_CONTEXT>` records return addresses and optional frame sizes.

## Control Flow
`UnwindImpl` obtains the current frame address with `__builtin_frame_address(0)`, calls the dummy function so the current function's return address is materialized on the stack, then walks frames until `max_depth` or a failed validation. It records `*sp` as the return PC and computes frame sizes when requested. `min_dropped_frames` is estimated by walking up to 200 additional frames.

## State And Persistence
There is no persistent state. All state is local to the unwind call.

## Dependencies And Integration Points
The code depends on GCC-compatible frame-address builtins, ARM frame layout, and the common stacktrace template signature. It is selected by the stacktrace config for `__arm__` when frame pointers are present.

## Risks
The header explicitly warns that mixed ARM/Thumb interworking can break frame-pointer discovery because caller and callee may use different frame-pointer registers. It does not consume `ucontext_t`, so signal unwinding support is weaker than the x86/AArch64/PowerPC implementations. Builds without frame pointers error or route away from this file.

## Test Signals
Coverage should include ARM and Thumb-mode builds separately, non-leaf and leaf frames, strict and non-strict frame-size validation, and capped-depth dropped-frame counting.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/stacktrace/stacktrace_internal/stacktrace_arm-inl.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/stacktrace/stacktrace_internal/stacktrace_generic-inl.inc -->
# sources/storage-engines/foundationdb/contrib/stacktrace/stacktrace_internal/stacktrace_generic-inl.inc

## Purpose
This is the portable fallback unwinder that delegates to glibc `backtrace`. It is used where FoundationDB/Abseil chooses a generic implementation, notably PowerPC builds without frame pointers per the stacktrace config.

## Important APIs, Types, And Functions
The only implementation is `UnwindImpl<IS_STACK_FRAMES, IS_WITH_CONTEXT>`. It allocates a fixed local stack array of 64 PCs, calls `backtrace`, skips the current frame plus requested frames, copies up to `max_depth`, zeroes frame sizes when requested, and computes a simple dropped-frame lower bound.

## Control Flow
The function ignores `ucp` and signal context. It uses `backtrace` output order directly, adjusts for `skip_count + 1`, clamps to caller depth, and returns the number copied.

## State And Persistence
There is no retained state. All output is written to caller-provided buffers.

## Dependencies And Integration Points
It depends on `<execinfo.h>` and glibc-compatible `backtrace`. It plugs into the same `UnwindImpl` template API as all architecture-specific unwinders.

## Risks
The file notes that glibc `backtrace` may call `malloc`, which can deadlock in heap profiling or crash-handler contexts. It cannot produce real frame sizes and cannot use signal context, so stack traces may be less reliable for the very paths stacktrace is often needed to debug.

## Test Signals
Basic stack depth tests are useful, but crash-safety and malloc-reentrancy are the important integration risks. Tests should also verify frame-size arrays are zero-filled and dropped-frame counts are non-negative.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/stacktrace/stacktrace_internal/stacktrace_generic-inl.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/stacktrace/stacktrace_internal/stacktrace_powerpc-inl.inc -->
# sources/storage-engines/foundationdb/contrib/stacktrace/stacktrace_internal/stacktrace_powerpc-inl.inc

## Purpose
This file implements PowerPC stack unwinding for ABI variants that preserve a stack chain. It handles PowerPC-specific link-register storage and has Linux signal-frame support.

## Important APIs, Types, And Functions
`StacktracePowerPCGetLR` returns the saved link register from ABI-specific stack slots. `NextStackFrame<STRICT_UNWINDING, IS_WITH_CONTEXT>` validates stack-chain transitions, enforces 16-byte alignment, and can recover pre-signal state from `ucontext_t`. `StacktracePowerPCDummyFunction` forces the link register to be saved. `UnwindImpl<IS_STACK_FRAMES, IS_WITH_CONTEXT>` performs the actual stack walk and frame-size reporting.

## Control Flow
`UnwindImpl` reads register `r1` into `sp` via inline assembly, calls the dummy function, skips the top link-register save area, then advances once before entering the main loop because PowerPC stores return addresses in the caller's frame. Linux signal support resolves `__kernel_sigtramp_rt64` through VDSO, detects signal trampoline frames, and can replace the next stack pointer with `PT_R1` from the signal context after readability checks.

## State And Persistence
The Linux signal path keeps static cached kernel-symbol status and trampoline address. No durable persistence exists.

## Dependencies And Integration Points
Dependencies include PowerPC ABI macros, inline assembly, Linux `asm/ptrace.h`/`ucontext.h`, VDSO support, `AddressIsReadable`, and sanitizer-suppression attributes. It is selected for `__ppc__` or `__PPC__` when frame pointers are available.

## Risks
ABI detection is brittle; unsupported ABI macros produce a compile-time error. Link-register placement differs across Darwin/AIX/SYSV/PPC64, and a wrong selection corrupts PCs. Signal support is Linux-specific and assumes VDSO symbol availability. The unwinder reads raw stack memory and suppresses sanitizer instrumentation for that reason.

## Test Signals
Testing should include PPC32/PPC64 ABI variants, Linux signal-handler traces, alternate stacks, frame-size reporting, and capped dropped-frame counting. Cross-compilation alone is not enough because runtime ABI stack layout matters.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/stacktrace/stacktrace_internal/stacktrace_powerpc-inl.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/stacktrace/stacktrace_internal/stacktrace_unimplemented-inl.inc -->
# sources/storage-engines/foundationdb/contrib/stacktrace/stacktrace_internal/stacktrace_unimplemented-inl.inc

## Purpose
This file is the explicit no-op stack unwinder for unsupported platforms or builds where stack unwinding is intentionally disabled, such as selected Apple, Android, Native Client, Fuchsia, MIPS, or no-frame-pointer configurations.

## Important APIs, Types, And Functions
It defines `UnwindImpl<IS_STACK_FRAMES, IS_WITH_CONTEXT>` with the common signature and no stack inspection. It sets `*min_dropped_frames` to 0 when provided and returns 0 captured frames.

## Control Flow
There is no frame walk. All parameters except `min_dropped_frames` are ignored.

## State And Persistence
No state is kept.

## Dependencies And Integration Points
It exists solely to satisfy the stacktrace implementation contract for unsupported configurations selected by `ABSL_STACKTRACE_INL_HEADER`.

## Risks
Any platform routed here silently loses stacktrace data. That may be acceptable for unsupported targets but can mask accidental build-flag regressions, especially `NO_FRAME_POINTER` on architectures where no alternate unwinder is configured.

## Test Signals
Tests should verify calls return zero frames without crashing and that higher-level crash/logging code handles empty traces gracefully. Build-configuration tests should confirm only intended platforms select this file.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/stacktrace/stacktrace_internal/stacktrace_unimplemented-inl.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/stacktrace/stacktrace_internal/stacktrace_win32-inl.inc -->
# sources/storage-engines/foundationdb/contrib/stacktrace/stacktrace_internal/stacktrace_win32-inl.inc

## Purpose
This file implements Windows stack capture using the undocumented but common `RtlCaptureStackBackTrace` exported by `ntdll.dll`. It avoids heavier symbol-server or `StackWalk64` dependencies.

## Important APIs, Types, And Functions
`RtlCaptureStackBackTrace_Function` declares the Windows function type. `RtlCaptureStackBackTrace_fn` is resolved at static initialization with `GetProcAddress(GetModuleHandleA("ntdll.dll"), "RtlCaptureStackBackTrace")`. `UnwindImpl<IS_STACK_FRAMES, IS_WITH_CONTEXT>` calls it with `skip_count + 2`, copies up to `max_depth`, zeroes frame sizes when requested, and does not implement dropped-frame counting.

## Control Flow
If the function pointer is unavailable, the implementation returns zero frames. Otherwise Windows fills the caller-provided result buffer directly. `ucp` is ignored.

## State And Persistence
The only state is the static function pointer resolved at load time. There is no persistence.

## Dependencies And Integration Points
It depends on `windows.h`, `ntdll.dll`, and the stacktrace common template signature. It is selected by `_WIN32`.

## Risks
The comment notes frame-pointer optimization can make Windows traces difficult; `RtlCaptureStackBackTrace` may not fully handle FPO. Static initialization touches loader-provided functions, which is intentional here to avoid later loader-lock issues. Frame sizes and dropped-frame lower bounds are unavailable.

## Test Signals
Windows tests should cover debug and release builds, missing/failed symbol resolution behavior, depth/skip semantics, zeroed frame sizes, and caller behavior with `min_dropped_frames == 0`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/stacktrace/stacktrace_internal/stacktrace_win32-inl.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/stacktrace/stacktrace_internal/stacktrace_x86-inl.inc -->
# sources/storage-engines/foundationdb/contrib/stacktrace/stacktrace_internal/stacktrace_x86-inl.inc

## Purpose
This file implements x86 and x86_64 frame-pointer unwinding for the stacktrace library. It contains extra Linux/i386 logic to unwind across VDSO system-call and signal trampoline frames.

## Important APIs, Types, And Functions
`CountPushInstructions` analyzes the i386 VDSO `__kernel_vsyscall` instruction prefix to understand how the kernel wrapper saved registers. `GetFP` extracts plausible base or stack pointers from Linux `ucontext_t`. `NextStackFrame<STRICT_UNWINDING, WITH_CONTEXT>` validates and advances the frame pointer with signal-context exceptions. `UnwindImpl<IS_STACK_FRAMES, IS_WITH_CONTEXT>` records return addresses from `fp + 1`, optional frame sizes, and dropped-frame estimates.

## Control Flow
`UnwindImpl` starts from `__builtin_frame_address(0)` and loops until max depth, null/self frames, or failed validation. Strict mode enforces monotonic upward frame addresses and a 100KB max frame; non-strict mode allows discontiguous frames but checks readability. In Linux i386 signal mode, it resolves `__kernel_rt_sigreturn` and `__kernel_vsyscall` from VDSO, detects when `%ebp` cannot be used, and restores the next frame pointer from saved `%esp`.

## State And Persistence
Linux i386 VDSO analysis stores static `num_push_instructions` and VDSO symbol addresses. No durable state exists.

## Dependencies And Integration Points
The implementation depends on GCC builtins, x86 frame-pointer ABI, Linux `ucontext_t`, VDSO support, `AddressIsReadable`, and sanitizer-suppression attributes. It is the primary selected unwinder for `__i386__` and `__x86_64__` with frame pointers.

## Risks
The file assumes frame pointers and rejects implausible chains; optimized leaf functions or code compiled with omitted frame pointers can truncate or corrupt traces. i386 VDSO instruction parsing is deliberately narrow and asserts on unexpected instruction sequences. Non-strict readability checks are slower and still cannot guarantee semantic validity of PCs.

## Test Signals
Useful coverage includes x86_64 and i386 builds, signal-handler unwinding, omitted-frame-pointer negative tests, VDSO-enabled kernels, `max_depth == 0`, frame-size output, and dropped-frame counts under shallow depth.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/stacktrace/stacktrace_internal/stacktrace_x86-inl.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/transaction_profiling_analyzer/transaction_profiling_analyzer.py -->
# sources/storage-engines/foundationdb/contrib/transaction_profiling_analyzer/transaction_profiling_analyzer.py

## Purpose
This Python CLI reads FoundationDB client transaction profiling samples from system keys, decodes versioned binary log events, optionally prints JSON transaction event records, and can summarize read/write hot spots and approximate key-space buckets with current shard-location annotations.

## Important APIs, Types, And Functions
Protocol constants enumerate supported client log encodings from 5.2 through 8.0. `ByteBuffer` is the binary decoder for little-endian ints, longs, doubles, booleans, length-prefixed byte strings, key ranges, and mutations. `MutationType`, `Mutation`, `KeyRange`, and the `BaseInfo` subclasses model event payloads from `FdbClientLogEvents::Event`: get version, get, get range, commit, and error variants. `ClientTransactionInfo` decodes one complete transaction sample and filters event types. `TransactionInfoLoader` scans `\xff\x02/fdbClientInfo/client_latency/`, reassembles multi-chunk values, and maps timestamp arguments through Timekeeper. `ReadCounter`, `WriteCounter`, and `ShardFinder` compute top operations, bucket boundaries, and storage-server address metadata. `main` owns CLI parsing and output.

## Control Flow
The CLI builds a `type_filter`, chooses read/write counters, parses required start/end times, opens the FDB database, and iterates `TransactionInfoLoader.fetch_transaction_info`. The loader computes start/end key selectors from Timekeeper versions when timestamps are supplied, scans system keys in snapshot read-lock-aware transactions, decodes single-chunk values directly, buffers ordered multi-chunk samples by transaction id, and yields decoded `ClientTransactionInfo` objects. Output either prints JSON per transaction or aggregates into counters, then reports top keys/ranges and key-space buckets with optional shard/address filters.

## State And Persistence
The script does not mutate FoundationDB. It reads system keys and current locality metadata. In-process state includes the multi-chunk cache capped by `max_num_chunks_to_store`, counters for reads/writes, a shard-address future cache, and a file logger at `transaction_profiling_analyzer.log`.

## Dependencies And Integration Points
Required dependencies are Python 3 and FDB Python bindings. Optional `dateparser` parses human time strings, and `sortedcontainers` enables read-density counting. The binary decoding must stay synchronized with FoundationDB `fdbclient/ClientLogEvents.h` and protocol-version layout changes. It uses `fdb.api_version(520)`, `fdb.impl.strinc`, `fdb.locality`, key selectors, transaction options for system-key and lock-aware reads, and `fdb.tuple` for Timekeeper values.

## Risks
The code is sensitive to binary protocol drift; unsupported protocol versions and malformed values are counted invalid and skipped. Chunk cache eviction can discard large or out-of-order multi-chunk samples. `assert` statements validate key parsing and chunk ordering, which can terminate optimized/debug runs differently. `full_output = args.full_output or (args.num_buckets is not None)` means the default bucket count makes commit mutations load even without `--full-output`. `print_top` assumes shard addresses are present when printing top results with shard finder. Current shard locations may not match historical operation locations, which the CLI warns about.

## Test Signals
The subset test file does not currently import this module successfully because it imports `RangeCounter`, which is not defined here. Missing tests include ByteBuffer decoding for each supported protocol, chunk reassembly and eviction, Timekeeper range selection, filter behavior, JSON output, top/bucket calculations, and CLI argument validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/transaction_profiling_analyzer/transaction_profiling_analyzer.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/transaction_profiling_analyzer/transaction_profiling_analyzer_tests.py -->
# sources/storage-engines/foundationdb/contrib/transaction_profiling_analyzer/transaction_profiling_analyzer_tests.py

## Purpose
This unit test file intends to validate a range-counting helper for transaction profiling analysis. It exercises insertion of key ranges into a sorted non-overlapping representation and verifies point counts across deterministic and randomized overlapping ranges.

## Important APIs, Types, And Functions
`RangeCounterTest` contains tests for one range, ascending and descending non-overlapping ranges, touching ranges, duplicate ranges, enclosing/enclosed ranges, before/after intersections, a wide multi-range overlap case, and randomized letter-range insertion. It expects `RangeCounter._insert_range`, `RangeCounter.get_count_for_key`, and a public `ranges` `SortedDict` mapping start key to `(end_key, count)`.

## Control Flow
Each deterministic test constructs `RangeCounter(1)`, inserts ranges, and asserts exact `SortedDict` segmentation. The random test repeats 100 runs of 100 random alphabetic ranges, maintains an independent per-letter count dictionary, and checks `get_count_for_key` after each insert.

## State And Persistence
State is local to each unittest case. There is no database access or file persistence.

## Dependencies And Integration Points
The tests import `sortedcontainers.SortedDict` and `RangeCounter` from `transaction_profiling_analyzer`. They are intended as local algorithm tests that do not require an FDB cluster.

## Risks
The tested `RangeCounter` symbol is absent from the current analyzer source, which defines `ReadCounter` and `WriteCounter` instead. As written, test collection fails at import before any assertions run. The random helper has an indentation/logical issue: `assert rc_count == v` appears outside the loop body that assigns `rc_count`, so it effectively checks only the last dictionary item rather than every item.

## Test Signals
The strongest current signal is negative: this test file is stale relative to the implementation. If `RangeCounter` is restored or replaced, the deterministic expected segmentations provide useful coverage for overlap splitting; the random case should be fixed to assert inside the loop.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/transaction_profiling_analyzer/transaction_profiling_analyzer_tests.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/documentation/CMakeLists.txt -->
# sources/storage-engines/foundationdb/documentation/CMakeLists.txt

## Purpose
This CMake file wires FoundationDB documentation targets into the build. It adds tutorial subdirectories, locates or bootstraps Sphinx, defines reusable documentation generation, serves local previews, and packages generated HTML into the project package set.

## Important APIs, Types, And Functions
`add_documentation_target` is the key CMake function. It accepts `GENERATOR`, optional `DOCTREE`, and optional `ADDITIONAL_ARGUMENTS`, computes an output directory and stamp file, globs Sphinx document files with `CONFIGURE_DEPENDS`, runs `sphinx-build` with `-W`, version/release defines, and creates a custom target named for the generator. Top-level targets include `html`, `docpreview`, and `package_html`.

## Control Flow
CMake first adds `tutorial` and `coro_tutorial`. It finds Python, then Sphinx. If Sphinx is missing, it creates a virtual environment under the build directory, runs `ensurepip`, installs `documentation/sphinx/requirements.txt`, sets `Sphinx_ROOT`, and retries `find_package(Sphinx REQUIRED)`. It then adds the HTML documentation target, chooses a preview server port from `DOCSERVER_PORT` or a stable username hash in the 8000-15999 range, and creates packaging dependencies from `packages` to `package_html` to `html`.

## State And Persistence
Build outputs are under the current binary directory: `sphinx-venv`, generator output directories, doctree cache, stamp files, preview-served HTML, and `${CMAKE_BINARY_DIR}/packages/*-docs-*.tar.gz`. Source files are not modified.

## Dependencies And Integration Points
Dependencies include CMake Python3 support, the repository `FindSphinx` module/package, Sphinx requirements, `FDB_VERSION`, the global `packages` target, and the documentation source tree at `documentation/sphinx`. It integrates with tutorial/coro tutorial builds via subdirectories.

## Risks
The function parses `ADDITIONAL_ARGUMENTS` but does not pass them to the Sphinx command. `message(ERROR ...)` is likely intended to be fatal but CMake fatal errors normally use `message(FATAL_ERROR ...)`. The virtualenv bootstrap performs network/package installation during configure/build if Sphinx is absent. The docs command uses `-W`, so warnings break builds, which is good for quality but brittle during doc changes.

## Test Signals
Signals are CMake configure success with and without a system Sphinx, `cmake --build . --target html`, `docpreview` binding to the expected port, and `package_html` producing the tarball under `packages`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/documentation/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/documentation/coro_tutorial/CMakeLists.txt -->
# sources/storage-engines/foundationdb/documentation/coro_tutorial/CMakeLists.txt

## Purpose
This one-line CMake file registers the coroutine tutorial executable and links it against `fdbclient`.

## Important APIs, Types, And Functions
It calls `add_flow_target(EXECUTABLE NAME coro_tutorial SRCS tutorial.cpp)` and `target_link_libraries(coro_tutorial PUBLIC fdbclient)`.

## Control Flow
During the documentation CMake traversal, this subdirectory defines the `coro_tutorial` target from `tutorial.cpp`, then attaches the FoundationDB client library.

## State And Persistence
It creates build-system target metadata only. No runtime persistence is involved.

## Dependencies And Integration Points
It depends on the FoundationDB build's `add_flow_target` helper and the `fdbclient` target. It integrates the coroutine tutorial into the normal CMake build graph.

## Risks
The file assumes `add_flow_target` is already in scope. Since the source uses Flow, RPC, and FDB client APIs, link or compile failures can appear here if those target dependencies are incomplete or if coroutine support flags are not propagated by `add_flow_target`.

## Test Signals
The main signal is a successful build of the `coro_tutorial` target.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/documentation/coro_tutorial/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/documentation/coro_tutorial/tutorial.cpp -->
# sources/storage-engines/foundationdb/documentation/coro_tutorial/tutorial.cpp

## Purpose
This executable is a Flow C++20 coroutine tutorial and demo harness. It shows timers, promises, triggers, RPC request streams, streaming replies, an in-memory key-value service, FDB client range reads/transactions, async generators, and basic network startup.

## Important APIs, Types, And Functions
Small actor demos include `simpleTimer`, `someFuture`, `promiseDemo`, `eventLoop`, and `triggerDemo`. RPC examples define `EchoServerInterface`, request/reply structs, `echoServer`, and `echoClient`, including `ReplyPromiseStream<StreamReply>`. The key-value demo defines `SimpleKeyValueStoreInterface`, `kvStoreServer`, `connect`, `kvSimpleClient`, `kvClient`, `throughputMeasurement`, and `multipleClients`. FDB client demos include `fdbClientStream`, `runTransactionWhile`, `runTransaction`, `runRYWTransaction`, `fdbClientGetRange`, and `fdbClient`. File/generator examples include `readBlocks`, `readLines`, and `testReadLines`. `actors` maps command-line names to runnable functions, and `main` initializes Flow networking and runs selected actors.

## Control Flow
`main` parses `-p` for server mode/listen port, `-s` for remote server address, `-C` for cluster file, and actor names. It initializes platform/network state, creates `FlowTransport`, optionally binds a server address, initializes `Net2FileSystem`, starts selected actors, wraps `waitForAll` in `stopAfter`, and runs the network. Server actors loop on `Choose().When(...)` over request streams. Client actors connect through well-known endpoints or FDB cluster files and perform coroutine awaits.

## State And Persistence
Most state is in-memory demo state: the echo interface, key-value `std::map`, operation counters, and actor futures. FDB examples read/write a real cluster using `clusterFile`, especially keys under `/tut/`. `testReadLines` reads `/etc/hosts`. Network endpoints are process state.

## Dependencies And Integration Points
The file depends on Flow coroutine primitives, FlowTransport/RPC serialization, deterministic random, `fdbclient` native API, ReadYourWrites, TLS/network filesystem setup, and `fmt`. It is built by the local `coro_tutorial` CMake target and is intended to be invoked manually with actor names shown in the `actors` map comments.

## Risks
Several demos are intentionally tutorial-grade rather than production-grade. Server loops run forever. `fdbClient` delays 30 seconds and writes to a real cluster. `fdbClientGetRange` appears to contain an extra closing brace near the range loop, which is a compile-risk unless hidden by surrounding syntax changes. `EchoServerInterface::serialize` omits `getInterface` even though the interface contains that stream, which may be intentional for bootstrap or a serialization bug. `StreamReply::expectedSize` returns `2e6` as `size_t`, and stream byte-limit behavior should be checked. `testReadLines` opens `/etc/hosts` with read-write flags, which may fail under normal permissions.

## Test Signals
Primary signals are compilation of `coro_tutorial`, running simple actors such as `timer`, paired server/client runs for echo and key-value demos, and manual FDB-cluster runs for range/transaction examples. The file has no automated tests in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/documentation/coro_tutorial/tutorial.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/documentation/sphinx/.pip.conf -->
# sources/storage-engines/foundationdb/documentation/sphinx/.pip.conf

## Purpose
This pip configuration sets a timeout for pip operations used by the documentation Sphinx environment.

## Important APIs, Types, And Functions
The file contains a `[global]` section with `timeout = 60`.

## Control Flow
There is no program control flow. Pip reads this configuration when the file is in an applicable config location or explicitly referenced by the environment.

## State And Persistence
The only state is the static timeout setting in source control.

## Dependencies And Integration Points
It relates to documentation dependency installation from CMake's virtualenv bootstrap, though that bootstrap does not explicitly point pip at this config file. Actual use depends on pip configuration discovery.

## Risks
If pip does not discover this file, the timeout has no effect. A 60-second timeout may still be too low for slow package indexes or too high for fast-failing CI expectations.

## Test Signals
Signals are pip install logs during documentation virtualenv setup and confirmation that pip reports or honors the configured timeout.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/documentation/sphinx/.pip.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/documentation/sphinx/conf.py -->
# sources/storage-engines/foundationdb/documentation/sphinx/conf.py

## Purpose
This is the Sphinx configuration for FoundationDB documentation. It configures extensions, theme, version metadata, HTML/LaTeX/man/Texinfo outputs, and enforces explicit roles by making the default role intentionally fail.

## Important APIs, Types, And Functions
The `extensions` list enables Sphinx built-ins plus local `brokenrole`, `relativelink`, and `rubydomain`. `sys.path.insert` exposes the local `extensions` directory. Version metadata is loaded from a `versions.target` XML file near the Python executable when present; otherwise CMake supplies `version` and `release` via `-D`. HTML uses `sphinx_bootstrap_theme` with local TOC sidebars and disabled Sphinx footer/source index features. `default_role = "broken"` routes unqualified backtick roles to the custom error role.

## Control Flow
At Sphinx startup, the module imports theme support, adds extension paths, optionally parses MSBuild XML version data, and assigns Sphinx config variables. No functions are defined here beyond configuration-time logic.

## State And Persistence
There is no runtime persistence. Sphinx consumes the config to create generated HTML, LaTeX, man, and Texinfo outputs in the build tree.

## Dependencies And Integration Points
Dependencies include `sphinx_bootstrap_theme`, Sphinx, local extensions, and optional `versions.target` XML. It integrates with `documentation/CMakeLists.txt`, which passes version/release overrides and points Sphinx at this config with `-c`.

## Risks
The computed `version_path` depends on `sys.executable`, which can differ between system Python, virtualenv Python, and packaged contexts. Copyright year and theme dependencies can drift. Setting `default_role` to a deliberately failing role is useful for docs hygiene but makes casual reST shorthand a hard build error under the CMake `-W` policy.

## Test Signals
Signals include successful `sphinx-build -W -b html`, correct rendered version/release strings, proper bootstrap theme rendering, and intentional failure when a document uses an unqualified default role.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/documentation/sphinx/conf.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/documentation/sphinx/extensions/brokenrole.py -->
# sources/storage-engines/foundationdb/documentation/sphinx/extensions/brokenrole.py

## Purpose
This Sphinx extension defines a role named `broken` that always emits an error. `conf.py` sets it as the default role to catch accidental single-backtick markup that lacks an explicit semantic role.

## Important APIs, Types, And Functions
`setup(app)` registers the role with `app.add_role("broken", broken_role)`. `broken_role` builds a reporter error with message `Broken role invoked`, wraps the raw text as a problematic node, and returns both the node and system message.

## Control Flow
Sphinx/docutils invokes `broken_role` whenever the `broken` role is used. Since it is the default role, unqualified interpreted text triggers this path.

## State And Persistence
No state is stored. Effects are limited to the current Sphinx parse/build.

## Dependencies And Integration Points
It depends on the docutils role callback contract supplied through Sphinx. It is loaded by `conf.py` and works with `-W` in the CMake docs build to turn these errors into build failures.

## Risks
This extension intentionally breaks builds for default-role usage; that is desired for markup discipline but can surprise documentation contributors. It does not return extension metadata such as version or parallel-read safety.

## Test Signals
A minimal reST document containing unqualified `` `text` `` should produce a Sphinx error, while explicit roles should not invoke this extension.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/documentation/sphinx/extensions/brokenrole.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/documentation/sphinx/extensions/relativelink.py -->
# sources/storage-engines/foundationdb/documentation/sphinx/extensions/relativelink.py

## Purpose
This Sphinx extension monkey-patches toctree resolution so toctree entries can contain relative internal links using `relative://path`, later emitted as plain relative `href` values.

## Important APIs, Types, And Functions
`setup(app)` imports `sphinx.environment.adapters.toctree` and `docutils.nodes`, saves `TocTree.resolve` as `old_resolve`, defines `resolve_toctree`, and replaces `TocTree.resolve`. The wrapper traverses resolved reference nodes and rewrites non-internal `refuri` values that start with `relative://`.

## Control Flow
During Sphinx toctree resolution, the patched method calls the original resolver, returns `None` unchanged, then mutates reference nodes in the resolved tree. The wrapper signature mirrors the Sphinx method signature but calls `old_resolve` with hard-coded values rather than forwarding the incoming `prune`, `maxdepth`, `titles_only`, `collapse`, and `includehidden` arguments.

## State And Persistence
It mutates the process-global Sphinx `TocTree.resolve` function for the duration of the Sphinx process. No files are persisted by the extension itself.

## Dependencies And Integration Points
It depends on Sphinx's internal `environment.adapters.toctree.TocTree` API and docutils reference node shape. It is loaded by `conf.py` and affects docs source files that use `relative://` in toctrees.

## Risks
Monkey-patching internal Sphinx APIs is version-sensitive. The wrapper currently ignores the caller's toctree-resolution arguments and always passes `prune=True`, `maxdepth=0`, `titles_only=False`, `collapse=False`, and `includehidden=False`, which can alter behavior outside relative-link rewriting. It also uses `result == None` rather than identity comparison.

## Test Signals
A docs build with a toctree entry like `Name <relative://some/path>` should render a relative href. Regression tests should also verify hidden/collapsed/maxdepth toctree behavior is not changed unintentionally by the hard-coded forwarding.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/documentation/sphinx/extensions/relativelink.py -->
