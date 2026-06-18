# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/devcom.c

Purpose: Implements a device-component communication registry that groups related mlx5 devices by component ID and match key, allows peer iteration, readiness gating, and event broadcast with rollback.

Important APIs and flow: Devices register with `mlx5_devcom_register_device()` and unregister by kref. Components register through `mlx5_devcom_register_component()`, which finds or creates a component matching ID/key/net namespace and handler, increments component refs, and attaches per-device data under the component rwsem. `mlx5_devcom_send_event()` calls the component handler on peers and rolls back earlier peers on error. Peer iteration is available under read lock or RCU. Lock helpers expose component write locking and trylock.

State and dependencies: Global `devcom_dev_list` and `devcom_comp_list` are protected by mutexes; each component owns a peer list, kref, ready flag, rwsem with lockdep class, match key, optional namespace, and event handler. `data` pointers are RCU-assigned for lockless peer lookup.

Risks and test signals: Handler mismatch for an existing component is rejected. Correctness depends on kref/lifetime pairing, rwsem use during ready changes, RCU read-side protection for RCU iteration, and rollback ordering. Tests should cover duplicate device registration, component sharing by key/ns, unregister while peers iterate, readiness false blocking iteration, event rollback, and lock/trylock behavior.
