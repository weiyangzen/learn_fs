# sources/distributed-fs/ceph-client/drivers/dma/switchtec_dma.c

## Purpose
`switchtec_dma.c` is a PCI DMAEngine driver for Microchip Switchtec PCIe switch DMA engines. It exposes private memcpy channels backed by hardware submission and completion queues in coherent memory, with MSI-X interrupts for per-channel completions and channel status/pause errors.

## Important APIs, Types, and Functions
`struct switchtec_dma_dev` owns the DMAEngine device, RCU-protected PCI device pointer, mapped BAR, channel array, channel count, and status IRQ. `struct switchtec_dma_chan` owns one DMAEngine channel, MMIO pointers for hardware and firmware channel registers, control/submit/completion locks, tasklet, ring state, SQ/CQ coherent memory, queue indices, phase tag, CID counter, IRQ, and software descriptor ring. Hardware queue entries are `struct switchtec_dma_hw_se_desc`; completions are `struct switchtec_dma_hw_ce`; software descriptors are `struct switchtec_dma_desc`.

Important functions include channel control helpers `halt_channel()`, `unhalt_channel()`, `reset_channel()`, `pause_reset_channel()`, `enable_channel()`, `disable_channel()`, ring processing `switchtec_dma_cleanup_completed()`, abort/stop/synchronize functions, descriptor preparation `switchtec_dma_prep_desc()` and `switchtec_dma_prep_memcpy()`, submission `switchtec_dma_tx_submit()`, doorbell `switchtec_dma_issue_pending()`, channel resource allocation/free, PCI channel enumeration, and `switchtec_dma_probe()`/`remove()`.

## Control Flow
PCI probe enables the device, sets a 64-bit coherent DMA mask, requests BAR regions, enables bus mastering, maps BAR0, initializes MSI-X vectors, requests a channel-status IRQ, reads channel count, initializes each channel, and registers a private DMAEngine memcpy device. Channel initialization maps per-channel firmware and hardware register windows, pause-resets the channel, programs performance tuning fields, configures an SE threshold, requests the per-channel completion IRQ from firmware `int_vec`, initializes locks/tasklet, and adds the DMA channel to the DMAEngine list.

Channel resource allocation creates coherent SQ and CQ rings, initializes all software descriptors to point into SQ slots, writes SQ/CQ base and size registers, enables/resets/unhalts the hardware channel, marks rings active, initializes cookies, and logs performance config. `prep_memcpy()` validates maximum size and fills the next available SQ descriptor under `submit_lock`; `tx_submit()` advances `head` with release ordering and assigns a cookie. `issue_pending()` writes the software head to hardware `sq_tail` because the device names the producer index oppositely.

Completions arrive through an IRQ tasklet or polling in `tx_status()`. `switchtec_dma_cleanup_completed()` compares CQ phase tags, computes residue/result, logs CE details on errors, advances CQ head to hardware, handles out-of-order completions by marking descriptors completed, and completes contiguous descriptors from `tail` with callbacks and unmapping.

## State and Persistence
All state is volatile: PCI BAR registers, coherent SQ/CQ memory, descriptor ring slots, head/tail/cq_tail/phase_tag/cid, active flags, and RCU `pdev` lifetime. No persistent storage is used. Removal releases channel IRQs, stops channels, nulls the RCU PCI pointer, synchronizes RCU, unregisters DMAEngine, unmaps BAR, releases PCI regions, and disables the device.

## Dependencies and Integration Points
The driver depends on PCI/MSI-X, DMAEngine, coherent DMA allocation, tasklets, spinlocks, RCU, circular-buffer helpers, MMIO polling, and Switchtec PCI IDs/class matching. It registers only `DMA_MEMCPY` and `DMA_PRIVATE`, with 8-byte copy alignment. The PCI ID table covers Microsemi/Microchip Switchtec PFX/PSX/PFXA/PSXA generations and EFAR IDs with class-code filtering.

## Risks and Edge Cases
The ring constants are large and used as masks, so power-of-two assumptions are fundamental. `SWITCHTEC_DMA_RING_SIZE`, `SQ_SIZE`, and `CQ_SIZE` are byte-size constants reused as entry counts, which is intentional only if hardware queue size fields and allocation sizing agree. `switchtec_dma_prep_desc()` leaves `submit_lock` held for `tx_submit()`; caller misuse would deadlock, though DMAEngine expects this pattern. Completion handling supports out-of-order CEs but only invokes callbacks for contiguous completed descriptors from tail. Terminate pauses/resets and disables completion processing; `synchronize()` aborts descriptors and reinitializes hardware/software indices. RCU guards hot-unplug/removal, but many register paths return early if `pdev` is gone.

## Test Signals
Test PCI probe/remove, MSI-X vector allocation, per-channel allocation/free cycles, memcpy sizes up to and above `SWITCHTEC_DESC_MAX_SIZE`, ring-full behavior, interrupt-driven and polling completion, out-of-order completion ordering, CE error logging/result mapping, pause/resume, terminate/synchronize reuse, and removal while rings are active.
