# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/jpeg-regs.h

## Purpose
This header is the hardware register and bit-field contract for the Samsung JPEG codec driver. It contains no executable code; it gives the operation driver stable names for MMIO offsets, mode bits, interrupt masks, DMA address registers, image format selectors, quantization/Huffman table windows, timer fields, scaling controls, and RGB/YUV conversion coefficients across S5PC210, Exynos4x12, and Exynos3250 style JPEG blocks.

## Important APIs, Types, and Constants
The exported API is preprocessor-only. The S5P group defines legacy registers such as `S5P_JPGMOD`, `S5P_JPGINTSE`, `S5P_JPGINTST`, `S5P_JPGCOM`, raw/JPEG address registers, quantizer and Huffman table address macros, and compression/decompression mode bits. The Exynos4 group defines linear codec control, interrupt, image plane, table selection, image format, decoded size, and table-entry registers. The Exynos3250 group adds split luma/chroma plane base/stride/offset registers, source/output tiled and endian controls, decode scaling, stream-bound fields, DMA operation status, and conversion coefficient constants.

## Control Flow and State
There is no local control flow. Runtime state is represented indirectly as bits the JPEG driver writes and reads: mode selection, stream size limits, interrupt enable/status, power/clock state, timer state, DMA active state, and table selections. Because the header spans incompatible generations, call sites must choose the right register family from device data before programming hardware.

## Dependencies and Integration Points
The file is consumed by the Samsung JPEG platform driver under the same media tree. It integrates with V4L2 memory-to-memory buffer setup through DMA address offsets and format selectors, and with IRQ handling through completion/error/status masks. It depends only on normal C preprocessor semantics and kernel integer types inherited by users.

## Risks
The main risk is programming a register family on the wrong hardware generation. Many field names are similar but offsets differ, especially between S5P/Exynos4 and Exynos3250. Mask constants also encode hardware-specific reserved bits; using a broad mask when preserving unrelated fields could clear feature bits. Stream-bound and timer fields should be validated by tests around oversized JPEGs and timeout paths.

## Test Signals
Useful signals include successful encode/decode on each supported SoC variant, correct interrupt completion and error reporting, correct byte-count reporting, quantization/Huffman table loading, RGB/YUV conversion correctness, tiled and multi-plane formats on Exynos3250, and suspend/reset recovery that leaves `POWER_ON` and clock-down bits consistent.
