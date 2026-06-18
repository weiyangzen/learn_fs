# Group Research: group_1585_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_zarith_c_sources_os_1d3b083f12f5

Scope checked against `Docs/research_subset_a.md`: `sources/os/plan9/plan9` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zarith.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zarith.c

Implements Ghostscript PostScript arithmetic operators: `abs`, `add`, `.bitadd`, `ceiling`, `div`, `idiv`, `floor`, `mod`, `mul`, `neg`, `round`, `sub`, and `truncate`.

Key behavior:
- `zop_add` and `zop_sub` are exported helper paths used directly by the interpreter and FunctionType 4 code.
- Integer operations preserve integer results when possible, converting to real on detected overflow for `add`, `sub`, `mul`, and `neg(MIN_INTVAL)`.
- `div` always returns real quotient and checks divide-by-zero; `idiv` and `mod` require integer operands and reject zero divisors.
- Rounding operators accept integer or real operands and leave integers unchanged.
- `.bitadd` is a non-standard integer-only addition without overflow conversion.

Dependencies and coupling:
- Uses operand-stack refs from `oper.h` and typed constructors/checks from `store.h`.
- Depends on `math_.h` for `ceil` and `floor`.
- Explicit file note says arithmetic operators do not currently check floating exceptions.

<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zarith.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zarray.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zarray.c

Implements core PostScript array operators `array`, `aload`, and `astore`; generic array operators are delegated to `zgeneric.c`.

Key behavior:
- `array` validates requested size against `max_array_size`, allocates a ref array with `ialloc_ref_array`, and initializes all slots to null.
- `aload` supports normal and packed arrays. If the current operand stack segment lacks room, it uses `ref_stack_push` and `packed_get` to handle segmented stacks safely.
- `astore` validates writable arrays, stores operand-stack values into the target array, and handles cross-stack-segment stores with `ref_stack_store`.
- For same-segment `astore`, it uses `refcpy_to_old` to preserve VM write-barrier behavior.

Dependencies and coupling:
- Uses interpreter allocator APIs (`ialloc.h`), packed array support (`ipacked.h`), ref-stack utilities, and VM-aware store helpers.
- Important for GC correctness because array writes use old-object assignment helpers.

<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zarray.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zbfont.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zbfont.c

Provides common font construction utilities and the Type 3 `.buildfont3` operator.

Key behavior:
- `.buildfont3` validates a font dictionary, extracts `BuildChar`/`BuildGlyph`, builds a user-defined base font, and registers it.
- `zfont_encode_char` maps character codes through `Encoding`; for non-conforming Type 3 fonts with `.notdef`, it may synthesize glyph names for high-level devices.
- `zfont_glyph_name` resolves normal glyph names or fabricates numeric names for CID glyphs.
- `gs_font_map_glyph_to_unicode` maps glyphs through `FontInfo/GlyphNames2Unicode` and fallback Unicode decoding resources.
- `build_gs_primitive_font`, `build_gs_outline_font`, `build_gs_simple_font`, `build_gs_font`, and `build_gs_sub_font` fill Ghostscript `gs_font` structures from PostScript dictionaries.
- Handles `CharStrings`, `FontBBox`, UID validation, `PaintType`, `StrokeWidth`, `Encoding`, bitmap width policy, `WMode`, `FID`, `FontMatrix`, aliases, and original font names.
- `lookup_gs_simple_font_encoding` compares a font encoding with known built-in encodings and records exact/nearest matches.

Dependencies and coupling:
- Central bridge between interpreter dictionaries/refs and graphics-library font objects.
- Shares `font_data` refs with character rendering modules (`zchar*.c`).
- Uses VM spaces carefully when allocating font data and when storing dictionary refs.

<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zbfont.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zbseq.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zbseq.c

Implements Level 2 binary object sequence support.

Key behavior:
- Defines `names_array_ref_t`, a GC-visible wrapper around a names array ref.
- `create_names_array` allocates system/user name table refs in stable memory and initializes them as readonly empty arrays.
- Initialization installs a fake system name table until PostScript setup installs the real one.
- `.installsystemnames` accepts only a global shortarray at global save level 0, then replaces `system_names_p`.
- `currentobjectformat` and `setobjectformat` expose and mutate the binary object format, accepting only values 0 through 4.
- `.bosobject` encodes one object into binary object-sequence representation using `encode_binary_token`, updating ref/char offsets and returning an 8-byte string slice.

Dependencies and coupling:
- Uses binary-token machinery from `btoken.h`.
- Uses stable/global memory and old-ref assignment to keep name tables GC-safe.

<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zbseq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcfont.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcfont.c

Implements composite-font-specific character operators `cshow` and `rootfont`.

Key behavior:
- `cshow` accepts operands in either documented or Adobe-compatible reversed order, sets up a `gs_cshow` text enumerator, and stores the user procedure in `sslot`.
- `cshow_continue` processes text until intervention. On each intervention it pushes character code plus width, constructs an appropriate scaled leaf font, temporarily sets currentfont, and executes the user procedure.
- `cshow_restore_font` restores both root font and current font before continuing.
- `rootfont` returns the current root font dictionary.

Dependencies and coupling:
- Uses `zchar.c` show setup/finish helpers and estack slots.
- Depends on font stack details from `gs_text_enum_t` and on `gs_makefont` for scaled leaf font creation.
- Important for composite fonts because it preserves root/current font distinction during callback execution.

<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcfont.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zchar.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zchar.c

Implements core PostScript text operators and shared show-enumerator control flow.

Key behavior:
- Operators include `show`, `ashow`, `widthshow`, `awidthshow`, `kshow`, `stringwidth`, `charpath`, `.charboxpath`, `setcachedevice`, `setcachedevice2`, `setcharwidth`, and `.fontbbox`.
- `finish_stringwidth` pushes accumulated text width and is reused by `.glyphwidth`.
- `op_show_finish_setup` records show state on the execution stack, including operand/dictionary stack depths, graphics state level, saved fonts, end procedure, and text enumerator.
- `op_show_continue_dispatch` handles normal completion, kshow intervention, character rendering through `BuildChar`/`BuildGlyph`, and CID/TrueType CDevProc cache setup.
- `op_show_return_width` short-circuits BuildChar/BuildGlyph execution when only width is needed and the font type is safe.
- `op_show_restore` frees text enumerators, restores currentfont, unwinds extra gstates, frees replacement-width arrays, and repairs stacks on error.
- `font_bbox_param` tolerates missing/invalid FontBBox and filters unreasonable boxes.

Dependencies and coupling:
- Central runtime used by `zcfont.c`, `zcharx.c`, `zchar1.c`, `zchar42.c`, and `zcharout.c`.
- Couples PostScript procedures with `gs_text_enum_t` and graphics-library text processing.
- Handles CID cshow special cases and composite-font current glyph propagation.

<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zchar.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zchar1.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zchar1.c

Implements Type 1 character display and shared CharString execution for Type 1, Type 2, disk-based, and CID Type 0 paths.

Key behavior:
- `.type1execchar` delegates to `charstring_execchar` with Type 1/disk font masks.
- `charstring_execchar` validates current show context, handles PostScript-procedure glyph definitions, initializes Type 1 interpretation, extracts metrics, and chooses FontBBox or no-FontBBox rendering paths.
- The bbox path sets cache device early using FontBBox and metrics; if the drawn path exceeds FontBBox, it enlarges FontBBox and retries.
- The no-bbox path builds the path first, derives bbox from the path, then sets cache device; anti-aliased rendering may rebuild the path after cache setup.
- Supports unknown `OtherSubrs` by moving Type 1 interpreter state to the heap, pushing saved arguments/procedures onto the estack, and resuming later.
- `zsetweightvector` sets multiple-master weight vectors for Type 1/2 fonts.
- Exposes `z1_data_procs` for glyph data, subr data, seac data, and Type 1 push/pop callbacks.
- `zchar1_glyph_outline`, `zcharstring_outline`, `z1_glyph_info`, and `z1_set_cache` provide outline, metrics, and cache services for higher-level font code.

Dependencies and coupling:
- Depends heavily on `gxtype1`, `gxfont1`, `ichar1`, and `icharout`.
- Shares cache setup through `zcharout.c`.
- Contains compatibility choices for fill rule, stroke width, FontBBox-as-Metrics2, and Adobe behavior around stroked fonts.

<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zchar1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zchar2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zchar2.c

Provides the Type 2 character display operator.

Key behavior:
- `.type2execchar` calls the shared `charstring_execchar` implementation from `zchar1.c`, restricted to `ft_encrypted2`.
- The file intentionally contains only the thin Type 2 dispatch layer.

Dependencies and coupling:
- Requires `ichar1.h` for `charstring_execchar`.
- All substantive Type 2 CharString execution behavior is inherited from `zchar1.c`.

<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zchar2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zchar32.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zchar32.c

Implements Type 32 bitmap CID font glyph support.

Key behavior:
- `.makeglyph32` encodes bitmap glyph metrics into compact glyph strings. It supports 6-value WMode 0 metrics or 10-value dual-WMode metrics.
- Uses a short 5-byte metrics form when dimensions and offsets fit byte-sized constraints; otherwise uses 14- or 22-byte long forms.
- Validates bitmap size against calculated raster and bounding box dimensions.
- `.getmetrics32` decodes short and long forms, pushing width, height, metrics values, and consumed metrics-string size.
- `.removeglyphs` purges cached glyphs for a CID range in a Type 32 bitmap font.

Dependencies and coupling:
- Uses `gx_purge_selected_cached_chars` to invalidate font cache entries.
- Assumes CID bitmap fonts and 16-bit CID inputs.
- Metrics encoding is private to Type 32 font machinery.

<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zchar32.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zchar42.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zchar42.c

Implements Type 42 / TrueType character display and cache setup.

Key behavior:
- `zchar42_set_cache` obtains metrics from PostScript `Metrics` when available, otherwise from TrueType glyph metrics via `gs_type42_wmode_metrics`.
- Handles vertical writing mode, including fallback vertical metrics for CID TrueType fonts derived from FontBBox.
- `.type42execchar` validates TrueType/CID TrueType show context, sets stroke width for stroked fonts, handles procedure glyph definitions, establishes current point, and calls cache setup.
- `type42_finish` appends the TrueType glyph outline to the current path with `gs_type42_append`, then fills or strokes.
- Fill path temporarily sets `fill_adjust` to `-1,-1`; stroke path uses `gs_stroke`.

Dependencies and coupling:
- Shares cache setup with `zcharout.c` and show context with `zchar.c`.
- Exports `zchar42_set_cache` for CID CDevProc handling in `zchar.c`.

<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zchar42.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zchar42.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zchar42.h

Declares the Type 42 cache setup helper.

Key behavior:
- Provides include guard `zchar42_INCLUDED`.
- Declares `zchar42_set_cache(i_ctx_t *, gs_font_base *, ref *, uint glyph_index, op_proc_t cont, op_proc_t *exec_cont, bool put_lsb)`.

Dependencies and coupling:
- Used by `zchar.c` to set caches for CID TrueType CDevProc paths and by `zchar42.c` as the implementation contract.

<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zchar42.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcharout.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcharout.c

Contains shared outline-font support for Type 1, Type 4, and Type 42 rendering.

Key behavior:
- `zchar_exec_char_proc` executes procedure-defined outlines inside `systemdict` and font dictionary `begin`/`end` wrappers.
- `zchar_get_metrics` reads `Metrics` entries, accepting width-only, `[sbx wx]`, and `[sbx sby wx wy]` forms.
- `zchar_get_metrics2` reads vertical `Metrics2` arrays.
- `zchar_get_CDevProc` detects a font `CDevProc`.
- `zchar_set_cache` computes cache device parameters, expands bbox for stroked fonts, applies Metrics2/default vertical metrics, and either calls `setcachedevice[2]` directly or schedules CDevProc/setcachedevice through the estack.
- `zchar_charstring_data` fetches glyph CharStrings and special-cases ADOBEPS4 `.notdef` procedures by synthesizing a minimal encrypted or unencrypted Type 1 CharString.
- `zchar_enumerate_glyph` enumerates glyph names or CID integers from a dictionary.

Dependencies and coupling:
- Provides the common cache and metrics layer used by `zchar1.c`, `zchar42.c`, and font embedding/outline code.
- Important for VM/GC safety because generated `.notdef` CharString data is allocated in font memory and attached to glyph data.

<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcharout.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcharx.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcharx.c

Implements Level 2 character operators `glyphshow`, `.glyphwidth`, `xshow`, `yshow`, and `xyshow`.

Key behavior:
- `glyph_show_setup` accepts integer CIDs for CID fonts and names for non-CID fonts, converting to a `gs_glyph`.
- `glyphshow` begins a glyph show enumerator and reuses the generic show continuation pipeline.
- `.glyphwidth` begins a glyph-width enumerator and finishes through `finish_stringwidth`.
- `moveshow` converts numeric arrays/strings into a temporary float array and calls `gs_xyshow_begin` with x and/or y displacements.
- Temporary movement arrays are freed on setup errors; successful ownership passes to the text enumerator path.

Dependencies and coupling:
- Level 2 operator table only.
- Reuses `op_show_enum_setup`, `op_show_finish_setup`, and `op_show_continue` from `zchar.c`.
- Uses binary number array helpers from `ibnum.h`.

<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcharx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcid.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcid.c

Provides CMap and CID-keyed font utility routines.

Key behavior:
- `cid_system_info_param` extracts and validates `Registry`, `Ordering`, and `Supplement` from `CIDSystemInfo`.
- `TT_char_code_from_CID_no_subst` maps a CID through a `Decoding` dictionary and optional TrueType cmap array.
- `cid_to_TT_charcode` applies `SubstNWP` substitution ranges bidirectionally when direct CID mapping fails, returning source/destination substitution type refs.
- `set_CIDMap_element` stores 2-byte glyph indices into segmented string arrays representing a CIDMap.
- `cid_fill_CIDMap` validates `GDBytes == 2`, validates CIDMap array-of-strings structure, enumerates `Decoding`, resolves glyph indices with substitutions, and fills the CIDMap.

Dependencies and coupling:
- Used by CIDFont/CMap construction code rather than exposed directly as an operator table.
- Assumes `GDBytes == 2` and array-based CIDMap; other forms return `e_unregistered`.

<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcidtest.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcidtest.c

Implements internal/testing operators for CIDFont and CMap facilities.

Key behavior:
- `.wrapfont` wraps the current Type 42 or CID font into a Type 0 composite font. For Type 42 fonts, it patches `CIDMap` and `BuildGlyph` to suit PostScript-implemented BuildChar behavior.
- `.writecmap` serializes a CMap dictionary’s `CodeMap` to a writable file with `psf_write_cmap`.
- `.writefont9` serializes a CIDFontType 0 encrypted font using `psf_write_cid0_font`.

Dependencies and coupling:
- Uses font serialization support from `gdevpsf.h`.
- Intended as test/support functionality, not general user-facing PostScript behavior.

<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcidtest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcie.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcie.c

Implements Level 2 CIE color-space operators and CIE procedure-cache setup.

Key behavior:
- Provides dictionary parameter helpers for ranges, procedure arrays, 3x3 matrices, white/black points, and 3D/4D lookup tables.
- `.setcieaspace`, `.setcieabcspace`, `.setciedefspace`, and `.setciedefgspace` build CIE color spaces, extract PostScript decode procedures, allocate lookup tables, prepare sampled caches, and set the graphics color space.
- `cie_set_finish` installs the color space, releases temporary references, records interpreter-side CIE procedures, and handles continuation completion.
- `cie_prepare_cache` pushes a sampling loop through the estack using `zfor_samples`; finish operators copy sampled results into `cie_cache_floats`.
- Finish callbacks replace decode functions with cache-backed implementations and call `gs_cie_*_complete`.

Dependencies and coupling:
- Bridges PostScript CIE dictionaries/procedures with graphics-library `gs_cie_*` structures.
- Uses estack continuations because arbitrary PostScript decode procedures must be sampled before the C color space can be completed.
- Careful about freeing color-space objects after `gs_setcolorspace` copies them.

<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcie.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcolor.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcolor.c

Implements core color, colorspace, transfer, and color-device test operators.

Key behavior:
- `currentcolor` pushes numeric components and optional pattern dictionary/null for pattern color spaces; integral values are pushed as integers.
- `currentcolorspace` returns the interpreter-tracked colorspace array and normalizes DeviceGray fallback behavior.
- `.getuseciecolor` reads interpreter `UseCIEColor` state.
- `setcolor` gathers numeric and optional pattern operands and calls `gs_setcolor`.
- `setcolorspace` records the nominal PostScript colorspace array; `.setdevcspace` installs DeviceGray/RGB/CMYK in the graphics state.
- `currenttransfer`, `settransfer`, and shared remapping helpers sample PostScript transfer procedures into graphics transfer maps via estack sampling loops.
- `.color_test` and `.color_test_all` exercise device encode/decode color behavior and report worst errors through debug output.
- `.includecolorspace` asks the graphics layer whether a named colorspace should be included for high-level device output.

Dependencies and coupling:
- Shared remap helpers are used by `zcolor1.c`.
- Uses `zfor_samples` and estack continuations to sample procedures.
- Maintains interpreter-side refs for transfer procedures and pattern dictionaries in `istate`.

<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcolor.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcolor1.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcolor1.c

Implements Level 1 extended color transfer operators.

Key behavior:
- `currentblackgeneration`, `currentcolortransfer`, and `currentundercolorremoval` return interpreter-stored procedure refs.
- `setblackgeneration` installs a black-generation procedure, asks the graphics state to use mapped transfer, and samples the procedure with `zcolor_remap_one`.
- `setcolortransfer` installs red/green/blue/gray transfer procedures and samples all four maps before resetting effective transfer.
- `setundercolorremoval` installs UCR and samples it with signed output support.

Dependencies and coupling:
- Reuses `zcolor_remap_one`, `zcolor_remap_color`, and `zcolor_reset_transfer` from `zcolor.c`.
- Uses estack continuations because transfer procedures are arbitrary PostScript procedures sampled into fixed-size maps.

<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcolor1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcolor2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcolor2.c

Implements a small Level 2 color helper.

Key behavior:
- `.usealternate` returns true when the current color space has and uses a base/alternate color space, as detected by `cs_base_space`.

Dependencies and coupling:
- Level 2-only operator table.
- Relies on graphics color-space inspection from `gxcspace.h` / `gscolor2.h`.

<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcolor2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcolor3.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcolor3.c

Implements the Level 3 `UseCIEColor` setter.

Key behavior:
- `.setuseciecolor` stores the supplied boolean ref into `istate->use_cie_color` and pops it.
- Operator is Level 3-only and intended for controlled initialization/setpagedevice paths, so it does no operand checking.

Dependencies and coupling:
- Complements `.getuseciecolor` in `zcolor.c`.
- Keeps `UseCIEColor` cached in interpreter state for fast checks and language-level-specific behavior.

<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcolor3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcontext.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcontext.c

Implements Display PostScript context, scheduler, lock, condition, monitor, fork/join, yield, and context-aware `usertime` operators.

Key behavior:
- Defines `gs_context_t`, `gs_scheduler_t`, locks, conditions, context lists, and GC descriptors.
- Initialization hooks interpreter reschedule/time-slice callbacks, creates a scheduler in system memory, wraps VM reclaim, and creates the initial context.
- Scheduler keeps active contexts by index, supports time slicing, handles dead-context destruction, and enforces local-VM save-level restrictions so contexts sharing local VM cannot run while another has unmatched saves.
- `context_reclaim` hides contexts outside the current local VM during GC, then restores visibility after collection.
- Operators include `condition`, `currentcontext`, `detach`, `.fork`, `join`, `.localfork`, `lock`, `monitor`, `notify`, `wait`, `yield`, and replacement `usertime`.
- `.fork` creates a new context sharing local/global VM; `.localfork` creates private local VM with shared global VM and a new `userdict`.
- Fork setup copies dictionary/execution/operand stacks, stdio refs, language level, binary object format, and for shared-VM forks copies graphics-state stack.
- `fork_done` unwinds stacks/gstates, performs pending restores, handles detached contexts, wakes joiners, and reschedules.
- `monitor` acquires a lock, pushes cleanup/release continuations, and executes the protected procedure.
- `wait` releases a lock, queues the context on a condition, and reacquires the lock through `await_lock` after notify.
- `usertime` begins per-context usertime accounting lazily and returns elapsed execution time for the current context.

Dependencies and coupling:
- Deeply coupled to interpreter context state, ref stacks, VM spaces, GC roots, graphics state, files/stdin/stdout refs, and interpreter scheduling hooks.
- Uses context indices rather than cross-local-VM pointers for wait/active lists.
- Comments flag incomplete cleanup areas around freeing local VM/gstates and error handling during fork restore paths.

<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcontext.c -->