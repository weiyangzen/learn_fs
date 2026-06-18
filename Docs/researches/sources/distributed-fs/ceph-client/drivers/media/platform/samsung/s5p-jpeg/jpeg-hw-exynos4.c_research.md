# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/jpeg-hw-exynos4.c

Purpose: MMIO helper backend for Exynos4x12-style JPEG hardware and Exynos5433-compatible differences. It controls reset, encode/decode mode, image and encoded output formats, interrupts, Huffman-table enable, stream/frame buffer addresses, image size, table selection, decode table component selection, stream size, bitstream size, and decoded frame format.

Important APIs: `exynos4_jpeg_sw_reset()`, `exynos4_jpeg_set_enc_dec_mode()`, `__exynos4_jpeg_set_img_fmt()`, `__exynos4_jpeg_set_enc_out_fmt()`, `exynos4_jpeg_set_interrupt()`, `exynos4_jpeg_set_huf_table_enable()`, `exynos4_jpeg_set_sys_int_enable()`, address/size setters, `exynos4_jpeg_set_encode_tbl_select()`, decode Q/H table selectors, `exynos4_jpeg_get_stream_size()`, and `exynos4_jpeg_get_frame_fmt()`.

Control flow: `exynos4_jpeg_device_run()` uses these helpers to reset and program encode or decode jobs. Exynos5433 decode additionally parses JPEG Huffman/quantization markers in the core and uses selector helpers before enabling tables. The IRQ path disables system interrupts, reads status, maps it to result codes, completes buffers, disables mode, and reads decoded subsampling for Exynos4.

State and persistence: no software-owned state; writes volatile registers. Some register fields differ by version, handled by version parameters in internal format helpers.

Dependencies and integration: includes shared JPEG core, Exynos4 helper header, and `jpeg-regs.h`. Maps many V4L2 raw formats to Exynos4/Exynos5433 register encodings and chroma swap bits.

Risks: unsupported formats fall through without error in helper switches, depending on the core to filter. Version-specific masks and swap bits must be kept correct for Exynos4 vs Exynos5433. Table selection programming is tightly coupled to header parsing and default table setup.

Test signals: Exynos4 and Exynos5433 encode/decode, all supported YUV/RGB/GREY formats, decoded subsampling readback, JPEGs with custom DHT/DQT tables on Exynos5433, interrupt status error mapping, and bitstream size/payload reporting.
