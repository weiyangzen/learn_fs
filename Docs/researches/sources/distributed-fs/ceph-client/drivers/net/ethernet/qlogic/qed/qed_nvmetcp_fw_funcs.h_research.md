# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_nvmetcp_fw_funcs.h

Purpose: Declares NVMe/TCP task-context initialization helpers used by the exported NVMe/TCP core ops table.

Important APIs/types/functions: Under `CONFIG_QED_NVMETCP`, declares host read/write task initializers, initial connection request initializer, and cleanup task initializer. The prototypes use `struct nvmetcp_task_params`, NVMe/TCP PDU types, NVMe command type, and `struct storage_sgl_task_params`.

Control flow: No runtime control flow is implemented here; it gates declarations for call sites in `qed_nvmetcp.c`.

State and persistence: No state is stored. Callers pass all context/SGL/SQE storage.

Dependencies/integration: Includes kernel/QED storage and NVMe/TCP HSI headers so function signatures match firmware context structures.

Risks: The disabled-config branch provides no stubs in this header, so users must compile the function-pointer assignments only when NVMe/TCP support is enabled. Prototype drift from `qed_nvmetcp_fw_funcs.c` would break the ops-table integration.

Test signals: Build coverage with NVMe/TCP enabled and disabled, plus compile checks that `qed_nvmetcp_ops_pass` sees the expected function signatures.
