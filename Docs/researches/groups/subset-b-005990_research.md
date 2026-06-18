# Research: subset-b-005990

Grouped research for Linux UAPI headers under `sources/distributed-fs/ceph-client/include/uapi/linux`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/npcm-video.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/npcm-video.h

Purpose: Defines the userspace V4L2 control ABI for the Nuvoton NPCM video capture/differentiation engine.

Important APIs/types/functions: Exports `V4L2_CID_NPCM_CAPTURE_MODE`, `enum v4l2_npcm_capture_mode`, `V4L2_NPCM_CAPTURE_MODE_COMPLETE`, `V4L2_NPCM_CAPTURE_MODE_DIFF`, and `V4L2_CID_NPCM_RECT_COUNT`. The controls are based on `V4L2_CID_USER_NPCM_BASE` from `<linux/v4l2-controls.h>`.

Control flow: This header has no executable flow. Userspace sets the capture mode control through V4L2 ioctls; the driver interprets complete mode as capture of a full frame and diff mode as comparison against the previous in-memory frame. Userspace reads the rectangle count control to learn how many HEXTILE rectangles the compressed result contains.

State and persistence behavior: The header defines only ABI constants. Runtime state lives in the NPCM V4L2 driver and hardware frame buffers; complete mode normally reports one rectangle, while diff mode reports the current differentiated frame rectangle count.

Dependencies and integration points: Integrates with V4L2 control enumeration, `v4l2-ctl`, media userspace, and the NPCM driver documentation referenced by the comments. It is not Ceph-specific; this source tree vendors the Linux kernel UAPI set.

Risks: Control ID drift would break userspace control discovery. Incorrect mode handling can make userspace interpret full-frame output as differential rectangles or vice versa. Rectangle count must be synchronized with the frame returned by the driver.

Test signals: Compile UAPI consumers, enumerate controls via V4L2, set both capture modes, capture complete and diff frames, and verify rectangle counts and HEXTILE output match driver documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/npcm-video.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nsfs.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/nsfs.h

Purpose: Defines ioctl and structure ABI for namespace file descriptors exposed by nsfs, including namespace discovery, owner lookup, PID translation, mount namespace iteration, and stable namespace IDs.

Important APIs/types/functions: Exports `NSIO`, `NS_GET_USERNS`, `NS_GET_PARENT`, `NS_GET_NSTYPE`, `NS_GET_OWNER_UID`, PID/TGID translation ioctls, `NS_MNT_GET_INFO`, `NS_MNT_GET_NEXT`, `NS_MNT_GET_PREV`, `NS_GET_MNTNS_ID`, and `NS_GET_ID`. Important layouts are `struct mnt_ns_info`, `struct nsfs_file_handle`, and `struct ns_id_req`, with version-size macros such as `MNT_NS_INFO_SIZE_VER0`, `NSFS_FILE_HANDLE_SIZE_VER0`, and `NS_ID_REQ_SIZE_VER0`. Enums define initial namespace inode numbers, initial namespace IDs, and `enum ns_type` bit masks matching `CLONE_NEW*` values.

Control flow: Userspace opens a namespace fd, then issues ioctls to derive related namespace fds, query namespace type/owner, translate PIDs between caller and target PID namespaces, enumerate mount namespaces, or retrieve IDs. The `ns_id_req` layout supports `statns(2)` and `listns(2)` style request filtering by namespace type and owning user namespace.

State and persistence behavior: The header owns no state. It exposes stable-ish namespace identity snapshots: inode numbers for init namespaces, 64-bit namespace IDs, mount counts, and owning user namespace IDs. Callers must treat namespace lifetime as fd-pinned and handle disappearance or permission failures during iteration.

Dependencies and integration points: Depends on `<linux/ioctl.h>` and `<linux/types.h>`. Integrates with procfs namespace links, pidfds/namespace fds, container runtimes, checkpoint/restore tooling, monitoring agents, and namespace-aware process managers.

Risks: ABI size fields must be honored for forward compatibility. PID translation can fail or return different visible IDs depending on caller namespace. Exposing namespace IDs and owner UIDs is security-sensitive and must preserve kernel permission checks. Mount namespace iteration can race namespace creation/destruction.

Test signals: Exercise ioctls from nested user, pid, net, and mount namespaces; verify `size` version handling; test PID/TGID translation in both directions; enumerate mount namespaces with `LISTNS_CURRENT_USER`; and validate permission failures for unprivileged callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nsfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nsm.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/nsm.h

Purpose: Defines the ioctl ABI for AWS Nitro Secure Module raw message exchange.

Important APIs/types/functions: Exports `NSM_MAGIC`, `NSM_REQUEST_MAX_SIZE`, `NSM_RESPONSE_MAX_SIZE`, `struct nsm_iovec`, `struct nsm_raw`, and `NSM_IOCTL_RAW`. `struct nsm_iovec` carries a userspace virtual address and length as 64-bit fields; `struct nsm_raw` pairs request and response buffers.

Control flow: A privileged userspace process opens the NSM device and submits `NSM_IOCTL_RAW` with request and response iovecs. The driver copies or maps the request, sends it to the Nitro Secure Module, then fills the response buffer subject to maximum sizes.

State and persistence behavior: The header defines transient request/response buffers only. Persistent attestation keys, entropy state, and module state live in the platform device or firmware, not in this ABI header.

Dependencies and integration points: Depends on `<linux/ioctl.h>` and `<linux/types.h>`. Integrates with enclave attestation agents and Nitro platform drivers. The comment notes raw access is gated by `CAP_SYS_ADMIN`.

Risks: User pointers and lengths are untrusted; kernel handling must enforce request and response maxima and avoid leaking stale response bytes. Because raw messages can affect attestation or key operations, capability and device access policy are high-impact.

Test signals: Build 32/64-bit userspace clients, submit boundary-size requests, verify response truncation/error behavior, test invalid pointers and over-limit lengths, and confirm unprivileged callers cannot use the raw ioctl.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nsm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ntsync.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ntsync.h

Purpose: Defines the ioctl ABI for Linux kernel emulation of Windows NT synchronization primitives used by Wine/Proton-style runtimes.

Important APIs/types/functions: Exports `struct ntsync_sem_args`, `struct ntsync_mutex_args`, `struct ntsync_event_args`, `struct ntsync_wait_args`, `NTSYNC_WAIT_REALTIME`, `NTSYNC_MAX_WAIT_COUNT`, creation ioctls for semaphores, mutexes, and events, wait-any/wait-all ioctls, and object operations such as semaphore release, mutex unlock/kill/read, and event set/reset/pulse/read.

Control flow: Userspace creates synchronization objects through an ntsync device fd, receives object fds, then waits on arrays of object fds through `NTSYNC_IOC_WAIT_ANY` or `NTSYNC_IOC_WAIT_ALL`. Wait arguments carry a userspace pointer to object references, a count capped by `NTSYNC_MAX_WAIT_COUNT`, timeout mode, owner ID, alert object, and return index.

State and persistence behavior: The header defines userspace-visible object state: semaphore count/max, mutex owner/recursion count, event manual-reset and signaled bits, and wait result fields. Object lifetime and wait queues persist only while kernel object fds are open.

Dependencies and integration points: Depends on `<linux/types.h>` and ioctl encoding macros. Integrates with `/dev/ntsync`, Wine synchronization layers, pollable file descriptors, and Linux wait queue implementation behind the driver.

Risks: Windows-compatible semantics are subtle: abandoned/killed mutexes, pulse events, alertable waits, timeout clock selection, and wait-all atomicity must match expectations. The ABI uses userspace pointers and owner IDs, so validation and 32/64-bit compatibility matter.

Test signals: Run Wine synchronization conformance tests, verify wait-any indexes, wait-all atomic acquisition, realtime versus monotonic timeouts, max wait count rejection, event pulse behavior, mutex kill/read semantics, and concurrent close during waits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ntsync.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nubus.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/nubus.h

Purpose: Publishes NuBus category, type, driver software/hardware, and ROM resource IDs for old Macintosh NuBus drivers and userspace tooling.

Important APIs/types/functions: Defines `enum nubus_category`, network/display/CPU type enums, `enum nubus_drsw`, `enum nubus_drhw`, `enum nubus_res_id`, and category-specific resource ID enums for board, vendor, network, CPU, and display resources. Constants identify display cards, SONIC Ethernet variants, CPU boards, ROM directories, MAC address records, and display mode resources.

Control flow: No executable flow. Kernel NuBus probing and drivers match ROM tuples such as category/type/DrSW/DrHW and walk resource directories using these IDs. Userspace diagnostic tools can use the same constants to decode ROM contents.

State and persistence behavior: The header describes persistent firmware ROM metadata on NuBus cards. It does not store state; matched devices and parsed ROM data live in bus/device structures at runtime.

Dependencies and integration points: Depends on `<linux/types.h>`. Integrates with m68k Macintosh NuBus bus code, framebuffer and network drivers, and historical ROM inspection tooling.

Risks: Some cards misidentify themselves, as noted by comments, so consumers must avoid over-trusting DrHW values. Numeric IDs are ABI and historical hardware documentation; reusing or renumbering them would break drivers and tooling.

Test signals: Decode known NuBus ROMs, match documented Ethernet and framebuffer tuples, verify resource directory parsing for vendor/MAC/display modes, and compile m68k NuBus drivers against the UAPI header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nubus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nvme_ioctl.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/nvme_ioctl.h

Purpose: Defines the userspace ioctl and io_uring command ABI for NVM Express namespace, controller, admin, and passthrough operations.

Important APIs/types/functions: Exports `struct nvme_user_io`, `struct nvme_passthru_cmd`, `struct nvme_passthru_cmd64`, `struct nvme_uring_cmd`, `nvme_admin_cmd`, and ioctl numbers `NVME_IOCTL_ID`, `NVME_IOCTL_ADMIN_CMD`, `NVME_IOCTL_SUBMIT_IO`, `NVME_IOCTL_IO_CMD`, reset/rescan ioctls, 64-bit passthrough ioctls, vectored IO variants, and `NVME_URING_CMD_*` async commands.

Control flow: Userspace opens an NVMe character or block device and either submits structured namespace I/O through `nvme_user_io`, sends arbitrary admin or I/O command dwords via passthrough structures, or issues async io_uring commands. The kernel translates the ABI structure to NVMe SQEs, DMA maps data and metadata buffers, waits or completes asynchronously, and returns command result fields.

State and persistence behavior: The header carries transient command parameters, user buffer addresses, data lengths, metadata pointers, timeouts, namespace IDs, and completion results. Durable state changes may occur on the device for admin commands, format, firmware, namespace management, reset, or writes, but the header itself owns no state.

Dependencies and integration points: Depends on `<linux/types.h>`. Integrates with nvme-cli, libnvme, io_uring, block devices, controller char devices, and kernel NVMe core passthrough validation.

Risks: Raw passthrough exposes powerful device operations; capability checks, namespace/controller targeting, buffer length validation, metadata handling, and 32/64-bit layout compatibility are critical. Vectored commands overload `data_len` with `vec_cnt`, so callers and kernel paths must select the correct ioctl.

Test signals: Run nvme-cli identify/get-log/admin passthrough, read/write namespace I/O, invalid opcode and timeout cases, 64-bit result propagation, vectored io_uring commands, reset/rescan behavior, and compat userspace structure tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nvme_ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nvram.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/nvram.h

Purpose: Defines the small `/dev/nvram` ioctl ABI and offset helper constants for legacy system NVRAM access.

Important APIs/types/functions: Exports `NVRAM_INIT`, `NVRAM_SETCKS`, `NVRAM_FIRST_BYTE`, and `NVRAM_OFFSET(x)`.

Control flow: Userspace can ask the driver to initialize NVRAM and set the checksum, or recalculate the checksum after modifications. Data reads/writes use NVRAM offsets relative to `NVRAM_FIRST_BYTE` rather than absolute platform byte positions.

State and persistence behavior: NVRAM is persistent firmware/platform storage. This header does not store data but defines operations that can update persistent checksum-covered bytes.

Dependencies and integration points: Depends on `<linux/ioctl.h>`. Integrates with architecture-specific NVRAM drivers, boot variables, and old platform configuration tools.

Risks: Incorrect offset calculation can corrupt firmware settings. Init and checksum ioctls mutate persistent state and should be access-controlled. The constant assumes current systems expose NVRAM starting at byte 14.

Test signals: Exercise read/write/checksum tools on emulated or disposable NVRAM, verify `NVRAM_OFFSET()` conversions, reject invalid offsets in the driver, and ensure checksum recalculation survives reboot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nvram.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/omap3isp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/omap3isp.h

Purpose: Defines the private V4L2 userspace ABI for TI OMAP3 ISP configuration, statistics delivery, and image-processing block tuning.

Important APIs/types/functions: Exports private ioctls `VIDIOC_OMAP3ISP_CCDC_CFG`, `VIDIOC_OMAP3ISP_PRV_CFG`, `VIDIOC_OMAP3ISP_AEWB_CFG`, `VIDIOC_OMAP3ISP_HIST_CFG`, `VIDIOC_OMAP3ISP_AF_CFG`, `VIDIOC_OMAP3ISP_STAT_REQ`, `VIDIOC_OMAP3ISP_STAT_REQ_TIME32`, and `VIDIOC_OMAP3ISP_STAT_EN`. Defines private V4L2 events for AEWB, AF, and histogram readiness. Major structs include `omap3isp_h3a_aewb_config`, `omap3isp_stat_data`, `omap3isp_hist_config`, `omap3isp_h3a_af_config`, `omap3isp_ccdc_update_config`, many nested CCDC/preview tuning structs, and `omap3isp_prev_update_config`.

Control flow: Userspace configures sensor pipeline blocks with private ioctls, enables statistics modules, waits for V4L2 events, then requests statistics buffers by frame/config counter. CCDC update flags select A-Law, low-pass, black clamp/compensation, faulty-pixel correction, culling, and lens shading. Preview update flags select luma, CFA, chroma suppression, white balance, color conversion, defect correction, noise filter, gamma, and dark-frame features.

State and persistence behavior: The header defines transient configuration snapshots and statistics buffer contracts. Persistent driver state includes hardware register configuration, buffer queues, frame numbers, config counters, and statistics readiness. Time32 and native timestamp layouts preserve compat behavior.

Dependencies and integration points: Depends on `<linux/types.h>` and `<linux/videodev2.h>`. Integrates with the OMAP3 ISP media driver, V4L2 subdev/media-controller pipelines, camera applications, and 32-bit compatibility ioctl handling.

Risks: Many structs contain `__user` pointers to secondary configuration tables, making copy-in validation and size/range checks critical. Hardware limits are encoded as constants and must match driver validation. ABI layout differs under `__KERNEL__` for timestamps and time32 compatibility, so padding and conversion bugs can break userspace.

Test signals: Run media-controller camera capture with AEWB/AF/hist events, verify all ioctl range checks, exercise compat 32-bit `STAT_REQ_TIME32`, pass invalid nested user pointers, validate buffer size maxima, and compare register programming against expected image output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/omap3isp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/omapfb.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/omapfb.h

Purpose: Defines the legacy TI OMAP framebuffer userspace ABI for display updates, plane setup, memory setup, color keying, VRAM queries, and synchronization.

Important APIs/types/functions: Exports OMAP ioctl constructors and commands including `OMAPFB_MIRROR`, `OMAPFB_SYNC_GFX`, `OMAPFB_VSYNC`, update mode, caps, window update, color key, plane setup/query, memory setup/query, vsync/go waits, memory read, overlay colormode, VRAM info, tear sync, and display info. Important structs include `omapfb_update_window`, `omapfb_plane_info`, `omapfb_mem_info`, `omapfb_caps`, `omapfb_color_key`, `omapfb_memory_read`, `omapfb_ovl_colormode`, `omapfb_vram_info`, `omapfb_tearsync_info`, and `omapfb_display_info`.

Control flow: Userspace opens the framebuffer device, queries capabilities and memory, configures planes and update mode, submits update windows, waits for vsync or GO completion, and optionally reads display memory. Plane and update structures carry position, output size, color format, memory index, channel output, and reserved extension fields.

State and persistence behavior: The header exposes runtime display state, not durable storage. Driver state includes VRAM allocation, plane enablement and positions, manual/auto update mode, color keying, tear sync, and overlay formats. Reserved fields provide ABI growth space.

Dependencies and integration points: Depends on `<linux/fb.h>`, `<linux/ioctl.h>`, and `<linux/types.h>`. Integrates with fbdev applications and OMAP display hardware; it predates DRM/KMS but may coexist in old userspace stacks.

Risks: `struct omapfb_memory_read` includes a userspace pointer and `size_t`, which makes compat handling important. Window scaling, rotation, and memory relocation depend on capability bits. Incorrect reserved-field handling or ioctl direction macros can break old binaries.

Test signals: Query caps/memory/planes on OMAP hardware or emulator, perform manual and auto updates, test color key and tear sync, wait for vsync/go, read back framebuffer regions, and run 32-bit userspace ioctl compatibility tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/omapfb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/oom.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/oom.h

Purpose: Publishes userspace constants for configuring OOM killer scoring through procfs.

Important APIs/types/functions: Defines `OOM_SCORE_ADJ_MIN`, `OOM_SCORE_ADJ_MAX`, legacy `OOM_DISABLE`, `OOM_ADJUST_MIN`, and `OOM_ADJUST_MAX`.

Control flow: Userspace writes values to `/proc/<pid>/oom_score_adj` or legacy `/proc/<pid>/oom_adj`; the kernel uses them during badness scoring when selecting OOM kill victims.

State and persistence behavior: Values are per-process runtime attributes and do not persist across exec/fork except according to kernel task inheritance rules. This header only fixes the numeric ABI range.

Dependencies and integration points: No external header dependencies beyond include guards. Integrates with procfs, init systems, container runtimes, service managers, and memory pressure policy tools.

Risks: `OOM_SCORE_ADJ_MIN` disables OOM killing for a task, so overly broad use can make system-wide OOM unrecoverable. Legacy `oom_adj` has a different range and mapping, creating migration risk for old tools.

Test signals: Write min/max/out-of-range values through procfs, verify inherited values for child processes, check container runtime policy, and trigger controlled memory pressure to confirm scoring changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/oom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/openat2.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/openat2.h

Purpose: Defines `openat2(2)` argument layout and path-resolution hardening flags.

Important APIs/types/functions: Exports `struct open_how` with `flags`, `mode`, and `resolve`, plus `RESOLVE_NO_XDEV`, `RESOLVE_NO_MAGICLINKS`, `RESOLVE_NO_SYMLINKS`, `RESOLVE_BENEATH`, `RESOLVE_IN_ROOT`, and `RESOLVE_CACHED`.

Control flow: Userspace passes `open_how` and its size to `openat2`. The kernel validates unknown bits strictly, checks mode only with creation flags, and applies resolution constraints while walking the path. `RESOLVE_CACHED` can short-circuit with `-EAGAIN` if a nonblocking cached lookup is not possible.

State and persistence behavior: The header defines one syscall argument snapshot. No persistent state is stored; resulting file descriptors and filesystem side effects follow normal open semantics.

Dependencies and integration points: Depends on `<linux/types.h>`. Integrates with libc wrappers, sandboxing/container runtimes, package managers, and security-sensitive path opening code.

Risks: Userspace must pass correct structure size for forward compatibility. Misunderstanding `RESOLVE_BENEATH` versus `RESOLVE_IN_ROOT`, magic links, or mount crossing can create directory traversal vulnerabilities. The comment typo `OEXT_NO_MAGICLINKS` should be read as implying `RESOLVE_NO_MAGICLINKS`.

Test signals: Run path traversal tests with symlinks, `..`, bind mounts, procfs magic links, and absolute paths; verify unknown flag rejection; verify `RESOLVE_CACHED` `-EAGAIN`; and test structure size extension behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/openat2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/openvswitch.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/openvswitch.h

Purpose: Defines the Generic Netlink ABI for the in-kernel Open vSwitch datapath, including datapaths, packets, vports, flows, flow keys, actions, meters, and conntrack limits.

Important APIs/types/functions: Exports family names and versions for datapath, packet, vport, flow, meter, and conntrack-limit operations. Core layouts include `struct ovs_header`, `ovs_dp_stats`, `ovs_dp_megaflow_stats`, `ovs_vport_stats`, `ovs_flow_stats`, flow key structs for Ethernet, VLAN/MPLS, IPv4/IPv6, TCP/UDP/SCTP/ICMP/ARP/ND, conntrack tuples/labels, tunnel metadata, NSH keys, and action payloads such as VLAN/MPLS push, hash, truncation, CT/NAT, clone/sample/check-packet-length, decrement TTL, and psample.

Control flow: Userspace creates a datapath, adds vports, receives packet miss/action upcalls, installs or deletes flows with nested key/mask/action attributes, and queries stats/meters/limits. Packet execution applies nested `OVS_ACTION_ATTR_*` lists. Conntrack and NAT actions alter tracking state, recirculation restarts matching with a new ID, and meters enforce configured rate bands.

State and persistence behavior: Runtime state lives in the kernel datapath: flow tables, mask caches, megaflow stats, vport stats, upcall PID arrays, meters, conntrack limits, and per-flow actions. The header defines the wire format for creating, querying, and mutating that state; nothing is durable across module unload or datapath deletion unless userspace reconstructs it.

Dependencies and integration points: Depends on `<linux/types.h>` and `<linux/if_ether.h>`. Integrates with Open vSwitch userspace daemons, Generic Netlink policy parsing, tunnel drivers, conntrack/netfilter, tc offload, psample, and network namespaces.

Risks: This ABI is deeply nested and backward compatibility is critical. Attribute type squatting, in-kernel-only enum members under `__KERNEL__`, alignment, mask/value pairing, endian-marked fields, tunnel option lengths, NAT/CT semantics, and upcall PID routing all create compatibility and security risk. Malformed netlink attributes must not lead to out-of-bounds parsing or unintended packet mutation.

Test signals: Run OVS datapath selftests, create/delete datapaths and vports, install flows with masks and all major key families, exercise tunnel metadata, CT/NAT, clone/sample/meter/psample/dec-ttl actions, fuzz malformed netlink attributes, and verify old userspace continues to work with new kernels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/openvswitch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ovpn.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ovpn.h

Purpose: Defines the YAML-generated Generic Netlink UAPI for the in-kernel OpenVPN data channel.

Important APIs/types/functions: Exports `OVPN_FAMILY_NAME`, `OVPN_FAMILY_VERSION`, `OVPN_NONCE_TAIL_SIZE`, cipher algorithms, peer deletion reasons, key slots, nested peer attributes, key configuration attributes, key direction attributes, top-level attributes, commands, and multicast group `OVPN_MCGRP_PEERS`.

Control flow: Userspace configures peers with `OVPN_CMD_PEER_NEW/SET/GET/DEL`, receives deletion and float notifications, installs/queries/swaps/deletes keys with key commands, and passes nested peer/key attributes such as remote/local addresses, ports, sockets, keepalive settings, VPN addresses, counters, tx ID, key slot, key ID, cipher algorithm, cipher keys, and nonce tails.

State and persistence behavior: Kernel state includes peer table entries, transport socket association, VPN/link counters, keepalive timers, current and secondary key slots, cipher material, and nonce tails. The header defines netlink state exchange only; configured peers and keys are runtime state.

Dependencies and integration points: It is auto-generated from `Documentation/netlink/specs/ovpn.yaml` and integrates with YNL tooling, Generic Netlink policy, OpenVPN userspace, UDP/TCP sockets, network namespaces, and crypto implementations for AES-GCM and ChaCha20-Poly1305.

Risks: Generated UAPI must stay in sync with the YAML spec. Key attributes carry sensitive material and must be validated, zeroized in kernel paths, and not emitted unexpectedly. Socket netns IDs, peer floating, and notification ordering can cause stale peer state in userspace.

Test signals: Regenerate header from YAML and compare, use YNL tests for every command, add/get/delete peers, install/swap/delete primary and secondary keys, verify multicast notifications, test unsupported cipher rejection, and inspect counter updates under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ovpn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/packet_diag.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/packet_diag.h

Purpose: Defines the netlink socket diagnostic ABI for AF_PACKET sockets.

Important APIs/types/functions: Exports `struct packet_diag_req`, `PACKET_SHOW_*` request bits, `struct packet_diag_msg`, diagnostic attribute enum values, `struct packet_diag_info`, `PDI_*` flags, `struct packet_diag_mclist`, and `struct packet_diag_ring`.

Control flow: Userspace sends a diagnostic request selecting family, protocol, inode/cookie filters, and show bits. The kernel replies with packet socket identity and optional nested attributes for basic info, multicast memberships, RX/TX ring configuration, fanout, UID, memory info, and attached filter.

State and persistence behavior: The header snapshots live socket state: packet socket type/num, inode, cookie, interface index, TPACKET version, reserve/copy thresholds, timestamp mode, flags, multicast memberships, and ring geometry. No state is persisted by the header.

Dependencies and integration points: Depends on `<linux/types.h>`. Integrates with `sock_diag`, `ss`, packet socket ring setup, fanout, BPF filters, and network namespace introspection.

Risks: Diagnostics can expose packet socket configuration and filter programs. Ring fields must match TPACKET setup, and multicast address buffers are fixed at 32 bytes. Inode/cookie filtering must avoid leaking sockets across namespace or permission boundaries.

Test signals: Query AF_PACKET sockets with each `PACKET_SHOW_*` bit, compare ring config to `PACKET_RX_RING`/`TX_RING` setup, validate multicast list output, test namespace isolation, and check attached filter reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/packet_diag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/papr_pdsm.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/papr_pdsm.h

Purpose: Defines PAPR SCM NVDIMM DSM payloads embedded in `ND_CMD_CALL` requests for libndctl and the powerpc papr_scm driver.

Important APIs/types/functions: Exports `ND_PDSM_PAYLOAD_MAX_SIZE`, `ND_PDSM_HDR_SIZE`, health status constants, extension flags, `struct nd_papr_pdsm_health`, SMART injection flags, `struct nd_papr_pdsm_smart_inject`, `enum papr_pdsm`, `union nd_pdsm_payload`, and packed `struct nd_pkg_pdsm`.

Control flow: Userspace constructs a generic `struct nd_cmd_pkg` with family `NVDIMM_FAMILY_PAPR_SCM`, command `PAPR_PDSM_HEALTH` or `PAPR_PDSM_SMART_INJECT`, and a following `nd_pkg_pdsm`. The libnvdimm layer routes it to papr_scm, which fills `cmd_status`, firmware status fields, and the selected payload union.

State and persistence behavior: Health payloads report persistent-memory durability risk: unarmed DIMM, bad shutdown/restore, scrubbed state, locked/encrypted state, health class, optional fuel gauge, and optional DSC. SMART injection is a test/debug mutation of reported firmware health state.

Dependencies and integration points: Depends on `<linux/types.h>` and `<linux/ndctl.h>`. Integrates with libndctl, ndctl health reporting, PAPR platform firmware calls, and powerpc NVDIMM drivers.

Risks: Packed layout and fixed 184-byte payload size are ABI-sensitive. Health flags affect operator decisions about persistent-memory reliability. SMART injection should be gated to debug/test paths. Reserved fields should be zeroed for future compatibility.

Test signals: Use ndctl/libndctl to issue health queries, validate payload size and `nd_fw_size`, test optional extension flags, inject fatal and bad-shutdown SMART states on supported platforms, and verify packed layout across 32/64-bit builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/papr_pdsm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/param.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/param.h

Purpose: Provides the generic UAPI include wrapper for architecture-specific system parameter constants.

Important APIs/types/functions: Includes `<asm/param.h>`, which typically provides constants such as `HZ`, `EXEC_PAGESIZE`, `NOGROUP`, and related architecture values.

Control flow: No runtime flow. Userspace includes `<linux/param.h>` and receives the architecture's exported parameter definitions through the asm UAPI layer.

State and persistence behavior: No state. Values are compile-time constants that describe kernel/userspace ABI assumptions for the target architecture.

Dependencies and integration points: Integrates directly with per-architecture UAPI headers and libc/kernel-header consumers.

Risks: Architecture mismatches or stale installed headers can produce incorrect constants in userspace. This wrapper must remain minimal to avoid diverging from `asm/param.h`.

Test signals: Compile on each supported architecture, compare exported constants with the target asm UAPI, and ensure userspace packages can include the header without kernel-only dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/parport.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/parport.h

Purpose: Defines user-visible constants for parallel port hardware classes, status/control bits, capability modes, IEEE1284 negotiation modes, and transfer flags.

Important APIs/types/functions: Exports `PARPORT_MAX`, IRQ/DMA auto/none/probe constants, control and status register bits, `parport_device_class`, `PARPORT_MODE_*` hardware capabilities, `IEEE1284_MODE_*` negotiation values, address/data flags, and EPP fast-transfer flags.

Control flow: Drivers and tools use these constants to describe port capabilities, interpret device IDs, negotiate IEEE1284 transfer modes, and select block transfer behavior. There are no functions in the header.

State and persistence behavior: The header describes runtime port configuration and attached-device capabilities. It does not persist state; port probing and negotiated mode live in parport core/driver state.

Dependencies and integration points: Integrates with parallel printer/scanner/storage drivers, IEEE1284 probing, ppdev userspace, and architecture-specific parport backends.

Risks: Mode bits have hardware timing implications; selecting unsafe EPP fast modes can produce unreliable counts. Magic IRQ/DMA values overlap negative sentinel meanings and must be interpreted in the correct context.

Test signals: Probe legacy, ECP, EPP, and tristate-capable ports; validate IEEE1284 negotiation; exercise ppdev read/write paths; test IRQ/DMA auto and probe-only settings; and compare status/control bit decoding against hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/parport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/patchkey.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/patchkey.h

Purpose: Preserves the `_PATCHKEY()` macro ABI used by legacy OSS/AWE sound patch structures while discouraging direct inclusion.

Important APIs/types/functions: Enforces indirect inclusion through `_LINUX_PATCHKEY_H_INDIRECT`, includes `<endian.h>` for userspace, and defines `_PATCHKEY(id)` differently for big- and little-endian byte order.

Control flow: No runtime flow. At preprocessing time, consumers included via `<sys/soundcard.h>` or `<linux/soundcard.h>` obtain an endian-correct patch key value.

State and persistence behavior: No runtime state. The macro encodes persistent binary patch identifiers in the endian layout expected by old userspace and driver interfaces.

Dependencies and integration points: Integrates with OSS soundcard headers and legacy AWE voice/patch userspace. It depends on userspace byte-order macros when not compiling in the kernel.

Risks: Direct include intentionally fails, so packaging or include-order changes can break builds. Incorrect byte-order detection changes binary patch identifiers and breaks legacy sound data exchange.

Test signals: Compile OSS userspace on little- and big-endian targets through the supported include path, verify direct inclusion errors, and compare `_PATCHKEY()` output against historical soundcard ABI expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/patchkey.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pci.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/pci.h

Purpose: Publishes basic PCI userspace helpers, legacy `/proc/bus/pci` ioctl values, and hotplug event IDs.

Important APIs/types/functions: Exports `PCI_DEVFN(slot, func)`, `PCI_SLOT(devfn)`, `PCI_FUNC(devfn)`, `PCIIOC_CONTROLLER`, `PCIIOC_MMAP_IS_IO`, `PCIIOC_MMAP_IS_MEM`, `PCIIOC_WRITE_COMBINE`, and `enum pci_hotplug_event`. It includes `<linux/pci_regs.h>` for register definitions.

Control flow: Userspace and kernel code encode or decode slot/function numbers with the macros. Legacy tools issue PCIIOC ioctls to change mmap space or query controller data for `/proc/bus/pci/X/Y` nodes. Hotplug events communicate link/card presence changes.

State and persistence behavior: The header owns no state. It describes addressing and ioctl commands that operate on kernel PCI device state and mmap behavior.

Dependencies and integration points: Depends on `pci_regs.h`. Integrates with pciutils-style tooling, legacy procfs PCI access, hotplug agents, and PCI core definitions.

Risks: `PCI_DEVFN` masks slot/function bits, so callers must validate inputs before encoding. Legacy mmap ioctls can expose device MMIO/IO space and require appropriate permissions.

Test signals: Compile pciutils consumers, encode/decode representative devfns, exercise procfs PCI mmap mode selection where enabled, and verify hotplug event constants in user/kernel ABI tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pci_regs.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/pci_regs.h

Purpose: Defines standard PCI, PCI-X, PCIe, extended capability, CXL DVSEC, DOE, IDE, and related configuration-space register offsets, bit masks, and helper macros.

Important APIs/types/functions: Exports constants for conventional config space size, standard header fields, BARs, bridge/CardBus headers, capability IDs, PM, AGP, VPD, MSI/MSI-X, PCI-X, HyperTransport, PCI Express capabilities/control/status/link/slot/root/AER/VC/ACS/SR-IOV/ATS/PRI/PASID/TPH/DPC/PTM/L1SS/DOE/IDE, Enhanced Allocation, Resizable BAR, NPEM, DVSEC accessors, and CXL DVSEC register blocks. Helper-style macros include field extractors such as `PCI_DVSEC_HEADER1_VID(x)` and indexed offsets for IDE/CXL ranges.

Control flow: No runtime flow. PCI core, drivers, and userspace tools use these offsets and masks to read, write, decode, and validate PCI configuration space and capability lists.

State and persistence behavior: The header describes hardware configuration state. Writes by consumers can change device enablement, bus mastering, BARs, power states, MSI/MSI-X, PCIe link behavior, AER status, SR-IOV, DPC, PTM, IDE, or CXL memory enablement, but the header itself stores nothing.

Dependencies and integration points: It is included by `<linux/pci.h>` and many drivers/tools. Integrates with PCI core enumeration, pciutils, sysfs config access, hotplug, virtualization/IOMMU, CXL, DOE protocols, and security features such as ACS and IDE.

Risks: Register definitions must match evolving PCI-SIG specifications. Incorrect masks or offsets can cause device misconfiguration, broken enumeration, disabled interrupts, link instability, or security boundary failures. Some macros use bit-generation helpers expected from kernel-style includes, so userspace header installation must provide compatible definitions.

Test signals: Build broad PCI driver/userspace consumers, compare offsets against spec and pciutils decoding, run PCI config-space selftests, validate capability walking on real and virtual devices, test MSI/MSI-X and AER/DPC paths, and verify CXL/DOE/IDE definitions against supported hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pci_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pcitest.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/pcitest.h

Purpose: Defines ioctl ABI for the PCI endpoint test driver.

Important APIs/types/functions: Exports `PCITEST_BAR`, `PCITEST_INTX_IRQ`, `PCITEST_MSI`, `PCITEST_WRITE`, `PCITEST_READ`, `PCITEST_COPY`, `PCITEST_MSIX`, IRQ type set/get, BAR query/subrange, doorbell, clear IRQ, IRQ type constants, `PCITEST_FLAGS_USE_DMA`, and `struct pci_endpoint_test_xfer_param`.

Control flow: Userspace opens the endpoint test device, selects IRQ mode, triggers BAR tests, runs read/write/copy transfers with a size or transfer parameter, triggers interrupts or doorbells, and checks test results returned by the driver.

State and persistence behavior: The header defines transient test commands. Runtime state includes selected IRQ type, endpoint BAR mappings, DMA use flag, and transfer buffers; it does not persist beyond the device/test session.

Dependencies and integration points: Integrates with PCI endpoint controller/function testing, kernel PCI endpoint test driver, and hardware validation suites.

Risks: Transfer sizes and DMA flags must be validated to avoid overrun or mapping misuse. IRQ mode transitions need cleanup. The older unsigned-long size ioctls may have compat width concerns.

Test signals: Run endpoint test utility across INTx/MSI/MSI-X, BAR and BAR subrange checks, DMA and non-DMA transfers, read/write/copy sizes including zero and large values, doorbell signaling, and clear IRQ behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pcitest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/perf_event.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/perf_event.h

Purpose: Defines the `perf_event_open(2)` ABI, perf event attributes, ioctl controls, mmap metadata page, ring-buffer record formats, sample formats, branch and memory-data encodings, and related constants.

Important APIs/types/functions: Exports event type enums, hardware/software/cache IDs, sample format bits, branch sample bits, read formats, `PERF_ATTR_SIZE_VER*`, `struct perf_event_attr`, `struct perf_event_query_bpf`, perf ioctls, `struct perf_event_mmap_page`, `struct perf_event_header`, namespace link info, `enum perf_event_type`, ksymbol/BPF/cgroup/text-poke/AUX/callchain records, `union perf_mem_data_src`, memory hierarchy masks, `struct perf_branch_entry`, and `union perf_sample_weight`.

Control flow: Userspace fills `perf_event_attr` and calls `perf_event_open`, then controls the event fd through ioctls, reads counts, mmaps a metadata page plus data/AUX rings, and parses `perf_event_header` records. The kernel emits record layouts conditionally based on `sample_type`, `read_format`, `sample_id_all`, event flags, and mmap/AUX configuration.

State and persistence behavior: Event state is runtime kernel state: enabled/running time, PMU index/offset, ring buffer producer positions, AUX buffer positions, lost counts, BPF attachments, and sampling configuration. The mmap page exposes seqlock-protected metadata for user reads. No state is durable beyond event fd lifetime, though perf.data files persist decoded records.

Dependencies and integration points: Depends on `<linux/types.h>`, `<linux/ioctl.h>`, and `<asm/byteorder.h>`. Integrates with PMU drivers, tracepoints, kprobes/uprobes, BPF, cgroups, namespace reporting, AUX trace engines such as Intel PT/CoreSight, and perf tooling.

Risks: This is a dense forward-compatible ABI; `attr.size`, reserved bits, endianness-specific bitfields, ring-buffer memory ordering, sample layout conditionals, and compat struct handling are high risk. Raw sample payloads are explicitly not stable ABI. Permission controls must protect kernel, hypervisor, branch, register, and physical-address sampling data.

Test signals: Run `perf test`, open every event type, verify old `attr.size` versions, parse records with many `sample_type` combinations, test mmap ring and AUX overwrite modes, exercise BPF query/attach ioctls, run 32-bit compat tests, and validate memory data source and branch stack decoding on supported PMUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/perf_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/personality.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/personality.h

Purpose: Defines process personality flags and personality type constants used by the `personality(2)` syscall and exec compatibility behavior.

Important APIs/types/functions: Exports bug-emulation/security flags such as `ADDR_NO_RANDOMIZE`, `FDPIC_FUNCPTRS`, `MMAP_PAGE_ZERO`, `ADDR_COMPAT_LAYOUT`, `READ_IMPLIES_EXEC`, address limit flags, `STICKY_TIMEOUTS`, `PER_CLEAR_ON_SETID`, personality constants such as `PER_LINUX`, `PER_LINUX32`, SVR/IRIX/Solaris/HPUX variants, and `PER_MASK`.

Control flow: Userspace calls `personality()` to query or set the low personality byte plus high compatibility flags. The kernel consults these bits during exec, memory layout selection, mmap permissions, signal/function-pointer interpretation, uname behavior, and timeout restart behavior.

State and persistence behavior: Personality is per-task state inherited across fork and modified/reset across exec according to kernel rules. `PER_CLEAR_ON_SETID` identifies security-sensitive flags cleared on setuid/setgid exec.

Dependencies and integration points: No external dependencies. Integrates with libc, compatibility loaders, binfmt handlers, ASLR policy, and old UNIX binary emulation.

Risks: Flags such as `READ_IMPLIES_EXEC`, `ADDR_NO_RANDOMIZE`, and `MMAP_PAGE_ZERO` are security-relevant. Personality low byte avoids the top bit to prevent confusion with negative syscall returns. Setid clearing must stay aligned with `PER_CLEAR_ON_SETID`.

Test signals: Use `personality(2)` to set each supported flag, verify ASLR and mmap behavior, test setuid exec clearing, run 32-bit/compat binary loaders, and confirm legacy personality types preserve expected timeout and uname semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/personality.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pfkeyv2.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/pfkeyv2.h

Purpose: Defines the PF_KEY v2 socket ABI for IPsec Security Association and Security Policy management, following RFC 2367 plus Linux extensions.

Important APIs/types/functions: Exports `PF_KEY_V2`, `PFKEYV2_REVISION`, packed SADB message/extension structs, SA/lifetime/address/key/identity/sensitivity/proposal/supported/algorithm/SPIRANGE structures, Linux extension structs for SA2, policy, IPsec request, NAT-T, security context, KM address, and dump filter. Defines message types, SA flags/states/types, auth/encryption/compression algorithms, extension IDs, and identity types.

Control flow: Key management daemons communicate over PF_KEY sockets by sending `sadb_msg` headers followed by 64-bit-length extension blocks. The kernel creates, updates, deletes, dumps, expires, acquires, and migrates IPsec SAs and policies based on these messages, and emits notifications back to registered daemons.

State and persistence behavior: Runtime state lives in the kernel XFRM/IPsec SAD and SPD. The ABI represents SA SPI, replay, algorithm, keys, lifetimes, addresses, identities, policies, NAT-T ports, security contexts, and migration data. SAs/policies persist until deleted, expired, flushed, or namespace teardown.

Dependencies and integration points: Depends on `<linux/types.h>`. Integrates with racoon, setkey, strongSwan compatibility paths, XFRM state/policy management, SELinux/LSM contexts, NAT traversal, and network namespaces.

Risks: Packed layouts and RFC-specified length units must be exact. Key material is sensitive and must be copied, validated, and zeroed carefully. Algorithm IDs include legacy and Linux-specific values; arbitrary renumbering would break key daemons. Extension parsing must reject malformed lengths.

Test signals: Run PF_KEY key-manager tests, add/update/delete AH/ESP/IPComp SAs, install SPD entries, dump/filter SAs, test NAT-T and security contexts, validate expire/acquire notifications, fuzz extension length/order, and compare behavior with XFRM netlink equivalents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pfkeyv2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pfrut.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/pfrut.h

Purpose: Defines ioctl ABI and payload layouts for Platform Firmware Runtime Update and telemetry log access.

Important APIs/types/functions: Exports `PFRUT_IOCTL_MAGIC`, update ioctls `PFRU_IOC_SET_REV`, `PFRU_IOC_STAGE`, `PFRU_IOC_ACTIVATE`, `PFRU_IOC_STAGE_ACTIVATE`, `PFRU_IOC_QUERY_CAP`, telemetry ioctls `PFRT_LOG_IOC_SET_INFO`, `PFRT_LOG_IOC_GET_INFO`, `PFRT_LOG_IOC_GET_DATA_INFO`, `struct pfru_payload_hdr`, `enum pfru_dsm_status`, `struct pfru_update_cap_info`, `struct pfru_com_buf_info`, `struct pfru_updated_result`, `struct pfrt_log_data_info`, and `struct pfrt_log_info`.

Control flow: Userspace sets the revision, queries capability, stages a firmware capsule from a communication buffer, activates the staged image, or performs stage+activate. Telemetry userspace sets/gets log selector information and queries physical buffer chunks and rollover/reset counters.

State and persistence behavior: PFRUT operations can mutate platform firmware runtime state and may have durable firmware effects. Capability, communication-buffer, result, and telemetry structs snapshot firmware/ACPI DSM status, versions, GUIDs, physical buffer addresses, sizes, timing, and log metadata.

Dependencies and integration points: Depends on `<linux/ioctl.h>` and `<linux/types.h>`. Integrates with ACPI/DSM firmware interfaces, platform firmware update tools, capsule image formats, and telemetry log readers.

Risks: Firmware update ioctls are high-impact. User input must validate revision IDs, capsule headers, communication buffer boundaries, anti-rollback versions, and firmware status. Physical addresses in telemetry/buffer info must not be exposed to untrusted callers without policy checks.

Test signals: Query capability on supported firmware, stage invalid and valid capsules, activate staged images in controlled environments, verify DSM status mapping, read telemetry log info/data info, test invalid revision/log selectors, and ensure update failures return documented errno paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pfrut.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pg.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/pg.h

Purpose: Defines the read/write buffer ABI for the generic parallel-port ATAPI packet driver `/dev/pgN`.

Important APIs/types/functions: Exports `PG_MAGIC`, `PG_RESET`, `PG_COMMAND`, `PG_MAX_DATA`, `struct pg_write_hdr`, and `struct pg_read_hdr`.

Control flow: Userspace writes a `pg_write_hdr` followed by optional outbound data. For `PG_COMMAND`, a successful write must be followed by a read that returns `pg_read_hdr`, device data, and status. For `PG_RESET`, no following read is expected. The driver assumes 12-byte ATAPI command packets and caps data transfer at `PG_MAX_DATA`.

State and persistence behavior: The ABI models one pending command per device. Runtime state includes command-in-progress, internal copy buffer, timeout, ATAPI packet, status, and command duration. The header defines no durable state.

Dependencies and integration points: Integrates with the old parallel port ATAPI `pg` driver, ATAPI devices, and userspace tools modeled loosely after generic SCSI but without ioctls.

Risks: The protocol is sequencing-sensitive: read without pending command or write while busy should fail. Fixed 12-byte packets and internal buffer copying require length validation. The magic byte is the only version marker.

Test signals: Send valid command/read pairs, reset operations without reads, invalid magic/function values, over-`PG_MAX_DATA` lengths, timeouts, concurrent command attempts, and offline/malfunctioning device cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/phantom.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/phantom.h

Purpose: Defines ioctl ABI and register constants for the SensAble Phantom haptic device driver.

Important APIs/types/functions: Exports `struct phm_reg`, `struct phm_regs`, `PH_IOC_MAGIC`, legacy pointer-typed ioctls `PHN_GET_REG`, `PHN_SET_REG`, `PHN_GET_REGS`, `PHN_SET_REGS`, value-typed ioctls `PHN_GETREG`, `PHN_SETREG`, `PHN_GETREGS`, `PHN_SETREGS`, `PHN_NOT_OH`, control register constants, and `PHN_ZERO_FORCE`.

Control flow: Userspace reads or writes one register or a masked set of up to eight registers, optionally declares it is not OpenHaptics with `PHN_NOT_OH`, and uses control bits for amplifier switching, button status, and IRQ enablement.

State and persistence behavior: Runtime state lives in device registers and driver mode flags. `PHN_NOT_OH` changes driver update behavior to avoid unwanted device switch-offs for libphantom-style callers. Register values are hardware state, not file-backed persistence.

Dependencies and integration points: Depends on `<linux/types.h>` and ioctl macros from transitive UAPI context. Integrates with haptic device userspace libraries and the Phantom PCI/char driver.

Risks: The header contains both pointer-encoded and direct-struct ioctl variants, so compat handling is easy to get wrong. Register masks/counts must be bounded to eight values. Incorrect torque/control writes can affect physical haptic output.

Test signals: Exercise single and multi-register get/set paths, compare old and new ioctl encodings, test `PHN_NOT_OH` mode, validate mask/count bounds, read button/IRQ control state, and verify zero-force behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/phantom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/phonet.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/phonet.h

Purpose: Defines the Phonet socket ABI used for Nokia modem/resource communication, including protocol numbers, socket options, ioctls, packet headers, socket addresses, and address helper functions.

Important APIs/types/functions: Exports protocol constants `PN_PROTO_TRANSPORT`, `PN_PROTO_PHONET`, `PN_PROTO_PIPE`, socket options `PNPIPE_*`, address/resource constants, ioctl numbers `SIOCPNGETOBJECT`, `SIOCPNENABLEPIPE`, `SIOCPNADDRESOURCE`, `SIOCPNDELRESOURCE`, packed `struct phonethdr`, `struct phonetmsg`, packed `struct sockaddr_pn`, well-known `PN_DEV_PC`, and inline helpers for object/address/port construction and sockaddr get/set operations.

Control flow: Userspace creates Phonet sockets, binds/connects using `sockaddr_pn`, sets pipe options, and sends packets with Phonet headers and common payload headers. The inline helpers pack 6-bit device addresses and 10-bit ports into `spn_dev` and `spn_obj` fields.

State and persistence behavior: Runtime state includes socket binding, pipe encapsulation, resource routing entries, object handles, and network device association. The header exposes packet and address formats only; no durable state is stored.

Dependencies and integration points: Depends on `<linux/types.h>` and `<linux/socket.h>`. Integrates with AF_PHONET sockets, Nokia modem drivers, resource routing, and network-device plumbing.

Risks: Packed structs and bit packing must match wire format. Address helpers mask low bits for ports and high bits for device address; incorrect use can route to the wrong resource. Phonet is niche, so regression coverage may be thin.

Test signals: Build userspace socket clients, bind/connect with helper-generated addresses, test pipe socket options and resource add/delete ioctls, encode/decode common and extended messages, and validate packet headers on loopback or supported modem hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/phonet.h -->
