# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/ocrdma.h

Purpose: central private header for the Emulex OneConnect RoCE driver, defining device attributes, queue/memory/resource objects, RDMA core wrappers, and utility inline helpers.

Important APIs/types/functions: defines version/name constants, device IDs, `OCRDMA_MAX_AH`, DMA/PBL/queue structs, `ocrdma_dev_attr`, EQ/MQ command context, HW/user MR types, PD resource manager, stats/PHY structs, `ocrdma_dev`, CQ/PD/AH/QP/SRQ/ucontext/mm wrappers, container helpers (`get_ocrdma_*`), CQE predicate helpers, `ocrdma_resolve_dmac`, `hca_name`, EQ lookup, ASIC type/prio/link helpers, and UDP encapsulation support checks.

Control flow: inline functions convert RDMA core objects to private structs, check CQE validity/flags, derive destination MACs from multicast/link-local/roce attributes, map device ids to names, locate EQ table entries, lazily read ASIC id from PCI config, and interpret link/PFC/app-priority state.

State and persistence: structures hold all runtime ocrdma state: firmware limits, EQ/CQ/QP tables, GSI CQs, AV table, mailbox queue context, be2net NIC info, stats/debugfs memory, PD bitmaps, per-object queues, doorbells, DMA addresses, and user mmap metadata.

Dependencies and integration: includes RDMA core headers, `ib_addr.h`, be2net RoCE integration header `be_roce.h`, and `ocrdma_sli.h`. Other ocrdma source files include this for all private driver state.

Risks: this header is a broad shared contract; structure changes affect multiple object lifetimes and userspace interactions. CQE phase logic and MAC resolution must match hardware/RDMA core semantics. Comments show synchronization responsibilities, so misuse can race CQ polling, QP flushing, or GID updates.

Test signals: full ocrdma build, RoCE connection traffic, CQ polling phase wrap tests, link/PFC changes, AH creation for multicast/link-local/routed GIDs, debugfs stats, and be2net integration probe/remove.
