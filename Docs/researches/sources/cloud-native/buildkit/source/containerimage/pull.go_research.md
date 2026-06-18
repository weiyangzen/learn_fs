# sources/cloud-native/buildkit/source/containerimage/pull.go

## Purpose
This file implements image source cache-key and snapshot behavior. It resolves manifests, computes stable manifest/config cache keys, wires descriptor handlers for lazy layer fetch/progress, applies layer limits/checksums, and materializes image layers into cache refs.

## Important APIs and Types
`puller` embeds `*pull.Puller` and holds cache, lease, resolver, image store, record type, session, layer limit, checksum, manifest state, descriptor handlers, and `flightcontrol.Group` state. `mainManifestKey` hashes manifest digest plus platform and layer limit. `CacheKey` resolves/pulls metadata and returns either manifest or config cache keys. `Snapshot` materializes layers. `cacheKeyFromConfig` prefers OCI chain ID when possible.

## Control Flow
`CacheKey` chooses a registry or OCI-layout resolver, then runs resolution once through `p.g.Do`. It creates a temporary lease, emits resolve progress, calls `PullManifests`, checks expected checksum, enforces layer limit, creates descriptor handlers with inherited labels and estargz snapshot labels, computes the manifest key, reads config, computes config key, and marks cache-key work done. It returns the manifest key for index 0; later indexes can return the config key and set `cacheDone`.

`Snapshot` reconstructs the resolver, returns nil for empty layer sets, releases temporary leases on exit, walks layer descriptors through `CacheAccessor.GetByBlob`, releases parents, marks Windows layers when needed, ensures non-layer blobs still exist or re-pulls manifests, attaches non-layer content to the final ref lease, sets record type, and returns the final immutable ref.

## State and Persistence
Persistent artifacts include pulled content in the content store, cache snapshots for layer chains, and lease resource links. Temporary leases are held between cache-key and snapshot phases and released after snapshot.

## Dependencies and Integration Points
It depends on containerd content/images/leases/remotes/snapshots, BuildKit cache, sessions, source resolver options, progress controller, pull utilities, resolver pool, estargz labels, and OCI image identity.

## Risks
State spans `CacheKey` and `Snapshot`; callers must run them in the expected solver lifecycle. Layer limits can change both manifest and config keys. Manifest/config blobs can be garbage-collected between phases, so `Snapshot` has a re-pull path. Cache load failures fall back to execution in scheduler tests, but source-specific IO errors still fail the solve.

## Test Signals
`scheduler_test.go` exercises generic cache-key/load fallback behavior, not image-specific pulling. Image pull behavior should be covered by container image integration tests elsewhere.
