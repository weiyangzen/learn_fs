# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/resolver.go

## Purpose
Implements the Docker registry resolver: reference resolution to descriptors, fetcher/pusher construction, HTTP request composition, retry/auth handling, proxy namespace query support, and default resolver setup.

## Important APIs, Types, And Functions
`ResolverOptions`, `NewResolver`, `dockerResolver.Resolve`, `Fetcher`, `Pusher`, `dockerBase`, `request.do`, `doWithRetries`, `retryRequest`, `getManifestMediaType`, `DefaultHost`, and `IsLocalhost`.

## Control Flow
`NewResolver` prepares headers, default user agent, Accept headers, tracker, and hosts. `Resolve` parses a Docker reference, builds candidate manifest/blob paths depending on tag or digest input, filters hosts by pull/resolve capability, adds pull scope, and issues HEAD requests. It trusts `Docker-Content-Digest` only for tag resolution from resolve-capable hosts; if digest or size is absent it GETs the content and computes digest, with schema1 signature stripping. Oversized manifests are rejected. `request.doWithRetries` handles 401 auth learning, HEAD-to-GET fallback for unsupported manifest HEAD, and retryable timeout/rate-limit statuses.

## State And Persistence
Resolver state is headers, host function, resolve headers, and upload tracker. Requests clone headers to avoid concurrent map access. No disk state is used.

## Dependencies And Integration Points
Implements `remote/remotes.Resolver` and returns `dockerFetcher`/`dockerPusher`. Integrates with registry host config, authorizers, schema1 converter helpers, OpenTelemetry tracing, content media types, and `remote/remotes/errors`.

## Risks And Edge Cases
Manifest digest computation by GET can consume up to response size before enforcing `MaxManifestSize`; the size guard follows the read. Retry recursion is capped by response count. Auth errors are rewritten for user-facing pull/push access denial. Header mutation in `NewResolver` removes Accept from general headers when provided.

## Test Signals
`resolver_test.go` covers HTTP/TLS, Basic and bearer token auth, refresh tokens, bad tokens, host fallback, TLS fallback, proxy namespace resolution, fetcher construction, digest fetches, and content verification.
