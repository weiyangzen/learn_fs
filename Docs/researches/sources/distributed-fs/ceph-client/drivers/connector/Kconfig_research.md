# sources/distributed-fs/ceph-client/drivers/connector/Kconfig

## Purpose
This Kconfig file defines build-time configuration for the kernel connector subsystem and its process-event producer.

## Important APIs, Types, And Functions
`menuconfig CONNECTOR` is a tristate option named "Connector - unified userspace <-> kernelspace linker" and depends on `NET`. `config PROC_EVENTS` is a bool option under `CONNECTOR`, depends on `CONNECTOR=y`, defaults to `y`, and enables process event reporting to userspace.

## Control Flow
Kconfig presents `PROC_EVENTS` only inside the connector menu. Because it depends on `CONNECTOR=y`, process events are available only when connector is built into the kernel, not when connector is a module.

## State And Persistence
No runtime state exists. The selections persist in kernel configuration and drive compiled objects.

## Dependencies And Integration Points
The file integrates with `drivers/connector/Makefile`, where `CONFIG_CONNECTOR` builds `cn.o` and `CONFIG_PROC_EVENTS` builds `cn_proc.o`.

## Risks And Edge Cases
The built-in-only dependency for `PROC_EVENTS` is important: enabling connector as a module does not allow process event support. The default `y` can expose process events whenever built-in connector is enabled.

## Test Signals
Configuration tests should confirm `CONNECTOR=n/m/y` object outcomes, `PROC_EVENTS` visibility only for built-in connector, and expected default selection behavior.
