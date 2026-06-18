<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn31/dcn31_smu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn31/dcn31_smu.h

## Purpose

`dcn31_smu.h` defines the DCN31 PMFW interface subset and declares SMU mailbox helpers. It provides binary layouts for display clocks, DPM clocks, watermarks, custom DPM settings, metrics, table IDs, idle optimization bits, and WCK ratio metadata.

## Important APIs, Types, And Functions

Key definitions include `PMFW_DRIVER_IF_VERSION`, `FloatInIntFormat_t`, `DSPCLK_e`, `DisplayClockTable_t`, `WatermarkRowGeneric_t`, watermark constants/enums, `CustomDpmSettings_t`, DPM level counts, `WCK_RATIO_e`, `DfPstateTable_t`, `DpmClocks_t`, throttler status bits, `SmuMetrics_t`, workload bits, table IDs, `struct dcn31_watermarks`, `struct dcn31_smu_dpm_clks`, display idle bitfield/union, and all `dcn31_smu_*` prototypes.

## Control Flow

There is no runtime flow. The structures are allocated and filled by `dcn31_clk_mgr.c`, transferred with `dcn31_smu.c`, and interpreted by PMFW.

## State And Persistence Behavior

The header describes shared ABI state: DPM tables copied from SMU, watermark tables copied to SMU, DTB/Z-state/idle parameters sent by messages, and metrics/custom DPM structures used by broader PMFW consumers. Runtime ownership is outside the header.

## Dependencies And Integration Points

It is the contract between DCN31 display clock code and PMFW. The clock manager uses `DpmClocks_t`, `dcn31_watermarks`, table IDs, WCK ratio enums, and idle bitfields directly.

## Risks

ABI layout drift is high risk because padding, counts, enum values, and table IDs must match PMFW. The `PMFW_DRIVER_IF_H` guard wraps many definitions, so include-order interactions with other PMFW headers can change what is visible. The idle optimization struct is marked as copied from Van Gogh and may not be fully correct.

## Test Signals

Static ABI layout/version checks, DPM table transfer and parse validation, watermark upload acceptance, WCK ratio handling, Z-state/DTBCLK message tests, and build coverage with other PMFW headers included in different orders.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn31/dcn31_smu.h -->
