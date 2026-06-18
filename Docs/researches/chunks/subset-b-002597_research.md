# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_sh_mask.h lines 12491-15118

## Scope

This chunk is a generated AMD GC 12.1.0 shift/mask header segment. It contains preprocessor constants only: each `REGISTER__FIELD__SHIFT` macro gives a bit offset, and each `REGISTER__FIELD_MASK` macro gives the corresponding 32-bit field mask. The requested range contains 2,127 `#define` entries across 474 register-name groups.

The span begins mid-register at the final `CP_GFX_HQD_QUE_MGR_CONTROL__DISABLE_MAPPED_QUEUE_IDLE_MSG_MASK` define, then covers CP graphics HQD, CP DMA watchpoints, CP status/error, compute HQD/MQD, graphics context, PF/VF, PF-only, GCR, GFXU, CP DMA, draw/dispatch, coherency, GE/VGT, and the start of MES control/status masks. It ends at the `//CP_MES_IC_OP_CNTL` comment before that register's fields, so adjacent chunks are required for complete per-register and per-file coverage.

This source tree is under a local `ceph-client` mirror, but this file is AMDGPU DRM graphics hardware metadata. It has no Ceph or distributed filesystem behavior.

## Purpose

`gc_12_1_0_sh_mask.h` publishes bit layouts for GC 12.1.0 registers. AMDGPU, KFD, MES, GFXHUB, IMU, SDMA, and SOC code include this header together with `gc_12_1_0_offset.h` so they can compose register values, extract status bits, and keep ASIC-specific field positions out of hand-written driver logic.

This chunk's main purposes are:

- Describe queue-manager, HQD, MQD, doorbell, PQ/IB/IQ/EOP, dequeue, suspend, AQL, dispatch-id, kernel-dispatch, and GDS fields used by compute and graphics queue setup.
- Describe CP DMA watchpoint, DMA command, scratch, append/atomic, indirect-buffer, wait, coherency, fence, and pipeline-statistics fields used by command processor programming and diagnostics.
- Describe CP/CPF/CPG/CPC busy, UTCL1 fault/retry/PRT, fed-error, ring-buffer, SDMA arbitration, soft-reset, ME/MEC control, unmapped queue, PF-only DFY/HPD/GCR, and MES fields used for debug, reset, virtualization, and firmware control.
- Describe graphics context and draw-state fields for VGT/GE, including draw initiator, DMA/index type, shader stages, tessellation, streamout, primitive type, VRS, geometry throttling, user VGPRs, and primitive-id reset.
- Describe GFXU statistics, scratch, EOP done, append/atomic, metadata, indirect draw/dispatch, coherency destination, RLC perf counter, and GRBM index fields.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, callbacks, locks, allocations, or executable branches in this chunk. The exported interface is the generated macro naming contract:

- `REGISTER__FIELD__SHIFT` is the left-shift count used when packing a field value into a register word or after masking/extracting a field.
- `REGISTER__FIELD_MASK` is the bit mask for the field in the register word.
- Address-block comments divide related register groups, including `CHIP_XCD_gfxip_xcc_gfx_cpwd_cpwd_cpphqddec`, `gfxdec0`, `pfvf_cpdec`, `pfvf_grbmdec`, `pfonly_cpdec`, `pfonly_cpphqddec`, `pfonly_gcrdec`, `gfxudec`, and `cprs64dec`.

Important register groups in this range include:

- Queue and descriptor state: `CP_GFX_HQD_IQ_TIMER`, `CP_GFX_HQD_HQ_STATUS0`, `CP_GFX_MQD_CONTROL`, `CP_HQD_ACTIVE`, `CP_HQD_VMID`, `CP_HQD_PERSISTENT_STATE`, `CP_HQD_PQ_CONTROL`, `CP_HQD_PQ_DOORBELL_CONTROL`, `CP_HQD_IB_CONTROL`, `CP_HQD_IQ_TIMER`, `CP_HQD_DEQUEUE_REQUEST`, `CP_HQD_DMA_OFFLOAD`, `CP_HQD_OFFLOAD`, `CP_HQD_HQ_SCHEDULER0`, `CP_HQD_HQ_STATUS0`, `CP_HQD_EOP_CONTROL`, `CP_HQD_CTX_SAVE_CONTROL`, `CP_HQD_ERROR`, `CP_HQD_AQL_CONTROL`, `CP_HQD_AQL_CONTROL_1`, and `CP_HQD_KD_CNTL`.
- Address and pointer fields for queue backing memory: `CP_MQD_BASE_ADDR`, `CP_HQD_PQ_BASE`, read/write pointer report and poll addresses, IB base, EOP base, context-save base, suspend offsets, DDID pointers, AQL dispatch IDs, KD base, EOP done addresses, pipe-stats addresses, append addresses, CP DMA source/destination/command-buffer addresses, IB/ST/DB bases and buffer sizes, metadata base, indirect draw/dispatch addresses, and index base.
- Watchpoint and status fields: four `CP_DMA_WATCH[0-3]` slots, `CP_DMA_WATCH_STAT`, `CP_PFP_JT_STAT`, `CP_MEC_JT_STAT`, busy hysteresis registers, CP fed-error address registers, doorbell clear/status, RCIU CAM phases, timestamp offsets, SDMA request arbitration, UTCL1 status registers, soft-reset fields, HPD UTCL1 error/status, HPD queue status, GCR command/status, and MES exception/control status.
- Graphics frontend fields: `VGT_DRAW_INITIATOR`, `VGT_DMA_INDEX_TYPE`, `VGT_EVENT_INITIATOR`, `VGT_SHADER_STAGES_EN`, `VGT_TF_PARAM`, `VGT_TESS_DISTRIBUTION`, `VGT_LS_HS_CONFIG`, `VGT_PRIMITIVE_TYPE`, `VGT_INDEX_TYPE`, `GE_MULTI_PRIM_IB_RESET_EN`, `GE_GS_THROTTLE`, `GE_CNTL`, `GE_STEREO_CNTL`, `GE_USER_VGPR_EN`, `VGT_PRIMITIVEID_EN`, `GE_VRS_RATE`, and geometry-shader fast-launch dimensions.
- Virtualization and privileged control fields: `CP_UNMAPPED_QUEUE0` through `CP_UNMAPPED_QUEUE63`, `CP_UNMAPPED_DOORBELL`, queue banks, `GRBM_GFX_CNTL`, `CP_DFY_*`, PF-only HPD status/ROQ offsets, and PF-only `GCR_*` controls.
- MES fields at the end of the chunk: program counter start, interrupt routine/vector addresses, `CP_MES_CNTL` reset/active/halt/step bits for four pipes, pipe priorities, interrupt enables/pending state, scratch index/data, instruction pointer, machine scratch/status/EPC/cause/bad-address/IP halves.

Concrete consumers in this source tree include `gfx_v12_1.c`, `mes_v12_1.c`, `amdgpu_amdkfd_gfx_v12_1.c`, `gfxhub_v12_1.c`, `imu_v12_1.c`, `sdma_v7_1.c`, `soc_v1_0.c`, and KFD's `kfd_mqd_manager_v12_1.c`. For example, `kfd_mqd_manager_v12_1.c` packs MQD fields with `CP_HQD_AQL_CONTROL__CONTROL0__SHIFT`, `CP_HQD_PQ_CONTROL__RPTR_BLOCK_SIZE__SHIFT`, `CP_HQD_PQ_CONTROL__UNORD_DISPATCH_MASK`, `CP_HQD_PQ_DOORBELL_CONTROL__DOORBELL_OFFSET__SHIFT`, `CP_HQD_PQ_CONTROL__NO_UPDATE_RPTR_MASK`, `CP_HQD_PQ_CONTROL__SLOT_BASED_WPTR__SHIFT`, `CP_HQD_PQ_CONTROL__QUEUE_FULL_EN__SHIFT`, `CP_HQD_PQ_CONTROL__PRIV_STATE__SHIFT`, and `CP_HQD_PQ_CONTROL__KMD_QUEUE__SHIFT`.

## Control Flow

This header has no direct runtime control flow. Its direct behavior is compile-time macro substitution.

The implied runtime flow in AMDGPU/KFD consumers is:

1. Select the GC 12.1.0 register headers for the active ASIC.
2. Use a register offset macro from `gc_12_1_0_offset.h` and a shift/mask macro from this file.
3. Pack a register word with `FIELD_VALUE << REGISTER__FIELD__SHIFT`, apply `REGISTER__FIELD_MASK`, or extract a status value after an MMIO read.
4. Write, read, or emit the register through SOC15/MMIO helpers, KFD MQD memory layout, command processor packets, firmware interfaces, or reset/debug paths.
5. Higher-level code interprets acknowledgement, error, idle, queue-active, doorbell, pointer, interrupt, or fault fields according to the hardware programming sequence.

Typical sequences using this chunk include KFD MQD construction, HQD queue activation/deactivation, doorbell programming, AQL queue setup, CP/HQD dequeue and suspend/resume, CP DMA command construction, EOP/fence programming, coherency flush range setup, indirect draw/dispatch programming, graphics context emission, CP/ME/MEC/MES reset or halt/step control, and status/error polling. The header does not encode ordering, polling, privilege, read-only/write-one-to-clear, or reset sequencing rules; those live in the driver and hardware documentation.

## State And Persistence Behavior

The macros themselves store no state and persist nothing. They describe fields in hardware-visible state:

- HQD/MQD/PQ/IB/IQ/EOP fields describe live queue configuration and queue progress. Some values are initialized by software or by MQD memory, while others are advanced or latched by CP hardware.
- Doorbell, read/write pointer, dequeue, suspend, dispatch-id, AQL, and KD fields are queue-liveness state. They must be rebuilt or reconciled across queue teardown, process eviction, GPU reset, suspend/resume, and VM reset.
- `CP_HQD_PERSISTENT_STATE`, context-save, suspend, and restore-related fields describe state that bridges queue switches and preemption. Incorrect bits can break wave relaunch, saved control-stack state, or TMZ/QoS behavior.
- UTCL1, DMA watch, fed-error, HPD, GCR, MES exception, and CP error fields are diagnostic or fault state. They may be latched by hardware and may require specific clear or acknowledgement flows not represented in this header.
- Graphics context fields such as VGT/GE/draw/tessellation/index/primitive/streamout state persist until overwritten by command streams, context restore, reset, or power-management reinitialization.
- PF/VF and PF-only fields describe virtualization-visible and privileged state. The macro names do not by themselves enforce access policy.
- MES control, scratch, machine status, EPC, cause, bad-address, interrupt, and pipe-priority fields represent firmware execution state and are sensitive to firmware load, reset, halt/step, and interrupt sequencing.

Because the file is generated metadata, it cannot tell whether a field is read-only, write-only, volatile, clear-on-read, write-one-to-clear, shadowed in an MQD, or safe for read-modify-write. Consumers must follow the relevant GC 12.1.0 programming sequence.

## Dependencies And Integration Points

This chunk depends on AMD's authoritative GC 12.1.0 register database and must stay synchronized with companion generated headers in the same directory:

- `gc_12_1_0_offset.h` supplies the register offsets that pair with these field definitions.
- Other GC 12.1.0 headers supply enumerations or packet definitions used by the same driver code.
- AMDGPU SOC15 helpers and register access macros perform MMIO reads/writes using the offset header and field macros.
- KFD MQD and device-queue managers use the HQD/MQD/AQL/PQ/doorbell fields to build queue descriptors for user-mode compute queues.
- GFX ring, CP DMA, IB, fence, append/atomic, and draw/dispatch paths use the GFXU and CP command fields in this chunk.
- MES and CP firmware control code uses MES reset/active/halt/step, interrupt, scratch, and machine-status fields for firmware bring-up and diagnostics.
- GFXHUB/UTCL1/fault handling paths use the UTCL1 status/error fields and CP fed-error address fields for translation and fault analysis.
- SR-IOV and virtualization paths depend on PF/VF and PF-only naming boundaries for unmapped queues, doorbells, GRBM selection, HPD status, DFY, and GCR controls.

Integration is intentionally low-level. A macro typo, mask drift, or generation mismatch may still compile because these are untyped integer constants, but it can silently alter hardware programming.

## Risks And Edge Cases

- The range starts and ends mid-family. `CP_GFX_HQD_QUE_MGR_CONTROL` is inherited from the previous chunk, and `CP_MES_IC_OP_CNTL` fields are in the next chunk.
- Generated-header drift is the primary risk. Wrong shifts or masks compile cleanly and can program or decode the wrong hardware bits.
- Queue-control fields are high impact. Incorrect `CP_HQD_PQ_CONTROL`, doorbell, active, VMID, EOP, dequeue, AQL, or persistent-state masks can cause stuck queues, missed interrupts, broken preemption, bad MQD restore, or reset recovery failures.
- Address fields often have alignment-defined low bits and limited high-bit masks. Using the wrong mask can truncate addresses or allow invalid low bits in PQ/IB/EOP/context-save/append/DMA/metadata/indirect buffers.
- Some fields are security-sensitive: VMID, privilege, TMZ, scope/cache policy, PF/VF, GCR target disable, unmapped queue, and doorbell fields can affect isolation and memory visibility.
- Repeated families are copy-sensitive: `CP_DMA_WATCH0-3`, `CP_UNMAPPED_QUEUE0-63`, scratch registers, counter low/high pairs, CP DMA ME/PFP pairs, CP append aliases, and MES pipe priority/state fields must keep exact naming and bit layout.
- Aliases and spelling are part of the ABI-like generated namespace. For example, `CP_APPEND_DATA` and `CP_APPEND_DATA_LO` both exist, and `CP_SAMPLE_STATUS__Z_PASS_ACITVE` preserves the generated spelling.
- Status/error fields can be latched or access-sensitive. The header does not distinguish safe polling bits from bits that clear, trigger side effects, or require privileged access.
- Cross-generation similarity is risky. Older GC/GCA headers have similarly named masks but not always identical layouts, especially around HQD queue control, CP DMA command bits, and CP/ME/MES control.

## Test Signals

Useful validation should combine generated-data checks, build coverage, and hardware/runtime tests:

- Build AMDGPU with GC 12.1.0, KFD, MES, GFXHUB, SDMA, and SOC support enabled. Missing or renamed macros should fail in `gfx_v12_1.c`, `mes_v12_1.c`, `amdgpu_amdkfd_gfx_v12_1.c`, `gfxhub_v12_1.c`, `sdma_v7_1.c`, and KFD queue-manager files.
- Mechanically compare this chunk against AMD's GC 12.1.0 register database and companion `gc_12_1_0_offset.h`. Validate both field masks and shift positions.
- Cross-check repeated families for consistency: DMA watch slots, HQD pointer/address pairs, EOP low/high pairs, counter low/high pairs, CP DMA ME/PFP command/address pairs, unmapped queues 0-63, scratch registers, and MES pipe fields.
- Run KFD compute queue creation, AQL dispatch, doorbell, preemption, eviction, restore, and teardown tests. Watch for stuck HQDs, dequeue timeouts, incorrect MQD fields, EOP pointer mismatches, and reset failures.
- Run graphics ring and CP DMA tests covering IB submission, indirect draw/dispatch, append/atomic operations, coherency flushes, fences, and pipeline statistics. Signals include forward ring progress, correct fence completion, no CP fatal errors, and plausible stats.
- Exercise GPU reset, suspend/resume, MES firmware load/reset, and CP/ME/MEC halt or step diagnostics. Relevant signals include expected active/reset bits, no stale firmware exception state, and successful post-reset queue reinitialization.
- Exercise VM fault, UTCL1 status, DMA watchpoint, fed-error, and HPD error paths where hardware is available. Validate captured VMID, queue ID, client, pipe, watch ID, address, and fault/retry/PRT IDs.
- Exercise SR-IOV/PF-VF scenarios for unmapped queue accounting, doorbell clearing, PF-only HPD/GCR/DFY access, and GRBM selection boundaries.
- Run graphics frontend workloads that stress tessellation, geometry, streamout, VRS, indexed/indirect draws, primitive restart, and multi-instance draws. Bad VGT/GE masks usually appear as draw corruption, hangs, or implausible counters.

## Cross-Chunk Notes

The previous chunk should document the beginning of `CP_GFX_HQD_QUE_MGR_CONTROL`; this chunk only contains its final `DISABLE_MAPPED_QUEUE_IDLE_MSG` mask. The next chunk should begin with the `CP_MES_IC_OP_CNTL` fields and continue the MES register block. The final per-file document should merge this report with adjacent chunks before making complete claims about the GC 12.1.0 shift/mask namespace.
