<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/multiplatform.go -->
# sources/cloud-native/moby/internal/testutil/specialimage/multiplatform.go

Purpose: creates a multi-platform image index from caller-provided platforms and image reference. `MultiPlatform` returns both the top-level index and the per-platform manifest descriptors. Control flow writes one simple layer/config/manifest per platform through shared helpers and wraps them in a tagged image index. State is a nested OCI index layout. Dependencies include containerd platform formatting/defaults, distribution references, OCI specs, and specialimage shared writers. Risks include platform descriptor accuracy and consumers selecting the correct manifest. Test signal is for multi-platform image load and platform matching.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/multiplatform.go -->
