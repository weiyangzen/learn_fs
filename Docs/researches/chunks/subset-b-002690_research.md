# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_3_sh_mask.h lines 11974-14503

## Purpose

This chunk is a generated register-field mask slice for AMD GC 9.4.3. It exports C preprocessor constants for bit shifts and masks used to compose and decode 32-bit graphics-core register values. The range starts in the tail of `TCC_CTRL2`, covers TCC/TCA/TCX cache fabric diagnostic, soft-reset, writeback-invalidate, and ECC/error-status fields, then enters `addressBlock: xcd0_gc_shdec` for shader and compute state registers, and ends in `addressBlock: xcd0_gc_cppdec` with command processor ring, doorbell, interrupt, ECC, power, and debug masks through `CP_ME1_PIPE0_INT_CNTL`.

The file is declarative. It contains no executable code, but its macro names and numeric values are part of the AMDGPU hardware binding for GC 9.4.3. Including code combines these masks with companion register-offset headers and register helper macros to program shader stages, compute dispatches, command processor rings, KIQ/HQD queues, interrupts, and error reporting.

## Major Register Areas Covered

The initial TCC/TCA/TCX section describes lower-level cache and transaction fabric fields. `TCC_DSM_CNTL`, `TCC_DSM_CNTLA`, `TCC_DSM_CNTL2`, `TCC_DSM_CNTL2A`, `TCC_DSM_CNTL2B`, and `TCC_DSM_CNTL3` expose DSM irritator and error-injection fields for cache data banks, dirty banks, tag arrays, source/atomic/write-return FIFOs, latency FIFOs, return paths, output FIFOs, and write-early-return behavior. `TCC_WBINVL2` exposes a `DONE` status bit, while `TCC_SOFT_RESET` exposes `HALT_FOR_RESET`. `TCA_CTRL`, `TCA_BURST_MASK`, `TCA_BURST_CTRL`, `TCA_DSM_CNTL`, `TCA_DSM_CNTL2`, `TCX_CTRL`, `TCX_DSM_CNTL`, and `TCX_DSM_CNTL2` cover fabric arbitration, fine-grained clock-gating disables, burst controls, and SED/error-injection controls. `TCA_*_ERR_STATUS_*`, `TCX_*_ERR_STATUS_*`, and `TCC_*_ERR_STATUS_*` provide corrected and uncorrected error status fields, including validity bits, address, memory ID, ECC/parity indicators, error info, CE/UE counters, FED counters, and poison status.

The `xcd0_gc_shdec` section defines shader-program state for graphics stages. It covers PS, VS, GS, ES, HS, and LS program base registers, resource registers, late allocation, user data, and cross-stage details such as `SPI_SHADER_PGM_RSRC*_PS`, `SPI_SHADER_PGM_RSRC*_VS`, `SPI_SHADER_PGM_RSRC*_GS`, `SPI_SHADER_PGM_RSRC*_HS`, `SPI_SHADER_PGM_RSRC2_GS_VS`, `SPI_SHADER_PGM_RSRC4_GS`, and the `SPI_SHADER_USER_DATA_*` families. Important fields include shader program base low/high words, VGPR/SGPR counts, priority, float mode, private/debug/IEEE flags, scratch enable, user SGPR count and MSB, exception enables, trap-present flags, LDS sizing, stream-out enables, CU masks, wave limits, SIMD disable masks, and 32 full-width user-data registers per stage or common bank.

The compute portion of `xcd0_gc_shdec` defines dispatch packet and resource fields. `COMPUTE_DISPATCH_INITIATOR` controls shader enable, partial threadgroups, ordered append, thread-dimension mode, cache invalidation hints, and restore behavior. Dimension, start, restart, and thread-count registers define grid geometry and full/partial thread counts. `COMPUTE_PGM_LO/HI`, `COMPUTE_DISPATCH_PKT_ADDR_*`, `COMPUTE_DISPATCH_SCRATCH_BASE_*`, `COMPUTE_PGM_RSRC1`, `COMPUTE_PGM_RSRC2`, `COMPUTE_PGM_RSRC3`, `COMPUTE_RESOURCE_LIMITS`, static thread management by SE, temporary ring size, VMID, relaunch, wave restore address, thread trace, dispatch ID, threadgroup ID, checksum, and `COMPUTE_USER_DATA_0..15` describe the hardware state needed to launch and resume compute workloads.

The `xcd0_gc_cppdec` section starts command processor control and diagnostics. It includes defer/write data command registers (`CP_DFY_*`), EOP wait time, CPC MGCG sync, interrupt info/address/PASID, virtualization status, `CP_GFX_ERROR`, UTCL1 control/error fields for CPG/CPC/CPF, AQL SMM status, graphics ring-buffer base/control/read-pointer/write-pointer fields, write-pointer polling address fields, privilege mode, global and per-ring CP interrupt enable/status registers, CP device/priority/fatal-error/VMID registers, doorbell control/range registers, active bits, ME/PFP/CE/MEC F32 interrupt summaries, CP power and memory-sleep controls, ECC first-occurrence registers, `GB_EDC_MODE`, CP/CPF/CPC debug controls, CP priority-queue write-pointer polling controls, and `CP_ME1_PIPE0_INT_CNTL`.

## Important APIs, Types, and Functions

There are no functions, types, structs, or enums in this chunk. The exported interface is the macro namespace:

- `REGISTER__FIELD__SHIFT` gives the field's least-significant bit position.
- `REGISTER__FIELD_MASK` gives the field's 32-bit mask.
- Register comments and `addressBlock` comments preserve generated grouping metadata for readers and downstream tooling.

The main consumers are AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_RLC`, `RREG32_XCC`, `WREG32_XCC`, and `WREG32_FIELD15_PREREG`. For GC 9.4.3 specifically, representative integration appears in `amdgpu/gfx_v9_4_3.c`: `CP_INT_CNTL_RING0` fields are set when enabling GUI idle interrupts, `CP_PQ_WPTR_POLL_CNTL.EN` is disabled during KIQ/HQD setup, and `CP_ME1_PIPE0_INT_CNTL.TIME_STAMP_INT_ENABLE` is toggled in MEC interrupt setup. `amdgpu/amdgpu_amdkfd_gc_9_4_3.c` writes `CP_PQ_WPTR_POLL_CNTL1` with a queue mask when restoring KFD queue write-pointer polling.

## Control Flow

This header has no runtime control flow. Its effective flow is compile-time constant expansion:

1. A GC 9.4.3 AMDGPU source file includes generated register offset and mask headers.
2. The code selects a register and field by ASIC generation, XCC instance, shader stage, ring, pipe, or queue.
3. Helper macros combine the `SHIFT` and `MASK` definitions with a field value.
4. The resulting 32-bit value is written to MMIO or read back and decoded by the including driver code.

The hardware flows implied by the masks are substantial. Shader/compute setup programs resource registers, user data, program base addresses, VMIDs, thread geometry, scratch bases, and dispatch initiators before a graphics draw or compute dispatch can execute. Command processor setup writes ring-buffer bases, ring sizes, read-pointer report addresses, write-pointer registers, doorbell offsets and ranges, queue masks, and interrupt enables. Error-handling flows read status and first-occurrence fields to decode ECC, UTCL1, fatal, privilege, opcode, timestamp, and reserved-bit events.

## State and Persistence Behavior

The header stores no state. The state described by the macros lives in GPU registers and persists according to hardware power/reset behavior and driver sequencing:

- TCC/TCA/TCX fields can affect cache/fabric diagnostics, error injection, clock-gating overrides, writeback invalidation, soft reset, ECC/SED status, and corrected/uncorrected error counters.
- Shader and compute fields hold per-dispatch or per-pipeline executable state such as program addresses, resource usage, wave/CU limits, user SGPR payloads, scratch pointers, LDS allocation, exception/trap bits, thread geometry, VMID, and relaunch/restore metadata.
- CP fields hold ring and queue control state, read/write pointers, doorbell ranges, VMID assignment, interrupt enables/status, error-first-occurrence data, debug overrides, power/memory-sleep gating controls, and write-pointer polling configuration.

The chunk does not encode access type, reset values, read-clear behavior, write-one-to-clear behavior, locking, sequencing requirements, or XCC broadcast rules. Those are enforced by the caller, firmware, hardware documentation, and the AMDGPU/KFD lifecycle around GPU reset, suspend/resume, queue eviction/restore, and per-XCC initialization.

## Dependencies and Integration Points

This generated header depends only on the C preprocessor. In practice it must stay synchronized with adjacent generated GC 9.4.3 headers that define register offsets and base indices, especially `gc_9_4_3_offset.h`-style files and SOC15 register-base metadata.

Important integration points include:

- `amdgpu/gfx_v9_4_3.c` graphics IP initialization and ring/KIQ setup, which use CP ring, polling, interrupt, and per-XCC register access helpers.
- `amdgpu/amdgpu_amdkfd_gc_9_4_3.c` KFD queue restore paths, which write `CP_PQ_WPTR_POLL_CNTL1` and related HQD registers for user-mode compute queues.
- Shader and command processor packet setup paths that program `SPI_SHADER_*` and `COMPUTE_*` registers through PM4 or direct register programming.
- Interrupt handling and enable paths for global CP interrupts, per-ring interrupts, ME/PFP/CE/MEC F32 summaries, timestamp interrupts, ECC errors, GPF/SUA violations, opcode errors, and reserved-bit errors.
- RAS and diagnostics paths that decode TCC/TCA/TCX CE/UE status, CP ECC first occurrence, UTCL1 errors, `CP_GFX_ERROR`, `CP_FATAL_ERROR`, and CP debug state.
- Multi-XCC GC 9.4.3 paths that select `GET_INST(GC, xcc_id)` and must pair these masks with the correct instance-specific register offset.

## Risks and Edge Cases

The primary risk is silent hardware misprogramming if a mask or shift drifts from the GC 9.4.3 register database. A wrong bit in this chunk can corrupt shader resource programming, compute dispatch geometry, CP ring pointer handling, doorbell routing, interrupt enables, or ECC/error decoding without producing a compile failure.

Repeated register families are a notable review hazard. The chunk contains many near-identical PS/VS/GS/HS/LS user-data registers, per-SE static thread-management registers, per-ring CP interrupt registers, and TCC/TCA/TCX error-status layouts. Copy-generation mistakes can be hard to spot because the structure looks intentionally repetitive.

Several masks expose full 32-bit data fields such as shader user data, program base low words, dispatch IDs, restart coordinates, ring write pointers, and obsolete ECC first-occurrence ring registers. Callers must use the correct fixed-width types and avoid assuming signed semantics from the `L` suffix on constants like `0xFFFFFFFFL`.

Some fields are control bits with side effects, while others are sticky status, counters, address captures, first-occurrence records, or debug-only overrides. The header does not distinguish safe read/write behavior. In particular, error-injection controls, soft reset, writeback invalidation, doorbell enable/hit, fatal-error, debug, and interrupt status fields require external sequencing and hardware-specific clearing rules.

The chunk starts mid-register at the mask tail of `TCC_CTRL2` and ends after `CP_ME1_PIPE0_INT_CNTL`; surrounding chunks are needed for the complete generated header context. A per-file report should avoid treating this range as a complete register map for GC 9.4.3.

## Test Signals

Useful validation signals are mostly build-time, static, and hardware-integration oriented:

- Kernel builds that include GC 9.4.3 AMDGPU and KFD paths should compile without missing or renamed macro errors.
- Static comparison against AMD's authoritative generated register database should verify every `SHIFT`/`MASK` pair, repeated family, and address-block boundary.
- Register helper tests or build-time assertions can check representative field round trips for `SPI_SHADER_PGM_RSRC*`, `COMPUTE_PGM_RSRC*`, `CP_INT_CNTL_RING0`, `CP_ME1_PIPE0_INT_CNTL`, `CP_PQ_WPTR_POLL_CNTL`, and TCC/TCA/TCX error status masks.
- GC 9.4.3 hardware testing should exercise graphics shader launch, compute dispatch, KIQ/HQD queue setup, queue eviction/restore, write-pointer polling, doorbell delivery, and per-XCC ring initialization.
- Interrupt tests should confirm CP busy/empty/idle, timestamp, ECC, GPF, SUA, opcode, privilege, and reserved-bit interrupt enables and statuses map to the expected handler paths.
- RAS and fault-injection testing should validate TCC/TCA/TCX CE/UE decode, CP ECC first-occurrence decode, UTCL1 error handling, fatal-error paths, and debug/status reporting under controlled errors.
