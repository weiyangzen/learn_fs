# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/cpupower.c

## Purpose
Provides the `cpupower` top-level executable: global option parsing, command dispatch, CPU mask setup, root checks, CPU capability discovery, version/help, and optional MSR module loading.

## Important APIs, Types, and Functions
Important globals are `cpupower_cpu_info`, `run_as_root`, `base_cpu`, `cpus_chosen`, `online_cpus`, and `offline_cpus`. The command table maps command names to functions from `builtin.h` and records whether root is required. Key functions are `print_help`, `print_man_page`, `cmd_help`, `print_version`, `handle_options`, and `main`.

## Control Flow, State, and Persistence
`main` allocates bitmasks sized by configured processors, strips global options, selects the subcommand, initializes locale, rewrites `cmd --help` into `help cmd`, finds `base_cpu` via `sched_getcpu`, populates CPU info, optionally `modprobe`s `msr` on x86_64 root runs, then dispatches the matching command after checking root requirements. It frees global bitmasks only after successful dispatch; unknown commands exit after printing help.

## Dependencies and Integration Points
Depends on all subcommand objects, helper bitmask and CPU info APIs, gettext package macros, `/proc/cpuinfo`, `/dev/cpu/*/msr`, and man pages named `cpupower[-subcommand]`.

## Risks and Test Signals
`handle_options` only recognizes global options before the command; later global-looking options belong to subcommands. `system("modprobe msr")` is a privileged side effect. Allocation failures for bitmasks are not checked before use. Test help/version flows, CPU list parsing including `all`, non-root root-required commands, systems without `/dev/cpu/*/msr`, and unknown command behavior.
