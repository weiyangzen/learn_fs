
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/health/health.go

- Purpose: defines the `health` command namespace.
- Important APIs: exported `NewHealthCmd`.
- Control flow/state: creates a no-arg Cobra command and adds `check`, `network`, `capacity`, and `bundle` subcommands.
- Dependencies/integration: imported by root command and used by post-run quick-alert handling.
- Risks/tests: low logic risk; command-tree registration is the main behavior. No direct tests observed.
