# sources/cloud-native/containers-storage/pkg/reexec/command_linux.go

Purpose: implements Linux self-reexec command construction using `/proc/self/exe`.

Important APIs, types, and functions: `Self`, `Command`, and `CommandContext`.

Control flow: `Self` returns `/proc/self/exe`. Command constructors first require `Init` to have been called, create an `exec.Cmd` or context-aware command for `/proc/self/exe`, and set `cmd.Args` to the requested child argv.

State and persistence: no persistence. Uses the kernel's live executable reference, so it remains valid if the on-disk binary is replaced.

Dependencies and integration points: depends on `context` and `os/exec`. Used by lockfile tests and any package that registers reexec initializers.

Risks and edge cases: panics if `reexec.Init` was not called in main. `/proc` must be mounted and accessible.

Test signals: `reexec_test.go` covers `Command` and `CommandContext` on supported platforms.
