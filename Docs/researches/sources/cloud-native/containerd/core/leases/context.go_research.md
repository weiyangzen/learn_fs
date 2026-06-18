# sources/cloud-native/containerd/core/leases/context.go

## Purpose

This file stores and retrieves lease IDs on contexts. It also ensures lease IDs propagate through gRPC metadata for remote calls.

## Important APIs, Types, and Functions

`WithLease(ctx, lid)` returns a context containing the lease ID under a private key and outgoing gRPC metadata. `FromContext(ctx)` returns the lease ID from the private context key or, if absent, from incoming gRPC metadata.

## Control Flow

`WithLease` wraps the context with `context.WithValue`, then calls `withGRPCLeaseHeader`. `FromContext` checks the local value first and falls back to `fromGRPCHeader`.

## State and Persistence Behavior

There is no persistence. Lease identity is request-scoped context state and optional gRPC metadata.

## Dependencies and Integration Points

It integrates with lease-aware content, snapshot, and metadata operations and with the gRPC helpers in `grpc.go`. Remote clients can set a lease once on context and have it reach server handlers.

## Risks and Edge Cases

The private value must be a string; empty strings are accepted. Incoming metadata is only consulted when the local context key is absent. Context values do not cross process boundaries unless the gRPC metadata path is used.

## Test Signals

Tests should verify local context retrieval, outgoing metadata creation, incoming metadata fallback, precedence of local value over incoming header, and behavior when no lease exists.
