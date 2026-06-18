# sources/distributed-fs/ceph-client/drivers/scsi/scsicam.c

## Purpose

`scsicam.c` provides legacy SCSI-CAM geometry helpers for `HDIO_GETGEO` and similar BIOS-style cylinder/head/sector queries. It infers geometry from an MSDOS partition table when possible, otherwise synthesizes a plausible SCSI-CAM geometry.

## Important APIs, Types, and Functions

Exports are `scsi_bios_ptable()`, `scsi_partsize()`, and `scsicam_bios_param()`. `scsi_bios_ptable()` reads the first disk folio and returns a kmalloc copy of the four MBR partition entries plus signature. `scsi_partsize()` parses the largest nonempty primary partition, decodes CHS end fields, and verifies CHS/LBA consistency. `setsize()` implements the SCSI-CAM fallback using up to 1024 cylinders and 62 sectors per track. `scsicam_bios_param()` tries partition inference, then fallback mappings.

## Control Flow

`scsicam_bios_param()` first calls `scsi_partsize()`. If an MBR partition has consistent CHS and LBA end positions, it returns that mapping. If not, capacities below 32 bits are passed through `setsize()`. If that fails or exceeds CHS field limits, the function chooses fixed 255/63 or 64/32 geometry and caps cylinders when necessary.

## State and Persistence Behavior

There is no persistent state. The only allocation is the partition table copy, freed before return. The code reads disk metadata but never writes media. Outputs are the caller-provided geometry integers.

## Dependencies and Integration Points

The file depends on block-layer `gendisk` mappings, folios, MSDOS partition structures, and unaligned little-endian helpers. `sd.c` uses it from `sd_getgeo()` when a SCSI host template does not provide `bios_param`.

## Risks and Edge Cases

The geometry is a compatibility fiction for modern disks. GPT-only disks, malformed MBRs, inconsistent CHS fields, and very large capacities fall back to synthetic values. `scsi_bios_ptable()` can fail if sector zero cannot be read. Consumers must not infer true media topology from this output.

## Test Signals

Test valid and invalid MBR signatures, CHS/LBA agreement and mismatch, 1023-cylinder extension handling, empty partition tables, zero sector fields, below/above-32-bit capacities, and `HDIO_GETGEO` through `sd_getgeo()` with and without host `bios_param`.
