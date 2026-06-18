# sources/distributed-fs/ceph-client/samples/vfio-mdev/Makefile

## Purpose

This Kbuild file builds mediated-device VFIO sample modules for serial and display devices.

## Important APIs, Types, and Functions

It maps configs to objects: `mtty.o`, `mdpy.o`, `mdpy-fb.o`, and `mbochs.o`.

## Control Flow

Kbuild includes each sample object when its `CONFIG_SAMPLE_VFIO_MDEV_*` symbol is enabled.

## State and Persistence Behavior

Only build outputs are affected.

## Dependencies and Integration Points

The modules integrate with VFIO, mediated devices, PCI-like emulation, framebuffer, and DMA-BUF depending on the selected sample.

## Risks and Edge Cases

These samples depend on VFIO/mdev APIs that can change; Kconfig must provide the required dependencies.

## Test Signals

Enable the sample configs and verify all selected modules build.
