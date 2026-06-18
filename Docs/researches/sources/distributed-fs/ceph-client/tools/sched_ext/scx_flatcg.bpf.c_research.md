# sources/distributed-fs/ceph-client/tools/sched_ext/scx_flatcg.bpf.c

Purpose: BPF scheduler implementing flattened hierarchical cgroup CPU control. It compounds active cgroup weights into a flat virtual-time competition, then schedules tasks inside each selected cgroup by weighted vtime or FIFO.

Important APIs/types/functions: rodata `nr_cpus`, `cgrp_slice_ns`, and `fifo_sched`; global `cvtime_now`; stats map; per-CPU `fcg_cpu_ctx`; cgroup local storage `fcg_cgrp_ctx`; task storage `fcg_task_ctx`; rbtree `cgv_tree` of `cgv_node`; stash map of kptr nodes. Key helpers include `cgrp_refresh_hweight()`, `cgrp_cap_budget()`, `cgrp_enqueued()`, `update_active_weight_sums()`, and `try_pick_next_cgroup()`. Struct_ops include select/enqueue/dispatch/runnable/running/stopping/quiescent/init_task/cgroup callbacks/init/exit.

Control flow: runnable/quiescent callbacks update active weight sums up the cgroup tree. Enqueue either bypasses tasks with restricted affinity into local/global fallback DSQs or inserts into a cgroup DSQ using FIFO/vtime and marks the cgroup queued in the rbtree. Dispatch keeps the current cgroup until its slice expires or empties, charges unused/used virtual time, drains fallback DSQ first, then repeatedly picks the lowest virtual-time cgroup from the rbtree and moves a task from that cgroup DSQ to local. Cgroup init creates a DSQ, storage, and rbtree node stash; exit destroys DSQ and removes stash.

State and persistence: BPF maps and kptr rbtree nodes persist while loaded. Cgroup storage tracks weights, active counts, runnable counts, hweight, child sums, task vtime, cgroup vtime delta, and queued state. Task storage tracks bypass charge points.

Dependencies and integration: uses sched_ext DSQs keyed by cgroup ID, cgroup local storage, task storage, BPF rbtree/kptr APIs, cgroup kfuncs, task weight scaling helpers, and UEI exit reporting. User space sets slice duration, FIFO mode, and CPU count.

Risks: comments acknowledge flattening can mishandle thundering-herd cgroups behind low-priority parents. Some operations are intentionally opportunistic/racy because BPF spin locks cannot cover complex map operations. Cgroup ID is treated as a DSQ ID despite DSQ width caveats. Exiting cgroups with nodes still in the rbtree are drained later in dispatch.

Test signals: cgroup weight ratio workloads, nested cgroup hierarchy benchmarks, FIFO vs weighted-vtime mode, cgroup creation/deletion, task cgroup moves, restricted-affinity tasks, and stats counters for enqueue/race/pick paths.
