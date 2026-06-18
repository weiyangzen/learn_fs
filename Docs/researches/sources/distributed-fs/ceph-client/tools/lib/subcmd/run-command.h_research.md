# sources/distributed-fs/ceph-client/tools/lib/subcmd/run-command.h

Purpose: Declares child process execution data structures, error codes, option flags, and APIs for libsubcmd.

Important APIs/types/functions: Error enum values start at `ERR_RUN_COMMAND_FORK`; `IS_RUN_COMMAND_ERR()` identifies normalized library errors. `struct child_process` describes argv, pid, FDs, dir, env, finish status, behavior bitfields, preexec callback, and no-exec callback. Declares run/start/finish/check APIs plus `RUN_COMMAND_*` flags.

Control flow: Callers zero-initialize `struct child_process`, fill fields, call `start_command()` then manage returned FDs and `finish_command()`, or use `run_command()`/`run_command_v_opt()` for synchronous execution.

State and persistence: State is caller-owned in `struct child_process`; implementation updates fields.

Dependencies/integration: Includes `<unistd.h>` for `pid_t` and POSIX types. Used by pager and other tools.

Risks: FD semantics require careful caller cleanup after `start_command()`. Bitfields encode booleans but do not validate incompatible combinations. Header comments are the primary ownership contract.

Test signals: Compile and exercise all documented FD modes through `run-command.c` tests.
