# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v10.c

Purpose: implements MQD manager operations for GFX10 compute and SDMA queues using `v10_compute_mqd` and `v10_sdma_mqd` layouts.

Important APIs/types/functions: `mqd_manager_init_v10` wires CP, HIQ, DIQ, and SDMA vtables. Core helpers include `allocate_mqd`, `init_mqd`, `load_mqd`, `update_mqd`, `get_wave_state`, `checkpoint_mqd`, `restore_mqd`, `init_mqd_hiq`, `destroy_hiq_mqd`, `init_mqd_sdma`, and `update_mqd_sdma`.

Control flow: compute MQD init zeros the descriptor, writes header/static thread masks/persistent state/PQ defaults/base address/quantum/debug scheduler bit, enables AQL if requested, and configures CWSR fields when enabled. Update programs PQ size/base/rptr/wptr polling/doorbell, IB/EOP controls, VMID, AQL no-update/slot-based/full/drop bits, CWSR control, CU mask, and priority. Load calls `hqd_load` with AQL write-pointer shift. HIQ init marks privileged KMD and destroy unmaps HIQ by doorbell offset. SDMA update programs RB control/base/rptr/doorbell, engine/queue IDs, and dummy register.

State and persistence: MQD memory captures queue state and CWSR metadata. Checkpoint copies compute or SDMA MQDs; GFX10 control stack remains in the user-accessible context save area, so `get_wave_state` only copies a header to userspace.

Dependencies/integration: relies on GFX10 register masks, shared MQD helpers, amdgpu HQD/HIQ callbacks, KFD CWSR/debugger queue properties, and debugfs dumping.

Risks: GFX10 removed WPP clamp bits used by earlier generations, so AQL field programming must stay generation-correct. EOP size calculation uses `ffs` and assumes nonzero EOP size. Test signals include CWSR wave-state header reporting, AQL/PM4 queues, HIQ unmap, SDMA MQD load, CU-mask updates, checkpoint/restore, and debugfs dumps.
