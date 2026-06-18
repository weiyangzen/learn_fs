
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/node/node.go

- Purpose: defines the `node` command namespace.
- Important APIs: exported `NewCmd`.
- Control flow/state: creates a no-arg Cobra command and registers `list`, `set-alias`, `delete`, and `ping`.
- Dependencies/integration: imported by root command; actual behavior is implemented in sibling files and `ctl/pkg/ctl/node`.
- Risks/tests: command-tree integration only. No direct tests observed.
