
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_vi.c

## Purpose
Implements the VI/GFX8 memory queue descriptor manager for AMD KFD queues. It constructs, updates, checkpoints, restores, dumps, and loads CP, HIQ/DIQ, and SDMA MQDs used by the device queue manager to map user queues onto hardware queue descriptors.

## Important APIs, types, and functions
- `mqd_manager_init_vi` allocates a `struct mqd_manager` and fills its function table according to `enum KFD_MQD_TYPE`.
- CP/HIQ paths use `struct vi_mqd`; SDMA paths use `struct vi_sdma_mqd`.
- `allocate_mqd`, `init_mqd`, `load_mqd`, `update_mqd`, `checkpoint_mqd`, `restore_mqd`, and `get_wave_state` are the main CP queue hooks.
- `init_mqd_sdma`, `update_mqd_sdma`, `checkpoint_mqd_sdma`, and `restore_mqd_sdma` are the SDMA hooks.
- `update_cu_mask` maps a user CU mask through `mqd_symmetrically_map_cu_mask`.

## Control flow
The DQM asks this manager to allocate an MQD, initialize it with defaults, and then update it with queue properties. CP MQD initialization programs static defaults, persistence, base address, quantum, EOP fetcher, AQL read-pointer behavior, trap TBA/TMA, and CWSR fields. `load_mqd` delegates to `kfd2kgd->hqd_load` with an AQL-specific write-pointer shift. Updates fill PQ, EOP, IB, IQ, VMID, doorbell, ATC/MTYPE, CU mask, and active-state fields. HIQ/DIQ reuse CP initialization but set privileged/KMD queue bits. SDMA updates program ring base, read pointer writeback, doorbell, VM address, engine, and queue ID.

## State and persistence behavior
State persists in GTT-allocated `kfd_mem_obj` storage and in queue properties. Checkpoint/restore copies raw MQD bytes and rewrites doorbell fields from restored queue properties, then marks restored queues inactive until remapped. For VI CP, control stack data is reported as user-mode accessible, so checkpoint info returns zero control-stack bytes.

## Dependencies and integration points
Depends on `kfd_priv.h`, `kfd_mqd_manager.h`, VI hardware layout definitions, GFX8/OSS bit masks, GTT suballocation, DQM MQD callbacks, and `kfd2kgd` HQD operations. It integrates with CRIU through the PQM checkpoint hooks and with debugfs through `debugfs_show_mqd` callbacks.

## Risks
Bitfield shifts and memory type/ATC choices are hardware ABI sensitive. Queue-size calculations use `order_base_2`, so invalid or non-power-of-two sizes can produce wrong ring encodings if not validated earlier. Restored MQDs trust checkpointed raw data except for doorbell rewrites. CWSR and trap fields must match process-level TBA/TMA setup. The EOP size clamp is a specific hardware workaround and is easy to regress.

## Test signals
Exercise compute, AQL, PM4, HIQ/DIQ, and SDMA queue creation on VI ASICs; update CU masks and priority; suspend/preempt/restore queues; CRIU checkpoint/restore queues; inspect MQDs through debugfs; verify CWSR wave-state reporting and EOP-size boundary behavior.
