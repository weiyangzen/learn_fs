# sources/distributed-fs/ceph-client/include/linux/ata.h

## Purpose
Defines core ATA/ATAPI/SATA constants, command values, register/status bits, IDENTIFY word offsets, feature-detection helpers, transfer-limit helpers, and port multiplier helpers for libata and related drivers.

## Important APIs, Types, And Functions
The large enum covers global limits, IDENTIFY DEVICE word indexes, PIO/SWDMA/MWDMA/UDMA masks, PRD/DMA constants, command-block bits, ATA/ATAPI commands, NCQ subcommands, log pages, SET FEATURES values, SMART, DSM/TRIM, ATAPI packet flags, SATA PMP registers, cable types, SCR indexes, and SError bits. `enum ata_prot_flags` describes taskfile protocol types. `struct ata_bmdma_prd` defines BMDMA PRD entries. Inline helpers inspect IDENTIFY data for LBA, DMA, NCQ, FUA, flush, LBA48, HPA, write cache, power management, read-log DMA, sense reporting, SCT features, ATA version, SATA, TPM/trusted, unload, WWN, form factor, rotation, NCQ capabilities, TRIM/zero-after-trim, CHS validity, CFA, SSD, zoned capability, IORDY, cable type, ATAPI CDB length, command packet set, DMADIR, status OK, LBA28/LBA48 bounds, and PMP GSCR fields.

## Control Flow, State, And Persistence
The header is stateless but encodes many validation flows as inline helpers. Most helpers first check version/validity marker bits before trusting IDENTIFY words. LBA helpers enforce hardware sector-count and address limits. Protocol enum values let libata select PIO, DMA, NCQ, or ATAPI handling.

## Dependencies And Integration Points
Depends on `linux/bits.h`, `linux/string.h`, and fixed-width types. Integrated by libata core, host drivers, SCSI translation, disk feature detection, NCQ, zoned ATA, power management, SMART/security/trusted command paths, and SATA port multipliers.

## Risks And Test Signals
This is a hardware ABI header: wrong constants can cause data loss. Subtle risks include trusting invalid IDENTIFY words, off-by-one LBA limits, 40-wire cable misdetection, and NCQ/log feature misclassification. Tests should cover representative IDENTIFY fixtures, old ATA versions, SATA vs PATA, LBA28/LBA48 boundary values, TRIM and zero-after-trim detection, flush/FUA/wcache flags, zoned capability, ATAPI packet lengths, and real or emulated libata probe.
