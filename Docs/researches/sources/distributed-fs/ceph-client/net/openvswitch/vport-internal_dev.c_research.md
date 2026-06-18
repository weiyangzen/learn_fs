# sources/distributed-fs/ceph-client/net/openvswitch/vport-internal_dev.c

## Purpose
`vport-internal_dev.c` implements OVS internal vports, which are kernel-created Ethernet netdevices representing datapath ports such as the local port. They let packets enter the datapath from a netdevice transmit path and let datapath output deliver packets up to the host networking stack.

## Important APIs, Types, and Functions
`struct internal_dev` stores the owning `struct vport`. `internal_dev_xmit()` is the netdevice transmit function: it records skb length, calls `ovs_vport_receive()` under RCU, updates software TX stats on success, and increments tx_errors on failure.

`do_setup()` configures the netdevice: Ethernet setup, max MTU, netdev ops, no TX skb sharing, live address change, OVS/internal flags, no queue, software GSO and checksum features, VLAN offload features, random MAC, ethtool ops, and rtnl link kind. `internal_dev_create()` allocates the vport, allocates the netdevice, sets namespace and desired ifindex, records the vport in private data, marks the local port as netns immutable, registers the netdevice under RTNL, sets the destructor, enables promiscuity, and starts the queue.

`internal_dev_destroy()` stops the queue, drops promiscuity, and unregisters the netdevice; unregister waits for an RCU grace period. `internal_dev_recv()` is the vport send function for packets output to the internal device: it drops if the device is down, clears dst and conntrack state, sets host packet type and protocol via `eth_type_trans()`, updates RX stats, and injects with `netif_rx()`.

`ovs_internal_vport_ops` registers type `OVS_VPORT_TYPE_INTERNAL`. Public helpers identify internal devices, get their vport, and register/unregister rtnl link and vport ops.

## Control Flow
For host-originated packets sent on an internal interface, the netdevice start_xmit path calls into OVS receive and datapath processing. For datapath output to an internal vport, action execution calls the vport `send` op, which delivers to the Linux receive path. Creation and deletion are driven by vport generic-netlink commands and datapath lifecycle.

## State and Persistence
Runtime state is the netdevice, vport, private pointer, netdevice flags/features, queues, and per-device software stats. The vport is freed by the netdevice private destructor after unregister.

## Dependencies
It depends on Linux netdevice, ethtool, rtnetlink, dst/xfrm helpers, and shared OVS `datapath.h`, `vport.h`, and `vport-netdev.h`.

## Risks
Ownership between vport and netdevice is delicate: create failure, unregister, destructor, and vport free must not double free. Packets are consumed by `ovs_vport_receive()`, so xmit must not touch skb afterward. Output path must clear dst and conntrack references before host delivery. Local port namespace immutability prevents cross-netns surprises.

## Test Signals
Creating/deleting datapaths and internal ports, host ping/traffic through internal interfaces, output to down internal devices, netns teardown, stats correctness, and KASAN/lockdep around unregister validate behavior.
