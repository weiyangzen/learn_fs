# sources/cloud-native/containerd/internal/cri/server/podsandbox/recover.go

## Purpose

This file lets the pod sandbox controller reconstruct in-memory sandbox state from existing containerd containers and sandbox-store extensions during CRI plugin restart.

## Important APIs, Types, and Functions

`RecoverContainer` loads sandbox metadata, container creation time, updated resources extension, task status, runtime options, and network namespace. `getNetNS` loads a non-host network namespace from metadata. `hostNetwork` contains OS-specific host-network detection for Linux, Windows HostProcess, and Darwin.

## Control Flow

Recovery uses a ten-second timeout per sandbox. It loads metadata and container info, optionally reads `UpdatedResources`, inspects the task, marks missing or stopped tasks not-ready, waits on running tasks, deletes stopped tasks, saves a `PodSandbox` in the controller store, starts an exit waiter when needed, and returns a CRI sandbox store object.

## State and Persistence Behavior

It rebuilds in-memory controller and CRI sandbox stores from persisted container extensions and sandbox-store data. It does not create new containerd resources, but it can delete stopped tasks.

## Dependencies and Integration Points

It depends on containerd container/task APIs, sandbox store metadata/status, CRI config mode, runtime API resources, netns loading, and the controller store.

## Risks and Test Signals

Risks include stale metadata, races where a task disappears during status inspection, and nil metadata assumptions after extension load. Recovery tests use fake containers/tasks to cover running, stopped, missing, and metadata cases.
