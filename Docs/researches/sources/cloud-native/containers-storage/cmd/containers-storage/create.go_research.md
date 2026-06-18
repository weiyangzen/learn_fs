<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/create.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/create.go

- Purpose: Implements creation/import commands for storage-driver layers, logical layers, images, and containers.
- Important functions: `paramIDMapping`, `createStorageLayer`, `createLayer`, `importLayer`, `createImage`, and `createContainer`.
- Control flow: Parse ID/name/read-only/mount label/idmap/subuid/subgid flags, optionally read metadata from file, create or import layers, create images from top layers, and create containers from images.
- State and persistence: Mutates storage by adding driver layers, layer metadata, image records, container records, id mappings, metadata, and volatile flags.
- Dependencies and integration: Uses storage `Create*`, `ApplyDiff`, ID mapping options, and common command registration.
- Risks: ID/name collisions and overlapping ID maps must be rejected; importing diffs from stdin/files can ingest untrusted archives.
- Test signals: CLI integration tests and storage library create/import tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/create.go -->
