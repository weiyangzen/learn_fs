<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/wipe.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/wipe.go

- Purpose: Removes all storage content through the CLI.
- Important behavior: Calls store wipe API and returns any error.
- Control flow and state: Destructive full-store operation.
- Dependencies and integration: Uses storage wipe implementation across layers/images/containers.
- Risks: Irreversible data loss; should be protected by operator intent and isolated roots in tests.
- Test signals: Store lists are empty after wipe and can be reused.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/wipe.go -->
