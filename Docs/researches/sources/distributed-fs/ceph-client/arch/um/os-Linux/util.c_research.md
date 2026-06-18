# sources/distributed-fs/ceph-client/arch/um/os-Linux/util.c

## Purpose
Provides miscellaneous host utility functions for stacks, terminals, host identity, random bytes, helper signal defaults, core dumping, early printing, and boot info/warning output.

## Important APIs, Types, and Functions
`stack_protections()`, `raw()`, `setup_machinename()`, `setup_hostinfo()`, `os_getrandom()`, `os_fix_helper_signals()`, `os_dump_core()`, `um_early_printk()`, `quiet_cmd_param()`, `os_info()`, and `os_warn()` are the main APIs. `uml_abort()` avoids glibc abort behavior that is unsafe for UML kernel threads.

## Control Flow, State, and Persistence
Persistent state is `quiet_info`, set by the `quiet` UML setup option. `os_dump_core()` resets SIGSEGV, terminates the process group, tries to kill ptraced children, then self-aborts.

## Dependencies and Integration Points
Used throughout boot, panic, helper, console, and architecture setup paths. Depends on host `uname`, termios, signals, getrandom, waitpid, and kernel `vscnprintf` for small-stack-safe formatting.

## Risks and Test Signals
Risks include process-group overkill during core dump, stack-protection mprotect failures, terminal raw-mode partial application, and quiet suppressing needed diagnostics. Test panic/core dump, helper signal behavior, `quiet`, host info in `/proc/cpuinfo`, and terminal setup.
