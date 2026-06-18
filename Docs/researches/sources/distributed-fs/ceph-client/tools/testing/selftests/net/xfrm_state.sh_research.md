# sources/distributed-fs/ceph-client/tools/testing/selftests/net/xfrm_state.sh

Purpose: XFRM/IPsec state behavior test for ICMP error source address and MTU exceeded handling over tunnel mode ESP across multi-hop IPv4 and IPv6 topologies.

Important APIs/functions: declares test table for unreachable and MTU cases. Uses namespace-set builders (`setup_ns_set_v4`, `v4x`, `v6`, `v6x`), `setup_namespaces`, `setup_network`, nftables ICMP/ESP filters, and `setup_xfrm_mode()` to install ESP policies/states with AEAD rfc4106(gcm(aes)) and `flag icmp` on relevant fwd/out policies/states. `run_test()` isolates each test in a subshell with cleanup trap.

Control flow: command-line options control pause/verbose/exit-on-fail and optional test names. For each listed test, `run_test()` invokes a named test function. Each test sets up a topology, verifies base ping to reachable endpoint, then runs a ping to unreachable or oversized destination and greps for expected ICMP source and MTU text. MTU tests adjust route MTUs on r2, r3, or s2 depending on scenario.

State and persistence: temporary namespaces a/r1/s1/r2/s2/r3/b or shortened x topology, veths, routes, sysctls, nftables rules, XFRM policy/state, and globals describing last command/output. Cleanup deletes all namespaces after each test. No files.

Dependencies and integration: requires root, iproute2, nft, ping, XFRM/ESP AEAD support, and `lib.sh`. Kselftest skip code is used when setup needs root and is unavailable.

Risks: grep patterns depend on ping output wording. `run_cmd_err` always returns 0 after capturing status in `rc`, so tests must inspect `$out`/`rc` explicitly; current test functions do that by grepping output. Complex dynamic namespace variable construction is sensitive to shell behavior.

Test signals: per-test `[ PASS ]`, `[SKIP]`, or failure output with command/output when verbose. Final exitcode is 0, 1, or skip depending on aggregate results.
