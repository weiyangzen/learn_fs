# subset-b-005979 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/dm-ioctl.h -->
## sources/distributed-fs/ceph-client/include/uapi/linux/dm-ioctl.h

Purpose: This UAPI header defines the traditional ioctl ABI for Linux device-mapper control via `/dev/mapper/control`. It is the userspace contract for creating, removing, renaming, suspending, resuming, loading tables for, querying, and messaging dm devices. The core model is a dm device with an active table and an inactive table; userspace prepares the inactive table with `DM_TABLE_LOAD`, then activates it with resume through `DM_DEV_SUSPEND`.

Important APIs and types: `struct dm_ioctl` is the fixed header for every ioctl payload and carries ABI version, buffer sizing, target count, open count, flags, event or udev cookie, device number, name, UUID, and trailing data. `struct dm_target_spec` describes table segments with sector range, target type, status, and `next` offsets into a packed variable-length buffer. `struct dm_target_deps`, `struct dm_name_list`, `struct dm_target_versions`, and `struct dm_target_msg` define dependency lists, device enumeration records, target version records, and target message payloads. The ioctl command family is keyed by `DM_IOCTL` and includes `DM_VERSION`, `DM_REMOVE_ALL`, `DM_LIST_DEVICES`, `DM_DEV_CREATE`, `DM_DEV_REMOVE`, `DM_DEV_RENAME`, `DM_DEV_SUSPEND`, `DM_DEV_STATUS`, `DM_DEV_WAIT`, `DM_TABLE_LOAD`, `DM_TABLE_CLEAR`, `DM_TABLE_DEPS`, `DM_TABLE_STATUS`, `DM_LIST_VERSIONS`, `DM_GET_TARGET_VERSION`, `DM_TARGET_MSG`, `DM_DEV_SET_GEOMETRY`, `DM_DEV_ARM_POLL`, and `DM_MPATH_PROBE_PATHS`.

Control flow and state: There are no functions beyond ioctl number definitions, but the comments define the control protocol. A normal flow is `DM_DEV_CREATE`, `DM_TABLE_LOAD`, `DM_DEV_SUSPEND` resume, status/deps queries, optional `DM_TARGET_MSG`, then suspend/remove. `DM_DEV_WAIT` blocks on target or table-change events. `event_nr` doubles as an event counter and as a udev cookie for operations that generate uevents. Flags drive state transitions and query modes, including read-only, suspended, persistent dev, active/inactive table present, buffer full, skip filesystem freeze, noflush, query inactive table, uevent generated, UUID rename, secure data wipe, data output, deferred remove, internal suspend, and IMA measurement output.

Persistence and dependencies: Persistent state lives in kernel dm devices, target tables, target-private metadata, device numbers, UUIDs, and udev-visible events, not in this header. The ABI depends on `<linux/types.h>`, Linux ioctl encoding, `dm-ioctl.c:lookup_ioctl()` command ordering, and userspace tools such as `dmsetup`, LVM, multipath, cryptsetup, and initramfs storage assembly.

Risks and test signals: Risks center on packed variable-length buffers, 32/64-bit layout stability, offset alignment for `dm_target_spec` and `dm_name_list`, stale UUID/name ambiguity, event cookie misuse, sensitive target parameters not using `DM_SECURE_DATA_FLAG`, and tools assuming old version values. Tests should cover version negotiation, too-small buffers setting `DM_BUFFER_FULL_FLAG`, table load/status round trips, inactive-table querying, deferred removal behavior, uevent cookie propagation, target message in/out data, and compatibility of `DM_VERSION_MAJOR/MINOR/PATCHLEVEL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/dm-ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/dm-log-userspace.h -->
## sources/distributed-fs/ceph-client/include/uapi/linux/dm-log-userspace.h

Purpose: This header defines the netlink connector protocol between the device-mapper userspace dirty log target and a userspace daemon. It mirrors callbacks from `dm-dirty-log.h` into request types that userspace receives, processes, and returns to the kernel.

Important APIs and types: `DM_ULOG_CTR` through `DM_ULOG_IS_REMOTE_RECOVERING` encode constructor, destructor, suspend/resume, region size, region cleanliness, sync state, flush, mark/clear region, resync work selection, sync count, status, and remote recovery queries. `DM_ULOG_REQUEST_MASK` and `DM_ULOG_REQUEST_TYPE()` reserve low 8 bits for request IDs while leaving upper bits for future compatibility. `DM_ULOG_REQUEST_VERSION` is currently 3, adding constructor log-device returns and integrated flush payloads. `struct dm_ulog_request` carries a local unique ID, dm UUID, version, error result, sequence number, request type, data size, and flexible payload.

Control flow and state: Userspace opens a `NETLINK_CONNECTOR` socket, joins `CN_IDX_DM`, then loops receiving `struct dm_ulog_request` plus optional payload and returning the same request with `error` and response payload filled. The constructor establishes a UUID/luid association and may return a backing log device name. Region operations send or receive `__u64` region identifiers and `__s64` boolean-like results. Integrated flush can bundle region marks into a flush request to reduce round trips.

Persistence and dependencies: Persistent dirty-log state is intentionally outside the kernel target when this module is used; the daemon owns region dirty/sync state and any backing store. The ABI depends on `<linux/types.h>`, `DM_UUID_LEN` from `dm-ioctl.h`, connector netlink membership, and the kernel dm userspace log implementation.

Integration points: It is consumed by clustered mirroring or replication stacks that need a user-managed dirty log. The protocol integrates with dm table constructor arguments, `dm_get_device()` for an optional log device, suspend/resume ordering, and target status output.

Risks and test signals: Risks include lost or reordered netlink messages, mismatched sequence IDs, daemon crashes holding authoritative log state, version skew, incorrect `data_size`, UUID/luid collisions when live and inactive tables overlap, and ambiguous signed integer boolean payloads. Tests should simulate each request type, validate payload sizes for scalar and array operations, exercise integrated flush, verify constructor/destroy device reference behavior, confirm error propagation, and cover daemon restart or timeout handling in the kernel component.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/dm-log-userspace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/dma-buf.h -->
## sources/distributed-fs/ceph-client/include/uapi/linux/dma-buf.h

Purpose: This UAPI header defines ioctl structures for dma-buf file descriptors shared across devices and subsystems. It covers CPU cache synchronization, naming, and explicit/implicit synchronization interop through `sync_file` export and import.

Important APIs and types: `struct dma_buf_sync` contains `flags` combining `DMA_BUF_SYNC_START` or `DMA_BUF_SYNC_END` with read/write intent. `struct dma_buf_export_sync_file` returns a sync-file fd for current dma-buf fences. `struct dma_buf_import_sync_file` imports a sync-file fd as a read or write fence on a dma-buf. Ioctls are `DMA_BUF_IOCTL_SYNC`, `DMA_BUF_SET_NAME` plus Android-compatible `_A` and `_B` encodings, `DMA_BUF_IOCTL_EXPORT_SYNC_FILE`, and `DMA_BUF_IOCTL_IMPORT_SYNC_FILE`.

Control flow and state: For CPU mmap access, userspace brackets access with START and END using matching read/write flags so the kernel can maintain cache coherency. For explicit synchronization interop, userspace snapshots current implicit fences with EXPORT, schedules device work that waits on the returned sync file, then IMPORTs completion fences back into the dma-buf so implicit consumers see ordering. This is not atomic across export, work submission, and import; userspace must serialize against other contexts if strict ordering is required.

Persistence and dependencies: The persistent object is the dma-buf file and its attached reservation/fence state. The header depends on `<linux/ioctl.h>` and `<linux/types.h>`. Consumers include DRM, V4L2, media, GPU, display, Android graphics, and any dma-buf heap allocator user.

Integration points: Polling on dma-buf fds provides implicit sync waits. Export/import sync-file bridges explicit APIs such as Vulkan with implicit dma-buf users such as many media and OpenGL paths.

Risks and test signals: Risks include forgetting CPU sync brackets, assuming cache sync also prevents concurrent device access, using invalid flag combinations, fd leaks from sync-file export, Android ioctl number compatibility, and races between export and import. Tests should validate accepted flag masks, CPU mmap coherency on noncoherent platforms, poll equivalence for read/write fences, import visibility to later implicit consumers, rejected invalid flags/fds, and behavior across 32-bit and 64-bit userspace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/dma-buf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/dma-heap.h -->
## sources/distributed-fs/ceph-client/include/uapi/linux/dma-heap.h

Purpose: This header defines the dma-buf heaps userspace allocation ABI. A heap device accepts an allocation request and returns a dma-buf file descriptor for memory from that heap.

Important APIs and types: `DMA_HEAP_VALID_FD_FLAGS` allows `O_CLOEXEC` and access-mode bits. `DMA_HEAP_VALID_HEAP_FLAGS` is currently zero, so heap-specific flags are not exposed here. `struct dma_heap_allocation_data` carries requested `len`, returned `fd`, `fd_flags`, and `heap_flags`. `DMA_HEAP_IOCTL_ALLOC` is the only ioctl in this header.

Control flow and state: Userspace opens a heap node, populates allocation data, calls `DMA_HEAP_IOCTL_ALLOC`, and receives a dma-buf fd in `fd`. Subsequent sharing, mmap, sync, and fencing use the dma-buf ABI, not this heap ABI. The heap object itself manages backing pages and lifetime through the returned file descriptor.

Persistence and dependencies: There is no on-disk persistence. Allocations persist while the returned dma-buf fd or its duplicates/imports are referenced. The header depends on Linux ioctl and type definitions and assumes open flags are visible through included userspace headers.

Integration points: This ABI feeds dma-buf consumers such as DRM, V4L2, camera, display, codecs, and userspace graphics pipelines. It is the replacement for older Android ion allocation patterns.

Risks and test signals: Risks include accepting unsupported heap flags, integer overflow or truncation in `len`, failing to set close-on-exec for sensitive buffers, assuming heap names imply security properties, and mismatched access mode expectations. Tests should cover zero and non-page-aligned lengths, invalid `fd_flags`/`heap_flags`, successful fd close-on-exec behavior, mmap and dma-buf sync through `dma-buf.h`, and allocation failure under memory pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/dma-heap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/dns_resolver.h -->
## sources/distributed-fs/ceph-client/include/uapi/linux/dns_resolver.h

Purpose: This header defines the binary payload layout for the kernel DNS resolver key type, especially server-list payloads requested with `srv=1`. It gives userspace resolvers and kernel clients a compact typed format for DNS-derived service records.

Important APIs and types: Enums describe content type, address type, server transport protocol, record source, and lookup status. `struct dns_payload_header` marks a binary payload with a leading zero, content type, and version. `struct dns_server_list_v1_header` adds source, status, and server count. `struct dns_server_list_v1_server` stores name length, SRV priority/weight/port, source/status/protocol, and address count. `struct dns_server_list_v1_address` prefixes variable address bytes as IPv4 or IPv6.

Control flow and state: A resolver produces a payload beginning with a binary header, followed by a v1 server-list header, then repeated server records. Each server record is immediately followed by a non-NUL-terminated name and then address records. Kernel clients parse counts and lengths to locate variable records.

Persistence and dependencies: Payloads are stored in kernel keyring DNS resolver keys and expire according to key/resolver policy outside this header. The ABI depends only on `<linux/types.h>` and uses packed structs, so byte layout is part of the contract.

Integration points: It is relevant to kernel subsystems that perform upcalls for DNS names, including distributed filesystems and network filesystems that need service discovery. Userspace helpers such as keyutils resolvers must encode exactly this format.

Risks and test signals: Risks include malformed length/count fields, endian assumptions for little-endian annotated fields in comments, non-NUL names, unsupported future versions, empty records with failure status, and distinguishing local config/NSS/DNS/SRV sources. Tests should parse mixed IPv4/IPv6 records, bad lengths, zero-server failures, partial decoding statuses, unsupported content or version values, and resolver cache refresh behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/dns_resolver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/dpll.h -->
## sources/distributed-fs/ceph-client/include/uapi/linux/dpll.h

Purpose: This generated UAPI header defines the generic-netlink family contract for Digital Phase Locked Loop devices and pins. It exposes clock selection, lock status, quality, phase/frequency monitoring, and pin control for synchronization hardware.

Important APIs and types: The family is `DPLL_FAMILY_NAME` `"dpll"` version 1 with monitor multicast group `DPLL_MCGRP_MONITOR`. Device enums cover mode, lock status, lock-status error, clock quality, type, and device attributes `DPLL_A_*`. Pin enums cover type, direction, state, capabilities, supported frequencies, phase adjustment, fractional frequency offset, embedded sync, reference sync, and measured frequency through `DPLL_A_PIN_*`. Commands include device id/get/set/create/delete/change notifications and pin id/get/set/create/delete/change notifications.

Control flow and state: Userspace queries device or pin IDs, gets attributes, and sends set commands for mutable fields such as mode, pin state, priority, direction, phase adjust, or monitor toggles where supported. Drivers publish notifications for device and pin lifecycle and changes. Lock status transitions from unlocked to locked, locked with holdover acquired, or holdover based on input signal availability and hardware state.

Persistence and dependencies: Runtime state is held in synchronization hardware and kernel dpll objects, not persisted by this header. It is auto-generated from `Documentation/netlink/specs/dpll.yaml`, so source-of-truth changes should regenerate it via `tools/net/ynl/ynl-regen.sh`.

Integration points: DPLL integrates with NICs, SyncE, GNSS, PPS, telecom timing, PTP-adjacent clock infrastructure, and netlink YNL tooling. Pin types identify external, SyncE Ethernet port, internal oscillator, GNSS, and mux pins.

Risks and test signals: Risks include manual edits being overwritten, enum value stability, unsupported mutable attributes, misreported units using dividers for temperature/phase/frequency, and racey notifications. Tests should validate YNL spec regeneration, netlink policy for each attribute, get/set permission failures, notification delivery, lock-status error reporting, and driver conformance for pin capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/dpll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/dqblk_xfs.h -->
## sources/distributed-fs/ceph-client/include/uapi/linux/dqblk_xfs.h

Purpose: This header defines XFS quota-manager commands and data structures used with `quotactl(2)`. It covers user, group, and project quota accounting, enforcement, limits, usage, timers, warnings, and quota subsystem status.

Important APIs and types: `XQM_CMD()` builds XFS-specific quota commands such as `Q_XQUOTAON`, `Q_XQUOTAOFF`, `Q_XGETQUOTA`, `Q_XSETQLIM`, `Q_XGETQSTAT`, `Q_XQUOTARM`, `Q_XQUOTASYNC`, `Q_XGETQSTATV`, and `Q_XGETNEXTQUOTA`. `fs_disk_quota_t` stores per-ID hard/soft block, inode, and realtime block limits and usage, warning counts, timers, 40-bit bigtime timer extension bytes, flags, ID, and field mask. Field masks distinguish limit, timer, warning, and accounting updates. `fs_quota_stat_t` and `struct fs_quota_statv` report global quota file/storage and default timer/warning status, with `statv` adding versioning and project quota fields.

Control flow and state: Userspace enables quota accounting/enforcement, reads or sets per-ID limits using field masks, syncs delayed allocation quota updates, removes quota storage, and iterates quota records at or after a given ID. For non-superuser dquots, timers are started/stopped by quota state changes; superuser dquot timer and warning fields act as defaults.

Persistence and dependencies: Quota state persists in XFS quota metadata and in-core dquot caches. Units for block fields are 512-byte basic blocks. The ABI depends on `<linux/types.h>` and `quotactl` command encoding.

Integration points: It integrates with XFS, generic quota tools, project quota administration, and filesystem repair/check tooling.

Risks and test signals: Risks include BB versus filesystem-block unit confusion, signed 40-bit timer encoding, partial updates with incorrect `d_fieldmask`, version fallback for `Q_XGETQSTATV`, and non-transactional accounting field writes. Tests should cover user/group/project quota types, soft-limit timer start/expiry, warning count changes, bigtime timestamps, `Q_XGETNEXTQUOTA` iteration gaps, unsupported statv versions returning `EINVAL`, and sync/removal interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/dqblk_xfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/dvb/audio.h -->
## sources/distributed-fs/ceph-client/include/uapi/linux/dvb/audio.h

Purpose: This deprecated DVB MPEG-TS audio decoder UAPI describes legacy decoder control ioctls. It remains for compatibility but should not be used by new drivers.

Important APIs and types: Enums define audio source (`AUDIO_SOURCE_DEMUX` or memory), play state, and channel selection. `audio_mixer_t` stores left/right volumes. `audio_status_t` reports AV sync, mute, play state, source, channel, bypass mode, and mixer state. Capability bits include DTS, LPCM, MPEG audio layers, AAC, OGG, SDDS, and AC3. Ioctls cover stop, play, pause, continue, source selection, mute, AV sync, bypass, channel selection, status, capabilities, buffer clear, stream ID/type, mixer, and bilingual channel selection.

Control flow and state: Userspace configures source and format, starts playback, pauses/resumes/stops, adjusts mute/mixer/channel state, and queries status. Decoder state is maintained by the underlying DVB audio device and may be coupled to demux and video synchronization.

Persistence and dependencies: State is runtime-only in decoder hardware/driver. The header depends on `<linux/types.h>` and the shared DVB ioctl magic `'o'`.

Integration points: It connects to DVB demux output (`AUDIO_SOURCE_DEMUX`), memory-fed playback, AV synchronization with video decoders, and legacy set-top-box hardware.

Risks and test signals: Risks include deprecated API use in new code, ambiguous `_IO` arguments for setters, codec capability mismatch, audio/video sync drift, and hardware-specific bypass semantics. Tests should cover state transitions, status reflection, unsupported capability rejection, demux versus memory source switching, mute/mixer effects, and coexistence with video decoder ioctls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/dvb/audio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/dvb/ca.h -->
## sources/distributed-fs/ceph-client/include/uapi/linux/dvb/ca.h

Purpose: This DVB conditional-access UAPI exposes Common Interface slots, descrambler capabilities, CAM messaging, and descrambler control-word programming.

Important APIs and types: `struct ca_slot_info` describes slot number, type (`CA_CI`, `CA_CI_LINK`, `CA_CI_PHYS`, `CA_DESCR`, `CA_SC`) and flags for module present/ready. `struct ca_descr_info` reports descrambler count and type (`CA_ECD`, `CA_NDS`, `CA_DSS`). `struct ca_caps` reports aggregate slot and descrambler capabilities. `struct ca_msg` carries up to 256 bytes to or from a CI CAM. `struct ca_descr` carries an 8-byte control word for a descrambler slot and parity. Ioctls reset, get capabilities, get slot/descrambler info, get/send CAM messages, and set descrambler words.

Control flow and state: Applications query CA capabilities and slot readiness, exchange messages with CAM modules, and program control words for descrambling. Slot insertion/readiness and descrambler key state persist in the driver/hardware until changed, reset, or removed.

Persistence and dependencies: Runtime state lives in CAM hardware, smart cards, and descrambler slots. No durable state is defined. Legacy userspace typedefs are provided outside `__KERNEL__`.

Integration points: CA is used with DVB demux and decoder pipelines to descramble protected MPEG-TS streams. CAM message protocols sit above this raw transport structure.

Risks and test signals: Risks include control-word sensitivity, insufficient bounds checking on `length`, parity slot confusion, slot hotplug races, and legal/security constraints around descrambling. Tests should cover slot presence/ready transitions, cap reporting, max-length message send/receive, invalid descrambler indices, reset effects, and key clearing behavior during module removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/dvb/ca.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/dvb/dmx.h -->
## sources/distributed-fs/ceph-client/include/uapi/linux/dvb/dmx.h

Purpose: This header defines the DVB demux UAPI for MPEG transport stream section/PES filtering, PID management, STC reads, and streaming buffers including mmap and DMABUF export.

Important APIs and types: `enum dmx_output`, `enum dmx_input`, and `enum dmx_ts_pes` select data routing, source, and PES class. `struct dmx_filter` and `struct dmx_sct_filter_params` describe 16-byte section header filters, masks, modes, PID, timeout, and flags such as CRC checking, one-shot, and immediate start. `struct dmx_pes_filter_params` configures PES filtering. `struct dmx_stc` returns system time counter data. `struct dmx_buffer`, `struct dmx_requestbuffers`, and `struct dmx_exportbuffer` define streaming buffer queue, mmap offset/cookie, status flags, counters, and DMABUF export fd.

Control flow and state: Userspace sets a section or PES filter, optionally starts it immediately or via `DMX_START`, reads filtered data or uses buffer queue ioctls, then stops/removes PIDs. `DMX_OUT_TS_TAP` routes selected filters into the logical DVR device, while `DMX_OUT_TSDEMUX_TAP` exposes transport stream data through the demux device. Buffer lifecycle follows request, query, queue, dequeue, and optional export.

Persistence and dependencies: Filter state, PID subscriptions, buffer mappings, and counters live in the demux driver until stop, close, or reconfiguration. The header depends on `<linux/types.h>` and includes `<time.h>` for non-kernel legacy compatibility.

Integration points: It integrates with DVB frontend tuning, DVR devices, audio/video decoders, network encapsulation, and dma-buf consumers.

Risks and test signals: Risks include filter mask/mode mistakes, PID leaks, CRC discard handling, TS continuity errors, buffer counter wrap, mmap offset misuse, and DMABUF fd ownership. Tests should cover section and PES filter setup, immediate and explicit start, timeout and one-shot behavior, multi-PID add/remove, STC reads, buffer queue underflow/overflow, flag reporting for TEI/discontinuity/CRC, and DVR routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/dvb/dmx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/dvb/frontend.h -->
## sources/distributed-fs/ceph-client/include/uapi/linux/dvb/frontend.h

Purpose: This header defines the DVB frontend tuning and status ABI. It covers frontend capabilities, DiSEqC/LNB control, signal status, DVBv5 property arrays, statistics, and deprecated DVBv3 tuning structures.

Important APIs and types: `enum fe_caps` reports modulation, FEC, inversion, auto-detection, multistream, second-generation modulation, recovery, and TS muting support. `struct dvb_frontend_info` reports name, frequency/symbol-rate ranges, and caps, with deprecated single frontend type. DiSEqC structures carry master commands and slave replies. Enums define voltage, tone, mini-burst, lock status, inversion, FEC, modulation, transmission mode, guard interval, hierarchy, interleaving, pilot, rolloff, and delivery system. DVBv5 properties are carried by `struct dtv_property` and `struct dtv_properties`, with commands from `DTV_FREQUENCY` through `DTV_STAT_*` and `DTV_ENUM_DELSYS`. `struct dtv_fe_stats` stores up to four scaled stats.

Control flow and state: Modern userspace queries `FE_GET_INFO` and `DTV_ENUM_DELSYS`, sets a batch of DVBv5 properties with `FE_SET_PROPERTY`, triggers tune with `DTV_TUNE`, and monitors `FE_READ_STATUS`, `FE_GET_EVENT`, and quality stats. Satellite flows also set LNB voltage/tone and send DiSEqC commands. `FE_TUNE_MODE_ONESHOT` disables normal zigzag tuning and event monitoring until reopened read-write.

Persistence and dependencies: Tuning parameters, DiSEqC/tone/voltage, and frontend state live in tuner/demod hardware and the kernel frontend device. The header depends on `<linux/types.h>`.

Integration points: It drives demux input: a locked frontend supplies MPEG-TS PIDs to `dvb/dmx.h`, then audio/video/net/CA layers consume streams. It also integrates with libdvbv5 and legacy DVBv3 applications.

Risks and test signals: Risks include mixed DVBv3/DVBv5 usage, unit differences for satellite frequency, unsupported property combinations, packed struct ABI, stats scale interpretation, and auto-detection fallback behavior. Tests should tune representative DVB-S/S2, DVB-T/T2, DVB-C, ATSC, ISDB, and DTMB configurations; validate `DTV_IOCTL_MAX_MSGS`; read layered stats; test DiSEqC timeouts; verify event generation; and confirm deprecated ioctls remain compatible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/dvb/frontend.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/dvb/net.h -->
## sources/distributed-fs/ceph-client/include/uapi/linux/dvb/net.h

Purpose: This header defines the DVB network interface ABI for exposing IP packets carried inside MPEG-TS PIDs as Linux network interfaces.

Important APIs and types: `struct dvb_net_if` carries a transport stream PID, returned interface number, and feed type. Feed types are MPE and ULE. Ioctls are `NET_ADD_IF`, `NET_REMOVE_IF`, and `NET_GET_IF`. An old two-field `__dvb_net_if_old` and old ioctl aliases are kept for binary compatibility.

Control flow and state: Userspace requests an interface for a PID and encapsulation type, receives or identifies an interface number, and later removes it. The kernel demux/network stack extracts datagrams from the selected MPEG-TS PID and presents them as a netdev.

Persistence and dependencies: Interfaces are runtime kernel netdev objects and disappear on removal, device close, driver unload, or adapter removal. The header depends on `<linux/types.h>` and the DVB ioctl magic.

Integration points: It sits on top of frontend tuning and demux PID filtering, then feeds the normal Linux networking stack. It is used for DVB data broadcast and satellite/cable IP delivery.

Risks and test signals: Risks include PID conflicts, feedtype mismatch, legacy ioctl layout compatibility, interface lifecycle leaks, and demux errors surfacing as packet loss. Tests should add/get/remove MPE and ULE interfaces, verify netdev naming and teardown, exercise the old two-field ABI, and validate behavior when frontend lock is lost or PID carries malformed encapsulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/dvb/net.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/dvb/osd.h -->
## sources/distributed-fs/ceph-client/include/uapi/linux/dvb/osd.h

Purpose: This deprecated DVB on-screen-display UAPI defines commands for old decoder hardware OSD planes, palettes, drawing primitives, text, windows, and capability queries. New drivers should not adopt it.

Important APIs and types: `OSD_Command` enumerates close/open/show/hide/clear/fill, palette and transparency changes, pixel/row/block operations, line drawing, query, test, text, window selection/move, and raw window open. `osd_cmd_t` carries command, coordinates, color/inc fields, and a userspace data pointer. `osd_raw_window_t` names bitmap, YCrCb, video-size, and cursor raw window modes. `osd_cap_t` reports capabilities such as memory size. Ioctls are `OSD_SEND_CMD` and `OSD_GET_CAPABILITY`.

Control flow and state: Applications open an OSD window with geometry and bit depth, populate palette/graphics, show or hide it, perform drawing commands, then close it. The hardware maintains window buffers, current window selection, palette, transparency, and visibility.

Persistence and dependencies: All state is runtime device state. The header depends on `<linux/compiler.h>` for `__user` pointer annotation.

Integration points: OSD overlays video decoder output in legacy DVB adapters and set-top-box designs. It may interact with video plane sizing and decoder display mode.

Risks and test signals: Risks include deprecated API exposure, unsafe userspace pointers, coordinate clipping, palette opacity interpretation, hardware memory exhaustion, and command-specific overloading of integer fields. Tests should cover open/close error codes, clipping, palette ranges, data pointer copy sizes for rows/blocks/text, multi-window behavior, capability reporting, and hide/show interactions with video output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/dvb/osd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/dvb/version.h -->
## sources/distributed-fs/ceph-client/include/uapi/linux/dvb/version.h

Purpose: This small header declares the DVB API version exposed by the kernel UAPI.

Important APIs and types: It defines `DVB_API_VERSION` as 5 and `DVB_API_VERSION_MINOR` as 12. There are no structs, functions, or ioctls.

Control flow and state: There is no runtime control flow. Userspace can compile-time or runtime-gated logic against these constants when checking DVB API availability.

Persistence and dependencies: No state or dependencies beyond the header guard.

Integration points: DVB applications and libraries use this with the rest of `linux/dvb/*` to reason about feature availability, especially DVBv5 properties.

Risks and test signals: Risks are mostly version skew and userspace assuming that a numeric version guarantees every driver supports every optional feature. Tests should verify that build environments expose the expected constants and that feature probing still uses actual ioctls such as `FE_GET_PROPERTY` and `DTV_ENUM_DELSYS` rather than version checks alone.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/dvb/version.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/dvb/video.h -->
## sources/distributed-fs/ceph-client/include/uapi/linux/dvb/video.h

Purpose: This deprecated DVB MPEG-TS video decoder UAPI controls legacy video decoder playback, still pictures, display format, events, status, PTS/frame counters, and extended commands.

Important APIs and types: Enums define aspect ratio, display format, source, and play state. `struct video_command` supports play/stop/freeze/continue with flags, PTS, speed, format, and raw extension data. `struct video_event` reports size, frame rate, decoder stopped, and vsync events. `struct video_status`, `struct video_still_picture`, `video_attributes_t`, and capability bits describe decoder state, still iframe injection, MPEG stream attributes, and supported features. Ioctls cover playback control, source/display/blank settings, status/event reads, still picture, speed controls, capabilities, buffer clear, stream type/format, size, PTS, frame count, and try/apply command.

Control flow and state: Userspace selects source, configures display behavior, starts playback, handles events, freezes/stops/continues, and queries timestamps and frame counters. `VIDEO_TRY_COMMAND` lets userspace validate a command before applying with `VIDEO_COMMAND`.

Persistence and dependencies: State is runtime decoder hardware/driver state. The header depends on `<linux/types.h>` and `<time.h>` outside kernel builds. User pointers appear in still-picture submission.

Integration points: It consumes demux or memory-fed streams and coordinates with audio AV sync, OSD overlays, and DVB frontend/demux pipelines.

Risks and test signals: Risks include deprecated API usage, userspace pointer copy bugs, timestamp width/meaning differences, event timestamp Y2038 note, speed control variance, and coupling to audio sync. Tests should cover play/stop/freeze/continue state, command validation, PTS/frame-count monotonicity, event delivery for size/vsync/stop, still picture bounds, and unsupported capability handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/dvb/video.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/dw100.h -->
## sources/distributed-fs/ceph-client/include/uapi/linux/dw100.h

Purpose: This header defines the V4L2 private control ID for the NXP DW100 dewarping engine.

Important APIs and types: It includes `<linux/v4l2-controls.h>` and defines `V4L2_CID_DW100_DEWARPING_16x16_VERTEX_MAP` as `V4L2_CID_USER_DW100_BASE + 1`. The referenced control configures a 16 by 16 vertex map; detailed semantics are delegated to `Documentation/userspace-api/media/drivers/dw100.rst`.

Control flow and state: Userspace controls DW100 through normal V4L2 control get/set flows. This header only allocates the control ID.

Persistence and dependencies: Runtime state lives in the V4L2 subdevice or mem2mem driver control handler. The ID depends on the DW100 user-control base from V4L2 controls.

Integration points: It integrates with media pipelines that use DW100 for geometric dewarping, typically camera or image-processing flows.

Risks and test signals: Risks include mismatched vertex-map size or element layout, documentation/header drift, and collision if controls are added without using the assigned base. Tests should query the control, validate payload size and type, set identity and distorted maps, run a frame through the pipeline, and verify older userspace fails cleanly when the control is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/dw100.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/edd.h -->
## sources/distributed-fs/ceph-client/include/uapi/linux/edd.h

Purpose: This header defines BIOS Enhanced Disk Drive data structures used to pass INT 13h boot disk information from early x86 boot code into the kernel and userspace-visible firmware interfaces.

Important APIs and types: Constants define boot parameter offsets (`EDDNR`, `EDDBUF`, MBR signature buffers), maximum record counts, BIOS function numbers, magic values, and flags. `struct edd_device_params` is a packed representation of EDD device parameters, including geometry, sector count, bytes per sector, host bus/interface type, interface path union, device path union, checksum, and reserved fields. `struct edd_info` adds BIOS device number, version, interface support, legacy geometry, and params. `struct edd` groups MBR signatures and up to `EDDMAXNR` EDD records.

Control flow and state: Early setup code gathers BIOS EDD data into boot parameters, kernel setup copies it into EDD structures, and firmware code uses it to identify the BIOS boot disk. The header itself has no functions, but its packed layout is consumed by assembly and firmware code, making size and alignment critical.

Persistence and dependencies: EDD data is boot-time firmware state, not persistent kernel state. The header depends on `<linux/types.h>` and excludes C structs for assembly builds.

Integration points: It integrates with x86 boot setup, firmware/edd driver code, disk identification, MBR signatures, and bootloader/kernel handoff.

Risks and test signals: Risks include changing packed structure sizes, BIOS-provided malformed checksums, truncation to six EDD records or sixteen MBR signatures, legacy geometry mismatch, and host/device path union interpretation. Tests should compare structure sizes to `EDDEXTSIZE` and `EDDPARMSIZE` expectations, boot with BIOS EDD-enabled devices, validate checksum handling, confirm sysfs/firmware output, and cover systems with no EDD support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/edd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/efs_fs_sb.h -->
## sources/distributed-fs/ceph-client/include/uapi/linux/efs_fs_sb.h

Purpose: This header describes SGI EFS filesystem superblock values and in-memory summary fields. It supports parsing and mounting legacy IRIX EFS volumes.

Important APIs and types: `EFS_MAGIC`, `EFS_NEWMAGIC`, and `IS_EFS_MAGIC()` identify supported superblock magic values. `EFS_SUPER` and `EFS_ROOTINODE` define key filesystem locations. `struct efs_super` models the big-endian on-disk superblock with filesystem size, cylinder group layout, geometry, dirty flag, update time, names, bitmap location/size, free block/inode counters, replicated superblock, last inode allocation, expansion space, and checksum. `struct efs_sb_info` stores normalized in-memory mount information.

Control flow and state: Mount code reads the on-disk superblock, validates magic and checksum, converts big-endian fields, computes group and inode layout, then fills `efs_sb_info`. Runtime free counters and dirty state reflect filesystem metadata handling outside this header.

Persistence and dependencies: `struct efs_super` is persistent disk format. `struct efs_sb_info` is kernel memory state. The header depends on `<linux/types.h>` and `<linux/magic.h>`.

Integration points: It integrates with the EFS filesystem driver, block device reads, VFS mount code, and filesystem checking tools.

Risks and test signals: Risks include endian conversion mistakes, accepting invalid magic or checksum, dirty filesystem handling, reserved bytes not zero, and overflow from legacy geometry fields. Tests should mount known EFS images, reject corrupted magic/checksum, validate root inode lookup, compare free counters, and test big-endian field parsing on little-endian hosts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/efs_fs_sb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/elf-em.h -->
## sources/distributed-fs/ceph-client/include/uapi/linux/elf-em.h

Purpose: This header defines ELF `e_machine` constants recognized by Linux UAPI. It centralizes machine IDs for architecture detection in loaders, core tooling, binfmt code, and userspace parsers.

Important APIs and types: It provides `EM_*` macros for many architectures, including x86, ARM, AArch64, MIPS, PowerPC, S390, RISC-V, BPF, C-SKY, LoongArch, FR-V, Alpha interim value, and historical aliases such as old S390 and Cygnus IDs. There are no structs or functions.

Control flow and state: There is no runtime state. ELF loaders and parsers compare an ELF header's `e_machine` against these constants to select architecture-specific validation, relocation, register note, or execution paths.

Persistence and dependencies: The constants are part of persistent ELF file format interpretation. The header has no includes beyond its guard.

Integration points: It is included by `linux/elf.h` and consumed by binfmt loaders, debuggers, crash dump readers, module loaders, and cross-toolchain code.

Risks and test signals: Risks include duplicate/historical values such as MIPS RS3/RS4, interim IDs that differ from final standards, rejecting legacy binaries, and adding new architecture IDs without coordinating parsers. Tests should parse ELF headers for supported architectures, ensure unknown IDs are rejected where appropriate, verify BPF and LoongArch values, and check old aliases remain compatible with intended policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/elf-em.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/elf-fdpic.h -->
## sources/distributed-fs/ceph-client/include/uapi/linux/elf-fdpic.h

Purpose: This header defines load-map structures for FDPIC ELF executables, libraries, and interpreters. FDPIC supports position-independent execution on systems without a traditional MMU.

Important APIs and types: It includes `linux/elf.h`, defines `PT_GNU_STACK` using the OS-specific program-header range, and declares 32-bit and 64-bit FDPIC load segment and load map structures. Each load segment records mapped core address, file virtual address, and memory size. Load maps carry a version, segment count, and flexible segment array. Both version constants are zero.

Control flow and state: During exec or dynamic loading, the loader maps each segment and records the mapping in an FDPIC load map so runtime code can translate between file VMAs and actual addresses. The header only defines the ABI structures.

Persistence and dependencies: Load maps are runtime process metadata. The persistent input is the ELF/FDPIC file. The header depends on ELF base types and program-header constants.

Integration points: It integrates with architecture-specific FDPIC binfmt support, dynamic loaders, debuggers, and core-dump tooling on FDPIC-capable architectures.

Risks and test signals: Risks include flexible-array sizing errors, 32/64-bit mismatch, version handling, duplicate `PT_GNU_STACK` definition consistency with `elf.h`, and incorrect address translation. Tests should execute FDPIC binaries with multiple segments, inspect load maps, validate core/debugger interpretation, and cover empty or malformed segment counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/elf-fdpic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/elf.h -->
## sources/distributed-fs/ceph-client/include/uapi/linux/elf.h

Purpose: This header defines Linux ELF base types, file/program/section/dynamic/symbol/relocation structures, magic values, note types, and GNU property constants for userspace and kernel consumers.

Important APIs and types: It declares 32-bit and 64-bit ELF scalar typedefs; program header types (`PT_LOAD`, `PT_DYNAMIC`, `PT_TLS`, GNU stack/relro/property, AArch64 MTE); file types; dynamic tags; symbol bindings/types; relocation macros and structs; symbol structs; ELF headers; program headers; section headers; identification indexes and magic; OS ABI values; note names and note type IDs for core dumps and ptrace regsets; GNU AArch64 BTI property; and version definition auxiliary structs.

Control flow and state: There are no executable functions, but these structures drive ELF loading, dynamic linking, relocation, core-dump generation, ptrace register set exchange, and debugger parsing. Extended program-header numbering uses `PN_XNUM` with section header zero to carry real counts when values exceed 16-bit fields.

Persistence and dependencies: Most structures are persistent on-disk ELF ABI. Note structures also define core dump and ptrace data exchange. The header depends on `<linux/types.h>` and `linux/elf-em.h`.

Integration points: It is central to `binfmt_elf`, module/toolchain parsers, crash dump readers, debuggers, loaders, architecture regset exports, livepatch section flags, and security features such as GNU property notes.

Risks and test signals: Risks include ABI layout changes, endian/class confusion, extended numbering bugs, note-size assumptions despite warnings, architecture note ID collisions, and parser trust in unvalidated offsets/sizes. Tests should parse 32/64-bit little/big-endian ELFs, extended header counts, PT_GNU_STACK/RELRO/property handling, relocation macros, core notes for supported architectures, malformed section/program tables, and compatibility with binutils/gdb expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/elf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/errno.h -->
## sources/distributed-fs/ceph-client/include/uapi/linux/errno.h

Purpose: This header forwards Linux UAPI errno definitions to the architecture-specific `<asm/errno.h>`.

Important APIs and types: It has a single include and defines no local constants, structs, or functions. The effective API is the errno namespace supplied by the target architecture.

Control flow and state: There is no control flow or state. Build preprocessing resolves errno values through the asm include path.

Persistence and dependencies: It depends entirely on architecture UAPI errno headers. Errno values are part of syscall ABI and userspace error handling conventions.

Integration points: Any UAPI header or userspace program including `<linux/errno.h>` receives the architecture errno constants used by syscall return translation, libc, and kernel/userspace interfaces.

Risks and test signals: Risks include include-path misconfiguration, architecture errno differences, and code assuming this file itself enumerates values. Tests should preprocess the header for each target architecture, verify common errno constants are visible, and ensure generated UAPI include sets resolve `<asm/errno.h>` correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/errno.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/errqueue.h -->
## sources/distributed-fs/ceph-client/include/uapi/linux/errqueue.h

Purpose: This header defines ancillary data structures for socket error queues, including extended errors, RFC 4884 data, zero-copy and txtime status, and timestamping control messages.

Important APIs and types: `struct sock_ee_data_rfc4884` carries extension length and flags. `struct sock_extended_err` carries errno, origin, type, code, info, and data or RFC4884 metadata. Origins include local, ICMP, ICMPv6, TX status/timestamping, zero-copy, and txtime. `SO_EE_OFFENDER()` locates the following offender sockaddr. `struct scm_timestamping` and `struct scm_timestamping64` expose three timestamps for socket timestamping, with kernel/userspace timespec layout handling. The timestamp type enum distinguishes send, scheduler, ACK, and completion timestamps.

Control flow and state: Network stack code queues extended errors or timestamp completions on a socket error queue. Userspace receives them with `recvmsg(MSG_ERRQUEUE)` and parses cmsgs into these structures. The values describe asynchronous status for earlier sends or network errors.

Persistence and dependencies: State is per-socket queued ancillary data. The header depends on `<linux/types.h>` and `<linux/time_types.h>`.

Integration points: It integrates with IP_RECVERR/IPV6_RECVERR, SO_TIMESTAMPING, MSG_ZEROCOPY, SO_TXTIME, ICMP diagnostics, and hardware/software timestamping.

Risks and test signals: Risks include old versus 64-bit timespec mismatch, assuming offender address is always present, treating timestamp origin incorrectly, missing zero-copy copied fallback, and RFC4884 extension validation. Tests should send packets that trigger ICMP errors, TX timestamps, zerocopy completions, and txtime failures; parse both timestamping structs; validate offender sockaddr alignment; and check origin/code-specific interpretation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/errqueue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/erspan.h -->
## sources/distributed-fs/ceph-client/include/uapi/linux/erspan.h

Purpose: This header defines ERSPAN tunnel metadata structures for userspace configuring metadata-mode ERSPAN tunnels.

Important APIs and types: `struct erspan_md2` models ERSPAN version 2/type III metadata with timestamp, security group tag, and bitfields for hardware ID, frame type, platform-specific flag, overflow, granularity, and direction. Bitfield order is selected based on little or big endian bitfield macros from `<asm/byteorder.h>`. `struct erspan_metadata` carries a version and a union of version 1 index or version 2 metadata.

Control flow and state: Userspace or tunnel code selects ERSPAN metadata version and supplies either a v1 index or v2 metadata. The kernel encapsulation path serializes these fields into ERSPAN headers; decapsulation can report them back depending on tunnel mode.

Persistence and dependencies: Metadata is per packet or per tunnel configuration runtime state. The header depends on `<linux/types.h>` for big-endian integer types and `<asm/byteorder.h>` for bitfield layout.

Integration points: It integrates with GRE/ERSPAN tunnel netdevices, tc, iproute2 tunnel configuration, and packet mirroring/monitoring systems.

Risks and test signals: Risks include bitfield endian mistakes, version/union mismatch, network byte-order confusion, and metadata loss through tooling. Tests should configure v1 and v2 metadata tunnels, inspect captured ERSPAN headers on little- and big-endian builds, validate direction/granularity/hwid fields, and reject unsupported versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/erspan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ethtool.h -->
## sources/distributed-fs/ceph-client/include/uapi/linux/ethtool.h

Purpose: This large UAPI header defines the legacy ioctl-facing ethtool ABI for querying and configuring Ethernet devices. It covers link modes, driver info, wake-on-LAN, EEPROM/register dumps, interrupt coalescing, ring/channel sizing, pause/EEE/FEC settings, RSS and flow steering, feature flags, timestamps, module data, firmware flashing/dumps, reset, PSE/PoE state enums, MAC merge status, and per-queue operations.

Important APIs and types: `struct ethtool_cmd` is deprecated link settings; `struct ethtool_link_settings` is the modern replacement with variable link-mode masks. Helper inlines get/set split speed in the old struct and validate speed/duplex. Core command structs include `ethtool_drvinfo`, `wolinfo`, `value`, `tunable`, `regs`, `eeprom`, `eee`, `modinfo`, `coalesce`, `ringparam`, `channels`, `pauseparam`, `gstrings`, `sset_info`, `test`, `stats`, `perm_addr`, RX flow specs, `rxnfc`, `rxfh_indir`, `rxfh`, flash/dump structs, feature get/set blocks, `ts_info`, `per_queue_op`, and `fecparam`. Command numbers run from `ETHTOOL_GSET`/`SSET` through `ETHTOOL_SFECPARAM`, with many older offload toggles now superseded by feature blocks. Link-mode bit indices extend up to 1.6T speeds and include FEC bits; legacy `SUPPORTED_*`/`ADVERTISED_*` macros are limited to the low 32 bits.

Control flow and state: Typical usage passes one of these structs through `SIOCETHTOOL`, with `cmd` selecting the operation. Many variable-length APIs use a probe-then-fetch pattern: query counts or sizes via driver info/string-set info/link-settings handshake, allocate enough trailing storage, then issue the real request. Set operations mutate driver, PHY, NIC, module, or queue state and are subject to validation. Link settings require read-modify-write; `GLINKSETTINGS` uses negative `link_mode_masks_nwords` to report the required bitmap size during handshake.

Persistence and dependencies: Most state is runtime device state; some settings may be saved by firmware or driver policy, but that is outside this ABI. EEPROM/module EEPROM and firmware flash touch persistent hardware storage. The header depends on const/type limits, Linux types, and Ethernet address definitions.

Integration points: It is consumed by the `ethtool` userspace utility, network drivers, PHYLIB, timestamping/PHC support, RSS/flow steering, module management, PoE/PSE, MAC merge/preemption, and netdev feature infrastructure. Newer generic-netlink ethtool APIs coexist with this ioctl ABI.

Risks and test signals: Risks include 32/64-bit layout stability, unzeroed reserved fields, variable trailing-buffer sizing, deprecated command use, link-mode bitmap length negotiation, legacy 32-bit masks truncating new speeds, driver-specific validation variance, EEPROM write hazards, firmware flash failure, RSS entropy reduction with symmetric transforms, and flow-rule priority conflicts. Tests should cover all probe/fetch variable-length APIs, old and new link setting fallback, invalid reserved fields, feature set return bits, RSS context allocate/delete, flow insert/delete/list, FEC autoneg interactions, coalescing invalid zero conditions, module EEPROM lengths, timestamp capability reporting, reset flags returning unreset components, and compatibility with 32-bit userspace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ethtool.h -->
