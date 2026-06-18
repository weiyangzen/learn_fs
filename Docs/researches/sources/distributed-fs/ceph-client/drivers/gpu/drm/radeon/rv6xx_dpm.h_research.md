# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv6xx_dpm.h

## Purpose
`rv6xx_dpm.h` defines the private data model used by `rv6xx_dpm.c` to translate BIOS PowerPlay states into register-programmable RV6xx DPM state.

## Important APIs, Types, and Functions
The header exports no functions. Its core types are `struct rv6xx_sclk_stepping` for a single VCO/post-divider engine-clock step, `struct rv6xx_pm_hw_state` for computed hardware indices and clock/voltage/backbias/PCIe arrays, `struct rv6xx_power_info` for driver-private feature and runtime state, `struct rv6xx_pl` for one logical power level, and `struct rv6xx_ps` for high/medium/low levels. It also defines default UVD VCLK/DCLK values in 10 kHz units.

## Control Flow
The header is consumed after `rv6xx_dpm_init` allocates `struct rv6xx_power_info` and attaches it to `rdev->pm.dpm.priv`. Parsed PowerPlay states allocate `struct rv6xx_ps` into each `radeon_ps.ps_priv`. Subsequent DPM enable and transition flows fill `rv6xx_pm_hw_state` from the requested `rv6xx_ps` and use the stored feature flags to decide which register blocks to program.

## State and Persistence
`struct rv6xx_power_info` persists for the DPM lifetime and is freed by `rv6xx_dpm_fini`. It stores probed platform capabilities, spread-spectrum flags, voltage-control availability, thermal/display/clock-gating booleans, PLL divider scaling, active auto-throttle sources, forced-level restrictions, and the current computed hardware state. `struct rv6xx_ps` instances persist as per-BIOS-state private payloads attached to `rdev->pm.dpm.ps`.

## Dependencies and Integration Points
The header includes `r600_dpm.h` for shared constants such as power-level counts. Its structs are not standalone ABI; they are internal to the radeon driver and tied to the R600/RV6xx register model, ATOMBIOS PowerPlay parsing, and common Radeon DPM callback wiring.

## Risks
Array sizes must stay aligned with R600 DPM constants. Since hardware indices are cached as `u8`, invalid generation of stepping indices or voltage indices can corrupt later register programming. Any extension must preserve the high/medium/low ordering assumed by parser, debugfs, and transition code.

## Test Signals
Build coverage is the primary signal for this header. Runtime validation comes indirectly from successful RV6xx DPM init/fini, power-state parsing, power-level transitions, forced-level changes, and debugfs current-level reporting using the structs defined here.
