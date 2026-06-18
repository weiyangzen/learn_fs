<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/exists.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/exists.go

- Purpose: Tests whether a layer, image, container, or generic object exists.
- Important behavior: Dispatches by requested object type and uses store `Exists`/lookup APIs.
- Control flow and state: Read-only, returning success/failure via exit status and optional output.
- Dependencies and integration: Used by scripts to gate create/delete flows.
- Risks: Ambiguous names across object namespaces require explicit type to avoid confusion.
- Test signals: CLI exit status after object creation/deletion.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/exists.go -->
