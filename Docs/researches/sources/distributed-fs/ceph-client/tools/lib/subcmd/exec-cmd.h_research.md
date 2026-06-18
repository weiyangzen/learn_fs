# sources/distributed-fs/ceph-client/tools/lib/subcmd/exec-cmd.h

Purpose: Declares the public path setup and subcommand execution API implemented by `exec-cmd.c`.

Important APIs/types/functions: Exports `exec_cmd_init()`, `set_argv_exec_path()`, `extract_argv0_path()`, `setup_path()`, `execv_cmd()`, `execl_cmd()`, `get_argv_exec_path()`, and `system_path()`.

Control flow: Header-only declarations; callers initialize config, optionally extract argv0 path and override exec path, update `PATH`, then execute subcommands.

State and persistence: Documents ownership for `get_argv_exec_path()` and `system_path()` as malloc-returning APIs that callers must free. Other state lives in the implementation.

Dependencies/integration: Included by tools using libsubcmd. Guarded by `__SUBCMD_EXEC_CMD_H`.

Risks: Callers must respect NULL-terminated argv for `execv_cmd()` and free returned strings. The header does not enforce initialization before use.

Test signals: Compile tests should include the header from C and C++-like strict contexts where applicable; API tests should validate ownership and initialization ordering.
