# sources/distributed-fs/ceph-client/tools/sched_ext/scx_cpu0.bpf.c

Purpose: minimal sched_ext scheduler that funnels runnable work to CPU0 through a custom DSQ to stress bypass/load-balancer behavior.

Important APIs/types/functions: rodata `nr_cpus`, `UEI_DEFINE(uei)`, custom DSQ ID `DSQ_CPU0`, per-CPU array `stats` with local and CPU0 counters, `stat_inc()`, and callbacks `cpu0_select_cpu()`, `cpu0_enqueue()`, `cpu0_dispatch()`, `cpu0_init()`, and `cpu0_exit()`.

Control flow: `select_cpu` always returns CPU0. `enqueue` sends tasks already on CPU0 to `DSQ_CPU0`; tasks that cannot run on CPU0 are queued to their local DSQ and counted separately. `dispatch` only moves from `DSQ_CPU0` when running on CPU0. `init` creates the custom DSQ.

State and persistence: per-CPU `stats` map persists while loaded; UEI stores exit data. No filesystem state.

Dependencies and integration: uses sched_ext DSQs, BPF per-CPU maps, and common UEI exit reporting. User space reads the stats map and sets `nr_cpus`.

Risks: intentionally creates pathological CPU0 concentration and can trigger stalls if bypass behavior fails. It ignores `enq_flags` for local fallback and always tries CPU0 as a hint.

Test signals: stats should show CPU0 versus local queueing, CPU0 should drain `DSQ_CPU0`, and stress tests should exercise bypass without hangs.
