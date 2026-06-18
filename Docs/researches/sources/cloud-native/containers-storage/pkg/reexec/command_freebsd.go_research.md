# sources/cloud-native/containers-storage/pkg/reexec/command_freebsd.go

Purpose: implements FreeBSD self-reexec command construction.

Important APIs, types, and functions: `Self`, `Command`, and `CommandContext`.

Control flow: `Self` uses `unix.SysctlArgs("kern.proc.pathname", -1)` and falls back to `os.Args[0]`. `Command` and `CommandContext` build exec commands targeting `Self()` and replace `cmd.Args` with the requested reexec args.

State and persistence: no persistence. It depends on current process path and command args.

Dependencies and integration points: depends on `context`, `os`, `os/exec`, and `x/sys/unix`. It is part of the `reexec` mechanism used by tests and subprocess isolation.

Risks and edge cases: unlike other platforms here, this file does not call `panicIfNotInitialized`, so FreeBSD behavior differs. Fallback to `os.Args[0]` may be relative or deleted.

Test signals: generic reexec tests exercise command behavior where platform support permits, but FreeBSD path lookup is not specifically tested.
