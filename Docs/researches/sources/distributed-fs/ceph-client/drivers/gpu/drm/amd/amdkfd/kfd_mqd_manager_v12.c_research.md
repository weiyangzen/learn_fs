# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v12.c

Purpose: implements GFX12.0 MQD manager operations for compute, HIQ/DIQ, and SDMA queues. It closely follows GFX11 but uses GFX12 structures, masks, context-save user header, and SDMA MCU write-pointer polling.

Important APIs/types/functions: `mqd_manager_init_v12` is the public initializer. Helpers include `allocate_mqd`, `init_mqd`, `load_mqd`, `update_mqd`, `get_wave_state`, `init_mqd_hiq`, `init_mqd_sdma`, `update_mqd_sdma`, and debugfs dump callbacks.

Control flow: compute init uses aligned MQD size, sets static thread masks for eight SE fields, persistent preload 0x55, MQD base, quantum, debug status, optional atomics support bit, AQL control, and CWSR fields. Update programs PQ size/base/rptr/wptr polling/doorbell, IB/EOP controls, VMID, AQL no-update/slot/full/drop fields, CWSR control, CU mask, and priority. `get_wave_state` fills `mqd_user_context_save_area_header`, not the older nested KFD context-save header. SDMA update programs queue RB control with MCU write-pointer polling, schedule quantum, dummy register, and switch-inside-IB for fairness.

State and persistence: MQD memory stores queue and CWSR state. The file does not implement checkpoint/restore callbacks for v12 CP/SDMA in this snapshot, unlike v10/v11; consumers must tolerate missing callbacks or use higher-level alternatives.

Dependencies/integration: depends on GFX12 struct/mask headers, shared MQD helpers, amdgpu atomics detection, `amdgpu_sdma_phase_quantum`, KFD2KGD HQD callbacks, and debugfs.

Risks: absence of checkpoint/restore callbacks is an ABI/feature difference to verify against checkpointing consumers. EOP size programming assumes valid nonzero sizes. SDMA allocation uses generic CP allocation/free for page-aligned MQDs. Test signals include GFX12 queue creation for CP/HIQ/DIQ/SDMA, CWSR header ABI, AQL/PM4 operation, SDMA fairness switch, and checkpointing feature probes.
