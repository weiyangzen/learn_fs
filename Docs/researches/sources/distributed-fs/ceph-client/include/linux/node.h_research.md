# sources/distributed-fs/ceph-client/include/linux/node.h

Purpose: Declares NUMA node device model integration, node cache/performance attributes, memory hotplug registration, node notifiers, and CPU/memory node registration APIs.

Important APIs, types, and functions: Key types are `struct access_coordinate`, coordinate/cache enums, `struct node_cache_attrs`, `struct node`, and `struct node_notify`. APIs add cache/perf attributes, register memory blocks under nodes, register node notifiers, initialize node devices, register/unregister nodes, attach CPUs/memory, and map `device` to `node`. Detected source surface: 213 lines; includes `linux/device.h`, `linux/list.h`; macros `NODE_ADDED_FIRST_MEMORY`, `NODE_ADDING_FIRST_MEMORY`, `NODE_CANCEL_ADDING_FIRST_MEMORY`, `NODE_CANCEL_REMOVING_LAST_MEMORY`, `NODE_REMOVED_LAST_MEMORY`, `NODE_REMOVING_LAST_MEMORY`, `_LINUX_NODE_H_`, `hotplug_node_notifier`, `to_node`; structs `access_coordinate`, `device`, `list_head`, `memory_block`, `node`, `node_cache_attrs`, `node_notify`; enums `access_coordinate_class`, `cache_indexing`, `cache_mode`, `cache_write_policy`; typedefs none; function-like declarations/helpers `hotplug_node_notifier`, `node_add_cache`, `node_dev_init`, `node_notify`, `node_set_perf_attrs`, `node_update_perf_attrs`, `register_cpu_under_node`, `register_memory_blocks_under_node_hotplug`, `register_memory_blocks_under_nodes`, `register_memory_node_under_compute_node`, `register_node`, `register_node_notifier`, `unregister_cpu_under_node`, `unregister_memory_block_under_nodes`, `unregister_node`, `unregister_node_notifier`.

Control flow: Boot and hotplug code register node devices, attach CPUs and memory blocks, publish cache/performance attributes, and notify listeners when first/last memory is added or removed.

State and persistence behavior: Global `node_devices[]` and sysfs device state persist for each NUMA node. Cache/perf attributes and hotplug notifier state are runtime system topology state.

Dependencies and integration points: Depends on device model, lists, memory block hotplug, notifier blocks, and NUMA configuration. Used by memory, CPU, sysfs, and topology code.

Risks and test signals: Risks are stale sysfs topology after hotplug, missing notifier rollback, and invalid node IDs. Test node registration, memory add/remove, CPU online/offline, cache attribute publishing, and non-NUMA stubs.
