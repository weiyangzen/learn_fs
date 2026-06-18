
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_neigh.sh

Purpose: Tests mirror-to-gretap/ip6gretap behavior when the tunnel remote neighbor entry is initially wrong and later refreshed.

Important APIs/functions: `test_span_gre_neigh`, `test_gretap`, `test_ip6gretap`, setup/cleanup from standard GRE topology.

Control flow: creates standard topology and underlay addresses. For each tunnel/direction, installs an intentionally invalid neighbor MAC for the GRE remote, installs mirror, verifies no decapsulated mirrored traffic, deletes the bad neighbor, verifies ARP/ND reinitialization makes mirroring work, then uninstalls mirror.

State/persistence: mutates neighbor table on `$swp3`, creates tc mirror/capture filters, and uses standard GRE tunnel/bridge state.

Dependencies/integration: depends on neighbor invalidation/refresh behavior, mirror helper counters, and both IPv4 and IPv6 neighbor handling.

Risks: neighbor re-resolution timing can be flaky; tests rely on the subsequent traffic generation to trigger resolution.

Test signals: zero mirrored packets with bad neighbor and positive counters after neighbor deletion for ingress and egress, gretap and ip6gretap.
