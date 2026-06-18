# Research: subset-b-003534

Grouped research for AMDGPU SWSMU interface and SMU11 platform files. Each section preserves the exact source path in its title and is bounded for reconciliation into source-tree-aligned per-file outputs.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v15_0_8_pmfw.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v15_0_8_pmfw.h

## Purpose

`smu_v15_0_8_pmfw.h` is the SMU 15.0.8 PMFW interface header. It defines firmware-facing constants, feature IDs, telemetry dimensions, metric table versions, and packed/aligned table layouts that the SMU15 platform driver uses when exchanging data with PMFW. The file is a binary contract, not executable logic.

## Important APIs, Types, and Functions

The header exports DPM level counts for VCLK, DCLK, SOCCLK, LCLK, UCLK, FCLK, XGMI, PCIe, and guardband/margin tables; product/FRU string lengths; `FEATURE_ID_*` values through `NUM_FEATURES`; MGCG feature IDs; PCIe link-speed, GFX guardband, GFX DVM margin, system/node/SVI temperature, and system power enums. The main data types are packed/aligned `MetricsTable_t`, `SystemMetricsTable_t`, `VfMetricsTable_t`, `FRUProductInfo_t`, and `StaticMetricsTable_t`. Table version macros include `SMU_METRICS_TABLE_VERSION`, `SMU_SYSTEM_METRICS_TABLE_VERSION`, `SMU_VF_METRICS_TABLE_VERSION`, and `SMU_STATIC_METRICS_TABLE_VERSION`.

## Control Flow

There is no local control flow. Runtime flow is controlled by consumers such as `smu15/smu_v15_0_8_ppt.c`: the driver sends PPSMC messages, requests metric/static/system/VF tables, maps returned bytes onto these layouts, and then converts fields into hwmon, GPU metrics, RAS, NVML-style, and power-management values.

## State and Persistence Behavior

The file stores no runtime state. Its structures describe PMFW-owned snapshots and accumulators: temperature/power/frequency/activity counters, PCIe error accumulators, throttler residency counters, XGMI bandwidth accumulators, FRU identity strings, public serial numbers, PLDM version, and power limits. Values persist only in firmware/device state and in driver-side cached copies after table transfers.

## Dependencies

The header depends on Linux integer typedefs and compiler support for `__attribute__((packed, aligned(4)))` and `#pragma pack(push, 4)`. Consumers must pair it with SMU15 common code, `smu_v15_0_8_ppsmc.h`, and the correct PMFW driver-interface version. Array dimensions such as HBM, XCD, VCN, JPEG, and PCIe lanes are part of the ABI.

## Integration Points

It is directly included by the SMU15.0.8 PPT implementation, which uses the feature IDs and table definitions to validate firmware versions, request metrics, expose GPU metrics, query static inventory, handle system/node telemetry, and set or query power/frequency limits. The FRU/static metrics content also integrates with management tooling and RAS/monitoring surfaces.

## Risks and Edge Cases

The dominant risk is ABI drift: field order, packing, alignment, table version, and array counts must match PMFW exactly. Misinterpreting Celsius, millivolts, MHz, accumulators, or invalid sentinel values can report wrong telemetry or apply wrong limits. Several arrays are sized for multi-die/multi-XCD OAM platforms; consumers must bound indexes and respect unused sentinel fields. Feature IDs are numeric firmware protocol values and should not be renumbered.

## Test Signals

Useful signals include successful build of SMU15.0.8 code, driver-interface-version checks, metrics-version checks, table transfer success for metrics/system/static/VF tables, sane hwmon/GPU metrics values, FRU strings with expected bounds, and suspend/resume or reset paths that refresh cached metrics without layout faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v15_0_8_pmfw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v15_0_8_ppsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v15_0_8_ppsmc.h

## Purpose

`smu_v15_0_8_ppsmc.h` defines the SMU 15.0.8 PPSMC command and response namespace. It is the numeric protocol map used by the host driver when sending messages to PMFW through the common SMU message path.

## Important APIs, Types, and Functions

The header exports response codes `PPSMC_Result_OK`, `Failed`, `UnknownCmd`, `CmdRejectedPrereq`, and `CmdRejectedBusy`; message IDs from `PPSMC_MSG_TestMessage` through `PPSMC_MSG_SetSoftMaxFclk`; reset type arguments for driver mode 1/2/3 reset; PLPD mode arguments; and typedefs `PPSMC_Result` and `PPSMC_MSG` as `uint32_t`. Messages cover version queries, feature enablement, metric table transfer, driver/tools DRAM addresses, PPT limits, DRAM logging, resets, DF C-state, MCA/RAS queries, bad-page reporting, timestamps, system/static metrics, SDMA/VCN reset, fast PPT limits, and soft min/max GFX/GL2/FCLK controls.

## Control Flow

There is no executable control flow. SMU15 platform code maps generic `SMU_MSG_*` values to these numeric `PPSMC_MSG_*` IDs, then calls `smu_cmn_send_smc_msg*()` or table-transfer helpers. Firmware replies with the result codes defined here, and common SMU code translates transport/protocol failures into kernel return values.

## State and Persistence Behavior

The header has no local state. Messages change PMFW/device state when sent: allowed feature masks, soft frequency bounds, PPT limits, reset/recovery state, RAS table erase/clear-on-read behavior, timestamps, PLPD policy, and DRAM log locations. Address-setting commands persist in firmware until reset or overwritten.

## Dependencies

It depends only on fixed-width integer types and must match the corresponding SMU15.0.8 firmware. It is meaningful when included with `smu_v15_0_8_pmfw.h`, SMU15 common message-control initialization, and platform-specific message maps.

## Integration Points

The SMU15.0.8 PPT file includes this header to build the ASIC-specific message map. Common operations such as `GetSmuVersion`, `GetDriverIfVersion`, `SetDriverDramAddr`, `GetMetricsTable`, `SetPptLimit`, `GetStaticMetricsTable`, and reset/RAS flows ultimately use these IDs.

## Risks and Edge Cases

Numeric IDs are firmware ABI values; reordering or inserting without matching firmware support sends the wrong command. Some commands require multi-argument address or size setup, so callers must preserve ordering and 32-bit splitting. Commands such as `ClearMcaOnRead`, `EraseRasTable`, reset messages, and soft limit changes have device-wide side effects. `CmdRejectedBusy` and prerequisite failures need retry or graceful fallback rather than being treated as unknown commands.

## Test Signals

Build coverage catches missing names. Runtime validation should include SMU version/driver-interface checks, metrics table retrieval, feature-mask queries, PPT get/set round trips, reset recovery paths, and RAS/MCA command handling with expected PMFW response codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v15_0_8_ppsmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_11_0_cdr_table.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_11_0_cdr_table.h

## Purpose

`smu_11_0_cdr_table.h` provides two static 4096-byte PRBS7 CDR patterns for SMU11 memory dummy-table training: `NoDbiPrbs7` and `DbiPrbs7`. The data is copied by Navi10 PM code when constructing dummy memory tables for DBI and non-DBI modes.

## Important APIs, Types, and Functions

The file exports two `static unsigned int` arrays and no functions. `NoDbiPrbs7` contains repeating nibble patterns such as `0x0f0f0f0f`/`0xf0f0f0f0`; `DbiPrbs7` contains the corresponding DBI-transformed words. The arrays are deliberately 4096 bytes and documented as 256-byte aligned data, although the C declarations do not enforce an alignment attribute.

## Control Flow

No local control flow exists. `smu11/navi10_ppt.c` includes the header and selects one of the arrays, then copies `0x1000` bytes into a dummy table based on the memory/DBI path. The PMFW or memory-training path then consumes the table indirectly through SMU table upload.

## State and Persistence Behavior

The arrays are compile-time static data. Because they are defined in a header as `static`, each translation unit that includes it gets a private copy. The copied dummy table becomes transient driver/firmware state during training; the source arrays themselves are immutable except that they are not declared `const`.

## Dependencies

The file uses `#pragma pack(push, 1)`/`pop` and a simple include guard. It depends on consumers knowing the exact 4096-byte size and selecting the correct DBI variant. It has no dependency on SMU structures beyond the include site.

## Integration Points

The only direct integration found in this tree is `smu11/navi10_ppt.c`, where `memcpy(dummy_table, &NoDbiPrbs7[0], 0x1000)` or `memcpy(dummy_table, &DbiPrbs7[0], 0x1000)` seeds a PMFW dummy table.

## Risks and Edge Cases

The arrays are mutable static header definitions, so accidental writes in one translation unit would not affect others but could corrupt that unit's future training copies. Size assumptions are implicit; changing array length without changing the `0x1000` copy size can overrun or truncate. The comment says 256-byte aligned, but no attribute enforces it; consumers relying on source-array alignment instead of destination alignment would be fragile.

## Test Signals

Build coverage for `navi10_ppt.c`, static checks that both arrays are exactly 1024 `unsigned int` elements, memory-training smoke tests, and comparing uploaded dummy-table bytes against known-good PRBS7/DBI vectors are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_11_0_cdr_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_types.h

## Purpose

`smu_types.h` is the common SMU enumeration contract shared across AMDGPU SWSMU generations. It defines the generic `SMU_MSG_*`, `SMU_*CLK`, and `SMU_FEATURE_*_BIT` namespaces that platform-specific code maps onto ASIC/PMFW-specific command IDs and feature bits.

## Important APIs, Types, and Functions

The main macros are `SMU_MESSAGE_TYPES` and `SMU_FEATURE_MASKS`, each expanded through `__SMU_DUMMY_MAP` to create `enum smu_message_type` and `enum smu_feature_mask`. `enum smu_clk_type` lists clock domains such as GFXCLK, VCLK/DCLK pairs, SOCCLK, UCLK, DCEFCLK, DISPCLK, FCLK, PCIe, ISP, OD-specific entries, fan curve controls, and GL2CLK. Message flags `SMU_MSG_VF_FLAG`, `SMU_MSG_RAS_PRI`, `SMU_MSG_NO_PRECHECK` and firmware capability flag `SMU_FW_CAP_RAS_PRI` annotate special message behavior.

## Control Flow

The file has no runtime flow, but it drives mapping control flow. Platform files declare arrays such as `cmn2asic_msg_mapping`, `cmn2asic_mapping` clock maps, table maps, feature maps, and workload maps indexed by these enums. Helpers like `smu_cmn_to_asic_specific_index()`, `smu_cmn_send_smc_msg*()`, and feature-mask routines use the generic enum as the frontend contract and reject or translate unsupported entries.

## State and Persistence Behavior

No state is stored here. The enums name state controlled elsewhere: firmware-enabled feature masks, frequency domains, power profile choices, RAS-priority command handling, and message precheck policy. The numeric order of enum members persists as an in-kernel ABI between common code and every platform mapping table.

## Dependencies

This header is consumed by `amdgpu_smu.h`, SMU generation headers, and all platform PPT implementations. It relies on every mapping table being sized to `SMU_MSG_MAX_COUNT`, `SMU_CLK_COUNT`, or `SMU_FEATURE_COUNT` and initialized consistently.

## Integration Points

Arcturus, Cyan Skillfish, Navi, Sienna, SMU13, SMU14, and SMU15 files all map subsets of these messages/features to PMFW IDs. User-facing sysfs and hwmon operations often begin with a generic `SMU_*` clock or message and then flow through these maps.

## Risks and Edge Cases

Adding or reordering enum entries can silently break array-indexed mappings if all tables are not updated. Some generic messages are valid only for specific generations, virtual functions, or RAS-priority firmware. Feature names are broad and sometimes generation-specific despite sharing a common enum; unsupported entries must remain unmapped rather than assumed available.

## Test Signals

Compile-time array-size coverage, platform boot probes, message-map lookup tests, feature enable/disable smoke tests, and sysfs clock/OD operations across multiple ASIC generations are the best validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v11_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v11_0.h

## Purpose

`smu_v11_0.h` declares the common SMU11 support layer used by SMU11 platform PPT files. It provides MP aperture/register constants, thermal defaults, DPM/power context structures, and prototypes for the shared SMU11 lifecycle, table, power, clock, fan, BACO, reset, and interrupt helpers.

## Important APIs, Types, and Functions

Important constants include MP0/MP1 aperture bases, `smnMP1_FIRMWARE_FLAGS`, `smnMP0_FW_INTF`, `smnMP1_PUB_CTRL`, `TEMP_RANGE_*`, `SMU11_TOOL_SIZE`, PCIe link limits, CTF offsets, and the `link_width` decode table. Types include `smu_11_0_max_sustainable_clocks`, `smu_11_0_dpm_tables`, `smu_11_0_dpm_context`, `smu_11_0_power_state`, `smu_11_0_power_context`, and `smu_11_5_power_context`. Prototypes cover microcode load/fini, SMC table init/fini, power init/fini, firmware status, PPT setup, boot values, table address notification, feature control, DPM table queries, power limits, thermal alerts, fan control, XGMI, GFXOFF, BACO, mode1 reset, soft/hard frequency ranges, PCIe queries, deep sleep, passthrough SBR, user OD restore, and message-control initialization.

## Control Flow

There is no implementation in the header. Platform files install `pptable_funcs` and delegate common steps to these functions: initialize microcode, allocate/init SMU tables, parse VBIOS powerplay data, program table locations, enable features, service sysfs/hwmon requests, send SMC messages, and handle interrupts/reset/suspend paths.

## State and Persistence Behavior

The structures define persistent driver-side state stored under `smu_context`: cached DPM tables, workload policy mask, deep-sleep DCEF clock, power source, power state, boost mode, and fast PPT limits for SMU11.5. Firmware/device state is changed by the declared functions but not stored in this header.

## Dependencies

It includes `amdgpu_smu.h` and is gated by `SWSMU_CODE_LAYER_L2`/`L3` for function prototypes. Consumers depend on SMU11 PMFW headers, PPTable layouts, SOC15 register helpers, and common SMU message/table infrastructure.

## Integration Points

`smu11/arcturus_ppt.c`, `navi10_ppt.c`, `sienna_cichlid_ppt.c`, `vangogh_ppt.c`, `cyan_skillfish_ppt.c`, and `smu_v11_0.c` use this header as the shared generation layer. It is the bridge between AMDGPU PM core and ASIC-specific platform code.

## Risks and Edge Cases

The header declares broad behavior across several ASICs, but not every helper is valid for every platform. Platform `pptable_funcs` must set unsupported hooks to `NULL` or provide guards. DPM table and PCIe bounds must match firmware table sizes. Thermal constants are defaults and must be overwritten from PPTable limits where available.

## Test Signals

SMU11 platform build coverage, boot probe on each SMU11 ASIC, sysfs clock/fan/power tests, BACO/reset/suspend-resume tests, and firmware-version compatibility checks validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v11_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v11_0_7_pptable.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v11_0_7_pptable.h

## Purpose

`smu_v11_0_7_pptable.h` defines the packed VBIOS PowerPlay table layout for SMU 11.0.7/Sienna Cichlid style boards. It describes driver-side table metadata, platform capabilities, thermal-controller IDs, power-saving clock bounds, OverDrive capabilities/settings, optimized power mode data, and the embedded PMFW `PPTable_t`.

## Important APIs, Types, and Functions

The file exports `SMU_11_0_7_TABLE_FORMAT_REVISION`, platform-cap bits for PowerPlay/SBIOS power source/hardware DC/BACO/MACO/shadow pstate, thermal controller IDs, OverDrive and power-saving-clock versions, OD capability and feature enums, OD setting enums, power-mode setting enums, and PP clock IDs. Key structures are `smu_11_0_7_overdrive_table`, `smu_11_0_7_power_saving_clock_table`, and packed `smu_11_0_7_powerplay_table` ending in `PPTable_t smc_pptable`.

## Control Flow

There is no code flow. Sienna Cichlid PPT code includes the header, parses a VBIOS table into this layout, copies or references the embedded PMFW table, and exposes OD/power-saving constraints to sysfs and common SMU helpers.

## State and Persistence Behavior

The header stores no state. Parsed instances persist in `smu_table_context` as VBIOS-derived board policy: platform caps, shutdown temperature, OD bounds, fan curve points, power modes, and PMFW SKU data. Firmware receives the embedded PMFW table through SMU table upload.

## Dependencies

It requires `atom_common_table_header` and `PPTable_t` from the SMU11 driver interface. Packing is part of the binary ABI; field order, reserve sizes, and array maxima are not arbitrary.

## Integration Points

Direct include is `smu11/sienna_cichlid_ppt.c`. It integrates with AMDGPU PPTable parsing, OverDrive sysfs, fan policy, BACO/MACO platform-cap checks, power-saving clock reporting, and PMFW table transfer.

## Risks and Edge Cases

Changing enum order or struct packing breaks VBIOS parsing. Some OD enum names use the base `SMU_11_0` prefix for auto fan acoustic limit, so consumers must use the exact identifiers. `feature_count` and `setting_count` must be validated against fixed array sizes. Firmware/BIOS table revision mismatches should fail cleanly.

## Test Signals

Build Sienna Cichlid PM code, parse known VBIOS PowerPlay tables, verify OD range/sysfs output, check fan curve and power-mode controls, and confirm PMFW accepts the embedded `PPTable_t`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v11_0_7_pptable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v11_0_pptable.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v11_0_pptable.h

## Purpose

`smu_v11_0_pptable.h` is the base packed PowerPlay table layout for early SMU11 boards such as Navi10/Arcturus users of the common SMU11 PPTable contract. It combines VBIOS metadata, platform capabilities, board power limits, power-saving clocks, OverDrive limits, and optionally the PMFW `PPTable_t`.

## Important APIs, Types, and Functions

It defines `SMU_11_0_TABLE_FORMAT_REVISION`, platform-cap bits, `SMU_11_0_PP_THERMALCONTROLLER_NONE`, OverDrive and power-saving-clock versions, OD capability/feature/setting enums, PP clock IDs, and maxima for OD features/settings and PP clocks. Structures are `smu_11_0_overdrive_table`, `smu_11_0_power_saving_clock_table`, and packed `smu_11_0_powerplay_table`. The `SMU_11_0_PARTIAL_PPTABLE` guard can omit the embedded PMFW table for partial parsing.

## Control Flow

No executable flow is present. Platform setup routines call common SMU11 PPTable parsing, cast the result to this layout, copy `smc_pptable` into `driver_pptable`, append supplemental atom BIOS DPM data where needed, and then upload the PMFW table.

## State and Persistence Behavior

The parsed table becomes persistent driver policy for the GPU lifetime: power limits, software shutdown temperature, platform caps, thermal controller type, OD bounds, and power-saving clock ranges. The header itself stores no state.

## Dependencies

It depends on the ATOM common table header and a visible `PPTable_t` definition unless partial mode is enabled. Exact `#pragma pack(push, 1)` layout is required for VBIOS binary compatibility.

## Integration Points

Direct includes include `smu11/navi10_ppt.c` and `smu11/arcturus_ppt.c`. Arcturus uses it to copy `powerplay_table->smc_pptable`, check BACO/MACO/fan support, read `software_shutdown_temp`, and derive thermal/power limits.

## Risks and Edge Cases

The same base layout is reused by multiple ASIC paths; platform-specific assumptions must stay in platform code. Wrong table revision or reserve sizing can offset `smc_pptable`. OD feature arrays are fixed size and must be bounded by counts. A missing `PPTable_t` definition will break non-partial builds.

## Test Signals

Build Navi10 and Arcturus PM, parse real VBIOS tables, validate thermal/power/fan caps, verify OD range reporting, and confirm table upload to PMFW succeeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v11_0_pptable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v12_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v12_0.h

## Purpose

`smu_v12_0.h` declares the compact shared SMU12 generation interface. It provides MP aperture constants and prototypes for firmware status, power-gating, GFXOFF/CGPG control, default DPM table setup, mode2 reset, soft frequency range, driver table location, VBIOS boot values, and message-control initialization.

## Important APIs, Types, and Functions

The exported prototypes are `smu_v12_0_check_fw_status`, `powergate_sdma`, `powergate_vcn`, `powergate_jpeg`, `set_gfx_cgpg`, `get_gfxoff_status`, `gfx_off_control`, `fini_smc_tables`, `set_default_dpm_tables`, `mode2_reset`, `set_soft_freq_limited_range`, `set_driver_table_location`, `get_vbios_bootup_values`, and `init_msg_ctl`.

## Control Flow

The header contains no implementation. SMU12 platform code installs a PPT function table and delegates common lifecycle and power-gating actions to the declared helpers. Message-control initialization wires generic messages to the platform's PMFW IDs.

## State and Persistence Behavior

No local state is defined. The functions mutate firmware/device state: media and SDMA power gates, GFXOFF/CGPG state, DPM limits, table addresses, and reset state. Driver-side SMU context stores any resulting cached state.

## Dependencies

It includes `amdgpu_smu.h` and exposes prototypes only for `SWSMU_CODE_LAYER_L2`/`L3` builds. Consumers need common SMU infrastructure and the appropriate SMU12 PMFW/PPSMC headers.

## Integration Points

This is the generation layer between SMU12 platform PPT files and AMDGPU PM core. Common hooks are used by sysfs/hwmon requests, suspend/resume, reset paths, and media power-management code.

## Risks and Edge Cases

The smaller SMU12 API surface means callers should not assume SMU11/13 helpers exist. Power-gating and reset calls must be serialized through PM mutexes where required by the implementation. Soft frequency limits are meaningful only for clock types supported by the platform message map.

## Test Signals

SMU12 platform build, boot firmware-status check, SDMA/VCN/JPEG power-gate toggles, GFXOFF status transitions, mode2 reset, and sysfs frequency-limit tests validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v12_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v13_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v13_0.h

## Purpose

`smu_v13_0.h` declares the shared SMU13 generation interface. It extends the SMU11-style contract with SMU13 firmware flag addresses, Q10 conversion helpers, PCIe decode arrays, DPM/power contexts with capability and board-voltage fields, and prototypes for common lifecycle, table, power, fan, media, BACO, reset, WBRF, UCLK shadow, and interrupt work.

## Important APIs, Types, and Functions

Important constants include MP aperture bases, firmware flag registers, `SMU13_TOOL_SIZE`, `MAX_PCIE_CONF`, CTF offsets, `SMU_13_VCLK_SHIFT`, `SMUQ10_*` helpers, and `SMU_V13_SOFT_FREQ_ROUND`. Types include `smu_13_0_max_sustainable_clocks`, `smu_13_0_dpm_tables`, `smu_13_0_dpm_context`, `smu_13_0_power_state`, and `smu_13_0_power_context` with `atomic_t throttle_status`. Prototypes cover microcode, SMC tables, power, PPTable setup, boot values, table locations, feature control, power limits, thermal alerts, VDD/fan control, XGMI, GFXOFF, BACO, DPM queries, VCN/JPEG, BTC, GPO, deep sleep, IMU power-up, OD editing, mode1 reset, firmware PPTable retrieval, PCIe parameter update, PMFW-state disable, UCLK shadow, WBRF exclusion ranges, boot frequency queries, interrupt work, and custom level reset.

## Control Flow

The header defines no code flow. Platform files in `smu13/` install their function tables and delegate common operations to these helpers. A typical probe path initializes microcode, SMC tables, power contexts, parses or retrieves PPTable data, sets table addresses, enables features, populates DPM tables, and exposes sysfs/hwmon operations.

## State and Persistence Behavior

SMU13 DPM context persists DPM tables, workload policy, deep-sleep DCEF clock, capability bits, and board voltage. Power context persists power source, boost mode, power state, and atomic throttle state. Firmware state is changed through the declared helpers and reflected in metrics or cached tables.

## Dependencies

It includes `amdgpu_smu.h` and depends on common SMU mapping/message infrastructure plus platform-specific PMFW/PPSMC/PPTable headers. Decode macros rely on external arrays `pmfw_decoded_link_speed` and `pmfw_decoded_link_width`.

## Integration Points

`smu13/aldebaran_ppt.c`, `smu_v13_0_0_ppt.c`, `smu_v13_0_7_ppt.c`, and common `smu_v13_0.c` use this header. It integrates with sysfs clocks, fan/hwmon, BACO, reset, WBRF radio-frequency exclusion, display/media power, and GPU metrics.

## Risks and Edge Cases

Array-indexed link decode must validate firmware indexes. Q10 conversions can lose precision if callers mix fixed-point and integer units. The API spans dGPU and APU variants; unsupported hooks must be guarded. Atomic throttle state requires consistent update/read semantics across interrupt and sysfs contexts.

## Test Signals

SMU13 platform builds, probe and firmware-version checks, PPTable parsing/retrieval, DPM sysfs, media power toggles, mode1 reset, UCLK shadow, WBRF exclusion, thermal alert, and GPU metrics validation provide coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v13_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v13_0_0_pptable.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v13_0_0_pptable.h

## Purpose

`smu_v13_0_0_pptable.h` defines the packed PowerPlay table layout for SMU13.0.0/Navi21-style platforms. It describes VBIOS metadata, platform caps, thermal controller, power limits, OverDrive 8.3 capabilities/settings, fan curve and power-mode settings, per-zone GFX voltage offset controls, and embedded PMFW `PPTable_t`.

## Important APIs, Types, and Functions

Exports include `SMU_13_0_0_TABLE_FORMAT_REVISION`, platform-cap bits, thermal-controller IDs, OD/power-saving-clock versions, OD capability and feature enums, OD setting enums including fan curve points and per-zone voltage-offset points, power-mode setting enums, PP clock IDs, `smu_13_0_0_overdrive_table`, and packed `smu_13_0_0_powerplay_table`.

## Control Flow

No executable flow exists. `smu13/smu_v13_0_0_ppt.c` parses VBIOS bytes with this layout, uses OD bounds for sysfs, and transfers the embedded PMFW table to firmware.

## State and Persistence Behavior

Parsed table instances persist as driver policy for platform caps, OD bounds, power modes, fan settings, shutdown temperature, and PMFW SKU data. The header itself has no state.

## Dependencies

It requires `atom_common_table_header` and `PPTable_t`; struct packing and reserve sizes are binary ABI. The `padding` fields are intentional layout stabilizers.

## Integration Points

Direct integration is the SMU13.0.0 PPT implementation. It feeds AMDGPU OverDrive, power-limit, fan, thermal, BACO/MACO, and PMFW table-upload paths.

## Risks and Edge Cases

The table has many fixed-size OD arrays; counts must not exceed maxima. Per-zone voltage offsets and fan curve settings require strict unit and range handling. Any field insertion before `smc_pptable` changes PMFW table offset. Revision mismatches must be rejected or handled explicitly.

## Test Signals

Build SMU13.0.0 PM, parse known Navi21 VBIOS tables, validate OD sysfs ranges, fan curve/power mode behavior, per-zone voltage offset limits, and successful PMFW PPTable upload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v13_0_0_pptable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v13_0_7_pptable.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v13_0_7_pptable.h

## Purpose

`smu_v13_0_7_pptable.h` defines the packed PowerPlay table layout for SMU13.0.7/Plum Bonito-style platforms. It describes VBIOS metadata, platform caps, thermal controller, power limits, OverDrive 8.3 capabilities/settings, fan curve and power-mode settings, per-zone GFX voltage offset controls, and embedded PMFW `PPTable_t`.

## Important APIs, Types, and Functions

Exports include `SMU_13_0_7_TABLE_FORMAT_REVISION`, platform-cap bits, thermal-controller IDs, OD/power-saving-clock versions, OD capability and feature enums, OD setting enums including fan curve points and per-zone voltage-offset points, power-mode setting enums, PP clock IDs, `smu_13_0_7_overdrive_table`, and packed `smu_13_0_7_powerplay_table`.

## Control Flow

No executable flow exists. `smu13/smu_v13_0_7_ppt.c` parses VBIOS bytes with this layout, uses OD bounds for sysfs, and transfers the embedded PMFW table to firmware.

## State and Persistence Behavior

Parsed table instances persist as driver policy for platform caps, OD bounds, power modes, fan settings, shutdown temperature, and PMFW SKU data. The header itself has no state.

## Dependencies

It requires `atom_common_table_header` and `PPTable_t`; struct packing and reserve sizes are binary ABI. The `padding` fields are intentional layout stabilizers.

## Integration Points

Direct integration is the SMU13.0.7 PPT implementation. It feeds AMDGPU OverDrive, power-limit, fan, thermal, BACO/MACO, and PMFW table-upload paths.

## Risks and Edge Cases

The table has many fixed-size OD arrays; counts must not exceed maxima. Per-zone voltage offsets and fan curve settings require strict unit and range handling. Any field insertion before `smc_pptable` changes PMFW table offset. Revision mismatches must be rejected or handled explicitly.

## Test Signals

Build SMU13.0.0 PM, parse known Plum Bonito VBIOS tables, validate OD sysfs ranges, fan curve/power mode behavior, per-zone voltage offset limits, and successful PMFW PPTable upload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v13_0_7_pptable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v13_0_pptable.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v13_0_pptable.h

## Purpose

`smu_v13_0_pptable.h` is the base packed PowerPlay table layout for SMU13 platforms that use the older, SMU11-like OD/power-saving schema. It defines VBIOS metadata, platform caps, thermal-controller type, power limits, power-saving clock ranges, OverDrive bounds, and optionally the embedded PMFW `PPTable_t`.

## Important APIs, Types, and Functions

It exports `SMU_13_0_TABLE_FORMAT_REVISION`, platform-cap bits, thermal-controller constants, OD/power-saving-clock versions, OD capability/feature/setting enums, PP clock IDs, `smu_13_0_overdrive_table`, `smu_13_0_power_saving_clock_table`, and packed `smu_13_0_powerplay_table`. `SMU_13_0_PARTIAL_PPTABLE` can omit `PPTable_t smc_pptable` for partial parsing.

## Control Flow

There is no local control flow. `smu13/aldebaran_ppt.c` includes it, parses the VBIOS powerplay table, copies or references the embedded PMFW table, and exposes the driver-facing constraints through common SMU helpers.

## State and Persistence Behavior

The parsed table persists under `smu_table_context` as board policy: platform caps, shutdown temperature, OD ranges, power-saving clocks, and PMFW table data. Firmware receives the embedded `PPTable_t` through table upload.

## Dependencies

It depends on `atom_common_table_header`, `PPTable_t`, and 1-byte packing. The layout mirrors firmware/BIOS expectations and must not be treated as a normal extensible C struct.

## Integration Points

Aldebaran SMU13 code uses this contract for PPTable setup, OverDrive and power-saving clock reporting, BACO/MACO/platform-cap checks, and PMFW table upload.

## Risks and Edge Cases

This base schema lacks newer OD features present in SMU13.0.0/13.0.7. Consumers must use the header matching the ASIC and VBIOS format. OD count fields require bounds checks, and table revision/format mismatches should not be silently accepted.

## Test Signals

Build Aldebaran PM code, parse real VBIOS tables, verify OD/power-saving-clock output, validate thermal/power limits, and confirm PMFW accepts the uploaded table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v13_0_pptable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v14_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v14_0.h

## Purpose

`smu_v14_0.h` declares the shared SMU14 generation interface. It mirrors the SMU13/15 common lifecycle contract with SMU14 register constants, DPM and power contexts, PCIe decode helpers, and function prototypes for microcode, SMC tables, power, PPTable, DPM, BACO, media, thermal, and OD behavior.

## Important APIs, Types, and Functions

Important constants include `FEATURE_MASK`, MP aperture bases, SMU14 firmware flag registers, `MAX_PCIE_CONF`, `SMU14_TOOL_SIZE`, CTF offsets, `DECODE_GEN_SPEED`, `DECODE_LANE_WIDTH`, and `SMU_V14_SOFT_FREQ_ROUND`. Types include `smu_14_0_max_sustainable_clocks`, `smu_14_0_dpm_tables`, `smu_14_0_dpm_context`, `smu_14_0_power_state`, and `smu_14_0_power_context`. Prototypes cover init/load/fini microcode, SMC tables, power, firmware status, PPTable setup/retrieval, boot values, table locations, feature control, display notification, power limits, GFXOFF, IRQ, BACO, DPM frequency limits, performance level, power source, media enablement, BTC, GPO/deep sleep, IMU power-up, default DPM tables, OD editing, and thermal alerts.

## Control Flow

The header contains declarations only. SMU14 platform implementations install hooks in `pptable_funcs` and delegate common operations to these functions through AMDGPU PM core calls.

## State and Persistence Behavior

DPM context persists clock tables, workload policy mask, and deep-sleep DCEF clock. Power context persists power source, boost mode, and power state. Firmware/device state changes occur in the implementation files, not in the header.

## Dependencies

It includes `amdgpu_smu.h`, depends on external decode arrays `decoded_link_speed`/`decoded_link_width`, and is gated by `SWSMU_CODE_LAYER_L2`/`L3` for prototypes.

## Integration Points

SMU14 platform files, especially `smu14/smu_v14_0_2_ppt.c` and common `smu_v14_0.c`, use this header to connect PMFW, PPTable, sysfs, hwmon, reset, and display/media power-management paths.

## Risks and Edge Cases

`FEATURE_MASK` is also defined in nearby generation headers; include order should avoid macro redefinition surprises. Decode macros assume valid indexes. Unsupported hooks must be omitted or guarded for specific SMU14 ASICs.

## Test Signals

Build SMU14 PM, probe firmware, parse/retrieve PPTable, exercise DPM sysfs, power-limit and OD paths, media power toggles, BACO/reset, and thermal alert enable/disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v14_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v14_0_2_pptable.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v14_0_2_pptable.h

## Purpose

`smu_v14_0_2_pptable.h` defines the packed PowerPlay table layout for SMU14.0.2/14.0.3-era platforms. It is richer than earlier layouts: it records PMFW PPTable/SKU/board/custom SKU offsets and sizes, source of the table, platform caps including LED/mobile OD, two-tier basic/advanced OD bounds, custom OD data, and embedded PMFW `PPTable_t`/`CustomSkuTable_t` payloads.

## Important APIs, Types, and Functions

Exports include table format revisions, platform-cap bits, thermal-controller constants, OD/custom OD versions, OD software feature capability/feature/setting enums, power-mode setting enums, `smu_14_0_2_overdrive_table_id`, `smu_14_0_2_overdrive_table`, `smu_14_0_3_pptable_source`, packed `smu_14_0_2_powerplay_table`, custom OD enums, `smu_14_0_2_custom_overdrive_table`, and `smu_14_0_3_custom_powerplay_table`.

## Control Flow

There is no executable code. `smu14/smu_v14_0_2_ppt.c` parses the layout, uses offset/size fields to locate PMFW SKU/board/custom tables, exposes OD and custom OD ranges, and uploads firmware-facing table data.

## State and Persistence Behavior

Parsed instances persist in driver table context as board policy and firmware payload. Offset fields identify substructures inside the PMFW table; custom table data persists as user/firmware policy until replaced or reset.

## Dependencies

It depends on `atom_common_table_header`, `PPTable_t`, and `CustomSkuTable_t` from the SMU14 PMFW driver interface. Packing and the comment requiring PMFW table 32-byte alignment are part of the ABI.

## Integration Points

Direct consumer is the SMU14.0.2 PPT implementation. It integrates with IFWI/driver-hardcoded/registry PPTable sourcing, AMDGPU OverDrive, power-mode policy, custom SKU handling, and PMFW table transfer.

## Risks and Edge Cases

The table has many absolute offsets and sizes; parsers must validate bounds before dereferencing. The comment says `table_size` offset and PMFW alignment must remain stable. Basic/advanced OD arrays have separate bounds and caps, so sysfs must select the right tier. The OverDrive version is marked TODO/TBD, which increases compatibility risk with firmware and PPGen.

## Test Signals

Build SMU14.0.2 PM, parse IFWI and registry/hardcoded PPTable sources, validate subtable offset bounds, verify OD basic/advanced range reporting, test custom power-mode data, and confirm PMFW accepts uploaded table bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v14_0_2_pptable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v15_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v15_0.h

## Purpose

`smu_v15_0.h` declares the shared SMU15 generation interface. It defines SMU15 driver-interface version constants, MP aperture/register constants, DPM/power contexts including GL2 clock support, and prototypes for common SMU15 microcode, SMC table, PPTable, DPM, power, BACO, media, OD, and thermal operations.

## Important APIs, Types, and Functions

Key constants include `SMU15_DRIVER_IF_VERSION_INV`, `SMU15_DRIVER_IF_VERSION_SMU_V15_0`, `SMU15_DRIVER_IF_VERSION_SMU_V15_0_8`, `FEATURE_MASK`, MP aperture bases, `smnMP1_FIRMWARE_FLAGS`, `smnMP1_PUB_CTRL`, `MAX_PCIE_CONF`, `SMU15_TOOL_SIZE`, CTF offsets, and decode macros. Types include `smu_15_0_max_sustainable_clocks`, `smu_15_0_dpm_tables` with `gl2_table`, `smu_15_0_dpm_context` with `caps` and `board_volt`, `smu_15_0_power_state`, and `smu_15_0_power_context` with atomic throttle status. Prototypes mirror SMU14 plus SMU15-specific PPTable retrieval and OD editing.

## Control Flow

No implementation lives here. SMU15 platform code installs `pptable_funcs`, initializes message maps, loads firmware, creates SMC/driver tables, sets DRAM table locations, exchanges PMFW tables, enables features, and services user-facing PM operations through these declared helpers.

## State and Persistence Behavior

The DPM context persists per-clock tables, workload mask, deep-sleep DCEF clock, caps, and board voltage. Power context persists power source, boost mode, power state, and throttle status. Firmware state is modified by implementations through SMC messages and table transfers.

## Dependencies

It includes `amdgpu_smu.h`, relies on common SMU infrastructure, and pairs with SMU15 PMFW/PPSMC headers such as `smu_v15_0_8_pmfw.h` and `smu_v15_0_8_ppsmc.h`. The duplicate `FEATURE_MASK` definition is harmless only if identical.

## Integration Points

`smu15/smu_v15_0.c` and `smu15/smu_v15_0_8_ppt.c` use this header to connect PMFW protocol, GPU metrics, clock/thermal/power sysfs, reset, media, and table-management paths.

## Risks and Edge Cases

Driver-interface versions must match PMFW expectations. `enum smu_15_0_power_state` uses lowercase enum constants unlike earlier headers, so copy/paste assumptions can break builds. GL2 clock handling requires callers to include the new table and map entries. As with other generations, unsupported hooks need platform guards.

## Test Signals

Build SMU15 code, probe SMU15.0.8 firmware, verify driver-interface version checks, table address setup, metrics/static/system table transfers, DPM/sysfs behavior including GL2, power-limit changes, reset/BACO, and thermal alerts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v15_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/Makefile

## Purpose

`smu11/Makefile` wires SMU11 platform manager objects into the AMDGPU powerplay build. It names the SMU11 PPT implementations and common SMU11 implementation object, prefixes them with `$(AMD_SWSMU_PATH)/smu11/`, and appends the result to `AMD_POWERPLAY_FILES`.

## Important APIs, Types, and Functions

The file defines `SMU11_MGR` with `arcturus_ppt.o`, `navi10_ppt.o`, `sienna_cichlid_ppt.o`, `vangogh_ppt.o`, `cyan_skillfish_ppt.o`, and `smu_v11_0.o`; defines `AMD_SWSMU_SMU11MGR` via `$(addprefix ...)`; and appends to `AMD_POWERPLAY_FILES`.

## Control Flow

Build-system flow is linear: Kbuild includes this makefile, expands the object list, prefixes paths, and links the selected objects into the AMDGPU driver according to the surrounding build configuration.

## State and Persistence Behavior

There is no runtime state. The persistent effect is build composition: removing an object drops that platform's PPT function installer/common implementation from the driver image.

## Dependencies

It depends on the parent AMDGPU makefiles defining `AMD_SWSMU_PATH` and `AMD_POWERPLAY_FILES`. The listed object names must correspond to C files in the same directory.

## Integration Points

This is the build integration point for all SMU11 platform files, including the Arcturus and Cyan Skillfish sources in this work item. Higher-level AMDGPU build rules consume `AMD_POWERPLAY_FILES`.

## Risks and Edge Cases

A missing object breaks platform support at link or runtime dispatch time. Adding a new SMU11 platform requires updating this list. Renames must keep path prefixing consistent with `AMD_SWSMU_PATH`.

## Test Signals

Kernel build of AMDGPU with powerplay enabled, link success, and boot probing on SMU11 ASICs confirm the makefile coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/arcturus_ppt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/arcturus_ppt.c

## Purpose

`arcturus_ppt.c` is the Arcturus-specific SMU11 powerplay table implementation. It installs the Arcturus `pptable_funcs`, maps generic SMU messages/features/tables/clocks/workloads to Arcturus PMFW IDs, initializes SMU driver tables, parses and stores the PowerPlay table, builds DPM state, exposes sensors/clock levels/fan controls/power profiles/GPU metrics, handles SMU-backed I2C, and delegates common lifecycle work to `smu_v11_0` helpers.

## Important APIs, Types, and Functions

Important static maps include `arcturus_message_map`, `arcturus_clk_map`, `arcturus_feature_mask_map`, `arcturus_table_map`, `arcturus_pwr_src_map`, `arcturus_workload_map`, and `arcturus_throttler_map`. Initialization paths are `arcturus_tables_init`, `arcturus_allocate_dpm_context`, `arcturus_init_smc_tables`, and `arcturus_init_allowed_features`. PPTable paths are `arcturus_setup_pptable`, `arcturus_store_powerplay_table`, `arcturus_append_powerplay_table`, `arcturus_check_powerplay_table`, `arcturus_check_bxco_support`, and `arcturus_check_fan_support`. Runtime hooks include DPM table setup, metrics access, clock-level emission/forcing, thermal range, sensors, fan PWM/RPM get/set, power limit/profile handling, VCN DPM, I2C adapter operations, unique ID query, DF C-state control, thermal throttling logging, PCIe speed query, GPU metrics export, and `arcturus_set_ppt_funcs`.

## Control Flow

Probe/setup calls `arcturus_set_ppt_funcs`, which assigns function/mapping tables and initializes message control with SMU11 common code. `init_smc_tables` allocates VRAM driver tables for PPTable, PMSTATUSLOG, metrics, I2C commands, and activity monitor coefficients, then allocates DPM/policy contexts and calls `smu_v11_0_init_smc_tables`. `setup_pptable` runs common SMU11 parsing, copies the embedded `smc_pptable`, appends atom BIOS DPM data, checks BACO/MACO and fan support, then later common code uploads tables and enables features. User-facing calls flow through `pptable_funcs` to metrics reads, DPM table lookups, SMC messages, or THM/MMIO register operations.

## State and Persistence Behavior

Persistent driver state includes allocated metrics and GPU metrics tables, driver PPTable, DPM context, PLPD policy mask/current level, `adev->pm.no_fan`, BACO platform support, fan maximum RPM, custom profile parameters, SMU I2C adapter registrations, RAS/FRU I2C bus pointers, and `adev->unique_id`. Firmware/device state is changed by feature masks, soft frequency limits, power limits, workload masks, fan mode/register writes, DF C-state messages, XGMI PLPD policy, VCN DPM toggles, I2C command table transfers, and BTC/reset-related common helpers.

## Dependencies

The file depends on AMDGPU core, atom firmware/BIOS helpers, common SMU code, SMU11 common functions, Arcturus driver-interface and PPSMC headers, SMU11 PPTable layout, NBIO/THM SOC15 register definitions, XGMI, RAS, Linux I2C, PCI, and mutex/ktime helpers. Firmware-version guards are embedded for PLPD, DF C-state, ReadSerial, and clock forcing.

## Integration Points

It is compiled through `smu11/Makefile` and selected by AMDGPU platform dispatch. It integrates with sysfs clock/OD/power profile paths, hwmon sensor reads, GPU metrics ioctl/sysfs paths, RAS EEPROM and FRU EEPROM I2C, KFD SMI throttling events, BACO/MACO platform support, XGMI PLPD policy, and common SMU11 lifecycle hooks.

## Risks and Edge Cases

Several operations are firmware-version gated; ignoring those checks can send unsupported commands. Clock forcing is intentionally disabled for PMFW 54.18 through 54.26. DPM table indexes derived from masks must be bounds-checked. Metrics use different current vs average fields depending on DPM enablement. Fan RPM/PWM code directly manipulates THM registers and has 0-RPM workarounds based on user flags. The I2C command builder must respect `MAX_SW_I2C_COMMANDS`, restart/stop semantics, DPM-enabled state, and PM mutex serialization. PPTable copying assumes the SMU11 layout and `PPTable_t` size match firmware.

## Test Signals

Build and boot on Arcturus, firmware-version compatibility logs, PPTable parsing/upload, DPM table/sysfs output, clock forcing rejection on affected firmware, fan PWM/RPM get/set, GPU metrics v1.3 sanity, RAS/FRU I2C access, XGMI PLPD policy toggles, DF C-state messages, thermal throttling logs/KFD SMI events, suspend/resume, reset, and BACO paths are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/arcturus_ppt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/arcturus_ppt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/arcturus_ppt.h

## Purpose

`arcturus_ppt.h` declares the Arcturus PPT installer and local DPM table structures used by the Arcturus SMU11 implementation. It gives the `.c` file and any selector code the function needed to attach Arcturus-specific `pptable_funcs` to an SMU context.

## Important APIs, Types, and Functions

The header defines UMD pstate indexes for GFXCLK, SOCCLK, and MCLK, `MAX_DPM_NUMBER`, `MAX_PCIE_CONF`, `arcturus_dpm_level`, `arcturus_dpm_state`, `arcturus_single_dpm_table`, `arcturus_pcie_table`, `arcturus_dpm_table`, and `extern void arcturus_set_ppt_funcs(struct smu_context *smu)`.

## Control Flow

There is no code flow in the header. At runtime, platform dispatch calls `arcturus_set_ppt_funcs`, implemented in `arcturus_ppt.c`, to install Arcturus maps and hooks. The DPM structs describe per-clock DPM levels and min/max state used by platform logic.

## State and Persistence Behavior

The header defines shapes for state but stores none itself. Arcturus DPM state persists in the SMU context after allocation and population from firmware/PPTable data.

## Dependencies

It depends on `bool`, fixed-width integer types, and a visible declaration of `struct smu_context` from surrounding includes. The DPM maxima must align with firmware/table expectations.

## Integration Points

Compiled users include Arcturus platform setup and common SMU selector code. The constants are used to choose standard/peak UMD pstate levels and allocate bounded DPM arrays.

## Risks and Edge Cases

The local `MAX_PCIE_CONF` name overlaps with generation headers; include order must avoid conflicting definitions. Fixed DPM array sizes require bounds checks before indexing. UMD pstate indexes are meaningful only when the firmware reports enough levels.

## Test Signals

Build coverage, Arcturus function-table installation, DPM table population with level counts at or below `MAX_DPM_NUMBER`, and UMD pstate reporting are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/arcturus_ppt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/cyan_skillfish_ppt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/cyan_skillfish_ppt.c

## Purpose

`cyan_skillfish_ppt.c` is the Cyan Skillfish SMU11.8/APU-specific PPT implementation. It provides a small SMU message/table map, metrics table allocation, sensor and GPU metrics export, clock-level reporting, simple OverDrive SCLK/VDDC editing, DPM-running detection, and a function-table installer that marks the SMU as APU.

## Important APIs, Types, and Functions

Key constants are `CYAN_SKILLFISH_SCLK_MIN/MAX`, `CYAN_SKILLFISH_VDDC_MIN/MAX`, and `CYAN_SKILLFISH_VDDC_MAGIC`. Static state includes `cyan_skillfish_user_settings` and `cyan_skillfish_sclk_default`. Important functions are `cyan_skillfish_tables_init`, `cyan_skillfish_init_smc_tables`, `cyan_skillfish_get_smu_metrics_data`, `cyan_skillfish_read_sensor`, `cyan_skillfish_get_current_clk_freq`, `cyan_skillfish_emit_clk_levels`, `cyan_skillfish_is_dpm_running`, `cyan_skillfish_get_gpu_metrics`, `cyan_skillfish_od_edit_dpm_table`, `cyan_skillfish_get_dpm_ultimate_freq`, `cyan_skillfish_get_enabled_mask`, and `cyan_skillfish_set_ppt_funcs`.

## Control Flow

`cyan_skillfish_set_ppt_funcs` assigns the Cyan Skillfish function table, table map, APU flag, driver-interface version, and message control map. `init_smc_tables` allocates the SMU metrics table and driver GPU metrics cache, then delegates to common SMU11 table init. Sensor and metrics calls fetch `SmuMetrics_t` through `smu_cmn_get_metrics_table` and convert fields into AMDGPU sensor units or GPU metrics v2.2. OD editing stages values in static user settings, validates ranges, and commits by sending `RequestGfxclk` and either `ForceGfxVid` or `UnforceGfxVid`.

## State and Persistence Behavior

Driver state includes cached metrics, GPU metrics driver table, static user OD settings, default SCLK discovered from metrics, and `smu->is_apu = true`. Firmware state changes when requested GFX clock or forced VID messages are sent. The `get_enabled_mask` hook reports all feature bits as enabled rather than querying per-feature support.

## Dependencies

The file depends on AMDGPU core, `amdgpu_smu.h`, SMU11 common helpers, Cyan Skillfish PMFW/driver interface headers, `smu_v11_8_ppsmc.h`, `smu_v11_8_pmfw.h`, `smu_cmn`, and SOC15 common definitions. It assumes the SMU11.8 metrics layout with `Current` and `Average` nested members.

## Integration Points

Compiled through `smu11/Makefile`, it integrates with AMDGPU APU power management, hwmon sensors, GPU metrics, OverDrive sysfs for SCLK/VDDC, common SMU11 IRQ/memory-table handling, and DPM feature checks.

## Risks and Edge Cases

OD settings are file-static, so multi-device Cyan Skillfish systems would share staged settings. The default SCLK is lazily captured and reset during suspend by returning DPM-not-running. Voltage conversion to SVI2 VID must preserve PMFW units. `get_enabled_mask` filling all bits can hide unsupported-feature distinctions from generic callers. Sensor unit conversions differ from Arcturus and must match the SMU11.8 metrics layout.

## Test Signals

Build and boot on Cyan Skillfish, metrics table reads, hwmon sensors for clocks/power/temperature/voltage, GPU metrics v2.2 fields, OD range output, SCLK/VDDC commit/restore behavior, suspend/resume DPM reinit, and firmware response to `RequestGfxclk`/VID messages validate the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/cyan_skillfish_ppt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/cyan_skillfish_ppt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/cyan_skillfish_ppt.h

## Purpose

`cyan_skillfish_ppt.h` is the public header for the Cyan Skillfish SMU11.8 PPT implementation. It exports only the function-table installer used by platform dispatch.

## Important APIs, Types, and Functions

The sole API is `extern void cyan_skillfish_set_ppt_funcs(struct smu_context *smu);`. There are no local types, macros, state objects, or inline helpers.

## Control Flow

No control flow exists here. Runtime dispatch calls the exported function implemented in `cyan_skillfish_ppt.c`, which installs Cyan Skillfish-specific `pptable_funcs`, maps, the APU flag, and message control.

## State and Persistence Behavior

The header stores no state. The implementation mutates the supplied `smu_context` by assigning function tables and platform metadata.

## Dependencies

It depends on a visible `struct smu_context` declaration from including code and the include guard `__CYAN_SKILLFISH_PPT_H__`.

## Integration Points

The header connects common SMU platform selection code to `cyan_skillfish_ppt.c`, which is compiled by the SMU11 makefile. It is part of AMDGPU's Cyan Skillfish APU PM dispatch path.

## Risks and Edge Cases

The interface is intentionally narrow; adding new exported helpers would couple platform-specific internals to common code. Consumers must call the installer only for Cyan Skillfish-compatible devices.

## Test Signals

Build coverage and successful Cyan Skillfish probe with `smu->ppt_funcs` installed are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/cyan_skillfish_ppt.h -->
