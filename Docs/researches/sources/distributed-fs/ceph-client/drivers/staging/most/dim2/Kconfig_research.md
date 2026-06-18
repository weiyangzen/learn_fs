# sources/distributed-fs/ceph-client/drivers/staging/most/dim2/Kconfig

## Purpose
Adds configuration for the MOST DIM2 MediaLB hardware dependent module.

## Important APIs, Types, And Functions
`MOST_DIM2` is a tristate named `DIM2`, depending on `HAS_IOMEM` and `OF`. Help text states it connects via MediaLB to a network transceiver and builds module `most_dim2`.

## Control Flow
Build-time selection controls whether the DIM2 platform driver and HAL are compiled.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Requires MMIO and device-tree support, and is included under `MOST_COMPONENTS`.

## Risks And Test Signals
The driver also uses DMA, interrupts, clocks, and MOST core APIs via parent dependencies. Test signals are DT-based build coverage and module probe with supported compatibles.
