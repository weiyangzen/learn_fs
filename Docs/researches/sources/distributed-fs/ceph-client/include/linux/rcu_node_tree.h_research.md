# sources/distributed-fs/ceph-client/include/linux/rcu_node_tree.h

Purpose: computes the compile-time hierarchy shape of TREE RCU/SRCU combining nodes based on `NR_CPUS`, `CONFIG_RCU_FANOUT`, and `CONFIG_RCU_FANOUT_LEAF`.

Important APIs and types: macros define fanout defaults, `RCU_FANOUT_1` through `RCU_FANOUT_4`, `RCU_NUM_LVLS`, per-level node counts, total `NUM_RCU_NODES`, level initializer arrays, node-name initializers, and force-quiescent-state node-name initializers. It emits a compile error if the configured fanout cannot cover `NR_CPUS`.

Control flow: RCU and SRCU structures use these macros at compile time to size arrays and initialize hierarchy metadata. The hierarchy limits contention by escalating only one contender per lower-level group.

State and persistence: no runtime state is stored here, but the macros determine the size/layout of RCU node arrays compiled into the kernel.

Dependencies and integration points: depends on `NR_CPUS`, RCU Kconfig values, and `DIV_ROUND_UP`. It is included by RCU internals and TREE SRCU because `srcu_struct` sizing depends on it.

Risks and test signals: risks include insufficient fanout for large CPU counts, poor fanout choices causing contention, and ABI/layout changes for SRCU structures. Test compile matrices for small and very large `NR_CPUS`, 32-bit vs 64-bit defaults, custom fanout values, CPU hotplug stress, and RCU torture scalability.
