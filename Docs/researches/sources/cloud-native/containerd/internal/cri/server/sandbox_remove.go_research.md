# sources/cloud-native/containerd/internal/cri/server/sandbox_remove.go

## Purpose

This file implements CRI `RemovePodSandbox`, force-stopping a sandbox, removing contained containers, deleting sandbox controller state, notifying NRI, and releasing indexes.

## Important APIs, Types, and Functions

`RemovePodSandbox` resolves the sandbox, calls `stopPodSandbox`, deletes the lease, checks netns closure, removes all containers in the sandbox, calls `sandboxService.ShutdownSandbox`, sends a deleted event, invokes `nri.RemovePodSandbox`, deletes in-memory and containerd sandbox-store metadata, releases the sandbox name, and updates metrics.

## Control Flow

Missing sandboxes are successful no-ops. Removal blocks NRI plugin sync during critical operations. It force-stops before removing containers and refuses to continue if a non-host netns is still open.

## State and Persistence Behavior

It deletes leases, network state through stop logic, containers, sandbox controller resources, CRI stores, containerd sandbox-store records, and name reservations.

## Dependencies and Integration Points

It integrates with leases, sandbox service, container removal, NRI, event generation, tracing, and metrics.

## Risks and Test Signals

Risks include container creation races after the stop point, netns closure failures, and partial metadata cleanup. End-to-end CRI remove tests and restart recovery are key signals.
