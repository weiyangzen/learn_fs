# sources/distributed-fs/ceph-client/drivers/scsi/smartpqi/Makefile

## Purpose
Defines how the smartpqi driver is built from its component objects when `CONFIG_SCSI_SMARTPQI` is enabled.

## Important APIs, Types, And Functions
The key Kbuild variables are `obj-$(CONFIG_SCSI_SMARTPQI) += smartpqi.o` and `smartpqi-objs := smartpqi_init.o smartpqi_sis.o smartpqi_sas_transport.o`.

## Control Flow
Kbuild includes this directory Makefile from the SCSI driver build. If `CONFIG_SCSI_SMARTPQI=y`, the objects are linked into the kernel; if `m`, they are linked into `smartpqi.ko`; if unset, no smartpqi objects are built.

## State And Persistence Behavior
No runtime state exists. Build output state is limited to generated object files and the final built-in or module artifact.

## Dependencies And Integration Points
This file ties the Kconfig symbol to three implementation units: initialization/core controller logic, SIS/PQI mode transition support, and SAS transport integration. It depends on Kbuild conventions for composite objects.

## Risks
Adding a new implementation source without updating `smartpqi-objs` silently omits functionality. Incorrect object ordering can matter if initialization sections or symbol dependencies change. The Makefile is small, so most risk is integration drift relative to source files.

## Test Signals
Build `CONFIG_SCSI_SMARTPQI=y` and `m`, confirm all three objects are compiled and linked, inspect `smartpqi.ko` symbols when modular, and run dependency-only builds after adding or removing smartpqi source files.
