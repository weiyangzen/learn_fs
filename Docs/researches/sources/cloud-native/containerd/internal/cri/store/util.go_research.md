# sources/cloud-native/containerd/internal/cri/store/util.go

## Purpose
Defines small store-level contracts for the CRI plugin: `StatsCollector` abstracts CPU/stat sample tracking for containers and sandboxes, and `StopCh` gives container state objects a one-shot stop notification channel.

## Important APIs, Types, And Functions
`StatsCollector` exposes `AddContainer` and `RemoveContainer`. `StopCh` owns a `chan struct{}` and `sync.Once`; `NewStopCh` creates the open channel, `Stop` closes it once, and `Stopped` returns a receive-only channel.

## Control Flow
Callers allocate `StopCh`, pass `Stopped()` to waiters, and invoke `Stop()` when lifecycle state reaches stopped. The `sync.Once` guard makes repeated stop paths safe.

## State And Persistence
All state is in-memory. `StopCh` persists only process-local notification state and does not encode container status.

## Dependencies And Integration Points
Depends only on `sync`. It integrates with CRI store objects and stats collectors that need stable interfaces without importing implementation details.

## Risks
Closing is irreversible, so a `StopCh` cannot be reused for restarted objects. Consumers must treat the returned channel as notification only and not infer why the container stopped.

## Test Signals
No direct tests in this file. Correctness is exercised indirectly by CRI lifecycle/store tests that wait on stop channels or manage stats collectors.
