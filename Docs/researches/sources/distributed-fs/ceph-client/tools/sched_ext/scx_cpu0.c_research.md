# sources/distributed-fs/ceph-client/tools/sched_ext/scx_cpu0.c

Purpose: user-space loader and stats printer for the CPU0 sched_ext example.

Important APIs/functions: `read_stats()` reads the per-CPU `stats` map for two counters and sums them across possible CPUs. `main()` uses `SCX_OPS_OPEN()`, `SCX_OPS_LOAD()`, `SCX_OPS_ATTACH()`, `UEI_EXITED()`, and `UEI_REPORT()`.

Control flow: set libbpf logging and signal handlers, open skeleton, set `nr_cpus`, parse `-v`/`-h`, load and attach, print `local=` and `cpu0=` once per second, detach/report/destroy, and restart if UEI encodes a restart action.

State and persistence: no persistent state. Runtime state is the skeleton, BPF link, exit flag, and per-iteration stats buffer.

Dependencies and integration: requires generated skeleton, libbpf, sched_ext, and access to BPF maps. It relies on libbpf's possible CPU count matching the per-CPU map value layout.

Risks: uses a variable-length stack array `cnts[2][nr_cpus]`, which can be large on high-CPU systems. Map lookup failures are silently skipped in stats aggregation.

Test signals: successful load/attach, monotonic stats under load, signal cleanup, and restart-on-hotplug behavior.
