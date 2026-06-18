# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn303/dcn303_resource.h

## Purpose
This header declares the DCN303 resource constructor and bandwidth-bounding-box update hook for Beige Goby / DCN3.0.3 resource setup.

## Important APIs, Types, And Functions
It includes `core_types.h`, declares extern DML globals `dcn3_03_ip` and `dcn3_03_soc`, declares `dcn303_create_resource_pool(const struct dc_init_data *init_data, struct dc *dc)`, and declares `dcn303_update_bw_bounding_box(struct dc *dc, struct clk_bw_params *bw_params)`.

## Control Flow
Display Core ASIC selection calls the constructor; bandwidth/clock update paths call the update hook. The header contributes declarations only.

## State And Persistence
No direct state is stored. The extern DML symbols are mutable global state owned by DCN303 DML code and patched by the C implementation.

## Dependencies And Integration Points
The header is a narrow boundary between ASIC init code, resource construction, and DCN303 FPU/DML code. It depends on `core_types.h` for DC and clock-bandwidth type definitions.

## Risks
Because DCN302 and DCN303 headers have nearly identical APIs, wiring the wrong constructor or update hook would compile but initialize the wrong resource shape. The DML externs must match the DCN303 implementation.

## Test Signals
Compile/link checks for exported symbols, plus runtime probe selecting DCN303 and using two-pipe caps, are the primary signals.
