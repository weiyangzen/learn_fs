<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mediatek/mtk-hsdma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/mediatek/mtk-hsdma.c

## Purpose
DMAEngine driver for MediaTek High-Speed DMA memory-to-memory copy engines. It multiplexes several virtual channels over one ring-based physical engine.

## Important APIs, Types, And Functions
Important structures are `mtk_hsdma_device`, `mtk_hsdma_vchan`, `mtk_hsdma_pchan`, `mtk_hsdma_ring`, hardware descriptor `mtk_hsdma_pdesc`, virtual descriptor `mtk_hsdma_vdesc`, and per-descriptor callback metadata `mtk_hsdma_cb`. `mtk_hsdma_alloc_pchan/free_pchan` allocate and program coherent TX/RX rings. `mtk_hsdma_issue_pending_vdesc` reserves ring entries and emits physical descriptors. `mtk_hsdma_free_rooms_in_ring` reclaims completed RX descriptors, updates residues, completes VDs, and reissues pending work. SoC data `mt7623_soc` and `mt7622_soc` define DDONE/LS0 bit positions.

## Control Flow
Probe maps registers, loads SoC match data, gets the clock and IRQ, initializes vchans, registers DMAEngine/OF DMA, enables runtime PM and global DMA settings, then requests the IRQ. Channel allocation lazily allocates the single physical ring on first user and reference-counts later users. A memcpy prep stores source, destination, length, and residue in one vdesc. Issue-pending reserves as many ring slots as are available, emits TX/RX descriptor pairs in chunks of `MTK_HSDMA_MAX_LEN`, tags the last physical descriptor for completion, writes the TX CPU pointer, and leaves partially emitted VDs on `desc_issued` until space returns. IRQ disables RXDONE, scans completed RX descriptors up to ring size, subtracts residue, completes tagged VDs, recycles descriptors, advances the RX CPU pointer, optionally acks status, and immediately tries to submit more pending VDs.

## State And Persistence
State lives in coherent descriptor rings, callback side arrays, atomic free-slot count, vchan issued/hardware-processing/completed lists, residues, refcounts, clocks/runtime PM, and HSDMA registers. The ring is allocated only while at least one virtual channel holds resources.

## Dependencies And Integration Points
Depends on DMAEngine, `virt-dma`, coherent DMA memory, MediaTek device-tree compatibles, clocks, runtime PM, OF DMA xlate by channel id, and platform IRQs. It advertises `DMA_MEMCPY`, memory-to-memory direction, 4-byte bus widths, and segment residue granularity.

## Risks And Edge Cases
`mtk_hsdma_hw_init` ignores its return value in probe, so clock/runtime PM failures can be hidden. Termination does not stop descriptors already on hardware; it waits until the ring completes them. Correctness depends on memory barriers around coherent descriptor updates and on callback metadata being cleared exactly once. Ring-space accounting and partial issue of a large VD are concurrency-sensitive because IRQ context and issue path share `nr_free` and vchan lists. Residue is modified in place as chunks are emitted and completed, so status for partially issued VDs must be checked under the VC lock.

## Test Signals
Run dmatest memcpy with many parallel virtual channels, transfer sizes larger than one physical descriptor, ring-full pressure, tx_status polling, terminate while active, and suspend/remove IRQ races. Hardware coverage should include both MT7622 and MT7623 compatible data because descriptor done bits differ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mediatek/mtk-hsdma.c -->
