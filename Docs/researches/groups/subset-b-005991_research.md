# Research: subset-b-005991

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pidfd.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/pidfd.h

Purpose: defines the userspace ABI for pid file descriptors, including `pidfd_open()` flags, `pidfd_send_signal()` targeting flags, namespace lookup ioctls, and structured process metadata retrieval.

Important APIs and types: `PIDFD_NONBLOCK`, `PIDFD_THREAD`, and kernel-only `PIDFD_STALE`/`PIDFD_AUTOKILL` describe pidfd creation semantics. `PIDFD_SIGNAL_THREAD`, `PIDFD_SIGNAL_THREAD_GROUP`, and `PIDFD_SIGNAL_PROCESS_GROUP` select signal delivery scope. `struct pidfd_info` is a versioned ioctl payload with `mask`, pid/tgid/ppid, credential IDs, cgroup id, exit status, coredump data, and `supported_mask`. `PIDFD_GET_*_NAMESPACE` ioctls return namespace file descriptors, and `PIDFD_GET_INFO` is an `_IOWR` query using `PIDFS_IOCTL_MAGIC`.

Control flow: userspace obtains a pidfd, optionally sends scoped signals, or calls ioctls against the pidfs file. For `PIDFD_GET_INFO`, userspace sets `mask` and passes a structure size implied by the ioctl ABI; the kernel fills only supported and size-covered fields and reflects valid fields in `mask`.

State and persistence: the header stores no state. Runtime state is process lifetime, pid namespace membership, credentials, coredump bookkeeping, and pidfs file lifetime. Returned metadata can be stale immediately after the ioctl, but is documented as correct for the intended process at execution time.

Dependencies and integration points: depends on Linux integer types, `fcntl` flag values, and ioctl encoding. Integrates with pidfs, process namespaces, signal delivery, cgroup identifiers, coredump reporting, and pidfd-aware process supervisors.

Risks and test signals: risks include ABI version drift, userspace failing to validate returned `mask`, stale-process assumptions, namespace fd permission mistakes, and signal scope confusion. Test with pidfd self constants, exited tasks, thread vs process-group signaling, short/old `pidfd_info` sizes, namespace ioctls across namespaces, and coredump/exit reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pidfd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pkt_cls.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/pkt_cls.h

Purpose: defines the traffic-control classifier and action netlink ABI used by `tc` and kernel networking to configure packet classification, policing, action chains, BPF/flower/u32 filters, extended matches, and hardware offload metadata.

Important APIs and types: generic action attributes are `TCA_ACT_*`, action return codes are `TC_ACT_*`, and extended opcodes use `TC_ACT_JUMP`/`TC_ACT_GOTO_CHAIN` with `TC_ACT_EXT_*` helpers. `enum tca_id`, `struct tc_police`, `struct tcf_t`, and `tc_gen` provide common action/police layout. Classifier sections expose `TCA_U32_*` plus `struct tc_u32_sel/key/mark/pcnt`, route4, fw, flow, basic, cgroup, BPF (`TCA_BPF_*`, `TCA_BPF_FLAG_ACT_DIRECT`), flower (`TCA_FLOWER_*` plus nested tunnel, MPLS, conntrack, CFM, and encapsulation option attributes), matchall, and ematch (`struct tcf_ematch_*`, `TCF_EM_*`).

Control flow: userspace builds rtnetlink messages with classifier-specific nested attributes. The kernel validates attributes, creates or updates filter/action objects, optionally offloads them, and later dumps stats and offload state through the same attribute IDs. Action chains return `TC_ACT_*` values that direct packet traversal, reclassification, redirect, trap, drop, or chain jumps.

State and persistence: persistent state is kernel qdisc/filter/action state bound to netdevices, chains, blocks, and net namespaces. This header defines serialized netlink attribute IDs and fixed structs; runtime counters, offload state, cookies, and timestamps live in classifier/action objects.

Dependencies and integration points: includes `linux/pkt_sched.h` for rate specs and uses fixed Linux integer and endian types. Integrates with rtnetlink, `tc`, cls_u32, cls_flower, cls_bpf, actions, ematch modules, BPF program fds/ids/tags, tunnel metadata, conntrack, MPLS, PPPoE/L2TP, CFM, and switchdev/devlink offload drivers.

Risks and test signals: high-risk areas are ABI numbering stability, nested attribute parsing, endian/mask handling, flexible-array sizing, offload flags (`SKIP_HW`, `SKIP_SW`, `IN_HW`), and range/tunnel/conntrack matches diverging between software and hardware. Test via `tc` filter add/replace/delete/dump for u32, flower, BPF, matchall, chained actions, police rate64 fields, hardware offload skip flags, malformed nested attrs, and netns cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pkt_cls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pkt_sched.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/pkt_sched.h

Purpose: defines the userspace ABI for Linux traffic-control queue disciplines, qdisc/class handles, generic stats, rate and size specs, and many scheduler-specific option/stat structures.

Important APIs and types: common pieces include `TC_PRIO_*`, `struct tc_stats`, `struct tc_estimator`, `TC_H_*` handle macros, `enum tc_link_layer`, `struct tc_ratespec`, `struct tc_sizespec`, and stab attributes. Scheduler sections define option and stats ABIs for FIFO, skbprio, prio, multiq, plug, TBF, SFQ/SFQRED, RED/GRED/CHOKe, HTB, HFSC, netem, DRR, mqprio, SFB, QFQ, CoDel/FQ-CoDel, FQ, HHF, PIE/FQ-PIE, CBS, ETF, CAKE, TAPRIO, ETS, and DUALPI2.

Control flow: `tc` encodes qdisc/class creation and changes as rtnetlink attributes using these `TCA_*` IDs and structs. The kernel parses the payload into scheduler instances, enqueues/dequeues packets according to qdisc-specific algorithms, and dumps generic and private xstats back to userspace.

State and persistence: qdisc state is in-memory per netdevice/queue/class: token buckets, deficits, RED averages, flow queues, timers, gate schedules, offload flags, statistics, and hardware state. The ABI structures persist only as configuration and dump serialization; no on-disk state is defined.

Dependencies and integration points: depends on Linux const/type headers and integrates with rtnetlink, `tc`, qdisc modules, netdevice TX queues, hardware offload for mqprio/taprio/ETF/CBS/HTB, PTP/clockids for time-aware scheduling, and AQM algorithms such as CoDel, PIE, CAKE, and DUALPI2.

Risks and test signals: risks include field unit confusion (bytes, packets, usec, nsec, sectors-like cells), 32-bit vs 64-bit rate/latency attributes, reserved flag compatibility, flexible nested TAPRIO/MQPRIO entries, and offload/software behavior mismatch. Test qdisc add/change/dump for each scheduler, strict flag validation for v1/v2 ioctls where present, rate64 fallbacks, netem distributions, TAPRIO schedules, mqprio frame preemption, and malformed netlink attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pkt_sched.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pktcdvd.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/pktcdvd.h

Purpose: defines the control ABI for the packet-writing block layer used with ATAPI/SCSI CD-R, CD-RW, DVD-R, and DVD-RW devices.

Important APIs and types: constants describe writer limits, packet buffering, device types (`PACKET_CDR*`, `PACKET_DVDR*`), media/status flags, disc/session states, and mode/block encodings. `struct pkt_ctrl_command` carries setup, teardown, and status requests with source device, packet device, device index, and device count. `PACKET_CTRL_CMD` is the only ioctl, encoded with magic `'X'`.

Control flow: userspace opens the packet control device and issues `PKT_CTRL_CMD_SETUP`, `PKT_CTRL_CMD_TEARDOWN`, or `PKT_CTRL_CMD_STATUS`; the kernel creates/removes packet devices or reports mapping state.

State and persistence: runtime state is packet-device binding, writer slots, buffered packet data, and optical media state. The header exposes control fields only; media contents are persisted by the underlying optical device.

Dependencies and integration points: depends on Linux integer types and ioctl encoding. Integrates with the block layer, cdrom/scsi drivers, packet writing module, and userspace tools managing `/dev/pktcdvd`.

Risks and test signals: risks include stale device numbers, old 32-bit `dev_t` encoding, teardown while I/O is active, and media-state/reporting mismatches. Test setup/status/teardown, max writer handling, invalid device indices, writable/non-writable media, and module unload with open packet devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pktcdvd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pmu.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/pmu.h

Purpose: defines the `/dev/pmu` ABI for Apple PowerBook Power Management Unit commands, model identifiers, wake events, I2C modes, interrupt bits, and ioctls.

Important APIs and types: command constants cover power control, ADB, XPRAM/NVRAM, RTC, backlight, PC-card eject, battery state, interrupt masks, shutdown/sleep/reset, I2C, and version reads. Model enums identify OHare, Heathrow, Paddington, KeyLargo, and deprecated 68K PMUs. `PMU_IOC_*` ioctls provide sleep, backlight get/set/grab, model query, ADB availability, and sleep capability.

Control flow: userspace or platform code issues ioctls or low-level PMU commands; the PMU microcontroller updates power, backlight, battery, RTC, and wake-event state and returns status through the character device.

State and persistence: state resides in PMU firmware/hardware: power rails, wake masks, RTC/NVRAM/XPRAM, battery and lid status. Some values persist in NVRAM/RTC; most ioctl state is transient hardware state.

Dependencies and integration points: includes ioctl definitions and integrates with PowerPC platform PMU drivers, ADB, battery/power subsystems, RTC, backlight, and legacy laptop userspace tools.

Risks and test signals: risks include legacy model differences, privileged power-control misuse, size_t ioctl type compatibility, and unclear command support per PMU generation. Test compile on relevant PowerPC configs, ioctl behavior on supported hardware/emulation, backlight bounds, sleep capability gating, and PMU interrupt/wake events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/poll.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/poll.h

Purpose: exposes the architecture-specific poll/select event bit definitions to userspace by including `<asm/poll.h>`.

Important APIs and types: this wrapper defines no new structures or constants itself; it forwards `POLLIN`, `POLLOUT`, `POLLERR`, `POLLHUP`, and related architecture ABI definitions.

Control flow: userspace includes this header when compiling code that calls `poll()`, `ppoll()`, or consumes poll masks from device APIs. Runtime behavior is implemented in syscall and file-operation poll paths.

State and persistence: no state is owned here. Poll state is transient wait-queue readiness in kernel file descriptors.

Dependencies and integration points: depends entirely on arch UAPI `asm/poll.h` and integrates with libc headers, syscalls, device drivers, sockets, and event loops.

Risks and test signals: risk is wrapper/architecture mismatch or duplicate libc definitions. Test architecture header export, C userspace compilation, and poll mask compatibility across supported architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/poll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/posix_acl.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/posix_acl.h

Purpose: defines common POSIX ACL constants for ACL type, entry tag, undefined IDs, and permission bits.

Important APIs and types: `ACL_TYPE_ACCESS` and `ACL_TYPE_DEFAULT` classify access/default ACLs. Entry tags include `ACL_USER_OBJ`, `ACL_USER`, `ACL_GROUP_OBJ`, `ACL_GROUP`, `ACL_MASK`, and `ACL_OTHER`. Permission bits are `ACL_READ`, `ACL_WRITE`, and `ACL_EXECUTE`; `ACL_UNDEFINED_ID` marks entries without a user/group ID.

Control flow: filesystem and userspace ACL tools use these constants when translating ACL entries to permissions or xattrs. There is no executable flow in the header.

State and persistence: ACL state persists as filesystem metadata, commonly in extended attributes. The header only defines constants used to encode/decode that state.

Dependencies and integration points: integrates with VFS POSIX ACL handling, filesystem xattr implementations, backup/restore tools, and `getfacl`/`setfacl` style utilities.

Risks and test signals: risks include inconsistent interpretation of `ACL_MASK`, undefined IDs, and default ACL inheritance. Test ACL create/read/update/delete across filesystems, chmod interactions, xattr round trips, and permission checks for named user/group entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/posix_acl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/posix_acl_xattr.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/posix_acl_xattr.h

Purpose: defines the on-xattr wire format for POSIX ACLs exposed to userspace.

Important APIs and types: `POSIX_ACL_XATTR_VERSION` is the supported ACL xattr version. `struct posix_acl_xattr_header` stores little-endian `a_version`, and `struct posix_acl_xattr_entry` stores little-endian tag, permission, and ID fields.

Control flow: userspace reads or writes ACL xattrs; the kernel validates the header version and converts each serialized xattr entry to in-kernel ACL entries before applying permissions.

State and persistence: ACL xattr data persists in filesystem extended attributes. All multibyte fields are little-endian, making the xattr format independent of host CPU endianness.

Dependencies and integration points: depends on Linux integer/endian types and integrates with VFS ACL helpers, filesystem xattr storage, NFS/export tools, and ACL utilities.

Risks and test signals: risks include endian conversion errors, malformed variable-length xattrs, version mismatch, and incorrect `ACL_UNDEFINED_ID` handling. Test xattr round trips on big/little endian builds, invalid lengths, unknown versions, and ACL enforcement after restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/posix_acl_xattr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/posix_types.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/posix_types.h

Purpose: provides generic Linux POSIX type declarations and includes architecture-specific type definitions needed by UAPI headers.

Important APIs and types: the header defines the `__FD_SETSIZE` baseline, `__kernel_fd_set`, `__kernel_sighandler_t`, `__kernel_key_t`, and `__kernel_mqd_t`, then includes `<asm/posix_types.h>` for architecture-width types such as inode, mode, pid, uid, gid, clock, and time representations.

Control flow: there is no runtime control flow. It is a foundational compile-time include used by many exported headers to stabilize type names.

State and persistence: no state is stored. ABI persistence is the stable size and signedness of exported POSIX scalar types per architecture.

Dependencies and integration points: depends on `linux/stddef.h` and arch UAPI `asm/posix_types.h`; integrates broadly with syscall structs, libc, filesystem, process, time, and socket ABIs.

Risks and test signals: risks include architecture type width drift, fd-set size assumptions, and userspace/libc redefinition conflicts. Test exported headers with `make headers_install`, cross-architecture compile checks, and ABI comparison tooling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/posix_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ppdev.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ppdev.h

Purpose: defines the Linux parallel-port userspace character-device ABI for claiming ports, data/control/status I/O, negotiation modes, IRQ/timeouts, and IEEE 1284 device ID retrieval.

Important APIs and types: mode constants include compatibility, nibble, byte, ECP, EPP, and vendor-specific flags. `struct ppdev_frob_struct` controls bit-mask updates, and ioctl constants such as `PPCLAIM`, `PPRELEASE`, `PPSETMODE`, `PPRDATA`, `PPWDATA`, `PPRCONTROL`, `PPFCONTROL`, `PPRSTATUS`, `PPNEGOT`, `PPGETTIME/PPSETTIME`, `PPGETMODES`, `PPGETPHASE`, `PPGETFLAGS/PPSETFLAGS`, and `PPGETDEVICEID` define the control surface.

Control flow: userspace opens `/dev/parportN`, claims exclusive access, selects protocol/mode, performs data/control/status operations or negotiation, and releases the port. Kernel parport code arbitrates claims and maps ioctls to hardware or parport driver methods.

State and persistence: state is transient per file/port claim: selected mode, phase, flags, timeout, IRQ use, and hardware register values. No durable state is stored by the header.

Dependencies and integration points: uses ioctl encoding and integrates with parport core, IEEE 1284 devices, printers, scanners, GPIO-like parallel hardware, and legacy userspace drivers.

Risks and test signals: risks include unsafe hardware access, missing `PPCLAIM`, ioctl size compatibility, timing-sensitive EPP/ECP negotiation, and concurrent access. Test claim/release exclusivity, mode negotiation, control-bit frobbing, timeout behavior, IRQ waits, and device-id retrieval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ppdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ppp-comp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ppp-comp.h

Purpose: defines PPP Compression Control Protocol constants and option helpers for BSD-Compress, Deflate, MPPE, and legacy predictor options.

Important APIs and types: CCP packet macros read code, id, length, option code, and option length. BSD helpers encode version and code size (`BSD_NBITS`, `BSD_VERSION`, `BSD_MAKE_OPT`). Deflate helpers encode window size and method (`DEFLATE_SIZE`, `DEFLATE_METHOD`, `DEFLATE_MAKE_OPT`). Constants define option IDs and minimum/maximum bit/window sizes.

Control flow: PPP negotiation code parses CCP packets, validates option lengths, negotiates compression methods, and resets compression state using these codes. The header itself is macro-only.

State and persistence: compression state lives in PPP channel/session compressors and decompressors; negotiated options persist only for the link lifetime.

Dependencies and integration points: integrates with PPP core, pppd, kernel compression modules, MPPE support, and RFC CCP negotiation.

Risks and test signals: risks include accepting malformed CCP lengths, compression parameter mismatch between peers, unsupported MPPE expectations, and reset handling. Test PPP CCP negotiation for BSD/Deflate, invalid option lengths, reset request/ack, and pppd interoperability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ppp-comp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ppp-ioctl.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ppp-ioctl.h

Purpose: defines the PPP character-device and socket ioctl ABI for configuring PPP units/channels, compression, filters, multilink, L2TP stats, and link flags.

Important APIs and types: `SC_*` flags control protocol/address compression, VJ TCP compression, CCP state, IP enablement, multilink, logging/debug, sync mode, and decompression errors. `struct npioctl`, `struct ppp_option_data`, and `struct pppol2tp_ioc_stats` carry network-protocol mode, compression option data, and L2TP counters. `PPPIOC*` ioctls cover flags, async maps, MRU/MRRU, units, channels, filters, compression, idle stats, bridge/unbridge, and L2TP stats; `SIOCGPPP*` commands expose device stats/version.

Control flow: pppd and related tools open PPP devices, create/attach units and channels, set flags/maps/MRU, install filters, enable compression, connect channels, then query stats or detach. The kernel PPP layer maps ioctls to per-unit and per-channel state changes.

State and persistence: state is per PPP unit/channel and link lifetime: flags, maps, filters, compression state, network protocol mode, channel bindings, idle counters, and L2TP statistics. No durable state is defined.

Dependencies and integration points: depends on `linux/ppp_defs.h`, compiler `__user`, BPF socket filter structs, and ioctl/socket command numbers. Integrates with PPP generic, ppp_async/sync, pppoe, pptp/l2tp, pppd, and network device stats.

Risks and test signals: risks include ioctl numbering compatibility, 32/64-bit idle time variants, user pointer validation for compression options, filter privilege checks, and channel/unit lifetime races. Test pppd bring-up/teardown, compression negotiation, filter install, multilink, L2TP stats, bridge/unbridge, and compat ioctl paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ppp-ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ppp_defs.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ppp_defs.h

Purpose: defines core PPP frame layout constants, protocol numbers, FCS helpers, packet statistics structs, idle-time structs, and network protocol mode enum values shared by PPP kernel and userspace.

Important APIs and types: constants include `PPP_HDRLEN`, `PPP_FCSLEN`, `PPP_MRU`, address/control bytes, protocol IDs such as `PPP_IP`, `PPP_IPV6`, `PPP_LCP`, `PPP_CCP`, and escape/control values. `struct pppstat`, `struct vjstat`, `struct ppp_stats`, `struct ppp_comp_stats`, and idle-time structs expose counters. `enum NPmode` controls pass/drop/error/queue behavior for protocols.

Control flow: PPP framing uses these constants to parse and emit frames, select protocol handlers, update stats, and negotiate modes. Userspace reads stats through ioctls and uses protocol constants in configuration.

State and persistence: PPP counters, VJ/compression stats, and idle timestamps are runtime link state. The header defines the serialized ABI, not storage.

Dependencies and integration points: depends on Linux types and integrates with PPP generic, pppd, compression modules, Van Jacobson TCP compression, and network protocol demultiplexing.

Risks and test signals: risks include protocol constant mismatch, FCS/stat struct compatibility, 32/64-bit time handling, and compression stats overflow. Test frame encode/decode, IPv4/IPv6 and control protocol demux, stats ioctls, idle counters, and pppd compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ppp_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pps.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/pps.h

Purpose: defines the Pulse-Per-Second userspace ABI for querying PPS sources, configuring capture modes, fetching timestamp events, and creating PPS clients.

Important APIs and types: mode bits include capture assert/clear, offset assert/clear, echo assert/clear, canonical/noncanonical timestamp formats, and read/write wait modes. `struct pps_ktime`, `pps_kparams`, `pps_fdata`, `pps_bind_args`, and `pps_info` carry timestamps, offsets, sequence counters, source metadata, and binding information. `PPS_GETPARAMS`, `PPS_SETPARAMS`, `PPS_GETCAP`, `PPS_FETCH`, `PPS_KC_BIND`, and related ioctls form the API.

Control flow: userspace opens a PPS device, queries capabilities, sets desired capture/offset mode, waits/fetches events, and optionally binds kernel consumers. The kernel timestamps assert/clear edges and updates sequence counters.

State and persistence: PPS source state is runtime only: current params, last assert/clear timestamps, sequence counters, and source path/name. Offsets and modes persist for the device open/source lifetime, not across reboot.

Dependencies and integration points: depends on Linux types and ioctl. Integrates with serial/GPIO/PTP PPS providers, NTP/chrony time synchronization, and kernel PPS clients.

Risks and test signals: risks include timestamp format compatibility, timeout semantics, sequence wrap, offset sign handling, and capability/mode mismatch. Test PPS_FETCH blocking and timeout paths, assert/clear modes, offsets, compat structs, and NTP/chrony integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pps_gen.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/pps_gen.h

Purpose: defines the generator-side PPS ABI for configuring a PPS pulse generator.

Important APIs and types: `struct pps_gen_event` reports the last generator event and sequence number. `PPS_GEN_EVENT_MISSEDPULSE` identifies a missed pulse. `PPS_GEN_SETENABLE`, `PPS_GEN_USESYSTEMCLOCK`, and `PPS_GEN_FETCHEVENT` are the ioctl controls for enabling generation, querying whether the system clock is used, and fetching event state.

Control flow: userspace configures a PPS generator device through ioctls; the kernel driver enables or disables pulse generation, reports clock-source behavior, and records missed-pulse events for later fetch.

State and persistence: generator enablement, clock-source selection, last event type, and event sequence are runtime device state. No persistent configuration is stored by the header.

Dependencies and integration points: depends on Linux types and ioctl encoding. Integrates with PPS generator drivers and time synchronization test setups that need synthetic PPS signals.

Risks and test signals: risks include timing precision, missed-pulse event loss, ioctl pointer compatibility, and ambiguity around system-clock mode. Test enable/disable, event sequence increments, missed-pulse reporting, invalid ioctl arguments, and pulse output timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pps_gen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pr.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/pr.h

Purpose: defines persistent reservation ioctl payloads, status values, reservation types, and key-query structures for block devices.

Important APIs and types: `enum pr_status` reports success, I/O error, reservation conflict, retryable path failure, fast path failure, and failed path states. `enum pr_type` includes write-exclusive, exclusive-access, registrants-only, and all-registrants modes. `struct pr_reservation`, `pr_registration`, `pr_preempt`, and `pr_clear` carry command arguments. `struct pr_read_keys` and `struct pr_read_reservation` query registered keys and the current reservation. `IOC_PR_*` ioctls register, reserve, release, preempt, clear, and read reservation state; `PR_FL_IGNORE_KEY` and `PR_KEYS_MAX` bound behavior.

Control flow: userspace reservation tools issue ioctls through the block layer using these structs to register keys, reserve, release, preempt, clear, or report reservation behavior. Kernel block/SCSI code translates requests to persistent reservation commands.

State and persistence: reservation keys and reservation state persist in target storage device firmware according to SCSI PR semantics. Header structs serialize commands but do not store state locally.

Dependencies and integration points: depends on Linux types. Integrates with block device ioctls, SCSI/NVMe reservation support, multipath clustering, fencing, and shared-storage failover tools.

Risks and test signals: risks include data-loss from incorrect preempt/clear, key pointer validation in read-key queries, unsupported target semantics, and cluster split-brain. Test registration/reserve/release/preempt/clear against capable devices or scsi_debug, read keys/reservation buffer sizing, multipath failover, permission checks, and invalid type/flag rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/prctl.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/prctl.h

Purpose: defines the large `prctl(2)` command namespace for per-process and per-thread controls spanning signals, credentials, seccomp, capabilities, memory layout, architecture features, speculation mitigations, scheduling, memory execution policy, timers, futex/rseq, and CFI.

Important APIs and types: early commands cover parent-death signal, dumpability, unaligned/FPU behavior, keepcaps, process name, endian, seccomp, capability bounding/ambient sets, TSC, securebits, timerslack, perf events, MCE kill, and `PR_SET_MM` with `struct prctl_mm_map`. Later commands include ptracer control, subreaper, no-new-privs, THP disable, FP modes, SVE/SME vector length, speculation controls, PAC, tagged address/MTE/RISC-V pointer masks, IO flusher, syscall user dispatch, scheduler core sharing, MDWE, VMA naming, auxv retrieval, memory merge, RISC-V vector/icache controls, PowerPC DEXCR, shadow stack, timer restore IDs, futex hash, rseq slice extension, and branch-landing-pad CFI.

Control flow: userspace calls `prctl(option, arg2, arg3, arg4, arg5)`. The kernel dispatches on `option`, validates privilege and architecture support, mutates task/mm/security/arch state, or returns current settings. Several controls are inherited across fork/exec or have explicit on-exec bits.

State and persistence: state is per task, thread group, mm, credentials, security state, or architecture context. Most settings persist for process/thread lifetime and may inherit across fork/exec depending on command-specific flags; none are durable after process exit.

Dependencies and integration points: depends on Linux types and bit helpers. Integrates with scheduler, LSM/commoncap, seccomp, perf, MM, CRIU, ptrace/Yama, architecture-specific vector/tag/PAC/DEXCR/shadow-stack code, futex, rseq, and libc process-control wrappers.

Risks and test signals: risks are severe because this is security- and ABI-sensitive: option number stability, privilege enforcement, inheritance semantics, architecture config gating, pointer validation, and irreversible locks. Test each command family with positive/negative permissions, fork/exec inheritance, seccomp/no-new-privs interactions, CRIU `PR_SET_MM`, arch selftests for SVE/SME/MTE/RISC-V/PowerPC/shadow stack, MDWE enforcement, and unknown option rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/prctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/psample.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/psample.h

Purpose: defines the generic netlink ABI for packet sampling events, sample groups, tunnel metadata, and sample-rate/probability reporting.

Important APIs and types: `PSAMPLE_ATTR_*` attributes describe ingress/egress ifindex, original size, sample group, group sequence, sample rate or probability, packet data, group refcount, tunnel metadata, output TC occupancy, latency, timestamp, protocol, and user cookie. `enum psample_command` includes sample and group operations. `enum psample_tunnel_key_attr` carries tunnel ID, IPv4/IPv6 endpoints, ToS/TTL, flags, Geneve/VXLAN/ERSPAN options, transport ports, and bridge mode. Family constants are `PSAMPLE_GENL_NAME`, version, and multicast group names.

Control flow: kernel sampling producers emit `PSAMPLE_CMD_SAMPLE` generic-netlink messages with attributes to the packets multicast group; userspace can query and receive group config messages via the config group.

State and persistence: sample groups, sequence counters, and refcounts are runtime network namespace state. Individual samples are transient netlink messages and are not persisted.

Dependencies and integration points: integrates with generic netlink, tc sample action, switchdev/offload sampling, tunnel metadata, monitoring collectors, and network telemetry systems.

Risks and test signals: risks include dropped multicast samples, inconsistent rate/probability semantics, oversized packet data, tunnel attribute mismatch, and group refcount leaks. Test tc sample action, hardware/offload sampled packets, netlink attribute validation, multicast listener loss behavior, and tunnel metadata decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/psample.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/psci.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/psci.h

Purpose: defines ARM Power State Coordination Interface function IDs, power-state encodings, version/feature helpers, reset/off types, and return codes shared by kernel, KVM, and userspace.

Important APIs and types: macros build 32-bit and 64-bit PSCI function IDs for v0.2 through v1.3, including CPU suspend/on/off, affinity info, system off/reset/suspend/reset2/off2, mem protect, and statistics. Power-state masks describe original and extended suspend encodings. Version macros decode major/minor. Return constants include success, not supported, invalid params, denied, already on, on pending, disabled, not present, and invalid address.

Control flow: ARM firmware clients issue PSCI calls through SMC/HVC using these function IDs; KVM may emulate or forward calls for guests. Callers decode return values and feature bits to select supported behavior.

State and persistence: PSCI state is firmware/platform CPU and system power state. The header only defines call numbers and encodings.

Dependencies and integration points: integrates with ARM/arm64 boot, CPU hotplug, suspend/resume, KVM PSCI emulation, firmware interfaces, and userspace tooling that interprets PSCI IDs.

Risks and test signals: risks include wrong 32/64-bit function ID selection, power-state encoding mismatch, firmware version quirks, and KVM guest ABI drift. Test PSCI feature discovery, CPU on/off/suspend under KVM and hardware, reset/off paths, hibernate off type, and invalid parameter handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/psci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/psp-dbc.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/psp-dbc.h

Purpose: defines the userspace ioctl ABI for AMD Dynamic Boost Control through the Platform Security Processor.

Important APIs and types: fixed sizes define nonce, signature, and UID buffers. `struct dbc_user_nonce`, `struct dbc_user_setuid`, and `struct dbc_user_param` are packed ioctl payloads for nonce exchange, UID programming, and parameter get/set. `DBCIOCNONCE`, `DBCIOCUID`, and `DBCIOCPARAM` use ioctl type `'D'`. `enum dbc_cmd_msg` identifies Fmax cap, power cap, graphics mode, current temperature, min/max limits, and current SoC power queries.

Control flow: userspace requests a nonce, optionally authenticates, sets a UID once, then sends signed parameter commands. The PSP validates signatures/state and returns parameter values or updated signatures.

State and persistence: PSP/driver state includes nonce validity, UID programming, mailbox state, and dynamic boost parameters. UID is documented as set once until reboot; boost limits affect platform power/performance until changed/reset.

Dependencies and integration points: depends on Linux types and ioctl macros through consumers. Integrates with AMD PSP mailbox driver, firmware authentication, power management, and platform tuning tools.

Risks and test signals: risks include authentication bypass, replayed nonce/signature, packed-struct ABI mistakes, mailbox recovery races, and unsafe power cap values. Test nonce one-shot vs authenticated reuse, UID set-once enforcement, signature failure, invalid message IDs, timeout/busy paths, and parameter bound checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/psp-dbc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/psp-sev.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/psp-sev.h

Purpose: defines the AMD SEV/SNP platform management userspace ABI for PSP firmware commands, return codes, certificates, platform status, firmware IDs, and SNP configuration.

Important APIs and types: command enum includes factory reset, platform status, PEK/PDH generation and certificate operations, deprecated and current ID retrieval, SNP platform status, commit, set config, and VLEK load. `sev_ret_code` lists firmware and wrapper errors. Packed structs include platform status, PEK CSR/import/export buffers, ID retrieval, SNP status/config/commit/VLEK payloads, and the top-level `struct sev_issue_cmd` used by the ioctl. The ioctl family is typically exposed through `/dev/sev` with command ID, data pointer, and firmware error reporting.

Control flow: userspace management tools build a command-specific packed payload, wrap it in the issue-command structure, and call the SEV ioctl. The kernel validates user buffers, serializes PSP mailbox access, invokes firmware, copies output fields, and reports both syscall errno and SEV firmware status.

State and persistence: state is PSP firmware/platform SEV state: ownership, certificates, platform config, guest count, SNP state, VLEK material, and firmware identity. Certificate and ownership state can persist across boots or until factory reset depending on platform firmware.

Dependencies and integration points: depends on Linux integer types and packed ABI layout. Integrates with AMD PSP, KVM SEV/SNP guest launch infrastructure, attestation/certificate tooling, firmware update/ownership workflows, and cloud confidential-computing management.

Risks and test signals: risks include destructive factory reset/commit operations, certificate buffer length races, packed alignment/compat issues, firmware error propagation, and SNP config policy mistakes. Test status and cert export/import, small/large buffers, deprecated `GET_ID` handling, SNP status/config flows, concurrent command serialization, and negative firmware return codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/psp-sev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/psp-sfs.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/psp-sfs.h

Purpose: defines the AMD Seamless Firmware Servicing userspace ioctl ABI for querying firmware versions and requesting PSP-managed firmware package updates.

Important APIs and types: `PAYLOAD_NAME_SIZE` and `TEE_EXT_CMD_BUFFER_SIZE` bound payload and version buffers. `struct sfs_user_get_fw_versions` returns a firmware-version blob plus SFS status fields. `struct sfs_user_update_package` carries a payload name and returns status/extended status. `SFSIOCFWVERS` and `SFSIOCUPDATEPKG` use ioctl type `'S'`.

Control flow: userspace asks for firmware versions or names an update package. The kernel driver loads firmware from the configured firmware search path, sends PSP/ASP commands, and returns SFS status codes.

State and persistence: firmware versions and update results are PSP/platform persistent state. Driver mailbox state is transient; an update may change durable firmware levels.

Dependencies and integration points: depends on Linux types and ioctl encoding. Integrates with AMD PSP, firmware_class search path, platform firmware packages under `/lib/firmware/amd`, and administrative update tooling.

Risks and test signals: risks include wrong firmware payload selection, path/config ambiguity, interrupted updates, oversized names/blobs, and poor status decoding. Test version query, valid and missing packages, firmware_class path overrides, PSP busy/timeout paths, and status/extended-status propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/psp-sfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/psp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/psp.h

Purpose: defines an auto-generated generic netlink UAPI for a `psp` networking family with device, association, key, and statistics attributes.

Important APIs and types: family constants are `PSP_FAMILY_NAME` and version. `enum psp_version` lists supported PSP header/security modes. Attribute sets define device ID/ifindex and enabled/capable versions, association device/version/RX/TX keys/socket fd, key material/SPI, and stats such as key rotations, stale events, RX/TX packets/bytes/errors/auth failures. Commands cover device get/set/add/delete/change notifications, key rotation and notification, RX/TX association, and stats retrieval. Multicast groups are `mgmt` and `use`.

Control flow: userspace speaks generic netlink to enumerate/configure PSP-capable devices, rotate keys, bind associations, and query stats. Kernel networking code validates nested attributes and emits notifications on management/use groups.

State and persistence: runtime state includes per-device PSP capabilities, enabled versions, associations, key material, SPI, socket binding, and counters. Persistence depends on device/driver; the netlink ABI itself is runtime.

Dependencies and integration points: generated from a YNL spec, integrates with generic netlink/YNL tooling, network devices, PSP-aware offload or protocol code, and management agents.

Risks and test signals: risks include generated spec/header drift, key material exposure, attribute policy mistakes, multicast notification loss, and stats width/ordering compatibility. Test YNL schema validation, dev get/set, association add/remove, key rotation, notification delivery, and malformed netlink attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/psp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ptp_clock.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ptp_clock.h

Purpose: defines the Precision Time Protocol hardware clock character-device ABI for capabilities, external timestamping, periodic output, PPS, pin muxing, and system/device time offset measurement.

Important APIs and types: flag definitions cover external timestamp edges/offsets/strict validation and periodic output one-shot/duty-cycle/phase modes. `struct ptp_clock_time`, `ptp_clock_caps`, `ptp_extts_request`, `ptp_perout_request`, `ptp_sys_offset`, `ptp_sys_offset_extended`, `ptp_sys_offset_precise`, `ptp_pin_desc`, and `ptp_extts_event` define ioctl/event payloads. Ioctls include v1 and strict v2 variants for get caps, external timestamp, periodic output, PPS enable, sys offset, pin get/set, precise/extended offset, mask controls, and cycle-based offset queries.

Control flow: userspace opens `/dev/ptpN`, queries capabilities, configures timestamp or output channels/pins, reads events, and measures PHC-system offset. The kernel validates flags, programs hardware through PTP clock drivers, and returns timestamp samples.

State and persistence: PTP state is per hardware clock: configured pins, external timestamp channels, periodic outputs, PPS enablement, masks, and driver counters. It is runtime hardware state, not persistent across driver reset.

Dependencies and integration points: depends on Linux ioctl/types and `__kernel_clockid_t`. Integrates with network drivers, PHC subsystem, PPS, time synchronization daemons such as linuxptp/chrony, hardware timestamping, and time-aware networking.

Risks and test signals: risks include nanosecond/second sign semantics, flag compatibility between v1/v2 ioctls, sample count bounds, clockid reserved-field compatibility, pin/channel validation, and hardware capability mismatches. Test `phc2sys`/`testptp`, ext timestamp edges, perout duty/phase, sys offset sample limits, pin muxing, PPS enable, and invalid flag rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ptp_clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ptrace.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ptrace.h

Purpose: defines generic architecture-independent ptrace request numbers, option/event bits, signal/syscall info structs, seccomp metadata, and register-set access contracts.

Important APIs and types: base requests include trace, peek/poke, continue, kill, singlestep, attach, detach, and syscall. Extended requests include set/get options, siginfo, regset get/set, seize/interrupt/listen, peeksiginfo, sigmask get/set, seccomp filter/metadata, syscall info get/set, and related option/event constants. `struct ptrace_peeksiginfo_args`, `struct seccomp_metadata`, and `struct ptrace_syscall_info` serialize extended data.

Control flow: a tracer attaches or is inherited via `PTRACE_TRACEME`, sets options, resumes/stops tracees, inspects registers/memory/signals, and observes syscall or seccomp stops. The kernel enforces ptrace permission and LSM policy before exposing task state.

State and persistence: ptrace state is per tracee/tracer relationship: stop state, options, event messages, signal masks, and seccomp filter metadata visibility. It ends when tracing detaches or task exits.

Dependencies and integration points: depends on Linux types and architecture regset note types. Integrates with procfs, signal delivery, seccomp, ELF core notes, debuggers, strace, crash dump tooling, CRIU, and architecture register APIs.

Risks and test signals: risks include privilege bypass, stop-state races, regset size handling through iovec, seccomp filter leakage, and arch-specific option drift. Test debugger/strace workflows, seize/interrupt/listen, syscall info entry/exit/seccomp stops, signal mask operations, regset partial buffers, and LSM/Yama permission denial.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pwm.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/pwm.h

Purpose: defines the userspace character-device ABI for querying PWM chips and getting/setting PWM channel state.

Important APIs and types: `struct pwmchip_info` reports chip name, npwm, and reserved fields. `struct pwm_args` carries default period and polarity. `struct pwm_state` carries period, duty cycle, polarity, enabled flag, and reserved padding. Ioctls are `PWM_GETCHIPINFO`, `PWM_GETARGS`, `PWM_GETSTATE`, and `PWM_SETSTATE` with magic `'p'`.

Control flow: userspace opens a PWM chip/channel cdev, queries chip/channel defaults, reads current state, and writes a new state. The kernel PWM core validates duty <= period, polarity support, and provider callbacks before programming hardware.

State and persistence: PWM state is runtime hardware/provider state: period, duty cycle, polarity, and enablement. It may survive process exit while the device remains configured but is not guaranteed persistent across reboot/driver reset.

Dependencies and integration points: depends on Linux ioctl/types. Integrates with PWM core, platform PWM providers, fan/backlight/motor control tools, and device-tree/default PWM arguments.

Risks and test signals: risks include unsafe duty/period values, polarity mismatch, unit confusion in nanoseconds, and racing kernel consumers. Test get/set state, invalid duty > period, enable/disable transitions, provider removal, and concurrent users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pwm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/qemu_fw_cfg.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/qemu_fw_cfg.h

Purpose: defines the userspace ABI and selector constants for QEMU firmware configuration entries exposed by the fw_cfg device.

Important APIs and types: constants identify fw_cfg signature, ID, UUID, RAM size, boot devices, kernel/initrd/cmdline/setup entries, file directory, write channel, architecture-local selector range, invalid selector, register width, file-name length, signature length, DMA feature bits, DMA control bits, and vmcoreinfo format values. `struct fw_cfg_file` describes directory entries with size, selector, reserved field, and name. `struct fw_cfg_dma_access` describes DMA control, length, and guest physical address. `struct fw_cfg_vmcoreinfo` describes host/guest vmcoreinfo format, size, and physical address.

Control flow: guest firmware, kernel drivers, or userspace select fw_cfg entries and read values or file directory contents; DMA-capable paths submit a `fw_cfg_dma_access` descriptor to QEMU.

State and persistence: fw_cfg data is supplied by the virtual machine monitor for the guest boot/runtime. It is not guest-persistent unless backed by QEMU configuration.

Dependencies and integration points: depends on Linux fixed and endian types. Integrates with QEMU virtual hardware, firmware/bootloaders, ACPI/SMBIOS/initrd passing, vmcoreinfo/crash dump plumbing, and guest userspace tools reading `/sys/firmware/qemu_fw_cfg`.

Risks and test signals: risks include endian handling, selector/address width mistakes, DMA control ordering, and trusting host-provided data. Test fw_cfg file directory reads, DMA vs non-DMA paths, invalid selectors, and QEMU machine/version compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/qemu_fw_cfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/qnx4_fs.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/qnx4_fs.h

Purpose: defines on-disk QNX4 filesystem constants and structures for superblocks, inodes, links, and extent blocks.

Important APIs and types: constants define root inode, block and directory entry sizes, name limits, extent counts, filesystem status, inode status flags, and magic integration. `struct qnx4_inode_entry`, `qnx4_link_info`, `qnx4_xblk`, and `qnx4_super_block` describe the serialized disk layout.

Control flow: the QNX4 filesystem driver reads the superblock and inode entries, follows direct and extended extent blocks, resolves long-name link entries, and maps file data from extents. The header itself is data-layout only.

State and persistence: all structures represent persistent on-disk metadata in little-endian or QNX-specific fixed layouts: inode times, sizes, extents, owner/group/mode, link counts, and superblock root records.

Dependencies and integration points: depends on `linux/qnxtypes.h`, Linux fixed types, and filesystem magic constants. Integrates with the QNX4 filesystem driver, VFS, mount tools, and forensic/recovery utilities.

Risks and test signals: risks include malformed disk images, endian/packing drift, extent chain loops, long filename link resolution bugs, and fixed 512-byte block assumptions. Test mounting valid QNX4 images, fsck/forensic comparisons, corrupted extent blocks, long names, and read-only behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/qnx4_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/qnxtypes.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/qnxtypes.h

Purpose: defines fixed-width QNX4 on-disk scalar types and extent representation used by the QNX4 filesystem ABI.

Important APIs and types: typedefs define QNX4 extent count, file type, mode, uid, gid, offset, and link count widths. `qnx4_xtnt_t` stores little-endian block and size fields for an extent.

Control flow: no control flow exists. QNX4 filesystem code uses these types while decoding on-disk metadata from `qnx4_fs.h`.

State and persistence: these typedefs describe persistent disk layout widths and endian choices; they do not own runtime state.

Dependencies and integration points: depends on Linux fixed integer types and integrates only with QNX4 filesystem structures and tools.

Risks and test signals: risks include widening/sign changes that would corrupt disk ABI, endian conversion mistakes, and extent-size overflow. Test compile layout assertions, QNX4 image mount/read, and cross-endian metadata decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/qnxtypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/qrtr.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/qrtr.h

Purpose: defines the Qualcomm IPC Router userspace socket address and control-packet ABI.

Important APIs and types: `QRTR_NODE_BCAST` and `QRTR_PORT_CTRL` define broadcast/control endpoints. `struct sockaddr_qrtr` carries address family, node, and port. `enum qrtr_pkt_type` identifies data, hello/bye, server/client add/delete, resume, exit, ping, and lookup messages. `struct qrtr_ctrl_pkt` carries little-endian command plus server or client endpoint payload.

Control flow: userspace binds/connects QRTR sockets using `sockaddr_qrtr`; control messages announce services and clients through the control port. Kernel QRTR routes data/control packets between local clients, remote nodes, and transports.

State and persistence: QRTR node/port mappings, service lookup registrations, and transport state are runtime IPC state. No persistent state is defined.

Dependencies and integration points: depends on socket and Linux type headers. Integrates with Qualcomm modem/remoteproc services, AF_QIPCRTR sockets, service discovery, and QRTR transports.

Risks and test signals: risks include endpoint spoofing, stale service records, endian mistakes in control packets, and broadcast storms. Test service registration/lookup, remote node connect/disconnect, malformed control packets, and socket address validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/qrtr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/quota.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/quota.h

Purpose: defines the `quotactl` userspace ABI for user, group, and project quotas, including command encoding, quota formats, limit/usage structures, grace timers, and notification values.

Important APIs and types: `QCMD`, `Q_SYNC`, `Q_QUOTAON/OFF`, `Q_GETFMT`, `Q_GETINFO/SETINFO`, `Q_GETQUOTA/SETQUOTA`, and `Q_GETNEXTQUOTA` define operations. `QFMT_*` names quota formats. `struct if_dqblk`, `struct if_nextdqblk`, and `struct if_dqinfo` carry space/inode limits, usage, grace times, validity masks, and warnings. `QIF_*` and `IIF_*` masks select valid fields; quota netlink warning constants identify soft/hard limit and grace events.

Control flow: userspace calls `quotactl()` with a `QCMD(command,type)` and filesystem path/id/payload. The kernel dispatches to filesystem quota ops, updates or reads quota records, and may emit warnings/events.

State and persistence: quota limits, usage, grace times, and accounting flags persist in filesystem quota files or metadata depending on format. Runtime state includes in-memory dquot caches and enabled/disabled status.

Dependencies and integration points: depends on Linux types and integrates with VFS quota core, ext*/xfs/ocfs2/shmem quota implementations, quota tools, project quotas, and quota warning delivery.

Risks and test signals: risks include block-size unit confusion (`QIF_DQBLKSIZE`), project quota type handling, validity-mask misuse, grace-time semantics, and format-specific behavior. Test quotaon/off, set/get limits for user/group/project, grace expiry, get-next iteration, usage accounting under writes/unlinks, and filesystem format compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/quota.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/radeonfb.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/radeonfb.h

Purpose: defines legacy Radeon framebuffer ioctl constants for querying MMIO, framebuffer, and AGP aperture regions.

Important APIs and types: ioctl constants such as `FBIO_RADEON_GET_MIRROR`, `FBIO_RADEON_SET_MIRROR`, `FBIO_RADEON_GET_MMON`, and aperture/MMIO query values expose old radeonfb control hooks.

Control flow: legacy userspace opens a framebuffer device and issues Radeon-specific ioctls to query or change display/memory aperture behavior. Actual behavior is implemented by the radeonfb driver.

State and persistence: display mirror and aperture mappings are runtime device state; no persistent state is defined here.

Dependencies and integration points: integrates with fbdev, old Radeon hardware support, mmap users, and legacy display utilities.

Risks and test signals: risks include stale ABI for uncommon hardware, unsafe MMIO exposure, and conflicts with DRM/KMS drivers. Test only on radeonfb configurations: ioctl query/set behavior, mmap bounds, and coexistence exclusion with DRM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/radeonfb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/raid/md_p.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/raid/md_p.h

Purpose: defines Linux MD RAID persistent superblock formats, disk roles/states, feature bits, and helper macros used by mdadm and the kernel.

Important APIs and types: constants define reserved sectors, superblock sizes/word offsets, disk state bits, special disk roles, superblock magic, state bits, and feature-map bits. `mdp_disk_t` and `mdp_super_t` describe legacy 0.90 superblocks with endian-dependent event fields; `md_event()` reconstructs 64-bit event counters. `struct mdp_superblock_1` describes v1 little-endian superblocks, including array UUID/name, layout/chunk, reshape fields, offsets, device flags, bad-block log fields, event/resync state, and flexible `dev_roles[]`.

Control flow: mdadm and kernel MD code read component-device superblocks, validate magic/checksum/features, assemble arrays, select roles, track events, perform recovery/reshape, and write updated superblocks after state changes.

State and persistence: these structures are persistent on-disk RAID metadata. They encode array identity, geometry, events, resync/reshape checkpoints, per-device roles, bad block logs, write-intent bitmap/PPL/journal features, and clustered state.

Dependencies and integration points: depends on Linux endian/fixed types and host byte order for legacy layout. Integrates with MD RAID personalities, mdadm, boot auto-assembly, clustered MD, write-intent bitmaps, RAID reshape/recovery, and block-device metadata scanners.

Risks and test signals: high-risk areas are endian-specific legacy event fields, feature-bit compatibility, checksum coverage, flexible array sizing, reshape/backward/new-offset semantics, and data-loss from wrong roles. Test mdadm create/assemble/incremental, v0.90/v1.x superblocks, big-endian builds, reshape/recovery checkpoints, bad-block logs, PPL/journal features, clustered arrays, and corrupted metadata rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/raid/md_p.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/raid/md_u.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/raid/md_u.h

Purpose: defines the legacy MD RAID userspace ioctl ABI between raidtools/mdadm and kernel RAID drivers.

Important APIs and types: version constants describe major/minor/patchlevel compatibility. Ioctls cover status (`RAID_VERSION`, `GET_ARRAY_INFO`, `GET_DISK_INFO`, `GET_BITMAP_FILE`), configuration (`CLEAR_ARRAY`, `ADD_NEW_DISK`, `SET_ARRAY_INFO`, `SET_BITMAP_FILE`, hot add/remove/fault), and usage (`RUN_ARRAY`, `STOP_ARRAY`, `STOP_ARRAY_RO`, `RESTART_ARRAY_RW`, `CLUSTERED_DISK_NACK`). Payload structs include `mdu_version_t`, `mdu_array_info_t`, `mdu_disk_info_t`, `mdu_start_info_t`, `mdu_bitmap_file_t`, and `mdu_param_t`.

Control flow: management tools open an MD device and issue ioctls to inspect, configure, start, stop, or modify arrays. Kernel MD code mutates in-memory array/disk state and writes persistent metadata through lower layers.

State and persistence: ioctl-visible state includes array geometry, disk membership, active/failed/spare counts, layout, chunk size, bitmap file, and running/stopped state. Durable metadata is stored in MD superblocks or external metadata, not in this header.

Dependencies and integration points: depends on MD ioctl magic from surrounding RAID headers and integrates with MD core, mdadm, block devices, bitmaps, clustered MD, and RAID personalities.

Risks and test signals: risks include legacy ioctl compatibility, device-number assumptions, unsafe hot-remove/fault operations, stale bitmap paths, and mismatch between ioctl state and superblock metadata. Test mdadm ioctl paths, array start/stop/read-only transitions, disk add/remove/fault, bitmap file set/get, and version compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/raid/md_u.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/random.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/random.h

Purpose: defines the random-number generator userspace ABI for `/dev/random` ioctls, `getrandom(2)` flags, entropy pool injection, and vDSO/vgetrandom opaque-state allocation parameters.

Important APIs and types: ioctls include `RNDGETENTCNT`, `RNDADDTOENTCNT`, removed legacy `RNDGETPOOL`, `RNDADDENTROPY`, `RNDZAPENTCNT`, `RNDCLEARPOOL`, and `RNDRESEEDCRNG`. `struct rand_pool_info` carries entropy count, buffer size, and flexible input buffer. `GRND_NONBLOCK`, `GRND_RANDOM`, and `GRND_INSECURE` define `getrandom()` flags. `struct vgetrandom_opaque_params` describes opaque state size and mmap parameters.

Control flow: userspace reads random devices or calls `getrandom()`, optionally nonblocking or insecure. Privileged users can adjust entropy accounting, inject entropy, clear/reseed CRNG, or allocate vgetrandom state according to kernel-provided parameters.

State and persistence: RNG state is kernel CRNG/entropy-pool runtime state. Seed state may be initialized from boot and persistent seed files managed by userspace, but this header only defines the ABI.

Dependencies and integration points: depends on Linux types, ioctl, and IRQ number headers. Integrates with random core, libc, systemd/random-seed, cryptographic consumers, init systems, and vDSO getrandom support.

Risks and test signals: risks include entropy overclaiming, privileged ioctl misuse, blocking/nonblocking surprises, insecure flag misuse, and vgetrandom mmap parameter compatibility. Test early-boot getrandom behavior, entropy ioctls with/without privilege, reseed paths, invalid `rand_pool_info` lengths, and vgetrandom state allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/random.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rds.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/rds.h

Purpose: defines the Reliable Datagram Sockets userspace ABI for socket options, control messages, RDMA/atomic operations, zcopy completion, statistics, IPv4/IPv6 info structs, and receive-path latency tracing.

Important APIs and types: socket options include memory registration/freeing, receive errors, congestion monitoring, transport selection, and latency tracing. Control messages include RDMA args/dest/map/status, congestion updates, atomic fetch-add/compare-swap and masked variants, RX latency trace, zcopy cookie/completion. Info structs report counters, connections, messages, sockets, TCP sockets, IB/RDMA connections, and IPv6 variants. RDMA structs describe memory vectors, keys, flags, atomics, notifiers, and status.

Control flow: applications use `SOL_RDS` sockets, set options, send messages with cmsgs for RDMA/atomic/zcopy behavior, receive completions/errors/counters, and query diagnostic info. Kernel RDS transports over TCP/IB route datagrams, manage memory registrations, and update congestion/latency state.

State and persistence: state is runtime per socket, connection, transport, memory registration, congestion map, and message queue. No durable state is defined; RDMA keys and zcopy cookies are lifetime-bound.

Dependencies and integration points: depends on Linux socket, IPv6, and fixed types. Integrates with RDS core, TCP and InfiniBand transports, RDMA memory registration, Oracle/cluster applications, socket diagnostics, and poll/error queues.

Risks and test signals: risks include packed struct compatibility, RDMA key lifetime leaks, cmsg validation, IPv4/IPv6 divergence, atomic operation alignment, congestion wakeups, and zcopy completion loss. Test RDS TCP/IB send/recv, RDMA map/free/status, atomics, congestion monitor polling, recv error queue, IPv6 info queries, and malformed cmsgs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/reboot.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/reboot.h

Purpose: defines magic values and command constants for the `reboot(2)` system call.

Important APIs and types: `LINUX_REBOOT_MAGIC1`, `LINUX_REBOOT_MAGIC2*` authenticate reboot calls. Command constants include restart, halt, CAD on/off, power off, restart2, software suspend, and kexec.

Control flow: privileged userspace calls `reboot(magic1, magic2, cmd, arg)`; the kernel validates magic values and capability, then dispatches to restart, halt, poweroff, CAD state change, kexec, or suspend logic.

State and persistence: reboot commands affect global system power/restart state. CAD setting and kexec image state are runtime; reboot/poweroff changes platform state and terminates current kernel state.

Dependencies and integration points: integrates with sys_reboot, init systems, kexec, hibernation, architecture restart/poweroff handlers, and watchdog/power-management code.

Risks and test signals: risks include accidental destructive reboot, wrong magic compatibility, privilege bypass, and command-specific arch/platform behavior. Test command validation, capability checks, restart2 argument handling, kexec loaded/unloaded paths, and CAD toggling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/reboot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/remoteproc_cdev.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/remoteproc_cdev.h

Purpose: defines the remoteproc character-device ioctl ABI for controlling whether a remote processor is automatically shut down when a controlling userspace file descriptor is closed.

Important APIs and types: `RPROC_MAGIC` is the ioctl magic. `RPROC_SET_SHUTDOWN_ON_RELEASE` accepts an `__s32` where zero disables automatic shutdown and nonzero enables it. `RPROC_GET_SHUTDOWN_ON_RELEASE` returns the current setting as an `__s32`.

Control flow: userspace opens a remoteproc cdev and sets or queries the shutdown-on-release policy. When the file is later closed, remoteproc cdev code uses that policy to decide whether the remote processor should be shut down automatically.

State and persistence: the exposed state is a runtime per-cdev control flag. It affects remote processor lifetime on close but is not durable across driver reset or reboot.

Dependencies and integration points: integrates with remoteproc core, firmware_class, rpmsg/virtio, SoC-specific remote processor drivers, and administrative tooling.

Risks and test signals: risks include accidentally stopping critical co-processors when the last controller closes, inconsistent policy across multiple opens, and permission-policy mistakes. Test set/get round trips, close behavior with shutdown enabled and disabled, multiple file descriptors, remoteproc removal while open, and permission checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/remoteproc_cdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/resource.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/resource.h

Purpose: defines generic resource-limit, resource-usage, and priority constants plus common `rusage`/`rlimit` structures for userspace resource accounting APIs.

Important APIs and types: `struct rusage` carries CPU time, RSS, page fault, block I/O, IPC, signal, and context-switch counters. `struct rlimit` and `struct rlimit64` carry soft/hard limits, with `RLIM64_INFINITY` as the 64-bit infinite value. Priority constants include `PRIO_MIN`, `PRIO_MAX`, and `PRIO_PROCESS/PGRP/USER`. `RUSAGE_SELF`, `RUSAGE_CHILDREN`, `RUSAGE_BOTH`, and `RUSAGE_THREAD` select usage scopes. `_STK_LIM` and `MLOCK_LIMIT` define default stack and locked-memory limits; `asm/resource.h` supplies architecture resource numbers and remaining limit constants.

Control flow: userspace calls `getpriority/setpriority`, `getrusage`, `getrlimit/setrlimit/prlimit64`; the kernel applies these constants to select target process/user/group or usage/limit scope.

State and persistence: resource limits are per process/credential state inherited across fork and usually preserved across exec. Usage counters accumulate per task/thread/process tree runtime state.

Dependencies and integration points: depends on arch UAPI `asm/resource.h`. Integrates with scheduler priority, signal/accounting, process resource limits, libc, shells, and container runtimes.

Risks and test signals: risks include architecture layout drift, signed priority range mistakes, inheritance semantics, and container/user namespace limit enforcement. Test get/set priority, rusage scopes, rlimit inheritance, prlimit permission checks, and cross-arch header exports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rfkill.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/rfkill.h

Purpose: defines the `/dev/rfkill` userspace event/control ABI for radio kill switches and wireless device block state.

Important APIs and types: state constants distinguish soft-blocked, unblocked, and hard-blocked. `enum rfkill_type` lists WLAN, Bluetooth, UWB, WiMAX, WWAN, GPS, FM, NFC, and all-types requests. `enum rfkill_operation` identifies add/delete/change/change-all. `enum rfkill_hard_block_reasons` identifies hardware signal and host-ownership reasons. `struct rfkill_event` is the legacy packed event, and `struct rfkill_event_ext` adds hard-block reasons. Ioctls disable rfkill-input and opt into a maximum event size.

Control flow: userspace reads events from `/dev/rfkill`, writes change requests, and can request extended event size. The kernel emits add/delete/change records and applies soft-block changes, while hard-block state follows hardware/firmware ownership.

State and persistence: rfkill state is runtime per device plus default state for hotplugged devices after change-all. Soft block may be policy-managed by userspace; hard block is hardware/firmware state.

Dependencies and integration points: depends on Linux types. Integrates with wireless, Bluetooth, platform hotkey drivers, NetworkManager/systemd/BlueZ, and input rfkill handling.

Risks and test signals: risks include event struct extensibility breakage, short read/write handling, default state surprises, hard-block reason opt-in, and policy races among managers. Test legacy and extended event sizes, add/change/delete events, change-all defaults, hard block reasons, `RFKILL_IOCTL_MAX_SIZE`, and old userspace compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rfkill.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rio_cm_cdev.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/rio_cm_cdev.h

Purpose: defines the RapidIO channelized messaging character-device ABI for endpoint discovery, channel lifecycle, connection management, and message send/receive.

Important APIs and types: `struct rio_cm_channel` carries local/remote channel IDs, remote destination ID, and mport ID. `struct rio_cm_msg` carries channel number, message size, receive timeout, and userspace message pointer. `struct rio_cm_accept` carries channel number and accept timeout. Ioctls include endpoint list size/list, channel create/close/bind/listen/accept/connect, send/receive, and mport list.

Control flow: userspace discovers endpoints/mports, creates and binds a channel, listens/accepts or connects to a remote channel, then sends/receives messages with optional blocking timeouts. The kernel RapidIO CM driver manages channel state and routes messages over RapidIO.

State and persistence: state is runtime per channel and endpoint: bindings, listen/connect state, remote IDs, queues, and timeouts. No durable state is defined.

Dependencies and integration points: depends on Linux types/ioctl and integrates with RapidIO subsystem, mport devices, endpoint discovery, and user messaging applications.

Risks and test signals: risks include user pointer validation for message buffers, timeout semantics, channel ID reuse, remote disconnect handling, and endpoint list races. Test create/bind/listen/connect/accept, send/receive with blocking and timeout, endpoint hotplug, invalid sizes, and close during pending receive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rio_cm_cdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rio_mport_cdev.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/rio_mport_cdev.h

Purpose: defines the RapidIO master-port character-device ABI for mport discovery, device enumeration, maintenance reads/writes, doorbells, port-write events, memory mapping, DMA allocation, DMA transfers, and dynamic device add/delete.

Important APIs and types: structures describe device info, component tags, network IDs, maintenance operations, events, doorbells, port-write filters, memory mappings, DMA memory, transfer sync/async descriptors, wait tokens, and transactions. Ioctls include `RIO_MPORT_GET_PROPERTIES`, `RIO_MPORT_MAINT_{HDID,COMPTAG,PORT_IDX,READ_LOCAL,WRITE_LOCAL,READ_REMOTE,WRITE_REMOTE}`, event enable/disable, doorbell/portwrite receive/send, outbound/inbound map/unmap, DMA alloc/free, transfer, async wait, and device add/delete.

Control flow: userspace opens an mport cdev, queries properties, performs maintenance transactions to local or remote RapidIO devices, enables events, exchanges doorbells/port-writes, maps RapidIO address windows, allocates DMA memory, submits transfers, waits for async completion, and may add/delete remote device records.

State and persistence: runtime state includes mport properties, enabled event masks, mapping windows, allocated DMA buffers, outstanding transactions, async tokens, and discovered remote devices. Hardware fabric configuration may persist outside the Linux driver, but cdev state is runtime.

Dependencies and integration points: depends on Linux types/ioctl and integrates with RapidIO core, mport drivers, DMA mapping, event queues, maintenance transaction routing, and fabric management tools.

Risks and test signals: high-risk areas are DMA address validation, map/unmap lifetime, async completion token reuse, remote maintenance fault handling, event queue overflow, and privileged fabric mutation. Test property queries, local/remote maintenance access, doorbell/portwrite events, inbound/outbound mapping lifecycle, DMA alloc/free/transfer sync and async, invalid remote IDs, and device add/delete races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rio_mport_cdev.h -->
