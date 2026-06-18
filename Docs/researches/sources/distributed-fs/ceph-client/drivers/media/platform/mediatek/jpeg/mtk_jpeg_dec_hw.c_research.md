# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/mtk_jpeg_dec_hw.c

## Purpose
This file implements the MediaTek JPEG decoder hardware helper layer and the per-hardware-block platform driver for MT8195 JPEG decode engines. It converts parsed JPEG frame parameters into hardware register programming, handles decoder interrupts/timeouts, returns V4L2 mem2mem buffers, and registers child decode engines with the master JPEG core.

## Important APIs, Types, and Functions
The exported decoder programming APIs are `mtk_jpeg_dec_fill_param()`, `mtk_jpeg_dec_get_int_status()`, `mtk_jpeg_dec_enum_result()`, `mtk_jpeg_dec_set_config()`, `mtk_jpeg_dec_reset()`, and `mtk_jpeg_dec_start()`. Internal helpers classify JPEG sampling patterns, calculate MCU counts, DMA grouping, component strides and payload sizes, and write decoder registers for bitstream addresses, destination banks, component IDs, sampling factors, quantization table IDs, and 34-bit address extensions. Platform-driver entry points are `mtk_jpegdec_hw_probe()` and `mtk_jpegdec_hw_irq_handler()`.

## Control Flow
The parser or core fills `struct mtk_jpeg_dec_param`, then `mtk_jpeg_dec_fill_param()` derives output fourcc, MCU layout, DMA group sizing, strides, and component byte sizes. For a job, the core supplies bitstream and framebuffer DMA addresses to `mtk_jpeg_dec_set_config()`, which programs the decoder in a fixed order before `mtk_jpeg_dec_start()` triggers hardware. The IRQ handler cancels timeout work, copies source metadata to the destination, reads and clears interrupt status, resets on underflow/overflow/bitstream errors, sets destination plane payloads from computed component sizes, returns buffers, drops runtime PM and the decode clock, marks the hardware idle, and wakes the master scheduler.

## State and Persistence
Hardware state is volatile MMIO register state. Software state is held in the child `struct mtk_jpegdec_comp_dev`, including `hw_param`, `hw_state`, register base, clocks, IRQ, and delayed timeout work. Destination completion order is persisted only in the V4L2 context done queue through frame numbers and `last_done_frame_num`; it is not durable across device reset or stream teardown.

## Dependencies and Integration Points
The file depends on V4L2 mem2mem/videobuf2 buffer lifetimes, `mtk_jpeg_core.h` context and child-device structures, register offsets from `mtk_jpeg_dec_reg.h`, runtime PM, clock bulk APIs, platform IRQ/MMIO helpers, and OF compatible `mediatek,mt8195-jpgdec-hw`. It integrates with the master JPEG device through `master_dev->dec_hw_dev`, `reg_decbase`, `hw_index`, `hw_rdy`, and `hw_wq`.

## Risks and Edge Cases
Sampling recognition is strict; unsupported sampling combinations produce `dst_fourcc = 0` and fail parameter fill. Address and size alignment failures only log through `mtk_jpeg_verify_align()`; callers do not get a hard failure during register programming. Several register fields subtract one from calculated counts, so zero MCU, group, or unit counts would underflow if invalid dimensions reached this layer. `mtk_jpegdec_put_buf()` maintains ordered destination completion under a spinlock, so frame-number initialization and wrap behavior matter. Timeout and IRQ paths both manipulate PM, clocks, source buffers, and destination completion, making delayed-work cancellation and hardware state transitions important race signals.

## Test Signals
Useful tests include decode jobs for grayscale, 4:2:0, 4:2:2, vertical 4:2:2, 4:4:4, and MTK 34-bit DMA variants; invalid sampling tables; unaligned bitstream/output DMA addresses; underflow/overflow/error IRQ injection; timeout recovery; multi-hardware scheduling; and V4L2 plane payload checks against `comp_size[]`.
