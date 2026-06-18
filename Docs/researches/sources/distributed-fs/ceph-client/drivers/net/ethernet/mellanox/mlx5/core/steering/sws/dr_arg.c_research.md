# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_arg.c

Purpose: manages pools of header-modify argument objects for pattern/argument modify-header support.

Important APIs/functions/types: `mlx5dr_arg_mgr_create`, `mlx5dr_arg_mgr_destroy`, `mlx5dr_arg_get_obj`, `mlx5dr_arg_put_obj`, and `mlx5dr_arg_get_obj_id`; internal `dr_arg_pool` tracks one chunk-size class with a mutex and free list.

Control flow: manager creation builds pools for supported chunk sizes if the domain supports pattern arguments. A get request maps number of actions to a chunk size, obtains a free object from the matching pool, allocating a firmware modify-header-argument object range if the free list is empty, writes action data via `mlx5dr_send_postsend_args`, and returns the object. Put returns it to the pool list.

State/persistence: each `mlx5dr_arg_obj` records firmware object id, offset, and log chunk size. Pools cache unused argument slots in memory; firmware general objects persist until pool destroy frees only the first slot of each allocated range with `obj_offset == 0`.

Dependencies/integration: depends on domain capabilities for argument granularity/max allocation, command create/destroy helpers, send-post path for writing argument data, and Linux lists/mutexes.

Risks: object range destruction assumes the first slot is present in the free list at destroy; leaked/in-use args during manager destruction would leak firmware objects or skip destroy. Error normalization sometimes returns `-EAGAIN`/`-ENOMEM` rather than original command status. Pool sizing must track hardware granularity caps.

Test signals: allocation for 1/2/3/4 chunk-size classes, free-list exhaustion and refill, write failure rollback, unsupported large action count, manager create on unsupported domains, and destroy with all objects returned.
