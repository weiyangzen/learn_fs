# subset-b-003518 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/pppcielanes.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/pppcielanes.c

## Purpose

This file provides the small PCIe lane-width codec used by AMD PowerPlay table handling. ATOM/VBIOS power tables encode lane counts as compact numeric fields, while driver-facing code often needs actual lane counts such as 1, 2, 4, 8, or 16.

## Important APIs, Types, and Functions

`encode_pcie_lane_width(uint32_t num_lanes)` indexes `pp_r600_encode_lanes` and maps a physical lane count to a BIOS lane code. `decode_pcie_lane_width(uint32_t num_lanes)` indexes `pp_r600_decoded_lanes` and maps an encoded value back to a lane count. The tables treat unsupported widths as `0`; decode slot `0` maps to 16 lanes, matching the historical R600 encoding convention.

## Control Flow and State

Both exported functions are pure table lookups with no branching, allocation, hardware access, locking, or persistent state. All state is immutable static const data in the translation unit.

## Dependencies and Integration

The file includes Linux integer types, ATOM BIOS headers, and `pppcielanes.h`. It integrates with PowerPlay table parsers and ASIC hwmgr code that need to translate between VBIOS PCIe records and internal PCIe state descriptions.

## Risks and Test Signals

There are no bounds checks on either index. Callers must only pass `num_lanes <= 16` to encode and encoded values within the 8-entry decode table. Invalid input can read past static arrays in kernel context. Test signals are narrow: unit-style checks for known lane mappings, boot-time parsing of VBIOS PCIe tables, and runtime PCIe DPM state reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/pppcielanes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/pppcielanes.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/pppcielanes.h

## Purpose

This header exposes the PCIe lane-width conversion helpers implemented in `pppcielanes.c` to the PowerPlay hardware manager code.

## Important APIs, Types, and Functions

It declares `encode_pcie_lane_width(uint32_t num_lanes)` and `decode_pcie_lane_width(uint32_t num_lanes)`. The API shape is intentionally minimal: callers provide a raw `uint32_t`, and the helper returns an 8-bit lane encoding or decoded lane count.

## Control Flow and State

The header has no executable logic and no state. It only provides include guards and extern declarations.

## Dependencies and Integration

The declarations rely on fixed-width integer types being available to includers, typically through nearby kernel or ATOM headers. The header is part of the AMDGPU PowerPlay hwmgr layer and allows table parsing, PCIe DPM, or ASIC-specific code to avoid duplicating lane mapping constants.

## Risks and Test Signals

The declarations do not document valid ranges, even though the implementation requires bounded inputs. Compile coverage catches signature drift; runtime coverage must come from consumers parsing PCIe table entries and from any tests that assert expected lane encode/decode values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/pppcielanes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/pptable_v1_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/pptable_v1_0.h

## Purpose

This header defines the packed ATOM PowerPlay table v1.0 schema used for Tonga-era and Polaris-era GPUs. It is the firmware contract consumed by `process_pptables_v1_0.c` when converting VBIOS data into driver-owned PowerPlay tables.

## Important APIs, Types, and Functions

The file is data-layout only. `ATOM_Tonga_POWERPLAYTABLE` is the root structure with offsets to state, fan, thermal, MCLK/SCLK dependency, voltage lookup, multimedia, VCE, PPM, PowerTune, hard-limit, PCIe, and GPIO subtables. The variable-length table types use flexible arrays annotated with `__counted_by`, including state arrays, MCLK/SCLK dependencies, PCIe tables, MM dependencies, voltage lookup tables, VCE state tables, and hard-limit tables. Revision-sensitive variants include `ATOM_Polaris_SCLK_Dependency_Record`, `ATOM_Polaris10_PCIE_Record`, `ATOM_Fiji_Fan_Table`, `ATOM_Polaris_Fan_Table`, `ATOM_Fiji_PowerTune_Table`, and `ATOM_Polaris_PowerTune_Table`.

## Control Flow and State

There is no control flow. The important state model is packed little-endian firmware data with many 16-bit offsets relative to the root table address. `#pragma pack(push, 1)` is critical because the structures must match byte-exact VBIOS layouts.

## Dependencies and Integration

The header includes `hwmgr.h` and uses ATOM-style aliases such as `UCHAR`, `USHORT`, and `ULONG`. Its macros define platform capability bits, thermal controller identifiers, classification flags, fan flags, and table revision constants consumed by the v1.0 parser and broader hwmgr capability logic.

## Risks and Test Signals

Any layout drift, packing change, or incorrect revision interpretation can corrupt pointer arithmetic in the parser. The structures expose firmware-controlled counts and offsets, so parser bounds validation is the main safety signal. Practical test signals are successful initialization on Tonga/Fiji/Polaris boards, sane sysfs clock and fan output, and absence of parser assertions such as invalid state arrays or dependency tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/pptable_v1_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/process_pptables_v1_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/process_pptables_v1_0.c

## Purpose

This file parses Tonga/Polaris-style PowerPlay table v1.0 data from VBIOS and builds normalized driver tables under `hwmgr->pptable`. It translates firmware offsets, counts, voltages, clock dependencies, fan controls, PowerTune limits, PCIe states, GPIO VRHot data, and VCE states into hwmgr structures.

## Important APIs, Types, and Functions

The exported `pptable_v1_0_funcs` provides `pptable_init` and `pptable_fini`. `get_number_of_powerplay_table_entries_v1_0()` returns the firmware state count. `get_powerplay_table_entry_v1_0()` converts a state entry and invokes an ASIC callback to fill hardware power-state data, patches boot states, and populates `hwmgr->vce_states`.

Key internal helpers include `get_powerplay_table()` for ATOM table lookup and caching, `set_platform_caps()` for platform capability mapping, `init_thermal_controller()`, `init_over_drive_limits()`, `init_clock_voltage_dependency()`, and `init_dpm_2_parameters()`. Revision-aware helpers parse SCLK, PCIe, fan, and PowerTune variants.

## Control Flow and State

Initialization allocates `struct phm_ppt_v1_information`, fetches or reuses `hwmgr->soft_pp_table`, validates table revision and state-array presence, maps platform caps, initializes thermal/fan data, overdrive limits, dependency tables, and DPM2/PPM fields. Cleanup frees every allocated subtable and clears pointers. Persistent state is stored in `hwmgr->pptable`, `hwmgr->dyn_state.cac_dtp_table`, `hwmgr->platform_descriptor`, `hwmgr->thermal_controller`, and cached VBIOS table fields.

## Dependencies and Integration

The parser depends on ATOM BIOS access through `smu_atom_get_data_table`, endian helpers, kernel allocation, `pp_debug` assertions, `phm_cap_set/unset`, and layout definitions from `pptable_v1_0.h`. ASIC hwmgr code consumes the resulting `phm_ppt_v1_information` and calls the exported entry APIs during power-state enumeration.

## Risks and Test Signals

Many offsets and counts are firmware-provided and used for pointer arithmetic; invalid VBIOS can cause failed assertions or unsafe reads if a path lacks bounds checks. `get_pcie_table()` assumes SCLK dependency data exists because it compares PCIe entries to `vdd_dep_on_sclk->count`. The entry-index checks use `<= ucNumEntries`, which is suspicious because valid zero-based indices normally end at `ucNumEntries - 1`. Test signals include boot logs for PP_ASSERT failures, correct DPM/fan/overdrive sysfs data, VCE state availability, and leak-free unload paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/process_pptables_v1_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/process_pptables_v1_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/process_pptables_v1_0.h

## Purpose

This header exposes the v1.0 PowerPlay table parser to ASIC-specific hwmgr implementations.

## Important APIs, Types, and Functions

`pptable_v1_0_funcs` is the function-table instance used by hwmgr setup. `get_number_of_powerplay_table_entries_v1_0()` exposes state-count retrieval. `get_powerplay_table_entry_v1_0()` exposes per-state conversion and accepts an ASIC callback with access to the raw state entry, destination `pp_power_state`, raw PowerPlay table, and classification flags.

## Control Flow and State

The header has no logic or state. It defines the handoff surface between generic v1.0 table parsing and hardware-specific power-state population.

## Dependencies and Integration

It includes `hwmgr.h` for `struct pp_hwmgr`, `struct pp_power_state`, and `struct pp_table_func`. It integrates with hwmgr initialization code by assigning the function table and with ASIC backends through the callback-based entry conversion API.

## Risks and Test Signals

The callback type is written inline rather than as a named typedef, which makes signature reuse error-prone. Compile coverage catches mismatched callbacks. Runtime test signals are successful power-state enumeration and correct boot-state patching through the selected ASIC hwmgr.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/process_pptables_v1_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/processpptables.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/processpptables.c

## Purpose

This file implements the older generic ATOM PPLIB PowerPlay table parser. It initializes `hwmgr->dyn_state`, platform descriptors, thermal controller data, fan parameters, overdrive limits, DPM2 parameters, clock/voltage dependencies, phase shedding, and VCE state access for pre-v1.0 table layouts.

## Important APIs, Types, and Functions

The public APIs are `pp_tables_get_response_times()`, `pp_tables_get_num_of_entries()`, `pp_tables_get_entry()`, and the exported `pptable_funcs`. `pp_tables_get_entry()` supports both pre-format-6 fixed state entries and format-6 variable DPM-level entries, calls `init_non_clock_fields()`, and delegates clock-info parsing to an ASIC callback.

Internal helpers derive extended-header offsets for VCE, UVD, SAMU, ACP, PowerTune, PPM, and SCLK/VDDGFX tables; allocate normalized dependency tables; map BIOS platform caps; parse thermal/fan table revisions; read firmware-info overdrive limits; parse CAC leakage and phase shedding tables; and expose VCE state records through the `pp_table_func` callbacks.

## Control Flow and State

`pp_tables_initialize()` skips most work for `CHIP_RAVEN`, otherwise marks `need_pp_table_upload`, fetches and caches the PowerPlay table, maps caps, initializes thermal/overdrive/dependency/DPM2/phase-shedding state, and returns the first failing result. `pp_tables_uninitialize()` frees all dynamically allocated `hwmgr->dyn_state` subtables. `get_powerplay_table()` uses a static dummy table for Raven and otherwise caches the ATOM PowerPlayInfo table in `hwmgr->soft_pp_table`.

## Dependencies and Integration

The parser depends on `pptable.h` legacy ATOM layouts, `smu_atom_get_data_table`, endian helpers, kernel allocation, AMDGPU PCI/device identity, hwmgr capability helpers, and ASIC callbacks for clock-info conversion. SMU10 still wires `hwmgr->pptable_func = &pptable_funcs`, so this legacy parser participates in Raven-family power-state enumeration even while other data comes from SMU tables.

## Risks and Test Signals

The code performs extensive offset arithmetic on firmware data with uneven validation. Several range checks use `entry_index > count` instead of `>= count`. VCE/UVD/SAMU/ACP offset helpers assume extended-header sizes encode table presence correctly. Raven has a dummy table but initialization and cleanup return early, so consumers must tolerate missing dyn_state subtables. Test signals include boot-time PP_ASSERT output, sane sysfs DPM levels, correct VCE/UVD clock dependency exposure, and clean unload without leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/processpptables.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/processpptables.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/processpptables.h

## Purpose

This header declares the public interface for the legacy PowerPlay table parser implemented in `processpptables.c`.

## Important APIs, Types, and Functions

`pptable_funcs` is the parser function table. `pp_tables_hw_clock_info_callback` is the ASIC callback type used to translate raw ATOM clock-info entries into a `pp_hw_power_state`. `pp_tables_get_num_of_entries()`, `pp_tables_get_entry()`, and `pp_tables_get_response_times()` expose the main read APIs for hwmgr backends.

## Control Flow and State

The header carries no executable logic. It defines a callback-driven flow: the generic parser handles BIOS table walking and non-clock fields, while the ASIC backend handles hardware-specific clock-info records.

## Dependencies and Integration

It forward-declares `pp_hwmgr`, `pp_power_state`, and `pp_hw_power_state` and relies on `struct pp_table_func` from included hwmgr context. It is included by SMU10 and other hwmgr files that need table enumeration or parser function-table assignment.

## Risks and Test Signals

The generic callback design keeps table walking reusable but makes correctness depend on matching the callback to the table format and ASIC. Compile coverage checks signature compatibility. Runtime signals are successful `get_num_of_entries`, per-state conversion, response-time reads, and boot-state patch behavior in ASIC backends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/processpptables.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_hwmgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_hwmgr.c

## Purpose

This file implements the SMU10/Raven PowerPlay hardware manager. It bridges AMDGPU power-management operations to SMU messages, maintains SMU10 backend state, exposes sysfs clock controls, reports sensors, manages VCN/GFX/MMHUB/SDMA power gating, and wires SMU10 into the generic hwmgr and PowerPlay table interfaces.

## Important APIs, Types, and Functions

`smu10_init_function_pointers()` installs `smu10_hwmgr_funcs` and legacy `pptable_funcs`. Backend lifecycle is handled by `smu10_hwmgr_backend_init()` and `smu10_hwmgr_backend_fini()`. Clock and DPM control flows include `smu10_dpm_force_dpm_level()`, `smu10_force_clock_level()`, `smu10_emit_clock_levels()`, `smu10_set_fine_grain_clk_vol()`, and display-clock request helpers. Sensor and query paths include `smu10_read_sensor()`, `smu10_get_clock_by_type_with_latency()`, `smu10_get_clock_by_type_with_voltage()`, and `smu10_get_performance_level()`.

## Control Flow and State

Backend init allocates `struct smu10_hwmgr`, initializes default caps and DPM fields, copies the SMU clock table or falls back to hardcoded clock/voltage arrays, initializes DAL power-level dependencies, constructs basic platform descriptors, and enables overdrive sysfs. Runtime functions update cached hard/soft frequency limits before sending SMU messages. Forced DPM levels translate policy modes into hard-min and soft-max SMU requests for GFX, FCLK, SOCCLK, and VCN. Cleanup frees clock-voltage dependency tables, DAL dependency state, and the backend object.

## Dependencies and Integration

The file depends on SMU message IDs from `rv_ppsmc.h`, SMU table access through `smum_smc_table_manager`, AMDGPU IP powergating calls, SOC15 register reads, display watermarks, hwmgr function tables, and the legacy PowerPlay table parser. It is a major integration point between display requirements, sysfs power controls, firmware clock tables, and runtime SMU firmware capabilities.

## Risks and Test Signals

Many SMU message sends ignore return values, and some state is updated before firmware success is known. Firmware-version gates affect forced DPM and GPU-busy sensors. `smu10_disable_gfx_off()` waits in a loop until GFX reports on, so broken firmware/register state can stall. Test signals include sysfs `power_dpm_force_performance_level`, `pp_dpm_sclk`, `pp_dpm_mclk`, `pp_od_clk_voltage`, sensor reads, suspend/resume restoration, VCN power-state transitions, watermark programming, and SMU firmware version coverage across Raven/Picasso/Raven2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_hwmgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_hwmgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_hwmgr.h

## Purpose

This header defines the SMU10 hardware-manager data model, power-state structures, constants, and initialization entry point used by `smu10_hwmgr.c`.

## Important APIs, Types, and Functions

The main exported function is `smu10_init_function_pointers(struct pp_hwmgr *hwmgr)`. Key types include `struct smu10_hwmgr` for persistent backend state, `struct smu10_power_state` for per-power-state hardware data, `struct smu10_power_level`, `struct smu10_dpm_entry`, `struct smu10_clock_voltage_information`, and `struct smu10_voltage_dependency_table`. Constants define feature-scoreboard masks, DPM flags, PCIe powergating targets, UMD pstate defaults, and clock limits.

## Control Flow and State

The header itself has no control flow, but it describes the state owned by the SMU10 backend: DPM flags, current frequency constraints, display and watermark data, power-gating booleans, CC6 settings, VCN/GFX state, clock tables, fine-grain tuning status, and allocated voltage dependency tables.

## Dependencies and Integration

It includes `hwmgr.h`, `smu10_inc.h`, `smu10_driver_if.h`, and `rv_ppsmc.h`, making it the local contract between generic hwmgr code, SMU firmware interfaces, and SOC register definitions. `smu10_power_state.magic` ties into cast helpers in the C file.

## Risks and Test Signals

Because this structure stores many cached firmware and user-control values, stale fields can desynchronize driver assumptions from SMU firmware state. Flexible-array voltage tables require allocation and cleanup discipline. Test signals are compile-time structure use, backend init/fini leak checks, sysfs clock output, forced DPM behavior, and suspend/resume restoration of cached fine-grain limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_hwmgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h

## Purpose

This header aggregates SMU10-related register include files for the hwmgr layer and defines one display PHY status index not provided by the generated register headers.

## Important APIs, Types, and Functions

There are no functions or types. The file includes MP 10.0, NBIO 7.0, and THM 10.0 default/offset/mask headers and defines `ixDDI_PHY_GEN_STATUS` as `0x3FCE8`.

## Control Flow and State

There is no control flow or runtime state. Its effect is compile-time availability of register offsets and masks.

## Dependencies and Integration

It is included by `smu10_hwmgr.h`, which makes SOC register definitions available to SMU10 hwmgr code. The included generated headers back direct register reads such as temperature and GFXOFF status paths in `smu10_hwmgr.c`.

## Risks and Test Signals

The main risk is register-generation drift or a stale manually defined index. Compile failures catch missing generated headers. Runtime signals are successful register reads for thermal and power-state functions on SMU10 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_baco.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_baco.c

## Purpose

This file implements SMU7 BACO/BAMACO support detection and state dispatch. BACO is the bus-active, chip-off low-power state used by supported AMD GPUs.

## Important APIs, Types, and Functions

`smu7_get_bamaco_support()` checks both the PowerPlay BACO platform capability and the BIF fuse strap before returning `BACO_SUPPORT`. `smu7_baco_get_state()` reads `mmBACO_CNTL` and maps `BACO_MODE` to `BACO_STATE_IN` or `BACO_STATE_OUT`. `smu7_baco_set_state()` dispatches to ASIC-specific implementations for Tonga, Fiji, Polaris, VegaM, and optionally CIK Bonaire/Hawaii.

## Control Flow and State

The file does not allocate memory or maintain driver-owned state. Runtime state lives in hardware registers and in ASIC-specific BACO implementation files. The set-state function is a switch on `adev->asic_type`.

## Dependencies and Integration

It depends on `amdgpu.h`, `common_baco.h` through the header, ASIC BACO helpers (`tonga_baco.h`, `fiji_baco.h`, `polaris_baco.h`, `ci_baco.h`), and BIF/SMU register masks. It integrates with the hwmgr BACO hooks selected for SMU7-class GPUs.

## Risks and Test Signals

Support is gated by both firmware platform caps and fuses; a mismatch can disable BACO even when an ASIC path exists. Unsupported ASICs return `-EINVAL`. Test signals include BACO capability reporting, register-observed state changes, suspend/runtime power transitions, and ASIC-specific BACO enter/exit validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_baco.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_baco.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_baco.h

## Purpose

This header declares the SMU7 BACO support, state query, and state transition functions.

## Important APIs, Types, and Functions

It exports `smu7_get_bamaco_support()`, `smu7_baco_get_state()`, and `smu7_baco_set_state()`. The state API uses `enum BACO_STATE` from `common_baco.h`.

## Control Flow and State

There is no logic or state in the header. It defines the BACO integration surface for SMU7 hwmgr code.

## Dependencies and Integration

The header includes `hwmgr.h` and `common_baco.h`, tying the API to the PowerPlay manager and shared BACO state definitions. ASIC-specific hwmgr files can include it to advertise or invoke BACO support.

## Risks and Test Signals

The API assumes callers pass valid `pp_hwmgr` and state pointers. Compile coverage verifies signatures; runtime signals are successful capability checks and BACO state transitions through the selected ASIC implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_baco.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_clockpowergating.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_clockpowergating.c

## Purpose

This file implements SMU7 clock and power gating controls for UVD, VCE, GFX, and selected graphics/system clock-gating blocks. It translates hwmgr power-gating requests and clock-gating bitfields into SMU messages and AMDGPU IP block state changes.

## Important APIs, Types, and Functions

Public functions include `smu7_disable_clock_power_gating()`, `smu7_powergate_uvd()`, `smu7_powergate_vce()`, `smu7_update_clock_gatings()`, and `smu7_powergate_gfx()`. Internal helpers enable/disable UVD/VCE DPM, update SMC UVD/VCE tables before ungating, and send UVD/VCE power-on/off messages. `smu7_update_clock_gatings()` decodes `PP_GROUP_*`, `PP_BLOCK_*`, `PP_STATE_*`, and support bits to send `PPSMC_MSG_EnableClockGatingFeature` or `PPSMC_MSG_DisableClockGatingFeature` with `CG_*` masks.

## Control Flow and State

UVD/VCE powergate paths update `struct smu7_hwmgr` booleans, gate or ungate AMDGPU IP block power and clock states, toggle DPM, and send SMU power messages in different orders for gate versus ungate. GFX per-CU power gating sends enable with the CU count or disable with no parameter. No memory is allocated.

## Dependencies and Integration

The file depends on `smu7_hwmgr.h`, `smu7_common.h`, SMU message sending, SMC table updates, platform cap checks, `phm_cf_want_*_power_gating()`, and AMDGPU IP power/clock gating APIs. It is used by SMU7 hwmgr function tables for media and graphics power management.

## Risks and Test Signals

Ordering matters: ungating updates SMC tables after power and clock ungate, while gating disables DPM before powerdown. `smu7_update_clock_gatings()` returns `-EINVAL` for unsupported group/block combinations and for failed SMU messages. Test signals include media playback resume after UVD/VCE gating, SMU message traces, clock-gating feature toggles, power-state sysfs behavior, and GPU stability on Polaris11 GFX CU power gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_clockpowergating.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_clockpowergating.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_clockpowergating.h

## Purpose

This header declares SMU7 clock and power gating functions for use by SMU7 hwmgr code.

## Important APIs, Types, and Functions

It declares `smu7_powergate_vce()`, `smu7_powergate_uvd()`, `smu7_powergate_acp()`, `smu7_powergate_gfx()`, `smu7_disable_clock_power_gating()`, and `smu7_update_clock_gatings()`. The ACP declaration is not implemented in the paired `smu7_clockpowergating.c`, so its definition must come from another SMU7 translation unit or the build would fail when referenced.

## Control Flow and State

The header has no control flow or state. The functions it declares mutate `struct smu7_hwmgr` backend booleans and hardware/SMU state in the implementation.

## Dependencies and Integration

It includes `smu7_hwmgr.h`, which supplies `struct pp_hwmgr`, backend definitions, and required SMU7 context. The declarations are consumed by SMU7 hwmgr function-table setup and clock-gating update paths.

## Risks and Test Signals

The public API mixes void powergate functions with int-returning ACP, disable, update, and GFX functions, so UVD/VCE media powergate errors are not propagated to callers. The unpaired ACP declaration is a linkage risk if no other object supplies it. Compile coverage catches signature and symbol drift; runtime test signals are UVD/VCE/GFX/ACP power-gating transitions and clock-gating SMU message success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_clockpowergating.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_dyn_defaults.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_dyn_defaults.h

## Purpose

This header defines default dynamic-power-management constants for SMU7 hardware manager behavior. These constants seed thresholds, hysteresis, display-watermark behavior, activity targets, and low-power defaults when firmware tables or runtime policy do not supply all values.

## Important APIs, Types, and Functions

There are no functions or types. The file defines default values for voting-rights clients, thermal protection counter, static-screen threshold, GFX idle clock-stop threshold, reference divider, ULV voltage-change delay, CG ULV parameter/control words, and target activity percentages for general, MCLK, and SCLK DPM policy.

## Control Flow and State

The file has no runtime control flow. Its constants become initial state when included by SMU7 hwmgr initialization code.

## Dependencies and Integration

It is a local configuration header for SMU7 hwmgr modules. The values integrate with SMU7 dynamic-state defaults and activity-based DPM policy setup.

## Risks and Test Signals

Hardcoded defaults can be wrong for board-specific tuning or firmware revisions. Because constants are compile-time, regressions surface as changed DPM behavior rather than direct failures. Test signals include stable idle clocks, appropriate activity-based SCLK/MCLK scaling, thermal protection behavior, and power consumption comparisons across SMU7 ASICs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_dyn_defaults.h -->
