# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_1_3_sh_mask.h lines 4613-6087

## Scope And Purpose

This chunk is the final 1,475-line segment of AMD's generated `SMU_7_1_3` register shift/mask header. It contains C preprocessor constants only: each hardware field is exposed as a `<REGISTER>__<FIELD>_MASK` macro and, where applicable, a matching `<REGISTER>__<FIELD>__SHIFT` macro. It defines no functions, structs, enums, variables, branches, locks, allocations, or direct MMIO operations.

The path is under a `ceph-client` source mirror, but this file is AMDGPU hardware register metadata, not Ceph filesystem logic. Runtime behavior comes from AMDGPU and PowerPlay code that combines these masks/shifts with register addresses from `smu_7_1_3_d.h` and uses indirect SMC/register helpers to program or read SMU, power-management, ROM, and CAC state.

This chunk starts at `GENERAL_PWRMGT__STATIC_PM_EN_MASK`, so the first `GENERAL_PWRMGT__GLOBAL_PWRMGT_EN` definition is in the previous chunk. It ends at the file guard close after `PWR_SVI2_STATUS`.

## Important APIs, Types, And Macros

The exported API is the generated macro namespace:

- `<REGISTER>__<FIELD>_MASK`: raw bit mask for a hardware register field.
- `<REGISTER>__<FIELD>__SHIFT`: low-bit position used to pack/unpack that field.

Major register families in this chunk:

- Power-management controls: `GENERAL_PWRMGT`, `CNB_PWRMGT_CNTL`, `SCLK_PWRMGT_CNTL`, `TARGET_AND_CURRENT_PROFILE_INDEX`, `TARGET_AND_CURRENT_PROFILE_INDEX_1`, `CG_ACPI_CNTL`, `CG_ULV_PARAMETER`, and `SCLK_MIN_DIV`. These describe global/static PM enablement, thermal-protection disable/type, ACPI low-voltage behavior, voltage PM, GPU counter clock/off bits, DPM state indexes, current/target SCLK/MCLK/LCLK/VDDCI/MVDD/VDDC/PCIe indexes, ACPI SCLK divisor, ULV threshold, and minimum SCLK divider fields.
- Frequency-transition voting: `CG_FREQ_TRAN_VOTING_0` through `CG_FREQ_TRAN_VOTING_7`. Each register repeats vote-enable fields for blocks such as BIF, HDP, ROM, IH semaphore, PDMA, DRM, IDCT, ACP, SDMA, UVD, VCE, DC_AZ, SAM, AVP, GRBM instances 0-15, and RLC. These fields let the SMU aggregate client votes that permit or block frequency transitions.
- Clock/display low-power controls: `PLL_TEST_CNTL`, `CG_STATIC_SCREEN_PARAMETER`, `CG_DISPLAY_GAP_CNTL`, `CG_DISPLAY_GAP_CNTL2`, `SCLK_DEEP_SLEEP_CNTL`, `SCLK_DEEP_SLEEP_CNTL2`, `SCLK_DEEP_SLEEP_CNTL3`, `SCLK_DEEP_SLEEP_MISC_CNTL`, `LCLK_DEEP_SLEEP_CNTL`, and `LCLK_DEEP_SLEEP_CNTL2`. These encode PLL test counters, static-screen thresholds, VBI/display-gap timing, deep-sleep divisors, hysteresis, enable bits, and many busy/idle mask inputs that gate SCLK/LCLK deep sleep.
- AVFS, clock-stretch, and idle controls: `PWR_AVFS_SEL`, `PWR_AVFS_CNTL`, `PWR_AVFS0_CNTL_STATUS` through `PWR_AVFS27_CNTL_STATUS`, `PWR_CKS_ENABLE`, `PWR_CKS_CNTL`, `PWR_DISP_TIMER_CONTROL`, `PWR_DISP_TIMER_DEBUG`, `PWR_DISP_TIMER2_CONTROL`, `PWR_DISP_TIMER2_DEBUG`, `PWR_DISP_TIMER_CONTROL2`, `VDDGFX_IDLE_PARAMETER`, `VDDGFX_IDLE_CONTROL`, and `VDDGFX_IDLE_EXIT`. These describe adaptive voltage/frequency scaling selection/control/status, PSM scan/gate/reset/isolation bits, per-sensor data/alarms, clock-stretch bypass/PCC/temp compensation/sample/wait/LDO fields, display timer interrupt programming, and VDDGFX idle detection/exit.
- LCAC/CAC measurement and overrides: `LCAC_MC0` through `LCAC_MC7`, `LCAC_CPL`, `GC_CAC_CGTT_CLK_CTRL`, `SE_CAC_CGTT_CLK_CTRL`, `GC_CAC_LKG_AGGR_*`, `GC_CAC_WEIGHT_CU_0` through `GC_CAC_WEIGHT_CU_7`, `GC_CAC_ACC_CU0` through `GC_CAC_ACC_CU15`, and `GC_CAC_OVRD_CU`. These expose leakage/current/activity counter thresholds, block and signal selectors, override select/value registers, clock-gating delays/overrides, leakage aggregation halves, per-CU signal weights, per-CU accumulators, and CU override masks/values.
- ROM and SMC ROM access: `ROM_SMC_IND_INDEX`, `ROM_SMC_IND_DATA`, `ROM_CNTL`, `PAGE_MIRROR_CNTL`, `ROM_STATUS`, `CGTT_ROM_CLK_CTRL0`, `ROM_INDEX`, `ROM_DATA`, `ROM_START`, `ROM_SW_CNTL`, `ROM_SW_STATUS`, `ROM_SW_COMMAND`, and `ROM_SW_DATA_1` through `ROM_SW_DATA_64`. These describe indirect ROM access, SPI clock timing/gating, page-mirror address/enable/invalidate/usage, busy/done status, command/data sizes, command instruction/address packing, and a 64-word software data window.
- Power-gating and voltage status: `CURRENT_PG_STATUS__VCE_PG_STATUS_MASK`, `CURRENT_PG_STATUS__UVD_PG_STATUS_MASK`, and `PWR_SVI2_STATUS` plane VID fields.

## Control Flow And Runtime Behavior

There is no control flow in this header. Runtime use is indirect:

1. ASIC-specific AMDGPU/PowerPlay files include `smu_7_1_3_d.h` for register addresses and this file for field masks/shifts.
2. Field helpers such as `PHM_WRITE_INDIRECT_FIELD`, `PHM_READ_INDIRECT_FIELD`, `cgs_read_ind_register`, `cgs_write_ind_register`, `RREG32_SMC`, and `WREG32_SMC` use these constants to build masked reads/writes against SMC-indexed registers.
3. SMU manager and hardware manager code sequences the actual PM transitions, deep-sleep policy, AVFS/clock-stretch setup, ROM access, voltage reads, and UVD/VCE power-gating checks.

Concrete integration in this tree includes `amdgpu/uvd_v6_0.c`, `pm/powerplay/inc/smu7_common.h`, `pm/powerplay/smumgr/vegam_smumgr.c`, `polaris10_smumgr.c`, `fiji_smumgr.c`, `tonga_smumgr.c`, and BACO-related PowerPlay code. Wider SMU7 code uses the same field names for `GENERAL_PWRMGT`, `CG_FREQ_TRAN_VOTING_0 + i * 4`, `LCAC_MC0_CNTL`, `PWR_CKS_CNTL`, `PWR_SVI2_STATUS`, and `CURRENT_PG_STATUS`.

## State And Persistence Behavior

The macros hold no software state and persist nothing by themselves. They describe stateful hardware registers whose values remain in the SMU/power/ROM/CAC blocks until reprogrammed, reset, power-gated, or restored after suspend/resume.

State represented by this chunk includes PM enable bits, thermal protection controls, frequency-transition vote masks, DPM current/target indexes, deep-sleep divisors and busy masks, display-gap/static-screen timers, AVFS status across 28 monitor instances, clock-stretch and droop-detection settings, VDDGFX idle state, LCAC/CAC thresholds and accumulators, ROM command/data windows, UVD/VCE power-gating status, and SVI2 VID readback.

Access type is not encoded in the macro names. Some fields are persistent configuration bits, some are read-only status, some are hardware-owned counters/accumulators, some are handshake or interrupt acknowledge bits, and some may be self-clearing or sequencing-sensitive. Consumers must preserve reserved fields and follow the ASIC programming model when using these masks.

## Dependencies And Integration Points

This chunk must stay synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_1_3_d.h`, which supplies addresses such as `ixGENERAL_PWRMGT`, `ixCG_FREQ_TRAN_VOTING_0`, `ixSCLK_DEEP_SLEEP_CNTL`, `ixPWR_AVFS0_CNTL_STATUS`, `ixROM_SW_COMMAND`, `ixGC_CAC_ACC_CU15`, and `ixPWR_SVI2_STATUS`.

Primary functional integration is in AMDGPU PowerPlay/legacy-DPM/SMU managers. The power managers use these masks to enable global/static power management, toggle thermal protection, enable voltage management and spread spectrum, configure frequency-transition voting, set clock-stretch controls, program LCAC thresholds, query SVI2 voltage IDs, and inspect media-block power-gating status. UVD/VCE code reads `CURRENT_PG_STATUS` to decide whether media blocks are currently power gated.

The generated names are the compile-time contract. Missing or renamed macros usually fail to build, but incorrect numeric masks or shifts can compile cleanly and cause hardware misprogramming at runtime.

## Risks And Edge Cases

- The chunk starts in the middle of `GENERAL_PWRMGT`; the `GLOBAL_PWRMGT_EN` mask/shift is in the prior chunk. A final per-file report should merge chunk boundaries before describing that register as complete.
- Generated-header drift is high risk. Wrong masks for PM enable, thermal disable, voltage PM, or deep-sleep busy gates can produce unstable clocks, missed protection behavior, failed low-power entry, or resume-only failures.
- `CG_FREQ_TRAN_VOTING_0` through `_7` are repetitive. Off-by-one register or field mistakes can affect only one vote bank or one client block and may appear only under specific UVD/VCE/SDMA/display/RLC workloads.
- Deep-sleep masks combine many block busy/idle signals. Incorrect mask polarity or width can either block power savings or enter deep sleep while a block is still active.
- AVFS and clock-stretch fields interact with voltage/frequency safety margins. Bad `PWR_AVFS_CNTL`, `PWR_AVFS*_CNTL_STATUS`, or `PWR_CKS_*` constants can lead to wrong alarm interpretation, over-aggressive stretching, or disabled protection.
- ROM software-window fields require command/data sizing and busy/done sequencing. Incorrect `ROM_SW_CNTL`, `ROM_SW_COMMAND`, or `ROM_SW_DATA_*` masks can corrupt ROM transactions or read/write wrong addresses.
- Status fields such as `CURRENT_PG_STATUS`, `PWR_SVI2_STATUS`, `ROM_STATUS`, timer debug/status, AVFS alarms, and CAC accumulators may be read-only, latched, or hardware-updated. Treating them like ordinary writable fields would be unsafe.
- Reserved and spare fields appear throughout the chunk. Full-register writes risk changing undocumented behavior; consumers should use masked updates where the programming model permits writes.

## Test Signals

Useful validation for this generated chunk includes:

- Build AMDGPU with SMU7/PowerPlay support so direct include users and field-helper macro expansion catch missing symbols.
- Mechanically compare `smu_7_1_3_sh_mask.h` against the authoritative generated register database and the companion `smu_7_1_3_d.h` address header.
- Check that every field in this line range has the expected mask/shift pair, while accounting for boundary and status-only exceptions such as the final power-gating masks.
- Diff against nearby SMU7 headers (`smu_7_1_0`, `smu_7_1_1`, `smu_7_1_2`) where ASIC layout parity is expected, especially for deep-sleep, ROM, AVFS, CKS, CAC, and SVI2 fields.
- Runtime exercise should cover DPM enable/disable, thermal-protection toggling, spread-spectrum and voltage-management paths, UVD/VCE power-gating transitions, SVI2 VID reads, clock-stretch setup, AVFS alarm/status reads, LCAC threshold programming, ROM software transactions, suspend/resume, and low-power display/idle transitions.
- Watch for kernel logs, SMU timeouts, media-block wake failures, clock/voltage instability, failed ROM reads, unexpected power-gating status, and regressions that only appear under high media/display/SDMA/GFX activity.

## Cross-Chunk Notes

The previous chunk is needed for the beginning of `GENERAL_PWRMGT` and adjacent thermal monitor status fields. This chunk closes the file and therefore has no following SMU 7.1.3 shift/mask content, but final reconciliation should still merge all chunks for the file before making complete claims about the generated header namespace.
