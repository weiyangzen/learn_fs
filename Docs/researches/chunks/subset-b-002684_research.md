# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_3_offset.h lines 7414-7450

## Scope

This chunk is the end of the generated AMD GC 9.4.3 register-offset header. It covers the tail of the `sqind` address block, specifically shader queue wavefront indirect-register offsets for program counter, instruction words, IB debug state, trap temporary registers, `M0`, execution masks, and SQ interrupt-word aliases. The file closes immediately after these definitions with the header guard `#endif`.

## Purpose

`gc_9_4_3_offset.h` supplies compile-time register numbers for GC 9.4.3 hardware. This range is for SQ indexed registers rather than direct MMIO registers. Driver code passes these `ixSQ_*` offsets through `regSQ_IND_INDEX`/`regSQ_IND_DATA` accessors to inspect per-wavefront state on a selected XCC, SIMD, wave, and sometimes thread.

The constants in this chunk let AMDGPU debug and fault-analysis paths read live shader wave state without embedding raw SQ index values. They are paired with field definitions in `gc_9_4_3_sh_mask.h` when software needs to decode returned register values, especially the `SQ_INTERRUPT_WORD_*` layouts.

## Important API Surface

- `ixSQ_WAVE_PC_LO` and `ixSQ_WAVE_PC_HI` define the low and high parts of the wavefront program counter.
- `ixSQ_WAVE_INST_DW0` and `ixSQ_WAVE_INST_DW1` expose the current or captured instruction doublewords for the selected wave.
- `ixSQ_WAVE_IB_DBG0`, `ixSQ_WAVE_IB_DBG1`, and `ixSQ_WAVE_FLUSH_IB` describe indirect offsets for instruction-buffer debug and flush state.
- `ixSQ_WAVE_TTMP0` through `ixSQ_WAVE_TTMP15` cover the trap temporary register window at offsets `0x026c` through `0x027b`.
- `ixSQ_WAVE_M0`, `ixSQ_WAVE_EXEC_LO`, and `ixSQ_WAVE_EXEC_HI` expose the scalar `M0` register and 64-bit execution mask halves.
- `ixSQ_INTERRUPT_WORD_AUTO_CTXID`, `ixSQ_INTERRUPT_WORD_AUTO_HI`, `ixSQ_INTERRUPT_WORD_AUTO_LO`, `ixSQ_INTERRUPT_WORD_CMN_CTXID`, `ixSQ_INTERRUPT_WORD_CMN_HI`, `ixSQ_INTERRUPT_WORD_WAVE_CTXID`, `ixSQ_INTERRUPT_WORD_WAVE_HI`, and `ixSQ_INTERRUPT_WORD_WAVE_LO` all alias SQ indirect offset `0x20c0`; the different names reflect alternate interpretations of the same interrupt payload.

There are no C functions, types, or structs in this chunk. The public interface is the generated preprocessor namespace of `ix...` constants.

## Control Flow

The header has no direct control flow. Runtime consumers follow the SQ indirect access pattern:

1. Select wave identity fields such as XCC, SIMD, wave, and optionally thread.
2. Program `regSQ_IND_INDEX` with the selected IDs, one of these `ixSQ_*` offsets shifted into `SQ_IND_INDEX__INDEX`, and `SQ_IND_INDEX__FORCE_READ_MASK`.
3. Read `regSQ_IND_DATA` to retrieve the selected wave register. Bulk SGPR/VGPR reads use the same path with `SQ_IND_INDEX__AUTO_INCR_MASK`.

In `amdgpu/gfx_v9_4_3.c`, `wave_read_ind()` implements this pattern. `gfx_v9_4_3_read_wave_data()` uses the constants from this final header region, including `ixSQ_WAVE_PC_LO`, `ixSQ_WAVE_PC_HI`, `ixSQ_WAVE_EXEC_LO`, `ixSQ_WAVE_EXEC_HI`, `ixSQ_WAVE_INST_DW0`, `ixSQ_WAVE_INST_DW1`, `ixSQ_WAVE_IB_DBG0`, `ixSQ_WAVE_M0`, and neighboring wave-state offsets, to build a type-1 wave dump.

## State and Persistence

The macros are stateless compile-time constants. The hardware state they address is volatile per-wave SQ execution state: program counter, instruction state, instruction-buffer debug state, trap temporary registers, scalar addressing state, and active-lane masks can change as shader waves execute, trap, stall, or retire.

Reads through `regSQ_IND_INDEX`/`regSQ_IND_DATA` are snapshots of selected live hardware state, not persisted driver-owned state. `ixSQ_WAVE_FLUSH_IB` is a control-oriented SQ indexed register, so incorrect use could affect the selected wave's instruction buffer behavior rather than just observing it. The `SQ_INTERRUPT_WORD_*` aliases describe interrupt payload storage/decoding state; the matching mask header determines which bits mean context ID, common high bits, wave fields, or split high/low forms.

## Dependencies and Integration Points

- Depends on AMD's generated GC 9.4.3 register specification and must remain synchronized with `gc_9_4_3_sh_mask.h`, especially the `SQ_IND_INDEX` fields and `SQ_INTERRUPT_WORD_*` bit layouts.
- Integrated by `amdgpu/gfx_v9_4_3.c` wave-dump helpers through `WREG32_SOC15_RLC()`, `RREG32_SOC15()`, `GET_INST(GC, xcc_id)`, `regSQ_IND_INDEX`, and `regSQ_IND_DATA`.
- Shares the broader generated-register pattern with neighboring GC 9.x headers; the same symbol names appear in other ASIC headers but may differ across generations, so consumers rely on including the ASIC-specific offset header.
- SQ interrupt-word aliases integrate with KFD and interrupt-processing code conceptually: payload decoding uses `SQ_INTERRUPT_WORD_*` field masks, while this offset header provides the indirect location for GC 9.4.3.

## Risks

- Offset drift is the main risk. A wrong `ixSQ_WAVE_*` value would cause wave dumps to read unrelated SQ state, producing misleading crash diagnostics or bad debugger data.
- The chunk is a partial address-block tail. Earlier wave offsets such as status, trap status, HW ID, and allocation state are defined before line 7414, so merge tooling must combine this chunk with adjacent chunks for complete `sqind` coverage.
- The `ixSQ_INTERRUPT_WORD_*` names intentionally alias the same `0x20c0` offset. Treating them as separate hardware locations would be a documentation or consumer bug; the difference is in payload interpretation, not address.
- Reads of live wave state are timing-sensitive. Without a stopped or stable wave, PC, EXEC, instruction, and TTMP values can change between reads, giving an inconsistent snapshot.
- Any write path using `ixSQ_WAVE_FLUSH_IB` or trap temporary offsets must ensure the selected SIMD/wave/thread context is correct, because SQ indirect selection errors can disturb the wrong wave.

## Test Signals

- Build AMDGPU with GC 9.4.3 support to catch missing or renamed generated macros in `gfx_v9_4_3.c` and related generated-header includes.
- Compare this exact range against the authoritative GC 9.4.3 register source to verify `PC`, `INST`, `IB_DBG`, `TTMP`, `M0`, `EXEC`, and `SQ_INTERRUPT_WORD` offsets.
- Exercise GPU hang or debugfs wave-dump paths on GC 9.4.3 hardware and verify returned PC/EXEC/instruction fields look plausible and match known-good traces.
- Trigger KFD/SQ interrupt scenarios and validate that interrupt-word decoding remains aligned with the shared `0x20c0` offset and the masks in `gc_9_4_3_sh_mask.h`.
- Run suspend/resume and GPU reset recovery tests, then repeat wave-dump collection to catch stale indirect-index programming or ASIC-generation include mismatches.
