# sources/distributed-fs/ceph-client/drivers/dma/mxs-dma.c

## Purpose
`mxs-dma.c` is a Freescale/NXP MXS APBH/APBX dmaengine slave and cyclic DMA controller driver for i.MX23 and i.MX28 style SoCs. It programs command-chain words (CCWs) in coherent memory and exposes channels through device tree DMA translation.

## Important APIs, Types, and Functions
- `struct mxs_dma_ccw` is the hardware command descriptor: next pointer, command bits, transfer byte count, buffer address, and optional PIO words.
- `struct mxs_dma_chan` stores one dmaengine channel, its tasklet, IRQ, coherent CCW block, status, flags for SG loop/semaphore mode, and reset state.
- `struct mxs_dma_engine` stores controller type/id, base registers, clock, `dma_device`, channel array, platform device, and number of channels.
- `mxs_dma_reset_chan()`, `mxs_dma_enable_chan()`, `mxs_dma_pause_chan()`, and `mxs_dma_resume_chan()` perform per-channel hardware control.
- `mxs_dma_prep_slave_sg()` emits linear or appended CCW chains and supports a special `DMA_TRANS_NONE` PIO-register programming mode.
- `mxs_dma_prep_dma_cyclic()` creates a circular CCW list with semaphore handling for audio-like cyclic transfers.
- `mxs_dma_int_handler()` handles completion and error interrupts, updates status, replenishes cyclic semaphores, completes cookies, and schedules callbacks.
- `mxs_dma_xlate()` maps a one-cell DT specifier to a DMA channel and records the per-channel IRQ.

## Control Flow
Probe reads `dma-channels`, selects APBH/APBX and i.MX23/i.MX28 behavior from OF match data, maps registers, gets a clock, initializes all 16 possible channel objects, resets/enables the controller block, registers dmaengine callbacks, and registers an OF DMA controller. Channel resource allocation allocates one 4-page coherent CCW block, requests the channel IRQ, enables the clock, resets the channel, and initializes a single reusable async descriptor. Prepare calls fill the CCW array and set channel status to `DMA_IN_PROGRESS`. `device_issue_pending` points hardware at the CCW block and increments the channel semaphore to start execution. IRQ handling clears completion/error bits, resets on real errors, keeps cyclic loops running by adding semaphore credits, completes cookies for non-reset complete transfers, and schedules the tasklet callback.

## State and Persistence
The driver keeps no persistent storage. Runtime state is split between the coherent CCW block, APBH/APBX channel registers, channel status, `desc_count`, flags, and cookies. Cyclic transfers maintain a circular command chain and depend on semaphore credits instead of resetting the channel. Controller initialization resets the block, enables APBH burst modes, and enables interrupts for all channels.

## Dependencies and Integration Points
The driver depends on platform resources, clocks, `stmp_reset_block()`, device tree compatibles (`fsl,imx23-dma-apbh`, `fsl,imx23-dma-apbx`, `fsl,imx28-dma-apbh`, `fsl,imx28-dma-apbx`), `linux/dma/mxs-dma.h` flag definitions, and the dmaengine slave/cyclic APIs. It registers an OF xlate function that expects one argument: channel id.

## Risks and Edge Cases
- This local source calls `dmaenginem_async_device_register(&mxs_dma->dma_device)`, which appears to be a misspelling of the normal `dma_async_device_register()` API and is a compile-time risk unless the tree carries a compatibility macro.
- The driver uses one reusable `dma_async_tx_descriptor` per channel, so overlapping independent submissions are constrained and rely on the intended MXS command-chain usage.
- `DMA_TRANS_NONE` treats `sgl` as a raw `u32 *` PIO-word source, so callers must obey the private contract exactly.
- i.MX28 APBX reset avoids READ_FLUSH for up to 50 ms; timeout only logs and proceeds with reset, which can still be risky on affected hardware.
- The cyclic residue calculation uses the last CCW address plus length minus the BAR register and is specific to the circular layout.

## Test Signals
Build coverage with the target config should catch the registration-name issue. Runtime signals include OF channel requests for valid and invalid channel ids, slave SG transfers at `MAX_XFER_BYTES` boundaries, cyclic audio-style transfers with semaphore replenishment, pause/resume behavior, termination during cyclic mode, and error IRQ paths that distinguish termination-with-completion from real bus errors.
