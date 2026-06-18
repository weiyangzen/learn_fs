# sources/cloud-native/containerd/internal/nri/domain.go

## Purpose
Defines the namespace-specific domain abstraction that lets the generic NRI adapter list, update, and evict containers across containerd namespaces.

## Important APIs, Types, And Functions
`Domain` includes listing/getting pods and containers plus update/evict operations. `RegisterDomain` adds a domain to global `domains`. `domainTable` manages registered domains and applies NRI updates/evictions.

## Control Flow
Registration enforces unique namespace names. Listing aggregates all domains. Update/evict resolves a container ID to a domain, wraps the context with that namespace, invokes domain methods, logs failures, and returns failed requests.

## State And Persistence
Global in-memory domain registry protected by a mutex. No persistent data.

## Dependencies And Integration Points
Uses containerd namespaces, errdefs, logging, and NRI adaptation update/eviction types.

## Risks
Container IDs are searched across domains with a TODO noting possible namespace conflicts. `RegisterDomain` logs fatal on duplicate registration. Registry iteration order is map order.

## Test Signals
No direct tests in this subset; NRI synchronization and update flows exercise it indirectly.
