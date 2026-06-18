# sources/cloud-native/buildkit/source/containerblob/pull.go

## Purpose
This file implements the source instance that turns a single image/blob digest into a one-file snapshot. It fetches the blob, computes a stable cache key from digest and file attributes, writes the blob into a new cache ref, and commits the snapshot.

## Important APIs and Types
`puller` stores the source, identifier, session manager, cached read closer, and digest. `hash` returns a digest over the blob digest plus filename, permission, UID, and GID. `ensureResolver` opens the blob stream through `blobfetch.FetchBlob`. `CacheKey` returns the stable hash and image digest. `Snapshot` materializes the file into a cache mount.

## Control Flow
`CacheKey` validates the reference digest, checks the content store for existing content/source metadata, and returns the hash as a completed cache key regardless of whether the content already exists. `Snapshot` gets the session group, ensures a reader, creates a retained mutable cache ref, mounts it, chooses the file mode and safe filename, opens the mount root with `os.OpenRoot`, writes the stream while hashing, applies identity-mapped ownership if needed, normalizes mtime to Unix epoch, unmounts, and commits.

## State and Persistence
The persistent artifact is the committed cache snapshot containing one file. Temporary state includes `p.rc`, which is closed and cleared after snapshot. File metadata is deterministic: default mode 0600, name defaults to digest hex, and mtime is zero.

## Dependencies and Integration Points
It depends on BuildKit cache, snapshot local mounter, sessions, content store, blobfetch, path utilities, and OCI digest. It implements the source instance methods expected by the solver.

## Risks
The code computes a SHA256 while copying but does not compare it to `p.dgst`; integrity relies on upstream fetch/content validation. Snapshot cleanup is carefully deferred, but mount unmount errors are only captured through the main error path. Large blobs stream directly into the snapshot and can consume disk.

## Test Signals
No direct tests in this subset. Related coverage should come from source integration tests that assert cache keys, file metadata, and registry/OCI fetch behavior.
