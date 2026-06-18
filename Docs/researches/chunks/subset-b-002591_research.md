# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_offset.h lines 12405-12418

## Scope

This chunk is the final slice of AMD's generated GC 12.1.0 register-offset header. It covers the tail of the `gfx_se_sqind` indirect shader-queue register namespace and the closing `#endif` for `_gc_12_1_0_OFFSET_HEADER`.

The exact register-offset macros in this range are:

- `ixSQ_WAVE_TTMP8` through `ixSQ_WAVE_TTMP15`, with offsets `0x0274` through `0x027b`.
- `ixSQ_WAVE_M0`, with offset `0x027d`.
- `ixSQ_WAVE_EXEC_LO` and `ixSQ_WAVE_EXEC_HI`, with offsets `0x027e` and `0x027f`.

This source file is hardware metadata for AMDGPU GC 12.1.0 devices. It contains preprocessor constants only; there are no functions, structs, variables, locks, allocation paths, or executable control flow in the requested lines.

## Purpose

The purpose of this chunk is to publish the indirect SQ wave-state indices needed to read selected live wavefront registers on GC 12.1.0 hardware. The `ix` prefix marks these as indirect register indices rather than ordinary `reg*` MMIO offsets. Driver code selects a wave through `regSQ_IND_INDEX`, writes one of these indices into the SQ indirect `INDEX` field, and reads or auto-increments through `regSQ_IND_DATA`.

The covered values describe per-wave architectural/debug state:

- `TTMP8`-`TTMP15`: trap temporary scalar registers visible through the SQ wave debug path.
- `M0`: the per-wave scalar register used by shader instructions for LDS/GDS and address-related operations, exposed for debug collection.
- `EXEC_LO` and `EXEC_HI`: the low and high halves of the wave execution mask, indicating active lanes in the wavefront.

Together with the preceding lines in the same `gfx_se_sqind` block, these constants allow AMDGPU debug and diagnostic paths to capture wave PC, status, allocation, exception, scheduling, trap, and execution-mask state.

## Important APIs, Types, And Macros

The exported interface is a set of untyped C preprocessor constants:

- `ixSQ_WAVE_TTMP8` = `0x0274`
- `ixSQ_WAVE_TTMP9` = `0x0275`
- `ixSQ_WAVE_TTMP10` = `0x0276`
- `ixSQ_WAVE_TTMP11` = `0x0277`
- `ixSQ_WAVE_TTMP12` = `0x0278`
- `ixSQ_WAVE_TTMP13` = `0x0279`
- `ixSQ_WAVE_TTMP14` = `0x027a`
- `ixSQ_WAVE_TTMP15` = `0x027b`
- `ixSQ_WAVE_M0` = `0x027d`
- `ixSQ_WAVE_EXEC_LO` = `0x027e`
- `ixSQ_WAVE_EXEC_HI` = `0x027f`

The main consumer pattern is visible in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v12_1.c`. Its `wave_read_ind()` helper writes `regSQ_IND_INDEX` using `SQ_IND_INDEX__WAVE_ID__SHIFT` and `SQ_IND_INDEX__INDEX__SHIFT`, then reads `regSQ_IND_DATA`. `gfx_v12_1_read_wave_data()` uses `ixSQ_WAVE_EXEC_LO`, `ixSQ_WAVE_EXEC_HI`, and `ixSQ_WAVE_M0` from this tail section while building type-4 wave debug data. Nearby helpers such as `wave_read_regs()` use the same indirect mechanism with `SQ_IND_INDEX__AUTO_INCR_MASK` for ranges of per-thread or per-wave registers.

The header is included by multiple GC 12.1.0 driver units, including `gfx_v12_1.c`, `mes_v12_1.c`, `amdgpu_amdkfd_gfx_v12_1.c`, `imu_v12_1.c`, `gfxhub_v12_1.c`, `soc_v1_0.c`, and `sdma_v7_1.c`. Not every include uses these exact wave offsets, but all depend on the same generated register namespace being synchronized with the matching `gc_12_1_0_sh_mask.h` field definitions and GC 12.1.0 silicon register database.

## Control Flow

This chunk has no direct runtime control flow. Runtime behavior comes from consumers that perform SQ indirect register reads:

1. Driver code selects the target graphics instance/XCC through SOC15 helpers such as `GET_INST(GC, xcc_id)`.
2. For a wave read, the driver writes `regSQ_IND_INDEX` with the target wave ID and one of the `ixSQ_WAVE_*` indices from this header.
3. The hardware SQ indirect path latches that selection.
4. The driver reads `regSQ_IND_DATA`, which returns the selected wave register value.
5. Higher-level debug code appends the value to a wave-state buffer for user-visible diagnostics or GPU debugging.

In `gfx_v12_1_read_wave_data()`, `ixSQ_WAVE_EXEC_LO`, `ixSQ_WAVE_EXEC_HI`, and `ixSQ_WAVE_M0` are interleaved with other wave-state indices such as `ixSQ_WAVE_STATUS`, `ixSQ_WAVE_PC_LO`, `ixSQ_WAVE_PC_HI`, allocation registers, exception flags, trap control, and scheduling mode. The function also warns if `simd != 0` because GC 12 encodes SIMD selection through the instance field in the surrounding `select_se_sh` path, not through the local SIMD argument.

## State And Persistence Behavior

These macros do not store software state and do not persist anything by themselves. They identify live hardware wavefront state inside the shader queue:

- `TTMP8`-`TTMP15` reflect trap temporary registers for the selected wave and are meaningful mainly when trap/debug state exists for that wave.
- `M0` reflects the selected wave's scalar `M0` value at the moment of the indirect read.
- `EXEC_LO` and `EXEC_HI` reflect the selected wave's current lane execution mask at the moment of capture.

The values returned through `regSQ_IND_DATA` are transient. They can change as the wave executes, stalls, traps, completes, or is invalidated. Persistence is hardware-defined and tied to wave residency rather than kernel-driver storage. If a selected wave slot is idle or changes between selection and read, consumers must rely on surrounding validity/status fields, such as `ixSQ_WAVE_STATUS` and `ixSQ_WAVE_VALID_AND_IDLE`, to interpret the data.

## Dependencies And Integration Points

This chunk depends on AMD's generated GC 12.1.0 register metadata. It must remain consistent with:

- `gc_12_1_0_sh_mask.h`, which defines bit positions and masks for `regSQ_IND_INDEX`, `regSQ_IND_DATA`, and related GC 12.1.0 registers.
- AMDGPU SOC15 register helpers such as `WREG32_SOC15()` and `RREG32_SOC15()`, which perform the actual MMIO accesses.
- The SQ indirect register protocol, especially the relationship between `regSQ_IND_INDEX`, `SQ_IND_INDEX__WAVE_ID__SHIFT`, `SQ_IND_INDEX__INDEX__SHIFT`, `SQ_IND_INDEX__WORKITEM_ID__SHIFT`, `SQ_IND_INDEX__AUTO_INCR_MASK`, and `regSQ_IND_DATA`.
- GC 12.1.0 wave debug collection in `gfx_v12_1.c`, which uses `ixSQ_WAVE_EXEC_LO`, `ixSQ_WAVE_EXEC_HI`, and `ixSQ_WAVE_M0` directly.
- Cross-version AMDGPU wave debug implementations in `gfx_v12_0.c`, `gfx_v11_0.c`, `gfx_v10_0.c`, and earlier GFX files, which use similarly named `ixSQ_WAVE_*` constants but may differ in exact offsets for some registers.

The path is under a `ceph-client` source mirror, but the file is AMD GPU driver metadata and has no distributed filesystem behavior.

## Risks And Edge Cases

- The constants are untyped preprocessor values. A wrong numeric index can compile cleanly and return the wrong wave register, causing misleading debug dumps or broken GPU fault analysis.
- These offsets are ASIC-specific. Reusing GC 12.1.0 values on another generation can be wrong even when macro names match. For example, nearby generated headers show generation differences for `ixSQ_WAVE_M0` between some GC/GCA families.
- The wave-state data is volatile. Reading `EXEC`, `M0`, or `TTMP` fields without checking wave validity can report stale or irrelevant data from an idle slot.
- Indirect SQ reads require correct selection sequencing. Incorrect wave ID, XCC/instance, shader engine, shader array, or SIMD selection can silently read a different wave than intended.
- The chunk boundary hides the preceding `TTMP0`-`TTMP7`, PC, status, exception, allocation, and scheduling offsets. Whole-file analysis should merge this chunk with the previous `gfx_se_sqind` chunk before making full claims about wave debug coverage.
- Manual edits are high risk because this file is generated from AMD register definitions. Divergence from the authoritative register database or sibling shift/mask header can break low-level diagnostics without producing ordinary compile-time type errors.

## Test Signals

Useful validation signals include:

- Build AMDGPU with GC 12.1.0 support enabled. Missing or renamed macros should fail in `gfx_v12_1.c` and other GC 12.1.0 units that include this header.
- Mechanically compare this tail block against AMD's authoritative GC 12.1.0 register database and adjacent generated headers such as `gc_12_0_0_offset.h` or `gc_11_0_0_offset.h`, while allowing expected ASIC-generation differences.
- Run GPU wave-state/debug dump paths on GC 12.1.0 hardware and verify that `EXEC_LO`, `EXEC_HI`, and `M0` fields appear in the expected order in type-4 wave data.
- Exercise GPU fault, hang, trap, or debug capture flows where active wave masks and scalar state are inspected; incorrect offsets would show implausible execution masks, mismatched PC/status correlation, or unusable trap temporary values.
- Check kernel logs for warnings around wave selection, especially the `simd != 0` warning in the GC 12.1 wave data path, because incorrect selection can make otherwise correct indices appear broken.

## Cross-Chunk Notes

This is the final chunk of `gc_12_1_0_offset.h`. The final per-file research document should combine it with earlier chunks that define the rest of the GC 12.1.0 offset namespace, especially the immediately preceding `gfx_se_sqind` lines containing `ixSQ_WAVE_TTMP0`-`TTMP7`, `ixSQ_WAVE_PC_LO/HI`, wave status, allocation, trap, exception, and scheduling offsets.
