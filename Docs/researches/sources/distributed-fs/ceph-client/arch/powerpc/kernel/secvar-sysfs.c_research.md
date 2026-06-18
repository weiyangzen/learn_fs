# sources/distributed-fs/ceph-client/arch/powerpc/kernel/secvar-sysfs.c

Purpose: exposes firmware secure variables under `/sys/firmware/secvar`, including format reporting, per-variable size/data reads, and update writes.

Important APIs/types/functions: `format_show()`, `size_show()`, `data_read()`, `update_write()`, `update_kobj_size()`, `add_var()`, `secvar_sysfs_load()`, `secvar_sysfs_load_static()`, and `secvar_sysfs_init()`. Sysfs objects include root `secvar_kobj`, `vars` kset, per-variable kobjects, `format`, `size`, binary `data`, and binary `update` attributes.

Control flow: `late_initcall(secvar_sysfs_init)` checks `secvar_ops`, creates `/sys/firmware/secvar`, publishes the backend format string, creates the `vars` kset, sizes binary attributes from `max_size()`, creates a deprecated PLPKS config symlink, and enumerates variables either dynamically with `get_next()` or statically from `var_names`. Reads first query a variable's size, allocate a buffer, fetch data with `get()`, and serve it through `memory_read_from_buffer()`. Writes pass the sysfs-provided buffer to backend `set()`.

State and persistence: sysfs kobjects persist after init; actual secure-variable data persists in firmware/backend storage. Attribute maximum sizes are copied into `data_attr.size` and `update_attr.size` once during init.

Dependencies and integration points: depends on `secvar_ops` registration, firmware kobject infrastructure, PLPKS compatibility symlink helper, sysfs binary attributes, and backend method contracts (`format`, `get`, `set`, `max_size`, optional `get_next` or `var_names`).

Risks: sysfs write buffers are page-limited; the code warns when backend max object size exceeds `PAGE_SIZE`, meaning large updates may be impossible through this interface. Variable names become kobject names and are capped only by backend enumeration buffer size. Missing backend operations are not individually checked. Init error handling drops the root kobject but may rely on kobject cleanup for partially created children.

Test signals: boot with PLPKS/secvar backend, inspect `/sys/firmware/secvar/format`, enumerate `vars`, read each `size` and `data`, perform valid and invalid `update` writes, test dynamic and static backends, and check warning behavior when max size exceeds page size.
