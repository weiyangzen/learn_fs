
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/buddygroup/resync/resync.go

- Purpose: creates the `mirror resync` command namespace.
- Important APIs: exported `NewResyncCmd`.
- Control flow/state: registers `stats`, `start`, and `restart` subcommands and performs no direct state mutation.
- Dependencies/integration: plugs the resync namespace into `buddygroup.NewCmd`; all work is delegated to sibling command files.
- Risks/tests: low logic risk; coverage is mainly command-tree integration. No direct tests observed.
