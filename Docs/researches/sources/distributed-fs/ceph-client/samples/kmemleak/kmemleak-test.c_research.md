# sources/distributed-fs/ceph-client/samples/kmemleak/kmemleak-test.c

Purpose: intentionally allocates different kinds of memory to exercise kmemleak leak detection.

Important APIs/functions: uses `kmalloc`, `vmalloc`, optional `kmem_cache_alloc(files_cachep)` when modules are disabled, `kzalloc`, `list_add_tail`, per-CPU storage via `DEFINE_PER_CPU`, `__alloc_percpu`, and module init/exit.

Control flow: init logs several orphan `kmalloc` and `vmalloc` allocations, builds a list of allocated `test_node` objects that remain reachable while loaded, allocates one pointer per possible CPU, and allocates an anonymous percpu block. Exit removes list nodes from `test_list` without freeing them so they become kmemleak candidates after module removal.

State and persistence: leaked allocations persist after load for kmemleak to discover. List-linked objects are intentionally reachable until exit unlinks them; per-CPU pointers keep their allocations reachable from per-CPU storage.

Dependencies and integration: depends on `CONFIG_DEBUG_KMEMLEAK` for meaningful runtime behavior.

Risks: intentionally leaks memory and should only be used in test kernels. Results depend on scan timing, module removal, percpu root scanning, and kmemleak configuration.

Test signals: load module, trigger `/sys/kernel/debug/kmemleak` scans, compare reported orphan allocations, unload to make list nodes unreachable, and scan again.
