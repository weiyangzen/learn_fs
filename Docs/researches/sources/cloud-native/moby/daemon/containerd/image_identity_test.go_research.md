# sources/cloud-native/moby/daemon/containerd/image_identity_test.go

## Purpose
Tests image identity cache correctness, persistence, refresh semantics, transient signature error classification, label parsing, and cache-only behavior.

## Important APIs, Types, And Functions
- Cache tests cover `updateImageIdentityCache`, `imageSignatureIdentityFromCache`, `cloneSignatureIdentity`, pruning helpers, and cache key construction.
- Persistence tests use `identitycache.NewBoltDBBackend`.
- Refresh tests use `specialimage.MultiLayer`, `fakeImageService`, and `refreshImageIdentityCache`.
- Transient classification tests cover context, net, DNS, URL-wrapped, and string-based errors.
- `newWritableContentStore` and `writeTestBlob` build local metadata/content fixtures.

## Control Flow
Tests create isolated namespaces and temporary content stores, write cache entries or content labels, call identity/cache APIs, then assert returned values, map sizes, persisted reload behavior, sorted refresh keys, and parsed build/pull identities. The refresh test stores an expired persisted entry, confirms load misses, runs refresh, and verifies a fresh persisted entry exists.

## State And Persistence
Uses temporary local content stores, bbolt metadata DBs, bbolt identity cache backends, and in-memory cache maps. It explicitly mutates source and returned signature structs to prove deep-copy isolation.

## Dependencies And Integration Points
Depends on containerd local content and metadata stores, Moby special image fixtures, identitycache backend, BuildKit exporter labels, distribution-source labels, and `gotest.tools`.

## Risks And Edge Cases
Tests do not exercise a real policy verifier success path with a signed image; many signature paths are covered through cache and refresh plumbing. String-based transient detection tests make the current heuristic behavior explicit and could need revision when typed verifier errors become available.

## Test Signals
Failures signal cache aliasing, expired-entry leakage in memory, zero-TTL writes, broken persistence, refresh selection errors, wrong transient TTL classification, bad build/pull label parsing, or unexpected cache population from cache-only lookups.
