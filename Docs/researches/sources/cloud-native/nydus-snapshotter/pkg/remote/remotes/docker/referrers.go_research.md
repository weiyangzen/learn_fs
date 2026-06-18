# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/referrers.go

## Purpose
Implements OCI artifact referrers fetching for Docker registry fetchers, with fallback to the older tag-based referrers convention.

## Important APIs, Types, And Functions
`dockerFetcher.FetchReferrers(ctx, dgst, artifactTypes...)` implements the `remotes.ReferrersFetcher` interface.

## Control Flow
The method filters hosts with resolve or referrers capability, adds pull scope, tries `GET /referrers/<digest>` with repeated `artifactType` query params and namespace proxy query when needed, and returns an image index descriptor with size from response. If not found and the host can resolve, it falls back to `GET /manifests/<digest-with-colon-replaced>`.

## State And Persistence
No state is persisted. Returned descriptor intentionally lacks digest because the referrers endpoint does not define a digest header.

## Dependencies And Integration Points
Uses `dockerFetcher.open`, host capability filtering, `scope.go`, OCI image index media type, and the `ReferrersFetcher` interface in `remote/remotes/resolver.go`.

## Risks And Edge Cases
The code currently attempts the referrers endpoint regardless of whether `HostCapabilityReferrers` is set, as the guard is commented out. Multiple artifact types are encoded as repeated query keys. Non-404 errors stop fallback.

## Test Signals
No dedicated tests in this subset. Behavior is structurally tied to fetcher open/error handling.
