<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/module.h -->
# sources/distributed-fs/ceph-client/include/linux/greybus/module.h

Purpose: This header defines Greybus modules, each representing a physical module with one or more interfaces attached to a host device.

Important APIs/types/functions: `struct gb_module` embeds a device, points to host, links into the host module list, records module id, interface count, disconnected flag, and a flexible array of interface pointers. Lifecycle APIs are `gb_module_create()`, `gb_module_add()`, `gb_module_del()`, and `gb_module_put()`.

Control flow, state, and persistence: SVC module-inserted events create modules with known interface counts. Adding publishes the module device and later creates interfaces. Deletion marks/removes interfaces and host links; put releases final references.

Dependencies/integration: It integrates with host devices, interfaces, Linux device model, and SVC module insertion/removal events.

Risks and test signals: Flexible-array allocation must match `num_interfaces`; removal must handle partially created interfaces. Tests should cover create/add/del lifecycle, interface pointer initialization, host list linkage, disconnected state, and reference cleanup after failed interface creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/module.h -->
