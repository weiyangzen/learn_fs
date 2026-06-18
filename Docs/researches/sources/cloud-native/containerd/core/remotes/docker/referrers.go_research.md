<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/referrers.go -->
# sources/cloud-native/containerd/core/remotes/docker/referrers.go

## Purpose
Implements OCI Distribution referrers discovery for Docker fetchers, including fallback to the legacy tag schema.

## Important APIs, Types, And Functions
- `FetchReferrers(ctx, dgst, opts...)` returns descriptors that refer to a subject digest.
- `openReferrers(ctx, dgst, config)` fetches the raw referrers index from `/referrers/<digest>` or fallback `/manifests/<digest-with-colon-replaced>`.
- `remotes.FetchReferrersConfig` options filter by artifact type and allow extra query filters.

## Control Flow
`FetchReferrers` applies options, opens the referrers index, returns an empty list for not-found, enforces `MaxManifestSize`, decodes exactly one OCI index JSON object, and optionally filters returned descriptors by `ArtifactType`.

`openReferrers` first chooses hosts with `HostCapabilityReferrers`; if none exist, it falls back to resolve-capable hosts. It adds `artifactType` and additional query filters to the referrers endpoint, appends namespace for proxy hosts, and opens using the fetcher's `open`. If the real endpoint is unavailable, it tries the tag fallback where `sha256:...` becomes `sha256-...`.

## State And Persistence
No state is persisted. It streams and decodes remote index content and returns descriptors.

## Dependencies And Integration Points
Depends on Docker fetcher transport, registry host capabilities, auth scopes, OCI `Index`, and generic remotes referrers options. Integrates with content fetches because returned descriptors can be fetched by the same fetcher.

## Risks And Edge Cases
Unknown content length is capped by `MaxManifestSize`; oversized indexes return an error wrapping not-found. The endpoint may return extra trailing JSON data, which is rejected. Query filters are trusted and appended directly through URL encoding. Fallback tags are compatibility behavior and may hide registry support differences.

## Test Signals
`referrers_test.go` covers normal referrers, missing content length, oversize errors, artifact-type filtering, descriptor fetchability, and fallback tag registration.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/referrers.go -->
