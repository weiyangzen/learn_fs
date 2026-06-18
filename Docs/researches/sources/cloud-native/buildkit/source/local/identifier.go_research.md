# sources/cloud-native/buildkit/source/local/identifier.go

## Purpose
Defines the identifier for local/session-provided source trees and provenance capture for local sources.

## Important APIs, Types, And Functions
- `LocalIdentifier` stores name, session ID, include/exclude/follow patterns, shared key hint, differ mode, metadata-only transfer flag, and metadata exceptions.
- `NewLocalIdentifier` creates a name-only identifier.
- `Scheme` returns `local`.
- `Capture` records a provenance local source by name.

## Control Flow
`localSource.Identifier` populates this struct from source attrs. The handler uses it to generate cache keys and configure file sync.

## State And Persistence
No persistence in this file. The struct controls cache-key and sync behavior in `source.go`.

## Dependencies And Integration Points
Uses provenance types, source interface, source type constants, and `fsutil.DiffType`.

## Risks And Edge Cases
Local provenance captures only the logical source name, not include/exclude patterns or session identity. More detailed state is encoded in cache keys by the handler.

## Test Signals
No direct tests in this subset; behavior is exercised through local source integration tests elsewhere.
