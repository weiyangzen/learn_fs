# sources/distributed-fs/ceph-client/drivers/mcb/mcb-core.c

## Purpose
`mcb-core.c` implements the Linux bus type for MEN Chameleon Bus devices. It lets carrier drivers allocate MCB buses and devices while function drivers bind by Chameleon device IDs.

## Important APIs, Types, and Functions
The file defines matching/probe/remove/shutdown callbacks for `mcb_bus_type`, sysfs attributes for carrier metadata, and exported APIs such as `__mcb_register_driver()`, `mcb_unregister_driver()`, `mcb_device_register()`, `mcb_alloc_bus()`, `mcb_release_bus()`, `mcb_bus_get()`, `mcb_bus_put()`, `mcb_alloc_dev()`, `mcb_free_dev()`, `mcb_bus_add_devices()`, `mcb_get_resource()`, `mcb_request_mem()`, `mcb_release_mem()`, and `mcb_get_irq()`.

## Control Flow, State, and Persistence
`fs_initcall(mcb_init)` registers the bus. Carriers call `mcb_alloc_bus()`, parse Chameleon tables into `mcb_device` objects, register them, then call `mcb_bus_add_devices()` to bind drivers. Driver probe pins the carrier module and device until remove. Bus numbering is allocated by `IDA`; bus lifetime is tied to device release and `mcb_bus_put()`. Runtime state lives in kernel device model structures, bus refs, resource descriptors, and sysfs-visible Chameleon header fields. There is no durable persistence.

## Dependencies and Integration Points
It depends on `linux/mcb.h`, the kernel device model, module refs, IDA, resource APIs, and sysfs attributes. Carrier drivers import the `MCB` namespace and function drivers use MCB registration helpers.

## Risks and Test Signals
Risks include global unregister scanning all devices on the bus type rather than only a carrier's children, module ref imbalance on failed probe/remove, resource lifetime mistakes, and IRQ fallback returning uninitialized resources. Tests should cover multiple carriers, failed function-driver probe, remove while devices are bound, sysfs attribute reads, resource request conflicts, and namespace/modpost checks.
