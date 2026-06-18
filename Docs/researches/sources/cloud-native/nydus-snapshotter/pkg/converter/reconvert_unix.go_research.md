# sources/cloud-native/nydus-snapshotter/pkg/converter/reconvert_unix.go

Purpose: implements nydus-to-OCI reconversion helpers and hooks, including a workaround for containerd diff ID calculation on nydus blobs.

Important APIs and functions: `DefaultIndexConvertFunc`, `collectNydusBlobDigests`, `collectFromManifest`, `wrappedStore.Info`, `ReconvertHookFunc`, `LayerReconvertFunc`, and `makeOCIBlobDesc`.

Control flow: `DefaultIndexConvertFunc` wraps containerd's `IndexConvertFuncWithHook` with `ReconvertHookFunc`; before conversion it scans the input descriptor for nydus blob digests and wraps the content store when needed. `wrappedStore.Info` injects `containerd.io/uncompressed` labels for nydus blobs so containerd skips decompression attempts. `ReconvertHookFunc` runs on converted manifests, removes nydus bootstrap layers and their GC labels, removes the corresponding rootfs diff ID when possible, strips the synthetic "Nydus Bootstrap Layer" history entry, writes updated config JSON, updates config GC labels, and writes the updated manifest. `LayerReconvertFunc` skips non-layers and bootstrap layers, unpacks nydus blobs to tar via `Unpack`, recompresses as gzip/zstd/uncompressed, commits to content store with uncompressed label, builds an OCI descriptor, and optionally pushes to backend.

State and persistence: writes converted OCI blobs, configs, and manifests into the content store. Optional backend push persists converted blobs remotely. The wrapped store mutates returned `content.Info.Labels` maps in memory but does not update the underlying store.

Dependencies and integration points: integrates with containerd image converter hooks, platform matching, content store, OCI descriptors/config, gzip/zstd, and conversion constants. Calls `Unpack` from `convert_unix.go`.

Risks: `ReconvertHookFunc` removes a diff ID only when `bootstrapIndex` is within bounds; mismatched config/layer history may remain inconsistent. `LayerReconvertFunc` computes uncompressed digest while writing through the compressor; for gzip/zstd this digester is attached to the compressed stream writer input before compression, so intent is uncompressed tar digest, but code changes here are high-risk. Unsupported compressor values hard fail. Full reconversion depends on external `nydus-image unpack`.

Test signals: `reconvert_unix_test.go` covers scanning nydus blobs, wrapped store label injection, OCI descriptor construction, and hook no-op cases; full layer reconversion is not directly tested.
