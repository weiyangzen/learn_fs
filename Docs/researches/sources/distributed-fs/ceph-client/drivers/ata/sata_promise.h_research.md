# sources/distributed-fs/ceph-client/drivers/ata/sata_promise.h

## Purpose
Provides common inline helpers and packet bit definitions for Promise SATA packet construction. The header is used by `sata_promise.c` to serialize ATA taskfile state into the controller's command packet format for DMA and no-data commands.

## Important APIs, Types, And Functions
- `enum pdc_packet_bits` defines packet flags for read/no-data, size fields, clear-BSY/wait-DRDY semantics, last-register markers, and device-control encoding.
- `pdc_pkt_header` initializes packet control words, writes the SG table DMA address, selects master/slave device state, and emits the device-control register write.
- `pdc_pkt_footer` optionally emits the taskfile device register and always emits the command register with the last-register marker.
- `pdc_prep_lba28` serializes feature, sector count, and 28-bit LBA registers.
- `pdc_prep_lba48` serializes high-order then low-order feature, count, and LBA bytes for 48-bit commands.

## Control Flow
`sata_promise.c` calls `pdc_pkt_header` first for ATA DMA or no-data commands, then chooses `pdc_prep_lba48` or `pdc_prep_lba28` according to `ATA_TFLAG_LBA48`, and finishes with `pdc_pkt_footer`. The helpers append bytes into a caller-owned 128-byte coherent packet buffer and return the next write offset so the caller can chain the packet pieces without extra parsing.

## State And Persistence
The header owns no persistent state. It mutates only the provided packet buffer using taskfile fields and the SG table DMA address. Endianness is explicit for 32-bit packet words via `cpu_to_le32`; individual register opcodes and values are byte writes.

## Dependencies And Integration Points
The header depends on `<linux/ata.h>` for taskfile fields, ATA register constants, protocol identifiers, and device-selection bits. It is tightly coupled to Promise controller packet layout and to `sata_promise.c`'s `pdc_qc_prep` sequencing.

## Risks And Edge Cases
`pdc_pkt_header` supports only `ATA_PROT_DMA` and `ATA_PROT_NODATA` and calls `BUG()` for other protocols, so callers must filter ATAPI and PIO paths before using it. The SG table address is stored as a 32-bit little-endian value, matching the 32-bit DMA mask requirement in the driver. LBA48 serialization order must remain high-byte then low-byte for each register pair. Incorrect offset chaining can corrupt the packet because the helpers do not bounds-check the caller's buffer.

## Test Signals
Test signals include correct packet bytes for read vs write DMA, no-data commands, master/slave device selection, device-control propagation, LBA28 and LBA48 register ordering, command byte with `PDC_LAST_REG`, and no use of these helpers for unsupported protocols.
