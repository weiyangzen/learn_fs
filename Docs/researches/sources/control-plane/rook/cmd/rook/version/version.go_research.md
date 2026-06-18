## sources/control-plane/rook/cmd/rook/version/version.go

Purpose: implements the `rook version` command that prints the Rook build version and Go runtime version.

Important APIs and functions: `VersionCmd` is a Cobra command with `Use: version`; its `RunE` prints `rook: <version.Version>` and `go: <runtime.Version()>`.

Control flow: no flags or arguments are declared. On execution it writes to stdout and returns nil. In `main.go`, the command is initially added with backend commands and hidden by the root command hiding loop unless separately exposed elsewhere.

State and persistence: no persistent state. It reads `github.com/rook/rook/pkg/version.Version` and Go runtime metadata.

Dependencies and integration points: useful for debugging image/build/runtime skew. Risks are low; the main subtlety is command visibility because `main.go` hides all commands added before user-facing commands. There are no direct tests in this subset.
