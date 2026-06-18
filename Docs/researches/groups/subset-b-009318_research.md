# subset-b-009318 research

Grouped research report for bundled Linux UAPI headers used by the strace test tooling. Each section preserves the exact source path and is wrapped for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/input.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/input.h

Purpose: defines the Linux evdev userspace ABI consumed through `/dev/input/event*`, including event records, device identity, absolute axis metadata, keymap access, per-client event masks, and force-feedback effect payloads.

Important APIs/types/functions: `struct input_event`, `input_id`, `input_absinfo`, `input_keymap_entry`, `input_mask`, the `EVIOC*` ioctl macros, bus ID constants, multitouch tool constants, and the `ff_*` structures gathered by `struct ff_effect`. There are no functions; behavior is encoded as ioctl numbers and binary layout.

Control flow: user space reads streams of `input_event` records, then calls query/update ioctls for capabilities, absolute axes, keymaps, masks, grabs, clock selection, revoke, and force-feedback upload/removal. Time fields switch layout on 32-bit time64 builds.

State/persistence behavior: most queries are read-only device state. `EVIOCS*`, `EVIOCGRAB`, event masks, clock id, and force-feedback uploads mutate fd-local or device-driver state; event masks are explicitly per-client and force-feedback effect IDs persist until removed or the device/fd lifecycle ends.

Dependencies/integration: depends on `sys/time.h`, `sys/ioctl.h`, Linux integer types, and `input-event-codes.h`. strace should decode ioctl directions, variable-length bitmap/string ioctls, pointer-bearing `input_mask`, and union payloads in `ff_effect`.

Risks and test signals: ABI risk is high around time layout, packed fields, variable ioctl lengths, and userspace pointers such as `custom_data`. Tests should exercise EVIOCG/EVIOCS ioctl decoding, 32-bit compat layouts, force-feedback type unions, and masked event filtering semantics.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/input.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/io_uring.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/io_uring.h

Purpose: declares the core `io_uring` userspace ABI for setup, mmap ring offsets, SQE/CQE layouts, submission opcodes, completion flags, enter/register flags, probe data, registered resources, provided buffers, NAPI, socket uring commands, and newer zcrx/query integration.

Important APIs/types/functions: central types are `io_uring_sqe`, `io_uring_cqe`, `io_uring_params`, `io_sqring_offsets`, `io_cqring_offsets`, `io_uring_register_op`, `io_uring_op`, resource registration/update structures, restriction structures, provided-buffer ring types, `io_uring_getevents_arg`, and `io_uring_sync_cancel_reg`.

Control flow: applications call `io_uring_setup`, mmap SQ/CQ/SQE regions using the exported offsets, fill SQEs using opcode-specific union fields, submit/wait with `io_uring_enter`, and configure shared kernel state with `io_uring_register`. CQEs return `res`, `user_data`, and flags for buffers, multishot, notification, skip, and large-CQE modes.

State/persistence behavior: rings persist as kernel objects behind fds or registered ring indexes. Registered files, buffers, personalities, provided-buffer groups, NAPI settings, clocks, zcrx interfaces, and memory regions survive across submissions until unregistered or fd close.

Dependencies/integration: includes `linux/fs.h`, `linux/types.h`, optional `linux/time_types.h`, and `linux/io_uring/zcrx.h`. strace integration must decode three syscalls plus many register op argument structs and SQE opcode fields.

Risks and test signals: dense unions make field interpretation opcode-dependent. Tests should cover setup feature flags, mixed SQE/CQE sizing, fixed fd allocation, registered-ring flags, probe output, buffer rings, zcrx registration, and endian-sensitive poll fields.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/io_uring.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/io_uring/query.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/io_uring/query.h

Purpose: defines the `IORING_REGISTER_QUERY` payload ABI for discovering supported io_uring capabilities, including opcode coverage, zcrx support, and shared CQ/SQ ring geometry.

Important APIs/types/functions: `struct io_uring_query_hdr` is the common entry header with `next_entry`, `query_data`, `query_op`, `size`, and `result`. Query payloads include `io_uring_query_opcode`, `io_uring_query_zcrx`, and `io_uring_query_scq`.

Control flow: userspace chains or points query headers at payload buffers, selects `IO_URING_QUERY_OPCODES`, `IO_URING_QUERY_ZCRX`, or `IO_URING_QUERY_SCQ`, and submits via the register API. The kernel fills capability bitmasks, counts, alignment, size, and result status.

State/persistence behavior: queries are observational and should not mutate ring state. Results reflect kernel and possibly ring-supported capability state at call time.

Dependencies/integration: depends only on `linux/types.h` but is referenced from `io_uring.h` register op comments. strace should decode this as a register subcommand with nested payload selected by `query_op`.

Risks and test signals: the header is versioned through size/reserved fields and uses pointer-like `__u64` fields. Tests should verify chained query decoding, unsupported query result handling, and zcrx/scq alignment fields.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/io_uring/query.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/io_uring/zcrx.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/io_uring/zcrx.h

Purpose: declares the io_uring zero-copy receive ABI for registering receive queues, memory areas, refill queue offsets, and auxiliary control operations.

Important APIs/types/functions: important layouts include `io_uring_zcrx_rqe`, `io_uring_zcrx_cqe`, `io_uring_zcrx_offsets`, `io_uring_zcrx_area_reg`, `io_uring_zcrx_ifq_reg`, and `zcrx_ctrl`. Flags include `IORING_ZCRX_AREA_DMABUF`, `ZCRX_REG_IMPORT`, `ZCRX_REG_NODEV`, and `ZCRX_FEATURE_RX_PAGE_SIZE`.

Control flow: user space registers an interface queue with `IORING_REGISTER_ZCRX_IFQ`, supplies or imports backing area metadata, obtains ring offsets and a `zcrx_id`, refills buffers through RQEs, and uses `IORING_REGISTER_ZCRX_CTRL` for flush or export operations.

State/persistence behavior: registration creates persistent zcrx state tied to the ring and possibly a netdev RX queue or dmabuf. Export can create a separate fd; flush affects queued refill state.

Dependencies/integration: depends on Linux integer types and is included by `io_uring.h`. It also integrates with netdev queue/page-pool concepts via queue indexes and dmabuf registration.

Risks and test signals: ABI is new and pointer-heavy; offsets encode area IDs in high bits. Tests should cover area mask formatting, nodev/import flags, dmabuf fd handling, exported fd output, and reserved-field validation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/io_uring/zcrx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/ioam6_genl.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/ioam6_genl.h

Purpose: defines the IPv6 IOAM generic netlink family ABI for namespace and schema management plus trace event reporting.

Important APIs/types/functions: exports `IOAM6_GENL_NAME`, version, command enum values for adding/deleting/dumping namespaces and schemas, namespace-to-schema binding, command attributes such as namespace ID/data and schema ID/data, and event attributes for IOAM trace notifications.

Control flow: userspace sends generic netlink commands to create namespaces, attach schema data up to `IOAM6_MAX_SCHEMA_DATA_LEN`, list configured objects, and receive multicast trace events from `IOAM6_GENL_EV_GRP_NAME`.

State/persistence behavior: namespace and schema commands mutate kernel IOAM configuration. Event messages are transient observations of traced packets and do not persist.

Dependencies/integration: no included dependencies beyond enum constants; semantically integrates with generic netlink, IPv6 IOAM encapsulation, and route/tunnel configuration using IOAM state.

Risks and test signals: schema data is variable binary data with a documented maximum. Tests should validate generic netlink family/command names, nested binary attribute formatting, namespace/schema lifecycle commands, and event-group trace decoding.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/ioam6_genl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/ip_vs.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/ip_vs.h

Purpose: exposes IP Virtual Server userspace ABI for configuring virtual services, real destinations, sync daemons, timeouts, and statistics through legacy socket options and generic netlink.

Important APIs/types/functions: legacy structures include `ip_vs_service_user`, `ip_vs_dest_user`, `ip_vs_stats_user`, `ip_vs_getinfo`, `ip_vs_service_entry`, `ip_vs_dest_entry`, `ip_vs_get_dests`, `ip_vs_get_services`, `ip_vs_timeout_user`, and `ip_vs_daemon_user`. Netlink enums define `IPVS_CMD_*`, service/destination/daemon/stat/info attributes, and `ip_vs_flags`.

Control flow: tools create/edit/delete services and destinations, read lists and stats, start/stop sync daemons, set timeouts, flush state, and zero counters. Legacy setsockopt/getsockopt numbers coexist with the generic netlink family `IPVS`.

State/persistence behavior: configuration changes persistent kernel load-balancer state; stats and counters change with traffic and may be reset. Sync daemon state persists until stopped or namespace teardown.

Dependencies/integration: depends on Linux fixed-width and big-endian types. Integrates with netfilter/conntrack, scheduler modules, tunnel encapsulation, multicast sync, and userspace tools such as `ipvsadm`.

Risks and test signals: several structs contain flexible arrays or fixed-size names. Tests should cover socket option decoding, nested generic netlink service/dest attributes, stats64 variants, tunnel flags, fwmark-vs-address service selection, and counter reset commands.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/ip_vs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/kcmp.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/kcmp.h

Purpose: defines constants and one helper struct for the `kcmp(2)` process-resource comparison syscall.

Important APIs/types/functions: `enum kcmp_type` selects comparison domains such as files, VM, file table, fs context, signal handlers, IO context, SysV semaphores, and epoll target-fd lookup. `struct kcmp_epoll_slot` carries epoll fd, target fd, and target offset for `KCMP_EPOLL_TFD`.

Control flow: userspace calls `kcmp(pid1, pid2, type, idx1, idx2)`. For epoll comparisons, one index points to a `kcmp_epoll_slot` describing the watched target.

State/persistence behavior: syscall is observational and does not mutate compared tasks. Results depend on live process resource sharing and can race with concurrent process activity.

Dependencies/integration: depends on `linux/types.h`; integrates with proc inspection, checkpoint/restore tooling, and strace syscall argument decoding.

Risks and test signals: pid lifetime races and pointer interpretation for epoll slots are key risks. Tests should decode every `KCMP_*` type and validate `kcmp_epoll_slot` printing for `KCMP_EPOLL_TFD`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/kcmp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/kexec.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/kexec.h

Purpose: defines userspace constants and segment layout for `kexec_load` and `kexec_file_load`, which load a replacement kernel or crash kernel.

Important APIs/types/functions: flags include `KEXEC_ON_CRASH`, `KEXEC_PRESERVE_CONTEXT`, `KEXEC_UPDATE_ELFCOREHDR`, `KEXEC_CRASH_HOTPLUG_SUPPORT`, file-load flags such as `KEXEC_FILE_UNLOAD`, `KEXEC_FILE_ON_CRASH`, `KEXEC_FILE_NO_INITRAMFS`, `KEXEC_FILE_NO_CMA`, `KEXEC_FILE_FORCE_DTB`, architecture encodings, `KEXEC_SEGMENT_MAX`, and `struct kexec_segment`.

Control flow: userspace passes an array of up to 16 segments for classic load, or kernel/initrd fds and flags for file load. Reboot into the loaded image occurs through a separate reboot path, not this header.

State/persistence behavior: load operations install or unload kernel crash/next-boot image state in the running kernel. The header warns that filesystem sync/unmount is not performed by kexec itself.

Dependencies/integration: depends on Linux types and architecture ELF numbering. Integrates with crash dump tooling, boot loaders, secure boot policy, and memory hotplug support.

Risks and test signals: risks include architecture mask decoding, pointer-size differences in `kexec_segment`, and privileged destructive semantics. Tests should decode flags, architecture values, segment arrays, unload mode, and no-initramfs/file-debug flags.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/kexec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/keyctl.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/keyctl.h

Purpose: declares command IDs, special keyring IDs, default request-key destinations, cryptographic parameter structures, move/capability flags, and notification capability bits for the `keyctl(2)` syscall.

Important APIs/types/functions: constants cover `KEY_SPEC_*`, `KEY_REQKEY_DEFL_*`, `KEYCTL_*` commands through watch support, `keyctl_dh_params`, `keyctl_kdf_params`, `keyctl_pkey_query`, `keyctl_pkey_params`, `KEYCTL_MOVE_EXCL`, and `KEYCTL_CAPS*` feature bits.

Control flow: userspace calls `keyctl` with a command selector and command-specific scalar or pointer arguments. Commands manage keyrings, update/revoke/link/search/read keys, instantiate request-key results, compute DH/KDF/public-key operations, restrict/move keys, query capabilities, or watch keys.

State/persistence behavior: many commands mutate persistent keyring/key objects scoped to thread, process, session, UID, group, namespace, or requestor contexts. Capabilities and describe/read queries are observational.

Dependencies/integration: depends on Linux integer types and integrates with kernel key retention service, request-key upcalls, LSM labels, watch queues, and crypto providers.

Risks and test signals: command-specific argument layouts are easy to misdecode. Tests should cover negative special IDs, C++ `private` field compatibility, public-key query structs, capability byte arrays, key movement, and watch-key command decoding.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/keyctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/landlock.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/landlock.h

Purpose: defines the Landlock sandboxing syscall ABI for creating rulesets, adding path/network rules, and restricting the current process or thread group.

Important APIs/types/functions: key types are `landlock_ruleset_attr`, `landlock_path_beneath_attr`, `landlock_net_port_attr`, `enum landlock_rule_type`, create/restrict flags, filesystem access bits, network access bits, and scope bits for abstract UNIX sockets and signals.

Control flow: applications query ABI/errata with `landlock_create_ruleset`, create a ruleset with handled access masks, add `PATH_BENEATH` and `NET_PORT` rules, then call `landlock_restrict_self` optionally with logging or thread-sync flags. Later filesystem, TCP, UNIX socket, signal, and ioctl decisions are mediated by the enacted domain.

State/persistence behavior: ruleset fds persist until closed; enacted Landlock domains are process/thread security state and are restrictive, stackable, and inherited across fork/exec according to kernel semantics. Logging flags affect audit behavior.

Dependencies/integration: depends on `linux/types.h` and integrates with LSM hooks, audit, `no_new_privs`, mount/path resolution, TCP sockets, and UNIX IPC.

Risks and test signals: versioned ABI and default-denied `REFER` semantics are subtle. Tests should cover ABI version queries, packed path rules, TCP port 0 behavior, scoped IPC flags, logging flags, TSYNC, and unknown access-bit compatibility.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/landlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/libc-compat.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/libc-compat.h

Purpose: coordinates Linux UAPI headers with libc headers to avoid duplicate struct, macro, and enum definitions while preserving ABI-compatible layouts.

Important APIs/types/functions: the exported surface is a set of `__UAPI_DEF_*` guard macros for net interface, IPv4/IPv6 socket structures/options, and xattr definitions. The logic branches on glibc markers such as `__GLIBC__`, `_NET_IF_H`, `_NETINET_IN_H`, `_SYS_XATTR_H`, and feature macros.

Control flow: UAPI headers include this early, then wrap conflicting definitions in `#if __UAPI_DEF_FOO`. If libc headers were included first, the UAPI header suppresses duplicates; if Linux headers come first, the guards tell libc to suppress duplicates later.

State/persistence behavior: compile-time only; no runtime state. The "state" is preprocessor include order and feature macro visibility in the translation unit.

Dependencies/integration: integrates with glibc and other libc implementations that may predefine `__UAPI_DEF_*`. It is foundational for headers such as networking ABI files included alongside libc headers.

Risks and test signals: risks are include-order regressions and unsupported libc behavior. Tests should compile small C snippets with libc-first and Linux-first include ordering for `net/if.h`, `netinet/in.h`, and `sys/xattr.h`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/libc-compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/lirc.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/lirc.h

Purpose: defines the Linux infrared remote control ABI for raw/mode2/scancode data, device feature flags, and LIRC ioctl configuration.

Important APIs/types/functions: macros encode/decode `LIRC_MODE2_*` packets, capability bits describe send/receive features, ioctls include `LIRC_GET_FEATURES`, mode getters/setters, carrier/duty/timeout controls, and wideband settings. `struct lirc_scancode` and `enum rc_proto` define decoded scancode records.

Control flow: userspace queries features, selects send/receive modes, configures carrier/timing behavior, reads pulse/space/frequency/timeout/overflow mode2 values or scancode records, and transmits protocol-specific data where supported.

State/persistence behavior: mode and carrier ioctls mutate per-device driver configuration. Timeout reporting and carrier measurement change future event stream contents. Scancode records are transient input data.

Dependencies/integration: depends on Linux types and ioctl macros. Integrates with rc-core protocols, media input devices, and lirc userspace daemons.

Risks and test signals: the upper byte of mode2 values carries packet type, so formatting must mask correctly. Tests should exercise capability flag groups, ioctl numbers, timeout-report toggles, scancode flags, and every `RC_PROTO_*` value.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/lirc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/loop.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/loop.h

Purpose: declares the loop block device ioctl ABI for attaching backing files, configuring flags, querying status, resizing capacity, direct I/O, block size, and loop-control device operations.

Important APIs/types/functions: `loop_info` is the legacy status layout; `loop_info64` is the modern layout; `loop_config` atomically combines backing fd, block size, and status. Constants include `LO_FLAGS_*`, settable/clearable masks, obsolete crypto IDs, `LOOP_*` ioctls, and `/dev/loop-control` ioctls.

Control flow: userspace finds or creates a loop device, calls `LOOP_SET_FD` or `LOOP_CONFIGURE`, adjusts status or capacity, optionally changes backing fd, and detaches with `LOOP_CLR_FD`.

State/persistence behavior: ioctls mutate kernel block-device state and backing-file association. `AUTOCLEAR` delays cleanup until last close; read-only, partition scan, and direct-IO flags affect later block operations.

Dependencies/integration: depends on asm posix types and Linux integer types. Integrates with block layer, partition scanning, mount tooling, and `/dev/loop-control`.

Risks and test signals: legacy 32-bit fields, obsolete encryption members, and ioctl numbers without `_IO*` encoding matter for tracing. Tests should decode `loop_info64`, `loop_config`, flag masks, control ioctls, and autoclear lifecycle.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/loop.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/lsm.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/lsm.h

Purpose: defines the generic Linux Security Module userspace context ABI used by LSM-related syscalls and interfaces.

Important APIs/types/functions: `struct lsm_ctx` carries an LSM ID, LSM-specific flags, total record length, context length, and flexible `ctx` bytes. Constants identify LSMs (`LSM_ID_SELINUX`, `LSM_ID_APPARMOR`, `LSM_ID_LANDLOCK`, and others), context attributes (`LSM_ATTR_CURRENT`, `EXEC`, `FSCREATE`, `KEYCREATE`, `PREV`, `SOCKCREATE`), and `LSM_FLAG_SINGLE`.

Control flow: callers request or set security contexts by attribute and receive one or more length-delimited `lsm_ctx` records. Consumers advance through buffers using the `len` field.

State/persistence behavior: context reads are observational; context-setting APIs can mutate process security state for supported LSM attributes. Records may contain strings or binary data and must preserve NUL termination rules when string-based.

Dependencies/integration: includes `linux/stddef.h`, `linux/types.h`, and `linux/unistd.h`. Integrates with SELinux, Smack, AppArmor, Landlock, IMA/EVM, and other LSMs.

Risks and test signals: flexible arrays and counted-by metadata require robust length validation. Tests should cover multi-record buffers, unknown LSM IDs, `LSM_FLAG_SINGLE`, binary contexts, and string context length including NUL.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/lsm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/mctp.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/mctp.h

Purpose: defines the Management Component Transport Protocol socket ABI, address structures, tag flags, extended address option, and tag allocation ioctls.

Important APIs/types/functions: exports `mctp_eid_t`, `mctp_addr`, `sockaddr_mctp`, `sockaddr_mctp_ext`, `mctp_fq_addr`, network/address constants, tag flags (`MCTP_TAG_OWNER`, `MCTP_TAG_PREALLOC`), `MCTP_OPT_ADDR_EXT`, `SIOCMCTP*TAG*` ioctls, and `mctp_ioc_tag_ctl`/`mctp_ioc_tag_ctl2`.

Control flow: userspace binds/connects/sends with MCTP sockaddr forms, optionally requests extended hardware address data, allocates preallocated tags for a peer, sends traffic, then drops tags.

State/persistence behavior: allocated tags are kernel state associated with socket/peer/network until explicitly dropped or socket cleanup. Addressing is scoped by local MCTP network IDs and EIDs.

Dependencies/integration: depends on Linux socket and netdevice definitions, especially `MAX_ADDR_LEN`. Integrates with AF_MCTP sockets, network-device binding, and platform management controllers.

Risks and test signals: deprecated TAG ioctls lack network ID and can be wrong on multi-network systems. Tests should cover sockaddr decoding, extended address option, tag flags, TAG2 structs, and `MCTP_ADDR_ANY`/`NULL`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/mctp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/memfd.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/memfd.h

Purpose: declares flags for `memfd_create(2)`, including close-on-exec, sealing, hugetlb-backed files, executable/no-exec policy, and hugepage size encodings.

Important APIs/types/functions: exports `MFD_CLOEXEC`, `MFD_ALLOW_SEALING`, `MFD_HUGETLB`, `MFD_NOEXEC_SEAL`, `MFD_EXEC`, `MFD_HUGE_SHIFT`, `MFD_HUGE_MASK`, and named hugepage encodings from 64 KiB through 16 GiB.

Control flow: userspace calls `memfd_create(name, flags)`, optionally ORing hugepage size encodings when `MFD_HUGETLB` is set. The returned anonymous file descriptor can later be sealed, mapped, executed, or shared according to flags and kernel policy.

State/persistence behavior: creates an in-kernel anonymous file object whose lifetime follows fd references. Sealing and executable mode affect later writes, mappings, and exec behavior.

Dependencies/integration: depends on `asm-generic/hugetlb_encode.h`. Integrates with `fcntl` seals, `mmap`, tmpfs/hugetlbfs, exec policy, and sandboxing.

Risks and test signals: flag interactions depend on kernel config and sysctls. Tests should decode hugepage encodings, mutually meaningful exec/noexec flags, sealing flag behavior, and unsupported hugepage-size error paths.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/memfd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/mmtimer.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/mmtimer.h

Purpose: defines the ioctl ABI for Intel/SGI multimedia timer devices, exposing timer resolution, frequency, counter width, mmap availability, offset, and current counter value.

Important APIs/types/functions: constants include `MMTIMER_IOCTL_BASE`, `MMTIMER_GETOFFSET`, `MMTIMER_GETRES`, `MMTIMER_GETFREQ`, `MMTIMER_GETBITS`, `MMTIMER_MMAPAVAIL`, and `MMTIMER_GETCOUNTER`.

Control flow: userspace opens the timer device, checks whether registers can be mmapped, reads frequency/resolution/bits, and either mmaps registers or calls `MMTIMER_GETCOUNTER` to read current timer value.

State/persistence behavior: all exported ioctls are read-only observations of hardware/device capability and counter state. The counter itself advances independently in hardware.

Dependencies/integration: relies on Linux `_IO/_IOR` ioctl encoding and unsigned long result sizes. Integrates with legacy high-resolution timing consumers and device-driver mmap support.

Risks and test signals: optional vs required ioctls and unsigned-long size differences are the main risks. Tests should decode all commands, validate pointer result formatting, and cover mmap-available versus ioctl-only devices.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/mmtimer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/mount.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/mount.h

Purpose: defines mount-related userspace ABI constants and structures for legacy `mount(2)` flags and newer file-descriptor based mount APIs, mount attributes, `statmount(2)`, and `listmount(2)`.

Important APIs/types/functions: exports `MS_*`, `OPEN_TREE_*`, `MOVE_MOUNT_*`, `FSOPEN/FSPICK/FSMOUNT_*`, `enum fsconfig_command`, `MOUNT_ATTR_*`, `struct mount_attr`, `struct statmount`, `struct mnt_id_req`, `STATMOUNT_*`, `LSMT_ROOT`, `LISTMOUNT_REVERSE`, and `STATMOUNT_BY_FD`.

Control flow: tools open or clone mount trees, configure fs contexts with `fsconfig`, create mounts, move them, set attributes with `mount_setattr`, and query/list mount metadata using request masks.

State/persistence behavior: mount operations mutate namespace mount topology, propagation, idmapping, and superblock configuration. `statmount`/`listmount` are read-only snapshots returning versioned structs and trailing string storage.

Dependencies/integration: depends on Linux types and `O_CLOEXEC` from included build context. Integrates with VFS, namespaces, idmapped mounts, filesystem drivers, and `/proc/*/mountinfo` replacement APIs.

Risks and test signals: versioned struct sizes, string offsets, mask negotiation, and flag aliasing (`MS_VERBOSE`/`MS_SILENT`) are subtle. Tests should cover every syscall flag family, `mount_attr` bit sets/clears, `statmount` string buffers, and list iteration.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/mount.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/mpls.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/mpls.h

Purpose: declares MPLS label stack entry layout, masks/shifts for RFC label fields, reserved label values, and MPLS link statistics netlink attributes.

Important APIs/types/functions: `struct mpls_label` wraps the big-endian 32-bit label stack entry. Macros extract label, traffic class, bottom-of-stack, and TTL fields. Reserved labels include IPv4/IPv6 explicit null, implicit null, entropy, GAL, OAM alert, and extension labels. `mpls_link_stats` carries per-link counters.

Control flow: route/link tooling and netlink consumers encode/decode MPLS labels, configure routes, and read `AF_MPLS` stats nested under `IFLA_STATS_AF_SPEC`.

State/persistence behavior: the header itself is declarative; MPLS routing and per-link statistics persist in kernel network namespace state and update with packet traffic.

Dependencies/integration: depends on Linux integer types and byteorder definitions. Integrates with rtnetlink, MPLS route configuration, interface stats, and packet parsers.

Risks and test signals: endian handling and bit masking are the core risks. Tests should decode label stack values, reserved labels, bottom-of-stack/TTL/TC fields, and nested MPLS stats attributes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/mpls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/mptcp.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/mptcp.h

Purpose: defines Multipath TCP socket-level ABI for connection info, subflow information, full info queries, reset reasons, endpoint flags, and socket option numbers.

Important APIs/types/functions: key items include `MPTCP_SUBFLOW_FLAG_*`, `MPTCP_INFO_FLAG_*`, PM group names, endpoint/event flags, `struct mptcp_info`, reset reason constants, `mptcp_subflow_data`, `mptcp_subflow_addrs`, `mptcp_subflow_info`, `mptcp_full_info`, and socket options `MPTCP_INFO`, `MPTCP_TCPINFO`, `MPTCP_SUBFLOW_ADDRS`, `MPTCP_FULL_INFO`.

Control flow: applications call `getsockopt` on MPTCP sockets to retrieve aggregate connection state, TCP info arrays, subflow addresses, and combined full information. The kernel fills counts and size fields to support ABI growth.

State/persistence behavior: mostly observational; values reflect live MPTCP connection/subflow state, counters, tokens, and limits. Endpoint flags are shared with path manager netlink state.

Dependencies/integration: includes libc and Linux socket/in headers plus `mptcp_pm.h`. Integrates with TCP sockets, MPTCP path manager events, and netlink endpoint management.

Risks and test signals: variable array pointers and user/kernel size negotiation are key risks. Tests should cover all socket options, fallback/remote-key flags, reset reasons, subflow flag combinations, and IPv4/IPv6 address unions.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/mptcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/mptcp_pm.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/mptcp_pm.h

Purpose: auto-generated generic netlink UAPI for the MPTCP path manager family, covering endpoint management commands, limits, subflow operations, and event notifications.

Important APIs/types/functions: exports family name/version, `enum mptcp_event_type`, endpoint address attributes, subflow attributes, path-manager attributes, event attributes, and commands from add/delete/get/flush addresses through set flags, announce/remove, and subflow create/destroy.

Control flow: userspace sends MPTCP PM netlink commands to manage local/remote endpoint state and listens for events such as connection created/established/closed, announced/removed addresses, subflow establishment/closure/priority, and listener lifecycle.

State/persistence behavior: commands mutate path-manager state in the network namespace and can trigger MPTCP signaling or subflow lifecycle changes. Events are transient notifications carrying tokens, IDs, addresses, ports, flags, and errors.

Dependencies/integration: generated from `mptcp_pm.yaml` and included by `mptcp.h`. Integrates with generic netlink, MPTCP sockets, endpoint flags, and user path managers.

Risks and test signals: sparse event numbering and nested address attributes can break decoders. Tests should cover command names, endpoint attrs, event attrs including reset reason/server-side flags, and subflow token/sequence attributes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/mptcp_pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/mqueue.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/mqueue.h

Purpose: defines POSIX message queue ABI constants, queue attribute layout, and special netlink-cookie behavior for user-space `SIGEV_THREAD` notification emulation.

Important APIs/types/functions: exports `MQ_PRIO_MAX`, `MQ_BYTES_MAX`, `struct mq_attr`, notification codes `NOTIFY_NONE`, `NOTIFY_WOKENUP`, `NOTIFY_REMOVED`, and `NOTIFY_COOKIE_LEN`.

Control flow: `mq_open`, `mq_getsetattr`, send/receive, and notify syscalls use `mq_attr` for flags, queue depth, message size, and current message count. For `SIGEV_THREAD`, libc uses an AF_NETLINK socket and a fixed-size cookie to receive notification completion/removal messages.

State/persistence behavior: message queues persist as kernel IPC objects until unlinked/closed per POSIX rules. `mq_attr` changes can affect nonblocking behavior; notification registration is one-shot mutable queue state.

Dependencies/integration: depends on Linux integer types and integrates with POSIX mqueue syscalls, libc notification helpers, netlink sockets, and per-UID resource limits.

Risks and test signals: long-size fields vary by ABI and notification cookie semantics are unusual. Tests should decode `mq_attr` in syscalls, queue limits, and `mq_notify` `SIGEV_THREAD` netlink-cookie paths.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/mqueue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/mroute.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/mroute.h

Purpose: defines IPv4 multicast routing socket option/ioctl ABI, virtual interface and multicast forwarding cache structures, PIM control messages, and rtnetlink multicast route attributes.

Important APIs/types/functions: exports `MRT_*` commands, `SIOCGETVIFCNT`, `SIOCGETSGCNT`, `SIOCGETRPF`, flush flags, `vifbitmap_t`, `vifi_t`, VIF bitmap macros, `vifctl`, `mfcctl`, `sioc_sg_req`, `sioc_vif_req`, `igmpmsg`, `IPMRA_*` attributes, and `IGMPMSG_*` pseudo-message types.

Control flow: multicast routing daemons enable MRT, add/delete VIFs and MFC entries, receive cache-miss/register messages on raw sockets, query counters, set PIM/assert/table behavior, and flush caches/interfaces.

State/persistence behavior: commands mutate per-netns multicast routing tables, VIFs, cache entries, counters, and daemon mode until `MRT_DONE` or namespace teardown. Counter queries are observational.

Dependencies/integration: includes sockios, Linux types, and IPv4 address definitions. Integrates with IGMP/PIM daemons, rtnetlink table dumps, and raw IP sockets.

Risks and test signals: legacy BSD-compatible structs and bitmaps are ABI-sensitive. Tests should cover all `MRT_*` options, flush flags, VIF flags, flexible control messages, counter ioctls, and netlink nested VIF/cache-report attrs.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/mroute.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/mroute6.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/mroute6.h

Purpose: defines IPv6 multicast routing ABI analogous to `mroute.h`, including MIF management, forwarding cache structs, counter ioctls, MRT6 control messages, and netlink cache report attributes.

Important APIs/types/functions: exports `MRT6_*` commands, `SIOCGETMIFCNT_IN6`, `SIOCGETSGCNT_IN6`, flush flags, `mifbitmap_t`, `mifi_t`, `if_set` macros, `mif6ctl`, `mf6cctl`, `sioc_sg_req6`, `sioc_mif_req6`, `mrt6msg`, `MRT6MSG_*`, and `IP6MRA_CREPORT_*`.

Control flow: IPv6 multicast routing daemons enable MRT6, add/delete MIFs and forwarding cache entries, receive MLD/PIM control payloads, query counters, select tables, and flush entries/interfaces.

State/persistence behavior: mutates per-netns IPv6 multicast routing state, MIFs, cache entries, and counters. Query ioctls and cache reports observe live state.

Dependencies/integration: depends on Linux constants/types/sockios and IPv6 sockaddr definitions. Integrates with PIM6/MLD daemons, raw IPv6 sockets, and rtnetlink.

Risks and test signals: `if_set` bitmap sizing and IPv6 sockaddr layouts must be decoded correctly. Tests should cover MRT6 commands, MIF flags, counter structs, `mrt6msg` packet reports, and IP6MRA attributes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/mroute6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/neighbour.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/neighbour.h

Purpose: declares rtnetlink ABI for neighbor cache entries, neighbor table parameters/statistics, bridge FDB extended attributes, flags, and state constants.

Important APIs/types/functions: core types are `ndmsg`, `nda_cacheinfo`, `ndt_stats`, `ndtmsg`, and `ndt_config`. Attribute enums include `NDA_*`, `NDTPA_*`, `NDTA_*`, and `NFEA_*`. Flags cover `NTF_*`, extended flags, and `NUD_*` states.

Control flow: userspace sends RTM neighbor messages to add/delete/query ARP/NDP/FDB entries and RTM_GET/SETNEIGHTBL for table configuration. Dumps may span multiple messages with global and per-device parameter sets.

State/persistence behavior: neighbor entries and table parameters are kernel networking state with aging, probing, garbage collection, offload, external-learning, locked, managed, and permanent behaviors. Counters/statistics update with neighbor activity.

Dependencies/integration: depends on Linux netlink and type headers. Integrates with ARP, IPv6 NDP, bridge FDB, routing, switchdev/offload, and user control planes.

Risks and test signals: many flags alter aging and deletion semantics. Tests should decode `ndmsg`, cacheinfo, NUD states, extended FDB attrs, table stats/config, per-device parms, and masks for state/flags updates.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/neighbour.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/netconf.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/netconf.h

Purpose: defines rtnetlink network configuration message ABI for per-family/per-interface forwarding and neighbor-related settings.

Important APIs/types/functions: `struct netconfmsg` carries the address family. Attributes include `NETCONFA_IFINDEX`, `FORWARDING`, `RP_FILTER`, `MC_FORWARDING`, `PROXY_NEIGH`, `IGNORE_ROUTES_WITH_LINKDOWN`, `INPUT`, `BC_FORWARDING`, and `FORCE_FORWARDING`. Special indexes select all or default configuration.

Control flow: userspace sends netconf get/dump messages and receives settings for a family and interface, or all/default pseudo-interfaces.

State/persistence behavior: the header primarily supports observing kernel network configuration; changes occur through related sysctl/rtnetlink paths and persist in network namespace interface/default state.

Dependencies/integration: depends on Linux netlink and type headers. Integrates with IPv4/IPv6 sysctl-backed forwarding, rp_filter, multicast forwarding, proxy neighbor, and link-down route behavior.

Risks and test signals: special negative ifindex constants must not be formatted as unsigned interface indexes. Tests should cover all attrs, `NETCONFA_ALL`, `IFINDEX_ALL`, `IFINDEX_DEFAULT`, and address-family-specific dumps.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/netconf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/netdev.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/netdev.h

Purpose: auto-generated generic netlink UAPI for the `netdev` family, exposing device XDP features, page pools, NAPI, queue stats, dmabuf bindings, queue leases, and io_uring provider hooks.

Important APIs/types/functions: exports family name/version, feature enums `netdev_xdp_act`, `netdev_xdp_rx_metadata`, `netdev_xsk_flags`, queue/NAPI enums, attribute groups for dev/page-pool/stats/NAPI/queue/qstats/lease/dmabuf, commands such as device get, page-pool get/stats, queue get/create, NAPI set, bind RX/TX, and multicast groups.

Control flow: userspace uses generic netlink to query devices, queues, NAPI instances, page pools, queue stats, bind queues to dmabufs or io_uring, create queues, and receive management/page-pool notifications.

State/persistence behavior: get/stat commands are observational; bind/create/set commands mutate netdev queue, NAPI, dmabuf, lease, and io_uring association state. Stats update with traffic and allocation behavior.

Dependencies/integration: generated from `netdev.yaml`. Integrates with XDP, AF_XDP, NAPI, page_pool, dmabuf, io_uring zcrx, and hardware queue management.

Risks and test signals: generated numeric gaps and nested attributes need exact decoding. Tests should cover feature bitmasks, queue type/scope enums, qstats counters, dmabuf fd/id attributes, bind RX/TX commands, and multicast group names.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/netdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/ipset/ip_set.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/ipset/ip_set.h

Purpose: defines ipset netfilter userspace ABI for protocol negotiation, set lifecycle, element add/delete/test, save/list/header/type operations, errors, flags, counters, and legacy socket interface.

Important APIs/types/functions: includes `IPSET_PROTOCOL`, command enum `ipset_cmd`, command/create/ADT/IP-address attributes, `enum ipset_errno`, command/CADT/create flags, `ip_set_id_t`, set dimension/kopt flags, counter match structs, `SO_IP_SET`, name/index union, and `ip_set_req_*` legacy structs.

Control flow: userspace sends nfnetlink ipset commands to create/destroy/flush/rename/swap/list/save sets and add/delete/test elements. Legacy iptables paths use getsockopt operations to resolve set names/indexes and kernel protocol version.

State/persistence behavior: commands mutate named set objects, elements, counters, comments, skb marks/prio/queue metadata, timeouts, and references in the network namespace. Listing and test commands are observational except counter side effects may be skipped by flags.

Dependencies/integration: depends on Linux types and netfilter nfnetlink subsystem ID `IPSET`. Integrates with iptables/nftables matches and set-type implementations.

Risks and test signals: attribute spaces overlap by command context and many flags are split across lower/upper halves. Tests should decode protocol attrs, restore line numbers, counter matches, comments, skbinfo, legacy `SO_IP_SET`, and type-specific error bases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/ipset/ip_set.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nf_tables.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nf_tables.h

Purpose: declares the full nftables nfnetlink ABI: ruleset object message types, tables, chains, rules, sets/elements, expressions, verdict/data/register schemas, stateful objects, flowtables, trace events, and tunnel/offload metadata.

Important APIs/types/functions: key groups include `nft_registers`, `nft_verdicts`, `nf_tables_msg_types`, table/chain/rule/set attributes, expression attributes for immediate, bitwise, byteorder, cmp, range, lookup, dynset, payload, exthdr, meta, rt, socket, ct, limit, counter, log, queue, quota, nat, tproxy, masq, redir, dup/fwd, fib, osf, synproxy, xfrm, trace, ng, tunnel, plus `NFT_OBJECT_*`.

Control flow: userspace sends batched nfnetlink transactions to create/update/delete/destroy/query tables, chains, rules, sets, elements, objects, and flowtables. Packet evaluation loads data into virtual registers, executes expressions in rule order, and returns verdicts or stateful side effects.

State/persistence behavior: most messages mutate persistent per-netns nftables ruleset state. Sets may contain timeouts, intervals, expressions, object refs, and dynamic updates. Counters, quotas, limits, last-seen, flowtables, and trace state evolve with packets.

Dependencies/integration: integrates with nfnetlink, generic netfilter verdicts/hooks, conntrack, NAT, routing/FIB, sockets/cgroups, XFRM, tunnel metadata, logging/queue subsystems, and compatibility layers.

Risks and test signals: schema is large, nested, versioned, and context-sensitive. Tests should decode every message type, object kind, expression attr family, transaction IDs, owner/persist flags, dynamic set operations, trace events, reset-get messages, and deprecated fields.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nf_tables.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nf_tables_compat.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nf_tables_compat.h

Purpose: defines nftables compatibility ABI for translating/querying legacy xtables matches and targets through nfnetlink.

Important APIs/types/functions: exports target attributes (`NFTA_TARGET_NAME`, `REV`, `INFO`), match attributes (`NFTA_MATCH_NAME`, `REV`, `INFO`), `NFT_COMPAT_NAME_MAX`, `NFNL_MSG_COMPAT_GET`, and compat query attributes (`NFTA_COMPAT_NAME`, `REV`, `TYPE`).

Control flow: userspace asks the nf_tables compat subsystem about legacy match/target support and embeds match/target info blobs inside nftables compatibility expressions/rules.

State/persistence behavior: query messages are observational. When used in nft rules, the info blobs become persistent ruleset state managed through the main nf_tables ABI.

Dependencies/integration: integrates with nfnetlink subsystem `NFNL_SUBSYS_NFT_COMPAT`, xtables modules, and `nf_tables.h` rule compatibility attributes.

Risks and test signals: `INFO` is opaque module-specific binary data. Tests should decode match/target names, revisions, compat type, name-length limits, and nested use from nft rule expressions without assuming blob structure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nf_tables_compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nfnetlink.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nfnetlink.h

Purpose: defines the common nfnetlink envelope ABI for netfilter netlink subsystems, multicast groups, subsystem/message ID splitting, batch messages, and the common `nfgenmsg` header.

Important APIs/types/functions: exports `enum nfnetlink_groups`, `struct nfgenmsg`, `NFNETLINK_V0`, `NFNL_SUBSYS_ID`, `NFNL_MSG_TYPE`, subsystem IDs for conntrack, queue, ulog, osf, ipset, acct, cttimeout, cthelper, nftables, compat, hook, and batch begin/end attributes.

Control flow: netfilter netlink messages carry `nfgenmsg` after `nlmsghdr`; high message-type bits select subsystem and low bits select subsystem operation. Batches use reserved begin/end messages and optional generation ID.

State/persistence behavior: common header is declarative. Batch boundaries coordinate atomic changes in subsystem state such as nftables transactions.

Dependencies/integration: includes `nfnetlink_compat.h` and Linux types. Every netfilter UAPI in this subset depends on this framing directly or conceptually.

Risks and test signals: subsystem/type bit splitting must be exact. Tests should cover multicast group names/numbers, `nfgenmsg` decoding, batch begin/end, generation IDs, and every `NFNL_SUBSYS_*` mapping.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nfnetlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nfnetlink_acct.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nfnetlink_acct.h

Purpose: defines nfnetlink accounting object ABI for named packet/byte counters, quotas, quota notifications, filtering, and counter-zeroing reads.

Important APIs/types/functions: exports `NFACCT_NAME_MAX`, message types `NFNL_MSG_ACCT_*`, quota flags `NFACCT_F_QUOTA_PKTS`, `BYTES`, `OVERQUOTA`, attributes for name, packets, bytes, use count, flags, quota, filter, and filter mask/value attributes.

Control flow: userspace creates/gets/deletes accounting objects, reads counters with or without reset, receives over-quota notifications, and can filter dumps by mask/value.

State/persistence behavior: accounting objects are persistent per-netns netfilter state. Packet/byte counters update with matching traffic, quota state can transition to overquota, and get-ctrzero mutates counters by clearing them.

Dependencies/integration: uses nfnetlink subsystem `NFNL_SUBSYS_ACCT` and integrates with nftables/iptables expressions that reference accounting objects.

Risks and test signals: counter-zeroing reads have side effects and overquota is kernel-set only. Tests should decode all message types, quota flags, name limits, filter nesting, and get-vs-get-reset behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nfnetlink_acct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nfnetlink_compat.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nfnetlink_compat.h

Purpose: provides legacy nfnetlink attribute helpers and old multicast group bitmasks for userspace compatibility.

Important APIs/types/functions: declares `struct nfattr`, old group masks such as `NF_NETLINK_CONNTRACK_NEW`, nesting/type macros `NFNL_NFA_NEST`, `NFA_TYPE`, alignment and traversal macros `NFA_ALIGN`, `NFA_OK`, `NFA_NEXT`, `NFA_LENGTH`, `NFA_SPACE`, `NFA_DATA`, `NFA_PAYLOAD`, and message helpers `NFM_NFA`/`NFM_PAYLOAD`.

Control flow: legacy parsers walk `nfattr` TLVs using length/alignment macros and detect nested payloads with the high type bit. Kernel-side helper macros are present for historical source compatibility.

State/persistence behavior: no runtime state; it defines binary parsing/wrapping rules for older nfnetlink payloads.

Dependencies/integration: depends on Linux types and assumes netlink/nfgenmsg helpers from including contexts. It is included by `nfnetlink.h`.

Risks and test signals: this header contains kernel-oriented statement macros that userspace tracers should not execute. Tests should validate alignment math, nested type masking, old group bit decoding, and payload length formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nfnetlink_compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nfnetlink_conntrack.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nfnetlink_conntrack.h

Purpose: defines conntrack and expectation nfnetlink ABI for creating, querying, deleting, dumping, filtering, and reporting connection tracking state.

Important APIs/types/functions: message enums cover CT and expectation operations plus stats/dying/unconfirmed dumps. Attribute groups describe tuples, IP addresses, L4 protocol fields, TCP/DCCP/SCTP protoinfo, counters, timestamps, NAT/protonat, sequence adjustment, synproxy, expectations, helper info, security context, per-CPU/global/expect stats, and filters.

Control flow: userspace sends ctnetlink messages to create/query/delete conntracks or expectations, optionally filter by tuple/status/marks/labels, retrieve stats, and receive multicast lifecycle events.

State/persistence behavior: conntrack entries, expectations, counters, NAT mapping, marks, labels, helper state, timestamps, and timeouts are mutable per-netns state. Counter-reset and delete operations have side effects.

Dependencies/integration: includes `nfnetlink.h`; integrates with netfilter hooks, NAT, helpers, labels, secctx, synproxy, and nftables `ct` expressions.

Risks and test signals: nested tuple direction and protocol-specific attrs are context-dependent. Tests should decode original/reply tuples, NAT aliases, 64-bit counters, timestamp events, expectation NAT, status masks, labels/masks, and stats messages.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nfnetlink_conntrack.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nfnetlink_cthelper.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nfnetlink_cthelper.h

Purpose: defines nfnetlink ABI for userspace connection tracking helper registration, query, deletion, helper policies, tuple metadata, queue number, private data length, and enable/disable status.

Important APIs/types/functions: exports helper status constants, message types `NFNL_MSG_CTHELPER_*`, top-level attributes `NFCTH_*`, policy-set attributes supporting multiple policy entries, policy attributes for name/expect max/timeout, and tuple attrs for L3/L4 protocol numbers.

Control flow: userspace registers helpers with name, tuple, policy, queue, private data size, and status, queries registered helpers, or deletes them.

State/persistence behavior: helper objects are persistent kernel conntrack-helper state and can affect later packet processing and expectation creation until removed or disabled.

Dependencies/integration: uses nfnetlink subsystem `NFNL_SUBSYS_CTHELPER`; integrates with conntrack expectations, userspace helper queues, and nftables ct helper objects.

Risks and test signals: policy sets use repeated numbered attributes and helper status can be changed. Tests should decode nested policy sets, tuple protocol fields, private data length, queue number, status constants, and get/delete messages.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nfnetlink_cthelper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nfnetlink_cttimeout.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nfnetlink_cttimeout.h

Purpose: defines nfnetlink ABI for named conntrack timeout policies and protocol-specific timeout values.

Important APIs/types/functions: exports timeout message types for new/get/delete/default set/default get, top-level attrs `CTA_TIMEOUT_*`, protocol timeout attr groups for generic, TCP, UDP, UDPLite, ICMP, DCCP, SCTP, ICMPv6, GRE, and `CTNL_TIMEOUT_NAME_MAX`.

Control flow: userspace creates or queries timeout policy objects by name/L3/L4 protocol, provides nested per-protocol timeout data, deletes policies, or reads/sets protocol defaults.

State/persistence behavior: timeout policy objects and defaults are persistent per-netns conntrack configuration and influence expiration of future/live conntrack entries depending on attachment.

Dependencies/integration: includes `nfnetlink.h`; integrates with conntrack, nftables ct timeout objects, and helper/expectation behavior.

Risks and test signals: protocol-specific nested attr interpretation changes with L4 protocol. Tests should decode every protocol timeout enum, default set/get messages, name limits, use counts, and unused/deprecated SCTP heartbeat-acked value.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nfnetlink_cttimeout.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nfnetlink_hook.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nfnetlink_hook.h

Purpose: defines nfnetlink hook introspection ABI for listing registered netfilter hooks and associated nftables/BPF/flowtable metadata.

Important APIs/types/functions: exports `NFNL_MSG_HOOK_GET`, hook attributes for hook number, priority, device, function name, module name, and chain info; chain info attributes for description/type; chain description attrs for table/family/name; hook chain types; and BPF attrs for program ID.

Control flow: userspace sends hook get/dump requests and receives records describing hook registrations and their owning module/function or base-chain metadata.

State/persistence behavior: read-only introspection over live hook registrations. Output changes as nftables chains, BPF programs, modules, and flowtables register/unregister hooks.

Dependencies/integration: uses nfnetlink subsystem `NFNL_SUBSYS_HOOK`; chain descriptors depend on `nf_tables.h` table attributes and BPF program IDs.

Risks and test signals: nested chain info changes shape based on type. Tests should cover nftables, BPF, and flowtable chain types, optional device names, function/module strings, priority formatting, and nested descriptions.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nfnetlink_hook.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nfnetlink_log.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nfnetlink_log.h

Purpose: defines NFLOG nfnetlink ABI for packet log delivery and logging instance configuration.

Important APIs/types/functions: exports message types `NFULNL_MSG_PACKET` and `CONFIG`, packet header/hardware/timestamp structs, VLAN attrs, packet attrs for marks, ifindexes, hwaddr, payload, prefix, UID/GID, sequence numbers, conntrack info, VLAN and L2 headers, config command/mode structs, config attrs, copy modes, and config flags.

Control flow: userspace binds/unbinds logging groups, configures copy mode/range, buffer size, timeout, queue threshold, and flags, then receives logged packet messages containing selected metadata and payload.

State/persistence behavior: configuration messages mutate logging-instance state. Packet messages are transient; sequence counters and queueing behavior evolve with traffic.

Dependencies/integration: includes Linux types and `nfnetlink.h`; integrates with iptables/nftables log targets/expressions, conntrack metadata, and netlink multicast delivery.

Risks and test signals: packed config structs, endian timestamps, and optional metadata attrs require careful formatting. Tests should decode config commands/modes, copy modes, seq flags, conntrack attrs, VLAN nesting, and packet payload truncation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nfnetlink_log.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nfnetlink_osf.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nfnetlink_osf.h

Purpose: defines passive OS fingerprinting ABI for netfilter OSF match support, including fingerprint records, matching flags, TCP option encoding, and add/remove nfnetlink messages.

Important APIs/types/functions: key types are `nf_osf_wc`, `nf_osf_opt`, `nf_osf_info`, `nf_osf_user_finger`, and `nf_osf_nlmsg`. Constants cover matching flags, log levels, TTL comparison modes, IANA TCP option kinds, window-size state machine values, OSF attributes, and `OSF_MSG_ADD/REMOVE`.

Control flow: userspace adds or removes OS fingerprints over nfnetlink. Packet matching compares IP/TCP header values, TTL/window/MSS wildcard rules, options, genre/version/subtype, and logs according to configured OSF info.

State/persistence behavior: fingerprint tables are persistent kernel netfilter state until removed. Match/log behavior affects later packet classification and logging but packet messages are transient.

Dependencies/integration: includes Linux IP/TCP header definitions and types. Integrates with nftables/iptables OSF expressions and netfilter packet path.

Risks and test signals: arrays sized by `MAX_IPOPTLEN` and multiple wildcard modes can be hard to render. Tests should decode add/remove messages, fingerprint strings, TTL/log flags, option arrays, window-size wildcard modes, and embedded IP/TCP headers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nfnetlink_osf.h -->
