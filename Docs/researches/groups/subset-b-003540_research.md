# subset-b-003540 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu14/smu_v14_0_2_ppt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu14/smu_v14_0_2_ppt.c

## Purpose

This file is the SMU v14.0.2 power-play table implementation for AMDGPU SWSMU. It binds the generic `smu_context` to ASIC-specific firmware messages, clock IDs, feature IDs, table IDs, workload IDs, overdrive limits, fan controls, metrics formats, I2C transport, BACO, reset, and power-limit behavior. The external entry point is `smu_v14_0_2_set_ppt_funcs()`, which installs `smu_v14_0_2_ppt_funcs`, maps common SMU enums to v14.0.2 firmware constants, records `SMU14_DRIVER_IF_VERSION_SMU_V14_0_2`, and initializes the MP1 message mailbox.

## Important APIs, Types, And Tables

Important static maps are `smu_v14_0_2_message_map`, `smu_v14_0_2_clk_map`, `smu_v14_0_2_feature_mask_map`, `smu_v14_0_2_table_map`, `smu_v14_0_2_pwr_src_map`, `smu_v14_0_2_workload_map`, and `smu_v14_0_2_throttler_map`. They define the ABI between common power-management code and PMFW. `PPTable_t`, `SkuTable_t`, `CustomSkuTable_t`, `SmuMetricsExternal_t`, `SmuMetrics_t`, `OverDriveTableExternal_t`, `Watermarks_t`, `SwI2cRequest_t`, `EccInfoTable_t`, and `DpmActivityMonitorCoeffIntExternal_t` are the main firmware-facing table formats.

The key functions are `smu_v14_0_2_setup_pptable()`, `smu_v14_0_2_tables_init()`, `smu_v14_0_2_init_smc_tables()`, `smu_v14_0_2_set_default_dpm_table()`, `smu_v14_0_2_get_smu_metrics_data()`, `smu_v14_0_2_read_sensor()`, `smu_v14_0_2_emit_clk_levels()`, `smu_v14_0_2_force_clk_levels()`, `smu_v14_0_2_update_pcie_parameters()`, `smu_v14_0_2_get_gpu_metrics()`, the OD helpers, the power-profile helpers, the I2C adapter callbacks, and reset/BACO helpers.

## Control Flow

Initialization sets every feature as allowed, fetches the combined PPTABLE from PMFW unless running as an SR-IOV VF, copies the embedded SMC PPT into `driver_pptable`, and derives driver policy from platform caps. Table initialization declares the VRAM/GTT-backed SMU tables, allocates CPU-side metrics, watermarks, ECC, overdrive, and GPU-metrics caches, allocates a `struct smu_14_0_dpm_context`, and then delegates common SMC table allocation to `smu_v14_0_init_smc_tables()`.

At DPM setup, each clock domain chooses either firmware DPM levels via `smu_v14_0_set_single_dpm_table()` or a one-entry boot-value fallback. GFX maximum reporting is clamped to `DriverReportedClocks.GameClockAc` when present. Sensor and sysfs clock reads flow through `smu_cmn_get_metrics_table()` and `smu_v14_0_2_get_smu_metrics_data()`, which translates SMU metrics fields into AMDGPU sensor units. Clock forcing converts a level mask into min/max table entries and sends soft frequency limits. PCIe parameter updates build levels from `SkuTable` and issue `SMU_MSG_OverridePcieParameters` when driver policy or platform caps require clamping.

Overdrive control loads boot/user/runtime tables, validates requested fields against `OverDriveLimitsBasicMin/Max`, marks the relevant `FeatureCtrlMask` bits for one upload, and then clears/caches user-visible settings after a successful `SMU_TABLE_OVERDRIVE` transfer. Power profile custom mode reads and rewrites `SMU_TABLE_ACTIVITY_MONITOR_COEFF`; compute workloads disable deep sleep before setting the workload mask. The I2C path registers `MAX_SMU_I2C_BUSES` Linux adapters and turns `i2c_msg` byte streams into `SwI2cRequest_t` commands transferred through `SMU_TABLE_I2C_COMMANDS`.

## State And Persistence

Persistent runtime state lives in `smu->smu_table` allocations, `smu->smu_dpm.dpm_context`, `smu->pstate_table`, `smu->user_dpm_profile`, `smu->custom_profile_params`, `adev->pm.od_feature_mask`, `adev->unique_id`, BACO state, and the registered I2C adapters. Metrics are cached in `metrics_table` through common SMU cache timing; GPU metrics are cached with `SMU_GPU_METRICS_CACHE_INTERVAL`. User overdrive settings are preserved across S3/S4/runpm resume by copying boot defaults and then restoring saved user fields when `adev->in_suspend` and `user_od` are true. Power-limit state is tracked in `smu->current_power_limit`.

## Dependencies And Integration Points

The file depends on common v14 helpers from `smu_v14_0.*`, the common SMU layer in `smu_cmn`, AMDGPU ATOM/VBIOS data, MP1 register definitions, RAS interrupt state, Linux I2C, firmware table formats from `smu14_driver_if_v14_0.h` and `smu_v14_0_2_pptable.h`, and PMFW message IDs from `smu_v14_0_2_ppsmc.h`. It integrates with sysfs power and clock reporting, pp_od_clk_voltage editing, power profiles, thermal policy, BACO/runpm, reset recovery, FRU/RAS EEPROM access over SMU I2C, and MP1 unload/DF C-state messaging.

## Risks And Edge Cases

`smu_v14_0_2_is_mode1_reset_supported()` unconditionally returns true with a TODO, and `smu_v14_0_2_mode2_reset()` is still a TODO returning success; callers may believe unsupported reset paths worked. `smu_v14_0_2_init_smc_tables()` does not unwind `tables_init()` if DPM context allocation or common initialization later fails. I2C request construction increments `NumCmds` for every byte and relies on adapter quirks to keep transfers within `MAX_SW_I2C_COMMANDS`; bypasses could overflow firmware command capacity. Some OD format strings print signed minima with unsigned formatting. Power-limit OD writes depend on `msg_limit` and `od_enabled`; bad PPTABLE data could expose invalid limits. Sensor paths return `UINT_MAX` for unknown metrics members, so callers must distinguish unsupported sensors from firmware-returned maximum values.

## Test Signals

Useful validation includes booting an IP 14.0.2 board with PMFW table retrieval, checking `pp_dpm_*` and `gpu_metrics` sysfs output, changing performance levels and workload profiles, editing and restoring OD fan/GFX/UCLK/PPT fields, testing suspend/resume OD persistence, forcing PCIe caps with and without `PP_PCIE_DPM_MASK`, exercising FRU/RAS EEPROM reads through SMU I2C, triggering RAS interrupt paths, and verifying BACO/runpm audio-function transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu14/smu_v14_0_2_ppt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu14/smu_v14_0_2_ppt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu14/smu_v14_0_2_ppt.h

## Purpose

This header is the public SMU v14.0.2 PPT hook declaration. It exposes `smu_v14_0_2_set_ppt_funcs(struct smu_context *smu)` so the AMDGPU SMU device selection path can install the v14.0.2-specific `pptable_funcs`, message map, feature map, table map, power-source map, workload map, driver interface version, and mailbox configuration implemented in `smu_v14_0_2_ppt.c`.

## Important APIs, Types, And Control Flow

The only API is the `extern` setter. The header intentionally does not include implementation details or local table types; it relies on users already seeing `struct smu_context` from the surrounding SWSMU headers. Control flow is one-way: ASIC discovery or SMU initialization includes this header, calls the setter for IP 14.0.2, and then uses the function pointers stored in the SMU context.

## State, Dependencies, And Integration

The header has no storage or persistence. Its include guard, `__SMU_V14_0_2_PPT_H__`, prevents duplicate declarations. It is coupled to the C implementation and to the global SWSMU initialization contract that each ASIC PPT module exports a `*_set_ppt_funcs()` symbol.

## Risks And Test Signals

The main risk is declaration drift: if the C implementation changes the function signature or symbol name, the IP selection path will fail at compile or link time. Build coverage for the AMDGPU SWSMU smu14 objects is the primary test signal; runtime coverage is any successful initialization that reaches the v14.0.2 setter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu14/smu_v14_0_2_ppt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu15/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu15/Makefile

## Purpose

This Makefile adds the SMU15 manager objects to the AMDGPU powerplay build. It defines the local object list for the SMU v15 subdirectory and appends the source-tree-qualified object paths to `AMD_POWERPLAY_FILES`, which the parent AMDGPU build includes.

## Important Variables And Control Flow

`SMU15_MGR` contains `smu_v15_0.o`, `smu_v15_0_0_ppt.o`, and `smu_v15_0_8_ppt.o`. `AMD_SWSMU_SMU15MGR` prefixes those objects with `$(AMD_SWSMU_PATH)/smu15/`. The final line appends that list to `AMD_POWERPLAY_FILES`. There are no conditional branches in this file, so all three objects are part of the configured SMU15 manager build whenever this Makefile is included by the parent AMDGPU make logic.

## State, Dependencies, And Integration

The file has no runtime state. It depends on parent make variables `AMD_SWSMU_PATH` and `AMD_POWERPLAY_FILES`. It integrates the common v15 support file and both IP-specific PPT implementations into the same driver object set, allowing runtime ASIC selection code to call the appropriate `smu_v15_0_0_set_ppt_funcs()` or `smu_v15_0_8_set_ppt_funcs()` symbol.

## Risks And Test Signals

Object-list omissions would produce unresolved symbols or unsupported ASIC paths at runtime. Adding a new SMU15 PPT implementation requires updating this list. Test signals are kernel build success, link success for AMDGPU, and runtime availability of SMU15 initialization on IP 15.0.0 and 15.0.8 devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu15/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu15/smu_v15_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu15/smu_v15_0.c

## Purpose

This is the common SMU v15 support layer used by SMU15 PPT implementations. It handles firmware acquisition/loading, soft PPTABLE source selection, common SMC table memory lifetimes, VBIOS boot-value parsing, driver/tool/memory-pool table address notification, feature-mask programming, generic power limits, clock limit messages, DPM table queries, performance-level transitions, media block power control, deep sleep and ULV feature toggles, BACO/BAMACO state control, thermal/MP1 IRQ registration, reset-complete event handling, and generic overdrive clock editing.

## Important APIs And Types

Exported functions include `smu_v15_0_init_microcode()`, `smu_v15_0_fini_microcode()`, `smu_v15_0_load_microcode()`, `smu_v15_0_init_pptable_microcode()`, `smu_v15_0_check_fw_status()`, `smu_v15_0_get_pptable_from_firmware()`, `smu_v15_0_setup_pptable()`, `smu_v15_0_init_smc_tables()`, `smu_v15_0_fini_smc_tables()`, `smu_v15_0_init_power()`, `smu_v15_0_fini_power()`, `smu_v15_0_get_vbios_bootup_values()`, address setters, feature controls, DPM helpers, media enable helpers, BACO helpers, `smu_v15_0_set_performance_level()`, `smu_v15_0_od_edit_dpm_table()`, and thermal alert helpers. It uses `smu_context`, `amdgpu_device`, firmware header structs, ATOM firmware info structs, `smu_15_0_dpm_context`, SMU table contexts, `smu_msg_args`, and AMDGPU IRQ source structures.

## Control Flow

Firmware initialization skips SR-IOV VFs, decodes the MP1 firmware prefix, requests `amdgpu/<prefix>.bin`, records the PM firmware version, and registers SMC firmware with PSP loading when applicable. Direct loading writes firmware dwords to MP1 SRAM and waits for the firmware interrupt-enabled flag. PPTABLE setup chooses between VBIOS and firmware tables based on SR-IOV state, emulator mode, boot `pp_table_id`, and optional `amdgpu_smu_pptable_id`; firmware tables support SMC header v2.0 and v2.1 entry tables.

Common table initialization allocates `driver_pptable`, max sustainable clocks, optional overdrive/boot/user OD tables, and `combo_pptable`; finalization frees those plus metrics, watermarks, ECC, DPM contexts, golden contexts, and power-state allocations. Boot-value parsing reads ATOM `firmwareinfo` and optional `smu_info` revisions to fill boot clocks, voltages, cooling ID, and PPTABLE ID. Runtime helpers send mailbox messages either through `smu_cmn_send_smc_msg*()` or directly through `smu->msg_ctl.ops->send_msg()` with multi-argument payloads.

Performance-level control computes per-clock min/max targets from DPM tables and UMD pstate values, then sends soft limits for GFX, UCLK, SOCCLK, VCLK/DCLK per unharvested VCN instance, and FCLK. BACO state control sends enter/exit messages and updates `smu_baco->state`; exit also clears VBIOS scratch registers for reinitialization. IRQ handling enables MP1 software interrupts and THM thermal interrupts, processes high/low thermal events, and schedules delayed software CTF work.

## State And Persistence

The file mutates firmware pointers, `adev->pm.fw_version`, PSP firmware size accounting, `smu->pptable_firmware`, `smu->smu_table.boot_values`, SMC table allocations, `smu_power.power_context`, DPM/current pstate bounds, `smu->current_power_limit`, `smu_baco->state`, IRQ source setup, and OD fine-grain GFX min/max fields. Most state is in-memory driver state and is reconstructed on device init/resume; firmware and VBIOS data are persistent external inputs.

## Dependencies And Integration Points

It depends on AMDGPU firmware helpers, PSP firmware loading, ATOMBIOS table readers, MP1/THM register definitions, common SWSMU message helpers, RAS/IRQ infrastructure, VCN/JPEG harvest metadata, BACO runpm policy, and global module parameters such as `amdgpu_smu_pptable_id` and `amdgpu_emu_mode`. ASIC-specific PPT files call these helpers from their `pptable_funcs`.

## Risks And Edge Cases

`smu_v15_0_load_microcode()` only assigns `mp1_fw_flags` inside `if (smu->is_apu)`, leaving non-APU direct-load behavior dependent on an uninitialized local if ever used. Many helpers return success when DPM is disabled, which is intentional for fallback but can hide missing feature enablement. Firmware PPTABLE parsing rejects non-v2 headers and unknown v2 minors. `smu_v15_0_init_smc_tables()` requires table sizes to be initialized by the ASIC file before allocation. OD editing only supports SCLK min/max and only in manual mode. IRQ register selection differs for APUs and dGPUs, so wrong `smu->is_apu` setup can mask or misroute interrupts.

## Test Signals

Build and boot tests should cover PSP and non-PSP firmware paths, SR-IOV VF bypass, VBIOS and firmware PPTABLE selection, ATOM firmware revisions 3.1, 3.3, 3.4, SMU info revisions 3.6 and 4.0, DPM table reads, forced performance levels, VCN/JPEG power toggles, BACO enter/exit, thermal interrupt handling, OD manual edits, and power-limit get/set sysfs paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu15/smu_v15_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu15/smu_v15_0_0_ppt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu15/smu_v15_0_0_ppt.c

## Purpose

This file is the SMU v15.0.0 ASIC-specific PPT implementation, marked as an APU path in `smu_v15_0_0_set_ppt_funcs()`. It defines the PMFW message map, feature map, table map, mailbox registers, SMU table transfers, metrics decoding, DPM clock handling, watermarks, performance levels, mode2 reset, and block power controls for IP 15.0.0.

## Important APIs, Types, And Tables

The installed `pptable_funcs` include `init_smc_tables`, `fini_smc_tables`, `get_vbios_bootup_values`, `system_features_control`, VCN/JPEG enable, `set_default_dpm_table`, `read_sensor`, `is_dpm_running`, `set_watermarks_table`, `get_gpu_metrics`, `get_enabled_mask`, `gfx_off_control`, `mode2_reset`, `get_dpm_ultimate_freq`, `od_edit_dpm_table`, `emit_clk_levels`, `force_clk_levels`, `set_performance_level`, fine-grain GFX initialization, IMU power-up, VPE/UMSCH power control, and DPM clock table export. Key firmware formats are `SmuMetrics_t`, `DpmClocks_t`, `Watermarks_t`, and `struct gpu_metrics_v3_0`.

## Control Flow

Initialization declares watermarks, DPM clocks, and metrics SMU tables, allocates CPU copies, and initializes a driver GPU metrics cache. Default DPM setup fetches `SMU_TABLE_DPMCLOCKS` from PMFW via `smu_v15_0_0_update_table()`, which copies through the shared driver table, flushes or invalidates HDP around transfers, and sends three-argument table-transfer mailbox messages. Metrics reads are cached for roughly one millisecond and decoded into sensor values, including firmware-version-specific scaling for `GfxActivity`.

DPM query paths read from the `DpmClocks_t` cache. GFX uses min/max fields; SOC, VCN, memory, and FCLK use enabled level counts and arrays. `emit_clk_levels()` prints OD range, OD SCLK, GFX pseudo-levels, or per-level tables. Clock forcing resolves mask endpoints to frequencies and sends soft min/max messages for SOC, FCLK, VCLK, and DCLK. Performance-level control computes high, low, auto, and profile clocks, then sends soft limits for SCLK, FCLK, SOCCLK, VCLK/VCLK1, and DCLK/DCLK1. Watermark updates translate display-provided reader/writer ranges into PMFW watermarks and upload them once.

## State And Persistence

State lives in `smu_table->metrics_table`, `clocks_table`, `watermarks_table`, the GPU metrics driver table, `smu->watermarks_bitmap`, `smu->gfx_default_hard_min_freq`, `smu->gfx_default_soft_max_freq`, and current actual GFX min/max fields. The mailbox setup stores MP1 C2PMSG 30-34 registers and allows up to three argument registers. `smu->is_apu` is set true and changes common v15 behavior such as firmware status register handling and media power messages.

## Dependencies And Integration Points

This file depends on `smu_v15_0.*` common helpers, `smu15_driver_if_v15_0_0.h`, `smu_v15_0_0_ppsmc.h`, `smu_v15_0_0_pmfw.h`, HDP cache helpers, display watermark structures, common GPU metrics initialization, VPE/UMSCH power management, and AMDGPU sysfs sensor/clock/OD entry points. It integrates as the IP 15.0.0 function table selected by the SMU initialization path.

## Risks And Edge Cases

`smu_v15_0_common_get_dpm_freq_by_index()`, `smu_v15_0_common_get_dpm_ultimate_freq()`, `smu_v15_0_common_get_dpm_level_count()`, `smu_v15_0_common_set_fine_grain_gfx_freq_parameters()`, and `smu_v15_0_common_get_dpm_table()` ignore return values from their underlying helpers and return success, which can hide invalid clock types or failed table reads. `smu_v15_0_0_set_soft_freq_limited_range()` does not support UCLK even though some higher-level code reasons about memory clocks. VCLK1/DCLK1 are explicitly skipped by common ultimate-frequency wrappers, so profile code may silently leave them zero. Metrics unit scaling changes by firmware version, which is fragile without broad PMFW coverage. `system_features_control(false)` only prepares MP1 for unload outside S0ix and does not disable all features.

## Test Signals

Test with IP 15.0.0 boot, `gpu_metrics` v3.0 reads, all supported sensors, display watermark programming, `pp_dpm_*` clock listings, forced levels high/low/auto/profile, OD manual SCLK min/max editing, mode2 reset, VCN/JPEG/VPE/UMSCH power toggles, GFXOFF allow/disallow, and suspend/S0ix unload behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu15/smu_v15_0_0_ppt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu15/smu_v15_0_0_ppt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu15/smu_v15_0_0_ppt.h

## Purpose

This header declares the SMU v15.0.0 PPT installation function, `smu_v15_0_0_set_ppt_funcs(struct smu_context *smu)`. It is the public handoff between ASIC/IP selection code and the IP 15.0.0-specific implementation in `smu_v15_0_0_ppt.c`.

## Important APIs, Types, And Control Flow

The only symbol is the setter. Callers pass a populated `struct smu_context`; the implementation installs the v15.0.0 `pptable_funcs`, feature map, table map, marks the SMU as APU, records `SMU15_DRIVER_IF_VERSION_SMU_V15_0`, and configures MP1 mailbox registers. The header itself has no direct dependency on the table or PMFW types used by the implementation.

## State, Dependencies, And Integration

The header owns no state. The include guard `__SMU_V15_0_0_PPT_H__` prevents redeclaration. It depends on the broader SWSMU convention that each PPT implementation exposes one setter used by runtime ASIC dispatch and by build-time linkage from the smu15 Makefile.

## Risks And Test Signals

The risk surface is declaration/linkage drift. A mismatch between this header, the C file, and callers will show up as compile or link failures. Runtime test signals are successful IP 15.0.0 SMU initialization and evidence that the v15.0.0 function table, feature map, table map, and mailbox registers were selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu15/smu_v15_0_0_ppt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu15/smu_v15_0_8_ppt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu15/smu_v15_0_8_ppt.c

## Purpose

This file is the SMU v15.0.8 PPT implementation for a large multi-die/discrete platform with extended PM metrics, system metrics, FRU/product data, XGMI data, RAS-related messages, fast PPT limits, and board temperature metrics. `smu_v15_0_8_set_ppt_funcs()` installs the function table, clock/feature/table maps, MP1 mailbox, temperature metric callbacks, and `SMU15_DRIVER_IF_VERSION_SMU_V15_0_8`.

## Important APIs, Types, And Tables

Important maps are `smu_v15_0_8_message_map`, `smu_v15_0_8_clk_map`, `smu_v15_0_8_feature_mask_map`, and `smu_v15_0_8_table_map`. Important table types are `MetricsTable_t`, `StaticMetricsTable_t`, `SystemMetricsTable_t`, `PPTable_t`, `struct smu_v15_0_8_gpu_metrics`, `struct smu_v15_0_8_baseboard_temp_metrics`, and `struct smu_v15_0_8_gpuboard_temp_metrics`. Main functions include table initialization/finalization, metrics retrieval, static metrics to driver PPTABLE conversion, DPM table setup, sensor reads, GPU/system/temp metrics export, power-limit handlers, fast PPT handlers, IRQ handling, mode2 reset, OD editing, and performance-level handling.

## Control Flow

Table initialization declares PMSTATUSLOG, SMU metrics, and PMFW system metrics tables, allocates driver PPTABLE and metrics CPU buffers with cleanup attributes, initializes GPU/baseboard/GPU-board driver metric caches, initializes a cached system metrics table, and creates a metrics mutex. It also allocates `smu_15_0_dpm_context` and DPM policy storage. Finalization tears down driver metric caches, the system metrics cache, the mutex, and then delegates broader allocation cleanup to common v15 finalization.

Unlike v14 and v15.0.0, `setup_pptable()` is mostly a placeholder and the driver PPTABLE is synthesized later from PMFW static metrics in `smu_v15_0_8_set_driver_pptable()`. That path fetches the static metrics table, records the metrics version, converts Q10 firmware values into integer clocks/power/thermal limits, populates public serial numbers and AMDGPU UID records for SOC/MID/AID/XCD, copies FRU product strings, stores PPT1 fast-limit bounds, PLDM version, board input voltage, and XGMI max speed/width. `set_default_dpm_table()` then builds fine-grained GFX/FCLK/GL2 and discrete UCLK tables plus fixed SOC/VCLK/DCLK entries from the synthesized PPTABLE.

Metrics reads send `GetMetricsTable`, invalidate HDP, copy from the driver table, and cache under `metrics_lock`; system metrics use a separate cache buffer and PMFW command. Sensor reads expose GPU/memory activity, input power, hotspot/HBM temperatures, board voltage, and node power manager values. GPU metrics export fills per-XCC, per-MID, per-AID, per-VCN, HBM, throttling residency, XGMI, and activity accumulator fields. Temperature metric callbacks expose baseboard data only for physical node 0 and GPU board data for all nodes.

Performance and OD control are deliberately narrow. Manual mode permits GFX min/max and UCLK max edits; auto mode restores default GFX range and UCLK max. Fast PPT limit support validates `PPT1Min/Max` before sending `SetFastPptLimit`; normal PPT falls back to common v15. Mode2 reset sends an async reset message, waits 200 ms, then polls for an ACK under the message lock.

## State And Persistence

The file persists runtime state in `driver_pptable->init`, synthesized PPTABLE fields, `metrics_table`, system metrics cache, driver metric caches, DPM tables, DPM policies, `smu->pstate_table` current/custom bounds, `dpm_context->board_volt`, `adev->unique_id`, `adev->fru_info`, `adev->firmware.pldm_version`, UID records, XGMI max data, IRQ source setup, and throttle status used by delayed logging. Metrics caches are time-based; static PPTABLE synthesis is guarded by `pptable->init` so it happens once per allocation lifetime.

## Dependencies And Integration Points

This file depends on v15 common helpers, PMFW headers for v15.0.8, MP1 register definitions, AMDGPU FRU and UID helpers, XGMI topology helpers, UMC active masks, RAS/throttle interrupt handling, SMU table cache helpers, Q10 metric conversions, and AMDGPU sysfs metric/sensor/OD/performance interfaces. It also exposes RAS-priority message mappings for MCA and bad-page PMFW commands used elsewhere through the common SMU message layer.

## Risks And Edge Cases

`smu_v15_0_8_clk_map` only maps UCLK and carries a TODO, so common clock-to-ASIC translation is incomplete for this ASIC. `setup_pptable()` is a placeholder; callers must reach `set_default_dpm_table()` before any logic depends on synthesized PPTABLE values. `smu_v15_0_8_get_enabled_mask()` comments mention 128 feature bits but requests only two out args and converts the default feature count, which may miss higher feature bits. `smu_v15_0_8_get_gpu_metrics()` sets `mid_mask` from `adev->aid_mask`, which may be suspicious if MID and AID masks diverge. HBM stack iteration mutates a local mask by nibbles and assumes active-mask grouping is valid. Manual OD rejects `min >= max`, which can prevent setting a single fixed GFX frequency. Several paths return `-EOPNOTSUPP` for unsupported deterministic/profile levels or missing PPT1 data, so UI callers need graceful fallback.

## Test Signals

Useful tests include IP 15.0.8 boot, static metrics/PPTABLE synthesis, FRU product export, UID population for SOC/MID/AID/XCD, XGMI speed/width publication, `gpu_metrics` v1.9 reads with populated multi-instance arrays, raw PM metrics header sizing, baseboard and GPU-board temp metric reads on node 0 and nonzero nodes, HBM temperature calculation with several UMC masks, fast PPT get/set bounds, normal PPT get/set, manual OD GFX/UCLK edits, auto restore, mode2 reset ACK timing, MP1 throttle interrupt logging, and SR-IOV/multi-VF thermal-range bypass behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu15/smu_v15_0_8_ppt.c -->
