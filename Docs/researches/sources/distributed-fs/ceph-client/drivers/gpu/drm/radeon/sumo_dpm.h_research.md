<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/sumo_dpm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/sumo_dpm.h

## Purpose
`sumo_dpm.h` is the private Sumo DPM interface and state header. It defines Sumo power-level/power-state structures, BIOS-derived system information, persistent DPM private state, default timing constants, and cross-file prototypes shared by `sumo_dpm.c`, `sumo_smc.c`, Trinity/Sumo-adjacent code, and Radeon ASIC registration.

## Important APIs, types, and definitions
- `struct sumo_pl` describes one hardware power level: SCLK, VDDC index, deep-sleep and short-sleep divider IDs, GNB-slow permission, and SCLK DPM TDP limit.
- `struct sumo_ps` contains up to `SUMO_MAX_HARDWARE_POWERLEVELS` levels plus flags for forced NBPS1 and boost state.
- Mapping/system structures: display-clock voltage map, VID mapping table, SCLK voltage map, and `struct sumo_sys_info`, which stores boot/min clocks, UMA clock, NB voltage, HTC limits, M3 arbiter tables, boost/TDP margins, boost SCLK/VID, and boost enablement.
- `struct sumo_power_info` is the DPM private state with timing parameters, feature flags, firmware version, system info, boot/ACPI/boost levels, and cached current/requested Radeon/Sumo power states.
- Default timing constants configure UTC/DTC arrays, activity hysteresis, response limits, VC, clock-gating, voltage-drop, and power-gating timings.
- Prototypes expose Sumo DPM helpers such as clock-gating initialization, VC/SSTP programming, SMU control, mapping table constructors, VID conversion, sleep divider selection, and `sumo_get_pi`, plus SMC helper calls for M3 arbiter, PG init, TDP limit, alt-VDDNB notification, boost, timer, and firmware version.

## Control flow and integration points
The header has no executable control flow. It defines the shared contract between the Sumo DPM implementation and the Sumo SMU helper implementation. Radeon ASIC callback prototypes are also declared in `radeon_asic.h`, but this header carries the Sumo-private helpers used within the power-management subsystem.

## State and persistence behavior
The structures persist as driver heap state across the DPM lifecycle. `sumo_power_info` is allocated during `sumo_dpm_init`, referenced through `rdev->pm.dpm.priv`, updated during state transitions, and freed in `sumo_dpm_fini`. Its fields mirror persistent hardware and firmware state but are not themselves written to disk.

## Dependencies and constraints
The file includes `atom.h` and `radeon.h`, tying it to AtomBIOS table types and Radeon core structures. Counts are fixed: five normal hardware power levels, 15 trend-control entries, ten M3 arbiter parameter sets, and four voltage entries. Callers must not exceed those bounds when translating BIOS tables.

## Risks and test signals
Layout or semantic drift between this header and `sumo_dpm.c`/`sumo_smc.c` can break DPM state transitions, boost handling, or firmware notifications. Test signals include successful compile linkage, Sumo DPM init/enable/fini, PowerPlay table parsing, boost and forced NBPS1 transitions, debugfs output, and suspend/resume state restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/sumo_dpm.h -->
