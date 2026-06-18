# Group Research: group_1545_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_gdevpdfm_c_sources__e8d8be53d60a

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfm.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfm.c

## Purpose

`gdevpdfm.c` implements `pdfmark` processing for Ghostscript's PDF-writing driver. It receives the PostScript-side `pdfmark` pseudo-parameter, normalizes its key/value argument array, resolves named object references, applies CTM transforms where needed, and dispatches to handlers for annotations, links, outlines, articles, destinations, PostScript XObjects, document/catalog/page dictionaries, page labels, named COS objects, and namespace operations.

This is application-level Ghostscript PDF writer code within the Plan 9 source tree, not OS/VFS or filesystem code.

## Main Entry Points

- `pdfmark_process(gx_device_pdf *pdev, const gs_param_string_array *pma)`: central dispatcher. It expects `(... key/value args ..., CTM, mark-type)`, validates the CTM, finds the mark type in `mark_names`, handles `/_objdef`, substitutes named references unless disabled, adjusts CTM unless `PDFMARK_TRUECTM`, then invokes the selected handler.
- `pdf_key_eq(...)`: shared helper for comparing parameter strings to literal keys.
- `pdfmark_scan_int(...)`: parses integer parameter strings.
- `pdfmark_close_outline(...)`: exported outline-level close helper.
- `pdfmark_write_article(...)`: exported article finalization helper.
- `pdfmark_end_pagelabels(...)`: flushes pending page-label state.

## Implemented Pdfmark Families

- Annotation/link marks:
  - `ANN`, `LNK` call `pdfmark_annot`.
  - `pdfmark_put_ao_pairs` performs key remapping such as `/Action` to `/A`, `/Color` to `/C`, `/Title` to `/T`, action subdictionary synthesis, `/Rect` and `/Border` CTM transforms, `/Contents` newline normalization, implicit outline destinations, and special handling for `/GoTo`, `/GoToR`, `/Launch`, and `/Article`.
- Outline marks:
  - `OUT` builds an outline tree incrementally using `pdev->outline_levels`.
  - Nodes are written as separate objects by `pdfmark_write_outline`.
  - Counts and open/closed subtree state are tracked manually.
- Article marks:
  - `ARTICLE` creates or finds article threads by `/Title`, appends beads, transforms bead rectangles, and writes bead/thread objects later.
- Destination and document-view marks:
  - `DEST` writes named destinations into `pdev->Dests`.
  - `DOCVIEW` sets `/OpenAction` or writes catalog pairs.
- PostScript passthrough:
  - `PS` emits inline PostScript for small sources or wraps source/Level1 code as `/Subtype /PS` XObjects.
- Page/document metadata:
  - `PAGES`, `PAGE` write key/value pairs into the pages tree or current page dictionary.
  - `DOCINFO` writes info dictionary entries and rewrites `Producer` strings that contain `Distiller`.
  - `PAGELABEL` accumulates page-label number-tree entries.
- Named object operations:
  - `BP`/`EP` create and close Form XObjects.
  - `SP` paints a named Form XObject.
  - `OBJ`, `PUT`, `.PUTDICT`, `.PUTSTREAM`, `APPEND`, `.PUTINTERVAL`, and `CLOSE` create and mutate named COS arrays/dicts/streams.
  - `NamespacePush`, `NamespacePop`, and `NI` manipulate named-object namespaces and image-reference stacks.
- Marked content and document structure:
  - `MP`, `DP`, `BMC`, `BDC`, `EMC`, `StRoleMap`, `StClassMap`, `StPNE`, `StBookmarkRoot`, `StPush`, `StPop`, `StPopAll`, `StBMC`, `StBDC`, `StOBJ`, `StAttr`, `StStore`, and `StRetrieve` are present as dispatchable stubs returning success without implementation.

## Important State and Dependencies

- Uses COS support from `gdevpdfo.h`, named-object lookup/replacement from `gdevpdfr.c`, and PDF output/resource helpers from `gdevpdfx.h`.
- Updates `gx_device_pdf` state including `next_page`, `max_referred_page`, `Dests`, `Catalog`, `Info`, `Pages`, `PageLabels`, `articles`, `outline_levels`, `outlines_id`, `local_named_objects`, `NI_stack`, `substream_Resources`, and current page annotations.
- Allocates COS dictionaries, arrays, streams, and PDF object IDs through the PDF writer allocator and object-reference helpers.
- Uses stream filters for pdfmark-created streams via `setup_pdfmark_stream_compression`.

## Notable Control Flow

- Destination construction flows through `pdfmark_make_dest`, which combines `/Page` and `/View`, supports `/Next` and `/Prev`, uses page object references for local destinations, and page indexes for remote GoToR actions.
- Named destination strings can be coerced from `(name)` to `/name` by `pdfmark_coerce_dest`, but the code explicitly notes missing escape handling.
- `pdfmark_process` allocates a temporary `pairs` array for every mark, possibly with `/_objdef` removed, then may call `pdf_replace_names` over arguments before dispatch.

## Risks and Edge Cases

- Several comments explicitly mark incomplete behavior, including destination escape handling and PostScript passthrough escape decoding.
- Document-structure and marked-content pdfmarks are accepted but not implemented, which may silently drop accessibility/structure semantics.
- Many parsers use fixed buffers and `sscanf`; malformed or oversized strings return `rangecheck`/`limitcheck`.
- Object/reference ownership is manual. Errors after partial COS allocation often return directly, so callers depend on broader PDF writer lifetime cleanup.
- `/Contents` newline normalization mutates copied dictionary storage in place and resizes it if needed.
- Outline count handling tolerates incorrect/incomplete trees at end-of-document but relies on manual depth/count invariants.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfo.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfo.c

## Purpose

`gdevpdfo.c` implements Ghostscript pdfwrite's internal COS object model: generic objects, arrays, dictionaries, streams, scalar/constant/object/resource values, serialization, equality checks, stream-piece storage, and a parameter-list writer that serializes Ghostscript parameters into COS dictionaries.

This is support code for PDF generation, not filesystem code.

## Main Object Model

- `cos_object_t` is the common base for all COS objects.
- Concrete types are selected by procedure tables:
  - `cos_generic_procs`
  - `cos_array_procs`
  - `cos_dict_procs`
  - `cos_stream_procs`
- `cos_value_t` stores:
  - scalar copied string values,
  - constant shared string values,
  - object references written as indirect `n 0 R`,
  - resource references written as `/R<n>`.
- Arrays use linked `cos_array_element_t` nodes sorted in decreasing index order.
- Dictionaries and stream dictionaries use linked `cos_dict_element_t` nodes.
- Streams use dictionary elements plus linked `cos_stream_piece_t` nodes that point into the PDF writer's temporary stream file.

## Key APIs

- Object lifetime and writing:
  - `cos_object_alloc`
  - `cos_become`
  - `cos_release`
  - `cos_free`
  - `cos_write`
  - `cos_write_object`
- Value helpers:
  - `cos_string_value`
  - `cos_c_string_value`
  - `cos_object_value`
  - `cos_resource_value`
  - `cos_value_free`
  - `cos_value_write`
- Array helpers:
  - `cos_array_alloc`
  - `cos_array_from_floats`
  - `cos_array_put`
  - `cos_array_put_no_copy`
  - `cos_array_add`
  - `cos_array_add_no_copy`
  - `cos_array_add_c_string`
  - `cos_array_add_int`
  - `cos_array_add_real`
  - `cos_array_add_object`
  - `cos_array_unadd`
  - `cos_array_element_first`
  - `cos_array_element_next`
- Dictionary helpers:
  - `cos_dict_alloc`
  - `cos_dict_put`
  - `cos_dict_put_no_copy`
  - `cos_dict_put_c_key*`
  - `cos_dict_put_string*`
  - `cos_dict_put_c_strings`
  - `cos_dict_move_all`
  - `cos_dict_find`
  - `cos_dict_find_c_key`
  - `cos_dict_elements_write`
  - `cos_dict_objects_write`
  - `cos_dict_objects_delete`
- Stream helpers:
  - `cos_stream_alloc`
  - `cos_stream_dict`
  - `cos_stream_length`
  - `cos_stream_add`
  - `cos_stream_add_bytes`
  - `cos_stream_add_stream_contents`
  - `cos_stream_release_pieces`
  - `cos_stream_elements_write`
  - `cos_stream_contents_write`
  - `cos_write_stream_alloc`
  - `cos_stream_from_pipeline`
  - `cos_write_stream_from_pipeline`

## Serialization Behavior

- Arrays are temporarily reordered into ascending index order for output, with missing indices emitted as `null`.
- Dictionaries are emitted as `<< key value ... >>`; stream dictionaries add `/Length` and then copy accumulated stream pieces.
- Indirect objects are written through `cos_write_object`, which opens a separate PDF object, serializes it, closes it, and marks it `written`.
- `cos_value_write_spaced` delegates scalar syntax to `pdf_write_value`, so PDF names, strings, arrays, dictionaries, encryption, and escaping remain centralized in `gdevpdfu.c`.

## Stream Storage

- Stream data is not kept in memory. `cos_stream_add` records byte ranges already written into `pdev->streams.strm`.
- `cos_stream_contents_write` copies those ranges to output, optionally applying object-specific encryption through ARC4.
- When writing from the same temporary file as the target, it uses `pdf_copy_data_safe`.
- `cos_write_stream_alloc` creates a write stream that forwards bytes into the PDF writer stream file and records the written byte ranges on close/filter flush.

## Parameter Writer

- `cos_param_list_writer_init` creates a `gs_param_list` implementation that writes typed parameters into a COS dictionary.
- `cos_param_put_typed` supports scalar printed parameter serialization plus int and float arrays. String/name arrays are explicitly not implemented and return `typecheck`.

## GC and Memory Ownership

- The file defines Ghostscript GC descriptors and enum/reloc procedures for COS objects, values, array elements, dict elements, and stream pieces.
- Scalar values and owned dictionary keys are heap-owned by the containing collection.
- Constant strings are not copied or freed.
- Non-ID object values are assumed singly referenced and may be freed through their containing value.
- Objects with IDs are manually managed, not reference counted.

## Risks and Edge Cases

- COS objects are not reference counted, so ownership discipline is central.
- Equality for streams assumes identical segmentation of stream pieces; comments state this is not generally true.
- `cos_dict_objects_delete` clears object IDs so later dictionary freeing also frees those objects; this is specialized and hazardous outside its intended close path.
- Several helper buffers are marked ad hoc.
- `cos_param_put_typed` has incomplete support for string/name arrays.
- Error paths can leave allocated objects attached to larger writer state for later cleanup.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfo.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfo.h

## Purpose

`gdevpdfo.h` declares the internal COS object API used by Ghostscript's pdfwrite driver. It defines the abstract and concrete object structures, value representation, procedure-table type model, ownership assumptions, and public functions implemented in `gdevpdfo.c`.

This header supports PDF generation internals, not filesystem functionality.

## Core Definitions

- Abstract types:
  - `cos_object_t`
  - `cos_stream_t`
  - `cos_dict_t`
  - `cos_array_t`
  - `cos_value_t`
  - `cos_object_procs_t`
  - `cos_type_t`
- Procedure table:
  - `release`
  - `write`
  - `equal`
- `cos_object_struct(...)` macro defines the shared layout for all COS objects:
  - `cos_procs`
  - `id`
  - `elements`
  - `pieces`
  - `pdev`
  - `pres`
  - `is_open`
  - `is_graphics`
  - `written`
  - `length`
  - `input_strm`

## Value Model

`cos_value_t` can hold:

- `COS_VALUE_SCALAR`: heap-allocated string.
- `COS_VALUE_CONST`: shared constant string.
- `COS_VALUE_OBJECT`: object written inline or as indirect reference.
- `COS_VALUE_RESOURCE`: object referenced as a resource name.

The header documents that COS objects are not reference counted. Objects without IDs are assumed to have one owner; objects with IDs are manually managed.

## Declared APIs

The header exposes:

- Object allocation and mutation:
  - `cos_object_alloc`
  - `cos_array_alloc`
  - `cos_array_from_floats`
  - `cos_dict_alloc`
  - `cos_stream_alloc`
  - `cos_become`
- Object writing/lifetime:
  - `cos_release`
  - `cos_write`
  - `cos_write_object`
  - `cos_free`
- Value construction:
  - `cos_string_value`
  - `cos_c_string_value`
  - `cos_object_value`
  - `cos_resource_value`
  - `cos_value_write`
  - `cos_value_free`
- Array mutation/enumeration:
  - `cos_array_put`
  - `cos_array_put_no_copy`
  - `cos_array_add*`
  - `cos_array_unadd`
  - `cos_array_element_first`
  - `cos_array_element_next`
- Dictionary mutation/lookup:
  - `cos_dict_put*`
  - `cos_dict_move_all`
  - `cos_dict_find`
  - `cos_dict_find_c_key`
  - `cos_dict_elements_write`
  - `cos_dict_objects_write`
  - `cos_dict_objects_delete`
- Stream operations:
  - `cos_stream_add`
  - `cos_stream_add_bytes`
  - `cos_stream_add_stream_contents`
  - `cos_stream_release_pieces`
  - `cos_stream_dict`
  - `cos_stream_elements_write`
  - `cos_stream_contents_write`
  - `cos_stream_length`
  - `cos_write_stream_alloc`
  - `cos_stream_from_pipeline`
  - `cos_write_stream_from_pipeline`
- Parameter-list bridge:
  - `cos_param_list_writer_t`
  - `cos_param_list_writer_init`

## Integration Notes

- Depends on Ghostscript `gsparam.h` and the forward-declared `gx_device_pdf`.
- Uses `pdf_resource_t`, `stream`, `gs_memory_t`, `gs_id`, and Ghostscript GC macros/types from surrounding pdfwrite headers.
- The `COS_OBJECT`, `CONST_COS_OBJECT`, `COS_OBJECT_VALUE`, `COS_RESOURCE_VALUE`, `COS_RELEASE`, `COS_WRITE`, `COS_WRITE_OBJECT`, and `COS_FREE` macros are central to how other files cast and manage these objects.

## Risks and Contract Constraints

- The header explicitly warns that COS objects are not reference-counted.
- `_c_` dictionary/string procedures do not copy C-string arguments; callers must ensure lifetime.
- `_no_copy` array/dictionary variants assume strings are already allocated by the same allocator and should be adopted.
- `is_open`, `is_graphics`, and `written` are lightweight state flags used for error checking and writer flow, not comprehensive object lifecycle safety.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfo.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfp.c

## Purpose

`gdevpdfp.c` implements get/put parameter handling for Ghostscript's PDF-writing device. It exposes real pdfwrite parameters, accepts write-only pseudo-parameters for `pdfmark` and DSC comments, enforces selected Distiller compatibility constraints, updates version/capability flags, and maps DSC metadata into PDF structures.

This is PDF device parameter plumbing, not filesystem code.

## Main Entry Points

- `gdev_pdf_get_params(gx_device *dev, gs_param_list *plist)`: writes current pdfwrite parameters to a parameter list, including `CoreDistVersion`, `CompatibilityLevel`, `.EmbedFontObjects`, `pdfmark`, `DSC`, and items from `pdf_param_items`.
- `gdev_pdf_put_params(gx_device *dev, gs_param_list *plist)`: reads/validates pdfwrite parameters or dispatches pseudo-parameters.
- `pdf_dsc_process(gx_device_pdf *pdev, const gs_param_string_array *pma)`: maps recognized DSC comments to PDF document/page state.

## Parameter Table

`pdf_param_items` maps many `gx_device_pdf` fields to parameter names, including:

- Distiller-style controls:
  - `PDFEndPage`
  - `PDFStartPage`
  - `Optimize`
  - `ParseDSCCommentsForDocInfo`
  - `ParseDSCComments`
  - `EmitDSCWarnings`
  - `CreateJobTicket`
  - `PreserveEPSInfo`
  - `AutoPositionEPSFiles`
  - `PreserveCopyPage`
  - `UsePrologue`
  - `OffOptimizations`
- Ghostscript-specific behavior:
  - `ReAssignCharacters`
  - `ReEncodeCharacters`
  - `FirstObjectNumber`
  - `CompressFonts`
  - `PrintStatistics`
  - `MaxInlineImageSize`
- Encryption:
  - `OwnerPassword`
  - `UserPassword`
  - `KeyLength`
  - `Permissions`
  - `EncryptionR`
  - `NoEncrypt`
- Viewer/OPDF/PDFX capabilities:
  - `ForOPDFRead`
  - `PatternImagemask`
  - `MaxClipPathSize`
  - `MaxShadingBitmapSize`
  - `MaxViewerMemorySize`
  - `HaveTrueTypes`
  - `HaveCIDSystem`
  - `HaveTransparency`
  - `OPDFReadProcsetPath`
  - `CompressEntireFile`
  - `PDFX`

## Pseudo-Parameter Flow

- If `pdfmark` is present:
  - `pdf_open_document` is called.
  - `pdfmark_process` handles the mark array.
  - Errors are signaled on the `pdfmark` parameter.
- If `DSC` is present:
  - `pdf_open_document` is called.
  - `pdf_dsc_process` handles DSC key/value pairs.
  - Errors are signaled on `DSC`.
- Real parameter validation is skipped for these pseudo-parameter-only calls.

## Real Parameter Handling

- Honors `LockDistillerParams`: if already locked and not being unlocked, most PDF-specific reset attempts are ignored.
- Enforces:
  - `.EmbedFontObjects == 1`
  - `CoreDistVersion == 5000`
  - `CompatibilityLevel` rounded/substituted to supported values.
  - `FirstObjectNumber` can only change before object IDs have advanced, or to the same value.
- Handles `ProcessColorModel` early because lower-level device parameter handling depends on it.
- Updates capability flags for `PDFX` and `ForOPDFRead`.
- Adjusts `pdev->version` based on compatibility and TrueType support.
- Reduces device resolution if page device dimensions exceed Acrobat coordinate limits.
- On failure, restores saved PDF-specific fields and color state.

## DSC Processing

Recognized DSC keys include:

- Document info:
  - `Creator` to `/Creator`
  - `Title` to `/Title`
  - `For` to `/Author`
- Orientation:
  - `Orientation`
  - `PageOrientation`
- Viewing orientation:
  - `ViewingOrientation`
  - `PageViewingOrientation`
- EPS and bounding boxes:
  - `EPSF`
  - `BoundingBox`
  - `PageBoundingBox`

DSC info is ignored entirely when `ParseDSCComments` is false. Creator/title/author are only written when `ParseDSCCommentsForDocInfo` or `PreserveEPSInfo` is enabled.

## Risks and Edge Cases

- The comment block lists many Distiller parameters/features that are incomplete or deferred.
- `pdf_dsc_process` parses with `sscanf` and silently continues on malformed bounding boxes/orientations.
- Compatibility coercion may surprise callers because unsupported values are rounded to nearby supported levels.
- Failure restoration copies fields by parameter-table offsets; fields outside that table are restored manually or may remain changed if not handled.
- `save_dev.saved_stroke_color` restoration appears to assign from `save_dev.saved_fill_color`, which is suspicious and worth review if this code is maintained.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfr.c

## Purpose

`gdevpdfr.c` implements named-object support for pdfmark processing. It validates pdfmark object-name syntax, creates and resolves named COS objects, manages local/global namespaces, scans serialized PostScript/PDF-like parameter strings, and replaces `{object}` references with PDF indirect object references.

This is PDF writer support code, not filesystem functionality.

## Main APIs

- `pdf_objname_is_valid(const byte *data, uint size)`: validates `{name}` syntax.
- `pdf_find_named(...)`: looks in local then global named-object dictionaries.
- `pdf_create_named(...)`: creates a named or anonymous generic/COS object, optionally assigning an object ID.
- `pdf_create_named_dict(...)`: convenience creator for dictionaries.
- `pdf_refer_named(...)`: resolves an object or creates a forward reference. It also maps predefined page names such as `{ThisPage}`, `{NextPage}`, `{PrevPage}`, and `{PageN}` to page dictionaries.
- `pdf_make_named(...)`: creates or completes a forward-referenced object of a required type.
- `pdf_make_named_dict(...)`: dictionary variant.
- `pdf_get_named(...)`: resolves a named object and verifies its type.
- `pdf_push_namespace(...)`: pushes current local named-object dictionary and NI stack, then creates fresh local ones.
- `pdf_pop_namespace(...)`: restores the previous local named-object dictionary and NI stack.
- `pdf_scan_token(...)`: scans one token from a parameter string.
- `pdf_scan_token_composite(...)`: scans a composite token such as an array/dictionary as one logical token.
- `pdf_replace_names(...)`: replaces embedded `{name}` references with `n 0 R` strings.

## Named Object Semantics

- Local namespace lookup takes precedence over global lookup.
- Missing non-page names become generic forward-reference objects.
- Page aliases resolve to actual page dictionaries and allocate page IDs as needed.
- `pdf_make_named` rejects attempts to redefine a non-generic object.
- Forward references can be mutated in place from generic to array/dict/stream through `cos_become`.

## Scanner Behavior

- The scanner is PostScript-like, not full PDF syntax.
- Special tokens include `<<`, `>>`, `[`, `]`, `{`, `}`.
- String tokens are skipped with `PSSD` decoding logic.
- Hex strings are scanned to the next `>`.
- It recognizes a Ghostscript extension where names preceded by two null bytes can include non-regular characters until a null terminator.
- Syntax errors are mapped to `gs_error_syntaxerror`, falling back to `rangecheck` when unavailable.

## Name Replacement Flow

- `pdf_replace_names` first scans the full string to compute output size.
- It calls `pdfmark_next_object`, which finds composite `{...}` object references and attempts to resolve them.
- Resolution failures leave the original text unchanged for that reference.
- If replacements are needed, it allocates a new buffer and emits ` <id> 0 R ` around each resolved object ID.

## Risks and Edge Cases

- Scanning is deliberately minimal and not a complete PDF parser.
- Malformed tokens during replacement are skipped by advancing one byte, so bad strings can be partially processed.
- `pdf_replace_names` sets `to->persistent = true`, but ownership of allocated replacement memory depends on later caller cleanup.
- Namespace push/pop assumes the namespace stack remains balanced and ordered as NI stack then local-name dictionary.
- `pdf_pop_namespace` frees current local dictionaries before restoring previous ones; misuse can invalidate active references.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdft.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdft.c

## Purpose

`gdevpdft.c` handles PDF 1.4 transparency compositor operations for the pdfwrite driver. It converts Ghostscript PDF14 transparency group and soft-mask operations into PDF group dictionaries, Form XObjects, soft-mask dictionaries, and page group references when transparency output is enabled.

This is graphics/PDF emission code, not filesystem code.

## Main Entry Point

- `gdev_pdf_create_compositor(...)`: intercepts `GX_COMPOSITOR_PDF14_TRANS` operations when `HaveTransparency` is true and `CompatibilityLevel >= 1.4`; otherwise delegates to `psdf_create_compositor`.

Handled PDF14 operations:

- `PDF14_PUSH_DEVICE`
- `PDF14_POP_DEVICE`
- `PDF14_BEGIN_TRANS_GROUP`
- `PDF14_END_TRANS_GROUP`
- `PDF14_INIT_TRANS_MASK`
- `PDF14_BEGIN_TRANS_MASK`
- `PDF14_END_TRANS_MASK`
- `PDF14_SET_BLEND_PARAMS`

## Transparency Group Flow

- `pdf_make_group_dict` creates a `/Group` dictionary resource with:
  - `/Type /Group`
  - `/S /Transparency`
  - optional `/I true`
  - optional `/K true`
  - optional `/CS` based on current graphics-state color space.
- `pdf_begin_transparency_group`:
  - opens the current page/stream,
  - emits pending clip path if necessary,
  - for page-level groups stores `group_id` on the current page,
  - for nested groups prepares graphics state, enters an XObject substream, and writes a Form XObject dictionary through `pdf_make_form_dict`.
- `pdf_end_transparency_group`:
  - leaves page-level groups open for page finalization,
  - or closes nested substreams, substitutes/deduplicates the XObject resource, and emits `/Rname Do`.

## Soft Mask Flow

- `pdf_make_soft_mask_dict` creates a soft-mask dictionary resource with:
  - `/S /Alpha` or `/S /Luminosity`
  - optional `/BC`
  - optional `/TR` transfer function reference.
- `pdf_begin_transparency_mask`:
  - for image masks sets `pdev->image_mask_skip` to avoid installing a transparency buffer while still allowing image enumeration.
  - for non-image masks creates a soft-mask dictionary and begins a transparency group.
- `pdf_end_transparency_mask`:
  - clears `image_mask_skip` for image masks.
  - for non-image masks closes the group XObject, records it as `/G` in the soft-mask dictionary, substitutes the soft-mask resource, and stores the resulting ID in `pis->soft_mask_id`.

## Additional Functions

- `pdf_make_form_dict` writes Form XObject keys such as `/Type /XObject`, `/Subtype /Form`, `/FormType 1`, `/Matrix`, `/BBox`, and `/Group`.
- `pdf_set_blend_params` is a stub returning success.
- Device transparency method stubs:
  - `gdev_pdf_begin_transparency_group`
  - `gdev_pdf_end_transparency_group`
  - `gdev_pdf_begin_transparency_mask`
  - `gdev_pdf_end_transparency_mask`
  - `gdev_pdf_discard_transparency_layer`

## Risks and Limitations

- Blend parameter setting is not implemented.
- Several device methods are stubs because comments say they are apparently never called.
- Image soft-mask handling intentionally enumerates mask images without creating a reference, relying on later duplicate-image recognition.
- Error paths around resource substitution can return success in one case after `pdf_substitute_resource` fails in `pdf_end_transparency_mask`, which is suspicious.
- Transparency is gated on PDF 1.4 compatibility and `HaveTransparency`; lower compatibility falls back to the generic psdf compositor.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdft.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfu.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfu.c

## Purpose

`gdevpdfu.c` is a broad utility layer for Ghostscript's PDF-writing driver. It handles document opening, object IDs and xref position recording, page content state transitions, compression/encryption filters, resource allocation/deduplication, page resource dictionaries, low-level PDF value writing, data-stream setup, Function object creation, procset copying, and miscellaneous helpers.

This is PDF output infrastructure, not filesystem/VFS code.

## Document and Object Lifecycle

- `pdf_open_document` writes optional OPDFRead procsets and the `%PDF-x.y` header, sets binary output behavior, and selects page compression.
- `pdf_stell` reports logical output position, accounting for the asides stream base.
- `pdf_obj_ref` reserves object IDs and records xref positions.
- `pdf_open_obj`, `pdf_begin_obj`, and `pdf_end_obj` emit object wrappers.
- `pdf_open_separate`, `pdf_begin_separate`, and `pdf_end_separate` temporarily switch to the asides stream for resources, annotations, and other non-content objects.

## Page Content Context Management

- `pdf_open_contents` transitions among:
  - `PDF_IN_NONE`
  - `PDF_IN_STREAM`
  - `PDF_IN_TEXT`
  - string/text context.
- Transition helpers open content streams, set page compression/encryption, emit initial coordinate scaling, begin/end text objects, and close streams.
- `pdf_close_contents` closes active content context and emits the final `Q` for the initial page `q`.
- `pdf_open_page` ensures the document and current page dictionary exist before opening requested context.
- `pdf_unclip` restores viewer state out of clipping contexts and returns to unclipped stream context.

## Encryption and Value Writing

- `pdf_object_key` derives per-object ARC4 keys from the document encryption key and object ID.
- `pdf_encrypt_init`, `pdf_begin_encrypt`, and `pdf_end_encrypt` manage encryption filter setup/removal.
- `pdf_put_name_chars`, `pdf_put_name`, `pdf_put_string`, and `pdf_write_value` serialize PDF names, strings, arrays, dictionaries, and scalar values.
- `pdf_put_composite` selectively encrypts string tokens inside serialized arrays/dictionaries.
- `pdf_put_encoded_hex_string` is explicitly unimplemented and returns an error after writing a diagnostic.

## Resource Management

- Resource type names and struct descriptors are declared through `pdf_resource_type_names` and `pdf_resource_type_structs`.
- Allocation/opening:
  - `pdf_alloc_aside`
  - `pdf_begin_aside`
  - `pdf_begin_resource_body`
  - `pdf_begin_resource`
  - `pdf_alloc_resource`
  - `pdf_reserve_object_id`
- Deduplication and cleanup:
  - `pdf_find_resource_by_gs_id`
  - `pdf_find_resource_by_resource_id`
  - `pdf_find_same_resource`
  - `pdf_substitute_resource`
  - `pdf_cancel_resource`
  - `pdf_forget_resource`
  - `pdf_drop_resources`
  - `pdf_write_resource_objects`
  - `pdf_free_resource_objects`
  - `pdf_write_and_free_all_resource_objects`
- Page resource collection:
  - `pdf_store_page_resources` writes per-page resource dictionaries for resources used by the current `used_mask`.

## Stream and Filter Helpers

- `pdf_copy_data` and `pdf_copy_data_safe` copy temporary stream data to output, optionally encrypting.
- `pdf_put_filters` inspects a stream filter pipeline and writes `/Filter` and `/DecodeParms` entries for ASCII85, CCITTFax, DCT, Flate, LZW, PNG predictor, and RunLength filters.
- `pdf_flate_binary` chooses LZW for older compatibility and Flate for newer output.
- `pdf_begin_data`, `pdf_begin_data_stream`, `pdf_append_data_stream_filters`, and `pdf_end_data` set up and finalize data streams, including binary, compression, ASCII85, encryption, and length handling.

## Page Helpers

- `pdf_page_id` grows the page array, creates page dictionaries, and reserves page object IDs.
- `pdf_current_page` returns the current page state.
- `pdf_current_page_dict` ensures and returns the current page dictionary.
- `pdf_write_saved_string` writes and frees saved strings.

## Function Objects

- `pdf_function_scaled` creates a scaled function wrapper when output ranges require it.
- `pdf_function_aux` builds COS dictionary/stream/array representations for Ghostscript functions, including sampled-function data streams and nested function arrays.
- `pdf_function` deduplicates function resources and returns a COS object value.
- `pdf_write_function` writes or resolves a Function object ID.
- `pdf_write_font_bbox` writes `/FontBBox`, expanding empty boxes to avoid Acrobat Reader display problems.

## Procset Support

- `copy_ps_file_stripping`, `copy_procsets`, and `doit` strip comments/whitespace from PostScript procset files and optionally skip TrueType-specific sections.
- `pdf_open_document` uses these when `ForOPDFRead` and `OPDFReadProcsetPath` are enabled.

## Risks and Edge Cases

- Many operations depend on manual stream switching between main/asides/temporary streams.
- `pdf_put_encoded_hex_string` is not implemented.
- Encryption is split: temporary stream data is not encrypted until copied to final output.
- Resource deduplication relies on COS equality; stream equality assumes comparable segmentation in `gdevpdfo.c`.
- Several fixed-size buffers are used for names, filter strings, and function data chunks.
- Resource lifecycle is manual and cross-linked through hash chains and `last_resource`.
- Comments note legacy or compatibility workarounds for Acrobat coordinate limits, Acrobat Reader 4 behavior, and OPDFRead procset compression.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfv.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfv.c

## Purpose

`gdevpdfv.c` writes color-related high-level PDF constructs for pdfwrite, especially PatternType 1 tiling patterns, PatternType 2 shading patterns, mesh shading streams, and named color-space inclusion.

This is PDF graphics output code, not filesystem code.

## PatternType 1 Tiling Patterns

- `pdf_pattern` creates a `/Pattern` resource as a stream that paints an image XObject:
  - validates Acrobat image-pattern size constraints,
  - checks that pattern steps align with coordinate axes,
  - creates a resource dictionary containing the image XObject,
  - writes `/PatternType 1`, `/PaintType`, `/TilingType`, `/Resources`, `/BBox`, `/Matrix`, `/XStep`, and `/YStep`,
  - writes `/R<image-id> Do` as pattern stream contents.
- `pdf_store_pattern1_params` stores pattern dictionary fields for high-level pattern streams and sets up `pdev->substream_Resources`.
- `pdf_set_pattern_image` initializes image matrix/size from tile dimensions.
- `pdf_put_pattern_mask` writes a 1-bit mask image for pattern masks, inverting Y because pattern masks are device-coordinate based.

## Colored and Uncolored Pattern Output

- `pdf_put_uncolored_pattern`:
  - can optimize an all-ones uncolored pattern into a pure color when pattern streams are unavailable.
  - otherwise creates or locates a pattern resource and emits the Pattern color space selection.
  - includes an Acrobat Reader 4 stack workaround for some uncolored pattern stream cases.
- `pdf_put_colored_pattern`:
  - detects masked pure-color cases and delegates to `pdf_put_uncolored_pattern`.
  - rejects masked colored patterns for PDF versions before 1.3.
  - writes image and optional mask XObjects, attaches `/Mask`, creates the pattern, or finds a high-level pattern resource.
  - emits colored Pattern color-space selection.

## PatternType 2 and Shadings

- `pdf_put_shading_common` writes shared shading dictionary keys:
  - `/ShadingType`
  - optional `/AntiAlias`
  - `/ColorSpace`
  - optional `/Background`
  - optional `/BBox`
- `pdf_put_shading_Function` writes optional `/Function` using `pdf_function_scaled`.
- `pdf_put_linear_shading` writes `/Coords`, optional `/Domain`, optional `/Function`, and optional `/Extend`.
- `pdf_put_scalar_shading` handles Function-based, Axial, and Radial shadings.
- `pdf_put_mesh_shading` handles mesh shading stream parameters and data:
  - Free-form Gouraud triangle
  - Lattice-form Gouraud triangle
  - Coons patch
  - Tensor-product patch
- `put_float_mesh_data` converts array-backed floating-point mesh data into packed binary with fixed bit widths.
- `pdf_put_pattern2` creates a Pattern resource plus Shading resource, writes scalar or mesh shading representation, computes the pattern matrix in default user coordinates, and emits the Pattern color-space selection.

## Mesh Encoding Details

- Coordinates are limited to a 14-bit-safe Acrobat-compatible range and encoded into 24-bit coordinate fields.
- Color components are encoded into 16-bit component fields.
- Flags are encoded as 8-bit fields for array-backed mesh data.
- For stream-backed mesh data, existing stream contents and decode parameters are copied rather than repacked.

## Other API

- `gdev_pdf_include_color_space` includes a named color-space resource through `pdf_color_space_named`.

## Dependencies and State

- Uses Ghostscript color, pattern, image, shading, and matrix types.
- Depends heavily on image writer helpers from other pdfwrite files, COS helpers from `gdevpdfo`, color-space helpers from `gdevpdfg`, and function writing from `gdevpdfu`.
- Updates PDF resources of types Pattern and Shading, current stream output, and some pdfwrite compatibility flags.

## Risks and Limitations

- Null patterns are explicitly not handled.
- Image patterns are rejected if image/mask data exceeds about 64 KiB due to Acrobat Reader limitations.
- Pattern steps must be axis-aligned; non-axis-aligned steps return `rangecheck`.
- Comments note unscaled `/Background` and `/Decode` cases.
- Mesh packing uses fixed ranges and clamping, so out-of-range geometry/color data is saturated.
- High-level pattern stream resource lookup assumes matching IDs and may return substituted pattern resources.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfv.c -->