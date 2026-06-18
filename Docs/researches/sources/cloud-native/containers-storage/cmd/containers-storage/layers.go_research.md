<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/layers.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/layers.go

- Purpose: Lists logical layers and low-level storage-driver layers.
- Important functions: `storageLayers` and `layers`; flags include tree/quiet variants.
- Control flow: Enumerate store layers or driver-only layers, print IDs and metadata, optionally tree-format relationships.
- State and persistence: Read-only.
- Dependencies and integration: Uses storage layer enumeration, graph-driver layer listing, and `tree.go` formatting.
- Risks: Driver layer listing can reveal unaccounted internal layers that logical metadata does not know about.
- Test signals: CLI list after layer creation and tree formatting tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/layers.go -->
