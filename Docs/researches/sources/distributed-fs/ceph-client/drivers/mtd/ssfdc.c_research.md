# sources/distributed-fs/ceph-client/drivers/mtd/ssfdc.c

## Purpose
Implements a read-only SSFDC/SmartMedia flash translation layer as an MTD block translation driver. It detects SSFDC-formatted small-page NAND, builds a logical-to-physical block map from OOB metadata, and exposes a read-only block device.

## Important APIs, Types, and Functions
`struct ssfdcr_record` extends `mtd_blktrans_dev` with CHS geometry, CIS block, erase size, logical block map, and map length. Detection and mapping are handled by `get_valid_cis_sector()`, `read_raw_oob()`, `get_logical_address()`, and `build_logical_block_map()`. Block translation hooks are `ssfdcr_add_mtd()`, `ssfdcr_remove_dev()`, `ssfdcr_readsect()`, and `ssfdcr_getgeo()`, registered through `ssfdcr_tr`.

## Control Flow
On module init, `register_mtd_blktrans()` installs the translator. For each MTD, `ssfdcr_add_mtd()` accepts only NAND with 16-byte OOB and size within `UINT_MAX`, finds the CIS/IDI signature, allocates state, computes geometry, allocates an all-`0xffff` logical map, scans physical blocks after the CIS block, reads OOB address fields, validates signature/parity, stores logical-to-physical mappings by zone, and registers the block device. Reads compute logical block and sector offsets, translate through the map, read the physical 512-byte sector, or return `0xff` for unmapped logical sectors.

## State and Persistence
Persistent state is on-flash SSFDC CIS and OOB logical address metadata. Runtime state is the allocated logical block map and geometry cached in `ssfdcr_record`. The driver is read-only and does not update flash metadata.

## Dependencies and Integration Points
It depends on MTD core, raw NAND bad block checks, OOB reads, and `mtd_blktrans` block translation. It registers major 257 with three partition bits.

## Risks
The CIS detection loop appears to read when `mtd_block_isbad()` returns true, which is a sensitive area to verify against intended semantics. The mapper trusts OOB logical address metadata and overwrites duplicate logical entries with the latest scanned physical block. `BUG_ON(block_address >= map_len)` can crash on out-of-range block device reads. This legacy read-only FTL assumes small-page SmartMedia geometry.

## Test Signals
Test with known SSFDC images and malformed OOB metadata. Verify block reads, unmapped sectors returning `0xff`, CHS geometry, bad block skipping, and non-SSFDC NAND rejection.
