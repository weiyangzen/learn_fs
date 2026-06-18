# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma/sdma_4_4_0_sh_mask.h lines 7808-10409

## Purpose

This chunk is part of AMD's generated `sdma_4_4_0_sh_mask.h` register-field header for the SDMA 4.4.0 block. It does not implement runtime logic; it defines `__SHIFT` and `_MASK` constants used by the AMDGPU driver to pack, unpack, and test SDMA MMIO register fields without hard-coding bit positions in C code.

The covered range starts inside the `SDMA2_RLC5_RB_CNTL` field set, then covers the rest of `SDMA2_RLC5`, all of `SDMA2_RLC6` and `SDMA2_RLC7`, the `addressBlock: sdma0_sdma3dec` public register block for `SDMA3`, the full `SDMA3_GFX` and `SDMA3_PAGE` queue register groups, the full `SDMA3_RLC0` through `SDMA3_RLC3` compute queue groups, and the beginning of `SDMA3_RLC4` through `SDMA3_RLC4_RB_WPTR_POLL_CNTL`.

## Important APIs, Types, and Macro Families

There are no functions, structs, enums, or storage definitions in this chunk. The important public surface is the preprocessor macro naming contract:

- `REGISTER__FIELD__SHIFT` gives the field's bit offset.
- `REGISTER__FIELD_MASK` gives the already-shifted field mask.
- The register names match the companion offset header, `sdma_4_4_0_offset.h`, where `regSDMA3_GFX_RB_CNTL`, `regSDMA3_PAGE_RB_CNTL`, `regSDMA3_RLC0_RB_CNTL`, and related address constants are defined.
- Driver code consumes these macros through common AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, `RREG32`, and `WREG32`.

The queue register groups repeat a common SDMA queue programming schema across `SDMA2_RLC5/6/7`, `SDMA3_GFX`, `SDMA3_PAGE`, and `SDMA3_RLC0/1/2/3`, with the start of the same schema for `SDMA3_RLC4`:

- Ring-buffer control and addressing: `RB_CNTL`, `RB_BASE`, `RB_BASE_HI`, `RB_RPTR`, `RB_RPTR_HI`, `RB_WPTR`, `RB_WPTR_HI`.
- Write-pointer polling and read-pointer writeback: `RB_WPTR_POLL_CNTL`, `RB_RPTR_ADDR_HI`, `RB_RPTR_ADDR_LO`, `RB_WPTR_POLL_ADDR_HI`, `RB_WPTR_POLL_ADDR_LO`.
- Indirect-buffer state: `IB_CNTL`, `IB_RPTR`, `IB_OFFSET`, `IB_BASE_LO`, `IB_BASE_HI`, `IB_SIZE`, `IB_SUB_REMAIN`.
- Scheduling and context state: `SKIP_CNTL`, `CONTEXT_STATUS`, `PREEMPT`, `CSA_ADDR_LO`, `CSA_ADDR_HI`, `MIDCMD_DATA0` through `MIDCMD_DATA10`, `MIDCMD_CNTL`.
- Doorbell and queue status: `DOORBELL`, `DOORBELL_OFFSET`, `DOORBELL_LOG`, `STATUS`, `WATERMARK`, `MINOR_PTR_UPDATE`.
- AQL queue support: `RB_AQL_CNTL`.

The `SDMA3` public engine block adds fields for firmware and engine-wide controls:

- Microcode and virtualization: `SDMA3_UCODE_ADDR`, `SDMA3_UCODE_DATA`, `SDMA3_VF_ENABLE`.
- Power, clock, and global control: `SDMA3_POWER_CNTL`, `SDMA3_CLK_CTRL`, `SDMA3_CNTL`, `SDMA3_POWER_CNTL_IDLE`, `SDMA3_CLK_STATUS`.
- Engine status and debug: `SDMA3_STATUS_REG`, `SDMA3_STATUS1_REG`, `SDMA3_STATUS2_REG`, `SDMA3_STATUS3_REG`, `SDMA3_STATUS4_REG`, `SDMA3_ERROR_LOG`, `SDMA3_PROGRAM`, `SDMA3_FREEZE`, `SDMA3_ID`, `SDMA3_VERSION`.
- Memory translation and UTCL1 behavior: `SDMA3_UTCL1_CNTL`, `SDMA3_UTCL1_WATERMK`, `SDMA3_UTCL1_RD_STATUS`, `SDMA3_UTCL1_WR_STATUS`, invalidation/XNACK registers, timeout, and page configuration.
- RAS and EDC: `CC_SDMA3_EDC_CONFIG`, `SDMA3_EDC_COUNTER`, `SDMA3_EDC_COUNTER2`, `SDMA3_RAS_STATUS`.
- Performance and diagnostics: `SDMA3_PERFCNT_*`, `SDMA3_F32_*`, `SDMA3_SCRATCH_RAM_*`, public dummy registers, and physical address debug fields.

## Control Flow and Runtime Use

This header has compile-time control flow only: include guards expose macro constants to translation units that include it. The runtime control flow lives in consumers. In this tree, `drivers/gpu/drm/amd/amdgpu/sdma_v4_4.c` includes `sdma_4_4_0_offset.h` and this mask header, then uses the generated field macros indirectly through register helpers and RAS field tables.

For SDMA 4.4, `sdma_v4_4_get_reg_offset()` computes the absolute MMIO offset for SDMA instances by adding per-instance deltas such as `SDMA3_REG_OFFSET` to the SDMA0 base. KFD integration code also relies on queue register spacing, for example deriving an RLC queue register base from `mmSDMA*_RLC0_RB_CNTL` and adding `queue_id * (mmSDMA0_RLC1_RB_CNTL - mmSDMA0_RLC0_RB_CNTL)`. The repeated `RLCn` macro groups in this chunk must therefore stay aligned with the offset header's spacing assumptions.

Queue programming normally follows the hardware state model represented by these masks: program ring base and size, configure write/read pointer handling, set doorbell offset/enables, configure IB and VMID behavior, then enable the queue or allow preemption/context switching. The header only supplies field locations for those writes; ordering, synchronization, and polling are enforced by the driver and hardware documentation.

## State and Persistence Behavior

The macros describe persistent hardware state held in SDMA MMIO registers and, for selected queues, state mirrored to GPU memory:

- `RB_BASE*`, `RB_RPTR*`, `RB_WPTR*`, and `RB_CNTL` define queue ring-buffer state. Misprogramming these fields can persist until queue teardown, engine reset, or full GPU reset.
- `RB_RPTR_ADDR_*` enables read-pointer writeback into memory. `RPTR_WB_IDLE` in the low address register is a hardware-visible status bit, while the address field is aligned by a low-bit shift.
- `RB_WPTR_POLL_*` registers let hardware poll a memory write pointer, which creates persistence outside the MMIO register file because GPU memory contents drive queue progress.
- `CSA_ADDR_*`, `CONTEXT_STATUS`, `PREEMPT`, `MIDCMD_DATA*`, and `MIDCMD_CNTL` represent context-save/preemption state. These fields are especially relevant for recovery and context switch correctness.
- `DOORBELL`, `DOORBELL_OFFSET`, and `DOORBELL_LOG` connect the queue to doorbell aperture writes from the CPU or user-mode/KFD paths. Doorbell state persists while the queue is active.
- `EDC_COUNTER*`, `RAS_STATUS`, `STATUS*_REG`, `UTCL1_*_STATUS`, and XNACK/invalidation registers expose accumulated or in-flight hardware status that may survive until read-clear, explicit reset, or engine reset depending on the register.

Because this is a generated register header, there is no software serialization or persistence mechanism in the file itself. Its state model is entirely the SDMA hardware register file plus memory locations referenced by address fields.

## Dependencies and Integration Points

This chunk depends on exact agreement with several neighboring generated and driver components:

- `sdma_4_4_0_offset.h` supplies the `regSDMA*` offsets that pair with these masks.
- `sdma_4_4_0_default.h` or other default tables, where present in sibling ASIC register trees, must match reset defaults for fields such as `RB_CNTL`, `IB_CNTL`, `CONTEXT_STATUS`, and AQL control.
- `amdgpu/sdma_v4_4.c` includes this header for SDMA 4.4 RAS and register access support.
- `amdgpu_amdkfd_arcturus.c` and related KFD code derive SDMA RLC queue register bases and depend on consistent `RLCn` register layout across engines and queue IDs.
- Generic SOC15 register macros depend on the `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` naming pattern.

The generated macros are also conceptually tied to firmware and ASIC documentation. A one-bit drift in fields such as VMID, doorbell enable, writeback enable, preempt, UTCL1 credit/watermark, or RAS counters changes hardware behavior even though the C compiler will still build successfully.

## Risks and Edge Cases

- The line range begins mid-register at `SDMA2_RLC5_RB_CNTL`, so chunk-local readers need the previous chunk for the first four field definitions in that register. The remaining `RB_CNTL` fields in this chunk still show the same layout repeated for later queues.
- Queue blocks are repetitive but not purely cosmetic. A missing, duplicated, or shifted macro in one instance can break only a single engine/queue combination, making failures hardware- and workload-specific.
- `SDMA3_RLC4` is incomplete in this chunk; only `RB_CNTL` through `RB_WPTR_POLL_CNTL` appear before the line boundary. The following chunk must be consulted for the rest of that queue's IB, doorbell, context, and mid-command fields.
- Field widths encode alignment requirements. Address fields such as `IB_BASE_LO`, `RB_RPTR_ADDR_LO`, `DOORBELL_OFFSET`, and polling address lows mask off low bits. Consumers must provide aligned addresses and avoid assuming the raw register stores byte-granular values.
- `RB_VMID`, `CMD_VMID`, `RB_PRIV`, and doorbell fields are privilege/VM isolation sensitive. Incorrect masks can allow commands to execute in the wrong VM context or with wrong privilege.
- Preemption and mid-command save fields are recovery-sensitive. Incorrect `MIDCMD_CNTL`, `PREEMPT`, or `CONTEXT_STATUS` masks can make queue preemption, reset recovery, or context switch diagnostics unreliable.
- UTCL1 and XNACK fields affect memory translation retry, invalidation, and timeout behavior. Bad field definitions can present as hangs, page fault storms, or silent performance regressions rather than obvious compile failures.
- RAS counter masks feed error accounting. If EDC field masks drift, `sdma_v4_4` RAS reporting can undercount, overcount, or attribute errors to the wrong SDMA buffer.

## Test Signals

Useful validation is mostly integration and hardware-facing:

- Build coverage for AMDGPU with SDMA 4.4 support verifies macro names expected by `sdma_v4_4.c`, SOC15 helpers, and KFD code still exist.
- Register read/write smoke tests should confirm `RB_CNTL` enable/size/writeback fields, `IB_CNTL`, doorbell enable/offset, and write-pointer polling fields land in the documented bits for `SDMA3_GFX`, `SDMA3_PAGE`, and representative `RLCn` queues.
- KFD queue creation tests on SDMA-capable ASICs should exercise RLC queue spacing and doorbell programming, especially queues near the edges covered here: `SDMA2_RLC7`, `SDMA3_RLC0`, `SDMA3_RLC3`, and `SDMA3_RLC4`.
- GPU reset, queue preemption, and hang-recovery tests should watch `CONTEXT_STATUS`, `PREEMPT`, `CSA_ADDR_*`, and `MIDCMD_*` behavior.
- RAS injection or counter polling tests should validate `SDMA3_EDC_COUNTER`, `SDMA3_EDC_COUNTER2`, and `SDMA3_RAS_STATUS` accounting through the `sdma_v4_4` RAS path.
- VM fault and XNACK stress tests should monitor `SDMA3_UTCL1_*` status, invalidation, timeout, and page fields.
- Performance-counter tests should ensure `SDMA3_PERFCNT_*` configuration and result masks produce stable, nonzero counters under SDMA traffic.
