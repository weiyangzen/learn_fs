# Research: subset-b-005984

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/kvm.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/kvm.h

Purpose: defines the public `/dev/kvm` userspace ABI for creating virtual machines, configuring VM memory and devices, creating and running vCPUs, exchanging exit reasons through the shared `struct kvm_run` page, managing interrupts, reading/writing register state, dirty logging, stats, confidential/private guest memory, and architecture-specific extension plumbing.

Important APIs and types: `KVM_API_VERSION`, `struct kvm_userspace_memory_region`, `struct kvm_userspace_memory_region2`, memory flags such as `KVM_MEM_LOG_DIRTY_PAGES`, `KVM_MEM_READONLY`, and `KVM_MEM_GUEST_MEMFD`, `struct kvm_run`, `KVM_EXIT_*`, `struct kvm_irq_routing`, `struct kvm_irqfd`, `struct kvm_ioeventfd`, `struct kvm_enable_cap`, `struct kvm_one_reg`, `struct kvm_dirty_gfn`, `struct kvm_stats_header`, `struct kvm_stats_desc`, `struct kvm_memory_attributes`, and `struct kvm_create_guest_memfd` form the key ABI. The ioctl families are split by fd type: system fd ioctls such as `KVM_GET_API_VERSION`, `KVM_CREATE_VM`, and `KVM_CHECK_EXTENSION`; VM fd ioctls such as memory region setup, IRQ routing, device creation, guest memfd, and memory attributes; device fd ioctls; and vCPU fd ioctls such as `KVM_RUN`, register access, CPUID/MSR access, one-reg access, guest debug, nested state, and reset paths.

Control flow: a VMM checks `KVM_GET_API_VERSION` and capabilities, creates a VM fd, installs memory slots, optional irqchip/PIT/routes/ioeventfd/irqfd/device fds, creates vCPUs, mmaps each vCPU run area, initializes architecture state, and loops on `KVM_RUN`. On each exit, userspace dispatches by `kvm_run.exit_reason`; common exits report I/O, MMIO, hypercalls, system events, MSR traps, memory faults, TDX/SNP/ARM RAS exits, and arch-specific conditions. Userspace may re-enter after satisfying emulation or updating shared fields such as `immediate_exit`, `cr8`, dirty sync registers, or exit-specific return data.

State and persistence: this header does not store state itself, but its structs define how KVM VM state is serialized across ioctl calls and run-page mappings. Persistent or migration-relevant surfaces include memory slot layout, dirty bitmaps/rings, IRQ routing, device attributes, vCPU registers, CPUID/MSRs, nested virtualization state, guest_memfd private memory, memory attributes, binary stats fds, and architecture-specific state from `<asm/kvm.h>`. Reserved padding and fixed union sizes are part of the ABI and must be preserved.

Dependencies and integration points: depends on `linux/types.h`, `linux/ioctl.h`, `linux/compiler.h`, `linux/stddef.h`, `asm/kvm.h`, and kernel-only `linux/kvm_types.h`. It integrates VMMs such as QEMU/Cloud Hypervisor/crosvm with KVM core, architecture KVM, eventfd, VFIO device assignment, Hyper-V/Xen/PAPR/RISC-V/LoongArch paravirtual interfaces, dirty logging, confidential computing, memory attributes, and media-like stats fd readers.

Risks and test signals: highest risk is ABI drift: changing ioctl numbers, struct packing, padding, union size, flag bits, capability numbers, or exit semantics breaks existing VMMs. `struct kvm_run` is explicitly TOCTOU-sensitive because userspace may mutate the mmaped page while KVM runs. Test with KVM selftests for API version/capability discovery, memory slots including `KVM_SET_USER_MEMORY_REGION2`, dirty log ring state transitions, ioeventfd/irqfd routing, register round trips, stats fd parsing, confidential guest memory faults, architecture compile matrices, and VMM boot/migration smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/kvm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/kvm_para.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/kvm_para.h

Purpose: defines the generic UAPI hypercall number and error-code namespace used by KVM paravirtualized guests, then includes the architecture-specific paravirtual header.

Important APIs and types: exported values include KVM hypercall error returns such as `KVM_ENOSYS`, `KVM_EFAULT`, `KVM_EINVAL`, `KVM_E2BIG`, `KVM_EPERM`, and `KVM_EOPNOTSUPP`, plus hypercall IDs `KVM_HC_VAPIC_POLL_IRQ`, `KVM_HC_MMU_OP`, `KVM_HC_FEATURES`, `KVM_HC_PPC_MAP_MAGIC_PAGE`, `KVM_HC_KICK_CPU`, `KVM_HC_MIPS_GET_CLOCK_FREQ`, `KVM_HC_MIPS_EXIT_VM`, `KVM_HC_MIPS_CONSOLE_OUTPUT`, `KVM_HC_CLOCK_PAIRING`, `KVM_HC_SEND_IPI`, `KVM_HC_SCHED_YIELD`, and `KVM_HC_MAP_GPA_RANGE`.

Control flow: guest code uses architecture-provided `kvm_hypercall*` helpers and feature discovery to invoke these numeric operations on the host. The generic header only reserves IDs and return codes; calling convention and feature bits are provided by `<asm/kvm_para.h>`.

State and persistence: no local state. The ABI affects guest/host behavior at runtime, but any state changed by a hypercall is owned by the KVM host or guest architecture code.

Dependencies and integration points: includes `<asm/kvm_para.h>` and expects architectures to provide `kvm_hypercall0`, `kvm_hypercall1`, feature queries, and availability checks. It is consumed by paravirtual guest kernels and low-level KVM support code.

Risks and test signals: risks are numeric ID collisions, architecture mismatch, and guests issuing hypercalls not advertised by feature discovery. Test by compiling guest headers on supported architectures and running KVM paravirtual feature selftests for clock pairing, IPI, sched-yield, and GPA-range mapping where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/kvm_para.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/l2tp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/l2tp.h

Purpose: defines the userspace ABI for L2TP-over-IP sockets and the generic netlink family used to manage L2TP tunnels and sessions.

Important APIs and types: `struct sockaddr_l2tpip` and `struct sockaddr_l2tpip6` encode IPv4/IPv6 L2TP-over-IP socket addresses with connection IDs. Generic netlink commands include tunnel/session create, delete, modify, and get operations. Attributes cover pseudowire type, encapsulation type, protocol version, interface name, connection/session IDs, cookies, sequencing flags, IP/UDP addressing, checksums, file descriptors, and nested stats. Enums define `l2tp_pwtype`, `l2tp_l2spec_type`, `l2tp_encap_type`, `l2tp_seqmode`, and debug flags. The family is `L2TP_GENL_NAME` version `L2TP_GENL_VERSION`.

Control flow: userspace creates sockets or sends generic netlink messages to create a tunnel, bind it to UDP or raw IP encapsulation, create sessions under that tunnel, then queries stats or deletes objects. Kernel validation keys off command-specific attributes.

State and persistence: no state in the header. Runtime state lives in kernel L2TP tunnel/session objects and netdevice/socket state. Stats attributes expose packet, byte, error, sequence discard, cookie discard, and invalid-packet counters.

Dependencies and integration points: depends on `linux/types.h`, `linux/socket.h`, `linux/in.h`, and `linux/in6.h`. Integrates socket address handling, generic netlink policy, L2TP netdevices, UDP/IP encapsulation, and userspace tunnel managers.

Risks and test signals: risks include sockaddr layout compatibility, netlink attribute length/type drift, unused legacy attributes misleading callers, and IPv6 zero-checksum handling mistakes. Test with generic netlink create/get/delete flows, IPv4 and IPv6 socket binding, UDP and IP encapsulation, cookie validation, stats reporting, and invalid attribute fuzzing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/l2tp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/landlock.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/landlock.h

Purpose: defines the Landlock sandboxing userspace API: ruleset attributes, rule types, filesystem and network access-right bits, scoping bits, ruleset creation flags, and self-restriction logging/thread-synchronization flags.

Important APIs and types: `struct landlock_ruleset_attr` declares handled filesystem rights, handled network rights, and domain scopes. `LANDLOCK_CREATE_RULESET_VERSION` and `LANDLOCK_CREATE_RULESET_ERRATA` query ABI version and fixed errata. `LANDLOCK_RESTRICT_SELF_LOG_*` and `LANDLOCK_RESTRICT_SELF_TSYNC` tune audit logging and multithreaded enforcement. `enum landlock_rule_type`, `struct landlock_path_beneath_attr`, and `struct landlock_net_port_attr` describe path hierarchy and TCP-port rules. Access masks include `LANDLOCK_ACCESS_FS_*`, `LANDLOCK_ACCESS_NET_BIND_TCP`, `LANDLOCK_ACCESS_NET_CONNECT_TCP`, and `LANDLOCK_SCOPE_*`.

Control flow: userspace creates a ruleset with a declared set of handled rights, adds path or port rules, then restricts the current process or thread group. Later filesystem, TCP bind/connect, UNIX socket resolution, abstract socket, and signal checks are mediated by the resulting Landlock domain.

State and persistence: the header has no storage. Runtime policy is held by kernel Landlock domains attached to tasks and inherited across fork/exec according to Landlock rules. Policies are process state, not filesystem persistence.

Dependencies and integration points: depends on `linux/types.h`; integrates with Landlock syscalls, LSM hooks, audit logging, pathname resolution, TCP socket operations, UNIX sockets, signal delivery, `no_new_privs`, and thread synchronization.

Risks and test signals: risks include ABI-version mismatch, forgetting to set handled rights, special `LANDLOCK_ACCESS_FS_REFER` deny-by-default semantics, packed path rule layout, port 0 ephemeral behavior, and over/under-auditing. Test all ABI versions, unknown flag rejection, packed struct size, path rule inheritance, rename/link constraints, TCP bind/connect per port, scope denials, TSYNC behavior, and audit logging toggles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/landlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/libc-compat.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/libc-compat.h

Purpose: coordinates Linux UAPI headers with C library headers so duplicate structs, enums, and macros are defined by exactly one side when headers are included in either order.

Important APIs and types: it exports guard macros such as `__UAPI_DEF_IF_IFCONF`, `__UAPI_DEF_IF_IFMAP`, `__UAPI_DEF_IF_IFNAMSIZ`, `__UAPI_DEF_IF_IFREQ`, `__UAPI_DEF_IF_NET_DEVICE_FLAGS`, `__UAPI_DEF_IN_ADDR`, `__UAPI_DEF_IN_IPPROTO`, `__UAPI_DEF_IN_PKTINFO`, `__UAPI_DEF_IP_MREQ`, `__UAPI_DEF_SOCKADDR_IN`, `__UAPI_DEF_IN_CLASS`, IPv6 equivalents, and `__UAPI_DEF_XATTR`.

Control flow: UAPI headers include this file early, then wrap conflicting definitions in `#if __UAPI_DEF_*`. If glibc headers such as `net/if.h`, `netinet/in.h`, or `sys/xattr.h` are already included, corresponding Linux definitions are suppressed. If Linux headers are included first, the macros tell libc headers to avoid redefining the same constructs. Non-glibc libraries can predefine macros to opt out.

State and persistence: no runtime state. The state is preprocessor inclusion order and feature macro detection.

Dependencies and integration points: integrates Linux UAPI headers with glibc and other libc implementations, especially networking and xattr headers. It indirectly protects downstream builds that mix libc and kernel UAPI includes.

Risks and test signals: risks are redefinition warnings/errors, missing definitions, incorrect glibc feature-test macro handling, and stale coordination as libc adds symbols. Test include-order matrices for `<linux/if.h>`, `<net/if.h>`, `<linux/in.h>`, `<netinet/in.h>`, `<linux/xattr.h>`, and `<sys/xattr.h>` under glibc and non-glibc toolchains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/libc-compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/limits.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/limits.h

Purpose: exposes core Linux userspace limit constants for file descriptors, groups, argument length, path/name lengths, pipe atomicity, xattr sizes, and real-time signal count.

Important APIs and types: constants include `NR_OPEN`, `NGROUPS_MAX`, `ARG_MAX`, `LINK_MAX`, `MAX_CANON`, `MAX_INPUT`, `NAME_MAX`, `PATH_MAX`, `PIPE_BUF`, `XATTR_NAME_MAX`, `XATTR_SIZE_MAX`, `XATTR_LIST_MAX`, and `RTSIG_MAX`.

Control flow: there is no executable flow. User and kernel headers include these constants when validating buffers, path lengths, pipe writes, group arrays, and xattr data.

State and persistence: no state. The constants shape ABI expectations and buffer sizing.

Dependencies and integration points: standalone UAPI header used by libc, tools, filesystems, xattr consumers, shell/runtime code, and kernel UAPI consumers.

Risks and test signals: risks are changing values that applications compile into fixed buffers, and mismatch with libc `limits.h` or runtime sysconf behavior. Test by compiling representative userspace headers, checking xattr boundary tests, path/name limit tests, pipe atomic write behavior, and group/exec argument limit validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/limits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/lirc.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/lirc.h

Purpose: defines the Linux infrared remote-control userspace ABI for raw pulse/space streams, scancode reporting, device feature discovery, and LIRC ioctl controls.

Important APIs and types: mode2 encoding macros include `LIRC_SPACE`, `LIRC_PULSE`, `LIRC_FREQUENCY`, `LIRC_TIMEOUT`, `LIRC_OVERFLOW`, `LIRC_VALUE`, `LIRC_MODE2`, and type predicates. Feature flags describe send/receive modes, carrier/duty/transmitter controls, receive timeout, carrier measurement, wideband receiver, and masks. Ioctls include `LIRC_GET_FEATURES`, mode getters/setters, carrier/duty/timeout controls, transmitter mask, wideband receiver, and receive timeout retrieval. `struct lirc_scancode` carries timestamp, flags, protocol, keycode, and scancode. `enum rc_proto` enumerates supported IR protocols.

Control flow: userspace queries features, selects a send or receive mode, configures carrier/timeout behavior when supported, then reads mode2 words or `lirc_scancode` records or writes transmit data. Kernel drivers encode raw timing and decoded protocol state according to mode and feature flags.

State and persistence: runtime state lives in each LIRC/rc device: selected modes, carrier settings, timeout reporting, protocol decoding, and queued events. No persistent state is stored by the header.

Dependencies and integration points: depends on `linux/types.h` and `linux/ioctl.h`; integrates rc-core drivers, `/dev/lirc*`, lircd-style userspace, input keycode mapping, and protocol decoders.

Risks and test signals: risks include mode2 high-bit encoding mistakes, feature flags advertising unsupported ioctls, protocol enum drift, timestamp expectations, and unused compatibility flags. Test ioctl feature/mode negotiation, raw pulse read/write, timeout and overflow events, scancode flags for toggle/repeat, protocol-specific decode/encode, and unsupported ioctl rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/lirc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/liveupdate.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/liveupdate.h

Purpose: defines the `/dev/liveupdate` userspace ioctl ABI for creating/retrieving named live-update sessions and preserving/restoring file descriptors across a kernel live update.

Important APIs and types: constants include `LIVEUPDATE_IOCTL_TYPE`, `LIVEUPDATE_SESSION_NAME_LENGTH`, device command IDs, and session command IDs. Device-level structs are `struct liveupdate_ioctl_create_session` and `struct liveupdate_ioctl_retrieve_session`. Session fd structs are `struct liveupdate_session_preserve_fd`, `struct liveupdate_session_retrieve_fd`, and `struct liveupdate_session_finish`. Ioctl macros include `LIVEUPDATE_IOCTL_CREATE_SESSION`, `LIVEUPDATE_IOCTL_RETRIEVE_SESSION`, `LIVEUPDATE_SESSION_PRESERVE_FD`, `LIVEUPDATE_SESSION_RETRIEVE_FD`, and `LIVEUPDATE_SESSION_FINISH`.

Control flow: userspace opens `/dev/liveupdate`, creates a named session, issues preserve-FD operations with opaque tokens, the kernel carries preserved resources through live update phases, then the new userspace/kernel side retrieves the session by name, retrieves each preserved fd by token, and finishes the session to release kernel ownership.

State and persistence: the ABI is explicitly stateful. Session names, tokens, preserved file references, and snapshot/restoration metadata survive the live update boundary in kernel-managed memory. Structs use a first-field `size` convention; future extension requires zeroed unknown tail bytes.

Dependencies and integration points: depends on `linux/ioctl.h` and `linux/types.h`. Integrates live update orchestration, fd-type-specific preservation support such as memfd/KVM/iommufd/VFIO, kernel reference counting, and userspace agents that coordinate update phases.

Risks and test signals: risks include nonzero unknown extension fields, token collision or lifetime bugs, restoring unsupported fd types, leaking preserved references on failed finish, and state-machine misuse outside the updated state. Test size negotiation, malformed names, duplicate sessions, preserve/retrieve token ordering, unsupported fd rejection, repeated finish, ENOENT paths, and live-update cycle cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/liveupdate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/llc.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/llc.h

Purpose: defines the IEEE 802.2 LLC userspace socket address, socket options, SAP constants, and ancillary packet-info ABI.

Important APIs and types: `struct sockaddr_llc` carries LLC family, ARP hardware type, TEST/XID/UA fields, SAP, MAC address, and padding. `enum llc_sockopts` defines retry, PDU size, timer expiry, TX/RX window, and packet-info options. Limits such as `LLC_OPT_MAX_RETRY`, `LLC_OPT_MAX_SIZE`, and timer maxima constrain socket options. `LLC_SAP_*` constants define well-known service access points. `struct llc_pktinfo` reports interface index, SAP, and MAC address.

Control flow: userspace opens AF_LLC sockets, binds/connects with `sockaddr_llc`, tunes LLC behavior through sockopts, and may receive packet metadata through `LLC_OPT_PKTINFO`.

State and persistence: socket option values, connection state, timers, and windows are kernel socket state. No persistent storage is defined here.

Dependencies and integration points: depends on `linux/socket.h` and `linux/if.h`; integrates LLC networking, Ethernet MAC addressing, ancillary data, and legacy protocol users.

Risks and test signals: risks include fixed sockaddr size/padding mismatch, invalid SAP values, option limit validation, timer overflow, and ancillary data layout drift. Test AF_LLC bind/connect/send/recv, sockopt boundaries, pktinfo delivery, and SAP-specific behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/llc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/loadpin.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/loadpin.h

Purpose: defines the LoadPin userspace ioctl used to configure trusted dm-verity root digests through securityfs.

Important APIs and types: `LOADPIN_IOC_MAGIC` and `LOADPIN_IOC_SET_TRUSTED_VERITY_DIGESTS` are the only exported ABI items. The ioctl takes an unsigned-int-sized fd argument identifying a file containing ASCII root digests.

Control flow: userspace writes or prepares a digest list file, opens the LoadPin securityfs control node `loadpin/dm-verity`, and calls the ioctl with the digest-list fd. The kernel reads and installs trusted verity digests used by LoadPin policy.

State and persistence: trusted digest configuration is kernel security-module state and may affect subsequent file-loading decisions. The header itself stores nothing; persistence across boot/update depends on userspace reconfiguration.

Dependencies and integration points: depends on ioctl numbering and securityfs exposure from LoadPin. Integrates dm-verity, LoadPin LSM policy, and boot/update trust provisioning tools.

Risks and test signals: risks include wrong ioctl target, malformed digest files, fd lifetime/permission mistakes, and failure to reject unsupported formats. Test securityfs ioctl success/failure, valid and invalid digest lists, repeated configuration, and enforcement against trusted/untrusted verity-backed loads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/loadpin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/lockd_netlink.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/lockd_netlink.h

Purpose: provides the generated generic-netlink UAPI for lockd server configuration and status.

Important APIs and types: `LOCKD_FAMILY_NAME` is `"lockd"` and version is `LOCKD_FAMILY_VERSION`. Attributes include `LOCKD_A_SERVER_GRACETIME`, `LOCKD_A_SERVER_TCP_PORT`, and `LOCKD_A_SERVER_UDP_PORT`. Commands include `LOCKD_CMD_SERVER_SET` and `LOCKD_CMD_SERVER_GET`.

Control flow: netlink clients issue server get/set commands with grace-time and port attributes. The lockd kernel family applies or reports NFS lock daemon settings according to its generated YNL policy.

State and persistence: runtime lockd server settings and grace-period state live in the kernel lockd/NFS server subsystem. The header stores no data and does not define persistence across service restart.

Dependencies and integration points: generated from `Documentation/netlink/specs/lockd.yaml`; integrates generic netlink/YNL tooling, lockd, and NFS server administration tools.

Risks and test signals: risks include generated header/spec drift, enum renumbering, invalid port validation, and inconsistent get/set behavior. Test YNL schema generation, netlink get/set with valid and invalid attributes, and lockd server behavior after configuration changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/lockd_netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/loop.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/loop.h

Purpose: defines the loop block-device userspace ABI for attaching regular files or block devices as loop devices, querying/configuring status, and controlling `/dev/loop-control`.

Important APIs and types: constants include `LO_NAME_SIZE`, `LO_KEY_SIZE`, loop flags `LO_FLAGS_READ_ONLY`, `LO_FLAGS_AUTOCLEAR`, `LO_FLAGS_PARTSCAN`, and `LO_FLAGS_DIRECT_IO`, plus settable/clearable masks. `struct loop_info` is the legacy status format, `struct loop_info64` is the 64-bit status format, and `struct loop_config` supports atomic setup through `LOOP_CONFIGURE`. Ioctls include `LOOP_SET_FD`, `LOOP_CLR_FD`, status get/set, `LOOP_CHANGE_FD`, `LOOP_SET_CAPACITY`, direct I/O, block size, configure, and loop-control add/remove/get-free.

Control flow: userspace opens a loop device, attaches a backing fd, optionally sets offset/size/name/flags/block size, scans partitions, uses the block device, then clears or autoclears it. `LOOP_CONFIGURE` combines setup and configuration to avoid partial state.

State and persistence: runtime state is per loop device: backing file reference, offset, size limit, flags, block size, file/crypt names, and obsolete crypto fields. It is not persistent after detach or reboot unless userspace recreates it.

Dependencies and integration points: depends on `asm/posix_types.h` and `linux/types.h`; integrates block layer, partition scanning, util-linux `losetup`, udev, direct I/O, and legacy loop crypto compatibility.

Risks and test signals: risks include legacy struct width differences, partial configuration races, wrong flag mutability, direct I/O alignment, block size validation, and stale partition tables. Test attach/detach, atomic configure, read-only/autoclear/partscan/direct-io flags, capacity changes, backing fd replacement, 32-bit userspace ABI, and loop-control allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/loop.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/lp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/lp.h

Purpose: defines the legacy parallel-printer `/dev/lp*` userspace ABI: status flags, 8255 status bits, default timing constants, and printer ioctl numbers.

Important APIs and types: status flags include `LP_EXIST`, `LP_SELEC`, `LP_BUSY`, `LP_OFFL`, `LP_NOPA`, `LP_ERR`, `LP_ABORT`, `LP_ABORTOPEN`, `LP_NO_REVERSE`, and `LP_DATA_AVAIL`. Hardware status bits include `LP_PBUSY`, `LP_PACK`, `LP_POUTPA`, `LP_PSELECD`, and `LP_PERRORP`. Timing constants include `LP_INIT_CHAR`, `LP_INIT_WAIT`, `LP_INIT_TIME`, `LP_TIMEOUT_INTERRUPT`, and `LP_TIMEOUT_POLLED`. Ioctls include `LPCHAR`, `LPTIME`, `LPABORT`, IRQ get/set, `LPWAIT`, `LPABORTOPEN`, `LPGETSTATUS`, `LPRESET`, `LPGETFLAGS`, and `LPSETTIMEOUT`.

Control flow: userspace configures retry/abort, timing, IRQ/polling, and timeout behavior, writes print data, reads status, and can reset the printer. Some controls are obsolete but kept for ABI compatibility.

State and persistence: state is per printer device in the lp/parport driver: flags, timing settings, IRQ mode, and status cache. No persistent state is defined.

Dependencies and integration points: depends on `linux/types.h`, `linux/ioctl.h`, `HZ`, and word-size/time_t conditionals. Integrates the lp character device, parport, legacy tunelp tooling, and hardware status lines.

Risks and test signals: risks include old/new timeout ioctl selection on 32-bit time64 userspace, obsolete flag semantics, active-low/active-high status interpretation, and IRQ vs polling behavior. Test ioctl compatibility on 32/64-bit, status reading, timeout configuration, abort-open behavior, reset, and parport error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/lp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/lsm.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/lsm.h

Purpose: defines common userspace structures and identifiers for Linux Security Module context APIs.

Important APIs and types: `struct lsm_ctx` carries an LSM ID, LSM-specific flags, total record length, context length, and flexible context bytes. `LSM_ID_*` constants identify capability, SELinux, Smack, Tomoyo, AppArmor, Yama, LoadPin, SafeSetID, Lockdown, BPF, Landlock, IMA, EVM, and IPE. `LSM_ATTR_*` constants identify current, exec, fscreate, keycreate, previous, and socket-create security attributes. `LSM_FLAG_SINGLE` requests special single-record behavior.

Control flow: userspace LSM APIs return or accept one or more `lsm_ctx` records; callers iterate by `len`, interpret `ctx` according to `id`, and select requested attributes with `LSM_ATTR_*`.

State and persistence: no state in the header. Runtime context data comes from active LSMs and task/object security blobs. String contexts should be NUL-terminated when applicable; binary contexts are allowed.

Dependencies and integration points: depends on `linux/stddef.h`, `linux/types.h`, and `linux/unistd.h`; integrates LSM syscalls, security context queries, multi-LSM stacking, and userspace policy tools.

Risks and test signals: risks include incorrect flexible-array sizing, nonzero unused flags, string-vs-binary context assumptions, ID collisions, and multi-record parsing bugs. Test stacked LSM context retrieval, malformed `len`/`ctx_len`, `LSM_FLAG_SINGLE`, each supported attribute, and unknown IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/lsm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/lwtunnel.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/lwtunnel.h

Purpose: defines lightweight tunnel netlink attribute IDs used by routes with encapsulation actions.

Important APIs and types: `enum lwtunnel_encap_types` covers MPLS, IPv4, ILA, IPv6, Segment Routing, BPF, SEG6 local, RPL, IOAM6, and XFRM encapsulations. Attribute enums define IPv4/IPv6 tunnel IDs, source/destination addresses, TTL/hoplimit, TOS/traffic class, flags, options, Geneve/VXLAN/ERSPAN option layouts, BPF program fd/name attributes for in/out/xmit hooks, XMIT headroom, and XFRM if_id/link attributes. `LWT_BPF_MAX_HEADROOM` caps BPF tunnel headroom.

Control flow: route management tools encode lwtunnel attributes in rtnetlink route messages. Kernel routing decodes the selected encapsulation type and nested attributes, attaches tunnel state or BPF programs to the route, and applies them on forwarding/output.

State and persistence: route entries hold lwtunnel configuration in kernel FIB state. Persistence depends on userspace route configuration replay, not this header.

Dependencies and integration points: depends on `linux/types.h`; integrates rtnetlink, iproute2, MPLS, IP/IP6 tunnels, SEG6, BPF LWT hooks, XFRM interfaces, Geneve/VXLAN/ERSPAN options, and IOAM/RPL support.

Risks and test signals: risks include nested attribute policy drift, unsupported encap type handling, BPF headroom bounds, address-family confusion, and route dump/restore incompatibility. Test iproute2 add/dump/delete for every encap type, invalid nested attrs, BPF fd lifetime, XFRM link attributes, and packet-path forwarding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/lwtunnel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/magic.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/magic.h

Purpose: publishes filesystem and pseudo-filesystem magic numbers used by `statfs(2)`, filesystem detection tools, and kernel/userspace ABI checks.

Important APIs and types: constants cover many on-disk and virtual filesystems, including `CEPH_SUPER_MAGIC`, `EXT*_SUPER_MAGIC`, `BTRFS_SUPER_MAGIC`, `FUSE_SUPER_MAGIC`, `NFS_SUPER_MAGIC`, `CIFS_SUPER_MAGIC`, `SMB2_SUPER_MAGIC`, `PROC_SUPER_MAGIC`, `SYSFS_MAGIC`, `BPF_FS_MAGIC`, `ZONEFS_MAGIC`, `GUEST_MEMFD_MAGIC`, and many legacy filesystem identifiers. Some entries are string magic values for ReiserFS variants.

Control flow: no executable flow. Callers compare returned magic values from `statfs`/`statx`-adjacent logic or on-disk probes to identify filesystems or special pseudo-filesystems.

State and persistence: no state. Numeric values are ABI identifiers and must remain stable.

Dependencies and integration points: standalone UAPI header used by filesystem utilities, mount helpers, container runtimes, sandboxes, backup tools, and kernel code exposing filesystem type values.

Risks and test signals: risks are collisions, accidental renumbering, confusing superblock magic with on-disk probe strings, and missing new filesystem constants. Test `statfs` magic comparisons for representative mounted filesystems, userspace build compatibility, and uniqueness/static analysis of assigned values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/magic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/major.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/major.h

Purpose: exposes legacy and reserved Linux major device numbers for character and block devices.

Important APIs and types: constants include well-known majors for memory/ramdisk, floppy/PTY/IDE/TTY/LP/VCS/loop, SCSI disks/tapes/CD-ROM/generic, misc, framebuffer, MTD, netlink, NBD, DASD, raw, USB, MMC, Xen block, MSR, CPUID, IBM terminal devices, block extended major, and many legacy hardware assignments.

Control flow: no executable flow. Code and tools use these values to interpret or construct device numbers, though modern systems normally allocate many majors dynamically.

State and persistence: no state. The values are ABI allocations and device-node compatibility anchors.

Dependencies and integration points: integrates device-number documentation, static `/dev` creation, udev-like tools, old drivers, block/char device registration, and compatibility code.

Risks and test signals: risks include collisions, using static majors for dynamically allocated drivers, and confusing overlapping historical aliases such as ramdisk/mem or VCS/loop. Test static device-node creation, driver registration conflicts, documentation consistency, and userspace tools that decode `st_rdev`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/major.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/map_benchmark.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/map_benchmark.h

Purpose: defines the DMA mapping benchmark ioctl ABI used to measure map/unmap latency under configurable thread, duration, NUMA, addressing, direction, transfer-delay, and map-mode settings.

Important APIs and types: `DMA_MAP_BENCHMARK` is the ioctl over magic `'d'`. Limits include `DMA_MAP_MAX_THREADS`, `DMA_MAP_MAX_SECONDS`, and `DMA_MAP_MAX_TRANS_DELAY`. Direction constants include bidirectional, to-device, and from-device. Modes distinguish single-page and scatterlist tests. `struct map_benchmark` carries output averages/stddevs and input parameters such as threads, seconds, NUMA node, DMA bits, DMA direction, transfer delay, granule, map mode, and reserved expansion.

Control flow: userspace fills benchmark parameters, calls the ioctl, the kernel runs map/unmap loops for the requested duration and concurrency, then returns latency statistics in 100ns units and standard deviations.

State and persistence: benchmark state is temporary per ioctl call. Results are returned to userspace and not persisted by the kernel.

Dependencies and integration points: depends on `linux/types.h` and time constants such as `NSEC_PER_MSEC`; integrates DMA API benchmarking, NUMA allocation, scatterlist mapping, and device-specific DMA mask behavior.

Risks and test signals: risks include excessive threads/runtime, invalid DMA direction, NUMA node handling, overflow in timing/statistics, and reserved field misuse. Test parameter bounds, both map modes, all directions, high thread counts, invalid nodes, timing overflow, and reserved-field zeroing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/map_benchmark.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/map_to_14segment.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/map_to_14segment.h

Purpose: provides UAPI-visible helpers and default ASCII lookup tables for mapping characters to 14-segment display bitmasks.

Important APIs and types: bit indices `BIT_SEG14_*` name all segment positions plus reserved bits. `struct seg14_conversion_map` stores 128 big-endian 16-bit entries. `map_to_seg14()` validates an ASCII index and returns a CPU-endian segment mask or `-EINVAL`. `SEG14_CONVERSION_MAP`, `SEG14_DEFAULT_MAP`, `MAP_TO_SEG14_SYSFS_FILE`, `_SEG14`, and `MAP_ASCII14SEG_ALPHANUM` provide static map construction and sysfs naming.

Control flow: a display driver instantiates a conversion map, optionally exposes it through a sysfs binary-like attribute, then converts each character to a segment bitmask before driving hardware. Userspace can replace the table if the driver exposes `map_seg14`.

State and persistence: map state is a driver-owned `struct seg14_conversion_map`; updates via sysfs are runtime driver state and not persisted unless userspace reloads them.

Dependencies and integration points: depends on `linux/errno.h`, `linux/types.h`, and `asm/byteorder.h`. Integrates LED/LCD/front-panel drivers and userspace custom character map tooling.

Risks and test signals: risks include endian conversion mistakes, accepting non-ASCII indexes, table size mismatch in sysfs writes, reserved-bit leakage, and visually ambiguous glyph mappings. Test `map_to_seg14()` bounds, known digits/letters, big/little-endian builds, sysfs map replacement size checks, and rendered display output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/map_to_14segment.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/map_to_7segment.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/map_to_7segment.h

Purpose: provides helpers and predefined ASCII conversion tables for 7-segment display drivers.

Important APIs and types: `BIT_SEG7_*` defines segment bit positions, `struct seg7_conversion_map` stores 128 byte entries, and `map_to_seg7()` maps an ASCII index to a segment mask or returns `-EINVAL` for out-of-range input. Macros include `SEG7_CONVERSION_MAP`, `SEG7_DEFAULT_MAP`, `MAP_TO_SEG7_SYSFS_FILE`, `_SEG7`, `MAP_ASCII7SEG_ALPHANUM`, and `MAP_ASCII7SEG_ALPHANUM_LC`.

Control flow: drivers instantiate a default or custom map, expose `map_seg7` when custom mapping is needed, and convert each character before programming display hardware.

State and persistence: conversion maps are in-memory driver state. Sysfs replacement changes runtime behavior only.

Dependencies and integration points: depends on `linux/errno.h`; integrates simple display drivers, front-panel devices, and sysfs-based map customization.

Risks and test signals: risks include off-by-one ASCII bounds, table initializer length drift, ambiguous upper/lower-case mapping, and sysfs writes with wrong size. Test bounds, digit/hex display, lowercase-map selection, sysfs round trip, and rendered segment masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/map_to_7segment.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/matroxfb.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/matroxfb.h

Purpose: defines Matrox framebuffer userspace controls for output mode and output-to-framebuffer connection management.

Important APIs and types: `struct matroxioc_output_mode` carries an output selector and mode selector. Output IDs include primary, secondary, and DFP; modes include PAL, NTSC, and monitor. Ioctls include `MATROXFB_SET_OUTPUT_MODE`, `MATROXFB_GET_OUTPUT_MODE`, `MATROXFB_SET_OUTPUT_CONNECTION`, `MATROXFB_GET_OUTPUT_CONNECTION`, `MATROXFB_GET_AVAILABLE_OUTPUTS`, and `MATROXFB_GET_ALL_OUTPUTS`. Connection bitmasks map each output to a bit. `enum matroxfb_ctrl_id` reserves V4L2 private controls for test output and deflicker.

Control flow: userspace queries available/all outputs, reads or sets output connections, and configures TV/monitor output modes for Matrox framebuffer devices.

State and persistence: state is per framebuffer/device: output routing and mode settings. Persistence depends on driver/hardware/userspace reconfiguration, not this header.

Dependencies and integration points: depends on `asm/ioctl.h`, `linux/types.h`, `linux/videodev2.h`, and `linux/fb.h`; integrates fbdev, V4L2 controls, and Matrox-specific output hardware.

Risks and test signals: risks include ioctl argument type using `size_t`, 32/64-bit compatibility, obsolete fbdev/V4L2 private-control assumptions, and invalid output bitmasks. Test ioctl compat, mode set/get round trip, unavailable outputs, DFP/TV routing, and legacy userspace tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/matroxfb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/max2175.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/max2175.h

Purpose: defines V4L2 user controls for the Maxim MAX2175 RF-to-bits tuner driver.

Important APIs and types: control IDs are `V4L2_CID_MAX2175_I2S_ENABLE`, `V4L2_CID_MAX2175_HSLS`, and `V4L2_CID_MAX2175_RX_MODE`, all allocated from `V4L2_CID_USER_MAX217X_BASE`.

Control flow: userspace configures the tuner through V4L2 controls, enabling I2S output, selecting HSLS behavior, and choosing RX mode. The driver maps control values to hardware register programming.

State and persistence: control values are runtime V4L2 subdevice/device state and may be restored by userspace after open or pipeline setup. No persistent storage is defined.

Dependencies and integration points: depends on `linux/v4l2-controls.h`; integrates V4L2 control handlers, tuner subdevices, media pipelines, and MAX217x-family userspace configuration.

Risks and test signals: risks include control ID collisions, unsupported control values, and userspace relying on driver-specific semantics not visible in this small header. Test V4L2 query/control set/get, invalid values, streaming after control changes, and media-controller pipeline integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/max2175.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/mctp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/mctp.h

Purpose: defines the Management Component Transport Protocol socket ABI, address types, tag flags, socket options, and tag allocation ioctls.

Important APIs and types: `mctp_eid_t`, `struct mctp_addr`, `struct sockaddr_mctp`, `struct sockaddr_mctp_ext`, and `struct mctp_fq_addr` encode endpoint IDs, network IDs, message type, tags, ifindex, and link-layer addresses. Constants include `MCTP_NET_ANY`, `MCTP_ADDR_NULL`, `MCTP_ADDR_ANY`, `MCTP_TAG_MASK`, `MCTP_TAG_OWNER`, `MCTP_TAG_PREALLOC`, and `MCTP_OPT_ADDR_EXT`. Ioctls include deprecated tag controls and network-aware `SIOCMCTPALLOCTAG2`/`SIOCMCTPDROPTAG2` using `struct mctp_ioc_tag_ctl2`.

Control flow: userspace creates AF_MCTP sockets, binds/connects/sends with MCTP sockaddr data, may request extended addressing, allocates preallocated tags for request/response flows, then drops tags when done.

State and persistence: runtime state includes socket bindings, route/network configuration, allocated tags, and link-layer neighbor state. No persistent state is defined by this header.

Dependencies and integration points: depends on `linux/types.h`, `linux/socket.h`, and `linux/netdevice.h`; integrates MCTP core networking, netdevice addressing, platform management protocols, and userspace management daemons.

Risks and test signals: risks include deprecated tag ioctl use on multi-network systems, tag owner/prealloc bit handling, local EID restrictions, extended sockaddr size, and ifindex/hardware-address validation. Test bind/send/recv, tag alloc/drop v1/v2, multi-network routing, extended address option, invalid tags, and concurrent tag allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/mctp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/mdio.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/mdio.h

Purpose: defines Clause 45 MDIO manageable-device IDs, register numbers, bit masks, Ethernet PHY ability/status constants, EEE constants, BASE-T1/USXGMII support bits, and a helper for encoding Clause 45 PHY IDs in ioctl data.

Important APIs and types: constants cover MMDs such as PMA/PMD, WIS, PCS, PHYXS, AN, C22 extension, and vendor devices; generic registers like `MDIO_CTRL1`, `MDIO_STAT1`, `MDIO_DEVS*`, EEE registers, AN registers, 10GBASE-T, BASE-T1, LASI, and USXGMII fields. Bit masks describe speeds, loopback, low power, reset, autonegotiation, device presence, media types, link faults, FEC, EEE, pause, master/slave, polarity, transmit disable, and link state. `mdio_phy_id_c45()` encodes PRTAD/DEVAD using `MDIO_PHY_ID_C45`, `MDIO_PHY_ID_PRTAD`, and `MDIO_PHY_ID_DEVAD`.

Control flow: PHY drivers, ethtool paths, and ioctl users read/write MDIO registers using these addresses and masks, decode advertised/link-partner capabilities, configure speed/EEE/autoneg/FEC/low-power behavior, and map Clause 45 addresses through legacy MII ioctl structures.

State and persistence: hardware PHY registers hold link/autoneg/power state; kernel PHY state machines cache and act on it. This header defines constants only.

Dependencies and integration points: depends on `linux/types.h` and `linux/mii.h`; integrates phylib, ethtool, netdevice drivers, SFP/PHY modules, copper/fiber Ethernet standards, BASE-T1 automotive PHYs, and user ioctl tools.

Risks and test signals: risks include overlapping PMA/PCS speed encodings, deprecated aliases, GENMASK/BIT macro availability, Clause 45 address packing errors, and wrong interpretation of hardware-specific register pages. Test phylib compile/use, ethtool advertise/link-mode conversion, C45 ioctl encoding, EEE negotiation, BASE-T1 autoneg, USXGMII in-band status, and register decode against known PHYs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/mdio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/media-bus-format.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/media-bus-format.h

Purpose: enumerates stable media bus format codes used to describe pixel or metadata formats transferred across media subdevice links.

Important APIs and types: `MEDIA_BUS_FMT_FIXED` and many `MEDIA_BUS_FMT_*` constants cover RGB, YUV/greyscale, Bayer raw formats from 8 to 20 bits, JPEG, vendor-specific interleaved formats, HSV, fixed metadata, and generic line-based metadata widths. Values are explicitly assigned and grouped by format family; comments track the next free value per category.

Control flow: subdevice drivers advertise and negotiate these codes through V4L2/media-subdevice pad format APIs. Pipeline setup chooses compatible bus codes between sensors, bridges, ISPs, and capture devices.

State and persistence: active bus formats are runtime media pipeline state. The header only defines stable numeric identifiers.

Dependencies and integration points: standalone UAPI header integrated with V4L2 subdev format negotiation, media controller pipelines, camera sensors, display bridges, CSI/parallel/LVDS buses, ISPs, and metadata capture.

Risks and test signals: risks include renumbering existing codes, adding values in the wrong range, ambiguous sample order names, and driver disagreement about padding/endian semantics. Test media-ctl/v4l2-ctl format enumeration, sensor-to-bridge negotiation, raw Bayer capture for each bit depth, metadata formats, and userspace header compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/media-bus-format.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/media.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/media.h

Purpose: defines the Linux Media Controller userspace ABI for device information, entity/pad/link enumeration, link setup, topology dumps, request allocation, and request queue/reinit operations.

Important APIs and types: `struct media_device_info`, entity function constants `MEDIA_ENT_F_*`, entity flags, `struct media_entity_desc`, pad/link flags, `struct media_pad_desc`, `struct media_link_desc`, `struct media_links_enum`, interface type constants, v2 packed topology structs (`media_v2_entity`, `media_v2_interface`, `media_v2_pad`, `media_v2_link`, `media_v2_topology`), and ioctls `MEDIA_IOC_DEVICE_INFO`, `MEDIA_IOC_ENUM_ENTITIES`, `MEDIA_IOC_ENUM_LINKS`, `MEDIA_IOC_SETUP_LINK`, `MEDIA_IOC_G_TOPOLOGY`, and `MEDIA_IOC_REQUEST_ALLOC`. Request fds support `MEDIA_REQUEST_IOC_QUEUE` and `MEDIA_REQUEST_IOC_REINIT`.

Control flow: userspace queries media device info, enumerates entities/pads/links or requests a full v2 topology, enables/disables mutable links, allocates request fds for atomic per-frame controls/buffers, queues requests, and reinitializes them for reuse.

State and persistence: runtime media graph state includes registered entities, interfaces, pads, links, link flags, topology version, and request objects. No persistent state is stored here. Legacy symbols remain to avoid userspace build breakage and should not drive new topology logic.

Dependencies and integration points: depends on `linux/ioctl.h` and `linux/types.h`; integrates V4L2, DVB, ALSA-adjacent media graphs, camera pipelines, ISPs, encoders/decoders, connectors, devnodes, media-ctl, libcamera, and request API users.

Risks and test signals: risks include packed v2 layout changes, pointer-sized userspace fields, topology version races, legacy entity type confusion, link flag misuse, and request lifecycle bugs. Test topology enumeration with changing graphs, link setup validation, media request allocate/queue/reinit, 32-bit userspace compatibility, and legacy ioctl behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/media.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/media/amlogic/c3-isp-config.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/media/amlogic/c3-isp-config.h

Purpose: defines the Amlogic C3 ISP userspace ABI for 3A statistics buffers and V4L2 ISP parameter blocks.

Important APIs and types: max-zone constants define AE/AF/AWB grid sizes and coordinate counts. Statistics structs include AWB ratio zones, AE 5-bin zone histograms plus 1024-bin global histogram, AF contrast metrics with mantissa/exponent bitfields, and aggregate `struct c3_isp_stats_info`. Parameter ABI includes version `C3_ISP_PARAMS_BUFFER_V0`, block types for AWB gains/config, AE config, AF config, post gamma, CCM, CSC, and BLC, block-header alias `c3_isp_params_block_header`, per-block enable/disable flags, parameter structs with explicit alignment, `C3_ISP_PARAMS_MAX_SIZE`, and `struct c3_isp_params_cfg`.

Control flow: userspace receives metadata buffers containing AWB/AE/AF stats, computes updated ISP tuning, then submits a `c3_isp_params_cfg` buffer containing one or more typed parameter blocks. Each block header tells the driver how to parse and enable/disable a block.

State and persistence: stats buffers are per-frame capture output. Parameter buffers configure runtime ISP hardware state such as gains, metering grids, gamma LUT, color matrices, and black-level offsets. Settings are not persistent unless userspace reapplies them.

Dependencies and integration points: depends on `linux/types.h`, `linux/media/v4l2-isp.h`, and kernel-only build assertions. Integrates V4L2 metadata formats, ISP params buffers, Amlogic C3 camera pipeline, 3A algorithms, and userspace camera stacks.

Risks and test signals: risks include struct alignment/packing drift, bitfield portability, mismatched `v4l2_isp_params_block_header`, incorrect max-size calculation, nonzero reserved fields, zone coordinate bounds, fixed-point scale mistakes, and block ordering/size parsing bugs. Test compile-time size assertions, metadata buffer size, all block types individually and combined, reserved zero validation, max zone counts, malformed headers, and frame-to-frame parameter application.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/media/amlogic/c3-isp-config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/media/arm/mali-c55-config.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/media/arm/mali-c55-config.h

Purpose: defines the ARM Mali-C55 ISP userspace ABI for capability controls, 3A statistics buffers, and V4L2 ISP parameter blocks controlling exposure histograms, AWB, digital gain, sensor offsets, and mesh shading.

Important APIs and types: `V4L2_CID_MALI_C55_CAPABILITIES` and `MALI_C55_GPS_*` flags advertise hardware pipeline capabilities. Statistics structs include 1024-bin AE histograms, 5-bin AE zone histograms, AWB average ratios, AF statistics, and aggregate `struct mali_c55_stats_buffer`. `enum mali_c55_param_block_type` selects typed blocks. Parameter structs include sensor black-level offsets, AEXP histogram config, AEXP weights, digital gain, AWB gains/config, mesh shading table config, mesh alpha bank selection, and mesh selection. `MALI_C55_PARAMS_MAX_SIZE` sums the maximum multi-block parameter buffer footprint.

Control flow: userspace queries capabilities, consumes per-frame stats metadata, computes 3A/lens-shading decisions, and submits a buffer of typed `v4l2_isp_params_block_header` blocks. Histogram configuration controls tap points, skip/offset patterns, intensity scaling, plane modes, and zone weights. AWB config gates pixel inclusion by intensity and ratio windows. Mesh shading config uploads coefficient pages and selection blends light-source tables.

State and persistence: stats buffers are frame outputs. Parameter blocks update runtime ISP state: offsets, histograms, digital gain, AWB gains/windows, and mesh tables. Mesh tables can be large runtime state but are not persistent beyond driver/device lifetime unless userspace reloads them.

Dependencies and integration points: depends on `linux/types.h`, `linux/v4l2-controls.h`, and `linux/media/v4l2-isp.h`. Integrates Mali-C55 V4L2 drivers, media request pipelines, libcamera-style 3A, sensor Bayer order handling, WDR/Iridix paths, and ISP metadata capture.

Risks and test signals: risks include packed-stat layout drift, exponent/mantissa decode errors, invalid skip/offset combinations losing color planes, zone bounds, mesh table size and page selection errors, Q-format scaling mistakes, capability mismatch, repeated struct accounting in max-size, and malformed block headers. Test stats buffer ABI size/content, all parameter block types, histogram plane modes, zone weights, AWB ratio windows, mesh upload/select/blend, invalid enum values, max parameter buffer parsing, and request-synchronized frame application.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/media/arm/mali-c55-config.h -->
