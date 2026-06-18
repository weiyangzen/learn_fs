# Research Group: subset-b-009490

This grouped report covers syzkaller Linux report-parser golden fixtures under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report`. Each fixture is a persisted parser input: leading expectation headers are followed by kernel console text, and some files also contain an explicit `REPORT:` block for normalized extraction comparison.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/441 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/441

Purpose: golden fixture for Linux hung-task parsing where the canonical title is `INFO: task hung in rtnl_lock`, alternate title is `hang in rtnl_lock`, and crash type is `HANG`.

Important APIs, types, and functions: the fixture is consumed by `report_test.go` through `ParseTest`, `parseReport`, `parseHeaderLine`, `Reporter.Parse`, `Reporter.ContainsCrash`, and `crash.TitleToType`. The kernel stack exercises `rtnl_lock`, `ipv6_sock_ac_close`, `inet6_release`, `__sock_release`, `sock_close`, `__fput`, `task_work_run`, and exit-to-usermode paths. It also includes many lock inventory lines for `rtnl_mutex`, `pernet_ops_rwsem`, workqueue completions, and socket inode mutexes.

Control flow: the test reader first parses the three expectation headers, then feeds the full hung-task log to the Linux reporter. The log begins with a blocked `syz-executor.1` task, walks through scheduler and mutex acquisition frames into the IPv6 socket close path, prints all locks held in the system, and later includes additional blocked executor evidence. Parser control flow must choose the original hung-task report, retain `rtnl_lock` as the title frame, and avoid treating lock inventory or repeated blocked tasks as separate higher-priority reports.

State and persistence behavior: this is static testdata with no runtime mutation. The meaningful persisted state is the expected title, alternate title, and `HANG` type plus the raw console stream that preserves long lock-list ordering.

Dependencies and integration points: depends on Linux hung-task regexes in the report package, console-prefix stripping in the Linux reporter, and the test harness' convention that blank line separates headers from log. It integrates with syzkaller's report parser regression suite and protects parsing of network namespace/socket lock hangs.

Risks: the long file stresses parser boundaries because it contains many `rtnl_mutex` holders, repeated executor PIDs, workqueue stacks, and lock debug output. A too-greedy parser may select a later lock owner or emit a generic scheduler title instead of `rtnl_lock`.

Test signals: `INFO: task syz-executor.1:5269 blocked for more than 140 seconds`, stack frame `rtnl_lock+0x17/0x20`, IPv6 close frames, `Showing all locks held in the system`, and repeated `rtnetlink_rcv_msg`/workqueue holders of `rtnl_mutex`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/441 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/442 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/442

Purpose: golden fixture for a hung task in `synchronize_rcu`/`synchronize_sched` that escalates to a hung-task panic. Expected title is `INFO: task hung in synchronize_rcu`, alternate titles include both `synchronize_rcu` and legacy `synchronize_sched` forms, type is `HANG`, and `PANICKED: Y`.

Important APIs, types, and functions: parser APIs are the same `ParseTest` header contract and `Reporter.Parse` path. Kernel frames include `wait_for_completion`, `__wait_rcu_gp`, `synchronize_sched.part.0`, `synchronize_sched`, `synchronize_net`, `packet_release`, `__sock_release`, plus a secondary CPU backtrace in `tc_new_tfilter` via `rtnetlink_rcv_msg`.

Control flow: the log starts from a blocked packet socket release waiting for an RCU grace period. It then prints held locks, NMI backtraces, a contending netlink/tc stack, and finally `Kernel panic - not syncing: hung_task: blocked tasks`. The parser must still classify the root as a hang in RCU synchronization rather than the final panic or the unrelated NMI frame.

State and persistence behavior: persistent state is the panicked flag in the header and the raw panic tail. No mutable test state exists, but `PANICKED: Y` verifies that `linuxPanickedRe` is detected independently from title extraction.

Dependencies and integration points: depends on Linux RCU/hung-task report matchers, panic detection, and alternate-title generation that preserves older `synchronize_sched` naming. It integrates packet socket release and traffic-control netlink stacks into parser regression coverage.

Risks: kernel versions and function names may drift from `synchronize_sched` to `synchronize_rcu`; losing alternate titles would break deduplication across versions. NMI backtrace content can also distract guilty-frame selection.

Test signals: blocked `syz-executor.0`, `packet_release+0x978/0xc30`, `synchronize_net+0x4d/0x60`, NMI frame `tc_new_tfilter`, and `Kernel panic - not syncing: hung_task: blocked tasks`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/442 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/443 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/443

Purpose: golden fixture for Linux 4.4 hung-task parsing where the title is `INFO: task hung in rtnl_lock`, alternate title is `hang in rtnl_lock`, and type is `HANG`.

Important APIs, types, and functions: the syzkaller parser APIs are `ParseTest` headers and Linux report extraction. The kernel stacks cover `rtnl_lock`, `ipv6_route_ioctl`, `inet6_ioctl`, `sock_do_ioctl`, `sock_ioctl`, `do_vfs_ioctl`, plus multiple `proc_cleanup_work` workers in `synchronize_sched`, perf release paths, `tun_chr_close`, and `ipv6_sock_mc_close`.

Control flow: after header parsing, the reporter sees a primary blocked ioctl path holding `rtnl_mutex`. The file then includes other blocked workqueue and executor stacks, including compact `<Same stack as pid ...>` markers. The correct flow is to identify the first hung-task report and preserve the title frame from the route ioctl path.

State and persistence behavior: static golden data stores a noisy multi-task hung-task snapshot. The fixture persists older kernel formatting, including 4.4-style task lines and `<Same stack as pid>` summaries.

Dependencies and integration points: depends on compatibility with older Linux console formatting and lock-debug output. It integrates IPv6 route ioctl, proc namespace cleanup, perf teardown, and tun close hangs into one parser stress fixture.

Risks: repeated stacks and abbreviated stack references can confuse report end detection. If parser selection prefers later repeated stacks, title may become `synchronize_sched`, `perf_trace_destroy`, or `tun_chr_close` instead of `rtnl_lock`.

Test signals: `INFO: task syz-executor.4:15720 blocked`, frame `ipv6_route_ioctl+0x1f8/0x2b0`, held `rtnl_mutex`, workqueue `events proc_cleanup_work`, and several `<Same stack as pid ...>` lines.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/443 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/444 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/444

Purpose: compact golden fixture for a network namespace cleanup worker hung on `rtnl_lock`. Expected title is `INFO: task hung in rtnl_lock`, alternate title is `hang in rtnl_lock`, and type is `HANG`.

Important APIs, types, and functions: parser-facing types are the standard report fixture headers. Kernel frames are `rtnl_lock`, `nat_exit_net`, `ops_exit_list.isra.0`, `cleanup_net`, `process_one_work`, `worker_thread`, `kthread`, and `ret_from_fork`.

Control flow: the log contains a single blocked `kworker/u4:0` on the `netns cleanup_net` workqueue. The reporter strips prefixes, sees the hung-task banner, follows the call trace to the first non-scheduler blocking frame, and emits `rtnl_lock`.

State and persistence behavior: no runtime state is created; the file persists a minimal netns cleanup hang to keep parser behavior stable for short reports.

Dependencies and integration points: depends on hung-task matching, workqueue context parsing, and title selection for kernel worker tasks rather than syz-executor processes. Integrates netfilter NAT namespace teardown into Linux report tests.

Risks: because the fixture is short, over-filtering scheduler/mutex frames must still leave enough signal to title the report. Worker task names should not be required to contain `syz-executor`.

Test signals: `Workqueue: netns cleanup_net`, `rtnl_lock+0x17/0x20`, `nat_exit_net+0x25/0x380`, and `cleanup_net+0x4d8/0xa20`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/444 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/445 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/445

Purpose: golden fixture for a multi-task hang where the canonical title is `INFO: task hung in synchronize_rcu`, alternates include `synchronize_rcu_expedited`, and type is `HANG`.

Important APIs, types, and functions: parser APIs are fixture headers, `Reporter.Parse`, and title-to-type mapping. Kernel frames include `synchronize_rcu_expedited`, `synchronize_net`, `rollback_registered_many`, `unregister_netdevice_many`, `vti6_exit_batch_net`, `cleanup_net`, and many `rtnl_lock` waiters in `dev_ioctl` and `rtnetlink_rcv_msg`.

Control flow: a netns cleanup worker blocks in an expedited RCU grace period while syz-executor tasks block on RTNL-related ioctls and netlink requests. The parser must select the RCU synchronization hang from the first blocked task, generate alternate names, and keep later RTNL waiters as context.

State and persistence behavior: static data persists modern `[ T...]` task context prefixes and the full lock list. It has no `PANICKED` header, so panic detection should remain false.

Dependencies and integration points: depends on Linux console context stripping, hung-task start detection, alternate-title derivation, and network cleanup stack handling. Integrates vti6 namespace teardown and RTNL lock contention into the test suite.

Risks: there are many plausible blocking frames. A parser that reports the most frequent waiter would produce `rtnl_lock`; the expected result requires prioritizing the first reported hung task and mapping expedited RCU to the canonical synchronize-rcu title.

Test signals: blocked `kworker/u4:0` in `netns cleanup_net`, `synchronize_rcu_expedited+0x57f/0x5f0`, `rollback_registered_many`, several executor `dev_ioctl` stacks, and lock inventory for blocked tasks.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/445 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/446 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/446

Purpose: golden fixture for a TLS socket close hang. Expected title is `INFO: task hung in tls_sw_free_resources_tx`, alternate title is `hang in tls_sw_free_resources_tx`, type is `HANG`, and `PANICKED: Y`.

Important APIs, types, and functions: syzkaller report parsing uses the standard header contract and panic recognition. Kernel frames include `wait_for_completion`, `__flush_work`, `__cancel_work_timer`, `cancel_delayed_work_sync`, `tls_sw_free_resources_tx`, `tls_sk_proto_close`, `inet_release`, `__sock_release`, and `sock_close`.

Control flow: the blocked task waits while synchronously canceling delayed TLS transmit work during socket release. After lock inventory and NMI backtrace, the kernel panics on hung tasks. Parser flow must title the hang from `tls_sw_free_resources_tx` rather than scheduler, workqueue, or panic frames.

State and persistence behavior: static fixture persists the panic outcome and lock snapshot. It does not model runtime state beyond the reported pending work and socket close stack.

Dependencies and integration points: depends on Linux hung-task and panic parsing, plus frame filtering that skips generic completion and workqueue cancellation helpers. It integrates kernel TLS teardown into syzkaller parser coverage.

Risks: many frames are generic workqueue synchronization helpers; title extraction must descend far enough to the TLS-specific function. Panic tail must set `Panicked` without replacing the hang title.

Test signals: `cancel_delayed_work_sync`, `tls_sw_free_resources_tx+0x1df/0xcf0`, `tls_sk_proto_close+0x602/0x750`, and `Kernel panic - not syncing: hung_task: blocked tasks`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/446 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/447 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/447

Purpose: golden fixture for repeated 9p transport close hangs. Expected title is `INFO: task hung in p9_fd_close`, alternate title is `hang in p9_fd_close`, type is `HANG`, and `PANICKED: Y`.

Important APIs, types, and functions: report parser interfaces are the same fixture and `Reporter.Parse` path. Kernel frames include `wait_for_completion`, `__flush_work`, `__cancel_work_timer`, `cancel_work_sync`, `p9_fd_close`, `p9_client_create`, `v9fs_session_init`, and VFS mount setup.

Control flow: several syz-executor tasks block in the same 9p close stack while creating v9fs sessions. The log then prints lock inventory, NMI CPU backtraces, an idle CPU stack, and a hung-task panic. The parser must collapse the repeated evidence into one report titled by `p9_fd_close`.

State and persistence behavior: static testdata persists repeated blocked tasks and a panic tail. It has no mutable state, but the repeated stacks encode a regression case for report deduplication and title stability.

Dependencies and integration points: depends on hung-task detection, workqueue-helper frame filtering, panic detection, and compatibility with many executor task names. It integrates 9p/V9FS mount initialization into report tests.

Risks: repeated nearly identical stacks can cause parser end-position or title instability. Generic cancellation frames should not hide the 9p-specific blocking function.

Test signals: multiple `INFO: task syz-executor... blocked`, `p9_fd_close+0x376/0x5c0`, `p9_client_create+0xa41/0x159b`, `v9fs_session_init`, and final `hung_task: blocked tasks` panic.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/447 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/448 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/448

Purpose: golden fixture for a kernel BUG caused by an skb over-panic in PF_KEY/XFRM output. Expected title is `kernel BUG in pfkey_send_acquire`, type is `BUG`, and `PANICKED: Y`.

Important APIs, types, and functions: parser consumes `TYPE: BUG` and panic status through `ParseTest`. Kernel frames include `skb_panic`, `skb_put.cold`, `pfkey_send_acquire`, `km_query`, `xfrm_state_find`, `xfrm_tmpl_resolve`, `xfrm_lookup_with_ifid`, `ip_route_output_flow`, `udp_sendmsg`, and `udpv6_sendmsg`.

Control flow: the console starts with `skbuff: skb_over_panic`, then a `kernel BUG at net/core/skbuff.c:108`, invalid opcode, full trace, repeated RIP register dump, and a fatal-exception panic. The parser must report the semantic caller `pfkey_send_acquire`, not the low-level `skb_panic`.

State and persistence behavior: no runtime state is changed by the fixture. The persistent expectation verifies that panic-on-fatal-exception is captured and that low-level skb helpers are treated as less guilty than PF_KEY.

Dependencies and integration points: depends on Linux BUG/oops regexes, stack guilty-frame selection, and panic detection. It integrates skbuff, PF_KEY, XFRM, and UDPv6 send paths into parser coverage.

Risks: the first RIP is `skb_panic`, so naive top-frame title selection would be less useful. Interleaved kobject messages test report boundary handling.

Test signals: `skb_over_panic`, `kernel BUG at net/core/skbuff.c:108`, stack `skb_put.cold -> pfkey_send_acquire -> km_query -> xfrm_state_find`, and `Kernel panic - not syncing: Fatal exception`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/448 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/449 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/449

Purpose: golden fixture for KCSAN race report parsing. Expected title is `KCSAN: data-race in netlink_recvmsg / netlink_recvmsg`, type is `KCSAN-DATARACE`, and `PANICKED: Y`.

Important APIs, types, and functions: the fixture uses the optional `REPORT:` block path in `parseReport`, so `ParseTest.HasReport` and normalized `Report` comparison are important. Kernel frames include two racing `netlink_recvmsg` accesses, `sock_recvmsg_nosec`, `___sys_recvmsg`, `do_recvmmsg`, `sock_recvmsg`, `__sys_recvfrom`, `kcsan_report`, `kcsan_setup_watchpoint`, and `__tsan_unaligned_write2`.

Control flow: the log contains the raw KCSAN report, then panic-on-warn stack text, then an explicit normalized `REPORT:` block. The parser must detect KCSAN as the crash, set the panicked flag from the later panic, and return a report body matching the normalized block rather than including the panic tail.

State and persistence behavior: static data stores both raw console output and expected normalized report body. There is no mutable state, but this fixture persists a dual-section oracle for report extraction.

Dependencies and integration points: depends on KCSAN-specific Linux oops matchers, normalized report extraction, and the test harness' `REPORT:` comparison. It integrates netlink receive paths and KCSAN sanitizer output.

Risks: if the parser includes the panic stack in the report body, `HasReport` comparison fails. If the title normalizer loses the two-function race format, deduplication across KCSAN reports degrades.

Test signals: `BUG: KCSAN: data-race in netlink_recvmsg / netlink_recvmsg`, two write stacks to the same address, `Reported by Kernel Concurrency Sanitizer`, panic-on-warn, and explicit `REPORT:` block.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/449 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/45 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/45

Purpose: golden fixture for ARM64 paging-request parsing in ALSA timer teardown. Expected title is `BUG: unable to handle kernel paging request in _snd_timer_stop`, alternate title is `bad-access in _snd_timer_stop`, type is `MEMORY_SAFETY_BUG`, and `CORRUPTED: Y`.

Important APIs, types, and functions: parser fields include `Corrupted` and memory-safety crash typing. Kernel frames are represented in ARM64 style with `PC is at _snd_timer_stop.constprop.9+0x184/0x2b0`, `LR is at` the same function, and register/state lines.

Control flow: after headers, the log reports lock debugging disabled by taint, a bad virtual address `dead000000000108`, page table state, internal oops, and an ARM64 PC/LR crash location. The parser must extract the title from `PC is at` formatting rather than x86 `RIP:`.

State and persistence behavior: static corrupted fixture; `CORRUPTED: Y` records that report extraction should mark the crash as potentially unreliable. No runtime state is updated.

Dependencies and integration points: depends on Linux ARM64 oops parsing, bad-access alternate-title generation, corruption detection, and `crash.TitleToType` mapping to `MEMORY_SAFETY_BUG`.

Risks: architecture-specific format can be missed by x86-only parsing. The `dead...` poison address and taint text are strong signals for corruption and must not suppress the report.

Test signals: `Unable to handle kernel paging request`, address `dead000000000108`, `Internal error: Oops`, `PC is at _snd_timer_stop.constprop.9`, and corrupted expectation header.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/45 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/450 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/450

Purpose: golden fixture for a boot-time general protection fault in the DMA/SCSI initialization path. Expected title is `general protection fault in dma_direct_max_mapping_size`, alternate title is `bad-access in dma_direct_max_mapping_size`, type is `DoS`, and `PANICKED: Y`.

Important APIs, types, and functions: parser APIs include GPF detection, bad-access alternate generation, and panic recognition. Kernel frames include `dma_direct_max_mapping_size`, `dma_max_mapping_size`, `__scsi_init_queue`, `scsi_mq_alloc_queue`, `scsi_alloc_sdev`, `scsi_probe_and_add_lun`, `__scsi_scan_target`, `do_scan_async`, `async_run_entry_fn`, and workqueue execution.

Control flow: the file contains a long boot log with subsystem initialization noise before the crash. The actual report begins around the KASAN GPF lines in `kworker/u4:1` on `events_unbound async_run_entry_fn`. The parser must ignore earlier boot warnings and device registration chatter, select the DMA direct mapping RIP, follow the SCSI scan call trace, and set `Panicked` from the fatal-exception tail.

State and persistence behavior: static boot-log fixture persists interleaved kobject messages and repeated RIP/register blocks. No mutable state exists, but the file protects parser start-boundary and noise handling.

Dependencies and integration points: depends on Linux console-prefix stripping with `[ T...]` contexts, GPF detection, KASAN noise tolerance, guilty-frame selection, and panic matching. It integrates DMA mapping, SCSI scan, async workqueue, and boot-time device discovery paths.

Risks: the long prelude includes a `WARNING: workqueue cpumask...` that should not become the title. Interleaved device/kobject logs in the middle of the call trace can break simplistic contiguous-stack parsers.

Test signals: `general protection fault: 0000 [#1] PREEMPT SMP KASAN`, `RIP: 0010:dma_direct_max_mapping_size+0x7c/0x1a7`, `Workqueue: events_unbound async_run_entry_fn`, SCSI allocation frames, and `Kernel panic - not syncing: Fatal exception`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/450 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/451 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/451

Purpose: golden fixture for an intentional LKDTM-style bad address dereference. Expected title is `general protection fault in deliberately_dereference_bad_address`, alternate title is `bad-access in deliberately_dereference_bad_address`, and type is `DoS`.

Important APIs, types, and functions: parser fields cover GPF recognition and bad-access alternate-title creation. Kernel frames include `deliberately_dereference_bad_address`, `do_vfs_ioctl`, `ksys_ioctl`, `__x64_sys_ioctl`, `do_syscall_64`, and syscall entry.

Control flow: an ioctl process triggers a non-canonical address GPF with KASAN `maybe wild-memory-access` output. The parser must title from the kernel RIP, preserve syscall-origin context as supporting evidence, and not require a panic tail.

State and persistence behavior: static non-panicking crash fixture. Persisted state is limited to the expectation headers and the raw GPF report.

Dependencies and integration points: depends on x86 GPF parsing, KASAN auxiliary-line tolerance, and alternate-title mapping for bad accesses. It integrates ioctl-triggered LKDTM fault injection into report tests.

Risks: helper frames and repeated final RIP/register blocks can cause duplicated extraction. The magic address `00badbeefbadbeef` should be evidence, not part of title normalization.

Test signals: `general protection fault for non-canonical address`, KASAN wild-memory-access range, `RIP: deliberately_dereference_bad_address+0x33/0x60`, and ioctl syscall frames.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/451 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/452 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/452

Purpose: companion golden fixture for a segment-related general protection fault in `deliberately_dereference_bad_address`. Expected title and alternate match report `451`, with type `DoS`.

Important APIs, types, and functions: parser coverage is GPF detection, title normalization across related fault wording, and bad-access alternate generation. Kernel frames include `deliberately_dereference_bad_address`, `do_vfs_ioctl`, `ksys_ioctl`, `__x64_sys_ioctl`, and `do_syscall_64`.

Control flow: the log starts with `segment-related general protection fault: beec`, reports RIP at offset `+0x1b`, shows ioctl call trace, and then repeats an older RIP/register block at offset `+0x33`. The parser must use the active fault site but normalize to the same function-level title.

State and persistence behavior: static fixture with no panic and no `REPORT:` block. It persists variant GPF wording and repeated RIP text.

Dependencies and integration points: depends on Linux x86 GPF regexes and title canonicalization by function name. It integrates fault-injection ioctl behavior with report deduplication across similar bad-address crashes.

Risks: repeated trailing RIP from another fault context may confuse start/end handling. Segment-related wording must still map to a general protection fault.

Test signals: `segment-related general protection fault: beec`, first `RIP: deliberately_dereference_bad_address+0x1b/0x60`, ioctl stack, and repeated `badbeef` register state.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/452 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/453 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/453

Purpose: golden fixture for UBSAN out-of-bounds parsing in LKDTM. Expected title is `UBSAN: undefined-behaviour in lkdtm_ARRAY_BOUNDS` and type is `UBSAN`.

Important APIs, types, and functions: parser coverage includes UBSAN report recognition and stack-based title extraction. Kernel frames include `__ubsan_handle_out_of_bounds`, `lkdtm_ARRAY_BOUNDS`, `lkdtm_do_action`, `direct_entry`, `full_proxy_write`, `__vfs_write`, `vfs_write`, and `ksys_write`.

Control flow: the report begins with a UBSAN undefined-behaviour line referencing `drivers/misc/lkdtm/bugs.c:243:16`, then a call trace from UBSAN epilogue through LKDTM's direct debugfs/proc entry and the write syscall. The parser should report the LKDTM action function rather than the generic UBSAN handler.

State and persistence behavior: static sanitizer fixture with no panic flag. It persists source-location details and module-qualified `[lkdtm]` frame names.

Dependencies and integration points: depends on Linux UBSAN oops patterns, module suffix handling, and frame filtering for sanitizer helpers. It integrates LKDTM fault injection into report tests.

Risks: title extraction could stop at `__ubsan_handle_out_of_bounds` or include `.cold`/module suffixes if normalization regresses.

Test signals: `UBSAN: Undefined behaviour in drivers/misc/lkdtm/bugs.c:243:16`, `__ubsan_handle_out_of_bounds.cold`, `lkdtm_ARRAY_BOUNDS.cold.2 [lkdtm]`, and write syscall frames.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/453 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/454 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/454

Purpose: golden fixture for UBSAN out-of-bounds parsing in the V4L2 test pattern generator. Expected title is `UBSAN: undefined-behaviour in precalculate_color` and type is `UBSAN`.

Important APIs, types, and functions: parser-facing behavior is UBSAN recognition and guilty-frame selection. Kernel frames include `precalculate_color`, `tpg_recalc`, `tpg_calc_text_basep`, `vivid_fillbuff`, `vivid_thread_vid_cap_tick`, `vivid_thread_vid_cap`, `kthread`, and `ret_from_fork`.

Control flow: a Vivid video capture kernel thread hits a UBSAN out-of-bounds report at `drivers/media/common/v4l2-tpg/v4l2-tpg-core.c:942:56`. The reporter must skip UBSAN helper frames and title the report from `precalculate_color`.

State and persistence behavior: static fixture; the persisted state includes one expected title/type and a thread-driven call trace. No panic or corruption state is expected.

Dependencies and integration points: depends on UBSAN parsing and stack frame normalization. Integrates media/v4l2-tpg and vivid virtual video capture threads into Linux parser tests.

Risks: since the crash happens in a kernel thread rather than a syscall, parser logic should not depend on user RIP frames. Helper frame filtering must expose the media-specific function.

Test signals: UBSAN line for `v4l2-tpg-core.c:942:56`, `precalculate_color+0x304e/0x3830`, `vivid_fillbuff`, and `vivid_thread_vid_cap`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/454 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/455 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/455

Purpose: golden fixture for UBSAN shift-out-of-bounds parsing in SUNRPC transport timeout calculation. Expected title is `UBSAN: undefined-behaviour in xprt_calc_majortimeo` and type is `UBSAN`.

Important APIs, types, and functions: parser coverage includes `__ubsan_handle_shift_out_of_bounds` filtering and stack title extraction. Kernel frames include `xprt_calc_majortimeo`, `xprt_do_reserve`, `xprt_reserve`, `call_reserve`, `__rpc_execute`, `rpc_execute`, `rpc_run_task`, `rpc_call_sync`, and `rpc_create_xprt`.

Control flow: the report identifies undefined behaviour at `net/sunrpc/xprt.c:597:14`, then shows the RPC client task path that reserves transport resources. The reporter must title from `xprt_calc_majortimeo` rather than the UBSAN helper.

State and persistence behavior: static sanitizer fixture with no panicked/corrupted state. It persists a deeper call chain through RPC task execution for parser regression coverage.

Dependencies and integration points: depends on UBSAN shift report detection, generic helper-frame suppression, and SUNRPC stack frame normalization. Integrates network filesystem/RPC behavior into the report suite.

Risks: many `rpc_*` frames are plausible but less precise than the timeout calculation function. Parser changes that over-trim `.cold` UBSAN helper paths should still preserve the next frame.

Test signals: `UBSAN: Undefined behaviour in net/sunrpc/xprt.c:597:14`, `__ubsan_handle_shift_out_of_bounds`, `xprt_calc_majortimeo+0x210/0x280`, and RPC reserve/execute frames.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/455 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/456 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/456

Purpose: golden fixture for UBSAN shift-out-of-bounds parsing in F2FS mount setup. Expected title is `UBSAN: undefined-behaviour in f2fs_fill_super` and type is `UBSAN`.

Important APIs, types, and functions: parser behavior includes UBSAN source-line recognition and stack guilty-frame extraction. Kernel frames include `f2fs_fill_super.cold`, `mount_bdev`, `f2fs_mount`, `legacy_get_tree`, `vfs_get_tree`, `do_mount`, `ksys_mount`, and `__x64_sys_mount`.

Control flow: a mount syscall triggers undefined behavior at `fs/f2fs/super.c:2563:16`. The parser follows the UBSAN report into the filesystem superblock fill path and ignores unrelated perf-rate chatter interleaved later in the log.

State and persistence behavior: static non-panicking fixture. Persisted state is the expected UBSAN title/type and raw mount-path stack.

Dependencies and integration points: depends on UBSAN parsing, syscall stack handling, and filesystem frame normalization that drops `.cold` suffixes from the title. Integrates F2FS mount handling into report tests.

Risks: interleaved performance messages can disrupt contiguous report extraction. Title normalization should not emit `f2fs_fill_super.cold.79`.

Test signals: `UBSAN: Undefined behaviour in fs/f2fs/super.c:2563:16`, `__ubsan_handle_shift_out_of_bounds`, `f2fs_fill_super.cold.79`, and mount syscall frames.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/456 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/457 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/457

Purpose: golden fixture for UBSAN out-of-bounds parsing in the 6pack hamradio line discipline. Expected title is `UBSAN: undefined-behaviour in decode_data` and type is `UBSAN`.

Important APIs, types, and functions: parser behavior includes UBSAN helper filtering and workqueue-context handling. Kernel frames include `decode_data`, `sixpack_receive_buf`, `tty_ldisc_receive_buf`, `tty_port_default_receive_buf`, `flush_to_ldisc`, `process_one_work`, and workqueue thread helpers.

Control flow: the workqueue `events_unbound flush_to_ldisc` processes TTY input, reaches `sixpack_receive_buf`, and UBSAN reports an out-of-bounds condition at `drivers/net/hamradio/6pack.c:843:16`. The title should use `decode_data`.

State and persistence behavior: static fixture with no panic. It persists a TTY workqueue stack rather than a direct syscall-triggered report.

Dependencies and integration points: depends on UBSAN report matching, workqueue context parsing, and network/TTY frame normalization. Integrates hamradio 6pack receive parsing into the regression suite.

Risks: parser frame filtering might select `sixpack_receive_buf` if it misses the more precise `decode_data` frame. Workqueue context should not obscure the report body.

Test signals: `Workqueue: events_unbound flush_to_ldisc`, source location `drivers/net/hamradio/6pack.c:843:16`, `decode_data+0x308/0x3a0`, and TTY ldisc receive frames.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/457 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/458 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/458

Purpose: golden fixture for an input-device teardown GPF where expected title is `general protection fault in input_close_device`, alternate title is `bad-access in input_close_device`, type is `DoS`, and `PANICKED: Y`.

Important APIs, types, and functions: parser coverage includes GPF parsing, bad-access alternate generation, and panic recognition. Kernel frames include `timer_is_static_object`, `debug_object_assert_init`, `del_timer`, `try_to_grab_pending`, `input_close_device`-related teardown, and userspace return frames.

Control flow: the immediate RIP is inside debugobjects/timer validation, with a call trace that flows through timer deletion and pending-work handling during input close. The parser's guilty-frame logic is expected to title the report as `input_close_device` rather than `timer_is_static_object`.

State and persistence behavior: static fixture persists fatal-exception panic state and repeated RIP/register output. No mutable runtime state is represented beyond the freed/uninitialized object implied by debugobjects.

Dependencies and integration points: depends on GPF/oops patterns, guilty-frame ranking that ignores generic debugobject helpers, and panic detection. Integrates input subsystem close paths and timer debug checks into report tests.

Risks: top-frame title selection would produce a generic debugobject function. The expected input-subsystem title relies on source/stack heuristics that may change as kernel internals evolve.

Test signals: `general protection fault: 0000 [#1] SMP KASAN`, `RIP: timer_is_static_object`, `debug_object_assert_init`, `del_timer`, `try_to_grab_pending`, and fatal-exception panic.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/458 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/459 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/459

Purpose: golden fixture for a page fault during USB HID/input device removal. Expected title is `BUG: unable to handle kernel paging request in input_unregister_device`, alternate title is `bad-access in input_unregister_device`, type is `MEMORY_SAFETY_BUG`, and `PANICKED: Y`.

Important APIs, types, and functions: parser behavior includes page-fault classification, bad-access alternate creation, and panic detection. Kernel frames include `kobject_put`, `device_del`, `input_unregister_device`, `hidinput_disconnect`, `hid_disconnect`, `hid_hw_stop`, `ms_remove`, `hid_device_remove`, and USB hub workqueue handling.

Control flow: a `usb_hub_wq hub_event` worker faults in `kobject_put`; the stack identifies the higher-level input unregister path during HID disconnect. The parser must prefer `input_unregister_device` over the generic `kobject_put` top frame and handle an interleaved raw-gadget failure message.

State and persistence behavior: static fixture with fatal-exception panic state. It persists teardown ordering and repeated RIP/register sections but no mutable test state.

Dependencies and integration points: depends on Linux page-fault oops parsing, stack guilty-frame ranking, panic detection, and workqueue context handling. Integrates USB HID, input, device core, and raw gadget noise into parser coverage.

Risks: generic device-core frames can hide the subsystem-specific cause. Interleaved `raw_ioctl_run` text can break report body extraction if boundaries are too strict.

Test signals: `BUG: unable to handle page fault`, `Workqueue: usb_hub_wq hub_event`, `RIP: kobject_put`, stack `device_del -> input_unregister_device -> hidinput_disconnect`, and fatal-exception panic.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/459 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/46 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/46

Purpose: golden fixture for an ARM-style paging request in block request scatter-gather mapping. Expected title is `BUG: unable to handle kernel paging request in blk_rq_map_sg`, alternate title is `bad-access in blk_rq_map_sg`, type is `MEMORY_SAFETY_BUG`, and `CORRUPTED: Y`.

Important APIs, types, and functions: parser fields cover memory-safety typing and corruption. The key kernel crash frame is `PC is at blk_rq_map_sg+0x70/0x2c0`.

Control flow: the log records a paging request/oops with architecture-specific `PC is at` formatting. The parser must extract the function from PC rather than x86 RIP and set the corrupted bit from expectation metadata.

State and persistence behavior: static corrupted fixture. The file persists a minimal block-layer crash report and does not include panic state.

Dependencies and integration points: depends on architecture-neutral Linux oops parsing, bad-access alternate generation, and corruption expectations in `ParseTest`. Integrates block layer request mapping into report regression coverage.

Risks: short reports provide little fallback context, so missing `PC is at` support would lose the title. Corruption status must not suppress crash detection.

Test signals: paging-request header, `PC is at blk_rq_map_sg+0x70/0x2c0`, expected `MEMORY_SAFETY_BUG`, and `CORRUPTED: Y`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/46 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/460 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/460

Purpose: golden fixture for warning parsing in input device registration. Expected title is `WARNING in input_register_device`, type is `WARNING`, and `PANICKED: Y`.

Important APIs, types, and functions: parser behavior includes warning-title extraction and panic-on-warn detection. Kernel frames include `add_uevent_var`, `__warn`, `report_bug`, `do_error_trap`, `input_register_device`-related USB/input device setup, `usb_set_configuration`, `usb_new_device`, and `hub_event`.

Control flow: a USB hub worker triggers a warning at `lib/kobject_uevent.c:670` and panic-on-warn follows immediately. The stack later reaches input registration during USB configuration. The parser should title the warning by the subsystem-level `input_register_device` rather than only `add_uevent_var`.

State and persistence behavior: static warning fixture with `PANICKED: Y`. It persists a long USB probe stack and warning panic tail.

Dependencies and integration points: depends on Linux warning report matching, panic-on-warn detection, and guilty-frame selection through device core/USB/input layers. Integrates USB input registration with kobject uevent warnings.

Risks: the first warning site is a generic kobject helper, so parser ranking is needed to preserve the expected input registration title. Immediate panic lines must not end extraction before the useful stack appears.

Test signals: `WARNING: CPU: 1 PID: 22 at lib/kobject_uevent.c:670 add_uevent_var`, `Kernel panic - not syncing: panic_on_warn set ...`, `Workqueue: usb_hub_wq hub_event`, `RIP: add_uevent_var`, and USB/input registration frames.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/460 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/461 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/461

Purpose: golden fixture for a stack segment fault in early init. Expected title is `stack segment fault in kernel_init`, type is `DoS`, and `PANICKED: Y`.

Important APIs, types, and functions: parser coverage includes x86 exception wording outside the usual BUG/WARNING forms. Kernel frames include `kernel_init`, optional `rest_init`, `ret_from_fork`, and the panic path for killing init.

Control flow: PID 1 faults in `kernel_init`, the trace is short, and the kernel panics with `Attempted to kill init! exitcode=0x0000000b`. The parser must title from the exception plus RIP function and detect the panic tail.

State and persistence behavior: static boot/early-init crash fixture. It persists fatal process state through the panic line but has no mutable test state.

Dependencies and integration points: depends on Linux exception pattern matching for `stack segment`, RIP extraction, and panic detection. Integrates init-thread faults into report parser coverage.

Risks: short trace and absent syz-executor context can expose assumptions that crashes always occur in fuzzing tasks. The panic line should not replace the original stack-segment fault title.

Test signals: `stack segment: 0000 [#1]`, `RIP: kernel_init+0x55/0x122`, `ret_from_fork`, and `Kernel panic - not syncing: Attempted to kill init`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/461 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/462 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/462

Purpose: golden fixture for RCU stall parsing in ipset add handling. Expected title is `INFO: rcu detected stall in ip_set_uadd`, alternate title is `stall in ip_set_uadd`, and type is `HANG`.

Important APIs, types, and functions: parser behavior includes RCU stall recognition and user-context stack title extraction. Kernel frames include `hash_ipportnet4_expire`, `hash_ipportnet4_add`, `hash_ipportnet4_uadt`, `call_ad`, `ip_set_ad.isra.28`, `ip_set_uadd`, `nfnetlink_rcv_msg`, `netlink_rcv_skb`, `nfnetlink_rcv`, `netlink_unicast`, and `netlink_sendmsg`.

Control flow: an RCU preempt self-detected stall on CPU 3 triggers NMI backtrace output. After IRQ/timer frames, the interrupted code is an ipset hash expiration/add path reached through nfnetlink sendmsg. The parser must identify `ip_set_uadd` as the semantic stalled operation.

State and persistence behavior: static non-panicking stall fixture. It persists RCU generation/jiffies details and the interrupted stack.

Dependencies and integration points: depends on RCU stall oops matching, IRQ frame handling, and stack frame ranking across netfilter/ipset functions. Integrates ipset netlink add behavior into parser tests.

Risks: the current RIP is `hash_ipportnet4_expire`, while the expected title is the higher-level operation `ip_set_uadd`; parser heuristics must preserve that call-chain judgment.

Test signals: `rcu_preempt self-detected stall on CPU`, NMI backtrace, `hash_ipportnet4_expire`, `hash_ipportnet4_add`, `ip_set_uadd`, and netlink sendmsg syscall frames.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/462 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/463 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/463

Purpose: golden fixture for RCU stall parsing in generic ipset add/delete handling. Expected title is `INFO: rcu detected stall in ip_set_ad`, alternate title is `stall in ip_set_ad`, and type is `HANG`.

Important APIs, types, and functions: parser coverage includes RCU stall detection and title selection from netfilter/ipset call chains. Kernel frames include `hash_ip4_expire.isra.17`, `hash_ip4_add`, `hash_ip4_uadt`, `call_ad`, `ip_set_ad.isra.33`, `nfnetlink_rcv_msg`, `nfnetlink_rcv`, `netlink_unicast`, and `netlink_sendmsg`.

Control flow: the CPU self-detected RCU stall interrupts an ipset hash operation. The report moves from timer/RCU backtrace frames to the network set update path and then to a userspace `sendmsg`. The parser should report the higher-level `ip_set_ad` operation.

State and persistence behavior: static stall fixture with no panic. It persists older prefix formatting without `[T...]` contexts on every line.

Dependencies and integration points: depends on Linux RCU stall matchers, IRQ boundary stripping, and netfilter frame ranking. Integrates ipset hash4 add/update paths into the parser suite.

Risks: top interrupted frame `hash_ip4_expire` could be chosen if the parser does not climb the stack. `ip_set_ad.isra.33` suffix normalization should still match the expected title.

Test signals: `rcu_sched self-detected stall on CPU`, `hash_ip4_expire.isra.17`, `hash_ip4_add`, `ip_set_ad.isra.33`, `nfnetlink_rcv_msg`, and `sendmsg` syscall frames.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/463 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/464 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/464

Purpose: golden fixture for RCU stall parsing in nftables generation query handling. Expected title is `INFO: rcu detected stall in nf_tables_getgen`, alternate title is `stall in nf_tables_getgen`, and type is `HANG`.

Important APIs, types, and functions: parser behavior includes RCU stall detection and selection of netfilter control-plane frames. Kernel frames include `check_memory_region`, `rcu_is_watching`, `rcu_read_lock_held_common`, `rcu_read_lock_held`, `netlink_lookup`, `netlink_unicast`, `nf_tables_getgen`, `nfnetlink_rcv_msg`, `nfnetlink_rcv`, and `netlink_sendmsg`.

Control flow: the RCU stall report starts with timer/NMI backtrace frames, then lands in KASAN memory checking and RCU lock-state helpers before the netlink/nftables call path. The parser must skip low-level instrumentation and choose `nf_tables_getgen`.

State and persistence behavior: static non-panicking hang fixture. It persists the interrupted CPU state and netlink syscall context.

Dependencies and integration points: depends on RCU stall parsing, KASAN/helper frame filtering, and nftables/netlink stack ranking. Integrates nftables generation queries into syzkaller report coverage.

Risks: instrumentation frames such as `check_memory_region` and RCU lock helpers are noisy and could produce poor titles. The expected title relies on deeper stack inspection.

Test signals: `rcu_sched self-detected stall on CPU`, `RIP: check_memory_region`, frames `rcu_read_lock_held -> netlink_lookup -> netlink_unicast -> nf_tables_getgen`, and netlink sendmsg syscall context.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/464 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/465 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/465

Purpose: golden fixture for RCU stall parsing where the interrupted top frame is lockdep. Expected title is `INFO: rcu detected stall in lock_is_held_type`, alternate title is `stall in lock_is_held_type`, and type is `HANG`.

Important APIs, types, and functions: parser coverage includes RCU stall matching and accepting lockdep helper frames as the expected title when they are the interrupted RIP. Kernel frames include `lock_is_held_type`, `rcu_read_lock_held`, `nfnetlink_rcv_msg`, `netlink_rcv_skb`, `nfnetlink_rcv`, `netlink_unicast`, `netlink_sendmsg`, and `__sys_sendmsg`.

Control flow: an RCU sched stall interrupts CPU 1 in `lock_is_held_type` while processing nfnetlink sendmsg. Unlike the previous nftables fixture, the expected title is the lockdep frame itself, so parser ranking must not always skip lock helpers for RCU stalls.

State and persistence behavior: static non-panicking stall fixture. It persists CPU/jiffies RCU stall counters, interrupted register state, and netlink receive stack.

Dependencies and integration points: depends on RCU stall parser rules, IRQ/timer frame stripping, and nuanced guilty-frame selection. Integrates lockdep/RCU state checking inside nfnetlink message processing.

Risks: overly aggressive helper filtering could skip `lock_is_held_type` and title the report as `nfnetlink_rcv_msg`; overly shallow parsing could lose netlink context. The fixture locks in the current expected balance.

Test signals: `rcu_sched self-detected stall on CPU`, `RIP: lock_is_held_type+0x1ca/0x240`, `rcu_read_lock_held`, `nfnetlink_rcv_msg`, and sendmsg syscall frames.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/465 -->
