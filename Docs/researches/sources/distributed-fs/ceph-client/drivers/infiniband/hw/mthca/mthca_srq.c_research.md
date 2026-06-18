# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_srq.c

Purpose: implements shared receive queue allocation, firmware context setup, receive posting, event dispatch, querying/modification, and SRQ table lifetime for mthca.

Important APIs/functions: defines Tavor and Arbel SRQ context structures; exports `mthca_alloc_srq`, `mthca_free_srq`, `mthca_modify_srq`, `mthca_query_srq`, `mthca_srq_event`, `mthca_free_srq_wqe`, `mthca_tavor_post_srq_recv`, `mthca_arbel_post_srq_recv`, `mthca_max_srq_sge`, `mthca_init_srq_table`, and `mthca_cleanup_srq_table`.

Control flow: allocation validates requested WR/SGE limits, adjusts max WR for hardware generation, computes WQE stride, allocates SRQN, maps mem-free SRQ ICM and DB record, allocates kernel buffers/WRID array unless userspace owns them, initializes a free-list embedded in WQEs, builds the proper firmware context, transitions with `SW2HW_SRQ`, and publishes the SRQ in the table. Posting pops WQEs from the free list, fills data segments, stores WRIDs, and rings either Tavor receive doorbells or Arbel DB records after write barriers.

State and persistence: runtime state includes SRQN allocation, firmware SRQ context, queue buffer/MR, free-list indices, WQE counter, DB record, WRID array, table pointer, refcount, wait queue, and locks. Hardware state persists until `HW2SW_SRQ` and table cleanup.

Dependencies and integration: provider SRQ verbs call these APIs; CQ completion handling returns WQEs through `mthca_free_srq_wqe`; uses `mthca_memfree`, `mthca_wqe`, buffer/MR allocation, and SRQ firmware commands.

Risks: SRQ free-list manipulation is subtle, especially because Tavor posting can overwrite the previous WQE next segment, so the code stores software links in `imm`. Doorbell ordering requires barriers. SRQ resize is explicitly unsupported. Destruction must wait for event references before freeing.

Test signals: create/query/arm/destroy SRQs, post receive bursts up to capacity, completion recycling, SRQ limit events, Arbel versus Tavor paths, userspace SRQ doorbell mapping, and lockdep/event race testing.
