
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/index/index.go

- Purpose: defines the `index` command namespace for BeeGFS Hive Index operations.
- Important APIs: exported `NewCmd`.
- Control flow/state: builds no-arg Cobra command and registers `create`, `ls`, `find`, `stat`, `stats`, `query`, and `rescan`; database upgrade is not registered.
- Dependencies/integration: imported by root command; behavior delegated to sibling wrappers and external Hive Index tools.
- Risks/tests: namespace depends on external package presence for most subcommands. No direct tests observed.
