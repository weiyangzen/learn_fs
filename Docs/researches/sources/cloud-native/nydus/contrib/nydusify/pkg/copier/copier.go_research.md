# sources/cloud-native/nydus/contrib/nydusify/pkg/copier/copier.go

Purpose: copies images from a source reference or local tar to a target reference or local tar, with special handling for Nydus backend blobs so registry targets can receive externally stored blobs.

Important APIs/types/functions: `Opt`, `Copy`, `hosts`, `getLocalPath`, `getPlatform`, `getPusherInChunked`, and `pushBlobFromBackend`.

Control flow: `Copy` sets a containerd namespace, parses platforms, optionally creates a backend for source Nydus blobs, prepares work dirs, builds a streaming content store, imports or pulls the source, exports immediately for local targets, otherwise resolves manifests, optionally injects backend blob descriptors via `pushBlobFromBackend`, pushes target manifests, and pushes a rebuilt index for multi-platform sources. `pushBlobFromBackend` reads the manifest/config/bootstrap, runs nydus inspector output, deduplicates blob IDs, uploads each backend blob with chunked or normal push, prepends blob layers, updates config `RootFS.DiffIDs`, and writes new JSON descriptors.

State and persistence: uses temporary work dirs, provider content store state, transient `output.json`, unpacked bootstrap, and remote registry blobs/manifests. StreamContent minimizes local layer ingestion.

Dependencies and integration points: containerd images/content/remotes/compression, acceleration-service remote/platform utilities, nydus checker builder, backend readers/range readers, parser bootstrap detection, and provider push/pull/import/export.

Risks and test signals: plain HTTP retry is heuristic. Source/target identical refs collapse insecure settings. Manifest/config rewrite correctness and chunked push behavior are high-impact areas. Semaphore acquisition ignores returned errors.
