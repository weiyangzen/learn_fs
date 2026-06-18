# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/ci_smumgr.c

## Purpose

`ci_smumgr.c` implements the CI/Sea Islands SMU manager backend for AMDGPU PowerPlay. It loads SMU firmware, discovers firmware table offsets, constructs SMU7 discrete DPM, voltage, fan, memory-controller, memory-timing, and power-tune tables, uploads those tables into SMC SRAM, sends SMC messages, updates runtime DPM settings, and stops/resets the SMC.

The exported integration point is `ci_smu_funcs`, a `pp_smumgr_func` table wired into the generic `smumgr.h` façade.

## Important APIs, functions, and data

The file defines device-specific `ci_pt_defaults` for Hawaii XT/PRO, Bonaire XT, and Saturn XT. These defaults seed SVI load-line, TDC, DTE, BAPM gradient, and thermal RC table fields.

Low-level SMC access helpers include `ci_set_smc_sram_address`, `ci_copy_bytes_to_smc`, `ci_read_smc_sram_dword`, `ci_program_jump_on_start`, `ci_is_smc_ram_running`, `ci_send_msg_to_smc`, and `ci_send_msg_to_smc_with_parameter`. They access SMC indirect registers, copy big-endian words into SRAM, poll responses, and manage SMC start state.

Clock/DPM population functions include `ci_calculate_sclk_params`, `ci_populate_single_graphic_level`, `ci_populate_all_graphic_levels`, `ci_calculate_mclk_params`, `ci_populate_single_memory_level`, `ci_populate_all_memory_levels`, `ci_populate_smc_link_level`, `ci_populate_smc_acpi_level`, `ci_populate_smc_uvd_level`, `ci_populate_smc_vce_level`, and `ci_populate_smc_acp_level`.

Voltage and PowerTune functions include `ci_get_dependency_volt_by_clk`, `ci_populate_smc_voltage_table`, VDDC/VDDCI/MVDD table population, ULV population, PM fuse population, BAPM parameter setup, leakage/SIDD helpers, SVI2/VR config, and PowerTune default selection.

Memory-controller support includes `ci_program_memory_timing_parameters`, `ci_initialize_mc_reg_table`, VBIOS MC table copy/translation, LP register initialization, valid-flag detection, and update/upload paths for overdrive MCLK changes.

Runtime update functions include `ci_update_sclk_threshold`, `ci_update_dpm_settings`, `ci_update_uvd_smc_table`, `ci_update_vce_smc_table`, `ci_update_smc_table`, `ci_thermal_setup_fan_table`, and offset/max query helpers.

Lifecycle functions include `ci_upload_firmware`, `ci_process_firmware_header`, `ci_init_smc_table`, `ci_smu_init`, `ci_smu_fini`, `ci_is_dpm_running`, `ci_reset_smc`, `ci_stop_smc_clock`, and `ci_stop_smc`.

## Control flow

Initialization allocates a `struct ci_smumgr` in `ci_smu_init`. Firmware processing then calls `ci_upload_firmware` if the SMC is not already running, resets/disables the SMC clock as needed, loads the firmware image into SRAM, and reads firmware header offsets for the DPM table, soft registers, MC register table, fan table, ARB timing table, and version.

`ci_init_smc_table` is the main table-construction flow. It selects PowerTune defaults, clears the cached DPM table, populates voltage tables, sets platform flags, builds ULV state, uploads graphics and memory levels, fills PCIe link, ACPI, VCE, ACP, UVD, memory timing, boot levels, initial state, BAPM, intervals, thermal limits, PCIe boot level, VR/SVI2 config, GPIOs, endian-converts scalar fields, uploads the DPM table to SRAM, initializes MC registers, uploads PM fuses, and finally starts the SMC.

Runtime profile updates freeze SCLK or MCLK DPM if enabled, patch activity/hysteresis fields directly in SMC SRAM at field offsets, and then unfreeze the DPM level. UVD/VCE table updates recalculate enable masks based on AC/DC voltage ceilings and forced-profile modes, then send SMC mask messages.

## State and persistence behavior

State is split between `hwmgr->backend` (`smu7_hwmgr` policy and DPM data), `hwmgr->smu_backend` (`ci_smumgr` cached SMU tables and firmware offsets), SMC SRAM, hardware registers, VBIOS-derived tables, and firmware runtime state. Cached tables persist until `ci_smu_fini` frees `smu_backend`, but firmware SRAM state persists independently until reset, stop, or reupload.

Many fields are endian-converted before upload because SMC firmware expects big-endian table encoding. The memory-controller table is derived from VBIOS timing data and current hardware LP registers, with only registers whose values vary across memory timing entries marked valid.

## Dependencies and integration points

The implementation depends on Linux kernel allocation/delay/types, CGS register access, AMDGPU device and PCI IDs, SMU7 table definitions, PowerPlay hardware manager state, VBIOS/ATOM control helpers, generated register headers, PCIe lane encoding, and firmware lookup through `cgs_get_firmware_info`.

It integrates upward through `ci_smu_funcs` and generic `smumgr` wrappers. It integrates downward with SMC indirect registers, SMC firmware headers, memory controller registers, clock PLL divider queries, thermal controller parameters, platform capability flags, and SMC messages from `ppsmc.h`.

## Risks

Several helpers trust table counts and firmware offsets after limited validation. Bad VBIOS dependency tables, zero clock entries, oversized MC tables, or stale firmware offsets can fail initialization or write invalid SRAM contents. The code uses many direct unit conversions and endian conversions; missing one can corrupt firmware policy.

`ci_send_msg_to_smc` logs a non-OK response but still returns `0`, so callers may treat rejected or failed firmware commands as success. Some update paths ignore return values from `smum_send_msg_to_smc*`. Direct SMC SRAM patching in `ci_update_dpm_settings` depends on exact structure offsets and field widths.

The firmware copy path rejects images larger than SMC RAM and requires a 4-byte-multiple size, but address-plus-size validation is otherwise simple. Partial-byte copy logic in `ci_copy_bytes_to_smc` preserves low bytes from the existing word, so callers must understand the byte ordering.

## Test signals

Build tests should compile the CI manager and all referenced SMU7 structures/registers. Runtime tests need CI-family hardware boot, firmware header parsing, DPM table upload, SMC start, DPM-running detection, graphics/memory level enumeration, UVD/VCE/ACP transitions, fan table upload, thermal throttling, AC/DC and PCIe behavior, suspend/resume, and driver unload/reset.

Good debug signals include no invalid SMC address messages, no firmware load size errors, no failed ATOM divider queries, no PM fuse/MC table upload failures, stable DPM masks, correct fan response, and absence of SMC unknown/failed message logs during supported flows.
