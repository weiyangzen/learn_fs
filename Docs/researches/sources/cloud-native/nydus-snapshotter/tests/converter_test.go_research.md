<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tests/converter_test.go -->
## sources/cloud-native/nydus-snapshotter/tests/converter_test.go

Purpose: integration-heavy tests for nydus converter pack/merge/unpack/image-convert/reconvert behavior, including fs versions 5/6, chunk dictionaries, OCI refs, S3 backend, and encryption.

Important APIs/helpers: tar builders (`buildChunkDictTar`, `buildOCILowerTar`, `buildOCIUpperTar`), `packLayer`, `packLayerRef`, `unpackLayer`, `verify`, `buildChunkDict`, option structs, `TestPack`, `TestPackRef`, `TestUnpack`, `TestImageConvert`, and `TestImageReConvert`. Embedded RSA keys support encryption tests.

Control flow and state: tests synthesize OCI tar layers with whiteouts/opaque dirs/large files, convert layers through `converter.Pack`, merge bootstraps, mount with a real `nydusd` via `tests/nydusd.go`, and verify file trees. Image conversion tests start local Docker registry/MinIO containers, pull nginx with `ctr`, convert/push images, optionally encrypt bootstraps, and validate with `nydusify`. Reconvert converts a nydus image back to OCI.

Dependencies/integration: depends on Docker, containerd socket, ctr, nydusd, nydusify, AWS S3 client, MinIO image, root privileges for cache drop/mounts, and local content store APIs.

Risks and test signals: high-value end-to-end coverage but expensive and environment-sensitive. Several tests assume Docker/containerd availability and root privileges; `TestPackRef` is gated by `TEST_PACK_REF`. Failure cleanup relies on deferred container/image removal.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tests/converter_test.go -->
