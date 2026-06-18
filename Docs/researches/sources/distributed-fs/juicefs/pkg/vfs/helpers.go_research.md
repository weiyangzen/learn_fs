# sources/distributed-fs/juicefs/pkg/vfs/helpers.go

Purpose: contains small VFS formatting and context helpers used by logging, tests, and diagnostics.

Important APIs and types: mode permission constants, `strerr`, `typestr`, `smode.String`, `Entry.String`, `LogContext`, `logContext`, and `NewLogContext`.

Control flow and state: `strerr` maps errno 0 to `"OK"` and otherwise uses the errno error string. `smode.String` builds Unix file-mode text including file type, rwx bits, and suid/sgid/sticky uppercase/lowercase semantics. `Entry.String` lazily formats meta entry inode plus selected attributes. `NewLogContext` wraps a `meta.Context` with a start timestamp so `Duration` reports elapsed operation time.

Persistence and integration: no persistence. Used by access logging, tests, and VFS log output.

Risks and test signals: formatting is exact-string-sensitive and must match Unix mode conventions. `helpers_test.go` covers mode strings, entry formatting, and errno string conversion.
