# subset-b-009500 research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/6 -->
# sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/6

## Purpose

This 1242-line fixture is a NetBSD syzkaller report parser test for the expected title `ASan: Unauthorized Access in sys__lwp_getname`. It captures a KASAN/ASan panic from a read during `kasan_copyoutstr` while servicing syscall 198, with enough debugger, process, lock, malloc, pool, and reboot context to exercise long-report capture and title normalization.

## Important APIs, Types, and Functions

The file is static testdata, so the important APIs are syzkaller reporter behaviors: metadata parsing from `TITLE:`, crash detection from `panic: ASan: Unauthorized Access`, extraction through `Reporter.Parse`, frame filtering, and report-end detection. Kernel evidence includes `vpanic`, `snprintf`, `kasan_report`, `kasan_copyoutstr`, `sys__lwp_getname`, `sys___syscall`, `syscall`, `breakpoint`, `db_panic`, and the syscall marker `--- syscall (number 198) ---`.

## Control Flow

The represented kernel flow is syscall entry through `sys___syscall` into `sys__lwp_getname`, followed by `kasan_copyoutstr` checking a user copyout string and reporting an unauthorized read. The panic enters DDB, emits a second symbolic traceback, register state, LWP/process tables, locks, allocator summaries, and dump/reboot lines. The parser must choose the actionable syscall frame, not helper frames such as `vpanic`, `snprintf`, `kasan_report`, or `kasan_copyoutstr`.

## State and Persistence Behavior

The fixture persists volatile runtime addresses, CPU/LWP identifiers, multiple `syz-executor` processes, held locks, pool statistics, and dump metadata. Parser state should remain transient: crash start offset, selected title, body bytes, and end offset. None of the allocator counts, addresses, timestamps, or process IDs should be used as stable title material.

## Dependencies and Integration Points

This case integrates NetBSD panic matching, sanitizer report normalization, DDB transcript handling, traceback frame selection, and long-report boundary handling. It also exercises the path where the initial timestamped kernel log and the later DDB traceback both describe the same crash.

## Risks and Edge Cases

The title must normalize `Unauthorized Access In ...` to the expected `ASan: Unauthorized Access in sys__lwp_getname` while preserving the crash body. A naive frame picker could group under KASAN helpers, and a naive end detector could truncate before lock/pool context or accidentally treat later debugger output as a second crash. Syslog-like timestamps and repeated stack frames must not destabilize deduplication.

## Test Signals

A passing test returns exactly the expected title, produces a non-empty report containing the ASan panic and `sys__lwp_getname` frame, and keeps the complete DDB evidence as one crash report. The strongest signal is correct selection of `sys__lwp_getname` as the first meaningful non-sanitizer kernel frame.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/6 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/7 -->
# sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/7

## Purpose

This tiny NetBSD fixture contains no `TITLE:` metadata and consists of a syslog-looking login line that includes `postfix/pickup[596]: panic: event_init: unable to initialize`. Its purpose is negative coverage: the reporter should not classify arbitrary userland syslog text as a kernel crash.

## Important APIs, Types, and Functions

The relevant syzkaller APIs are `Reporter.ContainsCrash` and `Reporter.Parse` for NetBSD report detection. There are no kernel stack frames, DDB commands, or executable source APIs in the file. The important token is the literal word `panic:` embedded in a daemon log line.

## Control Flow

The parser receives a two-line input, sees no expected title, and must distinguish a syslog facility/program message from a kernel panic transcript. There is no traceback, no `Stopped in pid`, no `cpuN: Begin traceback`, no DDB prompt, and no dump/reboot boundary.

## State and Persistence Behavior

The only persisted state is the syslog timestamp, hostname, process name, process ID, and message. Parser state should remain empty for crash extraction. No kernel state is represented.

## Dependencies and Integration Points

This integrates with false-positive filtering for NetBSD logs that include the word `panic` outside kernel context. It protects syzkaller dashboards from ingesting service startup failures as kernel bugs.

## Risks and Edge Cases

The risk is overmatching on `panic:` alone. A parser that ignores syslog prefixes or process names would produce a bogus title and report. The case also checks that missing `TITLE:` is acceptable for a no-crash fixture.

## Test Signals

A passing test reports no crash or yields an empty parsed result, depending on harness convention. It should not create `panic: event_init: unable to initialize` as a kernel title.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/7 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/8 -->
# sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/8

## Purpose

This three-line NetBSD fixture verifies UBSan detection and title normalization. It expects `UBSan: Undefined behavior` from a one-line undefined-behavior report in an ACPICA table-loading source file.

## Important APIs, Types, and Functions

The relevant reporter APIs are sanitizer-pattern matching, `TITLE:` expectation parsing, and normalized title construction. Kernel/source evidence names `/sys/external/bsd/acpica/dist/tables/tbxfload.c:187:10`, a misaligned load, type `UINT32`, and address/alignment details.

## Control Flow

The parser reads the expected title and then a timestamped UBSan diagnostic. There is no panic stack, DDB prompt, or reboot trailer. The reporter must still classify the sanitizer line as a crash signal and use the generic UBSan title rather than volatile file path, address, or type-specific wording.

## State and Persistence Behavior

The fixture stores the source location, bad address, access type, and required alignment. Those are evidence in the report body, but they are intentionally excluded from the stable title. Runtime parser state is limited to the sanitizer match and report byte range.

## Dependencies and Integration Points

This integrates NetBSD sanitizer recognition with the common syzkaller report pipeline. It also covers early boot or single-line crash evidence, where the parser cannot depend on a subsequent traceback.

## Risks and Edge Cases

Over-specific titles would fragment UBSan bugs by build path or address. Under-detection would miss reports that lack `panic:`. The parser also needs to preserve case-insensitive or capitalization-insensitive matching between `Undefined Behavior` in the log and `Undefined behavior` in the expected title.

## Test Signals

A passing test returns exactly `UBSan: Undefined behavior` and a non-empty report containing the misaligned `UINT32` load diagnostic.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/8 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/0 -->
# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/0

## Purpose

This OpenBSD fixture expects title `uvm_fault` and marks the report `CORRUPTED: Y`. It is a short page-fault transcript ending at `vn_writechk+0x13`, used to verify that a damaged or incomplete crash log can still be recognized while being flagged as corrupted.

## Important APIs, Types, and Functions

Reporter-facing items are `TITLE:`, `CORRUPTED: Y`, page-fault matching, and DDB stop-line parsing. Kernel evidence includes `uvm_fault(...) -> e`, `kernel: page fault trap, code=0`, and `Stopped at vn_writechk+0x13`.

## Control Flow

The log begins around a login prompt, reports a UVM fault, then stops at an instruction in `vn_writechk`. There is no trace, process table, or DDB command output. The parser should prefer the generic `uvm_fault` title because the report is explicitly corrupted and too incomplete to form a reliable function-specific title.

## State and Persistence Behavior

The fixture persists only the fault map/address/code tuple and a stopped instruction. Parser state should record the corruption annotation separately from crash title selection. Address values and the stopped instruction are volatile evidence.

## Dependencies and Integration Points

This integrates OpenBSD page-fault detection with corrupted-report metadata handling. It protects callers that need to keep crash evidence while reducing confidence in deduplication or reproduction signals.

## Risks and Edge Cases

The main risk is over-trusting an incomplete stop frame and producing a specific title such as `uvm_fault in vn_writechk`. Another risk is discarding the crash entirely because the trace is absent. The CR-style carriage returns in the source also test console text normalization.

## Test Signals

A passing test returns `uvm_fault`, marks the parsed report as corrupted, and includes the `kernel: page fault trap` and `vn_writechk` stop line in the body.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/0 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/1 -->
# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/1

## Purpose

This OpenBSD fixture expects `panic: cleaned vnode isn't` and is typed as `DoS`. It exercises panic-title extraction from a vnode consistency failure during filesystem lookup after a `cleaned vnode` diagnostic.

## Important APIs, Types, and Functions

Syzkaller-facing items are `TITLE:`, `TYPE: DoS`, panic matching, DDB trace parsing, and line-wrap repair. Kernel functions include `getnewvnode`, `ffs_vget`, `ufs_lookup`, `VOP_LOOKUP`, `vfs_lookup`, `namei`, `dofstatat`, `syscall`, and `Xsyscall_untramp`.

## Control Flow

The transcript prints vnode metadata, panics, enters DDB, and traces from panic helpers into vnode allocation and UFS lookup. The represented system call path is `dofstatat` through name lookup, where `ffs_vget` calls `getnewvnode` and encounters a supposedly cleaned vnode that is not in the expected state.

## State and Persistence Behavior

The log stores vnode type, UFS inode number, device, link counts, mode, ownership, size, process IDs, and trace addresses. These values are diagnostic state only. Parser state should preserve the DoS classification and the stable panic string.

## Dependencies and Integration Points

This integrates OpenBSD filesystem panic parsing, VFS/UFS stack filtering, and multiline wrapped frame handling. It also connects report metadata to vulnerability classification through `TYPE: DoS`.

## Risks and Edge Cases

The panic line is preceded by a detailed diagnostic, so the parser must not title the report from `cleaned vnode:` rather than `panic:`. Wrapped `VOP_LOOKUP` and `dofstatat` lines must remain readable enough for stack evidence. The parser should not fold the OpenBSD bug-report URL into a second report.

## Test Signals

A passing test returns the exact panic title, retains type `DoS`, and includes the `getnewvnode`/`ffs_vget`/`ufs_lookup` trace as evidence.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/1 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/10 -->
# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/10

## Purpose

This OpenBSD fixture expects `witness: reversal: vmmaplk inode` and is marked `SUPPRESSED: Y`. It captures a WITNESS lock-order reversal between the VM map lock and an inode lock, without a kernel panic.

## Important APIs, Types, and Functions

Reporter behaviors include witness diagnostic recognition, suppressed metadata handling, lock-name title construction, DDB parsing where `show panic` says the kernel did not panic, and trace capture. Kernel functions include `witness_checkorder`, `_rw_enter`, `vm_map_lock_ln`, `uvm_map`, `km_alloc`, `pool_get`, `ufsdirhash_build`, `ufs_lookup`, `_rrw_enter`, `VOP_LOCK`, `vn_lock`, `uvn_io`, `uvn_get`, `uvm_fault`, `uvm_fault_wire`, `uvm_map_pageable_wire`, and `sys_mlockall`.

## Control Flow

WITNESS reports two observed lock orders: inode to VM map from UFS lookup and VM map to inode from `mlockall` wiring a vnode-backed fault. It enters DDB through `witness_checkorder`, but `show panic` confirms this is a debugger break rather than a panic. The parser must still extract the witness report and title it from the two lock classes.

## State and Persistence Behavior

The fixture stores lock addresses, lock class names, source locations, two historical order stacks, DDB registers, process tables, and allocator/pool summaries. The stable state is the lock pair `vmmaplk inode`; addresses and counts are volatile.

## Dependencies and Integration Points

This integrates OpenBSD WITNESS lock-order diagnostics with suppression handling. It matters for syzkaller triage because suppressed reports should be detected but not treated with the same priority as unsuppressed crashes.

## Risks and Edge Cases

The absence of `panic:` can cause under-detection if the parser only watches panic lines. Conversely, generic DDB stops must not be reported unless preceded by WITNESS content. The title must use lock class names rather than full source paths or addresses.

## Test Signals

A passing test returns `witness: reversal: vmmaplk inode`, marks the report suppressed, and includes both lock-order stacks plus the `the kernel did not panic` DDB evidence.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/10 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/11 -->
# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/11

## Purpose

This OpenBSD fixture expects `witness: thread exiting with locks held`. It tests WITNESS detection for a reaper thread that attempts to exit while holding a sleeplock, with panic text and a compact reaper stack.

## Important APIs, Types, and Functions

Relevant reporter logic covers `TITLE:`, WITNESS warning matching, panic extraction, DDB command transcript parsing, and process-table inclusion. Kernel functions include `witness_thread_exit`, `panic`, `db_enter`, and `reaper`.

## Control Flow

The log first lists a held inode `rrwlock`, then panics with `Thread ... cannot exit while holding sleeplocks`. The trace runs through `witness_thread_exit` into `reaper`, and the later DDB `show panic`/`trace` repeats the same path. The title should come from the WITNESS class of bug rather than the volatile thread pointer in the panic.

## State and Persistence Behavior

Persistent evidence includes held lock class, source path, thread/process identifiers, scheduler flags, registers, process list, and allocator state. Parser state should store the stable title and body range without embedding thread addresses into the title.

## Dependencies and Integration Points

This integrates OpenBSD WITNESS exit checks with normal panic report parsing. It also tests that kernel housekeeping threads such as `reaper` can be valid crashing contexts even when no syzkaller executor appears on the top trace.

## Risks and Edge Cases

Using the panic string verbatim would create address-sensitive titles. The parser must also avoid treating the repeated DDB trace as a second crash and must preserve the original WITNESS preamble, which explains the lock context.

## Test Signals

A passing test returns `witness: thread exiting with locks held`, keeps a non-empty report, and includes `witness_thread_exit` plus `reaper` in the stack evidence.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/11 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/12 -->
# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/12

## Purpose

This OpenBSD fixture expects `witness: userret: returning with the following locks held:`. It captures a WITNESS `userret` panic caused by returning to user space while an inode lock remains held.

## Important APIs, Types, and Functions

Reporter functions under test are WITNESS title extraction, panic matching for `witness_warn`, DDB trace parsing, and metadata preservation. Kernel functions include `witness_warn`, `userret`, `syscall`, and `Xsyscall`; the held lock is an exclusive inode `rrwlock`.

## Control Flow

The kernel reports held locks at user return, then panics through `witness_warn`. The stack shows the panic on the syscall return path rather than the original syscall that acquired the lock. The parser must title the report from the WITNESS `userret` diagnostic, not from the generic `panic: witness_warn`.

## State and Persistence Behavior

The fixture preserves the held inode lock address, source location, process flags, registers, process list, and allocator/pool tables. Parser state should keep the stable WITNESS title and type-neutral report body; address-bearing lock details remain evidence only.

## Dependencies and Integration Points

This integrates WITNESS user-return checks with OpenBSD panic parsing and DDB transcript boundaries. It also validates that a colon-ending title in `TITLE:` is preserved exactly.

## Risks and Edge Cases

The `panic: witness_warn` line is too generic for deduplication and must not override the witness message. The original lock acquisition path may be absent, so the reporter has to accept the WITNESS preamble as primary evidence.

## Test Signals

A passing test returns exactly the expected title including the trailing colon and includes `witness_warn` and `userret` in the parsed report.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/12 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/13 -->
# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/13

## Purpose

This OpenBSD `DoS` fixture expects `panic: timeout_add: to_ticks < NUM`. It validates title generalization for a timer panic where `timeout_add` receives a negative tick count from speaker/PC speaker ioctl handling.

## Important APIs, Types, and Functions

Reporter behavior includes panic-title normalization that replaces numeric values with `NUM`, DoS metadata parsing, DDB transcript capture, and report-end handling through large `show malloc` and `show all pools` sections. Kernel functions include `timeout_add`, `pcppi_bell`, `spkrioctl`, `VOP_IOCTL`, `vn_ioctl`, `sys_ioctl`, `syscall`, and `Xsyscall`.

## Control Flow

The syscall path is `sys_ioctl` on a vnode/device, into `spkrioctl`, then `pcppi_bell`, which calls `timeout_add` with `to_ticks (-3)`. The panic enters DDB, repeats the panic and trace, then emits registers, process state, and allocator/pool data.

## State and Persistence Behavior

The source stores the negative tick value, process IDs, DDB registers, and extensive allocator/pool counters. The normalized title intentionally abstracts `-3` to `NUM` so equivalent bugs with different inputs deduplicate together.

## Dependencies and Integration Points

This integrates OpenBSD panic parsing with numeric sanitization and ioctl/device-driver stack capture. It also exercises long diagnostic sections following the actionable trace.

## Risks and Edge Cases

If numeric generalization fails, syzkaller may fragment reports by the exact tick value. If the parser prefers `pcppi_bell` or `spkrioctl`, it loses the direct failing invariant. Long pool listings should remain part of the same report, not become noise that hides the crash.

## Test Signals

A passing test returns `panic: timeout_add: to_ticks < NUM`, preserves `TYPE: DoS`, and includes the `timeout_add` to `sys_ioctl` trace.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/13 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/14 -->
# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/14

## Purpose

This OpenBSD fixture expects `uvm_fault: rtable_satoplen`. It captures a kernel page fault in route-table prefix-length parsing during route socket output from a `sendto` path.

## Important APIs, Types, and Functions

Reporter behaviors include page-fault recognition, function-specific title extraction from `Stopped at` and DDB trace lines, and DDB context capture. Kernel functions include `rtable_satoplen`, `rtable_lookup`, `rtm_output`, `route_output`, `route_usrreq`, `sosend`, `sendit`, `sys_sendto`, `syscall`, and `Xsyscall`.

## Control Flow

The log starts with a page-fault trap at `rtable_satoplen+0x150`. DDB `show panic` records `kernel page fault`, and the trace shows route message output through a socket send path into route-table lookup. The parser should title the report as a UVM fault in `rtable_satoplen` rather than generic `kernel page fault`.

## State and Persistence Behavior

The fixture stores the faulting virtual address, instruction, registers, process list, locks, malloc stats, and pool stats. The stable persisted research signal is the faulting function; addresses and route buffer values are volatile.

## Dependencies and Integration Points

This integrates OpenBSD page-fault parsing with networking route-socket stack selection. It also uses `show all locks` content that mentions concurrent filesystem locks, which must remain secondary context rather than title input.

## Risks and Edge Cases

The stopped instruction and first trace frame agree on `rtable_satoplen`; losing either can weaken title extraction. Concurrent lock/process noise could mislead a parser that scans all later frames indiscriminately. The title should not include raw fault addresses.

## Test Signals

A passing test returns `uvm_fault: rtable_satoplen` and includes the route-output trace from `rtable_satoplen` through `sys_sendto`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/14 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/15 -->
# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/15

## Purpose

This short OpenBSD fixture expects the unusual title `panic: kernel diagnostic assertion "tname->un_flags serialport: VM disconnected.` It captures a truncated or interleaved console session where syzkaller program lines and a VM disconnection message interrupt an assertion panic.

## Important APIs, Types, and Functions

Reporter behavior under test includes partial panic extraction, title preservation from `TITLE:`, and tolerance of serial transport artifacts. The only source-level operations visible are syzkaller `mknod` calls and the panic prefix `kernel diagnostic assertion "tname->un_flags`; no complete stack is present.

## Control Flow

The file shows syzkaller program fragments creating `./bus`, then a panic line that is cut by `serialport: VM disconnected.` There is no DDB trace, register block, or reboot trailer. The parser must still recognize the panic start and preserve the truncated evidence as the report body.

## State and Persistence Behavior

The fixture persists test-program calls, a partial assertion expression, and a transport-disconnect suffix. Parser state should classify the crash based on the available panic line but treat the report as low-context evidence.

## Dependencies and Integration Points

This integrates OpenBSD panic parsing with syzkaller's VM/serial output collection. It protects the path that ingests crashes even when the VM dies before full DDB output is available.

## Risks and Edge Cases

The greatest risk is discarding the crash because the assertion line is incomplete. Another risk is treating `serialport: VM disconnected` as part of a stable kernel assertion; here it is intentionally present in the expected title, so the fixture documents current parser behavior around truncated console text.

## Test Signals

A passing test returns the exact expected truncated title and produces a non-empty report containing the `mknod` repro lines plus the partial panic line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/15 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/16 -->
# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/16

## Purpose

This OpenBSD fixture expects `witness: userret: write`. It is a WITNESS `userret` report where the diagnostic includes the held-lock acquisition stack, allowing syzkaller to specialize the title to the write path.

## Important APIs, Types, and Functions

Reporter behavior includes WITNESS `userret` matching, stack-derived operation naming, panic matching for `witness_warn`, and DDB transcript capture. Kernel functions include `rw_enter`, `rrw_enter`, `VOP_LOCK`, `vn_write`, `dofilewritev`, `sys_write`, `witness_warn`, `userret`, `syscall`, and `Xsyscall`. Later lock dumps also mention `ptmioctl`, `vn_ioctl`, `sys_ioctl`, and `sys_fsync`.

## Control Flow

The report begins with WITNESS listing an inode lock held by a write stack. The panic happens later at `userret`, so the active trace is generic, but the preamble identifies `sys_write` as the lock acquisition path. The parser should combine these facts into the expected `witness: userret: write` title.

## State and Persistence Behavior

The fixture stores held locks for multiple processes, process states, registers, malloc tables, and pool statistics. The held inode address and unrelated processes are volatile; the stable state is that user return occurred while a write-acquired inode lock was still held.

## Dependencies and Integration Points

This integrates WITNESS lock diagnostics with semantic title refinement. It also tests that `show all locks` after the panic can contain several locks without overriding the first WITNESS subject.

## Risks and Edge Cases

If the parser looks only at the panic trace, it will title the report as generic `witness_warn` or `userret`. If it scans all locks without ordering, it may choose ioctl or fsync instead of write. The acquisition stack in the preamble is the authoritative signal.

## Test Signals

A passing test returns `witness: userret: write`, keeps the `witness_warn` panic, and includes the write stack from `vn_write` through `sys_write`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/16 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/17 -->
# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/17

## Purpose

This OpenBSD `DoS` fixture expects `panic: attempt to execute user address`. It captures a supervisor-mode attempt to execute address `0xf7` during route cloning in the UDP `connect` path.

## Important APIs, Types, and Functions

Reporter behaviors include panic-title normalization that drops the exact user address, DoS metadata parsing, DDB trace capture, and stack frame filtering around trap helpers. Kernel functions include `pageflttrap`, `kerntrap`, `alltraps_kern_meltdown`, the bogus frame at `0xf7`, `rt_clone`, `rtalloc_mpath`, `in_pcbselsrc`, `in_pcbconnect`, `udp_usrreq`, `sys_connect`, `syscall`, and `Xsyscall`.

## Control Flow

The system panics after trap handling detects an attempted supervisor execution from user space. The trace shows the failing call target before the networking route path, then proceeds through UDP connect. Later DDB output repeats the panic, registers, process table, and locks.

## State and Persistence Behavior

The source preserves the exact attempted address, process IDs, register state, netlock/kernel lock information, and allocator statistics. The title intentionally abstracts the address so different bad user addresses group together.

## Dependencies and Integration Points

This integrates OpenBSD trap/panic parsing with network stack report grouping. It also covers symbolic traces with a non-symbol frame (`f7(...) at 0xf7`) that should be evidence, not the selected title.

## Risks and Edge Cases

Including `0xf7` in the title would fragment reports. Selecting `pageflttrap` or `alltraps_kern_meltdown` would hide the execution-at-user-address condition. The parser must also keep route/UDP frames for triage without treating them as the panic title.

## Test Signals

A passing test returns `panic: attempt to execute user address`, preserves `TYPE: DoS`, and includes the `rt_clone` to `sys_connect` stack.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/17 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/18 -->
# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/18

## Purpose

This OpenBSD fixture expects generic `uvm_fault`. It captures a kernel page fault at an anonymous executable address before `rt_match` in the UDP connect source-selection path.

## Important APIs, Types, and Functions

Reporter behavior includes generic page-fault title selection when the top frame is an address rather than a named function, DDB transcript parsing, and report-end handling. Kernel functions visible after the anonymous frame include `rt_match`, `in_pcbselsrc`, `in_pcbconnect`, `udp_usrreq`, `sys_connect`, `syscall`, and `Xsyscall`.

## Control Flow

The console records a UVM fault and a stop at raw address `0xfffffd802ea85278`, then DDB repeats `kernel page fault` and traces through route matching and UDP connect. Because the immediate faulting frame is not a stable symbol, the expected title stays generic.

## State and Persistence Behavior

The fixture stores the faulting address, instruction bytes, registers, process table, allocator state, and pool tables. The address is volatile and should not become title material. Parser state should retain the whole report as one crash.

## Dependencies and Integration Points

This integrates OpenBSD page-fault detection with anonymous-frame handling. It complements report 14, where a named route-table function allows a specific `uvm_fault: function` title.

## Risks and Edge Cases

The parser must avoid using raw addresses as titles. It also should not select `rt_match` merely because it is the first named frame after the anonymous address; the expected output documents that this report lacks enough confidence for a function-specific title.

## Test Signals

A passing test returns exactly `uvm_fault`, keeps the anonymous stopped-address line, and includes the route/UDP connect trace as evidence.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/18 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/19 -->
# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/19

## Purpose

This OpenBSD fixture expects `malloc: free list modified: devbuf`. It captures an allocator integrity panic for a modified freelist object from the `devbuf` malloc type during BPF device open.

## Important APIs, Types, and Functions

Reporter behavior includes malloc-corruption title extraction, panic parsing, DDB transcript handling, and allocator diagnostic normalization. Kernel functions include `malloc`, `bpfopen`, `spec_open_clone`, `spec_open`, `VOP_OPEN`, `vn_open`, `doopenat`, `syscall`, and `Xsyscall`.

## Control Flow

The panic is raised by `malloc` after detecting that a freed object's poison value changed. The call path is opening a cloned special device for BPF, through VFS open helpers. DDB repeats the panic and trace, then records registers, process tables, malloc statistics, and pool state.

## State and Persistence Behavior

The fixture stores the object address, word index, object size, previous type `devbuf`, observed value, expected poison, process IDs, and allocator tables. The stable title uses the corruption class and malloc type, not addresses or poison values.

## Dependencies and Integration Points

This integrates OpenBSD allocator panic parsing with device-open/VFS stack capture. It also helps syzkaller group memory-corruption reports by allocator type when the direct corruptor may be earlier than the detecting allocation.

## Risks and Edge Cases

The detecting function `malloc` is generic, so the title must come from the diagnostic string. Including object addresses would make each run look unique. The parser must keep `bpfopen` and open-path frames as triage hints while not over-attributing the root cause.

## Test Signals

A passing test returns `malloc: free list modified: devbuf` and includes the `Data modified on freelist` panic plus the `bpfopen` open stack.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/19 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/2 -->
# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/2

## Purpose

This OpenBSD fixture expects `pool: double put: mbufpl`. It records a pool allocator panic for a double `pool_put` of an mbuf object during socket receive cleanup.

## Important APIs, Types, and Functions

Reporter behavior includes pool-corruption title extraction, panic parsing, DDB stack handling, and wrapped-line tolerance. Kernel functions include `pool_do_put`, `pool_put`, `m_free`, `m_freem`, `soreceive`, `recvit`, `sys_recvfrom`, `syscall`, and `Xsyscall_untramp`.

## Control Flow

The panic begins at `pool_do_put: mbufpl: double pool_put`, enters DDB, and traces through mbuf free logic while servicing `recvfrom`. Several frame names are split across physical lines, so the parser must keep the stack readable even with console wrapping.

## State and Persistence Behavior

The fixture stores the mbuf address, process metadata, stack addresses, and bug-report footer. The stable title is the allocator class plus pool name `mbufpl`; addresses are volatile.

## Dependencies and Integration Points

This integrates OpenBSD pool allocator diagnostics with network socket receive stack capture. It protects deduplication of mbuf double-free style bugs.

## Risks and Edge Cases

Line wrapping can split `soreceive`, `recvit`, and `sys_recvfrom`, which may confuse frame extraction. The parser should not title this from generic `panic()` or from the user syscall alone.

## Test Signals

A passing test returns `pool: double put: mbufpl`, keeps a non-empty report, and includes the `m_free`/`m_freem`/`soreceive` evidence.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/2 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/20 -->
# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/20

## Purpose

This OpenBSD fixture expects `pool: cpu free list modified: mbufpl`. It captures a pool cache magic check failure for the mbuf pool during IPv4 interface address ioctl handling.

## Important APIs, Types, and Functions

Reporter behavior includes pool-cache corruption title extraction, panic parsing, DDB trace capture, and lock/malloc/pool diagnostic handling. Kernel functions include `pool_cache_get`, `pool_get`, `m_get`, `rt_ifa_del`, `in_ioctl_sifaddr`, `in_ioctl`, `ifioctl`, `sys_ioctl`, `syscall`, and `Xsyscall`.

## Control Flow

The allocator detects a modified CPU freelist item while allocating an mbuf. The stack shows route/interface address deletion in response to an ioctl, which needs an mbuf via `m_get`. DDB repeats the panic and trace, then emits locks and allocator state.

## State and Persistence Behavior

The fixture stores the corrupted item address, offset, observed and expected magic values, process metadata, locks, and allocator counters. The title uses the stable pool name `mbufpl` and corruption class, omitting volatile item and magic values.

## Dependencies and Integration Points

This integrates OpenBSD pool-cache diagnostics with networking ioctl stacks. It also tests that `show all locks` content after the crash does not override the allocator-derived title.

## Risks and Edge Cases

The detecting stack may not identify the original corruptor, so over-attributing to `in_ioctl_sifaddr` would be misleading. Numeric magic values should not enter the title. The parser must distinguish this from report 2's double put despite both involving `mbufpl`.

## Test Signals

A passing test returns `pool: cpu free list modified: mbufpl` and includes `pool_cache_item_magic_check`, `m_get`, and `in_ioctl_sifaddr` in the report.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/20 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/21 -->
# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/21

## Purpose

This OpenBSD fixture expects `panic: vop_generic_badop`, is typed `DoS`, and is marked `SUPPRESSED: Y`. It captures a VFS bad-operation panic during UFS mkdir/writeback logic.

## Important APIs, Types, and Functions

Reporter behavior includes panic-title extraction, DoS and suppressed metadata parsing, DDB repeated-trace handling, and post-crash lock context capture. Kernel functions include `vop_generic_badop`, `VOP_STRATEGY`, `bwrite`, `VOP_BWRITE`, `ufs_mkdir`, `VOP_MKDIR`, `domkdirat`, `syscall`, and `Xsyscall`; later lock stacks mention `ffs_update`, `ffs_inode_alloc`, `vfs_lookup`, and `vn_closefile`.

## Control Flow

The panic occurs when a generic bad VOP handler is invoked through `VOP_STRATEGY` while writing a buffer during `ufs_mkdir`. The syscall path is `mkdirat` through `domkdirat` and `VOP_MKDIR`. DDB repeats the trace, then `show all locks` records multiple filesystem lock acquisition stacks.

## State and Persistence Behavior

The fixture stores process metadata, VFS operation stack, lock stacks, registers, and allocator/pool diagnostics. The stable state is the panic string and VFS operation path. Suppression and DoS metadata should remain attached to the parsed report.

## Dependencies and Integration Points

This integrates OpenBSD VFS panic parsing with syzkaller suppression handling. It also tests that post-panic lock diagnostics are retained as evidence but do not change the primary panic title.

## Risks and Edge Cases

The report is suppressed despite being a panic, so consumers must preserve both facts. Generic VFS helper names can be broad; however, the expected title is the panic string, not a deeper `ufs_mkdir` title. Repeated DDB traces must not create duplicate crashes.

## Test Signals

A passing test returns `panic: vop_generic_badop`, marks `TYPE: DoS` and suppressed state, and includes the `VOP_STRATEGY` to `domkdirat` trace.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/21 -->
