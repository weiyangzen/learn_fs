# Research: subset-b-009324

Grouped source-tree-aligned research for the listed strace bundled Linux UAPI, CI, build, packaging, and documentation files. Each source file section is delimited for deterministic reconciliation into the mapped per-file document.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/videodev2.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/videodev2.h

## Purpose
Defines the bundled Video4Linux2 userspace ABI used by strace when system kernel headers are older than the bundled snapshot. It supplies ioctl numbers, public structures, enums, fourcc pixel format IDs, capability flags, control/event metadata, buffer queue layouts, analog TV/radio/tuner state, digital-video timing descriptors, SDR/meta/touch formats, and compatibility aliases that strace decoders can compile against consistently.

## Important APIs, Types, and Functions
Read coverage: 2769 lines and 105802 bytes. Foundational helpers are `v4l2_fourcc`, `v4l2_fourcc_be`, `VIDEO_MAX_FRAME`, `VIDEO_MAX_PLANES`, field/type helper macros, and enums for `v4l2_field`, `v4l2_buf_type`, `v4l2_memory`, `v4l2_colorspace`, transfer functions, YCbCr/HSV encodings, quantization, tuner type, and priority. Geometry and capability structures include `v4l2_rect`, `v4l2_fract`, `v4l2_area`, `v4l2_capability`, `v4l2_pix_format`, `v4l2_fmtdesc`, frame-size and interval enumeration structures, `v4l2_format`, multi-planar `v4l2_plane_pix_format`/`v4l2_pix_format_mplane`, `v4l2_sdr_format`, and `v4l2_meta_format`.

The pixel-format catalog is large and includes RGB/BGR, greyscale, packed and planar YUV, multi-planar variants, tiled formats, Bayer RAW and packed Bayer, HSV, JPEG/MJPEG, MPEG/H.26x/VPx/HEVC/AV1/stateless-codec formats, vendor formats, IPU3 and PiSP camera formats, and deprecated aliases such as `V4L2_PIX_FMT_HM12`. Buffer APIs use `v4l2_requestbuffers`, `v4l2_plane`, `v4l2_buffer`, `v4l2_exportbuffer`, `v4l2_create_buffers`, and `v4l2_remove_buffers`, with flags for MMAP/USERPTR/DMABUF support, request fds, cache hints, timestamp source, queued/done/error state, and buffer ownership. Control APIs use `v4l2_control`, `v4l2_ext_control`, `v4l2_ext_controls`, `v4l2_queryctrl`, `v4l2_query_ext_ctrl`, and `v4l2_querymenu`, including compound and dynamic-array controls.

Timing, routing, and legacy media structures include `v4l2_standard`, `v4l2_bt_timings`, `v4l2_dv_timings`, `v4l2_enum_dv_timings`, `v4l2_dv_timings_cap`, `v4l2_input`, `v4l2_output`, `v4l2_tuner`, `v4l2_modulator`, `v4l2_frequency`, `v4l2_frequency_band`, `v4l2_hw_freq_seek`, `v4l2_rds_data`, audio input/output records, encoder/decoder command structures, VBI and sliced VBI records, MPEG VBI payload structures, events, debug register access, and chip matching. The tail defines `VIDIOC_*` ioctl numbers from `VIDIOC_QUERYCAP` through `VIDIOC_REMOVE_BUFS`, plus `BASE_VIDIOC_PRIVATE`.

## Control Flow
There is no executable control flow in the header, but it encodes the V4L2 userspace protocol. A normal capture flow opens a device node, calls `VIDIOC_QUERYCAP`, enumerates inputs and formats, negotiates with `VIDIOC_TRY_FMT` and `VIDIOC_S_FMT`, requests or creates buffers, queries buffers for offsets or dma-buf export, queues buffers with `VIDIOC_QBUF`, starts streaming with `VIDIOC_STREAMON`, waits for readiness, dequeues with `VIDIOC_DQBUF`, requeues, and ends with `VIDIOC_STREAMOFF`. Output and mem2mem codecs use the same queue lifecycle for output/capture queues plus encoder/decoder commands and end-of-stream events. Controls are discovered through query ioctls, read or written through simple and extended control calls, and may be bound to media requests. Analog and digital TV flows select input/output, standard or DV timings, tuner/frequency, audio route, crop/selection, and EDID.

## State and Persistence Behavior
Runtime state lives in the kernel V4L2 device and media graph: active queue formats, selected input/output, streaming state, allocated buffers, mmap or dma-buf mappings, queued/done buffer status, per-file-handle priority, control values, request-bound settings, event subscriptions, tuner/frequency/standard/timing state, and debug register target selection. The header is ABI state rather than persisted storage; its reserved fields, fixed struct layouts, fixed ioctl numbers, deprecated aliases, and compat-sensitive unions are what strace relies on for stable decoding across host systems.

## Dependencies and Integration Points
Direct includes are `<sys/time.h>`, `<linux/ioctl.h>`, `<linux/types.h>`, `<linux/v4l2-common.h>`, and `<linux/v4l2-controls.h>`. Within strace this bundled copy integrates with configure's bundled-header selection and ioctl decoders that need current `VIDIOC_*`, structure, and flag definitions even on older distributions. In the kernel ecosystem it integrates with V4L2 core, vb2 buffer queues, media controller, dma-buf, request API, codec controls, radio/RDS, EDID/DV timing support, libv4l2, libcamera, FFmpeg, GStreamer, browsers, and camera HALs.

## Risks and Edge Cases
This is one of the broadest Linux UAPIs. ABI risks include 32-bit compat layout, `timeval` and pointer-sized fields, multi-planar `length` semantics, reserved fields that must remain zero, vendor fourcc collisions, big-endian fourcc variants, deprecated compatibility aliases, dynamic payload controls, request-fd lifetime, cache maintenance flags, and stateful/stateless codec distinctions. For strace specifically, stale bundled definitions can cause unknown ioctl names or incorrect flag decoding, while using newer structures against older runtime kernels must remain compile-time only and not assume kernel support.

## Test Signals
Good signals include strace ioctl decoder tests for `VIDIOC_*` names and structures, build tests with `--enable-bundled=yes`, cross/compat builds where V4L2 structs contain pointers and time fields, and comparison against system-header builds. Kernel/userland behavioral coverage comes from `v4l2-compliance`, vb2 streaming tests across MMAP/USERPTR/DMABUF, control query/get/set tests including compound controls, event subscription/dequeue tests, tuner/timing/standard tests, and real userspace integration through libcamera/GStreamer/FFmpeg.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/videodev2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/vm_sockets.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/vm_sockets.h

## Purpose
Defines the Linux AF_VSOCK userspace ABI for virtual-machine sockets, including socket options, well-known context IDs, address structure layout, local-CID ioctl, and zerocopy error-queue control-message constants.

## Important APIs, Types, and Functions
Read coverage: 211 lines and 7428 bytes. The header exports `SO_VM_SOCKETS_BUFFER_SIZE`, minimum/maximum buffer socket options, peer host VM ID, trust, nonblocking TX/RX, and old/new connect-timeout option numbers. `SO_VM_SOCKETS_CONNECT_TIMEOUT` is selected with ABI-aware logic based on word size, x32, and `time_t` versus `__kernel_long_t`. Addressing constants include `VMADDR_CID_ANY`, `VMADDR_PORT_ANY`, `VMADDR_CID_HYPERVISOR`, `VMADDR_CID_LOCAL`, `VMADDR_CID_HOST`, and `VMADDR_FLAG_TO_HOST`. Version helpers split epoch, major, and minor from a packed version integer. `struct sockaddr_vm` defines the AF_VSOCK socket address with family, port, CID, flags, and zero padding sized to match `struct sockaddr`. `IOCTL_VM_SOCKETS_GET_LOCAL_CID` returns the local CID. `SOL_VSOCK` and `VSOCK_RECVERR` identify zerocopy completion notifications on the error queue.

## Control Flow
Userspace creates an `AF_VSOCK` socket, optionally adjusts stream-buffer options with `setsockopt`, binds to a CID/port or wildcard address, connects to host, hypervisor, local, or guest CIDs, and can use `VMADDR_FLAG_TO_HOST` to force host forwarding for sibling/nested VM use cases. Code that needs its local address can issue `IOCTL_VM_SOCKETS_GET_LOCAL_CID`. MSG_ZEROCOPY senders receive completion notifications through control messages using `SOL_VSOCK` and `VSOCK_RECVERR`.

## State and Persistence Behavior
No persistent storage is defined. Runtime state is kernel socket state: buffer sizes, connect timeout, trust/nonblocking metadata, selected local and peer CID/port, routing flag, and error-queue notifications. The address struct's fixed size and padding are ABI state that user and kernel code must preserve.

## Dependencies and Integration Points
Direct includes are `<sys/socket.h>`, `<linux/socket.h>`, and `<linux/types.h>`. In strace the constants feed socket option, ioctl, address-family, and control-message decoding. System integration points include VMCI, virtio-vsock, Hyper-V vsock transports, host/guest services, nested VM routing, and zerocopy networking notification handling.

## Risks and Edge Cases
The connect-timeout compatibility macro is time64-sensitive and differs for x32 and 32-bit ABIs. `struct sockaddr_vm` deliberately matches `struct sockaddr`; changing padding or family type would break ABI and strace decoding. CID values use unsigned `-1U` wildcards and low reserved IDs, so decoders must avoid treating them as normal signed negative addresses. `VMADDR_FLAG_TO_HOST` only affects specific routing scenarios, and zerocopy notifications are encoded as standard socket extended errors.

## Test Signals
Compile tests should cover 32-bit, 64-bit, and x32 timeout macro selection. Runtime tests should exercise bind/connect with wildcard, host, local, and hypervisor CIDs, `GET_LOCAL_CID`, buffer option get/set clamping, `VMADDR_FLAG_TO_HOST` routing where supported, zerocopy error-queue messages, and strace output for AF_VSOCK sockaddr and socket options.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/vm_sockets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/xattr.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/xattr.h

## Purpose
Defines Linux extended-attribute userspace constants used by filesystem, security, and strace xattr decoders: set flags, an extensible argument structure, namespace prefixes, and standard security/system attribute names.

## Important APIs, Types, and Functions
Read coverage: 96 lines and 3294 bytes. When `__UAPI_DEF_XATTR` permits kernel definitions, it exports `XATTR_CREATE` and `XATTR_REPLACE` for setxattr-style calls and `struct xattr_args` containing an aligned userspace value pointer, value size, and flags. Namespace prefix macros cover `os2.`, `osx.`, `btrfs.`, `gnu.`, `security.`, `system.`, `trusted.`, and `user.`, with matching length macros. Security names include EVM, IMA, SELinux, SMACK variants, AppArmor, file capabilities, and BPF LSM prefix naming. System ACL names include `system.posix_acl_access` and `system.posix_acl_default`.

## Control Flow
The header has no runtime flow. Userspace passes the flags to `setxattr`/`lsetxattr`/`fsetxattr` or related syscalls, and kernel/filesystem/security code uses the namespace prefixes to route access control and interpretation. `struct xattr_args` is suitable for newer extensible syscall payloads that need a stable pointer/size/flag tuple.

## State and Persistence Behavior
Extended attributes are persisted by filesystems or security subsystems on inodes. This header defines the names and flags that describe those persisted key/value entries; it does not store state itself. Names in `security.*`, `system.*`, `trusted.*`, and `user.*` carry policy-sensitive state such as LSM labels, IMA/EVM metadata, POSIX ACLs, and file capabilities.

## Dependencies and Integration Points
Direct includes are `<linux/libc-compat.h>` and `<linux/types.h>`. The libc-compat guard avoids conflicting definitions when libc supplies the xattr API. In strace this header supports symbolic decoding of xattr flags and well-known names. It integrates with VFS xattr syscalls, filesystems, SELinux, SMACK, AppArmor, IMA/EVM, file capabilities, BPF LSM, POSIX ACLs, and backup/archive tools.

## Risks and Edge Cases
Namespace semantics differ: `trusted.*` requires privilege, `security.*` is LSM-controlled, `system.*` may be filesystem-managed, and `user.*` depends on mount/filesystem policy. Incorrect create/replace flag decoding changes error expectations. `struct xattr_args.value` is an aligned 64-bit user pointer for compat safety, so strace must decode it as an address rather than inline data. Security attribute values may be sensitive.

## Test Signals
Test signals include strace xattr syscall decoding with no flags, `XATTR_CREATE`, `XATTR_REPLACE`, known security/system/user names, 32-bit compat pointer layout for `struct xattr_args`, filesystem round-trips on ext4/xfs/btrfs/tmpfs where supported, and permission/error checks for security and trusted namespaces.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/xattr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/mtd/mtd-abi.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/mtd/mtd-abi.h

## Purpose
Defines the primary Linux Memory Technology Device userspace ABI that strace uses to decode MTD ioctl commands and payloads: flash geometry, erase/OOB/read/write requests, ECC statistics, OTP operations, bad-block management, lock state, file modes, and legacy NAND OOB layouts.

## Important APIs, Types, and Functions
Read coverage: 342 lines and 11876 bytes. Core request structures are `erase_info_user`, `erase_info_user64`, `mtd_oob_buf`, `mtd_oob_buf64`, `mtd_write_req`, `mtd_read_req_ecc_stats`, and `mtd_read_req`. Device descriptions use `mtd_info_user`, `region_info_user`, and `otp_info`. Flash type and capability constants include `MTD_RAM`, `MTD_ROM`, `MTD_NORFLASH`, `MTD_NANDFLASH`, `MTD_DATAFLASH`, `MTD_UBIVOLUME`, `MTD_MLCNANDFLASH`, `MTD_WRITEABLE`, `MTD_BIT_WRITEABLE`, `MTD_NO_ERASE`, `MTD_POWERUP_LOCK`, `MTD_SLC_ON_MLC_EMULATION`, and capability bundles. Operation modes include `MTD_OPS_PLACE_OOB`, `MTD_OPS_AUTO_OOB`, and `MTD_OPS_RAW`; file modes include normal, factory/user OTP, and raw.

Ioctl commands include `MEMGETINFO`, `MEMERASE`, `MEMWRITEOOB`, `MEMREADOOB`, `MEMLOCK`, `MEMUNLOCK`, `MEMGETREGIONCOUNT`, `MEMGETREGIONINFO`, `MEMGETOOBSEL`, `MEMGETBADBLOCK`, `MEMSETBADBLOCK`, `OTPSELECT`, `OTPGETREGIONCOUNT`, `OTPGETREGIONINFO`, `OTPLOCK`, `ECCGETLAYOUT`, `ECCGETSTATS`, `MTDFILEMODE`, `MEMERASE64`, `MEMWRITEOOB64`, `MEMREADOOB64`, `MEMISLOCKED`, `MEMWRITE`, `OTPERASE`, and `MEMREAD`. Legacy compatibility structures include `nand_oobinfo`, `nand_oobfree`, `nand_ecclayout_user`, and `mtd_ecc_stats`. The inline helper `mtd_type_is_nand_user` identifies SLC and MLC NAND types.

## Control Flow
Userspace opens an MTD character device, queries geometry with `MEMGETINFO`, optionally discovers erase regions, OOB layout, and ECC stats, then performs erase, read, write, OOB, lock/unlock, OTP, or bad-block operations. Newer generic `MEMREAD` and `MEMWRITE` carry data and OOB userspace addresses plus an operation mode, while older OOB calls use 32-bit or 64-bit OOB buffer descriptors. File mode can be set per descriptor to raw or OTP behavior and affects read/write paths that cannot carry per-operation mode.

## State and Persistence Behavior
The header itself is stateless, but its ioctls mutate persistent flash contents, OOB areas, bad-block tables, OTP regions and locks, erase state, and chip lock state. `mtd_info_user`, `region_info_user`, and ECC structures snapshot kernel device state. File mode is per-open-file-descriptor runtime state. ECC counters and bad-block state are persistent or device-maintained signals that strace can reveal through decoded ioctl payloads.

## Dependencies and Integration Points
Direct include is `<linux/types.h>`. In strace this bundled header integrates with ioctl number tables and structure decoders for MTD tools. Kernel ecosystem integration includes `/dev/mtd*` character devices, NAND/NOR/dataflash drivers, nandsim/mtdram, mtd-utils, UBI attachment, flash filesystems, bootloaders, and manufacturing or recovery tools.

## Risks and Edge Cases
Flash operations can be destructive: erase, raw write, OTP lock, OTP erase, and bad-block marking are high-risk. ABI compatibility risks include legacy 32-bit offsets versus 64-bit offsets, userspace pointers in old structures, only lower 32 bits of `len`/`ooblen` being used in generic requests, reserved padding that must be zero, deprecated OOB/ECC layout truncation, raw mode bypassing ECC, and loff_t compat for bad-block ioctls. Strace decoders must avoid assuming a specific flash geometry and must treat user pointers as addresses.

## Test Signals
Use strace tests for every `MEM*`, `OTP*`, and `ECC*` ioctl name and representative payload formatting, including compat layouts. Behavioral tests can run mtd-utils on nandsim/mtdram, covering query, erase, OOB read/write, generic read/write with ECC stats, raw mode, OTP paths where emulated, bad-block get/set, lock state, and UBI attach after MTD operations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/mtd/mtd-abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/mtd/ubi-user.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/mtd/ubi-user.h

## Purpose
Defines the UBI userspace ioctl ABI for attaching/detaching MTD devices, managing UBI volumes, querying erase counters, performing volume updates, changing logical eraseblocks, setting volume properties, and creating or removing read-only ubiblock devices.

## Important APIs, Types, and Functions
Read coverage: 506 lines and 19974 bytes. Constants include `UBI_VOL_NUM_AUTO`, `UBI_DEV_NUM_AUTO`, `UBI_MAX_VOLUME_NAME`, `MAX_UBI_MTD_NAME_LEN`, `UBI_MAX_RNVOL`, UBI device/volume ioctl magic values, `UBI_DYNAMIC_VOLUME`, `UBI_STATIC_VOLUME`, `UBI_VOL_PROP_DIRECT_WRITE`, `UBI_VOL_SKIP_CRC_CHECK_FLG`, and `UBI_VOL_VALID_FLGS`. Control-device ioctls are `UBI_IOCATT` and `UBI_IOCDET`; UBI device ioctls are `UBI_IOCMKVOL`, `UBI_IOCRMVOL`, `UBI_IOCRSVOL`, `UBI_IOCRNVOL`, `UBI_IOCRPEB`, `UBI_IOCSPEB`, and `UBI_IOCECNFO`; volume ioctls are `UBI_IOCVOLUP`, `UBI_IOCEBER`, `UBI_IOCEBCH`, `UBI_IOCEBMAP`, `UBI_IOCEBUNMAP`, `UBI_IOCEBISMAP`, `UBI_IOCSETVOLPROP`, `UBI_IOCVOLCRBLK`, and `UBI_IOCVOLRMBLK`.

Structures are `ubi_attach_req`, `ubi_mkvol_req`, `ubi_rsvol_req`, `ubi_rnvol_req`, `ubi_ecinfo_req` with flexible erase-counter array, `ubi_leb_change_req`, `ubi_map_req`, `ubi_set_vol_prop_req`, and `ubi_blkcreate_req`. Many are packed and contain reserved padding that callers must zero.

## Control Flow
UBI control-device flow attaches an MTD device with `UBI_IOCATT` and detaches with `UBI_IOCDET`. UBI device flow creates, removes, resizes, and atomically renames volumes, scrubs PEBs, and reads erase counters. Volume-device flow starts a full-volume update by declaring image size with `UBI_IOCVOLUP` and then writing exactly that many bytes, performs atomic LEB change with a similar write-after-ioctl sequence, maps or unmaps LEBs, checks mapping state, sets direct-write property, and creates/removes a read-only block device.

## State and Persistence Behavior
UBI operations mutate persistent flash metadata: attached device identity, volume table entries, volume names and IDs, volume sizes and types, static-volume CRC policy, logical-to-physical eraseblock mappings, erase counters, update transactions, and ubiblock exposure. Some operations are explicitly transactional, especially atomic volume rename and atomic LEB change. `UBI_IOCEBUNMAP` is asynchronous with respect to physical erase completion, so an unclean reboot can leave the LEB mapped again.

## Dependencies and Integration Points
Direct include is `<linux/types.h>`. In strace it supports symbolic decoding of UBI ioctl calls and packed request payloads. Kernel and userspace integration points include MTD devices, UBI core, UBIFS, ubiblock, ubiattach/ubidetach/ubimkvol/ubirmvol/ubirsvol/ubirename/ubiupdatevol/ubinfo, boot-time volume handling, and NAND wear-leveling/scrubbing.

## Risks and Edge Cases
Risks include destructive attach/detach and volume changes, power-cut behavior, packed ABI layout, fixed maximum names and rename count, zeroing padding for forward compatibility, `UBI_IOCVOLUP` taking a pointer to `__s64` despite ioctl encoding constraints on 32-bit systems, obsolete `dtype` fields that should be set to 3 for old kernels, autoreserved bad-block pool settings, fastmap disable semantics, skip-CRC use only when another integrity mechanism exists, and flexible-array erase-counter allocation sizing.

## Test Signals
Strace tests should cover all UBI ioctl names and request structures, including packed fields and flexible `ubi_ecinfo_req` output. Behavioral signals include nandsim-based attach/detach, create/remove/resize, atomic multi-volume rename with power-cut simulation, interrupted volume update, LEB map/unmap/change/is-mapped, erase-counter reads with bad/unknown blocks, direct-write property setting, scrub requests, and ubiblock create/remove.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/mtd/ubi-user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/rdma/ib_user_verbs.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/rdma/ib_user_verbs.h

## Purpose
Defines the legacy write-based RDMA uverbs ABI used by libibverbs and kernel RDMA providers, giving strace stable command numbers, command headers, object lifecycle payloads, work request layouts, flow steering specs, completion event descriptors, extended query responses, and device capability flags.

## Important APIs, Types, and Functions
Read coverage: 1380 lines and 29479 bytes. Global constants include `IB_USER_VERBS_ABI_VERSION`, `IB_USER_VERBS_CMD_THRESHOLD`, `IB_USER_VERBS_CMD_COMMAND_MASK`, `IB_USER_VERBS_CMD_FLAG_EXTENDED`, `IB_USER_VERBS_MAX_LOG_IND_TBL_SIZE`, and `IB_DEVICE_NAME_MAX`. `enum ib_uverbs_write_cmds` enumerates command IDs for context/device/port/GID/P_Key query, PD/MR/MW/CQ/QP/AH/SRQ lifecycle, posting send/receive work, multicast attach/detach, flow create/destroy, extended CQ/QP/device operations, WQ and RWQ indirection table commands, and CQ modification. Header and event structures include `ib_uverbs_cmd_hdr`, `ib_uverbs_ex_cmd_hdr`, `ib_uverbs_async_event_desc`, `ib_uverbs_comp_event_desc`, and `ib_uverbs_cq_moderation_caps`.

Object and query payloads include `ib_uverbs_get_context`, `ib_uverbs_query_device`, extended query structs and ODP/RSS/tag-matching caps, `ib_uverbs_query_port`, PD allocation/deallocation, XRCD open/close, MR register/reregister/deregister, MW allocation/deallocation, completion channel/CQ create/resize/poll/notify/destroy, QP create/open/query/modify/destroy, AH create/destroy, SRQ create/modify/query/destroy, WQ create/modify/destroy, RWQ indirection table create/destroy, and CQ moderation. Data-path structures include `ib_uverbs_sge`, send and receive work requests, work-completion opcodes, QP attributes/destinations, global route and AH attributes, and post-send/recv response bad-WR reporting. Flow steering structures include Ethernet, IPv4, IPv6, TCP/UDP, tunnel, ESP, GRE, MPLS, action tag/drop/handle/count specs, plus `ib_uverbs_flow_attr`. Capability enums cover ODP, raw-packet capabilities, placement/selectivity levels, and device capability flags.

## Control Flow
Userspace opens an RDMA uverbs device and writes command headers plus command-specific payloads. A typical flow gets a context, queries device and port capability, allocates a protection domain, registers memory, creates completion queues and queue pairs, moves QPs through modify/query states, posts send/receive work requests, polls or arms CQs, and eventually destroys objects in dependency order. More advanced flows create address handles, shared receive queues, work queues, receive indirection tables, flow steering rules, multicast memberships, XRC domains, and use extended command headers for newer object features.

## State and Persistence Behavior
State is kernel RDMA object state scoped to a uverbs file/context and hardware provider: contexts, PDs, MRs, memory windows, completion channels, CQs, QPs, AHs, SRQs, WQs, multicast memberships, flow rules, and indirection tables. Work requests and completions are transient queue entries, while handles, keys, queue numbers, and capability responses are runtime state visible to userspace. There is no durable on-disk state, but resources map to pinned memory, DMA keys, device queues, and provider hardware state until destroyed or the file is closed.

## Dependencies and Integration Points
Direct include is `<linux/types.h>`. In strace it supports decoding write-based uverbs command payloads independently of host RDMA header freshness. It integrates with `/dev/infiniband/uverbs*`, rdma-core/libibverbs, provider libraries, InfiniBand/RoCE/iWARP hardware drivers, memory registration and pinning, CQ event file descriptors, multicast, flow steering, and the newer ioctl-based RDMA uAPI that coexists with this legacy path.

## Risks and Edge Cases
The ABI is broad and compatibility-sensitive. Risks include 32/64-bit pointer encoding through `__u64` addresses, structure alignment and reserved fields, extended command flag parsing, provider-specific command data appended after generic payloads, bad-WR index reporting, flow-spec length validation, object lifetime ordering, stale capability bits retained for old kernels, ODP and RSS capability interpretation, and security-sensitive MR registration/pinning. Strace must decode without assuming provider-private payload shape beyond the generic structs.

## Test Signals
Strace tests should cover write command numbers, command headers, extended command flag decoding, representative create/query/modify/destroy payloads, post-send/recv bad-WR output, flow specs, and compat pointer fields. Runtime signals include rdma-core verbs tests on software or hardware providers, 32-bit userspace compat runs, MR registration/reregistration edge cases, CQ event and poll paths, QP state transitions, multicast attach/detach, flow steering filters, WQ/RSS objects, and ABI size/layout checks.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/rdma/ib_user_verbs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/ci/install-dependencies.sh -->
# sources/test-tools/strace/ci/install-dependencies.sh

## Purpose
Installs CI build dependencies for strace across compiler, architecture, kernel-header, libc, stacktrace, and validation matrix variants. It prepares Ubuntu/Debian runners for the later build-and-test script.

## Important APIs, Types, and Functions
Read coverage: 150 lines and 2792 bytes. Important shell variables include `TARGET`, `CC`, `KHEADERS`, `KBRANCH`, `STACKTRACE`, `CHECK`, `j`, `sudo`, `common_packages`, `packages`, `KHEADERS_INC`, and `git_installed`. Helper functions are `retry_if_failed`, which retries a command up to 100 times with one-second sleeps, `apt_get_install`, which lazily runs `apt-get update` once before installing without recommends/suggests, and `clone_repo`, which ensures git/CA certificates, resolves relative GitHub-style repository names using the current remote origin, and shallow-clones an optional branch.

## Control Flow
The script starts with `sh -ex`, detects parallelism with `nproc`, and conditionally uses `sudo`. It selects package sets based on `TARGET`: cross armhf tooling for aarch64 compat, `gcc-multilib` for x86/x32/x86_64/s390x, or plain gcc otherwise. If `CC` names a GCC version, it enables the Ubuntu toolchain PPA and installs target-specific compiler packages; clang installs the selected clang package; other compilers use the default package set. If `KHEADERS` looks like an owner/repo path, it clones that kernel tree, installs headers into `/opt/kernel`, removes the clone, and records `/opt/kernel/include`; otherwise it uses `/usr/include`.

For `CC=musl-gcc`, it clones strace's musl fork, configures/builds/installs musl into `/opt/musl`, adjusts target flags for x32 or x86, removes the clone, and symlinks kernel header directories into musl's include directory. `STACKTRACE=libdw` or `libunwind` installs corresponding development packages plus libiberty. `CHECK=valgrind` installs valgrind. Finally, if `/dev/kvm` exists, it chmods it world-readable/writable for CI tests.

## State and Persistence Behavior
The script mutates the CI host by installing apt packages, possibly adding a PPA, cloning and deleting temporary repositories, installing kernel headers under `/opt/kernel`, installing musl under `/opt/musl`, creating symlinks into `/opt/musl/include`, and changing `/dev/kvm` permissions. State is intentionally outside the source tree except temporary `kernel` and `musl` directories that are removed.

## Dependencies and Integration Points
Depends on POSIX shell, apt, optional sudo, nproc, add-apt-repository, git, make, kernel `headers_install`, rsync for custom headers, and Ubuntu package naming. It integrates with the CI environment variables consumed by `ci/run-build-and-tests.sh`, with strace's cross/personality build matrix, with custom kernel header testing, stacktrace backends, valgrind runs, and KVM-dependent tests.

## Risks and Edge Cases
The retry loop masks transient apt/network failures but can delay real failures for about 100 seconds per command. Relative repository URL rewriting assumes the current git remote has a GitHub-like path. Adding the toolchain PPA is Ubuntu-specific. Musl setup symlinks kernel header directories and may conflict if paths already exist. `/dev/kvm` chmod is privileged and intentionally broad for CI. Cross packages are tailored to known matrix targets rather than arbitrary architectures.

## Test Signals
Run the script in CI containers for default gcc, versioned gcc, clang, musl-gcc, custom `KHEADERS`, stacktrace variants, and valgrind. Verify installed compiler commands, `/opt/kernel/include` content for custom headers, `/opt/musl` for musl builds, no leftover `kernel` or `musl` directories, retry behavior on transient apt failures, and successful handoff to `run-build-and-tests.sh`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/ci/install-dependencies.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/ci/run-build-and-tests.sh -->
# sources/test-tools/strace/ci/run-build-and-tests.sh

## Purpose
Runs the strace CI build, configure, and test workflow after dependencies are installed. It applies matrix-specific compiler flags, stacktrace/check options, custom kernel headers, diagnostics, bootstrap/configure, normal or coverage/valgrind/distcheck test modes, and a final source-tree cleanliness check.

## Important APIs, Types, and Functions
Read coverage: 120 lines and 2935 bytes. Key variables include `DISTCHECK_CONFIGURE_FLAGS`, `CC`, `TARGET`, `STACKTRACE`, `KHEADERS`, `CHECK`, `CPPFLAGS`, `VERBOSE`, `VALGRIND_TOOLS`, `VALGRIND_TESTDIR`, `CC_FOR_BUILD`, `nproc`, `j`, and `j2`. It sets configure cache variables such as `st_cv_mx32_runtime=no` for clang x32 and coverage-tool cache variables for lcov/genhtml. Major commands are `git-set-file-times`, `bootstrap`, `configure`, `make all`, `make check`, `make check-valgrind-*`, `make distcheck`, log tailing, and `git status --porcelain`.

## Control Flow
The script exports default distcheck flags `--disable-dependency-tracking --enable-gcc-Werror`, adjusts clang x32 runtime detection, appends `-mx32` or `-m32` target flags, and adds configure options for stacktrace enable/disable. Custom kernel headers set `CPPFLAGS=-isystem /opt/kernel/include`. Coverage mode enables code coverage and supplies lcov/genhtml cache hits; valgrind mode enables valgrind. It prints environment diagnostics including uname, libc, shell file type, compiler version, multilibs, make/autoconf/automake versions, and kernel header version computed by preprocessing `<linux/version.h>`.

It exports `CC_FOR_BUILD`, normalizes file times, bootstraps autotools, and runs `./configure --enable-maintainer-mode` with the accumulated flags. On configure failure it dumps `config.log` and compiler specs before exiting. Coverage builds all with debug/`-Og`, runs checks, and tails test logs. Valgrind builds, runs selected valgrind test targets, tails logs, and preserves failure status. Default mode runs `make distcheck`. The final guard fails if git status shows source-tree changes.

## State and Persistence Behavior
Build outputs, generated autotools files, configured Makefiles, test logs, coverage files, valgrind logs, and distribution tarball artifacts are created in the working tree as part of the build. The final cleanliness guard requires the build system and tests to clean up after themselves for successful CI. Environment-variable exports persist only within the script process and child commands.

## Dependencies and Integration Points
Depends on POSIX shell, compiler toolchains, make, autoconf/automake, ldd, file, git, bootstrap prerequisites, optional lcov/genhtml, optional valgrind, optional custom kernel headers, and strace's generated autotools build. It integrates with `install-dependencies.sh`, `configure.ac` options, test-suite log files, ksysent generation logs, maintainer mode, mpers/cross targets, and CI failure diagnostics.

## Risks and Edge Cases
`ldd /bin/sh` parsing may fail for static or unusual shells, but the script mainly uses it for diagnostics. Kernel header version preprocessing assumes `LINUX_VERSION_CODE` is available. `make -k` preserves more failures but requires careful rc handling; valgrind mode captures failures across tools. The final git-clean check can fail if generated files or tests leave nondeterministic artifacts. x32 clang is forced off through a cache variable because the runtime probe is known to fail.

## Test Signals
Exercise default distcheck, coverage, valgrind, x86 `-m32`, x32, clang, stacktrace libdw/libunwind/no, and custom kernel-header modes. Confirm configure failure diagnostics include `config.log` and dumpspecs, test-suite logs are tailed on failures, coverage and valgrind flags reach configure, final git cleanliness catches generated drift, and output contains the expected environment information block.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/ci/run-build-and-tests.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/configure.ac -->
# sources/test-tools/strace/configure.ac

## Purpose
Defines strace's Autoconf/Automake configuration logic. It establishes package metadata, supported architectures and personalities, bundled-header selection, compiler/build tools, feature probes, libc/kernel compatibility shims, optional stacktrace/SELinux/coverage/valgrind/install-test features, mpers support, generated outputs, and substitution variables consumed by the build and packaging system.

## Important APIs, Types, and Functions
Read coverage: 827 lines and 22534 bytes. Top-level macros include `AC_PREREQ`, `AC_INIT`, `AC_CONFIG_SRCDIR`, `AC_CONFIG_AUX_DIR`, `AC_CONFIG_HEADERS`, `AM_INIT_AUTOMAKE`, `AM_MAINTAINER_MODE`, `AC_CANONICAL_HOST`, compiler/tool probes, `AC_USE_SYSTEM_EXTENSIONS`, and `AX_CODE_COVERAGE`. It computes version, copyright year, manpage dates, and bundled Linux version through build-aux scripts and substitutes `RPM_CHANGELOGTIME`, `DEB_CHANGELOGTIME`, `COPYRIGHT_YEAR`, `STRACE_MANPAGE_DATE`, and `SLM_MANPAGE_DATE`.

The architecture case maps host CPUs to strace `arch`, kernel `karch`, m32/mx32 personalities, compiler flags, and `AC_DEFINE`s for AARCH64, ALPHA, ARC, ARM, HPPA, I386, LOONGARCH64, MIPS, POWERPC variants, RISCV64, S390X, SPARC, X32, X86_64, and others. Options include `--enable-bundled`, `--enable-arm-oabi`, `--enable-mpers`, and `--enable-install-tests`. Feature probes cover functions, types, headers, struct members, declarations, sizes, signal constants, builtins, library search results for dl/rt/m/termcap, readelf, stacktrace, SELinux, valgrind, and many Linux header structures used by decoders.

## Control Flow
Configure first initializes package metadata and tools, then determines endian and architecture. It validates supported host CPU, sets architecture variables and defaults, decides whether bundled kernel headers are needed by comparing system `<linux/version.h>` against the bundled version, and amends `CPPFLAGS` if bundled headers are selected. MIPS ABI and ARM OABI options are resolved next. The script then probes C functions, types, members, headers, and declarations, creating fallback generated headers for missing `struct sockaddr_storage` or incompatible `<linux/signal.h>` combinations.

Later flow computes ABI sizes and signal constants, probes compiler/library features, runs project-specific macros such as `st_CHECK_ENUMS`, `st_STACKTRACE`, and `st_SELINUX`, generates MIPS syscallent stubs when needed, discovers aarch64 compat compilers, sets default m32/mx32 compiler variables, invokes `st_MPERS` for supported secondary personalities, configures optional installed tests and valgrind defaults, declares generated files, and emits `AC_OUTPUT`.

## State and Persistence Behavior
Configure writes `src/config.h`, generated Makefiles, `debian/changelog`, `doc/strace.1`, `doc/strace-log-merge.1`, `strace.spec`, cache variables, and in some compatibility paths generated headers or MIPS syscall stubs under the build tree. It persists selected architecture, feature availability, library flags, header choices, mpers settings, and manpage/package substitutions into generated build artifacts rather than runtime state.

## Dependencies and Integration Points
Depends on Autoconf, Automake, project m4 macros, build-aux scripts, C compiler/preprocessor/linker, system and bundled Linux headers, optional cross compilers, optional libraries (`dl`, `rt`, `m`, termcap/ncurses/tinfo, stacktrace providers, SELinux), and valgrind/code coverage macros. It integrates with `ci/run-build-and-tests.sh`, `debian/rules`, bundled Linux UAPI headers, `src/config.h` conditional compilation, generated syscall tables, manpage templates including `strace-log-merge.1.in`, RPM/Debian packaging, tests and tests-m32/tests-mx32 directories.

## Risks and Edge Cases
Architecture detection is central; wrong `arch`/`karch` mapping affects syscall tables and bundled include paths. Bundled-header selection compares only version granularity and can differ from vendor-patched system headers. Probes that temporarily modify `CPPFLAGS` must restore it correctly. Missing or incompatible Linux/libc headers trigger fallback copies that can shadow system headers. Cross and mpers builds depend on compiler availability and ABI flags. Generated MIPS stubs can fail when `no_create` is not set. Library probes save/restore `LIBS` to avoid contaminating later checks. Cache variables supplied by CI can force paths that need validation.

## Test Signals
Run `./bootstrap && ./configure` across supported native and cross-like targets, with `--enable-bundled=yes/no/check`, `--enable-mpers` variants, `--enable-arm-oabi`, stacktrace backends, SELinux present/absent, coverage, valgrind, install-tests, and old/new kernel headers. Verify generated `src/config.h`, architecture substitutions, Makefile conditionals, bundled include flags, MIPS stubs, manpage date substitutions, Debian changelog substitution, and full `make distcheck` plus mpers tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/configure.ac -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/debian/changelog.in -->
# sources/test-tools/strace/debian/changelog.in

## Purpose
Provides the Autoconf-substituted Debian changelog template for strace packaging. The top entry is generated for the current snapshot, followed by historical Debian package changelog records from recent 7.x releases back through early strace Debian packaging.

## Important APIs, Types, and Functions
Read coverage: 1244 lines and 38694 bytes. The template uses substitution tokens `@PACKAGE_VERSION@`, `@PACKAGE_STRING@`, `@PACKAGE_BUGREPORT@`, and `@DEB_CHANGELOGTIME@` in the first `experimental` entry. Historical entries record upstream versions, Debian revisions, urgency, maintainers, uploaders, bug closure references, and notable packaging/build changes. There are no functions; the file is a Debian policy-format data source consumed by configure and packaging tools.

## Control Flow
During configure, `AC_CONFIG_FILES([debian/changelog])` substitutes package metadata and the generated RFC-2822 changelog timestamp into this template. Debian packaging tools then consume the resulting `debian/changelog` to determine source package version, distribution, urgency, maintainer signature, and release history for `dh_installchangelogs`, source package construction, and archive metadata.

## State and Persistence Behavior
The generated `debian/changelog` is persistent packaging metadata in the build tree. It records release history and current snapshot identity but does not affect strace runtime behavior. The top generated stanza changes with package version and configure time, while historical records are static and source-controlled in the template.

## Dependencies and Integration Points
Depends on Autoconf substitution from `configure.ac` and Debian packaging tools that parse changelog format. It integrates with `debian/rules`, `dh_installchangelogs`, source package versioning, release snapshots, maintainer workflows, and downstream bug tracking references in historical entries.

## Risks and Edge Cases
Malformed changelog syntax can break Debian package builds. Incorrect substitution values can produce wrong package versions, maintainer contact, or timestamps. The generated top entry targets `experimental`, so release packaging must intentionally adjust if a different distribution is needed. Very old historical entries include legacy formatting and bug references; changes should avoid disturbing parseable Debian changelog structure.

## Test Signals
Run configure and verify `debian/changelog` is generated with the expected current package version, package string, bug-report address, and timestamp. Run `dpkg-parsechangelog` and a Debian package build to validate syntax, check `dh_installchangelogs` output, and confirm the top generated entry matches release expectations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/debian/changelog.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/debian/rules -->
# sources/test-tools/strace/debian/rules

## Purpose
Defines the Debian package build recipe for strace. It bootstraps autotools, configures normal, udeb, and selected 64-bit builds, applies Debian hardening/build flags, runs tests unless disabled, and drives debhelper install/package targets.

## Important APIs, Types, and Functions
Read coverage: 103 lines and 2494 bytes. Key make variables are `DEB_BUILD_MAINT_OPTIONS=hardening=+all`, `DPKG_EXPORT_BUILDFLAGS=1`, included `buildflags.mk` and `architecture.mk`, `CFLAGS`, `DEB_BUILD_OPTIONS`, `NUMJOBS`, `MAKEFLAGS`, `extra_build_targets`, `arch64_map`, `HOST64`, `CC64`, and `CONFIG_OPTS`. Targets include `all`, `build`, `build-arch`, `build-indep`, `configure`, pattern `%-stamp`, `build/Makefile`, `build-udeb/Makefile`, `build64/Makefile`, `clean`, `binary`, `binary-indep`, and `binary-arch`.

## Control Flow
The rules file enables hardening and dpkg build flags, adds `-Wall -g`, selects `-O0` for `noopt` or `-O2` otherwise, and honors `DEB_BUILD_OPTIONS=parallel=N`. It always adds a udeb build target and conditionally adds a 64-bit build for i386, powerpc, sparc, and s390 hosts. `CONFIG_OPTS` uses `--build` alone for native builds or adds `--host` for cross builds. The `configure` target runs `./bootstrap`. Each build directory is configured with `--enable-mpers=check --prefix=/usr`, with udeb disabling stacktrace/libiberty and build64 using `gcc -m64`.

The stamp rule builds the directory, runs `src/strace -V` and `make check VERBOSE=1` unless `nocheck` is set, then touches the stamp. `binary-arch` ensures build completion, renames the 64-bit binary/manpage to `strace64` when present, and runs debhelper commands from directory creation through builddeb. `clean` removes build directories and generated substvars before `dh_clean`.

## State and Persistence Behavior
Creates build directories `build`, `build-udeb`, and optionally `build64`, stamp files, generated configure outputs, test artifacts, binary/manpage rename artifacts for strace64, Debian substvars, and final package staging under `debian/`. Clean removes the main build artifacts and leaves source-controlled packaging files intact.

## Dependencies and Integration Points
Depends on GNU make, dpkg build flags and architecture makefiles, gcc, bootstrap/configure from this source tree, debhelper commands, and strace's test suite. It integrates with `configure.ac`, generated `debian/changelog`, Debian control/install/manpage files, udeb packaging for installer debugging, multiarch/biarch strace64 support, and Debian build option conventions.

## Risks and Edge Cases
Parallelism is manually translated into `MAKEFLAGS`; recursive make behavior should be checked. 64-bit companion builds only trigger for mapped 32-bit host architectures. Tests are skipped under `nocheck`, so package quality then depends on external CI. Renaming `strace` and `strace.1` in build64 must match install file expectations. Cross builds rely on `DEB_HOST_GNU_TYPE` and compiler availability. Udeb intentionally disables stacktrace and libiberty, so feature differences are expected.

## Test Signals
Run `debian/rules clean`, `build`, and `binary-arch` with and without `nocheck`, with `parallel=N`, and on mapped biarch hosts if available. Validate hardening flags, normal and udeb configure options, optional `strace64` artifacts, test execution through `src/strace -V` and `make check VERBOSE=1`, debhelper staging, and successful package lint/build parsing.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/debian/rules -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/doc/strace-log-merge.1.in -->
# sources/test-tools/strace/doc/strace-log-merge.1.in

## Purpose
Provides the generated manpage template for `strace-log-merge`, documenting the helper that merges `strace -ff -tt[t]` per-process logs by prepending PIDs and sorting lines chronologically.

## Important APIs, Types, and Functions
Read coverage: 131 lines and 3409 bytes. The roff template defines an `.OR` macro for required options, a `.TH` header using `@SLM_MANPAGE_DATE@` and `@VERSION@`, and sections for NAME, SYNOPSIS, DESCRIPTION, OPTIONS, EXIT STATUS, USAGE EXAMPLE, NOTES, BUGS, HISTORY, REPORTING BUGS, and SEE ALSO. User-facing interface items are `strace-log-merge STRACE_LOG` and `strace-log-merge --help`. The documented input pattern is `STRACE_LOG.*`.

## Control Flow
There is no executable logic, but the documentation describes operational flow: run strace with `-o prefix -ff -tt` or `-ttt`, invoke `strace-log-merge prefix`, read all matching per-PID files, prepend PID to each line, and sort combined output by timestamp. The usage example traces several sleeps, folds output, and shows merged `execve`, `nanosleep`, exit, and `SIGCHLD` lines.

## State and Persistence Behavior
The template is transformed by configure into `doc/strace-log-merge.1` with the current manpage date and package version. The utility documented by the manpage reads log files but does not persist merged output unless the caller redirects it. Documentation notes that input files are assumed to be correctly formatted logs from one strace session.

## Dependencies and Integration Points
Depends on roff/man macro processing and Autoconf substitution from `configure.ac`. It integrates with the `src/strace-log-merge` utility, `doc/strace.1`, packaging manpage installation, strace's `-ff`, `-tt`, and `-ttt` options, and bug-reporting via the strace mailing list.

## Risks and Edge Cases
The NOTES section documents a key sorting risk: `-tt` timestamps lack dates, so logs spanning midnight may sort incorrectly; `-ttt` avoids that by including date-capable timestamps. The BUGS section states the utility does not validate input format and assumes all `STRACE_LOG.*` files belong to one correctly formatted session. Glob overmatch, mixed sessions, malformed logs, locale-sensitive sorting, or timestamps without enough precision are practical edge cases.

## Test Signals
Validate `configure` substitutes date and version, `man`/`mandoc` can parse the generated page, `strace-log-merge --help` matches documented synopsis, examples work against actual `strace -ff -tt` logs, `-ttt` logs sort across midnight or date boundaries, and malformed or mixed-prefix inputs produce documented non-zero/error behavior where applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/doc/strace-log-merge.1.in -->
