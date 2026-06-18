# sources/cloud-native/moby/daemon/logger/journald/journald_test.go

Purpose: unit test for journald field-key sanitization.

Important APIs/types/functions: `TestSanitizeKeyMod` validates lower-to-upper conversion, invalid-character replacement with underscores, and leading underscore removal.

Control flow/state/persistence: table-style assertions only, no persistence.

Dependencies/integration: validates behavior used by `logger.Info.ExtraAttributes(sanitizeKeyMod)` in `newJournald`.

Risks: tests cover representative cases but not collision behavior when multiple raw keys sanitize to the same journal field.

Test signals: direct signal for journald metadata-key compatibility with systemd field rules.
