# Group Research: group_137_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_ierrors_h_sources__886158e4760f

Scope: `Docs/research_subset_a.md`, specifically `sources/os/plan9/9front` under the bundled Ghostscript interpreter source tree. I read all 36 listed files completely. The supplied internal group report path was not present in the workspace, so this report is based on the source files themselves.

This group covers Ghostscript interpreter infrastructure: PostScript error codes, execution stack data, font/filter/image/function internal APIs, interpreter graphics state, GC for refs/strings/objects, initialization, top-level interpreter API, command-line dispatch, and name-table management.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ierrors.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ierrors.h

Defines interpreter-level error codes and error-name lists for Ghostscript.

Key points:
- Explicitly warns this is interpreter-only; graphics library code should use `gserrors.h`.
- Uses negative integer codes for failures and non-negative values for success.
- Declares `gs_error_names[]`, populated in `iinit.c`.
- Defines Level 1 PostScript errors from `e_unknownerror (-1)` through `e_VMerror (-25)`.
- Defines Level 2/DPS additions: `e_configurationerror`, `e_invalidcontext`, `e_undefinedresource`, `e_unregistered`, `e_invalidid`.
- Defines pseudo-errors used internally:
  - `e_Fatal`, `e_Quit`, `e_InterpreterExit`
  - `e_RemapColor`
  - `e_ExecStackUnderflow`
  - `e_VMreclaim`
  - `e_NeedInput`, `e_NeedStdin`, `e_NeedStdout`, `e_NeedStderr`
  - `e_Info`
- `ERROR_IS_INTERRUPT(ecode)` treats `e_interrupt` and `e_timeout` as retry/re-execute cases.

Dependencies and interactions:
- `iinit.c` builds `gs_error_names[]` from `ERROR_NAMES`.
- `imain.c` handles `e_NeedStdin/stdout/stderr`, `e_Fatal`, `e_Quit`, and finalization paths.
- Many interpreter modules return these codes as canonical PostScript/interpreter errors.

Research relevance:
- This is the central error-code contract for interpreter control flow, including normal quits, fatal exits, VM reclaim, input suspension, and console callouts.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ierrors.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iesdata.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iesdata.h

Defines the execution stack data structure.

Key points:
- Includes `isdata.h`.
- Defines `exec_stack_t` containing:
  - `ref_stack_t stack`
  - cached `ref *current_file`
- The `current_file` cache points to the topmost executable file on the execution stack, or is null.
- Comments define cache invariants and require stack push/pop code to clear/check the cache when executable files may be involved.
- Provides `public_st_exec_stack()` descriptor macro using `st_ref_stack` as suffix storage metadata.
- Notes that `current_file` is cleared by GC and therefore not declared as a traced pointer.

Dependencies and interactions:
- `iestack.h` provides cache manipulation macros around this data.
- Interpreter execution uses this to accelerate `currentfile` lookups.

Research relevance:
- Small but important performance/data-integrity component for Ghostscript’s execution stack.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iesdata.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iestack.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iestack.h

Defines the execution stack API aliases and cache helpers.

Key points:
- Includes `iesdata.h` and `istack.h`.
- Defines `es_ptr` and `const_es_ptr` as execution-stack pointer aliases.
- Provides macros:
  - `estack_clear_cache(pes)`
  - `estack_set_cache(pes, pref)`
  - `estack_check_cache(pes)`
- `estack_check_cache` caches the top stack entry if it is an executable file ref.

Dependencies and interactions:
- Operates on `exec_stack_t.current_file`.
- Relies on ref type/attribute predicates such as `r_has_type_attrs`.

Research relevance:
- Supports fast `currentfile` behavior and documents the coupling between execution-stack mutation and cache correctness.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iestack.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ifapi.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ifapi.h

Defines Ghostscript’s Font API plugin interface.

Key points:
- Includes `iplugin.h`.
- Defines `FracInt` and `FAPI_retcode`.
- Defines `fapi_font_feature` enum for PostScript/Type1/TrueType font properties such as `FontMatrix`, `UniqueID`, blue values, stem snaps, `Subrs`, and TrueType size.
- Defines metric replacement modes in `FAPI_metrics_type`.
- `FAPI_char_ref` identifies a character by code, glyph index, or name and can carry replacement metrics.
- `FAPI_font` carries server-owned font data, client context, font source path, Type1/CID flags, char data, and callback functions for retrieving font features, subrs, glyphs, and serialized TrueType data.
- `FAPI_path` abstracts outline callbacks: `moveto`, `lineto`, `curveto`, `closepath`.
- `FAPI_font_scale`, `FAPI_metrics`, and `FAPI_raster` describe scaling, metrics, and 1-bit raster output.
- `FAPI_server` extends `i_plugin_instance` and exposes plugin/server callbacks for opening, scaled-font acquisition, decoding IDs, metrics, raster/outline retrieval, and data/typeface release.
- Comments clarify that Ghostscript cannot tell the server when scaled fonts are no longer used; the server must cache and evict internally.

Dependencies and interactions:
- Used by FAPI bridge/plugin code such as `zfapi.c`.
- Coordinates font data retrieval between the interpreter and external font backends.

Research relevance:
- Important extension boundary: the interpreter delegates font scaling/raster/outline operations through this ABI-like interface.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ifapi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ifcid.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ifcid.h

Declares internal CID font helper APIs exported by `zfcid.c`.

Key points:
- `cid_font_system_info_param` extracts `CIDSystemInfo` from a CIDFont dictionary.
- `cid_font_data_param` extracts additional CIDFontType 0/2 data into `gs_font_cid_data`, including `GlyphDirectory`.

Dependencies and interactions:
- Uses `gs_cid_system_info_t`, `ref`, `os_ptr`, and `gs_font_cid_data`.
- Used by CID font builders/operators.

Research relevance:
- Small bridge header for CID-keyed font dictionary parsing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ifcid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ifilter.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ifilter.h

Defines interpreter-level filter creation support.

Key points:
- Includes `istream.h` and `ivmspace.h`.
- Declares `filter_read` and `filter_write`, which create stream filters from operator operands, a stream template, optional state, and VM-space metadata.
- Declares simplified no-parameter/no-state helpers:
  - `filter_read_simple`
  - `filter_write_simple`
- Declares temporary-stream helpers:
  - `filter_mark_temp`
  - `filter_mark_strm_temp`
- Declares `filter_report_error`, a standard stream error reporter that records messages in `$error.errorinfo`.
- Defines `stream_proc_state` for procedure-based streams, containing `eof`, current data index, interpreter procedure ref, and data ref.
- Provides GC descriptor macro `private_st_stream_proc_state()`.
- Declares `s_is_proc` to detect procedure-based streams.

Dependencies and interactions:
- Filter operators in `zf*.c` use this to construct PostScript filter streams.
- Procedure streams are interpreter-level because they store refs/procedures, unlike lower-level stream package filters.

Research relevance:
- Central adapter from PostScript filter operators to Ghostscript stream templates and VM allocation rules.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ifilter.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ifilter2.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ifilter2.h

Declares Level 2 filter setup helpers.

Key points:
- Exports setup routines from `zfdecode.c`:
  - `zcf_setup` for CCITTFax (`stream_CF_state`)
  - `zlz_setup` for LZW (`stream_LZW_state`)
  - `zpd_setup` for PNG/TIFF predictor diff (`stream_PDiff_state`)
  - `zpp_setup` for PNG predictor (`stream_PNGP_state`)

Dependencies and interactions:
- Used by Level 2 filter operator implementations to parse dictionaries into stream states.
- `zcf_setup` takes `gs_ref_memory_t *imem`, reflecting VM-aware parameter storage.

Research relevance:
- Narrow interface for shared Level 2 decode/filter parameter parsing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ifilter2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ifont.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ifont.h

Defines interpreter-side font client data and shared font procedures.

Key points:
- Includes `gsccode.h` and `gsstype.h`.
- Defines `font_data`, the interpreter client data attached to library `gs_font` objects.
- Common refs include:
  - font dictionary
  - `BuildChar`, `BuildGlyph`
  - `Encoding`
  - `CharStrings`
  - `GlyphNames2Unicode`
- Union stores font-type-specific refs:
  - Type 1: `OtherSubrs`, `Subrs`, `GlobalSubrs`
  - Type 42/CIDFontType2: `sfnts`, `CIDMap`, `GlyphDirectory`
  - CIDFontType0: `GlyphDirectory`, `GlyphData`, `DataSource`
- Defines `st_font_data` descriptor macro and helpers `pfont_data`, `pfont_dict`.
- Declares:
  - `font_bbox_param`
  - `font_param`
  - `zfont_mark_glyph_name`
  - `zfont_info`

Dependencies and interactions:
- Used by font-building modules (`zfont.c`, `zbfont.c`, `zchar.c`) and character cache marking.
- The design treats refs as an ordinary structure to avoid allocation fragmentation/sandbars.

Research relevance:
- Core interpreter/library boundary for PostScript font objects and GC-visible font metadata.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ifont.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ifont1.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ifont1.h

Declares shared utilities for Type 1, Type 2, and other CharString-based fonts.

Key points:
- Defines `charstring_font_refs_t` with refs to:
  - `Private`
  - `OtherSubrs`
  - `Subrs`
  - `GlobalSubrs`
  - `no_subrs`
- Defines Type 1 default `lenIV` as `4`.
- Declares:
  - `charstring_font_get_refs`
  - `charstring_font_params`
  - `charstring_font_init`
  - `build_charstring_font`

Dependencies and interactions:
- Used by Type 1/2/CIDFontType0 builders.
- Bridges PostScript font dictionaries/FDArray entries into `gs_type1_data` and `gs_font_type1`.

Research relevance:
- Shared parsing/build path for encrypted CharString font data and subroutine dictionaries.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ifont1.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ifont2.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ifont2.h

Declares Type 2-specific font parameter parsing.

Key points:
- Defines Type 2 default `lenIV` as `-1`.
- Declares `type2_font_params`, which extracts Type 2 parameters beyond the common Type 1/Type 2 CharString parameters.

Dependencies and interactions:
- Requires `charstring_font_refs_t` and `gs_type1_data`, so it works with `ifont1.h` utilities.
- Used for Type 2 fonts and FontType 2 FDArray entries in CIDFontType 0 fonts.

Research relevance:
- Small specialization point for Type 2/CFF-style font handling.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ifont2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ifont42.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ifont42.h

Declares Type 42 and CIDFontType 2 TrueType font build helpers.

Key points:
- `build_gs_TrueType_font` builds Type 11 or Type 42 fonts.
- `font_string_array_param` validates/extracts string arrays while returning the parameter value even on wrong type.
- `font_GlyphDirectory_param` returns 0 if present, 1 if absent, or an error.
- `font_gdir_get_outline` retrieves glyph outlines from `GlyphDirectory`, returning an empty string if missing/out of range.
- `string_array_access_proc` accesses byte ranges across arrays of strings, used for `sfnts` and `CIDMap`.

Dependencies and interactions:
- Used by TrueType-backed font construction.
- Handles Ghostscript’s representation of TrueType `sfnts` as arrays of strings and CID maps.

Research relevance:
- Interface for interpreter-side TrueType/CID TrueType font materialization.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ifont42.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ifrpred.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ifrpred.h

Declares read-side predictor filter helper.

Key points:
- Exports `filter_read_predictor` from `zfdecode.c` for `zfzlib.c`.
- Signature takes interpreter context, operand pop count, stream template, and stream state.

Dependencies and interactions:
- Used by Flate/zlib decode paths that need PNG/TIFF predictor wrapping.

Research relevance:
- Small shared hook for composing read filters with predictor processing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ifrpred.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ifunc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ifunc.h

Defines internal interpreter APIs for PostScript/PDF Functions.

Key points:
- Includes `gsfunc.h`.
- Defines `build_function_proc` signature and function-pointer type.
- Defines `build_function_type_t`, mapping `FunctionType` integers to builder procedures.
- Declares `build_function_type_table[]` and count.
- Declares:
  - `fn_build_function`
  - `fn_build_sub_function`
  - `fn_build_float_array`
  - `fn_build_float_array_forced`
  - `ref_function`
  - `zexecfunction`
- `fn_build_float_array` handles optional/required arrays and even-length constraints.
- `fn_build_float_array_forced` also accepts a scalar numeric parameter as a one-element array.

Dependencies and interactions:
- Used by function-type operator builders and function execution operators.
- Bridges PostScript dictionary/function refs into library `gs_function_t`.

Research relevance:
- Function-object construction API for gradients, transfer functions, and PDF function semantics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ifunc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ifwpred.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ifwpred.h

Declares write-side predictor filter helper.

Key points:
- Exports `filter_write_predictor` from `zfilter2.c` for `zfzlib.c`.
- Signature mirrors read predictor setup: context, pop count, stream template, and stream state.

Dependencies and interactions:
- Used by encoded output filters that need predictor preprocessing.

Research relevance:
- Small shared hook for composing write filters with predictor processing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ifwpred.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/igc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/igc.c

Implements Ghostscript’s interpreter garbage collector for ref memory.

Key points:
- Defines the collector procedure vector `igc_procs`, including relocation for structs, strings, const strings, parameter strings, refs, and ref arrays.
- Defines pointer descriptors:
  - `ptr_struct_procs`
  - `ptr_string_procs`
  - `ptr_const_string_procs`
  - `ptr_ref_procs`
- Main entry point is `gs_gc_reclaim(vm_spaces *pspaces, bool global)`.
- Supports local and global collection:
  - Determines which VM spaces to trace and which to compact.
  - Handles stable allocators and save levels.
  - Registers allocator roots so change/save lists are traced.
- Marking:
  - Clears object and string marks in collected spaces.
  - Unmarks roots and optionally names.
  - Builds a mark stack from a default C-stack segment, free blocks, and heap-allocated extensions.
  - Traces roots, non-local chunks during local GC, names, refs, arrays, dictionaries, strings, devices, files, fonts, structs, and op arrays.
  - Handles mark-stack overflow by recording rescan intervals in chunks.
- Relocation/compaction:
  - Clears reloc info for traced-only chunks.
  - Disables freeing while finalizers run.
  - Computes object/string relocation.
  - Relocates pointers in chunks and roots.
  - Compacts object and string storage.
  - Frees empty chunks.
  - Updates allocator saved-state memory statistics.
- Debug support:
  - Phase logging under debug flags.
  - Pointer validation hooks through `ilocate.c`.
  - Relocation printing via `print_reloc_proc`.
- Exports `gcst_get_memory_ptr`.

Dependencies and interactions:
- Calls string GC helpers from `igcstr.c`.
- Calls ref GC helpers from `igcref.c`.
- Uses name-table marking and trace finish routines.
- Uses `ilocate.c` for chunk lookup and validation.
- Uses operator-array name tables from `opdef.h`.

Risks and notes:
- Relocation uses compacting GC assumptions and low-level pointer arithmetic.
- Debug paths can abort on impossible states.
- Comments note deprecated const-removal puns in relocation.

Research relevance:
- This is the core memory-management engine for the Ghostscript interpreter VM: mark, relocate, compact, finalize, and free.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/igc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/igc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/igc.h

Defines internal GC interfaces and state.

Key points:
- Declares `gs_gc_reclaim`.
- Defines `struct_shared_procs_s`, the per-genus operations:
  - `clear_reloc`
  - `set_reloc`
  - `compact`
- Defines `gc_state_s` with:
  - GC procedure vector
  - chunk locator
  - VM spaces
  - minimum collected space
  - untraced relocation flag
  - heap pointer
  - name table pointer
  - debug container chunk
- Declares ref mark/unmark helpers exported by `igcref.c`.
- Declares allocator validation functions exported by `ilocate.c`.
- Declares `gcst_get_memory_ptr` exported by `igc.c`.
- Defines `print_reloc` debug macro.

Dependencies and interactions:
- Included by `igc.c`, `igcref.c`, `igcstr.c`, and `ilocate.c`.
- Ties together struct/ref/string GC mechanisms.

Research relevance:
- Primary internal contract for Ghostscript’s compacting garbage collector.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/igc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/igcref.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/igcref.c

Implements GC support for Ghostscript `ref` objects and packed refs.

Key points:
- Defines special structure type descriptor `st_refs`.
- Defines shared procs for ref blocks:
  - `refs_clear_reloc`
  - `refs_set_reloc`
  - `refs_compact`
- Defines helper procs for structs containing embedded refs:
  - `ref_struct_clear_marks`
  - `ref_struct_enum_ptrs`
  - `ref_struct_reloc_ptrs`
- `ptr_ref_unmark` and `ptr_ref_mark` manage l_mark/pmark bits for full and packed refs.
- `refs_clear_marks` clears marks across mixed packed/full ref blocks.
- `refs_set_reloc`:
  - Computes freed bytes within a refs object.
  - Preserves packed-ref alignment groups.
  - Stores relocation info in packed integer values or unused `r_size` fields.
  - Handles cases where relocation cannot fit into `r_size`.
- `igc_reloc_refs` relocates the contents of marked refs, including:
  - files/devices/structs/fonts
  - dictionaries
  - arrays and packed arrays
  - names
  - strings
  - op arrays
- `igc_reloc_ref_ptr` relocates a pointer into a ref block by scanning forward for relocation metadata.
- `refs_compact` copies only marked refs, clears marks, pads alignment, creates free block space if possible, and recreates a final sentinel ref.

Dependencies and interactions:
- Uses name-table relocation helpers from `iname.h`.
- Uses string relocation macros from the GC procedure vector.
- Used directly by `igc.c`.

Risks and notes:
- The file itself describes `igc_reloc_ref_ptr` as intrinsically inefficient.
- Uses careful overlap-safe copying for refs.
- Contains architecture/alignment conditionals for packed refs.

Research relevance:
- This is the specialized compacting collector for PostScript object references, a central piece of interpreter VM correctness.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/igcref.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/igcstr.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/igcstr.c

Implements string marking, relocation, and compaction for the Ghostscript GC.

Key points:
- Strings are marked using chunk-level bitmaps (`smark`).
- `gc_strings_set_marks` clears or fills string marks for a chunk.
- `gc_mark_string` marks/unmarks a known-chunk byte range word-at-a-time, with byte-order handling.
- `gc_string_mark` locates a string’s chunk and applies marking, with debug validation for string range correctness.
- `gc_strings_clear_reloc` prepares relocation metadata by marking all strings and computing relocation.
- `gc_strings_set_reloc` computes relocation offsets per `string_data_quantum`, using a zero-bit count table.
- `igc_reloc_string` relocates mutable strings using `sreloc` and `smark`.
- `igc_reloc_const_string` and `igc_reloc_param_string` adapt relocation for const and parameter strings; parameter strings are relocated only when non-persistent.
- `gc_strings_compact` compacts marked string bytes downward from the top of the chunk and fills reclaimed memory.

Dependencies and interactions:
- Uses `gc_locate` from `ilocate.c`.
- Called by object GC in `igc.c`.
- Works with chunk fields `sbase`, `smark`, `sreloc`, `sdest`, `ctop`, and `climit`.

Research relevance:
- Specialized string allocator compaction layer for the interpreter’s mixed object/string chunks.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/igcstr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/igcstr.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/igcstr.h

Declares internal string GC APIs.

Key points:
- Declares `gc_locate` from `ilocate.c`.
- Declares string GC functions exported by `igcstr.c`:
  - `gc_strings_set_marks`
  - `gc_string_mark`
  - `gc_strings_clear_reloc`
  - `gc_strings_set_reloc`
  - `gc_strings_compact`
  - `igc_reloc_string`
  - `igc_reloc_const_string`
  - `igc_reloc_param_string`

Dependencies and interactions:
- Used by `igc.c` and `igcref.c` through relocation macros/procs.

Research relevance:
- Internal interface between the main object GC and string-specific compaction.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/igcstr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/igstate.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/igstate.h

Defines interpreter-specific graphics state data layered on top of library `gs_state`.

Key points:
- The library graphics state is mostly opaque to the interpreter, but the interpreter attaches client data made of refs.
- Defines `igstate_obj`, a wrapper ref structure used for gstate objects so save/restore can manipulate an intermediate object rather than copying full `gs_state`s.
- Defines helper macro `igstate_ptr`.
- Defines ref-bearing parameter groups for:
  - DeviceN names/tint transform
  - CIE decode/procedure refs
  - CIE rendering transforms
  - Separation name/tint transform
  - Indexed color procedure
- Defines `ref_colorspace` holding the current color space array and associated procedure refs.
- Defines `int_gstate`, containing refs for:
  - dash pattern
  - screen and transfer procedures
  - black generation and undercolor removal
  - colorspace and pattern
  - color rendering dictionary/procs
  - UseCIEColor
  - halftone
  - pagedevice
  - remap color info
  - opacity and shape masks
- Provides `int_gstate_map_refs` for enumerating refs in the structure.
- Declares `int_gstate_alloc`.
- Defines `gs_int_gstate`, `igs`, and `istate` helpers.

Dependencies and interactions:
- Used by graphics-state operators and color/halftone/page-device code.
- Tied to `e_RemapColor` in `ierrors.h`.

Research relevance:
- Captures all interpreter-visible graphics state refs that must participate in GC and save/restore.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/igstate.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iht.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iht.h

Declares halftone screen helper procedures exported by `zht.c`.

Key points:
- `zscreen_params` parses screen halftone parameters into `gs_screen_halftone`.
- `zscreen_enum_init` initializes screen enumeration against a halftone order, screen params, procedure ref, operand pop count, finish proc, and VM space index.

Dependencies and interactions:
- Used by `zht1.c` and `zht2.c`.
- Works with `gx_ht_order`, `gs_screen_halftone`, `ref`, and operator finish procedures.

Research relevance:
- Shared interface for PostScript halftone/screen operator implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iht.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iimage.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iimage.h

Declares image operator entry points and auxiliary image parameters.

Key points:
- Defines `image_params` for interpreter-side parameters not in core image structs:
  - `MultipleDataSources`
  - `DataSource[]`
  - `pDecode`
- Declares:
  - `data_image_params`
  - `pixel_image_params`
  - `zimage_setup`
  - `image1_setup`
- Supports data and pixel image parameter extraction, including alpha and component-count constraints.

Dependencies and interactions:
- Exported by `zimage.c`.
- Used by `zimage3.c`, `ztrans.c`, and `zdpnext.c`.

Research relevance:
- Interpreter-side parsing/setup interface for PostScript image operators.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iimage.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iimage2.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iimage2.h

Declares Level 2 image support for images without explicit source data.

Key points:
- Declares `process_non_source_image`.
- Comments note this is not used by standard Level 2 but needed by DPS/NeXT-related modules.
- Takes interpreter context, common image parameters, and a client name.

Dependencies and interactions:
- Exported by `zimage2.c`.
- Used by `zdps.c` and `zdpnext.c`.

Research relevance:
- Small compatibility hook for non-standard image processing paths.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iimage2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iinit.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iinit.c

Initializes Ghostscript interpreter objects, dictionaries, errors, and operator tables.

Key points:
- Defines dictionary size defaults:
  - `SYSTEMDICT_SIZE`, `SYSTEMDICT_LEVEL2_SIZE`, `SYSTEMDICT_LL3_SIZE`
  - `LEVEL2DICT_SIZE`, `LL3DICT_SIZE`, `FILTERDICT_SIZE`
- Defines `gs_error_names[]` from `ERROR_NAMES`.
- Defines global and local `op_array_table` instances.
- Provides `i_initial_enter_name` and `i_initial_remove_name`.
- Defines initial dictionaries:
  - `level2dict`
  - `ll3dict`
  - `globaldict`
  - `userdict`
  - `filterdict`
- Determines compiled operator language level by scanning `op_defs_all`.
- `gs_have_level2` reports whether Level 2 operators are compiled in.
- `obj_init`:
  - Allocates `systemdict`.
  - Calls `gs_interp_init`.
  - Creates dictionaries referenced by op definitions.
  - Sets up the dictionary stack.
  - Enters dictionaries into `systemdict`.
  - Resets interpreter.
  - Enters `null`, `true`, `false`.
  - Builds `ErrorNames`.
- `zop_init`:
  - Runs initialization procedures embedded in op definition arrays.
  - Enters product/revision/copyright metadata.
- `op_init`:
  - Inserts operator refs into appropriate dictionaries.
  - Skips internal `%` operators and duplicate special-index operators.
  - Allocates global and local op-array tables.
  - Registers op-array tables and name-index tables as GC roots.

Dependencies and interactions:
- Called from `imain.c` during `gs_main_init1/init2`.
- Uses name table, dictionary stack, op definitions, interpreter initialization, and allocator roots.

Research relevance:
- Startup hub that creates the PostScript dictionary/operator environment before init files run.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iinit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iinit.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iinit.h

Declares internal initialization stages exported by `iinit.c`.

Key points:
- Declares the required order:
  - `obj_init`
  - `zop_init`
  - `op_init`
- Declares `gs_have_level2`.
- Notes `gs_have_level2` checks compiled operators, not the runtime language level.

Dependencies and interactions:
- Used by `imain.c` during staged interpreter initialization.

Research relevance:
- Compact contract for interpreter object/operator initialization ordering.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iinit.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ijs.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ijs.mak

Partial makefile for building the IJS client library within Ghostscript.

Key points:
- Users must define:
  - `IJSSRCDIR`
  - `IJSEXECTYPE`
  - `BINDIR`
- Defines source/generated/object directory variables for IJS.
- Defines IJS include and compiler flags.
- Builds `ijslib.dev` from:
  - `ijs.o`
  - `ijs_server.o`
  - `ijs_client.o`
  - `ijs_exec_$(IJSEXECTYPE).o`
- Provides rules for Unix and Windows process-control implementations:
  - `ijs_exec_unix.c`
  - `ijs_exec_win.c`
- Provides clean targets:
  - `ijs.clean`
  - `ijs.config-clean`
  - `ijs.clean-not-config-clean`
- Provides example client/server build targets:
  - `ijs_client_example`
  - `ijs_server_example`
- Comments flag known issues:
  - clean target is too broad: “WRONG. MUST DELETE OBJ AND GEN FILES SELECTIVELY.”
  - example linking is not portable / policy FIXME.
  - Windows exec source cannot use `/Za` because it needs `windows.h`.

Dependencies and interactions:
- Related to `gdevijs.c` and external IJS printer/server integration.
- Consumed by the larger Ghostscript make system.

Research relevance:
- Build-system glue for Ghostscript’s IJS inkjet-server client support.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ijs.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ilevel.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ilevel.h

Defines interpreter language-level convenience macros.

Key points:
- `LANGUAGE_LEVEL` maps to `i_ctx_p->language_level`.
- `LL2_ENABLED` checks `LANGUAGE_LEVEL >= 2`.
- `LL3_ENABLED` checks `LANGUAGE_LEVEL >= 3`.
- `level2_enabled` aliases `LL2_ENABLED` for backward compatibility.

Dependencies and interactions:
- Used throughout interpreter operators to gate Level 2/3 behavior.

Research relevance:
- Simple but widespread runtime language-level control contract.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ilevel.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ilocate.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ilocate.c

Implements chunk lookup and debug validation for Ghostscript ref memory.

Key points:
- `gc_locate` locates a pointer in chunks across:
  - current memory
  - stable allocator
  - local/global counterpart space
  - save levels
  - system space
- Used primarily by string GC and debug validation.
- Debug-only validation includes:
  - `ialloc_validate_spaces`
  - `ialloc_validate_memory`
  - `ialloc_validate_chunk`
  - `ialloc_validate_object`
- Temporarily saves allocator state to make current allocation chunks appear valid during validation.
- Validates:
  - freelist object types and sizes
  - object sizes and type descriptors
  - refs and packed refs
  - names and name strings
  - strings
  - arrays, packed arrays, dictionaries
  - struct pointers enumerated through type descriptors
- Optional `IGC_PTR_STABILITY_CHECK` detects references from more stable spaces to less stable spaces.
- Non-debug builds provide no-op validation functions.

Dependencies and interactions:
- Used by `igc.c` and `igcstr.c`.
- Uses `iname.h`, packed-ref utilities, dictionary layout, and allocator/chunk internals.

Research relevance:
- GC support utility for locating referents and diagnosing heap/reference corruption.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ilocate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/imain.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/imain.c

Provides common top-level support for Ghostscript interpreter front ends.

Key points:
- `get_minst_from_memory` retrieves the interpreter instance through library context backpointers.
- `gs_main_alloc_instance` allocates and initializes `gs_main_instance`.
- `gs_main_init0`:
  - calls platform init
  - resets debug flags
  - records base time
  - allocates library path containers
- `gs_main_init1`:
  - initializes interpreter allocator spaces
  - initializes library level 1
  - initializes save machinery
  - creates name table and roots it
  - calls `obj_init`
  - initializes plugins
- `gs_main_init2`:
  - runs `zop_init`
  - initializes IO devices
  - calls `op_init`
  - publishes `INITFILES`, `EMULATORS`, and `LIBPATH`
  - runs the standard init file or compiled init string
  - sets display callback if present
  - initializes readline
- `gs_main_interpret` wraps `gs_interpret` and handles `e_NeedStdin`, `e_NeedStdout`, and `e_NeedStderr` callouts by moving data through interpreter stacks and resuming with a null ref plus `zpop`.
- Search path helpers:
  - `gs_main_add_lib_path`
  - `gs_main_set_lib_paths`
  - `gs_main_lib_open`
- Execution helpers:
  - `gs_main_run_file`
  - `gs_main_run_file_open`
  - `gs_main_run_string`
  - `gs_main_run_string_with_length`
  - suspendable string begin/continue/end
- Operand stack C API:
  - `gs_push_boolean/integer/real/string`
  - `gs_pop_boolean/integer/real/string`
- `gs_main_finit`:
  - collects temporary filenames
  - performs final global reclaim
  - uninstalls page device and closes current device
  - flushes stdout/stderr files
  - finalizes readline
  - restores all allocations
  - finalizes plugins
  - closes redirected stdout
  - unlinks temp files
  - calls `gs_lib_finit`
- Provides `gs_to_exit`, `gs_to_exit_with_code`, `gs_abort`, resource-usage printing, and stack dumping.

Dependencies and interactions:
- Calls `iinit.c`, interpreter core, allocator/save machinery, plugin system, devices, file/path code, and error codes.
- Front-end API documented in `imain.h` and driven by `imainarg.c`.

Risks and notes:
- Header comments call instance lookup from memory a hack.
- Some init and platform/device behavior is order-sensitive.

Research relevance:
- Main lifecycle engine for embedding/running/finalizing the Ghostscript interpreter.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/imain.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/imain.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/imain.h

Declares the public-ish front-end API to `imain.c`.

Key points:
- Defines opaque `gs_main_instance`.
- Declares:
  - `get_minst_from_memory`
  - `gs_main_alloc_instance`
  - `gs_main_init0`
  - `gs_main_init1`
  - `gs_main_init2`
  - `gs_main_add_lib_path`
  - `gs_main_set_lib_paths`
  - `gs_main_lib_open`
- Documents the three initialization stages and common command-line switch equivalents for C API clients.
- Declares execution APIs for files and strings, including suspendable string input.
- Documents return conventions: `0`, `e_Quit`, `e_Fatal`, with exit code returned separately.
- Declares operand stack push/pop helpers.
- Declares `gs_main_dump_stack` and `gs_main_finit`.

Dependencies and interactions:
- Used by front ends and `imainarg.c`.
- Includes `gsexit.h` exported by `imain.c`.

Research relevance:
- Top-level API contract for embedding and driving the Ghostscript interpreter.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/imain.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/imainarg.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/imainarg.c

Implements command-line parsing and dispatch for Ghostscript.

Key points:
- `gs_main_init_with_args`:
  - initializes argument reader with `@` file expansion support
  - calls `gs_main_init0`
  - reads `GS_LIB` and `GS_OPTIONS`
  - sets default library path
  - prescans `--help` and `--version`
  - processes switches and filenames
  - finishes init with `gs_main_init2`
- `gs_main_run_start` runs `systemdict /start get exec`.
- `swproc` handles switches:
  - `-` / `-_` stdin execution modes
  - `--`, `-+`, `-@` command-line args for PostScript program
  - `-A`, `-E`, `-Z`, `-T` debug/log flags
  - `-B` buffered run-string size
  - `-c` inline PostScript code
  - `-f`, `-F` file execution
  - `-g`, `-r` device geometry/resolution
  - `-h`, `-?`, `-v`
  - `-I` library path
  - `-K`, `-M`, `-N` memory/name table settings
  - `-P` current-directory search policy
  - `-q` quiet startup
  - `-d/-D`, `-s/-S` systemdict definitions
  - `-u` undefine name
  - `-X` debug test hook
- `-d` parses a PostScript token; executable names are restricted to `null`, `true`, or `false`.
- `-sstdout=...` supports stdout redirection to files or stderr.
- File execution:
  - `argproc` dispatches direct or buffered execution.
  - `run_buffered` feeds file bytes through suspendable `run_string`.
  - `runarg` hex-escapes file/argument strings before building PostScript snippets.
- Error/finish behavior:
  - flushes output and display
  - dumps stacks for unexpected interpreter errors
- Help output prints revision, usage, emulators, sorted device list, search paths, and docs/bug-report trailer.

Dependencies and interactions:
- Wraps `imain.c` API.
- Uses `gsargs`, platform env/file APIs, scanner, stacks, dictionaries, and device registry.

Risks and notes:
- Several switches initialize only as much of the interpreter as needed.
- Path and option environment inputs are copied into Ghostscript heap allocations.
- Help device list sorting falls back to unsorted output if allocation fails.

Research relevance:
- User-facing CLI semantics and translation layer from argv/env into interpreter state and PostScript snippets.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/imainarg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/imainarg.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/imainarg.h

Declares argc/argv front-end helpers.

Key points:
- Defines opaque `gs_main_instance` if needed.
- Declares:
  - `gs_main_init_with_args`
  - `gs_main_run_start`
- Notes `argv` should conceptually be `const char *[]`, but ANSI C conventions expose writable strings.

Dependencies and interactions:
- Used by simple Ghostscript program front ends that want command-line behavior.

Research relevance:
- Small high-level API for command-line-compatible interpreter invocation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/imainarg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/imemory.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/imemory.h

Defines interpreter extensions to the Ghostscript allocator interface.

Key points:
- Includes `ivmspace.h` and `gsalloc.h`.
- Declares ref-array allocation APIs:
  - `gs_alloc_ref_array`
  - `gs_resize_ref_array`
  - `gs_free_ref_array`
- Declares string-ref allocation:
  - `gs_alloc_string_ref`
- Declares `gs_register_ref_root`.
- Defines `gs_dual_memory_t`, representing interpreter VM allocation state:
  - current allocator
  - system/global/local `vm_spaces`
  - current space
  - GC reclaim hook
  - store-check masks
- Notes:
  - system VM is immune to even outermost save/restore.
  - in Level 1 configs global may equal local, but not necessarily in a Level 2 executable running Level 1 mode.
  - embedded `gs_dual_memory_t` pointers must not persist across GC.
- Provides structure descriptor macro for `gs_dual_memory_t`.

Dependencies and interactions:
- Used by interpreter allocation, save/restore, GC, stacks, names, and dictionaries.

Research relevance:
- Defines the interpreter’s local/global/system VM abstraction over the base memory manager.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/imemory.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iminst.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iminst.h

Defines the concrete `gs_main_instance` and library search path structure.

Key points:
- Defines `gs_file_path`:
  - `container`
  - `list`
  - env path
  - final/default path
  - user-specified count
- Defines stdio buffer sizes for stdin/stdout/stderr callouts.
- Defines `gs_main_instance_s` fields:
  - heap allocator
  - memory chunk size
  - name table size
  - run buffer size
  - init stage
  - user error mode
  - current-directory search policy
  - run-start flag
  - library path
  - base time
  - readline data
  - stdio buffers
  - error object
  - display callback
  - current interpreter context
- Defines default init values through `gs_main_instance_default_init_values` and external `gs_main_instance_init_values`.

Dependencies and interactions:
- Used internally by `imain.c` and `imainarg.c`.
- Clients should treat `gs_main_instance` as opaque despite the definition being here.

Research relevance:
- Captures interpreter instance state and lifecycle configuration.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iminst.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iname.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iname.c

Implements Ghostscript interpreter name-table lookup, allocation, GC integration, and restore cleanup.

Key points:
- Defines public `name_max_string`.
- Uses generated/permutation data:
  - `hash_permutation`
  - `nt_1char_names`
- Defines structure descriptors for:
  - `name_sub_table`
  - `name_string_sub_table_t`
  - `name_table`
- `names_init`:
  - allocates the name table
  - sets maximum subtable count
  - initializes one-character names as permanent foreign strings
  - reconstructs the free list
- `names_ref`:
  - hashes strings
  - fast-paths empty and one-character names
  - looks up existing names
  - enters new names depending on `enterflag`
  - returns `e_undefined`, `e_limitcheck`, or `e_VMerror` as appropriate
- String/name conversions:
  - `names_string_ref`
  - `names_from_string`
  - `names_enter_string`
- Cache/index helpers:
  - `names_invalidate_value_cache`
  - `names_index`
  - `names_index_ref`
  - `names_index_ptr`
  - `names_next_valid_index`
- GC support:
  - `names_unmark_all`
  - `names_mark_index`
  - `names_ref_sub_table`
  - `names_index_sub_table`
  - `names_index_string_sub_table`
  - `names_trace_finish`
- `names_trace_finish` removes unmarked names from hash chains, clears string data, rebuilds the free list, and may free empty subtables.
- `names_restore` marks only names older than a save and then reuses trace finish cleanup.
- Internal allocation:
  - `name_alloc_sub`
  - `name_free_sub`
  - `name_scan_sub`
- GC descriptors enumerate and relocate subtable pointers and relocate non-foreign name strings.

Dependencies and interactions:
- Used through macros in `iname.h`.
- GC in `igc.c` marks names referenced by refs and operator arrays.
- `igcref.c` relocates name refs by relocating their containing subtable.

Research relevance:
- Core symbol table for PostScript names, tightly coupled to dictionaries, GC, and save/restore.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iname.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iname.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iname.h

Defines interpreter-facing name-table macros.

Key points:
- Includes `inames.h`.
- Provides convenience macros that route through `mem->gs_lib_ctx->gs_name_table`:
  - `name_memory`
  - `name_ref`
  - `name_string_ref`
  - `name_enter_string`
  - `name_from_string`
  - `name_eq`
  - `name_invalidate_value_cache`
  - `name_index`
  - `name_index_ptr`
  - `name_index_ref`
  - `name_next_valid_index`
  - `name_mark_index`
  - `name_ref_sub_table`
- Notes these APIs refer to the interpreter’s distinguished name-table instance.

Dependencies and interactions:
- Used by most interpreter code that needs name lookup or name/string conversion.
- Wraps lower-level `names_*` APIs implemented in `iname.c`.

Research relevance:
- Main include-level access point for interpreter-wide PostScript name handling.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iname.h -->