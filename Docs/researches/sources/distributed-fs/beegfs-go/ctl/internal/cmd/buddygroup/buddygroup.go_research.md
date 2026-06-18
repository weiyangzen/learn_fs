# sources/distributed-fs/beegfs-go/ctl/internal/cmd/buddygroup/buddygroup.go

Purpose: defines the top-level `beegfs mirror` command for mirroring and buddy group management.

Important API is `NewCmd() *cobra.Command`. It creates a cobra command with `Use: "mirror"`, short and long descriptions, no positional arguments, and attaches subcommands.

Control flow: construction is declarative. It calls `cmd.AddCommand` with list, create, automatic create, set-alias, delete, mirror-root-inode, and resync command groups. Actual behavior lives in sibling files and the `resync` subpackage.

State and persistence: this file creates no persistent state directly. Subcommands may query or mutate BeeGFS buddy groups and mirroring configuration.

Dependencies are cobra and `ctl/internal/cmd/buddygroup/resync`.

Integration points are the CTL command tree and all buddy-group subcommands. The user-facing command name is `mirror`, not `buddygroup`, which is important for documentation and compatibility.

Risks: this file is only an aggregator, so missing an added subcommand here would hide functionality. `Args: cobra.NoArgs` applies to the top-level command but subcommands define their own args.

Test signals: no direct tests in this subset.
