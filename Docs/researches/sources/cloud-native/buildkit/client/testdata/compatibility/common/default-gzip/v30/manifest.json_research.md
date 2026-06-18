# sources/cloud-native/buildkit/client/testdata/compatibility/common/default-gzip/v30/manifest.json

## Purpose
This JSON fixture is an image manifest baseline for the BuildKit client compatibility suite. It belongs to `common/default-gzip/v30`, representing the common fixture shared by exporter compatibility tests across image layout modes and the default gzip compression baseline.

## Important Fields and Data Shape
- Schema version: `2`.
- Manifest media type: `application/vnd.oci.image.manifest.v1+json`.
- Config descriptor media type: `application/vnd.oci.image.config.v1+json`, digest `sha256:1772fd0a3b45a62fc...`, size `2295`.
- Layer count: `4`.
- Layer media types: `application/vnd.oci.image.layer.v1.tar+gzip`.
- First layer digest/size: `sha256:430ee4fa77d640d42...` / `2219886`.
- Manifest annotations present: `False`; layer descriptors with annotations: `4`.
- Compatibility version directory: `v30`.

## Control Flow and Integration Role
The file is fixture input for compatibility comparisons. Tests use it to verify that exporter output preserves expected manifest media types, config references, layer descriptors, annotations, compression choices, and compatibility-version behavior.

## State and Persistence Behavior
The manifest models persisted registry or OCI-layout metadata. It is content-addressable through its JSON bytes, and its config/layer descriptors must match adjacent config blobs and generated layer blobs. It has no runtime mutation path.

## Dependencies and Integration Points
It integrates with exporter compatibility tests, the image/OCI exporter, compression settings, OCI/Docker media-type conversion, provenance/annotation options, and adjacent `config.json` fixture files where present.

## Risks and Edge Cases
Risks include digest churn from non-deterministic timestamps or compression, wrong Docker-vs-OCI media types, dropped annotations, incorrect uncompressed/zstd media type selection, or layer order changes. For `manifest-annotation` fixtures, annotations are part of the behavior under test. For compression fixtures, descriptor sizes and digests are sensitive to compressor settings.

## Test Signals
A match means BuildKit emitted the expected manifest structure for `default-gzip` in `common` mode at compatibility version `v30`. A mismatch is a high-signal exporter compatibility regression because consumers use these descriptors to pull or load the image.
