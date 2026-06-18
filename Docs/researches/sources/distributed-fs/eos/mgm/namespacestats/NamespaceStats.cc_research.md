# sources/distributed-fs/eos/mgm/namespacestats/NamespaceStats.cc

## Purpose
`NamespaceStats.cc` implements the MGM namespace statistics adapter. It satisfies the namespace layer's `INamespaceStats` interface by forwarding namespace operation counters and execution-time samples into the global MGM statistics object.

## Important APIs, Types, And Functions
The file implements `NamespaceStats::Add(const char* tag, uid_t uid, gid_t gid, unsigned long val)` and `NamespaceStats::AddExec(const char* tag, float exectime)`. Both methods call through `gOFS->MgmStats`.

## Control Flow
The control flow is intentionally direct: namespace code calls `INamespaceStats::Add()` or `AddExec()`, this adapter dereferences global `gOFS`, then forwards to `MgmStats.Add()` or `MgmStats.AddExec()`. Comments state that no additional locking is needed because `MgmStats` methods lock internally.

## State And Persistence Behavior
The adapter owns no state and persists nothing. Counter and timing state lives in `eos::mgm::Stat` through `gOFS->MgmStats`, which is owned by the MGM OFS singleton.

## Dependencies And Integration Points
It depends on `NamespaceStats.hh`, `mgm/ofs/XrdMgmOfs.hh` for the global `gOFS`, and `mgm/stat/Stat.hh` for the concrete statistics sink. `XrdMgmOfs` embeds `mNamespaceStats`, making this adapter the bridge from namespace services back into MGM monitoring/stat reporting.

## Risks And Edge Cases
The code assumes `gOFS` is initialized and `MgmStats` is alive whenever namespace stats are emitted. Calls during early boot, failed boot, or late shutdown would be sensitive to singleton lifetime. The adapter trusts `tag` and does no null validation before forwarding.

## Test Signals
Tests should verify namespace events increment the expected MGM stat tags and execution samples. Shutdown and boot-order tests should cover that namespace code does not emit through this adapter before `gOFS` is valid or after statistics teardown.
