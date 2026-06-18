# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager.c

Purpose: provides generation-independent MQD manager helpers used by per-ASIC MQD manager implementations. It centralizes priority mapping, shared HIQ/SDMA MQD allocation, CU-mask mapping, HQD load/destroy/free helpers, stride helpers, and preemption-failure reporting.

Important APIs/types/functions: `pipe_priority_map` maps KFD queue priorities to CP pipe priorities. `allocate_hiq_mqd`, `allocate_sdma_mqd`, and `free_mqd_hiq_sdma` manage MQDs inside the preallocated HIQ/SDMA MQD region. `mqd_symmetrically_map_cu_mask` maps user CU masks across SE/SH/XCC topology. `kfd_hiq_load_mqd_kiq`, `kfd_destroy_mqd_cp`, `kfd_free_mqd_cp`, `kfd_is_occupied_cp`, `kfd_load_mqd_sdma`, `kfd_destroy_mqd_sdma`, and `kfd_is_occupied_sdma` call the `kfd2kgd` hardware callbacks. `kfd_hiq_mqd_stride`, `kfd_get_hiq_xcc_mqd`, `kfd_mqd_stride`, and `kfd_check_hiq_mqd_doorbell_id` support multi-XCC and diagnostics.

Control flow: generation-specific initializers install these helpers into `struct mqd_manager` vtables. HIQ and SDMA allocations carve offsets from `dev->dqm->hiq_sdma_mqd`; CP MQDs may be freed either through amdgpu kernel memory free or GTT suballocation free based on the backing object. CU mask mapping bounds-checks shader-engine/shader-array dimensions, counts active CUs from amdgpu topology, and symmetrically spreads selected CUs across available SE/SH and XCC instances, using WGP pairs on GFX10+.

State and persistence: mutates `kfd_mem_obj` descriptors, queue properties via vtable users, and hardware HQD state through `kfd2kgd`. It owns no global mutable state except `pipe_priority_map`.

Dependencies/integration: depends on amdgpu topology (`gfx.cu_info`, `gfx.config`), DQM MQD manager arrays, KFD/XCC masks, and `kfd2kgd` hardware callbacks.

Risks: CU-mask mapping has explicit stack-corruption guardrails for unsupported topology sizes; exceeding them leaves no CUs enabled and can hang queues. Shared HIQ/SDMA allocation uses pointer arithmetic on a common BO and must stay aligned with manager sizes and XCC counts. Test signals include CU-mask topology variants, HIQ/SDMA offset calculations, CP/SDMA HQD load/destroy/is_occupied callbacks, and preemption-failure doorbell diagnostics.
