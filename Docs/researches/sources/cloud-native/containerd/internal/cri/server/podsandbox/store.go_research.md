# sources/cloud-native/containerd/internal/cri/server/podsandbox/store.go

## Purpose

This file defines the in-memory store used by the pod sandbox controller for live `PodSandbox` objects.

## Important APIs, Types, and Functions

`Store` wraps `sync.Map`. `NewStore` allocates it. `Save` rejects nil sandboxes and stores by ID. `Get` loads and type-asserts a sandbox. `Remove` atomically deletes and returns the previous sandbox.

## Control Flow

All operations are direct map wrappers with nil/not-found handling.

## State and Persistence Behavior

State is process-local and lost on restart. Recovery repopulates it from containerd metadata.

## Dependencies and Integration Points

It stores `server/podsandbox/types.PodSandbox` values for controller start, stop, status, wait, event, and recovery flows.

## Risks and Test Signals

The store does not prevent duplicate saves or validate IDs beyond nil object checks. Controller and recovery tests indirectly validate its behavior.
