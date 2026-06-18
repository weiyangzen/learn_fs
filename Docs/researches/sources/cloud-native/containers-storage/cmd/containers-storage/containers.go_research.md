<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/containers.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/containers.go

- Purpose: Lists known containers.
- Important behavior: Calls `m.Containers()`, emits JSON when requested, otherwise prints container IDs with names and big-data item names.
- Control flow and state: Read-only command registered as `containers`.
- Dependencies and integration: Uses the common `jsonOutput` flag and storage store enumeration.
- Risks: Human output omits some fields; scripts should use JSON.
- Test signals: CLI list output after container creation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/containers.go -->
