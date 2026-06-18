
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/index/find.go

- Purpose: implements `index find` by adapting many find-like flags to Hive Index `bee find`.
- Important APIs: `newGenericFindCmd`, `newFindCmd`, and `runPythonFindIndex`.
- Control flow/state: defaults path to current working directory, checks Hive Index installation/config, appends paths and wrapped predicate/action flags, adds output format `-Q` when non-table output is configured, then execs the Python binary.
- Dependencies/integration: uses `bflag`, Viper output config, and `os/exec`; annotated as allowed for all users.
- Risks/tests: large user-provided flag surface has little local validation; SQL/index semantics live in external tool. No direct tests found.
