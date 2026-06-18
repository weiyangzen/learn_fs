# subset-b-004051 research

This grouped report covers videobuf2 core, V4L2/DVB adapters, memory backends, and DVB demux device build/runtime glue under `sources/distributed-fs/ceph-client/drivers/media`. Each section preserves the original source path for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/videobuf2/videobuf2-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/common/videobuf2/videobuf2-core.c

## Purpose
`videobuf2-core.c` is the generic videobuf2 queue engine. It owns allocation, state transitions, cache synchronization hooks, queueing/dequeueing, streaming start/stop, mmap/export support, compatibility read/write file I/O, and the special thread-I/O path used by DVB helpers. It is intentionally format-agnostic: subsystem-specific code supplies `vb2_buf_ops` to translate userspace buffer structures and drivers supply `vb2_ops` plus `vb2_mem_ops`.

## Important APIs, Types, and Functions
The exported core APIs include `vb2_core_reqbufs()`, `vb2_core_create_bufs()`, `vb2_core_prepare_buf()`, `vb2_core_qbuf()`, `vb2_core_dqbuf()`, `vb2_core_streamon()`, `vb2_core_streamoff()`, `vb2_core_expbuf()`, `vb2_mmap()`, `vb2_core_poll()`, `vb2_core_queue_init()`, `vb2_core_queue_release()`, `vb2_buffer_done()`, `vb2_queue_error()`, `vb2_wait_for_all_buffers()`, `vb2_read()`, `vb2_write()`, `vb2_thread_start()`, and `vb2_thread_stop()`. Internal workhorses include `__vb2_queue_alloc()`, `__vb2_queue_free()`, `__buf_prepare()`, `__prepare_mmap()`, `__prepare_userptr()`, `__prepare_dmabuf()`, `vb2_start_streaming()`, `__vb2_queue_cancel()`, and `__vb2_perform_fileio()`. Key data is in `struct vb2_queue`, `struct vb2_buffer`, per-plane `struct vb2_plane`, `queued_list`, `done_list`, `done_wq`, `done_lock`, `mmap_lock`, `owned_by_drv_count`, and state values such as `VB2_BUF_STATE_DEQUEUED`, `QUEUED`, `ACTIVE`, `DONE`, `ERROR`, and `IN_REQUEST`.

## Control Flow
Initialization validates required queue callbacks, memory ops, type, io modes, request constraints, buffer limits, and locking, then initializes queues, waitqueues, and DMA direction. `REQBUFS`/`CREATE_BUFS` validate memory type, call driver `queue_setup`, allocate `vb2_buffer` instances, allocate memory for MMAP buffers, initialize driver buffer state, and return first/count information. Preparation fills internal plane metadata through `buf_ops`, attaches or pins USERPTR/DMABUF memory when needed, runs driver validation/prepare callbacks, and performs memory `prepare` cache synchronization. `QBUF` either binds a buffer to a media request or queues it, optionally starts streaming when enough buffers are queued, and hands buffers to the driver through `buf_queue`. Drivers complete buffers with `vb2_buffer_done()`, which moves them to `done_list` or back to queued state and wakes waiters. `DQBUF` waits unless nonblocking, verifies output planes, calls driver `buf_finish`, fills userspace data through `buf_ops`, removes the buffer from vb2 queues, and releases request references. `STREAMOFF` and queue release cancel streaming, call stop/unprepare callbacks, force-reclaim any leaked active buffers, clear lists, finish prepared memory, and return buffers to dequeued state.

## State and Persistence
All state is in-memory queue state; there is no persistence beyond open file/device lifetime. The queue tracks ownership (`owner` in wrappers), memory mode, allocated buffer bitmap, prepared/synced flags, request mode (`uses_requests` versus `uses_qbuf`), streaming status, waiting flags, done/error status, and the number of driver-owned buffers. MMAP buffer lifetime can outlive `REQBUFS(0)` through VMA refcounts exposed by memory backends; the core checks `num_users()` to decide whether buffers are still externally mapped. File I/O creates transient MMAP buffers and stores progress in `struct vb2_fileio_data`.

## Dependencies and Integration Points
The file integrates with `media/videobuf2-core.h`, subsystem buffer ops from `videobuf2-v4l2.c` and DVB glue, allocator ops from dma-contig/dma-sg/vmalloc backends, DMA-BUF APIs, media request objects, waitqueues, kthreads/freezer, and V4L2 memory flag constants used for cache/coherency hints. Drivers must implement `queue_setup` and `buf_queue`, and often implement `buf_init`, `buf_prepare`, `buf_finish`, `start_streaming`, `stop_streaming`, and request-specific completion callbacks.

## Risks and Edge Cases
Most risks are lifecycle balance issues: driver `start_streaming()` and `stop_streaming()` must return all active buffers with `vb2_buffer_done()`, `buf_init`/`buf_cleanup` and `buf_prepare`/`buf_finish` must balance, and media request references must not be dropped from interrupt context. Mixed request and non-request queueing is explicitly rejected, and request-capable queues cannot use `min_queued_buffers`. USERPTR/DMABUF re-acquisition paths reset timestamps and call cleanup/init when memory changes; errors there must not leave stale `mem_priv` pointers. Offset cookies encode buffer and plane indexes and are bounded by `MAX_BUFFER_INDEX`; mmap must reject file I/O and non-MMAP queues. Blocking `DQBUF` uses `waiting_in_dqbuf` to reject another dup'ed fd waiting on the same queue. Cache hint flags can skip allocator sync, so drivers must advertise them only when safe.

## Test Signals
Useful tests include `v4l2-compliance` streaming, mmap, USERPTR, DMABUF import/export, request API queueing, poll/read/write paths, and streamon/streamoff error injection. Kernel logs with `CONFIG_VIDEO_ADV_DEBUG` should show balanced callback counters. Runtime signals include no stuck waiters after streamoff/error, `owned_by_drv_count` returning to zero, correct `EAGAIN`/`EPIPE`/`EIO` behavior, valid mmap offsets for all planes, successful `EXPBUF`, and no use-after-free under mapped-buffer orphaning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/videobuf2/videobuf2-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/videobuf2/videobuf2-dma-contig.c -->
# sources/distributed-fs/ceph-client/drivers/media/common/videobuf2/videobuf2-dma-contig.c

## Purpose
`videobuf2-dma-contig.c` implements the vb2 memory backend for devices that require one DMA-contiguous address range. It supports MMAP allocation, USERPTR pin/import, DMABUF import, and exporting MMAP buffers as dma-bufs, with separate handling for coherent and non-coherent DMA memory.

## Important APIs, Types, and Functions
The exported memops table is `vb2_dma_contig_memops`, and the helper export is `vb2_dma_contig_set_max_seg_size()`. `struct vb2_dc_buf` stores the device, virtual address, size, DMA address cookie, DMA direction, attributes, scatterlist, frame vector, mmap handler/refcount, dma-buf attachment, owning `vb2_buffer`, and non-coherent flag. Important functions include `vb2_dc_alloc()`, `vb2_dc_alloc_coherent()`, `vb2_dc_alloc_non_coherent()`, `vb2_dc_put()`, `vb2_dc_prepare()`, `vb2_dc_finish()`, `vb2_dc_mmap()`, `vb2_dc_get_userptr()`, `vb2_dc_put_userptr()`, `vb2_dc_attach_dmabuf()`, `vb2_dc_map_dmabuf()`, `vb2_dc_unmap_dmabuf()`, `vb2_dc_get_dmabuf()`, and `vb2_dc_get_contiguous_size()`.

## Control Flow
For MMAP buffers, allocation chooses `dma_alloc_attrs()` for coherent memory or `dma_alloc_noncontiguous()` for non-coherent memory, records a device reference, initializes a VMA refcount handler, and returns private allocator state to vb2. MMAP maps coherent memory with `dma_mmap_attrs()` or non-coherent memory with `dma_mmap_noncontiguous()`. USERPTR checks DMA cache alignment, pins a complete frame vector, maps page-backed vectors through an sg table, or falls back to resource mapping for physically contiguous PFN vectors, then verifies the DMA mapping is contiguous enough for the requested size. DMABUF import attaches to the device, maps the attachment during prepare, verifies the mapped sg list has a sufficiently contiguous DMA span, and records `dma_addr`. Export builds or reuses a base sg table, creates a dma-buf, and gives it attach/map/vmap/mmap/release callbacks.

## State and Persistence
Buffer state is per allocation/import and persists only while vb2 or exported dma-buf references hold the refcount. `refcount` tracks kernel/VMA/dma-buf users. `vaddr` can be allocated immediately for coherent buffers, created on demand for non-coherent or imported buffers, and released on unmap/put. `dma_sgt` changes meaning by mode: internal non-coherent allocation, USERPTR mapping, or imported dma-buf mapping. USERPTR pages are marked dirty for device-to-CPU directions when released.

## Dependencies and Integration Points
This backend depends on the DMA mapping API, dma-buf framework, scatterlist helpers, frame-vector helpers from `videobuf2-memops.c`, common VMA ops, `vb2_queue` DMA direction/attributes/cache flags, and device DMA parameters. Drivers select this backend when hardware consumes one contiguous DMA address, often after raising max segment size with `vb2_dma_contig_set_max_seg_size()` for IOMMU-backed sharing.

## Risks and Edge Cases
The backend rejects unaligned USERPTR buffers based on DMA cache alignment because partial cache lines are unsafe. Imported USERPTR/DMABUF memory must map as one contiguous DMA span; otherwise `-EFAULT` is returned even if the physical pages exist. Coherent allocations with `DMA_ATTR_NO_KERNEL_MAPPING` cannot provide a kernel `vaddr`. Non-coherent memory requires correct `prepare`/`finish` cache maintenance unless vb2 cache hints skip it. Export attach code copies `sgt_base`, so stale or missing base sg tables break dma-buf export. Detach paths warn if callers detach still-mapped buffers.

## Test Signals
Exercise MMAP allocation/mmap, non-coherent cache sync, `EXPBUF`, DMABUF import with contiguous and fragmented mappings, USERPTR alignment failures, and IOMMU max-segment sizing. Runtime checks should confirm stable DMA addresses, successful vmap only when supported, dirtying of capture USERPTR pages, no leaked device references, and clean unmap/detach ordering under streamoff and process exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/videobuf2/videobuf2-dma-contig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/videobuf2/videobuf2-dma-sg.c -->
# sources/distributed-fs/ceph-client/drivers/media/common/videobuf2/videobuf2-dma-sg.c

## Purpose
`videobuf2-dma-sg.c` implements the scatter/gather DMA memory backend for vb2. It allocates page-backed buffers, maps them as scatterlists for DMA, supports USERPTR and DMABUF import, allows dma-buf export, and provides optional kernel virtual mappings through `vm_map_ram()` or dma-buf vmap.

## Important APIs, Types, and Functions
The exported table is `vb2_dma_sg_memops`. `struct vb2_dma_sg_buf` stores device, kernel vaddr, pages, frame vector, offset, DMA direction, internal sg table, active DMA sg table, size, page count, refcount/VMA handler, dma-buf attachment, and owning `vb2_buffer`. Key functions are `vb2_dma_sg_alloc_compacted()`, `vb2_dma_sg_alloc()`, `vb2_dma_sg_put()`, `vb2_dma_sg_prepare()`, `vb2_dma_sg_finish()`, `vb2_dma_sg_get_userptr()`, `vb2_dma_sg_put_userptr()`, `vb2_dma_sg_vaddr()`, `vb2_dma_sg_mmap()`, `vb2_dma_sg_get_dmabuf()`, `vb2_dma_sg_attach_dmabuf()`, `vb2_dma_sg_map_dmabuf()`, and the dma-buf ops for attach/map/cpu access/vmap/mmap/release.

## Control Flow
MMAP allocation allocates a page pointer array, attempts compacted high-order page allocation with fallback to lower orders, creates an sg table from pages, maps it with `dma_map_sgtable(..., DMA_ATTR_SKIP_CPU_SYNC)`, and initializes VMA refcount state. `prepare` and `finish` perform explicit DMA sync unless vb2 skip flags are set. USERPTR pins a frame vector, requires page-backed memory, creates an sg table with the user offset, maps it for DMA, and later unmaps/dirties pages on release. MMAP maps pages into userspace with `vm_map_pages()`. `vaddr` maps internal pages with `vm_map_ram()` or imported dma-bufs with `dma_buf_vmap_unlocked()`. Export copies the active sg table for each attachment and maps/unmaps it per importer direction. Import attaches to the dma-buf and defers mapping until `map_dmabuf`.

## State and Persistence
State is volatile per buffer. Internal allocations keep `dma_sgt` pointing at `sg_table`; imported dma-bufs set `dma_sgt` only while pinned/mapped. `refcount` tracks MMAP and exported dma-buf references. `vaddr` is cached after first kernel mapping and unmapped on release/unmap. USERPTR page arrays are borrowed from the frame vector and released by `vb2_destroy_framevec()`.

## Dependencies and Integration Points
The backend integrates with page allocator, scatterlist and DMA mapping APIs, vmalloc mapping helpers, dma-buf, common vb2 VMA operations, and frame-vector helpers. It is appropriate for devices capable of scatter/gather DMA or IOMMU mappings that do not require one contiguous DMA address.

## Risks and Edge Cases
High-order allocation fallback reduces failure risk but can still fail under memory pressure after partial allocations. Unlike dma-contig, this backend does not enforce contiguous DMA mappings; drivers that need contiguity must not use it. USERPTR requires page-backed frame vectors and returns allocation-style errors for pin/map failures. Cache synchronization is explicit; wrong skip flags can expose stale data. Imported dma-buf `dma_sgt` being non-NULL indicates an active mapping, and detach warns/unmaps if vb2 lifecycle is violated. `vm_map_ram()` mappings must be released on all put paths.

## Test Signals
Test MMAP allocation under fragmentation, USERPTR import with aligned and offset addresses, DMABUF import/export, repeated vaddr requests, poll/streamoff while mapped, and cache sync on capture/output queues. Useful signals include no leaked pages after refcount drop, proper dirtying for capture USERPTR pages, sg table map/unmap balance, and successful dma-buf CPU access sync callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/videobuf2/videobuf2-dma-sg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/videobuf2/videobuf2-dvb.c -->
# sources/distributed-fs/ceph-client/drivers/media/common/videobuf2/videobuf2-dvb.c

## Purpose
`videobuf2-dvb.c` is helper glue for simple DVB devices that DMA complete transport streams into vb2 buffers and rely on the software demux. It registers DVB adapters/frontends/demux/net devices and uses the vb2 thread-I/O helper to feed completed buffers into `dvb_dmx_swfilter()`.

## Important APIs, Types, and Functions
Exports include `vb2_dvb_register_bus()`, `vb2_dvb_unregister_bus()`, `vb2_dvb_get_frontend()`, `vb2_dvb_find_frontend()`, `vb2_dvb_alloc_frontend()`, and `vb2_dvb_dealloc_frontends()`. Important internal functions are `dvb_fnc()`, `vb2_dvb_start_feed()`, `vb2_dvb_stop_feed()`, `vb2_dvb_register_adapter()`, and `vb2_dvb_register_frontend()`. The code operates on `struct vb2_dvb`, `struct vb2_dvb_frontend`, and `struct vb2_dvb_frontends`.

## Control Flow
Frontend allocation creates list entries and initializes the per-DVB lock. Bus registration requires frontend id 1, registers the adapter, then registers each frontend. Frontend registration calls `dvb_register_frontend()`, initializes a software demux with TS, section, and memory filtering capabilities, registers the demux device, adds hardware and memory frontends, connects the hardware frontend, and registers DVB network support. When a demux feed starts, `nfeeds` is incremented and the vb2 thread starts on the first feed. The thread callback sends each buffer's payload to the software demux. Feed stop decrements `nfeeds` and stops the vb2 thread when the last feed is gone. Unregister/dealloc tears down net, frontend links, dmxdev, demux, frontend registration, frontend attachment, and list nodes.

## State and Persistence
The helper keeps transient adapter/frontend list state plus per-DVB feed counts and vb2 thread state. Nothing is persistent beyond driver binding. `nfeeds` controls when the vb2 thread is active. Frontend list membership and adapter registration determine the lifetime of associated demux and net devices.

## Dependencies and Integration Points
It depends on DVB core APIs (`dvb_register_adapter`, `dvb_register_frontend`, `dvb_dmx_init`, `dvb_dmxdev_init`, `dvb_net_init`), media-controller graph creation when configured, and vb2 core thread I/O. It is used by DVB capture drivers that provide an initialized vb2 queue and frontend structures but want common software-demux plumbing.

## Risks and Edge Cases
Registration has many staged failure paths; each must unwind only resources already initialized. `vb2_dvb_unregister_bus()` first deallocates frontends and then unregisters the adapter, so callers must not use frontend pointers afterward. Feed start requires a connected demux frontend or returns `-EINVAL`. `nfeeds` is protected by `dvb->lock`; imbalance would leave the thread running or stop it too early. Media graph creation failure inside the frontend loop unwinds the whole bus.

## Test Signals
Probe a simple DVB device with one and multiple frontends, start and stop several demux feeds, and confirm the vb2 thread starts once and stops after the final feed. Runtime signals include TS packets reaching `dvb_dmx_swfilter()`, correct `/dev/dvb/adapter*/demux*` and DVR nodes from dmxdev, successful DVB net setup when enabled, clean unregister under active feeds, and no leaked frontend list entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/videobuf2/videobuf2-dvb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/videobuf2/videobuf2-memops.c -->
# sources/distributed-fs/ceph-client/drivers/media/common/videobuf2/videobuf2-memops.c

## Purpose
`videobuf2-memops.c` provides shared low-level memory helpers used by vb2 allocators. It creates and destroys frame vectors for USERPTR memory and provides common VMA operations that keep vb2 buffer refcounts balanced while buffers are mmap'ed.

## Important APIs, Types, and Functions
Exports are `vb2_create_framevec()`, `vb2_destroy_framevec()`, and `vb2_common_vm_ops`. The common VMA ops call `vb2_common_vm_open()` and `vb2_common_vm_close()` with a `struct vb2_vmarea_handler` stored in `vma->vm_private_data`.

## Control Flow
`vb2_create_framevec()` computes the page frame range covering a userspace address and length, allocates a frame vector, calls `get_vaddr_frames()`, requires a complete pin of all frames, and unwinds partial pins on failure. `vb2_destroy_framevec()` releases frames and destroys the vector. `vb2_common_vm_open()` increments the allocator-provided refcount when a VMA is duplicated or opened, while `vb2_common_vm_close()` calls the allocator-provided `put()` callback to drop the mapping reference.

## State and Persistence
Frame-vector state is temporary and owned by whichever allocator imported USERPTR memory. VMA state persists for the lifetime of userspace mappings and is represented by allocator-specific refcounts. There is no persistent storage.

## Dependencies and Integration Points
The file depends on mm frame-vector APIs, `get_vaddr_frames()`, `put_vaddr_frames()`, and the `vb2_vmarea_handler` contract shared with dma-contig, dma-sg, and vmalloc backends. Allocators install `vb2_common_vm_ops` after mapping their buffers into userspace.

## Risks and Edge Cases
Partial frame-vector acquisition is rejected with `-EFAULT` and must release any frames already pinned. USERPTR callers must pass the correct write flag so get-user-pages permissions and dirty tracking match DMA direction. The VMA close path trusts `vm_private_data` and the handler's refcount/put pointers; allocator mmap code must initialize them before calling `open()`. Refcount imbalance can keep orphaned buffers alive or free buffers while still mapped.

## Test Signals
USERPTR import tests should cover complete and partial/inaccessible ranges, write versus read mappings, and process exit while buffers are queued. MMAP tests should show refcount increments on mapping duplication and decrements on munmap/exit. KASAN/refcount warnings around `vb2_common_vm_close()` are high-value failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/videobuf2/videobuf2-memops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/videobuf2/videobuf2-v4l2.c -->
# sources/distributed-fs/ceph-client/drivers/media/common/videobuf2/videobuf2-v4l2.c

## Purpose
`videobuf2-v4l2.c` adapts the generic vb2 core to V4L2 userspace APIs. It validates and translates `struct v4l2_buffer`, sets V4L2 buffer flags/capabilities, handles media requests, exposes standard ioctl and file-operation helpers, and initializes `vb2_queue` instances for V4L2 drivers.

## Important APIs, Types, and Functions
Exports include `vb2_querybuf()`, `vb2_reqbufs()`, `vb2_create_bufs()`, `vb2_prepare_buf()`, `vb2_qbuf()`, `vb2_dqbuf()`, `vb2_streamon()`, `vb2_streamoff()`, `vb2_expbuf()`, `vb2_queue_init_name()`, `vb2_queue_init()`, `vb2_queue_release()`, `vb2_queue_change_type()`, `vb2_poll()`, standard `vb2_ioctl_*` helpers, standard `vb2_fop_*` helpers, `vb2_video_unregister_device()`, `vb2_request_validate()`, and `vb2_request_queue()`. Internal helpers include `__verify_planes_array()`, `__verify_length()`, `vb2_fill_vb2_v4l2_buffer()`, `set_buffer_cache_hints()`, `vb2_queue_or_prepare_buf()`, `__fill_v4l2_buffer()`, `__fill_vb2_buffer()`, and `vb2_find_buffer()`.

## Control Flow
Queue initialization checks V4L2 timestamp flags, sets `v4l2_buf_ops`, derives multiplanar/output/copy-timestamp flags from queue type, and calls the core initializer. `REQBUFS` and `CREATE_BUFS` validate memory/type, sanitize flags, populate capability bits, derive requested plane sizes from V4L2 formats, and delegate to core allocation. `PREPARE_BUF` and `QBUF` validate queue ownership, buffer index, type, memory, plane arrays, output lengths, cache hints, request FD semantics, and then call core prepare/qbuf. `DQBUF` delegates to the core, marks last capture-buffer state for `V4L2_BUF_FLAG_LAST`, and clears `DONE` before returning to userspace. Fill/copy functions translate vb2 plane state to/from single-planar and multiplanar V4L2 layouts, including timestamp, timecode, request FD, mapped/queued/done/error/prepared flags, and output-only flags. Ioctl and file-operation helpers add video-device ownership and locking around the core.

## State and Persistence
This layer stores V4L2-specific per-buffer metadata in `struct vb2_v4l2_buffer`: flags, field, timecode, sequence, request FD, held-buffer state, and plane copy data. Queue state includes timestamp policy, cache hint support, owner, file I/O ownership, request support, and last-buffer-dequeued tracking. State is volatile and tied to queue/device/file lifetimes.

## Dependencies and Integration Points
The file integrates with V4L2 core objects (`video_device`, `v4l2_fh`, events, ioctl ops, file ops), media requests, V4L2 buffer/format ABI definitions, and vb2 core. Drivers can either call the exported helpers directly from their ioctl implementations or install the standard `vb2_ioctl_*` and `vb2_fop_*` helpers.

## Risks and Edge Cases
Plane array length and output `bytesused`/`data_offset` validation protect against userspace overruns. `bytesused == 0` for output is deprecated but still optionally supported with `allow_zero_bytesused`. Request API use is mutually exclusive with direct QBUF and requires driver `buf_request_complete`; output request queues also need `buf_out_validate`. Cache hint flags are only honored for allowed MMAP queues. File I/O and streaming ioctls are mutually exclusive. Queue ownership helpers reject operations from other file handles once buffers are allocated or file I/O starts. `vb2_video_unregister_device()` takes a device reference so it can release queues after unregister without premature device free.

## Test Signals
Run `v4l2-compliance` across single-planar/multiplanar, capture/output, MMAP/USERPTR/DMABUF, request API, read/write, poll, expbuf, and remove-bufs cases. Useful runtime signals include correct capability bits, sanitized unknown flags, correct `EFAULT`/`EINVAL` for bad plane arrays and lengths, `EBUSY` for queue ownership conflicts, event polling through `EPOLLPRI`, and clean queue release on file close or video-device unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/videobuf2/videobuf2-v4l2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/videobuf2/videobuf2-vmalloc.c -->
# sources/distributed-fs/ceph-client/drivers/media/common/videobuf2/videobuf2-vmalloc.c

## Purpose
`videobuf2-vmalloc.c` implements the CPU-addressable vmalloc memory backend for vb2. It is useful for devices or software paths that do not need a hardware DMA-contiguous allocation, and it supports MMAP, USERPTR, DMABUF import, and dma-buf export when DMA support is enabled.

## Important APIs, Types, and Functions
The exported table is `vb2_vmalloc_memops`. `struct vb2_vmalloc_buf` stores vaddr, frame vector, DMA direction, size, refcount/VMA handler, and imported dma-buf pointer. Key functions include `vb2_vmalloc_alloc()`, `vb2_vmalloc_put()`, `vb2_vmalloc_get_userptr()`, `vb2_vmalloc_put_userptr()`, `vb2_vmalloc_vaddr()`, `vb2_vmalloc_mmap()`, `vb2_vmalloc_get_dmabuf()`, `vb2_vmalloc_attach_dmabuf()`, `vb2_vmalloc_map_dmabuf()`, `vb2_vmalloc_unmap_dmabuf()`, and dma-buf attach/map/vmap/mmap/release callbacks.

## Control Flow
MMAP allocation creates a `vmalloc_user()` buffer, initializes refcount/VMA handler state, and returns it to vb2. MMAP uses `remap_vmalloc_range()` and common VMA ops to track mappings. USERPTR creates a frame vector, maps page-backed vectors with `vm_map_ram()`, or ioremaps physically contiguous PFN vectors when page structs are unavailable, then stores a CPU pointer adjusted by page offset. USERPTR release unmaps RAM or I/O mapping, dirties pages for capture/bidirectional directions, destroys the frame vector, and frees state. Export builds an sg table from `vmalloc_to_page()` pages for each dma-buf attachment and maps it for importers. Import simply keeps the dma-buf pointer, vmap's it on `map_dmabuf`, and vunmap's it on unmap/detach.

## State and Persistence
The backend keeps per-buffer virtual address state and refcounts while mappings or exported dma-bufs exist. Imported dma-bufs use `vaddr == NULL` until mapped. USERPTR frame-vector state persists until vb2 releases the user pointer. No state is persistent across queue lifetime.

## Dependencies and Integration Points
It depends on vmalloc APIs, mm frame-vector helpers from `videobuf2-memops.c`, common VMA ops, dma-buf when available, and V4L2/vb2 memory contracts. DVB mmap support selects this backend through Kconfig because demux/DVR mmap buffers are CPU-filled rather than hardware DMA-contiguous.

## Risks and Edge Cases
This backend provides CPU virtual access but not a hardware-specific DMA address cookie, so it is unsuitable for drivers that need direct DMA addresses unless they only use dma-buf scatter mappings. USERPTR PFN vectors must be physically contiguous for ioremap fallback. `buf->vaddr += offset` stores an adjusted pointer, so release masks back to the page boundary before unmapping page-backed mappings. Export requires every vmalloc page to resolve through `vmalloc_to_page()`. Imported dma-buf vmap failures become `-EFAULT`.

## Test Signals
Test MMAP read/write paths, USERPTR with page-backed and PFN-backed ranges, DMABUF import/export, repeated mmap/munmap, and DVB mmap consumers. Signals include stable CPU vaddr access, correct dirtying on capture release, successful sg-table construction for exported vmalloc buffers, no VMA refcount leaks, and clean detach when imported dma-bufs are still mapped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/videobuf2/videobuf2-vmalloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-core/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-core/Kconfig

## Purpose
This Kconfig file defines optional DVB core features: experimental memory-mapped DVB demux/DVR APIs, DVB network support, adapter count limits, dynamic minor allocation, and debug logging for demux section loss and ULE packet handling.

## Important APIs, Types, and Functions
The important configuration symbols are `DVB_MMAP`, `DVB_NET`, `DVB_MAX_ADAPTERS`, `DVB_DYNAMIC_MINORS`, `DVB_DEMUX_SECTION_LOSS_LOG`, and `DVB_ULE_DEBUG`. The file uses Kconfig primitives `config`, `bool`, `int`, `depends on`, `default`, `range`, `select`, and help text.

## Control Flow
When `DVB_CORE` is enabled, these options become available. `DVB_MMAP` additionally requires a compatible built-in or module relationship with `VIDEO_DEV` and selects `VIDEOBUF2_VMALLOC`. `DVB_NET` defaults to enabled when `NET` and `INET` are available. `DVB_MAX_ADAPTERS` bounds the number of adapter slots. The selected symbols drive conditional object inclusion in `drivers/media/dvb-core/Makefile` and conditional code in `dmxdev.c`.

## State and Persistence
Selections persist in the kernel `.config`. Runtime state is not stored here, but choices affect available device APIs, number of adapter minors, and debug verbosity compiled into the DVB subsystem.

## Dependencies and Integration Points
`DVB_MMAP` ties DVB demux/DVR mmap ioctls to vb2 vmalloc support and the video device core. `DVB_NET` controls inclusion of DVB network code. Debug options are consumed by DVB demux/net C files through preprocessor conditionals. `DVB_MAX_ADAPTERS` and `DVB_DYNAMIC_MINORS` influence DVB device registration behavior in core code.

## Risks and Edge Cases
`DVB_MMAP` is explicitly experimental and changes userspace-visible ioctl/mmap behavior. Its dependency on `VIDEO_DEV=y || VIDEO_DEV=DVB_CORE` prevents invalid module/built-in combinations for vb2/video helpers. Increasing `DVB_MAX_ADAPTERS` increases memory footprint. Debug logging options can be very verbose and should not be enabled casually on production systems.

## Test Signals
Build configurations should cover `DVB_CORE` with and without `DVB_MMAP`, `DVB_NET`, and debug symbols. Runtime checks include presence or absence of `DMX_REQBUFS`/mmap behavior, DVB net device availability, correct adapter numbering limits, and no Kconfig unmet-dependency warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-core/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-core/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-core/Makefile

## Purpose
This Makefile composes the `dvb-core` object from core DVB subsystem sources and optional DVB network and mmap support objects.

## Important APIs, Types, and Functions
The key Kbuild variables are `dvb-net-$(CONFIG_DVB_NET)`, `dvb-vb2-$(CONFIG_DVB_MMAP)`, `dvb-core-objs`, and `obj-$(CONFIG_DVB_CORE)`. Core objects include `dvbdev.o`, `dmxdev.o`, `dvb_demux.o`, `dvb_ca_en50221.o`, `dvb_frontend.o`, and `dvb_ringbuffer.o`, with `dvb_net.o` and `dvb_vb2.o` added conditionally.

## Control Flow
Kbuild evaluates `CONFIG_DVB_NET` and `CONFIG_DVB_MMAP` to populate optional object lists, then links all selected objects into `dvb-core.o` when `CONFIG_DVB_CORE` is enabled. If `DVB_CORE` is modular, this composition becomes the DVB core module.

## State and Persistence
There is no runtime state. The persistent effect is build artifact composition based on `.config` selections.

## Dependencies and Integration Points
The file is coupled to symbols defined in `drivers/media/dvb-core/Kconfig` and source files in the same directory. `dmxdev.o` is always part of DVB core, while mmap support is separated into `dvb_vb2.o` and only built when `CONFIG_DVB_MMAP` is selected.

## Risks and Edge Cases
A mismatch between Kconfig symbols and object names would either omit intended functionality or break builds. Because optional objects are folded into `dvb-core-objs`, dependency mistakes can affect built-in versus module linking. Removing `dvb_ringbuffer.o` or `dmxdev.o` would break the demux/DVR file operations.

## Test Signals
Run targeted builds with `CONFIG_DVB_CORE=y/m`, `CONFIG_DVB_NET=y/n`, and `CONFIG_DVB_MMAP=y/n`. Expected artifacts are `dvb-core.o` or `dvb-core.ko` containing optional symbols only when selected, with no unresolved references to `dvb_vb2_*` when mmap is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-core/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-core/dmxdev.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-core/dmxdev.c

## Purpose
`dmxdev.c` implements the DVB demux and DVR character devices. It exposes demux filter ioctls/read/poll/mmap operations, DVR read/write/buffer ioctls, ringbuffer delivery, optional vb2 mmap delivery, and registration/release of `/dev/dvb/.../demux*` and `dvr*` devices around an underlying `struct dmx_demux`.

## Important APIs, Types, and Functions
Exports are `dvb_dmxdev_init()` and `dvb_dmxdev_release()`. File operations are `dvb_demux_fops` and `dvb_dvr_fops`. Important helpers include `dvb_dmxdev_buffer_write()`, `dvb_dmxdev_buffer_read()`, `dvb_dvr_open()`, `dvb_dvr_release()`, `dvb_dvr_read()`, `dvb_dvr_write()`, `dvb_dvr_set_buffer_size()`, `dvb_dmxdev_set_buffer_size()`, `dvb_dmxdev_section_callback()`, `dvb_dmxdev_ts_callback()`, `dvb_dmxdev_feed_start()`, `dvb_dmxdev_feed_stop()`, `dvb_dmxdev_filter_start()`, `dvb_dmxdev_filter_stop()`, `dvb_dmxdev_filter_set()`, `dvb_dmxdev_pes_filter_set()`, `dvb_dmxdev_add_pid()`, `dvb_dmxdev_remove_pid()`, `dvb_demux_do_ioctl()`, and `dvb_dvr_do_ioctl()`. Key state lives in `struct dmxdev`, `struct dmxdev_filter`, `struct dmxdev_feed`, `struct dvb_ringbuffer`, and optional `struct dvb_vb2_ctx`.

## Control Flow
Initialization opens the demux, allocates the filter array, initializes locks and free filter states, registers demux and DVR DVB devices, and initializes the DVR ringbuffer. Opening a demux device reserves a free filter, initializes its mutex, ringbuffer, vb2 context, timer, type, and state. Filter ioctls set section or PES parameters, optionally allocate PID feed list entries, and start filtering immediately if requested. Section start either reuses an active same-PID section feed or allocates a new one, installs filter values/masks/modes, starts filtering, and arms timeout. PES start allocates TS feeds for each PID and starts them. Callbacks copy section/TS data into either ringbuffers or vb2 buffers, record overflow/error status, update oneshot state, and wake readers. Reads drain ringbuffers, with section reads first reconstructing the 3-byte section header to know payload length. Stop/release tears down filtering, timers, feeds, PID lists, vb2 streaming, ringbuffer memory, and state.

## State and Persistence
State is runtime-only. `dmxdev->filter[]` tracks allocation and filter state (`FREE`, `ALLOCATED`, `SET`, `GO`, `DONE`, `TIMEDOUT`), filter type, section/PES parameters, PID feed lists, timers, and ringbuffer/vb2 contexts. `dmxdev->dvr_buffer` stores DVR ringbuffer data and errors. `dmxdev->may_do_mmap` gates mmap for compatible opens when `CONFIG_DVB_MMAP` is enabled. Device `users` counts and `exit` coordinate release with open file handles. Ringbuffers are vmalloc-backed and can be resized before active streaming/filtering.

## Dependencies and Integration Points
The file integrates with DVB core registration (`dvb_register_device`, `dvb_unregister_device`), demux feed APIs (`allocate_section_feed`, `allocate_ts_feed`, `start_filtering`, `stop_filtering`, `release_*_feed`, `write`, `get_stc`, `get_pes_pids`), `dvb_ringbuffer`, `dvb_usercopy`, waitqueues/poll, timers, and optional `dvb_vb2` mmap helpers. DVR write mode switches the demux frontend to `DMX_MEMORY_FE` and restores the original frontend on release.

## Risks and Edge Cases
Buffer overflow sets ringbuffer error and wakes readers; subsequent reads flush and return the error. Filter buffer size cannot change while the filter is running, but DVR buffer resize is protected by the device mutex/spinlock. Section feed sharing for same PID requires careful stop/restart so one filter does not kill another. The demux open comment notes a known locking limitation for vb2 blocking waits because only one mutex is passed to the vb2 context. DVR open access-mode logic differs for read, write, and duplex devices; unsupported RDWR mmap paths return `-EOPNOTSUPP` when mmap is disabled. Release waits for users to drain before unregistering; missed wakeups would hang teardown.

## Test Signals
Exercise demux `DMX_SET_FILTER`, `DMX_SET_PES_FILTER`, `DMX_START`, `DMX_STOP`, `DMX_ADD_PID`, `DMX_REMOVE_PID`, buffer resize, poll/read timeout, DVR read/write, frontend switching for memory feeds, and optional `DMX_REQBUFS`/`QBUF`/`DQBUF`/mmap paths. Runtime signals include correct error returns for invalid state, no ringbuffer overrun without `-EOVERFLOW`, timeout delivery as `-ETIMEDOUT`, clean release with active filters, correct wakeups on data/error/exit, and no leaked TS or section feeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-core/dmxdev.c -->
