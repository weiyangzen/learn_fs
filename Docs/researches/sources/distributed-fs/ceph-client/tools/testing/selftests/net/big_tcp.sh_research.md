# sources/distributed-fs/ceph-client/tools/testing/selftests/net/big_tcp.sh

Purpose: Tests IPv4 and IPv6 BIG TCP/GRO/GSO behavior across a routed three-namespace topology, including netfilter conntrack trimming interaction via `tc ct`.

Important APIs/types/functions: Uses client/router/server namespaces, veths, `gro_ipv4_max_size`, `gso_ipv4_max_size`, `gro_max_size`, `gso_max_size`, `ethtool -K` toggles, `tc flower action ct`, iptables/ip6tables raw length counters, `netserver`, and `netperf`.

Control flow: Setup configures namespaces, addresses, routes, BIG TCP device limits, forwarding, and conntrack `tc` filters, then starts `netserver`. For IPv4 and IPv6, `testup()` runs five combinations of client TSO, router GRO/GSO, and server GRO. Each `do_test()` enables counters for packets larger than 65535 bytes, runs a large-write TCP_STREAM netperf, verifies large packets appeared at router and server, removes counters, and reports pass/fail.

State and persistence behavior: Creates namespaces, veths, qdiscs/filters, netfilter raw rules, sysctls, netserver process, and offload settings. Trap cleanup kills netserver and removes namespaces/links.

Dependencies and integration points: Requires `netperf/netserver`, iproute2 support for BIG TCP link attributes, ethtool offload control, iptables/ip6tables, `tc ct`, IPv4/IPv6 forwarding, and root.

Risks: External netperf availability and timing affect results. The script uses `ip net exec` forms; environment must support that alias. Cleanup assumes router links exist. Counters are textual parsed with grep/awk, which can be brittle.

Test signals: PASS rows for all toggle combinations under `NF=4` and `NF=6`, followed by `***v4 Tests Done***` and `***v6 Tests Done***`, indicate large TCP packets traversed expected points.
