# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_hw_stats.c

Purpose: RDMA hardware statistics and RDMA counter support for Ionic. It discovers firmware-provided statistic descriptors, exposes global port stats through RDMA core, and supports per-counter QP aggregation by issuing admin commands for each bound QP.

Important APIs/functions: public entry points are `ionic_stats_init()` and `ionic_stats_cleanup()`. RDMA device ops installed from this file include `alloc_hw_port_stats`, `get_hw_stats`, `counter_alloc_stats`, `counter_dealloc`, `counter_bind_qp`, `counter_unbind_qp`, and `counter_update_stats`. Internal helpers normalize `struct ionic_v1_stat`, fill `rdma_stat_desc`, decode typed values, and issue stats admin WQEs.

Control flow: initialization checks `lif_cfg.stats_type`. Global stats allocate a descriptor buffer and value buffer, DMA-map the descriptor page, send `IONIC_V1_ADMIN_STATS_HDRS`, normalize names/types/offsets, and install port stat ops. QP counters allocate a `struct ionic_counter_stats`, request `IONIC_V1_ADMIN_QP_STATS_HDRS`, initialize an xarray of counters, and install counter ops. A stats read DMA-maps the value page, sends a values command, then decodes each descriptor offset into RDMA counters. QP counter reads iterate all QPs bound to a counter and sum returned values.

State and persistence: device-level state lives in `dev->hw_stats`, `dev->hw_stats_buf`, `dev->hw_stats_hdrs`, and `dev->hw_stats_count`. Per-counter state is kept in `dev->counter_stats`, xarray entries, `struct ionic_counter` value pages, and QP list membership. No persistent storage exists beyond driver lifetime.

Dependencies and integration: uses Ionic admin queue submission/waiting, DMA mapping, RDMA hardware stats and counter APIs, xarray allocation, and QP list entries in `struct ionic_qp`.

Risks: descriptor offsets are firmware-provided; `ionic_v1_stat_val()` bounds and alignment checks invalid entries but returns all-ones on bad layout, which can look like a huge counter. Counter QP lists are updated without local locking in this file, so correctness depends on RDMA counter core serialization and QP teardown ordering. Admin opcode availability is checked against `lif_cfg.admin_opcodes`.

Test signals: devices advertising global stats, devices advertising QP stats, invalid port reads, counter bind/unbind/dealloc, aggregation across multiple QPs, admin timeout/error handling, and cleanup after partial initialization failure.
