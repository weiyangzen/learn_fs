# Group Research: group_1503_plan9_sources_os_plan9_plan9_sys_src_cmd_aux_antiword_misc_c_source_3e1e7c1adeac

Scope: `Docs/research_subset_a.md` includes `sources/os/plan9/plan9`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/misc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/misc.c

## Summary
`misc.c` provides shared utility code for Antiword’s Plan 9 tree copy: platform directory lookup, regular-file sizing, compound-document block reads, output-list splitting, number formatting, Unicode/string helpers, locale-to-mapping selection, and Word timestamp conversion.

## Main Responsibilities
- Resolves user/global Antiword configuration directories, with Plan 9 using the `home` environment variable and header-defined Antiword paths.
- Validates regular files and obtains sizes via `stat` outside RISC OS.
- Implements `bReadBytes()` and `bReadBuffer()` for reading OLE-style chained big/small block streams.
- Converts Word color IDs, Roman/alpha list numbers, UCS characters to UTF-8, and Word DTTM timestamps.
- Splits `output_type` linked lists at whitespace or hyphen boundaries for wrapping.
- Selects default character mapping files from locale codesets.

## Key Dependencies
Uses `antiword.h`, low-level Word helpers such as `ulDepotOffset()`, `usGetWord()`, `ulTranslateCharacters()`, allocation wrappers, debug/fail macros, and output-width helpers.

## Filesystem Relevance
This file is the closest in this group to direct filesystem behavior: it checks file metadata, seeks/reads document streams, and resolves config/mapping-file locations.

## Notes
`bReadBuffer()` treats damaged block depots as fatal warnings/errors. Locale parsing is environment-driven and predates modern UTF-8-default assumptions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/notes.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/notes.c

## Summary
`notes.c` builds and owns Antiword’s footnote/endnote metadata tables. It maps note reference positions to footnote/endnote types and prepares extracted footnote text for later output.

## Main Responsibilities
- Maintains global arrays for footnote reference offsets, endnote reference offsets, and footnote text records.
- Parses note metadata for Word for DOS, WinWord 1/2, Word 6/7, and Word 8 formats.
- Uses direct file reads for older flat formats and `bReadBuffer()` over Big/Small Block Depots for compound-document formats.
- Converts character positions to file offsets through `ulCharPos2FileOffset()`.
- Calls `szFootnoteDecryptor()` to materialize useful footnote text after note ranges are known.
- Exposes `eGetNotetype()` and `szGetFootnootText()` for downstream text processing.

## Key Dependencies
Depends on `antiword.h`, OLE block depot readers, FIB offset conventions, memory wrappers, and global character-position mapping functions.

## Filesystem Relevance
Reads structured regions from Word document files and compound streams but does not implement filesystem behavior.

## Notes
The implementation is version-specific and offset-table driven. Endnotes are absent for Word for DOS and WinWord 1/2 paths.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/notes.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/options.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/options.c

## Summary
`options.c` owns Antiword runtime options. In the Plan 9/non-RISC OS path it parses command-line options, chooses output mode, validates paper sizes, opens character mapping files, and derives defaults from environment state.

## Main Responsibilities
- Stores current options in `tOptionsCurr` with platform-specific defaults.
- Supports text, formatted text, PostScript, PDF, and XML-related command-line switches.
- Handles paper-size names for PS/PDF and computes paragraph width from page dimensions and margins.
- Searches mapping files in `ANTIWORDHOME`, user home Antiword directory, then global Antiword directory.
- Maps selected mapping-file names to internal encoding classes.
- Rejects unsupported output/encoding combinations such as PDF UTF-8, PDF Cyrillic, and PostScript UTF-8.
- Contains RISC OS choices-window UI handlers behind `__riscos`.

## Key Dependencies
Uses `getopt`, environment variables, `szGetDefaultMappingFile()`, `szGetHomeDirectory()`, `bReadCharacterMappingTable()`, and conversion geometry helpers.

## Filesystem Relevance
Important for config-file lookup and mapping-file opening. Plan 9 inherits the non-RISC OS path and Antiword directory constants from `antiword.h`.

## Notes
The mapping-file search logic is path-length guarded and emits warnings rather than silently truncating.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/options.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/out2window.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/out2window.c

## Summary
`out2window.c` converts buffered paragraph and table text into Antiword’s `diagram_type` output abstraction. It handles line movement, alignment, justification, outline numbering, and fixed-width table fallback rendering.

## Main Responsibilities
- Emits linked `output_type` substrings via `vSubstring2Diagram()`.
- Computes net line width after trimming trailing whitespace.
- Aligns text left, right, centered, or justified by adding spaces across whitespace “holes”.
- Maintains heading counters for outline-style numbering.
- Formats Word table rows into text-window lines when XML table output does not handle them.
- Computes column widths from Word twips, character width, and paragraph-break magnification.

## Key Dependencies
Uses output dispatch functions from `output.c`, text-width helpers, table row metadata, list numbering helpers from `misc.c`, and UTF-8/column-count utilities.

## Filesystem Relevance
No direct filesystem interaction. This is userland presentation logic for document output.

## Notes
The table fallback assumes fixed-width font behavior and skips rows whose parsed column count does not match row metadata.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/out2window.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/output.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/output.c

## Summary
`output.c` is Antiword’s generic output dispatcher. It creates/destroys `diagram_type` objects and routes paragraph, substring, page, image, list, table, and prologue/epilogue operations to text, formatted text, PostScript, XML, or PDF backends.

## Main Responsibilities
- Captures current conversion type and encoding from parsed options.
- Initializes the selected backend in `pCreateDiagram()`.
- Finalizes the selected backend in `vDestroyDiagram()`.
- Adds second-stage document metadata/fonts after Word version is known.
- Dispatches line movement, substring output, paragraph starts/ends, page breaks, XML list/table events, and image prologues/epilogues.
- Provides `bAddDummyImage()` and `bAddTableRow()` backend capability shims.

## Key Dependencies
Depends on backend functions in text/FMT/XML/PostScript/PDF modules, global options, and image/table metadata types from `antiword.h`.

## Filesystem Relevance
No direct filesystem interaction beyond writing to `stdout` through backend output functions.

## Notes
This module centralizes output-mode branching, keeping parsing code mostly independent from concrete output formats.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/output.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/pdf.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/pdf.c

## Summary
`pdf.c` is a hand-written PDF 1.3 backend. It emits catalog/pages/info/resources/font objects, tracks file positions for xref generation, manages page flow, and writes text and inline image data.

## Main Responsibilities
- Maintains object numbers, page object arrays, object offsets, stream positions, and xref trailer state.
- Creates document information dictionaries from parsed Word metadata.
- Emits standard Type 1 font resources and Latin-1/Latin-2 encoding differences.
- Handles headers and footers per section/page, including first-page and odd/even variants.
- Moves text positions in PDF text matrices and creates new pages when footer space is reached.
- Emits inline images for JPEG, PNG, DIB, and fallback formats with appropriate filters and color spaces.
- Escapes PDF strings and supports superscript/subscript baseline shifts.

## Key Dependencies
Uses document metadata getters, header/footer lists, output alignment helpers, image metadata, color conversion, font lookup, and ASCII85/image translators.

## Filesystem Relevance
Writes PDF bytes to the output stream and uses `ftell()` to reconcile image byte positions. It does not read filesystem metadata.

## Notes
PDF support explicitly excludes UTF-8 and Cyrillic encodings via option validation and runtime checks.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/pdf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/pictlist.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/pictlist.c

## Summary
`pictlist.c` implements a small private singly linked list mapping Word text/file offsets to picture-data offsets.

## Main Responsibilities
- Stores `picture_block_type` records in insertion order.
- Ignores invalid text offsets and invalid picture-storage offsets.
- Provides cleanup through `vDestroyPictInfoList()`.
- Exposes lookup through `ulGetPictInfoListItem()`.

## Key Dependencies
Uses `antiword.h`, allocation wrappers, `FC_INVALID`, and picture records produced by property parsers such as `prop2.c` and `prop6.c`.

## Filesystem Relevance
No direct filesystem calls. The stored offsets refer to positions inside Word document streams and are later used by image extraction paths.

## Notes
Lookup is linear, which is acceptable for the expected small picture counts in legacy Word documents.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/pictlist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/png2eps.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/png2eps.c

## Summary
`png2eps.c` translates PNG image payloads from a Word document into backend image output by streaming PNG `IDAT` chunks through ASCII85 encoding.

## Main Responsibilities
- Validates and skips the PNG signature.
- Walks PNG chunks, searching for `IDAT` data and stopping at `IEND`.
- Skips chunk payloads and CRCs while tracking remaining byte budget.
- Emits backend image prologue/epilogue calls.
- Sends compressed IDAT bytes unchanged through `vASCII85EncodeArray()`, relying on PS/PDF Flate decode filters.
- In debug builds, can dump extracted PNG bytes to `/tmp/pic/picNNNN.png`.

## Key Dependencies
Uses PNG chunk constants from `antiword.h`, file-position helpers such as `bSetDataOffset()`, byte readers, ASCII85 encoders, and backend image functions.

## Filesystem Relevance
Reads image bytes from the Word document stream. Debug dumping writes temporary PNG files.

## Notes
This is not a full PNG decoder; it preserves compressed pixel data and lets the output backend declare the decompression/filter pipeline.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/png2eps.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/png2sprt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/png2sprt.c

## Summary
`png2sprt.c` is the RISC OS sprite-side PNG translation stub. It does not decode PNG and instead emits a dummy image placeholder.

## Main Responsibilities
- Defines `bTranslatePNG()` for the sprite conversion build path.
- Returns `bAddDummyImage()` for any PNG input.

## Key Dependencies
Uses `antiword.h` and the generic image placeholder dispatch.

## Filesystem Relevance
No direct filesystem behavior. Parameters include the source file and image offsets, but they are unused.

## Notes
The file documents that PNG-to-sprite conversion was not implemented in this Antiword version.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/png2sprt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/postscript.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/postscript.c

## Summary
`postscript.c` is the PostScript backend. It emits DSC headers/trailers, font re-encoding prologs, page flow, headers/footers, formatted text, and EPS-wrapped images.

## Main Responsibilities
- Initializes page size, orientation, encoding, image level, and page counters.
- Emits PostScript document headers, creator/date metadata, bounding boxes, font lists, and page setup.
- Provides ISO-8859-1, ISO-8859-2, and ISO-8859-5 font re-encoding data.
- Handles section-aware headers/footers and starts new pages when body text reaches footer space.
- Writes text strings with PostScript escaping, underline/strike rendering, superscript/subscript movement, font changes, and RGB colors.
- Emits EPS image wrappers for JPEG, PNG, DIB, and fallback images using ASCII85/DCT/Flate/filter pipelines.
- Supports dummy image boxes when image data cannot be emitted.

## Key Dependencies
Uses output alignment helpers, metadata/header/footer getters, font-table APIs, image translators, color conversion, time/user environment data, and geometry helpers.

## Filesystem Relevance
Writes PostScript to `stdout`; reads user name from environment. No filesystem metadata handling.

## Notes
PostScript UTF-8 is unsupported. Image output has a Ghostscript-special PNG predictor mode.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/postscript.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/prop0.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/prop0.c

## Summary
`prop0.c` parses property information from Word for DOS files. It extracts document dates/default tab width, sections, paragraph styles, character font runs, and simple heading/style metadata.

## Main Responsibilities
- Converts DOS-style summary dates to `time_t`.
- Reads Word for DOS summary blocks and creates document info records.
- Reads section descriptors and section property bytes from 128-byte pages.
- Parses section break behavior.
- Parses paragraph property pages into style records, including heading levels, alignment, indents, and before/after spacing.
- Parses character property pages into font records, including bold/italic/underline/strike/caps/hidden, superscript/subscript, font number, size, and color.

## Key Dependencies
Uses direct `bReadBytes()` reads, Word byte/word helpers, style/font/document list builders, stylesheet defaults, and file-offset/character-position conventions.

## Filesystem Relevance
Reads fixed-layout regions from legacy Word for DOS files. No OS filesystem logic.

## Notes
Parsing is conservative: invalid FODO offsets are skipped, and missing section properties fall back to defaults.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/prop0.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/prop2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/prop2.c

## Summary
`prop2.c` parses property information for WinWord 1 and WinWord 2 files. It handles document properties, sections, header/footer offset tables, paragraph/table row properties, character/font runs, and picture references.

## Main Responsibilities
- Defines `iGet2InfoLength()` to advance through WinWord 1/2 sprm/property streams.
- Reads document properties including header/footer specification, default tab width, and DTTM dates.
- Parses section PLCs, section property pages, and header/footer character-position tables.
- Detects table cells/end-of-row markers and extracts column widths/border flags.
- Parses paragraph properties for alignment, numbering, tab changes, indents, and spacing.
- Reads paragraph and character BTE pages, extending page lists from header counters when needed.
- Applies WinWord 1 and WinWord 2 character property formats to font records.
- Extracts picture offsets from character property data and adds them to the picture list.

## Key Dependencies
Uses direct file reads, stylesheet/font defaults, row/style/font/picture list builders, character-position mapping helpers, and `antiword.h` Word constants.

## Filesystem Relevance
Reads structured Word file pages from offsets. It is format parsing, not filesystem implementation.

## Notes
The parser includes defensive length checks around malformed table definitions and property runs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/prop2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/prop6.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/prop6.c

## Summary
`prop6.c` parses property information for Word 6 and Word 7/95 compound-document streams. It is the Word 6/7 counterpart to `prop2.c`, using Big Block Depot stream reads and newer sprm layouts.

## Main Responsibilities
- Defines `iGet6InfoLength()` for Word 6/7 property stream advancement.
- Reads document properties from the WordDocument stream via `bReadBuffer()`.
- Parses section PLCs, section property pages, outline numbering data, section breaks, columns, and header/footer flags.
- Builds header/footer metadata from PLC character-position tables.
- Detects table rows/cells and extracts borders/column widths from Word 6/7 table sprms.
- Parses paragraph property BTE pages into style records, including list metadata and file-offset conversion.
- Applies character property sprms for revision deletion, plain/default resets, bold/italic/strike/caps/hidden toggles, underline, font number, font size, color, superscript/subscript, and size increments.
- Extracts picture offsets from `fcPic` sprms while filtering OLE objects.

## Key Dependencies
Uses OLE Big Block Depot reads, style/font/row/header/footer/picture list APIs, stylesheet defaults, character-position-to-file-offset conversion, and Word constants.

## Filesystem Relevance
Reads from compound-file streams by depot chain. No kernel or filesystem implementation behavior.

## Notes
There is an apparent debug-only typo near `vGet6ChrInfo()` referencing `lBeginCharInfo` instead of `ulBeginCharInfo`; impact depends on debug macro expansion.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/prop6.c -->