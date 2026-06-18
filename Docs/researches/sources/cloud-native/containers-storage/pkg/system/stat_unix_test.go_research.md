# sources/cloud-native/containers-storage/pkg/system/stat_unix_test.go

Purpose: shared Linux/FreeBSD stat conversion test.

Important APIs/types/functions: `TestFromStatT` uses `prepareFiles`, raw `syscall.Lstat`, `fromStatT`, and platform-specific assertions.

Control flow: creates a temp file, reads syscall stat data, converts it, compares UID/GID/Rdev, then calls `platformTestFromStatT`.

State/persistence: temporary filesystem state only.

Dependencies/integration: shares `prepareFiles` with utime tests and validates platform converters.

Risks: covers Linux and FreeBSD only; other Unix converters rely mainly on compile coverage unless separate tests exist.

Test signals: catches accidental field mixups in common ownership/device metadata.
