<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/converter.go -->
# sources/cloud-native/containerd/core/remotes/docker/converter.go

Purpose: converts legacy Docker schema2 manifests whose config media type is `application/octet-stream` into manifests using the Docker schema2 config media type.

Important APIs/types/functions: `LegacyConfigMediaType` and `ConvertManifest`.

Control flow: exits unchanged for non-manifest descriptors. Reads the manifest blob from a content store, unmarshals OCI manifest JSON, returns unchanged when config media type is not legacy, rewrites the config media type, marshals indented JSON, recomputes descriptor digest/size, builds GC reference labels for config and layers, and writes the new blob under a remote ref key.

State and persistence: writes a new content blob to `content.Store`; the old manifest is left for future GC. Descriptor digest/size are returned for the new content.

Dependencies and integration points: used in Docker remote conversion paths to normalize old registry content. Integrates `content.ReadBlob`, `content.WriteBlob`, `images` media type helpers, OCI descriptors, digest calculation, and remotes ref keys.

Risks: only manifest media types are converted, not manifest lists; malformed or missing blobs return errors. JSON indentation changes the digest by design. Existing labels are replaced with generated GC refs.

Test signals: `converter_fuzz_test.go` fuzzes descriptor/content-store inputs for panic resistance; deterministic conversion assertions are outside this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/converter.go -->
