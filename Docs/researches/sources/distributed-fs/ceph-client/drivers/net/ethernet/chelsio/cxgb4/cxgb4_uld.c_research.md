# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_uld.c

Purpose: implements the cxgb4 Upper Layer Driver registration and SGE queue management layer for RDMA, iSCSI, crypto, IPsec, TLS, and related offload clients.

Important APIs/functions: `t4_uld_mem_alloc`, `t4_uld_mem_free`, `t4_uld_clean_up`, `cxgb4_uld_enable`, `cxgb4_register_uld`, `cxgb4_unregister_uld`, and optional `cxgb4_set_ktls_feature`; internal helpers allocate/free ULD RX/TX queues, request/free MSI-X IRQs, enable/quiesce RX, populate `cxgb4_lld_info`, attach ULDs, and shut them down.

Control flow: a ULD registers global callbacks in `uld_list`; each enabled adapter is added to `adapter_list` and attempts resource allocation for every compatible registered ULD. Allocation configures RX/concentrator queues, SGE queues, MSI-X IRQs, RX enablement, shared or crypto TX queues, copies ULD callbacks, and calls the ULD `add` method with low-level device info. Shutdown clears callbacks/handle, releases TX queues, quiesces RX, frees IRQs, SGE queues, and queue metadata.

State and persistence: global `uld_list` and `adapter_list` are protected by `uld_mutex`; per-adapter `adap->uld[type]`, `sge.uld_rxq_info`, and `sge.uld_txq_info` hold runtime state. TX queue info has a users counter for shared offload queues. Optional kTLS state uses `chcr_ktls.ktls_refcount`.

Dependencies/integration: depends on SGE allocation/free helpers, MSI-X bitmap/affinity helpers, firmware params, netevent notifier registration, offload capability checks, and ULD callback contracts defined in `cxgb4_uld.h`.

Risks: multi-step resource allocation has many unwind labels; missed cleanup can leak IRQs, queue contexts, or bitmap indices. `cxgb4_uld_alloc_resources` skips unsupported adapter/ULD combinations, so registration success does not imply every adapter attached. kTLS enablement blocks when other ULD connections are active. Queue count rounding by port count can produce zero for crypto and returns `-EINVAL`.

Test signals: register/unregister each ULD type, attach failure at every allocation stage, MSI-X and non-MSI-X modes, full-init versus early-init paths, adapter removal with active ULDs, shared TX queue user counting, kTLS enable/disable refcounting, and state-change notification to attached ULDs.
