# sources/distributed-fs/ceph-client/drivers/net/can/rockchip/rockchip_canfd-tx.c

Purpose: this file implements Rockchip CAN FD transmit submission, queue throttling, hardware command writes, TX retry for errata, and TX completion accounting.

Important APIs and functions: `rkcanfd_start_xmit()` is the netdev transmit method used by core. `rkcanfd_get_effective_tx_free()` reports queue space while honoring erratum 6 constraints. `rkcanfd_xmit_retry()` resends the current TX FIFO slot. `rkcanfd_handle_tx_done_one()` is called by RX self-reception filtering to complete one transmitted frame with the hardware timestamp.

Control flow: TX first drops invalid skbs through `can_dev_dropped_skb()`, then uses `netif_subqueue_maybe_stop()` with an effective free count. It builds frameinfo and ID registers from SFF/EFF/RTR/FDF/BRS/DLC, writes payload words into `RKCANFD_REG_FD_TXDATA*`, stores an echo skb with frame length, advances `tx_head`, and writes the appropriate TX request bit to `RKCANFD_REG_CMD`. Erratum 12 is handled by temporarily enabling `SPACE_RX_MODE` around command writes. Completion is not driven by the masked TX_FINISH interrupt; instead RX self-reception supplies the timestamp and calls `rkcanfd_handle_tx_done_one()`, which updates error counters, timestamps the echo skb, completes it through CAN RX offload, and updates tx stats.

State and persistence: TX state is `tx_head`, `tx_tail`, echo skb slots, netdev queue state, corrected `bec.txerr`, and ethtool erratum counters updated elsewhere. It persists only while the interface is registered/open. Queue state depends on the two-slot hardware FIFO depth.

Dependencies and integration points: integrates with netdev queue helpers, CAN echo skb APIs, CAN RX offload echo timestamp completion, RX erratum filtering, and shared register definitions. It assumes core enabled RX self-transmit mode and masked normal TX_FINISH interrupts.

Risks and test signals: payload writes cast unaligned byte data to `u32 *`, so architecture alignment behavior matters. Effective free count can return zero for pending extended frames under erratum 6, intentionally serializing TX. Completion depends on RX path correctness; if self-reception is lost, queues can stall. Tests should cover SFF/EFF/RTR/CAN FD/BRS TX encoding, queue busy/stop/wake behavior, erratum 12 command wrapping, erratum 6 retry, timestamped echo completion, bus-off cleanup interactions, and loopback/self-reception behavior.
