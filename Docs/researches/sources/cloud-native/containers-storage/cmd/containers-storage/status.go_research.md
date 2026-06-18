<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/status.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/status.go

- Purpose: Prints storage driver/store status.
- Important behavior: Calls status APIs and emits key/value or JSON output.
- Control flow and state: Read-only command registered as `status`.
- Dependencies and integration: Relies on graph-driver status support.
- Risks: Output shape is driver-specific; scripts need defensive parsing.
- Test signals: CLI status returns successfully for configured drivers.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/status.go -->
