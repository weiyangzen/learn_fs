# sources/distributed-fs/ceph-client/drivers/iio/industrialio-buffer.c

## Purpose
`industrialio-buffer.c` implements IIO buffered data plumbing. It owns attached buffer lists, scan-mask sysfs, buffer enable/disable transitions, scan-byte calculation, demultiplexing when per-buffer masks differ from the active device mask, legacy character-device read/write/poll operations, newer per-buffer anon-fd access, dma-buf attachment/enqueue support, and helpers for pushing samples into active buffers.

## Important APIs, types, and functions
- `struct iio_dmabuf_priv` tracks an attached dma-buf, mapped sg table, direction, IIO DMA block, fence context, refcount, and list membership.
- `struct iio_dma_fence` wraps `struct dma_fence` with an IIO dma-buf private pointer and deferred cleanup work.
- `iio_buffer_read()`, `iio_buffer_write()`, and `iio_buffer_poll()` implement blocking/nonblocking user I/O against an `iio_dev_buffer_pair`.
- `iio_scan_mask_set()`, `iio_scan_mask_clear()`, `iio_scan_el_store()`, and timestamp scan-element helpers implement `scan_elements/*_en`.
- `iio_compute_scan_bytes()` computes packed scan size using channel storage bits, repeat count, alignment, and optional timestamp.
- `iio_verify_update()`, `__iio_update_buffers()`, `iio_enable_buffers()`, and `iio_disable_buffers()` negotiate buffer modes, scan masks, watermark, trigger attachment, and setup callbacks.
- `iio_buffer_update_demux()` builds `struct iio_demux_table` entries when a buffer wants a subset of the active scan mask.
- `iio_buffer_attach_dmabuf()`, `_detach_dmabuf()`, `_enqueue_dmabuf()`, and `iio_buffer_signal_dmabuf_done()` implement dma-buf import and fence signaling.
- `iio_buffers_alloc_sysfs_and_mask()` creates `bufferN`, legacy `buffer`, and legacy `scan_elements` groups; it also registers the `IIO_BUFFER_GET_FD_IOCTL` handler.
- `iio_push_to_buffers()` and `iio_push_to_buffers_with_ts_unaligned()` are exported producer-side sample push helpers.
- `iio_device_attach_buffer()`, `iio_buffer_init()`, `iio_buffer_get()`, and `iio_buffer_put()` manage buffer lifetime.

## Control flow
Drivers attach one or more initialized buffers to an IIO device. During device registration, `iio_buffers_alloc_sysfs_and_mask()` derives `masklength` from channel scan indexes, validates scan types, allocates scan masks, creates per-buffer sysfs groups, and creates legacy groups for buffer zero. Users configure `length`, `watermark`, channel enable bits, and timestamp enable while the buffer is inactive. Stores take the IIO device `mlock` and reject changes when the buffer is active.

Enabling a buffer calls `__iio_update_buffers()`. The function verifies the combined configuration, requests a buffer update, disables any old active configuration, activates/removes list entries, and enables the new configuration. Mode selection intersects device modes with all active buffer access modes, preferring triggered mode when a trigger is present, otherwise hardware then software. The active scan mask may be a driver-provided available mask or a dynamically allocated compound mask. Enable paths run setup `preenable`, driver `update_scan_mode`, optional hardware FIFO watermark update, each buffer `enable`, trigger pollfunc attachment for triggered mode, and setup `postenable`. Error paths disable and deactivate buffers to leave direct mode.

Reads wait on the buffer poll queue until enough samples are available or a flush succeeds. Writes wait for output-buffer space. The newer `IIO_BUFFER_GET_FD_IOCTL` returns an anon inode tied to one attached buffer and sets `IIO_BUSY_BIT_POS`, causing legacy wrapper access to return `-EBUSY` while the new fd owns the buffer. Dma-buf ioctls attach, detach, and enqueue externally allocated memory; enqueue reserves a dma fence, waits for conflicting reservation-object fences, queues the transfer through buffer access ops, and signals completion asynchronously through `iio_buffer_signal_dmabuf_done()`.

## State and persistence behavior
State is runtime kernel state: attached buffer array, active buffer list, scan masks, timestamp flags, per-buffer demux tables, watermarks, lengths, dma-buf attachment lists, fence sequence numbers, busy bits, and device current mode. There is no persistent on-disk state. Active scan masks allocated dynamically are freed on disable; driver-provided available masks are not. Buffer reference counts protect attached buffers and active list membership. Unregister paths set `indio_dev->info` elsewhere and wake poll queues so blocked readers and writers exit.

## Dependencies and integration points
The file integrates with IIO core opaque state, IIO trigger attach/detach, channel scan types, setup ops, buffer implementation callbacks, sysfs group registration, anon inodes, `poll`, wait queues, dma-buf, dma-resv, dma-fence, scatter-gather mappings, and exported IIO producer APIs. Buffer access implementations supply operations such as `read`, `write`, `store_to`, `set_length`, `request_update`, `attach_dmabuf`, and `enqueue_dmabuf`.

## Risks
- The available scan-mask terminator logic intentionally uses only the first `unsigned long`; comments warn multi-long masks are not fully handled and can hide valid masks.
- Error recovery after failed enable/disable is best effort. `__iio_update_buffers()` deactivates all buffers after low-level failures because hardware state may be uncertain.
- Dma-buf paths involve reservation locks, attachment references, queued fences, and deferred cleanup. Incorrect buffer access implementations can deadlock or leak attachments.
- `iio_buffer_attach_dmabuf()` unlocks the reservation object before duplicate attachment detection and uses custom cleanup for that case; this is subtle lifetime code.
- Legacy and anon-fd access are mutually excluded with busy bits, but tests must cover both device-level and buffer-level busy states.
- Demux code assumes timestamp placement and scan-index ordering; bad channel metadata can produce wrong sample layouts.

## Test signals
- Build with dma-buf enabled and exercise both `CONFIG_DEBUG_FS`-independent buffer paths and compile-time namespace imports.
- Sysfs tests should cover scan type validation, duplicate or invalid scan masks, changing length/watermark/channel bits while active, and legacy group aliases for buffer zero.
- Runtime tests should enable single and multiple buffers in software/triggered modes, hardware single-buffer mode rejection for extra buffers, and trigger attach/detach ordering.
- I/O tests should check blocking read wakeups, nonblocking `-EAGAIN`, hardware FIFO flush behavior, output buffer write/poll, unregister wakeups, and `-ENODEV` after removal.
- Dma-buf tests should cover attach/detach/enqueue, duplicate attach rejection, cyclic only on output buffers, invalid sizes/flags, reservation-object contention, fence error signaling, and close cleanup.
