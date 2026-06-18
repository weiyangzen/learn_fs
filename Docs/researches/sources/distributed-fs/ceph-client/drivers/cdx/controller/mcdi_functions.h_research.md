# sources/distributed-fs/ceph-client/drivers/cdx/controller/mcdi_functions.h

## Purpose
This header declares the typed MCDI helper API used by the CDX controller to enumerate and control CDX buses/devices.

## Important APIs, Types, and Functions
It declares bus enumeration (`cdx_mcdi_get_num_buses`, `cdx_mcdi_get_num_devs`), device configuration (`cdx_mcdi_get_dev_config`), bus state (`cdx_mcdi_bus_enable`, `cdx_mcdi_bus_disable`), MSI programming (`cdx_mcdi_write_msi`, `cdx_mcdi_msi_enable`), device reset (`cdx_mcdi_reset_device`), and bus mastering (`cdx_mcdi_bus_master_enable`).

## Control Flow
`cdx_controller.c` calls these functions from its scan path and `dev_configure`/bus callbacks. Each function synchronously issues one or more MCDI RPCs.

## State and Persistence Behavior
No state is defined here. The functions either return counts/status or populate caller-provided `struct cdx_dev_params`.

## Dependencies and Integration Points
The header includes Linux MCDI types, protocol constants, and the private CDX bus header. It is the typed API boundary between controller policy and generic RPC framing.

## Risks
Because helpers are synchronous and may sleep, callers must stay in process context. The API exposes only simple return codes, so richer firmware retry guidance such as `EAGAIN` generation-change handling must be implemented by callers if needed.

## Test Signals
Compile-time checks should ensure declarations match implementations. Controller tests should observe each declared helper being invoked for scan, reset, bus master, MSI enable, and MSI message programming paths.
