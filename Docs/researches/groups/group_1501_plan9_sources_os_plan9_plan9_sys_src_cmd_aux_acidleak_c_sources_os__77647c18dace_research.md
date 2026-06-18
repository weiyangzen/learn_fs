# Group Research: group_1501_plan9_sources_os_plan9_plan9_sys_src_cmd_aux_acidleak_c_sources_os__77647c18dace

Scope verified against `Docs/research_subset_a.md`: all files are under included source tree `sources/os/plan9/plan9`. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/acidleak.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/acidleak.c

This file implements `acidleak`, a Plan 9 auxiliary tool that reads heap/block tracing records from stdin and reports unreachable allocated blocks or emits a memory-map bitmap.

Key behavior:
- Parses `data`, `block`, `free`, and `range alloc` input records into growable arrays.
- Sorts blocks and data words by address, then marks reachable allocation blocks by following pointer-like values through heap headers.
- Treats candidate pointers as block starts at `value - 8` or `value - 16`, guessing common allocator header sizes.
- In text mode, prints unmarked non-free blocks as leak candidates.
- With `-b`, emits an `m8` bitmap where colors distinguish allocated, free, header, leaked, and leaked-header regions.
- Supports `-r` bitmap resolution and `-x` bitmap width.

Important details:
- `Block` records keep address, size, two header words, optional labels, mark/free flags, and first data pointer.
- `Data` records track source address, value, type, and owning block.
- Reachability is recursive through `markblock()`.
- Input trust is high; malformed or inconsistent traces can trigger assertions.

Filesystem relevance:
- Indirect: diagnostic utility for Plan 9 process/memory debugging, not filesystem implementation code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/acidleak.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/antiword.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/antiword.h

This is Antiword’s central project header. It defines platform constants, common macros, path names, output defaults, and prototypes for nearly every Antiword module.

Key behavior:
- Enforces exactly one of `DEBUG` or `NDEBUG`.
- Provides fallback definitions for `PATH_MAX`, time and size limits, separators, screen widths, margins, font names, mapping files, and platform-specific Antiword directories.
- Defines common comparison, rounding, bit, min/max, and element-count macros.
- Declares public functions across document detection, OLE/block depot handling, text/data block lists, character conversion, rendering backends, image translation, property parsing, fonts, lists, notes, options, output, and memory helpers.

Important details:
- The Plan 9 configuration uses `GLOBAL_ANTIWORD_DIR` as `/sys/lib/antiword`, local `ANTIWORD_DIR` as `lib/antiword`, and `fontnames` as the font-name file.
- RISC OS-specific GUI/drawfile APIs are conditionally exposed.
- The header is the coupling point between parsing, formatting, image, and output subsystems.

Filesystem relevance:
- Indirect to direct configuration relevance: defines where Antiword searches runtime support files such as character maps and font-name tables.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/antiword.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/asc85enc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/asc85enc.c

This file implements ASCII85 encoding for image/data streams written to PostScript or PDF-like output.

Key behavior:
- Buffers groups of four input bytes and emits five ASCII85 characters.
- Uses `z` as the compact encoding for all-zero 32-bit groups.
- Flushes partial groups and writes the `~>` end marker when passed `EOF`.
- Provides helpers to encode a fixed-length byte array or file region using Antiword’s data-stream reader.
- Limits output lines and avoids starting a line with `%%`, which can confuse some PostScript post-processors.

Important details:
- Encoder state is static, so each stream must be ended with `vASCII85EncodeByte(..., EOF)` to reset state.
- `vASCII85EncodeArray()` reads via `iNextByte()`, so it depends on `datalist.c` cursor state.

Filesystem relevance:
- Indirect: transforms embedded document image bytes after they have been mapped from file storage.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/asc85enc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/blocklist.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/blocklist.c

This file builds, splits, reads, and maps Antiword’s logical Word text block lists.

Key behavior:
- Maintains separate linked lists for main text, footnotes, headers/footers, macros, annotations, endnotes, text boxes, and header text boxes.
- Adds contiguous text blocks and merges adjacent compatible blocks.
- Splits the initially collected text stream into per-region lists using document character lengths.
- Removes empty text-box lists by reading their bytes and checking for whitespace/control-only content.
- Provides streaming character readers that handle byte and Unicode text blocks.
- Converts logical character positions to physical file offsets, header/footer offsets to character positions, and text file offsets to sequence numbers.

Important details:
- `readinfo_type` caches `BIG_BLOCK_SIZE` chunks and keeps independent cursors for general text, headers/footers, and footnotes.
- Unicode blocks consume two bytes per character.
- Some lengths are in characters while block lengths are stored in bytes; split logic accounts for this.
- Optional extension pads intermediate block lengths to big-block boundaries for certain file layouts.

Filesystem relevance:
- Direct document-storage mapping: translates Word logical text ranges into physical offsets inside compound-file block chains.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/blocklist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/chartrans.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/chartrans.c

This file translates Word character codes and Unicode values into Antiword’s selected local output encoding.

Key behavior:
- Contains codepage tables for DOS CP850, Windows CP1250/1251/1252, MacRoman, and Microsoft private-use symbols.
- Reads external character mapping tables, stores local-byte-to-Unicode mappings, and sorts them for binary search.
- Returns local bullet and non-breaking-space representations.
- Converts Word control/special characters into internal markers or ignores non-printing controls.
- Handles PS/PDF-specific Latin-1 substitutions for typography.
- Falls back from many Unicode punctuation, spaces, arrows, boxes, and symbols to simple ASCII approximations.
- Provides locale-independent uppercase conversion for ASCII and common Latin-1 characters.

Important details:
- UTF-8 output bypasses local table conversion and returns Unicode code points.
- Word note markers are resolved through `eGetNotetype()` based on file offset.
- Unmappable characters usually become `?`, except some layout/control marks are ignored.

Filesystem relevance:
- Indirect: consumes character data extracted from Word file streams and support mapping files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/chartrans.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/datalist.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/datalist.c

This file manages Antiword’s logical data block list and provides sequential binary readers over it.

Key behavior:
- Adds and merges contiguous data blocks mapping logical data positions to physical file offsets.
- Seeks the current data cursor to a physical file offset with `bSetDataOffset()`.
- Reads bytes through a `BIG_BLOCK_SIZE` cache, advancing across linked data blocks.
- Provides little-endian and big-endian word/long readers.
- Skips byte ranges and maps logical data positions back to file offsets.

Important details:
- EOF/error cases set `errno = EIO` because all byte values can be valid data.
- The reader assumes `pBlockCurrent` has been initialized by `bSetDataOffset()`.
- `ulGetDataOffset()` ignores its `FILE *` parameter and reports cursor position from internal state.

Filesystem relevance:
- Direct document-storage mapping: abstracts scattered Word/OLE data blocks as one readable byte stream.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/datalist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/debug.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/debug.h

This header defines Antiword’s debug and trace macros.

Key behavior:
- Under `DEBUG`, emits file/line-tagged messages, strings, chars, decimal/hex/float values, fixme markers, block dumps, and Unicode dumps.
- Under non-debug builds, expands those macros to empty statements.
- Provides conditional debug variants and explicit `NO_DBG_*` macros that are always empty.
- Under `TRACE`, emits trace messages and flushes stderr.

Important details:
- Debug macros use `stderr` directly and rely on helper functions declared elsewhere for block/Unicode dumps.
- This is compile-time instrumentation only.

Filesystem relevance:
- Indirect: helps inspect parsing and storage-mapping behavior during Antiword debugging.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/debug.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/depot.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/depot.c

This file computes physical offsets for OLE big-block and small-block depot indices.

Key behavior:
- Builds a cached list of big blocks that contain the small-block stream.
- Validates Big Block Depot chain indices while walking the chain.
- Converts a big-block index to `(index + 1) * BIG_BLOCK_SIZE`.
- Converts a small-block index through the cached small-block-list mapping and `SMALL_BLOCK_SIZE`.

Important details:
- `SIZE_RATIO` is `BIG_BLOCK_SIZE / SMALL_BLOCK_SIZE`.
- Returns `0` for invalid small-block mappings or unsupported block sizes.
- Big-block offset skips the OLE header block by adding one.

Filesystem relevance:
- Direct: maps OLE compound-document allocation tables to physical file offsets.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/depot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/dib2eps.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/dib2eps.c

This file translates embedded DIB bitmap images into EPS-compatible encoded image data.

Key behavior:
- Decodes uncompressed 1, 4, 8, and 24 bits-per-pixel DIB pixel data.
- Decodes RLE4 and RLE8 compressed bitmap data, handling end-of-line, end-of-file, literal packets, and basic escape handling.
- Skips bitmap info headers, color tables, and row padding.
- Converts 24-bit BGR input into RGB output.
- Emits decoded pixels via the ASCII85 encoder between image prologue and epilogue hooks.
- In debug builds, can dump DIB data as BMP-like files under `/tmp/pic`.

Important details:
- Input bytes come from `datalist.c` through `iNextByte()` and `tSkipBytes()`.
- Delta escapes in RLE streams terminate decoding rather than applying offsets.
- `bTranslateDIB()` first positions the data cursor with `bSetDataOffset()`.

Filesystem relevance:
- Indirect but storage-aware: reads embedded image streams from Word file data blocks and emits converted output.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/dib2eps.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/dib2sprt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/dib2sprt.c

This RISC OS-specific file translates embedded DIB images into RISC OS sprite objects for Draw output.

Key behavior:
- Computes sprite row byte widths for 1, 4, 8, and 24 bpp images.
- Allocates and initializes a sprite area, including palettes for low-color images.
- Reduces 24-bit and palette colors to the RISC OS default 256-color palette.
- Decodes uncompressed and RLE4/RLE8 DIB data into sprite pixel memory.
- Reverses bit/nibble ordering and writes rows bottom-up.
- Wraps the sprite into the current Draw diagram through `vImage2Diagram()`.

Important details:
- Uses DeskLib Sprite APIs and is not part of the Plan 9 build path.
- Reads image bytes through the Antiword data-list cursor.
- Debug sprite dumping is present but disabled by `#if 0`.

Filesystem relevance:
- Indirect: converts image data extracted from document storage; platform-specific rendering code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/dib2sprt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/doclist.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/doclist.c

This file stores the single document-information record used by Antiword.

Key behavior:
- Creates and destroys a one-record “document info list”.
- Returns the default tab width, falling back to half an inch when unavailable or zero.
- Returns the document header/footer specification byte from the stored document properties.

Important details:
- There is no real linked list; `pAnchor` points to a static `document_block_type`.
- Tab width is converted from twips to millipoints.

Filesystem relevance:
- Indirect: holds parsed document metadata after it is read from Word file streams.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/doclist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/draw.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/draw.c

This RISC OS-specific file builds, displays, scales, and manages Antiword Draw-format diagrams.

Key behavior:
- Provides fallback `flex_alloc/free/extend` wrappers for non-GNUC builds.
- Creates main and scale-view windows from templates.
- Allocates and initializes a Draw diagram with default memory and bounding box.
- Appends font tables, text objects, sprite/JPEG images, and dummy image placeholders.
- Tracks current output coordinates and paragraph/page movement.
- Implements RISC OS window redraw, title, keyboard, mouse, save-menu, and scale controls.
- Verifies and destroys diagrams, including cleanup of event-message references.

Important details:
- Diagram memory grows in 4 KiB increments from an initial 32 KiB.
- Text positioning accounts for font size, baseline, superscript, and subscript.
- Several list/table/header methods are dummy no-ops for Draw output.
- Uses DeskLib, Wimp, Drawfile, and flexlib APIs; not Plan 9 runtime code.

Filesystem relevance:
- Indirect: output rendering path for converted Word content, including save actions, but not filesystem internals.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/draw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/draw.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/draw.h

This header defines small helper types for RISC OS Draw image handling.

Key behavior:
- Includes Draw type definitions.
- Defines JPEG stream header and JPEG stream structures compatible with Draw data.
- Provides a union that can view image payloads as sprite, JPEG, byte, or word pointers.

Important details:
- The structures mirror Draw object layout and are used by RISC OS image rendering paths.

Filesystem relevance:
- Indirect: data layout support for converted embedded document images.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/draw.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/drawfile.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/drawfile.c

This file provides RISC OS Drawfile helper routines for creating, appending, rendering, validating, and querying diagrams.

Key behavior:
- Maps local Drawfile validation error codes to `os_error` structures.
- Calls RISC OS SWIs for bounding-box calculation and rendering.
- Initializes Drawfile headers with tag `Draw`, version 201.0, creator, and bounding box.
- Appends objects to diagram memory and optionally expands the diagram bounding box.
- Verifies text, path, sprite, JPEG, font-table, object-size, and diagram-header validity.
- Queries diagram bounding boxes and optionally converts Draw units to screen units.

Important details:
- Only a subset of object types is accepted by verification: font table, text, path, sprite, and JPEG.
- Text verification rejects control characters.
- Path verification requires at least one line and an end marker.

Filesystem relevance:
- Indirect: validates and renders converted output objects, not source file storage.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/drawfile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/drawfile.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/drawfile.h

This header defines RISC OS Drawfile constants, structures, SWI declarations, and helper prototypes.

Key behavior:
- Provides Draw/screen unit conversion macros.
- Defines DrawFile SWI numbers and object type/path type enums.
- Declares core Drawfile structures: font tables, text, paths, sprites, groups, tagged objects, text areas, options, transformed text/sprites, JPEGs, objects, and diagrams.
- Defines Drawfile error constants and path/text/render flag bits.
- Declares SWI wrappers and local helper functions for create, append, render, verify, and query operations.

Important details:
- Depends on DeskLib Sprite and Wimp types.
- Uses flexible one-element arrays for variable-sized Drawfile payloads.
- This is platform-specific support code preserved in the Antiword source tree.

Filesystem relevance:
- Indirect: describes serialized output layout for converted Draw files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/drawfile.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/fail.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/fail.c

This file implements Antiword’s custom assertion failure handler.

Key behavior:
- In non-`NDEBUG` builds, `__fail()` validates its arguments, optionally prints a debug message, and terminates through `werr(1, ...)`.
- Reports the failed expression, source file, and line number.

Important details:
- The function is compiled only when assertions are enabled.
- Runtime behavior depends on `werr()` for fatal reporting.

Filesystem relevance:
- Indirect: assertion support for document parsing and conversion code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/fail.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/fail.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/fail.h

This header defines Antiword’s `fail()` assertion macro.

Key behavior:
- In `NDEBUG`, `fail(e)` compiles to a no-op.
- Otherwise, if expression `e` is true, it calls `__fail()` with expression text, file, and line.
- Declares `__fail()`.

Important details:
- The macro is inverted compared with standard `assert`: callers pass the failure condition.

Filesystem relevance:
- Indirect: defensive checks throughout document storage parsing and rendering paths.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/fail.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/finddata.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/finddata.c

This file discovers the Word data blocks that contain non-text document data.

Key behavior:
- `bAddDataBlocks()` walks a Big Block Depot chain and adds physical ranges to the data block list.
- Handles starting offsets inside the first big block and caps each added range to remaining length.
- Rejects unused or out-of-range depot entries.
- `bGet6DocumentData()` reads Word 6/7 fast-save CLX text-info data, locates type-2 piece tables, and adds the corresponding data ranges.

Important details:
- Uses header offsets `0x160` and `0x164` for Word 6/7 CLX location and length.
- Reads CLX content through `bReadBuffer()` over the document block chain.
- The parser skips type-0/type-1 records and expects type 2 for piece data.

Filesystem relevance:
- Direct: follows Word block allocation chains and maps logical data streams to physical file offsets.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/finddata.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/findtext.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/findtext.c

This file discovers the Word file blocks that contain document text.

Key behavior:
- `bAddTextBlocks()` walks a block depot chain and adds logical character ranges as text blocks, accounting for single-byte versus Unicode text.
- `bGet6DocumentText()` reads Word 6/7 fast-save CLX data, records property modifiers, and builds text block ranges from the piece table.
- `bGet8DocumentText()` reads Word 8/97 CLX data from the table stream, choosing small-block or big-block depot based on stream size.
- Decodes Word 8 piece-table offsets, including the `BIT(30)` flag that indicates compressed single-byte text.

Important details:
- Text block file offsets are ultimately resolved relative to the WordDocument stream’s starting block.
- Property modifiers are stored through `vAdd2PropModList()`.
- Word 8 table-stream reading uses either `aulSBD`/`SMALL_BLOCK_SIZE` or `aulBBD`/`BIG_BLOCK_SIZE`.

Filesystem relevance:
- Direct: maps compound-document stream piece tables into physical file offsets for text extraction.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/findtext.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/fmt_text.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/fmt_text.c

This file implements Antiword’s “formatted text” output backend.

Key behavior:
- Initializes output encoding and diagram cursor state.
- Emits UTF-8 strings unchanged when UTF-8 output is selected.
- For non-UTF-8 output, preserves leading/trailing spaces, converts non-breaking spaces to normal spaces, and wraps visible text in simple style markers: `*bold*`, `/italic/`, and `_underline_`.
- Moves horizontally by emitting filler characters when the current diagram X/Y position changes.
- Advances the diagram cursor by the supplied string width after each substring.

Important details:
- Lazily resolves the local non-breaking-space byte through `ucGetNbspCharacter()`.
- Style markers exclude surrounding whitespace so spaces remain outside emphasis delimiters.
- Depends on diagram positioning fields even though output is textual.

Filesystem relevance:
- Indirect: output formatting layer for text extracted from Word document storage.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/fmt_text.c -->