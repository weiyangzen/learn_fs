# sources/distributed-fs/ceph-client/tools/sched_ext/scx_simple.bpf.c

Purpose: simple sched_ext BPF scheduler that demonstrates either global FIFO scheduling or weighted virtual-time scheduling using a shared DSQ.

Important APIs, types, and functions: defines read-only `fifo_sched`, global `vtime_now`, UEI state, shared DSQ ID 0, and a per-CPU array `stats` with local/global queue counters. Struct_ops callbacks are `simple_select_cpu`, `simple_enqueue`, `simple_dispatch`, `simple_running`, `simple_stopping`, `simple_enable`, `simple_init`, and `simple_exit`.

Control flow: `simple_init()` creates the shared DSQ. On wakeup, `simple_select_cpu()` uses the default selector; if it finds an idle CPU it inserts directly into the local DSQ and increments local stats. Otherwise `simple_enqueue()` inserts into the shared DSQ, either FIFO or by `p->scx.dsq_vtime`. In virtual-time mode it clamps idle credit to one default slice, uses `scx_bpf_dsq_insert_vtime()`, advances `vtime_now` when a task starts running, and charges consumed slice in `simple_stopping()` scaled by inverse task weight. `simple_dispatch()` pulls from the shared DSQ to the local CPU.

State and persistence: `vtime_now` persists while the BPF object is loaded and is intentionally racy but monotonic enough for a sample scheduler. Per-task virtual time is stored in sched_ext task state, not in custom maps. The per-CPU `stats` map persists until unload and is aggregated by userspace.

Dependencies and integration points: uses sched_ext BPF helpers, DSQ APIs, per-CPU BPF maps, task weight scaling helpers, and UEI. It is loaded by `scx_simple.c`.

Risks: FIFO mode can starve interactive workloads if CPU-saturating tasks dominate. Vtime updates are racy across CPUs by design, so fairness is approximate. There is no preemption implementation beyond sched_ext defaults. Built-in global DSQ is avoided because vtime insertion requires a custom priority-capable DSQ.

Test signals: successful attach, local/global stats increments, and stable workload progress are main signals. In vtime mode, weighted tasks should receive differentiated CPU shares; in FIFO mode, queue order should dominate. UEI errors or DSQ creation failure indicate scheduler failure.
