# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/vegam_smumgr.h

Purpose: private VegaM SMU manager header for the SMU75 path. It defines SMU RAM bounds, tuning bit shifts/defaults, PowerTune default layout, SCLK range cache, and backend state used by `vegam_smumgr.c`.

Important APIs and types: `SMC_RAM_END` sets the SMC SRAM limit used in copy/read calls. `DPMTuning_*` shifts and `GraphicsDPMTuning_VEGAM`, `MemoryDPMTuning_VEGAM`, `SclkDPMTuning_VEGAM`, and `MclkDPMTuning_VEGAM` encode default hysteresis/activity values. `struct vegam_pt_defaults` stores PowerTune and BAPM constants sized by SMU75 dimensions. `struct vegam_range_table` caches lower/upper SCLK transition frequencies. `struct vegam_smumgr` embeds common SMU7 data, protected-mode flag, SMU75 DPM table, ULV state, PM fuses, range table, selected defaults, and BIF SCLK levels.

Control flow and integration: the implementation allocates this struct as `hwmgr->smu_backend`, fills range and BIF tables during DPM setup, and serializes SMU75 tables to firmware SRAM. The header bridges generic SMU7 helpers with VegaM-specific SMU75 layouts.

State and persistence: all fields are driver cache until copied to SMC SRAM or used to send SMU messages. `protected_mode` records boot mode discovery; `range_table` supports fallback FCW calculations; `bif_sclk_table` feeds link-level DFS divider programming.

Dependencies, risks, and tests: depends on `pp_endian.h`, `smu75_discrete.h`, and `smu7_smumgr.h`. Risks are firmware-structure size coupling, hardcoded tuning constants, and duplicated names relative to other SMU manager headers. Compile coverage and table-upload boot tests on VegaM hardware are the primary signals.
