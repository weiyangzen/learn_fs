
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/index/rescan.go

- Purpose: implements `index rescan <directory-path>` for refreshing an indexed subtree.
- Important APIs: `newGenericRescanCmd`, `newRescanCmd`, and `runPythonRescanIndex`.
- Control flow/state: defaults to cwd, validates package/config, wraps rescan flags, runs `bee rescan` for non-recursive mode or tree-summary/rescan-related external flow for recursive mode as implemented in the runner.
- Dependencies/integration: uses `bflag`, global worker/debug flags, and external Hive Index rescan tools.
- Risks/tests: persistent index updates and stale-entry deletion are delegated externally; recursive behavior can update broad database state. No direct tests observed.
