<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/vxlan_mtu_frag.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/vxlan_mtu_frag.sh

## Purpose
This test checks that large packets through a VLAN-aware bridge with an external VXLAN device and br_netfilter do not panic when VXLAN MTU forces fragmentation. Packet delivery is expected to fail; absence of kernel crash is the pass condition.

## Important APIs, Types, And Functions
The script uses `lib.sh`, `modprobe br_netfilter`, `ip`, `bridge`, `ping`, and helpers `create_topology()`, `setup_host()`, `setup_vtep()`, `setup_router()`, `setup()`, `test_large_mtu_untagged_traffic()`, `test_large_mtu_tagged_traffic()`, and `do_test()`.

## Control Flow
It checks for `br_netfilter`, creates host/vtep/router namespaces, links them with veth pairs, configures host VLAN subinterfaces, builds a VLAN-filtering bridge in the VTEP namespace, adds an external VXLAN device with VLAN-to-VNI mappings, and brings links up. Tests set VXLAN MTU to 1000 and send 2000-byte pings for VLAN-tagged and untagged traffic toward static neighbor entries.

## State, Persistence, And Dependencies
State includes namespaces, veths, VLAN subinterfaces, a bridge, VXLAN device, bridge VLAN/VNI mappings, static neighbors, and loaded br_netfilter module state. Cleanup removes namespaces. It requires bridge/VXLAN/VLAN kernel support and root privileges.

## Integration Points
This test is a netfilter/bridge/VXLAN integration regression focused on fragmentation paths with br_netfilter enabled. It exercises bridge VLAN tunnel metadata, external VXLAN mode, and oversized ICMP frames.

## Risks
Because ping failure is expected, the script can only detect command/setup errors or crashes indirectly. It does not inspect dmesg, so kernel warnings without panic may be missed. The `modprobe -n` feature check may differ from actual load behavior.

## Test Signals
Success prints the test banner and `PASS!` after traffic generation returns. Setup command failures or module absence lead to SKIP/failure; a kernel panic or hang is the primary regression signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/vxlan_mtu_frag.sh -->
