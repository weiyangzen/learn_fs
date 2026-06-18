# sources/distributed-fs/ceph-client/include/linux/qed/rdma_common.h

Purpose: publishes QED firmware-facing RDMA constants and small shared structures used by RoCE/RDMA command queues and shared receive queue handling.

Important APIs and types: constants define reserved LKEY, ring page size, maximum SGEs per SQ/RQ WQE, maximum data size, atomic element sizes, CQ/TID/PD/SRQ limits, IRQ elements per page, per-vport statistic counter counts, and `RDMA_TASK_TYPE`. `struct rdma_srq_id` carries an SRQ index plus opaque function ID in little-endian layout. `struct rdma_srq_producers` exposes SGE and WQE producer indexes.

Control flow: QED RDMA code uses these values when sizing hardware resources, programming firmware ramrods, validating WQE layout, and exchanging SRQ producer state with firmware. There are no executable functions in this header.

State and persistence: no state is stored here. The structures describe memory shared between driver and firmware; persistence is limited to device runtime queues and firmware contexts.

Dependencies and integration points: relies on protocol constants such as `PROTOCOLID_ROCE` and vport count macros from adjacent QED firmware headers. It is consumed by QED core and RDMA/RoCE provider code.

Risks and test signals: risks are ABI/layout drift with firmware, endian mistakes, and resource-limit mismatches that surface only under large queue/table counts. Test with compile-time structure layout checks where available, RDMA resource exhaustion tests, SRQ create/use/destroy, CQ/TID/PD maximum boundary tests, and firmware compatibility matrices across supported QED devices.
