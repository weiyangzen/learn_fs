<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-kallsyms.c -->
# sources/distributed-fs/ceph-client/tools/perf/builtin-kallsyms.c

## Purpose
Implements `perf kallsyms`, a small command that searches the running kernel and loaded modules for named symbols and prints their mapped and original address ranges.

## Important APIs, Types, and Functions
The entry point is `cmd_kallsyms()`. `__cmd_kallsyms()` initializes a `perf_env`, records the command line into that env, creates a kernel-symbol `machine` with `machine__new_kallsyms()`, then resolves each requested symbol through `machine__find_kernel_symbol_by_name()`. For successful hits it uses `map__dso()`, `dso__short_name()`, `dso__long_name()`, and `map__unmap_ip()` to print module/DSO names and address ranges.

## Control Flow
`cmd_kallsyms()` parses only `-v/--verbose`, requires at least one symbol name, enables `symbol_conf.try_vmlinux_path` when no explicit vmlinux was supplied, initializes symbols, and delegates to `__cmd_kallsyms()`. The helper creates the kallsyms-backed machine, loops over input names, prints either `<name>: not found` or a formatted symbol line, then deletes the machine and exits the perf environment.

## State and Persistence Behavior
State is local to one process invocation. The command reads `/proc/kallsyms` and optional vmlinux/module symbol data through perf symbol infrastructure, but writes no persistent output. `perf_env__set_cmdline()` stores the searched symbol names in the temporary environment object.

## Dependencies and Integration Points
Depends on perf symbol, machine, map, DSO, env, debug, and parse-options infrastructure. It integrates with the live host kernel symbol source and global `symbol_conf`, especially vmlinux path selection and verbosity.

## Risks and Edge Cases
The command requires access to `/proc/kallsyms`; kernel pointer restrictions or permissions can reduce symbol fidelity. A failure to create the machine returns a generic `-1`. Symbols are looked up by exact name and duplicate names resolve according to machine symbol lookup behavior. Output includes both unmapped and raw symbol addresses, so users need to understand module address translation.

## Test Signals
Test known kernel symbols, known module symbols, unknown names, restricted `/proc/kallsyms` environments, explicit and implicit vmlinux path behavior, and verbose mode. Cleanup signals are no leaked machine/env objects and correct nonzero return on initialization failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-kallsyms.c -->
