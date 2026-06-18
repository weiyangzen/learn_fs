# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_handlers.c

Purpose: Implements the RMNET ingress and egress packet handlers between a real lower net_device and virtual RMNET devices. It classifies MAP command/data frames, selects logical endpoints by mux id, bridges frames when configured, and wraps outbound virtual-device traffic in MAP headers.

Important APIs and functions: `rmnet_rx_handler()` is the lower-device RX handler. `rmnet_egress_handler()` is called by virtual netdev TX. `rmnet_map_ingress_handler()` handles Ethernet headroom correction and optional deaggregation. `__rmnet_map_ingress_handler()` processes one MAP frame. `rmnet_map_egress_handler()` builds MAP plus checksum headers and may aggregate TX. `rmnet_deliver_skb()` finalizes skb headers, updates VND RX stats through `rmnet_vnd_rx_fixup()`, and feeds GRO cells.

Control flow: RX linearizes the skb, ignores loopback packets, gets the port with RCU lookup, then dispatches by `rmnet_mode`. VND mode parses MAP, validates mux endpoint, strips MAP/checksum headers, sets `skb->protocol`, trims padding, and delivers to the virtual egress device. Bridge mode pushes an existing MAC header and transmits to `bridge_ep`. TX moves `skb->dev` from virtual to real device, uses the virtual private mux id, invokes MAP egress formatting, records virtual TX stats, and queues to the real device.

State and persistence: Persistent state is in `struct rmnet_port`, endpoint tables, `struct rmnet_priv`, per-cpu VND stats, and aggregation fields owned by `rmnet_map_data.c`. The file mutates skb metadata and drops packets on invalid mux ids, missing endpoints, checksum parse errors, or headroom allocation failure.

Dependencies and integration: Depends on `rmnet_config` for port/endpoint lookup and flags, `rmnet_map` for MAP protocol helpers, `rmnet_vnd` for stats/fixups, Linux RX handler API, GRO cells, SKB helpers, and `dev_queue_xmit()`.

Risks and test signals: Key risks are malformed MAP lengths, MAPv5 next-header expectations, aggregation error returns, and bridge-mode header handling. Tests should exercise mux routing, bad mux drops, command packets with/without command flag enablement, CKSUMV4 and CKSUMV5 paths, deaggregation, aggregation enabled vs disabled, bridge mode, and stat/drop counters.
