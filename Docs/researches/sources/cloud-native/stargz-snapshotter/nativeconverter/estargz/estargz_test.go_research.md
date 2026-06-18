# sources/cloud-native/stargz-snapshotter/nativeconverter/estargz/estargz_test.go

## Purpose
Tests the native eStargz layer converter as a pure unit test without requiring a daemon.

## Important APIs, Types, And Functions
`TestLayerConvertFunc` uses `testutil.EnsureHello` to create sample content, `LayerConvertFunc` with prioritized file option, `converter.DefaultIndexConvertFunc`, and `images.Walk` to inspect converted descriptors.

## Control Flow
The test builds or locates a sample hello image in a content store, converts the image with Docker-to-OCI enabled and default platform matching, walks the converted descriptor graph, collects any `estargz.TOCJSONDigestAnnotation`, and fails if no converted eStargz layer was found.

## State And Persistence
State is limited to the test content store returned by `EnsureHello`. Converted blobs and descriptors live in that store for the duration of the test.

## Dependencies And Integration
Depends on containerd image walking/converter APIs, platforms matcher, local eStargz converter, local eStargz annotations, and test utility content fixtures.

## Risks And Test Signals
Passing confirms the converter can process a real sample layer and emit TOC annotations through an index conversion. It does not verify byte-for-byte layer contents, lazy-read performance, all media type variants, or uncompressed-size annotation correctness.
