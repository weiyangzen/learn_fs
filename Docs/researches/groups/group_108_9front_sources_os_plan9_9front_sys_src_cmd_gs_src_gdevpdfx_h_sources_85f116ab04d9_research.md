# Group Research: group_108_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_gdevpdfx_h_sources_85f116ab04d9

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfx.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfx.h

Central private header for Ghostscript's PDF-writing device. It defines the shared `gx_device_pdf` state, resource model, output contexts, page bookkeeping, temporary-file streams, encryption fields, and cross-module procedure declarations used by the `pdfwrite` implementation.

Key contents:
- Defines output stream contexts: `PDF_IN_NONE`, `PDF_IN_STREAM`, `PDF_IN_TEXT`, and `PDF_IN_STRING`.
- Declares abstract COS object types used by the PDF object layer.
- Defines PDF resource types, including standard page resources (`ColorSpace`, `ExtGState`, `Pattern`, `Shading`, `XObject`, `Font`) and internal pseudo-resources (`CharProc`, `CIDFont`, `CMap`, `FontDescriptor`, `Group`, `SoftMaskDict`, `Function`, `Page`).
- Defines common resource fields: linked-list links, resource ID, global/named flags, resource name, usage bitmask, and associated COS object.
- Defines `pdf_x_object_t` for Image/Form/PS XObject resources and `pdf_procset_t` bits for page ProcSet tracking.
- Defines document/page helper structures for outlines, articles, DSC-derived page metadata, saved pages, stream positions, text rotation, and temporary files.
- Defines `pdf_font_cache_elem_t` for cached font-resource attachment, glyph usage, and real-width arrays.
- Defines `pdf_viewer_state`, the driver-side mirror of the emitted viewer graphics state: transfer/halftone IDs, alpha/blend/soft-mask state, overprint flags, saved colors, line parameters, dash pattern, and related state.
- Defines `pdf_substream_save` for saving text state, clip state, viewer state, stream/resource context, and substream flags while accumulating charprocs, patterns, forms, and masks.
- Defines the full `gx_device_pdf_s` structure, including Distiller parameters, compression/encryption settings, DSC flags, temporary files, current page/content IDs, resource chains, named-object dictionaries, NI/namespace stacks, font cache, clipping state, page labels, viewer-state stack, substream stack, pattern/image-mask temporary fields, and ps2write-specific flags.
- Declares GC descriptor macros for `gx_device_pdf`, resource objects, XObjects, local converter devices, and substream save objects.
- Declares driver procedure entry points implemented in other files for bitmap copying, path drawing, images, parameters, text, patterns, color spaces, compositors, and transparency.
- Declares shared utilities for object allocation, page/content stream management, resources, encryption, path clipping, masked-image conversion, matrices, names/strings, filters, data streams, functions, font bbox writing, pdfmark processing, named objects, namespaces, and text module hooks.

Notable dependencies:
- Depends on Ghostscript core device/font/stream headers such as `gxdevice.h`, `gxfont.h`, `gxline.h`, `gxdevmem.h`, `stream.h`, and `gdevpsdf.h`.
- Cross-links to many implementation modules: `gdevpdf*.c` for general PDF output and `gdevpdt*.c` for text/font handling.
- Exposes private resource descriptor names such as `st_pdf_font_resource`, `st_pdf_char_proc`, `st_pdf_font_descriptor`, and `st_pdf_color_space`, which are defined by sibling modules.

Research notes:
- This is the central internal contract for the PDF-writing subsystem; it is not a public API.
- Several comments document viewer compatibility limits, especially Acrobat coordinate limits and viewer stack depth.
- The `pte` and `cgp` members are explicitly dangerous temporary pointers from global to local memory and must not be traced by the garbage collector.
- The file is PDF/vector-output infrastructure, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdt.c

Small initialization module for `pdfwrite` text data. It allocates and ties together the text subsystem's top-level bookkeeping objects.

Key behavior:
- Defines the GC descriptor for `pdf_text_data_t` through `private_st_pdf_text_data()`.
- Implements `pdf_text_data_alloc`.
- Allocates `pdf_text_data_t`, outline-font bookkeeping, bitmap-font bookkeeping, and text-state bookkeeping.
- Cleans up all partially allocated components if any allocation fails.
- Initializes the text data structure to zero and stores `outline_fonts`, `bitmap_fonts`, and `text_state`.

Notable dependencies:
- Uses `gdevpdfx.h` for `gx_device_pdf`/PDF internals.
- Uses `gdevpdtx.h`, `gdevpdtf.h`, `gdevpdti.h`, and `gdevpdts.h` for text/font data types and allocation helpers.

Research notes:
- This file contains no text processing logic; it is only the construction point for the text subsystem's aggregate state.
- Allocation is defensive: all component pointers are freed on failure before returning `NULL`.
- This is PDF output infrastructure, not filesystem functionality.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdt.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdt.h

Public-facing internal interface for `pdfwrite` text and font handling. It is intended as the only text/font subsystem header included by pdfwrite code outside `pdftext.dev`.

Key contents:
- Declares allocation and reset functions for text state and text data.
- Declares page/document lifecycle hooks: reset at page start, reset after `grestore`, close page text state, and close/write text-related document resources.
- Declares content-context transitions from stream/string context into text context and a close hook for text contents.
- Declares bitmap-font support functions used by bitmap output: character image Y offset, CharProc begin/end, and image-as-character emission.
- Notes that declarations deliberately duplicate subsystem-private headers so the compiler can check consistency.

Notable dependencies:
- References types from `gdevpdfx.h` and text/font subsystem headers without exposing their full implementations.
- Function comments point to the implementation headers/files that own each function, such as `gdevpdts.h`, `gdevpdti.h`, and `gdevpdtw.h`.

Research notes:
- This header is a narrow façade over the text subsystem, not the full internal structure definition.
- It separates general pdfwrite code from lower-level font resource, encoding, bitmap, and text-state details.
- No filesystem interfaces are present.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtb.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtb.c

BaseFont implementation for `pdfwrite`. It makes stable copies of Ghostscript fonts, tracks glyph usage, decides subsetting, creates subset prefixes, and writes embedded font programs into PDF stream objects.

Key behavior:
- Defines `pdf_base_font_t`, holding copied and complete font copies, subset decision state, standard-font flag, glyph count, optional CIDSet bitmap, font name, written flag, and FontFile COS object.
- Recognizes subset prefixes of the form `XXXXXX+` and strips them when building stable font names.
- Builds deterministic subset prefixes by hashing the used-glyph bitmap and prepending six uppercase letters plus `+`.
- `pdf_base_font_alloc` copies fixed font data into stable memory, zeroes TrueType/Type42 FontMatrix translation components for viewer compatibility, decides initial subset policy, optionally creates a complete copy, counts Type 1 glyphs, allocates CIDSet for CID fonts, and stores a prefix-free font name.
- CID fonts and large TrueType fonts are forced toward subsetting; Type 1/2 and smaller TrueType fonts may remain complete depending on Distiller parameters.
- `pdf_base_font_copy_glyph` copies a used glyph into the saved font and marks the CIDSet bit when appropriate.
- `pdf_do_subset_font` finalizes the subset decision using `SubsetFonts` and `MaxSubsetPct`.
- `pdf_write_FontFile_entry` chooses `/FontFile`, `/FontFile2`, or `/FontFile3` depending on font type and `ResourcesBeforeUsage`.
- `pdf_adjust_font_name` appends a unique `~<id>` suffix for Acrobat Reader 3 compatibility when emitting unsubsetted embedded fonts in PDF 1.2.
- `pdf_write_embedded_font` writes Type 1, Type1C/CFF, TrueType, CIDFontType0C, and CIDFontType2 font programs using Ghostscript PostScript font writers and records stream dictionary lengths/subtypes.
- Writes Type 1 `/CharSet` strings for subsetted fonts and CID `/CIDSet` streams for subsetted CID fonts.
- Exposes helpers for standard-font status and storing/retrieving the associated FontFile COS object.

Notable dependencies:
- Uses Ghostscript font copy/writer APIs from `gxfcopy.h`, `gxfont42.h`, and `gdevpsf.h`.
- Uses PDF stream/object helpers from `gdevpdfx.h` and `gdevpdfo.h`.
- Interfaces with font resource and descriptor layers through `gdevpdtb.h` and `gdevpdtf.h`.

Research notes:
- The file documents Distiller-style subsetting policy and intentionally differs for Type 1, TrueType, and CID fonts.
- FontMatrix translation is cleared because older Adobe rasterizers/viewers mishandle Type42/TrueType matrix translations.
- TrueType embedding uses a position-only stream first to compute `/Length1`.
- Error paths in `pdf_base_font_alloc` free the `pdf_base_font_t` wrapper but rely on Ghostscript allocation ownership patterns for copied fonts.
- This is font/PDF output code, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtb.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtb.h

BaseFont structure/API header for the `pdfwrite` text subsystem. It describes stable font copies, glyph-copying, subsetting, embedded font writing, and subset metadata emission.

Key contents:
- Documents the `pdf_base_font_t` concept used by `gdevpdt*.[ch]`: a stable copy of a supported Ghostscript base font with glyphs copied as needed.
- Explains why the implementation may store both a partial copied font and a complete font copy until the final subsetting decision is known.
- Documents PDF font-name handling and the rule that base font names stored here must not include a `XXXXXX+` subset prefix.
- Declares allocation and accessors for base-font name and copied/complete font pointers.
- Declares subset tests, complete-font dropping, glyph-copying, subset-prefix detection/creation, subset decision, FontFile entry writing, embedded font writing, CharSet writing, CIDSet writing, standard-font testing, and FontFile object accessors.

Notable dependencies:
- Includes `gdevpdtx.h` for shared text/font subsystem types.
- Exposes `gs_font_base`, `gs_glyph`, `gs_matrix`, `gs_string`, `cos_dict_t`, and `gx_device_pdf` interactions indirectly through the subsystem.

Research notes:
- The header explicitly limits supported base font types to Type 1/2, TrueType/Type42, CIDFontType 0, and CIDFontType 2.
- It is a private subsystem API, but its comments are important design documentation for font copying and naming.
- No filesystem behavior is present.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtc.c

Composite and CID-keyed text processing for `pdfwrite`. It handles non-CMap composite fonts, CMap-based Type 0 fonts, CIDFont text, standard/embedded CMap selection, CID width tracking, CID-to-GID maps, and ToUnicode generation.

Key behavior:
- `process_composite_text` handles composite fonts with `FMapType != 9` by scanning text into runs that use the same leaf font, computing effective FontMatrix values, and delegating each run to simple-font encoding/text processing.
- Maintains current point and return-width accumulation when the caller requests width results.
- Rejects unsupported text sources and `TEXT_INTERVENE` cases for composite processing.
- Defines a table of standard PDF CMap names, with PDF 1.4-only names skipped for older compatibility levels.
- `attach_cmap_resource` uses a standard CMap name when possible, writes non-standard CMaps as resources, recognizes identity CMaps with non-standard names, and creates reusable identity ToUnicode CMaps for simple two-byte Unicode mappings.
- `scan_cmap_text` walks a Type 0 CMap text stream, resolves descendant CID fonts, obtains or creates CIDFont resources, resizes CID arrays when documents use CIDs beyond declared counts, records glyph usage, computes horizontal/vertical widths, fills CIDToGIDMap entries for CIDFontType2, and creates parent Type 0 font resources.
- Adds ToUnicode entries, including a workaround for PScript5-generated GlyphNames2Unicode data that uses character codes instead of CIDs.
- Handles `CDevProc` callout by stopping after the affected character and returning `TEXT_PROCESS_CDEVPROC`.
- Emits processed substrings through `process_text_modify_width`, preserving/restoring text parameters around width modification.
- `process_cmap_text` wraps `scan_cmap_text` and updates the text enum's CDevProc callout flag.
- `process_cid_text` supports CIDFont `glyphshow` by converting glyph numbers to two-byte Identity-CMap text, synthesizing a Type 0 font from the CIDFont when needed, and delegating to `process_cmap_text`.

Notable dependencies:
- Uses CMap/font internals from `gxfcmap.h`, `gxfont0.h`, `gxfont0c.h`, `gxfcid.h`, and text helpers from `gdevpdtt.h`.
- Calls font resource, descriptor, width, ToUnicode, and text-state helpers from `gdevpdtf.h`, `gdevpdtd.h`, `gdevpdte.c`, and `gdevpdts.h`.

Research notes:
- PDF has no direct `glyphshow` for CIDFont glyphs; the file represents it through a Type 0 font and Identity CMap.
- The code contains explicit compatibility notes for PScript5.dll and Windows-generated CMaps.
- Width and resource updates happen while scanning, before actual text emission, so the final PDF font dictionaries can be written correctly at document close.
- This is text/font output logic, not filesystem functionality.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtd.c

FontDescriptor implementation for `pdfwrite`. It computes PDF font descriptor metrics, owns the descriptor-to-base-font relationship, writes embedded-font references and descriptor dictionaries, and handles subset-specific CharSet/CIDSet entries.

Key behavior:
- Defines common descriptor values: required metrics (`Ascent`, `CapHeight`, `Descent`, `ItalicAngle`, `StemV`, `FontBBox`, `FontName`, `Flags`) and optional metrics (`AvgWidth`, `Leading`, `MaxWidth`, `MissingWidth`, `StemH`, `XHeight`).
- Defines `pdf_font_descriptor_t` for actual fonts and `pdf_sub_font_descriptor_t` for CID FD dictionary character-class entries.
- Allocates descriptors as pseudo-resources and creates a `pdf_base_font_t` at the same time.
- Exposes descriptor ID, font type, embedding status, subset status, descriptor/base names, copied font access, complete-copy dropping, and glyph-use recording.
- `pdf_compute_font_descriptor` scans the font glyph space to compute bounding boxes, ascent/descent, missing width, fixed-width status, cap height, x-height, italic angle, StemV, and flags.
- Applies 1000-unit scaling for TrueType/CID TrueType metrics and handles CID fonts with existing FontBBox specially.
- Uses glyph-name heuristics for Roman fonts to infer capitals, lowercase dimensions, serif/script/italic/small-caps-like flags, and stem width.
- `pdf_finish_FontDescriptor` computes metrics and writes the embedded font before the descriptor dictionary is written.
- `pdf_write_FontDescriptor` writes the descriptor dictionary, CIDSet for CID subsets, CharSet for Type 1 subsets, FontFile entries for embedded fonts, optional CID style/language/FD data, and then writes the referenced FontFile object.
- Marks embedded subset TrueType fonts symbolic as an Acrobat compatibility workaround.
- `pdf_release_FontDescriptor_components` frees the associated base font and is explicitly underimplemented.

Notable dependencies:
- Uses `gdevpdtb.c` for base-font copying, subset decisions, FontFile writing, CharSet, and CIDSet.
- Uses `gdevpdfo.h` for COS object state and writing.
- Uses Ghostscript glyph metrics, font flags, rectangle handling, and math helpers.

Research notes:
- Comments explain the one-to-one relationship used here between BaseFonts and FontDescriptors, even though PDF permits more.
- The file preserves old Acrobat interpretations of the `Flags` bit shared by StandardEncoding/Adobe Roman.
- There appears to be a likely typo in the CID FontBBox fast path: `desc.FontBBox.p.x` is assigned twice, and `p.y` is not assigned there.
- This is PDF font metadata generation, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtd.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtd.h

FontDescriptor API header for `pdfwrite`. It documents descriptor lifetime, sharing, font-name rules, metric computation, embedded font finalization, and writing.

Key contents:
- Explains that FontDescriptors are pseudo-resources that persist until device close and may be shared by multiple Font resources.
- Documents the subsystem's one-to-one FontDescriptor/BaseFont relationship.
- Documents the rule that a descriptor's `FontName` must match the `BaseFont` of referencing Font/CIDFont resources and is set alongside the font resource name.
- Declares descriptor allocation, ID/type/embed/subset accessors, descriptor and base font-name accessors, copied font access, complete-font dropping, glyph-use recording, metric computation, descriptor finalization, descriptor iteration/finalization helper, descriptor writing, and component release.

Notable dependencies:
- Includes `gdevpdtx.h` and `gdevpdtb.h`.
- References `gx_device_pdf`, `gs_font_base`, `gs_glyph`, and `pdf_font_descriptor_t`.

Research notes:
- This is a private font subsystem interface, mostly consumed by font-resource and text-processing code.
- Descriptor writing is intentionally delayed until font subsetting and CharSet/CIDSet decisions are known.
- No filesystem behavior is present.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdte.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdte.c

Encoding-based Type 1/Type 2/Type 42/simple-font text processing for `pdfwrite`. It obtains encoded font resources, records glyph/encoding/ToUnicode data, estimates text bounds, emits high-level PDF text when possible, and falls back to per-character positioning when widths differ.

Key behavior:
- `pdf_encode_process_string` accepts simple Ghostscript font types (`ft_TrueType`, `ft_encrypted`, `ft_encrypted2`, `ft_user_defined`), encodes or records the string, and sends it to the processing path.
- `pdf_add_ToUnicode` lazily creates a ToUnicode CMap for a font resource and records character-code to Unicode mappings when glyph decoding succeeds.
- Tracks resources used inside Type 3 charprocs and marks nested font/resources as used when a Type 3 font is emitted.
- `pdf_encode_string` obtains a compatible PDF font resource, registers it in substream resources, copies glyphs into base fonts/descriptors, records encoding entries and Differences, adds encodings to copied fonts, handles incomplete "complete" font copies, records used characters, and always builds ToUnicode data for simple fonts.
- `process_text_estimate_bbox` estimates a string's device-space bounding box using the font bbox and current text matrix so text outside the clip can be skipped to avoid huge-coordinate Acrobat problems.
- `pdf_process_string` updates text state, chooses fast `Tj`/`TJ` emission when widths match, or delegates to `process_text_modify_width` when PostScript width operations or real-width differences need explicit positioning.
- Supports `TEXT_RETURN_WIDTH`, `TEXT_DO_DRAW`, `TEXT_DO_NONE`, `TEXT_ADD_TO_ALL_WIDTHS`, `TEXT_ADD_TO_SPACE_WIDTH`, and `TEXT_REPLACE_WIDTHS`.
- `pdf_char_widths` computes/caches PDF Widths and real widths, including Type 3 width arrays and vertical-writing origin adjustments.
- `process_text_return_width` computes total width and detects whether cached real widths differ from PDF Widths.
- `process_text_modify_width` emits characters one at a time, handles glyph-origin shifts, character/word spacing, replacement widths, vertical writing, composite text, CDevProc results, and text matrix repositioning between characters.
- `pdf_encode_glyph` maps a glyph back to a single-byte character code by scanning the font encoding.
- `process_plain_text` converts different Ghostscript text sources into byte strings: strings/bytes, chars, single chars, glyph arrays, and single glyphs. If glyph encoding fails, it tries an unencoded font resource path before allowing fallback.

Notable dependencies:
- Uses Ghostscript font, path, text, and CMap APIs from `gxfont*.h`, `gxfcmap.h`, `gxfcopy.h`, and `gxpath.h`.
- Uses font-resource and descriptor APIs from `gdevpdtf.h`, `gdevpdtd.h`, and shared text helpers from `gdevpdtt.h` and `gdevpdts.h`.
- Uses graphics/resource helpers from `gdevpdfg.h` and `gdevpdfx.h`.

Research notes:
- The file intentionally avoids re-encoding text in newer behavior because font merging can cause encoding conflicts.
- It contains several viewer compatibility guards around huge coordinates, Type 3 widths, vertical glyph origins, and Acrobat text-position limitations.
- `RIGHT_SBW` selects the current sidebearing/origin-shift logic, leaving the older helper compiled out.
- This is text output logic, not filesystem functionality.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdte.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtf.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtf.c

Font and CMap resource implementation for `pdfwrite` text. It defines PDF font resource GC behavior, standard-font recognition, embedding policy, BaseFont computation, allocation for Type 0/Type 3/simple/CID resources, CID width arrays, and CMap resource allocation.

Key behavior:
- Defines public/private GC descriptors for `pdf_font_resource_t`, encoding elements, standard-font bookkeeping, and outline-font bookkeeping.
- Enumerates and relocates different resource subfields depending on font type: Type 0 descendant fonts/CMap names, simple Encoding/v arrays, Type 3 charprocs/cached resources, and CID widths/maps/parent/used2 arrays.
- Defines the 14 standard PDF fonts, their names, and base encodings.
- Scans loaded font resources to find standard fonts by resource status, UniqueID, and standard names.
- Compares candidate font outlines with standard fonts to decide whether a font can be treated as a standard 14 font.
- Allocates `pdf_outline_fonts_t` and the per-device standard-font table.
- Implements generic font-resource allocation with width and used-bit arrays, plus encoded simple-font allocation with 256 Encoding entries and vertical-origin data.
- Resizes font resource arrays, especially for CID fonts whose documents use CIDs beyond the advertised CIDCount.
- Determines whether a font is symbolic, whether font names appear in AlwaysEmbed/NeverEmbed parameter arrays, and whether standard fonts should be embedded or treated as base 14.
- `pdf_font_embed_status` applies PDF/X, compatibility level, standard-font appearance, `EmbedAllFonts`, symbolic-font behavior, and embed lists to return `FONT_EMBED_STANDARD`, `FONT_EMBED_NO`, or `FONT_EMBED_YES`.
- `pdf_compute_BaseFont` computes PDF BaseFont names for simple, CID, and Type 0 fonts; removes spaces for TrueType names; handles Multiple Master non-embedded names; appends CMap names for Type 0 CID descendants; adds subset prefixes at finish time; and synchronizes descriptor FontName.
- Allocates Type 0 font resources with descendant fonts and CMap names.
- Allocates Type 3 font resources for synthesized bitmap/vector fonts.
- Allocates standard base-14 font resources and stores original standard font mappings.
- Allocates simple Type 1/TrueType font resources backed by FontDescriptors.
- Allocates CIDFont resources, including CIDToGIDMap for CIDFontType2, WMode-1 usage maps, and early CIDSystemInfo object writing.
- Lazily allocates CID horizontal/vertical width arrays and vertical origin arrays.
- `pdf_cmap_alloc` delegates CMap writing to `pdf_write_cmap`.

Notable dependencies:
- Uses font copying and standard-font comparison helpers from Ghostscript font internals (`gxfcache.h`, `gxfcid.h`, `gxfcmap.h`, `gxfcopy.h`, `gxfont1.h`).
- Uses descriptor/base-font APIs from `gdevpdtb.h` and `gdevpdtd.h`.
- Uses font-writing declarations from `gdevpdtw.h`.

Research notes:
- The code preserves Acrobat Distiller behavior differences between PDF 1.2 and 1.3 around base 14 font embedding.
- The standard-font path uses actual appearance/outlines, not just names, to avoid treating unrelated fonts with standard names as base 14 fonts.
- CID resource allocation writes CIDSystemInfo immediately to avoid depending on live font objects later.
- This is PDF font resource management, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtf.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtf.h

Font and CMap resource API/header for the `pdfwrite` text subsystem. It defines `pdf_font_resource_t`, encoding entries, standard-font bookkeeping, outline-font state, embedding status, and allocation/accessor routines.

Key contents:
- Documents the supported PDF font resource categories: Type 0 composite fonts, standard 14 fonts, Type 3 bitmap/vector fonts, Type 1/2, Type 42/TrueType, CIDFontType0, and CIDFontType2.
- Provides extensive documentation for PDF `BaseFont` naming rules by font type, including Type 0 descendant/CMap naming, TrueType space removal, Multiple Master non-embedded naming, and subset prefixes.
- Defines `pdf_char_glyph_pair_t` for character/glyph associations used in compatibility checks.
- Defines `pdf_font_write_contents_proc_t`, the callback used to write font-type-specific dictionary contents after generic font keys are written.
- Defines `pdf_encoding_element_t` for Encoding entries, including glyph, glyph-name string, and Differences marker.
- Defines `pdf_resource_ref_t` for resources referenced by Type 3 charprocs.
- Defines `pdf_font_resource_t` with common resource fields, FontType, write callback, BaseFont, descriptor/base-font links, width/used arrays, ToUnicode resource/CMap, and unions for Type 0, CIDFont, and simple font details.
- Type 0 data includes descendant font, Encoding name, CMapName, standard-CMap flag, and WMode.
- CIDFont data includes CIDSystemInfo object ID, CIDToGIDMap, glyphshow Type 0 font ID, vertical widths/origins, second used map, and parent Type 0 font pointer.
- Simple font data includes FirstChar/LastChar, BaseEncoding, Encoding, vertical origin array, and type-specific Type 1/TrueType/Type3 fields.
- Type 3 fields include FontBBox, FontMatrix, CharProcs, max Y offset, bitmap-font flag, used resource refs, and cached-bit map.
- Defines `pdf_font_embed_t` with standard/no/yes embedding statuses.
- Defines standard-font and outline-font bookkeeping structures and their GC descriptors.
- Declares allocation and cleanup for outline fonts, standard-font table access, font-cache freeing, Type 0/Type 3/standard/simple/CID font resource allocation, resource array resizing, font-resource font access, embedding-policy computation, BaseFont computation, document close hook, font-name selection, CMap allocation, and CID-to-GID map addition.

Notable dependencies:
- Includes `gdevpdtx.h` and references `gx_device_pdf`, `gs_font_type0`, `gs_cmap_t`, `pdf_base_font_t`, and `pdf_font_descriptor_t`.
- The header is consumed by most `gdevpdt*.c` files.

Research notes:
- The comments are central to understanding why font naming is delayed or recomputed at finish time.
- The structure intentionally keeps both PDF-visible widths and real PostScript widths because they can differ through Metrics/Metrics2/CDevProc.
- No filesystem behavior is present.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdti.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdti.c

Bitmap and Type 3 CharProc implementation for `pdfwrite`. It creates synthesized bitmap fonts, accumulates Type 3 charprocs, manages substream save/restore, deduplicates charprocs, writes Type 3 font contents, and registers substream resources.

Key behavior:
- Defines `pdf_char_proc_t` pseudo-resources with owning font, next pointer, Y offset, character code/name, real width, and vertical origin.
- Defines `pdf_bitmap_fonts_t` with current open synthesized Type 3 font, reuse flag, shared bitmap Encoding object ID, and maximum embedded character code.
- `assign_char_code` creates/reuses synthesized Type 3 bitmap fonts, increments synthetic font names (`A`, `B`, ...), assigns character codes, stores rounded widths, and creates ToUnicode mappings through the current text enum.
- `pdf_write_contents_bitmap` writes Type 3 font dictionaries: Encoding reference, CharProcs dictionary, FontMatrix, and Type 3 finishing data. For non-bitmap Type 3 fonts it writes an explicit Encoding object.
- `pdf_bitmap_fonts_alloc` initializes bitmap-font bookkeeping.
- `pdf_close_text_page` prevents adding new chars to a Type 3 font across pages for PDF 1.2/Acrobat Reader 3 compatibility.
- `pdf_char_image_y_offset` computes a plausible vertical offset for bitmap character images relative to current text position.
- `pdf_begin_char_proc` and `pdf_end_char_proc` create encrypted CharProc stream objects, reserve/fill stream length in place, and update bitmap Type 3 FontBBox/max offset data.
- `pdf_do_char_image` emits a bitmap character as text using the synthesized Type 3 font and image placement matrix.
- `pdf_write_bitmap_fonts_Encoding` writes the shared synthetic bitmap Encoding Differences object.
- `pdf_start_charproc_accum` enters substream accumulation mode for a Type 3 charproc resource.
- `pdf_set_charproc_attrs` installs charproc metadata, writes `d0`/`d1` width/bbox operators, toggles color skipping per Type 3 cache behavior, marks used/cached bits, and records the active Type 3 owner.
- `pdf_open_aside` and `pdf_close_aside` open and close stream COS objects in temporary aside storage, attaching compression filters without immediate final document output.
- `pdf_enter_substream` saves current stream, context, text state, clip path, viewer graphics state, procsets, resources, Type 3 owner, soft-mask state, object name, and related flags before accumulating a nested object.
- `pdf_exit_substream` restores all saved context and viewer/text state after closing the accumulated stream.
- CharProc deduplication compares character code, encoding/glyph, name, real width, vertical origin, bitmap flag, FontMatrix, encoding compatibility, and COS stream content equality.
- `pdf_end_charproc_accum` exits accumulation, deduplicates or installs the charproc, handles glyph variations by creating another Type 3 font when needed, updates widths/real widths/used bits, and propagates widths for all encoding slots that map to the same glyph.
- `pdf_add_procsets` writes `/ProcSet` arrays.
- `pdf_add_resource` adds a resource reference to a substream resource dictionary and marks resources global for ps2write global-object accumulation when needed.

Notable dependencies:
- Uses text state and font-resource APIs from `gdevpdts.h`, `gdevpdtf.h`, `gdevpdtw.h`, and `gdevpdtt.h`.
- Uses graphics state save/restore and COS object helpers from `gdevpdfg.h`, `gdevpdfx.h`, and `gdevpdfo.h`.

Research notes:
- The file does more than bitmap fonts: it is also the generic substream/charproc accumulation machinery used by Type 3 and other nested PDF resources.
- The in-place CharProc length update assumes length fits in six digits; longer streams return `limitcheck`.
- Comments document Acrobat Reader 3 bugs around Type 3 Encoding and cross-page font downloading.
- This is PDF font/substream infrastructure, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdti.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdti.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdti.h

Bitmap font interface header for `pdfwrite`. It exposes synthesized Type 3 bitmap font operations and internal Type 3 content-writing hooks.

Key contents:
- Documents bitmap fonts as internally created Type 3 fonts whose CharProcs contain a single bitmap image at device resolution.
- Forward-declares `pdf_bitmap_fonts_t`.
- Declares page-close text update, bitmap image Y-offset calculation, CharProc begin/end, and image-as-character emission for bitmap copy code.
- Declares bitmap-font bookkeeping allocation.
- Declares writing the shared bitmap font Encoding object.
- Declares writing the contents of a Type 3 bitmap font resource.

Notable dependencies:
- Includes `gdevpdt.h`, giving access to the outer text/font interface and PDF device types.
- Implemented by `gdevpdti.c` and used by bitmap/text output code.

Research notes:
- This is a small private interface for the bitmap/Type 3 side of the text subsystem.
- It does not define the internal bitmap-font or charproc structures; those live in the implementation file.
- No filesystem behavior is present.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdti.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdts.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdts.c

Text state management for `pdfwrite`. It buffers text and inter-character moves, tracks client-side versus emitted PDF text state, emits text-state operators, and transitions between PDF stream/text/string contexts.

Key behavior:
- Defines an internal text buffer with up to 200 characters and 50 movement entries.
- Maintains two text-state value sets: `in`, reflecting current client/Ghostscript state, and `out`, reflecting the state already emitted to the PDF stream.
- Tracks buffer start position, WMode, leading, line continuation, line start, and output position.
- `append_text_move` adds TJ movement values, merges adjacent moves, rounds near-integers, and rejects movement values that exceed Acrobat limits.
- `set_text_distance` converts device/user deltas back into text-space deltas and rounds near-integers.
- `add_text_delta_move` tries to express a text matrix translation as a TJ offset when transformation parts are compatible and the move is in writing direction.
- `pdf_set_text_matrix` emits `TL`/`T*`, `Td`, or `Tm` depending on how the text matrix changes; `Tm` is adjusted by device resolution scaling.
- Allocates, defaults, copies, page-resets, and grestore-resets `pdf_text_state_t`.
- `pdf_from_stream_to_text` initializes state when entering text from regular stream context.
- `flush_text_buffer` emits either a simple string plus `Tj`/apostrophe or an array plus `TJ`, including embedded movement offsets.
- `sync_text_state` emits changed text state operators (`Tc`, `Tf`, `Tm`/`Td`/leading, `Tr`, `Tw`) before flushing buffered text.
- `pdf_from_string_to_text` flushes/synchronizes accumulated string context back to text context.
- `pdf_close_text_contents` clears current font pointers and sizes.
- `pdf_render_mode_uses_stroke` detects render-mode changes that require stroke-state preparation.
- `pdf_get_text_state_values`, `pdf_set_text_wmode`, and `pdf_set_text_state_values` expose and update the client-side text state.
- `pdf_set_text_state_values` attempts to fold position-only changes into TJ offsets before flushing; otherwise it synchronizes the current buffer.
- `pdf_text_distance_transform` and `pdf_text_position` expose current text-space coordinate behavior.
- `pdf_append_chars` opens the page in string context, appends bytes into the buffer, flushes when full, preserves continuation state, and advances input/output positions.

Notable dependencies:
- Uses `gdevpdfx.h` for page/context operations and `gdevpdtf.h` for font resource details.
- Uses Ghostscript matrix/math helpers and PDF string/name emission helpers.

Research notes:
- This file is a state-delta engine for efficient PDF text output, choosing compact `Tj`, `TJ`, `Td`, `Tm`, `TL`, and related operators.
- The buffering logic is constrained by old Acrobat movement and coordinate limits.
- It intentionally emits `Tw` only when the buffered text contains space characters.
- This is text stream output infrastructure, not filesystem functionality.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdts.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdts.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdts.h

Text state structure/API header for `pdfwrite`. It defines the client-visible text-state values and declares context transition, synchronization, positioning, and append helpers used across the text subsystem.

Key contents:
- Forward-declares `pdf_text_state_t`.
- Defines `pdf_text_state_values_t` with character spacing, active PDF font resource, font size, text-to-user/device matrix, render mode, and word spacing.
- Provides `TEXT_STATE_VALUES_DEFAULT`.
- Declares stream/string-to-text context transitions and closing the text aspect of current contents.
- Declares internal text helpers for render-mode stroke detection, reading text state values, setting WMode, setting text state values, transforming text-space distances, reading current text position, and appending characters with advance widths.

Notable dependencies:
- Includes `gsmatrix.h`.
- Comments point to `gdevpdtt.h` for coordinate-system discussion used by the broader text subsystem.
- Implemented by `gdevpdts.c` and consumed by simple/composite/bitmap text processing modules.

Research notes:
- The matrix comment is important: pdfwrite treats the text-space-to-user-space matrix as text-space-to-device-space for output purposes.
- The header separates caller-provided text-state values from the implementation's buffering/emission decisions.
- No filesystem behavior is present.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdts.h -->