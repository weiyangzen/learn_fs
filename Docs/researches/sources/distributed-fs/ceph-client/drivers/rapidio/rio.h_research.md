# sources/distributed-fs/ceph-client/drivers/rapidio/rio.h

## Purpose
Internal RapidIO core header shared by the core, scan, sysfs, and switch drivers. It declares non-public core helpers and exports the sysfs attribute group arrays used by bus/device registration.

## Important APIs, types, and functions
Defines `RIO_MAX_CHK_RETRY`, `RIO_MPORT_ANY`, `RIO_GET_DID(size, x)`, and `RIO_SET_DID(size, x)` for base versus extended destID encoding. Declares feature-walk helpers, device access checking, host lock/unlock, route add/get/clear, port lockout, component-tag lookup, net/device add/remove, RX/TX port enabling, scan registration, device attachment, and mport scan. Also declares `rio_dev_groups`, `rio_bus_groups`, and `rio_mport_groups`.

## Control flow
This file has no executable control flow. Its declarations define the private call graph used by `rio-scan.c`, `rio-sysfs.c`, `rio.c`, and `switches/*.c`. The destID macros centralize the conditional 8-bit or 16-bit packing used whenever code reads or writes `RIO_DID_CSR`.

## State and persistence
No state is stored here. The macros affect how hardware destination ID state is interpreted and written.

## Dependencies and integration
Includes `linux/device.h`, `linux/list.h`, and `linux/rio.h`. It is intentionally not a public userspace ABI; it links internal compilation units in the RapidIO subsystem.

## Risks
The prototypes must stay synchronized with implementations in `rio.c`; mismatches can cause build failures or subtle ABI changes for in-tree callers. Incorrect `RIO_GET_DID`/`RIO_SET_DID` use would corrupt destID programming in mixed 8-bit/16-bit systems.

## Test signals
Build coverage across RapidIO core and switch drivers, plus enumeration tests on both `sys_size` modes, are the main signals.
