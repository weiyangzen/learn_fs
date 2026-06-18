<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/partial.go -->
# sources/cloud-native/moby/internal/testutil/specialimage/partial.go

Purpose: creates a multi-platform index where some referenced platform manifests are intentionally missing from storage. Important APIs are `PartialOpts` and `PartialMultiPlatform`. Control flow writes real manifests for `Stored` platforms, constructs fake descriptors with deterministic digests for `Missing` platforms, then wraps all descriptors in a multi-platform image. State is a deliberately incomplete OCI layout. Dependencies include platform formatting, OCI specs, digest generation, and shared manifest writers. Risks are intentional: missing blobs must remain missing to test partial-load behavior. Test signal targets import validation, lazy platform selection, and missing-content error paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/partial.go -->
