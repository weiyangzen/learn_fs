# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h lines 17372-19900

## Purpose

This chunk is generated AMD GC 10.3.0 register bitfield metadata. It contains no executable C logic; it exports preprocessor `__SHIFT` and `_MASK` constants that AMDGPU, AMDKFD, power-management, debug, and profiling code use to compose and decode 32-bit MMIO register values. The matching register offsets and base indices are in `gc_10_3_0_offset.h`.

The selected range starts in the command-processor suspend/DDID/HQD area, spans SPI, compute HQD, DIDT/CAC, TCP, and GDS address blocks, and ends at the first depth-buffer render/count registers in `gc_gfxdec0`. Although this repository subtree is under `ceph-client`, this file is AMD GPU hardware-description metadata rather than filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocations, locks, or callbacks in this range. The API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask for that field inside the register.
- Consumers combine these with `mm<REGISTER>` and `mm<REGISTER>_BASE_IDX` macros from `gc_10_3_0_offset.h`, usually via `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, `SOC15_REG_OFFSET`, or KFD MQD initialization code.

Major register groups in this chunk:

- Command processor suspend and draw-dispatch ID state: `CP_SUSPEND_CNTL`, `CP_IQ_WAIT_TIME3`, `CPC_DDID_*`, `CP_DDID_*`, and graphics DDID counters/pointers. These define suspend enable/lock/status bits, DDID buffer base addresses, VMID selection, policy/mode/enable fields, in-flight counts, read/write pointers, and delta-report counters.
- Graphics HPD/HQD and MQD queue state: `CP_GFX_HPD_*`, `CP_GFX_MQD_*`, `CP_GFX_HQD_*`, `CP_RB_*`, `CP_CE_*`, and `CP_HQD_GFX_*`. Fields describe mapped/active queue state, queue priority and quantum, ring-buffer base/read/write pointers, read-pointer report addresses, write-pointer poll addresses, doorbell offsets and enables, buffer sizing, cache policy, execute/volatile/no-update flags, dequeue requests, idle/preempt status, HQ control messages, CE queue mirrors, and MQD VMID/privilege/cache controls.
- CP DMA watchpoints and miscellaneous CP status/control: `CP_DMA_WATCH0..3_*`, `CP_DMA_WATCH_STAT_*`, `CP_PFP_JT_STAT`, `CP_CE_JT_STAT`, `CP_MEC_JT_STAT`, `CP_FETCHER_SOURCE`, `CP_CE_CS_PARTITION_INDEX`, ring active/status registers, `CPG_RCIU_CAM_*`, timestamp offsets, UTCL1 status registers, `CP_SD_CNTL`, `CP_SOFT_RESET_CNTL`, and `CP_CPC_GFX_CNTL`. These fields support DMA address watch setup, read/write watch masks, VMID filtering, trap/status reporting, command-source selection, ring activity inspection, timestamp adjustment, translation-cache status, soft reset, and CP graphics control.
- `addressBlock: gc_spipdec` shader-processor input controls: `SPI_ARB_PRIORITY`, arbitration cycle registers, workload-control pipe percentage registers for GFX/HP3D/CS pipes, graphics debug wave/trap control and mask registers, `SPI_COMPUTE_QUEUE_RESET`, CU resource reservation masks `SPI_RESOURCE_RESERVE_CU_0..9`, corresponding enable registers, compute wavefront context-save control, arbiter control, feature controls, and shader resource limit controls.
- `addressBlock: gc_cpphqddec` compute packet-processor HQD/MQD registers: `CP_HPD_*`, `CP_MQD_*`, `CP_HQD_*`, EOP base/control/pointers/events, context-save base/control/size/offset registers, GDS resource state, AQL control, suspend context-stack/workgroup-state offsets, DDID pointers/counts, and dequeue status. These macros are central to compute queue creation, MES/HWS interaction, KFD MQD layout, doorbells, packet queue behavior, indirect-buffer handling, semaphores, atomics, scheduler controls, EOP event queues, context save/restore, and suspend/resume.
- `addressBlock: gc_didtdec` and `gc_gccacdec` power/telemetry controls: DIDT indirect index/data/auto-increment registers and GC/SE CAC, EDC, throttle, perf counter, stretch, hysteresis, and indirect index/data registers. These fields are used for dynamic-inductive-droop and chip-activity/power-control programming by firmware or power-management code.
- `addressBlock: gc_tcpdec` texture/cache watch and perf filter registers: `TCP_WATCH0..3_ADDR_H/L`, `TCP_WATCH0..3_CNTL`, `TCP_UTCL0_STATUS`, `TCP_PERFCOUNTER_FILTER`, `TCP_PERFCOUNTER_FILTER_EN`, and `TCP_PERFCOUNTER_FILTER2`. Fields define watched address windows, VMID/mode/valid controls, translation-cache status, and performance counter filter selection.
- `addressBlock: gc_gdspdec` GDS/GWS/OA state: `GDS_VMID0..15_BASE/SIZE`, `GDS_GWS_VMID0..15`, `GDS_OA_VMID0..15`, GWS resource reset masks, OA reset mask/reset, GDS clock/enhancement controls, OA CGPG restore selectors, compute max wave ID, CS/GFX context-switch status and counters, VS/PS/GS context-switch counters and index, and `GDS_MEMORY_CLEAN`. These fields partition GDS, global wave sync, and ordered append resources per VMID, reset or clean resources, expose context-switch read/write activity, and control GDS memory cleanup.
- The beginning of `addressBlock: gc_gfxdec0`: `DB_RENDER_CONTROL` and `DB_COUNT_CONTROL`. These depth-buffer fields control depth/stencil clear/copy/decompress/resummarize behavior, pixel-shader invocation disable, Z-pass/Z-fail/stencil/depth-fail counting, sample rate, and slice enables.

Field naming is hardware-descriptive. `*_BASE_ADDR_*`, `*_ADDR_*`, and `*_POLL_ADDR_*` fields carry aligned GPU addresses; `*_RPTR` and `*_WPTR` fields carry queue pointers; `DOORBELL_*` fields map queue notification; `ACTIVE`, `MAPPED`, `IDLE`, `STATUS`, `FINISH`, `HIT`, and `INFLIGHT_COUNT` fields expose live hardware state; `START`, `RESET`, `CLEAR`, `DEQUEUE_REQ`, and `SUSPEND_ENABLE` fields trigger state transitions; `RSVD` and `UNUSED` fields identify bits that consumers should not repurpose.

## Control Flow

This header has no runtime control flow. Runtime behavior is implemented by driver and firmware code that includes the generated offset and shift/mask headers:

1. ASIC-specific code selects the GC 10.3 register namespace and includes `gc_10_3_0_offset.h` plus `gc_10_3_0_sh_mask.h`.
2. Driver paths choose a register offset such as `mmCP_HQD_PQ_CONTROL`, `mmCP_GFX_HQD_CNTL`, `mmGDS_VMID0_BASE`, or `mmTCP_WATCH0_CNTL`.
3. The code composes or decodes register values with the macros in this chunk, often using `REG_SET_FIELD` or direct shift/mask operations for MQD memory images.
4. MMIO helpers or MQD writes apply the value while higher-level driver code serializes access with GRBM/SRBM selection, reset state, queue ownership, firmware handoff, or power-management sequencing.

Representative consumer flows in this tree include `gfx_v10_0.c` building graphics and compute MQDs with `CP_GFX_HQD_CNTL`, `CP_RB_DOORBELL_CONTROL`, `CP_HQD_PQ_DOORBELL_CONTROL`, `CP_MQD_CONTROL`, and `CP_HQD_PQ_CONTROL`; GDS VMID initialization clearing `GDS_VMID0_BASE/SIZE`, `GDS_GWS_VMID0`, and `GDS_OA_VMID0`; KFD MQD managers setting `CP_HQD_PQ_CONTROL__QUEUE_SIZE`, `RPTR_BLOCK_SIZE`, `NO_UPDATE_RPTR`, `SLOT_BASED_WPTR`, `QUEUE_FULL_EN`, `PRIV_STATE`, and `KMD_QUEUE`; and KFD debug paths programming TCP watch registers.

The macros do not encode valid ordering. Queue setup still requires correct MQD zeroing/restoration, base-address alignment, ring pointer initialization, doorbell programming, GRBM selection, queue activation/dequeue sequencing, and GPU reset/suspend handling. Similarly, GDS resource programming, TCP watchpoint updates, SPI queue resets, power telemetry controls, and DB render/count changes depend on hardware-defined ordering outside this header.

## State And Persistence Behavior

This file stores no software state and persists nothing. It describes hardware state exposed through GC 10.3 registers.

The represented state is highly stateful in hardware:

- Queue state persists in CP MQD/HQD registers and in MQD memory images until reprogrammed, overwritten by firmware, or lost/reset by GPU reset and power events.
- Doorbell and ring-pointer registers bridge CPU-visible queues, writeback memory, and CP scheduling state; stale base addresses, VMID fields, or pointer fields can redirect hardware queue traffic.
- Suspend, dequeue, preempt, idle, active, mapped, in-flight, and status fields are live hardware state rather than ordinary durable configuration.
- GDS/GWS/OA VMID windows and reset/clean bits define per-VMID access to scarce global resources; initialization commonly clears non-firmware VMID access and relies on firmware or later queue setup to re-enable valid allocations.
- TCP watchpoint and CP DMA watchpoint state can affect debugging and memory-fault observability for selected VMIDs and address windows.
- DIDT/CAC/EDC/throttle controls describe power and reliability telemetry/control state that may be firmware-owned and power-state-sensitive.
- DB render/count registers affect graphics pipeline behavior and counters for active draws.

The macros do not mark fields as read-only, write-only, write-one-to-clear, self-clearing, sticky, reserved, shadowed in an MQD, or firmware-owned. Consumers must preserve unrelated fields on read-modify-write paths and respect the access semantics from the ASIC register specification.

## Dependencies And Integration Points

Direct dependency:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_offset.h` for the corresponding `mm*` register offsets and base indices.

Known direct include users of this GC 10.3.0 shift/mask header in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10_3.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_sdma.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_2.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_1.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/vangogh_ppt.c`

Broader integration points include:

- AMDGPU graphics ring and compute ring initialization, reset recovery, suspend/resume, and MQD backup/restore.
- AMDKFD process queue creation, debug trap/watchpoint support, VMID setup, and hardware scheduler or MES interactions.
- GDS/GWS/OA allocation and cleanup for graphics, compute, and firmware-owned VMIDs.
- CP queue doorbells, EOP queues, indirect buffers, context-save areas, dequeue/preempt handling, and DDID tracking.
- SPI queue reset, wave debug/trap controls, resource-reservation controls, and shader resource limits.
- TCP watchpoints and perf-counter filtering used by debugging, profiling, and validation.
- Power-management and firmware paths using DIDT, CAC, EDC, throttle, and hysteresis registers.
- Depth-buffer render/count state used by clear/decompress/copy and z/stencil count paths.

## Risks And Edge Cases

- Header/offset pairing is critical. Using these `gc_10_3_0_sh_mask.h` fields with a different GC offset header can compile cleanly while programming the wrong register bits.
- The constants are untyped and carry no access semantics. A field that looks writable may actually be read-only, write-one-to-clear, self-clearing, firmware-owned, or reserved.
- Queue fields are sequencing-sensitive. Wrong `QUEUE_SIZE`, `RB_BUFSZ`, `RB_BLKSZ`, `RPTR_BLOCK_SIZE`, base address alignment, VMID, `PRIV_STATE`, `KMD_QUEUE`, `NO_UPDATE_RPTR`, `SLOT_BASED_WPTR`, or doorbell offset can cause lost packets, stuck queues, memory corruption, preemption failures, or GPU hangs.
- Several address fields intentionally start at bit 2, 6, 7, 8, or 12 because the hardware stores aligned addresses. Consumers must shift or mask GPU addresses exactly as expected by the register, not as generic byte addresses.
- Many status/action registers mix live status bits with control bits. Blind writes can clear status, retrigger resets, force dequeue/suspend behavior, or preserve stale live bits into an MQD image.
- GDS/GWS/OA VMID programming is resource-partitioning state. Failing to clear or restore the correct VMID windows can leak global data-share access across processes or prevent firmware from saving/restoring needed entries.
- TCP and CP DMA watchpoint registers are VMID and address-window sensitive. Incorrect masks, valid bits, or mode fields can silently miss debug events or trigger on unrelated traffic.
- DIDT/CAC/EDC/throttle fields are power and reliability controls. Driver-side changes must be coordinated with SMU/firmware ownership and power state, or telemetry and throttling behavior can become misleading or unstable.
- Reserved/unused fields are common. ASIC revisions may assign different meanings to those bits, so read-modify-write preservation matters.
- The chunk boundary is artificial: it starts immediately after `CP_SUSPEND_RESUME_REQ` and ends before the rest of `gc_gfxdec0` DB state. Adjacent chunks are required for a complete per-file register map.

## Test Signals

Useful validation is mostly build, static, and hardware behavior coverage:

- Build coverage for AMDGPU, AMDKFD, SDMA, GFXHUB, and SMU paths that include `gc_10_3_0_offset.h` and `gc_10_3_0_sh_mask.h`.
- Generated-header checks that every `__SHIFT` has a matching `_MASK`, masks are aligned to their shifts, fields do not overlap unexpectedly, and register names match `gc_10_3_0_offset.h`.
- Graphics ring and compute ring smoke tests that initialize MQDs, enable doorbells, submit packets, observe read/write pointer movement, idle queues, and recover correctly after reset and suspend/resume.
- KFD queue tests covering user queues, kernel queues, AQL queues, queue full/no-update-pointer modes, dequeue/preempt, EOP handling, and MQD save/restore.
- GDS/GWS/OA tests that verify per-VMID base/size/mask programming, reset behavior, memory clean start/finish, and context-switch counters.
- Debug/watchpoint tests for CP DMA and TCP watch registers using multiple VMIDs and address ranges, confirming expected trap/status behavior and no false positives on unrelated traffic.
- SPI tests that exercise compute queue reset, trap/debug controls, wave context save, and CU resource reservation enable masks.
- Power-management validation for DIDT/CAC/EDC/throttle registers across runtime PM, suspend/resume, and SMU firmware transitions.
- DB render/count tests around depth/stencil clears, copies, decompression/resummarization, zpass/zfail/stencil/depth-fail counts, sample-rate selection, and slice enable fields.
- Regression indicators include stuck or unmapped queues, doorbell misses, non-advancing ring pointers, incorrect queue idle/preempt status, VMID resource leakage, missed watchpoint traps, unexpected throttling telemetry, failed depth/stencil clears, and GPU hangs isolated to GC 10.3 ASICs.
