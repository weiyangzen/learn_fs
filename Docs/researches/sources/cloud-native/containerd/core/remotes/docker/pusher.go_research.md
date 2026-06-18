<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/pusher.go -->
# sources/cloud-native/containerd/core/remotes/docker/pusher.go

## Purpose
Implements Docker/OCI registry push support for blobs and manifests. It handles existence checks, cross-repository mounts, upload start/commit requests, streaming request bodies, upload status tracking, and content writer semantics.

## Important APIs, Types, And Functions
- `dockerPusher` wraps `dockerBase`, target object, and `StatusTracker`.
- `Writer(ctx, opts...)` implements content ingester semantics, validating `Ref`, digest, and media type, then calling `push` with `unavailableOnFail`.
- `Push(ctx, desc)` returns a writer using `remotes.MakeRefKey`.
- `push(ctx, desc, ref, unavailableOnFail)` is the core push state machine.
- `getManifestPath(object, dgst)` decides whether to PUT a manifest by tag or digest.
- `pushWriter` implements `content.Writer` over an async `io.Pipe` request body.
- `requestWithMountFrom` clones a request and adds `mount`/`from` query parameters.

## Control Flow
`push` locks by ref when the tracker supports it, injects pull/push auth scope, checks existing tracker status, filters push-capable hosts, and chooses the first host. It sends a `HEAD` to the target manifest/blob endpoint; existing content marks tracker status and returns `ErrAlreadyExists`.

For manifests it prepares `PUT /manifests/<tag-or-digest>` with content type. For blobs it sends `POST /blobs/uploads/`, optionally first with `mount` and `from` from distribution source annotations plus an appended pull scope. A `201 Created` mount marks committed status and returns already-exists. Otherwise it parses `Location`, adjusts host/scheme if redirected, strips authorizer when destination changes, appends the digest query, and prepares final `PUT`.

The returned `pushWriter` receives a pipe from the request goroutine, writes user bytes into it, tracks offset, closes/commits the pipe, waits for response or error, validates response status, optional `Docker-Content-Digest`, size, and expected digest, then marks status committed.

## State And Persistence
Push state lives in `StatusTracker`, usually the in-memory tracker from `status.go`. It records offsets, expected digest, start/update times, committed state, close errors, and mount/existence status. Registry state is mutated through HTTP uploads/manifests. No chunked resumable upload is implemented yet.

## Dependencies And Integration Points
Depends on `content.Writer`, `remotes.MakeRefKey`, Docker registry upload APIs, auth scopes from `scope.go`, distribution labels from `handler.go`, request/retry helpers from `resolver.go`, and `errdefs` classification.

## Risks And Edge Cases
Only the first push-capable host is used. Redirected upload destinations remove authorizer if host/scheme changes, which avoids credential leakage but can fail private redirects. Incomplete close sets `ErrClosed` so retries are allowed. `Commit` has no explicit timeout while waiting for the request goroutine. Manifests and blobs use different existence checks; tag/digest object handling is subtle.

## Test Signals
`pusher_test.go` covers manifest path selection, retry after closed incomplete upload, namespace query propagation, missing digest header acceptance, HTTP fallback, `ErrReset`, unauthorized mount fallback, existing content, successful/failed cross-repo mount, and blob/manifest push flows.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/pusher.go -->
