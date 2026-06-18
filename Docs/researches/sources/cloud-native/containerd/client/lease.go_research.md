# Research: sources/cloud-native/containerd/client/lease.go

## Purpose
Provides a convenience helper for attaching a containerd lease to a context so content and snapshot mutations are protected from garbage collection during multi-step client operations.

## Important APIs, Control Flow, And State
`Client.WithLease` checks whether the context already carries a lease and returns a no-op cleanup if so. Otherwise it creates a lease through `LeasesService`, using a random ID and 24-hour expiration by default when no options are supplied, stores the lease ID in the returned context, and returns a cleanup function that deletes the lease. Persistent state is the lease record in the lease manager; callers own invoking cleanup.

## Dependencies And Integration
Depends on `core/leases`, `context`, and `time`. It is used by import, pull, checkpoint, and other content-producing flows to bridge several service calls safely.

## Risks And Test Signals
Risks include leaked leases if callers ignore the cleanup function, premature GC if a caller uses the original context, and custom options that omit useful expiration. Tests should cover existing lease passthrough, default lease creation, custom options, deletion errors, and behavior when lease creation fails.
