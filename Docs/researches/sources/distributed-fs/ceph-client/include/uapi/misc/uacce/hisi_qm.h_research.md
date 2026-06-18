<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/misc/uacce/hisi_qm.h -->
# sources/distributed-fs/ceph-client/include/uapi/misc/uacce/hisi_qm.h

Purpose: defines HiSilicon queue-manager UACCE ioctls and payloads for configuring queue-pair context and queue depth/element sizing.

Important APIs and types: `struct hisi_qp_ctx` returns/sets queue pair ID and accelerator algorithm type. `struct hisi_qp_info` carries SQE size, submission queue depth, completion queue depth, and reserved data. API version strings identify supported queue-manager ABIs. Ioctls `UACCE_CMD_QM_SET_QP_CTX` and `UACCE_CMD_QM_SET_QP_INFO` use magic `H`.

Control flow, state, and persistence: userspace configures a UACCE queue before starting accelerator work; queue parameters persist for that queue lifetime.

Dependencies and integration points: integrates UACCE common queue files, HiSilicon accelerator drivers, hardware queue managers, and userspace crypto/compression runtimes.

Risks and test signals: risks include incompatible API version selection, queue depth mismatch, invalid algorithm type, and reserved field handling. Test QP setup, queue start, accelerator submission/completion, version negotiation, and invalid depths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/misc/uacce/hisi_qm.h -->
