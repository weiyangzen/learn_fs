# sources/cloud-native/nydus-snapshotter/pkg/backend/localfs.go

Purpose: stores nydus blobs as digest-named files in a local directory backend.

Important APIs and functions: `LocalFSBackend` holds `dir` and `forcePush`; `newLocalFSBackend` parses `{"dir": "..."}; `dstPath` maps blob hex to a path; `Push`, `Check`, `Type`, and `Size` implement `Backend`.

Control flow: `Push` skips existing blobs unless `forcePush` is true, creates the backend directory, opens the descriptor from the content store, creates/truncates the destination file named by digest hex, and copies the full content. `Check` stats the expected file and returns errdefs not found for missing paths or directories. `Size` stats the file.

State and persistence: blobs persist as files under the configured directory. There is no metadata aside from file names and sizes.

Dependencies and integration points: uses containerd content readers and `errdefs.ErrNotFound`. It is selected by `NewBackend("localfs", ...)` and can be used by converter pack/merge paths.

Risks: `path.Join` is used rather than `filepath.Join`; with digest hex this is harmless on Unix but less portable. `os.Create` overwrites existing files when `forcePush` is true and does not use atomic rename, so interrupted writes can leave partial blobs. No digest verification is performed after copy.

Test signals: no listed direct tests for localfs backend.
