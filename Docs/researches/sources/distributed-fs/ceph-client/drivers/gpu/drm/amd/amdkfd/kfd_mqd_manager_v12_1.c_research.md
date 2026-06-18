# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v12_1.c

Purpose: implements GFX12.1 MQD management, including multi-XCC compute MQD replication, a GFX12.1-specific CU-mask mapper, metadata queue programming, and updated SDMA register fields.

Important APIs/types/functions: `mqd_manager_init_v12_1` wires queue-type vtables. `mqd_symmetrically_map_cu_mask_v12_1` maps CU masks across the smaller GFX12.1 SE/SH layout and XCC subsets. Core helpers include `allocate_mqd`, base `init_mqd`/`update_mqd`, multi-XCC `init_mqd_v12_1`/`update_mqd_v12_1`/`load_mqd_v12_1`/`destroy_mqd_v12_1`, `get_wave_state_v12_1`, `init_mqd_sdma`, and `update_mqd_sdma`.

Control flow: compute allocation multiplies aligned MQD size by `NUM_XCC` for compute queues. Base init programs GFX12.1 descriptor defaults, preload size 0x63, static masks including `se8`, atomics bit, AQL control, and CWSR fields. Base update rebuilds PQ control, programs queue base, optional metadata queue base/control when metadata size equals four times main queue size, rptr/wptr polling, doorbell, IB/EOP controls, VMID, AQL flags, priority, and active state. Multi-XCC init/update iterates each XCC MQD at `mqd_stride`, adjusts per-XCC CWSR base, sets `compute_current_logical_xcc_id` and `compute_tg_chunk_size` for AQL, and handles PM4 target XCC. Load/destroy iterate `for_each_inst` over `xcc_mask`, passing XCC IDs to KGD. Wave-state retrieval iterates per-XCC context-save areas and reports XCC0 sizes to callers.

State and persistence: per-compute queue state is persisted as one MQD per XCC in a single allocation. `current_logical_xcc_start` is advanced to distribute AQL logical XCC assignment. Metadata queue settings are persisted in MQD KD fields when valid.

Dependencies/integration: depends on GFX12.1 masks, DQM `current_logical_xcc_start`, `NUM_XCC`, XCC masks, KFD2KGD per-XCC load/destroy callbacks, shared MQD helpers, amdgpu SDMA quantum, and debugfs.

Risks: `err` in `destroy_mqd_v12_1` and `load_mqd_v12_1` is not initialized before the XCC loop; if `xcc_mask` were empty, return would be undefined, though normal devices should have at least one XCC. Metadata queue size validation is strict and silently ignores invalid metadata after a warning. CU mapper assumes GFX12.1 topology dimensions fitting `[2][2]`. Test signals include multi-XCC compute creation/load/destroy, metadata queue valid/invalid sizes, CWSR per-XCC addresses, CU-mask mapping, PM4 target XCC, and SDMA queue programming.
