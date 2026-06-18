# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/qos.h

Purpose: declares mlx5e QoS, HTB offload, QoS SQ lifecycle, and mqprio rate-limit APIs.

Important APIs/types: `BYTES_IN_MBIT`, QoS rate/capability helpers, `mlx5e_qid_from_qos`, QoS SQ open/activate/deactivate/close/reactivate/reset functions, all-queue lifecycle functions, `mlx5e_htb_setup_tc`, and opaque `struct mlx5e_mqprio_rl` lifecycle/accessors.

Control flow: HTB and channel code use this header to allocate/open/activate QoS queues when HTB is active and to dispatch TC qdisc commands.

State and persistence: no header-owned state; implementation stores queue arrays, stats, HTB object, and firmware QoS ids.

Dependencies and integration: includes mlx5 core device type; forward-declares mlx5e structures and TC HTB offload type.

Risks: callers must hold the appropriate driver state lock for lifecycle operations and must map qids through `mlx5e_qid_from_qos` before touching netdev queues.

Test signals: compile coverage in TC/HTB enabled builds and mqprio rate-limit flows.
