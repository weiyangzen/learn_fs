# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/builtin.h

## Purpose
Declares the subcommand entry points linked into the `cpupower` command dispatcher.

## Important APIs, Types, and Functions
Exports prototypes for `cmd_set`, `cmd_info`, `cmd_freq_set`, `cmd_freq_info`, `cmd_idle_set`, `cmd_idle_info`, `cmd_cap_info`, `cmd_cap_set`, and `cmd_monitor`. Each follows the `argc, argv` command-main convention expected by `utils/cpupower.c`.

## Control Flow, State, and Persistence
The file carries no state. Its control role is compile-time coupling: adding or removing a subcommand requires keeping this header, the concrete command source, and the `commands[]` dispatch table synchronized.

## Dependencies and Integration Points
Integrated by `cpupower.c` and implemented across `cpufreq-*`, `cpuidle-*`, `cpupower-*`, `powercap-info.c`, and `idle_monitor/cpupower-monitor.c`.

## Risks and Test Signals
Several implementation files define parameters as `char **argv` while this header declares `const char **argv`, which relies on permissive C compilation and can produce warnings. Build tests should compile the full utility with strict warnings and invoke `cpupower help` to confirm command table/prototype coverage.
