<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_vec.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_vec.h

Purpose: declares the vector/NAPI API that connects NIC lifecycle code with ring allocation, interrupt handlers, and per-ring stats.

Important APIs/types: forward declares key driver structs and exposes ISR entry points, vector allocation/init/start/stop/deinit/free, ring allocation/free, IRQ affinity retrieval, TC validity, and software stat collection.

Control flow: NIC registration allocates vectors; NIC init allocates and initializes vector rings; NIC start starts vectors and requests IRQs using `aq_vec_isr`; NIC stop/deinit/free calls stop/deinit/ring_free/free; ethtool stats paths use `aq_vec_get_sw_stats`.

State and persistence: the vector structure is opaque to users of the header; state is owned by `aq_vec.c`.

Dependencies and integration: includes common, NIC, ring, hardware, IRQ, BPF filter, and netdevice headers. This header is part of the common driver contract between high-level NIC code and data-path implementation.

Risks: include coupling is high because `aq_vec.h`, `aq_ring.h`, and `aq_nic.h` reference one another; changing prototypes affects probe/open/close and IRQ handling. Test signals are compile coverage and runtime open/close under different TC/vector counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_vec.h -->
