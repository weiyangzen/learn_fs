# sources/distributed-fs/ceph-client/tools/testing/selftests/net/amt.sh

Purpose: End-to-end selftest for Automatic Multicast Tunneling (AMT) gateway/relay behavior with IPv4 and IPv6 multicast forwarding.

Important APIs/types/functions: Uses four network namespaces (`LISTENER`, `GATEWAY`, `RELAY`, `SOURCE`), veth links, bridge `br0`, AMT netdevices (`mode gateway` and `mode relay`), `smcrouted/smcroutectl`, iptables/ip6tables TTL/hop-limit mangling, `socat`, `nc`, `jq`, and `wait_local_port_listen` from `lib.sh`.

Control flow: The script checks iproute2 AMT support, creates namespaces, configures listener/gateway/relay/source topology, starts multicast routing, verifies gateway discovery reports the relay IP, runs IPv4 and IPv6 receive tests in the listener while source sends multicast datagrams, then sends larger repeated multicast traffic as torture. Cleanup deletes namespaces, kills `smcrouted`, and removes temp state.

State and persistence behavior: Creates temporary namespaces, veth devices, AMT devices, a bridge, multicast routes, firewall mangle rules, and a temp directory containing an AMT pid file. All are intended to be removed by trap cleanup.

Dependencies and integration points: Requires kernel AMT support, iproute2 AMT support, `smcrouted`, `socat`, `nc`, iptables/ip6tables, multicast routing, and root privileges.

Risks: External tools and timing dominate reliability. Background receive/send synchronization uses port-listen polling and timeouts. Torture traffic uses `/dev/urandom` and large sends, which can be slow. Cleanup depends on `ERR` and trap paths.

Test signals: OK messages for AMT discovery, IPv4 forwarding, IPv6 forwarding, and both torture sends indicate AMT tunnel setup and multicast forwarding work.
