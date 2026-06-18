# sources/cloud-native/containers-storage/pkg/reexec/command_unsupported.go

Purpose: provides unsupported stubs for reexec command construction.

Important APIs, types, and functions: `Command` and `CommandContext`.

Control flow: both call `panicIfNotInitialized` and then return nil. If initialized, the nil return indicates unsupported operation without an explicit panic.

State and persistence: no state or persistence.

Dependencies and integration points: depends on `context` and `os/exec`; selected outside Linux, Windows, FreeBSD, Solaris, and Darwin.

Risks and edge cases: returning nil after successful initialization can lead to nil pointer panics in callers expecting a command. Callers should platform-guard reexec usage.

Test signals: no unsupported-platform tests in the requested set.
