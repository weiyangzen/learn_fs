# subset-b-005996 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vfio.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/vfio.h

Purpose: defines the public Linux VFIO userspace ABI for safe-ish device assignment, including container/group/device file descriptor ioctls, device regions, IRQ delivery, PCI reset ownership, graphics planes, ioeventfd acceleration, iommufd cdev binding, device migration, dirty logging, Type1 IOMMU, SPAPR TCE, and POWER EEH operations.

Important APIs/types/functions: this header exports ioctl numbers rather than functions. Top-level ioctls are `VFIO_GET_API_VERSION`, `VFIO_CHECK_EXTENSION`, and `VFIO_SET_IOMMU`. Group ioctls include `VFIO_GROUP_GET_STATUS`, `VFIO_GROUP_SET_CONTAINER`, `VFIO_GROUP_UNSET_CONTAINER`, and `VFIO_GROUP_GET_DEVICE_FD`. Device ioctls cover `VFIO_DEVICE_GET_INFO`, `VFIO_DEVICE_GET_REGION_INFO`, `VFIO_DEVICE_GET_IRQ_INFO`, `VFIO_DEVICE_SET_IRQS`, `VFIO_DEVICE_RESET`, `VFIO_DEVICE_GET_PCI_HOT_RESET_INFO`, `VFIO_DEVICE_PCI_HOT_RESET`, `VFIO_DEVICE_QUERY_GFX_PLANE`, `VFIO_DEVICE_GET_GFX_DMABUF`, `VFIO_DEVICE_IOEVENTFD`, `VFIO_DEVICE_FEATURE`, `VFIO_DEVICE_BIND_IOMMUFD`, `VFIO_DEVICE_ATTACH_IOMMUFD_PT`, and `VFIO_DEVICE_DETACH_IOMMUFD_PT`. Core structs include `vfio_info_cap_header`, `vfio_group_status`, `vfio_device_info`, `vfio_region_info`, `vfio_irq_info`, `vfio_irq_set`, `vfio_pci_hot_reset_info`, `vfio_device_feature`, migration feature structs, DMA logging structs, `vfio_iommu_type1_info`, `vfio_iommu_type1_dma_map`, `vfio_iommu_type1_dma_unmap`, `vfio_iommu_type1_dirty_bitmap`, SPAPR TCE structs, and EEH structs.

Control flow: the legacy VFIO flow is open `/dev/vfio/vfio`, check API/extensions, open a group fd, verify `VFIO_GROUP_FLAGS_VIABLE`, set the group container, select an IOMMU, map DMA windows, acquire device fds, query device/region/IRQ info, mmap/read/write regions or bind eventfds, and tear down by unmapping DMA and releasing device/group/container fds. The cdev/iommufd flow binds a device fd to an iommufd, attaches an IOAS or HW page table, optionally replaces the attached page table, then detaches or closes. Migration flows through `VFIO_DEVICE_FEATURE_MIG_DEVICE_STATE`: userspace probes supported states, drives the explicit FSM, consumes or supplies opaque data FDs for saving/resuming, and may query `VFIO_MIG_GET_PRECOPY_INFO` on the migration data FD during precopy.

State and persistence: this header defines kernel-maintained state associated with open fds: group/container membership, selected IOMMU backend, IOVA mappings, dirty logging, IRQ eventfd bindings, vfio device feature state, migration state/data sessions, low-power permission, DMA logging ranges, iommufd binding and attached page tables, and SPAPR dynamic DMA windows. Persistent ABI compatibility is handled by `argsz`, flags, capability chains, reserved fields, and fixed ioctl numbers; callers must zero reserved fields and set `argsz` correctly.

Dependencies and integration: includes `linux/types.h`, `linux/ioctl.h`, and `linux/stddef.h`; `vfio_zdev.h` extends the device-info capability IDs declared here. It integrates with userspace VMMs such as QEMU, eventfd, mmap/read/write on device fds, PCI config/BAR semantics, IOMMUFD, Type1 IOMMU, POWER SPAPR TCE, POWER EEH, DRM dma-buf for graphics planes, and kernel bus drivers such as vfio-pci, vfio-ccw, vfio-ap, platform, AMBA, FSL-MC, and CDX.

Risks: VFIO is a security-sensitive ABI. `VFIO_NOIOMMU_IOMMU` explicitly lacks DMA isolation and taints the host. Incorrect IOVA/vaddr updates can corrupt userspace memory or let devices DMA the wrong object. PCI hot reset requires complete ownership of affected devices; cdev and legacy proof models must not be mixed. IRQ setup combines data and action flag classes, so malformed ranges or stale eventfds can misroute interrupts. Migration requires strict state transitions and opaque stream preservation; touching device regions during STOP_COPY or RESUMING can corrupt migration. New fields are exposed through `argsz`/caps, so assuming a fixed struct size is a compatibility bug.

Test signals: validate with UAPI header compile checks, ioctl number ABI tests, QEMU/VFIO smoke tests for container/group setup, IOMMU map/unmap and dirty bitmap tests, eventfd IRQ loopback through `VFIO_IRQ_SET_ACTION_TRIGGER`, PCI hot reset ownership tests, cdev+iommufd attach/detach tests, migration FSM transition tests including invalid arcs, and 32-bit compat/ioctl tests for struct layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vfio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vfio_ccw.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/vfio_ccw.h

Purpose: defines vfio-ccw region layouts for exposing IBM s390 channel-subsystem operations to userspace through VFIO device regions.

Important APIs/types/functions: exports packed structs `ccw_io_region`, `ccw_cmd_region`, `ccw_schib_region`, and `ccw_crw_region`. The I/O region carries ORB, SCSW, IRB byte areas and a return code. The async command region uses `VFIO_CCW_ASYNC_CMD_HSCH` and `VFIO_CCW_ASYNC_CMD_CSCH`. The SCHIB region contains the subchannel-information block captured via `stsch()`. The CRW region returns a Channel Report Word plus padding.

Control flow: userspace discovers vfio-ccw regions through `VFIO_DEVICE_GET_REGION_INFO` and region type/subtype capabilities in `vfio.h`. Writing/reading the I/O region initiates or observes START SUBCHANNEL state. Writing supported commands to the async command region triggers halt or clear subchannel actions when the capability exists. Reading the SCHIB region triggers a hardware `stsch()` collection path. The CRW region is used with the corresponding vfio-ccw interrupt/index support to report channel events.

State and persistence: all state is exchanged through packed region memory backed by the vfio-ccw kernel driver. Return codes communicate the result of the most recent region operation. The header itself stores no state; it fixes byte sizes for hardware-defined areas and therefore must remain ABI-stable.

Dependencies and integration: includes `linux/types.h` and integrates with `vfio.h` CCW region subtypes (`VFIO_REGION_SUBTYPE_CCW_ASYNC_CMD`, `SCHIB`, `CRW`) and IRQ indexes (`VFIO_CCW_IO_IRQ_INDEX`, `VFIO_CCW_CRW_IRQ_INDEX`, `VFIO_CCW_REQ_IRQ_INDEX`). It is specific to s390 channel I/O virtualization.

Risks: region contents are raw hardware ABI blocks, so packing, exact sizes, and byte interpretation matter. Async commands are capability-gated; userspace must not assume the region exists on every vfio-ccw device. Incorrect ORB or command fields can leave subchannels in unexpected states or surface guest-visible I/O errors.

Test signals: vfio-ccw UAPI layout checks, s390 virtualization tests that start/halt/clear subchannels, capability discovery tests for optional regions, SCHIB read tests, CRW interrupt delivery tests, and userspace VMM tests that validate `ret_code` behavior on success and error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vfio_ccw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vfio_zdev.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/vfio_zdev.h

Purpose: defines s390 zPCI-specific VFIO device-info capability payloads that extend the common VFIO capability chain.

Important APIs/types/functions: exports `vfio_device_info_cap_zpci_base`, `vfio_device_info_cap_zpci_group`, `vfio_device_info_cap_zpci_util`, and `vfio_device_info_cap_zpci_pfip`. Base capability fields describe DMA range, physical channel ID, virtual function number, measurement block length, PCI function type, group ID, and function handle. Group capability fields describe DMA address-space mask, MSI address, flags including `VFIO_DEVICE_INFO_ZPCI_FLAG_REFRESH`, measurement intervals, MSI limits, store block limits, PCI version, and interpreted store block length. Utility and PFIP capabilities carry variable-length byte strings.

Control flow: userspace calls `VFIO_DEVICE_GET_INFO`, detects `VFIO_DEVICE_FLAGS_CAPS`, walks `vfio_info_cap_header` links, and interprets capability IDs declared in `vfio.h` as these structures. Version comments mark field growth boundaries so older userspace can consume v1 subsets while newer userspace can read added fields when `argsz` permits.

State and persistence: the header describes read-only descriptive device/group state provided by the kernel. Variable-length strings are sized by `size` and are not NUL-terminated by contract. Persistent ABI behavior depends on capability header versioning and stable offsets.

Dependencies and integration: includes `linux/types.h` and `linux/vfio.h`. It integrates with s390 zPCI VFIO devices, zPCI DMA/MSI setup in userspace VMMs, and the VFIO info capability chain.

Risks: EBCDIC utility strings and raw path strings need length-aware handling. DMA range and group parameters are device-specific and must feed later IOMMU/iommufd setup correctly. Userspace must guard versioned tail fields and not assume all kernels expose `fh` or `imaxstbl`.

Test signals: capability-chain parsing tests, zPCI VFIO device-info tests on s390, ABI layout checks, version compatibility tests with truncated `argsz`, and VMM startup tests that consume DMA/MSI metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vfio_zdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vhost.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/vhost.h

Purpose: defines vhost ioctl numbers for userspace hypervisors configuring in-kernel virtio accelerators such as vhost-net, vhost-scsi, vhost-vsock, and vhost-vDPA.

Important APIs/types/functions: core ioctls include `VHOST_GET_FEATURES`, `VHOST_SET_FEATURES`, `VHOST_SET_OWNER`, `VHOST_RESET_OWNER`, `VHOST_SET_MEM_TABLE`, log base/fd setup, worker creation/freeing, virtqueue setup (`VHOST_SET_VRING_NUM`, `ADDR`, `BASE`, `GET_VRING_BASE`, endian, worker attach/get), eventfd binding (`KICK`, `CALL`, `ERR`), busy-loop timeout, and backend feature get/set. Device-family ioctls include `VHOST_NET_SET_BACKEND`, vhost-scsi endpoint/events ABI, vhost-vsock guest CID/running, and a large vhost-vDPA surface for device id/status/config, vring enable/count/size/group/ASID, config callbacks, IOVA range, suspend/resume, feature arrays, and fork-owner control.

Control flow: userspace normally opens a vhost device, optionally configures fork-owner mode before ownership, calls `VHOST_SET_OWNER`, negotiates features, installs guest memory, configures each virtqueue's size/base/address/endian/eventfds, attaches a backend, then starts the emulated virtio device. Migration and reset flows query vring bases, stop or unbind backends, log writes, and for vDPA call suspend/resume or status/config ioctls. Worker ioctls let one device create extra vhost workers and bind selected virtqueues to them.

State and persistence: state lives in the vhost kernel device fd: exclusive owner, memory table, log settings, feature masks, worker pool, per-vring geometry/base/eventfds/worker/endian/busy-loop settings, backend bindings, and vDPA status/config/group/ASID state. `VHOST_RESET_OWNER` and fd close discard most state; vDPA suspend requires preserving enough device-specific state for resume.

Dependencies and integration: includes `linux/vhost_types.h`, `linux/types.h`, and `linux/ioctl.h`. It integrates with virtio rings, eventfd, tap/raw sockets, target core for vhost-scsi, AF_VSOCK, vDPA hardware/software devices, QEMU, and userspace memory slots.

Risks: `VHOST_SET_OWNER` ordering is mandatory and many ioctls fail before ownership. Memory regions and vring addresses must match guest mappings and alignment requirements from `vhost_types.h`. Incorrect eventfd binding can hang guest I/O or lose interrupts. vDPA ASID/group ioctls affect DMA isolation, and suspend/resume support must be feature-checked. Feature-array and extended feature ioctls share command numbers with feature masks in ways userspace must call with the exact expected struct.

Test signals: QEMU vhost-net/scsi/vsock smoke tests, virtqueue setup/teardown tests, live migration tests verifying vring base and logging, vDPA conformance tests for config/status/IOVA/group APIs, eventfd kick/call tests, worker attach/free tests, and UAPI ioctl-number/layout checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vhost.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vhost_types.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/vhost_types.h

Purpose: defines the data structures and feature/backend flags used by vhost ioctls and vhost IOTLB messages.

Important APIs/types/functions: exports `vhost_vring_state`, `vhost_vring_file`, `vhost_vring_addr`, `vhost_worker_state`, `vhost_vring_worker`, `vhost_iotlb_msg`, `vhost_msg`, `vhost_msg_v2`, `vhost_features_array`, `vhost_memory_region`, `vhost_memory`, `vhost_scsi_target`, `vhost_vdpa_config`, and `vhost_vdpa_iova_range`. It defines access bits (`VHOST_ACCESS_RO/WO/RW`), IOTLB message types including miss/update/invalidate/access-fail and batch begin/end, memory page alignment via `VHOST_PAGE_SIZE`, SCSI ABI version, frontend feature bits such as `VHOST_F_LOG_ALL`, and backend feature bits such as `VHOST_BACKEND_F_IOTLB_MSG_V2`, `BATCH`, `ASID`, `SUSPEND`, `RESUME`, `DESC_ASID`, and `IOTLB_PERSIST`.

Control flow: these structs are passed to `vhost.h` ioctls or sent over vhost IOTLB message channels. Memory table setup passes a flexible `vhost_memory` array. Vring setup passes state, address, and eventfd structs. IOTLB backends send misses and receive mapping updates/invalidation, optionally with V2 ASIDs and batch hints. vDPA config reads/writes pass an offset/length/buffer descriptor.

State and persistence: the structures describe state installed in a vhost fd: guest memory map, vring addresses and bases, per-vring file descriptors, worker binding, backend IOTLB mappings, SCSI endpoint identity, vDPA config slices, and IOVA limits. Flexible arrays carry variable-sized state and must be sized exactly by userspace.

Dependencies and integration: includes `linux/types.h`, `linux/compiler.h`, `linux/virtio_config.h`, and `linux/virtio_ring.h`. It integrates with the vhost ioctl layer, virtqueue layout definitions, IOMMU/IOTLB handling, QEMU memory listeners, target SCSI WWPNs, and vDPA devices.

Risks: all region addresses and sizes must be 4K-aligned for memory tables. `vhost_vring_addr` alignment comments for descriptor/used/available/log addresses are ABI-relevant. IOTLB batching is only a hint and not guaranteed atomic. V2 IOTLB ASIDs require backend feature negotiation. Flexible arrays using `__counted_by` require careful allocation size calculation.

Test signals: compile/layout tests, vhost memory table alignment tests, IOTLB miss/update/invalidate tests, V2 ASID tests, SCSI ABI version tests, vDPA config range tests, and QEMU memory hotplug/migration paths that rebuild memory tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vhost_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/videodev2.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/videodev2.h

Purpose: defines the public Video4Linux2 userspace ABI for video, radio, SDR, touch, metadata, codec, buffer streaming, controls, events, tuner, and timing devices.

Important APIs/types/functions: this is an ioctl and struct catalog. Foundational helpers include `v4l2_fourcc`, `v4l2_fourcc_be`, field/type/memory/colorspace/xfer/ycbcr/quantization enums, and mapping macros for defaults. Capability and format structs include `v4l2_capability`, `v4l2_pix_format`, many `V4L2_PIX_FMT_*` fourcc constants, `v4l2_fmtdesc`, frame-size/frame-interval enumeration, `v4l2_format`, `v4l2_pix_format_mplane`, `v4l2_sdr_format`, and `v4l2_meta_format`. Buffer APIs use `v4l2_requestbuffers`, `v4l2_plane`, `v4l2_buffer`, `v4l2_exportbuffer`, `v4l2_create_buffers`, and `v4l2_remove_buffers`. Controls use `v4l2_control`, `v4l2_ext_control`, `v4l2_ext_controls`, `v4l2_queryctrl`, `v4l2_query_ext_ctrl`, and `v4l2_querymenu`. Timing/tuner/event structures include `v4l2_standard`, `v4l2_bt_timings`, `v4l2_dv_timings`, `v4l2_input`, `v4l2_output`, `v4l2_tuner`, `v4l2_frequency`, `v4l2_event`, and `v4l2_event_subscription`. The tail defines `VIDIOC_*` ioctl numbers from querycap through private ranges.

Control flow: common capture flow is open a video node, `VIDIOC_QUERYCAP`, enumerate inputs/formats/sizes/intervals, negotiate format with `TRY_FMT`/`S_FMT`, request or create buffers, query and mmap/export/import buffers, `QBUF`, `STREAMON`, poll/select, `DQBUF`, requeue, then `STREAMOFF`. Output and mem2mem devices use symmetric output/capture queues, encoder/decoder commands, and timestamp/sequence flags. Control flow queries controls, gets/sets simple or extended controls, optionally uses request fds, and receives events through subscribe/dequeue. Analog/digital input flow uses standards, DV timings, tuner/frequency, audio, crop/selection, and EDID ioctls.

State and persistence: driver state includes selected input/output, active format per queue, allocated buffer queues, queued/done buffer state, mmap or dma-buf mappings, stream-on state, control values, priorities, selected standard/timing/frequency, subscribed events, and request-bound control/buffer state. The ABI preserves compatibility through reserved fields, fixed ioctl numbers, packed structs where needed, and deprecated aliases retained for userspace.

Dependencies and integration: includes `sys/time.h` for userspace, `linux/compiler.h`, `linux/ioctl.h`, `linux/types.h`, `linux/v4l2-common.h`, and `linux/v4l2-controls.h`. It integrates with media controller graphs, V4L2 core compat ioctl handling, vb2 buffer queues, dma-buf, codec stateless controls, DRM/EDID timing concepts, radio/RDS, and userspace libraries such as libv4l2, GStreamer, FFmpeg, browsers, camera stacks, and test tools.

Risks: this header is extremely ABI-stable; adding or changing ioctl structs requires 32-bit compat updates as the file notes. Reserved fields must be zeroed by userspace. Multi-planar buffers require `length` to mean plane count, not byte length. Time structs differ between kernel and userspace builds. Fourcc constants include many vendor formats, deprecated aliases, and packed endian variants that drivers must report accurately. Buffer flags encode ownership and cache maintenance; wrong handling can cause stale data, lost frames, or memory corruption. Request API and dynamic array controls require careful fd and payload lifetime management.

Test signals: V4L2 compliance tests (`v4l2-compliance`), ioctl32 compat tests, vb2 streaming tests for MMAP/USERPTR/DMABUF, format enumeration and try/set/get round-trips, colorspace default mapping tests, control query/get/set tests including compound codec controls, event subscription/dequeue tests, tuner/timing/standard tests, and userspace integration through GStreamer/FFmpeg/libcamera on representative drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/videodev2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_9p.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_9p.h

Purpose: defines the virtio 9P filesystem device configuration ABI.

Important APIs/types/functions: exports feature bit `VIRTIO_9P_MOUNT_TAG` and packed `virtio_9p_config`, which contains a little-endian tag length and a flexible, non-NUL-terminated mount tag byte array.

Control flow: a virtio 9P driver negotiates features through common virtio config mechanisms, reads the config space tag length and tag bytes, and uses that tag to select the exported 9P mount endpoint. Data-plane 9P requests are defined elsewhere; this header only covers the virtio-specific config surface.

State and persistence: persistent device state is the configuration-space mount tag. The tag length controls parsing and must be honored exactly because the byte array is not NUL-terminated.

Dependencies and integration: includes `linux/virtio_types.h`, `linux/virtio_ids.h`, and `linux/virtio_config.h`. It integrates with virtio transport, guest 9P clients, and host filesystem export implementations such as virtio-9p in VMMs.

Risks: length/tag parsing errors can cause overreads or incorrect mount selection. The flexible array means callers must allocate/read enough config bytes. The mount tag feature must be negotiated or otherwise treated according to virtio device behavior.

Test signals: virtio config layout checks, guest mount tests by tag, VMM/device tests with short and maximum tags, and negative tests for unterminated tag handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_9p.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_balloon.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_balloon.h

Purpose: defines the virtio memory balloon device ABI for guest memory inflation/deflation, statistics, free-page hinting/reporting, page poisoning, and page reporting.

Important APIs/types/functions: feature bits include `VIRTIO_BALLOON_F_MUST_TELL_HOST`, `STATS_VQ`, `DEFLATE_ON_OOM`, `FREE_PAGE_HINT`, `PAGE_POISON`, and `REPORTING`. `virtio_balloon_config` carries host-requested page count, actual ballooned pages, free-page hint/report command id, and poison value. Statistic tags range from swap/fault/memory totals through hugepage and reclaim counters, with `VIRTIO_BALLOON_S_NAMES` name macros. `virtio_balloon_stat` is the packed tag/value pair sent on the stats virtqueue.

Control flow: the host updates `num_pages`; the guest inflates or deflates by sending PFNs over balloon queues and updates `actual`. Optional stats queues send arrays of `virtio_balloon_stat`. Free-page hint/reporting uses command IDs `STOP` and `DONE` to coordinate reporting batches. Page poisoning communicates the poison value when negotiated.

State and persistence: device config tracks desired and actual balloon size plus hint/report command state. The guest owns transient PFN lists and stat arrays. Ballooned pages persist as unavailable guest memory until deflated; stats are sampled, not durable.

Dependencies and integration: includes Linux integer types and common virtio type/id/config headers. It integrates with guest memory management, host memory overcommit, OOM behavior, page reporting, and VMM memory accounting.

Risks: the PFN interface assumes `VIRTIO_BALLOON_PFN_SHIFT` of 12, so page size assumptions must be managed. Packed `virtio_balloon_stat` is kept for compatibility but can generate inefficient accesses. Incorrect command ID handling can race free-page reporting. Misreported `actual` breaks host memory accounting.

Test signals: virtio-balloon inflate/deflate tests, stats virtqueue tests, OOM deflate behavior, free-page hint/reporting command tests, page poisoning negotiation tests, and ABI layout checks for the packed stat structure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_balloon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_blk.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_blk.h

Purpose: defines the virtio block device ABI, including config-space fields, request header/status layout, discard/write-zeroes/secure-erase, multi-queue, cache flush, device ID, and zoned block device commands.

Important APIs/types/functions: feature bits include size/segment limits, geometry, read-only, block size, topology, multi-queue, discard, write-zeroes, secure erase, and zoned support, plus legacy barrier/SCSI/flush/config-WCE bits. `virtio_blk_config` is the packed config-space structure for capacity, limits, topology, write cache, queue count, discard/write-zeroes/secure-erase limits, and zoned characteristics. Requests start with `virtio_blk_outhdr`, use command types such as `VIRTIO_BLK_T_IN`, `OUT`, `FLUSH`, `GET_ID`, `DISCARD`, `WRITE_ZEROES`, `SECURE_ERASE`, and zone operations. Zoned structs include `virtio_blk_zone_descriptor` and `virtio_blk_zone_report`. Status bytes include OK, IOERR, UNSUPP, and zoned-specific errors.

Control flow: driver negotiates features, reads config limits, creates one or more virtqueues, and submits scatter-gather requests headed by `virtio_blk_outhdr`. The device processes data direction by command type and writes a final one-byte status. Discard/write-zeroes/secure-erase pass arrays of range descriptors. Zoned commands open/close/finish/reset/report/append zones and return zone-specific status on errors.

State and persistence: persistent state is the virtual disk content and device config. Runtime state includes queue submissions, cache state, writeback mode, multi-queue count, and zoned write pointers/open/active zone counts. The header fixes request/status layouts that must remain stable across guest/host implementations.

Dependencies and integration: includes Linux types and common virtio id/config/type headers. It integrates with guest block layers, VMM block backends, host files/devices, flush/discard plumbing, SCSI passthrough legacy behavior, and zoned block device semantics.

Risks: command `type` uses both values and legacy flag bits, so combining flags incorrectly can create invalid requests. Capacity is in 512-byte sectors while block size and topology use logical units; unit conversion bugs are common. Feature-gated config fields must not be consumed unless negotiated. Zoned commands add strict alignment/resource constraints. `write_zeroes_may_unmap` affects data persistence expectations.

Test signals: virtio-blk boot/read/write tests, feature negotiation matrix tests, flush/writeback tests, discard/write-zeroes/secure-erase tests, multi-queue I/O tests, zoned command conformance tests, status-byte error injection, and packed config layout checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_blk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_bt.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_bt.h

Purpose: defines the virtio Bluetooth device feature and configuration ABI.

Important APIs/types/functions: feature bits identify vendor HCI support, Microsoft vendor support, AOSP vendor support, and the v2 config layout. Enums define primary config type and vendor IDs for none, Zephyr, Intel, and Realtek. `virtio_bt_config` carries type, vendor, and Microsoft opcode in a packed legacy layout; `virtio_bt_config_v2` adds an alignment byte and uses a naturally aligned layout.

Control flow: the guest negotiates virtio feature bits, selects the config layout based on `VIRTIO_BT_F_CONFIG_V2`, reads type/vendor/opcode, and configures the Bluetooth HCI transport accordingly. Vendor extension support gates use of vendor-specific commands.

State and persistence: config-space fields are static descriptive state. Runtime HCI command/event state is outside this header.

Dependencies and integration: includes `linux/virtio_types.h` and integrates with virtio transport, guest Bluetooth HCI stacks, and VMM/device implementations that emulate Bluetooth controllers.

Risks: using the wrong config layout can misread `vendor` and `msft_opcode`. Vendor extension bits should be treated as capability gates. The legacy struct is packed, so cross-language implementations need exact byte layout.

Test signals: config layout tests with and without `CONFIG_V2`, vendor feature negotiation tests, HCI bring-up smoke tests, and ABI compile checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_bt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_config.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_config.h

Purpose: defines common virtio configuration status bits and transport feature bit numbers shared by virtio device-specific UAPI headers.

Important APIs/types/functions: status bits include `VIRTIO_CONFIG_S_ACKNOWLEDGE`, `DRIVER`, `DRIVER_OK`, `FEATURES_OK`, `NEEDS_RESET`, and `FAILED`. Transport feature range is `VIRTIO_TRANSPORT_F_START` through `VIRTIO_TRANSPORT_F_END`. Feature bits include legacy `VIRTIO_F_NOTIFY_ON_EMPTY` and `VIRTIO_F_ANY_LAYOUT`, `VIRTIO_F_VERSION_1`, `VIRTIO_F_ACCESS_PLATFORM`/legacy alias `VIRTIO_F_IOMMU_PLATFORM`, packed rings, in-order use, platform ordering, SR-IOV, notification data/config data, per-queue reset, and admin virtqueue.

Control flow: virtio drivers use status bits to acknowledge, bind, negotiate features, confirm `FEATURES_OK`, set up queues/config, and finally set `DRIVER_OK`. Device reset/error paths use `NEEDS_RESET` and `FAILED`. Feature bits are negotiated before device-specific queues and config fields are consumed.

State and persistence: the header defines the status byte and feature bit meanings, but the transport stores them in device config space or transport-specific registers. Negotiated feature state persists until reset.

Dependencies and integration: includes `linux/types.h`. It is included by most virtio UAPI device headers and integrates with virtio-pci, MMIO, CCW, vDPA, vhost, and all virtio drivers.

Risks: `VIRTIO_F_ACCESS_PLATFORM` has reverse-polarity history and an old alias, so DMA isolation behavior must be interpreted carefully. Status transitions have ordering semantics; setting `DRIVER_OK` too early or ignoring `FEATURES_OK` failure breaks devices. Transport feature bits must not collide with device-specific feature spaces.

Test signals: virtio feature negotiation tests, status transition tests, packed-ring and ring-reset tests, platform DMA/IOMMU tests, and cross-header compile checks for shared feature definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_console.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_console.h

Purpose: defines the virtio console and virtio serial port device ABI.

Important APIs/types/functions: feature bits include console size, multiport support, and emergency write support. `virtio_console_config` exposes columns, rows, max port count, and emergency write register. `virtio_console_control` carries per-port control messages with port ID, event, and value. Control events include device ready, port add/remove/ready, console port designation, resize, port open, and port name. `VIRTIO_CONSOLE_BAD_ID` marks an invalid port ID.

Control flow: after feature negotiation, the guest reads size and port capacity, exchanges control messages with the host over control queues, creates/removes ports, marks ports ready/open, handles resize events, and writes emergency characters through `emerg_wr` when supported.

State and persistence: runtime state includes screen geometry, port list, per-port open/ready flags, names, console designation, and emergency write register content. Config fields are device state; data streams for ports are handled by virtqueues outside this header.

Dependencies and integration: includes Linux types and virtio type/id/config headers. It integrates with guest console/tty/hvc layers, virtio-serial ports, host VMM chardevs, and emergency console paths.

Risks: multiport control events are asynchronous and must be ordered per port. `emerg_wr` is a config register, not a normal data queue. Incorrect port ID handling can route console data to the wrong chardev. Geometry fields are feature-gated by `VIRTIO_CONSOLE_F_SIZE`.

Test signals: boot console tests, multiport add/remove/open/name tests, resize event tests, emergency write tests, and host/guest virtio-serial integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_console.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_crypto.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_crypto.h

Purpose: defines the virtio crypto accelerator ABI for session creation/destruction and data requests across cipher, hash, MAC, AEAD, and asymmetric cipher services.

Important APIs/types/functions: service IDs and `VIRTIO_CRYPTO_OPCODE()` compose control/data opcodes. Control structs include `virtio_crypto_ctrl_header`, service-specific session parameter structs, `virtio_crypto_sym_create_session_req`, `virtio_crypto_destroy_session_req`, and `virtio_crypto_op_ctrl_req`. Data structs include `virtio_crypto_op_header`, cipher/hash/MAC/AEAD/algorithm-chain/akcipher parameter structs, and `virtio_crypto_op_data_req`. Config and response structs include `virtio_crypto_config`, `virtio_crypto_session_input`, `virtio_crypto_inhdr`, status codes (`OK`, `ERR`, `BADMSG`, `NOTSUPP`, `INVSESS`, `NOSPC`, `KEY_REJECTED`), and hardware-ready status `VIRTIO_CRYPTO_S_HW_READY`.

Control flow: the driver reads `virtio_crypto_config` to learn service/algorithm masks, queue counts, key limits, and max request size. It creates sessions on the control virtqueue by sending a header plus service-specific parameters and key material in the descriptor chain, receives a session ID/status, then submits data requests on data virtqueues with opcode, algorithm, session ID, operation flags, lengths, IV/AAD/source/destination buffers, and receives a status in `virtio_crypto_inhdr`. Sessions are explicitly destroyed on the control queue.

State and persistence: device state includes supported algorithm masks, session table entries keyed by 64-bit session ID, per-queue data processing, and possibly accelerator hardware readiness. Session state persists until destroy or reset. Request buffers and IV/counter updates are per-operation/transient.

Dependencies and integration: includes Linux and virtio type/id/config headers. It integrates with guest crypto APIs, VMM or hardware crypto backends, virtqueues, and algorithm-specific standards for AES, DES/3DES, KASUMI, SNOW3G, ZUC, SHA/SHA3, HMAC/CMAC/GMAC, AEAD GCM/CCM/ChaCha20-Poly1305, RSA, DSA, and ECDSA.

Risks: all request lengths drive descriptor parsing and must match buffer chains. Unsupported or deprecated algorithms/opcodes need clear `NOTSUPP`/error behavior. Session IDs are device-generated and invalid after destroy/reset. AEAD and algorithm-chain offsets/AAD/hash lengths are easy to miscompute. Cryptographic key material crosses the virtqueue boundary, so zeroization and isolation are important in implementations.

Test signals: algorithm negotiation tests, session create/destroy lifecycle tests, known-answer tests for each supported algorithm/mode, invalid session/status tests, max request/key length tests, multi-queue concurrency tests, AEAD authentication failure tests, and ABI layout checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_crypto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_fs.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_fs.h

Purpose: defines the virtio-fs device configuration ABI for sharing a host filesystem with a guest.

Important APIs/types/functions: exports packed `virtio_fs_config`, containing a fixed 36-byte UTF-8 filesystem tag padded with NULs and little-endian `num_request_queues`. It also defines `VIRTIO_FS_SHMCAP_ID_CACHE` for identifying the DAX/cache shared-memory PCI capability.

Control flow: after virtio feature negotiation, the guest reads the tag to identify the mountable filesystem and reads `num_request_queues` to size request virtqueues. If shared memory capabilities are exposed through virtio-pci, the cache region is identified by `VIRTIO_FS_SHMCAP_ID_CACHE`.

State and persistence: config-space state is the filesystem tag and queue count. Data-plane filesystem state is handled by FUSE/virtiofs request queues and optional shared cache memory outside this header.

Dependencies and integration: includes Linux types and common virtio id/config/type headers. It integrates with virtio transport, virtiofs guest drivers, host virtiofsd/VMM implementations, FUSE protocol handling, and DAX shared-memory mappings.

Risks: the tag is fixed-size and not necessarily a conventional C string beyond NUL padding. Queue count must match device-provided virtqueues. Shared-memory capability IDs must be interpreted through the transport-specific capability table.

Test signals: virtio-fs mount tests by tag, queue count/config parsing tests, DAX cache shared-memory discovery tests, and VMM/virtiofsd integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_gpio.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_gpio.h

Purpose: defines the virtio GPIO controller ABI for line naming, direction/value operations, and optional GPIO interrupt delivery.

Important APIs/types/functions: feature bit `VIRTIO_GPIO_F_IRQ` gates IRQ support. Request types include get names, get/set direction, get/set value, and IRQ type. Status values are OK/ERR. Direction values are none/out/in. IRQ type values cover none, rising/falling/both edges, high/low levels. Structs include `virtio_gpio_config`, `virtio_gpio_request`, `virtio_gpio_response`, `virtio_gpio_response_get_names`, `virtio_gpio_irq_request`, and `virtio_gpio_irq_response`, plus IRQ status valid/invalid constants.

Control flow: the guest reads config to learn `ngpio` and name table size, fetches names with `GET_NAMES`, sends request/response operations for individual GPIO lines, and when IRQ support is negotiated configures line IRQ type and receives IRQ responses on the interrupt virtqueue.

State and persistence: runtime state includes per-line direction, output value, sampled input value, configured IRQ trigger type, and line names. The config space persists number of lines and name table size. Requests are stateless transactions except for set operations updating line state.

Dependencies and integration: includes `linux/types.h` and integrates with virtio transport, guest GPIO frameworks, host GPIO emulation or forwarding, and interrupt delivery paths.

Risks: GPIO numbers are 16-bit and must be range-checked against `ngpio`. `GET_NAMES` returns a flexible byte array sized by config, so parsers need length discipline. IRQ support is optional and must be feature-negotiated. Level and edge trigger constants are bit-like but should be interpreted according to the protocol.

Test signals: line enumeration/name tests, get/set direction and value round-trips, invalid GPIO number tests, IRQ feature negotiation tests, edge/level interrupt delivery tests, and ABI layout checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_gpu.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_gpu.h

Purpose: defines the virtio GPU device ABI for 2D scanout, cursor updates, 3D/Virgl contexts, capsets, EDID, resource UUIDs, blob resources, host-visible shared memory, and resource mapping.

Important APIs/types/functions: feature bits include VIRGL, EDID, RESOURCE_UUID, RESOURCE_BLOB, and CONTEXT_INIT. `virtio_gpu_ctrl_type` enumerates 2D commands, 3D commands, cursor commands, success responses, and error responses. Shared memory IDs include host-visible blob memory. Common command header `virtio_gpu_ctrl_hdr` carries type, flags, fence ID, context ID, and optional ring index. Other key structs include cursor position/update, rectangles, 2D and 3D resource creation, scanout setup, flush/transfer commands, backing memory entries, display info response, 3D context/resource/submit commands, capset queries/responses, EDID response, config events, resource UUID response, blob create/set-scanout/map/unmap commands, and map info response. Format enums define common framebuffer formats.

Control flow: the driver negotiates features, reads `virtio_gpu_config` for scanout/capset counts and display events, queries display info, creates resources, attaches guest memory backing, transfers data to/from host, sets scanout, flushes rectangles, and handles cursor commands on the cursor queue. 3D flow creates a context, attaches resources, submits command buffers, and queries capsets. Blob flow creates resources with guest/host memory modes, optionally maps/unmaps host-visible blobs, and can set scanout from blob resources. Fences in the common header order asynchronous completion.

State and persistence: device state includes scanout configuration, resources and attached backing memory, contexts, capsets, fences, display event bits, EDID blobs, UUIDs, blob map state, and cursor position/resource. Resources persist until unref/detach/reset; config events persist in `events_read` until cleared via `events_clear`.

Dependencies and integration: includes `linux/types.h`. It integrates with virtio transport, DRM virtio-gpu driver, framebuffer console, Mesa/Virgl/Venus/gfxstream userspace, dma-buf/resource sharing, EDID consumers, and VMM GPU backends.

Risks: resource IDs and context IDs are guest-selected but device-validated; stale or duplicate IDs return protocol errors. Backing memory entries are guest physical addresses/lengths and require correct DMA mapping. Fence/ring-index behavior depends on feature negotiation. Blob mapping cache mode must be honored by the guest. Scanout dimensions, strides, offsets, and formats must match resource layout or display corruption follows.

Test signals: 2D boot/fbcon tests, display-info and EDID tests, resource create/attach/transfer/flush/unref tests, cursor move/update tests, Virgl/capset rendering tests, blob map/unmap tests, fence ordering tests, display hotplug event tests, and ABI layout checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_gpu.h -->
