# sources/distributed-fs/ceph-client/net/openvswitch/vport-geneve.c

## Purpose
`vport-geneve.c` implements the OVS Geneve tunnel vport type. It creates metadata-collecting Geneve netdevices, links them into the datapath as netdev-backed vports, reports configuration options, and registers a module alias for dynamic vport-type loading.

## Important APIs, Types, and Functions
`struct geneve_port` stores the destination UDP port in vport private data. `geneve_vport()` maps a `struct vport` to that private data. `geneve_get_options()` emits `OVS_TUNNEL_ATTR_DST_PORT`.

`geneve_tnl_create()` validates that options exist and contain a u16 `OVS_TUNNEL_ATTR_DST_PORT`, allocates a vport with private storage, creates a fallback/metadata Geneve device through `geneve_dev_create_fb()`, brings it up with `dev_change_flags()`, stores the netdev pointer, and takes a netdev reference. `geneve_create()` then calls `ovs_netdev_link(vport, true)` so the generic netdev vport layer attaches RX handling and datapath upper-device linkage.

`ovs_geneve_vport_ops` supplies type `OVS_VPORT_TYPE_GENEVE`, create, destroy (`ovs_netdev_tunnel_destroy()`), get_options, and send (`dev_queue_xmit`). Module init/exit register and unregister the vport ops.

## Control Flow and Integration
Userspace requests a Geneve vport through OVS vport generic netlink. `vport.c` locates these ops, calls `geneve_create()`, and later dispatches send/destroy/get-options through the ops. Received packets arrive via the netdev RX handler in `vport-netdev.c` and are processed by `ovs_vport_receive()` with tunnel metadata from the skb.

## State and Persistence
Runtime state is a vport object, private destination-port copy, created net_device, and netdev reference. The underlying Geneve device is deleted when the tunnel vport is destroyed.

## Dependencies
It depends on `net/geneve.h`, rtnetlink/netdevice helpers, `vport.h`, and `vport-netdev.h`. It uses OVS tunnel option UAPI.

## Risks
Destination port is mandatory and must be validated. Error paths must release the vport and delete the netdevice if bring-up fails. The stored private dst port must remain consistent with the actual Geneve device because get-options reports the private copy.

## Test Signals
Module load via `vport-type-5`, creating/deleting Geneve OVS ports with a dst port, dumping options, receiving Geneve traffic with tunnel metadata, and error cases for missing/invalid options validate behavior.
