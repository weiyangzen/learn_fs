# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma1/sdma1_4_2_2_sh_mask.h lines 1-2569

## Scope

This chunk covers the first 2569 lines of the generated SDMA1 4.2.2 shift/mask header for the `sdma1_sdma1dec` address block. The complete source file has 2956 lines; this chunk starts at the license/header guard and ends at `SDMA1_RLC5_MIDCMD_DATA8__DATA8_MASK`. The remaining `RLC5_MIDCMD_CNTL` and later RLC queue definitions continue in the next chunk.

The chunk contains only C preprocessor definitions. It defines 2123 `#define` lines in the covered range, almost entirely paired `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` constants. There are no functions, structs, global variables, allocations, or executable statements in this range.

## Purpose

This header is the bitfield map for SDMA engine 1 on the 4.2.2 register layout used by Arcturus-generation AMDGPU paths. Its job is to let driver code compose and decode SDMA1 hardware register values without hard-coded bit numbers. The matching `sdma1_4_2_2_offset.h` file supplies register offsets such as `mmSDMA1_RLC5_MIDCMD_DATA8`; this file supplies the field positions and masks inside those 32-bit registers.

Consumers generally use these constants through AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32`, `WREG32`, and `SOC15_REG_OFFSET`. The semantics are hardware-defined: the macros describe bit layout, while the owning SDMA/KFD code decides when to write, poll, clear, or preserve fields.

## Important Macro Families

### Global SDMA1 Control and Virtualization

The opening section maps engine-wide control and virtualization-facing registers:

- `SDMA1_UCODE_ADDR` and `SDMA1_UCODE_DATA` expose the microcode address/data access window.
- `SDMA1_VM_CNTL`, `SDMA1_VM_CTX_LO`, `SDMA1_VM_CTX_HI`, and `SDMA1_VM_CTX_CNTL` define command, address, privilege, and VMID fields for SDMA virtual-memory context handling.
- `SDMA1_ACTIVE_FCN_ID`, `SDMA1_VIRT_RESET_REQ`, and `SDMA1_VF_ENABLE` describe PF/VF selection, reset request bits, VF ID fields, and VF enable state.
- `SDMA1_CONTEXT_REG_TYPE0..3` and `SDMA1_PUB_REG_TYPE0..3` are register type/visibility bitmaps. They group public and context registers for firmware, virtualization, or context-save/restore policy rather than configuring one queue directly.

These definitions matter for SR-IOV or KFD contexts because wrong masks can select the wrong VMID/VF, expose the wrong registers to a context image, or mishandle virtual reset bits.

### Public Engine Configuration and Status

The public SDMA1 register fields cover power, clocking, engine control, addressing, queue fetching, status, atomics, UTCL1, and performance counters:

- `SDMA1_MMHUB_CNTL` selects the MMHUB unit ID.
- `SDMA1_POWER_CNTL`, `SDMA1_CLK_CTRL`, `SDMA1_POWER_CNTL_IDLE`, and `SDMA1_ULV_CNTL` define memory power modes, clock on/off hysteresis, idle delays, soft clock overrides, and ultra-low-voltage interrupt/status bits.
- `SDMA1_CNTL` controls trap, UTC L1, semaphore wait interrupt, data/fence swapping, mid-command preemption/world switch, automatic context switch, and context-empty/frozen/IB-preempt interrupts.
- `SDMA1_CHICKEN_BITS`, `SDMA1_CHICKEN_BITS_2`, `SDMA1_GB_ADDR_CONFIG`, and `SDMA1_GB_ADDR_CONFIG_READ` encode copy-engine tuning, burst/watermark behavior, QoS, and graphics-bank address configuration.
- `SDMA1_RB_RPTR_FETCH*`, `SDMA1_IB_OFFSET_FETCH`, `SDMA1_PROGRAM`, `SDMA1_RD_BURST_CNTL`, `SDMA1_HBM_PAGE_CONFIG`, and `SDMA1_SEM_WAIT_FAIL_TIMER_CNTL` cover command-stream fetch offsets, burst sizes, page size, and semaphore timeout behavior.
- `SDMA1_STATUS_REG`, `SDMA1_STATUS1_REG`, `SDMA1_STATUS2_REG`, and `SDMA1_STATUS3_REG` expose idle, FIFO, packet-ready, memory-request, semaphore, interrupt, copy-engine, command-op, queue-id, and exception status fields.
- `SDMA1_FREEZE`, `SDMA1_F32_CNTL`, `SDMA1_F32_COUNTER`, `SDMA1_PHASE0_QUANTUM`, `SDMA1_PHASE1_QUANTUM`, and `SDMA1_PHASE2_QUANTUM` map freeze/preempt controls, F32 halt/step/counter state, and scheduling quantum fields.
- `SDMA1_EDC_CONFIG`, `SDMA1_EDC_COUNTER`, and `SDMA1_EDC_COUNTER_CLEAR` define ECC/EDC enable, interrupt, many single-error-detected counter bits, and a clear trigger.
- `SDMA1_ATOMIC_CNTL`, `SDMA1_ATOMIC_PREOP_LO`, and `SDMA1_ATOMIC_PREOP_HI` define atomic loop timing, return interrupt enable, and 64-bit pre-op payload storage.
- `SDMA1_PERFMON_CNTL`, `SDMA1_PERFCOUNTER0_RESULT`, `SDMA1_PERFCOUNTER1_RESULT`, and `SDMA1_PERFCOUNTER_TAG_DELAY_RANGE` expose two selectable performance counters and range filtering.
- `SDMA1_GPU_IOV_VIOLATION_LOG` and `SDMA1_GPU_IOV_VIOLATION_LOG2` record GPU IOV violation status, address, operation type, VF/VFID, and initiator ID.

This group supplies diagnostic and control bits used by bring-up, reset, interrupt, power-management, and error-handling paths.

### UTCL1, Page Fault, Invalidation, and XNACK Fields

The `SDMA1_UTCL1_*` group is the SDMA engine's L1 translation/cache interface:

- `SDMA1_UTCL1_CNTL` defines redo enable/delay/watermark, invalidation-ack delay, L2 request credits, and virtual-address watermarks.
- `SDMA1_UTCL1_WATERMK` defines request, page-request, invalidation-request, and XNACK watermarks.
- `SDMA1_UTCL1_RD_STATUS` and `SDMA1_UTCL1_WR_STATUS` expose read/write-side FIFO empty/full state, page fault/null state, L2 idle state, CE/F32 routing state, merge state, write-pointer polling, and related status.
- `SDMA1_UTCL1_INV0..2` define invalidation controls and address/VMID vectors, including flush/non-flush idle bits and invalidation address pieces.
- `SDMA1_UTCL1_RD_XNACK0/1`, `SDMA1_UTCL1_WR_XNACK0/1`, and `SDMA1_UTCL1_TIMEOUT` define XNACK address/VMID/vector/status and read/write XNACK timeout limits.
- `SDMA1_UTCL1_PAGE` defines VM hole, request type, MTYPE, and page-table snoop fields.

These fields are important for page fault, retry, invalidation, and GPU virtual-memory behavior. They are status- and timing-heavy, so software must treat them according to the hardware programming guide rather than inferring write semantics from the names alone.

### Queue Register Blocks: GFX, PAGE, and RLC0-RLC5

From `SDMA1_GFX_RB_CNTL` onward, the chunk defines repeated queue-context register layouts. The same field pattern appears for:

- `SDMA1_GFX_*`, the graphics SDMA queue block.
- `SDMA1_PAGE_*`, the page/VM SDMA queue block.
- `SDMA1_RLC0_*` through `SDMA1_RLC5_*`, six RLC queue blocks covered in this chunk.

Each queue block includes the same major register families:

- Ring buffer control: `RB_CNTL` fields for `RB_ENABLE`, `RB_SIZE`, swap enable, read-pointer writeback enable/swap/timer, `RB_PRIV`, and `RB_VMID`.
- Ring buffer addresses and pointers: `RB_BASE`, `RB_BASE_HI`, `RB_RPTR`, `RB_RPTR_HI`, `RB_WPTR`, `RB_WPTR_HI`, `RB_RPTR_ADDR_HI`, and `RB_RPTR_ADDR_LO`. Low address fields are aligned, with low bits masked out where required.
- Write-pointer polling: `RB_WPTR_POLL_CNTL` and `RB_WPTR_POLL_ADDR_*` define enable/swap/F32 poll controls, frequency, idle poll count, and poll address.
- Indirect buffer controls: `IB_CNTL`, `IB_RPTR`, `IB_OFFSET`, `IB_BASE_LO`, `IB_BASE_HI`, and `IB_SIZE` define enable, swap, inside-IB switch, command VMID, aligned IB address, offset, and size.
- Context and doorbell state: `SKIP_CNTL`, `CONTEXT_STATUS`, `DOORBELL`, `STATUS`, `DOORBELL_LOG`, `DOORBELL_OFFSET`, `CSA_ADDR_LO`, `CSA_ADDR_HI`, and `IB_SUB_REMAIN` expose selection, idle, expired, exception, context-switch, preempted, doorbell enable/capture/log, queue status, watermarks, and context-save-area addresses.
- Preemption and pointer update: `PREEMPT` and `MINOR_PTR_UPDATE` provide IB preemption and controlled pointer update bits.
- AQL and mid-command state: `RB_AQL_CNTL`, `MIDCMD_DATA0..8`, and `MIDCMD_CNTL` define AQL enable/packet sizing, packet step, saved mid-command payload words, data-valid state, copy mode, split state, and preemption allowance.

The chunk ends immediately after the data field for `SDMA1_RLC5_MIDCMD_DATA8`; the corresponding `SDMA1_RLC5_MIDCMD_CNTL` and RLC6/RLC7 blocks are outside this work item.

## Important APIs, Types, and Functions

This chunk itself defines no APIs in the C function or type sense. The important interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset used when encoding or decoding a field.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask for the field in the 32-bit register value.

The primary local consumer found in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_arcturus.c`, which includes `sdma1/sdma1_4_2_2_offset.h` and `sdma1/sdma1_4_2_2_sh_mask.h` alongside the matching SDMA0 and SDMA2-SDMA7 headers. That code computes engine-specific RLC register bases with `SOC15_REG_OFFSET`, then programs or dumps RLC queue registers through the common SDMA register layout.

Even when the direct code path shown there mostly uses SDMA0-named offsets/masks after deriving an engine-relative base, the SDMA1 mask header is still part of the per-engine generated register set and must stay consistent with the SDMA1 offset file and the sibling SDMA engine headers.

## Control Flow and State Behavior

There is no runtime control flow in this header. It affects compiled driver control flow indirectly by defining which bits are set, cleared, tested, or preserved by C code.

Representative runtime flows that depend on these layouts include:

- Queue load: disable `RB_ENABLE`, wait until `CONTEXT_STATUS.IDLE` is observed, program doorbell offset/enabled state, set read/write pointers, install ring base/writeback addresses, then re-enable `RB_ENABLE`.
- Queue dump: iterate contiguous queue register ranges from `RB_CNTL` through doorbell/status/CSA/IB-subremain/minor-pointer/mid-command registers and record raw values for diagnostics.
- Fault and retry handling: read UTCL1 status, invalidation, page, XNACK, and timeout fields to understand translation retry/fault state.
- Power and reset handling: write or poll global power, clock, freeze, preempt, EDC, IOV violation, and status fields during bring-up, reset, or error recovery.

The persistent state represented by these macros lives in hardware registers, not in the header. Some fields are configuration state that persists until reset or reprogramming, such as RB base addresses, VMID, RB size, doorbell offset, AQL control, power/clock settings, and UTCL1 watermarks. Other fields are live or sticky status, such as idle bits, FIFO empty/full indicators, page fault/null state, XNACK state, doorbell captured/log values, EDC counters, IOV violation logs, and preemption/frozen status.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header set:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma1/sdma1_4_2_2_offset.h` provides SDMA1 register offsets and base indices. Its address block starts at base address `0x6180`, and it maps the same names used here, including RLC5 offsets through `mmSDMA1_RLC5_MIDCMD_DATA8` at `0x0330`.
- Sibling SDMA engine headers (`sdma0` through `sdma7`) provide equivalent per-engine layouts for Arcturus multi-SDMA support.
- Common AMDGPU helpers (`REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32`, `WREG32`, `SOC15_REG_OFFSET`) consume the masks and shifts.
- KFD/AMDGPU SDMA queue management uses the queue block fields through MQD-backed values, doorbell programming, pointer updates, context status polling, and register dumps.
- GPU VM/MMHUB paths interact with the VM context and UTCL1/page/XNACK fields.
- Power, reset, diagnostics, virtualization, and SR-IOV/IOV paths interact with the public status, power, EDC, freeze, active function, VF enable/reset, and violation-log fields.

The header must be included as a matched pair with the corresponding SDMA1 4.2.2 offset header. Mixing masks from `sdma1_4_2_2_sh_mask.h` with nearby variants such as `sdma1_4_2_sh_mask.h`, `sdma1_4_0_sh_mask.h`, or `sdma/sdma_4_4_0_sh_mask.h` risks field drift even when many names look identical.

## Risks

- Bitfield drift is high impact. A wrong queue mask can program the wrong RB size, VMID, pointer, doorbell, CSA address, IB address, or AQL field and break SDMA command execution.
- Repeated queue blocks are copy-sensitive. GFX, PAGE, and RLC0-RLC5 share nearly identical layouts, so a generated naming or offset mismatch can silently affect only one queue instance.
- Address alignment masks must be preserved. Fields such as `RB_RPTR_ADDR_LO`, `DOORBELL_OFFSET`, `CSA_ADDR_LO`, and `IB_BASE_LO` intentionally mask low bits; incorrect handling can generate misaligned hardware addresses.
- Polling/status bits are not ordinary software booleans. `CONTEXT_STATUS.IDLE`, FIFO status, page fault, XNACK, EDC, doorbell captured/log, frozen/preempted, and violation-log fields may have hardware-specific clear or latch behavior.
- Virtualization fields are privilege-sensitive. `ACTIVE_FCN_ID`, `VIRT_RESET_REQ`, `VF_ENABLE`, VMID, and GPU IOV violation log masks must not be cross-wired across PF/VF contexts.
- UTCL1/XNACK fields affect GPU VM fault/retry behavior. Bad masks can hide page faults, misidentify a VMID/vector, set bad invalidation controls, or produce unbounded retry/timeout behavior.
- This chunk ends mid-file. A complete per-file report must reconcile this document with the following chunk for `RLC5_MIDCMD_CNTL`, RLC6/RLC7, and any trailing header closure.

## Test and Validation Signals

Useful validation is mostly compile-time plus hardware/driver behavior:

- Build AMDGPU/KFD code that includes the SDMA1 4.2.2 offset and mask headers; this catches renamed, missing, or duplicate macros.
- Run KFD SDMA queue load/unload tests on Arcturus-class hardware and verify RLC queues become idle before programming, then execute after `RB_ENABLE` is restored.
- Exercise doorbell and write-pointer paths, including user write-pointer polling and `MINOR_PTR_UPDATE`, and verify no stuck `WPTR_UPDATE_PENDING` or update-fail counts.
- Dump SDMA RLC registers through the KFD diagnostic path and confirm the register count/ranges align with `RB_CNTL` through `MIDCMD_CNTL` for each queue.
- Run SDMA copy/fill/IB/AQL workloads across SDMA engine 1 and multiple RLC queues to catch RB, IB, VMID, and doorbell field mistakes.
- Exercise GPU VM fault/retry scenarios and validate UTCL1 read/write status, page fault/null, invalidation, XNACK address/VMID/vector, and timeout decoding.
- Validate reset and preemption flows by checking `FREEZE`, `PREEMPT`, `CONTEXT_STATUS`, and mid-command save/restore fields during queue eviction or timeout recovery.
- Check power-management and clock-gating behavior with `POWER_CNTL`, `CLK_CTRL`, `POWER_CNTL_IDLE`, and `ULV_CNTL` fields under suspend/resume and idle workloads.
- Use ECC/EDC and IOV diagnostics where supported to confirm `EDC_COUNTER`, `EDC_COUNTER_CLEAR`, `GPU_IOV_VIOLATION_LOG`, and `GPU_IOV_VIOLATION_LOG2` decode expected hardware events.
