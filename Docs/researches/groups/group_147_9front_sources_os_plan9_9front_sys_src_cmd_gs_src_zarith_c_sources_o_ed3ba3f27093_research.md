# Group Research: group_147_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_zarith_c_sources_o_ed3ba3f27093

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. I read every listed source file completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zarith.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zarith.c

This file implements Ghostscript/PostScript arithmetic operators for integers and reals.

Key behavior:
- Defines `add`, `sub`, `mul`, `div`, `idiv`, `mod`, `neg`, `abs`, `ceiling`, `floor`, `round`, and `truncate`.
- Exposes `zop_add` and `zop_sub` as reusable helper procedures for direct interpreter and FunctionType 4 use.
- Detects integer overflow in `add`, `sub`, and `mul`, converting overflowing integer results to reals where PostScript semantics allow it.
- Checks divide-by-zero for `div`, `idiv`, and `mod`; handles `MIN_INTVAL / -1` as a rangecheck boundary case for `idiv`.
- Includes a non-standard `.bitadd` integer-only addition operator that deliberately skips the normal overflow conversion semantics.

Important dependencies:
- Uses `oper.h` stack/operator helpers, `store.h` ref construction, and `math_.h` for `ceil`/`floor`.
- Registered through `zarith_op_defs`.

Research notes:
- This is interpreter arithmetic plumbing, not filesystem code, but it is part of the vendored 9front Ghostscript command tree.
- The file explicitly notes that arithmetic operators do not check floating-point exceptions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zarith.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zarray.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zarray.c

This file implements the core PostScript array creation and stack transfer operators.

Key behavior:
- `array` allocates a writable array of the requested integer size and initializes entries to null.
- `aload` expands an array or packed array onto the operand stack and leaves the source array on top.
- `astore` stores stack objects into a writable array, including the slow path for stack segments that cross ref-stack boundaries.
- Generic array-like operators such as `copy`, `get`, `put`, `length`, `forall`, and interval operations are intentionally implemented elsewhere in `zgeneric.c`.

Important dependencies:
- Uses Ghostscript allocator APIs from `ialloc.h`.
- Handles packed arrays via `ipacked.h`.
- Uses `ref_stack_push`, `ref_stack_store`, and `refcpy_to_old` to preserve VM/write-barrier behavior.

Registered operators:
- `aload`
- `array`
- `astore`
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zarray.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zbfont.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zbfont.c

This is a central Ghostscript font construction utility file for base, simple, primitive, outline, Type 3, and FDArray-backed fonts.

Key behavior:
- Implements `.buildfont3` for Type 3 user-defined fonts.
- Provides glyph encoding helpers: character-to-glyph lookup through `Encoding`, glyph-name lookup, CID numeric-name fabrication, and glyph-to-Unicode mapping via `GlyphNames2Unicode` or a `UnicodeDecoding` resource.
- Builds common font procedure references from `BuildChar` and `BuildGlyph`.
- Implements common builders:
  - `build_gs_font`
  - `build_gs_sub_font`
  - `build_gs_simple_font`
  - `build_gs_outline_font`
  - `build_gs_primitive_font`
  - `build_gs_FDArray_font`
- Validates font dictionaries for `FontType`, `Encoding`, `FontMatrix`, `FontBBox`, `PaintType`, `StrokeWidth`, bitmap policy keys, UID, and FID behavior.
- Handles re-registered/scaled fonts, re-encoded fonts, and Type 0/CID FDArray subfont construction.
- Initializes `font_data`, stores font dictionary/procs/encoding, assigns glyph and Unicode procedures, and registers fonts through `define_gs_font`.

Important dependencies:
- Uses Ghostscript font core headers: `gxfont.h`, `bfont.h`, `gscencs.h`, `gsmatrix.h`.
- Uses interpreter dictionary/name/ref memory APIs: `idict.h`, `idparam.h`, `iname.h`, `ialloc.h`, `istruct.h`.

Research notes:
- This file is high-value for understanding Ghostscript’s PostScript dictionary-to-C font object bridge.
- It contains compatibility accommodations for malformed or non-standard fonts, including synthetic glyph names for Type 3 `.notdef` cases and UID invalidation when metrics differ.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zbfont.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zbseq.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zbseq.c

This file implements Level 2 binary object sequence support.

Key behavior:
- Defines a stable-memory wrapper for the system/user name table reference.
- `create_names_array` allocates a names-array reference in stable memory.
- Initialization creates a temporary fake system name table; PostScript initialization later installs the real one.
- `.installsystemnames` installs the global, readonly shortarray of system names, only from global VM at save level zero.
- `currentobjectformat` and `setobjectformat` expose the binary object format setting.
- `.bosobject` encodes one object into binary object sequence representation using `encode_binary_token`.

Important dependencies:
- Uses binary token machinery from `btoken.h`.
- Uses stable allocator behavior from `gxalloc.h` and `ialloc.h`.
- Registered as Level 2 operators in `zbseq_l2_op_defs`.

Research notes:
- This is serialization/interpreter infrastructure for PostScript binary object sequences, not rendering or filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zbseq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zcfont.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zcfont.c

This file implements composite-font character operators, mainly `cshow` and `rootfont`.

Key behavior:
- `cshow` accepts the procedure and string in either order for Adobe compatibility.
- Sets up a C-show text enumerator and calls the user procedure for each character with character code and current width.
- During `cshow`, constructs an appropriately scaled leaf font when processing composite fonts and temporarily changes current font while preserving root/current font state.
- Restores root and current font after the user procedure using e-stack continuations.
- `rootfont` returns the current root font dictionary.

Important dependencies:
- Uses Ghostscript text enumerators from `gxtext.h`.
- Uses interpreter show setup/continuation helpers declared through `ichar.h`.
- Uses font and graphics state APIs from `ifont.h` and `igstate.h`.

Registered operators:
- `cshow`
- `rootfont`
- Internal `%cshow_continue`
- Internal `%cshow_restore_font`
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zcfont.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zchar.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zchar.c

This is the main Ghostscript character rendering operator file.

Key behavior:
- Implements `show`, `ashow`, `widthshow`, `awidthshow`, `kshow`, `stringwidth`, `charpath`, `.charboxpath`, `setcachedevice`, `setcachedevice2`, and `setcharwidth`.
- Builds and drives `gs_text_enum_t` text enumerators for rendering, measuring, kerning, charpath construction, and cache-device setup.
- Stores show state on the e-stack, including saved operand/dictionary stack depths, graphics-state level, current/root font state, and cleanup procedure.
- Dispatches text processing outcomes:
  - normal completion
  - kshow/cshow intervention
  - BuildChar/BuildGlyph rendering
  - CDevProc cache setup for CID Type 0 and CID TrueType fonts
  - error cleanup
- Chooses BuildChar versus BuildGlyph based on font type, glyph availability, character code, and Encoding equality.
- Implements glyph-to-character reverse lookup for Type 3 `glyphshow` fallback.
- Provides `font_bbox_param`, tolerating missing or unreasonable FontBBox values by zeroing them.

Important dependencies:
- Works with `gstext`, `gxfont`, `gxfont42`, `gxfont0`, `ichar`, `ichar1`, `ifont`, `igstate`, `estack`, and dictionary stack APIs.
- Calls specialized cache helpers from `zchar42.h` and Type 1 helper `z1_set_cache`.

Research notes:
- This file is the core interpreter lifecycle for text rendering and text measurement.
- It is careful about error cleanup because BuildChar/BuildGlyph can execute arbitrary PostScript and mutate stacks/gstate.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zchar.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zchar1.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zchar1.c

This file implements Type 1 character display and shared charstring execution support for Type 1, Type 2, Type 4/disk-based, and CID Type 0 flows.

Key behavior:
- `.type1execchar` delegates to `charstring_execchar` for Type 1 and disk-based fonts.
- Initializes a Type 1 interpreter using current gstate/path, text enumerator scale, alpha/oversampling rules, PaintType, and font data.
- Supports both valid-FontBBox and no-FontBBox execution paths:
  - bbox path sets cache before interpreting full outline when possible.
  - no-bbox path builds the outline first, derives bbox, sets cache, and may re-run for antialiasing oversampling.
- Handles Type 1 OtherSubrs by moving interpreter state to heap, pushing saved operands/continuations on the e-stack, and calling PostScript OtherSubrs.
- Implements fill/stroke finishing paths with compatibility adjustments for fill rule, StrokeWidth, and fill_adjust behavior.
- Exposes `.setweightvector` for Multiple Master Type 1/Type 2 weight vectors.
- Provides backend helpers:
  - Type 1 glyph data, subr data, SEAC data
  - stack push/pop callbacks for Type 1 interpreter
  - glyph outline construction
  - glyph info with Metrics, Metrics2, and CDevProc awareness
  - `z1_set_cache` for CID encrypted font cache setup

Important dependencies:
- Uses Type 1 interpreter structures from `gxtype1.h` and font structures from `gxfont1.h`.
- Depends on common char output helpers in `icharout.h` and show lifecycle helpers from `zchar.c`.

Research notes:
- This is one of the highest-risk files in the group because it bridges arbitrary PostScript execution, font charstring interpretation, stack manipulation, cache-device setup, and graphics-state restoration.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zchar1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zchar2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zchar2.c

This is a small Type 2 character display operator wrapper.

Key behavior:
- Defines `.type2execchar`.
- Delegates implementation to `charstring_execchar` with a font-type mask restricted to `ft_encrypted2`.

Important dependencies:
- Uses shared Type 1/Type 2 charstring execution declared in `ichar1.h`.
- Registered through `zchar2_op_defs`.

Research notes:
- Most Type 2 behavior lives in `zchar1.c`; this file only supplies the Type 2 operator entry point.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zchar2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zchar32.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zchar32.c

This file implements Type 32 bitmap CID font glyph operators.

Key behavior:
- `.makeglyph32` serializes bitmap glyph metrics into compact short or long string forms.
- Validates metric arrays of either 6 values or 10 values, bitmap dimensions, CID range, Type 32 font type, and output string capacity.
- `.getmetrics32` decodes Type 32 metric strings and returns width, height, metrics, and consumed byte count.
- `.removeglyphs` purges cached glyphs in a CID range for a Type 32 bitmap font.

Important dependencies:
- Uses font cache APIs from `gxfcache.h`.
- Uses CID glyph code ranges via `gs_min_cid_glyph`.
- Requires `ft_CID_bitmap` fonts.

Registered operators:
- `.getmetrics32`
- `.makeglyph32`
- `.removeglyphs`
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zchar32.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zchar42.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zchar42.c

This file implements Type 42 and CID TrueType character display support.

Key behavior:
- `zchar42_set_cache` computes metrics for TrueType/Type 42 glyphs and calls common `zchar_set_cache`.
- Uses font Metrics when present; otherwise asks the Type 42 backend for horizontal and, when needed, vertical WMode metrics.
- Provides vertical fallback metrics for CID TrueType fonts when vertical TrueType metrics are unavailable.
- `.type42execchar` validates current show context and TrueType/CID TrueType font type, establishes a current point, sets cache, and then fills or strokes the glyph.
- `type42_finish` appends a TrueType glyph outline to the current path through `gs_type42_append` and draws it.

Important dependencies:
- Uses `gxfont42.h`, `gxtext.h`, `gspath.h`, `gspaint.h`, and common char output cache helpers.
- Declared externally in `zchar42.h`.

Research notes:
- Rendering deliberately uses current gstate/path rather than the text enumerator imager/path; the source calls this a design bug.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zchar42.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zchar42.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zchar42.h

This header declares the shared Type 42 cache setup helper.

Key content:
- Include guard `zchar42_INCLUDED`.
- Declares `zchar42_set_cache(i_ctx_t *, gs_font_base *, ref *, uint glyph_index, op_proc_t cont, op_proc_t *exec_cont, bool put_lsb)`.

Used by:
- `zchar.c` for CID TrueType CDevProc/cache paths.
- `zchar42.c` as the implementation file.

Research notes:
- The header is narrow and only exposes one cross-file Type 42 helper.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zchar42.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zcharout.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zcharout.c

This file contains common outline-font character output helpers used by Type 1, Type 4, Type 42, and CID font paths.

Key behavior:
- `zchar_exec_char_proc` executes a PostScript outline procedure inside `systemdict` and font dictionary scopes.
- `zchar_get_metrics` reads Metrics entries and supports width-only, 2-element, and 4-element side-bearing/width formats.
- `zchar_get_metrics2` reads vertical Metrics2 entries.
- `zchar_get_CDevProc` detects a font CDevProc.
- `zchar_set_cache` combines width, bbox, Metrics2, default vertical metrics, CDevProc, and width-only short-circuiting into `setcachedevice`/`setcachedevice2` behavior.
- `zchar_charstring_data` fetches CharStrings data and special-cases a common `.notdef` procedure into a synthetic Type 1 charstring.
- `zchar_enumerate_glyph` iterates CharStrings dictionary keys and maps integer keys to CID glyphs or name keys to glyph names.

Important dependencies:
- Uses `gscrypt1.h` to synthesize encrypted `.notdef` charstrings when needed.
- Uses common show/cache APIs from `ichar.h` and `icharout.h`.

Research notes:
- This is shared glue between font dictionaries and lower-level glyph cache/rendering code.
- It is compatibility-heavy, especially around Metrics/CDevProc and malformed `.notdef` entries.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zcharout.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zcharx.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zcharx.c

This file implements Level 2 character operators beyond basic `show`.

Key behavior:
- `glyphshow` renders a glyph by name for simple fonts or by CID integer for CID fonts.
- `.glyphwidth` measures a glyph and returns width using the same text-enumerator flow as `stringwidth`.
- `xshow`, `yshow`, and `xyshow` accept a string plus numeric array/string and apply per-character displacement values.
- `moveshow` normalizes numeric arrays/strings into a temporary float array, starts `gs_xyshow_begin`, and frees the array on setup failure.

Important dependencies:
- Uses numeric packed-array helpers from `ibnum.h`.
- Reuses show setup and finishing helpers from `ichar.h`.
- Registered as Level 2 operators in `zcharx_op_defs`.

Research notes:
- The file depends on correct temporary allocation lifetime: the float displacement array is handed to the text enumerator on success.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zcharx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zcid.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zcid.c

This file provides CMap and CID-keyed font service routines.

Key behavior:
- `cid_system_info_param` extracts and validates `Registry`, `Ordering`, and `Supplement` from a CIDSystemInfo dictionary.
- Converts CIDs to TrueType character codes or glyph indexes using a Decoding dictionary and optional TrueType cmap.
- Applies `SubstNWP` substitution ranges in both directions when direct CID lookup fails.
- Builds a GDBytes=2 CIDMap from Decoding, TrueType cmap, and SubstNWP by writing glyph indexes into CIDMap strings.
- Validates CIDMap array/string shape before filling it.

Important dependencies:
- Uses CID structures from `gxcid.h` and `icid.h`.
- Uses Ghostscript dictionary and array APIs from `idict.h`, `idparam.h`, and `store.h`.

Research notes:
- This file does not register PostScript operators directly; it is support code for CID font/CMap construction.
- Several comments mark unimplemented general cases, including non-2-byte GDBytes and non-array CIDMap forms.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zcid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zcidtest.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zcidtest.c

This file adds testing/debug operators for CIDFont and CMap facilities.

Key behavior:
- `.wrapfont` wraps TrueType, CID encrypted, CID user-defined, or CID TrueType fonts into Type 0 fonts.
- For Type 42 fonts, patches `BuildGlyph` to `%Type11BuildGlyph` and adjusts CIDMap behavior for PostScript BuildChar-backed Type 42 handling.
- `.writecmap` writes a CMap dictionary’s `CodeMap` structure to a writable file through `psf_write_cmap`.
- `.writefont9` writes a CIDFontType 0 / FontType 9 font to a writable file using `psf_write_cid0_font`.

Important dependencies:
- Uses font serialization support from `gdevpsf.h`.
- Uses `gxfont0c.h` Type 0 conversion helpers.
- Uses stream/file operators through `files.h` and `stream.h`.

Research notes:
- These operators are explicitly for testing facilities rather than normal language-level rendering.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zcidtest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zcie.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zcie.c

This file implements CIE color-space operators and the procedure-cache setup needed by CIE spaces.

Key behavior:
- Provides dictionary parameter helpers for ranges, 3x3 matrices, procedure arrays, white/black points, and lookup tables.
- Validates CIE white/black points and lookup table dimensions/string sizes.
- Implements `.setcieaspace`, `.setcieabcspace`, `.setciedefspace`, and `.setciedefgspace`.
- Builds CIE color spaces using graphics-library constructors, fills parameter structures, installs cached decode procedures, and calls `gs_setcolorspace`.
- Uses e-stack continuations to sample PostScript decode procedures into fixed-size CIE caches before completing color-space setup.
- Provides shared cache preparation and completion routines for one, three, or four decode procedures.

Important dependencies:
- Uses CIE color structures from `gscie.h`, `gscolor2.h`, and `gxcspace.h`.
- Uses interpreter procedure execution through `zfor_samples`, `zcvx`, and e-stack continuations.
- Stores active CIE procedure refs in `istate->colorspace.procs.cie`.

Research notes:
- This file is interpreter-to-graphics-library glue for calibrated color spaces.
- It is sensitive to e-stack cleanup because setup can partially allocate color spaces and cache tables before errors.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zcie.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zcolor.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zcolor.c

This file implements core color and color-space operators.

Key behavior:
- `currentcolor` returns numeric color components and, for pattern spaces, the pattern dictionary or null object.
- `currentcolorspace` returns the interpreter’s stored color-space array, with special handling to synthesize `DeviceGray` when necessary.
- `.getuseciecolor` reads the interpreter state flag corresponding to `UseCIEColor`.
- `setcolor` gathers numeric and pattern operands and passes them to `gs_setcolor`.
- `setcolorspace` stores the nominal PostScript color-space array in interpreter state.
- `.setdevcspace` sets DeviceGray, DeviceRGB, or DeviceCMYK via graphics-library color-space initialization.
- Implements `currenttransfer`, `settransfer`, and color remapping helpers that sample transfer procedures into transfer maps.
- Provides internal color remap/reset operators and diagnostic `.color_test` / `.color_test_all`.

Important dependencies:
- Uses graphics color APIs from `gxcolor2.h`, `gxcspace.h`, `gxcmap.h`, `gxdcolor.h`, and `gxpcolor.h`.
- Uses e-stack sampling through `zfor_samples`.
- Relies on `gx_set_effective_transfer` from halftone/transfer logic.

Research notes:
- This file owns interpreter color state synchronization with graphics state.
- Several operators are internal and invoked under controlled PostScript initialization paths rather than doing full operand validation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zcolor.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zcolor1.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zcolor1.c

This file implements Level 1 extended color operators for transfer, black generation, and undercolor removal.

Key behavior:
- Provides current-state operators:
  - `currentblackgeneration`
  - `currentcolortransfer`
  - `currentundercolorremoval`
- `setblackgeneration` installs a PostScript black-generation procedure and samples it into the graphics transfer map.
- `setcolortransfer` installs red, green, blue, and gray transfer procedures and remaps all four.
- `setundercolorremoval` installs an undercolor-removal procedure and samples it with signed output support.
- Invalidates current device color after remapping so later painting uses updated transfer behavior.

Important dependencies:
- Reuses shared remapping helpers from `zcolor.c`.
- Calls graphics-library remap setters from `gscolor1.h`.

Research notes:
- The main complexity is sequencing e-stack remap continuations for one or four procedure maps.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zcolor1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zcolor2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zcolor2.c

This is a small Level 2 color operator file.

Key behavior:
- Implements `.usealternate`, which pushes true when the current color space has a base or alternate color space in use.
- Uses `cs_base_space(gs_currentcolorspace(igs))` to detect that condition.

Important dependencies:
- Uses color-space APIs from `gxcspace.h` and `gscolor2.h`.
- Registered as Level 2 in `zcolor2_l2_op_defs`.

Research notes:
- This is a narrow interpreter helper for Separation/alternate color-space behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zcolor2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zcolor3.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zcolor3.c

This file implements the Level 3 internal UseCIEColor setter.

Key behavior:
- `.setuseciecolor` stores the supplied boolean-like ref into `istate->use_cie_color`.
- The comment states this parameter mirrors the `UseCIEColor` page-device parameter and may be set only in language level 3.
- Operand checking is intentionally omitted because the operator is only accessible during controlled initialization paths.

Important dependencies:
- Uses interpreter graphics state from `igstate.h`.
- Registered in `zcolor3_l3_op_defs`.

Research notes:
- This is a tiny state-setting companion to `.getuseciecolor` in `zcolor.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zcolor3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zcontext.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zcontext.c

This file implements Display PostScript context operators: cooperative scheduling, fork/join, detach, locks, conditions, monitor/wait/notify, yield, and context-aware usertime.

Key behavior:
- Defines `gs_context_t`, `gs_scheduler_t`, `gs_lock_t`, and `gs_condition_t`.
- Hooks Ghostscript interpreter scheduling callbacks on initialization, creates the initial context, and installs a scheduler.
- Maintains active/dead/waiting context lists using context IDs rather than raw pointers.
- Handles time slicing through `ctx_time_slice` and explicit rescheduling through `ctx_reschedule`.
- Wraps VM reclaim/GC so contexts in other local VMs can be hidden during local collection.
- Implements:
  - `currentcontext`
  - `detach`
  - `.fork`
  - `.localfork`
  - `join`
  - `yield`
  - `condition`
  - `lock`
  - `monitor`
  - `notify`
  - `wait`
  - context-aware replacement for `usertime`
- Supports local forks with private local VM and shared global VM, including userdict replacement and stack copying.
- Supports regular forks sharing local/global VM, including gstate stack copying.
- Cleans up terminated contexts, restores stacks/gstate, processes unmatched saves, and schedules joiners.
- Implements locks and conditions with waiting lists and monitor cleanup continuations to release locks on normal completion or stack unwinding.

Important dependencies:
- Uses interpreter state storage/loading from `icontext.h`.
- Uses VM/save/GC internals from `isave.h`, `istruct.h`, and allocator APIs.
- Uses file refs for fork stdin/stdout setup through `files.h`.
- Integrates with operand, dictionary, and execution stacks through `ostack.h`, `dstack.h`, and `estack.h`.

Research notes:
- This is the most OS-like file in the group: it models lightweight interpreter contexts and synchronization primitives.
- It is explicitly cooperative, not kernel-thread based.
- The source contains several cautionary comments around local VM save levels, GC visibility, gstate copying, and incomplete/freeing cleanup paths.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zcontext.c -->