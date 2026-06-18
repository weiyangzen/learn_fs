# sources/distributed-fs/ceph-client/include/linux/sched/ext.h

Purpose: declares the BPF extensible scheduler class data structures, dispatch queue IDs, task state flags, and diagnostic hooks.

Important APIs and types: `SCX_SLICE_*`, built-in `SCX_DSQ_*` IDs, `struct scx_dispatch_q`, `struct scx_dsq_pcpu`, `struct scx_dsq_list_node`, `struct sched_ext_entity`, `struct scx_task_group`, task/DSQ flag enums, `INIT_DSQ_LIST_CURSOR()`, `sched_ext_dead()`, `print_scx_info()`, and lockup/stall hooks are central.

Control flow: when `CONFIG_SCHED_CLASS_EXT` is enabled, each task embeds `sched_ext_entity`; BPF schedulers enqueue tasks into built-in or user dispatch queues, manipulate slices and virtual time, and transition task states through init/ready/enabled/dead. Disabled configs provide no-op diagnostics.

State and persistence: runtime state includes per-task SCX fields, dispatch queues, DSQ sequence numbers, RCU/hash/list membership, cgroup SCX metadata, and BPF-modifiable slice/vtime fields. It exists only while the scheduler and tasks are alive.

Dependencies and integration points: depends on BPF scheduler infrastructure, rhashtable, RCU, cgroups, core scheduling, and scheduler class integration. It is the header-level contract between scheduler core and sched_ext implementation/BPF programs.

Risks and test signals: risks include DSQ ordering corruption if vtime changes while queued, task state transition races, RCU lifetime errors, bypass-mode starvation, cgroup migration drift, and lockup diagnostics missing SCX state. Test sched_ext selftests, BPF scheduler load/unload, task fork/exit, cgroup moves, DSQ iteration, preemption/kick behavior, and disabled-config stubs.
