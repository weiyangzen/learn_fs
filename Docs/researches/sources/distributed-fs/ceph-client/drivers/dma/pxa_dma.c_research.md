# sources/distributed-fs/ceph-client/drivers/dma/pxa_dma.c Research

## Purpose
`pxa_dma.c` implements the Marvell/PXA peripheral DMA controller as a Linux dmaengine provider. It supports slave scatter-gather transfers, memory-to-memory copies, cyclic audio-style transfers, dynamic assignment of virtual channels to physical DMA channels, debugfs inspection, platform-data and device-tree channel lookup, residue reporting, and termination/synchronization through the virt-dma framework.

## Important APIs, Types, and Functions
The hardware descriptor is `struct pxad_desc_hw` with DDADR, DSADR, DTADR, and DCMD words. `struct pxad_desc_sw` wraps a virt-dma descriptor, the coherent hardware descriptor array, length, first DMA address, misalignment flag, cyclic flag, and descriptor pool pointer. `struct pxad_phy` models a physical channel and current virtual-channel owner. `struct pxad_chan` embeds `struct virt_dma_chan`, stores requestor mapping (`drcmr`), required priority, current slave config, physical channel assignment, descriptor pool, bus-error cookie, and waitqueue. `struct pxad_device` is the controller and owns the dma_device, MMIO base, physical channels, and debugfs state.

Core dmaengine methods are `pxad_alloc_chan_resources()`, `pxad_free_chan_resources()`, `pxad_prep_memcpy()`, `pxad_prep_slave_sg()`, `pxad_prep_dma_cyclic()`, `pxad_config()`, `pxad_tx_submit()`, `pxad_issue_pending()`, `pxad_tx_status()`, `pxad_terminate_all()`, and `pxad_synchronize()`. Hardware helpers include `lookup_phy()`, `pxad_free_phy()`, `phy_enable()`, `phy_disable()`, `pxad_launch_chan()`, `pxad_try_hotchain()`, `clear_chan_irq()`, and the IRQ handlers. Probe helpers are `pxad_init_phys()`, `pxad_dma_xlate()`, `pxad_init_dmadev()`, and `pxad_probe()`.

## Control Flow
Probe maps MMIO, reads channel/requestor counts from OF or platform data, configures dmaengine capabilities, initializes physical channel IRQ handling, creates one virt channel per physical slot, registers the dma_device, optionally registers an OF DMA controller, and creates debugfs files. Client configuration stores address, width, and burst information in `chan->cfg`. Prepare paths allocate one hardware descriptor per transfer segment plus one updater descriptor, fill descriptor chains, set source/target addresses and DCMD width/burst/flow bits, mark misalignment when needed, and pass the descriptor to virt-dma.

Submit finalizes the updater descriptor, assigns a cookie, and either hot-chains onto a still-running physical channel or queues the descriptor in `desc_submitted`. Cold chaining links submitted descriptors when alignment mode remains compatible. `issue_pending()` moves submitted descriptors to issued and launches the first one if the channel cannot be hot-chained.

Interrupt flow handles either per-channel IRQs or a shared controller IRQ via `DINT`. `pxad_chan_handler()` clears DCSR status, walks issued descriptors, uses the updater descriptor to decide completion, completes normal descriptors, invokes cyclic callbacks without removing the cyclic descriptor, records bus-error cookies, stops on errors, and relaunches the next issued descriptor after STOPSTATE. Termination disables hardware, frees physical mapping, gathers all virt-dma descriptors, and frees them without callbacks.

## State and Persistence
All state is in memory and MMIO registers. Persistent runtime state includes channel/requestor mappings in DRCMR registers, active physical channel ownership, DALGN alignment bits, descriptor pools, descriptor queues managed by virt-dma, bus-error cookie, waitqueue state, and debugfs dentries. There is no filesystem persistence beyond debugfs views.

## Dependencies and Integration Points
The driver depends on Linux dmaengine, virt-dma, DMA pool allocation, platform device APIs, OF DMA translation, platform data from `linux/platform_data/mmp_dma.h`, request parameters from `linux/dma/pxa-dma.h`, interrupt APIs, waitqueues, and optional debugfs. It integrates with clients via either OF two-cell DMA specs (`requestor`, `priority`) or legacy filter parameters in `struct pxad_param`.

## Risks and Edge Cases
The updater descriptor completion scheme is subtle: the final descriptor writes to the previous descriptor's address so software can detect whether hardware reached the end. Residue must read current DSADR/DTADR before completion testing to avoid reordering. Hot chaining is intentionally refused when a pending descriptor would require switching into misaligned mode, otherwise DALGN could be wrong for active hardware. Bus errors mark a cookie as `DMA_ERROR` and disable the physical channel. Cyclic transfers require period length alignment and period size under the hardware DCMD length mask. `pxad_terminate_all()` appears to clear `phy->vchan` both through `pxad_free_phy()` and again after, so concurrency assumptions around `phy_lock` matter.

## Test Signals
Useful tests include dmatest memcpy, slave SG transfers in both directions with several widths and bursts, cyclic DMA callbacks, OF xlate and legacy filter lookup, hot-chain stress with back-to-back descriptors, misaligned and aligned transfer mixtures, residue reporting during active transfers, bus-error injection if available, terminate/synchronize while running, shared versus per-channel IRQ configurations, and debugfs state/descriptors/requesters output.
