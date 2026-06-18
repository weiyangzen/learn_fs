# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/action_ste_pool.h

## Purpose
`action_ste_pool.h` declares the in-memory model and API for action STE pooling. It is the boundary between action/rule code that needs STE chunks and the implementation that owns backing STE pools, RTCs, and jump STCs.

## Important APIs, Types, And Functions
The header defines initial, step, and maximum table log sizes, plus cleanup and expiration periods. `struct mlx5hws_action_ste_table` wraps one STE pool, its jump STC, RX/TX RTC IDs, list membership, parent pool element, and `last_used` timestamp. `struct mlx5hws_action_ste_pool_element` groups available/full tables for one optimization mode and remembers the largest size allocated so far. `struct mlx5hws_action_ste_pool` contains a mutex and one element for each `mlx5hws_pool_optimize` mode. `struct mlx5hws_action_ste_chunk` is the caller-facing allocation result containing the table pointer and pool chunk.

The API exposes context-wide init/uninit and chunk alloc/free. Callers must set `chunk->ste.order` before allocation; allocation fills the table pointer and offset.

## Control Flow And State
The state is volatile kernel memory tied to an HWS context. Tables persist until explicit uninit or delayed cleanup removes stale full tables. List placement tracks whether a table can be searched for new chunks (`available`) or is exhausted (`full`). The per-pool mutex serializes allocation, free, and garbage-collection list movement.

## Dependencies And Integration Points
Definitions depend on HWS context, pool chunks, `list_head`, mutexes, delayed cleanup in `context.c`, action STC helpers, and command-level RTC creation. BWC complex/simple rule insertion can allocate action STEs through rule/action paths that depend on this contract.

## Risks And Test Signals
The header’s correctness depends on callers honoring `chunk->ste.order` and not freeing chunks after context teardown. Useful tests allocate each optimization mode (`skip_rx`, `skip_tx`, neither), exercise full/available transitions, and verify that debug dumps can safely walk table lists under the pool lock.
