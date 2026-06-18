# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_arfs.c

Purpose: implements accelerated Receive Flow Steering for mlx5e by translating kernel RPS flow-steering requests into mlx5 flow-table rules targeting direct TIRs for specific RX queues.

Important APIs, types, and functions: public entry points are `mlx5e_arfs_create_tables()`, `mlx5e_arfs_destroy_tables()`, `mlx5e_arfs_enable()`, `mlx5e_arfs_disable()`, and `mlx5e_rx_flow_steer()`. `struct mlx5e_arfs_tables` owns four protocol tables, a spinlock, workqueue, state bit, and filter-id counter. `struct arfs_rule` stores the flow tuple, target RX queue, filter id, flow id, async work item, and hardware rule pointer.

Control flow: table creation allocates IPv4/IPv6 TCP/UDP flow tables with two groups: a large exact-match group and a default group forwarding to RSS TIRs. Enabling redirects TTC traffic types to aRFS tables and sets the enabled bit. `ndo_rx_flow_steer` dissects SKB flow keys, rejects unsupported protocols or encapsulation, finds/allocates a hashed rule under spinlock, updates queue accounting, and queues work. Work creates a flow rule or modifies an existing rule destination to the new direct TIR, then opportunistically expires old flows via `rps_may_expire_flow()`.

State and persistence: rules persist in hash buckets until explicit disable/destroy or RPS expiry. Hardware flow rules persist in mlx5 flow tables. `last_filter_id` wraps modulo `RPS_NO_FILTER`. The enabled bit gates work execution and new steering requests.

Dependencies and integration points: depends on Linux flow dissector/RPS, mlx5 flow steering, TTC table redirection, RX resource direct/RSS TIRs, workqueues, and per-channel RQ stats.

Risks: work is asynchronous, so rule targets can change before hardware creation. Disable must cancel all pending work and delete rules safely. Filter-id wrap can collide after many flows but follows RPS expectations. Table defaults cannot use TTC default dest at creation because TTC is not ready, so RSS TIR lookup is duplicated.

Test signals: ntuple on/off creation, enable/disable, IPv4/IPv6 TCP/UDP steering, unsupported encapsulated SKBs, queue migration modifying existing rule, expiry counters, destroy while work pending, and switchdev transition with `fs->arfs` already NULL.
