<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mmp_tdma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/mmp_tdma.c

## Purpose
DMAEngine driver for Marvell two-channel DMA blocks, mainly cyclic slave DMA for audio/SQU-style peripherals.

## Important APIs, Types, And Functions
`mmp_tdma_device` owns two `mmp_tdma_chan` entries and a DMAEngine device. `mmp_tdma_chan` tracks register base, SRAM descriptor array, direction, peripheral address, burst/bus width, status, cyclic buffer geometry, and a reusable `dma_async_tx_descriptor`. `mmp_tdma_config_chan` programs TDCR for ADMA or PXA910 SQU variants. `mmp_tdma_prep_dma_cyclic` allocates descriptors from an SRAM gen_pool and chains periods into a ring. `mmp_tdma_tx_status` reports residue from current hardware position.

## Control Flow
Probe identifies the variant from DT, maps MMIO, obtains an `asram` gen_pool for descriptors, requests either shared or per-channel IRQs, initializes two channels, configures DMAEngine cyclic slave callbacks, registers DMAEngine, and registers OF DMA xlate. Resource allocation initializes the reusable descriptor and optionally requests per-channel IRQ. Prep validates slave direction, idle status, and period size, writes channel config, allocates a descriptor array, fills source/destination/next fields for each period, enables interrupts if requested, and returns the reusable descriptor. Submit immediately writes the descriptor physical address to TDNDPR and fetches it. Issue-pending sets channel enable. IRQ clears completion and schedules a tasklet, which invokes the descriptor callback. Pause/resume toggle channel enable; terminate aborts and disables IRQ.

## State And Persistence
State is stored in the channel descriptor array allocated from on-chip SRAM, the descriptor physical address, channel status, current position, buffer/period lengths, slave config, and TDMA registers. `descriptor_reuse` is enabled, so the same descriptor object represents the cyclic stream.

## Dependencies And Integration Points
Depends on DMAEngine, OF DMA, platform IRQ/MMIO resources, `gen_pool` SRAM named `asram`, and compatible strings `marvell,adma-1.0` and `marvell,pxa910-squ`. Clients select channels by one DT argument through a filter function.

## Risks And Edge Cases
`mmp_tdma_tx_submit` returns cookie 0 and does not use normal cookie assignment, which is unusual for DMAEngine clients. The file calls `dmaenginem_async_device_register`, which appears to be a misspelling of `dmaengine_async_device_register` unless a local compatibility macro exists elsewhere. Prep does not explicitly validate `buf_len % period_len`, so a partial final period is silently ignored by `num_periods = buf_len / period_len`. Descriptor memory requires an `asram` pool. Residue position logic assumes channel 0 reads source position and channel 1 reads destination position.

## Test Signals
Build coverage should verify the registration symbol typo. Runtime tests should cover cyclic playback/capture on both variants, callback cadence per period, pause/resume/terminate, residue over wrap, OF xlate channel selection, and failure when `asram` is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mmp_tdma.c -->
