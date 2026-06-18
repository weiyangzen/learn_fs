## sources/control-plane/rook/cmd/rook/userfacing/userfacing.go

Purpose: centralizes baseline behavior for supported user-facing Rook CLI commands.

Important APIs and functions: `Commands` currently contains `multus.Cmd`. init iterates commands and ensures they are visible, have signal-aware context setup, configure logging, validate args, stop signal capture after execution, and initialize help command/flag.

Control flow: each command gets a `PersistentPreRunE` that creates a context canceled by Ctrl-C or SIGTERM, stores its cancel function in package-global `stopSignalCapture`, calls `rook.SetLogLevel()`, and returns `cmd.ValidateArgs(args)`. `PersistentPostRun` cancels signal capture if set.

State and persistence: no external persistence, but uses package-global cancel state. It mutates command definitions at init time.

Dependencies and integration points: bridges user-facing commands with shared root logging and graceful cancellation. It relies on Cobra pre/post-run semantics; child commands that define their own persistent pre/post runs could override this behavior. Risks: a single global `stopSignalCapture` assumes one command execution per process; `cmd.ValidateArgs()` in pre-run can be redundant with Cobra's normal args validation and may have subtle interactions. No direct tests are present.
