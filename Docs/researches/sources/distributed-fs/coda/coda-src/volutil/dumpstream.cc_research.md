## sources/distributed-fs/coda/coda-src/volutil/dumpstream.cc

Purpose: `dumpstream.cc` implements a seekable `FILE*` reader for Coda dump files. It duplicates parts of `readstuff.cc` but adds stream positioning, vnode offset tracking, payload skipping/copying, and direct copy helpers used by merge, inspection, and tar conversion tools.

Important APIs/types/functions: scalar helpers are `GetShort`, `GetInt32`, `GetString`, `GetByteString`, and `GetVV`. `dumpstream` methods include constructor/destructor, `isopen`, `getDumpHeader`, `getVolDiskData`, `getVnodeIndex`, `getNextVnode`, `getVnode`, `copyVnodeData`, `EndOfDump`, `setIndex`, `readDirectory`, `CopyBytesToMemory`, and `CopyBytesToFile`. `PrintDumpHeader` is a diagnostic helper.

Control flow: stream readers parse a structural tag, then consume field tags until the next structural tag and `ungetc` it. `getVnodeIndex` sets the current vnode class and reads count/list-size metadata. `getNextVnode` first calls `skip_vnode_garbage` to consume any previous payload, records the current offset, then parses null, removed, or real vnode records. Directory payloads are read by `readDirectory`; file payloads are copied to memory/file or a `DumpBuffer_t`.

State and persistence behavior: `dumpstream` owns a `FILE*`, a short source name, and current `IndexType`. It is read-only, but can write copied bytes to an output `FILE*` or dump buffer. Seeking only works for named files; stdin use supports sequential operations but not `getVnode`.

Dependencies/integration points: uses `dump.h` tags, Coda vnode/volume structs, directory page constants, `codadir`, external ACL format, `coda_largefile.h`, and dump writer functions for copy-through. A bogus `WriteDump` stub exists to satisfy linkage when dump writer code is pulled in.

Risks: constructor exits on open failure rather than leaving a recoverable error. Destructor always `fclose(stream)`, including stdin. `readDirectory` allocates pages by `npages` without validating against `DIR_MAXPAGES`. Old internal ACL handling reads fixed sizes and probes for 32-bit padding. `CopyBytesToFile` pads to 512-byte tar blocks, so it is tar-specific despite being on the stream class. Error handling often returns `-1` after partial stream movement.

Test signals: parse dumps with large/small indexes, deleted/null vnodes, directories with external ACLs, old-style internal ACLs, files of sizes around 0/1/511/512/513 bytes, and stdin input. Validate `getVnode` offset lookups against sequential reads and verify `EndOfDump` catches postamble bytes.
