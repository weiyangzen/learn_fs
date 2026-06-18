
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_lib.sh

Purpose: Generic mirroring test helper library for tc `mirred egress mirror` validation.

Important APIs/functions: `mirror_install`, `mirror_uninstall`, `is_ipv6`, `mirror_test`, `do_test_span_dir_ips`, `quick_test_span_dir_ips`, `test_span_dir_ips`, `test_span_dir`, `do_test_span_vlan_dir_ips`, `quick_test_span_vlan_dir_ips`, `fail_test_span_vlan_dir_ips`, `quick_test_span_vlan_dir`, `fail_test_span_vlan_dir`.

Control flow: installs tc mirror filters, sends mausezahn ICMP/ICMPv6 traffic from one VRF to another, reads tc rule counters before and after, and checks expected deltas. VLAN helpers install skip_hw VLAN capture filters to avoid double counting.

State/persistence: creates and deletes tc filters on source and capture devices. It relies on topology scripts for qdisc setup and device state.

Dependencies/integration: expects `tc_rule_stats_get`, `icmp_capture_install`, `vlan_capture_install`, `MZ`, and VRF names from `lib.sh`.

Risks: `mirror_uninstall` ignores its `from_dev` argument and always deletes from `$swp1`, so callers must use that convention. Counter comparisons rely on traffic timing and sleep.

Test signals: `mirror_test` checks exact or relational packet deltas and reports via `check_err`; higher-level helpers log direction and VLAN mirror outcomes.
