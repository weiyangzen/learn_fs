# sources/cloud-native/buildkit/cache/blobs_linux.go

Purpose: Linux overlayfs-specialized diff generation for cache blobs. It tries to create a tar diff directly from overlay upperdir data before falling back to generic differs in `blobs.go`.

Important APIs/types/functions: `emptyDesc` and `(*immutableRef).tryComputeOverlayBlob`. The function returns `(descriptor, ok, error)` so callers can distinguish unsupported mounts from real failures.

Control flow: it calls `overlay.GetUpperdir` to verify compatible overlay mounts. It opens a content writer with the ref and media type, truncates previous ingest state, wraps the writer in a buffered writer, optionally wraps compression and an uncompressed digester, writes the overlay upperdir diff, flushes, commits content, closes the writer, then reads content info to build an OCI descriptor. On pre-commit errors it aborts the content-store ingest using a context that ignores cancellation.

State and persistence behavior: writes content blobs to the cache manager content store and stores/updates the `containerd.io/uncompressed` label when compression is used. It does not write ref metadata directly; `blobs.go` consumes the descriptor and persists metadata.

Dependencies and integration points: depends on containerd content APIs, errdefs, labels, BuildKit overlay diff writer, compression callbacks, and logger. Called only on Linux builds.

Risks: the branch setting a missing uncompressed label assumes `labels` is non-nil; callers currently provide a compressor when this path needs the label. Writer abort/close handling is important to avoid locked content ingests. Overlay mount detection must stay conservative to avoid producing incorrect diffs.

Test signals: coverage is mostly integration-level via overlayfs snapshotter behavior. Fallback branches in `blobs.go` protect unsupported snapshotters such as native or fuse-overlayfs.
