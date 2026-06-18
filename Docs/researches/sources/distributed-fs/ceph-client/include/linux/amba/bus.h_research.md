<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/amba/bus.h -->
# sources/distributed-fs/ceph-client/include/linux/amba/bus.h

## Purpose
`amba/bus.h` defines the Linux AMBA/PrimeCell bus abstraction, device and driver structures, registration helpers, and convenience macros for APB/AHB AMBA devices.

## Important APIs, types, and functions
Constants include `AMBA_NR_IRQS`, `AMBA_CID`, and `CORESIGHT_CID`. `struct amba_cs_uci_id` represents CoreSight unique component identifiers. `struct amba_device` embeds `struct device`, resource, pclk, DMA parameters, periphid/cid, IRQs, UCI, and driver override. `struct amba_driver` wraps `device_driver`, probe/remove/shutdown callbacks, ID table, and managed-DMA flag. APIs include driver register/unregister, `dev_is_amba()`, device alloc/put/add/register/unregister, region request/release, and module/builtin driver macros. Field macros extract config, revision, manufacturer, and part IDs.

## Control flow
AMBA devices are allocated/registered with resources and IDs. The bus matches drivers by AMBA ID/UCI data, calls probe/remove/shutdown, and manages regions/clocks/devices through standard driver core paths.

## State and persistence behavior
Each `amba_device` is persistent device-core state. Driver override strings are core-owned when set through proper APIs. Registered drivers persist on `amba_bustype`.

## Dependencies and integration points
It depends on clocks, device core, resources, regulators, module infrastructure, mod_devicetable, and DMA/IOMMU handling. It integrates ARM PrimeCell, CoreSight, APB/AHB static device declarations, and driver modules.

## Risks and test signals
Risks include invalid CID/periphid matching, direct writes to `driver_override`, DMA mask mistakes for APB/AHB, and config-disabled stubs returning `-EINVAL`. Test signals include AMBA driver probe/remove, CoreSight UCI matching, static APB/AHB device registration, region conflicts, and builds without `CONFIG_ARM_AMBA`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/amba/bus.h -->
