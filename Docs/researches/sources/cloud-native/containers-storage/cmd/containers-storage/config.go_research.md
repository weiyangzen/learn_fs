<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/config.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/config.go

- Purpose: CLI command that prints effective storage configuration.
- Important behavior: Reads store/options information and emits human or JSON output.
- Control flow and state: No mutation beyond normal store initialization.
- Dependencies and integration: Uses common CLI flag parsing and storage options/defaults.
- Risks: Output can expose host paths and graph driver options.
- Test signals: CLI smoke tests comparing effective config.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/config.go -->
