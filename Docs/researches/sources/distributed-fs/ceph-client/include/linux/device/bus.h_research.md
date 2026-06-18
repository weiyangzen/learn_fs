# sources/distributed-fs/ceph-client/include/linux/device/bus.h

Purpose: Defines the bus-specific portion of the Linux driver model, including bus registration, device/driver matching, bus attributes, iteration helpers, notifiers, DMA hooks, PM hooks, and online/offline callbacks.

Important APIs, types, and functions: Key type is `struct bus_type`, with name/dev_name, default bus/device/driver groups, match/uevent/probe/sync_state/remove/shutdown callbacks, IRQ affinity, online/offline, suspend/resume, VF count, DMA configure/cleanup, PM ops, driver_override support, and parent-lock requirement. Other APIs define `bus_attribute`, `device_match_t`, generic match helpers, `device_iter_t`, bus device/driver iteration and find helpers, breadth-first sorting, notifier registration, notifier event enum, and accessors for bus kset/root device.

Control flow: A bus registers its `bus_type`; devices and drivers added to that bus are matched with the bus `match()` callback and probed via bus/driver callbacks. Iteration/find helpers walk bus device lists and return referenced devices. Notifiers report device add/remove and driver bind/unbind events, often while the device lock is held.

State and persistence: Bus core state is maintained internally in `subsys_private`, ksets, device/driver lists, attributes, and notifier chains. The header exposes the immutable bus descriptor and callback contract, not storage implementation.

Dependencies and integration points: Depends on kobjects, klists, PM, devices, drivers, ACPI/OF/fwnode matching, notifiers, and DMA setup. Used by PCI, platform, USB, virtual, and other bus implementations.

Risks and test signals: Risks include match callbacks returning wrong errors, notifier deadlocks under device lock, forgetting to drop references from find helpers, parent-lock ordering issues, and inconsistent DMA cleanup. Test bus register/unregister, driver/device hotplug, deferred probe, generic match helpers, notifier ordering, bus sysfs attributes, bus rescan, and online/offline callbacks.
