<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/ebus_dma.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/ebus_dma.h

## Purpose
This header declares EBus DMA support for SPARC systems.

## Important APIs, Types, and Functions
It defines EBus DMA channel structures, callback/status definitions, and setup/control APIs used by EBus-attached devices.

## Control Flow
Drivers allocate/configure an EBus DMA channel, program transfer parameters, start/stop transfers, and receive completion/error status.

## State and Persistence Behavior
DMA channel state persists in driver structures and hardware registers while a channel is allocated.

## Dependencies and Integration Points
It integrates with EBus device drivers, interrupt handling, and SPARC DMA mapping.

## Risks
Channel lifecycle mistakes can leak DMA resources or leave devices bus-mastering after teardown.

## Test Signals
Run EBus device transfer tests, interrupt completion paths, and start/stop/error handling scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/ebus_dma.h -->
