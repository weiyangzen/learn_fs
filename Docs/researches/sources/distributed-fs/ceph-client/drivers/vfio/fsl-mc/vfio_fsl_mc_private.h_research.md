# sources/distributed-fs/ceph-client/drivers/vfio/fsl-mc/vfio_fsl_mc_private.h

## Purpose

This private header defines VFIO fsl-mc offset encoding, per-region/per-IRQ metadata, per-device state, and interrupt helper prototypes.

## Important APIs, Types, and Functions

`VFIO_FSL_MC_OFFSET_SHIFT` is 40, with macros to convert VFIO offsets to region indexes and indexes back to offsets. `struct vfio_fsl_mc_irq` stores eventfd trigger and IRQ name. `struct vfio_fsl_mc_region` stores VFIO flags, fsl-mc type bits, physical address, size, and lazy `ioaddr`. `struct vfio_fsl_mc_device` embeds `vfio_device` and stores `mc_dev`, notifier, regions, interrupt mutex, and IRQ array.

## Control Flow

The header has no runtime flow. It defines the shared interface between `vfio_fsl_mc.c` and `vfio_fsl_mc_intr.c`.

## State and Persistence Behavior

It defines transient in-kernel state. Region mappings and IRQ eventfds are allocated during open/IRQ setup and freed on close.

## Dependencies and Integration Points

It depends on fsl-mc and VFIO types through the including C files and declares interrupt setup/cleanup functions used by the main driver.

## Risks and Edge Cases

The offset shift must match mmap/read/write region-index decoding. Lazy `ioaddr` lifetime requires every mapped region to be unmapped in cleanup.

## Test Signals

Compile both implementation files together, validate offset/index conversions, and exercise lazy mapping cleanup for every region.
