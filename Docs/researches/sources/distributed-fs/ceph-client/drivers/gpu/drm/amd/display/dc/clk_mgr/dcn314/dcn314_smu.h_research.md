<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn314/dcn314_smu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn314/dcn314_smu.h

## Purpose
Defines the DCN314 display SMU ABI data structures and function prototypes used by the clock manager to exchange DPM and watermark tables with PMFW.

## Important APIs, Types, And Functions
- `DpmClocks314_t` describes PMFW-reported DCF/DISP/DPP/SOC/VCN clocks, SOC voltages, DF pstate data, enabled level counts, and GFX clock limits.
- `DfPstateTable314_t` includes FCLK, memory clock, voltage, and WCK ratio.
- `struct dcn314_watermarks` mirrors PMFW's two-dimensional watermark rows plus MMHUB padding.
- `struct dcn314_smu_dpm_clks`, `struct display_idle_optimization`, and `union display_idle_optimization_u` define GPU table addressing and idle bit packing.

## Control Flow
The header has no executable flow, but the table IDs and prototypes define which operations the `.c` mailbox layer can issue: version query, clock requests, table transfers, idle optimization, zstate policy, and DTBCLK control.

## State And Persistence
DPM and watermark structures are copied through GPU-visible memory shared with PMFW. The idle optimization union persists only as a packed message argument. WCK ratios become persisted bandwidth-table fields after construction.

## Dependencies And Integration Points
It includes `smu13_driver_if_v13_0_4.h` for common PMFW constants such as clock-level counts and watermark row definitions. It is tightly coupled to the DCN314 clock-manager bandwidth-population logic.

## Risks And Edge Cases
ABI layout drift between driver and PMFW would corrupt DPM or watermark interpretation. The code assumes enabled counts do not exceed fixed array lengths and that at least one valid memory/FCLK entry exists when constructing bandwidth limits.

## Test Signals
Compile-time structure compatibility, successful DPM table transfer, correct WCK ratio conversion, valid watermark row upload, and sane enabled-level counts from PMFW are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn314/dcn314_smu.h -->
