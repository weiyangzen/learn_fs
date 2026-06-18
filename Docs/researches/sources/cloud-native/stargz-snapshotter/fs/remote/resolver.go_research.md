# sources/cloud-native/stargz-snapshotter/fs/remote/resolver.go

## Purpose
Resolves OCI layer descriptors into fetchers and blob readers. It supports custom remote handlers, Docker registry hosts, authenticated transports, redirects, size discovery, retry/backoff, multipart range parsing, signed URL refresh, and single-range fallback.

## Important APIs, Types, And Functions
`NewResolver` normalizes `config.BlobConfig`. `Resolver.Resolve` returns a `Blob`; `resolveFetcher` chooses a custom `Handler` or HTTP fetcher. `newHTTPFetcher`, `redirect`, and `getSize` build a registry URL and determine blob size. `httpFetcher.fetch`, `check`, `refreshURL`, and `genID` implement remote range access. `Handler` and `Fetcher` define extension points.

## Control Flow
Resolution first tries configured handlers. If none succeed, registry hosts are enumerated. Each host is validated, wrapped with authorization if needed, redirected with a `GET` range probe, and measured with `HEAD` or fallback `GET`. Fetching squashes adjacent/overlapping regions, optionally collapses to one range, performs `GET Range`, and interprets 200, 206 multipart, and 206 singlepart responses. Forbidden responses trigger URL refresh once; bad multi-range requests switch to single-range mode once.

## State And Persistence
HTTP fetcher state is in memory: current URL, headers, original registry headers, single-range mode, timeout, digest, and transport. Cache identity uses SHA-256 over `blobURL-b-e`, so refreshed redirected URLs do not change cache keys.

## Dependencies And Integration
Depends on containerd Docker resolver types, retryablehttp, registry authorizers, `fs/source.RegistryHosts`, blob config, metrics, OCI descriptors, and digest IDs. `remoteFetcher` adapts non-HTTP handlers into the same internal fetcher interface.

## Risks And Test Signals
Risks include registry-specific redirect and HEAD behavior, large multi-range headers, unsigned `Content-Range` parsing, random jitter panics if crypto randomness fails, and unsupported nested redirects. Tests cover mirror selection, custom headers, redirects, check failures, and retry behavior.
