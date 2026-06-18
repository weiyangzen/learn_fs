# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_formats.h

## Purpose
Declares the DPU format helper API and provides a small inline helper for checking whether a DRM fourcc appears in a supported-format table.

## Important APIs, Types, and Functions
`dpu_find_format` linearly searches a `u32` format array and returns true on exact match. `dpu_format_populate_addrs` fills plane IOVA addresses in `struct dpu_hw_fmt_layout`, and `dpu_format_populate_plane_sizes` fills layout dimensions, pitches, sizes, plane count, and total size.

## Control Flow and State
There is no persistent state. The inline lookup is intentionally simple and is used by resource and format validation paths that already hold catalog-backed arrays. The implementation functions declared here operate on caller-provided DRM framebuffer and DPU layout structures.

## Dependencies and Integration Points
Includes DRM fourcc definitions, MSM GEM/framebuffer declarations, and `dpu_hw_mdss.h` for layout types. It is consumed by writeback setup, plane validation, and other DPU paths that need DPU-specific plane layout rather than generic DRM layout.

## Risks and Test Signals
The main header-level risk is passing an incorrect `num_formats` or unsynchronized catalog format table; the helper cannot detect malformed arrays. Tests should check format validation against VIG/DMA/WB catalog format lists and ensure callers handle false results before programming hardware. ABI-sensitive tests should confirm layout helper outputs remain compatible with DRM framebuffer pitch/address expectations.
