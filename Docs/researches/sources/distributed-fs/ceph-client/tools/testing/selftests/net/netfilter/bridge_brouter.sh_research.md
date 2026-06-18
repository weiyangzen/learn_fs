## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/bridge_brouter.sh

Purpose: validates bridge "brouting" behavior, where ebtables BROUTING redirects selected bridged IPv4/ICMP frames into L3 routing rather than normal bridge forwarding.

Important APIs and tools: requires `ebtables`, uses namespace helpers, bridge/veth setup, IPv4 forwarding sysctls on bridge ports, `ebtables -t broute`, `ebtables -t filter`, and `ping`.

Control flow: creates a bridge namespace connected to two host namespaces by veths, bridges both veths, assigns bridge and endpoint IPv4 addresses, and verifies baseline bridged connectivity. `test_ebtables_broute()` installs a BROUTING redirect/drop rule for ICMP, first verifies ping fails while interface forwarding is off, then enables forwarding and verifies routed connectivity. It flushes broute to verify normal bridging, installs a bridge FORWARD drop, verifies bridge forwarding is blocked, then reinstalls broute and verifies routing still succeeds around the bridge filter drop.

State and persistence: namespace, bridge, routes, and ebtables rules are temporary and cleaned by `cleanup_all_ns`. Dependencies include legacy ebtables broute support, bridge module support, and root. Risks include legacy ebtables backend differences and short ping timeout sensitivity. Test signals are PASS/ERROR lines and the function exit status.
