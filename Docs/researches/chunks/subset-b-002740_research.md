# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_8_1_sh_mask.h lines 9960-14959

## Scope And Purpose

This chunk is the third line range of the generated-style GMC 8.1 register mask header. It contains preprocessor constants only: each hardware register field is represented as a `<REGISTER>__<FIELD>_MASK` and matching `<REGISTER>__<FIELD>__SHIFT` definition. There are no functions, structs, storage objects, or executable control-flow paths in this range.

The chunk describes bit layouts for memory-controller sequencer, PHY, memory PLL, power-management, training/debug, and indirect IO debug registers used by AMDGPU/PowerPlay code for CI/Tonga/Iceland-era ASICs. It spans about 600 register macro bases in these broad groups:

- low-power memory sequencer command/timing fields, including `MC_SEQ_PMG_CMD_{EMRS,MRS,MRS1,MRS2}_LP`, `MC_SEQ_PMG_TIMING_LP`, `MC_SEQ_PMG_DVS_{CTL,CMD}` and `_LP`, `MC_SEQ_G5PDX_*`, and `MC_SEQ_DLL_STBY`;
- training and diagnostic sequencer fields, including `MC_SEQ_TCG_CNTL`, `MC_SEQ_TSM_*`, `MC_TSM_DEBUG_*`, `MC_SEQ_IO_RWORD*`, `MC_SEQ_IO_RDBI`, `MC_SEQ_IO_REDC`, timers, and DRAM error insertion;
- PHY and clock controls, including `MC_PHY_TIMING_D0`, `MC_PHY_TIMING_D1`, `MC_PHY_TIMING_2`, `MC_SEQ_MPLL_OVERRIDE`, `MCLK_PWRMGT_CNTL`, `DLL_CNTL`, and the `MPLL_*` control/status families;
- PHY lane power-gating and broadcast controls, including `MC_SEQ_PMG_PG_HWCNTL`, `MC_SEQ_PMG_PG_SWCNTL_0`, `MC_SEQ_PMG_PG_SWCNTL_1`, and `MC_SEQ_PHYREG_BCAST`;
- the large indirect `MC_IO_DEBUG_*` namespace, including `MC_SEQ_IO_DEBUG_INDEX/DATA`, `MC_IO_DEBUG_UP_0` through `MC_IO_DEBUG_UP_159`, and per-lane/clock/command debug registers for DQB, DBI, EDC, WCK, CK, ADDR, ACMD, CMD, and WCDR paths.

The header's purpose is to let driver code form and decode 32-bit register values symbolically instead of open-coding bit literals beside MMIO or indirect-register accesses.

## Important APIs, Types, And Constants

There are no C APIs or types exported here. The usable interface is the macro namespace:

- `MC_SEQ_PMG_CMD_*_LP__ADR/MOP/BNK_MSB/END/CSB/ADR_MSB*`: low-power mode register command encodings. The matching `MC_SEQ_PMG_TIMING_LP` fields define self-refresh and CKE timing windows such as `TCKSRE`, `TCKSRX`, `TCKE_PULSE`, `SEQ_IDLE`, and `SEQ_IDLE_SS`.
- `MC_SEQ_IO_RWORD[0-7]`, `MC_SEQ_IO_RDBI`, and `MC_SEQ_IO_REDC`: full-width readback words, DBI mask, and EDC data from memory IO training/debug paths.
- `MC_SEQ_TCG_CNTL`: test command generator control bits for reset, channel enable, start/done, FIFO loading, command opcodes, data counts, burst count, auto-refresh injection, DBI control, frame training, and runtime read-data overrides.
- `MC_SEQ_TSM_CTRL` plus `MC_SEQ_TSM_{GCNT,OCNT,NCNT,BCNT,FLAG,UPDATE,EDC,DBI,WCDR,MISC}`: training state machine controls and comparison/update fields. These macros define start/capture/done/error/step behavior, channel selection, pointer fields, true/false actions, test masks, compare ranges, nibble skip/masks, capture/update tests, and WCDR offsets.
- `MC_SEQ_TIMER_{WR,RD}` and `MC_SEQ_DRAM_ERROR_INSERTION`: full-width timer counters plus TX/RX error-insertion masks for DRAM test paths.
- `MC_PHY_TIMING_D0`, `MC_PHY_TIMING_D1`, and `MC_PHY_TIMING_2`: RX/TX clock delay/extension fields per channel, inversion/force bits, clock-enable controls, write delay, and RX power-on force bits.
- `MC_SEQ_MPLL_OVERRIDE`, `MCLK_PWRMGT_CNTL`, `DLL_CNTL`, `MPLL_SEQ_UCODE_{1,2}`, `MPLL_CNTL_MODE`, `MPLL_FUNC_CNTL*`, `MPLL_AD/DQ_FUNC_CNTL`, `MPLL_TIME`, `MPLL_SS*`, `MPLL_CONTROL`, and `MPLL_*_STATUS`: memory PLL programming, reset, bypass, spread-spectrum, power-on, lock-time, divider, status, and sticky-unlock field layouts.
- `MC_SEQ_PMG_PG_HWCNTL` and `MC_SEQ_PMG_PG_SWCNTL_{0,1}`: memory PHY power-gating controls for hardware-managed gating and per-PMD/PMA software gating of DQ, DBI, EDC, WCLK, and AC TX/RX lanes.
- `MC_SEQ_IO_DEBUG_INDEX/DATA` and `MC_IO_DEBUG_*`: indirect IO debug index/data fields and decoded 4-byte `VALUE0`-`VALUE3` overlays for hundreds of internal debug registers. The named groups cover generic `UP_*` registers and lane/control families such as `DQB[0-3][LH]`, `DBI`, `EDC`, `WCK`, `CK`, `ADDRL`, `ADDRH`, `ACMD`, `CMD`, and `WCDR`.
- `MC_SEQ_CNTL_3`, `MC_SEQ_G5PDX_*`, `MC_SEQ_SREG_*`, `MC_SEQ_PHYREG_BCAST`, and `MC_SEQ_PMG_DVS_*`: late-chunk sequencer controls for pipe delay, repeat-clock gating, CDC programming, CAC/IDSC enable, GDDR5 power-down exit command/timing mirrors, sequencer register read/status, PHY broadcast masks, and dynamic-voltage-scaling command setup.

## Control Flow And State Behavior

This chunk has no local control flow. At compile time, including C files receive symbolic bit masks and shifts. Runtime behavior appears only in consumers that pair these masks with register address macros from `gmc_8_1_d.h`/related address headers.

The relevant runtime state lives in GPU hardware registers:

- Power-management and SMU code reads and writes `MCLK_PWRMGT_CNTL`, `DLL_CNTL`, and `MPLL_*` fields while programming memory clock transitions, DLL reset/power state, and BACO or low-power entry/exit flows.
- SMU manager code mirrors normal registers into low-power versions such as `MC_SEQ_G5PDX_CMD0_LP`, `MC_SEQ_G5PDX_CMD1_LP`, `MC_SEQ_G5PDX_CTRL_LP`, `MC_SEQ_PMG_DVS_CMD_LP`, and `MC_SEQ_PMG_DVS_CTL_LP`.
- Training/debug code can use `MC_SEQ_TCG_CNTL`, `MC_SEQ_TSM_*`, `MC_SEQ_IO_DEBUG_INDEX/DATA`, and `MC_TSM_DEBUG_*` as state-machine controls and indirect readback windows. The header does not provide locking, sequencing, polling, or timeout behavior for those operations.
- Full-width readback and status macros such as `MC_SEQ_IO_RWORD*`, `MC_SEQ_TIMER_RD`, `MC_SEQ_SREG_READ`, `MPLL_*_STATUS`, and `MC_IO_DEBUG_*__VALUE*` describe hardware-observed state. They do not cache or persist anything in system memory.

Persistence is therefore hardware-defined. Values can survive until GPU reset, power-gating, clock reprogramming, or firmware/SMU intervention, depending on the register block. The header itself has no restore path or ownership policy.

## Dependencies And Integration Points

This header is included as part of the AMDGPU GMC 8.1 ASIC register vocabulary. It depends on matching address headers for the `mm*` and `ix*` register offsets; the mask header alone cannot perform an MMIO access.

Important integration points visible from repository cross-references:

- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/ci_baco.c`, `tonga_baco.c`, and `polaris_baco.c` use `MPLL_CNTL_MODE__MPLL_SW_DIR_CONTROL_MASK`, `MPLL_CNTL_MODE__MPLL_MCLK_SEL_MASK`, `MPLL_CNTL_MODE__GLOBAL_MPLL_RESET_MASK`, and `MCLK_PWRMGT_CNTL__MRDCK*_PDNB_MASK` in command tables for BACO/low-power transitions.
- `drivers/gpu/drm/amd/pm/powerplay/smumgr/{ci,tonga,iceland}_smumgr.c` uses `MCLK_PWRMGT_CNTL` fields through register-field helper macros while programming DLL speed, MRDCK power/reset state, and memory-clock setup. The same SMU managers translate normal G5PDX/DVS registers to `_LP` register addresses and copy normal values into the low-power mirrors.
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_hwmgr.c` writes `mmMC_SEQ_IO_DEBUG_INDEX` and reads/writes `MCLK_PWRMGT_CNTL` as part of SMU7 hardware-manager setup and clock-register snapshots.
- `drivers/gpu/drm/amd/pm/legacy-dpm/si_dpm.c` also touches `MC_SEQ_IO_DEBUG_INDEX` and snapshots `MCLK_PWRMGT_CNTL` into SMC state-table structures, showing that these generated masks support both legacy DPM and PowerPlay paths.
- The indirect `MC_IO_DEBUG_*` and `MC_TSM_DEBUG_*` families are paired with `MC_SEQ_IO_DEBUG_INDEX/DATA` and `MC_SEQ_TSM_DEBUG_INDEX/DATA`; consumers must select an index/register address before reading or writing the data aperture.

## Risks And Edge Cases

- Hardware contract drift is the main risk. These constants must match the exact GMC 8.1 register specification. A wrong mask or shift can write reserved bits, miss a power gate, choose the wrong PLL divider, corrupt memory-clock transitions, or misdecode training/debug state.
- This chunk begins in the middle of `MC_SEQ_WR_CTL_2_LP`; line 9960 starts with a `__SHIFT` definition whose matching earlier mask is in the previous chunk. The merge lane should join adjacent chunks before making whole-register claims.
- Some fields intentionally use names such as `*_MASK_MASK`, for example `MC_SEQ_TCG_CNTL__VPTR_MASK_MASK`, `MC_SEQ_TSM_FLAG__NBBL_MASK_MASK`, and `MC_SEQ_PHYREG_BCAST__DQ_MASK_MASK`. These are generated field names where the hardware field itself is called `MASK`; cleanup scripts must not collapse the double `MASK`.
- Many registers expose full-width `0xffffffff` fields and high-bit masks such as `0x80000000`. Consumers should keep values unsigned/32-bit and avoid signed shifts or host-width assumptions.
- Indirect debug windows are order-sensitive. Interleaving writes to `MC_SEQ_IO_DEBUG_INDEX` or `MC_SEQ_TSM_DEBUG_INDEX` with unrelated data-window reads/writes can observe or update the wrong internal register unless the caller serializes access.
- The `MC_IO_DEBUG_*` region is highly repetitive: most entries decode four packed 8-bit values at shifts `0`, `8`, `16`, and `24`. Mechanical regeneration errors are easy to miss because names differ only by lane, channel suffix (`D0`/`D1`), or function (`CLKSEL`, `MISC`, `RXPHASE`, `TXPHASE`, `TXSLF`, `TXBST_*`, `RX_EQ`, `RX_VREF_CAL`, `RX_EQ_PM`, `RX_DYN_PM`, `CDR_PHSIZE`).
- Low-power mirror registers must stay layout-compatible with their normal counterparts. The `_LP` variants for G5PDX and DVS command/control use the same field shapes as the non-LP versions; a mismatch would break SMU code that copies normal register values into low-power mirrors.
- Several fields control destructive or timing-sensitive hardware behavior, including PLL resets, DLL resets, power gating, DRAM error insertion, TCG start/reset, and TSM start/step/capture. Incorrect writes can cause memory training failures, display hangs, or GPU resets.

## Test And Validation Signals

There are no direct unit tests for this macro chunk. Useful validation signals are integration-level:

- Compile coverage of AMDGPU PowerPlay, legacy DPM, and SMU manager files that include `gmc_8_1_sh_mask.h` and use the affected macro names.
- Static mask/shift validation: single-bit masks should shift to their bit index; packed 8-bit `VALUE0`-`VALUE3` fields should use `0xff`, `0xff00`, `0xff0000`, and `0xff000000`; full-width fields should have shift zero.
- Register table or helper validation for BACO and SMU memory-clock setup: read-modify-write helpers should preserve unrelated bits when applying `MPLL_CNTL_MODE`, `MCLK_PWRMGT_CNTL`, and `DLL_CNTL` fields.
- Runtime power-management smoke tests on supported CI/Tonga/Iceland/SMU7 hardware: memory-clock changes, BACO entry/exit, suspend/resume, and low-power state transitions should complete without hangs or PLL/DLL lock failures.
- Debugfs/register-dump checks can compare `MC_SEQ_G5PDX_*` and `MC_SEQ_PMG_DVS_*` normal-vs-`_LP` values after the SMU mirror-copy path runs.
- Hardware memory stress or error-injection validation can exercise `MC_SEQ_TCG_CNTL`, `MC_SEQ_TSM_*`, and `MC_SEQ_DRAM_ERROR_INSERTION` paths where they are exposed by diagnostic tooling.

## Chunk Notes For Merge Lane

This is a partial chunk of a much larger generated register mask header. Whole-file research should merge it with chunks 1, 2, and 4 for `gmc_8_1_sh_mask.h` before summarizing register coverage. This chunk is the dense middle/tail section for GMC memory sequencer training, memory PLL/power control, PHY timing, IO debug, low-power mirror, DVS, and PHY broadcast bitfield definitions.
