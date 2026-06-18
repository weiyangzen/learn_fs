# sources/distributed-fs/ceph-client/tools/perf/util/bpf_kwork_top.c

## sources/distributed-fs/ceph-client/tools/perf/util/bpf_kwork_top.c

Purpose: this file loads and reads the BPF implementation for `perf kwork top`, providing live runtime aggregation for IRQ, softirq, and scheduler work classes. It maps BPF per-work/per-CPU runtime rows into `kwork_work` objects and enriches scheduler rows with task metadata.

Important APIs and functions: `perf_kwork__top_prepare_bpf()` opens the `kwork_top` skeleton, disables all autoload, enables only selected class programs, configures CPU filters, loads, attaches, and stores class pointers. `perf_kwork__top_start()` and `perf_kwork__top_finish()` set BPF session timestamps and toggle `enabled`. `perf_kwork__top_read_bpf()` iterates `kwork_top_works` and calls `add_work()` for every nonzero per-CPU runtime. `read_task_info()` pulls `tgid`, kernel-thread flag, and command from `kwork_top_tasks`.

Control flow: selected classes decide which tp_btf programs attach: scheduler uses `sched_switch`, IRQ uses handler entry/exit, softirq uses entry/exit. The read path allocates a possible-CPU-sized array because `kwork_top_works` is per-CPU. Each key encodes class type, pid, and task pointer, while CPU is represented by the per-CPU array slot.

State and persistence: static `skel` and static supported-list class pointers hold process/session state. BPF maps store task local timestamps, IRQ/softirq timestamp rows, task metadata, runtime rows, and CPU filter entries. BPF globals `from_timestamp` and `to_timestamp` bound runtime fallback calculations.

Dependencies and integration: the user-space structs must stay in sync with `kwork_top.bpf.c`. Integration is via perf kwork's class list and `add_work` callback. It uses libbpf and perf CPU map helpers.

Risks: `perf_kwork__top_read_bpf()` can return early without freeing `data` on lookup or add-work errors. Runtime fallback to `from_timestamp` can overstate work if an entry timestamp is missing. Task names are allocated with `strdup()` and rely on downstream ownership. BPF map cardinality is capped at `MAX_ENTRIES`.

Test signals: run kwork top with scheduler-only, IRQ-only, softirq-only, and combined classes; test CPU filters; verify task names/tgids for user and kernel threads; and stress context-switch/interrupt-heavy workloads to catch map capacity and cleanup issues.
