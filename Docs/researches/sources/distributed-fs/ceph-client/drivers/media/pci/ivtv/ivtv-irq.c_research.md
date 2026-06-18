# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-irq.c

## Purpose
This file handles ivtv hardware interrupts, DMA/PIO scheduling, completion processing, VBI/YUV/PCM deferred work, and DMA timeout recovery. It converts firmware mailbox interrupt data into buffer queue movement and stream wakeups.

## Important APIs, Types, and Functions
Public entry points are `ivtv_irq_handler`, `ivtv_irq_work_handler`, `ivtv_dma_stream_dec_prepare`, and `ivtv_unfinished_dma`. Key internals include `stream_enc_dma_append`, `dma_post`, encoder/decoder DMA start helpers, IRQ-specific handlers for DMA read/write completion/errors, encoder start capture, VBI capture/reinsert, decoder data requests, and vsync processing.

## Control Flow
The top-half IRQ handler reads and masks interrupt status, clears handled bits, dispatches DMA, capture, decoder, EOS, and vsync events, then round-robins pending DMA or PIO streams when the engine is idle. DMA preparation builds `sg_pending`, moves buffers through `q_predma`/`q_dma`, starts the hardware transfer, and arms a timeout. Completion handlers sync DMA memory, retry failed segments up to a small limit, post buffers to `q_full` or `q_free`, wake stream waitqueues, and queue kthread work for PIO, VBI, YUV, or PCM handling.

## State and Persistence Behavior
The file mutates `itv->i_flags`, `cur_dma_stream`, `cur_pio_stream`, `dma_retries`, `irq_rr_idx`, `dma_data_req_size`, `dma_data_req_offset`, `last_vsync_field`, and stream scatter-gather state such as `sg_pending`, `sg_processing`, offsets, PTS, and transfer counters. It also maintains buffer queue membership and updates YUV frame scheduling state during vsync.

## Dependencies and Integration Points
It integrates with the queue layer, mailbox data extraction, UDMA, VBI conversion/output, YUV work, ALSA PCM callbacks, kthread work, timers, waitqueues, V4L2 event queues, hardware register accessors, and firmware interrupt mailbox conventions.

## Risks
The file is concurrency-sensitive: hard IRQs, timers, kthread work, DMA callbacks, and userspace waits all share flags and queue state. DMA error handling can race the hardware status register, and the code deliberately avoids clearing certain busy states. Magic-cookie offset correction, VBI piggybacking on MPEG DMA, and PIO fallback are fragile. Missed vsync detection can report `IRQ_NONE` even after doing local work.

## Test Signals
Test with sustained MPEG/YUV/VBI/PCM capture, decoder feed under backpressure, DMA timeout injection, DMA error retry behavior, PIO-only streams, ALSA and V4L2 PCM contention, VBI reinsertion, vsync event delivery, YUV register updates on field changes, and stream stop while DMA is pending.
