# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_hem.c

Purpose: Implements Hardware Entry Memory management for HNS RoCE. It allocates refcounted coherent memory chunks for hardware context tables and constructs multi-hop base-address trees for MTR/MTT style buffers.

Important APIs/types/functions: Public table APIs are `hns_roce_table_get()`, `hns_roce_table_put()`, `hns_roce_table_find()`, `hns_roce_init_hem_table()`, `hns_roce_cleanup_hem_table()`, `hns_roce_cleanup_hem()`, `hns_roce_calc_hem_mhop()`, and `hns_roce_check_whether_mhop()`. HEM-list APIs are `hns_roce_hem_list_init()`, `hns_roce_hem_list_request()`, `hns_roce_hem_list_release()`, `hns_roce_hem_list_calc_root_ba()`, and `hns_roce_hem_list_find_mtt()`.

Control flow: Table get determines whether the table is direct or multi-hop. Direct mode indexes a chunk by object number, allocates a coherent HEM chunk, calls hardware `set_hem`, and sets refcount. Multi-hop mode calculates L0/L1/L2 indexes from caps, lazily allocates BA pages and buffer pages, wires DMA addresses through parent BA pages, then programs the relevant hardware steps for context tables. Put decrements refcount, clears hardware entries, frees buffer and now-empty BA pages. Init preallocates pointer arrays for HEM and BA levels based on object count and cap-derived chunk sizes.

State and persistence: `hns_roce_hem_table` owns arrays of `hns_roce_hem` chunks plus optional L0/L1 BA page arrays and DMA addresses. Each allocated HEM has coherent DMA memory and a refcount. HEM lists own root, middle, and bottom `hns_roce_hem_item` lists and a root BA for a specific MTR.

Dependencies and integration: Uses device caps for hop counts/page sizes, hardware `set_hem`/`clear_hem`, coherent DMA, mutex/refcount/list helpers, and context users such as CQ/QP/MR/SRQ/timer/GMV tables. HEM-list output is consumed by MTR creation and MR/CQ/QP buffer mapping.

Risks: Multi-hop index math must match firmware exactly; off-by-one errors corrupt BA trees. Cleanup conditionally frees parent BA pages only when sibling chunks are absent. Large MR construction can be long-running, so the loop calls `cond_resched()` after a 4K-page threshold. Test signals include direct and 1/2/3-hop tables, refcount sharing, hardware set/clear failures, large MRs, mixed-region MTRs, cleanup after partial allocation failure, and `hns_roce_table_find()` DMA offset correctness.
