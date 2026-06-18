# Research: subset-b-009501

This grouped report covers syzkaller report parser fixtures under `pkg/report/testdata/openbsd/report` and `pkg/report/testdata/starnix/report`. Each section is source-tree-aligned and intended to be split into the corresponding per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/22 -->
# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/22

Purpose: OpenBSD reporter fixture for a pool allocator integrity panic. The expected title is `pool: free list modified: mbufpl`, derived from `panic: pool_p_free: mbufpl free list modified...`.

Important parser APIs and patterns: `ctorOpenbsd` builds a BSD reporter with `openbsdOopses`. This fixture targets the `panic:` oops format whose title regex is `panic: pool_p_free: ([^:]+) free list modified`, formatted as `pool: free list modified: %[1]v`. Stack symbolization relies on OpenBSD frame text like `pool_p_free(...) at pool_p_free+0x1de`.

Control flow: the raw console starts with the panic, enters DDB, runs `show panic`, `trace`, `show registers`, and later memory/pool diagnostics. The parser should start at the panic, retain enough report text through the OpenBSD crash/debug block, and not let the trailing allocator table change the title.

State and persistence: this is a static golden test fixture. It stores no runtime state, but it preserves volatile pool page, item address, register, process, and allocator statistics to test noisy real-world logs.

Dependencies and integration: integrated with `pkg/report` golden tests for OpenBSD crash detection, title extraction, report boundaries, and frame capture.

Risks: dynamic addresses and long diagnostics can destabilize title extraction if not normalized. Boundary logic must avoid truncating before DDB output while ignoring allocator-table noise for title selection.

Test signals: title should be exactly `pool: free list modified: mbufpl`; the useful stack includes `pool_p_free`, `pool_gc_pages`, and `taskq_thread`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/22 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/23 -->
# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/23

Purpose: OpenBSD fixture for a packet-filter address-family panic. Expected title is `panic: unhandled af`; expected crash type is `DoS`.

Important parser APIs and patterns: handled by `openbsdOopses` under the `panic:` group, specifically `panic: unhandled af`, formatted without the numeric family value. `Reporter.ParseFrom` later sanitizes dynamic values and assigns `crash.Type` from the test metadata.

Control flow: the log records `panic: unhandled af 1`, DDB entry, process table row for `syz-executor6559`, and a stack through `unhandled_af`, `pf_addrcpy`, `pfioctl`, `VOP_IOCTL`, `vn_ioctl`, `sys_ioctl`, `syscall`, and `Xsyscall`. The repeated `show panic` and `trace` output confirms the panic line and stack after DDB prompt handling.

State and persistence: no mutable program state exists in this fixture. The file persists representative OpenBSD kernel state such as process IDs, register dump, and pool statistics.

Dependencies and integration: tests OpenBSD-specific panic title compaction and syzkaller’s generic dynamic-title replacement. It also validates that network/pf ioctl crashes are grouped under the stable `unhandled af` title.

Risks: if the parser captured the numeric address family, deduplication would fragment. The long trailing diagnostics also stress report-end heuristics.

Test signals: expected title `panic: unhandled af`, expected `TYPE: DoS`, and stack frame signal `unhandled_af` reached from `pfioctl`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/23 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/24 -->
# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/24

Purpose: OpenBSD kqueue invariant panic fixture. Expected title is `kqueue: knote !ACTIVE`.

Important parser APIs and patterns: `openbsdOopses` includes `panic: (kqueue|knote).* ([a-z]+ .*)` formatted as `kqueue: %[2]v`. This fixture proves that the reporter extracts the semantic invariant (`knote !ACTIVE`) from a panic line containing addresses and source line data.

Control flow: the panic begins in `kqueue_scan:879`, enters DDB on CPU 1, and the primary stack runs through `kqueue_do_check`, `kqueue_scan`, `sys_kevent`, `syscall`, and `Xsyscall`. Later DDB sections include registers, process state, locks, and allocator tables.

State and persistence: the fixture is static, but encodes concurrent executor state with multiple TIDs/CPUs and a concrete kqueue/knote pair. Those details exercise noise tolerance rather than persistent application state.

Dependencies and integration: covers the OpenBSD reporter’s kqueue/knote title formatter and BSD stack parsing. It interacts with shared title sanitization to ignore hex addresses and line numbers.

Risks: regex greediness could capture too much from `kqueue_scan:879: kq=... kn=... knote !ACTIVE`, or fail if future OpenBSD messages reorder fields. Multi-CPU DDB prompts can also affect boundaries.

Test signals: exact title `kqueue: knote !ACTIVE`; key frames are `kqueue_do_check`, `kqueue_scan`, and `sys_kevent`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/24 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/25 -->
# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/25

Purpose: Short OpenBSD kqueue fixture for a queued-state invariant. Expected title is `kqueue: knote !QUEUED`.

Important parser APIs and patterns: handled by the same `panic: (kqueue|knote).* ([a-z]+ .*)` formatter as other kqueue/knote fixtures. The source line `knote_enqueue:1276` and pointer fields should not appear in the deduplicated title.

Control flow: the panic reports `knote_enqueue:1276`, drops into DDB, and shows a compact stack: `db_enter`, `panic`, `kqueue_do_check`, `knote_enqueue`, `kqueue_register`, `sys_kevent`, `syscall`, `Xsyscall`. Unlike larger fixtures, it stops after the OpenBSD bug-report guidance, so it tests minimal but complete report extraction.

State and persistence: static testdata only. It captures two executor threads on different CPUs to preserve concurrency context for the stack.

Dependencies and integration: validates OpenBSD panic recognition and stable title formatting for a `knote_` function, not only `kqueue_` functions.

Risks: because the file is only 19 lines, an overly strict parser expecting DDB commands after the guidance block could mark it incomplete. Regex changes could include source line numbers or addresses in the title.

Test signals: exact title `kqueue: knote !QUEUED`; stack should include `knote_enqueue` and `kqueue_register`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/25 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/26 -->
# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/26

Purpose: OpenBSD socket receive panic fixture for a numeric `receive` invariant. Expected title is `soreceive NUM`.

Important parser APIs and patterns: `openbsdOopses` has `panic: receive ([0-9][a-z]*):` formatted as `soreceive %[1]v`. Shared dynamic replacement turns title digits into `NUM`, so `receive 1` becomes `soreceive NUM`.

Control flow: the panic starts in `soreceive`, runs from a `dhclient` thread through `soo_read`, `dofilereadv`, `sys_read`, `syscall`, and `Xsyscall`. DDB repeats `show panic` and `trace`, then appends registers and allocator pool data.

State and persistence: static fixture with socket address, socket type, and buffer count (`sb_cc`) captured from the kernel. These values are intentionally dynamic and should not affect title identity.

Dependencies and integration: exercises OpenBSD panic regex matching, dynamic-title sanitization, and stack extraction from DDB output. It also covers a non-syzkaller process name generated by syzkaller-triggered network activity.

Risks: the numeric suffix must be normalized but the alphanumeric form in report/27 must remain distinct. If sanitization changes before formatter application, grouping can change.

Test signals: expected title `soreceive NUM`; stack frame signal `soreceive+0x16ac`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/26 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/27 -->
# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/27

Purpose: Companion OpenBSD socket receive fixture for an alphanumeric receive invariant. Expected title is `soreceive 1a`.

Important parser APIs and patterns: uses the same `panic: receive ([0-9][a-z]*):` title rule as report/26. Because the captured token is `1a`, generic numeric replacement should not reduce it to `NUM`.

Control flow: the kernel panics in `soreceive` while `dhclient` reads from a socket. The stack is `soreceive`, `soo_read`, `dofilereadv`, `sys_read`, `syscall`, `Xsyscall`, followed by repeated DDB `show panic` and `trace`, registers, and pool statistics.

State and persistence: static fixture preserving socket pointer, socket type, mbuf pointer, and mbuf type. These values are noisy kernel state; only the receive checkpoint token is title-relevant.

Dependencies and integration: validates subtle title sanitization behavior in the OpenBSD reporter and shared report package. It proves alphanumeric invariants can remain distinct from purely numeric ones.

Risks: overly aggressive dynamic-title replacement could collapse `1a` into `NUM`, merging different socket receive invariants. Report-boundary logic must tolerate long trailing diagnostics.

Test signals: exact title `soreceive 1a`; stack includes `soreceive+0x170a`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/27 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/28 -->
# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/28

Purpose: Negative OpenBSD fixture for a non-crash `uvm_fault` substring. The file has no expected `TITLE`, so the reporter should not produce a crash report.

Important parser APIs and patterns: `openbsdOopses` recognizes `uvm_fault(` and `kernel: page fault trap` patterns, but this line is `vmx_mprotect_ept: uvm_fault returns 14, GPA=...`. It should not match the `uvm_fault\\(` start condition nor the `kernel:` fault trap title formats.

Control flow: there is no DDB entry, panic, stack, or stopped-at frame. It is a single informational line from VMX/EPT code mentioning a fault return.

State and persistence: static no-crash test input. It preserves a guest physical address as a dynamic value that should be ignored because no report is generated.

Dependencies and integration: integrates with `ContainsCrash` and `Parse` negative tests for OpenBSD. It prevents broad substring matching from treating informational fault messages as kernel crashes.

Risks: changing crash detection from strict oops headers to loose substring search could create false positives and noisy syzkaller reports.

Test signals: expected behavior is no report. Any non-nil parse result for this file is a regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/28 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/29 -->
# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/29

Purpose: OpenBSD truncated fault fixture. Expected title is `uvm_fault`; expected `CORRUPTED: Y`.

Important parser APIs and patterns: targets the `uvm_fault(` oops group. The fallback format has `title: compile("uvm_fault\\(")`, `fmt: "uvm_fault"`, and `corrupted: true` for incomplete fault reports.

Control flow: the file contains a carriage-return-prefixed `uvm_fault(...) -> e` line and a `kernel: page fault trap, code=0` line, but no `Stopped at` function or `end trace frame`. The parser should still detect a crash while marking the report corrupted.

State and persistence: static corrupted-log fixture. It captures only the faulting map address and virtual address, intentionally lacking stack or DDB state.

Dependencies and integration: validates OpenBSD CR/LF handling noted in `Reporter.ParseFrom` and the corrupted-report path in `openbsdOopses`.

Risks: if fallback matching is removed, truncated kernel faults are missed. If corruption is not marked, downstream triage may treat a low-information report as complete.

Test signals: exact title `uvm_fault`; `CORRUPTED: Y`; no frame should be required.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/29 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/3 -->
# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/3

Purpose: Minimal OpenBSD page-fault fixture with a stopped function. Expected title is `uvm_fault: vn_writechk`.

Important parser APIs and patterns: handled by the `kernel:` oops group, specifically `kernel: page fault trap, code=0.*\\nStopped at[ ]+([^\\+]+)` formatted as `uvm_fault: %[1]v`.

Control flow: the log contains a `login:` prompt, a carriage-return-prefixed `kernel: page fault trap`, and `Stopped at vn_writechk+0x13`. There is no full DDB trace, so parser success depends on the `kernel:` plus `Stopped at` title path.

State and persistence: static minimal fixture with no persistent runtime state. It preserves the exact terminal prompt and CR-prefixed lines that OpenBSD console output can emit.

Dependencies and integration: tests the OpenBSD reporter’s ability to extract a useful faulting function without a complete panic report or `uvm_fault(` line.

Risks: line-ending normalization and prefix stripping are critical. A parser that expects `uvm_fault(` or a full trace would miss this crash.

Test signals: exact title `uvm_fault: vn_writechk`; the only required frame signal is the `Stopped at vn_writechk+0x13` line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/3 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/30 -->
# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/30

Purpose: Smallest OpenBSD corrupted `uvm_fault` fixture. Expected title is `uvm_fault`; expected `CORRUPTED: Y`.

Important parser APIs and patterns: exercises the corrupted fallback in the `uvm_fault(` oops group: `title: compile("uvm_fault\\(")`, `fmt: "uvm_fault"`, `corrupted: true`.

Control flow: after metadata, the raw body contains only one carriage-return-prefixed `uvm_fault(...) -> e` line. There is no `kernel:` line, no `Stopped at`, no trace, and no DDB prompt.

State and persistence: static truncation sample. The only kernel state is the fault map/address tuple; it is not enough to identify a faulting function.

Dependencies and integration: validates that OpenBSD crash detection can still classify severely truncated output as a corrupted crash report. This protects against VM or serial-console loss around a real fault.

Risks: broadening negative filters could accidentally suppress this because it lacks full context. Conversely, the fallback must remain specific to `uvm_fault(` to avoid false positives like report/28.

Test signals: exact title `uvm_fault`; corrupted flag set; no stack requirement.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/30 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/32 -->
# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/32

Purpose: Full OpenBSD page-fault fixture with DDB trace and symbolized source locations. Expected title is `uvm_fault: pfsync_state_import`.

Important parser APIs and patterns: uses the `uvm_fault(` oops group title rule that finds `Stopped at` and formats `uvm_fault: %[1]v`. Stack symbolization/recognition uses OpenBSD frames such as `pfsync_state_import(...) at pfsync_state_import+0x10f`.

Control flow: the crash starts with `uvm_fault(...) -> e`, `kernel: page fault trap`, and `Stopped at pfsync_state_import+0x10f`. DDB then runs `show panic`, `trace`, `show registers`, `ps`, `show malloc`, and CPU trace commands. Primary execution flows from `pfsync_state_import` through `pfioctl`, vnode ioctl wrappers, and syscall.

State and persistence: static fixture containing register state (`r15` is zero at the fault), process tables, allocator statistics, and repeated CPU traces.

Dependencies and integration: tests OpenBSD fault extraction with complete DDB context and source-line-enriched stack frames.

Risks: duplicate traces and failed `machine ddbcpu` commands can confuse report-end logic. The title must select the stopped function, not later repeated stack frames.

Test signals: exact title `uvm_fault: pfsync_state_import`; stack path includes `pfioctl` and `sys_ioctl`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/32 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/33 -->
# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/33

Purpose: OpenBSD witness lock-order reversal fixture. Expected title is `witness: reversal: inode netlock`; expected `SUPPRESSED: Y`.

Important parser APIs and patterns: handled by `openbsdOopses` under `lock order reversal:`. The title regex captures first and second lock names from `1st ... inode` and `2nd ... netlock`. `ctorOpenbsd` also defines a suppression regex for witness lock-order reversals with `first seen at`.

Control flow: the log starts after SSH setup and `executing program`, reports a witness reversal, prints both lock-order histories with `#0...#10` frames, then enters DDB and traces the active CPU and other CPUs.

State and persistence: static fixture preserving lock addresses, lock names, witness history, process state, and allocator tables. It represents diagnostic state rather than a kernel panic (`show panic` says the kernel did not panic).

Dependencies and integration: tests OpenBSD witness detection, title extraction, suppression policy, and stack parsing for `#N function+offset` witness frames.

Risks: witness reports are diagnostic and can be noisy; unsuppressed handling would overreport known lock-order classes. Regex must still identify lock names despite addresses and parenthesized descriptions.

Test signals: exact title `witness: reversal: inode netlock`; `SUPPRESSED: Y`; lock history contains `witness_checkorder`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/33 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/34 -->
# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/34

Purpose: Negative OpenBSD fixture for failed DDB command automation at a login prompt. It has no expected title and should not parse as a crash.

Important parser APIs and patterns: this file is relevant to false-positive prevention in `containsCrash` and `simpleLineParser`/BSD parsing. It contains command words such as `show panic`, `show registers`, `machine ddbcpu`, and `show malloc`, but none of the OpenBSD oops headers (`panic:`, `uvm_fault(`, `kernel: page fault trap`, `witness:`, or `lock order reversal:`).

Control flow: the VM is at `OpenBSD/amd64 ... login:`. Automation sends DDB-like commands to the login prompt, receives password prompts and `Login incorrect`, and never enters DDB or emits a kernel stack.

State and persistence: static no-crash fixture preserving console interaction state only.

Dependencies and integration: protects OpenBSD report extraction from treating scripted crash-collection commands as evidence of a crash when the VM is merely at a login prompt.

Risks: command keywords are tempting anchors for boundary logic. Crash detection must be driven by oops signatures, not by diagnostic command names.

Test signals: expected result is no report. Any title, especially one inferred from `show panic`, is a regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/34 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/35 -->
# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/35

Purpose: OpenBSD witness lock-order fixture where detailed order history is missing. Expected title is `witness: reversal: lock order data missing`.

Important parser APIs and patterns: the `lock order reversal:` oops group has a special title regex for `lock order data .* missing`, formatted as `witness: reversal: lock order data missing`. This rule should take precedence over the generic two-lock-name formatter.

Control flow: the log begins with `witness: lock order reversal`, lists `fdlock` then `inode`, immediately reports both `w2 -> w1` and `w1 -> w2` data missing, then enters DDB. The stack includes `witness_checkorder`, lock acquisition functions, vnode lookup, `ktrwriteraw`, `ktrstruct`, `sys_socketpair`, and syscall. Later CPU traces and pool data follow.

State and persistence: static diagnostic fixture with lock state, process tables, and allocator statistics. It is not a panic; `show panic` says the kernel did not panic.

Dependencies and integration: validates witness special-case title extraction and BSD stack handling for diagnostic reports.

Risks: if the generic reversal regex runs first, title could become `fdlock inode`, losing the important missing-history signal. Long DDB output can also affect report boundaries.

Test signals: exact title `witness: reversal: lock order data missing`; stack includes `witness_checkorder+0x108b`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/35 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/36 -->
# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/36

Purpose: OpenBSD protection fault fixture with source-line-rich stack. Expected title is `protection_fault: ktrops`.

Important parser APIs and patterns: handled by the `kernel:` oops group rule `kernel: protection fault trap, code=0.*\\nStopped at[ ]+([^\\+]+)` formatted as `protection_fault: %[1]v`. Symbolization frame regexes consume `at function+0xoffset` lines and inline source annotations.

Control flow: a login-prefixed `kernel: protection fault trap` stops at `ktrops+0x4a`. DDB trace shows `ktrops`, `doktrace`, `sys_ktrace`, `syscall`, and `Xsyscall`, with inline references to `sys/kern/kern_ktrace.c`. Additional process, lock, malloc, and per-CPU traces follow.

State and persistence: static crash fixture retaining register values; the `rbx`/`r12` poison value `0xdead4110dead4110` is significant diagnostic context but not title material.

Dependencies and integration: tests OpenBSD protection-fault title extraction, CR/prompt tolerance, source-line stack preservation, and multi-CPU DDB output.

Risks: page-fault and protection-fault formats are similar; mixing them would misclassify this crash. The title must use `ktrops`, not later CPU-0 `kqueue_scan`.

Test signals: exact title `protection_fault: ktrops`; primary stack includes `sys_ktrace`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/36 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/37 -->
# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/37

Purpose: OpenBSD panic fixture for a corrupted-looking `vop_generic_badop` message. Expected title is `panic: vop_generic_badop`; expected type is `DoS`.

Important parser APIs and patterns: `ctorOpenbsd` suppresses exact `panic: vop_generic_badop`, but this fixture’s expected metadata does not mark it suppressed. The title is extracted through the DDB `show panic` rule: `ddb{...}> show panic ... *cpu0: vop_generic_badop ... ddb{...}> trace`, which normalizes the garbled initial panic text.

Control flow: raw panic text appears as `panic: vop_generic_bapdoapn` followed by a malformed `iStopped at`, then a stack through `vop_generic_badop`, `VOP_STRATEGY`, `bwrite`, `VOP_BWRITE`, `ufs_mkdir`, `VOP_MKDIR`, `domkdirat`, and syscall. DDB `show panic` supplies the canonical CPU panic line.

State and persistence: static fixture preserving multi-CPU panic state and a second CPU assertion. It tests recovery from partially corrupted serial output.

Dependencies and integration: exercises OpenBSD DDB panic-title extraction, DoS type metadata, and stack capture despite malformed early lines.

Risks: relying only on the first `panic:` line would produce the wrong title. Suppression matching must remain intentionally tied to full output rules.

Test signals: exact title `panic: vop_generic_badop`; stack frame `vop_generic_badop+0x1b`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/37 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/38 -->
# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/38

Purpose: Minimal OpenBSD suppressed panic fixture for a broken-pipe disconnect. Expected title is `panic: vop_generic_bclient_loop: send disconnect: Broken pipe`, expected type `DoS`, and `SUPPRESSED: Y`.

Important parser APIs and patterns: the generic `panic:` title path captures the panic text. `ctorOpenbsd` has suppression `panic:.*send disconnect: Broken pipe`, which marks this report suppressed.

Control flow: the raw body contains only `panic: vop_generic_bclient_loop: send disconnect: Broken pipe`. There is no DDB output or stack.

State and persistence: static minimal fixture. It represents a crash-like console line caused by an SSH/client disconnect condition that syzkaller should suppress.

Dependencies and integration: validates OpenBSD suppression configuration in `ctorOpenbsd`, plus generic panic detection when no stack is available.

Risks: if suppressions are changed, infrastructure disconnects could become user-visible bugs. If the parser required stack frames, this suppression case might be missed and handled as lost connection elsewhere.

Test signals: exact title and `SUPPRESSED: Y`; no stack required.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/38 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/4 -->
# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/4

Purpose: OpenBSD pool allocator fixture for `pool_do_get` freelist corruption. Expected title is `pool: free list modified: knotepl`.

Important parser APIs and patterns: handled by `openbsdOopses` `panic:` format `panic: pool_do_get: ([^:]+) free list modified`, formatted as `pool: free list modified: %[1]v`.

Control flow: panic starts with `pool_do_get: knotepl free list modified`, enters DDB, and the stack goes through `pool_do_get`, `pool_get`, `kqueue_register`, `sys_kevent`, syscall, and `Xsyscall_untramp`. The fixture includes line wrapping in `sys_kevent+0x\n207`, which tests robust frame parsing.

State and persistence: static fixture preserving allocator page/item/offset fields and executor context. Those values are dynamic and should not affect grouping.

Dependencies and integration: validates OpenBSD pool corruption formatting for allocation (`pool_do_get`) versus free paths (`pool_p_free`, `pool_do_put`).

Risks: line wrapping can disrupt frame parsing. Regex ordering must keep this specific pool title before generic panic fallback.

Test signals: exact title `pool: free list modified: knotepl`; stack includes `pool_do_get` and `kqueue_register`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/4 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/5 -->
# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/5

Purpose: Negative OpenBSD fixture for kernel relinking failure text. It has no expected title and should not parse as a crash.

Important parser APIs and patterns: `openbsdOopses` has a `kernel:` oops group with suppressing regex `reorder_kernel`, but this fixture contains only `reorder_kernel: kernel relinking failed; see ...`. It lacks `panic:`, `uvm_fault(`, `kernel: page fault trap`, `kernel: protection fault trap`, or witness signatures.

Control flow: single diagnostic line from OpenBSD kernel relinking infrastructure. No DDB prompt, stack, or stopped frame exists.

State and persistence: static no-crash fixture preserving a path to the relink log. It represents VM setup/boot noise.

Dependencies and integration: protects `ContainsCrash` from treating relinking failure as a kernel crash, while still allowing the `reorder_kernel` suppressor to filter real `kernel:` fault lines if needed.

Risks: overbroad matching on the word `kernel` could create false positives during OpenBSD boot or relink failures.

Test signals: expected behavior is no report.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/5 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/6 -->
# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/6

Purpose: OpenBSD pool double-free fixture with an explicit expected `REPORT:` subsection. Expected title is `pool: double put: lockfpl`.

Important parser APIs and patterns: handled by `panic: pool_do_put: ([^:]+): double pool_put`, formatted as `pool: double put: %[1]v`. The test also validates report-body extraction against the `REPORT:` block embedded in the fixture.

Control flow: the raw crash starts at `login: panic: pool_do_put: lockfpl: double pool_put`, stops at `db_enter`, and traces through `pool_do_put`, `pool_put`, `lf_advlock`, `VOP_ADVLOCK`, `closef`, `fdfree`, `exit1`, `sys_exit`, syscall, and `Xsyscall`. The `REPORT:` section records the expected normalized report text beginning at the login-prefixed panic.

State and persistence: static fixture containing lockf pool state, stack, and registers. CR-prefixed lines model OpenBSD console behavior.

Dependencies and integration: tests title extraction, report boundary normalization, and CR/LF cleanup in the OpenBSD reporter.

Risks: losing the `login:` prefix or mishandling CR characters can make expected report comparisons fail. Double-put and freelist-modified titles must remain distinct.

Test signals: exact title `pool: double put: lockfpl`; expected report starts with `login: panic: pool_do_put...`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/6 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/7 -->
# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/7

Purpose: Negative OpenBSD fixture combining relinking failure, login prompts, and normal syzkaller startup logs. It has no expected title.

Important parser APIs and patterns: like report/5, this protects crash detection from `reorder_kernel` text. It also includes benign fuzzer log lines (`fuzzer started`, manager dial, unsupported features) that should not affect OpenBSD report parsing.

Control flow: the console shows `reorder_kernel: kernel relinking fail`, OpenBSD login banners, an accidental `trace` at login with password failure, SSH host-key warning, and syzkaller startup messages. There is no kernel panic, DDB crash prompt, `Stopped at`, or stack.

State and persistence: static no-crash fixture representing VM boot/connection noise and fuzzer initialization state.

Dependencies and integration: integrated with `ContainsCrash` negative tests for OpenBSD. It ensures infrastructure output and syzkaller logs are ignored by kernel crash parsing.

Risks: a loose match on `trace`, `kernel`, or `relinking fail` could produce false positives, blocking fuzzing with bogus crashes.

Test signals: expected behavior is no report.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/7 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/8 -->
# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/8

Purpose: OpenBSD kernel assertion fixture in VFS buffer memory code. Expected title is `assert "pg->wire_count == NUM" failed in vfs_biomem.c`.

Important parser APIs and patterns: `openbsdOopses` has assertion title regex `panic: kernel diagnostic assertion (.+) failed: file ".*/([^"]+)`, formatted as `assert %[1]v failed in %[2]v`. Shared dynamic replacement normalizes literal `1` inside the assertion to `NUM`.

Control flow: panic reports an assertion in `vfs_biomem.c` line 329. Stack flows through `__assert`, `buf_free_pages`, `buf_dealloc_mem`, `buf_put`, `brelse`, `vinvalbuf`, `ffs_truncate`, `ufs_rmdir`, `VOP_RMDIR`, `dounlinkat`, syscall, and `Xsyscall`. Later process-table output is retained.

State and persistence: static fixture with filesystem and process state; no mutable syzkaller state. The file path and assertion expression are the key persisted semantics.

Dependencies and integration: validates assertion title extraction, basename selection from full kernel source paths, and dynamic numeric normalization.

Risks: path handling must avoid leaking manager-specific prefixes into titles. Numeric replacement inside quoted assertions must remain stable.

Test signals: exact title with `NUM`; stack includes `buf_free_pages` and `ufs_rmdir`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/8 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/9 -->
# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/9

Purpose: OpenBSD kernel assertion fixture in UVM fault unwiring. Expected title is `assert "next != NULL && next->start <= entry->end" failed in uvm_fault.c`.

Important parser APIs and patterns: uses the assertion regex in `openbsdOopses`, extracting the assertion expression and source basename from `panic: kernel diagnostic assertion ... file ".../uvm_fault.c"`.

Control flow: panic occurs in `__assert`, then `uvm_fault_unwire_locked`, `uvm_fault_unwire`, `physio`, `spec_read`, `VOP_READ`, `vn_read`, `dofilereadv`, `sys_read`, syscall, and `Xsyscall`. The log includes line wrapping inside `physio` and `dofilereadv` argument lists.

State and persistence: static fixture preserving virtual address range arguments and process context. The assertion expression is stable semantic state; addresses and syscall arguments are noisy.

Dependencies and integration: validates OpenBSD assertion parsing for UVM paths and stack parsing across wrapped lines.

Risks: if the regex is too greedy or path trimming fails, title could include manager-specific prefixes or line numbers. Wrapped frames can confuse stack extraction.

Test signals: exact assertion title; stack includes `uvm_fault_unwire_locked`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/9 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/starnix/report/0 -->
# sources/test-tools/syzkaller/pkg/report/testdata/starnix/report/0

Purpose: Starnix/Fuchsia reporter fixture for a Rust panic while starting an empty container. Expected title is `starnix kernel panic in src/starnix/kernel/runner/container.rs: failed to start container.: errno NUM, details: ENOENT (`.

Important parser APIs and patterns: Starnix uses `ctorFuchsia` because `NewReporter` maps `targets.Starnix` to the Fuchsia reporter. `starnixOopses` detects `STARNIX KERNEL PANIC`, extracts `info=panicked at ...` with file and message, and formats `starnix kernel panic in %[1]v: %[2]v`. `shortenStarnixPanicReport` keeps Rust stack/module lines and suppresses long unrelated runs.

Control flow: the log emits `STARNIX KERNEL PANIC`, an `ERROR` panic line at `container.rs:201:30`, an exit-without-code line, then Rust `WARN` panic/backtrace output. It includes ELF module BuildIDs, six deliberate `unrelated line` entries, and a long stack from Rust panic machinery to `Container::serve_outgoing_directory`, `main`, and libc startup. A `REPORT:` block records the expected shortened report.

State and persistence: static fixture preserving Fuchsia moniker/log prefixes, BuildIDs, Rust source paths, and async executor stack state.

Dependencies and integration: validates Starnix-specific title extraction, Rust backtrace frame regexes, BuildID module lines, unrelated-line retention limit, and shortened report generation.

Risks: log-prefix changes or too-aggressive unrelated-line filtering can drop useful backtrace context. Dynamic errno normalization must keep title dedup stable.

Test signals: expected title with `errno NUM`; expected report starts at `STARNIX KERNEL PANIC` and includes the stack through container startup.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/starnix/report/0 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/starnix/report/1 -->
# sources/test-tools/syzkaller/pkg/report/testdata/starnix/report/1

Purpose: Starnix/Fuchsia reporter fixture for a Rust panic in vendored route-netlink parsing. Expected title is `starnix kernel panic in third_party/rust_crates/vendor/netlink-packet-route-NUM.NUM.NUM/src/rtnl/link/nlas/link_infos.rs`.

Important parser APIs and patterns: handled by `starnixOopses` in `fuchsia.go`. The title captures the panicking source path from `info=panicked at ...` and uses shared dynamic-title replacement to normalize version `0.17.0` to `NUM.NUM.NUM`. Stack frames are matched by `starnixFramePatterns`, including prefixed frames and continuation lines.

Control flow: the log begins with route netlink socket creation, emits `STARNIX KERNEL PANIC`, panics at `link_infos.rs:1636:41` with `range end index 4 out of range for slice of length 3`, then prints module BuildIDs and a Rust backtrace. The stack moves from Rust panic hooks through slice indexing, `netlink_packet_route` parsers, `socket_netlink.rs::write`, socket sendmsg handling, syscall dispatch, and restricted executor task execution. A `REPORT:` block captures the shortened expected report.

State and persistence: static fixture preserving component monikers, thread labels, BuildIDs, Rust source paths, and a malformed netlink payload failure path.

Dependencies and integration: validates Starnix title sanitization for dependency versions, backtrace parsing with inline-style `#0.3` frames, and tolerance for unrelated component warnings inside a stack.

Risks: version normalization is important for deduplication across crate upgrades. Backtrace continuation lines without Starnix prefixes can be dropped if `shortenStarnixPanicReport` thresholds are too strict.

Test signals: exact version-normalized title; key frames include `link_infos.rs:1636`, `socket_netlink.rs:904`, and `sys_sendmsg`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/starnix/report/1 -->
