# Research: subset-b-003505

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/v12_structs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/v12_structs.h

## Purpose
`v12_structs.h` is a GFX12-generation AMDGPU/KFD hardware layout header. It exports C structs whose fields map directly onto MQD (memory queue descriptor) and MES queue descriptor DWORD layouts consumed by CP, MEC, SDMA, and MES firmware/hardware. The file contains no functions and no executable logic; its behavior is in the consumers that allocate these structs in GPU-visible memory, zero or populate selected registers, and submit them through ring/MES queue setup paths.

The declared layouts cover:

- `struct v12_gfx_mqd`, a 512-DWORD graphics MQD used by the GFX ring path.
- `struct v12_sdma_mqd`, a 128-DWORD SDMA queue descriptor with driver-internal `sdma_engine_id` and `sdma_queue_id` occupying the final reserved slots.
- `struct v12_compute_mqd`, a 512-DWORD GFX12.0 compute MQD.
- `struct v12_1_compute_mqd`, a 1024-DWORD GFX12.1 compute MQD with expanded user data, logical XCC/XCP fields, queue connect fields, suspend/DDID/AQL state, and a larger reserved tail.
- `struct v12_1_mes_mqd`, a 1024-DWORD MES-specific GFX12.1 compute-like descriptor used by MES v12.1 rings.

The file guard is `V12_STRUCTS_H_`, but the closing comment says `V11_STRUCTS_H_`; that looks like a stale comment rather than a preprocessing bug.

## Important Types And Layouts
`v12_gfx_mqd` starts with firmware/shadow setup (`shadow_base_lo/hi`, `fw_work_area_base_lo/hi`, `shadow_initialized`, `ib_vmid`), exposes query/checkpoint words (`checksum_lo/hi`, `cp_mqd_query_time_*`, wave count and HQD pointer query fields), task shader control/ring addresses, then the CP GFX HQD block (`cp_mqd_base_addr*`, `cp_gfx_hqd_active`, VMID, queue priority, base/read/write pointers, doorbell control, HQD status/control, MQD control). The tail is mostly reserved padding out to offset 511, with DFWX state at offsets 272-275 and fence address at offsets 510-511. Consumers in `amdgpu/gfx_v12_0.c` use it for graphics ring MQD init and assign `sizeof(struct v12_gfx_mqd)` as the graphics MQD size.

`v12_sdma_mqd` mirrors SDMA RLC queue context registers: ring buffer control/base/rptr/wptr, read-pointer report address, IB control/base/size, doorbell registers, context-save area, scheduler/preempt/mid-command fields, MCU debug and context-switch status, MQD base/control, then reserved padding. The last two DWORDs are explicitly repurposed for driver-internal `sdma_engine_id` and `sdma_queue_id`. `amdgpu/sdma_v7_0.c`, `amdgpu/sdma_v7_1.c`, `amdkfd/kfd_mqd_manager_v12.c`, and `amdkfd/kfd_mqd_manager_v12_1.c` cast MQD memory to this type, initialize it, copy it out to userspace/debug paths, and publish `sizeof(struct v12_sdma_mqd)` as the SDMA MQD size.

`v12_compute_mqd` is the GFX12.0 compute layout. It begins with compute dispatch parameters, program and scratch addresses, resource registers, VMID, static thread management fields, user accumulators, shader checksum, user data 0-15, CP query/connect/save/restore timing state, packet execution status, context-save base, HQD state for persistent queues, EOP buffer state, IQ timer packet template words, SET_RESOURCES packet template words, per-queue doorbell IDs, task/draw control buffer fields, DFWX state, fence address, and 64 GWS value words. `amdgpu/gfx_v12_0.c`, `amdgpu/mes_v12_0.c`, and `amdkfd/kfd_mqd_manager_v12.c` are the primary consumers.

`v12_1_compute_mqd` is not a simple typedef over `v12_compute_mqd`; it reorders and expands early compute state. Notable differences include `compute_current_logical_xcc_id`, `compute_restart_cg_tg_id`, `compute_tg_chunk_size`, `compute_restore_tg_chunk_size`, prescaled dimensions, `tg_counter_id`, user data 0-31, `compute_relaunch2`, suspend/DDID/dequeue/AQL/kd fields, `pm4_target_xcc_in_xcp`, `cp_mqd_stride_size`, `xcc_sync_counter`, DFWX queue connect address, and query/connect timing shifted to offsets 288+. It is consumed by `amdgpu/gfx_v12_1.c` and `amdkfd/kfd_mqd_manager_v12_1.c`.

`v12_1_mes_mqd` is a MES v12.1 descriptor that resembles the GFX12.1 compute MQD but has MES-specific semantic differences: `compute_start_total_lo/hi` in the early dispatch block, `cp_hqd_gfx_control` where the compute path has a suspend stack offset, and query counters at offsets 318-320. `amdgpu/mes_v12_1.c` uses `sizeof(struct v12_1_mes_mqd)` and casts `ring->mqd_ptr` to this type during MES ring setup.

## Control Flow And State Behavior
This header has declarative control flow only: include guard entry, type declarations, include guard exit. Runtime control flow appears in consumers:

- MQD manager code allocates a GPU-visible memory object, casts `cpu_ptr` to the appropriate struct, zeroes it, fills selected fields from `queue_properties`, `mqd_update_info`, doorbell IDs, GPU addresses, VMIDs, and priority policy, then passes the object to hardware or firmware.
- Ring initialization code stores `sizeof(struct v12_*_mqd)` into MQD metadata so later allocation, backup, restore, and debugging paths copy exactly the expected layout.
- MES paths use compute-like descriptors as persistent command processor state for MES-managed rings.

State is persisted in the MQD memory itself, not in this header. Many fields are state snapshots or hardware-owned status words: read/write pointers, query timestamps, packet execution status, save/restore timestamps, HQD active/VMID/control state, context-save addresses, EOP pointers, DFWX fields, and GWS values. Since these structs are binary contracts, field order and implicit alignment are persistence behavior: changing a field name is lower risk than changing order, type width, or reserved-space count.

## Dependencies And Integration Points
The only direct type dependency is `uint32_t`; users must include this header in a compilation context that has already provided fixed-width integer definitions. The header itself does not include `<linux/types.h>` or `<stdint.h>`.

Observed direct include/integration sites include:

- `amdkfd/kfd_mqd_manager_v12.c` and `amdkfd/kfd_mqd_manager_v12_1.c` for KFD compute/SDMA queue allocation, update, debug copying, and MQD manager sizing.
- `amdgpu/gfx_v12_0.c` and `amdgpu/gfx_v12_1.c` for graphics and compute ring MQD initialization and restore.
- `amdgpu/mes_v12_0.c` and `amdgpu/mes_v12_1.c` for MES ring descriptors.
- `amdgpu/sdma_v7_0.c` and `amdgpu/sdma_v7_1.c` for SDMA queue MQDs.

These structs also depend semantically on AMD hardware register documentation and firmware expectations. The large reserved ranges are integration points too: they keep offsets compatible with hardware packet layouts and future firmware-owned fields.

## Risks And Maintenance Notes
The main risk is ABI/layout drift. The compiler will naturally align `uint32_t` fields to 4 bytes, but any inserted, removed, or widened field changes all subsequent offsets and can break hardware queue restore, firmware parsing, userspace debug dumps, or suspend/resume state. The risk is highest in `v12_1_compute_mqd` and `v12_1_mes_mqd` because they are 1024-DWORD layouts with many similarly named fields and offset shifts from the GFX12.0 layout.

The stale `#endif /* V11_STRUCTS_H_ */` comment can mislead reviewers during generation or auditing, although it does not change compilation. The `v12_sdma_mqd` comments around `reserved_71` through `reserved_78` show incorrect offset numbers restarting at 0-7; if tooling or human review relies on comments rather than actual field order, this can cause bad offset assumptions. The file also has no compile-time `static_assert` coverage for expected struct sizes or offsets.

Because several fields represent GPU addresses split into low/high DWORDs, consumers must provide correct address alignment and lower/upper word splitting. Doorbell IDs, queue priorities, VMIDs, and CP_HQD state are security- and isolation-sensitive; incorrect values can break queue scheduling or cross-process isolation.

## Test Signals
Useful validation signals are build-level and hardware/driver behavior rather than unit tests inside this header:

- Compile all direct consumers so missing `uint32_t`, renamed fields, or changed types are caught.
- Add or preserve `static_assert(sizeof(struct v12_gfx_mqd) == 512 * 4)`, `sizeof(struct v12_compute_mqd) == 512 * 4`, `sizeof(struct v12_sdma_mqd) == 128 * 4`, and `sizeof(struct v12_1_compute_mqd) == sizeof(struct v12_1_mes_mqd) == 1024 * 4` in an appropriate C consumer or layout test.
- Add offset assertions for hardware-sensitive fields used by consumers: `cp_hqd_pq_base_lo`, `cp_hqd_pq_wptr_lo`, `cp_hqd_pq_doorbell_control`, `pm4_target_xcc_in_xcp`, `cp_mqd_stride_size`, `dfwx_*`, SDMA ring/IB/doorbell fields, and MES-only `compute_start_total_*`.
- Runtime smoke signals are successful GFX/compute/SDMA ring init, KFD queue creation/destruction, MES ring bring-up, suspend/resume queue restore, preemption, and debugfs MQD dumps that match expected sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/v12_structs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/v9_structs.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/v9_structs.h -->
