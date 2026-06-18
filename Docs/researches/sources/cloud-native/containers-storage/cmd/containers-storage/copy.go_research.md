<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/copy.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/copy.go

- Purpose: Copies file content between host paths and mounted storage objects.
- Important behavior: Parses chown options and calls storage copy helpers to place or retrieve files/directories.
- Control flow: Validate arguments, parse ownership override, open source/destination, and delegate to storage/archive copy logic.
- State and persistence: Mutates layer/container mounted content or host filesystem destinations depending on direction.
- Dependencies and integration: Uses storage mount/copy APIs and CLI flags.
- Risks: Ownership and path handling are security-sensitive; copying into mounted layers can alter container state.
- Test signals: Integration tests validating copied content and ownership.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/copy.go -->
