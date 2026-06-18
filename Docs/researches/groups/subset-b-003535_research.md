# subset-b-003535 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/navi10_ppt.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/navi10_ppt.c

### Purpose
`navi10_ppt.c` is the SMU11 PowerPlay table implementation for Navi 1x ASICs using the Navi10/Navi12/Navi14 firmware interface. It binds the generic AMDGPU SWSMU layer to ASIC-specific message IDs, clock IDs, feature IDs, table layouts, sysfs power-management operations, metrics decoding, OverDrive controls, display watermark programming, BACO runtime power transitions, SMU-backed I2C, and several Navi-specific firmware workarounds.

### Important APIs, Types, And Functions
The file is centered on `navi10_ppt_funcs`, a `struct pptable_funcs` vtable installed by `navi10_set_ppt_funcs()`. Static mapping arrays translate common SMU concepts into ASIC firmware concepts: `navi10_message_map`, `navi10_clk_map`, `navi10_feature_mask_map`, `navi10_table_map`, `navi10_pwr_src_map`, `navi10_workload_map`, and `navi1x_throttler_map`.

Power table setup flows through `navi10_setup_pptable()`, `navi10_store_powerplay_table()`, `navi10_append_powerplay_table()`, and `navi10_check_powerplay_table()`. `navi10_tables_init()` declares SMU VRAM tables and allocates host-side metrics, watermark, GPU metrics, and driver config buffers. `navi10_init_allowed_features()` builds the allowed firmware feature mask from `adev->pm.pp_feature`, power-gating flags, DC GPIO control, secure ASIC checks, and revision quirks.

Runtime APIs include `navi10_set_default_dpm_table()`, `navi10_emit_clk_levels()`, `navi10_force_clk_levels()`, `navi10_read_sensor()`, `navi10_get_power_limit()`, `navi10_get_thermal_temperature_range()`, `navi10_update_pcie_parameters()`, `navi10_set_watermarks_table()`, and `navi10_notify_smc_display_config()`. OverDrive is handled by `navi10_set_default_od_settings()`, `navi10_od_edit_dpm_table()`, range helpers, and `navi10_overdrive_get_gfx_clk_base_voltage()`. Metrics fan out through legacy and newer Navi10/Navi12 structures via `navi1x_get_smu_metrics_data()` and `navi1x_get_gpu_metrics()`. SMU I2C is exported through `navi10_i2c_xfer()`, `navi10_i2c_algo`, and `navi10_i2c_control_init()`.

### Control Flow
Initialization starts when `navi10_set_ppt_funcs()` assigns the vtable, mapping tables, workload maps, power-source maps, and driver interface version for MP1 IP versions 11.0.0, 11.0.5, and 11.0.9. The generic SMU layer then calls into the vtable. PPT setup first delegates ATOM/VBIOS parsing to `smu_v11_0_setup_pptable()`, copies the firmware `PPTable_t` into the driver PPT buffer, appends trailing board fields from the ATOM `smc_dpm_info` table revision 4.5 or 4.7, checks platform capabilities, and wires `smu->od_settings` directly to the powerplay table's overdrive limits.

SMC table initialization declares table sizes for PPTABLE, WATERMARKS, SMU_METRICS, I2C_COMMANDS, OVERDRIVE, PMSTATUSLOG, ACTIVITY_MONITOR_COEFF, and DRIVER_SMU_CONFIG, then allocates CPU-side mirrors. Default DPM setup queries firmware tables when DPM features are enabled and falls back to VBIOS boot clocks when they are not. Fine-grained DPM is inferred from `DpmDescriptor[].SnapToDiscrete`.

Clock reporting maps sysfs clock types to DPM tables or OverDrive table views. PCIE reporting uses current link speed and width from SMU helpers. Clock forcing converts a bitmask to soft min/max DPM indices, clamps fine-grained tables to the low/high endpoints, translates indices to frequencies, and sends soft frequency limits to PMFW. Display reconfiguration sends display count, deep-sleep DCEFCLK, and UCLK hard-min requests depending on feature enablement and watermark state.

Metrics collection first reads the firmware metrics table through `smu_cmn_get_metrics_table()`, then selects a layout based on MP1 IP version and SMU firmware version. Legacy layouts provide direct average clocks; newer layouts choose pre-deep-sleep or post-deep-sleep GFXCLK based on a 15 percent activity threshold. GPU metrics conversion fills `gpu_metrics_v1_3`, including temperatures, activity, power, clocks, throttle status, fan speed, PCIe data, system time, and derived voltages.

OverDrive initialization exports the firmware overdrive table, fills missing curve voltages by asking PMFW for base GFX voltage, and snapshots boot, live, and user OD tables. OD edits validate feature support and board ranges before modifying SCLK min/max, MCLK max, a three-point VDDC curve, restore, or commit. Commit pushes `SMU_TABLE_OVERDRIVE` to PMFW and updates `smu->user_dpm_profile.user_od`.

Post-initialization may run the UMC CDR workaround for Navi10/Navi14 when UCLK DPM is enabled. New enough PMFW is queried with `GET_UMC_FW_WA`; depending on UMC firmware status it either toggles UCLK hard limits or programs a dummy pstate VRAM table filled with `NoDbiPrbs7`/`DbiPrbs7` patterns. BACO entry and exit choose between ArmD3 sequencing and legacy BACO messages depending on runtime PM and audio-function availability.

### State, Persistence, And Dependencies
Persistent driver state is kept in `struct smu_context`, `struct smu_table_context`, `struct smu_dpm_context`, `struct smu_baco_context`, `smu->pstate_table`, `smu->user_dpm_profile`, `smu->custom_profile_params`, watermark bitmaps, and SMU table buffers. Firmware-visible state is persisted by writing SMU tables in VRAM and sending SMC messages. User OD state persists across commits and, by design, is not overwritten on suspend/resume in `navi10_set_default_od_settings()`.

Key dependencies are AMDGPU device state, ATOMBIOS table access, SMU11 driver interface headers, `smu_v11_0_*` helpers, `smu_cmn_*` helpers, Linux PCI/I2C/firmware APIs, NBIO/THM/MP register definitions, VCN/JPEG power-gating state, and firmware message/table compatibility. The file assumes `PPTable_t`, metrics structs, OD structs, and activity monitor structs match the installed PMFW interface version.

### Integration Points
The file integrates with the AMDGPU power-management core through `pptable_funcs`. It serves sysfs and ioctl-facing operations for clock levels, power profiles, fan control, sensors, thermal limits, power limits, PCIe caps, GPU metrics, and OverDrive. It integrates with display code through watermark programming and min-clock notifications, with runtime PM through BACO/ArmD3, with RAS/board services through SMU I2C adapter registration, and with firmware boot through microcode, PPTABLE, feature mask, table-location, and memory-pool callbacks delegated to common SMU11 helpers.

### Risks
The implementation is highly firmware-version-sensitive: selecting the wrong metrics layout, table size, or message availability can produce incorrect telemetry or failed SMC commands. The powerplay append path accepts only specific `smc_dpm_info` revisions, so unsupported VBIOS revisions fail initialization. `smu->od_settings` points into the parsed powerplay table rather than an independent copy, making lifetime and table-layout correctness important. Several user-facing paths intentionally return `0` after failed frequency-limit operations, which can hide unsuccessful clock forcing. The UMC workaround depends on PMFW message availability, VRAM dummy table programming, and ASIC-specific thresholds, so regressions can affect memory stability. I2C transactions rely on adapter quirks and PM mutex serialization; malformed or oversized transaction construction would map directly to SMU command slots. Some ASIC revision tables and hard-coded SKU workarounds are brittle as new board revisions appear.

### Test Signals
Useful validation includes booting Navi10, Navi12, and Navi14 boards across old and new PMFW versions; checking PPT setup with ATOM `smc_dpm_info` revisions 4.5 and 4.7; verifying sysfs clock levels and forced clock masks for discrete and fine-grained DPM; reading all supported sensors and `gpu_metrics`; exercising OD range display, SCLK/MCLK/curve edit, restore, commit, and suspend/resume retention; validating watermark programming during display hotplug and memory-clock switch disabling; testing VCN/JPEG power-gating transitions; checking BACO runtime suspend/resume with and without audio function; verifying SMU I2C adapters against FRU/RAS EEPROMs; and confirming UMC CDR workaround paths on firmware below and above the gating versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/navi10_ppt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/navi10_ppt.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/navi10_ppt.h

### Purpose
`navi10_ppt.h` is the small public header for the Navi10/Navi12/Navi14 SMU11 PowerPlay table implementation. It publishes ASIC-specific UMD pstate clock constants, the voltage scaling factor used by Navi10 OverDrive voltage curves, and the `navi10_set_ppt_funcs()` registration entry point.

### Important APIs, Types, And Functions
The header defines peak GFX clock constants for Navi10 XTX/XT/XL, Navi14 XT/XTM/XLM/XTX/XL, and Navi12. It also defines profiling pstate clocks for Navi10 and Navi14 across GFXCLK, SOCCLK, MEMCLK, VCLK, and DCLK. `NAVI10_VOLTAGE_SCALE` is used by `navi10_ppt.c` when converting between firmware OD curve voltage units and millivolts. The only function declaration is `extern void navi10_set_ppt_funcs(struct smu_context *smu);`.

### Control Flow
There is no executable control flow in the header. Its constants are consumed when `navi10_populate_umd_state_clk()` derives standard and peak UMD pstates, and the exported function is called by higher-level SMU ASIC-selection code to install Navi10 PPT behavior into `struct smu_context`.

### State, Persistence, And Dependencies
The header stores no state. Its values become part of runtime pstate and OD behavior through the C implementation. It depends on the caller including or forward-declaring `struct smu_context` in the include chain; the header itself only carries include guards and macro definitions.

### Integration Points
`navi10_ppt.c` includes this header for pstate and voltage constants. Platform dispatch code includes or references the header to call `navi10_set_ppt_funcs()` for MP1 IP versions handled by the Navi10 PPT module.

### Risks
The constants are board/ASIC policy values rather than values queried at runtime. If a future SKU uses a different UMD profiling or peak clock policy but reuses this path, user-visible pstate reporting can be misleading. The voltage scale must continue to match the firmware OD table encoding; a mismatch would display or program VDDC curve values incorrectly.

### Test Signals
Validation is mostly indirect: confirm `pp_dpm_*` and UMD pstate reporting on Navi10, Navi12, and Navi14 SKUs; verify OD VDDC curve display and writes round-trip in millivolts; and check that the ASIC dispatch path calls `navi10_set_ppt_funcs()` only for compatible SMU11 IP versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/navi10_ppt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/sienna_cichlid_ppt.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/sienna_cichlid_ppt.c

### Purpose
`sienna_cichlid_ppt.c` is the SMU11 PowerPlay table implementation for the newer SMU 11.0.7 family: Sienna Cichlid, Navy Flounder, Dimgrey Cavefish, and Beige Goby. It performs the same generic PPT role as the Navi10 implementation while adding newer firmware table formats, multi-instance media clocks, FCLK handling, SmartShift metrics, ECC export, STB collection, GPO control, second USB2 port notification, mode1/mode2 reset hooks, board-specific PPT quirks, and ASIC-specific table indirection for Beige Goby.

### Important APIs, Types, And Functions
The exported entry point is `sienna_cichlid_set_ppt_funcs()`, which installs `sienna_cichlid_ppt_funcs` plus message, clock, feature, table, power-source, and workload mappings. `GET_PPTABLE_MEMBER()` and `get_table_size()` abstract the difference between `PPTable_t` and `PPTable_beige_goby_t` for MP1 IP 11.0.13. The main mapping arrays are `sienna_cichlid_message_map`, `sienna_cichlid_clk_map`, `sienna_cichlid_feature_mask_map`, `sienna_cichlid_table_map`, `sienna_cichlid_pwr_src_map`, `sienna_cichlid_workload_map`, and `sienna_cichlid_throttler_map`.

Initialization and table management are handled by `sienna_cichlid_init_allowed_features()`, `sienna_cichlid_setup_pptable()`, `sienna_cichlid_store_powerplay_table()`, `sienna_cichlid_append_powerplay_table()`, `sienna_cichlid_patch_pptable_quirk()`, `sienna_cichlid_tables_init()`, and `sienna_cichlid_init_smc_tables()`. Runtime power APIs include `sienna_cichlid_set_default_dpm_table()`, media power-gating helpers, clock level emission/forcing, display clock notification, watermark programming, sensors, power limits, thermal ranges, PCIe cap updates, power profiles, OD editing, BACO, GPO, MP1 state, and reset callbacks.

Telemetry is provided by `sienna_cichlid_get_smu_metrics_data()`, `sienna_cichlid_get_gpu_metrics()`, `sienna_cichlid_get_smartshift_power_percentage()`, `sienna_cichlid_get_unique_id()`, and `sienna_cichlid_get_ecc_info()`. SMU I2C mirrors the Navi10 adapter pattern through `sienna_cichlid_i2c_xfer()` and `sienna_cichlid_i2c_control_init()`. STB support is initialized and read by `sienna_cichlid_stb_init()` and `sienna_cichlid_stb_get_data_direct()`.

### Control Flow
ASIC binding starts in `sienna_cichlid_set_ppt_funcs()`, which assigns driver interface versions for MP1 IP 11.0.7, 11.0.11, 11.0.12, and 11.0.13 before initializing SMU message control. PPT setup calls the common SMU11 parser, copies the embedded PMFW PPTABLE into the driver buffer using an ASIC-dependent size, appends ATOM `smc_dpm_info` board fields, checks hardware DC, BACO, and fan support, points `smu->od_settings` at board OD limits, then applies specific OEM PPT quirks to board-reserved fields or high GFX clock entries.

SMC table initialization declares firmware table buffers for PPTABLE, WATERMARKS, SMU_METRICS, I2C_COMMANDS, OVERDRIVE, PMSTATUSLOG, ACTIVITY_MONITOR_COEFF, ECCINFO, and DRIVER_SMU_CONFIG. It allocates metrics, GPU metrics cache, watermarks, ECC, and driver config memory, and initializes STB for non-SRIOV devices when firmware has enabled it. Default DPM setup fills SOC, GFX, UCLK, FCLK, VCLK0/1, DCLK0/1, DCEFCLK, display, pixel, PHY, and PCIe tables. Media clock setup loops over VCN instances and skips harvested instances.

Metrics control flow selects one of several embedded metrics layouts in `SmuMetricsExternal_t` based on ASIC and firmware version. Metrics v2 and v3 add newer fields and throttling-percentage arrays; otherwise the base metrics struct is used. SmartShift power-share percentages are computed from metrics v4 fields by comparing APU and dGPU observed socket power against normalized limits. GPU metrics conversion fills `gpu_metrics_v1_3`, including dual VCLK/DCLK fields and fallback PCIe queries for older PMFW.

Clock sysfs output covers GFX, SOC, UCLK/MCLK, FCLK, VCLK/VCLK1, DCLK/DCLK1, DCEFCLK, PCIE, and OD views. OD support differs from Navi10: SCLK and UCLK have min/max limit editing, and newer firmware exposes a GFX voltage offset instead of the older three-point VDDC curve. `sienna_cichlid_set_default_od_settings()` refreshes boot/live OD tables on resume but preserves user OD fields if `user_od` is active. `sienna_cichlid_restore_user_od_settings()` restores common SMU OD state and mirrors user values back to the live table.

System feature enablement first notifies PMFW about the second USB2 port on firmware 58.45.0 and later, then delegates to common SMU feature control. Reset support checks SRIOV status, PMFW version, and PSP liveness before allowing mode1 reset; mode2 reset sends an async PMFW reset message, waits for ACK with retries, and reloads saved PCI config space. STB collection reads MP1 PMI registers under a spinlock into a caller buffer. ECC export checks minimum PMFW version 58.70.0, fetches `SMU_TABLE_ECCINFO`, and copies per-channel ECC fields into UMC RAS structures.

### State, Persistence, And Dependencies
Runtime state is spread across `struct smu_context`, `smu_table`, `smu_dpm`, `stb_context`, `smu_baco`, `user_dpm_profile`, `custom_profile_params`, and AMDGPU device fields such as `pm.no_fan`, I2C bus pointers, unique ID, VCN harvest information, and firmware capabilities. Firmware-facing persistent state is written through SMU tables in VRAM and SMC messages. The driver keeps CPU mirrors of metrics, watermarks, ECC info, OD, user OD, boot OD, and driver config tables.

The implementation depends on SMU 11.0.7 driver interface headers, the SMU 11.0.7 PPTABLE and PPSMC definitions, ATOMBIOS `smc_dpm_info`, `smu_v11_0_*` and `smu_cmn_*` helpers, AMDGPU RAS structures, Linux I2C infrastructure, PCI config save/restore, MP/NBIO/THM register definitions, and exact PMFW version gates. Beige Goby support depends on `GET_PPTABLE_MEMBER()` being used consistently for every field whose offset differs from the normal table.

### Integration Points
The vtable integrates this ASIC family with generic AMDGPU power management. It exposes user-visible clock, power, fan, thermal, sensor, OD, GPU metrics, ECC, reset, and STB operations. It integrates with display code through watermark and min-clock paths, with media blocks through per-instance VCN/JPEG power messages, with platform firmware through ATOM PPTABLE fields and firmware caps, with RAS through ECC info and SMU I2C EEPROM buses, and with runtime PM through BACO and MP1 state transitions.

### Risks
This file has many firmware-version gates, so telemetry, OD voltage offset, unique ID, ECC, USB2 notification, PCIe metrics, and reset support can fail or silently degrade if version checks are wrong. The `GET_PPTABLE_MEMBER()` macro is critical for Beige Goby; direct `PPTable_t` field access in a future edit would risk corrupt reads or writes on IP 11.0.13. Board-specific PPT patches are intentionally narrow but brittle. `sienna_cichlid_force_clk_levels()` returns success after internal errors, which can hide failed force-clock requests. Metrics v3 throttling converts percentages to bit presence, which changes semantics from raw status fields. The I2C path and STB register reads need serialization discipline to avoid conflicting firmware or interrupt access. Mode2 reset manually waits for PMFW response and restores PCI config, so timeout handling and saved-state validity are important.

### Test Signals
High-value testing covers all supported MP1 IP versions, including Beige Goby table-size and member access; firmware before and after each metrics, OD, unique ID, ECC, USB2, and reset threshold; VCN harvested and dual-instance media configurations; sysfs clock emission for FCLK and VCLK/DCLK instance clocks; OD SCLK/UCLK min/max, voltage offset, restore, commit, and suspend/resume retention; SmartShift sensor output on non-11.0.7 ASICs; ECC table export and unsupported-version behavior; STB enablement and collection; mode1 and mode2 reset paths; GPO enable/disable behavior across 58.37.0 gating; and I2C EEPROM bus assignment for RAS and FRU devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/sienna_cichlid_ppt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/sienna_cichlid_ppt.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/sienna_cichlid_ppt.h

### Purpose
`sienna_cichlid_ppt.h` is the public header for the Sienna Cichlid-family SMU11 PowerPlay table implementation. It defines a small AC/DC power-source enum, ASIC-family UMD profiling clock constants, and the `sienna_cichlid_set_ppt_funcs()` registration entry point.

### Important APIs, Types, And Functions
`POWER_SOURCE_e` declares `POWER_SOURCE_AC`, `POWER_SOURCE_DC`, and `POWER_SOURCE_COUNT`. The profiling constants define standard UMD pstate GFXCLK, SOCCLK, and MEMCLK values for Sienna Cichlid/Navy Flounder, Dimgrey Cavefish, and Beige Goby. The header declares `extern void sienna_cichlid_set_ppt_funcs(struct smu_context *smu);`.

### Control Flow
The header has no executable control flow. Its constants are consumed by `sienna_cichlid_populate_umd_state_clk()`, which chooses standard UMD pstate clocks based on MP1 IP version. The function declaration is used by ASIC dispatch code to install the Sienna Cichlid PPT vtable and mappings into the active SMU context.

### State, Persistence, And Dependencies
The header stores no runtime state. The enum and constants become runtime policy only when the C implementation uses them to populate `smu->pstate_table` or map power-source behavior. The header assumes `struct smu_context` is available through the including compilation unit and uses normal include guards.

### Integration Points
`sienna_cichlid_ppt.c` includes this header for UMD profiling constants and the local entrypoint declaration. Higher-level SMU initialization uses `sienna_cichlid_set_ppt_funcs()` for MP1 IP versions 11.0.7, 11.0.11, 11.0.12, and 11.0.13.

### Risks
The profiling constants are static policy. If a new board or firmware changes recommended UMD standard clocks while staying on this implementation path, reported or selected standard pstates may not match the hardware's desired policy. The local `POWER_SOURCE_e` overlaps conceptually with common SMU power-source mappings, so edits should avoid introducing enum-value drift against firmware expectations.

### Test Signals
Indirect validation should check UMD pstate standard clocks on each supported ASIC family, verify AC/DC power-source notifications still map correctly through the common-to-ASIC map, and confirm ASIC dispatch invokes `sienna_cichlid_set_ppt_funcs()` only for compatible SMU11 IP versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/sienna_cichlid_ppt.h -->
