# sources/distributed-fs/ceph/src/client/barrier.h

## Purpose
`barrier.h` declares the write barrier data structures used by CephFS client block synchronization.

## Important APIs, Types, and Functions
It defines `barrier_interval`, `CBlockSync_State`, forward declarations for `BarrierContext` and `C_Block_Sync`, `BlockSyncList`, `Barrier`, `BarrierList`, and `BarrierContext`. `Barrier` stores a condition variable, interval set span, write list, and intrusive hook. `BarrierContext` stores the owning `Client`, inode, mutex, `outstanding_writes`, and `active_commits`.

## Control Flow
Public `BarrierContext` methods register writes, enforce barriers, commit intervals, and complete callbacks. `Barrier` exposes internals to `BarrierContext` via friendship.

## State and Persistence Behavior
The declared state is volatile synchronization state for an inode. Interval sets summarize writes claimed by active commits.

## Dependencies and Integration Points
It integrates with `Client` and Ceph type aliases, and uses Boost ICL/intrusive containers to avoid separate allocation for list nodes.

## Risks
Intrusive containers require member hooks to remain valid for the entire list membership. The header exposes only coarse operations, so implementation correctness controls all lifecycle safety.

## Test Signals
Compile-time signals include correct hook member types; runtime signals are absence of aborts or use-after-free under concurrent write/commit completion.
