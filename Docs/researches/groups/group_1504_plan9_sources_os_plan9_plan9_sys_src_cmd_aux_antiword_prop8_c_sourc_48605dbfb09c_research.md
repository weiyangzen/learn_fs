# Group Research: group_1504_plan9_sources_os_plan9_plan9_sys_src_cmd_aux_antiword_prop8_c_sourc_48605dbfb09c

Scope verified against `Docs/research_subset_a.md`: all files are under included source tree `sources/os/plan9/plan9`. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/prop8.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/prop8.c

This file parses Word 8/9/10/11, Word 97 through Word 2003, property streams and builds Antiword’s internal document metadata lists.

Key behavior:
- Reads Word table-stream records through big-block or small-block depots depending on stream size.
- Extracts document properties, section descriptors, header/footer offsets, list definitions, paragraph properties, table row bounds, character/font runs, and picture references.
- Decodes Word 8 SPRM/grpprl records by opcode class and applies recognized properties to `document_block_type`, `section_block_type`, `row_block_type`, `style_block_type`, `font_block_type`, and `picture_block_type`.
- Builds downstream lists via `vCreateDocumentInfoList`, `vAdd2SectionInfoList`, `vCreat8HdrFtrInfoList`, `vAdd2ListInfoList`, `vAdd2StyleInfoList`, `vAdd2RowInfoList`, `vAdd2FontInfoList`, and `vAdd2PictInfoList`.

Important details:
- `iGet8InfoLength()` is the local SPRM length decoder and has special handling for tab-change opcode `0xc615`.
- Table row detection combines explicit table flags and row-end table definition data.
- Word 8 list data is split between LFO, LSTF, LVLF, PAPX, CHPX, and XString records.
- Character property parsing rejects OLE objects as pictures and maps picture offsets through the Data stream.

Filesystem relevance:
- Indirect but important: this is binary document/container metadata parsing on top of OLE stream block reads.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/prop8.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/properties.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/properties.c

This file dispatches property extraction according to detected Word version.

Key behavior:
- `vGetPropertyInfo()` calls the version-specific stylesheet, document, section, paragraph, header/footer, character, font table, and summary readers.
- Skips expensive character/font/image-oriented parsing for output modes that do not need it.
- Handles Word for DOS, WinWord 1/2, Word 6/7, and Word 8; Word 4/5 has no active property extraction path here.
- `ePropMod2RowInfo()` resolves stored property modifiers and delegates row detection to the appropriate version parser.

Important details:
- The Word 8 path reads list information before stylesheet and paragraph data so list-dependent style data can be resolved.
- Font table correction is always run after property extraction.

Filesystem relevance:
- Indirect: coordinates parsing of file-resident Word metadata and OLE substreams.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/properties.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/propmod.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/propmod.c

This file stores and retrieves Word property modifier blobs.

Key behavior:
- Maintains a growable array of copied property modifier records.
- `vAdd2PropModList()` stores records whose first word is the byte length.
- `aucReadPropModListItem()` interprets even property modifiers as inline two-byte data and odd modifiers as array indices.
- `vDestroyPropModList()` releases every stored blob and resets counters.

Important details:
- `IGNORE_PROPMOD` returns no modifier.
- Debug builds grow the array in smaller increments than release builds.

Filesystem relevance:
- Indirect: supports fast-save/text-block property metadata recovered from Word file structures.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/propmod.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/riscos.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/riscos.c

This file implements RISC OS platform services used by Antiword.

Key behavior:
- `werr()` reports errors through DeskLib and exits on fatal severities.
- `iGetFiletype()` and `vSetFiletype()` read and set RISC OS file types through `OS_File`.
- `bMakeDirectory()` verifies or creates the directory portion of a dotted RISC OS path.
- Reads current alphabet and OS version through SWIs.
- In debug builds, `bGetJpegInfo()` queries JPEG metadata through the JPEG module.

Important details:
- Filetype-setting ignores expected read-only media errors.
- Directory parsing uses the last `.` as the directory/file separator.

Filesystem relevance:
- Direct platform filesystem support for RISC OS file metadata and directory creation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/riscos.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/rowlist.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/rowlist.c

This file manages a linked list of detected Word table-row records.

Key behavior:
- `vAdd2RowInfoList()` appends valid row ranges and copies the row layout.
- Rejects rows with invalid or equal start/end file offsets.
- Normalizes negative column widths to zero.
- `pGetNextRowInfoListItem()` iterates through rows in insertion order.
- `vDestroyRowInfoList()` frees the list and resets write/read cursors.

Important details:
- The read cursor is initialized to the first row when the first list member is added.

Filesystem relevance:
- Indirect: records file offsets for table rows discovered while parsing Word streams.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/rowlist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/saveas.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/saveas.c

This RISC OS file implements Save As handlers for generated Antiword diagrams.

Key behavior:
- Wraps DeskLib `Save_InitSaveWindowHandler` for text and Draw file output.
- `bText2File()` walks drawfile objects and writes text objects with inferred newlines and indentation.
- `bDraw2File()` writes a Draw file while translating Y coordinates from Antiword’s top-left layout to Draw’s bottom-left origin.
- Handles text, font-table, path, sprite, and JPEG drawfile object types.
- `bSaveTextfile()` and `bSaveDrawfile()` trigger saves from menu events or keyboard shortcuts.

Important details:
- Failed saves remove the partially written destination.
- Successful saves assign RISC OS filetypes for text or Draw files.

Filesystem relevance:
- Direct user-facing file creation and metadata setting for exported results.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/saveas.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/sectlist.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/sectlist.c

This file stores Word section information in a linked list.

Key behavior:
- Adds section records keyed by character position.
- Provides default section initialization with `bNewPage = TRUE`.
- `pGetSectionInfo()` returns the first section, a section matching a character position, or the previous section if no match is found.
- `tGetNumberOfSections()` counts records.
- `ucGetSepHdrFtrSpecification()` retrieves header/footer flags by section number.

Important details:
- If no section records exist, the getter creates a default section at character position zero.
- It treats `ulCharPos` and `ulCharPos + 1` as equivalent for lookup.

Filesystem relevance:
- Indirect: maps parsed file character positions to section rendering state.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/sectlist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/startup.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/startup.c

This RISC OS helper enforces a single running Antiword application instance.

Key behavior:
- Enumerates running tasks through `TaskManager_EnumerateTasks`.
- Performs case-insensitive task-name comparison.
- If Antiword is not running, chains `<Antiword$Dir>.!Antiword`, optionally passing a filename.
- If Antiword is running and a filename is supplied, sends a `message_DATALOAD` as if the file was dropped on the iconbar icon.
- If Antiword is already running without a file argument, reports an error.

Important details:
- Checks the filename length against the Wimp dataload message buffer.
- Debug builds append redirection to `<Antiword$Dir>.Debug`.

Filesystem relevance:
- Directly passes user-selected document paths to the running app and launches the application from the RISC OS application directory.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/startup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/stylelist.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/stylelist.c

This file stores paragraph style runs and normalizes list/indentation data for rendering.

Key behavior:
- Maintains a linked list of style records keyed by file offset and sequence number.
- Converts Word list bullet/private-use characters into output-specific text or UTF-8.
- Clamps excessive before/after paragraph spacing and corrects negative/invalid indents.
- Provides ordered iteration, text-only style iteration, and `usGetIstd()` lookup by file offset.
- Determines whether a paragraph style implies list membership.

Important details:
- Consecutive records at the same file offset collapse to the last style.
- A midpoint pointer and sequence-order flag optimize `usGetIstd()` scans.
- Heading styles are explicitly excluded from list detection.

Filesystem relevance:
- Indirect: ties parsed file offsets to layout/list rendering state.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/stylelist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/stylesheet.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/stylesheet.c

This file builds the stylesheet arrays used as defaults for paragraph and character formatting.

Key behavior:
- Stores style and font defaults in parallel arrays indexed by stylesheet records.
- Implements built-in WinWord 1/2 style/font defaults and `stc` to `istd` conversion.
- Parses WinWord 1/2, Word 6/7, and Word 8 stylesheet formats.
- Resolves base-style inheritance by repeatedly filling records whose base style is already known.
- Supplies `vFillStyleFromStylesheet()` and `vFillFontFromStylesheet()` to initialize run-level formatting.

Important details:
- Word 8 stylesheet names are Unicode and lengths are converted from characters to bytes.
- Unresolved or empty records fall back to default style/font data.
- Word 6/7 and Word 8 share similar STD/UPX parsing but differ in table stream/block access and name encoding.

Filesystem relevance:
- Indirect: reads stylesheet records from Word file streams and feeds rendering metadata.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/stylesheet.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/summary.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/summary.c

This file extracts document summary metadata and language information.

Key behavior:
- Stores title, subject, author, creation time, last-save time, application name, manager, company, and language ID.
- Parses DOS date strings, Word DTTM-derived values, and OLE FILETIME values.
- Reads OLE SummaryInformation and DocumentSummaryInformation streams through big/small block depots.
- Handles Word for DOS, WinWord 1/2, Word 6/7, and Word 8 summary sources.
- Provides getters for metadata strings, PDF-style dates, and locale-like language tags.

Important details:
- OLE property sections are validated for little-endian byte order and expected section count.
- LPSTR values are trimmed at both ends.
- Language ID handling includes many specific locale exceptions before applying a general low-byte language mapping.

Filesystem relevance:
- Directly parses OLE property streams embedded in the document container.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/summary.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/tabstop.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/tabstop.c

This file determines the document default tab width.

Key behavior:
- Maintains a global default tab width in millipoints.
- Reads `dxaTab` from version-specific document property locations for Word for DOS, WinWord 1/2, Word 6/7, and Word 8.
- Chooses big-block or small-block table access for Word 8 document properties.
- Resets to a half-inch default before each version-specific read.

Important details:
- A zero Word tab width falls back to half an inch.
- The public `lGetDefaultTabWidth()` implementation is compiled out in this file, so the active getter must come from elsewhere or configuration.

Filesystem relevance:
- Indirect: reads document property bytes from file/OLE streams.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/tabstop.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/text.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/text.c

This file implements plain text output primitives.

Key behavior:
- Initializes text-output state from conversion options.
- Writes substrings, line moves, paragraph starts/ends, and page ends to the output file.
- Emits UTF-8 strings unchanged, while non-UTF-8 output maps local non-breaking spaces to ordinary spaces.
- Converts horizontal position to filler characters when moving to a new text position.

Important details:
- Paragraph gaps at least `HEADING_GAP` become blank lines.
- `vSubstringTXT()` requires the provided length to match `strlen()`.

Filesystem relevance:
- Direct output writing through `FILE *`, but no filesystem metadata handling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/text.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/unix.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/unix.c

This file provides Unix replacements for a small set of RISC OS UI/platform functions.

Key behavior:
- `werr()` prints warnings/errors to `stderr` and exits for fatal severities.
- Defines no-op `Hourglass_On()` and `Hourglass_Off()`.

Important details:
- Fatal code `1` maps to `EXIT_FAILURE`; other fatal values are used as process exit codes.

Filesystem relevance:
- Minimal: reports errors for file operations performed elsewhere.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/unix.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/utf8.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/utf8.c

This file implements UTF-8 width and locale helpers.

Key behavior:
- Contains a table of combining/zero-width Unicode intervals.
- Converts UTF-8 byte sequences to UCS values.
- Computes display column width for UTF-8 strings using a Kuhn-derived `wcwidth` approach.
- Reports the byte length of a UTF-8 character.
- Detects whether the normalized locale codeset is UTF-8.

Important details:
- Invalid or truncated UTF-8 is not strongly validated; missing continuation bytes contribute zeroed payload bits.
- East Asian wide/fullwidth ranges count as width 2, combining/control handling follows the local table.

Filesystem relevance:
- None directly; supports correct text layout of decoded document content.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/utf8.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/version.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/version.h

This header defines Antiword release strings.

Key behavior:
- Sets purpose, author, version, platform-specific secondary version, and status strings.
- Version is `0.37  (21 Oct 2005)`.
- Debug builds identify themselves as `DEBUG version`; release builds report GPL status.

Important details:
- RISC OS author string uses a copyright symbol variant, while other platforms use ASCII `(C)`.

Filesystem relevance:
- None directly.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/version.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/word2text.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/word2text.c

This file is Antiword’s main Word-to-output rendering pipeline.

Key behavior:
- Initializes a document, reads options, prepares headers/footers and notes, and emits through the selected output backend.
- Walks text, footnote, endnote, text-box, and header text-box lists.
- Applies style, font, list, section, table-row, hidden-text, deletion-mark, image, note, tab, and page-break state while reading characters.
- Converts list numbers, bullets, roman numerals, alphabetic counters, notes, images, and tables into output records.
- Provides separate decryptors for header/footer output and XML footnote text.

Important details:
- Output is accumulated as a doubly linked list of `output_type` fragments, split and justified when width limits are exceeded.
- Table rows temporarily switch to a fixed table font and are rendered via `vTableRow2Window()`.
- Embedded Word control ranges are skipped between `START_EMBEDDED` and `END_IGNORE`/`END_EMBEDDED`.
- The pipeline frees all document-global lists through `vFreeDocument()` after conversion.

Filesystem relevance:
- Central consumer of parsed file streams; output writing is delegated to backend functions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/word2text.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/wordconst.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/wordconst.h

This header defines core constants and macros for Word parsing and output conversion.

Key contents:
- OLE/Word block sizes, small-vs-big stream threshold, invalid offsets, max columns/tabs, font sizes, font style bits, colors, list types, alignment values, and table border flags.
- Little-endian and big-endian byte extraction macros.
- Unit conversion macros for twips, millipoints, draw units, points, and character cells.
- Word control characters, pseudo note characters, Unicode constants, and platform-local fallback glyphs.

Important details:
- The constants establish the shared interpretation contract for nearly every parser in this group.
- `FC_INVALID`, `CP_INVALID`, `END_OF_CHAIN`, and block-size constants are especially important for OLE stream traversal.

Filesystem relevance:
- Indirect but foundational: defines block/container constants used by Word/OLE file readers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/wordconst.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/worddos.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/worddos.c

This file initializes Word for DOS documents.

Key behavior:
- Reads the 128-byte Word for DOS header.
- Verifies the DOS magic identifier and detected version.
- Rejects autosave/fast-saved DOS documents.
- Adds a single non-Unicode text block starting after the 128-byte header.
- Triggers property, tab-width, and notes extraction for version 0.

Important details:
- Text length is derived from the header’s file length field minus the header size.
- Property and notes extraction are called with no OLE PPS/depot data.

Filesystem relevance:
- Direct parsing of flat pre-OLE Word document files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/worddos.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/wordlib.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/wordlib.c

This file provides common Word file identification, version detection, document initialization dispatch, and cleanup.

Key behavior:
- Checks file signatures for Word for DOS, WinWord 1/2, Mac Word 4/5, OLE Word files, RTF, and WordPerfect.
- Maps FIB/version header values to Antiword version numbers.
- Tracks old Macintosh Word files for character translation behavior.
- Dispatches initialization to DOS, Windows, Mac, or OLE handlers.
- `vFreeDocument()` destroys every global parsing/rendering list.

Important details:
- OLE file detection tolerates certain extra trailing bytes caused by buggy email/base64 handling.
- Unknown FIB values below Word 97 are rejected; newer values are treated as Word 8 format.

Filesystem relevance:
- Direct file signature inspection and top-level file-format dispatch.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/wordlib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/wordmac.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/wordmac.c

This file initializes old Macintosh Word 4/5 documents.

Key behavior:
- Reads a 256-byte header and verifies the Mac Word magic value.
- Rejects fast-saved Mac documents.
- Reads big-endian text start/end offsets and creates one non-Unicode text block.
- Invokes property extraction and default tab-width setup for Word 4/5.

Important details:
- Character positions are initialized to the same values as file offsets.
- Word 4/5 property extraction is effectively sparse in `properties.c`.

Filesystem relevance:
- Direct parsing of flat pre-OLE Macintosh Word files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/wordmac.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/wordole.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/wordole.c

This file parses OLE Compound File storage for Word 6 and later documents.

Key behavior:
- Reads Big Block Depot, Small Block Depot, root directory chain, and property set storage entries.
- Finds `WordDocument`, `Data`, `0Table`, `1Table`, `SummaryInformation`, and `DocumentSummaryInformation` streams.
- Chooses the active table stream from the Word header status bit.
- Reads the WordDocument FIB/header and initializes text, data, properties, tabs, and notes.
- Handles Word 6/7 and Word 8 text/data block discovery differently.

Important details:
- PPS entries are converted from UTF-16-ish names to narrow strings and assigned tree levels with recursion limits to avoid loops.
- Files without a WordDocument stream are distinguished from Excel workbooks for diagnostics.
- Small streams use the small-block depot; large streams use the big-block depot.
- The initializer rejects encrypted documents and unsupported pre-Word-6 OLE content.

Filesystem relevance:
- Direct and central: implements OLE compound-file stream traversal and substream discovery.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/wordole.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/wordtypes.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/wordtypes.h

This header defines Antiword’s shared Word parsing and rendering data types.

Key contents:
- Basic unsigned integer typedefs.
- Platform-specific `diagram_type` for RISC OS drawfile/window output or generic `FILE *` output.
- Output fragments, conversion and encoding enums, options, font table entries, OLE PPS info, text/data blocks, document/row/style/font/picture/section/header/footer/note/list blocks, image metadata, row detection enum, note type enum, and image info enum.

Important details:
- `pps_info_type` is the OLE stream map used by Word 6+ parsing.
- `text_block_type` carries file offset, character position, length, Unicode flag, and property modifier.
- `style_block_type` is the central structure for paragraph/list rendering state.

Filesystem relevance:
- Indirect but foundational: models file offsets, stream positions, and parsed document structures.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/wordtypes.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/wordwin.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/wordwin.c

This file initializes WinWord 1/2 documents.

Key behavior:
- Reads a 384-byte header and verifies WinWord 1.x or 2.0 magic.
- Rejects fast-saved and encrypted documents.
- Builds one text block covering main text plus footnotes, headers/footers, macros, and annotations.
- Splits the block list into logical text sublists.
- Builds a coarse data block for images when image output is enabled.
- Invokes property, tab-width, and notes extraction.

Important details:
- Data block discovery uses the range between end-of-text and character-info start as an image-containing region.
- Text-only, formatted-text, XML, and no-image modes skip data block setup.

Filesystem relevance:
- Direct parsing of flat pre-OLE Windows Word files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/wordwin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/xmalloc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/xmalloc.c

This file wraps memory allocation with fatal error handling.

Key behavior:
- `xmalloc()`, `xcalloc()`, and `xrealloc()` never return `NULL`; they call `werr(1, ...)` on allocation failure.
- Zero-size `malloc`/`calloc` requests are normalized to one byte/item.
- `xstrdup()` provides a portable string duplicate implementation.
- `xfree()` frees non-null pointers and returns `NULL` for assignment-style cleanup.

Important details:
- 16-bit DOS builds reject allocations larger than segment-addressable memory in `xcalloc()`.
- Most list managers in this group depend on `xfree()` returning `NULL` to reset pointers.

Filesystem relevance:
- None directly; supports robust allocation while parsing file data.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/xmalloc.c -->