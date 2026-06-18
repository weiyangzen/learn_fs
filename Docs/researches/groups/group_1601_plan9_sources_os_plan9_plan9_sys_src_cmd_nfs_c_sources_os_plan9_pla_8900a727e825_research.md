# Group Research: group_1601_plan9_sources_os_plan9_plan9_sys_src_cmd_nfs_c_sources_os_plan9_pla_8900a727e825

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/nfs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/nfs.c

Implements a Plan 9 9P server front-end for NFSv3. It dials mount and NFS RPC services, optionally discovers ports through portmap, mounts an exported NFS path, and exposes the result through `threadpostmountsrv`.

Core logic is split between SunRPC/NFS wrappers and 9P request handlers. RPC helpers wrap `MOUNT`, `GETATTR`, `ACCESS`, `LOOKUP`, `READ`, `WRITE`, `READDIR`, `READDIRPLUS`, `CREATE`, `MKDIR`, `REMOVE`, `RMDIR`, `RENAME`, `SETATTR`, and `COMMIT`, translating NFS status to Plan 9 error strings. `FidAux` stores the NFS handle, parent handle, name, readdir cookie, and auth data for each fid.

The file maps Unix passwd/group data to Plan 9 names and SunAuthUnix credentials when `-u passwd group` is supplied. Unknown users fall back to nobody-style uid/gid `-1` credentials.

The 9P layer translates NFS attributes into Plan 9 `Qid`/`Dir`, performs permission checks through NFS `ACCESS`, serves directory reads by converting NFS directory entries to 9P stat records, and handles walk/clone/remove/wstat semantics. Rename plus setattr is explicitly non-atomic.

Operationally, `threadmain` handles `-D`, `-R`, `-v`, `-p`, `-s`, and `-u`, discovers mount/NFS ports if only one address is supplied, starts a dial helper process, then posts the service. `Tflush` forwards tags to both RPC clients’ flush channels.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/nfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/nm.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/nm.c

Implements Plan 9 `nm`, listing symbols from object files, archives, or executable images using `<mach.h>` object/symbol APIs.

Command flags select all symbols, globals, suppress filename headers, sort by numeric value, preserve symbol-table order, undefined-only, and type-signature output. Archive handling skips `__.SYMDEF`, iterates members with `nextar`, loads each member with `readar`, and prints member symbols under the archive/member name.

Symbol filtering is type-based: text/data/bss/local/undefined/debug records are included or suppressed according to `-a`, `-g`, and `-u`. `z` records use a filename translation table built from `m`/`f` symbols so source paths can be printed.

Output is sorted by name unless `-n` or `-s` changes behavior. Width expands from 8 to 16 hex digits when large symbol values require it.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/nm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/nntpfs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/nntpfs.c

Implements an NNTP-backed 9P file server mounted by default at `/mnt/news`. It presents NNTP newsgroup hierarchy as directories, article numbers as subdirectories, and article parts as files named `header`, `body`, `article`, and `xover`.

`Netbuf` wraps the NNTP connection, buffered I/O, response state, optional authentication, and current group. NNTP helpers handle reconnecting commands, response validation, AUTHINFO, group refresh, XOVER chunk caching, article retrieval, and posting.

`Group` forms a sorted hierarchy split on dots. Root refresh uses `LIST`; per-group refresh uses `GROUP` with a 30-second access-time throttle. Qid encoding packs group and article numbers into limited path/version bits.

The 9P server supports attach, walk, open, read, write-to-post, stat, clone, and destroyfid. Directories are synthesized from group children, post file, and article-number ranges. Posting writes accumulate in fid aux state and are submitted on zero-length write or fid destroy.

Authentication uses Plan 9 auth key lookup when `-a` is supplied, optionally with `-u user`. Debug flags include 9P and network command tracing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/nntpfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ns.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ns.c

Implements `ns`, a namespace dumper/replayer for a target process. It reads `/proc/<pid>/ns`, parses namespace records, quotes arguments, and prints shell commands that reconstruct the namespace.

By default, mount records whose new side is `/net/.../data` are translated into a more stable network address by reading the corresponding `/net/<net>/<port>/remote`. The `-r` flag disables that translation and preserves raw namespace paths.

The parser accepts several namespace line forms, including `cd`, bind/mount forms with or without flags, and optional specs. It rejects malformed line widths to avoid emitting ambiguous reconstruction commands.

The `quote` helper emits single-quoted strings only when needed for whitespace or shell metacharacters.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ns.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/p.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/p.c

Implements a minimal pager. It prints input in chunks of `pglen` lines, defaulting to 22 lines, and waits for commands from `/dev/cons` between chunks.

Arguments beginning with `-` set page length; file arguments are opened and paged sequentially. With no file arguments, stdin is paged.

At prompts, `q` or EOF exits. Commands beginning with `!` are run through `/bin/rc -c` with console input attached, after which the pager prompts again. Long lines that exceed `Brdline` handling are copied character by character.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/p.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/page/cache.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/page/cache.c

Provides the page image cache for the `page` viewer. It keeps five cached `(Document*, page, angle)` image entries and moves hits to the front.

`cachedpage` validates page bounds, calls the document’s `drawpage`, normalizes non-zero image origins, applies rotation, and returns a cached `Image`. Failed page rendering in forward-only mode exits; otherwise it returns a small question-mark placeholder.

The cache includes simple sequential readahead. When the viewed page advances or retreats by one, it forks a shared-memory process to render the likely next page while holding the display lock.

`cacheflush` frees cached images and clears document associations; it is also used as a recovery path when allocation fails.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/page/cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/page/filter.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/page/filter.c

Contains conversion front-ends for formats that are first transformed to PostScript. `initfilt` runs an rc command, writes converted output to an ORCLOSE temp file, then calls `initps` on the generated stream.

`initdvi` spools stdin to disk because `dvips` wants a filename, then runs `dvips -Pps -r0 -q1 -f1`. `inittroff` pipes through `lp -H -dstdout`. `initmsdoc` pipes through `doc2ps`.

The function accepts an initial already-read buffer and either copies the remaining `Biobuf` or stdin into the converter, preserving `page`’s file type sniffing flow.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/page/filter.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/page/gfx.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/page/gfx.c

Implements graphics-file support for `page`. It builds a `Document` whose pages are individual image files or one stdin image, and whose `drawpage` converts the selected graphic into a Plan 9 image.

`genaddpage` classifies formats by magic bytes and filename suffix: Plan 9 bitmaps, Inferno compressed images, GIF, TIFF, JPEG, PNG, PPM, BMP, YUV, fax/CCITT, and fallback `cvt2pic`. Conversion commands are stored in `cvt[]`, with true-color variants for some formats.

`convert` either reads native Plan 9 images directly or spawns `/bin/rc -c <converter>`, optionally feeding a stdin buffer through a pipe, then `readimage`s converter output. Converter wait statuses are reported except for known special cases.

The document supports dynamic `addpage`/`rmpage`, enabling plumbed image additions and interactive discard from the viewer.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/page/gfx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/page/gs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/page/gs.c

Provides the Ghostscript process interface shared by PDF and PostScript backends. It spawns `/bin/gs` with the Plan 9 output device, pipes command input, captures intended bitmap data on fd 3, and monitors error output.

`spawngs` carefully reassigns low-numbered fds before exec, supports optional teeing of Ghostscript input, installs an `atexit` killer, initializes helper PostScript procedures, and stores fds in `GSInfo`.

`gscmd` writes formatted PostScript commands. `waitgs` synchronizes by asking Ghostscript to print a sentinel line and reading until it appears, treating lines containing `Error:` as fatal.

`setdim` configures resolution, page size, margins, optional bounding-box translation, and landscape rotation before a page is rendered.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/page/gs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/page/nrotate.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/page/nrotate.c

Contains an older or incomplete experimental implementation of logarithmic 180-degree image rotation using draw masks and shuffling.

The visible code sketches mask halving, adjacent-region swaps, slop movement, and range swaps along X/Y axes, but contains unresolved identifiers and incomplete statements, including references such as `swapadjacent`, `moveup`, `lastnn`, `nn`, `n`, `mask`, and `im` in scopes where they are not defined.

Compared with `rotate.c`, this file appears stale and not suitable as the active build source. Its value is mostly historical: it documents the intended divide-and-shuffle rotation algorithm later realized in a compilable form elsewhere.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/page/nrotate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/page/page.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/page/page.c

Main entry point for the `page` document/image viewer. It parses global flags, sniffs input type, initializes the appropriate `Document`, starts the draw display, and enters `viewer`.

Supported options include resizing/new-window behavior, reverse order, PPI, bounding-box handling, image-only mode, debug verbosity, Ghostscript teeing, abort-on-note, and antialias bits. With no files and non-image mode, stdin is duplicated and `/dev/cons` replaces fd 0 for interaction.

File type detection uses the first 16 bytes to select PDF, PostScript/PJL, DVI, Microsoft Office, troff output, or graphics. Unrecognized input falls back to graphics conversion.

The file also manages a note watcher. Non-`die` notes are forwarded to the process group; alarms from Ghostscript trigger group termination. `wexits` coordinates shutdown and watcher cleanup.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/page/page.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/page/page.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/page/page.h

Shared header for the `page` program. It defines the `Document` interface: document name, page count, forward-only flag, page-name callback, draw-page callback, optional add/remove callbacks, backing `Biobuf`, and backend-specific `extra`.

It declares backend initializers for PostScript, PDF, graphics, troff, DVI, and Microsoft Office conversion, plus viewer, cache, rotation/resampling, Ghostscript, temporary input, window, label, and utility helpers.

`GSInfo` records Ghostscript command/data fds, reader buffer, process id, and rendering PPI. The header also exposes global configuration flags such as `chatty`, `ppi`, `reverse`, antialias bits, resizing, true-color mode, and stdin fd.

The final macros intentionally map draw operations back to older draw calls because new draw operators were not reliable across drawterm/vncs and some kernel paths.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/page/page.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/page/pdf.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/page/pdf.c

Implements PDF support for `page` through Ghostscript. It includes `pdfprolog.c` as a C string, opens or spools the PDF, starts Ghostscript with delayed safer mode, loads the prolog, opens the PDF in Ghostscript, and asks for page count.

`PDFInfo` embeds `GSInfo` and stores per-page crop boxes. `pdfbbox` queries `/CropBox`, parses a four-number rectangle, and falls back to a trailer-level bounding box if a page has no usable crop box.

`pdfdrawpage` sends `DoPDFPage` for the page number, reads the generated Plan 9 image from the Ghostscript data fd, and waits for Ghostscript completion. Page names are simple `p N` labels.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/page/pdf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/page/pdfprolog.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/page/pdfprolog.c

A small C string fragment of Ghostscript/PDF PostScript prolog consumed by `pdf.c`.

It initializes PDF-related variables, defines `DoPDFPage` as page lookup plus rendering, and overrides page setup to honor `CropBox`, `Rotate`, page size, and page offset via `setpagedevice`.

The file is not standalone C logic; it is included directly into a string literal assignment.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/page/pdfprolog.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/page/ps.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/page/ps.c

Implements PostScript support for `page`. It scans DSC comments to identify page offsets, page labels, trailer position, document bounding box, page order, orientation, and whether translation tricks are safe.

`PSInfo` stores Ghostscript state, default bounding box, page offset table, whether the document is “clueless”/forward-only, the `%!` offset, and related metadata. If no page boundaries are found, the file is treated as one stream rendered forward-only.

`rdbbox` parses and normalizes bounding boxes, expanding likely page-sized documents to A4 or 8.5x11 unless true bounding-box mode is requested. `repaginate` can collapse multiple physical pages into one logical page group.

Rendering writes either just the requested page slice or header/page/trailer slices to Ghostscript, depending on `goodps`. A newline is sent after page data to avoid a Ghostscript read-ahead deadlock on carriage-return-terminated input.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/page/ps.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/page/rotate.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/page/rotate.c

Provides image rotation and resampling routines for `page`. `rot180` uses a logarithmic draw-mask shuffle algorithm to reverse X and Y axes with an auxiliary image, optimizing for remote draw performance. Sub-byte images are temporarily converted to `CMAP8`.

`rot90` and `rot270` allocate transposed images and copy pixels one at a time through draw operations, then free the source image.

The resampler uses a Kaiser-windowed filter table and performs two-pass resizing: first X into scanline buffers, then Y into destination scanlines. It supports byte-per-channel formats directly and converts palette/sub-byte formats through `RGB24` or `GREY8` temporary images.

Allocation failures in transform paths are fatal via `wexits`/`sysfatal`; unsupported channel types also abort.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/page/rotate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/page/util.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/page/util.c

Utility support for `page`: checked allocation, string duplication, temp-file creation, stdin spooling, stdin-to-pipe bridging, and window label updates.

`opentemp` repeatedly applies `mktemp` to a template, creates an ORCLOSE temp file, writes the final name back into the template, and exits on failure.

`spooltodisk` writes the already-read header plus remaining stdin to `/tmp/pagespool...` and returns a seeked fd. `stdinpipe` forks a shared-memory writer process that streams the initial buffer and remaining stdin into a pipe.

`setlabel` writes to `<windir>/label` if possible and deliberately ignores errors.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/page/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/page/view.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/page/view.c

Implements the interactive viewer for `page`. It handles window drawing, menus, keyboard/mouse navigation, zoom/fit/rotate, plumbed image additions, page deletion, bitmap export, panning, resize recovery, and new-window setup.

Global state tracks the current document, image, page, rotation angle, screen upper-left placement, and allowed panning range. `showpage` loads through `cachedpage`, optionally resizes the window, and redraws. `redraw` paints image, border, and gray background; `translate` scrolls using differential redraw to minimize work.

Keyboard controls include numeric page selection, next/previous, reverse order, rotate/upside-down, write bitmap, discard, quit, and vertical panning. Mouse controls include left-drag pan, middle command menu, and right page menu. Forward-only documents expose a restricted menu.

Plumbing supports `showdata`, `quit`, absolute paths, and paths relative to the sender’s working directory, adding pages through the document callback. `newwin`, `screenrect`, and `zerox` handle rio/acme window plumbing and spawning a second `page` instance fed by the current image.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/page/view.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/paqfs/mkpaqfs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/paqfs/mkpaqfs.c

Builds a `paqfs` archive from a root file or directory. The format consists of a header, typed blocks, a root directory block, and a trailer containing the root block offset and SHA1 digest.

Files are split into fixed-size data blocks; a pointer block stores each data block offset. Directories recursively serialize child `PaqDir` entries into directory blocks and store those block offsets in a pointer block. Blocks may be deflate-compressed unless `-u` is used.

The header records magic, version, block size, creation time, and label. The block header records magic, stored size, type, encoding, and Adler-32 of unencoded data. The trailer stores magic, root offset, and the accumulated SHA1.

Limitations are tied to block size: each pointer block only holds `blocksize / 4` offsets, and entries larger than a block are skipped with warnings.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/paqfs/mkpaqfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/paqfs/paqfs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/paqfs/paqfs.c

Implements a read-only 9P server for `paqfs` archives. It can mount an archive, post a srv file, run on stdio, set cache/message sizes, disable auth-style ownership checks, quiet banner output, and verify the archive SHA1.

Initialization reads and validates the header, optionally streams all blocks for SHA1 verification, reads the trailer, allocates an LRU-ish block cache, and constructs a root `Paq` tree node. If the archived root is a regular file, it synthesizes a containing root directory.

9P support includes version, attach, walk, open, read, clunk, stat, and read-only failures for create/write/remove/wstat. Reads load pointer blocks then data or directory blocks. Directory reads pack serialized `PaqDir` entries into 9P stat records and maintain fid offset state.

`blockLoad` caches blocks by archive byte address with refcounts and age. `blockRead` validates block headers, inflates deflated blocks when needed, and checks Adler-32 against unencoded data.

Permission checks use owner/group/other mode bits, with `-a` allowing username comparisons to pass owner/group checks more broadly.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/paqfs/paqfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/paqfs/paqfs.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/paqfs/paqfs.h

Shared on-disk format definitions for `mkpaqfs` and `paqfs`.

Defines header, block, trailer, and directory structures plus magic numbers, version, fixed header sizes, min/max block sizes, block types, and encodings.

`PaqHeader` records archive metadata. `PaqBlock` describes each stored block’s encoded size, semantic type, encoding, and Adler-32 checksum. `PaqTrailer` records the root directory block offset and final SHA1 digest. `PaqDir` is the serialized directory/file metadata model used by both writer and reader.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/paqfs/paqfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pbd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/pbd.c

Tiny utility that prints the basename of the current working directory.

It calls `getwd`, finds the last slash, skips it when appropriate, writes the selected component to stdout, and exits. If `getwd` fails, it prints `???`.

No newline is emitted.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pbd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pcc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/pcc.c

Implements `pcc`, a Plan 9 APE C compiler driver. It chooses architecture-specific compiler/linker tools from `$objtype`, runs `cpp`, pipes to the selected C compiler, and optionally links with APE libraries.

The architecture table maps Plan 9 objtypes to compiler, linker, object suffix, and output name. Source `.c` inputs become architecture-suffixed objects; matching object/archive files are passed to the linker; wrong-architecture objects are ignored with a warning.

Flags are split between preprocessor, compiler, linker, and driver behavior. `-E` and `-P` stop after preprocessing; `-c` stops after compilation; `-o` selects output; `-l` maps to architecture APE libraries; `-v` prints commands.

`dopipe` forks compiler and preprocessor around a pipe and waits for both. The linker appends `/arch/lib/ape/libap.a` and removes the temporary single object after successful link unless it is an archive.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pcc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pic/arcgen.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/pic/arcgen.c

Generates `pic` arc objects from parsed attributes. It computes start, end, center, radius, arrowhead sizing, clockwise handling, fill state, invisibility, and current-direction updates.

Default arcs use current position, direction, and `arcrad`; `TO` without `AT` derives a center from chord midpoint and radius, expanding radius if too small. Clockwise arcs swap start/end and arrowhead orientation for output compatibility.

The resulting object stores start, end, arrow dimensions, radius, head flags, clockwise flag, fill flags, and fill value. It also updates `curx/cury` to the logical arc endpoint.

`arc_extreme` computes bounding-box extremes by considering endpoints plus quadrant extrema on the circular arc.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pic/arcgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pic/blockgen.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/pic/blockgen.c

Handles grouped `pic` constructs: braces `{...}` and bracketed blocks `[...]`.

`leftthing` saves current position/direction and, for `[...]`, starts a `BLOCK` object while resetting local bounds. `rightthing` restores state and emits either a `MOVE` for braces or a `BLOCKEND` object paired with the block start.

`blockgen` computes the final block size and placement from enclosed-object bounds plus attributes like height, width, with-corner, at/from, invis, and text. It updates global extremes and cursor position according to direction.

`blockadj` shifts every enclosed object by the final block translation and adjusts embedded absolute coordinates for lines, splines, arrows, and arcs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pic/blockgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pic/boxgen.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/pic/boxgen.c

Generates rectangular `pic` box objects. It consumes attributes for height, width, same-as-previous sizing, with-corner anchoring, explicit `at`, invisibility, no-edge, dot/dash style, fill, and text.

If no explicit position is supplied, placement follows the current direction and advances by half the box dimension before creating the object. After creation it advances `curx/cury` to the exiting edge.

The object stores width, height, style bits, dash/dot value, and fill value, and updates drawing extremes to include the box bounds.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pic/boxgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pic/circgen.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/pic/circgen.c

Generates circle and ellipse objects. It reads defaults from `circlerad`, `ellipsewid`, and `ellipseht`, then applies radius, diameter, width, height, same, with-corner, at, invis, no-edge, dot/dash, fill, and text attributes.

Circle radius is forced equal on both axes; ellipses store separate horizontal/vertical radii. Invalid non-positive radii produce warnings.

Placement follows current direction unless `AT` is used. The object updates extremes using the full bounding rectangle and advances current position to the appropriate edge.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pic/circgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pic/for.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/pic/for.c

Implements `pic` `for` loops and `if` source expansion. Loop state is stored on a fixed stack of ten `For` frames.

`forloop` installs the loop variable, stores limit/operator/increment/body, and pushes the first iteration body back into the input stream. `endfor` updates the variable using `+`, `-`, `*`, or `/`, then schedules the next iteration.

The loop completion test is simple and noted as direction-insensitive: it stops when the variable exceeds `to * 1.001`.

`ifstat` pushes either the then-body or else-body back into input and frees the unused body.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pic/for.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pic/input.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/pic/input.c

Implements `pic` input-source stacking, macro expansion, argument substitution, `copy`, `thru`, shell escapes, and syntax-error context reporting.

Sources can be files, strings, macros, single pushed-back chars, `thru` sentinels, or free-after-use strings. `input` and `nextchar` multiplex those sources and maintain a rolling error buffer.

Macro definitions are collected with balanced delimiters and stored in the symbol table. Macro invocation parses parenthesized args into argument frames and expands `$N` references while reading the macro body.

`copy thru` reads lines, tokenizes fields into macro arguments, expands a selected macro per line, and stops on `.PE` or an optional `until` string. `copy file` pushes a new file source.

`yyerror` prints command, file, line, nearby context, and pushes a synthetic `.PE` to recover safely.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pic/input.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pic/linegen.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/pic/linegen.c

Generates line, arrow, and spline objects. It accumulates one or more relative segments from direction, `TO`, `BY`, `THEN`, `FROM`, and `AT` attributes, with default line width/height from variables.

Attributes control heads, invisibility, no-edge, dotted/dashed style, same-as-previous segment, arrowhead dimensions, chop distances, fill, and text. `CHOP` shortens the first and last segments along their direction, defaulting to circle radius when no explicit distance is supplied.

The created object stores final endpoint, arrowhead dimensions, segment count, and all segment deltas. It updates extremes differently for straight lines/arrows and splines, approximating spline extents from neighboring control points.

Current position is advanced to the final endpoint, and previous delta state is saved for `same`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pic/linegen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pic/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/pic/main.c

Main driver for the classic `pic` preprocessor. It initializes globals, defaults, object/text/attribute arrays, a predefined `pid` macro, and processes stdin or file arguments.

`getdata` copies normal troff input through unchanged, detects `.PS` blocks, optionally includes external picture files via `.PS <file>`, runs the parser, computes picture dimensions, emits troff output if no syntax errors occurred, and handles `.lf` line directives.

Defaults include scale-sensitive dimensions for line, move, box, circle, arc, ellipse, arrow, text, max page size, and fill value. Changing `scale` recalculates scalable defaults.

`reset` frees previous picture objects, block symbol tables, and text strings, resets cursor/direction/bounds, and prepares for the next `.PS` block.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pic/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pic/makefile -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/pic/makefile

Historical makefile for building `pic` outside the Plan 9 mk system. It lists yacc/lexer/generated objects plus geometry, input, output, and utility modules.

`pic` links `picy.o` with object files and `-lm`. Object files depend on `pic.h` and `prevy.tab.h`; `prevy.tab.h` is refreshed from `y.tab.h` only when changed.

Targets include `bundle`, `bowell` deployment, `clean`, and `install` to `/usr/bin/pic`. The file contains two `CFLAGS` assignments, with the later debug/include-path assignment overriding the initial empty one.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pic/makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pic/misc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/pic/misc.c

Contains shared `pic` geometry, attribute, position, and object-allocation utilities.

It maps direction tokens to internal direction, extracts object components like `.x`, `.y`, `.wid`, `.ht`, and `.rad`, formats `sprintf` expressions, and builds typed attributes consumed by object generators.

Position helpers create points, interpolate between points, offset/add/subtract positions, locate object corners/center/start/end, and resolve references to first/last objects or objects inside blocks.

`makenode` allocates variable-sized `obj` records, initializes type/count/mode/current position/text range, grows `objlist`, and appends the object. `extreme` updates picture bounds.

Block variable lookup retrieves named positions or variables from a block-local symbol table.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pic/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pic/movegen.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/pic/movegen.c

Generates invisible movement objects. It consumes text, same, direction, `TO`, `BY`, `FROM`, and `AT` attributes to compute cursor displacement.

Without explicit displacement, it uses `movewid`/`moveht` in the current direction. With `same`, it repeats the previous movement delta.

It records bounds before and after movement, updates `curx/cury`, saves the previous delta, creates a `MOVE` object, and returns it.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pic/movegen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pic/pic.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/pic/pic.h

Central header for the `pic` implementation. It defines geometry constants, style/text flags, direction encodings, the variable-sized `obj` representation, yacc semantic union, symbol table, attributes, text records, input-source stack records, file stack records, macro argument frames, and block push-stack state.

It declares the large shared global state used by parser, generators, input, and output: object/text/attribute arrays, current position, direction, codegen flag, picture extents, line/file state, and block stack.

Function declarations cover macro input, loops/conditionals, variable/symbol lookup, object generation, geometry helpers, output helpers, text saving, attribute construction, and math wrappers.

The header encodes many cross-module contracts: object `o_val` fields are type-specific, style bits combine in `o_attr`, and parser tokens from `y.tab.h` must match generator expectations.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pic/pic.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pic/picy.y -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/pic/picy.y

Yacc grammar for `pic`. It defines token numbers for object types, language keywords, attributes, positions, functions, operators, and statement terminators, then maps parsed constructs to generator and utility calls.

Top-level grammar recognizes picture statements inside `.PS/.PE`: primitives, blocks, named places, assignments, direction changes, print/reset, copy, for, if, and empty statements. Primitives dispatch to box/circle/ellipse/arc/line/arrow/spline/move/text/troff/block generators.

Attribute grammar translates dimensions, directions, from/to/at/by, with-corner/position, same, text attributes, heads, dot/dash/chop/fill/noedge, and nested text lists into the global attribute array.

Position grammar supports coordinates, relative offsets, position arithmetic, mixed x/y coordinates, interpolation, named places, object corners, first/last/nth references, and block member references.

Expression grammar implements arithmetic, comparisons, boolean operators, assignment, object component lookup, block variable lookup, math functions, random, min/max, and integer conversion.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pic/picy.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pic/pltroff.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/pic/pltroff.c

Troff output backend for `pic`. It converts picture coordinates into troff motions and `\D` drawing commands, manages `.PS/.PE` wrapping, scaling, current output position, and line directives.

`openpl` bounds and possibly shrinks the picture to `maxpswid`/`maxpsht`, initializes coordinate transforms, emits diagnostic bounding comments, disables fill mode, and starts `.PS`. `closepl` restores position and fill state.

Primitive emitters draw lines, arrows, boxes, circles, ellipses, arcs, splines, dots, labels, and raw troff text. Text positioning uses troff width calculations and vertical half-line adjustments.

Fill support emits PostScript-specific `\X` BeginObject/EndObject commands compatible with dpost conventions, combining fill and optional stroke.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pic/pltroff.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pic/prevy.tab.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/pic/prevy.tab.h

Checked-in yacc token header snapshot for `pic`. It defines token constants for object types, control constructs, attributes, positions, math functions, drawing styles, and operators.

The first object token values are deliberately fixed to match object type values used throughout the generator and printer code: `BOX` through `PLACE`.

The makefile updates this file from generated `y.tab.h` only when token definitions change, giving non-yacc C files a stable include.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pic/prevy.tab.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pic/print.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/pic/print.c

Walks the `pic` object list and emits drawing operations through the troff backend. It handles each object type, applies visibility/fill/style bits, places text, emits arrowheads, and updates output position.

Boxes/blocks compute bounds from center and dimensions; blocks themselves are not drawn but may carry text. Circles, ellipses, arcs, lines, arrows, splines, moves, text, and raw troff each dispatch to backend primitives.

Dotted and dashed lines/boxes are synthesized by subdividing line segments into dots or dash/space intervals. Splines are passed to the backend with dash metadata, though backend dash handling is limited.

`dotext` vertically spaces all text strings attached to an object, calling `label` with half-line offsets.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pic/print.c -->