# Research: subset-b-003529

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/polaris10_smumgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/polaris10_smumgr.c

## Purpose
This file is the Polaris10/11/12 SMU manager backend for the legacy AMD PowerPlay stack. It specializes the generic `pp_smumgr_func` interface for SMU7-family discrete GPUs using the SMU74 firmware layout. Its main job is to start the SMC firmware, discover firmware-provided table offsets, build the SMU DPM table, populate AVFS and PowerTune data, write those tables into SMC SRAM, and provide runtime update hooks for fan control, AVFS enablement, DPM thresholds, multimedia boot levels, BIF clocks, and profile hysteresis.

## Important APIs, types, and functions
The exported integration point is `polaris10_smu_funcs`, which wires Polaris-specific callbacks into `struct pp_hwmgr`: `polaris10_smu_init`, `polaris10_start_smu`, `polaris10_process_firmware_header`, `polaris10_init_smc_table`, `polaris10_populate_all_graphic_levels`, `polaris10_populate_all_memory_levels`, `polaris10_update_smc_table`, `polaris10_thermal_avfs_enable`, `polaris10_thermal_setup_fan_table`, `polaris10_update_sclk_threshold`, `polaris10_initialize_mc_reg_table`, `polaris10_is_dpm_running`, `polaris10_is_hw_avfs_present`, and `polaris10_update_dpm_settings`. It reuses SMU7 primitives for message passing, SMC SRAM reads/writes, firmware upload, firmware-load completion, and teardown.

The central persistent object is `struct polaris10_smumgr` from the header. Its `smu7_data` subobject stores SMC firmware offsets and BOs inherited from SMU7. `smc_state_table` is the host-side mirror of the SMU74 DPM table. `power_tune_table`, `ulv_setting`, `range_table`, `bif_sclk_table`, and `mc_reg_table` hold derived state used to populate SMC SRAM. Static default data includes `polaris10_power_tune_data_set_array`, fallback SCLK FCW `Range_Table`, and AVFS bootstrap graphics/memory levels.

## Control flow
Initialization allocates `struct polaris10_smumgr`, stores it in `hwmgr->smu_backend`, and delegates BO setup to `smu7_init`. Starting the SMU first checks whether SMC RAM is already running. On physical functions it reads firmware mode/security fields, chooses protected or non-protected startup, uploads the SMU image, waits for interrupt enable/status bits, and then runs `polaris10_avfs_event_mgr` when AVFS is supported. Regardless of the startup path, it reads the soft-register base from the firmware header and calls `smu7_request_smu_load_fw` to ask the SMU to load the other GPU microcodes through the SMU7 TOC path.

`polaris10_process_firmware_header` is the required bridge between firmware layout and later table writes. It reads SMC SRAM header fields for the DPM table, soft registers, MC register table, fan table, MC arbitration timing table, and firmware version. `polaris10_init_smc_table` then builds the DPM table in a fixed sequence: initialize PowerTune defaults, voltage/CAC tables, system flags, ULV, PCIe link levels, graphics levels, memory levels, ACPI level, VCE/SAMU/UVD levels, memory timing tables, boot levels, BAPM/zero-RPM, clock stretcher, AVFS parameters, VR configuration, GPIO assignments, BIF SCLK dividers, endian conversion, bulk upload to SMC SRAM, and PM fuse upload.

Graphics level population derives SCLK PLL settings from ATOMBIOS when available, otherwise from the fallback FCW range table. It maps voltage dependencies, deep-sleep dividers, activity thresholds, hysteresis, PCIe DPM level selection, enabled masks, and optional SPLL shutdown programming before copying the full graphics array into SMC memory. Memory level population maps MCLK voltage dependencies, MVDD, stutter support, display watermark, enabled masks, and the memory array copy. Runtime update functions patch selected fields in SMC SRAM directly, using word-aligned read/modify/write for byte and halfword fields.

## State and persistence behavior
This backend persists derived state in two places: host memory under `hwmgr->smu_backend` and firmware-visible SRAM/VRAM. The host copy of `SMU74_Discrete_DpmTable` remains authoritative for later runtime edits, but many fields are copied into SMC SRAM immediately. Firmware-header offsets such as `dpm_table_start`, `soft_regs_start`, `fan_table_start`, and `arb_table_start` are required for later writes. The PM fuse table is read, partially overwritten with defaults and PPTable-derived values, then copied back to SMC SRAM. AVFS data is copied both into the DPM table and into firmware-header-referenced AVFS side tables. Fan control writes an `SMU74_Discrete_FanTable` to the firmware fan-table offset and sends optional minimum PWM/SCLK target messages.

## Dependencies and integration points
The file depends heavily on SMU7 helper functions, SMU74 firmware structures, ATOMBIOS helpers (`atomctrl_get_*`), PowerPlay tables (`phm_ppt_v1_information`), thermal controller data, platform capability bits, CGS register accessors, and ASIC ID macros. It integrates upward through `hwmgr.c`, which selects `polaris10_smu_funcs` for supported Polaris ASICs, and sideways with SMU7 hwmgr/powertune/clockpowergating code through generic `smum_*` wrappers and shared soft-register offsets.

## Risks and edge cases
Several SMU message helpers used here return success even when firmware response registers indicate unsupported or failed messages, so higher layers may miss firmware-side failures. `polaris10_get_dependency_volt_by_clk` has suspicious fallback paths that reference `dep_table->entries[i]` after the search loop has ended with `i == count` in some branches, which is an out-of-bounds risk if those branches execute. Many routines assume PPTable dependency tables and firmware offsets are populated and coherent; malformed VBIOS tables can cause invalid level counts, bad voltage lookup indexes, divide-by-zero in fan slope calculations, or invalid SMC writes. Endianness conversion is manual and broad, making double-conversion or missed-conversion bugs plausible. Runtime DPM profile updates patch packed SMC fields by computed offsets, so structure layout drift would be dangerous.

## Test signals
Useful validation signals are successful driver boot with no SMU firmware load errors, nonzero firmware-header offsets after `process_firmware_header`, DPM enabled status via `FEATURE_STATUS.VOLTAGE_CONTROLLER_ON`, correct SCLK/MCLK DPM masks and level counts, stable fan control when microcode fan control is enabled, AVFS enable messages succeeding on AVFS-capable boards, suspend/resume and SR-IOV paths where applicable, and stress tests that exercise SCLK/MCLK transitions, multimedia clocks, PCIe link changes, thermal throttling, and overdrive/profile hysteresis updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/polaris10_smumgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/polaris10_smumgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/polaris10_smumgr.h

## Purpose
This header defines the private Polaris SMU manager state used by `polaris10_smumgr.c`. It binds the generic SMU7 manager storage to Polaris-specific SMU74 table mirrors, PowerTune defaults, SCLK range data, BIF SCLK values, and memory-controller register table state.

## Important APIs, types, and functions
The important types are `struct polaris10_pt_defaults`, `struct polaris10_range_table`, and `struct polaris10_smumgr`. `polaris10_pt_defaults` carries default PowerTune knobs such as SVI load-line parameters, TDC behavior, DTE ambient temperature, display CAC, BAPM gradient, and BAPM thermal impedance arrays. `polaris10_range_table` stores fallback SCLK transition frequency bounds. `polaris10_smumgr` embeds `struct smu7_smumgr`, a `protected_mode` flag, host mirrors for `SMU74_Discrete_DpmTable`, ULV, and PM fuse data, a range table, a pointer to selected PowerTune defaults, BIF SCLK entries, and an ATOMBIOS MC register table.

## Control flow
The header has no executable control flow, but its layout controls how the C implementation shares state across SMU startup, firmware-header processing, DPM table construction, runtime DPM updates, and teardown. Because `smu7_data` is the first field, code can treat `hwmgr->smu_backend` as either Polaris-specific state or SMU7-compatible state in shared helpers.

## State and persistence behavior
All fields are per-device backend state stored under `hwmgr->smu_backend`. The `smc_state_table` and `power_tune_table` are host mirrors that are later copied into SMC SRAM. Offset and BO state inside `smu7_data` persists until `smu7_smu_fini` frees it.

## Dependencies and integration points
The header depends on endian helpers, SMU74 firmware structures, SMU74 discrete table definitions, and SMU7 manager definitions. It is included by the Polaris implementation and indirectly coupled to SMU7 teardown and firmware-load helpers.

## Risks and test signals
The main risk is structure layout coupling: helper code assumes the embedded `smu7_smumgr` is available at `hwmgr->smu_backend`, and the C file assumes SMU74 structure layouts match firmware. Test signals are successful initialization, correct table offset storage, and clean teardown without BO leaks or invalid casts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/polaris10_smumgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/smu10_smumgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/smu10_smumgr.c

## Purpose
This file implements the SMU manager backend for SMU10/Raven-style APUs. It provides MP1 message passing, driver interface validation, two managed SMU tables, and the `smu10_smu_funcs` callback table used by the PowerPlay hardware manager.

## Important APIs, types, and functions
The exported callback table is `smu10_smu_funcs`. Internal message helpers are `smu10_wait_for_response`, `smu10_send_msg_to_smc_without_waiting`, `smu10_send_msg_to_smc`, `smu10_send_msg_to_smc_with_parameter`, and `smu10_read_arg_from_smc`. Table transfer helpers are `smu10_copy_table_from_smc`, `smu10_copy_table_to_smc`, and `smu10_smc_table_manager`. Lifecycle functions are `smu10_smu_init`, `smu10_start_smu`, `smu10_verify_smc_interface`, and `smu10_smu_fini`.

## Control flow
Initialization allocates `struct smu10_smumgr`, then allocates kernel BOs for `Watermarks_t` and `DpmClocks_t`, recording version, size, firmware table ID, MC address, CPU mapping, and BO handle. Start-up reads the SMU version through `PPSMC_MSG_GetSmuVersion`, updates `adev->pm.fw_version`, disables GFXOFF for older Raven firmware where required, and validates that the firmware driver interface version matches `SMU10_DRIVER_IF_VERSION` or one revision newer.

SMU table transfers set the driver DRAM address high/low through SMC messages and then send either `PPSMC_MSG_TransferTableSmu2Dram` or `PPSMC_MSG_TransferTableDram2Smu`. Reads invalidate HDP before copying from the mapped BO to the caller buffer; writes copy into the mapped BO, flush HDP, and then notify SMU. `smu10_smc_table_manager` uses its `rw` flag as read-from-SMU when true and write-to-SMU when false.

## State and persistence behavior
The backend persists two BO-backed tables in VRAM/GTT for firmware exchange. Table metadata lives in `priv->smu_tables.entry[]`, and the mapped CPU pointers are reused for each transfer. Teardown frees both BOs and clears `hwmgr->smu_backend`.

## Dependencies and integration points
The implementation uses SOC15 MP1 C2PMSG registers, Raven PPSMC message definitions, SMU10 driver interface structures, AMDGPU BO allocation/freeing, HDP cache maintenance, and generic `smum_*` message wrappers. Higher-level hwmgr code uses `smum_smc_table_manager` to exchange watermark and DPM clock tables.

## Risks and test signals
Message helpers report errors only when the final response is zero, so nonzero firmware error codes other than success may be missed. Table IDs are bounded by `MAX_SMU_TABLE`, but callers must pass buffers large enough for the configured table size. The `rw` flag polarity can be easy to misuse. Test signals include successful interface-version validation, correct firmware version in `adev->pm.fw_version`, successful watermark/DPM clock table transfers, HDP-coherent table contents, and no BO leaks on partial init failure or teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/smu10_smumgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/smu10_smumgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/smu10_smumgr.h

## Purpose
This header defines the private table storage used by the SMU10 manager. It is a compact description of the BO-backed tables that SMU10 firmware exchanges with the driver.

## Important APIs, types, and functions
`MAX_SMU_TABLE` is set to 2. `struct smu_table_entry` stores table version, size, firmware table ID, GPU MC address, CPU mapping, and BO handle. `struct smu_table_array` wraps the fixed entry array. `struct smu10_smumgr` contains that array as the backend state.

## Control flow
There is no executable control flow. `smu10_smumgr.c` allocates entries for `SMU10_WMTABLE` and `SMU10_CLOCKTABLE`, initializes their metadata, and later uses them in transfer helpers.

## State and persistence behavior
Each entry represents one persistent BO-backed firmware exchange buffer. The metadata is valid after `smu10_smu_init` succeeds and remains live until `smu10_smu_fini`.

## Dependencies and integration points
The header includes Raven PPSMC and SMU10 driver-interface definitions for table IDs and C structures. It integrates with generic hwmgr table management through `smum_smc_table_manager`.

## Risks and test signals
The fixed table count means new SMU10 table users must update both the enum/index assumptions and allocation paths. Test signals are table metadata with nonzero version and size, valid MC addresses, and clean BO release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/smu10_smumgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/smu7_smumgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/smu7_smumgr.c

## Purpose
This file provides common SMU7-family helper code for discrete GPUs. It handles SMC SRAM access, SMU firmware upload, SMU message transport, microcode TOC construction/loading, firmware-load polling, power-virus setup for AVFS/BTC paths, and allocation/freeing of shared SMU7 backend buffers.

## Important APIs, types, and functions
The public helpers include `smu7_copy_bytes_to_smc`, `smu7_program_jump_on_start`, `smu7_is_smc_ram_running`, `smu7_send_msg_to_smc`, `smu7_send_msg_to_smc_with_parameter`, `smu7_get_argument`, `smu7_send_msg_to_smc_offset`, `smu7_convert_fw_type_to_cgs`, `smu7_read_smc_sram_dword`, `smu7_write_smc_sram_dword`, `smu7_request_smu_load_fw`, `smu7_check_fw_load_finish`, `smu7_reload_firmware`, `smu7_upload_smu_firmware_image`, `smu7_setup_pwr_virus`, `smu7_init`, and `smu7_smu_fini`. Static helpers set indirect SMC SRAM addresses, populate individual firmware TOC entries, upload the SMU image, and execute power-virus command tables.

## Control flow
SMC SRAM writes use `mmSMC_IND_INDEX_11` and `mmSMC_IND_DATA_11`, enforcing 4-byte alignment and limit bounds. `smu7_copy_bytes_to_smc` writes full words MSB-first and preserves untouched bytes for trailing partial words. Message sends wait for the previous response, clear the response register, write the message or argument, wait again, and log unsupported/failure responses.

Firmware loading is a two-stage path. `smu7_upload_smu_firmware_image` fetches either SMU or SMU_SK firmware depending on `security_hard_key`, records kicker and version state in `hwmgr`, and streams the image into SMC SRAM. `smu7_request_smu_load_fw` initializes AMDGPU ucode BOs, clears the firmware load status soft register, optionally provides SMU DRAM buffer addresses, lazily builds a `SMU_DRAMData_TOC` with RLC/SDMA/CP/MEC entries, copies it into the header buffer, gives the SMU the header buffer address, sends `PPSMC_MSG_LoadUcodes`, and waits until the load status matches the requested firmware mask.

## State and persistence behavior
`smu7_init` expects `hwmgr->smu_backend` to already point at a compatible `struct smu7_smumgr` or embedding object. It allocates a VRAM header buffer for the DRAM TOC and, for non-VF paths, a larger SMU buffer. It also marks `hwmgr->avfs_supported` when hardware AVFS is present and the feature mask allows it. `smu7_request_smu_load_fw` caches the TOC pointer until failure or final teardown. `smu7_smu_fini` frees header and SMU BOs, frees the TOC, frees the backend object, and clears `hwmgr->smu_backend`.

## Dependencies and integration points
The code depends on CGS register access, SMU7 PPSMC definitions, `cgs_get_firmware_info`, AMDGPU ucode BO initialization, AMDGPU kernel BO allocation, soft-register offsets supplied by chip-specific managers via `smum_get_offsetof`, and firmware IDs shared with the graphics/memory/compute blocks. Polaris, Tonga, Fiji, and related backends reuse these helpers.

## Risks and test signals
`smu7_send_msg_to_smc` logs firmware errors but returns 0, so callers cannot reliably distinguish SMU rejection from success. `smu7_populate_single_firmware_entry` also returns 0 even when firmware lookup failed, leaving callers dependent on side effects rather than a propagated error. Bounds checks protect SRAM access, but callers must pass correct firmware-provided offsets and limits. Test signals include successful SMU SRAM upload, nonzero SMU version, firmware load status matching requested masks, no BO leaks across VF/non-VF init and teardown, and no dmesg errors from unsupported SMU messages during DPM enablement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/smu7_smumgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/smu7_smumgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/smu7_smumgr.h

## Purpose
This header declares the shared SMU7 backend state and helper APIs used by chip-specific SMU managers such as Polaris, Tonga, and Fiji.

## Important APIs, types, and functions
`struct smu7_buffer_entry` describes a BO-backed firmware exchange buffer with size, MC address, CPU mapping, and BO handle. `struct smu7_smumgr` stores the SMU/header buffers, optional TOC pointer, firmware-discovered SMC table offsets, security key selection, ACPI optimization, and AVFS BTC parameter. The function declarations expose SMC SRAM copy/read/write helpers, SMU message helpers, firmware ID conversion, firmware loading/reload, init/fini, and power-virus setup.

## Control flow
The header itself has no control flow, but it establishes the lifecycle: chip-specific code allocates or embeds `struct smu7_smumgr`, `smu7_init` allocates buffers, chip-specific startup uploads/starts SMU firmware, `smu7_request_smu_load_fw` loads dependent microcodes, and `smu7_smu_fini` releases the state.

## State and persistence behavior
The offset fields are populated from SMU firmware headers and then reused for SMC SRAM updates. Buffer entries persist for the device lifetime, while `toc` may be created lazily during firmware load and freed on failure or final teardown.

## Dependencies and integration points
The header depends on endian helpers and AMDGPU BO types. It is included by SMU7-family managers and by common code that needs message/SRAM helper prototypes.

## Risks and test signals
The structure is frequently embedded, so teardown frees `hwmgr->smu_backend` and must match allocation ownership. Offset fields are valid only after firmware-header processing. Test signals are valid BO addresses, populated offsets, successful firmware-load masks, and clean teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/smu7_smumgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/smu8_smumgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/smu8_smumgr.c

## Purpose
This file implements the SMU8/Carrizo-Stoney manager backend. It manages MP1 message passing, a TOC/job-list model for firmware and scratch tasks, firmware loading for graphics-related microcodes, Fusion clock table transfer, MEC firmware setup, DPM-running detection, and lifecycle allocation/freeing for SMU8 buffers.

## Important APIs, types, and functions
The exported callback table is `smu8_smu_funcs`. Message helpers include `smu8_get_argument`, `smu8_send_msg_to_smc_with_parameter`, and `smu8_send_msg_to_smc`. SRAM helpers include `smu8_set_smc_sram_address`, `smu8_write_smc_sram_dword`, and `smu8_check_fw_load_finish`. Firmware and TOC helpers include `smu8_translate_firmware_enum_to_arg`, `smu8_convert_fw_type_to_cgs`, `smu8_smu_populate_single_scratch_task`, `smu8_smu_populate_single_ucode_load_task`, `smu8_smu_construct_toc`, `smu8_smu_populate_firmware_entries`, and `smu8_request_smu_load_fw`. Lifecycle and table functions include `smu8_smu_init`, `smu8_start_smu`, `smu8_smu_fini`, `smu8_download_pptable_settings`, `smu8_upload_pptable_settings`, and `smu8_is_dpm_running`.

## Control flow
Initialization allocates `struct smu8_smumgr`, a 4 KiB TOC BO, and a combined SMU scratch BO. It carves the scratch BO into aligned entries for RLC scratch, RLC SRM ARAM/DRAM, multimedia power profiling, and the Fusion clock table. Starting SMU reads the firmware version from SMU SRAM, records it in `hwmgr` and `adev->pm`, and calls `smu8_request_smu_load_fw`.

Firmware loading initializes AMDGPU ucode BOs, populates driver buffer entries from firmware info, constructs the TOC job list, clears `UcodeLoadStatus` in SMU SRAM, sends the TOC address to SMU, initializes jobs, executes ARAM save, power profiling, and bootup tasks, polls the firmware load status mask, and finally programs MEC instruction base registers from CP MEC firmware info. Stoney-specific branches collapse SDMA1 and MEC_JT2 handling onto single-engine equivalents.

PowerPlay clock-table exchange finds the Fusion clock table scratch entry, tells SMU its address, executes the clock-table TOC task, and sends either `PPSMC_MSG_ClkTableXferToDram` or `PPSMC_MSG_ClkTableXferToSmu`. DPM running is checked by asking firmware for feature status and testing `SMU_EnabledFeatureScoreboard_SclkDpmOn`.

## State and persistence behavior
`struct smu8_smumgr` persists TOC indices, buffer usage, BO mappings, firmware entries, and scratch entries. The TOC in VRAM is mutable and reconstructed before firmware load. Scratch entries point into a single BO and are reused for job execution and clock table transfer. Firmware load state is also stored in SMU SRAM header fields.

## Dependencies and integration points
The file depends on SMU8 register definitions, CZ PPSMC messages, SMU8 Fusion structures, SMU ucode transfer structures, GFX8 MEC registers, CGS firmware lookup, AMDGPU BO management, and generic `smum_*` wrappers. It integrates with SMU8 hwmgr code through PowerPlay table download/upload and DPM feature checks.

## Risks and test signals
Several scratch-entry searches assume the requested entry exists; if not, later code can use an out-of-range index. TOC task population increments `toc_entry_used_count` before validating backing buffers, so error paths must be treated carefully. Message timeout warnings provide useful diagnostics, but many `smum_send_msg_*` return values are ignored in load and table-transfer paths. Test signals include nonzero SMU version, successful firmware load status masks, MEC firmware base programmed, valid TOC indices, clock table round-trip success, DPM feature status showing SCLK DPM enabled, and clean BO release on all init failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/smu8_smumgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/smu8_smumgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/smu8_smumgr.h

## Purpose
This header defines SMU8 private backend storage, scratch entry IDs, buffer descriptors, and metadata structures used for Carrizo/Stoney firmware TOC and scratch jobs.

## Important APIs, types, and functions
Key constants define maximum firmware and scratch entries plus scratch sizes for clock gating, golden settings, SDMA metadata, and IH metadata. `enum smu8_scratch_entry` names all supported firmware, scratch, data, and Fusion clock-table entries. `struct smu8_buffer_entry` records size, MC address, CPU mapping, logical firmware/scratch ID, and BO handle. `struct smu8_register_index_data_pair` and `struct smu8_ih_meta_data` describe metadata used for register restore tasks. `struct smu8_smumgr` tracks TOC indices, buffer usage, TOC/SMU/firmware BOs, driver buffers, metadata buffers, and scratch buffers.

## Control flow
The header has no executable logic, but its enum values drive TOC construction in `smu8_smumgr.c`: entries are translated into firmware arguments, task types, scratch addresses, and job-list indices.

## State and persistence behavior
The backend state is per-device and lives under `hwmgr->smu_backend`. Most scratch entries are slices of one SMU buffer; TOC and firmware entries persist across firmware load and table exchange until teardown.

## Dependencies and integration points
The header is paired with SMU8 firmware transfer definitions and CZ PPSMC task/job concepts. Higher layers interact with it only through `smu8_smu_funcs` and generic `smum_*` wrappers.

## Risks and test signals
The fixed array sizes mean future firmware entries require careful bounds updates. The semantic coupling between enum IDs, firmware IDs, and task arguments is high. Test signals are valid scratch lengths, no TOC overrun, correct Stoney entry substitutions, and successful firmware/clock-table tasks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/smu8_smumgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/smu9_smumgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/smu9_smumgr.c

## Purpose
This file provides common SMU9 MP1 message helpers for Vega-era PowerPlay code. It checks whether SMU firmware is running, sends messages with or without parameters, waits for firmware responses, and reads response arguments.

## Important APIs, types, and functions
The public functions are `smu9_is_smc_ram_running`, `smu9_send_msg_to_smc`, `smu9_send_msg_to_smc_with_parameter`, and `smu9_get_argument`. Static helpers are `smu9_wait_for_response` and `smu9_send_msg_to_smc_without_waiting`.

## Control flow
SMU-running detection reads `smnMP1_FIRMWARE_FLAGS` through the MP1 public aperture and tests the interrupt-enabled bit. Message sending first waits until the previous response register is nonzero, clears it, writes the parameter register when needed, writes the message register, waits for a new response, and logs an error when the response is not `1`. SR-IOV one-VF mode uses C2PMSG 101/102/103, while the normal path uses C2PMSG 66/82/90.

## State and persistence behavior
The file does not allocate persistent backend state. It persists only through hardware mailbox registers and uses `hwmgr->pp_one_vf` to select mailbox layout.

## Dependencies and integration points
The code depends on SOC15 MP1 register macros, Vega10 register definitions, PP debug/wait helpers, and generic hwmgr state. Chip-specific SMU9 managers can install these helpers in their `pp_smumgr_func` tables or call them directly.

## Risks and test signals
Both send functions return 0 even when firmware returns an error response, so callers need logs or response-specific side effects to detect failures. Timeout errors are logged by `smu9_wait_for_response`, but the final return path still reads the register. Test signals include MP1 firmware flags showing interrupts enabled, correct mailbox selection in one-VF versus PF mode, response value `1` for expected messages, and valid argument reads from C2PMSG 82 or 102.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/smu9_smumgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/smu9_smumgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/smu9_smumgr.h

## Purpose
This header declares the common SMU9 message helper surface used by Vega-era SMU manager implementations.

## Important APIs, types, and functions
It declares `smu9_is_smc_ram_running`, `smu9_send_msg_to_smc`, `smu9_send_msg_to_smc_with_parameter`, and `smu9_get_argument`. There are no private structs in this header.

## Control flow
The header has no executable flow. Implementations use the functions to wait on MP1 mailbox responses, send messages, optionally pass a parameter, and read the response argument.

## State and persistence behavior
No persistent state is declared here; state is held in MP1 registers and `struct pp_hwmgr` fields such as `pp_one_vf`.

## Dependencies and integration points
The prototypes depend on `struct pp_hwmgr` and PowerPlay SMU message conventions. The header is included by SMU9-family code that wants the shared message transport.

## Risks and test signals
The interface reports `int` status for sends but the implementation currently returns 0 for firmware error responses. Test signals are correct compile-time linkage, successful mailbox traffic, and valid argument reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/smu9_smumgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/smumgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/smumgr.c

## Purpose
This file is the generic SMU manager dispatch layer for the legacy AMD PowerPlay stack. It declares firmware blobs required by supported ASICs and provides stable wrapper functions that call the currently selected `hwmgr->smumgr_funcs` implementation.

## Important APIs, types, and functions
The `MODULE_FIRMWARE` declarations cover SMU firmware for Bonaire, Hawaii, Topaz, Tonga, Fiji, Polaris10/11/12, VegaM, Vega10, Vega12, and Vega20 variants. Wrapper APIs include thermal/AVFS setup, SCLK threshold update, SMU table update, firmware-header processing, macro/offset lookup, PowerPlay table download/upload, message sending with optional response capture, SMC table management, DPM-running and AVFS-present checks, MC register table initialization, profile update, and SMU stop.

## Control flow
Most wrappers are null-safe dispatch functions: if the selected backend provides the callback, the wrapper calls it; otherwise it returns a neutral default such as 0, true, false, or `-EINVAL` depending on the API. `smum_send_msg_to_smc` and `smum_send_msg_to_smc_with_parameter` are stricter: they validate `hwmgr`, required backend callbacks, and `get_argument` availability when the caller asks for a response. They serialize mailbox access with `hwmgr->msg_lock`, invoke the backend send function, optionally fetch the argument, and release the mutex.

## State and persistence behavior
This file owns no backend state. Its persistent effect is through function dispatch into the active SMU manager and through the message mutex protecting firmware mailbox registers shared across the driver.

## Dependencies and integration points
It depends on Linux module/firmware infrastructure, AMDGPU DRM headers, and `smumgr.h`. It is the integration point used by hwmgr, powertune, clock/power gating, display, and ASIC-specific code so callers do not need to know which SMU generation is active.

## Risks and test signals
Neutral defaults can hide missing backend functionality; for example `smum_is_dpm_running` returns true when no callback exists, while update APIs may silently do nothing. Message wrappers serialize access correctly, but they trust backend send helpers to propagate firmware failures, and several backends return 0 after logging errors. Test signals include correct backend selection in `hwmgr.c`, successful firmware blob requests, no concurrent mailbox corruption under multi-call workloads, expected `-EINVAL` when a required callback is absent, and meaningful response values when callers request `resp`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/smumgr.c -->
