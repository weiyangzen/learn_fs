# sources/distributed-fs/ceph-client/tools/testing/selftests/net/broadcast_pmtu.sh

Purpose: Tests that a broadcast route's MTU is respected for large broadcast pings.

Important APIs/types/functions: Uses two namespaces, veth with mismatched MTUs, local broadcast route manipulation, `ping -f -M want -s 8000 -b`, and ICMP broadcast response sysctl.

Control flow: Setup creates client/server namespaces and veth, sets client MTU 9000 and server MTU 1500, configures addresses, reads the client's local broadcast route, deletes it, re-adds it with MTU 1500, and enables broadcast echo replies on the server. The final command sends a large broadcast ping and the script exits with that result.

State and persistence behavior: Creates namespaces, veths, routes, and a server sysctl. Cleanup deletes link and namespaces.

Dependencies and integration points: Requires root, IPv4, ping supporting `-M want`, and route MTU handling.

Risks: It lacks explicit SKIP handling for missing tools. It relies on parsing `ip route show table local type broadcast` into an array and reusing it exactly.

Test signals: Exit status 0 from the large broadcast ping indicates route MTU behavior allowed correct fragmentation/PMTU handling.
