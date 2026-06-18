## sources/distributed-fs/coda/coda-src/volutil/dumpstream.h

Purpose: `dumpstream.h` declares the C++ `dumpstream` class used for random/sequential access to Coda dump files. It gives utilities a higher-level interface than raw `DumpBuffer_t` reads while still exposing Coda vnode and volume structures.

Important APIs/types/functions: the class stores `FILE *stream`, `name`, `IndexType`, and private `skip_vnode_garbage`. Public APIs read dump headers, volume disk data, vnode index headers, next/specific vnode records, directory pages, file bytes, and dump trailers. `MAXSTRLEN` limits stored filename display. `PrintDumpHeader` is exported for debug output.

Control flow: callers construct with a filename or empty/null for stdin, call `getDumpHeader`, `getVolDiskData`, then `getVnodeIndex` for `vLarge` or `vSmall`. After that, `getNextVnode` returns metadata and leaves the stream before any associated payload; callers either copy/read the payload or let the next stream method skip it. `getVnode` uses a saved offset from a previous scan.

State and persistence behavior: `dumpstream` is a lightweight stateful reader around a dump file handle. It does not persist state beyond the file position and selected vnode class. Copy methods persist to caller-provided output destinations.

Dependencies/integration points: includes LWP/lock headers, `voltypes.h`, `cvnode.h`, and `volume.h`, and depends on `DumpHeader`, `DumpBuffer_t`, `PDirInode`, `VnodeDiskObject`, and `AL_ExternalAccessList` from included Coda headers.

Risks: the header defines `_LARGEFILE_SOURCE` and `_FILE_OFFSET_BITS` after comments but before some includes; consistency with the rest of the build matters. APIs expose raw allocated ACL/directory memory ownership to callers. The class is non-copy-safe by default because it owns a `FILE*` but does not declare copy/move behavior.

Test signals: compile all users after signature changes, run stream consumers on seekable files and stdin, and check ownership discipline for returned `PDirInode` and ACL buffers with leak tools.
