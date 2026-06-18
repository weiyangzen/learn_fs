# Group Research: group_1575_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_ierrors_h_sources_o_f95f356d2e68

Scope checked against `Docs/research_subset_a.md`: `sources/os/plan9/plan9` is included in subset A. All listed files were read completely.

This group covers Ghostscript interpreter infrastructure in the Plan 9 source tree: error codes, execution stack data, font/filter/image/function APIs, graphics state, compacting GC, initialization, main interpreter lifecycle, command-line handling, and name-table management.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ierrors.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ierrors.h

Defines interpreter-level Ghostscript error codes and error-name lists.

Key points:
- Explicitly warns this is interpreter-only; graphics library code should use `gserrors.h`.
- Uses non-negative returns for success and negative integers for failures.
- Declares `gs_error_names[]`, populated from `ERROR_NAMES` in `iinit.c`.
- Defines Level 1 PostScript errors from `e_unknownerror (-1)` through `e_VMerror (-25)`.
- Defines Level 2/DPS additions: `e_configurationerror`, `e_invalidcontext`, `e_undefinedresource`, `e_unregistered`, and NeXT DPS `e_invalidid`.
- Defines internal pseudo-errors for fatal/quit/interpreter exit, color remap retry, exec-stack underflow, VM reclaim, incremental input, stdio callouts, and usage-info exit.
- `ERROR_IS_INTERRUPT(ecode)` treats `e_interrupt` and `e_timeout` as re-execute cases.

Research relevance:
- Central interpreter control-flow contract for PostScript errors, normal quits, fatal exits, GC-triggering VM reclaim, input suspension, and console callouts.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ierrors.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iesdata.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iesdata.h

Defines the execution stack data structure.

Key points:
- Includes `isdata.h`.
- Defines `exec_stack_t` with the actual `ref_stack_t stack` and a cached `ref *current_file`.
- `current_file` points to the topmost executable file on the execution stack, or null.
- Comments document the cache invariant and require stack push/pop code to clear or check the cache when executable files may be involved.
- Provides `public_st_exec_stack()` descriptor macro using `st_ref_stack` suffix storage metadata.
- Notes `current_file` is cleared by GC and is not declared as a traced pointer.

Research relevance:
- Small performance/data-integrity component for fast `currentfile` lookup in the interpreter.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iesdata.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iestack.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iestack.h

Defines execution-stack pointer aliases and current-file cache helpers.

Key points:
- Includes `iesdata.h` and `istack.h`.
- Defines `es_ptr` and `const_es_ptr`.
- Provides:
  - `estack_clear_cache(pes)`
  - `estack_set_cache(pes, pref)`
  - `estack_check_cache(pes)`
- `estack_check_cache` caches the top stack entry if it is an executable file ref.

Research relevance:
- Documents and enforces the coupling between execution-stack mutation and `currentfile` cache correctness.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iestack.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifapi.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifapi.h

Defines Ghostscript’s Font API plugin interface.

Key points:
- Includes `iplugin.h`.
- Defines `FracInt`, `FAPI_retcode`, `fapi_font_feature`, `FAPI_metrics_type`, and FAPI descriptor structures.
- `FAPI_font` carries server font state, client font state, font source path/subfont flags, character data, and callbacks for font features, subrs, glyphs, and serialized TrueType data.
- `FAPI_path` abstracts outline callbacks: `moveto`, `lineto`, `curveto`, `closepath`.
- `FAPI_font_scale`, `FAPI_metrics`, and `FAPI_raster` describe scaling, metrics, and 1-bit raster output.
- `FAPI_server` extends `i_plugin_instance` and exposes callbacks for opening a backend, acquiring scaled fonts, decoding IDs, metrics, raster/outline retrieval, and release.
- Comments clarify that Ghostscript cannot tell the server when scaled fonts are no longer used; the server or bridge must cache and evict internally.

Research relevance:
- Important interpreter/plugin boundary for delegating font scaling, metrics, rasterization, and outline extraction to external font backends.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifapi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifcid.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifcid.h

Declares internal CID font helper APIs exported by `zfcid.c`.

Key points:
- `cid_font_system_info_param` extracts `CIDSystemInfo` from a CIDFont dictionary.
- `cid_font_data_param` extracts CIDFontType 0/2 data into `gs_font_cid_data`, including `GlyphDirectory`.

Research relevance:
- Narrow bridge for CID-keyed font dictionary parsing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifcid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifilter.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifilter.h

Defines interpreter-level filter creation support.

Key points:
- Includes `istream.h` and `ivmspace.h`.
- Declares `filter_read` and `filter_write`, which create stream filters from operator operands, a stream template, optional state, and VM-space metadata.
- Declares simplified no-parameter/no-state helpers `filter_read_simple` and `filter_write_simple`.
- Declares temporary-stream helpers `filter_mark_temp` and `filter_mark_strm_temp`.
- Declares `filter_report_error`, a standard filter error reporter that records messages in `$error.errorinfo`.
- Defines `stream_proc_state` for procedure-based streams, storing EOF state, current data index, procedure ref, and data ref.
- Provides GC descriptor macro `private_st_stream_proc_state()`.
- Declares `s_is_proc`.

Research relevance:
- Central adapter from PostScript filter operators to Ghostscript stream templates and VM allocation rules.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifilter.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifilter2.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifilter2.h

Declares Level 2 filter setup helpers.

Key points:
- Exports setup routines from `zfdecode.c`:
  - `zcf_setup` for CCITTFax
  - `zlz_setup` for LZW
  - `zpd_setup` for PNG/TIFF predictor differencing
  - `zpp_setup` for PNG predictor
- `zcf_setup` takes `gs_ref_memory_t *imem`, reflecting VM-aware parameter storage.

Research relevance:
- Small shared interface for Level 2 decode/filter parameter parsing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifilter2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifont.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifont.h

Defines interpreter-side font client data and shared font procedures.

Key points:
- Includes `gsccode.h` and `gsstype.h`.
- Defines `font_data`, interpreter client data attached to library `gs_font` objects.
- Common refs include font dictionary, `BuildChar`, `BuildGlyph`, `Encoding`, `CharStrings`, and `GlyphNames2Unicode`.
- Type-specific union stores Type 1, Type 42/CIDFontType2, and CIDFontType0 refs.
- Exports `st_font_data`, `pfont_data`, and `pfont_dict`.
- Declares `font_bbox_param`, `font_param`, `zfont_mark_glyph_name`, and `zfont_info`.

Research relevance:
- Core interpreter/library boundary for PostScript font objects and GC-visible font metadata.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifont.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifont1.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifont1.h

Declares utilities for Type 1, Type 2, and other CharString-based fonts.

Key points:
- Defines `charstring_font_refs_t` with refs to `Private`, `OtherSubrs`, `Subrs`, `GlobalSubrs`, and `no_subrs`.
- Defines Type 1 default `lenIV` as `4`.
- Declares `charstring_font_get_refs`, `charstring_font_params`, `charstring_font_init`, and `build_charstring_font`.
- Used by Type 1/2/CIDFontType0 builders to bridge PostScript font dictionaries or FDArray entries into `gs_type1_data` and `gs_font_type1`.

Research relevance:
- Shared parsing/build path for CharString font data and subroutine dictionaries.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifont1.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifont2.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifont2.h

Declares Type 2-specific font parameter parsing.

Key points:
- Defines Type 2 default `lenIV` as `-1`.
- Declares `type2_font_params`, which extracts Type 2 parameters beyond common Type 1/Type 2 CharString parameters.
- Depends on `charstring_font_refs_t` and `gs_type1_data`.

Research relevance:
- Small specialization point for Type 2/CFF-style font handling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifont2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifont42.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifont42.h

Declares Type 42 and CIDFontType 2 TrueType font build helpers.

Key points:
- `build_gs_TrueType_font` builds Type 11 or Type 42 fonts.
- `font_string_array_param` validates/extracts string arrays while returning the value even on wrong type.
- `font_GlyphDirectory_param` returns 0 if present, 1 if absent, or an error.
- `font_gdir_get_outline` retrieves glyph outlines from `GlyphDirectory`, returning an empty string if missing or out of range.
- `string_array_access_proc` accesses byte ranges across arrays of strings, used for `sfnts` and `CIDMap`.

Research relevance:
- Interface for interpreter-side TrueType and CID TrueType font materialization.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifont42.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifrpred.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifrpred.h

Declares read-side predictor filter helper.

Key points:
- Exports `filter_read_predictor` from `zfdecode.c` for `zfzlib.c`.
- Signature takes interpreter context, operand pop count, stream template, and stream state.

Research relevance:
- Shared hook for composing read filters with PNG/TIFF predictor processing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifrpred.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifunc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifunc.h

Defines internal interpreter APIs for PostScript/PDF Functions.

Key points:
- Includes `gsfunc.h`.
- Defines `build_function_proc`, `build_function_proc_t`, and `build_function_type_t`.
- Declares function builder table and count.
- Declares `fn_build_function`, `fn_build_sub_function`, `fn_build_float_array`, `fn_build_float_array_forced`, `ref_function`, and `zexecfunction`.
- `fn_build_float_array` handles optional/required arrays and even-length constraints.
- `fn_build_float_array_forced` accepts scalar numeric input as a one-element array.

Research relevance:
- Function-object construction and execution API used by gradients, transfer functions, and PDF function semantics.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifunc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifwpred.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifwpred.h

Declares write-side predictor filter helper.

Key points:
- Exports `filter_write_predictor` from `zfilter2.c` for `zfzlib.c`.
- Signature mirrors read predictor setup: context, pop count, stream template, and stream state.

Research relevance:
- Shared hook for encoded output filters that need predictor preprocessing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifwpred.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/igc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/igc.c

Implements Ghostscript’s interpreter garbage collector for ref memory.

Key points:
- Defines collector procedure vector `igc_procs` for struct, string, const string, parameter string, ref pointer, and ref-array relocation.
- Defines pointer descriptors for structs, strings, const strings, and refs.
- Main entry point is `gs_gc_reclaim(vm_spaces *pspaces, bool global)`.
- Supports local and global collection, stable allocators, and save levels.
- Registers allocators as roots so change/save lists are traced.
- Clears marks, traces roots, traces non-local chunks during local GC, handles names, refs, arrays, dictionaries, strings, devices, files, fonts, structs, and op arrays.
- Uses a segmented mark stack built from a stack default segment, large free blocks, and heap extensions.
- Handles mark-stack overflow by recording chunk rescan intervals.
- Computes relocation for objects and strings, relocates chunk and root pointers, compacts object/string storage, frees empty chunks, and updates allocator statistics.
- Provides debug phase logging, validation hooks through `ilocate.c`, and relocation printing.
- Exports `gcst_get_memory_ptr`.

Research relevance:
- Core memory-management engine for the Ghostscript interpreter VM: mark, relocate, compact, finalize, and free.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/igc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/igc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/igc.h

Defines internal GC interfaces and state.

Key points:
- Declares `gs_gc_reclaim`.
- Defines `struct_shared_procs_s` for shared genus operations: `clear_reloc`, `set_reloc`, and `compact`.
- Defines `gc_state_s` with GC procs, chunk locator, VM spaces, minimum collected space, untraced relocation flag, heap pointer, name table pointer, and debug container chunk.
- Declares ref mark/unmark helpers exported by `igcref.c`.
- Declares allocator validation functions exported by `ilocate.c`.
- Declares `gcst_get_memory_ptr`.
- Defines `print_reloc` debug macro.

Research relevance:
- Primary internal contract tying together Ghostscript’s struct/ref/string compacting GC.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/igc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/igcref.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/igcref.c

Implements GC support for Ghostscript `ref` objects and packed refs.

Key points:
- Defines special structure descriptor `st_refs`.
- Defines shared procs for ref blocks: `refs_clear_reloc`, `refs_set_reloc`, and `refs_compact`.
- Defines helper procs for structs containing embedded refs: `ref_struct_clear_marks`, `ref_struct_enum_ptrs`, and `ref_struct_reloc_ptrs`.
- `ptr_ref_unmark` and `ptr_ref_mark` manage mark bits for full refs and packed refs.
- `refs_clear_marks` clears marks across mixed packed/full ref blocks.
- `refs_set_reloc` computes freed bytes, preserves packed-ref alignment groups, stores relocation in packed integer values or unused `r_size` fields, and handles relocation values too large for `r_size`.
- `igc_reloc_refs` relocates marked refs for files, devices, structs, fonts, dictionaries, arrays, packed arrays, names, strings, and op arrays.
- `igc_reloc_ref_ptr` relocates a pointer into a ref block by scanning forward for relocation metadata; comments call this intrinsically inefficient.
- `refs_compact` copies only marked refs, clears marks, pads alignment, creates a free block when possible, and recreates the final sentinel ref.
- The Plan 9 copy pads `new_size` using `new_size & (sizeof(ref) - 1)` in `refs_compact`, a power-of-two alignment mask.

Research relevance:
- Specialized compacting collector for PostScript object references, central to interpreter VM correctness.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/igcref.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/igcstr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/igcstr.c

Implements string marking, relocation, and compaction for the Ghostscript GC.

Key points:
- Strings are marked through chunk-level bitmaps (`smark`).
- `gc_strings_set_marks` clears or fills string marks for a chunk.
- `gc_mark_string` marks/unmarks a known-chunk byte range word-at-a-time, with byte-order handling.
- `gc_string_mark` locates a string’s chunk and applies marking, with debug validation for ranges.
- `gc_strings_clear_reloc` prepares relocation metadata by marking all strings and computing relocation.
- `gc_strings_set_reloc` computes relocation offsets per `string_data_quantum` using a zero-bit count table.
- `igc_reloc_string` relocates mutable strings using `sreloc` and `smark`.
- `igc_reloc_const_string` and `igc_reloc_param_string` adapt relocation for const and parameter strings; parameter strings are relocated only when non-persistent.
- `gc_strings_compact` compacts marked string bytes downward from the top of the chunk and fills reclaimed memory.

Research relevance:
- Specialized string allocator compaction layer for the interpreter’s mixed object/string chunks.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/igcstr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/igcstr.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/igcstr.h

Declares internal string GC APIs.

Key points:
- Declares `gc_locate` from `ilocate.c`.
- Declares string GC functions exported by `igcstr.c`: mark setup, single-string marking, relocation clearing/setting, compaction, and mutable/const/parameter string relocation helpers.

Research relevance:
- Internal interface between the main object GC and string-specific compaction.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/igcstr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/igstate.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/igstate.h

Defines interpreter-specific graphics state data layered on top of library `gs_state`.

Key points:
- The interpreter treats the library graphics state mostly as opaque, but attaches client data made of refs.
- Defines `igstate_obj`, a wrapper used for gstate objects so save/restore can manipulate an intermediate object instead of copying full `gs_state`s.
- Defines ref-bearing parameter groups for DeviceN, CIE, CIE rendering, Separation, and Indexed color procedures.
- Defines `ref_colorspace` for the current color-space array and associated procedure refs.
- Defines `int_gstate`, containing refs for dash pattern, screen and transfer procedures, black generation, undercolor removal, colorspace, pattern, color rendering, UseCIEColor, halftone, pagedevice, remap color info, opacity mask, and shape mask.
- Provides `int_gstate_map_refs` for GC enumeration.
- Declares `int_gstate_alloc`.
- Defines `gs_int_gstate`, `igs`, and `istate` helpers.

Research relevance:
- Captures interpreter-visible graphics state refs that must participate in GC, save/restore, color remapping, halftones, page devices, and transparency state.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/igstate.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iht.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iht.h

Declares halftone screen helper procedures exported by `zht.c`.

Key points:
- `zscreen_params` parses screen halftone parameters into `gs_screen_halftone`.
- `zscreen_enum_init` initializes screen enumeration against a halftone order, screen params, procedure ref, operand pop count, finish proc, and VM space index.
- Used by `zht1.c` and `zht2.c`.

Research relevance:
- Shared interface for PostScript halftone/screen operator implementation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iht.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iimage.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iimage.h

Declares image operator entry points and auxiliary image parameters.

Key points:
- Defines `image_params` for interpreter-side parameters not in core image structs: `MultipleDataSources`, `DataSource[]`, and `pDecode`.
- Declares `data_image_params`, `pixel_image_params`, `zimage_setup`, and `image1_setup`.
- Supports data and pixel image parameter extraction, including source requirements, component count, max bits per component, and alpha handling.
- Exported by `zimage.c` for image-related modules.

Research relevance:
- Interpreter-side parsing/setup interface for PostScript image operators.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iimage.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iimage2.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iimage2.h

Declares Level 2 image support for images without explicit source data.

Key points:
- Declares `process_non_source_image`.
- Comments note this is not used by standard Level 2 but is needed by DPS/NeXT-related modules.
- Takes interpreter context, common image parameters, and a client name.

Research relevance:
- Small compatibility hook for non-standard image processing paths.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iimage2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iinit.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iinit.c

Initializes Ghostscript interpreter objects, dictionaries, errors, and operator tables.

Key points:
- Defines dictionary size defaults for `systemdict`, `level2dict`, `ll3dict`, and `filterdict`.
- Defines `gs_error_names[]` from `ERROR_NAMES`.
- Defines global and local `op_array_table` instances.
- Provides `i_initial_enter_name` and `i_initial_remove_name`.
- Defines initial dictionaries: `level2dict`, `ll3dict`, `globaldict`, `userdict`, and `filterdict`.
- Determines compiled operator language level by scanning `op_defs_all`; `gs_have_level2` reports whether Level 2 operators are compiled in.
- `obj_init` allocates `systemdict`, initializes the interpreter, creates dictionaries referenced by op definitions, sets up the dictionary stack, enters dictionaries and booleans/null into `systemdict`, and builds `ErrorNames`.
- `zop_init` runs initialization procedures embedded in op definition arrays and enters product/revision/copyright metadata.
- `op_init` inserts operator refs into dictionaries, skips internal `%` operators and duplicate special-index operators, allocates global/local op-array tables, and registers them as GC roots.

Research relevance:
- Startup hub that creates the PostScript dictionary/operator environment before init files run.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iinit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iinit.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iinit.h

Declares internal initialization stages exported by `iinit.c`.

Key points:
- Declares required initialization order: `obj_init`, `zop_init`, then `op_init`.
- Declares `gs_have_level2`.
- Notes `gs_have_level2` checks compiled operators, not runtime language level.

Research relevance:
- Compact contract for interpreter object/operator initialization ordering.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iinit.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ijs.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ijs.mak

Partial makefile for building the IJS client library within Ghostscript.

Key points:
- Requires callers to define `IJSSRCDIR`, `IJSEXECTYPE`, and `BINDIR`.
- Defines IJS source, generated, object, include, and compiler variables.
- Builds `ijslib.dev` from `ijs.o`, `ijs_server.o`, `ijs_client.o`, and `ijs_exec_$(IJSEXECTYPE).o`.
- Provides Unix and Windows exec rules for `ijs_exec_unix.c` and `ijs_exec_win.c`.
- Provides clean targets and example client/server targets.
- Comments flag known issues: clean target deletes too broadly, example linking is not portable/policy clean, and Windows exec cannot compile with `/Za` because it needs `windows.h`.

Research relevance:
- Build-system glue for Ghostscript’s IJS inkjet-server client support.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ijs.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ilevel.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ilevel.h

Defines interpreter language-level convenience macros.

Key points:
- `LANGUAGE_LEVEL` maps to `i_ctx_p->language_level`.
- `LL2_ENABLED` checks `LANGUAGE_LEVEL >= 2`.
- `LL3_ENABLED` checks `LANGUAGE_LEVEL >= 3`.
- `level2_enabled` aliases `LL2_ENABLED` for backward compatibility.

Research relevance:
- Simple but widespread runtime language-level control contract.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ilevel.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ilocate.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ilocate.c

Implements chunk lookup and debug validation for Ghostscript ref memory.

Key points:
- `gc_locate` locates a pointer in chunks across current memory, stable allocators, local/global counterpart spaces, save levels, and system space.
- Used primarily by string GC and debug validation.
- Debug-only validation includes `ialloc_validate_spaces`, `ialloc_validate_memory`, `ialloc_validate_chunk`, and `ialloc_validate_object`.
- Temporarily saves allocator state so current allocation chunks appear valid during validation.
- Validates freelist object types/sizes, object sizes/type descriptors, refs and packed refs, names and name strings, strings, arrays, packed arrays, dictionaries, and struct pointers enumerated by type descriptors.
- Optional `IGC_PTR_STABILITY_CHECK` detects references from more stable spaces to less stable spaces.
- Non-debug builds provide no-op validation functions.

Research relevance:
- GC support utility for locating referents and diagnosing heap/reference corruption.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ilocate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/imain.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/imain.c

Provides common top-level support for Ghostscript interpreter front ends.

Key points:
- `get_minst_from_memory` retrieves the interpreter instance through library context backpointers.
- `gs_main_alloc_instance` allocates and initializes `gs_main_instance`.
- `gs_main_init0` performs platform setup, resets debug flags, records base time, and allocates library path containers.
- `gs_main_init1` initializes interpreter allocator spaces, library level 1, save machinery, name table, object dictionaries, and plugins.
- `gs_main_init2` runs operator initialization, initializes IO devices, publishes `INITFILES`/`EMULATORS`/`LIBPATH`, runs init files or compiled init string, sets display callback, and initializes readline.
- `gs_main_interpret` wraps `gs_interpret` and handles `e_NeedStdin`, `e_NeedStdout`, and `e_NeedStderr` callouts.
- Provides search path helpers, file/string execution helpers, suspendable string input, operand stack C API, stack dumping, resource usage, and exit/abort helpers.
- `gs_main_finit` collects temp filenames, performs final reclaim, closes devices/files, finalizes readline/plugins/library state, restores allocations, and unlinks temp files.

Research relevance:
- Main lifecycle engine for embedding, running, and finalizing the Ghostscript interpreter.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/imain.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/imain.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/imain.h

Declares the front-end API to `imain.c`.

Key points:
- Defines opaque `gs_main_instance`.
- Declares `get_minst_from_memory`, `gs_main_alloc_instance`, `gs_main_init0`, `gs_main_init1`, `gs_main_init2`, library-path helpers, and library file open helper.
- Documents the three initialization stages and common command-line switch equivalents for C API clients.
- Declares execution APIs for files and strings, including suspendable string input.
- Documents return conventions: `0`, `e_Quit`, or `e_Fatal`, with exit code returned separately.
- Declares operand stack push/pop helpers, `gs_main_dump_stack`, and `gs_main_finit`.

Research relevance:
- Top-level API contract for embedding and driving the Ghostscript interpreter.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/imain.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/imainarg.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/imainarg.c

Implements command-line parsing and dispatch for Ghostscript.

Key points:
- `gs_main_init_with_args` initializes argument reading with `@` file expansion, calls `gs_main_init0`, reads `GS_LIB` and `GS_OPTIONS`, sets default library path, prescans help/version, processes switches and filenames, then finishes with `gs_main_init2`.
- `gs_main_run_start` runs `systemdict /start get exec`.
- `swproc` handles stdin modes, PostScript argv passing, debug/log flags, run-string buffer sizing, inline code, file execution, geometry/resolution, help/version, library paths, memory/name-table settings, search policy, quiet startup, `-d/-D`, `-s/-S`, undefine, and debug hooks.
- `-d` parses a PostScript token; executable names are restricted to `null`, `true`, or `false`.
- `-sstdout=...` supports stdout redirection to files or stderr.
- `argproc`, `run_buffered`, and `runarg` dispatch file/direct/buffered execution and escape file/argument strings into PostScript snippets.
- Error/finish behavior flushes output/display and dumps stacks for unexpected interpreter errors.
- Help output prints revision, usage, emulators, sorted devices, search paths, and documentation/bug-report text.

Research relevance:
- User-facing CLI translation layer from argv/env into interpreter state and PostScript execution.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/imainarg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/imainarg.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/imainarg.h

Declares argc/argv front-end helpers.

Key points:
- Defines opaque `gs_main_instance` if needed.
- Declares `gs_main_init_with_args` and `gs_main_run_start`.
- Notes `argv` should conceptually be `const char *[]`, but ANSI C conventions expose writable strings.

Research relevance:
- Small high-level API for command-line-compatible interpreter invocation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/imainarg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/imemory.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/imemory.h

Defines interpreter extensions to the Ghostscript allocator interface.

Key points:
- Includes `ivmspace.h` and `gsalloc.h`.
- Declares ref-array allocation, resize, and free APIs.
- Declares string-ref allocation and `gs_register_ref_root`.
- Defines `gs_dual_memory_t`, representing current allocator, system/global/local VM spaces, current space, GC reclaim hook, and store-check masks.
- Notes system VM is immune to even outermost save/restore.
- Notes global VM may equal local in Level 1 configs, but not necessarily in a Level 2 executable running Level 1 mode.
- Warns embedded `gs_dual_memory_t` pointers must not persist across GC.
- Provides structure descriptor macro for `gs_dual_memory_t`.

Research relevance:
- Defines the interpreter’s local/global/system VM abstraction over the base memory manager.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/imemory.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iminst.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iminst.h

Defines the concrete `gs_main_instance` and library search path structure.

Key points:
- Defines `gs_file_path` with container/list refs, environment path, final/default path, and user-specified count.
- Defines stdio buffer sizes for stdin/stdout/stderr callouts.
- Defines `gs_main_instance_s` fields for heap allocator, memory chunk size, name table size, run buffer size, init stage, user error mode, current-directory search policy, run-start flag, library path, base time, readline data, stdio buffers, error object, display callback, and current interpreter context.
- Defines default init values and external `gs_main_instance_init_values`.

Research relevance:
- Captures interpreter instance state and lifecycle configuration. Clients should still treat the type as opaque.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iminst.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iname.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iname.c

Implements Ghostscript interpreter name-table lookup, allocation, GC integration, and restore cleanup.

Key points:
- Defines public `name_max_string`.
- Uses generated/permutation data: `hash_permutation` and `nt_1char_names`.
- Defines structure descriptors for `name_sub_table`, `name_string_sub_table_t`, and `name_table`.
- `names_init` allocates the table, sets maximum subtable count, initializes one-character names as permanent foreign strings, and reconstructs the free list.
- `names_ref` hashes strings, fast-paths empty and one-character names, looks up existing names, enters new names depending on `enterflag`, and returns `e_undefined`, `e_limitcheck`, or `e_VMerror` as appropriate.
- Implements string/name conversions, cache/index helpers, and name iteration.
- GC support includes unmarking, marking by index, subtable lookup, string-subtable lookup, and trace finish.
- `names_trace_finish` removes unmarked names from hash chains, clears string data, rebuilds the free list, and may free empty subtables.
- `names_restore` marks only names older than a save and reuses trace-finish cleanup.
- GC descriptors enumerate and relocate subtable pointers and non-foreign name strings.

Research relevance:
- Core PostScript symbol table, tightly coupled to dictionaries, GC, and save/restore.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iname.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iname.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iname.h

Defines interpreter-facing name-table macros.

Key points:
- Includes `inames.h`.
- Provides convenience macros routed through `mem->gs_lib_ctx->gs_name_table`: `name_memory`, `name_ref`, `name_string_ref`, `name_enter_string`, `name_from_string`, `name_eq`, `name_invalidate_value_cache`, `name_index`, `name_index_ptr`, `name_index_ref`, `name_next_valid_index`, `name_mark_index`, and `name_ref_sub_table`.
- Notes these APIs refer to the interpreter’s distinguished name-table instance.

Research relevance:
- Main include-level access point for interpreter-wide PostScript name handling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iname.h -->