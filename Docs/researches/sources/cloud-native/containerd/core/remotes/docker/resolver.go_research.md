<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/resolver.go -->
# sources/cloud-native/containerd/core/remotes/docker/resolver.go

## Purpose
Implements the Docker registry resolver and shared HTTP request machinery for resolving references, creating fetchers/pushers, authorizing requests, retrying transient failures, sanitizing logs, and falling back from HTTPS to HTTP for configured scenarios.

## Important APIs, Types, And Functions
- `Authorizer` defines `Authorize` and `AddResponses` for challenge-based auth.
- `ResolverOptions` configures hosts, headers, tracker, legacy credentials/authorizer/client/plain HTTP settings.
- `NewResolver` builds a `dockerResolver`, clones headers to avoid races, splits resolve `Accept` headers, and creates default registry hosts when needed.
- `Resolve(ctx, ref)` resolves a tag/digest to an OCI descriptor using trusted hosts.
- `Fetcher` and `Pusher` construct Docker fetcher/pusher instances for a ref.
- `dockerBase` stores parsed reference, repository, hosts, headers, performance settings, and download limiter.
- `request` builds and executes registry HTTP requests, with auth, body replay, redirect authorization, namespace query support, retries, and sanitized logging.
- `withErrorCheck`, `withOffsetCheck`, `doWithRetries`, `retryRequest`, and `doWithTransportRetries` implement response and transport retry policy.
- `IsLocalhost`, `NewHTTPFallback`, `isTLSError`, and `isPortError` support local registry HTTP fallback.

## Control Flow
`Resolve` parses the reference, decides endpoint paths (`/manifests/<object>` for tags, `/manifests/<digest>` then possibly `/blobs/<digest>` for digests), filters hosts by pull/resolve capability, injects pull scope, and iterates paths and hosts. It prefers errors by priority: transport/auth, not found, unexpected HTTP status, and oversize manifest. HEAD is used first; if digest/size are missing it GETs the manifest to compute digest or size. Schema1 manifests are rejected. The final descriptor includes digest, media type, and size, bounded by `MaxManifestSize`.

`request.do` constructs an HTTP request, clones headers, attaches replayable body, authorizes initial and redirect requests, applies tracing, and returns the response. `doWithRetries` combines transport retries, auth challenge retries, selected status retries, and caller checks. Status retries include auth challenge, HEAD-to-GET for manifest 405, 408/429, and selected 5xx only on the last host. Transport retries apply only on last host and only for timeout/EOF/unexpected EOF, respecting context cancellation.

`NewHTTPFallback` wraps a transport. On TLS handshake/port errors it retries the same request as `http://` and remembers the host so future requests use HTTP directly. It replays the body with `GetBody` when needed.

## State And Persistence
Resolver state is in-memory: hosts, cloned headers, tracker, transfer performance options, and optional limiter. HTTP fallback stores the host that fell back behind a mutex. No registry data is persisted by resolver itself.

## Dependencies And Integration Points
Depends on containerd `images`, `remotes`, `transfer`, `reference`, tracing/logging, `errdefs`, OCI descriptors, digest validation, and registry host configuration. It is the factory for fetcher and pusher and provides common `request` behavior they reuse.

## Risks And Edge Cases
Resolving tags trusts only resolve-capable hosts; wrong host capabilities can be a security risk. Fallback from manifests to blobs is intentionally limited to 404 to avoid poisoning descriptors with blob media types after transient manifest failures. Query logging must redact secrets while preserving `ns`. `MaxManifestSize` prevents large-manifest DoS but may reject legitimate non-image artifacts with large annotations. Retry semantics differ by last-host status to preserve mirror fallback behavior.

## Test Signals
`resolver_test.go` covers HTTP/HTTPS resolution, header clone races, basic/token/refresh auth, bad/missing/wrong auth errors, host fallback, TLS fallback, proxy namespace queries, query sanitization, transient transport classification and retry counts, digest manifest 5xx vs 404 fallback, and unexpected status code wrapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/resolver.go -->
