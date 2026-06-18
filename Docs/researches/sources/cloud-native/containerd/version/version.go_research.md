<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/version/version.go -->
# sources/cloud-native/containerd/version/version.go

- Purpose: Defines build-time version identity for containerd.
- Important variables/constants: `Name`, `Package`, `Version = "2.3.0+unknown"`, `Revision`, `GoVersion = runtime.Version()`, and `ConfigVersion = 4`.
- Control flow and state: Values are package globals overridden by linker flags in release builds; `GoVersion` is computed at initialization.
- Dependencies and integration: Imported by CLI/server version reporting and configuration handling. `ConfigVersion` is the maximum supported config version for main and plugin config migration.
- Risks: Default version is only a fallback; missing linker flags produce `+unknown`. Config version changes need matching migration support.
- Test signals: Version command output and config migration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/version/version.go -->
