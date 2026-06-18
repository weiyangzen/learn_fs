
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_changes.sh

Purpose: Exercises dynamic configuration changes affecting mirror-to-gretap/ip6gretap offload and software behavior.

Important APIs/functions: `test_span_gre_ttl`, `test_span_gre_tun_up`, `test_span_gre_egress_up`, `test_span_gre_remote_ip`, `test_span_gre_tun_del`, `test_span_gre_route_del`, plus grouped tests `test_ttl`, `test_tun_up`, `test_egress_up`, `test_remote_ip`, `test_tun_del`, `test_route_del`.

Control flow: standard GRE mirror topology with underlay addresses. Tests install mirrors, then change tunnel TTL, tunnel up/down, egress port up/down, tunnel remote address, delete/recreate tunnel devices, and remove/readd underlay routes, checking mirroring fails and recovers as appropriate.

State/persistence: mutates tunnel attributes, interface state, routes, sysctl `net.ipv6.conf.$swp3.keep_addr_on_down`, and tc mirror/capture filters.

Dependencies/integration: uses `mirror_gre_topo_lib.sh`, `mirror_gre_lib.sh`, ping for neighbor resolution, and tc counters.

Risks: timing after link changes and neighbor resolution can cause flakiness; sleeps are used to stabilize. Recreating tunnels intentionally does not preserve existing mirror binding, so the test reinstalls the mirror.

Test signals: expected zero counters while bad/down/deleted/unrouted state is active and `>=10` counters after correcting the configuration.
