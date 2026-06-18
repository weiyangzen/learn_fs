# sources/distributed-fs/ceph-client/tools/lib/subcmd/exec-cmd.c

Purpose: Manages subcommand executable path configuration and provides wrappers to execute external subcommands through a configured main executable name.

Important APIs/types/functions: `exec_cmd_init()` initializes `subcmd_config` and `PREFIX`. `system_path()`, `extract_argv0_path()`, `set_argv_exec_path()`, `get_argv_exec_path()`, and `setup_path()` resolve and export executable search paths. `execv_cmd()` and `execl_cmd()` execute the configured command with added argv[0].

Control flow: Initialization stores config and environment. Path resolution prefers explicit `argv_exec_path`, then the configured environment variable, then `prefix/exec_path`. `setup_path()` prepends the exec path and the path of `argv0` to `PATH`. Execution builds a new argv where element 0 is `subcmd_config.exec_name`, then calls `execvp()`.

State and persistence: Static `argv_exec_path` and `argv0_path` persist for the process; environment variables `PREFIX`, `PATH`, and configured exec-path env are mutated.

Dependencies/integration: Depends on `subcmd-config.h`, `subcmd-util.h`, `linux/string.h` for `strlcpy`, and POSIX `getcwd`, `stat`, `execvp`, `setenv`. Used by subcmd tools to locate built-in and external command helpers.

Risks: `prepare_exec_cmd()` does not check `malloc()` failure. `extract_argv0_path()` uses `strndup(argv0, slash - argv0)`, yielding an empty string for `/cmd` paths and storing static allocated memory never freed. `execl_cmd()` caps arguments at `MAX_ARGS` and returns an error if exceeded. Environment mutation affects all later child processes.

Test signals: Verify relative/absolute exec paths, `PWD` symlink preservation, PATH prepending, environment override precedence, `execl_cmd()` overflow, and failed `execvp()` return path.
