<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr_smu_msg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr_smu_msg.h

## Purpose

`dcn30_clk_mgr_smu_msg.h` declares the DCN30 SMU mailbox wrapper API.

## Important APIs, Types, And Functions

It declares message wrappers for test/version checks, DRAM address setup, watermark transfers, hard min/max frequency, DPM frequency queries, DC-mode max DPM, deep-sleep DCEFCLK, display count, MALL refresh, external DF C-state allow, and PME workaround.

## Control Flow

The header has no runtime flow. It exposes the typed SMU command surface to `dcn30_clk_mgr.c`.

## State And Persistence Behavior

No state is owned. Implementations persist effects in PMFW and mailbox registers.

## Dependencies And Integration Points

It includes `core_types.h` and forward-declares `struct clk_mgr_internal`. It is the public boundary between DCN30 clock policy and DALSMC transport.

## Risks

Prototype mismatches can corrupt SMU parameter packing or return handling. Because many wrappers are void, callers cannot observe failure unless implementation or logs are checked.

## Test Signals

Build coverage and runtime SMU command tests via DCN30 clock-manager operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr_smu_msg.h -->
