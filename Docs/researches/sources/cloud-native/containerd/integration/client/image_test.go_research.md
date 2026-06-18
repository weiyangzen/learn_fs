<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/image_test.go -->
# sources/cloud-native/containerd/integration/client/image_test.go

## Purpose
Tests image lifecycle APIs for unpack status, distribution source labels, content usage accounting, snapshot usage accounting, and snapshotter-platform compatibility errors.

## APIs, Types, And Functions
The file defines `TestImageIsUnpacked`, `TestImagePullWithDistSourceLabel`, `TestImageUsage`, and `TestImageSupportedBySnapshotter_Error`. It uses `Pull`, `Fetch`, `ImageService().Delete`, `Image.IsUnpacked`, `Image.Unpack`, `Image.Usage`, `Image.RootFS`, `images.Dispatch`, `images.LimitManifests`, content `Info`, usage options, default snapshotter, and platform matchers.

## Control Flow And State
Tests delete any preexisting image record, pull without unpack, assert unpack state, then unpack and reassert. Distribution label coverage walks the selected platform descriptor graph and checks `containerd.io/distribution.source.<registry>` labels include the repository name. Usage coverage compares single-manifest usage, all-manifest usage, manifest-reported usage, full fetched content, and snapshot usage after unpack. Unsupported snapshotter coverage pulls an image for the opposite OS and expects unpack to fail under platform checking.

## Persistence And Integration Points
The tests persist image records, content labels, descriptors, and snapshots in the default snapshotter. They integrate with registry pulls, platform filtering, content labeling, image usage options, and snapshotter platform validation.

## Risks And Test Signals
Failures indicate incorrect unpack tracking, lost distribution source labels, undercounted/overcounted usage, or allowing incompatible image layers into a snapshotter. Tests may depend on registry availability and platform-specific image references.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/image_test.go -->
