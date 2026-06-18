# sources/distributed-fs/ceph-client/samples/vfio-mdev/mdpy-defs.h

## Purpose

This header defines the simple virtual PCI display device ABI used by the `mdpy` mediated display and its framebuffer driver.

## Important APIs, Types, and Functions

It defines PCI vendor/device/subsystem ids and vendor capability offsets: `MDPY_VENDORCAP_OFFSET`, `MDPY_VENDORCAP_SIZE`, `MDPY_FORMAT_OFFSET`, `MDPY_WIDTH_OFFSET`, and `MDPY_HEIGHT_OFFSET`.

## Control Flow

There is no executable control flow. Producers write these config-space fields, and `mdpy-fb.c` reads them during PCI probe.

## State and Persistence Behavior

The constants describe config-space state exposed by the virtual PCI device.

## Dependencies and Integration Points

It depends on PCI id constants and DRM fourcc values used by the driver code.

## Risks and Edge Cases

Changing offsets or IDs breaks compatibility between the virtual device and framebuffer driver.

## Test Signals

Verify `mdpy-fb.c` matches devices using the IDs and reads format/width/height from the declared offsets.
