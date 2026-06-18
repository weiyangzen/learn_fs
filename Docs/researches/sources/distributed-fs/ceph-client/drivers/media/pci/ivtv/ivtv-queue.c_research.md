# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-queue.c

## Purpose
This file implements ivtv stream buffer queue management and stream buffer allocation/freeing. It provides byte-counted list queues used by file I/O, DMA preparation, IRQ completion, and stream teardown.

## Important APIs, Types, and Functions
Public functions are `ivtv_buf_copy_from_user`, `ivtv_buf_swap`, `ivtv_queue_init`, `ivtv_enqueue`, `ivtv_dequeue`, `ivtv_queue_move`, `ivtv_flush_queues`, `ivtv_stream_alloc`, and `ivtv_stream_free`. The internal `ivtv_queue_move_buf` performs locked list/accounting transitions.

## Control Flow
Buffers start in `q_free`. Writers fill buffers from userspace, capture DMA moves free buffers into `q_predma`, active DMA moves them to `q_dma`, and completion moves them to `q_full` or back to `q_free`. `ivtv_queue_move` can move a byte target or all buffers and can steal complete transfer groups from another queue when free buffers are exhausted. Allocation creates host SG arrays, a hardware SG element, DMA mappings, and per-stream data buffers.

## State and Persistence Behavior
The file mutates queue list membership and counters (`buffers`, `length`, `bytesused`), buffer fields (`bytesused`, `readpos`, flags, DMA handles, transfer counters), and stream SG pointers/handles. `ivtv_stream_free` unmaps DMA and frees all allocated buffers and SG arrays.

## Dependencies and Integration Points
It depends on Linux list/spinlock APIs, DMA mapping/sync APIs through header helpers, userspace copy helpers, and `struct ivtv_stream` queue fields. It is a core dependency for fileops, IRQ, stream lifecycle, VBI, and decode/encode DMA.

## Risks
Queue counters must stay synchronized with list operations under `qlock`. Stealing buffers from full queues can drop application data; the transfer-counter grouping avoids partial-frame drops but depends on correct `dma_xfer_cnt`. DMA mappings must be unmapped exactly once and SG handles must respect `IVTV_DMA_UNMAPPED`.

## Test Signals
Stress read/write under backpressure, queue stealing during slow readers, stream allocation failure unwinding, DMA and PIO streams, repeated open/close, buffer byteswap for MPEG/VBI, and leak checks for DMA mappings and allocated buffers.
