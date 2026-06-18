# Research: subset-b-007021

This grouped report covers Coda `volutil` dump, backup, clone, creation, lookup, and inspection utilities. Each section is delimited for deterministic reconciliation into the source-tree-aligned per-file research outputs.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/codadump2tar.cc -->
## sources/distributed-fs/coda/coda-src/volutil/codadump2tar.cc

Purpose: `codadump2tar.cc` is a standalone converter from Coda binary volume dump format to a POSIX/GNU-style tar archive. It makes Coda backups portable outside Coda by reconstructing a pathname graph from directory vnodes, emitting tar directory/file/symlink/link records, and adding `..CodaACLs.yaml` metadata for external ACLs.

Important APIs/types/functions: `DumpObject` models one dumped vnode/uniquifier object, including parent links, path components, directory attributes, and ACL text. `TarRecd` wraps a `union block` tar header and formats name, prefix, size, mode, type, uid, mtime, link target, and checksum fields. Main passes are `ParseArgs`, `DoGlobalSetup`, `ProcessDirectory`, `CreateDirectories`, `ProcessFileOrSymlink`, `ProcessHardLinks`, `DumpACLs`, `GetDumpObj`, and `AddNameEntry`.

Control flow: `main` opens a `dumpstream`, reads `DumpHeader` and `VolumeDiskData`, initializes the Coda directory package, then walks the large vnode index first. Each directory vnode is parsed by `getNextVnode`, its directory pages are read with `readDirectory`, converted to a directory handle, and enumerated to create parent/name edges. After all directories are known, it emits directory tar records, then walks small vnodes to emit regular file or symlink entries. Hard links are emitted after regular data so link targets already exist. Finally `DumpACLs` emits a YAML file and `WriteZeroTrailer` closes the tar stream.

State and persistence behavior: all graph state is in-process global memory (`DumpTable`, `LVNlist`, `RootName`, `ThisHead`, `ThisVDD`, `TarFile`). It writes tar records to stdout or `-o`; it does not modify Coda volumes. It stores ACL data as a generated tar entry rather than restoring Coda ACLs directly.

Dependencies/integration points: consumes `dumpstream` and dump tags from `dump.h`; uses Coda directory routines (`DIR_Init`, `DH_EnumerateDir`, `DI_DiToDh`), PDB rights constants, `yaml_encode_double_quoted_string`, and GNU tar structures from `tar-FromRedHatCD.h`. It depends on Coda directory entries being network-order and converts vnode/unique ids with `ntohl`.

Risks: tar name and prefix fields are fixed-size and truncated with ad hoc `~` markers, so very long paths can collide. Symlink targets are capped to tar header limits. Hard-link handling assumes the first path for an object is a valid target. `CollectACLs` parses external ACL text with `%ms` and newline scanning, so malformed ACLs can produce partial YAML. Directory output forces mode `0755`, intentionally dropping original directory modes. The root/lost+found fallback can hide missing directory links rather than failing.

Test signals: use full dumps containing directories, files, symlinks, empty directories, hard links, long names, paths requiring tar prefix splitting, malformed/unusual ACL names, and incrementals with deleted vnodes. Validate with `tar tvf`, extraction checks, ACL YAML parsing, and round-trip comparison of file sizes, symlink targets, mtime/uid/mode behavior, and hard-link inode sharing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/codadump2tar.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/codamergedump.cc -->
## sources/distributed-fs/coda/coda-src/volutil/codamergedump.cc

Purpose: `codamergedump.cc` merges an incremental Coda dump into a full dump, producing a new full-style dump. It replaces, adds, or removes vnodes from the base dump according to vnode records in the incremental dump while preserving the binary dump format used by restore/dump consumers.

Important APIs/types/functions: `ventry` records a vnode uniquifier, file offset, source `dumpstream`, and next pointer. `vtable` is a hash/list table indexed by vnode bit number. Core routines are `BuildTable`, `ModifyTable`, `WriteTable`, `WriteVnodeDiskObject`, `DumpVolumeDiskData`, and `WriteDumpHeader`. It uses `DumpBuffer_t` and `Dump*` functions for output serialization.

Control flow: `main` opens full and incremental dumpstreams, validates headers have matching parent/name, rejects merging onto an incremental or from a full dump, and opens an exclusive output file. It writes a merged header using base volume identity and incremental backup date/latest uniquifier. It reads and writes volume disk data, then processes large and small indices independently. For each class, `BuildTable` indexes non-null vnodes from the full dump by offset. `ModifyTable` reads the incremental class: `D_RMVNODE` removes matching entries, changed vnodes update their source dump/offset, and new vnodes are added. `WriteTable` seeks back to each selected vnode, rewrites the vnode metadata, and copies its associated file or directory payload.

State and persistence behavior: persistent output is the new dump file; input dumps are read-only. The in-memory `vtable` owns linked `ventry` records but does not free all structures before exit. It relies on seekable input dump files because `getVnode` seeks by stored offsets.

Dependencies/integration points: integrates with `dumpstream` for parse/seek/copy behavior, `dumpstuff.cc` for binary output, Coda vnode numbering helpers (`vnodeIdToBitNumber`, `bitNumberToVnodeNumber`), `VolumeDiskData`, `VnodeDiskObject`, and external ACL handling passed through `getVnode`.

Risks: the table growth path copies old entries into a larger allocation without zero-initializing the new tail, which can leave garbage buckets. The check `vnum > Table->nslots` should likely be `>=`. `WriteVnodeDiskObject` calls `DumpString(buf, 'X', eacl)` for directories without guarding `eacl` against NULL. Header/date semantics rely on incremental metadata but volume disk data comes from the incremental after both dumps are read. Any malformed offset, non-seekable input, or inconsistent vnode counts can abort via `CODA_ASSERT`.

Test signals: merge a full dump plus incrementals that add, delete, and modify both directory and file vnodes; verify output parses with `codareaddump`, converts with `codadump2tar`, and has a valid `D_DUMPEND`. Include incremental directory ACL changes, vnode uniquifier reuse, grown vnode list sizes, and corrupt/truncated dumps to exercise error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/codamergedump.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/codareaddump.cc -->
## sources/distributed-fs/coda/coda-src/volutil/codareaddump.cc

Purpose: `codareaddump.cc` is an interactive dump-inspection utility. It provides parser commands to open a Coda dump, show the dump header and volume disk data, select large or small vnode indexes, skip vnodes, and print vnode disk objects.

Important APIs/types/functions: the command table exposes `openDumpFile`, `setIndex`, `showHeader`, `showVolumeDiskData`, `nextVnode`, `skipVnodes`, and `quit`. Global state includes `DefaultDumpFile`, `DefaultSize`, `DumpStream`, and `Open`. Helper functions include `Rewind`, `PrintVersionVector`, `showHeader`, `showVolumeDiskData`, `setIndex`, `skipVnodes`, and `showVnodeDiskObject`.

Control flow: `main` seeds the default dump filename if provided, initializes the parser prompt, and hands control to `Parser_commands`. Most commands verify a dump is open, often rewind by destroying/recreating `dumpstream`, then call stream APIs. `setIndex` reads the header and volume metadata, reads the large index, and optionally scans all large vnodes before reading the small index. `showVnodeDiskObject` and `skipVnodes` advance from the current stream position.

State and persistence behavior: this tool is read-only with respect to dumps and Coda state. It keeps only interactive process state: current dumpstream position, default filename, and default vnode class. Rewind requires a named file; stdin/empty filename cannot be reliably rewound or seeked.

Dependencies/integration points: uses Coda parser library, `dumpstream`, `DumpHeader`, `VolumeDiskData`, `VnodeDiskObject`, version vector printing, and vnode numbering conventions. It is mainly a diagnostic companion to `vol-dump`, restore code, `codamergedump`, and `codadump2tar`.

Risks: commands assume a correct stream position; using `nextVnode` before `setIndex` or after payload data can misparse. `strncpy` into local buffers may not always null-terminate if the input exactly fills the buffer. Many errors are printed but do not reset state. It prints raw pointer-like inode/dir node fields that are meaningful only inside Coda internals. It does not display external ACL payloads.

Test signals: open full and incremental dumps, verify header/volume fields match `vol-dump`, step through both vnode classes, skip past directory/file payloads, and test behavior on invalid/truncated dumps. Interactive regression tests can feed command scripts to stdin and compare stable portions of output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/codareaddump.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/dump.h -->
## sources/distributed-fs/coda/coda-src/volutil/dump.h

Purpose: `dump.h` defines the Coda volume dump wire/file format tags, dump header shape, shared buffer structure, and exported serialization/deserialization APIs. It is the central contract between volume dumping, restoring, merge tools, dump readers, and tar conversion.

Important APIs/types/functions: constants include `DUMPVERSION`, `DUMPBEGINMAGIC`, `DUMPENDMAGIC`, and tags such as `D_DUMPHEADER`, `D_VOLUMEDISKDATA`, `D_LARGEINDEX`, `D_SMALLINDEX`, `D_VNODE`, `D_DIRPAGES`, `D_FILEDATA`, `D_RMVNODE`, and `D_BADINODE`. `DumpHeader` stores dump version, volume ids/name, incremental flag, backup date, and uniquifier range. `DumpBuffer_t` stores buffer pointers, offset, RPC handle, file descriptor/volume id, byte count, and elapsed transfer time. Exports cover `InitDumpBuf`, `Dump*`, `Read*`, `ReadDumpHeader`, `ReadVolumeDiskData`, `ReadFile`, `EndOfDump`, and YAML string encoding.

Control flow: producers emit tag-prefixed fields using the `Dump*` routines and terminate with `DumpEnd`. Consumers read tags with `ReadTag`, parse known fields until the next structural tag, then push that tag back with `PutTag` where needed. The format is extensible at the field level because unknown high-valued field tags can be skipped only if the reader knows their width; in practice readers switch on known tags.

State and persistence behavior: the header itself has no storage behavior, but `DumpBuffer_t` coordinates persistent file writes or RPC SMARTFTP transfer. `VOLID` aliases `DumpFd` for RPC-style dumps, making the field overloaded.

Dependencies/integration points: depends on Coda volume ids, `VolumeDiskData`, `ViceVersionVector`, and RPC2 types. It is included by `dumpstuff.cc`, `readstuff.cc`, `dumpstream.cc`, `vol-dump.cc`, `codamergedump.cc`, `codareaddump.cc`, and `codadump2tar.cc`.

Risks: the binary ABI assumes fixed Coda structure field meanings and manually serialized 32-bit integers. `DumpBuffer_t::DumpFd` overload is easy to misuse. Tag values are small chars, so signedness matters when comparing with EOF or `D_MAX`. The public API mixes `int`, `unsigned int`, `VolumeId`, and pointer casts, which can become fragile on wider platforms.

Test signals: compile all dump producer/consumer tools together, exercise full and incremental dump round trips, verify magic/version rejection, and fuzz tag streams around structural tags, unexpected EOF, string lengths, and vnode payload sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/dump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/dumpstream.cc -->
## sources/distributed-fs/coda/coda-src/volutil/dumpstream.cc

Purpose: `dumpstream.cc` implements a seekable `FILE*` reader for Coda dump files. It duplicates parts of `readstuff.cc` but adds stream positioning, vnode offset tracking, payload skipping/copying, and direct copy helpers used by merge, inspection, and tar conversion tools.

Important APIs/types/functions: scalar helpers are `GetShort`, `GetInt32`, `GetString`, `GetByteString`, and `GetVV`. `dumpstream` methods include constructor/destructor, `isopen`, `getDumpHeader`, `getVolDiskData`, `getVnodeIndex`, `getNextVnode`, `getVnode`, `copyVnodeData`, `EndOfDump`, `setIndex`, `readDirectory`, `CopyBytesToMemory`, and `CopyBytesToFile`. `PrintDumpHeader` is a diagnostic helper.

Control flow: stream readers parse a structural tag, then consume field tags until the next structural tag and `ungetc` it. `getVnodeIndex` sets the current vnode class and reads count/list-size metadata. `getNextVnode` first calls `skip_vnode_garbage` to consume any previous payload, records the current offset, then parses null, removed, or real vnode records. Directory payloads are read by `readDirectory`; file payloads are copied to memory/file or a `DumpBuffer_t`.

State and persistence behavior: `dumpstream` owns a `FILE*`, a short source name, and current `IndexType`. It is read-only, but can write copied bytes to an output `FILE*` or dump buffer. Seeking only works for named files; stdin use supports sequential operations but not `getVnode`.

Dependencies/integration points: uses `dump.h` tags, Coda vnode/volume structs, directory page constants, `codadir`, external ACL format, `coda_largefile.h`, and dump writer functions for copy-through. A bogus `WriteDump` stub exists to satisfy linkage when dump writer code is pulled in.

Risks: constructor exits on open failure rather than leaving a recoverable error. Destructor always `fclose(stream)`, including stdin. `readDirectory` allocates pages by `npages` without validating against `DIR_MAXPAGES`. Old internal ACL handling reads fixed sizes and probes for 32-bit padding. `CopyBytesToFile` pads to 512-byte tar blocks, so it is tar-specific despite being on the stream class. Error handling often returns `-1` after partial stream movement.

Test signals: parse dumps with large/small indexes, deleted/null vnodes, directories with external ACLs, old-style internal ACLs, files of sizes around 0/1/511/512/513 bytes, and stdin input. Validate `getVnode` offset lookups against sequential reads and verify `EndOfDump` catches postamble bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/dumpstream.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/dumpstream.h -->
## sources/distributed-fs/coda/coda-src/volutil/dumpstream.h

Purpose: `dumpstream.h` declares the C++ `dumpstream` class used for random/sequential access to Coda dump files. It gives utilities a higher-level interface than raw `DumpBuffer_t` reads while still exposing Coda vnode and volume structures.

Important APIs/types/functions: the class stores `FILE *stream`, `name`, `IndexType`, and private `skip_vnode_garbage`. Public APIs read dump headers, volume disk data, vnode index headers, next/specific vnode records, directory pages, file bytes, and dump trailers. `MAXSTRLEN` limits stored filename display. `PrintDumpHeader` is exported for debug output.

Control flow: callers construct with a filename or empty/null for stdin, call `getDumpHeader`, `getVolDiskData`, then `getVnodeIndex` for `vLarge` or `vSmall`. After that, `getNextVnode` returns metadata and leaves the stream before any associated payload; callers either copy/read the payload or let the next stream method skip it. `getVnode` uses a saved offset from a previous scan.

State and persistence behavior: `dumpstream` is a lightweight stateful reader around a dump file handle. It does not persist state beyond the file position and selected vnode class. Copy methods persist to caller-provided output destinations.

Dependencies/integration points: includes LWP/lock headers, `voltypes.h`, `cvnode.h`, and `volume.h`, and depends on `DumpHeader`, `DumpBuffer_t`, `PDirInode`, `VnodeDiskObject`, and `AL_ExternalAccessList` from included Coda headers.

Risks: the header defines `_LARGEFILE_SOURCE` and `_FILE_OFFSET_BITS` after comments but before some includes; consistency with the rest of the build matters. APIs expose raw allocated ACL/directory memory ownership to callers. The class is non-copy-safe by default because it owns a `FILE*` but does not declare copy/move behavior.

Test signals: compile all users after signature changes, run stream consumers on seekable files and stdin, and check ownership discipline for returned `PDirInode` and ACL buffers with leak tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/dumpstream.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/dumpstuff.cc -->
## sources/distributed-fs/coda/coda-src/volutil/dumpstuff.cc

Purpose: `dumpstuff.cc` implements binary dump serialization into a buffered destination. The destination can be a local file descriptor or an RPC2/SMARTFTP connection used by volume dump RPCs.

Important APIs/types/functions: `InitDumpBuf` initializes `DumpBuffer_t`; `FlushBuf` writes buffered bytes to a file or calls `WriteDump` over RPC; `Reserve` allocates contiguous buffer space and flushes when necessary. Serialization functions include `DumpTag`, `DumpByte`, `DumpDouble`, `DumpInt32`, `DumpArrayInt32`, `DumpShort`, `DumpBool`, `DumpString`, `DumpByteString`, `DumpVV`, `DumpFile`, and `DumpEnd`.

Control flow: each `Dump*` call reserves the exact byte count, writes a structural or field tag, and serializes values in explicit big-endian byte order. `DumpFile` writes a size field then streams inode contents in chunks based on `st_blksize`. `DumpEnd` writes the end marker and forces a final flush.

State and persistence behavior: persistent effects are writes to `DumpFd` or remote client transfer through `WriteDump`. `DumpBuffer_t` tracks byte offsets, total bytes, and transfer seconds. On RPC failure, `FlushBuf` marks `rpcid = -1` so later calls fail.

Dependencies/integration points: used by `vol-dump`, `codamergedump`, and `dumpstream::copyVnodeData`. It depends on RPC2 side-effect descriptors, Coda logging, `VolumeId`, `ViceVersionVector`, and `voldump.h` RPC stubs.

Risks: file-write error returns `0` in one path while most failures use `-1`, so callers can miss local write failures. `DumpFile` asserts on short read, aborting the process. `Reserve` assumes one requested item fits in the whole buffer; callers must size the buffer larger than max chunk/page. `DumpString` requires non-NULL NUL-terminated input. Logging uses pointer/integer formatting that may be dated on 64-bit builds.

Test signals: serialize fixed scalar values and compare byte-for-byte big-endian output, dump files with varying block sizes and zero length, force short writes/RPC errors, and verify `DumpEnd` produces a readable trailer. Use valgrind/asan around NULL string or oversized reservation tests if hardening.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/dumpstuff.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/physio.cc -->
## sources/distributed-fs/coda/coda-src/volutil/physio.cc

Purpose: `physio.cc` supplies physical directory I/O callbacks for the Coda directory/buffer package, adapted for salvager-style use with in-memory/RVM-backed directory pages.

Important APIs/types/functions: exported callbacks include `ReallyRead`, `ReallyWrite`, `FidZap`, `FidEq`, and `FidCpy`. It references `DirHandle`, `DirInode`, `shadowDirPage`, `DirHtb`, `VFid`, and `VolumeChanged`. `PAGESIZE` is fixed at 2048 bytes.

Control flow: `ReallyRead` checks the shadow directory hash table first for an uncommitted page matching the directory fid/block, then falls back to the committed `DirInode` page array. `ReallyWrite` creates a new `shadowDirPage`, removes any prior matching shadow page, inserts the new one, and marks `VolumeChanged`. The Fid helpers zero, compare, or copy `DirHandle` values.

State and persistence behavior: writes are staged in the global directory hash table rather than written immediately to recoverable storage; later directory commit logic flushes shadow pages. Reads can observe staged pages before committed pages. The code mutates global `VolumeChanged`.

Dependencies/integration points: integrates with the directory package, Coda vnode/volume structs, `dirvnode.h`, `DirHtb`, and `shadowDirPage`. It is low-level support for volume utilities and salvage/commit flows that manipulate directory pages.

Risks: `while (nsdp = ...)` and similar patterns rely on assignment in condition. No bounds check is performed on `block` before indexing `dinode->Pages`. `ReallyWrite` allocates with `new` and depends on hash-table replacement to avoid leaks. It uses `printf` diagnostics rather than structured logging. The `extern VolumeChanged;` declaration lacks an explicit type in this old C style.

Test signals: directory page read/write unit tests should cover committed-only pages, staged page override, replacement of an existing staged page, missing inode/page behavior, and invalid block indices. Integration tests should commit staged pages and verify directory contents survive salvage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/physio.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/printvldb.cc -->
## sources/distributed-fs/coda/coda-src/volutil/printvldb.cc

Purpose: `printvldb.cc` is a standalone diagnostic program that reads the on-disk VLDB file and prints sorted volume location records. It filters duplicate hash entries and orders output by volume id.

Important APIs/types/functions: macros `VID` and `UNIQUE` derive ids from `struct vldb`. Sorting helpers are `heapify` and `heapsort`. `main` opens `VLDB_PATH`, reads batches of `struct vldb`, filters entries, grows an array, sorts, and prints volume id, key, type, and server numbers.

Control flow: records are read in chunks into a small stack buffer, converted to record counts by `LOG_VLDBSIZE`, filtered to skip numeric-key duplicates, appended to a dynamically grown array, then heap-sorted using 1-based indexing semantics and printed.

State and persistence behavior: read-only. It allocates a process-local VLDB array and prints to stdout; it does not update VLDB files.

Dependencies/integration points: depends on Coda `vldb.h`, `VLDB_PATH`, network byte order helpers, and volume/vnode headers. It is separate from RPC volutil lookup paths and operates directly on the local VLDB file.

Risks: `main` is declared `void`, old C/C++ style. The heap sort expects array elements from index 1, but population starts at index 0; this can leave element 0 unsorted and risks off-by-one behavior. Read sizes not aligned to full records are not explicitly rejected. Filtering by `VID(vldp) != atoi(vldp->key)` assumes numeric keys only represent duplicate id entries.

Test signals: run against synthetic VLDB files with name/id duplicate entries, multiple server counts, empty files, partial final reads, and enough entries to force array growth. Compare output ordering and filtering against expected records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/printvldb.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/readstuff.cc -->
## sources/distributed-fs/coda/coda-src/volutil/readstuff.cc

Purpose: `readstuff.cc` implements buffered deserialization for Coda dump streams from local file descriptors or RPC2/SMARTFTP. It is the inverse of `dumpstuff.cc` for restore-style consumers that do not require random access.

Important APIs/types/functions: private `get` refills the buffer and returns a pointer to requested bytes; private `put` pushes bytes back. Public functions include `ReadTag`, `PutTag`, `ReadShort`, `ReadInt32`, `ReadString`, `ReadByteString`, `ReadVV`, `ReadDumpHeader`, `EndOfDump`, `ReadVolumeDiskData`, and `ReadFile`.

Control flow: `get` preserves unused bytes, refills from RPC `ReadDump` or `read`, updates offsets/counts, and advances `DumpBufPtr`. Scalar readers decode explicit big-endian values. Struct readers consume field tags while tags are above `D_MAX`, then push back the structural tag. `ReadFile` reads the file payload length, then copies chunks to an output `FILE*`.

State and persistence behavior: mutates `DumpBuffer_t` position, offset, byte count, elapsed seconds, and RPC failure state. `ReadFile` writes extracted file content to the caller-provided file. It does not alter Coda volume state.

Dependencies/integration points: used by restore and dump readers that work over RPC or file descriptors. It depends on dump tags from `dump.h`, `VolumeDiskData`, `ViceVersionVector`, `voldump.h` RPC stubs, and Coda logging.

Risks: the local-file refill path reads `DumpBufPtr - DumpBuf` bytes after resetting/copying state, which is subtle and can be error-prone. String truncation logs the adjusted length rather than original length. Unknown field tags cannot be skipped unless known by switch logic, so format extension is limited. `ReadTag` returns `FALSE` on EOF, conflating tag `0`/false states. `put` asserts there is room to move backward.

Test signals: round-trip data written by `dumpstuff.cc`, exercise RPC and file modes, strings at exact/truncated lengths, volume headers with optional fields, malformed VV termination, missing dump end magic, and file payload short reads/writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/readstuff.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/strencode.c -->
## sources/distributed-fs/coda/coda-src/volutil/strencode.c

Purpose: `strencode.c` provides YAML double-quoted string escaping for generated ACL metadata in tar output. It returns an allocated encoded copy suitable for insertion between double quotes.

Important APIs/types/functions: helpers `is_ascii_printable`, `yaml_should_escape`, and `hex_nibble` classify bytes and generate hex digits. The exported API is `yaml_encode_double_quoted_string`.

Control flow: the encoder first scans the input string to determine whether escaping is needed and to compute a worst-case output length. If no byte needs escaping, it returns `strdup(string)`. Otherwise it allocates `len + 1`, then emits either the original byte or YAML-style escapes for control characters, quotes, backslash, and other non-printable bytes using `\xXX`.

State and persistence behavior: no global state. The caller owns the returned heap allocation and must `free` it.

Dependencies/integration points: declared in `dump.h` and used by `codadump2tar.cc` when writing `..CodaACLs.yaml`. It depends only on libc and `assert`.

Risks: input is a C string, so embedded NUL bytes terminate encoding even though ACL names/pathnames may theoretically be byte strings elsewhere. `yaml_should_escape` includes only characters that need escaping in double quotes; forward slash handling is present in the switch but disabled in the predicate. `char *c` reads potentially signed `char` values before passing to unsigned helpers, which can matter for bytes above 0x7f.

Test signals: encode plain ASCII, quotes, backslashes, tabs/newlines/carriage returns, ESC, bytes above 0x7f, and empty strings. Verify returned strings parse as YAML double-quoted scalars and memory ownership is clean under ASAN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/strencode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/tar-FromRedHatCD.h -->
## sources/distributed-fs/coda/coda-src/volutil/tar-FromRedHatCD.h

Purpose: `tar-FromRedHatCD.h` is a bundled GNU tar archive-format definition used by `codadump2tar.cc` to construct tar headers without relying on the system `<tar.h>`.

Important APIs/types/functions: it defines `struct posix_header`, GNU sparse/extra/oldgnu header structs, tar typeflag constants (`REGTYPE`, `LNKTYPE`, `SYMTYPE`, `DIRTYPE`, etc.), permission bit constants, `BLOCKSIZE`, GNU extension type constants, `enum archive_format`, and `union block`.

Control flow: no executable flow; it provides layout and constants. `TarRecd` writes into `union block.header`, fills POSIX fields, computes checksums over `BLOCKSIZE`, and writes the raw block.

State and persistence behavior: none directly. Its struct layout defines the persistent tar bytes emitted by the converter.

Dependencies/integration points: included only by `codadump2tar.cc` in this subset. The comments describe GNU tar historical compatibility; `codadump2tar` uses the POSIX header portion and basic type constants, not sparse extensions.

Risks: this is a copied historical header under GPL terms and may differ from modern tar semantics. Fixed arrays enforce classic ustar limits: 100-byte name, 155-byte prefix, 100-byte linkname, and octal size fields. The converter does not implement GNU long-name records, so paths beyond these limits are truncated before using this layout.

Test signals: verify generated headers with GNU tar and bsdtar, including directory, file, symlink, and hard-link records; validate checksum calculation and zero trailer. Include boundary names/prefixes and sizes near octal field limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/tar-FromRedHatCD.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-ancient.cc -->
## sources/distributed-fs/coda/coda-src/volutil/vol-ancient.cc

Purpose: `vol-ancient.cc` advances dump version-vector list files by marking a newly generated list as the ancient baseline for future incremental dumps.

Important APIs/types/functions: `S_NewVolMarkAsAncient` accepts a backup volume id, attaches the volume, derives the parent replicated group id through `VRDB.ReverseFind`, and calls `S_VolMarkAsAncient`. `S_VolMarkAsAncient` builds list paths with `getlistfilename` and renames `newlist` to `ancient`.

Control flow: the new-style RPC gets the backup volume, discovers group/parent ids, delegates, then releases the volume. The underlying operation initializes volutil, computes source and destination list filenames, renames atomically at the filesystem level, disconnects, and returns RPC success or failure.

State and persistence behavior: the persistent state is the list file rename, typically used by `vol-dump` to decide what changed since the previous backup. It also attaches/releases volumes but does not mutate volume RVM data.

Dependencies/integration points: integrates with `VGetVolume`, `VPutVolume`, `VRDB`, and `vvlist.h` filename conventions. It is part of the incremental dump workflow: successful `S_VolNewDump` writes `newlist`, and this RPC promotes it after the client accepts the dump.

Risks: if `rename` fails, future incrementals may fall back to full dumps or use stale baselines. There is no explicit cleanup of an existing destination before rename, so platform rename semantics matter. `S_NewVolMarkAsAncient` does not call `VInitVolUtil` before `VGetVolume`; it relies on caller/server context or delegated call behavior. Group id defaults to 0 when no VRDB entry exists.

Test signals: run after successful full and incremental dumps, verify expected `newlist` to `ancient` transition, missing source file failure, existing destination behavior, non-replicated volumes, and replicated VRDB reverse lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-ancient.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-backup.cc -->
## sources/distributed-fs/coda/coda-src/volutil/vol-backup.cc

Purpose: `vol-backup.cc` implements server-side backup-volume creation and refresh. It can create a new backup clone or update an existing backup clone in place to match a locked read-write/non-replicated volume.

Important APIs/types/functions: main RPC `S_VolMakeBackups` coordinates the operation. Helpers include `MakeNewClone`, `ModifyIndex`, `purgeDeadVnodes`, `updateBackupVnodes`, `deleteDeadVnode`, `cleanup`, and debug `checklists`. It reuses `VUCloneVolume`/`CloneVnode` from clone logic.

Control flow: `S_VolMakeBackups` initializes volutil, attaches the original, verifies type and that volutil holds the volume lock, then tries to attach the existing backup id. If no valid backup exists, `MakeNewClone` allocates/creates/clones a backup volume, deletes/renumbers old backup if present, and sets backup metadata. If a backup exists, it marks it unblessed/destroy-me, updates small and large vnode indexes to match the RW volume, copies the RW version vector, then blesses and updates both volumes. It releases volumes and unlocks the original at the end.

State and persistence behavior: heavily mutates RVM volume headers, vnode list structures, directory inode references, inode reference counts, backup id/date, blessed/destroyMe flags, and hash tables. Vnode updates are batched in transactions limited by `MaxVnodesPerTransaction`; inode decrements are delayed until after transaction commit to avoid abort inconsistencies.

Dependencies/integration points: depends on volutil initialization, volume locks, RVM transaction APIs, vnode index/list structures, inode operations (`idec`), directory inode refcounts, volume hash functions, `CloneVnode`, and Coda server globals.

Risks: correctness depends on the `cloned` bit and version-vector comparisons accurately identifying changed data and metadata. Many paths use `CODA_ASSERT`, so production corruption can abort. Lock identity is a magic IP address value (`5`). In-place update manipulates shared vnode structures and inode refcounts; transaction/inode ordering bugs can leak or prematurely delete data. Debug output may write `/vicepa/dcstest`.

Test signals: backup RW and non-replicated volumes with file creation/deletion/modification, directory changes, metadata-only changes, barren inodes, grown vnode lists, existing/absent old backups, and crash/restart around unblessed/destroyMe states. Verify inode refcounts, vnode counts, backup readability, and unlock behavior on errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-backup.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-clone.cc -->
## sources/distributed-fs/coda/coda-src/volutil/vol-clone.cc

Purpose: `vol-clone.cc` creates read-only clones of existing read-write, read-only, or non-replicated volumes and implements the shared low-level vnode cloning routine used by backup creation.

Important APIs/types/functions: RPC `S_VolClone` creates a new readonly clone. Internal APIs include `VUCloneVolume`, `VUCloneIndex`, and exported/shared `CloneVnode`. Global `MaxVnodesPerTransaction` bounds transaction batches.

Control flow: `S_VolClone` initializes volutil, validates optional new name against VLDB, attaches the source volume, locks RW/non-replicated sources, allocates a new id, creates an unblessed readonly volume, clones all large then small vnodes, assigns a name, sets metadata, blesses/detaches the clone, updates the original `cloneId`, releases the write lock, and returns the clone id. `VUCloneIndex` replaces the destination vnode lists, then iterates source vnodes in transactions, calling `CloneVnode` for each. `CloneVnode` copies vnode metadata, increments directory or file inode references when possible, creates empty inodes for barren/zero-inode cases, marks source vnode cloned, clears readonly inconsistency/cloned flags, and appends to the clone list.

State and persistence behavior: mutates RVM volume records, vnode lists, source vnode cloned bits, inode reference counts, directory inode refcounts, volume names/types/dates/stats, and volume locks. New clones are unblessed until fully populated.

Dependencies/integration points: interacts with VLDB lookup, RVM allocation/transactions, `VCreateVolume`, `VUCloneVolume`, `VGetVnode`, inode operations (`iinc`, `icreate`), directory inode refs, volume hash/server globals, and resolution flags.

Risks: failure paths must release locks and put volumes; several use assertions rather than recovery. New volume creation and clone population are separate phases, so crash recovery depends on unblessed/destroy flags and salvage. Source vnode mutation (`cloned = 1`) is part of copy-on-write correctness. `newvolname` logic treats an empty RPC string differently from NULL and can assign names unexpectedly.

Test signals: clone RW, RO, and non-replicated volumes; reject invalid source types and duplicate names; verify lock conflict returns `EWOULDBLOCK`; test files, directories, symlinks, barren inodes, resolution logs, and transaction batching. Validate clone has independent volume metadata but shared/incremented backing data until copy-on-write.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-clone.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-create.cc -->
## sources/distributed-fs/coda/coda-src/volutil/vol-create.cc

Purpose: `vol-create.cc` creates new read-write or replicated Coda volumes and initializes their root directory with administrator ACLs.

Important APIs/types/functions: RPC `S_VolCreate` handles volume allocation/creation. `ViceCreateRoot` creates the root large vnode and physical directory. It references `PrintVnode` for debug output and uses `PRS_ADMINGROUP`, `AL_AccessList`, `VnodeDiskObject`, and `vindex`.

Control flow: `S_VolCreate` initializes volutil, begins an RVM transaction, allocates or accepts a volume id, updates max id if needed, validates replicated group id, creates the volume, sets initial header fields/name/type, calls `ViceCreateRoot`, clears salvage/destroy state, updates/detaches the volume, commits, flushes RVM, disconnects, and returns the id. `ViceCreateRoot` resolves the admin group id, creates a directory handle and `.`/`..` root directory, builds an ACL granting all rights to administrators, fills vnode fields, commits the directory, optionally creates a resolution log, writes the vnode to the large vnode index, and updates disk usage.

State and persistence behavior: creates persistent RVM volume metadata, vnode index entries, directory inode data, ACL data, optional resolution log, and max volume id state. It runs the root creation and volume update in one transaction for version-vector consistency.

Dependencies/integration points: depends on volutil/RVM, partition and volume creation code, protection database lookup, directory/vnode commit APIs, resolution logging, and server globals such as `AllowResolution`.

Risks: user-supplied explicit volume ids can advance max volume id and may collide if external validation is incomplete. Root ACL creation fails if the PDB admin group is unavailable. `ViceCreateRoot` uses stack buffers cast to vnode types and assumes `SIZEOF_LARGEDISKVNODE`. Several operations assert after commit-related calls. The global `Error error` is file-scope.

Test signals: create non-replicated and replicated volumes, explicit and allocated ids, missing admin group failure, invalid replicated group id, root directory lookup, ACL rights, volume detach/reattach, and resolution-log creation when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-create.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-dump.cc -->
## sources/distributed-fs/coda/coda-src/volutil/vol-dump.cc

Purpose: `vol-dump.cc` implements server-side Coda volume dump and dump-size estimation. It serializes readonly/backup volumes to the dump format over RPC2 SMARTFTP and maintains version-vector list files for incremental dumps.

Important APIs/types/functions: RPCs are `S_VolNewDump` and `S_VolDumpEstimate`. Serialization helpers include `DumpDumpHeader`, `DumpVolumeDiskData`, `DumpVnodeDiskObject`, `DumpVnodeIndex`, `DumpVnodeDiskObject_estimate`, and `DumpVnodeIndex_estimate`. It uses `vvtable`, `ListVV`, `DumpListVVHeader`, `ValidListVVHeader`, and `getlistfilename`.

Control flow: `S_VolNewDump` initializes volutil, attaches the requested volume, rejects RW/non-replicated sources for dumping, allocates a dump buffer, determines a replicated or non-replicated uniquifier baseline, opens a `newlist`, optionally opens/validates `ancient` for incremental mode, binds back to the client dump subsystem, then writes header, volume disk data, large index, small index, and dump end. `DumpVnodeIndex` writes count/list metadata, then either emits all vnodes for full dumps or compares against the ancient VV table to emit modified/new vnodes and `D_RMVNODE` records for deletions. `S_VolDumpEstimate` walks similar state to populate level estimates.

State and persistence behavior: writes dump bytes to the client, writes a new VV list file, reads an ancient VV list file, and updates only transient volume attachment state. On dump failure it unlinks the new list. It does not mutate the dumped volume except normal attach/put behavior.

Dependencies/integration points: relies on `dumpstuff.cc`, volume/vnode/index iterators, inode open/read, directory page access, ACL externalization, RPC2 binding/side effects, VRDB reverse translation, and VV-list incremental logic. `vol-ancient.cc` promotes successful new lists.

Risks: only readonly/backup volumes can be dumped; callers must clone/backup first. Incremental correctness depends on valid ancient list files and version-vector/store-id comparisons. `DumpVnodeDiskObject_estimate` uses `VAclDiskSize` while actual dump externalizes ACL strings, so estimates can drift. `DumpVnodeIndex` decrements `nVnodes` while iterating and relies on list consistency. `D_BADINODE` records are emitted for missing file inodes, producing lossy dumps.

Test signals: full and incremental dump/restore flows, invalid ancient list fallback to full, deletion records, large and small vnodes, directory ACLs, missing/barren inode handling, RPC failures, dump estimate monotonicity across levels, and cleanup of `newlist` on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-dump.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-dumpvrdb.cc -->
## sources/distributed-fs/coda/coda-src/volutil/vol-dumpvrdb.cc

Purpose: `vol-dumpvrdb.cc` dumps the in-memory Volume Replication Database to a text file in the format expected by VRDB rebuild tools.

Important APIs/types/functions: the sole RPC is `S_VolDumpVRDB`, which accepts an output filename, opens it with `O_CREAT | O_EXCL | O_WRONLY`, calls `DumpVRDB(fd)`, closes the descriptor, and returns `0` or `VFAIL`.

Control flow: validate by attempting exclusive file creation, delegate all formatting to `DumpVRDB`, clean up the descriptor, and map any open/dump error to volutil failure.

State and persistence behavior: writes a caller-specified filesystem path. It does not mutate VRDB or volume state. Exclusive creation prevents overwriting existing files.

Dependencies/integration points: depends on `vrdb.h`, `DumpVRDB`, volutil RPC types, and Coda logging. Its output should be compatible with `S_VolMakeVRDB` outside this subset.

Risks: the server writes to an arbitrary path supplied by the RPC caller, subject to process permissions. It does not initialize volutil in this function. Error detail is collapsed to `VFAIL`. No side-effect transfer is used; the file remains on the server filesystem.

Test signals: dump to a fresh path, reject existing path, permission-denied paths, empty/non-empty VRDB contents, and parse the result with the VRDB loader.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-dumpvrdb.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-getvolumelist.cc -->
## sources/distributed-fs/coda/coda-src/volutil/vol-getvolumelist.cc

Purpose: `vol-getvolumelist.cc` returns the server's in-RVM volume list to a volutil client using an RPC2 SMARTFTP side effect.

Important APIs/types/functions: `S_GetVolumeList` calls `VListVolumes(&buf, &buflen)`, prepares an `SE_Descriptor` with `FILEINVM`, sends the memory buffer to the client with `RPC2_InitSideEffect` and `RPC2_CheckSideEffect`, frees the buffer, and returns the RPC result.

Control flow: collect list, configure side effect as server-to-client memory transfer, initialize transfer, wait for local completion, log result, free memory.

State and persistence behavior: read-only with respect to volume state. It allocates a heap buffer for the list and transfers it over RPC; no server file is written.

Dependencies/integration points: depends on `VListVolumes`, RPC2 SMARTFTP descriptors, volutil RPC service, and Coda logging. It is likely used by administrative clients to enumerate volumes.

Risks: it does not call `VInitVolUtil`, so correctness depends on server context already having volume state initialized. If `RPC2_InitSideEffect` returns a positive nonzero code, the `!rc` guard can skip `CheckSideEffect`, depending on RPC2 return conventions. Large volume lists require a contiguous memory buffer.

Test signals: empty and populated volume lists, large lists, side-effect failures, client disconnects, and leak checks around `free(buf)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-getvolumelist.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-info.cc -->
## sources/distributed-fs/coda/coda-src/volutil/vol-info.cc

Purpose: `vol-info.cc` generates a textual report for a Coda volume and transfers it to the client. It can include volume header metadata, resolution logs/stats, and optionally all vnode records.

Important APIs/types/functions: RPC `S_VolInfo` resolves a volume key, attaches the volume, writes `/tmp/volinfo.tmp`, and transfers it. Helpers are `PrintHeader`, `printvns`, `PrintVnode`, `date`, and `typestring`.

Control flow: initialize volutil, locate volume id with `VOL_Locate`, attach via `VGetVolume`, open the temp file, print header fields, print resolution log/statistics if enabled, optionally iterate large and small vnode indexes, close file, put volume, then send the file using SMARTFTP `FILEBYNAME`.

State and persistence behavior: creates/overwrites a fixed temp file `/tmp/volinfo.tmp` and reads volume/vnode state. It does not mutate the volume except resolution stats pre/post collection may update in-memory statistic state.

Dependencies/integration points: integrates with volume lookup/attachment, vnode index iterators, resolution logs (`V_VolLog`), stats, RPC2 side effects, and shared `PrintVnode` used by `vol-create` debug code.

Risks: fixed temp filename is race-prone and unsafe under concurrent requests. The function does not check `fopen` failure before printing. Date formatting uses `localtime` and `sprintf` into caller buffer. `VInitVolUtil` return is ignored. It exposes raw vnode inode/dir-node pointer values in text output.

Test signals: request by name and id, invalid volume key, `dumpall` on/off, volumes with resolution enabled/disabled, concurrent requests, side-effect failure, and file permission/temp directory failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-info.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-lock.cc -->
## sources/distributed-fs/coda/coda-src/volutil/vol-lock.cc

Purpose: `vol-lock.cc` provides volutil RPCs to lock and unlock a volume, primarily for backup coordination.

Important APIs/types/functions: `S_VolLock` attaches a volume, checks `V_VolLock(vol).IPAddress`, obtains the write lock, stamps the lock owner, copies the volume version vector to the caller, and releases the volume attachment. `S_VolUnlock` attaches the volume, verifies a nonzero lock owner, clears it, releases the write lock, and disconnects.

Control flow: both RPCs initialize volutil, get the volume, operate on `V_VolLock`, put the volume, and disconnect. Lock failure returns `EWOULDBLOCK`; unlocking an unlocked volume returns `EINVAL`.

State and persistence behavior: mutates in-memory volume lock state and lock primitive state. It does not appear to persist lock owner to disk. The returned `ViceVersionVector` is a snapshot used by backup clients.

Dependencies/integration points: used by backup tooling before `S_VolMakeBackups`; that code verifies owner `IPAddress == 5`. Depends on volume attach/put, LWP locks, and Coda logging.

Risks: lock owner identity is a magic constant (`5`) with comments saying it needs changing; RPC caller identity is not recorded. No timeout queue is active despite comments. `S_VolUnlock` releases any nonzero owner, not specifically the caller's lock. Error paths must avoid leaving locks held.

Test signals: lock/unlock success, double lock returns `EWOULDBLOCK`, unlock unlocked returns `EINVAL`, backup sees owner `5`, failure after `ObtainWriteLock`, and concurrent callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-lock.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-lookup.cc -->
## sources/distributed-fs/coda/coda-src/volutil/vol-lookup.cc

Purpose: `vol-lookup.cc` returns human-readable VLDB/location information for a volume specified by name or id.

Important APIs/types/functions: RPC `S_VolLookup` writes `/tmp/vollookup.tmp` and transfers it with SMARTFTP. It uses `VGetVolumeInfo`, `HashLookup`, `SRV_RVM(VolumeList[index]).data.volumeInfo`, `gethostbyaddr`, and a local `voltypes` string table.

Control flow: initialize volutil, open temp output, parse the input as a hex volume id if possible and present in the volume hash, otherwise treat it as a name. Fetch `VolumeInfo`, print primary volume id/type, associated read-write/readonly/backup ids, and server hostnames, then transfer the temp file to the client.

State and persistence behavior: read-only against volume/VLDB state. Creates/overwrites fixed `/tmp/vollookup.tmp` on the server.

Dependencies/integration points: depends on volume hash, VLDB, volume info service, host DNS lookup, RPC2 side effects, and server RVM volume list state.

Risks: fixed temp filename is unsafe under concurrency. If `VGetVolumeInfo` fails, the function jumps to exit without closing `infofile`, leaking the descriptor and leaving a partial file. `status` is never set on lookup error, so error return behavior can be misleading. Hostname output skips numeric fallback when reverse lookup fails.

Test signals: lookup by name, by hex id, invalid key, missing reverse DNS, multi-server replicated volumes, concurrent lookups, and side-effect failure. Check descriptor cleanup on errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/volutil/vol-lookup.cc -->
