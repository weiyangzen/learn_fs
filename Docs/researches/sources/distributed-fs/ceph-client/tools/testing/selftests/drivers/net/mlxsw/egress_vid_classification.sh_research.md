# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/egress_vid_classification.sh

## Purpose

Tests that egress VID classification selects the correct bridge RIF independent of configuration order.

## Important APIs, Types, and Functions

Creates three hosts and a switch bridge/RIF topology with VLAN 10 and an external routed VLAN subinterface. Helpers `bridge_rif_add`, `bridge_rif_del`, `port_vid_map_rif`, and `rif_port_vid_map` use devlink RIF occupancy and TC flower counters to validate hardware routing.

## Control Flow

Setup builds VRFs, host VLAN subinterfaces, a bridge with controlled IPv6 address generation, switch VLAN devices, neighbor entries, and egress clsact filters. One test creates the port-VID to FID mapping before adding the bridge RIF; the other adds the RIF first and then the mapping. Both ping across the routed boundary and require hardware-forwarded TC hits.

## State and Persistence Behavior

State includes VLAN devices, bridge membership, bridge IP address/RIF allocation, neighbor entries, routes, TC filters, and devlink `rifs` resource occupancy. Cleanup reverses each component.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

The test depends on accurate RIF occupancy accounting and on neighbor prepopulation to avoid a first software-forwarded packet. Configuration-order bugs can be masked if TC counters are not offloaded or if routes resolve through software.

## Test Signals

Signals are devlink `rifs` occupancy increasing by one after bridge address addition and TC `skip_sw` packet counts during pings.
