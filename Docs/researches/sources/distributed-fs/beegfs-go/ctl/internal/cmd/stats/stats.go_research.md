# sources/distributed-fs/beegfs-go/ctl/internal/cmd/stats/stats.go

Purpose: defines the top-level `stats` command group.

Important APIs/types/functions: `NewCmd` constructs the Cobra command and registers `server`, `client`, `user`, and `rebalance`.

Control flow: the command has no run logic of its own; subcommands own validation and execution.

State and persistence: no state. It exposes read-only statistics subcommands.

Dependencies and integration points: depends on Cobra and package-local command constructors.

Risks: new stats commands must be added here. Aliases or command names affect scripts.

Test signals: no direct tests. A command-tree test can verify registered children.
