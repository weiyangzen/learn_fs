# sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-cpmem.c

## Purpose
Implements Channel Parameter Memory programming for IPUv3 IDMAC channels. CPMEM entries describe image dimensions, strides, DMA buffer addresses, pixel format layout, rotation/block mode, burst size, interlacing, UV offsets, priority, and alpha/separate-plane behavior.

## Important APIs, Types, and Functions
`struct ipu_cpmem_word`, `struct ipu_ch_param`, and `struct ipu_cpmem` model packed parameter memory and its spinlock. Low-level `ipu_ch_param_write_field()` and `ipu_ch_param_read_field()` write bitfields that may cross 32-bit words using `bitrev8()`. Exported setters include `ipu_cpmem_zero()`, resolution/stride/buffer/UV/interlaced/burst/block/rotation/AXI/high-priority functions, RGB/passthrough/YUV format functions, `ipu_cpmem_set_fmt()`, `ipu_cpmem_set_image()`, and `ipu_cpmem_dump()`. RGB format descriptors define bit widths and offsets for many DRM fourcc formats.

## Control Flow
Users typically obtain an IDMAC channel, call `ipu_cpmem_zero()`, set image geometry and format either explicitly or via `ipu_cpmem_set_image()`, set buffers, burst/rotation/block flags, then enable the channel through `ipu-common.c`. `ipu_cpmem_set_image()` validates crop/size assumptions, selects planar/packed address offsets, handles V4L2-to-DRM conversion for legacy formats, programs resolution/stride/format, and stores plane addresses. Initialization maps the 128 KiB CPMEM aperture and stores it in `ipu->cpmem_priv`.

## State and Persistence
State is hardware CPMEM content plus the mapped base and spinlock in `struct ipu_cpmem`. CPMEM content persists until overwritten or reset. The spinlock serializes field writes so read-modify-write sequences do not corrupt adjacent packed fields.

## Dependencies and Integration Points
Depends on DRM fourcc definitions, V4L2 pixel format compatibility mapping, bit reversal helpers selected by Kconfig, and `struct ipuv3_channel` from the private IPU headers. It is used by image conversion, display, capture, and any IDMAC client before channel enable.

## Risks
Packed bitfield writes are sensitive to field definitions and cross-word handling. DMA base fields shift addresses, so unsupported alignment or high physical addresses could be misprogrammed if callers violate assumptions. Planar offset calculations depend on bytesperline, crop, subsampling, and chroma order; wrong format metadata causes corrupted images. Separate alpha uses a limited channel mapping table and returns errors for unsupported channels.

## Test Signals
Useful tests are format-by-format CPMEM dumps for RGB, packed YUV, NV12/NV16, planar YUV, interlaced scan, rotation, and separate alpha. Hardware frame checks should verify stride, crop, chroma offsets, and double-buffer addresses. KUnit-style tests for field packing would catch bitfield regressions without hardware.
