<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/nsmap.go -->
# sources/cloud-native/containerd/core/runtime/nsmap.go

## Purpose
Provides a generic namespace-aware map for runtime objects keyed by object ID and namespace.

## Important APIs, Types, And Functions
- `object` constraint requires `ID() string`.
- `NSMap[T]` stores `map[namespace]map[id]T` behind an RW mutex.
- `NewNSMap` constructs the map.
- `Get`, `GetAll`, `Add`, `AddWithNamespace`, `Delete`, and `IsEmpty` expose namespace-aware operations.

## Control Flow
Most methods require a namespace from context via `namespaces.NamespaceRequired`. `AddWithNamespace` creates the inner map when needed and rejects duplicate IDs with `ErrAlreadyExists`. `GetAll(noNS=true)` returns objects across all namespaces; otherwise it returns only the context namespace.

## State And Persistence
State is in-memory only. Deleted namespaces are not removed when their inner maps become empty, but `IsEmpty` checks inner lengths.

## Dependencies And Integration Points
Used by runtime managers and shim tracking code for namespace-scoped tasks/shims. Depends on containerd namespace context helpers and `errdefs`.

## Risks And Edge Cases
`Delete` silently returns when the context lacks a namespace. `GetAll(noNS=true)` order is map iteration order and not deterministic. Empty namespace maps can remain after deletions.

## Test Signals
No direct test in this subset; runtime v2 shim/task manager tests elsewhere likely exercise it.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/nsmap.go -->
