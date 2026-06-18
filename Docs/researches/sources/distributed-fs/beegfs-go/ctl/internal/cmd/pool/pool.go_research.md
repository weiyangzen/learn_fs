
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/pool/pool.go

- Purpose: defines the `pool` command namespace.
- Important APIs: exported `NewCmd`.
- Control flow/state: creates a no-arg Cobra command and registers list, set-alias, create, assign, and delete.
- Dependencies/integration: imported by root command and quota command for list-defaults behavior.
- Risks/tests: command-tree integration only. No direct tests observed.
