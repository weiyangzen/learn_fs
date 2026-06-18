# sources/distributed-fs/ceph-client/drivers/cdx/controller/Makefile

## Purpose
This Makefile builds the CDX controller module/object from platform-controller, RPMsg transport, MCDI core, and MCDI helper sources.

## Important APIs, Types, and Functions
The target is `cdx-controller.o`, composed from `cdx_controller.o`, `cdx_rpmsg.o`, `mcdi.o`, and `mcdi_functions.o`.

## Control Flow
Kbuild includes the aggregate object when `CONFIG_CDX_CONTROLLER` is enabled. The combined object registers the platform driver and RPMsg driver pieces needed for the controller.

## State and Persistence Behavior
No runtime state exists in this file. It controls link composition and therefore which internal symbols are available in one module.

## Dependencies and Integration Points
It is reached from `drivers/cdx/Makefile` when the bus subtree is built. The object imports CDX bus controller namespace symbols from the bus core.

## Risks
All four sources are tightly coupled; omitting any object breaks probe, RPMsg transport, or firmware RPC wrappers. Link-order issues are minimal because the files communicate through normal C symbols.

## Test Signals
Build `CONFIG_CDX_CONTROLLER=y` and `=m`; verify `cdx-controller` contains the platform driver, RPMsg driver, MCDI RPC engine, and helper wrappers.
