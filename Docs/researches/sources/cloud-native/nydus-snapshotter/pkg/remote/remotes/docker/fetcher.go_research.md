# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/fetcher.go

## Purpose
Implements registry content fetching for Docker/OCI manifests, blobs, external URLs, and digest-only fetches with HTTP range support.

## Important APIs, Types, And Functions
`dockerFetcher.Fetch`, `FetchByDigest`, `createGetReq`, and `open` are the core methods. `newHTTPReadSeeker` is used to provide seekable reads over repeated HTTP requests.

## Control Flow
`Fetch` filters pull-capable hosts, adds pull scope, and returns an HTTP read seeker. The seeker first tries descriptor `URLs`, then manifest endpoints for manifest media types, and finally blob endpoints. `FetchByDigest` performs HEAD/GET setup against `blobs/<digest>`, then falls back to `manifests/<digest>` with manifest accept headers. `open` sets Accept and Range headers, executes retries, decodes Docker error envelopes on non-2xx statuses, checks `Content-Range` when present, and otherwise discards bytes to emulate offset reads.

## State And Persistence
No durable state. It mutates request headers and relies on registry hosts, authorizers, and context scopes. Returned readers hold HTTP response bodies until closed.

## Dependencies And Integration Points
Integrates with `dockerBase.request`, `request.doWithRetries`, `scope.go`, Docker/OCI media types, `remote/remotes.FetcherByDigest`, and `httpreadseeker.go`.

## Risks And Edge Cases
If all hosts fail, the first error is returned and 404s are wrapped as not-found. External URLs use `http.DefaultClient` and only support HTTP(S). Range support is defensive because some registries advertise or ignore ranges inconsistently. Missing content length can lead to unknown-size seekers.

## Test Signals
`fetcher_test.go` covers offset reads, ignored and valid content ranges, invalid range errors, Docker error-envelope messages, plain status errors, and retry exhaustion for timeout/rate-limit statuses. `resolver_test.go` validates fetch and digest-fetch parity.
