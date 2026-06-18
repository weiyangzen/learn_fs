# subset-b-008452 FoundationDB fdbrpc coroutine, libeio, KAIO, and file-transfer research

This grouped report covers the requested FoundationDB `fdbrpc` coroutine support, bundled `libeio`, Linux KAIO syscall shim, and file-transfer protobuf files. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/libcoroutine/386-ucontext.h -->
# sources/storage-engines/foundationdb/fdbrpc/libcoroutine/386-ucontext.h

## Purpose

This vendored header defines a minimal i386 `ucontext_t`/`mcontext_t` ABI for platforms where FoundationDB's old `libcoroutine` cannot rely on a usable system `ucontext` implementation. It maps `getcontext` and `setcontext` to private `getmcontext`/`setmcontext` routines implemented in `asm.S`, allowing `Coro.c` and `context.c` to build portable user-space context switching on older BSD/OpenBSD/Apple-style environments.

## Important APIs, types, and functions

The file exposes `mcontext_t`, `ucontext_t`, `swapcontext()`, `makecontext()`, `getmcontext()`, and `setmcontext()`. `struct mcontext` stores i386 segment registers, general registers, trap/error fields, instruction pointer, stack pointer, flags, and x87 floating-point storage. `struct ucontext` carries a signal mask, machine context, link, stack, and spare space. The first context fields intentionally match older `sigcontext` layout assumptions.

## Control flow, state, and persistence

The header itself has no runtime control flow. Its layout controls how assembly saves/restores register state and how `context.c` writes new instruction and stack pointers in `makecontext()`. Runtime state is entirely in caller-owned `ucontext_t` instances, usually inside `struct Coro`. Nothing is persisted beyond process memory.

## Dependencies and integration points

It assumes `sigset_t` and `stack_t` are visible before inclusion through `taskimpl.h`/system headers. `taskimpl.h` includes it for Apple i386 and OpenBSD i386 after renaming the public type names to `libthread_*` names, avoiding direct collision with system headers. `asm.S` depends on the exact byte offsets of the i386 `mcontext` fields, and `context.c` depends on `mc_eip` and `mc_esp`.

## Risks and test signals

The risk is ABI drift: any field reorder, size mismatch, or platform where `sigset_t`/`stack_t` differs from the assumed layout can corrupt registers or crash on context switch. The file also does not model modern SIMD state beyond the old x87 block. Test signals are successful build on the targeted legacy i386 platforms, coroutine creation/switch tests, and FoundationDB CoroFlow workloads completing without stack/register corruption.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/libcoroutine/386-ucontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/libcoroutine/Base.h -->
# sources/storage-engines/foundationdb/fdbrpc/libcoroutine/Base.h

## Purpose

`Base.h` is a tiny common include guard for the vendored coroutine support. It centralizes standard C library includes needed by the old Steve Dekorte coroutine code and prevents repeated inclusion through `IOBASE_DEFINED`.

## Important APIs, types, and functions

There are no exported functions or data types. The file includes `stdio.h`, `stdlib.h`, `string.h`, `stddef.h`, `time.h`, `setjmp.h`, and `stdarg.h`.

## Control flow, state, and persistence

The file has no runtime behavior and no state. Its only effect is compile-time inclusion of common C declarations.

## Dependencies and integration points

`Coro.c` includes this file before using C runtime APIs and `jmp_buf`-related declarations. It is part of the `coro` static library when `COROUTINE_IMPL` is `libcoro`.

## Risks and test signals

Risk is low, but because this is a broad umbrella header, changes can affect old platform branches in `Coro.c`. Test by compiling the `coro` target across POSIX and Windows coroutine configurations.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/libcoroutine/Base.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/libcoroutine/Common.c -->
# sources/storage-engines/foundationdb/fdbrpc/libcoroutine/Common.c

## Purpose

`Common.c` implements memory helper functions used by the coroutine library and optional allocation tracking when `IO_CHECK_ALLOC` is enabled. It also provides byte-order utility functions used by the old BaseKit-style support code.

## Important APIs, types, and functions

With `IO_CHECK_ALLOC`, the file defines `MemoryBlock` headers placed before each returned allocation, linked-list tracking through `baseblock()`, and wrappers `io_real_malloc()`, `io_real_calloc()`, `io_real_realloc()`, `io_free()`, `io_show_mem()`, `io_showUnfreed()`, and allocation counters. Always-built helpers are `cpalloc()`, `io_freerealloc()`, `io_isBigEndian()`, and `io_uint32InBigEndian()`.

## Control flow, state, and persistence

In tracking mode, allocations are routed through `MemoryBlock_newWithSize_file_line_()`, inserted into a global linked list, and removed on free or realloc. Counters track allocation count, realloc count, current bytes, maximum bytes, and frees. In normal builds, `Common.h` maps `io_malloc`/`io_calloc`/`io_free` directly to libc and `io_realloc` to `io_freerealloc()`, so the tracking code is compiled out. State is process-local and reset at process start; there is no persistence.

## Dependencies and integration points

`Common.h` declares these APIs and macro-selects the tracked or direct allocator path. `Coro.c` uses `io_calloc()` and `io_free()` for `Coro` objects and stacks, so out-of-memory behavior and optional leak reports flow through this file. The code depends on `stdio.h`, `string.h`, and integer typedefs from `Common.h`.

## Risks and test signals

The tracking allocator is not protected by locks, so it is unsafe if enabled for concurrent coroutine allocation. `io_real_calloc()` does not zero the user allocation, despite the `calloc` name, which would be a serious behavior mismatch if tracking mode were enabled. `io_isBigEndian()` returns the first byte of integer `1`, so its truth value is little-endian rather than big-endian; as written, `io_uint32InBigEndian()` appears inverted if it is used for host-to-big-endian conversion. Test signals include coroutine allocation/free under `COROUTINE_IMPL=libcoro`, optional `IO_CHECK_ALLOC` leak output, and endian conversion tests on little- and big-endian hosts.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/libcoroutine/Common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/libcoroutine/Common.h -->
# sources/storage-engines/foundationdb/fdbrpc/libcoroutine/Common.h

## Purpose

`Common.h` is the portability and allocator facade for `libcoroutine`. It normalizes integer typedefs on older systems, handles Windows and DBCS feature macros, exposes `BASEKIT_API`, and maps `io_*` allocation functions either to debug wrappers or libc.

## Important APIs, types, and functions

The file defines fallback `uint8_t`, `int8_t`, `uint16_t`, `int16_t`, `uint32_t`, `int32_t`, `uint64_t`, and `int64_t` for platforms without standard integer headers. It sets Windows-specific macros such as `HAS_FIBERS` and `ON_WINDOWS`, DBCS helpers `ismbchar()` and `mbcharlen()`, allocator macros `io_malloc`, `io_calloc`, `io_realloc`, `io_free`, and declarations for `cpalloc()`, `io_freerealloc()`, `io_isBigEndian()`, and `io_uint32InBigEndian()`.

## Control flow, state, and persistence

There is no direct runtime flow. Compile-time branches decide whether coroutine code uses Win32 fibers, system headers, debug allocation tracking, or direct libc allocation. The optional allocation state lives in `Common.c`; otherwise there is no state.

## Dependencies and integration points

`Coro.c` and `Common.c` include this header. On Windows it includes `winsock2.h`, `memory.h`, `string.h`, and `malloc.h`, and maps `usleep()` to `Sleep()`. It affects `Coro.h` implementation choice indirectly by defining `HAS_FIBERS`.

## Risks and test signals

The header carries many legacy platform branches and globally visible macro rewrites, so include-order changes can cause surprises. In tracking mode, macro replacement changes allocation semantics and exposes the nonzeroing `io_real_calloc()` issue in `Common.c`. Test by compiling both Windows/fiber and POSIX/ucontext builds and by running coroutine lifecycle tests under normal and allocation-checking configurations.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/libcoroutine/Common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/libcoroutine/Coro.c -->
# sources/storage-engines/foundationdb/fdbrpc/libcoroutine/Coro.c

## Purpose

`Coro.c` implements FoundationDB's old `libcoroutine` backend: stack allocation, coroutine startup, context setup, and cooperative switching. In this repository it is built into the `coro` static library when `COROUTINE_IMPL` is `libcoro`, and `fdbserver/coroimpl/CoroFlowCoro.actor.cpp` uses it to run coroutine-style worker code.

## Important APIs, types, and functions

Public functions are `Coro_new()`, `Coro_free()`, `Coro_stack()`, `Coro_stackSize()`, `Coro_setStackSize_()`, `Coro_bytesLeftOnStack()`, `Coro_stackSpaceAlmostGone()`, `Coro_initializeMainCoro()`, `Coro_startCoro_()`, `Coro_switchTo_()`, and private `Coro_setup()`. Internal startup helpers are `CallbackBlock`, `Coro_StartWithArg()`, and `Coro_Start()`. The file integrates with FoundationDB's `g_stackYieldLimit`, `setProfilingEnabled()`, and `criticalError()`.

## Control flow, state, and persistence

`Coro_new()` allocates a zeroed `Coro` and initializes requested stack size. `Coro_startCoro_()` creates a stack for the target coroutine, builds an initial machine context using `Coro_setup()`, then immediately switches to it. The startup trampoline calls the user callback with its context and aborts through `criticalError()` if the callback returns unexpectedly. `Coro_switchTo_()` updates `g_stackYieldLimit`, then switches through fibers, `swapcontext()`, or `setjmp`/`longjmp` depending on compile-time backend. `Coro_initializeMainCoro()` marks the current thread as the main coroutine and estimates its stack. State is held in `Coro` objects, allocated stacks, platform context objects, and the process-global stack-yield/profiling hooks.

## Dependencies and integration points

The file includes `Common.h`, `flow/Platform.h`, `Base.h`, `Coro.h`, and `taskimpl.h` for platform context declarations. CMake compiles it with `USE_UCONTEXT` on non-Windows and `USE_FIBERS` on Windows. `CoroFlowCoro.actor.cpp` wraps `Coro_startCoro_()` and `Coro_switchTo_()` in FoundationDB's coroutine thread-pool implementation. Valgrind integration optionally registers coroutine stacks.

## Risks and test signals

This file is highly ABI-sensitive. The `setjmp` fallback edits private `jmp_buf` fields on several architectures. The ucontext x86-64 path splits pointer arguments into two `unsigned int` values for `makecontext()`. Stack accounting assumes downward-growing stacks; the upward path is disabled. `Coro_allocStackIfNeeded()` sets `requestedStackSize` to zero when freeing an oversized stack, which can make a later allocation invalid if that branch is reached. Test signals are CoroFlow startup/shutdown tests, context switching under sanitizer/Valgrind, slow-task profiling behavior around switches, and stress tests that exercise stack-depth warnings through `g_stackYieldLimit`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/libcoroutine/Coro.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/libcoroutine/Coro.h -->
# sources/storage-engines/foundationdb/fdbrpc/libcoroutine/Coro.h

## Purpose

`Coro.h` declares the public coroutine object and selects the implementation backend. It is the API consumed by FoundationDB's old CoroFlow implementation.

## Important APIs, types, and functions

The header defines stack-size defaults (`CORO_DEFAULT_STACK_SIZE`, `CORO_STACK_SIZE_MIN`), backend macros (`USE_FIBERS`, `USE_UCONTEXT`, `USE_SETJMP`), `CORO_IMPLEMENTATION`, `CoroStartCallback`, and `struct Coro`. `struct Coro` stores requested/allocated stack sizes, stack pointer, optional Valgrind stack id, backend-specific context handle (`fiber`, `ucontext_t`, or `jmp_buf`), and `isMain`. It declares creation, destruction, stack, startup, switching, and setup APIs.

## Control flow, state, and persistence

The header has compile-time control flow that chooses fibers on Windows with fiber support, ucontext when `HAS_UCONTEXT` or a forced `USE_UCONTEXT` is present, and `setjmp` otherwise. Runtime state is the `Coro` object created by `Coro.c`; no state is persisted.

## Dependencies and integration points

On non-Windows it includes `taskimpl.h`; on ucontext builds it includes `<sys/ucontext.h>`. `fdbserver/coroimpl/CoroFlowCoro.actor.cpp` includes this header directly. CMake forces `USE_UCONTEXT` or `USE_FIBERS` for the `coro` target, so the auto-detection branch is usually overridden in FoundationDB builds.

## Risks and test signals

The main risks are backend selection drift and stack-size mismatch. Some platform branches depend on macros such as `HAS_UCONTEXT` that may not be consistently provided outside the configured CMake target. Test by building all supported `COROUTINE_IMPL=libcoro` platforms, checking `CORO_IMPLEMENTATION`, and running CoroFlow tests under normal and low-stack conditions.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/libcoroutine/Coro.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/libcoroutine/amd64-ucontext.h -->
# sources/storage-engines/foundationdb/fdbrpc/libcoroutine/amd64-ucontext.h

## Purpose

This vendored header defines a minimal AMD64 `ucontext_t`/`mcontext_t` layout for platforms where `libcoroutine` uses private context save/restore routines rather than system `ucontext`. It targets Apple x86-64 through `taskimpl.h` and pairs with `asm.S` and `context.c`.

## Important APIs, types, and functions

It maps `setcontext()` and `getcontext()` to `setmcontext()` and `getmcontext()`, typedefs `mcontext_t` and `ucontext_t`, and declares `swapcontext()`, `makecontext()`, `getmcontext()`, and `setmcontext()`. `struct mcontext` stores AMD64 argument registers, callee-saved registers, trap metadata, `mc_rip`, `mc_rsp`, flags, FP format/ownership fields, XMM/FPU storage, and spare fields. `struct ucontext` holds signal mask, machine context, link, stack, and spare space.

## Control flow, state, and persistence

The file only defines layout and declarations. `context.c` fills `mc_rdi`, `mc_rsi`, `mc_rip`, and `mc_rsp` for new contexts; `asm.S` saves and restores the register slots. State is process-memory context snapshots inside coroutine objects.

## Dependencies and integration points

`taskimpl.h` includes this file for Apple x86-64 after renaming the system type names to `libthread_*`. `Coro.c` uses the resulting `ucontext_t` in its `USE_UCONTEXT` backend. `asm.S` uses fixed offsets corresponding to this struct, so this header and assembly must stay in lockstep.

## Risks and test signals

ABI and stack alignment are the key risks. If offsets diverge from `asm.S` or `makecontext()` stack setup, context switches can restore wrong registers. The header only captures the FP state shape expected by the vendored code. Test with Apple x86-64 `libcoro` builds, coroutine switch stress, and tests that pass pointer arguments through `makecontext()` startup.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/libcoroutine/amd64-ucontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/libcoroutine/asm.S -->
# sources/storage-engines/foundationdb/fdbrpc/libcoroutine/asm.S

## Purpose

`asm.S` provides low-level `getmcontext`/`setmcontext` routines for platforms where `libcoroutine` needs a portable replacement for missing or unsuitable system context APIs. It covers legacy i386, AMD64, PowerPC, and ARM cases through preprocessor-selected assembly.

## Important APIs, types, and functions

The externally visible symbols are selected by macros `SET` and `GET`, usually `setmcontext`/`getmcontext` or underscored Apple variants. Conditional blocks define `NEEDX86CONTEXT`, `NEEDAMD64CONTEXT`, `NEEDPOWERCONTEXT`, and `NEEDARMCONTEXT`. Each `GET` stores enough registers into the matching `mcontext_t` layout, and each `SET` restores registers and transfers control to the saved PC/LR/RIP/EIP path.

## Control flow, state, and persistence

At compile time, OS/architecture macros select one assembly implementation. At runtime, `GET` snapshots current register state and returns 0; `SET` restores the stored context and resumes as though `GET` returned nonzero. This is the primitive used by `context.c`'s `swapcontext()` and by `Coro.c`'s ucontext backend. State is only the caller-provided `mcontext_t`.

## Dependencies and integration points

The assembly depends directly on the field offsets defined by `386-ucontext.h`, `amd64-ucontext.h`, `power-ucontext.h`, or Linux ARM system context layout. CMake includes this file in the `coro` target on Apple. It is also relevant for OpenBSD/i386 and Linux/ARM branches if built with the vendored context path.

## Risks and test signals

This is the highest-risk part of the coroutine support: register save sets, stack alignment, calling conventions, and symbol naming must match the platform exactly. PowerPC comments note missing vector/floating-point handling in the companion header, which can matter for code using those registers across coroutine switches. Test by running tight context-switch loops, CoroFlow workloads with optimized builds, and architecture-specific sanitizer/debugger checks for preserved callee-saved registers.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/libcoroutine/asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/libcoroutine/context.c -->
# sources/storage-engines/foundationdb/fdbrpc/libcoroutine/context.c

## Purpose

`context.c` implements missing `makecontext()` and `swapcontext()` functions for the vendored coroutine context layer. It complements the private `getmcontext`/`setmcontext` assembly and lets `Coro.c` use a ucontext-like API on Apple, old FreeBSD/OpenBSD i386, and Linux ARM.

## Important APIs, types, and functions

Depending on platform macros, the file defines `makecontext()` for PowerPC, i386, AMD64, and ARM, plus `swapcontext()` when `NEEDSWAPCONTEXT` is selected. The AMD64 implementation expects exactly two integer arguments, stores them into `mc_rdi` and `mc_rsi`, aligns the stack, writes a fake return address, and sets `mc_rip`/`mc_rsp`.

## Control flow, state, and persistence

Compile-time branches select the needed implementation. `makecontext()` mutates a provided `ucontext_t` by setting the initial stack pointer, program counter, and argument registers/stack slots. `swapcontext()` calls `getcontext()` on the outgoing context and, only on the initial return, calls `setcontext()` for the incoming context. There is no persistent state outside the mutated context objects.

## Dependencies and integration points

It includes `taskimpl.h`, which selects the correct vendored or system `ucontext_t` definition. `Coro.c` calls `makecontext()` from `Coro_setup()` and `swapcontext()` from `Coro_switchTo_()`. CMake includes this file in `coro` for non-Windows builds.

## Risks and test signals

The `makecontext()` variants depend on stack growth and alignment rules. AMD64 traps if called with an argument count other than two, matching the pointer-splitting convention in `Coro.c`; future callers must preserve that contract. ARM setup writes general registers but does not provide deep signal-mask behavior. Test by starting coroutines with pointer contexts, switching repeatedly, and validating on Apple x86/x86-64 and Linux ARM builds if those targets remain supported.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/libcoroutine/context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/libcoroutine/power-ucontext.h -->
# sources/storage-engines/foundationdb/fdbrpc/libcoroutine/power-ucontext.h

## Purpose

This header defines a minimal PowerPC context layout for vendored coroutine context switching. It is used by `taskimpl.h` on non-x86 Apple and some OpenBSD fallback paths.

## Important APIs, types, and functions

The file maps `setcontext()`/`getcontext()` to `_setmcontext()`/`_getmcontext()`, typedefs `mcontext_t` and `ucontext_t`, and declares `makecontext()`, `swapcontext()`, `_getmcontext()`, and `_setmcontext()`. `struct mcontext` stores link register/program counter, condition register, counter, XER, stack pointer, TOC, first argument/return register `r3`, and callee-saved `r13` through `r31`. `struct ucontext` includes a simple stack object, signal mask, and machine context.

## Control flow, state, and persistence

No runtime control flow exists in the header. `asm.S` fills/restores the context fields, and `context.c` uses them to prepare new stacks and function entry. State is per-context process memory.

## Dependencies and integration points

It requires `ulong`, `uint`, and `sigset_t` declarations from `taskimpl.h` and system includes. It integrates with the `NEEDPOWERCONTEXT` and `NEEDPOWERMAKECONTEXT` code paths in `asm.S` and `context.c`.

## Risks and test signals

The header explicitly does not save vector or floating-point state, so code relying on those callee-saved registers across coroutine switches can break. Type assumptions for `ulong`/`uint` also make it sensitive to include order. Test signals are successful old PowerPC builds, preserved scalar callee-saved registers across switches, and workload tests that would expose FP/vector corruption if this target is used.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/libcoroutine/power-ucontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/libcoroutine/taskimpl.h -->
# sources/storage-engines/foundationdb/fdbrpc/libcoroutine/taskimpl.h

## Purpose

`taskimpl.h` is the platform selection layer inherited from Russ Cox-style coroutine/task code. It configures `ucontext` availability, pulls in system headers, and substitutes vendored context definitions for platforms with broken or removed `ucontext` APIs.

## Important APIs, types, and functions

The file defines utility macros `nil` and `nelem()`, SunOS makecontext feature macros, `USE_UCONTEXT` overrides for OpenBSD and macOS 10.5+, Apple/OpenBSD type renames to `libthread_mcontext_t`/`libthread_ucontext_t`, and declarations for legacy FreeBSD and ARM `getmcontext()`/`setmcontext()` APIs. Large commented-out `Task` definitions document the original library lineage but are not active.

## Control flow, state, and persistence

All behavior is compile-time. The header decides whether `<ucontext.h>` is included and whether local `386-ucontext.h`, `amd64-ucontext.h`, or `power-ucontext.h` is used. It holds no runtime state.

## Dependencies and integration points

`Coro.h`, `Coro.c`, and `context.c` include this file on non-Windows builds. It depends on POSIX headers such as `unistd.h`, `sys/time.h`, `signal.h`, `sys/utsname.h`, and `inttypes.h`. The CMake `coro` target forces `USE_UCONTEXT` on non-Windows, but this header can still undefine or replace parts for specific OSes.

## Risks and test signals

Because it uses broad platform macros and type renaming, subtle OS version changes can select the wrong context path. OpenBSD forcibly disables `USE_UCONTEXT`, while CMake may define it, so build behavior should be verified if that target matters. Test by compiling `coro` across configured platforms, ensuring no system/vendored `ucontext_t` conflicts, and running context switch smoke tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/libcoroutine/taskimpl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/libeio/ecb.h -->
# sources/storage-engines/foundationdb/fdbrpc/libeio/ecb.h

## Purpose

`ecb.h` is the bundled libecb compatibility header used by `libeio`. It provides compiler/architecture feature detection, memory fences, inline/attribute macros, branch prediction hints, bit operations, byte swapping, endian tests, and arithmetic helpers.

## Important APIs, types, and functions

The file defines fixed-width integer typedefs on Windows, `ECB_GCC_VERSION()`, `ECB_MEMORY_FENCE` and acquire/release variants, `ecb_inline`, `ecb_restrict`, `ecb_attribute()`, `ecb_expect()`, `ecb_likely()`, `ecb_unlikely()`, bit helpers `ecb_ctz32/64`, `ecb_popcount32/64`, `ecb_ld32/64`, rotation helpers, `ecb_bswap16/32/64`, `ecb_unreachable()`, `ecb_assume()`, endian helpers `ecb_big_endian()` and `ecb_little_endian()`, `ecb_mod()`, division rounding macros, and `ecb_array_length()`.

## Control flow, state, and persistence

Most functionality is inline or macro-only. If no architecture/compiler fence is available and pthread fallback is allowed, it declares a static `pthread_mutex_t ecb_mf_lock` used by `ECB_MEMORY_FENCE`, which is process-local state. Otherwise the header has no persistent state.

## Dependencies and integration points

`eio.c` includes this header for `ecb_inline`, `ecb_noinline`, `ecb_cold`, branch prediction, endian-aware sorting, and other low-level helpers. The fence macros may pull in pthreads, but FoundationDB builds `eio` as a static C library and links it into `fdbrpc` when bundled `libeio` is compiled.

## Risks and test signals

This old compatibility header uses architecture-specific assembly and compiler-version heuristics. Incorrect fence selection can cause queue visibility bugs on weak memory models; incorrect bit/endian helpers can affect directory entry sorting. Test signals are clean `eio` compilation on the target compiler, thread sanitizer runs around request queues, and readdir ordering tests on large directories.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/libeio/ecb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/libeio/eio.c -->
# sources/storage-engines/foundationdb/fdbrpc/libeio/eio.c

## Purpose

`eio.c` is the bundled libeio implementation that gives FoundationDB asynchronous POSIX-style filesystem operations through a detached worker-thread pool. `AsyncFileEIO.h` initializes it, submits open/read/write/fsync/stat/custom requests, and polls completions from the Flow network thread.

## Important APIs, types, and functions

Public API implementations include `eio_init()`, `eio_poll()`, tuning setters, counters, `eio_submit()`, `eio_cancel()`, synchronous working-directory helpers, request wrappers such as `eio_open()`, `eio_read()`, `eio_write()`, `eio_fsync()`, `eio_stat()`, `eio_readdir()`, `eio_custom()`, group functions, and `eio_sendfile_sync()`. Internal subsystems include priority queues `req_queue` and `res_queue`, worker management through `etp_proc()`, `etp_start_thread()`, and `etp_maybe_start_thread()`, execution dispatch in `eio_execute()`, completion in `eio_finish()`, and helper implementations for `sendfile`, `realpath`, `readdir`, `sync_file_range`, `mlock`, `msync`, `fallocate`, and missing POSIX functions.

## Control flow, state, and persistence

`eio_init()` creates mutexes/condition variables and initializes global queues/counters. `eio_submit()` normalizes priority, increments in-flight counters, and either places normal requests on `req_queue` for worker threads or places group requests directly on `res_queue`. Workers in `etp_proc()` wait on `reqwait`, execute requests via `eio_execute()`, record `errno` into `req->errorno`, then push completed requests to `res_queue` and call `want_poll_cb` when the poller should wake. `eio_poll()` drains completed requests, decrements counters, invokes finish callbacks unless cancelled, destroys request-owned buffers, and enforces optional max-time/max-request budgets. Group requests track child counts, optional feed callbacks, cancellation propagation, and delayed group completion while children remain. State is global process memory: thread counts, idle limits, queues, locks, callbacks, and per-worker temporary buffers.

## Dependencies and integration points

The file includes platform config headers, `eio.h`, `ecb.h`, and `xthread.h`. It uses pthreads or Windows pthread wrappers, POSIX file APIs, `openat`/`*at` APIs when available, platform `sendfile`, `mmap` synchronization, and Linux syscalls where configured. In FoundationDB, CMake builds it as static library `eio` on non-Windows when no system `eio` is used, with warnings disabled and `USE_UCONTEXT` defined. `AsyncFileEIO` calls `eio_set_max_parallel()`, `eio_init()`, `eio_poll()`, wrappers, and `eio_custom()` for platform-specific fsync work.

## Risks and test signals

The implementation uses global state and is intended to be initialized once. Cancellation is cooperative: it sets `cancelled`, short-circuits queued execution, and can interrupt long `readdir`/`mtouch` loops, but it cannot stop arbitrary blocking syscalls already running. Worker shutdown uses sentinel requests and detached threads. Some emulations, especially `pread`/`pwrite` via `lseek`, `sendfile` fallback, and `realpath`, have race or performance caveats. In `eio__mtouch()`, the page-walk loop compares the absolute address against `len` rather than the computed end, which looks suspicious for multi-page ranges. Test signals include `AsyncFileEIO` open/read/write/truncate/fsync/stat tests, cancellation-on-future-error paths, high concurrency with `FLOW_KNOBS->EIO_MAX_PARALLELISM`, parent-directory fsync/custom requests, and thread sanitizer or stress tests around queue counters.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/libeio/eio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/libeio/eio.h -->
# sources/storage-engines/foundationdb/fdbrpc/libeio/eio.h

## Purpose

`eio.h` is the public API contract for the bundled libeio asynchronous I/O library. It defines request types, callback signatures, request layout, result macros, tuning APIs, wrapper constructors, groups, and cancellation/submission functions.

## Important APIs, types, and functions

Key types are `eio_req`, `eio_dirent`, `eio_cb`, `eio_wd`, `eio_uid_t`, `eio_gid_t`, `eio_ssize_t`, `eio_ino_t`, and `eio_tstamp`. Important enums cover readdir flags, directory entry types, memory sync/touch flags, sync-file-range flags, fallocate flags, request types from `EIO_CUSTOM` through `EIO_READLINK`, mlockall constants, and priorities. `struct eio_req` stores path/FD parameters, buffers, offsets, result/error state, cancellation flag, priority, user data, finish/destroy/feed callbacks, and group links. Public functions include initialization/polling/tuning/counters, many operation wrappers, group APIs, `eio_submit()`, `eio_cancel()`, and `eio_sendfile_sync()`.

## Control flow, state, and persistence

This header declares the lifecycle contract: callers create a zeroed request through wrappers or manually, submit it, wait for `want_poll` notification, call `eio_poll()` regularly, inspect `result`/`errorno` in the finish callback, and let libeio destroy request-owned resources. Runtime state lives in `eio.c` and in active `eio_req` objects. Nothing is persisted across process exit.

## Dependencies and integration points

It includes `stddef.h`, `signal.h`, `sys/types.h`, and `stdio.h`. `AsyncFileEIO.h` includes this header and uses both wrappers and direct manual `eio_req` construction for Apple `F_FULLFSYNC` custom handling. CMake adds `fdbrpc/libeio` as a private include directory for `fdbrpc` and `fdbrpc_sampling`.

## Risks and test signals

The struct is part of the in-repo C/C++ ABI between `AsyncFileEIO` and `eio.c`; field changes can break manual request construction. `cancelled` is `unsigned char` on i386/amd64 and `sig_atomic_t` elsewhere, so memory-order assumptions are minimal. Request buffers may be owned either by the caller or by libeio depending on flags, which is an easy source of lifetime bugs. Test by building `AsyncFileEIO`, exercising direct and wrapper-created requests, and checking finish callbacks do not access freed data.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/libeio/eio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/libeio/xthread.h -->
# sources/storage-engines/foundationdb/fdbrpc/libeio/xthread.h

## Purpose

`xthread.h` abstracts thread, mutex, condition variable, signal-mask, and result-pipe operations for libeio across Windows and POSIX platforms. It lets `eio.c` use one set of `X_*` macros for worker-thread management.

## Important APIs, types, and functions

The file defines `xmutex_t`, `xcond_t`, `xthread_t`, `X_MUTEX_INIT`, `X_MUTEX_CREATE`, `X_LOCK`, `X_UNLOCK`, `X_COND_INIT`, `X_COND_CREATE`, `X_COND_SIGNAL`, `X_COND_WAIT`, `X_COND_TIMEDWAIT`, `X_THREAD_PROC`, `X_THREAD_ATFORK`, `thread_create()`, and `respipe_read`/`respipe_write`/`respipe_close`. POSIX builds optionally use adaptive mutexes on Linux and create detached pthreads with signals blocked during `pthread_create()`.

## Control flow, state, and persistence

`thread_create()` initializes detached thread attributes, blocks all signals around pthread creation on POSIX so workers do not inherit signal delivery, creates the thread, restores the old signal mask, and destroys attributes. On Windows it uses pthread-compatible wrappers and socket-style result pipe functions. It holds no persistent state beyond objects owned by callers.

## Dependencies and integration points

`eio.c` includes this header after optionally mapping `EIO_STACKSIZE` to `X_STACKSIZE`. The file depends on pthread headers for both POSIX and the Windows compatibility path in this vendored copy, plus WinSock/Windows headers for `_WIN32`.

## Risks and test signals

The POSIX code comments out explicit stack-size setting to avoid jemalloc-related stack overflow, so worker stacks use platform defaults. Signal masking around worker creation is important for FoundationDB processes that manage signals centrally; regressions could deliver signals on I/O workers. Test with libeio worker startup/shutdown, signal-handling tests, and high-concurrency AsyncFileEIO workloads.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/libeio/xthread.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/linux_kaio.h -->
# sources/storage-engines/foundationdb/fdbrpc/linux_kaio.h

## Purpose

`linux_kaio.h` is a small Linux native asynchronous I/O syscall shim for FoundationDB's `AsyncFileKAIO` implementation. It avoids relying on a separate libaio wrapper by declaring the kernel IOCB/result structures and thin syscall functions.

## Important APIs, types, and functions

The file defines `io_context_t` as `struct io_context*`, operation constants `IO_CMD_PREAD`, `IO_CMD_PWRITE`, `IO_CMD_FSYNC`, and `IO_CMD_FDSYNC`, `struct linux_iocb`, `struct linux_ioresult`, and static wrappers `io_setup()`, `io_submit()`, and `io_getevents()`. `linux_iocb` includes user data, opcode, priority, fd, buffer, byte count, offset, flags, and eventfd; `linux_ioresult` returns user data, original IOCB pointer, result, and secondary result.

## Control flow, state, and persistence

The wrappers directly call `syscall(__NR_io_setup)`, `syscall(__NR_io_submit)`, and `syscall(__NR_io_getevents)`. The header stores no state; kernel AIO state is held in the `io_context_t` owned by `AsyncFileKAIO`.

## Dependencies and integration points

`AsyncFileKAIO.h` includes this header, initializes a context with `io_setup(FLOW_KNOBS->MAX_OUTSTANDING, ...)`, submits arrays of `linux_iocb*`, and collects `linux_ioresult` events. The header assumes syscall numbers, `syscall()`, `uint*_t`, `timespec`, and related Linux types are available from the including translation unit.

## Risks and test signals

The struct layout must match the Linux kernel ABI exactly. Return values from raw syscalls are negative error codes rather than libc-style `-1` with `errno` in some paths, and callers must handle that carefully. Kernel AIO has filesystem and alignment limitations, and this header does not wrap `io_destroy()`. Test with `AsyncFileKAIO` read/write/fsync/truncate workloads, eventfd polling, error paths such as `EAGAIN`, and Linux ABI compatibility across supported architectures.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/linux_kaio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/protos/file_transfer.proto -->
# sources/storage-engines/foundationdb/fdbrpc/protos/file_transfer.proto

## Purpose

`file_transfer.proto` defines the gRPC contract for FoundationDB fdbrpc file transfer support. It supports querying file metadata and streaming file contents in chunks.

## Important APIs, types, and functions

The `fdbrpc.FileTransferService` service has unary `GetFileInfo(GetFileInfoRequest) returns (GetFileInfoReply)` and server-streaming `DownloadFile(DownloadRequest) returns (stream DownloadChunk)` RPCs. `DownloadRequest` carries `file_name`, `chunk_size`, and `first_chunk_index`. `DownloadChunk` carries `offset` and raw `data`. `GetFileInfoRequest` carries `file_name`, `get_size`, and `get_crc_checksum`. `GetFileInfoReply` carries `file_size` and `crc_checksum`.

## Control flow, state, and persistence

The proto has no runtime state itself. Generated stubs drive `FileTransferServiceImpl` and `FileTransferClient`: the server opens the requested file, streams chunks from `first_chunk_index * chunk_size`, and optionally computes size and CRC32C metadata. Persistence is the underlying file on disk, outside the proto contract.

## Dependencies and integration points

`fdbrpc/CMakeLists.txt` runs `generate_grpc_protobuf(fdbrpc.file_transfer protos/file_transfer.proto)` when `WITH_GRPC` is enabled and links `proto_fdbrpc_file_transfer` into `fdbrpc` and `fdbrpc_sampling`. `FileTransfer.h/.cpp` include the generated `file_transfer.pb.h` and `file_transfer.grpc.pb.h`. `FlowGrpcTests.cpp` registers `FileTransferServiceImpl` and tests normal transfer and error-injection paths.

## Risks and test signals

The protocol trusts `file_name` as supplied by the caller; path authorization and sandboxing must be enforced by the service layer or deployment context. `chunk_size` is `int32`; the implementation defaults nonpositive values but large values can drive memory allocation. CRC32C is useful for corruption detection but is not a strong checksum, and the file notes TODOs for stronger or partial checksums. Test signals are generated-code builds with `WITH_GRPC`, gRPC file transfer tests, resume-from-`first_chunk_index` behavior, checksum mismatch detection, and compatibility checks before changing field numbers.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/protos/file_transfer.proto -->
