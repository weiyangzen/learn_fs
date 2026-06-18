# sources/cloud-native/buildkit/source/http/source_test.go

## Purpose
Tests the HTTP source backend's digest/cache-key behavior, ETag cache reuse, filename fallback, checksum pinning, signature verification, and job-context retention through pruning.

## Important APIs, Types, And Functions
- `TestHTTPSource`, `TestHTTPDefaultName`, `TestHTTPInvalidURL`, `TestHTTPChecksum`, `TestHTTPSignatureVerification`, and `TestPruneAfterCacheKey`.
- Helpers `readFile`, `newHTTPSource`, `newCacheManager`, `simpleJobContext`, and `readSignFixture`.

## Control Flow
Tests create an in-memory HTTP test server, resolve a source, call `CacheKey`, assert request counters and expected digest strings, call `Snapshot`, mount refs, and read payload files. The prune test holds cleanup functions in `simpleJobContext`, prunes the cache, mutates server content, and verifies the original ref is still used until the job context releases it.

## State And Persistence
Each test uses a temporary BuildKit cache manager backed by native snapshotter, containerd metadata/content stores, bbolt, and metadata DB. HTTP server route state is mutated to simulate changed ETags/content. Signature tests depend on optional signing fixtures.

## Dependencies And Integration Points
Exercises BuildKit cache, snapshots, leases, source interfaces, test HTTP server, identity ETags, OCI digests, and winlayers wrappers.

## Risks And Edge Cases
Expected cache-key strings are tied to JSON serialization shape. Signature tests skip without `BUILDKIT_TEST_SIGN_FIXTURES`. The checksum test demonstrates that static checksum metadata avoids network during `CacheKey` but still requires network during `Snapshot`.

## Test Signals
Strong regression signals around conditional-request counts, digest mismatch errors, retained refs after prune, and filename `download` fallback.
