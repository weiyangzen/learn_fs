<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/referrers_test.go -->
# sources/cloud-native/containerd/core/remotes/docker/referrers_test.go

## Purpose
Tests fetching and filtering OCI referrers through the Docker resolver/fetcher stack.

## Important APIs, Types, And Functions
- `TestFetchReferrers` has subtests for basic behavior, missing length, and oversized index content.
- `runReferrersTest` builds a manifest subject and an OCI index of two referrer manifests.
- `testIndex` creates and registers OCI index descriptors.

## Control Flow
The test server registers subject manifest routes, `/referrers/<digest>`, fallback manifest tag routes, and blob/manifest routes for the referrer descriptors. It resolves an image by digest, obtains the fetcher, casts it to `remotes.ReferrersFetcher`, fetches referrers, fetches each returned descriptor, then repeats with an artifact-type filter.

## State And Persistence
Uses only test-server routes and in-memory payloads. No content store is written.

## Dependencies And Integration Points
Exercises `NewResolver`, `Resolve`, `Fetcher`, `FetchReferrers`, `Fetch`, artifact-type options, `MaxManifestSize`, and OCI descriptor/index encoding.

## Risks And Edge Cases
The missing-length case validates the size fallback to `MaxManifestSize`; the too-long case verifies bounded reads and not-found classification. Query-filter options are not deeply asserted beyond artifact type.

## Test Signals
Good integration coverage for both the referrers endpoint and fallback schema, including ability to fetch returned referrer manifests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/referrers_test.go -->
