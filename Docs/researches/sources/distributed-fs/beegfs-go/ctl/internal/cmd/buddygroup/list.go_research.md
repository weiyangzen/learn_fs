
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/buddygroup/list.go

- Purpose: lists BeeGFS metadata or storage buddy groups for `mirror list`.
- Important APIs: `list_Config`, `newListCmd`, and `runListCmd`.
- Control flow/state: fetches all buddy groups with `buddygroup.GetBuddyGroups`, filters by optional node type, formats primary/secondary target IDs differently in debug mode, and prints a table.
- Dependencies/integration: uses `cmdfmt.Printomatic`, Viper `config.DebugKey`, BeeGFS entity formatting, and `ctl/pkg/ctl/buddygroup`.
- Risks/tests: output correctness depends on backend returning complete target mapping; debug and non-debug fields have separate formatting paths. No direct tests in this subset.
