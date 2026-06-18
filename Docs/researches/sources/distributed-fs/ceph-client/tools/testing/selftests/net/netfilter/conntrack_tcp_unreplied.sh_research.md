## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_tcp_unreplied.sh

Purpose: checks that an UNREPLIED TCP conntrack entry eventually times out and that a later NAT redirect can create a fresh redirected connection.

Important APIs and tools: requires `nft`, `conntrack`, `socat`, namespace helpers, veth pair, nft counters, `nf_conntrack_tcp_timeout_syn_sent`, `conntrack -L`, and route/DNAT setup.

Control flow: builds two namespaces connected by veth. ns1 routes a virtual IP through ns2; ns2 has forwarding and a TCP listener. ns2 nft rules count initial SYNs to 10.99.99.99:80 and redirected DNAT traffic. A loop from ns1 attempts repeated connections to the virtual IP before NAT exists, creating an UNREPLIED conntrack entry. The script waits until conntrack sees it, then adds a redirect/DNAT rule and waits for counters/connection state to show the stale entry expired and a redirected connection succeeded.

State and persistence: temporary namespaces, nft rules, conntrack entries, background socat/connect loops; cleanup kills namespace pids. Dependencies include conntrack timeout behavior, busywait helpers, and socat. Risks include timing windows around 10-second timeout, background process cleanup, and counter expectations that depend on retries. Test signals are INFO/ERROR/PASS lines and final `ret`.
