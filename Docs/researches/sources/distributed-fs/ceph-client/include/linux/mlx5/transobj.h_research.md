# sources/distributed-fs/ceph-client/include/linux/mlx5/transobj.h

## Purpose
This header declares mlx5 transport object management APIs. It covers allocation of transport domains, creation/query/modification/destruction of receive queues, send queues, TIRs, TISs, RQTs, and hairpin queue pairs.

## Important APIs, Types, And Data
- `mlx5_core_alloc_transport_domain()` and `mlx5_core_dealloc_transport_domain()` manage transport domain numbers.
- RQ APIs: `mlx5_core_create_rq()`, `mlx5_core_modify_rq()`, `mlx5_core_destroy_rq()`, `mlx5_core_query_rq()`.
- SQ APIs: `mlx5_core_create_sq()`, `mlx5_core_modify_sq()`, `mlx5_core_destroy_sq()`, `mlx5_core_query_sq()`, `mlx5_core_query_sq_state()`.
- TIR/TIS APIs create, modify where supported, and destroy transport interface receive/send objects.
- RQT APIs create, modify, and destroy receive queue tables.
- `struct mlx5_hairpin_params` captures log data size, log packet count, queue counter, and channel count.
- `struct mlx5_hairpin` stores function and peer mlx5 devices, channel count, RQN/SQN arrays, and a `peer_gone` flag.
- Hairpin APIs create, destroy, and clear dead peer state.

## Control Flow
Networking code allocates transport domains, creates queues and indirection objects, wires RQTs into TIRs or TIS/SQ paths, modifies objects as configuration changes, queries state for validation/debug, and destroys objects in reverse order. Hairpin creation builds paired SQ/RQ objects across a function device and peer device for direct packet redirection; peer-death handling marks or clears state to prevent unsafe access.

## State And Persistence
Firmware owns object state identified by RQN, SQN, TIRN, TISN, RQTN, and TDN values. The hairpin structure persists driver-side arrays of queue numbers and peer identity until destroyed. No state is stored in this header.

## Dependencies And Integration Points
It includes `linux/mlx5/driver.h` and integrates with mlx5e channels, representors, eswitch/offload flows, RSS/RQT setup, queue counters, and multi-device hairpin forwarding. Command buffers are raw `u32 *in/out`, so callers depend on mlx5 IFC layout headers for object contexts.

## Risks
Object lifecycle ordering matters: destroying an object still referenced by a TIR/TIS/RQT or flow table can break traffic. Raw command buffers increase the risk of malformed input lengths or missing required fields. Hairpin creation spans two devices, so peer teardown races and partial creation failures must be handled carefully. `peer_gone` state must be honored by destroy/cleanup code.

## Test Signals
Runtime tests should cover create/query/modify/destroy for RQ, SQ, TIR, TIS, and RQT objects, SQ state queries, transport domain leak checks, RSS table updates, hairpin traffic forwarding, peer removal during active hairpin use, and rollback from injected command failures.
