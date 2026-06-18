## sources/control-plane/rook/cmd/rook/userfacing/multus/multus.go

Purpose: defines the visible `rook multus` command grouping for tools that help users configure Multus or compatible multi-network providers for Rook.

Important APIs and functions: `Cmd` is the Cobra command with `Use: multus`; init attaches `validation.Cmd` as its subcommand. The long description points to the Kubernetes Network Plumbing Working Group multi-network spec.

Control flow: no runtime logic beyond command tree assembly. All execution is delegated to subcommands in the validation package and to shared user-facing command setup.

State and persistence: no local state. It depends on global Cobra command registration and the validation package.

Integration points: `cmd/rook/main.go` exposes this through `userfacing.Commands`, and `userfacing.go` wraps it with interrupt handling, logging setup, and help initialization. Risks are low, but adding more subcommands should account for the user-facing package's persistent pre/post run behavior. Test signals are absent; coverage depends on CLI/help tests or validation package tests.
