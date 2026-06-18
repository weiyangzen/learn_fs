# sources/cloud-native/buildkit/client/client_nydus_test.go

## Purpose

This build-tagged test file validates image export behavior when Nydus compression is enabled. It ensures Nydus layers are produced with expected annotations and are not mixed incorrectly with gzip or zstd compressed layers across repeated exports.

## Important APIs, Types, and Functions

- Build tag `nydus` gates compilation.
- `init` appends `testBuildExportNydusWithHybrid` to the shared integration test list.
- `testBuildExportNydusWithHybrid` builds and pushes images with Nydus, gzip, and zstd compression and inspects stored manifests.

## Control Flow and State

The test requires direct push support, Linux, and a containerd worker address. It creates a containerd client, a registry fixture, and a BuildKit client. Helper `buildNydus` builds an Alpine-derived image that touches a file, exports it as an image with `compression=nydus`, OCI media types, push, and forced compression, then reads the pushed image manifest from containerd. It asserts there are three layers and checks Nydus blob/bootstrap annotations. Helper `buildOther` repeats the flow for gzip or zstd and asserts two layers with the expected OCI media type.

The sequence builds Nydus, gzip, zstd for one file and gzip, zstd, Nydus for another, guarding against cross-build compression cache contamination.

## Dependencies and Integration Points

The test depends on containerd image/content services, nydus snapshotter converter annotations, BuildKit image exporter compression options, registry fixtures, LLB image/run construction, and integration worker feature gates.

## Risks and Edge Cases

The test is only compiled with the `nydus` build tag and requires containerd, a registry fixture, and direct push. It inspects manifests from the containerd namespace `buildkit`, so namespace or image-service changes can affect it. It validates manifest shape and annotations, not runtime mountability of the resulting Nydus image.

## Test Signals

This is the subset's signal for Nydus export compression isolation. It indirectly exercises the client solve/export path and cache/compression behavior across sequential builds.
