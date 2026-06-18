# sources/distributed-fs/ceph-client/tools/testing/selftests/net/fib_nexthop_nongw.sh

Purpose: this script validates source-address selection and reachability for a route that uses a nexthop object without an explicit gateway. It creates a direct-device nexthop and verifies both `route get` and ping to a peer address work.

Important APIs and functions: it uses `setup_ns`, dummy and veth links, `ip nexthop add id 1 dev veth0`, `ip route add ... nhid 1`, `ip route get`, `ping`, plus local `run_cmd`, `log_test`, `setup`, and `cleanup` helpers.

Control flow: `setup` creates namespaces h1 and h2, gives h1 a dummy `eth0` with `192.168.0.1/24`, creates a veth pair, assigns h2 `192.168.1.1/32`, adds a default route in h2 through veth1, creates a gateway-less nexthop object in h1 on veth0, and adds a route to `192.168.1.1` through that nexthop. Main then checks route lookup and ping success.

State and persistence: namespace-local links, addresses, route, and nexthop object are removed by the exit trap. No files persist.

Dependencies and integration points: requires kernel nexthop object support and iproute2 support for gateway-less nexthops. It targets FIB behavior for directly connected nexthop objects.

Risks and test signals: the topology uses no ARP suppression beyond the comment's note, so neighbor behavior depends on normal veth semantics. Strong signals are zero exit from `ip route get` and one successful ping through the nexthop route.
