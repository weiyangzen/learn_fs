# sources/distributed-fs/ceph-client/drivers/dma/idma64.h

## Purpose
`idma64.h` defines the Intel iDMA64 private register map, bitfields, linked-list descriptors, channel/controller structures, and MMIO helpers.

## Important APIs, Types, And Functions
Important pieces are channel offsets for SAR/DAR/LLP/CTL/CFG, interrupt register macros, `idma64_lli`, `idma64_hw_desc`, `idma64_desc`, `idma64_chan`, `idma64`, and `idma64_chip`. Helpers wrap 32-bit and lo-hi 64-bit MMIO.

## Control Flow
No standalone flow exists; `idma64.c` uses these definitions for descriptor allocation, register programming, interrupt masking/clearing, and platform resource handoff.

## State And Persistence Behavior
LLIs are DMA-visible runtime state. `idma64_chip` bridges platform resources into the core. No persistent storage is defined.

## Dependencies And Integration Points
It depends on Linux I/O, `io-64-nonatomic-lo-hi`, `virt-dma`, and the public `linux/dma/idma64.h` naming contract.

## Risks And Test Signals
Descriptor chaining requires final LLP bits to be cleared, and burst/width fields require encoded values. Validate compile coverage, sparse checks, chained SG DMA, and residue behavior.
