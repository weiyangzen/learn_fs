# sources/cloud-native/soci-snapshotter/util/testutil/ensurehello.go

## Purpose
`ensurehello.go` provides an integration-test helper that downloads a known `hello-world` OCI archive, verifies its digest, imports it into a temporary containerd content store, and returns the image descriptor and store.

## Important APIs, Types, and Functions
Constants `HelloArchiveURL` and `HelloArchiveDigest` identify the fixture archive. `EnsureHello(ctx)` performs the download, gzip decompression, digest calculation, temporary directory creation, local content store creation, and `archive.ImportIndex`.

## Control Flow, State, and Persistence
The function streams the HTTP response through an SHA256 tee reader and gzip reader. It creates a temporary content store on disk with `os.MkdirTemp` and `local.NewStore`. The store persists after return; the helper does not return the temp path or register cleanup, so callers must manage lifecycle through the returned content store and process temp cleanup policies.

## Dependencies and Integration Points
It depends on net/http, gzip, containerd content/archive/local store packages, OCI descriptors, and `go-digest`. It integrates with tests needing a real image without a daemon pull.

## Risks and Test Signals
The helper is network-dependent and uses `http.Get` without context binding or response status checks. It closes `resp.Body` twice, which is harmless but redundant. Digest verification protects against fixture corruption after import, but if import reads before full digest consumption, digest calculation depends on the tee reader being fully consumed by the gzip importer.
