<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/metadata.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/metadata.go

- Purpose: Gets or sets metadata strings for layers, images, or containers.
- Important functions: `metadata` and `setMetadata`; `metadataQuiet` controls output.
- Control flow: Resolve object type/name, call corresponding metadata getter/setter, and print value or JSON/human response.
- State and persistence: `setMetadata` mutates metadata in the relevant store JSON.
- Dependencies and integration: Uses storage metadata APIs shared across object types.
- Risks: Metadata is opaque caller data; replacing it can break higher-level tools.
- Test signals: Round-trip get/set CLI tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/metadata.go -->
