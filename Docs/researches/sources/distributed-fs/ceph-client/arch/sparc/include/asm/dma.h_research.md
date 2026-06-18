<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/dma.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/dma.h

## Purpose
This header defines SPARC legacy DMA constants, controller registers, and helper declarations.

## Important APIs, Types, and Functions
It includes DMA channel/controller definitions, address/count handling, and architecture-specific DMA limits used by old SBUS/ISA-style devices.

## Control Flow
Legacy drivers program DMA controllers through these constants and helpers before starting device transfers.

## State and Persistence Behavior
State resides in DMA controller hardware and driver-owned descriptors.

## Dependencies and Integration Points
It integrates with legacy floppy/SBUS/ISA-like devices and generic DMA definitions.

## Risks
Wrong count/address programming causes memory corruption. Legacy DMA limits may not match modern DMA API assumptions.

## Test Signals
Exercise floppy/legacy DMA devices, DMA API debug, and transfer boundary tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/dma.h -->
