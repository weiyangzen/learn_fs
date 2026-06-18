## sources/distributed-fs/ceph-client/drivers/mtd/devices/bcm47xxsflash.c

Purpose: MTD driver for BCMA ChipCommon-attached serial flash on Broadcom BCM47xx-style systems. It supports ST-compatible and Atmel DataFlash-like controller command paths, a fast memory window for reads, and partition probing with `bcm47xxpart`.

Important APIs, types, and functions: `bcm47xxsflash_cmd()` starts controller opcodes and polls controller busy. `bcm47xxsflash_poll()` waits for flash ready using ST `RDSR` or Atmel status. MTD callbacks are `bcm47xxsflash_erase()`, `bcm47xxsflash_read()`, and `bcm47xxsflash_write()`, with type-specific `bcm47xxsflash_write_st()` and `_write_at()`. `bcm47xxsflash_bcma_probe()` maps resources and registers the MTD.

Control flow: platform probe receives `struct bcma_sflash` platform data, maps the memory window cached or uncached based on ChipCommon revision, infers flash type from BCMA capabilities, fills `mtd_info`, and registers partitions. Reads use the direct window for the first 16 MiB and indirect `FLASHADDR`/`FLASHDATA` reads beyond it. Writes loop until all data is written, because ST writes can stop at page boundaries or after one byte on old controllers and Atmel writes buffer/program one page at a time.

State and persistence: `struct bcm47xxsflash` stores BCMA ChipCommon accessors, type, mapped window, block geometry, size, and embedded `mtd_info`. Persistent media state is serial NOR/DataFlash content and controller registers.

Dependencies and integration points: depends on BCMA, platform devices created by BCMA, ChipCommon register definitions, MTD partition parsers, and `bcm47xxsflash.h` opcodes.

Risks: `bcm47xxsflash_read()` returns `orig_len` instead of zero on success, which is unusual for MTD callbacks and worth checking against caller expectations. Indirect reads always use an ST 4-byte read opcode even for the generic tail path. Cache mapping differs by SoC revision due to corruption risk. Erase/write lack explicit range checks in write path.

Test signals: successful BCMA probe, partition detection, read correctness through window and indirect paths, ST page-program behavior on old/new ChipCommon revisions, Atmel partial-page preservation, erase block size selection, and no timeout logs from controller or flash polling.
