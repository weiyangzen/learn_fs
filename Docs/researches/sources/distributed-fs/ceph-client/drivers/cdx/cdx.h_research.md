# sources/distributed-fs/ceph-client/drivers/cdx/cdx.h

## Purpose
This private CDX bus header defines the controller-to-bus handoff structure and declares internal bus/controller integration APIs.

## Important APIs, Types, and Functions
`struct cdx_dev_params` carries all data needed to instantiate a `struct cdx_device`: controller pointer, parent bus device, IDs, bus/device numbers, resource array, resource count, requester ID, class, revision, MSI device ID, and MSI count. Declared functions are `cdx_register_controller()`, `cdx_unregister_controller()`, `cdx_device_add()`, `cdx_bus_add()`, and `cdx_msi_domain_init()`.

## Control Flow
Controller drivers fill `cdx_dev_params` from firmware enumeration, then call `cdx_device_add()`. They call `cdx_bus_add()` before adding child devices and register/unregister themselves through the controller APIs.

## State and Persistence Behavior
The header owns no state. Its structure layout defines the transient parameter contract copied into persistent `cdx_device` objects by `cdx_device_add()`.

## Dependencies and Integration Points
It includes `<linux/cdx/cdx_bus.h>` for public CDX types and constants such as `MAX_CDX_DEV_RESOURCES`. It is included by bus core, MSI support, and controller code.

## Risks
This header is a narrow ABI inside the CDX subsystem: field mismatches between firmware decode and bus object population can misidentify devices, expose wrong MMIO resources, or configure DMA/MSI with incorrect requester IDs. The documentation typo `@us_num` for `cdx_bus_add()` is harmless but can confuse generated docs.

## Test Signals
Compile all CDX objects together, then validate that firmware-provided IDs/resources/MSI counts appear correctly in sysfs, resource files, DMA configuration, and MSI domain setup.
