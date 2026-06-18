# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_matchall.c

Purpose: Implements tc matchall offload for Prestera mirroring/SPAN rules.

Important APIs/types/functions: `prestera_mall_replace()`, `prestera_mall_destroy()`, and `prestera_mall_prio_get()`. Internal helpers check priority compatibility with flower rules and maintain matchall priority min/max on a flow block.

Control flow: Replace requires exactly one action, a Prestera target port, chain 0/offload eligibility, `FLOW_ACTION_MIRRED`, and `ETH_P_ALL`. It checks ordering against existing flower priorities, then adds a SPAN rule for each port binding in the block. On partial failure it rolls back already added SPAN rules. Destroy removes SPAN rules from all bindings and resets priority state.

State and persistence: Uses `block->mall` to track whether matchall is bound and the min/max priority. SPAN IDs live in each flow block binding and are managed by the SPAN subsystem. No persistent storage.

Dependencies/integration: Depends on flow block binding state, flower priority query, SPAN rule add/delete, Prestera netdev validation, and tc matchall structures.

Risks: Only singular mirred mirror-like actions are supported. Shared block behavior means destroy removes SPAN for every binding. Priority ordering differs for ingress/egress and can be surprising to users mixing flower and matchall. Rollback must align with list traversal after failures.

Test signals: `tc filter add matchall ... action mirred`, invalid action count, non-Prestera target rejection, chain/offload rejection, ingress/egress priority conflicts with flower, multi-port shared block mirroring, duplicate SPAN handling, and destroy cleanup.
