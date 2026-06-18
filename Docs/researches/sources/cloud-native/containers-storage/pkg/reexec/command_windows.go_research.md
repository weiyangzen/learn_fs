# sources/cloud-native/containers-storage/pkg/reexec/command_windows.go

Purpose: implements Windows self-reexec command construction.

Important APIs, types, and functions: `Self`, `Command`, and `CommandContext`.

Control flow: `Self` uses `naiveSelf`. Command constructors require `Init`, create commands for `Self()`, and set `cmd.Args` to the requested reexec argv.

State and persistence: no persistence. Depends on the current executable path.

Dependencies and integration points: depends on `context` and `os/exec`; uses common registration/init logic.

Risks and edge cases: deleted or moved binaries can break reexec. The comment for `CommandContext` repeats "Command", but behavior is context-aware. Initialization must run before use.

Test signals: generic reexec tests exercise command construction and context cancellation where platform support permits.
