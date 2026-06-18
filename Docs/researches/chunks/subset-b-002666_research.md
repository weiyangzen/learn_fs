# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_2_offset.h lines 7411-7687

## Purpose

This chunk is the tail of the generated GC 9.4.2 register-offset header. It defines symbolic offsets for three indirect register address spaces and then closes the include guard:

- `gccacind`: graphics-core CAC/LCAC weighting, accumulator, override, throttling-pattern, and fixed-pattern performance-counter offsets.
- `secacind`: shader-engine CAC control/override offsets.
- `sqind`: shader-queue debug, wave-state, trap/status, temporary register, execution-mask, and SQ interrupt-word offsets.

The definitions are compile-time constants only. They let AMDGPU and KFD code address GC 9.4.2 hardware registers through named macros instead of hard-coded numeric indices. In this generated header, the `ix*` prefix marks indexed/indirect register offsets rather than ordinary memory-mapped `reg*` offsets. Earlier in the same source file, the real MMIO index/data ports are defined as `regGC_CAC_IND_INDEX`, `regGC_CAC_IND_DATA`, `regSE_CAC_IND_INDEX`, `regSE_CAC_IND_DATA`, `regSQ_IND_INDEX`, and `regSQ_IND_DATA`; this chunk supplies the values written into those index ports.

## Important APIs, Types, And Data

There are no C functions, structs, enums, or callable APIs in this chunk. The API surface is the set of preprocessor names exported to AMDGPU/KFD code and sibling generated headers:

- `ixGC_CAC_WEIGHT_*` maps CAC contribution weights for many GC blocks: `SC`, `SPI`, `SQ`, `SX`, `SXRB`, `TA`, `TCC`, `TCP`, `TD`, `VGT`, `WD`, `CU`, `EA`, `RMI`, `UTCL2_ATCL2`, `UTCL2_ROUTER`, `UTCL2_VML2`, and `UTCL2_WALKER`.
- `ixGC_CAC_ACC_*` maps CAC accumulator readouts for the same broad set of blocks, including split lower/upper SQ accumulators (`ixGC_CAC_ACC_SQ0_LOWER` through `ixGC_CAC_ACC_SQ8_UPPER`) and per-CU accumulators (`ixGC_CAC_ACC_CU0` through `ixGC_CAC_ACC_CU13`).
- `ixGC_CAC_OVRD_*` maps per-block CAC override selectors for BCI, CB, CP, DB, GDS, IA, LDS, PA, PC, SC, SPI, CU, SQ, SX, SXRB, TA, TCC, TCP, TD, VGT, WD, EA, RMI, and UTCL2 subblocks.
- `ixEDC_STALL_PATTERN_*`, `ixPCC_STALL_PATTERN_*`, `ixPCC_THROT_*`, `ixPWRBRK_STALL_PATTERN_*`, and `ixPCC_PWRBRK_HYSTERESIS_CTRL` expose power/throttling pattern registers in the same GC CAC indirect space.
- `ixFIXED_PATTERN_PERF_COUNTER_CTRL` and `ixFIXED_PATTERN_PERF_COUNTER_1` through `_10` expose fixed-pattern performance-counter control and count slots.
- `ixSE_CAC_CNTL`, `ixSE_CAC_OVR_SEL`, and `ixSE_CAC_OVR_VAL` are the minimal shader-engine CAC indirect register set.
- `ixSQ_*` names expose SQ-local debug and wave registers: `ixSQ_DEBUG_STS_LOCAL`, `ixSQ_DEBUG_CTRL_LOCAL`, `ixSQ_WAVE_VALID_AND_IDLE`, `ixSQ_WAVE_MODE`, `ixSQ_WAVE_STATUS`, `ixSQ_WAVE_TRAPSTS`, `ixSQ_WAVE_HW_ID`, `ixSQ_WAVE_GPR_ALLOC`, `ixSQ_WAVE_LDS_ALLOC`, `ixSQ_WAVE_IB_STS`, `ixSQ_WAVE_PC_LO`, `ixSQ_WAVE_PC_HI`, `ixSQ_WAVE_INST_DW0`, `ixSQ_WAVE_INST_DW1`, `ixSQ_WAVE_IB_DBG0`, `ixSQ_WAVE_IB_DBG1`, `ixSQ_WAVE_FLUSH_IB`, `ixSQ_WAVE_TTMP*`, `ixSQ_WAVE_M0`, `ixSQ_WAVE_EXEC_LO`, and `ixSQ_WAVE_EXEC_HI`.
- `ixSQ_INTERRUPT_WORD_AUTO_CTXID`, `_AUTO_HI`, `_AUTO_LO`, `_CMN_CTXID`, `_CMN_HI`, `_WAVE_CTXID`, `_WAVE_HI`, and `_WAVE_LO` are all aliases for offset `0x20c0`; the companion mask header gives different field interpretations for the same interrupt payload.

The companion `gc_9_4_2_sh_mask.h` provides the field contract. For the CAC and CAC-index data ports, the masks are mostly full-width 32-bit data fields. For SQ wave state, the masks describe decoded wave status (`VALID`, `HALT`, `TRAP`, `ECC_ERR`, `EXECZ`, `VCCZ`, etc.), hardware identity (`WAVE_ID`, `SIMD_ID`, `CU_ID`, `SH_ID`, `SE_ID`, `VM_ID`, `QUEUE_ID`), allocation fields, instruction-buffer counters, program-counter halves, `TTMP` data, `M0`, and `EXEC` halves. The interrupt-word masks define the GC 9 encoded SQ interrupt payload used by KFD.

## Control Flow

This header has no runtime control flow. The runtime access pattern is created by call sites that combine these offsets with index/data register helpers.

For SQ wave inspection, local AMDGPU call sites show the intended flow clearly. In `amdgpu/gfx_v9_0.c`, `wave_read_ind()` writes `mmSQ_IND_INDEX` with selected `WAVE_ID`, `SIMD_ID`, the supplied `ixSQ_WAVE_*` address, and `SQ_IND_INDEX__FORCE_READ_MASK`, then reads `mmSQ_IND_DATA`. `gfx_v9_0_read_wave_data()` calls that helper for `ixSQ_WAVE_STATUS`, `PC_LO`, `PC_HI`, `EXEC_LO`, `EXEC_HI`, `HW_ID`, instruction words, allocation registers, trap status, IB status/debug, `M0`, and wave mode. `amdgpu/gfx_v9_4_3.c` uses the same pattern with `GET_INST(GC, xcc_id)` and `regSQ_IND_INDEX`/`regSQ_IND_DATA` for multi-XCC hardware.

For SQ interrupts, `amdkfd/kfd_int_process_v9.c` decodes interrupt-ring `context_id0/context_id1` with `SQ_INTERRUPT_WORD_*` field masks. The code first extracts the `ENCODING` field, then treats the payload as `AUTO`, `INST`, or `ERROR`; wave-encoded interrupts are further decoded into SE, shader array, privilege, wave, SIMD, CU, and data fields. The offset aliases in this chunk describe the hardware source register for those payload shapes, while the non-generated KFD path usually works with the captured IH context words.

For GC CAC and SE CAC, the expected flow is analogous to SQ indirect access: code writes a `ixGC_CAC_*` or `ixSE_CAC_*` offset to the relevant CAC index register and reads or writes the matching data register. Earlier offsets in the same header expose those index/data MMIO ports; this chunk defines the tail of the CAC table that callers select through them.

## State And Persistence Behavior

The macros themselves are stateless and disappear after preprocessing. The named hardware registers are stateful:

- CAC weight and override registers configure how hardware estimates or overrides per-block graphics-core power/current contribution. These values can persist in hardware until reset, power-gating, firmware reinitialization, or explicit driver/SMU programming.
- CAC accumulator registers are telemetry/state readouts. They are volatile hardware counters or accumulated values whose meaning depends on CAC enablement, snapshot, and reset behavior outside this chunk.
- EDC/PCC/PWRBRK stall-pattern and hysteresis registers influence hardware throttling behavior. Writes can change throttling response and must be coordinated with power-management policy.
- Fixed-pattern performance counters are hardware telemetry slots controlled by `ixFIXED_PATTERN_PERF_COUNTER_CTRL`.
- SQ wave registers describe live shader wave execution state. They are only meaningful while a selected wave/SIMD exists and may change as the GPU runs. Debug reads must select the intended wave and handle idle/invalid states.
- `ixSQ_WAVE_FLUSH_IB` is a control-style SQ indirect register; using it can alter instruction-buffer state rather than just observe it.
- SQ interrupt-word registers and IH context payloads are transient event state. KFD consumes captured values from the interrupt handler rather than persisting them.

No software persistence, file storage, or cached kernel object is implemented by this header.

## Dependencies

This chunk depends on the generated GC 9.4.2 register set remaining synchronized with AMD's ASIC specification. Important local dependencies are:

- `gc_9_4_2_offset.h` earlier sections, which define the ordinary MMIO index/data ports used to reach these indirect offsets.
- `gc_9_4_2_sh_mask.h`, which defines fields and masks for the register names in this chunk.
- SOC15 access helpers such as `RREG32_SOC15`, `WREG32_SOC15_RLC`, and `WREG32_SOC15_RLC_SHADOW_EX`.
- GFX9/GFX9.4 AMDGPU debug paths that read wave state through `SQ_IND_INDEX`/`SQ_IND_DATA`.
- KFD GC 9 interrupt-processing code that decodes `SQ_INTERRUPT_WORD_*` payload fields.
- Power-management and firmware policy code that may own CAC, PCC, PWRBRK, EDC, and fixed-pattern performance-counter programming.

The offsets are generation-specific. Similar macro names exist in GC 9.0, GC 9.4.3, GC 10.x, GC 11.x, and GC 12.x headers, but the numeric indices and available wave registers differ. For example, GC 10+ wave register tables introduce additional `HW_ID1/HW_ID2`, scratch, and scheduling registers, and GC 12 interrupt decoding uses a wider/two-word layout. Code must include the correct ASIC header for the selected IP block.

## Integration Points

The main integration points are generated AMD register include consumers:

- AMDGPU GFX debug and devcoredump paths call `wave_read_ind()` and `wave_read_regs()` with `ixSQ_WAVE_*` offsets to collect live wave state.
- KFD interrupt processing decodes SQ interrupt context words with the matching `SQ_INTERRUPT_WORD_*` masks, which correspond to the `0x20c0` SQ interrupt-word aliases in this chunk.
- Power-management, SMU, and diagnostic tooling can select `ixGC_CAC_*` and `ixSE_CAC_*` offsets through CAC indirect index/data ports to program CAC weights/overrides or read accumulator/performance-counter telemetry.
- Hardware validation or bring-up code can compare offset definitions in this file with `gc_9_4_2_sh_mask.h` field definitions and with sibling GC generation headers.

Because this is a header-only metadata fragment, all integration is compile-time inclusion plus runtime register access by other modules.

## Risks

- A wrong `ix` offset silently targets the wrong indirect register. For CAC/PCC/PWRBRK registers, that can misprogram throttling or power estimation; for SQ registers, it can produce misleading wave dumps or disturb debug state.
- `gccacind`, `secacind`, and `sqind` use separate index/data mechanisms. Reusing a macro with the wrong index port can read meaningless data or affect unrelated hardware.
- Several registers are control/override registers, not passive telemetry. Writes to `ixGC_CAC_OVRD_*`, `ixSE_CAC_OVR_*`, `ixPWRBRK_*`, or `ixSQ_WAVE_FLUSH_IB` can change hardware behavior.
- SQ wave reads are inherently racy with GPU execution. A wave may advance, terminate, trap, or be rescheduled between selecting the index and reading the data.
- The `ixSQ_INTERRUPT_WORD_*` names alias the same `0x20c0` offset with multiple semantic views. Consumers must choose the field layout according to the `ENCODING` bits, as KFD does.
- Cross-generation copy/paste is unsafe. The macro names look stable, but GC 9.4.2 offsets and field widths are not a universal contract across AMD GPU IP generations.
- Manual edits to generated register headers can desynchronize offset and mask headers, creating compile-time success with runtime register corruption.

## Test Signals

Useful validation signals are mostly build-time, static, and hardware-facing:

- Build AMDGPU/KFD configurations that include GC 9.4.2 generated headers and exercise GFX9-era debug and KFD interrupt code.
- Static checks that every `ixSQ_WAVE_*` and `ixSQ_INTERRUPT_WORD_*` offset used by GFX/KFD has a matching field definition in `gc_9_4_2_sh_mask.h`.
- Static checks that `ixGC_CAC_*` and `ixSE_CAC_*` macros are only used with the corresponding CAC index/data ports, and `ixSQ_*` macros only with SQ indirect access.
- Runtime wave-dump smoke tests on supported GC 9.x hardware: selected waves should return plausible `STATUS`, `PC`, `EXEC`, `HW_ID`, allocation, trap, and instruction-buffer values without invalid register access faults.
- KFD SQ interrupt tests should show correct decoding of automatic, instruction, and error encodings, including SE/wave/SIMD/CU fields.
- Power-management regression tests should verify that CAC/PCC/PWRBRK programming still applies expected throttling policy and that accumulator/performance-counter reads behave as 32-bit volatile telemetry.
- Header consistency checks should compare this chunk against adjacent generated GC 9.4.2 mask definitions and sibling GC 9.x offset tables to catch missing aliases or accidental numeric drift.
