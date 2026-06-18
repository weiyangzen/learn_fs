# sources/cloud-native/nydus/contrib/nydusify/pkg/external/modctl/modctl_test.go

Purpose: tests the local modctl handler, tar parsing, option parsing, blob conversion, backend output, and helper methods.

Important fixtures/APIs: `MockReadSeeker`, `TestReadImageRefBlob`, `TestReadTarBlob`, `TestGetOption`, `TestHandle`, `TestModctlBackend`, `TestConvertToBlobs`, `TestExtractManifest`, `TestSetBlobsMap`, `TestSetWeightChunkSize`, `TestNewHandler`, `TestInitHandler`, `TestChunkMethods`, `TestGetChunkSizeByMediaType`, `TestGetConfig`, `TestGetLayers`, and `TestNeedIgnore`.

Control flow and state: tests build in-memory tar files, temporary registry-like blob paths, and handlers with preloaded blob maps. Gomonkey patches initialization in some constructor tests. `TestReadImageRefBlob` is environment-gated by `NYDUS_MODEL_IMAGE_REF` and exercises real remote model images.

Dependencies and integration points: tar archive format, local `/tmp` files in some tests, gomonkey monkey-patching, model provider remote, snapshotter external backend structs, humanize parsing, and OCI digests.

Risks and test signals: local tests cover many edge cases, but several use fixed `/tmp/test` paths and global chunk-size map state. Real-image coverage is optional. Tests validate offset expectations for small tar entries and confirm invalid CRC annotation JSON is rejected in the remote path indirectly.
