# sources/distributed-fs/ceph-client/samples/configfs/configfs_sample.c

Purpose: demonstration kernel module for configfs subsystems and the helper macros in `linux/configfs.h`. It shows a childless subsystem, subsystems that create items, subsystems that create groups, and deeper item/group nesting.

Important APIs/functions: uses `struct configfs_subsystem`, `struct config_group`, `struct config_item`, `struct config_item_type`, `CONFIGFS_ATTR*`, `config_item_init_type_name`, `config_group_init_type_name`, `configfs_register_subsystem`, and `configfs_unregister_subsystem`. Attribute stores parse integers with `kstrtoint`; release callbacks free dynamically allocated children with `kfree`.

Control flow: module initialization initializes subsystem mutexes/groups, registers the sample subsystems, and unwinds earlier registrations on failure. Runtime control is driven by configfs mkdir/rmdir/read/write operations: `make_item` allocates simple children, `make_group` allocates child groups, attribute show/store methods expose per-object values, and release hooks free objects when configfs drops references. Exit unregisters all subsystems.

State and persistence: all state is in kernel memory and configfs dentries. Values such as `showme` and `storeme` persist only while the module and configfs objects exist. `showme` intentionally increments on read to demonstrate side effects.

Dependencies and integration: depends on `CONFIGFS_FS` and sample config support. Integrates with user space through `/sys/kernel/config` directories and files, not through Ceph-specific code.

Risks: examples are intentionally minimal and rely on correct configfs lifetime rules; leaked references or missing release callbacks would leak memory. Attribute writes accept plain decimal integers and return parser errors directly. This sample should not be treated as a policy or persistence layer.

Test signals: build with `CONFIG_SAMPLE_CONFIGFS`, load the module, mount configfs, create/remove sample items and groups, read description files, write `storeme`, and confirm object cleanup by removing the module.
