# subset-b-009485 Research

Grouped source research for Linux syzkaller report-parser fixtures under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report`. Each marker-delimited section preserves the original source path and is intended to be split unchanged into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/245 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/245

## Purpose
This fixture exercises syzkaller's Linux report parser on a long x86 stack-unwinder warning where the canonical title must be `WARNING: kernel stack regs has bad value`. The source is a 897-line console log dominated by raw `unwind stack type` frame dumps and ending with both `kernel stack regs ... bad 'bp' value` and `kernel stack frame pointer ... bad value` warnings.

## Important APIs, Types, and Functions
The file is data consumed by `ParseTest` in `pkg/report/report_test.go`, using only the `TITLE` header followed by raw log text. Parser APIs under test include `Reporter.Parse`, Linux oops matching, `findFirstOops`, title formatting, and the Linux suppression list. Kernel symbols that act as parser context include `__save_stack_trace`, `keccakf`, `save_trace`, `mark_lock`, `__lock_acquire`, `lock_sock_nested`, `__sys_bind`, `__x64_sys_sendto`, and syscall-return frames.

## Control Flow
The test harness reads the `TITLE` header, treats the remainder as the log, and asks the Linux reporter to find the first report signature. The reporter must ignore hundreds of pointer-value stack dump lines and choose the explicit warning near the end, without requiring a normal call trace because the matching oops rule is marked as a no-stack-trace report.

## State and Persistence Behavior
There is no mutable state. The persistent contract is the checked-in expected title and the specific raw log shape with sanitized `(ptrval)` tokens, repeated addresses, and two equivalent stack-register warnings.

## Dependencies and Integration Points
This fixture depends on the Linux oops table entries for `WARNING: kernel stack regs .* bad 'bp' value` and `WARNING: kernel stack frame pointer .* bad value`, plus generic printk prefix stripping and corruption detection. It integrates through `TestParse` and the Linux reporter selected for the test target.

## Risks and Edge Cases
The main risk is false extraction from the huge preceding stack dump, where many function-like tokens look like useful frames. Another risk is title drift if the parser starts preferring the later frame-pointer variant or demands stack traces for this warning family.

## Test Signals
A passing parse yields title `WARNING: kernel stack regs has bad value`, no explicit crash type, no panic/corruption flags, and a report beginning at the actual warning rather than at earlier `unwind stack type` data.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/245 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/246 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/246

## Purpose
This is a second large stack-unwinder fixture for the same normalized syzkaller title, `WARNING: kernel stack regs has bad value`. It provides a 1061-line variant with different surrounding kernel work, networking, and syscall frames so the no-stack-trace warning rule is not overfit to report 245.

## Important APIs, Types, and Functions
The data contract is the same `ParseTest` header/log format with a single `TITLE`. Parser paths include `Reporter.Parse`, Linux oops signature scanning, title normalization, and printk-prefix cleanup. Representative kernel symbols in the noise include `keccakf`, `rcu_is_watching`, `nf_hook_slow`, `ip_rcv`, `fd_install`, `__sys_accept4`, `__x64_sys_sendto`, `do_syscall_64`, and `entry_SYSCALL_64_after_hwframe`.

## Control Flow
`parseReport` reads the expected header, then the Linux reporter scans the raw log until it reaches the two terminal warnings: one for a bad frame pointer and one for bad `bp` stack regs. The intended parser control flow is to classify either spelling through the same no-stack-trace oops rule and emit the stable generic title.

## State and Persistence Behavior
The file persists a different raw kernel trace variant, including sanitized pointer values and networking/syscall frames, but it owns no runtime state. Expected state is the canonical title only; no `TYPE`, `PANICKED`, `CORRUPTED`, or explicit `REPORT` block is stored.

## Dependencies and Integration Points
It depends on the Linux report regex catalog, especially the stack-regs and stack-frame-pointer warning patterns, and on the generic test harness comparison of parsed fields. Integration is through the syzkaller Linux report testdata directory.

## Risks and Edge Cases
Because the actual warning is at EOF, parser truncation, scanner limits, or early false positives would regress this fixture. The file also checks that irrelevant NMI, RCU, lockdep, and syscall-looking entries do not become the selected title.

## Test Signals
Success means the parsed title remains `WARNING: kernel stack regs has bad value` and the report bounds include the terminal stack-register warning rather than the preceding function dump.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/246 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/247 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/247

## Purpose
This fixture verifies NULL program-counter oops parsing for an IPv4 send path crash. The expected title is `BUG: unable to handle kernel NULL pointer dereference in inet_sendmsg`, with alternate `bad-access in inet_sendmsg`, type `NULL-POINTER-DEREFERENCE`, and `PANICKED: Y`.

## Important APIs, Types, and Functions
The source uses `TITLE`, `ALT`, `TYPE`, and `PANICKED` headers. Parser code under test includes Linux page-fault/oops matchers, frame extraction, crash type mapping, and panic detection. Kernel frames include `inet_autobind`, `inet_sendmsg`, `sock_sendmsg`, `___sys_sendmsg`, `__sys_sendmsg`, `SyS_sendmsg`, and `system_call_fastpath`.

## Control Flow
The reporter encounters `BUG: unable to handle kernel NULL pointer dereference at (null)`, a null `RIP`, register dump, stack, and call trace. Because the raw instruction pointer is null, the parser must walk the call trace and choose `inet_sendmsg` as the meaningful frame, then notice the later `Kernel panic - not syncing: Fatal exception`.

## State and Persistence Behavior
The file has no mutable state. Persistent expected state is the normalized title, alternate bad-access title, crash type, and panic flag. Dynamic machine names, task pointers, and trace ids are retained only as raw fixture input.

## Dependencies and Integration Points
It depends on Linux oops parsing, bad-access title generation, `crash.TitleToType`, panic-line detection, and `TestParse` field comparison.

## Risks and Edge Cases
The null `RIP` and `Code: Bad RIP value` lines are not useful frames; using them directly would produce an empty or `(null)` title. Secondary lockdep helper frames must not displace `inet_sendmsg`.

## Test Signals
Regression checks are stable title, type `NULL-POINTER-DEREFERENCE`, alt title `bad-access in inet_sendmsg`, and `PANICKED: Y`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/247 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/248 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/248

## Purpose
This fixture covers suspicious RCU usage detection in IPv6 flow-label socket-option handling. The expected title is `INFO: suspicious RCU usage in ipv6_flowlabel_opt`.

## Important APIs, Types, and Functions
The file uses a `TITLE` header and a raw lockdep RCU warning. Parser paths include Linux info-report matching, RCU suspicious usage regexes, function extraction from lockdep reports, and printk cleanup. Important kernel symbols include `do_ipv6_setsockopt.isra.13`, `ipv6_flowlabel_opt`, `dump_stack`, `lockdep_rcu_suspicious.cold.44`, `ipv6_setsockopt`, `tcp_setsockopt`, `sock_common_setsockopt`, and `SyS_setsockopt`.

## Control Flow
The reporter sees `[ INFO: suspicious RCU usage. ]`, the file and line `/linux/net/ipv6/ip6_flowlabel.c:543`, lock context, then a call trace. The Linux matcher must classify the report as informational lockdep/RCU output and use `ipv6_flowlabel_opt` from the stack rather than generic lockdep helper frames.

## State and Persistence Behavior
No state is mutated. The durable test contract is the title and raw log; there are no explicit crash type, panic, corruption, or report-boundary headers.

## Dependencies and Integration Points
The fixture depends on syzkaller's Linux RCU suspicious-use patterns and stack parser. It integrates with `TestParse` through the standard report testdata directory.

## Risks and Edge Cases
`debug_locks = 0` and multiple lock lines can make the report look like general lockdep noise. The parser must not suppress it as harmless RCU chatter or title it after `lockdep_rcu_suspicious`.

## Test Signals
A passing parse returns the exact title `INFO: suspicious RCU usage in ipv6_flowlabel_opt` and selects the subsystem frame from the trace.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/248 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/249 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/249

## Purpose
This fixture checks warning parsing for a sleep-in-invalid-state report reached through `rfkill_fop_read`. The expected title is `WARNING in rfkill_fop_read`, type `WARNING`, and `PANICKED: Y`.

## Important APIs, Types, and Functions
Headers include `TITLE`, `TYPE`, and `PANICKED`. Parser components include generic WARNING extraction, frame selection, panic-on-warn detection, and crash type mapping. The kernel stack includes `__might_sleep`, `prepare_to_wait_event`, `panic`, `warn_slowpath_common`, `warn_slowpath_fmt`, `mutex_lock_nested`, `rfkill_fop_read`, `do_loop_readv_writev`, `do_readv_writev`, `vfs_readv`, and `SyS_readv`.

## Control Flow
The Linux reporter starts at `WARNING: CPU... __might_sleep`, observes the explanatory line about blocking ops when not `TASK_RUNNING`, then traverses the call trace. Although panic frames appear early because `panic_on_warn` is set, the report title must use the non-helper frame `rfkill_fop_read`.

## State and Persistence Behavior
The checked-in state is a compact raw kernel warning plus expected metadata. There is no executable state, persistence, or mutation beyond the fixture file.

## Dependencies and Integration Points
This depends on warning-pattern extraction, skip lists for generic warn/panic helpers, and panic line recognition. It integrates through `Reporter.Parse` and `ParseTest.Equal`.

## Risks and Edge Cases
Panic-on-warn stack frames can obscure the original warning site. The parser must also avoid choosing scheduler helper frames such as `__might_sleep` when a better subsystem frame exists.

## Test Signals
Stable signals are title `WARNING in rfkill_fop_read`, type `WARNING`, and panic flag set.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/249 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/25 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/25

## Purpose
This minimal fixture verifies that a malformed or too-short WARNING report is classified as corrupted. The expected title is `WARNING in corrupted`, type `WARNING`, and `CORRUPTED: Y`.

## Important APIs, Types, and Functions
The file uses `TITLE`, `TYPE`, and `CORRUPTED` headers followed by a single warning line at `genl_unbind+0x110/0x130`. Parser code under test includes generic WARNING matching, corruption detection for incomplete reports, and fallback title formatting.

## Control Flow
The harness reads the headers and passes one log line to the Linux reporter. The reporter can identify a warning signature but has no full call trace or report context, so it must preserve the warning type while marking the result corrupted and using the synthetic `corrupted` frame.

## State and Persistence Behavior
The file persists only the expected corrupted parse result and one printk line. It has no mutable state.

## Dependencies and Integration Points
It depends on generic Linux warning regexes, report-boundary validation, and `ParseTest` support for the `CORRUPTED` flag.

## Risks and Edge Cases
If the parser becomes too permissive it may emit `genl_unbind` as a normal warning, hiding truncated-report handling regressions. If it becomes too strict it may miss that the log is still a warning.

## Test Signals
A passing parse keeps `TYPE: WARNING`, marks `CORRUPTED: Y`, and returns title `WARNING in corrupted`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/25 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/250 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/250

## Purpose
This lockdep fixture verifies circular-locking report parsing for the loop block-device path. The expected title is `possible deadlock in blkdev_reread_part` and type `LOCKDEP`.

## Important APIs, Types, and Functions
The source uses `TITLE` and `TYPE` headers. Parser paths include Linux lockdep circular-dependency matching, lock-chain report extraction, frame selection, and type mapping to `LOCKDEP`. Key symbols include `blkdev_reread_part`, `lo_compat_ioctl`, `lo_release`, `__blkdev_put`, `lo_open`, `__blkdev_get`, `loop_reread_partitions`, `loop_set_status`, `compat_blkdev_ioctl`, and `entry_SYSENTER_compat`.

## Control Flow
The reporter sees `WARNING: possible circular locking dependency detected`, reads the attempted lock `&bdev->bd_mutex`, the held lock `&lo->lo_ctl_mutex#2`, the reverse dependency chain, the unsafe locking scenario, and the stack backtrace. It must title the report from the acquisition site `blkdev_reread_part`, not from lockdep helper frames.

## State and Persistence Behavior
There is no runtime state. The fixture persists one complete lockdep report including lock classes, dependency chain, and 32-bit compat syscall context.

## Dependencies and Integration Points
It depends on syzkaller's lockdep oops patterns, stack-frame parsing, and `crash.Type` conversion. Integration is via `TestParse` on Linux report fixtures.

## Risks and Edge Cases
The report contains multiple historical stack traces for lock classes before the final backtrace. Parser changes can accidentally choose `lo_release` or `lo_open` instead of the current acquisition frame.

## Test Signals
The parse must return title `possible deadlock in blkdev_reread_part` with type `LOCKDEP` and no panic/corruption flags.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/250 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/251 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/251

## Purpose
This is a negative/noise fixture for perf NMI throttling output. It begins with a blank header section and contains only `INFO: NMI handler ... took too long ... lowering kernel.perf_event_max_sample_rate`, so the expected parsed report is empty.

## Important APIs, Types, and Functions
The important harness behavior is `parseReport` entering log mode immediately because the file starts with a blank line. Parser code under test is the Linux suppression list, particularly patterns for `INFO: NMI handler` and `(handler|interrupt).*took too long`.

## Control Flow
The test harness records no expected `TITLE` or type. `Reporter.Parse` scans the single INFO line and must suppress it as benign performance-throttling noise instead of creating a crash report.

## State and Persistence Behavior
The file persists a two-line raw log and no expected metadata. It has no mutable state.

## Dependencies and Integration Points
It depends on Linux report suppression regexes in `linux.go` and on `testFromReport(nil)` producing an empty `ParseTest` for comparison.

## Risks and Edge Cases
The line includes typo-like `peperf: interrupt` text and numeric threshold values, so overly narrow suppression patterns may regress and report it as a crash.

## Test Signals
Success is no parsed report: empty title, unknown type, no flags, and no report body.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/251 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/252 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/252

## Purpose
This negative fixture verifies that a standard perf NMI latency message is ignored. The log says `INFO: NMI handler (perf_event_nmi_handler) took too long to run: 2.277 msecs` and has no expected title.

## Important APIs, Types, and Functions
The key interfaces are the blank-header `ParseTest` contract and Linux suppression regexes for `INFO: NMI handler` and long-running handlers. `perf_event_nmi_handler` is data text, not a kernel crash frame to title.

## Control Flow
`parseReport` stores the INFO line as raw log. The Linux reporter scans it, matches suppression/noise logic, and should return nil so the expected empty `ParseTest` compares equal.

## State and Persistence Behavior
The fixture is immutable raw text with no expected metadata and no runtime state.

## Dependencies and Integration Points
It integrates with the Linux report parser's benign-info filtering and the generic test harness nil-report handling.

## Risks and Edge Cases
If the parser treats every `INFO:` line as a report, this file would produce a false positive. If suppression is too broad, adjacent real INFO reports such as RCU stalls must still parse, so this fixture constrains the benign subset.

## Test Signals
The only acceptable output is no report: empty title, empty alternatives, unknown type, and all flags false.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/252 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/253 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/253

## Purpose
This negative fixture covers corrupted/interleaved console text that resembles a perf NMI warning but is not a kernel crash. It has no headers and must parse as no report.

## Important APIs, Types, and Functions
The relevant parser pieces are blank-header fixture handling, Linux suppression patterns for NMI handler messages, and robustness against garbled printk text. The recognizable token is `perf_event_nmi_handler`; the rest of the line is intentionally scrambled.

## Control Flow
The harness reads the garbled line as raw log with no expected title. The reporter must not manufacture a crash title from malformed `INFO:` content, and it must tolerate the unusual spacing and mixed fragments without corruption failures.

## State and Persistence Behavior
The file persists one raw noise line. It has no stateful behavior.

## Dependencies and Integration Points
It depends on syzkaller's Linux noise filtering and on scanner/test harness behavior for files with an initial blank line.

## Risks and Edge Cases
Too-strict text matching could stop suppressing this noisy line, while too-broad matching could hide real garbled kernel crashes. This fixture specifically guards the perf-NMI noise path.

## Test Signals
The expected parse is empty: no title, type, panic, corruption, or report body.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/253 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/254 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/254

## Purpose
This fixture verifies hung-task parsing for console device opens. The expected title is `INFO: task hung in console_device`, alternate `hang in console_device`, type `HANG`, and `PANICKED: Y`.

## Important APIs, Types, and Functions
Headers include `TITLE`, `ALT`, `TYPE`, and `PANICKED`. Parser functions under test include hung-task detection, stack extraction, alternate hang-title generation, and panic detection. Important symbols include `schedule`, `schedule_timeout`, `__down`, `down`, `console_lock`, `console_device`, `tty_open`, `chrdev_open`, `do_dentry_open`, `path_openat`, `SyS_open`, `watchdog`, and `panic`.

## Control Flow
The reporter sees an `INFO: task init... blocked for more than 120 seconds` section, repeated blocked `init` task stacks, NMI backtraces, and a final hung-task panic. It must choose the blocked task's meaningful wait site `console_device`, not the later NMI or khungtaskd panic stack.

## State and Persistence Behavior
The fixture persists a large multi-task console log. No runtime state is owned; expected state is the HANG classification, alt title, and panic flag.

## Dependencies and Integration Points
It depends on Linux hung-task regexes, stack collapsing for repeated tasks, panic-line detection, and skip lists for scheduler/wait helpers.

## Risks and Edge Cases
Multiple call traces and NMI backtraces can lure the parser to `io_serial_in`, `watchdog`, or `panic`. The repeated `<Same stack>` style also tests report boundary robustness.

## Test Signals
Stable output is title `INFO: task hung in console_device`, type `HANG`, alt `hang in console_device`, and `PANICKED: Y`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/254 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/255 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/255

## Purpose
This is another hung-task console-device fixture, from a different 4.4 kernel log. It should parse to `INFO: task hung in console_device`, alternate `hang in console_device`, type `HANG`, and `PANICKED: Y`.

## Important APIs, Types, and Functions
The file uses standard report headers and a raw hung-task log. Parser paths include task-hang oops matching, blocked-task stack extraction, title normalization, and panic detection. Representative symbols include `schedule`, `schedule_timeout`, `__down`, `down`, `console_lock`, `console_device`, `tty_open`, `chrdev_open`, `do_dentry_open`, `path_openat`, `do_sys_open`, `SyS_open`, and `watchdog`.

## Control Flow
The Linux reporter starts at the `INFO: task init:1 blocked for more than 120 seconds` section, extracts the blocked stack through `console_lock` and `console_device`, then observes NMI backtraces and the `Kernel panic - not syncing: hung_task: blocked tasks` line. The chosen title must remain tied to the blocked task, not the watchdog/panic section.

## State and Persistence Behavior
The fixture stores expected metadata and a 168-line raw log. No mutable state or persistence beyond checked-in test data exists.

## Dependencies and Integration Points
It depends on hung-task parser rules, function skip lists, panic recognition, and generic `ParseTest` comparison.

## Risks and Edge Cases
Because it is similar to report 254 but not identical, it guards against overfitting to one kernel's symbol offsets and against selecting NMI backtrace frames.

## Test Signals
The expected parse is the same HANG title/alt/panic tuple centered on `console_device`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/255 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/256 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/256

## Purpose
This fixture verifies NULL pointer dereference parsing in the socket polling path. The expected title is `BUG: unable to handle kernel NULL pointer dereference in sock_poll`, alt `bad-access in sock_poll`, type `NULL-POINTER-DEREFERENCE`, and `PANICKED: Y`.

## Important APIs, Types, and Functions
The raw log is a KASAN-enabled oops with `BUG: unable to handle kernel NULL pointer dereference at 0000000000000000`. Parser pieces include page-fault matching, stack frame extraction, bad-access alternate generation, panic detection, and crash type mapping. Key symbols include `smc_poll`, `ep_insert`, `__x64_sys_epoll_ctl`, `sock_poll`, `vfs_poll`, `ep_item_poll.isra.15`, `__mutex_lock`, and `do_syscall_64`.

## Control Flow
The reporter must handle a null `RIP`, stack data, call trace, module/end-trace lines, and a final fatal-exception panic. The meaningful title frame is `sock_poll`, even though `smc_poll` and epoll allocation frames appear around it.

## State and Persistence Behavior
No state is mutated. Persistent expected state is title, alt title, null-deref type, and panic flag.

## Dependencies and Integration Points
It depends on Linux oops regexes, stack parsing, KASAN/noise tolerance, and `crash.TitleToType`.

## Risks and Edge Cases
The parser could select `smc_poll` or an epoll helper if frame scoring changes. The repeated RIP/user-register sections must not create a second report.

## Test Signals
Success is stable `sock_poll` title and alt, `NULL-POINTER-DEREFERENCE`, and panic flag true.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/256 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/257 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/257

## Purpose
This compact fixture checks the warning spelling for returning to user space while a lock is held. The expected title is `WARNING: lock held when returning to user space in fuse_lock_inode` and type `LOCKDEP`.

## Important APIs, Types, and Functions
Headers include `TITLE` and `TYPE`. Parser coverage targets the Linux regex for `WARNING: lock held when returning to user space`, its `leaving the kernel with locks still held` detail, and function extraction from `at: fuse_lock_inode+0xaf/0xe0`.

## Control Flow
The reporter sees the warning line, process context, the explanatory lock-held line, and the `at:` location. It does not need a full call trace; the oops-specific matcher extracts `fuse_lock_inode` directly.

## State and Persistence Behavior
The fixture stores a 10-line raw warning and expected lockdep classification. It has no runtime state.

## Dependencies and Integration Points
It depends on the Linux lock-held warning rule in `linux.go` and the generic report test harness.

## Risks and Edge Cases
The report is intentionally short; requiring a full stack would mark it corrupted. The title must retain the `WARNING:` prefix and not be rewritten to the `BUG:` variant.

## Test Signals
Expected output is title `WARNING: lock held when returning to user space in fuse_lock_inode` and type `LOCKDEP`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/257 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/258 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/258

## Purpose
This compact fixture checks the BUG spelling of the lock-held-on-return report. The expected title is `BUG: lock held when returning to user space in fuse_lock_inode`.

## Important APIs, Types, and Functions
The file uses only a `TITLE` header. Parser coverage targets the Linux matcher for `[ BUG: lock held when returning to user space! ]`, the detail line `leaving the kernel with locks still held`, and the `at: fuse_lock_inode+0xa2/0xd0` frame. A distractor `somethingelse+0xa2/0xd0` appears after the real frame.

## Control Flow
The Linux reporter matches the BUG-form title, reads the subsequent details, extracts `fuse_lock_inode` from the `at:` line, and stops before the unrelated trailing symbol.

## State and Persistence Behavior
No state is owned. The persistent test data is the short raw log and expected title, with no explicit type or flags.

## Dependencies and Integration Points
It depends on the Linux BUG lock-held regex and function extraction rules in `pkg/report/linux.go`.

## Risks and Edge Cases
The nearby `somethingelse` line is a guard against choosing a later arbitrary symbol. The short input also tests no-stack report handling.

## Test Signals
A passing parse returns exactly `BUG: lock held when returning to user space in fuse_lock_inode`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/258 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/259 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/259

## Purpose
This fixture verifies warning parsing for a kmalloc-size bug reached through extended attribute retrieval. The expected title is `WARNING: kmalloc bug in vfs_getxattr_alloc`, type `WARNING`, and `PANICKED: Y`.

## Important APIs, Types, and Functions
The raw log starts at `WARNING: CPU... mm/slab_common.c:1031 kmalloc_slab` and immediately includes `panic_on_warn set`. Parser pieces include warning extraction, panic-on-warn handling, and selecting a meaningful non-helper frame. Key symbols include `kmalloc_slab`, `panic`, `__warn.cold.8`, `do_invalid_op`, `vfs_getxattr_alloc`, `__kmalloc_track_caller`, `krealloc`, `cap_inode_getsecurity`, and `security_inode_getsecurity`.

## Control Flow
The reporter encounters a warning in allocation internals, then walks the stack past warn/panic helpers and allocation helpers to title the report at `vfs_getxattr_alloc`. User-space register tail lines must remain part of the same report.

## State and Persistence Behavior
The fixture persists expected metadata and a raw warning log. There is no runtime state.

## Dependencies and Integration Points
It depends on Linux warning rules, helper-frame suppression, panic detection, and crash type mapping to `WARNING`.

## Risks and Edge Cases
Allocation helper frames such as `kmalloc_slab`, `__kmalloc_track_caller`, and `krealloc` can obscure the higher-level xattr operation. The panic-on-warn section appears before the useful frame.

## Test Signals
The parser must return `WARNING: kmalloc bug in vfs_getxattr_alloc`, type `WARNING`, and panic flag true.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/259 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/26 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/26

## Purpose
This older lockdep fixture covers the same loop-device circular dependency as report 250 on a 4.14-era kernel. The expected title is `possible deadlock in blkdev_reread_part` and type `LOCKDEP`.

## Important APIs, Types, and Functions
Headers include `TITLE` and `TYPE`. Parser paths include circular locking dependency detection and lockdep stack extraction. Key symbols include `blkdev_reread_part`, `lo_compat_ioctl`, `__lock_acquire`, `lo_release`, `__blkdev_put`, `loop_reread_partitions`, `loop_set_status`, `loop_set_status_compat`, `compat_blkdev_ioctl`, `compat_SyS_ioctl`, and `entry_SYSENTER_compat`.

## Control Flow
The reporter identifies `WARNING: possible circular locking dependency detected`, reads the lock chain and stack backtrace, and chooses `blkdev_reread_part` as the acquisition site responsible for the title.

## State and Persistence Behavior
The source is an immutable 82-line lockdep log. Expected state is the lockdep title/type; no panic or corruption flag is stored.

## Dependencies and Integration Points
It depends on Linux lockdep regexes and generic `ParseTest` comparison, and complements report 250 with a different kernel's output style.

## Risks and Edge Cases
Kernel-version differences in syscall labels and lockdep helper names should not change the normalized title. Parser frame scoring must not pick `lo_compat_ioctl`.

## Test Signals
Stable output is `possible deadlock in blkdev_reread_part` with `TYPE: LOCKDEP`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/26 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/260 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/260

## Purpose
This fixture verifies general-protection-fault parsing for a 9p connection cancellation path. The expected title is `general protection fault in p9_conn_cancel`, alt `bad-access in p9_conn_cancel`, type `DoS`, and `PANICKED: Y`.

## Important APIs, Types, and Functions
The log includes KASAN configuration lines, `general protection fault: 0000`, register dump, call trace, and fatal panic. Parser paths include GPF matching, frame selection, bad-access alt generation, and panic detection. Key symbols include `perf_trace_lock`, `perf_trace_lock_acquire`, `find_held_lock`, `__lock_acquire`, `lock_release`, `p9_conn_cancel`, `p9_fd_cancelled`, `p9_poll_workfn`, `process_one_work`, and worker-thread frames.

## Control Flow
The first RIP is in tracing/lock instrumentation, but the call trace includes the 9p cancellation path. The reporter must step past instrumentation and lockdep helpers to title the report at `p9_conn_cancel`, then record the later fatal-exception panic.

## State and Persistence Behavior
The persistent contract is title, alt, type `DoS`, and panic flag over a 119-line raw log. No mutable state is present.

## Dependencies and Integration Points
It depends on Linux GPF oops patterns, stack-frame skip lists, KASAN/noise handling, panic detection, and syzkaller crash-type mapping.

## Risks and Edge Cases
Instrumentation frames are prominent and could be chosen incorrectly. The report also mixes workqueue context and lock tracing, which tests parser resilience against noisy helper stacks.

## Test Signals
Expected output centers on `p9_conn_cancel`, includes `bad-access in p9_conn_cancel`, maps to `DoS`, and marks `PANICKED: Y`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/260 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/261 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/261

## Purpose
This fixture verifies KASAN use-after-free write parsing for ALSA timer callbacks. The expected title is `KASAN: use-after-free Write in snd_timer_user_interrupt`, alt `bad-access in snd_timer_user_interrupt`, and type `KASAN-USE-AFTER-FREE-WRITE`.

## Important APIs, Types, and Functions
The source uses `TITLE`, `ALT`, and `TYPE` headers. Parser paths include KASAN report matching, access kind extraction, stack classification, and alternate bad-access generation. Important symbols include `register_lock_class`, `kasan_report.cold.6`, `__asan_report_store8_noabort`, `__lock_acquire`, `snd_seq_check_queue.part.4`, `snd_timer_user_interrupt`, `snd_timer_interrupt`, `snd_hrtimer_callback`, and hrtimer/APIC frames.

## Control Flow
The reporter starts from `BUG: KASAN: use-after-free in register_lock_class`, then uses the stack and KASAN write metadata to identify the relevant ALSA timer user interrupt frame. It must ignore generic lock-class registration frames in the report headline.

## State and Persistence Behavior
The file persists one KASAN crash report with expected title, alt, and type. It has no mutable state.

## Dependencies and Integration Points
It depends on KASAN parser rules, write/read access typing, frame skip lists, and crash type mapping.

## Risks and Edge Cases
The textual KASAN headline names `register_lock_class`, while the expected syzkaller title names `snd_timer_user_interrupt`; parser frame selection is therefore the critical behavior under test.

## Test Signals
The output must be the ALSA timer title, alt `bad-access in snd_timer_user_interrupt`, and type `KASAN-USE-AFTER-FREE-WRITE`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/261 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/262 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/262

## Purpose
This negative fixture ensures Android userspace/debug output and benign audio driver messages do not become Linux kernel crash reports. It has no expected headers and should parse as an empty report.

## Important APIs, Types, and Functions
The log contains `DEBUG:` backtrace lines for Android libraries such as `libart.so`, `libandroid_runtime.so`, `app_process64`, and `libc.so`, plus `audio_aio_open` and `audio_open` messages. Parser behavior under test is filtering of non-kernel userspace stack text.

## Control Flow
Because the file starts with a blank line, the harness records no expected metadata. The Linux reporter scans the userspace frames and audio messages and should return nil rather than treating function-like C++ symbols as kernel frames.

## State and Persistence Behavior
The fixture is immutable noise text with no expected title, type, or flags. It owns no state.

## Dependencies and Integration Points
It depends on Linux report parser boundaries, suppression/noise handling, and nil-report comparison in `report_test.go`.

## Risks and Edge Cases
The C++ symbols contain namespaces, shared-library paths, and offsets that can look like stack frames. A permissive parser could false-positive on them.

## Test Signals
The correct parse is empty: no title, no type, no report body, and all flags false.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/262 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/263 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/263

## Purpose
This fixture verifies RCU stall parsing for ALSA sequencer writes. The expected title is `INFO: rcu detected stall in snd_seq_write`, alt `stall in snd_seq_write`, and type `HANG`.

## Important APIs, Types, and Functions
Headers include `TITLE`, `ALT`, and `TYPE`. Parser paths include RCU stall detection, NMI backtrace parsing, hang-title normalization, and frame selection. Key symbols include `dump_stack`, `nmi_cpu_backtrace`, `rcu_dump_cpu_stacks`, `print_cpu_stall`, `rcu_check_callbacks`, `lock_release`, `__might_fault`, `_copy_from_user`, `snd_seq_write`, `__vfs_write`, `vfs_write`, and `__x64_sys_write`.

## Control Flow
The reporter sees a self-detected `rcu_sched` CPU stall, NMI backtrace, interrupt frames, then the stalled task stack. It must title the hang at `snd_seq_write`, not at RCU timer or interrupt helper frames.

## State and Persistence Behavior
The fixture has no mutable state. Expected persistent metadata is title, alt title, and `HANG` type over an 85-line raw log.

## Dependencies and Integration Points
It depends on Linux RCU stall regexes, stack parsing across IRQ boundaries, and hang crash-type mapping.

## Risks and Edge Cases
The first stack section belongs to RCU/NMI machinery; the parser must find the task frame after interrupt unwinding. User copy and write helpers are nearby lower-value frames.

## Test Signals
Stable output is `INFO: rcu detected stall in snd_seq_write`, alt `stall in snd_seq_write`, and type `HANG`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/263 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/264 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/264

## Purpose
This fixture tests soft-lockup parsing for directory removal. The expected title is `BUG: soft lockup in sys_rmdir`, alternates for `__x64_sys_rmdir` and generic stall spellings, type `HANG`, and `PANICKED: Y`.

## Important APIs, Types, and Functions
Headers include `TITLE`, multiple `ALT` entries, `TYPE`, and `PANICKED`. Parser paths include watchdog soft-lockup matching, syscall-name normalization, alternate title generation, and panic detection. Important symbols include `d_walk`, `shrink_dcache_parent`, `vfs_rmdir`, `do_rmdir`, `__x64_sys_rmdir`, `select_collect`, `dump_stack`, `panic`, `watchdog_timer_fn.cold.5`, and hrtimer/APIC frames.

## Control Flow
The reporter reads a `watchdog: BUG: soft lockup` report, task register dump, call trace through the rmdir path, a second CPU stack, and a final softlockup panic. It must normalize the syscall-facing title to `sys_rmdir` while retaining alternates for the concrete `__x64_sys_rmdir` frame.

## State and Persistence Behavior
The file persists a 110-line soft-lockup log and expected hang metadata. It has no mutable state.

## Dependencies and Integration Points
It depends on Linux soft-lockup patterns, syscall alias normalization, panic recognition, and alternate-title sorting in the test harness.

## Risks and Edge Cases
Multiple CPUs and the later panic stack can displace the original stalled task. The syscall alias logic must stay stable across old `sys_*` and newer `__x64_sys_*` names.

## Test Signals
Expected output includes title `BUG: soft lockup in sys_rmdir`, all listed alternates, type `HANG`, and panic flag true.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/264 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/265 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/265

## Purpose
This fixture verifies soft-lockup parsing in ALSA raw MIDI writes. The expected title is `BUG: soft lockup in snd_rawmidi_write`, alternate `stall in snd_rawmidi_write`, type `HANG`, and `PANICKED: Y`.

## Important APIs, Types, and Functions
The raw log contains a watchdog soft lockup, panic, and later RCU stall output. Parser paths include soft-lockup matching, hang alt generation, panic detection, and report-boundary handling. Key symbols include `_raw_spin_unlock_irqrestore`, `snd_virmidi_output_trigger`, `snd_rawmidi_kernel_write1`, `snd_rawmidi_write`, `__vfs_write`, `vfs_write`, `ksys_write`, `SyS_write`, `watchdog_timer_fn.cold.5`, and printk/console functions.

## Control Flow
The reporter must take the first soft-lockup report, select `snd_rawmidi_write` from the stalled task stack, record the panic, and not let the later RCU stall or console printing stack retitle the report.

## State and Persistence Behavior
The fixture persists a 153-line mixed softlockup/RCU/panic log. Expected state is the HANG title, alt, and panic flag.

## Dependencies and Integration Points
It depends on Linux watchdog soft-lockup regexes, stack parser skip lists, panic detection, and hang classification.

## Risks and Edge Cases
The log includes secondary RCU stall diagnostics after the panic, which can look like another hang report. The parser must preserve first-crash semantics.

## Test Signals
Stable parse returns `BUG: soft lockup in snd_rawmidi_write`, alt `stall in snd_rawmidi_write`, type `HANG`, and `PANICKED: Y`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/265 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/266 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/266

## Purpose
This shorter soft-lockup fixture covers the rmdir path without a panic flag. Expected title is `BUG: soft lockup in sys_rmdir`, with alternates for `__x64_sys_rmdir` and stall spellings, and type `HANG`.

## Important APIs, Types, and Functions
Headers include `TITLE`, three `ALT` entries, and `TYPE`. Parser paths include soft-lockup matching, syscall normalization, alternate generation, and stack parsing. Key symbols include `d_walk`, `check_memory_region`, `_raw_spin_unlock`, `shrink_dcache_parent`, `vfs_rmdir`, `do_rmdir`, `__x64_sys_rmdir`, `do_syscall_64`, and `entry_SYSCALL_64_after_hwframe`.

## Control Flow
The reporter reads one watchdog soft-lockup report and extracts the rmdir stack. Unlike report 264, there is no subsequent panic line, so the parser must leave `PANICKED` false while still classifying the hang.

## State and Persistence Behavior
The file is immutable test data with no runtime state. Persistent metadata is title, alternates, and HANG type.

## Dependencies and Integration Points
It depends on Linux soft-lockup regexes, syscall alias handling, and alternate-title sorting.

## Risks and Edge Cases
The top RIP is `check_memory_region`, not the intended syscall. Parser frame scoring must follow the stack to `__x64_sys_rmdir` and normalize it.

## Test Signals
Expected output is the rmdir soft-lockup title/alternates, type `HANG`, and no panic flag.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/266 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/267 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/267

## Purpose
This fixture verifies soft-lockup parsing in IPv6 receive processing. The expected title is `BUG: soft lockup in ipv6_rcv`, alt `stall in ipv6_rcv`, and type `HANG`.

## Important APIs, Types, and Functions
The raw log is a watchdog soft lockup with a network receive stack. Parser paths include soft-lockup report matching, hang alt generation, and meaningful frame selection. Important symbols include `tun_get_user`, `_decode_session6`, `__xfrm_decode_session`, `icmpv6_route_lookup`, `icmp6_send`, `ip6_input_finish`, `ip6_input`, `ip6_rcv_finish`, `ipv6_rcv`, `__netif_receive_skb_core`, `napi_gro_frags`, `tun_chr_write_iter`, and `__x64_sys_writev`.

## Control Flow
The reporter sees the watchdog line, register dump, and call trace. The selected title frame should be `ipv6_rcv` in the network stack, not earlier tun/xfrm helper frames or syscall wrappers.

## State and Persistence Behavior
No mutable state exists. The persistent contract is title, alt title, and HANG type over a 55-line log.

## Dependencies and Integration Points
It depends on Linux soft-lockup patterns and stack parser heuristics for network paths.

## Risks and Edge Cases
Network receive traces are deep and include tun, xfrm, ICMPv6, and syscall frames; frame-priority changes can retitle the report.

## Test Signals
The parse must return `BUG: soft lockup in ipv6_rcv`, alt `stall in ipv6_rcv`, and type `HANG`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/267 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/268 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/268

## Purpose
This fixture verifies RCU-preempt self-detected stall parsing in KVM vCPU ioctl execution. The expected title is `INFO: rcu detected stall in kvm_vcpu_ioctl`, alt `stall in kvm_vcpu_ioctl`, and type `HANG`.

## Important APIs, Types, and Functions
Headers include `TITLE`, `ALT`, and `TYPE`. Parser paths include RCU stall matching, grace-period kthread stack handling, IRQ-boundary stack parsing, and hang title generation. Important symbols include `rcu_gp_kthread`, `rcu_dump_cpu_stacks`, `print_cpu_stall`, `kvm_mmu_page_fault`, `handle_ept_violation`, `vmx_handle_exit`, `vcpu_enter_guest`, `kvm_arch_vcpu_ioctl_run`, `kvm_vcpu_ioctl`, `do_vfs_ioctl`, and `__x64_sys_ioctl`.

## Control Flow
The reporter first sees an RCU grace-period kthread stack, then the stalled CPU/task stack in KVM. It must ignore the kthread diagnostic stack for titling and choose the KVM ioctl frame from the actual stalled task.

## State and Persistence Behavior
The file stores a raw RCU stall log and expected HANG metadata. It has no mutable state.

## Dependencies and Integration Points
It depends on Linux RCU stall parsing, stack section selection, and hang crash-type mapping.

## Risks and Edge Cases
The first available stack is not the bug site. If the parser selects `rcu_gp_kthread` or `kvm_mmu_page_fault`, this fixture catches the regression.

## Test Signals
Expected output is title `INFO: rcu detected stall in kvm_vcpu_ioctl`, alt `stall in kvm_vcpu_ioctl`, and type `HANG`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/268 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/269 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/269

## Purpose
This related RCU stall fixture covers KVM instruction emulation and guest-memory reads. It should normalize to `INFO: rcu detected stall in kvm_vcpu_ioctl`, alt `stall in kvm_vcpu_ioctl`, and type `HANG`.

## Important APIs, Types, and Functions
The raw log contains `rcu_preempt detected stalls on CPUs/tasks` and a KVM call trace. Parser paths include RCU stall matching, task-stack extraction, and hang-title normalization. Key symbols include `sched_show_task`, `print_other_cpu_stall`, `rcu_check_callbacks`, `__virt_addr_valid`, `__check_object_size`, `__kvm_read_guest_page`, `kvm_fetch_guest_virt`, `x86_decode_insn`, `x86_emulate_instruction`, `kvm_mmu_page_fault`, `vcpu_enter_guest`, `kvm_arch_vcpu_ioctl_run`, and `kvm_vcpu_ioctl`.

## Control Flow
The reporter reads the RCU stall header and task stack, skips IRQ and RCU helper frames, then follows the KVM stack to the vCPU ioctl interface for the title.

## State and Persistence Behavior
The fixture is immutable raw log data with expected title, alt, and HANG type. It has no runtime state.

## Dependencies and Integration Points
It depends on RCU stall parser rules, KVM stack frame scoring, and generic `ParseTest` comparison.

## Risks and Edge Cases
Several KVM internals are more specific than `kvm_vcpu_ioctl`, but the expected title intentionally groups the hang at the user-facing ioctl boundary.

## Test Signals
The parse must return the KVM vCPU ioctl RCU-stall title and alt with type `HANG`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/269 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/27 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/27

## Purpose
This minimal lockdep fixture verifies corrupted handling for an incomplete circular-locking report. Expected title is `possible deadlock in flush_workqueue`, type `LOCKDEP`, and `CORRUPTED: Y`.

## Important APIs, Types, and Functions
The file uses `TITLE`, `TYPE`, and `CORRUPTED` headers, followed by the beginning of a 2.6.32 lockdep report. The only meaningful target frame is `flush_workqueue+0x0/0xb0`.

## Control Flow
The reporter identifies a possible circular locking dependency and an attempted lock site, but the report is truncated before a full dependency chain and backtrace. It must still infer the lockdep title while marking the result corrupted.

## State and Persistence Behavior
No runtime state exists. Persistent expected state is title, type, corruption flag, and a short raw partial log.

## Dependencies and Integration Points
It depends on lockdep report matching and corruption detection for incomplete reports.

## Risks and Edge Cases
Too-permissive parsing could mark the truncated report as clean, while too-strict parsing could fail to preserve the useful `flush_workqueue` title.

## Test Signals
Expected output is `possible deadlock in flush_workqueue`, type `LOCKDEP`, and `CORRUPTED: Y`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/27 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/270 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/270

## Purpose
This fixture verifies RCU stall parsing for the input subsystem mouse device write path. The expected title is `INFO: rcu detected stall in mousedev_write`, alt `stall in mousedev_write`, and type `HANG`.

## Important APIs, Types, and Functions
The log contains an `rcu_sched self-detected stall on CPU` with NMI backtrace. Parser paths include RCU stall detection, IRQ stack skipping, and hang-title generation. Key symbols include `dump_stack`, `nmi_cpu_backtrace`, `rcu_dump_cpu_stacks`, `print_cpu_stall`, `rcu_check_callbacks`, `_raw_spin_unlock_irq`, `mousedev_write`, `__vfs_write`, `vfs_write`, `ksys_write`, `__x64_sys_write`, and `do_syscall_64`.

## Control Flow
The reporter reads the RCU stall header, passes through timer/IRQ frames, and extracts `mousedev_write` from the task stack as the hang site.

## State and Persistence Behavior
The fixture is immutable and stores expected title, alt, and HANG type. It has no mutable state.

## Dependencies and Integration Points
It depends on Linux RCU stall regexes and function-priority rules for write syscall stacks.

## Risks and Edge Cases
The top RIP is `_raw_spin_unlock_irq`, which is too generic. The parser must prefer `mousedev_write` instead of write syscall wrappers.

## Test Signals
Output should be `INFO: rcu detected stall in mousedev_write`, alt `stall in mousedev_write`, and type `HANG`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/270 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/271 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/271

## Purpose
This fixture covers RCU stall parsing in FUSE device release. The expected title is `INFO: rcu detected stall in fuse_dev_release`, alt `stall in fuse_dev_release`, and type `HANG`.

## Important APIs, Types, and Functions
Headers include `TITLE`, `ALT`, and `TYPE`. Parser paths include RCU stall detection, task stack extraction, and later grace-period kthread diagnostics. Key symbols include `sched_show_task`, `print_other_cpu_stall`, `check_cpu_stall`, `rcu_check_callbacks`, `native_queued_spin_lock_slowpath`, `request_end`, `end_requests`, `fuse_dev_release`, `__fput`, `task_work_run`, `exit_to_usermode_loop`, and `rcu_gp_kthread`.

## Control Flow
The reporter sees a detected-stalls report, follows the stalled task stack through request completion into `fuse_dev_release`, then sees additional RCU kthread starvation output. The title must come from the stalled task, not the diagnostic kthread.

## State and Persistence Behavior
The file persists expected HANG metadata and a 59-line raw log. It owns no runtime state.

## Dependencies and Integration Points
It depends on RCU stall parser support for both task and kthread diagnostic sections, and on hang title generation.

## Risks and Edge Cases
The log has two RCU-related stack sections. Choosing the later `rcu_gp_kthread` stack would hide the FUSE regression.

## Test Signals
Expected parse is the FUSE release RCU-stall title and alt with type `HANG`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/271 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/272 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/272

## Purpose
This fixture verifies RCU stall parsing for a netlink send path involving TIPC compatibility dumps. The expected title is `INFO: rcu detected stall in netlink_sendmsg`, alt `stall in netlink_sendmsg`, and type `HANG`.

## Important APIs, Types, and Functions
The raw log is an `rcu_sched self-detected stall on CPU`. Parser paths include RCU stall matching, NMI/IRQ frame skipping, and network-stack frame selection. Important symbols include `lock_acquire`, `tipc_sk_lookup`, `tipc_nl_publ_dump`, `__tipc_nl_compat_dumpit.isra.11`, `tipc_nl_compat_sk_dump`, `tipc_nl_compat_recv`, `genl_family_rcv_msg`, `netlink_rcv_skb`, `netlink_unicast`, `netlink_sendmsg`, `sock_sendmsg`, and `__x64_sys_sendmsg`.

## Control Flow
The reporter processes timer and RCU frames first, then the network stack. It should title at `netlink_sendmsg`, the user-facing send path, rather than deeper TIPC dump helpers.

## State and Persistence Behavior
No mutable state exists. The fixture stores expected HANG metadata and raw log text.

## Dependencies and Integration Points
It depends on RCU stall patterns, stack parser ordering, and hang title normalization.

## Risks and Edge Cases
Many deeper TIPC functions appear before `netlink_sendmsg`; parser heuristics must still produce the expected stable subsystem boundary.

## Test Signals
The parse must produce `INFO: rcu detected stall in netlink_sendmsg`, alt `stall in netlink_sendmsg`, and type `HANG`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/272 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/273 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/273

## Purpose
This fixture is another KVM RCU stall variant, this time with `__srcu_read_lock` at the stalled RIP. It should still parse to `INFO: rcu detected stall in kvm_vcpu_ioctl`, alt `stall in kvm_vcpu_ioctl`, and type `HANG`.

## Important APIs, Types, and Functions
Parser paths include RCU detected-stalls matching, IRQ helper skipping, KVM stack frame selection, and hang title generation. Key symbols include `sched_show_task`, `print_other_cpu_stall`, `rcu_check_callbacks`, `__srcu_read_lock`, `vcpu_enter_guest`, `kvm_arch_vcpu_ioctl_run`, `kvm_vcpu_ioctl`, `do_vfs_ioctl`, `ksys_ioctl`, `__x64_sys_ioctl`, and `do_syscall_64`.

## Control Flow
The reporter reads the RCU stall header and task stack. Although `__srcu_read_lock` is the immediate RIP, the parser must walk outward to the KVM vCPU ioctl path for the stable title.

## State and Persistence Behavior
The source persists the expected HANG title, alt, and raw log. It has no runtime state.

## Dependencies and Integration Points
It depends on RCU stall parsing and KVM frame-priority rules shared with reports 268 and 269.

## Risks and Edge Cases
The stall is inside SRCU rather than a KVM MMU helper, so naive first-frame selection would regress the title to a generic synchronization primitive.

## Test Signals
Expected output is the KVM vCPU ioctl RCU-stall title and alt with type `HANG`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/273 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/274 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/274

## Purpose
This fixture verifies RCU stall parsing for IPv6 receive handling on a compat writev/tun input path. The expected title is `INFO: rcu detected stall in ipv6_rcv`, alt `stall in ipv6_rcv`, and type `HANG`.

## Important APIs, Types, and Functions
The raw log contains an `rcu_sched self-detected stall on CPU` and a deep IPv6 receive stack. Parser paths include RCU stall matching, NMI/IRQ stack skipping, and network frame selection. Important symbols include `__sanitizer_cov_trace_pc`, `__xfrm_decode_session`, `__xfrm_policy_check`, `ip6_input_finish`, `ip6_input`, `ip6_mc_input`, `ip6_rcv_finish`, `ipv6_rcv`, `__netif_receive_skb_core`, `tun_rx_batched.isra.50`, `tun_get_user`, `tun_chr_write_iter`, `compat_writev`, and `entry_SYSENTER_compat`.

## Control Flow
The reporter processes RCU timer and NMI frames, then extracts the stalled network receive stack. It must title at `ipv6_rcv`, not xfrm policy helpers, tun ingress helpers, or compat syscall wrappers.

## State and Persistence Behavior
The fixture stores expected HANG metadata and raw log data. There is no mutable state or persistence outside the checked-in file.

## Dependencies and Integration Points
It depends on Linux RCU stall regexes, network-stack frame prioritization, and hang alternate-title generation.

## Risks and Edge Cases
The stack includes many plausible network frames and a 32-bit compat syscall tail. Title selection must remain stable across these details.

## Test Signals
The parse must return `INFO: rcu detected stall in ipv6_rcv`, alt `stall in ipv6_rcv`, and type `HANG`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/274 -->
