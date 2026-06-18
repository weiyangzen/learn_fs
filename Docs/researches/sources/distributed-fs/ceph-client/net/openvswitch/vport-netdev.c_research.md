# sources/distributed-fs/ceph-client/net/openvswitch/vport-netdev.c

## Purpose
`vport-netdev.c` implements OVS vports backed by existing or tunnel netdevices. It attaches a netdevice RX handler to feed ingress packets into the OVS datapath, links the device under the datapath local device, manages promiscuity/LRO, and supplies shared destroy logic for tunnel vports.

## Important APIs and Functions
`netdev_port_receive()` locates the vport from `skb->dev`, rejects LRO skbs, makes a private skb copy with `skb_share_check()`, pushes an Ethernet header for Ethernet devices, and calls `ovs_vport_receive()` with any skb tunnel info. `netdev_frame_hook()` consumes non-loopback RX packets and passes loopback packets through.

`ovs_netdev_link()` is shared by normal and tunnel netdev-backed vports. It takes RTNL, links the device as an upper/lower relation to the datapath local device, registers the RX handler, disables LRO, enables promiscuity, sets `IFF_OVS_DATAPATH`, and unwinds all steps on failure. `netdev_create()` allocates a vport for an existing device, takes a reference by name in the datapath namespace, rejects aliases, loopback, unsupported ARP types, and internal OVS devices, then links it.

`ovs_netdev_detach_dev()` removes the RX handler and upper link, drops promiscuity, and clears `IFF_OVS_DATAPATH` with memory barriers paired against destroy. `netdev_destroy()` handles explicit deletion and notifier-detached devices, then RCU-frees the vport and releases the netdev reference. `ovs_netdev_tunnel_destroy()` additionally deletes registered tunnel netdevices when appropriate and schedules vport release before RTNL unlock can run netdev cleanup.

`ovs_netdev_get_vport()` returns the RX handler data for OVS ports. `ovs_netdev_vport_ops` registers type `OVS_VPORT_TYPE_NETDEV`.

## Control Flow
Existing-device vport creation flows through `netdev_create()` and `ovs_netdev_link()`. Tunnel modules create their own netdevice and then call `ovs_netdev_link(vport, true)`. On ingress, the kernel RX handler routes packets into OVS. On egress, vport send uses `dev_queue_xmit()`.

## State and Persistence
Runtime state lives in the vport, netdev reference tracker, netdevice RX handler data, upper-device relationship, promiscuity count, and `IFF_OVS_DATAPATH` flag. RCU defers vport free after detach.

## Dependencies
It depends on Linux netdevice/rtnetlink APIs, VLAN/bridge helpers, OVS datapath/vport/internal-device headers, and tunnel metadata carried on skbs.

## Risks
RX handler registration and netdevice notifier paths can race with explicit deletion; barriers and double checks reduce detach races. Forgetting to drop promiscuity or upper links leaks device state. LRO packets are rejected because OVS expects parseable packets. The code must avoid attaching loopback or internal devices as normal netdev vports.

## Test Signals
Adding/removing physical devices as OVS ports, deleting underlying devices, netns teardown, ingress traffic reaching datapath, LRO rejection, tunnel vport destroy, and lockdep around RTNL/RCU paths are strong signals.
