## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_ipip_mtu.sh

Purpose: regression test for packet loss caused by conntrack reassembly on fragmented packets traversing an IPIP tunnel with PMTU constraints.

Important APIs and tools: requires `iptables` and `socat`, uses five namespaces, veth topology, `ip link add ipip0 type ipip`, IPv4 forwarding sysctls, MTU changes, UDP socat listener/sender, and a single conntrack match rule via iptables.

Control flow: builds Client A - Router A - WAN - Router B - Client B with IPIP tunnels between routers and WAN MTU 1400. `test_path()` starts a UDP listener on Client B, sends three 1400-byte UDP payloads from Client A, then expects exactly 1400 bytes received, demonstrating that PMTU behavior allows one successful delivery. The test first runs without conntrack, then adds `iptables -A FORWARD -m conntrack --ctstate NEW` on Router A and repeats to ensure conntrack reassembly does not drop the packet.

State and persistence: temporary namespaces, routes, ipip devices, MTUs, and iptables rule are cleaned via namespace removal. Dependencies include IPIP support, socat, iptables conntrack match, root, and PMTU propagation. Risks include timing around listener exit, strict byte expectation, and old kernels lacking the IPIP device type. Test signal is `OK`/`FAIL` from byte count and exit status.
