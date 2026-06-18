# sources/distributed-fs/ceph-client/tools/sched_ext/scx_central.c

Purpose: user-space loader and monitor for `scx_central.bpf.c`.

Important APIs/functions: uses `SCX_OPS_OPEN()`, `RESIZE_ARRAY()`, `SCX_OPS_LOAD()`, `SCX_OPS_ATTACH()`, `UEI_EXITED()`, and `UEI_REPORT()`. Options are `-s` slice microseconds, `-c` central CPU, `-v`, and `-h`.

Control flow: install signal handlers, open skeleton, initialize rodata (`central_cpu`, `nr_cpu_ids`, `slice_ns`), parse options, validate central CPU, resize `cpu_gimme_task` and `cpu_started_at`, load and attach struct_ops, then print BPF counters once per second until signal or UEI exit. On exit, detach, report UEI, destroy the skeleton, and restart when the exit code requests restart.

State and persistence: no external persistence. Runtime state includes `exit_req`, libbpf verbosity, skeleton rodata/data/bss, and the struct_ops link.

Dependencies and integration: depends on generated `scx_central.bpf.skel.h`, libbpf, `common.h`, sched_ext sysfs/BTF, and possible CPU count from libbpf.

Risks: uses `assert()` for CPU count assumptions; assertions can be compiled out. Restart uses `goto restart` and re-parses options. Invalid central CPU exits after destroying the skeleton.

Test signals: CLI parse tests, invalid central CPU rejection, successful attach, per-second stats output, SIGINT/SIGTERM cleanup, and hotplug restart path.
