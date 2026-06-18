# sources/cloud-native/moby/daemon/cluster/executor/container/attachment.go

## Purpose
Implements a swarmkit controller for network attachment tasks associated with unmanaged containers, delegating concrete network operations to `containerAdapter`.

## Important APIs, Types, And Functions
Defines `networkAttacherController`, `newNetworkAttacherController`, and lifecycle methods `Update`, `Prepare`, `Start`, `Wait`, `Shutdown`, `Terminate`, `Remove`, and `Close`.

## Control Flow
Construction creates a container adapter. `Prepare` ensures task networks exist. `Start` calls backend attachment update through the adapter. `Wait` waits until detachment using a child context. `Remove` attempts network cleanup when the task is gone. Other lifecycle methods are no-ops.

## State And Persistence
Controller holds backend, task, adapter, and an unused `closed` channel. Persistent effects are delegated to managed network creation/removal and attachment state updates.

## Dependencies And Integration Points
Used by swarmkit agent task execution for network attachment runtime tasks. Depends on executor backends, image/volume backends for adapter construction, and swarmkit `exec.DependencyGetter`.

## Risks And Test Signals
The `closed` channel is allocated but not used here. Network cleanup can be skipped when active endpoints remain via adapter logic. Coverage is indirect through executor/network attachment tests.
