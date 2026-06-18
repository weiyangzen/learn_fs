# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_0_1_d.h

## Purpose

`smu_7_0_1_d.h` is a generated ASIC register address header for AMD SMU 7.0.1 hardware, used by the CIK/Sea Islands AMDGPU driver paths. It exports preprocessor constants for memory-mapped and indirect SMU registers: direct `mm...` offsets such as `mmSMC_IND_INDEX_0`, `mmSMC_IND_DATA_0`, `mmSMC_MESSAGE_0`, and GPIO registers, plus indirect `ix...` addresses for clock, PLL, SMC SRAM, firmware tables, thermal, power-management, ROM, and status spaces.

The file is data-only. It has no functions, types, storage objects, or executable control flow. Its value is the address contract between AMDGPU C code and a particular hardware register layout. The companion `smu_7_0_1_sh_mask.h` supplies bit masks and field shifts for many of these address names.

## Exported API Surface

The exported API is a macro namespace guarded by `SMU_7_0_1_D_H`. The file contains 1,289 `#define` entries: 111 `mm...` register offsets and 1,177 `ix...` indirect addresses, plus the include guard.

Important macro families:

- SMC indirect access windows: `mmSMC_IND_INDEX`, `mmSMC_IND_DATA`, `mmSMC_IND_INDEX_0..7`, `mmSMC_IND_DATA_0..7`, and aliased `mmGCK_*`, `mmSMU_*`, `mmROM_*` variants. These are the index/data ports used to address the larger SMC register or SRAM spaces.
- SMC message mailbox registers: `mmSMC_MESSAGE_0..11`, `mmSMC_RESP_0..11`, and `mmSMC_MSG_ARG_0..11`. Power-management code writes command IDs and arguments here and waits for response fields.
- Clock and PLL registers: `ixCG_DCLK_*`, `ixCG_VCLK_*`, `ixCG_ECLK_*`, `ixCG_SPLL_*`, `ixSPLL_CNTL_MODE`, `ixMPLL_BYPASSCLK_SEL`, `ixCG_CLKPIN_*`, `ixTHM_CLK_CNTL`, and `ixMISC_CLK_CTRL`. These support UVD/VCE clock programming, PCIe clock-source setup, and BACO entry/exit sequences.
- SMC firmware/SRAM control: `ixSMC_SYSCON_*`, `ixSMC_PC_C`, `ixSMC_SCRATCH9`, `ixSMU_STATUS`, `ixSMU_FIRMWARE`, `ixSMU_INPUT_DATA`, and `ixFIRMWARE_FLAGS`.
- Table windows: `ixDPM_TABLE_1..510`, `ixMCARB_DRAM_TIMING_TABLE_1..144`, `ixMC_REGISTERS_TABLE_1..113`, `ixFAN_TABLE_1..9`, `ixSOFT_REGISTERS_TABLE_1..30`, `ixPM_FUSES_1..19`, and `ixSMU_PM_STATUS_0..127`. These expose SMC-managed dynamic power management, memory timing, fan, fuse, soft-register, and status-log memory regions.
- Thermal and fan control: `ixCG_THERMAL_*`, `ixCG_FDO_CTRL*`, `ixCG_TACH_*`, `ixTHM_TMON0_*`, and `ixCC_THM_STRAPS0`.
- Power management controls: `ixGENERAL_PWRMGT`, `ixCNB_PWRMGT_CNTL`, `ixSCLK_PWRMGT_CNTL`, deep-sleep controls, profile index registers, ULV parameters, and frequency-transition voting registers.
- ROM access: `ixROM_CNTL`, `ixROM_INDEX`, `ixROM_DATA`, `ixROM_START`, `ixROM_SW_*`, and `ixPAGE_MIRROR_CNTL`, used when reading VBIOS data via the SMC indirect path.
- GPIO and power-gating status: `mmGPIOPAD_*`, `ixCURRENT_PG_STATUS`, and related symbols used by BACO and UVD power-gating flows.

## Control Flow and Access Pattern

There is no local control flow in the header. Runtime behavior emerges in consumers that use these constants with AMDGPU register accessors:

- `amdgpu/cik.c` includes this header and defines `cik_smc_rreg()` and `cik_smc_wreg()`. Those wrappers take `adev->reg.smc.lock`, write `mmSMC_IND_INDEX_0`, then read or write `mmSMC_IND_DATA_0`. This is the core SMC indirect-register path behind `RREG32_SMC()` and `WREG32_SMC()` for CIK devices.
- `cik_read_disabled_bios()` reads and restores `ixROM_CNTL`, while `cik_read_bios_from_rom()` writes `ixROM_INDEX` and then streams `ixROM_DATA` through `mmSMC_IND_DATA_0`.
- `cik_set_uvd_clocks()` and `cik_set_vce_clocks()` program `ixCG_VCLK_CNTL`, `ixCG_DCLK_CNTL`, and `ixCG_ECLK_CNTL`, then poll corresponding status registers such as `ixCG_VCLK_STATUS`, `ixCG_DCLK_STATUS`, and `ixCG_ECLK_STATUS`.
- `cik_pcie_gen3_enable()` modifies clock-source registers such as `ixTHM_CLK_CNTL`, `ixMISC_CLK_CTRL`, `ixCG_CLKPIN_CNTL`, `ixCG_CLKPIN_CNTL_2`, and `ixMPLL_BYPASSCLK_SEL` while setting up PCIe behavior.
- `pm/powerplay/smumgr/ci_smumgr.c` uses `mmSMC_IND_INDEX_0`, `mmSMC_IND_DATA_0`, and `SMC_IND_ACCESS_CNTL` to upload firmware bytes into SMC RAM, read SMC SRAM dwords, and send commands through `mmSMC_MESSAGE_0`, `mmSMC_RESP_0`, and `mmSMC_MSG_ARG_0`.
- `pm/powerplay/hwmgr/ci_baco.c` builds BACO command tables that write `mmGCK_SMC_IND_INDEX` with `ixCG_SPLL_*`, `ixMPLL_BYPASSCLK_SEL`, `ixMISC_CLK_CTRL`, `ixTHM_CLK_CNTL`, and related addresses, then manipulate data through `mmGCK_SMC_IND_DATA`.
- `amdgpu/uvd_v4_2.c` checks `ixCURRENT_PG_STATUS` when manually coordinating UVD power-gating if DPM is disabled.
- `pm/powerplay/hwmgr/smu7_hwmgr.c` uses `ixSMU_PM_STATUS_95` as a sampled package-power status-log slot after sending SMC status-log messages.

The common runtime sequence is: select an indirect address in an `mm...IND_INDEX...` register, access the selected register or memory word through the paired `mm...IND_DATA...` register, and use masks from `smu_7_0_1_sh_mask.h` or accessor helpers to isolate fields.

## State and Persistence Behavior

The header stores no software state and has no persistence behavior. The constants identify hardware state that is persistent at device/register scope until reset, firmware action, power-gating, or explicit driver writes change it.

Stateful hardware touched through these constants includes:

- SMC SRAM and firmware image content written via `mmSMC_IND_INDEX_0`/`mmSMC_IND_DATA_0`.
- SMC mailbox state in message, response, and argument registers.
- Clock and PLL programming state for video, display, PCIe, thermal monitoring, and low-power modes.
- Power-management tables and status-log slots in the `0x3f000`-range SMC address space.
- ROM controller/index/data state during VBIOS reads.
- Thermal/fan and GPIO state used during power transitions.

Because indirect index/data ports are shared mutable hardware state, consumers must serialize accesses. The CIK core path does this with `adev->reg.smc.lock`; table-driven BACO and CGS/PowerPlay callers rely on their surrounding execution context and helper abstractions to avoid interleaving index/data operations.

## Dependencies

Direct dependencies are minimal: the header only depends on the C preprocessor and its own include guard. It is, however, semantically paired with:

- `smu_7_0_1_sh_mask.h` for bit masks and shift values matching many register names.
- AMDGPU register-access macros and callbacks such as `RREG32_SMC`, `WREG32_SMC`, `cgs_read_ind_register()`, `cgs_write_ind_register()`, `PHM_READ_FIELD()`, `PHM_WRITE_FIELD()`, and `REG_GET_FIELD()`.
- ASIC-specific driver code for CIK/SMU7-era chips, especially `cik.c`, `ci_smumgr.c`, `ci_baco.c`, `uvd_v4_2.c`, `vce_v2_0.c`, and DCE 8.0 GPIO translation code.
- Hardware documentation or AMD-generated register databases that define the numeric address layout. The file should be treated as generated register data rather than manually derived logic.

## Integration Points

This header is integrated into the AMDGPU stack wherever SMU 7.0.1 addresses are required:

- CIK ASIC setup and reset code uses it for SMC indirect access, ROM access, clock programming, PCIe clock-source programming, and SMC running-state detection.
- Legacy PowerPlay/SMU manager code uses it to load SMC firmware and communicate with the SMC firmware command processor.
- BACO support for CIK uses its GPIO, clock, PLL, and GCK/SMC index-data register definitions in table-driven power state transitions.
- UVD/VCE media blocks include it for clock and power-gating coordination.
- Display GPIO translation includes it alongside DCE 8.0 headers to recognize cross-block register offsets for the DCE80 generation.

The file is one member of a family of ASIC-specific SMU register headers (`smu_7_0_0_d.h`, `smu_7_1_0_d.h`, `smu_7_1_1_d.h`, etc.). Consumers must include the address header matching the target ASIC family; adjacent generations have similar symbol names with different numeric values.

## Risks and Edge Cases

- Address drift is the central risk. A single incorrect macro value can redirect a register write to an unrelated hardware register, causing firmware upload failure, clock misprogramming, failed power transitions, VBIOS read corruption, hangs, or device reset requirements.
- Shared indirect windows are order-sensitive. Any caller that writes `mmSMC_IND_INDEX_*` and is preempted or interleaved before the paired data access can read or write the wrong SMC location unless the access is locked or otherwise serialized.
- Similar aliases can hide mistakes. `mmSMC_*`, `mmGCK_*`, `mmSMU_*`, and `mmROM_*` index/data macros share offsets in this file, but call sites may assume a particular logical block. Refactoring between aliases should preserve the hardware access path and locking context.
- Generated table ranges are large and mostly untyped. `ixDPM_TABLE_1..510`, memory timing tables, and PM status slots encode array-like hardware regions without C array bounds. Callers must ensure any computed table index matches firmware expectations.
- The header intentionally lacks field masks. Using an address macro without the matching `_sh_mask.h` field definitions can lead to whole-register writes where read-modify-write behavior was required.
- Multi-generation code often shares symbol names. Accidentally including `smu_7_0_1_d.h` for a non-7.0.1 ASIC can compile successfully while programming the wrong register map.
- Hardware side effects are not visible from the header. Many addresses control clocks, thermal behavior, power gates, ROM windows, and firmware command processing; tests that only compile the header cannot validate safe runtime sequencing.

## Test Signals

Useful signals for this header are mostly integration-level:

- Build coverage for CIK/SMU7 AMDGPU configurations should compile all consumers without missing macro or field-mask references.
- Register-access smoke tests on supported CIK hardware should validate SMC indirect reads/writes, SMC firmware upload, mailbox command/response completion, and `cik_need_reset_on_init()` SMC-running detection.
- VBIOS read paths should exercise both `ixROM_CNTL` restore behavior and streaming reads via `ixROM_INDEX`/`ixROM_DATA`.
- UVD/VCE tests should verify clock programming via `ixCG_VCLK_*`, `ixCG_DCLK_*`, and `ixCG_ECLK_*` reaches ready status without timeouts.
- Power-management tests should cover DPM table access, PM status logging through `ixSMU_PM_STATUS_95`, and BACO entry/exit tables that touch GCK/SMC indirect registers.
- Static review should compare generated addresses against the authoritative register database and against neighboring SMU generation headers for intentional differences.
- Race-oriented review should inspect every index/data sequence using `mmSMC_IND_INDEX_*`, `mmGCK_SMC_IND_INDEX`, or aliases to confirm serialization around the paired data access.
