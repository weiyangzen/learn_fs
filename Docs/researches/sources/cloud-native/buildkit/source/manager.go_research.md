# sources/cloud-native/buildkit/source/manager.go

## Purpose
Provides the registry and router for BuildKit source implementations.

## Important APIs, Types, And Functions
- `Source` interface defines `Schemes`, `Identifier`, and `Resolve`.
- `SourceInstance` interface defines `CacheKey` and `Snapshot`.
- `Manager` stores a mutex-protected scheme-to-source map.
- `NewManager`, `Register`, `Identifier`, and `Resolve` are the public operations.

## Control Flow
Backends register themselves by scheme. For an LLB `Op_Source`, `Identifier` splits `scheme://ref`, finds the backend, and delegates identifier construction with attrs and platform. Later, `Resolve` routes the concrete identifier by `id.Scheme()` to create a source instance.

## State And Persistence
In-memory map only. Register overwrites duplicate schemes with the latest source.

## Dependencies And Integration Points
Imports BuildKit cache, session, solver, protobuf ops, and pkg/errors. All source backends in this subset implement these interfaces.

## Risks And Edge Cases
Parsing requires `://`; opaque identifiers without that separator fail. The manager trusts `id.Scheme()` on resolve, so mismatched identifier objects can route unexpectedly if a custom identifier lies about its scheme.

## Test Signals
No direct tests in this subset, but every source backend depends on this contract.
