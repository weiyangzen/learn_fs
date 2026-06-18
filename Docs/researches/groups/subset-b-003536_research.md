# Research: subset-b-003536

Grouped research for AMDGPU SWSMU SMU11, SMU12, and SMU13 power-management implementation files. Each section preserves the exact source path in its title and is bounded for reconciliation into source-tree-aligned per-file outputs.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/smu_v11_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/smu_v11_0.c

## Purpose

`smu_v11_0.c` is the common SMU11 support layer for AMDGPU SWSMU devices. It handles MP1 firmware loading/status, PowerPlay table discovery, common SMU table allocation/freeing, VBIOS boot clock extraction, SMU message register setup, DPM clock and power-limit helpers, GFXOFF, fan control, thermal/SMU interrupts, BACO/BAMACO, mode resets, PCIe link reporting, and deep-sleep/ULV feature toggles. ASIC-specific SMU11 policy files, such as `vangogh_ppt.c`, bind these helpers through their `pptable_funcs`.

## Important APIs, Types, and Functions

The file exports common routines including `smu_v11_0_init_microcode`, `smu_v11_0_load_microcode`, `smu_v11_0_check_fw_status`, `smu_v11_0_setup_pptable`, `smu_v11_0_init_smc_tables`, `smu_v11_0_fini_smc_tables`, `smu_v11_0_init_power`, `smu_v11_0_get_vbios_bootup_values`, `smu_v11_0_notify_memory_pool_location`, `smu_v11_0_set_driver_table_location`, `smu_v11_0_set_tool_table_location`, `smu_v11_0_set_allowed_mask`, `smu_v11_0_system_features_control`, `smu_v11_0_init_max_sustainable_clocks`, `smu_v11_0_get_current_power_limit`, `smu_v11_0_set_power_limit`, fan helpers, `smu_v11_0_register_irq_handler`, BACO helpers, reset helpers, DPM frequency helpers, and `smu_v11_0_init_msg_ctl`.

Important local helpers include `smu_v11_0_set_pptable_v2_0`, `smu_v11_0_set_pptable_v2_1`, `smu_v11_0_atom_get_smu_clockinfo`, `smu_v11_0_get_max_sustainable_clock`, `smu_v11_0_set_irq_state`, `smu_v11_0_irq_process`, and `convert_to_vddc`.

Key state structures are `struct smu_context`, `struct amdgpu_device`, `struct smu_table_context`, `struct smu_power_context`, `struct smu_dpm_context`, `struct smu_baco_context`, `struct smu_msg_ctl`, `struct smu_table`, and `struct smu_feature`.

## Control Flow

Firmware bring-up requests an SMC firmware blob based on the MP1 IP version unless an SR-IOV VF uses PSP-managed firmware for selected SMU11 variants. PSP load mode registers the firmware in `adev->firmware.ucode`; direct loading writes the firmware words into MP1 SRAM, toggles MP1 reset, and polls `MP1_FIRMWARE_FLAGS.INTERRUPTS_ENABLED` until firmware is alive.

PowerPlay table setup prefers a driver-provided soft PPTABLE from the SMC firmware header when a v2 firmware header and nonzero `pp_table_id` are present. Otherwise it falls back to the VBIOS `powerplayinfo` ATOM table, then records `power_play_table` and size in `smu->smu_table`.

Table initialization allocates driver PPTABLE, max sustainable clocks, and optional overdrive copies based on `tables[SMU_TABLE_*].size`; finalization frees all common SMU tables, metrics/watermark/config/ECC buffers, DPM contexts, power-state objects, and resets cache timestamps and sizes.

Runtime control mostly routes high-level requests into SMU messages. Frequency helpers map common clocks to ASIC-specific IDs and send `GetMinDpmFreq`, `GetMaxDpmFreq`, `SetSoftMinByFreq`, `SetSoftMaxByFreq`, `SetHardMinByFreq`, and `SetHardMaxByFreq`. Power-limit helpers map AC/DC power source to firmware encoding and pack source/controller/limit fields into `GetPptLimit` and `SetPptLimit` parameters. GFXOFF helpers gate on MP1 IP version and `PP_GFXOFF_MASK` before sending allow/disallow messages.

Interrupt control programs THM thermal thresholds, clears/enables THM interrupt bits, configures MP1 software interrupts, and registers THM high/low, SMUIO GPIO19 CTF, and MP1 SMU-to-host interrupt IDs. Processing schedules delayed software CTF work, powers off on hardware CTF, updates AC/DC state and ACK work, and counts/logs thermal throttling.

BACO enter/exit handles ASIC-specific sequences: newer Navi-family variants use `EnterBaco` message parameters for BACO/BAMACO, Arcturus writes a different THM BACO register, RAS/XGMI conditions select different firmware parameters, and exit clears BIOS scratch registers then polls BACO exit status.

## State and Persistence Behavior

Persistent driver state includes `adev->pm.fw`, `adev->pm.fw_version`, `adev->firmware.fw_size`, boot values under `smu_table.boot_values`, allocated table pointers, DPM contexts, `smu_power.power_context`, `smu_baco.state`, `smu->current_power_limit`, user overdrive/fan profile fields, `adev->pm.ac_power`, and `smu->hard_min_uclk_req_from_dal`.

Hardware state is changed through MP1 SRAM/SMN registers, MP1 C2P message registers, SMUIO voltage telemetry registers, THM fan/thermal/BACO registers, PCIe link registers, BIOS scratch registers, and SMU firmware-managed DPM, feature, PPT, and BACO state. Many writes persist until reset, suspend/resume, BACO exit, or later SMU messages.

## Dependencies

The file depends on AMDGPU core objects, ATOMBIOS/VBIOS helpers, firmware loader APIs, SOC15 register helpers, SMU common helpers (`smu_cmn_*`), SMU message ops (`smu_msg_v1_ops`), THM/MP/SMUIO generated register headers, RAS state, IRQ infrastructure, delayed/workqueue APIs, and kernel allocation/time/reboot helpers.

## Integration Points

ASIC-specific SMU11 PPT files call these helpers through `pptable_funcs`, especially for firmware status, table lifecycle, power context, IRQs, memory/table address notification, GFXOFF, power limits, VBIOS boot values, resets, and message control initialization. Display code consumes max sustainable clocks and display clock voltage requests. Runtime PM and reset code use BACO/BAMACO and mode-reset helpers. Sysfs/hwmon paths consume fan, power, and DPM helpers.

## Risks and Edge Cases

Firmware header version handling is strict; malformed or unsupported SMC firmware tables cause PPTABLE setup failures. Direct firmware loading skips the first and last firmware dwords and assumes MP1 SRAM semantics. Many clock values convert from 10 kHz to MHz or kHz, so unit mistakes can overconstrain DPM. Power-limit parameters truncate the limit to 16 bits. Fan tach/PWM code guards zero divisors but still depends on THM register availability and ASIC fan wiring. BACO paths vary by MP1 IP version, RAS, SR-IOV, and runtime PM mode; incorrect selection can leave the ASIC in an unresponsive state. Hardware CTF interrupt handling calls `orderly_poweroff(true)`, so false positives are severe.

## Test Signals

Build coverage should include all SMU11 ASIC-specific policy users. Runtime signals include firmware request/load success, `check_fw_status` passing, VBIOS and driver PPTABLE selection logs, successful SMU table transfer, sysfs DPM level reads/writes, fan PWM/RPM reads/writes, thermal interrupt registration and throttling logs, AC/DC transition handling, GFXOFF allow/disallow behavior, BACO enter/exit, mode1/mode2 reset, suspend/resume table reinitialization, and PCIe link reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/smu_v11_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/vangogh_ppt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/vangogh_ppt.c

## Purpose

`vangogh_ppt.c` implements the Vangogh APU-specific SMU11.5 PowerPlay table policy layer. It maps common SMU abstractions to Vangogh firmware messages, features, tables, workloads, metrics, DPM clocks, sensors, overdrive, watermarks, GFXOFF, power limits, and post-init WGP power-saving behavior, then installs those callbacks with `vangogh_set_ppt_funcs`.

## Important APIs, Types, and Functions

The central API is `vangogh_set_ppt_funcs`, which assigns `vangogh_ppt_funcs`, feature/table/workload maps, marks `smu->is_apu = true`, sets `SMU13_DRIVER_IF_VERSION`, and initializes SMU11 message control with `vangogh_message_map`.

Important functions include `vangogh_tables_init`, `vangogh_init_smc_tables`, `vangogh_dpm_set_vcn_enable`, `vangogh_dpm_set_jpeg_enable`, `vangogh_is_dpm_running`, `vangogh_common_get_smu_metrics_data`, `vangogh_common_emit_clk_levels`, `vangogh_get_dpm_ultimate_freq`, `vangogh_set_power_profile_mode`, `vangogh_set_soft_freq_limited_range`, `vangogh_force_clk_levels`, `vangogh_set_performance_level`, `vangogh_read_sensor`, `vangogh_set_watermarks_table`, `vangogh_common_get_gpu_metrics`, `vangogh_od_edit_dpm_table`, `vangogh_set_default_dpm_tables`, `vangogh_set_fine_grain_gfx_freq_parameters`, `vangogh_post_smu_init`, `vangogh_mode2_reset`, GFXOFF residency/entry helpers, and Vangogh-specific power-limit helpers.

Important firmware data types include `SmuMetrics_t`, `SmuMetrics_legacy_t`, `DpmClocks_t`, `Watermarks_t`, `DpmActivityMonitorCoeffExt_t`, `struct gpu_metrics_v2_2`, `v2_3`, `v2_4`, and `struct smu_11_5_power_context`.

## Control Flow

Initialization registers SMU tables for watermarks, DPM clocks, PM status log, activity monitor coefficients, and SMU metrics, then allocates CPU-side metrics, watermarks, clocks, GPU metrics cache, and a SMU11 DPM context. CPU core count comes from x86 topology when available.

Metrics reads branch on `smu->smc_fw_if_version`: legacy firmware uses `SmuMetrics_legacy_t`, newer firmware uses nested current/average `SmuMetrics_t`. GPU metrics selection also branches on SMU program/version to expose v2.2, v2.3, or v2.4 layouts.

DPM clock queries read `DpmClocks_t`, with reverse indexing for FCLK/MCLK DF pstates. GFXCLK is treated as fine-grained min/current/max rather than a full DPM table. Soft range setting sends clock-specific min/max messages; VCN combines VCLK into high 16 bits and DCLK into low 16 bits of VCN parameters.

Performance-level control resets CPU soft limits, sets GFX hard min/soft max according to high/low/auto/profile modes, optionally forces FCLK/SOCCLK/VCN DPM levels, and for firmware `>= 0x43f1b00` sends per-core CCLK soft min/max messages. Manual overdrive edits only stage values until commit sends GFX and optional CPU CCLK constraints.

Post-init enables GFXOFF when GFX DPM and power gating are available; otherwise it clears `PP_GFXOFF_MASK`. It then optionally requests active WGP count based on CU count and `RLC_PG_ALWAYS_ON_WGP_MASK`.

Watermark setup validates reader/writer counts, copies DC ranges into the firmware watermark table, and uploads once by tracking `WATERMARKS_EXIST` and `WATERMARKS_LOADED`.

## State and Persistence Behavior

The file stores allocated tables in `smu->smu_table`, CPU core count and selected CPU core ID in `smu`, actual/default GFX and CPU frequency limits, watermark load bitmap, Vangogh power limits under `struct smu_11_5_power_context`, cached GFXOFF residency/entry count in `adev->gfx`, and cached GPU metrics via `SMU_DRIVER_TABLE_GPU_METRICS`.

Firmware state changes include VCN/JPEG power state, active workload mask, soft/hard clock ranges, CPU CCLK ranges, GFXOFF enable/allow/disallow/residency logging, WGP active requests, watermarks, thermal limit, fast/slow PPT limits, and asynchronous mode2 reset.

## Dependencies

Dependencies include SMU11 common helpers, Vangogh firmware interface headers, SMU11.5 PPSMC/PMFW message IDs, GC 10.3 RLC register headers, CPU topology on x86, `smu_cmn_*` table/message helpers, `sysfs_emit_at`, KIQ register reads, and AMDGPU PM/DPM state.

## Integration Points

The `pptable_funcs` table integrates with the AMDGPU powerplay framework for sensors, GPU metrics, DPM sysfs, watermarks from DC, multimedia power gating, GFXOFF accounting, runtime reset, thermal limit, PPT limit, and VBIOS boot values. It reuses `smu_v11_0.c` for common firmware status, IRQ handling, table finalization, memory/table location, power context, and VBIOS parsing.

## Risks and Edge Cases

Legacy/new metrics layout selection is firmware-version sensitive; using the wrong layout corrupts sensor values. CPU overdrive accepts only firmware that supports CCLK messages, and the input-size diagnostic text for CPU OD says four parameters while code requires three. Some profile paths call `vangogh_force_clk_levels` without checking every return value. VCN parameter packing differs for VCLK and DCLK. Watermarks upload only once after `WATERMARKS_LOADED`, so later range changes require careful bitmap handling elsewhere. `SMU13_DRIVER_IF_VERSION` is assigned despite this being an SMU11.5 policy, so compatibility depends on the corresponding Vangogh firmware contract.

## Test Signals

Useful validation includes Vangogh boot with both old and new PMFW interfaces, `gpu_metrics` ABI version selection, sensor reads for GPU/VCN load, power, temperatures, CPU clocks, voltage, DPM sysfs clock levels, manual OD edits and commit, GFXOFF enable/status/residency/entry count, VCN/JPEG power-gating during multimedia use, DC watermark programming, WGP power-save request after init, and mode2 reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/vangogh_ppt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/vangogh_ppt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/vangogh_ppt.h

## Purpose

`vangogh_ppt.h` is the public header for the Vangogh SMU11.5 PPT policy implementation. It exposes the policy installation function and Vangogh-specific UMD P-state frequency constants used by `vangogh_ppt.c`.

## Important APIs, Types, and Macros

The only function declaration is `void vangogh_set_ppt_funcs(struct smu_context *smu);`.

Macros define standard, peak, minimum-SCLK, and minimum-MCLK UMD P-state frequencies for GFXCLK, SOCCLK, FCLK, VCLK, and DCLK. It also defines RLC power status message parameters `RLC_STATUS_OFF` and `RLC_STATUS_NORMAL`.

## Control Flow

The header has no executable control flow. Consumers include it to call `vangogh_set_ppt_funcs` during ASIC selection and to use the P-state constants while programming performance profiles.

## State and Persistence Behavior

The header stores no state. Its constants influence persistent firmware state indirectly when `vangogh_ppt.c` sends SMU messages using the defined frequencies or RLC status values.

## Dependencies

The header assumes `struct smu_context` is declared by the including translation unit. It has only an include guard and C preprocessor constants.

## Integration Points

`vangogh_ppt.c` includes this header and uses the UMD P-state macros for performance profile mode, clock level emission, and peak/standard/min profile programming. AMDGPU SMU ASIC setup code can include the header to call `vangogh_set_ppt_funcs`.

## Risks and Edge Cases

These constants encode platform policy. Wrong frequencies can overconstrain clocks, reduce performance, or send unsupported requests to firmware. The min-SCLK and min-MCLK profiles deliberately constrain different clock domains, so swapping constants would change user-visible `power_dpm_force_performance_level` behavior.

## Test Signals

Build coverage catches declaration and macro name drift. Runtime DPM sysfs profile tests should confirm standard, peak, min-SCLK, and min-MCLK modes apply the frequencies expected for Vangogh.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/vangogh_ppt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu12/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu12/Makefile

## Purpose

This Makefile fragment wires SMU12 SWSMU manager objects into the AMDGPU PowerPlay build. It identifies the Renoir policy file and common SMU12 helper file as the SMU12 manager object set.

## Important APIs, Types, and Functions

The file defines `SMU12_MGR = renoir_ppt.o smu_v12_0.o`, derives `AMD_SWSMU_SMU12MGR` by prefixing each object with `$(AMD_SWSMU_PATH)/smu12/`, and appends those objects to `AMD_POWERPLAY_FILES`.

## Control Flow

There is no runtime control flow. During Kbuild evaluation, the object list is expanded and incorporated into the larger AMDGPU powerplay object list.

## State and Persistence Behavior

The Makefile has no runtime state. Its build state effect is that changes to `renoir_ppt.c` or `smu_v12_0.c` participate in AMDGPU builds that include SWSMU powerplay.

## Dependencies

It depends on the parent AMDGPU make context defining `AMD_SWSMU_PATH` and `AMD_POWERPLAY_FILES`. It also assumes the listed `.c` files compile into the named `.o` files.

## Integration Points

The parent AMDGPU driver build includes this fragment when collecting SWSMU manager sources. `renoir_ppt.o` supplies ASIC policy callbacks, while `smu_v12_0.o` supplies common SMU12 helpers consumed by Renoir.

## Risks and Edge Cases

Omitting a required object causes unresolved symbols or missing runtime callbacks for Renoir. Adding an object here without corresponding source/config guards can break builds for all AMDGPU configurations that include SWSMU.

## Test Signals

Kernel build coverage for AMDGPU with SWSMU enabled validates object inclusion. Link errors for `renoir_set_ppt_funcs` or `smu_v12_0_*` helpers would indicate Makefile/object-list drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu12/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu12/renoir_ppt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu12/renoir_ppt.c

## Purpose

`renoir_ppt.c` implements the Renoir APU-specific SMU12 PowerPlay policy layer. It maps common SMU messages, clocks, tables, workloads, and sensors to Renoir firmware interfaces and provides callbacks for DPM clock reporting/control, power profiles, watermarks, multimedia power gating, GPU metrics, overdrive, GFXOFF, and VBIOS boot values.

## Important APIs, Types, and Functions

The exported entry point is `renoir_set_ppt_funcs`, which installs `renoir_ppt_funcs`, clock/table/workload maps, the SMU12 driver interface version, APU flag, and SMU12 message control.

Important functions include `renoir_init_smc_tables`, `renoir_get_dpm_clk_limited`, `renoir_get_dpm_ultimate_freq`, `renoir_od_edit_dpm_table`, `renoir_set_fine_grain_gfx_freq_parameters`, `renoir_emit_clk_levels`, `renoir_dpm_set_vcn_enable`, `renoir_dpm_set_jpeg_enable`, `renoir_force_dpm_limit_value`, `renoir_unforce_dpm_levels`, `renoir_get_dpm_clock_table`, `renoir_force_clk_levels`, `renoir_set_power_profile_mode`, `renoir_set_performance_level`, `renoir_set_watermarks_table`, `renoir_get_smu_metrics_data`, `renoir_read_sensor`, `renoir_is_dpm_running`, `renoir_get_gpu_metrics`, and `renoir_get_enabled_mask`.

Key firmware structures are `DpmClocks_t`, `Watermarks_t`, `SmuMetrics_t`, and `struct gpu_metrics_v2_2`.

## Control Flow

Initialization defines SMU watermarks, DPM clocks, and metrics tables, allocates CPU-side copies, and registers a GPU metrics cache. Clock maximum/minimum discovery reads firmware min/max messages for GFXCLK and uses DPM clock table indexes for FCLK/UCLK/SOCCLK/VCN clocks. When DPM for a clock is disabled, boot VBIOS values are returned instead.

DPM sysfs emission starts by refreshing `SmuMetrics_t`, then prints OD ranges, synthetic GFX min/current/max levels, or table-based levels for SOCCLK, MCLK/FCLK, DCFCLK, VCLK, and DCLK. MCLK/FCLK levels are printed in reverse order.

Performance level changes set hard-min and soft-max clock constraints through `smu_v12_0_set_soft_freq_limited_range` or direct SMU messages. Standard profile programs fixed UMD P-state constants for GFX/FCLK/SOCCLK/VCN; min and peak profiles derive per-clock targets. Manual overdrive is only accepted when DPM level is manual, stages min/max GFX frequencies, and commits by sending hard-min and soft-max GFX messages.

Watermark handling validates reader/writer counts, copies DC ranges and watermark types into the Renoir watermark table, then uploads once using the watermark bitmap state.

Metrics and sensor paths refresh the SMU metrics table, map clocks/activity/temperature/voltage/power values into common sensor units, compute smart-shift APU/dGPU share percentages, and populate `gpu_metrics_v2_2`.

## State and Persistence Behavior

Allocated state includes `clocks_table`, `metrics_table`, `watermarks_table`, and the GPU metrics cache. Runtime policy state includes staged/current GFX OD min/max, watermark bitmap flags, and `smu->is_apu`. Firmware state is modified for VCN/JPEG power gates, soft/hard clock limits, workload mask, watermarks, GFXOFF, SDMA power gating, CGPG, and mode2 reset.

## Dependencies

The file depends on SMU12 firmware message and driver-interface headers, common SMU helpers, `smu_v12_0.c` common functions, AMDGPU PM objects, sysfs formatting, and Renoir firmware table definitions.

## Integration Points

`renoir_ppt_funcs` plugs into AMDGPU powerplay for Renoir APUs. It delegates common operations to `smu_v12_0_*`, including firmware status, SDMA power gating, GFX CGPG/OFF, table finalization/default load, DPM range programming, driver table address, mode2 reset, and VBIOS boot parsing. DC consumes watermark and DPM clock table callbacks; hwmon/sysfs consumers use sensors, GPU metrics, OD, and DPM controls.

## Risks and Edge Cases

Renoir reports all feature bits enabled through `renoir_get_enabled_mask`, because PMFW lacks early APU feature-mask export; this can hide unsupported feature combinations. Power unit conversion for current socket power depends on MP1 IP version and firmware version. `renior_set_dpm_profile_freq` is misspelled but internal. Some profile helper calls ignore return values in min-profile branches. Watermarks are uploaded only once after `WATERMARKS_LOADED`. GFXCLK exposes synthetic three-level DPM even though firmware provides min/max plus current, so user masks above level 2 are rejected.

## Test Signals

Validation should include Renoir boot and SMU12 firmware status, DPM sysfs level output for all supported clocks, force-clock masks, OD edit/commit/restore, standard/min/peak performance profiles, VCN/JPEG/SDMA power-gating, DC watermark programming, GFXOFF status transitions, GPU metrics v2.2 content, smart-shift sensors, suspend/resume DPM-running behavior, and mode2 reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu12/renoir_ppt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu12/renoir_ppt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu12/renoir_ppt.h

## Purpose

`renoir_ppt.h` is the public header for the Renoir SMU12 PPT policy implementation. It exposes the callback installation function and the fixed Renoir UMD P-state constants used by performance-profile handling.

## Important APIs, Types, and Macros

The header declares `void renoir_set_ppt_funcs(struct smu_context *smu);`.

It defines `RENOIR_UMD_PSTATE_GFXCLK`, `RENOIR_UMD_PSTATE_SOCCLK`, `RENOIR_UMD_PSTATE_FCLK`, and packed `RENOIR_UMD_PSTATE_VCNCLK`.

## Control Flow

There is no executable control flow. `renoir_ppt.c` includes this header to publish its install function and to program standard profile clocks.

## State and Persistence Behavior

The header has no storage. Its constants affect firmware state indirectly when Renoir profile callbacks send SMU clock-limit messages.

## Dependencies

The declaration assumes `struct smu_context` is visible at include sites. The file otherwise depends only on the C preprocessor and its include guard.

## Integration Points

AMDGPU SMU ASIC setup calls `renoir_set_ppt_funcs` for Renoir-class devices. `renoir_ppt.c` uses the macros in DPM profile and clock emission code.

## Risks and Edge Cases

The packed VCN clock value carries both VCLK and DCLK policy in a single firmware parameter; wrong packing would affect video clock constraints. Updating Renoir performance policy requires keeping these constants consistent with PMFW expectations.

## Test Signals

Build coverage catches declaration drift. Runtime profile tests should confirm Renoir standard profile applies the expected GFX, SOC, FCLK, and VCN frequencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu12/renoir_ppt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu12/smu_v12_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu12/smu_v12_0.c

## Purpose

`smu_v12_0.c` provides common SMU12 helper logic used by Renoir-class APUs. It covers firmware status polling, SDMA/GFX power-gating messages, GFXOFF status/control, SMU table finalization/default loading, mode2 reset, clock range programming, driver table address notification, VBIOS boot value parsing, and SMU message-control initialization.

## Important APIs, Types, and Functions

Exported functions include `smu_v12_0_check_fw_status`, `smu_v12_0_powergate_sdma`, `smu_v12_0_set_gfx_cgpg`, `smu_v12_0_get_gfxoff_status`, `smu_v12_0_gfx_off_control`, `smu_v12_0_fini_smc_tables`, `smu_v12_0_set_default_dpm_tables`, `smu_v12_0_mode2_reset`, `smu_v12_0_set_soft_freq_limited_range`, `smu_v12_0_set_driver_table_location`, `smu_v12_0_get_vbios_bootup_values`, and `smu_v12_0_init_msg_ctl`.

The key local helper is `smu_v12_0_atom_get_smu_clockinfo`. Important structures include `struct smu_context`, `struct amdgpu_device`, `struct smu_table_context`, `struct atom_firmware_info_v3_1`, and `struct atom_firmware_info_v3_3`.

## Control Flow

Firmware status reads `smnMP1_FIRMWARE_FLAGS` through PCIe and checks the interrupt-enabled bit. Power gating sends SMU messages only where appropriate: SDMA is gated only for APUs, and GFX CGPG exits early if the device lacks `AMD_PG_SUPPORT_GFX_PG` or is in S0ix.

GFXOFF control sends allow/disallow messages; disable waits up to 500 ms for `smu_v12_0_get_gfxoff_status` to report status `2` (not in GFXOFF). GFXOFF status is extracted from `SMUIO_GFX_MISC_CNTL.PWR_GFXOFF_STATUS`.

Soft frequency range programming maps common clock types to SMU12-specific messages: GFX uses hard-min/soft-max GFXCLK, FCLK/MCLK/UCLK share FCLK messages, SOCCLK uses SOC messages, and VCLK uses VCN messages.

VBIOS boot parsing reads the ATOM `firmwareinfo` table, supports format revision 3 content revisions through the v3.1 and v3.3 layouts, stores boot values, then queries ATOM `getsmuclockinfo` for SOC, DCEF, VCLK, DCLK, optional FCLK, and LCLK boot clocks.

Message control configures the SMU v1 message registers at MP1 C2PMSG 66/90/82 and installs the caller-supplied message map.

## State and Persistence Behavior

The file frees and nulls `clocks_table`, `metrics_table`, and `watermarks_table`, and finalizes the GPU metrics driver table. It reads/writes no persistent host files. Firmware/hardware state is changed by SDMA, CGPG, GFXOFF, reset, DPM range, DPM clock table, and driver-table-address SMU messages, and by reading SMUIO/MP1 registers.

## Dependencies

Dependencies include AMDGPU core, ATOM firmware helpers, `smu_v12_0.h`, SOC15 helpers, SMU common helpers, MP 12.0 and SMUIO 12.0 generated register headers, and SMU message v1 ops.

## Integration Points

`renoir_ppt.c` uses this file for most common callbacks. Display and PM code indirectly call GFXOFF, DPM range, watermarks/default table, and VBIOS boot helpers through `pptable_funcs`. The message-control setup is the foundation for all Renoir SMU message traffic.

## Risks and Edge Cases

The file undefines `mmPWR_MISC_CNTL_STATUS` from the SMUIO12 header because some SMU12 ASICs use older offset tables, highlighting register-map ambiguity. GFXOFF disable logs but does not return a timeout error if status never reaches on-state. Clock handling maps MCLK/UCLK to FCLK, which is Renoir-specific and should not be generalized blindly. VBIOS parsing rejects non-format-3 firmware info. Driver table address messages are skipped silently when `mc_address` is zero.

## Test Signals

Test signals include firmware status success, Renoir GFXOFF status/control, SDMA power gate on APU, CGPG enable/disable with S0ix guard, default DPM table transfer, mode2 reset, DPM clock range sysfs operations, correct VBIOS boot clocks, and successful SMU message traffic using MP1 C2P registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu12/smu_v12_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/Makefile

## Purpose

This Makefile fragment wires SMU13 SWSMU manager objects into the AMDGPU PowerPlay build. It includes the common SMU13 helper plus multiple ASIC-specific PPT policy implementations.

## Important APIs, Types, and Functions

`SMU13_MGR` lists `smu_v13_0.o`, `aldebaran_ppt.o`, `yellow_carp_ppt.o`, `smu_v13_0_0_ppt.o`, `smu_v13_0_4_ppt.o`, `smu_v13_0_5_ppt.o`, `smu_v13_0_7_ppt.o`, `smu_v13_0_6_ppt.o`, and `smu_v13_0_12_ppt.o`. `AMD_SWSMU_SMU13MGR` prefixes them with `$(AMD_SWSMU_PATH)/smu13/`, and `AMD_POWERPLAY_FILES` is extended with that list.

## Control Flow

There is no runtime control flow. Kbuild evaluates the variables and includes the objects in the AMDGPU powerplay link.

## State and Persistence Behavior

The Makefile has no runtime state. Its build-state effect is inclusion of SMU13 common and ASIC-specific power-management code.

## Dependencies

It depends on the parent AMDGPU Makefile defining `AMD_SWSMU_PATH` and `AMD_POWERPLAY_FILES`, and on the listed sources being present and buildable.

## Integration Points

The build output provides SMU13 policy entry points such as `aldebaran_set_ppt_funcs` and common SMU13 helpers to the AMDGPU driver.

## Risks and Edge Cases

Object-list drift causes missing symbols or stale policy code in AMDGPU builds. Since the list includes many ASICs unconditionally in this fragment, compile errors in one policy file can break all SWSMU SMU13 builds.

## Test Signals

Kernel build and link coverage for AMDGPU with SWSMU enabled validates the fragment. Missing callback symbols or unreferenced object changes point to Makefile integration issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/aldebaran_ppt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/aldebaran_ppt.c

## Purpose

`aldebaran_ppt.c` implements the Aldebaran SMU13 policy layer for AMD Instinct-class GPUs. It maps common SMU concepts to Aldebaran firmware messages, features, clocks, tables, thermal limits, DPM policy, metrics, power limits, reset flows, I2C EEPROM access, ECC reporting, XGMI PLPD policy, determinism, and bad HBM page/channel notification.

## Important APIs, Types, and Functions

The exported entry point is `aldebaran_set_ppt_funcs`, which installs `aldebaran_ppt_funcs`, clock/feature/table maps, the Aldebaran SMU13 driver interface version, and SMU13 message control.

Important functions include `aldebaran_tables_init`, `aldebaran_select_plpd_policy`, `aldebaran_allocate_dpm_context`, `aldebaran_init_smc_tables`, `aldebaran_init_allowed_features`, `aldebaran_get_dpm_ultimate_freq`, `aldebaran_set_default_dpm_table`, `aldebaran_setup_pptable`, `aldebaran_run_btc`, `aldebaran_populate_umd_state_clk`, `aldebaran_get_smu_metrics_data`, `aldebaran_get_current_clk_freq_by_table`, `aldebaran_emit_clk_levels`, `aldebaran_force_clk_levels`, `aldebaran_get_thermal_temperature_range`, `aldebaran_read_sensor`, `aldebaran_get_power_limit`, `aldebaran_set_power_limit`, `aldebaran_system_features_control`, `aldebaran_set_performance_level`, `aldebaran_set_soft_freq_limited_range`, `aldebaran_usr_edit_dpm_table`, `aldebaran_is_dpm_running`, `aldebaran_i2c_xfer`, `aldebaran_i2c_control_init`, `aldebaran_get_unique_id`, `aldebaran_set_df_cstate`, `aldebaran_log_thermal_throttling_event`, `aldebaran_get_gpu_metrics`, `aldebaran_get_ecc_info`, `aldebaran_mode1_reset`, `aldebaran_mode2_reset`, and bad HBM page/channel helpers.

Key firmware data types include `PPTable_t`, `SmuMetrics_t`, `SwI2cRequest_t`, `SwI2cCmd_t`, `EccInfoTable_t`, `struct gpu_metrics_v1_3`, `struct smu_13_0_dpm_context`, and `struct smu_dpm_policy_ctxt`.

## Control Flow

Initialization registers PPTABLE, PM status log, SMU metrics, I2C commands, and ECC info tables; allocates metrics and ECC buffers; initializes the GPU metrics cache; allocates DPM context; and creates an XGMI PLPD policy whose setter only sends `GmiPwrDnControl` on master die.

PPTABLE setup forces VBIOS table selection, calls common SMU13 PPTABLE setup, copies the embedded SMC PPTABLE into the driver buffer, appends trailing fields from ATOM `smc_dpm_info` revision 4.10, and records thermal controller type.

DPM setup fills SOC, GFX, UCLK, and FCLK DPM tables. GFXCLK is represented as a two-entry fine-grained table using `GfxclkFmin`/`GfxclkFmax` from the PPTABLE. SR-IOV VF ultimate-frequency queries use cached DPM tables; non-VF delegates to common SMU13.

Metrics paths refresh the SMU metrics table and expose clock, activity, power, temperature, throttler, unique ID, energy accumulator, PCIe, and HBM temperature data. Power and energy are valid only on the primary die; secondary dies report zero or `-EOPNOTSUPP` for those values.

Manual and determinism clock control only accepts GFX/SCLK. Manual mode enforces `min < max` and sends common SMU13 soft min/max messages. Determinism mode restores default min/max, waits briefly, then sends `EnableDeterminism` with the target max clock. Changing away from determinism sends `DisableDeterminism`.

I2C transfer builds a `SwI2cRequest_t` command list from Linux I2C messages, handles direction-change restarts and STOP placement, uploads it through `SMU_TABLE_I2C_COMMANDS`, then copies read bytes from the returned driver table. The adapter is registered as "AMDGPU SMU 0" and assigned to RAS/FRU EEPROM bus pointers.

Reset paths are firmware-version dependent. Mode1 uses legacy `Mode1Reset` before PMFW 68.07 and `GfxDeviceDriverReset` afterward, with optional fatal-error flag for RAS FED status on newer firmware. Mode2 sends an async reset, waits, restores PCI config space, then waits for an ACK with retries.

ECC and bad-channel flows gate on minimum PMFW versions, transfer `SMU_TABLE_ECCINFO`, translate v1/v2 ECC table layouts into `umc_ecc_info`, and send bad HBM page/channel counts to firmware.

## State and Persistence Behavior

Persistent driver state includes allocated SMU tables, ECC table, GPU metrics cache, DPM tables, PLPD policy context, copied driver PPTABLE, current/custom GFX pstate min/max values, `adev->unique_id`, RAS/FRU I2C adapter pointers, power limits, and feature/table/clock maps.

Firmware and hardware state changed by this file includes allowed/enabled SMU features, DPM soft limits, determinism, GMI power-down policy, DF C-state control, board/DC BTC calibration, I2C command execution, reset mode, bad HBM page/channel notifications, PPT limits, and thermal throttling notifications to KFD SMI.

## Dependencies

The file depends on SMU13 common helpers, Aldebaran driver interface and PPSMC headers, SMU13 PPTABLE definitions, ATOMBIOS tables, SOC15/NBIO/THM/MP generated registers, AMDGPU XGMI/RAS/KFD/PCI helpers, Linux I2C APIs, and common SMU message/table helpers.

## Integration Points

`aldebaran_ppt_funcs` integrates with AMDGPU powerplay, hwmon/sysfs, GPU metrics, reset/recovery, RAS, XGMI policy, KFD SMI throttling events, EEPROM access, and DC/clock consumers. It delegates common firmware/table/microcode/power/IRQ/display-clock operations to `smu_v13_0_*` helpers while overriding Aldebaran-specific power, reset, metrics, ECC, and I2C behavior.

## Risks and Edge Cases

Many operations must run only on the primary die; sending power calibration or PPT messages on secondary dies can fail or return invalid data. Firmware-version gates are critical for ECC table versions, bad-channel messages, mode resets, fatal reset flags, and board BTC. `aldebaran_allocate_dpm_context` leaks the DPM context if policy allocation fails unless common cleanup handles partial init later. I2C command count is bounded by adapter quirks, but command construction itself relies on the I2C core honoring those quirks. RAS interrupt state suppresses some sensor/clock output. Mode2 reset must restore PCI config space before waiting for firmware ACK.

## Test Signals

Validation should include Aldebaran boot, PPTABLE copy/append, BTC on primary die, DPM table population, sysfs clock levels, manual OD and determinism modes, primary/secondary die power reporting, GPU metrics v1.3 including HBM temperatures and energy, thermal throttling logs and KFD SMI events, I2C EEPROM reads/writes through the SMU adapter, ECC table v1/v2 reads, mode1/mode2 reset across supported firmware versions, SR-IOV VF DPM limits, XGMI PLPD policy changes, DF C-state messages, and bad HBM page/channel notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/aldebaran_ppt.c -->
