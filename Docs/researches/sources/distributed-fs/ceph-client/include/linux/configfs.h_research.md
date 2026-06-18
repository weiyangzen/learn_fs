## sources/distributed-fs/ceph-client/include/linux/configfs.h

Purpose: This header defines the in-kernel configfs object model, allowing userspace to instantiate and configure kernel objects through a filesystem hierarchy.

Important APIs, types, and functions: Core types are `struct config_item`, `struct config_item_type`, `struct config_group`, `struct configfs_attribute`, `struct configfs_bin_attribute`, `struct configfs_item_operations`, `struct configfs_group_operations`, and `struct configfs_subsystem`. Item APIs include `config_item_set_name`, `config_item_name`, `config_item_init_type_name`, `config_item_get`, `config_item_get_unless_zero`, and `config_item_put`. Group APIs include `config_group_init`, `config_group_init_type_name`, `to_config_group`, `config_group_get`, `config_group_put`, `config_group_find_item`, and `configfs_add_default_group`. Attribute macros create read/write, read-only, write-only, and binary attributes. Registration APIs cover subsystems, groups, default groups, default removal, and dependency pinning.

Control flow: A subsystem registers a root `config_group`. Userspace mkdir operations call group `make_group` or `make_item`; rmdir/drop operations call `drop_item` and item release paths after reference counts drain. Attribute reads/writes call the configured `show`, `store`, `read`, or `write` callbacks. Links are controlled by `allow_link` and `drop_link`.

State and persistence: Runtime state is embodied by config items, krefs, dentries, group child lists, default group lists, and subsystem mutexes. Configfs state persists while objects are referenced from the filesystem and kernel users; it is not durable storage. Dependency APIs pin target items to prevent removal during dependent operations.

Dependencies and integration points: It depends on krefs, dentries, lists, mutexes, modules, VFS/configfs core, and caller-defined object lifecycles. It is often used by storage, target, USB gadget, and subsystem configuration code.

Risks and test signals: Risks are reference-count leaks, destructor misuse, calling dependency APIs from forbidden contexts, exposing writable attributes without validation, default group cleanup races, and using too-short names beyond `CONFIGFS_ITEM_NAME_LEN` expectations. Test signals include mount/unmount, mkdir/rmdir/link/unlink stress, attribute fuzzing, module unload under open files, and lockdep around subsystem mutexes.
