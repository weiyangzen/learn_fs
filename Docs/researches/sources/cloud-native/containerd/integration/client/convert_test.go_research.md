<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/convert_test.go -->
# sources/cloud-native/containerd/integration/client/convert_test.go

## Purpose
Tests image conversion from Docker media types to OCI media types, compressed layers to uncompressed tar layers, and multi-platform image metadata to a single selected platform.

## APIs, Types, And Functions
`TestConvert` uses `client.Fetch`, `converter.Convert`, `converter.WithDockerToOCI`, `converter.WithLayerConvertFunc`, `uncompress.LayerConvertFunc`, `converter.WithPlatform`, `images.Platforms`, and `images.Manifest`.

## Control Flow And State
The test fetches `testImage`, converts it to a derived reference, deletes the derived image during cleanup, inspects available platforms on the converted target, and then reads the manifest for the default strict platform to assert that every layer has `ocispec.MediaTypeImageLayer`.

## Persistence And Integration Points
Conversion writes new image records and content blobs through the client content store and image service. It integrates containerd's image converter package, OCI descriptors, platform matching, and layer decompression pipeline.

## Risks And Test Signals
Failures indicate conversion regressions in media type rewriting, layer conversion, platform filtering, or image record cleanup. Because the test fetches from an image reference and mutates daemon content, it is skipped in short mode.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/convert_test.go -->
