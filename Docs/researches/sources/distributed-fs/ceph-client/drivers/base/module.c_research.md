# sources/distributed-fs/ceph-client/drivers/base/module.c

## Purpose
Maintains sysfs relationships between registered device drivers and the modules or built-in module kobjects that provide them.

## Important APIs, Types, And Functions
`module_add_driver()` creates a `module` link under the driver's private kobject and a reverse link under `/sys/module/<module>/drivers/<bus>:<driver>`. `module_remove_driver()` removes both links. `make_driver_name()` creates the stable reverse-link name, while `module_create_drivers_dir()` lazily creates the module's `drivers` directory under a static mutex.

## Control Flow
Driver registration calls `module_add_driver()` with the owning module and driver. If the driver is built in and carries `mod_name`, the function looks up or creates a built-in module kobject and stores it in `drv->p->mkobj`. It then creates the driver-to-module symlink, allocates the reverse name, creates the module `drivers` directory if needed, and adds the reverse symlink. Each failure path unwinds the links and allocated name created so far. Removal is symmetric and tolerates NULL drivers and missing module kobjects.

## State And Persistence
The only persistent state is live sysfs topology and, for built-in drivers, the cached `drv->p->mkobj` pointer. No disk state is written. Lifetime is governed by kobject references and the driver's private object lifetime.

## Dependencies And Integration
Uses driver private kobjects from the driver core, module kobjects from the module subsystem, sysfs link APIs, `lookup_or_create_module_kobject()`, and `drv->bus->name` for namespace-stable reverse names.

## Risks And Test Signals
Risks include stale or duplicate sysfs links, unbalanced kobject references for built-in module kobjects, and inconsistent cleanup when reverse-link creation fails. Test signals are driver registration/unregistration with loadable modules and built-in `mod_name` drivers, sysfs link presence under both driver and module directories, and repeated unload/reload without leaked links.
