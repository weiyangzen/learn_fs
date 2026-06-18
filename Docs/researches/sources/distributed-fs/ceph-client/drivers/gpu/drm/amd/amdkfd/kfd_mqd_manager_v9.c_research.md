# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v9.c

Purpose: implements MQD management for GFX9, including special CWSR control-stack allocation, VRAM-backed MQDs for selected IPs, SDMA descriptors, HIQ handling, and multi-XCC variants for GFX9.4.3/9.4.4/9.5.0.

Important APIs/types/functions: `mqd_manager_init_v9` builds managers for CP, HIQ, DIQ, and SDMA. Key helpers include `mqd_stride_v9`, `mqd_on_vram`, `allocate_mqd`, `init_mqd`, `load_mqd`, `update_mqd`, `get_wave_state`, `get_checkpoint_info`, checkpoint/restore helpers, SDMA init/update/checkpoint/restore, HIQ init/destroy, and GFX9.4.3 multi-XCC init/update/load/destroy/wave-state/checkpoint/restore helpers.

Control flow: for compute queues with CWSR, allocation creates an enlarged buffer with MQD in the first GPU page and the control stack after it, using special amdgpu kernel memory allocation and VRAM/GTT domain selection. Init programs GFX9 MQD defaults, queue size/base/rptr/wptr/EOP/VMID, AQL flags, CWSR save area fields, trap-present bit, CU masks, priority, and optional GWS SIMD distribution. Wave-state reads copy a header plus control-stack bytes from the MQD-adjacent stack. GFX9.4.3-style devices replicate MQDs per XCC, update per-XCC CWSR base addresses, assign logical XCC IDs, flush HDP if MQDs are in VRAM, and load/destroy each XCC through KGD. HIQ multi-XCC paths use shared HIQ MQD slices and unmap each XCC. SDMA paths program RB control/base/rptr/doorbell, dummy register, engine/queue IDs, and switch-inside-IB.

State and persistence: MQD memory stores queue state, CWSR fields, control-stack contents, doorbell IDs, and per-XCC stride metadata. `current_logical_xcc_start` advances on multi-XCC init/restore. `queue_doorbell_id0` is cleared after preemption-failure checks.

Dependencies/integration: depends on v9 structs/masks, amdgpu kernel memory allocation/free, HDP flush, DQM XCC masks/logical counters, shared MQD helpers, KFD2KGD HQD callbacks, user copy APIs, and debugfs.

Risks: this is one of the most delicate MQD files. The enlarged MQD/control-stack allocation must preserve 4K boundaries and memory attributes. Multi-XCC stride and checkpoint buffer math must match user ABI and allocation size. VRAM-backed MQDs require HDP flushes for CPU writes to become visible. Test signals include CWSR allocation and wave-state copying, checkpoint/restore with multiple XCCs, HIQ per-XCC load/unmap, GWS update flag behavior, VRAM MQD paths on 9.4.3/9.5.0, SDMA restore, and preemption-failure doorbell clearing.
