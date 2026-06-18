# sources/distributed-fs/ceph-client/drivers/nubus/Makefile

## Purpose
Builds the NuBus core objects and optional procfs support.

## Important APIs, Types, And Functions
No runtime APIs. It always builds `nubus.o` and `bus.o`; it builds `proc.o` when `CONFIG_PROC_FS` is enabled.

## Control Flow
The kernel build system includes core NuBus scanning/resource code and bus registration code unconditionally for this directory, plus procfs helpers when configured.

## State And Persistence
Build-only state.

## Dependencies And Integration Points
Integrates with NuBus source files and `CONFIG_PROC_FS`.

## Risks And Edge Cases
No complex logic. Procfs resource exposure is compile-time optional.

## Test Signals
NuBus builds should include core bus support, and procfs symbols should resolve only when `CONFIG_PROC_FS=y`.
