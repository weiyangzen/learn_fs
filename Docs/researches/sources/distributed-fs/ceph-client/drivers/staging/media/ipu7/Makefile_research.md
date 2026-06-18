# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/Makefile

## Purpose

This Makefile defines the IPU7 object split: a base PCI/bus/boot/DMA/MMU/buttress/CPD/syscom module and a separate ISYS media capture module.

## Important APIs, Types, and Functions

`intel-ipu7-objs` contains `ipu7.o`, bus, DMA, MMU, buttress, CPD, syscom, and boot objects. `intel-ipu7-isys-objs` contains ISYS, CSI2, CSI PHY, firmware ISYS, video, queue, and subdevice objects. Both modules are built from `CONFIG_VIDEO_INTEL_IPU7`.

## Control Flow

There is no runtime flow; object lists define link composition and symbol ownership.

## State and Persistence Behavior

No runtime state is owned here. Build output creates two modules that cooperate through exported `INTEL_IPU7` namespace symbols.

## Dependencies and Integration Points

The base module provides infrastructure used by the ISYS module: bus devices, DMA helpers, boot, syscom, and buttress controls. The ISYS module depends on these exports to initialize firmware and media entities.

## Risks and Edge Cases

Missing an object can lead to unresolved namespace exports or runtime feature absence. Because both modules key off one Kconfig symbol, load ordering and symbol namespaces matter.

## Test Signals

Module build/link tests and `modpost` namespace checks are the primary signals, followed by loading `intel_ipu7` and `intel_ipu7_isys` together.
