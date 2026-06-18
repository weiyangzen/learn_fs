# sources/distributed-fs/ceph-client/net/openvswitch/vport-vxlan.c

## Purpose
`vport-vxlan.c` implements the OVS VXLAN tunnel vport type. It creates collect-metadata VXLAN netdevices, supports a mandatory destination UDP port and optional GBP extension, and reuses the netdev vport layer for datapath attachment.

## Important APIs and Functions
`vxlan_get_options()` emits `OVS_TUNNEL_ATTR_DST_PORT` and, when enabled, nested `OVS_TUNNEL_ATTR_EXTENSION` with `OVS_VXLAN_EXT_GBP`. `exts_policy` validates VXLAN extension attributes. `vxlan_configure_exts()` parses nested extensions and sets `VXLAN_F_GBP`.

`vxlan_tnl_create()` requires `OVS_TUNNEL_ATTR_DST_PORT`, initializes `struct vxlan_config` with `no_share`, collect metadata, UDP zero checksum IPv6 receive, and `IP_MAX_MTU`, allocates a vport, parses optional extensions, creates a VXLAN device with `vxlan_dev_create()`, brings it up, stores the netdev, and holds a reference. `vxlan_create()` links it into OVS via `ovs_netdev_link(vport, true)`.

`ovs_vxlan_netdev_vport_ops` registers type `OVS_VPORT_TYPE_VXLAN`, destroy via `ovs_netdev_tunnel_destroy()`, get_options, and `dev_queue_xmit` send. Module alias `vport-type-4` supports autoload.

## Control Flow and Integration
Vport generic-netlink requests instantiate the VXLAN module ops. RX and TX after creation use the shared netdev-backed vport paths. Tunnel key parsing and emission in `flow_netlink.c` must agree with the GBP option represented here.

## State and Persistence
Runtime state is the created VXLAN netdevice, vport, netdev reference, configured destination port, and optional GBP flag in the VXLAN config/device.

## Dependencies
It depends on `net/vxlan.h`, UDP tunnel helpers, rtnetlink, OVS vport/netdev helpers, and OVS tunnel UAPI.

## Risks
Destination port is mandatory. Extension parsing must reject malformed nested attributes. Error paths must delete partially created devices and free vports. MTU is intentionally set high to avoid tunnel-device MTU limiting OVS output; changing it can alter datapath behavior.

## Test Signals
Creating VXLAN OVS ports with and without GBP, dumping options, rejecting missing dst port or invalid extension attributes, VXLAN tunnel traffic with metadata keys, and module autoload/unload are useful tests.
