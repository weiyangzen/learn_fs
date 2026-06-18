# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/efx.h

Purpose: Central shared header for SFC netdev datapath APIs, indirect EF100/common RX/TX dispatch, filter wrappers, RSS helpers, queue size limits, ethtool declaration, MTD stubs, SR-IOV VF sizing, device attach/detach helpers, and XDP TX.

Important APIs and definitions: Declares `efx_net_open()`, `efx_net_stop()`, TX queue/xmit helpers, RX packet helpers, `efx_enqueue_skb()` and `efx_rx_flush_packet()` indirect-call wrappers, TSO/RX/TX queue limits, filter insert/remove/get/count wrappers, `efx_rss_active()`, `efx_ethtool_ops`, IRQ moderation helpers, stats update, MTD helpers, `efx_device_detach_sync()`, `efx_device_attach_if_not_resetting()`, and `efx_xdp_tx_buffers()`.

Control flow: Inline wrappers route generic callers to EF100-specific or common implementations based on NIC type callbacks. Device detach stops representors before detaching the PF netdev and freezing TX queues; attach restores PF netdev presence and wakes reps when the device is NET_UP and not resetting.

State and persistence: Header does not own state but manipulates netdev present state, representor carrier/TX queues, filter tables through type callbacks, RSS context IDs, and queue sizing constants used at runtime.

Dependencies and integration points: Includes EF100 RX/TX headers, `efx_common.h`, filters, and `net_driver.h`. It is a high-fanout dependency for TX, RX, ethtool, core, and NIC-specific files.

Risks: Indirect call target lists must match actual function signatures. Queue limit macros combine generic limits with EF10 workarounds, so misuse can under-size or overrun rings. Attach/detach ordering matters for representors that transmit through PF queues.

Test signals: Build all NIC variants, verify hard-start-xmit dispatch for EF100 and common TX, RX flush dispatch, filter ioctl/ethtool flows, queue-size ethtool bounds, reset attach/detach behavior with representors, and XDP TX queue access.
