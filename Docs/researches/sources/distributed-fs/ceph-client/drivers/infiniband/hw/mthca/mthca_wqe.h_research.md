# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_wqe.h

Purpose: defines mthca work queue element segment layouts and helpers used to build send, receive, SRQ, and special QP descriptors.

Important APIs/types/functions: declares WQE flag bits such as `MTHCA_NEXT_DBD`, `MTHCA_NEXT_FENCE`, CQ/event/solicit/checksum bits, MLX VL15/SLR bits, invalid L_Key sentinel, and Tavor/Arbel doorbell batch limits. Defines segment structs: `mthca_next_seg`, `mthca_tavor_ud_seg`, `mthca_arbel_ud_seg`, `mthca_bind_seg`, `mthca_raddr_seg`, `mthca_atomic_seg`, `mthca_data_seg`, and `mthca_mlx_seg`. Provides `mthca_set_data_seg` and `mthca_set_data_seg_inval`.

Control flow: inline helpers encode `ib_sge` into big-endian hardware data segments or mark a data segment invalid with L_Key `0x100`.

State and persistence: no persistent state; structs are hardware descriptor formats written into QP/SRQ WQE rings and consumed by the HCA.

Dependencies and integration: included by `mthca_qp.c` and `mthca_srq.c`; relies on Linux fixed-width/endian types and RDMA `struct ib_sge` being visible through includers.

Risks: segment layout and endian fields are firmware ABI. Any packing, size, or flag mistakes can corrupt DMA operations. Invalid sentinel use must match hardware expectations so unused SGEs are not interpreted as valid DMA.

Test signals: compile layout-sensitive code, run send/receive/RDMA/atomic/UD/special-QP traffic, validate checksum offload flags on Arbel, and inspect failed CQEs for descriptor formatting issues.
