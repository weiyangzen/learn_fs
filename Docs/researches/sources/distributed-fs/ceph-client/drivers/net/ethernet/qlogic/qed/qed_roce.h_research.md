# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_roce.h

Purpose: Declares RoCE-specific hooks consumed by the generic RDMA layer and DCBX code.

Important APIs/types/functions: Exposes `qed_roce_dpm_dcbx()`, `qed_roce_setup()`, `qed_roce_stop()`, `qed_roce_init_hw()`, `qed_roce_alloc_cid()`, `qed_roce_destroy_qp()`, `qed_roce_query_qp()`, and `qed_roce_modify_qp()`. `qed_roce_dpm_dcbx()` has a no-op stub when `CONFIG_QED_RDMA` is disabled.

Control flow: No implementation logic; it defines the protocol-specific call surface invoked during RDMA start/stop and QP state transitions.

State and persistence: No direct state. Functions operate on `struct qed_hwfn` and `struct qed_rdma_qp` state defined elsewhere.

Dependencies/integration: Includes Linux types/slab and relies on QED RDMA structures being declared before use in compilation units.

Risks: Most declarations are not config-stubbed, so non-RDMA builds must avoid linking users of the full RoCE API. The header forms a circular conceptual dependency with `qed_rdma.h`, which includes it while also defining `struct qed_rdma_qp`.

Test signals: Build with RDMA enabled/disabled, verify generic RDMA code links all RoCE symbols in enabled builds, and confirm DCBX code can call `qed_roce_dpm_dcbx()` unconditionally.
