<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/labeled.go -->
# sources/cloud-native/moby/internal/testutil/specialimage/labeled.go

Purpose: creates a single-platform OCI image whose config carries caller-supplied labels. `Labeled` writes a config, manifest, legacy manifest, and index for the requested image reference. State is generated OCI layout files. Dependencies include containerd platform defaults, distribution references, OCI image config, and shared layer/blob helpers. Risks include label map ordering not affecting JSON semantics but potentially affecting byte-level digests; test signal validates label preservation through image load paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/labeled.go -->
