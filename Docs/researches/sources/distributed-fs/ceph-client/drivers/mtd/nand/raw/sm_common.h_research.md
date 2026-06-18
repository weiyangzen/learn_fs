## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/sm_common.h

Purpose: this header defines the shared SmartMedia/xD OOB structure, format constants, registration prototype, and small validity helpers used by SmartMedia/xD NAND support.

Important APIs, types, and functions: `struct sm_oob` is the packed 16-byte spare-area format with reserved bytes, data status, block status, two LBA copies, and two ECC fields. Constants include `SM_SECTOR_SIZE`, `SM_OOB_SIZE`, `SM_MAX_ZONE_SIZE`, `SM_SMALL_PAGE`, and `SM_SMALL_OOB_SIZE`. `sm_register_device()` is declared for host drivers. Inline helpers `sm_sector_valid()`, `sm_block_valid()`, and `sm_block_erased()` classify spare-area status bytes and erased OOB patterns.

Control flow: the header itself has no execution path, but `sm_common.c` writes `struct sm_oob` instances when marking bad blocks and host/FTL code can use the inline helpers while scanning card metadata. The validity helpers use Hamming weight thresholds rather than exact-byte comparisons for status fields, matching SmartMedia’s bit-tolerant status encoding.

State and persistence: all state described here is on-media spare-area metadata. The packed struct fixes the physical layout that persists in NAND OOB. `sm_block_erased()` treats an all-0xff 16-byte OOB as erased.

Dependencies and integration points: it includes Linux bit operations and MTD core declarations. It is paired with `sm_common.c` and any SmartMedia/xD translation layer that needs to interpret LBA/status fields.

Risks: the `sm_block_erased()` helper compares the whole packed OOB structure to a static 16-byte erased pattern; structure size/layout must remain exactly 16 bytes. `hweight16()` is used on 8-bit fields after integer promotion, so callers must pass valid `struct sm_oob` contents. Any change to this header affects on-media format interpretation.

Test signals: compile-time packed struct size stability, correct valid/invalid threshold behavior for status bytes, erased OOB detection for all-0xff data, and consistency with the OOB layout offsets implemented in `sm_common.c`.
