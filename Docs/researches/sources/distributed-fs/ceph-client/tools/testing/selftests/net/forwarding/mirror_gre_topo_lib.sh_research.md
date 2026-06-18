
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_topo_lib.sh

Purpose: Standard topology library for tests mirroring to `gretap` and `ip6gretap` netdevices.

Important APIs/functions: `mirror_gre_topo_h3_create/destroy`, `mirror_gre_topo_switch_create/destroy`, `mirror_gre_topo_create/destroy`; sources `mirror_topo_lib.sh`.

Control flow: reuses generic H1/H2/bridge topology, extends H3 with decapsulation tunnels `h3-gt4` and `h3-gt6`, and extends switch side with tunnel devices `gt4` and `gt6`. H3 tunnel devices are placed in `v$h3` and configured as matchall sinks for counter-based validation.

State/persistence: creates four tunnel devices, clsact/drop filters on H3-side tunnel devices, and the generic bridge/host topology from `mirror_topo_lib.sh`.

Dependencies/integration: depends on `tunnel_create`, `matchall_sink_create`, VRF created by generic H3 setup, and caller-assigned underlay addresses/routes.

Risks: tunnel devices are created before callers assign underlay addresses; tests must configure routes/addresses separately. Naming conventions are consumed by `mirror_gre_lib.sh`.

Test signals: not a standalone test; downstream tests observe counters on `h3-gt4`/`h3-gt6` after mirror actions to `gt4`/`gt6`.
