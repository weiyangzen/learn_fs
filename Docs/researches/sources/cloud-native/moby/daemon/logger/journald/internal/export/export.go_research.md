# sources/cloud-native/moby/daemon/logger/journald/internal/export/export.go

Purpose: serializes fields in systemd Journal Export Format for journald tests and fake journal creation.

Important APIs/types/functions: `WriteField` writes either direct `VARIABLE=value\n` form or binary-safe form with variable name, newline, little-endian uint64 length, raw value, newline. `WriteEndOfEntry` writes the blank line terminating an entry. `isSerializableAsIs` rejects values containing newline or non-printable ASCII.

Control flow/state/persistence: stateless writer helpers encode one field at a time. The output is consumed by `systemd-journal-remote` in the fake sender.

Dependencies/integration: standard `encoding/binary`, `io`, and `strings`; used by `journald/internal/fake`.

Risks: no variable-name validation is done here; callers must validate names. Incorrect binary length or missing entry terminator makes `systemd-journal-remote` reject or drop entries.

Test signals: `export_test.go` compares serialization against a golden file, including binary-safe paths.
