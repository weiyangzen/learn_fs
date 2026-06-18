# sources/distributed-fs/ceph-client/drivers/cdx/cdx_msi.c

## Purpose
This file provides CDX MSI support. It creates a CDX-specific MSI irq domain layered over a parent ITS/MSI domain and forwards MSI message programming and enable/disable operations to controller firmware.

## Important APIs, Types, and Functions
Exported APIs are `cdx_enable_msi()`, `cdx_disable_msi()`, and `cdx_msi_domain_init()`. The IRQ chip is `cdx_msi_irq_chip`, with parent mask/unmask/eoi, affinity support, and deferred `irq_write_msi_msg` handling. Domain callbacks are `cdx_msi_prepare()` and `cdx_msi_set_desc()`.

## Control Flow
When a CDX device probes, the bus core can call `msi_setup_device_data()` if the controller has `msi_domain`. During allocation, `cdx_msi_prepare()` maps the device's `msi_dev_id` through the controller node's `msi-map` into a parent device ID and calls the parent MSI domain prepare callback. `cdx_msi_write_msg()` stores the message in the MSI descriptor and marks the CDX device pending; `irq_bus_sync_unlock()` later programs firmware through `dev_configure(CDX_DEV_MSI_CONF)`.

## State and Persistence Behavior
Per-device state includes `msi_write_pending`, `irqchip_lock`, `num_msi`, `msi_dev_id`, and the generic MSI descriptors. MSI enable state and message routing live in controller firmware/hardware after `cdx_enable_msi()`, `cdx_disable_msi()`, or message writes.

## Dependencies and Integration Points
It depends on OF `msi-map`, irqdomain, generic MSI core, parent domain operations, GIC ITS-like parent domains, and CDX controller `dev_configure()` support. The bus core attaches the resulting domain to CDX devices.

## Risks
Message writes are intentionally deferred so sleeping controller firmware calls do not happen under the MSI core's low-level write callback; missing the bus unlock path would leave firmware unprogrammed. `cdx_msi_prepare()` assumes the parent MSI domain has valid `msi_domain_info` and an `msi_prepare` op. Incorrect `msi-map` entries or mismatched `msi_dev_id` break interrupt delivery. `cdx_msi_write_irq_unlock()` clears pending before calling firmware and does not report errors to the MSI core.

## Test Signals
Validate `msi-map` parsing, domain creation, MSI allocation/free, message programming callbacks, interrupt delivery from CDX devices, affinity changes, enable/disable sequencing, and behavior when firmware `dev_configure()` fails.
