# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/hv_vhca.c

Purpose: Implements a Hyper-V vHCA agent framework where mlx5 subagents advertise capabilities, react to host control blocks, handle invalidations asynchronously, and write agent data blocks to Hyper-V config space.

Important APIs and flow: `mlx5_hv_vhca_create()` allocates state and a single-thread workqueue; `mlx5_hv_vhca_init()` registers the Hyper-V invalidate callback and creates the control agent. Invalidations allocate work in atomic context and later dispatch to matching agents under `agents_lock`. The control agent reads block 0, computes capability bits from registered agents, rejects unsupported controls, calls agent control callbacks, and writes command acknowledgements. `mlx5_hv_vhca_agent_create()` registers a typed agent and triggers capability update; destroy removes it, calls cleanup, frees it, and updates capabilities. `mlx5_hv_vhca_agent_write()` fragments payloads into fixed config blocks with sequence and offset.

State and dependencies: `struct mlx5_hv_vhca` stores core device, workqueue, agent array, and mutex. Agents store type, callbacks, private pointer, and sequence. It depends on `hv.c` config helpers, Hyper-V invalidation, fixed block size, and agent type bit masks.

Risks and test signals: The control-agent bit mapping uses `AGENT_MASK(type)` where control type maps to zero; capability/control semantics depend on host agreement. Tests should cover duplicate/out-of-range agent types, invalidate allocation failure, create/init cleanup failures, control block with unsupported bits, write fragmentation/sequence increments, cleanup with live agents warnings, and concurrent agent create/destroy versus invalidation.
