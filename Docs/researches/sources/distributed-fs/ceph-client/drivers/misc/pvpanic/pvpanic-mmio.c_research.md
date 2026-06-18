# sources/distributed-fs/ceph-client/drivers/misc/pvpanic/pvpanic-mmio.c

Purpose: platform/ACPI/OF front end for pvpanic devices exposed as IO or memory resources.

Important APIs and functions: `pvpanic_mmio_probe()` obtains resource 0 via `platform_get_mem_or_io()`, maps IO resources with `devm_ioport_map()` or memory resources with `devm_ioremap_resource()`, and calls shared `devm_pvpanic_probe()`. Match tables cover OF compatible `qemu,pvpanic-mmio` and ACPI ID `QEMU0001`.

Control flow: probe rejects missing or unsupported resource types, maps the resource with devm-managed lifetime, and delegates all capability/event/sys_off/list registration to the core. The platform driver exposes `pvpanic_dev_groups`.

State and persistence: transport-local state is only the mapped base pointer; persistent pvpanic state is in the shared core instance.

Dependencies and integration points: integrates platform devices from OF/ACPI with the shared `pvpanic.c` implementation and sysfs attribute groups.

Risks and test signals: test IORESOURCE_IO and IORESOURCE_MEM mapping paths, missing resources, devm unwind, ACPI and OF enumeration, and sysfs attributes on the platform device.
