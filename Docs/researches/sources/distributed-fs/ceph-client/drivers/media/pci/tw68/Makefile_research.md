
# sources/distributed-fs/ceph-client/drivers/media/pci/tw68/Makefile

## Purpose
This Makefile defines the TW68 composite module.

## Important APIs, Types, And Functions
`tw68-objs` links `tw68-core.o`, `tw68-video.o`, and `tw68-risc.o`. `obj-$(CONFIG_VIDEO_TW68) += tw68.o` connects the module to the selected config symbol.

## Control Flow
There is no runtime flow; Kbuild uses the object list to construct the driver.

## State And Persistence
The file contains only build metadata.

## Dependencies And Integration Points
The object split mirrors core PCI/IRQ/probe logic, V4L2/vb2 video handling, and RISC DMA program generation.

## Risks
Any new cross-file symbol implementation must be added here or link failures will occur. Removing `tw68-risc.o` would break buffer preparation.

## Test Signals
Build with `CONFIG_VIDEO_TW68=m` and check that all three object files are included in the linked module.
