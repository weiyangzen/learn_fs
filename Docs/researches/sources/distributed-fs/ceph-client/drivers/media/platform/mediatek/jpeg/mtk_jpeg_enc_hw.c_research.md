# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/mtk_jpeg_enc_hw.c

## Purpose
This file implements MediaTek JPEG encoder hardware programming and the MT8195 JPEG encode hardware child platform driver. It writes source/destination DMA addresses, image size, stride, quality, restart interval, EXIF offset behavior, handles encoder completion/timeout, and registers encoder engines with the master JPEG device.

## Important APIs, Types, and Functions
Exported APIs are `mtk_jpeg_enc_reset()`, `mtk_jpeg_enc_get_file_size()`, `mtk_jpeg_enc_start()`, `mtk_jpeg_set_enc_src()`, `mtk_jpeg_set_enc_dst()`, and `mtk_jpeg_set_enc_params()`. `mtk_jpeg_enc_quality[]` maps user quality thresholds to hardware quality codes. Runtime platform hooks include `mtk_jpegenc_hw_probe()`, `mtk_jpegenc_hw_irq_handler()`, timeout work, IRQ setup, and ordered destination completion via `mtk_jpegenc_put_buf()`.

## Control Flow
For a job, the core sets source plane DMA addresses, destination DMA window and optional EXIF offset, encoder size/stride/block count/quality/control bits, then calls `mtk_jpeg_enc_start()`. The IRQ handler cancels timeout work, copies metadata, clears interrupt status, warns on non-DONE interrupts, calculates output byte count from DMA pointer registers, sets destination payload, returns source and destination buffers, releases runtime PM/clocks, marks the hardware idle, and wakes the master scheduler. Timeout work resets hardware and completes the source as error while still returning the destination through the ordered completion queue.

## State and Persistence
Per-engine runtime state lives in `struct mtk_jpegenc_comp_dev`: current buffers/context, delayed timeout work, register base, clocks, IRQ, and hardware state. Per-context encode controls such as quality, restart interval, output format, crop, and EXIF enable drive register state but are not persisted by this file.

## Dependencies and Integration Points
The code depends on videobuf2 DMA-contig addresses, V4L2 mem2mem buffer handling, runtime PM, MediaTek JPEG core structures, and OF compatible `mediatek,mt8195-jpgenc-hw`. It integrates with the master device through `enc_hw_dev`, `reg_encbase`, `hw_index`, `hw_rdy`, and `hw_wq`.

## Risks and Edge Cases
`mtk_jpeg_enc_get_file_size()` infers size by subtracting destination base from the current DMA pointer; 34-bit handling shifts `DMA_ADDR0` but does not combine all high bits in an obvious way. `mtk_jpeg_set_enc_dst()` writes `addr_ext + size` for the stall extension, which is suspicious if the extension register expects only high address bits. Format-dependent block count and stride logic must match supported V4L2 formats. Timeout and IRQ paths share buffer/clock/PM cleanup responsibilities, so cancellation ordering matters.

## Test Signals
Exercise NV12/NV21 and packed 4:2:2 formats, all quality thresholds, EXIF and non-EXIF output, restart intervals, 34-bit DMA addresses, output buffer near stall boundary, timeout recovery, non-DONE IRQ status, and ordered completion under multi-frame scheduling.
