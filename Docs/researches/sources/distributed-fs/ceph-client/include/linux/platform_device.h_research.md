# sources/distributed-fs/ceph-client/include/linux/platform_device.h

## Purpose
the Linux platform bus interface. It defines platform devices, platform drivers, resource lookup
helpers, registration APIs, and driver matching surfaces used by non-discoverable or firmware-
described devices.

## Important APIs, types, and functions
Macros/constants: `_PLATFORM_DEVICE_H_`, `PLATFORM_DEVID_NONE`, `PLATFORM_DEVID_AUTO`,
`platform_get_device_id`, `dev_is_platform`, `to_platform_device`, `to_platform_driver`,
`platform_driver_register`, `platform_driver_probe`, `module_platform_driver`,
`builtin_platform_driver`, `module_platform_driver_probe`, `builtin_platform_driver_probe`,
`platform_create_bundle`, and 8 more. Types: `struct platform_device`, `struct
platform_device_info`, `struct platform_driver`. Declared or inline functions:
`platform_device_register`, `platform_device_unregister`, `IOMEM_ERR_PTR`, `platform_get_irq`,
`platform_get_irq_optional`, `platform_irq_count`, `platform_get_irq_byname`,
`platform_add_devices`, `platform_device_register_full`, `platform_device_add`,
`platform_device_del`, `platform_device_put`, `int`, `void`, `platform_driver_unregister`,
`dev_get_drvdata`, `dev_set_drvdata`, `module_init`, and 15 more. Important struct details: struct
platform_device fields include `const char *name`, `int id`, `bool id_auto`, `struct device dev`,
`u64 platform_dma_mask`, `struct device_dma_parameters dma_parms`, `u32 num_resources`, `struct
resource *resource`; struct platform_device_info fields include `struct device *parent`, `struct
fwnode_handle *fwnode`, `bool of_node_reused`, `const char *name`, `int id`, `const struct resource
*res`, `unsigned int num_res`, `const void *data`; struct platform_driver fields include `int
(*probe)(struct platform_device *)`, `void (*remove)(struct platform_device *)`, `void
(*shutdown)(struct platform_device *)`, `int (*suspend)(struct platform_device *, pm_message_t
state)`, `int (*resume)(struct platform_device *)`, `struct device_driver driver`, `const struct
platform_device_id *id_table`, `bool prevent_deferred_probe`.

## Control flow
Board, firmware, or MFD code allocates resources and platform data, registers a `struct
platform_device`, and the platform bus matches it to a `struct platform_driver` by id table, OF/ACPI
data, or name. Probe code retrieves MMIO/IRQ/resources and platform data, then normal driver
lifecycle callbacks handle remove, shutdown, suspend, and resume.

## State and persistence
Persistent kernel state is the registered `struct platform_device`, its resource array, optional
platform data, DMA mask, id, and `struct device` membership on the platform bus. The objects live
until unregistration or devres cleanup and do not survive reboot.

## Dependencies and integration points
It includes `linux/device.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/rust/bindings/bindings_helper.h`, `sources/distributed-fs/ceph-
client/arch/um/drivers/vector_kern.c`, `sources/distributed-fs/ceph-
client/arch/um/drivers/virtio_uml.c`, `sources/distributed-fs/ceph-
client/arch/um/drivers/ubd_kern.c`, `sources/distributed-fs/ceph-
client/arch/xtensa/platforms/xt2000/setup.c`, `sources/distributed-fs/ceph-
client/arch/um/drivers/vector_kern.h`, `sources/distributed-fs/ceph-
client/arch/um/drivers/rtc_kern.c`, `sources/distributed-fs/ceph-client/net/rfkill/rfkill-gpio.c`.
It integrates with the Linux driver core and in-kernel helper libraries that include this header.

## Risks and test signals
Risks include resource index/name mismatches, stale platform-data pointers, incorrect DMA masks,
duplicate platform ids, OF/ACPI/name matching ambiguity, and unregister paths racing active driver
users. Test signals include probe/remove cycles, deferred probe, resource lookup by name and index,
hotplug or MFD child teardown, and randconfig builds with and without OF/ACPI.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_device.h` completely for this pass (432 lines, 15416 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_device.h_research.md`.
