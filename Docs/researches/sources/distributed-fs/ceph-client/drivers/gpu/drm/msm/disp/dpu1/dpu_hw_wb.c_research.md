# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_wb.c

## Purpose
Implements the DPU writeback hardware wrapper for destination addresses, output format, ROI, QoS, CDP, pingpong binding, and clock force control.

## Important APIs, types, and functions
- `dpu_hw_wb_init()` constructs a `struct dpu_hw_wb` and installs ops.
- `dpu_hw_wb_setup_outaddress()` writes destination plane addresses.
- `dpu_hw_wb_setup_format()` programs destination format, pack pattern, strides, output size, alpha behavior, and address status.
- `dpu_hw_wb_roi()` programs output image size and ROI output size.
- QoS/CDP helpers: `dpu_hw_wb_setup_qos_lut()`, `dpu_hw_wb_setup_qos_lut_v13()`, and `dpu_hw_wb_setup_cdp()`.
- `dpu_hw_wb_bind_pingpong_blk()` muxes writeback to pingpong/CWB paths.

## Control flow
Ops are installed according to catalog features and MDSS major version: ROI if `DPU_WB_XY_ROI_OFFSET`, QoS if `DPU_WB_QOS` with v13 common QoS layout, CDP if supported, pingpong binding from v5, and clock force from v9. Format setup builds a destination format word from `msm_format`, enables alpha channel or alpha fill behavior as needed, chooses YUV bit, packs element order, writes strides and either ROI or full-destination output size.

## State and persistence
Wrapper state stores MMIO base, WB index, catalog caps, and ops. Destination addresses and format/ROI/QoS/mux registers persist in the WB block through the writeback job until reprogrammed.

## Dependencies and integration points
Depends on `dpu_formats`, writeback catalog caps, MDSS format layout, pingpong enums, and shared QoS/CDP/clock utilities. `dpu_kms.c` initializes writeback connector/encoder support when WB_2 exists in the catalog.

## Risks
There is a duplicate `WB_DST_YSTRIDE1` macro definition with the same value; harmless but noisy. Format programming assumes the supplied `msm_format` and layout are consistent with the DRM writeback job. Pingpong mux encodings for CWB and PP paths are hard-coded and must track hardware documentation.

## Test signals
Writeback jobs should validate captured image content, formats, alpha behavior, ROI cropping, UBWC/CDP if supported, CWB mux selection, and register snapshots for WB format/address/QoS blocks.
