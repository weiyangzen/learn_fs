# sources/distributed-fs/ceph-client/net/batman-adv/bat_v.c

## Purpose
`bat_v.c` registers and coordinates the BATMAN V routing algorithm. It wires together ELP neighbor discovery, OGMv2 route propagation, throughput-based neighbor comparison, originator/neighbor/gateway netlink dumps, and per-hard-interface/mesh initialization.

## Important APIs and Functions
- Interface ops: `batadv_v_iface_activate`, `batadv_v_iface_enable`, `batadv_v_iface_disable`, `batadv_v_primary_iface_set`, and `batadv_v_iface_update_mac`.
- Neighbor ops: `batadv_v_hardif_neigh_init`, `batadv_v_neigh_cmp`, `batadv_v_neigh_is_sob`, and netlink neighbor dump helpers.
- Originator/gateway dumps and selection: `batadv_v_orig_dump`, `batadv_v_gw_get_best_gw_node`, `batadv_v_gw_is_eligible`, `batadv_v_gw_dump`.
- Lifecycle exports: `batadv_v_hardif_init`, `batadv_v_mesh_init`, `batadv_v_mesh_free`, and `batadv_v_init`.
- Static `batadv_batman_v` defines the algorithm callbacks registered with `batadv_algo_register`.

## Control Flow
Module init registers receive handlers for ELP and OGM2 before registering the algorithm. Hard-interface init sets throughput override to auto, default ELP interval to 500 ms, initializes aggregation queue state, and sets up the OGM aggregation delayed work. Enabling an interface starts ELP then OGMv2; failure rolls back ELP. Activation updates ELP originator fields from the selected primary interface and can mark the interface active immediately because BATMAN V has no BATMAN IV-style forward queue activation hazard. Mesh init/free allocate and release OGMv2 mesh resources through `bat_v_ogm.c`.

## State and Persistence
Persistent BATMAN V state includes per-hard-interface throughput override, ELP interval, ELP/OGM work items, OGM aggregation queue and length, per-neighbor EWMA throughput, per-neighbor-interface path throughput, gateway selection class, and per-mesh OGMv2 buffer state.

## Dependencies and Integration
Integrates with `bat_v_elp.c`, `bat_v_ogm.c`, algorithm registration, hard-interface/originator/gateway subsystems, generic netlink, and Kconfig guards through `bat_v.h`.

## Risks and Test Signals
Risks include inconsistent initialization order between ELP and OGMv2, stale primary MAC in protocol packets, throughput comparison overflow/units, gateway reselection threshold behavior, and dump cursor handling. Test signals include BATMAN V registration only when configured, interface enable rollback on ELP/OGM failure, throughput-visible neighbor/originator/gateway netlink dumps, gateway selection by effective throughput, and BATMAN V disabled builds using stubs.
