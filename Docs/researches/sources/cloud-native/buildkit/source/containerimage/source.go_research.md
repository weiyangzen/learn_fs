# sources/cloud-native/buildkit/source/containerimage/source.go

## Purpose
This file registers and resolves container image sources for registry and OCI-layout modes, parses image attributes, and exposes metadata resolution helpers used by frontends. It also resolves attestation chains for registry images.

## Important APIs and Types
`ResolverType` distinguishes registry and OCI layout. `SourceOpt` carries snapshotter, content store, applier, cache accessor, optional image store, registry hosts, resolver type, and lease manager. `Source` stores options and two `flightcontrol.Group`s for image config and attestation chain deduplication. Key methods are `NewSource`, `Schemes`, `Identifier`, `Resolve`, `ResolveImageMetadata`, `ResolveOCILayoutMetadata`, `registryIdentifier`, `ociIdentifier`, `addAttestationBlobs`, and `parseImageRecordType`.

## Control Flow
`Resolve` type-checks the identifier by resolver type, derives platform/defaults, resolve mode, record type, ref, store, layer limit, and checksum, builds a `pull.Puller`, and returns the local `puller`. `ResolveImageMetadata` creates a registry resolver with image-store behavior, fetches config through `imageutil.Config`, falls back to local image store when allowed, and optionally resolves an attestation chain from an image index. Attestation resolution reads signature/attestation manifests and selected predicate blobs, stores blobs in the response, and sets GC labels. `ResolveOCILayoutMetadata` uses `getOCILayoutResolver` and returns config metadata only.

`registryIdentifier` and `ociIdentifier` parse frontend attributes into identifier fields, including platform clones, resolve mode, record type, positive layer limits, checksum, and OCI session/store IDs.

## State and Persistence
`Source` persists no content directly but holds backend handles and in-flight deduplication groups. Metadata resolution creates temporary leases for registry attestation/config content; those leases expire or are pruned later.

## Dependencies and Integration Points
It integrates with BuildKit source APIs, solver, cache, sessions, image resolver frontend APIs, policy-helper image referrers, containerd content/diff/images/leases, resolver pool, image utilities, and provenance capture.

## Risks
Attribute parsing ignores unknown keys. Attestation chain resolution only proceeds for image indexes; non-index images return nil chains. Digest mismatches between config and attestation root are hard errors. OCI layout metadata requires a store ID from opts or identifier.

## Test Signals
No direct tests in this subset. The source's generic solver interactions are covered by scheduler/cache tests; registry/OCI metadata and attestation paths need integration tests with content stores and sessions.
