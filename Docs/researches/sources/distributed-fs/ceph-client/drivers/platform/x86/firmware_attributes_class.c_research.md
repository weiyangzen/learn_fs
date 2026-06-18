## sources/distributed-fs/ceph-client/drivers/platform/x86/firmware_attributes_class.c

Purpose: defines and registers a shared kernel class named `firmware-attributes`, used by platform firmware-setting drivers such as Dell WMI sysman to publish firmware configuration attributes under a common sysfs class.

Important APIs/functions: `const struct class firmware_attributes_class` contains only `.name = "firmware-attributes"` and is exported with `EXPORT_SYMBOL_GPL()`. `fw_attributes_class_init()` calls `class_register()`. `fw_attributes_class_exit()` calls `class_unregister()`.

Control flow: module init registers the class before consumers create devices under it. Consumers call `device_create(&firmware_attributes_class, ...)` and then build their own ksets/attributes below the class device. Exit unregisters the class.

State and persistence: the class object is global static state for the module lifetime. It does not store firmware attributes itself; all per-vendor data is owned by consumers. Sysfs devices disappear when consumers unregister and when the class unregisters.

Dependencies and integration: Linux device class core and module infrastructure. Export is GPL-only, so consumer modules must be GPL-compatible.

Risks: consumers must ensure class lifetime through Kconfig/module dependencies; creating devices before class registration would fail. The class has no dev_groups or release behavior, so consumers must manage their own devices and cleanup. Test signals include class presence in sysfs, consumer device creation/removal, module build as built-in or module, symbol resolution for consumers, and unload ordering when no consumers remain.
