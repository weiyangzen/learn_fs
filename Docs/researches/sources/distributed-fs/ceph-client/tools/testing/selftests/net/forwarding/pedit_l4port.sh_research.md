
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/pedit_l4port.sh

Purpose: Tests tc pedit rewriting of TCP and UDP source/destination ports.

Important APIs/functions: `do_test_pedit_l4port_one`, `do_test_pedit_l4port`, exported tests `test_udp_sport`, `test_udp_dport`, `test_tcp_sport`, `test_tcp_dport`.

Control flow: creates bridged H1-H2 topology with clsact qdiscs, installs pedit on `$swp1 ingress` or `$swp2 egress`, installs H2 ingress flower probe matching rewritten L4 port, sends 10 UDP/TCP packets with initial `sp=54321,dp=12345`, and checks H2 and pedit counters.

State/persistence: creates bridge, VRFs, qdiscs, pedit filters, and H2 ingress probe filters. Cleanup removes topology and qdiscs.

Dependencies/integration: depends on `tc_common.sh` counter helpers, `MZ`, and kernel pedit support for TCP/UDP port fields.

Risks: `ALL_TESTS` omits `ping_ipv6` even though function exists; only IPv4 L4 pedit paths are tested. Checksums may be affected by offload but test validates tc-level field match.

Test signals: for ports 1, 11111, and 65535, H2 flower probes and pedit rule counters see at least 10 packets for each protocol/field/locus combination.
