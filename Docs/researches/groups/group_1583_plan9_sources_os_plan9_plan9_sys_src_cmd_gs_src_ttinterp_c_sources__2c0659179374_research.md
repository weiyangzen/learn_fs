# Group Research: group_1583_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_ttinterp_c_sources__2c0659179374

Scope confirmed against `Docs/research_subset_a.md`: this group belongs to `sources/os/plan9/plan9`, one of the included subset A source trees. I read all eight listed source files completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttinterp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttinterp.c

## Role

`ttinterp.c` is the TrueType bytecode interpreter used by this Ghostscript-derived TrueType scaler in the Plan 9 tree. It is FreeType-derived code with Aladdin/Ghostscript modifications. It executes font, CVT/prep, and glyph instruction streams over a `TExecution_Context`.

## Main Responsibilities

- Implements the interpreter dispatch loop in `RunIns(PExecution_Context exc)`.
- Defines opcode stack effects in `Pop_Push_Count`.
- Implements TrueType stack, flow-control, arithmetic, graphics-state, storage, CVT, outline, delta, function-definition, and instruction-definition opcodes.
- Selects optimized projection/movement/rounding/CVT access callbacks based on the current graphics state and pixel metrics.
- Maintains interpreter state through `CUR`, which maps to the passed execution context unless `TT_STATIC_INTERPRETER` is enabled.
- Uses `setjmp`/`longjmp` via `exc->trap` for disabled patented algorithms and error escape.

## Important Implementation Details

- The interpreter supports both indirect/reentrant and static/non-reentrant builds through macros. The normal path uses `PExecution_Context exc`.
- Axis-aligned projection and movement are fast-pathed through `Project_x`, `Project_y`, `Direct_Move_X`, and `Direct_Move_Y`.
- Non-axis projection routines `Project`, `Dual_Project`, and `Free_Project` are disabled with `THROW_PATENTED`, causing `TT_Err_Invalid_Engine`. This is a major behavioral limitation relative to a full TrueType interpreter.
- `RunIns` sets CVT handlers to stretched or normal variants depending on whether `x_ppem != y_ppem`.
- The opcode dispatch table maps all 256 bytecodes to named handlers, with unimplemented or custom opcodes routed through `Ins_UNKNOWN` so `IDEF` redefinitions can still be honored.
- Function definitions (`FDEF`) and instruction definitions (`IDEF`) are stored as code-range/start records in the execution context and later persisted back to the instance.
- The interpreter handles glyph zones (`pts`, `twilight`, `zp0`, `zp1`, `zp2`) and touch flags directly.
- Several compatibility comments describe undocumented TrueType behavior, including twilight-zone handling, Microsoft font behavior, phantom-point allowance in delta instructions, and out-of-range CVT reads being stubbed for a Ghostscript bug workaround.
- Debug builds allocate snapshots of point arrays around each instruction and log coordinate changes through the font debug hooks.

## Cross-File Relationships

- Public entry point is declared in `ttinterp.h`.
- Operates on structures and function pointer types from `ttobjs.h`.
- Uses table and scalar types from `tttables.h`, `tttypes.h`, and math helpers from `ttcalc.h`.
- Called by `Instance_Init`, `Instance_Reset`, and `Context_Run` in `ttobjs.c`.
- CVT, font program, and prep program byte arrays are loaded by `ttload.c`.

## Notable Risks / Review Notes

- Full TrueType hinting is intentionally incomplete because non-axis projection algorithms throw `TT_Err_Invalid_Engine`.
- Interpreter safety depends on table maxima and allocation sizes prepared by `ttobjs.c` and `ttload.c`.
- Many opcodes manipulate indexes from untrusted font bytecode; there are bounds checks throughout, but compatibility exceptions exist.
- `Ins_ALIGNPTS` appears to compute the projected y delta using `CUR.zp1.cur_x[p1]` in the second coordinate expression, which looks suspicious and may be a historical bug or typo.
- The file is legacy C with macro-heavy execution context access, making local reasoning about stack top, code range, and zone state delicate.

<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttinterp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttinterp.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttinterp.h

## Role

`ttinterp.h` is the public header for the TrueType bytecode interpreter.

## Main Responsibilities

- Provides include guards and C++ linkage wrappers.
- Includes `ttcommon.h` and `ttobjs.h` so callers can reference `TT_Error` and `PExecution_Context`.
- Declares the interpreter entry point:
  - `TT_Error RunIns(PExecution_Context exc);`

## Cross-File Relationships

- Implemented by `ttinterp.c`.
- Used by `ttobjs.c`, where font, CVT, and glyph code ranges are selected and then executed.
- Depends on `TExecution_Context` from `ttobjs.h`.

## Notable Risks / Review Notes

- The header exposes only one function, so interpreter behavior is almost entirely governed by the mutable execution context contract.
- The comment says the TrueType instruction interpreter was cut out after FreeType, but this tree still contains a partial interpreter with patented projection paths disabled.

<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttinterp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttload.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttload.c

## Role

`ttload.c` loads the small subset of TrueType tables needed by this scaler’s interpreter and instance setup.

## Main Responsibilities

- `Load_TrueType_MaxProfile(PFace face)` reads the `maxp` table and fills `face->maxProfile`.
- `Load_TrueType_CVT(PFace face)` reads the raw control value table into `face->cvt`.
- `Load_TrueType_Programs(PFace face)` loads optional `fpgm` font program bytes and optional `prep` CVT program bytes.

## Important Implementation Details

- Table offsets and lengths come from `ttfFont` fields such as `t_maxp`, `t_cvt_`, `t_fpgm`, and `t_prep`.
- Data is read through `ttfReader` helper macros from `ttload.h`.
- Allocations use the Ghostscript `ttfMemory` allocator reachable through `font->tti->ttf_memory`.
- `maxp` values are also normalized into face-level maxima:
  - `numGlyphs`
  - `maxPoints`
  - `maxContours`
  - `maxComponents`
- The font program is optional. The prep program may be absent, in which case CVT program size is zero.
- CVT size is derived from table length divided by two, because entries are signed shorts.

## Cross-File Relationships

- Loaded face fields are consumed by `ttobjs.c` during `Face_Create`, `Context_Create`, `Instance_Create`, `Instance_Init`, and `Instance_Reset`.
- CVT data loaded here is copied/scaled into instance CVT arrays before prep or glyph programs execute.
- Uses type definitions from `ttobjs.h` and `tttables.h`.

## Notable Risks / Review Notes

- The implementation assumes directory entries have already been populated in `ttfFont`; this file does not validate table checksums or directory structure.
- Reads stop on reader EOF for CVT entries but do not otherwise enforce exact table completeness.
- Only `maxp`, `cvt`, `fpgm`, and `prep` are actively loaded in this file; many loader prototypes exist elsewhere or are unused by this reduced path.

<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttload.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttload.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttload.h

## Role

`ttload.h` declares TrueType table loader functions and defines stream/reader convenience macros for table parsing.

## Main Responsibilities

- Declares loader functions for many TrueType tables:
  - directory, maxp, gasp, header, hhea, loca, names, CVT, cmap, hmtx, programs, OS/2, post, hdmx, and arbitrary table data.
- Declares cleanup helpers for names and hdmx tables.
- Defines byte-order reader macros:
  - `GET_Byte`, `GET_UShort`, `GET_Short`, `GET_Long`, `GET_ULong`.
- Contains legacy FreeType stream/frame macros split by `TT_CONFIG_REENTRANT`.

## Important Implementation Details

- In this Plan 9/Ghostscript port, the active reader macros call `ttfReader__*` helpers on a local `r`.
- Reentrant and thread-safe macro sections preserve older FreeType loader conventions, though this group’s active implementation in `ttload.c` mostly uses the direct `ttfReader` path.
- The header exposes a broader loader API than the small subset implemented in this grouped `ttload.c`.

## Cross-File Relationships

- Included by `ttload.c` for parsing macros and prototypes.
- Included by `ttobjs.c`, where `Face_Create` uses `Load_TrueType_MaxProfile`, `Load_TrueType_CVT`, and `Load_TrueType_Programs`.
- Depends on `ttcommon.h` and forward-declared face types.

## Notable Risks / Review Notes

- The prototype surface is wider than the implementations present in this group, so some functions are expected to be in other files or omitted by this port.
- Macro-based parsing relies on a correctly named local reader variable `r`, which is fragile but consistent with the local code.

<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttload.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttmisc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttmisc.h

## Role

`ttmisc.h` is a small compilation-context bridge for FreeType-derived modules inside Ghostscript/Plan 9.

## Main Responsibilities

- Includes Ghostscript/platform headers:
  - `gx.h`
  - `string_.h`
  - `math_.h`
  - `std.h`
- Includes `tttypes.h`.
- Maps `MulDiv` to `ttMulDiv`.

## Cross-File Relationships

- Included at the top of `ttinterp.c`, `ttload.c`, and `ttobjs.c`.
- Provides the surrounding Ghostscript compatibility environment expected by the imported FreeType code.

## Notable Risks / Review Notes

- This header is intentionally thin, but it is a central portability shim. Changes here can affect all FreeType-derived modules that include it.
- The `MulDiv` alias can hide which arithmetic implementation is in use unless `tttypes.h`/`ttcalc.h` are also inspected.

<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttmisc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttobjs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttobjs.c

## Role

`ttobjs.c` manages TrueType face, instance, and execution-context lifecycle for this scaler. It is the glue between loaded font tables, scaled instance metrics, and bytecode execution.

## Main Responsibilities

- Manages code ranges:
  - `Goto_CodeRange`
  - `Unset_CodeRange`
  - `Get_CodeRange`
  - `Set_CodeRange`
  - `Clear_CodeRange`
- Creates, grows, loads, saves, and destroys execution contexts.
- Creates, initializes, resets, and destroys font instances.
- Creates and destroys face-level data.
- Provides scaling helpers `Scale_X` and `Scale_Y`.
- Defines `Default_GraphicsState`.

## Important Implementation Details

- `Context_Create` is an adjust/grow operation rather than a pure constructor. It allocates or expands shared buffers for stacks, glyph point zones, twilight zone, and contours.
- Execution contexts are reference-counted with `lock`; `Context_Destroy` frees buffers only when the lock count drops to zero.
- `Context_Load` copies instance state into the execution context before running bytecode. `Context_Save` persists definitions, code ranges, CVT/storage pointers, and IDEF mapping back to the instance.
- `Context_Run` prepares glyph code execution by selecting `TT_CodeRange_Glyph`, resetting zone pointers, graphics-state vectors, stack top, and call stack, then calling `RunIns`.
- `Instance_Create` allocates function definitions, instruction definitions, scaled CVT storage, and TrueType storage. It enforces a maximum of 255 instruction definitions and raises the FDEF table to at least 50 entries for a Ghostscript bug workaround.
- `Instance_Init` executes the font program (`fpgm`) with neutral metrics and disabled CVT/glyph code ranges.
- `Instance_Reset` recomputes scaling for a ppem/transform, scales face CVT values into the instance CVT, clears storage and twilight points, and executes the prep/CVT program.
- `Face_Create` currently loads only max profile, CVT, and programs; other TrueType table loads are commented out.
- Memory management uses the `ttfMemory` allocator through local `FREE` and `ALLOC_ARRAY` macros.

## Cross-File Relationships

- Calls `RunIns` from `ttinterp.c`.
- Uses loader functions from `ttload.c`.
- Implements declarations from `ttobjs.h`.
- Uses table structures from `tttables.h`, especially `TMaxProfile`.
- Relies on `ttfMemory`, `ttfFont`, and `ttfReader` types from surrounding Ghostscript TrueType code.

## Notable Risks / Review Notes

- Shared-context reuse makes ownership subtle. Failed allocation intentionally does not destroy existing shared buffers.
- `Context_Destroy` returns `TT_Err_Out_Of_Memory` if `current_face` is missing, even during cleanup. The comment explains this as a high-level device close edge case.
- `Face_Create` omits many standard TrueType tables, implying this component is a specialized hinting/program subset rather than a full standalone TrueType loader.
- Instance validity depends on successful prep execution; invalid ppem values return `TT_Err_Invalid_PPem`.

<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttobjs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttobjs.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttobjs.h

## Role

`ttobjs.h` defines the main object model and execution context contract for the FreeType-derived TrueType engine.

## Main Responsibilities

- Declares face, instance, execution context, and glyph pointer types.
- Defines `TGraphicsState`, `TCodeRange`, `TDefRecord`, `TCallRecord`, `TGlyph_Zone`, `TTransform`, `TSubglyph_Record`, and `TIns_Metrics`.
- Defines the three active TrueType code ranges:
  - font program
  - CVT/prep program
  - glyph instructions
- Defines interpreter callback function types for rounding, movement, projection, and CVT access.
- Defines `TExecution_Context`, the large mutable state object used by `RunIns`.
- Declares lifecycle, code-range, instance, face, and scaling functions implemented in `ttobjs.c`.

## Important Implementation Details

- `TGraphicsState` mirrors TrueType interpreter state: reference points, vectors, loop count, rounding, cut-ins, delta parameters, scan control, and zone pointer selectors.
- `TGlyph_Zone` stores original/current x/y coordinates, touch flags, contour endpoints, and point/contour counts.
- `TIns_Metrics` stores point size, resolution, ppem, scaling factors, non-square-pixel ratios, compensation values, and transform flags.
- `TExecution_Context` contains instruction stream state, function/instruction definitions, code ranges, storage, stack, rounding state, zones, graphics state, CVT, callback function pointers, `jmp_buf trap`, allocation capacities, and lock count.
- `EXEC_OPS`, `EXEC_OP`, `EXEC_ARGS`, and `EXEC_ARG` macros abstract indirect versus static interpreter builds.

## Cross-File Relationships

- Included by `ttinterp.h`, `ttinterp.c`, `ttobjs.c`, and `ttload.c`.
- Includes `tttables.h`, so face objects can embed `TMaxProfile`.
- The structs defined here are filled by `ttload.c`, managed by `ttobjs.c`, and mutated heavily by `ttinterp.c`.

## Notable Risks / Review Notes

- This header is the central ABI between loader, interpreter, and object manager. Field layout and macro changes would have broad effects.
- The execution context contains both borrowed pointers and owned buffers, so ownership is not obvious from the structure alone.
- The static/indirect interpreter macros make function signatures conditional at compile time.

<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttobjs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/tttables.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/tttables.h

## Role

`tttables.h` defines C structures for selected TrueType/OpenType table records used by the FreeType-derived scaler.

## Main Responsibilities

- Defines TrueType Collection header representation.
- Defines table directory and table directory entry structures.
- Defines cmap directory and cmap directory entry structures.
- Defines `TMaxProfile` for the `maxp` table.
- Defines `gasp` table flags and range structures.
- Defines horizontal metric records.
- Defines `loca` and `name` table structures.

## Important Implementation Details

- `TMaxProfile` is the most important structure for this group. `ttload.c` reads it, and `ttobjs.c` uses its maximum values to allocate interpreter stack, point zones, twilight zone, storage, FDEF/IDEF arrays, and instruction capacity.
- Some table types are declared here even though this grouped implementation does not load them directly.
- The header intentionally leaves `head`, `hhea`, `OS/2`, and `post` table definitions to other headers.

## Cross-File Relationships

- Included by `ttobjs.h`.
- `ttload.c` fills `TMaxProfile` through `Load_TrueType_MaxProfile`.
- `ttobjs.c` consumes max profile values during face, instance, and context setup.

## Notable Risks / Review Notes

- These are raw table-shape definitions. Validation and endian conversion happen in loader code, not here.
- The declared table surface is broader than the subset used by `Face_Create` in `ttobjs.c`.

<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/tttables.h -->