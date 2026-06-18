
# sources/distributed-fs/ceph-client/drivers/media/pci/tw68/tw68-video.c

## Purpose
This file implements the TW68 V4L2 capture device. It defines supported pixel formats and TV norms, programs decoder/scaler/crop registers, manages vb2 DMA-SG queues, chains RISC DMA buffers, handles video controls and ioctls, and completes buffers from video interrupts.

## Important APIs, Types, And Functions
Public functions used by the core are `tw68_set_tvnorm_hw`, `tw68_video_init1`, `tw68_video_init2`, `tw68_irq_video_done`, and `tw68_video_start_dma`. Internal functions include `format_by_fourcc`, `set_tvnorm`, `tw68_set_scale`, queue callbacks (`tw68_queue_setup`, `tw68_buf_queue`, `tw68_buf_prepare`, `tw68_buf_finish`, `tw68_start_streaming`, `tw68_stop_streaming`), control handler `tw68_s_ctrl`, format/std/input handlers, and optional advanced debug register access.

## Control Flow
Initialization first creates V4L2 controls, then `tw68_video_init2` selects PAL defaults, BGR24 720x576 interlaced format, initializes the vb2 DMA-SG queue, and registers the video device. Format ioctls validate pixel format, clamp width/height, choose field mode, and update device capture state. Buffer prepare allocates a RISC program based on field layout. Queueing appends a looping jump to each buffer and, when a previous buffer exists, patches the previous buffer's final jump to the new program and enables an interrupt on the new buffer's first instruction. Streaming starts DMA from the first active buffer. Video interrupts reset handled bits, complete the current buffer on `TW68_DMAPI`, stamp timestamp/field/sequence, and log/reset exceptional FIFO or DMA conditions.

## State And Persistence
Runtime state is held in `struct tw68_dev`: current format, width, height, field, selected norm, input, sequence number, vb2 queue, active buffer list, and IRQ mask. Per-buffer RISC state lives in `struct tw68_buf`. Hardware scaler, decoder, DMA, and control registers hold current capture configuration.

## Dependencies And Integration Points
The file integrates V4L2 ioctls/controls/events, videobuf2 DMA-SG, RISC program generation from `tw68-risc.c`, register macros from `tw68-reg.h`, and lifecycle/IRQ management in `tw68-core.c`.

## Risks
`tw68_start_streaming` assumes the active list contains a buffer, relying on `min_queued_buffers`. `tw68_stop_streaming` walks the active list without taking `slock`, while queueing/IRQ paths use it. Format changes can leave already-active buffers using the previous RISC program until drained, as noted in comments. Debug register access lacks bounds checks. Input switching while active may trigger FDMIS on some chips.

## Test Signals
Exercise all advertised formats and byte orders, norm switching while idle, input switching, mmap/userptr/read/DMABUF paths, single-field and interlaced modes, and stop/start while buffers are queued. Logs should avoid PABORT/DMAPERR and persistent FIFO overflow. Captured frame sizes and colorspace should match V4L2 format ioctls.
