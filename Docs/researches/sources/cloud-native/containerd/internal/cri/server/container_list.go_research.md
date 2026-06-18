# sources/cloud-native/containerd/internal/cri/server/container_list.go

## Purpose
This file implements the CRI `ListContainers` RPC and conversion from internal container store entries to CRI container summaries.

## Important APIs, Types, and Functions
Key functions are `ListContainers`, `toCRIContainer`, `normalizeContainerFilter`, and `filterCRIContainers`. It uses `containerStore`, `sandboxStore`, CRI `ContainerFilter`, and `runtime.Container` fields.

## Control Flow, State, and Persistence
`ListContainers` reads all containers from the in-memory/checkpoint-backed store, converts them, normalizes short IDs through store lookups, applies ID/sandbox/state/label filters, records a timer, and returns the list. It does not mutate container state except that `normalizeContainerFilter` rewrites the request filter object to canonical IDs.

## Dependencies and Integration Points
It integrates CRI list semantics with container store state derivation. `ImageRef` and `ImageId` both use the stored platform-specific image config digest for backward compatibility and garbage collection without doing image-store lookups.

## Risks and Test Signals
Risks include surprising mutation of filter input, short-ID ambiguity, stale image reference semantics, and label matching drift. `container_list_test.go` covers conversion, filter combinations, and truncated container/sandbox IDs.
