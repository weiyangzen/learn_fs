# sources/cloud-native/moby/errdefs/defs.go

## Purpose
Defines Moby's package-boundary error classification interfaces.

## Important APIs and Types
Exports marker interfaces for not found, invalid parameter, conflict, unauthorized, unavailable, forbidden, system, not modified, not implemented, unknown, cancelled, deadline exceeded, and data loss errors.

## Control Flow, State, and Persistence
There is no executable flow or stored state. The file establishes type contracts: classified errors implement exactly one marker method such as `NotFound()` or `InvalidParameter()`.

## Dependencies, Integration Points, Risks, and Test Signals
The helper wrappers in `helpers.go` implement these interfaces and containerd errdefs recognizes them. API layers use classifications to choose HTTP/gRPC status codes. Risks are semantic overlap, packages asserting marker interfaces directly without unwrapping, and errors implementing multiple markers. `helpers_test.go` validates that wrapped errors are recognized through containerd predicates and Go unwrapping.
