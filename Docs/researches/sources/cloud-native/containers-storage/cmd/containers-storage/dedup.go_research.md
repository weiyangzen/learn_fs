<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/dedup.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/dedup.go

- Purpose: CLI command for deduplicating storage content where the driver supports it.
- Important behavior: Accepts hash method selection, invokes store deduplication, and reports reclaimed/processed results.
- Control flow and state: Mutates storage driver backing files through dedup operations.
- Dependencies and integration: Depends on graph-driver support and the selected hash method, defaulting to CRC.
- Risks: Deduplication is filesystem/driver-sensitive and can be expensive.
- Test signals: Driver integration tests and reported dedup statistics.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/dedup.go -->
