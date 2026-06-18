<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/locks.go -->
# sources/cloud-native/containerd/plugins/content/local/locks.go

## Purpose
In-memory per-ref lock manager for local content ingests.

## Important APIs, Types, And Functions
lock records since time; store.tryLock and store.unlock manage the locks map.

## Control Flow
tryLock rejects an already locked ref with ErrUnavailable and duration information; unlock deletes the entry.

## State And Persistence
State is process-local and not persisted, so it coordinates writers only within one store process.

## Dependencies And Integration Points
Used by store.Writer to enforce single active writer per ref.

## Risks And Edge Cases
Does not coordinate across processes; stale locks are cleared only by unlock or process exit.

## Test Signals
locks_test.go validates duplicate lock error text.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/locks.go -->
