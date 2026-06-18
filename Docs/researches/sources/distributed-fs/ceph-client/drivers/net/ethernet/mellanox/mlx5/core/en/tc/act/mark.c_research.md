# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/mark.c

Purpose: Handles TC skbedit mark offload for NIC namespace flows.

Important API: `mlx5e_tc_act_mark` validates that marks fit `MLX5E_TC_FLOW_ID_MASK`, stores `act->mark` into `attr->nic_attr->flow_tag`, and sets FWD_DEST.

Control flow and state: No persistent state; it mutates NIC flow attribute state.

Dependencies and integration: Included in the NIC action table only. Uses `en_tc.h` for flow tag mask definitions and extack reporting.

Risks and tests: Only 16-bit marks are supported. Tests should cover max supported mark, overflow rejection, and NIC-only availability.
