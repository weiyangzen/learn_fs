# sources/distributed-fs/ceph-client/drivers/scsi/fcoe/libfcoe.h

## Purpose

`libfcoe.h` is a private debug header for the local libfcoe implementation. It declares `libfcoe_debug_logging` and defines category bits plus logging macros used by controller, sysfs, and transport code.

## Important APIs, types, and functions

Categories are `LIBFCOE_LOGGING`, `LIBFCOE_FIP_LOGGING`, `LIBFCOE_TRANSPORT_LOGGING`, and `LIBFCOE_SYSFS_LOGGING`. `LIBFCOE_CHECK_LOGGING()` conditionally executes a command. The `LIBFCOE_*_DBG()` macros format subsystem-specific printk prefixes.

## Control flow

No standalone flow exists. The macros expand inline and are gated by the runtime debug bitmask defined as a module parameter in `fcoe_transport.c`.

## State and persistence behavior

The header declares the global debug mask but stores no state itself. Logging configuration is runtime module state.

## Dependencies and integration points

The macros assume kernel logging helpers and valid FCoE controller/controller-device pointers for FIP and sysfs variants. Public libfcoe contracts come from `<scsi/libfcoe.h>`, not this local header.

## Risks and edge cases

Debug-only pointer dereferences can make bugs appear only when a logging bit is enabled. FIP receive logging can become noisy under packet load.

## Test signals

Compile all users and smoke-test each debug bitmask category while exercising transport, controller, and sysfs paths.
