# sources/distributed-fs/ceph-client/include/trace/events/net.h

Purpose: Supplies core networking tracepoints for transmit start/completion/timeout and receive ingress/exit paths. It is a generic visibility layer for netdev TX queues, skb metadata, and NAPI/GRO/netif receive flows.

Important APIs/types/functions: TX events `net_dev_start_xmit`, `net_dev_xmit`, and `net_dev_xmit_timeout`; `DECLARE_EVENT_CLASS(net_dev_template)` for `net_dev_queue`, `netif_receive_skb`, and `netif_rx`; `DECLARE_EVENT_CLASS(net_dev_rx_verbose_template)` for verbose RX entry events; and `DECLARE_EVENT_CLASS(net_dev_rx_exit_template)` for exit return codes. Fields include skb pointers, lengths, protocol, VLAN tags, queue mappings, transport offsets, GSO details, checksum state, hash, traffic class, device names, and return codes.

Control flow: Net core emits start-xmit before driver handoff, completion after qdisc/dev return, timeout when watchdog detects a stuck queue, and receive events around GRO and `netif_receive_skb`/`netif_rx` entry and exit. Fast assignment snapshots skb fields while still valid.

State and persistence: No persistent state. Events mirror skb and netdev state moving through hot networking paths.

Dependencies and integration points: Depends on skb, netdevice, VLAN/IP, busy-poll, and trace infrastructure. Consumers include tracing tools for qdisc, driver, GRO, and receive-path debugging.

Risks and test signals: Risks are hot-path overhead, stale skb field access, format drift as skb metadata evolves, and inconsistent return-code meaning across call sites. Test with TX/RX traffic, GSO/checksum/VLAN cases, qdisc drops, watchdog timeouts, GRO list receive, and tracing during netdev unregister.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/net.h` completely for this pass (338 lines, 8576 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/net.h_research.md`.
