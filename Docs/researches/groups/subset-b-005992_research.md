# Research: subset-b-005992

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rkisp1-config.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/rkisp1-config.h

Purpose: defines the Rockchip ISP1 userspace ABI for V4L2 metadata buffers that configure ISP processing blocks and return statistics. It covers the older monolithic `rkisp1_params_cfg` layout, the statistics buffer, and the newer extensible V4L2 ISP parameter-block format used to pass typed, aligned blocks.

Important APIs, types, and functions: exported module masks include `RKISP1_CIF_ISP_MODULE_*` for DPCC, BLS, SDG, HST, LSC, AWB gain/measure, FLT, BDM, CTK, GOC, CPROC, AFC, AEC, IE, WDR, DPF, and DPF strength. Core configuration structs include `rkisp1_cif_isp_bls_config`, `rkisp1_cif_isp_dpcc_config`, `rkisp1_cif_isp_sdg_config`, `rkisp1_cif_isp_lsc_config`, `rkisp1_cif_isp_awb_gain_config`, `rkisp1_cif_isp_flt_config`, `rkisp1_cif_isp_ctk_config`, `rkisp1_cif_isp_goc_config`, `rkisp1_cif_isp_dpf_config`, compand/WDR structs, and `rkisp1_params_cfg`. Statistics are returned through `rkisp1_stat_buffer`, `rkisp1_cif_isp_stat`, AWB/AE/AF/histogram substructures, and version-dependent maximum arrays. The extensible ABI uses `rkisp1_ext_params_block_type`, `rkisp1_ext_params_block_header`, one typed `rkisp1_ext_params_*_config` wrapper per block, `RKISP1_EXT_PARAMS_MAX_SIZE`, `RKISP1_CID_SUPPORTED_PARAMS_BLOCKS`, and `rkisp1_ext_params_cfg`.

Control flow: userspace discovers the media device and hardware revision, prepares a params metadata buffer, sets update masks for legacy layout or fills a versioned extensible buffer with typed blocks, then queues it to the params video node. The driver validates block sizes, enable/disable flags, module support, and revision-dependent array lengths before programming hardware registers for the next frame. Statistics travel in the reverse direction from ISP hardware to a stats metadata buffer tagged with `meas_type` and `frame_id`.

State and persistence behavior: this header owns no kernel state; it defines copy-to/from-userspace layouts. Effective state lives per queued video buffer, per ISP device, and in hardware registers until a later buffer updates them. Frame statistics are transient snapshots; controls such as `RKISP1_CID_SUPPORTED_PARAMS_BLOCKS` expose immutable or driver-instance capability state. The kernel-only `static_assert` guards the relationship between the driver-specific extensible buffer header and generic V4L2 ISP params buffer.

Dependencies and integration points: depends on fixed-width Linux UAPI types and `linux/media/v4l2-isp.h`. It integrates with V4L2 mem2mem/meta buffer queues, the media controller hardware-revision discovery path, Rockchip ISP1 driver register programming, image-tuning userspace, and generic V4L2 ISP parameter-block helpers.

Risks and edge cases: ABI risk is high because arrays are sized to maximum V12 capabilities even when V10 hardware uses fewer entries. Userspace must not assume every block in `RKISP1_EXT_PARAMS_MAX_SIZE` is supported by a given device. Alignment of extensible blocks, signed fixed-point fields, reserved/unknown compand fields, module mask synchronization, and duplicate legacy/extensible ways to express the same blocks are common drift points.

Test signals: compile-test UAPI size/alignment, run v4l2-compliance for params and stats nodes, queue legacy and extensible buffers on V10 and V12-style devices, verify rejected oversized or unsupported blocks, compare frame IDs between params and stats, and exercise boundary values for BLS, LSC tables, gamma/histogram arrays, WDR curves, and DPF coefficients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rkisp1-config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/romfs_fs.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/romfs_fs.h

Purpose: describes the on-disk ROMFS filesystem superblock and inode layouts plus constants used by kernel and tooling that parse or create ROMFS images.

Important APIs, types, and functions: `ROMBSIZE`, `ROMBSBITS`, and `ROMBMASK` map ROMFS block alignment to Linux block size definitions. `ROMFS_MAGIC`, `ROMSB_WORD0`, and `ROMSB_WORD1` identify the `-rom1fs-` magic words in big-endian form. `struct romfs_super_block` contains magic words, image size, checksum, and a flexible volume name. `struct romfs_inode` contains next inode pointer/type bits, device/spec data, file size, checksum, and a flexible name. `ROMFH_*` constants encode inode type and execute flag in the low bits of `next`; `ROMFH_SIZE`, `ROMFH_PAD`, and `ROMFH_MASK` define 16-byte alignment.

Control flow: the ROMFS mount/parser path reads the superblock, validates magic and checksum, walks inode records using the aligned `next` field, decodes the low type bits with `ROMFH_TYPE`, and interprets `spec`/`size` according to hardlink, directory, regular, symlink, block, char, socket, or FIFO type.

State and persistence behavior: all represented state is persistent image data. The header has no functions and no runtime state. The flexible array members mean callers must treat the fixed struct as a prefix and bounds-check volume/file names against image size and alignment.

Dependencies and integration points: depends on `linux/types.h` for big-endian integer types and `linux/fs.h` for block-size constants. It integrates with the ROMFS filesystem driver and image creation/inspection tools that need exact disk-format compatibility.

Risks and edge cases: name and inode records are variable length and alignment-sensitive. Endianness must be honored; `__mk4` builds big-endian constants. The low bits of `next` carry type flags, so code must mask before following offsets. Corrupt checksums, unterminated names, and offsets outside image size are the main parser risks.

Test signals: mount known-good ROMFS images, fuzz superblock/inode lengths and checksums, validate big-endian decoding on little-endian hosts, test every `ROMFH_*` type, and compare mkromfs output with kernel mount traversal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/romfs_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/route.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/route.h

Purpose: preserves the legacy IPv4 route ioctl ABI used by `SIOCADDRT` and `SIOCDELRT`, predating rtnetlink.

Important APIs, types, and functions: `struct rtentry` carries destination, gateway, netmask, flags, metric, optional device pointer, MTU/MSS, window, and initial RTT. Route flags include `RTF_UP`, `RTF_GATEWAY`, `RTF_HOST`, `RTF_DYNAMIC`, `RTF_MODIFIED`, `RTF_MTU`, `RTF_WINDOW`, `RTF_IRTT`, and `RTF_REJECT`; `rt_mss` aliases `rt_mtu` for userspace compatibility.

Control flow: legacy route tools fill `struct rtentry` and issue socket ioctls. The kernel copies the structure, resolves the optional device name from `rt_dev`, decodes flags and socket addresses, then adds or deletes an IPv4 route through compatibility glue.

State and persistence behavior: the header stores no state. Routes created through this ABI become kernel FIB state like routes created through rtnetlink, but the ioctl representation is a lossy legacy interface.

Dependencies and integration points: includes `linux/if.h` for `struct sockaddr` use and `linux/compiler.h` for `__user`. It integrates with IPv4 route ioctl handling and old net-tools-style programs.

Risks and edge cases: pointer-sized fields make the ABI architecture-sensitive. `rt_metric` has historical “+1” semantics, `rt_dev` is a userspace pointer, and flags overlap conceptually with newer rtnetlink route attributes. IPv6 uses route flag values above 64k, so flag expansion must avoid collisions.

Test signals: exercise add/delete of host, network, gateway, reject, MTU, window, and IRTT routes through ioctl on 32- and 64-bit builds; compare resulting FIB entries to rtnetlink dumps; validate bad `rt_dev` pointers and malformed sockaddr families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/route.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rpl.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/rpl.h

Purpose: defines the IPv6 RPL source-routing header layout exported to userspace and tunnel code.

Important APIs, types, and functions: `struct ipv6_rpl_sr_hdr` contains IPv6 extension-header fields, RPL compression fields `cmpri`/`cmpre`, padding/reserved bits with endian-specific bitfields, and a flexible union of IPv6 segment addresses or raw data. `rpl_segaddr` and `rpl_segdata` are compatibility aliases.

Control flow: packet creation or parsing code reads the fixed header, uses `hdrlen` and compression fields to determine segment encoding, and then consumes the flexible segment area as either full addresses or compressed bytes.

State and persistence behavior: state is packet wire data only. The packed struct does not own storage and must be used with validated skb or userspace buffers.

Dependencies and integration points: includes byteorder definitions, `linux/types.h`, and IPv6 address definitions. It integrates with IPv6 RPL source-routing, lightweight tunnel encapsulation, and packet parsers.

Risks and edge cases: bitfield order differs by endian and the struct is packed. Callers must validate `hdrlen`, `segments_left`, compression nibble values, and flexible-array bounds before dereferencing segment data.

Test signals: parse and emit RPL SRH packets on big- and little-endian builds, test compressed and uncompressed segment lists, fuzz `hdrlen` and compression fields, and verify tunnel encapsulation size calculations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rpl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rpl_iptunnel.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/rpl_iptunnel.h

Purpose: provides netlink attribute IDs and a size helper for RPL source-routing IPv6 tunnel encapsulation.

Important APIs, types, and functions: the anonymous enum exports `RPL_IPTUNNEL_UNSPEC`, `RPL_IPTUNNEL_SRH`, and `RPL_IPTUNNEL_MAX`. `RPL_IPTUNNEL_SRH_SIZE(srh)` computes the byte size of an RPL SRH from `hdrlen`.

Control flow: userspace sends a tunnel attribute carrying an RPL SRH. Kernel tunnel code validates the attribute, uses the size macro to copy or compare the header length, and attaches it to the tunnel encap state.

State and persistence behavior: no state is held here. Tunnel state lives in route/lwtunnel configuration and includes the serialized SRH payload.

Dependencies and integration points: integrates with `rpl.h`, IPv6 lwtunnel netlink parsing, route encap attributes, and iproute2 tunnel configuration.

Risks and edge cases: `hdrlen` must be trusted only after the containing attribute length is checked. A malformed header can make the size macro exceed provided bytes.

Test signals: create RPL tunnel routes with valid and invalid SRH attributes, verify netlink policy rejects short payloads, and check that route dumps preserve the SRH bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rpl_iptunnel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rpmsg.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/rpmsg.h

Purpose: defines the rpmsg character-device ioctl ABI for creating, destroying, and flow-controlling remote-processor messaging endpoints and local service devices.

Important APIs, types, and functions: `RPMSG_ADDR_ANY` marks wildcard addresses. `struct rpmsg_endpoint_info` carries a 32-byte service name plus source and destination addresses. Ioctls include `RPMSG_CREATE_EPT_IOCTL`, `RPMSG_DESTROY_EPT_IOCTL`, `RPMSG_CREATE_DEV_IOCTL`, `RPMSG_RELEASE_DEV_IOCTL`, `RPMSG_GET_OUTGOING_FLOWCONTROL`, and `RPMSG_SET_INCOMING_FLOWCONTROL`.

Control flow: userspace opens an rpmsg control or endpoint character device, issues create ioctls with endpoint info, exchanges data through the resulting device, optionally queries or sets flow-control state, and destroys/releases endpoints when done.

State and persistence behavior: the header is declarative. Runtime endpoint state lives in rpmsg core, virtio/remoteproc transport state, and character-device instances. Created endpoints persist until destroyed, released, or the remote processor/device goes away.

Dependencies and integration points: depends on Linux ioctl and fixed-width type headers. It integrates with rpmsg char drivers, remoteproc, virtio rpmsg, and userspace services communicating with remote firmware.

Risks and edge cases: service names are fixed-size and may not be NUL-terminated if userspace fills all bytes. Address wildcarding, endpoint lifetime after remoteproc reset, and ioctl direction correctness for flow-control integers require care.

Test signals: create/destroy endpoints with wildcard and fixed addresses, test overlong/non-terminated names, reset the remote processor while endpoints are open, exercise flow-control ioctls, and verify data path error returns after teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rpmsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rpmsg_types.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/rpmsg_types.h

Purpose: provides bitwise-annotated rpmsg integer typedefs for protocol fields whose endian or transport representation should not be mixed with normal integers.

Important APIs, types, and functions: `__rpmsg16`, `__rpmsg32`, and `__rpmsg64` are `__bitwise` wrappers over `__u16`, `__u32`, and `__u64`.

Control flow: rpmsg protocol headers and transports use these typedefs so sparse and reviewers can catch accidental mixing of raw CPU integers and rpmsg-formatted fields.

State and persistence behavior: no state exists here; the typedefs affect compile-time type checking.

Dependencies and integration points: depends on `linux/types.h` and integrates with rpmsg core/protocol headers that need annotated fields.

Risks and edge cases: the annotations only help when sparse or compatible checking is used. They do not encode conversion semantics by themselves, so callers must still use the proper endian/format helpers.

Test signals: sparse builds should report bad assignments, while normal builds should compile protocol structs using the annotated aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rpmsg_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rseq.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/rseq.h

Purpose: defines the restartable sequences syscall ABI shared between the kernel and C libraries for per-thread, userspace-managed critical sections that abort on migration, signal, or preemption.

Important APIs, types, and functions: enums define special CPU ID states, `RSEQ_FLAG_UNREGISTER`, and critical-section feature/status bits. `struct rseq_cs` describes a critical section by version, flags, start IP, post-commit offset, and abort IP with cacheline alignment. `struct rseq` is the per-thread registered area containing CPU IDs, active `rseq_cs` pointer, feature flags, NUMA node ID, memory-map concurrency ID, `rseq_slice_ctrl`, reserved feature byte, and flexible end marker.

Control flow: userspace allocates an aligned `struct rseq`, registers it with the `rseq` syscall, updates `rseq_cs` before entering assembly critical sections, verifies CPU ID fields before commit, and unregisters when a thread exits or disables rseq. The kernel updates CPU, node, mm_cid, flags, and slice-control state, and clears/redirects active critical sections on abort events.

State and persistence behavior: state is per-thread userspace memory registered with the kernel. It is not persistent across process lifetime, and a thread may have only one active registration. The extensible area size and alignment are advertised by auxv but remain backward-compatible with the original 32-byte allocation.

Dependencies and integration points: depends on Linux types and byteorder headers. It integrates with the `rseq` syscall, libc TLS setup, sched/migration paths, signal delivery, restartable sequence assembly, and userspace allocators or per-CPU data structures.

Risks and edge cases: alignment and feature-size handling are critical. Userspace must not reclaim active `rseq_cs` memory without clearing the pointer. Unsupported historical no-restart flags must remain false. 32-bit architectures must write the low bits of `rseq_cs` consistently. Feature growth must preserve old 32-byte behavior.

Test signals: libc registration tests, migration/preemption/signal abort tests, auxv size/alignment handling, unregister paths, 32-bit compat builds, mm_cid/node_id correctness, and stress tests with per-CPU counters under CPU hotplug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rseq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rtc.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/rtc.h

Purpose: defines the generic `/dev/rtc` userspace ABI for reading and setting RTC time, alarms, periodic interrupts, PLL correction, voltage-low status, feature flags, and device parameters.

Important APIs, types, and functions: `struct rtc_time` mirrors broken-down calendar time. `struct rtc_wkalrm` carries alarm enable/pending state and time. `struct rtc_pll_info` describes clock correction capabilities. `struct rtc_param` is a generic indexed parameter container. Ioctls include alarm/update/periodic/watchdog interrupt toggles, `RTC_ALM_SET/READ`, `RTC_RD_TIME`, `RTC_SET_TIME`, `RTC_IRQP_READ/SET`, epoch, wake alarm, PLL, parameter, and voltage-low operations. Constants define IRQ flags, feature IDs, parameter IDs, backup-switch modes, voltage flags, and `RTC_MAX_FREQ`.

Control flow: userspace opens an RTC character device, issues ioctl reads/writes for time and alarm state, optionally enables interrupts and reads interrupt flags from the device, queries feature bitmaps through parameters, and clears voltage-low flags after inspection.

State and persistence behavior: time, alarm, correction, and voltage status live in RTC hardware and driver state, often backed by battery power. Parameter and feature values may be static capabilities or runtime settings. The header itself owns no state.

Dependencies and integration points: depends on const, ioctl, and fixed-width type UAPI headers. It integrates with RTC class drivers, wakeup alarm infrastructure, poll/read interrupt delivery, and time-setting tools.

Risks and edge cases: calendar fields follow `struct tm` conventions and need range validation. Some ioctl command numbers overlap historically (`RTC_WIE_*` with wake alarm, parameter with voltage-low), so driver dispatch must disambiguate by command encoding. Not all RTCs support every feature or high interrupt rates.

Test signals: read/set time round trips, alarm wakeup behavior, periodic/update/alarm interrupts, unsupported ioctl returns, voltage-low flag read/clear, feature bitmap queries, backup-switch modes, and boundary calendar values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rtc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rtnetlink.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/rtnetlink.h

Purpose: defines the core rtnetlink ABI for network link, address, route, neighbor, rule, traffic-control, multicast, nexthop, VLAN, tunnel, and stats messages.

Important APIs, types, and functions: message IDs span `RTM_NEWLINK` through `RTM_GETTUNNEL`; `RTM_NR_MSGTYPES`, `RTM_NR_FAMILIES`, and `RTM_FAM` classify them. `struct rtattr` plus `RTA_*` macros define generic netlink attributes. Route ABI types include `struct rtmsg`, `rt_scope_t`, `rt_class_t`, `rtattr_type_t`, `struct rtnexthop`, `struct rtvia`, `struct rta_cacheinfo`, `RTAX_*` metrics, `struct rta_session`, and multicast stats. Link and TC messages use `struct ifinfomsg`, `prefixmsg`, `tcmsg`, `nduseroptmsg`, `tcamsg`, and TCA/TA access macros. Multicast subscriptions are exported as legacy `RTMGRP_*` masks and modern `enum rtnetlink_groups`.

Control flow: userspace sends netlink messages with an nlmsghdr type in the RTM range, a fixed family-specific struct payload, and a stream of aligned `rtattr` TLVs. The kernel validates lengths with `RTA_OK`/`RTNH_OK`, applies requested mutations or dumps state, and multicasts notifications to rtnetlink groups.

State and persistence behavior: this header has no storage. It serializes mutable kernel networking state: links, addresses, routes, rules, qdiscs/classes/filters/actions, nexthops, multicast DBs, namespaces, tunnels, and statistics. Route attributes may carry cached expiry and counters.

Dependencies and integration points: depends on netlink, link, address, and neighbor UAPI headers. It integrates with iproute2, routing daemons, traffic-control tools, namespace management, kernel FIB/neighbour/link subsystems, and rtnetlink multicast listeners.

Risks and edge cases: ABI compatibility is paramount. Attribute and nexthop parsing must enforce alignment and length. Deprecated values remain visible, legacy group masks differ from modern group IDs, route protocol/table IDs are shared with userspace daemons, and variable-length multipath/encap attributes are common bug sources.

Test signals: netlink selftests and iproute2 round trips for links, addresses, routes, rules, qdiscs, actions, nexthops, VLANs, and tunnels; fuzz malformed attributes; verify multicast notifications; test route dumps with metrics, multipath, encap, offload/trap flags, and strict length checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rtnetlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rxrpc.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/rxrpc.h

Purpose: defines the AF_RXRPC socket ABI, including sockaddr layout, socket options, control messages, security levels/indices, abort codes, and challenge payloads.

Important APIs, types, and functions: `struct sockaddr_rxrpc` wraps an RxRPC service ID and an IPv4/IPv6 datagram transport address. Socket options include `RXRPC_SECURITY_KEY`, `RXRPC_SECURITY_KEYRING`, `RXRPC_MIN_SECURITY_LEVEL`, service upgrade, supported-cmsg discovery, and managed response. `enum rxrpc_cmsg_type` defines sendmsg/recvmsg control messages such as `RXRPC_USER_CALL_ID`, `RXRPC_ABORT`, `RXRPC_ACK`, `RXRPC_NEW_CALL`, exclusive call, timeouts, challenge/response, and appdata. Security constants cover plain/auth/encrypt levels and RXKAD/RXGK/RXK5/YFS indices. Abort codes cover local RxRPC, rxgen, RXKAD, and RXGK failures. `struct rxrpc_challenge` and `rxgk_challenge` describe challenge metadata.

Control flow: userspace binds or connects AF_RXRPC sockets with `sockaddr_rxrpc`, configures security material with socket options, uses control messages to identify calls and manage call lifecycle, receives terminal ACK/abort/error notifications, and may respond to security challenges when managed response is enabled.

State and persistence behavior: call, connection, key, timeout, and service-upgrade state lives in AF_RXRPC sockets and kernel keyrings. User call IDs are application-owned tags that can be recycled after terminal messages. This header only defines the ABI.

Dependencies and integration points: includes Linux types and IPv4/IPv6 address headers. It integrates with AF_RXRPC, keyrings, Kerberos/RXKAD/RXGK security, AFS/YFS filesystems, and sendmsg/recvmsg cmsg handling.

Risks and edge cases: control-message applicability differs for client/server and send/receive paths. Terminal messages affect user call ID reuse. Security abort code compatibility with OpenAFS/YFS matters. Variable security-class challenge data follows fixed challenge prefixes, so bounds validation is required.

Test signals: AF_RXRPC client/server calls with no security, RXKAD, and RXGK; cmsg parsing for user call IDs and aborts; service upgrade; managed challenge/response; timeout notifications; IPv4 and IPv6 transports; and malformed cmsg length tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rxrpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sched.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/sched.h

Purpose: defines process creation, namespace, clone3, and scheduler policy/flag UAPI constants.

Important APIs, types, and functions: clone flags include traditional `CLONE_*` bits for VM, FS, files, signal handlers, pidfd, vfork, parent, thread, namespaces, TLS, TID pointers, cgroups, IO, and `CLONE_NEWTIME`. Clone3-only flags include `CLONE_CLEAR_SIGHAND`, `CLONE_INTO_CGROUP`, `CLONE_AUTOREAP`, `CLONE_NNP`, `CLONE_PIDFD_AUTOKILL`, and `CLONE_EMPTY_MNTNS`. `struct clone_args` is the extensible clone3 argument block with aligned 64-bit fields. Scheduler constants define normal, FIFO, RR, batch, idle, deadline, and ext policies plus `SCHED_RESET_ON_FORK` and sched_attr flag masks.

Control flow: libc or container runtimes pass legacy clone flags or `struct clone_args` to the kernel. The kernel validates flag combinations, creates processes/threads/namespaces/cgroup membership, and later scheduler syscalls use policy and flag constants to update task scheduling behavior.

State and persistence behavior: process, namespace, pidfd, cgroup, signal, VM, and scheduler state live in task structures. `clone_args` is copied at syscall entry and versioned by size constants, allowing extension without breaking old userspace.

Dependencies and integration points: depends on Linux fixed-width types. It integrates with `clone`, `clone3`, `unshare`, sched_setattr/getattr, pidfds, namespaces, cgroups, and process supervisors.

Risks and edge cases: clone flags overlap with exit-signal low bits and some bits are syscall-specific. New `clone_args` fields must be appended and 64-bit aligned. Invalid combinations such as thread without shared signal semantics or namespace constraints must be rejected by syscall code.

Test signals: clone3 size-version tests, pidfd and cgroup cloning, namespace creation, invalid flag combination selftests, scheduler flag validation, and compatibility tests for legacy clone/unshare bit overlap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sched.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sched/types.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/sched/types.h

Purpose: defines the extensible `sched_attr` structure used by `sched_setattr` and `sched_getattr` to pass scheduler policy, realtime priority, deadline parameters, and utilization hints.

Important APIs, types, and functions: `SCHED_ATTR_SIZE_VER0` and `SCHED_ATTR_SIZE_VER1` record ABI growth. `struct sched_attr` includes `size`, `sched_policy`, `sched_flags`, nice value, realtime priority, deadline runtime/deadline/period, and utilization clamp min/max.

Control flow: userspace fills `sched_attr` with a size value and calls scheduler attribute syscalls. The kernel copies only the advertised size, validates flags and fields for the selected policy, applies scheduling-class parameters, and reports supported fields through `sched_getattr`.

State and persistence behavior: task scheduling state persists in kernel task structures until changed or reset on fork according to flags. The struct is a transient syscall payload.

Dependencies and integration points: depends on `linux/types.h` and integrates with `sched.h` policy/flag constants, deadline scheduling, realtime scheduling, CFS nice values, and utilization clamping.

Risks and edge cases: ABI extension requires append-only fields and correct `size` handling. Utilization hints use scheduler capacity units and can be reset with special values documented outside the struct. Deadline fields need nonzero and ordered runtime/deadline/period validation.

Test signals: sched_setattr/getattr selftests for every size version, deadline policy boundary checks, utilization clamp flags, reset-on-fork behavior, and invalid size/flag combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sched/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/scif_ioctl.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/scif_ioctl.h

Purpose: defines the Intel SCIF character-device ioctl ABI for connecting MIC endpoints, sending messages, registering memory windows, performing remote copies, and using fences.

Important APIs, types, and functions: endpoint identity is `struct scif_port_id`. Ioctl payloads include `scifioctl_connect`, `scifioctl_accept`, `scifioctl_msg`, `scifioctl_reg`, `scifioctl_unreg`, `scifioctl_copy`, `scifioctl_fence_mark`, `scifioctl_fence_signal`, and `scifioctl_node_ids`. Ioctl commands range from `SCIF_BIND`, `SCIF_LISTEN`, `SCIF_CONNECT`, and `SCIF_ACCEPT*` through send/recv, memory registration, read/write, vector read/write, node discovery, and fence operations.

Control flow: userspace opens a SCIF endpoint, binds/listens or connects to a node/port, exchanges messages, registers local memory ranges, performs local/remote offset-based copies or virtual copies, and synchronizes DMA visibility with fences.

State and persistence behavior: endpoint connection state, registered windows, fence marks, and DMA mappings live in the SCIF driver and hardware/peer state. The ioctl structs are transient copy_from_user/copy_to_user payloads carrying user addresses as `__u64`.

Dependencies and integration points: depends on fixed-width Linux types and ioctl command macros from included kernel headers. It integrates with Intel MIC/MPSS SCIF drivers, DMA mapping, file descriptor endpoint lifetimes, and node topology discovery.

Risks and edge cases: all user pointers are encoded as 64-bit integers, so compat handling must be explicit. Offset/length overflow, stale remote registrations, fence pointer validity, endpoint teardown during DMA, and blocking accept/recv semantics are high-risk areas.

Test signals: connect/listen/accept pairs, send/recv length accounting, registration/unregistration bounds, DMA copy to/from remote windows, vector copy, fence mark/wait/signal, node discovery, invalid user addresses, and disconnect during active operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/scif_ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/screen_info.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/screen_info.h

Purpose: exports boot-time screen and framebuffer metadata used by architecture setup code, early consoles, and framebuffer drivers.

Important APIs, types, and functions: `struct screen_info` carries text-mode cursor and geometry, video page/mode, width/height/depth, framebuffer base and size, line length, capabilities, ext_lfb_base for 64-bit addresses, and EFI/VESA-related fields. Constants define legacy video types such as MDA, CGA, EGA/VGA, VESA LFB, architecture-specific framebuffers, EFI, video flags, and capability bits.

Control flow: boot loaders or firmware fill the structure before or during kernel entry. Early console and framebuffer initialization read it to choose text/video mode, locate the framebuffer, and decide whether quirks or 64-bit base handling are needed.

State and persistence behavior: the structure is boot-time state that becomes kernel global/arch state; it does not represent persistent storage. Values are often trusted early before full driver probing.

Dependencies and integration points: depends on Linux types and integrates with x86/EFI/VESA boot protocols, early printk/console, simplefb/efifb-like framebuffer setup, and platform video quirks.

Risks and edge cases: firmware may supply inconsistent dimensions, line length, depth, or framebuffer base. 64-bit base addresses require capability handling. Early consumers must avoid mapping invalid physical addresses or assuming text-mode fields are meaningful in graphics modes.

Test signals: boot with EFI framebuffer, VESA LFB, legacy VGA text, and no framebuffer; verify 64-bit framebuffer base, video type selection, line length/depth, and quirk skip behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/screen_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sctp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/sctp.h

Purpose: defines the Linux SCTP sockets API extension: socket option numbers, ancillary data structures, notification events, association/address/query structs, PR-SCTP, authentication, stream reset/reconfiguration, UDP encapsulation, and scheduler controls.

Important APIs, types, and functions: `sctp_assoc_t` identifies associations. Socket options include public SCTP options, internal bindx/connectx/peeloff helpers, PR-SCTP, stream reset, event subscription, ASCONF/AUTH/ECN exposure, UDP encapsulation, and PLPMTUD probe interval. Ancillary structs include `sctp_initmsg`, `sctp_sndrcvinfo`, `sctp_sndinfo`, `sctp_rcvinfo`, `sctp_nxtinfo`, `sctp_prinfo`, and `sctp_authinfo`. Notification structs include association, peer address, remote error, send failed, shutdown, adaptation, partial delivery, auth key, sender dry, stream reset, association reset, and stream change events, unified by `union sctp_notification`. Query/control structs cover RTO, association params, primary addresses, peer address params/info, authentication chunks/keys, SACK info, status, addresses, association stats, PR status/defaults, `sctp_info`, stream add/reset, event toggle, UDP encapsulation, scheduler type, and probe interval.

Control flow: applications configure an SCTP socket with setsockopt, send messages with SCTP cmsgs, receive data or `MSG_NOTIFICATION` events through recvmsg, query association and peer address state, and use internal socket options through lksctp helper library calls for bindx/connectx/peeloff/address enumeration.

State and persistence behavior: SCTP endpoint, association, stream, peer address, authentication key, scheduler, and statistics state lives in kernel SCTP sockets and associations. Many variable-length arrays are snapshot outputs. The header defines packed/aligned layouts for sockaddr_storage-containing structs to preserve ABI across architectures.

Dependencies and integration points: depends on Linux types and socket storage. It integrates with the SCTP protocol stack, libc/lksctp-tools, sendmsg/recvmsg cmsg handling, socket options, netlink-independent diagnostics, and applications using one-to-one or one-to-many SCTP sockets.

Risks and edge cases: ABI is large and historically compatible aliases/spellings must remain. Flexible arrays require length checks. Packed sockaddr_storage structs can expose alignment bugs. Notification subscription has legacy and per-event forms. PR policy bits share `sinfo_flags`, and internal options must not be confused with standardized options.

Test signals: lksctp functional tests for connectx/bindx/peeloff, cmsg send/receive, every notification type, auth key lifecycle, PR-SCTP TTL/RTX/PRIO, stream reset/add, UDP encapsulation, PLPMTUD probe interval, stats snapshots, packed struct size on 32/64-bit, and malformed option length rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sctp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/seccomp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/seccomp.h

Purpose: defines the seccomp syscall and notification ABI for strict/filter mode, filter flags, BPF return actions, seccomp data passed to filters, user notification structures, and notification fd ioctls.

Important APIs, types, and functions: modes include disabled, strict, and filter. Operations include setting strict/filter mode and querying action or notification sizes. Filter flags include TSYNC, log, speculation allow, new listener, TSYNC_ESRCH, and killable receive wait. Return actions range from kill/trap/errno/user-notif/trace/log/allow with masks for action and data bits. `struct seccomp_data` is the BPF input. Notification ABI uses `seccomp_notif_sizes`, `seccomp_notif`, `seccomp_notif_resp`, `seccomp_notif_addfd`, and ioctls for receive, send, ID validity, addfd, and notification-fd flags.

Control flow: userspace installs a BPF filter with seccomp or prctl. On syscall entry, the kernel evaluates filters and applies the least-permissive action. For `SECCOMP_RET_USER_NOTIF`, a supervising process reads notifications from a listener fd, optionally injects fds, validates IDs, and sends responses.

State and persistence behavior: filters attach to tasks and optionally synchronize across thread groups. User notification IDs and listener fds are runtime kernel state. The structs are transient ioctl/syscall payloads.

Dependencies and integration points: includes compiler/type definitions and integrates with classic BPF filters, ptrace/audit/logging, no_new_privs, process/thread lifecycle, and container supervisors.

Risks and edge cases: `SECCOMP_USER_NOTIF_FLAG_CONTINUE` is explicitly unsafe as a standalone security policy because syscall pointer arguments can change while supervised. Stacked filters, TSYNC failure handling, notification ID races, and addfd atomicity require careful validation. Return action ordering must remain least-permissive.

Test signals: seccomp selftests for all actions, TSYNC and TSYNC_ESRCH, listener creation, notification receive/send/ID_VALID/addfd/set flags, stacked filters, ptrace interactions, fatal signal wait behavior, and BPF `seccomp_data` arch/args correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/seccomp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/securebits.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/securebits.h

Purpose: defines per-process securebits controlling legacy root privilege behavior, setuid capability fixups, keep-caps, ambient capability raising, and check_exec restrictions.

Important APIs, types, and functions: each setting has a bit and a locked companion bit. Macros include `issecure_mask`, `SECUREBITS_DEFAULT`, `SECURE_NOROOT`, `SECURE_NO_SETUID_FIXUP`, `SECURE_KEEP_CAPS`, `SECURE_NO_CAP_AMBIENT_RAISE`, `SECURE_EXEC_RESTRICT_FILE`, `SECURE_EXEC_DENY_INTERACTIVE`, their `SECBIT_*` masks, `SECURE_ALL_BITS`, `SECURE_ALL_LOCKS`, and `SECURE_ALL_UNPRIVILEGED`.

Control flow: privileged userspace or security runtimes set securebits through prctl. Kernel credential and exec paths consult these bits when handling UID 0 special cases, setuid transitions, capability retention, ambient capabilities, and check_exec policy.

State and persistence behavior: securebits are task credential state. Lock bits make corresponding settings immutable for the task and descendants according to credential inheritance rules. The header owns no storage.

Dependencies and integration points: integrates with Linux capabilities, `prctl(PR_SET_SECUREBITS)`, exec credential recalculation, ambient capabilities, and check_exec documentation/policy.

Risks and edge cases: settings are paired with locks by adjacent bits, so masks must stay aligned. `SECURE_KEEP_CAPS` clears on exec unless locked. New unprivileged exec-restriction bits must be included in aggregate masks without changing old semantics.

Test signals: capability selftests for setuid transitions, no-root mode, keep-caps across exec, ambient raise denial, locked-bit immutability, and check_exec restriction/interactive denial behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/securebits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sed-opal.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/sed-opal.h

Purpose: defines ioctl payloads and command numbers for managing TCG Opal self-encrypting drives through block device ioctls.

Important APIs, types, and functions: constants define `OPAL_KEY_MAX` and `OPAL_MAX_LRS`. Enums cover MBR enable/done, users, lock states/flags, key types, revert options, and table operations. Structs include `opal_key`, LR activation/reactivation/setup/status, session info, user/LR assignment, sum ranges, lock/unlock, password changes, MBR data/done/shadow MBR, generic table read/write, status, geometry, discovery, and revert LSP. Ioctls `IOC_OPAL_*` cover save, lock/unlock, ownership, LSP activation/revert, password changes, LR setup/erase/status, MBR operations, table RW, status/geometry/discovery, PSID revert, stack reset, and SUM status.

Control flow: userspace opens a block device and issues Opal ioctls with credentials and target ranges. The kernel Opal layer translates requests into TCG commands, authenticates sessions, manipulates locking ranges, MBR shadowing, or tables, and returns status/geometry/discovery data.

State and persistence behavior: Opal state persists inside drive firmware: ownership, users, keys, locking ranges, MBR flags, geometry, and SUM/range status. Kernel state is a transient command session. User keys are copied through ioctl buffers and must be cleared by callers when appropriate.

Dependencies and integration points: depends on Linux types and ioctl encoding via included block/ioctl context. It integrates with block devices, libata/NVMe/SCSI passthrough as implemented by the Opal core, drive firmware, and storage encryption management tools.

Risks and edge cases: credential buffers are fixed 256 bytes with explicit lengths. Many ioctls are destructive, especially revert, erase, secure erase, PSID revert, and stack reset. Range IDs are bounded by `OPAL_MAX_LRS`; table offsets/lengths and shadow MBR buffers need strict bounds checks.

Test signals: ioctl layout tests, discovery/status/geometry on supported and unsupported drives, lock/unlock and LR setup on test devices, invalid key lengths, invalid LR numbers, MBR enable/done flows, generic table bounds, and negative tests for destructive commands gated by credentials.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sed-opal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/seg6.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/seg6.h

Purpose: defines base IPv6 Segment Routing Header (SRH) UAPI constants and structures.

Important APIs, types, and functions: `struct ipv6_sr_hdr` contains extension-header fields, SRH type, segments-left, first-segment, flags, tag, and flexible IPv6 segment list. `struct sr6_tlv` represents generic SRH TLVs. Constants define SRH flag bits and TLV types for ingress/egress timestamps, opaque container, padding, HMAC, and others.

Control flow: packet, tunnel, and routing code parse the SRH fixed header, iterate segment addresses and TLVs, update segments-left during forwarding, and optionally validate HMAC or local SID behavior.

State and persistence behavior: represented state is packet wire data or route encapsulation data. This header owns no runtime state.

Dependencies and integration points: depends on IPv6 address and Linux type definitions. It integrates with IPv6 SRv6 routing, lightweight tunnels, HMAC, local SID actions, iproute2, and netlink route attributes.

Risks and edge cases: SRH is variable length. Code must check `hdrlen`, segment count, TLV lengths, HMAC presence, and alignment before reading flexible data. Segment routing semantics may be disabled or policy-gated in forwarding paths.

Test signals: create and parse SRH packets with multiple segments and TLVs, verify HMAC TLVs, fuzz hdrlen/TLV lengths, and test SRv6 tunnel route dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/seg6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/seg6_genl.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/seg6_genl.h

Purpose: defines generic-netlink command and attribute IDs for configuring SRv6 global behavior.

Important APIs, types, and functions: command enum values include `SEG6_CMD_SETHMAC`, `SEG6_CMD_DUMPHMAC`, `SEG6_CMD_SET_TUNSRC`, `SEG6_CMD_GET_TUNSRC`, and max constants. Attribute IDs include HMAC key ID, secret, algorithm, tunnel source address, and max constants.

Control flow: userspace sends generic-netlink SRv6 commands to set or dump HMAC keys and to set or query the tunnel source address. The kernel validates attributes, updates SRv6 per-netns state, and replies or dumps configured data.

State and persistence behavior: HMAC keys and tunnel source are kernel network-namespace runtime state. They are not persistent except through userspace reconfiguration.

Dependencies and integration points: integrates with SRv6 generic-netlink family, HMAC validation, tunnel encap code, and iproute2 `seg6` commands.

Risks and edge cases: secrets are sensitive netlink payloads; dumps must avoid unintended exposure according to permissions. Attribute length for IPv6 tunnel source and algorithm/key IDs must be validated.

Test signals: generic-netlink set/get/dump tests for HMAC and tunnel source, permission checks, malformed attributes, key replacement/removal, and packet HMAC validation after configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/seg6_genl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/seg6_hmac.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/seg6_hmac.h

Purpose: defines SRv6 HMAC algorithm identifiers shared by userspace and kernel.

Important APIs, types, and functions: constants include `SEG6_HMAC_ALGO_SHA1`, `SEG6_HMAC_ALGO_SHA256`, and `SEG6_HMAC_ALGO_MAX`.

Control flow: userspace selects an algorithm when configuring SRv6 HMAC keys through generic netlink; packet validation/generation code uses the selected algorithm ID.

State and persistence behavior: no state is stored here. Algorithm choice is part of SRv6 HMAC key configuration.

Dependencies and integration points: integrates with `seg6_genl.h`, SRH HMAC TLVs, kernel crypto API, and iproute2.

Risks and edge cases: algorithm IDs are ABI values; adding algorithms must preserve old values. Unsupported algorithms must be rejected consistently.

Test signals: configure SHA1 and SHA256 keys, reject out-of-range IDs, and verify generated/validated HMAC TLVs match expected digest algorithms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/seg6_hmac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/seg6_iptunnel.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/seg6_iptunnel.h

Purpose: defines netlink attributes and mode constants for SRv6 lightweight tunnel encapsulation.

Important APIs, types, and functions: attributes include `SEG6_IPTUNNEL_SRH` and max constants. Mode constants include inline, encap, L2 encap, encap with reduced SRH, and L2 encap with reduced SRH. `SEG6_IPTUNNEL_SRH_SIZE(srh)` computes SRH byte size from `hdrlen`.

Control flow: route configuration passes an SRH and mode through netlink. Kernel lwtunnel code validates the SRH, stores it in route encap state, and applies inline or encapsulation behavior when packets match the route.

State and persistence behavior: route/lwtunnel entries retain the serialized SRH and mode until route deletion or replacement. The header itself stores nothing.

Dependencies and integration points: integrates with `seg6.h`, rtnetlink route encap attributes, IPv6 lwtunnel output, and iproute2.

Risks and edge cases: reduced modes have specific segment-list requirements. The size macro assumes a valid SRH pointer and must only run after attribute length checks. Inline mode mutates existing IPv6 packets while encap modes add outer headers.

Test signals: route add/dump/delete for each mode, packet forwarding checks, invalid SRH length rejection, reduced-mode segment validation, and l2/l3 encapsulation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/seg6_iptunnel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/seg6_local.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/seg6_local.h

Purpose: defines SRv6 local SID action IDs, behavior attributes, counters, flavors, and nested flavor operations used by rtnetlink route configuration.

Important APIs, types, and functions: action enum values cover End, End.X, End.T, End.DX2, End.DX6, End.DX4, End.DT6, End.DT4, End.B6, End.B6.Encaps, End.BM, End.S, End.AS, End.AM, lookup-table variants, and NEXT_CSID behavior. Attribute IDs include action, SRH, table, nexthop, interface, counters, flavors, and VRF table. Counter structs expose packet/byte/error counters. Flavor enums include PSP, USP, USD, and NEXT_CSID with next-csid length attributes.

Control flow: userspace configures a local SID route with action and action-specific attributes. Kernel route code validates mandatory attributes, installs seg6local state, and executes the behavior when a packet reaches the local SID.

State and persistence behavior: local SID behavior state persists in route entries and may maintain counters. The header only defines serialized configuration and dump layouts.

Dependencies and integration points: integrates with SRv6 local processing, rtnetlink route attributes, VRFs, nexthop/interface lookup, counters, and iproute2 `seg6local`.

Risks and edge cases: each action requires a different attribute set; accepting missing or extra attributes can misroute traffic. Counter sizes, flavor nesting, NEXT_CSID bit lengths, and table/VRF handling are common validation risks.

Test signals: install and dump every local action, exercise PSP/USP/USD/NEXT_CSID flavors, verify counters increment, reject invalid attribute combinations, and route packets through End.DX/DT/B6 behaviors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/seg6_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/selinux_netlink.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/selinux_netlink.h

Purpose: defines SELinux netlink notification message types and payloads for policy state changes visible to userspace.

Important APIs, types, and functions: message constants include notifications for enforcing mode, policy load, setenforce denial, policy capability changes, and status. Payload structs carry enforcing mode, policy sequence numbers, deny_unknown, capability values, and status fields.

Control flow: SELinux kernel code multicasts events when policy is loaded or enforcement/capability state changes. Userspace policy daemons or monitors subscribe to the SELinux netlink channel and decode the fixed payload for each message type.

State and persistence behavior: SELinux enforcement mode, policy sequence, deny_unknown, and policy capability state live in the SELinux security server. Netlink messages are transient notifications.

Dependencies and integration points: integrates with SELinux policy loading, libselinux status monitoring, audit/security tooling, and netlink multicast delivery.

Risks and edge cases: userspace must tolerate missed messages and query current state when needed. Message struct layout must remain stable, and unknown future message types should be ignored safely.

Test signals: policy reload notifications, enforcing/permissive transitions, capability toggles, userspace monitor decoding, and netlink subscriber behavior across dropped messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/selinux_netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sem.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/sem.h

Purpose: defines the System V semaphore userspace ABI, including semop flags, semctl commands, legacy structures, semop payloads, semctl union, and default limits.

Important APIs, types, and functions: `SEM_UNDO` requests undo-on-exit behavior. Semctl commands include `GETPID`, `GETVAL`, `GETALL`, `GETNCNT`, `GETZCNT`, `SETVAL`, `SETALL`, `SEM_STAT`, `SEM_INFO`, and `SEM_STAT_ANY`. `struct sembuf` carries semaphore index, operation, and flags. `union semun` is the semctl argument shape. `struct seminfo` and constants such as `SEMMNI`, `SEMMSL`, `SEMMNS`, `SEMOPM`, `SEMVMX`, and `SEMAEM` describe limits. Legacy `struct semid_ds` remains for compatibility while `asm/sembuf.h` supplies modern 64-bit layouts.

Control flow: userspace creates semaphore sets through SysV IPC, performs arrays of `sembuf` operations via semop/semtimedop, and manages/query sets through semctl commands.

State and persistence behavior: semaphore sets, values, wait queues, undo lists, timestamps, and permissions live in the kernel IPC namespace until removed. Undo state is per process and applied on exit. The header defines ABI shapes only.

Dependencies and integration points: depends on `linux/ipc.h` and architecture semaphore buffer layouts. It integrates with SysV IPC namespaces, libc semctl wrappers, ipcs/ipcrm tools, and checkpoint/compat code.

Risks and edge cases: `union semun` contains userspace pointers and differs from some libc declarations. Large `SEMOPM` values can trigger allocation fragmentation, as documented. Legacy and 64-bit time layouts must be kept compatible.

Test signals: semget/semop/semctl tests for all command values, SEM_UNDO on process exit, IPC namespace isolation, 32-bit compat semid layouts, limit sysctl changes, and large semop array failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/serial.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/serial.h

Purpose: defines legacy and modern serial port userspace structures for setserial-style configuration, multiport cards, interrupt counters, RS485 mode, and ISO7816 smartcard mode.

Important APIs, types, and functions: `struct serial_struct` carries UART type, line, port, irq, flags, fifo size, custom divisor, baud base, close delays, I/O type, hub6, iomem fields, and map base. Port type and I/O constants cover 8250-class devices and memory/port access modes. `serial_multiport_struct` and `serial_icounter_struct` describe multiport interrupt matching and line counters. `struct serial_rs485` carries RS485 flags, RTS delays, optional address filter/destination, and padding. `struct serial_iso7816` carries ISO7816 flags and timing/clock fields.

Control flow: userspace uses tty ioctls such as TIOCGSERIAL/TIOCSSERIAL, TIOCSRS485/TIOCGRS485, and ISO7816 ioctls to query or modify driver configuration. Drivers sanitize unsupported bits and return the applied state.

State and persistence behavior: serial configuration lives in tty/uart driver state and hardware registers while the port exists. Some legacy settings affect device open/close behavior; RS485/ISO7816 fields affect transmit mode.

Dependencies and integration points: depends on Linux constants/types and `tty_flags.h`. It integrates with the tty layer, 8250 and platform UART drivers, RS485 transceiver control, and userspace tools.

Risks and edge cases: `serial_struct` contains pointer-sized fields and is legacy/architecture-sensitive. RS485 address fields overlap deprecated padding, so callers must not use both. Unsupported RS485/ISO7816 flags should be cleared by drivers rather than silently accepted.

Test signals: TIOCGSERIAL/TIOCSSERIAL compat tests, RS485 enable/RTS/address/bus-termination modes, ISO7816 T parameter and clock settings, unsupported flag sanitization, and open/close delay behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/serial.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/serial_core.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/serial_core.h

Purpose: extends serial port type identifiers beyond the historical values in `serial.h` for platform UART drivers and generic userspace reporting.

Important APIs, types, and functions: `PORT_*` constants assign stable numeric IDs for NS16550A, XScale, Tegra, Exar, ARM, SPARC, OMAP, Cadence, SiFive, STM32, Qualcomm, Broadcom, Freescale, and many other UART families. `PORT_GENERIC` is `-1` for ports whose exact type is not important to userspace.

Control flow: UART drivers report a type through serial-core data structures or legacy serial ioctls. Userspace tools can display or compare the type without knowing driver internals.

State and persistence behavior: no state is stored in this header. The selected type is runtime driver metadata for a registered serial port.

Dependencies and integration points: includes `linux/serial.h` and integrates with serial core, UART drivers, and setserial-style tooling.

Risks and edge cases: values 0-19 are reserved for historical busybox/setserial compatibility and must not be modified. Adding new types must avoid reusing existing numeric IDs. Userspace should not depend on type IDs for hardware programming.

Test signals: compile coverage for UART drivers, serial ioctl reporting for representative ports, stable numeric values in ABI tests, and generic type reporting for drivers using `PORT_GENERIC`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/serial_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/serial_reg.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/serial_reg.h

Purpose: exports 8250/16450/16550-compatible UART register offsets and bit definitions, plus common vendor extension registers used by serial drivers and low-level tools.

Important APIs, types, and functions: constants define DLAB=0 registers (`UART_RX`, `UART_TX`, `UART_IER`, `UART_IIR`, `UART_FCR`, `UART_LCR`, `UART_MCR`, `UART_LSR`, `UART_MSR`, `UART_SCR`), divisor registers (`UART_DLL`, `UART_DLM`), enhanced registers (`UART_EFR`, XON/XOFF, TI TCR/TLR), trigger/FIFO bits, line/modem status bits, XScale, 16C950, RSA, DA8xx, OMAP, and Altera extension registers.

Control flow: serial drivers use these offsets and masks to program UART hardware: enable interrupts/FIFOs, set word length and baud divisors, manage modem control, read status, handle vendor FIFO trigger modes, and service interrupts.

State and persistence behavior: state is hardware register state. The header defines numeric offsets and masks only. Values persist in device registers until reprogrammed, reset, or power-managed.

Dependencies and integration points: integrates with 8250 serial drivers, platform UART variants, boot consoles, debug tools, and some low-level board code.

Risks and edge cases: many offsets are mode-dependent, especially DLAB and LCR configuration modes. Some bit values are reused with different meanings by variants. FIFO trigger levels are chip-specific despite common bit positions. Incorrect mode sequencing can corrupt divisor or enhanced registers.

Test signals: UART loopback tests, baud divisor programming, FIFO trigger behavior on 16550/16750/16C950/OMAP variants, interrupt cause decoding, modem status changes, and register access mode tests with DLAB/EFR sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/serial_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/serio.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/serio.h

Purpose: defines serio input-device ioctl, event flags, bus/controller types, and protocol/device IDs for serial input devices such as keyboards, mice, touchscreens, game controllers, and CEC adapters.

Important APIs, types, and functions: `SPIOCSTYPE` sets the serio type. Event flags include timeout, parity, frame, and out-of-band data. Bus/controller constants include XT, 8042, RS232, HIL, passthrough, and XL. Protocol IDs cover many mouse, keyboard, touchscreen, tablet, joystick, and adapter devices such as MSC, Sun, Microsoft, Wacom, eGalax, Pulse8 CEC, RainShadow CEC, FS-iA6B, and Extron.

Control flow: serio drivers report port and device protocol types to input core. Userspace or compatibility tools may set a port type through ioctl. Drivers consume event flags while decoding input bytes.

State and persistence behavior: serio port type and attached device identity live in kernel input/serio state. The header only defines ABI constants.

Dependencies and integration points: depends on const and ioctl UAPI headers. It integrates with the Linux input subsystem, i8042, serial input drivers, and device matching tables.

Risks and edge cases: protocol IDs are stable ABI. Misidentifying a device can bind the wrong input driver. Event flags may be reported asynchronously with data bytes and must be decoded with ordering preserved.

Test signals: input device probing for common serio protocols, ioctl type setting, parity/frame/timeout error injection, hotplug/unplug, and ID stability checks for userspace device databases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/serio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sev-guest.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/sev-guest.h

Purpose: defines the AMD SEV-SNP guest device ioctl ABI for attestation reports, derived keys, extended reports, and structured firmware/VMM errors.

Important APIs, types, and functions: `SNP_REPORT_USER_DATA_SIZE` sizes report nonce/user data. Request/response structs include `snp_report_req`, `snp_report_resp`, `snp_derived_key_req`, `snp_derived_key_resp`, `snp_guest_request_ioctl`, and `snp_ext_report_req`. Ioctls are `SNP_GET_REPORT`, `SNP_GET_DERIVED_KEY`, and `SNP_GET_EXT_REPORT`. Error helpers split firmware error and VMM error fields with `SNP_GUEST_FW_ERR_MASK`, `SNP_GUEST_VMM_ERR_SHIFT`, `SNP_GUEST_ERR`, and VMM error codes.

Control flow: confidential-VM userspace opens the SNP guest device, prepares a request buffer, issues an ioctl, and receives firmware-provided attestation report, derived key, or extended certificate/report material. The common ioctl wrapper carries request/response pointers and firmware error output.

State and persistence behavior: no state is stored here. Runtime state lives in the SNP guest driver, firmware mailbox, and hypervisor-mediated request path. Reports and keys are transient sensitive outputs.

Dependencies and integration points: depends on Linux types and ioctl macros. It integrates with AMD PSP/SNP firmware, confidential computing attestation agents, key derivation flows, and VMM error reporting.

Risks and edge cases: request/response pointers and lengths must be validated, extended report buffers may be too small, firmware busy/invalid-length errors need retry/reporting, and derived keys are sensitive material.

Test signals: GET_REPORT with fixed user data, derived-key requests for valid/invalid selectors, extended report buffer sizing retries, firmware and VMM error decoding, and tests in SNP guests under busy/error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sev-guest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/shm.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/shm.h

Purpose: defines the System V shared memory userspace ABI: default limits, legacy and modern info structures, shmget/shmat flags, hugepage encoding, and shmctl commands.

Important APIs, types, and functions: constants define `SHMMIN`, `SHMMNI`, `SHMMAX`, `SHMALL`, and `SHMSEG`. Legacy `struct shmid_ds` and `struct shminfo` remain for compatibility while `asm/shmbuf.h` supplies 64-bit layouts. Flags include `SHM_R`, `SHM_W`, `SHM_HUGETLB`, `SHM_NORESERVE`, `SHM_RDONLY`, `SHM_RND`, `SHM_REMAP`, `SHM_EXEC`, hugepage-size encodings, and commands `SHM_LOCK`, `SHM_UNLOCK`, `SHM_STAT`, `SHM_INFO`, `SHM_STAT_ANY`. `struct shm_info` reports usage.

Control flow: userspace creates segments with shmget, attaches with shmat, controls/removes/locks/queries with shmctl, and detaches with shmdt. HugeTLB size bits refine `SHM_HUGETLB` allocations.

State and persistence behavior: shared-memory segments live in an IPC namespace until removed and detached. Attach counts, creator/last operator pids, timestamps, permissions, resident/swap usage, and hugepage backing are kernel state. Defaults are sysctl-adjustable.

Dependencies and integration points: depends on IPC, errno, and generic hugepage encoding headers plus architecture shmbuf layouts. It integrates with SysV IPC, hugetlbfs, namespaces, libc, and ipcs/ipcrm tools.

Risks and edge cases: `SHMMAX` and `SHMALL` are intentionally below `ULONG_MAX` to avoid userspace overflow patterns. Hugepage flags must not conflict with mode bits. Legacy structures have old time and size fields and need compat handling.

Test signals: shmget/shmat/shmctl/shmdt flows, hugepage-size selection, `SHM_NORESERVE`, lock/unlock permissions, namespace isolation, 32-bit compat structure tests, and boundary limit/sysctl behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/shm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/signal.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/signal.h

Purpose: provides the Linux UAPI include wrapper for signal definitions, pulling in architecture-specific signal numbers and generic signal file-descriptor constants.

Important APIs, types, and functions: this header includes `asm/signal.h` and `asm/siginfo.h`; it does not define additional structs of its own in this copy.

Control flow: userspace and kernel UAPI consumers include `linux/signal.h` to obtain architecture signal numbers, sigset/sigaction-related types, and siginfo layouts through the architecture headers.

State and persistence behavior: no state is represented here. Signal dispositions, masks, and pending queues live in task structures and are defined by included ABI headers.

Dependencies and integration points: integrates with architecture UAPI signal headers, libc, syscall ABIs such as rt_sigaction/rt_sigprocmask, signalfd, ptrace, and seccomp trap delivery.

Risks and edge cases: behavior is architecture-dependent because the actual definitions come from `asm/*`. Include-order and namespace expectations matter for libc and kernel header users.

Test signals: architecture compile coverage, libc header compatibility, signal number/layout selftests, and cross-arch `siginfo_t`/sigset ABI checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/signalfd.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/signalfd.h

Purpose: defines the signalfd userspace ABI for receiving signals as structured records through a file descriptor.

Important APIs, types, and functions: `struct signalfd_siginfo` contains signal number, errno, code, pid/uid, fd, timer, band, overrun/trap/status/int/ptr, utime/stime, sender address, address_lsb, syscall, call address, architecture, and padding. `SFD_CLOEXEC` and `SFD_NONBLOCK` alias descriptor flags from fcntl.

Control flow: userspace blocks signals in a mask, creates or updates a signalfd, then reads one or more `signalfd_siginfo` records instead of using traditional signal handlers. Kernel signal delivery packages pending signal metadata into the fixed record format.

State and persistence behavior: signalfd file descriptors reference a signal mask and task/signal state. Pending signals remain kernel task state until consumed. The record is a transient read output.

Dependencies and integration points: depends on Linux types and fcntl flags. It integrates with signal delivery, poll/epoll, pidfd/process supervision, seccomp `SIGSYS` metadata, and timer/async I/O signals.

Risks and edge cases: padding preserves fixed record size for future expansion. Consumers must handle partial reads only in multiples of the struct size. Architecture and syscall fields are meaningful only for some signal codes.

Test signals: signalfd reads for standard and realtime signals, timer signals with overrun, SIGCHLD status, SIGSYS/seccomp fields, nonblocking and close-on-exec flags, epoll readiness, and record-size ABI checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/signalfd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/smc.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/smc.h

Purpose: defines UAPI constants and socket options for the SMC protocol family, including SMC-R/SMC-D selection, diagnostics, and connection metadata.

Important APIs, types, and functions: the header exports SMC protocol/socket constants, option names for enabling/disabling SMC variants and retrieving info, and structures used to describe SMC connection, link, device, peer, or fallback state for userspace.

Control flow: applications create AF_SMC sockets or query SMC state through socket options. The kernel negotiates SMC-R over RDMA or SMC-D over ISM when possible, otherwise falls back to TCP, and reports negotiated/fallback state through the defined ABI.

State and persistence behavior: SMC connection, link group, RDMA/ISM device, token, buffer, and fallback state lives in kernel socket and device state for the connection lifetime. The header defines query/control layouts only.

Dependencies and integration points: integrates with AF_SMC sockets, TCP fallback, RDMA/InfiniBand, ISM devices, net namespaces, and diagnostic tooling.

Risks and edge cases: fallback reasons and link metadata must be stable for tooling. Protocol selection must handle systems lacking RDMA/ISM. Socket option structs need version/length compatibility as SMC features grow.

Test signals: AF_SMC connection setup with SMC-R, SMC-D, and TCP fallback, socket-option get/set behavior, metadata dumps, unsupported-device cases, and connection teardown under device loss.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/smc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/smc_diag.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/smc_diag.h

Purpose: defines netlink sock_diag request, response, attribute, and payload layouts for inspecting SMC sockets and SMC-R/SMC-D internals.

Important APIs, types, and functions: `struct smc_diag_req` and message/extension enums select SMC diagnostics. Payload structs include `smc_diag_msg`, `smc_diag_cursor`, `smc_diag_conninfo`, `smc_diag_linkinfo`, `smc_diag_lgrinfo`, `smc_diag_fallback`, and `smcd_diag_dmbinfo`.

Control flow: diagnostic tools send a sock_diag request for SMC sockets. The kernel dumps socket records with optional connection info, link group/link info, fallback data, and SMC-D DMB information encoded as netlink attributes.

State and persistence behavior: responses are snapshots of live socket, cursor, send/receive buffer, link, token, GID, and fallback state. The header owns no persistent state.

Dependencies and integration points: depends on inet diagnostics, socket diagnostics, and InfiniBand device-name limits. It integrates with `ss`, sock_diag netlink, AF_SMC internals, RDMA, and ISM.

Risks and edge cases: live sockets can change while being dumped, so cursors and counters are snapshots. Optional extensions must be length-checked. GID/token fields differ between SMC-R and SMC-D, and tooling must tolerate absent attributes.

Test signals: sock_diag dumps for idle and active SMC-R/SMC-D sockets, fallback connections, extension filtering, namespace isolation, socket destruction during dump, and attribute length fuzzing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/smc_diag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/smiapp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/smiapp.h

Purpose: defines V4L2 test-pattern mode constants for SMIA/SMIA++ compliant camera modules handled by the SMIAPP driver.

Important APIs, types, and functions: constants cover disabled, solid colour, colour bars, grey colour bars, and PN9 test pattern modes.

Control flow: userspace sets a V4L2 test-pattern control to one of these values; the camera sensor driver maps it to the sensor register sequence for test pattern generation.

State and persistence behavior: selected test pattern mode lives in sensor driver state and hardware registers until changed or the device is reset. The header only defines numeric values.

Dependencies and integration points: integrates with V4L2 controls, SMIA/SMIA++ sensor drivers, media pipelines, and camera test applications.

Risks and edge cases: mode values must match driver control menus and hardware support. Unsupported modes should be rejected or hidden through control enumeration.

Test signals: enumerate the V4L2 test-pattern menu, set every mode, capture frames to verify pattern output, and test fallback/rejection on sensors with partial support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/smiapp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/snmp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/snmp.h

Purpose: defines numeric MIB counter indexes for Linux networking SNMP/proc statistics across IP, ICMP, ICMPv6, TCP, UDP, and Linux-specific protocol counters.

Important APIs, types, and functions: enums export `IPSTATS_MIB_*`, `ICMP_MIB_*`, `ICMP6_MIB_*`, `TCP_MIB_*`, `UDP_MIB_*`, and many `LINUX_MIB_*` counters. `__ICMPMSG_MIB_MAX` and `__ICMP6MSG_MIB_MAX` size per-message-type arrays. Comments map many counters to RFC MIB names and Linux `/proc/net/snmp`/`netstat` labels.

Control flow: kernel networking fast paths increment per-CPU MIB counters by enum index. Procfs/sysctl/netlink readers aggregate and format counters for userspace monitoring.

State and persistence behavior: counters are runtime per-network-namespace/per-CPU statistics. They reset on namespace or system lifetime and are not persistent. The header defines indexes only.

Dependencies and integration points: integrates with IPv4/IPv6, ICMP, TCP, UDP, MIB aggregation, `/proc/net/snmp`, `/proc/net/netstat`, SNMP agents, and monitoring tools.

Risks and edge cases: enum ordering is ABI-sensitive for array indexes and proc output mapping. Fast-path counters are grouped partly for cache behavior. Adding counters must update string tables and max values consistently.

Test signals: compare procfs counter names/counts with enum tables, run packet-level tests that increment representative counters, verify per-netns isolation, and compile-check string table alignment with max enum values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/snmp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sock_diag.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/sock_diag.h

Purpose: defines generic socket diagnostics netlink commands, memory-info indexes, multicast groups, and BPF socket-storage diagnostic attributes.

Important APIs, types, and functions: command IDs include `SOCK_DIAG_BY_FAMILY` and `SOCK_DESTROY`. `struct sock_diag_req` selects family and protocol. `SK_MEMINFO_*` indexes describe receive/send buffer allocation, queued memory, optmem, backlog, and drops. `sknetlink_groups` defines destroy notification groups. BPF storage request/reply/map-value attribute enums define how socket-local BPF storage is requested and returned.

Control flow: diagnostic tools send sock_diag netlink requests by family/protocol, optionally request memory or BPF storage data, and receive family-specific dumps. Destroy commands can request socket termination where supported.

State and persistence behavior: responses are snapshots of live socket memory and optional BPF storage state. Destroy commands mutate socket state. The header stores no state.

Dependencies and integration points: depends on Linux types and integrates with inet/unix/packet/smc diagnostics, netlink multicast destroy notifications, BPF maps, and tools such as `ss`.

Risks and edge cases: the macro typo `SK_DIAB_BPF_STORAGE_REP_MAX` is exported ABI and cannot simply be renamed without compatibility care. BPF storage values are variable length and must be policy-checked. Socket destruction requires permission and race handling.

Test signals: sock_diag dumps for multiple families, memory-info indexes, destroy notification groups, BPF storage map fd requests and replies, malformed attribute rejection, and namespace/permission tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sock_diag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/socket.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/socket.h

Purpose: defines generic socket UAPI pieces shared across protocol headers: sockaddr storage size/alignment, kernel socket family type, socket buffer lock flags, and transmit hash policy constants.

Important APIs, types, and functions: `_K_SS_MAXSIZE` fixes sockaddr storage at 128 bytes. `__kernel_sa_family_t` is the exported family type. `struct __kernel_sockaddr_storage` uses an anonymous union/struct and pointer member to enforce family placement and default alignment. `SOCK_SNDBUF_LOCK`, `SOCK_RCVBUF_LOCK`, and `SOCK_BUF_LOCK_MASK` describe locked buffer settings. `SOCK_TXREHASH_*` constants define transmit rehash policy values.

Control flow: protocol UAPI headers embed or alias sockaddr storage for address payloads. Socket option code uses buffer lock flags to report or enforce user-locked send/receive buffer sizes, and networking code can expose txrehash policy through sysctl/socket options.

State and persistence behavior: storage structs are transient ABI containers. Buffer lock and txrehash state live in kernel socket objects.

Dependencies and integration points: this header is included by many networking UAPI headers and libc-visible socket definitions. It integrates with protocol address structs, getsockopt/setsockopt buffer handling, and core socket code.

Risks and edge cases: storage size and alignment are ABI-critical and must satisfy RFC2553-style expectations. Anonymous unions/structs can interact with compiler modes. Protocols must not exceed `_K_SS_MAXSIZE` when using generic storage.

Test signals: compile/layout tests for sockaddr storage size/alignment, protocol structs embedding storage, buffer lock option behavior, txrehash policy values, and 32/64-bit ABI checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/socket.h -->
