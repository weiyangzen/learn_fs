<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/textplain.go -->
# sources/cloud-native/moby/internal/testutil/specialimage/textplain.go

Purpose: creates an OCI layout with a descriptor using `text/plain` content so tests can validate media-type filtering and rejection behavior. `TextPlain` writes a small text blob and references it from image metadata. State is a deliberately unusual layout under the target directory. Dependencies include strings, distribution references, OCI descriptors, and shared blob/index helpers. Risks are intentional incompatibility with normal image media types. Test signal targets loader validation for unsupported descriptor media types.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/textplain.go -->
