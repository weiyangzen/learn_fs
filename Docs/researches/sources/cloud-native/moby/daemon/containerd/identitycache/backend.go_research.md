# sources/cloud-native/moby/daemon/containerd/identitycache/backend.go

## Purpose
Defines the persistent backend contract for image signature identity cache entries and supplies a no-op implementation for configurations without durable caching.

## Important APIs, Types, And Functions
- `Entry` stores `CachedAt`, `ExpiresAt`, and an optional `SignatureIdentity`.
- `Backend` defines `Load`, `Store`, `Walk`, `PruneExpired`, and `Close`.
- `NewNopBackend` returns `nopBackend`, whose methods are successful no-ops and always miss.

## Control Flow
Callers depend on the backend interface for cache reads, writes, iteration, pruning, and lifecycle closure. The no-op backend short-circuits all persistence paths while preserving the same call contract.

## State And Persistence
The interface represents durable storage, but `nopBackend` persists nothing. Entry expiry semantics are implemented by concrete backends and callers.

## Dependencies And Integration Points
Uses API image signature identity types. It is consumed by `image_identity.go` and implemented by `bbolt.go`.

## Risks And Edge Cases
Backends must make clear whether `Walk` includes expired entries; the bbolt implementation does until prune. Callers must handle nil signatures as cacheable values.

## Test Signals
The contract is indirectly tested by bbolt backend and image identity cache tests for persistence, nil signatures, expiry, walking, and pruning.
