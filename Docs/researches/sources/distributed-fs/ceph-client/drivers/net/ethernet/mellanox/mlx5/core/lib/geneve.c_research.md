# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/geneve.c

Purpose: Manages one firmware Geneve TLV option object for mlx5 offload users, with reference counting for repeated requests for the same option class/type.

Important APIs and flow: `mlx5_geneve_create()` allocates state and initializes a mutex. `mlx5_geneve_tlv_option_add()` validates the object manager, then either increments the refcount for matching class/type or creates a firmware `GENEVE_TLV_OPT` general object and records class/type/object ID. A different class/type while an object exists is rejected with `-EOPNOTSUPP`. `mlx5_geneve_tlv_option_del()` decrements refcount and destroys the firmware object on the final user. `mlx5_geneve_destroy()` frees any still-live object during unload.

State and dependencies: `struct mlx5_geneve` stores core device, option class/type, object ID, mutex, and refcount. It depends on Geneve option layout, mlx5 general object caps, and mlx5 command execution.

Risks and test signals: Only one TLV option object is supported at a time, and `del()` assumes a prior add because it pre-decrements refcount. Tests should cover unsupported caps, duplicate matching add/del, conflicting option add, destroy with nonzero refcount, and command failure logging.
