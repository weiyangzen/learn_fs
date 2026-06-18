# sources/distributed-fs/ceph-client/drivers/greybus/module.c

## Purpose

`module.c` manages Greybus modules, which are hotpluggable components containing one or more Greybus interfaces. It creates interface children, registers and deregisters modules, coordinates interface activation/enable during insertion, tears interfaces down during removal, and exposes sysfs attributes including a user-triggered eject path.

## Important APIs, Types, and Functions

- `gb_module_create()` allocates a flexible `struct gb_module` with an interface pointer array and creates each `gb_interface`.
- `gb_module_add()` registers the module device and calls `gb_module_register_interface()` for each interface.
- `gb_module_del()` deregisters each interface through `gb_module_deregister_interface()` and removes the module device.
- `gb_module_put()` drops all interface references and the module device reference.
- `eject_store()` marks interfaces ejected, disables/deactivates them, and asks SVC to eject the primary interface.
- Read-only sysfs attributes expose `module_id` and `num_interfaces`.

## Control Flow

SVC hotplug code creates a module and calls `gb_module_add()`. Each interface is activated first. Even if activation fails for a non-dummy interface, the interface device is still added so users can see the failed or dummy state. Successful activation is followed by device registration and full interface enablement. Removal marks interfaces removed, disables and deactivates them under their mutex, then deregisters device objects.

## State and Persistence Behavior

The module owns a persistent array of interface pointers until `gb_module_put()`. The `disconnected` flag is set by SVC removal and propagated to interfaces before teardown to prevent I/O during disable. The `ejected` flag is stored per interface by the eject sysfs path and prevents future activation.

## Dependencies and Integration Points

This file depends on SVC eject, interface lifecycle, Greybus bus/device model, sysfs attributes, and tracepoints. `svc.c` owns adding/removing module objects from the host-device module list after successful module registration.

## Risks and Edge Cases

- Module IDs and interface IDs assume contiguous IDs beginning at the primary interface ID.
- `gb_module_register_interface()` adds the interface device even after activation failure, but only enables it on full success.
- If `gb_interface_enable()` fails after interface device registration, the code deactivates but does not call `gb_interface_del()` in that path; later module removal must handle the partially registered interface.
- Eject is described as forceful and best-effort; failures from SVC eject are returned after local teardown already occurred.

## Test Signals

Cover module creation with multiple interfaces, allocation failure midway, add failure, activation failure for dummy and non-dummy interfaces, enable failure after add, sysfs eject with zero/nonzero values, SVC eject error reporting, module removal with `disconnected` set, and reference cleanup under tracepoints.
