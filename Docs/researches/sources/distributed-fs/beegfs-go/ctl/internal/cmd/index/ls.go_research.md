
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/index/ls.go

- Purpose: implements `index ls` by invoking Hive Index `bee ls`.
- Important APIs: `newGenericLsCmd`, `newLsCmd`, and `runPythonLsIndex`.
- Control flow/state: defaults paths to cwd, validates Hive Index installation, translates many GNU-ls-like flags, appends output format when requested, and execs the external binary.
- Dependencies/integration: uses `bflag`, Viper output config, and `os/exec`; hidden `in-memory-name` and custom help flag maintain compatibility.
- Risks/tests: ordering of paths before wrapped flags may matter for external parsing; direct tests are absent.
