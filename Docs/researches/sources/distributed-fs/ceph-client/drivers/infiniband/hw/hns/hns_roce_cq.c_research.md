# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_cq.c

Purpose: Implements completion queue allocation, hardware context creation/destruction, event delivery, and CQ table initialization for HNS RoCE.

Important APIs/types/functions: Public APIs include `hns_roce_create_cq()`, `hns_roce_destroy_cq()`, `hns_roce_cq_completion()`, `hns_roce_cq_event()`, `hns_roce_init_cq_table()`, `hns_roce_cleanup_cq_table()`, and HIP09 user-context bank helpers. Internal helpers allocate CQN IDs, MTR-backed CQ buffers, optional record doorbells, CQC HEM contexts, and firmware CQC objects.

Control flow: Creation rejects unsupported flags, validates CQE count and vector, copies userspace command data, rounds entries to a power of two with a minimum, chooses CQE size, creates an MTR, maps or allocates doorbell records if supported, allocates a banked CQN, gets CQC HEM, stores the CQ in an xarray, writes CQC data into a command mailbox, sends CREATE_CQC, and copies response to userspace. Error paths unwind in reverse. Destruction sends DESTROY_CQC, erases the xarray entry, synchronizes IRQ, waits for event references, returns HEM, frees ID/DB/buffer.

State and persistence: `hns_roce_cq` owns MTR, DB, CQN, vector, counters, refcount, completion, QP linkage lists, and flags. `hns_roce_cq_table` owns the lookup xarray and bank IDAs/load counters. HIP09 user contexts reserve a CQ bank for all CQs in that context.

Dependencies and integration: Uses RDMA uverbs, user/kernel doorbell helpers, HEM table management, command mailbox, hardware `write_cqc`, EQ IRQs, xarray, IDA, and DFX counters. Completion events call RDMA core CQ handlers.

Risks: CQN lower bits encode bank ID and lookup masks with `num_cqs - 1`; sizing must match hardware power-of-two assumptions. IRQ synchronization and refcount completion prevent use-after-free during async events. Test signals include userspace/kernel CQ creation, CQ record DB capability negotiation, bank balancing, invalid vector/count rejection, async error events, destroy under interrupt load, and mailbox failure unwinds.
