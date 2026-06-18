<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/mod.c -->
# sources/distributed-fs/ceph-client/net/9p/mod.c

This file is the 9P network module entry point and dynamic transport registry. It also provides optional debug logging when `CONFIG_NET_9P_DEBUG` is enabled.

State includes global `p9_debug_level` under debug builds, a spinlock-protected `v9fs_trans_list`, and registered `struct p9_trans_module` entries. `v9fs_register_trans()` and `v9fs_unregister_trans()` add/remove transport modules. `v9fs_get_trans_by_name()` searches by name, optionally `request_module("9p-%s")`, and takes a module reference with `try_module_get()`. `v9fs_get_default_trans()` first picks a registered default, then any registered transport, then tries built-in default names in order: virtio, tcp, fd, unix, xen, rdma. `v9fs_put_trans()` drops the module reference.

Module initialization calls `p9_client_init()`, initializes error mappings, and logs installation. Exit logs unload and destroys client caches through `p9_client_exit()`.

Dependencies are Linux module refcounting, optional module autoloading, transport modules, 9P client initialization, and error mapping. Risks include transport unregister while clients hold references, default transport selection surprises, missing autoload aliases, and no cleanup for error hash entries because they are static. Tests should register/unregister dummy transports, lookup by name with module refs, default selection ordering, debug logging masks, and init failure if request cache allocation fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/mod.c -->
