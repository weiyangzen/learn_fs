# sources/distributed-fs/ceph-client/drivers/dma/owl-dma.c

## Purpose
`owl-dma.c` is the Actions Semi Owl SoC dmaengine driver. It uses `virt-dma` to multiplex device-tree-visible virtual channels/request lines over a smaller set of physical DMA channels and supports memcpy, slave SG, and cyclic transfers through hardware linked-list descriptors.

## Important APIs, Types, and Functions
- `struct owl_dma_lli` represents a DMA-pool-allocated hardware linked-list item.
- `struct owl_dma_txd` wraps `virt_dma_desc`, owns an LLI list, and marks cyclic transfers.
- `struct owl_dma_pchan` models a hardware physical channel and its current virtual channel.
- `struct owl_dma_vchan` wraps `virt_dma_chan`, tracks assigned physical channel, active transaction, slave config, and DRQ id.
- `struct owl_dma` stores the controller-level dmaengine device, MMIO base, clock, global lock, LLI pool, IRQ, physical/virtual channel arrays, and SoC id.
- `owl_dma_cfg_lli()` converts dmaengine direction and slave config into Owl descriptor mode/control words.
- `owl_dma_start_next_txd()`, `owl_dma_phy_alloc_and_start()`, and `owl_dma_issue_pending()` allocate physical channels and launch queued virtual descriptors.
- `owl_dma_interrupt()` clears global/channel interrupt state, completes active virtual descriptors, starts queued work, or releases physical channels.
- `owl_dma_prep_memcpy()`, `owl_dma_prep_slave_sg()`, and `owl_prep_dma_cyclic()` construct LLI chains.

## Control Flow
Probe reads `dma-channels` and `dma-requests`, selects S700/S900 descriptor layout behavior from OF match data, initializes dmaengine callbacks and channel lists, maps physical channel register windows, creates virtual channels with `vchan_init()`, creates a DMA pool for LLIs, enables the clock, registers dmaengine, and registers the OF xlate callback. OF xlate assigns a DRQ id to an arbitrary slave channel. Prepare paths allocate an `owl_dma_txd`, build one or more LLIs, and return a `virt-dma` prepared descriptor. `issue_pending` queues descriptors through `vchan_issue_pending()` and, if no physical channel is assigned, grabs a free pchan and starts the next txd. Interrupt handling clears pending bits, checks for missed channel-level status, completes the active `virt_dma_desc`, and either starts the next queued descriptor on the same pchan or terminates/releases the pchan.

## State and Persistence
The driver maintains only runtime state: virtual-channel queues from `virt-dma`, current `vchan->txd`, physical-channel ownership, slave config, DRQ assignment, LLI pool contents, and controller interrupt masks. Hardware descriptors differ between S700 and S900 in frame length/frame count/control packing. No persistent storage is used.

## Dependencies and Integration Points
Dependencies include platform/OF resources, `of_dma_controller_register()`, `virt-dma`, DMA pools, clocks, MMIO, and a single shared controller IRQ. Compatible strings include `actions,s500-dma`, `actions,s700-dma`, and `actions,s900-dma`. The driver uses `subsys_initcall()` rather than `module_platform_driver()`.

## Risks and Edge Cases
- `owl_dma_pause()` dereferences `vchan->pchan` without a null check, unlike resume, so pause before physical assignment would be unsafe.
- `owl_dma_of_xlate()` rejects `drq > od->nr_vchans`; since valid DRQs are zero-based, `drq == nr_vchans` should also be invalid and may index beyond the virtual request range semantically.
- `od->dma.directions` is set only to `BIT(DMA_MEM_TO_MEM)` even though slave SG/cyclic callbacks and capabilities are registered; this may under-advertise slave directions.
- `owl_dma_get_pchan()` returns the last pchan pointer even if all pchans are busy because the loop leaves `pchan` non-NULL; this can lead to assigning a busy physical channel.
- Busy waits on channel idle use `cpu_relax()` without timeout in `owl_dma_start_next_txd()`.

## Test Signals
Tests should include build/probe for S700 and S900 compatibles, OF DRQ boundary tests, memcpy over lengths greater than `OWL_DMA_FRAME_MAX_LENGTH`, slave SG with 1-byte and 4-byte widths, cyclic callback repetition, pchan exhaustion with more virtual requests than hardware channels, pause/resume before and during active transfers, residue reporting, and missed global-vs-channel IRQ status handling.
