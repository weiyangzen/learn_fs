# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/hotplug-cpu.c

Purpose: Implements pseries CPU hotplug and DLPAR CPU add/remove. It manages RTAS CPU stop, logical CPU id assignment, present/online maps, OF node attach/detach, DRC state, NUMA/cache metadata, and optional CPU probe/release callbacks.

Important APIs/types/functions: Key state includes `rtas_stop_self_token` and per-node `node_recorded_ids_map`. Important functions include `pseries_cpu_offline_self()`, `pseries_cpu_disable()`, `pseries_cpu_die()`, `find_cpu_id_range()`, `pseries_add_processor()`, `pseries_remove_processor()`, `dlpar_offline_cpu()`, `dlpar_online_cpu()`, DRC index validation, `dlpar_cpu_add()`, `pseries_cpuhp_detach_nodes()`, `dlpar_cpu_remove()`, `dlpar_cpu()`, OF reconfig notifier, `pseries_cpu_hotplug_init()`, and `pseries_dlpar_init()`.

Control flow: Boot init checks RTAS stop/query tokens and installs SMP CPU hotplug callbacks. DLPAR add validates the requested CPU DRC under `/cpus`, acquires the DRC, configures connector nodes, attaches nodes with an OF changeset, updates NUMA distance, and onlines all allowed threads. Remove offlines all threads, releases the DRC, detaches the CPU node and uniquely referenced cache nodes, and rolls back by reacquiring/onlining if detach fails. OF reconfig events update `cpu_present_mask` and hard CPU ids.

State and persistence: Persistent state includes CPU online/present masks, hard SMP processor ids, PACA `cpu_start`, boot CPU id, per-node recorded id masks, NUMA lookup tables, dynamic OF CPU/cache nodes, DRC allocation/isolation state, and installed `smp_ops` callbacks.

Dependencies and integration points: Depends on RTAS stop-self and query stopped state, XICS/XIVE teardown and IRQ migration, VPA/SLB shadow unregister, CPU device hotplug core, topology SMT policy, dynamic OF notifiers, pseries DLPAR common helpers, and NUMA topology update functions.

Risks: Logical CPU ids must preserve SMT sibling adjacency while avoiding cross-node id reuse. Removing the last online CPU is blocked but races are guarded by CPU hotplug locks. Rollback after partial add/remove must restore DRC and online state. Cache node detachment depends on accurate use counts across CPUs and cache hierarchy.

Test signals: CPU DLPAR add/remove by DRC index, SMT-disabled online policy, last-CPU removal rejection, XICS and XIVE interrupt migration, NUMA id assignment across nodes, OF reconfig notifier behavior, kexec/offline stop-self path, and rollback injection are primary.

Source read size: 904 lines, 20202 bytes.
