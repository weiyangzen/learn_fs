# sources/distributed-fs/ceph-client/drivers/ata/pata_optidma.c

## Purpose
Handles OPTi FireStar and FireStar Plus DMA-capable PCI PATA controllers, including both base DMA timing and FireStar Plus UDMA-specific paths.

## Important APIs, Types, And Functions
`optidma_pre_reset()` checks enable bits. `optidma_lock()` and `optidma_unlock()` guard the controller's timing-programming window. `optidma_mode_setup()` handles base PIO/MWDMA timing, while `optiplus_mode_setup()` handles Plus timing and UDMA. `optidma_set_mode()` coordinates libata mode selection and controller-specific bit programming. `optiplus_with_udma()` identifies UDMA-capable Plus variants.

## Control Flow
Probe chooses either `optidma_port_ops` or `optiplus_port_ops` based on PCI ID and hardware probing, then registers BMDMA ATA ports. Mode setup computes or selects timing values, enters the controller's indexed programming mode, writes timing/control registers, and exits the mode. Plus chips use a different setup routine and can expose UDMA masks.

## State And Persistence
The module-level `pci_clock` captures clock assumptions, while actual transfer state persists in PCI config and controller timing registers. Runtime ATA state is owned by libata.

## Dependencies And Integration Points
Uses libata BMDMA operations, PCI config IO, controller-specific locking sequences, generic PCI power-management helpers, and ATA mode/timing helpers.

## Risks And Edge Cases
The indexed timing register lock/unlock sequence is fragile; failures can corrupt unrelated controller settings. Clock assumptions affect timing correctness. UDMA detection for Plus variants is hardware-specific, and mixed devices require careful mode bit composition.

## Test Signals
PIO, MWDMA, and UDMA mode transitions; Plus versus non-Plus hardware; lock/unlock error paths; disabled port reset; suspend/resume; and data integrity under sustained DMA.
