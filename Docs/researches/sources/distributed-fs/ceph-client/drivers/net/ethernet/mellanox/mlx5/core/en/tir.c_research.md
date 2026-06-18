# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tir.c

Purpose: implements a builder and lifecycle wrapper for mlx5 Transport Interface Receive objects. TIRs route received packets to direct RQs or indirect RQTs and carry RSS, packet merge/LRO, self-loopback blocking, and TLS receive settings.

Important APIs and types: private `struct mlx5e_tir_builder` stores a create/modify command buffer and a `modify` flag. Public builder functions allocate/free/clear, build inline direct-RQ dispatch, build indirect RQT dispatch, configure packet merge, RSS, direct mode, self loopback blocking, and TLS. Lifecycle functions are `mlx5e_tir_init`, `mlx5e_tir_destroy`, and `mlx5e_tir_modify`.

Control flow: callers allocate a builder for create or modify, fill the relevant TIRC context through helper functions, then create or modify a hardware TIR. Builders select the correct `create_tir_in.ctx` or `modify_tir_in.ctx` layout. Create-only helpers warn if used with a modify builder. Modify-capable helpers set the appropriate modify bitmask. `mlx5e_tir_init` creates the TIR and optionally registers it in the transport-domain TIR list under a mutex; destroy removes it if registered and destroys the hardware object.

State and persistence: the hardware TIR number persists in `struct mlx5e_tir`. Optional list registration persists until destroy. Builder state is temporary command input memory.

Dependencies and integration points: mlx5 transport object commands, Ethernet params for packet merge constants, RSS hash definitions, transport-domain hardware object list, and callers such as normal RX channels and trap queues.

Risks and test signals: incorrect create-vs-modify use, missing modify bitmasks, RSS key length mismatches, and list registration races are key risks. Test create/destroy for direct and RQT TIRs, modify RSS/packet merge/self-loopback, TLS TIR creation, trap direct-RQ TIR creation, and lockdep around registered TIR list deletion.
