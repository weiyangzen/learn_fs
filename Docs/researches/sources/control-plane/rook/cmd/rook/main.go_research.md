## sources/control-plane/rook/cmd/rook/main.go

Purpose: entry point for the `rook` binary. It assembles root-level command groups, hides backend/operator commands from normal users, adds user-facing commands, and executes `rook.RootCmd`.

Important APIs and functions: `main()` calls `addCommands()` and then `rook.RootCmd.Execute()`. `addCommands()` registers version, discovery, key management, Ceph backend, and utility commands, marks all currently registered root commands hidden, then adds `userfacing.Commands`.

Control flow: backend commands are added first and then hidden as a second line of defense. User-facing commands are added after this hiding loop so their own package can make them visible and attach signal/logging behavior. Execution errors are printed to stdout with a formatted `rook error` message rather than fatal termination.

State and persistence: no persistent state; this file mutates the global Cobra command tree at process startup. Dependencies include command packages whose init functions also register flags/subcommands.

Integration points: this is the boundary between operator-internal CLI surfaces and supported user commands. Ordering matters: if a future user-facing command is added before the hide loop, it may be hidden unintentionally; if a backend command is added after the loop, it may be exposed unless explicitly hidden. Test signals are not present here. Risks include global Cobra state interactions and silent continuation after `Execute()` returns an error because `main()` does not call `os.Exit(1)`.
