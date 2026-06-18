# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_ptp.h

Purpose: declares the cxgb4 PTP interface and small skb timestamp helpers shared by transmit, receive, and adapter lifecycle code.

Important APIs/types: constants `MAX_PTP_FREQ_ADJ`, `PTP_CLOCK_MAX_ADJTIME`, `PTP_MIN_LENGTH`, `PTP_IN_TRANSMIT_PACKET_MAXNUM`, and `PTP_EVENT_PORT`; enum `ptp_rx_filter_mode`; inline helpers `cxgb4_xmit_with_hwtstamp` and `cxgb4_xmit_hwtstamp_pending`; prototypes for PTP initialization, stop, packet classification, timestamp configuration, and hardware timestamp readout.

Control flow/state: the header has no owning control flow. Callers use the inline helpers to test/set `skb_shinfo(skb)->tx_flags` before the implementation in `cxgb4_ptp.c` stores pending TX skbs and programs firmware.

Dependencies/integration: relies on `struct sk_buff`, `struct adapter`, `struct net_device`, and `struct port_info` definitions from surrounding cxgb4 headers. It is included by main driver paths that configure hwtstamp and TX paths that mark packets in progress.

Risks: helper use assumes skb shared info is valid and that only appropriate packets get `SKBTX_IN_PROGRESS`. Constants constrain packet recognition to IPv4 UDP PTP event packets of a bounded size.

Test signals: compile coverage with PTP enabled/disabled, timestamp flag propagation in TX tests, and hwtstamp ioctl paths selecting `PTP_TS_NONE`, L2, L4, or combined modes.
