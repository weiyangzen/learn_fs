# sources/distributed-fs/ceph-client/net/openvswitch/vport-netdev.h

## Purpose
`vport-netdev.h` declares shared netdev-backed vport helpers used by normal netdev ports and tunnel vport modules.

## Important APIs
`ovs_netdev_get_vport()` maps an OVS-attached netdevice to its vport. `ovs_netdev_link()` attaches an allocated vport and its netdevice to datapath RX handling; the `tunnel` flag controls tunnel-device cleanup on failure. `ovs_netdev_detach_dev()` removes RX and upper-device attachment. `ovs_netdev_init()` and `ovs_netdev_exit()` register/unregister normal netdev vport ops. `ovs_netdev_tunnel_destroy()` is the common destroy function for tunnel vports.

## Control Flow and Integration
`vport-gre.c`, `vport-geneve.c`, and `vport-vxlan.c` create tunnel netdevices, hold references, then call `ovs_netdev_link()`. Datapath/device notifier code can call detach helpers when netdevices disappear.

## State and Persistence
The header declares APIs that manipulate runtime netdevice references, RX handlers, and vport lifetimes. It declares no standalone state.

## Dependencies
It depends on Linux netdevice/RCU headers and `vport.h`.

## Risks
Callers must pass vports with valid `dev` pointers and must use the correct destroy helper for tunnel-created devices. Mispaired link/detach can leave RX handlers or references behind.

## Test Signals
Build coverage for all tunnel modules, normal netdev port lifecycle tests, and notifier-triggered detach tests validate the contract.
