
# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/mipi-csi2/Makefile

## Purpose

This Makefile maps the C3 MIPI CSI-2 Kconfig symbol to its driver object. It is the only build directive needed for the single-file receiver driver.

## Important APIs, Types, And Functions

There are no C interfaces. The relevant Kbuild line is `obj-$(CONFIG_VIDEO_C3_MIPI_CSI2) += c3-mipi-csi2.o`.

## Control Flow

Kbuild includes `c3-mipi-csi2.o` as built-in, module, or not at all depending on whether `CONFIG_VIDEO_C3_MIPI_CSI2` is `y`, `m`, or unset.

## State And Persistence

The Makefile has no runtime state. Build outputs reflect the kernel configuration.

## Dependencies And Integration Points

The file integrates with the same directory's Kconfig and the parent platform media build. It assumes all CSI-2 receiver code remains in `c3-mipi-csi2.c`.

## Risks

Future source splits require Makefile updates. Otherwise, risk is low because the object and Kconfig symbol names match directly.

## Test Signals

Build with `CONFIG_VIDEO_C3_MIPI_CSI2=m` and confirm a module object is produced. Disable the symbol and verify the object is omitted.
