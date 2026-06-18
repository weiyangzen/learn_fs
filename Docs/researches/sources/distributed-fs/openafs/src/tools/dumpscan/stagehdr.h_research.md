# sources/distributed-fs/openafs/src/tools/dumpscan/stagehdr.h

Purpose: declares the legacy Stage backup header wire format used by `stagehdr.c` and `backuphdr.c`.

Important definitions: constants `STAGE_MAGIC`, `STAGE_CHECKSUM`, `STAGE_VERSMIN`, `STAGE_NAMLEN`, and `STAGE_HDRLEN`. `struct stage_header` lays out version, dates, tape file number, dump time, host/disk/name strings, volume ID, dump length, level, magic, checksum, and flags.

State/dependencies: no behavior or persistent state. It includes `intNN.h` for AFS integer types.

Integration points: `parsedump.c` recognizes `STAGE_VERSMIN` as a possible top-level backup header tag. `ParseStageHdr` validates and maps this struct into the generic `backup_system_header` exposed by `dumpscan.h`.

Risks/test signals: the struct models a fixed 1024-byte header but does not itself enforce packing; compatibility depends on field ordering and platform ABI matching the intended layout. Validation is through checksum and magic during parsing.
