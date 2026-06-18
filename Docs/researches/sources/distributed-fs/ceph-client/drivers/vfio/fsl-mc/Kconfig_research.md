# sources/distributed-fs/ceph-client/drivers/vfio/fsl-mc/Kconfig

## Purpose

This Kconfig file enables VFIO support for NXP/Freescale QorIQ DPAA2 Management Complex devices on the fsl-mc bus.

## Important APIs, Types, and Functions

`VFIO_FSL_MC` is a tristate option under a menu that depends on `FSL_MC_BUS`. It selects `EVENTFD` for interrupt delivery.

## Control Flow

When selected, Kbuild includes the fsl-mc VFIO driver so fsl-mc devices can be passed to userspace through VFIO.

## State and Persistence Behavior

Only build configuration state is represented.

## Dependencies and Integration Points

The option depends on the fsl-mc bus and maps to the fsl-mc Makefile. It also relies on VFIO core being enabled by the surrounding top-level Kconfig inclusion.

## Risks and Edge Cases

The feature is bus-specific and only useful when fsl-mc objects exist. Interrupt support assumes eventfd.

## Test Signals

Build with `FSL_MC_BUS` and `VFIO_FSL_MC` as module and built-in, and verify the resulting module links `vfio_fsl_mc.o` and `vfio_fsl_mc_intr.o`.
