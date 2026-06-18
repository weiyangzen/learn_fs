# sources/cloud-native/moby/daemon/stats_windows.go

## Purpose
`stats_windows.go` converts Windows HCS/containerd task stats into Docker API stats responses.

## Important APIs, Types, And Functions
`stats` obtains a running task, reads task stats, and maps HCS processor, memory, storage, and network counters. `getNetworkStats` returns an empty map because network stats are already included. `getSystemCPUUsage` is a no-op returning zeros.

## Control Flow
The function locks only to get the running task. If HCS stats exist, it fills CPU total/kernel/user 100ns counters, memory commit/private working set, storage normalized counters, and per-endpoint network stats.

## State And Persistence
No state is persisted; reads HCS task metrics only.

## Dependencies And Integration Points
Depends on containerd task stats, Windows HCS stats shape, daemon platform `NumProcs`, API stats response types, and error classification.

## Risks
Windows stats units differ from Unix. System CPU usage is unavailable here, so consumers must handle zero host CPU fields.

## Test Signals
Windows Docker stats integration tests are the primary signal.
