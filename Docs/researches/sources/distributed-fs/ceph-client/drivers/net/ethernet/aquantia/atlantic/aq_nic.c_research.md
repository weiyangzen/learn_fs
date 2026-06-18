<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_nic.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_nic.c

Purpose: implements the common Atlantic NIC lifecycle and netdev-facing behavior above the chip-specific `aq_hw_ops` and firmware operations. It owns RSS defaults, vector sizing, netdev registration, link monitoring, TX mapping, ethtool link settings, filters, traffic-class setup, power, and shutdown sequencing.

Important APIs/functions: `aq_nic_cfg_start`, `aq_nic_ndev_register`, `aq_nic_init`, `aq_nic_start`, `aq_nic_xmit`, `aq_nic_xmit_xdpf`, `aq_nic_stop`, `aq_nic_deinit`, `aq_nic_get_stats`, `aq_nic_set_link_ksettings`, `aq_nic_setup_tc_mqprio`, and filter reservation/release helpers. Static service functions drive link/status refresh and polling mode.

Control flow: PCI probe allocates the netdev and calls config, netdev init, and registration. Open paths call `aq_nic_init` to reset hardware, initialize firmware/PHY/PTP/rings, then `aq_nic_start` to program filters, start vectors/PTP rings, enable interrupts, and start queues. TX maps skb or XDP fragments into ring buffers before calling `hw_ring_tx_xmit`. Stop disables queues, timers, IRQs, vectors, PTP rings, and hardware.

State and persistence: state is in `aq_nic_s`, including atomic readiness flags, `aq_nic_cfg`, rings/vectors, timers, link status, multicast/VLAN/filter state, PTP pointer, PCI state, and firmware mutex. Persistent device state is programmed into firmware/hardware, but no filesystem persistence exists.

Dependencies and integration: depends on Linux netdev, ethtool, timers, NAPI vectors, PCI IRQ allocation, firmware ops, `aq_ring`, `aq_vec`, PHY, PTP, filters, and optional MACsec. It is the central integration point between netdev operations and chip-specific A0/B0/ATL2 hardware methods.

Risks: vector count rounding and TC remapping can change queue topology; QoS can auto-disable PTP; TX mapping must unwind DMA mappings exactly on errors; link changes reprogram interrupt moderation and flow control; firmware calls require `fwreq_mutex`; hot-unplug paths rely on presence checks. Test signals include netdev probe/open/close, link up/down, ethtool speed changes, XDP TX, TC mqprio/rate-limit, PTP enablement, suspend/resume, and DMA mapping failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_nic.c -->
