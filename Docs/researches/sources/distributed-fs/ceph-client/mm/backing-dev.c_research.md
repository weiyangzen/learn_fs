# sources/distributed-fs/ceph-client/mm/backing-dev.c

## Purpose
`backing-dev.c` manages `struct backing_dev_info` registration, visibility, sysfs/debugfs attributes, writeback workqueue setup, and cgroup writeback domains. It is the central lifetime manager connecting filesystems and block devices to kernel writeback accounting and throttling.

## Important APIs, types, and functions
Important global state includes `noop_backing_dev_info`, `bdi_lock`, `bdi_tree`, `bdi_list`, and `bdi_wq`. Public functions include `bdi_init`, `bdi_alloc`, `bdi_register_va`, `bdi_register`, `bdi_set_owner`, `bdi_unregister`, `bdi_put`, `inode_to_bdi`, `bdi_dev_name`, and, with cgroup writeback, `wb_get_lookup`, `wb_get_create`, `wb_memcg_offline`, and `wb_blkcg_offline`. Internal helpers manage `bdi_writeback` initialization, shutdown, stats, debugfs, sysfs stores, and cgwb release.

## Control flow
`bdi_class_init` registers the `bdi` class and debugfs root, while `default_bdi_init` creates the global writeback workqueue. `bdi_alloc` initializes a BDI and root writeback state. `bdi_register_va` creates a class device, links the root writeback, registers debugfs, assigns an ID in the rb-tree, and publishes the BDI on the RCU list. Unregister removes global visibility, shuts down writeback work, tears down cgroup writebacks, resets ratios, removes devices/debugfs, and drops owner references.

## State and persistence
State is runtime-only: BDI IDs, rb-tree/list membership, krefs, device names, owner refs, ratio/byte limits, read-ahead values, writeback lists, delayed work, bandwidth counters, per-cpu counters, cgroup writeback radix trees, and offline cgwb lists. RCU and kref rules control when removed objects can be freed.

## Dependencies and integration points
It depends on device core, debugfs, writeback, memcg/blkcg, cgroups, workqueues, RCU, radix trees, percpu refs/counters, and tracepoints. It integrates with superblocks, block devices, sysfs `/sys/class/bdi`, debugfs `bdi`, and dirty throttling helpers.

## Risks and test signals
Risks include registration/unregistration races, use-after-free through RCU-visible lists, delayed work after shutdown, cgroup writeback offlining races, blkcg association changes, ratio accounting imbalance, and sysfs validation errors. Test signals include repeated BDI register/unregister, concurrent writeback and unmount, memcg/blkcg offlining, debugfs reads during teardown, sysfs min/max ratio and byte writes, block-device inode lookup, and lockdep/RCU stall checks.
