<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/bbm.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/bbm.h

## Purpose
`mtd/bbm.h` defines NAND/OneNAND bad-block table descriptors, flags, generic BBM state, and the OneNAND default bad-block-table entry point.

## Important APIs, Types, and Functions
It defines `NAND_MAX_CHIPS`, `struct nand_bbt_descr`, many `NAND_BBT_*` option flags, `NAND_BBT_SCAN_MAXBLOCKS`, OneNAND read error flags, `struct bbm_info`, and `onenand_default_bbt()`.

## Control Flow and State
NAND code uses descriptors to locate, create, version, scan, and write bad-block tables. `bbm_info` holds the in-memory BBT bitmap, option flags, erase-shift geometry, bad-block checker callback, optional scan pattern, and private data. Flash-based BBTs may reserve blocks and store markers in OOB or in-band.

## State and Persistence Behavior
The BBT can be both runtime state (`bbt` pointer) and persistent flash metadata. Version bytes, descriptor pages, and reserved block codes affect on-flash state.

## Dependencies and Integration Points
It integrates with MTD NAND/OneNAND drivers, OOB layouts, ECC policy, chip arrays, and `struct mtd_info`.

## Risks
BBT option combinations are delicate: `NO_OOB_BBM` must be paired with flash-based BBT, dynamic descriptors must be freed, and incorrect version/page fields can overwrite data or lose factory bad-block marks. ECC layouts that cover spare area need special handling.

## Test Signals
NAND bad-block scan/create/write tests, multi-chip BBT, OOB and no-OOB modes, version rollover, reserved block handling, OneNAND BBT creation, and power-failure recovery scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/bbm.h -->
