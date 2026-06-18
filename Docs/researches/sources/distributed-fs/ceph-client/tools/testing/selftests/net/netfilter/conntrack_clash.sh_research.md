## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_clash.sh

Purpose: tests conntrack clash-resolution accounting for concurrent UDP flows, both through nft DNAT load balancing and without NAT on loopback.

Important APIs and tools: requires `nft`, `conntrack`, `socat`, helper `./udpclash`, namespace helpers, nft `numgen random mod` maps, and `conntrack -S` counters including `clash_resolve`.

Control flow: sets up two client namespaces and one router namespace. The router receives a NAT ruleset that DNATs a fixed UDP destination port to one of three backend ports. Helper functions create simple forward rules, spawn UDP echo servers, configure addresses/routes/forwarding, and verify ping connectivity. `run_clash_test()` invokes `udpclash` up to ten times and inspects `conntrack -S`; if any namespace reports a nonzero clash resolution delta, the test passes. If timing never triggers the race, it returns kselftest xfail rather than hard failure.

State and persistence: temporary namespaces, nft rules, socat servers, and conntrack state are cleaned with namespace removal. Dependencies include helper binary and timing-sensitive concurrent inserts. Risks include legitimate xfail when the race does not happen, hidden failure if `udpclash` times out but stats still show clash resolution, and reliance on exact conntrack stat names. Test signals are PASS/XFAIL/INFO lines and final `ret`.
