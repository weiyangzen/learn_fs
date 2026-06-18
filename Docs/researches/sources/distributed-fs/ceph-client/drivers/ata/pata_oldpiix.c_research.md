# sources/distributed-fs/ceph-client/drivers/ata/pata_oldpiix.c

## Purpose
Implements libata support for early Intel PIIX controllers that lack separate slave timing registers. Because timing is effectively per channel, the driver reloads timing when issuing commands to a different device.

## Important APIs, Types, And Functions
`oldpiix_pre_reset()` verifies PCI enable bits before SFF reset. `oldpiix_set_piomode()` and `oldpiix_set_dmamode()` program IDE timing registers at `0x40/0x42`. `oldpiix_qc_issue()` is the key wrapper that detects drive changes and reloads PIO/DMA timing before delegating to `ata_bmdma_qc_issue()`.

## Control Flow
PCI probe registers a BMDMA host for device ID `0x1230`. During mode setup, libata calls timing functions and the driver records the currently programmed `ata_device` in `ap->private_data`. Every command issue compares that pointer with `qc->dev`; if it differs, the driver reprograms shared timing and then starts the normal BMDMA/SFF command path.

## State And Persistence
Persistent state is minimal: PCI config timing registers and `ap->private_data` as a cache of which drive's timing is loaded. No driver-private allocation is needed.

## Dependencies And Integration Points
Uses libata BMDMA port operations, SFF prereset, PCI config access, Intel timing encodings, and standard libata PCI suspend/resume helpers.

## Risks And Edge Cases
The entire correctness model depends on `qc_issue()` seeing all drive switches. Clearing the other drive's TIME bits is a defensive fallback but may reduce performance. Shared timing makes mixed master/slave devices a regression-prone path, especially for MWDMA modes that require derived PIO timing.

## Test Signals
Master-only, slave-only, and master/slave configurations; alternating command streams; MWDMA mode selection; disabled PCI port bits returning `-ENOENT`; suspend/resume preserving libata behavior.
