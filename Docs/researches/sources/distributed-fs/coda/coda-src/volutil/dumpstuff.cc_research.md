## sources/distributed-fs/coda/coda-src/volutil/dumpstuff.cc

Purpose: `dumpstuff.cc` implements binary dump serialization into a buffered destination. The destination can be a local file descriptor or an RPC2/SMARTFTP connection used by volume dump RPCs.

Important APIs/types/functions: `InitDumpBuf` initializes `DumpBuffer_t`; `FlushBuf` writes buffered bytes to a file or calls `WriteDump` over RPC; `Reserve` allocates contiguous buffer space and flushes when necessary. Serialization functions include `DumpTag`, `DumpByte`, `DumpDouble`, `DumpInt32`, `DumpArrayInt32`, `DumpShort`, `DumpBool`, `DumpString`, `DumpByteString`, `DumpVV`, `DumpFile`, and `DumpEnd`.

Control flow: each `Dump*` call reserves the exact byte count, writes a structural or field tag, and serializes values in explicit big-endian byte order. `DumpFile` writes a size field then streams inode contents in chunks based on `st_blksize`. `DumpEnd` writes the end marker and forces a final flush.

State and persistence behavior: persistent effects are writes to `DumpFd` or remote client transfer through `WriteDump`. `DumpBuffer_t` tracks byte offsets, total bytes, and transfer seconds. On RPC failure, `FlushBuf` marks `rpcid = -1` so later calls fail.

Dependencies/integration points: used by `vol-dump`, `codamergedump`, and `dumpstream::copyVnodeData`. It depends on RPC2 side-effect descriptors, Coda logging, `VolumeId`, `ViceVersionVector`, and `voldump.h` RPC stubs.

Risks: file-write error returns `0` in one path while most failures use `-1`, so callers can miss local write failures. `DumpFile` asserts on short read, aborting the process. `Reserve` assumes one requested item fits in the whole buffer; callers must size the buffer larger than max chunk/page. `DumpString` requires non-NULL NUL-terminated input. Logging uses pointer/integer formatting that may be dated on 64-bit builds.

Test signals: serialize fixed scalar values and compare byte-for-byte big-endian output, dump files with varying block sizes and zero length, force short writes/RPC errors, and verify `DumpEnd` produces a readable trailer. Use valgrind/asan around NULL string or oversized reservation tests if hardening.
