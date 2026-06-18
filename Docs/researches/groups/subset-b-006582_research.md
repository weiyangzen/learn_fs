# Research Report: subset-b-006582

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/nsfs.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/nsfs.h

Purpose: this UAPI header defines the user-visible namespace filesystem ABI used by tools that inspect namespace file descriptors, namespace IDs, and mount namespace metadata. It is a contract header, not executable code, and its behavior is implemented by kernel namespace and nsfs ioctl handlers.

Important APIs/types: the `NS_GET_*` ioctls return owning user namespaces, parent namespaces, namespace type, owner UID, namespace IDs, and pid/tgid translations across pid namespaces. `struct mnt_ns_info`, `struct nsfs_file_handle`, and `struct ns_id_req` are versioned request/response layouts with explicit size constants. `enum init_ns_ino`, `enum init_ns_id`, and `enum ns_type` encode stable IDs for initial namespaces and CLONE_NEW-style namespace type bits.

Control flow: callers open an nsfs fd, issue one of the ioctl requests, and interpret either an fd, integer, UID, u64 ID, or filled struct. The list/stat namespace interfaces use a request struct with size and filter fields so callers can negotiate layout versions.

State and persistence: the header defines no state itself; persistent state is kernel namespace lifetime and namespace IDs. The risk is ABI drift, so size fields and reserved/spare fields must be preserved.

Dependencies/integration: depends on `linux/ioctl.h` and `linux/types.h`; integrated by userspace namespace tools, checkpoint/restore, container runtimes, and tests using `ioctl(2)` on `/proc/*/ns/*` fds.

Risks and test signals: validate ioctl number stability, struct sizes (`MNT_NS_INFO_SIZE_VER0`, `NSFS_FILE_HANDLE_SIZE_VER0`, `NS_ID_REQ_SIZE_VER0`), pid namespace translation behavior, permission failures, and compatibility with older kernels that lack later ioctls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/nsfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/perf_event.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/perf_event.h

Purpose: this is the core Linux `perf_event_open(2)` UAPI definition. It supplies event type IDs, sample/read formats, `struct perf_event_attr`, mmap metadata layout, record stream formats, ioctls, memory data-source encodings, branch records, and constants used by perf tools and trace consumers.

Important APIs/types: key surfaces are `enum perf_type_id`, hardware/software/cache event enums, `enum perf_event_sample_format`, branch sampling masks, `enum perf_event_read_format`, `struct perf_event_attr`, `struct perf_event_mmap_page`, `struct perf_event_header`, `enum perf_event_type`, `union perf_mem_data_src`, `struct perf_branch_entry`, and `union perf_sample_weight`. The `PERF_ATTR_SIZE_VER*` constants are critical for forward/backward compatibility. Ioctls such as `PERF_EVENT_IOC_ENABLE`, `DISABLE`, `RESET`, `PERIOD`, `SET_FILTER`, `SET_BPF`, `QUERY_BPF`, and `MODIFY_ATTRIBUTES` define the fd control plane.

Control flow: userspace fills `perf_event_attr`, opens an event fd, optionally mmaps the metadata/ring pages, controls the event with ioctls, reads grouped counter formats, and parses `PERF_RECORD_*` records according to enabled `sample_type` and `sample_id_all` bits. The mmap page includes seqlock-style fields for lockless user reads and AUX ring-buffer coordinates for hardware trace.

State and persistence: kernel event state persists while fds are open. Ring-buffer contents, counter values, lost counts, AUX watermarks, and enable/running times are live kernel/user shared state. ABI state is mostly append-only; consumers must honor `attr.size`, `header.size`, feature bits, endianness, and optional fields.

Dependencies/integration: included by perf, BPF tracing tools, KVM tooling, profilers, and observability agents. It depends on fixed-width Linux types, ioctl macros, and architecture byte-order definitions. In this subset, `tools/kvm/kvm_stat/kvm_stat` mirrors a small `perf_event_attr` subset and uses tracepoint events plus group reads.

Risks and test signals: high-risk areas are struct packing, bitfield endianness, ring-buffer ordering, interpreting optional sample payloads, 32-bit vs 64-bit truncation, and older-kernel attr sizes. Good tests open tracepoint/software events, exercise grouped reads, mmap records, lost-sample accounting, branch/data-source samples, BPF query paths, and parser tolerance for unknown `PERF_RECORD_*` types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/perf_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/pkt_cls.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/pkt_cls.h

Purpose: this UAPI header defines Linux traffic-control classifier and action ABI constants used over rtnetlink. It names action result codes, action attributes, classifier-specific netlink attributes, filter flags, and several variable-length structures used by `tc`.

Important APIs/types: generic action definitions include `TCA_ACT_*`, `TC_ACT_*`, extended action opcodes (`TC_ACT_JUMP`, `TC_ACT_GOTO_CHAIN`), `struct tc_police`, `struct tcf_t`, `struct tc_cnt`, and the `tc_gen` macro reused by action headers. Classifier sections cover u32 (`struct tc_u32_key`, `tc_u32_sel`, `tc_u32_mark`, `tc_u32_pcnt`), route4, fw, flow, basic, cgroup, BPF (`TCA_BPF_*`), flower (`TCA_FLOWER_*` and Geneve encapsulation option attributes), matchall, and ematch (`struct tcf_ematch_tree_hdr`, `struct tcf_ematch_hdr`).

Control flow: userspace builds netlink `RTM_NEWTFILTER`/`DELTFFILTER` messages with nested `TCA_*` attributes. Kernel classifier/action modules parse those attributes, install match/action state, and later return stats and flags in dumps.

State and persistence: filter and action state lives in kernel qdisc/classifier instances. Indexes, cookies, refcounts, bind counts, offload flags, timers, and per-filter counters are exposed but not owned by this header.

Dependencies/integration: depends on `linux/types.h` and `linux/pkt_sched.h`; integrated by `iproute2 tc`, hardware offload drivers, BPF tc programs, and rtnetlink `tcmsg` APIs from `rtnetlink.h`.

Risks and test signals: risks include netlink attribute number stability, flexible-array sizing, byte-order fields in u32/flower selectors, hardware offload flag interpretation, and unsupported classifier modules. Test with `tc filter` add/dump/delete for u32, flower, BPF, and actions; verify skip_hw/skip_sw/in_hw/not_in_hw flags and stats round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/pkt_cls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/pkt_sched.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/pkt_sched.h

Purpose: this header defines the traffic-control queueing discipline UAPI: qdisc handles, generic stats, rate/size specifications, and parameter/stat structures for many schedulers.

Important APIs/types: generic APIs are `struct tc_stats`, `struct tc_estimator`, handle macros (`TC_H_MAJ`, `TC_H_MIN`, `TC_H_MAKE`, root/ingress constants), `struct tc_ratespec`, and `struct tc_sizespec`. Scheduler-specific sections define FIFO, skbprio, prio, multiq, plug, TBF, SFQ/SFQRED, RED/GRED/CHOKe, HTB, HFSC, netem and loss models, DRR, MQPRIO, SFB, QFQ, CoDel, FQ-CoDel, FQ, HHF, PIE, CBS, ETF, CAKE, and TAPRIO attributes/stats.

Control flow: userspace sends `RTM_NEWQDISC`, `RTM_NEWTCLASS`, and related rtnetlink messages with `tcmsg` plus nested `TCA_*` attributes. Kernel qdisc implementations parse these structs, maintain queue state, and return xstats/stats to dump requests.

State and persistence: qdisc state persists in kernel attached to network devices/classes. This header exposes configuration knobs, statistics snapshots, and queue handles but stores no local state. Many structs are ABI-frozen and contain fixed units such as bytes, packets, microseconds, nanoseconds, rates, or fixed-point probabilities.

Dependencies/integration: depends on `linux/types.h`; integrated with `pkt_cls.h`, `rtnetlink.h`, `iproute2 tc`, NIC hardware offload paths, and time-aware scheduling features.

Risks and test signals: risks include unit confusion, 32-bit rate overflow mitigated by later 64-bit attributes, attribute nesting errors, and scheduler-specific kernel availability. Test by adding/dumping each supported qdisc, checking handle/class linkage, stats growth under traffic, and offload flags for mqprio, cbs, etf, taprio, and cake.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/pkt_sched.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/prctl.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/prctl.h

Purpose: this header defines numeric operations and sub-flags for the `prctl(2)` process-control syscall. It covers process attributes, security controls, architecture features, memory-map manipulation, scheduler-core controls, and recent architecture extensions.

Important APIs/types: it is mostly macro constants (`PR_SET_*`, `PR_GET_*`) plus `struct prctl_mm_map` for `PR_SET_MM_MAP`. Major groups include death signal, dumpability, unaligned/FPU/endian controls, keepcaps/capability bounding/ambient caps, seccomp, timerslack, perf event enable/disable, memory corruption policy, checkpoint/restore MM mutation, `no_new_privs`, THP disable, SVE/SME vector length, speculation controls, pointer authentication, tagged address/MTE/RISC-V pointer masking, syscall user dispatch, core scheduling, MDWE, named VMAs, memory merge, RISC-V vector and icache controls, PowerPC DEXCR, shadow stack status, timer restore IDs, and futex hash sizing.

Control flow: userspace calls `prctl(option, arg2, arg3, arg4, arg5)`, and the kernel dispatches by option. Some options set persistent per-thread or per-mm state, some query into user pointers, and some affect later `execve`, signal, scheduling, or memory behavior.

State and persistence: many settings persist per task, thread group, mm, or across exec when flagged. ABI stability is numeric: removed features such as MPX retain reserved numbers.

Dependencies/integration: depends on `linux/types.h`; integrated by runtimes, sandboxes, CRIU, language VMs, architecture feature probes, and security hardening code. `seccomp.h` supplies related filter-mode constants.

Risks and test signals: risk comes from architecture-specific availability, privilege checks, pointer arguments, inheritance semantics, and option numbers being permanent. Tests should cover expected `EINVAL`/`EPERM`, get-after-set behavior, exec inheritance flags, and per-architecture guarded options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/prctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/rtnetlink.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/rtnetlink.h

Purpose: this header defines rtnetlink message types, core route/link/traffic-control message structs, attribute helpers, route constants, nexthop layouts, multicast groups, and dump filters used to manage networking state from userspace.

Important APIs/types: the `RTM_*` enum covers links, addresses, routes, neighbours, rules, qdiscs/classes/filters/actions, multicast/anycast, neighbour tables, netconf, MDB, namespace IDs, stats, chains, nexthops, VLANs, buckets, and tunnels. Core structs are `rtattr`, `rtmsg`, `rtnexthop`, `rtvia`, `rta_cacheinfo`, `rta_session`, `rta_mfc_stats`, `rtgenmsg`, `ifinfomsg`, `prefixmsg`, `tcmsg`, `nduseroptmsg`, and `tcamsg`. Helper macros (`RTA_*`, `RTM_RTA`, `RTNH_*`, `TCA_RTA`, `TA_RTA`) define aligned parsing of nested payloads.

Control flow: userspace opens a netlink route socket, sends messages with `nlmsghdr` plus one of these payload structs, and appends aligned `rtattr` attributes. Kernel networking subsystems reply and multicast changes to `RTNLGRP_*` groups.

State and persistence: live state is in kernel network namespaces: interfaces, addresses, routes, neighbours, tc objects, and multicast subscriptions. The header only defines serialization and stable numeric IDs.

Dependencies/integration: includes `linux/netlink.h`, `if_link.h`, `if_addr.h`, and `neighbour.h`; used by iproute2, network managers, container runtimes, routing daemons, and tc tooling. It integrates directly with `pkt_cls.h` and `pkt_sched.h` through `tcmsg`.

Risks and test signals: risks include alignment bugs, incomplete `rta_len` validation, message-family drift, attribute nesting mistakes, and privilege/network-namespace behavior. Tests should add/dump/delete routes, links, qdiscs, filters, actions, and nexthops, including multipart dumps and multicast notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/rtnetlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/seccomp.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/seccomp.h

Purpose: this header defines the seccomp syscall/prctl ABI for strict mode, BPF filter mode, filter flags, filter return actions, `struct seccomp_data`, and user-notification ioctls.

Important APIs/types: constants include `SECCOMP_MODE_*`, `SECCOMP_SET_MODE_*`, filter flags such as `TSYNC`, `LOG`, `NEW_LISTENER`, `WAIT_KILLABLE_RECV`, return actions from `SECCOMP_RET_KILL_PROCESS` through `SECCOMP_RET_ALLOW`, and return masks. Structs include `seccomp_data`, `seccomp_notif_sizes`, `seccomp_notif`, `seccomp_notif_resp`, and `seccomp_notif_addfd`. Ioctls include notification receive/send, ID validation, addfd, and fd flag setting.

Control flow: userspace installs filters with `seccomp(2)` or `prctl(PR_SET_SECCOMP)`. BPF programs inspect `seccomp_data` and return an action. If `SECCOMP_RET_USER_NOTIF` is used, a supervisor receives notifications, validates IDs, can inject fds, and replies with allow/error/value or continue flags.

State and persistence: filters stack on tasks and are inherited according to kernel rules. User-notification fds represent live supervisor state. The comments explicitly warn that `CONTINUE` is not safe as a standalone security policy due to TOCTOU on pointer arguments.

Dependencies/integration: depends on compiler and type headers; integrates with `prctl.h`, classic BPF filter loading, container sandboxes, syscall brokers, and tracing/debugging tools.

Risks and test signals: test action precedence, data mask extraction, TSYNC errors, listener fd behavior, notification ID validity, addfd atomic send, and unsafe `CONTINUE` cases. ABI risks are struct-size negotiation and correct signed ordering of return actions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/seccomp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/seg6.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/seg6.h

Purpose: this header defines the userspace-visible IPv6 Segment Routing Header (SRH) layout and basic SRv6 TLV constants.

Important APIs/types: `struct ipv6_sr_hdr` models the SRH fixed header followed by a flexible array of `struct in6_addr` segments. Flags include protected, OAM, alert, and HMAC bits. TLV IDs include ingress, egress, opaque, padding, and HMAC. `sr_has_hmac(srh)` checks the HMAC flag. `struct sr6_tlv` represents generic type/length/data TLVs.

Control flow: networking tools and kernel netlink attribute parsers serialize or inspect SRHs using this layout. The header itself performs no parsing beyond the `sr_has_hmac` macro; callers must walk segments and TLVs using lengths from the IPv6 extension header.

State and persistence: SR state is packet-local or route configuration state elsewhere; this header only fixes wire/control-plane structures.

Dependencies/integration: depends on `linux/types.h` and `linux/in6.h`; integrated by SRv6 route actions, encapsulation attributes, packet parsers, and `seg6_local.h`.

Risks and test signals: risks include malformed `hdrlen`, flexible-array bounds, HMAC TLV handling, and network byte order for fields. Tests should build SRHs with/without HMAC, validate TLV iteration, and round-trip SRv6 route attributes through rtnetlink.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/seg6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/seg6_local.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/seg6_local.h

Purpose: this header defines netlink attributes and action IDs for SRv6 local segment endpoint behaviors.

Important APIs/types: `SEG6_LOCAL_*` attributes describe action, SRH, table, IPv4/IPv6 nexthops, input/output interfaces, and BPF configuration. `SEG6_LOCAL_ACTION_*` enumerates endpoint behaviors such as End, End.X, End.T, End.DX2/DX4/DX6, End.DT4/DT6, End.B6, End.B6.Encap, End.BM, End.S, End.AS, End.AM, and End.BPF. `SEG6_LOCAL_BPF_PROG*` attributes attach BPF program descriptors and names.

Control flow: userspace route tools encode these values in rtnetlink encapsulation/local-action attributes. Kernel SRv6 local processing dispatches the configured behavior when packets match a local SID.

State and persistence: configured SRv6 local actions persist as routing entries or lightweight tunnel state in the kernel. This file only defines the ABI values.

Dependencies/integration: includes `linux/seg6.h`; integrated with IPv6 routing, lightweight tunnels, BPF, and `iproute2` SRv6 commands.

Risks and test signals: risks include mismatched action IDs, missing mandatory attributes for a chosen action, BPF attachment compatibility, and route-table interactions. Test by adding/dumping each local action type and verifying packet forwarding/decapsulation behavior for nexthop/table/SRH cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/seg6_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/stat.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/stat.h

Purpose: this header defines file mode constants for non-glibc or kernel contexts and the `statx(2)` ABI for extended file metadata.

Important APIs/types: it defines `S_IF*`, `S_IS*`, and permission bits when appropriate. `struct statx_timestamp` and `struct statx` expose mask, block size, attributes, ownership, mode, inode, size, blocks, timestamps, device IDs, mount ID, direct-I/O alignments, subvolume ID, atomic-write limits, and spare space. `STATX_*` masks request/result fields, and `STATX_ATTR_*` exposes file attributes like compressed, immutable, append-only, encrypted, automount, mount-root, verity, DAX, and atomic-write support.

Control flow: userspace calls `statx()` with a mask; the kernel fills fields it supports and reports valid fields in `stx_mask`. The comments document synchronization behavior and compatibility fallback for basic stats.

State and persistence: returned metadata reflects filesystem/inode state and mount state at call time. Layout reserves space for future ABI expansion.

Dependencies/integration: depends on `linux/types.h`; integrated by filesystems, libc fallbacks, backup/indexing tools, direct-I/O users, and distributed filesystem clients that need mount IDs or alignment data.

Risks and test signals: risks include assuming requested fields are always returned, confusing `STATX_MNT_ID` vs unique mount ID, alignment fields availability, and treating deprecated `STATX_ALL` as complete. Test masks individually across filesystems, symlinks, device nodes, DAX/verity/encrypted files, and unsupported fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/stat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/stddef.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/stddef.h

Purpose: this compatibility header provides small UAPI helper macros for inline behavior, grouped structs, flexible arrays in unions, counted-by annotations, and nonstring markers.

Important APIs/types: `__always_inline` defaults to `__inline__` if absent. `__struct_group()` creates anonymous and named mirrored struct members inside a union so callers can address a group by name while preserving direct member access. `__DECLARE_FLEX_ARRAY()` handles C vs C++ flexible-array constraints. `__counted_by*` macros are annotation placeholders when compiler support is absent. `__kernel_nonstring` marks non-NUL string-like buffers.

Control flow: no runtime flow; these macros affect C/C++ declarations at compile time.

State and persistence: no state. ABI risk is layout: `__struct_group` and flexible-array macros must preserve intended struct size and member offsets.

Dependencies/integration: broadly used by UAPI structs that need flexible arrays or grouped layout without depending on newer compiler extensions. It is important for generated bindings and C++ consumers.

Risks and test signals: test with C and C++ compilation, `sizeof`, `offsetof`, and flexible-array placement in unions. Watch spelling/parameter compatibility because these macros are consumed by many headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/stddef.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/taskstats.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/taskstats.h

Purpose: this header defines the generic-netlink taskstats ABI for exporting per-task accounting, delay, I/O, memory, and exit statistics.

Important APIs/types: `TASKSTATS_VERSION` is 17 and `TS_COMM_LEN` is 32. `struct taskstats` is append-only and contains exit code/flags, delay accounting counters/totals/min/max/timestamps, basic accounting fields, RSS/VM high watermarks, I/O counters, context switches, scaled CPU time, begin time, executable device/inode identity, thread-group stats, and IRQ/write-protect/compaction/thrashing delay data. Netlink command/type enums define GET/NEW messages, PID/TGID/STATS aggregate attributes, and CPU mask register/deregister attributes. `TASKSTATS_GENL_NAME` and version identify the family.

Control flow: userspace talks to generic netlink `TASKSTATS`, requests stats by PID/TGID or registers CPU masks for exit notifications, then parses nested aggregate attributes containing IDs and `struct taskstats`.

State and persistence: stats are kernel task accounting snapshots; exit events are emitted when listeners are registered. Counters may wrap as documented, and delay fields require kernel delay accounting.

Dependencies/integration: depends on Linux types and time types; integrated by accounting daemons, performance diagnostics, and container/task monitors.

Risks and test signals: risks include struct version drift, alignment requirements, optional delay accounting, 32-bit begin-time overflow mitigated by `ac_btime64`, and netlink nesting. Test current/exiting tasks, PID/TGID aggregation, CPU mask registration, and version/size parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/taskstats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/tc_act/tc_bpf.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/tc_act/tc_bpf.h

Purpose: this header defines the traffic-control BPF action ABI.

Important APIs/types: `struct tc_act_bpf` expands `tc_gen` from `pkt_cls.h`, providing action index, capability, action result, refcount, and bind count. The `TCA_ACT_BPF_*` enum names nested attributes for timing metadata, parameters, classic BPF op length/ops, eBPF fd, name, padding, program tag, and program ID.

Control flow: userspace installs or dumps a tc action of kind `bpf` through rtnetlink action messages. The kernel parses BPF program attributes, attaches the action to classifier chains, and later reports metadata/stats.

State and persistence: action state and referenced BPF programs persist in kernel tc action tables while referenced. This file only fixes the serialization contract.

Dependencies/integration: includes `linux/pkt_cls.h`; used with `tc action add bpf`, clsact/flower/u32 classifiers, and BPF loaders that pass fds and names.

Risks and test signals: risks include fd lifetime, program type compatibility, tag/ID dump mismatches, and action result semantics. Tests should attach by fd, dump name/tag/id, execute action on traffic, and delete/unbind while checking refcounts and stats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/tc_act/tc_bpf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/tcp.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/tcp.h

Purpose: this header defines the Linux TCP wire header layout, socket options, diagnostic structs, TCP_INFO telemetry, MD5 signature configuration, and zero-copy receive ABI.

Important APIs/types: `struct tcphdr` uses endian-specific bitfields for data offset and flags. `union tcp_word_hdr`, `tcp_flag_word`, and `TCP_FLAG_*` support flag-word inspection. Socket options range from `TCP_NODELAY`, `MAXSEG`, keepalive, `TCP_INFO`, congestion control, MD5, repair, Fast Open, ULP, zerocopy receive, INQ, and TX delay. `struct tcp_info` exposes state, congestion state, RTT, cwnd, pacing, segment/byte counters, delivery rate, busy/limited time, retransmission, reordering, and receive window. MD5 structs and `struct tcp_zerocopy_receive` define specialized options.

Control flow: applications use `setsockopt`/`getsockopt` with these constants and structs. Packet parsers inspect `tcphdr`. Diagnostics receive netlink attributes such as `TCP_NLA_*` for timestamping stats.

State and persistence: socket options mutate per-socket TCP state; `TCP_INFO` is a snapshot. Repair mode and MD5 keys are high-impact persistent socket state.

Dependencies/integration: depends on Linux types, byte order, and socket storage. Used by networking apps, route daemons, diagnostics, packet filters, and kernel selftests.

Risks and test signals: risks include endian bitfield assumptions, partial `tcp_info` support across kernels, privileged/unsafe repair and MD5 operations, and zerocopy buffer alignment/error reporting. Test get/set option round trips, TCP_INFO length-tolerant reads, TFO/MD5 behavior, and packet flag parsing on both endian configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/tcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/tls.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/tls.h

Purpose: this header defines the Linux kernel TLS socket option ABI for configuring TLS offload/ktls crypto parameters.

Important APIs/types: `TLS_TX` and `TLS_RX` select transmit/receive parameters. Version helpers compose and split TLS version numbers; this header defines TLS 1.2. AES-GCM-128 constants define cipher ID and IV/key/salt/record-sequence sizes. `struct tls_crypto_info` carries version and cipher type; `struct tls12_crypto_info_aes_gcm_128` appends the cipher material. `TLS_SET_RECORD_TYPE` and `TLS_GET_RECORD_TYPE` are control options.

Control flow: userspace performs the handshake itself, then calls `setsockopt` with TLS_TX/TLS_RX and a cipher-specific crypto-info struct to hand record encryption/decryption to the kernel.

State and persistence: configured crypto state persists on the socket. Record sequence values and keys are sensitive and must match userspace TLS state exactly.

Dependencies/integration: depends on `linux/types.h`; integrated by OpenSSL/ktls users, NIC offload paths, and TCP ULP (`TCP_ULP`) setup.

Risks and test signals: risks include key material exposure, struct-size/cipher mismatch, unsupported TLS versions/ciphers, record sequence errors, and option ordering. Test successful ktls send/receive, fallback on unsupported kernels, and record type get/set where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/tls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/types.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/types.h

Purpose: this local UAPI copy provides Linux fixed-width and endian-tagged type aliases for tools.

Important APIs/types: it includes `asm-generic/int-ll64.h`, defines `__bitwise`, endian typedefs (`__le16`, `__be16`, `__le32`, `__be32`, `__le64`, `__be64`), checksum types (`__sum16`, `__wsum`), and 8-byte aligned aliases (`__aligned_u64`, `__aligned_be64`, `__aligned_le64`) when not assembling.

Control flow: no runtime flow; it is a compile-time foundation for UAPI structs.

State and persistence: no state. Layout and alignment choices influence all ABI structs that include these types.

Dependencies/integration: consumed by most headers in this subset, especially networking, perf, statx, namespace, and userfaultfd headers.

Risks and test signals: risks are compiler compatibility and alignment differences across architectures. Test by compiling representative UAPI structs and checking size/alignment against kernel expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/userfaultfd.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/userfaultfd.h

Purpose: this header defines the userfaultfd ABI for userspace-managed page faults, write protection, minor faults, page movement, poisoning, and `/dev/userfaultfd` creation.

Important APIs/types: `UFFD_API`, feature masks, and ioctl bitmasks advertise available modes. Ioctls include API negotiation, register/unregister, wake, copy, zeropage, move, writeprotect, continue, and poison. `struct uffd_msg` defines read events for pagefault, fork, remap, remove, and unmap. `struct uffdio_api`, `uffdio_range`, `uffdio_register`, `uffdio_copy`, `uffdio_zeropage`, `uffdio_writeprotect`, `uffdio_continue`, `uffdio_poison`, and `uffdio_move` are the request/response structs.

Control flow: userspace creates a userfaultfd, negotiates `UFFDIO_API`, registers memory ranges, polls/reads `uffd_msg` events, resolves faults with copy/zeropage/continue/move/poison/writeprotect ioctls, and wakes waiting threads unless DONTWAKE is set.

State and persistence: registered ranges and enabled features persist while the fd and mappings exist. Ioctl result fields are intentionally at the end because the kernel writes them without reading them from userspace.

Dependencies/integration: depends on `linux/types.h`; used by live migration, post-copy VM migration, checkpoint/restore, memory managers, and fault-injection tests.

Risks and test signals: risks include feature negotiation mistakes, range alignment, wake semantics, async write-protection behavior, fork/remap/unmap event ordering, and security restrictions for kernel vs user-mode faults. Test all register modes, feature probes, short/failed ioctls, event delivery, and race handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/userfaultfd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/vdso/bits.h -->
# sources/distributed-fs/ceph-client/tools/include/vdso/bits.h

Purpose: this tiny vDSO helper defines `BIT()` and `BIT_ULL()` using vDSO constant-suffix helpers.

Important APIs/types: `BIT(nr)` expands to `UL(1) << nr`; `BIT_ULL(nr)` expands to `ULL(1) << nr`. These macros create unsigned long or unsigned long long bit masks without hard-coding suffixes directly.

Control flow: compile-time macro expansion only.

State and persistence: no state.

Dependencies/integration: includes `vdso/const.h`, which wraps UAPI constant helpers. Used by vDSO and low-level headers needing bit constants in C and assembler-friendly contexts.

Risks and test signals: risks are shift overflow or using a bit index wider than the target type. Test by compiling masks in 32-bit and 64-bit builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/vdso/bits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/vdso/const.h -->
# sources/distributed-fs/ceph-client/tools/include/vdso/const.h

Purpose: this vDSO helper exposes typed constant macros `UL()` and `ULL()` backed by the UAPI Linux constant helpers.

Important APIs/types: `UL(x)` expands to `_UL(x)`, and `ULL(x)` expands to `_ULL(x)`. The included `uapi/linux/const.h` handles details such as assembler vs C constant spelling.

Control flow: compile-time only.

State and persistence: no state.

Dependencies/integration: used by `vdso/bits.h` and other low-level headers that need literal suffixes to be portable across toolchains.

Risks and test signals: test with C and assembler preprocessing where these headers are included. Main risk is suffix mismatch causing truncation or invalid assembly tokens.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/vdso/const.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/vdso/unaligned.h -->
# sources/distributed-fs/ceph-client/tools/include/vdso/unaligned.h

Purpose: this header provides safe unaligned scalar load/store macros for vDSO and low-level code.

Important APIs/types: `__get_unaligned_t(type, ptr)` declares a non-const scalar temporary via `__unqual_scalar_typeof`, copies bytes from `ptr` with `__builtin_memcpy`, and returns the value. `__put_unaligned_t(type, val, ptr)` copies a scalar value into an unaligned destination. Both cast through `void *` to avoid UBSAN noise.

Control flow: macro expansion performs a fixed-size `memcpy` at the call site. No loops or external functions are required.

State and persistence: the get macro reads caller memory; the put macro mutates caller memory. There is no persistent state.

Dependencies/integration: includes `linux/compiler_types.h` for attributes and scalar type helpers. Used when direct unaligned dereference or type punning would violate strict aliasing or alignment rules.

Risks and test signals: risks include passing expressions with side effects, incorrect `type`, invalid pointers, and endian assumptions left to callers. Test under UBSAN/ASAN, strict-aliasing builds, and architectures that fault on unaligned accesses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/vdso/unaligned.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/kvm/kvm_stat/Makefile -->
# sources/distributed-fs/ceph-client/tools/kvm/kvm_stat/Makefile

Purpose: this Makefile builds and installs the `kvm_stat` man page and installs the Python tool into a target bindir.

Important APIs/targets: it includes shared tool makefiles, sets `BINDIR`, `MANDIR`, `MAN1DIR`, `MAN1`, and `A2X`, resolves `a2x` with `get-executable`, and defines targets `all`, `clean`, `man`, `install-man`, `install-tools`, and `install`.

Control flow: default `all` depends on `man`. The `%.1: %.txt` rule errors if `a2x` is missing, otherwise runs `a2x --doctype manpage --format manpage`. Install targets create destination directories and copy `kvm_stat.1` and `kvm_stat` with install modes.

State and persistence: generated state is `kvm_stat.1`; installed state goes under `$(INSTALL_ROOT)/usr/bin` and `$(INSTALL_ROOT)/usr/share/man/man1`.

Dependencies/integration: depends on asciidoc/a2x and kernel tools makefile helpers. The `install-tools` target honors `TARGET` for destination filename.

Risks and test signals: risk is missing `a2x`, incorrect install root, or stale man page. Test `make man`, `make clean`, and staged `make INSTALL_ROOT=/tmp/... install`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/kvm/kvm_stat/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/kvm/kvm_stat/kvm_stat -->
# sources/distributed-fs/ceph-client/tools/kvm/kvm_stat/kvm_stat

Purpose: `kvm_stat` is a Python 3, top-like KVM monitoring tool. It samples KVM debugfs counters and/or KVM tracepoint perf events, then renders an interactive curses UI, one-shot batch output, or continuous log/CSV output.

Important APIs/types/functions: architecture classes (`ArchX86`, `ArchPPC`, `ArchA64`, `ArchS390`) provide perf syscall numbers, ioctl numbers, exit-reason fields, and child-event rules. `perf_event_attr`, `Group`, and `Event` wrap tracepoint perf-event setup, grouped reads, filter ioctls, enable/disable/reset. `TracepointProvider` discovers KVM tracing events, expands exit-reason filters, opens per-CPU or per-thread groups, and aggregates counts. `DebugfsProvider` reads KVM debugfs files with baselines. `Stats` merges providers and calculates deltas. `Tui` handles curses rendering, guest selection, regex filters, sorting, resets, and child display. `batch`, `StdFormat`, `CSVFormat`, and `log` implement noninteractive modes.

Control flow: `main()` discovers debugfs paths, parses options, checks tracing access, validates pid/delay, builds `Stats`, optionally lists fields, then selects log, curses, or batch mode. Tracepoint setup reads event IDs from debugfs tracing, calls `perf_event_open`, applies optional filters, and reads group leader fds. Debugfs mode walks `/sys/kernel/debug/kvm` and subtracts baselines.

State and persistence: runtime state includes open perf fds, fd limits, debugfs baselines, previous `EventStat` values, curses screen state, selected pid/regex, and optional log file. With `-L`, SIGHUP reopens the log file and CSV mode avoids duplicate headers on append.

Dependencies/integration: requires mounted readable debugfs, KVM debugfs entries, tracing events, `/proc`, `ps`, libc syscall access via `ctypes`, curses, CAP_SYS_ADMIN/perf permissions in some cases, and possibly CAP_SYS_RESOURCE for fd limits. It integrates with `perf_event.h` ABI and the provided systemd service.

Risks and test signals: risks include architecture syscall-number drift, perf permission failures, high fd counts on many CPUs/events, debugfs layout changes, guest-name parsing heuristics, curses terminal errors, and event disappearance while reading. Test `--fields help`, `--once`, debugfs-only mode, tracepoint mode, pid/guest filters, invalid regex/delay, log/CSV append and SIGHUP reopen, and behavior when debugfs/tracing/KVM is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/kvm/kvm_stat/kvm_stat -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/kvm/kvm_stat/kvm_stat.service -->
# sources/distributed-fs/ceph-client/tools/kvm/kvm_stat/kvm_stat.service

Purpose: this systemd unit runs `kvm_stat` as a background logger for KVM module trace events.

Important APIs/directives: `[Unit]` sets a description and orders the service before `qemu-kvm.service`. `[Service]` uses `Type=simple`, executes `/usr/bin/kvm_stat -dtcz -s 10 -L /var/log/kvm_stat.csv`, reloads with `SIGHUP`, restarts always after 60 seconds, and sets syslog identity/level. `[Install]` targets `multi-user.target`.

Control flow: systemd starts the Python tool in debugfs plus tracepoint mode, CSV mode, skip-zero-records mode, 10-second interval, and log-to-file mode. Reload sends SIGHUP, which `kvm_stat` handles by closing/reopening the log path and reprinting headers as needed.

State and persistence: persistent output is `/var/log/kvm_stat.csv`. Systemd restart policy keeps monitoring alive across failures.

Dependencies/integration: depends on installed `/usr/bin/kvm_stat`, readable debugfs/tracing/KVM state, and system permissions suitable for perf/debugfs access. Ordering before qemu-kvm means it should be available early for VM launches.

Risks and test signals: risks include missing permissions, absent debugfs, log growth, restart loops, and startup before KVM modules are loaded. Test `systemctl start/reload/status`, CSV creation, SIGHUP rotation behavior, and failure output when tracing is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/kvm/kvm_stat/kvm_stat.service -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/laptop/dslm/Makefile -->
# sources/distributed-fs/ceph-client/tools/laptop/dslm/Makefile

Purpose: this small Makefile builds the `dslm` disk sleep monitor utility.

Important APIs/targets: it sets `CC := $(CROSS_COMPILE)gcc`, `CFLAGS := -I../../usr/include`, `PROGS := dslm`, and defines `all` plus `clean`.

Control flow: default `all` builds `dslm` through make's implicit C compilation rule. `clean` removes the program.

State and persistence: generated state is the `dslm` executable in the source directory.

Dependencies/integration: depends on a C compiler, optional `CROSS_COMPILE`, and headers under `../../usr/include` including Linux hdreg definitions used by `dslm.c`.

Risks and test signals: risk is relying on implicit rules and local kernel headers. Test `make`, `make clean`, and cross-compile variable propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/laptop/dslm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/laptop/dslm/dslm.c -->
# sources/distributed-fs/ceph-client/tools/laptop/dslm/dslm.c

Purpose: `dslm.c` is a simple disk sleep monitor that samples an ATA disk's power mode and prints time spent active, sleeping, or unknown until interrupted.

Important APIs/functions: `check_powermode()` issues `HDIO_DRIVE_CMD` with `WIN_CHECKPOWERMODE1`, retries `WIN_CHECKPOWERMODE2`, and maps results to active/sleeping/unknown. `state_name()` and `myctime()` format output. `measure()` samples once per second, detects state transitions, accumulates per-state durations, and prints summary percentages. `ender()` handles SIGINT by setting global `endit`. `main()` parses either `<disk>` or `-w <time> <disk>`-shaped arguments, opens the disk nonblocking read-only, waits for settle time, installs SIGINT, and calls `measure()`.

Control flow: after optional settle sleep, the loop calls `check_powermode()` every second. When the state changes or SIGINT ends the loop, it accounts elapsed time against the previous state and prints the transition.

State and persistence: runtime state is in local counters and global `endit`; no files are modified. The disk fd remains open until exit.

Dependencies/integration: depends on Linux `hdreg.h`, ATA ioctls, permissions to open the block device, and signal handling. It is standalone and built by the local Makefile.

Risks and test signals: notable risk: `if (!(fd = open(...)))` treats fd 0 as failure and negative fd as success; it should have been `fd < 0`. Other risks are deprecated ioctls, non-ATA devices, percentage divide by zero on very short runs, and `ctime()` buffer mutation. Test with invalid devices, fd 0 edge via closed stdin, SIGINT summary, and active/sleeping disks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/laptop/dslm/dslm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/laptop/freefall/Makefile -->
# sources/distributed-fs/ceph-client/tools/laptop/freefall/Makefile

Purpose: this Makefile builds and installs the `freefall` laptop disk-protection daemon.

Important APIs/targets: configurable variables include `PREFIX`, `SBINDIR`, and `INSTALL`. `TARGET = freefall`. Pattern rule `%: %.c` compiles with `$(CC) $(CFLAGS) $(LDFLAGS)`. Targets are `all`, `clean`, and `install`.

Control flow: `all` builds `freefall`; `clean` removes it; `install` copies it to `$(DESTDIR)$(PREFIX)/$(SBINDIR)/freefall` with mode 755.

State and persistence: generated executable and installed binary are the only artifacts.

Dependencies/integration: depends on a C compiler and install utility. It deliberately uses standard make variables for distro packaging.

Risks and test signals: test build with custom `CC/CFLAGS/LDFLAGS`, staged install with `DESTDIR`, and clean idempotence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/laptop/freefall/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/laptop/freefall/freefall.c -->
# sources/distributed-fs/ceph-client/tools/laptop/freefall/freefall.c

Purpose: `freefall.c` is a daemon for HP/DELL-style free-fall sensors that parks disk heads when `/dev/freefall` reports motion and optionally toggles an HDD-protection LED.

Important APIs/functions: `set_unload_heads_path()` validates `/dev/*` input and maps it to `/sys/block/<dev>/device/unload_heads`. `valid_disk()` checks sysfs support. `write_int()` writes numeric sysfs values. `set_led()` writes LED brightness unless missing. `protect()` writes park duration in milliseconds and logs with syslog. `ignore_me()` handles SIGALRM by unparking heads and clearing the LED. `main()` validates the target disk, opens `/dev/freefall`, daemonizes, opens syslog, elevates scheduling to FIFO, locks memory, installs alarm handler, and loops reading sensor events.

Control flow: each successful read from `/dev/freefall` cancels old alarms, parks heads for 21 seconds, turns the LED on, then sets a short alarm to unpark. If `read()` is interrupted by SIGALRM, the loop continues after `ignore_me()` has unparked.

State and persistence: persistent side effects are sysfs writes to `unload_heads` and LED brightness plus syslog messages. Runtime state includes global paths, `noled`, open sensor fd, scheduler policy, and locked memory.

Dependencies/integration: depends on `/dev/freefall`, block-device sysfs `unload_heads`, optional HP LED path, daemon/syslog APIs, realtime scheduling, and memory locking privileges.

Risks and test signals: risks include fixed buffer sizes/truncation, hard-coded LED path, stubbed `on_ac()`/`lid_open()` always returning true, ignored scheduler/mlock failures, and running as a daemon with hardware side effects. Test invalid devices, absent LED, SIGALRM unpark path, read interruption, sysfs write failures, and daemon startup under expected privileges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/laptop/freefall/freefall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/leds/Makefile -->
# sources/distributed-fs/ceph-client/tools/leds/Makefile

Purpose: this Makefile builds LED userspace tools `uledmon` and `led_hw_brightness_mon`.

Important APIs/targets: `CFLAGS = -Wall -Wextra -g -I../../include/uapi`; default target builds both tools using a generic `%: %.c` rule; `clean` removes both executables; `.PHONY` marks `all` and `clean`.

Control flow: invoking `make` compiles each C file into a same-name executable with the configured compiler and UAPI include path.

State and persistence: generated executables are stored in the tools/leds directory.

Dependencies/integration: depends on a C compiler and local UAPI headers. The directory also contains the shell validator researched separately.

Risks and test signals: risks include no install target and debug flags in default CFLAGS. Test `make`, warning-free builds under `-Wall -Wextra`, and `make clean`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/leds/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/leds/get_led_device_info.sh -->
# sources/distributed-fs/ceph-client/tools/leds/get_led_device_info.sh

Purpose: this shell script inspects an LED class device in sysfs, reports hardware details, and validates the LED class device name against Linux LED color/function definitions.

Important APIs/functions: it accepts `LED_CDEV_PATH` and optionally `LED_COMMON_DEFS_PATH`; otherwise it derives the kernel top and uses `include/dt-bindings/leds/common.h`. It probes `brightness`, bus type via `device/subsystem`, USB ancestry, OF compatible strings, input devices, drivers, vendor/product/manufacturer files, and optional Wi-Fi phy names. Helper functions `print_msg_ok` and `print_msg_failed` format validation rows.

Control flow: after argument and path validation, the script classifies the LED as USB, input, OF gpio/pwm/compatible, or unknown. It prints hardware fields, splits the LED device basename on `:`, maps one/two/three-section names to devicename/color/function, derives expected device names from input or wifi phy, checks redundant/unknown devicenames, and looks up color/function definitions in the common header.

State and persistence: it reads sysfs and the definitions header only; no system state is changed. It exits nonzero on invalid paths, unknown types, malformed names, or failed hard checks.

Dependencies/integration: depends on POSIX shell utilities (`realpath`, `dirname`, `awk`, `sed`, `grep`, `cut`, `readlink`, `ls`, `cat`, `tr`) and Linux LED sysfs layout.

Risks and test signals: risks include unquoted variables in tests/cd/cat paths, fragile USB path regexes, binary OF compatible contents, grep pattern false positives, and assumptions about input/driver paths. Test LED names with one/two/three colon sections, USB Wi-Fi LEDs, input LEDs, gpio/pwm OF LEDs, missing definitions, spaces/special chars in paths, and unknown bus types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/leds/get_led_device_info.sh -->
