# Group Research: group_153_9front_sources_os_plan9_9front_sys_src_cmd_gs_zlib_zlib_h_sources_os_d8400c8fc0cb

Scope: `Docs/research_subset_a.md`, specifically `sources/os/plan9/9front`. I read all 32 listed source files completely. The supplied internal group report path was not present in the workspace, so this report is based on the source files themselves.

This group covers four nearby Plan 9 command areas: bundled Ghostscript zlib API/support files, native gzip/zip tools using Plan 9 `<flate.h>`, an interactive graph viewer, Mercurial revlog-backed 9P filesystem tooling, a live histogram UI, and the front half of `hjfs`, a buffered/authenticated 9P filesystem server.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/zlib.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/zlib.h

Defines the public zlib 1.2.2 API bundled under Ghostscript.

Key points:
- Identifies `ZLIB_VERSION` as `1.2.2` and `ZLIB_VERNUM` as `0x1220`.
- Declares the `z_stream` structure, allocator hooks, stream state pointer, byte counters, `data_type`, checksum field, and reserved field.
- Defines canonical zlib flush values, return codes, compression levels, compression strategies, data type hints, the deflate method, and `Z_NULL`.
- Documents and declares stream APIs:
  - `deflate`, `deflateEnd`, `deflateSetDictionary`, `deflateCopy`, `deflateReset`, `deflateParams`, `deflateBound`
  - `inflate`, `inflateEnd`, `inflateSetDictionary`, `inflateSync`, `inflateReset`
  - `deflateInit2_`, `inflateInit2_`, and version/structure-size checking macros
  - `inflateBack`, `inflateBackEnd`, and `inflateBackInit_`
- Declares utility APIs:
  - `compress`, `compress2`, `compressBound`, `uncompress`
  - gzip file interface: `gzopen`, `gzdopen`, `gzread`, `gzwrite`, `gzprintf`, `gzputs`, `gzgets`, `gzputc`, `gzgetc`, `gzungetc`, `gzflush`, `gzseek`, `gzrewind`, `gztell`, `gzeof`, `gzclose`, `gzerror`, `gzclearerr`
  - checksums: `adler32`, `crc32`
  - introspection: `zlibVersion`, `zlibCompileFlags`, `zError`, `inflateSyncPoint`, `get_crc_table`
- The long comments are part of the API contract: caller ownership of input/output pointers, flush semantics, dictionary behavior, raw/gzip/zlib wrapper options, and expected return-code handling.

Dependencies and interactions:
- Includes `zconf.h` for portability types and export macros.
- Implemented by the rest of the bundled zlib sources under `cmd/gs/zlib`.
- Used as the external-facing compression ABI for Ghostscript’s vendored zlib copy.

Research relevance:
- This is a third-party bundled interface, not Plan 9-specific filesystem code, but it is important dependency surface for Ghostscript compression, gzip stream, checksum, and inflate/deflate behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/zlib.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/zutil.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/zutil.c

Implements target-dependent utility functions for the bundled zlib library.

Key points:
- Defines `z_errmsg[]`, indexed through `ERR_MSG`, for zlib return-code strings.
- `zlibVersion()` returns `ZLIB_VERSION`.
- `zlibCompileFlags()` encodes compile-time size, compiler, assembler, debug, table-generation, missing-feature, and sprintf/snprintf options into a bitfield.
- Under `DEBUG`, provides `z_verbose` and fatal `z_error()`.
- `zError()` exposes error-code-to-string conversion.
- Provides fallback `zmemcpy`, `zmemcmp`, and `zmemzero` when `HAVE_MEMCPY` is unavailable.
- Contains legacy 16-bit allocation implementations for Turbo C and Microsoft C.
- Default `zcalloc()`/`zcfree()` use `malloc` or `calloc` depending on `sizeof(uInt)` and call `free`.

Dependencies and interactions:
- Includes `zutil.h`.
- Supplies allocation and memory routines used by deflate/inflate internals.
- Error strings are used by `ERR_RETURN` and public `zError()`.

Research relevance:
- This is the portability and allocator layer for the vendored zlib copy. It preserves old platform compatibility even though the Plan 9 build path mainly uses the normal allocator branch.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/zutil.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/zutil.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/zutil.h

Defines internal zlib configuration, constants, diagnostics, memory helpers, and target portability macros.

Key points:
- Marks itself as internal and includes `zlib.h` with `ZLIB_INTERNAL`.
- Defines internal aliases `uch`, `ush`, `ulg`, `local`, and error helpers `ERR_MSG` and `ERR_RETURN`.
- Sets common compression constants:
  - `DEF_WBITS`
  - `DEF_MEM_LEVEL`
  - block types `STORED_BLOCK`, `STATIC_TREES`, `DYN_TREES`
  - match lengths `MIN_MATCH`, `MAX_MATCH`
  - zlib preset dictionary flag
- Maps operating-system codes for gzip headers across DOS, Amiga, VMS, Atari, OS/2, Mac, TOPS20, Win32, Prime, BeOS, RISC OS, and default Unix.
- Provides `F_OPEN` abstraction and `fdopen` compatibility shims.
- Detects `vsnprintf`, `strerror`, and memcpy availability.
- Maps `zmemcpy`, `zmemcmp`, and `zmemzero` to libc or fallback functions.
- Defines debug macros `Assert`, `Trace`, `Tracev`, `Tracevv`, `Tracec`, `Tracecv`.
- Declares `zcalloc` and `zcfree`, and wraps stream alloc/free through `ZALLOC`, `ZFREE`, and `TRY_FREE`.

Dependencies and interactions:
- Used by zlib implementation files, not applications.
- Depends on `zconf.h` via `zlib.h`.
- Paired with `zutil.c`.

Research relevance:
- This is the internal portability contract for the vendored compression library and explains how the same source is configured for Plan 9’s Ghostscript build.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/zlib/zutil.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gview.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gview.c

Implements `gview`, an interactive graphical viewer/editor for labeled 2D polygonal line graphs.

Key points:
- Reads ASCII input containing one `x y` point per line, with a label terminating each polyline.
- Maintains a linked list of `fpolygon` objects under global `fpolygons univ`.
- Computes floating-point bounding boxes, display windows, transforms, slanted views, zoom-in/zoom-out regions, recentering, and square aspect adjustment.
- Draws a Plan 9 window using `draw` and `event`, including frame, axis ticks, numeric labels, unit scaling text, colors, and selected-point markers.
- Supports label-driven colors and thickness:
  - explicit names such as `Red`, `Blue`, `Dkgreen`
  - `Thick`
  - `Multi(...)` schemes selectable by key
- Provides clipping against the visible parallelogram before drawing or selecting paths.
- Selection logic finds the nearest point or path segment within a tolerance rectangle after applying the active slant transform.
- Editing features include recolor, thicken/thin, delete, undo, move, rotate, restack, read more data, and write data.
- Optional `-l` logs selected coordinates and labels; `-m` enables movement/rotation; `-p` plots vertices as dots.
- Uses Plan 9 mouse buttons:
  - button 1 selects and optionally drags
  - button 2 opens edit menu
  - button 3 opens main menu

Dependencies and interactions:
- Uses Plan 9 `<draw.h>`, `<event.h>`, and `<cursor.h>`, plus libc and stdio.
- No filesystem implementation dependency, but it reads and writes local graph data files.
- State is largely global and event-driven.

Research relevance:
- A self-contained interactive command that demonstrates Plan 9 graphical UI patterns, event handling, text prompting, geometry transforms, and file-backed editing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gview.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gzip/gunzip.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gzip/gunzip.c

Implements Plan 9 `gunzip`.

Key points:
- Parses options:
  - `-c` write decompressed output to stdout
  - `-t` list/test table mode
  - `-T` set output modification times from gzip metadata
  - `-v` verbose
  - `-D` debug
- Uses Plan 9 `<flate.h>` `inflateinit()` and `inflate()`.
- Validates gzip magic bytes and compression method before processing file inputs.
- Generates output names by removing `.gz`, mapping `.tgz` to `.tar`, or refusing to overwrite unchanged names.
- Supports concatenated gzip members by repeatedly reading headers, inflating, checking trailers, and continuing until EOF.
- Parses gzip header fields including optional extra data, original filename, comment, and header CRC.
- Maintains CRC and uncompressed length through `crcwrite()`, using `mkcrctab(GZCRCPOLY)` and `blockcrc`.
- Validates trailer CRC and output length.
- Uses `setjmp`/`longjmp` to abort a bad member and remove partially written output files.
- In table mode, prints embedded names and optional size/time information without writing output.

Dependencies and interactions:
- Includes `gzip.h` for gzip constants.
- Uses Plan 9 `Biobuf`, file descriptors, `Dir`, and `<flate.h>` callbacks.
- Shares gzip format constants with `gzip.c`.

Research relevance:
- Native Plan 9 gzip decompressor wrapper around the system flate library, with filesystem-safe output handling and trailer integrity checks.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gzip/gunzip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gzip/gzip.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gzip/gzip.c

Implements Plan 9 `gzip`.

Key points:
- Parses options:
  - `-c` write compressed output to stdout
  - `-n` suppress stored modification time
  - `-v` verbose
  - `-D` debug
  - `-1` through `-9` compression level
- Initializes Plan 9 deflate support with `deflateinit()`.
- For file inputs, rejects directories, derives output names, and maps `.tar` to `.tgz`.
- Writes a gzip header with magic bytes, deflate method, optional filename, modification time, extra flags, and OS code.
- Uses `deflate()` with `crcread()` input and `gzwrite()` output callbacks.
- Tracks CRC and total uncompressed bytes while reading.
- Writes gzip trailer CRC and original length in little-endian order.
- On write failure, removes incomplete non-stdout output.

Dependencies and interactions:
- Includes `gzip.h` for constants.
- Uses Plan 9 `<flate.h>` rather than vendored zlib.
- Paired with `gunzip.c`.

Research relevance:
- Minimal gzip creator around Plan 9’s flate callback API and gzip wire-format framing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gzip/gzip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gzip/gzip.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gzip/gzip.h

Defines gzip header constants used by `gzip.c` and `gunzip.c`.

Key points:
- Defines gzip magic bytes `0x1f`, `0x8b`.
- Defines compression method `GZDEFLATE`.
- Defines gzip header flag bits:
  - `GZFTEXT`
  - `GZFHCRC`
  - `GZFEXTRA`
  - `GZFNAME`
  - `GZFCOMMENT`
  - `GZFMASK`
- Defines extra flag values `GZXFAST` and `GZXBEST`.
- Defines gzip OS identifiers from FAT through Acorn RISCOS and unknown.
- Defines CRC polynomial `GZCRCPOLY`.
- Maps Plan 9/Inferno output OS code to Unix via `GZOSINFERNO = GZOSUNIX`.

Dependencies and interactions:
- Shared by gzip compressor and decompressor.
- Constants match RFC 1952 gzip framing.

Research relevance:
- Small format contract header for the native gzip tools.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gzip/gzip.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gzip/unzip.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gzip/unzip.c

Implements Plan 9 `unzip`.

Key points:
- Parses options:
  - `-a` automatically create missing parent directories
  - `-c` write file contents to stdout
  - `-i` lower-case extracted/listed names
  - `-s` stream mode using local file headers instead of central directory seeks
  - `-t` table/list mode
  - `-T` set extracted modification times
  - `-v` verbose
  - `-D` debug
  - `-f zipfile` select archive file, otherwise stdin
- Supports both central directory mode and streaming local-header mode.
- `findCDir()` searches backwards for the end-of-central-directory record, reads entry counts and central-directory offset, then seeks to the directory.
- `cheader()` parses central directory entries; `header()` parses local file headers.
- `unzipEntry()` extracts one entry, creating directories or files, honoring stdout, optional auto-parent creation, and DOS directory attributes.
- Supports stored method `0` and deflate method `8`; rejects unsupported compression methods.
- Uses Plan 9 `inflate()` for deflated entries and direct copy for stored entries.
- Validates CRC, uncompressed size, and compressed size.
- Handles data-descriptor trailers when `ZTrailInfo` is set, including Apple-style optional signature `0x08074b50`.
- `wantFile()` supports exact requested files and requested directory prefixes.
- Uses `setjmp`/`longjmp` for per-entry error handling and a separate jump path to retry non-seekable input in stream mode.

Dependencies and interactions:
- Includes `zip.h`.
- Uses Plan 9 `Biobuf`, `<flate.h>`, directories, and file descriptors.
- Shares CRC polynomial and ZIP constants with `zip.c`.

Research relevance:
- Full native ZIP extractor/listing tool with both seekable and streaming archive handling, important for Plan 9 archive/file workflow.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gzip/unzip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gzip/zip.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gzip/zip.c

Implements Plan 9 `zip`.

Key points:
- Parses options:
  - `-f zipfile` write archive to named file, otherwise stdout
  - `-v` verbose
  - `-D` debug
  - `-1` through `-9` compression level
- Recursively archives input files and directories.
- Builds an in-memory array of `ZipHead` records for later central-directory emission.
- For each file:
  - records DOS-style version fields
  - converts Plan 9 `Dir` mtime into MS-DOS time/date
  - sets DOS external attributes
  - stores local-header offset
  - compresses regular files with deflate method `8`
- Directory entries are stored with method `0` and trailing slash names.
- When writing to stdout, sets `ZTrailInfo` and writes CRC/size data after compressed data; otherwise seeks back into the local header to fill CRC and sizes.
- `putCDir()` emits all central-directory entries and the end-of-central-directory record.
- Uses `crcread()` to feed data while computing CRC and uncompressed length, and `zwrite()` to count compressed bytes.
- Aborts through `longjmp` and removes a named output archive on fatal error.

Dependencies and interactions:
- Includes `zip.h`.
- Uses Plan 9 `<flate.h>` `deflate()`.
- Paired with `unzip.c`.

Research relevance:
- Native ZIP writer covering recursive directory traversal, local headers, central directory construction, streamed archive output, and CRC/size bookkeeping.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gzip/zip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gzip/zip.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gzip/zip.h

Defines ZIP format constants and the shared `ZipHead` structure.

Key points:
- Defines local, central, and end-central magic numbers:
  - `ZHeader`
  - `ZCHeader`
  - `ZECHeader`
- Defines general-purpose flag bits:
  - `ZEncrypted`
  - `ZTrailInfo`
  - `ZCompPatch`
- Defines ZIP CRC polynomial `ZCrcPoly`.
- Defines compression method `ZDeflate = 8`.
- Defines internal text attribute and OS identifiers for version fields.
- Defines DOS external attribute flags, including read-only, hidden, system, volume label, directory, and archive.
- Defines byte sizes/offsets for local headers, trailers, central headers, and end-central headers.
- `ZipHead` stores version info, flags, method, timestamps, CRC, compressed/uncompressed sizes, attributes, local-header offset, and filename.

Dependencies and interactions:
- Shared by `zip.c` and `unzip.c`.
- Encodes exactly the subset of ZIP metadata those tools read/write.

Research relevance:
- The common ZIP metadata contract for Plan 9 archive creation and extraction.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gzip/zip.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hgfs/ancestor.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/hgfs/ancestor.c

Finds a common Mercurial ancestor revision hash through a mounted `hgfs` tree.

Key points:
- Defines temporary `XNode` records with hash, traversal mark, hash-table link, and queue link.
- Uses a 256-bucket hash table keyed by the first hash byte.
- Handles equal hashes and `nullid` inputs as fast paths.
- Performs alternating breadth-first expansion from `xhash` and `yhash`.
- Reads each revision’s `rev1` and `rev2` files from the mounted `hgfs` namespace to discover parents.
- Stops when a node already marked from the opposite side is found.
- Returns `nullid` when no common ancestor exists.
- Frees all allocated traversal nodes before returning.

Dependencies and interactions:
- Uses `readhash()` and `%H` formatting from `hash.c`.
- Depends on `hgfs` exposing revision directories with `rev1` and `rev2`.

Research relevance:
- Ancestor discovery utility used by the update/merge planner in `hgdb.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hgfs/ancestor.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hgfs/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/hgfs/dat.h

Defines core data structures for `hgfs`.

Key points:
- Sets constants:
  - `MAXPATH = 1024`
  - `BUFSZ = 1024`
  - `HASHSZ = 20`
- Declares structures:
  - `Revmap`: one revlog index entry, including revision numbers, parent/base/link revisions, hash, flags, data offsets/lengths, full length, and aux pointer.
  - `Revlog`: opened revlog state, index/data file descriptors, parsed map, temp extraction cache, and refcount.
  - `Revnode`: manifest tree node with name, file hash, qid-derived path, parent/sibling/child links, historical `before` link, and mode.
  - `Revinfo`: parsed changelog metadata, including changelog hash, manifest hash, author, message, time, log offset/length.
  - `Revtree`: refcounted tree wrapper.
  - `Revfile`: per-9P-fid state for current level, revision info/tree/node/revlog, opened temp file, metadata offset, and buffered string.
- Defines global `nullid`.

Dependencies and interactions:
- Included by all `hgfs` C files.
- Structures are populated by `revlog.c`, `info.c`, and `tree.c`, and served by `fs.c`.

Research relevance:
- Central schema for the Mercurial revlog-backed 9P filesystem.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hgfs/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hgfs/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/hgfs/fns.h

Declares all `hgfs` helper APIs.

Key points:
- Hash helpers:
  - `Hfmt`, `hex2hash`, `hash2qid`, `fhash`, `readhash`
- Patch helpers:
  - `fcopy`, `fpatchmark`, `fpatch`
- Revlog decompression:
  - `funzip`
- Revlog operations:
  - `fmktemp`, `revlogopen`, `revlogupdate`, `revlogclose`, `revlogextract`, `revhash`, `hashrev`, `revlogopentemp`, `fmetaheader`
- Changelog metadata:
  - `loadrevinfo`
- Manifest tree operations:
  - `nodepath`, `mknode`, `loadfilestree`, `loadchangestree`, `closerevtree`
- Utility operations:
  - `hashstr`, `getworkdir`, `readfile`
- Ancestor finder:
  - `ancestor`

Dependencies and interactions:
- Included by `hgfs` implementation files.
- Provides module boundaries across parsing, revlog extraction, manifest trees, and 9P serving.

Research relevance:
- Compact map of the `hgfs` subsystem’s internal API.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hgfs/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hgfs/fs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/hgfs/fs.c

Implements the main read-only `hgfs` 9P server over a Mercurial repository.

Key points:
- Exposes a namespace rooted at revisions, where each revision directory contains:
  - `rev`, `rev1`, `rev2`
  - `log`, `who`, `why`
  - `files`
  - `changes`
- Opens `.hg/store/00changelog` and `.hg/store/00manifest` as revlogs.
- Lazily opens per-file revlogs under `.hg/store/data`, with fallback to filename mangling for Mercurial store encodings.
- Caches unused file revlogs and evicts idle revlogs when too many are free.
- Caches a small number of loaded revision trees by loader function and `Revinfo`.
- Builds 9P `Qid`s from revision hashes and manifest node hash-derived paths.
- Parses revision names by integer revision, `tip`, full/partial hash, or `rev.hash` style names.
- Walk logic supports:
  - revision directories from root
  - fixed metadata files under a revision
  - manifest trees for all files or changed files
  - file historical revisions through `.revN` suffixes
- Opens changelog/file data by extracting revlog revisions to temp files.
- Skips Mercurial metadata headers in extracted file data via `fmetaheader()`.
- Directory reads are generated through `dirread9p`.
- Serves only read/execute where applicable; write operations are denied.
- `main()` mounts the server at `/mnt/hg` by default or posts a service, with optional 9P debugging.

Dependencies and interactions:
- Uses Plan 9 `<9p.h>`, `<fcall.h>`, `<auth.h>`, `<flate.h>`.
- Relies on `revlog.c`, `tree.c`, `info.c`, `hash.c`, and `util.c`.
- Consumers such as `ancestor.c` and `hgdb.c` read the mounted tree.

Research relevance:
- The core filesystem-facing part of `hgfs`: a read-only versioned 9P view of Mercurial history, manifests, file contents, and changelog metadata.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hgfs/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hgfs/hash.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/hgfs/hash.c

Implements hash formatting, parsing, qid conversion, and Mercurial revision hashing.

Key points:
- `Hfmt()` formats a 20-byte SHA-1 hash as lowercase hex for `%H`.
- `fhash()` computes a Mercurial-style node hash by hashing parent hashes in lexicographic order followed by file contents.
- `hex2hash()` parses up to 40 hex characters into a 20-byte buffer and returns bytes parsed.
- `hash2qid()` maps the first eight hash bytes into a `uvlong` qid path.
- `readhash()` reads a named metadata file under a path, skips an optional `rev.hash` prefix before `.`, and parses the hash.

Dependencies and interactions:
- Uses Plan 9 libsec SHA-1.
- Used by revlog validation, qid generation, revision lookup, and ancestor/update tools.

Research relevance:
- Defines how Mercurial SHA-1 node IDs become filesystem names and qids in `hgfs`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hgfs/hash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hgfs/hgdb.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/hgfs/hgdb.c

Implements an experimental Mercurial debug/update/merge planning tool.

Key points:
- Loads `.hg/dirstate` to get parent hashes and tracked file state.
- Parses dirstate entries into a hash table keyed by path.
- Uses mounted `hgfs` revision trees to compare working parent, target revision, and common ancestor.
- Finds the target revision hash from `/mnt/hg/<rev>/rev`.
- Refuses updates with an outstanding merge parent.
- Uses `ancestor()` to locate common ancestor between current parent and target revision.
- Runs `/bin/derp` with selected options to compare left, right, and ancestor trees.
- Parses `derp` output and prints shell-like actions:
  - create directories
  - copy files
  - remove files
  - invoke `merge3` for conflicts
  - annotate delete conflicts or unknown states
- Option `-c` treats working directory as clean.
- `pjoin()` safely joins base paths and relative names.

Dependencies and interactions:
- Depends on a mounted `hgfs` namespace, `ancestor.c`, and external `/bin/derp`.
- Uses `getworkdir()`, `readhash()`, and hash formatting.

Research relevance:
- Not the 9P server itself, but a companion tool showing intended use of `hgfs` history views for update/merge planning.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hgfs/hgdb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hgfs/info.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/hgfs/info.c

Parses changelog revision metadata into `Revinfo`.

Key points:
- Extracts a changelog revision into a temp file via `revlogopentemp()`.
- Skips Mercurial metadata header with `fmetaheader()`.
- Reads:
  - manifest hash line into `mhash`
  - author line into `who`
  - timestamp line into `when`
  - changed-file list region, recording `logoff` and `loglen`
  - commit message into `why`
- Stores the changelog node hash into `chash`.
- Cleans up file descriptors and allocated strings on parse failure.

Dependencies and interactions:
- Called by `fs.c` when revision metadata is needed.
- `tree.c` uses `Revinfo` to load manifests and changed-file subsets.

Research relevance:
- Converts raw Mercurial changelog text into structured metadata exposed by the 9P filesystem.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hgfs/info.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hgfs/patch.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/hgfs/patch.c

Applies Mercurial binary delta patches to reconstruct revlog contents.

Key points:
- `fcopy()` copies a range from one fd to another, supporting bounded or until-EOF copy.
- Defines a 12-byte all-`0xff` patch marker used to separate patch streams.
- `fpatchmark()` writes that marker.
- `fpatch()` builds a linked list of fragments representing base file ranges and patch-inserted data.
- Reads patch records as 12-byte big-endian triples:
  - start
  - end
  - inserted length
- Maintains Mercurial patch offset adjustment as patches are applied.
- Splits, trims, or removes existing fragments overlapped by the patch range.
- Inserts new fragments pointing into the patch file.
- Finally copies fragment sequence to output.
- Frees all fragment records on success or failure.

Dependencies and interactions:
- Used by `revlogextract()` after compressed delta chunks are decompressed.
- Works with temp files created by `fmktemp()`.

Research relevance:
- Core delta-application logic needed to materialize Mercurial revlog revisions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hgfs/patch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hgfs/revlog.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/hgfs/revlog.c

Implements Mercurial revlog opening, index parsing, revision extraction, temp caching, and metadata-header skipping.

Key points:
- `fmktemp()` creates ORCLOSE temp files under `/tmp`.
- `revlogopen()` opens `<path>.i` and optionally `<path>.d`, stores base path, and parses index entries.
- `revlogupdate()` reads 64-byte revlog index entries into `Revmap`, decoding offsets, flags, compressed length, full length, base/link/parent revisions, and node hash.
- Handles inline revlog data by redirecting data offsets into the index file when no `.d` exists.
- `revhash()` returns `nullid` for invalid revisions.
- `hashrev()` linearly maps node hash to revision number.
- Builds revision chains either by previous index entry or bundle parent rule.
- `revlogextract()`:
  - builds the delta chain
  - decompresses the base fulltext or patches via `funzip()`
  - applies patches with `fpatch()`
  - validates reconstructed data using Mercurial SHA-1 parent/content hash
- `revlogopentemp()` caches the last extracted revision per `Revlog` and returns duped fds.
- `fmetaheader()` detects Mercurial `\1\n...\1\n` metadata wrappers and returns the data offset to skip.

Dependencies and interactions:
- Uses `zip.c` for revlog chunk decompression.
- Uses `patch.c` for deltas.
- Used by `fs.c`, `info.c`, and `tree.c`.

Research relevance:
- The low-level Mercurial storage reader that makes the 9P filesystem possible.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hgfs/revlog.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hgfs/tree.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/hgfs/tree.c

Builds manifest-derived revision trees for `hgfs`.

Key points:
- `nodepath()` reconstructs filesystem/store paths from `Revnode` ancestry.
- Supports Mercurial filename mangling for Windows-reserved names, uppercase letters, underscores, high bytes, and disallowed punctuation.
- `mknode()` allocates a tree node, optionally embedding hash bytes and name string.
- `addnode()` inserts manifest paths into a hierarchical tree, creating directory nodes as needed and updating ancestor path qid values.
- `loadmanifest()` parses manifest lines containing path, NUL, file hash, and mode byte.
- Can load a full manifest tree or filter to a hash table of changed paths.
- `loadfilestree()` builds the full file tree for a revision.
- `loadchangestree()` reads changed file names from a changelog entry, builds a hash table, then loads only matching manifest entries.
- `closerevtree()` refcounts and frees tree nodes, including historical `before` links.

Dependencies and interactions:
- Uses manifest revlog extraction through `revlogopentemp()`.
- Used by `fs.c` to serve `files` and `changes` directories.

Research relevance:
- Converts Mercurial manifest text into the directory hierarchy exposed through 9P.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hgfs/tree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hgfs/util.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/hgfs/util.c

Provides small utility helpers for `hgfs`.

Key points:
- `hashstr()` implements a simple rolling hash for string hash tables.
- `getworkdir()` locates a Mercurial working directory:
  - uses an explicit path if supplied
  - otherwise starts at current directory and walks upward until `.hg` exists
- `readfile()` reads up to `nbuf - 1` bytes from a file and NUL-terminates the buffer, returning bytes read.

Dependencies and interactions:
- Used by `fs.c`, `hgdb.c`, `tree.c`, and `hash.c`.

Research relevance:
- Shared filesystem/path utility layer for locating Mercurial repositories and reading small metadata files.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hgfs/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hgfs/zip.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/hgfs/zip.c

Decompresses Mercurial revlog compressed chunks.

Key points:
- Defines a buffered input wrapper `struct zbuf` around a fd and remaining compressed length.
- `zgetc()` feeds bytes to Plan 9 `inflate()` from an in-memory buffer, refilling from the fd until the specified length is exhausted.
- `zwrite()` writes inflated bytes to an output fd.
- `funzip()` handles Mercurial revlog chunk prefixes:
  - `'\0'`: raw uncompressed data
  - `'u'`: uncompressed data with explicit marker
  - `'x'`: deflated data
  - anything else is rejected
- Copies raw chunks directly and inflates deflated chunks through `<flate.h>`.
- Returns written length or `-1` on failure.

Dependencies and interactions:
- Used by `revlogextract()` to unpack revlog base and delta chunks.
- Depends on Plan 9 `<flate.h>`.

Research relevance:
- Minimal revlog compression adapter for Mercurial’s per-chunk storage format.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hgfs/zip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/histogram.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/histogram.c

Implements a live graphical histogram window fed by numbers from stdin.

Key points:
- Creates a new Plan 9 window and initializes draw, mouse, and keyboard controls.
- Reads numeric values from stdin in a separate process using `Biobuf`.
- Maintains a rolling `double` array sized to the current graph width.
- `updatehistogram()` shifts previous samples and draws the newest column at the right edge.
- `redrawhistogram()` handles full window redraw and resize, including title, border, current numeric value, and all stored samples.
- Uses selectable color palettes through `-c`.
- Options:
  - `-v maxv` set displayed maximum
  - `-s scale` set input scaling
  - `-t title` set title
  - `-r rect` set window rectangle
  - `-h` keep running after input EOF
  - `-c index` select palette
- Event loop handles incoming data, mouse menu exit, Delete key exit, and resize events.

Dependencies and interactions:
- Uses Plan 9 draw, mouse, keyboard, thread, and bio libraries.
- No persistent filesystem logic beyond stdin and window creation.

Research relevance:
- A compact Plan 9 UI utility demonstrating channel-based event multiplexing, live redraw, and streaming visualization.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/histogram.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hjfs/9p.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/hjfs/9p.c

Implements the 9P front end and worker dispatch loop for `hjfs`.

Key points:
- `tauth()` routes auth requests:
  - no auth required if `FSNOAUTH` or user `none`
  - otherwise delegates to `auth9p()` for normal or `dump` attach specs
- `tattach()` validates authentication, maps usernames to uids, handles normal and `dump` attaches, and creates a `Chan`.
- Queues most 9P operations per channel through `tqueue()` rather than executing directly in the lib9p callback.
- Maintains per-channel request queues and a global ready queue protected by `chanqu`.
- `tdestroyfid()` marks channels for clunk and wakes workers.
- `start9p()` can listen on network addresses, serve stdio, or post/mount a service.
- `twalk()` clones unopened fids and walks path elements through channel operations.
- `workerproc()` serializes operations per channel and executes `chanwalk`, `chanopen`, `chancreat`, `chanread`, `chanwrite`, `chanremove`, `chanstat`, and `chanwstat`.
- `workerinit()` starts `NWORKERS` worker threads and initializes ready-queue state.

Dependencies and interactions:
- Uses Plan 9 `<9p.h>`, `<fcall.h>`, and auth helpers.
- Calls core channel/filesystem functions declared in `fns.h`.
- Coordinates with `auth.c` for user/auth policy and `buf.c` for worker initialization.

Research relevance:
- The concurrency boundary between 9P RPCs and the internal `hjfs` filesystem engine.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hjfs/9p.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hjfs/auth.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/hjfs/auth.c

Manages `hjfs` users, groups, permissions, and user database updates.

Key points:
- Defines built-in default users/groups including `adm`, `none`, `tor`, `glenda`, `sys`, `map`, `doc`, `upas`, and `font`.
- Validates user names by rejecting empty names, control characters, and selected punctuation.
- Parses user database lines in `uid:name:leader:member,member` format.
- `usersload()` reads a user database file through a `Chan`, parses it, resolves names to uids, sorts users and memberships, and atomically swaps `fs->udata`.
- `userssave()` writes the current or default user database through a `Biobuf`, optionally using channel-backed append writes.
- `lookupuid()`, `uid2name()`, and `name2uid()` provide uid/name resolution.
- `ingroup()` checks direct identity, group leader, and membership.
- `permcheck()` evaluates Plan 9-style owner/group/other read/write/execute permissions, unless `FSNOPERM` is set.
- `cmdnewuser()` implements the console `newuser` command:
  - creates users/groups
  - renames users
  - changes leader
  - adds/removes memberships
  - writes updated users
  - optionally creates `/usr/<name>`

Dependencies and interactions:
- Uses core `Chan` operations to read/write users and create user directories.
- Called by 9P attach and permission checks.
- Exposes administrative command hooks used by `cons.c`.

Research relevance:
- Defines `hjfs` identity and permission semantics, including mutable user database behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hjfs/auth.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hjfs/buf.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/hjfs/buf.c

Implements the asynchronous buffer cache for `hjfs`.

Key points:
- Maintains free buffers, device hash lists, per-buffer wait queues, and global pending free-buffer requests.
- `markbusy()` removes a buffer from the free list; `markfree()` returns it.
- `changedev()` moves a buffer between device/off hash chains.
- `givebuf()` satisfies get requests from cached buffers, waits on busy buffers, or recycles free buffers.
- Delayed-write buffers are scheduled for writeback before reuse.
- `handleput()` handles immediate writeback (`BWRIM`), delayed write errors, freeing, and waking waiters.
- `handlesync()` schedules all delayed-write buffers and can notify a waiting caller.
- `bufproc()` multiplexes get, put, and sync channels, and starts 9P workers.
- Installs `%T` formatting for block types.
- `bufinit()` allocates buffers with `sbrk`, initializes channels, and starts `bufproc`.
- `getbuf()` checks bounds, fetches or allocates a buffer, validates expected block type, and records caller pc for debugging.
- `sync(wait)` flushes delayed writes and optionally sends sync sentinel work to every device.

Dependencies and interactions:
- Device I/O is performed by `dev.c` workers through per-device work queues.
- Used by almost every filesystem operation to access superblocks, dentries, indirect blocks, raw data, and ref blocks.

Research relevance:
- Central cache/writeback layer for `hjfs`, mediating concurrency, type checking, delayed writes, and sync.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hjfs/buf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hjfs/cons.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/hjfs/cons.c

Implements the administrative console command service for `hjfs`.

Key points:
- Creates `/srv/<service>.cmd` backed by a pipe and a console process.
- Parses line-oriented commands with up to 16 arguments.
- Commands include:
  - `sync`
  - `halt`
  - `dump`
  - `allow`
  - `disallow`
  - `noauth`
  - `chatty`
  - `create`
  - `newuser`
  - `users`
  - `echo`
  - `df`
  - debug commands for dentries and block lookup/modification
- `walkpath()` resolves absolute paths through `Chan` operations.
- `cmdcheck()` scans reference blocks and validates referenced data/dentry/indir/ref/superblock blocks, though it is commented out of the command table.
- `cmdcreate()` creates a file or directory with specified owner, group, permissions, and flags.
- `cmddf()` reports free/used/total block counts and MB equivalents.
- Debug commands inspect dentry location, raw dentry bytes, and block mappings for a file.
- `consproc()` tokenizes commands, validates arity, invokes handlers, and prints errors through `dprint`.

Dependencies and interactions:
- Uses channel operations and buffer functions from the core filesystem.
- Calls `fsdump()`, `sync()`, `shutdown()`, `readusers()`, `cmdnewuser()`, and `dprint()`.

Research relevance:
- Operational control surface for `hjfs`, including maintenance, permission toggles, user management, and low-level diagnostics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hjfs/cons.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hjfs/conv.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/hjfs/conv.c

Packs and unpacks `hjfs` on-disk block formats.

Key points:
- Defines little-endian GET/PUT macros for 8-, 16-, 24-, 32-, and 64-bit fields.
- `unpack()` reads a raw disk block into a typed `Buf`:
  - unknown/default type copies raw data
  - `TSUPERBLOCK` decodes superblock fields
  - `TDENTRY` decodes all dentries in a block
  - `TINDIR` decodes indirect block offsets
  - `TREF` decodes 24-bit reference counts
- `pack()` serializes typed `Buf` contents back into the one-byte type tag plus payload.
- Aborts on unknown block types when packing.

Dependencies and interactions:
- Used by `dev.c` for every block read/write.
- Layout constants come from `dat.h`.

Research relevance:
- Defines the byte-level on-disk format for `hjfs` metadata and data blocks.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hjfs/conv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hjfs/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/hjfs/dat.h

Defines `hjfs` on-disk constants, block structures, runtime state, and flags.

Key points:
- On-disk constants:
  - `BLOCK = 4096`
  - `RBLOCK = BLOCK - 1` because the first byte stores block type
  - `SUPERMAGIC`
  - `SUPERBLK`
  - name length, direct/indirect block counts, root qids
- Runtime constants:
  - sync interval
  - freelist length
  - buffer hash size
  - worker count
  - exclusive lock duration
  - user name/id constants
- Block types:
  - `TRAW`
  - `TSUPERBLOCK`
  - `TDENTRY`
  - `TINDIR`
  - `TREF`
  - `TDONTCARE`
- Defines `Superblock`, `Dentry`, `BufReq`, `Buf`, `ThrData`, `Dev`, `FLoc`, `Loc`, `Fs`, and `Chan`.
- `Dentry` embeds Plan 9 `Qid`, ownership, mode, size, direct/indirect block pointers, and times.
- Reference counts are stored as 24-bit entries with sentinel value.
- `Loc` tracks in-memory file locations, reference state, dump flags, and exclusive locks.
- `Fs` carries device, flags, root location, freelist, location tree, and user database.
- `Chan` carries per-fid filesystem state, directory walk state, and queued worker requests.
- Defines `HOWMANY()` for block count rounding.

Dependencies and interactions:
- Included by all `hjfs` files.
- Matches serialization logic in `conv.c`.

Research relevance:
- Central structural definition of the `hjfs` filesystem’s disk format and runtime object model.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hjfs/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hjfs/dev.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/hjfs/dev.c

Implements block-device access workers for `hjfs`.

Key points:
- Maintains global linked list `devs`.
- `newdev()` opens a backing file read/write, determines size in filesystem blocks, initializes hash sentinels and work queue, starts a device worker, and links the device globally.
- Rejects zero-length device files.
- `devwork()` waits on the device work queue.
- For write requests:
  - zeroes a 4096-byte block buffer
  - packs the `Buf`
  - writes one full block at `off * BLOCK`
- For read requests:
  - reads a full block, tolerating short read loops
  - unpacks into the `Buf`
- Reports bounds errors and I/O errors through `b->error`.
- Treats a work item with `b->d == nil` as a sync acknowledgement request.

Dependencies and interactions:
- Work is queued by `buf.c`.
- Uses `pack()`/`unpack()` from `conv.c`.

Research relevance:
- The I/O backend connecting `hjfs` typed buffers to a flat block device file.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hjfs/dev.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hjfs/dump.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/hjfs/dump.c

Implements snapshot/dump support and copy-on-write preparation for `hjfs`.

Key points:
- `copydentry()` copies a dentry into a destination directory under a new name, increments references for direct and indirect blocks, and writes the destination dentry.
- `fsdump()` creates a date-based snapshot under the dump tree:
  - ensures a year directory exists
  - selects a unique month/day name
  - copies the root dentry into the dump directory
  - resets `LDUMPED` flags
- `resetldumped()` clears dump flags over the location tree.
- `willmodify1()` ensures a `Loc` is private before modification:
  - checks block refcount
  - if shared, finds parent block reference
  - asks `getblk(..., GBWRITE)` to allocate/copy as needed
  - updates descendant `Loc` records when the block changes
  - marks location dumped
- `willmodify()` walks the ancestor chain, upgrades locks when necessary, calls `willmodify1()` from rootward to leafward order, and retries if refcounts changed.

Dependencies and interactions:
- Uses channel, dentry, buffer, block reference, and allocation functions from the rest of `hjfs`.
- Called before mutating shared dumped data to preserve snapshots.

Research relevance:
- The snapshot/copy-on-write layer for `hjfs`, tying dump creation to refcounted block mutation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hjfs/dump.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hjfs/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/hjfs/fns.h

Declares the internal `hjfs` API.

Key points:
- Memory helpers: `emalloc`, `erealloc`, `estrdup`.
- Buffer/device helpers: `bufinit`, `getbuf`, `putbuf`, `sync`, `pack`, `unpack`, `newdev`.
- Filesystem core: `initfs`, `getdent`, `getfree`, `putfree`, `getblk`, `trunc`, `delete`, `chref`, `newentry`, `findentry`.
- Channel/9P operations: `chanattach`, `chanclone`, `chanwalk`, `chancreat`, `chanopen`, `chanwrite`, `chanread`, `chanstat`, `chanwstat`, `chanclunk`, `chanremove`.
- Identity and auth: `permcheck`, `uid2name`, `name2uid`, `usersload`, `userssave`, `ingroup`, `writeusers`, `readusers`.
- Server/ops: `start9p`, `initcons`, `shutdown`, `fsdump`, `willmodify`, `workerinit`.
- Location management: `chbegin`, `chend`, `newqid`, `getloc`, `haveloc`, `cloneloc`, `putloc`.
- Validation/debug: `namevalid`, `modified`, `dprint`.
- Declares `dprint` vararg checking.

Dependencies and interactions:
- Included by all `hjfs` implementation files.
- Serves as the module boundary between the files in this group and omitted core files.

Research relevance:
- Function map for the `hjfs` filesystem implementation, showing the subsystems not all present in this work item.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hjfs/fns.h -->