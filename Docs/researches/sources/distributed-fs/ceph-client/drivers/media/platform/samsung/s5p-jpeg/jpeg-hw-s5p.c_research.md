# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/jpeg-hw-s5p.c

Purpose: MMIO helper backend for original S5P JPEG hardware. It handles reset, power, raw input/output mode, encode/decode mode, subsampling, restart interval, quant/Huffman selectors, dimensions, decode interrupts, timer/stream status, DMA addresses, color conversion coefficients, start, completion status, interrupt clear, and compressed-size readback.

Important APIs: `s5p_jpeg_reset()`, `s5p_jpeg_poweron()`, `s5p_jpeg_input_raw_mode()`, `s5p_jpeg_proc_mode()`, `s5p_jpeg_subsampling_mode()`, `s5p_jpeg_dri()`, `s5p_jpeg_qtbl()`, `s5p_jpeg_htbl_ac/dc()`, `s5p_jpeg_x/y()`, interrupt enable/status helpers, `s5p_jpeg_jpgadr()`, `s5p_jpeg_imgadr()`, `s5p_jpeg_coef()`, `s5p_jpeg_start()`, and `s5p_jpeg_compressed_size()`.

Control flow: `s5p_jpeg_device_run()` calls these helpers to configure legacy S5P encode/decode jobs. The legacy IRQ handler checks stream-bound, timer, result, and stream status through these helpers, clears relevant status, sets capture payload for encode, updates subsampling, clears the interrupt, and finishes the mem2mem job.

State and persistence: no software-owned state; all effects are volatile register writes/reads.

Dependencies and integration: includes shared core definitions, `jpeg-regs.h`, and `jpeg-hw-s5p.h`. It supports a narrower raw format set than newer helpers: RGB565 and YUV422 input for encode, YUV422/YUV420 output for decode.

Risks: `s5p_jpeg_reset()` busy-waits indefinitely until reset clears, unlike Exynos3250's bounded loops. Status clearing sequences depend on documented read/write side effects. Compressed size is assembled from three byte registers and must match hardware counter semantics.

Test signals: legacy S5P encode/decode, reset behavior, timeout and stream-bound error handling, interrupt clear sequencing, compressed payload size, RGB565/YUV422 input mode, and decode YUV420/YUV422 output mode.
