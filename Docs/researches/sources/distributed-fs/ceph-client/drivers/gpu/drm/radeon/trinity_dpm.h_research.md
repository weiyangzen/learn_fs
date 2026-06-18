# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/trinity_dpm.h

## Purpose

`trinity_dpm.h` defines the Trinity-specific DPM private data model shared by `trinity_dpm.c` and `trinity_smc.c`. It describes per-power-level fields, per-power-state policy flags, parsed system information, persistent DPM driver state, and the SMC message helper prototypes used to control DPM firmware.

## Important APIs, Types, and Functions

- `struct trinity_pl` is one hardware SCLK DPM level: SCLK, voltage index, deep/sleep dividers, NB slow/force settings, display watermark, and VCE watermark.
- `struct trinity_ps` wraps up to `SUMO_MAX_HARDWARE_POWERLEVELS` levels plus NB P-state flags, BAPM flags, NB low/high policy values, and UVD low/high divider selections.
- `struct trinity_uvd_clock_table_entry` maps firmware UVD VCLK/DCLK values to divider IDs.
- `struct trinity_sys_info` stores IntegratedSystemInfo data: boot clocks, minimum SCLK, dentist VCO, NB P-state clocks/voltages, thermal limits, SCLK/VID mapping tables, UMA channels, and UVD clock table entries.
- `struct trinity_power_info` is the device-lifetime private DPM state with per-level activity thresholds, feature flags, parsed sys-info, boot level, minimum divider, and current/requested Radeon/Trinity power-state snapshots.
- Prototypes expose SMC operations: BAPM enable, DPM config, UVD DPM config, forced state, disabled-level count, no-forced-level, DCE voltage adjustment, dynamic MGPG config, and SMC mutex acquire/release.

## Control Flow

The header does not execute behavior directly. `trinity_dpm_init()` allocates and populates `struct trinity_power_info`, and every Trinity DPM transition uses the structures here to transform AtomBIOS states into SMU register programming. `trinity_smc.c` implements the SMC command prototypes declared here.

## State and Persistence Behavior

All structures are in-memory driver state; persistent hardware state is represented indirectly through the values later written into SMU registers. `current_rps/current_ps` and `requested_rps/requested_ps` keep stable internal snapshots, with `ps_priv` redirected to the embedded Trinity private copies.

## Dependencies and Integration Points

- Includes `sumo_dpm.h` for shared Sumo/Trinity constants and mapping table types.
- Depends on `struct radeon_device`, `struct radeon_ps`, and Radeon DPM definitions supplied by including translation units.
- Uses register spacing from `trinityd.h` through `TRINITY_SIZEOF_DPM_STATE_TABLE`, so register layout and DPM state structure are coupled.

## Risks and Edge Cases

- The header exposes mutable private structures broadly, so consumers can bypass invariants around `num_levels`, `ps_priv`, or feature flags.
- `TRINITY_POWERSTATE_FLAGS_NBPS_*` and `TRINITY_POWERSTATE_FLAGS_BAPM_DISABLE` are overlapping bit values in separate fields; mixing fields would be easy in future edits.
- `trinity_power_info` stores many booleans that gate register programming; uninitialized or partially initialized instances would produce unsafe hardware sequences.

## Test Signals

- Build coverage should catch type drift between this header, `trinity_dpm.c`, `trinity_smc.c`, and Sumo helpers.
- Runtime DPM tests should inspect current/requested state snapshots and confirm `ps_priv` points at the embedded private state after transitions.
