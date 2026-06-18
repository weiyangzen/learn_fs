# sources/distributed-fs/ceph-client/include/soc/tegra/irq.h

## Purpose

`irq.h` exposes a Tegra ARM helper for detecting pending software-generated interrupts.

## Important APIs, Types, and Functions

When both `CONFIG_ARM` and `CONFIG_ARCH_TEGRA` are set, `tegra_pending_sgi()` is declared. Otherwise a static inline stub returns `false`.

## Control Flow

Callers can check for pending SGIs before entering idle or suspend-sensitive paths. Unsupported builds always report no pending SGI.

## State and Persistence

The header owns no state. The enabled implementation reads interrupt-controller state.

## Dependencies and Integration Points

It includes Linux types for `bool` and integrates with ARM Tegra idle, interrupt, and power-management code.

## Risks

The stubbed `false` result is safe for compilation but can mask missing platform support if a path assumes real SGI visibility.

## Test Signals

Test ARM Tegra builds, non-ARM builds, idle entry with pending SGIs, and interrupt wake behavior.
