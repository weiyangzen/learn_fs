# sources/distributed-fs/ceph-client/drivers/xen/arm-device.c

## Purpose
`arm-device.c` maps and unmaps device MMIO regions into Xen initial-domain physical space for ACPI-enumerated platform and AMBA devices on ARM/ARM64 Dom0.

## Important APIs, types, and functions
Important helpers are `xen_map_device_mmio`, `xen_unmap_device_mmio`, `xen_platform_notifier`, optional `xen_amba_notifier`, and their `arch_initcall` registration functions. It uses Xen `XENMEM_add_to_physmap_range` and `XENMEM_remove_from_physmap`.

## Control flow
At arch init, if running in the Xen initial domain with ACPI enabled, the file registers bus notifiers. On `BUS_NOTIFY_ADD_DEVICE`, each memory resource is split into Xen pages, guest PFNs and device indexes are allocated and filled 1:1 from resource addresses, and Xen maps them as `XENMAPSPACE_dev_mmio`. On delete, the resources are removed from physmap page by page. Mapping failures trigger cleanup of already mapped resources.

## State and persistence
The file keeps no long-lived per-device state; Xen physmap mappings persist until corresponding bus delete or domain teardown.

## Dependencies and integration points
It depends on platform bus, optional AMBA bus, ACPI state, Xen memory hypercalls, Xen page macros, and initial-domain detection.

## Risks and test signals
Risks include resource-size rounding over partial pages, large allocation sizes for big MMIO windows, absence of per-page `errs` checking after range hypercalls, notifier ordering around driver probe, and cleanup only up to the failed resource index. Test signals include ACPI platform devices with multiple MMIO resources, AMBA devices, add/delete notifier paths, hypercall error injection, non-initial-domain no-op behavior, and partial mapping failure.
