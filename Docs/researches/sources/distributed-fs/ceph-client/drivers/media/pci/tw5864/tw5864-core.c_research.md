
# sources/distributed-fs/ceph-client/drivers/media/pci/tw5864/tw5864-core.c

## Purpose
This file is the PCI core for the Techwell TW5864 driver. It registers the PCI driver, maps MMIO, initializes V4L2 device state and video subdevices, handles top-level interrupts, schedules H.264 frame bottom halves, and coordinates the single hardware encoder among four inputs.

## Important APIs, Types, And Functions
Key functions are `tw5864_initdev`, `tw5864_finidev`, `tw5864_isr`, `tw5864_h264_isr`, `tw5864_timer_isr`, `tw5864_irqmask_apply`, and `tw5864_interrupts_disable`. The `video_nr` module parameter assigns V4L2 node numbers. The PCI ID table matches vendor Techwell and device `0x5864`. `tw5864_h264_isr` fills `struct tw5864_h264_frame` ring entries; `tw5864_timer_isr` scans inputs for new raw frames and starts an encode request.

## Control Flow
Probe allocates `struct tw5864_dev` with devm, registers a V4L2 device, enables PCI, sets 32-bit DMA, maps BAR0, initializes the spinlock, logs hardware revisions, calls `tw5864_video_init`, and requests a shared IRQ. The ISR reads low/high interrupt status, clears both halves, then dispatches VLC-done and timer interrupts. VLC-done records encoded frame metadata, advances the four-entry H.264 ring if space is available, queues `bh_work`, updates per-input sequence/GOP state, clears `encoder_busy`, programs the next DMA buffer addresses, and acknowledges the PCI/VLC interrupt. Timer interrupts avoid starting a new encode if the encoder is busy, otherwise round-robin over enabled inputs, compare raw frame buffer pointers, and call `tw5864_request_encoded_frame`.

## State And Persistence
Runtime state includes MMIO base, IRQ mask, global spinlock, `encoder_busy`, `next_input`, H.264 DMA ring read/write indices, and per-input sequence/deadline state. Nothing is persisted outside device registers and allocated kernel memory.

## Dependencies And Integration Points
The core depends on PCI, DMA mask setup, V4L2 device registration, `tw5864_video_init/fini`, register macros from `tw5864-reg.h`, workqueues, and bottom-half handling in `tw5864-video.c`.

## Risks
The hardware has one encoder for four channels, so bugs in `encoder_busy` or ring index handling can drop frames or stall all channels. The timer stuck-channel recovery writes `ENC_BUF_PTR_REC1` based on `buf_id + 3`, a hardware-specific workaround. The driver comments document known H.264 quality issues; GOP size 1 is the practical workaround. Interrupt clearing acknowledges all bits, so future interrupt sources need careful dispatch.

## Test Signals
Expected logs include hardware and H.264 core versions plus video node registration. Streaming tests should show round-robin service across four inputs, no repeated "all buffers busy" messages, frame sequence increments, and correct unload after `tw5864_interrupts_disable` and `tw5864_video_fini`.
