## sources/distributed-fs/coda/coda-src/volutil/codamergedump.cc

Purpose: `codamergedump.cc` merges an incremental Coda dump into a full dump, producing a new full-style dump. It replaces, adds, or removes vnodes from the base dump according to vnode records in the incremental dump while preserving the binary dump format used by restore/dump consumers.

Important APIs/types/functions: `ventry` records a vnode uniquifier, file offset, source `dumpstream`, and next pointer. `vtable` is a hash/list table indexed by vnode bit number. Core routines are `BuildTable`, `ModifyTable`, `WriteTable`, `WriteVnodeDiskObject`, `DumpVolumeDiskData`, and `WriteDumpHeader`. It uses `DumpBuffer_t` and `Dump*` functions for output serialization.

Control flow: `main` opens full and incremental dumpstreams, validates headers have matching parent/name, rejects merging onto an incremental or from a full dump, and opens an exclusive output file. It writes a merged header using base volume identity and incremental backup date/latest uniquifier. It reads and writes volume disk data, then processes large and small indices independently. For each class, `BuildTable` indexes non-null vnodes from the full dump by offset. `ModifyTable` reads the incremental class: `D_RMVNODE` removes matching entries, changed vnodes update their source dump/offset, and new vnodes are added. `WriteTable` seeks back to each selected vnode, rewrites the vnode metadata, and copies its associated file or directory payload.

State and persistence behavior: persistent output is the new dump file; input dumps are read-only. The in-memory `vtable` owns linked `ventry` records but does not free all structures before exit. It relies on seekable input dump files because `getVnode` seeks by stored offsets.

Dependencies/integration points: integrates with `dumpstream` for parse/seek/copy behavior, `dumpstuff.cc` for binary output, Coda vnode numbering helpers (`vnodeIdToBitNumber`, `bitNumberToVnodeNumber`), `VolumeDiskData`, `VnodeDiskObject`, and external ACL handling passed through `getVnode`.

Risks: the table growth path copies old entries into a larger allocation without zero-initializing the new tail, which can leave garbage buckets. The check `vnum > Table->nslots` should likely be `>=`. `WriteVnodeDiskObject` calls `DumpString(buf, 'X', eacl)` for directories without guarding `eacl` against NULL. Header/date semantics rely on incremental metadata but volume disk data comes from the incremental after both dumps are read. Any malformed offset, non-seekable input, or inconsistent vnode counts can abort via `CODA_ASSERT`.

Test signals: merge a full dump plus incrementals that add, delete, and modify both directory and file vnodes; verify output parses with `codareaddump`, converts with `codadump2tar`, and has a valid `D_DUMPEND`. Include incremental directory ACL changes, vnode uniquifier reuse, grown vnode list sizes, and corrupt/truncated dumps to exercise error paths.
