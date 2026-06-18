# sources/distributed-fs/ceph-client/net/openvswitch/vport-gre.c

## Purpose
`vport-gre.c` implements the OVS GRE tunnel vport type using a fallback gretap netdevice. It is a small module that registers `OVS_VPORT_TYPE_GRE` and delegates most receive/send/lifetime behavior to the shared netdev vport layer.

## Important APIs and Functions
`gre_tnl_create()` allocates a vport, creates a `gretap_fb_dev_create()` device in the datapath net namespace, brings it up, assigns it to the vport, and holds a netdev reference. `gre_create()` then calls `ovs_netdev_link(vport, true)`. `ovs_gre_vport_ops` defines create, send (`dev_queue_xmit`), and destroy (`ovs_netdev_tunnel_destroy`) for GRE. Module init/exit register and unregister the ops and expose `MODULE_ALIAS("vport-type-3")`.

## Control Flow and Integration
The core vport registry dynamically loads this module for GRE vport requests. Once linked, the generic netdev RX hook processes received GRE-decapsulated packets through `ovs_vport_receive()`, and transmit uses the kernel netdevice output path.

## State and Persistence
State consists of the vport, its created GRE net_device, and held reference. All state is runtime only; the netdevice is deleted on tunnel destroy.

## Dependencies
It depends on GRE, IP tunnel, rtnetlink, net namespace, and shared OVS vport/netdev helpers.

## Risks
Error paths must unlock RTNL, free the vport, and delete failed devices correctly. There are no vport options here, so userspace GRE configuration is limited to the fallback metadata mode created by the kernel helper.

## Test Signals
Creating and deleting GRE OVS ports, module autoload by type 3, traffic through GRE tunnel ports, and failure injection around device creation/bring-up are useful signals.
