# sources/cloud-native/containerd/internal/cri/nri/nri_api.go

## Purpose

This file declares the CRI-side interface required by the NRI adapter. It decouples NRI integration from the full CRI service implementation while exposing the stores and lifecycle operations NRI plugins need.

## Important APIs, Types, and Functions

`CRIImplementation` exposes configuration, sandbox/container stores, sandbox metadata store, container metadata extension key, container resource update, and stop-container operations. Its return types bind the adapter to CRI config, CRI stores, containerd sandbox metadata, CRI runtime protobuf requests, and container store status.

## Control Flow

There is no implementation control flow. The interface defines callbacks used by platform-specific `API` implementations.

## State and Persistence Behavior

The interface itself stores nothing. Implementations provide access to persistent/in-memory CRI stores and containerd metadata.

## Dependencies and Integration Points

It integrates `internal/nri` with CRI server/store packages. Linux NRI code calls these methods for discovery, updates, evictions, spec metadata, and resource update synchronization.

## Risks and Edge Cases

Adding methods increases coupling between NRI and CRI service internals. Implementations must preserve store concurrency semantics and status update invariants. Returning nil or stale stores would make plugin discovery/update behavior unreliable.

## Test Signals

Mocks of this interface should be used for NRI API unit tests, especially resource update, eviction, metadata extension lookup, and disabled-NRI behavior.
