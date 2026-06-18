# sources/distributed-fs/ceph-client/drivers/vfio/fsl-mc/Makefile

## Purpose

This Makefile builds the VFIO driver for fsl-mc bus devices.

## Important APIs, Types, and Functions

`vfio-fsl-mc-y := vfio_fsl_mc.o vfio_fsl_mc_intr.o` composes the module, and `obj-$(CONFIG_VFIO_FSL_MC) += vfio-fsl-mc.o` enables it.

## Control Flow

Kbuild links the main fsl-mc VFIO implementation with its interrupt helper when `CONFIG_VFIO_FSL_MC` is enabled.

## State and Persistence Behavior

No runtime state exists here.

## Dependencies and Integration Points

The file ties the Kconfig symbol to the two implementation objects and uses dual GPL/BSD SPDX metadata.

## Risks and Edge Cases

Object list drift would break symbols between `vfio_fsl_mc.c` and `vfio_fsl_mc_intr.c`.

## Test Signals

Compile `CONFIG_VFIO_FSL_MC=y` and `m` to verify object composition and exported internal helper resolution.
