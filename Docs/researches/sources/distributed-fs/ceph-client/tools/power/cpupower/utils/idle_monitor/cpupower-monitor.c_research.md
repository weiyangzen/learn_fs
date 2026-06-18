# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/idle_monitor/cpupower-monitor.c

## Purpose
Implements `cpupower monitor`, the framework that registers available idle/power monitors, measures over an interval or child command, and prints topology-organized tabular results.

## Important APIs, Types, and Functions
Important globals are `all_monitors`, selected `monitors`, `avail_monitors`, `cpu_count`, `mode`, `interval`, `cpu_top`, and `wake_cpus`. Key functions include `timespec_diff_us`, `print_header`, `print_results`, `parse_monitor_param`, `list_monitors`, `fork_it`, `do_interval_measure`, `cmdline`, and `cmd_monitor`.

## Control Flow, State, and Persistence
`cmd_monitor` parses monitor options, obtains topology, defaults CPU mask to all CPUs, calls every compiled monitor `do_register`, filters root-required monitors for non-root users, optionally lists or filters monitors, then starts/stops measurements around either a sleep interval or an execed child command. Results are printed by invoking each state callback. It releases topology and monitor resources at exit; state is in process memory and hardware counters only.

## Dependencies and Integration Points
Depends on `idle_monitors.def`, monitor plugin descriptors, topology APIs from libcpupower, bitmask globals, helper CPU info/root state, and POSIX fork/exec/wait/signal APIs.

## Risks and Test Signals
`-i` is declared as requiring an argument in behavior but option string uses `i:` only if present? Here `+lci:m:` makes `-i` require an argument, but errors rely on getopt. Header formatting has fixed widths and can truncate names. Child command monitoring ignores signal-exit reporting. Test list mode, monitor filtering order, non-root filtering, interval and command modes, offline CPUs, multi-package topology, and wake-cpu affinity behavior.
