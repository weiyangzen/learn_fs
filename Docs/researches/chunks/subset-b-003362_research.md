# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma/sdma_4_4_0_offset.h lines 4849-5224

## Purpose

This chunk is the final slice of the generated AMD SDMA 4.4.0 register-offset header. It is not executable driver logic; it exports preprocessor constants that name SDMA4 RLC context queue registers and their register-base indices.

The covered range finishes the `regSDMA4_RLC3_MIDCMD_*` block, then defines complete `regSDMA4_RLC4_*`, `regSDMA4_RLC5_*`, `regSDMA4_RLC6_*`, and `regSDMA4_RLC7_*` register blocks. The file ends with the `#endif` for `_sdma_4_4_0_OFFSET_HEADER`, so this is the tail of the source file.

## Public Surface

The exported interface is macro-only:

- `regSDMA4_RLC*_...` macros map symbolic register names to 32-bit register offsets for SDMA instance 4.
- `regSDMA4_RLC*_..._BASE_IDX` macros map each register to base index `0`.

There are no functions, structs, enums, inline helpers, state variables, or side-effecting code in this chunk. Consumers include this header and pass the offset constants into AMDGPU/SOC15 register access helpers, or use them as generated ABI data for register dumps and tooling.

## Register Families Covered

The first lines complete RLC3 mid-command snapshot registers: `MIDCMD_DATA1` through `MIDCMD_DATA10` and `MIDCMD_CNTL`. Adjacent previous lines define `MIDCMD_DATA0`, so merge-time documentation should treat RLC3 as a partial block in this chunk.

Each complete RLC4-RLC7 block follows the same layout:

- Ring-buffer setup and pointer registers: `RB_CNTL`, `RB_BASE`, `RB_BASE_HI`, `RB_RPTR`, `RB_RPTR_HI`, `RB_WPTR`, `RB_WPTR_HI`.
- Write-pointer polling and read-pointer writeback registers: `RB_WPTR_POLL_CNTL`, `RB_RPTR_ADDR_HI`, `RB_RPTR_ADDR_LO`, `RB_WPTR_POLL_ADDR_HI`, `RB_WPTR_POLL_ADDR_LO`.
- Indirect-buffer registers: `IB_CNTL`, `IB_RPTR`, `IB_OFFSET`, `IB_BASE_LO`, `IB_BASE_HI`, `IB_SIZE`, and `IB_SUB_REMAIN`.
- Scheduling/context state registers: `SKIP_CNTL`, `CONTEXT_STATUS`, `PREEMPT`, `MINOR_PTR_UPDATE`, and `DUMMY_REG`.
- Doorbell and queue status registers: `DOORBELL`, `STATUS`, `DOORBELL_LOG`, `WATERMARK`, and `DOORBELL_OFFSET`.
- Context-save area registers: `CSA_ADDR_LO` and `CSA_ADDR_HI`.
- AQL and mid-command capture registers: `RB_AQL_CNTL`, `MIDCMD_DATA0` through `MIDCMD_DATA10`, and `MIDCMD_CNTL`.

The offsets are regular and context-strided. RLC4 begins at `0x1d830`, RLC5 at `0x1d888`, RLC6 at `0x1d8e0`, and RLC7 at `0x1d938`, with the same internal gaps before status and mid-command regions. This regularity matters because generated-header consumers often assume same-generation register groups have a stable shape across RLC contexts and SDMA instances.

## Important APIs, Types, And Functions

This chunk itself defines no C API beyond macros. Its important integration API is the AMDGPU register-access convention:

- `amdgpu/sdma_v4_4.c` includes both `sdma/sdma_4_4_0_offset.h` and `sdma/sdma_4_4_0_sh_mask.h`.
- `sdma_v4_4_get_reg_offset()` computes an absolute register address for SDMA instances 0-4 from the SDMA0 base plus instance deltas. The hard-coded SDMA4 instance delta is `0x1d5a0`.
- SOC15-style helpers and macros such as `SOC15_REG_ENTRY`, `SOC15_REG_FIELD`, `RREG32`, `WREG32`, `RREG32_SOC15`, `WREG32_SOC15`, and field helpers combine an offset macro from this file with bit definitions from `sdma_4_4_0_sh_mask.h`.

The matching shift/mask header provides semantic fields for these offsets. For example, the RLC ring-buffer control registers carry enable, size, swap, read-pointer writeback, privilege, and VMID fields; indirect-buffer control carries enable, swap, in-IB switching, and command VMID fields; context status exposes selected, idle, expired, exception, context-switch, preempted, and preempt-disable state; doorbell registers expose enable/captured status; and mid-command control exposes data-valid, copy-mode, split-state, and allow-preempt bits.

## Control Flow

There is no runtime control flow in the header. The effective flow in driver code is compile-time substitution followed by hardware MMIO access:

1. An SDMA 4.4 translation unit includes this offset header and the matching shift/mask header.
2. Driver code selects a register macro for an SDMA instance/context queue, or computes the equivalent instance address from the SDMA0 register layout.
3. The AMDGPU register helper resolves the SOC15 block base and per-instance offset.
4. The driver reads or writes the hardware register, using shift/mask macros for bit fields when needed.
5. Hardware consumes the programmed queue base, pointer, doorbell, polling, context, AQL, preemption, or mid-command state.

For this specific chunk, the control surface is queue/context management for SDMA4 RLC queues 3-7 rather than the global SDMA engine control path.

## State And Persistence Behavior

The header persists no software state. All state represented by these macros lives in SDMA hardware registers or in memory regions pointed to by those registers.

Ring-buffer registers persist queue configuration until reset or reprogramming: base addresses, high address bits, read/write pointers, write-pointer polling configuration, and read-pointer writeback addresses. Indirect-buffer registers persist IB execution state such as base, offset, read pointer, and size. Doorbell registers persist enable/offset state and capture doorbell activity. Context and preemption registers expose scheduler-visible state for queue selection, idleness, exceptions, context-switch readiness, preemption, and context-save area location. `MIDCMD_DATA*` and `MIDCMD_CNTL` hold hardware mid-command snapshot or resume state, used when preemption or context switching interrupts a command stream.

Several registers represent live or hardware-owned state rather than simple configuration. `STATUS`, `DOORBELL_LOG`, `WATERMARK`, `CONTEXT_STATUS`, `IB_SUB_REMAIN`, and `MIDCMD_*` values can change as the engine executes work. The macros do not encode read-only, write-one-to-clear, reset, ordering, or synchronization rules; callers must rely on SDMA hardware documentation and the surrounding AMDGPU queue-management code.

## Dependencies And Integration Points

The direct generated-header dependency is `sdma_4_4_0_sh_mask.h`, which supplies the bit layout for the register names defined here. The broader AMDGPU dependency is the SOC15 register-access layer and the SDMA 4.4 implementation in `amdgpu/sdma_v4_4.c`.

The register families integrate with:

- AMDGPU SDMA queue setup and teardown, where ring-buffer bases, pointer registers, polling addresses, and doorbells are configured.
- GPU scheduler and context-switch/preemption flows, where `CONTEXT_STATUS`, `PREEMPT`, `CSA_ADDR_*`, `IB_SUB_REMAIN`, and `MIDCMD_*` registers are relevant.
- Doorbell infrastructure, where user or kernel queues notify hardware through doorbell offsets and logs.
- VMID and privilege handling via ring-buffer and indirect-buffer control fields in the matching shift/mask header.
- AQL/HSA-style queue operation through `RB_AQL_CNTL`.
- Register dumps, diagnostics, RAS/debug flows, and generated tooling that need symbolic names for SDMA4 RLC queue registers even if handwritten driver code tends to use SDMA0-style offsets plus instance deltas.

## Risks And Maintenance Notes

- The file is generated and repetitive. A single wrong offset can point queue setup, preemption state, or diagnostics at the wrong hardware register without a C compiler warning.
- This chunk starts mid-RLC3. Merge/reconciliation must include the previous chunk to capture `regSDMA4_RLC3_MIDCMD_DATA0` and the earlier RLC3 queue registers.
- RLC4-RLC7 blocks are structurally identical but not interchangeable. Copying a register name or offset across RLC indices can target a different queue context.
- These are SDMA4-specific offsets. `sdma_v4_4.c` also computes SDMA instance addresses from SDMA0 offsets and instance deltas; generated SDMA4 offsets must remain consistent with that calculation.
- All `_BASE_IDX` values in this chunk are `0`. If a future generation changes base indexing, using these names with the wrong generation's SOC15 metadata would misaddress registers.
- Ring-buffer, IB, doorbell, and polling registers touch GPU-visible memory addresses. Bad offset use can cause the engine to read or write the wrong queue memory, stale pointer writeback area, or doorbell slot.
- Context-save, preemption, and mid-command registers are sensitive to scheduler timing. Reading or writing them outside the expected quiescent/preemption flow can race active hardware.
- Full-width data/address registers rely on 32-bit unsigned MMIO paths. Signed constants or truncating address composition would be unsafe for `*_BASE_HI`, `*_ADDR_HI`, and `MIDCMD_DATA*` registers.
- The final `#endif` is part of this chunk. Any generated-file edit that drops or duplicates it will break the whole include guard.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage for `amdgpu/sdma_v4_4.c` with `sdma_4_4_0_offset.h` and `sdma_4_4_0_sh_mask.h` included together.
- Generated-header consistency checks that every `regSDMA4_RLC4` through `regSDMA4_RLC7` offset has a matching `_BASE_IDX` and matching field definitions in `sdma_4_4_0_sh_mask.h`.
- Cross-instance checks that SDMA4 offsets match SDMA0 offsets plus the `SDMA4_REG_OFFSET` delta used by `sdma_v4_4_get_reg_offset()`.
- Static checks for complete RLC4-RLC7 register sequences: RB, IB, context/status, doorbell, CSA, polling, AQL, minor pointer update, and `MIDCMD_DATA0` through `MIDCMD_DATA10` plus `MIDCMD_CNTL`.
- Register-dump validation on SDMA 4.4 hardware that symbolic SDMA4 RLC4-RLC7 addresses decode to the same values reached through the driver's instance-offset calculation.
- Runtime SDMA queue tests that submit work on contexts using ring-buffer, indirect-buffer, doorbell, and write-pointer polling paths, then verify pointer writeback and queue idleness.
- Preemption/context-switch tests that force SDMA IB preemption and verify `CONTEXT_STATUS`, `IB_SUB_REMAIN`, `CSA_ADDR_*`, and `MIDCMD_*` state is coherent before and after resume.
- Negative diagnostics for doorbell misrouting: doorbell logs and queue write pointers should change only for the intended RLC context.
