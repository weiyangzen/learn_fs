# sources/distributed-fs/ceph-client/drivers/base/platform.c

## Purpose
Implements the Linux platform pseudo-bus: resource and IRQ lookup helpers, platform device allocation/registration/unregistration, platform driver registration/probing, bus matching/uevents, DMA setup, PM callbacks, and platform bus initialization.

## Important APIs, Types, And Functions
Exports `platform_bus`, `platform_bus_type`, resource helpers (`platform_get_resource()`, `platform_get_mem_or_io()`, `platform_get_resource_byname()`), ioremap helpers, IRQ helpers (`platform_get_irq*()`, `platform_irq_count()`, `devm_platform_get_irqs_affinity()`), device lifecycle helpers (`platform_device_alloc()`, `platform_device_add_resources()`, `platform_device_add_data()`, `platform_device_add()`, `platform_device_del()`, `platform_device_register_full()`), and driver helpers (`__platform_driver_register()`, `platform_driver_unregister()`, `__platform_driver_probe()`, `__platform_create_bundle()`, `__platform_register_drivers()`). The `platform_devid_ida` allocates automatic IDs.

## Control Flow
Resource lookup scans `pdev->resource[]` by type, index, or name. IRQ lookup prioritizes firmware IRQs from OF/ACPI, falls back to resources, sets trigger type from resource flags, supports ACPI GPIO IRQ fallback for index zero, and treats IRQ 0 as invalid. Device registration initializes DMA masks, assigns a parent and bus, formats the device name from explicit/none/auto IDs, claims memory/I/O resources, and calls `device_add()`, with rollback for IDA and resources. Driver registration assigns bus ownership and delegates to `driver_register()`. Probe attaches PM domains, applies OF clock defaults, rejects one-shot probe functions after initial use, and invokes the platform driver's `probe()`.

## State And Persistence
State includes registered platform devices on `platform_bus_type`, claimed resources under `iomem_resource`/`ioport_resource`, allocated auto IDs, copied resources/platform data/software nodes, OF node references, DMA mask fields, driver override matching state, and `pdev->id_entry` from ID-table matching. No local disk state is used.

## Dependencies And Integration
Integrates with OF, ACPI, IRQ mapping/affinity, devres, IOMMU default domains, DMA configuration, PM domains, runtime/system PM generic ops, module loading via modalias uevents, and the broader driver core bus/device/driver model.

## Risks And Test Signals
High-risk areas are rollback on partial resource insertion, auto-ID freeing, OF/ACPI IRQ fallback differences, probe deferral suppression in `__platform_driver_probe()`, DMA/IOMMU cleanup for driver-managed DMA, modalias ABI stability, and matching order changes. Test signals include platform device KUnit/selftests, resource conflict tests, IRQ-by-index/name tests for OF and ACPI, auto-ID register/unregister loops, driver override matching, PM-domain attach/detach behavior, and module autoload modalias checks.
