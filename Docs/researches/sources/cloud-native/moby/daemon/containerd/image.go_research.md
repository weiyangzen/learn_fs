# sources/cloud-native/moby/daemon/containerd/image.go

## Purpose
Provides core image resolution and inspection helpers for the containerd-backed image service, including name/digest/short-ID lookup, platform-specific manifest selection, parent label retrieval, reference grouping, and truncated ID validation.

## Important APIs, Types, And Functions
- `GetImage`, `ResolveImage`, `resolveImage`, `resolveDescriptor`, and `resolveAllReferences`.
- `getBestPresentImageManifest` selects the best local platform manifest using a platform matcher.
- `getAllImagesWithRepository`, `imageFamiliarName`, and `getImageLabelByDigest`.
- `checkTruncatedID` validates 4-64 hex chars with optional `sha256:` prefix.
- `errPlatformNotFound` reports platform-specific missing-manifest errors as not found.

## Control Flow
`GetImage` resolves a containerd image, chooses a present manifest matching requested/default platform, reads OCI config into Docker image metadata, attaches parent label and manifest descriptor details, then returns the internal image object. Resolution handles digested references first, name:tag references next, and valid short IDs by regex filtering target digests. `resolveAllReferences` returns the matched reference plus all images with the same target digest and retries if image data changes mid-lookup.

## State And Persistence
Read-only against image/content stores. It interprets containerd image names, target digests, and labels but does not mutate them.

## Dependencies And Integration Points
Depends on containerd image store, distribution reference parsing, OCI descriptors, platform matchers, Moby image error types, and Docker image-spec conversion helpers. It underlies nearly every image API: inspect, history, delete, export, builder cache, and commit.

## Risks And Edge Cases
Ambiguous short IDs return not-found conflict-style errors, and named digested references must match repository names, not just digest. `resolveAllReferences` detects inconsistent data and retries only three times. Parent label conflicts across references are surfaced as conflicts. Platform selection considers only locally present manifests.

## Test Signals
No direct test in this subset, but deletion/export/history/identity tests exercise resolution paths. Dedicated coverage should assert short-ID ambiguity, named digest repository filtering, label conflicts, and platform-not-found messaging.
