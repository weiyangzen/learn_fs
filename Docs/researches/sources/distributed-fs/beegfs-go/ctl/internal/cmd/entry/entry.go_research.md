
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/entry/entry.go

- Purpose: defines the `entry` command namespace.
- Important APIs: exported `NewEntryCmd`.
- Control flow/state: creates a no-arg Cobra command and registers info, set, disposal, migrate, create, and refresh subcommands.
- Dependencies/integration: is imported by root command assembly in `root.go`; concrete behavior is in sibling files and `ctl/pkg/ctl/entry`.
- Risks/tests: command-tree integration only; no persistence or direct backend calls. No direct tests observed.
