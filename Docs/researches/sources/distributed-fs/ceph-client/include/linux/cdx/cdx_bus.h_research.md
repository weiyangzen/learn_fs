## sources/distributed-fs/ceph-client/include/linux/cdx/cdx_bus.h

**Purpose:** This header exposes the public CDX bus interface for AMD/Xilinx CDX controllers, devices, and drivers.

**Important APIs/types/functions:** Constants include resource limits and bus/controller ID helpers. `struct cdx_device_config` models MSI, bus-master, reset, and MSI-enable configuration. `struct cdx_ops` supplies controller callbacks for bus enable/disable, scan, and device configure. `struct cdx_controller` stores backing device, private data, MSI domain, ID, registration state, and ops. `struct cdx_device` embeds a device object, IDs, resources, DMA mask, flags, bus/dev numbers, MSI fields, driver override, and IRQ-chip state. `struct cdx_driver` wraps driver model callbacks. APIs include `__cdx_driver_register()`, `cdx_driver_unregister()`, `cdx_dev_reset()`, `cdx_set_master()`, `cdx_clear_master()`, resource macros, conversion macros, and external `cdx_bus_type`.

**Control flow, state, persistence:** Controllers register, scan buses, create devices, and route configuration requests to controller ops. Drivers bind by ID table, probe/remove/shutdown, and receive reset notifications. Device enable/MSI/master state is runtime hardware/bus state.

**Dependencies/integration:** Depends on Linux device model, MSI/IRQ domains, module device tables, resources, debugfs, and DMA/IOMMU policy.

**Risks and test signals:** Risks include resource-count overflow, driver-override lifetime mistakes, MSI locking races, reset callback ordering, and bus-mastering/IOMMU policy errors. Test signals include CDX enumeration, driver bind/unbind, reset and MSI tests, DMA/IOMMU validation, and hot-remove/resource sysfs checks.
