# sources/cloud-native/moby/daemon/logger/journald/journald.go

Purpose: Linux journald logging driver implementation for writing container logs to the systemd journal.

Important APIs/types/functions: `New`, `newJournald`, `validateLogOpt`, `Log`, `Name`, `Close`, and `sanitizeKeyMod`. The `journald` struct stores an epoch, atomic ordinal, fixed journal vars, closed channel, and test hooks.

Control flow/state/persistence: construction verifies journald availability, parses log tag, generates an epoch, builds fields for container ID/name/tag/image, and merges sanitized extra labels/env. `Log` copies base vars per message, attaches timestamp and partial-log metadata, increments ordinal, and sends to journald at stderr/info priority. On success it returns the message to the pool. `Close` closes the channel and optionally waits until read-capable builds can see the last ordinal.

Dependencies/integration: depends on `coreos/go-systemd/journal`, `logger.Info`, `loggerutils.ParseLogTag`, and optional `read.go` wait hook. Registered as `journald` by `register.go`.

Risks: field-name sanitization can collapse distinct labels/env vars. `Close` is not guarded against double close. Read synchronization only exists under the narrower cgo journald build.

Test signals: `journald_test.go` covers key sanitization; read tests cover end-to-end writes when fake journal support is available.
