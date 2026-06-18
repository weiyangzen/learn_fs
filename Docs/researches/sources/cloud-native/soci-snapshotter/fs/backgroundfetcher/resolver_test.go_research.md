# sources/cloud-native/soci-snapshotter/fs/backgroundfetcher/resolver_test.go

Purpose: validates that `NewSequentialResolver` fetches spans in increasing order until all spans in a ztoc have been resolved.

Important APIs and flow: `TestSequentialResolver` builds a gzip ztoc reader for a large random tar file, creates a `spanmanager.SpanManager` with memory cache, constructs a sequential resolver, repeatedly records `nextSpanFetchID`, calls `Resolve`, and stops when `more` is false. It checks that the final span ID equals `ztoc.MaxSpanID + 1` and that every recorded span index matches its position.

State and persistence: entirely test-local memory cache and generated ztoc reader. It directly type-asserts to `*sequentialLayerResolver` to inspect internal state.

Dependencies and integration: uses the same span manager and ztoc helpers as production, so it validates the resolver against real span boundaries. It depends on package-private access by being in the same package.

Risks and test signals: strong signal for normal sequential progression. It does not test `Close`, `Closed`, `ErrExceedMaxSpan` metric behavior, or unexpected `FetchSingleSpan` failures.
