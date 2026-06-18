# subset-b-003530 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/tonga_smumgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/tonga_smumgr.c

Purpose: Tonga's PowerPlay SMU manager for SMU 7.2 hardware. It boots protected or non-protected SMU firmware, reads firmware-header table addresses, constructs SMU72 DPM/voltage/fan/MC tables from VBIOS PowerPlay data, uploads them to SMC SRAM, and exposes the `tonga_smu_funcs` backend.

Important APIs and functions: `tonga_smu_init()` allocates `struct tonga_smumgr` then delegates common setup to `smu7_init()`. `tonga_start_smu()` selects `tonga_start_in_non_protection_mode()` or `tonga_start_in_protection_mode()` based on `SMU_FIRMWARE.SMU_MODE`, then requests firmware loading. `tonga_process_firmware_header()` captures DPM, soft-register, MC-register, fan, ARB, and version offsets. `tonga_init_smc_table()` is the central orchestration path, calling voltage table, ULV, PCIe link, graphics, memory, ACPI, VCE, ACP, ARB timing, UVD, boot-level, BAPM, clock-stretcher, VR-config, PM-fuse, and MC-register population routines. Runtime update hooks include `tonga_update_smc_table()`, `tonga_update_sclk_threshold()`, `tonga_update_dpm_settings()`, and `tonga_thermal_setup_fan_table()`.

Control flow: initialization starts with allocation and SMU7 common initialization, firmware start/reset sequencing, firmware-header parsing, then full DPM-table construction. Graphics levels are derived from SCLK DPM entries, AtomBIOS PLL dividers, voltage dependencies, profile hysteresis/activity, display deep-sleep constraints, and PCIe-level mapping. Memory levels use MCLK dependencies, memory PLL dividers, strobe/EDC/stutter thresholds, display state, and GDDR5/DDR3 handling. The final `SMU72_Discrete_DpmTable` is endian-converted and copied into SMC SRAM from `SystemFlags` onward, while graphics and memory level arrays are also uploaded at their array offsets.

State and persistence: persistent driver state lives in `hwmgr->smu_backend` as `struct tonga_smumgr`, including cached `smc_state_table`, `power_tune_table`, `mc_regs`, VBIOS-derived `mc_reg_table`, and inherited `smu7_data` table offsets. Hardware-visible state persists in SMC SRAM, indirect SMC registers, soft registers, and selected platform capability bits. Several paths mutate `hwmgr->platform_descriptor.platformCaps` depending on GPIO/VBIOS capability discovery.

Dependencies and integration: this file depends on SMU72 firmware structs, `smu7_smumgr` helpers, CGS register access, AtomBIOS clock/voltage helpers, `smu7_hwmgr` DPM state, PowerPlay table structures, AMDGPU device/PCI IDs, and VI register headers for SMU/GMC/BIF/DCE blocks. The exported `pp_smumgr_func` table plugs Tonga into the PowerPlay hardware manager.

Risks and test signals: high-risk areas are endian conversion before SRAM upload, table offset validity from firmware headers, VBIOS table bounds, boot-level fallback behavior, MC register valid-flag compaction, bitfield updates to unaligned SMC words, and protected-mode boot sequencing. Useful tests are boot/resume on Tonga boards, SR-IOV/non-VF behavior, DPM enable/disable checks through `FEATURE_STATUS`, UVD/VCE boot-level changes, fan-table upload with and without a fan, OverDrive SCLK/MCLK update paths, clock-stretcher capability handling, and register traces confirming SMC messages and SRAM writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/tonga_smumgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/tonga_smumgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/tonga_smumgr.h

Purpose: Tonga SMU manager private interface. It defines the ASIC ID predicate, default PowerTune data layout, memory-controller register table structures, and the private backend state consumed by `tonga_smumgr.c`.

Important APIs and types: `ASICID_IS_TONGA_P()` identifies Tonga-P device/revision combinations used by clock-stretcher voltage formulas. `struct tonga_pt_defaults` stores PowerTune/BAPM constants, including DTE iteration arrays sized by SMU72 dimensions. `struct tonga_mc_reg_entry` and `struct tonga_mc_reg_table` represent VBIOS memory timing register entries plus valid-address metadata. `struct tonga_smumgr` embeds `struct smu7_smumgr`, the cached `SMU72_Discrete_DpmTable`, ULV settings, PM fuses, MC registers, MC register conversion table, and selected PowerTune defaults.

Control flow and integration: the header is included by the Tonga implementation and bridges common SMU7 code with SMU72-specific firmware table definitions. Its structures are allocated by `tonga_smu_init()`, filled by firmware-header parsing, DPM table population, PowerTune population, and MC register initialization, then used when uploading SRAM payloads.

State and persistence: all fields are driver-resident cached state; persistence to hardware only happens when the C file serializes these structures into SMC SRAM or indirect registers. The MC table caches both original and low-power register aliases so later DPM updates can compact and upload only valid changing registers.

Dependencies and risks: depends on `smu72_discrete.h`, `smu7_smumgr.h`, and `smu72.h`. Risks are array size coupling with firmware definitions, packed hardware table assumptions, and macro device ID drift. Compile coverage across Tonga variants and DPM-table upload tests are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/tonga_smumgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/vega10_smumgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/vega10_smumgr.c

Purpose: Vega10 SMU9 PowerPlay manager shim. Unlike Tonga, it does not build large legacy SRAM DPM tables; it allocates driver-visible VRAM buffers for SMU tables, transfers them through SMU messages, controls feature masks, verifies the SMU interface version, and registers `vega10_smu_funcs`.

Important APIs and functions: `vega10_copy_table_from_smc()` and `vega10_copy_table_to_smc()` set high/low driver DRAM addresses, transfer tables between SMU and VRAM, and use HDP invalidate/flush around CPU-visible copies. `vega10_enable_smc_features()` gates feature enable/disable and intentionally no-ops for virtual functions. `vega10_get_enabled_smc_features()` reads the enabled feature mask; `vega10_is_dpm_running()` checks it against `SMC_DPM_FEATURES`. `vega10_smu_init()` allocates buffers for PPTABLE, watermark, AVFS, PM status log/tools, and AVFS fuse override. `vega10_start_smu()` checks RAM is already running, verifies SMU9 driver interface version except for selected device/revision IDs, and programs the tools address.

Control flow: init validates firmware availability through CGS, allocates the backend and each table buffer, recording version/size/table IDs. Table transfers copy user data into the backing buffer, flush HDP, send address and transfer messages, or reverse that flow with invalidate and memcpy. Fini frees each allocated buffer in the reverse shape and clears `hwmgr->smu_backend`.

State and persistence: persistent state is `struct vega10_smumgr` with an array of table entries containing version, size, SMU table ID, MC address, CPU pointer, and BO handle. Hardware state persists in SMU-managed tables after transfer messages and in enabled feature bits. SR-IOV VFs are prevented from mutating SMU features and table uploads are skipped because firmware/hypervisor owns the state.

Dependencies and integration: depends on SMU9 messaging helpers, Vega10 SMU interface definitions, AMDGPU BO allocation, HDP cache management, CGS firmware info, and PowerPlay `pp_smumgr_func`. Risk areas are mismatched table IDs/sizes, missing HDP cache synchronization, partial allocation cleanup, firmware interface mismatch, and VF behavior. Test signals include table round-trips, feature-mask enable/disable, DPM-running detection, firmware-version rejection, and leak/error-path coverage for each allocation failure point.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/vega10_smumgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/vega10_smumgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/vega10_smumgr.h

Purpose: private Vega10 SMU manager declarations for the PowerPlay SMU9 path. It declares the driver-side table bookkeeping structs and exported helpers for SMU feature control.

Important APIs and types: `MAX_SMU_TABLE` fixes the local table array size at five entries. `struct smu_table_entry` records table version, byte size, SMU table ID, GPU MC address, CPU mapping pointer, and BO handle. `struct smu_table_array` wraps the fixed entries, and `struct vega10_smumgr` stores that array as the backend. Exported functions are `vega10_enable_smc_features()` and `vega10_get_enabled_smc_features()`.

Control flow and integration: `vega10_smumgr.c` allocates and fills these entries during init, then table-manager calls use the metadata to validate and transfer tables. Other Vega10 PowerPlay code can include this header to toggle or query SMU feature state.

State and persistence: the header defines driver-owned metadata only; persistence to VRAM and SMU state occurs in the C file through AMDGPU BOs and SMU transfer messages. The explicit `table_id` member distinguishes local array indexes from SMU protocol table IDs.

Dependencies, risks, and tests: depends on AMDGPU BO and `pp_hwmgr` declarations from the surrounding include graph. Main risks are `MAX_SMU_TABLE` staying aligned with enum usage and duplicate type names across sibling Vega headers if included together. Compile tests and allocation/transfer table coverage are the practical signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/vega10_smumgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/vega12_smumgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/vega12_smumgr.c

Purpose: Vega12 SMU9 PowerPlay manager. It manages SMU table buffer allocation, table transfers, feature masks split across low/high 32-bit messages, DPM-running detection, tools-log address setup, and SMU function registration.

Important APIs and functions: `vega12_copy_table_from_smc()` and `vega12_copy_table_to_smc()` validate `TABLE_COUNT` entries, set driver DRAM address registers via SMU messages, transfer tables, and synchronize HDP. `vega12_enable_smc_features()` splits a 64-bit feature mask into low/high halves and sends enable or disable messages for both. `vega12_get_enabled_smc_features()` reconstructs the 64-bit feature mask from low/high responses. `vega12_smu_init()` allocates PPTABLE, WMTABLE, PMSTATUSLOG, AVFS fuse override, OverDrive, and SMU metrics buffers. `vega12_start_smu()` requires `smu9_is_smc_ram_running()` and sets the PM status log tools address.

Control flow: the backend is allocated after firmware availability is confirmed. Each table buffer is allocated in VRAM with page alignment, then version and size are recorded. On failure, labels free already-created buffers. Table-manager calls use `rw` as read-from-SMC vs write-to-SMC selector. Fini frees all table BOs and nulls the backend.

State and persistence: `struct vega12_smumgr` caches table metadata and BO mappings. Hardware-visible state is created by SMU table transfers, enabled-feature messages, and tools-address messages. There is no per-table protocol ID field; `table_id` is sent directly, so local enum values must match the SMU interface contract.

Dependencies and integration: integrates with `smu9_smumgr`, `vega12/smu9_driver_if.h`, AMDGPU BO/HDP helpers, CGS firmware lookup, and PowerPlay manager callbacks. Risks include low/high feature-mask bit shifts, direct table ID assumptions, absent explicit SMU interface-version verification compared with Vega10, and cleanup correctness on mid-init failures. Test signals are table transfer round-trips, feature toggling above and below bit 32, DPM-running checks, allocation failure injection, and suspend/resume with PM status logging enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/vega12_smumgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/vega12_smumgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/vega12_smumgr.h

Purpose: private Vega12 SMU manager declarations. It defines table metadata sized by Vega12's SMU9 `TABLE_COUNT`, feature-mask split constants, and exported feature control helpers.

Important APIs and types: `struct smu_table_entry` stores version, size, MC address, CPU table pointer, and BO handle. `struct smu_table_array` contains `entry[TABLE_COUNT]`; `struct vega12_smumgr` embeds it. `SMU_FEATURES_LOW_MASK/HIGH_MASK` and shifts encode the split between low and high SMU feature messages. Exports are `vega12_enable_smc_features()` and `vega12_get_enabled_smc_features()`.

Control flow and state: implementation code fills each entry during init and uses indexes directly as SMU protocol table IDs. The table state remains driver-resident until transfer messages copy payloads to or from SMU-owned memory.

Dependencies, integration, and risks: depends on `hwmgr.h`, `vega12/smu9_driver_if.h`, and `vega12_hwmgr.h`. The largest coupling risk is that `TABLE_COUNT` and enum values must stay synchronized with firmware headers. Compile coverage, feature-mask tests for high bits, and table allocation/transfer tests are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/vega12_smumgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/vega20_smumgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/vega20_smumgr.c

Purpose: Vega20 SMU11 PowerPlay manager. It implements direct MP1 mailbox messaging, SMU table transfers, activity-monitor coefficient transfers, 64-bit feature control, table-buffer lifecycle, tools/PPTABLE address setup, I2C-control init/fini, and registers `vega20_smu_funcs`.

Important APIs and functions: `vega20_is_smc_ram_running()` checks MP1 firmware flags through PCIE MMIO. `vega20_wait_for_response()`, `vega20_send_msg_to_smc_without_waiting()`, `vega20_send_msg_to_smc()`, `vega20_send_msg_to_smc_with_parameter()`, and `vega20_get_argument()` implement the SMU11 mailbox protocol on MP1 C2PMSG registers. Table movement is handled by `vega20_copy_table_from_smc()` and `vega20_copy_table_to_smc()`. `vega20_set_activity_monitor_coeff()` and `vega20_get_activity_monitor_coeff()` transfer workload-specific activity monitor coefficient tables. `vega20_smu_init()` allocates PPTABLE, watermarks, PM status log, OverDrive, SMU metrics, activity monitor buffers, and initializes SMU v11 I2C control.

Control flow: start verifies SMC RAM is running and sets the tools DRAM address. Message sends wait for an idle response, clear response content, optionally write a parameter, send a message ID, then wait for `PPSMC_Result_OK`. Table transfers set high/low DRAM addresses, issue transfer messages, and use HDP flush/invalidate around CPU copies. Fini shuts down I2C control and releases all table BOs.

State and persistence: backend state is `struct vega20_smumgr` containing table metadata. Hardware state persists in MP1 mailbox registers, SMU feature masks, SMU-resident table contents, the tools address, and I2C control state. `vega20_set_pptable_driver_address()` separately exposes the PPTABLE buffer address for callers that need to stage PPTABLE transfer.

Dependencies and integration: depends on SMU11 driver interface structs, Vega20 PPSMC messages, SOC15/MP1 register access, AMDGPU BO/HDP helpers, SMU ucode firmware lookup through CGS, `smu_v11_0_i2c`, and the PowerPlay callback table. Risks include mailbox timeout/error handling, direct enum-to-table-ID coupling, HDP coherency, activity-monitor workload ID packing in the high 16 bits, and init error cleanup. A notable cleanup risk is that if I2C init fails after the activity-monitor BO is allocated, the error path jumps to a label that frees later common tables but does not explicitly free the activity-monitor BO. Test signals include mailbox response failure tests, table round-trips, high-bit feature toggling, activity-monitor per-workload transfers, I2C init/fini leak checks, and boot/resume DPM-running detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/vega20_smumgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/vega20_smumgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/vega20_smumgr.h

Purpose: private Vega20 SMU11 manager declarations and exported helper prototypes. It describes table metadata sized by SMU11 `TABLE_COUNT`, feature-mask split constants, activity-monitor helpers, PPTABLE address setup, and SMC RAM running detection.

Important APIs and types: `struct smu_table_entry`, `struct smu_table_array`, and `struct vega20_smumgr` mirror the table metadata used by the C implementation. `SMU_FEATURES_LOW_MASK/HIGH_MASK` and shifts split 64-bit feature masks across low/high SMU messages. Exported helpers are `vega20_enable_smc_features()`, `vega20_get_enabled_smc_features()`, `vega20_set_activity_monitor_coeff()`, `vega20_get_activity_monitor_coeff()`, `vega20_set_pptable_driver_address()`, and `vega20_is_smc_ram_running()`.

Control flow and integration: other Vega20 PowerPlay modules can include this header to query feature state, move activity monitor coefficients, set the PPTABLE address before SMU consumption, and check MP1 firmware readiness. The implementation owns allocation and transfer details.

State, dependencies, and risks: the header defines driver-resident metadata for VRAM-backed SMU tables and relies on `smu11_driver_if.h` for table IDs and payload types. Risks are table enum drift, duplicated `struct smu_table_entry` names among sibling headers, and feature-mask split mistakes. Compile coverage plus table and feature tests are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/vega20_smumgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/vegam_smumgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/vegam_smumgr.c

Purpose: VegaM SMU manager for an SMU7/SMU75-based PowerPlay path. It boots SMU firmware, reads SMU75 firmware-header offsets, builds and uploads SMU75 DPM/voltage/thermal/AVFS tables, updates media/BIF tables, and registers `vegam_smu_funcs`.

Important APIs and functions: `vegam_smu_init()` allocates backend state and calls `smu7_init()`. Protected/non-protected boot paths are `vegam_start_smu_in_protection_mode()` and `vegam_start_smu_in_non_protection_mode()`, selected by `vegam_start_smu()`. `vegam_process_firmware_header()` captures DPM, soft-register, MC, fan, ARB, and version offsets. `vegam_init_smc_table()` is the central table-building path. It calls voltage, ULV, link, graphics, memory, ACPI, VCE, memory timing, UVD, boot, initial-state, BAPM, clock-stretcher, AVFS, VR config, PM fuse, and CU-reconfiguration setup. Runtime hooks include `vegam_update_smc_table()`, `vegam_update_sclk_threshold()`, `vegam_thermal_avfs_enable()`, and `vegam_thermal_setup_fan_table()`.

Control flow: graphics levels use AI PLL divider helpers when available, otherwise a local FCW range table derived from AtomBIOS or hardcoded ranges. Memory levels use AI memory PLL dividers and voltage dependencies. UVD/VCE levels derive DFS dividers and packed voltage fields. `vegam_init_smc_table()` sets system flags, fills link and clock levels, programs ARB timing tables for every SCLK/MCLK pair, configures GPIOs, BIF SCLK DFS dividers, endian-converts fields, then copies the SMU75 DPM table to SMC SRAM.

State and persistence: driver state lives in `struct vegam_smumgr`, including SMU7 common offsets, protected-mode status, cached SMU75 DPM table, PM fuse table, FCW range table, PowerTune defaults, and BIF SCLK table. Hardware-visible persistence occurs through SMC SRAM writes, indirect SMC soft-register writes, SMU messages, capability-bit mutation, and firmware-owned AVFS/PM fuse tables. AVFS parameters are copied to firmware-header-referenced SRAM tables and can later be enabled with SMU messages.

Dependencies and integration: depends on SMU75 firmware structs, SMU7 common helpers, AtomBIOS clock/voltage/AVFS helpers, CGS register access, GFX/GMC/BIF/DCE register headers, `smu7_hwmgr` state, PowerPlay tables, and AMDGPU CU information. The backend callback table exposes SMU7 messaging, firmware reload, DPM table population, offset lookup, AVFS probing, and thermal hooks.

Risks and test signals: risks include packed voltage bitfield correctness, endian conversion, VBIOS dependency-table bounds, hardcoded FCW/clock-stretcher formulas, GPIO capability mutation, and AVFS SRAM offset validity. `vegam_get_dependency_volt_by_clk()` has suspicious max-clock fallback indexing: it checks `dep_table->entries[i].mvdd` after `i` can equal `count`, while assigning from `entries[i - 1]`; this is an out-of-bounds risk. Test signals include SMU boot in both protection modes, DPM table upload validation, UVD/VCE/BIF table updates, AVFS present/enable paths, fanless thermal behavior, memory timing updates after DPM changes, and boot-level matching against VBIOS dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/vegam_smumgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/vegam_smumgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/vegam_smumgr.h

Purpose: private VegaM SMU manager header for the SMU75 path. It defines SMU RAM bounds, tuning bit shifts/defaults, PowerTune default layout, SCLK range cache, and backend state used by `vegam_smumgr.c`.

Important APIs and types: `SMC_RAM_END` sets the SMC SRAM limit used in copy/read calls. `DPMTuning_*` shifts and `GraphicsDPMTuning_VEGAM`, `MemoryDPMTuning_VEGAM`, `SclkDPMTuning_VEGAM`, and `MclkDPMTuning_VEGAM` encode default hysteresis/activity values. `struct vegam_pt_defaults` stores PowerTune and BAPM constants sized by SMU75 dimensions. `struct vegam_range_table` caches lower/upper SCLK transition frequencies. `struct vegam_smumgr` embeds common SMU7 data, protected-mode flag, SMU75 DPM table, ULV state, PM fuses, range table, selected defaults, and BIF SCLK levels.

Control flow and integration: the implementation allocates this struct as `hwmgr->smu_backend`, fills range and BIF tables during DPM setup, and serializes SMU75 tables to firmware SRAM. The header bridges generic SMU7 helpers with VegaM-specific SMU75 layouts.

State and persistence: all fields are driver cache until copied to SMC SRAM or used to send SMU messages. `protected_mode` records boot mode discovery; `range_table` supports fallback FCW calculations; `bif_sclk_table` feeds link-level DFS divider programming.

Dependencies, risks, and tests: depends on `pp_endian.h`, `smu75_discrete.h`, and `smu7_smumgr.h`. Risks are firmware-structure size coupling, hardcoded tuning constants, and duplicated names relative to other SMU manager headers. Compile coverage and table-upload boot tests on VegaM hardware are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/vegam_smumgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/Makefile

Purpose: build-system glue for AMDGPU's software SMU power-management layer. It includes per-generation swsmu Makefiles and adds common swsmu manager objects to the broader PowerPlay file list.

Important variables and control flow: `AMD_SWSMU_PATH` points to `../pm/swsmu` relative to the AMDGPU build path. `SWSMU_LIBS` lists generation subdirectories `smu11 smu12 smu13 smu14 smu15`. `AMD_SWSMU` expands those into included Makefile paths under `$(FULL_AMD_PATH)/pm/swsmu/`. `SWSMU_MGR` lists common objects `amdgpu_smu.o` and `smu_cmn.o`. `AMD_SWSMU_POWER` prefixes those objects with the swsmu path, and `AMD_POWERPLAY_FILES += $(AMD_SWSMU_POWER)` appends them to the driver build.

State and persistence: this file has no runtime state. Its persistent effect is make-time composition of object lists and inclusion of generation-specific build fragments. It relies on outer AMDGPU Makefile variables such as `FULL_AMD_PATH` and `AMD_POWERPLAY_FILES`.

Dependencies and integration: integrates the swsmu directory into the kernel DRM AMDGPU build, while generation sub-Makefiles contribute additional objects. It coexists with the older `powerplay/smumgr` files in this research set by selecting build inputs rather than runtime behavior.

Risks and test signals: risks are path mismatches when the AMDGPU tree layout changes, missing generation Makefiles, object list omissions, and accidental ordering changes in `AMD_POWERPLAY_FILES`. Test signals are kernel build coverage for all configured ASIC generations, `make M=drivers/gpu/drm/amd` dependency expansion, and checking that `amdgpu_smu.o`/`smu_cmn.o` are linked when swsmu-supported ASICs are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/Makefile -->
