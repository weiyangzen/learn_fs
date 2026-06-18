# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_sh_mask.h lines 12530-15146

## Scope

This chunk is a generated AMD GC 12.0.0 shift/mask register-header segment. It contains C preprocessor constants only: each hardware register field is represented by a `__SHIFT` value and a matching `__MASK` value used by AMDGPU register helpers to compose or decode 32-bit register values. There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or executable branches in this range.

The selected lines begin in the middle of the command processor DDID control family, with `CP_DDID_CNTL` field masks immediately preceding the `CP_GFX_DDID_*` counters. The chunk then covers graphics HQD/MQD queue state, compute HQD/MQD queue state, CP DMA watch/debug controls, CP busy/UTCL1/reset controls, graphics-draw context registers, CP ME/MEC reset and halt controls, unmapped queue tracking, PF-only HPD/GCR controls, GFXU CP counters and scratch/atomic/append/DMA registers, ME coherence controls, RLC GPM counters, GRBM instance selection, and VGT/GE draw and primitive fields. It ends at the `GE_GS_FAST_LAUNCH_WG_DIM` comment; that register's field definitions continue in the next adjacent chunk.

Although the repository path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata for the GC 12.0.0 graphics IP and is not Ceph filesystem code.

## Purpose

`gc_12_0_0_sh_mask.h` supplies the bit layouts for GC 12.0.0 registers. Driver code pairs these masks with register addresses from the matching `gc_12_0_0_offset.h` header and generated/default values used by GC 12 runtime code. Consumers normally use `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15`, `RREG32_SOC15`, KFD queue loading code, command-packet emission, or debug/perf code so register fields can be packed and decoded without hand-coded bit positions.

This chunk is centered on queue execution and draw/dispatch plumbing:

- Graphics CP queue state: DDID counts, HPD status/control/fence values, MQD base/control, GFX HQD active/VMID/priority/quantum/ring base/read/write pointers, write-pointer polling, doorbells, dequeue/mapped state, queue-manager policy, HQ status/control, and GFX HQD-to-MQD handshakes.
- Compute CP queue state: HPD UTCL1 controls/errors, compute MQD base/control, compute HQD active/VMID/persistent state/priority/quantum/PQ/IB/EOP/context-save/GDS/error/AQL/DDID/dequeue fields.
- CP debug and diagnostic state: DMA watch address/mask/control sets, watch status, PFP/MEC JT status, busy hysteresis, doorbell clear/hit vectors, ring active/status, RCIU CAM data phases, GPU timestamp offset, SDMA completion and checksum/status fields, CP soft reset and CPC graphics controls.
- Per-draw graphics context state: coherence destination bases, perfmon context enable, pipe/ring/VMID context registers, VGT DMA/draw/event/tessellation/shader-stage/streamout fields, and reserved context/config registers.
- PF/VF and PF-only CP/GCR control state: MEC/ME reset and halt controls, unmapped queue bitmaps and doorbell status, PF/VF GRBM graphics control, CP fetcher/DFY data path, PF-only HPD ROQ/status, GCR general/target/command/spare controls, and PMM interrupt/flush controls.
- GFXU CP user-facing registers: EOP done address/data/fence, pipe statistics address/control, many 64-bit pipeline invocation counters, scratch registers and scratch atomics, append/fence address/data, CP atomic preop registers, CP ME memory copy/DMA source/destination/command fields, wait timeout, DMA controls, IB/preamble offsets, command buffer sizes, draw/dispatch/index indirect addresses, sample status, and ME coherence commands.
- Late graphics register families: RLC GPM performance counters, `GRBM_GFX_INDEX` broadcast/instance selection, primitive/index/count registers, GE throttling/control/user VGPR/stereo/VRS fields, and primitive ID reuse control.

## Important APIs, Types, And Macros

There are no callable APIs or C types. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- Register address symbols live in the companion offset header, commonly as `reg...` or `mm...` names matching these register names.
- AMDGPU callers use the masks through helpers such as `REG_SET_FIELD` and `REG_GET_FIELD`; direct bit tests also occur for single-bit status fields such as `CP_HQD_ACTIVE__ACTIVE_MASK`.

The major macro families in this slice are:

- `CP_GFX_DDID_*` and `CP_HQD_DDID_*`: inflight, read pointer, write pointer, and delta report count fields for DDID accounting on graphics and compute HQDs.
- `CP_GFX_HPD_*`, `CP_HPD_*`, `CP_HPD_MES_ROQ_OFFSETS`, and `CP_HPD_ROQ_OFFSETS`: queue slot status, mapped queue selection, suspend/freeze/force controls, OSPRE fence address/data fields, and request-offset layout.
- `CP_GFX_MQD_*`, `CP_GFX_HQD_*`, `CP_MQD_*`, and `CP_HQD_*`: MQD/HQD base addresses, active bits, VMID, priority, quantum, persistent state, ring/PQ base and pointer registers, doorbell controls, PQ/IB/EOP controls, context-save state, GDS resource state, AQL controls, dequeue request/status, and error status.
- `CP_RB_*` and `CP_HQD_PQ_*`: ring buffer and packet queue write-pointer polling, doorbell offset/enable/hit/source/drop fields, buffer sizing, block sizing, privilege/KMD/TMZ/cache controls, and read/write pointer report addresses.
- `CP_DMA_WATCH{0..3}_*` and `CP_DMA_WATCH_STAT*`: watchpoint address/mask/control and status fields for CP DMA diagnostics.
- `CP_CPC_*`, `CP_CPF_*`, `CP_CPG_*`, `CP_SD_CNTL`, and `CP_SOFT_RESET_CNTL`: busy hysteresis, UTCL1 status, soft reset, VMID check, SDMA command checksum, ECC/fault-status forwarding, and CPC graphics enable/status controls.
- `COHER_DEST_BASE*`, `CP_ME_COHER_*`: coherence destination base, size, control, and status fields for CP ME coherence operations.
- `VGT_*` and `GE_*`: draw initiator, DMA index base/size/type, event initiator/address, shader-stage enablement, tessellation parameters/distribution, LS/HS config, primitive type, index type, primitive/index/instance counts, geometry throttling, GE control, user VGPRs, stereo, primitive ID, and VRS fields.
- `CP_MEC_CNTL` and `CP_ME_CNTL`: reset, disable, invalidate, halt, and step fields for MEC/ME/PFP/CE pipelines.
- `CP_UNMAPPED_QUEUE0..63`, `CP_UNMAPPED_DOORBELL`, and `CP_UNMAPPED_QUEUE_BANK*`: unmapped queue and doorbell status bitmaps used by queue management and virtualization paths.
- `GCR_GENERAL_CNTL`, `GCR_TARGET_DISABLE`, `GCR_CMD_STATUS`, and `GCR_SPARE`: GCR/UTCL2 control, target disable/status, command/error/nack status, TLB shootdown VMID, and credit/spare fields.
- `CP_EOP_*`, `CP_PIPE_STATS_*`, `CP_VGT_*_COUNT_*`, `CP_PA_*_COUNT_*`, `CP_SC_*_COUNT_*`: EOP/fence writeback and 64-bit pipeline statistics counters.
- `SCRATCH_REG*`, `SCRATCH_REG_ATOMIC`, and `SCRATCH_REG_CMPSWAP_ATOMIC`: scratch storage plus immediate/id/op encoding for scratch atomic operations.
- `CP_APPEND_*`, `CP_ATOMIC_PREOP_*`, `CP_PFP_ATOMIC_PREOP_*`, and `CP_ME_ATOMIC_PREOP_*`: append/fence memory address/data selection and CP atomic pre-operation fields.
- `CP_DMA_*`, `CP_PFP_IB_CONTROL`, `CP_PFP_LOAD_CONTROL`, `CP_SCRATCH_*`, `CP_RB_OFFSET`, `CP_IB*_OFFSET`, `CP_IB*_PREAMBLE_*`, `CP_*_CMD_ADDR_*`, and command-buffer size/base fields: packet DMA, indirect-buffer, scratch, preamble, and command-buffer plumbing.
- `RLC_GPM_PERF_COUNT_0/1` and `GRBM_GFX_INDEX`: performance event selection by feature/SE/SA/WGP plus GRBM targeted/broadcast register selection.

## Control Flow

This header has no runtime control flow. Its only direct behavior is compile-time macro substitution.

The implied runtime flow is in AMDGPU and KFD consumers:

1. Select the GC 12.0.0 register headers for the active ASIC generation.
2. Choose a register address from `gc_12_0_0_offset.h` or an SOC15 `reg...` symbol.
3. Read an existing register value or start from a generated default.
4. Use the `__SHIFT`/`__MASK` pairs, usually through `REG_SET_FIELD` or `REG_GET_FIELD`, to pack a field value or extract status.
5. Write the value to hardware, store it in an MQD image, emit it into a command path, or use it while decoding status/debug state.

The graphics queue setup path in `gfx_v12_0.c` is representative. `gfx_v12_0_cp_gfx_set_doorbell()` reads `regCP_RB_DOORBELL_CONTROL`, updates `CP_RB_DOORBELL_CONTROL.DOORBELL_OFFSET` and `DOORBELL_EN`, and writes doorbell range registers. `gfx_v12_0_cp_gfx_resume()` programs ring buffer size, read/write pointers, write-pointer poll addresses, ring base, active state, and then starts the graphics CP. `gfx_v12_0_gfx_mqd_init()` fills a `v12_gfx_mqd` image with `CP_GFX_MQD_CONTROL`, `CP_GFX_HQD_VMID`, `CP_GFX_HQD_QUEUE_PRIORITY`, `CP_GFX_HQD_QUANTUM`, `CP_GFX_HQD_CNTL`, and `CP_RB_DOORBELL_CONTROL` fields from this chunk before the queue is loaded.

The compute queue setup path uses the compute HQD side of this chunk. `gfx_v12_0_compute_mqd_init()` builds a `v12_compute_mqd` with EOP base/control, PQ doorbell control, MQD base/control, PQ base/control, read-pointer report and write-pointer poll addresses, VMID, persistent state, IB control, queue priority, active state, and static thread masks. `gfx_v12_0_kiq_init_register()` then writes the MQD/HQD register image to selected hardware queue registers, optionally dequeues an active queue, resets PQ pointers, and reactivates the HQD.

KFD queue-management code has the same conceptual flow for user queues: select a MEC/pipe/queue, write the range from `CP_MQD_BASE_ADDR` through HQD registers, enable doorbell logic, reconstruct a 64-bit write pointer when needed, start the EOP fetcher by setting `CP_HQD_EOP_RPTR.INIT_FETCHER`, and set `CP_HQD_ACTIVE.ACTIVE`. Queue teardown writes `CP_HQD_DEQUEUE_REQUEST` and polls `CP_HQD_ACTIVE__ACTIVE_MASK` until the queue drains or resets.

For GRBM selection, wave/debug paths write `GRBM_GFX_INDEX` with targeted instance/SA/SE fields, execute a command such as `SQ_CMD`, then restore broadcast writes by setting `INSTANCE_BROADCAST_WRITES`, `SA_BROADCAST_WRITES`, and `SE_BROADCAST_WRITES`. That flow makes the broadcast bits in this chunk critical for avoiding accidental per-instance targeting after debug operations.

Draw, DMA, GCR, perf, and counter fields are generally programmed by command streams, golden-register tables, debugfs/perf tooling, reset paths, and firmware-mediated paths. This header does not encode required ordering, polling, clear-on-read, write-one-to-clear, latching, or reset sequencing; those rules live in AMDGPU engine code, firmware interfaces, and hardware programming guides.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe GPU register fields whose state is owned by hardware, firmware, command streams, and AMDGPU runtime programming.

MQD/HQD and ring fields are persistent queue execution state. Active bits, VMID, queue priority, quantum, buffer base/size, read/write pointers, pointer report addresses, write-pointer poll addresses, doorbells, EOP base/control, IB base/control, context-save offsets/sizes, GDS allocation, and AQL controls remain live until reprogrammed, dequeued, reset, or lost through suspend/resume or GPU reset. Driver code also persists queue images in MQD memory and backup copies, so mask mistakes can survive across restore paths.

Doorbell fields are externally visible synchronization state between CPU/KFD/user queues and the CP. Incorrect offset, enable, source, or range programming can send writes to the wrong queue, drop writes through BIF/drop policy, miss user submissions, or make a disabled queue appear active. `DOORBELL_HIT` and unmapped doorbell/queue registers are diagnostic/status state and may have hardware-specific clear behavior outside this header.

Pointer and address fields often use aligned, shifted, or truncated addresses. Examples include MQD base addresses masked with low bits cleared, HQD/PQ base values derived from GPU addresses shifted by 8, read-pointer report and write-pointer poll addresses aligned to dword boundaries, EOP/context-save addresses, CP append/DMA/source/destination addresses, and ME coherence base/size fields expressed in 256-byte units. Treating all fields as unshifted byte addresses is unsafe.

CP reset/halt/invalidate controls and GCR controls have immediate side effects. `CP_MEC_CNTL`, `CP_ME_CNTL`, `CP_SOFT_RESET_CNTL`, `CP_CPC_GFX_CNTL`, `GCR_GENERAL_CNTL`, `GCR_TARGET_DISABLE`, `GCR_CMD_STATUS`, and `PMM_CNTL2` can stop engines, invalidate caches, alter target routing, trigger TLB shootdowns, disable interrupts, or change request credits. Full-register writes must preserve reserved or unrelated fields unless a documented reset sequence requires otherwise.

Pipeline statistics and performance counters are hardware accumulation state. Low/high counter pairs can be torn if read without a hardware-defined latch/snapshot sequence, and obsolete counter fields such as `CP_SC_PSINVOC_COUNT1_*__OBSOLETE` should not be treated as valid telemetry. RLC GPM counter selection persists while counters are enabled and can perturb or misattribute measurements if feature/SE/SA/WGP/event fields are wrong.

Draw context fields such as VGT DMA base/size/type, draw initiator, shader-stage enablement, tessellation parameters, streamout opaque state, primitive type/index/count, GE throttle/control, user VGPRs, stereo, primitive ID, and VRS are active graphics pipeline state. They are normally command-stream driven and persist in context until overwritten or reset. Bad masks can cause malformed draws, wrong topology, incorrect tessellation/streamout behavior, broken primitive restart, or hangs.

Scratch, append, atomic, DMA, and ME coherence fields can write GPU memory. Incorrect address, size, command, cache-policy, or data-selection fields can corrupt memory, signal the wrong fence, report stale EOP completion, or leave caches incoherent. Many diagnostic/status fields are sticky or latched by hardware; this generated header does not document how to clear them.

## Dependencies And Integration Points

This chunk depends on the generated GC 12.0.0 register set remaining internally synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_offset.h` provides matching register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_default.h`, where present for this generated family, provides default/reset values that runtime code uses before applying these masks.
- AMDGPU register helpers in the driver tree provide field packing/extraction and MMIO access.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v12_0.c` consumes many of these fields for graphics ring setup, async graphics MQD initialization, compute MQD initialization, KIQ register programming, doorbell range setup, GRBM selection, reset/resume, and firmware/cache operations.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v11.c` is a close KFD queue-management consumer pattern for HQD load, active polling, dequeue, and GRBM index restore; the same HQD macro families are carried into GC 12 paths.
- Firmware and command processor microcode consume MQD/HQD images and command-stream register writes whose layout is defined by these masks.

Integration points include graphics ring resume/start, async graphics queues, compute queue creation/destruction, KIQ/HIQ queue programming, KFD user queue load/unload, SR-IOV PF/VF queue tracking, doorbell routing, EOP/fence signaling, writeback pointer polling, context save/restore, GDS/GWS allocation, AQL dispatch handling, CP DMA and copy operations, indirect buffer preambles, draw and dispatch indirect addresses, pipeline statistics, RLC/GPM perf monitoring, GCR/TLB shootdown and target routing, GRBM per-instance access, wave control/debug, and hang/reset diagnostics.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong shift or mask compiles cleanly but writes the wrong hardware bits or decodes misleading queue/status state.
- This range starts and ends mid-family. It begins after the `CP_DDID_CNTL` comment and field shifts and ends at the `GE_GS_FAST_LAUNCH_WG_DIM` comment before the actual field definitions. Adjacent chunks are required for complete per-file conclusions.
- Graphics and compute HQD families are similar but not identical. Reusing `CP_GFX_HQD_*` assumptions for `CP_HQD_*`, or vice versa, can break queue setup because PQ, EOP, IB, AQL, context-save, and error fields differ.
- Address fields have mixed alignment contracts. Some masks clear low two bits, some use 8-bit-shifted queue bases, and coherence fields use 256-byte units. Incorrect packing can point hardware at the wrong MQD, ring, EOP buffer, writeback slot, DMA address, fence, or coherence range.
- Queue-size fields encode powers of two in register-specific ways. Runtime code derives values with `order_base_2()` and comments such as EOP size being `2^(EOP_SIZE+1)` dwords; wrong masks produce queues that wrap, overflow, or starve.
- Doorbell offsets and ranges are high risk. Off-by-one or missing shifts can route user submissions to the wrong engine/queue or make a queue unreachable.
- Active/dequeue polling depends on exact status bits. If `CP_HQD_ACTIVE__ACTIVE_MASK`, dequeue request/type bits, or HQ status bits are wrong, teardown can time out, fail to drain waves, or assume an active queue is idle.
- GRBM targeting must be restored after per-instance operations. Missing broadcast bits in `GRBM_GFX_INDEX` can leave subsequent register writes aimed at only one SE/SA/instance.
- GCR and CP reset/halt bits have side effects, and many fields are PF-only or PF/VF scoped. Writing them from the wrong virtualization context can be ineffective or disruptive.
- GFXU counters and status fields include obsolete or split low/high pairs. Consumers need latch/ordering rules not present in the header to avoid torn reads or bogus telemetry.
- Scratch atomic, append, DMA, and ME coherence commands can write memory or signal fences. Incorrect field widths for commands, cache policy, fence size, or addresses can corrupt memory or hide completion/fault information.
- Reserved fields appear throughout this generated region. Read-modify-write paths should preserve reserved and unrelated bits unless the hardware programming sequence says otherwise.

## Test Signals

Useful validation is generated-data consistency, build coverage, and hardware/runtime diagnostics:

- Kernel build coverage for AMDGPU files that include `gc_12_0_0_sh_mask.h`, especially GC 12 graphics, compute/KFD, queue setup, reset/resume, virtualization, debug, and perf paths.
- Mechanical comparison against AMD's authoritative GC 12.0.0 register database to confirm every `__SHIFT` and `__MASK` value in lines 12530-15146.
- Cross-check that all register names in this chunk have matching address macros in `gc_12_0_0_offset.h` and expected defaults in the matching default header where generated.
- Static sanity checks that each mask aligns with its shift, repeated queue/counter families remain structurally consistent, full-width data fields use `0xFFFFFFFFL`, and repeated queue banks/counters are not missing members.
- Graphics ring tests that resume/start the ring, program `CP_RB_DOORBELL_CONTROL`, write/read ring pointers, and verify doorbell submission reaches the expected queue.
- Async graphics MQD tests that initialize `CP_GFX_MQD_CONTROL`, `CP_GFX_HQD_*`, write-pointer poll addresses, doorbell control, queue priority/quantum, and active state, then submit work and recover through suspend/reset.
- Compute/KFD queue tests that create and destroy user queues, load MQD/HQD state, enable doorbells, reconstruct write pointers, start the EOP fetcher, set `CP_HQD_ACTIVE`, dequeue with drain/reset requests, and poll for inactive state without timeouts.
- Doorbell range and unmapped queue tests that exercise valid and invalid user queues, unmapped queue banks, unmapped doorbell bits, and PF/VF behavior.
- GRBM/wave-control tests that select a targeted SE/SA/instance, issue wave/debug commands, then confirm broadcast writes are restored for later register programming.
- CP DMA, scratch atomic, append/fence, and ME coherence tests that write known memory/fence patterns and verify no address truncation, cache-policy, or command-field mistakes.
- Pipeline statistics and RLC GPM perf tests that enable counters, run controlled draw/dispatch workloads, latch/read low/high pairs, and compare monotonic or expected activity.
- Draw-path tests covering primitive type/index type, primitive restart, draw initiator, tessellation config, shader-stage enablement, streamout opaque state, GE throttle/control, stereo, primitive ID, and VRS fields.
- GCR/TLB/reset diagnostics that exercise GCR command status, UTCL2 nack/error fields, CP soft reset, MEC/ME halt/reset/invalidate, and PMM interrupt/flush controls under recovery paths.
- Runtime warning signals include queue activation failures, dequeue/preemption timeouts, stuck EOP fetcher, lost doorbell updates, wrong writeback pointers, VM/UTCL1 errors in `CP_HQD_ERROR`, stale or incorrect pipeline counters, failed CP DMA/fence writes, unexpected GCR nack errors, GRBM writes affecting only one instance, and GPU reset loops after ring or compute queue setup.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002574`. It covers lines 12530-15146 of `gc_12_0_0_sh_mask.h`. The final per-file research should merge this with adjacent chunks to complete the partial `CP_DDID_CNTL` and `GE_GS_FAST_LAUNCH_WG_DIM` families and to place these CP/HQD/GCR/GFXU/VGT/GE definitions in the full GC 12.0.0 register map.
