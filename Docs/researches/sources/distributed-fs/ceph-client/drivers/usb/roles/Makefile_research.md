<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/roles/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/roles/Makefile

Purpose: maps USB role-switch Kconfig symbols to build objects for the generic role class and Intel xHCI role-switch glue.

Important APIs/types/functions: `obj-$(CONFIG_USB_ROLE_SWITCH) += roles.o`, `roles-y := class.o`, and `obj-$(CONFIG_USB_ROLES_INTEL_XHCI) += intel-xhci-usb-role-switch.o`.

Control flow and state: no runtime flow; Kbuild links `class.o` into the `roles` aggregate and leaves Intel glue independently selectable. No runtime state is stored.

Dependencies and integration points: `drivers/usb/roles/Kconfig`, Kbuild module naming, exported role-switch APIs, and Intel platform driver selection.

Risks and test signals: risks are build-map drift and accidentally mixing platform-specific glue into the generic module. Test built-in and modular builds and verify generated objects/modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/roles/Makefile -->
