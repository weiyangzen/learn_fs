<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nftlmount.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nftlmount.c

Purpose: NFTL mount and recovery code. It finds NFTL media headers, reconstructs virtual erase-unit chains from OOB metadata, handles interrupted folds, formats invalid/free blocks, and initializes free-block accounting.

Important APIs/types/functions: `find_boot_record()` scans for `ANAND` media headers and allocates/initializes tables. `check_free_sectors()`, `NFTL_formatblock()`, `check_sectors_in_chain()`, `calc_chain_length()`, `format_chain()`, `check_and_mark_free_block()`, and `get_fold_mark()` validate and repair media. `NFTL_mount()` performs the two-pass reconstruction.

Control flow: Mount first finds a valid media header and spare copy, validates formatted size and block ranges, allocates `EUNtable`/`ReplUnitTable`, marks BIOS/header/bad blocks reserved, and sets formatted block-device size. The first pass explores each unvisited block chain by reading UCI/OOB headers, validating logical unit numbers and replacement links, detecting fold-in-progress cases, and either formatting invalid chains or assigning the chain to `EUNtable`. Duplicate chains at the same logical address are resolved by keeping the longer chain. The second pass formats unreferenced blocks and counts free EUNs.

State and persistence: Persistent state is NFTL media header, bad-unit table derived via `mtd_block_isbad()`, erase marks, wear info, fold marks, virtual/replacement unit numbers, and per-sector status bytes. Runtime state after mount is the logical-to-physical `EUNtable`, replacement `ReplUnitTable`, `numfreeEUNs`, `LastFreeEUN`, `EraseSize`, `nb_blocks`, `lastEUN`, and `MediaHdr`.

Dependencies/integration: Called by `nftlcore.c` during MTD add. Uses MTD read/OOB/erase/bad-block APIs and NFTL structures/constants from `linux/mtd/nftl.h`.

Risks: Recovery is necessarily destructive for invalid/unreferenced chains because it formats blocks. Multiple comments flag uncertain power-failure behavior around chain formatting. Some write paths use OOB writes after erase and assume erase-mark semantics. `get_fold_mark()` returns 0 on read error, causing chain format in mount logic.

Test signals: Mount images with valid primary/spare headers, bad headers, reserved bad blocks, free blocks with/without erase marks, interrupted in-place and out-of-place folds, duplicate chains, invalid replacement loops, and unreferenced blocks. Verify free counts, selected chain lengths, wear-info preservation/increment, and bad-block marking on format failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nftlmount.c -->
