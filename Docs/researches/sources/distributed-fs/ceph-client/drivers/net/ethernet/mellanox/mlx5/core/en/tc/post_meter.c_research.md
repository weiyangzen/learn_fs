# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/post_meter.c

Purpose: Creates post-meter steering tables that branch on meter color or MTU result and forward to conform/exceed flow attributes with shared counters.

Important APIs: `mlx5e_post_meter_init()`, `cleanup()`, and getters for rate FT and MTU true/false FTs.

Control flow: Rate mode creates one unmanaged table, a flow group matching packet color register C5, and two rules for red and green colors. MTU mode creates separate green/red tables with miss groups and zero-spec rules. `mlx5e_post_meter_add_rule()` attaches action/drop counters according to branch action, sets no-in-port and match levels, offloads through eswitch, and clears COUNT from attr afterward to avoid freeing counters it does not own.

State and persistence: `mlx5e_post_meter_priv` stores type and either a rate table with green/red rules/attrs or MTU tables with separate FTs/groups/rules/attrs. Hardware flow tables, groups, and rules persist until cleanup.

Dependencies and integration: Uses packet color register mapping, eswitch rule offload, flow table namespace lookup, flow counters from meter handles, post-action/meter branching attrs, and FDB slow-path priorities.

Risks and tests: Cleanup assumes initialization fully succeeded for the selected type. Error paths must destroy already-created tables/groups/rules. Counter ownership is intentionally borrowed. Tests should cover rate red/green branch action selection, MTU true/false tables, missing namespace, rule creation failure at each step, cleanup ordering, and COUNT flag clearing.
