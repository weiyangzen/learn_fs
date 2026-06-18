# Research: sources/cloud-native/nydus-snapshotter/pkg/referrer/manager.go

This file provides a cached manager for OCI referrers-based Nydus metadata discovery. `NewManager` stores the insecure-registry flag, creates a 500-entry LRU cache, and initializes singleflight. `CheckReferrer` coalesces checks by manifest digest, returns a cached descriptor when present, creates an auth keychain, calls a `referrer` to fetch and parse referrers, caches the returned metadata layer descriptor, and logs failures.

`TryFetchMetadata` checks for a metadata descriptor, rebuilds auth, creates a referrer, and fetches/unpacks metadata to the requested path. State is the LRU descriptor cache and singleflight in-flight state. Unlike the index manager, failed checks are not cached as negative results.

Integration points include filesystem referrer adaptor, auth, remote registry APIs, OCI descriptors, and metadata unpacking. Risks include cache invalidation when referrers change, type assertions on cached values, singleflight keyed only by digest, repeated remote failures because negatives are not cached, and no direct tests in this subset.
