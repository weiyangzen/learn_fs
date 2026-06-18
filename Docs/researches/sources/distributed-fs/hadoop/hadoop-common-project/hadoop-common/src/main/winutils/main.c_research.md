# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/main.c

Purpose: top-level Unicode entry point for `winutils.exe`, dispatching subcommands and installing an unhandled structured-exception handler.

Important APIs/functions: `wmain` selects `ls`, `chmod`, `chown`, `groups`, `hardlink`, `symlink`, `readlink`, `task`, `systeminfo`, `service`, or `help`; `WinutilsSehUnhandled` logs and exits on unhandled SEH exceptions; `Usage` aggregates subcommand usage text.

Control flow: arguments with fewer than two elements print usage and fail. Recognized subcommands call their implementation with `argc - 1` and `argv + 1`, so each command sees its own name at `argv[0]`. `help` returns success; unknown commands return failure after printing usage.

State and persistence: no durable state is changed directly, but it installs a process-wide exception filter and can route into commands that mutate files, jobs, services, or security descriptors.

Dependencies/integration: includes `winutils.h` and assumes all command usage/entry functions are linked. It is the shared contract used by Hadoop Java code and tests invoking `winutils`.

Risks and test signals: dispatch depends on exact wide-string command names. Tests should confirm exit codes for no args, help, unknown commands, and that each subcommand receives argv layout expected by its parser.
