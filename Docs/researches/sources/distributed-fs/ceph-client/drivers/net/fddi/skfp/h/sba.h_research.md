# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/sba.h

## Purpose
`sba.h` declares Synchronous Bandwidth Allocation state when the optional full SBA allocator is enabled and always declares ESS runtime state used by `ess.c`.

## Important APIs, Types, And Functions
Under `SBA`, it defines `struct timer_cell`, `struct s_sba_node_vars`, `struct s_sba_sessions`, and `struct s_sba` for nodes, sessions, timers, received RAF message fields, allocator totals, and SBA state machine variables. Always-relevant `struct s_ess` stores ESS flags, timer state, pending local reply, `sync_bw`, and `alloc_trans_id`.

## Control Flow
The full SBA structs support allocator state machines outside this subset. ESS uses `struct s_ess` for timer polling, local SBA reply handoff, and matching allocation responses by transaction ID.

## State And Persistence
All state is in-memory under `struct s_smc`. SBA session/node arrays and ESS allocation values are reset with the adapter and are not persisted to disk.

## Dependencies And Integration Points
It includes `mbuf.h` and `sba_def.h`, references SMT headers and FDDI addresses, and is included by `smc.h` when `ESS` is enabled.

## Risks And Edge Cases
`SBA` is disabled in the Linux config comments, so only ESS is commonly compiled; stale full-SBA declarations can drift from unavailable implementation code. Fixed `MAX_NODES`/`MAX_SESSIONS` arrays can cap allocator scale.

## Test Signals
ESS builds without `SBA`, optional SBA builds where available, local SBA pending reply behavior, allocation response TID tracking, and session/node array initialization in full allocator configurations.
