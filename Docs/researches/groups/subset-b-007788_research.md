# Research Report: subset-b-007788

This grouped report covers the assigned OpenAFS LWP, OPR, and MacOS packaging files. Each file section is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/lwp.h -->
# sources/distributed-fs/openafs/src/lwp/lwp.h

Purpose: public LWP and IOMGR interface header for non-kernel OpenAFS builds. It defines the cooperative lightweight process ABI when `AFS_PTHREAD_ENV` is not active and exposes fasttime, LWP scheduler, IOMGR select/sleep, and keyboard wait helpers.

Important APIs/types/functions: `PROCESS` is a pointer to `struct lwp_pcb`. The Unix PCB stores name, status, block flag, event list, wait counts, priority, stack memory, saved `lwp_context`, per-process rocks, IOMGR request pointer, and an index. The NT PCB uses a Windows fiber and a smaller state set. Public calls include `LWP_InitializeProcessSupport`, `LWP_CreateProcess`, `LWP_DestroyProcess`, `LWP_WaitProcess`, `LWP_INTERNALSIGNAL`, `LWP_QWait`, `LWP_QSignal`, `LWP_DispatchProcess`, `LWP_TerminateProcessSupport`, `LWP_CurrentProcess`, `LWP_ThreadId`, `savecontext`, and `returnto`. IOMGR entry points allocate fd sets and wrap select/poll/sleep/cancel.

Control flow: callers initialize LWP support, create runnable PCBs, wait on event addresses, signal events, and voluntarily dispatch. Context switching is delegated to platform C or assembly implementations declared here. The header also maps `LWP_SignalProcess` and `LWP_NoYieldSignal` to `LWP_INTERNALSIGNAL` on most platforms.

State and persistence: all state is process-memory only. Global `lwp_cpptr`, `lwp_debug`, stack sizing variables, overflow action, and `lwp_nextindex` are shared scheduler state. There is no disk persistence.

Dependencies/integration: depends on `afs/param.h`, platform select headers, `ucontext` or `setjmp`, Windows headers under NT, and LWP implementation files. It is consumed by LWP tests, IOMGR, lock tests, and legacy server code.

Risks and test signals: ABI and structure layout are architecture-sensitive, especially `lwp_context` and `lwp_pcb`. Stack-size constants encode historical platform behavior. Tests in `src/lwp/test` exercise process switching, event signaling, IOMGR select, and keyboard helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/lwp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/lwp_elf.h -->
# sources/distributed-fs/openafs/src/lwp/lwp_elf.h

Purpose: small assembler portability header that normalizes C symbol labels for ELF, SYSV, Sun, and underscore-prefixed platforms. Despite the file name, comments state it also serves a.out platforms.

Important APIs/types/functions: defines `_C_LABEL(name)` and `ENTRY(name)`. On ELF/SYSV/Sun these expand to plain labels. On older underscore platforms they prepend `_`, with token-pasting variants for ANSI C and pre-ANSI assemblers.

Control flow: no runtime control flow. Assembly files include it before declaring `savecontext`, `returnto`, `PRE_Block`, or abort-like symbols, so the same assembly source can target multiple symbol naming conventions.

State and persistence: no state and no persistence.

Dependencies/integration: included by `process.amd64.s`, `process.i386.s`, and related assembly context-switch implementations. It integrates build-time platform macros with assembler syntax.

Risks and test signals: breakage here causes link-time failures or wrong entry labels for all assembly context switchers. Validation is mostly compile/link coverage for each target architecture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/lwp_elf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/lwp_nt.c -->
# sources/distributed-fs/openafs/src/lwp/lwp_nt.c

Purpose: Windows NT implementation of the LWP scheduler using Windows fibers. It mirrors the Unix LWP API so the rest of OpenAFS can use one cooperative-process model.

Important APIs/types/functions: exports `LWP_InitializeProcessSupport`, `LWP_CreateProcess`, `LWP_DestroyProcess`, `LWP_QWait`, `LWP_QSignal`, `LWP_CurrentProcess`, `LWP_ThreadId`, `LWP_DispatchProcess`, `LWP_GetProcessPriority`, `LWP_INTERNALSIGNAL`, `LWP_TerminateProcessSupport`, and `LWP_WaitProcess`. Internal helpers include `Initialize_PCB`, `Enter_LWP`, `Dispatcher`, `Internal_Signal`, `purge_dead_pcbs`, `Delete_PCB`, `Free_PCB`, and circular queue operations. `runnable[MAX_PRIORITIES]` and `blocked` hold PCB queues.

Control flow: initialization converts the main thread to a fiber, creates the control block, initializes queues, and inserts the main PCB. New LWPs allocate a PCB, enforce minimum stack size, create a fiber, insert it by priority, then switch to it. Waiting moves the current PCB from runnable to blocked with event-list metadata. Signaling scans blocked PCBs for matching event pointers, decrements wait counts, and moves satisfied PCBs back to runnable. `Dispatcher` advances the current queue head, chooses the highest non-empty priority queue, updates `lwp_cpptr`, and calls `SwitchToFiber`.

State and persistence: process-local globals hold scheduler state, process count, current PCB, queues, stack-size metrics, and debug flags. No persistent storage is used.

Dependencies/integration: compiled only for `AFS_NT40_ENV`; uses Windows fiber APIs, `afs/opr.h`, `afs/afsutil.h`, and `lwp.h`. IOMGR uses `lwp_MaxStackSeen` and PCB `iomgrRequest` fields.

Risks and test signals: the Win95 compatibility stubs return null/no-op and would not provide real scheduling. `LWP_CreateProcess` switches to the new fiber before assigning `*pid`, which preserves old LWP behavior but makes caller assumptions delicate. Queue corruption and destroyed-PCB lifetime are main risks. LWP tests cover analogous API behavior but Windows-specific fiber paths need platform build/runtime testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/lwp_nt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/process.amd64.s -->
# sources/distributed-fs/openafs/src/lwp/process.amd64.s

Purpose: x86_64 assembly implementation of the LWP low-level context-switch primitives `savecontext` and `returnto`.

Important APIs/types/functions: exports `savecontext(int (*f)(), struct savearea *area1, char *newsp)` and `returnto(struct savearea *area2)`. The save area stores `topstack` at offset 0. It references global `PRE_Block` through GOT-relative addressing and uses `_C_LABEL`/`ENTRY` from `lwp_elf.h`.

Control flow: `savecontext` builds a normal frame, stores arguments in stack slots, sets `PRE_Block = 1`, pushes general registers, records the current stack pointer in the save area, optionally switches `%rsp` to `newsp`, and jumps to the supplied function. `returnto` restores `%rsp` from the target save area, pops registers in reverse order, clears `PRE_Block`, repairs the frame, and returns into the restored context.

State and persistence: only CPU register/stack state and `PRE_Block` are modified. No disk or heap state is touched.

Dependencies/integration: used by LWP scheduler on amd64 targets that select assembly switching instead of `process.c`/ucontext. It depends on exact AMD64 calling convention and frame layout.

Risks and test signals: stack alignment, callee-saved register coverage, and GOT use are critical. Any ABI drift can corrupt scheduler state. Compile/link tests verify labels; runtime LWP switching tests (`test`, `rw`, select tests) are the behavioral signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/process.amd64.s -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/process.c -->
# sources/distributed-fs/openafs/src/lwp/process.c

Purpose: C implementation of LWP context switching for platforms using `ucontext` or manipulable `setjmp` buffers instead of architecture assembly.

Important APIs/types/functions: exports `savecontext` and `returnto`. Under `USE_UCONTEXT && HAVE_UCONTEXT_H`, `savecontext` uses `getcontext`, `makecontext`, and `setcontext`; otherwise it uses `setjmp`, mutates the stack-pointer slot in `jmp_buf`, and returns through `longjmp`. Platform macros define `LWP_SP` and sometimes `LWP_FP`.

Control flow: `savecontext` sets `PRE_Block`, captures current context, stores a top-stack pointer, and either invokes the supplied entry point on the current stack or creates/switches to a new stack. The `setjmp` path uses a temporary jump buffer to install the new stack pointer and then calls the entry function. `returnto` clears `PRE_Block` and restores the saved context via `setcontext` or `longjmp`.

State and persistence: manipulates only process runtime state: saved context buffers, stack pointers, static helper globals (`EP`, `rc`, `jmpBuffer`), and `PRE_Block`. No persistent state.

Dependencies/integration: included by LWP scheduler implementations through `lwp.h`. Depends on `afs/param.h` platform macros, `roken.h`, `assert.h`, libc context APIs, and glibc pointer-mangling details for some old SPARC cases.

Risks and test signals: the `setjmp` path is highly libc- and architecture-dependent. Several Linux architectures are explicitly unsupported unless `LWP_SP` is known. Pointer mangling and frame-pointer updates can break across libc releases. Runtime process-switch tests are essential.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/process.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/process.default.s -->
# sources/distributed-fs/openafs/src/lwp/process.default.s

Purpose: legacy multi-architecture assembly context-switch implementation for LWP. It contains conditional implementations for ARM, RIOS/AIX, m68k, SPARC, IBM032, VAX, MIPS, HPUX, Alpha, and PowerPC.

Important APIs/types/functions: each architecture exports variants of `savecontext` and `returnto`, with platform-specific symbol names and register save areas. The common contract is storing a top-of-stack pointer in the save area, optionally switching to `newsp`, calling the supplied function, and later restoring saved registers/stack. Several blocks also set or clear global `PRE_Block`.

Control flow: all architecture blocks follow the same scheduler handoff: save callee/global registers and special registers as needed, store current stack pointer, switch stack if requested, branch to the target function, and restore on `returnto`. SPARC additionally flushes register windows; MIPS/Alpha save floating-point registers; HPUX delegates to `process.s.hpux`.

State and persistence: CPU register state and `PRE_Block` are the only persistent runtime effects. No heap or file persistence.

Dependencies/integration: selected by build macros from `afs/param.h`. It integrates with `lwp.h`'s `struct lwp_context` layout; for SPARC it relies on the larger `globals` area in the context structure.

Risks and test signals: high maintenance risk because many target ABIs are obsolete and hard to test. Register save completeness, stack-frame sizing, and symbol naming are the critical failure modes. The most useful signal is successful per-architecture build plus LWP runtime tests on that architecture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/process.default.s -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/process.i386.s -->
# sources/distributed-fs/openafs/src/lwp/process.i386.s

Purpose: i386 assembly implementation of `savecontext` and `returnto` for LWP stack/context switching.

Important APIs/types/functions: exports `_C_LABEL(savecontext)` and `_C_LABEL(returnto)`. `savecontext` receives `f`, `area1`, and `newsp` at standard i386 stack offsets. The save area stores `topstack` at offset 0.

Control flow: `savecontext` pushes a new frame, executes `pusha` to save registers, sets `PRE_Block`, writes `%esp` into the save area, optionally switches `%esp` to `newsp`, and jumps to the entry function. `returnto` restores `%esp` from the save area, executes `popa`, clears `PRE_Block`, restores `%ebp`, and returns.

State and persistence: only CPU stack/register state and global `PRE_Block` are modified. No file or heap persistence.

Dependencies/integration: includes `lwp_elf.h` for labels. It is consumed by the LWP scheduler on 32-bit x86 builds that use assembly context switching.

Risks and test signals: assumes classic i386 calling convention and `pusha`/`popa` availability. Stack alignment and signal/preemption interactions are sensitive. Behavioral validation comes from LWP process-switch, wait/signal, and IOMGR tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/process.i386.s -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/test/Makefile.in -->
# sources/distributed-fs/openafs/src/lwp/test/Makefile.in

Purpose: build rules for LWP test binaries.

Important APIs/types/functions: targets `test`, `selclient`, `selserver`, `test_key`, and `rw`. It compiles shared `selsubs.o` for select tests and links `rw` with `libopr.a` in addition to `liblwp.a`.

Control flow: normal make dependency graph. `all` builds every test. Clean removes objects, archives, binaries, and core files.

State and persistence: produces local test binaries and object files. No runtime state.

Dependencies/integration: includes OpenAFS config make fragments `Makefile.config` and `Makefile.lwp`, uses `AFS_LDRULE`, `XLIBS`, `DESTDIR` includes, `TOP_LIBDIR`, and `../liblwp.a`.

Risks and test signals: the test set is the main signal for LWP behavior. Missing `XLIBS` or `libopr.a` will break selected targets. The makefile itself has low logic risk but depends on generated config variables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/test/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/test/rw.c -->
# sources/distributed-fs/openafs/src/lwp/test/rw.c

Purpose: readers/writer stress test for LWP scheduling and OpenAFS lock primitives.

Important APIs/types/functions: defines an intrusive queue with an embedded `struct Lock`, helpers `init`, `empty`, `insert`, and `Remove`, and LWP entry points `read_process` and `write_process`. `main` initializes LWP, a shared queue, reader LWPs, and one writer LWP.

Control flow: readers start, dispatch once, then repeatedly take a read lock, wait on the queue event while empty, remove a message, and dispatch. The writer takes a write lock, inserts fixed messages, releases the lock, and signals the queue event. `main` spins dispatching until all readers plus writer are asleep, then destroys LWPs and terminates support.

State and persistence: all state is in process memory: shared queue `q`, lock state, `asleep`, reader IDs, and LWP PCBs. No disk state.

Dependencies/integration: includes `lwp.h` and `afs/afs_lock.h`, linking with `liblwp` and `libopr`. It exercises LWP wait/signal plus lock read/write paths.

Risks and test signals: it intentionally demonstrates concurrent cooperative access but has simplistic queue locking, fixed messages, and busy delay loops. Success is visible through orderly message printing and clean process termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/test/rw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/test/selclient.c -->
# sources/distributed-fs/openafs/src/lwp/test/selclient.c

Purpose: client-side IOMGR select test, especially for read/write/exception fd sets with descriptors above 31 and TCP out-of-band behavior.

Important APIs/types/functions: parses options `-fd`, `-oob`, `-soob`, `-delay`, `-end`, and `-write`. Uses `sendTest` for write/echo verification and `sendEnd` to request server termination. Uses helpers from `selsubs.c` and protocol structure from `seltest.h`.

Control flow: `main` opens enough dummy descriptors to force the socket to a requested number, connects to the server, and either sends an end command, sends OOB data, or initializes IOMGR and runs `sendTest`. `sendTest` sends an `SC_WRITE` command, writes a deterministic byte pattern, optionally one byte at a time through `IOMGR_Select` on writable/exception sets, reads the echo, and compares buffers.

State and persistence: uses transient socket state, allocated buffers, and optional signal count `nSigIO`. No persistent files.

Dependencies/integration: depends on sockets, `IOMGR_Initialize`, `IOMGR_Select`, `IOMGR_AllocFDSet`, and common select-test helpers.

Risks and test signals: assumes blocking socket behavior and timing appropriate to the host/network; loopback may require longer delays. Assertions validate fd set cleanup, write progress, and echoed data integrity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/test/selclient.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/test/selserver.c -->
# sources/distributed-fs/openafs/src/lwp/test/selserver.c

Purpose: server-side IOMGR select test for high-numbered fds, connection handling, read/write readiness, and exception/OOB fd sets.

Important APIs/types/functions: defines `clientHandle_t` pool entries with fd sets and LWP process IDs. `getClientHandle` reserves a pool slot. `handleRequest` waits for an accepted connection signal and processes commands. `handleWrite` reads client data with `IOMGR_Select` and echoes it back.

Control flow: `main` initializes IOMGR and a pool of LWP handler threads, creates/listens on a socket, then selects for accept readiness and exceptions. Accepted sockets are stored in a free client handle and signaled to the corresponding LWP. Handler LWPs wait on `ch_state`, select on their socket, read a `selcmd_t`, branch on `SC_PROBE`, `SC_WRITE`, or `SC_END`, and return the handle to the pool.

State and persistence: in-memory pool `clientHandles`, `nThreads`, socket fds, and fd sets. No disk persistence.

Dependencies/integration: uses LWP process creation/signaling, IOMGR fd-set allocation and select, and `selsubs` helpers.

Risks and test signals: the condition `while (nThreads > MAX_THREADS)` appears off by one for a full pool and may not throttle at exactly `MAX_THREADS`; `nThreads` is cooperative-thread shared. Assertions check fd-set cleanup and read/write results. A successful client roundtrip validates IOMGR readiness paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/test/selserver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/test/selsubs.c -->
# sources/distributed-fs/openafs/src/lwp/test/selsubs.c

Purpose: shared utility functions for the select client/server tests.

Important APIs/types/functions: `sendOOB` and `recvOOB` send/receive one byte with `MSG_OOB`; `assertNullFDSet` clears one expected fd then asserts the rest of the fd set storage is zero; `OpenFDs` opens `/dev/null` until a requested fd threshold is reached; `Die` reports errors and exits or aborts; `Log` prints timestamped messages with current LWP process pointer.

Control flow: helpers are synchronous. `Log` calls `LWP_CurrentProcess`, so it expects LWP support to be initialized in normal use.

State and persistence: no persistent state; may leave dummy `/dev/null` descriptors open to influence subsequent socket fd allocation.

Dependencies/integration: depends on socket APIs, `lwp.h`, `seltest.h`, and IOMGR tests. `assertNullFDSet` assumes fd_set can be interpreted as an array of `int`.

Risks and test signals: fd_set layout assumptions are non-portable but intentional for this low-level test. `OpenFDs` relies on descriptor allocation order. Test failures generally surface as assertions or aborts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/test/selsubs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/test/seltest.h -->
# sources/distributed-fs/openafs/src/lwp/test/seltest.h

Purpose: shared protocol and helper declarations for LWP IOMGR select tests.

Important APIs/types/functions: defines `selcmd_t` with command, delay, flags, and info fields. Commands are `SC_PROBE`, `SC_WRITE`, and `SC_END`; flags include `SC_WAIT_ONLY` and `SC_WAIT_OOB`. It defines data marker range constants and declares helpers from `selsubs.c`.

Control flow: no runtime control flow. It shapes the client/server command contract.

State and persistence: no state or persistence.

Dependencies/integration: used by `selclient.c`, `selserver.c`, and `selsubs.c`. Under `NEEDS_ALLOCFDSET` it declares IOMGR fd-set allocation functions for compatibility testing.

Risks and test signals: structure layout is sent directly over TCP without byte-order conversion, so tests assume same-endian compatible client/server. Protocol constants are small and stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/test/seltest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/test/test.c -->
# sources/distributed-fs/openafs/src/lwp/test/test.c

Purpose: microbenchmark for LWP wait/signal cost.

Important APIs/types/functions: `OtherProcess` continuously signals a static `semaphore`. `main` initializes LWP, creates `OtherProcess`, waits on the semaphore a requested number of times, and reports elapsed time.

Control flow: the worker LWP loops forever calling `LWP_SignalProcess`. The main process loops `count` times through `LWP_WaitProcess`, relying on cooperative dispatch and event signaling to bounce between LWPs.

State and persistence: static in-memory `semaphore`, LWP PCBs, and timing variables. No persistence.

Dependencies/integration: depends on `lwp.h`, `gettimeofday`, and assertions. It is built by the LWP test makefile.

Risks and test signals: argument validation is absent; `argv[1]` must exist and be a positive count. It is primarily a performance and smoke signal for LWP event dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/test/test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/test/test_key.c -->
# sources/distributed-fs/openafs/src/lwp/test/test_key.c

Purpose: interactive test for `LWP_WaitForKeystroke`, `LWP_GetResponseKey`, and `LWP_GetLine`.

Important APIs/types/functions: command options include `-nobuf`, `-delay`, `-iters`, `-inter`, and `-line`. `DotWriter` waits on `waitingForAnswer` and prints dots through `PrintDots` while keyboard waits are active. `interTest` beeps every five seconds until a key arrives; `lineTest` waits for a whole line.

Control flow: `main` initializes IOMGR, creates `DotWriter`, chooses interactive mode, signals the dot writer, and calls the keyboard helper under test. In delayed mode, it repeats waits and flushes pending input after a key is available.

State and persistence: process-local flag `waitingForAnswer`, stdin buffering mode, and console output. No persistent data.

Dependencies/integration: includes `lwp.h`; uses IOMGR sleep/select behavior and keyboard wrappers from `waitkey.c`.

Risks and test signals: interactive tests are hard to automate and platform terminal buffering affects behavior. Success is user-visible: dots continue while waiting, timeouts report no data, and entered keys/lines are returned.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/test/test_key.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/threadname.c -->
# sources/distributed-fs/openafs/src/lwp/threadname.c

Purpose: legacy thread-name registry used by server logging, supporting both pthread and LWP process identifiers.

Important APIs/types/functions: `threadname` returns the registered name for the current thread/LWP or `"main"`. `registerthread` stores or updates a mapping from thread ID to name. `swapthreadname` replaces a registered name and optionally returns the old name.

Control flow: each lookup scans the fixed arrays linearly. Registration updates an existing slot or appends a new one until `MAX_THREADS`.

State and persistence: global arrays `ThreadId` and `ThreadName`, plus `nThreads`. No locking is present in this file, and no state persists outside the process.

Dependencies/integration: uses `pthread_self` under `AFS_PTHREAD_ENV`; otherwise uses `LWP_ThreadId`. This is separate from `opr/threadname.c`, which sets OS thread names.

Risks and test signals: fixed capacity of 128, global mutable state, no synchronization, and truncation to 63 characters. Tests are indirect through logging behavior in server/LWP code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/threadname.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/timer.c -->
# sources/distributed-fs/openafs/src/lwp/timer.c

Purpose: timer-list implementation used by LWP/IOMGR code for scheduling timeout events.

Important APIs/types/functions: exports `TM_Init`, `TM_Final`, `TM_Insert`, `TM_Rescan`, `TM_GetExpired`, `TM_GetEarliest`, `TM_eql`, `openafs_insque`, and `openafs_remque`. Internal helpers `subtract`, `add`, and `blocking` manage `timeval` arithmetic and infinite timeout detection.

Control flow: `TM_Init` initializes fasttime once and creates a circular sentinel. `TM_Insert` sets `TimeLeft`, treats negative times as blocking/infinite, computes absolute expiration for finite timers, and inserts by remaining time order. `TM_Rescan` refreshes each finite timer's `TimeLeft` from current time and counts expired entries. `TM_GetExpired` returns the first expired finite timer; `TM_GetEarliest` returns the head's first element.

State and persistence: timer lists are caller-owned circular in-memory lists. `globalInitDone` prevents repeated fasttime init. No persistence.

Dependencies/integration: depends on `FT_Init` and `FT_AGetTimeOfDay` from fasttime, `timer.h`, and `lwp.h`. IOMGR is the likely consumer.

Risks and test signals: list ordering compares original `TimeLeft` values while storing absolute expiration, so callers must rescan before relying on current state. Negative `timeval` fields mean blocking. Tests should cover insertion, rescan, expiration, infinite timers, and list removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/timer.h -->
# sources/distributed-fs/openafs/src/lwp/timer.h

Purpose: public timer-list data structure and API declarations for LWP timers.

Important APIs/types/functions: `struct TM_Elem` contains circular list links, caller-provided `TotalTime`, package-filled `TimeLeft`, and caller-owned `BackPointer`. Declares `TM_Init`, `TM_Final`, `TM_Rescan`, `TM_Insert`, `TM_GetExpired`, `TM_GetEarliest`, `TM_eql`, `openafs_insque`, and `openafs_remque`. Defines `FOR_ALL_ELTS` circular-list scanner.

Control flow: no runtime logic beyond macros. `TM_Remove` maps to `openafs_remque`; `Tm_Insert` appears to be a compatibility macro using raw insertion when `_TIMER_IMPL_` is not defined.

State and persistence: no header-owned state.

Dependencies/integration: requires `struct timeval` to be visible from includers. Used by `timer.c` and LWP/IOMGR timeout handling.

Risks and test signals: macro names are historically inconsistent (`Tm_Insert` vs `TM_Insert`), and intrusive list use requires callers not to remove unlinked elements. Compile coverage and timer behavior tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/timer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/waitkey.c -->
# sources/distributed-fs/openafs/src/lwp/waitkey.c

Purpose: cross-platform keyboard-input wait helpers for LWP tools and tests.

Important APIs/types/functions: exports `LWP_WaitForKeystroke`, `LWP_GetLine`, and `LWP_GetResponseKey`. The NT implementation uses `_kbhit`, `getch/getche`, and either `Sleep` or `IOMGR_Select`; the Unix implementation inspects stdio buffers then uses `select` or `IOMGR_Select`.

Control flow: `LWP_WaitForKeystroke` returns immediately if buffered data exists, waits indefinitely for negative seconds, polls for zero seconds, or waits up to the timeout. `LWP_GetLine` waits for input then reads a full line, with NT manually handling carriage return and backspace. `LWP_GetResponseKey` flushes stdin, waits, then reads one character if available.

State and persistence: only stdin buffering and transient timeout state. No persistent storage.

Dependencies/integration: depends on platform stdio internals (`__fbufsize`, `_IO_read_ptr`, BSD `_bf`, or `_cnt`) where available; uses IOMGR unless pthread mode is selected.

Risks and test signals: direct access to libc `FILE` internals is fragile across libc versions. `fflush(stdin)` is non-portable but used historically. `test_key` is the direct behavioral test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/lwp/waitkey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/mkdest.pl -->
# sources/distributed-fs/openafs/src/mkdest.pl

Purpose: interactive Perl helper for creating an AFS platform build tree with symlinks back to the source tree.

Important APIs/types/functions: top-level script asks for confirmation, creates `dest` and `obj`, and recursively processes source directories through `dodir`. `lastcomp` derives a source component relative to `$srcdir`.

Control flow: after user confirms `y`, it creates build directories, enters `obj`, then `dodir` traverses `$srcdir`. For each directory it creates `DEST` and `SRC` symlinks, symlinks non-directory files to `SRC/<name>`, skips `.`/`..`/`RCS`, creates matching subdirectories, and recurses.

State and persistence: creates filesystem directories and symbolic links in the current working directory. Does not modify source files.

Dependencies/integration: uses Perl built-ins and shell `ln -s` through `system`. It assumes `$ENV{PWD}` reflects the target platform tree.

Risks and test signals: unquoted `system` strings and simplistic path parsing can misbehave with spaces or shell metacharacters. It is interactive and old-style Perl. Correct output is a mirrored object tree with `SRC` and `DEST` links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/mkdest.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/Makefile.in -->
# sources/distributed-fs/openafs/src/opr/Makefile.in

Purpose: build/install rules for OpenAFS portable runtime (`opr`) library and exported headers.

Important APIs/types/functions: builds libtool objects for assert, cache, string case helpers, dict, fmt, proc, rbtree, softsig, threadname, and uuid. Produces `liboafs_opr.la`, static `libopr.a`, PIC archive, and installed headers under `afs/` and `opr/`.

Control flow: `all` installs headers into the top include directory and builds libraries. Header targets copy source headers to canonical public names, including `opr_lock.h` to `opr/lock.h` and `opr_time.h` to `opr/time.h`. `install`, `dest`, and `buildtools` provide build-system integration.

State and persistence: creates build artifacts, installed libraries, and copied headers.

Dependencies/integration: includes OpenAFS config make fragments for pthreads and libtool. Links with hcrypto and roken libraries.

Risks and test signals: installed header names are part of the public contract. Missing copy targets break downstream includes. Build and link coverage are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/assert.c -->
# sources/distributed-fs/openafs/src/opr/assert.c

Purpose: assertion failure implementation for OPR.

Important APIs/types/functions: `opr_AssertionFailed(file, line)` formats current local time, prints an assertion failure message to stderr, flushes, and calls `opr_abort`. On NT, `opr_NTAbort` triggers `DebugBreak`.

Control flow: assertion macros in `opr.h` call this function when expressions fail. It does not return.

State and persistence: no persistent state; writes diagnostic output to stderr.

Dependencies/integration: depends on `opr.h`, time functions, stderr, and platform abort handling. Used by `opr_Assert` and `opr_Verify` across OPR and other OpenAFS code.

Risks and test signals: `localtime_r` and `strftime` are used during failure handling; if unavailable or broken, diagnostics may fail. Tests are normally assertion-trigger smoke tests or indirect failure output checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/assert.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/cache.c -->
# sources/distributed-fs/openafs/src/opr/cache.c

Purpose: simple thread-safe in-memory cache for flat binary keys and values.

Important APIs/types/functions: public `opr_cache_init`, `opr_cache_free`, `opr_cache_get`, and `opr_cache_put`; structures `opr_cache` and `cache_entry`. Internal functions include `free_entry_contents`, `evict_entry`, `alloc_entry`, `find_entry`, `memdup`, `isPowerOf2`, and `nextPowerOf2`.

Control flow: initialization validates bucket/entry bounds, rounds bucket count up to a power of two, initializes a mutex, and creates an `opr_dict`. `put` duplicates key/value, locks, finds or allocates an entry, and replaces the value. If full, allocation evicts a random bucket's least-recently-used entry. `get` locks, finds and promotes the entry in its bucket, checks output buffer capacity, and copies bytes. Free scans every bucket and frees entries.

State and persistence: cache state is heap memory protected by `opr_mutex_t`; entries are held in dictionary buckets using intrusive queues. No persistence.

Dependencies/integration: uses `opr/dict.h`, `opr/queue.h`, Jenkins hash from `opr/jhash.h`, and either pthread locks or `lockstub.h` for LWP/non-pthread builds.

Risks and test signals: `rand()` is used without seeding/control. `get` assumes `a_val_len` is valid and `val_buf` has the specified size. Null cache acts as empty. Tests should cover invalid options, duplicate puts, ENOSPC gets, eviction, and threaded access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/casestrcpy.c -->
# sources/distributed-fs/openafs/src/opr/casestrcpy.c

Purpose: small string utilities for case conversion and bounded string composition.

Important APIs/types/functions: `lcstring` copies lowercased text with forced NUL termination; `ucstring` copies uppercased text; `stolower` lowercases a string in place; `strcompose` concatenates a NULL-terminated varargs list into a bounded buffer.

Control flow: conversion helpers copy until `n` bytes or source NUL. `strcompose` starts with an empty buffer, tracks remaining capacity, and returns NULL if any component would exceed the buffer.

State and persistence: caller-provided buffers only; no global or persistent state.

Dependencies/integration: exposed through macro-renamed names in `afs/opr.h` (`opr_lcstring`, etc.). Uses ctype and string functions.

Risks and test signals: ctype functions receive `char` values directly; negative signed chars can be undefined outside ASCII. `strcompose` returns without `va_end` on early overflow, which is a cleanup correctness issue. Unit tests should cover exact buffer limits and case conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/casestrcpy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/dict.c -->
# sources/distributed-fs/openafs/src/opr/dict.c

Purpose: allocation/free implementation for a simple hash-bucket dictionary backed by `opr_queue` chains.

Important APIs/types/functions: `opr_dict_Init(size)` allocates `struct opr_dict`, validates that size is a power of two, allocates a table of queue heads, and initializes each. `opr_dict_Free` frees the table and dictionary and nulls the caller pointer.

Control flow: no lookup logic lives here; bucket insertion, scanning, and promotion are static inline helpers in `dict.h`.

State and persistence: heap-allocated dictionary table only. No persistence and no element ownership beyond bucket heads.

Dependencies/integration: includes `dict.h`, which depends on `opr/queue.h`. Used by `opr_cache`.

Risks and test signals: callers must free or detach all elements before `opr_dict_Free`. Non-power-of-two sizes fail. Tests should validate init failure for invalid sizes and bucket initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/dict.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/dict.h -->
# sources/distributed-fs/openafs/src/opr/dict.h

Purpose: dictionary structure and inline helpers for queue-backed hash buckets.

Important APIs/types/functions: `struct opr_dict` stores `size` and `table`. Inline helpers `opr_dict_Prepend`, `opr_dict_Append`, and `opr_dict_Promote` map an integer hash to `index & (size - 1)`. Macros `opr_dict_ScanBucket` and `opr_dict_ScanBucketSafe` expose bucket iteration. Declares init/free functions.

Control flow: no standalone runtime flow; helpers perform intrusive queue operations.

State and persistence: no header-owned state. The dictionary does not own user entries.

Dependencies/integration: requires `opr/queue.h` and power-of-two `size` from `opr_dict_Init`. Used by cache and any other small hashed collections.

Risks and test signals: direct masking requires power-of-two sizes. No locking is provided. Caller must avoid using freed or unlinked queue nodes. Cache tests indirectly validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/dict.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/ffs.h -->
# sources/distributed-fs/openafs/src/opr/ffs.h

Purpose: portable fallback implementations for finding first and last set bits in a 32-bit integer.

Important APIs/types/functions: `opr_ffs(int value)` returns one-based index of the least significant set bit or 0. `opr_fls(int value)` returns one-based index of the most significant set bit or 0.

Control flow: each function casts to unsigned 32-bit to avoid signed-shift undefined behavior, then loops until a set bit is found.

State and persistence: no state.

Dependencies/integration: depends on OpenAFS integer typedefs being visible. Installed as `opr/ffs.h`.

Risks and test signals: assumes 32-bit `afs_uint32` semantics and returns positions in the BSD convention. Unit tests should cover 0, powers of two, negative `int`, and all-bits-set values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/ffs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/fmt.c -->
# sources/distributed-fs/openafs/src/opr/fmt.c

Purpose: callback-driven percent-escape formatter with snprintf-like truncation semantics.

Important APIs/types/functions: `opr_fmt` is public. Internal `opr_fmt_ctx_priv_s` tracks input pointer, output pointer, remaining output bytes, and bytes written. `opr_fmt_cb` emits a character and counts it. `opr_fmt_internal` scans the format string and dispatches escape characters through a 256-entry formatter table.

Control flow: ordinary characters are copied. After `%`, the next byte indexes `ctx->fmtrs`; callbacks return 0 to finish escape processing, 1 to remain in escape mode, or -1 to abort. Unknown escapes emit the escape byte literally. The implementation always emits a terminating NUL during successful formatting and returns the number of bytes that would have been written excluding NUL.

State and persistence: state is stack-local per call and caller-provided output buffer. No global state.

Dependencies/integration: includes `fmt.h` and `afs/opr.h` for assertions. Used by code needing custom lightweight formatting.

Risks and test signals: if `n` is 0, the termination logic can write `out[-1]` when `ret >= n`; callers should pass positive sizes. Formatter callbacks consume a shared `va_list`, so callback conventions must match. Unit tests should cover truncation, unknown escapes, multi-step callbacks, and callback failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/fmt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/fmt.h -->
# sources/distributed-fs/openafs/src/opr/fmt.h

Purpose: public interface for the OPR callback formatter.

Important APIs/types/functions: forward-declares `opr_fmt_ctx_priv` and `opr_fmt_ctx`, defines `opr_fmtr` callback type, and defines `struct opr_fmt_ctx_s` with formatter table, user data, output callback, and private implementation pointer. Declares `opr_fmt`.

Control flow: no runtime logic. Callback users write output through `ctx->put`.

State and persistence: no header-owned state.

Dependencies/integration: depends on `va_list` being visible to includers. Installed as `opr/fmt.h`.

Risks and test signals: the formatter table must have 256 entries indexed by unsigned char values. Callback implementations must not assume `priv` layout. Compile-time integration tests catch missing `stdarg.h` context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/fmt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/jhash.h -->
# sources/distributed-fs/openafs/src/opr/jhash.h

Purpose: OpenAFS wrapper around Bob Jenkins lookup3 hash routines for integers and opaque byte buffers.

Important APIs/types/functions: macros `opr_jhash_size`, `opr_jhash_mask`, `opr_jhash_rot`, `opr_jhash_mix`, and `opr_jhash_final`; inline functions `opr_jhash`, `opr_jhash_int`, `opr_jhash_int2`, and `opr_jhash_opaque`.

Control flow: hash functions initialize Jenkins state, process input in 12-byte or three-word blocks, then use switch fallthrough to mix trailing input. Opaque hashing reads bytes little-endian into 32-bit accumulators.

State and persistence: pure functions with no global state.

Dependencies/integration: uses OpenAFS integer typedefs and `AFS_FALLTHROUGH`. `opr_cache` uses `opr_jhash_opaque` for keys; `uuid.c` uses it for UUID hashes.

Risks and test signals: not cryptographic. `opr_jhash` expects word-aligned `afs_uint32` input if the platform requires alignment; use `opr_jhash_opaque` for arbitrary buffers. Regression tests should use fixed vectors for stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/jhash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/lockstub.h -->
# sources/distributed-fs/openafs/src/opr/lockstub.h

Purpose: no-op lock and condition-variable facade for non-pthread/LWP builds.

Important APIs/types/functions: typedefs `opr_mutex_t` and `opr_cv_t` as `int`; defines mutex and CV operations as no-ops, with `opr_mutex_tryenter` returning success.

Control flow: no runtime logic. It intentionally disables synchronization in code that is only cooperatively scheduled or single-threaded.

State and persistence: no state.

Dependencies/integration: hard-errors if included under `AFS_PTHREAD_ENV`. Used by `opr_cache.c` when pthreads are not active.

Risks and test signals: including this in real pthreaded code would create data races, so the preprocessor guard is critical. Build configuration tests should ensure pthread builds include `opr/lock.h` instead.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/lockstub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/opr.h -->
# sources/distributed-fs/openafs/src/opr/opr.h

Purpose: main public OPR header aggregating common macros, assertions, string helpers, thread-name API, and cache API.

Important APIs/types/functions: defines `opr_containerof`, stringization macros, `opr_abort`, `opr_min`, `opr_max`, `opr_Assert`, `opr_Verify`, and `opr_StaticAssert`. Declares `opr_AssertionFailed`, case-string helpers, `opr_threadname_set`, `struct opr_cache_opts`, opaque `struct opr_cache`, and cache operations.

Control flow: assertion macros call `opr_AssertionFailed` when expressions fail; `opr_Verify` guarantees expression evaluation. In non-pthread/NT contexts `opr_threadname_set` is inline no-op.

State and persistence: no header-owned state. Cache state is owned by cache implementation.

Dependencies/integration: installed as `afs/opr.h` and included widely across OpenAFS. It bridges OPR implementation files and callers.

Risks and test signals: macros evaluate operands multiple times for `opr_min`/`opr_max`. Assertions may be used in paths where abort behavior matters. Compile coverage across C dialects and platforms is important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/opr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/opr_assert.h -->
# sources/distributed-fs/openafs/src/opr/opr_assert.h

Purpose: compatibility header that redefines the standard `assert` macro to use OpenAFS `opr_Assert`.

Important APIs/types/functions: includes `afs/opr.h` and defines `assert(ex)` as `opr_Assert(ex)`.

Control flow: no runtime logic beyond assertion macro expansion.

State and persistence: no state.

Dependencies/integration: used by code that wants standard-looking `assert` calls but OPR failure behavior and formatting.

Risks and test signals: it overrides `assert` regardless of prior definitions, so include order can matter. Compile and assertion-failure tests validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/opr_assert.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/opr_lock.h -->
# sources/distributed-fs/openafs/src/opr/opr_lock.h

Purpose: pthread-backed mutex and condition-variable wrapper API for OPR.

Important APIs/types/functions: typedefs `opr_mutex_t` as `pthread_mutex_t` and `opr_cv_t` as `pthread_cond_t`. Defines init/destroy/enter/exit/tryenter macros and CV init/destroy/wait/timedwait/signal/broadcast wrappers. With `OPR_DEBUG_LOCKS`, mutexes use `PTHREAD_MUTEX_ERRORCHECK` and `opr_mutex_assert` verifies ownership via `EDEADLK`.

Control flow: most operations call pthread functions and verify success with `opr_Verify`; timed wait allows success or `ETIMEDOUT` and returns the code.

State and persistence: synchronization objects are caller-owned memory. No persistence.

Dependencies/integration: includes pthreads, errno, and `afs/opr.h`. Installed as `opr/lock.h` and used by pthreaded OPR code, including cache.

Risks and test signals: macros abort on unexpected pthread errors, so callers cannot recover from misuse. Debug ownership assert temporarily locks error-check mutexes. Threaded unit tests should cover lock lifecycle and timed wait.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/opr_lock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/opr_time.h -->
# sources/distributed-fs/openafs/src/opr/opr_time.h

Purpose: inline utility API for `struct afs_time64`, a signed 64-bit timestamp/duration in 100ns ticks.

Important APIs/types/functions: defines tick conversion constants and representable bounds. Provides compare helpers (`opr_time64_cmp`, relational/equality wrappers), checked addition, conversions from ticks, seconds, microseconds, and timeval-like sec/usec pairs, conversions back to ticks/seconds, uint32 wrapping conversion, and userland `opr_time64_now_safe`/`opr_time64_now`.

Control flow: checked constructors validate range before multiplying to ticks. `opr_time64_add_safe` checks overflow based on operand signs. `opr_time64_now_safe` reads `gettimeofday` and converts to ticks; on impossible `gettimeofday` failure it aborts.

State and persistence: pure value operations; no persistent state.

Dependencies/integration: requires `struct afs_time64` typedef from OpenAFS headers, `afs/opr.h`, and either kernel includes or userland time/errno headers. Installed as `opr/time.h`.

Risks and test signals: unchecked constructors assert on invalid input and should not be used with untrusted data. Microsecond value is not normalized in `fromTimeval_safe`; very large usec can overflow independently. Unit tests should cover bounds, overflow, negative values, and wrapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/opr_time.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/proc.c -->
# sources/distributed-fs/openafs/src/opr/proc.c

Purpose: process-size reporting helper.

Important APIs/types/functions: `opr_procsize()` returns an approximate process size in kilobytes. On NT it returns -1. Where `struct rusage` has `ru_idrss`, it uses `getrusage`; otherwise it approximates with `sbrk(0) >> 10`.

Control flow: simple platform conditional selection.

State and persistence: reads process resource/heap state only. No persistence.

Dependencies/integration: includes unistd and optionally sys/resource. Declared by `opr/proc.h`.

Risks and test signals: metric semantics differ by platform and can be unavailable. It is useful only for relative logging on the same host. Tests should tolerate -1 and platform variation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/proc.h -->
# sources/distributed-fs/openafs/src/opr/proc.h

Purpose: public declaration for OPR process information utilities.

Important APIs/types/functions: declares `afs_int32 opr_procsize(void)`.

Control flow: no runtime logic.

State and persistence: no state.

Dependencies/integration: requires `afs_int32` typedef visible from includers. Installed as `opr/proc.h`.

Risks and test signals: low-risk declaration header; compile coverage verifies correct include context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/proc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/queue.h -->
# sources/distributed-fs/openafs/src/opr/queue.h

Purpose: generic intrusive doubly-linked circular queue implementation.

Important APIs/types/functions: `struct opr_queue` embeds next/prev links. Provides scan macros, init/zero/add/remove operations, append/prepend/insert, emptiness/on-queue checks, count, swap, split, splice, and container macros (`opr_queue_Entry`, `First`, `Last`, `Next`, `Prev`).

Control flow: all operations are inline pointer rewrites. Split/splice transfer ranges between circular queues and reinitialize sources as appropriate.

State and persistence: queue state is embedded in caller-owned objects. No allocation or persistence.

Dependencies/integration: used by `opr_dict`, `opr_cache`, and any code needing multi-queue membership. In kernel builds it avoids stdlib.

Risks and test signals: intrusive queues require each object to have separate link fields for separate queues. Removing an unlinked element or double insertion corrupts pointers. Tests should cover empty/single/multiple elements, safe scans with removal, split/splice, and swap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/rbtree.c -->
# sources/distributed-fs/openafs/src/opr/rbtree.c

Purpose: function-based red/black tree implementation with parent pointers and NULL leaves.

Important APIs/types/functions: exports `opr_rbtree_init`, `opr_rbtree_first`, `opr_rbtree_last`, `opr_rbtree_next`, `opr_rbtree_prev`, `opr_rbtree_insert`, `opr_rbtree_remove`, and `opr_rbtree_replace`. Internal helpers include `update_parent_ptr`, rotations, `swapnode`, `insert_recolour`, and `remove_recolour`.

Control flow: callers perform their own key search and pass the parent/child slot to `opr_rbtree_insert`; the implementation links the node red and recolors/rotates. Removal handles leaf, two-child, and one-child cases, using successor replacement for two-child nodes and recoloring when a black node is removed. Iteration finds min/max and successor/predecessor via child and parent traversal.

State and persistence: tree/node links and color bits are embedded in caller-owned objects. No allocation or persistence.

Dependencies/integration: includes `rbtree.h` and platform config. Intended as a reusable primitive.

Risks and test signals: no comparator is embedded, so caller search correctness is essential. `remove_recolour` assumes sibling nodes exist in cases where red/black invariants require them. Tests should validate ordering, insert/remove permutations, replacement, and invariants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/rbtree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/rbtree.h -->
# sources/distributed-fs/openafs/src/opr/rbtree.h

Purpose: public node/tree structures and function declarations for OPR red/black trees.

Important APIs/types/functions: `struct opr_rbtree_node` has left, right, parent, and red fields. `struct opr_rbtree` stores root. Declares traversal, insert, remove, and replace functions.

Control flow: no runtime logic in the header.

State and persistence: state is caller-owned embedded tree nodes.

Dependencies/integration: used with `rbtree.c`; callers must provide search/comparison logic around it.

Risks and test signals: because there is no type-safe container macro here, callers must manage embedding and key comparisons carefully. Compile and invariant tests cover integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/rbtree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/softsig.c -->
# sources/distributed-fs/openafs/src/opr/softsig.c

Purpose: pthread-compatible signal handling system that routes allowed signals to normal handler functions in a dedicated thread, avoiding async-signal-safety constraints.

Important APIs/types/functions: public `opr_softsig_Init` and `opr_softsig_Register`. Internal `softsigSignalSet` builds the managed signal set, `signalHandler` loops on `sigwait`, `ExitHandler` restores default-style termination by unblocking and raising the signal, and `StopHandler` sends `SIGSTOP`.

Control flow: initialization blocks managed signals in the calling thread before other threads are created, registers default handlers for INT/TERM/QUIT/TSTP/FPE, starts and detaches the handler thread. Registration validates that the signal is in the managed set and stores the handler. The handler thread waits synchronously for signals and invokes registered callbacks.

State and persistence: process-local static `handlers[NSIG]`. No persistence.

Dependencies/integration: requires pthreads, signal APIs, and `opr_Verify`. Exposed by `softsig.h`.

Risks and test signals: must be called before creating other threads so signal masks are inherited. Handler table updates are not locked. Fatal synchronous signals such as SEGV and BUS are deliberately excluded. Tests should send handled signals and verify callback/default behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/softsig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/softsig.h -->
# sources/distributed-fs/openafs/src/opr/softsig.h

Purpose: public API for OPR soft signal handling.

Important APIs/types/functions: declares `opr_softsig_Init` and `opr_softsig_Register`. On NT includes `afs/procmgmt_softsig.h` for platform-specific support.

Control flow: no runtime logic.

State and persistence: no header-owned state.

Dependencies/integration: included by pthreaded applications wanting centralized signal handling.

Risks and test signals: low-risk declaration header; behavior risk resides in `softsig.c`. Compile coverage validates platform includes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/softsig.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/threadname.c -->
# sources/distributed-fs/openafs/src/opr/threadname.c

Purpose: sets the operating-system-visible name for the current pthread where supported.

Important APIs/types/functions: `opr_threadname_set(const char *threadname)` chooses among platform variants of `pthread_set_name_np`/`pthread_setname_np` based on configure macros and expected argument count.

Control flow: compiled only for pthread, non-NT builds. If no supported pthread naming function is detected, the function body effectively does nothing.

State and persistence: thread name is stored by the OS/thread library; no OpenAFS global state.

Dependencies/integration: public inline/no-op declaration is in `afs/opr.h`; this file provides the real implementation under pthread builds. Includes optional `pthread_np.h`.

Risks and test signals: platform APIs differ in name length limits and argument order; configure macros must be accurate. Tests can verify thread names through debugger/procfs where available, but compile coverage is the primary signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/threadname.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/uuid.c -->
# sources/distributed-fs/openafs/src/opr/uuid.c

Purpose: UUID creation, comparison, hashing, string conversion, parsing, and packed/unpacked conversion.

Important APIs/types/functions: exports `opr_uuid_create`, `opr_uuid_isNil`, `opr_uuid_equal`, `opr_uuid_hash`, userland `opr_uuid_toString`, `opr_uuid_freeString`, `opr_uuid_fromString`, plus `opr_uuid_pack` and `opr_uuid_unpack`.

Control flow: creation uses Windows `UuidCreate`, platform `uuid_generate`, or random bytes from hcrypto with version/variant bits set. Equality and nil checks use `memcmp`. String conversion formats canonical hex groups; parsing accepts canonical format and an older AFS grouping. Pack/unpack converts structured fields with network byte order for multi-byte components.

State and persistence: no global mutable state except constant nil UUID. UUID values are caller-owned. No persistence.

Dependencies/integration: depends on hcrypto random, optional libuuid, Windows RPC, Jenkins hash, and network byte-order helpers. Exposed by `uuid.h`.

Risks and test signals: fallback random path must have reliable `RAND_bytes`; return value is ignored. `sscanf` parsing with `%02x` accepts variable-width hex in C semantics, so strict validation may be weaker than expected. Tests should cover nil, equality, roundtrip string parse, old AFS parse format, and pack/unpack byte order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/uuid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/uuid.h -->
# sources/distributed-fs/openafs/src/opr/uuid.h

Purpose: public UUID data structures and API declarations.

Important APIs/types/functions: `struct opr_uuid` stores 16 raw bytes; `struct opr_uuid_unpacked` exposes time fields, clock sequence, and node bytes. Defines `opr_uuid_t` and XDR compatibility alias `opr_uuid`. Declares create, nil/equality/hash, userland string functions, and pack/unpack.

Control flow: no runtime logic in the header.

State and persistence: caller-owned UUID values only.

Dependencies/integration: requires OpenAFS integer typedefs. Installed as `opr/uuid.h`.

Risks and test signals: packed layout is exactly 16 bytes and should not change. Compile coverage and UUID roundtrip tests validate users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/opr/uuid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/MacOS/Distribution.xml.in -->
# sources/distributed-fs/openafs/src/packaging/MacOS/Distribution.xml.in

Purpose: Mac Installer distribution XML template for the OpenAFS product package set.

Important APIs/types/functions: declares root-volume-only install, OS version bounds through placeholders, RAM installation check, title/background/readme/license, optional presentation extra content, choices for normal client and debug symbols, package references, and product version placeholder.

Control flow: consumed by Apple installer tooling, not executable code. User-facing choices include required normal OpenAFS client and optional debug extension.

State and persistence: template values are substituted during packaging; installer state is external.

Dependencies/integration: depends on build scripts supplying `%%OSVER_CUR%%`, `%%OSX_MAJOR_CUR%%`, `%%OSVER_NEXT%%`, `%%OSX_MAJOR_NEXT%%`, `%%PRES_EXTRA%%`, and `%%OPENAFS_VERSION%%`, plus package files named in `pkg-ref`.

Risks and test signals: mismatched package IDs or version placeholders break installer assembly. OS version bounds must track supported macOS releases. Validation is `productbuild`/Installer acceptance and test installs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/MacOS/Distribution.xml.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/MacOS/OpenAFS-debug.Description.plist.in -->
# sources/distributed-fs/openafs/src/packaging/MacOS/OpenAFS-debug.Description.plist.in

Purpose: PackageMaker description plist template for the OpenAFS debug-symbol extension.

Important APIs/types/functions: defines package title, description, version placeholder, and delete warning field.

Control flow: metadata only; consumed by packaging tools.

State and persistence: substituted into package resources during build.

Dependencies/integration: paired with `OpenAFS-debug.Info.plist.in` and `buildpkg.sh.in` debug package construction.

Risks and test signals: stale or mismatched `@PACKAGE_VERSION@` substitution affects installer metadata. Package build output and installer UI verify it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/MacOS/OpenAFS-debug.Description.plist.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/MacOS/OpenAFS-debug.Info.plist.in -->
# sources/distributed-fs/openafs/src/packaging/MacOS/OpenAFS-debug.Info.plist.in

Purpose: PackageMaker info plist template for the optional OpenAFS debug package.

Important APIs/types/functions: sets bundle identifier `org.openafs.OpenAFS-debug.pkg`, bundle name, version placeholders, authorization action, install location `/`, root-volume-only, relocatability, restart behavior, and package format version.

Control flow: metadata only.

State and persistence: becomes package receipt/install metadata after substitution.

Dependencies/integration: used by `buildpkg.sh.in` when major macOS version is 9 or newer.

Risks and test signals: contains duplicate `IFPkgFlagAllowBackRev` keys with conflicting false/true values; plist consumers may choose the later value but ambiguity is risky. Test by building and inspecting the generated pkg metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/MacOS/OpenAFS-debug.Info.plist.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/MacOS/OpenAFS.Description.plist.in -->
# sources/distributed-fs/openafs/src/packaging/MacOS/OpenAFS.Description.plist.in

Purpose: PackageMaker description plist template for the main OpenAFS package.

Important APIs/types/functions: provides delete warning, description text, title `OpenAFS`, and `@PACKAGE_VERSION@`.

Control flow: metadata only.

State and persistence: substituted into installer package resources.

Dependencies/integration: used with `OpenAFS.Info.plist.in` by `buildpkg.sh.in`.

Risks and test signals: description says "client and server" while package contents/scripts focus heavily on client install; metadata should match actual packaging intent. Installer UI and package inspection validate substitution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/MacOS/OpenAFS.Description.plist.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/MacOS/OpenAFS.Info.plist.in -->
# sources/distributed-fs/openafs/src/packaging/MacOS/OpenAFS.Info.plist.in

Purpose: PackageMaker info plist template for the main OpenAFS package.

Important APIs/types/functions: sets bundle identifier `org.openafs.OpenAFS.pkg`, bundle name/version placeholders, root authorization, install location `/`, root-volume-only, no restart, non-relocatable flags, and format version.

Control flow: metadata only.

State and persistence: becomes package metadata/receipt after build and install.

Dependencies/integration: consumed by `buildpkg.sh.in`; paired with resource scripts such as postinstall and preupgrade.

Risks and test signals: duplicate `IFPkgFlagAllowBackRev` keys appear, although both are true here. PackageMaker compatibility on newer macOS is a broader risk. Validate with package build and installer metadata inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/MacOS/OpenAFS.Info.plist.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/MacOS/OpenAFS.info.in -->
# sources/distributed-fs/openafs/src/packaging/MacOS/OpenAFS.info.in

Purpose: legacy PackageMaker plain-text package info template for older macOS packaging paths.

Important APIs/types/functions: key/value metadata for title, version, description, default location, authorization, masks, relocatability, reboot, fat install, root volume restriction, and back-rev behavior.

Control flow: metadata only; used by older packaging mode in `buildpkg.sh.in` for major versions below 7.

State and persistence: substituted into package metadata during build.

Dependencies/integration: relies on `@PACKAGE_VERSION@` substitution and old PackageMaker command syntax.

Risks and test signals: legacy format is likely unsupported on modern build hosts. Only old macOS package builds validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/MacOS/OpenAFS.info.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/MacOS/Uninstall -->
# sources/distributed-fs/openafs/src/packaging/MacOS/Uninstall

Purpose: Perl uninstaller for Mac OpenAFS packages, adapted from Apple's devtools uninstaller.

Important APIs/types/functions: `main`, `remove_generated_files`, `remove_main_packages`, `remove_generated_directories`, `add_directory_to_tree`, `remove_empty_directories`, `remove_a_file`, `remove_a_dir`, `remove_package_receipts`, `maybe_remove_ds_store`, and printing/spinner helpers. Package names include OpenAFS and debug variants. Generated config files under `/var/db/openafs/etc` are explicitly removed.

Control flow: defaults package directory from script location, removes generated files, scans package BOMs from old `/Library/Receipts` or new `/var/db/receipts`, queues files/directories/receipts for deletion, then runs a single privileged `osascript` shell command to remove them. It uses `lsbom` to enumerate package files and directories and attempts to remove empty directories bottom-up.

State and persistence: destructive filesystem changes: removes package files, generated OpenAFS config/cache metadata, empty dirs, and package receipts. Arrays `@rmfiles`, `@rmdirs`, and `@rmpkg` accumulate removals.

Dependencies/integration: depends on Perl, `File::Basename`, `/usr/bin/lsbom`, `/bin/rm`, `/bin/rmdir`, `osascript`, macOS receipt layout, and package BOM metadata.

Risks and test signals: command construction interpolates file paths into an AppleScript shell string, so spaces/quotes are risky. It can remove user config files listed in `@gen_files`. Dry-run mode variables exist but are not exposed via CLI. Test in a disposable system image with package receipts and generated files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/MacOS/Uninstall -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/MacOS/afs.conf -->
# sources/distributed-fs/openafs/src/packaging/MacOS/afs.conf

Purpose: shell-style default OpenAFS client configuration for Mac packaging, used when `afsd.options` does not override it.

Important APIs/types/functions: defines variables consumed by launch scripts: `VERBOSE`, `OPTIONS`, `AFS_SYSNAME`, `AFS_PRECACHE`, `AFS_POST_INIT`, and `AFS_PRE_SHUTDOWN`. Comments document many `afsd` flags and optional hook functions.

Control flow: no executable control flow besides optional user-defined shell functions in comments. Launch scripts source or parse these variables to start/shutdown the client.

State and persistence: installed as a sample/default config under `/var/db/openafs/etc/config`. Users may edit derived copies.

Dependencies/integration: used by Mac `openafs.launchdaemon`/launch scripts and `afsd`. The default `OPTIONS` enables dynamic root, fakestat, AFSDB, cache/stat sizing, daemons, volumes, and chunksize.

Risks and test signals: comments mention Linux for sysname despite Mac location, suggesting copied documentation. Defaults may be stale for modern clients. Test signal is successful client launch with expected afsd flags and optional hook behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/MacOS/afs.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/MacOS/buildpkg.sh.in -->
# sources/distributed-fs/openafs/src/packaging/MacOS/buildpkg.sh.in

Purpose: Mac packaging script template that stages OpenAFS files, builds PackageMaker packages, and wraps them into a DMG.

Important APIs/types/functions: command modes are default, `-firstpass`, and `-secondpass`. Key variables include `BINDEST`, `RESSRC`, `majorvers`, `RELNAME`, `PKGROOT`, `PKGRES`, `DPKGROOT`, `DPKGRES`, and `PACKAGEMAKER`. It builds main and debug packages, resource directories, symlinks into `/usr`, package plugins, and final hybrid/compressed DMG.

Control flow: first pass validates `CellServDB`, required resources, and binary destination, then creates package roots with preference panes, SecurityAgent plugin, tools, launchd plist, OpenAFS config, kernel extension, cache directories, symlinks, man pages, and ownership/mode settings. For newer systems it separates debug symbols. Second pass creates resource trees, runs PackageMaker, optionally embeds installer plugins, assembles a `dmg` directory, copies uninstall/background assets, and uses `hdiutil` to create the final DMG.

State and persistence: creates and deletes staging directories and package/DMG artifacts in the current directory; downloads `CellServDB` when curl is present.

Dependencies/integration: depends on macOS tools: PackageMaker, mdfind, pax, curl, hdiutil, strip, gzip, chown/chmod. It consumes many MacOS packaging resource files and a `make dest` output tree.

Risks and test signals: PackageMaker is obsolete on modern macOS. Numerous unquoted paths risk breakage with spaces. Network download uses plain HTTP. Version mapping stops at Darwin major 15. Test by running both passes on a known-supported macOS build host and installing the resulting DMG.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/MacOS/buildpkg.sh.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/MacOS/csrvdbmerge.pl -->
# sources/distributed-fs/openafs/src/packaging/MacOS/csrvdbmerge.pl

Purpose: Perl script to merge an updated master `CellServDB` into a local `CellServDB` while preserving locally modified cells.

Important APIs/types/functions: `doit` opens `CellServDB`, `CellServDB.master.last`, `CellServDB.master`, and writes `CellServDB.NEW`. It tracks `%cellstat` per cell: unchanged relative to last master, locally changed, or local-only.

Control flow: first pass scans the current file and compares each cell's server lines against the previous master. Cells missing from old master are local-only; line count or content differences mark local changes. Second pass rewrites the current file: unchanged cells are replaced from the new master, while changed/local cells are copied from the current file. Finally it renames `CellServDB.NEW` to `CellServDB` and copies the new master to `CellServDB.master.last`.

State and persistence: mutates files in the current directory and updates the saved master copy.

Dependencies/integration: uses `File::Copy`, `IO::File`, `Fcntl`, and the CellServDB text format. Included in Mac package resources by `buildpkg.sh.in`.

Risks and test signals: variable `$pos` is declared but never assigned before `setpos`, which may affect handling of cells with more servers than master. Parsing assumes cell header lines match `^>([-a-zA-Z0-9._]+)\s`. Tests should cover unchanged, changed, local-only, deleted, and server-count-different cells.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/MacOS/csrvdbmerge.pl -->
