<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/209 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/209

## Purpose
This is a syzkaller Linux report-parser fixture for `WARNING: kmalloc bug in cpu_map_update_elem`. It preserves a `x86_64 BPF CPU map update path` console shape under `pkg/report/testdata/linux/report` so `TestParse` can verify that the Linux reporter extracts the expected crash title, crash type, alternative titles, panic state, and corruption state from real kernel output rather than from synthetic unit data.

## Important APIs, Types, And Functions
The file is data, not executable code. Its API surface is the fixture header contract consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, optional `FRAME`, and optional `REPORT`. At runtime the important code paths are `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, Linux oops matching, `extractDescription`, report boundary selection, frame extraction, and `crash.TitleToType`. The kernel symbols and report signatures that matter for this fixture are summarized by: warning at kvmalloc_node followed by panic_on_warn; audit lines are interleaved in the call trace; the actionable stack reaches cpu_map_update_elem and SyS_bpf.

## Control Flow
`parseReport` reads the metadata headers until the first blank line and treats the rest of `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/209` as raw console log. The Linux reporter scans the log line by line for an oops signature, strips printk prefixes or architecture-specific stack notation, ignores report-start patterns that can appear inside another report, and builds the selected `Report`. `testParseImpl` then compares the parsed title `WARNING: kmalloc bug in cpu_map_update_elem`, type `WARNING`, alt titles `none`, panic flag, corruption flag, executor information if present, and explicit report text if the file contains a `REPORT:` block.

## State And Persistence
There is no mutable runtime state in this fixture. The persistent state is the checked-in header block `TITLE: WARNING: kmalloc bug in cpu_map_update_elem; TYPE: WARNING; PANICKED: Y` plus the raw kernel log body. This file currently has 91 lines and 4940 bytes. The expected flags are PANICKED=Y, CORRUPTED=N; alternatives are `none`. Addresses, PIDs, CPU ids, device names, or syscall details may be normalized by the reporter, but the source fixture itself keeps the original console text so boundary and corruption heuristics remain testable.

## Dependencies And Integration Points
The fixture depends on syzkaller's Linux oops regex catalog, warning/KASAN/lockdep/hung-task/RCU-stall recognizers, dynamic-title sanitization, architecture-specific stack parsing, and crash type mapping. It is integrated through `TestParse`, `forEachFile("report", ...)`, target-specific reporter construction, and the surrounding Linux reporter implementation in `linux.go`. Because it lives in `testdata/linux/report`, normal Go test discovery treats it as golden input for the parser rather than as a standalone test binary.

## Risks
Parser changes can regress this file by selecting a generic helper frame, choosing a later interleaved report, missing an unprefixed or truncated architecture-specific line, changing normalized title wording, or flipping panic/corruption state. The expected non-corrupted result is part of the contract; parser changes should not over-mark this clean report as interleaved or truncated. The panicked flag should be set from panic-on-warn, fatal exception, hung-task panic, or equivalent kernel panic text. The highest-risk edits are broad changes to Linux oops ordering, `reportStartIgnores`, stack-frame filtering, and title fallback rules.

## Test Signals
The primary signal is that `go test ./pkg/report` parses this fixture into exactly the recorded metadata. For this file, useful smoke checks are: `ContainsCrash` returns true, the first stable title remains `WARNING: kmalloc bug in cpu_map_update_elem`, crash type remains `WARNING`, alt titles remain `none`, panic/corruption flags remain PANICKED=Y, CORRUPTED=N, and the selected report still includes the kernel evidence described above. Absence of a `REPORT:` block means parser-selected report boundaries are indirectly checked through metadata and generated report comparison when tests are updated.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/209 -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/21 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/21

## Purpose
This is a syzkaller Linux report-parser fixture for `BUG: unable to handle kernel NULL pointer dereference in skb_release_data`. It preserves a `minimal x86 NULL dereference` console shape under `pkg/report/testdata/linux/report` so `TestParse` can verify that the Linux reporter extracts the expected crash title, crash type, alternative titles, panic state, and corruption state from real kernel output rather than from synthetic unit data.

## Important APIs, Types, And Functions
The file is data, not executable code. Its API surface is the fixture header contract consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, optional `FRAME`, and optional `REPORT`. At runtime the important code paths are `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, Linux oops matching, `extractDescription`, report boundary selection, frame extraction, and `crash.TitleToType`. The kernel symbols and report signatures that matter for this fixture are summarized by: two-line report with no full stack; it verifies that IP-only evidence still resolves skb_release_data and that truncation is marked corrupted.

## Control Flow
`parseReport` reads the metadata headers until the first blank line and treats the rest of `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/21` as raw console log. The Linux reporter scans the log line by line for an oops signature, strips printk prefixes or architecture-specific stack notation, ignores report-start patterns that can appear inside another report, and builds the selected `Report`. `testParseImpl` then compares the parsed title `BUG: unable to handle kernel NULL pointer dereference in skb_release_data`, type `NULL-POINTER-DEREFERENCE`, alt titles `bad-access in skb_release_data`, panic flag, corruption flag, executor information if present, and explicit report text if the file contains a `REPORT:` block.

## State And Persistence
There is no mutable runtime state in this fixture. The persistent state is the checked-in header block `TITLE: BUG: unable to handle kernel NULL pointer dereference in skb_release_data; ALT: bad-access in skb_release_data; TYPE: NULL-POINTER-DEREFERENCE; CORRUPTED: Y` plus the raw kernel log body. This file currently has 7 lines and 299 bytes. The expected flags are PANICKED=N, CORRUPTED=Y; alternatives are `bad-access in skb_release_data`. Addresses, PIDs, CPU ids, device names, or syscall details may be normalized by the reporter, but the source fixture itself keeps the original console text so boundary and corruption heuristics remain testable.

## Dependencies And Integration Points
The fixture depends on syzkaller's Linux oops regex catalog, warning/KASAN/lockdep/hung-task/RCU-stall recognizers, dynamic-title sanitization, architecture-specific stack parsing, and crash type mapping. It is integrated through `TestParse`, `forEachFile("report", ...)`, target-specific reporter construction, and the surrounding Linux reporter implementation in `linux.go`. Because it lives in `testdata/linux/report`, normal Go test discovery treats it as golden input for the parser rather than as a standalone test binary.

## Risks
Parser changes can regress this file by selecting a generic helper frame, choosing a later interleaved report, missing an unprefixed or truncated architecture-specific line, changing normalized title wording, or flipping panic/corruption state. The expected corrupted flag is part of the contract; parser changes must keep rejecting unreliable frame attribution. The panicked flag should remain unset even though the log may contain severe oops or sanitizer text without a kernel panic line. The highest-risk edits are broad changes to Linux oops ordering, `reportStartIgnores`, stack-frame filtering, and title fallback rules.

## Test Signals
The primary signal is that `go test ./pkg/report` parses this fixture into exactly the recorded metadata. For this file, useful smoke checks are: `ContainsCrash` returns true, the first stable title remains `BUG: unable to handle kernel NULL pointer dereference in skb_release_data`, crash type remains `NULL-POINTER-DEREFERENCE`, alt titles remain `bad-access in skb_release_data`, panic/corruption flags remain PANICKED=N, CORRUPTED=Y, and the selected report still includes the kernel evidence described above. Absence of a `REPORT:` block means parser-selected report boundaries are indirectly checked through metadata and generated report comparison when tests are updated.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/21 -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/210 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/210

## Purpose
This is a syzkaller Linux report-parser fixture for `WARNING: ODEBUG bug in xt_free_table_info`. It preserves a `netfilter debugobjects timer free` console shape under `pkg/report/testdata/linux/report` so `TestParse` can verify that the Linux reporter extracts the expected crash title, crash type, alternative titles, panic state, and corruption state from real kernel output rather than from synthetic unit data.

## Important APIs, Types, And Functions
The file is data, not executable code. Its API surface is the fixture header contract consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, optional `FRAME`, and optional `REPORT`. At runtime the important code paths are `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, Linux oops matching, `extractDescription`, report boundary selection, frame extraction, and `crash.TitleToType`. The kernel symbols and report signatures that matter for this fixture are summarized by: ODEBUG free-active timer message precedes a debug_print_object warning; a syzkaller program dump and netfilter chatter are mixed into the report.

## Control Flow
`parseReport` reads the metadata headers until the first blank line and treats the rest of `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/210` as raw console log. The Linux reporter scans the log line by line for an oops signature, strips printk prefixes or architecture-specific stack notation, ignores report-start patterns that can appear inside another report, and builds the selected `Report`. `testParseImpl` then compares the parsed title `WARNING: ODEBUG bug in xt_free_table_info`, type `WARNING`, alt titles `none`, panic flag, corruption flag, executor information if present, and explicit report text if the file contains a `REPORT:` block.

## State And Persistence
There is no mutable runtime state in this fixture. The persistent state is the checked-in header block `TITLE: WARNING: ODEBUG bug in xt_free_table_info; TYPE: WARNING; PANICKED: Y` plus the raw kernel log body. This file currently has 94 lines and 5303 bytes. The expected flags are PANICKED=Y, CORRUPTED=N; alternatives are `none`. Addresses, PIDs, CPU ids, device names, or syscall details may be normalized by the reporter, but the source fixture itself keeps the original console text so boundary and corruption heuristics remain testable.

## Dependencies And Integration Points
The fixture depends on syzkaller's Linux oops regex catalog, warning/KASAN/lockdep/hung-task/RCU-stall recognizers, dynamic-title sanitization, architecture-specific stack parsing, and crash type mapping. It is integrated through `TestParse`, `forEachFile("report", ...)`, target-specific reporter construction, and the surrounding Linux reporter implementation in `linux.go`. Because it lives in `testdata/linux/report`, normal Go test discovery treats it as golden input for the parser rather than as a standalone test binary.

## Risks
Parser changes can regress this file by selecting a generic helper frame, choosing a later interleaved report, missing an unprefixed or truncated architecture-specific line, changing normalized title wording, or flipping panic/corruption state. The expected non-corrupted result is part of the contract; parser changes should not over-mark this clean report as interleaved or truncated. The panicked flag should be set from panic-on-warn, fatal exception, hung-task panic, or equivalent kernel panic text. The highest-risk edits are broad changes to Linux oops ordering, `reportStartIgnores`, stack-frame filtering, and title fallback rules.

## Test Signals
The primary signal is that `go test ./pkg/report` parses this fixture into exactly the recorded metadata. For this file, useful smoke checks are: `ContainsCrash` returns true, the first stable title remains `WARNING: ODEBUG bug in xt_free_table_info`, crash type remains `WARNING`, alt titles remain `none`, panic/corruption flags remain PANICKED=Y, CORRUPTED=N, and the selected report still includes the kernel evidence described above. Absence of a `REPORT:` block means parser-selected report boundaries are indirectly checked through metadata and generated report comparison when tests are updated.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/210 -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/211 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/211

## Purpose
This is a syzkaller Linux report-parser fixture for `BUG: workqueue leaked lock or atomic in addrconf_dad_work`. It preserves a `workqueue leaked lock with duplicate last-function text` console shape under `pkg/report/testdata/linux/report` so `TestParse` can verify that the Linux reporter extracts the expected crash title, crash type, alternative titles, panic state, and corruption state from real kernel output rather than from synthetic unit data.

## Important APIs, Types, And Functions
The file is data, not executable code. Its API surface is the fixture header contract consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, optional `FRAME`, and optional `REPORT`. At runtime the important code paths are `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, Linux oops matching, `extractDescription`, report boundary selection, frame extraction, and `crash.TitleToType`. The kernel symbols and report signatures that matter for this fixture are summarized by: the true last function is addrconf_dad_work while a later misleading last-function line names another symbol, protecting first-report selection.

## Control Flow
`parseReport` reads the metadata headers until the first blank line and treats the rest of `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/211` as raw console log. The Linux reporter scans the log line by line for an oops signature, strips printk prefixes or architecture-specific stack notation, ignores report-start patterns that can appear inside another report, and builds the selected `Report`. `testParseImpl` then compares the parsed title `BUG: workqueue leaked lock or atomic in addrconf_dad_work`, type `none recorded`, alt titles `none`, panic flag, corruption flag, executor information if present, and explicit report text if the file contains a `REPORT:` block.

## State And Persistence
There is no mutable runtime state in this fixture. The persistent state is the checked-in header block `TITLE: BUG: workqueue leaked lock or atomic in addrconf_dad_work` plus the raw kernel log body. This file currently has 26 lines and 1750 bytes. The expected flags are PANICKED=N, CORRUPTED=N; alternatives are `none`. Addresses, PIDs, CPU ids, device names, or syscall details may be normalized by the reporter, but the source fixture itself keeps the original console text so boundary and corruption heuristics remain testable.

## Dependencies And Integration Points
The fixture depends on syzkaller's Linux oops regex catalog, warning/KASAN/lockdep/hung-task/RCU-stall recognizers, dynamic-title sanitization, architecture-specific stack parsing, and crash type mapping. It is integrated through `TestParse`, `forEachFile("report", ...)`, target-specific reporter construction, and the surrounding Linux reporter implementation in `linux.go`. Because it lives in `testdata/linux/report`, normal Go test discovery treats it as golden input for the parser rather than as a standalone test binary.

## Risks
Parser changes can regress this file by selecting a generic helper frame, choosing a later interleaved report, missing an unprefixed or truncated architecture-specific line, changing normalized title wording, or flipping panic/corruption state. The expected non-corrupted result is part of the contract; parser changes should not over-mark this clean report as interleaved or truncated. The panicked flag should remain unset even though the log may contain severe oops or sanitizer text without a kernel panic line. The highest-risk edits are broad changes to Linux oops ordering, `reportStartIgnores`, stack-frame filtering, and title fallback rules.

## Test Signals
The primary signal is that `go test ./pkg/report` parses this fixture into exactly the recorded metadata. For this file, useful smoke checks are: `ContainsCrash` returns true, the first stable title remains `BUG: workqueue leaked lock or atomic in addrconf_dad_work`, crash type remains `none recorded`, alt titles remain `none`, panic/corruption flags remain PANICKED=N, CORRUPTED=N, and the selected report still includes the kernel evidence described above. Absence of a `REPORT:` block means parser-selected report boundaries are indirectly checked through metadata and generated report comparison when tests are updated.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/211 -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/212 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/212

## Purpose
This is a syzkaller Linux report-parser fixture for `BUG: workqueue leaked lock or atomic in addrconf_dad_work`. It preserves a `truncated workqueue leaked lock` console shape under `pkg/report/testdata/linux/report` so `TestParse` can verify that the Linux reporter extracts the expected crash title, crash type, alternative titles, panic state, and corruption state from real kernel output rather than from synthetic unit data.

## Important APIs, Types, And Functions
The file is data, not executable code. Its API surface is the fixture header contract consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, optional `FRAME`, and optional `REPORT`. At runtime the important code paths are `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, Linux oops matching, `extractDescription`, report boundary selection, frame extraction, and `crash.TitleToType`. The kernel symbols and report signatures that matter for this fixture are summarized by: shortened ipv6_addrconf worker report that still has the key last-function and Workqueue lines but lacks a complete trailing stack.

## Control Flow
`parseReport` reads the metadata headers until the first blank line and treats the rest of `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/212` as raw console log. The Linux reporter scans the log line by line for an oops signature, strips printk prefixes or architecture-specific stack notation, ignores report-start patterns that can appear inside another report, and builds the selected `Report`. `testParseImpl` then compares the parsed title `BUG: workqueue leaked lock or atomic in addrconf_dad_work`, type `none recorded`, alt titles `none`, panic flag, corruption flag, executor information if present, and explicit report text if the file contains a `REPORT:` block.

## State And Persistence
There is no mutable runtime state in this fixture. The persistent state is the checked-in header block `TITLE: BUG: workqueue leaked lock or atomic in addrconf_dad_work` plus the raw kernel log body. This file currently has 11 lines and 688 bytes. The expected flags are PANICKED=N, CORRUPTED=N; alternatives are `none`. Addresses, PIDs, CPU ids, device names, or syscall details may be normalized by the reporter, but the source fixture itself keeps the original console text so boundary and corruption heuristics remain testable.

## Dependencies And Integration Points
The fixture depends on syzkaller's Linux oops regex catalog, warning/KASAN/lockdep/hung-task/RCU-stall recognizers, dynamic-title sanitization, architecture-specific stack parsing, and crash type mapping. It is integrated through `TestParse`, `forEachFile("report", ...)`, target-specific reporter construction, and the surrounding Linux reporter implementation in `linux.go`. Because it lives in `testdata/linux/report`, normal Go test discovery treats it as golden input for the parser rather than as a standalone test binary.

## Risks
Parser changes can regress this file by selecting a generic helper frame, choosing a later interleaved report, missing an unprefixed or truncated architecture-specific line, changing normalized title wording, or flipping panic/corruption state. The expected non-corrupted result is part of the contract; parser changes should not over-mark this clean report as interleaved or truncated. The panicked flag should remain unset even though the log may contain severe oops or sanitizer text without a kernel panic line. The highest-risk edits are broad changes to Linux oops ordering, `reportStartIgnores`, stack-frame filtering, and title fallback rules.

## Test Signals
The primary signal is that `go test ./pkg/report` parses this fixture into exactly the recorded metadata. For this file, useful smoke checks are: `ContainsCrash` returns true, the first stable title remains `BUG: workqueue leaked lock or atomic in addrconf_dad_work`, crash type remains `none recorded`, alt titles remain `none`, panic/corruption flags remain PANICKED=N, CORRUPTED=N, and the selected report still includes the kernel evidence described above. Absence of a `REPORT:` block means parser-selected report boundaries are indirectly checked through metadata and generated report comparison when tests are updated.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/212 -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/213 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/213

## Purpose
This is a syzkaller Linux report-parser fixture for `KASAN: slab-out-of-bounds in rds_cong_queue_updates`. It preserves a `interleaved KASAN and warning panic` console shape under `pkg/report/testdata/linux/report` so `TestParse` can verify that the Linux reporter extracts the expected crash title, crash type, alternative titles, panic state, and corruption state from real kernel output rather than from synthetic unit data.

## Important APIs, Types, And Functions
The file is data, not executable code. Its API surface is the fixture header contract consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, optional `FRAME`, and optional `REPORT`. At runtime the important code paths are `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, Linux oops matching, `extractDescription`, report boundary selection, frame extraction, and `crash.TitleToType`. The kernel symbols and report signatures that matter for this fixture are summarized by: slab-out-of-bounds read in RDS is mixed with a compat_copy_entries warning and panic_on_warn, forcing corruption detection without losing the KASAN title.

## Control Flow
`parseReport` reads the metadata headers until the first blank line and treats the rest of `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/213` as raw console log. The Linux reporter scans the log line by line for an oops signature, strips printk prefixes or architecture-specific stack notation, ignores report-start patterns that can appear inside another report, and builds the selected `Report`. `testParseImpl` then compares the parsed title `KASAN: slab-out-of-bounds in rds_cong_queue_updates`, type `KASAN-READ`, alt titles `none`, panic flag, corruption flag, executor information if present, and explicit report text if the file contains a `REPORT:` block.

## State And Persistence
There is no mutable runtime state in this fixture. The persistent state is the checked-in header block `TITLE: KASAN: slab-out-of-bounds in rds_cong_queue_updates; TYPE: KASAN-READ; CORRUPTED: Y; PANICKED: Y` plus the raw kernel log body. This file currently has 181 lines and 9265 bytes. The expected flags are PANICKED=Y, CORRUPTED=Y; alternatives are `none`. Addresses, PIDs, CPU ids, device names, or syscall details may be normalized by the reporter, but the source fixture itself keeps the original console text so boundary and corruption heuristics remain testable.

## Dependencies And Integration Points
The fixture depends on syzkaller's Linux oops regex catalog, warning/KASAN/lockdep/hung-task/RCU-stall recognizers, dynamic-title sanitization, architecture-specific stack parsing, and crash type mapping. It is integrated through `TestParse`, `forEachFile("report", ...)`, target-specific reporter construction, and the surrounding Linux reporter implementation in `linux.go`. Because it lives in `testdata/linux/report`, normal Go test discovery treats it as golden input for the parser rather than as a standalone test binary.

## Risks
Parser changes can regress this file by selecting a generic helper frame, choosing a later interleaved report, missing an unprefixed or truncated architecture-specific line, changing normalized title wording, or flipping panic/corruption state. The expected corrupted flag is part of the contract; parser changes must keep rejecting unreliable frame attribution. The panicked flag should be set from panic-on-warn, fatal exception, hung-task panic, or equivalent kernel panic text. The highest-risk edits are broad changes to Linux oops ordering, `reportStartIgnores`, stack-frame filtering, and title fallback rules.

## Test Signals
The primary signal is that `go test ./pkg/report` parses this fixture into exactly the recorded metadata. For this file, useful smoke checks are: `ContainsCrash` returns true, the first stable title remains `KASAN: slab-out-of-bounds in rds_cong_queue_updates`, crash type remains `KASAN-READ`, alt titles remain `none`, panic/corruption flags remain PANICKED=Y, CORRUPTED=Y, and the selected report still includes the kernel evidence described above. Absence of a `REPORT:` block means parser-selected report boundaries are indirectly checked through metadata and generated report comparison when tests are updated.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/213 -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/214 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/214

## Purpose
This is a syzkaller Linux report-parser fixture for `KASAN: wild-memory-access in sg_read`. It preserves a `KASAN wild memory plus fatal exception` console shape under `pkg/report/testdata/linux/report` so `TestParse` can verify that the Linux reporter extracts the expected crash title, crash type, alternative titles, panic state, and corruption state from real kernel output rather than from synthetic unit data.

## Important APIs, Types, And Functions
The file is data, not executable code. Its API surface is the fixture header contract consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, optional `FRAME`, and optional `REPORT`. At runtime the important code paths are `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, Linux oops matching, `extractDescription`, report boundary selection, frame extraction, and `crash.TitleToType`. The kernel symbols and report signatures that matter for this fixture are summarized by: a KASAN sg_read report is interleaved with a general protection fault and fatal panic, then another CPU emits read-size and sg_read stack evidence.

## Control Flow
`parseReport` reads the metadata headers until the first blank line and treats the rest of `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/214` as raw console log. The Linux reporter scans the log line by line for an oops signature, strips printk prefixes or architecture-specific stack notation, ignores report-start patterns that can appear inside another report, and builds the selected `Report`. `testParseImpl` then compares the parsed title `KASAN: wild-memory-access in sg_read`, type `KASAN-READ`, alt titles `none`, panic flag, corruption flag, executor information if present, and explicit report text if the file contains a `REPORT:` block.

## State And Persistence
There is no mutable runtime state in this fixture. The persistent state is the checked-in header block `TITLE: KASAN: wild-memory-access in sg_read; TYPE: KASAN-READ; CORRUPTED: Y; PANICKED: Y` plus the raw kernel log body. This file currently has 101 lines and 6762 bytes. The expected flags are PANICKED=Y, CORRUPTED=Y; alternatives are `none`. Addresses, PIDs, CPU ids, device names, or syscall details may be normalized by the reporter, but the source fixture itself keeps the original console text so boundary and corruption heuristics remain testable.

## Dependencies And Integration Points
The fixture depends on syzkaller's Linux oops regex catalog, warning/KASAN/lockdep/hung-task/RCU-stall recognizers, dynamic-title sanitization, architecture-specific stack parsing, and crash type mapping. It is integrated through `TestParse`, `forEachFile("report", ...)`, target-specific reporter construction, and the surrounding Linux reporter implementation in `linux.go`. Because it lives in `testdata/linux/report`, normal Go test discovery treats it as golden input for the parser rather than as a standalone test binary.

## Risks
Parser changes can regress this file by selecting a generic helper frame, choosing a later interleaved report, missing an unprefixed or truncated architecture-specific line, changing normalized title wording, or flipping panic/corruption state. The expected corrupted flag is part of the contract; parser changes must keep rejecting unreliable frame attribution. The panicked flag should be set from panic-on-warn, fatal exception, hung-task panic, or equivalent kernel panic text. The highest-risk edits are broad changes to Linux oops ordering, `reportStartIgnores`, stack-frame filtering, and title fallback rules.

## Test Signals
The primary signal is that `go test ./pkg/report` parses this fixture into exactly the recorded metadata. For this file, useful smoke checks are: `ContainsCrash` returns true, the first stable title remains `KASAN: wild-memory-access in sg_read`, crash type remains `KASAN-READ`, alt titles remain `none`, panic/corruption flags remain PANICKED=Y, CORRUPTED=Y, and the selected report still includes the kernel evidence described above. Absence of a `REPORT:` block means parser-selected report boundaries are indirectly checked through metadata and generated report comparison when tests are updated.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/214 -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/215 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/215

## Purpose
This is a syzkaller Linux report-parser fixture for `general protection fault in ucma_close`. It preserves a `ucma close GPF through lock/workqueue teardown` console shape under `pkg/report/testdata/linux/report` so `TestParse` can verify that the Linux reporter extracts the expected crash title, crash type, alternative titles, panic state, and corruption state from real kernel output rather than from synthetic unit data.

## Important APIs, Types, And Functions
The file is data, not executable code. Its API surface is the fixture header contract consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, optional `FRAME`, and optional `REPORT`. At runtime the important code paths are `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, Linux oops matching, `extractDescription`, report boundary selection, frame extraction, and `crash.TitleToType`. The kernel symbols and report signatures that matter for this fixture are summarized by: general-protection-fault report where the RIP is a generic lockdep helper but the responsible non-ignored frame is ucma_close.

## Control Flow
`parseReport` reads the metadata headers until the first blank line and treats the rest of `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/215` as raw console log. The Linux reporter scans the log line by line for an oops signature, strips printk prefixes or architecture-specific stack notation, ignores report-start patterns that can appear inside another report, and builds the selected `Report`. `testParseImpl` then compares the parsed title `general protection fault in ucma_close`, type `DoS`, alt titles `bad-access in ucma_close`, panic flag, corruption flag, executor information if present, and explicit report text if the file contains a `REPORT:` block.

## State And Persistence
There is no mutable runtime state in this fixture. The persistent state is the checked-in header block `TITLE: general protection fault in ucma_close; ALT: bad-access in ucma_close; TYPE: DoS` plus the raw kernel log body. This file currently has 79 lines and 5285 bytes. The expected flags are PANICKED=N, CORRUPTED=N; alternatives are `bad-access in ucma_close`. Addresses, PIDs, CPU ids, device names, or syscall details may be normalized by the reporter, but the source fixture itself keeps the original console text so boundary and corruption heuristics remain testable.

## Dependencies And Integration Points
The fixture depends on syzkaller's Linux oops regex catalog, warning/KASAN/lockdep/hung-task/RCU-stall recognizers, dynamic-title sanitization, architecture-specific stack parsing, and crash type mapping. It is integrated through `TestParse`, `forEachFile("report", ...)`, target-specific reporter construction, and the surrounding Linux reporter implementation in `linux.go`. Because it lives in `testdata/linux/report`, normal Go test discovery treats it as golden input for the parser rather than as a standalone test binary.

## Risks
Parser changes can regress this file by selecting a generic helper frame, choosing a later interleaved report, missing an unprefixed or truncated architecture-specific line, changing normalized title wording, or flipping panic/corruption state. The expected non-corrupted result is part of the contract; parser changes should not over-mark this clean report as interleaved or truncated. The panicked flag should remain unset even though the log may contain severe oops or sanitizer text without a kernel panic line. The highest-risk edits are broad changes to Linux oops ordering, `reportStartIgnores`, stack-frame filtering, and title fallback rules.

## Test Signals
The primary signal is that `go test ./pkg/report` parses this fixture into exactly the recorded metadata. For this file, useful smoke checks are: `ContainsCrash` returns true, the first stable title remains `general protection fault in ucma_close`, crash type remains `DoS`, alt titles remain `bad-access in ucma_close`, panic/corruption flags remain PANICKED=N, CORRUPTED=N, and the selected report still includes the kernel evidence described above. Absence of a `REPORT:` block means parser-selected report boundaries are indirectly checked through metadata and generated report comparison when tests are updated.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/215 -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/216 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/216

## Purpose
This is a syzkaller Linux report-parser fixture for `KASAN: invalid-free in xt_free_table_info`. It preserves a `netfilter KASAN invalid-free` console shape under `pkg/report/testdata/linux/report` so `TestParse` can verify that the Linux reporter extracts the expected crash title, crash type, alternative titles, panic state, and corruption state from real kernel output rather than from synthetic unit data.

## Important APIs, Types, And Functions
The file is data, not executable code. Its API surface is the fixture header contract consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, optional `FRAME`, and optional `REPORT`. At runtime the important code paths are `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, Linux oops matching, `extractDescription`, report boundary selection, frame extraction, and `crash.TitleToType`. The kernel symbols and report signatures that matter for this fixture are summarized by: double-free/invalid-free in kvfree with xt_free_table_info in the stack plus allocation/free history and shadow memory.

## Control Flow
`parseReport` reads the metadata headers until the first blank line and treats the rest of `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/216` as raw console log. The Linux reporter scans the log line by line for an oops signature, strips printk prefixes or architecture-specific stack notation, ignores report-start patterns that can appear inside another report, and builds the selected `Report`. `testParseImpl` then compares the parsed title `KASAN: invalid-free in xt_free_table_info`, type `KASAN-INVALID-FREE`, alt titles `invalid-free in xt_free_table_info`, panic flag, corruption flag, executor information if present, and explicit report text if the file contains a `REPORT:` block.

## State And Persistence
There is no mutable runtime state in this fixture. The persistent state is the checked-in header block `TITLE: KASAN: invalid-free in xt_free_table_info; ALT: invalid-free in xt_free_table_info; TYPE: KASAN-INVALID-FREE` plus the raw kernel log body. This file currently has 100 lines and 5060 bytes. The expected flags are PANICKED=N, CORRUPTED=N; alternatives are `invalid-free in xt_free_table_info`. Addresses, PIDs, CPU ids, device names, or syscall details may be normalized by the reporter, but the source fixture itself keeps the original console text so boundary and corruption heuristics remain testable.

## Dependencies And Integration Points
The fixture depends on syzkaller's Linux oops regex catalog, warning/KASAN/lockdep/hung-task/RCU-stall recognizers, dynamic-title sanitization, architecture-specific stack parsing, and crash type mapping. It is integrated through `TestParse`, `forEachFile("report", ...)`, target-specific reporter construction, and the surrounding Linux reporter implementation in `linux.go`. Because it lives in `testdata/linux/report`, normal Go test discovery treats it as golden input for the parser rather than as a standalone test binary.

## Risks
Parser changes can regress this file by selecting a generic helper frame, choosing a later interleaved report, missing an unprefixed or truncated architecture-specific line, changing normalized title wording, or flipping panic/corruption state. The expected non-corrupted result is part of the contract; parser changes should not over-mark this clean report as interleaved or truncated. The panicked flag should remain unset even though the log may contain severe oops or sanitizer text without a kernel panic line. The highest-risk edits are broad changes to Linux oops ordering, `reportStartIgnores`, stack-frame filtering, and title fallback rules.

## Test Signals
The primary signal is that `go test ./pkg/report` parses this fixture into exactly the recorded metadata. For this file, useful smoke checks are: `ContainsCrash` returns true, the first stable title remains `KASAN: invalid-free in xt_free_table_info`, crash type remains `KASAN-INVALID-FREE`, alt titles remain `invalid-free in xt_free_table_info`, panic/corruption flags remain PANICKED=N, CORRUPTED=N, and the selected report still includes the kernel evidence described above. Absence of a `REPORT:` block means parser-selected report boundaries are indirectly checked through metadata and generated report comparison when tests are updated.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/216 -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/217 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/217

## Purpose
This is a syzkaller Linux report-parser fixture for `BUG: unable to handle kernel paging request in foo_ioctl`. It preserves a `vmalloc allocation failure fused with paging request` console shape under `pkg/report/testdata/linux/report` so `TestParse` can verify that the Linux reporter extracts the expected crash title, crash type, alternative titles, panic state, and corruption state from real kernel output rather than from synthetic unit data.

## Important APIs, Types, And Functions
The file is data, not executable code. Its API surface is the fixture header contract consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, optional `FRAME`, and optional `REPORT`. At runtime the important code paths are `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, Linux oops matching, `extractDescription`, report boundary selection, frame extraction, and `crash.TitleToType`. The kernel symbols and report signatures that matter for this fixture are summarized by: the allocation-failure message and BUG line share one physical line, validating prefix stripping and corruption marking.

## Control Flow
`parseReport` reads the metadata headers until the first blank line and treats the rest of `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/217` as raw console log. The Linux reporter scans the log line by line for an oops signature, strips printk prefixes or architecture-specific stack notation, ignores report-start patterns that can appear inside another report, and builds the selected `Report`. `testParseImpl` then compares the parsed title `BUG: unable to handle kernel paging request in foo_ioctl`, type `MEMORY_SAFETY_BUG`, alt titles `bad-access in foo_ioctl`, panic flag, corruption flag, executor information if present, and explicit report text if the file contains a `REPORT:` block.

## State And Persistence
There is no mutable runtime state in this fixture. The persistent state is the checked-in header block `TITLE: BUG: unable to handle kernel paging request in foo_ioctl; ALT: bad-access in foo_ioctl; TYPE: MEMORY_SAFETY_BUG; CORRUPTED: Y` plus the raw kernel log body. This file currently has 11 lines and 357 bytes. The expected flags are PANICKED=N, CORRUPTED=Y; alternatives are `bad-access in foo_ioctl`. Addresses, PIDs, CPU ids, device names, or syscall details may be normalized by the reporter, but the source fixture itself keeps the original console text so boundary and corruption heuristics remain testable.

## Dependencies And Integration Points
The fixture depends on syzkaller's Linux oops regex catalog, warning/KASAN/lockdep/hung-task/RCU-stall recognizers, dynamic-title sanitization, architecture-specific stack parsing, and crash type mapping. It is integrated through `TestParse`, `forEachFile("report", ...)`, target-specific reporter construction, and the surrounding Linux reporter implementation in `linux.go`. Because it lives in `testdata/linux/report`, normal Go test discovery treats it as golden input for the parser rather than as a standalone test binary.

## Risks
Parser changes can regress this file by selecting a generic helper frame, choosing a later interleaved report, missing an unprefixed or truncated architecture-specific line, changing normalized title wording, or flipping panic/corruption state. The expected corrupted flag is part of the contract; parser changes must keep rejecting unreliable frame attribution. The panicked flag should remain unset even though the log may contain severe oops or sanitizer text without a kernel panic line. The highest-risk edits are broad changes to Linux oops ordering, `reportStartIgnores`, stack-frame filtering, and title fallback rules.

## Test Signals
The primary signal is that `go test ./pkg/report` parses this fixture into exactly the recorded metadata. For this file, useful smoke checks are: `ContainsCrash` returns true, the first stable title remains `BUG: unable to handle kernel paging request in foo_ioctl`, crash type remains `MEMORY_SAFETY_BUG`, alt titles remain `bad-access in foo_ioctl`, panic/corruption flags remain PANICKED=N, CORRUPTED=Y, and the selected report still includes the kernel evidence described above. Absence of a `REPORT:` block means parser-selected report boundaries are indirectly checked through metadata and generated report comparison when tests are updated.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/217 -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/218 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/218

## Purpose
This is a syzkaller Linux report-parser fixture for `WARNING: ODEBUG bug in corrupted`. It preserves a `ODEBUG warning corrupted by allocation-failure stack` console shape under `pkg/report/testdata/linux/report` so `TestParse` can verify that the Linux reporter extracts the expected crash title, crash type, alternative titles, panic state, and corruption state from real kernel output rather than from synthetic unit data.

## Important APIs, Types, And Functions
The file is data, not executable code. Its API surface is the fixture header contract consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, optional `FRAME`, and optional `REPORT`. At runtime the important code paths are `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, Linux oops matching, `extractDescription`, report boundary selection, frame extraction, and `crash.TitleToType`. The kernel symbols and report signatures that matter for this fixture are summarized by: free-active work_struct in process_one_req is corrupted by a concurrent vmalloc allocation failure and another CPU context.

## Control Flow
`parseReport` reads the metadata headers until the first blank line and treats the rest of `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/218` as raw console log. The Linux reporter scans the log line by line for an oops signature, strips printk prefixes or architecture-specific stack notation, ignores report-start patterns that can appear inside another report, and builds the selected `Report`. `testParseImpl` then compares the parsed title `WARNING: ODEBUG bug in corrupted`, type `WARNING`, alt titles `none`, panic flag, corruption flag, executor information if present, and explicit report text if the file contains a `REPORT:` block.

## State And Persistence
There is no mutable runtime state in this fixture. The persistent state is the checked-in header block `TITLE: WARNING: ODEBUG bug in corrupted; TYPE: WARNING; CORRUPTED: Y; PANICKED: Y` plus the raw kernel log body. This file currently has 103 lines and 4966 bytes. The expected flags are PANICKED=Y, CORRUPTED=Y; alternatives are `none`. Addresses, PIDs, CPU ids, device names, or syscall details may be normalized by the reporter, but the source fixture itself keeps the original console text so boundary and corruption heuristics remain testable.

## Dependencies And Integration Points
The fixture depends on syzkaller's Linux oops regex catalog, warning/KASAN/lockdep/hung-task/RCU-stall recognizers, dynamic-title sanitization, architecture-specific stack parsing, and crash type mapping. It is integrated through `TestParse`, `forEachFile("report", ...)`, target-specific reporter construction, and the surrounding Linux reporter implementation in `linux.go`. Because it lives in `testdata/linux/report`, normal Go test discovery treats it as golden input for the parser rather than as a standalone test binary.

## Risks
Parser changes can regress this file by selecting a generic helper frame, choosing a later interleaved report, missing an unprefixed or truncated architecture-specific line, changing normalized title wording, or flipping panic/corruption state. The expected corrupted flag is part of the contract; parser changes must keep rejecting unreliable frame attribution. The panicked flag should be set from panic-on-warn, fatal exception, hung-task panic, or equivalent kernel panic text. The highest-risk edits are broad changes to Linux oops ordering, `reportStartIgnores`, stack-frame filtering, and title fallback rules.

## Test Signals
The primary signal is that `go test ./pkg/report` parses this fixture into exactly the recorded metadata. For this file, useful smoke checks are: `ContainsCrash` returns true, the first stable title remains `WARNING: ODEBUG bug in corrupted`, crash type remains `WARNING`, alt titles remain `none`, panic/corruption flags remain PANICKED=Y, CORRUPTED=Y, and the selected report still includes the kernel evidence described above. Absence of a `REPORT:` block means parser-selected report boundaries are indirectly checked through metadata and generated report comparison when tests are updated.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/218 -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/22 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/22

## Purpose
This is a syzkaller Linux report-parser fixture for `WARNING in corrupted`. It preserves a `minimal warning with missing context` console shape under `pkg/report/testdata/linux/report` so `TestParse` can verify that the Linux reporter extracts the expected crash title, crash type, alternative titles, panic state, and corruption state from real kernel output rather than from synthetic unit data.

## Important APIs, Types, And Functions
The file is data, not executable code. Its API surface is the fixture header contract consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, optional `FRAME`, and optional `REPORT`. At runtime the important code paths are `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, Linux oops matching, `extractDescription`, report boundary selection, frame extraction, and `crash.TitleToType`. The kernel symbols and report signatures that matter for this fixture are summarized by: very short warning at shm_open with only Modules line, checking generic corrupted warning fallback.

## Control Flow
`parseReport` reads the metadata headers until the first blank line and treats the rest of `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/22` as raw console log. The Linux reporter scans the log line by line for an oops signature, strips printk prefixes or architecture-specific stack notation, ignores report-start patterns that can appear inside another report, and builds the selected `Report`. `testParseImpl` then compares the parsed title `WARNING in corrupted`, type `WARNING`, alt titles `none`, panic flag, corruption flag, executor information if present, and explicit report text if the file contains a `REPORT:` block.

## State And Persistence
There is no mutable runtime state in this fixture. The persistent state is the checked-in header block `TITLE: WARNING in corrupted; TYPE: WARNING; CORRUPTED: Y` plus the raw kernel log body. This file currently has 6 lines and 182 bytes. The expected flags are PANICKED=N, CORRUPTED=Y; alternatives are `none`. Addresses, PIDs, CPU ids, device names, or syscall details may be normalized by the reporter, but the source fixture itself keeps the original console text so boundary and corruption heuristics remain testable.

## Dependencies And Integration Points
The fixture depends on syzkaller's Linux oops regex catalog, warning/KASAN/lockdep/hung-task/RCU-stall recognizers, dynamic-title sanitization, architecture-specific stack parsing, and crash type mapping. It is integrated through `TestParse`, `forEachFile("report", ...)`, target-specific reporter construction, and the surrounding Linux reporter implementation in `linux.go`. Because it lives in `testdata/linux/report`, normal Go test discovery treats it as golden input for the parser rather than as a standalone test binary.

## Risks
Parser changes can regress this file by selecting a generic helper frame, choosing a later interleaved report, missing an unprefixed or truncated architecture-specific line, changing normalized title wording, or flipping panic/corruption state. The expected corrupted flag is part of the contract; parser changes must keep rejecting unreliable frame attribution. The panicked flag should remain unset even though the log may contain severe oops or sanitizer text without a kernel panic line. The highest-risk edits are broad changes to Linux oops ordering, `reportStartIgnores`, stack-frame filtering, and title fallback rules.

## Test Signals
The primary signal is that `go test ./pkg/report` parses this fixture into exactly the recorded metadata. For this file, useful smoke checks are: `ContainsCrash` returns true, the first stable title remains `WARNING in corrupted`, crash type remains `WARNING`, alt titles remain `none`, panic/corruption flags remain PANICKED=N, CORRUPTED=Y, and the selected report still includes the kernel evidence described above. Absence of a `REPORT:` block means parser-selected report boundaries are indirectly checked through metadata and generated report comparison when tests are updated.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/22 -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/221 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/221

## Purpose
This is a syzkaller Linux report-parser fixture for `kernel panic: hung_task: blocked tasks`. It preserves a `hung-task panic` console shape under `pkg/report/testdata/linux/report` so `TestParse` can verify that the Linux reporter extracts the expected crash title, crash type, alternative titles, panic state, and corruption state from real kernel output rather than from synthetic unit data.

## Important APIs, Types, And Functions
The file is data, not executable code. Its API surface is the fixture header contract consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, optional `FRAME`, and optional `REPORT`. At runtime the important code paths are `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, Linux oops matching, `extractDescription`, report boundary selection, frame extraction, and `crash.TitleToType`. The kernel symbols and report signatures that matter for this fixture are summarized by: starts directly at Kernel panic - not syncing: hung_task and should be treated as a panicked DoS even with corrupted surrounding task context.

## Control Flow
`parseReport` reads the metadata headers until the first blank line and treats the rest of `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/221` as raw console log. The Linux reporter scans the log line by line for an oops signature, strips printk prefixes or architecture-specific stack notation, ignores report-start patterns that can appear inside another report, and builds the selected `Report`. `testParseImpl` then compares the parsed title `kernel panic: hung_task: blocked tasks`, type `DoS`, alt titles `none`, panic flag, corruption flag, executor information if present, and explicit report text if the file contains a `REPORT:` block.

## State And Persistence
There is no mutable runtime state in this fixture. The persistent state is the checked-in header block `TITLE: kernel panic: hung_task: blocked tasks; TYPE: DoS; CORRUPTED: Y; PANICKED: Y` plus the raw kernel log body. This file currently has 35 lines and 1528 bytes. The expected flags are PANICKED=Y, CORRUPTED=Y; alternatives are `none`. Addresses, PIDs, CPU ids, device names, or syscall details may be normalized by the reporter, but the source fixture itself keeps the original console text so boundary and corruption heuristics remain testable.

## Dependencies And Integration Points
The fixture depends on syzkaller's Linux oops regex catalog, warning/KASAN/lockdep/hung-task/RCU-stall recognizers, dynamic-title sanitization, architecture-specific stack parsing, and crash type mapping. It is integrated through `TestParse`, `forEachFile("report", ...)`, target-specific reporter construction, and the surrounding Linux reporter implementation in `linux.go`. Because it lives in `testdata/linux/report`, normal Go test discovery treats it as golden input for the parser rather than as a standalone test binary.

## Risks
Parser changes can regress this file by selecting a generic helper frame, choosing a later interleaved report, missing an unprefixed or truncated architecture-specific line, changing normalized title wording, or flipping panic/corruption state. The expected corrupted flag is part of the contract; parser changes must keep rejecting unreliable frame attribution. The panicked flag should be set from panic-on-warn, fatal exception, hung-task panic, or equivalent kernel panic text. The highest-risk edits are broad changes to Linux oops ordering, `reportStartIgnores`, stack-frame filtering, and title fallback rules.

## Test Signals
The primary signal is that `go test ./pkg/report` parses this fixture into exactly the recorded metadata. For this file, useful smoke checks are: `ContainsCrash` returns true, the first stable title remains `kernel panic: hung_task: blocked tasks`, crash type remains `DoS`, alt titles remain `none`, panic/corruption flags remain PANICKED=Y, CORRUPTED=Y, and the selected report still includes the kernel evidence described above. Absence of a `REPORT:` block means parser-selected report boundaries are indirectly checked through metadata and generated report comparison when tests are updated.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/221 -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/222 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/222

## Purpose
This is a syzkaller Linux report-parser fixture for `general protection fault in tipc_nametbl_unsubscribe`. It preserves a `TIPC list deletion GPF` console shape under `pkg/report/testdata/linux/report` so `TestParse` can verify that the Linux reporter extracts the expected crash title, crash type, alternative titles, panic state, and corruption state from real kernel output rather than from synthetic unit data.

## Important APIs, Types, And Functions
The file is data, not executable code. Its API surface is the fixture header contract consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, optional `FRAME`, and optional `REPORT`. At runtime the important code paths are `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, Linux oops matching, `extractDescription`, report boundary selection, frame extraction, and `crash.TitleToType`. The kernel symbols and report signatures that matter for this fixture are summarized by: generic __list_del_entry_valid RIP must be retitled to the TIPC unsubscribe frame; fatal exception in interrupt marks panic.

## Control Flow
`parseReport` reads the metadata headers until the first blank line and treats the rest of `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/222` as raw console log. The Linux reporter scans the log line by line for an oops signature, strips printk prefixes or architecture-specific stack notation, ignores report-start patterns that can appear inside another report, and builds the selected `Report`. `testParseImpl` then compares the parsed title `general protection fault in tipc_nametbl_unsubscribe`, type `DoS`, alt titles `bad-access in tipc_nametbl_unsubscribe`, panic flag, corruption flag, executor information if present, and explicit report text if the file contains a `REPORT:` block.

## State And Persistence
There is no mutable runtime state in this fixture. The persistent state is the checked-in header block `TITLE: general protection fault in tipc_nametbl_unsubscribe; ALT: bad-access in tipc_nametbl_unsubscribe; TYPE: DoS; PANICKED: Y` plus the raw kernel log body. This file currently has 140 lines and 7304 bytes. The expected flags are PANICKED=Y, CORRUPTED=N; alternatives are `bad-access in tipc_nametbl_unsubscribe`. Addresses, PIDs, CPU ids, device names, or syscall details may be normalized by the reporter, but the source fixture itself keeps the original console text so boundary and corruption heuristics remain testable.

## Dependencies And Integration Points
The fixture depends on syzkaller's Linux oops regex catalog, warning/KASAN/lockdep/hung-task/RCU-stall recognizers, dynamic-title sanitization, architecture-specific stack parsing, and crash type mapping. It is integrated through `TestParse`, `forEachFile("report", ...)`, target-specific reporter construction, and the surrounding Linux reporter implementation in `linux.go`. Because it lives in `testdata/linux/report`, normal Go test discovery treats it as golden input for the parser rather than as a standalone test binary.

## Risks
Parser changes can regress this file by selecting a generic helper frame, choosing a later interleaved report, missing an unprefixed or truncated architecture-specific line, changing normalized title wording, or flipping panic/corruption state. The expected non-corrupted result is part of the contract; parser changes should not over-mark this clean report as interleaved or truncated. The panicked flag should be set from panic-on-warn, fatal exception, hung-task panic, or equivalent kernel panic text. The highest-risk edits are broad changes to Linux oops ordering, `reportStartIgnores`, stack-frame filtering, and title fallback rules.

## Test Signals
The primary signal is that `go test ./pkg/report` parses this fixture into exactly the recorded metadata. For this file, useful smoke checks are: `ContainsCrash` returns true, the first stable title remains `general protection fault in tipc_nametbl_unsubscribe`, crash type remains `DoS`, alt titles remain `bad-access in tipc_nametbl_unsubscribe`, panic/corruption flags remain PANICKED=Y, CORRUPTED=N, and the selected report still includes the kernel evidence described above. Absence of a `REPORT:` block means parser-selected report boundaries are indirectly checked through metadata and generated report comparison when tests are updated.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/222 -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/223 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/223

## Purpose
This is a syzkaller Linux report-parser fixture for `KASAN: use-after-free Read in binder_release_work`. It preserves a `binder deferred work KASAN UAF` console shape under `pkg/report/testdata/linux/report` so `TestParse` can verify that the Linux reporter extracts the expected crash title, crash type, alternative titles, panic state, and corruption state from real kernel output rather than from synthetic unit data.

## Important APIs, Types, And Functions
The file is data, not executable code. Its API surface is the fixture header contract consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, optional `FRAME`, and optional `REPORT`. At runtime the important code paths are `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, Linux oops matching, `extractDescription`, report boundary selection, frame extraction, and `crash.TitleToType`. The kernel symbols and report signatures that matter for this fixture are summarized by: binder_release_work is derived from a __list_del_entry stack under binder_deferred_func, with binder_alloc noise glued to Workqueue text.

## Control Flow
`parseReport` reads the metadata headers until the first blank line and treats the rest of `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/223` as raw console log. The Linux reporter scans the log line by line for an oops signature, strips printk prefixes or architecture-specific stack notation, ignores report-start patterns that can appear inside another report, and builds the selected `Report`. `testParseImpl` then compares the parsed title `KASAN: use-after-free Read in binder_release_work`, type `KASAN-USE-AFTER-FREE-READ`, alt titles `bad-access in binder_release_work`, panic flag, corruption flag, executor information if present, and explicit report text if the file contains a `REPORT:` block.

## State And Persistence
There is no mutable runtime state in this fixture. The persistent state is the checked-in header block `TITLE: KASAN: use-after-free Read in binder_release_work; ALT: bad-access in binder_release_work; TYPE: KASAN-USE-AFTER-FREE-READ` plus the raw kernel log body. This file currently has 138 lines and 8442 bytes. The expected flags are PANICKED=N, CORRUPTED=N; alternatives are `bad-access in binder_release_work`. Addresses, PIDs, CPU ids, device names, or syscall details may be normalized by the reporter, but the source fixture itself keeps the original console text so boundary and corruption heuristics remain testable.

## Dependencies And Integration Points
The fixture depends on syzkaller's Linux oops regex catalog, warning/KASAN/lockdep/hung-task/RCU-stall recognizers, dynamic-title sanitization, architecture-specific stack parsing, and crash type mapping. It is integrated through `TestParse`, `forEachFile("report", ...)`, target-specific reporter construction, and the surrounding Linux reporter implementation in `linux.go`. Because it lives in `testdata/linux/report`, normal Go test discovery treats it as golden input for the parser rather than as a standalone test binary.

## Risks
Parser changes can regress this file by selecting a generic helper frame, choosing a later interleaved report, missing an unprefixed or truncated architecture-specific line, changing normalized title wording, or flipping panic/corruption state. The expected non-corrupted result is part of the contract; parser changes should not over-mark this clean report as interleaved or truncated. The panicked flag should remain unset even though the log may contain severe oops or sanitizer text without a kernel panic line. The highest-risk edits are broad changes to Linux oops ordering, `reportStartIgnores`, stack-frame filtering, and title fallback rules.

## Test Signals
The primary signal is that `go test ./pkg/report` parses this fixture into exactly the recorded metadata. For this file, useful smoke checks are: `ContainsCrash` returns true, the first stable title remains `KASAN: use-after-free Read in binder_release_work`, crash type remains `KASAN-USE-AFTER-FREE-READ`, alt titles remain `bad-access in binder_release_work`, panic/corruption flags remain PANICKED=N, CORRUPTED=N, and the selected report still includes the kernel evidence described above. Absence of a `REPORT:` block means parser-selected report boundaries are indirectly checked through metadata and generated report comparison when tests are updated.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/223 -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/224 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/224

## Purpose
This is a syzkaller Linux report-parser fixture for `general protection fault in xfrm_state_walk_done`. It preserves a `xfrm state walker list deletion GPF` console shape under `pkg/report/testdata/linux/report` so `TestParse` can verify that the Linux reporter extracts the expected crash title, crash type, alternative titles, panic state, and corruption state from real kernel output rather than from synthetic unit data.

## Important APIs, Types, And Functions
The file is data, not executable code. Its API surface is the fixture header contract consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, optional `FRAME`, and optional `REPORT`. At runtime the important code paths are `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, Linux oops matching, `extractDescription`, report boundary selection, frame extraction, and `crash.TitleToType`. The kernel symbols and report signatures that matter for this fixture are summarized by: ARM-style-free text concatenates the GPF phrase with KASAN text and panics in interrupt after list_del.

## Control Flow
`parseReport` reads the metadata headers until the first blank line and treats the rest of `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/224` as raw console log. The Linux reporter scans the log line by line for an oops signature, strips printk prefixes or architecture-specific stack notation, ignores report-start patterns that can appear inside another report, and builds the selected `Report`. `testParseImpl` then compares the parsed title `general protection fault in xfrm_state_walk_done`, type `DoS`, alt titles `bad-access in xfrm_state_walk_done`, panic flag, corruption flag, executor information if present, and explicit report text if the file contains a `REPORT:` block.

## State And Persistence
There is no mutable runtime state in this fixture. The persistent state is the checked-in header block `TITLE: general protection fault in xfrm_state_walk_done; ALT: bad-access in xfrm_state_walk_done; TYPE: DoS; PANICKED: Y` plus the raw kernel log body. This file currently has 111 lines and 8105 bytes. The expected flags are PANICKED=Y, CORRUPTED=N; alternatives are `bad-access in xfrm_state_walk_done`. Addresses, PIDs, CPU ids, device names, or syscall details may be normalized by the reporter, but the source fixture itself keeps the original console text so boundary and corruption heuristics remain testable.

## Dependencies And Integration Points
The fixture depends on syzkaller's Linux oops regex catalog, warning/KASAN/lockdep/hung-task/RCU-stall recognizers, dynamic-title sanitization, architecture-specific stack parsing, and crash type mapping. It is integrated through `TestParse`, `forEachFile("report", ...)`, target-specific reporter construction, and the surrounding Linux reporter implementation in `linux.go`. Because it lives in `testdata/linux/report`, normal Go test discovery treats it as golden input for the parser rather than as a standalone test binary.

## Risks
Parser changes can regress this file by selecting a generic helper frame, choosing a later interleaved report, missing an unprefixed or truncated architecture-specific line, changing normalized title wording, or flipping panic/corruption state. The expected non-corrupted result is part of the contract; parser changes should not over-mark this clean report as interleaved or truncated. The panicked flag should be set from panic-on-warn, fatal exception, hung-task panic, or equivalent kernel panic text. The highest-risk edits are broad changes to Linux oops ordering, `reportStartIgnores`, stack-frame filtering, and title fallback rules.

## Test Signals
The primary signal is that `go test ./pkg/report` parses this fixture into exactly the recorded metadata. For this file, useful smoke checks are: `ContainsCrash` returns true, the first stable title remains `general protection fault in xfrm_state_walk_done`, crash type remains `DoS`, alt titles remain `bad-access in xfrm_state_walk_done`, panic/corruption flags remain PANICKED=Y, CORRUPTED=N, and the selected report still includes the kernel evidence described above. Absence of a `REPORT:` block means parser-selected report boundaries are indirectly checked through metadata and generated report comparison when tests are updated.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/224 -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/225 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/225

## Purpose
This is a syzkaller Linux report-parser fixture for `KASAN: use-after-free Read in binder_release_work`. It preserves a `long binder KASAN UAF` console shape under `pkg/report/testdata/linux/report` so `TestParse` can verify that the Linux reporter extracts the expected crash title, crash type, alternative titles, panic state, and corruption state from real kernel output rather than from synthetic unit data.

## Important APIs, Types, And Functions
The file is data, not executable code. Its API surface is the fixture header contract consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, optional `FRAME`, and optional `REPORT`. At runtime the important code paths are `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, Linux oops matching, `extractDescription`, report boundary selection, frame extraction, and `crash.TitleToType`. The kernel symbols and report signatures that matter for this fixture are summarized by: large binder deferred work report with extensive allocation/free history and later binder warnings after the KASAN block.

## Control Flow
`parseReport` reads the metadata headers until the first blank line and treats the rest of `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/225` as raw console log. The Linux reporter scans the log line by line for an oops signature, strips printk prefixes or architecture-specific stack notation, ignores report-start patterns that can appear inside another report, and builds the selected `Report`. `testParseImpl` then compares the parsed title `KASAN: use-after-free Read in binder_release_work`, type `KASAN-USE-AFTER-FREE-READ`, alt titles `bad-access in binder_release_work`, panic flag, corruption flag, executor information if present, and explicit report text if the file contains a `REPORT:` block.

## State And Persistence
There is no mutable runtime state in this fixture. The persistent state is the checked-in header block `TITLE: KASAN: use-after-free Read in binder_release_work; ALT: bad-access in binder_release_work; TYPE: KASAN-USE-AFTER-FREE-READ` plus the raw kernel log body. This file currently has 398 lines and 25793 bytes. The expected flags are PANICKED=N, CORRUPTED=N; alternatives are `bad-access in binder_release_work`. Addresses, PIDs, CPU ids, device names, or syscall details may be normalized by the reporter, but the source fixture itself keeps the original console text so boundary and corruption heuristics remain testable.

## Dependencies And Integration Points
The fixture depends on syzkaller's Linux oops regex catalog, warning/KASAN/lockdep/hung-task/RCU-stall recognizers, dynamic-title sanitization, architecture-specific stack parsing, and crash type mapping. It is integrated through `TestParse`, `forEachFile("report", ...)`, target-specific reporter construction, and the surrounding Linux reporter implementation in `linux.go`. Because it lives in `testdata/linux/report`, normal Go test discovery treats it as golden input for the parser rather than as a standalone test binary.

## Risks
Parser changes can regress this file by selecting a generic helper frame, choosing a later interleaved report, missing an unprefixed or truncated architecture-specific line, changing normalized title wording, or flipping panic/corruption state. The expected non-corrupted result is part of the contract; parser changes should not over-mark this clean report as interleaved or truncated. The panicked flag should remain unset even though the log may contain severe oops or sanitizer text without a kernel panic line. The highest-risk edits are broad changes to Linux oops ordering, `reportStartIgnores`, stack-frame filtering, and title fallback rules.

## Test Signals
The primary signal is that `go test ./pkg/report` parses this fixture into exactly the recorded metadata. For this file, useful smoke checks are: `ContainsCrash` returns true, the first stable title remains `KASAN: use-after-free Read in binder_release_work`, crash type remains `KASAN-USE-AFTER-FREE-READ`, alt titles remain `bad-access in binder_release_work`, panic/corruption flags remain PANICKED=N, CORRUPTED=N, and the selected report still includes the kernel evidence described above. Absence of a `REPORT:` block means parser-selected report boundaries are indirectly checked through metadata and generated report comparison when tests are updated.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/225 -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/226 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/226

## Purpose
This is a syzkaller Linux report-parser fixture for `KASAN: use-after-free Read in rdma_listen`. It preserves a `RDMA list-add UAF` console shape under `pkg/report/testdata/linux/report` so `TestParse` can verify that the Linux reporter extracts the expected crash title, crash type, alternative titles, panic state, and corruption state from real kernel output rather than from synthetic unit data.

## Important APIs, Types, And Functions
The file is data, not executable code. Its API surface is the fixture header contract consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, optional `FRAME`, and optional `REPORT`. At runtime the important code paths are `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, Linux oops matching, `extractDescription`, report boundary selection, frame extraction, and `crash.TitleToType`. The kernel symbols and report signatures that matter for this fixture are summarized by: use-after-free in __list_add_valid where the parser must promote the RDMA listener frame instead of the list helper.

## Control Flow
`parseReport` reads the metadata headers until the first blank line and treats the rest of `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/226` as raw console log. The Linux reporter scans the log line by line for an oops signature, strips printk prefixes or architecture-specific stack notation, ignores report-start patterns that can appear inside another report, and builds the selected `Report`. `testParseImpl` then compares the parsed title `KASAN: use-after-free Read in rdma_listen`, type `KASAN-USE-AFTER-FREE-READ`, alt titles `bad-access in rdma_listen`, panic flag, corruption flag, executor information if present, and explicit report text if the file contains a `REPORT:` block.

## State And Persistence
There is no mutable runtime state in this fixture. The persistent state is the checked-in header block `TITLE: KASAN: use-after-free Read in rdma_listen; ALT: bad-access in rdma_listen; TYPE: KASAN-USE-AFTER-FREE-READ` plus the raw kernel log body. This file currently has 123 lines and 6190 bytes. The expected flags are PANICKED=N, CORRUPTED=N; alternatives are `bad-access in rdma_listen`. Addresses, PIDs, CPU ids, device names, or syscall details may be normalized by the reporter, but the source fixture itself keeps the original console text so boundary and corruption heuristics remain testable.

## Dependencies And Integration Points
The fixture depends on syzkaller's Linux oops regex catalog, warning/KASAN/lockdep/hung-task/RCU-stall recognizers, dynamic-title sanitization, architecture-specific stack parsing, and crash type mapping. It is integrated through `TestParse`, `forEachFile("report", ...)`, target-specific reporter construction, and the surrounding Linux reporter implementation in `linux.go`. Because it lives in `testdata/linux/report`, normal Go test discovery treats it as golden input for the parser rather than as a standalone test binary.

## Risks
Parser changes can regress this file by selecting a generic helper frame, choosing a later interleaved report, missing an unprefixed or truncated architecture-specific line, changing normalized title wording, or flipping panic/corruption state. The expected non-corrupted result is part of the contract; parser changes should not over-mark this clean report as interleaved or truncated. The panicked flag should remain unset even though the log may contain severe oops or sanitizer text without a kernel panic line. The highest-risk edits are broad changes to Linux oops ordering, `reportStartIgnores`, stack-frame filtering, and title fallback rules.

## Test Signals
The primary signal is that `go test ./pkg/report` parses this fixture into exactly the recorded metadata. For this file, useful smoke checks are: `ContainsCrash` returns true, the first stable title remains `KASAN: use-after-free Read in rdma_listen`, crash type remains `KASAN-USE-AFTER-FREE-READ`, alt titles remain `bad-access in rdma_listen`, panic/corruption flags remain PANICKED=N, CORRUPTED=N, and the selected report still includes the kernel evidence described above. Absence of a `REPORT:` block means parser-selected report boundaries are indirectly checked through metadata and generated report comparison when tests are updated.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/226 -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/227 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/227

## Purpose
This is a syzkaller Linux report-parser fixture for `KASAN: use-after-free Read in cma_cancel_operation`. It preserves a `RDMA CMA cancellation UAF` console shape under `pkg/report/testdata/linux/report` so `TestParse` can verify that the Linux reporter extracts the expected crash title, crash type, alternative titles, panic state, and corruption state from real kernel output rather than from synthetic unit data.

## Important APIs, Types, And Functions
The file is data, not executable code. Its API surface is the fixture header contract consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, optional `FRAME`, and optional `REPORT`. At runtime the important code paths are `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, Linux oops matching, `extractDescription`, report boundary selection, frame extraction, and `crash.TitleToType`. The kernel symbols and report signatures that matter for this fixture are summarized by: use-after-free in __list_del_entry_valid with cma_cancel_operation as the meaningful frame and full KASAN object history.

## Control Flow
`parseReport` reads the metadata headers until the first blank line and treats the rest of `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/227` as raw console log. The Linux reporter scans the log line by line for an oops signature, strips printk prefixes or architecture-specific stack notation, ignores report-start patterns that can appear inside another report, and builds the selected `Report`. `testParseImpl` then compares the parsed title `KASAN: use-after-free Read in cma_cancel_operation`, type `KASAN-USE-AFTER-FREE-READ`, alt titles `bad-access in cma_cancel_operation`, panic flag, corruption flag, executor information if present, and explicit report text if the file contains a `REPORT:` block.

## State And Persistence
There is no mutable runtime state in this fixture. The persistent state is the checked-in header block `TITLE: KASAN: use-after-free Read in cma_cancel_operation; ALT: bad-access in cma_cancel_operation; TYPE: KASAN-USE-AFTER-FREE-READ` plus the raw kernel log body. This file currently has 159 lines and 7947 bytes. The expected flags are PANICKED=N, CORRUPTED=N; alternatives are `bad-access in cma_cancel_operation`. Addresses, PIDs, CPU ids, device names, or syscall details may be normalized by the reporter, but the source fixture itself keeps the original console text so boundary and corruption heuristics remain testable.

## Dependencies And Integration Points
The fixture depends on syzkaller's Linux oops regex catalog, warning/KASAN/lockdep/hung-task/RCU-stall recognizers, dynamic-title sanitization, architecture-specific stack parsing, and crash type mapping. It is integrated through `TestParse`, `forEachFile("report", ...)`, target-specific reporter construction, and the surrounding Linux reporter implementation in `linux.go`. Because it lives in `testdata/linux/report`, normal Go test discovery treats it as golden input for the parser rather than as a standalone test binary.

## Risks
Parser changes can regress this file by selecting a generic helper frame, choosing a later interleaved report, missing an unprefixed or truncated architecture-specific line, changing normalized title wording, or flipping panic/corruption state. The expected non-corrupted result is part of the contract; parser changes should not over-mark this clean report as interleaved or truncated. The panicked flag should remain unset even though the log may contain severe oops or sanitizer text without a kernel panic line. The highest-risk edits are broad changes to Linux oops ordering, `reportStartIgnores`, stack-frame filtering, and title fallback rules.

## Test Signals
The primary signal is that `go test ./pkg/report` parses this fixture into exactly the recorded metadata. For this file, useful smoke checks are: `ContainsCrash` returns true, the first stable title remains `KASAN: use-after-free Read in cma_cancel_operation`, crash type remains `KASAN-USE-AFTER-FREE-READ`, alt titles remain `bad-access in cma_cancel_operation`, panic/corruption flags remain PANICKED=N, CORRUPTED=N, and the selected report still includes the kernel evidence described above. Absence of a `REPORT:` block means parser-selected report boundaries are indirectly checked through metadata and generated report comparison when tests are updated.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/227 -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/229 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/229

## Purpose
This is a syzkaller Linux report-parser fixture for `WARNING: kmalloc bug in corrupted`. It preserves a `corrupted kmalloc_slab warning with multiple CPUs` console shape under `pkg/report/testdata/linux/report` so `TestParse` can verify that the Linux reporter extracts the expected crash title, crash type, alternative titles, panic state, and corruption state from real kernel output rather than from synthetic unit data.

## Important APIs, Types, And Functions
The file is data, not executable code. Its API surface is the fixture header contract consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, optional `FRAME`, and optional `REPORT`. At runtime the important code paths are `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, Linux oops matching, `extractDescription`, report boundary selection, frame extraction, and `crash.TitleToType`. The kernel symbols and report signatures that matter for this fixture are summarized by: a warning/panic_on_warn is preceded and followed by other CPU call traces, so the title intentionally falls back to corrupted.

## Control Flow
`parseReport` reads the metadata headers until the first blank line and treats the rest of `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/229` as raw console log. The Linux reporter scans the log line by line for an oops signature, strips printk prefixes or architecture-specific stack notation, ignores report-start patterns that can appear inside another report, and builds the selected `Report`. `testParseImpl` then compares the parsed title `WARNING: kmalloc bug in corrupted`, type `WARNING`, alt titles `none`, panic flag, corruption flag, executor information if present, and explicit report text if the file contains a `REPORT:` block.

## State And Persistence
There is no mutable runtime state in this fixture. The persistent state is the checked-in header block `TITLE: WARNING: kmalloc bug in corrupted; TYPE: WARNING; CORRUPTED: Y; PANICKED: Y` plus the raw kernel log body. This file currently has 192 lines and 9782 bytes. The expected flags are PANICKED=Y, CORRUPTED=Y; alternatives are `none`. Addresses, PIDs, CPU ids, device names, or syscall details may be normalized by the reporter, but the source fixture itself keeps the original console text so boundary and corruption heuristics remain testable.

## Dependencies And Integration Points
The fixture depends on syzkaller's Linux oops regex catalog, warning/KASAN/lockdep/hung-task/RCU-stall recognizers, dynamic-title sanitization, architecture-specific stack parsing, and crash type mapping. It is integrated through `TestParse`, `forEachFile("report", ...)`, target-specific reporter construction, and the surrounding Linux reporter implementation in `linux.go`. Because it lives in `testdata/linux/report`, normal Go test discovery treats it as golden input for the parser rather than as a standalone test binary.

## Risks
Parser changes can regress this file by selecting a generic helper frame, choosing a later interleaved report, missing an unprefixed or truncated architecture-specific line, changing normalized title wording, or flipping panic/corruption state. The expected corrupted flag is part of the contract; parser changes must keep rejecting unreliable frame attribution. The panicked flag should be set from panic-on-warn, fatal exception, hung-task panic, or equivalent kernel panic text. The highest-risk edits are broad changes to Linux oops ordering, `reportStartIgnores`, stack-frame filtering, and title fallback rules.

## Test Signals
The primary signal is that `go test ./pkg/report` parses this fixture into exactly the recorded metadata. For this file, useful smoke checks are: `ContainsCrash` returns true, the first stable title remains `WARNING: kmalloc bug in corrupted`, crash type remains `WARNING`, alt titles remain `none`, panic/corruption flags remain PANICKED=Y, CORRUPTED=Y, and the selected report still includes the kernel evidence described above. Absence of a `REPORT:` block means parser-selected report boundaries are indirectly checked through metadata and generated report comparison when tests are updated.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/229 -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/23 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/23

## Purpose
This is a syzkaller Linux report-parser fixture for `WARNING in corrupted`. It preserves a `minimal watchdog warning` console shape under `pkg/report/testdata/linux/report` so `TestParse` can verify that the Linux reporter extracts the expected crash title, crash type, alternative titles, panic state, and corruption state from real kernel output rather than from synthetic unit data.

## Important APIs, Types, And Functions
The file is data, not executable code. Its API surface is the fixture header contract consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, optional `FRAME`, and optional `REPORT`. At runtime the important code paths are `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, Linux oops matching, `extractDescription`, report boundary selection, frame extraction, and `crash.TitleToType`. The kernel symbols and report signatures that matter for this fixture are summarized by: single-line dev_watchdog warning with no supporting stack, protecting the generic corrupted warning path.

## Control Flow
`parseReport` reads the metadata headers until the first blank line and treats the rest of `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/23` as raw console log. The Linux reporter scans the log line by line for an oops signature, strips printk prefixes or architecture-specific stack notation, ignores report-start patterns that can appear inside another report, and builds the selected `Report`. `testParseImpl` then compares the parsed title `WARNING in corrupted`, type `WARNING`, alt titles `none`, panic flag, corruption flag, executor information if present, and explicit report text if the file contains a `REPORT:` block.

## State And Persistence
There is no mutable runtime state in this fixture. The persistent state is the checked-in header block `TITLE: WARNING in corrupted; TYPE: WARNING; CORRUPTED: Y` plus the raw kernel log body. This file currently has 6 lines and 223 bytes. The expected flags are PANICKED=N, CORRUPTED=Y; alternatives are `none`. Addresses, PIDs, CPU ids, device names, or syscall details may be normalized by the reporter, but the source fixture itself keeps the original console text so boundary and corruption heuristics remain testable.

## Dependencies And Integration Points
The fixture depends on syzkaller's Linux oops regex catalog, warning/KASAN/lockdep/hung-task/RCU-stall recognizers, dynamic-title sanitization, architecture-specific stack parsing, and crash type mapping. It is integrated through `TestParse`, `forEachFile("report", ...)`, target-specific reporter construction, and the surrounding Linux reporter implementation in `linux.go`. Because it lives in `testdata/linux/report`, normal Go test discovery treats it as golden input for the parser rather than as a standalone test binary.

## Risks
Parser changes can regress this file by selecting a generic helper frame, choosing a later interleaved report, missing an unprefixed or truncated architecture-specific line, changing normalized title wording, or flipping panic/corruption state. The expected corrupted flag is part of the contract; parser changes must keep rejecting unreliable frame attribution. The panicked flag should remain unset even though the log may contain severe oops or sanitizer text without a kernel panic line. The highest-risk edits are broad changes to Linux oops ordering, `reportStartIgnores`, stack-frame filtering, and title fallback rules.

## Test Signals
The primary signal is that `go test ./pkg/report` parses this fixture into exactly the recorded metadata. For this file, useful smoke checks are: `ContainsCrash` returns true, the first stable title remains `WARNING in corrupted`, crash type remains `WARNING`, alt titles remain `none`, panic/corruption flags remain PANICKED=N, CORRUPTED=Y, and the selected report still includes the kernel evidence described above. Absence of a `REPORT:` block means parser-selected report boundaries are indirectly checked through metadata and generated report comparison when tests are updated.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/23 -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/230 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/230

## Purpose
This is a syzkaller Linux report-parser fixture for `WARNING: kmalloc bug in corrupted`. It preserves a `kmalloc_slab warning with trailing foreign stack` console shape under `pkg/report/testdata/linux/report` so `TestParse` can verify that the Linux reporter extracts the expected crash title, crash type, alternative titles, panic state, and corruption state from real kernel output rather than from synthetic unit data.

## Important APIs, Types, And Functions
The file is data, not executable code. Its API surface is the fixture header contract consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, optional `FRAME`, and optional `REPORT`. At runtime the important code paths are `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, Linux oops matching, `extractDescription`, report boundary selection, frame extraction, and `crash.TitleToType`. The kernel symbols and report signatures that matter for this fixture are summarized by: panic_on_warn report for kmalloc_slab plus another CPU's syscall trace after the main panic report.

## Control Flow
`parseReport` reads the metadata headers until the first blank line and treats the rest of `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/230` as raw console log. The Linux reporter scans the log line by line for an oops signature, strips printk prefixes or architecture-specific stack notation, ignores report-start patterns that can appear inside another report, and builds the selected `Report`. `testParseImpl` then compares the parsed title `WARNING: kmalloc bug in corrupted`, type `WARNING`, alt titles `none`, panic flag, corruption flag, executor information if present, and explicit report text if the file contains a `REPORT:` block.

## State And Persistence
There is no mutable runtime state in this fixture. The persistent state is the checked-in header block `TITLE: WARNING: kmalloc bug in corrupted; TYPE: WARNING; CORRUPTED: Y; PANICKED: Y` plus the raw kernel log body. This file currently has 164 lines and 8115 bytes. The expected flags are PANICKED=Y, CORRUPTED=Y; alternatives are `none`. Addresses, PIDs, CPU ids, device names, or syscall details may be normalized by the reporter, but the source fixture itself keeps the original console text so boundary and corruption heuristics remain testable.

## Dependencies And Integration Points
The fixture depends on syzkaller's Linux oops regex catalog, warning/KASAN/lockdep/hung-task/RCU-stall recognizers, dynamic-title sanitization, architecture-specific stack parsing, and crash type mapping. It is integrated through `TestParse`, `forEachFile("report", ...)`, target-specific reporter construction, and the surrounding Linux reporter implementation in `linux.go`. Because it lives in `testdata/linux/report`, normal Go test discovery treats it as golden input for the parser rather than as a standalone test binary.

## Risks
Parser changes can regress this file by selecting a generic helper frame, choosing a later interleaved report, missing an unprefixed or truncated architecture-specific line, changing normalized title wording, or flipping panic/corruption state. The expected corrupted flag is part of the contract; parser changes must keep rejecting unreliable frame attribution. The panicked flag should be set from panic-on-warn, fatal exception, hung-task panic, or equivalent kernel panic text. The highest-risk edits are broad changes to Linux oops ordering, `reportStartIgnores`, stack-frame filtering, and title fallback rules.

## Test Signals
The primary signal is that `go test ./pkg/report` parses this fixture into exactly the recorded metadata. For this file, useful smoke checks are: `ContainsCrash` returns true, the first stable title remains `WARNING: kmalloc bug in corrupted`, crash type remains `WARNING`, alt titles remain `none`, panic/corruption flags remain PANICKED=Y, CORRUPTED=Y, and the selected report still includes the kernel evidence described above. Absence of a `REPORT:` block means parser-selected report boundaries are indirectly checked through metadata and generated report comparison when tests are updated.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/230 -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/231 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/231

## Purpose
This is a syzkaller Linux report-parser fixture for `WARNING: kmalloc bug in corrupted`. It preserves a `kmalloc_slab warning corrupted by vmalloc failure` console shape under `pkg/report/testdata/linux/report` so `TestParse` can verify that the Linux reporter extracts the expected crash title, crash type, alternative titles, panic state, and corruption state from real kernel output rather than from synthetic unit data.

## Important APIs, Types, And Functions
The file is data, not executable code. Its API surface is the fixture header contract consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, optional `FRAME`, and optional `REPORT`. At runtime the important code paths are `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, Linux oops matching, `extractDescription`, report boundary selection, frame extraction, and `crash.TitleToType`. The kernel symbols and report signatures that matter for this fixture are summarized by: same kmalloc warning class, with vmalloc allocation failure stack interleaved before the main CPU context completes.

## Control Flow
`parseReport` reads the metadata headers until the first blank line and treats the rest of `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/231` as raw console log. The Linux reporter scans the log line by line for an oops signature, strips printk prefixes or architecture-specific stack notation, ignores report-start patterns that can appear inside another report, and builds the selected `Report`. `testParseImpl` then compares the parsed title `WARNING: kmalloc bug in corrupted`, type `WARNING`, alt titles `none`, panic flag, corruption flag, executor information if present, and explicit report text if the file contains a `REPORT:` block.

## State And Persistence
There is no mutable runtime state in this fixture. The persistent state is the checked-in header block `TITLE: WARNING: kmalloc bug in corrupted; TYPE: WARNING; CORRUPTED: Y; PANICKED: Y` plus the raw kernel log body. This file currently has 168 lines and 8396 bytes. The expected flags are PANICKED=Y, CORRUPTED=Y; alternatives are `none`. Addresses, PIDs, CPU ids, device names, or syscall details may be normalized by the reporter, but the source fixture itself keeps the original console text so boundary and corruption heuristics remain testable.

## Dependencies And Integration Points
The fixture depends on syzkaller's Linux oops regex catalog, warning/KASAN/lockdep/hung-task/RCU-stall recognizers, dynamic-title sanitization, architecture-specific stack parsing, and crash type mapping. It is integrated through `TestParse`, `forEachFile("report", ...)`, target-specific reporter construction, and the surrounding Linux reporter implementation in `linux.go`. Because it lives in `testdata/linux/report`, normal Go test discovery treats it as golden input for the parser rather than as a standalone test binary.

## Risks
Parser changes can regress this file by selecting a generic helper frame, choosing a later interleaved report, missing an unprefixed or truncated architecture-specific line, changing normalized title wording, or flipping panic/corruption state. The expected corrupted flag is part of the contract; parser changes must keep rejecting unreliable frame attribution. The panicked flag should be set from panic-on-warn, fatal exception, hung-task panic, or equivalent kernel panic text. The highest-risk edits are broad changes to Linux oops ordering, `reportStartIgnores`, stack-frame filtering, and title fallback rules.

## Test Signals
The primary signal is that `go test ./pkg/report` parses this fixture into exactly the recorded metadata. For this file, useful smoke checks are: `ContainsCrash` returns true, the first stable title remains `WARNING: kmalloc bug in corrupted`, crash type remains `WARNING`, alt titles remain `none`, panic/corruption flags remain PANICKED=Y, CORRUPTED=Y, and the selected report still includes the kernel evidence described above. Absence of a `REPORT:` block means parser-selected report boundaries are indirectly checked through metadata and generated report comparison when tests are updated.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/231 -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/233 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/233

## Purpose
This is a syzkaller Linux report-parser fixture for `unregister_netdevice: waiting for DEV to become free`. It preserves a `netdevice unregister wait` console shape under `pkg/report/testdata/linux/report` so `TestParse` can verify that the Linux reporter extracts the expected crash title, crash type, alternative titles, panic state, and corruption state from real kernel output rather than from synthetic unit data.

## Important APIs, Types, And Functions
The file is data, not executable code. Its API surface is the fixture header contract consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, optional `FRAME`, and optional `REPORT`. At runtime the important code paths are `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, Linux oops matching, `extractDescription`, report boundary selection, frame extraction, and `crash.TitleToType`. The kernel symbols and report signatures that matter for this fixture are summarized by: four-line fixture for unregister_netdevice waiting messages, requiring device-name normalization to DEV.

## Control Flow
`parseReport` reads the metadata headers until the first blank line and treats the rest of `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/233` as raw console log. The Linux reporter scans the log line by line for an oops signature, strips printk prefixes or architecture-specific stack notation, ignores report-start patterns that can appear inside another report, and builds the selected `Report`. `testParseImpl` then compares the parsed title `unregister_netdevice: waiting for DEV to become free`, type `DoS`, alt titles `none`, panic flag, corruption flag, executor information if present, and explicit report text if the file contains a `REPORT:` block.

## State And Persistence
There is no mutable runtime state in this fixture. The persistent state is the checked-in header block `TITLE: unregister_netdevice: waiting for DEV to become free; TYPE: DoS` plus the raw kernel log body. This file currently has 4 lines and 155 bytes. The expected flags are PANICKED=N, CORRUPTED=N; alternatives are `none`. Addresses, PIDs, CPU ids, device names, or syscall details may be normalized by the reporter, but the source fixture itself keeps the original console text so boundary and corruption heuristics remain testable.

## Dependencies And Integration Points
The fixture depends on syzkaller's Linux oops regex catalog, warning/KASAN/lockdep/hung-task/RCU-stall recognizers, dynamic-title sanitization, architecture-specific stack parsing, and crash type mapping. It is integrated through `TestParse`, `forEachFile("report", ...)`, target-specific reporter construction, and the surrounding Linux reporter implementation in `linux.go`. Because it lives in `testdata/linux/report`, normal Go test discovery treats it as golden input for the parser rather than as a standalone test binary.

## Risks
Parser changes can regress this file by selecting a generic helper frame, choosing a later interleaved report, missing an unprefixed or truncated architecture-specific line, changing normalized title wording, or flipping panic/corruption state. The expected non-corrupted result is part of the contract; parser changes should not over-mark this clean report as interleaved or truncated. The panicked flag should remain unset even though the log may contain severe oops or sanitizer text without a kernel panic line. The highest-risk edits are broad changes to Linux oops ordering, `reportStartIgnores`, stack-frame filtering, and title fallback rules.

## Test Signals
The primary signal is that `go test ./pkg/report` parses this fixture into exactly the recorded metadata. For this file, useful smoke checks are: `ContainsCrash` returns true, the first stable title remains `unregister_netdevice: waiting for DEV to become free`, crash type remains `DoS`, alt titles remain `none`, panic/corruption flags remain PANICKED=N, CORRUPTED=N, and the selected report still includes the kernel evidence described above. Absence of a `REPORT:` block means parser-selected report boundaries are indirectly checked through metadata and generated report comparison when tests are updated.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/233 -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/234 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/234

## Purpose
This is a syzkaller Linux report-parser fixture for `possible deadlock in rtnl_lock`. It preserves a `recursive rtnl locking` console shape under `pkg/report/testdata/linux/report` so `TestParse` can verify that the Linux reporter extracts the expected crash title, crash type, alternative titles, panic state, and corruption state from real kernel output rather than from synthetic unit data.

## Important APIs, Types, And Functions
The file is data, not executable code. Its API surface is the fixture header contract consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, optional `FRAME`, and optional `REPORT`. At runtime the important code paths are `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, Linux oops matching, `extractDescription`, report boundary selection, frame extraction, and `crash.TitleToType`. The kernel symbols and report signatures that matter for this fixture are summarized by: lockdep possible recursive locking report where title extraction should resolve rtnl_lock from the held/requested lock stack.

## Control Flow
`parseReport` reads the metadata headers until the first blank line and treats the rest of `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/234` as raw console log. The Linux reporter scans the log line by line for an oops signature, strips printk prefixes or architecture-specific stack notation, ignores report-start patterns that can appear inside another report, and builds the selected `Report`. `testParseImpl` then compares the parsed title `possible deadlock in rtnl_lock`, type `LOCKDEP`, alt titles `none`, panic flag, corruption flag, executor information if present, and explicit report text if the file contains a `REPORT:` block.

## State And Persistence
There is no mutable runtime state in this fixture. The persistent state is the checked-in header block `TITLE: possible deadlock in rtnl_lock; TYPE: LOCKDEP` plus the raw kernel log body. This file currently has 149 lines and 7007 bytes. The expected flags are PANICKED=N, CORRUPTED=N; alternatives are `none`. Addresses, PIDs, CPU ids, device names, or syscall details may be normalized by the reporter, but the source fixture itself keeps the original console text so boundary and corruption heuristics remain testable.

## Dependencies And Integration Points
The fixture depends on syzkaller's Linux oops regex catalog, warning/KASAN/lockdep/hung-task/RCU-stall recognizers, dynamic-title sanitization, architecture-specific stack parsing, and crash type mapping. It is integrated through `TestParse`, `forEachFile("report", ...)`, target-specific reporter construction, and the surrounding Linux reporter implementation in `linux.go`. Because it lives in `testdata/linux/report`, normal Go test discovery treats it as golden input for the parser rather than as a standalone test binary.

## Risks
Parser changes can regress this file by selecting a generic helper frame, choosing a later interleaved report, missing an unprefixed or truncated architecture-specific line, changing normalized title wording, or flipping panic/corruption state. The expected non-corrupted result is part of the contract; parser changes should not over-mark this clean report as interleaved or truncated. The panicked flag should remain unset even though the log may contain severe oops or sanitizer text without a kernel panic line. The highest-risk edits are broad changes to Linux oops ordering, `reportStartIgnores`, stack-frame filtering, and title fallback rules.

## Test Signals
The primary signal is that `go test ./pkg/report` parses this fixture into exactly the recorded metadata. For this file, useful smoke checks are: `ContainsCrash` returns true, the first stable title remains `possible deadlock in rtnl_lock`, crash type remains `LOCKDEP`, alt titles remain `none`, panic/corruption flags remain PANICKED=N, CORRUPTED=N, and the selected report still includes the kernel evidence described above. Absence of a `REPORT:` block means parser-selected report boundaries are indirectly checked through metadata and generated report comparison when tests are updated.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/234 -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/235 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/235

## Purpose
This is a syzkaller Linux report-parser fixture for `INFO: task hung in corrupted`. It preserves a `hung task corrupted by multiple executor stacks` console shape under `pkg/report/testdata/linux/report` so `TestParse` can verify that the Linux reporter extracts the expected crash title, crash type, alternative titles, panic state, and corruption state from real kernel output rather than from synthetic unit data.

## Important APIs, Types, And Functions
The file is data, not executable code. Its API surface is the fixture header contract consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, optional `FRAME`, and optional `REPORT`. At runtime the important code paths are `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, Linux oops matching, `extractDescription`, report boundary selection, frame extraction, and `crash.TitleToType`. The kernel symbols and report signatures that matter for this fixture are summarized by: khungtaskd, executor traces, a native_write_msr frame, and final panic_on_hung_task are interleaved, so the title remains corrupted.

## Control Flow
`parseReport` reads the metadata headers until the first blank line and treats the rest of `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/235` as raw console log. The Linux reporter scans the log line by line for an oops signature, strips printk prefixes or architecture-specific stack notation, ignores report-start patterns that can appear inside another report, and builds the selected `Report`. `testParseImpl` then compares the parsed title `INFO: task hung in corrupted`, type `HANG`, alt titles `hang in corrupted`, panic flag, corruption flag, executor information if present, and explicit report text if the file contains a `REPORT:` block.

## State And Persistence
There is no mutable runtime state in this fixture. The persistent state is the checked-in header block `TITLE: INFO: task hung in corrupted; ALT: hang in corrupted; TYPE: HANG; CORRUPTED: Y; PANICKED: Y` plus the raw kernel log body. This file currently has 642 lines and 34654 bytes. The expected flags are PANICKED=Y, CORRUPTED=Y; alternatives are `hang in corrupted`. Addresses, PIDs, CPU ids, device names, or syscall details may be normalized by the reporter, but the source fixture itself keeps the original console text so boundary and corruption heuristics remain testable.

## Dependencies And Integration Points
The fixture depends on syzkaller's Linux oops regex catalog, warning/KASAN/lockdep/hung-task/RCU-stall recognizers, dynamic-title sanitization, architecture-specific stack parsing, and crash type mapping. It is integrated through `TestParse`, `forEachFile("report", ...)`, target-specific reporter construction, and the surrounding Linux reporter implementation in `linux.go`. Because it lives in `testdata/linux/report`, normal Go test discovery treats it as golden input for the parser rather than as a standalone test binary.

## Risks
Parser changes can regress this file by selecting a generic helper frame, choosing a later interleaved report, missing an unprefixed or truncated architecture-specific line, changing normalized title wording, or flipping panic/corruption state. The expected corrupted flag is part of the contract; parser changes must keep rejecting unreliable frame attribution. The panicked flag should be set from panic-on-warn, fatal exception, hung-task panic, or equivalent kernel panic text. The highest-risk edits are broad changes to Linux oops ordering, `reportStartIgnores`, stack-frame filtering, and title fallback rules.

## Test Signals
The primary signal is that `go test ./pkg/report` parses this fixture into exactly the recorded metadata. For this file, useful smoke checks are: `ContainsCrash` returns true, the first stable title remains `INFO: task hung in corrupted`, crash type remains `HANG`, alt titles remain `hang in corrupted`, panic/corruption flags remain PANICKED=Y, CORRUPTED=Y, and the selected report still includes the kernel evidence described above. Absence of a `REPORT:` block means parser-selected report boundaries are indirectly checked through metadata and generated report comparison when tests are updated.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/235 -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/236 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/236

## Purpose
This is a syzkaller Linux report-parser fixture for `WARNING in corrupted`. It preserves a `ARM i2c warning` console shape under `pkg/report/testdata/linux/report` so `TestParse` can verify that the Linux reporter extracts the expected crash title, crash type, alternative titles, panic state, and corruption state from real kernel output rather than from synthetic unit data.

## Important APIs, Types, And Functions
The file is data, not executable code. Its API surface is the fixture header contract consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, optional `FRAME`, and optional `REPORT`. At runtime the important code paths are `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, Linux oops matching, `extractDescription`, report boundary selection, frame extraction, and `crash.TitleToType`. The kernel symbols and report signatures that matter for this fixture are summarized by: ARM console report without bracketed printk prefixes; warning in __i2c_transfer panics on warn and uses ARM frame notation.

## Control Flow
`parseReport` reads the metadata headers until the first blank line and treats the rest of `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/236` as raw console log. The Linux reporter scans the log line by line for an oops signature, strips printk prefixes or architecture-specific stack notation, ignores report-start patterns that can appear inside another report, and builds the selected `Report`. `testParseImpl` then compares the parsed title `WARNING in corrupted`, type `WARNING`, alt titles `none`, panic flag, corruption flag, executor information if present, and explicit report text if the file contains a `REPORT:` block.

## State And Persistence
There is no mutable runtime state in this fixture. The persistent state is the checked-in header block `TITLE: WARNING in corrupted; TYPE: WARNING; CORRUPTED: Y; PANICKED: Y` plus the raw kernel log body. This file currently has 17 lines and 710 bytes. The expected flags are PANICKED=Y, CORRUPTED=Y; alternatives are `none`. Addresses, PIDs, CPU ids, device names, or syscall details may be normalized by the reporter, but the source fixture itself keeps the original console text so boundary and corruption heuristics remain testable.

## Dependencies And Integration Points
The fixture depends on syzkaller's Linux oops regex catalog, warning/KASAN/lockdep/hung-task/RCU-stall recognizers, dynamic-title sanitization, architecture-specific stack parsing, and crash type mapping. It is integrated through `TestParse`, `forEachFile("report", ...)`, target-specific reporter construction, and the surrounding Linux reporter implementation in `linux.go`. Because it lives in `testdata/linux/report`, normal Go test discovery treats it as golden input for the parser rather than as a standalone test binary.

## Risks
Parser changes can regress this file by selecting a generic helper frame, choosing a later interleaved report, missing an unprefixed or truncated architecture-specific line, changing normalized title wording, or flipping panic/corruption state. The expected corrupted flag is part of the contract; parser changes must keep rejecting unreliable frame attribution. The panicked flag should be set from panic-on-warn, fatal exception, hung-task panic, or equivalent kernel panic text. The highest-risk edits are broad changes to Linux oops ordering, `reportStartIgnores`, stack-frame filtering, and title fallback rules.

## Test Signals
The primary signal is that `go test ./pkg/report` parses this fixture into exactly the recorded metadata. For this file, useful smoke checks are: `ContainsCrash` returns true, the first stable title remains `WARNING in corrupted`, crash type remains `WARNING`, alt titles remain `none`, panic/corruption flags remain PANICKED=Y, CORRUPTED=Y, and the selected report still includes the kernel evidence described above. Absence of a `REPORT:` block means parser-selected report boundaries are indirectly checked through metadata and generated report comparison when tests are updated.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/236 -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/237 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/237

## Purpose
This is a syzkaller Linux report-parser fixture for `INFO: rcu detected stall in mount`. It preserves a `RCU stall in mount` console shape under `pkg/report/testdata/linux/report` so `TestParse` can verify that the Linux reporter extracts the expected crash title, crash type, alternative titles, panic state, and corruption state from real kernel output rather than from synthetic unit data.

## Important APIs, Types, And Functions
The file is data, not executable code. Its API surface is the fixture header contract consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, optional `FRAME`, and optional `REPORT`. At runtime the important code paths are `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, Linux oops matching, `extractDescription`, report boundary selection, frame extraction, and `crash.TitleToType`. The kernel symbols and report signatures that matter for this fixture are summarized by: RCU stall report with grace-period kthread text and normalized mount/ksys_mount alternative titles.

## Control Flow
`parseReport` reads the metadata headers until the first blank line and treats the rest of `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/237` as raw console log. The Linux reporter scans the log line by line for an oops signature, strips printk prefixes or architecture-specific stack notation, ignores report-start patterns that can appear inside another report, and builds the selected `Report`. `testParseImpl` then compares the parsed title `INFO: rcu detected stall in mount`, type `HANG`, alt titles `INFO: rcu detected stall in ksys_mount, stall in ksys_mount, stall in mount`, panic flag, corruption flag, executor information if present, and explicit report text if the file contains a `REPORT:` block.

## State And Persistence
There is no mutable runtime state in this fixture. The persistent state is the checked-in header block `TITLE: INFO: rcu detected stall in mount; ALT: INFO: rcu detected stall in ksys_mount; ALT: stall in ksys_mount; ALT: stall in mount; TYPE: HANG` plus the raw kernel log body. This file currently has 54 lines and 3642 bytes. The expected flags are PANICKED=N, CORRUPTED=N; alternatives are `INFO: rcu detected stall in ksys_mount, stall in ksys_mount, stall in mount`. Addresses, PIDs, CPU ids, device names, or syscall details may be normalized by the reporter, but the source fixture itself keeps the original console text so boundary and corruption heuristics remain testable.

## Dependencies And Integration Points
The fixture depends on syzkaller's Linux oops regex catalog, warning/KASAN/lockdep/hung-task/RCU-stall recognizers, dynamic-title sanitization, architecture-specific stack parsing, and crash type mapping. It is integrated through `TestParse`, `forEachFile("report", ...)`, target-specific reporter construction, and the surrounding Linux reporter implementation in `linux.go`. Because it lives in `testdata/linux/report`, normal Go test discovery treats it as golden input for the parser rather than as a standalone test binary.

## Risks
Parser changes can regress this file by selecting a generic helper frame, choosing a later interleaved report, missing an unprefixed or truncated architecture-specific line, changing normalized title wording, or flipping panic/corruption state. The expected non-corrupted result is part of the contract; parser changes should not over-mark this clean report as interleaved or truncated. The panicked flag should remain unset even though the log may contain severe oops or sanitizer text without a kernel panic line. The highest-risk edits are broad changes to Linux oops ordering, `reportStartIgnores`, stack-frame filtering, and title fallback rules.

## Test Signals
The primary signal is that `go test ./pkg/report` parses this fixture into exactly the recorded metadata. For this file, useful smoke checks are: `ContainsCrash` returns true, the first stable title remains `INFO: rcu detected stall in mount`, crash type remains `HANG`, alt titles remain `INFO: rcu detected stall in ksys_mount, stall in ksys_mount, stall in mount`, panic/corruption flags remain PANICKED=N, CORRUPTED=N, and the selected report still includes the kernel evidence described above. Absence of a `REPORT:` block means parser-selected report boundaries are indirectly checked through metadata and generated report comparison when tests are updated.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/237 -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/238 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/238

## Purpose
This is a syzkaller Linux report-parser fixture for `BUG: unable to handle kernel paging request in corrupted`. It preserves a `ARM internal oops corrupted` console shape under `pkg/report/testdata/linux/report` so `TestParse` can verify that the Linux reporter extracts the expected crash title, crash type, alternative titles, panic state, and corruption state from real kernel output rather than from synthetic unit data.

## Important APIs, Types, And Functions
The file is data, not executable code. Its API surface is the fixture header contract consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, optional `FRAME`, and optional `REPORT`. At runtime the important code paths are `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, Linux oops matching, `extractDescription`, report boundary selection, frame extraction, and `crash.TitleToType`. The kernel symbols and report signatures that matter for this fixture are summarized by: ARM Internal error/Oops report lacks a reliable frame, so paging-request title is intentionally corrupted and panicked.

## Control Flow
`parseReport` reads the metadata headers until the first blank line and treats the rest of `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/238` as raw console log. The Linux reporter scans the log line by line for an oops signature, strips printk prefixes or architecture-specific stack notation, ignores report-start patterns that can appear inside another report, and builds the selected `Report`. `testParseImpl` then compares the parsed title `BUG: unable to handle kernel paging request in corrupted`, type `MEMORY_SAFETY_BUG`, alt titles `bad-access in corrupted`, panic flag, corruption flag, executor information if present, and explicit report text if the file contains a `REPORT:` block.

## State And Persistence
There is no mutable runtime state in this fixture. The persistent state is the checked-in header block `TITLE: BUG: unable to handle kernel paging request in corrupted; ALT: bad-access in corrupted; TYPE: MEMORY_SAFETY_BUG; CORRUPTED: Y; PANICKED: Y` plus the raw kernel log body. This file currently has 37 lines and 1585 bytes. The expected flags are PANICKED=Y, CORRUPTED=Y; alternatives are `bad-access in corrupted`. Addresses, PIDs, CPU ids, device names, or syscall details may be normalized by the reporter, but the source fixture itself keeps the original console text so boundary and corruption heuristics remain testable.

## Dependencies And Integration Points
The fixture depends on syzkaller's Linux oops regex catalog, warning/KASAN/lockdep/hung-task/RCU-stall recognizers, dynamic-title sanitization, architecture-specific stack parsing, and crash type mapping. It is integrated through `TestParse`, `forEachFile("report", ...)`, target-specific reporter construction, and the surrounding Linux reporter implementation in `linux.go`. Because it lives in `testdata/linux/report`, normal Go test discovery treats it as golden input for the parser rather than as a standalone test binary.

## Risks
Parser changes can regress this file by selecting a generic helper frame, choosing a later interleaved report, missing an unprefixed or truncated architecture-specific line, changing normalized title wording, or flipping panic/corruption state. The expected corrupted flag is part of the contract; parser changes must keep rejecting unreliable frame attribution. The panicked flag should be set from panic-on-warn, fatal exception, hung-task panic, or equivalent kernel panic text. The highest-risk edits are broad changes to Linux oops ordering, `reportStartIgnores`, stack-frame filtering, and title fallback rules.

## Test Signals
The primary signal is that `go test ./pkg/report` parses this fixture into exactly the recorded metadata. For this file, useful smoke checks are: `ContainsCrash` returns true, the first stable title remains `BUG: unable to handle kernel paging request in corrupted`, crash type remains `MEMORY_SAFETY_BUG`, alt titles remain `bad-access in corrupted`, panic/corruption flags remain PANICKED=Y, CORRUPTED=Y, and the selected report still includes the kernel evidence described above. Absence of a `REPORT:` block means parser-selected report boundaries are indirectly checked through metadata and generated report comparison when tests are updated.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/238 -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/239 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/239

## Purpose
This is a syzkaller Linux report-parser fixture for `WARNING in corrupted`. It preserves a `ARM warning with corrupted task fields` console shape under `pkg/report/testdata/linux/report` so `TestParse` can verify that the Linux reporter extracts the expected crash title, crash type, alternative titles, panic state, and corruption state from real kernel output rather than from synthetic unit data.

## Important APIs, Types, And Functions
The file is data, not executable code. Its API surface is the fixture header contract consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, optional `FRAME`, and optional `REPORT`. At runtime the important code paths are `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, Linux oops matching, `extractDescription`, report boundary selection, frame extraction, and `crash.TitleToType`. The kernel symbols and report signatures that matter for this fixture are summarized by: finish_task_switch warning has negative PID and non-printable comm bytes, validating corrupted classification on malformed context.

## Control Flow
`parseReport` reads the metadata headers until the first blank line and treats the rest of `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/239` as raw console log. The Linux reporter scans the log line by line for an oops signature, strips printk prefixes or architecture-specific stack notation, ignores report-start patterns that can appear inside another report, and builds the selected `Report`. `testParseImpl` then compares the parsed title `WARNING in corrupted`, type `WARNING`, alt titles `none`, panic flag, corruption flag, executor information if present, and explicit report text if the file contains a `REPORT:` block.

## State And Persistence
There is no mutable runtime state in this fixture. The persistent state is the checked-in header block `TITLE: WARNING in corrupted; TYPE: WARNING; CORRUPTED: Y; PANICKED: Y` plus the raw kernel log body. This file currently has 20 lines and 881 bytes. The expected flags are PANICKED=Y, CORRUPTED=Y; alternatives are `none`. Addresses, PIDs, CPU ids, device names, or syscall details may be normalized by the reporter, but the source fixture itself keeps the original console text so boundary and corruption heuristics remain testable.

## Dependencies And Integration Points
The fixture depends on syzkaller's Linux oops regex catalog, warning/KASAN/lockdep/hung-task/RCU-stall recognizers, dynamic-title sanitization, architecture-specific stack parsing, and crash type mapping. It is integrated through `TestParse`, `forEachFile("report", ...)`, target-specific reporter construction, and the surrounding Linux reporter implementation in `linux.go`. Because it lives in `testdata/linux/report`, normal Go test discovery treats it as golden input for the parser rather than as a standalone test binary.

## Risks
Parser changes can regress this file by selecting a generic helper frame, choosing a later interleaved report, missing an unprefixed or truncated architecture-specific line, changing normalized title wording, or flipping panic/corruption state. The expected corrupted flag is part of the contract; parser changes must keep rejecting unreliable frame attribution. The panicked flag should be set from panic-on-warn, fatal exception, hung-task panic, or equivalent kernel panic text. The highest-risk edits are broad changes to Linux oops ordering, `reportStartIgnores`, stack-frame filtering, and title fallback rules.

## Test Signals
The primary signal is that `go test ./pkg/report` parses this fixture into exactly the recorded metadata. For this file, useful smoke checks are: `ContainsCrash` returns true, the first stable title remains `WARNING in corrupted`, crash type remains `WARNING`, alt titles remain `none`, panic/corruption flags remain PANICKED=Y, CORRUPTED=Y, and the selected report still includes the kernel evidence described above. Absence of a `REPORT:` block means parser-selected report boundaries are indirectly checked through metadata and generated report comparison when tests are updated.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/239 -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/24 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/24

## Purpose
This is a syzkaller Linux report-parser fixture for `WARNING in corrupted`. It preserves a `minimal locks warning` console shape under `pkg/report/testdata/linux/report` so `TestParse` can verify that the Linux reporter extracts the expected crash title, crash type, alternative titles, panic state, and corruption state from real kernel output rather than from synthetic unit data.

## Important APIs, Types, And Functions
The file is data, not executable code. Its API surface is the fixture header contract consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, optional `FRAME`, and optional `REPORT`. At runtime the important code paths are `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, Linux oops matching, `extractDescription`, report boundary selection, frame extraction, and `crash.TitleToType`. The kernel symbols and report signatures that matter for this fixture are summarized by: single-line locks_free_lock_context warning, another generic corrupted warning fallback with old warning syntax.

## Control Flow
`parseReport` reads the metadata headers until the first blank line and treats the rest of `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/24` as raw console log. The Linux reporter scans the log line by line for an oops signature, strips printk prefixes or architecture-specific stack notation, ignores report-start patterns that can appear inside another report, and builds the selected `Report`. `testParseImpl` then compares the parsed title `WARNING in corrupted`, type `WARNING`, alt titles `none`, panic flag, corruption flag, executor information if present, and explicit report text if the file contains a `REPORT:` block.

## State And Persistence
There is no mutable runtime state in this fixture. The persistent state is the checked-in header block `TITLE: WARNING in corrupted; TYPE: WARNING; CORRUPTED: Y` plus the raw kernel log body. This file currently has 6 lines and 205 bytes. The expected flags are PANICKED=N, CORRUPTED=Y; alternatives are `none`. Addresses, PIDs, CPU ids, device names, or syscall details may be normalized by the reporter, but the source fixture itself keeps the original console text so boundary and corruption heuristics remain testable.

## Dependencies And Integration Points
The fixture depends on syzkaller's Linux oops regex catalog, warning/KASAN/lockdep/hung-task/RCU-stall recognizers, dynamic-title sanitization, architecture-specific stack parsing, and crash type mapping. It is integrated through `TestParse`, `forEachFile("report", ...)`, target-specific reporter construction, and the surrounding Linux reporter implementation in `linux.go`. Because it lives in `testdata/linux/report`, normal Go test discovery treats it as golden input for the parser rather than as a standalone test binary.

## Risks
Parser changes can regress this file by selecting a generic helper frame, choosing a later interleaved report, missing an unprefixed or truncated architecture-specific line, changing normalized title wording, or flipping panic/corruption state. The expected corrupted flag is part of the contract; parser changes must keep rejecting unreliable frame attribution. The panicked flag should remain unset even though the log may contain severe oops or sanitizer text without a kernel panic line. The highest-risk edits are broad changes to Linux oops ordering, `reportStartIgnores`, stack-frame filtering, and title fallback rules.

## Test Signals
The primary signal is that `go test ./pkg/report` parses this fixture into exactly the recorded metadata. For this file, useful smoke checks are: `ContainsCrash` returns true, the first stable title remains `WARNING in corrupted`, crash type remains `WARNING`, alt titles remain `none`, panic/corruption flags remain PANICKED=N, CORRUPTED=Y, and the selected report still includes the kernel evidence described above. Absence of a `REPORT:` block means parser-selected report boundaries are indirectly checked through metadata and generated report comparison when tests are updated.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/24 -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/240 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/240

## Purpose
This is a syzkaller Linux report-parser fixture for `WARNING in corrupted`. It preserves a `ARM netns cleanup warning` console shape under `pkg/report/testdata/linux/report` so `TestParse` can verify that the Linux reporter extracts the expected crash title, crash type, alternative titles, panic state, and corruption state from real kernel output rather than from synthetic unit data.

## Important APIs, Types, And Functions
The file is data, not executable code. Its API surface is the fixture header contract consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, optional `FRAME`, and optional `REPORT`. At runtime the important code paths are `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, Linux oops matching, `extractDescription`, report boundary selection, frame extraction, and `crash.TitleToType`. The kernel symbols and report signatures that matter for this fixture are summarized by: xfrm6_tunnel_net_exit warning in cleanup_net workqueue panics on warn but remains corrupted because ARM output is minimal.

## Control Flow
`parseReport` reads the metadata headers until the first blank line and treats the rest of `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/240` as raw console log. The Linux reporter scans the log line by line for an oops signature, strips printk prefixes or architecture-specific stack notation, ignores report-start patterns that can appear inside another report, and builds the selected `Report`. `testParseImpl` then compares the parsed title `WARNING in corrupted`, type `WARNING`, alt titles `none`, panic flag, corruption flag, executor information if present, and explicit report text if the file contains a `REPORT:` block.

## State And Persistence
There is no mutable runtime state in this fixture. The persistent state is the checked-in header block `TITLE: WARNING in corrupted; TYPE: WARNING; CORRUPTED: Y; PANICKED: Y` plus the raw kernel log body. This file currently has 22 lines and 1000 bytes. The expected flags are PANICKED=Y, CORRUPTED=Y; alternatives are `none`. Addresses, PIDs, CPU ids, device names, or syscall details may be normalized by the reporter, but the source fixture itself keeps the original console text so boundary and corruption heuristics remain testable.

## Dependencies And Integration Points
The fixture depends on syzkaller's Linux oops regex catalog, warning/KASAN/lockdep/hung-task/RCU-stall recognizers, dynamic-title sanitization, architecture-specific stack parsing, and crash type mapping. It is integrated through `TestParse`, `forEachFile("report", ...)`, target-specific reporter construction, and the surrounding Linux reporter implementation in `linux.go`. Because it lives in `testdata/linux/report`, normal Go test discovery treats it as golden input for the parser rather than as a standalone test binary.

## Risks
Parser changes can regress this file by selecting a generic helper frame, choosing a later interleaved report, missing an unprefixed or truncated architecture-specific line, changing normalized title wording, or flipping panic/corruption state. The expected corrupted flag is part of the contract; parser changes must keep rejecting unreliable frame attribution. The panicked flag should be set from panic-on-warn, fatal exception, hung-task panic, or equivalent kernel panic text. The highest-risk edits are broad changes to Linux oops ordering, `reportStartIgnores`, stack-frame filtering, and title fallback rules.

## Test Signals
The primary signal is that `go test ./pkg/report` parses this fixture into exactly the recorded metadata. For this file, useful smoke checks are: `ContainsCrash` returns true, the first stable title remains `WARNING in corrupted`, crash type remains `WARNING`, alt titles remain `none`, panic/corruption flags remain PANICKED=Y, CORRUPTED=Y, and the selected report still includes the kernel evidence described above. Absence of a `REPORT:` block means parser-selected report boundaries are indirectly checked through metadata and generated report comparison when tests are updated.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/240 -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/241 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/241

## Purpose
This is a syzkaller Linux report-parser fixture for `Unhandled fault in n_tty_set_termios`. It preserves a `ARM unhandled fault` console shape under `pkg/report/testdata/linux/report` so `TestParse` can verify that the Linux reporter extracts the expected crash title, crash type, alternative titles, panic state, and corruption state from real kernel output rather than from synthetic unit data.

## Important APIs, Types, And Functions
The file is data, not executable code. Its API surface is the fixture header contract consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, optional `FRAME`, and optional `REPORT`. At runtime the important code paths are `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, Linux oops matching, `extractDescription`, report boundary selection, frame extraction, and `crash.TitleToType`. The kernel symbols and report signatures that matter for this fixture are summarized by: ARM fatal exception whose meaningful frame is n_tty_set_termios; validates Unhandled fault title normalization.

## Control Flow
`parseReport` reads the metadata headers until the first blank line and treats the rest of `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/241` as raw console log. The Linux reporter scans the log line by line for an oops signature, strips printk prefixes or architecture-specific stack notation, ignores report-start patterns that can appear inside another report, and builds the selected `Report`. `testParseImpl` then compares the parsed title `Unhandled fault in n_tty_set_termios`, type `DoS`, alt titles `bad-access in n_tty_set_termios`, panic flag, corruption flag, executor information if present, and explicit report text if the file contains a `REPORT:` block.

## State And Persistence
There is no mutable runtime state in this fixture. The persistent state is the checked-in header block `TITLE: Unhandled fault in n_tty_set_termios; ALT: bad-access in n_tty_set_termios; TYPE: DoS; PANICKED: Y` plus the raw kernel log body. This file currently has 64 lines and 3775 bytes. The expected flags are PANICKED=Y, CORRUPTED=N; alternatives are `bad-access in n_tty_set_termios`. Addresses, PIDs, CPU ids, device names, or syscall details may be normalized by the reporter, but the source fixture itself keeps the original console text so boundary and corruption heuristics remain testable.

## Dependencies And Integration Points
The fixture depends on syzkaller's Linux oops regex catalog, warning/KASAN/lockdep/hung-task/RCU-stall recognizers, dynamic-title sanitization, architecture-specific stack parsing, and crash type mapping. It is integrated through `TestParse`, `forEachFile("report", ...)`, target-specific reporter construction, and the surrounding Linux reporter implementation in `linux.go`. Because it lives in `testdata/linux/report`, normal Go test discovery treats it as golden input for the parser rather than as a standalone test binary.

## Risks
Parser changes can regress this file by selecting a generic helper frame, choosing a later interleaved report, missing an unprefixed or truncated architecture-specific line, changing normalized title wording, or flipping panic/corruption state. The expected non-corrupted result is part of the contract; parser changes should not over-mark this clean report as interleaved or truncated. The panicked flag should be set from panic-on-warn, fatal exception, hung-task panic, or equivalent kernel panic text. The highest-risk edits are broad changes to Linux oops ordering, `reportStartIgnores`, stack-frame filtering, and title fallback rules.

## Test Signals
The primary signal is that `go test ./pkg/report` parses this fixture into exactly the recorded metadata. For this file, useful smoke checks are: `ContainsCrash` returns true, the first stable title remains `Unhandled fault in n_tty_set_termios`, crash type remains `DoS`, alt titles remain `bad-access in n_tty_set_termios`, panic/corruption flags remain PANICKED=Y, CORRUPTED=N, and the selected report still includes the kernel evidence described above. Absence of a `REPORT:` block means parser-selected report boundaries are indirectly checked through metadata and generated report comparison when tests are updated.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/241 -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/242 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/242

## Purpose
This is a syzkaller Linux report-parser fixture for `Alignment trap in corrupted`. It preserves a `ARM alignment trap corrupted` console shape under `pkg/report/testdata/linux/report` so `TestParse` can verify that the Linux reporter extracts the expected crash title, crash type, alternative titles, panic state, and corruption state from real kernel output rather than from synthetic unit data.

## Important APIs, Types, And Functions
The file is data, not executable code. Its API surface is the fixture header contract consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, optional `FRAME`, and optional `REPORT`. At runtime the important code paths are `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, Linux oops matching, `extractDescription`, report boundary selection, frame extraction, and `crash.TitleToType`. The kernel symbols and report signatures that matter for this fixture are summarized by: alignment-trap fatal exception with no reliable symbol in title, marked corrupted and panicked.

## Control Flow
`parseReport` reads the metadata headers until the first blank line and treats the rest of `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/242` as raw console log. The Linux reporter scans the log line by line for an oops signature, strips printk prefixes or architecture-specific stack notation, ignores report-start patterns that can appear inside another report, and builds the selected `Report`. `testParseImpl` then compares the parsed title `Alignment trap in corrupted`, type `DoS`, alt titles `none`, panic flag, corruption flag, executor information if present, and explicit report text if the file contains a `REPORT:` block.

## State And Persistence
There is no mutable runtime state in this fixture. The persistent state is the checked-in header block `TITLE: Alignment trap in corrupted; TYPE: DoS; CORRUPTED: Y; PANICKED: Y` plus the raw kernel log body. This file currently has 47 lines and 2496 bytes. The expected flags are PANICKED=Y, CORRUPTED=Y; alternatives are `none`. Addresses, PIDs, CPU ids, device names, or syscall details may be normalized by the reporter, but the source fixture itself keeps the original console text so boundary and corruption heuristics remain testable.

## Dependencies And Integration Points
The fixture depends on syzkaller's Linux oops regex catalog, warning/KASAN/lockdep/hung-task/RCU-stall recognizers, dynamic-title sanitization, architecture-specific stack parsing, and crash type mapping. It is integrated through `TestParse`, `forEachFile("report", ...)`, target-specific reporter construction, and the surrounding Linux reporter implementation in `linux.go`. Because it lives in `testdata/linux/report`, normal Go test discovery treats it as golden input for the parser rather than as a standalone test binary.

## Risks
Parser changes can regress this file by selecting a generic helper frame, choosing a later interleaved report, missing an unprefixed or truncated architecture-specific line, changing normalized title wording, or flipping panic/corruption state. The expected corrupted flag is part of the contract; parser changes must keep rejecting unreliable frame attribution. The panicked flag should be set from panic-on-warn, fatal exception, hung-task panic, or equivalent kernel panic text. The highest-risk edits are broad changes to Linux oops ordering, `reportStartIgnores`, stack-frame filtering, and title fallback rules.

## Test Signals
The primary signal is that `go test ./pkg/report` parses this fixture into exactly the recorded metadata. For this file, useful smoke checks are: `ContainsCrash` returns true, the first stable title remains `Alignment trap in corrupted`, crash type remains `DoS`, alt titles remain `none`, panic/corruption flags remain PANICKED=Y, CORRUPTED=Y, and the selected report still includes the kernel evidence described above. Absence of a `REPORT:` block means parser-selected report boundaries are indirectly checked through metadata and generated report comparison when tests are updated.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/242 -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/243 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/243

## Purpose
This is a syzkaller Linux report-parser fixture for `BUG: unable to handle kernel paging request in migrate_task_rq_fair`. It preserves a `ARM scheduler oops` console shape under `pkg/report/testdata/linux/report` so `TestParse` can verify that the Linux reporter extracts the expected crash title, crash type, alternative titles, panic state, and corruption state from real kernel output rather than from synthetic unit data.

## Important APIs, Types, And Functions
The file is data, not executable code. Its API surface is the fixture header contract consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, optional `FRAME`, and optional `REPORT`. At runtime the important code paths are `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, Linux oops matching, `extractDescription`, report boundary selection, frame extraction, and `crash.TitleToType`. The kernel symbols and report signatures that matter for this fixture are summarized by: ARM Internal error/Oops with migrate_task_rq_fair as the selected frame and fatal exception panic.

## Control Flow
`parseReport` reads the metadata headers until the first blank line and treats the rest of `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/243` as raw console log. The Linux reporter scans the log line by line for an oops signature, strips printk prefixes or architecture-specific stack notation, ignores report-start patterns that can appear inside another report, and builds the selected `Report`. `testParseImpl` then compares the parsed title `BUG: unable to handle kernel paging request in migrate_task_rq_fair`, type `MEMORY_SAFETY_BUG`, alt titles `bad-access in migrate_task_rq_fair`, panic flag, corruption flag, executor information if present, and explicit report text if the file contains a `REPORT:` block.

## State And Persistence
There is no mutable runtime state in this fixture. The persistent state is the checked-in header block `TITLE: BUG: unable to handle kernel paging request in migrate_task_rq_fair; ALT: bad-access in migrate_task_rq_fair; TYPE: MEMORY_SAFETY_BUG; PANICKED: Y` plus the raw kernel log body. This file currently has 59 lines and 3231 bytes. The expected flags are PANICKED=Y, CORRUPTED=N; alternatives are `bad-access in migrate_task_rq_fair`. Addresses, PIDs, CPU ids, device names, or syscall details may be normalized by the reporter, but the source fixture itself keeps the original console text so boundary and corruption heuristics remain testable.

## Dependencies And Integration Points
The fixture depends on syzkaller's Linux oops regex catalog, warning/KASAN/lockdep/hung-task/RCU-stall recognizers, dynamic-title sanitization, architecture-specific stack parsing, and crash type mapping. It is integrated through `TestParse`, `forEachFile("report", ...)`, target-specific reporter construction, and the surrounding Linux reporter implementation in `linux.go`. Because it lives in `testdata/linux/report`, normal Go test discovery treats it as golden input for the parser rather than as a standalone test binary.

## Risks
Parser changes can regress this file by selecting a generic helper frame, choosing a later interleaved report, missing an unprefixed or truncated architecture-specific line, changing normalized title wording, or flipping panic/corruption state. The expected non-corrupted result is part of the contract; parser changes should not over-mark this clean report as interleaved or truncated. The panicked flag should be set from panic-on-warn, fatal exception, hung-task panic, or equivalent kernel panic text. The highest-risk edits are broad changes to Linux oops ordering, `reportStartIgnores`, stack-frame filtering, and title fallback rules.

## Test Signals
The primary signal is that `go test ./pkg/report` parses this fixture into exactly the recorded metadata. For this file, useful smoke checks are: `ContainsCrash` returns true, the first stable title remains `BUG: unable to handle kernel paging request in migrate_task_rq_fair`, crash type remains `MEMORY_SAFETY_BUG`, alt titles remain `bad-access in migrate_task_rq_fair`, panic/corruption flags remain PANICKED=Y, CORRUPTED=N, and the selected report still includes the kernel evidence described above. Absence of a `REPORT:` block means parser-selected report boundaries are indirectly checked through metadata and generated report comparison when tests are updated.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/243 -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/244 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/244

## Purpose
This is a syzkaller Linux report-parser fixture for `WARNING: suspicious RCU usage in corrupted`. It preserves a `suspicious RCU usage with multiple traces` console shape under `pkg/report/testdata/linux/report` so `TestParse` can verify that the Linux reporter extracts the expected crash title, crash type, alternative titles, panic state, and corruption state from real kernel output rather than from synthetic unit data.

## Important APIs, Types, And Functions
The file is data, not executable code. Its API surface is the fixture header contract consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, optional `FRAME`, and optional `REPORT`. At runtime the important code paths are `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, Linux oops matching, `extractDescription`, report boundary selection, frame extraction, and `crash.TitleToType`. The kernel symbols and report signatures that matter for this fixture are summarized by: lockdep RCU warning interleaved with several executor call traces; corrupted title protects against selecting unrelated refcount/syscall frames.

## Control Flow
`parseReport` reads the metadata headers until the first blank line and treats the rest of `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/244` as raw console log. The Linux reporter scans the log line by line for an oops signature, strips printk prefixes or architecture-specific stack notation, ignores report-start patterns that can appear inside another report, and builds the selected `Report`. `testParseImpl` then compares the parsed title `WARNING: suspicious RCU usage in corrupted`, type `LOCKDEP`, alt titles `none`, panic flag, corruption flag, executor information if present, and explicit report text if the file contains a `REPORT:` block.

## State And Persistence
There is no mutable runtime state in this fixture. The persistent state is the checked-in header block `TITLE: WARNING: suspicious RCU usage in corrupted; TYPE: LOCKDEP; CORRUPTED: Y` plus the raw kernel log body. This file currently has 462 lines and 23633 bytes. The expected flags are PANICKED=N, CORRUPTED=Y; alternatives are `none`. Addresses, PIDs, CPU ids, device names, or syscall details may be normalized by the reporter, but the source fixture itself keeps the original console text so boundary and corruption heuristics remain testable.

## Dependencies And Integration Points
The fixture depends on syzkaller's Linux oops regex catalog, warning/KASAN/lockdep/hung-task/RCU-stall recognizers, dynamic-title sanitization, architecture-specific stack parsing, and crash type mapping. It is integrated through `TestParse`, `forEachFile("report", ...)`, target-specific reporter construction, and the surrounding Linux reporter implementation in `linux.go`. Because it lives in `testdata/linux/report`, normal Go test discovery treats it as golden input for the parser rather than as a standalone test binary.

## Risks
Parser changes can regress this file by selecting a generic helper frame, choosing a later interleaved report, missing an unprefixed or truncated architecture-specific line, changing normalized title wording, or flipping panic/corruption state. The expected corrupted flag is part of the contract; parser changes must keep rejecting unreliable frame attribution. The panicked flag should remain unset even though the log may contain severe oops or sanitizer text without a kernel panic line. The highest-risk edits are broad changes to Linux oops ordering, `reportStartIgnores`, stack-frame filtering, and title fallback rules.

## Test Signals
The primary signal is that `go test ./pkg/report` parses this fixture into exactly the recorded metadata. For this file, useful smoke checks are: `ContainsCrash` returns true, the first stable title remains `WARNING: suspicious RCU usage in corrupted`, crash type remains `LOCKDEP`, alt titles remain `none`, panic/corruption flags remain PANICKED=N, CORRUPTED=Y, and the selected report still includes the kernel evidence described above. Absence of a `REPORT:` block means parser-selected report boundaries are indirectly checked through metadata and generated report comparison when tests are updated.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/244 -->
