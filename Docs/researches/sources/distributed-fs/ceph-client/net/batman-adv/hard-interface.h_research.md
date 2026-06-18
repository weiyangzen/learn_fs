<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/hard-interface.h -->
# sources/distributed-fs/ceph-client/net/batman-adv/hard-interface.h research

Purpose: declares hard-interface states, broadcast avoidance return codes, lifecycle APIs, lookup helpers, and primary-interface access.

Important APIs and types: `enum batadv_hard_if_state` models not-in-use, to-be-removed, inactive, active, and to-be-activated. `enum batadv_hard_if_bcast` tells broadcast code whether forwarding is unnecessary because there is no recipient, only the forwarder, only the originator, or whether broadcast is OK. Exports include the notifier block, real netdev lookup, Wi-Fi predicates, hardif lookup, enable/disable, MTU update, kref release, and broadcast avoidance. Inline `batadv_hardif_put()` and `batadv_primary_if_get_selected()` encode reference handling.

Control flow and state behavior: `batadv_primary_if_get_selected()` uses RCU to read `bat_priv->primary_if` and returns a kref-protected hard interface or NULL. Callers must release it with `batadv_hardif_put()`. The header's enums define legal lifecycle transitions used by the implementation and by callers checking activity.

Dependencies and integration: includes `main.h`, kref, netdevice, RCU, and basic kernel types. It is included by most packet, routing, DAT, BLA, and gateway modules because hard-interface ownership is central to all receive/send paths.

Risks: forgetting to put selected or looked-up hard interfaces leaks references. Checking only non-NULL without checking `if_status` can route through inactive devices. Broadcast avoidance enum values are consumed as policy, so adding values requires updating switch-like callers.

Test signals: compile with all users, reference leak testing around primary selection, activity checks for netlink dumps, and broadcast avoidance behavior for zero, one, and multiple neighbors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/hard-interface.h -->
