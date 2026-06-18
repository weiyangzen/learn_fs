<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/180 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/180

## Purpose
This syzkaller Linux report-parser fixture exercises a corrupted mixed crash log where the expected title is `BUG: unable to handle kernel paging request in corrupted`, with alternate title `bad-access in corrupted`, type `MEMORY_SAFETY_BUG`, and both `CORRUPTED` and `PANICKED` set. The log starts with a page-fault signature and then contains a stronger KASAN use-after-free in `rb_first_postorder`, followed by panic-on-warn and a later oops in `dst_release`. Its purpose is to ensure the parser can classify the report as corrupted instead of over-trusting later stack frames.

## Important APIs, Types, And Functions
This is data consumed by syzkaller's `pkg/report` tests rather than executable code. The important fixture API is the header contract: `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, and `PANICKED`, followed by raw console output. Parser paths exercised include Linux oops matching, KASAN report parsing, corrupted-report heuristics, title sanitization, crash-type mapping, and panic detection. Kernel functions visible in the signal include `rb_first_postorder`, `tipc_group_join`, `tipc_setsockopt`, allocation and free stacks through `tipc_group_create` and `tipc_group_delete`, plus the trailing `dst_release`, `ip6_make_skb`, and `udpv6_sendmsg` oops.

## Control Flow
`parseReport` reads the headers up to the blank line and passes the remaining 165-line log to the Linux reporter. The reporter sees an early `BUG: unable to handle kernel paging request`, then a KASAN use-after-free with allocation and free provenance, and later an additional oops after `Kernel panic - not syncing`. The expected behavior is to keep the selected title anchored to the corrupted bad-access class rather than generating a precise TIPC or IPv6 title from a secondary crash.

## State And Persistence
The file has no mutable state; the persistent state is the checked-in expected metadata and raw crash text. The log includes dynamic addresses, PIDs, CPU ids, slab object addresses, and register dumps that should be treated as volatile. The source records panic state and corruption state explicitly so regressions in metadata extraction are visible.

## Dependencies And Integration Points
It integrates through the Linux report testdata loader, `Reporter.Parse`, Linux KASAN matchers, panic detection, and `crash.TitleToType` mapping. It also depends on parser rules that distinguish primary reports from noisy follow-on oopses and on normalization rules for unstable addresses and offsets.

## Risks
The main risk is selecting `KASAN: use-after-free in rb_first_postorder` or `general dst_release` as the title and losing the intended corrupted-page-fault classification. Another risk is panic detection latching to the later fatal exception while ignoring the earlier `panic_on_warn` line. Because the log contains allocation/free sections and two crash contexts, report-boundary logic is also exposed.

## Test Signals
Regression checks should confirm title `BUG: unable to handle kernel paging request in corrupted`, alt `bad-access in corrupted`, type `MEMORY_SAFETY_BUG`, `CORRUPTED: Y`, and `PANICKED: Y`. The parsed report should preserve the KASAN use-after-free and panic evidence without promoting the follow-on `dst_release` oops to the primary crash.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/180 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/181 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/181

## Purpose
This fixture verifies warning parsing for duplicate proc entry registration in the iptables CLUSTERIP target. The expected title is `WARNING: proc registration bug in clusterip_tg_check`, type `WARNING`, with `PANICKED: Y`. The console line `proc_dir_entry 'ipt_CLUSTERIP/172.20.0.170' already registered` gives the semantic reason for the warning.

## Important APIs, Types, And Functions
The fixture API is the syzkaller report header plus raw Linux log. Parser components exercised include warning extraction, source-location stripping from `fs/proc/generic.c:330`, function-title selection from `proc_register` and caller context, and panic-on-warn recognition. Important kernel frames include `proc_register`, `proc_create_data`, `clusterip_tg_check`, `xt_check_target`, `find_check_entry`, `translate_table`, `do_ipt_set_ctl`, `nf_setsockopt`, `ip_setsockopt`, `sctp_setsockopt`, and `SyS_setsockopt`.

## Control Flow
The test loader reads the metadata, then the Linux reporter finds the cut-here warning and call trace. The parser should use the CLUSTERIP caller to produce a subsystem-specific title instead of the generic `proc_register` frame. The syscall path flows from `setsockopt` through SCTP/IP netfilter hooks into iptables table translation and target validation.

## State And Persistence
Persistent state is the expected title, type, panic flag, and the 130-line log. Runtime values such as IP address, PID, stack addresses, and register contents are volatile parser input. There is no local mutation beyond the test harness comparing parsed output to this file.

## Dependencies And Integration Points
The fixture depends on Linux warning regexes, proc-registration special-case title cleanup, netfilter stack parsing, and panic detection. It is integrated by `TestParse` via the `report` testdata directory and helps keep Linux reporter behavior stable for CLUSTERIP setup failures.

## Risks
The parser could collapse the warning to `WARNING in proc_register`, omit the CLUSTERIP context, or miss the panic flag because the panic line appears immediately after the warning. Another risk is treating the human-readable proc_dir_entry line as the title instead of the expected normalized title.

## Test Signals
Useful checks are the title `WARNING: proc registration bug in clusterip_tg_check`, type `WARNING`, and `PANICKED: Y`. The selected report should include both the duplicate proc entry line and the call path through `clusterip_tg_check`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/181 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/182 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/182

## Purpose
This fixture covers a kobject warning raised while enslaving a network device to a bridge. The expected title is `WARNING: kobject bug in br_add_if`, type `WARNING`, with `PANICKED: Y`. The key diagnostic line is `kobject_add_internal failed for brport (error: -12 parent: syz6)`.

## Important APIs, Types, And Functions
The fixture uses syzkaller's report-test header schema and raw kernel trace. Parser logic exercised includes warning matching, kobject-special title extraction, source-location removal from `lib/kobject.c:244`, and panic-on-warn handling. Important frames include `kobject_add_internal`, `kobject_init_and_add`, `br_add_if`, `br_add_slave`, `do_set_master`, `do_setlink`, `rtnl_newlink`, `rtnetlink_rcv_msg`, `netlink_sendmsg`, `sock_write_iter`, and `SyS_writev`.

## Control Flow
The Linux reporter scans from the kobject failure text into the cut-here warning, then follows the stack from rtnetlink writev handling into bridge configuration. The expected title uses the higher-level bridge function `br_add_if`, not only the low-level kobject helper. The panic flag is derived from `Kernel panic - not syncing: panic_on_warn set ...`.

## State And Persistence
The checked-in file persists expected metadata and a 138-line trace. Runtime state represented in the log includes netdevice names, netlink socket state, PIDs, register values, and memory addresses; these are parser input only and should not be treated as stable state.

## Dependencies And Integration Points
It integrates with Linux report parsing, warning-title heuristics, bridge/rtnetlink stack recognition, and panic detection. The test relies on the reporter preserving enough context to classify the warning as a bridge kobject bug.

## Risks
Parser regressions may title this as `WARNING in kobject_add_internal`, miss `br_add_if`, or fail to handle the pre-warning diagnostic line. Because the trace is a network configuration path, many optional helper frames appear and should not perturb the title.

## Test Signals
The stable test signal is title `WARNING: kobject bug in br_add_if`, type `WARNING`, panic true, and report text containing both `kobject_add_internal failed for brport` and the bridge/rtnetlink call chain.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/182 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/183 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/183

## Purpose
This fixture validates list-corruption recognition in TIPC subscription teardown. It expects title `BUG: corrupted list in tipc_nametbl_unsubscribe`, alternate `bad-access in tipc_nametbl_unsubscribe`, and type `MEMORY_SAFETY_BUG`. The log contains `list_del corruption` followed by `kernel BUG at lib/list_debug.c:53!`.

## Important APIs, Types, And Functions
The file is report-test data with `TITLE`, `ALT`, and `TYPE` headers. Parser features under test include list-debug BUG parsing, invalid-op handling, corrupted-list title normalization, and stack-frame selection. Important frames include `__list_del_entry_valid`, `tipc_nametbl_unsubscribe`, `tipc_subscrb_subscrp_delete`, `tipc_subscrb_release_cb`, `tipc_close_conn`, `tipc_topsrv_kern_unsubscr`, `tipc_group_delete`, `tipc_sk_leave`, `tipc_release`, `sock_release`, `__fput`, `do_exit`, and `entry_SYSCALL_64_fastpath`.

## Control Flow
The reporter should identify the list debug message as the crash start, skip generic `__list_del_entry_valid` naming, and select `tipc_nametbl_unsubscribe` from the meaningful call stack. The execution path is user-triggered TIPC socket or group cleanup, descending through subscription deletion and socket release during exit/task-work processing.

## State And Persistence
Persistent expected state is the metadata and 140-line log. Volatile runtime state includes list pointer values, stack addresses, socket state, and PIDs. There is no persistence outside the test fixture; the source file itself is the golden parser input.

## Dependencies And Integration Points
This fixture depends on syzkaller's Linux list-corruption recognizers, bad-access alternate-title generation, TIPC stack parsing, and memory-safety type classification. It is consumed by the common report parser tests for Linux target data.

## Risks
A regression could emit `kernel BUG in __list_del_entry_valid` rather than the TIPC function, or classify the issue as a generic crash instead of `MEMORY_SAFETY_BUG`. Another risk is losing the alternate bad-access title for list corruption.

## Test Signals
Check for exact title, alt title, and type. The selected report should contain `list_del corruption`, `lib/list_debug.c:53`, and the `tipc_nametbl_unsubscribe` frame before generic socket-exit tail frames.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/183 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/184 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/184

## Purpose
This fixture covers packet-socket list corruption during protocol-hook removal. It expects title `BUG: corrupted list in __dev_remove_pack`, alt `bad-access in __dev_remove_pack`, and type `MEMORY_SAFETY_BUG`. The log is shorter than most neighboring files and centers on `kernel BUG at lib/list_debug.c:56!`.

## Important APIs, Types, And Functions
The file uses the same report-test metadata contract. Parser functions exercised are list-debug BUG detection, title selection from a short stack, alternate bad-access title generation, and memory-safety classification. Kernel frames include `__dev_remove_pack`, `__unregister_prot_hook`, `packet_release`, `packet_rcv_spkt`, `sock_close`, `__fput`, `task_work_run`, `do_exit`, `do_group_exit`, `SYSC_exit_group`, and `entry_SYSCALL_64_fastpath`.

## Control Flow
The reporter reads the metadata, then scans the 54-line raw report. The crash path is process exit closing a packet socket; release unregisters a protocol hook and trips list-debug validation in `__dev_remove_pack`. The parser should use the first meaningful frame as the title because there is little secondary context.

## State And Persistence
State is static fixture text. Dynamic addresses and KMSAN-style shadow-origin frames in the log are transient. The persistent expected state is the title, alt, type, and the compact console trace.

## Dependencies And Integration Points
It integrates with Linux list-corruption matchers, packet-socket stack parsing, and syzkaller's report test loader. The fixture broadens coverage beyond TIPC by exercising a networking core packet hook list.

## Risks
Short reports increase the risk that the parser selects `packet_release` or generic list-debug text instead of `__dev_remove_pack`. The source also contains sanitizer helper frames that should not be treated as crash-owner APIs.

## Test Signals
Regression checks should confirm exact title, `MEMORY_SAFETY_BUG`, and alt title. The report should retain `lib/list_debug.c:56` and the `packet_release` to process-exit path.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/184 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/185 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/185

## Purpose
This fixture validates lockdep circular-dependency parsing for IPv4 setsockopt. The expected title is `possible deadlock in do_ip_setsockopt` and type `LOCKDEP`. The log starts with `WARNING: possible circular locking dependency detected`.

## Important APIs, Types, And Functions
The fixture is report parser data; headers drive expected metadata. Parser logic under test includes lockdep title extraction, held-lock/dependency block boundary handling, and choosing the syscall-side top frame. Important functions include `do_ip_setsockopt.isra.12`, `rtnl_lock`, `__mutex_lock`, `mutex_lock_nested`, `unregister_netdevice_notifier`, `clusterip_tg_destroy`, `cleanup_entry`, `__do_replace`, `do_ipt_set_ctl`, `nf_setsockopt`, `ip_setsockopt`, `tcp_setsockopt`, `sock_common_setsockopt`, `SyS_setsockopt`, `xt_find_table_lock`, `xt_request_find_table_lock`, and `get_info`.

## Control Flow
The Linux reporter detects the lockdep warning and parses the dependency chain. The runtime path is a user `setsockopt` call entering IPv4 netfilter table replacement, where CLUSTERIP cleanup interacts with RTNL locking and xtables locks. The title should reflect `do_ip_setsockopt`, not the helper `rtnl_lock`.

## State And Persistence
The file persists a 153-line lockdep report and expected metadata. Lock addresses, lock class names, and task ids are transient data. No state is mutated by the fixture except parser test expectations.

## Dependencies And Integration Points
It depends on Linux lockdep report regexes, stack-frame extraction, and crash-type mapping to `LOCKDEP`. It integrates through the syzkaller Linux report test suite and overlaps with netfilter/CLUSTERIP warning fixtures in this group.

## Risks
Lockdep traces contain multiple stacks; the parser could select the wrong side of the dependency, generating `possible deadlock in rtnl_lock` or `clusterip_tg_destroy`. Report-boundary handling must not discard dependency details needed for title selection.

## Test Signals
Exact title and type are the primary signal. The report should include circular dependency text and both the `do_ip_setsockopt` and CLUSTERIP/netfilter cleanup stack segments.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/185 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/186 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/186

## Purpose
This is the IPv6 counterpart to the previous lockdep fixture. It expects title `possible deadlock in do_ipv6_setsockopt` and type `LOCKDEP`, covering circular locking during IPv6 socket option processing.

## Important APIs, Types, And Functions
The test fixture uses `TITLE` and `TYPE` headers plus a raw Linux lockdep trace. Important parser behavior is lockdep warning detection, IPv6 function naming despite inlined suffixes, and separation of dependency stacks. Important frames include `do_ipv6_setsockopt.isra.8`, `rtnl_lock`, `__mutex_lock`, `mutex_lock_nested`, `unregister_netdevice_notifier`, `clusterip_tg_destroy`, `cleanup_entry`, `__do_replace`, `do_ipt_set_ctl`, `nf_setsockopt`, `ip_setsockopt`, `tcp_setsockopt`, `sock_common_setsockopt`, `SyS_setsockopt`, and xtables lookup functions.

## Control Flow
The parser scans the circular locking warning and builds a lockdep report. The runtime flow begins with IPv6 setsockopt, crosses protocol socket option dispatch, and reaches netfilter table replacement and CLUSTERIP cleanup where RTNL and xtables locks interact. The expected title should prefer `do_ipv6_setsockopt` from the active stack.

## State And Persistence
The persistent content is a 155-line golden lockdep log and expected type. Lock instances, task names, addresses, and generated suffixes such as `.isra.8` are volatile and must be normalized or ignored appropriately.

## Dependencies And Integration Points
It integrates with syzkaller's Linux lockdep parsing and netfilter stack handling. It depends on frame normalization that can keep the semantic function name while tolerating compiler-generated suffixes.

## Risks
This fixture can regress if the parser confuses IPv4 and IPv6 paths or chooses a helper lock function as title. Because it resembles report 185, dedup or title logic must not collapse both cases to the same title.

## Test Signals
Checks should assert `possible deadlock in do_ipv6_setsockopt`, type `LOCKDEP`, and presence of the IPv6 setsockopt frame plus CLUSTERIP cleanup lock chain.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/186 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/187 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/187

## Purpose
This fixture verifies lockdep parsing for an IPv4 getsockopt path. Expected title is `possible deadlock in do_ip_getsockopt`, type `LOCKDEP`. It ensures read-side socket option paths are not folded into the setsockopt titles used by nearby fixtures.

## Important APIs, Types, And Functions
The file is a static lockdep report fixture. Important parser concepts include circular-dependency detection, stack owner selection, and function normalization. Key frames include `do_ip_getsockopt`, `rtnl_lock`, `__mutex_lock`, `mutex_lock_nested`, `unregister_netdevice_notifier`, `clusterip_tg_destroy`, `cleanup_entry`, `__do_replace`, `do_ipt_set_ctl`, `nf_setsockopt`, `ip_setsockopt`, `tcp_setsockopt`, `sock_common_setsockopt`, `SyS_setsockopt`, `xt_find_table_lock`, `xt_request_find_table_lock`, and `get_info`.

## Control Flow
The reporter should detect the first lockdep warning and derive title from the `do_ip_getsockopt` stack. The runtime path includes getsockopt and netfilter table information lookup interacting with a previously described CLUSTERIP teardown lock chain.

## State And Persistence
The fixture persists 145 lines of lockdep text and the expected metadata. Lockdep object addresses and task details are volatile. There is no executable state or side effect in the repository.

## Dependencies And Integration Points
It depends on syzkaller's Linux lockdep parser and title heuristics for socket option accessors. Integration is the common testdata loop over `pkg/report/testdata/linux/report`.

## Risks
The parser may choose `rtnl_lock` or an xtables helper instead of `do_ip_getsockopt`, or it may conflate this getsockopt regression with setsockopt fixtures. Missing dependency-chain boundaries can also change report text.

## Test Signals
The title must remain `possible deadlock in do_ip_getsockopt` with `LOCKDEP` type. The report should preserve both the getsockopt stack and the lock chain through netfilter/CLUSTERIP cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/187 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/188 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/188

## Purpose
This fixture checks lockdep parsing when the selected title is the lock acquisition function itself: `possible deadlock in rtnl_lock`, type `LOCKDEP`. The trace covers circular locking between rtnetlink and IPv6/xtables socket option paths.

## Important APIs, Types, And Functions
The static fixture exposes syzkaller's lockdep parser to a 181-line dependency report. Important frames include `rtnl_lock`, `xt_find_table_lock`, `__mutex_lock`, `mutex_lock_nested`, `xt_find_revision`, `do_ip6t_get_ctl`, `nf_getsockopt`, `ipv6_getsockopt`, `tcp_getsockopt`, `sock_common_getsockopt`, `SyS_getsockopt`, `lock_sock_nested`, `do_ipv6_setsockopt.isra.8`, `ipv6_setsockopt`, `rawv6_setsockopt`, `sock_common_setsockopt`, and `SyS_setsockopt`.

## Control Flow
The Linux reporter enters at the circular-lock warning and parses multiple stack sections. Unlike the preceding socket-option fixtures, the expected owner is `rtnl_lock`, indicating that the active dependency evidence points at RTNL lock acquisition itself. The parser must not force every netfilter lockdep report to a syscall wrapper title.

## State And Persistence
Persistent state is the expected title and type plus raw lockdep text. Dynamic kernel addresses, lock class ids, task ids, and CPU ids are volatile. The fixture has no runtime mutation.

## Dependencies And Integration Points
It integrates with Linux lockdep matching and netfilter/IPv6 title heuristics. It depends on syzkaller preserving dependency graph text sufficiently for stable parsing of the selected culprit.

## Risks
Risk lies in over-normalizing the title to `do_ip6t_get_ctl` or `do_ipv6_setsockopt`, which would lose the intended RTNL focus. Another risk is truncating one of the two stack sections and changing selection.

## Test Signals
Expected signal is exact title `possible deadlock in rtnl_lock` and type `LOCKDEP`. The output should include xtables getsockopt frames and raw IPv6 setsockopt frames, showing the conflicting acquisition paths.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/188 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/189 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/189

## Purpose
This fixture validates lockdep parsing for console virtual terminal reads interacting with pipe splice writes. The expected title is `possible deadlock in vcs_read`, type `LOCKDEP`.

## Important APIs, Types, And Functions
The fixture is static report data for Linux lockdep parser coverage. Important frames include `vcs_read`, `pipe_lock`, `lock_acquire`, `__mutex_lock`, `mutex_lock_nested`, `iter_file_splice_write`, `SyS_splice`, `entry_SYSCALL_64_fastpath`, plus dependency-side frames such as `dput`, `done_path_create`, `handle_create`, `devtmpfsd`, `wait_for_completion`, `devtmpfs_create_node`, `device_add`, `device_create_groups_vargs`, and `device_create`.

## Control Flow
The parser finds a circular locking warning and derives the title from the active `vcs_read` stack. The runtime path is splice-based file movement involving a VCS read path and pipe locking, contrasted against devtmpfs device creation acquiring related locks.

## State And Persistence
The file persists a 168-line lockdep trace. Volatile data includes lock class addresses, task ids, path state, and stack addresses. The fixture does not maintain runtime state; it is a golden parser input.

## Dependencies And Integration Points
It depends on lockdep regexes, splice/VFS stack handling, and the syzkaller test harness that compares parser output to headers. It broadens lockdep coverage beyond networking.

## Risks
The parser could choose the common `pipe_lock` or devtmpfs side instead of `vcs_read`. Lockdep sections with several filesystem stacks make report-boundary handling important.

## Test Signals
Checks should confirm `possible deadlock in vcs_read`, `LOCKDEP`, and report text containing the `vcs_read` to `SyS_splice` stack plus the devtmpfs creation dependency side.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/189 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/19 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/19

## Purpose
This minimal fixture tests recognition of a KASAN wild-memory-access read without a full stack trace. It expects title `KASAN: wild-memory-access Read`, type `KASAN-READ`, and `CORRUPTED: Y`.

## Important APIs, Types, And Functions
The only fixture API elements are the metadata headers and a short raw KASAN line: `BUG: KASAN: wild-memory-access on address ...`. Parser behavior under test includes sanitizer signature detection, read/write type classification, and corrupted-report handling when no reliable function frame exists.

## Control Flow
`parseReport` reads the three headers and the seven-line log. The Linux reporter must identify the KASAN wild-memory-access text directly and produce a generic read title because there is no stack function to name.

## State And Persistence
Persistent state is extremely compact: title, type, corruption flag, and an address-bearing sanitizer line. The address is dynamic and not semantically stable.

## Dependencies And Integration Points
It integrates with Linux KASAN parser rules and type mapping to `KASAN-READ`. It is useful for boundary testing parser behavior on underspecified reports.

## Risks
The parser could fail to report a crash due to missing stack frames, or it could attempt to embed the volatile address into the title. It could also misclassify the event as generic `MEMORY_SAFETY_BUG` rather than `KASAN-READ`.

## Test Signals
The stable signal is exact title `KASAN: wild-memory-access Read`, type `KASAN-READ`, and corruption true despite the absence of call trace data.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/19 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/190 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/190

## Purpose
This fixture is the write-side VCS counterpart to report 189. Expected title is `possible deadlock in vcs_write`, type `LOCKDEP`, covering circular locking in console virtual terminal writes plus pipe splice.

## Important APIs, Types, And Functions
The static report exercises lockdep parsing with key frames `vcs_write`, `pipe_lock`, `lock_acquire`, `__mutex_lock`, `mutex_lock_nested`, `iter_file_splice_write`, `SyS_splice`, `put_ucounts`, `wait_for_completion`, `devtmpfs_create_node`, `device_add`, `device_create_groups_vargs`, `device_create`, `vcs_make_sysfs`, `vc_allocate`, `con_install`, and `tty_init_dev`.

## Control Flow
The Linux reporter parses the circular-locking warning and should use the active write path `vcs_write` for the title. The runtime trace indicates splice/write interaction with VCS and a dependency chain through console/TTY setup and device creation.

## State And Persistence
The 163-line log and expected metadata are persistent fixture state. Runtime lock addresses, task ids, console numbers, and stack addresses are volatile.

## Dependencies And Integration Points
It integrates with the lockdep parser and with VFS/TTY stack title heuristics. It complements report 189 to ensure read and write VCS paths remain distinct.

## Risks
Title selection can drift to `pipe_lock`, `vcs_make_sysfs`, or the devtmpfs side. Another risk is deduplicating the write case with the read case and losing coverage.

## Test Signals
Assert exact title `possible deadlock in vcs_write` and type `LOCKDEP`. The report should include both the `vcs_write` stack and dependency frames around console/TTY device creation.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/190 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/191 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/191

## Purpose
This fixture validates lockdep extraction for perf event context locking during splice activity. Expected title is `possible deadlock in perf_event_ctx_lock_nested`, type `LOCKDEP`.

## Important APIs, Types, And Functions
The report-test file uses `TITLE` and `TYPE` headers with a 248-line lockdep trace. Important frames include `perf_event_ctx_lock_nested`, `pipe_lock`, `lock_acquire`, `__mutex_lock`, `mutex_lock_nested`, `iter_file_splice_write`, `SyS_splice`, `try_to_wake_up`, `default_wake_function`, `__wake_up_common`, `complete`, `wait_for_completion`, `devtmpfs_create_node`, `device_add`, `device_create_groups_vargs`, and `device_create`.

## Control Flow
The parser detects the circular locking dependency and must choose the perf context lock helper as the title. The runtime flow shows splice/pipe locking interacting with wakeups and device creation, with perf event context locking participating in the cycle.

## State And Persistence
Persistent state is the lockdep log and expected metadata. Lock graph entries, pointer values, task names, and CPU ids are volatile. There is no code path in this repository besides the parser test harness consuming the data.

## Dependencies And Integration Points
It depends on Linux lockdep report parsing and perf stack naming. It integrates through syzkaller's report fixtures and helps ensure perf lock helpers are retained as meaningful titles rather than filtered as generic lock internals.

## Risks
The parser may over-filter `perf_event_ctx_lock_nested` as a helper and choose `pipe_lock` or splice instead. Long lockdep reports also risk truncation that can change the selected frame.

## Test Signals
Stable checks are title `possible deadlock in perf_event_ctx_lock_nested`, type `LOCKDEP`, and preservation of perf, pipe, splice, and wakeup/device dependency stacks.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/191 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/192 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/192

## Purpose
This fixture verifies a longer perf lockdep report where the expected title is `possible deadlock in perf_event_init_task`, type `LOCKDEP`. It covers fork/task initialization interactions with perf trace initialization and splice/read paths.

## Important APIs, Types, And Functions
The static fixture exercises lockdep parsing across 312 lines. Important frames include `perf_trace_init`, `perf_event_init_task`, `perf_event_ctx_lock_nested`, `perf_read`, `do_iter_read`, `vfs_readv`, `default_file_splice_read`, `do_splice_to`, `SyS_splice`, `do_fast_syscall_32`, `entry_SYSENTER_compat`, `pipe_lock`, `iter_file_splice_write`, `fs_reclaim_acquire`, and `kmem_cache_alloc`.

## Control Flow
The Linux reporter parses the warning and dependency graph, then selects `perf_event_init_task` as the meaningful owner rather than the first visible frame `perf_trace_init`. The runtime evidence crosses compat syscalls, readv/splice handling, perf read locking, and task initialization.

## State And Persistence
The file persists the expected title and type plus a long lockdep report. Volatile state includes lock names with class ids, allocation contexts, task ids, and syscall ABI details. The fixture itself is immutable test input.

## Dependencies And Integration Points
It integrates with lockdep parsing, compat syscall frame normalization, perf event title heuristics, and report-boundary logic for long dependency reports.

## Risks
Because `perf_trace_init` appears above `perf_event_init_task`, simple first-frame selection would produce the wrong title. Long reports also risk losing dependency context or selecting `fs_reclaim_acquire` from a nested section.

## Test Signals
Assert exact title `possible deadlock in perf_event_init_task` and `LOCKDEP`. The report should retain the perf initialization frames and the splice/read path that exposes the lock cycle.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/192 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/193 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/193

## Purpose
This fixture covers a perf lockdep warning during CPU hotplug initialization. Expected title is `possible deadlock in perf_event_for_each_child`, type `LOCKDEP`.

## Important APIs, Types, And Functions
The report data exercises lockdep parsing with boot/hotplug stacks. Key frames include `perf_event_for_each_child`, `perf_event_ctx_lock_nested`, `__mutex_lock`, `mutex_lock_nested`, `perf_event_init_cpu`, `perf_event_init`, `start_kernel`, `x86_64_start_reservations`, `x86_64_start_kernel`, `secondary_startup_64`, `cpuhp_invoke_callback`, `_cpu_up`, `do_cpu_up`, `cpu_up`, `smp_init`, `kernel_init_freeable`, `kernel_init`, and `ret_from_fork`.

## Control Flow
The parser identifies a circular-locking warning and selects `perf_event_for_each_child` from the perf-side stack. Runtime flow is kernel initialization and CPU hotplug callbacks invoking perf event setup, contrasting with another lock acquisition path in the dependency report.

## State And Persistence
Persistent state is a 193-line lockdep report and expected metadata. CPU ids, lock class addresses, and boot sequence details are dynamic parser input. The file has no mutable state.

## Dependencies And Integration Points
It depends on lockdep parsing, perf stack frame retention, and syzkaller testdata comparison. It expands coverage to warnings during kernel initialization rather than only user syscalls.

## Risks
Boot/hotplug frames can cause title selection to drift to `perf_event_init_cpu` or `start_kernel`; the fixture asserts the child-iteration frame is the stable culprit. Parser filters that drop initialization frames too aggressively can also lose context.

## Test Signals
Expected signal is title `possible deadlock in perf_event_for_each_child` and type `LOCKDEP`. The selected report should include perf event child iteration and CPU initialization/hotplug frames.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/193 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/194 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/194

## Purpose
This fixture validates lockdep title selection for perf event release. Expected title is `possible deadlock in perf_event_release_kernel`, type `LOCKDEP`.

## Important APIs, Types, And Functions
The static report uses lockdep warning text with important frames `perf_trace_destroy`, `perf_event_release_kernel`, `perf_event_for_each_child`, `perf_ioctl`, `do_vfs_ioctl`, `SyS_ioctl`, `entry_SYSCALL_64_fastpath`, `perf_event_init_cpu`, `perf_event_init`, `start_kernel`, `x86_64_start_reservations`, `x86_64_start_kernel`, `secondary_startup_64`, `cpuhp_invoke_callback`, `_cpu_up`, and `do_cpu_up`.

## Control Flow
The Linux reporter parses the circular dependency and should select the semantic release function rather than `perf_trace_destroy` or ioctl wrappers. Runtime flow is user ioctl-driven perf event teardown interacting with perf initialization/hotplug dependency paths.

## State And Persistence
The fixture persists 257 lines of lockdep report and expected metadata. Task ids, lock addresses, and CPU hotplug details are volatile.

## Dependencies And Integration Points
It integrates with syzkaller's Linux lockdep parser and perf-event title heuristics. It complements reports 191-193 by covering release/teardown rather than read/init.

## Risks
The parser could select `perf_trace_destroy`, `perf_ioctl`, or `perf_event_for_each_child` instead of `perf_event_release_kernel`. Another risk is losing syscall context if report truncation happens too early.

## Test Signals
Check exact title and `LOCKDEP` type. The report should preserve the perf release stack, ioctl syscall path, and perf initialization dependency side.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/194 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/195 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/195

## Purpose
This fixture tests KASAN wild-memory-access read parsing in the SCSI generic read path. Expected title is `KASAN: wild-memory-access Read in sg_read`, alt `bad-access in sg_read`, type `KASAN-READ`.

## Important APIs, Types, And Functions
The fixture provides KASAN report data with headers and a 42-line stack. Parser features under test include KASAN read/write classification, function-title extraction, alternate bad-access title generation, and report boundary handling for short sanitizer traces. Important frames include `dump_stack`, `kasan_report`, `check_memory_region`, `kasan_check_read`, `sg_read`, `do_loop_readv_writev.part.17`, `do_readv_writev`, `vfs_readv`, `do_readv`, `SyS_readv`, and `entry_SYSCALL_64_fastpath`.

## Control Flow
The reporter finds `BUG: KASAN: wild-memory-access in sg_read` and selects `sg_read` as the function title. The runtime path is a user `readv` syscall through VFS into the SCSI generic driver.

## State And Persistence
Static state is the expected metadata and short raw KASAN report. The bad address, register state, and syscall arguments are volatile. No repository state changes occur.

## Dependencies And Integration Points
It depends on Linux KASAN regexes, SCSI generic stack frame extraction, and syzkaller's crash type mapping. It integrates as a standard report test fixture.

## Risks
The parser may return a generic wild-memory title without `sg_read`, or classify the report as `MEMORY_SAFETY_BUG` instead of `KASAN-READ`. Sanitizer helper frames must be skipped for title selection.

## Test Signals
Exact title, alt, and `KASAN-READ` type are required. The selected report should include the `sg_read` frame and readv syscall tail.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/195 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/196 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/196

## Purpose
This fixture extends report 195 with additional fault text after the initial KASAN SCSI generic read report. Expected title remains `KASAN: wild-memory-access Read in sg_read`, alt `bad-access in sg_read`, and type `KASAN-READ`.

## Important APIs, Types, And Functions
The file contains KASAN metadata and an 80-line mixed log. Important parser behaviors are first-report selection, handling of later `general protection fault`, and preservation of KASAN read classification. Important frames include `dump_stack`, `kasan_report`, `check_memory_region`, `kasan_check_read`, `__lock_acquire`, `_raw_write_lock_irqsave`, `sg_remove_request`, `sg_finish_rem_req`, `sg_read`, `do_readv_writev`, `vfs_readv`, `do_readv`, `SyS_readv`, and `entry_SYSCALL_64_fastpath`.

## Control Flow
The Linux reporter should detect the initial KASAN wild-memory access in `sg_read` and not let the later GPF/lock stack replace the primary title. Runtime flow remains readv into the SCSI generic driver, with request removal and lock acquisition appearing in the follow-on context.

## State And Persistence
The expected parser state is static in the headers. Dynamic addresses, lockdep data, and register dumps in the combined log are volatile. The source file is immutable test input.

## Dependencies And Integration Points
It depends on KASAN parsing, mixed-report boundary selection, and syzkaller title preference rules. It integrates with the Linux report test suite as a regression case for noisy logs.

## Risks
The primary risk is choosing the later `general protection fault` or `__lock_acquire` as the crash instead of the first KASAN report. Another risk is duplicate handling causing this fixture to diverge from report 195's expected title.

## Test Signals
Checks should assert the same title/alt/type as report 195 and verify that the parser's selected report is anchored to `BUG: KASAN: wild-memory-access in sg_read`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/196 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/197 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/197

## Purpose
This fixture validates KASAN global-out-of-bounds parsing in `/proc` timer display logic. It expects title `KASAN: global-out-of-bounds Read in show_timer`, alt `bad-access in show_timer`, type `KASAN-READ`, and `PANICKED: Y`.

## Important APIs, Types, And Functions
The fixture data includes a KASAN report and a later fatal interrupt panic. Parser behavior includes global-out-of-bounds recognition, read classification, panic detection, and mixed network noise tolerance. Important frames include `show_timer`, `seq_read`, `do_loop_readv_writev`, `do_readv_writev`, `vfs_readv`, `SyS_preadv`, plus unrelated UDP frames such as `udp_queue_rcv_skb`, `udp_sendmsg`, `inet_sendmsg`, `sock_sendmsg`, and `SyS_sendto`.

## Control Flow
The parser should select the KASAN report in `show_timer` as the primary crash. The runtime path for the primary bug is reading a seq_file timer representation, while the log also includes interrupt/network activity and a panic line. The expected panic flag comes from `Kernel panic - not syncing: Fatal exception in interrupt`.

## State And Persistence
Static state is the expected metadata and 109-line console log. Volatile state includes timer/global symbol addresses, UDP packet context, and register dumps.

## Dependencies And Integration Points
It integrates with KASAN out-of-bounds parsers, panic detection, and report-boundary logic that ignores unrelated network call traces. The fixture is consumed by syzkaller's Linux report parser tests.

## Risks
Mixed interrupt/network stack text can cause wrong title selection, such as `udp_queue_rcv_skb`. Parser logic must also preserve the KASAN-specific `KASAN-READ` type rather than broad memory-safety classification.

## Test Signals
Assert title `KASAN: global-out-of-bounds Read in show_timer`, alt `bad-access in show_timer`, type `KASAN-READ`, and panic true. The report should include `show_timer` and seq_file read frames.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/197 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/198 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/198

## Purpose
This long fixture validates a general protection fault in IPv6 iptables table traversal or setup. Expected title is `general protection fault in ip6t_do_table`, alt `bad-access in ip6t_do_table`, type `DoS`, and `PANICKED: Y`.

## Important APIs, Types, And Functions
The raw 438-line log includes allocation failure, KASAN-enabled GPF text, netfilter allocation/setup frames, and fatal panic. Parser behavior under test includes GPF recognition, title selection from netfilter context, panic detection, and not being distracted by allocation diagnostics. Important frames include `warn_alloc`, `__vmalloc_node_range`, `kvmalloc_node`, `xt_alloc_table_info`, `xt_alloc_entry_offsets`, `translate_table`, `do_ip6t_set_ctl`, `nf_setsockopt`, `ipv6_setsockopt`, and the expected `ip6t_do_table` title signal.

## Control Flow
The Linux reporter scans through allocation warnings into a general protection fault and later panic. The runtime path involves IPv6 netfilter table setup and packet/table logic; the parser is expected to select `ip6t_do_table` as the meaningful crash site despite earlier allocation stack frames and voluminous memory diagnostics.

## State And Persistence
The fixture persists the expected metadata and a large raw console report. Dynamic state includes memory pressure counters, addresses, register dumps, PIDs, and netfilter table data. There is no code state beyond golden test input.

## Dependencies And Integration Points
It depends on Linux GPF matchers, netfilter title heuristics, panic detection, and report-boundary trimming for large logs. It integrates with the report parser's DoS classification path rather than KASAN-specific crash types.

## Risks
The parser could title the report from allocation helper frames such as `xt_alloc_entry_offsets` or from `translate_table`, missing the expected `ip6t_do_table`. Long memory diagnostics can also shift boundaries or hide the fatal panic line.

## Test Signals
Stable checks are exact title, alt, type `DoS`, and panic true. The selected report should retain GPF text and enough netfilter stack context to justify `ip6t_do_table`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/198 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/199 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/199

## Purpose
This fixture validates KASAN stack-out-of-bounds read parsing in iterator advancement while handling TUN input. Expected title is `KASAN: stack-out-of-bounds Read in iov_iter_advance`, alt `bad-access in iov_iter_advance`, and type `KASAN-READ`.

## Important APIs, Types, And Functions
The 165-line log includes allocation failure noise, netfilter setup frames, and the KASAN stack-out-of-bounds report. Important frames include `iov_iter_advance`, `tun_get_user`, `tun_chr_write_iter`, `dump_stack`, `warn_alloc_failed`, `__vmalloc_node_range`, `vmalloc`, `xt_alloc_entry_offsets`, `translate_table`, `do_arpt_set_ctl`, `nf_setsockopt`, `ip_setsockopt`, `tcp_setsockopt`, `sock_common_setsockopt`, and `SyS_setsockopt`.

## Control Flow
The reporter should find the KASAN stack-out-of-bounds line and title the report from `iov_iter_advance`, not from preceding allocation/netfilter noise. Runtime flow for the primary bug is write into a TUN character device, which advances an iov iterator and triggers the sanitizer read.

## State And Persistence
Persistent state is title, alt, type, and raw log. Dynamic stack addresses, allocation failures, TUN packet data, and syscall arguments are volatile. The fixture is static.

## Dependencies And Integration Points
It depends on KASAN stack-out-of-bounds parsing, noisy-prefix filtering, and TUN/VFS stack extraction. It integrates as a Linux report parser test case for sanitizer reports embedded in unrelated console activity.

## Risks
Potential regressions include selecting `tun_get_user` instead of `iov_iter_advance`, choosing allocation failure as the report, or losing the `KASAN-READ` type.

## Test Signals
Assert title `KASAN: stack-out-of-bounds Read in iov_iter_advance`, alt `bad-access in iov_iter_advance`, and type `KASAN-READ`. The selected text should include the TUN write path.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/199 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/2 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/2

## Purpose
This minimal fixture contains only `INFO: lockdep is turned off.` and no expected title header. Its purpose is negative coverage: the Linux reporter should not manufacture a crash report from a benign informational line.

## Important APIs, Types, And Functions
The fixture has no `TITLE` or `TYPE` metadata and no call trace. The relevant parser behavior is ignoring lockdep status noise when scanning kernel logs.

## Control Flow
The test harness reads a two-line file and passes the raw text to the reporter. The expected outcome is no crash title/report extraction, or whatever the surrounding test semantics define for headerless non-crash input.

## State And Persistence
The only persistent state is the checked-in informational line. There are no dynamic addresses, stacks, or flags.

## Dependencies And Integration Points
It integrates with `forEachFile("report", ...)` negative test coverage and Linux ignore-pattern logic for non-oops messages.

## Risks
Over-broad lockdep matching could treat this informational line as a lockdep bug. Headerless fixture handling must also avoid false expectations.

## Test Signals
The stable signal is absence of a parsed crash from `INFO: lockdep is turned off.`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/2 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/20 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/20

## Purpose
This compact fixture tests corrupted NULL pointer dereference parsing. It expects title `BUG: unable to handle kernel NULL pointer dereference in corrupted`, alt `bad-access in corrupted`, type `NULL-POINTER-DEREFERENCE`, and `CORRUPTED: Y`.

## Important APIs, Types, And Functions
The file contains metadata plus an eight-line log with `BUG: unable to handle kernel NULL pointer dereference at 000000000000058c` and an `__lock_acquire` frame. Parser behavior under test includes NULL dereference recognition, corrupted-title selection, and not overfitting to a lone lockdep frame.

## Control Flow
The reporter sees the page fault/null-deref signature but lacks a reliable non-corrupted stack. It should therefore produce the corrupted title and bad-access alternate rather than `__lock_acquire`.

## State And Persistence
The persistent state is the expected metadata and a short crash line. The fault address is dynamic except for the null-range signal. No mutable state exists.

## Dependencies And Integration Points
It depends on Linux page-fault and null-deref matchers, corrupted-report heuristics, and crash type mapping to `NULL-POINTER-DEREFERENCE`.

## Risks
The parser could emit `BUG: unable to handle kernel NULL pointer dereference in __lock_acquire` or a generic bad-access title. Very short input also tests behavior with incomplete reports.

## Test Signals
Exact title, alt, type, and `CORRUPTED: Y` should remain stable. The fixture should not produce a lockdep title.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/20 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/200 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/200

## Purpose
This fixture validates general protection fault parsing in socket buffer allocation under fault injection. Expected title is `general protection fault in __alloc_skb`, alt `bad-access in __alloc_skb`, type `DoS`, with `CORRUPTED: Y` and `PANICKED: Y`.

## Important APIs, Types, And Functions
The 220-line log includes `FAULT_INJECTION: forcing a failure`, KASAN-enabled GPF text, and panic. Parser features under test include fault-injection noise handling, GPF title extraction, corruption flag, and panic detection. Important frames include `should_fail`, `should_failslab`, `kmem_cache_alloc_node_trace`, `__kmalloc_node_track_caller`, `__kmalloc_reserve.isra.39`, `__alloc_skb`, `skb_copy_and_csum_dev`, plus generic stack dump helpers.

## Control Flow
The Linux reporter should skip the fault-injection prologue as noise, then parse the general protection fault and select `__alloc_skb` from the allocation stack. Runtime flow is network packet buffer allocation/copy under simulated slab allocation failure, followed by fatal exception panic.

## State And Persistence
Static expected state is the title, alt, type, corruption flag, panic flag, and raw log. Dynamic state includes fault-injection counters, allocation flags, memory addresses, and register values.

## Dependencies And Integration Points
It depends on Linux GPF patterns, KASAN-enabled register dump handling, fault injection message filtering, and `DoS` crash-type mapping. It integrates as a report parser regression for corrupted fatal allocation failures.

## Risks
The parser may title from `should_fail` or `kmem_cache_alloc_node_trace`, or classify the report as a sanitizer memory-safety bug despite the expected `DoS` type. Panic and corruption flags must both be preserved.

## Test Signals
Check exact title `general protection fault in __alloc_skb`, alt, type `DoS`, `CORRUPTED: Y`, and `PANICKED: Y`. The selected report should include fault injection context and the `__alloc_skb` frame.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/200 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/201 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/201

## Purpose
This fixture covers a corrupted general protection fault in IPsec/pfkey processing. Expected title is `general protection fault in corrupted`, alt `bad-access in corrupted`, type `DoS`, with both `CORRUPTED` and `PANICKED` set.

## Important APIs, Types, And Functions
The log contains KASAN-enabled GPF text plus `BUG: using __this_cpu_read() in preemptible ...` and a panic. Important frames include `check_preemption_disabled`, `__this_cpu_preempt_check`, `ipcomp_init_state`, `ipcomp6_init_state`, `__xfrm_init_state`, `xfrm_init_state`, `pfkey_add`, `pfkey_process`, `pfkey_sendmsg`, `sock_sendmsg`, `___sys_sendmsg`, `__sys_sendmsg`, `compat_SyS_sendmsg`, and `entry_SYSENTER_compat`, with later SCSI cleanup frames such as `sg_remove_scat.isra.19`.

## Control Flow
The reporter should identify the GPF as corrupted rather than assigning a precise IPsec title. The runtime path is compat sendmsg into PF_KEY state creation and XFRM/IPComp initialization, followed by fatal exception panic and unrelated cleanup noise.

## State And Persistence
Persistent state is the expected corrupted title, type, panic/corruption flags, and 118-line log. Dynamic state includes preemption state, task IDs, register values, and protocol state addresses.

## Dependencies And Integration Points
It depends on Linux GPF parsing, corrupted-log heuristics, preemption warning handling, compat syscall frame parsing, and panic detection. It integrates with report tests as a noisy corrupted DoS case.

## Risks
The parser could choose `ipcomp_init_state`, `pfkey_add`, or `__this_cpu_preempt_check` as the title, losing the expected corrupted classification. It could also misclassify the preemption warning as the primary bug.

## Test Signals
Stable checks are title `general protection fault in corrupted`, alt `bad-access in corrupted`, type `DoS`, `CORRUPTED: Y`, and `PANICKED: Y`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/201 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/202 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/202

## Purpose
This fixture validates suspicious RCU usage parsing for RDS TCP connection allocation. Expected title is `WARNING: suspicious RCU usage in rds_tcp_conn_alloc`, type `LOCKDEP`. It also includes a sleeping-function warning in invalid context.

## Important APIs, Types, And Functions
The report exercises lockdep/RCU warning parsing. Important frames include `__rds_conn_create`, `lockdep_rcu_suspicious`, `___might_sleep`, `__might_sleep`, `kmem_cache_alloc`, `init_timer_key`, `rds_tcp_conn_alloc`, `rds_tcp_conn_free`, `rds_cmsg_atomic`, `rds_conn_drop`, and syscall/context frames. The parser should recognize `WARNING: suspicious RCU usage` and the later `BUG: sleeping function called from invalid context at mm/slab.h:420`.

## Control Flow
The Linux reporter starts at the suspicious RCU usage warning, parses the held `rcu_read_lock` context, and uses the RDS TCP allocator as title context. Runtime flow is RDS connection creation calling an allocator that may sleep while inside an RCU read-side critical section.

## State And Persistence
The persistent fixture state is title, type, and 177 lines of raw log. Dynamic state includes lockdep context, task ids, RCU scheduler counters, and addresses.

## Dependencies And Integration Points
It depends on Linux RCU/lockdep suspicious usage regexes, invalid-context warning handling, and RDS stack frame title selection. It integrates as a parser case where `TYPE` is `LOCKDEP` rather than `WARNING`.

## Risks
The parser may select the generic `suspicious RCU usage` title without `rds_tcp_conn_alloc`, or switch to the later sleeping-function BUG as primary. It must also preserve the `LOCKDEP` type.

## Test Signals
Assert title `WARNING: suspicious RCU usage in rds_tcp_conn_alloc`, type `LOCKDEP`, and report text showing RCU read lock context plus RDS TCP allocation.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/202 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/203 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/203

## Purpose
This fixture is the RDS loopback counterpart to report 202. Expected title is `WARNING: suspicious RCU usage in rds_loop_conn_alloc`, type `LOCKDEP`, with a sleeping-function invalid-context line later in the report.

## Important APIs, Types, And Functions
The static log exercises suspicious RCU usage matching and title extraction. Important frames include `__rds_conn_create`, `lockdep_rcu_suspicious`, `___might_sleep`, `__might_sleep`, `kmem_cache_alloc_trace`, `rds_loop_conn_alloc`, `rds_loop_conn_free`, `__init_waitqueue_head`, `rcutorture_record_progress`, `__lockdep_init_map`, `rds_conn_drop`, and `__raw_spin_lock_init`.

## Control Flow
The parser should detect the RCU warning, parse the held `rcu_read_lock` context, and select `rds_loop_conn_alloc` as the allocator that sleeps in the invalid context. Runtime flow is RDS loop connection creation inside RCU read-side protection.

## State And Persistence
Persistent state is the expected metadata and 177-line log. Dynamic values include lockdep state, CPU/task identifiers, and memory addresses.

## Dependencies And Integration Points
It integrates with Linux RCU/lockdep warning parsing, RDS stack title heuristics, and report test comparison. It complements report 202 by ensuring TCP and loopback allocators remain distinguishable.

## Risks
Parser title selection could collapse to `__rds_conn_create` or the later `BUG: sleeping function called from invalid context`, losing the allocator-specific title. Type could also regress from `LOCKDEP` to `WARNING`.

## Test Signals
Expected title `WARNING: suspicious RCU usage in rds_loop_conn_alloc` and type `LOCKDEP`. The report should include RCU read-lock context and the `rds_loop_conn_alloc` stack.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/203 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/204 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/204

## Purpose
This short fixture validates warning parsing for an oversized or invalid kmalloc request in KVM VM ioctl handling. Expected title is `WARNING: kmalloc bug in kvm_vm_ioctl`, type `WARNING`.

## Important APIs, Types, And Functions
The 38-line report includes `WARNING: CPU ... at mm/slab_common.c:903 kmalloc_slab` and stack frames `warn_alloc`, `__vmalloc_node_range_memcg`, `vmalloc`, `kvm_vm_ioctl`, `do_vfs_ioctl`, `SyS_ioctl`, and `entry_SYSCALL_64_fastpath`. Parser behavior includes kmalloc warning recognition and caller-title selection.

## Control Flow
The Linux reporter should scan the warning and use `kvm_vm_ioctl` as the subsystem caller, not the generic slab helper. Runtime flow is a user ioctl on a KVM VM file causing memory allocation logic to warn.

## State And Persistence
The fixture persists expected title/type and a compact warning trace. Dynamic state includes PID, allocation size/mode details, addresses, and ioctl arguments if present.

## Dependencies And Integration Points
It depends on Linux warning parser rules, slab/kmalloc message handling, and KVM ioctl stack title heuristics. It integrates with standard syzkaller report tests.

## Risks
The parser could emit `WARNING in kmalloc_slab`, `WARNING in vmalloc`, or fail because the trace is short. It should retain KVM context for deduplication value.

## Test Signals
Assert title `WARNING: kmalloc bug in kvm_vm_ioctl` and type `WARNING`; report text should contain the slab warning and KVM ioctl frame.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/204 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/205 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/205

## Purpose
This fixture is another CLUSTERIP proc registration warning, but with substantial unrelated TUN/VFS lock noise before and around the warning. Expected title is `WARNING: proc registration bug in clusterip_tg_check`, type `WARNING`, and `PANICKED: Y`.

## Important APIs, Types, And Functions
The parser must recognize the same proc warning as report 181 despite interleaved frames. Important visible functions include `proc_register`, `proc_create_data`, `clusterip_tg_check`, netfilter table replacement frames, and noisy frames such as `tun_build_skb.isra.50`, `build_skb`, `tun_flow_update`, `filemap_map_pages`, `tun_get_user`, and `tun_do_read`. It also uses panic-on-warn detection.

## Control Flow
The Linux reporter scans a mixed log where non-warning stack frames appear before the `WARNING: CPU ... proc_register` line. It should anchor report selection to the proc registration warning and derive the CLUSTERIP title. Panic is indicated immediately after the warning line.

## State And Persistence
The persistent state is expected metadata and a 159-line noisy report. Dynamic state includes network packets, filemap state, task ids, IP table/proc entry names, and addresses.

## Dependencies And Integration Points
It depends on warning boundary detection, proc-registration special title rules, netfilter stack parsing, and panic detection. It complements report 181 by testing noisy prelude tolerance.

## Risks
The parser could be distracted by TUN frames and title the report from `tun_get_user` or lock-acquisition helpers. It could also treat this as a duplicate of report 181 while losing the noisy-boundary regression value.

## Test Signals
Assert exact title, type, and panic flag. The report should include the `proc_register` warning and `clusterip_tg_check` frame even with surrounding TUN/VFS noise.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/205 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/206 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/206

## Purpose
This fixture validates corrupted suspicious-RCU parsing in a mixed memory-pressure and RDS report. Expected title is `WARNING: suspicious RCU usage`, type `WARNING`, and `CORRUPTED: Y`.

## Important APIs, Types, And Functions
The 323-line log contains `WARNING: suspicious RCU usage`, an enormous `vmalloc: allocation failure`, `Illegal context switch in RCU read-side critical section`, memory info, and later `BUG: sleeping function called from invalid context at mm/slab.h:420`. Important frames include `warn_alloc`, `__vmalloc_node_range`, `kvmalloc_node`, `xt_alloc_entry_offsets`, `translate_table`, `__rds_conn_create`, `lockdep_rcu_suspicious`, `___might_sleep`, `__might_sleep`, `rds_loop_conn_alloc`, and `rds_conn_create_outgoing`.

## Control Flow
The Linux reporter sees interleaved output from allocation failure and RCU/lockdep diagnostics. Because the expected report is marked corrupted and has a generic suspicious RCU title, the parser should not infer an allocator-specific RDS title as in reports 202 and 203. It must still classify it as a warning and flag corruption.

## State And Persistence
Persistent state is the expected metadata and long mixed console log. Dynamic state includes memory allocator counters, RCU state, task ids, lockdep state, and addresses.

## Dependencies And Integration Points
It depends on suspicious-RCU warning detection, corrupted-log heuristics, memory-info noise filtering, and warning type mapping. It integrates as a stress case for mixed concurrent console output.

## Risks
The parser may overfit to `rds_loop_conn_alloc` or netfilter allocation frames and emit a non-generic title. It may also misclassify as `LOCKDEP`, whereas the expected type is `WARNING`.

## Test Signals
Assert title `WARNING: suspicious RCU usage`, type `WARNING`, and `CORRUPTED: Y`. The selected report should include the illegal RCU context-switch line without relying on a stable allocator-specific title.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/206 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/207 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/207

## Purpose
This fixture verifies hang/stall parsing for an RCU scheduler stall in deferred BPF map freeing. Expected title is `INFO: rcu detected stall in bpf_map_free_deferred`, alt `stall in bpf_map_free_deferred`, and type `HANG`.

## Important APIs, Types, And Functions
The fixture contains an RCU stall report rather than an oops. Parser behavior under test includes `INFO: rcu_sched detected stalls on CPUs/tasks` matching, workqueue context extraction, and hang type mapping. Important frames include `_sched_show_task`, `sched_show_task`, `rcu_check_callbacks`, `update_process_times`, `tick_sched_timer`, `hrtimer_interrupt`, `free_percpu`, `array_map_free`, `bpf_map_free_deferred`, `process_one_work`, `worker_thread`, `kthread`, and `ret_from_fork`.

## Control Flow
The reporter detects the RCU stall line, parses the shown running task `kworker/0:0`, and uses the workqueue function `bpf_map_free_deferred` for the title. Runtime flow is workqueue execution of BPF map cleanup stuck or slow enough to trigger RCU stall reporting.

## State And Persistence
Persistent state is the expected metadata and a 45-line stall report. Dynamic state includes jiffies, CPU ids, task state, addresses, and RCU grace-period counters.

## Dependencies And Integration Points
It depends on Linux hang/RCU-stall parsing, workqueue function extraction, and alternate-title generation for stalls. It integrates with syzkaller's report parser tests for non-panic hangs.

## Risks
The parser could fail to parse a report without `BUG:` or `WARNING:` prefixes, or title from timer interrupt frames instead of `bpf_map_free_deferred`. It must also classify as `HANG`, not `WARNING`.

## Test Signals
Assert exact title, alt, and type `HANG`. The report should include the workqueue line `Workqueue: events bpf_map_free_deferred`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/207 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/208 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/208

## Purpose
This fixture validates corrupted suspicious-RCU warning parsing under fault injection and crypto/RDS noise. Expected title is `WARNING: suspicious RCU usage`, type `WARNING`, and `CORRUPTED: Y`.

## Important APIs, Types, And Functions
The 296-line log contains `WARNING: suspicious RCU usage`, `FAULT_INJECTION: forcing a failure`, held `rcu_read_lock` context in `__rds_conn_create`, crypto allocation failures, and a later sleeping-function invalid-context BUG. Important frames include `__rds_conn_create`, `lockdep_rcu_suspicious`, `___might_sleep`, `__might_sleep`, `should_fail`, `should_failslab`, `crypto_create_tfm`, `crypto_alloc_skcipher`, `cryptd_alloc_skcipher`, `simd_skcipher_init`, `drbg_init_sym_kernel`, `drbg_kcapi_seed`, `crypto_rng_reset`, `alg_setsockopt`, and `rds_loop_conn_alloc`.

## Control Flow
The Linux reporter should anchor on the suspicious RCU warning but treat the report as corrupted because fault-injection, crypto, CLUSTERIP, and RDS diagnostics are interleaved. The expected title is generic, not allocator-specific. Runtime flow includes AF_ALG setsockopt/DRBG setup and RDS connection creation while RCU context warnings are emitted.

## State And Persistence
Persistent state is the expected metadata and raw mixed log. Volatile state includes fault-injection state, crypto algorithm allocation failures, RCU lock context, PIDs, addresses, and socket options.

## Dependencies And Integration Points
It depends on suspicious-RCU matchers, corrupted-output heuristics, fault-injection noise filtering, and warning type mapping. It integrates with report tests as a high-noise RCU warning case distinct from the cleaner RDS fixtures.

## Risks
Parser regressions may choose crypto functions, RDS allocator functions, or the later sleeping-function warning as the title. It may also return `LOCKDEP` instead of the expected `WARNING`.

## Test Signals
Assert title `WARNING: suspicious RCU usage`, type `WARNING`, and corruption true. The report should preserve the illegal RCU critical-section evidence while tolerating fault-injection and crypto noise.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/208 -->
