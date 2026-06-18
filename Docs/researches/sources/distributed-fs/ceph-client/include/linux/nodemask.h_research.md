# sources/distributed-fs/ceph-client/include/linux/nodemask.h

Purpose: Provides the core NUMA nodemask API: bit operations, parsing/printing, remapping/folding, node-state masks, iteration macros, online/possible/memory node helpers, and scratch allocation.

Important APIs, types, and functions: Important exports are `node_set/clear/isset`, `nodes_and/or/xor/andnot/copy/complement`, equality/subset/intersection/empty/full/weight, first/next node helpers, `nodemask_of_node()`, parse helpers, remap/onto/fold helpers, `enum node_states`, `node_states[]`, online/possible macros, and `NODEMASK_ALLOC`/scratch helpers. Detected source surface: 540 lines; includes `linux/bitmap.h`, `linux/minmax.h`, `linux/nodemask_types.h`, `linux/random.h`, `linux/threads.h`; macros `NODEMASK_ALLOC`, `NODEMASK_FREE`, `NODEMASK_SCRATCH`, `NODEMASK_SCRATCH_FREE`, `NODE_MASK_ALL`, `NODE_MASK_LAST_WORD`, `NODE_MASK_NONE`, `__LINUX_NODEMASK_H`, `first_memory_node`, `first_node`, `first_online_node`, `first_unset_node`, `for_each_node`, `for_each_node_mask`, `for_each_node_state`, `for_each_node_with_cpus`, `for_each_online_node`, `next_memory_node`, and 40 more; structs `nodemask_scratch`; enums `node_states`; typedefs none; function-like declarations/helpers `__first_node`, `__first_unset_node`, `__next_node`, `__next_node_in`, `__node_clear`, `__node_remap`, `__node_set`, `__node_test_and_set`, `__nodelist_parse`, `__nodemask_parse_user`, `__nodemask_pr_numnodes`, `__nodes_and`, `__nodes_andnot`, `__nodes_clear`, `__nodes_complement`, `__nodes_copy`, `__nodes_empty`, `__nodes_equal`, and 36 more.

Control flow: Callers manipulate `nodemask_t` bitmaps at compile-time inline speed, iterate possible/online nodes, parse user masks, and update node state masks during topology changes.

State and persistence behavior: For NUMA builds, `node_states[]`, `nr_node_ids`, and `nr_online_nodes` are global topology state. Non-NUMA builds collapse helpers to single-node constants.

Dependencies and integration points: Depends on threads, bitmap, minmax, nodemask types, and random helpers. Used by scheduler, memory policy, cpusets, NUMA balancing, and hotplug code.

Risks and test signals: Risks are out-of-range node indexes, non-NUMA stub assumptions, parser accepting invalid masks, and node state races. Test mask operations, user parsers, memoryless nodes, hotplug state transitions, and large `MAX_NUMNODES` builds.
