## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/ring.c

Purpose: initializes v2 linked-list DMA descriptors and publishes TX/RX descriptor base addresses to hardware.

Important APIs, types, and functions: `xge_setup_desc` creates a circular linked list of `XGENE_ENET_NUM_DESC` descriptors by setting each descriptor empty and pointing `NEXT_DESC_ADDRL/H` to the next descriptor. `xge_update_tx_desc_addr` writes `DMATXDESCL/H` and resets TX head/tail. `xge_update_rx_desc_addr` writes `DMARXDESCL/H` and resets RX head/tail.

Control flow, state, and persistence: `main.c` calls setup when creating rings and during TX timeout recovery. Descriptor memory is coherent and persists for the open lifetime; head/tail software indexes are reset whenever the base address is republished.

Dependencies and integration points: depends on descriptor field macros from `ring.h`, CSR writes from `enet.c`, DMA addresses allocated in `main.c`, and hardware registers consumed by the DMA engine.

Risks: wrong next-descriptor links break the hardware ring permanently until reset. The ring size must be power-of-two for mask wrapping. Republish during live traffic must be done after stopping DMA/queue.

Test signals: ring initialization inspection, successful TX/RX after open, wraparound traffic beyond descriptor count, and timeout recovery that resumes TX after `xge_setup_desc`.
