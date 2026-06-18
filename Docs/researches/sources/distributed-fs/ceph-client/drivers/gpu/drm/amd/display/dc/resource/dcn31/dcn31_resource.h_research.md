# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.h

## Purpose
This header is the public interface for DCN31 resource construction and resource-specific helper operations. It also carries temporary B0-specific PHY PLL pixel-clock register definitions used before switching fully to DCN313 headers.

## Important APIs, Types, And Functions
`TO_DCN31_RES_POOL()` downcasts a generic pool to `struct dcn31_resource_pool`, which embeds `struct resource_pool base`. It declares extern `dcn3_1_ip`. Public APIs include resource creation, bandwidth validation, watermark/DLG calculation, DML pipe population, writeback DML population, MCIF arbitration setup, DET-buffer query, and `dcn31_update_dc_state_for_encoder_switch()` for DP1/DP2 encoder-rate transitions.

## Control Flow
The header enables other DC code to call DCN31-specific validation/population helpers through either direct declarations or the `resource_funcs` table installed by the C file. The encoder-switch function is called when a link changes mode/rate and needs current-state pipe pixel-clock and audio output updates.

## State And Persistence
No state is allocated by the header. It defines access to the DCN31 wrapper pool and exposes the mutable DML IP global. The temporary register constants encode hardware register addresses, shifts, and masks used by implementation code.

## Dependencies And Integration Points
It depends on `core_types.h` for DC core structures and integrates with DML, resource construction, link training/retraining, writeback, MCIF arbitration, and DET policy code. The register constants bridge missing/generated header coverage for Yellow Carp B0 PHY PLL resync controls.

## Risks
Temporary register definitions can become stale when generated headers change. Direct exports of many helpers increase the chance of cross-generation misuse. The downcast macro requires that the generic pointer really point to `struct dcn31_resource_pool`.

## Test Signals
Compile coverage should catch signature drift. Runtime signals include correct resource creation, validation callbacks, DET query behavior, and successful DP encoder switching with pixel-rate/audio recalculation.
