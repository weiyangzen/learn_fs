
# sources/distributed-fs/ceph-client/include/linux/nvme-rdma.h

Purpose: defines NVMe/RDMA private connection-management data formats, default ports, queue-size limits, status codes, and status text helpers.

Important APIs/types/functions: constants include `NVME_RDMA_IP_PORT`, maximum/default queue sizes, and metadata queue limits. `enum nvme_rdma_cm_fmt` identifies private data format 1.0. `enum nvme_rdma_cm_status` lists rejection reasons. `nvme_rdma_cm_msg()` maps rejection codes to strings. `struct nvme_rdma_cm_req`, `nvme_rdma_cm_rep`, and `nvme_rdma_cm_rej` define little-endian RDMA CM request, reply, and reject private data payloads.

Control flow: RDMA connection setup sends a request containing queue ID, host receive/send queue sizes, and controller ID; the controller replies with controller receive queue size or rejects with a status. Host and target code use the helper string for diagnostics.

State and persistence: no state is stored. Structures are transient RDMA CM private data exchanged during queue connection.

Dependencies and integration points: depends on fixed-width endian types and RDMA CM users in the NVMe/RDMA transport. It integrates fabrics queue setup with RDMA connection negotiation.

Risks and test signals: risks include endian mistakes, accepting invalid qid/queue sizes, mismatch between metadata and normal queue limits, and missing diagnostics for new status codes. Test signals include NVMe/RDMA connect/reject tests, invalid private-data length tests, queue-size boundary tests, and interop with target implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nvme-rdma.h -->
