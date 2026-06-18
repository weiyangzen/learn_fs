# sources/cloud-native/containerd/core/leases/grpc.go

## Purpose

This file defines the gRPC metadata header used to propagate containerd lease IDs and helper functions to write and read that header.

## Important APIs, Types, and Functions

`GRPCHeader` is the header key `containerd-lease`. `withGRPCLeaseHeader` adds the lease ID to outgoing metadata, merging with existing outgoing metadata and putting the latest value first. `fromGRPCHeader` reads the first lease value from incoming metadata.

## Control Flow

Writing creates a single-pair metadata set. If outgoing metadata already exists, it joins the new pair before the old metadata. Reading checks for incoming metadata, then the header key, then returns the first value.

## State and Persistence Behavior

The helpers only mutate context metadata values. No lease object is created or persisted here.

## Dependencies and Integration Points

It depends on `google.golang.org/grpc/metadata` and is called by `WithLease`/`FromContext`. Server-side lease-aware code can retrieve lease identity from incoming RPC contexts.

## Risks and Edge Cases

Multiple lease headers can exist; the first value wins. Header values are not validated. Outgoing metadata is separate from incoming metadata, so a client context with outgoing lease headers will not be visible to `fromGRPCHeader` until transported by gRPC.

## Test Signals

Useful tests cover metadata merge ordering, no-header false returns, multiple header values selecting the first, and round-trip propagation through a gRPC call context.
