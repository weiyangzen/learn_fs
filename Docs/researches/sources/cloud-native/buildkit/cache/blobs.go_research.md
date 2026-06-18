# sources/cloud-native/buildkit/cache/blobs.go

Purpose: ensures immutable cache references have OCI layer blobs and chain metadata in the content store. It is central to exporting cache refs as image layers and to maintaining diff ID/blob/chain metadata.

Important APIs/types/functions: `(*immutableRef).computeBlobChain`, package `computeBlobChain`, `(*immutableRef).setBlob`, `(*immutableRef).computeChainMetadata`, `isTypeWindows`, `ensureCompression`, and `commitOverlayBD`. `ErrNoBlobs` signals a missing blob when creation is disallowed. Flightcontrol groups `g` and `gFileList` deduplicate concurrent work.

Control flow: the public method requires an active lease, finalizes the ref, switches to Windows layer mode for Windows refs, builds a layer filter, and recurses by ref kind (`Merge`, `Diff`, `Layer`). For refs included by the filter, a flightcontrol section checks existing blobs, creates a temporary lease, mounts lower/upper snapshots, selects overlay/walking/containerd/overlaybd diff paths, finalizes compression annotations, records the uncompressed digest label, and calls `setBlob`. After recursion it computes chain and blob-chain IDs.

State and persistence behavior: blob descriptors are persisted in ref metadata via queued diff ID, blob digest, media type, blob size, URLs, chain ID, and blob-chain ID followed by `commitMetadata`. Content blobs are protected by leases; temporary leases are adopted only after successful creation. `setBlob` also links the blob into descriptor handlers.

Dependencies and integration points: integrates containerd content, diff, leases, mounts, labels, walking differ, BuildKit compression/converter utilities, Windows layer mode, overlaybd labels/commit tooling, and OCI digest identity chain calculation. It calls OS-specific `tryComputeOverlayBlob`.

Risks: missing lease context is a hard error. Diff refs can intentionally reuse upper blobs, so the filter must be correct. Compression finalizers and label propagation are required for later descriptor lookup. Overlay differ fallback behavior differs by snapshotter and debug env var. Metadata corruption would affect exports, cache reuse, and garbage collection.

Test signals: this file is exercised indirectly by cache/export tests and contenthash tests that create refs. Snapshotter-specific and compression-specific paths need integration coverage because many branches depend on platform, snapshotter name, and environment variables.
