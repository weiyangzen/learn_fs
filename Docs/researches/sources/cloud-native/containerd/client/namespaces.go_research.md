# Research: sources/cloud-native/containerd/client/namespaces.go

## Purpose
Adapts the gRPC namespace service client into the `namespaces.Store` interface used by containerd client and in-memory service code.

## Important APIs, Control Flow, And State
`NewNamespaceStoreFromClient` returns `remoteNamespaces`. `Create` sends labels after converting them to protobuf field values. `Labels` fetches namespace metadata and converts labels back to strings. `SetLabel` builds an update request with field paths for one label key and deletes a label when value is empty. `List` returns names from the service response. `Delete` applies namespace delete options into the request. Persistent state lives in the daemon namespace service, not this adapter.

## Dependencies And Integration
Uses `api/services/namespaces/v1`, `errgrpc`, package `namespaces`, and protobuf value helpers. It is wired by `services.go` for remote clients and by callers needing a namespace store abstraction.

## Risks And Test Signals
Risks include incorrect field paths for label updates, empty value semantics surprising callers, and gRPC error conversion gaps. Tests should cover create/list/delete, label conversion, single-label set/unset, delete options, and native error mapping.
