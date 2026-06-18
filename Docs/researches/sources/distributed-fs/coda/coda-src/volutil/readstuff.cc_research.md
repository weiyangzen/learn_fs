## sources/distributed-fs/coda/coda-src/volutil/readstuff.cc

Purpose: `readstuff.cc` implements buffered deserialization for Coda dump streams from local file descriptors or RPC2/SMARTFTP. It is the inverse of `dumpstuff.cc` for restore-style consumers that do not require random access.

Important APIs/types/functions: private `get` refills the buffer and returns a pointer to requested bytes; private `put` pushes bytes back. Public functions include `ReadTag`, `PutTag`, `ReadShort`, `ReadInt32`, `ReadString`, `ReadByteString`, `ReadVV`, `ReadDumpHeader`, `EndOfDump`, `ReadVolumeDiskData`, and `ReadFile`.

Control flow: `get` preserves unused bytes, refills from RPC `ReadDump` or `read`, updates offsets/counts, and advances `DumpBufPtr`. Scalar readers decode explicit big-endian values. Struct readers consume field tags while tags are above `D_MAX`, then push back the structural tag. `ReadFile` reads the file payload length, then copies chunks to an output `FILE*`.

State and persistence behavior: mutates `DumpBuffer_t` position, offset, byte count, elapsed seconds, and RPC failure state. `ReadFile` writes extracted file content to the caller-provided file. It does not alter Coda volume state.

Dependencies/integration points: used by restore and dump readers that work over RPC or file descriptors. It depends on dump tags from `dump.h`, `VolumeDiskData`, `ViceVersionVector`, `voldump.h` RPC stubs, and Coda logging.

Risks: the local-file refill path reads `DumpBufPtr - DumpBuf` bytes after resetting/copying state, which is subtle and can be error-prone. String truncation logs the adjusted length rather than original length. Unknown field tags cannot be skipped unless known by switch logic, so format extension is limited. `ReadTag` returns `FALSE` on EOF, conflating tag `0`/false states. `put` asserts there is room to move backward.

Test signals: round-trip data written by `dumpstuff.cc`, exercise RPC and file modes, strings at exact/truncated lengths, volume headers with optional fields, malformed VV termination, missing dump end magic, and file payload short reads/writes.
