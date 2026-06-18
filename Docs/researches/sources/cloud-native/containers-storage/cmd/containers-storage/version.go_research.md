<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/version.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/version.go

- Purpose: Prints containers-storage version/build information.
- Important behavior: `version` command emits version data in human or JSON form.
- Control flow and state: Read-only.
- Dependencies and integration: Uses module/version variables from the storage package/build.
- Risks: Missing linker/build metadata can produce incomplete version output.
- Test signals: CLI version smoke tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/version.go -->
