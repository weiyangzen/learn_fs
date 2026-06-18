# sources/distributed-fs/ceph-client/include/dt-bindings/dma/sun4i-a10.h

## Purpose
Defines Allwinner sun4i A10 DMA endpoint class constants. The header comment explains the two hardware channel categories.

## Important APIs, Types, and Constants
Exports `SUN4I_DMA_NORMAL` 0 and `SUN4I_DMA_DEDICATED` 1. Normal DMA channels handle memory-to-memory and some simple peripheral cases; dedicated channels cover broader peripheral use as described by the binding.

## Control Flow and State
No executable flow. Runtime allocation and transfer state live in the sun4i DMA controller driver.

## Dependencies and Integration Points
Self-contained header used by sun4i DT DMA specifiers and controller/client nodes.

## Risks and Test Signals
Using the wrong channel class can make a client request unsupported hardware resources. Test signals include schema validation and DMA client tests for peripherals that require normal versus dedicated channels.
