
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_topo_lib.sh

Purpose: Generic three-host bridge topology for mirroring tests.

Important APIs/functions: `mirror_topo_h1_create/destroy`, `mirror_topo_h2_create/destroy`, `mirror_topo_h3_create/destroy`, `mirror_topo_switch_create/destroy`, `mirror_topo_create/destroy`.

Control flow: creates simple VRF-backed H1 and H2 addresses, H3 sink with clsact qdisc, bridge `br1` with VLAN filtering, `$swp1` and `$swp2` as bridged data ports, `$swp3` as mirror/underlay side port, and clsact on `$swp1`.

State/persistence: creates VRFs through `simple_if_init`, bridge `br1`, qdiscs on H3 and `$swp1`, and master relationships for switch ports.

Dependencies/integration: depends on `lib.sh` helpers and caller globals `h1`, `h2`, `h3`, `swp1`, `swp2`, `swp3`.

Risks: not standalone; callers must call `vrf_prepare` and assign globals. `mirror_topo_switch_destroy` deletes `br1`, implicitly removing bridge VLAN state that callers may add.

Test signals: downstream tests use this topology to generate mirror traffic and capture on H3 or derived devices.
