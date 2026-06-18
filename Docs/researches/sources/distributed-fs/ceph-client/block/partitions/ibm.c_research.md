<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/ibm.c -->
# sources/distributed-fs/ceph-client/block/partitions/ibm.c

## Purpose

`ibm.c` implements IBM s390 DASD partition recognition for the generic Linux block partition scanner. It detects and interprets DASD volume labels in EBCDIC form, including `VOL1` CDL labels, `LNX1` Linux LDL labels, and `CMS1` VM/CMS labels, then emits Linux partitions through `put_partition()`.

Although the source is stored under a `ceph-client` snapshot, this file is kernel block-layer partition code. It integrates through `check.h` and the partition parser table, not through Ceph request or object paths.

## Important APIs, Types, And Functions

The public entry point is `ibm_partition(struct parsed_partitions *state)`. It obtains block geometry with `disk->fops->getgeo`, optional DASD metadata via the exported `dasd_biodasdinfo` symbol, logical block size from `bdev_logical_block_size()`, and disk capacity from `bdev_nr_sectors()`.

Local helpers `cchh2blk()` and `cchhb2blk()` convert IBM cylinder/head/block VTOC addresses into linear block numbers using `struct hd_geometry`, including the DASD large-volume cylinder encoding. `find_label()` probes the possible label sectors, copies the label into `union label_t`, converts type and volume id from EBCDIC to ASCII with `EBCASC()`, and selects the label parser. `find_vol1_partitions()`, `find_lnx1_partitions()`, and `find_cms1_partitions()` implement the three supported label formats.

Important structures come from architecture DASD and VTOC headers: `dasd_information2_t`, `vtoc_volume_label_cdl`, `vtoc_volume_label_ldl`, `vtoc_cms_label`, `vtoc_format1_label`, `vtoc_cchh`, and `vtoc_cchhb`.

## Control Flow

`ibm_partition()` exits early when geometry or capacity is unavailable. It dynamically pins `dasd_biodasdinfo` with `symbol_get()`, allocates temporary `info`, `geo`, and label objects, seeds `geo->start`, calls `getgeo`, and falls back to a generic scan if DASD info cannot be obtained.

`find_label()` probes exactly one known label location when DASD info is available, otherwise it tries sector 1, block 1, and block 2 adjusted for logical block size. Once a valid label type is found, `ibm_partition()` dispatches by label type. `VOL1` parsing walks VTOC format labels beginning at the VTOC pointer, skipping FMT4/FMT5/FMT7/FMT9, accepting FMT1/FMT8 extents, and emitting one partition per extent. `LNX1` parsing creates a single Linux partition after the label, using formatted-block metadata when the label has large-volume support and geometry/capacity checks otherwise. `CMS1` parsing creates one partition for the CMS data region, with special handling for reserved minidisks and DIAG FBA label placement.

If no valid label is found but the device responded to DASD info, the parser still claims the disk for backward compatibility; LDL-formatted DASDs get a synthetic single partition after the label block.

## State And Persistence Behavior

The file has no persistent kernel state. It builds temporary parse state from on-disk DASD labels and releases every sector with `put_dev_sector()` and every allocation with `kfree()`. The persistent state is the disk-resident volume label/VTOC/CMS metadata; emitted partition state is stored in `parsed_partitions` for the block layer to publish later.

## Dependencies And Integration Points

Dependencies include `linux/buffer_head.h`, `linux/hdreg.h`, `asm/dasd.h`, `asm/vtoc.h`, `asm/ebcdic.h`, `linux/dasd_mod.h`, and the local partition scanner API in `check.h`. Runtime DASD-specific integration is optional through `symbol_get(dasd_biodasdinfo)`, which allows this parser to run when DASD support is modular.

## Risks And Edge Cases

The parser depends on reliable geometry. Incorrect heads/sectors values can produce wrong VTOC extent starts and sizes. Label probing without DASD info intentionally tries multiple sectors, which can claim unusual disks if label-like data is present. `VOL1` parsing must stop on invalid format ids and avoid exceeding `state->limit`. `LNX1` has careful geometry-versus-capacity fallback for old labels; without real DASD info it may decline to create a partition rather than guess. `CMS1` must handle sector-1 labels on block sizes larger than 512 bytes while still starting the partition at block 2.

## Test Signals

Useful tests include DASD images with `VOL1`, `LNX1` old and new large-volume versions, `CMS1` regular and reserved-minidisk labels, missing labels on a DASD device, and malformed VTOC entries. Signals are the parser return value, `pp_buf` strings such as `VOL1/`, `LNX1/`, `CMS1/`, `(nonl)`, correct partition starts/sizes, no leaked sector references, and graceful `-1` only for real read/allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/ibm.c -->
