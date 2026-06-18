# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/srq.h

## Purpose
`srq.h` defines mlx5 SRQ command attributes, core SRQ resource state, SRQ table state, flags, and function prototypes shared by SRQ verbs and command code.

## Important APIs, types, and functions
- `MLX5_SRQ_FLAG_ERR`, `MLX5_SRQ_FLAG_WQ_SIG`, and `MLX5_SRQ_FLAG_RNDV` mark error state, WQ signature enablement, and rendezvous/tag-matching behavior.
- `struct mlx5_srq_attr` is the command-facing SRQ description: type, flags, queue geometry, SRQN, XRCD, page offset, CQN, PD, low watermark, user index, doorbell record, PAS, umem, tag-matching fields, and UID.
- `struct mlx5_core_srq` is the tracked hardware SRQ resource. Its `common` resource header must be first, followed by SRQN, queue capacities, WQE shift, event callback, and UID.
- `struct mlx5_srq_table` stores the notifier block and xarray used for SRQ event lookup.
- Declares command helpers `mlx5_cmd_create_srq()`, `mlx5_cmd_destroy_srq()`, `mlx5_cmd_query_srq()`, `mlx5_cmd_arm_srq()`, and `mlx5_cmd_get_srq()`.
- Declares table lifecycle helpers `mlx5_init_srq_table()` and `mlx5_cleanup_srq_table()`.

## Control flow
`srq.c` fills `mlx5_srq_attr` from RDMA verbs attributes and user/kernel buffer state, then passes it to `srq_cmd.c`. `srq_cmd.c` fills hardware command contexts, publishes `mlx5_core_srq` objects in the table, and routes events back through the callback declared in the core SRQ object.

## State and persistence
The header defines the persistent in-memory representation of an SRQ resource and the device-level SRQ event table. Hardware persistence is represented by SRQN, UID, queue geometry, PAS, and command attributes.

## Dependencies and integration points
It depends on mlx5 resource-common layout, RDMA `ib_umem`, notifier blocks, xarray, and mlx5 event types. It is consumed by both verbs-level SRQ code and firmware command wrappers.

## Risks
- `struct mlx5_core_srq.common` must remain first for casts through common resource code.
- Attribute fields are reused across legacy SRQ, XRC SRQ, RMP, and XRQ command formats; callers must set only fields valid for the selected type.
- Event callbacks rely on `srqn` and table lookup state remaining valid until refcounts drain.

## Test signals
- Compile coverage catches structure and prototype drift between `srq.c` and `srq_cmd.c`.
- Event tests should confirm `mlx5_cmd_get_srq()` and notifier lookup work for created SRQs and avoid stale pointers after destroy.
- Command tests should exercise every `mlx5_srq_attr` field used by basic, XRC, RMP, XRQ, and tag-matching flows.
