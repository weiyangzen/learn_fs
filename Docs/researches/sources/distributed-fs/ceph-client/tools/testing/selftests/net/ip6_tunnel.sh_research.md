# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ip6_tunnel.sh

Purpose: Simple IPv4-over-IPv6 and IPv6-over-IPv6 tunnel connectivity test using `ip6tnl` devices across two namespaces.

Important commands: Sources `lib.sh`, uses `setup_ns`, `cleanup_all_ns`, veth links, IPv6 transport addresses, `ip link add ... type ip6tnl mode ipip6`, `mode ip6ip6`, point-to-point IPv4 tunnel addresses, IPv6 tunnel addresses, and `ping`.

Control flow: `setup_prepare` creates a veth transport, moves endpoints into `ns1` and `ns2`, assigns two IPv6 transport address pairs, creates an IPv4 tunnel and IPv6 tunnel on each side with opposite local/remote addresses, assigns inner addresses, and brings tunnels up. The script then pings the peer IPv4 tunnel endpoint and the peer IPv6 tunnel endpoint from `ns1`.

State and persistence: Temporary namespaces and an initial transport link are removed by cleanup. No persistent state.

Dependencies and integration: Requires root, `lib.sh`, iproute2, `ip6tnl` kernel support, and ping.

Risks: Uses fixed namespace variable names from `lib.sh` and fixed addresses; failures do not distinguish tunnel creation from forwarding problems because `set -e` exits early.

Test signals: Both pings must complete within one second; any command failure fails the script.
