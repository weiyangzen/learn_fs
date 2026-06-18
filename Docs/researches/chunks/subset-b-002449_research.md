# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h lines 1-2602

## Scope

This chunk is the opening segment of the generated AMD GC 10.1.0 shift/mask header. It covers line 1 through line 2602 and defines the include guard plus the first `gc_sdma0_sdma0dec` register-field macros. In this range there are 2,114 `#define` entries: 1,058 `__SHIFT` macros and 1,055 `_MASK` macros across 464 visible register comments. The slice starts with `SDMA0_DEC_START` and ends inside the `SDMA0_RLC7_RB_CNTL` group after `SDMA0_RLC7_RB_CNTL__RB_SWAP_ENABLE__SHIFT`, so the final register group is incomplete in this chunk.

The content is declarative only. There are no C functions, structs, enums, runtime variables, loops, branches, allocation paths, or local persistence behavior. Its exported surface is a generated preprocessor namespace describing bit positions and bit masks for SDMA0 registers on GC 10.1.0-class hardware.

## Purpose

`gc_10_1_0_sh_mask.h` supplies symbolic bitfield constants for AMDGPU and AMDKFD code that programs Graphics Core 10.1.0 registers. Consumers combine this file with `gc_10_1_0_offset.h` register offsets and helpers such as `REG_SET_FIELD`, `RREG32`, `WREG32`, and SDMA instance wrappers to construct read-modify-write values without embedding raw bit numbers in driver logic.

This chunk focuses on the SDMA0 engine and queue-control register map:

- Top-level SDMA0 decoder, power, clock, control, status, performance, error, MMU/UTCL1, tiling, hash, interrupt, and virtualization/IOV fields.
- The GFX queue register window, including ring buffer control, base/read/write pointers, writeback addresses, indirect buffer control, context status, doorbell, watermark, CSA address, preemption, AQL, minor pointer update, and mid-command state fields.
- The PAGE queue register window with the same ring/IB/doorbell/context/AQL/mid-command structure for page-related SDMA work.
- RLC compute queue windows beginning at `SDMA0_RLC0`, continuing through complete `RLC0` to `RLC6` definitions in this slice, and ending at the start of `RLC7`.

## Exported API Surface

There are no callable APIs or local types. The public interface is the macro family `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`.

Important macro families in this chunk include:

- `SDMA0_POWER_CNTL`, `SDMA0_PG_*`, `SDMA0_CLK_CTRL`, `SDMA0_CNTL`, `SDMA0_F32_CNTL`, `SDMA_POWER_GATING`, and `SDMA_PGFSM_*` for SDMA power gating, clocking, halt, trap, page interrupt, context-switch, and memory-power behavior.
- `SDMA0_STATUS_REG`, `STATUS1_REG`, `STATUS2_REG`, and `STATUS3_REG` for idle, ring, command, exception, queue-match, VM/TLBI/GCR, and interrupt-state readback.
- `SDMA0_GB_ADDR_CONFIG`, `TILING_CONFIG`, `HASH`, `PHYSICAL_ADDR_*`, `UTCL1_*`, `TLBI_GCR_CNTL`, and page/XNACK/invalidate fields for memory addressing, tiling, translation, invalidation, and address debug support.
- `SDMA0_PERFMON_CNTL`, `PERFCOUNTER*_SELECT*`, `PERFCOUNTER*_LO/HI`, and `PERFCOUNTER*_RESULT` for SDMA performance counter selection, mode, clear, enable, and readback.
- `SDMA0_GFX_*` and `SDMA0_PAGE_*` queue register groups for kernel driver SDMA rings.
- `SDMA0_RLC{0..6}_*` plus the beginning of `SDMA0_RLC7_RB_CNTL` for compute/HSA SDMA queue contexts controlled by KFD and firmware-visible MQD state.

Repeated queue windows expose a consistent set of fields: `RB_ENABLE`, `RB_SIZE`, byte-swap controls, read-pointer writeback enable/timer, VMID/privilege selection, ring base/rptr/wptr, write-pointer polling address and cadence, IB enable/base/size/offset, skip count, context selected/idle/expired/exception/preempt status, doorbell enable/capture/offset, outstanding read/write watermarks, CSA address, preempt trigger, AQL packet controls, minor pointer update, and mid-command data/control.

## Register Areas Covered

The initial SDMA0 control block describes engine-wide setup. Power-gating fields carry command/status and memory low/deep/shutdown controls. Clock-control and chicken-bit groups expose clock gating, copy efficiency, stall behavior, write burst tuning, QoS, and internal FIFO watermarks. `SDMA0_CNTL` is the main software-facing control register for traps, UTC L1, semaphore wait interrupts, data/fence swapping, mid-command preemption, page interrupts, per-channel performance counters, world switch, automatic context switching, and selected exception interrupts.

The status and memory-management section provides readbacks for idle states, ring fullness, command-progress state, exception details, page/physical address logging, UTCL1 watermarks, invalidate and XNACK controls, TLBI/GCR command credits, GPU IOV violation logging, AQL status, relaxed ordering, and tiling/hash configuration. These fields are used by bring-up, fault handling, virtualization, debugging, and performance investigation code.

The GFX and PAGE queue windows are full SDMA execution contexts. Their ring-buffer controls define enable state, ring size, endianness behavior, read-pointer writeback, VMID, privilege, and writeback-idle state. Pointer and base registers carry queue memory addresses and hardware read/write offsets. Doorbell and write-pointer polling registers select how userspace or the kernel notifies the SDMA engine of new work. IB, skip, preempt, AQL, and mid-command registers support indirect-buffer execution, queue recovery, AQL packet mode, and preemption/restoration.

The RLC queue windows repeat the same structural contract for compute queues. The chunk fully covers RLC0 through RLC6 and begins RLC7. In-tree KFD code uses the RLC0 field layout as a template for per-queue MQD values, while queue index and engine offsets select the actual hardware queue window.

## Control Flow And State Behavior

This header has no software control flow. Runtime behavior appears only when included by AMDGPU or AMDKFD code that reads and writes the corresponding MMIO registers.

The field names describe several hardware state machines and driver workflows:

- Engine lifecycle: power-gating commands, clock/halt controls, F32 halt, context-switch enable, and phase quantum fields participate in SDMA start, stop, suspend, resume, and scheduling behavior.
- Queue lifecycle: the driver programs ring base, size, read/write pointers, read-pointer writeback, doorbell offset, polling address, and finally `RB_ENABLE`/`IB_ENABLE` to make a queue runnable.
- Compute queue handoff: KFD MQD setup stores values built from `SDMA0_RLC0_*` shifts, then queue load code writes RLC registers, waits for `CONTEXT_STATUS.IDLE`, installs doorbell and pointer state, and enables the ring.
- Preemption and context save/restore: context status, CSA address, IB subremain, mid-command data, split state, and allow-preempt fields model the hardware-visible state needed to stop and later resume queued work.
- Fault and diagnostic handling: status, physical-address, UTCL1, TLBI/GCR, error/log, interrupt, performance, and IOV violation fields expose observable state for driver diagnostics and recovery.

No software state is persisted in this file. Hardware register values persist according to ASIC reset, power, firmware, and context-switch domains. In driver code, selected values are mirrored in objects such as SDMA MQDs and `amdgpu_ring` state, but this header only names the bit positions used to encode those values.

## Dependencies And Integration Points

The syntactic dependency is the C preprocessor. The semantic dependency is AMD's generated GC 10.1.0 register database and the companion offset header `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h`, which defines matching `mmSDMA0_*` register addresses in the `gc_sdma0_sdma0dec` block.

Direct in-tree include sites for `gc_10_1_0_sh_mask.h` or the matching offset header include:

- `drivers/gpu/drm/amd/amdgpu/gfx_v10_0.c`, `gfxhub_v2_0.c`, `mmhub_v2_0.c`, `nv.c`, `mxgpu_nv.c`, and `sdma_v5_0.c` for GC 10/Navi-era graphics, memory hub, virtualization, and SDMA programming.
- `drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10.c` and related Arcturus/GFX KFD bridge code for compute queue save/load and SDMA queue offsets.
- `drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v10.c` and `kfd_device_queue_manager_v10.c` for constructing SDMA MQDs with fields such as `SDMA0_RLC0_RB_CNTL__RB_SIZE__SHIFT`, `RB_VMID__SHIFT`, and `RPTR_WRITEBACK_TIMER__SHIFT`.
- `drivers/gpu/drm/amd/amdgpu/sdma_v5_0.c` and related SDMA version files for ring bring-up, halt/unhalt, trap handling, page queue setup, doorbells, and performance/debug paths.

Common integration helpers include `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SDMA`, `WREG32_SDMA`, `RREG32`, and `WREG32`. The macro naming also aligns with firmware-visible SDMA MQD layouts, KFD queue management, GPU reset/recovery, SR-IOV, VM fault handling, and performance counter plumbing.

## Risks

- Generated-header drift is the main risk. A wrong shift or mask can silently write adjacent SDMA control bits during read-modify-write sequences.
- Ring and pointer fields are address-sensitive. Mis-shifting `RB_BASE`, `RB_RPTR_ADDR_LO`, `RB_WPTR_POLL_ADDR_LO`, IB base, doorbell offset, or CSA address fields can make SDMA fetch commands from the wrong memory or corrupt writeback state.
- Queue windows are highly repetitive. A generation or copy error in one RLC queue can create queue-index-specific compute failures that are difficult to diagnose.
- Enable ordering matters in consumer code even though the header cannot encode it. Drivers normally program size, base, read/write pointers, writeback, doorbell, polling, and VMID before asserting `RB_ENABLE` and `IB_ENABLE`.
- Status/control fields share the same macro form. Consumers must know from the hardware spec which fields are read-only, write-one-to-clear, sticky, reset-sensitive, privileged, or reserved.
- Preemption and mid-command fields are stateful hardware surfaces. Incorrect use can lose in-flight command state, break context switches, or leave a queue unable to resume.
- The chunk boundary ends inside `SDMA0_RLC7_RB_CNTL`; merge-time analysis should expect the remaining `RLC7` shift and mask definitions in the following chunk before flagging missing pairs.

## Test Signals

Useful validation is mostly build-time, generation-time, and hardware-integration oriented:

- Compile or preprocess AMDGPU and AMDKFD code that includes `gc_10_1_0_offset.h` and `gc_10_1_0_sh_mask.h`, especially `sdma_v5_0.c`, `gfx_v10_0.c`, `amdgpu_amdkfd_gfx_v10.c`, `kfd_mqd_manager_v10.c`, and `kfd_device_queue_manager_v10.c`.
- Static checks that complete register groups in the full header have matching `__SHIFT` and `_MASK` definitions; this slice has a known boundary mismatch because it ends at `SDMA0_RLC7_RB_CNTL__RB_SWAP_ENABLE__SHIFT`.
- Cross-check every register-family prefix in this chunk against `gc_10_1_0_offset.h` addresses such as `mmSDMA0_POWER_CNTL`, `mmSDMA0_GFX_RB_CNTL`, `mmSDMA0_PAGE_RB_CNTL`, and `mmSDMA0_RLC0_RB_CNTL`.
- Runtime SDMA ring tests on GC 10.1.0-class hardware: GFX ring initialization, command submission, fences, traps, indirect buffers, page queue operation, suspend/resume, reset recovery, and queue disable/enable cycles.
- KFD compute queue tests that create, load, preempt, restore, and destroy SDMA queues while validating MQD-programmed `RB_SIZE`, `RB_VMID`, read-pointer writeback, doorbell offset, and context idle behavior.
- Fault and debug tests for VM faults, UTCL1 invalidation/XNACK, TLBI/GCR activity, GPU IOV violations, performance counters, AQL status, and SDMA status register readback.

## Chunk Notes For Merge

This document intentionally covers only lines 1-2602 of `gc_10_1_0_sh_mask.h`. Later chunks should continue `SDMA0_RLC7_RB_CNTL` and the remaining GC 10.1.0 register-field namespace. The final per-file report should treat the whole file as a generated ASIC bitfield map for AMD GC 10.1.0 hardware rather than handwritten driver logic.
