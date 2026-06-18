# sources/distributed-fs/ceph-client/kernel/bpf/cpumap.c

## Purpose
`cpumap.c` implements `BPF_MAP_TYPE_CPUMAP`, an XDP redirect backend that moves XDP frames or generic skb redirects to per-CPU kernel threads. It isolates early XDP processing from normal network stack work and can optionally run a second XDP program on the target CPU before building or receiving skbs.

## Important APIs, types, and functions
Core types are `struct bpf_cpu_map`, `struct bpf_cpu_map_entry`, and per-CPU `struct xdp_bulk_queue`. Map operations are exposed through `cpu_map_ops`: `cpu_map_alloc()`, `cpu_map_update_elem()`, `cpu_map_delete_elem()`, `cpu_map_lookup_elem()`, `cpu_map_get_next_key()`, `cpu_map_free()`, `cpu_map_mem_usage()`, and `cpu_map_redirect()`. Runtime functions include `cpu_map_enqueue()`, `cpu_map_generic_redirect()`, `__cpu_map_flush()`, `cpu_map_kthread_run()`, `cpu_map_bpf_prog_run_xdp()`, `cpu_map_bpf_prog_run_skb()`, and `__cpu_map_entry_replace()`.

## Control flow
Map creation validates key and value sizes, flags, and `max_entries <= NR_CPUS`, then allocates an RCU pointer array. Updating an element validates map flags, target CPU, qsize, and optional XDP program fd, allocates per-CPU bulk queues, a `ptr_ring`, GRO node, optional attached `BPF_XDP_CPUMAP` program, and a bound kthread. The new entry is atomically swapped into the map; the old entry is freed through `queue_rcu_work()` after readers and pending flushes drain. XDP enqueue stores frames in a per-CPU bulk queue and links it into the current BPF net context flush list. Flush moves batched frames into the target ring and wakes the kthread. The kthread consumes frames/skbs, optionally runs the cpumap program under RCU and BPF net context, handles pass/drop/redirect results, builds skbs from frames, feeds GRO, emits tracepoints, and exits only after stop is requested and the ring is empty.

## State and persistence
State is per map and per populated CPU entry: RCU pointer slots, qsize, target CPU, map id, per-CPU bulk queues, ptr ring contents, kthread, optional BPF program reference, GRO state, completion, and deferred free work. Entries persist until map update/delete/free, then remain reachable through RCU until enqueue/flush critical sections finish. Packet queues are transient and intentionally short-lived across a NAPI poll and kthread processing cycle.

## Dependencies and integration points
This file integrates XDP redirect helpers, BPF map APIs, RCU and local locks, ptr rings, kthreads, workqueues, GRO, skb allocation caches, netdevice/XDP frame conversion, BPF net context flush lists, tracepoints, and optional cpumap XDP programs checked by `bpf_prog_map_compatible()`. Generic skb redirect uses a tagged pointer bit to distinguish skbs in the same ring.

## Risks and test signals
Risks include target CPU hotplug assumptions, RCU lifetime races between map updates and NAPI flush, producer ring overflow and frame return correctness, tagged skb pointer handling, kthread stop ordering, GRO flush latency, optional program compatibility errors, qsize memory pressure, and map memory accounting that omits dynamic entry allocations. Test signals include update/delete/free under redirect load, qsize zero delete behavior, invalid CPU rejection, cpumap program pass/drop/redirect paths, generic skb redirect paths, ring-full drops, kthread wake and drain on teardown, tracepoint counters, GRO behavior under empty and non-empty rings, and map lookup under RCU/read-bh contexts.
