# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_police.c

Purpose: implements ingress port policer offload for TC matchall/flower actions on LAN966x.

Important APIs and functions: `lan966x_police_port_add` validates a TC police action, converts rate/burst units, programs the port policer, enables it in `ANA_POL_CFG`, and initializes action stats. `lan966x_police_port_del` disables the configured policer and clears the stored police ID. `lan966x_police_port_stats` reports deltas using netdev RX stats. Internal helpers `lan966x_police_add`, `lan966x_police_del`, and `lan966x_police_validate` handle register programming and semantic checks.

Control flow: validation requires exceed action drop, conform action pipe or accept, accept only as the last action, no peakrate/avrate/overhead, byte-rate rather than packet-rate policing, ingress direction only, no shared ingress block, and at most one policer per port. Add converts bytes/sec to kbps and then to the hardware 33 1/3 kpps-like rate unit, converts burst to 4 KB units, checks field widths, programs ANA policer mode/state/PIR config, enables the port policer, and stores the ID. Delete verifies ID and restores default policer settings.

State and persistence: per-port state is `port->tc.police_id` and `police_stat` baseline. Hardware state persists in ANA policer registers and port policer enable/order bits.

Dependencies and integration points: called from LAN966x TC matchall/flower paths. Depends on Linux flow action structures, netlink extack, LAN966x stats aggregation, and ANA policer register macros.

Risks: rate conversion is coarse and field-limited; accepted software police configurations may not map exactly to hardware. Only one ingress policer per port is tracked. Stats are derived from whole-port RX counters/drops, not policer-specific hardware counters, so unrelated traffic can affect action stats.

Test signals: valid ingress police add/delete/stats; invalid exceed/conform actions; egress rejection; shared-block rejection; duplicate police ID behavior; rate/burst boundary values; traffic drop-rate measurement; action stats under mixed traffic.
