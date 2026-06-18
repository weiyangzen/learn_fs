<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_device.h -->
# sources/distributed-fs/ceph-client/include/linux/of_device.h

## Purpose
This header connects OF node matching with the generic device/driver model, including driver match tables, modalias/uevent generation, DMA configuration, and bus-id creation.

## Important APIs, types, and functions
`of_match_device()` finds a matching `struct of_device_id` for a `struct device`. `of_driver_match_device()` checks a driver's `of_match_table`. `of_device_modalias()`, `of_device_uevent()`, and `of_device_uevent_modalias()` expose OF compatibility data to userspace/module loading. `of_dma_configure_id()` and `of_dma_configure()` configure DMA parameters from an OF node and optional requester ID. `of_device_make_bus_id()` constructs a stable device name.

## Control flow
The driver core invokes match and uevent helpers during binding and hotplug. Device creation or probe configures DMA using the node, `dma-ranges`, coherency, and optional ID before the driver performs DMA. Without `CONFIG_OF`, match/modalias fail or no-op and DMA configuration returns success without applying OF data.

## State and persistence
The header stores no state. It affects device state by selecting a driver match, setting DMA masks/ops/coherency in implementation code, and populating uevent environment variables.

## Dependencies and integration points
It depends on `linux/device/driver.h`, OF match tables, the device model, module autoloading, uevents, and DMA/IOMMU setup paths.

## Risks and test signals
Risks include mismatched compatible tables, modalias truncation, drivers binding without DMA being configured, optional requester ID mistakes with IOMMUs, and relying on OF match in non-OF builds. Test OF driver binding, module autoload modaliases, uevent contents, DMA-coherent and non-coherent devices, IOMMU IDs, and `!CONFIG_OF` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_device.h -->
