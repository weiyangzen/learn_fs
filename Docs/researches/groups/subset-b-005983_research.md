# Research group subset-b-005983

This grouped report covers Linux UAPI headers under `sources/distributed-fs/ceph-client/include/uapi/linux`. Each file section is bounded by reconciliation markers so it can be split into the required source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/iommufd.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/iommufd.h

## Purpose
`iommufd.h` defines the userspace ABI for the IOMMU file descriptor subsystem. It exposes object IDs and ioctl structures for managing IO address spaces, hardware page tables, virtual IOMMUs, virtual devices, fault queues, event queues, and hardware-assisted queues used by VFIO, VMMs, and device assignment stacks.

## Important APIs, Types, and Functions
The ioctl command enum starts at `IOMMUFD_CMD_BASE` and maps to `IOMMU_DESTROY`, `IOMMU_IOAS_ALLOC`, `IOMMU_IOAS_MAP`, `IOMMU_IOAS_UNMAP`, `IOMMU_HWPT_ALLOC`, `IOMMU_GET_HW_INFO`, dirty tracking ioctls, fault queue allocation, vIOMMU/vDEVICE allocation, vEVENTQ allocation, and HW queue allocation. Core data carriers include `iommu_ioas_map`, `iommu_ioas_copy`, `iommu_ioas_unmap`, `iommu_hwpt_alloc`, `iommu_hw_info`, `iommu_hwpt_invalidate`, `iommu_hwpt_pgfault`, `iommu_viommu_alloc`, `iommu_vdevice_alloc`, `iommu_veventq_alloc`, and `iommu_hw_queue_alloc`.

## Control Flow
Userspace opens an iommufd, allocates an IOAS, optionally constrains allowed IOVA ranges, maps user memory or memfd-backed memory, attaches devices through related kernel paths, and allocates HWPTs for kernel-managed or nested page tables. Nested flows query hardware info, allocate parent and nested HWPTs, submit invalidations after userspace page table edits, handle PRI faults via fault FDs, and report page responses. Virtualization flows allocate vIOMMU objects, vDEVICE IDs, vEVENTQs, and platform-specific HW queues.

## State and Persistence
All durable state is kernel-owned and referenced by per-iommufd object IDs or returned file descriptors. IOAS mappings pin or reference memory until unmapped or destroyed. Dirty-tracking state is toggled on HWPT objects. vEVENTQ and FAULT queues persist as FDs and may lose events under overflow. `IOMMU_DESTROY` tears down destroyable IDs; closing the iommufd or auxiliary FDs releases remaining state.

## Dependencies and Integration Points
The header depends on `<linux/ioctl.h>` and `<linux/types.h>`, and uses aligned UAPI integer types. It integrates with VFIO compatibility IOAS handling, PCI PASID/ATS/PRI concepts, Intel VT-d, ARM SMMUv3, NVIDIA Tegra241 CMDQV, AMD IOMMU, memfd-backed mappings, and VMM device assignment code.

## Risks and Test Signals
ABI risk is high: structure size/version extension relies on zeroed unknown trailing fields, reserved fields must be zero, and `__aligned_u64` layout must be stable across 32/64-bit userspace. Security-sensitive tests should cover invalid IDs, IOVA overflow, unmapped or partially mapped ranges, permission flags, dirty bitmap sizing, fault response cookies, vEVENTQ overflow markers, nested invalidation type validation, and destroy ordering for vDEVICE/vIOMMU/HW queue objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/iommufd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ioprio.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ioprio.h

## Purpose
`ioprio.h` defines the packed I/O priority value used by `ioprio_get()` and `ioprio_set()` and interpreted by block schedulers and storage devices.

## Important APIs, Types, and Functions
The ABI is a 16-bit value split into a 3-bit class field, 10-bit hint field, and 3-bit level field. Macros such as `IOPRIO_PRIO_CLASS`, `IOPRIO_PRIO_DATA`, `IOPRIO_PRIO_LEVEL`, and `IOPRIO_PRIO_HINT` extract fields. Classes include none, realtime, best-effort, idle, and invalid. The inline helper `ioprio_value()` validates class, level, and hint and returns the invalid class encoding on bad input. `IOPRIO_PRIO_VALUE` and `IOPRIO_PRIO_VALUE_HINT` build values.

## Control Flow
Userspace composes a priority value, passes it to the ioprio syscall for a process, process group, or user, and the kernel stores it with task or credential-related scheduling state. Block schedulers then consult the packed value when dispatching I/O.

## State and Persistence
The header stores no state. Kernel state persists in task/user I/O-priority settings and may influence future bios. Device duration-limit hints are advisory and only matter when the target stack supports them.

## Dependencies and Integration Points
It includes `<linux/stddef.h>` and `<linux/types.h>`. Integration points are BFQ, mq-deadline, ATA/SCSI command-duration-limit support, and libc/man-page definitions of the ioprio syscalls.

## Risks and Test Signals
Tests should verify packing boundaries, invalid input returning `IOPRIO_CLASS_INVALID`, unchanged semantics for normal best-effort level 4, and scheduler behavior when hints are unsupported. Compatibility risk is mainly bit allocation: class and level widths cannot change without ABI breakage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ioprio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ip.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ip.h

## Purpose
`ip.h` exports IPv4 packet header, option, TOS/precedence, IPsec transform header, BEET/IPTFS, and per-device IPv4 configuration constants to userspace.

## Important APIs, Types, and Functions
The main ABI type is `struct iphdr`, with endian-specific bitfields for `version` and `ihl`, network-order length, ID, fragment, checksum, and grouped source/destination addresses. Related protocol headers include `ip_auth_hdr`, `ip_esp_hdr`, `ip_comp_hdr`, `ip_beet_phdr`, `ip_iptfs_hdr`, and `ip_iptfs_cc_hdr`. Macros define IP options (`IPOPT_*`), TOS/precedence masks, TTL defaults, option offsets, and `IPV4_BEET_PHMAXLEN`. The `IPV4_DEVCONF_*` enum names per-interface IPv4 sysctl slots.

## Control Flow
Packet-producing userspace or tooling fills these structures, usually through raw sockets, packet captures, test fixtures, or tunnel/IPsec control paths. The kernel networking stack parses the same wire layouts while routing, fragmenting, applying options, and handling IPsec headers.

## State and Persistence
The header has no storage; persistence is in packet buffers, route/device configuration, and xfrm/IPsec state managed elsewhere. `IPV4_DEVCONF_*` values index mutable per-device configuration.

## Dependencies and Integration Points
It depends on `<linux/types.h>`, `<linux/stddef.h>`, and `<asm/byteorder.h>`. Integration points include raw sockets, netfilter, xfrm, tunnel drivers, `/proc`/sysctl IPv4 devconf, packet decoders, and network test suites.

## Risks and Test Signals
Endianness is the largest layout risk because bitfield order differs by byte order. Tests should inspect `sizeof(struct iphdr)`, option parsing up to `MAX_IPOPTLEN`, fragment flag handling, checksum field offsets, devconf enum stability, and variable-length transform headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ip6_tunnel.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ip6_tunnel.h

## Purpose
`ip6_tunnel.h` defines the UAPI configuration structures and flags for IPv6 tunnel devices.

## Important APIs, Types, and Functions
`IPV6_TLV_TNL_ENCAP_LIMIT` and `IPV6_DEFAULT_TNL_ENCAP_LIMIT` describe tunnel encapsulation-limit behavior. Flags include ignore encapsulation limit, use original traffic class, use original flow label, mobile IPv6 device, receive DSCP copy, use original fwmark, and allow local/remote addresses. `struct ip6_tnl_parm` holds name, link, proto, encapsulation limit, hop limit, flowinfo, flags, and local/remote IPv6 addresses. `struct ip6_tnl_parm2` extends it with fwmark.

## Control Flow
Userspace supplies these structures through tunnel configuration paths such as netlink or ioctl-style tooling. The kernel creates or modifies tunnel netdevices, then uses the fields when encapsulating or decapsulating packets.

## State and Persistence
Tunnel configuration persists in kernel netdevice state until device deletion or network namespace teardown. No state is stored in the header itself.

## Dependencies and Integration Points
It includes `<linux/types.h>`, `<linux/if.h>`, and `<linux/in6.h>`. It integrates with IPv6 tunnel drivers, iproute2 tunnel configuration, net namespaces, fwmark routing, and IPv6 extension header processing.

## Risks and Test Signals
Tests should cover old and extended parameter structures, `IFNAMSIZ` name truncation, local/remote address validation, flow-label and traffic-class inheritance, fwmark preservation, and compatibility when `ip6_tnl_parm2` is passed to older tooling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ip6_tunnel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ip_vs.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ip_vs.h

## Purpose
`ip_vs.h` exports the Linux IP Virtual Server ABI for configuring services, real-server destinations, synchronization daemons, timeouts, connection flags, statistics, and the generic netlink family.

## Important APIs, Types, and Functions
Legacy socket-option commands are defined under `IP_VS_SO_SET_*` and `IP_VS_SO_GET_*`. Structures include `ip_vs_service_user`, `ip_vs_dest_user`, `ip_vs_stats_user`, `ip_vs_getinfo`, `ip_vs_service_entry`, `ip_vs_dest_entry`, `ip_vs_get_dests`, `ip_vs_get_services`, `ip_vs_timeout_user`, and `ip_vs_daemon_user`. The generic netlink family is `IPVS_GENL_NAME` with commands for service/destination CRUD, daemon control, config, info, zero, and flush. Attribute enums describe nested service, destination, daemon, stats, and info payloads.

## Control Flow
Userspace load-balancer tools create services, add destinations, tune scheduling flags and persistence, start sync daemons, and fetch stats. The kernel IPVS tables then classify packets, choose destinations, update connection state, and optionally synchronize connection entries to backup nodes.

## State and Persistence
IPVS services, destinations, connection tables, stats, timeouts, and daemon status live in kernel networking state and network namespaces. The header defines only request and response layouts. Counters are mutable until zeroed or flushed.

## Dependencies and Integration Points
It depends on `<linux/types.h>`. It integrates with netfilter/IPVS, generic netlink, legacy sockopt control paths, keepalived/ipvsadm, tunneling modes, conntrack, and multicast sync.

## Risks and Test Signals
Tests should cover struct layout for legacy sockopts, flexible-array response sizing, nested netlink attribute validation, stats32/stats64 compatibility, sync flag masks, tunnel type/flags, and namespace isolation. Risk is high for compatibility because both old sockopt and netlink ABIs coexist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ip_vs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ipc.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ipc.h

## Purpose
`ipc.h` defines common System V IPC constants, permission metadata, control commands, and legacy multiplexing numbers shared by message queues, semaphores, and shared memory.

## Important APIs, Types, and Functions
`IPC_PRIVATE` identifies private keys. `struct ipc_perm` carries key, UID/GID, creator UID/GID, mode, and sequence fields. Control flags include `IPC_CREAT`, `IPC_EXCL`, `IPC_NOWAIT`, historical DIPC flags, and commands `IPC_RMID`, `IPC_SET`, `IPC_STAT`, and `IPC_INFO`. `IPC_OLD` and `IPC_64` identify old/new ABI variants. `struct ipc_kludge` supports legacy message receive arguments. `IPCCALL(version, op)` packs legacy multiplexed syscall operations.

## Control Flow
Userspace creates or finds IPC objects by key, then performs resource-specific syscalls that share this permission and command vocabulary. The kernel validates permissions, object existence, namespace membership, and versioned structure layout.

## State and Persistence
IPC objects persist in kernel IPC namespaces until removed, namespace teardown, or system reboot. Permission changes via `IPC_SET` mutate object metadata.

## Dependencies and Integration Points
The header includes `<linux/types.h>` and `<asm/ipcbuf.h>`. It integrates with SysV IPC syscalls, namespace accounting, permission checks, `ipcs`/`ipcrm`, and compatibility syscall paths.

## Risks and Test Signals
Tests should cover namespace isolation, old versus `IPC_64` layout handling, permission mutation, stale sequence IDs, and behavior of wait versus `IPC_NOWAIT`. Compatibility risk exists around UID/GID field widths and architecture-specific `ipcbuf` layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ipc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ipmi.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ipmi.h

## Purpose
`ipmi.h` defines the multi-user IPMI character-device ABI for sending commands, receiving responses/events, registering command handlers, and configuring per-interface address, LUN, timing, and maintenance behavior.

## Important APIs, Types, and Functions
Address overlays include `ipmi_addr`, `ipmi_system_interface_addr`, `ipmi_ipmb_addr`, `ipmi_ipmb_direct_addr`, and `ipmi_lan_addr`. Message types are `ipmi_msg` for userspace pointers and `kernel_ipmi_msg` for kernel pointers. Request/receive structures include `ipmi_req`, `ipmi_req_settime`, and `ipmi_recv`. Ioctls include send, timed send, receive/truncating receive, register/unregister command, channel-scoped registration, event subscription, get/set channel address and LUN, legacy address/LUN controls, timing parameters, and maintenance mode.

## Control Flow
Userspace opens an IPMI device, sends an addressed message with a `msgid`, waits via poll/select, then receives matching responses or async events. Registration ioctls route incoming commands to specific users. The driver handles retries, timeout responses, event-queue polling, and lower-interface routing.

## State and Persistence
Open-file users have queues and registrations. Interface-wide state includes source address, LUN, timing parameters, event handling, and maintenance mode. BMC event state is external and periodically drained by the driver.

## Dependencies and Integration Points
It includes `ipmi_msgdefs.h` and `<linux/compiler.h>`. It integrates with IPMI system interfaces, IPMB/LAN channels, BMC event queues, poll/select, and server management tools.

## Risks and Test Signals
Tests should validate user pointers, address length/type matching, response correlation by `msgid`, timeout completion codes, event fanout, registration conflicts, channel masks, and receive truncation semantics. ABI risk is pointer-bearing structs and global interface controls that affect all users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ipmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ipmi_bmc.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ipmi_bmc.h

## Purpose
`ipmi_bmc.h` defines a small BMC-side IPMI ioctl ABI for manipulating SMS attention and abort state.

## Important APIs, Types, and Functions
The ioctl magic is `0xB1`. Exposed commands are `IPMI_BMC_IOCTL_SET_SMS_ATN`, `IPMI_BMC_IOCTL_CLEAR_SMS_ATN`, and `IPMI_BMC_IOCTL_FORCE_ABORT`. They carry no payload and are encoded with `_IO`.

## Control Flow
BMC emulation or management userspace opens the relevant device and issues one of the control ioctls. The kernel-side BMC driver asserts or clears attention signaling or forces abort handling.

## State and Persistence
State is entirely driver/hardware owned. SMS attention persists until cleared or reset by device state; abort behavior is an immediate control action.

## Dependencies and Integration Points
It includes `<linux/ioctl.h>` and integrates with IPMI BMC character devices and host-management signaling paths.

## Risks and Test Signals
Tests should confirm ioctl numbers, permission checks, idempotent set/clear behavior, abort effects on in-flight messages, and error handling when no BMC backend is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ipmi_bmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ipmi_msgdefs.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ipmi_msgdefs.h

## Purpose
`ipmi_msgdefs.h` provides common IPMI net function, command, completion-code, protocol, and channel-medium constants shared by IPMI UAPI users.

## Important APIs, Types, and Functions
Constants cover sensor/event, application, storage, and firmware netfns; common commands such as get device ID, reset, get/clear message flags, send/get/read event messages, channel info, SEL insertion, and BMC global enables; BMC enable bits; default slave address; maximum message length; standard and bus-level completion/error codes; channel protocol identifiers; and channel medium identifiers.

## Control Flow
No executable flow exists here. IPMI userspace and kernel drivers use these constants to construct raw `ipmi_msg` packets, decode completion codes, and interpret channel metadata.

## State and Persistence
The header has no state. It names values that appear in BMC messages, completion responses, and channel capability reports.

## Dependencies and Integration Points
It is included by `ipmi.h` and consumed by IPMI tools, BMC drivers, and management agents that need symbolic values for the IPMI specification.

## Risks and Test Signals
Tests should validate command encodings against IPMI specifications, max message length handling, and consistency between kernel responses and userspace decoders. Risk is low in code volume but high for interoperability if constants drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ipmi_msgdefs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ipmi_ssif_bmc.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ipmi_ssif_bmc.h

## Purpose
`ipmi_ssif_bmc.h` defines the message payload structure for SSIF BMC IPMI communication.

## Important APIs, Types, and Functions
`IPMI_SSIF_PAYLOAD_MAX` is 254 bytes. `struct ipmi_ssif_msg` contains `len`, `netfn_lun`, `cmd`, and a payload array sized to the maximum SSIF payload.

## Control Flow
Userspace or kernel-side BMC emulation passes a bounded SSIF message containing netfn/LUN, command, and payload. The receiving side validates `len` and interprets the payload according to IPMI command semantics.

## State and Persistence
The structure is transient message state only. Persistent behavior is in the SSIF/BMC backend and SMBus/I2C transport.

## Dependencies and Integration Points
It includes `<linux/types.h>` and integrates with IPMI SSIF BMC drivers and host-to-BMC management transports.

## Risks and Test Signals
Tests should cover payload length limits, zero-length payloads, command/netfn decoding, and rejection of overlong `len` values. ABI risk is straightforward fixed-size message layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ipmi_ssif_bmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ipsec.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ipsec.h

## Purpose
`ipsec.h` exports common IPsec/XFRM selector constants, direction identifiers, policy modes, and limits.

## Important APIs, Types, and Functions
It defines wildcard values `IPSEC_PORT_ANY`, `IPSEC_ULPROTO_ANY`, and `IPSEC_PROTO_ANY`. Enums identify security protocol IDs, policy directions, policy types/actions, and policy modes. `IPSEC_MANUAL_REQID_MAX` limits manual request IDs, and `IPSEC_REPLAYWSIZE` defines a default replay window size.

## Control Flow
Userspace policy managers use these values when configuring xfrm state/policies via PF_KEY or netlink. The kernel then applies policy lookup and transform processing during packet input/output/forwarding.

## State and Persistence
No local state exists. Policies and SAs persist in the kernel xfrm database until deleted, expired, or namespace teardown.

## Dependencies and Integration Points
The header includes `<linux/pfkeyv2.h>`. It integrates with PF_KEY, xfrm netlink, IPsec policy engines, and packet transform paths.

## Risks and Test Signals
Tests should validate wildcard selector behavior, direction/action/mode mapping, manual reqid limits, replay-window defaults, and compatibility with PF_KEY constants. Misnumbered enum values would break userspace policy tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ipsec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ipv6.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ipv6.h

## Purpose
`ipv6.h` exports IPv6 packet header, extension-header structures, socket ancillary-data structures, routing-header types, and IPv6 per-device configuration constants.

## Important APIs, Types, and Functions
Types include `in6_pktinfo`, `ip6_mtuinfo`, `in6_ifreq`, `ipv6_rt_hdr`, `ipv6_opt_hdr`, `rt0_hdr`, `rt2_hdr`, `ipv6_destopt_hao`, and `ipv6hdr`. The `ipv6hdr` layout uses endian-specific bitfields for priority/version and network-order flow label, payload length, next header, hop limit, and addresses. Constants define minimum MTU, deprecated and active routing header types, router alert values, and devconf enum entries.

## Control Flow
Userspace interacts through sockets, ancillary data, raw packet tooling, route configuration, and tunnel/IPsec stacks. The kernel parses these wire layouts during IPv6 receive/transmit and consults devconf values for per-interface behavior.

## State and Persistence
Header structures are transient packet/control data. Persistent state is in sockets, netdevice IPv6 devconf, routes, neighbor discovery, and namespaces.

## Dependencies and Integration Points
It includes libc compatibility gates, Linux integer/address types, and byteorder definitions. Integration points include IPv6 sockets, raw packet capture, iproute2, routing-header processing, segment routing, RPL, and MLD/router-alert handling.

## Risks and Test Signals
Tests should cover endian-sensitive header fields, extension-header length calculations, libc compatibility macro exposure, devconf enum stability, deprecated routing-header handling, and ancillary-data sizes on 32/64-bit userspace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ipv6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ipv6_route.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ipv6_route.h

## Purpose
`ipv6_route.h` defines IPv6 route flags, route-message layout, route notifications, and route-priority constants.

## Important APIs, Types, and Functions
Route flags include default, on-link, addrconf, prefix route, anycast, non-nexthop, expires, routeinfo, cache, flow, policy, per-CPU, and local. `RTF_PREF(pref)` encodes route preference in high bits. `struct in6_rtmsg` carries destination/source/gateway addresses, type, prefix lengths, metric, info, flags, and interface index. Notification constants include new/delete device and route events.

## Control Flow
Route tools and compatibility APIs pass `in6_rtmsg` to add, remove, or inspect IPv6 routes. The kernel stores routes and emits notifications when route or device state changes.

## State and Persistence
Routes persist in kernel fib state until deleted, expired, or namespace teardown. Some flags are read-only from userspace and reflect kernel-derived route state.

## Dependencies and Integration Points
It includes `<linux/types.h>` and `<linux/in6.h>`. Integration points include IPv6 FIB, route sockets/ioctls, rtnetlink compatibility, router advertisements, and policy routing.

## Risks and Test Signals
Tests should check user-settable versus read-only flags, preference-bit packing, ifindex validation, prefix-length validation, expiration behavior, and compatibility of `in6_rtmsg` layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ipv6_route.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/irqnr.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/irqnr.h

## Purpose
`irqnr.h` is an effectively empty UAPI guard header for IRQ-number definitions.

## Important APIs, Types, and Functions
This file contains only include guards and does not export constants, types, or functions in this tree snapshot.

## Control Flow
There is no control flow. It exists so code can include a stable header name even when no generic UAPI IRQ-number definitions are needed.

## State and Persistence
No state is represented.

## Dependencies and Integration Points
It has no includes. Integration value is source compatibility for userspace code that includes `<linux/irqnr.h>`.

## Risks and Test Signals
Tests are limited to header self-containment and successful inclusion from C/C++ userspace. Risk is low unless future definitions are added and conflict with architecture-specific IRQ numbering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/irqnr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/iso_fs.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/iso_fs.h

## Purpose
`iso_fs.h` exports ISO-9660 and High Sierra filesystem on-disk structure layouts and constants.

## Important APIs, Types, and Functions
`ISODCL(from, to)` computes field widths from spec byte ranges. Structures include `iso_volume_descriptor`, `iso_primary_descriptor`, `iso_supplementary_descriptor`, `hs_volume_descriptor`, `hs_primary_descriptor`, `iso_path_table`, and `iso_directory_record`. Constants identify descriptor types, standard IDs (`CD001`, `CDROM`), and block size (`ISOFS_BLOCK_SIZE` 2048).

## Control Flow
Filesystem parsers read sectors, match descriptor IDs/types, parse primary or supplementary descriptors, walk path tables, and interpret directory records. The kernel ISOFS driver uses these layouts for mount-time discovery and directory traversal.

## State and Persistence
The state represented is on-disk persistent media metadata. The header itself holds no runtime state.

## Dependencies and Integration Points
It includes `<linux/types.h>` and `<linux/magic.h>`. It integrates with the ISOFS filesystem driver, image-building tools, forensic parsers, and boot/media tooling.

## Risks and Test Signals
Tests should cover exact packed field offsets, block-size assumptions, malformed descriptor lengths, endianness encoded in ISO fields, supplementary descriptor handling, and directory records with variable-length names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/iso_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/isst_if.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/isst_if.h

## Purpose
`isst_if.h` defines the ioctl ABI for Intel Speed Select Technology control and discovery through OS-to-hardware interfaces.

## Important APIs, Types, and Functions
The header exposes platform info, CPU mapping, PUNIT IO register access, mailbox commands, MSR commands, core-power state, CLOS parameters and CPU associations, TPMI instance counts, performance-level discovery/control, feature enablement, detailed frequency/TDP data, fabric info, CPU masks, base-frequency info, and turbo-frequency info. Ioctls use `ISST_IF_MAGIC` and command numbers for `ISST_IF_GET_PLATFORM_INFO`, `ISST_IF_GET_PHY_ID`, `ISST_IF_IO_CMD`, `ISST_IF_MBOX_COMMAND`, `ISST_IF_MSR_COMMAND`, CLOS/core-power operations, and SST-PP/BF/TF queries and controls.

## Control Flow
Userspace first queries platform support and command batching limits, maps logical CPUs to PUNIT CPUs, then sends batched IO, mailbox, MSR, or feature-specific requests. Many structures contain `get_set` fields that select read or write behavior.

## State and Persistence
Kernel/hardware state includes platform SST capabilities, performance profile, CLOS assignments, core-power enablement, and PUNIT/MSR values. Changes persist according to firmware/hardware policy and may be reset by reboot, package reset, or firmware control.

## Dependencies and Integration Points
It includes `<linux/types.h>`. Integration points include Intel platform drivers, PUNIT/TPMI firmware interfaces, power/performance management daemons, and CPU topology mapping.

## Risks and Test Signals
Tests should cover max command counts, flexible single-element-array sizing, logical versus PUNIT CPU numbering, get/set semantics, permission checks for writes, unsupported feature reporting, and multi-socket/power-domain handling. ABI risk is high because firmware-specific structures must remain layout-stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/isst_if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ivtv.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ivtv.h

## Purpose
`ivtv.h` defines private V4L2 ioctls and types for IVTV MPEG encoder/decoder hardware.

## Important APIs, Types, and Functions
`struct ivtv_dma_frame` carries a userspace buffer pointer, type, pixel format, and width/height for DMA frame operations. `IVTV_IOC_DMA_FRAME` submits a frame transfer. `IVTV_IOC_PASSTHROUGH_MODE` controls passthrough mode. Sliced VBI type macros alias V4L2 MPEG VBI constants.

## Control Flow
Userspace video applications call IVTV private ioctls through a V4L2 device. The driver copies or DMA-transfers frame data and toggles passthrough behavior for hardware paths.

## State and Persistence
Passthrough mode and device DMA state are driver-owned and persist while the device/session is configured. Frame buffers are transient.

## Dependencies and Integration Points
It includes `<linux/compiler.h>`, `<linux/types.h>`, and `<linux/videodev2.h>`. Integration points are V4L2, IVTV hardware drivers, MPEG capture/playback applications, and VBI data handling.

## Risks and Test Signals
Tests should cover pointer validation, DMA frame dimensions/format compatibility, private ioctl numbering relative to `BASE_VIDIOC_PRIVATE`, passthrough state changes, and VBI constant compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ivtv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ivtvfb.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ivtvfb.h

## Purpose
`ivtvfb.h` exports the framebuffer-side private ioctl for IVTV DMA frame updates.

## Important APIs, Types, and Functions
`struct ivtvfb_dma_frame` contains a userspace source pointer plus destination x/y coordinates. `IVTVFB_IOC_DMA_FRAME` uses V4L2 private ioctl numbering to request a framebuffer DMA update.

## Control Flow
Userspace passes a frame buffer and target position to the IVTV framebuffer device. The driver validates the pointer and coordinates, then transfers the frame into display memory.

## State and Persistence
Framebuffer contents persist in device memory until overwritten or mode reset. The UAPI structure is transient.

## Dependencies and Integration Points
It includes compiler, integer, and V4L2 definitions. It integrates with the IVTV framebuffer driver and video output pipelines.

## Risks and Test Signals
Tests should cover buffer pointer validation, coordinate clipping, ioctl number compatibility with IVTV video ioctls, and behavior while the framebuffer mode changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ivtvfb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/jffs2.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/jffs2.h

## Purpose
`jffs2.h` defines JFFS2 flash filesystem on-media constants, node formats, compression identifiers, feature compatibility bits, summary structures, xattr records, and device-node encodings.

## Important APIs, Types, and Functions
It exports magic values, maximum name length, compression IDs, feature masks, node type constants, xattr prefixes, inode flags, endian-aware integer typedef wrappers, and raw node structures: `jffs2_unknown_node`, `jffs2_raw_dirent`, `jffs2_raw_inode`, `jffs2_raw_xattr`, `jffs2_raw_xref`, `jffs2_raw_summary`, `jffs2_node_union`, and `jffs2_device_node`.

## Control Flow
Mount or image-scan code walks flash eraseblocks, validates node magic/type/crc, interprets compatibility bits, reconstructs inode and directory state from append-only nodes, applies compression, and uses summaries to accelerate scanning.

## State and Persistence
All defined structures are persistent flash metadata. Runtime state such as inode caches, eraseblock lists, and garbage-collection decisions is built from these records by the filesystem driver.

## Dependencies and Integration Points
It includes `<linux/types.h>` and `<linux/magic.h>`. Integration points include the JFFS2 filesystem, MTD devices, image creation tools, flash recovery tooling, compression backends, xattr/ACL handling, and device special files.

## Risks and Test Signals
Tests should cover endian handling, CRC validation, unknown feature compatibility behavior, summary node parsing, xattr/xref consistency, compression ID handling, and malformed variable-length name/data fields. Layout changes would directly affect on-flash compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/jffs2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/joystick.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/joystick.h

## Purpose
`joystick.h` defines the legacy Linux joystick character-device ABI for event reads, device metadata, correction data, axis/button mappings, and old calibration structures.

## Important APIs, Types, and Functions
`struct js_event` carries timestamp, signed value, event type, and axis/button number. Event type bits identify button, axis, and init events. Ioctls fetch version, axes, buttons, name, correction data, axis map, and button map; some ioctls set correction and mappings. `struct js_corr` describes correction coefficients. Legacy structures `JS_DATA_TYPE`, `JS_DATA_SAVE_TYPE_32`, and `JS_DATA_SAVE_TYPE_64` support old API calibration.

## Control Flow
Userspace reads a stream of `js_event` records from `/dev/input/js*`, uses ioctls to discover device shape, and optionally updates correction or mapping tables. The input subsystem translates raw input events into joystick ABI records.

## State and Persistence
Axis/button maps and correction values are kernel device state, usually per open device and not durable across removal/reboot unless userspace reapplies them. Event queues are transient.

## Dependencies and Integration Points
It includes `<linux/types.h>` and `<linux/input.h>`. Integration points include evdev/input drivers, compatibility with old joystick applications, and game/controller calibration tools.

## Risks and Test Signals
Tests should cover struct sizes, event stream ordering, init events, ioctl buffer lengths, `JSIOCGNAME(len)` variable sizing, correction math boundaries, and 32/64-bit legacy save structure compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/joystick.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/kcm.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/kcm.h

## Purpose
`kcm.h` defines socket ioctl structures for Kernel Connection Multiplexor attachment, detachment, and cloning.

## Important APIs, Types, and Functions
`struct kcm_attach` carries a target file descriptor and BPF program file descriptor. `struct kcm_unattach` carries a file descriptor to detach. `struct kcm_clone` returns or accepts a file descriptor for clone operations. Ioctls are `SIOCKCMATTACH`, `SIOCKCMUNATTACH`, and `SIOCKCMCLONE`. `KCMPROTO_CONNECTED` and `KCM_RECV_DISABLE` define protocol/flag values.

## Control Flow
Userspace attaches lower sockets and parser programs to KCM sockets, detaches them, or clones KCM endpoints. The kernel multiplexes message-oriented traffic over attached connections.

## State and Persistence
Attached socket associations, BPF parser references, and clone relationships are kernel socket state tied to file descriptors and network namespaces.

## Dependencies and Integration Points
It relies on socket-private ioctl numbering from networking headers. Integration points include KCM protocol sockets, BPF stream parsing, and applications multiplexing logical messages over TCP.

## Risks and Test Signals
Tests should validate fd lifetime/reference handling, BPF program type validation, detach of unknown fds, clone semantics, receive-disable behavior, and namespace/credential checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/kcm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/kcmp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/kcmp.h

## Purpose
`kcmp.h` defines the comparison type enum and epoll-slot structure for the `kcmp` syscall, which compares whether two processes share selected kernel resources.

## Important APIs, Types, and Functions
`enum kcmp_type` includes file table, VM, files, fs, sighand, io context, System V sem undo, epoll target file, and file comparison cases. `struct kcmp_epoll_slot` identifies an epoll file descriptor, target file descriptor, target fd number, and epoll event offset.

## Control Flow
Userspace invokes `kcmp(pid1, pid2, type, idx1, idx2)` with optional pointer-like arguments for epoll comparison. The kernel checks process visibility and compares internal object pointers or resource identities.

## State and Persistence
No state is created. Results reflect current process resource sharing and can change immediately after the syscall due to process activity.

## Dependencies and Integration Points
It includes `<linux/types.h>`. Integration points include checkpoint/restore tooling, process inspection, epoll internals, and security ptrace access checks.

## Risks and Test Signals
Tests should cover permission failures, races with closing fds, each comparison type, epoll slot matching, and behavior across pid/user namespaces. ABI risk is low but pointer-identity semantics are subtle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/kcmp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/kcov.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/kcov.h

## Purpose
`kcov.h` defines ioctl controls and constants for kernel code coverage collection used by fuzzers and test harnesses.

## Important APIs, Types, and Functions
`struct kcov_remote_arg` configures remote coverage collection with trace mode, area size, handle count, and handle array pointer. Ioctls are `KCOV_INIT_TRACE`, `KCOV_ENABLE`, `KCOV_DISABLE`, and `KCOV_REMOTE_ENABLE`. Coverage modes include disabled, trace PC, and trace comparison. Comparison records use `KCOV_CMP_CONST`, `KCOV_CMP_SIZE`, and `KCOV_CMP_MASK`. `kcov_remote_handle(subsys, inst)` composes subsystem and instance bits, with common and USB subsystem constants.

## Control Flow
Userspace opens kcov, initializes an mmap-able trace area, enables a mode, runs target syscalls or remote work, then disables and reads coverage records from the shared buffer.

## State and Persistence
Coverage buffers and mode are per kcov fd/task or configured remote handle. State lasts until disabled or fd close; trace contents are transient and overwritten by subsequent runs.

## Dependencies and Integration Points
It includes `<linux/types.h>`. Integration points include syzkaller-style fuzzers, kernel instrumentation, USB/common remote coverage, and mmap shared buffers.

## Risks and Test Signals
Tests should cover buffer sizing, mode transitions, remote handle bit packing, max handle count, comparison record encoding, concurrent remote coverage, and cleanup on task/fd exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/kcov.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/kd.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/kd.h

## Purpose
`kd.h` exports Linux virtual-console keyboard/display ioctl numbers, font/palette structures, keymap structures, diacritic tables, keyboard modes, LED flags, and console font operations.

## Important APIs, Types, and Functions
The header defines ioctls for fonts (`GIO_FONT`, `PIO_FONT`, `GIO_FONTX`, `PIO_FONTX`, `KDFONTOP`), palette, sound/tone, LEDs, keyboard type/mode/meta/LED flags, keymap entries, function-key strings, diacritics, keycode translation, keyboard repeat, display mode, and low-level IO permissions. Structures include `consolefontdesc`, `unipair`, `unimapdesc`, `unimapinit`, `kbentry`, `kbsentry`, `kbdiacr`, `kbdiacrs`, `kbdiacruc`, `kbdiacrsuc`, `kbkeycode`, `kbd_repeat`, `console_font_op`, and `console_font`.

## Control Flow
Console tools issue ioctls on virtual terminals to query or mutate keyboard translation, LEDs, fonts, palette, display mode, and repeat behavior. The tty/vt subsystem applies changes to console state and hardware-facing display paths.

## State and Persistence
Most state is per virtual console or global vt keyboard/display state and persists until changed, console reset, module/device reset, or reboot. Font and mapping tables are mutable kernel memory.

## Dependencies and Integration Points
It includes `<linux/types.h>` and `<linux/compiler.h>`. Integration points include tty/vt, loadkeys, setfont, console display drivers, keyboard input, and legacy terminal tooling.

## Risks and Test Signals
Tests should cover ioctl numbers, privilege checks for dangerous IO operations, font buffer sizing, Unicode map limits, keyboard mode transitions, LED flag versus light state, diacritic table bounds, and 32/64-bit pointer fields in font operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/kd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/kdev_t.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/kdev_t.h

## Purpose
`kdev_t.h` provides old userspace macros for encoding and decoding device numbers when not compiling inside the kernel.

## Important APIs, Types, and Functions
`MAJOR(dev)` extracts the high 8 bits, `MINOR(dev)` extracts the low 8 bits, and `MKDEV(ma, mi)` composes the old 8:8 device number format. The macros are hidden under `#ifndef __KERNEL__`.

## Control Flow
There is no runtime flow. Userspace source code may use these macros to interpret legacy device IDs.

## State and Persistence
Device numbers appear in filesystem metadata and stat results, but this header stores no state.

## Dependencies and Integration Points
It has no external include dependency. It integrates with legacy userspace code that expects Linux device-number helpers.

## Risks and Test Signals
Tests should ensure the header compiles in userspace and that legacy 8:8 encoding is not confused with modern wider `dev_t` encoding. Risk is mainly misuse in code that should rely on libc `major()`, `minor()`, and `makedev()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/kdev_t.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/kernel-page-flags.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/kernel-page-flags.h

## Purpose
`kernel-page-flags.h` assigns bit numbers for page flags exported through kernel page-monitoring interfaces such as `/proc/kpageflags`.

## Important APIs, Types, and Functions
Constants include `KPF_LOCKED`, `KPF_REFERENCED`, `KPF_UPTODATE`, `KPF_DIRTY`, `KPF_LRU`, `KPF_ACTIVE`, `KPF_SLAB`, `KPF_WRITEBACK`, `KPF_RECLAIM`, `KPF_BUDDY`, `KPF_MMAP`, `KPF_ANON`, `KPF_SWAPCACHE`, `KPF_SWAPBACKED`, compound page bits, huge/THP bits, unevictable, hwpoison, nopage, KSM, offline, zero page, idle, and page-table markers.

## Control Flow
Userspace reads page-flag bitmasks from procfs and decodes set bits using these constants. The kernel sets and clears underlying page flags during memory-management operations.

## State and Persistence
The bitmasks reflect live physical page state and are highly volatile. No state is stored by the header.

## Dependencies and Integration Points
It has no includes. Integration points include procfs page monitors, memory diagnostics, NUMA/VM tooling, crash analysis, and tests for reclaim/compaction behavior.

## Risks and Test Signals
Tests should validate bit numbering against `/proc/kpageflags`, reserved/unused flags, THP/compound transitions, idle-page tracking, and permission restrictions for page-monitoring files. ABI risk is that bit numbers are externally decoded and must remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/kernel-page-flags.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/kernel.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/kernel.h

## Purpose
`kernel.h` is a small umbrella UAPI header that exposes generic kernel userspace definitions by including `sysinfo` and constant-expression helpers.

## Important APIs, Types, and Functions
This header defines no direct symbols in this snapshot. It includes `<linux/sysinfo.h>` and `<linux/const.h>`.

## Control Flow
There is no control flow. Its role is include compatibility for userspace code that expects `<linux/kernel.h>` to pull in common kernel UAPI definitions.

## State and Persistence
No state is represented.

## Dependencies and Integration Points
It integrates indirectly with `sysinfo(2)` structure definitions and constant macros used by Linux UAPI headers.

## Risks and Test Signals
Tests should verify userspace inclusion, absence of kernel-only leakage, and compatibility with libc headers. Risk is low, but adding broad definitions here can create namespace conflicts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/kernel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/kexec.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/kexec.h

## Purpose
`kexec.h` defines flags, architecture identifiers, segment limits, and userspace segment layout for the `kexec_load` and `kexec_file_load` system calls.

## Important APIs, Types, and Functions
Flags include crash load, preserve context, update ELF core header, crash hotplug support, file unload, file crash load, no initramfs, debug, no CMA, and force DTB. `KEXEC_ARCH_*` constants encode target architecture in high bits masked by `KEXEC_ARCH_MASK`. `KEXEC_SEGMENT_MAX` is 16. In userspace, `struct kexec_segment` contains user buffer pointer/size and destination memory pointer/size.

## Control Flow
Userspace loads kernel images and optional initramfs/segments into reserved memory, optionally for crash kernels. On reboot or panic, the kernel jumps to the prepared image.

## State and Persistence
Loaded kexec image state persists in kernel memory until unloaded, replaced, executed, or rebooted. Crash-kernel state may interact with reserved memory and elfcorehdr updates.

## Dependencies and Integration Points
It includes `<linux/types.h>`. Integration points include kexec-tools, crash dump infrastructure, architecture boot code, memory reservation, and secure/kernel image verification paths.

## Risks and Test Signals
Tests should cover flag validation, architecture mismatch rejection, segment overlap/bounds checking, max segment count, crash hotplug updates, unload behavior, and pointer-size compatibility for `kexec_segment`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/kexec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/keyboard.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/keyboard.h

## Purpose
`keyboard.h` defines virtual-console key symbol encoding, key types, modifier groups, function-key values, keypad/dead/accent/cursor/lock/braille/CSI symbols, and related table limits.

## Important APIs, Types, and Functions
`K(t,v)` packs key type and value; `KTYP` and `KVAL` unpack them. Modifier groups include shift, altgr, ctrl, alt, left/right variants, and caps shift. Key types include latin, function, special, keypad, dead key, console switch, cursor, shift, meta, ASCII, lock, letter, sticky lock, second dead-key set, braille, and CSI. The file enumerates `K_F1` through `K_F245` plus special actions, keypad keys, dead diacritics, cursor keys, lock symbols, braille dots, CSI escape keys, and table limits such as `NR_KEYS`, `MAX_NR_KEYMAPS`, `MAX_NR_FUNC`, and `MAX_DIACR`.

## Control Flow
Console keymap tools and the vt keyboard layer encode/decode key symbols with these macros. When key events arrive, the kernel consults keymaps indexed by modifier state and emits characters, escape sequences, console actions, or special control behavior.

## State and Persistence
The mutable state is in kernel keymap/function-string/diacritic tables and modifier/lock state, controlled through `kd.h` ioctls. This header only defines encodings.

## Dependencies and Integration Points
It includes `<linux/wait.h>`. Integration points include vt keyboard code, loadkeys/dumpkeys, console switching, braille input, terminal escape generation, and keyboard ioctls.

## Risks and Test Signals
Tests should verify `K/KTYP/KVAL` packing, max table bounds, no overlap between key types, CSI sequence values, dead-key limits, and compatibility with existing keymap files. ABI risk is high because keymap binaries rely on numeric values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/keyboard.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/keyctl.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/keyctl.h

## Purpose
`keyctl.h` defines operation codes, special keyring IDs, default request-key destinations, crypto parameter structures, public-key operation structures, move flags, and capability bits for the Linux key retention service.

## Important APIs, Types, and Functions
Special IDs address thread, process, session, user, user-session, group, request-key auth, and requestor keyrings. `KEYCTL_*` opcodes cover keyring lookup/join, update, revoke, chown, permissions, describe, clear, link/unlink/search/read, instantiate/negate/reject, timeout, authority, security label, parent session migration, persistent keyrings, Diffie-Hellman, public-key query/encrypt/decrypt/sign/verify, restriction, move, capabilities, and watch. Structures include `keyctl_dh_params`, `keyctl_kdf_params`, `keyctl_pkey_query`, and `keyctl_pkey_params`.

## Control Flow
Userspace calls the `keyctl` syscall with an opcode and operation-specific arguments. The kernel resolves key IDs or special keyrings, checks permissions and namespaces, then mutates key/keyring state or performs crypto operations.

## State and Persistence
Keys and keyrings are kernel objects with ownership, permissions, expiry, revocation, links, quotas, and namespace/user associations. Persistent keyrings can survive login sessions according to kernel policy.

## Dependencies and Integration Points
It includes `<linux/types.h>`. Integration points include request-key upcalls, fscrypto, network filesystems, module verification, public-key crypto, watch queues, user namespaces, and security labels.

## Risks and Test Signals
Tests should cover permission bits, special keyring resolution, quota/expiry/revocation, instantiate authorization, move exclusivity, capability bitmap length, watch notifications, and crypto buffer sizing. Security risk is high because the ABI controls credentials and secret material.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/keyctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/kfd_ioctl.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/kfd_ioctl.h

## Purpose
`kfd_ioctl.h` defines the AMD Kernel Fusion Driver compute UAPI for HSA/ROCm queues, memory, events, SVM, SMI events, CRIU checkpoint/restore, XNACK mode, runtime debugging, and process creation.

## Important APIs, Types, and Functions
The ABI version is 1.22. Queue APIs create, update, destroy, mask CUs, inspect wave state, and allocate GWS. Memory APIs set policy, acquire DRM VM, allocate/free/map/unmap GPU memory, import/export dma-bufs, query dma-buf info, and query available memory. Event APIs create/destroy/set/reset/wait events and carry memory, hardware, and signal data. SMI definitions expose event IDs, trigger enums, mask macros, event strings, and anonymous event FDs. CRIU structures describe process info, device buckets, BO buckets, and restore metadata. SVM uses `kfd_ioctl_svm_args` with variable attributes. Debug APIs use `kfd_ioctl_dbg_trap_args` as an operation multiplexer with many operation-specific structures. Ioctl macros run from `AMDKFD_IOC_GET_VERSION` through `AMDKFD_IOC_CREATE_PROCESS`.

## Control Flow
ROCm userspace queries version and apertures, creates GPU queues, allocates or imports memory, maps it to one or more GPU IDs, waits for events, and controls SVM attributes. Debuggers enable runtime/debug sessions, subscribe to exceptions, suspend/resume queues, set watchpoints, query snapshots, and clear events. CRIU flows pause/evict queues, checkpoint BOs and private state, unpause, restore, and resume.

## State and Persistence
State is per process, per GPU, per queue, per memory handle, per event, per SVM range, and per debug session. Handles and queue IDs persist until explicit destruction or process/device teardown. SMI event FDs hold masks and FIFO state. XNACK mode is process-wide and constrained by active queues.

## Dependencies and Integration Points
It includes `<drm/drm.h>` and `<linux/ioctl.h>`. Integration points include AMDGPU DRM render nodes, ROCm runtime, HSA queues, dma-buf, TTM memory migration, SVM/MMU notifiers, GPU reset/RAS events, CRIU, ptrace/debuggers, and sysfs capability headers.

## Risks and Test Signals
ABI risk is very high: many structs contain userspace pointers, variable arrays, bidirectional counters, version-gated fields, and security-sensitive debug controls. Tests should cover ioctl numbering, structure sizes, partial map/unmap `n_success`, memory flag validation, queue lifetime, event wait timeouts, SVM overlap splitting and aggregation, XNACK refusal with active queues, CRIU operation ordering, SMI privilege gating, debug permission/ptrace checks, snapshot entry sizing, and 32/64-bit compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/kfd_ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/kfd_sysfs.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/kfd_sysfs.h

## Purpose
`kfd_sysfs.h` defines bit masks and numeric values exported through AMD KFD sysfs topology nodes for HSA node capabilities, debug capabilities, memory heaps, caches, and IO links.

## Important APIs, Types, and Functions
Capability bits describe hotplug, ATS, graphics sharing, queue size constraints, idle events, VA limits, watchpoints, doorbell types, trap-debug support, memory RAS/EDC, SVM API, coherent host access, firmware trap support, precise ALU/memory debug support, and per-queue reset support. `HSA_CAP2_*` extends capabilities. Debug properties define watch address mask fields and dispatch-info validity. Memory heap types, memory flags, cache types, IO link types, and IO link flags describe topology resources and link semantics.

## Control Flow
Userspace reads sysfs topology attributes, decodes numeric bitfields using these constants, and decides which ROCm/HSA features can be enabled for each GPU node and link.

## State and Persistence
The values reflect live hardware/driver topology and capabilities. They persist while the device is present but can change with driver updates, hotplug, or reset.

## Dependencies and Integration Points
The header has no includes. Integration points include `/sys/class/kfd/kfd/topology`, ROCm runtime discovery, debuggers, memory allocators, peer-to-peer routing, and capability checks before using `kfd_ioctl.h` ioctls.

## Risks and Test Signals
Tests should verify bit decoding, reserved-mask handling, consistency with ioctl-reported capabilities, multi-GPU IO link types/flags, and capability-gated feature enablement. ABI risk is in preserving bit meanings and not reusing reserved bits incorrectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/kfd_sysfs.h -->
