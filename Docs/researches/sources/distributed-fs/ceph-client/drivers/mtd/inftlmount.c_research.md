<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/inftlmount.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/inftlmount.c

Purpose: mounts and validates an INFTL volume by finding the media header, reading partition geometry, constructing virtual-to-physical erase-unit chains, formatting unusable units, and initializing free-block state for `inftlcore.c`.

Important APIs, types, and functions: exported functions are `INFTL_mount()`, `INFTL_formatblock()`, `INFTL_dumptables()`, and `INFTL_dumpVUchains()`. Internal helpers include `find_boot_record()`, `check_free_sectors()`, `memcmpb()`, and `format_chain()`. The code consumes `struct INFTLMediaHeader`, `struct INFTLPartition`, `struct inftl_unithead1`, and `struct inftl_unittail` from INFTL/NFTL headers.

Control flow: `INFTL_mount()` calls `find_boot_record()` to scan erase units for a `BNAND` media header plus matching spare header, endian-converts fields, validates partition counts, chooses the BDTL partition, allocates `PUtable`/`VUtable`, reserves boot/media/bad units, and sizes `mbd`. Pass 1 explores OOB unit headers to link chains by logical block and previous-unit pointer. Invalid chains are formatted. Pass 2 detects loops and ANAC discontinuities, fixing table links. Pass 3 formats unreferenced blocks and counts free units.

State and persistence: mount reconstructs volatile tables from persistent OOB headers and erase marks. `INFTL_formatblock()` erases each physical eraseblock in a logical unit, verifies erased data/OOB as `0xff`, writes the erase mark tail, and marks failed physical blocks bad through MTD.

Dependencies and integration points: relies on MTD reads, erases, bad-block APIs, INFTL OOB helpers from `inftlcore.c`, and DiskOnChip media layout definitions. It feeds `inftlcore.c` with mounted geometry, free counts, and chain tables.

Risks: source text includes an apparent duplicated `PUtable = kmalloc_array(...)` line in the allocation block, which is a build-level red flag in this snapshot. Quick-mount hidden blocks are erased rather than supported. Formatting invalid/unreferenced blocks is destructive by design. Test signals are successful media-header detection, rejection of invalid headers, correct bad-unit reservation, loop/corruption warnings, free count consistency, and erase-mark verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/inftlmount.c -->
