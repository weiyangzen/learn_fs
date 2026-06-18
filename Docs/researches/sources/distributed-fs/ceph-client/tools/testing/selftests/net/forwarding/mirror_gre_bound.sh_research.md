
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_bound.sh

Purpose: Tests mirror-to-`gretap`/`ip6gretap` when tunnel devices are bound to an underlay dummy device in a separate underlay VRF, modeling overlay/underlay separation.

Important APIs/functions: local topology helpers `h1_create`, `h2_create`, `h3_create`, `switch_create`; tests `test_gretap` and `test_ip6gretap`; helper functions from `mirror_gre_lib.sh`.

Control flow: builds H1/H2 bridge, H3 tunnel endpoints, underlay interface `$swp3`, dummy `ul`, overlay VRF `vrf-ol`, and bound tunnel devices `gt4`/`gt6`. Tests mirror ingress and egress on `$swp1` and verify decap on H3.

State/persistence: creates VRFs, bridge `br1`, dummy `ul`, tunnel devices, H3 sink qdiscs, tc mirror filters, and underlay addresses.

Dependencies/integration: relies on `tunnel_create ... dev ul`, VRF master assignment, and mirror helper assertions.

Risks: destroy order deletes `vrf-ol` before tunnels, so kernel behavior with enslaved devices matters. Bound-tunnel offload support is the likely target risk.

Test signals: mirrored ICMP request/reply traffic is captured on `h3-gt4` and `h3-gt6` for both ingress and egress directions.
