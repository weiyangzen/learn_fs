# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_fw.c

Purpose: builds and tears down small firmware-owned flow tables used as helpers by SWS actions, specifically checksum-recalculation tables and multidestination forwarding tables.

Important APIs/functions: `mlx5dr_fw_create_recalc_cs_ft`, `mlx5dr_fw_destroy_recalc_cs_ft`, `mlx5dr_fw_create_md_tbl`, and `mlx5dr_fw_destroy_md_tbl`.

Control flow: checksum-recalc creation allocates a terminal FDB flow table near max level, creates an empty group, allocates a modify-header action that adds zero to IPv4 TTL to trigger checksum recalculation, inserts an FTE forwarding to a vport, and returns IDs plus RX ICM address. Multidest creation allocates an FDB table at an allowed multipath level, creates a group, programs an FTE forwarding to the supplied destination array, and returns table/group IDs. Destroy paths delete the FTE, group, table, and modify-header resources in reverse order.

State/persistence: returned structs/IDs represent firmware flow tables, groups, entries, and modify-header contexts. The domain caches checksum tables in `dr_domain.c`; multidest actions retain their table/group IDs until action destroy.

Dependencies/integration: depends on `dr_cmd.c` command wrappers, domain capabilities, action multidestination construction, and TTL workaround logic from `dr_action.c`.

Risks: helper tables consume firmware flow-table levels and resources; failures must unwind all created objects. Destroy helpers assume IDs were fully initialized. The TTL workaround is specific to FDB RX checksum recalculation behavior and must stay aligned with action selection logic.

Test signals: create/destroy checksum table per vport, injected failures after table/group/modify-header/FTE creation, multidest with and without reformat, ignore-flow-level propagation, and action destroy releasing multidest tables.
