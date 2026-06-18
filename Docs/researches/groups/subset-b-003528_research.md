# subset-b-003528 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/fiji_smumgr.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/fiji_smumgr.c

### Purpose
`fiji_smumgr.c` is the Fiji ASIC implementation of the AMD PowerPlay SMU manager. It allocates Fiji SMU backend state, starts the SMU firmware, parses firmware-resident table addresses, builds SMU73 discrete DPM/ULV/power-tune/fan/thermal tables from VBIOS and PowerPlay tables, uploads those structures into SMC SRAM, and exposes the Fiji-specific `pp_smumgr_func` vtable used by the common power-management stack.

### Important APIs, Types, And Functions
The exported integration object is `fiji_smu_funcs`, which wires `.smu_init`, `.start_smu`, `.process_firmware_header`, `.init_smc_table`, `.update_smc_table`, `.update_sclk_threshold`, `.thermal_setup_fan_table`, `.thermal_avfs_enable`, `.populate_all_graphic_levels`, `.populate_all_memory_levels`, `.initialize_mc_reg_table`, `.is_hw_avfs_present`, and `.update_dpm_settings` into the common SMU manager. `fiji_smu_init()` allocates `struct fiji_smumgr` and delegates common initialization to `smu7_init()`.

Startup is split between `fiji_start_smu_in_protection_mode()`, `fiji_start_smu_in_non_protection_mode()`, `fiji_start_smu()`, `fiji_is_hw_avfs_present()`, `fiji_avfs_event_mgr()`, and `fiji_start_avfs_btc()`. DPM table construction is driven by `fiji_init_smc_table()`, with helpers for voltage/CAC data (`fiji_get_dependency_volt_by_clk()`, `fiji_populate_cac_table()`), graphics levels (`fiji_calculate_sclk_params()`, `fiji_populate_single_graphic_level()`, `fiji_populate_all_graphic_levels()`), memory levels (`fiji_calculate_mclk_params()`, `fiji_populate_single_memory_level()`, `fiji_populate_all_memory_levels()`), ACPI and multimedia levels (`fiji_populate_smc_acpi_level()`, `fiji_populate_smc_uvd_level()`, `fiji_populate_smc_vce_level()`, `fiji_populate_smc_acp_level()`), boot state (`fiji_populate_smc_boot_level()`, `fiji_populate_smc_initailial_state()`), clock stretching (`fiji_populate_clock_stretcher_data_table()`), VR configuration (`fiji_populate_vr_config()`), PM fuses (`fiji_populate_pm_fuses()` and subhelpers), and BAPM/fan data (`fiji_populate_bapm_parameters_in_dpm_table()`, `fiji_thermal_setup_fan_table()`).

### Control Flow
Initialization starts when the common hardware manager calls `fiji_smu_funcs.smu_init`, which stores a zeroed `struct fiji_smumgr` in `hwmgr->smu_backend` and initializes SMU7 common state. `fiji_start_smu()` only uploads and starts firmware when SMC RAM is not already running and the device is not a VF. It chooses protected versus non-protected boot using the `SMU_FIRMWARE.SMU_MODE` field, waits for firmware interrupt readiness, triggers Fiji AVFS setup if supported, reads the soft-register base from the firmware header location as an early fallback, and then requests the SMU to load remaining firmware through `smu7_request_smu_load_fw()`.

`fiji_process_firmware_header()` later reads SMU73 firmware-header fields from SMC SRAM and persists DPM table, soft-register, MC register table, fan table, MC arbitration timing table, and SMC version addresses into `smu7_data` and `hwmgr->microcode_version_info`. `fiji_init_smc_table()` then constructs the resident SMU table in a fixed order: power-tune defaults, CAC voltage lookup, system flags, ULV, PCIe link levels, graphics levels, memory levels, ACPI level, VCE/ACP/UVD multimedia levels, memory timing arbitration data, boot levels, BAPM parameters, optional clock-stretcher tables, voltage/thermal intervals, VR/GPIO settings, endian conversion, full DPM table upload, arbitration-index update, PM-fuse upload, and LED configuration.

Runtime updates are narrower. `fiji_update_smc_table()` updates UVD or VCE boot levels and enabled masks. `fiji_update_sclk_threshold()` writes `LowSclkInterruptThreshold` and, when overdrive changed SCLK or MCLK, refreshes memory timing parameters. `fiji_update_dpm_settings()` freezes SCLK/MCLK DPM levels, patches per-level activity and hysteresis fields in both cached driver state and SMC SRAM with read-modify-write helpers, and unfreezes the levels.

### State, Persistence, And Dependencies
Persistent driver state is held in `struct fiji_smumgr`: common `smu7_smumgr` addresses/status, `SMU73_Discrete_DpmTable smc_state_table`, `SMU73_Discrete_Ulv`, `SMU73_Discrete_PmFuses`, and the selected `fiji_pt_defaults`. This state is mirrored into SMC SRAM through `smu7_copy_bytes_to_smc()`, `smu7_write_smc_sram_dword()`, and indirect SMC register writes. The source data comes from `hwmgr->pptable`, `hwmgr->dyn_state`, `struct smu7_hwmgr`, VBIOS atom-control queries, display configuration, thermal controller settings, device registers, and SMU firmware header offsets.

The file depends heavily on SMU73 layout headers (`smu73.h`, `smu73_discrete.h`, `fiji_ppsmc.h`), SMU7 common helpers (`smu7_*`, `smum_send_msg_to_smc*`), AtomBIOS helpers (`atomctrl_get_*`), CGS register access, endian conversion macros, and PowerPlay capability bits. Hardware state is not abstracted away: many helpers program or sample SMC, GFX, GMC, DCE, BIF, and thermal registers directly.

### Integration Points
The function table at the end is the contract consumed by the PowerPlay SMU manager dispatcher. It reuses common SMU7 firmware messaging and teardown but overrides Fiji-specific table construction and runtime updates. AVFS integrates with efuse reads, power-virus setup, BTC SMC messages, and the `thermal_avfs_enable` hook. Fan control integrates with the thermal controller and SMC fan table address. Multimedia DPM integration uses UVD/VCE table update hooks and PPSMC enabled-mask messages. The `get_offsetof()` and `get_mac_definition()` helpers provide SMU73 layout metadata to generic code that addresses soft registers or table members symbolically.

### Risks
Several paths assume PowerPlay/VBIOS tables contain enough entries; for example graphics and memory level builders write `levels[0]` and highest-level watermarks after looping over DPM counts. PM-fuse and DPM-table uploads rely on exact SMU73 struct layout and endian conversion; missing a conversion can silently corrupt SMC interpretation. `fiji_get_dependency_volt_by_clk()` has suspicious fallback indexing in the beyond-max-clock path where it uses `entries[i]` after the loop in some VDDCI/MVDD branches, which should be reviewed if this source is made live. Fan-table slope calculation divides by temperature deltas that must not be zero. Clock-stretcher setup is tightly coupled to efuse interpretation and hard-coded lookup tables, so unsupported PPTable stretch amounts disable the capability and fail initialization. Direct register programming and SMC SRAM read-modify-write operations are sensitive to alignment, concurrent SMU activity, and VF/non-VF behavior.

### Test Signals
Useful signals include SMU boot success in protected and non-protected modes, firmware-header address parsing, DPM table upload success, SCLK/MCLK DPM level counts and enable masks matching PPTable inputs, boot-level matching to VBIOS boot clocks, UVD/VCE boot mask updates under stable and non-stable P-state modes, AVFS enable/disable behavior based on efuse and BTC failure, fan-control capability fallback when no fan/table/FDO duty exists, endian-correct table contents in SMC SRAM, overdrive-triggered memory timing refreshes, and DPM-running detection via `FEATURE_STATUS.VOLTAGE_CONTROLLER_ON`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/fiji_smumgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/fiji_smumgr.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/fiji_smumgr.h

### Purpose
`fiji_smumgr.h` declares the Fiji-specific SMU manager private data used by `fiji_smumgr.c`. It binds common SMU7 manager state to the SMU73 discrete table layouts required by Fiji firmware.

### Important APIs, Types, And Functions
`struct fiji_pt_defaults` defines default PowerTune fields used to seed the SMU PM-fuse and DPM tables: SVI load-line enable/value, TDC throttle release, TDC MAW time, TDC waterfall control, and DTE ambient temperature base. `struct fiji_smumgr` is the private backend stored in `pp_hwmgr.smu_backend`; it embeds `struct smu7_smumgr`, an `SMU73_Discrete_DpmTable`, an `SMU73_Discrete_Ulv`, an `SMU73_Discrete_PmFuses`, and a pointer to the selected defaults.

### Control Flow
The header itself has no executable control flow. At runtime `fiji_smu_init()` allocates this structure, helper functions fill its DPM/ULV/PM-fuse members, and upload paths copy those members into SMC SRAM. The defaults pointer is selected during SMC table initialization before PM-fuse and BAPM population.

### State, Persistence, And Dependencies
The declared state is in-memory driver state that persists for the lifetime of the hardware manager backend and is released by the common SMU7 finalizer. It depends on `smu73_discrete.h` for firmware-visible table types, `smu7_smumgr.h` for common SMU7 state, and `pp_endian.h` for host/SMC conversion macros used by the implementation.

### Integration Points
This header is included by `fiji_smumgr.c` and is part of the ASIC-specific PowerPlay SMU manager boundary. Generic code sees the backend through `pp_smumgr_func`; Fiji-specific code casts `hwmgr->smu_backend` back to `struct fiji_smumgr` to access cached table addresses and SMU73 table instances.

### Risks
The structure layout must remain consistent with implementation casts and common-finalizer expectations: `smu7_data` is the first member, allowing common SMU7 code to treat the backend as `struct smu7_smumgr`. The firmware-visible table members are large and layout-sensitive; changing their types or conversion assumptions would break SMC uploads.

### Test Signals
Build coverage should catch missing SMU73 type definitions and include-order regressions. Runtime signals include successful allocation, common SMU7 initialization, SMC table population without NULL defaults, and correct common cleanup through the embedded first-member `smu7_data`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/fiji_smumgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/iceland_smumgr.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/iceland_smumgr.c

### Purpose
`iceland_smumgr.c` is the Iceland ASIC implementation of the AMD PowerPlay SMU manager. It provides SMU71 firmware upload/startup, builds and uploads SMU71 DPM/ULV/power-tune/fan tables, maintains a VBIOS-derived memory-controller register table for MCLK levels, and exposes Iceland-specific operations through `iceland_smu_funcs`.

### Important APIs, Types, And Functions
The exported integration object is `iceland_smu_funcs`, with hooks for SMU init/start, firmware-load checks/requests, specific firmware load requests, SMC messaging, firmware-header processing, SMC table initialization, SCLK threshold updates, fan table setup, graphics/memory level population, MC register table initialization, DPM-running checks, and SMU71 layout metadata.

SMU boot is handled by `iceland_smu_upload_firmware_image()`, `iceland_upload_smc_firmware_data()`, `iceland_smu_start_smc()`, and `iceland_start_smu()`. Main table construction is coordinated by `iceland_init_smc_table()`. Supporting helpers populate default power-tune data by PCI device ID (`iceland_initialize_power_tune_defaults()`), PM fuses (`iceland_populate_pm_fuses()` and subhelpers), voltage tables (`iceland_populate_smc_voltage_tables()`), graphics levels (`iceland_calculate_sclk_params()`, `iceland_populate_single_graphic_level()`, `iceland_populate_all_graphic_levels()`), memory levels (`iceland_calculate_mclk_params()`, `iceland_populate_single_memory_level()`, `iceland_populate_all_memory_levels()`), ACPI state, boot state, BAPM parameters, SVI2 configuration, and fan tables. MC register handling is a major subsystem: `iceland_initialize_mc_reg_table()`, `iceland_copy_vbios_smc_reg_table()`, `iceland_set_s0_mc_reg_index()`, `iceland_set_mc_special_registers()`, `iceland_set_valid_flag()`, `iceland_populate_initial_mc_reg_table()`, `iceland_update_and_upload_mc_reg_table()`, and conversion helpers transform AtomBIOS MC tables into SMU71 `MCRegisters`.

### Control Flow
`iceland_smu_init()` allocates `struct iceland_smumgr`, stores it as `hwmgr->smu_backend`, and runs `smu7_init()`. `iceland_start_smu()` uploads SMU firmware if SMC RAM is not already running, starts the SMC by programming jump-on-start, enabling its clock, deasserting reset, and waiting for interrupt readiness, then reads `SoftRegisters` from the SMU71 firmware header and asks SMU7 common code to load remaining firmware.

`iceland_process_firmware_header()` reads DPM table, soft-register, MC register table, fan table, arbitration table, firmware version, and ULV settings offsets from the SMU71 firmware header into the embedded common state. `iceland_initialize_mc_reg_table()` separately prepares driver-side MC register data by copying low-power register shadows from live registers, asking AtomBIOS for the MC timing table for the active memory module, deriving S0 low-power register indices, adding special PMG command registers, and marking only registers whose values vary across timing entries as valid.

`iceland_init_smc_table()` zeros the SMU71 DPM table and then populates power/voltage/system flags, optional ULV, PCIe link levels, graphics levels, memory levels, ACPI state, placeholder VCE/ACP/UVD levels, memory arbitration timings, boot levels, BAPM thermal/power parameters, thermal and interval fields, SVI2 configuration, endian conversions, main DPM table upload, ULV upload, initial MC register table upload, and PM-fuse upload. Runtime `iceland_update_sclk_threshold()` writes the low-SCLK interrupt threshold when enabled, refreshes and uploads MC register data when MCLK overdrive changed, and refreshes memory timing parameters for SCLK or MCLK changes.

### State, Persistence, And Dependencies
The persistent backend state is `struct iceland_smumgr`: embedded `smu7_smumgr`, cached `SMU71_Discrete_DpmTable`, `SMU71_Discrete_PmFuses`, `SMU71_Discrete_Ulv`, selected default pointer, converted `SMU71_Discrete_MCRegisters`, and a driver-format `iceland_mc_reg_table`. Firmware-visible state is persisted into SMC SRAM through `smu7_copy_bytes_to_smc()` and indirect register writes. Driver-side MC register data persists so later MCLK table updates can regenerate only the SMC MC register sets without rereading the full VBIOS table.

Dependencies include Linux kernel allocation and PCI/device types, SMU7 common helpers, SMU71 layout headers and PPSMC messages, AtomBIOS/PPTable processing, CGS register access, endian conversion macros, PowerPlay capability bits, and many GMC/BIF/DCE/SMU register definitions. Unlike Fiji, Iceland has a local firmware upload path that uses `cgs_get_firmware_info()` and writes the SMC image through `mmSMC_IND_INDEX_0` / `mmSMC_IND_DATA_0` with auto-increment.

### Integration Points
`iceland_smu_funcs` is consumed by the common SMU manager dispatcher for Iceland devices. Device IDs `0x6900` through `0x6903` select XT/PRO/default PowerTune profiles. The firmware upload path integrates with CGS firmware management. Voltage, clock, and memory timing helpers integrate with AtomBIOS clock-divider and MC-table services. The MC register subsystem bridges AtomBIOS VRAMInfo data and firmware-side SMU71 MC registers. The fan setup hook writes an SMU fan table from the thermal controller. `get_offsetof()` and `get_mac_definition()` expose SMU71 layout constants to generic code.

### Risks
The local firmware upload ignores the return value from `iceland_upload_smc_firmware_data()`, so an upload failure after size/alignment checks would not be propagated. `iceland_populate_smc_voltage_table()` appears to convert `StdVoltageHiSidd` twice and never converts `StdVoltageLoSidd`, which is a likely endian bug. `iceland_populate_smc_mvdd_table()` loops to `table->VddciLevelCount` while filling MVDD levels, which should be checked against `MvddLevelCount`. `iceland_populate_all_graphic_levels()` writes `GraphicsLevel[1]` for the mid PCIe level even if only one SCLK level exists, despite guarding only the high watermark. SVI2 assertions encode board assumptions and can fail initialization for unexpected voltage-controller combinations. MC table expansion must stay within `SMU71_DISCRETE_MC_REGISTER_ARRAY_SIZE`; the code asserts but uses compact bit masks that would overflow if table sizes exceeded mask width. Fan slope calculation depends on nonzero temperature deltas.

### Test Signals
High-value signals include firmware image size/alignment validation, SMC boot interrupt readiness, firmware-header offset parsing including `UlvSettings`, device-ID-specific default selection, voltage-table endian validation, SVI2 domain configuration, graphics/memory DPM level counts and enable masks, GDDR5 versus DDR3 memory-level ratio/strobe/EDC behavior, MC register table initialization from VBIOS for multiple memory modules, validflag filtering of unchanged registers, overdrive MCLK updates uploading MC register sets, thermal fan table upload and no-fan fallback, PM-fuse upload under `PHM_PlatformCaps_PowerContainment`, and DPM-running detection via `FEATURE_STATUS.VOLTAGE_CONTROLLER_ON`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/iceland_smumgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/iceland_smumgr.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/iceland_smumgr.h

### Purpose
`iceland_smumgr.h` declares the Iceland-specific SMU manager backend and memory-controller register table types used by `iceland_smumgr.c`. It ties common SMU7 manager state to SMU71 firmware-visible DPM, ULV, PM-fuse, and MC-register structures.

### Important APIs, Types, And Functions
`struct iceland_pt_defaults` stores PowerTune defaults and BAPM thermal model constants: SVI load-line settings, TDC fields, DTE ambient base, display CAC, BAPM temperature gradient, and flattened BAPMTI R/RC arrays sized by SMU71 DTE dimensions. `struct iceland_mc_reg_entry` stores one maximum-MCLK timing entry and its MC register values. `struct iceland_mc_reg_table` stores the driver-side MC table copied and expanded from AtomBIOS: count fields, a valid-bit mask, timing entries, and S0/S1 MC register addresses. `struct iceland_smumgr` embeds common `smu7_smumgr`, SMU71 DPM/PM-fuse/ULV state, selected defaults, converted SMU71 MC registers, and the driver-format MC register table.

### Control Flow
This header has no executable control flow. `iceland_smu_init()` allocates `struct iceland_smumgr`; initialization helpers fill the DPM, PM-fuse, ULV, and MC table members; `iceland_init_smc_table()` and MC update helpers upload those cached members into SMC SRAM. The defaults pointer is assigned based on PCI device ID before BAPM and PM-fuse population.

### State, Persistence, And Dependencies
The declared structures persist as the SMU backend for the lifetime of the hardware manager. `mc_reg_table` is driver-format state retained so later MCLK DPM changes can regenerate `mc_regs` for the SMU without repeating all AtomBIOS parsing. The header depends on `smu7_smumgr.h`, `pp_endian.h`, and `smu71_discrete.h` for common state, conversion helpers, table sizes, and firmware-visible structures.

### Integration Points
`iceland_smumgr.c` includes this header and casts `hwmgr->smu_backend` to `struct iceland_smumgr` throughout. The embedded first member allows common SMU7 routines to operate on the backend as `struct smu7_smumgr`. MC register types are the handoff between AtomBIOS MC register tables and SMU71 `SMU71_Discrete_MCRegisters` upload format.

### Risks
The `validflag` field is a 16-bit mask but `SMU71_DISCRETE_MC_REGISTER_ARRAY_SIZE` can drive loops over more entries if definitions change, so size assumptions must stay aligned. The embedded-first-member pattern is important for common cleanup and address access. BAPMTI arrays must match SMU71 DTE constants exactly or defaults will be copied incorrectly into the firmware table.

### Test Signals
Build tests should catch mismatched SMU71 constants and missing type declarations. Runtime signals include successful backend allocation, correct device-default selection, MC register table bounds validation, validflag generation, SMC MC register upload sizes, and common SMU7 finalization working through the embedded `smu7_data`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/iceland_smumgr.h -->
