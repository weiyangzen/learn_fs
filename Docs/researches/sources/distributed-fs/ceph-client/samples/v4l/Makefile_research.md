# sources/distributed-fs/ceph-client/samples/v4l/Makefile

## Purpose

This Kbuild fragment builds the V4L2 PCI skeleton sample driver.

## Important APIs, Types, and Functions

It maps `obj-$(CONFIG_VIDEO_PCI_SKELETON) := v4l2-pci-skeleton.o`.

## Control Flow

Kbuild compiles the sample when the video skeleton config is enabled.

## State and Persistence Behavior

No runtime state is created by the Makefile.

## Dependencies and Integration Points

The source depends on PCI, V4L2, controls, events, and videobuf2 DMA-contig APIs.

## Risks and Edge Cases

Kconfig must select the relevant media dependencies.

## Test Signals

Enable `CONFIG_VIDEO_PCI_SKELETON` and verify the module builds.
