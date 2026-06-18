# subset-b-005934 Research

Grouped research for the requested source-tree-aligned files. Each section preserves the source path in its title and is delimited for reconciliation.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-subdev.h -->
# sources/distributed-fs/ceph-client/include/media/v4l2-subdev.h

Purpose: This header defines the in-kernel V4L2 sub-device abstraction used by bridge drivers, sensors, decoders, tuners, IR devices, and media-controller graph entities. It is a contract header: it does not implement hardware behavior, but it describes callback tables, sub-device state storage, routing metadata, media-bus frame descriptors, stream enable helpers, and the public call macros that V4L2 core and drivers use to coordinate subcomponents.

Important APIs, types, and functions: The central type is `struct v4l2_subdev`, which embeds or references a media entity, module owner, callback tables, control handler, async registration lists, firmware node, device node, privacy LED, active state, enabled pad bitmask, and legacy `s_stream` tracking. `struct v4l2_subdev_ops` groups core, tuner, audio, video, VBI, IR, sensor, and pad callbacks. `struct v4l2_subdev_core_ops` covers status logging, private ioctl dispatch, debug register access, event subscription, reset, firmware load, GPIO, and IRQ-service callbacks. `struct v4l2_subdev_video_ops` contains legacy stream and bus preparation operations, while `struct v4l2_subdev_pad_ops` contains the modern format, selection, EDID, timings, media-bus config, routing, and per-stream enable/disable callbacks. The active-state model is represented by `struct v4l2_subdev_state`, `struct v4l2_subdev_pad_config`, `struct v4l2_subdev_krouting`, and `struct v4l2_subdev_stream_configs`. Helpers include `v4l2_subdev_init()`, `v4l2_subdev_init_finalize()`, `v4l2_subdev_cleanup()`, `v4l2_subdev_lock_state()`, `v4l2_subdev_lock_states()`, state accessors for format/crop/compose/interval, routing helpers, `v4l2_subdev_enable_streams()`, `v4l2_subdev_disable_streams()`, `v4l2_subdev_s_stream_helper()`, and the `v4l2_subdev_call*` macros.

Control flow: Driver probe code initializes `struct v4l2_subdev` with `v4l2_subdev_init()` or bus-specific wrappers, optionally initializes media pads, calls `v4l2_subdev_init_finalize()` for centralized active state, then registers the subdev through the V4L2 async or device framework. Bridge or media-graph callers invoke callbacks through `v4l2_subdev_call()` or state-aware call helpers. Format negotiation enters pad ops with either active state or try state. Modern streaming enables specific streams on source pads through `v4l2_subdev_enable_streams()`, falling back to legacy `.s_stream()` only for simple single-source-pad devices. Shutdown reverses stream state, unregisters the subdev, and releases active state or endpoint resources through `v4l2_subdev_cleanup()`.

State and persistence behavior: The header models runtime state, not persistent storage. Active subdev state is protected by a mutex, may share a driver-provided lock, and stores pad formats, crop/compose rectangles, intervals, routing, and stream configs. Per-file-handle try state lives in `struct v4l2_subdev_fh` when the subdev API is enabled. `enabled_pads` and `s_stream_enabled` track stream status for helper enforcement. Async lists and fwnode references connect the subdev to discovery and graph-building state.

Dependencies and integration points: The file depends on V4L2 core headers, media-controller entity support, async notifier support, media-bus types, V4L2 file handles, control handlers, firmware nodes, regulator data, and optional config blocks such as `CONFIG_MEDIA_CONTROLLER`, `CONFIG_VIDEO_V4L2_SUBDEV_API`, `CONFIG_VIDEO_ADV_DEBUG`, and `CONFIG_COMPAT`. It integrates with bridge drivers, sensor drivers, subdev character devices, the media graph, event queues, the request/state ioctl path, and pipeline link validation.

Risks: Incorrect lock ordering with `v4l2_subdev_lock_states()` can deadlock because callers must impose a stable order. Mixing legacy `.s_stream()` with streams-aware `.enable_streams()` can create double-start or double-stop bugs if drivers bypass helpers. Active-state drivers must call finalize and cleanup symmetrically. Pad and stream IDs must be validated before state accessors are dereferenced. Private ioctls and compat paths are risk areas because they bypass strongly typed operation contracts. IRQ callbacks must not sleep.

Test signals: Useful tests include media-controller graph validation, format try/active state round trips, route validation under all declared restrictions, stream enable/disable duplicate-call error paths, fallback `.s_stream()` behavior for legacy single-source-pad devices, lockdep coverage for active-state locks, event subscription delivery, async unregister/open/close ordering, and link validation failures for mismatched width, height, or media-bus codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-subdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-vp9.h -->
# sources/distributed-fs/ceph-client/include/media/v4l2-vp9.h

Purpose: This header provides helper data structures and exported helper routines for stateless VP9 codec drivers using V4L2 controls. It captures VP9 frame probability context, symbol-count views reported by hardware, and operations that update or reset probability tables according to the VP9 specification.

Important APIs, types, and functions: `struct v4l2_vp9_frame_mv_context` stores motion-vector probability tables. `struct v4l2_vp9_frame_context` stores transform, coefficient, skip, inter/intra, reference, mode, partition, and motion-vector probabilities. `struct v4l2_vp9_frame_symbol_counts` is a collection of pointers into hardware-produced count buffers for partitions, transform sizes, prediction modes, filters, motion vectors, coefficients, and end-of-block counts. Extern data includes key-frame Y and UV mode probabilities, key-frame partition probabilities, and `v4l2_vp9_default_probs`. Functions are `v4l2_vp9_fw_update_probs()`, `v4l2_vp9_reset_frame_ctx()`, `v4l2_vp9_adapt_coef_probs()`, `v4l2_vp9_adapt_noncoef_probs()`, and `v4l2_vp9_seg_feat_enabled()`.

Control flow: Userspace parses VP9 frame and compressed-header controls and submits them to a stateless decoder. The driver chooses or resets one of the frame contexts with `v4l2_vp9_reset_frame_ctx()`, applies forward updates from compressed header deltas before decode, programs hardware, then after decode maps hardware symbol counts into `struct v4l2_vp9_frame_symbol_counts` and calls backward adaptation helpers to update coefficients and non-coefficients for future frames.

State and persistence behavior: The header expects drivers to persist up to four VP9 frame contexts across frames in driver-private decode state. Symbol counts are transient and only valid after one decoded frame. No storage persists outside the driver; the helpers mutate caller-owned probability structs in place.

Dependencies and integration points: It depends on `media/v4l2-ctrls.h` for VP9 decode control structures. It integrates with stateless mem2mem video decoders, V4L2 request API workflows, and hardware-specific count-buffer layouts through pointer indirection rather than fixed overlays.

Risks: Count pointer arrays must match hardware layout and VP9 table dimensions exactly. Applying updates in the wrong order or using the wrong frame context index will cause decode drift. Reset semantics are frame-header dependent and easy to mishandle around key frames, intra frames, and context refresh. The pointer-heavy count structure carries normal kernel risks around invalid DMA buffer mappings and lifetime.

Test signals: Decode conformance should include VP9 key frames, inter frames, segmentation, frame-context refresh/reset cases, high-precision motion vectors, coefficient adaptation, and hardware count layouts. Unit-style tests can validate default table reset, segmentation feature lookup, and probability update determinism against known VP9 bitstream traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-vp9.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/videobuf2-core.h -->
# sources/distributed-fs/ceph-client/include/media/videobuf2-core.h

Purpose: This is the core videobuf2 buffer queue framework contract. It defines memory models, queue state, buffer state transitions, allocator callbacks, driver callbacks, core queue operations, polling, mmap, read/write file I/O emulation, thread I/O, and helpers used by V4L2 and DVB wrappers.

Important APIs, types, and functions: `enum vb2_memory` describes MMAP, USERPTR, and DMABUF ownership models. `struct vb2_mem_ops` is the allocator interface for allocation, userptr pinning, dmabuf attach/map, cache sync, virtual address lookup, cookie lookup, user counting, and mmap. `struct vb2_plane` stores per-plane private memory, dma-buf, payload, length, minimum length, offset/userptr/fd, and data offset. `enum vb2_io_modes` declares queue capabilities. `enum vb2_buffer_state` defines the state machine from dequeued, request-bound, preparing, queued, active, done, and error. `struct vb2_buffer` tracks queue, index, type, memory, planes, timestamp, request object, state, sync/prepared flags, cache-hint flags, and queued/done list membership. `struct vb2_ops` is the driver callback table for queue setup, buffer validation/init/prepare/finish/cleanup, streaming prepare/start/stop/unprepare, buffer queueing, and request cancellation completion. `struct vb2_queue` holds public queue configuration plus private state for allocated buffers, bitmap, queued/done lists, waitqueue, streaming/error flags, fileio/threadio, ownership, and debug counters.

Control flow: A driver fills mandatory queue fields and calls `vb2_core_queue_init()`. Userspace operations flow through subsystem wrappers into core helpers: `vb2_core_reqbufs()` negotiates with `queue_setup()` and allocates buffers; `vb2_core_create_bufs()` extends a queue; `vb2_core_prepare_buf()` validates and prepares a buffer; `vb2_core_qbuf()` queues directly or binds to a media request; `vb2_core_streamon()` transitions to streaming and invokes driver callbacks once enough buffers are queued; drivers return buffers with `vb2_buffer_done()`; `vb2_core_dqbuf()` finishes and returns completed buffers to userspace; `vb2_core_streamoff()` cancels streaming and returns outstanding buffers. `vb2_core_queue_release()` stops streaming and frees memory.

State and persistence behavior: Runtime queue state is entirely in `struct vb2_queue` and associated `struct vb2_buffer` objects. Buffer ownership moves among userspace, media request, vb2 queued list, driver active ownership, done list, and userspace again. `owned_by_drv_count`, `queued_count`, `streaming`, `start_streaming_called`, `error`, `waiting_in_dqbuf`, and `last_buffer_dequeued` are the key state flags and counters. Persistent storage is not used; all buffers and mappings are released by queue release or `REQBUFS(0)`.

Dependencies and integration points: The header depends on Linux MM, mutexes, polling, DMA-buf, bitops, media request objects, and frame vectors. It is wrapped by `videobuf2-v4l2.h`, allocator headers such as dma-contig/dma-sg/vmalloc, and DVB support. It integrates with file operations, ioctls, DMA mapping, request API, mmap VM operations, and hardware interrupt completion paths.

Risks: The buffer state machine is sensitive to unbalanced `buf_prepare`/`buf_finish`, allocator map/unmap, and `vb2_buffer_done()` calls. Drivers must return all active buffers in `stop_streaming()` or queue shutdown can hang. `vb2_get_buffer()` does not refcount, so lifetime must be controlled externally. Queue lock release during blocking dequeue creates race windows that must respect `waiting_in_dqbuf`. Incorrect plane length/payload validation can cause out-of-bounds DMA or userspace exposure. Mixing direct QBUF and request-based queueing is prohibited by `uses_qbuf` and `uses_requests`.

Test signals: Test request buffer allocation and release, create/remove buffers, MMAP/USERPTR/DMABUF paths, queue/dequeue in blocking and nonblocking modes, stream-on failure recovery, stream-off with active buffers, suspend/resume discard, fatal queue error propagation, poll readiness, cache-hint behavior, media-request mutual exclusion, and debug counter balance under `CONFIG_VIDEO_ADV_DEBUG`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/videobuf2-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/videobuf2-dma-contig.h -->
# sources/distributed-fs/ceph-client/include/media/videobuf2-dma-contig.h

Purpose: This header exposes the contiguous-DMA videobuf2 memory allocator. It is intended for drivers whose hardware consumes a single DMA address per plane.

Important APIs, types, and functions: `vb2_dma_contig_plane_dma_addr()` retrieves a `dma_addr_t` cookie from a vb2 plane via `vb2_plane_cookie()` and dereferences it. `vb2_dma_contig_set_max_seg_size()` configures the device DMA segment limit. `vb2_dma_contig_clear_max_seg_size()` is an inline no-op in this tree. `vb2_dma_contig_memops` is the allocator operations table to assign to `vb2_queue.mem_ops`.

Control flow: A driver sets `q->mem_ops = &vb2_dma_contig_memops`, initializes its queue, and after buffers are allocated or imported uses `vb2_dma_contig_plane_dma_addr()` inside prepare/queue paths to program hardware DMA registers.

State and persistence behavior: The header adds no state. Allocator-private state lives behind the plane cookie and is owned by the implementation of `vb2_dma_contig_memops`.

Dependencies and integration points: It depends on `videobuf2-v4l2.h` and Linux DMA mapping. It integrates with vb2 MMAP, USERPTR, or DMABUF memory flows depending on allocator support and with hardware that requires physically or DMA-contiguously mapped buffers.

Risks: The inline helper assumes `vb2_plane_cookie()` returns a valid `dma_addr_t *`; callers must validate plane indexes and queue setup. Segment-size setup must match device DMA limitations or DMA mappings may exceed hardware capability. Contiguous allocation can fail under memory pressure.

Test signals: Exercise buffer allocation under fragmentation, DMA address retrieval for all planes, exported/imported dmabuf paths, segment-size configuration on probe/remove, and DMA programming with multi-planar formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/videobuf2-dma-contig.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/videobuf2-dma-sg.h -->
# sources/distributed-fs/ceph-client/include/media/videobuf2-dma-sg.h

Purpose: This header exposes the scatter/gather DMA videobuf2 memory allocator for hardware that can consume an SG table or an IOMMU mapping rather than a single contiguous DMA address.

Important APIs, types, and functions: `vb2_dma_sg_plane_desc()` returns the per-plane `struct sg_table *` stored as the vb2 plane cookie. `vb2_dma_sg_memops` is the allocator operations table for vb2 queues.

Control flow: Drivers select `vb2_dma_sg_memops` during queue initialization. When a buffer reaches the driver through `buf_queue`, the driver retrieves the SG table for each plane and programs DMA descriptors or IOMMU-backed hardware.

State and persistence behavior: State is delegated to the allocator-private cookie and SG table lifetime. The header itself has no persistent state.

Dependencies and integration points: It depends on `videobuf2-v4l2.h`, vb2 core cookie lookup, and Linux scatterlist infrastructure through the opaque `struct sg_table` pointer. It integrates with DMA-capable media drivers, USERPTR pinning, and DMABUF attachment paths.

Risks: Drivers must not retain SG table pointers beyond buffer ownership. Cache synchronization and map/unmap order are owned by vb2 memory ops and must not be bypassed. Hardware descriptor limits may be exceeded if queue validation does not account for worst-case SG fragmentation.

Test signals: Validate SG table retrieval for MMAP, USERPTR, and DMABUF, streaming with fragmented buffers, map/unmap balance, DMA descriptor bounds, and teardown while buffers are queued or exported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/videobuf2-dma-sg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/videobuf2-dvb.h -->
# sources/distributed-fs/ceph-client/include/media/videobuf2-dvb.h

Purpose: This header bridges videobuf2 queue/thread support with DVB demux, frontend, network, and adapter registration. It lets media drivers expose DVB streaming using vb2-backed queues.

Important APIs, types, and functions: `struct vb2_dvb` contains driver-filled name/frontend and a `struct vb2_queue`, plus DVB-managed state: mutex, feed count, demux, dmxdev, hardware and memory frontends, and DVB network object. `struct vb2_dvb_frontend` wraps one frontend and list node. `struct vb2_dvb_frontends` stores all frontends, adapter, active frontend ID, and gate control. Registration helpers are `vb2_dvb_register_bus()`, `vb2_dvb_unregister_bus()`, `vb2_dvb_alloc_frontend()`, `vb2_dvb_dealloc_frontends()`, `vb2_dvb_get_frontend()`, and `vb2_dvb_find_frontend()`.

Control flow: A driver allocates frontends, initializes each frontend's DVB and vb2 queue data, registers the bus with module/device/media-device context, and feeds transport-stream data through the vb2 queue/thread machinery. Unregistration tears down DVB demux devices, net interfaces, frontends, and vb2 queues.

State and persistence behavior: Runtime state includes frontend list membership, active frontend selection, feed count, DVB demux state, and the embedded vb2 queue. No persistent storage is defined. The lock protects feed and frontend management state.

Dependencies and integration points: It depends on DVB core headers, `videobuf2-v4l2.h`, and optionally a media controller device. It integrates with DVB adapters, demux devices, DVB network support, frontends, and the special-purpose `vb2_thread` API noted by the header.

Risks: The header notes that vb2 thread support is not purely core and has V4L2 dependencies, so layering is fragile. Multi-frontend gate and active ID management can race if not protected. Feed count leaks can keep hardware active after unregister. Queue shutdown must happen before DVB objects disappear.

Test signals: Register/unregister single and multi-frontend adapters, start/stop feeds repeatedly, exercise frontend gate selection, verify vb2 thread start/stop, hot-unplug during active demux, and media-controller integration when an `mdev` is supplied.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/videobuf2-dvb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/videobuf2-memops.h -->
# sources/distributed-fs/ceph-client/include/media/videobuf2-memops.h

Purpose: This header provides generic memory helper declarations shared by videobuf2 allocators, especially VMA reference tracking and user memory frame-vector helpers.

Important APIs, types, and functions: `struct vb2_vmarea_handler` stores a refcount pointer, a `put` callback, and callback argument for common VMA open/close handling. `vb2_common_vm_ops` is the shared `vm_operations_struct`. `vb2_create_framevec()` pins or collects pages for a userspace memory range with read/write direction, and `vb2_destroy_framevec()` releases that frame vector.

Control flow: Allocator implementations install `vb2_common_vm_ops` into VMAs and use `vb2_vmarea_handler` as VMA private data so mmap references keep buffers alive. USERPTR allocators call `vb2_create_framevec()` to acquire page/frame backing and later call `vb2_destroy_framevec()`.

State and persistence behavior: VMA state is refcounted through the handler and allocator private buffer object. Frame vectors are transient per buffer acquisition and are destroyed when a USERPTR buffer is released.

Dependencies and integration points: It depends on vb2 V4L2 wrapper types, Linux MM APIs, and refcounting. It integrates underneath dma-sg, vmalloc, and other vb2 memory allocators.

Risks: Incorrect refcount pointer or `put` callback wiring can leak or prematurely free buffers still mapped into userspace. USERPTR pinning must handle short ranges, write permissions, and process teardown. Shared VM ops must be paired with allocator-specific lifetime rules.

Test signals: mmap open/close reference balance, mapping after queue release, USERPTR acquisition for read and write queues, invalid user ranges, page-fault behavior, and allocator teardown with active VMAs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/videobuf2-memops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/videobuf2-v4l2.h -->
# sources/distributed-fs/ceph-client/include/media/videobuf2-v4l2.h

Purpose: This header adapts the vb2 core queue framework to the V4L2 userspace ABI. It defines the V4L2-specific buffer wrapper and public helpers used by V4L2 ioctl and file-operation implementations.

Important APIs, types, and functions: `struct vb2_v4l2_buffer` embeds `struct vb2_buffer` and adds V4L2 flags, field order, timecode, sequence, request fd, hold-capture flag, and V4L2 plane array. `to_vb2_v4l2_buffer()` casts from core buffer to V4L2 buffer. Queue wrappers include `vb2_find_buffer()`, `vb2_querybuf()`, `vb2_reqbufs()`, `vb2_create_bufs()`, `vb2_prepare_buf()`, `vb2_qbuf()`, `vb2_expbuf()`, `vb2_dqbuf()`, `vb2_streamon()`, `vb2_streamoff()`, `vb2_queue_init()`, `vb2_queue_init_name()`, `vb2_queue_release()`, `vb2_queue_change_type()`, and `vb2_poll()`. Ioctl helpers implement request/create/query/prepare/qbuf/dqbuf/stream/export/remove operations. File-operation helpers implement mmap, release, read, write, poll, and no-MMU get-unmapped-area. Request API helpers are `vb2_request_validate()` and `vb2_request_queue()`.

Control flow: V4L2 drivers wire these helpers into `v4l2_ioctl_ops` and `v4l2_file_operations`. The wrapper validates V4L2 buffer type and memory fields, maps request fds to media requests when available, calls vb2 core, and fills or consumes `struct v4l2_buffer` fields. Helper ioctl paths also serialize on `vb2_queue->lock` or `video_device->lock` and enforce queue ownership through `vb2_queue_is_busy()`.

State and persistence behavior: State extends vb2 core queue state with V4L2 metadata per buffer and optional subsystem flags such as mem2mem hold-capture support. Queue ownership in `q->owner` prevents unrelated file handles from manipulating the same queue.

Dependencies and integration points: It depends on `linux/videodev2.h`, `videobuf2-core.h`, `struct video_device`, `struct media_device`, V4L2 file handles, and media request support. It integrates directly with the V4L2 ioctl ABI, poll/read/write/mmap file operations, video-device unregister, and request API validation.

Risks: ABI translation must keep `VIDEO_MAX_FRAME/PLANES` aligned with vb2 constants, enforced by preprocessor checks. Request fd binding must not mix direct QBUF and request queueing. Queue ownership checks are critical for multi-open devices. `vb2_video_unregister_device()` should be used when release helpers are used, or stream shutdown ordering can be wrong during unbind.

Test signals: Run V4L2 compliance for query/req/create/prepare/qbuf/dqbuf/expbuf/streamon/streamoff, multi-open ownership cases, request API queuing, mem2mem hold-capture behavior, poll events, file read/write emulation, mmap/no-MMU paths, queue type changes before allocation, and unregistration with streaming active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/videobuf2-v4l2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/videobuf2-vmalloc.h -->
# sources/distributed-fs/ceph-client/include/media/videobuf2-vmalloc.h

Purpose: This header exposes the vmalloc-backed videobuf2 allocator for drivers that need CPU-addressable, virtually contiguous buffers rather than DMA-oriented memory.

Important APIs, types, and functions: The sole public symbol is `vb2_vmalloc_memops`, a `struct vb2_mem_ops` implementation suitable for assigning to `vb2_queue.mem_ops`.

Control flow: Drivers select vmalloc memory ops at queue setup. vb2 core calls the allocator for allocation, vaddr lookup, userspace mapping, and release according to the queue's I/O mode.

State and persistence behavior: Allocator-private buffer state lives behind vb2 plane cookies and memory private pointers. The header adds no state or persistence.

Dependencies and integration points: It depends on `videobuf2-v4l2.h` and integrates with CPU-driven capture/output drivers, virtual devices, test drivers, or transports that do not require physically contiguous DMA buffers.

Risks: vmalloc memory is not physically contiguous and is unsuitable for DMA engines that cannot scatter/gather or use an IOMMU. Drivers must use `vaddr` paths rather than assuming DMA cookies. Large vmalloc allocations can fail or fragment virtual address space.

Test signals: Validate read/write file I/O, mmap, CPU access through `vb2_plane_vaddr()`, allocation/release loops, and rejection or avoidance on drivers that require DMA addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/videobuf2-vmalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/vsp1.h -->
# sources/distributed-fs/ceph-client/include/media/vsp1.h

Purpose: This header defines Renesas R-Car VSP1/VSPX integration APIs for display-unit composition and ISP-assisted transfers. It is a cross-driver interface between VSP hardware drivers, DRM display pipelines, and ISP drivers.

Important APIs, types, and functions: Display-unit APIs include `vsp1_du_init()`, `vsp1_du_setup_lif()`, `vsp1_du_atomic_begin()`, `vsp1_du_atomic_update()`, `vsp1_du_atomic_flush()`, `vsp1_du_map_sg()`, and `vsp1_du_unmap_sg()`. Display structs include `vsp1_du_lif_config`, `vsp1_du_atomic_config`, `vsp1_du_crc_config`, `vsp1_du_writeback_config`, and `vsp1_du_atomic_pipe_config`. ISP APIs include `vsp1_isp_init()`, `vsp1_isp_get_bus_master()`, buffer allocation/free helpers, streaming start/stop, job prepare/run/release, and frame-end callbacks. `struct vsp1_isp_job_desc` describes optional ConfigDMA register pairs, RAW image format and address, and a prepared display-list pointer.

Control flow: A DU client initializes VSP1, configures the LIF, begins an atomic update, submits one plane config per RPF/input, and flushes with optional CRC or writeback config. Completion status is reported through an optional callback exactly once per flush. An ISP client initializes VSPX, allocates buffers through VSP, starts streaming with a frame-end callback, prepares job display lists from config and image descriptors, runs jobs, and releases prepared but unused jobs during stream stop.

State and persistence behavior: The header passes DMA addresses, SG tables, display-list pointers, and callbacks between drivers; persistent hardware state is owned by the implementation. `vsp1_isp_buffer_desc` stores CPU and DMA mappings for allocated buffers. `vsp1_isp_job_desc.dl` is a prepared runtime resource that must be released if not run.

Dependencies and integration points: It depends on scatterlists, DMA addresses, V4L2 rectangles and pixel formats, and V4L2 color metadata. It integrates Renesas DRM DU plane composition, VSP display lists, ISP RAW image transfers, ConfigDMA, CRC capture, writeback, and SG mapping.

Risks: The ConfigDMA comment documents dangerous hardware behavior for fewer than 17 register pairs, including corruption or freeze, so clients must pad or avoid small transfers. Atomic callbacks must be exactly once per flush. DMA address arrays and pixel formats must match plane layout. Prepared jobs leak resources if not run or released. SG map/unmap must be balanced.

Test signals: Atomic plane composition with multiple z positions, interlaced LIF setup, CRC source selection, writeback buffers, SG map/unmap failures, ISP buffer allocation/free, ConfigDMA pair counts below and above the safe threshold, job prepare/run/release ordering, and stream stop with pending jobs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/vsp1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/memory/renesas-rpc-if.h -->
# sources/distributed-fs/ceph-client/include/memory/renesas-rpc-if.h

Purpose: This header defines the Renesas RPC-IF core interface used by flash or xSPI front-end drivers to describe command/address/dummy/option/data phases and execute direct-map or manual transfers.

Important APIs, types, and functions: `enum rpcif_data_dir` identifies no-data, input, and output transfers. `struct rpcif_op` describes command and optional command phases, address phase, dummy cycles, option phase, and data phase including bus width, byte counts, DDR flags, values, direction, and in/out buffers. `enum rpcif_type` identifies supported controller families. `struct rpcif` stores device pointer, direct-map I/O base, size, and xSPI mode. Functions include `rpcif_sw_init()`, `rpcif_hw_init()`, `rpcif_prepare()`, `rpcif_manual_xfer()`, `rpcif_dirmap_read()`, and `xspi_dirmap_write()`.

Control flow: A front-end driver initializes software and hardware state, constructs an `rpcif_op` for a memory operation, calls `rpcif_prepare()` to configure controller state and compute direct-map offset/length, then either triggers `rpcif_manual_xfer()` or uses direct-map read/write helpers for memory-window operations.

State and persistence behavior: Controller runtime state lives in `struct rpcif` and the associated device driver. Operation descriptors are transient. Runtime power management is included by dependency, so implementation is expected to coordinate device power around transfers.

Dependencies and integration points: It depends on Linux device and PM-runtime infrastructure and integrates with Renesas R-Car/RZ RPC-IF and xSPI controller drivers, SPI-NOR/HyperFlash style memory clients, and memory-mapped I/O.

Risks: Incorrect bus widths, DDR flags, dummy cycles, or phase byte counts can corrupt flash transactions. Direct-map offset and length must be bounded by `rpcif.size`. Direction and buffer union must agree. Power state must be active during register and direct-map access.

Test signals: Probe both RPCIF and xSPI variants, execute read and write commands with single/dual/quad widths as supported, verify dummy-cycle handling, manual transfer error paths, direct-map boundary reads/writes, runtime PM suspend/resume, and HyperFlash initialization mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/memory/renesas-rpc-if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/misc/altera.h -->
# sources/distributed-fs/ceph-client/include/misc/altera.h

Purpose: This header exposes a small interface for loading Altera STAPL firmware over a caller-provided JTAG I/O callback.

Important APIs, types, and functions: `struct altera_config` carries an opaque device pointer, an action buffer, and a `jtag_io` callback that drives TMS/TDI and reads TDO. `altera_init()` accepts the config and a firmware blob. When the STAPL driver is not enabled by Kconfig, an inline stub logs a warning and returns success.

Control flow: A board or device driver prepares firmware, fills `altera_config`, and calls `altera_init()`. The enabled implementation interprets the firmware/action data and toggles JTAG through `jtag_io`. In disabled builds the call is a no-op except for a warning.

State and persistence behavior: The header defines no persistent state. Any JTAG state machine, firmware parsing state, or device-specific state is in the implementation or caller.

Dependencies and integration points: It relies on `struct firmware`, kernel logging, Kconfig symbols `CONFIG_ALTERA_STAPL` and module builds. It integrates with firmware loading and hardware-specific JTAG bit-banging callbacks.

Risks: The disabled stub returning 0 can mask missing FPGA programming support. The JTAG callback contract is low-level and easy to invert or time incorrectly. Firmware/action data validation is implementation-dependent.

Test signals: Enabled and disabled Kconfig builds, firmware load failures, callback TMS/TDI/TDO sequencing, action selection, device-specific JTAG timing, and callers that must treat the disabled-stub warning as degraded functionality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/misc/altera.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/misc/ocxl-config.h -->
# sources/distributed-fs/ceph-client/include/misc/ocxl-config.h

Purpose: This header lists OpenCAPI 3.0 PCI DVSEC capability IDs and register offsets used by the OCXL configuration parser and setup code.

Important APIs, types, and functions: It defines `OCXL_EXT_CAP_ID_DVSEC`, common DVSEC vendor and ID offsets, TL DVSEC offsets for backoff timers and receive/send capabilities/rates, Function DVSEC offsets for AFU index and actag configuration, AFU information offsets, AFU control offsets for termination, enable, PASID, and actag fields, and vendor DVSEC offsets for version and reset/reload fields.

Control flow: OCXL config code scans PCI extended capabilities for DVSEC entries, compares IDs, and uses these offsets to read and write OpenCAPI function, TL, AFU info, AFU control, and vendor-specific configuration.

State and persistence behavior: The header has no runtime state. The constants address persistent PCI config-space registers whose values configure AFU and link behavior.

Dependencies and integration points: It is consumed by `ocxl.h` implementation functions and lower-level PCI config access. It integrates with OpenCAPI device discovery, PASID and actag assignment, TL negotiation, AFU enable/disable, and vendor reset handling.

Risks: Constants must match the OpenCAPI 3.0 specification. Wrong offsets can write unrelated PCI config fields and break devices. Endianness and field width are handled by implementation, not this header.

Test signals: PCI config parser tests should cover DVSEC discovery, multiple AFUs, absent optional DVSECs, TL negotiation, PASID/actag programming, AFU enable state transitions, and vendor reset/reload register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/misc/ocxl-config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/misc/ocxl.h -->
# sources/distributed-fs/ceph-client/include/misc/ocxl.h

Purpose: This header defines the in-kernel OpenCAPI library API used by OCXL-aware drivers. It abstracts PCI function discovery, AFU enumeration and reference management, context allocation/attachment, AFU IRQs, global MMIO access, and compatibility configuration/link helpers.

Important APIs, types, and functions: Configuration structs are `ocxl_afu_config` and `ocxl_fn_config`. Opaque objects are `ocxl_afu`, `ocxl_fn`, and `ocxl_context`. Device lifecycle includes `ocxl_function_open()`, `ocxl_function_close()`, `ocxl_function_afu_list()`, `ocxl_function_fetch_afu()`, `ocxl_afu_get()`, and `ocxl_afu_put()`. Context APIs include `ocxl_context_alloc()`, `ocxl_context_free()`, `ocxl_context_attach()`, and `ocxl_context_detach()`. IRQ APIs allocate/free IRQ IDs, get trigger page addresses, and install handlers. AFU metadata APIs expose config and private data. Global MMIO helpers read, write, set, and clear 32/64-bit registers with selected endian handling. Compatibility helpers read config space, set PASID/actag/AFU state/TL, terminate PASIDs, set up and release links, add/remove process elements, and allocate/free link IRQs.

Control flow: A driver opens an OCXL PCI function, enumerates or fetches AFUs, reads config, allocates a context for an AFU, attaches an `mm_struct` and AMR to grant process access, allocates AFU IRQs and handlers, programs AFU global MMIO, then detaches/frees context and closes the function during teardown. Compatibility flows perform lower-level PCI config and link setup for drivers that still manage function state directly.

State and persistence behavior: The API manages references for AFUs, opaque function/context lifetime, PASID and actag hardware allocation, link process elements, and IRQ registrations. `ocxl_function_close()` frees AFUs retrieved from the function and detaches associated contexts, but callers still free contexts. Hardware config persists in PCI/OpenCAPI device state until changed or reset.

Dependencies and integration points: It depends on PCI, MM, IRQ handling, address spaces, keys of process address space state, and OpenCAPI platform link services. It integrates with cxlflash compatibility paths and hardware drivers that need shared OCXL services.

Risks: The termination API documents that hardware can terminate only one PASID at a time, so callers must serialize. Context attach/detach must match process lifetime and MM ownership. IRQ private-data callbacks must not use freed memory. Endian selection for MMIO must match AFU registers. Closing a function while external references or contexts remain can lead to use-after-free if reference discipline is wrong.

Test signals: AFU enumeration and refcounting, function open/close error paths, context attach/detach under process exit, IRQ allocation/handler/free, MMIO endian read/write/set/clear, PASID and actag programming, link setup/add/remove PE, PASID termination timeout, and compatibility with cxlflash-style direct config flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/misc/ocxl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/6lowpan.h -->
# sources/distributed-fs/ceph-client/include/net/6lowpan.h

Purpose: This header defines 6LoWPAN core data structures and helpers for IPv6 header compression/decompression over low-power link layers such as IEEE 802.15.4 and BTLE.

Important APIs, types, and functions: Constants define EUI-64 length, next-header compression bounds, IPHC buffer sizes, context table size, and dispatch bytes for raw IPv6 and IPHC. Helpers `lowpan_is_ipv6()` and `lowpan_is_iphc()` classify dispatch bytes. `struct lowpan_iphc_ctx` and `struct lowpan_iphc_ctx_table` represent compression contexts with active and compression flags. `struct lowpan_dev` is the per-netdev private root with link-layer type, debugfs entry, context table, and flexible link-layer private data. IEEE 802.15.4 specific structs track neighbor short address, lowpan device info, and skb control block fragmentation fields. Address helpers build link-local IPv6 addresses from EUI-64 or EUI-48 link-layer addresses. `lowpan_fetch_skb()` safely pulls inline header data. `lowpan_register_netdevice()`, `lowpan_register_netdev()`, unregister variants, `lowpan_header_decompress()`, and `lowpan_header_compress()` are the public operations.

Control flow: A link-layer adaptation driver allocates a netdev with `LOWPAN_PRIV_SIZE()`, registers it with a lowpan link-layer type, and uses compression/decompression around packet transmit and receive. Receive paths inspect the dispatch byte, fetch compressed fields from the skb, reconstruct IPv6 headers using link-layer addresses and context table state, and pass IPv6 packets upward. Transmit paths compress IPv6 headers into IPHC form with optional next-header compression and push link-layer frames.

State and persistence behavior: Runtime state lives in `lowpan_dev`, the IPHC context table guarded by a spinlock, per-neighbor short addresses, fragment tags, and skb control blocks. Context active/compression flags influence compression decisions until changed by the context ops implementation.

Dependencies and integration points: It depends on IPv6, net namespaces, debugfs, mac802154, sk_buff helpers, and net_device private storage. It integrates with IEEE 802.15.4 neighbors, fragmentation/reassembly code, and IPv6 packet paths.

Risks: `lowpan_fetch_skb()` returns true on failure, which can be misread by callers. Header compression requires sufficient headroom and unshared skbs on transmit. Context table updates must be synchronized. Address reconstruction must correctly flip the universal/local bit for EUI-64 but not for all EUI-48 variants. Fragment tag handling is small and wraparound-sensitive.

Test signals: Dispatch classification, raw IPv6 and IPHC receive, EUI-64/EUI-48 link-local reconstruction, context-based address compression, insufficient skb pull failures, transmit with minimal headroom, short-address validation, fragment tag wraparound, and registration/unregistration for BTLE and IEEE 802.15.4 devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/6lowpan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/9p/9p.h -->
# sources/distributed-fs/ceph-client/include/net/9p/9p.h

Purpose: This header defines the 9P wire-protocol constants, debug flags, message IDs, open/permission flags, qid/stat structures, lock/statfs structures, and the packet buffer representation used by the Linux 9P client.

Important APIs, types, and functions: `enum p9_debug_flags` selects protocol, VFS, conversion, mux, transport, packet, fscache, cache, and mmap tracing. `enum p9_msg_t` enumerates 9P2000, 9P2000.u, and 9P2000.L request/response message numbers. `enum p9_open_mode_t`, `enum p9_perm_t`, and `enum p9_qid_t` model open flags, Plan 9 permission bits, and qid type bits. Dotl constants define Linux-like open and at flags plus POSIX lock constants. Core structs include `p9_qid`, `p9_wstat`, `p9_stat_dotl`, `p9_iattr_dotl`, `p9_flock`, `p9_getlock`, `p9_rstatfs`, and `p9_fcall`. Functions include `p9_errstr2errno()` and `p9_error_init()`.

Control flow: The client and VFS layers build `p9_fcall` packets using message IDs and protocol-specific structs, send them through a transport, parse responses, and translate qids/stats/locks into Linux VFS state. Server error strings are translated to errno values through the error map.

State and persistence behavior: This header models wire and per-message state. `p9_fcall` tracks message size, type, tag, current marshalling offset, capacity, slab cache, payload pointer, and zero-copy flag. QID version/path values are used by higher layers for cache coherency but are provided by the server.

Dependencies and integration points: It depends on kernel uid/gid types and allocation support through users of `kmem_cache`. It integrates with `net/9p/client.h`, transport modules, v9fs VFS code, fscache, and trace/debug infrastructure.

Risks: Message numeric values are ABI and must not change. Dotl, dotu, and legacy protocol fields differ; using the wrong struct for a negotiated protocol breaks interoperability. `p9_fcall` offset/capacity accounting must be exact to avoid packet overflow or truncation. Error-string translation depends on server text and length.

Test signals: Protocol negotiation for legacy, 9P2000.u, and 9P2000.L; marshalling/unmarshalling for every message ID; stat and stat_dotl round trips; lock status handling; qid version cache invalidation; large read/write header size limits; and debug packet dumping under `CONFIG_NET_9P_DEBUG`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/9p/9p.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/9p/client.h -->
# sources/distributed-fs/ceph-client/include/net/9p/client.h

Purpose: This header defines the Linux 9P client state machine and high-level RPC API used by v9fs and other in-kernel consumers to create sessions, manage fids, issue file operations, and communicate through pluggable transports.

Important APIs, types, and functions: `enum p9_proto_versions` captures legacy, 9P2000.u, and 9P2000.L. `enum p9_trans_status` tracks connection health from connected through begin-disconnect, disconnected, and hung. `enum p9_req_status_t` tracks request lifecycle. `struct p9_req_t` owns request/response fcalls, waitqueue, refcount, transport error, and list node. `struct p9_client` stores lock, negotiated msize, protocol, transport module, status, transport private data, fcall slab cache, transport options, idr maps for fids and requests, and client name. Option structs cover client, fd, rdma, and session mount options, aggregated in `struct v9fs_context`. `struct p9_fid` tracks fid number, refcount, mode, qid, iounit, uid, readdir state, and inode/dentry lists. The API includes client create/destroy/disconnect, attach/walk/open/create/link/symlink/mknod/mkdir/read/write/readdir/stat/wstat/setattr/getattr/xattr/readlink/lock/fsync/remove/unlink operations, fcall cleanup, tag lookup, request refcounting, fid refcounting, parser helpers, protocol checks, and module init/exit.

Control flow: Mount context options are parsed into `v9fs_context`, `p9_client_create()` negotiates a client and transport, and `p9_client_attach()` obtains a root fid. VFS operations call high-level `p9_client_*` functions, which allocate request tags, marshal fcalls, send through the transport, wait on `p9_req_t.wq`, parse responses, update fid/qid/iounit state, and return Linux errors. Fid references are acquired with `p9_fid_get()` and released with `p9_fid_put()`, with the final put clunking the server fid.

State and persistence behavior: Client state is runtime-only and protected by `client->lock`, idr maps, request refcounts, and fid refcounts. Fids may be cached on dentries or inodes through hlist nodes. Request status advances through allocation, unsent, sent, received, flushed, or error. Disconnect status gates new RPCs and cancels in-flight work.

Dependencies and integration points: It depends on UTS names, IDR, tracepoints, netfs write subrequests, fs_context, seq_file, iov_iter, VFS uid/gid, and `struct p9_trans_module`. It integrates with v9fs mount/session state, transport backends, netfs helpers, tracepoints, and fscache/cache options.

Risks: Final `p9_fid_put()` sends `TCLUNK`, so calling context must tolerate RPC on release and avoid holding locks that can deadlock. Request refcounts must protect callbacks racing with cancellation/disconnect. Direct QID and iounit state comes from the server and must be validated by callers. Protocol-version checks are required before dotu/dotl-specific calls. Large `msize` and zero-copy paths must align with transport limits.

Test signals: Mount option parsing, protocol negotiation, attach/walk/open/create/read/write/stat/lock/xattr/readlink sequences for all protocol versions, fid get/put tracepoints and final clunk, request cancellation/flush, disconnect during active RPCs, transport errors, idr tag reuse, netfs write subrequest path, and readdir offset handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/9p/client.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/9p/transport.h -->
# sources/distributed-fs/ceph-client/include/net/9p/transport.h

Purpose: This header defines the pluggable transport module interface for 9P clients, plus default port and RDMA queue settings.

Important APIs, types, and functions: Constants define reserved-port bounds, FD/TCP port 564, RDMA port 5640, default RDMA SQ/RQ depths, and RDMA timeout. `struct p9_trans_module` contains module list node, name, max packet size, pooled response-buffer flag, default flag, vmalloc-buffer support, owner module, create/close/request/cancel/cancelled callbacks, zero-copy request callback, and option display callback. Registration helpers are `v9fs_register_trans()`, `v9fs_unregister_trans()`, `v9fs_get_trans_by_name()`, `v9fs_get_default_trans()`, and `v9fs_put_trans()`. `MODULE_ALIAS_9P()` declares transport module aliases.

Control flow: A transport backend registers a static `p9_trans_module`. Client creation selects a backend by name or default, gets its module reference, calls `create()` with the fs context, and later sends requests through `request()` or `zc_request()`. Cancellation invokes `cancel()` and then `cancelled()` if no reply will arrive. Destroy calls `close()` and puts the module.

State and persistence behavior: Transport registry state is global and protected by the 9P transport lock in the implementation. Per-client transport state is opaque in `p9_client.trans`. No persistent storage is defined.

Dependencies and integration points: It depends on Linux modules, seq_file, fs_context, iov_iter, and the 9P client/request types. It integrates with TCP, FD, virtio, RDMA, or other transport implementations.

Risks: Backends must honor `maxsize` and pooled-buffer restrictions during msize negotiation. `supports_vmalloc` must be accurate or zero-copy/vmalloc buffers can break DMA transports. Cancellation races with late replies are a core transport hazard. Module reference handling must prevent unloading while clients exist.

Test signals: Register/unregister ordering, default transport selection, per-transport option printing, request and zero-copy paths, cancellation before send and after send, module alias autoloading, vmalloc buffer behavior, RDMA pooled-response sizing, and teardown with in-flight requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/9p/transport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/Space.h -->
# sources/distributed-fs/ceph-client/include/net/Space.h

Purpose: This small legacy header declares unified Ethernet adapter probe entry points intended to assign standard `ethN` style names.

Important APIs, types, and functions: It declares `ne_probe(int unit)` and `cs89x0_probe(int unit)`, both returning `struct net_device *`.

Control flow: Legacy network initialization code can call these probe functions with a unit number to discover or instantiate NE-compatible or CS89x0 Ethernet devices.

State and persistence behavior: The header has no state. Device state is returned as `struct net_device` objects owned by probe implementations and the netdev core.

Dependencies and integration points: It forward-uses `struct net_device` and integrates with legacy Ethernet probe code and net_device registration.

Risks: This header lacks include guards and includes no declaration of `struct net_device`, so it depends on caller include order. Legacy probing can conflict with modern bus-managed probing if both are active.

Test signals: Build coverage for include order, successful and failed probe paths for each unit, netdev naming, and coexistence with platform or bus-discovered Ethernet drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/Space.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/act_api.h -->
# sources/distributed-fs/ceph-client/include/net/act_api.h

Purpose: This header defines the public traffic-control action API shared by classifiers, qdiscs, action implementations, and flow offload integration.

Important APIs, types, and functions: `struct tcf_idrinfo` stores the per-net action IDR and mutex. `struct tc_action` contains action ops, type, IDR info, index, refcount, bind count, action code, timing, software and hardware stats, drops/overlimits, rate estimator, locks, percpu stats, user cookie, goto chain, flags, hardware stats preferences, and in-hardware count. `struct tc_action_ops` defines action kind/id, per-net ID, object size, owner module, act/dump/cleanup/lookup/init/walk/stats/get-size/get-device/get-psample/offload callbacks. Helpers update last-use timing, dump timing, translate hardware stats flags, initialize/exit per-net action state, create/search/insert/cleanup/release IDR entries, register/unregister actions, load/init/destroy/execute/dump action arrays, update software/hardware stats, reoffload, validate/set control actions, and transmit fragmented packets when enabled.

Control flow: Action modules register `tc_action_ops` with per-net operations. Netlink parsing loads ops, initializes one or more action instances, allocates or binds IDR entries, and attaches actions to classifier/qdisc rules. Packet processing executes action arrays under RCU BH context through the `act` callback, updates stats, and returns control actions such as ok, drop, shot, redirect, or goto chain. Dump paths collect timing, stats, cookies, and hardware state for netlink replies.

State and persistence behavior: Action instances are runtime kernel objects keyed by per-net IDR index and lifetime-managed by refcount and bind count. Stats may be global or percpu. User cookies, rate estimators, and goto chains are RCU-managed. Timing fields store install, lastuse, firstuse, and expires in jiffies.

Dependencies and integration points: It depends on refcounting, flow offload, qdisc internals, packet scheduler uAPI, net namespaces, generic netns storage, RCU, IDR, and optional `CONFIG_NET_CLS_ACT` and `CONFIG_INET`. It integrates with tc netlink, classifier chains, flow hardware offload, psample, and dev queue transmit.

Risks: The `act` callback runs under RCU BH lock, so blocking is unsafe. Refcount and bind count must distinguish bound filter use from temporary references. Per-cpu and global stats paths must not race. Hardware stats flags are user-visible, and invalid values warn and degrade to dont-care. Goto-chain RCU lifetime must be respected. The no-`CONFIG_NET_CLS_ACT` stubs mean callers must handle unavailable action infrastructure.

Test signals: Register/unregister each action, IDR allocation collisions and replacement, bind/unbind/refcount release, packet action execution and control flow, stats updates under percpu and global modes, hardware offload and reoffload callbacks, netns teardown, netlink dump size, invalid hw_stats values, and builds with `CONFIG_NET_CLS_ACT` disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/act_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/addrconf.h -->
# sources/distributed-fs/ceph-client/include/net/addrconf.h

Purpose: This header declares IPv6 address autoconfiguration, address lookup, multicast/anycast, notifier, and inet6 device lifetime helpers. It is the internal contract for IPv6 addrconf and related network subsystems.

Important APIs, types, and functions: Constants define router solicitation timing, minimum valid lifetime, temporary address lifetimes from RFC 8981, address check cadence, max addresses, and timer fuzz. `struct prefix_info` maps the 32-byte IPv6 Prefix Information Option with endian-specific flag bitfields and a static size assertion. `struct in6_validator_info`, `struct ifa6_config`, and `struct inet6_fill_args` carry address validation, address creation, and netlink fill context. Public functions include addrconf init/cleanup, add/delete/set-dst ioctls, IPv6 address and prefix checks, source address selection, link-local retrieval, solicited-node multicast join/leave, link-local addition, prefix receive/add, address label init/cleanup/query, multicast socket/device operations, MLD checks, prefix receive, anycast operations, inet6 notifier registration/calls, netconf notifications, proc init/exit, and netlink fill helpers. Inline helpers build EUI-48/EUI-64 interface identifiers, convert lifetimes safely, get/put/hold `inet6_dev` and `inet6_ifaddr`, compute solicited multicast addresses, and classify common multicast and ISATAP addresses.

Control flow: IPv6 device initialization creates inet6_dev state and addrconf timers. Router advertisements are parsed into `prefix_info`, validated, and may add autoconfigured addresses and routes. Address add/delete ioctls and netlink paths use `ifa6_config`. Multicast and anycast joins update per-socket and per-device membership. Notifier chains validate and publish address events. Source address selection and address checks serve socket routing and packet paths.

State and persistence behavior: Runtime state is in `inet6_dev`, `inet6_ifaddr`, multicast/anycast membership objects, address label tables, device config, and timers. References use `refcount_t`; `in6_dev_get()` acquires a reference while `__in6_dev_get()` is RCU/RTNL-only and unrefcounted. Lifetimes may be infinite or finite and are converted carefully to avoid overflow.

Dependencies and integration points: It depends on IPv6 core headers, net_device, inet6 device structs, neighbor discovery, MLD, multicast, anycast, notifier chains, netlink, procfs, RCU, RTNL, and sk_buff helpers. It integrates with routing, sockets, device notifiers, RA processing, duplicate address detection, and multicast snooping exceptions.

Risks: Include-order and endian correctness matter for `prefix_info` bitfields. Using unrefcounted inet6_dev pointers outside RCU/RTNL is unsafe. Lifetime conversion must avoid overflow and handle infinity. Multicast packet inspection must ensure skb data is pulled before dereference. zSeries EUI-48 dev_id handling intentionally differs from normal universal/local bit inversion.

Test signals: Prefix-info size and flag interpretation on big and little endian, SLAAC address creation and expiration, temporary address lifetimes, DAD failure, source address selection, link-local generation for normal and dev_id devices, multicast/anycast join/drop, notifier validation failures, RCU lifetime checks, MLD packet classification, and timer fuzz behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/addrconf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/af_ieee802154.h -->
# sources/distributed-fs/ceph-client/include/net/af_ieee802154.h

Purpose: This header defines the userspace socket address and socket-option ABI for IEEE 802.15.4 networking.

Important APIs, types, and functions: Address type constants distinguish none, 16-bit short address plus PAN ID, and 64-bit long address plus PAN ID. `IEEE802154_ADDR_LEN` is 8. `struct ieee802154_addr_sa` stores address type, PAN ID, and either hardware long address or short address. Broadcast and undefined PAN/address constants are defined. `struct sockaddr_ieee802154` combines socket family and address. Socket option constants under `SOL_IEEE802154` cover want-ack, security, security level, and want-LQI, with defaults and on/off values.

Control flow: Userspace fills `sockaddr_ieee802154` for bind/connect/sendto. Kernel AF_IEEE802154 code interprets address type and PAN/address values, applies socket options, and passes frames to IEEE 802.15.4 lower layers.

State and persistence behavior: The header defines ABI structures only. Runtime socket state lives in AF_IEEE802154 implementation and per-socket options.

Dependencies and integration points: It depends on `linux/socket.h` for `sa_family_t` and integrates with WPAN/IEEE 802.15.4 sockets, 6LoWPAN, MAC802154, and userspace tools.

Risks: Address union interpretation depends on `addr_type`. `SOL_IEEE802154` value and option numbers are ABI. Security option semantics must match MAC-layer implementation. Short address and PAN broadcast values overlap with valid-looking numeric values and must be treated specially.

Test signals: Bind/connect/sendto with short, long, broadcast, and undefined addresses; getsockopt/setsockopt for ack/security/LQI; ABI layout checks; and interoperability with 6LoWPAN over IEEE 802.15.4.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/af_ieee802154.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/af_rxrpc.h -->
# sources/distributed-fs/ceph-client/include/net/af_rxrpc.h

Purpose: This header defines the kernel-service interface for AF_RXRPC users such as kAFS. It provides call creation, data send/receive, peer management, security challenge handling, notifications, and socket option helpers.

Important APIs, types, and functions: `enum rxrpc_interruptibility` controls whether calls can be interrupted or canceled while waiting for slots. `enum rxrpc_oob_type` currently identifies security challenges. `rxrpc_debug_id` supports tracing. `struct rxrpc_kernel_ops` provides callbacks for new calls, discarded calls, user attachment, and out-of-band packets. Notification typedefs report receive and end-of-transmit events. Public APIs set notifications, begin calls, send data, receive data, abort/shutdown/put calls, look up/get/put peers, query remote addresses and RTT, set/get peer app data, pre-charge accept slots, set transmit length, check call life, configure security keyring/min-level/manage-response, dequeue/query/free OOB packets, inspect/respond/reject security challenges, and query call security.

Control flow: A kernel application configures callbacks on an rxrpc socket, looks up a peer or receives a new call notification, begins or accepts calls, sends request data, receives response data, handles end/receive notifications, and finally shuts down and puts the call. Security challenge OOB packets are dequeued, queried, and answered or rejected by rxkad/rxgk helpers.

State and persistence behavior: Runtime state is held in opaque `rxrpc_call` and `rxrpc_peer` objects plus socket state. Peer app data is an unsigned long stored with the peer. Call refs and peer refs must be put explicitly. Security keyrings and minimum levels persist in socket configuration while set.

Dependencies and integration points: It depends on rxrpc uAPI, ktime, keys, sockets, sk_buffs, Kerberos buffers, and abort reasons. It integrates with AF_RXRPC core, kAFS, key management, security protocols rxkad/rxgk, and kernel networking.

Risks: Call and peer lifetime is reference counted and asynchronous notifications can race with shutdown. Interruptibility selection changes blocking semantics and cancellation windows. Security challenge packets must be freed or responded to exactly once. Application callback code must obey socket locking and context rules from the implementation. Tx total length changes must match protocol framing.

Test signals: Client and server call lifecycles, interruptible and uninterruptible waits, send/receive short and full transfers, abort/shutdown behavior, peer lookup/refcount/appdata, RTT query, OOB challenge dequeue/query/reject/respond for rxkad and rxgk, socket security options, and race tests for call life during callback delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/af_rxrpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/af_unix.h -->
# sources/distributed-fs/ceph-client/include/net/af_unix.h

Purpose: This header defines core AF_UNIX internal socket structures and helpers shared by Unix-domain socket implementation and in-kernel users.

Important APIs, types, and functions: `unix_get_socket()` returns a `struct unix_sock *` for a file when Unix sockets are enabled, or NULL in disabled builds. `struct unix_address` is a refcounted variable-length sockaddr container. `struct scm_stat` tracks file-descriptor passing counts. `struct unix_sock` embeds `struct sock` as its first member and adds bound address, path, I/O and bind mutexes, peer and listener pointers, graph vertex pointer, state lock, peer waitqueue, peer wake entry, SCM stats, in-queue length, recvmsg inq flag, and optional out-of-band skb. Macros `unix_sk()`, `unix_peer()`, `unix_state_lock()`, and `unix_state_unlock()` provide casts and locking.

Control flow: AF_UNIX implementation allocates sockets as `unix_sock`, binds addresses and paths, connects peers/listeners, transfers data and SCM_RIGHTS, wakes peers through the peer waitqueue, and uses the state spinlock for peer/state transitions. In-kernel users can recover unix socket state from a file via `unix_get_socket()`.

State and persistence behavior: Socket state is runtime-only but may reference filesystem paths and passed file descriptors. Address lifetime is refcounted. Peer/listener links, waitqueue entries, and optional OOB skb require careful teardown during close and garbage collection.

Dependencies and integration points: It depends on atomic/refcounting, mutexes, net core, path handling, spinlocks, waitqueues, sock core, and the Unix socket uAPI. It integrates with SCM_RIGHTS accounting, AF_UNIX garbage collection, filesystem pathname sockets, and optional out-of-band support.

Risks: `struct sock` must remain the first member for casting. Peer pointer and waitqueue lifetime are race-prone during disconnect and close. File descriptor passing can create reference cycles and pressure GC. Disabled `CONFIG_UNIX` builds return NULL, so callers must handle unavailable Unix sockets. Optional OOB state changes struct behavior under config.

Test signals: Stream/datagram/seqpacket bind-connect-close cycles, pathname and anonymous sockets, SCM_RIGHTS accounting and GC, peer wakeups during shutdown, concurrent connect/disconnect, `unix_get_socket()` enabled and disabled builds, recvmsg inq behavior, and OOB support when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/af_unix.h -->
