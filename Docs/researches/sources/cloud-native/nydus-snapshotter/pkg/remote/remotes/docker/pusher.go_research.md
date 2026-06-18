# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/pusher.go

## Purpose
Implements Docker registry push support for blobs and manifests, including existence checks, upload sessions, cross-repository mount attempts, streaming writers, and in-memory upload status tracking.

## Important APIs, Types, And Functions
`dockerPusher.Writer`, `Push`, `push`, `getManifestPath`, `pushWriter` methods, and `requestWithMountFrom` are core. It uses `StatusTracker` from `status.go`.

## Control Flow
`push` locks by ref when possible, adds push scope, checks tracker state, filters push-capable hosts, and HEAD-checks existing content. Manifests are pushed with a PUT to `manifests/<tag-or-digest>`. Blobs start with POST to `blobs/uploads/`, optionally first trying `mount`/`from` based on source annotations. It follows the upload `Location`, appends `digest`, and creates a `pushWriter` backed by an `io.Pipe`. A goroutine performs the final PUT while the caller writes content through the writer. `Commit` closes the pipe, waits for response/error/reset, checks status, size, and `Docker-Content-Digest`, then marks the tracker committed.

## State And Persistence
Status is kept in the provided tracker: ref, total, expected digest, offset, start/update times, commit flag, close error, and upload UUID field. Registry state changes are remote writes. No local durable upload resume is implemented.

## Dependencies And Integration Points
Integrates with registry requests/auth/retries, content writer API, remotes ref keys, distribution-source labels from `handler.go`, and `remote/remotes/errors`.

## Risks And Edge Cases
Chunked upload/resume is TODO. Redirecting upload locations strip the authorizer when host/scheme changes, which avoids credential leakage but can fail if redirected host needs auth. `Commit` waits without timeout. Incomplete close records `ErrClosed` so later retries are allowed.

## Test Signals
`pusher_test.go` covers manifest path selection, retry after closed incomplete upload, reset after timeout, already-exists handling, manifest push, blob push, and mock registry status flows.
