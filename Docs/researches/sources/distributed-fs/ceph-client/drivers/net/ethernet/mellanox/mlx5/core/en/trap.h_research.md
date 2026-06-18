# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/trap.h

Purpose: declares the trap queue context and public trap-control hooks for mlx5e devlink trap support.

Important APIs and types: `struct mlx5e_trap` contains datapath fields (`mlx5e_rq`, `mlx5e_tir`, NAPI, DMA device, netdev, mkey, stats pointer) and control fields (`priv`, core device, channel state bitmap, params, RQ params). Public functions close and deactivate a trap, handle a devlink trap event, and apply configured traps on interface state changes.

Control flow: interface open or devlink action changes call into `trap.c` through this API. The trap context is opened lazily when a trap action is requested and closed when active traps are removed. Consumers use the public functions rather than manipulating the queue directly.

State and persistence: `struct mlx5e_trap` persists while `priv->en_trap` is set. It is not a normal traffic channel but shares receive queue and TIR infrastructure.

Dependencies and integration points: includes the main Ethernet private header and devlink definitions. Depends on `tir.h` transitively through `en.h` types and on RX queue structures.

Risks and test signals: the structure mixes datapath and control fields, so lifetime must be serialized by netdev lock and interface state. Test compile coverage, open/close idempotence through public hooks, and trap handling when no trap context exists.
