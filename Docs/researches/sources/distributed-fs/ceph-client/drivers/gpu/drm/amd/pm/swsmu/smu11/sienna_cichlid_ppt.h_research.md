# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/sienna_cichlid_ppt.h Research

## Purpose
`sienna_cichlid_ppt.h` is the public header for the Sienna Cichlid-family SMU11 PowerPlay table implementation. It defines a small AC/DC power-source enum, ASIC-family UMD profiling clock constants, and the `sienna_cichlid_set_ppt_funcs()` registration entry point.

## Important APIs, Types, And Functions
`POWER_SOURCE_e` declares `POWER_SOURCE_AC`, `POWER_SOURCE_DC`, and `POWER_SOURCE_COUNT`. The profiling constants define standard UMD pstate GFXCLK, SOCCLK, and MEMCLK values for Sienna Cichlid/Navy Flounder, Dimgrey Cavefish, and Beige Goby. The header declares `extern void sienna_cichlid_set_ppt_funcs(struct smu_context *smu);`.

## Control Flow
The header has no executable control flow. Its constants are consumed by `sienna_cichlid_populate_umd_state_clk()`, which chooses standard UMD pstate clocks based on MP1 IP version. The function declaration is used by ASIC dispatch code to install the Sienna Cichlid PPT vtable and mappings into the active SMU context.

## State, Persistence, And Dependencies
The header stores no runtime state. The enum and constants become runtime policy only when the C implementation uses them to populate `smu->pstate_table` or map power-source behavior. The header assumes `struct smu_context` is available through the including compilation unit and uses normal include guards.

## Integration Points
`sienna_cichlid_ppt.c` includes this header for UMD profiling constants and the local entrypoint declaration. Higher-level SMU initialization uses `sienna_cichlid_set_ppt_funcs()` for MP1 IP versions 11.0.7, 11.0.11, 11.0.12, and 11.0.13.

## Risks
The profiling constants are static policy. If a new board or firmware changes recommended UMD standard clocks while staying on this implementation path, reported or selected standard pstates may not match the hardware's desired policy. The local `POWER_SOURCE_e` overlaps conceptually with common SMU power-source mappings, so edits should avoid introducing enum-value drift against firmware expectations.

## Test Signals
Indirect validation should check UMD pstate standard clocks on each supported ASIC family, verify AC/DC power-source notifications still map correctly through the common-to-ASIC map, and confirm ASIC dispatch invokes `sienna_cichlid_set_ppt_funcs()` only for compatible SMU11 IP versions.
