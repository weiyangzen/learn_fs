# subset-b-003531 Research

Grouped source research for the subset B work item. Each section is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/amdgpu_smu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/amdgpu_smu.c

## Purpose
This file is the top-level AMDGPU software SMU integration layer. It wires the SMC/MP1 IP block into the AMDGPU IP lifecycle, selects ASIC-specific `pptable_funcs`, starts and checks SMU firmware, allocates and transfers SMU tables, enables power-management features, and exports the common powerplay operations through `swsmu_pm_funcs`. It is the coordination point between generic AMDGPU power management, display clock requirements, RAS, reset paths, debugfs STB capture, WBRF RF-interference handling, and per-ASIC PMFW command/table implementations.

## Important APIs, Types, and Functions
- IP lifecycle: `smu_early_init`, `smu_sw_init`, `smu_hw_init`, `smu_late_init`, `smu_hw_fini`, `smu_sw_fini`, `smu_suspend`, `smu_resume`, `smu_reset`, and exported `smu_ip_funcs` plus `smu_v11_0_ip_block` through `smu_v15_0_ip_block`.
- ASIC dispatch: `smu_set_funcs` selects Navi10, Sienna Cichlid, Renoir, Vangogh, Arcturus, Aldebaran, Cyan Skillfish, SMU v13/v14/v15 tables by MP1 IP version and adjusts OD/GFXOFF feature defaults.
- Table and memory setup: `smu_smc_table_sw_init`, `smu_init_fb_allocations`, `smu_alloc_memory_pool`, `smu_alloc_dummy_read_table`, `smu_update_gpu_addresses`, `smu_smc_hw_setup`, `smu_smc_hw_cleanup`.
- User and sysfs-facing PM operations: clock forcing, performance level, OD edits, power limits, pp table upload, pp feature mask, power profile modes, fan control, sensors, metrics, watermarks, and display clock voltage requests.
- Exported helpers: `is_support_sw_smu`, `is_support_cclk_dpm`, `smu_set_soft_freq_range`, `smu_get_dpm_freq_range`, `smu_set_ac_dc`, `smu_mode1_reset`, `smu_link_reset`, RAS helpers, GFXOFF helpers, ECC/HBM bad page messaging, SDMA/VCN reset helpers, PM policy helpers, and STB debugfs setup.

## Control Flow
Initialization starts in `smu_early_init`, which allocates `struct smu_context`, records `adev`, sets defaults, installs `swsmu_pm_funcs`, selects per-ASIC callbacks, and requests microcode. `smu_sw_init` initializes feature bitmaps, work items, atomic power-gate state, delayed thermal shutdown work, SMU table contexts, VBIOS boot values, PPTable microcode, IRQ handling, and fan capability flags. `smu_hw_init` starts/checks the SMC engine, evaluates WBRF support, powers APU media blocks as needed, initializes allowed feature masks, then runs `smu_smc_hw_setup`. Hardware setup pre-sets display count, sends driver/tool/memory-pool addresses, sets up and transfers the PPTable unless SCPM owns it, runs BTC, enables WBRF UCLK shadow, pushes allowed features, updates PCIe caps, enables system features, captures enabled feature masks, builds default DPM tables, fetches thermal limits, enables thermal alerts, notifies display state, sets minimum deep sleep DCEFCLK, and registers WBRF work.

Runtime operations mostly enter through `swsmu_pm_funcs`, validate `pm_enabled` and `adev->pm.dpm_enabled`, convert generic enums into SMU enums, and delegate to `smu->ppt_funcs`. Power-state changes run through `smu_handle_task` and `smu_adjust_power_state_dynamic`, which apply display changes, clock rules, SMC display notification, ASIC performance level selection, and workload profile updates. Suspend and fini paths cancel work, disable thermal alerting, selectively disable DPM features depending on BACO/S0ix/reset/ASIC/SCPM state, gate media blocks, clear watermarks/workloads, and save GFXOFF entry counts for continuity.

## State and Persistence Behavior
`struct smu_context` persists from early init to late fini and owns powerplay state, table buffers, feature masks, DPM levels, workload refcounts, user DPM profile, WBRF notifier state, work items, STB configuration, and cached limits/metrics. User settings are intentionally sticky: `smu_restore_dpm_user_profile` replays saved power limits, manual clock masks, fan mode/speed, and OD settings after suspend/resume while suppressing recursive profile updates with `SMU_DPM_USER_PROFILE_RESTORE`. `hardcode_pptable` persists a user-uploaded PPTable and triggers a full SMU reset. Metrics and temp tables use cache buffers and jiffies-based validity. Atomic power-gate fields mirror VCN/JPEG/VPE/ISP/UMSCH state so repeated gate requests are skipped. Delayed work persists for SW CTF shutdown and WBRF event coalescing until cleanup.

## Dependencies and Integration Points
- Depends on AMDGPU core device/IP infrastructure, firmware loading, PSP firmware mode, BO allocation, IRQ registration, PCIe capability masks, VBIOS boot values, power supply AC/DC state, debugfs, RAS, XCP, and display manager PP interfaces.
- Integrates with ASIC-specific `ppt_funcs` providers such as Navi10, Arcturus, Aldebaran, Cyan Skillfish, and SMU v13/v14/v15 backends.
- PMFW communication and table identifiers come from `amdgpu_smu.h`, `smu_internal.h`, `smu_types.h`, and pmfw interface headers.
- WBRF integration uses `linux/acpi_amd_wbrf.h` to consume Wi-Fi exclusion ranges and forward them to PMFW.
- Display integration uses DC callbacks for clocks, watermarks, display count, memory clock switching, and max sustainable clocks.

## Risks
- The file is callback-heavy; missing `ppt_funcs` members normally degrade to `-EOPNOTSUPP` or no-op, but an incorrectly selected callback table will misprogram firmware.
- State gates differ by path: reset/MP1/BACO functions intentionally work when DPM is down, while sysfs-like paths reject calls. Mixing those semantics can break suspend, reset, or runpm.
- PPTable upload resets the SMU and changes `power_play_table` backing storage, so size checks, lifetime, and reset error handling are important.
- Table BO sizes, DMA addresses, and cache sizes must match PMFW ABI expectations; mismatches can corrupt metrics, watermarks, or firmware tables.
- User DPM restoration can reapply stale power, clock, fan, or OD values after resume if validation rules change.
- WBRF delayed work and thermal shutdown work must be cancelled on fini to avoid use-after-free of `smu_context`.

## Test Signals
- Build with AMDGPU PM enabled and the relevant ASIC configs; compiler coverage should catch missing callback prototypes and PMFW table type mismatches.
- Boot or probe tests should show successful SMC firmware version check, PPTable transfer, DPM enablement, thermal alert enablement, and `SMU is initialized successfully`.
- Exercise sysfs/debugfs paths for `pp_dpm_*`, `power_dpm_force_performance_level`, `pp_power_profile_mode`, fan control, pp feature masks, metrics, and `amdgpu_smu_stb_dump`.
- Suspend/resume, runpm, BACO, mode1/mode2/link reset, and custom PPTable upload are critical regression paths.
- Negative tests should cover unsupported callbacks returning `-EOPNOTSUPP`, out-of-range power limits, invalid fan speed `U32_MAX`, invalid OD/clock types, and cache expiry for metrics tables.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/amdgpu_smu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/amdgpu_smu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/amdgpu_smu.h

## Purpose
This header defines the common software SMU contract used by the AMDGPU driver and all ASIC-specific SMU backends. It describes the shared `smu_context`, table/cache abstractions, DPM/user profile state, PMFW message-control structures, feature bitmaps, power policies, thermal and BACO state, the `pptable_funcs` backend vtable, exported SMU helper prototypes, and small inline helpers for cache and feature-list management.

## Important APIs, Types, and Functions
- Core state: `struct smu_context`, `struct smu_table_context`, `struct smu_dpm_context`, `struct smu_power_context`, `struct smu_user_dpm_profile`, `struct smu_feature`, `struct smu_feature_cap`, and `struct stb_context`.
- Table abstractions: `struct smu_table`, `struct smu_table_cache`, `struct smu_driver_table`, `enum smu_table_id`, `enum smu_driver_table_id`, and `SMU_TABLE_INIT`.
- Firmware messaging: `SMU_MSG_MAX_ARGS`, `SMU_MSG_FLAG_*`, `struct smu_msg_config`, `struct smu_msg_args`, `struct smu_msg_ops`, and `struct smu_msg_ctl`.
- Backend callback contract: `struct pptable_funcs` covers firmware loading, table init/transfer, feature control, clocks, display, power limits, fan control, sensors, metrics, power gating, reset, RAS, WBRF, STB, and per-ASIC policy operations.
- Mapping helpers: `MSG_MAP`, `CLK_MAP`, `FEA_MAP`, `TAB_MAP`, `PWR_MAP`, and `WORKLOAD_MAP` map generic SMU IDs to PMFW-specific IDs.
- Inline helpers manage metrics/temp table caches, driver table caches, feature bitmaps/lists, and safe unsigned-16 filtering.

## Control Flow
This file has no standalone execution path, but it shapes the control flow in `amdgpu_smu.c` and backend files. The generic SMU layer stores device state in `struct smu_context`, calls `pptable_funcs` when a concrete ASIC can implement an operation, and uses inline feature/cache helpers to update state without duplicating bitmap or lifetime logic. PMFW messages are described by `smu_msg_args` and are sent through an IP-specific `smu_msg_ops` implementation configured in `smu_msg_ctl`. Table transfers use `smu_table_context` to stage firmware-facing data in BO-backed memory or cached host buffers.

## State and Persistence Behavior
The header defines long-lived state rather than storing it itself. `smu_context` persists for the SMC IP lifetime and contains cached firmware versions, current/default/min/max power limits, OD settings, workload refcounts, user DPM profile, delayed work, WBRF notifier, message lock/control block, and feature bitmaps. Cache validity is time-based: table and driver-table caches require a non-null buffer, nonzero size and interval, a timestamp, and an unexpired jiffies window. Feature lists are bounded by `feature_num` and capped at `SMU_FEATURE_MAX`. Many structures are firmware ABI structures by pointer or table ID, so size, packing, and enum values are persistent cross-component contracts.

## Dependencies and Integration Points
- Includes Linux ACPI WBRF and units headers plus AMDGPU, KGD PP, DC PP, DC SMU, firmware, and SMU type headers.
- Shared by the generic SMU layer, ASIC-specific PPT implementations, display power integration, RAS, debugfs STB code, and firmware message layers.
- The `pptable_funcs` vtable is the key integration boundary between ASIC-independent code and PMFW-specific implementations.
- Table IDs and mappings integrate with PMFW interface headers such as Navi10, Arcturus, Aldebaran, and Cyan Skillfish definitions.

## Risks
- `struct pptable_funcs` is large and partially optional; callers must consistently guard absent callbacks and return the expected errno.
- Firmware ABI structures and mapping macros must stay synchronized with PMFW. Reordering enum values or changing table IDs can silently break mailbox commands or DMA table interpretation.
- Cache helpers rely on correct cache sizes and intervals; stale or undersized cache buffers can leak incorrect metrics.
- Feature helpers limit operations by `feature_num`, so backends with more than the default 64 features need correct initialization.
- `smu_memcpy_trailing` uses compile-time size checks, but both structures must still represent compatible firmware layouts.

## Test Signals
- Compile all SMU backends that include this header to catch callback signature drift and missing type definitions.
- Exercise feature-list conversion to and from arr32 for 64-bit and larger feature sets.
- Validate metrics/temp table caching by forcing cache hit, cache expiry, and size-only temp metrics requests.
- Firmware ABI tests should compare `sizeof` and key offsets for backend PPTable/metrics structures against PMFW expectations.
- Runtime tests should verify all exported prototypes link from AMDGPU, RAS, display, and debugfs users.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/amdgpu_smu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/aldebaran_ppsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/aldebaran_ppsmc.h

## Purpose
This header defines Aldebaran PPSMC mailbox response codes, PMFW message IDs, reset argument values, GFXOFF error codes, and typed aliases for SMU result and message words. It is an ASIC-specific firmware ABI map used by the Aldebaran SMU backend when translating generic SMU messages into the numeric protocol expected by PMFW.

## Important APIs, Types, and Functions
- Response codes: `PPSMC_Result_OK`, `Failed`, `UnknownCmd`, `CmdRejectedPrereq`, and `CmdRejectedBusy`.
- Message ID space: core version and driver interface queries, feature enable/disable, table DRAM address and transfer commands, DPM soft/hard min/max frequency commands, workload and voltage commands, PPT limit commands, MP1/reset commands, BTC, DRAM log, debug, memory channel, HBM bad page/channel, DF C-state, GMI power-down, GFXOFF, determinism, UCLK DPM mode, STB-to-DRAM, reset recovery, board power calibration, and HeavySBR.
- Reset arguments: warm reset, driver mode1/mode2, PCIe link, BIF link, and PF0 FLR.
- `GFXOFF_ERROR_e`, `PPSMC_Result`, and `PPSMC_Msg`.

## Control Flow
There is no executable control flow. Runtime control flow occurs when the Aldebaran backend maps a generic `enum smu_message_type` to one of these `PPSMC_MSG_*` values and sends it through the SMU mailbox. PMFW returns one of the response codes, which the driver message layer decodes into success, busy, prereq failure, unknown command, or generic failure. Reset operations pass one of the reset type constants as message argument data.

## State and Persistence Behavior
The file stores no runtime state. Its constants are persistent firmware ABI state: the numeric values must match Aldebaran PMFW. `#pragma pack(push, 1)` and `pop` bracket the definitions defensively even though the file only defines simple enum/typedef content.

## Dependencies and Integration Points
- Included by Aldebaran-specific SMU/PPT code and mapping tables.
- Integrates with generic `amdgpu_smu.h` message and reset paths, especially `smu_mode1_reset`, `smu_mode2_reset`, link reset, STB collection, HBM bad page reporting, and PMFW table transfers.
- Values are consumed by PMFW mailbox register programming, not by normal C function calls.

## Risks
- Message numbers are not interchangeable with Arcturus or Navi10. Copying mappings between ASICs can send a valid but wrong command.
- Some reset commands are marked retired in firmware comments; using them without version checks can fail on newer PMFW.
- Gaps and spare values are part of the ABI and should not be renumbered.
- Busy and prereq responses need retry or graceful failure at higher layers where appropriate.

## Test Signals
- Build Aldebaran SMU backend and verify all `MSG_MAP` entries resolve to these constants.
- Runtime firmware-version and driver-interface checks should pass before DPM setup.
- Exercise table transfer, power limit, GFXOFF, STB dump, HBM bad page/channel reporting, and reset commands on Aldebaran hardware or firmware simulation.
- Negative tests should confirm unknown/busy/prereq responses are decoded into the intended errno paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/aldebaran_ppsmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/arcturus_ppsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/arcturus_ppsmc.h

## Purpose
This header defines the Arcturus PPSMC mailbox ABI: PMFW response codes, message IDs, and simple typedefs for result and message words. It is the numeric command map used by Arcturus-specific SMU code when sending feature, table, DPM, BACO, VCN power, reset, BTC, debug, XGMI, bad HBM page, DF C-state, serial number, and LightSBR commands to PMFW.

## Important APIs, Types, and Functions
- Response codes mirror common PPSMC semantics: OK, failed, unknown command, rejected by prereq, and rejected busy.
- Basic messages cover SMU version, driver interface version, allowed feature masks, feature enable/disable, enabled feature masks, driver/tool DRAM addresses, table transfers, default/backup PPTable use, and system virtual DRAM address setup.
- Power and DPM messages include BACO entry/exit, ArmD3, soft/hard min/max by frequency, DPM frequency queries, workload mask, DF switch type, voltage queries, and PPT limits.
- Other IDs handle VCN0/VCN1 power, MP1 unload/reset/shutdown, soft reset, AFLL/DC BTC, dram log/debug, WAFL/XGMI, memory channel enable, bad HBM page count, DF C-state, GMI power-down, serial number reads, and LightSBR.
- Defines `PPSMC_Result` and `PPSMC_Msg` as `uint32_t`.

## Control Flow
The file is declarative. Arcturus mapping tables select these IDs for generic SMU operations, then the common message layer writes the numeric command and arguments to SMU mailbox registers. Feature and table setup in `amdgpu_smu.c` depends on these values through backend callbacks such as feature mask programming, PPTable transfer, DPM setup, VCN power gating, and reset handling.

## State and Persistence Behavior
No runtime state is stored. The constants are persistent firmware ABI values. The message count and gaps must remain synchronized with PMFW because the driver uses them as stable protocol identifiers across boots and resets.

## Dependencies and Integration Points
- Used by Arcturus PPT implementation and common SMU message mapping code.
- Connects generic SMU operations for BACO, DPM, VCN power gating, RAS serial/bad page paths, XGMI, DF C-state, and LightSBR to firmware.
- Depends on PMFW using the same result code and message numbering contract.

## Risks
- Numeric drift causes silent protocol corruption: PMFW may execute another command or reject the message.
- The LightSBR command has parameter semantics documented in comments; inverting the argument changes reset ownership between SMU/PSP and the driver.
- Some commands have ASIC-specific behavior and should not be assumed present just because a common `smu_message_type` exists.
- `PPSMC_Message_Count` is lower than later explicit serial/LightSBR values, so code must not use it as a complete max for all defines without checking intent.

## Test Signals
- Compile Arcturus backend mapping tables and confirm all referenced `PPSMC_MSG_*` names exist.
- On Arcturus hardware, verify feature mask setup, PPTable transfer, VCN power up/down, BACO transitions, XGMI controls, and LightSBR behavior.
- Check PMFW response decode for busy/prereq failure by injecting or observing rejected commands.
- Confirm serial number reads and HBM bad page reporting still use the expected command IDs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/arcturus_ppsmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu11_driver_if_arcturus.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu11_driver_if_arcturus.h

## Purpose
This header defines the Arcturus SMU11 driver interface tables and constants shared between the Linux driver and PMFW. It specifies PPTable layout, feature bits, clock level counts, I2C command/request structures, power/thermal/voltage/DPM enums, metrics/config/debug/activity tables, table IDs used for SMU table transfer messages, and related ABI constants.

## Important APIs, Types, and Functions
- Version and sizing: `PPTABLE_ARCTURUS_SMU_VERSION`, `NUM_*_DPM_LEVELS`, max level macros, `NUM_FEATURES`, and XGMI level counts.
- Feature and throttler ABI: `FEATURE_*_BIT` and `FEATURE_*_MASK` for DPM, deep sleep, ULV, VCN, thermal, fan, OOB, Vmin; `THROTTLER_*` bits; workload bits; XGMI state values.
- I2C ABI: `I2cControllerConfig_t`, `SwI2cCmd_t`, `SwI2cRequest_t`, controller/port/name/throttler/protocol/speed/command enums.
- Main firmware tables: packed `PPTable_t`, `DriverSmuConfig_t`, `SmuMetrics_t`, `AvfsDebugTable_t`, `AvfsFuseOverride_t`, and `DpmActivityMonitorCoeffInt_t`.
- Table transfer IDs: `TABLE_PPTABLE`, `TABLE_AVFS`, `TABLE_PMSTATUSLOG`, `TABLE_SMU_METRICS`, `TABLE_DRIVER_SMU_CONFIG`, `TABLE_OVERDRIVE`, `TABLE_WAFL_XGMI_TOPOLOGY`, `TABLE_I2C_COMMANDS`, and `TABLE_ACTIVITY_MONITOR_COEFF`.

## Control Flow
The file is data layout rather than executable logic. The Arcturus SMU backend fills or reads these packed structures, stages them in driver BOs, and transfers them with PMFW table-transfer messages. During SMU setup, the PPTable provides feature enablement, infrastructure limits, DPM frequency tables, fan settings, AVFS curves, XGMI training data, board telemetry, spread spectrum, I2C controllers, memory channel masks, and MMHUB padding. Runtime metrics reads copy `SmuMetrics_t` from PMFW, and configuration/activity/I2C tables are transferred when backend operations request them.

## State and Persistence Behavior
The tables represent persistent firmware-visible state for the running device. `PPTable_t` is consumed by PMFW as board and policy configuration. `DriverSmuConfig_t` stores averaging time constants. `SmuMetrics_t` is a snapshot of current telemetry. I2C request structures carry bounded command batches. The file uses packed layout around the main PPTable so alignment and padding are part of the ABI. Many fields include units such as MHz, mV Q2, Celsius, Amps, Q16, and IEEE float stored in integer words.

## Dependencies and Integration Points
- Used by `arcturus_ppt` code and common SMU table transfer helpers.
- Integrates with `amdgpu_smu.h` table IDs, feature maps, workload maps, metrics conversion, power limit/fan/thermal/sysfs paths, I2C support, XGMI policy, and RAS bad page flows.
- The PMFW binary must use exactly the same structure sizes, field order, and table IDs.

## Risks
- Any structural edit requires interface-version coordination; changing field order, packing, padding, or array counts breaks PMFW table parsing.
- Several comments mark FIXME/pending spec areas; those fields should be treated as firmware ABI even if documentation is incomplete.
- Units are mixed and sometimes fixed point. Misinterpreting Q formats or MHz/kHz/Celsius units can create unsafe voltage, thermal, or fan behavior.
- Table IDs must match the message-layer `TransferTable*` command arguments; cross-ASIC reuse can upload the wrong table type.
- Feature bit positions differ from Navi10, so common feature maps must be ASIC-specific.

## Test Signals
- Compile Arcturus backend and verify expected `sizeof(PPTable_t)`, `sizeof(SmuMetrics_t)`, and table IDs against firmware headers.
- Run SMU initialization to confirm PPTable transfer, enabled feature mask retrieval, DPM table population, thermal/fan limits, XGMI policy, and metrics reads.
- Exercise I2C command table transfers and confirm command count bounds at `MAX_SW_I2C_COMMANDS`.
- Validate metrics conversion for clocks, fan, socket power, HBM temperature, throttler status, and energy accumulator.
- Negative ABI tests should detect changed packing, missing MMHUB padding, or feature bit renumbering.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu11_driver_if_arcturus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu11_driver_if_cyan_skillfish.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu11_driver_if_cyan_skillfish.h

## Purpose
This compact header defines the Cyan Skillfish MP1/SMU11 driver interface version, firmware table IDs, and SMU metrics layout. It is the ABI used by the Cyan Skillfish backend to identify firmware tables and decode current/average telemetry for CPU, GFX, SOC IP clocks, power rails, socket power, temperatures, and throttling status.

## Important APIs, Types, and Functions
- Interface version: `MP1_DRIVER_IF_VERSION 0x8`.
- Table IDs: `TABLE_BIOS_IF`, `TABLE_WATERMARKS`, `TABLE_PMSTATUSLOG`, `TABLE_DPMCLOCKS`, `TABLE_MOMENTARY_PM`, `TABLE_SMU_METRICS`, and `TABLE_COUNT`.
- `SmuMetricsTable_t`: per-sample telemetry containing six CPU cores, two L3 entries, GFX/SOC/VCLK/DCLK/Memclk, voltage/current/power rails, socket power, SOC/edge temperatures, throttler status, and spare padding.
- `SmuMetrics_t`: wraps current and average metrics tables plus sample start/stop timestamps and `Accnt`.

## Control Flow
There is no code flow in this header. The Cyan Skillfish SMU backend requests `TABLE_SMU_METRICS` from PMFW, interprets the returned buffer as `SmuMetrics_t`, and maps fields into generic AMDGPU metrics/sysfs outputs. The table ID constants are also used when generic table-transfer helpers pass PMFW table identifiers.

## State and Persistence Behavior
The header stores no driver state. `SmuMetrics_t` describes firmware-produced telemetry snapshots; `Current` and `Average` are two views of the same field set. Table IDs are persistent ABI constants and include several backward-compatible entries declared but not actively used by the driver.

## Dependencies and Integration Points
- Used by Cyan Skillfish PPT/SMU code selected from `smu_set_funcs` for MP1 11.0.8.
- Integrates with generic `get_gpu_metrics`, `get_pm_metrics`, sensor reads, and table-transfer logic.
- Depends on PMFW and BIOS using the same table numbering and metrics layout.

## Risks
- Metrics arrays are fixed at six CPU cores and two L3 entries; code using this table must not assume a larger topology.
- Temperatures use centi-Celsius in several fields while other SMU headers often use Celsius or millidegrees Celsius in driver-facing APIs.
- Backward-compatible but unused table IDs should not be removed or renumbered because firmware may still expose them.
- No explicit packing pragma is used; ABI validation should confirm compiler layout matches PMFW expectations.

## Test Signals
- Compile Cyan Skillfish backend and verify the selected table IDs match backend mappings.
- Read SMU metrics and confirm current/average CPU, GFX, SOC, clock, rail, socket power, and temperature values are sane.
- Check unit conversion for centi-Celsius and mW/mV/mA fields when exposed through generic metrics.
- Regression tests should compare `sizeof(SmuMetricsTable_t)` and `sizeof(SmuMetrics_t)` against PMFW expectations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu11_driver_if_cyan_skillfish.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu11_driver_if_navi10.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu11_driver_if_navi10.h

## Purpose
This header defines the Navi10/Navi1x SMU11 driver interface ABI. It provides PPTable layout, feature and throttler bits, DPM clock counts, I2C command layouts, power/thermal/voltage enums, OOB monitor data, metrics variants for NV10/NV12, watermarks, overdrive, AVFS/debug/activity monitor tables, table transfer IDs, and UCLK switch constants used by Navi10-family SMU backends.

## Important APIs, Types, and Functions
- Version and sizing: `PPTABLE_NV10_SMU_VERSION`, `NUM_*_DPM_LEVELS`, link levels, max-level macros, Gemini mode constants, `NUM_FEATURES`.
- Feature bits include DPM clocks/link/DCEF, memory voltage scaling, deep sleep, ULV, FW D-state, GFXOFF, BACO, VCN/JPEG/USB power gating, RSMU CG, PPT/TDC/EDC/APCC/GTHR/ACDC/VRHOT/FW CTF/fan/thermal, RM, LED, spread spectrum, OOB, Vmin, MMHUB/ATHUB power gating, and APCC DFLL.
- Tables and structures: packed `PPTable_t`, `DriverSmuConfig_t`, `OverDriveTable_t`, `SmuMetrics_legacy_t`, `SmuMetrics_t`, `SmuMetrics_NV12_legacy_t`, `SmuMetrics_NV12_t`, `SmuMetrics_NV1X_t`, `Watermarks_t`, AVFS debug/fuse override tables, `DpmActivityMonitorCoeffInt_t`, `RlcPaceFlopsPerByteOverride_t`, and `OutOfBandMonitor_t`.
- Table IDs: PPTable, watermarks, AVFS, PSM debug, fuse override, PM status log, SMU metrics, driver config, activity monitor coeff, overdrive, I2C commands, and pace.

## Control Flow
The header is declarative, but it drives Navi10 backend control flow. During initialization the backend builds or patches `PPTable_t`, transfers it to PMFW, and later transfers watermarks, overdrive, AVFS, I2C, activity monitor, and pace tables as requested by generic SMU operations. Runtime metrics reads select the correct member of `SmuMetrics_NV1X_t` depending on ASIC or firmware generation. Display paths consume `Watermarks_t`; OD sysfs paths consume `OverDriveTable_t`; fan/power/thermal paths read limits and control fields from PPTable and metrics.

## State and Persistence Behavior
`PPTable_t` is persistent PMFW configuration for feature enablement, AC/DC power limits, TDC, thermal limits, FW D-state mask, ULV, voltage control, DPM frequency tables, UCLK divisors, PCIe link DPM, fan curves, AVFS curves, board telemetry, GPIOs, spread spectrum, board power, and MMHUB padding. Metrics structures are transient snapshots. Watermarks persist until reloaded for display clock ranges. Overdrive table values represent user-adjustable state. Table IDs persist as ABI values used as arguments to PMFW table transfer messages.

## Dependencies and Integration Points
- Used by Navi10 PPT implementation selected for MP1 11.0.0, 11.0.5, and 11.0.9.
- Integrates with generic SMU feature maps, clock maps, workload maps, table transfer, display watermarks, OD editing, fan control, metrics, sensors, BACO/GFXOFF, and DPM operations.
- Firmware, VBIOS PPTable data, and Linux structure definitions must agree on layout, units, array counts, and table IDs.

## Risks
- This is a dense firmware ABI. Changing `PPTable_t`, metrics variants, watermarks, or table IDs without a matching PMFW interface update can break boot-time DPM setup or runtime PM features.
- Navi10 feature bit positions differ from Arcturus and later ASICs; maps must remain per-ASIC.
- Multiple metrics variants make size and generation selection important. Reading an NV12 metrics buffer as legacy NV10 will misdecode energy, PCIe, and pre/post deep-sleep fields.
- Units and fixed point formats vary: MHz, Celsius, mV Q2, Q4.4, Q16, Q8.24, Q12.12, and 10 KHz units coexist.
- OOB monitor and I2C structures expose board-management data; command counts, addresses, and padding must be validated before transfer.

## Test Signals
- Compile Navi10 backend and compare structure sizes/offsets against the PMFW header used to build firmware.
- Boot Navi10/Navi12 hardware and verify PPTable transfer, watermarks upload, OD table reads/edits, GFXOFF/BACO behavior, fan controls, and metrics reporting.
- Exercise display mode changes to validate watermark rows for SOCCLK/DCEFCLK and UCLK ranges.
- Validate metrics variant selection by checking PCIe rate/width, energy accumulator, VCN activity, and pre/post deep-sleep averages on supported ASICs.
- Negative tests should catch accidental feature bit renumbering, table ID changes, and malformed I2C command counts above `MAX_SW_I2C_COMMANDS`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu11_driver_if_navi10.h -->
