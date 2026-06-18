<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn315/dcn315_smu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn315/dcn315_smu.h

## Purpose
Defines the DCN315 PMFW display clock ABI: DPM clock table format, watermark table format, table IDs, idle optimization bits, and SMU helper prototypes.

## Important APIs, Types, And Functions
- `DpmClocks_315_t` holds four-level DCF/DISP/DPP/SOC/VCN clock arrays, SOC voltages, DF pstate entries, enabled counts, and GFX limits.
- `WatermarkRowGeneric_t`, `WM_CLOCK_e`, and `struct dcn315_watermarks` describe PMFW watermark rows for SOC and DCF clocks.
- `struct dcn315_smu_dpm_clks` stores the PMFW-transfer table pointer and GPU address.
- Prototypes expose clock set/query, table transfer, idle optimization, voltage request declaration, PME workaround, and DTBCLK control.

## Control Flow
There is no executable flow. The constants and types constrain how `dcn315_smu.c` and `dcn315_clk_mgr.c` pack messages and interpret transferred tables.

## State And Persistence
DPM and watermark data persist in GPU-visible temporary or long-lived allocations owned by the clock manager. The idle optimization union is packed into a 32-bit PMFW argument.

## Dependencies And Integration Points
Includes `os_types.h` for fixed-width types and depends on `clk_mgr_internal` declarations supplied by includers. It is coupled to PMFW driver interface version 4.

## Risks And Edge Cases
The header declares `dcn315_smu_request_voltage_via_phyclk`, but the implementation in this subset does not define it, so callers must not rely on it unless another translation unit supplies it. Fixed array sizes mean PMFW enabled counts must be validated by consumers.

## Test Signals
Compile/link coverage for declared functions, DPM table import with four levels, watermark upload, and pstate table sanity checks are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn315/dcn315_smu.h -->
