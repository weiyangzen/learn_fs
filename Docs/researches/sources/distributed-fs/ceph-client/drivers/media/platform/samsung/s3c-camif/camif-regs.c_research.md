# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s3c-camif/camif-regs.c

Purpose: MMIO programming layer for S3C CAMIF. It translates driver state into register writes for reset, source format, crop, bus polarity, output DMA addresses/sizes, scaler, target format, flip, image effects, test pattern, capture enable/disable, interrupt clearing, and register dumps.

Important APIs: exported helpers include `camif_hw_reset()`, `camif_hw_set_source_format()`, `camif_hw_set_camera_crop()`, `camif_hw_set_camera_bus()`, `camif_hw_set_output_addr()`, `camif_hw_set_output_dma()`, `camif_hw_set_target_format()`, `camif_hw_set_scaler()`, `camif_hw_enable_scaler()`, `camif_hw_enable_capture()`, `camif_hw_disable_capture()`, `camif_hw_set_lastirq()`, `camif_hw_clear_pending_irq()`, and `camif_hw_dump_regs()`.

Control flow: capture initialization calls reset and global setup, then per-path configuration programs target format, scaler, flip, output DMA sizing, and initial buffer addresses. IRQ and stop paths clear pending IRQs, clear FIFO overflow, enable last-IRQ mode, and disable capture/scaler. Capture enable increments `camif->stream_count`; capture disable decrements it and disables global `IMGCPTEN` when the last path stops.

State and persistence: this file does not own durable state. It reads `camif_dev`, `camif_vp`, `camif_frame`, and `camif_scaler` and commits their current values to volatile hardware registers. The hardware register state persists only while the device is powered and not reset.

Dependencies and integration: depends on `camif-regs.h` register macros and `camif-core.h` data structures. It uses `readl/writel`, delays for reset timing, and V4L2 color-effect/media-bus constants. Variant checks split S3C244x from S3C6410 behavior.

Risks: many fields are encoded with fixed masks and shifts; wrong alignment or unsupported format state can silently program invalid hardware. `camif_get_dma_burst()` warns but leaves burst outputs zero if width/ybpp are invalid, so upstream format validation is essential. Stream count underflow is guarded with `WARN_ON` but still indicates lifecycle imbalance.

Test signals: register trace/dump comparison against hardware manuals for both variants, capture start/stop with both paths, scaler ratio tests, crop offset tests, planar Y/Cb/Cr DMA address tests, color effect/test pattern validation, and overflow IRQ handling on S3C244x.
