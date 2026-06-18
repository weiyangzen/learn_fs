# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_action.c

Purpose: implements SWS direct-rule action construction, validation, conversion to STE action attributes, firmware helper destinations, packet reformat/modify-header actions, VLAN/ASO/range actions, and action destruction.

Important APIs/functions: `mlx5dr_actions_build_ste_arr`, `mlx5dr_action_create_drop`, `mlx5dr_action_create_dest_table`, `mlx5dr_action_create_dest_flow_fw_table`, `mlx5dr_action_create_dest_match_range`, `mlx5dr_action_create_mult_dest_tbl`, `mlx5dr_action_create_flow_counter`, `mlx5dr_action_create_tag`, `mlx5dr_action_create_flow_sampler`, `mlx5dr_action_create_packet_reformat`, `mlx5dr_action_create_pop_vlan`, `mlx5dr_action_create_push_vlan`, `mlx5dr_action_create_modify_header`, `mlx5dr_action_create_dest_vport`, `mlx5dr_action_create_aso`, `mlx5dr_action_get_pkt_reformat_id`, and `mlx5dr_action_destroy`.

Control flow: action arrays are validated against a domain/nic-direction state machine (`next_action_state`) that enforces legal ordering and terminal/nonterminal constraints. `mlx5dr_actions_build_ste_arr()` scans the action list, fills `mlx5dr_ste_actions_attr`, resolves destination ICM addresses, applies capability workarounds such as TTL checksum recalculation, and calls RX/TX STE action builders. Constructors allocate the typed action payload after `struct mlx5dr_action`, obtain firmware objects or DR resources as needed, and increment domain/table/action refcounts.

State/persistence: actions are refcounted kernel objects. Some own firmware packet reformat IDs, modify-header ICM allocations, match definers, multidestination firmware tables, or references to tables/domains/vports. Modify-header conversion stores HW action lists and may use single-action optimization or pattern/argument resources.

Dependencies/integration: depends on `dr_types.h`, `dr_ste.h`, command wrappers, domain vport/csum helpers, definer manager, argument/pattern managers, ICM pools, firmware helper table creation, and mlx5 capabilities. Rule creation consumes these actions to build STE arrays.

Risks: the state machine is dense and domain-specific; missing an action transition can accept invalid hardware programming or reject valid flows. Resource ownership is split by action type, making destroy-path parity critical. TTL modification uses hardware workaround logic that depends on destination type and vport helper tables. Modify-header conversion must respect field limitations, L3/L4 incompatibilities, and paired-action hazards.

Test signals: legal/illegal action order matrices for NIC RX/TX and FDB RX/TX, action destructor leak checks, modify-header SET/ADD/COPY conversion including TTL-last behavior, reformat parameter validation, multidestination with vport reformat, range hit/miss tables, and capability-disabled VLAN/encap/pop/push paths.
