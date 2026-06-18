# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/jpeg-hw-exynos4.h

Purpose: public declarations for Exynos4/Exynos5433 JPEG MMIO helpers.

Important APIs: declares reset, mode setting, image format and encoded output format setters, table setup/selection helpers, interrupt/status helpers, stream/frame address and size setters, Huffman enable, system interrupt enable, stream-size readback, decode bitstream size, and decoded frame format readback.

Control flow role: used by `jpeg-core.c` for variants whose m2m ops are `exynos4_jpeg_m2m_ops`.

State and persistence: no runtime state in the header; all helpers operate on a register base supplied by the caller.

Dependencies and integration: relies on shared JPEG core types/enums such as `struct s5p_jpeg_addr` and `enum exynos4_jpeg_img_quality_level` through include order.

Risks: because declarations are low-level and unguarded, core code must ensure clocks are enabled, spinlocks held, and formats validated before calling.

Test signals: compile/prototype checks and full encode/decode paths on Exynos4-compatible variant data.
