<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/load.go -->
# sources/cloud-native/moby/internal/testutil/specialimage/load.go

Purpose: declares `SpecialImageFunc`, the common function signature for special image layout generators. It lets tests parameterize image fixture creation by passing a target directory and receiving an OCI index. Control flow and state are absent in this type-only file. Dependencies are OCI image-spec types. Risks are minimal; its value is API consistency across the specialimage package. Test signal is compile-time integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/load.go -->
