<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/containerdutil/manifest.go -->
# sources/cloud-native/stargz-snapshotter/util/containerdutil/manifest.go

## Purpose
Provides containerd/OCI manifest utilities for selecting platform-specific manifests, validating media types, and fetching manifests from remotes.

## Important APIs, Types, And Functions
- `ManifestDesc(ctx, provider, image, platform)` resolves an image/index descriptor to a manifest descriptor for a platform.
- `ValidateMediaType` inspects JSON shape and compares it to expected OCI/Docker media types.
- `FetchManifestPlatform(ctx, fetcher, desc, platform)` fetches and decodes the selected manifest.
- `unknownDocument` helps infer schema fields before strict media-type handling.

## Control Flow
Manifest selection reads descriptor content, handles image index/manifest list by iterating manifests and matching platforms, validates media types, and returns a concrete manifest descriptor. Fetching then opens the descriptor from a remote fetcher and decodes OCI manifest JSON.

## State And Persistence
No persistent state. It streams content from containerd content providers or remote fetchers.

## Dependencies And Integration Points
Used by store ref pool when resolving image manifest/config. Depends on containerd content/remotes/images helpers, platforms matching, and OCI/Docker media type constants.

## Risks And Edge Cases
Platform defaulting is caller-defined. Unknown or mismatched media types fail validation. Multi-platform images without a matching platform return errors even if other manifests exist.

## Test Signals
Expected tests include single manifest pass-through, index platform match/miss, media-type mismatch detection, Docker vs OCI schema handling, and remote fetch decode errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/containerdutil/manifest.go -->
