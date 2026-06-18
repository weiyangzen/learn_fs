# sources/cloud-native/buildkit/source/http/source.go

## Purpose
Implements the HTTP/HTTPS source backend: resolves remote or session-provided artifacts to digest metadata, caches downloaded bodies as immutable refs, reuses ETag-indexed refs, verifies optional signatures, computes optional metadata checksums, and materializes snapshots as single-file roots.

## Important APIs, Types, And Functions
- `Opt`, `Source`, `NewSource`, `Schemes`, `Identifier`, `Resolve`, and `ResolveMetadata` expose the BuildKit source boundary.
- `Metadata`, `MetadataOpts`, `MetadataChecksumRequest`, and `MetadataChecksumResponse` are metadata API objects.
- `httpSourceHandler` holds source identifier, cached resolution, cache accessor, transport, and session manager.
- `resolveMetadata`, `resolveMetadataStatic`, `resolveMetadataRef`, `CacheKey`, `Snapshot`, `save`, `newHTTPRequest`, `getFileName`, `verifySignature`, and `computeChecksumResponse` are the core operations.
- `cacheRefMetadata` stores `http.checksum`, `etag`, and `http.modtime` on cache refs.

## Control Flow
Identifier parsing applies digest, filename, permissions, ownership, auth, signature, and supported header attrs. Metadata resolution short-circuits when a checksum is pinned; otherwise it computes a URL/options hash, tries resolver cache, searches cache metadata, performs conditional HEAD/GET with known ETags, saves new responses when needed, validates pinned checksums, and records `resolved.refID`. `CacheKey` formats filename, digest, mtime, ownership, auth, and headers into a stable JSON digest. `Snapshot` returns the resolved ref when available, falls back to resolver-cache ref lookup, or performs a new GET/save and checks digest consistency.

## State And Persistence
Downloaded content is persisted in immutable refs with a single sanitized filename. ETags and Last-Modified values are stored as metadata, with ETag search indexed by a digest of URL and relevant source options. Job cleanup retains refs across cache-key/snapshot flow until the job releases them. File mtimes are set from Last-Modified or Unix zero, and UID/GID are mapped through idmapped mounts.

## Dependencies And Integration Points
Uses BuildKit cache/snapshot/session/secrets/solver APIs, source attrs from `pb`, tracing default transport, `pathutil.SafeFileName`, `cachedigest`, PGP verification, and version user agent. `transport.go` adds a special `buildkit-session` host for session uploads.

## Risks And Edge Cases
Only `Accept` and `User-Agent` user headers survive. Auth secret lookup through `hs.sm.Any` assumes a session manager is available; implicit host-based secrets are ignored on missing secret unless an explicit auth secret was requested. Some servers mishandle conditional requests, so the code uses HEAD first and falls back to GET. `etagValue` only strips weak prefixes and does not parse comma lists. Signature/checksum requests force a real cached ref even when static checksum metadata exists.

## Test Signals
`source_test.go` covers ETag reuse, default filename fallback, invalid HTTP status, pinned checksum mismatch and success, PGP detached signature verification, and cache retention after `CacheKey` while a job cleanup holds the ref.
