# subset-b-009482 Research

Grouped research for syzkaller Linux report parser fixtures. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/132 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/132

## Purpose
This is a syzkaller Linux report-parser fixture for `INFO: Freed in fasync_free_rcu age=NUM cpu=NUM pid=NUM`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/132` so `pkg/report` can verify parser edge-case coverage for Linux console output for fasync/slab lifetime diagnostics.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `fasync_free_rcu, native_queued_spin_lock_slowpath, SyS_fcntl, kmem_cache_alloc, fasync_helper, sg_remove_request, queued_write_lock_slowpath, __asan_report_load4_noabort`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `fasync_free_rcu age=NUM cpu=NUM pid=NUM`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `INFO: Freed in fasync_free_rcu age=NUM cpu=NUM pid=NUM`, type `none recorded`, alternatives `none`, flags `CORRUPTED=Y`, 67 log lines, 0 explicit report lines, and 7292 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
marked corrupted, so parser changes must continue to distinguish real frames from truncated, interleaved, or printk-dropped output.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `INFO: Freed in fasync_free_rcu age=NUM cpu=NUM pid=NUM`, the crash type remains `none recorded`, alt titles remain `none`, and representative frames around `fasync_free_rcu age=NUM cpu=NUM pid=NUM` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/132 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/133 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/133

## Purpose
This is a syzkaller Linux report-parser fixture for `INFO: Allocated in fasync_helper age=NUM cpu=NUM pid=NUM`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/133` so `pkg/report` can verify parser edge-case coverage for Linux console output for fasync/slab lifetime diagnostics.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `security_file_permission, __slab_alloc.isra.74.constprop.77, fasync_helper, native_queued_spin_lock_slowpath, SyS_fcntl, rw_verify_area, run_ksoftirqd, print_trailer`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `fasync_helper age=NUM cpu=NUM pid=NUM`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `INFO: Allocated in fasync_helper age=NUM cpu=NUM pid=NUM`, type `none recorded`, alternatives `none`, flags `CORRUPTED=Y`, 54 log lines, 0 explicit report lines, and 5686 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
marked corrupted, so parser changes must continue to distinguish real frames from truncated, interleaved, or printk-dropped output.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `INFO: Allocated in fasync_helper age=NUM cpu=NUM pid=NUM`, the crash type remains `none recorded`, alt titles remain `none`, and representative frames around `fasync_helper age=NUM cpu=NUM pid=NUM` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/133 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/134 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/134

## Purpose
This is a syzkaller Linux report-parser fixture for `BUG: using __this_cpu_read() in preemptible code in ipcomp_init_state`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/134` so `pkg/report` can verify lockdep and RCU/context validation coverage, where title extraction must preserve locking-context wording and the indicative kernel frame for xfrm/IPComp crypto initialization.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `__this_cpu_preempt_check, dump_stack, check_preemption_disabled, ipcomp_init_state, __lock_is_held, ipcomp4_init_state, __xfrm_init_state, xfrm_init_state`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `ipcomp_init_state`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `BUG: using __this_cpu_read() in preemptible code in ipcomp_init_state`, type `LOCKDEP`, alternatives `none`, flags `none`, 79 log lines, 0 explicit report lines, and 6870 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
lockdep messages often contain unrelated subsystem chatter that can be mistaken for the first report.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `BUG: using __this_cpu_read() in preemptible code in ipcomp_init_state`, the crash type remains `LOCKDEP`, alt titles remain `none`, and representative frames around `ipcomp_init_state` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/134 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/135 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/135

## Purpose
This is a syzkaller Linux report-parser fixture for `BUG: using __this_cpu_read() in preemptible code in ipcomp_init_state`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/135` so `pkg/report` can verify lockdep and RCU/context validation coverage, where title extraction must preserve locking-context wording and the indicative kernel frame for xfrm/IPComp crypto initialization.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `__this_cpu_preempt_check, dump_stack, check_preemption_disabled, ipcomp_init_state, ipcomp4_init_state, SyS_sendmsg, entry_SYSCALL_64_fastpath, handle_userfault`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `ipcomp_init_state`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `BUG: using __this_cpu_read() in preemptible code in ipcomp_init_state`, type `LOCKDEP`, alternatives `none`, flags `none`, 28 log lines, 0 explicit report lines, and 1960 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
lockdep messages often contain unrelated subsystem chatter that can be mistaken for the first report.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `BUG: using __this_cpu_read() in preemptible code in ipcomp_init_state`, the crash type remains `LOCKDEP`, alt titles remain `none`, and representative frames around `ipcomp_init_state` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/135 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/136 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/136

## Purpose
This is a syzkaller Linux report-parser fixture for `BUG: using __this_cpu_read() in preemptible code in corrupted`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/136` so `pkg/report` can verify lockdep and RCU/context validation coverage, where title extraction must preserve locking-context wording and the indicative kernel frame for parser corruption/truncation handling.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `__this_cpu_preempt_check, dump_stack, check_preemption_disabled`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `corrupted`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `BUG: using __this_cpu_read() in preemptible code in corrupted`, type `LOCKDEP`, alternatives `none`, flags `CORRUPTED=Y`, 13 log lines, 0 explicit report lines, and 1205 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
marked corrupted, so parser changes must continue to distinguish real frames from truncated, interleaved, or printk-dropped output; the title intentionally falls back to `corrupted`, which is a regression-sensitive signal for frame extraction failure; lockdep messages often contain unrelated subsystem chatter that can be mistaken for the first report.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `BUG: using __this_cpu_read() in preemptible code in corrupted`, the crash type remains `LOCKDEP`, alt titles remain `none`, and representative frames around `corrupted` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/136 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/137 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/137

## Purpose
This is a syzkaller Linux report-parser fixture for `BUG: using __this_cpu_read() in preemptible code in ipcomp_init_state`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/137` so `pkg/report` can verify lockdep and RCU/context validation coverage, where title extraction must preserve locking-context wording and the indicative kernel frame for xfrm/IPComp crypto initialization.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `__this_cpu_preempt_check, dump_stack, check_preemption_disabled, ipcomp_init_state, __lock_is_held, ipcomp4_init_state, __xfrm_init_state, xfrm_init_state`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `ipcomp_init_state`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `BUG: using __this_cpu_read() in preemptible code in ipcomp_init_state`, type `LOCKDEP`, alternatives `none`, flags `none`, 41 log lines, 0 explicit report lines, and 2970 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
lockdep messages often contain unrelated subsystem chatter that can be mistaken for the first report.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `BUG: using __this_cpu_read() in preemptible code in ipcomp_init_state`, the crash type remains `LOCKDEP`, alt titles remain `none`, and representative frames around `ipcomp_init_state` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/137 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/138 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/138

## Purpose
This is a syzkaller Linux report-parser fixture for `INFO: task hung in corrupted`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/138` so `pkg/report` can verify hang/stall detection coverage, where the parser must recognize scheduler, hung-task, or RCU-stall reports without a normal oops footer for parser corruption/truncation handling.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `__schedule, __sched_text_start, insert_work, find_held_lock, print_usage_bug`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `corrupted`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `INFO: task hung in corrupted`, type `HANG`, alternatives `hang in corrupted`, flags `CORRUPTED=Y`, 11 log lines, 0 explicit report lines, and 704 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
marked corrupted, so parser changes must continue to distinguish real frames from truncated, interleaved, or printk-dropped output; the title intentionally falls back to `corrupted`, which is a regression-sensitive signal for frame extraction failure; hang reports lack the usual oops boundary and depend on scheduler/RCU wording.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `INFO: task hung in corrupted`, the crash type remains `HANG`, alt titles remain `hang in corrupted`, and representative frames around `corrupted` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/138 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/139 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/139

## Purpose
This is a syzkaller Linux report-parser fixture for `BUG: unable to handle kernel paging request in hash_sendmsg`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/139` so `pkg/report` can verify generic oops memory-safety coverage, where page-fault and NX traces are normalized into a stable bad-access title for AF_ALG hash sendmsg.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `sha1_mb_async_init, hash_sendmsg, security_socket_sendmsg, sock_sendmsg, ___sys_sendmsg, perf_trace_lock, find_held_lock, __fget`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `hash_sendmsg`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `BUG: unable to handle kernel paging request in hash_sendmsg`, type `MEMORY_SAFETY_BUG`, alternatives `bad-access in hash_sendmsg`, flags `PANICKED=Y`, 55 log lines, 0 explicit report lines, and 3561 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
panic_on_warn/panic aftermath is present, so secondary panic stacks can obscure the root report.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `BUG: unable to handle kernel paging request in hash_sendmsg`, the crash type remains `MEMORY_SAFETY_BUG`, alt titles remain `bad-access in hash_sendmsg`, and representative frames around `hash_sendmsg` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/139 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/14 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/14

## Purpose
This is a syzkaller Linux report-parser fixture for `general protection fault in __ip_options_echo`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/14` so `pkg/report` can verify crash/oops denial-of-service coverage, where a kernel fault is expected even without a sanitizer-specific class for IPv4 option echo handling.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `__ip_options_echo`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `__ip_options_echo`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `general protection fault in __ip_options_echo`, type `DoS`, alternatives `bad-access in __ip_options_echo`, flags `CORRUPTED=Y`, 17 log lines, 0 explicit report lines, and 1287 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
marked corrupted, so parser changes must continue to distinguish real frames from truncated, interleaved, or printk-dropped output.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `general protection fault in __ip_options_echo`, the crash type remains `DoS`, alt titles remain `bad-access in __ip_options_echo`, and representative frames around `__ip_options_echo` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/14 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/140 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/140

## Purpose
This is a syzkaller Linux report-parser fixture for `WARNING in strp_data_ready`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/140` so `pkg/report` can verify WARNING and panic_on_warn coverage, where the primary warning stack must be kept while secondary panic stacks are trimmed or tolerated for stream parser/KCM networking.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `strp_data_ready, dump_stack, arch_local_irq_restore, vsnprintf, panic, refcount_error_report, show_regs_print_info, find_held_lock`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `strp_data_ready`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `WARNING in strp_data_ready`, type `WARNING`, alternatives `none`, flags `PANICKED=Y`, 130 log lines, 0 explicit report lines, and 26590 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
panic_on_warn/panic aftermath is present, so secondary panic stacks can obscure the root report; warning stacks may be followed by panic stacks and unrelated device logs.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `WARNING in strp_data_ready`, the crash type remains `WARNING`, alt titles remain `none`, and representative frames around `strp_data_ready` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/140 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/141 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/141

## Purpose
This is a syzkaller Linux report-parser fixture for `WARNING in kvm_arch_vcpu_ioctl_run`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/141` so `pkg/report` can verify WARNING and panic_on_warn coverage, where the primary warning stack must be kept while secondary panic stacks are trimmed or tolerated for KVM vCPU ioctl handling.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `kvm_arch_vcpu_ioctl_run, dump_stack, arch_local_irq_restore, vsnprintf, panic, refcount_error_report, show_regs_print_info, __warn`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `kvm_arch_vcpu_ioctl_run`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `WARNING in kvm_arch_vcpu_ioctl_run`, type `WARNING`, alternatives `none`, flags `PANICKED=Y`, 97 log lines, 0 explicit report lines, and 5357 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
panic_on_warn/panic aftermath is present, so secondary panic stacks can obscure the root report; warning stacks may be followed by panic stacks and unrelated device logs.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `WARNING in kvm_arch_vcpu_ioctl_run`, the crash type remains `WARNING`, alt titles remain `none`, and representative frames around `kvm_arch_vcpu_ioctl_run` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/141 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/142 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/142

## Purpose
This is a syzkaller Linux report-parser fixture for `WARNING in corrupted`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/142` so `pkg/report` can verify WARNING and panic_on_warn coverage, where the primary warning stack must be kept while secondary panic stacks are trimmed or tolerated for parser corruption/truncation handling.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `__switch_to, native_write_cr4, smp_reboot_interrupt, native_stop_other_cpus, _raw_spin_unlock, handle_edge_irq, task_prio, trace_hardirqs_off_thunk`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `corrupted`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `WARNING in corrupted`, type `WARNING`, alternatives `none`, flags `CORRUPTED=Y, PANICKED=Y`, 73 log lines, 0 explicit report lines, and 4550 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
marked corrupted, so parser changes must continue to distinguish real frames from truncated, interleaved, or printk-dropped output; panic_on_warn/panic aftermath is present, so secondary panic stacks can obscure the root report; the title intentionally falls back to `corrupted`, which is a regression-sensitive signal for frame extraction failure; warning stacks may be followed by panic stacks and unrelated device logs.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `WARNING in corrupted`, the crash type remains `WARNING`, alt titles remain `none`, and representative frames around `corrupted` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/142 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/143 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/143

## Purpose
This is a syzkaller Linux report-parser fixture for `kernel panic: Attempted to kill init!`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/143` so `pkg/report` can verify crash/oops denial-of-service coverage, where a kernel fault is expected even without a sanitizer-specific class for task exit and mmap semaphore teardown.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `dump_stack, panic, do_exit, do_group_exit, get_signal, do_signal, __bad_area_nosemaphore, __do_page_fault`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `dump_stack`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `kernel panic: Attempted to kill init!`, type `DoS`, alternatives `none`, flags `SUPPRESSED=Y, PANICKED=Y`, 23 log lines, 0 explicit report lines, and 1189 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
panic_on_warn/panic aftermath is present, so secondary panic stacks can obscure the root report; suppressed output is intentional and must not be promoted as a normal report.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `kernel panic: Attempted to kill init!`, the crash type remains `DoS`, alt titles remain `none`, and representative frames around `dump_stack` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/143 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/144 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/144

## Purpose
This is a syzkaller Linux report-parser negative fixture containing only `ODEBUG: Out of memory. ODEBUG disabled`. It keeps a minimal console line under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/144` so `pkg/report` can verify that this diagnostic alone is not promoted to a crash report with a synthesized title.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the absence of `TITLE`, `TYPE`, `CORRUPTED`, `PANICKED`, and `REPORT` headers in the schema consumed by `ParseTest` in `report_test.go`. The runtime APIs under test are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, and the Linux oops matcher; the expected result is effectively nil/no crash rather than a populated `Report`.

## Control Flow
`parseReport` sees no header block and treats the single ODEBUG line as raw log input. `testParseImpl` calls the Linux reporter, which scans for known oops signatures; this file asserts that the out-of-memory debugobjects notice by itself should not pass the first-oops filter or enter normal `findReport` extraction.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in lack of expected metadata: no title, no type, no alternative titles, no flags, one log line, zero explicit report lines, and a very small source footprint. That absence is the important state because adding a title would change the fixture from negative coverage to positive crash coverage.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog and ignore/suppression choices, plus the generic `TestParse`/`forEachFile("report", ...)` fixture walker. It integrates with the same Linux reporter selected by `NewReporter`, but exercises the no-report path instead of title, stack, and crash-type normalization.

## Risks
The main risk is over-broad ODEBUG matching: future parser changes could incorrectly treat this resource-exhaustion notice as a reportable warning. The opposite risk is weaker but still relevant: if Linux starts printing this line adjacent to real ODEBUG warnings, report-boundary logic must avoid using this fixture to suppress legitimate multi-line reports.

## Test Signals
Regression signal is that parsing this exact log produces no expected crash metadata and no explicit report bytes. A useful smoke check is that `report/144` remains a negative fixture while neighboring ODEBUG fixtures, such as release/free-active warnings with `TITLE` headers, continue to parse as normal warnings.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/144 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/145 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/145

## Purpose
This is a syzkaller Linux report-parser fixture for `INFO: rcu detected stall in ipv6_rcv`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/145` so `pkg/report` can verify hang/stall detection coverage, where the parser must recognize scheduler, hung-task, or RCU-stall reports without a normal oops footer for IPv6 receive path.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `sched_show_task, print_other_cpu_stall, check_cpu_stall.isra.61, rcu_check_callbacks, update_process_times, tick_sched_handle, tick_sched_timer, __hrtimer_run_queues`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `ipv6_rcv`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `INFO: rcu detected stall in ipv6_rcv`, type `HANG`, alternatives `stall in ipv6_rcv`, flags `none`, 61 log lines, 0 explicit report lines, and 3388 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
hang reports lack the usual oops boundary and depend on scheduler/RCU wording.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `INFO: rcu detected stall in ipv6_rcv`, the crash type remains `HANG`, alt titles remain `stall in ipv6_rcv`, and representative frames around `ipv6_rcv` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/145 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/146 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/146

## Purpose
This is a syzkaller Linux report-parser fixture for `BUG: unable to handle kernel paging request in remove_wait_queue`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/146` so `pkg/report` can verify generic oops memory-safety coverage, where page-fault and NX traces are normalized into a stable bad-access title for wait-queue and lockdep interactions.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `__lock_acquire, lock_acquire, remove_wait_queue, ep_unregister_pollwait.isra.7, _raw_spin_lock_irqsave, ep_remove, eventpoll_release_file, __fput`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `remove_wait_queue`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `BUG: unable to handle kernel paging request in remove_wait_queue`, type `MEMORY_SAFETY_BUG`, alternatives `bad-access in remove_wait_queue`, flags `none`, 51 log lines, 0 explicit report lines, and 3276 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
the main risk is title drift if Linux wording or stack formatting changes.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `BUG: unable to handle kernel paging request in remove_wait_queue`, the crash type remains `MEMORY_SAFETY_BUG`, alt titles remain `bad-access in remove_wait_queue`, and representative frames around `remove_wait_queue` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/146 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/147 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/147

## Purpose
This is a syzkaller Linux report-parser fixture for `KASAN: use-after-free Read in remove_wait_queue`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/147` so `pkg/report` can verify KASAN use-after-free read coverage, including allocation/free metadata and stack-frame extraction for wait-queue and lockdep interactions.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `__lock_acquire, dump_stack, print_address_description, kasan_report, __asan_report_load8_noabort, lock_downgrade, __bpf_address_lookup, remove_wait_queue`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `remove_wait_queue`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `KASAN: use-after-free Read in remove_wait_queue`, type `KASAN-USE-AFTER-FREE-READ`, alternatives `bad-access in remove_wait_queue`, flags `none`, 95 log lines, 0 explicit report lines, and 5169 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
sanitizer details are noisy but allocation/free metadata and access direction must remain parseable.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `KASAN: use-after-free Read in remove_wait_queue`, the crash type remains `KASAN-USE-AFTER-FREE-READ`, alt titles remain `bad-access in remove_wait_queue`, and representative frames around `remove_wait_queue` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/147 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/148 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/148

## Purpose
This is a syzkaller Linux report-parser fixture for `general protection fault in tipc_subscrb_subscrp_delete`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/148` so `pkg/report` can verify crash/oops denial-of-service coverage, where a kernel fault is expected even without a sanitizer-specific class for TIPC networking.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `__lock_acquire, find_held_lock, lock_downgrade, debug_check_no_locks_freed, llist_add_batch, find_last_bit, tick_nohz_tick_stopped, irq_work_queue`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `tipc_subscrb_subscrp_delete`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `general protection fault in tipc_subscrb_subscrp_delete`, type `DoS`, alternatives `bad-access in tipc_subscrb_subscrp_delete`, flags `none`, 87 log lines, 0 explicit report lines, and 5061 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
the main risk is title drift if Linux wording or stack formatting changes.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `general protection fault in tipc_subscrb_subscrp_delete`, the crash type remains `DoS`, alt titles remain `bad-access in tipc_subscrb_subscrp_delete`, and representative frames around `tipc_subscrb_subscrp_delete` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/148 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/149 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/149

## Purpose
This is a syzkaller Linux report-parser fixture for `KASAN: use-after-free Read in strp_check_rcv`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/149` so `pkg/report` can verify KASAN use-after-free read coverage, including allocation/free metadata and stack-frame extraction for stream parser/KCM networking.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `work_is_static_object, dump_stack, arch_local_irq_restore, show_regs_print_info, lock_release, debug_check_no_locks_freed, print_address_description, kasan_report`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `strp_check_rcv`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `KASAN: use-after-free Read in strp_check_rcv`, type `KASAN-USE-AFTER-FREE-READ`, alternatives `bad-access in strp_check_rcv`, flags `none`, 105 log lines, 0 explicit report lines, and 5519 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
sanitizer details are noisy but allocation/free metadata and access direction must remain parseable.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `KASAN: use-after-free Read in strp_check_rcv`, the crash type remains `KASAN-USE-AFTER-FREE-READ`, alt titles remain `bad-access in strp_check_rcv`, and representative frames around `strp_check_rcv` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/149 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/15 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/15

## Purpose
This is a syzkaller Linux report-parser fixture for `KASAN: slab-out-of-bounds Read in corrupted`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/15` so `pkg/report` can verify KASAN read violation coverage, including slab, stack, or bounds reports for parser corruption/truncation handling.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `memcpy`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `corrupted`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `KASAN: slab-out-of-bounds Read in corrupted`, type `KASAN-READ`, alternatives `bad-access in corrupted`, flags `CORRUPTED=Y`, 5 log lines, 0 explicit report lines, and 474 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
marked corrupted, so parser changes must continue to distinguish real frames from truncated, interleaved, or printk-dropped output; the title intentionally falls back to `corrupted`, which is a regression-sensitive signal for frame extraction failure; sanitizer details are noisy but allocation/free metadata and access direction must remain parseable.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `KASAN: slab-out-of-bounds Read in corrupted`, the crash type remains `KASAN-READ`, alt titles remain `bad-access in corrupted`, and representative frames around `corrupted` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/15 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/150 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/150

## Purpose
This is a syzkaller Linux report-parser fixture for `WARNING: held lock freed in sctp_wait_for_sndbuf`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/150` so `pkg/report` can verify lockdep and RCU/context validation coverage, where title extraction must preserve locking-context wording and the indicative kernel frame for SCTP socket lifetime and send-buffer handling.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `sctp_wait_for_sndbuf, dump_stack, arch_local_irq_restore, debug_check_no_locks_freed, kmem_cache_free, __sk_destruct, kasan_slab_free, sock_rfree`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `sctp_wait_for_sndbuf`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `WARNING: held lock freed in sctp_wait_for_sndbuf`, type `LOCKDEP`, alternatives `none`, flags `none`, 86 log lines, 0 explicit report lines, and 4440 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
lockdep messages often contain unrelated subsystem chatter that can be mistaken for the first report.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `WARNING: held lock freed in sctp_wait_for_sndbuf`, the crash type remains `LOCKDEP`, alt titles remain `none`, and representative frames around `sctp_wait_for_sndbuf` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/150 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/151 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/151

## Purpose
This is a syzkaller Linux report-parser fixture for `memory leak in new_inode_pseudo`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/151` so `pkg/report` can verify memory-leak detector coverage, where leak backtraces rather than oops stacks define the title for debugfs/pseudo-inode allocation.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `kmem_cache_alloc, alloc_inode, new_inode_pseudo, new_inode, debugfs_get_inode, __debugfs_create_file, debugfs_create_file, binder_open`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `new_inode_pseudo`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `memory leak in new_inode_pseudo`, type `LEAK`, alternatives `none`, flags `none`, 47 log lines, 0 explicit report lines, and 2365 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
the main risk is title drift if Linux wording or stack formatting changes.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `memory leak in new_inode_pseudo`, the crash type remains `LEAK`, alt titles remain `none`, and representative frames around `new_inode_pseudo` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/151 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/152 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/152

## Purpose
This is a syzkaller Linux report-parser fixture for `WARNING: possible circular locking dependency detected`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/152` so `pkg/report` can verify WARNING and panic_on_warn coverage, where the primary warning stack must be kept while secondary panic stacks are trimmed or tolerated for Linux crash-report parsing.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `none reliably extracted from this short/corrupted log`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `none isolated`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `WARNING: possible circular locking dependency detected`, type `WARNING`, alternatives `none`, flags `CORRUPTED=Y`, 21 log lines, 0 explicit report lines, and 2065 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
marked corrupted, so parser changes must continue to distinguish real frames from truncated, interleaved, or printk-dropped output; warning stacks may be followed by panic stacks and unrelated device logs.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `WARNING: possible circular locking dependency detected`, the crash type remains `WARNING`, alt titles remain `none`, and representative frames around `none isolated` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/152 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/153 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/153

## Purpose
This is a syzkaller Linux report-parser fixture for `WARNING: kmalloc bug in relay_open_buf`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/153` so `pkg/report` can verify WARNING and panic_on_warn coverage, where the primary warning stack must be kept while secondary panic stacks are trimmed or tolerated for relayfs buffer allocation.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `kmalloc_slab, dump_stack, arch_local_irq_restore, vsnprintf, panic, refcount_error_report, show_regs_print_info, __warn`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `relay_open_buf`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `WARNING: kmalloc bug in relay_open_buf`, type `WARNING`, alternatives `none`, flags `PANICKED=Y`, 86 log lines, 0 explicit report lines, and 4478 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
panic_on_warn/panic aftermath is present, so secondary panic stacks can obscure the root report; warning stacks may be followed by panic stacks and unrelated device logs.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `WARNING: kmalloc bug in relay_open_buf`, the crash type remains `WARNING`, alt titles remain `none`, and representative frames around `relay_open_buf` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/153 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/154 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/154

## Purpose
This is a syzkaller Linux report-parser fixture for `BUG: unable to handle kernel paging request in corrupted`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/154` so `pkg/report` can verify generic oops memory-safety coverage, where page-fault and NX traces are normalized into a stable bad-access title for TIPC networking.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `rb_first_postorder, dump_stack, arch_local_irq_restore, show_regs_print_info, print_address_description, kasan_report, __asan_report_load8_noabort, tipc_group_join`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `corrupted`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `BUG: unable to handle kernel paging request in corrupted`, type `MEMORY_SAFETY_BUG`, alternatives `bad-access in corrupted`, flags `CORRUPTED=Y, PANICKED=Y`, 159 log lines, 0 explicit report lines, and 8970 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
marked corrupted, so parser changes must continue to distinguish real frames from truncated, interleaved, or printk-dropped output; panic_on_warn/panic aftermath is present, so secondary panic stacks can obscure the root report; the title intentionally falls back to `corrupted`, which is a regression-sensitive signal for frame extraction failure.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `BUG: unable to handle kernel paging request in corrupted`, the crash type remains `MEMORY_SAFETY_BUG`, alt titles remain `bad-access in corrupted`, and representative frames around `corrupted` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/154 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/155 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/155

## Purpose
This is a syzkaller Linux report-parser fixture for `WARNING in ion_ioctl`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/155` so `pkg/report` can verify WARNING and panic_on_warn coverage, where the primary warning stack must be kept while secondary panic stacks are trimmed or tolerated for Android ION ioctl validation.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `ion_ioctl, dump_stack, arch_local_irq_restore, vsnprintf, panic, refcount_error_report, show_regs_print_info, __warn`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `ion_ioctl`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `WARNING in ion_ioctl`, type `WARNING`, alternatives `none`, flags `PANICKED=Y`, 65 log lines, 0 explicit report lines, and 3739 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
panic_on_warn/panic aftermath is present, so secondary panic stacks can obscure the root report; warning stacks may be followed by panic stacks and unrelated device logs.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `WARNING in ion_ioctl`, the crash type remains `WARNING`, alt titles remain `none`, and representative frames around `ion_ioctl` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/155 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/156 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/156

## Purpose
This is a syzkaller Linux report-parser fixture for `WARNING: bad unlock balance in ipmr_mfc_seq_stop`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/156` so `pkg/report` can verify lockdep and RCU/context validation coverage, where title extraction must preserve locking-context wording and the indicative kernel frame for IPv4 multicast routing seq-file iteration.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `ipmr_mfc_seq_stop, do_sendfile, seq_read, dump_stack, arch_local_irq_restore, print_unlock_imbalance_bug, lock_release, lock_downgrade`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `ipmr_mfc_seq_stop`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `WARNING: bad unlock balance in ipmr_mfc_seq_stop`, type `LOCKDEP`, alternatives `none`, flags `none`, 113 log lines, 0 explicit report lines, and 5889 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
lockdep messages often contain unrelated subsystem chatter that can be mistaken for the first report.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `WARNING: bad unlock balance in ipmr_mfc_seq_stop`, the crash type remains `LOCKDEP`, alt titles remain `none`, and representative frames around `ipmr_mfc_seq_stop` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/156 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/157 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/157

## Purpose
This is a syzkaller Linux report-parser fixture for `WARNING: refcount bug in sctp_wfree`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/157` so `pkg/report` can verify refcount_t warning coverage, where underflow or increment-on-zero text is mapped to a refcount crash type for SCTP socket lifetime and send-buffer handling.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `refcount_sub_and_test, dump_stack, arch_local_irq_restore, panic, __warn, show_regs_print_info, report_bug, fixup_bug`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `sctp_wfree`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `WARNING: refcount bug in sctp_wfree`, type `REFCOUNT_WARNING`, alternatives `none`, flags `PANICKED=Y`, 168 log lines, 0 explicit report lines, and 8329 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
panic_on_warn/panic aftermath is present, so secondary panic stacks can obscure the root report.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `WARNING: refcount bug in sctp_wfree`, the crash type remains `REFCOUNT_WARNING`, alt titles remain `none`, and representative frames around `sctp_wfree` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/157 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/158 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/158

## Purpose
This is a syzkaller Linux report-parser fixture for `WARNING: refcount bug in dev_activate`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/158` so `pkg/report` can verify refcount_t warning coverage, where underflow or increment-on-zero text is mapped to a refcount crash type for network device activation.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `refcount_inc, dump_stack, arch_local_irq_restore, panic, __warn, show_regs_print_info, retint_kernel, report_bug`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `dev_activate`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `WARNING: refcount bug in dev_activate`, type `REFCOUNT_WARNING`, alternatives `none`, flags `PANICKED=Y`, 113 log lines, 0 explicit report lines, and 10039 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
panic_on_warn/panic aftermath is present, so secondary panic stacks can obscure the root report.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `WARNING: refcount bug in dev_activate`, the crash type remains `REFCOUNT_WARNING`, alt titles remain `none`, and representative frames around `dev_activate` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/158 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/159 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/159

## Purpose
This is a syzkaller Linux report-parser fixture for `WARNING: refcount bug in l2tp_session_register`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/159` so `pkg/report` can verify refcount_t warning coverage, where underflow or increment-on-zero text is mapped to a refcount crash type for L2TP session/socket lifecycle.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `refcount_inc, dump_stack, arch_local_irq_restore, vsnprintf, panic, refcount_error_report, show_regs_print_info, __warn`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `l2tp_session_register`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `WARNING: refcount bug in l2tp_session_register`, type `REFCOUNT_WARNING`, alternatives `none`, flags `PANICKED=Y`, 85 log lines, 0 explicit report lines, and 4478 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
panic_on_warn/panic aftermath is present, so secondary panic stacks can obscure the root report.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `WARNING: refcount bug in l2tp_session_register`, the crash type remains `REFCOUNT_WARNING`, alt titles remain `none`, and representative frames around `l2tp_session_register` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/159 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/16 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/16

## Purpose
This is a syzkaller Linux report-parser fixture for `KASAN: use-after-free Write in remove_wait_queue`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/16` so `pkg/report` can verify KASAN use-after-free write coverage, including corrupted/truncated sanitizer output handling for wait-queue and lockdep interactions.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `remove_wait_queue`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `remove_wait_queue`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `KASAN: use-after-free Write in remove_wait_queue`, type `KASAN-USE-AFTER-FREE-WRITE`, alternatives `bad-access in remove_wait_queue`, flags `CORRUPTED=Y`, 2 log lines, 0 explicit report lines, and 301 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
marked corrupted, so parser changes must continue to distinguish real frames from truncated, interleaved, or printk-dropped output; sanitizer details are noisy but allocation/free metadata and access direction must remain parseable.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `KASAN: use-after-free Write in remove_wait_queue`, the crash type remains `KASAN-USE-AFTER-FREE-WRITE`, alt titles remain `bad-access in remove_wait_queue`, and representative frames around `remove_wait_queue` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/16 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/160 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/160

## Purpose
This is a syzkaller Linux report-parser fixture for `BUG: unable to handle kernel paging request in __run_timers`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/160` so `pkg/report` can verify generic oops memory-safety coverage, where page-fault and NX traces are normalized into a stable bad-access title for timer-list callback execution.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `call_timer_fn, __run_timers, irq_exit, run_timer_softirq, timers_dead_cpu, __do_softirq, exiting_irq, smp_apic_timer_interrupt`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `__run_timers`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `BUG: unable to handle kernel paging request in __run_timers`, type `MEMORY_SAFETY_BUG`, alternatives `bad-access in __run_timers`, flags `PANICKED=Y`, 110 log lines, 0 explicit report lines, and 5921 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
panic_on_warn/panic aftermath is present, so secondary panic stacks can obscure the root report.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `BUG: unable to handle kernel paging request in __run_timers`, the crash type remains `MEMORY_SAFETY_BUG`, alt titles remain `bad-access in __run_timers`, and representative frames around `__run_timers` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/160 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/161 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/161

## Purpose
This is a syzkaller Linux report-parser fixture for `WARNING: locking bug in destroy_unused_super`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/161` so `pkg/report` can verify lockdep and RCU/context validation coverage, where title extraction must preserve locking-context wording and the indicative kernel frame for VFS superblock teardown.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `lock_release, dump_stack, arch_local_irq_restore, vsnprintf, panic, refcount_error_report, show_regs_print_info, __warn`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `destroy_unused_super`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `WARNING: locking bug in destroy_unused_super`, type `LOCKDEP`, alternatives `none`, flags `PANICKED=Y`, 88 log lines, 0 explicit report lines, and 4497 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
panic_on_warn/panic aftermath is present, so secondary panic stacks can obscure the root report; lockdep messages often contain unrelated subsystem chatter that can be mistaken for the first report.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `WARNING: locking bug in destroy_unused_super`, the crash type remains `LOCKDEP`, alt titles remain `none`, and representative frames around `destroy_unused_super` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/161 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/162 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/162

## Purpose
This is a syzkaller Linux report-parser fixture for `general protection fault in sg_remove_request`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/162` so `pkg/report` can verify crash/oops denial-of-service coverage, where a kernel fault is expected even without a sanitizer-specific class for SCSI generic request teardown.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `__lock_acquire, handle_mm_fault, debug_check_no_locks_freed, vmacache_update, __do_page_fault, lock_acquire, sg_remove_request, _raw_write_lock_irqsave`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `sg_remove_request`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `general protection fault in sg_remove_request`, type `DoS`, alternatives `bad-access in sg_remove_request`, flags `none`, 61 log lines, 0 explicit report lines, and 4407 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
the main risk is title drift if Linux wording or stack formatting changes.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `general protection fault in sg_remove_request`, the crash type remains `DoS`, alt titles remain `bad-access in sg_remove_request`, and representative frames around `sg_remove_request` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/162 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/163 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/163

## Purpose
This is a syzkaller Linux report-parser fixture for `WARNING: locking bug in sg_remove_request`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/163` so `pkg/report` can verify lockdep and RCU/context validation coverage, where title extraction must preserve locking-context wording and the indicative kernel frame for SCSI generic request teardown.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `__lock_acquire, dump_stack, panic, percpu_up_read.constprop.46, warn_slowpath_common, warn_slowpath_fmt, save_trace, dump_trace`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `sg_remove_request`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `WARNING: locking bug in sg_remove_request`, type `LOCKDEP`, alternatives `none`, flags `PANICKED=Y`, 73 log lines, 0 explicit report lines, and 5035 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
panic_on_warn/panic aftermath is present, so secondary panic stacks can obscure the root report; lockdep messages often contain unrelated subsystem chatter that can be mistaken for the first report.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `WARNING: locking bug in sg_remove_request`, the crash type remains `LOCKDEP`, alt titles remain `none`, and representative frames around `sg_remove_request` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/163 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/164 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/164

## Purpose
This is a syzkaller Linux report-parser fixture for `KASAN: slab-out-of-bounds in native_queued_spin_lock_slowpath at addr ADDR`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/164` so `pkg/report` can verify KASAN read violation coverage, including slab, stack, or bounds reports for fasync/slab lifetime diagnostics.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `rw_verify_area, native_queued_spin_lock_slowpath, do_sendfile, ___slab_alloc.constprop.78, fasync_helper, run_ksoftirqd, fasync_free_rcu, __slab_free`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `native_queued_spin_lock_slowpath at addr ADDR`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `KASAN: slab-out-of-bounds in native_queued_spin_lock_slowpath at addr ADDR`, type `KASAN-READ`, alternatives `none`, flags `CORRUPTED=Y`, 66 log lines, 0 explicit report lines, and 7217 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
marked corrupted, so parser changes must continue to distinguish real frames from truncated, interleaved, or printk-dropped output; sanitizer details are noisy but allocation/free metadata and access direction must remain parseable.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `KASAN: slab-out-of-bounds in native_queued_spin_lock_slowpath at addr ADDR`, the crash type remains `KASAN-READ`, alt titles remain `none`, and representative frames around `native_queued_spin_lock_slowpath at addr ADDR` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/164 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/165 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/165

## Purpose
This is a syzkaller Linux report-parser fixture for `KASAN: use-after-free Read in shmem_disband_hugehead`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/165` so `pkg/report` can verify KASAN use-after-free read coverage, including allocation/free metadata and stack-frame extraction for tmpfs huge-page teardown.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `__lock_acquire, dump_stack, kasan_object_err, kasan_report_error, __asan_report_load8_noabort, set_next_entity, debug_check_no_locks_freed, finish_task_switch`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `shmem_disband_hugehead`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `KASAN: use-after-free Read in shmem_disband_hugehead`, type `KASAN-USE-AFTER-FREE-READ`, alternatives `bad-access in shmem_disband_hugehead`, flags `none`, 87 log lines, 0 explicit report lines, and 5965 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
sanitizer details are noisy but allocation/free metadata and access direction must remain parseable.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `KASAN: use-after-free Read in shmem_disband_hugehead`, the crash type remains `KASAN-USE-AFTER-FREE-READ`, alt titles remain `bad-access in shmem_disband_hugehead`, and representative frames around `shmem_disband_hugehead` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/165 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/166 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/166

## Purpose
This is a syzkaller Linux report-parser fixture for `WARNING: suspicious RCU usage in bpf_prog_array_copy_info`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/166` so `pkg/report` can verify lockdep and RCU/context validation coverage, where title extraction must preserve locking-context wording and the indicative kernel frame for BPF program-array query/copy path.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `perf_event_ctx_lock_nested, perf_event_query_prog_array, bpf_prog_array_copy_to_user, dump_stack, arch_local_irq_restore, lockdep_rcu_suspicious, ___might_sleep, trace_event_raw_event_sched_switch`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `bpf_prog_array_copy_info`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `WARNING: suspicious RCU usage in bpf_prog_array_copy_info`, type `LOCKDEP`, alternatives `none`, flags `none`, 116 log lines, 0 explicit report lines, and 6368 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
lockdep messages often contain unrelated subsystem chatter that can be mistaken for the first report.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `WARNING: suspicious RCU usage in bpf_prog_array_copy_info`, the crash type remains `LOCKDEP`, alt titles remain `none`, and representative frames around `bpf_prog_array_copy_info` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/166 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/167 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/167

## Purpose
This is a syzkaller Linux report-parser fixture for `BUG: unable to handle kernel paging request in snd_pcm_oss_write`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/167` so `pkg/report` can verify generic oops memory-safety coverage, where page-fault and NX traces are normalized into a stable bad-access title for ALSA OSS PCM write path.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `memset_erms, memset, _copy_from_user, snd_pcm_oss_write, snd_pcm_oss_ioctl_compat, __vfs_write, rcu_note_context_switch, kernel_read`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `snd_pcm_oss_write`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `BUG: unable to handle kernel paging request in snd_pcm_oss_write`, type `MEMORY_SAFETY_BUG`, alternatives `bad-access in snd_pcm_oss_write`, flags `PANICKED=Y`, 67 log lines, 0 explicit report lines, and 3877 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
panic_on_warn/panic aftermath is present, so secondary panic stacks can obscure the root report.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `BUG: unable to handle kernel paging request in snd_pcm_oss_write`, the crash type remains `MEMORY_SAFETY_BUG`, alt titles remain `bad-access in snd_pcm_oss_write`, and representative frames around `snd_pcm_oss_write` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/167 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/168 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/168

## Purpose
This is a syzkaller Linux report-parser fixture for `WARNING: ODEBUG bug in pppol2tp_release`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/168` so `pkg/report` can verify WARNING and panic_on_warn coverage, where the primary warning stack must be kept while secondary panic stacks are trimmed or tolerated for L2TP session/socket lifecycle.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `debug_print_object, dump_stack, arch_local_irq_restore, vsnprintf, panic, refcount_error_report, show_regs_print_info, __warn`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `pppol2tp_release`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `WARNING: ODEBUG bug in pppol2tp_release`, type `WARNING`, alternatives `none`, flags `PANICKED=Y`, 98 log lines, 0 explicit report lines, and 5155 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
panic_on_warn/panic aftermath is present, so secondary panic stacks can obscure the root report; warning stacks may be followed by panic stacks and unrelated device logs.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `WARNING: ODEBUG bug in pppol2tp_release`, the crash type remains `WARNING`, alt titles remain `none`, and representative frames around `pppol2tp_release` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/168 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/169 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/169

## Purpose
This is a syzkaller Linux report-parser fixture for `WARNING: bad usercopy in put_cmsg`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/169` so `pkg/report` can verify WARNING and panic_on_warn coverage, where the primary warning stack must be kept while secondary panic stacks are trimmed or tolerated for socket control-message usercopy.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `usercopy_warn, dump_stack, arch_local_irq_restore, vsnprintf, panic, refcount_error_report, show_regs_print_info, __warn`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `put_cmsg`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `WARNING: bad usercopy in put_cmsg`, type `WARNING`, alternatives `none`, flags `PANICKED=Y`, 85 log lines, 0 explicit report lines, and 4444 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
panic_on_warn/panic aftermath is present, so secondary panic stacks can obscure the root report; warning stacks may be followed by panic stacks and unrelated device logs.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `WARNING: bad usercopy in put_cmsg`, the crash type remains `WARNING`, alt titles remain `none`, and representative frames around `put_cmsg` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/169 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/17 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/17

## Purpose
This is a syzkaller Linux report-parser fixture for `KASAN: use-after-free Read in corrupted`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/17` so `pkg/report` can verify KASAN use-after-free read coverage, including allocation/free metadata and stack-frame extraction for parser corruption/truncation handling.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `copy_from_iter`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `corrupted`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `KASAN: use-after-free Read in corrupted`, type `KASAN-USE-AFTER-FREE-READ`, alternatives `bad-access in corrupted`, flags `CORRUPTED=Y`, 2 log lines, 0 explicit report lines, and 280 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
marked corrupted, so parser changes must continue to distinguish real frames from truncated, interleaved, or printk-dropped output; the title intentionally falls back to `corrupted`, which is a regression-sensitive signal for frame extraction failure; sanitizer details are noisy but allocation/free metadata and access direction must remain parseable.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `KASAN: use-after-free Read in corrupted`, the crash type remains `KASAN-USE-AFTER-FREE-READ`, alt titles remain `bad-access in corrupted`, and representative frames around `corrupted` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/17 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/170 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/170

## Purpose
This is a syzkaller Linux report-parser fixture for `WARNING: suspicious RCU usage in tipc_bearer_find`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/170` so `pkg/report` can verify lockdep and RCU/context validation coverage, where title extraction must preserve locking-context wording and the indicative kernel frame for TIPC networking.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `genl_rcv, genl_rcv_msg, dump_stack, arch_local_irq_restore, lockdep_rcu_suspicious, tipc_bearer_find, tipc_media_addr_printf, tipc_nl_compat_link_set`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `tipc_bearer_find`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `WARNING: suspicious RCU usage in tipc_bearer_find`, type `LOCKDEP`, alternatives `none`, flags `none`, 75 log lines, 0 explicit report lines, and 3680 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
lockdep messages often contain unrelated subsystem chatter that can be mistaken for the first report.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `WARNING: suspicious RCU usage in tipc_bearer_find`, the crash type remains `LOCKDEP`, alt titles remain `none`, and representative frames around `tipc_bearer_find` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/170 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/171 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/171

## Purpose
This is a syzkaller Linux report-parser fixture for `INFO: rcu detected stall in snd_pcm_oss_write`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/171` so `pkg/report` can verify hang/stall detection coverage, where the parser must recognize scheduler, hung-task, or RCU-stall reports without a normal oops footer for ALSA OSS PCM write path.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `sched_show_task, print_other_cpu_stall, check_cpu_stall.isra.61, rcu_check_callbacks, update_process_times, tick_sched_handle, tick_sched_timer, __hrtimer_run_queues`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `snd_pcm_oss_write`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `INFO: rcu detected stall in snd_pcm_oss_write`, type `HANG`, alternatives `stall in snd_pcm_oss_write`, flags `none`, 42 log lines, 0 explicit report lines, and 2554 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
hang reports lack the usual oops boundary and depend on scheduler/RCU wording.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `INFO: rcu detected stall in snd_pcm_oss_write`, the crash type remains `HANG`, alt titles remain `stall in snd_pcm_oss_write`, and representative frames around `snd_pcm_oss_write` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/171 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/172 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/172

## Purpose
This is a syzkaller Linux report-parser fixture for `KASAN: stack-out-of-bounds Read in xfrm_selector_match`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/172` so `pkg/report` can verify KASAN read violation coverage, including slab, stack, or bounds reports for xfrm policy/state selector matching.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `memcmp, dump_stack, arch_local_irq_restore, show_regs_print_info, find_held_lock, print_address_description, kasan_report, __asan_report_load1_noabort`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `xfrm_selector_match`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `KASAN: stack-out-of-bounds Read in xfrm_selector_match`, type `KASAN-READ`, alternatives `bad-access in xfrm_selector_match`, flags `none`, 190 log lines, 0 explicit report lines, and 20529 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
sanitizer details are noisy but allocation/free metadata and access direction must remain parseable.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `KASAN: stack-out-of-bounds Read in xfrm_selector_match`, the crash type remains `KASAN-READ`, alt titles remain `bad-access in xfrm_selector_match`, and representative frames around `xfrm_selector_match` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/172 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/173 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/173

## Purpose
This is a syzkaller Linux report-parser fixture for `WARNING: ODEBUG bug in unreserve_psock`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/173` so `pkg/report` can verify WARNING and panic_on_warn coverage, where the primary warning stack must be kept while secondary panic stacks are trimmed or tolerated for stream parser/KCM networking.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `strp_work, debug_print_object, dump_stack, arch_local_irq_restore, vsnprintf, panic, refcount_error_report, show_regs_print_info`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `unreserve_psock`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `WARNING: ODEBUG bug in unreserve_psock`, type `WARNING`, alternatives `none`, flags `PANICKED=Y`, 112 log lines, 0 explicit report lines, and 5614 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
panic_on_warn/panic aftermath is present, so secondary panic stacks can obscure the root report; warning stacks may be followed by panic stacks and unrelated device logs.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `WARNING: ODEBUG bug in unreserve_psock`, the crash type remains `WARNING`, alt titles remain `none`, and representative frames around `unreserve_psock` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/173 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/174 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/174

## Purpose
This is a syzkaller Linux report-parser fixture for `BUG: unable to handle kernel NULL pointer dereference in rtnl_dump_ifinfo`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/174` so `pkg/report` can verify null-pointer page-fault coverage with a stable bad-access alternative title for rtnetlink interface dump.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `strlen, rtnl_fill_ifinfo, rtnl_dump_ifinfo, netlink_dump, __netlink_dump_start, rtnetlink_rcv_msg, rtnl_getlink, validate_linkmsg`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `rtnl_dump_ifinfo`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `BUG: unable to handle kernel NULL pointer dereference in rtnl_dump_ifinfo`, type `NULL-POINTER-DEREFERENCE`, alternatives `bad-access in rtnl_dump_ifinfo`, flags `PANICKED=Y`, 70 log lines, 0 explicit report lines, and 5009 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
panic_on_warn/panic aftermath is present, so secondary panic stacks can obscure the root report.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `BUG: unable to handle kernel NULL pointer dereference in rtnl_dump_ifinfo`, the crash type remains `NULL-POINTER-DEREFERENCE`, alt titles remain `bad-access in rtnl_dump_ifinfo`, and representative frames around `rtnl_dump_ifinfo` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/174 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/175 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/175

## Purpose
This is a syzkaller Linux report-parser fixture for `BUG: unable to handle kernel paging request in ipcget`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/175` so `pkg/report` can verify generic oops memory-safety coverage, where page-fault and NX traces are normalized into a stable bad-access title for SysV IPC lookup.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `memcmp, ipcget, SyS_msgget, entry_SYSCALL_64_fastpath`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `ipcget`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `BUG: unable to handle kernel paging request in ipcget`, type `MEMORY_SAFETY_BUG`, alternatives `bad-access in ipcget`, flags `PANICKED=Y`, 39 log lines, 0 explicit report lines, and 2645 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
panic_on_warn/panic aftermath is present, so secondary panic stacks can obscure the root report.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `BUG: unable to handle kernel paging request in ipcget`, the crash type remains `MEMORY_SAFETY_BUG`, alt titles remain `bad-access in ipcget`, and representative frames around `ipcget` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/175 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/176 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/176

## Purpose
This is a syzkaller Linux report-parser fixture for `INFO: task hung in do_exit`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/176` so `pkg/report` can verify hang/stall detection coverage, where the parser must recognize scheduler, hung-task, or RCU-stall reports without a normal oops footer for task exit and mmap semaphore teardown.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `__schedule, __sched_text_start, check_noncircular, debug_check_no_locks_freed, print_irqtrace_events, schedule, lock_downgrade, lock_release`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `do_exit`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `INFO: task hung in do_exit`, type `HANG`, alternatives `hang in do_exit`, flags `none`, 81 log lines, 0 explicit report lines, and 4241 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
hang reports lack the usual oops boundary and depend on scheduler/RCU wording.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `INFO: task hung in do_exit`, the crash type remains `HANG`, alt titles remain `hang in do_exit`, and representative frames around `do_exit` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/176 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/177 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/177

## Purpose
This is a syzkaller Linux report-parser fixture for `KASAN: use-after-free Read in selinux_inode_free_security`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/177` so `pkg/report` can verify KASAN use-after-free read coverage, including allocation/free metadata and stack-frame extraction for SELinux inode security cleanup.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `do_raw_spin_lock, dump_stack, arch_local_irq_restore, show_regs_print_info, perf_trace_lock_acquire, print_address_description, kasan_report, __asan_report_load4_noabort`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `selinux_inode_free_security`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `KASAN: use-after-free Read in selinux_inode_free_security`, type `KASAN-USE-AFTER-FREE-READ`, alternatives `bad-access in selinux_inode_free_security`, flags `none`, 201 log lines, 0 explicit report lines, and 10036 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
sanitizer details are noisy but allocation/free metadata and access direction must remain parseable.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `KASAN: use-after-free Read in selinux_inode_free_security`, the crash type remains `KASAN-USE-AFTER-FREE-READ`, alt titles remain `bad-access in selinux_inode_free_security`, and representative frames around `selinux_inode_free_security` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/177 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/178 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/178

## Purpose
This is a syzkaller Linux report-parser fixture for `INFO: task hung in corrupted`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/178` so `pkg/report` can verify hang/stall detection coverage, where the parser must recognize scheduler, hung-task, or RCU-stall reports without a normal oops footer for parser corruption/truncation handling.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `__schedule, __sched_text_start, check_noncircular, __queue_work, insert_work`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `corrupted`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `INFO: task hung in corrupted`, type `HANG`, alternatives `hang in corrupted`, flags `CORRUPTED=Y`, 11 log lines, 0 explicit report lines, and 704 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
marked corrupted, so parser changes must continue to distinguish real frames from truncated, interleaved, or printk-dropped output; the title intentionally falls back to `corrupted`, which is a regression-sensitive signal for frame extraction failure; hang reports lack the usual oops boundary and depend on scheduler/RCU wording.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `INFO: task hung in corrupted`, the crash type remains `HANG`, alt titles remain `hang in corrupted`, and representative frames around `corrupted` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/178 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/179 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/179

## Purpose
This is a syzkaller Linux report-parser fixture for `INFO: task hung in synchronize_rcu`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/179` so `pkg/report` can verify hang/stall detection coverage, where the parser must recognize scheduler, hung-task, or RCU-stall reports without a normal oops footer for RCU grace-period synchronization.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `__schedule, __sched_text_start, lock_downgrade, lock_release, mark_held_locks, check_noncircular, trace_hardirqs_on, schedule`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `synchronize_rcu`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `INFO: task hung in synchronize_rcu`, type `HANG`, alternatives `INFO: task hung in synchronize_sched, hang in synchronize_rcu, hang in synchronize_sched`, flags `none`, 110 log lines, 0 explicit report lines, and 5604 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
hang reports lack the usual oops boundary and depend on scheduler/RCU wording.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `INFO: task hung in synchronize_rcu`, the crash type remains `HANG`, alt titles remain `INFO: task hung in synchronize_sched, hang in synchronize_rcu, hang in synchronize_sched`, and representative frames around `synchronize_rcu` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/179 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/18 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/18

## Purpose
This is a syzkaller Linux report-parser fixture for `KASAN: null-ptr-deref Read`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/18` so `pkg/report` can verify KASAN null-pointer read coverage with intentionally sparse legacy output for Linux crash-report parsing.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `none reliably extracted from this short/corrupted log`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `none isolated`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `KASAN: null-ptr-deref Read`, type `KASAN-NULL-POINTER-DEREFERENCE-READ`, alternatives `none`, flags `CORRUPTED=Y`, 5 log lines, 0 explicit report lines, and 307 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
marked corrupted, so parser changes must continue to distinguish real frames from truncated, interleaved, or printk-dropped output; sanitizer details are noisy but allocation/free metadata and access direction must remain parseable.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `KASAN: null-ptr-deref Read`, the crash type remains `KASAN-NULL-POINTER-DEREFERENCE-READ`, alt titles remain `none`, and representative frames around `none isolated` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/18 -->
