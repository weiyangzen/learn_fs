# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/v9_structs.h

## Purpose
`v9_structs.h` is the GFX9-era AMDGPU/KFD hardware layout header for compute, SDMA, and graphics preemption metadata. It exports fixed DWORD layouts used as MQDs and context-save metadata, with no functions or procedural logic. Runtime behavior comes from GFX9 ring and KFD queue-manager code that allocate these layouts in GPU-visible memory, populate selected fields, and let CP/SDMA hardware or firmware read and update them.

The file declares:

- `struct v9_sdma_mqd`, a 128-DWORD SDMA RLC queue descriptor with two driver-internal IDs at the end.
- `struct v9_mqd`, a 512-DWORD compute/graphics MQD used by GFX9 KIQ/MEC/KFD paths.
- `struct v9_mqd_allocation`, a wrapper that appends CPU/GPU-side polling/report/mask words after the MQD.
- `struct v9_ce_ib_state` and `struct v9_de_ib_state`, command-engine and draw-engine indirect-buffer context payloads.
- `struct v9_gfx_meta_data`, a 4 KiB metadata page containing CE/DE payloads and preempted PFP IB base state.

## Important Types And Layouts
`v9_sdma_mqd` captures SDMA ring buffer, indirect buffer, doorbell, context status, CSA, preemption, AQL, minor pointer update, and mid-command data registers. It reserves most of the second half of the 128-DWORD layout and repurposes the final two reserved words for `sdma_engine_id` and `sdma_queue_id`. It is used by KFD and amdgpu SDMA paths including `amdkfd/kfd_mqd_manager_v9.c`, `amdgpu/amdgpu_amdkfd_gfx_v9.c`, `amdgpu/amdgpu_amdkfd_arcturus.c`, and `amdgpu/amdgpu_amdkfd_gc_9_4_3.c`.

`v9_mqd` is the core GFX9 queue descriptor. It starts with compute dispatch parameters (`compute_dispatch_initiator`, dimensions, start coordinates, thread group size), shader program/TBA/TMA addresses, program resource registers, VMID, resource limits, static thread-management registers, restart/relaunch and wave-restore state, and a union that allows offsets 39-42 to be viewed either as `compute_static_thread_mgmt_se4..se7` or newer XCC/chunking fields (`compute_current_logic_xcc_id`, `compute_restart_cg_tg_id`, `compute_tg_chunk_size`, `compute_restore_tg_chunk_size`). It then carries user data 0-15, query/connect/save/restore timestamps, GDS context-switch counters, packet execution status, GDS/context-save/dynamic CU mask addresses, CP HQD persistent queue state, EOP/context-save state, IQ timer packet template words, a second union for reserved words versus `pm4_target_xcc_in_xcp` and `cp_mqd_stride_size`, SET_RESOURCES packet words, queue doorbell IDs 0-15, and reserved padding through DWORD 511.

`v9_mqd_allocation` embeds a `v9_mqd` followed by `wptr_poll_mem`, `rptr_report_mem`, `dynamic_cu_mask`, and `dynamic_rb_mask`. GFX9 ring setup code uses `sizeof(struct v9_mqd_allocation)` rather than plain `v9_mqd` for several graphics/KIQ allocations because the extra fields are addressed with `offsetof()` and used as backing words for polling, reporting, and dynamic masks.

`v9_ce_ib_state` is a 10-DWORD command-engine payload with completion status, constant-engine count, IB offsets, chained IB addresses, and chained IB sizes. `v9_de_ib_state` is a 27-DWORD draw-engine payload with completion/count/offset fields, chained IB state, preamble begin/end offsets, preamble chained IB address state, indirect draw/dispatch bases, GDS backup address, index base address, and sample control. The file comments state that from Vega10 onward the CSA format is shifted to chain-IB-compatible mode.

`v9_gfx_meta_data` is explicitly a 4 KiB page. It places `ce_payload` first with a 4 KiB-alignment note, reserves 54 DWORDs, places `de_payload` with a 64-byte-alignment note, stores `DeIbBaseAddrLo/Hi`, then reserves 931 DWORDs. GFX9 code uses `offsetof(struct v9_gfx_meta_data, ce_payload)` and `offsetof(..., de_payload)` when writing preemption payloads.

## Control Flow And State Behavior
The header itself has no runtime branches, calls, or side effects. Its include guard wraps plain struct declarations. The effective control flow in consumers is:

- Queue managers allocate GTT or GPU-visible memory sized as `v9_mqd`, `v9_sdma_mqd`, or `v9_mqd_allocation`.
- Init/update functions zero the structs, then write dispatch dimensions, program/resource registers, VMIDs, queue priority, ring base/pointers, doorbell controls, EOP/context-save buffers, and AQL controls.
- Backup/restore paths copy the complete MQD allocation around suspend/resume, GPU reset, or queue restore.
- Preemption/context-save code writes CE/DE metadata payloads into the 4 KiB `v9_gfx_meta_data` page at compile-time offsets.

State persists in the allocated descriptors and metadata pages. Many fields are hardware-owned or firmware-updated after initialization: read/write pointers, status words, timestamps, save/restore endpoints, EOP pointers, GDS and context-save state, packet execution state, and IB completion metadata. The reserved fields preserve binary offset stability and cannot be treated as ordinary unused memory without checking hardware/firmware contracts.

## Dependencies And Integration Points
The header requires `uint32_t` from an include context outside this file. It does not include fixed-width type headers itself.

Observed integration points include:

- `amdkfd/kfd_mqd_manager_v9.c`, which casts MQD memory to `v9_mqd`/`v9_sdma_mqd`, initializes and updates KFD queues, copies MQDs out for debug, and sets manager `mqd_size`.
- `amdgpu/gfx_v9_0.c` and `amdgpu/gfx_v9_4_3.c`, which allocate `v9_mqd_allocation`, initialize graphics/KIQ/MEC MQDs, preserve MQD backups, and use `offsetof()` to address appended dynamic mask fields.
- `amdgpu/amdgpu_amdkfd_gfx_v9.c`, `amdgpu/amdgpu_amdkfd_arcturus.c`, and `amdgpu/amdgpu_amdkfd_gc_9_4_3.c`, which reuse the GFX9 MQD and SDMA layouts for KFD interop on multiple GFX9-family variants.
- GFX9 preemption and metadata code in `amdgpu/gfx_v9_0.c`, which uses `v9_ce_ib_state`, `v9_de_ib_state`, and `v9_gfx_meta_data` sizes and offsets when saving/restoring CE/DE IB state.

The layout is semantically coupled to GFX9 hardware packets, CP/MEC/SDMA register layout, queue scheduling policy, doorbell aperture layout, and context-save firmware behavior.

## Risks And Maintenance Notes
The dominant risk is binary layout drift. `v9_mqd` and `v9_sdma_mqd` are consumed with raw casts, `sizeof`, `memcpy`, and `offsetof`; changing field order or size breaks hardware-visible offsets. `v9_mqd_allocation` is especially sensitive because consumers take offsets of appended fields after the embedded MQD. Any size change in `v9_mqd` moves `dynamic_cu_mask` and `dynamic_rb_mask`.

The anonymous unions in `v9_mqd` intentionally alias old reserved/static-thread fields with newer XCC/chunking and stride fields. Code must choose the right interpretation for the target ASIC and firmware. Writing both interpretations as independent state would corrupt the same DWORDs.

Address fields are split into low/high 32-bit words and frequently point to GPU-visible buffers. Bad splitting, alignment, or VMID assignment can produce queue hangs or isolation failures. Doorbell control and queue priority fields are scheduler-sensitive. The CE/DE metadata page has explicit alignment constraints; incorrect placement can break preemption recovery.

Like the v12 header, this file lacks local `static_assert` checks for expected sizes or key offsets. It relies on downstream compile coverage and hardware testing.

## Test Signals
Useful tests and signals include:

- Compile all direct consumers after any layout change to catch missing or renamed fields.
- Assert `sizeof(struct v9_sdma_mqd) == 128 * 4`, `sizeof(struct v9_mqd) == 512 * 4`, and `sizeof(struct v9_gfx_meta_data) == 4096` in a layout-test or consumer file.
- Assert offsets for appended allocation fields in `v9_mqd_allocation`, especially `dynamic_cu_mask` and `dynamic_rb_mask`, because graphics code addresses those with `offsetof`.
- Assert offsets for `cp_hqd_pq_base_lo`, `cp_hqd_pq_doorbell_control`, `cp_hqd_pq_wptr_lo`, `queue_doorbell_id0`, `pm4_target_xcc_in_xcp`, `cp_mqd_stride_size`, and SDMA ring/doorbell/IB fields.
- Runtime smoke signals are successful GFX9 ring init, KIQ/MEC queue bring-up, KFD queue creation/destruction, SDMA queue operation, GPU reset/suspend-resume MQD restore, and preemption tests that exercise CE/DE metadata save and restore.
