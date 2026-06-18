## sources/distributed-fs/coda/coda-src/volutil/dump.h

Purpose: `dump.h` defines the Coda volume dump wire/file format tags, dump header shape, shared buffer structure, and exported serialization/deserialization APIs. It is the central contract between volume dumping, restoring, merge tools, dump readers, and tar conversion.

Important APIs/types/functions: constants include `DUMPVERSION`, `DUMPBEGINMAGIC`, `DUMPENDMAGIC`, and tags such as `D_DUMPHEADER`, `D_VOLUMEDISKDATA`, `D_LARGEINDEX`, `D_SMALLINDEX`, `D_VNODE`, `D_DIRPAGES`, `D_FILEDATA`, `D_RMVNODE`, and `D_BADINODE`. `DumpHeader` stores dump version, volume ids/name, incremental flag, backup date, and uniquifier range. `DumpBuffer_t` stores buffer pointers, offset, RPC handle, file descriptor/volume id, byte count, and elapsed transfer time. Exports cover `InitDumpBuf`, `Dump*`, `Read*`, `ReadDumpHeader`, `ReadVolumeDiskData`, `ReadFile`, `EndOfDump`, and YAML string encoding.

Control flow: producers emit tag-prefixed fields using the `Dump*` routines and terminate with `DumpEnd`. Consumers read tags with `ReadTag`, parse known fields until the next structural tag, then push that tag back with `PutTag` where needed. The format is extensible at the field level because unknown high-valued field tags can be skipped only if the reader knows their width; in practice readers switch on known tags.

State and persistence behavior: the header itself has no storage behavior, but `DumpBuffer_t` coordinates persistent file writes or RPC SMARTFTP transfer. `VOLID` aliases `DumpFd` for RPC-style dumps, making the field overloaded.

Dependencies/integration points: depends on Coda volume ids, `VolumeDiskData`, `ViceVersionVector`, and RPC2 types. It is included by `dumpstuff.cc`, `readstuff.cc`, `dumpstream.cc`, `vol-dump.cc`, `codamergedump.cc`, `codareaddump.cc`, and `codadump2tar.cc`.

Risks: the binary ABI assumes fixed Coda structure field meanings and manually serialized 32-bit integers. `DumpBuffer_t::DumpFd` overload is easy to misuse. Tag values are small chars, so signedness matters when comparing with EOF or `D_MAX`. The public API mixes `int`, `unsigned int`, `VolumeId`, and pointer casts, which can become fragile on wider platforms.

Test signals: compile all dump producer/consumer tools together, exercise full and incremental dump round trips, verify magic/version rejection, and fuzz tag streams around structural tags, unexpected EOF, string lengths, and vnode payload sizes.
