# Research: subset-b-009498

This grouped research covers NetBSD syzkaller report fixtures used by `pkg/report` parser tests. The files are not executable source code; they are canonical crash-log inputs whose title and body shape exercise NetBSD-specific oops detection, report extraction, stack symbolization, and noise trimming.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/12 -->
# sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/12

## Purpose

`sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/12` is a NetBSD crash-report fixture for syzkaller's report parser. It encodes an AddressSanitizer/KASAN panic titled `ASan: Unauthorized Access in uvm_fault_internal`, where the first panic line reports an 8-byte read from a freed pool allocation and the stack identifies `uvm_fault_internal()` as the first non-ASan kernel frame after `__asan_load8()`.

The fixture exists to prove that the NetBSD reporter can recognize an `ASan: Unauthorized Access` panic, skip sanitizer frames, derive the crash title from the following functional kernel frame, and preserve enough of the diagnostic body for deduplication and symbolization.

## Important APIs, Types, And Functions

The fixture is consumed by syzkaller's Go test harness rather than by NetBSD itself. The relevant integration points are:

- `ctorNetbsd` in `pkg/report/netbsd.go`, which registers NetBSD oops patterns and stack-line symbolization regexes.
- `netbsdOopses`, especially the `panic: ` group with title pattern `ASan: Unauthorized Access` and report pattern that captures the first stack frame after `kasan` or `__asan`.
- `ctorBSD`, `bsd.Parse`, and `bsd.Symbolize` in `pkg/report/bsd.go`, which provide the common BSD parser and stack-line symbolizer.
- `simpleLineParser` through `bsd.Parse`, which extracts a bounded report from the full VM console transcript.
- `TestReportParse`/`forEachFile` in `pkg/report/report_test.go`, which discovers numbered files under `testdata/netbsd/report`.

The NetBSD frames inside the fixture identify kernel APIs involved in the crash path: `vpanic`, `kasan_report`, `__asan_load8`, `uvm_fault_internal`, and `trap`. The later DDB dump includes process, LWP, lock, page, and pool listings, but those are diagnostic payload rather than parser APIs.

## Control Flow

The crash path represented by the fixture starts with a syzkaller executor faulting in supervisor mode. NetBSD reports a sanitizer panic, enters `vpanic`, emits a timestamped traceback, and stops in DDB at `breakpoint`. The meaningful stack sequence is:

1. `vpanic` emits the panic.
2. `kasan_report` classifies the bad access.
3. `__asan_load8` performs the checked load and detects the invalid freed-pool access.
4. `uvm_fault_internal` is the first substantive kernel frame and becomes the extracted crash-site function.
5. `trap` shows the hardware trap path that led into the fault.

After the initial traceback, the file includes the DDB prompt response with `bt`, register state, process table, lock state, page lists, and pool state. For parser behavior, the opening `TITLE:` and early panic/stack lines are the high-signal region. The long tail is intentionally noisy and validates that the parser does not lose the primary crash identity when the console contains extensive debugger output.

## State And Persistence Behavior

The fixture is static testdata. It persists only as a repository file and has no runtime mutation, external storage, or side effects. Its state-like content is captured kernel state at panic time:

- current LWP `pid 731.1` in `syz-executor.3`;
- register values, including `rip` at `breakpoint+0x5`;
- multiple syzkaller executor LWPs and system threads;
- locks initialized by `uvm_obj_init`, `amap_alloc`, and `vcache_alloc`;
- DDB page and pool snapshots.

This diagnostic state matters because report extraction must tolerate large, repetitive tables and addresses without treating later lines as separate crashes or corrupting the original title.

## Dependencies

The test fixture depends on syzkaller's report-test file convention: a leading `TITLE:` header followed by the raw console log. It is tied to NetBSD-specific output syntax:

- `panic: ASan: Unauthorized Access ...`;
- timestamped traceback lines like `[ 77.2441254]`;
- stack frames in the `function() at netbsd:function+0xoffset file:line` format;
- DDB markers such as `Stopped in pid`, `show registers`, `ps`, and lock/page/pool dumps.

The parser-side dependency is the regular expression in `ctorNetbsd` that symbolization can match: ` at netbsd:([A-Za-z0-9_]+)\+0x([0-9a-f]+)`.

## Integration Points

This file integrates with `go test ./pkg/report` through directory scanning in `forEachFile`. The expected title is embedded in the `TITLE:` header and is compared against the title produced by `Reporter.Parse`. During symbolization tests, stack lines in the report may be rewritten with source file and line information when kernel symbols are available.

The key cross-file relationship is with `pkg/report/netbsd.go`: this fixture validates the ASan branch of `netbsdOopses`, while neighboring fixtures cover other NetBSD crash classes such as lock errors, supervisor faults, MSan, and UBSan.

## Risks

The main parser risk is regex fragility. If NetBSD changes sanitizer wording, stack indentation, `netbsd:` frame formatting, or DDB prompt sequencing, this fixture may stop matching or may extract the wrong frame. The `ASan` report regex is especially sensitive to the assumption that a sanitizer frame appears before the real kernel frame.

Another risk is over-capturing. The DDB dump is very large and contains many function-looking tokens, addresses, and lock owner records. A broad parser could accidentally select a later diagnostic function instead of `uvm_fault_internal`, or include too much low-value dump output in the normalized report.

## Test Signals

The expected test signal is the title `ASan: Unauthorized Access in uvm_fault_internal`. Successful parsing means `ContainsCrash` detects the panic, `Parse` returns a non-nil report with this title, and the report body keeps the relevant sanitizer stack while ignoring unrelated boot or DDB noise. Successful symbolization means NetBSD stack lines with `netbsd:<function>+0x<offset>` remain parseable and can be expanded when symbol data exists.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/12 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/13 -->
# sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/13

## Purpose

`sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/13` is a NetBSD report fixture for a UBSan panic titled `UBSan: Undefined Behavior in route_output`. The panic describes a member access through a misaligned address for `struct rt_msghdr` in `sys/net/rtsock_shared.c:667:41`, and the stack points to `route_output()` after the UBSan type-mismatch handler.

The fixture verifies that the NetBSD reporter can distinguish full UBSan panic reports from simpler boot-time UBSan lines, skip the UBSan handler frames, and derive the crash title from the kernel function that triggered the undefined behavior.

## Important APIs, Types, And Functions

Parser-side APIs and functions involved are:

- `netbsdOopses` in `pkg/report/netbsd.go`, specifically the `UBSan: Undefined Behavior` format inside the `panic: ` oops group.
- The fallback `UBSan:` oops format, which is used by shorter UBSan messages but should not override this richer panic pattern.
- `bsd.Parse` and `simpleLineParser`, which extract the report from the full console transcript.
- `bsd.Symbolize` and `bsd.symbolizeLine`, which handle NetBSD frame lines such as `route_output() at netbsd:route_output+0x1676`.

The crash-log functions are the UBSan runtime path `HandleTypeMismatch.part.1` and `HandleTypeMismatch`, followed by networking and socket functions: `route_output`, `raw_send`, `route_send_wrapper`, `sosend`, `soo_write`, `do_filewritev.part.1`, `sys_writev`, `sys___syscall`, and `syscall`. The central data type named by the panic is `struct rt_msghdr`, whose alignment requirement is the source of the UBSan report.

## Control Flow

The represented runtime flow is a user-space syzkaller executor writing routing-socket data through `writev`. The call path moves from the syscall layer to socket output and then into routing message handling:

1. `sys___syscall`/`sys_writev` receive the write request.
2. `soo_write` and `sosend` send data through the socket layer.
3. `route_send_wrapper` and `raw_send` dispatch the raw route socket message.
4. `route_output` accesses a misaligned `struct rt_msghdr`.
5. UBSan's type-mismatch handler reports undefined behavior and panics.
6. NetBSD enters DDB, prints the stack, registers, process table, locks, pages, and related diagnostic state.

For syzkaller parsing, the decisive line is the panic line with `UBSan: Undefined Behavior`, followed by the stack segment where `route_output()` appears after `HandleTypeMismatch`. The long DDB suffix is a stress case for report bounds and duplicate-crash avoidance.

## State And Persistence Behavior

The fixture is immutable repository testdata. The captured runtime state includes:

- LWP `851.285` in `syz-executor.4`, stopped at `breakpoint+0x5`;
- the routing-socket send path's active socket lock initialized at `soinit`;
- system process listings with multiple syzkaller executor and fuzzer threads;
- locks wanted by kernel helper threads and a CPU-held spin lock;
- page-state tables emitted by `show all pages`.

No persistent application data is read or written by the fixture. Its persistence role is regression coverage for parser behavior across future syzkaller and NetBSD changes.

## Dependencies

The fixture depends on NetBSD KUBSAN diagnostic formatting. Important textual dependencies include:

- `panic: UBSan: Undefined Behavior in <file>:<line>:<col>, ...`;
- UBSan handler frames named `HandleTypeMismatch`;
- NetBSD routing stack frames with `netbsd:` offsets;
- syscall number and DDB register/table formatting.

The report parser depends on regular expressions that assume the UBSan panic includes at least one handler frame and then a subsequent function frame that can be captured as the crash site. The symbolizer depends on kernel object symbols if source-line expansion is requested.

## Integration Points

This numbered fixture is automatically included by `forEachFile` for the NetBSD target. It complements report `14`, which is a short fallback UBSan message without a full panic/stack. Together they exercise both the rich `panic: UBSan: Undefined Behavior` path and the generic `UBSan:` path in `netbsdOopses`.

The kernel-domain integration point represented by the log is NetBSD route-socket output. From the parser's perspective, the important integration is that the extracted title should name `route_output`, not the UBSan handler, syscall wrapper, or raw socket send wrapper.

## Risks

The highest risk is title misclassification. If the parser captures `HandleTypeMismatch` instead of `route_output`, syzkaller would bucket the crash under the sanitizer runtime rather than the faulty routing code. If the generic `UBSan:` fallback fires before the richer panic format, the title could degrade to `UBSan: Undefined behavior`.

The file also carries truncation and noise risks because the DDB tail contains many addresses and function-like strings. Parser changes must keep report extraction bounded enough for performance and stable deduplication, while retaining the initial stack that identifies the fault.

## Test Signals

The expected signal is `UBSan: Undefined Behavior in route_output`. Passing tests demonstrate that `Reporter.Parse` recognizes the crash, selects the richer UBSan panic format, and extracts `route_output` as the functional crash site. Symbolization coverage is present through `netbsd:<function>+0x<offset>` stack lines in the extracted report.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/13 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/14 -->
# sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/14

## Purpose

`sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/14` is a compact NetBSD UBSan report fixture. It contains the expected title `UBSan: Undefined behavior` and a single boot-time diagnostic line reporting a misaligned member access in ACPICA resource parsing: `rsaddr.c:331:22`, involving `union AML_RESOURCE`.

Unlike reports `12` and `13`, this file has no panic prefix, stack trace, DDB stop, process table, locks, or registers. Its purpose is to validate the generic NetBSD `UBSan:` detector for sanitizer output that does not include enough stack context to name a kernel function.

## Important APIs, Types, And Functions

The relevant syzkaller parser entry is the generic `UBSan:` oops in `netbsdOopses`, which has:

- header trigger `[]byte("UBSan:")`;
- title pattern `UBSan:`;
- fixed output format `UBSan: Undefined behavior`.

The runtime type named in the diagnostic is `union AML_RESOURCE`, from NetBSD's imported ACPICA code under `sys/external/bsd/acpica/dist/resources/rsaddr.c`. There are no stack frames for `bsd.symbolizeLine` to rewrite and no function name for the parser to capture.

## Control Flow

The represented control flow is intentionally minimal:

1. NetBSD emits normal boot log lines.
2. UBSan reports undefined behavior in ACPICA code at timestamp `1.000003`.
3. The syzkaller reporter sees the `UBSan:` marker and classifies the log as a crash-like report with the generic UBSan title.

There is no panic path through `vpanic`, no `HandleTypeMismatch` stack frame, and no DDB command output. The parser must therefore avoid requiring a full panic traceback before recognizing UBSan output.

## State And Persistence Behavior

The fixture is static testdata with no mutable state. The only captured runtime state is the source location and misaligned address in the UBSan message. Because no DDB state is present, this file checks the low-context edge case where a report has a sanitizer finding but lacks stack, locks, process, or register diagnostics.

## Dependencies

The file depends on the textual marker `UBSan:` and NetBSD's sanitizer wording for undefined behavior. It also depends on the testdata convention of a `TITLE:` header followed by raw log text. It does not depend on kernel symbols, stack-frame formatting, or DDB output.

The fixture is closely related to `sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/10` and `11`, which are similarly short UBSan fixtures. This file broadens that coverage to an ACPICA `union AML_RESOURCE` misalignment report.

## Integration Points

The integration point is the fallback path in `netbsdOopses`. The report is discovered by the same `forEachFile` test harness as full panic reports, but it exercises a different branch: generic UBSan detection without a crash-site function.

In kernel-domain terms, the diagnostic originates in ACPICA resource parsing rather than syscall-triggered networking or VM code. For syzkaller, that distinction is secondary because the fixture lacks stack context and intentionally buckets to the generic UBSan title.

## Risks

The main risk is false negatives if parser logic becomes too dependent on `panic:` or stack traces for NetBSD sanitizer reports. A secondary risk is false positives: a broad `UBSan:` marker can classify any UBSan boot line as a crash, so ignore rules and higher-level crash triage need to decide whether these short boot diagnostics are actionable.

Another risk is title granularity. Because this fallback title is intentionally generic, multiple distinct UBSan findings can collapse into `UBSan: Undefined behavior` when no richer stack context is available.

## Test Signals

The expected signal is the exact title `UBSan: Undefined behavior`. Passing tests show that `ContainsCrash` and `Parse` recognize a bare UBSan line and do not require stack symbolization or NetBSD DDB output. The absence of stack frames is itself a test signal: `Symbolize` should leave the report effectively unchanged.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/14 -->
