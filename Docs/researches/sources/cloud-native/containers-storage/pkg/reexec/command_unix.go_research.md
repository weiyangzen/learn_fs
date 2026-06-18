# sources/cloud-native/containers-storage/pkg/reexec/command_unix.go

Purpose: implements self-reexec command construction for Solaris and Darwin.

Important APIs, types, and functions: `Self`, `Command`, and `CommandContext`.

Control flow: `Self` delegates to `naiveSelf`, which resolves `os.Args[0]`. Command constructors require initialization, create commands for `Self()`, and set `cmd.Args` to the child argv.

State and persistence: no persistence. Relies on the current executable path being resolvable and still usable.

Dependencies and integration points: depends on `context` and `os/exec`; uses common `reexec.go` helpers.

Risks and edge cases: unlike Linux, a deleted or replaced on-disk binary can break reexec. Initialization panic protects callers from missing `Init`.

Test signals: generic reexec tests cover behavior on supported platforms; `naiveSelf` has direct test coverage.
