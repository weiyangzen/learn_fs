# sources/cloud-native/moby/daemon/logger/journald/internal/export/export_test.go

Purpose: golden test for Journal Export Format serialization.

Important APIs/types/functions: `TestExportSerialization` writes multiple fields through `export.WriteField`, terminates the entry with `WriteEndOfEntry`, reads `testdata/export-serialization.golden`, and compares exact bytes.

Control flow/state/persistence: temporary in-memory buffer only. The test acts as a contract for byte-level export framing.

Dependencies/integration: uses `os.ReadFile`, `testing`, `bytes`, and `gotest.tools/assert`.

Risks: golden files can mask intent if not reviewed alongside the format spec. Exact byte comparison is correct here because downstream `systemd-journal-remote` is format-sensitive.

Test signals: directly validates normal and escaped field serialization and entry termination.
