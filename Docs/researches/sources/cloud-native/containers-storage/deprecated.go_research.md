<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/deprecated.go -->
# sources/cloud-native/containers-storage/deprecated.go

- Purpose: Preserves deprecated interface names for compatibility with older consumers.
- Important types: `ROFileBasedStore`, `RWFileBasedStore`, `FileBasedStore`, `ROMetadataStore`, `RWMetadataStore`, `MetadataStore`, big-data store aliases, `FlaggableStore`, `ContainerStore`, `ROImageStore`, `ImageStore`, `ROLayerStore`, and `LayerStore`.
- Control flow and state: Pure type/interface declarations; no runtime behavior.
- Dependencies and integration: Re-exports or composes current internal interfaces so downstream packages can continue compiling.
- Risks: Deprecated interfaces can freeze old API shape and complicate refactoring; removal would be breaking.
- Test signals: Downstream compile compatibility and package API checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/deprecated.go -->
