# sources/cloud-native/soci-snapshotter/fs/span-manager/span_manager.go

Purpose: provides lazy range access to a compressed layer by dividing it into zTOC spans, verifying compressed bytes, caching compressed or uncompressed span data, and returning assembled readers for requested uncompressed byte ranges.

Important APIs and flow: `New` derives `Zinfo`, validates zTOC max span ID and digest count, verifies the compressed header, initializes all `span` objects, and registers a finalizer. `FetchSingleSpan` is the background-prefetch path: if a span is `unrequested`, it fetches and caches compressed bytes and marks it `fetched`. `ResolveSpan` forces an uncompressed cache entry. `GetContents` maps uncompressed offsets to spans, fetches each span concurrently with `errgroup`, and returns a multi-reader. `getSpanContent` handles cache hits, decompresses cached compressed spans, or fetches/decompresses directly. `fetchSpanWithRetries` reads from the backing `SectionReader` and retries only digest verification failures.

State and persistence: per-span state tracks whether content is unfetched, being fetched, compressed-cached, or uncompressed-cached. The configured `cache.BlobCache` persists span bytes under stringified span IDs for the manager lifetime or backing cache lifetime. `Close` closes `Zinfo` and cache once.

Dependencies and integration: integrates with zTOC metadata, compression index extraction, digest verification, cache implementations, containerd logging, and `ioutils.NewMultiReadCloser`/section read closers. The backing reader is usually remote layer content exposed through a range-capable fetcher.

Risks and test signals: correctness depends on monotonic zinfo offsets, matching zTOC `SpanDigests`, and correct `MaxSpanID`. `getSpanInfo` does not perform explicit bounds validation beyond zinfo mapping. Cache writes call `Commit` without checking its return value. Tests cover header corruption, digest mismatch, max-span mismatch, non-monotonic checkpoints, range reads, cache slicing, state transitions, and digest-verification retry counts.
