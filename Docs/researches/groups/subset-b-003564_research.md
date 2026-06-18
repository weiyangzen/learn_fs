# subset-b-003564 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_fb_dma_helper.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_fb_dma_helper.c

### Purpose
`drm_fb_dma_helper.c` provides small KMS helpers for framebuffers backed by DMA GEM objects. It lets drivers derive DMA scanout addresses, synchronize non-coherent memory over damaged regions, and expose the active DMA-backed primary-plane buffer to DRM panic handling.

### Important APIs, Types, And Functions
The exported APIs are `drm_fb_dma_get_gem_obj()`, `drm_fb_dma_get_gem_addr()`, `drm_fb_dma_sync_non_coherent()`, and `drm_fb_dma_get_scanout_buffer()`. They operate on `struct drm_framebuffer`, `struct drm_plane_state`, `struct drm_gem_dma_object`, `struct drm_atomic_helper_damage_iter`, `struct drm_rect`, and `struct drm_scanout_buffer`.

### Control Flow
`drm_fb_dma_get_gem_obj()` fetches a framebuffer plane's GEM object through `drm_gem_fb_get_obj()` and casts it to DMA GEM. `drm_fb_dma_get_gem_addr()` starts at `obj->dma_addr + fb->offsets[plane]`, applies chroma subsampling for nonzero planes, rounds the source coordinate down to the containing format block, and adds pitch and block-size offsets. `drm_fb_dma_sync_non_coherent()` walks every format plane, skips coherent DMA objects, iterates damage clips, and calls `dma_sync_single_for_device()` for full affected scanlines. `drm_fb_dma_get_scanout_buffer()` validates that the current primary-plane framebuffer is linear, local, and already CPU-mapped before filling a panic scanout descriptor.

### State, Persistence, And Dependencies
The file keeps no persistent state. It reads immutable framebuffer metadata, current plane state, DMA GEM object addresses, and damage clips. It depends on GEM framebuffer helpers, DMA GEM helpers, DRM format block metadata, atomic damage iteration, DMA mapping sync, iosys maps, and DRM panic scanout types.

### Integration Points
DMA-backed KMS drivers call these helpers from plane update, CRTC, or panic paths. `drm_fb_dma_sync_non_coherent()` is intended for `.atomic_update` implementations that use damage clips with non-coherent DMA memory. `drm_fb_dma_get_scanout_buffer()` is a generic implementation for drivers that pre-vmap primary-plane buffers.

### Risks
The address calculation assumes framebuffer pitches, offsets, source coordinates, chroma subsampling, and block dimensions are already validated by KMS. Damage sync intentionally ignores clip x coordinates and syncs whole lines, which is conservative but can be expensive. `drm_fb_dma_get_scanout_buffer()` dereferences the plane's current state and DMA object and therefore only supports simple local linear CPU-visible buffers.

### Test Signals
Useful tests cover single-plane RGB and multi-plane YUV address derivation, block/tiled-like format block widths, nonzero source offsets, damage clips on non-coherent DMA objects, imported GEM rejection in panic scanout, non-linear modifier rejection, and unavailable `vaddr` handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_fb_dma_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_fb_helper.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_fb_helper.c

### Purpose
`drm_fb_helper.c` implements the DRM fbdev emulation core. It bridges Linux fbdev operations to DRM client modesets, manages `fb_info` lifecycle, tracks dirty rectangles, handles suspend/resume and hotplug reprobe, and translates fbdev colormap, panning, blanking, and screeninfo requests into DRM behavior.

### Important APIs, Types, And Functions
Major exported entry points include `drm_fb_helper_prepare()`, `drm_fb_helper_init()`, `drm_fb_helper_initial_config()`, `drm_fb_helper_hotplug_event()`, `drm_fb_helper_fini()`, `drm_fb_helper_fill_info()`, `drm_fb_helper_blank()`, `drm_fb_helper_check_var()`, `drm_fb_helper_set_par()`, `drm_fb_helper_pan_display()`, `drm_fb_helper_setcmap()`, `drm_fb_helper_ioctl()`, `drm_fb_helper_damage_range()`, `drm_fb_helper_damage_area()`, `drm_fb_helper_deferred_io()`, suspend helpers, and `drm_fb_helper_gem_is_fb()`. Core state lives in `struct drm_fb_helper`, `struct drm_client_dev`, `struct fb_info`, `struct drm_mode_set`, `struct drm_clip_rect`, `struct fb_cmap`, and `struct drm_fb_helper_surface_size`.

### Control Flow
Initialization starts with `drm_fb_helper_prepare()`, which initializes locks, work items, damage state, callbacks, and preferred bpp. `drm_fb_helper_initial_config()` probes DRM client modesets, allocates `fb_info`, asks the driver `fbdev_probe` callback to allocate backing storage, attaches the framebuffer to modesets, fills fbdev metadata, registers the framebuffer, and records deferred setup if no CRTC sizing is available. Hotplug events either finish deferred setup or reprobe connectors and commit fbdev modes. fbdev write paths accumulate damage and schedule `damage_work`, which waits for vblank, snapshots the accumulated clip, calls the driver's `fb_dirty` hook, and restores damage on failure.

### State, Persistence, And Dependencies
Persistent in-kernel state includes `dev->fb_helper`, `fb_helper->info`, `fb_helper->fb`, `fb_helper->buffer`, modeset lists in the DRM client, work items, `damage_clip`, `deferred_setup`, `delayed_hotplug`, and `fbdefio`. Module parameters control fbdev emulation, over-allocation, and optional physical smem address leakage. The file depends on fbdev core, DRM client modeset helpers, atomic and legacy modeset paths, CRTC gamma APIs, DRM format metadata, DRM master arbitration, console locking, and workqueue execution.

### Integration Points
Memory-manager-specific helpers such as DMA, SHMEM, and TTM call into this file to fill `fb_info`, route deferred I/O damage, and use standard fb_ops callbacks. DRM drivers expose `drm_driver.fbdev_probe`, mode_config callbacks, primary-plane format lists, and CRTC/connector state. fbcon and legacy fbdev users interact through `fb_ops`, while KMS compositors interact indirectly when fbdev restore occurs after master release.

### Risks
The main risks are locking and lifecycle ordering: `register_framebuffer()` requires dropping helper locks, hotplug can arrive before initial config, and suspend/resume must coordinate console lock and damage work. Dirty handling intentionally avoids scheduling during oops paths. Colormap support must choose between pseudo-palette, legacy gamma, and atomic gamma LUT paths without leaking blobs or mishandling `-EDEADLK`. The helper rejects pixel-format changes, so fbdev users that expect mutable fb_var fields must be handled through compatibility workarounds only.

### Test Signals
High-value tests include initial config with no connectors then hotplug, fbdev over-allocation clamping, damage aggregation from writes and deferred mmap pages, suspend/resume with pending damage, `FBIO_WAITFORVSYNC`, panning on atomic and legacy devices, colormap updates for truecolor and indexed visuals, SDL-style zeroed pixel fields, big and small bpp formats including C1/C2/C4, and forced restore on KD_TEXT transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_fb_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_fbdev_dma.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_fbdev_dma.c

### Purpose
`drm_fbdev_dma.c` implements fbdev emulation for drivers whose dumb buffers are backed by DMA GEM memory. It creates a dumb client framebuffer, maps it for fbdev access, and chooses between direct fbdev access or a shadow system-memory buffer when framebuffer dirty callbacks require deferred flushing.

### Important APIs, Types, And Functions
The exported entry point is `drm_fbdev_dma_driver_fbdev_probe()`. It defines two `fb_ops` tables: `drm_fbdev_dma_fb_ops` for direct DMA memory and `drm_fbdev_dma_shadowed_fb_ops` for a deferred shadow buffer. Important helpers include open/release/module refcount handling, GEM mmap, destroy callbacks, `drm_fbdev_dma_damage_blit_real()`, `drm_fbdev_dma_damage_blit()`, `drm_fbdev_dma_helper_fb_dirty()`, and probe-tail setup functions.

### Control Flow
Probe computes a legacy fb format, allocates a dumb `drm_client_buffer`, vmaps it, rejects I/O memory mappings, stores `fb_helper->buffer` and `fb_helper->fb`, and fills generic fbdev info. If the framebuffer has a dirty callback, it allocates a vmalloc shadow buffer and enables deferred I/O; otherwise it points `info->screen_buffer` directly at the DMA mapping and exposes smem metadata when permitted. Dirty handling copies only the damaged clip from the shadow buffer into the client buffer, then calls the framebuffer `dirty` callback.

### State, Persistence, And Dependencies
Persistent state is held by `fb_helper->buffer`, `fb_helper->fb`, `fb_helper->info`, optional `fbdefio`, and optional vmalloc shadow storage. Direct mode stores the client buffer vmap in `info->screen_buffer`; shadow mode stores a separate `vzalloc()` buffer. Dependencies include fbdev DMA memory ops, DRM client buffer allocation and vmap, DMA GEM object fields such as `map_noncoherent`, GEM PRIME mmap, DRM fb helper damage callbacks, and iosys map copying.

### Integration Points
DMA memory-manager drivers can use this as their `drm_driver.fbdev_probe` callback. The fb_ops integrate with fbcon, userspace fbdev opens, mmap, drawing operations, and deferred I/O. The dirty callback path integrates with manual-update display drivers by blitting shadow damage into the actual DRM framebuffer and then invoking `fb->funcs->dirty`.

### Risks
Direct mode assumes the vmap is normal CPU memory, not I/O memory. Shadow mode must keep clip byte math correct for sub-byte fbdev formats and bytes-per-pixel formats. Destroy paths must clean deferred I/O, finish fb helper state, unmap/delete the client buffer, free the shadow buffer if used, and release the DRM client in the right order. Non-coherent DMA buffers rely on flags and later synchronization by the driver.

### Test Signals
Tests should cover direct and shadowed probe paths, failure after buffer allocation or vmap, dirty clips for 1/2/4 bpp and normal packed formats, fb_mmap through GEM PRIME, non-coherent map flags, destroy after partial setup, and driver dirty callback failures preserving error returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_fbdev_dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_fbdev_shmem.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_fbdev_shmem.c

### Purpose
`drm_fbdev_shmem.c` implements fbdev emulation for GEM SHMEM backed DRM devices. It exposes the SHMEM dumb buffer through fbdev deferred I/O so mmap and fbdev drawing operations can dirty pages and later flush them through DRM framebuffer dirty callbacks.

### Important APIs, Types, And Functions
The exported entry point is `drm_fbdev_shmem_driver_fbdev_probe()`. The file defines SHMEM-specific fb_ops, open/release module refcount helpers, deferred sysmem ops via `FB_GEN_DEFAULT_DEFERRED_SYSMEM_OPS`, `drm_fbdev_shmem_fb_mmap()`, `drm_fbdev_shmem_fb_destroy()`, `drm_fbdev_shmem_get_page()`, and `drm_fbdev_shmem_helper_fb_dirty()`.

### Control Flow
Probe allocates a dumb DRM client buffer, casts its GEM object to SHMEM, vmaps the client buffer, rejects I/O memory mappings, installs helper callbacks, fills fbdev metadata, and points `info->screen_buffer` at the SHMEM vmap. It configures deferred I/O with `drm_fbdev_shmem_get_page()` and `drm_fb_helper_deferred_io()`, then initializes fb deferred I/O. Dirty handling calls the framebuffer `dirty` callback for nonempty clips if one exists. mmap adjusts page protection to write-combine for write-combined SHMEM mappings and delegates to `fb_deferred_io_mmap()`.

### State, Persistence, And Dependencies
Persistent state includes `fb_helper->buffer`, `fb_helper->fb`, `fb_helper->info`, the SHMEM object's page array protected by the active vmap, and `fb_helper->fbdefio`. The file depends on GEM SHMEM helper internals, DRM GEM framebuffer helpers, DRM client buffer APIs, fbdev deferred I/O, page refcounting, and DRM fb helper damage conversion.

### Integration Points
SHMEM GEM drivers use this as `drm_driver.fbdev_probe`. It integrates with fbdev userspace mmap through deferred I/O, with fbcon drawing through generated deferred sysmem ops, and with DRM manual-update paths through the framebuffer dirty callback.

### Risks
`drm_fbdev_shmem_get_page()` assumes the SHMEM `pages` array is populated and stable while the client buffer is vmapped. mmap protection must match `map_wc` or userspace can observe wrong cache behavior. Cleanup must run deferred I/O cleanup before unmapping and deleting the DRM client buffer. The dirty helper ignores empty clips and silently succeeds when no dirty callback exists, which is appropriate for always-scanout memory but important for manual-update devices.

### Test Signals
Useful tests cover write-combine and cached SHMEM mappings, deferred mmap page dirtying, `get_page()` bounds behavior, dirty callbacks for page-derived clips and direct fbdev drawing clips, vmap failure unwinding, and destroy after successful deferred I/O initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_fbdev_shmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_fbdev_ttm.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_fbdev_ttm.c

### Purpose
`drm_fbdev_ttm.c` implements fbdev emulation for TTM-backed DRM devices. It keeps a vmalloc shadow buffer for fbdev access and copies damaged regions into the real TTM client buffer through temporary local mappings.

### Important APIs, Types, And Functions
The exported entry point is `drm_fbdev_ttm_driver_fbdev_probe()`. The file defines fb_ops for TTM fbdev, module open/release helpers, deferred sysmem operations, `drm_fbdev_ttm_fb_destroy()`, `drm_fbdev_ttm_damage_blit_real()`, `drm_fbdev_ttm_damage_blit()`, and `drm_fbdev_ttm_helper_fb_dirty()`.

### Control Flow
Probe creates a dumb client buffer, stores it in `fb_helper`, allocates a vmalloc shadow buffer sized to the GEM object, fills fbdev metadata, installs deferred I/O, and returns with fbdev writes targeting the shadow. Damage work locks `fb_helper->lock`, locally vmaps the client buffer, copies the affected clip from shadow to the mapped TTM buffer, unmaps it, and then calls the framebuffer dirty callback if present.

### State, Persistence, And Dependencies
State is held in `fb_helper->buffer`, `fb_helper->fb`, `info->screen_buffer`, and `fb_helper->fbdefio`. The file depends on DRM client buffer allocation, local vmap/vunmap helpers, fbdev deferred sysmem ops, `iosys_map` copying, DRM fb helper damage callbacks, and TTM-style buffer movement constraints mediated by the client buffer reservation path.

### Integration Points
TTM drivers can use this as their `fbdev_probe` callback. It integrates with fbcon through generated deferred sysmem ops and with manual-update DRM framebuffers through optional dirty callbacks. The local vmap path accommodates TTM buffers that may move and therefore should only be pinned/mapped while copying damage.

### Risks
The lock comment is significant: fbdev modeset operations and damage blits must be serialized so buffer movement does not race with copying. Clip math must handle sub-byte formats correctly. Destroy must cleanup deferred I/O, finalize the helper, free the shadow buffer, delete the client buffer, and release the client. Probe failure after shadow allocation must clear helper pointers before deleting the buffer.

### Test Signals
Tests should exercise probe failure unwinding, dirty copies for 1/2/4 bpp and byte-aligned formats, local vmap failures, framebuffer dirty callback failures, deferred I/O flush behavior, and teardown with pending or completed fbdev registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_fbdev_ttm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_file.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_file.c

### Purpose
`drm_file.c` implements DRM character-device file lifecycle and common file operations. It allocates per-open `drm_file` contexts, wires driver open/postclose callbacks, manages event delivery to userspace, releases per-file DRM resources, prints fdinfo memory stats, and provides a test-only internal file constructor.

### Important APIs, Types, And Functions
Key exported APIs are `drm_open()`, `drm_release()`, `drm_release_noglobal()`, `drm_read()`, `drm_poll()`, `drm_file_alloc()`, `drm_file_free()`, `drm_file_update_pid()`, `drm_event_reserve_init()`, `drm_event_reserve_init_locked()`, `drm_event_cancel_free()`, `drm_send_event()`, `drm_send_event_locked()`, `drm_send_event_timestamp_locked()`, `drm_show_fdinfo()`, `drm_show_memory_stats()`, `drm_print_memory_stats()`, and `drm_file_err()`. Important state includes `struct drm_file`, event lists, GEM handle tables, PRIME file private data, syncobj state, DRM master state, and client identity fields.

### Control Flow
Open acquires a DRM minor, optionally takes `drm_global_mutex` for legacy load/unload drivers, increments open count, shares the device address space, allocates a `drm_file`, initializes GEM/syncobj/PRIME/debugfs/client state, runs driver open, initializes master state for primary clients, and links the file into `dev->filelist`. Release unlinks the file, frees events and mode objects, releases GEM/syncobj/PRIME/master resources, calls driver postclose, drops open count, and restores in-kernel clients on last close. `drm_read()` serializes event reads, waits like a pipe, copies only whole events, and puts events back if the userspace buffer is too small or copy fails.

### State, Persistence, And Dependencies
Per-file state persists from open to release: framebuffer ownership list, event space quota, pending and delivered events, waitqueue, locks, client id/name, pid, PRIME data, GEM handles, syncobjs, and master data. The file depends on DRM minor/device lifetime, debugfs clients, GEM and syncobj subsystems, DMA fences, poll/read waitqueues, PCI fdinfo, RCU pid handling, and optional legacy global locking.

### Integration Points
Drivers normally use these functions in their `file_operations` table. KMS page flips, vblank waits, and driver-private asynchronous completions reserve and send events through this file. `/proc/<pid>/fdinfo` uses `drm_show_fdinfo()` and optional driver `show_fdinfo` hooks. Tests and in-kernel clients can use `mock_drm_getfile()` to construct an anonymous DRM file around a minor.

### Risks
Event accounting is subtle: reservation subtracts from `event_space`, close must unlink pending events without racing senders, reads must restore accounting if an event cannot be copied, and fences/completions must be signaled exactly once. Open and release ordering must unwind driver callbacks, debugfs, GEM, syncobj, PRIME, master, and minor references correctly. `drm_file_update_pid()` must preserve master ownership semantics and use RCU safely.

### Test Signals
High-value tests include open failure unwinding after driver open failure, primary versus render-node clients, lastclose restore, event reserve/cancel/send/read with small buffers and nonblocking reads, close with pending events, fence timestamp signaling, fdinfo memory accounting for shared/private/resident/active/purgeable GEM objects, and pid update after file handoff.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_flip_work.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_flip_work.c

### Purpose
`drm_flip_work.c` provides a small queue/commit/workqueue helper for page-flip-related callbacks. It lets interrupt or atomic contexts enqueue opaque data, then later commits the queued data to a workqueue where a driver-provided callback processes it in process context.

### Important APIs, Types, And Functions
The public APIs are `drm_flip_work_init()`, `drm_flip_work_queue()`, `drm_flip_work_commit()`, and `drm_flip_work_cleanup()`. Internal `struct drm_flip_task` stores a list node and callback data pointer. `struct drm_flip_work` supplies the queued and committed lists, spinlock, worker, callback, and debug name.

### Control Flow
Initialization sets up both task lists, the spinlock, callback, name, and `INIT_WORK()`. Queue allocates a task with `GFP_KERNEL` when sleepable or `GFP_ATOMIC` otherwise, appends it to `work->queued` under the spinlock, and falls back to immediate callback execution if allocation fails. Commit splices queued tasks to the committed list under the spinlock and queues the worker. The worker repeatedly splices committed tasks to a private list, invokes the callback for each, frees tasks, and loops until no new committed tasks arrived.

### State, Persistence, And Dependencies
State persists in the caller-owned `drm_flip_work` object and heap-allocated tasks until the worker consumes them. Synchronization is a spinlock around list transfers. The file depends on Linux workqueues, list APIs, allocation helpers, `drm_can_sleep()`, and DRM logging.

### Integration Points
Drivers use this helper around vblank/page-flip completion flows where work may be collected before the hardware flip point and then run asynchronously after commit. The opaque callback data lets driver code own the payload format.

### Risks
Allocation failure executes the callback immediately in the caller's context, so callbacks must tolerate that path or drivers must ensure queuing cannot fail in unsafe contexts. Cleanup only warns if lists are nonempty; callers must flush or commit/consume work before cleanup. Correctness depends on callers choosing a live workqueue and ensuring callback data remains valid until processing.

### Test Signals
Tests should cover queuing from sleepable and atomic contexts, multiple queue batches before commit, commits racing with worker execution, allocation failure fallback, cleanup with and without pending tasks, and callback ordering across queued-to-committed splices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_flip_work.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_format_helper.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_format_helper.c

### Purpose
`drm_format_helper.c` implements generic framebuffer copy, byte-swap, and format-conversion helpers for simple display drivers. It focuses on clipped transfers from DRM framebuffers, usually XRGB8888 input, into device-native formats including RGB332, RGB565, RGB888/BGR888, 1555/5551, 8888 channel permutations, 2101010, grayscale, mono, gray2, and ARGB4444.

### Important APIs, Types, And Functions
State APIs are `drm_format_conv_state_init()`, `drm_format_conv_state_copy()`, `drm_format_conv_state_reserve()`, and `drm_format_conv_state_release()`. Copy/conversion APIs include `drm_fb_clip_offset()`, `drm_fb_memcpy()`, `drm_fb_swab()`, many `drm_fb_xrgb8888_to_*()` helpers, `drm_fb_argb8888_to_argb4444()`, `drm_fb_xrgb8888_to_mono()`, and `drm_fb_xrgb8888_to_gray2()`. Internals include `__drm_fb_xfrm()`, `__drm_fb_xfrm_toio()`, `drm_fb_xfrm()`, and vectorized line conversion helpers for 32-to-8/16/24/32 bit output.

### Control Flow
Generic transform helpers compute clipped line counts and source offsets, optionally allocate temporary storage when reading uncached or writing I/O memory, and process one line at a time. `drm_fb_memcpy()` walks all planes and copies clipped bytes with per-plane pitch handling. `drm_fb_swab()` selects 16-bit or 32-bit byte swapping based on bits per pixel. Most conversion wrappers set a destination pixel size and call `drm_fb_xfrm()` with a format-specific line function that uses inline pixel converters from `drm_format_internal.h`. Mono and gray2 conversions first copy one source line, convert XRGB8888 to BT.601 gray8, then pack one or two bits per pixel.

### State, Persistence, And Dependencies
Persistent state is optional temporary memory stored in caller-owned `struct drm_format_conv_state`; it can be reused across conversions and released explicitly. The helpers otherwise operate on caller-provided `iosys_map` arrays, framebuffer metadata, pitches, and clips. Dependencies include DRM rect helpers, DRM format metadata, iosys-map memory access, `memcpy_toio()`, endian conversion helpers, and `drm_format_internal.h` pixel conversion functions.

### Integration Points
Simple KMS drivers, fbdev emulation paths, panic paths, and manual-update drivers use these helpers when hardware scanout format differs from the framebuffer format or when copying from a shadow buffer to device memory. The helpers are deliberately generic and exported so drivers do not duplicate conversion loops.

### Risks
Several helpers are explicitly single-plane only in the transform path; multi-plane support is limited to raw `drm_fb_memcpy()`. Source I/O memory is not handled in `drm_fb_xfrm()`. Temporary allocation failures can drop conversions. Packed mono/gray2 bit ordering starts at the clip's first pixel rather than forcing byte-aligned x coordinates. Callers must supply clips and destination pitch consistent with the target hardware.

### Test Signals
Tests should cover clipped copies across pitch boundaries, destination I/O memory, uncached source hint behavior, temporary buffer reuse and release, every exported conversion with known pixel fixtures, endian byte-swap paths, mono and gray2 packing for non-multiple-of-8 or non-multiple-of-4 widths, invalid source format warnings, and multi-plane memcpy behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_format_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_format_internal.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_format_internal.h

### Purpose
`drm_format_internal.h` defines inline raw pixel conversion primitives used by DRM format helper loops. It keeps per-pixel bit manipulation separate from line-copy mechanics.

### Important APIs, Types, And Functions
The header provides static inline converters from XRGB8888 to R8 luma, RGB332, RGB565, big-endian RGB565, RGBX5551, RGBA5551, XRGB1555, ARGB1555, RGB888, BGR888, ARGB8888, XBGR8888, BGRX8888, ABGR8888, XRGB2101010, ARGB2101010, XBGR2101010, and ABGR2101010. It also provides ARGB8888 to ARGB4444 conversion. The helpers use `u32`, `BIT()`, `GENMASK()`, and `swab16()`.

### Control Flow
Each converter accepts a little-endian logical raw pixel as `u32`, masks source channels, shifts or expands bits into the target layout, and returns a `u32` wide enough for the target value. Alpha-setting variants fill alpha bits to opaque. The BT.601 helper computes grayscale luma as `(77 R + 150 G + 29 B) / 256`.

### State, Persistence, And Dependencies
The header has no state and no exported symbols. It depends only on Linux bit, type, and byte-swap helpers. Its conversion behavior is compiled into users such as `drm_format_helper.c`.

### Integration Points
Line conversion loops in `drm_format_helper.c` pass these functions as per-pixel callbacks to pack converted pixels into 8-, 16-, 24-, or 32-bit destination streams. Drivers indirectly use these helpers through exported DRM framebuffer conversion APIs.

### Risks
All conversions assume little-endian byte-order pixel interpretation at the helper boundary. Bit expansion for 2101010 formats approximates 8-bit channels into 10-bit channels by bit replication; tests should lock down expected values. The header intentionally expects 32-bit input/output and is not sufficient for output formats wider than 32 bits.

### Test Signals
Good tests use fixed XRGB8888 and ARGB8888 pixel fixtures for each converter, alpha-bit assertions for opaque variants, byte-order checks for RGB565BE, BT.601 luma known values, and 2101010 bit replication edge cases such as all-zero, all-one, and single-channel maxima.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_format_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_fourcc.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_fourcc.c

### Purpose
`drm_fourcc.c` centralizes DRM pixel-format metadata and legacy fb format translation. It maps bpp/depth or command-line color modes to FourCC formats, returns `drm_format_info` records, allows drivers to override format info for modifiers, and computes block dimensions, bits per pixel, and minimum pitch.

### Important APIs, Types, And Functions
Important exports are `drm_mode_legacy_fb_format()`, `drm_driver_legacy_fb_format()`, `drm_driver_color_mode_format()`, `drm_format_info()`, `drm_get_format_info()`, `drm_format_info_block_width()`, `drm_format_info_block_height()`, `drm_format_info_bpp()`, and `drm_format_info_min_pitch()`. Internal `__drm_format_info()` searches a static table of `struct drm_format_info` covering indexed, RGB, alpha, high-depth, YUV, packed, planar, and block-coded formats.

### Control Flow
Legacy format selection first maps bpp/depth to a canonical FourCC, then `drm_driver_legacy_fb_format()` applies device quirks for host byte order and XBGR 30 bpp preference. `drm_driver_color_mode_format()` interprets color-mode values for fbdev use. Format lookup linearly scans the static table and warns through `drm_format_info()` for unsupported formats. Block width/height helpers return explicit block dimensions or one-pixel defaults, and bpp/min-pitch derive byte and block geometry.

### State, Persistence, And Dependencies
There is no mutable state. The persistent data is the compiled static format table, whose fields include `format`, `depth`, `num_planes`, `cpp` or `char_per_block`, `block_w`, `block_h`, subsampling, alpha, indexed, and YUV flags. Dependencies include DRM device mode_config quirks and optional driver `get_format_info` callbacks.

### Integration Points
Framebuffer creation, plane validation, fbdev emulation, DMA address helpers, and format conversion helpers all rely on this metadata. Drivers can customize modifier-specific descriptions through `dev->mode_config.funcs->get_format_info()`, while core validation still uses `__drm_format_info()` to reject unknown FourCCs.

### Risks
The static table is a central contract; incorrect block sizes, plane counts, subsampling, or alpha/YUV flags can break framebuffer validation, pitch calculation, DMA addressing, and userspace-visible format behavior. Big-endian compatibility relies on driver quirks. `drm_format_info_bpp()` divides by block dimensions and assumes populated `char_per_block` for formats where bpp is meaningful.

### Test Signals
Tests should cover legacy bpp/depth mappings, device byte-order quirks, color-mode mappings, lookup for representative RGB/YUV/indexed/block formats, bpp and minimum pitch for packed and block-coded formats, unsupported format warnings, and driver-specific `get_format_info` override behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_fourcc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_framebuffer.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_framebuffer.c

### Purpose
`drm_framebuffer.c` implements DRM framebuffer object validation, ioctl handling, per-file ownership, lookup, lifetime management, removal from active scanout, dirty forwarding, and debugfs reporting. It is the core path behind ADDFB, ADDFB2, RMFB, CLOSEFB, GETFB, GETFB2, and DIRTYFB.

### Important APIs, Types, And Functions
Major functions include `drm_framebuffer_check_src_coords()`, `drm_mode_addfb()`, `drm_mode_addfb2()`, `drm_internal_framebuffer_create()`, `drm_mode_rmfb()`, `drm_mode_closefb_ioctl()`, `drm_mode_getfb()`, `drm_mode_getfb2_ioctl()`, `drm_mode_dirtyfb_ioctl()`, `drm_fb_release()`, `drm_framebuffer_init()`, `drm_framebuffer_lookup()`, `drm_framebuffer_unregister_private()`, `drm_framebuffer_cleanup()`, `drm_framebuffer_remove()`, and `drm_framebuffer_print_info()`. Important types include `struct drm_framebuffer`, `struct drm_mode_fb_cmd2`, `struct drm_format_info`, `struct drm_file`, and `struct drm_mode_rmfb_work`.

### Control Flow
ADDFB translates legacy bpp/depth to FourCC and delegates to ADDFB2. ADDFB2 validates mode-setting support, dimensions, flags, modifiers, format metadata, per-plane handles, pitches, offsets, and modifier consistency before calling the driver `fb_create` callback; the new framebuffer id is added to the calling file's framebuffer list. RMFB and file release remove framebuffers from the file list, then either drop the final reference or schedule removal from active usage. GETFB/GETFB2 return metadata and only create GEM handles for current DRM master or CAP_SYS_ADMIN callers. DIRTYFB copies clip rectangles from userspace and forwards them to `fb->funcs->dirty`.

### State, Persistence, And Dependencies
Framebuffer state persists as a mode object with a kref, idr registration, `dev->mode_config.fb_list`, per-file `fbs` ownership, GEM object pointers, handle-ref internal flags, immutable format/size/pitch/offset/modifier metadata, and allocator command name. Dependencies include DRM mode object registration, GEM handle accounting, DRM format metadata, atomic and legacy modeset APIs, user copy helpers, debugfs, and driver framebuffer callbacks.

### Integration Points
Userspace KMS APIs create and manage framebuffer ids through these ioctls. Drivers provide `mode_config.funcs->fb_create` and framebuffer funcs for destroy, dirty, and optional handle creation. Plane and CRTC state refer to framebuffer objects; removal must clear those references through atomic or legacy modeset paths. `drm_file_free()` calls `drm_fb_release()` to reap per-file framebuffers on close.

### Risks
Framebuffer lifetime is delicate because the lookup idr holds a weak reference while planes, CRTCs, file lists, and userspace handles hold strong or implied references. Removal can require modeset locks and can hit `-EDEADLK`, so atomic removal retries with a modeset acquire context and may retry by disabling CRTCs if simply clearing planes is invalid. GETFB handle disclosure is intentionally restricted for security. Validation must reject malformed unused planes when modifiers are enabled while tolerating old userspace that did not zero unused fields before modifier support.

### Test Signals
High-value tests cover ADDFB and ADDFB2 validation failures, planar formats with repeated GEM objects, modifier flag consistency, big-endian ADDFB2 restrictions, GETFB/GETFB2 privilege behavior and handle cleanup on partial failure, DIRTYFB clip copying and annotate-copy constraints, RMFB while framebuffer is active on atomic and legacy devices, file close reaping, private framebuffer unregister/cleanup, and debugfs framebuffer output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_framebuffer.c -->
