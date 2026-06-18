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
