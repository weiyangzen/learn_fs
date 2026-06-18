<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/resolver.go -->
# sources/cloud-native/containerd/core/remotes/resolver.go

## Purpose
Defines the generic remote resolver, fetcher, pusher, fetch-by-digest, and referrers interfaces used by containerd remote implementations.

## Important APIs, Types, And Functions
- `Resolver` resolves references and creates namespace-bound `Fetcher` and `Pusher` instances.
- `ResolverWithOptions` extends resolver with transfer option support.
- `Fetcher`, `FetcherByDigest`, `ReferrersFetcher`, and `Pusher` define remote content operations.
- `FetcherFunc` and `PusherFunc` adapt functions to interfaces.
- `FetchByDigestConfig`, `FetchByDigestOpts`, and `WithMediaType` configure digest fetch requests.
- `FetchReferrersConfig`, `FetchReferrersOpt`, `WithReferrerArtifactTypes`, and `WithReferrerQueryFilter` configure referrers retrieval.

## Control Flow
This file is contract-only. Implementations such as Docker resolver/fetcher/pusher satisfy these interfaces. Option functions mutate small config structs used by implementation methods.

## State And Persistence
No state is stored here. Config structs are per-call.

## Dependencies And Integration Points
Depends on `content`, transfer options, digest, OCI descriptors, and `net/url`. It is imported by higher-level image pull/push code and concrete remote implementations.

## Risks And Edge Cases
`FetcherByDigest` explicitly returns incomplete descriptors, so callers must not assume annotations or exact media type unless they supplied one. Referrers query filters are implementation-dependent and may or may not be applied server-side.

## Test Signals
No direct tests in this subset; Docker fetcher/referrers tests validate concrete conformance.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/resolver.go -->
