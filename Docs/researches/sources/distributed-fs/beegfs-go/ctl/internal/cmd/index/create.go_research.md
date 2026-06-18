
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/index/create.go

- Purpose: implements `index create` by invoking the external Hive Index `bee index` command.
- Important APIs: `newGenericCreateCmd`, `newCreateCmd`, and `runPythonCreateIndex`.
- Control flow/state: performs package/config checks, gathers wrapped flags from `bflag`, prefixes `index`, starts the Python binary, wires stdout/stderr, and waits.
- Dependencies/integration: uses `os/exec`, CTL logger, `commonIndexFlags`, and Hive Index filesystem/database tools.
- Risks/tests: external process exit code is wrapped as an execution error but not propagated as exact exit status; correctness depends on installed package version. No local tests.
