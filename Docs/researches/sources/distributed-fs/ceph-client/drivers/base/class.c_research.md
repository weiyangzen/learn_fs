# sources/distributed-fs/ceph-client/drivers/base/class.c

### Purpose
`class.c` implements driver-core device classes under `/sys/class`. It registers class ksets, class attribute files, class device iteration, class interfaces, dynamically-created classes, compatibility links, and class registration state queries.

### Important APIs, Types, And Functions
The file uses `struct class`, `struct class_interface`, `struct class_dev_iter`, `struct class_compat`, and `struct subsys_private`. Important exported functions are `class_register()`, `class_unregister()`, `class_create()`, `class_destroy()`, `class_create_file_ns()`, `class_remove_file_ns()`, `class_dev_iter_init()`, `class_dev_iter_next()`, `class_dev_iter_exit()`, `class_for_each_device()`, `class_find_device()`, `class_interface_register()`, `class_interface_unregister()`, `show_class_attr_string()`, `class_compat_register()`, `class_compat_unregister()`, `class_compat_create_link()`, `class_compat_remove_link()`, `class_is_registered()`, and `classes_init()`.

### Control Flow
`classes_init()` creates the top-level `/sys/class` kset. `class_register()` validates namespace callback consistency, allocates `subsys_private`, initializes the class device klist and interface list, registers the class kset, and creates class attribute groups. Class attributes route sysfs show/store through `class_attr_show()` and `class_attr_store()`. Iterators use the class klist and take device references through klist callbacks. Interface registration adds the interface under the class mutex and immediately invokes `add_dev()` for existing class devices; unregister removes the interface and invokes `remove_dev()` for current devices.

### State, Persistence, And Dependencies
Global `class_kset` anchors all class ksets. Each class owns a `subsys_private` with a device klist, interface list, glue directory kset, namespace operations, lockdep key, and mutex. Dynamic classes created by `class_create()` are freed through the `class_create_release()` callback when unregistered. The file depends on kobjects, sysfs, klist, class and device internals, and namespace ownership callbacks.

### Integration Points
`core.c` uses class private state when placing class devices in sysfs, creating class symlinks, iterating class interfaces, and changing sysfs ownership. Device classes such as `devlink`, block, net, tty, and char-device classes depend on these APIs to expose class-level and device-level sysfs views. Compatibility classes support migration from class devices to bus devices while preserving legacy userspace paths.

### Risks
As with bus code, reference handling is nontrivial: `class_to_subsys()` increments a reference, interface registration keeps a reference until unregister, and iterator init also stores a reference that must be released by `class_dev_iter_exit()`. `class_for_each_device()` and `class_find_device()` call `class_to_subsys()` and then `class_dev_iter_init()`, so their paired `subsys_put()` calls are intentional. Namespace callbacks must be provided as a matched pair or class registration fails. `class_is_registered()` is only momentary and can race with unregister.

### Test Signals
Test class lifecycle with normal and dynamic classes, class group creation failures, namespaced class attributes, iterator start/type filtering, `class_find_device()` reference ownership, interface callbacks for pre-existing and removed devices, compatibility symlink creation/removal, and registration state checks under concurrent unregister.
