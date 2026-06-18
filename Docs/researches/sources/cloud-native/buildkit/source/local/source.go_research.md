# sources/cloud-native/buildkit/source/local/source.go

## Purpose
Implements BuildKit's local source backend, synchronizing files from a client session into a cache ref and producing immutable snapshots for local contexts.

## Important APIs, Types, And Functions
- `Opt`, `NewSource`, `localSource`, `Schemes`, `Identifier`, and `Resolve` expose the source implementation.
- `localSourceHandler.CacheKey` hashes session ID and transfer filters into a session cache key.
- `Snapshot`, `snapshotWithAnySession`, and `snapshot` perform session selection and file sync.
- `newProgressHandler` reports transfer progress.
- `cacheUpdater` bridges fsutil content hashing into BuildKit contenthash cache.
- `searchSharedKey` and `cacheRefMetadata` persist and find reusable mutable refs by local shared key.

## Control Flow
`Identifier` parses attrs for session ID/name prefixing, include/exclude/follow patterns, shared key hints, differ mode, metadata-only transfer, and metadata exceptions. `CacheKey` chooses an explicit session or the next available session from the job group and hashes transfer options. `Snapshot` prefers an explicit session with a 5-second lookup and falls back to any session if unavailable or invalid. `snapshot` reuses or creates a mutable ref, mounts it, obtains contenthash context, configures `filesync.FSSendRequestOpt`, applies metadata-only exception and idmap filters, runs `filesync.FSSync`, persists contenthash context and shared-key metadata, then commits the mutable ref.

## State And Persistence
Mutable refs are reused using `local.sharedKey:<name>:<hint>:<caller.SharedKey()>[:metadata]`. Content hash state is stored with the mutable ref to support incremental file sync. On sync errors, cache policy is reset to default, contenthash context is cleared, and the mutable ref is released asynchronously.

## Dependencies And Integration Points
Depends on BuildKit cache/contenthash/session/filesync/snapshot/solver/progress, `pb` attrs, `patternmatcher`, `fsutil`, and idmap utilities. Integrates tightly with client sessions rather than remote transports.

## Risks And Edge Cases
`CacheKey` requires `jobCtx` and a session when `SessionID` is absent. Fallback from explicit session to any session may hide stale session IDs but improves robustness. Metadata-only exceptions rely on pattern matching and return false on matcher errors. Reusing mutable refs is sensitive to shared-key uniqueness and caller shared-key stability.

## Test Signals
No assigned local tests. Coverage is likely in broader BuildKit local source/file sync tests; this subset has no direct assertions for metadata-only transfer or shared-key reuse.
