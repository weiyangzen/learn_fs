<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/pusher_test.go -->
# sources/cloud-native/containerd/core/remotes/docker/pusher_test.go

## Purpose
Validates Docker pusher behavior across manifest uploads, blob uploads, existence checks, mount optimization, status tracking, auth/fallback handling, and writer retry/reset semantics.

## Important APIs, Types, And Functions
- `TestGetManifestPath` checks tag-vs-digest path construction.
- `TestPusherErrClosedRetry` ensures an upload closed with an error can be retried.
- `TestPusherCustomNamespace` verifies proxy namespace query propagation on final PUT.
- `TestPusherAcceptsMissingDigestHeader` confirms commit can succeed without `Docker-Content-Digest`.
- `TestPusherHTTPFallback` exercises HTTPS-to-HTTP fallback during push with basic auth.
- `TestPusherErrReset` verifies writer reset when a request must be retried.
- `TestPusherInvalidAuthorizationOnMount` verifies private-source mount auth failures fall back to normal upload.
- `Test_dockerPusher_push` covers manifest, existing content, mounted blob, failed mount, and normal blob push.
- `uploadableMockRegistry` is a small in-memory registry simulator.

## Control Flow
Tests build `samplePusher` backed by `httptest.Server`, then drive content through `Writer` or `push`. The mock registry implements minimal `HEAD`, `POST /blobs/uploads/`, and `PUT` behavior, including optional auth, omitted digest headers, mount responses, and upload failures.

## State And Persistence
The mock registry persists uploaded digest strings in memory. The pusher uses `NewInMemoryTracker`, and several assertions inspect tracker `PushStatus` values.

## Dependencies And Integration Points
Uses `content.Copy`, OCI descriptors/manifests, `remotes.MakeRefKey`, `reference.Spec`, and registry host configuration. It tests integration among `pusher.go`, `status.go`, `handler.go`, `scope.go`, and HTTP fallback in `resolver.go`.

## Risks And Edge Cases
The tests show the pusher must tolerate missing digest headers but reject mismatched digest headers, must recover from mount authorization failures, and must not confuse existing remote content with active local uploads.

## Test Signals
High-value integration signal for registry upload state transitions. It does not cover multi-host push fallback because production code selects the first push-capable host.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/pusher_test.go -->
