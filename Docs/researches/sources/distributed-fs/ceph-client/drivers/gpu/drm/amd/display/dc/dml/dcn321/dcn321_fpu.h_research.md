# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn321/dcn321_fpu.h

## Purpose
This header exposes the DCN321 FPU bounding-box update hook used by resource and clock-management code. It is intentionally narrow: DCN321 contributes only the bandwidth bounding-box update entry point here.

## Important APIs, Types, And Functions
The public API is `dcn321_update_bw_bounding_box_fpu(struct dc *dc, struct clk_bw_params *bw_params)`. The header includes `dml/display_mode_vba.h`, which provides DML-related type visibility used by the declaration path.

## Control Flow And State
There is no control flow or local state in the header. The implementation mutates `dc->dml`, current-state DML, DML2 bounding-box overrides, and DCN321 global IP/SOC bounding-box structures.

## Dependencies And Integration Points
Callers are expected to invoke this only inside FPU-protected display code paths because the implementation calls `dc_assert_fp_enabled()`. It integrates DCN321 resource setup with DML initialization and PMFW/BIOS clock data ingestion.

## Risks
The include guard name is `__DCN32_FPU_H__`, which is broader than the filename and could collide conceptually with DCN32 headers. The API does not indicate FPU requirements or mutation breadth, so call-site discipline is required.

## Test Signals
Compile coverage should verify the declaration is visible to DCN321 resource code. Runtime tests should verify calling the hook updates DML bounding-box state and does not run outside FPU-safe regions.
