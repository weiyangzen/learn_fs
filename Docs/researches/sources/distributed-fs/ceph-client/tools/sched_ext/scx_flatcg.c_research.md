# sources/distributed-fs/ceph-client/tools/sched_ext/scx_flatcg.c

Purpose: user-space loader and monitor for the flattened cgroup scheduler.

Important APIs/functions: parses options `-s`, `-i`, `-f`, `-v`, `-h`; `read_cpu_util()` computes CPU utilization from `/proc/stat`; `fcg_read_stats()` reads and sums the per-CPU stats map; main uses common sched_ext open/load/attach/UEI macros.

Control flow: open skeleton, initialize rodata (`nr_cpus`, default cgroup slice, FIFO flag), parse options, load/attach, then periodically read CPU utilization and BPF stats and print a monitoring line until signal or UEI exit. On exit, detach, report UEI, destroy, and restart on restart exit code.

State and persistence: keeps last `/proc/stat` sum/idle values to compute deltas and stores BPF stats snapshots in local arrays. No external persistent state.

Dependencies and integration: generated skeleton, libbpf, common sched_ext headers, `/proc/stat`, and `scx_flatcg.h` stat names/indices.

Risks: CPU utilization parsing assumes the first `/proc/stat` line format and uses simple tokenization. Large CPU counts affect per-CPU stats reads. Output is monitoring-oriented rather than structured.

Test signals: option parsing, CPU utilization sanity, stat counter changes under cgroup workloads, FIFO flag propagation, signal cleanup, and hotplug restart behavior.
