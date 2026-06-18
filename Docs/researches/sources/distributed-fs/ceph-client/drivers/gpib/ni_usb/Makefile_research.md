# sources/distributed-fs/ceph-client/drivers/gpib/ni_usb/Makefile

## Purpose

This Kbuild fragment builds the National Instruments USB GPIB driver when `CONFIG_GPIB_NI_USB` is enabled.

## Important APIs and Targets

- `obj-$(CONFIG_GPIB_NI_USB) += ni_usb_gpib.o` compiles the NI USB GPIB driver object.

## Control Flow and Integration

The fragment is included by the parent GPIB driver build. Although only the Makefile is in this work item, the object name shows the corresponding implementation is `ni_usb_gpib.c`.

## State and Persistence Behavior

No runtime state exists in the Makefile.

## Dependencies

The target depends on `CONFIG_GPIB_NI_USB` and the presence of `ni_usb_gpib.c` plus kernel USB/GPIB dependencies.

## Risks and Test Signals

Build tests should verify enabled/disabled config paths and module dependency resolution. Runtime risks belong to `ni_usb_gpib.c`, not this Makefile.
