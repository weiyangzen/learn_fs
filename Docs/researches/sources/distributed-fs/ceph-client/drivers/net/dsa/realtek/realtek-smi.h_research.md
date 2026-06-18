# sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/realtek-smi.h

## Purpose

This header provides conditional wrappers and declarations for the Realtek SMI platform transport driver, letting chip drivers compile whether or not SMI support is enabled.

## Important APIs, Types, and Functions

- With `CONFIG_NET_DSA_REALTEK_SMI` enabled, `realtek_smi_driver_register()` and `_unregister()` wrap platform driver registration, and probe/remove/shutdown are declared.
- With SMI disabled, registration is a no-op success, probe returns `-ENOENT`, and remove/shutdown are empty stubs.

## Control Flow

The enabled inline wrappers call the platform driver core. Disabled wrappers allow common chip-driver init/exit code to call transport registration functions without conditional compilation at each call site.

## State and Persistence

No state is stored by this header. Enabled wrappers affect global platform-driver registration; disabled wrappers have no runtime effect.

## Dependencies and Integration Points

It integrates chip drivers with the platform bus and Kconfig-controlled SMI availability. It expects `struct platform_driver` and `struct platform_device` to be visible in users.

## Risks and Edge Cases

Disabled registration returning 0 can make "no SMI transport registered" look like success to simple init code; this is intentional for multi-transport chip drivers but must be understood in diagnostics. Probe's `-ENOENT` stub should not be treated as a hardware probe failure in disabled builds.

## Test Signals

Compile chip drivers with SMI enabled and disabled. Enabled builds should register a platform driver and bind OF nodes; disabled builds should link through stubs and not expose an SMI transport.
