# sources/distributed-fs/ceph-client/lib/kobject.c

Purpose: implements core kobject and kset lifecycle management: naming, sysfs directory creation/removal, refcounting, kset membership, namespace hooks, sysfs attribute operations, and dynamic object helpers.

Important APIs: namespace/ownership (`kobject_namespace`, `kobject_get_ownership`, `kobj_ns_*`), path/name (`kobject_get_path`, `kobject_set_name`), lifecycle (`kobject_init`, `kobject_add`, `kobject_init_and_add`, `kobject_del`, `kobject_get`, `kobject_get_unless_zero`, `kobject_put`, `kobject_create_and_add`), mutation (`kobject_rename`, `kobject_move`), ksets (`kset_init`, `kset_register`, `kset_unregister`, `kset_find_obj`, `kset_create_and_add`), and `kobj_sysfs_ops`.

Control flow: initialization sets kref/list/state flags. Add sets the name, resolves parent or kset parent, joins the kset list, creates the sysfs directory and default groups, enables namespace filtering if needed, and marks `state_in_sysfs`. Delete removes default groups, auto-emits remove uevents when necessary, removes sysfs, releases sysfs/kset/parent references, and clears state. Put triggers cleanup via kref release, optionally delayed under debug config.

State and persistence: persistent state is the kobject name, kref, parent/kset links, sysfs node reference, state flags for sysfs and uevents, kset lists, and namespace ops table protected by a spinlock.

Dependencies and integration: integrates with sysfs/kernfs, kref, ksets, uevents, namespace operations, ownership callbacks, and dynamic allocation. It is a central object model for devices, buses, and kernel subsystems.

Risks: incorrect lifetime handling leaks or use-after-frees kobjects; missing release callbacks are flagged as broken; rename/move callers must serialize and avoid name collisions; auto cleanup uevents can surprise callers; namespace ops registration is global and one-shot by type; path building retries on concurrent rename.

Test signals: sysfs registration/unregistration tests, kobject refcount debugging, uevent sequence tests, namespace mount/filter tests, duplicate-name failures, and fault injection for allocation/sysfs errors.
