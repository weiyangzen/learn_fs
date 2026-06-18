# sources/distributed-fs/ceph-client/include/dt-bindings/dma/nbpfaxi.h

## Purpose
Defines NBPF AXI DMA slave request mode flags for DT bindings.

## Important APIs, Types, and Constants
Exports `NBPF_SLAVE_RQ_HIGH`, `NBPF_SLAVE_RQ_LOW`, and `NBPF_SLAVE_RQ_LEVEL` with bit values 1, 2, and 4. These describe active-high, active-low, and level-sensitive request semantics.

## Control Flow and State
No runtime flow. The DMA driver uses the flags when configuring handshake behavior.

## Dependencies and Integration Points
Self-contained binding included by DT nodes using the NBPF AXI DMA controller.

## Risks and Test Signals
Incorrect polarity or level configuration can prevent DMA requests or cause repeated service. Test signals include schema validation and peripheral DMA tests that verify handshake behavior.
