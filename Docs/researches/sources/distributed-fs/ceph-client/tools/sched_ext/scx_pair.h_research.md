# sources/distributed-fs/ceph-client/tools/sched_ext/scx_pair.h

Purpose: shared limits for the pair scheduler.

Important APIs/constants: defines `MAX_CGRPS` as 1024 and `MAX_QUEUED` as 4096.

Control flow: none.

State and persistence: constants size BPF maps and user-space-created queue maps.

Dependencies and integration: included by both `scx_pair.bpf.c` and `scx_pair.c`; values must match across BPF and loader.

Risks: fixed limits can reject or fail workloads with too many cgroups or queued tasks. Increasing them raises memory and initialization cost.

Test signals: cgroup counts near `MAX_CGRPS`, per-cgroup queue depth near `MAX_QUEUED`, and loader memory/map creation behavior.
