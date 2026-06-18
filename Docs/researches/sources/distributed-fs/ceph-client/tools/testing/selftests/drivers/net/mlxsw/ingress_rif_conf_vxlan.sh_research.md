# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/ingress_rif_conf_vxlan.sh

## Purpose

Tests ingress RIF behavior when VXLAN VNI-to-FID mappings are created before or after a VLAN RIF.

## Important APIs, Types, and Functions

Defines H1, switch VXLAN bridge, VRF/routed port setup, raw payload generation, `vlan_rif_add`, `vlan_rif_del`, `vni_fid_map_rif`, and `rif_vni_fid_map`. It uses VXLAN devices, bridge VLANs, TC counters, and devlink RIF occupancy.

## Control Flow

Setup creates a VXLAN tunnel/bridge context and a routed VRF port, then tests two configuration orders: create VNI/FID mapping then add the VLAN RIF, and add the RIF then create VNI/FID mapping. Crafted payloads are injected to prove decapsulated traffic is routed through the correct RIF in hardware.

## State and Persistence Behavior

State includes VXLAN devices, bridge/VLAN/VNI mappings, VRF and routes, TC filters, devlink RIF counters, and temporary payload traffic.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

VXLAN offload constraints are strict; wrong checksum, bridge, or VNI settings can make the test fail before RIF classification. Raw payload construction and neighbor state are also fragile. Cleanup must remove tunnel devices and bridge mappings in reverse order.

## Test Signals

Signals are RIF occupancy after VLAN RIF addition and TC counter hits showing routed decapsulated packets.
