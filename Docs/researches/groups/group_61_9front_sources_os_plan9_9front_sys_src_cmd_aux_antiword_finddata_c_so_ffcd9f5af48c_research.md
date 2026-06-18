# Group Research: group_61_9front_sources_os_plan9_9front_sys_src_cmd_aux_antiword_finddata_c_so_ffcd9f5af48c

Scope confirmed against `Docs/research_subset_a.md`: `sources/os/plan9/9front` is included. Every listed file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/finddata.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/finddata.c

This file builds data-block mappings for MS Word document data, especially Word 6/7 fast-save piece data.

Key routines:
- `bAddDataBlocks(...)` walks a Word OLE big-block chain from `ulStartBlock`, skips to the requested logical data offset, and appends `data_block_type` records through `bAdd2DataBlockList`.
- `bGet6DocumentData(...)` reads the Word 6/7 CLX/text-info area from header offsets `0x160`/`0x164`, parses fast-save records, and calls `bAddDataBlocks` for each type-2 piece.

Important behavior:
- Uses `BIG_BLOCK_SIZE` and BBD chain entries to translate logical document offsets into file offsets.
- Rejects invalid BBD indexes, `UNUSED_BLOCK`, damaged chains, null inputs, and lengths beyond `LONG_MAX`.
- Word 6/7 fast-save parsing recognizes record types `0`, `1`, and `2`; unknown types are fatal for this parse path.

Dependencies:
- `antiword.h` supplies types, constants, allocation helpers, endian helpers, list insertion, debug/fail macros, and `bReadBuffer`.

Role in antiword:
- Supplies non-text data block discovery for older Word files, parallel to `findtext.c` text block discovery.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/finddata.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/findtext.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/findtext.c

This file locates text pieces inside Word document streams and records them as text blocks.

Key routines:
- `bAddTextBlocks(...)` maps character positions and lengths to physical file blocks, accounting for Unicode pieces as two bytes per character.
- `bGet6DocumentText(...)` reads and parses Word 6/7 fast-save CLX data, records property modifiers, and appends text blocks.
- `bGet8DocumentText(...)` reads Word 8/97+ CLX data from the table stream, choosing the small or big block depot based on table stream size.

Important behavior:
- Word 8 piece offsets use bit 30 to distinguish Unicode vs compressed single-byte text; compressed offsets are cleared and divided by two.
- Type-1 CLX records are passed to `vAdd2PropModList`; type-2 records produce piece-table entries.
- Damaged BBD indexes in `bAddTextBlocks` produce a warning/error via `werr`.

Dependencies:
- OLE block-chain readers, piece table endian helpers, text block list insertion, property modifier list handling, and Word document/table PPS metadata.

Role in antiword:
- Central bridge from Word piece-table metadata to ordered text extraction.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/findtext.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/fmt_text.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/fmt_text.c

This file implements antiword’s formatted-text output mode.

Key routines:
- `vPrologueFMT(...)` initializes formatted-text output state and diagram coordinates.
- `vPrintFMT(...)` emits a string, preserving leading/trailing spaces while wrapping non-space content in simple markers for bold (`*`), italic (`/`), and underline (`_`).
- `vMoveTo(...)` emits filler characters to simulate horizontal positioning when the vertical position changes.
- `vSubstringFMT(...)` outputs a substring and advances the diagram x-position by the supplied rendered width.

Important behavior:
- UTF-8 output bypasses style-marker insertion and writes bytes directly.
- Non-breaking spaces are converted to ordinary spaces for non-UTF-8 formatted text.
- Style markers are only applied around the non-space core, so surrounding whitespace remains unstyled.

Dependencies:
- Font style predicates, encoding options, draw-unit-to-character conversion, and diagram output state from `antiword.h`.

Role in antiword:
- Provides a lightweight markup-like text rendering backend distinct from plain text, PostScript/PDF, XML, and draw output.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/fmt_text.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/fontinfo.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/fontinfo.h

This is an automatically generated font metrics header used by the Unix font backend.

Contents:
- `szFontnames[32]`: PostScript-compatible font names, including Courier, Times, Helvetica, Palatino, Helvetica-Narrow, Bookman, AvantGarde, and NewCenturySchlbk variants.
- `ausCharacterWidths1[32][256]`: 256-entry character width tables for each font, used for Latin-1 style width computation.
- `ausCharacterWidths2[32][256]`: parallel 256-entry width tables for Latin-2.
- Disabled `aiUnderlineInfo[32][2]` under `#if 0`, noted as unused until needed.

Important behavior:
- No functions are defined; this is static data included by `fonts_u.c`.
- Width values are in relative font units and are scaled by `lComputeStringWidth`.
- Many control-code slots are zero, while printable ranges and extended character positions carry per-font metrics.

Dependencies:
- Included directly by Unix font handling; array sizes are assumed by `fonts_u.c`.

Role in antiword:
- Enables deterministic text width calculation without querying a platform font system.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/fontinfo.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/fontlist.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/fontlist.c

This file stores extracted Word font runs in a linked list.

Key routines:
- `vDestroyFontInfoList()` frees all font run records and resets list state.
- `vCorrectFontValues(...)` normalizes font size/style: small caps become smaller capitals, superscript/subscript shrink size, size is clamped, and white text is remapped to light gray.
- `vAdd2FontInfoList(...)` appends a font block unless the offset is invalid; consecutive records at the same offset collapse to the last one.
- `pGetNextFontInfoListItem(...)` iterates records by recovering the containing list node from the embedded `font_block_type`.

Important behavior:
- Uses `FC_INVALID` to suppress impossible/past-end offsets.
- Maintains append order through `pAnchor` and `pFontLast`.
- Iterator exposes only `font_block_type`, hiding storage internals.

Dependencies:
- Font-style bit helpers, min/max/default font size constants, allocation helpers, and `offsetof`.

Role in antiword:
- Captures font transitions used later by layout, font-table minimization, and rendering.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/fontlist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/fonts.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/fonts.c

This file implements generic font translation table construction and lookup across Word versions.

Key routines:
- Lookup/accessors: `iGetFontByNumber`, `szGetOurFontname`, `iFontname2Fontnumber`, `pGetNextFontTableRecord`, `tGetFontTableLength`.
- Matching/defaulting: `szGetDefaultFont`, `bFontEqual`, `vFontname2Table`.
- Table lifecycle: `vCreateFontTable`, `vMinimizeFontTable`, `vDestroyFontTable`.
- Font table readers: `vCreate0FontTable`, `vCreate2FontTable`, `vCreate6FontTable`, `vCreate8FontTable`.
- Output corrections: `vCorrectFontTable`, with PDF default-font restriction and Cyrillic PostScript monospaced fallback.
- Metrics helper: `lComputeSpaceWidth`.

Important behavior:
- Internal table has four style entries per Word font: regular, bold, italic, bold+italic.
- Reads the external font translation file line-by-line as `Word font, italic, bold, local font, special`.
- Word 8/97+ font tables are read from the table stream using SBD or BBD depending on stream size.
- `vMinimizeFontTable` keeps only fonts used by font runs or potentially used by styles, and ensures the table font exists.

Dependencies:
- Font-info list, style-info list, stylesheet font filling, OLE stream readers, Unicode copy helpers, font table file opener, and platform-specific width/open-font backends.

Role in antiword:
- Converts Word font identifiers and names into antiword/local output font names, then trims and corrects that table for output format constraints.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/fonts.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/fonts_r.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/fonts_r.c

This file is the RISC OS font backend.

Key routines:
- `pOpenFontTableFile()` opens `<AntiWord$FontNamesFile>` or creates it from bundled defaults using RISC OS environment paths.
- `vCloseFont()` releases the current RISC OS font handle.
- `tOpenFont(...)` maps Word font/style to antiword’s font table, opens the RISC OS font via `Font_FindFont`, and returns a drawfile font reference.
- `tOpenTableFont(...)` opens the configured table font.
- `lComputeStringWidth(...)` uses `Font_StringWidth` when a font is active, otherwise falls back to character-count width.
- `tCountColumns(...)` and `tGetCharacterLength(...)` are one-byte/one-column implementations.

Important behavior:
- Stores one global current font handle, initialized to invalid.
- Font open failures return font reference zero and may report RISC OS error details.
- Control table separator has zero width to avoid font subsystem issues.

Dependencies:
- DeskLib/RISC OS `Font` API, drawfile types, filetype/directory helpers, generic font table functions.

Role in antiword:
- Provides native RISC OS font opening and measurement for drawfile-oriented rendering.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/fonts_r.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/fonts_u.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/fonts_u.c

This file is the Unix/DOS/NLM font backend.

Key routines:
- `pOpenFontTableFile()` searches for `fontnames` under `ANTIWORDHOME`, the user home antiword directory, then the global antiword directory.
- `vCloseFont()` resets encoding/font-use state.
- `tOpenFont(...)` decides whether fonts matter for the current conversion type, then maps a Word font/style to an index in `fontinfo.h`.
- `tOpenTableFont(...)` resolves and opens the table font.
- `szGetFontname(...)` returns a PostScript font name by font reference.
- `lComputeStringWidth(...)` computes widths using UTF-8 display width, plain character counts, Cyrillic approximation, or generated Latin-1/Latin-2 metric tables.
- `tCountColumns(...)` and `tGetCharacterLength(...)` use UTF-8 helpers only when UTF-8 encoding is active.

Important behavior:
- Plain text modes avoid font metrics and use character-count widths.
- Draw, PostScript, and PDF modes use font references and generated width tables.
- Cyrillic width support is approximate pending character tables.

Dependencies:
- `fontinfo.h`, option handling, path helpers, UTF-8 helpers, font translation table functions.

Role in antiword:
- Provides portable non-RISC OS font lookup and width measurement for layout and PostScript/PDF output.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/fonts_u.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/hdrftrlist.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/hdrftrlist.c

This file builds and prepares per-section Word header/footer records.

Key routines:
- `vDestroyHdrFtrInfoList()` frees generated header/footer text only where the record owns the text.
- `vCreat8HdrFtrInfoList(...)` maps Word 8+ character position arrays into six header/footer slots per section.
- `vCreat6HdrFtrInfoList(...)` maps Word 6/7 header/footer positions using DOP/SEP specification bits.
- `vCreat2HdrFtrInfoList(...)` delegates to the Word 6/7 creator.
- `pGetHdrFtrInfo(...)` returns the appropriate header/footer record for section, header/footer kind, odd/even page, and first-page status.
- `vPrepareHdrFtrText(...)` extracts header/footer text, computes rendered height, marks usefulness, and applies inheritance.

Important behavior:
- Six slots are tracked: even header, odd header, even footer, odd footer, first-page header, first-page footer.
- Inheritance fills missing odd/even records from first-page records in the first section, and from previous sections thereafter.
- `bTextOriginal` prevents double-free when inherited records share text pointers.

Dependencies:
- Section metadata, DOP/SEP header/footer flags, header/footer decryptor, output linked lists, font leading and unit conversion helpers.

Role in antiword:
- Supplies resolved header/footer content and height for page layout.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/hdrftrlist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/icons.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/icons.c

This file contains RISC OS Wimp icon update helpers.

Key routines:
- `vUpdateIcon(...)` redraws a window icon over update rectangles.
- `vUpdateRadioButton(...)` toggles selected state and redraws only if the requested state differs.
- `vUpdateWriteable(...)` updates indirected text in a writable icon and moves the caret to the end if needed.
- `vUpdateWriteableNumber(...)` formats an integer and delegates to `vUpdateWriteable`.

Important behavior:
- Requires writable icons to be indirected text.
- Uses `Error_CheckFatal` around Wimp calls.
- Maintains caret position for active edited icons.

Dependencies:
- DeskLib Wimp APIs and antiword error/debug helpers.

Role in antiword:
- Supports the RISC OS GUI choices and controls.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/icons.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/imgexam.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/imgexam.c

This file examines embedded Word image records and derives image metadata.

Key routines:
- DIB/BMP: `bFillPaletteDIB`, `bExamineDIB`.
- JPEG: `iNextMarker`, `bExamineJPEG`.
- PNG: `bFillPalettePNG`, `bExaminePNG`.
- WMF stub: `bExamineWMF`, currently always returns `FALSE`.
- Scaling: `vImage2Papersize` for non-RISC OS builds.
- Word wrappers: `tFind6Image`, `tFind8Image`, and public `eExamineImage`.

Important behavior:
- Supports full metadata for DIB, baseline/extended sequential JPEG, and non-interlaced PNG without alpha.
- Rejects unsupported JPEG modes, unsupported PNG bit/component combinations, invalid BMP compression/bit-depth combinations, and impossible image dimensions.
- Word 8 image search parses Office drawing record types and recognizes EMF, WMF, PICT, JPEG, PNG, and DIB instances.
- Vector/external images can still return minimal information.
- Image dimensions are scaled from Word twips/scaling factors and capped to page bounds for non-RISC OS output.

Dependencies:
- Binary stream readers, PNG chunk constants, image data structures, options/page sizing, and image type enums.

Role in antiword:
- Decides whether an embedded image can be translated fully or represented as a placeholder.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/imgexam.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/imgtrans.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/imgtrans.c

This file dispatches image translation based on image metadata.

Key routine:
- `bTranslateImage(...)` validates the diagram/file/image state, checks image options, and dispatches to `bTranslateDIB`, `bTranslateJPEG`, `bTranslatePNG`, or `bAddDummyImage`.

Important behavior:
- Minimal-information images always become dummy placeholders.
- PNG translation is disabled for `level_ps_2` and becomes a dummy image.
- EMF, WMF, PICT, external, and unknown images currently become dummy placeholders.

Dependencies:
- Image examination output, conversion options, DIB/JPEG/PNG translators, dummy image renderer.

Role in antiword:
- Central image conversion router between image metadata and output-specific image rendering.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/imgtrans.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/jpeg2eps.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/jpeg2eps.c

This file translates JPEG image data into EPS/PostScript output.

Key routine:
- `bTranslateJPEG(...)` seeks to the embedded JPEG data, emits an image prologue, ASCII85-encodes the JPEG bytes into the output file, then emits an image epilogue.

Debug behavior:
- Under `DEBUG`, `vCopy2File(...)` can dump the embedded JPEG to `/tmp/pic/picNNNN.jpg`.

Dependencies:
- Data offset seeking, image prologue/epilogue emission, ASCII85 file encoder, diagram output file state.

Role in antiword:
- Provides the non-RISC OS PostScript/PDF-style JPEG embedding path.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/jpeg2eps.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/jpeg2sprt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/jpeg2sprt.c

This file translates JPEG images for RISC OS draw/sprite output.

Key routines:
- `bSave2Draw(...)` reads the JPEG bytes into memory and inserts them into the draw diagram with `vImage2Diagram`.
- `bTranslateJPEG(...)` seeks to the JPEG data and either embeds it directly for RISC OS 3.6+ or emits a dummy image for older systems.

Important behavior:
- JPEG support is gated on `iGetRiscOsVersion() >= 360`.
- A disabled debug helper can write JPEGs to the Wimp scrap directory and set filetype.

Dependencies:
- RISC OS version helper, data offset seeking, allocation helpers, diagram image insertion, dummy image renderer.

Role in antiword:
- Provides the RISC OS-specific JPEG image path.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/jpeg2sprt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/listlist.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/listlist.c

This file stores Word list/numbering definitions and tracks current list numbering values.

Key routines:
- `vDestroyListInfoList()` frees LFO entries, list description records, and active numbering values.
- `vBuildLfoList(...)` extracts list IDs from the Word 8+ LFO list.
- `vAdd2ListInfoList(...)` appends a list-level definition and clamps invalid starts.
- `pGetListInfo(...)` resolves a list block by list index and level, falling back to level 0.
- `pGetListInfoByIstd(...)` resolves list info by style id.
- `vRestartListValues(...)` clears less-significant list levels.
- `usGetListValue(...)` increments or initializes numbering for old and new Word list models.

Important behavior:
- Word 8+ numbering uses `usListIndex`, `ucListLevel`, LFO IDs, and per-level value records.
- Word versions before 8 use a simpler sequence counter with pause/start behavior.
- Restart behavior deletes deeper list-level counters unless `bNoRestart` is set.

Dependencies:
- Style blocks, numbering type helpers, Word list constants, allocation helpers.

Role in antiword:
- Provides numbering state for list paragraph rendering.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/listlist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/main_ros.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/main_ros.c

This file is the RISC OS GUI entry point for `!Antiword`.

Key routines:
- GUI/menu handlers: `bBarInfo`, `vBarInfoSetText`, `bMouseButtonClick`, `bAutoRedrawWindow`, `bSaveSelect`, `bMenuSelect`, `bMenuClick`.
- Window setup: `pCreateTextWindow(...)`, `vTemplates()`, `vInitialise()`.
- File processing: `vProcessFile(...)` opens a file, identifies Word version, optionally sets filetype, creates a diagram, runs `bWordDecryptor`, verifies drawfile data, and shows the diagram.
- Messaging: `vSendAck(...)`, `bEventMsgHandler(...)`.
- `main(...)` initializes the GUI, reads options, optionally opens one file, then enters the event loop.

Important behavior:
- Handles RISC OS DataLoad/DataOpen messages and Closedown.
- Creates per-document save menus for scale view, drawfile save, and text-only save.
- Uses DeskLib event claims and RISC OS templates/resources.

Dependencies:
- DeskLib Dialog/Event/Menu/Template/Window APIs, drawfile verifier, filetype helpers, option reader, Word detector/decryptor, diagram/window helpers.

Role in antiword:
- RISC OS application shell around the shared Word decoding/rendering core.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/main_ros.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/main_u.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/main_u.c

This file is the Unix/DOS/NLM command-line entry point for `antiword`.

Key routines:
- `vUsage()` prints program metadata and supported switches.
- `pStdin2TmpFile(...)` copies standard input into a temporary seekable file.
- `bProcessFile(...)` opens a file or stdin, gets size, detects Word version, rejects RTF/WordPerfect/non-Word inputs, creates a diagram, runs `bWordDecryptor`, destroys the diagram, and reports success.
- `main(...)` parses options, configures locale, emits XML prologue/set wrappers when needed, processes all input files, and returns success only if at least one file succeeded.

Important behavior:
- `-` means read Word data from stdin.
- Multiple text outputs get filename separator banners.
- XML output emits a DocBook doctype and wraps multiple documents in `<set>`.
- UTF-8 locale is set only when the platform/environment and requested encoding support it.
- DOS mode switches stdin/stdout binary mode where needed.

Dependencies:
- Option parsing, basename/path helpers, locale helpers, Word detector/decryptor, diagram lifecycle, conversion options.

Role in antiword:
- Portable CLI wrapper around the shared Word decoding/rendering core.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/main_u.c -->