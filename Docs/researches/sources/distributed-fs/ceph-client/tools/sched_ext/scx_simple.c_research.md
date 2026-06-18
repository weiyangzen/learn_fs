# sources/distributed-fs/ceph-client/tools/sched_ext/scx_simple.c

Purpose: userspace control program for `scx_simple.bpf.c`, with options for FIFO mode and libbpf verbosity.

Important APIs, types, and functions: uses generated `scx_simple.bpf.skel.h`, `SCX_OPS_*` macros, `UEI_REPORT`, `bpf_map_lookup_elem()`, and `libbpf_num_possible_cpus()`. `read_stats()` aggregates the two-entry per-CPU `stats` map across all possible CPUs.

Control flow: `main()` configures libbpf logging and signal handlers, opens the skeleton, parses `-f`, `-v`, and `-h`, sets `skel->rodata->fifo_sched` for FIFO mode before load, loads and attaches struct_ops, then prints `local` and `global` aggregate queue counts once per second until signal or UEI exit. It destroys the link and skeleton and restarts on `UEI_ECODE_RESTART()`.

State and persistence: userspace state is only process-local. The scheduler mode is fixed by BPF rodata before load and cannot be changed after attach. Stats are read from BPF map state and reset with a new BPF object instance.

Dependencies and integration points: depends on libbpf, sched_ext userspace helpers, the generated skeleton, and matching BPF map layout. Requires enough privilege and kernel support for sched_ext.

Risks: `read_stats()` uses a VLA sized by possible CPUs, which is convenient but stack-sensitive on very large CPU counts. Failed map lookups are silently skipped, potentially under-reporting stats. The signal handler name argument is unused and misleadingly named `simple`.

Test signals: `-f` should flip BPF rodata and produce FIFO scheduling; without `-f` vtime mode should load. Queue counters should grow under runnable workloads. Attach/load failures or UEI reports identify kernel-side issues.
