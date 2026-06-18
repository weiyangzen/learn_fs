## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_tc_matchall.c

Purpose: this file handles tc `matchall` classifier offload for whole-port actions. It supports one action per filter and delegates policing, mirroring, and goto-chain actions to LAN966x helper modules.

Important APIs and functions: `lan966x_tc_matchall()` dispatches replace, destroy, and stats commands. `lan966x_tc_matchall_add()` enforces exactly one action and maps `FLOW_ACTION_POLICE`, `FLOW_ACTION_MIRRED`, and `FLOW_ACTION_GOTO`. `lan966x_tc_matchall_del()` chooses the delete helper by comparing the filter cookie with per-port police and mirror IDs. `lan966x_tc_matchall_stats()` reports police or mirror stats and rejects unsupported goto stats.

Control flow: replace validates `flow_offload_has_one_action()`, then calls `lan966x_police_port_add()`, `lan966x_mirror_port_add()`, or `lan966x_goto_port_add()` with ingress/egress context and extack. Destroy checks whether the cookie belongs to the active police ID, ingress mirror ID, or egress mirror ID, otherwise treats it as a goto rule. Stats follow the same cookie matching but only police and mirror expose stats.

State and persistence: this file does not store state itself. It relies on `port->tc.police_id`, `port->tc.ingress_mirror_id`, and `port->tc.egress_mirror_id` maintained by delegated helpers. Hardware state is in policing/mirroring/goto programming outside this file.

Dependencies and integration: called by `lan966x_tc.c` classifier block callbacks; integrates with driver policing, mirroring, and VCAP goto helpers. Uses kernel flow action structures and netlink extack for diagnostics.

Risks: one-action-only policy rejects valid Linux matchall filters that combine actions. Cookie-based delete routing can misroute if helper state is stale or cookies collide. Stats for goto actions are unsupported, so users may see errors for stats requests after a goto offload. Test signals include add/delete/stats for police and mirror on ingress/egress, add/delete for goto, duplicate-action rejection, unsupported action rejection, and stale-cookie destroy behavior.
