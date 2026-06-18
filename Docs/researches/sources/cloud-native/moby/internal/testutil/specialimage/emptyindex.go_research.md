<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/emptyindex.go -->
# sources/cloud-native/moby/internal/testutil/specialimage/emptyindex.go

Purpose: creates a valid-looking OCI layout with an empty index. `EmptyIndex` returns the written index after adding layout metadata. State is just `index.json` and `oci-layout` in the target directory. Dependencies are distribution references and OCI spec versioning. Risks are around whether consumers treat an empty index as malformed or simply empty. Test signal is for defensive image load/import validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/emptyindex.go -->
