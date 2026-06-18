# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_common.c

## Purpose
`icssg_common.c` provides shared ICSSG Ethernet runtime logic: K3 UDMA TX/RX channel setup and cleanup, descriptor pools, page-pool RX, AF_XDP zero-copy, XDP actions, NAPI/IRQ handlers, TX/RX timestamp support, netdev timestamp/stat helpers, device-tree port mapping, PRU/RTU/TX_PRU core acquisition, and system sleep PM.

## Important APIs, Types, and Functions
Exported channel lifecycle functions include `prueth_init_tx_chns()`, `prueth_cleanup_tx_chns()`, `prueth_ndev_add_tx_napi()`, `prueth_ndev_del_tx_napi()`, `prueth_init_rx_chns()`, `prueth_cleanup_rx_chns()`, `prueth_prepare_rx_chan()`, `prueth_reset_tx_chan()`, and `prueth_reset_rx_chan()`. Packet paths are `icssg_ndo_start_xmit()`, `emac_tx_complete_packets()`, `icssg_napi_rx_poll()`, `prueth_rx_irq()`, `emac_xmit_xdp_frame()`, `prueth_xmit_free()`, `prueth_tx_cleanup()`, and `prueth_rx_cleanup()`. Timestamp/stat helpers include `icssg_ts_to_ns()`, `emac_rx_timestamp()`, `icssg_ndo_set_ts_config()`, `icssg_ndo_get_ts_config()`, and `icssg_ndo_get_stats64()`.

## Control Flow and State
TX initialization requests one K3 UDMA TX channel per queue, creates CPPI5 host descriptor pools, obtains IRQs, and later registers per-queue TX NAPI. RX initialization requests a UDMA RX channel, creates a descriptor pool and page pool, initializes all flows, records flow IDs, and obtains flow IRQs. RX preparation fills the free descriptor queue with page-pool pages or AF_XDP buffers. TX builds CPPI5 descriptors for the linear SKB and page frags, encodes queue/port tags, handles HSR offload tags, optionally reserves a TX timestamp cookie, accounts BQL, pushes to UDMA, and stops the queue if descriptors fall below `MAX_SKB_FRAGS`. Completion pops TX descriptors, handles teardown completions, frees SKB/XDP/XSK resources, updates stats/BQL, wakes queues, and services XSK TX.

## Dependencies and Integration Points
The file depends on K3 UDMA glue, CPPI5 descriptors, K3 descriptor pools, page_pool, XDP/AF_XDP, PHY/OF helpers, PRUSS/remoteproc, shared memory timestamp registers, ICSSG firmware stats/config helpers, and netdev queues/NAPI. Other ICSSG mode-specific drivers use this as a common library through exported symbols.

## Risks and Test Signals
Risk areas include descriptor leak/unmap mismatches across SKB, XDP frame, XDP_TX page-pool, and XSK paths; TX timestamp cookie reservation cleanup on error; queue stop/wake races; teardown completion accounting; RX page replacement failure and requeue behavior; firmware CRC stripping; SR1 versus newer timestamp conversion; and IRQ pacing timers that defer re-enable. `prueth_reset_rx_chan()` currently uses a fixed flow count from callers, so SR1 flow-count mismatches are worth testing. Test signals include multi-queue TX with frags, descriptor exhaustion, XDP_PASS/TX/REDIRECT/DROP, AF_XDP zero-copy wakeups, RX/TX teardown while traffic runs, hardware timestamp configuration and delivery, HSR offload TX tags, stats aggregation, suspend/resume with running netdevs, and PRU core acquire/release failure paths.
