# Group Research: group_63_9front_sources_os_plan9_9front_sys_src_cmd_aux_antiword_prop8_c_sourc_0c1c63129923

Scope: `Docs/research_subset_a.md`, specifically `sources/os/plan9/9front/sys/src/cmd/aux/antiword`. I read all 25 listed files completely. The supplied internal group report path was not present in the workspace, so this grouped report is based on the source files themselves.

This group covers Antiword’s Word document detection, OLE storage setup, Word 8 property parsing, stylesheet/list/font/row/section metadata storage, summary metadata extraction, plain text rendering, platform wrappers, shared Word constants/types, and allocation helpers.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/prop8.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/prop8.c

Word 8/9/10/11 property parser for Word 97 through Word 2003 binary documents.

Key responsibilities:
- Decodes Word 8 SPRM/property record lengths with `iGet8InfoLength()`.
- Reads table-stream data from either the big block depot or small block depot.
- Extracts DOP document properties: header/footer flags, default tab width, creation and revision dates.
- Parses section PLCF/SEPX data, page-break behavior, header/footer specifications, outline numbering descriptors, and header/footer character positions.
- Parses Word 8 list structures (`LFO`, `LSTF`, `LVLF`) into Antiword list records.
- Parses paragraph FKPs into style records and table row records.
- Parses character FKPs into font records and picture references.

Important behavior:
- `vGet8LstInfo()` runs before paragraph/style parsing so list references can be resolved while interpreting paragraph SPRMs.
- `vGet8PapInfo()` combines stylesheet defaults with paragraph-specific SPRMs, maps character positions to file offsets/list IDs, and records table rows.
- `eGet8RowInfo()` detects table cells/end-of-row from `fInTable`, `fTtp`, sub-table flags, borders, and `sprmTDefTable`.
- `vGet8FontInfo()` handles revision deletion, bold/italic/strike/caps/hidden, underline, color, superscript/subscript, font size, font number, and reset/plain operations.
- `bGet8PicInfo()` recognizes `fcPic` references while rejecting OLE objects.

Dependencies:
- OLE PPS/block-depot readers, text/data block mapping, stylesheet/list/font/row/picture/header-footer list APIs, Word character-position conversion helpers.

Notable risks:
- Binary offsets and SPRM lengths must exactly match Word’s file format.
- Several unsupported or diagnostic-only SPRMs are logged rather than fully interpreted.
- Table/list parsing has explicit corruption guards, but still relies heavily on well-formed FKP/page structures.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/prop8.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/properties.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/properties.c

Central dispatcher for building document property lists across supported Word versions.

Key responsibilities:
- `vGetPropertyInfo()` selects the correct parser set for Word for DOS, WinWord 1/2, Word 6/7, and Word 8.
- Builds stylesheet, DOP, section, paragraph, header/footer, character, font table, list, and summary metadata as needed.
- Avoids expensive character/font/image parsing for output modes that do not need it.
- Calls `vCorrectFontTable()` after parsing to normalize font mappings for the chosen conversion and encoding.
- `ePropMod2RowInfo()` translates a stored property modifier into table row/cell information for Word 2, 6/7, or 8.

Dependencies:
- Version-specific property parsers (`prop0`, `prop2`, `prop6`, `prop8`), summary readers, font table builders, option state, and property modifier storage.

Research relevance:
- This is the conversion pipeline’s property ingestion coordinator.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/properties.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/propmod.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/propmod.c

Stores and retrieves Word property modifier byte sequences.

Key routines:
- `vDestroyPropModList()` frees all stored modifier records and resets static list state.
- `vAdd2PropModList()` appends a length-prefixed property modifier buffer, growing the backing array in batches.
- `aucReadPropModListItem()` resolves a `usPropMod` value either as an inline two-byte modifier or as an index into the stored list.

Important behavior:
- `IGNORE_PROPMOD` returns `NULL`.
- Even `usPropMod` values encode modifier data directly.
- Odd `usPropMod` values are treated as list indexes shifted right by one.

Dependencies:
- Shared little-endian helpers and fail-fast allocation wrappers.

Research relevance:
- Supports fast-saved or compressed text runs where paragraph property modifiers are referenced indirectly.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/propmod.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/riscos.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/riscos.c

RISC OS platform support layer.

Key responsibilities:
- Implements `werr()` using DeskLib error reporting.
- Gets and sets RISC OS filetypes through `OS_File`.
- Creates missing output directories for RISC OS path syntax.
- Reads the current alphabet number and RISC OS version through SWIs.
- In debug builds, queries JPEG metadata through `JPEG_Info`.

Important behavior:
- Fatal `werr()` exits; nonfatal calls only report warnings.
- `vSetFiletype()` silently tolerates common read-only media errors.
- `bMakeDirectory()` treats the part before the last dot as the directory name.

Dependencies:
- DeskLib `Error`, `SWI`, RISC OS SWIs, Antiword shared constants.

Research relevance:
- Isolates RISC OS-specific system integration from the portable document parser.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/riscos.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/rowlist.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/rowlist.c

Linked-list storage for parsed Word table row metadata.

Key routines:
- `vDestroyRowInfoList()` frees the row list and resets iteration state.
- `vAdd2RowInfoList()` appends valid row blocks and clamps negative column widths to zero.
- `pGetNextRowInfoListItem()` returns rows sequentially during rendering.

Important behavior:
- Rows with invalid or identical start/end file offsets are ignored.
- The read cursor is initialized when the first row is added and advances monotonically.

Dependencies:
- `row_block_type`, `xmalloc`, `xfree`, table constants.

Research relevance:
- Bridges binary table-property parsing and table-aware rendering in `word2text.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/rowlist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/saveas.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/saveas.c

RISC OS GUI “Save as” handlers for text and Draw output.

Key responsibilities:
- Creates and initializes the `xfer_send` save window.
- Saves Draw diagram text objects as a plain text file.
- Saves Draw diagram objects as a Draw file after translating Y coordinates from top-left to bottom-left origin.
- Handles menu and keyboard events for text or Draw saves.
- Sets output filetypes after successful saves and removes partial files on failure.

Important behavior:
- Text export reconstructs line breaks from text object bounding boxes and indentation from X positions.
- Draw export adjusts bounding boxes, text baselines, path coordinates, sprites, and JPEG transforms.
- Unknown Draw object types abort the save.

Dependencies:
- DeskLib menu/save/template/window APIs, Drawfile structures, RISC OS filetype helpers.

Research relevance:
- GUI/export adapter for RISC OS Antiword; not part of Word parsing itself.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/saveas.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/sectlist.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/sectlist.c

Linked-list storage for Word section metadata.

Key routines:
- `vDestroySectionInfoList()` frees stored section records.
- `vAdd2SectionInfoList()` appends a section record and its character position.
- `vGetDefaultSection()` initializes default section state with `bNewPage = TRUE`.
- `pGetSectionInfo()` finds section metadata for a character position, falling back to the previous section.
- `tGetNumberOfSections()` and `ucGetSepHdrFtrSpecification()` expose section counts/header-footer flags.

Important behavior:
- If no section records exist, the first lookup creates a default section at character position zero.
- `pGetSectionInfo()` accepts either exact `ulCharPos` or `ulCharPos + 1`, matching Word boundary behavior.

Dependencies:
- `section_block_type`, allocation helpers, parser-generated section lists.

Research relevance:
- Supplies rendering code with page/section transition and header/footer behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/sectlist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/startup.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/startup.c

RISC OS launcher that enforces a single running Antiword task.

Key responsibilities:
- Enumerates running tasks and compares task names case-insensitively.
- Starts `!Antiword` if no existing Antiword task is active.
- If Antiword is already running and an argument is supplied, sends it as a simulated iconbar drag-and-drop `DATALOAD` message.
- Reports an error if Antiword is already running and no file argument is provided.

Dependencies:
- DeskLib event/error/SWI APIs, TaskManager enumeration, Wimp messaging, RISC OS filetype constants.

Research relevance:
- Small platform-specific process coordination wrapper.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/startup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/stylelist.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/stylelist.c

Stores parsed style transitions and normalizes list/indent behavior for rendering.

Key responsibilities:
- Maintains a linked list of `style_block_type` records keyed by file offset/sequence number.
- Converts Word list bullet/private-use characters into UTF-8 or ASCII-compatible output markers.
- Normalizes invalid or excessive indentation and gives headings a minimum vertical gap.
- Tracks whether style records are in sequence and keeps a midpoint pointer for faster lookup.
- Provides sequential style iteration and text-only style iteration that skips header/footer, macro, and annotation lists.
- Maps file offsets back to current `istd` for character font inheritance.
- Determines whether a paragraph style implies list membership.

Dependencies:
- List constants, encoding/conversion options, sequence-number mapping, stylesheet defaults, output bullet helpers.

Notable risks:
- List character conversion contains many heuristic mappings for Symbol/private-use bullets.
- `usGetIstd()` relies on sequence-number ordering for its fast path but has a full scan fallback.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/stylelist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/stylesheet.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/stylesheet.c

Parses Word stylesheet tables into default style and font arrays.

Key responsibilities:
- Stores stylesheet-derived `style_block_type` and `font_block_type` arrays.
- Provides default style/font constructors.
- Maps old WinWord style codes to newer `istd` values.
- Supplies built-in style/font defaults for WinWord 1/2.
- Parses WinWord 1/2 stylesheet records and applies CHPX/PAPX changes.
- Parses Word 6/7 and Word 8 stylesheet `STD`/`UPX` records.
- Resolves base-style dependencies iteratively until no more records can be filled.
- Exposes `vFillStyleFromStylesheet()` and `vFillFontFromStylesheet()` for paragraph/character parsing.

Important behavior:
- Empty or unresolved records are filled with defaults.
- Word 8 style names are Unicode-length based, unlike Word 6/7 byte-length names.
- Paragraph styles can include both paragraph and character UPX data.

Dependencies:
- Version-specific property interpreters (`vGet1FontInfo`, `vGet2FontInfo`, `vGet6StyleInfo`, `vGet8StyleInfo`, etc.), block readers, allocation helpers.

Research relevance:
- Central inheritance/default source for later paragraph and character formatting.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/stylesheet.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/summary.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/summary.c

Extracts document summary metadata and language information.

Key responsibilities:
- Stores title, subject, author, app name, manager, company, creation date, last-save date, and language ID.
- Converts DOS date strings, Word DTTM values via helpers, and OLE FILETIME values.
- Parses OLE SummaryInformation and DocumentSummaryInformation property sets.
- Reads legacy Word for DOS and WinWord 1/2 summary/associated-string fields.
- Maps Word language IDs to locale-like strings.

Important behavior:
- String properties are trimmed at both ends and ignored if empty.
- OLE property streams may live in small or big block depots depending on stream size.
- Word 8 Far East documents may use an alternate language ID header field.
- Getter functions return static formatted date buffers for PDF/XML metadata.

Dependencies:
- OLE PPS stream info, block readers, time conversion helpers, allocation wrappers.

Notable risks:
- OLE property parsing assumes validated offsets after header checks.
- The language mapping is partial and returns `NULL` for unknown IDs.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/summary.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/tabstop.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/tabstop.c

Reads the document default tab width.

Key responsibilities:
- Defaults tab width to half an inch in millipoints.
- Reads `dxaTab` from Word for DOS headers, WinWord 1/2 DOP data, Word 6/7 DOP data, or Word 8 table-stream DOP data.
- Selects small or big block depot for Word 8 table stream reads.
- Dispatches by Word version in `vSetDefaultTabWidth()`.

Important behavior:
- Zero `dxaTab` falls back to half an inch.
- Word 4/5 paths leave the default unchanged.
- `lGetDefaultTabWidth()` is present but compiled out under `#if 0`; another implementation may be supplied elsewhere.

Dependencies:
- DOP offsets in version-specific FIB headers, block readers, twips-to-millipoints conversion.

Research relevance:
- Supplies tab expansion width to the text rendering state machine.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/tabstop.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/text.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/text.c

Plain text output backend.

Key responsibilities:
- Initializes text output state from options and diagram coordinates.
- Emits final newline in the epilogue.
- Writes substrings to the output file and advances horizontal position.
- Converts non-breaking spaces to normal spaces for non-UTF-8 output.
- Emits leading filler spaces based on current X position when moving to a new line.
- Handles paragraph/page boundaries as newline operations.

Important behavior:
- UTF-8 output strings are written byte-for-byte.
- Large before/after paragraph gaps become blank lines.
- This backend keeps formatting intentionally coarse: indentation and line breaks only.

Dependencies:
- Diagram/output abstraction, option encoding, width conversion helpers.

Research relevance:
- Final plain-text rendering endpoint for the parser pipeline.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/text.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/unix.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/unix.c

Unix approximation layer for RISC OS functions.

Key responsibilities:
- Implements `werr()` by printing to `stderr` and optionally exiting.
- Provides no-op `Hourglass_On()` and `Hourglass_Off()` functions for shared rendering code.

Important behavior:
- `iFatal == 0` is warning-only.
- `iFatal == 1` exits with `EXIT_FAILURE`; other fatal values exit with that code.

Research relevance:
- Keeps portable code independent of platform-specific error/progress APIs.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/unix.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/utf8.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/utf8.c

UTF-8 display-width and locale helper code.

Key responsibilities:
- Carries a Markus Kuhn-derived combining-character interval table.
- Determines whether a UCS code point has zero terminal width.
- Computes wcwidth-like display width, including East Asian wide/fullwidth ranges.
- Decodes UTF-8 byte sequences into UCS values.
- Computes UTF-8 string width in columns.
- Returns UTF-8 character byte length.
- Detects whether the normalized locale codeset is UTF-8.

Important behavior:
- Invalid/truncated UTF-8 is not strictly rejected; missing continuation bytes contribute zero bits.
- Control characters produce width `-1`, which callers ignore for total width.
- Width logic supports older Unicode-era ranges used by Antiword 0.37.

Dependencies:
- Character-set normalization helper, shared integer types/constants.

Research relevance:
- Helps text layout keep sensible column counts for UTF-8 output.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/utf8.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/version.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/version.h

Version and product metadata header.

Key definitions:
- `PURPOSESTRING`: “Display MS-Word files”.
- `AUTHORSTRING`: RISC OS copyright-symbol variant or portable `(C)` variant.
- `VERSIONSTRING`: `0.37  (21 Oct 2005)`.
- DOS-specific `VERSIONSTRING2` distinguishes protected-mode and real-mode builds.
- `STATUSSTRING` is either `DEBUG version` or `GNU General Public License`.

Research relevance:
- Provides CLI/info-box metadata for Antiword.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/version.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/word2text.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/word2text.c

Main Word-to-output conversion state machine.

Key responsibilities:
- Initializes a Word document, parses metadata/properties, prepares headers/footers and footnotes, and emits output prologue.
- Reads translated characters from text, footnote, endnote, textbox, and header textbox lists.
- Tracks current section, row/table state, style transitions, font transitions, list state, hidden/deleted text flags, and current image reference.
- Builds linked `output_type` fragments with font/style/width metadata.
- Handles paragraph breaks, page/column breaks, hard returns, tabs, table separators, footnotes/endnotes, images, lists, indentation, and wrapping.
- Frees document-wide parsed structures at the end.

Important behavior:
- `ulGetChar()` is the character ingestion point: it advances text lists, detects row/style/font starts, skips embedded regions, translates Word characters, records pictures, and prepares next-style/font defaults at paragraph ends.
- `bWordDecryptor()` wraps lines, switches output lists after EOF, renders table rows specially, and uses `[pic]` fallback when image translation fails.
- Text-list EOF flows through main text, footnotes, endnotes, text boxes, and header text boxes.
- XML output suppresses some text-only behavior and handles footnote text differently.
- Hidden and revision-deleted text are filtered based on options.

Dependencies:
- Document initialization, property/style/font/row/list/section/picture/note stores, character translation, image translation, output backends, font metrics.

Notable risks:
- This file is highly stateful; correctness depends on parser lists being ordered by file offset/sequence.
- Table rendering relies on both row-list offsets and property-modifier row detection.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/word2text.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/wordconst.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/wordconst.h

Shared constants and macros for Word binary interpretation and rendering.

Key contents:
- Boolean definitions for non-C99 portability.
- OLE/Word block sizes: header, big block, small block, PPS entry, and BBD threshold.
- Table, tab, font size, font style, font color, list type, alignment, and border constants.
- Invalid/sentinel values for character positions, file offsets, style IDs, block chains, and property modifiers.
- Little-endian and big-endian byte extraction macros.
- Font-style and table-border predicate macros.
- Unit conversion macros for twips, millipoints, draw units, points, and character cells.
- Word control-character constants and pseudo-character values for notes.
- Unicode constants used by character translation and output fallback.

Research relevance:
- This is the low-level compatibility contract used across the Antiword parser and renderers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/wordconst.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/worddos.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/worddos.c

Word for DOS document initializer.

Key responsibilities:
- Reads the 128-byte Word for DOS header.
- Verifies the Word for DOS magic/version.
- Rejects autosave/fast-saved Word for DOS documents.
- Creates one text block starting at offset 128 with length from the header.
- Invokes property parsing, default tab width parsing, and notes parsing.

Important behavior:
- Text is treated as non-Unicode.
- Property modifier is set to `IGNORE_PROPMOD`.
- Initialization returns Word version `0` only if text block setup succeeds.

Dependencies:
- Version detection, text block list, property dispatcher, tab-stop parser, notes parser.

Research relevance:
- Legacy Word for DOS entry point into the shared conversion pipeline.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/worddos.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/wordlib.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/wordlib.c

Top-level Word file detection, version detection, initialization dispatch, and cleanup.

Key responsibilities:
- Checks file signatures for Word for DOS, OLE Word, RTF, WordPerfect, WinWord 1/2, and MacWord 4/5.
- Guesses a broad document family from magic bytes.
- Reads FIB version numbers to classify Word versions 0, 1, 2, 4, 5, 6, 7, or 8.
- Tracks whether the current document is an old Macintosh Word file.
- Dispatches initialization to DOS, Win, Mac, or OLE handlers.
- Frees all document-level lists and metadata with `vFreeDocument()`.

Important behavior:
- OLE detection tolerates one or two trailing bytes from buggy email/base64 handling in limited cases.
- Word 6 Macintosh detection uses `chse` and sets the old-Mac flag.
- Unknown FIB values below 192 are rejected; 192 and above are treated as Word 8-era.

Dependencies:
- All document initializers and all list destructors.

Research relevance:
- The front door and teardown point for Antiword document processing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/wordlib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/wordmac.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/wordmac.c

MacWord 4/5 document initializer.

Key responsibilities:
- Reads the 256-byte MacWord header.
- Verifies MacWord 4/5 magic/version.
- Rejects fast-saved MacWord files.
- Creates one non-Unicode text block from big-endian begin/end text offsets.
- Invokes property parsing and default tab width setup.

Important behavior:
- Uses big-endian header fields for Mac file offsets.
- Does not call notes parsing in this initializer.
- Returns Word version 4 or 5 on success.

Dependencies:
- Version detection, text block list, property dispatcher, tab-stop parser.

Research relevance:
- Legacy Macintosh Word entry point into the shared conversion code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/wordmac.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/wordole.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/wordole.c

OLE compound-document reader and Word 6+ initializer.

Key responsibilities:
- Reads big block depot and small block depot chains.
- Parses Property Set Storage directory entries and computes tree levels.
- Locates required Word streams: `WordDocument`, `Data`, `0Table`, `1Table`, SummaryInformation, and DocumentSummaryInformation.
- Rejects OLE files without Word streams and reports Excel workbooks specially.
- Reads the WordDocument FIB header and determines Word version.
- Chooses active table stream based on FIB flags.
- Builds text/data block lists, property lists, tab width, notes, and summary metadata for Word 6/7/8.

Important behavior:
- PPS tree recursion is capped to avoid infinite loops.
- Word 8 text uses `bGet8DocumentText()`; Word 6/7 fast-save paths use Word 6 helpers.
- Image data comes from the text stream for Word 6/7 and the `Data` stream for Word 8.
- All depot and small-block resources are freed through a shared cleanup macro.

Dependencies:
- Block readers, small block list builder, PPS stream structs, version-specific text/property/data parsers.

Notable risks:
- OLE chain and PPS validation is partial; corrupted depots can still hit fatal errors.
- Files with too-small WordDocument streams are rejected.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/wordole.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/wordtypes.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/wordtypes.h

Shared type definitions for Antiword’s parser and renderers.

Key contents:
- Fixed-width-ish aliases: `UCHAR`, `USHORT`, `UINT`, `ULONG`.
- Platform-specific `diagram_type` for RISC OS Draw output versus portable file output.
- `output_type` linked-list fragment with text storage, width, font, color, and neighboring links.
- Conversion and encoding enums.
- Font table and user option structures.
- OLE PPS stream descriptors.
- Text/data/document/row/style/font/picture/section/header-footer/footnote/list block records.
- Image metadata, compression enums, row info enums, note type enums, and image info enums.

Research relevance:
- This header defines most cross-module data contracts used by property parsers, text block readers, and output backends.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/wordtypes.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/wordwin.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/wordwin.c

WinWord 1/2 document initializer.

Key responsibilities:
- Reads the 384-byte WinWord header.
- Verifies WinWord 1.x or 2.0 magic/version.
- Rejects fast-saved and encrypted documents.
- Builds one combined text block containing main text, footnotes, headers/footers, macros, and annotations.
- Splits that text block into logical lists.
- Optionally builds a data block for images when output settings require images.
- Invokes property parsing, tab width setup, and notes parsing.

Important behavior:
- Template flag is logged but not rejected.
- Data block extraction is skipped for text-only/XML/no-image modes.
- Image data is approximated as the region between end-of-text and character-info start.

Dependencies:
- Text/data block list APIs, option state, property dispatcher, tab-stop parser, notes parser.

Research relevance:
- Legacy Windows Word entry point into the shared conversion pipeline.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/wordwin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/xmalloc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/xmalloc.c

Fail-fast allocation wrapper module.

Key routines:
- `xmalloc()` allocates at least one byte and exits fatally on failure.
- `xcalloc()` allocates zeroed memory, with a 16-bit DOS size guard for non-DJGPP builds.
- `xrealloc()` resizes memory and exits fatally on failure.
- `xstrdup()` duplicates strings without relying on platform `strdup()`.
- `xfree()` frees nullable pointers and always returns `NULL`.

Important behavior:
- Zero-size allocations are normalized to one byte for `xmalloc()` and `xcalloc()`.
- `xfree()` supports the project idiom `ptr = xfree(ptr)`.

Dependencies:
- `werr()` platform error handler and debug macros.

Research relevance:
- Provides consistent allocation semantics throughout the parser, avoiding local null-check handling after allocation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/antiword/xmalloc.c -->