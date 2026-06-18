## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/sm_common.c

Purpose: this file provides common raw NAND registration support for SmartMedia and xD cards. It supplies their legacy ID tables, OOB layouts, bad-block marking convention, and a single exported helper for host drivers that expose such media as raw NAND.

Important APIs, types, and functions: `sm_register_device()` is the exported entry point. `nand_smartmedia_flash_ids[]` and `nand_xd_flash_ids[]` define legacy IDs, capacity, erase size, ROM, and broken-xD flags. `sm_attach_chip()` sets bad-block marker details, installs `sm_block_markbad()`, and selects the full or small-page OOB layout. The OOB callbacks define ECC positions and LBA/free regions for 512-byte SmartMedia sectors or 256-byte small pages.

Control flow: a caller creates and partially initializes a `nand_chip`/`mtd_info`, then calls `sm_register_device(mtd, smartmedia)`. The function sets `NAND_SKIP_BBTSCAN`, attaches SmartMedia/xD controller ops through the legacy dummy controller, scans one chip against the selected ID table, and registers the MTD device without partitions. During attach, the helper fixes the bad-block marker to OOB offset 5 with 7 valid bits and selects an OOB layout based on `mtd->writesize`.

State and persistence: there is no controller-owned runtime state. Persistent behavior is encoded in the media ID tables, OOB layout, bad-block marker rules, and `NAND_SKIP_BBTSCAN`, leaving card-format metadata such as LBAs visible to higher layers like sm_ftl.

Dependencies and integration points: it depends on raw NAND scan-with-IDs, MTD OOB layout APIs, exported symbol use by SmartMedia/xD host drivers, and the `struct sm_oob` format from `sm_common.h`. The `NAND_BROKEN_XD` flag is propagated through the ID table for larger xD cards.

Risks: the small-page layout is explicitly not fully SmartMedia-compliant for 256-byte devices, except that it preserves bad-block markers. `sm_block_markbad()` assumes erase-block-aligned offsets and requires a full 16-byte OOB write. Skipping BBT scan avoids generic BBT behavior and relies on the format’s own marker semantics. Unsupported write sizes return `-ENODEV`.

Test signals: successful detection of known SmartMedia/xD IDs, correct OOB ECC/free region reporting for 256- and 512-byte writes, bad-block marking writing `block_status = 0x0f`, preservation of LBA metadata for sm_ftl, and cleanup on `mtd_device_register()` failure.
