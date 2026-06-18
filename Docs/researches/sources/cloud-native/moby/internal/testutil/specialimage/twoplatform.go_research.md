<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/twoplatform.go -->
# sources/cloud-native/moby/internal/testutil/specialimage/twoplatform.go

Purpose: builds a known two-platform OCI image fixture for `linux/amd64` and `linux/arm64`. Important APIs are `TwoPlatform`, `FileInLayer`, `oneLayerPlatformManifest`, and `multiPlatformImage`. Control flow writes one file layer per platform, creates platform-specific configs/manifests, assigns descriptor platform fields, embeds them in a child index, then writes a top-level annotated index and `oci-layout`. State is a nested multi-platform OCI layout. Dependencies include containerd platform parsing, OCI specs, distribution references, digest helpers, and shared writers. Risks include nested index semantics and platform selection behavior. Test signal is high for deterministic multi-platform image load tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/twoplatform.go -->
