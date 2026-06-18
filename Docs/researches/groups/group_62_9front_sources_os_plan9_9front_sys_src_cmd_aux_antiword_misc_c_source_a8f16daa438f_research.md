# Group Research: group_62_9front_sources_os_plan9_9front_sys_src_cmd_aux_antiword_misc_c_source_a8f16daa438f

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/misc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/misc.c

Miscellaneous Antiword support routines shared across parsing, conversion, layout, locale setup, and diagnostics.

Key responsibilities:
- Finds user and Antiword configuration directories, with platform branches for VMS, Plan 9, DOS, NetWare, and RISC OS.
- Provides file-size and positioned-read helpers, including `bReadBuffer()` for following Word big/small block depot chains.
- Implements output-list splitting, Roman/alpha numbering, color mapping, basename extraction, line-leading calculation, zero-buffer checks, UCS-to-UTF-8, and bullet rendering.
- Converts counted Word Unicode strings to configured single-byte output and measures null-terminated UTF-16 byte length.
- Normalizes locale codeset names and chooses default character mapping files for non-RISC OS builds.
- Converts Word DTTM packed date/time values to `time_t`.

Dependencies:
- Uses `antiword.h` core types and helpers such as `xmalloc`, `xfree`, `werr`, `ulDepotOffset`, `lComputeStringWidth`, `ulTranslateCharacters`, and endian accessors.
- Uses C/POSIX file APIs, locale environment variables, `stat`, and `mktime`.

Notable risks:
- `bReadBuffer()` detects out-of-range depot indexes but does not detect cyclic block chains.
- File offsets are constrained through `long`/`ULONG`; very large files are rejected or truncated by design.
- Locale parsing is handcrafted and assumes classic `language[_territory][.codeset][@modifier]` formatting.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/notes.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/notes.c

Footnote/endnote table reader for distinguishing note references and preparing footnote body text.

Key responsibilities:
- Maintains global footnote-reference, endnote-reference, and footnote-text lists.
- Parses Word for DOS, WinWord 1/2, Word 6/7, and Word 8+ note PLCF structures from version-specific FIB offsets.
- Selects direct file reads for older flat files and big/small block depot reads for compound-file table streams.
- Converts note character positions to file offsets for later reference classification.
- Prepares footnote text lazily through `szFootnoteDecryptor()`.
- Exposes cleanup, note type lookup, and indexed footnote text retrieval.

Dependencies:
- Uses Antiword block depot readers, character-position/file-offset conversion, PPS table-stream metadata, and `footnote_block_type`.

Notable risks:
- State is global and must be reset with `vDestroyNotesInfoLists()` between documents.
- Endnote references are tracked, but only footnote text bodies are stored here.
- `szGetFootnootText()` contains a spelling error in the public symbol name, likely preserved for internal callers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/notes.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/options.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/options.c

Runtime option parser and character mapping file loader for Antiword.

Key responsibilities:
- Holds current options with defaults for paragraph width, conversion type, removed/hidden text handling, encoding, page size, image level, and RISC OS scale settings.
- Defines known paper sizes for PostScript/PDF output.
- Resolves mapping files from `ANTIWORDHOME`, `$HOME/.antiword`, and the global Antiword directory, adding `.txt` when needed.
- Maps selected mapping files to coarse encodings: Latin-1, Latin-2, Cyrillic, and UTF-8.
- Parses non-RISC OS CLI flags for landscape, paper size, formatted text, image handling, mapping file, PostScript/PDF, raw text, width, and XML DocBook output.
- Contains RISC OS choices-file and GUI event handling under `__riscos`.

Dependencies:
- Uses `getopt`, environment variables, Antiword mapping-table reader, output conversion enums, and RISC OS Wimp APIs when enabled.

Notable risks:
- Mapping filename storage is capped at 32 characters plus suffix.
- PDF/PostScript explicitly reject UTF-8; PDF also rejects Cyrillic.
- Option state is global, so callers rely on `iReadOptions()` before output creation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/options.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/out2window.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/out2window.c

Text-window layout adapter that turns Antiword output runs into diagram lines, aligned paragraphs, heading numbers, and fallback table text.

Key responsibilities:
- Emits linked `output_type` string runs into a `diagram_type`, preserving font/style/color metadata.
- Computes net line width, strips trailing whitespace, applies left/center/right alignment, and justifies text by distributing spaces.
- Maintains nine heading counters and renders outline numbering in Arabic, Roman, alpha, and outline-number styles.
- Sets left indentation in draw units.
- Removes Word table-row terminators and formats table rows into fixed-width text columns when XML table handling does not consume them.
- Calculates byte-safe wrapping for multi-byte/UTF-8 strings using column counts and character-length helpers.

Dependencies:
- Uses output/backend dispatcher calls such as `vMove2NextLine`, `vSubstring2Diagram`, and `bAddTableRow`.
- Uses style, section, and row metadata from Antiword parsing layers.

Notable risks:
- Justification rewrites run storage in place and depends on accurate string widths.
- Table rendering assumes fixed-width font behavior and warns/skips when parsed column counts do not match row metadata.
- Heading counters are static global state reset by `vResetStyles()`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/out2window.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/output.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/output.c

Generic output dispatcher that routes document events to text, formatted text, PostScript, XML, or PDF backends.

Key responsibilities:
- Creates and destroys `diagram_type` output contexts.
- Reads current options, records active conversion type and encoding, and calls backend prologue/epilogue functions.
- Dispatches image prologue/epilogue and dummy-image insertion.
- Dispatches second-stage document setup: PS fonts, XML book intro, PDF info dictionary and fonts.
- Routes line movement, substrings, paragraph boundaries, page boundaries, headers, lists, list items, table ends, and table rows to supported backends.
- Maintains common behavior such as advancing `pDiag->lXleft` after substring output.

Dependencies:
- Depends on backend modules for TXT/FMT/PS/XML/PDF functions and on global options from `options.c`.

Notable risks:
- Backend selection is global after prologue, so mixed simultaneous output contexts are not supported.
- Unsupported conversion/event combinations usually no-op rather than report errors.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/output.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/pdf.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/pdf.c

Handwritten PDF 1.3 backend for Antiword text, pages, fonts, metadata, headers/footers, and inline images.

Key responsibilities:
- Tracks PDF object numbers, xref locations, page objects, stream lengths, current page, section, font, color, and cursor position.
- Writes catalog, info dictionary, pages tree, resources, font objects, encoding differences, xref table, and trailer.
- Supports Latin-1 and Latin-2 font encodings; rejects UTF-8 and Cyrillic PDF output.
- Renders headers and footers through existing output-run alignment logic while avoiding recursive page breaks in footer space.
- Emits text objects with font/color switching, PDF string escaping, octal high-byte escaping, and sub/superscript text rise.
- Embeds JPEG, PNG, and DIB image data as inline images with ASCII85 plus DCT/Flate/DecodeParms as appropriate.
- Adds dummy image rectangles when full image output is unavailable.

Dependencies:
- Uses Antiword metadata getters, font tables, header/footer lists, image metadata, geometry conversion helpers, and `vAlign2Window`.

Notable risks:
- PDF state is entirely static/global and not reentrant.
- File position accounting uses `vfprintf()` return values and resets via `ftell()` after raw image bytes.
- Metadata strings are inserted into PDF literal strings without full PDF escaping beyond the text-output path.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/pdf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/pictlist.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/pictlist.c

Small linked-list registry for Word picture reference offsets.

Key responsibilities:
- Stores `picture_block_type` records in insertion order.
- Skips invalid logical reference offsets and invalid picture-storage offsets.
- Looks up a picture storage file offset by the file offset where the picture marker appears.
- Frees the full picture list and resets anchor/tail state.

Dependencies:
- Uses Antiword allocation helpers and `picture_block_type`/`FC_INVALID`.

Notable risks:
- Lookup is linear.
- State is global and document-scoped; cleanup is required between documents.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/pictlist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/png2eps.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/png2eps.c

PNG-to-EPS/PDF data bridge that extracts PNG IDAT chunks and forwards compressed image bytes through ASCII85 output.

Key responsibilities:
- Skips the PNG signature and walks PNG chunks until `IDAT` or `IEND`.
- Validates chunk names as alphabetic four-byte identifiers.
- Returns IDAT data lengths and skips non-image chunks plus CRCs.
- For each IDAT chunk, streams compressed data through `vASCII85EncodeArray()`.
- Wraps image data with backend image prologue/epilogue calls.
- Includes a debug-only helper to dump original PNG images to `/tmp/pic`.

Dependencies:
- Uses byte-reading helpers, PNG chunk constants, ASCII85 encoder, and backend image functions.

Notable risks:
- It does not decode PNG; it relies on downstream PostScript/PDF filters understanding the compressed IDAT stream.
- Chunk walking is minimal and treats malformed chunk names or lengths as failure.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/png2eps.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/png2sprt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/png2sprt.c

RISC OS sprite-output stub for PNG images.

Key responsibilities:
- Defines `bTranslatePNG()` for the sprite backend.
- Does not implement PNG-to-sprite conversion.
- Inserts a backend dummy image placeholder instead.

Dependencies:
- Uses `bAddDummyImage()` and Antiword image metadata types.

Notable risks:
- PNG images are intentionally unsupported for this backend, so visual output is a placeholder only.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/png2sprt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/postscript.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/postscript.c

Handwritten PostScript backend for paginated Antiword output, fonts, text styling, headers/footers, and embedded images.

Key responsibilities:
- Tracks page geometry, landscape mode, encoding, image level, current font/color/position, page count, image count, section index, and first-page state.
- Writes DSC header fields, page setup, prologue functions, encoding redefinitions, document font list, pages, trailer, and EOF.
- Supports Latin-1, Latin-2, and Cyrillic PostScript re-encoding; rejects UTF-8.
- Handles header/footer rendering and page transitions with footer-space recursion protection.
- Emits text with PostScript string escaping, octal high-byte escaping, underline/strike rendering via `LineShow`, and sub/superscript movement.
- Emits EPS-wrapped JPEG/PNG/DIB image streams using ASCII85, DCT/Flate/PNGPredictor filters, color spaces, palettes, and decode arrays.
- Provides dummy image rectangles for unavailable image data.

Dependencies:
- Uses Antiword font tables, metadata, header/footer APIs, image metadata, geometry conversion, style checks, and output alignment.

Notable risks:
- Static global output state prevents concurrent independent PostScript streams.
- EPS/image generation assumes target interpreters support the emitted filters and optional Ghostscript PNG predictor path.
- Page count is written at trailer time and depends on correct page transition bookkeeping.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/postscript.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/prop0.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/prop0.c

Word for DOS property extractor for document, section, paragraph, and character formatting metadata.

Key responsibilities:
- Parses DOS-style summary dates and converts them to `time_t`.
- Reads DOP-like document defaults, including default tab width and creation/revision dates.
- Reads section descriptor pages and extracts basic section properties such as new-page behavior.
- Reads paragraph property pages, derives style records, heading levels, alignment, indents, and spacing.
- Reads character property pages, derives font number, size, bold/italic/underline/strike/caps/hidden/subscript/superscript/color state.
- Adds parsed document, section, style, and font records to the shared Antiword info lists.

Dependencies:
- Uses 128-byte Word for DOS block/page structures, endian accessors, file reads, stylesheet defaults, and list insertion helpers.

Notable risks:
- Many offsets and structure lengths are fixed to old Word for DOS layouts.
- Invalid FODO offsets are skipped silently except for debug diagnostics.
- Date parsing accepts flexible separators but only two-digit years.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/prop0.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/prop2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/prop2.c

WinWord 1/2 property extractor for document properties, sections, headers/footers, paragraph/table metadata, character formatting, and pictures.

Key responsibilities:
- Implements `iGet2InfoLength()` for skipping WinWord 1/2 SPRM/property records.
- Reads DOP data for header/footer specification, default tabs, and created/revised DTTM dates.
- Parses section PLCF/SEPX data and header/footer character-position tables.
- Parses paragraph FKPs, style changes, indentation, spacing, list numbering fields, and table row/cell metadata.
- Detects row boundaries and border/column definitions for table output.
- Applies WinWord 1 and WinWord 2 CHPX character formatting variants to stylesheet-derived font records.
- Extracts picture offsets from character properties and registers them in the picture list.

Dependencies:
- Uses FIB offsets for WinWord 1/2, 512-byte FKPs, stylesheet helpers, row/picture/font/style list APIs, and direct file reads.

Notable risks:
- Property-length decoding is central; a wrong SPRM length desynchronizes parsing.
- Picture offsets are bounded by a hard-coded 32 MiB maximum.
- Table-state detection is heuristic over `fInTable`, `fTtp`, and table-definition properties.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/prop2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/prop6.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/prop6.c

Word 6/7 property extractor for compound-document table stream properties, sections, headers/footers, paragraph/table data, character formatting, and pictures.

Key responsibilities:
- Implements `iGet6InfoLength()` for Word 6/7 SPRM/property record traversal.
- Reads DOP data from the WordDocument stream through the big block depot.
- Parses section PLCF/SEPX data, including outline numbering descriptors, page-break behavior, header/footer specification, and list-level flags.
- Builds header/footer character-position lists.
- Parses paragraph FKPs from big-block reads, fills styles from stylesheets, applies paragraph SPRMs, and converts character positions to file offsets/list IDs.
- Detects table cells, row ends, borders, and column widths.
- Applies detailed character SPRMs for revision deletion, plain/default formatting, bold/italic/strike/caps/hidden, font number, underline, size, color, sub/superscript, and size deltas.
- Extracts picture references from `fcPic` while rejecting OLE objects and converts data positions to file offsets.

Dependencies:
- Uses compound-file block depot reads, FIB offsets, stylesheet helpers, character-position mapping, and shared document/section/header/style/font/row/picture list APIs.

Notable risks:
- Static SPRM length tables must match Word 6/7 binary format exactly.
- Several unsupported or partially handled SPRMs are logged only in debug paths.
- The parser trusts FKP run counts and offset arithmetic after basic bounds checks.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/prop6.c -->