# sources/distributed-fs/ceph-client/drivers/gpib/lpvo_usb_gpib/Makefile

## Purpose

This Kbuild fragment builds the LPVO USB GPIB driver when `CONFIG_GPIB_LPVO` is enabled.

## Important APIs and Targets

- `obj-$(CONFIG_GPIB_LPVO) += lpvo_usb_gpib.o` compiles the USB/GPIB adapter driver object.

## Control Flow and Integration

The parent GPIB Makefile includes this fragment. The resulting object registers a USB driver and conditionally registers a gpib interface when USB devices are present.

## State and Persistence Behavior

No runtime state exists in the Makefile.

## Dependencies

The build depends on `CONFIG_GPIB_LPVO`, USB support, linux-gpib core headers, and `lpvo_usb_gpib.c`.

## Risks and Test Signals

Build tests should cover enabled/disabled config. Since the source has an empty USB ID table by default, build success is separate from automatic device binding.
