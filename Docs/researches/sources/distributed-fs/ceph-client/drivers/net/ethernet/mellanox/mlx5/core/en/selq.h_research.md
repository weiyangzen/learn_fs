# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/selq.h

Purpose: Declares the queue selection state object, lifecycle/configuration APIs, and helper functions for mapping TX queue numbers to channel indexes.

Important APIs and types: `struct mlx5e_selq` contains RCU `active`, standby params, a pointer to `priv->state_lock`, and an `is_prepared` guard. Inline `mlx5e_txq_to_ch_ix()` and `mlx5e_txq_to_ch_ix_htb()` normalize queue indexes for regular and HTB-special layouts.

Control flow and state: Users initialize the selector, prepare either general params or HTB params while holding `state_lock`, then apply or cancel. `mlx5e_select_queue()` is exported for netdev operations.

Dependencies and integration: Depends on kernel types and forward-declares mlx5e params/netdev/sk_buff. Included by channel/profile code and netdev ops.

Risks and test signals: The inline HTB mapping has a fast path for high queue numbers (`>= num_channels << 3`) and a loop for moderate overflow; tests should include boundary values. API correctness depends on callers respecting prepare/apply sequencing under the state lock.
