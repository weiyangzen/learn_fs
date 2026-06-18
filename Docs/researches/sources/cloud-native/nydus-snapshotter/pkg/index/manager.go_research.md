# Research: sources/cloud-native/nydus-snapshotter/pkg/index/manager.go

This file provides a cached, singleflight-backed manager for OCI index alternative detection. `NewManager` stores the insecure-registry flag, creates a 500-entry LRU, and initializes a `singleflight.Group`. `CheckIndexAlternative` coalesces concurrent checks by manifest digest, returns cached descriptors, treats cached nil as `ErrNoNydusAlternative`, builds auth from the ref, runs a detector on cache miss, caches nil on failure to avoid repeated checks, and logs failures.

`TryFetchMetadata` calls `CheckIndexAlternative`, rebuilds auth, creates a detector, and fetches/unpacks metadata to the requested path. State is the LRU cache keyed by manifest digest and the singleflight in-flight map; metadata output is handled by the detector.

Integration points include `pkg/filesystem/index_adaptor.go`, auth keychain lookup, remote registry fetches, and OCI descriptors. Risks include caching negative results indefinitely even if registry referrers/index content changes under the same digest assumption, type assertions from LRU values, singleflight keyed only by digest rather than ref plus digest, and no local nil cache invalidation. Tests cover cache-hit success and cached nil failure; live registry behavior is untested.
