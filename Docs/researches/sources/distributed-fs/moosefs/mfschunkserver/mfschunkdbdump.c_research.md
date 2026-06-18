# sources/distributed-fs/moosefs/mfschunkserver/mfschunkdbdump.c

## Purpose
`mfschunkdbdump.c` is a read-only diagnostic utility for MooseFS `.chunkdb` files. It prints the stored disk path and chunk records while validating record format and terminator correctness.

## Important APIs and control flow
`chunkdb_dump()` opens the file, loads it fully into memory, checks the `MFS CHUNKDB` header and mode, parses a length-prefixed path, validates all records, then rewinds and prints them. Modes 1 through 4 have record sizes 16, 18, 19, and 23 bytes. Later modes add header size, tested flag, and disk usage.

## State, persistence, and dependencies
The utility does not modify persistence. It depends on POSIX file APIs and `datapack.h` for endian-safe parsing. Its format knowledge mirrors chunkserver `.chunkdb` persistence.

## Risks and test signals
Tests should cover supported modes, bad magic, unsupported version, short/truncated files, invalid path length, bad block count, invalid path id, malformed terminator, and very large files that stress full-file allocation.
