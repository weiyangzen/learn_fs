<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/configtarget.go -->
# sources/cloud-native/moby/internal/testutil/specialimage/configtarget.go

Purpose: builds an OCI image layout that targets an image configuration descriptor directly rather than a normal manifest. The exported `ConfigTarget` writes a config blob and creates an index referencing it with image annotations. State is the generated OCI layout under the provided directory. Dependencies are OCI image-spec descriptors, containerd platform defaults, distribution references, and shared specialimage blob helpers. Risks include intentionally unusual descriptor shape that may expose loader assumptions; test signal is for import/load paths handling config targets.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/configtarget.go -->
