# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h lines 9968-10002

## Scope

This chunk is the tail of the generated AMD GC 11.5.0 register-offset header. It contains C preprocessor constants only: no functions, structs, enums, storage, includes, locking, or runtime branches are introduced in this range. The selected lines define the last `sqind` indexed shader-queue wave register offsets and then close the `_gc_11_5_0_OFFSET_HEADER` include guard.

The exact chunk starts after the first basic SQ wave state registers were already introduced by the previous chunk. Lines 9968-10002 cover instruction-buffer status, program counter, scratch base, wave hardware identity, scheduler mode, shader cycle count, temporary trap registers, scalar `M0`, and execution-mask offsets:

- `ixSQ_WAVE_IB_STS`, `ixSQ_WAVE_IB_STS2`, and `ixSQ_WAVE_IB_DBG1`.
- `ixSQ_WAVE_PC_LO` and `ixSQ_WAVE_PC_HI`.
- `ixSQ_WAVE_FLUSH_IB`.
- `ixSQ_WAVE_FLAT_SCRATCH_LO` and `ixSQ_WAVE_FLAT_SCRATCH_HI`.
- `ixSQ_WAVE_HW_ID1`, `ixSQ_WAVE_HW_ID2`, `ixSQ_WAVE_POPS_PACKER`, `ixSQ_WAVE_SCHED_MODE`, and `ixSQ_WAVE_SHADER_CYCLES`.
- `ixSQ_WAVE_TTMP0` through `ixSQ_WAVE_TTMP15`.
- `ixSQ_WAVE_M0`, `ixSQ_WAVE_EXEC_LO`, and `ixSQ_WAVE_EXEC_HI`.

Although this repository is under a `ceph-client` source tree, this file is AMDGPU DRM hardware metadata for the GC 11.5.0 graphics IP block, not filesystem implementation code.

## Purpose

`gc_11_5_0_offset.h` maps generated register names to numeric offsets for the GC 11.5.0 ASIC family. The `ix...` names in this chunk are not normal memory-mapped register addresses by themselves. They are indexes into the shader queue indexed-register path, selected through the companion `regSQ_IND_INDEX`/`regSQ_IND_DATA` MMIO window defined earlier in the same offset header.

The driver uses this kind of register metadata to avoid embedding raw hardware indices in engine code. For SQ wave inspection, the runtime flow is to write `regSQ_IND_INDEX` with a wave selector and one of these `ixSQ_WAVE_*` index values, then read `regSQ_IND_DATA` to snapshot the selected wave register. The matching field layout for `SQ_IND_INDEX` lives in `gc_11_5_0_sh_mask.h`, where `SQ_IND_INDEX__WAVE_ID`, `SQ_IND_INDEX__WORKITEM_ID`, `SQ_IND_INDEX__AUTO_INCR`, and `SQ_IND_INDEX__INDEX` describe how the index register is packed.

This tail section is primarily diagnostic and context-inspection metadata. It supports wave dump paths, hang analysis, shader debugging, KFD/compute fault triage, and low-level validation of live wave execution state. It is not queue creation logic and does not directly program draw or dispatch commands.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The public interface is the macro naming contract:

- `ixSQ_WAVE_IB_STS` (`0x0107`) selects the wave instruction-buffer status register.
- `ixSQ_WAVE_PC_LO` (`0x0108`) and `ixSQ_WAVE_PC_HI` (`0x0109`) select the low and high halves of the wave program counter.
- `ixSQ_WAVE_IB_DBG1` (`0x010d`) selects additional instruction-buffer debug state.
- `ixSQ_WAVE_FLUSH_IB` (`0x010e`) selects an indexed control/status register related to flushing the wave instruction buffer.
- `ixSQ_WAVE_FLAT_SCRATCH_LO` (`0x0114`) and `ixSQ_WAVE_FLAT_SCRATCH_HI` (`0x0115`) select the wave flat-scratch base address halves.
- `ixSQ_WAVE_HW_ID1` (`0x0117`) and `ixSQ_WAVE_HW_ID2` (`0x0118`) select hardware identity information for the wave.
- `ixSQ_WAVE_POPS_PACKER` (`0x0119`) selects POPS packer state.
- `ixSQ_WAVE_SCHED_MODE` (`0x011a`) selects scheduling-mode state.
- `ixSQ_WAVE_IB_STS2` (`0x011c`) selects a second instruction-buffer status register.
- `ixSQ_WAVE_SHADER_CYCLES` (`0x011d`) selects the wave shader-cycle counter/state.
- `ixSQ_WAVE_TTMP0` through `ixSQ_WAVE_TTMP15` (`0x026c` through `0x027b`) select the wave temporary trap registers.
- `ixSQ_WAVE_M0` (`0x027d`) selects the scalar `M0` register.
- `ixSQ_WAVE_EXEC_LO` (`0x027e`) and `ixSQ_WAVE_EXEC_HI` (`0x027f`) select the low and high halves of the wave execution mask.

The main integration macros outside this chunk are:

- `regSQ_IND_INDEX` and `regSQ_IND_DATA` from the same offset header. These provide the indexed access aperture used to read the `ixSQ_WAVE_*` entries.
- `SQ_IND_INDEX__*` field masks and shifts from `gc_11_5_0_sh_mask.h`. These define how callers place the wave ID, work-item/thread ID, auto-increment bit, and target index into `regSQ_IND_INDEX`.
- `WREG32_SOC15`, `RREG32_SOC15`, `SOC15_REG_OFFSET`, and related AMDGPU register helpers. These perform the actual MMIO access after the generated constants are selected.

Representative consumers in the broader AMDGPU tree include the GC v11 and GC v12 wave snapshot helpers. In `gfx_v11_0_read_wave_data()`, the driver reads `ixSQ_WAVE_STATUS`, `ixSQ_WAVE_PC_LO`, `ixSQ_WAVE_PC_HI`, `ixSQ_WAVE_EXEC_LO`, `ixSQ_WAVE_EXEC_HI`, `ixSQ_WAVE_HW_ID1`, `ixSQ_WAVE_HW_ID2`, `ixSQ_WAVE_GPR_ALLOC`, `ixSQ_WAVE_LDS_ALLOC`, `ixSQ_WAVE_TRAPSTS`, `ixSQ_WAVE_IB_STS`, `ixSQ_WAVE_IB_STS2`, `ixSQ_WAVE_IB_DBG1`, `ixSQ_WAVE_M0`, and `ixSQ_WAVE_MODE` through the indexed SQ path. Several of the offsets used by that flow are defined in this chunk.

## Control Flow

This header has no runtime control flow. The only direct behavior is compile-time macro substitution.

The implied runtime control flow for these constants is:

1. AMDGPU selects the GC 11.5.0 generated register headers for a matching ASIC family.
2. A debug, hang-dump, wave-inspection, or compute diagnostics path selects a shader engine/shader array/SIMD/wave context using higher-level GPU selection helpers.
3. The path writes `regSQ_IND_INDEX` with `wave << SQ_IND_INDEX__WAVE_ID__SHIFT` and `index << SQ_IND_INDEX__INDEX__SHIFT`; register-read helpers may also set work-item/thread and auto-increment fields when reading SGPR/VGPR ranges.
4. The path reads `regSQ_IND_DATA`, which returns the contents of the selected wave indexed register.
5. The collected values are copied into a wave dump buffer or decoded by higher-level debug tooling.

For the specific macros in this chunk, the common ordering in diagnostic dumps is to read PC and execution-mask values alongside wave status and hardware ID, then read allocation, trap, instruction-buffer, and mode registers. This chunk contributes the PC, EXEC, IB status/debug, M0, hardware ID, and scheduler-mode pieces of that snapshot.

The header does not define wave selection, shader-engine selection, register-read barriers, polling, retry behavior, or the lifetime of the returned data. Those details live in AMDGPU engine code and in the hardware programming model.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They name hardware-owned indexed registers whose values are live wave state.

The values selected by this chunk are volatile. `PC_LO`/`PC_HI`, `EXEC_LO`/`EXEC_HI`, `M0`, `IB_STS`, `IB_STS2`, `IB_DBG1`, `SCHED_MODE`, and `SHADER_CYCLES` can change while a wave is executing. A snapshot collected without halting or otherwise stabilizing the target wave is best treated as a point-in-time diagnostic view, not a persistent software-owned record.

Some registers represent architecturally meaningful execution state. The program counter identifies where the wave is executing. `EXEC_LO` and `EXEC_HI` identify active lanes. `M0` is used by shader instructions for addressing and control behavior. `TTMP0..TTMP15` are trap-handler temporary registers and may contain context save/restore, exception, or trap handling state. `FLAT_SCRATCH_LO/HI` participates in per-wave flat scratch addressing. Incorrect offsets for these registers can make a debug dump point at the wrong instruction, wrong lanes, or wrong trap state.

Other registers are diagnostic or scheduling observability state. `HW_ID1/HW_ID2` identify where the wave resides in the hardware, `SCHED_MODE` reports scheduling mode, `SHADER_CYCLES` exposes cycle/accounting state, and the instruction-buffer status/debug registers expose fetch/decode-side state. These are especially useful during GPU hang analysis but are not persistent driver configuration.

The `ixSQ_WAVE_FLUSH_IB` name suggests a control/status register with a side-effect-oriented purpose. This chunk only supplies the index value and does not document whether reads are passive or writes are allowed. Any caller writing indexed SQ registers must rely on the hardware guide and established engine code, not on the offset header alone.

## Dependencies And Integration Points

This chunk depends on the generated GC 11.5.0 register family remaining synchronized:

- `gc_11_5_0_offset.h` earlier lines define `regSQ_IND_INDEX`, `regSQ_IND_DATA`, and the surrounding GC register offsets used to access these indexed values.
- `gc_11_5_0_sh_mask.h` defines the shift/mask layout for the indexed access register and for any non-indexed GC registers that surround the wave-debug flow.
- `gfx_v11_0.c` is the closest generation-level consumer pattern for GC 11.x wave dumps. It calls a local `wave_read_ind()` helper that writes `regSQ_IND_INDEX` and reads `regSQ_IND_DATA` for `ixSQ_WAVE_*` offsets.
- GFX hang detection, GPU reset diagnostics, debugfs register dumping, KFD compute debugging, and user-space tools that consume AMDGPU wave dumps rely on these index constants being generation-correct.
- The same logical register names appear across older and newer generated headers, but the numeric index values can vary by architecture generation. Code must include the header for the active IP version rather than assuming cross-generation constants are interchangeable.

The integration boundary is intentionally narrow: this header publishes numeric constants; engine code decides when it is safe to sample a wave, how to select the target shader instance, how large the output record is, and how to interpret the returned bits.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong `ixSQ_WAVE_*` value compiles cleanly but causes diagnostics to read the wrong indexed register.
- This chunk starts mid-`sqind` family. `ixSQ_WAVE_STATUS`, `ixSQ_WAVE_TRAPSTS`, `ixSQ_WAVE_GPR_ALLOC`, and `ixSQ_WAVE_LDS_ALLOC` are in the previous chunk, while this chunk covers the remaining values. File-level documentation must merge both chunks to describe a complete wave snapshot map.
- Wave state is volatile. Reading PC, EXEC, M0, scheduler, and instruction-buffer registers from a running wave can produce internally inconsistent snapshots unless the consumer uses a hardware-supported halt, trap, or debug sequence.
- Split registers must be paired correctly. `PC_LO/PC_HI`, `EXEC_LO/EXEC_HI`, and `FLAT_SCRATCH_LO/HI` are separate indices; a stale high half or mismatched low half can misrepresent addresses or lane masks.
- `TTMP0..TTMP15` are contiguous in this chunk. Off-by-one errors are easy because they are a dense sequence from `0x026c` to `0x027b`; a single bad value shifts every temporary register after it.
- The `regSQ_IND_INDEX` packing layout is separate from these index constants. If a caller shifts the index with the wrong generation's `SQ_IND_INDEX__INDEX__SHIFT`, the correct `ixSQ_WAVE_*` macro will still address the wrong hardware location.
- Some entries may be read-only, write-only, side-effecting, or debug-gated by hardware state. The offset header does not encode access permissions or sequencing.
- `ixSQ_WAVE_FLUSH_IB` is particularly sensitive because the name describes a flush action. Treating every `ixSQ_WAVE_*` constant as safe to write or safe to poll would be a bug.
- Cross-generation copy/paste is risky. GC v11, GC v12, and earlier GCA headers share names such as `ixSQ_WAVE_PC_LO` and `ixSQ_WAVE_EXEC_LO`, but consumers must not assume identical numeric offsets without generated-register verification.
- Because this is the final chunk of the file, a missing `#endif` or accidental edit near the guard terminator would break all compilation units that include this generated header.

## Test Signals

Useful validation is mostly generated-data consistency plus runtime diagnostic behavior:

- Build AMDGPU configurations that include GC 11.5.0 register headers and GFX v11 paths. Compilation catches missing or renamed macros such as `ixSQ_WAVE_PC_LO`, `ixSQ_WAVE_EXEC_LO`, `ixSQ_WAVE_HW_ID1`, and `ixSQ_WAVE_IB_STS`.
- Mechanically compare this tail of `gc_11_5_0_offset.h` against AMD's authoritative GC 11.5.0 register database, especially the dense `TTMP0..TTMP15` sequence and the `PC`, `EXEC`, `M0`, `IB_STS`, and `HW_ID` values used in wave dumps.
- Cross-check `regSQ_IND_INDEX`/`regSQ_IND_DATA` offsets and `SQ_IND_INDEX__*` masks in the matching `gc_11_5_0_sh_mask.h` to ensure the indexed access path and index values are from the same generated register set.
- Exercise GPU hang or debug-dump collection on GC 11.5.0 hardware and verify that wave records contain plausible PC values, lane masks, hardware IDs, allocation state, instruction-buffer state, and `M0` values.
- Run compute workloads that intentionally trap, fault, or hang, then confirm `TTMP`, `IB_STS`, `IB_STS2`, `IB_DBG1`, `EXEC`, and PC snapshots align with expected trap-handler/debug behavior.
- Validate split-register consistency in debug tooling: PC high/low and EXEC high/low should be decoded as paired values, not independent unrelated fields.
- Check that indexed SGPR/VGPR read helpers still use the correct `SQ_IND_INDEX__AUTO_INCR` and work-item fields when adjacent wave state reads are added or refactored.
- Runtime warning signals include impossible wave IDs or hardware IDs, all-zero or all-ones PCs for active waves, mismatched EXEC masks, trap temporaries that do not line up with a known trap path, wave dumps changing layout unexpectedly, or hang reports that lose instruction-buffer status fields.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002548`. It covers lines 9968-10002 of `gc_11_5_0_offset.h`, the final tail of the file. The previous chunk contains the opening `sqind` entries, including `ixSQ_DEBUG_STS_LOCAL`, `ixSQ_DEBUG_CTRL_LOCAL`, `ixSQ_WAVE_ACTIVE`, `ixSQ_WAVE_VALID_AND_IDLE`, `ixSQ_WAVE_MODE`, `ixSQ_WAVE_STATUS`, `ixSQ_WAVE_TRAPSTS`, `ixSQ_WAVE_GPR_ALLOC`, and `ixSQ_WAVE_LDS_ALLOC`. The final per-file research should merge those entries with this chunk to present the complete GC 11.5.0 indexed SQ wave register map.
