# Group Research: group_145_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_ttinterp_c_sources_6c27f88aca14

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/9front`. I read all 8 listed files completely.

This group covers Ghostscript’s FreeType-derived TrueType instruction runtime: bytecode interpretation, code-range/context management, face/instance allocation, CVT/program loading, and supporting TrueType table/object declarations.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ttinterp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ttinterp.c

FreeType-derived TrueType bytecode interpreter adapted for Ghostscript.

Key points:
- Implements `RunIns(PExecution_Context exc)`, the main TrueType instruction execution loop.
- Supports both static and indirect interpreter builds through `TT_STATIC_INTERPRETER`, with the indirect/re-entrant mode as the normal path.
- Uses `Pop_Push_Count[512]` to preflight stack pops/pushes for each opcode before dispatch.
- Computes variable instruction lengths for `NPUSHB`, `NPUSHW`, `PUSHB[]`, and `PUSHW[]`, and validates instruction-pointer bounds.
- Maintains code ranges for font program, CVT/prep program, and glyph instruction program.
- Provides stack, flow-control, logical, arithmetic, storage, CVT, graphics-state, outline, delta, and miscellaneous instruction handlers.
- Implements function definitions and calls:
  - `FDEF`, `ENDF`
  - `CALL`, `LOOPCALL`
  - `IDEF` and redirected unknown-opcode execution through `IDefPtr`.
- Implements vector setup and graphics-state changes:
  - projection/freedom/dual vectors
  - zone pointers
  - reference points
  - rounding mode
  - scan/instruction control
  - delta base and shift
- Implements point movement and interpolation instructions over normal and twilight zones:
  - `MDAP`, `MIAP`, `MDRP`, `MIRP`
  - `SHP`, `SHC`, `SHZ`, `SHPIX`
  - `IUP`, `IP`, `ALIGNRP`, `ALIGNPTS`, `ISECT`
  - point on/off-curve flag flipping
- Handles CVT access with separate square-pixel and stretched non-square-pixel routines.
- Uses `setjmp`/`longjmp` through `exc->trap` for hard interpreter exits.
- Ghostscript’s copy disables patent-sensitive projection implementations with `THROW_PATENTED`; generic `Project`, `Dual_Project`, and `Free_Project` throw `TT_Err_Invalid_Engine`, while axis-aligned `Project_x`/`Project_y` remain usable.
- Contains compatibility/workaround comments for real fonts and bugs, including out-of-range CVT read tolerance, extra stack space assumptions, phantom-point delta allowance, and twilight-zone behavior.
- Debug builds can print instruction traces, repaint, and compare point coordinate arrays before/after each instruction.

Dependencies and interactions:
- Includes `ttmisc.h`, `ttfoutl.h`, `tttypes.h`, `ttcalc.h`, `ttinterp.h`, and `ttfinp.h`.
- Uses execution context, graphics state, glyph zones, CVT/storage arrays, function records, and call records defined in `ttobjs.h`.
- Uses fixed-point and 64-bit helper macros from `ttcalc.h`.
- Called by `Instance_Init`, `Instance_Reset`, and `Context_Run` in `ttobjs.c`.
- Reads face/font debug callbacks through `current_face->font`.

Research relevance:
- This is the central TrueType hinting bytecode engine in this Ghostscript source tree. Its error paths, stack bounds, code-range transitions, CVT behavior, and patented-algorithm disablement determine how embedded TrueType instructions affect glyph loading and rendering.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ttinterp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ttinterp.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ttinterp.h

Public header for the TrueType bytecode interpreter.

Key points:
- Carries the same FreeType/Ghostscript provenance comments as `ttinterp.c`.
- Includes `ttcommon.h` and `ttobjs.h`.
- Declares the single interpreter entry point:
  - `TT_Error RunIns(PExecution_Context exc)`
- Wraps declarations in `extern "C"` for C++ consumers.
- Has standard include guards.

Dependencies and interactions:
- `PExecution_Context` comes from `ttobjs.h`.
- Used by `ttobjs.c` to run font, CVT, and glyph programs.

Research relevance:
- This is the narrow public contract for the interpreter: clients provide a prepared execution context and receive a TrueType error code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ttinterp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ttload.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ttload.c

Loader implementation for the subset of TrueType tables needed by this Ghostscript TrueType instruction runtime.

Key points:
- Implements `Load_TrueType_MaxProfile`.
  - Seeks to `maxp`.
  - Reads version, glyph count, point/contour maxima, twilight/storage/function/instruction/stack/instruction-size maxima, component maxima.
  - Derives `face->numGlyphs`, `face->maxPoints`, `face->maxContours`, and `face->maxComponents`.
- Implements `Load_TrueType_CVT`.
  - Seeks to `cvt `.
  - Computes `face->cvtSize` from table length / 2.
  - Allocates `face->cvt`.
  - Reads signed short CVT values until the table ends or reader EOF.
- Implements `Load_TrueType_Programs`.
  - Loads optional `fpgm` font program into `face->fontProgram`.
  - Loads optional `prep` CVT program into `face->cvtProgram`.
  - Allocates program byte buffers from Ghostscript’s `ttfMemory`.
- Uses debug trace macros tied to the font’s `DebugPrint` callback.

Dependencies and interactions:
- Includes `ttmisc.h`, `ttfoutl.h`, `tttypes.h`, `ttcalc.h`, `ttobjs.h`, `ttload.h`, and `ttfinp.h`.
- Uses `ttfReader` callbacks for `Seek`, `Read`, and `Eof`.
- Uses table metadata fields from `ttfFont` such as `t_maxp`, `t_cvt_`, `t_fpgm`, and `t_prep`.
- Called from `Face_Create` in `ttobjs.c`.

Research relevance:
- Supplies the interpreter with maximum allocation limits, the unscaled CVT, and executable TrueType programs. It is intentionally narrower than a full font loader.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ttload.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ttload.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ttload.h

Public declarations and stream-access macros for TrueType table loading.

Key points:
- Declares many FreeType-style table loader entry points:
  - directory, maxp, gasp, head, hhea, loca, name, CVT, cmap, hmtx, programs, OS/2, post, hdmx, arbitrary table reads
  - name and hdmx cleanup helpers
- In this group, only maxp/CVT/program loading is implemented in `ttload.c`; other declarations are part of the broader FreeType-derived interface.
- Defines reader macros used by loaders:
  - `GET_Byte`
  - `GET_UShort`
  - `GET_Short`
  - `GET_Long`
  - `GET_ULong`
- Provides legacy stream/frame helper macros for `TT_CONFIG_REENTRANT` and non-reentrant/thread-safe builds.
- Exposes file-position, seek, skip, read, read-at, frame access, and frame-forget macros in the old FreeType style.

Dependencies and interactions:
- Includes `ttcommon.h`.
- Depends on FreeType-style stream APIs such as `TT_Use_Stream`, `TT_Access_Frame`, `TT_File_Pos`, `TT_Seek_File`, and related functions where those legacy paths are compiled.
- The current `ttload.c` uses the newer Ghostscript `ttfReader` macros at the top of this header.

Research relevance:
- This is the loader-facing API and portability shim connecting FreeType table-loader idioms to Ghostscript’s font reader abstraction.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ttload.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ttmisc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ttmisc.h

Common compilation-context header for FreeType-derived TrueType modules.

Key points:
- Includes Ghostscript portability and math headers:
  - `gx.h`
  - `string_.h`
  - `math_.h`
  - `std.h`
- Includes `tttypes.h`.
- Maps `MulDiv` to `ttMulDiv`.

Dependencies and interactions:
- Included first by `ttinterp.c`, `ttload.c`, and `ttobjs.c`.
- Bridges Ghostscript’s core portability layer with the imported TrueType code.

Research relevance:
- Small but important adapter header that normalizes the build environment for this FreeType-derived TrueType subsystem.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ttmisc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ttobjs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ttobjs.c

Object and execution-context manager for the Ghostscript TrueType interpreter subsystem.

Key points:
- Implements code-range management:
  - `Goto_CodeRange`
  - `Unset_CodeRange`
  - `Get_CodeRange`
  - `Set_CodeRange`
  - `Clear_CodeRange`
- Implements execution-context lifecycle:
  - `Context_Create` allocates/resizes call stack, operand stack, glyph point zone, twilight zone, and contour arrays.
  - `Context_Destroy` frees those arrays when the context lock reaches zero.
  - `Context_Load` copies instance state into the execution context.
  - `Context_Save` copies code-range/IDEF state back into the instance and clears context pointers to avoid stale references.
  - `Context_Run` prepares a glyph code range, resets glyph execution state, and calls `RunIns`.
- Implements default graphics state as `Default_GraphicsState`.
- Implements instance lifecycle:
  - `Instance_Create` allocates function definitions, instruction definitions, scaled CVT, and storage arrays.
  - `Instance_Destroy` frees instance-owned interpreter data.
  - `Instance_Init` runs the font program (`fpgm`) once against a fresh instance.
  - `Instance_Reset` computes ppem/scaling/ratio state, scales the CVT, resets storage and twilight points, and runs the prep/CVT program.
- Implements face lifecycle:
  - `Face_Create` loads only maxp, CVT, and programs in this adapted build.
  - `Face_Destroy` frees CVT and program buffers.
- Provides `Scale_X` and `Scale_Y` helpers for FUnit-to-26.6 scaling.
- Uses allocation macros that reuse existing arrays when already large enough and grow them only as needed.
- Adds several Ghostscript-specific robustness changes:
  - shared context reuse and locking
  - avoiding full context buffer release on failed resize
  - extra stack headroom
  - minimum 50 FDEF slots for a known font bug
  - failure handling for low-memory cleanup paths.

Dependencies and interactions:
- Includes `ttmisc.h`, `ttfoutl.h`, `ttobjs.h`, `ttcalc.h`, `ttload.h`, and `ttinterp.h`.
- Uses `ttfMemory` for all allocation/free operations.
- Calls `Load_TrueType_MaxProfile`, `Load_TrueType_CVT`, and `Load_TrueType_Programs`.
- Calls `RunIns` to execute font, prep, and glyph programs.
- Reads font table metadata through the `PFace`/`ttfFont` structures.

Research relevance:
- This file owns the interpreter runtime state model: how face-global data, size-specific instance data, and transient glyph execution data move between structures before and after bytecode execution.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ttobjs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ttobjs.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ttobjs.h

Core object, graphics-state, code-range, glyph-zone, metrics, face, instance, and execution-context definitions for the TrueType subsystem.

Key points:
- Documents FreeType’s four object categories:
  - face
  - instance
  - execution context
  - glyph
- Declares opaque/forward types for `TFace`, `TInstance`, `TExecution_Context`, and `TGlyph`.
- Defines `TGraphicsState` with reference points, projection/dual/freedom vectors, loop, minimum distance, round state, auto-flip, cut-ins, delta parameters, instruction/scan controls, scan type, and zone pointer selectors.
- Defines three active code ranges:
  - `TT_CodeRange_Font`
  - `TT_CodeRange_Cvt`
  - `TT_CodeRange_Glyph`
- Defines `TCodeRange`, `TDefRecord`, and `TCallRecord` for bytecode execution.
- Defines `TGlyph_Zone` with original/current x/y coordinate arrays, touch flags, contour endpoints, and counts.
- Defines execution macro families for indirect and static interpreter modes:
  - `EXEC_OPS`
  - `EXEC_OP`
  - `EXEC_ARGS`
  - `EXEC_ARG`
- Defines interpreter callback function pointer types:
  - rounding
  - moving
  - projection
  - CVT read/write/move
- Defines composite glyph support structures:
  - `TTransform`
  - `TSubglyph_Record`
- Contains an extended note explaining non-square-pixel CVT scaling and ratio computation.
- Defines `TIns_Metrics` for point size, resolutions, ppem, scaling ratios, compensation values, rotation, and stretching.
- Defines `TFace` with reader/font pointers, maxp data, program buffers, CVT, and derived maxima.
- Defines `TInstance` with face pointer, validity flag, metrics, FDEF/IDEF arrays, IDEF opcode map, code ranges, graphics state, scaled CVT, and storage.
- Defines `TExecution_Context` with current instruction state, code range, stacks, function/instruction definitions, glyph zones, graphics state, metrics, CVT/storage pointers, function pointers, `jmp_buf trap`, allocation maxima, and lock.
- Declares lifecycle and helper functions implemented in `ttobjs.c`.

Dependencies and interactions:
- Includes `ttcommon.h`, `tttypes.h`, `tttables.h`, and `<setjmp.h>`.
- Supplies the structures consumed heavily by `ttinterp.c`, `ttobjs.c`, and `ttload.c`.

Research relevance:
- This is the structural contract for the entire TrueType interpreter runtime. Most behavior in `ttinterp.c` is direct mutation of fields declared here.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ttobjs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/tttables.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/tttables.h

TrueType table structure declarations used by the FreeType-derived loader/object code.

Key points:
- Defines TrueType Collection header `TTTCHeader`.
- Defines table directory header `TTableDir`.
- Defines table directory entry `TTableDirEntry`.
- Defines cmap directory and entry structures:
  - `TCMapDir`
  - `TCMapDirEntry`
- Defines maximum profile table `TMaxProfile`, including glyph counts and maxima for points, contours, components, zones, twilight points, storage, function defs, instruction defs, stack elements, instruction size, and component depth.
- Defines gasp flags:
  - `GASP_GRIDFIT`
  - `GASP_DOGRAY`
- Defines gasp range/table structures:
  - `GaspRange`
  - `TGasp`
- Notes that head, hhea, OS/2, and post tables are defined elsewhere.
- Defines horizontal metrics structure `TLongHorMetric`.
- Defines loca table structure `TLoca`.
- Defines name record and name table structures:
  - `TNameRec`
  - `TName_Table`
- Wraps declarations for C++.

Dependencies and interactions:
- Includes `tttypes.h`.
- `TMaxProfile` is used directly by `ttload.c`, `ttobjs.c`, and `ttobjs.h`.
- Several declared table types support broader loader APIs declared in `ttload.h`, even though this group’s implementation only loads a subset.

Research relevance:
- Provides the on-disk table metadata shapes that drive allocation limits and table parsing for the TrueType interpreter support code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/tttables.h -->