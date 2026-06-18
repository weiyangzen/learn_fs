# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/selq.c

Purpose: Implements mlx5e `ndo_select_queue` policy with support for regular queues, DCB traffic classes, PTP port timestamp queues, and HTB offload queues.

Important APIs: `mlx5e_selq_init()`, `cleanup()`, `prepare_params()`, `prepare_htb()`, `apply()`, `cancel()`, `is_htb_enabled()`, and `mlx5e_select_queue()`.

Control flow: A standby parameter block is prepared under `state_lock`, then atomically swapped into `active` with `rcu_replace_pointer()`; `synchronize_net()` waits for in-flight queue selection to see a consistent state. `mlx5e_select_queue()` uses RCU BH dereference, chooses regular queues through `netdev_pick_tx()`, normalizes to channel index, applies UP/TC offset, or routes PTP/HTB packets to special queues.

State and persistence: `mlx5e_selq_params` holds regular queue count, channels, TCs, special-queue flags, HTB major id, and default class. Active state is RCU-protected; standby is reused after swaps. Cleanup swaps a dummy/null-ish state and frees both allocations.

Dependencies and integration: Uses netdev queue selection, VLAN or DSCP priority extraction under DCB, PTP `mlx5e_use_ptpsq()`, HTB class-to-TXQ lookup, `state_lock`, and RCU networking synchronization. Called from netdev operations on the TX hot path.

Risks: This is datapath code; incorrect queue normalization can select PTP/HTB queues for regular traffic or wrong TC queues. DSCP trust depends on `READ_ONCE` of DCB state. Cleanup intentionally prepares/applies under lock; misuse of prepare/apply/cancel sequencing triggers warnings. Tests should cover no-special, multi-TC, PTP, HTB, HTB+PTP fallback, DSCP vs VLAN UP, profile-change null active workaround, and lockdep expectations.
