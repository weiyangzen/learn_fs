
# sources/distributed-fs/ceph-client/net/netfilter/nf_flow_table_procfs.c

Purpose: Exposes per-CPU flowtable workqueue counters through `/proc/net/stat/nf_flowtable` for each network namespace.

Important APIs and functions: `nf_flow_table_init_proc()` creates the proc entry using `proc_create_net()`. `nf_flow_table_fini_proc()` removes it. The seq operations iterate possible CPUs and print `count_wq_add`, `count_wq_del`, and `count_wq_stats` from `net->ft.stat`.

Control flow: The seq start function emits a header at position zero, then advances through `cpu_possible()` CPUs. `show` formats one row per CPU. Per-net init in core allocates the percpu stats before creating the proc entry.

State and persistence: Reads percpu `struct nf_flow_table_stat` in the target net namespace. No persistent state is stored in this file.

Dependencies and integration: Integrated by `nf_flow_table_core.c` pernet init/exit and incremented/decremented by `nf_flow_table_offload.c` workqueue scheduling/completion.

Risks: Main risks are proc entry lifecycle ordering relative to percpu allocation/free and counter consistency under concurrent updates. Test signals include reading the proc file with and without hardware-offload work, network namespace create/destroy, and CPU hotplug scenarios.
