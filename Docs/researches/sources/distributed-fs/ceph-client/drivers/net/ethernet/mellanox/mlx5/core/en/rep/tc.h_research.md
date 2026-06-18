# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rep/tc.h

Purpose: declares representor TC offload lifecycle, flow update, encap-neighbour, setup, and receive APIs with disabled-build fallbacks.

Important APIs/functions: TC init/cleanup, netdevice event register/unregister, enable/disable, port-affinity event, `mlx5e_rep_update_flows`, encap attach/detach, `mlx5e_rep_setup_tc`, and `mlx5e_rep_tc_receive`.

Control flow: representor lifecycle calls init/register/enable and their cleanup pairs; netdev TC setup calls `mlx5e_rep_setup_tc`; RX code calls `mlx5e_rep_tc_receive` to decode offload metadata before delivering skbs.

State and persistence: no header state. Enabled implementation stores TC offload state under representor/uplink private data; disabled fallback receives packets through GRO without TC metadata processing.

Dependencies and integration: includes skb, `en_tc.h`, and `en_rep.h`; guarded by `CONFIG_MLX5_CLS_ACT`.

Risks: disabled fallback changes behavior significantly by bypassing metadata restoration, so feature-gated tests must cover both modes.

Test signals: compile both configurations, representor setup callbacks, encap API call balance, and RX fallback behavior.
