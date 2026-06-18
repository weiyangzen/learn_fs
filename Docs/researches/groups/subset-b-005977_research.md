# Research: subset-b-005977

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/bpf_common.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/bpf_common.h

## Purpose
Defines the common classic BPF instruction encoding constants shared by user space and kernel code. The header is the low-level bit layout for decoding a BPF opcode into instruction class, load size, addressing mode, ALU/jump operation, source operand, and maximum classic-program length.

## APIs, Control Flow, and State
The API is macro-only: `BPF_CLASS()`, `BPF_SIZE()`, `BPF_MODE()`, `BPF_OP()`, and `BPF_SRC()` mask opcode fields, while constants such as `BPF_LD`, `BPF_LDX`, `BPF_ST`, `BPF_ALU`, `BPF_JMP`, `BPF_RET`, `BPF_W/H/B`, `BPF_IMM/ABS/IND/MEM/LEN/MSH`, ALU ops, jump ops, `BPF_K`, and `BPF_X` name field values. `BPF_MAXINSNS` defaults to 4096 if an includer has not provided a different value. There is no executable control flow or persistent state in the header; state lives in BPF program arrays and verifier/runtime users that interpret these bit fields.

## Dependencies, Integration, Risks, and Tests
The header is dependency-light and integrates with socket filters, seccomp, BPF loaders, disassemblers, and kernel compatibility code that still parses classic BPF opcodes. Risks are ABI drift in numeric opcode values, callers confusing classic BPF encodings with eBPF-only extensions, and out-of-tree code overriding `BPF_MAXINSNS` inconsistently. Test signals include classic socket-filter load tests, seccomp filter tests, BPF assembler/disassembler round trips, and compile checks for tools that include only UAPI headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/bpf_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/bpf_perf_event.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/bpf_perf_event.h

## Purpose
Defines the UAPI context passed to BPF programs attached to perf events. It provides the common wrapper around architecture-specific register state and sample-period data.

## APIs, Control Flow, and State
The header includes `<asm/bpf_perf_event.h>` for the architecture-defined `bpf_user_pt_regs_t` and declares `struct bpf_perf_event_data` with `regs` and `sample_period`. There are no functions or control branches; the structure is populated by perf/BPF attachment paths and consumed by BPF programs and loaders that know the target architecture's register layout. No persistence is owned by the header.

## Dependencies, Integration, Risks, and Tests
The main dependency is the arch UAPI perf-event register definition. Integration points are `BPF_PROG_TYPE_PERF_EVENT`, perf sampling, tracing/profiling programs, and libbpf skeletons that expose the context type. Risks include architecture register-layout mismatches, user programs assuming portable register fields where the layout is arch-specific, and sample-period interpretation errors for different perf event modes. Test signals include building BPF perf-event programs on each supported architecture, perf sample-period validation, and verifier tests that access `ctx->regs` and `ctx->sample_period`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/bpf_perf_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/bpqether.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/bpqether.h

## Purpose
Defines the legacy BPQ Ethernet UAPI used by AX.25-over-Ethernet drivers and tools. It exposes private socket ioctl numbers and small request structures for configuring BPQ Ethernet addresses and level-1 parameters.

## APIs, Control Flow, and State
Important exports are `SIOCSBPQETHOPT`, `SIOCSBPQETHADDR`, `SIOCGBPQETHPARAM`, `SIOCSBPQETHPARAM`, `struct bpq_ethaddr`, and `struct bpq_req`. `bpq_ethaddr` carries a destination Ethernet address, accepted source address, and an AX.25 address string sized by `AX25_ADDR_LEN`. `bpq_req` carries command, speed, clock mode, and persistence-style link parameters. The header contains no executable logic; control flow is in the BPQ Ethernet netdevice ioctl handlers, and state is persisted by the driver/device configuration.

## Dependencies, Integration, Risks, and Tests
Depends on `<linux/if_ether.h>` and AX.25 sizing conventions. Integration points include amateur-radio AX.25 networking, netdevice private ioctl dispatch, and legacy BPQ configuration tools. Risks are ioctl-number collisions in private ranges, fixed-size address/name assumptions, lack of modern netlink-style extensibility, and tools depending on obsolete driver behavior. Test signals include ioctl compatibility tests with BPQ devices, address length validation, and regression tests for 32/64-bit userspace structure layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/bpqether.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/bsg.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/bsg.h

## Purpose
Defines the block SCSI generic v4 userspace command ABI used by `/dev/bsg/*` and io_uring passthrough. It carries protocol identifiers, command/request pointers, data buffers, sense data, status fields, and packed helpers for io_uring SCSI result reporting.

## APIs, Control Flow, and State
`struct sg_io_v4` is the main ioctl payload. It includes guard/protocol/subprotocol fields, request and response lengths, user pointers, bidirectional data-transfer pointers and lengths, timeout/flags, device/transport/driver status, residual count, duration, and generated tag. `struct bsg_uring_cmd` is the io_uring variant with request buffer, data/sense addresses, lengths, timeout, flags, and `usr_ptr`. The header also defines queue-placement flags and inline helpers to unpack/build `res2` status fields: device status, driver status, host status, sense length, residual length, and combined builder. Control flow is external in bsg, SCSI, and io_uring command dispatch; this header only fixes ABI layouts. Persistent state is in device queues, pending commands, and user buffers referenced by the structures.

## Dependencies, Integration, Risks, and Tests
Depends on Linux integer types and kernel-only build assertions for structure size. Integration points are SCSI generic passthrough, block transport management, bsg char devices, and io_uring command completion. Risks include user pointer validation, 32/64-bit ABI compatibility, unchecked response/sense lengths, status packing mistakes in `res2`, and exposing transport commands to callers with insufficient permissions. Test signals include sg3_utils passthrough tests, bsg transport management commands, io_uring passthrough completion-status tests, compat syscall tests, and fuzzing of lengths, flags, and timeout paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/bsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/bt-bmc.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/bt-bmc.h

## Purpose
Provides the userspace ioctl for IPMI BT BMC character devices. It lets management software assert the SMS attention signal through the BMC BT interface.

## APIs, Control Flow, and State
The header includes `<linux/ioctl.h>`, defines `__BT_BMC_IOCTL_MAGIC`, and exposes `BT_BMC_IOCTL_SMS_ATN` as an `_IO` command. There are no data structures or inline helpers. Control flow is entirely in the BT BMC driver ioctl handler, which interprets this command as a signal operation. Device and IPMI transaction state live in the driver/hardware, not in the header.

## Dependencies, Integration, Risks, and Tests
Integrates with OpenBMC/IPMI BT BMC device nodes and host-management daemons. Risks are incorrect ioctl magic reuse, missing permission checks around attention signaling, and callers assuming the command queues payload data when it is signal-only. Test signals include ioctl smoke tests on BT BMC devices, permission/namespace checks for the character device, and IPMI host-notification integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/bt-bmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/btf.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/btf.h

## Purpose
Defines the BPF Type Format binary ABI used to describe C types, function prototypes, variables, data sections, declaration tags, type tags, and 64-bit enums for BPF, kernel BTF, module BTF, and CO-RE relocation consumers.

## APIs, Control Flow, and State
Key exports include `BTF_MAGIC`, `BTF_VERSION`, `struct btf_header`, `struct btf_type`, kind constants from `BTF_KIND_UNKN` through `BTF_KIND_ENUM64`, masks such as `BTF_MAX_TYPE`, `BTF_MAX_NAME_OFFSET`, and `BTF_MAX_VLEN`, and field helpers `BTF_INFO_KIND()`, `BTF_INFO_VLEN()`, `BTF_INFO_KFLAG()`, `BTF_INT_ENCODING()`, `BTF_INT_OFFSET()`, `BTF_INT_BITS()`, `BTF_MEMBER_BITFIELD_SIZE()`, and `BTF_MEMBER_BIT_OFFSET()`. Payload structs include `btf_enum`, `btf_array`, `btf_member`, `btf_param`, `btf_var`, `btf_var_secinfo`, `btf_decl_tag`, and `btf_enum64`; `enum btf_func_linkage` and variable-linkage enums describe linkage semantics. The header has no runtime control flow; BTF parsers walk the header's type and string sections, interpret kind-specific trailing records, and resolve type IDs. BTF blobs are persisted in ELF sections, kernel sysfs/debug interfaces, and BPF object metadata outside this header.

## Dependencies, Integration, Risks, and Tests
Depends on `<linux/types.h>` and fixed-width UAPI integer layout. Integration points are libbpf, bpftool, BPF verifier type checking, BPF CO-RE, kernel/module BTF generation, pahole, and tracing pretty printers. Risks include malformed offsets or vlen causing parser overruns, mismatch between `kind_flag` interpretation for structs/unions/enums, type-ID exhaustion assumptions, endian handling in serialized blobs, and consumers ignoring newer kinds such as `DECL_TAG`, `TYPE_TAG`, or `ENUM64`. Test signals include BTF parser fuzzing, libbpf CO-RE relocation tests, bpftool dump validation, verifier tests with function prototypes and data sections, and cross-endian BTF load checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/btf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/btrfs.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/btrfs.h

## Purpose
Defines the userspace ioctl ABI for Btrfs filesystem management. It covers subvolume and snapshot operations, device management, scrub, device replace, filesystem and device information, feature flags, balance, tree search, clone/dedupe, defrag, quota/qgroup operations, send/receive metadata, encoded read/write, subvolume cleanup waiting, and shutdown.

## APIs, Control Flow, and State
The main API surface is a set of `BTRFS_IOC_*` ioctl numbers built around `BTRFS_IOCTL_MAGIC`. Important structures include `btrfs_ioctl_vol_args` and `_v2` for named/by-id subvolume and device operations; qgroup limit/inherit structures; scrub progress/args; device replace start/status/args; device and filesystem info structures; feature-flag structures; packed `btrfs_balance_args`, `btrfs_balance_progress`, and `btrfs_ioctl_balance_args`; inode/path/logical lookup containers; tree-search key/header/args and v2 flexible-buffer form; clone, defrag, extent-same, space-info, device-stat, quota, send, subvolume-info/rootref, encoded I/O, and subvolume-wait structures. Control flow is ioctl-driven: user space fills an argument struct, the filesystem validates flags and pointers, may mutate persistent filesystem metadata, and returns status/progress fields in the same structure. State and persistence are central to this ABI: subvolumes, qgroups, feature bits, balance progress, scrub/device-replace cursors, send/receive UUID/transid metadata, and encoded extents all map to persistent Btrfs metadata or long-running kernel jobs.

## Dependencies, Integration, Risks, and Tests
Depends on `<linux/types.h>`, `<linux/ioctl.h>`, `<linux/fs.h>`, user-pointer annotations, and Btrfs on-disk constants shared with `btrfs_tree.h`. Integration points include btrfs-progs, mount/admin tools, backup tools using send/receive, dedupe/reflink users, quota managers, scrub/balance daemons, encoded I/O tools, and generic fs-label ioctls. Risks are high because this is a stable UAPI: structure padding and flexible arrays must remain compatible, flag masks must reject unknown behavior safely, CAP_SYS_ADMIN-gated operations such as encoded I/O and device-stat reset must stay protected, long-running jobs can race with cancellation/progress queries, and feature-bit changes can render filesystems unmountable on older kernels. Test signals include btrfs-progs ioctl tests, xfstests for subvolumes/snapshots/send/receive/dedupe/quota/scrub/balance/replace, compat 32-bit ioctl tests, feature-flag downgrade tests, encoded-read/write corruption tests, and fuzzing of user pointers, sizes, and reserved fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/btrfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/btrfs_tree.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/btrfs_tree.h

## Purpose
Defines Btrfs on-disk metadata constants and packed structures that user space can retrieve through tree-search ioctls. It describes tree object IDs, key types, superblock and tree-block layouts, chunk/device records, extent/reference records, inode and directory items, root/subvolume metadata, balance persistence, file extents, block-group and quota metadata, verity descriptors, and remap items.

## APIs, Control Flow, and State
The header exposes persistent identifiers such as `BTRFS_ROOT_TREE_OBJECTID`, extent/chunk/dev/fs/csum/quota/uuid/free-space/block-group/raid-stripe/remap tree IDs, special object IDs for balance/orphan/log/reloc/csum/free-space/free-ino, item-key constants for inode refs, xattrs, verity, directories, extents, roots, block groups, free space, devices/chunks, qgroups, dev replace, UUIDs, and strings. Major packed structs include `btrfs_disk_key`, `btrfs_key`, `btrfs_header`, `btrfs_root_backup`, `btrfs_item`, `btrfs_leaf`, `btrfs_node`, `btrfs_dev_item`, `btrfs_stripe`, `btrfs_chunk`, `btrfs_super_block`, free-space records, RAID stripe records, extent refs, dev extents, inode refs/items/times, dir items, root items/refs, disk balance args/items, file extent items, checksum/dev-stat/dev-replace items, block-group items, qgroup status/info/limit items, verity descriptors, and remap items. Inline helpers convert directory flags to file type, compute legacy root item size, convert chunk profile flags to extended profile flags and back, and extract qgroup level. There is no active algorithm in the header, but the structures are the persistent state format of the filesystem; kernel and tools traverse B-trees by key order and interpret item payloads according to these definitions.

## Dependencies, Integration, Risks, and Tests
Depends on `linux/btrfs.h`, Linux fixed-width types, `offsetof`, endian-qualified integer types, and flexible-array declarations. Integration points are kernel Btrfs metadata readers/writers, btrfs-progs, fsck/restore, tree-search ioctl consumers, scrub and recovery tools, send/receive metadata interpretation, and any code validating on-disk feature compatibility. Risks include packed layout or endian mistakes, item-key numeric reuse breaking old tools, corrupted metadata causing parser overreads, feature flags or new item types not being understood by old user space, confusion between CPU-order `btrfs_key` and disk-order `btrfs_disk_key`, and persistent-state transitions such as device replace, balance, qgroups, remap, and block-group-tree migration. Test signals include btrfs image round-trip tests, fsck validation, xfstests metadata/recovery groups, tree-search dump comparisons, endian build tests, superblock size/layout assertions, fuzzed filesystem images, and backward/forward compatibility tests with btrfs-progs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/btrfs_tree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/byteorder/big_endian.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/byteorder/big_endian.h

## Purpose
Defines UAPI byte-order conversion macros for big-endian architectures. It marks the host as big-endian and maps CPU/native, little-endian, big-endian, and network-order conversions to either identity casts or byte-swapping helpers.

## APIs, Control Flow, and State
The header defines `__BIG_ENDIAN`, `__BIG_ENDIAN_BITFIELD`, includes `stddef`, `types`, and `swab`, and exports constant, value, pointer, and in-place conversion macros such as `__constant_htonl`, `__constant_cpu_to_le32`, `__cpu_to_be64`, `__le32_to_cpu`, `__cpu_to_le32p`, and `__cpu_to_be32s`. On a big-endian CPU, big-endian/network conversions are identity casts, while little-endian conversions call `___constant_swab*`, `__swab*`, pointer swab, or in-place swab. There is no runtime state; the "control flow" is compile-time selection by including the architecture's byteorder header.

## Dependencies, Integration, Risks, and Tests
Depends on endian-qualified Linux types and swab helpers. Integration points include every UAPI structure with fixed wire/disk endianness, especially filesystems, networking, storage, and ioctl structs containing `__le*` or `__be*`. Risks include including the wrong endian header for the target architecture, losing sparse `__force` type checking through casts, evaluating macro arguments with side effects, and mismatched bitfield layout in headers that key on `__BIG_ENDIAN_BITFIELD`. Test signals include cross-compilation for big-endian architectures, sparse endian warnings, protocol/filesystem round trips, and layout tests for bitfield-bearing UAPI structs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/byteorder/big_endian.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/byteorder/little_endian.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/byteorder/little_endian.h

## Purpose
Defines UAPI byte-order conversion macros for little-endian architectures. It marks the host as little-endian and maps CPU/native, little-endian, big-endian, and network-order conversions to identity casts or byte swaps.

## APIs, Control Flow, and State
The header defines `__LITTLE_ENDIAN`, `__LITTLE_ENDIAN_BITFIELD`, includes `stddef`, `types`, and `swab`, and exports the same constant, value, pointer, and in-place conversion families as the big-endian variant. On little-endian CPUs, little-endian conversions are identity casts, while big-endian/network conversions use swab helpers. It has no runtime state and no function control flow; conversion behavior is selected by preprocessor inclusion.

## Dependencies, Integration, Risks, and Tests
Depends on Linux fixed-width/endian types and swab helpers. Integration points are broad: socket protocols, disk formats, device descriptors, ioctl payloads, and user tools that include kernel UAPI headers. Risks include side effects in macro arguments, incorrect bitfield assumptions when a UAPI struct uses `__LITTLE_ENDIAN_BITFIELD`, poor test coverage on big-endian peers, and accidentally using host-order values where an explicit `__be*`/`__le*` conversion is required. Test signals include sparse endian checking, cross-endian protocol/file-image tests, and build coverage for user programs including this header outside the kernel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/byteorder/little_endian.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/cachefiles.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/cachefiles.h

## Purpose
Defines the UAPI control protocol for CacheFiles, the local disk-cache backend used by FS-Cache/Netfs clients. It names the devnode, daemon control commands, error classes, and object-state notifications exchanged through the cachefiles control interface.

## APIs, Control Flow, and State
The header exports the cachefiles devnode name and single-character command identifiers such as bind, brun, bcull, bstop, cull, debug, dir, frun, fcull, fstop, inuse, secctx, tag, and xcalloc/xdebug/xdir/xsecctx/xstat variants. It also defines error classes like daemon bind error, daemon error, cull error, and restore error, plus state identifiers including absent, available, active, burried, and culled. The header is macro-only; control flow occurs in the cachefiles daemon and kernel control parser, where commands transition cache availability and object state. Persistent state is the on-disk cache tree and daemon policy, not the header.

## Dependencies, Integration, Risks, and Tests
Integration points are the cachefiles daemon, FS-Cache users such as network filesystems, security-context setup, cache culling, and cache restore paths. Risks include string-command compatibility, daemon/kernel version mismatch, unsafe cache-directory permissions, SELinux/security-context handling errors, and stale object-state assumptions after crashes. Test signals include cachefilesd control-command tests, FS-Cache/netfs read-through workloads, culling and restore simulations, security-context tests, and crash/restart validation of object states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/cachefiles.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/can.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/can.h

## Purpose
Defines the core SocketCAN UAPI shared by raw CAN, CAN FD, CAN XL, BCM, ISO-TP, J1939, gateways, and netlink configuration. It standardizes CAN identifiers, frame layouts, protocol numbers, socket addresses, and filter structures.

## APIs, Control Flow, and State
Important exports include `canid_t`, `can_err_mask_t`, identifier flags/masks (`CAN_EFF_FLAG`, `CAN_RTR_FLAG`, `CAN_ERR_FLAG`, `CAN_SFF_MASK`, `CAN_EFF_MASK`), payload sizes for classic CAN, CAN FD, and CAN XL, `struct can_frame`, `struct canfd_frame`, `struct canxl_frame`, MTU constants, protocol numbers (`CAN_RAW`, `CAN_BCM`, `CAN_ISOTP`, `CAN_J1939`), `SOL_CAN_BASE`, `struct sockaddr_can`, and `struct can_filter`. The frame structs encode the per-packet state passed through sockets; `sockaddr_can` selects interface and protocol-specific addressing data. There is no implementation control flow in the header; kernel socket families validate MTU, flags, and filters and route frames to netdevices and protocol modules.

## Dependencies, Integration, Risks, and Tests
Depends on Linux integer, socket, and `offsetof` definitions. Integration spans PF_CAN sockets, CAN netdevices, vcan/vxcan, CAN FD/XL drivers, filters, error frames, and protocol modules. Risks include ABI layout constraints for the dual-use classic/FD structs, misinterpreting CAN ID flag bits as identifier bits, accepting invalid CAN XL length or mandatory XLF flags, filter inversion errors, and userspace not enabling FD/XL support before sending larger MTUs. Test signals include SocketCAN selftests, vcan/vxcan frame send/receive, CAN FD/XL MTU validation, filter-match tests including inverted filters, and compat layout checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/can.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/can/bcm.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/can/bcm.h

## Purpose
Defines the SocketCAN Broadcast Manager protocol ABI. It supports timed transmit jobs, receive filters, change notifications, and multiplexed CAN/CAN FD frame handling through BCM socket messages.

## APIs, Control Flow, and State
Exports include `struct bcm_timeval`, `struct bcm_msg_head`, operation codes such as `TX_SETUP`, `TX_DELETE`, `TX_READ`, `TX_SEND`, `RX_SETUP`, `RX_DELETE`, `RX_READ`, `TX_STATUS`, `TX_EXPIRED`, `RX_STATUS`, `RX_TIMEOUT`, and `RX_CHANGED`, plus flags like `SETTIMER`, `STARTTIMER`, `TX_COUNTEVT`, `TX_ANNOUNCE`, `TX_CP_CAN_ID`, `RX_FILTER_ID`, `RX_CHECK_DLC`, `RX_NO_AUTOTIMER`, `RX_ANNOUNCE_RESUME`, `TX_RESET_MULTI_IDX`, `RX_RTR_FRAME`, and `CAN_FD_FRAME`. User messages carry timers, counters, CAN ID filters, frame count, and a following frame array. Kernel BCM sockets maintain the persistent per-socket job/filter state and timers; the header only defines the message contract.

## Dependencies, Integration, Risks, and Tests
Depends on core `linux/can.h` and fixed-width types. Integration points are PF_CAN BCM sockets, periodic transmission, receive timeout/change detection, and CAN FD frame arrays. Risks include variable-length frame array bounds, timer/counter races, userspace mixing classic and FD frames without `CAN_FD_FRAME`, and 32/64-bit `bcm_timeval` compatibility. Test signals include BCM selftests for setup/read/delete, periodic transmit expiry, RX timeout/change events, RTR behavior, CAN FD jobs, and malformed message length fuzzing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/can/bcm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/can/error.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/can/error.h

## Purpose
Defines SocketCAN error-frame class bits and payload byte encodings. It lets drivers and userspace classify arbitration loss, controller errors, protocol violations, transceiver faults, ACK failures, bus-off, bus-error, restart, and error-counter reports.

## APIs, Control Flow, and State
The header exports `CAN_ERR_DLC`, top-level `CAN_ERR_*` mask bits, per-byte detail constants such as `CAN_ERR_LOSTARB_*`, controller state bits, protocol violation bits, protocol-location codes, transceiver status codes, and error-counter byte assignments. There are no functions; drivers populate an error `can_frame` with `CAN_ERR_FLAG` plus these masks, and userspace decodes `data[0]` through `data[7]` according to the constants. Persistent controller error state lives in the CAN driver/netdevice, not in the header.

## Dependencies, Integration, Risks, and Tests
Integrates with CAN drivers, raw sockets subscribed to error masks, netlink state/error counters, and diagnostic tools. Risks include flooding userspace with bus-error frames, drivers setting inconsistent class/detail bytes, ambiguity in unspecified locations/statuses, and userspace forgetting that error frames use classic CAN DLC 8 even for FD-capable devices. Test signals include injected CAN controller error states, raw socket error-mask filtering, bus-off/restart tests, transceiver error mapping checks, and diagnostics comparing error frames with netlink counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/can/error.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/can/gw.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/can/gw.h

## Purpose
Defines the SocketCAN gateway netlink ABI for routing, filtering, modifying, and checksum-updating CAN and CAN FD frames between CAN interfaces.

## APIs, Control Flow, and State
The header exports gateway routing flag bits, netlink attribute IDs, `struct rtcanmsg`, CAN/CAN FD frame modification structures, checksum descriptors (`cgw_csum_xor`, `cgw_csum_crc8`), CRC8 profile constants, and length macros for each attribute payload. A gateway rule combines source/destination interfaces, filter/mask, optional frame modifications, checksum operations, and deletion/echo/control flags. Control flow is in the gateway netlink handler and packet forwarding path: rules are created, matched against incoming frames, transformations are applied, and packets are emitted to destination interfaces. Persistent state is the configured gateway rule table in the kernel.

## Dependencies, Integration, Risks, and Tests
Depends on core CAN frame layouts and netlink route-message conventions. Integration points are can-gw userspace tools, CAN network namespaces, vcan/vxcan setups, and in-kernel CAN receive/transmit paths. Risks include malformed netlink attributes, out-of-bounds modification/checksum offsets, rule loops between interfaces, FD/classic frame-size confusion, and CRC profile drift. Test signals include can-gw rule add/delete/list tests, frame modification and checksum verification, loop-prevention tests, netns/vxcan forwarding, and fuzzed netlink attribute lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/can/gw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/can/isotp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/can/isotp.h

## Purpose
Defines the SocketCAN ISO 15765-2 transport protocol socket options. It exposes addressing, padding, flow-control, link-layer, timing, broadcast, and CAN FD support configuration for ISO-TP sockets.

## APIs, Control Flow, and State
Exports include `SOL_CAN_ISOTP`, socket option names `CAN_ISOTP_OPTS`, `CAN_ISOTP_RECV_FC`, `CAN_ISOTP_TX_STMIN`, `CAN_ISOTP_RX_STMIN`, and `CAN_ISOTP_LL_OPTS`; structures `can_isotp_options`, `can_isotp_fc_options`, and `can_isotp_ll_options`; flags such as listen mode, extended/RX extended addressing, TX/RX padding and pad checks, half-duplex, forced STmin, wait-for-TX-done, single-frame and consecutive-frame broadcast, and dynamic flow-control parameters; defaults for flags, padding, frame tx time, block size, STmin, WFTmax, MTU, tx data length, and tx flags; and `CAN_ISOTP_FRAME_TXTIME_ZERO`. Kernel ISO-TP sockets use these options to drive segmentation, flow-control exchange, timers, padding validation, and CAN/CAN FD frame generation. Per-socket protocol state persists in the kernel.

## Dependencies, Integration, Risks, and Tests
Depends on `linux/can.h` and fixed-width types. Integration points are PF_CAN ISO-TP sockets, automotive diagnostics, UDS tools, CAN FD transport, and vcan tests. Risks include invalid extended-address combinations, padding-check incompatibility with peers, STmin unit/override confusion, broadcast modes bypassing normal flow control, invalid link-layer MTU/tx_dl pairs, and timing races around half-duplex or wait-for-TX-done. Test signals include ISO-TP selftests for multi-frame transfer, flow-control limits, padding validation, CAN FD payload sizes, broadcast modes, timeout paths, and setsockopt/getsockopt round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/can/isotp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/can/j1939.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/can/j1939.h

## Purpose
Defines the SocketCAN SAE J1939 transport and addressing UAPI. It provides PGN/address/name types, common PGN constants, socket options, ancillary message identifiers, and filter structures for heavy-duty vehicle and industrial CAN networks.

## APIs, Control Flow, and State
Exports include address/name/PGN constants (`J1939_MAX_UNICAST_ADDR`, idle/no address/name, request/address-claimed/address-commanded PGNs, PDU1 and max PGN values), typedefs `pgn_t`, `priority_t`, `name_t`, `SOL_CAN_J1939`, socket options for filters, promiscuous mode, send priority, error queue, and loopback, SCM identifiers for destination address/name and priority, filter flags, `struct j1939_filter`, and `J1939_FILTER_MAX`. The kernel protocol stack uses socket bind/connect/sendmsg control data and filters to resolve names, addresses, priority, PGNs, and transport sessions. Persistent state lives in per-socket filters/options and the J1939 address/name tables.

## Dependencies, Integration, Risks, and Tests
Depends on core CAN and socket headers. Integration points are PF_CAN J1939 sockets, address claim handling, transport protocol sessions, error queues, and userspace diagnostics. Risks include PGN masking mistakes for PDU1/PDU2 semantics, large filter arrays, spoofed name/address handling, priority misconfiguration, and error-queue compatibility. Test signals include J1939 selftests, address-claim/request PGN exchange, filter mask behavior, loopback/promiscuous modes, transport sessions over vcan, and ancillary data round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/can/j1939.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/can/netlink.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/can/netlink.h

## Purpose
Defines rtnetlink attributes and structures for configuring CAN netdevices. It covers bit timing, data bit timing, CAN XL timing, clocking, controller state, error counters, controller modes, statistics, termination, transceiver delay compensation, and restart behavior.

## APIs, Control Flow, and State
Important structures are `can_bittiming`, `can_bittiming_const`, `can_clock`, `can_berr_counter`, `can_ctrlmode`, `can_device_stats`, and TDC structures/consts. `enum can_state` names controller lifecycle states from error-active through bus-off and stopped/sleeping. Control-mode bits cover loopback, listen-only, triple sampling, one-shot, bus-error reporting, CAN FD, presume ACK, non-ISO FD, CC len8 DLC, FD and XL TDC auto/manual, restricted mode, CAN XL, and XL TMS. Attribute enums define `IFLA_CAN_*` payloads and nested TDC attributes. Control flow is rtnetlink-driven: userspace sends attributes through `ip link`/netlink, drivers validate capabilities and timing ranges, and controller state/statistics are reported back. Persistent state is netdevice configuration and controller runtime state.

## Dependencies, Integration, Risks, and Tests
Depends on Linux fixed-width types and rtnetlink conventions. Integration points are CAN drivers, `ip link set type can`, netlink monitors, CAN FD/XL controller configuration, bus-off restart, and termination management. Risks include invalid timing calculations, controllers advertising unsupported modes, TDC range errors, state/statistics races, netlink attribute versioning, and mixing arbitration/data/XL timing fields. Test signals include can netlink selftests, driver bit-timing boundary tests, mode toggles for FD/XL/TDC, bus-off/restart tests, termination get/set, and `iproute2` compatibility checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/can/netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/can/raw.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/can/raw.h

## Purpose
Defines the SocketCAN RAW protocol socket options. It lets userspace configure classic/FD/XL frame reception, filter lists, error filters, loopback, receive-own-messages behavior, join filters, and CAN XL virtual CAN ID handling.

## APIs, Control Flow, and State
Exports include `SOL_CAN_RAW`, `CAN_RAW_FILTER_MAX`, option enums for `CAN_RAW_FILTER`, `CAN_RAW_ERR_FILTER`, `CAN_RAW_LOOPBACK`, `CAN_RAW_RECV_OWN_MSGS`, `CAN_RAW_FD_FRAMES`, `CAN_RAW_JOIN_FILTERS`, `CAN_RAW_XL_FRAMES`, and `CAN_RAW_XL_VCID_OPTS`, plus `struct can_raw_vcid_options` and VCID option flags for TX set/pass and RX filter. RAW sockets store per-socket filter arrays and mode flags; receive paths match frames against filters and error masks, while transmit paths validate MTU and optional XL VCID behavior. The header itself has no runtime logic.

## Dependencies, Integration, Risks, and Tests
Depends on `linux/can.h`. Integration points are PF_CAN RAW sockets, candump/cansend-style tools, vcan/vxcan tests, CAN FD/XL enablement, and error-frame diagnostics. Risks include large filter-array allocations, inverted/joined filter semantics surprising users, sending FD/XL frames without enabling the corresponding option, VCID masking mistakes, and loopback/own-message confusion in multi-socket tests. Test signals include raw socket filter tests, error-mask subscriptions, FD/XL send/receive, VCID option validation, and loopback/receive-own toggles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/can/raw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/can/vxcan.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/can/vxcan.h

## Purpose
Defines the netlink information attributes for virtual CAN tunnel pairs (`vxcan`). It is the minimal UAPI used to create and inspect peer links.

## APIs, Control Flow, and State
The header exports an enum with `VXCAN_INFO_UNSPEC`, `VXCAN_INFO_PEER`, and `__VXCAN_INFO_MAX`, plus `VXCAN_INFO_MAX`. There are no structures or functions; rtnetlink creation paths interpret the peer attribute to instantiate linked virtual CAN devices. Persistent state is the netdevice pair and namespace placement, not the header.

## Dependencies, Integration, Risks, and Tests
Integration points are `ip link add type vxcan`, network namespaces, CAN protocol tests that need linked virtual devices, and rtnetlink parsers. Risks are malformed nested peer attributes, namespace cleanup issues, and tooling assuming veth-like attributes beyond the single peer definition. Test signals include vxcan create/delete tests, namespace move tests, frame forwarding between peers, and netlink attribute validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/can/vxcan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/capability.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/capability.h

## Purpose
Defines Linux process and file capability UAPI. It specifies the capget/capset user structures, version constants, file xattr formats, all capability numbers, helper macros for validation and bit indexing, and the current `CAP_LAST_CAP`.

## APIs, Control Flow, and State
The header exports `_LINUX_CAPABILITY_VERSION_{1,2,3}` and word counts, `cap_user_header_t`, `struct __user_cap_data_struct`, file capability revision/size/flag constants, `struct vfs_cap_data`, `struct vfs_ns_cap_data`, and capability numbers from `CAP_CHOWN` through `CAP_CHECKPOINT_RESTORE`. The list covers traditional DAC/UID/GID/network/admin powers plus newer splits such as `CAP_SYSLOG`, `CAP_PERFMON`, `CAP_BPF`, and checkpoint/restore. Macros `cap_valid()`, `CAP_TO_INDEX()`, and `CAP_TO_MASK()` validate and address bitmaps. Runtime control flow is in credential management, LSMs, VFS xattr handling, namespaces, and syscall permission checks; persistent state includes process credentials, bounding/ambient/inheritable/effective/permitted sets, and file capability xattrs.

## Dependencies, Integration, Risks, and Tests
Depends on Linux fixed-width and endian types, and uses `__user` annotations. Integration points are `capget`, `capset`, exec credential calculation, file xattrs, user namespaces, container runtimes, LSM policy, and permission gates throughout the kernel. Risks include adding capabilities without updating `CAP_LAST_CAP`, overloading `CAP_SYS_ADMIN`, namespace-rootid handling for v3 file caps, incompatibility with old libcap/userspace versions, and security regressions when checks use the wrong capability. Test signals include libcap tests, capget/capset ABI tests, file capability xattr round trips across namespaces, container runtime capability sets, LSM integration tests, and targeted permission tests for `CAP_BPF`, `CAP_PERFMON`, and checkpoint/restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/capability.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/cciss_defs.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/cciss_defs.h

## Purpose
Defines legacy HP Smart Array/CCISS command, LUN, request, and error-info structures shared by cciss ioctls. It models CISS command status, transfer direction, queue attributes, command type, SCSI-3 addressing, physical/logical device addressing, and sense/error payloads.

## APIs, Control Flow, and State
The header exports status codes such as `CMD_SUCCESS`, target status, underrun/overrun, invalid, protocol/hardware errors, connection loss, abort, timeout, and unabordable states; transfer direction values; tag attributes; command/message type values; aliases for byte/word/dword types; `CISS_MAX_LUN`; and packed/legacy typedefs for `SCSI3Addr_struct`, `PhysDevAddr_struct`, `LogDevAddr_struct`, `LUNAddr_struct`, `RequestBlock_struct`, `MoreErrInfo_struct`, and `ErrorInfo_struct`. There is no active logic. Driver ioctl paths and hardware command submission code fill these structures, and controller/device state persists in the driver and array firmware.

## Dependencies, Integration, Risks, and Tests
Depends on Linux integer types and legacy cciss ABI conventions. Integration points are `cciss_ioctl.h`, Smart Array management utilities, SCSI passthrough, and logical/physical LUN enumeration. Risks include old structure packing assumptions, endian/addressing quirks for multi-level LUNs, fixed sense buffer size, and ABI compatibility with tools for removed or legacy drivers. Test signals include management-tool passthrough tests, structure-size/compat checks, simulated status/error returns, and regression tests against known Smart Array firmware command formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/cciss_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/cciss_ioctl.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/cciss_ioctl.h

## Purpose
Defines the legacy CCISS userspace ioctl ABI for HP Smart Array controller management. It exposes controller information, interrupt coalescing, node name, heartbeat, bus/firmware/driver versions, passthrough commands, logical-volume info, and disk registration/rescan commands.

## APIs, Control Flow, and State
Important structures include `cciss_pci_info_struct`, `cciss_coalint_struct`, node/heartbeat/bus/firmware/driver typedefs, `IOCTL_Command_struct`, `BIG_IOCTL_Command_struct`, and `LogvolInfo_struct`. Ioctl numbers under `CCISS_IOC_MAGIC` include `CCISS_GETPCIINFO`, `GET/SETINTINFO`, `GET/SETNODENAME`, `GETHEARTBEAT`, `GETBUSTYPES`, `GETFIRMVER`, `GETDRIVVER`, `REVALIDVOLS`, `PASSTHRU`, `DEREGDISK`, `REGNEWDISK`, `REGNEWD`, `RESCANDISK`, `GETLUNINFO`, and `BIG_PASSTHRU`. Control flow is ioctl-dispatch based and may query firmware, submit CISS commands, or mutate logical disk registration. Persistent state includes controller settings, logical volume tables, and firmware command effects.

## Dependencies, Integration, Risks, and Tests
Depends on `linux/ioctl.h`, fixed-width types, and `cciss_defs.h`. Integration points are cciss character/block device management tools and SCSI/CISS passthrough. Risks include arbitrary passthrough command exposure, user buffer length validation, `MAX_KMALLOC_SIZE` assumptions, compat-layout drift, stale logical volume registration, and legacy tool dependence. Test signals include ioctl compat tests, passthrough read/write bounds tests, interrupt coalescing get/set, logical-volume info queries, rescan/register/deregister workflows, and permission checks around raw controller commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/cciss_ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ccs.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ccs.h

## Purpose
Defines UAPI constants for the CCS static-priority scheduler policy. It gives userspace the scheduler policy number and priority range used when requesting this policy through scheduler syscalls.

## APIs, Control Flow, and State
The header defines `SCHED_CCS`, `SCHED_CCS_PRIO_MIN`, and `SCHED_CCS_PRIO_MAX`. There are no structures or functions. Runtime control flow is in scheduler policy validation and scheduling-class code that interprets these constants; per-task scheduling policy and priority are stored in kernel task state.

## Dependencies, Integration, Risks, and Tests
Integration points are `sched_setscheduler`/`sched_getscheduler`, scheduler policy tooling, and any CCS scheduling class implementation. Risks include policy-number collision, userspace using priorities outside the advertised range, and kernels without CCS support rejecting the policy. Test signals include scheduler syscall tests for min/max priority, invalid priority rejection, policy reporting, and runtime scheduling behavior under CCS-enabled configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ccs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/cdrom.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/cdrom.h

## Purpose
Defines the generic Linux CD-ROM, DVD, MMC packet, and media feature UAPI. It standardizes legacy CD audio/data ioctls, drive and disc capability/status constants, sector geometry, generic packet commands, DVD structure/authentication payloads, SCSI request sense layout, and MMC feature descriptors.

## APIs, Control Flow, and State
The header exports ioctl numbers from `CDROMPAUSE` through media-change queries, DVD commands (`DVD_READ_STRUCT`, `DVD_WRITE_STRUCT`, `DVD_AUTH`), generic packet command and writable-location ioctls, and structures for MSF/LBA addresses, audio play ranges, TOC entries, volume, subchannel, data reads, audio reads, multisession info, MCN, block play, `cdrom_generic_command`, and timed media-change info. It also defines sector size constants, address types, audio states, uniform-driver capability and option flags, drive/disc statuses, changer slot values, generic MMC command opcodes, mode page codes, DVD structure/authentication unions, `request_sense`, and feature descriptors for MRW/random writable/disc/track/removable media. Control flow is ioctl and packet-command based: user space requests media/drive operations, drivers translate to SCSI/MMC/ATAPI commands, and status/sense data return through these structs. Persistent state includes drive settings, tray/media state, writable session state, DVD authentication state, and cached media-change timestamps.

## Dependencies, Integration, Risks, and Tests
Depends on Linux types and architecture byteorder bitfield macros. Integration points are sr/scsi-cd, block CD/DVD devices, media players, ripping/burning tools, DVD authentication libraries, udev/media monitors, and generic packet passthrough. Risks include many legacy ioctls with weak type encoding, user pointer validation in read/generic-command structures, bitfield endian layout, command opcode passthrough security, stale media-change state, DVD auth state-machine errors, and inconsistent support across old drive types. Test signals include cdrom ioctl smoke tests with tray/media status, audio/TOC read tests, generic packet request-sense tests, DVD auth/structure tests, media-change timestamp checks, endian layout builds, and fuzzing of buffer lengths and packet commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/cdrom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/cec-funcs.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/cec-funcs.h

## Purpose
Provides inline helper functions and operand structs for building and decoding HDMI CEC messages. It covers One Touch Play, Routing Control, Standby, recording and timer programming, system information, deck and tuner control, vendor commands, OSD/menu/user-control, power, feature abort, system audio, ARC, dynamic audio latency, and CDC/HEC/HPD messages.

## APIs, Control Flow, and State
The header is a large inline encoder/decoder library around `struct cec_msg` from `<linux/cec.h>`. Functions named `cec_msg_*` set `msg->len`, opcode bytes, operands, broadcast destination bits, and expected `msg->reply`; matching `cec_ops_*` functions decode operands from received messages. Helper structs include digital-service identifiers, record sources, tuner-device info, UI commands, and CDC-related operands. Control flow is mostly switch-based operand packing for record sources, digital service IDs, UI optional operands, timer status duration fields, CEC version feature blocks, tuner analog/digital forms, and variable-length CDC/HEC physical-address lists. The header stores no durable state, but it mutates caller-provided `struct cec_msg` buffers; persistent CEC adapter state, logical addresses, pending replies, and topology live in the CEC framework and devices.

## Dependencies, Integration, Risks, and Tests
Depends on the opcode/operand constants and helpers in `linux/cec.h`. Integration points are V4L2 CEC adapters, HDMI device-control daemons, cec-ctl/libcec-style tools, CEC compliance testing, and kernel drivers that emit or parse CEC messages. Risks include caller-provided buffers being too small or not initialized with source/destination nibbles, missing message-length validation before `cec_ops_*` reads operands, BCD time packing accepting invalid values, variable-length string/vendor/audio descriptor truncation, subtle reply-opcode expectations, and protocol bugs in rarely used CDC/HEC helpers. Test signals include CEC compliance suites, encode/decode round trips for every opcode family, fuzzing short `msg->len` inputs, broadcast vs directed address checks, reply expectation tests, and HDMI topology tests for ARC, routing, power, and CDC messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/cec-funcs.h -->
