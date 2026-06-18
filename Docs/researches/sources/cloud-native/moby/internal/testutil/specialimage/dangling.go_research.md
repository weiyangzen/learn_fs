<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/dangling.go -->
# sources/cloud-native/moby/internal/testutil/specialimage/dangling.go

Purpose: creates an OCI/docker-archive-style image without a normal repository tag so tests can exercise dangling image import behavior. The exported `Dangling` writes descriptors and legacy manifest metadata with empty or special tag state. State is the OCI layout and `manifest.json` content under the directory. Dependencies are filesystem/path operations and OCI specs. Risks are in exact legacy manifest semantics because image load behavior may change around dangling tags. Test signal targets image load/listing edge cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/dangling.go -->
