# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/htb.h

Purpose: declares the mlx5e HTB offload interface shared between TC setup code, queue lifecycle code, and the TX queue selector.

Important APIs/types: exposes opaque `struct mlx5e_htb`, `MLX5E_QOS_MAX_LEAF_NODES`, `mlx5e_fp_htb_enumerate`, leaf enumeration/query helpers, leaf topology mutation helpers, node modification, allocation/free, init, and cleanup.

Control flow: callers allocate an HTB object, initialize it from a `tc_htb_qopt_offload`, use command-specific helpers as TC changes arrive, enumerate leaves to open/activate QoS SQs, and clean it up on qdisc destroy.

State and persistence: the header hides all tree internals. Persistence is only the lifetime of the allocated HTB instance; callers must serialize mutations through the driver state lock as expected by the implementation.

Dependencies and integration: includes `en.h`, forward-declares `mlx5e_selq`, and uses `netlink_ext_ack` for user-visible TC errors. `qos.h` calls these APIs to implement `mlx5e_htb_setup_tc`.

Risks: the ABI is intentionally low-level; callers must pass class ids/qids from the TC command consistently and must not enumerate leaves after cleanup.

Test signals: compile coverage with `CONFIG_NET_SCHED`, HTB offload command coverage, and queue-open enumeration under channel reopen.
