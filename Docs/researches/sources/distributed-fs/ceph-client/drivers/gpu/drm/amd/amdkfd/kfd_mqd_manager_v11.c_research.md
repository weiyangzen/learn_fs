# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v11.c

Purpose: implements GFX11 MQD managers, adding aligned MQD allocation, debugger workaround CU-mask modes, PCIe atomic acknowledgement bits, SDMA write-pointer polling, and MES-specific SDMA allocation behavior.

Important APIs/types/functions: `mqd_manager_init_v11` wires CP/HIQ/DIQ/SDMA managers. `update_cu_mask` supports `UPDATE_FLAG_DBG_WA_ENABLE`/`DISABLE` by forcing static thread masks. `init_mqd`, `update_mqd`, `get_wave_state`, `checkpoint_mqd`, `restore_mqd`, `init_mqd_hiq`, `destroy_hiq_mqd`, `init_mqd_sdma`, and `update_mqd_sdma` implement queue operations.

Control flow: compute allocation uses `AMDGPU_MQD_SIZE_ALIGN`. Init programs full or workaround static masks, persistent preload size 0x55, base address, quantum, dispatch-pointer debug status, optional atomics support acknowledgement, AQL control, and CWSR fields. Update fills PQ/EOP/IB/VMID/doorbell fields and AQL flags, then applies CU-mask/WA updates and priority. SDMA init zeros a page when MES is enabled, otherwise the SDMA MQD size. SDMA update enables rptr writeback, 32-bit wptr polling, schedule quantum, and doorbell offset. Manager init switches SDMA allocation/free to generic CP allocation/free under MES.

State and persistence: queue state is persisted in aligned MQD memory. Debug workaround state is encoded as static thread masks. Checkpoint/restore copy MQDs and rewrite doorbell offset; wave-state retrieval copies only the context-save header because control stack is user-visible elsewhere.

Dependencies/integration: depends on GFX11 structs/masks, amdgpu atomics support detection, global `amdgpu_sdma_phase_quantum`, shared MQD helpers, MES shared-resource flag, and debugfs.

Risks: WA flag handling can override user CU masks. MES SDMA uses different backing allocation size and free path. Atomics acknowledgement is firmware-dependent. Test signals include CU debug WA toggles, MES and non-MES SDMA queue creation, atomics-capable devices, AQL flag programming, CWSR wave-state reads, and HIQ preemption-failure reporting.
