<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/apb.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/apb.h

## Purpose
This header describes SPARC APB (Advanced PCI Bridge) register layout used by platform PCI code.

## Important APIs, Types, and Functions
It defines APB register offsets and bit fields for bridge control/status, interrupt, and bus-facing configuration.

## Control Flow
Platform PCI/probing code includes the header and uses the constants when mapping and programming APB registers.

## State and Persistence Behavior
The header has no state; hardware register writes by users of these constants persist in the bridge until reset or reprogramming.

## Dependencies and Integration Points
It integrates with SPARC PCI host bridge support and low-level I/O accessors.

## Risks
Wrong masks or offsets can misconfigure PCI routing or interrupt behavior. Because this is hardware-facing, errors may appear as device enumeration failures.

## Test Signals
Boot APB-equipped systems, enumerate PCI devices, exercise interrupts and DMA, and compare register dumps against platform documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/apb.h -->
