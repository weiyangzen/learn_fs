# sources/distributed-fs/ceph-client/drivers/gpib/include/gpibP.h

## Purpose

`gpibP.h` is a private kernel header for linux-gpib internals. It pulls together core types, ioctl/user definitions, I/O helpers, PCI lookup helpers, event queues, pseudo IRQ support, and exported core driver registration entry points.

## Important APIs and Types

- `gpib_register_driver()` and `gpib_unregister_driver()` are the central integration points for board drivers exposing a `struct gpib_interface`.
- `gpib_pci_get_device()` and `gpib_pci_get_subsys()` provide config-filtered PCI discovery helpers.
- `num_gpib_events()`, `push_gpib_event()`, and `pop_gpib_event()` manage per-board event queues.
- `gpib_request_pseudo_irq()` and `gpib_free_pseudo_irq()` support timer-backed polling when hardware IRQs are unavailable.
- `gpib_match_device_path()` matches sysfs device paths used by USB attach flows.
- `board_array` and `registered_drivers` expose global core state to drivers.

## Control Flow and Integration

Board modules include this header to register their callback table and use common discovery/event helpers. The HP, INES, NEC7210, and LPVO files in this subset all rely on types or functions reached through this header.

## State and Persistence Behavior

The header declares global board and registered-driver lists but does not define them. Driver lifetime state is coordinated through these globals by the gpib core.

## Dependencies

It includes `gpib_types.h`, `gpib_proto.h`, `gpib_cmd.h`, public linux-gpib headers, `linux/fs.h`, `linux/interrupt.h`, and `linux/io.h`. It is not a userspace header.

## Risks and Test Signals

Because it exposes private globals, misuse can bypass core locking or registration invariants. Test signals include module registration/unregistration ordering, event queue correctness under interrupt load, and PCI/USB path matching for multi-board configurations.
