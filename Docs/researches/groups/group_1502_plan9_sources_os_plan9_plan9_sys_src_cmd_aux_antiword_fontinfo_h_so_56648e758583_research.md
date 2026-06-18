# Group Research: group_1502_plan9_sources_os_plan9_plan9_sys_src_cmd_aux_antiword_fontinfo_h_so_56648e758583

This group covers Antiword support code in the Plan 9 source tree under `sys/src/cmd/aux/antiword`. The files are not filesystem code; they are document conversion support modules for font mapping/metrics, header/footer/list state, image recognition/translation, and Unix/RISC OS entry points.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/fontinfo.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/fontinfo.h

Automatically generated static font metric data; the file explicitly says not to edit it.

Defines:

- `szFontnames[32]`: PostScript/PDF base font names and variants such as Courier, Times, Helvetica, Palatino, Helvetica-Narrow, Bookman, AvantGarde, and NewCenturySchlbk.
- `ausCharacterWidths1[32][256]`: per-font width table, mainly used for Latin-1 style output.
- `ausCharacterWidths2[32][256]`: second per-font width table, used by the Unix font path for Latin-2 output.
- Disabled `aiUnderlineInfo[32][2]` under `#if 0`.

The width tables store 1000-em relative character widths indexed by byte value. `fonts_u.c` consumes these arrays to calculate rendered string widths for PS/PDF/draw style output, scaling by Antiword font size in half-points. The generated data is pure lookup state, with no control flow or allocation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/fontinfo.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/fontlist.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/fontlist.c

Maintains an ordered linked list of Word font-change records.

Key structure:

- private `font_mem_type`, wrapping `font_block_type tInfo` plus `pNext`.

Key functions:

- `vDestroyFontInfoList()` frees the linked list and resets anchors.
- `vCorrectFontValues()` normalizes font records:
  - small caps become capitals at 4/5 size,
  - super/subscript become 2/3 size,
  - size is clamped to `MIN_FONT_SIZE..MAX_FONT_SIZE`,
  - Word white color `8` becomes light gray `16`.
- `vAdd2FontInfoList()` skips invalid offsets, replaces a consecutive record with the same file offset, normalizes values, and appends.
- `pGetNextFontInfoListItem()` exposes iteration over `font_block_type` while hiding the list node layout via `offsetof`.

This file is shared state for later output layout and font table pruning. It depends on `antiword.h` memory helpers like `xmalloc`, `xfree`, and `fail`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/fontlist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/fonts.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/fonts.c

Generic font translation logic. It maps Word font numbers/styles to Antiword output font names, then prunes unused entries.

Core state:

- `tFontTableRecords`
- `pFontTable`, an array of `font_table_type`

Main responsibilities:

- Lookup:
  - `iGetFontByNumber()`
  - `szGetOurFontname()`
  - `iFontname2Fontnumber()`
  - `pGetNextFontTableRecord()`
  - `tGetFontTableLength()`
- Default selection:
  - `szGetDefaultFont()` maps Word pitch/family/emphasis to serif, sans-serif, or monospaced defaults.
- Translation-table parsing:
  - `bReadFontFile()` reads CSV-style font mapping records from the platform-specific fontnames file.
  - `bFontEqual()` compares Word font names case-insensitively, handling one-byte and two-byte Unicode-style strings.
  - `vFontname2Table()` writes matching Word/local font mappings into a `font_table_type`.
- Table creation:
  - `vCreate0FontTable()` handles Word for DOS with synthetic Courier/Times mapping.
  - `vCreate2FontTable()` handles WinWord 1/2 font tables, including three implicit fonts for Word 1.
  - `vCreate6FontTable()` parses Word 6/7 FFN records and optional alternate names.
  - `vCreate8FontTable()` parses Word 8/9/10 Unicode FFN records from OLE streams.
- Cleanup and correction:
  - `vMinimizeFontTable()` marks fonts actually used by font records and stylesheet-derived fonts, compacts unused entries, and ensures `TABLE_FONT` exists.
  - `vDestroyFontTable()` frees the table.
  - `vCorrectFontTable()` restricts PDF output to built-in PDF fonts and maps Cyrillic PS to monospaced fonts.
  - `lComputeSpaceWidth()` delegates to platform-specific string-width logic.

The file is central to output fidelity. It interacts with property parsers, stylesheet lists, font lists, OLE stream reading, output encodings, and platform-specific font opening in `fonts_u.c`/`fonts_r.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/fonts.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/fonts_r.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/fonts_r.c

RISC OS-specific font implementation.

Key behavior:

- `pOpenFontTableFile()` opens `<AntiWord$FontNamesFile>` or creates it by copying `<AntiWord$Dir>.Resources.Default` into the configured save location.
- `vCloseFont()` releases the current RISC OS font handle using `Font_LoseFont`.
- `tOpenFont()` maps Word font/style through the generic font table, then opens a RISC OS font with `Font_FindFont`; returns a drawfile font reference of `iFontnumber + 1`.
- `tOpenTableFont()` resolves `TABLE_FONT` and opens it.
- `lComputeStringWidth()` uses RISC OS `Font_StringWidth`; if no font is open or an error occurs, falls back to character-count millipoints.
- `tCountColumns()` and `tGetCharacterLength()` are one-byte assumptions for this platform.

This file owns live RISC OS font handles and uses DeskLib/RISC OS APIs. It is the platform counterpart to `fonts_u.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/fonts_r.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/fonts_u.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/fonts_u.c

Unix font implementation, including Plan 9 build paths via `antiword.h` platform macros.

Key state:

- `bUsePlainText`: true for plain text/XML-like output where font metrics are unnecessary.
- `eEncoding`: current output encoding.

Key functions:

- `pOpenFontTableFile()` searches for `fontnames` in:
  - `ANTIWORDHOME`,
  - user home `.antiword`,
  - `GLOBAL_ANTIWORD_DIR`.
- `vCloseFont()` resets encoding and plain-text mode.
- `tOpenFont()` chooses whether metrics are needed based on conversion type; for PS/PDF/draw it maps Word font/style to one of the 32 generated PostScript font names in `fontinfo.h`.
- `tOpenTableFont()` opens the configured table font.
- `szGetFontname()` returns the generated PostScript font name for a font reference.
- `lComputeStringWidth()`:
  - UTF-8 plain text uses `utf8_strwidth`,
  - plain text uses byte count,
  - Cyrillic uses fixed 600-unit width,
  - Latin-1 uses `ausCharacterWidths1`,
  - Latin-2 uses `ausCharacterWidths2`.
- `tCountColumns()` and `tGetCharacterLength()` switch between byte semantics and UTF-8 helpers.

This is the primary consumer of `fontinfo.h` and the Unix-side bridge between Word font metadata and output positioning.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/fonts_u.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/hdrftrlist.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/hdrftrlist.c

Builds and owns per-section header/footer metadata.

Data model:

- Each section has six slots:
  - even header,
  - odd header,
  - even footer,
  - odd footer,
  - first-page header,
  - first-page footer.
- Private `hdrftr_local_type` stores exported `hdrftr_block_type`, character-position range, usefulness flag, and ownership flag for text lists.

Key functions:

- `vDestroyHdrFtrInfoList()` frees only original header/footer output chains, avoiding double-free when entries inherit text from another slot/section.
- `vCreat8HdrFtrInfoList()` builds section records from Word 8+ character position arrays.
- `vCreat6HdrFtrInfoList()` builds Word 6/7 records using DOP/SEP header-footer specification bits.
- `vCreat2HdrFtrInfoList()` reuses the Word 6 path.
- `pGetHdrFtrInfo()` selects the correct slot for section, header/footer, odd/even page, and first-page state.
- `lComputeHdrFtrHeight()` estimates vertical height by scanning output tokens and paragraph/line terminators.
- `vPrepareHdrFtrText()` decrypts header/footer text ranges, computes heights, marks useful records, and applies inheritance from first-page records and previous sections.

This module links file-position parsing to page-layout output. It relies on document property accessors and `pHdrFtrDecryptor()`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/hdrftrlist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/icons.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/icons.c

Small RISC OS GUI utility module for updating WIMP icons.

Functions:

- `vUpdateIcon()` redraws an icon through `Wimp_UpdateWindow`, `Wimp_PlotIcon`, and `Wimp_GetRectangle`.
- `vUpdateRadioButton()` checks current selected state and toggles the RISC OS selected flag if needed.
- `vUpdateWriteable()` writes a string into an indirected text icon, keeps the caret at the end when focused, and redraws.
- `vUpdateWriteableNumber()` formats an integer and delegates to `vUpdateWriteable()`.

The file is GUI-only and does not participate in document parsing. It depends on DeskLib WIMP APIs and Antiword error helpers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/icons.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/imgexam.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/imgexam.c

Examines embedded Word image containers and image headers. It identifies image type, validates basic dimensions/format constraints, and fills `imagedata_type`.

Supported recognition:

- DIB/BMP headers with uncompressed, RLE4, and RLE8 variants.
- Baseline/extended sequential JPEG usable for PostScript Level 2.
- PNG with non-interlaced zlib compression, no unsupported alpha/component forms.
- WMF stub examination exists but currently returns false.
- Word 6/7 image records.
- Word 8/9/10 OfficeArt records.

Important functions:

- `bExamineDIB()` parses DIB headers, validates planes, size, bit depth, compression, palette, component count.
- `bExamineJPEG()` walks JPEG markers, rejects unsupported SOF types, records Adobe APP14, dimensions, component count, and compression.
- `bExaminePNG()` validates PNG signature/chunks, extracts IHDR/PLTE, rejects unsupported interlace/filter/compression/alpha/component combinations, and creates default grayscale palette when needed.
- `tFind6Image()` locates Word 6/7 embedded DIB records.
- `tFind8Image()` scans OfficeArt records and identifies EMF, WMF, PICT, JPEG, PNG, and DIB payload starts.
- `vImage2Papersize()` scales oversized images to fit configured page size for non-RISC OS builds.
- `eExamineImage()` is the public entry point: reads the Word image wrapper, computes scaled physical size, dispatches image-specific examination, and returns no/minimal/full information.

The module is defensive: many malformed or unsupported cases degrade to minimal image information rather than attempting full translation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/imgexam.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/imgtrans.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/imgtrans.c

Generic image translation dispatcher.

Single public function:

- `bTranslateImage(diagram_type *pDiag, FILE *pFile, BOOL bMinimalInformation, ULONG ulFileOffsetImage, const imagedata_type *pImg)`

Behavior:

- If only minimal image information is available, adds a dummy image.
- DIB dispatches to `bTranslateDIB()`.
- JPEG dispatches to `bTranslateJPEG()`.
- PNG dispatches to `bTranslatePNG()` unless output image level is PS level 2, where it uses a dummy placeholder.
- EMF, WMF, PICT, external, unknown image types currently become dummy placeholders.

This file sits between `imgexam.c` and format-specific translators such as `dib2eps.c`, `jpeg2eps.c`, `png2eps.c`, or RISC OS sprite translators.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/imgtrans.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/jpeg2eps.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/jpeg2eps.c

PostScript/PDF-side JPEG translator.

Key function:

- `bTranslateJPEG()` seeks to the JPEG payload, emits image prologue, ASCII85-encodes the JPEG bytes to the output file, then emits image epilogue.

Debug-only helper:

- `vCopy2File()` can dump embedded JPEGs into `/tmp/pic/picNNNN.jpg` when compiled with `DEBUG`.

The module does not decode JPEG pixels; it wraps already-validated JPEG data for EPS-style output. Actual prologue/epilogue behavior is delegated through generic output functions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/jpeg2eps.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/jpeg2sprt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/jpeg2sprt.c

RISC OS Draw/sprite-side JPEG translator.

Key functions:

- `bSave2Draw()` reads the JPEG payload into memory and embeds it in a Draw diagram via `vImage2Diagram()`.
- `bTranslateJPEG()` seeks to JPEG data and, on RISC OS 3.6 or later, saves the JPEG into the Draw file; older systems fall back to a dummy image.

Debug-only code can dump JPEGs to the RISC OS scrap directory, but it is disabled with `#if 0`.

Unlike `jpeg2eps.c`, this path embeds the raw JPEG in a Draw diagram rather than ASCII85-encoding it.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/jpeg2sprt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/listlist.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/listlist.c

Stores Word list definitions and tracks current numbering values.

Private structures:

- `list_desc_type`: list definition record with `list_block_type`, Word list ID, style ID, level, and next pointer.
- `list_value_type`: current numbering state for a list index and level.

Core state:

- `aulLfoList` / `usLfoLen`: Word 8+ LFO list ID mapping.
- `pAnchor` / `pBlockLast`: list definition linked list.
- `pValues`: active numbering values.
- `iOldListSeqNumber` / `usOldListValue`: legacy pre-Word-8 numbering state.

Key functions:

- `vDestroyListInfoList()` frees all list definition/state memory and resets counters.
- `vBuildLfoList()` parses the `pllfo` buffer into list IDs with sanity checks.
- `vAdd2ListInfoList()` appends list metadata and clamps invalid huge `ulStartAt` to `1`.
- `pGetListInfo()` maps list index and level to a `list_block_type`, with level-0 fallback.
- `pGetListInfoByIstd()` retrieves list metadata by style ID.
- `vRestartListValues()` deletes less-significant level counters after a higher-level increment when restart rules require it.
- `usGetListValue()` advances numbering for old and new list formats.

This module directly affects generated list numbers and indentation behavior during `word2text.c` output.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/listlist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/main_ros.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/main_ros.c

RISC OS GUI entry point for `!Antiword`.

Responsibilities:

- Initializes DeskLib resources, event system, templates, choices window, iconbar icon, and menus.
- Creates per-document diagrams/windows via `pCreateTextWindow()`.
- Processes a Word file in `vProcessFile()`:
  - opens file,
  - gets size,
  - guesses Word version,
  - rejects RTF/WordPerfect/non-Word cases,
  - optionally sets RISC OS filetype,
  - creates diagram,
  - calls `bWordDecryptor()`,
  - verifies Drawfile diagram,
  - displays it.
- Handles iconbar menu actions, save menu selections, scale view, save drawfile, save text.
- Handles RISC OS `DATALOAD` / `DATAOPEN` messages and sends `DATALOADACK`.
- Enters infinite `Event_Poll()` loop after initialization and optional command-line file processing.

This file is platform orchestration only; all Word parsing and conversion are delegated to shared Antiword modules.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/main_ros.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/main_u.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/main_u.c

Unix command-line entry point for `antiword`.

Responsibilities:

- Prints usage and version/help text.
- Parses command-line options with `iReadOptions()`.
- Supports `-` as stdin by copying stdin to `tmpfile()` in `pStdin2TmpFile()`.
- Processes each input in `bProcessFile()`:
  - opens file/stdin temp,
  - gets size,
  - guesses Word version,
  - rejects RTF/WordPerfect/non-Word,
  - creates output diagram,
  - runs `bWordDecryptor()`,
  - destroys diagram and closes file.
- Handles locale setup:
  - UTF-8 output may set `LC_CTYPE` from environment when supported,
  - otherwise falls back to normal locale or `C`.
- Handles multi-file text output by printing filename separators.
- Handles XML output by writing a DocBook prologue and optional `<set>` wrapper.
- On DOS builds, switches stdout to binary for PDF output and stdin to binary while copying.

Exit status is success only if at least one file was successfully processed. This is the normal non-GUI entry point in Unix-like builds, including the Plan 9-oriented source tree variant.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/main_u.c -->