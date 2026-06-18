
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/pedit_ip.sh

Purpose: Tests tc pedit rewriting of IPv4 and IPv6 source/destination addresses on bridge ingress and egress.

Important APIs/functions: `do_test_pedit_ip`, `do_test_pedit_ip4`, `do_test_pedit_ip6`, tests `test_ip4_src`, `test_ip4_dst`, `test_ip6_src`, `test_ip6_dst`.

Control flow: creates bridged H1-H2 topology, installs pedit action on `$swp1 ingress` or `$swp2 egress`, installs H2 ingress flower probe matching the rewritten address, sends 10 packets with mausezahn, waits for H2 counter, verifies pedit counter, and removes filters.

State/persistence: creates bridge `br1`, VRFs, clsact qdiscs, pedit/flower filters, and temporarily disables bridge netfilter if present.

Dependencies/integration: uses `tc_common.sh`, `busywait`, `tc_rule_handle_stats_get`, `MZ`, and `lib.sh`.

Risks: rewriting destination addresses to off-subnet values still relies on L2 delivery from mausezahn, not normal routing. Hardware pedit support may differ between ingress and egress.

Test signals: H2 ingress probe receives at least 10 packets with rewritten IPv4/IPv6 src or dst, and the pedit rule records at least 10 hits for both loci.
