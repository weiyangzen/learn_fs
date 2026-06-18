# sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_int.c

Purpose: Handles Sunplus interrupt dispatch plus RX/TX NAPI polling for the shared descriptor rings.

Important APIs/functions: `spl2sw_ethernet_interrupt()` reads/acks `L2SW_SW_INT_STATUS_0`, masks RX and/or TX interrupt bits, accounts descriptor errors, and schedules RX/TX NAPI. `spl2sw_rx_poll()` drains high-priority then low-priority RX queues, validates source port and length/error bits, unmaps DMA, submits packets with `netif_receive_skb()`, allocates replacement SKBs, reinitializes descriptors, and unmasks RX interrupts. `spl2sw_tx_poll()` reclaims completed TX descriptors, updates the stats for the VLAN-selected netdev, unmaps/free SKBs, clears full state, wakes stopped queues, and unmasks TX interrupts.

Control flow and state: RX source selection comes from `RXD_PKT_SP`; TX completion stats recover the netdev by `ffs(FIELD_GET(TXD_VLAN, cmd)) - 1`. RX and TX NAPI both complete and re-enable interrupt bits after their loops. TX ring mutation is protected by `tx_lock`; interrupt mask register access is serialized by `int_mask_lock`.

Dependencies and integration points: Depends on descriptor layout, shared `spl2sw_common`, netdev stats, DMA mapping APIs, NAPI, and Sunplus interrupt mask/status registers. It is wired by `spl2sw_driver.c` through `devm_request_irq()` and `netif_napi_add*()`.

Risks and test signals: `spl2sw_rx_poll()` and `spl2sw_tx_poll()` call `napi_complete()` unconditionally even if they used the whole budget, which can re-enable interrupts while work remains. In RX low-priority processing, `h_desc` is used as the saved high-priority descriptor pointer; priority break behavior should be verified carefully. Replacement SKB allocation failures leave descriptors without buffers until later cleanup/reset. Test NAPI budget exhaustion, interrupt storms, descriptor errors, RX allocation failure, mixed high/low priority traffic, invalid source port, and TX ring full wakeups.
