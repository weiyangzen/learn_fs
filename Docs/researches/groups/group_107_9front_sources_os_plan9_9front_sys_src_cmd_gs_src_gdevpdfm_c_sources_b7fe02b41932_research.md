# Group Research: group_107_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_gdevpdfm_c_sources_b7fe02b41932

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfm.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfm.c

Ghostscript `pdfwrite` pdfmark processor. It receives `pdfmark` pseudo-parameters from PostScript execution, normalizes arguments, resolves named-object references, transforms coordinates, and dispatches each pdfmark type to PDF object/resource construction logic.

Key behavior:
- Provides utilities for pdfmark handling: `pdf_key_eq`, integer scanning, page reference resolution, destination construction, destination name coercion, rectangle/border parsing, and dictionary pair insertion.
- Implements annotation/link handling through `pdfmark_annot`, mapping pdfmark keys to PDF annotation keys, transforming `/Rect` and `/Border`, and attaching annotations to the target page’s `/Annots` array.
- Builds outline trees for `OUT` pdfmarks, tracking depth, parent/prev/next/first/last links, `/Count`, implicit destinations, and delayed writing of prior outline nodes.
- Implements article/thread support with bead objects, page references, bead rectangles, and final article dictionaries.
- Handles named destinations via `DEST`, including simple destination arrays and destination dictionaries with extra metadata.
- Handles PostScript pass-through `PS` pdfmarks, either inlining short code or emitting `/Subtype /PS` XObject resources, with optional Level 1 fallback streams.
- Supports document/page dictionary pdfmarks: `PAGES`, `PAGE`, `DOCINFO`, `DOCVIEW`, and `PAGELABEL`.
- Rewrites `/Producer` values in `DOCINFO` when they reference Distiller, replacing the Distiller segment with Ghostscript’s producer string.
- Implements named object pdfmarks: `BP`, `EP`, `SP`, `OBJ`, `PUT`, `.PUTDICT`, `.PUTINTERVAL`, `.PUTSTREAM`, `APPEND`, `CLOSE`, `NamespacePush`, `NamespacePop`, and `NI`.
- Starts and ends form XObject accumulation for `BP`/`EP`, storing `/BBox`, `/Matrix`, `/Resources`, OPDF-read global flags, and named-object bindings.
- Creates COS arrays, dictionaries, and streams for `/OBJ`, with stream compression setup for pdfmark-owned stream objects.
- Mutates named COS objects through array put/append, dictionary put, stream writes, interval writes, and close state checks.
- Maintains local namespace stacks for named-object scoping and named-image stack entries for later image handling.
- Includes dispatch entries for marked content and document structure pdfmarks, but those handlers currently return success without implementing output.

Notable dependencies:
- COS object APIs from `gdevpdfo.h`.
- Named-object scanning/replacement from `gdevpdfr.c`.
- PDF object/resource/page utilities from `gdevpdfx.h` and `gdevpdfu.c`.
- Stream compression filters from `szlibx.h` and `slzwx.h`.

Research notes:
- `pdfmark_process` expects argument layout `(key,value)*, CTM, type`; it strips CTM/type, optionally extracts `/_objdef`, substitutes `{name}` references with indirect references, and dispatches by pdfmark name.
- CTM handling is pdfmark-specific: most pdfmarks are converted into default user space, while `BP` and `SP` request the true CTM.
- Named content and document-structure pdfmarks are explicitly marked “NOT IMPLEMENTED YET”.
- This is PDF metadata/resource/output glue, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfo.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfo.c

Ghostscript `pdfwrite` COS object implementation. It supplies the internal object model for PDF arrays, dictionaries, streams, scalar values, resources, object references, writing, equality checks, and memory management.

Key behavior:
- Defines concrete element structures for arrays, dictionaries, and stream content pieces, plus Ghostscript GC descriptors and relocation/enumeration procedures.
- Initializes generic COS objects and allows unresolved generic objects to “become” arrays, dictionaries, or streams for forward-reference pdfmark workflows.
- Represents COS values as scalar strings, constant strings, indirect object references, or resource-name references.
- Handles value copying/freeing rules, including ownership of scalar strings and recursive freeing of un-IDed object values.
- Writes scalar values through `pdf_write_value`, object values inline or as `N 0 R`, and resource values as `/R#`.
- Implements COS arrays with sparse index support: array elements are stored in decreasing index order, temporarily reversed for writing, and missing indices are emitted as `null`.
- Provides array helpers for adding strings, integers, reals, objects, and stack-style `unadd`.
- Implements COS dictionaries with key/value insertion, replacement, move-all, lookup, writing, and equality checks.
- Provides a parameter-list writer that serializes Ghostscript typed parameters into a COS dictionary, including integer and float arrays.
- Implements COS streams as dictionary-plus-content-piece objects. Stream data is accumulated in temporary stream storage, then copied into final PDF streams on write.
- Supports stream equality by comparing dictionaries and temporary-file stream pieces, with a noted assumption that compared streams have matching segmentation.
- Implements stream piece append/release, byte append, stream-content copy, and stream length tracking.
- Provides `cos_write_stream_alloc`, a stream adapter that writes into a COS stream and records piece boundaries when closed or flushed.

Notable dependencies:
- PDF output helpers from `gdevpdfx.h` and `gdevpdfu.c`.
- Ghostscript memory/GC infrastructure and stream filters.
- `pdf_copy_data`, `pdf_copy_data_safe`, and encryption helpers for copying stream content into final output.

Research notes:
- COS objects are not reference counted; the code relies on object IDs and ownership conventions.
- Generic objects are intentionally used for forward references and are later mutated to a concrete type.
- Dictionary keys are unsorted and array entries are sparse, matching pdfmark/resource generation needs rather than a general-purpose PDF object library.
- This file underpins pdfmark and PDF resource construction; it contains no filesystem behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfo.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfo.h

Internal header for `pdfwrite` COS object support. It declares the object/value/container model implemented by `gdevpdfo.c` and exposes helpers used throughout the PDF-writing driver.

Key contents:
- Defines abstract COS types: `cos_object_t`, `cos_array_t`, `cos_dict_t`, `cos_stream_t`, `cos_value_t`, and associated procedure tables.
- Documents the model: only arrays, dictionaries, and streams are composite COS objects; other PDF syntactic values are stored as printed scalar strings.
- Defines shared object fields through `cos_object_struct`: procedure table, object ID, elements, stream pieces, owning PDF device, resource pointer, open/graphics/written flags, stream length, and optional input stream.
- Defines COS value types: scalar strings, constant strings, indirect object references, and resource-name references.
- Declares allocation functions for generic objects, arrays, dictionaries, streams, and float arrays.
- Declares object lifecycle, type mutation, writing, and value construction APIs.
- Declares array operations for indexed put, append, typed append, stack pop, and enumeration.
- Declares dictionary operations for keyed put, typed put, string put, move-all, and lookup.
- Declares stream operations for adding bytes, adding stream contents, releasing pieces, getting the dictionary, and allocating a stream writer.
- Declares COS stream/dictionary writing helpers and named-object write/delete helpers used at document close.
- Defines `cos_param_list_writer_t`, a Ghostscript parameter-list writer that stores parameters into a COS dictionary.

Research notes:
- The header explicitly states COS objects are not reference counted and that objects without IDs are assumed to be owned by a single parent.
- Procedures containing `_c_` in their names do not copy C string arguments; this ownership convention is important for callers.
- `is_open` and `is_graphics` are mainly pdfmark validation flags for `CLOSE`, `PUT`, and `SP`.
- This is private PDF output infrastructure, not a filesystem-facing API.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfo.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfp.c

Ghostscript `pdfwrite` parameter get/put implementation. It exposes PDF device parameters, handles write-only `pdfmark` and `DSC` pseudo-parameters, updates compatibility/device settings, and maps selected DSC comments into PDF metadata/page state.

Key behavior:
- Defines supported PDF-specific parameter items, including Distiller-compatible controls, Ghostscript-specific toggles, encryption fields, OPDF-read behavior, clipping/shading/viewer limits, and PDF/X.
- `gdev_pdf_get_params` writes inherited PSDF parameters plus PDF-specific values such as `.EmbedFontObjects`, `CoreDistVersion`, `CompatibilityLevel`, `pdfmark`, and `DSC`.
- `gdev_pdf_put_params` handles pseudo-parameters first:
  - `pdfmark` opens the document and dispatches to `pdfmark_process`.
  - `DSC` opens the document and dispatches to `pdf_dsc_process`.
- Enforces `LockDistillerParams` by ignoring PDF-specific reset attempts unless unlocking.
- Validates `.EmbedFontObjects` and `CoreDistVersion`.
- Normalizes requested `CompatibilityLevel` to supported PDF levels and adjusts version handling for PDF/X and OPDF-read mode.
- Reads `ProcessColorModel`, updates the PDF process color model, and resets initial fill/stroke colors.
- Validates `FirstObjectNumber`, only allowing changes before object allocation or to the existing effective value.
- Adjusts resolution if page dimensions would exceed Acrobat’s user-coordinate limits.
- Restores saved device state on parameter errors.
- `pdf_dsc_process` recognizes DSC comments for creator/title/author, orientation, viewing orientation, EPS state, and bounding boxes.

Notable dependencies:
- Generic PSDF parameter handling from `gdev_psdf_get_params` and `gdev_psdf_put_params`.
- `pdfmark_process`, `pdf_open_document`, COS dictionary helpers, and page/DSC state fields in `gx_device_pdf`.

Research notes:
- The comments list many Distiller parameters and features that are partially implemented or not implemented.
- OPDF-read mode forces resources-before-usage behavior, disables CFF/PDF widths/stroke color support, sets PDF 1.2-like behavior, and permits large inline images to reduce temporary buffering.
- PDF/X forces compatibility behavior toward PDF 1.3.
- This file configures PDF output behavior; it does not implement filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfr.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfr.c

Named-object and token-scanning support for pdfmark processing. It manages `{name}` object references, local/global named-object namespaces, namespace stack operations, and substitution of named references inside pdfmark argument strings.

Key behavior:
- Validates object-name syntax as `{name}` with braces spanning the full string.
- Looks up named objects first in the current local namespace, then in the global namespace.
- Creates named objects as generic forward references or as typed COS arrays/dictionaries/streams with optional assigned object IDs.
- Resolves predefined page names: `{ThisPage}`, `{NextPage}`, `{PrevPage}`, and `{PageN}`.
- Maps page names to page dictionary objects by ensuring page IDs exist.
- Supports `pdf_make_named` and `pdf_make_named_dict` for creating or finalizing forward references, rejecting attempts to redefine already typed objects.
- Supports `pdf_get_named` with type checking.
- Pushes and pops local named-object namespaces, also saving/restoring the named-image stack.
- Implements a simplified PostScript-token scanner used for pdfmark strings, including composite array/dictionary token scanning.
- Handles a Ghostscript-specific null-delimited name convention produced by `gs_pdfwr.ps`.
- Replaces `{name}` references in parameter strings with `N 0 R` references through a two-pass sizing/copying process.

Notable dependencies:
- COS dictionary/array/object APIs from `gdevpdfo.h`.
- Page ID allocation from `gdevpdfu.c`.
- Scanner character classes and PostScript string decode helpers.

Research notes:
- The scanner intentionally handles a subset of PostScript syntax, not full PDF syntax.
- Forward references are allowed; unresolved or invalid references are left as literal strings during substitution.
- Namespace push/pop is used by pdfmark scoping and must preserve both named objects and named-image entries.
- This file is pdfmark object-reference plumbing, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdft.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdft.c

Ghostscript `pdfwrite` transparency compositor bridge. It converts Ghostscript PDF 1.4 transparency compositor operations into PDF group, form XObject, and soft-mask resources when transparency output is available.

Key behavior:
- Builds soft-mask dictionaries with `/S /Alpha` or `/S /Luminosity`, optional `/BC` background color arrays, and optional `/TR` transfer function references.
- Builds transparency group dictionaries with `/Type /Group`, `/S /Transparency`, optional `/I`, optional `/K`, and optional `/CS` based on the current Ghostscript color space.
- Deduplicates group resources through `pdf_substitute_resource`.
- Builds form XObject dictionaries for nested transparency groups, including transformed `/BBox`, `/Subtype /Form`, `/FormType 1`, identity `/Matrix`, and `/Group`.
- Begins transparency groups by opening the page, emitting needed clip paths, and either recording a page group ID or entering an XObject substream for nested groups.
- Ends transparency groups by closing the substream, deduplicating the XObject resource, and emitting `/R# Do` for nested groups.
- Begins transparency masks either by setting an image-mask skip flag for image masks or by creating a soft-mask dictionary and nested group.
- Ends transparency masks by closing the accumulated group XObject, storing it as `/G` in the soft-mask dictionary, deduplicating the soft-mask dictionary, and recording `pis->soft_mask_id`.
- `gdev_pdf_create_compositor` intercepts `GX_COMPOSITOR_PDF14_TRANS` operations for PDF 1.4+ when transparency is enabled; otherwise it delegates to `psdf_create_compositor`.
- Provides stub device methods for older transparency device hooks that comments say are not expected to be called.

Notable dependencies:
- Ghostscript transparency types from `gstrans.h`.
- Color-space, drawing-state, resource, and COS helpers from `gdevpdfx.h`, `gdevpdfg.h`, and `gdevpdfo.h`.

Research notes:
- Transparency output is gated by `HaveTransparency` and `CompatibilityLevel >= 1.4`.
- Image soft masks are handled with a documented double-enumeration workaround so high-level image handling can deduplicate the actual image stream later.
- `pdf_set_blend_params` is currently a no-op.
- This file is PDF transparency output support, unrelated to filesystem behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdft.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfu.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfu.c

Core output utility implementation for the Ghostscript `pdfwrite` driver. It owns document opening, object IDs and xref positions, content-stream context transitions, encryption, resource lifecycle, page helpers, PDF value writing, filter dictionary writing, generic data streams, function resources, and font bounding boxes.

Key behavior:
- Copies and strips OPDF-read procsets, with optional filtering/compression and TrueType-related skipping.
- Opens the PDF document header, writes binary marker bytes when allowed, and selects page compression mode.
- Allocates object IDs, records xref positions, opens/closes numbered objects, and handles separate/asides streams.
- Manages page content contexts through state transitions among none, stream, text, and string contexts.
- Starts page content streams with scaling from device resolution to default user space, optional rendering intent, encryption, and Flate/LZW compression.
- Closes page content streams, writes stream lengths, restores viewer state, and closes compression/encryption filters.
- Implements PDF object encryption key derivation and ARC4 stream/string encryption helpers.
- Maintains resource chains by type, including allocation, cancellation, forgetting, substitution/deduplication, lookup by Ghostscript ID/resource ID, dropping by condition, statistics, writing, reversing, and freeing.
- Stores per-page resource dictionaries and ProcSet usage.
- Copies temporary stream data safely, including same-file copy handling and optional encryption during final copy.
- Grows the page table on demand and allocates page dictionaries and IDs.
- Opens current pages and unclipped stream contexts.
- Writes matrices, PDF names with escaping, strings, arrays/dictionaries with encrypted string elements, and generic serialized values.
- Writes filter and decode-parameter dictionaries for ASCII85, CCITT, DCT, Flate, LZW, PNG predictor, and RunLength filters.
- Begins and ends generic data streams and writes function resources from Ghostscript function objects.
- Supports sampled/function data streams, function arrays, scaled functions, and function resource substitution.
- Writes font bounding boxes, expanding empty boxes to avoid Acrobat display issues.

Notable dependencies:
- Ghostscript stream filters: ASCII85, CCITT, DCT, LZW, PNG predictor, RunLength, ARC4, MD5, zlib.
- COS object APIs from `gdevpdfo.h`.
- PDF graphics/color/font helpers from `gdevpdfg.h`, `gdevpdfx.h`, and `gdevpdtd.h`.

Research notes:
- The file is the central low-level backend for many other `gdevpdf*` modules.
- Temporary streams are deliberately not encrypted while being accumulated because they may be compared for deduplication; encryption is applied when copying to final output.
- Resource deduplication uses COS object equality plus optional type-specific equality callbacks.
- The compatibility comments retain older PDF 1.2/LZW paths, though current comments say Flate is always available for supported levels.
- This is PDF file generation infrastructure, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfv.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfv.c

Pattern and shading color output for Ghostscript `pdfwrite`. It writes PatternType 1 tiling patterns, PatternType 2 shading patterns, image-backed pattern masks, and PDF shading dictionaries/streams.

Key behavior:
- Defines mesh shading coordinate and component encoding ranges, including Acrobat coordinate-range constraints.
- Provides a COS helper for writing matrix arrays.
- Validates image-pattern tile sizes against Acrobat’s approximate 64 KB image pattern limit.
- Creates PatternType 1 resources that reference image XObjects, with `/PatternType`, `/PaintType`, `/TilingType`, `/Resources`, `/BBox`, `/Matrix`, `/XStep`, `/YStep`, and a small content stream invoking the image XObject.
- Stores high-level PatternType 1 parameters from Ghostscript pattern instances, compensating for shifted bitmap origins and device resolution scaling.
- Writes imagemask resources for uncolored pattern masks, inverting Y because pattern masks are in device coordinates.
- Emits uncolored patterns, optimizing all-ones masks into pure-color output when no pattern stream is needed.
- Emits colored patterns, including optimization of masked colored patterns into uncolored pure-color patterns when all masked pixels share one color.
- Rejects masked image patterns for compatibility levels below PDF 1.3.
- Handles high-level pattern streams by finding/deduplicating already-created Pattern resources.
- Writes common shading dictionary keys: `/ShadingType`, `/AntiAlias`, `/ColorSpace`, optional `/Background`, and optional `/BBox`.
- Writes scalar shadings: function-based, axial, and radial.
- Writes optional shading `/Function` entries, with range scaling when needed.
- Converts array-backed mesh data into packed binary PDF shading streams with 24-bit coordinates, 16-bit components, and 8-bit flags.
- Handles free-form Gouraud triangle, lattice-form Gouraud triangle, Coons patch, and tensor-product patch shadings.
- Writes PatternType 2 shading pattern dictionaries with `/PatternType 2`, `/Shading`, and transformed `/Matrix`.
- Exposes `gdev_pdf_include_color_space` to register a color space resource by name.

Notable dependencies:
- Ghostscript pattern/shading APIs: `gsiparm3.h`, `gsptype2.h`, `gxpcolor.h`, and `gxshade.h`.
- PDF color-space, image-writer, resource, and COS helpers from `gdevpdfg.h`, `gdevpdfx.h`, and `gdevpdfo.h`.

Research notes:
- Pattern output is tightly coupled to image XObject creation from the image-writing modules.
- Mesh data handling distinguishes array data sources from stream data sources; array data is re-encoded into PDF-friendly packed binary.
- Several comments document viewer compatibility limits rather than core PDF spec limitations.
- This file handles PDF graphics resources and color output, not filesystem functionality.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfv.c -->