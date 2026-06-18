# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/polaris10_smumgr.h

## Purpose
This header defines the private Polaris SMU manager state used by `polaris10_smumgr.c`. It binds the generic SMU7 manager storage to Polaris-specific SMU74 table mirrors, PowerTune defaults, SCLK range data, BIF SCLK values, and memory-controller register table state.

## Important APIs, types, and functions
The important types are `struct polaris10_pt_defaults`, `struct polaris10_range_table`, and `struct polaris10_smumgr`. `polaris10_pt_defaults` carries default PowerTune knobs such as SVI load-line parameters, TDC behavior, DTE ambient temperature, display CAC, BAPM gradient, and BAPM thermal impedance arrays. `polaris10_range_table` stores fallback SCLK transition frequency bounds. `polaris10_smumgr` embeds `struct smu7_smumgr`, a `protected_mode` flag, host mirrors for `SMU74_Discrete_DpmTable`, ULV, and PM fuse data, a range table, a pointer to selected PowerTune defaults, BIF SCLK entries, and an ATOMBIOS MC register table.

## Control flow, state, and integration
The header has no executable control flow, but its layout controls how the C implementation shares state across SMU startup, firmware-header processing, DPM table construction, runtime DPM updates, and teardown. Because `smu7_data` is the first field, code can treat `hwmgr->smu_backend` as either Polaris-specific state or SMU7-compatible state in shared helpers. The `smc_state_table` and `power_tune_table` are host mirrors copied into SMC SRAM, while offset and BO state inside `smu7_data` persists until `smu7_smu_fini` frees it.

## Dependencies, risks, and test signals
The header depends on endian helpers, SMU74 firmware structures, SMU74 discrete table definitions, and SMU7 manager definitions. The main risk is structure layout coupling: helper code assumes the embedded `smu7_smumgr` is available at `hwmgr->smu_backend`, and the C file assumes SMU74 structure layouts match firmware. Test signals are successful initialization, correct table offset storage, and clean teardown without BO leaks or invalid casts.
