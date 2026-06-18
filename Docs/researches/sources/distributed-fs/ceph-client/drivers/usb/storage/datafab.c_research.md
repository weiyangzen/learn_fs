# sources/distributed-fs/ceph-client/drivers/usb/storage/datafab.c

## Purpose

`datafab.c` implements a usb-storage subdriver for Datafab USB CompactFlash readers. It exposes an ATA-like CompactFlash device as a SCSI disk by emulating core SCSI commands and issuing Datafab-specific bulk commands.

## Important APIs, Types, and Functions

`struct datafab_info` caches total sectors, sector size, selected LUN, and faked sense data. `datafab_bulk_read()` and `datafab_bulk_write()` wrap USB bulk transfers. `datafab_determine_lun()` probes dual-slot readers by trying IDENTIFY DEVICE on LUN 0 and 1. `datafab_id_device()` performs IDENTIFY and extracts capacity. `datafab_read_data()` and `datafab_write_data()` split transfers into at most 64 KiB bounce-buffer chunks and move data to/from the SCSI scatterlist. `datafab_handle_mode_sense()` fabricates a few mode pages. `datafab_transport()` dispatches SCSI commands, and `datafab_probe()` installs the custom transport and bulk reset handler.

## Control Flow

On first transport use, the driver allocates `struct datafab_info` and initializes `lun` to -1. INQUIRY and REQUEST_SENSE are faked. READ_CAPACITY identifies the CF media, stores 512-byte sector geometry, and returns last LBA plus sector size. READ_10/READ_12 and WRITE_10/WRITE_12 parse LBAs and sector counts, determine LUN if needed, issue 8-byte Datafab ATA-style commands, and transfer data in bounce-buffer windows. START_STOP is used as a media-change probe: a failed identify sets UNIT ATTENTION and check-condition result.

## State and Persistence Behavior

Runtime state is cached in `us->extra`: selected LUN, media capacity, sector size, and sense triplet. This cache survives across commands for a bound device but is not persisted. The physical CF card stores user data; the driver does not maintain metadata on the card beyond normal ATA-style read/write commands.

## Dependencies and Integration Points

The file depends on usb-storage probe/transport helpers, SCSI command constants, scatterlist transfer helpers, unusual-device tables, and Datafab's vendor bulk command protocol. It integrates with the SCSI disk layer by faking enough inquiry, capacity, mode-sense, sense, and medium-removal behavior for block devices.

## Risks and Test Signals

Risks include limited 28-bit LBA checks that compare sector counts rather than full address range, no READ_6/WRITE_6 support, a likely write-success condition bug using `&&` instead of `||` for reply validation, stale LUN selection after media changes, and simplistic sense data. Test signals include dual-slot LUN detection, READ_CAPACITY after insertion/removal, 64 KiB split reads/writes across scatterlists, MODE_SENSE page variants, START_STOP media-change behavior, and write-result error handling with malformed two-byte replies.
