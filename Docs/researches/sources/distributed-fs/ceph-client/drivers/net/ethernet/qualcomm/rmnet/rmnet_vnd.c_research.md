# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_vnd.c

Purpose: Implements RMNET virtual network device behavior: TX entry, RX/TX statistics, MTU rules, ethtool stats and TX aggregation coalescing, net_device setup, link creation/deletion, flow control, and MTU synchronization with the real device.

Important APIs and functions: Public functions include `rmnet_vnd_setup()`, `rmnet_vnd_newlink()`, `rmnet_vnd_dellink()`, `rmnet_vnd_do_flow_control()`, `rmnet_vnd_rx_fixup()`, `rmnet_vnd_tx_fixup_len()`, `rmnet_vnd_validate_real_dev_mtu()`, and `rmnet_vnd_update_dev_mtu()`. Netdev ops cover `ndo_start_xmit`, `ndo_change_mtu`, `ndo_get_iflink`, bridge slave add/del, init/uninit, and stats64. Ettool ops expose checksum counters and TX aggregation coalescing.

Control flow: Device setup creates a raw-IP net_device with no header ops, random hardware/permanent addresses, fixed headroom, and lltx. Init allocates per-cpu stats and GRO cells; uninit frees them. TX calls `rmnet_egress_handler()` when a real device is attached, otherwise drops. Newlink validates mux uniqueness, enables checksum/SG features, sets private real_dev and mux id, derives MTU from real MTU minus MAP headroom, registers the netdev, and stores the endpoint. Dellink clears endpoint state. Flow control stops or wakes the VND TX queue.

State and persistence: `struct rmnet_priv` stores real device, mux id, per-cpu stats, GRO cells, and checksum stat counters. `struct rmnet_port` stores endpoints and aggregation parameters. Endpoint creation increments `nr_rmnet_devs`, deletion decrements it.

Dependencies and integration: Integrates with rtnetlink link ops, RMNET config endpoint lookup, MAP aggregation config, Linux ethtool coalescing, GRO cells, per-cpu u64 stats, and bridge operations from config code.

Risks and test signals: Risks include MTU/headroom miscalculation, per-cpu stat lifetime, coalescing values that permit zero-byte aggregation size, feature toggles vs checksum path assumptions, and endpoint cleanup ordering. Tests should create/delete VND links, duplicate mux ids, transmit without real_dev, flow-control queue state, ethtool stats/coalescing, MTU shrink propagation, and GRO receive stats.
