# subset-b-009499 Research

Grouped source research for NetBSD syzkaller report parser fixtures. Each section is marker-delimited for reconciliation into the mapped source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/2 -->
# sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/2

## Purpose

`sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/2` is a NetBSD syzkaller report parser fixture for the expected title `page fault in copystr`. It captures a supervisor-mode page fault while a syz executor reaches `copystr` through NetBSD pathname handling and `mknodat` syscall dispatch. The source was read as a complete 1680-line file: the meaningful parser signal is concentrated in the title/header, trap line, stopped frame, stack trace, register dump, process table, and lockdebug availability line; the remainder is a long NetBSD debugger page listing with repetitive `PAGE FLAG PQ UOBJECT UANON` rows that tests report-boundary handling and noise tolerance.

## Important APIs, Types, and Functions

This file is static testdata consumed by syzkaller's report package, not executable Go or kernel code. Relevant syzkaller APIs and types are the report test harness around `Reporter.ContainsCrash`, `Reporter.Parse`, `Reporter.ParseFrom`, parser expectations extracted from `TITLE:`, and the NetBSD reporter implementation that recognizes fatal traps, stopped debugger frames, stack frames, and register dumps. Kernel functions and symbols present in the fixture include `copystr`, `pathbuf_maybe_copyin`, `do_sys_mknodat`, `sys_syscall`, and `syscall`. Important diagnostic tokens include `fatal page fault`, `supervisor mode`, `trap type 6 code 0`, `cr2 0`, `Stopped in pid 603.1`, `syz-executor1586`, `--- syscall (number 0) ---`, and `Sorry, kernel not built with the LOCKDEBUG option.`

## Control Flow

During tests, the harness reads the fixture, consumes the leading `TITLE:` expectation, and feeds the remaining console transcript to the NetBSD reporter. The reporter must detect the first fatal page fault despite duplicated/interleaved console text, identify `copystr` as the crash frame from the stopped instruction and stack trace, and avoid using lower-value frames such as `syscall`. The kernel-side flow represented by the stack is `syscall` -> `sys_syscall` -> `do_sys_mknodat` -> `pathbuf_maybe_copyin` -> `copystr`, where `copystr+0xe` executes `lodsb (%rsi)` with `rsi` equal to zero and `cr2 0`, consistent with a null source pointer fault during string copy.

## State and Persistence Behavior

The fixture persists expected parser state as a text file: a title header plus raw NetBSD debugger output. Runtime test state is transient and includes the detected crash start/end offsets, extracted title, crash type, report byte slice, selected frame, and any corruption/noise classification. No kernel state is mutated when the fixture is used. The transcript itself contains volatile kernel state such as LWP IDs, register values, process names, CPU/LWP scheduling states, and physical page metadata; those values are evidence for parsing but should not become brittle title components.

## Dependencies and Integration Points

The file integrates with syzkaller's `pkg/report` NetBSD reporter and generic report tests under `pkg/report/testdata/netbsd/report`. It exercises parser integration with NetBSD trap grammar, kernel debugger stopped-line parsing, stack frame extraction, process table noise, optional lockdebug output, and report truncation after repeated memory/page dumps. At product level, the same parsing path feeds syzkaller crash deduplication, dashboard grouping, reproducer association, and kernel subsystem triage for NetBSD crashes.

## Risks and Edge Cases

The main risk is overfitting to clean stack traces. This fixture contains duplicated `fatal page fault` text, garbled/interleaved console fragments, two trap lines with different stack pointers, raw register output, a large process table, no LOCKDEBUG build, and thousands of repetitive page rows. A robust parser must still select `page fault in copystr`, not a generic `fatal page fault`, not `pathbuf_maybe_copyin`, and not a repeated address/table token. It must also avoid treating the page metadata tail as a second report or extending the crash title with volatile addresses and PID values.

## Test Signals

A passing test should find a crash in the fixture, return the expected title `page fault in copystr`, preserve a non-empty report body, and keep `ParseFrom` behavior stable around the detected offsets. Strong additional signals are that the parser tolerates interleaved trap text, recognizes the stopped instruction line, chooses the first semantic crashing kernel frame, ignores process-table and page-list noise, and does not require LOCKDEBUG output to be present.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/2 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/3 -->
# sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/3

## Purpose

`sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/3` is a NetBSD syzkaller report parser fixture for the expected title `page fault in __asan_load8`. It records a KASAN/ASan-instrumented NetBSD kernel page fault while servicing `ptrace`, with source-line annotations for the ASan helper and ptrace path. The source was read as a complete 1431-line file: high-value parser data appears in the initial fatal page fault, stopped instruction, stack trace with inline source locations, register dump, process/LWP table, lockdebug sections, and the later repetitive page metadata dump.

## Important APIs, Types, and Functions

This is static parser testdata, not executable code. The relevant syzkaller APIs are the generic report test flow, `Reporter.ContainsCrash`, `Reporter.Parse`, `Reporter.ParseFrom`, title extraction from the `TITLE:` header, and NetBSD-specific oops/frame selection logic. Kernel symbols and implementation details represented in the transcript include `__asan_load8`, `kasan_shadow_8byte_isvalid`, `kasan_shadow_check`, `ptrace_machdep_dorequest`, `do_ptrace`, `sys_ptrace`, `sys___syscall`, and `syscall`. Source paths embedded in the stack include `sys/kern/subr_asan.c`, `sys/arch/amd64/amd64/process_machdep.c`, `sys/kern/sys_ptrace_common.c`, `sys/kern/sys_ptrace.c`, `sys/kern/sys_syscall.c`, `sys/sys/syscallvar.h`, and `sys/arch/x86/x86/syscall.c`.

## Control Flow

The test harness parses the title header, then asks the NetBSD reporter to detect and summarize the console body. The parser must classify the `fatal page fault in supervisor mode`, extract `__asan_load8` from the stopped line and stack, and handle inline annotation suffixes without polluting the title. The kernel-side path is syscall entry for syscall number 198 -> `sys___syscall` -> `sys_ptrace` -> `do_ptrace` -> `ptrace_machdep_dorequest` -> ASan instrumentation helper `__asan_load8`, which faults while checking an address associated with `rax = ffff900000000000` and `cr2 = 0xffff900000000000`.

## State and Persistence Behavior

The file persists expected parser behavior through the `TITLE:` line plus a raw kernel debugger transcript. Runtime parser state is ephemeral: report boundaries, selected frame, source-location trimming, title, crash type, and parse offsets. The kernel transcript includes volatile state such as register values, LWP structures, syz executor instances, lock owner addresses, CPU IDs, and `uvm_obj_init` lockdebug records. These fields are useful for parser coverage but should remain report body details rather than title keys.

## Dependencies and Integration Points

The fixture integrates with the NetBSD reporter's support for fatal page faults, KASAN/ASan helper frames, inline source annotations, ptrace stack traces, lockdebug output, process tables, and long debugger tails. It also exercises the generic report package's stack-frame sanitization and crash deduplication contract: sanitizer helper names are sometimes real top frames and must be preserved when they are the actual stopped frame. The downstream integration point is syzkaller dashboard grouping for NetBSD ASan faults in architecture-specific ptrace code.

## Risks and Edge Cases

The key parser risk is confusing sanitizer helper frames with ignorable diagnostic helpers. In this fixture, `__asan_load8` is the expected title because the CPU stopped in that function, even though inline lines mention `kasan_shadow_8byte_isvalid` and `kasan_shadow_check`. The parser must strip source-line suffixes, avoid volatile addresses, and not retitle the crash as `ptrace_machdep_dorequest` or `do_ptrace`. It must also tolerate lockdebug sections, two executor LWPs marked with `>`, held `uvm_obj_init` locks, `Turnstile` text, and a long page metadata tail without creating secondary crashes.

## Test Signals

A passing test detects a crash and returns exactly `page fault in __asan_load8` with non-empty report bytes. Strong signals include correct handling of `kernel: page fault trap, code=0`, preservation of the ASan top frame despite inline annotations, stable parse offsets across `ParseFrom`, and ignoring lockdebug/page-table noise. Regression tests should fail if a parser starts choosing ptrace wrapper frames, source file paths, raw addresses, or repeated `PAGE FLAG` rows for the title.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/3 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/4 -->
# sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/4

## Purpose

`sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/4` is a compact NetBSD syzkaller report parser fixture for the expected title `UBSan: Undefined behavior`. It contains a single UBSan diagnostic emitted very early in boot or initialization time, reporting a misaligned `UINT32` store in ACPICA GPE initialization code. The source was read as a complete 3-line file.

## Important APIs, Types, and Functions

The file is static testdata for syzkaller's NetBSD report parser. Parser-facing APIs are the test harness, `Reporter.ContainsCrash`, `Reporter.Parse`, `Reporter.ParseFrom`, the `TITLE:` expectation, and UBSan pattern matching in the NetBSD reporter. Diagnostic entities in the text include `UBSan: Undefined Behavior`, source location `/media/k4iz3n/event1/kWork/src/sys/external/bsd/acpica/dist/events/evgpeinit.c:362:5`, a `store to misaligned address`, target address `0xffffffff85b09a03`, type `UINT32`, and required `4 byte alignment`.

## Control Flow

The test harness reads the title header and passes the single log line to the reporter. The parser must recognize the UBSan diagnostic without needing a stack trace, panic line, stopped debugger frame, or process table. The represented kernel flow is an ACPICA event/GPE initialization path reaching `evgpeinit.c` line 362 and performing a misaligned 32-bit store; the fixture intentionally provides only the sanitizer summary line.

## State and Persistence Behavior

The file persists a minimal expected parser state: title plus one raw UBSan line. Runtime state consists only of the detected crash offset, title, report bytes, and type/classification. There is no process state, lock state, dump state, or file-backed persistence. The absolute build path and kernel address are volatile details and should not be required for stable grouping.

## Dependencies and Integration Points

This fixture integrates with NetBSD UBSan report recognition and with generic syzkaller report handling for one-line crashes. It protects dashboard grouping for undefined-behavior reports that lack a traceback and ensures the parser can use sanitizer category text as the title when no better function frame is available. The kernel-domain integration point is NetBSD's external ACPICA code under `sys/external/bsd/acpica/dist/events`.

## Risks and Edge Cases

The main risk is treating the line as non-crashing because it lacks `panic`, `fatal`, `Stopped`, or stack frames. Another risk is over-specific title extraction that includes the absolute local build path, address, type, or alignment value. The parser should preserve the broad, stable title `UBSan: Undefined behavior`, while retaining detailed location and alignment evidence in the report body.

## Test Signals

A passing test detects this one-line report and returns `UBSan: Undefined behavior` with non-empty report bytes. Useful regression signals are that the parser accepts both `Undefined Behavior` capitalization in the log and `Undefined behavior` capitalization in the expected title, handles sanitizer reports without stack traces, and keeps volatile paths/addresses out of the deduplication title.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/4 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/5 -->
# sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/5

## Purpose

`sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/5` is a NetBSD syzkaller report parser fixture for the expected title `lock error in do_sys_accept`. It captures a LOCKDEBUG panic caused by a mutex ownership assertion failure while handling `paccept`/`accept` syscall logic. The source was read as a complete 18-line file.

## Important APIs, Types, and Functions

The file is static report testdata rather than executable code. Relevant syzkaller APIs are the report test harness, `Reporter.ContainsCrash`, `Reporter.Parse`, `Reporter.ParseFrom`, `TITLE:` expectation parsing, and NetBSD panic/traceback title extraction. Kernel functions and diagnostics in the transcript include `panic: lock error`, `Mutex: mutex_vector_exit,761`, assertion `MUTEX_OWNER(mtx->mtx_owner) == curthread`, `vpanic`, `snprintf`, `lockdebug_abort`, `mutex_vector_exit`, `do_sys_accept`, `sys_paccept`, `sys___syscall`, and `syscall`. The syscall marker is `--- syscall (number 198) ---`.

## Control Flow

The test harness reads the expected title and feeds the panic transcript to the NetBSD reporter. The parser must identify the lock-error panic, walk the traceback, and choose `do_sys_accept` as the semantic crashing frame rather than generic panic helpers or lockdebug internals. The represented kernel flow is syscall entry -> `sys___syscall` -> `sys_paccept` -> `do_sys_accept` -> `mutex_vector_exit`; the lockdebug subsystem detects that the current LWP does not own the mutex being released and triggers `lockdebug_abort`/`vpanic`.

## State and Persistence Behavior

The fixture persists the expected parser title plus a concise panic and reboot transcript. Runtime parser state is transient: detected panic offset, traceback frame list, selected title frame, report bytes, and end offset near dump/reboot lines. Kernel state in the log includes a mutex address, CPU number, LWP pointer, dump device, and reboot action; those values are volatile and should remain body evidence, not title components. No external state is changed by running the parser test.

## Dependencies and Integration Points

This fixture integrates with NetBSD panic parsing, LOCKDEBUG assertion recognition, traceback frame filtering, syscall wrapper handling, and panic dump/reboot boundary detection. It protects the path that syzkaller uses to group NetBSD locking bugs by the kernel subsystem frame (`do_sys_accept`) instead of by shared helpers such as `vpanic`, `lockdebug_abort`, or `mutex_vector_exit`. Downstream, this improves deduplication and triage for socket accept path locking regressions.

## Risks and Edge Cases

The title extractor must filter generic frames carefully. Selecting `mutex_vector_exit` would identify the failed primitive but lose the owning subsystem, while selecting `vpanic` or `lockdebug_abort` would collapse unrelated lock bugs together. The parser also needs to tolerate compact logs with no register dump or process table, retain the panic line as report evidence, and stop cleanly around `dumping ... not possible` and `rebooting...`.

## Test Signals

A passing test detects the panic and returns exactly `lock error in do_sys_accept` with a non-empty report. Strong signals include recognizing `panic: lock error` as the crash start, selecting the first meaningful non-helper traceback frame, preserving syscall context in the report body, and keeping dump/reboot lines inside or at the boundary of the parsed report without creating extra crashes.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/5 -->
