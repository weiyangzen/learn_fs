# sources/distributed-fs/ceph-client/drivers/mtd/parsers/tplink_safeloader.c

Purpose: TP-Link Safeloader partition table parser. It reads an ASCII partition table embedded in firmware and exposes its entries as MTD partitions.

Important APIs/types/functions: `mtd_parser_tplink_safeloader_parse()` is the parser entry for `tplink,safeloader-partitions`. `mtd_parser_tplink_safeloader_read_table()` locates and reads the table using DT property `partitions-table-offset`. `mtd_parser_tplink_safeloader_cleanup()` frees dynamic names.

Control flow: the table reader obtains the relevant OF node, reads a big-endian size header, allocates `size + 1`, reads the table body, and NUL-terminates it. The parser scans from offset 4 using `sscanf("partition %64s base 0x%llx size 0x%llx%zn\n", ...)`, creating up to 32 partitions and duplicating each name. Cleanup frees names and the array on failure or MTD parser teardown.

State and persistence: persistent state is the Safeloader table in flash and the DT offset. Runtime state is the table buffer and dynamic partition names. The parser does not write flash.

Dependencies and integration: depends on OF, MTD reads, and a specific ASCII table grammar. Risks include trusting header size, parse offset assumptions, node reference handling when the table is on a partition versus master, and partial parsing if formatting deviates. Test signals include master and partition MTD nodes, missing offset property, large/truncated size, max partition count, malformed lines, dynamic-name cleanup, and corrected bitflip reads.
