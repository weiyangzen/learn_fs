# sources/cloud-native/nydus-snapshotter/pkg/converter/reconvert_unix_test.go

Purpose: tests reconversion helper behavior without invoking the external nydus-image binary.

Important APIs and functions: `mockContentStore`, `mockReaderAt`, `TestCollectNydusBlobDigests`, `TestCollectFromManifest`, `TestWrappedStore_Info`, `TestWrappedStore_Info_Error`, `TestMakeOCIBlobDesc`, `TestReconvertHookFunc_NilDescriptor`, and `TestReconvertHookFunc_NonManifestType`.

Control flow: tests build synthetic OCI manifests/indexes in an in-memory content store, scan for nydus blob annotations, verify bootstrap and regular layers are ignored by blob collection, wrap store info calls to inject uncompressed labels for selected digests, build descriptors for compressed target blobs, and ensure the reconvert hook handles nil and non-manifest descriptors.

State and persistence: mock store maps digests to `content.Info` and byte slices. No real content writes or external process execution.

Dependencies and integration points: exercises production JSON reading through `readJSON`, descriptor constants, and reconvert helper logic.

Risks and gaps: the mock store does not implement writer/update paths needed by full `ReconvertHookFunc` manifest rewriting or `LayerReconvertFunc`, so those paths are not covered. No tests for compressor selection, bootstrap removal from a real manifest, config history cleanup, GC label cleanup, or backend pushes.

Test signals: good focused coverage for nydus blob discovery and the content-store info workaround that prevents containerd from decompressing nydus blobs.
