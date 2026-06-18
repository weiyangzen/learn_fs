# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ni_dpm.h

## Purpose

`ni_dpm.h` defines the Northern Islands DPM private data model and exported helpers used by `ni_dpm.c` and adjacent Radeon power-management code. It is the structural contract between generic Radeon PM state and NI-specific SMC/CAC/MC timing implementation.

## Important Types and Constants

- `struct ni_clock_registers` snapshots SPLL/MPLL/MCLK/DLL/spread-spectrum registers used to build SMC clock states.
- `struct ni_mc_reg_entry` and `struct ni_mc_reg_table` hold VBIOS-derived memory-controller register timing entries plus SMC register address mappings and a validity bitmap.
- `enum ni_dc_cac_level` defines DC CAC table levels.
- `struct ni_leakage_coeffients`, `struct ni_cac_data`, and `struct ni_cac_weights` describe leakage formula inputs, runtime CAC table data, and per-chip hardware CAC weights.
- `struct ni_ps` is the NI private power-state payload: count, DC compatibility, and up to `NISLANDS_MAX_SMC_PERFORMANCE_LEVELS_PER_SWSTATE` RV7xx-style performance levels.
- `struct ni_power_info` is the main private DPM object. It embeds `struct evergreen_power_info` first, then NI clock snapshots, MC tables, flags, SMC offsets, CAC state, current/requested states, and scratch SMC structures.

Constants define SMC arb slots, MC register table driver slot base, and DPM2 power-containment/SQ-ramping parameters.

## Exported APIs

The header publishes `ni_copy_and_switch_arb_sets()`, current/requested power-state update helpers, UVD clock ordering helpers, `ni_dpm_vblank_too_short()`, and accessors `ni_get_pi()`/`ni_get_ps()`.

## Control Flow and State

The header itself has no executable control flow, but its layout drives `ni_dpm.c`. The comment `/* must be first! */` on `struct ni_power_info.eg` is critical: generic Evergreen/RV770 helper code can treat NI private data as an Evergreen power-info prefix. Current/requested state copies inside `ni_power_info` provide stable backing storage for `eg_pi->current_rps.ps_priv` and `eg_pi->requested_rps.ps_priv`.

## Dependencies and Integration Points

`ni_dpm.h` includes `cypress_dpm.h`, `btc_dpm.h`, and `nislands_smc.h`, so it depends on RV7xx/Evergreen/BTC performance-level structures and SMC table definitions. Consumers must already be in the Radeon driver environment with `struct radeon_device`, `struct radeon_ps`, integer types, and AtomBIOS constants available.

## Risks and Test Signals

Structure layout changes are high risk because SMC table sizes, array bounds, and prefix embedding are assumed by implementation code. Changes to CAC weights or DPM2 constants can alter thermal/power behavior. Build coverage catches signature and include issues; runtime DPM tests, SMC table upload success, and debugfs current-state reporting validate that the structures are populated consistently.
