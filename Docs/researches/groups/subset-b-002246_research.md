# subset-b-002246

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/df/df_1_7_default.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/df/df_1_7_default.h

## Purpose
`df_1_7_default.h` provides default reset-style values for the AMD Data Fabric 1.7 register block. In this subset it exports the default value for `mmFabricConfigAccessControl`, used by the DF v1.7 driver to leave broadcast/instance access control in its baseline state.

## Important APIs, Types, And Functions
The file defines only preprocessor constants. Its key export is `mmFabricConfigAccessControl_DEFAULT`, set to `0x00000000`. There are no C types, functions, inline helpers, or data structures.

## Control Flow
This header has no runtime control flow. It participates in control flow when `df_v1_7_enable_broadcast_mode()` disables broadcast mode by writing `mmFabricConfigAccessControl_DEFAULT` through `WREG32_SOC15(DF, 0, mmFabricConfigAccessControl, ...)`.

## State, Persistence, And Dependencies
The header stores no software state. The value it defines is written to a persistent hardware register until later driver or firmware writes change it. It depends only on include guards and is meaningful together with `df_1_7_offset.h`, which defines the register address, and `df_1_7_sh_mask.h`, which defines the bit fields used when broadcast mode is enabled.

## Integration Points
`drivers/gpu/drm/amd/amdgpu/df_v1_7.c` includes this header with the matching offset and mask headers. The DF function table exposes the behavior through `amdgpu_df_funcs.enable_broadcast_mode`, so callers that toggle DF broadcast mode rely on this default value to restore direct register access.

## Risks
The main risk is register-generation drift: if the default value stops matching the hardware generation, disabling broadcast mode could leave stale instance-access bits set or clear bits that should be preserved. Because the macro is untyped and globally named, accidental reuse with another DF generation would compile but target the wrong semantics.

## Test Signals
Useful signals include build coverage for `df_v1_7.c`, register traces showing `mmFabricConfigAccessControl` returning to zero after broadcast-mode exit, and suspend/resume or clock-gating tests that repeatedly enter and leave DF broadcast mode without later register access failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/df/df_1_7_default.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/df/df_1_7_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/df/df_1_7_offset.h

## Purpose
`df_1_7_offset.h` maps AMD Data Fabric 1.7 register names to SOC15 MMIO offsets and base-index selectors. It gives the v1.7 DF driver stable symbolic names for fabric access control, medium-grain clock gating, DRAM base decoding, and coherent slave mode control.

## Important APIs, Types, And Functions
The public surface is a set of macros: `mmFabricConfigAccessControl`, `mmDF_PIE_AON0_DfGlobalClkGater`, `mmDF_CS_AON0_DramBaseAddress0`, and `mmDF_CS_AON0_CoherentSlaveModeCtrlA0`, each paired with a `_BASE_IDX` macro. There are no functions or types.

## Control Flow
The header has no direct control flow. It supplies the register identifiers used by `RREG32_SOC15`, `WREG32_SOC15`, and `WREG32_FIELD15` in `df_v1_7.c`: broadcast-mode toggling reads/writes `FabricConfigAccessControl`, clock-gating updates read/modify/write `DfGlobalClkGater`, channel discovery reads `DramBaseAddress0`, and ECC RMW forcing writes a field in `CoherentSlaveModeCtrlA0`.

## State, Persistence, And Dependencies
The macros are compile-time constants. Hardware state lives in the registers they address and persists until changed by the driver, firmware, reset, or power transitions. These offsets depend on the SOC15 DF register accessor convention and on the matching shift/mask header for field extraction and modification.

## Integration Points
`df_v1_7.c` is the direct consumer. The exported `amdgpu_df_funcs` methods use these addresses for DF broadcast mode, HBM channel discovery, DF medium-grain clock gating, clock-gating state reporting, and ECC force-parallel-write read-modify-write behavior.

## Risks
Incorrect offsets or base indices can redirect writes to unrelated DF registers, with high impact because these paths affect global fabric access, memory interleaving interpretation, clock gating, and ECC behavior. Generated headers also expose no type safety, so cross-generation macro mixups may compile.

## Test Signals
Signals include successful compilation of `df_v1_7.c`, correct HBM channel counts from known `DramBaseAddress0` encodings, clock-gating enable/disable register traces, and ECC feature tests that verify `ForceParWrRMW` changes only the intended bit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/df/df_1_7_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/df/df_1_7_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/df/df_1_7_sh_mask.h

## Purpose
`df_1_7_sh_mask.h` defines bit shifts and masks for selected AMD Data Fabric 1.7 registers. It lets register-helper macros extract or update fields without hard-coded bit arithmetic in the DF v1.7 implementation.

## Important APIs, Types, And Functions
The file exports field macros for `FabricConfigAccessControl`, `DF_PIE_AON0_DfGlobalClkGater`, `DF_CS_AON0_DramBaseAddress0`, and `DF_CS_AON0_CoherentSlaveModeCtrlA0`. Important fields include `CfgRegInstAccEn`, `CfgRegInstAccRegLock`, `CfgRegInstID`, `MGCGMode`, `AddrRngVal`, `LgcyMmioHoleEn`, `IntLvNumChan`, `IntLvAddrSel`, `DramBaseAddr`, and `ForceParWrRMW`.

## Control Flow
There is no executable flow in the header. Consumers use the masks inside read/modify/write flows: `df_v1_7_enable_broadcast_mode()` clears `CfgRegInstAccEn`, `df_v1_7_get_fb_channel_number()` masks and shifts `IntLvNumChan`, `df_v1_7_update_medium_grain_clock_gating()` replaces `MGCGMode`, and `df_v1_7_enable_ecc_force_par_wr_rmw()` updates `ForceParWrRMW` through `WREG32_FIELD15`.

## State, Persistence, And Dependencies
The macros do not store state. They describe persistent hardware fields in DF configuration registers. They depend on AMD's register-helper naming convention where `REG_GET_FIELD` and `WREG32_FIELD15` construct macro names from register and field identifiers.

## Integration Points
The direct integration is `drivers/gpu/drm/amd/amdgpu/df_v1_7.c`. Higher-level integration is through `amdgpu_df_funcs`, especially clock-gating, channel-number, broadcast-mode, and ECC setup hooks.

## Risks
Bitfield mistakes can silently produce wrong register programming. A bad `IntLvNumChan` mask changes memory-channel reporting; a bad `MGCGMode` mask can break clock-gating policy; a bad `CfgRegInstAccEn` mask can leave the fabric in broadcast mode or prevent broadcast writes. The `L` suffix also relies on callers treating masks as 32-bit register values.

## Test Signals
Useful checks include static comparison against hardware register specifications, unit-style tests of `REG_GET_FIELD` expansions for representative values, runtime register traces for clock-gating toggles, HBM channel-count validation on supported ASICs, and ECC RMW enablement checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/df/df_1_7_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/df/df_3_6_default.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/df/df_3_6_default.h

## Purpose
`df_3_6_default.h` provides the default value for an AMD Data Fabric 3.6 access-control register. In this subset, that value is used to restore `mmFabricConfigAccessControl` after broadcast-mode access.

## Important APIs, Types, And Functions
The only exported macro is `mmFabricConfigAccessControl_DEFAULT`, with value `0x00000000`. The header contains no functions, types, variables, or inline logic.

## Control Flow
The header has no direct control flow. `df_v3_6_enable_broadcast_mode()` uses the macro in its disable path, writing the default back to `mmFabricConfigAccessControl` after the enable path has cleared `CfgRegInstAccEn`.

## State, Persistence, And Dependencies
Software state is not stored here. The defined value becomes persistent hardware state when written to the DF register. It is coupled with `df_3_6_offset.h` for the register address and `df_3_6_sh_mask.h` for the field layout.

## Integration Points
The direct consumer is `drivers/gpu/drm/amd/amdgpu/df_v3_6.c`, where broadcast-mode behavior is part of the `amdgpu_df_funcs` table. That same DF implementation also handles perfmon setup, hash querying, clock gating, channel discovery, and RAS poison-mode queries, so restoring fabric access control is part of broader DF lifecycle management.

## Risks
If the reset/default value differs on a specific DF 3.6 ASIC variant, the driver may restore the wrong fabric access mode. The macro name matches the v1.7 default name, so using multiple generation headers in one translation unit would be unsafe.

## Test Signals
Signals include build coverage for `df_v3_6.c`, register traces confirming `mmFabricConfigAccessControl` returns to zero after broadcast-mode exit, and stress tests around DF clock-gating and perfmon operations that require reliable direct DF register access after broadcast writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/df/df_3_6_default.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/df/df_3_6_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/df/df_3_6_offset.h

## Purpose
`df_3_6_offset.h` maps AMD Data Fabric 3.6 register names to MMIO or SMN addresses. It supports DF access-control, clock-gating, memory-interleave discovery, DF performance counters, indirect fabric configuration access, DRAM range reads, and RAS hardware-assert mask reads.

## Important APIs, Types, And Functions
The macro surface includes `mmFabricConfigAccessControl`, `mmDF_PIE_AON0_DfGlobalClkGater`, `mmDF_CS_UMC_AON0_DfGlobalCtrl`, `mmDF_CS_UMC_AON0_DramBaseAddress0`, `mmDF_GCM_AON0_DramMegaBaseAddress0`, and hardware assert mask registers. It also exports SMN addresses for `smnPerfMonCtlLo0` through `smnPerfMonCtlHi7`, `smnPerfMonCtrLo0` through `smnPerfMonCtrHi7`, fabric indirect config access address/data registers, and SMN DRAM base/limit registers.

## Control Flow
The header itself is declarative. In `df_v3_6.c`, its macros drive several flows: initialization queries hash/interleave state, broadcast mode reads and writes `mmFabricConfigAccessControl`, channel discovery reads either `mmDF_GCM_AON0_DramMegaBaseAddress0` for Aldebaran or `mmDF_CS_UMC_AON0_DramBaseAddress0` otherwise, perfmon code programs the SMN perfmon control and counter pairs, and RAS poison detection reads hardware assert mask low/high registers.

## State, Persistence, And Dependencies
The file has no software persistence. The addressed registers represent hardware state in DF, UMC-facing memory decode logic, performance monitors, and RAS controls. MMIO-style `mm*` constants depend on SOC15 accessors and `_BASE_IDX` values; `smn*` constants depend on SMN read/write helpers used elsewhere in the AMDGPU stack.

## Integration Points
`df_v3_6.c` includes this header directly. `amdgpu_xgmi.c` also includes it, so XGMI or multi-GPU fabric code can reuse the DF 3.6 address definitions. The macros integrate with `RREG32_SOC15`, `WREG32_SOC15`, SMN register helpers, `REG_GET_FIELD`, and the `amdgpu_df_funcs` operation table.

## Risks
Address drift is the primary risk: perfmon control/counter pairs, indirect access data registers, and RAS mask registers are sensitive to exact offsets. Mixing MMIO `mm*` and SMN `smn*` access paths is another risk because the same logical block appears through different address spaces. ASIC-specific differences, such as Aldebaran's alternate DRAM interleave mask, require consumers to choose the right macro set.

## Test Signals
Validation signals include successful DF perfmon allocation and counter reads, known-good HBM channel counts on both Aldebaran and non-Aldebaran devices, XGMI/fabric discovery tests, RAS poison-mode reporting from hardware assert masks, and register-access tracing that confirms SMN addresses are used only with SMN helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/df/df_3_6_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/df/df_3_6_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/df/df_3_6_sh_mask.h

## Purpose
`df_3_6_sh_mask.h` defines shifts and masks for AMD Data Fabric 3.6 registers used by AMDGPU. It describes access-control fields, DF clock-gating mode, global hash-interleave controls, DRAM base/limit fields, and low/high hardware assert mask bits used for RAS poison-mode detection.

## Important APIs, Types, And Functions
Important macro groups cover `FabricConfigAccessControl`, `DF_PIE_AON0_DfGlobalClkGater`, `DF_CS_UMC_AON0_DfGlobalCtrl`, `DF_CS_UMC_AON0_DramBaseAddress0`, `DF_CS_UMC_AON0_DramLimitAddress0`, `DF_CS_UMC_AON0_HardwareAssertMaskLow`, and `DF_NCS_PG0_HardwareAssertMaskHigh`. The file includes one ASIC-specific variant, `ALDEBARAN_DF_CS_UMC_AON0_DramBaseAddress0__IntLvNumChan_MASK`, for wider channel-interleave encoding.

## Control Flow
There is no executable flow in the header. In `df_v3_6.c`, these macros shape branch outcomes and register writes: broadcast mode clears `CfgRegInstAccEn`, hash-query logic interprets `GlbHashIntlvCtl64K`, `GlbHashIntlvCtl2M`, and `GlbHashIntlvCtl1G`, channel discovery masks `IntLvNumChan`, DRAM range logic can decode base/limit fields, and RAS poison mode checks `HWAssertMsk0`, `HWAssertMsk1`, `HWAssertMsk28`, and `HWAssertMsk31` for consistency.

## State, Persistence, And Dependencies
The macros are stateless descriptions of persistent hardware fields. They depend on AMD register helper conventions where field names are concatenated into macro names by `REG_GET_FIELD` and field-write helpers. The hardware state they describe affects memory interleaving, fabric hashing, clock gating, and RAS behavior.

## Integration Points
`drivers/gpu/drm/amd/amdgpu/df_v3_6.c` is the main integration point. The masks feed `amdgpu_df_funcs` implementations for initialization, clock-gating, channel reporting, perfmon operation, and `query_ras_poison_mode`. The offset header also reaches `amdgpu_xgmi.c`, so matching field definitions may be relevant to multi-GPU fabric configuration.

## Risks
Incorrect bit definitions can cause subtle platform behavior changes: hash status may be reported incorrectly, channel counts may be wrong, DF clock-gating could be misprogrammed, and poison-mode detection could issue false positives or miss inconsistent hardware assert settings. The 32 single-bit assert-mask definitions are repetitive, so generated off-by-one errors are plausible.

## Test Signals
Useful tests include field extraction against known register snapshots, RAS poison-mode tests for all-on, all-off, and inconsistent bit combinations, ASIC-specific channel-count validation for Aldebaran, clock-gating state checks, and static comparison of generated masks against the DF 3.6 register specification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/df/df_3_6_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/df/df_4_15_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/df/df_4_15_offset.h

## Purpose
`df_4_15_offset.h` provides the Data Fabric 4.15 register offset needed by the AMDGPU DF v4.15 implementation. In this subset it exposes `NCSConfigurationRegister1`, used to control local processing of internal atomics.

## Important APIs, Types, And Functions
The file exports `regNCSConfigurationRegister1` with offset `0x0901` and `regNCSConfigurationRegister1_BASE_IDX` with base index `4`. It contains no C functions or types.

## Control Flow
The header is declarative. `df_v4_15_hw_init()` reads `regNCSConfigurationRegister1` when `adev->have_atomics_support` is true, ORs in a shifted bit set, and writes the register back through `WREG32_SOC15`.

## State, Persistence, And Dependencies
No software state is stored. The addressed hardware register persists the selected NCS atomic-processing policy until reset or another writer updates it. The offset depends on SOC15 register access and must be paired with `df_4_15_sh_mask.h` for the `DisIntAtomicsLclProcessing` field location.

## Integration Points
`drivers/gpu/drm/amd/amdgpu/df_v4_15.c` includes this header and exposes the programming through `amdgpu_df_funcs.hw_init`. The behavior is tied to the device capability flag `have_atomics_support`, so it integrates with broader ASIC discovery and initialization.

## Risks
A wrong offset or base index could modify an unrelated DF register during hardware initialization. Since the consumer ORs bits into the register, stale or mis-shifted values may accumulate unless the target mask is correct. The `reg*` naming also differs from older `mm*` headers, so helper compatibility matters.

## Test Signals
Signals include successful build of `df_v4_15.c`, hardware-init traces showing a read and write to base index 4 offset `0x0901` only when atomics support is present, and atomics-capability tests that confirm local internal atomic processing is disabled for the intended lanes/bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/df/df_4_15_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/df/df_4_15_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/df/df_4_15_sh_mask.h

## Purpose
`df_4_15_sh_mask.h` defines the shift and mask for the DF 4.15 `NCSConfigurationRegister1` field that disables local processing of internal atomics. It is the field-layout companion to `df_4_15_offset.h`.

## Important APIs, Types, And Functions
The exported macros are `NCSConfigurationRegister1__DisIntAtomicsLclProcessing__SHIFT`, set to `0x3`, and `NCSConfigurationRegister1__DisIntAtomicsLclProcessing_MASK`, set to `0x0003FFF8L`. There are no runtime APIs.

## Control Flow
The header has no flow. `df_v4_15_hw_init()` builds `dis_lcl_proc` from bits 1, 2, and 13, shifts it by `DisIntAtomicsLclProcessing__SHIFT`, ORs it into `regNCSConfigurationRegister1`, and writes the result when `adev->have_atomics_support` is enabled.

## State, Persistence, And Dependencies
The macros do not store state. They define how software writes persistent hardware state controlling NCS internal atomic local-processing behavior. The consumer currently uses the shift macro directly and does not mask before ORing, so correctness of both the chosen bit set and the field layout is important.

## Integration Points
The direct integration is `drivers/gpu/drm/amd/amdgpu/df_v4_15.c` through the `hw_init` hook in `amdgpu_df_funcs`. The field affects devices with atomic support and therefore ties into GPU initialization rather than an optional debug path.

## Risks
The defined mask covers bits 3 through 17, but the current consumer only shifts and ORs selected bits. If the input bit set grows beyond the mask or the shift changes, the code could set unintended register bits. A missing clear step means firmware-provided values are preserved, which may be intended but makes validation dependent on reset state.

## Test Signals
Useful checks include static validation that `(dis_lcl_proc << SHIFT)` stays inside `MASK`, register readback after `df_v4_15_hw_init()`, boot tests with `have_atomics_support` both true and false, and workload tests that exercise internal atomics after initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/df/df_4_15_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/df/df_4_3_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/df/df_4_3_offset.h

## Purpose
`df_4_3_offset.h` provides Data Fabric 4.3 register offsets for RAS poison-mode discovery. It maps the low and high hardware assert mask registers used by the DF v4.3 driver.

## Important APIs, Types, And Functions
The file exports `regDF_CS_UMC_AON0_HardwareAssertMaskLow` at `0x0e3e`, `regDF_NCS_PG0_HardwareAssertMaskHigh` at `0x0e3f`, and matching `_BASE_IDX` macros set to `4`. It contains no executable code.

## Control Flow
The header is used by `df_v4_3_query_ras_poison_mode()`, which reads both registers with `RREG32_SOC15`, extracts four assert-mask bits using the companion shift/mask header, and returns true, false, or warns on inconsistent mixed settings.

## State, Persistence, And Dependencies
No software state is stored. The addressed registers are persistent DF hardware state that reflects RAS poison handling configuration. The offsets depend on SOC15 access with base index 4 and on `df_4_3_sh_mask.h` for bit definitions.

## Integration Points
`drivers/gpu/drm/amd/amdgpu/df_v4_3.c` includes this header and exposes poison-mode reporting through `amdgpu_df_funcs.query_ras_poison_mode`. The result can inform higher-level AMDGPU RAS handling and diagnostics.

## Risks
Wrong offsets or base indices would make poison-mode detection read unrelated registers, potentially causing false diagnostics or hiding inconsistent RAS settings. Because the logic treats mixed bit states as a warning and false result, any address error could downgrade valid poison mode.

## Test Signals
Signals include register readback tests for base index 4 offsets `0x0e3e` and `0x0e3f`, simulated or captured register values for all-on/all-off/mixed assert bits, and RAS diagnostic logs confirming the warning path only appears for genuinely inconsistent hardware state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/df/df_4_3_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/df/df_4_3_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/df/df_4_3_sh_mask.h

## Purpose
`df_4_3_sh_mask.h` defines one-bit shift and mask macros for the DF 4.3 hardware assert mask low/high registers. These fields let the driver determine whether RAS poison mode is consistently enabled or disabled.

## Important APIs, Types, And Functions
The file exports `HWAssertMsk0` through `HWAssertMsk31` shifts and masks for `DF_CS_UMC_AON0_HardwareAssertMaskLow`, plus the same field range for `DF_NCS_PG0_HardwareAssertMaskHigh`. Each field maps to a single bit in a 32-bit register.

## Control Flow
The header is declarative. `df_v4_3_query_ras_poison_mode()` uses `REG_GET_FIELD` to read `HWAssertMsk0` and `HWAssertMsk1` from the low register and `HWAssertMsk28` and `HWAssertMsk31` from the high register. If all four are set it returns true; if all are clear it returns false; otherwise it warns and returns false.

## State, Persistence, And Dependencies
The macros describe persistent hardware state but keep no software state. They depend on AMD register-helper expansion conventions and on `df_4_3_offset.h` for the actual register addresses.

## Integration Points
The direct consumer is `drivers/gpu/drm/amd/amdgpu/df_v4_3.c`, where the result is published through `amdgpu_df_funcs.query_ras_poison_mode`. The field naming is intentionally aligned with the DF 3.6 assert-mask macros, allowing similar RAS logic across generations.

## Risks
Generated bitfield repetition creates off-by-one risk. If `HWAssertMsk28` or `HWAssertMsk31` is wrong, the warning logic may report inconsistent poison settings even on healthy systems. If low-register bits 0 or 1 are wrong, poison mode may be inverted or always false.

## Test Signals
Useful tests include `REG_GET_FIELD` extraction checks for representative low/high values, RAS poison-mode tests covering all set, all clear, and mixed states, and cross-generation comparison against DF 3.6 masks for the same logical assert bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/df/df_4_3_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_2_0_0_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_2_0_0_offset.h

## Purpose
`dpcs_2_0_0_offset.h` is a generated DCN 2.0 DisplayPort/PHY Control Subsystem register offset map. It supplies MMIO offsets and base indices for six DPCSTX/RDPCSTX transmitter instances, per-link CR address/data aliases, shared DPCSRX receiver controls, and related debug, PLL, PHY, SRAM, fuse, DPALT, and power-control registers.

## Important APIs, Types, And Functions
The file exports preprocessor macros only. For each link instance 0 through 5 it defines `mmDPCSTXn_DPCSTX_*` TX clock/control/CBUS/interrupt/PLL/debug registers, `mmRDPCSTXn_RDPCSTX_*` control/clock/interrupt/PLL/memory/debug/PHY/fuse/DPALT registers, and `mmDPCSSYS_CRn_DPCSSYS_CR_ADDR/DATA` aliases. It also defines shared `mmDPCSRX_*` receiver and indexed-access registers. All listed registers use `_BASE_IDX 2`.

## Control Flow
The header has no runtime flow. It is consumed by DCN resource setup through `DPCS_DCN2_REG_LIST(id)` in `dcn20_resource.c`. That macro expands into per-link register tables for link encoders, letting link-encoder code program clocks, TX controls, PHY lanes, PLL update data, fuses, DP alternate-mode controls, and debug registers by struct field rather than hard-coded offsets.

## State, Persistence, And Dependencies
The macros are compile-time constants. Runtime state lives in display hardware registers and persists according to DCN power, reset, and link-training flows. The header depends on the display register-helper macros `SR`, `SRI`, and link-encoder mask/shift lists, and is normally paired with `dpcs_2_0_0_sh_mask.h` for bitfield definitions.

## Integration Points
`drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c` includes this file and builds `link_enc_regs[]` for six links via `DPCS_DCN2_REG_LIST(id)`. `dcn20_link_encoder.h` defines that list and names the DPCS/RDPCS fields link encoders need, including `RDPCSTX_PHY_CNTL*`, `RDPCS_TX_CR_ADDR/DATA`, `RDPCSTX_PHY_FUSE*`, `DPCSTX_TX_CLOCK_CNTL`, `DPCSTX_TX_CNTL`, `DPCSTX_DEBUG_CONFIG`, `RDPCSTX_DEBUG_CONFIG`, and DPALT registers.

## Risks
The table is large and repetitive, so instance-stride or copy/paste errors are the main risk. A wrong offset can affect link training, PHY programming, PLL updates, AUX/CBUS behavior, DP alternate mode, or debug access for a single connector. Alias registers such as `DPCSSYS_CRn` sharing RDPCS TX CR address/data offsets must remain intentional. Because every macro uses base index 2, a base-index generation error would break the whole DCN20 link-encoder register map.

## Test Signals
Useful signals include successful compilation of DCN20 resource and link-encoder code, link training across all six possible transmitter instances, hotplug and HPD tests, DP and HDMI modeset tests, DPALT/USB-C display tests where applicable, register dumps confirming per-instance strides, and comparison of offset tables against the generated ASIC register source.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_2_0_0_offset.h -->
