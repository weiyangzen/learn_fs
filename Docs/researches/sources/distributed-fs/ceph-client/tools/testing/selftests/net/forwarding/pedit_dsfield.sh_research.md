
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/pedit_dsfield.sh

Purpose: Tests tc pedit rewriting of IPv4 DS field and IPv6 traffic class, including full byte, DSCP-only, ECN-only, and DSCP+ECN chained edits.

Important APIs/functions: topology helpers; `do_test_pedit_dsfield_common`, `do_test_pedit_dsfield`, `do_test_ip_dsfield`, `do_test_ip_dscp`, `do_test_ip_ecn`, `do_test_ip_dscp_ecn`, `do_test_ip6_dsfield`, `do_test_ip6_dscp`, `do_test_ip6_ecn`; exported test wrappers.

Control flow: creates H1-H2 bridge through `$swp1/$swp2`, installs pedit filter at either ingress `$swp1` or egress `$swp2`, installs H2 ingress probe matching rewritten `ip_tos`, sends TCP packets with initial TOS 0x7d, waits for H2 counter, checks pedit rule counter, and removes filters.

State/persistence: creates bridge `br1`, VRFs, clsact qdiscs, pedit/flower filters, and optionally disables `bridge-nf-call-iptables`.

Dependencies/integration: imports `tc_common.sh` for `tc_rule_handle_stats_get`, uses `busywait`, `MZ`, and `lib.sh`.

Risks: `HIT_TIMEOUT` is defined but code uses `TC_HIT_TIMEOUT` from `tc_common.sh`; environment mismatch could affect waits. Exact traffic-class matching can be sensitive to checksum/offload behavior.

Test signals: H2 ingress sees at least 10 packets with expected DS/traffic-class bits and pedit rule counters increment at both ingress and egress loci.
