# sources/distributed-fs/ceph-client/include/linux/via.h

## Purpose
This header defines VIA Super I/O parallel-port function and configuration register constants.

## Important APIs, types, and functions
It defines function values for SPP/ECP/EPP/disable/probe, parallel port capability bits, config index/data ports, and IRQ/DMA control register offsets.

## Control flow, state, and persistence
There is no executable flow. Platform or parport code writes these constants to VIA configuration ports to probe or set parallel-port mode and IRQ/DMA behavior. State is hardware register configuration.

## Dependencies and integration points
It integrates with VIA Super I/O and parallel-port setup code and has no header dependencies.

## Risks and test signals
Risks include writing the probe magic value to hardware as a real mode and using wrong config ports. Tests should validate probe/read/write sequences on supported chipsets or mocks.
