# sources/distributed-fs/ceph-client/drivers/misc/bcm-vk/bcm_vk_msg.c

## Purpose
`bcm_vk_msg.c` implements the Broadcom Valkyrie misc-device message transport between host user space and the VK card firmware. It synchronizes BAR-advertised message queues, allocates per-open contexts, rewrites user transport IDs into driver-owned message IDs, enqueues host-to-card messages, dequeues card-to-host responses, handles shutdown messages, drains outstanding work on reset or close, and runs heartbeat monitoring.

## Important APIs, Types, and Functions
The public entry points are `bcm_vk_msg_init()`, `bcm_vk_msg_remove()`, `bcm_vk_sync_msgq()`, `bcm_vk_msgq_irqhandler()`, `bcm_vk_open()`, `bcm_vk_read()`, `bcm_vk_write()`, `bcm_vk_poll()`, `bcm_vk_release()`, `bcm_to_h_msg_dequeue()`, `bcm_vk_send_shutdown_msg()`, `bcm_vk_hb_init()`, `bcm_vk_hb_deinit()`, and `bcm_vk_drv_access_ok()`. Queue helpers include `msgq_avail_space()`, `msgq_occupied()`, `msgq_blk_addr()`, `bcm_to_v_msg_enqueue()`, `bcm_to_v_q_doorbell()`, and pending-list helpers. DMA transfer messages use `bcm_vk_sg_alloc()` and `bcm_vk_sg_free()` through each `bcm_vk_wkent`.

## Control Flow
Initialization sets context locks, hash buckets, message-ID bitmap state, and queue locks, then tries to read queue metadata from BAR1. Open allocates a `bcm_vk_ctx` tied to the caller's TGID. Write validates block alignment, copies user message blocks, assigns an internal message ID, optionally converts transfer-buffer user pointers into DMA SGLs, appends in-band SGL data if there is queue space, adds the entry to the host-to-card pending list, writes blocks into the BAR queue, advances `wr_idx`, and rings the doorbell. The IRQ handler schedules work; `bcm_to_h_msg_dequeue()` drains card queues, matches responses by queue and internal message ID, and moves complete entries to the read queue for the owning context. Read returns only responses for the file's context and restores the user's original message ID before copying to user space. Release waits briefly for outstanding DMA, drains both pending queues, frees the context, and sends a last-session shutdown message when appropriate.

## State and Persistence
State is volatile driver memory plus BAR queue indices. Persistent per-device state includes context slots, PID hash lists, pending queues per message channel, a message-ID bitmap, heartbeat counters, and `msgq_inited`. Per-open state tracks PID, queue number, pending response count, pending DMA count, and wait queue. No data persists across driver removal, reset drain, or close.

## Dependencies and Integration Points
The file depends on `bcm_vk.h` for BAR accessors, reset/access state, workqueues, alerts, and device fields; `bcm_vk_msg.h` for message layouts; `bcm_vk_sg.h` for DMA SGL conversion; and Linux misc, poll, list, bitmap, waitqueue, spinlock, mutex, interrupt, timer, and user-copy APIs. It integrates with firmware through BAR0 doorbells, BAR1 queue descriptors, queue memory, and host alert bits.

## Risks and Edge Cases
Queue index corruption is treated as fatal and blocks driver access, but queue sizes are assumed power-of-two because masking is used. `bcm_to_v_msg_enqueue()` returns success after `idx_err`, so callers may not see a low-level enqueue failure after access is blocked. DMA close handling waits at most two seconds and then frees SGL resources even if firmware might still touch buffers. `bcm_vk_write()` trusts message layout enough to locate `_vk_data` from `size` and plane count after only limited bounds checks. PID translation assumes the PID is packed in `arg` with a fixed mask. Heartbeat detection intentionally uses relaxed timing but may block access on repeated unchanged uptime reads.

## Test Signals
Useful tests include open/write/read/poll round trips with multiple contexts and queues, message-ID wrap and overflow, short read buffer `-EMSGSIZE`, DMA upload/download with multiple planes, queue-full retry returning `-EAGAIN`, reset drain while responses are pending, last-session shutdown emission, invalid BAR queue metadata, heartbeat loss alerting, and close while DMA is outstanding.
