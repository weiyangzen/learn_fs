# subset-b-009322 research

Grouped research for strace's bundled Linux UAPI headers under `sources/test-tools/strace/bundled/linux/include/uapi/linux`. Each section preserves the original source path and is delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/nsfs.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/nsfs.h

## Purpose

Defines the userspace ABI for namespace filesystem file descriptors and namespace identifiers. strace consumes these ioctl numbers, fixed inode/id constants, request structs, and namespace type masks to decode nsfs operations such as `NS_GET_USERNS`, `NS_GET_PARENT`, mount namespace iteration, pid translation between pid namespaces, and namespace identity queries.

## Important APIs, Types, and Dependencies

The header depends on `linux/ioctl.h` for `_IO`/`_IOR` encodings and `linux/types.h` for fixed-width ABI types. Important exports include `NSIO`, `NS_GET_USERNS`, `NS_GET_PARENT`, `NS_GET_NSTYPE`, `NS_GET_OWNER_UID`, `NS_GET_PID_FROM_PIDNS`, `NS_GET_TGID_FROM_PIDNS`, `NS_GET_PID_IN_PIDNS`, `NS_GET_TGID_IN_PIDNS`, `NS_GET_MNTNS_ID`, `NS_GET_ID`, and the mount namespace ioctls `NS_MNT_GET_INFO`, `NS_MNT_GET_NEXT`, and `NS_MNT_GET_PREV`. `struct mnt_ns_info`, `struct nsfs_file_handle`, and `struct ns_id_req` are explicitly versioned by size macros. `enum init_ns_ino`, `enum init_ns_id`, and `enum ns_type` expose stable namespace identity constants.

## Control Flow, State, and Integration

There is no executable control flow. The ABI describes request/response layout for kernel ioctl handlers on namespace file descriptors and for newer namespace listing/stat APIs. State is external kernel namespace state: namespace ids, inodes, owning user namespace ids, mount counts, and pid translations. The strace integration point is decoding ioctl command numbers and nested fields without interpreting them as process-local state.

## Risks and Test Signals

Risks are ABI-size drift, confusing namespace inode constants with namespace ids, and treating `enum ns_type` as arbitrary bit flags rather than clone-style namespace type values. Test signals include strace decoding every nsfs ioctl name, printing `struct mnt_ns_info` and `struct ns_id_req` fields with correct widths, and preserving unknown future structure tail bytes by honoring the `size` field.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/nsfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/openat2.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/openat2.h

## Purpose

Defines the `openat2(2)` argument ABI. strace uses it to decode the `struct open_how` payload and the `RESOLVE_*` path-resolution constraints that distinguish `openat2` from older `openat` behavior.

## Important APIs, Types, and Dependencies

The only dependency is `linux/types.h`. `struct open_how` contains `flags`, `mode`, and `resolve`, all `__u64` for extensible syscall ABI stability. The exported resolve bits are `RESOLVE_NO_XDEV`, `RESOLVE_NO_MAGICLINKS`, `RESOLVE_NO_SYMLINKS`, `RESOLVE_BENEATH`, `RESOLVE_IN_ROOT`, and `RESOLVE_CACHED`.

## Control Flow, State, and Integration

The header has no runtime control flow. Its values are consumed by the kernel during pathname lookup and by strace when formatting the third syscall argument. Kernel state affected by callers is the opened file descriptor and path walk result; the header itself only specifies validation rules such as rejecting unknown `flags` bits and requiring `mode` to be zero unless creation flags are set.

## Risks and Test Signals

Risks include silently accepting unknown flag bits in user decoders, confusing `RESOLVE_BENEATH` with `RESOLVE_IN_ROOT`, and missing `RESOLVE_CACHED` retry behavior where `-EAGAIN` is a valid outcome. Test signals are syscall decode tests that show all `open_how` fields, named resolve flags, unknown-bit fallback, and correct handling of short or future-extended struct sizes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/openat2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/packet_diag.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/packet_diag.h

## Purpose

Defines netlink diagnostic ABI structures for packet sockets. strace uses this to decode `SOCK_DIAG_BY_FAMILY` requests for `AF_PACKET` sockets and their optional multicast list, ring, fanout, memory, and filter attributes.

## Important APIs, Types, and Dependencies

The header depends on `linux/types.h`. `struct packet_diag_req` carries family, protocol, inode, show-mask, and cookie filters. `PACKET_SHOW_INFO`, `PACKET_SHOW_MCLIST`, `PACKET_SHOW_RING_CFG`, `PACKET_SHOW_FANOUT`, `PACKET_SHOW_MEMINFO`, and `PACKET_SHOW_FILTER` select response details. `struct packet_diag_msg` is the base response. Attribute ids are `PACKET_DIAG_INFO`, `PACKET_DIAG_MCLIST`, `PACKET_DIAG_RX_RING`, `PACKET_DIAG_TX_RING`, `PACKET_DIAG_FANOUT`, `PACKET_DIAG_UID`, `PACKET_DIAG_MEMINFO`, and `PACKET_DIAG_FILTER`. Payload structs include `packet_diag_info`, `packet_diag_mclist`, and `packet_diag_ring`.

## Control Flow, State, and Integration

No functions are defined. The control pattern is netlink request selection followed by a kernel diagnostic dump of packet socket state. Persistent state belongs to live packet sockets: ring sizing, membership addresses, fanout group, socket flags, UID, and filters.

## Risks and Test Signals

Risks are attribute-number drift, incorrectly sizing the fixed 32-byte hardware address array, and treating diagnostic output as portable across kernel versions without checking requested show bits. Test signals include netlink decoder coverage for every `PACKET_SHOW_*` flag, ring field formatting, `PDI_*` flags, and graceful display of missing optional attributes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/packet_diag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/perf_event.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/perf_event.h

## Purpose

Defines the public ABI for `perf_event_open(2)`, perf event file descriptor ioctls, mmap metadata pages, perf ring-buffer records, sampling format flags, branch records, and data-source encodings. In strace this header is the basis for decoding `perf_event_attr`, `PERF_EVENT_IOC_*`, and perf-related flags passed through syscalls and ioctls.

## Important APIs, Types, and Dependencies

Dependencies are `linux/types.h`, `linux/ioctl.h`, and `asm/byteorder.h`. The large exported surface includes event families (`perf_type_id`), hardware/software/cache event ids, `perf_event_sample_format`, branch sampling flags and branch classifications, register ABI ids, transaction bits, `perf_event_read_format`, and the versioned `PERF_ATTR_SIZE_VER*` constants. `struct perf_event_attr` is the primary syscall input and contains type/config selectors, sampling period/frequency unions, sample/read format masks, many one-bit behavior flags, breakpoint/probe/config extension unions, register masks, AUX options, signal data, and newer `config3`/`config4` extensions. `struct perf_event_query_bpf` and `PERF_EVENT_IOC_ENABLE`, `DISABLE`, `REFRESH`, `RESET`, `PERIOD`, `SET_OUTPUT`, `SET_FILTER`, `ID`, `SET_BPF`, `PAUSE_OUTPUT`, `QUERY_BPF`, and `MODIFY_ATTRIBUTES` define fd ioctl interactions. `struct perf_event_mmap_page` defines seqlock-protected counter/time metadata plus data and AUX ring offsets. Record ABI exports include `struct perf_event_header`, namespace link info, `enum perf_event_type` through `PERF_RECORD_CALLCHAIN_DEFERRED`, ksymbol and BPF event types, callchain context markers, AUX flags, syscall flags `PERF_FLAG_FD_*`, `union perf_mem_data_src`, memory hierarchy macros, `struct perf_branch_entry`, and `union perf_sample_weight`.

## Control Flow, State, and Integration

The header is declarative, but it documents several ABI control flows: opening an event with `perf_event_attr`, controlling it through fd ioctls, reading counts through `read()` according to `read_format`, mapping a metadata page and ring buffer, using seqlock loops for self-monitoring reads, and parsing variable-length records according to `perf_event_header.size` and selected sample bits. Persistent state lives in kernel perf events, attached BPF programs, mmap data/AUX rings, group relationships, and per-task/per-cpu counters.

## Risks and Test Signals

Risks are high because the ABI is densely versioned and bitfield-heavy. Decoders must honor `attr.size`, endian-specific bitfield layouts, reusable `PERF_RECORD_MISC_*` bits whose meaning depends on record type, variable payload order under `sample_type`, and ring-buffer memory barriers described by the header. Test signals include strace coverage for `perf_event_open` with old and new attr sizes, every known `PERF_EVENT_IOC_*`, grouped read formats, `PERF_FLAG_FD_CLOEXEC`, BPF query payloads, and unknown future record/sample bits printed without corrupting following fields.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/perf_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/pidfd.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/pidfd.h

## Purpose

Defines pidfd-related flags, information structures, and pidfs ioctl numbers. strace uses these constants to decode `pidfd_open`, `pidfd_send_signal`, and pidfd namespace/info ioctls.

## Important APIs, Types, and Dependencies

The header includes `linux/types.h`, `linux/fcntl.h`, and `linux/ioctl.h`. `PIDFD_NONBLOCK` and `PIDFD_THREAD` alias file-open flags; kernel-only aliases expose stale/autokill internal flags. Signal targeting flags are `PIDFD_SIGNAL_THREAD`, `PIDFD_SIGNAL_THREAD_GROUP`, and `PIDFD_SIGNAL_PROCESS_GROUP`. `struct pidfd_info` is versioned by `PIDFD_INFO_SIZE_VER0` through `VER3` and includes a request/result `mask`, cgroup id, pid/tgid/ppid, real/effective/saved/fs credentials, exit code, coredump fields, and supported-mask reporting. `PIDFD_INFO_*` and `PIDFD_COREDUMP_*` bits describe optional sections. `PIDFS_IOCTL_MAGIC` defines namespace getter ioctls and `PIDFD_GET_INFO`.

## Control Flow, State, and Integration

Runtime flow is fd-centered: userspace obtains a pidfd, sends signals or ioctls to query the referenced process, and the kernel snapshots current process metadata. State is intentionally race-prone after return because the target may exit immediately; correctness depends on pidfd identity at the moment the ioctl was serviced.

## Risks and Test Signals

Risks include assuming returned process metadata remains live, reading optional fields without verifying `mask`, using the wrong version size, and conflating thread pidfds with process-group operations. Test signals are decoder coverage for namespace getter ioctl names, `PIDFD_GET_INFO` in/out masks, coredump subfields, and pidfd signal flags.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/pidfd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/pkt_sched.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/pkt_sched.h

## Purpose

Defines the userspace ABI for Linux traffic-control queue disciplines and scheduler-specific netlink attributes. strace relies on these constants and structs to decode `RTM_NEWQDISC`, `RTM_NEWTCLASS`, `RTM_NEWTFILTER`, qdisc option blobs, and nested `TCA_*` attributes.

## Important APIs, Types, and Dependencies

The header depends on `linux/const.h` and `linux/types.h`. It exports generic priority constants, `struct tc_stats`, `struct tc_estimator`, traffic-control handle macros (`TC_H_MAJ`, `TC_H_MIN`, `TC_H_MAKE`, `TC_H_ROOT`, `TC_H_INGRESS`), link-layer/rate/size specs, and a long catalog of qdisc option structs and attribute enums. Covered qdiscs include FIFO, SKBPRIO, PRIO, MULTIQ, PLUG, TBF, SFQ, RED/GRED/CHOKE, HTB, HFSC, NETEM, DRR, MQPRIO, SFB, QFQ, CODEL, FQ_CODEL, FQ, HHF, PIE, FQ_PIE, CBS, ETF, CAKE, TAPRIO, ETS, and DUALPI2. Each family has one or more `struct tc_*_qopt`/`xstats` definitions plus `TCA_*_MAX` enum bounds.

## Control Flow, State, and Integration

The header is not executable; the operational flow is netlink message construction where `tcmsg` from rtnetlink carries a qdisc/class target and this header describes family-specific attribute payloads. Persistent state is kernel qdisc configuration and counters attached to network devices, classes, and offload-capable hardware.

## Risks and Test Signals

Risks are nested-attribute misdecoding, endian/width mistakes in rate and time fields, qdisc-specific structs changing while older tools still see raw blobs, and interpreting handle major/minor fields as stable semantic ids. Test signals include strace or netlink tests for each `TCA_*_MAX` family, handle macro display, `tc_stats` formatting, TAPRIO schedule entries, CAKE tin statistics, and unknown qdisc attributes preserved as raw netlink data.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/pkt_sched.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/prctl.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/prctl.h

## Purpose

Defines command numbers and subflags for `prctl(2)`, covering process lifecycle, credentials, memory layout, security hardening, architecture-specific controls, and newer runtime knobs. strace uses it to name the first argument and decode command-specific remaining arguments.

## Important APIs, Types, and Dependencies

The header depends on `linux/types.h`. It exports classic commands for parent-death signals, dumpability, unaligned/FPU/endian controls, keepcaps, seccomp, capability bounding set, TSC, securebits, timerslack, perf enable/disable, memory corruption kill mode, `PR_SET_MM`, ptracer, child subreaper, no-new-privs, TID address, THP disable, ambient capabilities, SVE/SME vector length, speculation controls, pointer authentication, tagged address/MTE/RISC-V pointer masking, syscall user dispatch, core scheduling, MDWE, named anonymous VMAs, auxv fetch, memory merge, RISC-V vector and icache controls, PowerPC DEXCR, shadow-stack controls, timer restore ids, futex hash, rseq slice extension, and CFI controls. `struct prctl_mm_map` provides the complex `PR_SET_MM_MAP` payload.

## Control Flow, State, and Integration

There is no local code flow. Each constant selects a kernel operation on the current task, process, mm, credentials, architecture state, or security policy. Some settings persist across exec or can be locked; others are process-local, thread-local, or architecture-specific.

## Risks and Test Signals

Risks are command-specific argument interpretation, unsigned long flag width on 32-bit userspace, reserved command numbers that remain nonfunctional, and decode ambiguity for architecture-only controls. Test signals are syscall decoding tests for each command family, `struct prctl_mm_map` field output, named flag sets for speculation, SVE/SME, MTE, shadow-stack, rseq slice, and CFI, plus unknown command fallback.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/prctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/ptp_clock.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/ptp_clock.h

## Purpose

Defines the character-device ioctl ABI for Precision Time Protocol hardware clocks. strace uses it to decode `PTP_*` ioctl commands, timestamp request structures, pin configuration, and external timestamp events.

## Important APIs, Types, and Dependencies

The header depends on `linux/ioctl.h` and `linux/types.h`. It exports feature and validation flags for external timestamp and periodic output requests, `struct ptp_clock_time`, `ptp_clock_caps`, `ptp_extts_request`, `ptp_perout_request`, `ptp_sys_offset`, `ptp_sys_offset_extended`, `ptp_sys_offset_precise`, `enum ptp_pin_function`, `ptp_pin_desc`, and `ptp_extts_event`. Ioctls are encoded under `PTP_CLK_MAGIC`, including original and `*2` variants for caps, external timestamp, per-out, PPS, system offset, pin get/set, precise/extended offsets, mask operations, and cycle-based offset ioctls.

## Control Flow, State, and Integration

Runtime flow is device-fd ioctl based. Userspace queries clock capabilities, configures external timestamp or periodic output channels, requests cross timestamp samples, configures pins, and reads timestamp events. State persists in the kernel PTP clock device: enabled channels, pin function mappings, PPS state, masks, and hardware clock capabilities.

## Risks and Test Signals

Risks include accepting invalid v1 flags, mishandling the `ptp_perout_request` unions where `start` and `phase` depend on `PTP_PEROUT_PHASE`, and missing `clockid` reuse in `ptp_sys_offset_extended`. Test signals include ioctl decode tests for original and `*2` command names, flag validation display, sample-array sizing at `PTP_MAX_SAMPLES`, and external timestamp event formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/ptp_clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/qrtr.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/qrtr.h

## Purpose

Defines the userspace socket address and control packet ABI for Qualcomm IPC Router sockets. strace uses this to decode `AF_QIPCRTR`/QRTR socket addresses and control messages.

## Important APIs, Types, and Dependencies

The header includes `linux/socket.h` for `__kernel_sa_family_t` and `linux/types.h`. `QRTR_NODE_BCAST` and `QRTR_PORT_CTRL` define broadcast and control endpoints. `struct sockaddr_qrtr` contains family, node, and port. `enum qrtr_pkt_type` names data and control commands such as HELLO, BYE, NEW_SERVER, DEL_SERVER, DEL_CLIENT, RESUME_TX, EXIT, PING, NEW_LOOKUP, and DEL_LOOKUP. `struct qrtr_ctrl_pkt` is a packed little-endian command with either server or client payload.

## Control Flow, State, and Integration

The header has no functions. Runtime flow is datagram socket exchange between QRTR nodes and ports, with control packets advertising or removing services and clients. State is network/service discovery state held by the QRTR subsystem and peers.

## Risks and Test Signals

Risks are endian mistakes in packed control packets, confusing node broadcast with a normal node id, and assuming the union payload is valid for every command. Test signals include sockaddr decode tests, named packet type output, and raw fallback for unknown commands.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/qrtr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/quota.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/quota.h

## Purpose

Defines the generic quota control ABI for `quotactl(2)` plus netlink quota-warning attributes. strace uses it to decode quota command composition, quota record structures, quota info flags, and notification messages.

## Important APIs, Types, and Dependencies

The header depends on `linux/types.h`. It exports quota type constants `USRQUOTA`, `GRPQUOTA`, `PRJQUOTA`, command composition macros `SUBCMDMASK`, `SUBCMDSHIFT`, and `QCMD`, commands such as `Q_SYNC`, `Q_QUOTAON`, `Q_QUOTAOFF`, `Q_GETFMT`, `Q_GETINFO`, `Q_SETINFO`, `Q_GETQUOTA`, `Q_SETQUOTA`, and `Q_GETNEXTQUOTA`, quota format `QFMT_OCFS2`, and block-size constants. `struct if_dqblk` and `struct if_nextdqblk` carry hard/soft block and inode limits, usage, grace times, validity masks, and ids. `struct if_dqinfo` carries grace periods, flags, and validity. Netlink warning constants and enums describe command and attribute ids for quota notifications.

## Control Flow, State, and Integration

No runtime code is present. Kernel flow is command plus quota type packed by `QCMD`, with filesystem quota state read or mutated depending on command. Persistent state is filesystem quota accounting, limits, grace periods, and notification delivery.

## Risks and Test Signals

Risks include wrong command packing, confusing block-count units with byte-space fields, failing to honor `dqb_valid`/`dqi_valid`, and not decoding `Q_GETNEXTQUOTA`'s id-bearing result. Test signals include `quotactl` decoding for all commands/types, struct field printing with 64-bit usage and limits, validity flag names, and quota netlink warning attributes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/quota.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/rseq.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/rseq.h

## Purpose

Defines the restartable sequences userspace ABI. strace uses it to decode `rseq(2)` registration arguments and to understand the task-local shared memory layout the kernel updates on CPU migration or critical-section aborts.

## Important APIs, Types, and Dependencies

The header depends on `linux/types.h` and `asm/byteorder.h`. It exports `enum rseq_cpu_id_state`, `enum rseq_flags`, `enum rseq_cs_flags_bit`, and `enum rseq_cs_flags` for migration/no-restart-on-signal/preempt/migrate behavior. `struct rseq_cs` describes one critical section with version, flags, start IP, post-commit offset, and abort IP. `struct rseq_slice_ctrl` describes the slice extension state. `struct rseq` contains cpu id start/current fields, current `rseq_cs` pointer, flags, node id, mm cids, and embedded slice control.

## Control Flow, State, and Integration

Runtime flow is userspace registering a per-thread `struct rseq`, then placing critical-section descriptors where the kernel can abort or update CPU identity around preemption, signal, and migration events. State is per-thread and memory-mapped/shared with the kernel, not persisted to disk.

## Risks and Test Signals

Risks include ABI alignment mistakes, endian-specific field interpretation, stale cpu id use, failing to reset `rseq_cs` after abort, and decoding the slice extension as always present without considering size negotiated by syscall arguments. Test signals include `rseq` syscall decode with flags, structure-size handling, and named critical-section flags.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/rseq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/rtnetlink.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/rtnetlink.h

## Purpose

Defines the core routing netlink ABI for link, address, route, neighbor, rule, traffic-control, multicast database, nexthop, tunnel, VLAN, and statistics messages. strace uses it to decode `NETLINK_ROUTE` message types, common payload structs, attribute headers, multicast groups, and routing flags.

## Important APIs, Types, and Dependencies

Dependencies are `linux/types.h`, `linux/netlink.h`, `linux/if_link.h`, `linux/if_addr.h`, and `linux/neighbour.h`. Message ids run from `RTM_NEWLINK` through route, neighbor, rule, qdisc/class/filter/action, prefix, netconf, MDB, NSID, stats, chain, nexthop, linkprop, VLAN, nexthop bucket, and tunnel families. `struct rtattr` and `RTA_*` macros define generic nested attributes. `struct rtmsg` plus route type, protocol, scope, table, route flags, and `enum rtattr_type_t` describe routes. `struct rtnexthop`, `rtvia`, `rta_cacheinfo`, `rta_session`, `rta_mfc_stats`, `rtgenmsg`, `ifinfomsg`, `prefixmsg`, `tcmsg`, `nduseroptmsg`, and `tcamsg` cover common payloads. The header also exports `RTMGRP_*` legacy groups, `enum rtnetlink_groups`, traffic-control root/action attributes, dump flags, and extended link filters.

## Control Flow, State, and Integration

The ABI is message based: userspace sends netlink requests with a route-netlink message type, base struct, and nested attributes; the kernel replies or multicasts state changes. Persistent state is network namespace routing tables, device/link configuration, addresses, neighbors, qdisc state, bridge VLAN/MDB state, nexthop objects, and tunnel metadata.

## Risks and Test Signals

Risks include broken `RTA_OK`/`RTA_NEXT` length walking, attribute alignment mistakes, message-family number drift, route metric nesting confusion, and old legacy multicast group names overlapping newer group enums. Test signals include decoder tests for every `RTM_*` family, route/nexthop attribute parsing, tc payload parsing with `pkt_sched.h`, multicast group display, and safe unknown attribute handling.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/rtnetlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/sched.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/sched.h

## Purpose

Defines task creation flags for `clone`, `clone3`, and `unshare`, plus scheduler policy and flag constants. strace uses this header to decode process-creation bitmasks, `struct clone_args`, and scheduler syscall arguments.

## Important APIs, Types, and Dependencies

The header depends on `linux/types.h`. Classic low 32-bit clone flags include `CSIGNAL`, `CLONE_VM`, `CLONE_FS`, `CLONE_FILES`, `CLONE_SIGHAND`, `CLONE_PIDFD`, `CLONE_PTRACE`, `CLONE_VFORK`, `CLONE_PARENT`, `CLONE_THREAD`, namespace flags, TLS/TID flags, and `CLONE_IO`. `clone3` extends the flag space with `CLONE_CLEAR_SIGHAND`, `CLONE_INTO_CGROUP`, `CLONE_AUTOREAP`, `CLONE_NNP`, `CLONE_PIDFD_AUTOKILL`, and `CLONE_EMPTY_MNTNS`. `CLONE_NEWTIME` and `UNSHARE_EMPTY_MNTNS` are separately documented. `struct clone_args` is versioned by size macros and carries flags, pidfd, tids, exit signal, stack, TLS, set_tid array, and cgroup fd. Scheduler exports include `SCHED_NORMAL`, `FIFO`, `RR`, `BATCH`, `IDLE`, `DEADLINE`, `EXT`, reset-on-fork, and `SCHED_FLAG_*`.

## Control Flow, State, and Integration

Kernel flow is syscall-entry validation of flags and optional `clone_args` fields before creating or unsharing task resources. State effects are process/thread creation, namespace membership, pidfd publication, cgroup placement, signal behavior, and scheduler policy metadata.

## Risks and Test Signals

Risks include treating `CSIGNAL` bits as valid for `clone3`, missing 64-bit flags above bit 31, wrong `clone_args` version sizing, and conflating clone-only and unshare-only empty mount namespace bits. Test signals include strace decode for clone, clone3, unshare, `sched_setattr` policy flags, unknown high-bit clone flags, and short `clone_args` sizes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/sched.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/sched/types.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/sched/types.h

## Purpose

Defines `struct sched_attr`, the extensible ABI used by `sched_setattr(2)` and `sched_getattr(2)` for scheduler policy, deadline scheduling, and utilization clamping.

## Important APIs, Types, and Dependencies

The header includes `linux/types.h`. `SCHED_ATTR_SIZE_VER0` and `SCHED_ATTR_SIZE_VER1` document ABI growth. `struct sched_attr` starts with `size`, then `sched_policy`, `sched_flags`, nice value, realtime priority, deadline runtime/deadline/period fields, and utilization hint fields `sched_util_min` and `sched_util_max`.

## Control Flow, State, and Integration

No executable code is defined. Syscall flow depends on caller-provided `size` for forward/backward compatibility; the kernel reads or writes fields up to the negotiated size. State affected is per-task scheduling policy, realtime/deadline parameters, reset/keep flags, and utilization clamp hints.

## Risks and Test Signals

Risks are failing to initialize `size`, decoding util clamp fields for v0-sized structs, and mixing this extended ABI with legacy `struct sched_param`. Test signals include strace decode of `sched_setattr`/`sched_getattr`, versioned size output, deadline nanosecond fields, and utilization clamp reset values.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/sched/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/seccomp.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/seccomp.h

## Purpose

Defines seccomp modes, syscall operations, BPF return encodings, user notification structures, and notification fd ioctls. strace uses it for `seccomp(2)`, `prctl(PR_SET_SECCOMP)`, and notification ioctl decoding.

## Important APIs, Types, and Dependencies

The header depends on `linux/types.h`. It exports `SECCOMP_MODE_DISABLED`, `STRICT`, and `FILTER`; syscall operations `SECCOMP_SET_MODE_STRICT`, `SET_MODE_FILTER`, `GET_ACTION_AVAIL`, and `GET_NOTIF_SIZES`; filter flags including TSYNC, LOG, SPEC_ALLOW, NEW_LISTENER, TSYNC_ESRCH, and WAIT_KILLABLE_RECV; ordered `SECCOMP_RET_*` action values plus masks; `struct seccomp_data`; `struct seccomp_notif_sizes`, `seccomp_notif`, `seccomp_notif_resp`, and `seccomp_notif_addfd`; addfd and continue flags; and `SECCOMP_IOCTL_NOTIF_RECV`, `SEND`, `ID_VALID`, `ADDFD`, and `SET_FLAGS`.

## Control Flow, State, and Integration

Runtime flow is installing a seccomp mode/filter, then optionally receiving user notifications on a listener fd, validating ids, responding, or injecting fds into the target. State is task/thread-group seccomp filter stacks and live notification ids. The header documents that `CONTINUE` is not a general security policy mechanism because intercepted syscall arguments can change while blocked.

## Risks and Test Signals

Risks include action ordering mistakes, masking the high action bits incorrectly, unsafe assumptions about notification TOCTOU, and missing newer listener/addfd flags. Test signals include named `SECCOMP_RET_*` decoding, `seccomp_data` argument layout, notification ioctl structs, and composed filter flag output.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/seccomp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/securebits.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/securebits.h

## Purpose

Defines process securebits used by capability handling and `prctl(PR_GET_SECUREBITS/PR_SET_SECUREBITS)`. strace uses these masks to decode securebit values.

## Important APIs, Types, and Dependencies

The header has no include dependencies. It defines `issecure_mask`, `SECUREBITS_DEFAULT`, paired setting and lock bits for `SECURE_NOROOT`, `SECURE_NO_SETUID_FIXUP`, `SECURE_KEEP_CAPS`, `SECURE_NO_CAP_AMBIENT_RAISE`, `SECURE_EXEC_RESTRICT_FILE`, and `SECURE_EXEC_DENY_INTERACTIVE`, plus `SECBIT_*` masks. Aggregate masks are `SECURE_ALL_BITS`, `SECURE_ALL_LOCKS`, and `SECURE_ALL_UNPRIVILEGED`.

## Control Flow, State, and Integration

No executable flow is present. Kernel credential logic uses these per-task flags to decide how UID 0, setuid transitions, ambient capability raises, and exec restrictions behave. Lock bits make corresponding settings immutable from userspace.

## Risks and Test Signals

Risks are ignoring lock-bit pairs, assuming only the older four securebits exist, and treating aggregate masks as values to set blindly. Test signals include prctl securebits decode with all `SECBIT_*` names, locked/unlocked combinations, and unknown-bit fallback.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/securebits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/seg6_genl.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/seg6_genl.h

## Purpose

Defines the generic netlink family ABI for IPv6 Segment Routing (`SEG6`). strace uses it to decode generic netlink family name/version, commands, and attributes.

## Important APIs, Types, and Dependencies

There are no include dependencies. Exports are `SEG6_GENL_NAME`, `SEG6_GENL_VERSION`, attributes `SEG6_ATTR_DST`, `DSTLEN`, `HMACKEYID`, `SECRET`, `SECRETLEN`, `ALGID`, and `HMACINFO`, and commands `SEG6_CMD_SETHMAC`, `DUMPHMAC`, `SET_TUNSRC`, and `GET_TUNSRC`.

## Control Flow, State, and Integration

The header is declarative. Runtime flow is userspace sending generic-netlink requests to configure or dump SRv6 HMAC settings and tunnel source address state. Kernel state persists in the network namespace SRv6 configuration.

## Risks and Test Signals

Risks are simple but important: generic netlink decoders must distinguish attributes from commands, preserve unknown attrs, and handle secret material carefully when displaying payloads. Test signals include named family, command, and attribute output for `SEG6`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/seg6_genl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/smc_diag.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/smc_diag.h

## Purpose

Defines socket diagnostic ABI for SMC-R/SMC-D sockets. strace uses it to decode netlink diagnostic requests and extension attributes that expose SMC connection, link group, fallback, and DMB state.

## Important APIs, Types, and Dependencies

The header depends on `linux/types.h`, `linux/inet_diag.h`, and `rdma/ib_user_verbs.h`. `struct smc_diag_req` carries family, requested extensions, and `inet_diag_sockid`. `struct smc_diag_msg` is the base response with socket state, mode/fallback field, shutdown, id, uid, and inode. Mode constants distinguish SMC-R, fallback TCP, and SMC-D. Extension ids include `SMC_DIAG_CONNINFO`, `LGRINFO`, `SHUTDOWN`, `DMBINFO`, and `FALLBACK`. Payload structs include `smc_diag_cursor`, `smc_diag_conninfo`, `smc_diag_linkinfo`, `smc_diag_lgrinfo`, `smc_diag_fallback`, and `smcd_diag_dmbinfo`.

## Control Flow, State, and Integration

Netlink diagnostic flow mirrors inet diag: userspace requests SMC sockets and optional extensions, kernel returns base messages and nested attributes. State belongs to live SMC sockets, RDMA links, direct memory buffers, fallback causes, and cursor positions.

## Risks and Test Signals

Risks include treating `diag_fallback` as a boolean when it aliases mode, fixed one-entry link arrays hiding variable netlink nesting, RDMA device-name size dependencies, and 64-bit aligned token/gid fields. Test signals include request/response decoding, extension id names, cursor formatting, fallback reason fields, and SMC-D DMB token output.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/smc_diag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/sock_diag.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/sock_diag.h

## Purpose

Defines common socket diagnostic netlink command ids, request headers, memory info indexes, destroy multicast groups, and BPF socket storage attributes. strace uses it as shared context for protocol-specific socket diagnostic headers.

## Important APIs, Types, and Dependencies

The header depends on `linux/types.h`. It exports netlink command ids `SOCK_DIAG_BY_FAMILY` and `SOCK_DESTROY`, `struct sock_diag_req`, `SK_MEMINFO_*` indexes, `enum sknetlink_groups`, BPF storage request/reply enums, and `SK_DIAG_BPF_STORAGE_*` nested attribute ids.

## Control Flow, State, and Integration

The flow is generic netlink-style socket diagnostics: request by family/protocol, optional destroy operation, and optional protocol-specific payloads. State is live socket table metadata and optional BPF local storage maps attached to sockets.

## Risks and Test Signals

Risks include misspelling compatibility (`SK_DIAB_BPF_STORAGE_REP_MAX` is exported as written), mixing request and reply BPF storage attribute namespaces, and assuming memory-info index count is fixed forever. Test signals include netlink decode for commands, `SK_MEMINFO_*` arrays, destroy groups, and BPF storage attributes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/sock_diag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/socket.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/socket.h

## Purpose

Provides Linux UAPI socket storage and small generic socket-option constants shared by other headers. strace uses it indirectly through address structures such as QRTR, TCP MD5/AO, and generic sockaddr decoding.

## Important APIs, Types, and Dependencies

The header defines `_K_SS_MAXSIZE`, typedef `__kernel_sa_family_t`, and `struct __kernel_sockaddr_storage`, whose anonymous union controls size and pointer alignment. It also exports send/receive buffer lock masks (`SOCK_SNDBUF_LOCK`, `SOCK_RCVBUF_LOCK`, `SOCK_BUF_LOCK_MASK`) and TX rehash option values (`SOCK_TXREHASH_DEFAULT`, `DISABLED`, `ENABLED`).

## Control Flow, State, and Integration

No code flow is present. The ABI role is structural: it gives fixed-size address storage for protocol-specific socket options and generic constants for socket behavior. Kernel state affected by related options is per-socket buffer locking and transmit hash behavior.

## Risks and Test Signals

Risks include assuming libc `sockaddr_storage` is identical, breaking anonymous union layout in C++ consumers, and printing TX rehash values as booleans despite the default sentinel. Test signals include compile/layout checks and strace decoding of socket option values using these constants.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/socket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/stat.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/stat.h

## Purpose

Defines Linux file mode constants for non-glibc contexts and the `statx(2)` result ABI. strace uses it to decode `struct statx`, request/result masks, and file attribute flags.

## Important APIs, Types, and Dependencies

The header depends on `linux/types.h`. It conditionally exports `S_IF*`, `S_IS*`, and permission bit macros. `struct statx_timestamp` carries seconds, nanoseconds, and reserved space. `struct statx` is a fixed 0x100-byte extensible structure with mask, block size, attributes, link/uid/gid/mode, inode, size, blocks, attribute mask, four timestamps, device ids, mount id, DIO alignment, subvolume id, atomic write bounds, DIO read alignment, and reserved expansion. `STATX_*` request/result bits include basic stats, birth time, mount id variants, DIO alignment, subvolume, write-atomic, and DIO-read alignment. `STATX_ATTR_*` flags describe compression, immutability, append-only, nodump, encryption, automount, mount root, verity, DAX, and atomic write support.

## Control Flow, State, and Integration

There is no local control flow. The syscall fills fields according to the requested mask and filesystem support; unavailable data may be fabricated or omitted as documented. State is filesystem metadata and mount/file attributes at the time of lookup.

## Risks and Test Signals

Risks include assuming requested bits are always returned, failing to parse newer fields after `stx_mnt_id`, treating `STATX_ALL` as future-complete, and confusing `stx_attributes` with `stx_attributes_mask`. Test signals include statx decode tests for partial masks, atomic write fields, DIO alignment, mount id unique, and all attribute flags.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/stat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/stddef.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/stddef.h

## Purpose

Provides UAPI helper macros for inline annotation, mirrored struct groups, flexible arrays inside unions, counted-by annotations, and nonstring markers. This supports source compatibility for many other UAPI headers and for userspace builds of strace's bundled headers.

## Important APIs, Types, and Dependencies

There are no include dependencies. Exports include fallback `__always_inline`, `__struct_group_tag`, `__struct_group(TAG, NAME, ATTRS, MEMBERS...)`, C++ and C-specific `__DECLARE_FLEX_ARRAY`, no-op `__counted_by`, `__counted_by_le`, `__counted_by_be`, and `__kernel_nonstring`.

## Control Flow, State, and Integration

The header is macro-only. The control effect is compile-time: it preserves layout by creating anonymous and named struct views over identical members, and it permits flexible-array-like declarations in contexts that standard C otherwise rejects. It has no runtime or persistence behavior.

## Risks and Test Signals

Risks include C/C++ layout differences, compiler extension assumptions around anonymous structs/unions, and losing counted-by annotations when consumers expect them for static analysis. Test signals are successful compilation of headers that use these macros, structure offset checks, and no runtime strace behavior changes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/stddef.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/taskstats.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/taskstats.h

## Purpose

Defines the generic netlink task accounting ABI. strace uses it to decode taskstats messages reporting per-task exit, delay accounting, basic accounting, I/O accounting, context switches, executable identity, and delay extrema.

## Important APIs, Types, and Dependencies

The header depends on `linux/types.h` and `linux/time_types.h`. `TASKSTATS_VERSION` is 17 and `TS_COMM_LEN` is 32. `struct taskstats` is a versioned append-only ABI containing exit code, flags, nice, CPU/blkio/swapin/freepages/thrashing/compact/wpcopy/irq delay counts/totals/min/max/timestamps, runtime fields, command, scheduling, uid/gid/pid/ppid/tgid, start time, elapsed/user/system times, page faults, memory usage, high watermarks, I/O byte/syscall counters, scaled times, executable device/inode, and v17 max-delay timestamps. Command/type/attribute enums define generic netlink request and aggregation payloads. `TASKSTATS_GENL_NAME` and version identify the family.

## Control Flow, State, and Integration

Runtime flow is generic netlink registration, request by pid/tgid or CPU mask, and kernel event delivery when tasks exit. State is accumulated in task accounting and delay-accounting subsystems; some fields only update when accounting is enabled.

## Risks and Test Signals

Risks include struct version drift, alignment errors around 64-bit fields, interpreting delay totals without checking accounting availability, and 32-bit `ac_btime` overflow despite the v10 64-bit field. Test signals include netlink command/type decode, full `struct taskstats` formatting, v17 timestamp fields, and aggregation by PID/TGID.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/taskstats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/tcp.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/tcp.h

## Purpose

Defines the TCP protocol header, socket option numbers, TCP diagnostic/statistics structures, TCP MD5 and TCP-AO option payloads, and zero-copy receive ABI. strace uses it to decode `setsockopt`, `getsockopt`, inet diagnostic attributes, and raw TCP header-related constants.

## Important APIs, Types, and Dependencies

The header depends on `linux/types.h`, `asm/byteorder.h`, and `linux/socket.h`. Key exports are `struct tcphdr`, endian-specific flag bitfields, `union tcp_word_hdr`, `tcp_flag_word`, TCP flag constants, MSS defaults, socket options from `TCP_NODELAY` through `TCP_DELACK_MAX_US`, repair mode constants, `struct tcp_repair_opt`, `tcp_repair_window`, queue ids, fastopen failure enum, `TCPI_OPT_*`, congestion state enum and flags, ECN/AccECN constants, and the large append-only `struct tcp_info`. Netlink timestamping statistic attributes are `TCP_NLA_*`. Security/authentication payloads include `struct tcp_md5sig`, `tcp_diag_md5sig`, `tcp_ao_add`, `tcp_ao_del`, `tcp_ao_info_opt`, `tcp_ao_getsockopt`, and `tcp_ao_repair`. `struct tcp_zerocopy_receive` defines `TCP_ZEROCOPY_RECEIVE`.

## Control Flow, State, and Integration

Runtime flows are socket options configuring TCP behavior, retrieving connection stats, repairing sequence/window state, managing authentication keys, and requesting zero-copy receive mapping. Persistent state is per-socket TCP control block state, congestion-control metrics, authentication key material, fastopen state, and receive queue mapping state.

## Risks and Test Signals

Risks include endian-specific `tcphdr` layout, append-only `tcp_info` growth, sensitive key display for MD5/AO options, bitfield packing in TCP-AO structs, and fixed-size sockaddr storage in authentication options. Test signals include named socket-option decoding, `tcp_info` field coverage, TCP-AO add/delete/get/info payloads, zero-copy receive struct output, and unknown option fallback.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/tcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/tcp_metrics.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/tcp_metrics.h

## Purpose

Defines the generic netlink ABI for cached TCP destination metrics. strace uses it to decode the `tcp_metrics` family, metric ids, address attributes, Fast Open cache attributes, and list/delete commands.

## Important APIs, Types, and Dependencies

The header depends on `linux/types.h`. It exports `TCP_METRICS_GENL_NAME`, version, `enum tcp_metric_index` for RTT, RTTVAR, ssthresh, cwnd, reordering, and usec RTT variants, a duplicated attribute-id mapping for nested metrics, top-level `TCP_METRICS_ATTR_*` values for IPv4/IPv6 destination/source addresses, age, TIME-WAIT timestamp data, metric values, Fast Open MSS/drop/cookie data, and command ids `TCP_METRICS_CMD_GET` and `TCP_METRICS_CMD_DEL`.

## Control Flow, State, and Integration

Runtime flow is generic netlink request/dump/delete against the kernel's TCP metrics cache. State persists in memory as learned per-destination metrics and Fast Open cache metadata, influencing future TCP connections.

## Risks and Test Signals

Risks include the historical misspelling `TCP_METRICS_A_METRICS_REODERING`, nested metric attribute confusion, IPv4 versus IPv6 address field decoding, and assuming metrics are per-socket instead of cached per destination. Test signals include family command decode, nested metric value output, source/destination address attributes, and Fast Open cookie/drop fields.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/tcp_metrics.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/tee.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/tee.h

## Purpose

Defines the Trusted Execution Environment character-device ioctl ABI used by OP-TEE, AMDTEE, TSTEE, QTEE, and supplicant interfaces. strace uses it to decode `/dev/tee*` and `/dev/teepriv*` ioctls, shared memory operations, session management, invocation parameters, and object invocation.

## Important APIs, Types, and Dependencies

The header depends on `linux/ioctl.h` and `linux/types.h`. It exports `TEE_IOC_MAGIC`, max argument size, generic capability bits, implementation ids, OP-TEE capabilities, `struct tee_ioctl_version_data`, shared-memory allocation/register structs, `tee_ioctl_buf_data`, parameter attribute types for values, memrefs, user buffers, and object refs, login constants, `struct tee_ioctl_param`, UUID length, session open/invoke/cancel/close structs, supplicant receive/send structs, shared-memory fd registration, and `struct tee_ioctl_object_invoke_arg`. Ioctls include `TEE_IOC_VERSION`, `SHM_ALLOC`, `OPEN_SESSION`, `INVOKE`, `CANCEL`, `CLOSE_SESSION`, `SUPPL_RECV`, `SUPPL_SEND`, `SHM_REGISTER_FD`, `SHM_REGISTER`, and `OBJECT_INVOKE`.

## Control Flow, State, and Integration

Runtime flow is ioctl based: query driver version, allocate or register shared memory, open a trusted application session with typed parameters, invoke commands, cancel or close sessions, and exchange supplicant RPC messages. Persistent state is file-descriptor scoped shared memory handles, open sessions, supplicant queues, and TEE-side object references.

## Risks and Test Signals

Risks include decoding variably sized parameter arrays from `tee_ioctl_buf_data`, leaking sensitive buffer/key material in traces, confusing memory reference kinds, and alignment of 64-bit user pointers. Test signals include ioctl name coverage, parameter attribute decoding, login method names, shared-memory fd handling, and object-ref invocation formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/tee.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/thermal.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/thermal.h

## Purpose

Defines the generic netlink ABI for Linux thermal zones, trips, cooling devices, governors, and thermal events. strace uses it to decode the `thermal` family, commands, attributes, multicast groups, and event ids.

## Important APIs, Types, and Dependencies

The header has no include dependencies. It exports `THERMAL_NAME_LENGTH`, threshold direction flags, `enum thermal_device_mode`, `enum thermal_trip_type`, family name/version/group names, `enum thermal_genl_attr` for IDs, names, temperatures, trip data, cooling-device data, governor, weight, CPU masks, and threshold data, sampling ids, event ids such as thermal zone create/delete/enable/disable/trip/up/down/change/cdev/governor/threshold, and command ids for getting thermal zones, trips, cooling devices, governors, sampling, and threshold add/delete/flush.

## Control Flow, State, and Integration

Runtime flow is generic netlink request/dump and multicast notification. State belongs to thermal zones, trip points, cooling devices, governors, and thresholds in the kernel thermal framework.

## Risks and Test Signals

Risks include stale enum coverage as new thermal events are added, decoding threshold way flags as single values instead of masks, and losing nested trip/cdev attributes. Test signals include generic netlink decode for every command/event, attribute name formatting, and multicast group display.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/thermal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/tipc.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/tipc.h

## Purpose

Defines the TIPC socket ABI: addressing primitives, service subscriptions, socket address layout, options, ioctl payloads, AEAD key handling, and deprecated address helpers. strace uses it to decode `AF_TIPC` socket addresses, options, ancillary data, and ioctls.

## Important APIs, Types, and Dependencies

The header depends on `linux/types.h` and `linux/sockios.h`. It exports `tipc_socket_addr`, `tipc_service_addr`, `tipc_service_range`, service type constants, `enum tipc_scope`, message size/importance/rejection constants, subscription filter bits, `struct tipc_subscr`, `tipc_event`, `sockaddr_tipc`, ancillary data names, socket options from `TIPC_IMPORTANCE` through `TIPC_NODELAY`, group flags and `tipc_group_req`, bearer name length constants, `SIOCGETLINKNAME`, `SIOCGETNODEID`, request structs, `tipc_aead_key`, key length macros, `tipc_aead_key_size`, `TIPC_REKEYING_NOW`, deprecated address constants, aliases, and inline helpers `tipc_addr`, `tipc_zone`, `tipc_cluster`, and `tipc_node`.

## Control Flow, State, and Integration

Runtime flow is socket creation/bind/connect/send/recv using service or socket addresses, topology subscription events, option get/set, link-name/node-id ioctls, and crypto key updates. State is TIPC cluster membership, service publications, subscriptions, group membership, bearer/link metadata, and AEAD keys.

## Risks and Test Signals

Risks include union decoding based on `addrtype`, flexible-array key sizing, deprecated address helper compatibility, scope value ambiguity, and not redacting crypto key payloads. Test signals include sockaddr decode for each address type, option and ancillary names, subscription/event structs, AEAD key length handling, and ioctl request formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/tipc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/tls.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/tls.h

## Purpose

Defines Linux kernel TLS socket option ABI for configuring record-layer crypto on TCP sockets and reporting TLS offload state. strace uses it to decode `SOL_TLS` option payloads and TLS info netlink attributes.

## Important APIs, Types, and Dependencies

The header depends on `linux/types.h`. It exports options `TLS_TX`, `TLS_RX`, `TLS_TX_ZEROCOPY_RO`, `TLS_RX_EXPECT_NO_PAD`, and `TLS_TX_MAX_PAYLOAD_LEN`; version macros for TLS 1.2 and 1.3; cipher ids and key/iv/salt/tag/record-sequence sizes for AES-GCM-128/256, AES-CCM-128, CHACHA20-POLY1305, SM4-GCM/CCM, and ARIA-GCM-128/256; record type controls; base `struct tls_crypto_info`; cipher-specific TLS 1.2 crypto info structs; `TLS_INFO_*` attributes; and config states `TLS_CONF_BASE`, `SW`, `HW`, and `HW_RECORD`.

## Control Flow, State, and Integration

Runtime flow is setting transmit or receive crypto info through socket options, enabling hardware/software TLS offload state, and querying info attributes. Persistent state is per-socket crypto material, record sequence numbers, offload mode, zero-copy receive/tx hints, and maximum plaintext length.

## Risks and Test Signals

Risks include exposing key material in traces, choosing the wrong cipher-specific struct by `cipher_type`, TLS 1.3 using the same crypto-info families with different protocol semantics, and fixed array sizes drifting with new ciphers. Test signals include option decode by cipher id, version display, redaction policy checks, and `TLS_INFO_*` netlink attributes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/tls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/typelimits.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/typelimits.h

## Purpose

Defines kernel-flavored integer limit macros for UAPI userspace consumers that cannot rely on a specific libc limit header. This is a small compatibility support header for bundled Linux UAPI snapshots.

## Important APIs, Types, and Dependencies

There are no include dependencies. The only exports are `__KERNEL_INT_MAX`, computed from unsigned all-ones shifted down one bit and cast to `int`, and `__KERNEL_INT_MIN`, computed as negative max minus one.

## Control Flow, State, and Integration

The header is compile-time only and has no runtime control flow or state. It integrates indirectly wherever other UAPI headers need stable signed-int bounds without pulling in libc-specific definitions.

## Risks and Test Signals

Risks are minimal but include macro collision and non-two's-complement assumptions in exotic compilation environments. Test signals are successful preprocessing and matching values to the target compiler's `INT_MAX`/`INT_MIN`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/typelimits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/types.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/types.h

## Purpose

Defines Linux-specific fixed-width, endian-tagged, checksum, aligned, and poll types that form the foundation for most UAPI structs in this group. strace's bundled headers depend on these typedefs for ABI-correct structure layouts.

## Important APIs, Types, and Dependencies

The header includes `asm/types.h`, and outside assembly includes `linux/posix_types.h`. If the compiler supports `__int128`, it defines aligned `__s128` and `__u128`. It defines sparse-aware `__bitwise` and legacy `__bitwise__`, endian-tagged typedefs `__le16`, `__be16`, `__le32`, `__be32`, `__le64`, `__be64`, checksum types `__sum16` and `__wsum`, aligned macros `__aligned_u64`, `__aligned_s64`, `__aligned_be64`, `__aligned_le64`, and `__poll_t`.

## Control Flow, State, and Integration

This is a type foundation header with no runtime flow or persistent state. Its integration point is structural ABI stability: fields using aligned 64-bit macros must have the same layout for 32-bit userspace talking to 64-bit kernels.

## Risks and Test Signals

Risks include removing sparse annotations, using plain `__u64` where an aligned type is required, and breaking 32/64-bit compat layout. Test signals are compile checks for all dependent headers, `sizeof`/`offsetof` validation on compat-sensitive structs, and endian-tagged type availability.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/udmabuf.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/udmabuf.h

## Purpose

Defines the ioctl ABI for creating userspace DMA-BUF objects from memfd-backed memory. strace uses it to decode `/dev/udmabuf` creation requests.

## Important APIs, Types, and Dependencies

The header depends on `linux/types.h` and `linux/ioctl.h`. It exports `UDMABUF_FLAGS_CLOEXEC`, `struct udmabuf_create` for a single memfd/offset/size, `struct udmabuf_create_item` for list elements, `struct udmabuf_create_list` with flags, count, and flexible `list[]`, and ioctl numbers `UDMABUF_CREATE` and `UDMABUF_CREATE_LIST`.

## Control Flow, State, and Integration

Runtime flow is ioctl based: userspace passes one or more memfd ranges and receives a DMA-BUF fd from the kernel driver. State is fd-scoped: source memfds, exported DMA-BUF objects, offsets, sizes, and close-on-exec behavior.

## Risks and Test Signals

Risks include incorrect flexible-array sizing for list creates, integer overflow in count-to-byte calculations, invalid offset/size alignment assumptions, and missing close-on-exec flag decode. Test signals include ioctl decode for single and list create requests, list item iteration by `count`, and named flag display.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/udmabuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/unix_diag.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/unix_diag.h

## Purpose

Defines netlink diagnostic ABI for Unix-domain sockets. strace uses it to decode `SOCK_DIAG_BY_FAMILY` requests and responses for `AF_UNIX` sockets.

## Important APIs, Types, and Dependencies

The header depends on `linux/types.h`. `struct unix_diag_req` carries family, protocol, state mask, inode filter, show mask, and cookie. Show flags include `UDIAG_SHOW_NAME`, `VFS`, `PEER`, `ICONS`, `RQLEN`, `MEMINFO`, and `UID`. `struct unix_diag_msg` is the base response with family, type, state, inode, and cookie. Attribute ids are `UNIX_DIAG_NAME`, `VFS`, `PEER`, `ICONS`, `RQLEN`, `MEMINFO`, `SHUTDOWN`, and `UID`. Payload structs include `unix_diag_vfs` and `unix_diag_rqlen`.

## Control Flow, State, and Integration

Runtime flow is netlink diagnostic request and dump of kernel Unix socket table state. Persistent state is live socket names, VFS inode data, peer links, pending connection inodes, receive/write queue lengths, memory info, shutdown state, and UID.

## Risks and Test Signals

Risks include confusing abstract socket names with filesystem paths, handling optional attributes only when requested, and stale peer/socket state during dumps. Test signals include show-mask decoding, base message formatting, VFS and queue payloads, and graceful handling of missing optional attributes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/unix_diag.h -->
