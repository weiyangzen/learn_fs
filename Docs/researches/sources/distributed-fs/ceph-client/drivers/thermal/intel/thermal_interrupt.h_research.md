# sources/distributed-fs/ceph-client/drivers/thermal/intel/thermal_interrupt.h

## Purpose

`thermal_interrupt.h` declares the shared x86 Intel thermal interrupt interfaces used by throttling, HFI, and package temperature drivers.

## Important APIs, Types, and Functions

It defines `CORE_LEVEL` and `PACKAGE_LEVEL`, declares platform threshold callback pointers, declares the rate-control callback, declares weak-overridable `notify_hwp_interrupt()`, and declares `thermal_clear_package_intr_status()`.

## Control Flow

There is no runtime flow in the header. It provides the common contract that lets independent drivers register callbacks and clear thermal status bits without circular includes.

## State and Persistence Behavior

The callback pointers are extern state defined in `therm_throt.c`. The header itself owns no storage.

## Dependencies and Integration Points

It integrates `x86_pkg_temp_thermal.c`, `intel_hfi.c`, and `therm_throt.c`. Core/package level constants must match the implementation's MSR selection.

## Risks and Test Signals

Risks include global callback pointer ownership, missing synchronization around callback updates, and callers passing incorrect level/bit masks. Test signals include builds of all users, package temp callback registration/removal, HFI status clear calls, and HWP override linkage.
