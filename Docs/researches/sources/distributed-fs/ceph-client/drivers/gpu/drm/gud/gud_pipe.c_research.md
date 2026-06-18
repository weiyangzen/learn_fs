
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gud/gud_pipe.c

## Purpose
`gud_pipe.c` implements the GUD primary plane and CRTC update path. It validates atomic state with the USB gadget, converts framebuffer damage rectangles into the gadget's selected transfer format, optionally compresses with LZ4, sends rectangle metadata over USB control transfers, transfers pixel data over USB bulk, and supports optional asynchronous damage coalescing.

## Important APIs, Types, And Functions
The module parameter `async_flush` enables queued flushing through `system_long_wq`. Public internal functions are `gud_clear_damage()`, `gud_flush_work()`, `gud_plane_atomic_check()`, `gud_crtc_atomic_enable()`, `gud_crtc_atomic_disable()`, and `gud_plane_atomic_update()`.

Important helpers include `gud_xrgb8888_to_r124()`, `gud_xrgb8888_to_color()`, `gud_prep_flush()`, `gud_usb_bulk_timeout()`, `gud_usb_bulk()`, `gud_flush_rect()`, `gud_flush_damage()`, `gud_fb_queue_damage()`, and `gud_fb_handle_damage()`. `struct gud_usb_bulk_context` holds the timer and USB scatter-gather request for one bulk transfer.

## Control Flow
Atomic check first validates plane scaling/visibility, marks mode changes for rotation or format changes, requires exactly one connector for visible state changes, resolves the active connector state, builds a `gud_state_req` containing display mode, transfer format, connector index, connector properties, and plane properties, then sends `GUD_REQ_SET_STATE_CHECK` to the gadget. CRTC enable sends controller enable, state commit, and display enable requests. Disable turns display and controller off.

Atomic update clears pending async damage and shadow buffers when the CRTC is disabled or mode-changed, enters the DRM device, begins CPU access to the framebuffer, iterates damage clips, and handles each damage rectangle. Full-update devices expand damage to the entire framebuffer. If async flushing is enabled, damage is copied to a shadow buffer, coalesced under `damage_lock`, and queued; otherwise flushing is synchronous.

Flush preparation chooses the actual transfer format, aligns sub-byte formats to byte boundaries, converts XRGB8888 to monochrome/gray/RGB332/RGB565/RGB888/XRGB1111 when needed, handles big-endian byte swapping, copies or directly references framebuffer data, fills `gud_set_buffer_req`, and tries LZ4 compression. If compression fails, it retries uncompressed. Large damage rectangles are split by the maximum bulk buffer length. Each rectangle may send `GUD_REQ_SET_BUFFER`, then performs a USB scatter-gather bulk transfer with a 3 second timeout.

## State And Persistence
State persists in `struct gud_device`: compression mode, bulk buffers and scatterlist, LZ4 memory, stats counters, `prev_flush_failed`, pending async `fb`, accumulated `damage`, and `shadow_buf`. `prev_flush_failed` causes the next full-update flush to resend buffer metadata. Transfer statistics accumulate uncompressed and actual byte counts for debugfs.

## Dependencies And Integration Points
The file depends on DRM atomic helpers, damage helpers, GEM framebuffer CPU access, format conversion helpers, LZ4, USB scatter-gather APIs, workqueues, GUD protocol requests, connector property serialization from `gud_connector_fill_properties()`, and USB control helpers from `gud_drv.c`.

## Risks
The file explicitly notes likely breakage on big-endian systems. If `bulk_len` is smaller than one line's pitch, the split calculation can produce zero lines, so descriptor/buffer sizing must prevent that. Async flushing trades latency for copied shadow memory and can coalesce damage beyond the original dirty rectangles. Imported buffers are treated as slow/uncached reads. USB bulk timeout cancellation and disconnect races rely on `drm_dev_enter()` and error filtering. Full-update plus compression is rejected at probe because this path cannot combine those semantics safely.

## Test Signals
Tests should exercise every supported and emulated pixel format, sub-byte rectangle alignment, LZ4 success and fallback, damage splitting at `bulk_len`, async and synchronous flushing, disconnect during active transfer, full-update devices, rotation state checks, connector property changes causing state checks, bulk timeout behavior, and debugfs compression/error counters.
