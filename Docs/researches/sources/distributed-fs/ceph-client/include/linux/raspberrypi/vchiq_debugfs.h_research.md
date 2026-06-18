# sources/distributed-fs/ceph-client/include/linux/raspberrypi/vchiq_debugfs.h

Purpose: declares VCHIQ debugfs integration for global state and per-instance debug nodes.

Important APIs and types: `struct vchiq_debugfs_node` stores a `struct dentry *`. Functions include `vchiq_debugfs_init()`, `vchiq_debugfs_deinit()`, `vchiq_debugfs_add_instance()`, and `vchiq_debugfs_remove_instance()`.

Control flow: driver/core initialization creates debugfs roots for a `vchiq_state`; instances are added and removed as clients open/close; deinit tears down the debugfs hierarchy.

State and persistence: debugfs dentries and per-instance nodes are runtime diagnostic state only.

Dependencies and integration points: integrates VCHIQ core/instance state with debugfs. The header forward-declares VCHIQ types and leaves debugfs implementation details in source files.

Risks and test signals: risks include stale dentries after instance removal, debugfs disabled build assumptions, teardown races with readers, and leaking per-instance nodes. Test mount/unmount debugfs, instance add/remove while reading files, driver unload, and multiple concurrent instances.
