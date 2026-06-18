# sources/cloud-native/containerd/core/leases/lease.go

## Purpose

This file defines the core lease model, resource model, manager interface, and common lease options. Leases retain resources so garbage collection does not remove them before they are fully referenced elsewhere.

## Important APIs, Types, and Functions

`Manager` defines create, delete, list, add/delete resource, and list resources operations. `Lease` carries ID, creation time, and labels. `Resource` carries type and ID for retained content, ingests, snapshots, or other resource types. `DeleteOptions` and `SynchronousDelete` control delete cleanup behavior. `WithLabel`, `WithLabels`, and `WithExpiration` mutate lease labels.

## Control Flow

Option functions initialize label maps when needed and then set or copy entries. `WithExpiration` writes `containerd.io/gc.expire` as an RFC3339 timestamp based on `time.Now().Add(d)`. The manager interface leaves concrete CRUD behavior to implementations.

## State and Persistence Behavior

The model is in-memory here, but labels have GC semantics in metadata: expiration labels can make leases stop acting as roots after the timestamp. Resource additions are persisted by manager implementations such as metadata or proxy services.

## Dependencies and Integration Points

It integrates with metadata GC, content ingest/write lease attachment, gRPC proxy managers, and client contexts carrying lease IDs. It uses `maps.Copy` for label merging and standard time formatting.

## Risks and Edge Cases

Label values are not validated by option helpers. `WithLabels` copies all entries, including empty values. Expiration depends on local clock and RFC3339 precision. `SynchronousDelete` is a function rather than a closure factory, so callers pass it directly as a `DeleteOpt`.

## Test Signals

`lease_test.go` covers label merging for empty and non-empty maps and equivalence between `WithLabels` and repeated `WithLabel`. Further tests should cover expiration label format, nil/empty label behavior, synchronous delete propagation, and resource retention through metadata GC.
