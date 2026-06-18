# Group Research: group_1546_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_gdevpdfx_h_sources__7e354b38cf4c

Scope checked against `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfx.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfx.h

## Purpose
Internal master header for the Ghostscript `pdfwrite` driver. It defines the PDF device state, resource model, page/object bookkeeping, temporary stream files, encryption/data-stream helpers, pdfmark hooks, and exported cross-module entry points.

## Main Definitions
- Defines output contexts: `PDF_IN_NONE`, `PDF_IN_STREAM`, `PDF_IN_TEXT`, `PDF_IN_STRING`.
- Declares abstract Cos object types and resource types, including standard resources and pseudo-resources such as `resourceCharProc`, `resourceCIDFont`, `resourceCMap`, and `resourceFontDescriptor`.
- Defines `pdf_resource_t`, `pdf_x_object_t`, `pdf_procset_t`, outline/article/page structs, temp-file structs, font-cache structs, viewer state, and substream save records.
- Defines the central `gx_device_pdf_s`, including distiller parameters, encryption state, temp files, object IDs, page/resource lists, text state, named-object namespaces, font cache, clipping state, graphics viewer stack, substream stack, and image-mask conversion state.
- Provides GC descriptor macros for resources, pages, substream state, masked-image converters, and the PDF device.

## Integration
- Used by nearly every PDF backend module as the internal contract for `gx_device_pdf`.
- Text/font modules in this group rely on `pdev->text`, resource chains, substream state, `used_mask`, `substream_Resources`, `font3`, `accumulating_substream_resource`, and stream/object helpers declared here.
- Declares device procedures implemented across `gdevpdf*.c`, including drawing, images, params, text, patterns, transparency, and color spaces.

## APIs Declared
- Document/object/page operations: `pdf_open_document`, `pdf_obj_ref`, `pdf_open_obj`, `pdf_begin_obj`, `pdf_end_obj`, `pdf_open_page`, `pdf_current_page`.
- Resource operations: allocation, lookup, substitution, cancellation, writing, freeing, reversing chains, and page-resource storage.
- Data/encryption operations: `pdf_begin_data_stream`, filter attachment, `pdf_begin_data`, `pdf_end_data`, `pdf_begin_encrypt`, `pdf_encrypt_init`.
- Output helpers: matrix/name/string/value writers, function writers, font bounding-box writer, masked-image conversion helpers.
- pdfmark and named-object APIs.
- Text-module bridge APIs: text data allocation/reset, bitmap CharProc handling, Type 3 accumulation, substream enter/exit, and text context transitions.

## Risks and Notes
- Contains explicit “dangerous pointer” fields (`pte`, `cgp`) that point from global to local memory and must not be traced by the garbage collector.
- `MAX_USER_COORD`, outline depth, destination-string size, and viewer stack depth encode Acrobat/PDF compatibility constraints.
- Resource identity depends on `gs_id_hash` chains and object IDs; incorrect resource ownership can leak or duplicate PDF objects.
- Substream save/restore covers many fields; missing a field would corrupt nested patterns, Type 3 charprocs, masks, or global object accumulation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdt.c

## Purpose
Small initialization module for `pdfwrite` text state. It allocates the aggregate `pdf_text_data_t` object used by `gx_device_pdf`.

## Main Logic
- Registers the GC descriptor for `pdf_text_data_t` using `private_st_pdf_text_data()`.
- Implements `pdf_text_data_alloc(gs_memory_t *mem)`.
- Allocates three subordinate components:
  - `pdf_outline_fonts_t` via `pdf_outline_fonts_alloc`.
  - `pdf_bitmap_fonts_t` via `pdf_bitmap_fonts_alloc`.
  - `pdf_text_state_t` via `pdf_text_state_alloc`.
- Frees all partially allocated components if any allocation fails.
- Zeroes the aggregate and installs the three component pointers.

## Integration
- Called by the PDF device initialization path declared through `gdevpdfx.h`/`gdevpdt.h`.
- Bridges the layered text/font subsystem into one object stored at `pdev->text`.
- Depends on `gdevpdtx.h`, `gdevpdtf.h`, `gdevpdti.h`, and `gdevpdts.h`.

## Risks and Notes
- Allocation is all-or-nothing and returns `0` on failure rather than a Ghostscript error code.
- The aggregate only stores pointers; ownership/lifetime of component internals is managed by the Ghostscript allocator/GC descriptors.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdt.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdt.h

## Purpose
Narrow external interface for `pdfwrite` text and font handling. The file explicitly says it is the only text/font header that code outside `pdftext.dev` should include.

## API Surface
- Text state allocation and reset:
  - `pdf_text_state_alloc`
  - `pdf_text_data_alloc`
  - `pdf_reset_text_page`
  - `pdf_reset_text_state`
  - `pdf_close_text_page`
  - `pdf_close_text_document`
- Contents-state transitions:
  - `pdf_from_stream_to_text`
  - `pdf_from_string_to_text`
  - `pdf_close_text_contents`
- Bitmap font entry points for `gdevpdfb.c`:
  - `pdf_char_image_y_offset`
  - `pdf_begin_char_proc`
  - `pdf_end_char_proc`
  - `pdf_do_char_image`

## Integration
- Duplicates selected declarations from internal headers so the compiler can check consistency while hiding most internals from non-text modules.
- Depends on types declared elsewhere through `gdevpdfx.h` inclusion chains, especially `gx_device_pdf`, `pdf_text_data_t`, `pdf_char_proc_t`, and `pdf_stream_position_t`.

## Risks and Notes
- This header intentionally exposes only lifecycle, context transition, and bitmap-char APIs; other font-resource manipulation should remain inside the text subsystem.
- Mismatch between this facade and internal headers would create compile-time contract failures.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtb.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtb.c

## Purpose
Implements `pdf_base_font_t`, the stable copied-font layer used by PDF font resources and descriptors. It handles font copying, subset decisions, subset prefixes, glyph copying, embedded font writing, CharSet, and CIDSet output.

## Main Structures
- `pdf_base_font_t` stores:
  - Partial copied font and optional complete copied font.
  - Subsetting decision state: unknown/no/yes.
  - Standard-font flag.
  - Glyph/CID count and CIDSet bitmap.
  - Stable font name without subset prefix.
  - Written flag and FontFile Cos object pointer.

## Main Functions
- `pdf_base_font_alloc` copies the source font, strips existing subset prefixes, decides mandatory/possible subsetting by font type, allocates CIDSet for CID fonts, and stores a stable font name.
- `pdf_has_subset_prefix` validates `XXXXXX+` prefixes.
- `pdf_add_subset_prefix` hashes the used-glyph bitmap to synthesize a deterministic six-letter subset prefix.
- `pdf_base_font_copy_glyph` copies glyphs into the stable copy and marks CIDSet entries.
- `pdf_do_subset_font` lazily decides optional subsetting from `SubsetFonts` and `MaxSubsetPct`.
- `pdf_write_embedded_font` writes Type 1, Type1C/CFF, TrueType, CIDFontType0C, or CIDFontType2 embedded font streams.
- `pdf_write_CharSet` emits Type 1 subset CharSet.
- `pdf_write_CIDSet` emits the CIDSet stream for subset CID fonts.
- Accessors expose base font name, copied font, subset state, standard state, and FontFile object.

## Integration
- Used by `gdevpdtd.c` for descriptors and by `gdevpdtf.c` for font-resource naming/allocation.
- Uses Ghostscript font-copy APIs (`gs_copy_font`, `gs_copy_font_complete`, `gs_copy_glyph_options`) and PostScript font writers from `gdevpsf.h`.
- Writes data streams through `pdf_begin_data_stream`, `pdf_close_aside`, and Cos dictionaries.

## Risks and Notes
- Contains compatibility workarounds for Acrobat Reader 3/4/5 and Type 42 FontMatrix translation behavior.
- `pdf_add_subset_prefix` reads `used` in ushort-sized chunks, which assumes the used bitmap buffer is valid for the count.
- Type 2 conversion for `ft_encrypted2` without CFF support returns `gs_error_unregistered`.
- `pdf_base_font_alloc` frees only the top-level base font on some failure paths; copied-font ownership is expected to be managed by the Ghostscript memory model.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtb.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtb.h

## Purpose
Defines the base-font interface for `pdfwrite`.

## Model
- A `pdf_base_font_t` is a stable copy of a supported Ghostscript base font.
- Supported font types are Type 1/2, TrueType/Type 42, CIDFontType 0, and CIDFontType 2.
- The module copies fixed font data at creation and copies glyphs as they are used.
- Optional complete copies allow the end-of-document writer to choose full embedding versus subsetting.
- Font names are stored without `XXXXXX+`; subset prefixes are added later if needed.

## API Surface
- Allocation and glyph-copying:
  - `pdf_base_font_alloc`
  - `pdf_base_font_copy_glyph`
- Name/font accessors:
  - `pdf_base_font_name`
  - `pdf_base_font_font`
  - `pdf_base_font_is_subset`
  - `pdf_base_font_drop_complete`
- Subset helpers:
  - `pdf_has_subset_prefix`
  - `pdf_add_subset_prefix`
  - `pdf_do_subset_font`
- Output helpers:
  - `pdf_write_FontFile_entry`
  - `pdf_write_embedded_font`
  - `pdf_write_CharSet`
  - `pdf_write_CIDSet`
- Standard/FontFile helpers:
  - `pdf_is_standard_font`
  - `pdf_set_FontFile_object`
  - `pdf_get_FontFile_object`

## Integration
- Included by font descriptor and font resource layers.
- Keeps PDF font naming and copied-font lifetime separate from font resource dictionaries.

## Risks and Notes
- The header documents name handling in detail because PDF font names are compatibility-sensitive.
- Clients must not add subset prefixes directly to the returned base-font name.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtc.c

## Purpose
Handles composite and CID-based text processing for `pdfwrite`, including Type 0/CMap fonts, CIDFont glyph tracking, widths, CIDToGID maps, and glyphshow adaptation.

## Main Paths
- `process_composite_text` handles composite fonts with non-CMap FMapType by scanning runs in the same leaf font, computing effective leaf FontMatrix values, and delegating each run to `pdf_encode_process_string`.
- `attach_cmap_resource` determines whether a CMap is standard, identity, or needs embedding, writes CMap resources if needed, and attaches identity ToUnicode CMaps where possible.
- `scan_cmap_text` scans CMap-based composite text, obtains CIDFont and parent Type 0 resources, records widths, used CIDs, CIDToGID mappings, ToUnicode pairs, and handles CDevProc callouts.
- `process_cmap_text` validates input modes and wraps `scan_cmap_text`.
- `process_cid_text` supports CIDFont glyphshow by creating or reusing a Type 0 identity-CMap wrapper and then delegating to `process_cmap_text`.

## Integration
- Uses helpers from `gdevpdtt.c` for font-resource lookup, text-state updates, width calculation, and current-point movement.
- Uses `gdevpdtf.c` APIs to allocate or resize CID font resource arrays.
- Uses `gdevpdte.c` via `pdf_encode_process_string` and `process_text_modify_width`.
- Adds ToUnicode data through `pdf_add_ToUnicode`.

## Compatibility Behavior
- Maintains a table of standard CMap names, with PDF 1.4 CMaps gated by compatibility level.
- Treats some nonstandard identity CMaps generated by PScript5.dll as standard identity CMaps.
- Handles PScript5.dll `GlyphNames2Unicode` behavior by sometimes using character code rather than CID for ToUnicode mapping.

## Risks and Notes
- Unsupported subfont types in CMap text return rangecheck, causing fallback behavior higher up.
- Width and CDevProc logic mutates text enumerator indices carefully; mistakes here affect text positioning and `stringwidth`.
- CID resource arrays may be resized if documents use CIDs beyond advertised CIDCount.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtd.c

## Purpose
Implements `pdf_font_descriptor_t`, the pseudo-resource layer for PDF FontDescriptor objects and descriptor metric computation.

## Main Structures
- `pdf_font_descriptor_values_t` stores required and optional FontDescriptor metrics: Ascent, CapHeight, Descent, ItalicAngle, StemV, FontBBox, FontName, Flags, AvgWidth, Leading, MaxWidth, MissingWidth, StemH, XHeight.
- `pdf_font_descriptor_common_t` embeds `pdf_resource_common` plus descriptor values.
- `pdf_font_descriptor_t` adds base font, font type, embedding flag, and CID-specific Style/Lang/FD values.
- `pdf_sub_font_descriptor_t` models FD dictionary entries for CID-keyed character classes.

## Main Functions
- `pdf_font_descriptor_alloc` allocates a descriptor pseudo-resource and associated base font.
- Accessors expose object ID, font type, embedding state, subset state, names, and copied font.
- `pdf_font_used_glyph` forwards glyph copying to the base font.
- `pdf_compute_font_descriptor` scans glyphs to compute metrics and flags, including symbolic/roman/fixed-width/italic/serif/small-caps heuristics.
- `pdf_finish_FontDescriptor` computes descriptor metrics and writes embedded font data if required.
- `pdf_write_FontDescriptor` writes the PDF FontDescriptor dictionary, including CIDSet, CharSet, FontFile, Style, Lang, and FD entries.
- `pdf_release_FontDescriptor_components` frees the base font pointer but is marked underimplemented.

## Integration
- Depends on `gdevpdtb.c` for base-font storage and embedded font output.
- Used by font resources in `gdevpdtf.c` and writing code in `gdevpdtw.c`.
- Writes Cos objects through `pdf_open_separate`, `COS_WRITE`, and `COS_WRITE_OBJECT`.

## Risks and Notes
- Descriptor metric computation is heuristic and explicitly described as crude in places.
- Contains compatibility hack marking embedded subset TrueType fonts symbolic for Acrobat behavior.
- There appears to be a duplicated assignment to `desc.FontBBox.p.x` when initializing CID FontBBox from base font values; likely intended to set both p/q x values.
- Error handling during glyph metric scans skips many non-VM errors because this can run indirectly during finalization.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtd.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtd.h

## Purpose
Defines the FontDescriptor interface for `pdfwrite`.

## Model
- FontDescriptors are pseudo-resources retained until device close.
- Multiple Font resources may share one descriptor.
- In this implementation, FontDescriptors and BaseFonts correspond one-to-one.
- Descriptor `FontName` must match the Font resource `BaseFont`, so naming is coordinated with `gdevpdtf.h` and `gdevpdtb.h`.

## API Surface
- Allocation: `pdf_font_descriptor_alloc`.
- Accessors: descriptor ID, FontType, embedding state, subset state, descriptor name, copied font, base name.
- Glyph tracking: `pdf_font_used_glyph`.
- Metric/output lifecycle:
  - `pdf_compute_font_descriptor`
  - `pdf_finish_FontDescriptor`
  - `pdf_finish_font_descriptors`
  - `pdf_write_FontDescriptor`
  - `pdf_release_FontDescriptor_components`

## Integration
- Includes `gdevpdtx.h` and `gdevpdtb.h`.
- Exposes descriptor operations to font-resource allocation and writing modules.

## Risks and Notes
- The header documents delayed descriptor writing because CharSet depends on final subset contents.
- Descriptor objects are not reference-counted; lifetime relies on all descriptors persisting until device close.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdte.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdte.c

## Purpose
Implements encoding-based text processing for simple fonts: Type 1/2, TrueType/Type 42, and Type 3/user-defined fonts.

## Main Paths
- `pdf_encode_process_string` validates font type, obtains/updates a PDF font resource, then processes the encoded string.
- `pdf_add_ToUnicode` creates and populates ToUnicode CMaps for simple, CID0, and CID2 fonts.
- `pdf_register_charproc_resource` and `pdf_used_charproc_resources` track resources used inside Type 3 CharProcs.
- `pdf_encode_string` obtains a compatible PDF font resource, registers it, copies glyphs, populates encoding entries, marks used characters, and adds ToUnicode pairs.
- `process_text_estimate_bbox` estimates transformed text bounding boxes to skip text outside the clip box when Acrobat coordinate limits would be risky.
- `pdf_process_string` coordinates state update, fast-path text emission, width-return behavior, width modifications, clipping skip, and current-point updates.
- `pdf_char_widths` reads or computes cached Widths and real widths for a character.
- `process_text_return_width` computes total text width and detects when real widths differ from PDF Widths.
- `process_text_modify_width` emits text character-by-character when spacing, replaced widths, vertical origin shifts, or differing real/PDF widths require manual positioning.
- `pdf_encode_glyph` maps a glyph back to a one-byte character code when possible.
- `process_plain_text` adapts Ghostscript text input forms into byte strings and handles intervene/single-glyph cases.

## Integration
- Calls resource APIs from `gdevpdtt.c`, `gdevpdtf.c`, and `gdevpdtd.c`.
- Emits text through `gdevpdts.c` via `pdf_set_text_state_values` and `pdf_append_chars`.
- Uses Type 3 helpers from `gdevpdti.c` for charproc interactions.
- Supplies ToUnicode data used later by font-resource writing.

## Compatibility Behavior
- Avoids re-encoding text in modern paths to prevent encoding conflicts during font merging.
- Falls back for glyphshow if glyphs cannot be encoded with the current simple font.
- Handles Type 3 cached versus uncached charproc width behavior.
- Applies vertical writing and side-bearing shift handling through cached or computed `v` vectors.

## Risks and Notes
- Some fallback paths intentionally return errors so the default rendering path can produce outlines/bitmaps.
- Text enumerator state is temporarily mutated and restored in width-modification paths.
- `process_text_estimate_bbox` uses FontBBox per character, so it is conservative rather than exact.
- There is a likely typo in Type 3 vertical vector storage elsewhere consumed here (`v[ch].y` is assigned from `pcp->v.x` in `gdevpdti.c`).
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdte.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtf.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtf.c

## Purpose
Implements PDF font and CMap resource allocation/management, standard-font recognition, embedding decisions, BaseFont computation, resource array sizing, and CID width array allocation.

## Main Structures and GC
- Provides GC enumeration/relocation for `pdf_font_resource_t`, including BaseFont strings, descriptors, base fonts, Widths, used bitmaps, ToUnicode resources/CMaps, Type0 descendant fonts, CMap names, Type3 charprocs/resources, and CID arrays.
- Defines the 14 standard PDF font names and default base encodings.
- Allocates `pdf_outline_fonts_t` and its standard-font table.

## Main Functions
- `pdf_outline_fonts_alloc`, `pdf_standard_fonts`, and `pdf_clean_standard_fonts` manage standard font bookkeeping.
- `scan_for_standard_fonts` discovers standard fonts in the font directory.
- `find_std_appearance` compares a font’s outlines against known standard fonts.
- `font_resource_alloc`, `font_resource_simple_alloc`, and `font_resource_encoded_alloc` allocate generic, simple, and encoded font resource objects.
- `pdf_resize_resource_arrays` grows Widths/used/CIDToGID/vertical arrays for CID fonts whose documents use larger CIDs than expected.
- `pdf_font_resource_font` resolves copied font data through base font or descriptor.
- `pdf_font_embed_status` decides standard/no/yes embedding using PDF/X, compatibility level, NeverEmbed/AlwaysEmbed/EmbedAllFonts, symbolic status, and standard-font equivalence.
- `pdf_compute_BaseFont` computes final BaseFont names, handles Type0 CMap suffixes, MM Type1 spaces, TrueType space removal, subset prefixes, and descriptor FontName synchronization.
- Allocators create Type0, Type3, standard, simple, CIDFont, and CMap resources.
- `pdf_obtain_cidfont_widths_arrays` lazily allocates horizontal and vertical CID width/origin arrays.
- `pdf_cmap_alloc` delegates CMap writing.

## Integration
- Depends on base-font and descriptor APIs from `gdevpdtb.c` and `gdevpdtd.c`.
- Uses font writing callbacks declared in `gdevpdtw.h`.
- Called by text processing modules to obtain correct PDF font resources and arrays.

## Risks and Notes
- Standard-font substitution depends on font directory scanning, UniqueID checks, and glyph-outline compatibility.
- `pdf_resize_array` copies raw bytes and assumes caller passes correct element counts.
- CID vertical array allocation is deferred; text code must call `pdf_obtain_cidfont_widths_arrays` before writing vertical metrics.
- BaseFont finalization can invalidate copied-font UID for subset fonts to avoid writing inappropriate UIDs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtf.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtf.h

## Purpose
Defines PDF font-resource and CMap-resource structures and APIs for `pdfwrite`.

## Main Definitions
- Defines `pdf_char_glyph_pair_t`, encoding elements, resource references, and font write callback type.
- Defines `pdf_font_resource_t`, a resource wrapper for:
  - Type 0 composite fonts.
  - CIDFontType 0 and CIDFontType 2 descendants.
  - Simple Type 1/2 and TrueType fonts.
  - Type 3 fonts, including bitmap/vector charprocs.
  - Standard 14 fonts.
- Stores BaseFont, FontDescriptor, Widths, used bitmaps, ToUnicode resources/CMaps, and variant-specific union data.
- Defines `pdf_font_embed_t` with standard/no/yes embedding states.
- Defines `pdf_standard_font_t` and `pdf_outline_fonts_t`.

## API Surface
- Outline/standard font lifecycle:
  - `pdf_outline_fonts_alloc`
  - `pdf_standard_fonts`
  - `pdf_clean_standard_fonts`
  - `pdf_free_font_cache`
- Resource allocation:
  - `pdf_font_type0_alloc`
  - `pdf_font_type3_alloc`
  - `pdf_font_std_alloc`
  - `pdf_font_simple_alloc`
  - `pdf_font_cidfont_alloc`
  - `font_resource_encoded_alloc`
- Resource utilities:
  - `pdf_resize_resource_arrays`
  - `pdf_font_resource_font`
  - `pdf_font_embed_status`
  - `pdf_compute_BaseFont`
  - `pdf_choose_font_name`
  - `pdf_obtain_cidfont_widths_arrays`
- CMap/CID utilities:
  - `pdf_cmap_alloc`
  - `pdf_font_add_cid_to_gid`

## Integration
- Central structural contract used by text processing, descriptor generation, base-font embedding, and font writing modules.
- Relies on `gdevpdtx.h` for core text/device abstractions.

## Risks and Notes
- The struct is large and variant-heavy; callers must only access union arms that match `FontType`.
- The header’s long BaseFont naming notes are important for PDF compatibility and subset correctness.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdti.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdti.c

## Purpose
Implements bitmap-font and Type 3 CharProc support for `pdfwrite`, including synthesized bitmap fonts, vector Type 3 charproc accumulation, substream save/restore, duplicate CharProc detection, and substream resource dictionaries.

## Main Structures
- `pdf_char_proc_t` is a pseudo-resource with owning font, same-font chain link, y offset, char code/name, real width, and vertical origin vector.
- `pdf_bitmap_fonts_t` tracks the current synthesized Type 3 bitmap font, encoding object ID, and max embedded code.

## Main Functions
- `assign_char_code` creates/reuses synthesized Type 3 bitmap fonts, assigns character codes, stores widths, and creates ToUnicode mappings.
- `pdf_write_contents_bitmap` writes Type 3 `/Encoding`, `/CharProcs`, `/FontMatrix`, and delegates common Type 3 finalization.
- `pdf_bitmap_fonts_alloc` initializes bitmap-font state.
- `pdf_close_text_page` prevents adding characters to existing Type 3 fonts across pages for old Acrobat compatibility.
- `pdf_char_image_y_offset` computes bitmap character y-offset relative to current text position.
- `pdf_begin_char_proc` and `pdf_end_char_proc` open/write/close bitmap CharProc streams with inline length patching and encryption support.
- `pdf_do_char_image` emits a bitmap image reference as text using the synthesized Type 3 font.
- `pdf_write_bitmap_fonts_Encoding` writes the shared bitmap encoding differences object.
- `pdf_start_charproc_accum`, `pdf_set_charproc_attrs`, and `pdf_end_charproc_accum` manage Type 3 vector charproc capture, widths, cache flags, duplicate detection, and font attachment.
- `pdf_open_aside`/`pdf_close_aside` create Cos stream objects in temporary storage.
- `pdf_enter_substream`/`pdf_exit_substream` save and restore device state around nested substream accumulation.
- `pdf_add_procsets` and `pdf_add_resource` populate substream Resources dictionaries.

## Integration
- Uses font resource allocation from `gdevpdtf.c`, text-state APIs from `gdevpdts.c`, and resource/object APIs from `gdevpdfx.h`.
- Interacts with viewer graphics state save/restore and graphics reset helpers outside this group.
- Registers resources used inside Type 3 charprocs so page/substream resource dictionaries remain complete.

## Risks and Notes
- CharProc length is patched into a fixed-width placeholder and rejects streams longer than 999999 bytes.
- Substream state save/restore touches many `gx_device_pdf` fields; missing one can corrupt nested charprocs/patterns/masks.
- Duplicate CharProc detection uses Cos object equality and encoding compatibility.
- In `pdf_end_charproc_accum`, `pdfont->u.simple.v[ch].y` is assigned `pcp->v.x`, likely a typo for `pcp->v.y`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdti.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdti.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdti.h

## Purpose
Defines the bitmap-font interface for `pdfwrite`.

## API Surface
- Page/text integration:
  - `pdf_close_text_page`
- Bitmap image character support:
  - `pdf_char_image_y_offset`
  - `pdf_begin_char_proc`
  - `pdf_end_char_proc`
  - `pdf_do_char_image`
- Internal bitmap-font lifecycle:
  - `pdf_bitmap_fonts_alloc`
  - `pdf_write_bitmap_fonts_Encoding`
  - `pdf_write_contents_bitmap`

## Integration
- Included by `gdevpdt.c`, `gdevpdt.h`, and bitmap/text implementation modules.
- Type 3 bitmap fonts are described as internally created fonts whose CharProc is a single bitmap image at device resolution.

## Risks and Notes
- The API is split between external bitmap image output used by `gdevpdfb.c` and internal font-writing helpers used by text code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdti.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdts.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdts.c

## Purpose
Implements PDF text-state management and buffered text emission. It tracks client-visible text state versus emitted PDF text state and writes compact PDF text operators only when needed.

## Main Structures
- `pdf_text_buffer_t` accumulates up to 200 characters and 50 movement adjustments.
- `pdf_text_state_t` stores:
  - Input/client state (`in`), current start point, buffer, and writing mode.
  - Output/PDF stream state (`out`), leading, line-continuation flags, line start, and output position.

## Main Functions
- Allocation/reset/copy:
  - `pdf_text_state_alloc`
  - `pdf_set_text_state_default`
  - `pdf_text_state_copy`
  - `pdf_reset_text_page`
  - `pdf_reset_text_state`
- Context transitions:
  - `pdf_from_stream_to_text`
  - `pdf_from_string_to_text`
  - `pdf_close_text_contents`
- Buffer/state synchronization:
  - `append_text_move`
  - `add_text_delta_move`
  - `pdf_set_text_matrix`
  - `flush_text_buffer`
  - `sync_text_state`
- Public state APIs:
  - `pdf_render_mode_uses_stroke`
  - `pdf_get_text_state_values`
  - `pdf_set_text_wmode`
  - `pdf_set_text_state_values`
  - `pdf_text_distance_transform`
  - `pdf_text_position`
  - `pdf_append_chars`

## Output Behavior
- Emits `Tc`, `Tf`, `Tm`, `Td`, `TL`, `T*`, `Tr`, `Tw`, `Tj`, and `TJ` as needed.
- Uses `TJ` movement entries to represent small compatible text-position deltas without flushing/repositioning.
- Uses leading optimization for line advances.
- Opens pages in `PDF_IN_STRING` when appending characters.

## Integration
- Called by simple/composite text processing (`gdevpdte.c`, `gdevpdtc.c`) and bitmap-image text emission (`gdevpdti.c`).
- Uses font-resource fields to derive writing mode and register Type 3 charproc resources.
- Relies on `gdevpdfx.h` stream/page context APIs.

## Risks and Notes
- Buffer limits are arbitrary; overflow forces synchronization and continuation handling.
- Acrobat coordinate limits influence movement thresholds.
- State comparison uses raw matrix memory comparison in places, so exact floating-point equality affects optimization choices.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdts.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdts.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdts.h

## Purpose
Defines text-state values and APIs shared inside the `pdfwrite` text subsystem.

## Main Definitions
- Forward declares `pdf_text_state_t`.
- Defines `pdf_text_state_values_t`, the client-facing state that can be translated into PDF text operators:
  - Character spacing (`Tc`)
  - Font resource and size (`Tf`)
  - Text matrix (`Tm` and related positioning)
  - Render mode (`Tr`)
  - Word spacing (`Tw`)
- Defines `TEXT_STATE_VALUES_DEFAULT`.

## API Surface
- Context transitions:
  - `pdf_from_stream_to_text`
  - `pdf_from_string_to_text`
  - `pdf_close_text_contents`
- Internal text code helpers:
  - `pdf_render_mode_uses_stroke`
  - `pdf_get_text_state_values`
  - `pdf_set_text_wmode`
  - `pdf_set_text_state_values`
  - `pdf_text_distance_transform`
  - `pdf_text_position`
  - `pdf_append_chars`

## Integration
- Used by text processing modules to update PDF text state without knowing the buffering internals in `gdevpdts.c`.
- Includes `gsmatrix.h` because matrices are part of the public text-state value contract.

## Risks and Notes
- The matrix is documented as text-space to user/device-space after combining PostScript CTM, FontMatrix, and inverse font size scaling; callers must pass the correct coordinate-space matrix.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdts.h -->