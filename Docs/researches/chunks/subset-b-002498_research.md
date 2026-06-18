# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_default.h lines 5858-6114

## Scope

This chunk is the final segment of the generated AMD GC 11.0.0 default-register header. It contains only C preprocessor `#define` constants for hardware reset/default values; it declares no functions, structs, enums, storage objects, or executable initialization code.

The range starts at the tail of the `gccacind` address block with `ixFIXED_PATTERN_PERF_COUNTER_4_DEFAULT` through `ixFIXED_PATTERN_PERF_COUNTER_10_DEFAULT` and `ixHW_LUT_UPDATE_STATUS_DEFAULT`. It then covers the full `secacind` block, the full `grtavfsind` RTAVFS register table from `ixRTAVFS_REG0_DEFAULT` through `ixRTAVFS_REG194_DEFAULT`, and the tail `sqind` block from local SQ debug state through selected-wave execution masks. The range ends with the header's `#endif`.

## Purpose

`gc_11_0_0_default.h` is generated hardware metadata for AMDGPU GC 11 ASICs. Its `_DEFAULT` macros document the reset value associated with register names from the matching GC register offset header. Driver code includes this header with `gc_11_0_0_offset.h` and `gc_11_0_0_sh_mask.h` so GC 11 code can compile against one ASIC-specific set of register names, offsets, masks, and known baseline values.

This chunk documents late-file indexed register defaults rather than programming policy:

- The fixed-pattern counter and LUT-status defaults describe the idle baseline for the end of the global CAC/power-management indexed register area.
- The `secacind` defaults describe per-shader-engine CAC selector/control reset state.
- The `grtavfsind` defaults describe real-time adaptive voltage/frequency scaling table and status reset words.
- The `sqind` defaults describe selected-wave debug/readout state reset values for shader queue wave inspection.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The important interface is the generated macro convention:

- `ix<REGISTER>_DEFAULT` gives the default value for an indexed register accessed through an indirect register block.
- Matching `ix<REGISTER>` address macros live in `gc_11_0_0_offset.h`.
- Matching bit shifts and masks live in `gc_11_0_0_sh_mask.h`.
- Normal consumers combine these generated definitions with AMDGPU register helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `REG_SET_FIELD`, `REG_GET_FIELD`, and indirect-register selector/data sequences.

Notable macro groups in this chunk:

- `ixFIXED_PATTERN_PERF_COUNTER_4_DEFAULT` through `ixFIXED_PATTERN_PERF_COUNTER_10_DEFAULT`: fixed-pattern performance-counter defaults at the end of the global CAC indexed block. All reset to `0x00000000`.
- `ixHW_LUT_UPDATE_STATUS_DEFAULT`: hardware LUT update status default. It resets to `0x00000000`, matching an idle/no-status baseline.
- `ixSE_CAC_ID_DEFAULT` and `ixSE_CAC_CNTL_DEFAULT`: shader-engine CAC ID and control defaults. `ID` resets to zero; `CNTL` resets to `0x000000ff`. In the companion mask header, `SE_CAC_CNTL` exposes a `CAC_THRESHOLD` field, so the default represents a nonzero threshold/control value rather than an all-disabled word.
- `ixRTAVFS_REG0_DEFAULT` through `ixRTAVFS_REG194_DEFAULT`: RTAVFS register-table defaults. The table is mostly zero but has several important nonzero runs and singleton values:
  - `REG0`-`REG4` = `0x01000000`.
  - `REG32`-`REG42` = `0x000000ff`.
  - `REG43` = `0xcccdbcdd`, whose masks split the word into PI-controller proportional/integral nibbles (`RTAVFSKP*`/`RTAVFSKI*`).
  - `REG44` = `0x2587d190`, whose masks expose voltage-code fields and binary-search/hardware-calibration bits.
  - `REG46` = `0x000211cd`, `REG47` = `0x000af12c`, `REG48` = `0x00000010`, and `REG51` = `0x00000008`.
  - `REG54`-`REG72`, `REG80`-`REG101`, `REG109`-`REG111`, and `REG115`-`REG117` = `0x01000000`.
  - `REG73`-`REG79`, `REG102`-`REG108`, and `REG112`-`REG114` = `0x00000100`.
  - `REG118`-`REG188` are zero, except `REG189` = `0x0007d12c`.
  - `REG193` = `0x00000001`; `REG190`-`REG192` and `REG194` reset to zero.
- `ixSQ_DEBUG_STS_LOCAL_DEFAULT` and `ixSQ_DEBUG_CTRL_LOCAL_DEFAULT`: local SQ debug status/control defaults, both zero.
- `ixSQ_WAVE_ACTIVE_DEFAULT` and `ixSQ_WAVE_VALID_AND_IDLE_DEFAULT`: selected-wave slot/activity/idle views, both zero at reset.
- `ixSQ_WAVE_MODE_DEFAULT`, `ixSQ_WAVE_STATUS_DEFAULT`, and `ixSQ_WAVE_TRAPSTS_DEFAULT`: selected-wave mode, status, and trap-state views. The companion mask header defines floating-point mode bits, exception enables, privilege/debug/status bits, valid/idle flags, trap events, and exception fields; all reset to zero in this generated default table.
- `ixSQ_WAVE_GPR_ALLOC_DEFAULT`, `ixSQ_WAVE_LDS_ALLOC_DEFAULT`, `ixSQ_WAVE_IB_STS_DEFAULT`, `ixSQ_WAVE_IB_STS2_DEFAULT`, `ixSQ_WAVE_IB_DBG1_DEFAULT`, and `ixSQ_WAVE_FLUSH_IB_DEFAULT`: selected-wave allocation, instruction-buffer status, debug, and flush views, all zero.
- `ixSQ_WAVE_PC_LO_DEFAULT`, `ixSQ_WAVE_PC_HI_DEFAULT`, `ixSQ_WAVE_FLAT_SCRATCH_LO_DEFAULT`, `ixSQ_WAVE_FLAT_SCRATCH_HI_DEFAULT`, `ixSQ_WAVE_M0_DEFAULT`, `ixSQ_WAVE_EXEC_LO_DEFAULT`, and `ixSQ_WAVE_EXEC_HI_DEFAULT`: full-width selected-wave scalar/debug state and execution-mask words, all zero.
- `ixSQ_WAVE_HW_ID1_DEFAULT` and `ixSQ_WAVE_HW_ID2_DEFAULT`: selected-wave hardware identity words, both zero. The mask header splits these into wave/SIMD/WGP/SA/SE and queue/pipe/ME/state/workgroup/VM fields.
- `ixSQ_WAVE_TTMP0_DEFAULT`, `ixSQ_WAVE_TTMP1_DEFAULT`, and `ixSQ_WAVE_TTMP3_DEFAULT` through `ixSQ_WAVE_TTMP15_DEFAULT`: trap temporary register defaults, all zero. `TTMP2` is not present in this chunk's generated list.
- `ixSQ_WAVE_POPS_PACKER_DEFAULT`, `ixSQ_WAVE_SCHED_MODE_DEFAULT`, and `ixSQ_WAVE_SHADER_CYCLES_DEFAULT`: selected-wave packing, scheduling, and cycle-count views, all zero.

## Control Flow

This header has no runtime control flow. The direct behavior is compile-time substitution of constants by the C preprocessor.

The implied consumer flow is:

1. Include the GC 11.0.0 offset, shift/mask, and default headers for the active ASIC generation.
2. Select a register through an `ix...` macro and the appropriate indirect-address path.
3. Read, write, or read-modify-write the selected register through SOC15 or block-specific helpers.
4. Use the `_DEFAULT` macro as generated reset documentation, an initialization-table baseline, or a comparison/restoration value.

The SQ wave debug path shows the register-access pattern around this chunk. In `gfx_v11_0.c`, `wave_read_ind()` writes `regSQ_IND_INDEX` with a wave ID and indexed SQ register address, then reads `regSQ_IND_DATA`. `gfx_v11_0_read_wave_data()` reads many of this chunk's `ixSQ_WAVE_*` registers, including `STATUS`, `PC_LO`, `PC_HI`, `EXEC_LO`, `EXEC_HI`, `HW_ID1`, `HW_ID2`, `GPR_ALLOC`, `LDS_ALLOC`, `TRAPSTS`, `IB_STS`, `IB_STS2`, `IB_DBG1`, `M0`, and `MODE`.

For CAC and RTAVFS registers, real sequencing occurs in power-management, firmware, or hardware-init paths outside this file: choose the indexed block, program thresholds or table entries, poll status, and restore hardware policy after reset/resume. This header only records the generated reset baseline those flows must be compatible with.

## State And Persistence

The chunk stores no software state. All definitions are compile-time constants and allocate no memory.

The represented state is hardware state:

- Fixed-pattern counters and hardware LUT status represent counter/status state in the global CAC indexed block.
- `secacind` state represents per-shader-engine CAC identity and threshold/control state.
- RTAVFS state represents adaptive voltage/frequency controller table entries, PI-controller constants, voltage-code values, binary-search/calibration controls, status words, and FSM state. Several defaults are nonzero and should be treated as ASIC-specific reset data.
- SQ state represents selected-wave debug state: activity, validity/idle status, mode/status/trap flags, register allocation metadata, program counter, instruction-buffer counters, scratch pointers, hardware identity, trap temporaries, scalar `M0`, execution masks, scheduling state, and shader-cycle accounting.

Hardware reset, GPU reset, suspend/resume, runtime power management, firmware bring-up, and shader debug/fault collection are the events that make these defaults relevant. Runtime software may observe values very different from these defaults after firmware or driver initialization, especially for RTAVFS and SQ wave state.

## Dependencies And Integration Points

This generated header depends on the surrounding ASIC register description set:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_offset.h` supplies indexed register addresses such as `ixFIXED_PATTERN_PERF_COUNTER_4`, `ixSE_CAC_CNTL`, `ixRTAVFS_REG0`, `ixRTAVFS_REG189`, and `ixSQ_WAVE_ACTIVE`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_sh_mask.h` supplies field interpretation for `SE_CAC_CNTL`, RTAVFS table words, and SQ wave debug/status registers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0.c` uses the matching SQ indexed register names to read wave debug data through `regSQ_IND_INDEX` and `regSQ_IND_DATA`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v11_0.c`, `mes_v12_0.c`, `mes_v12_1.c`, `sdma_v6_0.c`, and `gfxhub_v3_0.c` include `gc_11_0_0_default.h` with the matching offset/mask headers for GC 11-family programming.
- Other GC 11 consumers include `amdgpu_amdkfd_gfx_v11.c`, `imu_v11_0.c`, `soc21.c`, display helpers, and SDMA/GFXHUB paths that include the offset and mask headers even when they do not include this default header directly.

The chunk is source-tree-aligned with `drivers/gpu/drm/amd/include/asic_reg/gc/`. It must remain synchronized with the generated GC 11.0.0 offset and mask headers; changing a default independently from the generated address/mask metadata can create a compile-clean but semantically inconsistent hardware description.

## Risks And Edge Cases

- Generated-header drift is the primary risk. Defaults, offsets, and masks must come from the same hardware database and ASIC revision.
- RTAVFS names are opaque (`REG0`-`REG194`), so many values cannot be reviewed semantically from the default header alone. Nonzero defaults such as `0xcccdbcdd`, `0x2587d190`, `0x000211cd`, `0x000af12c`, `0x0007d12c`, and `0x00000001` need validation against the generator or hardware specification.
- The RTAVFS table contains large repeated runs of `0x01000000`, `0x00000100`, `0x000000ff`, and zeros. Mechanical regeneration, sorting, or deduplication mistakes could silently move values to the wrong table index.
- `ixSE_CAC_CNTL_DEFAULT` is `0x000000ff`, not zero. Treating all CAC registers as zero-initialized would lose a meaningful shader-engine threshold/control default.
- SQ wave defaults are zero because they describe reset/idle selected-wave readout state, not because live wave state is expected to be zero. Debug and hang-analysis code must read live registers through the SQ indirect path after selecting the target wave.
- The generated SQ TTMP list skips `ixSQ_WAVE_TTMP2_DEFAULT` in this chunk. Consumers should rely on generated register names rather than assuming every numbered register appears in a contiguous default list.
- The header itself cannot validate hardware behavior. Incorrect values can surface only as ASIC-specific power-management instability, throttling anomalies, GPU reset/resume issues, hang-dump decoding errors, or shader debug regressions.

## Test Signals

There are no unit-testable functions in this chunk. Useful validation signals are build, generation, and hardware-integration oriented:

- Build coverage for AMDGPU files that include `gc_11_0_0_default.h`, especially MES, SDMA v6, and GFXHUB GC 11 paths.
- Compile-time detection of missing or renamed `ix...` macros when default, offset, and mask headers are regenerated inconsistently.
- GPU initialization and firmware bring-up logs on GC 11 hardware, especially MES and SDMA initialization paths that include this default header.
- Runtime power-management and throttling telemetry that can expose incorrect CAC or RTAVFS defaults after reset/resume.
- Suspend/resume and GPU reset testing on GC 11 ASICs, which can expose bad assumptions about RTAVFS or CAC reset state.
- Shader fault, hang-dump, wave-debug, and trap handling tests that exercise SQ indirect reads of `SQ_WAVE_*` registers through `gfx_v11_0_read_wave_data()`.
- Register-header regeneration checks comparing this file against the authoritative hardware database so table index/value ordering is preserved.
