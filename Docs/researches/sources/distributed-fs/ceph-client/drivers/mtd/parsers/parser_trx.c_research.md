# sources/distributed-fs/ceph-client/drivers/mtd/parsers/parser_trx.c

Purpose: TRX firmware subparser that exposes loader, Linux, and data/rootfs/UBI subpartitions inside a TRX image.

Important APIs/types/functions: `parser_trx_parse()` is the registered parser for `brcm,trx`. `parser_trx_data_part_name()` reads the first word of the data area and returns `ubi` when it sees UBI EC magic, otherwise `rootfs`. Local `struct trx_header` mirrors the TRX header.

Control flow: it optionally reads `brcm,trx-magic` from DT, allocates up to four partitions, reads the header from offset 0, and rejects non-matching magic with `-ENOENT`. If `offset[2]` is nonzero it treats `offset[0]` as an LZMA loader. It then creates `linux` and data partitions for subsequent nonzero offsets. Sizes are inferred by the next partition offset or MTD partition end.

State and persistence: persistent input is the TRX header and optional UBI magic in flash. Runtime state is the allocated partition array. The parser performs no writes.

Dependencies and integration: depends on OF for magic override, MTD reads, and MTD parser chaining from parent firmware partitions. Risks include little/native-endian assumptions, malformed offset ordering causing underflow sizes, limited validation of offsets against device size, and incomplete handling of unusual TRX layouts. Test signals include default and custom magic, loader/no-loader images, UBI data detection, out-of-order offsets, short reads/errors, and bitflip behavior.
