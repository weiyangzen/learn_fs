# sources/distributed-fs/beegfs-go/ctl/internal/cmd/rst/rst.go

Purpose: defines the top-level Remote Storage Target command group.

Important APIs/types/functions: `NewRSTCmd` constructs the `remote` command with aliases `remote-storage-target` and `rst`.

Control flow: the command accepts no args and registers subcommands from this package: push, pull, job, list, and status.

State and persistence: no state itself; it is the integration point for subcommands that query or mutate Remote jobs/configuration.

Dependencies and integration points: depends only on Cobra and package-local command constructors.

Risks: command discoverability and alias stability affect scripts. Adding a new RST subcommand requires wiring it here.

Test signals: no direct tests. A basic command-tree test could verify aliases, arg rejection, and registered subcommands.
