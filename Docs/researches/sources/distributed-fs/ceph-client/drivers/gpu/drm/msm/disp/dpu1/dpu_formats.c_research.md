# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_formats.c

## Purpose
Computes DPU hardware framebuffer layout metadata from DRM framebuffer state and MSM format descriptors. It validates dimensions and pitches, calculates plane sizes/pitches for linear and UBWC/tiled formats, and maps framebuffer IOVAs into the plane order expected by DPU hardware.

## Important APIs, Types, and Functions
Exports `dpu_format_populate_plane_sizes` and `dpu_format_populate_addrs`. Internal helpers include `_dpu_get_v_h_subsample_rate`, `_dpu_format_populate_plane_sizes_ubwc`, `_dpu_format_populate_plane_sizes_linear`, `_dpu_format_populate_addrs_ubwc`, and `_dpu_format_populate_addrs_linear`. `DPU_UBWC_PLANE_SIZE_ALIGNMENT` enforces 4 KiB plane alignment.

## Control Flow and State
The file is stateless. `dpu_format_populate_plane_sizes` clears `dpu_hw_fmt_layout`, sets image dimensions and format plane count, then chooses UBWC/tile or linear calculations. Linear layouts verify framebuffer pitches are at least the required hardware pitch and use user pitch when larger. UBWC YUV and RGB paths compute bitstream and metadata sizes using format-specific tile sizes, scanline rounding, stride rounding, and an RGB meta-plane quirk where uAPI leaves plane 1 empty and metadata is plane 2. Address population then uses `msm_framebuffer_iova`; UBWC reorders base-address offsets so hardware sees bitstream planes before metadata planes.

## Dependencies and Integration Points
Depends on DRM framebuffer fields, `msm_framebuffer_format`, `msm_framebuffer_iova`, format flags such as `MSM_FORMAT_IS_UBWC`, `MSM_FORMAT_IS_TILE`, `MSM_FORMAT_IS_YUV`, `MSM_FORMAT_IS_DX`, and DPU max image limits from the catalog header. Writeback setup consumes both sizes and addresses.

## Risks and Test Signals
Layout errors lead directly to memory corruption or wrong scanout/writeback content. Risks include unsupported odd dimensions for subsampled formats, DX tight-unpack stride math, RGB UBWC plane count adjustment, YUV metadata offsets, and pitch acceptance for linear multi-plane buffers. Tests should validate known-good offsets and total sizes for RGB linear, NV12/P010 linear, UBWC RGB, UBWC NV12-like formats, oversized dimension rejection, and undersized pitch rejection.
