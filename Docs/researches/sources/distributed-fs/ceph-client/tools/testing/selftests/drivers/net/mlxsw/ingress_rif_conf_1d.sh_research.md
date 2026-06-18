# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/ingress_rif_conf_1d.sh

## Purpose

Tests ingress RIF configuration order for VLAN subinterfaces enslaved to a VLAN-unaware bridge.

## Important APIs, Types, and Functions

Creates H1/H2/H3 VLAN 10 hosts, switch VLAN devices, bridge `br0`, a routed switch VLAN toward H3, and helpers `bridge_rif_add`, `bridge_rif_del`, `port_vid_map_rif`, and `rif_port_vid_map`. It uses devlink RIF occupancy and TC hardware counters.

## Control Flow

Setup disables automatic IPv6 address generation on the bridge, prepares host VLAN interfaces and routes, creates switch VLAN mappings, and preloads a neighbor to avoid software forwarding. One test adds a port-VID mapping before bridge RIF creation; the other creates the RIF before adding the mapping. Both ping H3 from H1.10 and require hardware TC hits on SWP3.

## State and Persistence Behavior

State includes bridge/VLAN interfaces, bridge RIF address, RIF resource occupancy, routes, neighbor entries, and TC filters. Cleanup deletes VLANs, bridge, filters, routes, and VRFs.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

Order-sensitive bugs can be hidden by neighbor misses or software forwarding, hence the explicit neighbor replacement and `skip_sw` counters. RIF occupancy checks depend on devlink resource accounting settling after address changes.

## Test Signals

Signals are one new RIF after bridge address addition and TC `skip_sw` egress packet counts during routed pings.
