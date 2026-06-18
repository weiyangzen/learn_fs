<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/vlan_dev.c -->
# sources/distributed-fs/ceph-client/net/8021q/vlan_dev.c

This file defines the VLAN netdevice operations, header operations, statistics, feature inheritance, and lower-device pass-through hooks. It is the behavior surface for a VLAN interface after it has been created.

Transmit flow starts in `vlan_dev_hard_start_xmit()`: it adds a hardware-accelerated VLAN tag when header reordering is enabled or the skb lacks an inline VLAN header, switches `skb->dev` to the real device, sends through netpoll or `dev_queue_xmit()`, and updates per-CPU TX stats or drops. Header creation is split between `vlan_dev_hard_header()` for inline VLAN headers and `vlan_passthru_hard_header()` for hardware-offload-capable devices. MTU, MAC address, multicast/unicast sync, RX flags, hwtstamp, MII ioctl, neighbor setup, FCoE, MACsec offload, and forward-path operations are delegated to or constrained by the real device.

Lifecycle functions include `vlan_dev_init()`, `vlan_dev_uninit()`, `vlan_dev_free()`, `vlan_dev_open()`, and `vlan_dev_stop()`. Init copies lower-device flags/features, sets header ops based on VLAN offload capability, allocates per-CPU stats, and holds the real device. Open verifies lower device state unless loose binding is set, maintains unicast filters for non-inherited MACs, records the real MAC, requests GVRP/MVRP joins, and mirrors carrier. Stop unsyncs filters and carrier. Free releases stats and the lower-device reference.

State includes `struct vlan_dev_priv`, ingress and RCU-protected egress priority maps, per-CPU stats, optional netpoll state, inherited real-device address, and lower-device reference tracking. Synchronization uses RTNL for configuration, RCU for egress maps, per-CPU u64 stat sequences, and netdevice core serialization.

Risks include skb tagging/header-order mistakes, priority-map lifetime, lower-device reference leaks, MAC filter imbalance, feature mismatch for Q-in-Q, netpoll cleanup, and optional MACsec/FCoE delegation. Tests should cover transmit with reorder on/off and offload/no-offload, egress/ingress QoS maps, open/stop with inherited/custom MACs, stats aggregation, MTU limits, feature changes, and optional netpoll/MACsec paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/vlan_dev.c -->
