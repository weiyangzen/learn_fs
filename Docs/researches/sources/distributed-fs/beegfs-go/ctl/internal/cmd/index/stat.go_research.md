
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/index/stat.go

- Purpose: implements `index stat` by invoking Hive Index `bee stat`.
- Important APIs: `newGenericStatCmd`, `newStatCmd`, and `runPythonStatIndex`.
- Control flow/state: chooses a single path argument or cwd, validates Hive Index config, appends wrapped stat flags and output format, then runs external binary with stdout/stderr inherited.
- Dependencies/integration: uses package-global `path`, `bflag`, Viper output config, and `os/exec`.
- Risks/tests: package-level mutable `path` may retain state across tests or reused command instances. No direct tests found.
