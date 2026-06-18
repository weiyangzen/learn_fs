# sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/kwork_top.bpf.c

## sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/kwork_top.bpf.c

Purpose: this BPF program backs `perf kwork top` by accumulating runtime for scheduler tasks, IRQ handlers, and softirqs in per-CPU work maps.

Important maps and globals: `kwork_top_task_time` is task local storage for scheduler timestamps; `kwork_top_irq_time` stores IRQ/softirq entry timestamps; `kwork_top_tasks` stores pid/cpu task metadata; `kwork_top_works` stores runtime totals; `kwork_top_cpu_filter` gates CPUs. BSS globals include `enabled`, `from_timestamp`, and `to_timestamp`.

Control flow: `on_switch` records runtime for the previous task and timestamp for the next task. IRQ and softirq entry programs store a timestamp keyed by current task and class; exit programs compute delta and call `update_work()`. `update_task_info()` captures tgid, kernel-thread flag, and comm once per pid/cpu.

State and persistence: task-local scheduler timestamps survive across switches. Per-CPU hash maps accumulate runtimes by work key. Missing timestamps fall back to `from_timestamp`, trading continuity for possible overcounting.

Dependencies and integration: user space in `bpf_kwork_top.c` selects which programs autoload, sets CPU filter flags, reads maps, and translates class enum values. The program depends on tp_btf context layout and CO-RE reads of `task_struct`.

Risks: work key includes task pointer for disambiguation, so task lifetime/reuse affects cardinality. Max entries are finite. Runtime updates are not atomic across per-CPU rows but are isolated by per-CPU map semantics. Missing entry timestamps can inflate runtime.

Test signals: run scheduler/IRQ/softirq top modes, CPU-filtered sessions, high interrupt rates, task churn workloads, and verify user-space task metadata matches map rows.
