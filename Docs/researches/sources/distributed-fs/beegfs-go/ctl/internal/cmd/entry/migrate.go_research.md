
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/entry/migrate.go

- Purpose: implements `entry migrate` for moving file data away from source targets/nodes/pools to destination pools/targets/groups.
- Important APIs: `migrateCfg`, `newMigrateCmd`, and `migrateRunner`.
- Control flow/state: enforces path args and recursive `--yes`, builds `entry.MigrateCfg`, chooses path input method, streams migration results, updates `MigrateStats`, prints verbose/error rows, and returns partial success for per-entry failures.
- Dependencies/integration: uses BeeGFS entity flags, filesystem filters, background rebalancing version constants, `entry.MigrateEntries`, and CTL partial-success errors.
- Risks/tests: migration has high consistency risk, especially temp-file mode on live writable trees; recursive operations are gated but stdin bulk input is not separately confirmed. No direct tests observed.
