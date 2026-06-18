# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_dim.c

Purpose: enables and disables dynamic interrupt moderation (DIM) for mlx5e RX and TX completion queues.

Important APIs, types, and functions: `mlx5e_rx_dim_work()` and `mlx5e_tx_dim_work()` apply net-DIM-selected moderation profiles to RX RQ and TX SQ CQs. `mlx5e_dim_rx_change()` and `mlx5e_dim_tx_change()` toggle DIM on queues. Internal `mlx5e_dim_enable()` allocates and initializes `struct dim`, sets CQ period mode, and binds queue private data. `mlx5e_complete_dim_work()` calls `mlx5e_modify_cq_moderation()` and resets DIM state to `DIM_START_MEASURE`.

Control flow: enabling allocates DIM on the queue CPU node, initializes work, sets the CQ period mode in hardware, stores the dim pointer on the queue, and sets the queue DIM state bit. Disabling clears the state bit, waits for datapath quiescence with `synchronize_net()`, cancels pending work, frees DIM, and clears the pointer. Work functions obtain the current profile from net-DIM and program CQ moderation.

State and persistence: per-queue `struct dim` persists while DIM is enabled. Queue state bits advertise DIM to datapath. Hardware CQ moderation persists until changed by DIM or queue teardown.

Dependencies and integration points: depends on Linux net-DIM, mlx5 CQ moderation helpers, queue/channel structs, workqueues, and NAPI/datapath synchronization.

Risks: disable ordering must prevent datapath from scheduling work after `dim` is freed. CQ period mode programming failure aborts enable. Work assumes queue private pointer remains valid until work cancellation.

Test signals: enable/disable RX and TX DIM repeatedly, validate CQ moderation changes under traffic, inject CQ period mode failures, and teardown queues while DIM work is pending.
