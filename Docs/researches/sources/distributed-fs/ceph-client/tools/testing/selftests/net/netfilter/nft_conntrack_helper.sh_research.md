## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_conntrack_helper.sh

Purpose: tests nftables assignment of conntrack FTP helpers and verifies auto-assignment behavior controlled by `nf_conntrack_helper`.

Important APIs and tools: requires `socat`, `conntrack`, `nft`, namespace helpers, nft `ct helper` objects, `ct helper set`, sysctl `net.netfilter.nf_conntrack_helper`, and IPv4/IPv6 TCP connections.

Control flow: creates two namespaces connected by veth with IPv4 and IPv6 addresses. `load_ruleset_family()` installs raw-family helper rules setting the FTP helper for TCP dport 2121 in prerouting and output. It tries ip/ip6 in ns1 and inet fallback in ns2. `test_helper()` starts a TCP listener in ns2, connects from ns1, and calls `check_for_helper()` in both namespaces to assert helper presence for ruleset assignment on port 2121. It then enables auto assignment in both namespaces and tests port 21, expecting helper absence/presence semantics according to the `autoassign` flag in the check logic. IPv6 is skipped if ip6 ruleset load fails.

State and persistence: temporary netns, nft rules, conntrack entries, socat listeners; cleanup kills ns1 pids and deletes namespaces. Dependencies include FTP conntrack helper support and nft helper syntax. Risks include confusing local/global `autoassign` use in `check_for_helper()`, IPv6 conditional coverage, and stale conntrack entries if flush fails. Test signals are PASS/FAIL messages and final `ret`.
