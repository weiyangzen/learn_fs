# sources/cloud-native/moby/daemon/containerd/image_identity.go

## Purpose
Computes and caches image identity metadata: build refs from labels, pull repositories from distribution-source labels, and signature identity from local OCI referrer/signature chains and policy verification.

## Important APIs, Types, And Functions
- `imageIdentity`, `imageIdentityFromCache`, and `imageIdentityWithCachePolicy` combine label-derived identity with cached/computed signature identity.
- `imageIdentityFromLabels`, `imageIdentityBestMatch`, `imageIdentityCacheKey`, and `parseImageIdentityCacheKey`.
- Cache functions: `imageSignatureIdentityFromCache`, `updateImageIdentityCache`, `cacheComputedSignatureIdentity`, pruning/refresh helpers, `startImageIdentityCacheRefresh`, `stopImageIdentityCacheRefresh`, and `warmImageIdentityCache`.
- Verification helpers: `computeSignatureIdentity`, `signatureIdentity`, transient error classifiers, `cloneSignatureIdentity`, and `referrersProvider`.

## Control Flow
Identity lookup reads content labels, derives build/pull identities, computes a cache key from root image digest and best platform manifest, then checks in-memory and persistent caches. On cache miss with compute enabled, singleflight coalesces verification, resolves the signature chain, invokes the configured policy verifier, maps policy identity fields to API types, caches success or deterministic failures for 48 hours, and caches transient verification failures for 15 minutes. Maintenance periodically refreshes near-expiry entries and prunes expired memory/persistent records. Load/import paths can warm the cache asynchronously for available manifests.

## State And Persistence
Uses an in-memory map protected by `cacheMu`, an optional persistent `identitycache.Backend`, a singleflight group, and a background refresh goroutine. Cache entries store cloned signature values, including nil signatures, with `CachedAt` and `ExpiresAt`.

## Dependencies And Integration Points
Depends on containerd content/image stores, labels, distribution references, BuildKit exporter labels, Moby policy helpers, signature verifier providers, OCI referrers, platforms, errgroup, and identitycache backends. It integrates with image inspect/list paths that expose identity and with load warmup.

## Risks And Edge Cases
Transient-error detection currently relies partly on string matching. Cache keys include selected platform digest and platform string, so multi-platform selection changes create separate entries. Nil signatures are cacheable and can suppress repeat work. Background refresh must be stopped cleanly to avoid goroutine leaks. Persistent walk includes expired entries until prune, intentionally enabling refresh before deletion.

## Test Signals
`image_identity_test.go` covers deep-copy isolation, expiry, zero TTL, nil signatures, persistence across restart, refresh keys, persisted refresh, transient classification, label parsing, nil identity output, and cache-only behavior.
