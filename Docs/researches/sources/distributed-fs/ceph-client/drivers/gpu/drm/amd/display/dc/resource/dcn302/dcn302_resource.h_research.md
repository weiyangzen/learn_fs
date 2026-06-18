# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn302/dcn302_resource.h

## Purpose
This header declares the DCN302 resource-pool entry points and exposes the DCN302 DML IP/SOC bounding-box globals used by the implementation.

## Important APIs, Types, And Functions
It includes `core_types.h`, declares extern `dcn3_02_ip` and `dcn3_02_soc`, exposes `dcn302_create_resource_pool(const struct dc_init_data *init_data, struct dc *dc)`, and exposes `dcn302_update_bw_bounding_box(struct dc *dc, struct clk_bw_params *bw_params)`.

## Control Flow
ASIC initialization calls `dcn302_create_resource_pool()` after matching DCN302 hardware. Clock-manager or bandwidth code can call `dcn302_update_bw_bounding_box()` when clock/bandwidth parameters change. All actual control flow lives in the C file.

## State And Persistence
The header does not own state but exposes mutable DML globals and the update hook that mutates `dc->dml`/SOC bounding-box data through FPU code.

## Dependencies And Integration Points
The declarations integrate the DCN302 resource implementation with Display Core initialization, clock-bandwidth update paths, and DML/FPU providers for `dcn3_02_ip` and `dcn3_02_soc`.

## Risks
The header exports an update function that assumes the DCN302 FPU implementation and global bounding-box structures are linked. Misusing it for another ASIC family would patch the wrong DML tables.

## Test Signals
Build/link checks should ensure both exported symbols resolve. Runtime signal is a non-null resource pool and successful bounding-box refresh when `clk_bw_params` are updated.
