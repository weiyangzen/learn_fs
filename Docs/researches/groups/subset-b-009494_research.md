# subset-b-009494 research

Grouped research for syzkaller Linux report parser fixtures under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report`. Each section preserves the exact source path and is intended to be split into the mapped source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/608 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/608

## Purpose
This fixture validates recognition of an `ATOMIC_SLEEP` report titled `BUG: sleeping function called from invalid context in __alloc_skb`. It models a netlink/nfnetlink send path that reaches `netlink_ack`, `__alloc_skb`, and `kmem_cache_alloc_node` while RCU/preemption context is still relevant.

## Important APIs, types, and functions
Key symbols are `___might_sleep`, `__alloc_skb`, `netlink_ack`, `netlink_rcv_skb`, `nfnetlink_rcv`, `netlink_unicast`, `netlink_sendmsg`, `__sys_sendmsg`, and `do_syscall_64`. The header fields `TITLE` and `TYPE` are the expected parser outputs.

## Control flow
The log starts with the metadata oracle, then a kernel diagnostic, lock context, preemption-disabled site in `__dev_queue_xmit`, and the syscall stack from `sendmsg`.

## State and persistence behavior
The file is static test data. It persists only the expected classification and the raw console lines needed to reproduce parser matching.

## Dependencies and integration points
It integrates with syzkaller's Linux report extraction tests and exercises parsing of sleeping-in-atomic reports that include lock-held and preemption context.

## Risks and test signals
The main risk is misattributing the title to allocation helpers instead of preserving the canonical `__alloc_skb` frame. Test success is signaled by `TYPE: ATOMIC_SLEEP` and the exact title.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/608 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/609 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/609

## Purpose
This fixture covers a normal `WARNING` report titled `WARNING: zero-size vmalloc in dvb_dmx_init`. It represents a USB DVB probe path that requests a zero-sized vmalloc region.

## Important APIs, types, and functions
Important frames include `__vmalloc_node_range`, `vmalloc`, `dvb_dmx_init`, `dvb_usb_adapter_dvb_init`, `dvb_usb_device_init`, `cxusb_probe`, `usb_probe_interface`, `really_probe`, `device_add`, and `hub_event`.

## Control flow
The kernel worker `kworker/0:1` handles `usb_hub_wq hub_event`, probes a USB device, enters DVB initialization, and triggers the warning in vmalloc validation.

## State and persistence behavior
The fixture stores a complete warning stack but no mutable state. The parser-relevant persistent state is the expected `TITLE` and `TYPE` at the top.

## Dependencies and integration points
It links syzkaller report parsing with Linux USB, driver core, media/DVB, and memory-management warning formats.

## Risks and test signals
The parser must prefer the semantic title `zero-size vmalloc in dvb_dmx_init`, not a generic `WARNING in __vmalloc_node_range`. The `TYPE: WARNING` header is the oracle.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/609 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/61 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/61

## Purpose
This very small fixture marks an RCU stall report as corrupted. It expects `TITLE: INFO: rcu detected stall in corrupted`, `ALT: stall in corrupted`, `TYPE: HANG`, and `CORRUPTED: Y`.

## Important APIs, types, and functions
The only raw log signal is `INFO: rcu_sched self-detected stall on CPU`. The important parser API behavior is not stack extraction but corruption-aware classification.

## Control flow
The metadata header precedes a minimal RCU stall line. There is not enough stack context to identify a trustworthy blocked function, so the expected function token is `corrupted`.

## State and persistence behavior
The fixture persists a negative-quality crash sample. `CORRUPTED: Y` is part of the expected state consumed by the report test harness.

## Dependencies and integration points
It integrates with syzkaller's RCU stall and hang recognizers and verifies that incomplete logs do not produce overconfident function names.

## Risks and test signals
The risk is false precision. Passing behavior preserves the corrupted marker, hang type, and alternate title instead of inventing a stack frame.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/61 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/610 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/610

## Purpose
This fixture validates an RCU self-stall hang attributed to `sys_recvmmsg` with alternates for `__x64_sys_recvmmsg` and shorter stall titles.

## Important APIs, types, and functions
Key frames include `rcu_sched_clock_irq`, `hrtimer_interrupt`, `copy_user_generic_unrolled`, `__copy_msghdr_from_user`, `___sys_recvmsg`, `do_recvmmsg`, `__x64_sys_recvmmsg`, `do_syscall_64`, and `entry_SYSCALL_64_after_hwframe`.

## Control flow
The log first dumps the RCU grace-period kthread, then an NMI backtrace for CPU 0, and finally shows the interrupted syscall path copying a user msghdr for recvmmsg.

## State and persistence behavior
The file is immutable parser data. Its meaningful persisted state is the expected primary and alternate titles plus `TYPE: HANG`.

## Dependencies and integration points
It exercises integration between the report parser, RCU stall format handling, interrupt/NMI trace parsing, and syscall-name normalization.

## Risks and test signals
The parser must find the syscall frame despite timer and RCU frames. Passing output is the exact title `INFO: rcu detected stall in sys_recvmmsg`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/610 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/611 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/611

## Purpose
This fixture is a sibling RCU self-stall hang for `sys_sendmmsg`. It verifies that the parser can distinguish sendmmsg from nearby scheduler and migration frames.

## Important APIs, types, and functions
Important symbols include `rcu_sched_clock_irq`, `nmi_trigger_cpumask_backtrace`, `lock_is_held_type`, `rcu_read_lock_sched_held`, `lock_acquire`, `_raw_spin_lock`, `__migration_entry_wait`, and the expected syscall aliases `sys_sendmmsg` and `__x64_sys_sendmmsg`.

## Control flow
An RCU stall on CPU 1 produces an RCU kthread dump and an NMI backtrace. The useful stack descends through lock/migration waiting in the sendmmsg syscall context.

## State and persistence behavior
The file has no runtime state. It persists the expected hang classification and alternate titles for parser regression checks.

## Dependencies and integration points
It targets syzkaller's Linux RCU stall extractor and syscall alias matching.

## Risks and test signals
The risk is taking helper frames such as `lock_acquire` as the report identity. The test signal is the primary title ending in `sys_sendmmsg`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/611 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/612 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/612

## Purpose
This fixture validates an RCU stall hang attributed to `ext4_file_read_iter`. The expected alternate title is `stall in ext4_file_read_iter`.

## Important APIs, types, and functions
The log contains RCU/timer frames and multiple trace fragments, including `lock_acquire`, `copy_user_generic_string`, `preempt_schedule_irq`, `exit_to_user_mode_prepare`, and ext4 read-path attribution through `ext4_file_read_iter`.

## Control flow
The report is assembled from an RCU stall and repeated CPU backtrace sections. The parser must skip generic interrupt, lockdep, unwind, and user-copy frames to keep the filesystem read iterator as the useful site.

## State and persistence behavior
The fixture stores expected metadata and a noisy raw log. No state is updated by the file itself.

## Dependencies and integration points
It integrates RCU hang recognition with ext4/VFS stack parsing and frame-priority heuristics.

## Risks and test signals
The risk is unstable title selection from repeated stacks. The stable signal is `TYPE: HANG` with title `INFO: rcu detected stall in ext4_file_read_iter`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/612 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/613 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/613

## Purpose
This fixture covers a warning in `netlbl_cipsov4_add` that panics because `panic_on_warn` is enabled.

## Important APIs, types, and functions
Relevant symbols include `__alloc_pages`, `alloc_pages`, `kmalloc_order_trace`, `netlbl_cipsov4_add`, `genl_family_rcv_msg_doit`, `genl_rcv_msg`, `netlink_rcv_skb`, `netlink_sendmsg`, `__sys_sendmsg`, `panic`, and `__warn`.

## Control flow
Generic netlink receives a message, enters the NetLabel CIPSOv4 add path, attempts a high-order allocation, warns in page allocation, and then panics.

## State and persistence behavior
The top-level `PANICKED: Y` is persisted as expected parser state. Runtime state in the log is allocation parameters and syscall register state only.

## Dependencies and integration points
The fixture connects generic netlink parsing, network-label subsystem frames, allocator warning formats, and panic-on-warn suffix handling.

## Risks and test signals
The parser must keep the title as `WARNING in netlbl_cipsov4_add` rather than `__alloc_pages`, while also retaining `TYPE: WARNING` and `PANICKED: Y`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/613 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/614 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/614

## Purpose
This long fixture validates a panicking kernel stack overflow in `rtnl_newlink`, with alternate title `stack-overflow in rtnl_newlink`.

## Important APIs, types, and functions
Key frames include `netdev_next_lower_dev_rcu`, `bond_get_lowest_level_rcu`, `bond_get_stats`, `dev_get_stats`, `rtnl_fill_stats`, `rtnl_fill_ifinfo`, `rtmsg_ifinfo_build_skb`, `rtnetlink_event`, `netdev_change_features`, `bond_compute_features`, `bond_netdev_event`, `bond_option_xmit_hash_policy_set`, `bond_changelink`, `__rtnl_newlink`, `rtnl_newlink`, and `netlink_sendmsg`.

## Control flow
A netlink `sendmsg` creates or changes a bonding device through rtnetlink. Bond feature updates recursively notify network-device listeners, repeatedly re-entering feature recomputation until the stack guard page is hit and the kernel panics.

## State and persistence behavior
The fixture stores the panic marker and an intentionally repetitive stack. The persistence concern is parser stability across deep recursion, not mutable program state.

## Dependencies and integration points
It exercises stack-overflow detection, panic recognition, network-device notifier recursion, rtnetlink syscall attribution, and report deduplication for repeated frames.

## Risks and test signals
The risk is selecting the top faulting helper `netdev_next_lower_dev_rcu` instead of the actionable entry point. Passing behavior preserves `BUG: stack guard page was hit in rtnl_newlink` and `PANICKED: Y`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/614 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/615 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/615

## Purpose
This is another panicking `rtnl_newlink` stack-overflow fixture, but the top frame is `arch_stack_walk`, making it a stronger test of frame filtering.

## Important APIs, types, and functions
Important symbols include `arch_stack_walk`, `stack_trace_save`, KASAN stack tracking helpers, `pskb_expand_head`, `netlink_trim`, `netlink_broadcast_filtered`, `nlmsg_notify`, `rtnetlink_event`, `bond_netdev_event`, `bond_compute_features`, `br_add_if`, `do_set_master`, `__rtnl_newlink`, `rtnl_newlink`, and `netlink_sendmsg`.

## Control flow
The log shows bonding and bridge-related feature updates recursing through netdevice notifier chains during a rtnetlink newlink operation. Stack tracing and KASAN allocation tracking appear near the top because the overflow interrupts instrumentation.

## State and persistence behavior
The file persists `PANICKED: Y` and repeated recursive frames. It has no runtime persistence outside the test fixture.

## Dependencies and integration points
It integrates stack-overflow parsing with bridge, bonding, ethtool notification, netlink broadcast, and kernel instrumentation noise.

## Risks and test signals
The parser must not title the crash after `arch_stack_walk` or KASAN helpers. The expected stable signal is `stack-overflow in rtnl_newlink`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/615 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/616 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/616

## Purpose
This fixture validates an arm64 tag-based KASAN invalid read attributed to `ip6_mc_del1_src`.

## Important APIs, types, and functions
Important frames include `__list_add_valid`, `ip6_mc_del1_src`, `firmware_fallback_sysfs`, `_request_firmware`, `request_firmware`, `devlink_compat_flash_update`, `ethtool_flash_device`, `dev_ethtool`, `dev_ioctl`, `sock_ioctl`, and `__arm64_sys_ioctl`.

## Control flow
An ioctl path invokes ethtool flash update, requests firmware, and hits a tag mismatch while list manipulation occurs. The log includes allocation and free stacks for the same kmalloc object.

## State and persistence behavior
The file persists KASAN object lifetime evidence: pointer tag, memory tag, allocation stack, free stack, object cache, and memory state bytes.

## Dependencies and integration points
It exercises syzkaller parsing for arm64 KASAN tag-check faults, firmware fallback, devlink compatibility, ethtool, and IPv6 multicast symbol attribution.

## Risks and test signals
The title should use `KASAN: invalid-access Read in ip6_mc_del1_src` even though the first bad access frame is `__list_add_valid`. `TYPE: KASAN-READ` is the expected type.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/616 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/617 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/617

## Purpose
This fixture covers an early boot denial-of-service style panic: `kernel panic: VFS: Unable to mount root fs on unknown-block(NUM,NUM)`.

## Important APIs, types, and functions
Important frames include `panic`, `mount_block_root`, `mount_root`, and `prepare_namespace`. The metadata sets `TYPE: DoS` and `PANICKED: Y`.

## Control flow
PID 1 reaches root filesystem mounting during namespace preparation and panics because the root block device cannot be resolved.

## State and persistence behavior
The file records boot-time global system state rather than per-process state. There is no recovery path in the fixture; the expected state is a panic.

## Dependencies and integration points
It integrates parser handling for early boot VFS panics where standard task stacks are short and no syzkaller executor is involved.

## Risks and test signals
The parser must normalize numeric block identifiers to `NUM,NUM` and classify the report as `DoS`, not as a generic panic.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/617 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/618 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/618

## Purpose
This is a negative fixture: it has no expected `TITLE` or `TYPE` metadata and contains only benign networking messages plus a deprecation warning for the `mand` mount option.

## Important APIs, types, and functions
There are no kernel crash functions. Log strings include WLAN IBSS setup, IPv6 link readiness, and the warning text `the mand mount option is being deprecated`.

## Control flow
The console output records ordinary device/network state transitions followed by an informational deprecation block.

## State and persistence behavior
The file persists an ignored log sample. Its absence of metadata is itself the parser expectation.

## Dependencies and integration points
It integrates with negative-path tests in the Linux report parser, ensuring harmless deprecation warnings are not surfaced as syzkaller crashes.

## Risks and test signals
The risk is false-positive warning extraction. Passing behavior is no crash report for this file.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/618 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/619 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/619

## Purpose
This negative fixture is similar to report 618 but uses the newer text saying the `mand` mount option has been deprecated and ignored.

## Important APIs, types, and functions
No crash APIs are present. The relevant strings are IPv6 link readiness messages and the multi-line deprecation notice for `mand`.

## Control flow
The log shows network interfaces becoming ready around a mount-option deprecation warning. There is no stack trace, BUG line, panic, or report title.

## State and persistence behavior
It is static ignored console output. The lack of `TITLE` metadata persists the expected no-report state.

## Dependencies and integration points
It verifies parser integration with the warning suppression/ignore list for kernel informational notices.

## Risks and test signals
A parser regression could turn the deprecation block into a fake warning report. The correct test signal is that no report is extracted.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/619 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/62 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/62

## Purpose
This small fixture is another corrupted RCU stall sample. It expects the same hang title and alternate as report 61.

## Important APIs, types, and functions
The only useful raw line is `INFO: rcu_sched self-detected stall on CPU`; no reliable function stack is available.

## Control flow
The parser sees the RCU stall signature without enough stack detail and should produce a corrupted hang classification.

## State and persistence behavior
`CORRUPTED: Y` is the persisted expected state. The raw log is intentionally too short for normal attribution.

## Dependencies and integration points
It exercises duplicate/minimal corrupted hang handling in syzkaller's Linux report tests.

## Risks and test signals
The parser must not infer a random function name. Passing behavior keeps `TITLE: INFO: rcu detected stall in corrupted`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/62 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/621 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/621

## Purpose
This fixture validates a suppressed overlayfs warning in `ovl_create_real`. It also includes noisy userspace segfault and stack-smashing lines before the kernel warning.

## Important APIs, types, and functions
Important frames are `ovl_create_real`, `ovl_workdir_create`, `ovl_make_workdir`, `ovl_get_workdir`, `ovl_fill_super`, `mount_nodev`, `legacy_get_tree`, `vfs_get_tree`, `path_mount`, `__x64_sys_mount`, and `do_syscall_64`.

## Control flow
The log begins with repeated executor userland faults, then an overlayfs mount path warns while creating a real workdir object.

## State and persistence behavior
The expected parser state includes `SUPPRESSED: Y`, meaning the report is recognized but marked suppressed.

## Dependencies and integration points
It connects report parsing with overlayfs mount stacks, userspace-noise filtering, and suppression metadata.

## Risks and test signals
The parser must ignore preamble segfault noise, keep the overlayfs title, and preserve the suppressed flag.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/621 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/622 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/622

## Purpose
This fixture covers a refcount warning in `memfd_secret`, with alternates for syscall wrapper names.

## Important APIs, types, and functions
Key symbols include `refcount_warn_saturate`, `__se_sys_memfd_secret`, `do_syscall_64`, and `entry_SYSCALL_64_after_hwframe`.

## Control flow
A userspace call to the memfd secret syscall triggers `refcount_t: addition on 0; use-after-free`, then emits a standard warning stack.

## State and persistence behavior
The file persists a refcount warning without a panic. The expected aliases account for syscall wrapper variation.

## Dependencies and integration points
It tests the report parser's refcount warning type, syscall wrapper normalization, and memfd-secret naming.

## Risks and test signals
The parser must classify the type as `REFCOUNT_WARNING` and prefer `WARNING: refcount bug in memfd_secret` over the generic refcount helper.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/622 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/623 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/623

## Purpose
This fixture is another memfd secret refcount warning, but its canonical title is `WARNING: refcount bug in sys_memfd_secret`.

## Important APIs, types, and functions
Important frames include `refcount_warn_saturate`, `__x64_sys_memfd_secret`, `do_syscall_64`, and `entry_SYSCALL_64_after_hwframe`.

## Control flow
The syscall path enters the x86-64 wrapper and triggers the same `refcount_t: addition on 0; use-after-free` diagnostic.

## State and persistence behavior
The fixture keeps the wrapper-specific expected title and an alternate for `__x64_sys_memfd_secret`.

## Dependencies and integration points
It complements report 622 and verifies architecture-specific syscall wrapper handling in syzkaller report tests.

## Risks and test signals
The risk is over-normalizing this report to `memfd_secret`. Passing behavior preserves `sys_memfd_secret` as the title target.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/623 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/624 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/624

## Purpose
This fixture validates a dentry lifetime bug during ramfs unmount: `BUG: Dentry still in use in unmount`.

## Important APIs, types, and functions
Key frames are `umount_check`, `d_walk`, `shrink_dcache_for_umount`, `generic_shutdown_super`, `kill_litter_super`, `ramfs_kill_sb`, `deactivate_locked_super`, `cleanup_mnt`, `task_work_run`, and `do_exit`.

## Control flow
A task exits, mount cleanup runs task work, ramfs shutdown walks dentries, and `umount_check` finds `.index` still referenced.

## State and persistence behavior
The raw line persists dentry name, reference count, and filesystem pair `[unmount of ramfs ramfs]`. No file-level mutable state exists.

## Dependencies and integration points
It tests VFS/dcache report parsing and alternate-title extraction containing filesystem-specific unmount context.

## Risks and test signals
The parser must keep the generic title while accepting the ramfs-specific alternate string.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/624 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/625 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/625

## Purpose
This fixture covers the same dentry-still-in-use bug during ext4 loop-device unmount.

## Important APIs, types, and functions
Key frames include `umount_check`, `d_walk`, `shrink_dcache_for_umount`, `generic_shutdown_super`, `kill_block_super`, `deactivate_super`, `cleanup_mnt`, `task_work_run`, and `entry_SYSCALL_64_after_hwframe`.

## Control flow
An unmount syscall completes, task work releases the mount, and ext4 shutdown reaches `umount_check` with a still-referenced `.index` dentry.

## State and persistence behavior
The fixture persists the ext4-specific alternate title `[unmount of ext4 loop4]` and raw dentry identity.

## Dependencies and integration points
It complements report 624 and verifies filesystem-specific alternate extraction for VFS dcache warnings.

## Risks and test signals
The parser should deduplicate on the generic title but preserve the ext4 loop alternate for detail.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/625 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/626 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/626

## Purpose
This fixture validates a panicking KMSAN uninitialized-value report in `prepare_task_switch`.

## Important APIs, types, and functions
Important frames include `prepare_task_switch`, `__schedule`, `__cond_resched`, `__dentry_kill`, `dentry_kill`, plus KMSAN reporting helpers. The metadata expects `TYPE: KMSAN-UNINIT-VALUE` and `PANICKED: Y`.

## Control flow
The scheduler prepares a task switch while a dentry release path is active, KMSAN reports use of uninitialized data, and the kernel panics.

## State and persistence behavior
The fixture persists sanitizer state, origin context, and panic classification. It has no mutable fixture state.

## Dependencies and integration points
It exercises KMSAN title extraction, scheduler frame selection, and panic suffix parsing.

## Risks and test signals
The parser must choose `prepare_task_switch` over surrounding VFS cleanup frames and keep the KMSAN type.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/626 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/627 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/627

## Purpose
This fixture covers a panicking KASAN slab-out-of-bounds read attributed to `ext4_group_desc_csum`.

## Important APIs, types, and functions
Key symbols include `crc16`, `ext4_group_desc_csum`, ext4 metadata validation paths, KASAN allocation evidence, and `panic_on_warn`.

## Control flow
An ext4 operation computes or verifies a group descriptor checksum, `crc16` reads beyond a slab object, KASAN reports the invalid access, and panic-on-warn converts it into a panic.

## State and persistence behavior
The file stores KASAN object bounds, allocation stack, memory state, and `PANICKED: Y`.

## Dependencies and integration points
It integrates KASAN slab-out-of-bounds parsing with ext4 filesystem symbol attribution and panic handling.

## Risks and test signals
The parser must not title the report as `crc16`; the expected title is `KASAN: slab-out-of-bounds Read in ext4_group_desc_csum`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/627 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/628 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/628

## Purpose
This fixture validates an `ATOMIC_SLEEP` report where `console_lock` is called with interrupts disabled and TTY locks held.

## Important APIs, types, and functions
Important frames include `__might_resched`, `console_lock`, `do_con_write`, `con_write`, `n_hdlc_send_frames`, `tty_wakeup`, `__start_tty`, `n_tty_ioctl_helper`, `n_hdlc_tty_ioctl`, `tty_ioctl`, and `__x64_sys_ioctl`.

## Control flow
An ioctl on a TTY enters HDLC line-discipline handling, wakes the TTY, sends frames, attempts console output, and reaches a sleeping console lock in atomic context.

## State and persistence behavior
The log persists lock state, IRQ state, preempt count, and syscall registers. The fixture itself is immutable.

## Dependencies and integration points
It tests atomic-sleep parsing for TTY/console paths and held-lock context.

## Risks and test signals
The parser must preserve `console_lock` as the title frame and classify the report as `ATOMIC_SLEEP`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/628 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/629 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/629

## Purpose
This fixture covers a non-panicking stack guard hit in `rtnl_newlink` on a 5.16 kernel.

## Important APIs, types, and functions
Important frames include `mark_lock`, `__lock_acquire`, `psi_group_change`, `psi_task_switch`, `__schedule`, `ethnl_default_notify`, `ethtool_notify`, `ethnl_netdev_event`, `__netdev_update_features`, `bond_compute_features`, `bond_netdev_event`, and rtnetlink newlink handling.

## Control flow
Network-device feature updates recursively notify bonding and ethtool listeners. A timer interrupt and scheduler/lockdep path appear near the guard-page hit, but the deeper source is rtnetlink newlink recursion.

## State and persistence behavior
The file persists a long recursive trace and expected alternate title. It lacks `PANICKED: Y`, distinguishing it from reports 614 and 615.

## Dependencies and integration points
It integrates stack-overflow parsing with lockdep, PSI, ethtool netlink notifications, and bonding notifier recursion.

## Risks and test signals
The risk is titling the report as `mark_lock` or scheduler code. Passing behavior identifies `BUG: stack guard page was hit in rtnl_newlink`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/629 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/63 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/63

## Purpose
This is a third minimal corrupted RCU stall fixture.

## Important APIs, types, and functions
The raw signal is `INFO: rcu_sched self-detected stall on CPU`; the expected parser metadata supplies the title, alternate, hang type, and corruption flag.

## Control flow
The report contains no trustworthy stack. The parser should recognize the RCU stall class and stop at `corrupted` attribution.

## State and persistence behavior
`CORRUPTED: Y` is the key persisted state. The fixture intentionally preserves insufficient crash context.

## Dependencies and integration points
It provides another regression sample for minimal RCU stall handling.

## Risks and test signals
False frame extraction is the main risk. The correct result is the exact corrupted hang title.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/63 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/630 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/630

## Purpose
This fixture validates a stack guard hit attributed to `tls_setsockopt`.

## Important APIs, types, and functions
Key symbols include `__sanitizer_cov_trace_const_cmp4`, TLS setsockopt paths, stack-unwind frames, and syscall/socket option handling. The expected alternate is `stack-overflow in tls_setsockopt`.

## Control flow
The log shows at least two guard-page hits while a TLS socket option path recurses or overuses stack. Instrumentation and coverage frames appear at the top, so the parser must recover the semantic entry point.

## State and persistence behavior
The fixture persists guard-page addresses, task metadata, register state, and expected title metadata.

## Dependencies and integration points
It tests stack-overflow parsing in networking TLS code and filtering of sanitizer coverage frames.

## Risks and test signals
The parser must not title the crash as a sanitizer coverage helper. The expected title is `BUG: stack guard page was hit in tls_setsockopt`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/630 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/631 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/631

## Purpose
This fixture covers a memory-safety bug titled `BUG: unable to handle kernel paging request in __unwind_start`.

## Important APIs, types, and functions
Important frames include `__read_once_word_nocheck`, `__unwind_start`, stack unwinding code, and syscall return frames. The expected type is `MEMORY_SAFETY_BUG`.

## Control flow
A page fault occurs while the kernel is reading stack words for unwinding. The raw faulting instruction is a low-level read helper, but the useful subsystem frame is `__unwind_start`.

## State and persistence behavior
The fixture persists fault address, page-fault diagnostic data, registers, and expected metadata.

## Dependencies and integration points
It exercises page-fault report parsing and frame selection in the kernel unwinder.

## Risks and test signals
The parser must normalize the report to `bad-access in __unwind_start` as an alternate and classify it as memory safety.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/631 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/632 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/632

## Purpose
This fixture validates a corrupted KMSAN uninitialized-value report in `__perf_event_task_sched_in`.

## Important APIs, types, and functions
Key symbols include `__perf_event_task_sched_in`, `stack_depot_fetch`, `kmsan_print_origin`, `kmsan_report`, and `__msan_warning`.

## Control flow
During scheduler/perf event task switch handling, KMSAN detects uninitialized data. Origin reporting itself warns because stack depot data is out of bounds, so the fixture is marked corrupted.

## State and persistence behavior
The persisted state includes `CORRUPTED: Y`, KMSAN type, warning side-effect, and partial origin data.

## Dependencies and integration points
It tests KMSAN parsing, perf/scheduler attribution, and corruption handling when sanitizer origin metadata is damaged.

## Risks and test signals
The parser must preserve the KMSAN title while acknowledging corruption, rather than switching to `stack_depot_fetch`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/632 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/633 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/633

## Purpose
This fixture covers a corrupted KMSAN uninitialized-value report in `prepend_path`.

## Important APIs, types, and functions
Important frames include `prepend_path`, `d_absolute_path`, `tomoyo_realpath_from_path`, `tomoyo_path_number_perm`, `tomoyo_path_mknod`, `security_path_mknod`, `path_openat`, `do_filp_open`, and `__x64_sys_open`.

## Control flow
A path creation/open operation passes through TOMOYO security hooks, path rendering calls `prepend_path`, and KMSAN reports uninitialized data. Stack depot origin lookup also warns, marking the report corrupted.

## State and persistence behavior
The fixture stores both the KMSAN diagnostic and secondary stack-depot warning. `CORRUPTED: Y` is expected persisted metadata.

## Dependencies and integration points
It integrates KMSAN parsing with VFS path generation and LSM/TOMOYO call stacks.

## Risks and test signals
The parser must attribute the bug to `prepend_path` and retain KMSAN type despite the secondary warning.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/633 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/634 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/634

## Purpose
This fixture validates a KMSAN kernel info leak reported in `urandom_read_nowarn`.

## Important APIs, types, and functions
Important frames include `_copy_to_user`, `urandom_read_nowarn`, `__x64_sys_getrandom`, `chacha_permute`, `chacha_block_generic`, `_extract_crng`, `_get_random_bytes`, `get_random_bytes`, `nsim_dev_trap_report_work`, and worker-thread frames.

## Control flow
Uninitialized bytes originate in CRNG/chacha reseed and extraction paths, then are copied to userspace by `getrandom` through `urandom_read_nowarn`.

## State and persistence behavior
The fixture persists origin stacks, byte count, kernel address, and user destination address for the info leak.

## Dependencies and integration points
It tests KMSAN info-leak parsing, random-number generator stacks, and copy-to-user sink handling.

## Risks and test signals
The parser must use `urandom_read_nowarn` rather than `_copy_to_user` as the title frame and classify the type as `KMSAN-INFO-LEAK`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/634 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/635 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/635

## Purpose
This fixture covers a KMSAN uninitialized-value report in `sctp_epaddr_lookup_transport`.

## Important APIs, types, and functions
Key frames include `sctp_epaddr_lookup_transport`, `sctp_endpoint_bh_rcv`, `sctp_inq_push`, `sctp_rcv`, `sctp4_rcv`, `ip_protocol_deliver_rcu`, `ip_local_deliver`, `ip_rcv`, `__netif_receive_skb`, `process_backlog`, and `net_rx_action`.

## Control flow
An SCTP packet is processed in softirq context; address initialization leaves a local `src` value uninitialized, and lookup later consumes it.

## State and persistence behavior
The log persists origin storage in `sctp_init_addrs`, local variable metadata, CPU/task context, and KMSAN type.

## Dependencies and integration points
It integrates network softirq stack parsing, SCTP protocol handling, and KMSAN origin extraction.

## Risks and test signals
The parser must classify this as `KMSAN-UNINIT-VALUE` and title it after `sctp_epaddr_lookup_transport`, not generic IP receive helpers.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/635 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/636 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/636

## Purpose
This fixture validates a KMSAN uninitialized-value report in `ppp_send_frame`.

## Important APIs, types, and functions
Important frames include `ppp_send_frame`, `__ppp_xmit_process`, `ppp_xmit_process`, `ppp_write`, `do_iter_write`, `do_writev`, `__x64_sys_writev`, `__alloc_skb`, and `__kmalloc_node_track_caller`.

## Control flow
A userspace `writev` to PPP allocates an skb in `ppp_write`, then transmit processing consumes uninitialized data in `ppp_send_frame`.

## State and persistence behavior
The fixture persists KMSAN creation stack for the skb allocation and the consuming transmit stack.

## Dependencies and integration points
It tests KMSAN parsing across character-device write paths, skb allocation, and PPP network transmit logic.

## Risks and test signals
The parser must use `ppp_send_frame` as the bug site and keep the `KMSAN-UNINIT-VALUE` type.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/636 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/637 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/637

## Purpose
This fixture validates a KMSAN USB info leak in `hif_usb_send`, with alternate origin `htc_connect_service`.

## Important APIs, types, and functions
Key frames include `usb_submit_urb`, `hif_usb_send`, `htc_connect_service`, worker context, and KMSAN origin-reporting helpers.

## Control flow
A USB send path submits an URB containing uninitialized data. The origin traces back to HTC service connection setup.

## State and persistence behavior
The fixture persists info-leak metadata, USB submission context, and an alternate origin-based title.

## Dependencies and integration points
It integrates KMSAN info-leak parsing with USB networking/ath9k-style HIF and HTC service stacks.

## Risks and test signals
The parser must title the sink as `hif_usb_send` while retaining the origin alternate. `TYPE: KMSAN-INFO-LEAK` is the oracle.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/637 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/638 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/638

## Purpose
This fixture covers a KASAN use-after-free write attributed to `put_ucounts`.

## Important APIs, types, and functions
Important frames include `_atomic_dec_and_lock_irqsave`, `put_ucounts`, KASAN reporting helpers, allocation stack for the object, and free stack from another task.

## Control flow
A syzkaller executor uses an object after another task has freed it; atomic reference-count teardown attempts to write through freed memory in the ucounts path.

## State and persistence behavior
The raw log persists allocation and free stacks, task identities, object bounds, and the write classification.

## Dependencies and integration points
It tests KASAN use-after-free parsing, refcount/ucounts symbol selection, and cross-task lifetime evidence.

## Risks and test signals
The parser must not title the report as `_atomic_dec_and_lock_irqsave`; the expected semantic title is `put_ucounts` with type `KASAN-USE-AFTER-FREE-WRITE`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/638 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/639 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/639

## Purpose
This fixture validates a panic-on-warning report in `free_netdev` caused by reference tracker cleanup.

## Important APIs, types, and functions
Key frames include `ref_tracker_dir_exit`, `free_netdev`, `netdev_run_todo`, `default_device_exit_batch`, `ops_exit_list`, `cleanup_net`, `process_one_work`, `worker_thread`, `panic`, and `__warn`.

## Control flow
Network namespace cleanup runs in a workqueue, releases network devices, and reference-tracker exit detects leaked or inconsistent references, causing a warning and panic.

## State and persistence behavior
The file persists workqueue context, network namespace cleanup stack, and `PANICKED: Y`.

## Dependencies and integration points
It tests warning parsing for ref-tracker diagnostics during netdev teardown and panic-on-warn handling.

## Risks and test signals
The parser must choose `free_netdev` as the warning site and retain the panic marker.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/639 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/64 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/64

## Purpose
This minimal fixture covers a corrupted lockdep/spinlock lockup report.

## Important APIs, types, and functions
The raw signal is `BUG: spinlock lockup suspected on CPU#2, syz-executor/12636`. Expected metadata sets `TYPE: LOCKDEP` and `CORRUPTED: Y`.

## Control flow
There is not enough stack information to name a reliable lock holder or caller, so the title is intentionally `in corrupted`.

## State and persistence behavior
The persisted state is the corrupted lockdep classification. The fixture has no mutable behavior.

## Dependencies and integration points
It verifies syzkaller's lockdep recognizer for incomplete spinlock lockup reports.

## Risks and test signals
The parser must not infer a missing frame. Passing behavior preserves `BUG: spinlock lockup suspected in corrupted`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/64 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/640 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/640

## Purpose
This fixture validates a warning in `packet_release` from reference tracker free logic.

## Important APIs, types, and functions
Important frames include `ref_tracker_free`, `packet_release`, `__sock_release`, `sock_close`, `__fput`, `task_work_run`, `do_exit`, `do_group_exit`, and `__x64_sys_exit_group`.

## Control flow
Process exit closes a packet socket, file release runs socket release, and packet socket cleanup warns in ref-tracker code.

## State and persistence behavior
The fixture persists task-exit context, socket release stack, and warning metadata. It does not include panic metadata.

## Dependencies and integration points
It integrates AF_PACKET socket teardown with Linux warning parsing and ref-tracker diagnostics.

## Risks and test signals
The parser should title the report `WARNING in packet_release`, not `ref_tracker_free`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/640 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/641 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/641

## Purpose
This fixture covers a non-panicking scheduling-while-atomic report in `simple_recursive_removal` on arm64.

## Important APIs, types, and functions
Key frames include `__schedule_bug`, `__schedule`, `schedule`, `rwsem_down_write_slowpath`, `down_write`, `simple_recursive_removal`, `debugfs_remove`, `blk_release_queue`, `kobject_put`, `blk_put_queue`, `blkg_free`, `__blkg_release`, and `rcu_core`.

## Control flow
RCU softirq cleanup releases a block cgroup/queue, removes debugfs entries, attempts a sleeping rwsem write lock, and triggers scheduling-while-atomic.

## State and persistence behavior
The log persists preemption/atomic state, architecture call trace, and scheduler diagnostic lines.

## Dependencies and integration points
It tests atomic-sleep parsing for scheduling-while-atomic messages on arm64 block/debugfs cleanup paths.

## Risks and test signals
The parser must identify `simple_recursive_removal` as the actionable frame and classify `TYPE: ATOMIC_SLEEP`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/641 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/642 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/642

## Purpose
This fixture validates a panicking scheduling-while-atomic report in `exit_to_user_mode_prepare`.

## Important APIs, types, and functions
Important frames include `kernel_fpu_begin_mask` as the preemption-disabled site, `panic`, `__schedule_bug`, `__schedule`, `schedule`, `exit_to_user_mode_prepare`, `syscall_exit_to_user_mode`, and `do_syscall_64`.

## Control flow
A syscall returns toward user mode while preemption remains disabled from FPU handling. The scheduler detects atomic sleep and panic-on-bug behavior reboots the kernel.

## State and persistence behavior
The fixture persists preemption-disabled metadata, no-locks-held state, syscall register data, and `PANICKED: Y`.

## Dependencies and integration points
It tests atomic-sleep parsing for syscall-exit paths and panic marker extraction.

## Risks and test signals
The parser must use `exit_to_user_mode_prepare` rather than `kernel_fpu_begin_mask` as the title frame.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/642 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/643 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/643

## Purpose
This fixture is a panicking ARM scheduling-while-atomic report in `simple_recursive_removal`.

## Important APIs, types, and functions
Important symbols include `__do_softirq`, `panic`, `__schedule_bug`, `__schedule`, `schedule`, `rwsem_down_write_slowpath`, `down_write`, `simple_recursive_removal`, `debugfs_remove`, `blk_release_queue`, `kobject_put`, `blk_put_queue`, `__blkg_release`, and `rcu_core`.

## Control flow
Softirq/RCU cleanup releases block queue state and removes debugfs files, taking a sleeping rwsem while atomic. The kernel panics and also dumps another CPU stopping.

## State and persistence behavior
The file persists ARM backtrace format, panic state, and softirq preemption context.

## Dependencies and integration points
It verifies architecture-specific parsing for ARM backtraces and atomic-sleep panic reports.

## Risks and test signals
The parser must keep the same semantic title as report 641 while also preserving `PANICKED: Y`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/643 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/644 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/644

## Purpose
This fixture is another non-panicking scheduling-while-atomic report in `simple_recursive_removal`.

## Important APIs, types, and functions
The same block/debugfs/RCU stack family appears: `simple_recursive_removal`, `debugfs_remove`, `blk_release_queue`, `kobject_put`, `blk_put_queue`, `blkg_free`, `__blkg_release`, and `rcu_core`.

## Control flow
An atomic context cleanup path attempts recursive debugfs removal and blocks on a write semaphore, producing the scheduling-while-atomic diagnostic.

## State and persistence behavior
The persisted test data is the expected title/type plus raw stack evidence. There is no panic marker.

## Dependencies and integration points
It broadens coverage for repeated atomic-sleep reports around block queue release and simple filesystem removal helpers.

## Risks and test signals
The parser must treat it as `TYPE: ATOMIC_SLEEP` and avoid overfitting to architecture-specific details.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/644 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/645 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/645

## Purpose
This fixture is another panicking `exit_to_user_mode_prepare` scheduling-while-atomic sample.

## Important APIs, types, and functions
Key frames are `kernel_fpu_begin_mask`, `panic`, `__schedule_bug`, `__schedule`, `schedule`, `exit_to_user_mode_prepare`, `syscall_exit_to_user_mode`, `do_syscall_64`, and syscall return assembly.

## Control flow
The report follows syscall exit while atomic scheduling is detected, with the preemption-disabled site pointing to kernel FPU state setup.

## State and persistence behavior
The file persists panic classification, preemption-disabled metadata, and syscall register state.

## Dependencies and integration points
It provides duplicate coverage for syscall-exit atomic-sleep parser behavior and panic-on-scheduling-bug recognition.

## Risks and test signals
The expected title must remain `BUG: scheduling while atomic in exit_to_user_mode_prepare` with `PANICKED: Y`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/645 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/646 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/646

## Purpose
This fixture validates a KASAN use-after-free read attributed to `tty_release`.

## Important APIs, types, and functions
Important frames include `__wake_up_common`, `tty_release`, KASAN report helpers, allocation stack from a syzkaller task, and free stack from a worker or async task.

## Control flow
TTY release uses a wait queue or related object after it has been freed. The top access helper is wakeup code, but the owning lifecycle path is `tty_release`.

## State and persistence behavior
The raw log persists allocation/free evidence, task IDs, memory state, and read classification.

## Dependencies and integration points
It tests KASAN use-after-free read parsing in TTY teardown and wakeup paths.

## Risks and test signals
The parser must pick `tty_release` over `__wake_up_common` and classify `TYPE: KASAN-USE-AFTER-FREE-READ`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/646 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/647 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/647

## Purpose
This is a negative/no-report fixture containing CPU vulnerability mitigation boot messages.

## Important APIs, types, and functions
There are no crash functions. The relevant strings mention Spectre V1, Spectre V2, Enhanced IBRS, RSB filling, conditional IBPB, and Speculative Store Bypass mitigation.

## Control flow
The log is early boot mitigation reporting from CPU/security initialization. It contains a line with `WARNING` in prose but no kernel warning stack.

## State and persistence behavior
The absence of metadata persists the expected parser result: no report should be produced.

## Dependencies and integration points
It tests false-positive suppression for boot-time security warning text.

## Risks and test signals
The parser must not treat `Spectre V2 : WARNING` as a crash. Correct behavior is no extracted report.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/647 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/648 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/648

## Purpose
This fixture validates lockdep parsing for `possible deadlock in tick_handler`.

## Important APIs, types, and functions
Important signals include `WARNING: possible circular locking dependency detected`, interrupt/tick handler context, lock dependency chains, and the expected `TYPE: LOCKDEP`.

## Control flow
The kernel emits a lockdep circular-dependency warning while handling timer tick activity. The parser should extract the canonical deadlock title from the lockdep report.

## State and persistence behavior
The fixture persists lock graph evidence and stack context only as static test data. No mutable state is modified.

## Dependencies and integration points
It exercises syzkaller's lockdep/deadlock recognizer, especially titles beginning `possible deadlock in ...`.

## Risks and test signals
The parser must classify the report as lockdep and keep `tick_handler` as the reported site rather than generic lockdep helpers.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/648 -->
