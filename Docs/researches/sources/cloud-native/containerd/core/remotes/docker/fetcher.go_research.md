<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/fetcher.go -->
# sources/cloud-native/containerd/core/remotes/docker/fetcher.go

## Purpose
Implements Docker/OCI registry content retrieval. It provides `dockerFetcher.Fetch`, `FetchByDigest`, low-level HTTP opening, content-encoding decoding, range seeking, and optional parallel chunked downloads.

## Important APIs, Types, And Functions
- `dockerFetcher` wraps `*dockerBase` and implements `remotes.Fetcher`, `remotes.FetcherByDigest`, and, via `referrers.go`, `remotes.ReferrersFetcher`.
- `Fetch(ctx, desc)` returns an `io.ReadCloser` for descriptor content, trying descriptor URLs, manifest endpoints for manifest/index media types, then blob endpoints.
- `FetchByDigest(ctx, dgst, opts...)` fetches content by digest, probing blobs first and manifests second, and returns a best-effort descriptor.
- `open(ctx, req, mediatype, offset, lastHost)` is the core HTTP path. It sets `Accept`, `Accept-Encoding`, optional `Range`, applies the download limiter, validates status/range, optionally parallelizes reads, and decodes zstd/gzip/deflate responses.
- `pipe`, `pipeReader`, `pipeWriter`, `bufferPool`, and `newPipeWriter` implement the asynchronous buffered in-memory pipes used to order chunk results from concurrent range requests.
- `fnOnClose` releases limiter capacity and cancels parallel fetch work before closing the wrapped reader.

## Control Flow
`Fetch` first filters hosts with `HostCapabilityPull` and injects repository pull scope into context. The returned `httpReadSeeker` calls back with offsets. For each open, external URLs are attempted only for HTTP(S), then registry `GET /manifests/<digest>` for manifests/indexes, then `GET /blobs/<digest>`. `FetchByDigest` does a `HEAD`-first `createGetReq` over blobs and manifests to discover size, then creates a seekable reader.

`open` decides parallelism from `transfer.ImageResolverPerformanceSettings`. Small buffers, request bodies, missing/ignored ranges, or small content force single-stream mode. In parallel mode it splits the remaining body into chunks, queues chunk indexes, reuses the first response body for chunk zero, opens cloned range requests for later chunks, writes each chunk into ordered pipe readers, and exposes an `io.MultiReader` over those readers. It then wraps the stream with decoders in reverse `Content-Encoding` order.

## State And Persistence
Fetcher itself persists no content. It consumes shared resolver state: host list, repository, headers, performance settings, and download limiter. The custom pipe holds transient buffered chunk data and returns buffers to a pool. The limiter is acquired per in-flight request and released through close/error cleanup.

## Dependencies And Integration Points
Depends on Docker registry endpoints, `dockerBase.request`, retry/error helpers in `resolver.go`, OCI/Docker media-type helpers from `images`, descriptor metadata from OCI image spec, and `remotes` interfaces. Integrates with `httpreadseeker.go` for reconnectable seeking and with `handlers.go` when content is copied into a content store.

## Risks And Edge Cases
Parallel range handling is sensitive: ignored `Range` headers must collapse concurrency, incorrect `Content-Range` offsets must fail, and body/limiter cleanup must happen even when decoders fail. Encoded range responses can be tricky because the code decodes after parallel assembly. Descriptor URLs bypass registry auth and only allow HTTP(S). `FetchByDigest` returns incomplete descriptors when media type is unknown.

## Test Signals
`fetcher_test.go` covers offset handling, registries that ignore ranges, invalid ranges, parallel reads, retry of mid-stream request timeouts, close behavior after copy errors, zstd/gzip/deflate decoding chains, registry error messages, and limiter release on decoder errors. `fetcher_fuzz_test.go` fuzzes arbitrary payload fetches through an HTTP test server.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/fetcher.go -->
