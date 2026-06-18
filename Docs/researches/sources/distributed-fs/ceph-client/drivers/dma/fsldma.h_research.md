# sources/distributed-fs/ceph-client/drivers/dma/fsldma.h

## Purpose
`fsldma.h` defines the private hardware and software contract for the Freescale Elo DMA driver: register bits, descriptor layout, channel/controller structures, feature flags, and endian helpers.

## Important APIs, Types, And Functions
Key types are `fsl_dma_ld_hw`, `fsl_desc_sw`, `fsldma_chan_regs`, `fsldma_device`, and `fsldma_chan`. Feature flags encode big/little endian mode, 83xx/85xx IP family, and external pause/start state. `FSL_DMA_IN`, `FSL_DMA_OUT`, `DMA_TO_CPU`, and `CPU_TO_DMA` centralize endian conversion.

## Control Flow
The header has no standalone flow; `fsldma.c` uses it for register access, descriptor chain construction, channel probing, interrupt handling, and PM save/restore.

## State And Persistence Behavior
All modeled state is runtime-only. Hardware descriptors are DMA-visible and 32-byte aligned. Under `CONFIG_PM`, the header adds saved mode-register state and a suspend/running enum.

## Dependencies And Integration Points
It depends on dmaengine, DMA pools, device APIs, PPC/ARM MMIO helpers, and endian conversion APIs. The descriptor alignment, byte-count max, and link-address masks constrain transfer preparation.

## Risks And Test Signals
Wrong endian selection, link flag masking, or descriptor alignment can break hardware fetches. Validate with sparse/endian builds, PPC and ARM/ARM64 compile coverage, and runtime DMA on both endian feature paths.
