# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_error.c

## Purpose
This file handles asynchronous AIE2 firmware error events. It allocates DMA-visible event buffers, registers them with firmware, decodes AIE event payloads into AMD XDNA error categories, stores the latest error, and exposes it to userspace.

## Important APIs, Types, And Functions
`struct async_events` owns an ordered workqueue, a DMA buffer, and one `struct async_event` per AIE column. `struct aie_error` and `struct aie_err_info` describe firmware error payloads. `aie_get_error_category()` maps module/row/event IDs through lookup tables. Public functions are `aie2_error_async_events_alloc()`, `aie2_error_async_events_free()`, and `aie2_get_array_async_error()`.

## Control Flow
Allocation creates the event container, allocates one large message buffer sized as `ASYNC_BUF_SIZE * total_col`, creates an ordered workqueue, initializes per-column event structures, and registers each buffer with firmware. Firmware callbacks read status/type from BAR data, use a write memory barrier so status is observed last, and queue worker processing. The worker validates error counts, logs payloads, builds an error-column bitmap, updates `ndev->last_async_err`, and re-registers the event buffer for future firmware notifications.

## State, Dependencies, Integration, Risks, And Tests
Persistent state is `ndev->async_events` and `ndev->last_async_err`. Dependencies include message buffer allocation/free from `aie2_message.c`, mailbox async registration, DMA cache flushing, DRM logging, workqueues, `dev_lock`, and userspace copy helpers. Risks include firmware-provided count overflow, assuming fewer than 32 columns for bitmaps, races during free versus queued work, noncoherent DMA cache handling, and unknown event IDs reducing diagnostic quality. Test signals are synthetic async event injection, oversized `err_cnt` validation, module/row mapping checks, free during active events, userspace query of last error, and repeated event re-registration.
