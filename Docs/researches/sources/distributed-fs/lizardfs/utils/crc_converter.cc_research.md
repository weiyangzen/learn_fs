# sources/distributed-fs/lizardfs/utils/crc_converter.cc

Purpose: offline chunk utility that recalculates and rewrites CRC tables for standard or XOR chunk files. It accepts an input chunk and type selector `{ Std | Xor }`.

Important APIs/types/functions: `ChunkType` encodes file layout differences: standard chunks have data at 5 KiB, up to 1024 blocks, and 4 KiB CRC data; XOR chunks have data at 4 KiB, up to 512 blocks, and 2 KiB CRC data. `parseArguments()` validates CLI arguments. `calculateCrc()` seeks to the data region and fills a CRC buffer. `calculateCrcForBlock()` reads one full 64 KiB block and computes zlib CRC32. `writeCrc()` overwrites the CRC region at offset 1024.

Control flow: `main()` parses the type, allocates the exact CRC table size, computes CRCs block by block, and writes the table back to the same file. Short final blocks are considered incorrect chunk files and cause exit status 2.

State and persistence: mutates the input file in place. It opens the chunk first as input and later as read/write output. There is no backup or transactional rewrite.

Dependencies/integration: depends on zlib, `<arpa/inet.h>` for `htonl`, and fixed LizardFS chunk layout constants. It complements chunk conversion/repair workflows.

Risks and test signals: uses `reinterpret_cast<uint32_t*>` on a byte buffer, which can be alignment-sensitive on strict architectures. It does not verify chunk signature or file length before rewriting. Test signals are standard and XOR chunk fixtures, corrupted/short block behavior, endian correctness of CRC entries, and preservation of non-CRC regions.
