<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/roles/class.c -->
# sources/distributed-fs/ceph-client/drivers/usb/roles/class.c

Purpose: implements the Linux USB role-switch class: provider registration, consumer lookup, role get/set, optional sysfs userspace control, uevents, module references, and connector symlink integration. The complete 469-line source was read.

Important APIs/types/functions: private `struct usb_role_switch`; exported `usb_role_switch_register()`, `usb_role_switch_unregister()`, `usb_role_switch_set_role()`, `usb_role_switch_get_role()`, `usb_role_switch_get()`, `fwnode_usb_role_switch_get()`, `usb_role_switch_put()`, `usb_role_switch_find_by_fwnode()`, `usb_role_string()`, and drvdata accessors; sysfs `role` attribute.

Control flow and state: `subsys_initcall` registers class `usb_role`; providers register a switch device from a descriptor; consumers find it via parent `usb-b-connector` fwnode or connection lookup; setting a role locks, calls provider `set`, caches the role, and emits `KOBJ_CHANGE`; getting calls provider `get` or returns cache. State includes cached role, registration flag, driver data, module reference, fwnode, and connector links.

Dependencies and integration points: device core, sysfs, firmware-node/property connections, component framework, lockdep, module refcounting, and `include/linux/usb/role.h`.

Risks and test signals: risks include lifetime races during unregister, invalid provider enum returns indexing `usb_roles`, symlink bind failures, and `-EPROBE_DEFER` lookup behavior. Test provider/consumer lookup paths, sysfs visibility and writes, uevents, connector links, module get/put, concurrent set/get/unregister, and error-returning callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/roles/class.c -->
