# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_mirror.c

Purpose: implements TC matchall mirror offload for LAN966x ingress and egress port mirroring.

Important APIs and functions: `lan966x_mirror_port_add` validates the monitor device, updates mirror masks and monitor port, programs ANA mirror registers, and records per-port mirror IDs. `lan966x_mirror_port_del` removes a port from the relevant mirror mask, disables hardware mirroring, and clears global monitor state when no mirrors remain. `lan966x_mirror_port_stats` reports immediate action stats using deltas from `lan966x_stats_get`.

Control flow: add requires the destination to be another LAN966x port, rejects duplicate mirrors for the same ingress/egress direction, prevents changing monitor port while any mirror is active, and rejects mirroring the monitor port itself. Ingress mirroring sets `ANA_PORT_CFG_SRC_MIRROR_ENA`; egress mirroring writes the egress mirror port mask. Delete mirrors the add path and clears `ANA_MIRRORPORTS` when `mirror_count` reaches zero.

State and persistence: global state is `lan966x->mirror_monitor`, `mirror_mask[2]`, and `mirror_count`; per-port TC state stores ingress/egress mirror IDs and one `mirror_stat` baseline. Hardware mirror destination and source masks persist in ANA registers until deletion or reset.

Dependencies and integration points: called from TC matchall handling. Depends on LAN966x netdevice checking, netlink extack, ANA mirror registers, and ethtool stats aggregation for action stats.

Risks: ingress and egress share one `mirror_stat` baseline, so simultaneous stats queries for both directions can interfere. Egress delete writes `mirror_mask[0]` to `ANA_EMIRRORPORTS`, which appears to use the ingress mask rather than egress mask and is a likely bug. The hardware supports only one monitor port while any mirror is active.

Test signals: ingress mirror add/delete, egress mirror add/delete, duplicate add rejection, destination outside LAN966x rejection, monitor-port self-mirror rejection, changing monitor while active, simultaneous ingress+egress stats, and register verification for egress mask handling.
