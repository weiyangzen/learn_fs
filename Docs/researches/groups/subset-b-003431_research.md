# Research: subset-b-003431

Grouped source research for subset B work item `subset-b-003431`. Each delimited section preserves the source path and can be split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_9_0_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_9_0_sh_mask.h

## Purpose
This generated AMDGPU register header describes bit shifts and masks for the THM 9.0 thermal-management register block. It contains no executable code; it is compile-time metadata used by AMD power-management and thermal code to read, write, and preserve fields in THM, CG thermal, fan, pump, BACO, SBRMI, and SMBus registers.

## Important APIs, Types, and Functions
The exported interface is a set of preprocessor macros named `<register>__<field>__SHIFT` and `<register>__<field>_MASK`. Important families include `THM_TCON_CUR_TMP` for current temperature and slew selection, `THM_TCON_HTC` for hardware thermal control and PROCHOT signaling, `THM_TCON_THERM_TRIP` for critical temperature fault and thermal trip state, repeated `THM_GPIO_*_CTRL` fields for PROCHOT, thermtrip, PWM, tach, pump, and MACO pins, `THM_THERMAL_INT_ENA`, `THM_THERMAL_INT_CTRL`, and `THM_THERMAL_INT_STATUS` for interrupt programming, many `THM_TMON*_*_DATA` fields for local and remote temperature monitors, `THM_DIE*_TEMP` and `CG_MULT_THERMAL_*` fields for die and aggregate thermal readings, `CG_FDO_*`, `CG_TACH_*`, `CG_PUMP_*`, and `CG_PUMP_TACH_*` fields for fan and pump control, `THM_TCON_LOCAL*` fields for local sensor policy, `THM_BACO_*` and `XTAL_CNTL` fields for low-power entry and timing, and `SBRMI_*` plus `SMBUS_*` fields for sideband management.

There are no C types or functions in this file. Consumers use these macros through helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, direct mask-and-shift expressions, and SOC15 register accessors.

## Control Flow
This header has no runtime control flow. It participates in control flow when included by PM code. For example, Vega thermal code reads `CG_MULT_THERMAL_STATUS__CTF_TEMP`, programs `THM_THERMAL_INT_CTRL` thresholds, clears bits through `THM_THERMAL_INT_ENA`, and masks or unmasks high/low thermal interrupts. SMU v11/v13 code also uses the thermal interrupt macros to configure interrupt handler credits, high/low temperature thresholds, trigger masks, and CTF shutdown paths. Older hwmgr code reads `THM_TCON_CUR_TMP` to convert sensor fields into temperatures.

## State and Persistence Behavior
The header itself stores no state. The macros describe fields in hardware registers whose values persist in GPU register state until reset, suspend/resume reprogramming, BACO/MACO transitions, firmware intervention, or driver writes. Fields here can affect persistent hardware behavior such as thermal interrupt enablement, fan and pump PWM mode, GPIO output enable, BACO isolation timing, and SMBus readiness.

## Dependencies and Integration Points
It depends only on the C preprocessor and include guards. It is paired with `thm_9_0_offset.h` and `thm_9_0_default.h` to provide register addresses and defaults. Integration points include `pm/powerplay/hwmgr/vega10_thermal.c`, `vega12_thermal.c`, `vega12_inc.h`, SMU thermal setup in `pm/swsmu/smu11/smu_v11_0.c`, related SMU v13 thermal code, and generic AMD register helpers. The header also aligns with SOC15 THM IP base tables such as `THM_BASE` in ASIC IP offset headers.

## Risks
The primary risk is hardware field drift. A wrong mask or shift can corrupt adjacent control bits, misreport temperature, suppress thermal interrupts, or program unsafe fan, pump, PROCHOT, or CTF behavior. Thermal fields are safety relevant: incorrect `DIG_THERM_INTH`, `DIG_THERM_INTL`, `TEMP_THRESHOLD`, or CTF masks can delay shutdown or create spurious shutdowns. Repeated GPIO and TMON macro families are easy to copy incorrectly. Another risk is width assumptions: most fields are 32-bit, and callers must not apply sign conversion or temperature unit conversion without checking the field semantics in the consuming driver.

## Test Signals
Compile-test AMDGPU configurations that include Vega, SMU11, and SMU13 thermal paths. Runtime signals include correct `hwmon` temperature readings, thermal interrupt registration, high/low threshold programming, fan and pump PWM behavior, BACO/MACO entry and exit stability, and CTF handling. Targeted tests should exercise `REG_SET_FIELD` and `REG_GET_FIELD` users for `THM_THERMAL_INT_CTRL`, `THM_THERMAL_INT_ENA`, `CG_MULT_THERMAL_STATUS`, and `THM_TCON_CUR_TMP`, and compare register dumps against vendor specifications on supported hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_9_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_12_0_0_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_12_0_0_offset.h

## Purpose
This generated AMDGPU register-offset header names the UMC 12.0.0 registers used by RAS code for on-die ECC counter control, ECC error counters, and MCA status/address reporting. It gives symbolic offsets and base-index selectors for the first UMC channel register view.

## Important APIs, Types, and Functions
The public interface is four offset macros plus matching `_BASE_IDX` macros: `regUMCCH0_OdEccCntSel`, `regUMCCH0_OdEccErrCnt`, `regMCA_UMC_UMC0_MCUMC_STATUST0`, and `regMCA_UMC_UMC0_MCUMC_ADDRT0`. There are no functions or types. Consumers pass these names to `SOC15_REG_OFFSET(UMC, 0, ...)`, then add a per-node, per-UMC, and per-channel offset before using PCIe extended 32-bit or 64-bit register accessors.

## Control Flow
The file has no internal control flow. In `amdgpu/umc_v12_0.c`, reset and initialization paths calculate `SOC15_REG_OFFSET` from these macros, then clear or initialize `OdEccErrCnt` and program `OdEccCntSel`. RAS query paths read `MCUMC_STATUST0` to classify correctable, uncorrectable, and deferred errors, then read `MCUMC_ADDRT0` when an address-bearing error must be translated into a system physical address.

## State and Persistence Behavior
This header stores no state. The registers it names are persistent GPU hardware state. `regUMCCH0_OdEccErrCnt` holds a correctable-error counter that driver code clears or initializes. `regMCA_UMC_UMC0_MCUMC_STATUST0` and `regMCA_UMC_UMC0_MCUMC_ADDRT0` hold machine-check status and address information until read and cleared by the RAS flow.

## Dependencies and Integration Points
It is included by `amdgpu/umc_v12_0.c` together with `umc_12_0_0_sh_mask.h`. It depends on SOC15 register offset infrastructure, UMC instance/channel topology in `adev->umc`, extended PCIe register accessors such as `RREG64_PCIE_EXT` and `WREG32_PCIE_EXT`, and AMDGPU RAS data structures. The base-index values tie these offsets to the correct register aperture in the generated ASIC register database.

## Risks
Incorrect offsets or base indices would send RAS code to the wrong hardware register, causing missed ECC events, clearing the wrong counter, or reading a bogus MCA address. Because UMC v12.0 has multi-node and cross-node address arithmetic in the caller, these base offsets must remain channel-local and compatible with `get_umc_v12_0_reg_offset()`.

## Test Signals
Build-test `amdgpu/umc_v12_0.c`. Runtime validation should check ECC counter initialization, MCA status reads, address collection, and status clearing on UMC 12.0 ASICs. Register dumps should show access to offsets `0x032c`, `0x032d`, `0x03c2`, and `0x03c4` plus the caller-computed UMC channel offset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_12_0_0_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_12_0_0_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_12_0_0_sh_mask.h

## Purpose
This generated header defines field shifts and masks for UMC 12.0.0 ECC counter and MCA registers. It lets AMDGPU RAS code select ECC counter behavior, extract counter overflow state, classify MCA status, and read error addresses without hard-coded bit arithmetic in C files.

## Important APIs, Types, and Functions
The interface is macro-only. `UMCCH0_OdEccCntSel__OdEccCntSel` selects the ECC counter source and `UMCCH0_OdEccCntSel__OdEccErrInt` selects the error interrupt type. `UMCCH0_OdEccErrCnt__Cnt`, `CntOvr`, and `OvrClr` describe the counter value, overflow flag, and overflow clear bit. `MCA_UMC_UMC0_MCUMC_STATUST0` exposes 64-bit MCA fields including `ErrorCode`, `ErrorCodeExt`, `AddrLsb`, `ErrCoreId`, `Scrub`, `Poison`, `Deferred`, `UECC`, `CECC`, `Transparent`, `SyndV`, `TCC`, `ErrCoreIdVal`, `PCC`, `AddrV`, `MiscV`, `En`, `UC`, `Overflow`, and `Val`. `MCA_UMC_UMC0_MCUMC_ADDRT0` exposes a 56-bit `ErrorAddr` and high reserved bits.

## Control Flow
The header has no control flow. `amdgpu/umc_v12_0.c` uses the masks in classification helpers. `umc_v12_0_is_deferred_error()` checks `Val`, `Poison`, and `Deferred`; `umc_v12_0_is_uncorrectable_error()` checks `PCC`, `UC`, and `TCC`; `umc_v12_0_is_correctable_error()` checks `CECC`, selected `UECC` cases, and replay-mode `ErrorCodeExt` values. Address query code extracts `MCUMC_ADDRT0.ErrorAddr` before platform-specific address translation.

## State and Persistence Behavior
No state is stored by the header. The bitfields describe hardware state that persists until firmware or the driver clears it. The MCA `Val`, `Overflow`, and error-type bits act as latches for RAS handling. `OdEccErrCnt` accumulates correctable-event count state and can signal overflow.

## Dependencies and Integration Points
It pairs with `umc_12_0_0_offset.h` and is consumed by `amdgpu/umc_v12_0.c`, AMDGPU RAS helpers, SMUIO topology helpers, and register helper macros `REG_GET_FIELD` and `REG_SET_FIELD`. The field naming must match those helper conventions exactly.

## Risks
These fields drive RAS severity decisions. A wrong status mask can misclassify deferred poison as uncorrectable, treat uncorrectable memory faults as correctable, or skip address translation. The address mask intentionally covers only low 56 bits; consumers must not infer the high reserved bits as address bits. Counter overflow handling depends on the `CntOvr` and `OvrClr` positions matching hardware.

## Test Signals
Unit-style compile coverage comes from building UMC v12.0 RAS code. Hardware or emulation tests should inject correctable, uncorrectable, deferred, poison, replay-mode parity, and overflow cases, then confirm `ce_count`, `ue_count`, `de_count`, error-address records, and register clearing match expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_12_0_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_6_0_default.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_6_0_default.h

## Purpose
This generated header records reset/default values for a small UMC 6.0 register subset: ECC control, UMC configuration, and local capability. It is reference metadata for code or diagnostics comparing runtime UMC state with expected defaults.

## Important APIs, Types, and Functions
The exported macros are `mmUMCCH0_0_EccCtrl_DEFAULT` set to `0x00000000`, `mmUMCCH0_0_UMC_CONFIG_DEFAULT` set to `0x00000203`, and `mmUMCCH0_0_UmcLocalCap_DEFAULT` set to `0x00000000`. There are no functions or types.

## Control Flow
There is no control flow. The defaults are passive constants. In this source snapshot, direct references to these exact default macros are not present in nearby AMDGPU code, but the companion UMC 6.0 mask header is included by `gmc_v9_0.c`, and generated default headers are commonly used for register bring-up, reset comparison, or debug table generation.

## State and Persistence Behavior
The header stores no state. It documents reset-like expected values for hardware state. Runtime UMC registers can diverge from these defaults after firmware memory training, ECC enablement, memory initialization, or driver RAS setup.

## Dependencies and Integration Points
It pairs with `umc_6_0_offset.h` and `umc_6_0_sh_mask.h`. Any consumer comparing register values would also need SOC15 address mapping and register read helpers. The constants map only channel 0 names; per-channel equivalence is inferred through companion offset patterns rather than repeated default macros.

## Risks
Treating defaults as runtime invariants is risky because firmware and driver initialization legitimately change UMC state. `UMC_CONFIG_DEFAULT` includes nonzero bits, so code that assumes zeroed UMC configuration would be wrong. Defaults should not be used to overwrite live registers unless the hardware reset sequence explicitly requires it.

## Test Signals
Compile tests are enough for macro syntax. Runtime validation would compare early boot register dumps against these defaults only at a known reset point, then verify later ECC and DRAM-ready state through the companion mask macros after firmware and driver initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_6_0_default.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_6_0_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_6_0_offset.h

## Purpose
This generated header defines UMC 6.0 register offsets for four memory channels. The covered registers are ECC control, UMC configuration, and local capability. It lets callers build per-channel register addresses without hard-coding the channel stride.

## Important APIs, Types, and Functions
The public macros are `mmUMCCH0_0_EccCtrl` through `mmUMCCH3_0_EccCtrl`, `mmUMCCH0_0_UMC_CONFIG` through `mmUMCCH3_0_UMC_CONFIG`, and `mmUMCCH0_0_UmcLocalCap` through `mmUMCCH3_0_UmcLocalCap`, each with `_BASE_IDX 0`. Channel spacing is visible in the offsets: ECC control at `0x0053`, `0x0853`, `0x1053`, and `0x1853`; UMC config at `0x0040`, `0x0840`, `0x1040`, and `0x1840`; local capability at `0x0306`, `0x0b06`, `0x1306`, and `0x1b06`.

## Control Flow
There is no code flow in the header. Consumers include the file or related generated headers and use these symbols with SOC15 register address helpers. The pattern supports loops over channels by selecting the channel-specific macro or by using an equivalent stride in calling code.

## State and Persistence Behavior
The header has no state. It names hardware state for ECC enablement, DRAM-ready status, and ECC capability/disablement. Those states persist in UMC registers and are changed by firmware, memory initialization, RAS setup, and potentially GPU reset paths.

## Dependencies and Integration Points
It pairs with `umc_6_0_sh_mask.h` for field extraction and with `umc_6_0_default.h` for reset values. Nearby AMDGPU code includes `umc_6_0_sh_mask.h` in `gmc_v9_0.c`, and later generated UMC 6.x headers extend the same register concepts for RAS flows. Consumers depend on SOC15 register offset macros and MMIO accessors.

## Risks
Offsets are hardware-contract data. A wrong channel offset can read the wrong channel's ECC state or write to the wrong UMC register. Because this header enumerates only four channels and later UMC variants use different channel topology, code must not reuse these macros for incompatible ASICs.

## Test Signals
Build coverage should include ASIC paths that include UMC 6.0 register headers. Runtime signals include correct channel-by-channel ECC enable state, DRAM-ready reads, and local capability reads on matching hardware. Register dumps can verify the four-channel offset stride.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_6_0_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_6_0_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_6_0_sh_mask.h

## Purpose
This generated header defines field masks and shifts for a minimal UMC 6.0 register set: ECC read/write enable, DRAM-ready status, and ECC disabled capability. It allows callers to interpret or set these hardware bits using AMD register helper macros.

## Important APIs, Types, and Functions
The interface is macro-only. `UMCCH0_0_EccCtrl__RdEccEn` and `UMCCH0_0_EccCtrl__WrEccEn` describe ECC enablement bits. `UMCCH0_0_UMC_CONFIG__DramReady` describes the high status bit indicating DRAM readiness. `UMCCH0_0_UmcLocalCap__EccDis` describes whether ECC is disabled or unavailable in the local capability register. There are no functions or types.

## Control Flow
The header has no control flow. It is included by `amdgpu/gmc_v9_0.c`, where UMC state contributes to graphics memory controller initialization and capability decisions. Callers typically read a register, apply `REG_GET_FIELD` or a mask/shift expression, and branch on ECC availability, ECC enablement, or DRAM readiness.

## State and Persistence Behavior
No state is stored by the header. The fields describe hardware state. `RdEccEn` and `WrEccEn` may be programmed by firmware or driver setup. `DramReady` is a hardware status bit reflecting memory initialization. `EccDis` is capability state and should generally be treated as read-only unless hardware documentation says otherwise.

## Dependencies and Integration Points
It pairs with `umc_6_0_offset.h` for register addresses and `umc_6_0_default.h` for default values. It integrates with AMDGPU GMC and RAS decisions through register helper conventions. The macros use the channel-0 register prefix even when equivalent fields apply to other channels through companion offsets.

## Risks
Using channel-0 field names against other channel offsets is conventional in generated AMD headers, but it requires the field layouts to be identical. Incorrect ECC enable interpretation can lead to false RAS capability reporting. Treating `DramReady` as writable, or clearing enable bits while memory is active, would be hazardous.

## Test Signals
Compile-test `gmc_v9_0.c` and related AMDGPU configurations. Runtime checks should compare reported ECC capability with VBIOS/firmware tables, confirm DRAM-ready before memory-dependent operations, and verify ECC enable bits on hardware with and without ECC support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_6_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_6_1_1_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_6_1_1_offset.h

## Purpose
This generated header defines the UMC 6.1.1 register offsets needed by AMDGPU RAS handling for ECC error counter selection, ECC count reads, and MCA status/address collection on non-Arcturus UMC 6.1 ASICs.

## Important APIs, Types, and Functions
The public offsets are `mmUMCCH0_0_EccErrCntSel`, `mmUMCCH0_0_EccErrCnt`, `mmMCA_UMC_UMC0_MCUMC_STATUST0`, and `mmMCA_UMC_UMC0_MCUMC_ADDRT0`, all with `_BASE_IDX 0`. There are no functions or types.

## Control Flow
There is no internal flow. In `amdgpu/umc_v6_1.c`, code chooses these offsets when `adev->asic_type != CHIP_ARCTURUS`. It then adds per-UMC and per-channel offsets from `get_umc_6_reg_offset()`. Counter initialization selects lower and upper chips, configures APIC-based ECC interrupt behavior, and writes an initial counter value. Query flow reads counts and MCA status. Address flow reads `MCUMC_ADDRT0` when an uncorrectable ECC error is valid.

## State and Persistence Behavior
The header has no state. The named registers hold persistent hardware state: ECC counter selection, ECC counter values, MCA status latches, and MCA error address latches. The RAS code temporarily disables UMC index mode around accesses and clears status after recording an address.

## Dependencies and Integration Points
It pairs with `umc_6_1_1_sh_mask.h` and is included by `amdgpu/umc_v6_1.c`. Integration depends on RSMU index-mode control, `SOC15_REG_OFFSET`, `RREG32_PCIE`, `RREG64_PCIE`, `WREG32_PCIE`, `WREG64_PCIE`, `adev->umc.channel_offs`, and `amdgpu_umc_fill_error_record()`.

## Risks
The file is part of an ASIC split: Arcturus uses the `umc_6_1_2_offset.h` `_ARCT` variant instead. Choosing the wrong offset family or base index can silently read the wrong register aperture. Counter and MCA status registers are used across many UMC instances and channels, so offset errors scale across the whole memory topology.

## Test Signals
Build `amdgpu/umc_v6_1.c`. Runtime validation should cover non-Arcturus UMC 6.1 hardware, checking counter initialization, lower/higher chip selection, CE/UE counting, MCA status clearing, and translated retired-page addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_6_1_1_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_6_1_1_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_6_1_1_sh_mask.h

## Purpose
This generated header defines shifts and masks for UMC 6.1.1 ECC counter and MCA status/address fields. It provides the field names used by `amdgpu/umc_v6_1.c` to configure ECC counting, accumulate correctable and uncorrectable error counts, and decode error addresses.

## Important APIs, Types, and Functions
`UMCCH0_0_EccErrCntSel__EccErrCntCsSel` selects lower or upper chip counter source, `EccErrInt` selects the interrupt type, and `EccErrCntEn` enables counting. `UMCCH0_0_EccErrCnt__EccErrCnt` exposes the 16-bit count. `MCA_UMC_UMC0_MCUMC_STATUST0` exposes MCA fields such as `ErrorCode`, `ErrorCodeExt`, `ErrCoreId`, `Scrub`, `Poison`, `Deferred`, `UECC`, `CECC`, `Transparent`, `SyndV`, `TCC`, `ErrCoreIdVal`, `PCC`, `AddrV`, `MiscV`, `En`, `UC`, `Overflow`, and `Val`. `MCA_UMC_UMC0_MCUMC_ADDRT0` exposes `ErrorAddr`, `LSB`, and reserved bits.

## Control Flow
The header has no runtime branches, but its fields drive `umc_v6_1.c`. Counter clear and initialization paths write `EccErrCntCsSel` for lower and higher chips and set `EccErrInt`. Correctable-error queries read `EccErrCnt`, subtract the initial count, and add one extra SRAM CE when `ErrorCodeExt == 6`, `Val == 1`, and `CECC == 1`. Uncorrectable-error queries check `Val` and any of `Deferred`, `UECC`, `PCC`, `UC`, or `TCC`. Address query checks `Val` and `UECC`, extracts `LSB` and `ErrorAddr`, masks low address bits, then builds a retired page address from channel and offset fields.

## State and Persistence Behavior
No software state lives here. Hardware counter and MCA status bits persist until the RAS path clears or reinitializes them. `EccErrCntCsSel` is a selector state, so reads of `EccErrCnt` depend on the last selected chip. MCA status is cleared by writing zero after address processing.

## Dependencies and Integration Points
It pairs with `umc_6_1_1_offset.h`. It is also used for field extraction in the Arcturus path because `umc_v6_1.c` includes `umc_6_1_2_offset.h` but not the `_ARCT` sh/mask header, relying on equivalent field layouts and non-ARCT field names for `REG_GET_FIELD` and `REG_SET_FIELD`.

## Risks
Correct RAS severity depends on these bit positions. Wrong `LSB` handling can retire the wrong page. Wrong `EccErrCntCsSel` fields can double count or miss one chip side. The shared use of 6.1.1 field names for 6.1.2-style offsets makes layout compatibility a critical assumption.

## Test Signals
Inject or simulate CE, UE, deferred, PCC, UC, and TCC conditions. Verify lower/higher chip counter accounting, SRAM CE detection, MCA status clearing, and error-address translation. Build tests should catch naming mismatches in `REG_GET_FIELD` and `REG_SET_FIELD`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_6_1_1_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_6_1_2_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_6_1_2_offset.h

## Purpose
This generated header defines Arcturus-specific UMC 6.1.2 register offsets for ECC counter selection, ECC count, MCA status, and MCA address registers. It mirrors the UMC 6.1.1 register set but uses `_ARCT` macro names and base index 1.

## Important APIs, Types, and Functions
The exported symbols are `mmUMCCH0_0_EccErrCntSel_ARCT`, `mmUMCCH0_0_EccErrCnt_ARCT`, `mmMCA_UMC_UMC0_MCUMC_STATUST0_ARCT`, and `mmMCA_UMC_UMC0_MCUMC_ADDRT0_ARCT`, each with `_BASE_IDX 1`. There are no functions or types.

## Control Flow
The header is selected in `amdgpu/umc_v6_1.c` when `adev->asic_type == CHIP_ARCTURUS`. The caller uses these offsets for counter clearing, counter initialization, CE/UE count queries, and UE address queries. Field manipulation still uses the UMC 6.1.1 field names because the C file includes only the 6.1.1 sh/mask header.

## State and Persistence Behavior
The header has no software state. It names Arcturus UMC registers whose values persist in hardware until driver, firmware, reset, or RAS clearing changes them. Arcturus paths also temporarily disallow DF C-state during RAS queries so register access and address collection remain stable.

## Dependencies and Integration Points
It integrates with `amdgpu/umc_v6_1.c`, Arcturus ASIC detection, RSMU UMC index-mode handling, DF C-state control via `amdgpu_dpm_set_df_cstate()`, SOC15 register offset infrastructure, and PCIe MMIO accessors. It pairs conceptually with `umc_6_1_2_sh_mask.h`, although the current C integration uses 6.1.1 field macro names.

## Risks
Base index 1 is the main difference from 6.1.1. A mismatch would target the wrong generated register base for Arcturus. Because field masks are assumed compatible with 6.1.1 names, any future 6.1.2 field layout change would require updating `umc_v6_1.c` includes and field names, not just this offset file.

## Test Signals
Run UMC RAS tests on Arcturus. Check that the Arcturus branch accesses `_ARCT` offsets, disables and restores DF C-state around queries, handles UMC index mode correctly, initializes both chip counters, and records valid UE addresses before clearing MCA status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_6_1_2_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_6_1_2_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_6_1_2_sh_mask.h

## Purpose
This generated header defines Arcturus-named UMC 6.1.2 field shifts and masks for ECC counter and MCA status/address registers. It is the `_ARCT` counterpart to the UMC 6.1.1 sh/mask file.

## Important APIs, Types, and Functions
The macro families mirror UMC 6.1.1 with `_ARCT` register prefixes. `UMCCH0_0_EccErrCntSel_ARCT` fields include `EccErrCntCsSel`, `EccErrInt`, and `EccErrCntEn`. `UMCCH0_0_EccErrCnt_ARCT__EccErrCnt` exposes the 16-bit ECC counter. `MCA_UMC_UMC0_MCUMC_STATUST0_ARCT` exposes MCA status fields including `ErrorCode`, `ErrorCodeExt`, `ErrCoreId`, `Scrub`, `Poison`, `Deferred`, `UECC`, `CECC`, `Transparent`, `SyndV`, `TCC`, `ErrCoreIdVal`, `PCC`, `AddrV`, `MiscV`, `En`, `UC`, `Overflow`, and `Val`. `MCA_UMC_UMC0_MCUMC_ADDRT0_ARCT` exposes `ErrorAddr`, `LSB`, and reserved bits.

## Control Flow
The header itself has no control flow. In this tree, `amdgpu/umc_v6_1.c` includes the Arcturus offset header but not this sh/mask header, so current code relies on 6.1.1 field macros against Arcturus offsets. This file documents the equivalent `_ARCT` names that would be used if the C path were switched to fully Arcturus-prefixed field extraction.

## State and Persistence Behavior
The file stores no software state. Its fields describe persistent hardware selector, counter, status, and address state. The semantics match the RAS path: select chip side, read or initialize counters, classify MCA status, extract low-significant-bit information, and clear status after processing.

## Dependencies and Integration Points
It pairs with `umc_6_1_2_offset.h`. It is generated to fit AMD register helper conventions but is currently an integration reserve or documentation-equivalent surface because the C file uses 6.1.1 sh/mask names. Any future consumer would use `REG_GET_FIELD` and `REG_SET_FIELD` with the `_ARCT` register prefixes.

## Risks
Dead or unused generated headers can drift from real call sites. If a developer includes this file and mixes `_ARCT` and non-`_ARCT` field names, macro lookup or field interpretation can break. The risk is especially high around `LSB` and RAS classification bits because address retirement and error severity depend on exact positions.

## Test Signals
Compile a path that includes this header with `_ARCT` field names to ensure macro naming is complete. On Arcturus hardware, compare field positions against the 6.1.1 macros currently used by `umc_v6_1.c`, then validate CE/UE/deferred injection, address extraction, and status clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_6_1_2_sh_mask.h -->
