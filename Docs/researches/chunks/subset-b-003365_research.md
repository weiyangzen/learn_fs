# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma/sdma_4_4_0_sh_mask.h lines 5211-7807

## Scope

This chunk is a generated AMD SDMA 4.4.0 shift/mask header segment. It covers lines 5211-7807 of `sdma_4_4_0_sh_mask.h` and defines 2,120 preprocessor constants: 1,061 `__SHIFT` values and 1,059 `_MASK` values under 475 visible register comments. The range begins inside `SDMA1_RLC5_MIDCMD_CNTL`, covers complete `SDMA1_RLC6` and `SDMA1_RLC7` queue-context register groups, enters the `sdma0_sdma2dec` address block for SDMA instance 2, covers SDMA2 global/status/RAS/performance fields, then covers `SDMA2_GFX`, `SDMA2_PAGE`, and `SDMA2_RLC0` through `SDMA2_RLC4` queue groups. It ends inside `SDMA2_RLC5_RB_CNTL`, before the remaining `SDMA2_RLC5` fields.

The file is data-only register metadata. It has no functions, structs, control statements, or storage. Runtime behavior comes from C code that includes this header together with `sdma_4_4_0_offset.h`, then uses the constants in register access macros such as `RREG32`, `WREG32`, `SOC15_REG_FIELD`, `REG_SET_FIELD`, and related AMDGPU helpers.

## Purpose

The chunk provides bit layouts for SDMA 4.4.0 registers. Each logical field has a shift constant and usually a mask constant, allowing driver code to construct, update, and decode 32-bit MMIO register values without hard-coding bit positions at call sites. This matters for SDMA ring setup, indirect-buffer execution, context switching, doorbell delivery, queue preemption, RAS/error reporting, performance counters, and low-level debug/status reads.

The source path is under `drivers/gpu/drm/amd/include/asic_reg/sdma`, so it belongs to AMDGPU hardware-description headers rather than Ceph-specific code. In this repository it is carried inside the Linux client source tree used by the distributed-fs snapshot.

## Important Macro Families

- Boundary carry-in: lines 5211-5216 finish `SDMA1_RLC5_MIDCMD_CNTL` by defining `SPLIT_STATE` and `ALLOW_PREEMPT` shifts/masks plus the `DATA_VALID` and `COPY_MODE` masks. Because the chunk starts mid-register, the `DATA_VALID` and `COPY_MODE` shifts are in the previous chunk.
- `SDMA1_RLC6_*` and `SDMA1_RLC7_*`: two complete SDMA1 RLC queue contexts. Each context has ring-buffer control/base/read-pointer/write-pointer registers, write-pointer poll registers, indirect-buffer control/base/size/offset/read-pointer registers, skip count, context status, doorbell state/log/offset, read/write watermarks, context-save-area addresses, IB preemption, dummy/debug storage, AQL packet sizing, minor pointer update, and eleven mid-command data registers plus mid-command control.
- `SDMA2_UCODE_*`, `SDMA2_VF_ENABLE`, `SDMA2_CONTEXT_GROUP_BOUNDARY`, `SDMA2_POWER_CNTL`, `SDMA2_CLK_CTRL`, and `SDMA2_CNTL`: global SDMA2 setup fields for microcode access, virtualization enable, power/clock behavior, trap and interrupt enables, data/fence swap, mid-command preemption/expiry/world-switch, auto context switching, and frozen/preempt interrupt enables.
- `SDMA2_STATUS_REG`, `SDMA2_STATUS1_REG`, `SDMA2_STATUS2_REG`, `SDMA2_STATUS3_REG`, and `SDMA2_STATUS4_REG`: status decode fields for idle/full/empty conditions, ring and IB command states, memory-controller read/write idleness, semaphore state, interrupt stall state, copy-engine sub-block idleness, and additional internal status words.
- `SDMA2_RD_BURST_CNTL`, `SDMA2_HBM_PAGE_CONFIG`, `SDMA2_F32_CNTL`, `SDMA2_PHASE0_QUANTUM`, `SDMA2_PHASE1_QUANTUM`, `SDMA2_PHASE2_QUANTUM`, `SDMA2_BA_THRESHOLD`, and `SDMA2_RELAX_ORDERING_LUT`: scheduling, burst, page, functional-test/debug, quantum, boundary-address, and relaxed-ordering controls.
- `SDMA2_EDC_COUNTER`, `SDMA2_EDC_COUNTER2`, `SDMA2_ERROR_LOG`, and `SDMA2_RAS_STATUS`: RAS/error-observation fields. The chunk includes single-error-detection counters for SDMA memory banks, ucode/RB/IB command buffers, UTCL1 FIFOs, data LUT/split buffers, memory-controller FIFOs, plus RAS fetch ECC and NACK-generation status bits.
- `SDMA2_UTCL1_*`: UTCL1 control, watermark, read/write status, invalidation slots, read/write XNACK address ranges, timeout, and page-control fields. These tie SDMA memory accesses into GPU virtual-memory translation, retry, and fault-observation paths.
- `SDMA2_PERFCNT_*` and `SDMA2_F32_COUNTER`: performance-counter selection, clear/reset/start/stop controls, result readout control, low/high counter values, and a free-running or debug counter.
- `SDMA2_GFX_*`, `SDMA2_PAGE_*`, and `SDMA2_RLC0_*` through `SDMA2_RLC4_*`: queue-specific register groups with a repeated layout. `GFX` and `PAGE` cover graphics and page queues; `RLCn` covers RLC-managed queue contexts. The chunk begins the `SDMA2_RLC5_RB_CNTL` group but only includes the first part of that register.

## Register Field Semantics

The repeated queue groups expose the SDMA queue programming model:

- `*_RB_CNTL` fields include `RB_ENABLE`, `RB_SIZE`, byte-swap controls, read-pointer writeback enable/swap/timer, privilege bit, and VMID. These fields control whether the ring runs, how large it is, how pointers are written back, and which VM context owns commands.
- `*_RB_BASE`, `*_RB_BASE_HI`, `*_RB_RPTR`, `*_RB_RPTR_HI`, `*_RB_WPTR`, and `*_RB_WPTR_HI` describe the ring buffer address and producer/consumer offsets. Low address fields often use alignment masks such as `0xFFFFFFFCL`, while high fields are full or partial upper address words.
- `*_RB_WPTR_POLL_CNTL` and `*_RB_WPTR_POLL_ADDR_{HI,LO}` configure polling of a memory write pointer, including enable, swap, F32 poll mode, poll frequency, idle poll count, and aligned poll address.
- `*_IB_CNTL`, `*_IB_RPTR`, `*_IB_OFFSET`, `*_IB_BASE_{LO,HI}`, `*_IB_SIZE`, and `*_IB_SUB_REMAIN` define indirect-buffer execution state. These fields gate IB execution, endian/swap handling, switching inside an IB, command VMID, IB address, current pointer, and remaining sub-buffer size.
- `*_CONTEXT_STATUS` exposes scheduler/context state: selected, idle, expired, exception, context-switch capable, context-switch ready, preempted, and preempt disabled.
- `*_DOORBELL`, `*_DOORBELL_OFFSET`, and `*_DOORBELL_LOG` define doorbell enable/captured bits, queue doorbell offset, logged doorbell data, and backend-error status.
- `*_WATERMARK` captures outstanding read/write thresholds, while `*_CSA_ADDR_{LO,HI}` points at context-save storage.
- `*_PREEMPT`, `*_MIDCMD_DATA0` through `*_MIDCMD_DATA10`, and `*_MIDCMD_CNTL` support mid-command preemption/restart. Control fields identify whether saved data is valid, whether copy mode is active, split state, and whether preemption is allowed.
- `*_RB_AQL_CNTL` and `*_MINOR_PTR_UPDATE` support AQL packet sizing/step and minor pointer update behavior for queues that can process AQL-formatted packets.

Most masks are 32-bit `L` integer constants. Consumers are expected to combine masks with shifts through the AMD register-field macros rather than by direct arithmetic where possible.

## Control Flow

There is no direct control flow in this header. The operational flow implied by the macros is:

1. Include `sdma_4_4_0_offset.h` for register addresses and this file for field masks.
2. Compute the register address for a given SDMA instance and queue. In `amdgpu/sdma_v4_4.c`, `sdma_v4_4_get_reg_offset()` starts from `adev->reg_offset[SDMA0_HWIP][0][0]` and adds instance deltas such as `SDMA1_REG_OFFSET`, `SDMA2_REG_OFFSET`, `SDMA3_REG_OFFSET`, and `SDMA4_REG_OFFSET`.
3. Read or compose a register value with `RREG32`, `WREG32`, `REG_SET_FIELD`, or `SOC15_REG_FIELD`.
4. For ring/IB setup, program base addresses, pointer addresses, pointer polling, doorbells, and enable bits. For shutdown or preemption, clear enable/preempt bits and poll status bits such as `IDLE`, `CONTEXT_EMPTY`, or per-context `CONTEXT_STATUS`.
5. For diagnostics and RAS, read status/counter registers, mask and shift the relevant fields, then report or clear counters.

The queue groups are intentionally regular, so driver code can often calculate offsets from an RLC0 base register and a per-queue stride. Adjacent KFD code in the AMDGPU tree uses this pattern for SDMA RLC save/restore and queue enable/disable flows.

## State And Persistence

The header itself persists only compile-time constants. Hardware state lives in SDMA MMIO registers and in GPU-visible memory addresses programmed through those registers:

- Ring state persists in RB base, read pointer, write pointer, and read-pointer writeback registers until reset, reinitialization, or context teardown.
- IB state persists in IB base, size, offset/read-pointer, and remaining-size registers while an indirect buffer is executing.
- Doorbell state is partly MMIO-visible through enable/captured/log fields and partly external through doorbell aperture writes.
- Context-switch and preemption state persists in context status, CSA address, mid-command data, and mid-command control registers.
- RAS and performance state persists in EDC/error/status/perf-counter registers until cleared or reset.
- Power/clock and global SDMA2 control fields persist as device runtime state and are usually reprogrammed during ASIC init, resume, reset, or mode changes.

Because these are hardware register definitions, incorrect masks can corrupt persistent device state even though the header has no C storage of its own.

## Dependencies

- `sdma_4_4_0_offset.h`: supplies the matching `regSDMA*` register offsets and base-index metadata. The masks in this chunk are only meaningful with the matching offset header from the same generated register package.
- `amdgpu/sdma_v4_4.c`: directly includes both the offset and shift/mask headers. Its RAS helpers use SDMA register field metadata and instance offset calculations to query and clear SDMA EDC counters.
- AMDGPU register helpers: `RREG32`, `WREG32`, `REG_SET_FIELD`, `SOC15_REG_FIELD`, and `SOC15_REG_ENTRY` are the normal integration layer for these constants.
- AMDGPU device state: `struct amdgpu_device`, especially `adev->reg_offset`, `adev->sdma.num_instances`, and RAS support checks, determines which physical SDMA instances are accessed.
- KFD/compute SDMA queue management patterns: related AMDGPU KFD files use RLC queue register offsets, enable bits, context status bits, doorbells, and CSA/mid-command ranges for queue save, restore, disable, and resume.

## Integration Points

- ASIC bring-up and reset: global SDMA2 power, clock, control, freeze, status, and microcode fields help bring an SDMA instance online and verify idleness.
- Ring and IB submission: `GFX`, `PAGE`, and `RLCn` queue macros support ring buffer and indirect-buffer setup, including endian/swap handling and write-pointer writeback.
- Doorbell signaling: queue doorbell enable, captured, offset, and log fields integrate with userspace/kernel queue notification and hang diagnosis.
- GPU virtual memory: UTCL1 control/status/XNACK/timeout fields connect SDMA memory operations to GPUVM translation and retry/fault paths.
- RAS: EDC counters, error log, and RAS status fields feed AMDGPU RAS reporting. `sdma_v4_4.c` queries and clears EDC counter registers across SDMA instances.
- Performance/debug: performance-counter config/result fields, F32 controls/counter, scratch RAM fields, dummy registers, and status words support low-level debug and performance tracing.
- Queue preemption and context switching: per-queue context status, `PREEMPT`, CSA address, and mid-command save/control fields integrate with scheduler and KFD queue lifecycle flows.

## Risks

- Generated-header drift: masks must match the hardware register specification and the paired offset header. A stale or mismatched mask can silently write the wrong bit, which is especially dangerous for enable, VMID, privilege, doorbell, preempt, RAS, and address fields.
- Chunk boundary hazards: this research range starts and ends mid-register family. `SDMA1_RLC5_MIDCMD_CNTL` is incomplete at the start, and `SDMA2_RLC5_RB_CNTL` is incomplete at the end. Any merge/reconciliation pass must combine adjacent chunks before making per-file conclusions about those two registers.
- Repetition mistakes: `GFX`, `PAGE`, and `RLC0`-`RLC7` groups are highly repetitive. Manual edits or generated diffs can easily alter one queue context but not its siblings.
- Address alignment assumptions: several low address fields mask off low bits (`ADDR` shifted by 2 or 5). Callers must pass aligned GPU addresses or the low bits will be discarded.
- Width/sign assumptions: constants use `L` suffixes and many masks occupy bit 31. Consumers should use unsigned 32-bit temporaries for register values to avoid signed comparison or promotion surprises.
- Instance offset assumptions: `sdma_v4_4.c` computes instance register addresses by adding fixed deltas from the SDMA0 base. If the ASIC instance layout or number of instances changes, the same field masks may still compile but target the wrong MMIO block.
- RAS interpretation risk: `sdma_v4_4.c` treats SDMA RAS single-error-detection counts as uncorrectable error count increments and sets correctable count to zero. Field mapping errors in EDC masks would directly skew user-visible RAS accounting.

## Test Signals

- Compile coverage: any typo or missing macro used by SDMA v4.4 code should surface during kernel/AMDGPU compilation, especially in `amdgpu/sdma_v4_4.c`.
- Register-field sanity: inspect generated pairs to ensure each `__SHIFT` has the intended `_MASK`, masks align to field widths, and paired offset names exist in `sdma_4_4_0_offset.h`.
- Runtime ring tests: SDMA queue initialization, memcpy/fill operations, IB execution, and fence completion verify `RB_*`, `IB_*`, writeback, and doorbell masks.
- Suspend/resume and GPU reset: these flows stress persistence and reprogramming of ring base/pointer, global control, status, and RAS/perf state.
- KFD compute queue tests: RLC queue save/restore, doorbell updates, context idle polling, and preemption paths exercise the `RLCn` queue register families.
- RAS injection or counter-read tests: reading and clearing EDC counters should produce expected SDMA RAS counts and logs, validating the EDC and status masks used by `sdma_v4_4.c`.
- Hang/debug diagnostics: status register dumps should decode idle/full/stall/preempt states consistently with observed SDMA behavior.

## Research Notes

This chunk was read as a hardware-description block, not as executable logic. The most important structural fact is that it is part of one generated mask namespace for SDMA 4.4.0 and is consumed by code that already knows the matching register offsets. For final per-file reconciliation, merge this with adjacent chunks to restore the full `SDMA1_RLC5` and `SDMA2_RLC5` register groups and to verify that every SDMA instance/queue group remains internally consistent across the full header.
