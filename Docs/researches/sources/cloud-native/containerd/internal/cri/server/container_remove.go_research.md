# sources/cloud-native/containerd/internal/cri/server/container_remove.go

## Purpose
This file implements CRI `RemoveContainer`, including idempotent not-found handling, forced stop of running/unknown containers, NRI notification, containerd deletion, checkpoint/root cleanup, store removal, name release, and delete event generation.

## Important APIs, Types, and Functions
Key functions are `RemoveContainer`, `setContainerRemoving`, and `resetContainerRemoving`. It uses `containerStore`, `containerNameIndex`, containerd `Container.Delete(WithSnapshotCleanup)`, `ensureRemoveAll`, NRI hooks, and tracing/timers.

## Control Flow, State, and Persistence
Removal first resolves store metadata and containerd info. If containerd metadata is missing, the CRI store entry and name index are cleaned. Running or unknown containers are force-stopped with timeout 0. `setContainerRemoving` prevents concurrent start/remove. On success the containerd container, checkpoint, root dir, volatile root dir, store entry, and name reservation are removed; on failure `Removing` is reset.

## Dependencies and Integration Points
It integrates with stop logic, NRI plugin synchronization, container checkpoint persistence, snapshot cleanup, lifecycle events, and metrics.

## Risks and Test Signals
Risks include races with start, leaked root directories, name-index leaks, non-idempotent not-found behavior, and NRI failures masking removal. `container_remove_test.go` covers the `Removing` guard state; full deletion behavior needs integration tests.
