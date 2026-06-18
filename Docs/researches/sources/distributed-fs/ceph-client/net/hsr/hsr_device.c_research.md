<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_device.c -->
# sources/distributed-fs/ceph-client/net/hsr/hsr_device.c

## Purpose
Implements virtual HSR/PRP net_device behavior: carrier and operstate propagation, MTU and feature handling, transmit entry point, supervision frame generation, VLAN/multicast propagation, protocol operation selection, and device finalization.

## APIs, Types, and Functions
Exports or defines `hsr_check_carrier_and_operstate()`, `hsr_get_max_mtu()`, `hsr_del_ports()`, `hsr_dev_setup()`, `is_hsr_master()`, `hsr_get_port_ndev()`, `hsr_get_port_type()`, and `hsr_dev_finalize()`. Key internal functions include `hsr_dev_xmit()`, `send_hsr_supervision_frame()`, `send_prp_supervision_frame()`, `hsr_announce()`, `hsr_proxy_announce()`, VLAN add/kill handlers, and protocol op tables `hsr_ops` and `prp_ops`.

## Control Flow, State, and Persistence
Carrier checks turn the master carrier on if any non-master port is administratively and operationally up, set master operstate, and arm or delete supervision timers. TX from the virtual master resets skb MAC metadata, locks `seqnr_lock`, and calls `hsr_forward_skb()`. Supervision timers allocate control skbs, fill HSR or PRP supervision tags and payloads, increment normal or supervision sequence counters, optionally add RedBox TLVs, pad to Ethernet minimum, and forward. Finalization initializes lists, locks, self node, sequence counters, timers, multicast address, protocol ops, master/slave/interlink ports, offload flags, PRP slave MAC alignment, RedBox state, debugfs, and prune timers. Persistent runtime state lives in `struct hsr_priv`: ports, node databases, sequence counters, timers, protocol version, RedBox metadata, and offload flags.

## Dependencies and Integration
Depends on net_device operations, HSR slave management, frame registry, forwarding, netlink notifications, timers, RCU port traversal, VLAN helpers, debugfs helpers, and hardware offload feature bits. It integrates with `hsr_netlink.c` for device creation and `hsr_main.c` for netdev event handling.

## Risks and Test Signals
Risks include timer lifetime during port/device teardown, MTU bounds across heterogeneous slaves, supervision skb construction for VLAN/PRP/RedBox variants, offload feature assumptions, PRP MAC mutation of slave B, and partial finalization unwind. Test signals include master open/close warnings, carrier changes from slaves, MTU rejection, TX forwarding, supervision and proxy supervision frames, VLAN propagation unwind, debugfs creation, RedBox interlink setup, and finalization failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_device.c -->
