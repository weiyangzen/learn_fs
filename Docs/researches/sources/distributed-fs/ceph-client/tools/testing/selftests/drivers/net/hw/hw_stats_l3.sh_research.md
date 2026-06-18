# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/hw_stats_l3.sh

Purpose: Tests L3 hardware statistics enablement/reporting on routed VLAN interfaces for IPv4 and IPv6 RX/TX paths.

Important APIs/functions: `h1_create/destroy`, `h2_create/destroy`, router port create/destroy helpers, `setup_prepare()`, `cleanup()`, `ping_ipv4()`, `ping_ipv6()`, packet send helpers, `___test_stats()`, `__test_stats()`, per-direction/per-IP tests, `respin_enablement()`, `reapply_config()`, `__test_stats_report()`, `test_destroy_enabled()`, and `test_double_enable()`.

Control flow: The script builds a routed two-host/two-router-port topology with VLAN 200 and VRFs/routes, verifies ping, enables L3 hardware stats on RX/TX paths, sends packets, checks stat deltas, toggles/reapplies configuration, verifies report output, tests destruction while enabled, and double-enable semantics.

State and persistence: Creates VLANs, VRFs/routes, L3 stats configuration, TC/common forwarding state, and interface counters. Cleanup removes topology.

Dependencies and integration points: Requires hardware L3 stats support, VLAN, VRF/route setup, forwarding and TC common libraries, IPv4/IPv6 traffic.

Risks and test signals: Failures reveal L3 stats enable/report/delete bugs, stat direction mixups, persistence across reapply, or teardown leaks.
