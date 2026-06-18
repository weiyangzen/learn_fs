# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager.h

Purpose: defines the MQD manager abstraction used by KFD queue management and declares common helpers implemented in `kfd_mqd_manager.c`.

Important APIs/types/functions: `struct mqd_manager` is a vtable plus device context and `mqd_size`. It covers MQD allocation/init/load/update/destroy/free, occupancy checks, wave-state extraction, checkpoint/restore, debugfs dumping, preemption-failure checks, and stride calculation. `struct mqd_user_context_save_area_header` defines the user-visible compact header for control-stack and wave-state offsets/sizes. The header declares HIQ/SDMA allocation helpers, CP/SDMA load/destroy/free helpers, CU-mask mapping, stride helpers, and HIQ XCC accessors.

Control flow: DQM selects a per-generation `mqd_manager_init_*` function and stores manager instances by `KFD_MQD_TYPE`. Queue creation and scheduling then call through the vtable for CP, HIQ, DIQ, and SDMA queues without knowing the underlying MQD layout.

State and persistence: the abstraction persists function pointers, a mutex, device pointer, and MQD size. Queue state is persisted in hardware-visible MQD memory allocated/managed by implementations.

Dependencies/integration: includes `kfd_priv.h` for queue/device/process types and is included by all ASIC-specific MQD manager files plus kernel queue/DQM code.

Risks: vtable omissions are runtime failures; each queue type must install a coherent set of callbacks. The checkpoint/restore ABI must match user-space expectations for debugger/process checkpointing. Test signals include manager initialization for every queue type and ASIC, debugfs dumps, checkpoint/restore round trips, and wave-state extraction ABI validation.
