# sources/distributed-fs/ceph-client/drivers/net/ethernet/google/gve/gve_register.h

## Purpose

`gve_register.h` defines the fixed MMIO register block and status-bit contract used by the driver to communicate with the virtual NIC outside descriptor rings and adminq memory.

## Important APIs, types, and constants

- `struct gve_registers`: BAR0 layout for device status, driver status, max queue counts, adminq PFN/doorbell/event-counter/base/length fields, and byte-wide driver version write sink.
- `enum gve_device_status_flags`: reset request, link status, report-stats request, and device-is-reset bits.
- `enum gve_driver_status_flags`: driver run and reset bits.

## Control flow and state

The structure maps hardware registers; it owns no driver memory. `gve_probe()` maps BAR0, writes the version string to `driver_version`, reads max queue counts to size the netdev, and stores the mapped pointer in `priv->reg_bar0`. `gve_service_task()` reads `device_status` to handle reset, report-stats, and link-state events. Adminq setup code uses the adminq fields.

## Dependencies and integration points

The file depends on endian integer types and `BIT`. `gve_main.c` is the visible consumer for queue sizing and service-task status handling. `gve_adminq.c` uses the adminq register fields to publish queue memory and ring the adminq doorbell.

## Risks and test signals

Risks are MMIO layout drift, endian mistakes, reading stale status without appropriate ordering in surrounding code, and writing driver status bits incorrectly during reset. Tests should cover probe queue-count reads, status-triggered reset/report-stats/link handling, adminq initialization, and device reset detection.
