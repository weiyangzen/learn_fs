<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/imageinfo.go -->
# sources/cloud-native/buildkit/util/testutil/imageinfo.go

Purpose: reads OCI image/index descriptors from a content provider into convenient test structures including parsed config and layer tar contents.

Important APIs and types: `ImageInfo`, `ImagesInfo`, `Find`, `Filter`, `FindAttestation`, `ReadImages`, and `ReadImage`.

Control flow: `ReadImages` reads the root descriptor as an index; if it is not an index media type, reads a single image and derives platform from image config. For indexes, it reads each manifest descriptor and stores platform from descriptor platform. `ReadImage` reads manifest, validates media type, reads image config, then reads every layer; layer media types are decompressed/parsed via `ReadTarToMap`.

State and persistence: builds in-memory structures and raw layer byte slices from content provider blobs.

Dependencies and integration: uses containerd content/images helpers, OCI specs, platform formatting, and test tar helpers. Used by image-output integration tests.

Risks: assumes index manifests have non-nil `Platform`; nil would panic. Attestation lookup assumes `Desc.Annotations` is non-nil before indexing. Reads all layer blobs into memory.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/imageinfo.go -->
