# sources/distributed-fs/openafs/src/tools/dumpscan/stagehdr.c

Purpose: parses and writes legacy Stage backup headers that may precede an AFS dump.

Important APIs/functions: `hdr_checksum` computes a 32-bit checksum over the fixed header buffer. `ParseStageHdr` preserves the starting offset, reads a 1024-byte header, validates minimum version, `STAGE_MAGIC`, and checksum, fills `backup_system_header`, duplicates host/partition/volume strings, and optionally reads the next tag byte. On no-header/EOF it seeks back and returns `DSERR_MAGIC`. `DumpStageHdr` fills a fixed `stage_header`, computes checksum complement, and writes it.

State/dependencies: transient allocation of strings in `backup_system_header`; caller frees. Depends on `XFILE`, network byte-order conversion, `stagehdr.h`, and `intNN.h`.

Risks/test signals: fixed `strcpy` into 64-byte fields assumes caller-provided strings fit. Native 64-bit dump length is truncated to 32 bits when written because the Stage header has a 32-bit length field. Test signal is header parse/print and checksum validation on known Stage dumps.
