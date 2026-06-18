# sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/dma.c

## Purpose

`dma.c` implements R-Car audio DMA integration. It supports normal DMAEngine transfers between memory and a module, Audio-DMAC peri-peri transfers between hardware modules, DMA address calculation for Gen2/Gen4, DMA channel discovery from DT, and fallback signaling to PIO when DMA cannot be used.

## Important APIs, types, and functions

`struct rsnd_dma_ctrl` stores Audio-DMAC PP MMIO state and allocation counters. `struct rsnd_dma` is a synthetic module carrying source/destination modules and DMA addresses plus mode-specific state. `rsnd_dma_probe()` creates the controller for Gen2+ and maps `audmapp` unless Gen4. `rsnd_dma_attach()` allocates and connects an `AUDMA` or `AUDMAPP` module. `rsnd_dma_alloc()` chooses normal vs peri-peri DMA based on whether both endpoints are hardware modules. `rsnd_dma_of_path()` derives the adjacent transfer endpoints from the stream's SSI/SRC/CTU/MIX/DVC chain. `rsnd_dma_request_channel()` walks DT child nodes by fixed index and requests named DMA channels. `rsnd_dmaen_*` implements DMAEngine open/config/start/stop/pointer; `rsnd_dmapp_*` programs peri-peri registers.

## Control Flow

Submodules request DMA attachment during their probe callbacks. The DMA layer first determines the logical path, chooses Audio-DMAC PP for hardware-to-hardware links and DMAEngine for memory-facing links, initializes a synthetic `rsnd_mod`, then runs the relevant attach path. Normal DMA probes channel availability early, records the DMA device for IPMMU-aware buffer allocation, releases the probe channel, and opens a real channel later in `.prepare` because DMAEngine channel operations may sleep. At stream start, normal DMA configures source/destination bus addresses and widths before triggering DMAEngine; peri-peri DMA writes source, destination, and channel control registers directly.

## State and Persistence Behavior

The controller tracks monotonically allocated DMA IDs. Each stream keeps a pointer to its DMA module in `io->dma`. Normal DMA keeps the live DMAEngine channel only between prepare and cleanup; cleanup releases it outside the trigger spinlock. Peri-peri DMA keeps fixed PP ID and CHCR values. DMA addresses are computed once during allocation from SoC base physical addresses and module IDs.

## Dependencies and Integration Points

The file depends on OF DMA, DMAEngine PCM helpers, module DMA request callbacks from SSI/SSIU/SRC/DVC, generation base addresses from `gen.c`, and common stream/module helpers from `core.c`. It feeds ASoC pointer and trigger behavior through synthetic module ops in the same lifecycle sequence as hardware blocks.

## Risks and Test Signals

Risks include fragile Gen2 address formulas, unsupported SSI9 BUSIF4-7, Gen4 non-SSI0 rejection, sleeping DMAEngine APIs accidentally called under spinlock, channel-name mismatches, and fallback not correctly reconnecting SSI-only PIO paths. Tests should cover DMA and PIO fallback probe, memory-to-SSI, memory-to-SRC-to-SSI, SRC-to-DVC peri-peri links, capture and playback address selection, mono bus-width selection, and DMA pointer progression.
