# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/xsk/pool.h

Purpose: exposes the small XSK pool lookup and bind API used by mlx5e setup and BPF callbacks.

Important APIs/types/functions: `mlx5e_xsk_get_pool` safely returns a queue pool only when the XSK container, pool array, and queue index are valid. It also declares `mlx5e_build_xsk_param` and `.ndo_bpf` entry `mlx5e_xsk_setup_pool`.

Control flow and state: no ownership changes occur in the header. Lookup reads `xsk->pools[ix]` after guarding null and `ix >= params->num_channels`; allocation/refcounting lives in `pool.c`.

Dependencies and integration: includes `en.h` for `mlx5e_params`/`mlx5e_xsk`. Callers rely on the null return for "no AF_XDP pool on this queue."

Risks and test signals: callers must hold or otherwise synchronize with `state_lock` when binding/unbinding. Test invalid qid, missing `xsk->pools`, and queue reopen paths that consult the helper.
