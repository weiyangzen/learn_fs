# Group Research: group_1586_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_zcontrol_c_sources__07b77ddcc521

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/plan9`, which is included in subset A. I read each listed source file completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcontrol.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcontrol.c

Implements core Ghostscript/PostScript control operators around the operand stack and execution stack.

Key operators include `.cond`, `exec`, `.execn`, `superexec`, `.runandhide`, `if`, `ifelse`, `for`, `%for_samples`, `repeat`, `loop`, `exit`, `stop`, `.stop`, `stopped`, `.stopped`, `.instopped`, `countexecstack`, `execstack`, `.needinput`, `.quit`, and `currentfile`.

The implementation is continuation-heavy: `cond`, loops, `stopped`, `execstack`, `runandhide`, and sample iteration push continuation operators or marks onto the execution stack. Loop and stopped scopes are represented by estack marks such as `es_for` and `es_stopped`.

Important internal routines:
- `pop_estack()` unwinds execution stack entries and invokes cleanup procedures on marks.
- `count_to_stopped()` locates a matching stopped mark by signal mask.
- `count_exec_stack()` optionally hides executable null mark entries.
- `unmatched_exit()` converts unmatched `exit`/`stop` into an interpreter quit with `e_invalidexit`.

Security and correctness notes: `zexecn()` validates executable access before pushing objects to the execution stack; `do_execstack()` sanitizes internal operators and stack-associated structs before exposing stack contents; `.runandhide` temporarily removes an array from the operand stack and restores attributes on normal or error paths.

Registered operator tables are split into `zcontrol1_op_defs`, `zcontrol2_op_defs`, and `zcontrol3_op_defs` because of the operator table size limit.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcontrol.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcrd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcrd.c

Implements Level 2 CIE Color Rendering Dictionary support.

Primary operators expose current CRD state, build ColorRenderingType 1 CRDs, build device CRDs, and install CRDs into the graphics state: `currentcolorrendering`, `.buildcolorrendering1`, `.builddevicecolorrendering1`, `.setcolorrendering1`, and `.setdevicecolorrendering1`.

`zcrd1_params()` extracts dictionary parameters such as `MatrixLMN`, `RangeLMN`, `MatrixABC`, `RangeABC`, white/black points, `MatrixPQR`, `RangePQR`, and optional `RenderTable`. `zcrd1_proc_params()` extracts executable procedures including `EncodeLMN`, `EncodeABC`, `TransformPQR`, and render-table transform procedures.

The file schedules cache construction on the execution stack. `cache_colorrendering1()` prepares sampled caches for encoding functions and render-table transforms, while `cie_cache_render_finish()` converts caches and completes the CRD.

`cie_cache_joint()` builds joint TransformPQR caches between the active CIE color space and CRD. It constructs temporary executable arrays that shuffle operands through `cie_exec_tpqr()` and cleanup through `cie_tpqr_finish()`.

Includes optimized C implementations of default white/black scaling procedures: `.TransformPQR_scale_WB0`, `.TransformPQR_scale_WB1`, and `.TransformPQR_scale_WB2`.

Notable risk areas: several comments flag reference-count fixes; cache building depends on correct estack unwinding; driver-provided CRDs use null procedure refs and bypass PostScript procedure sampling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcrd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcsdevn.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcsdevn.c

Implements DeviceN color space setup for LanguageLevel 3.

The sole operator, `.setdevicenspace`, expects a four-element color-space array. The current color space is treated as the alternate space for the new DeviceN space.

The operator validates the component-name array, enforces a nonzero component count and `GS_CLIENT_COLOR_MAX_COMPONENTS`, converts string names to PostScript names when needed, and stores component name indexes into `cs.params.device_n.names`.

It validates the tint transform procedure, resolves it with `ref_function()`, installs it with `gs_cspace_set_devn_function()`, and records interpreter-side references for layer names and tint transform in `istate->colorspace.procs.special.device_n`.

Memory handling explicitly frees `names` and `pmap` on error paths and decrements the map reference after successful `gs_setcolorspace()` because the build path starts it with refcount 1.

Registered through `zcsdevn_op_defs` with `op_def_begin_ll3()`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcsdevn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcsindex.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcsindex.c

Implements Indexed color space support.

`.setindexedspace` consumes a four-element color-space array and uses the current color space as the base space. It validates `hival`, rejects non-base-capable current spaces, and constructs a `gs_color_space_type_Indexed` color space.

Two lookup forms are supported:
- String lookup table: validates length, tolerates extra trailing bytes for compatibility, stores table pointer directly, and disables procedure lookup.
- Procedure lookup: validates executable procedure and calls `zcs_begin_map()` to allocate an indexed map and schedule cache population.

`indexed_map1()` is the continuation that repeatedly pushes the current index, runs the lookup procedure, collects returned component values, and writes them into `gs_indexed_map`.

The code uses `memmove()` for color-space parameter copying to avoid compiler aliasing issues noted in comments.

`zcs_begin_map()` is shared by indexed/tint map users. It allocates the map, initializes estack bookkeeping fields, and schedules the first continuation.

Main risk area: procedure-based maps are asynchronous and leave partially built data on the execution stack until all entries are sampled.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcsindex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcspixel.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcspixel.c

Implements DevicePixel color space setup.

`.setdevicepixelspace` expects a two-element array, reads element 1 as an integer depth, initializes a DevicePixel color space through `gs_cspace_init_DevicePixel()`, and installs it with `gs_setcolorspace()`.

This is a small adapter from PostScript array operands to the graphics library DevicePixel color-space constructor. On success it pops the operand array; otherwise it propagates the graphics-library error.

Registered in `zcspixel_op_defs`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcspixel.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcssepr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcssepr.c

Implements Separation color space support plus overprint state operators.

`.setseparationspace` expects a four-element color-space array and uses the current color space as the alternate space. It accepts separation names as strings or names, resolves special names `/All` and `/None`, validates the tint transform, builds a Separation color space, installs the tint function, and records interpreter references for layer name and tint transform.

The file notes that Separation is treated similarly to a single-component DeviceN color space except for `/All` and `/None`.

Overprint operators:
- `currentoverprint`
- `setoverprint`
- `.currentoverprintmode`
- `.setoverprintmode`

Memory handling frees the separation map on errors and decrements the map reference after successful installation.

Registered as Level 2 operators in `zcssepr_l2_op_defs`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcssepr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdevcal.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdevcal.c

Defines the `%Calendar%` IODevice.

`gs_iodev_calendar` is a special IODevice whose only meaningful implementation is `calendar_get_params()`. Most file/device operations are wired to `iodev_no_*` stubs.

`calendar_get_params()` calls `time()` and `localtime()`, converts `tm_year` to calendar year and `tm_mon` to 1-based month, writes fields `Year`, `Month`, `Day`, `Weekday`, `Hour`, `Minute`, and `Second`, then writes a boolean `Running`.

If time acquisition fails, all time fields are zeroed and `Running` is false.

This file has no operator table; it exports an IODevice descriptor.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdevcal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdevice.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdevice.c

Implements core device-related PostScript operators.

Major operators include `.copydevice2`, `currentdevice`, `.devicename`, `.doneshowpage`, `flushpage`, `.getbitsrect`, `.getdevice`, `.getdeviceparams`, `.gethardwareparams`, `makewordimagedevice`, `nulldevice`, `.outputpage`, `.putdeviceparams`, and `.setdevice`.

`zgetbitsrect()` is the main raster extraction bridge. It validates device, rectangle, alpha placement, optional standard component depth, target string size, and calls the device `get_bits_rectangle` procedure.

`zget_device_params()` writes device or hardware parameters onto the operand stack using `stack_param_list_write()` and inserts a mark before returned key/value pairs.

`zputdeviceparams()` reads key/value parameter pairs from the operand stack, applies them to a device, reports per-key failures, detects size/open-state changes, may reinstall the current device, and clears the current page device.

`zsetdevice()` respects `LockSafetyParams`, preventing switching to a different device when safety parameters are locked. `nulldevice`, `.setdevice`, and `.putdeviceparams` clear `istate->pagedevice`.

Registered in `zdevice_op_defs`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdevice.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdevice2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdevice2.c

Implements Level 2 page-device operators and wrappers around graphics-state save/restore operations.

Page-device query/setup operators:
- `.currentshowpagecount`
- `.currentpagedevice`
- `.setpagedevice`
- `.callinstall`
- `.callbeginpage`
- `.callendpage`

It replaces earlier implementations of `copy`, `gsave`, `save`, `gstate`, `currentgstate`, `grestore`, `grestoreall`, `restore`, and `setgstate` when page-device behavior requires PostScript callouts.

`save_page_device()` detects when a page-device dictionary must be created before saving graphics state. `restore_page_device()` detects when restore-like operations need to reapply page-device state and temporarily unlocks safety params when dictionaries differ.

`push_callout()` pushes executable names such as `%gsavepagedevice`, `%restorepagedevice`, and `%setgstatepagedevice` onto the execution stack.

The file exports `z2copy()` for FunctionType 4 handling and delegates gstate copying to `z2copy_gstate()` when ordinary `copy` fails on a gstate object.

Registered as Level 2 replacements in `zdevice2_l2_op_defs`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdevice2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdfilter.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdfilter.c

Implements a small PostScript interface for device filter stack management.

The sole operator, `.popdevicefilter`, calls `gs_pop_device_filter()` using stable memory and the current graphics state.

The includes are largely copied from `zdevice.c`, but the only functional dependency beyond interpreter/device basics is `gsdfilt.h`.

Registered in `zdfilter_op_defs`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdfilter.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdict.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdict.c

Implements core PostScript dictionary operators.

Core operators include `dict`, `maxlength`, `begin`, `end`, `def`, `load`, `.undef`, `known`, `where`, `currentdict`, `countdictstack`, `dictstack`, and `cleardictstack`.

`zop_def()` is a performance-sensitive helper used by `def`. It fast-paths top-dictionary name redefinition with single-probe lookup, combines writable dictionary and store checks, and falls back to `idict_put()` when necessary.

`zload()` fast-paths name lookup through the dictionary stack, while non-name keys are searched explicitly with read checks on each dictionary.

`zcopy_dict()` implements dictionary copy behavior, including Level 1 access-attribute compatibility and dictionary auto-expand behavior.

Extensions include `.dictcopynew`, `.dicttomark`, `.forceundef`, `.knownget`, `.knownundef`, and `.setmaxlength`.

Operator definitions are split into `zdict1_op_defs` and `zdict2_op_defs`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdict.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdosio.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdosio.c

Implements MS-DOS direct I/O and raw memory operators.

Operators:
- `.inport`
- `.inportb`
- `.outport`
- `.outportb`
- `.peek`
- `.poke`

The file explicitly warns it should never be included in a released configuration.

The port operators call DOS `inport`, `inportb`, `outport`, and `outportb`. The memory operators cast integer operands to byte pointers for raw reads/writes.

Risk is intentionally high: these operators expose direct hardware port and memory access to PostScript code.

Registered in `zdosio_op_defs`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdosio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdouble.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdouble.c

Implements double-precision floating point operators using 8-byte strings as double containers.

Arithmetic operators include `.dadd`, `.ddiv`, `.dmul`, and `.dsub`. Simple functions include `.dabs`, `.dceiling`, `.dfloor`, `.dneg`, `.dround`, `.dsqrt`, and `.dtruncate`. Transcendentals include `.darccos`, `.darcsin`, `.datan`, `.dcos`, `.dexp`, `.dln`, `.dlog`, and `.dsin`.

Comparison operators include `.deq`, `.dge`, `.dgt`, `.dle`, `.dlt`, and `.dne`.

Conversion operators include `.cvd`, `.cvsd`, `.dcvi`, `.dcvr`, and `.dcvs`.

`double_params()` accepts real, integer, or readable 8-byte string operands. `double_params_result()` validates writable 8-byte result strings. `double_result()` writes the result into the supplied string and collapses stack operands.

Notable behavior: `.cvsd` does strict string syntax filtering before `sscanf`; `.dcvs` first prints with `%g` and retries with `%.16g` if needed for accuracy.

Operator definitions are split into `zdouble1_op_defs` and `zdouble2_op_defs`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdouble.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdpnext.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdpnext.c

Implements NeXT Display PostScript extensions.

Alpha operators: `currentalpha` and `setalpha`.

Imaging/compositing operators:
- `.alphaimage`
- `composite`
- `compositerect`
- `dissolve`

`begin_composite()` creates a `gs_composite_alpha` object and asks the current device to create a compositor device. `end_composite()` closes/frees the temporary compositor and restores the original device.

`composite_image()` builds a `gs_image2_t` source image from either current state or a supplied gstate, adjusts CTM around destination placement, and sends it to `process_non_source_image()`.

Image sizing helpers:
- `.sizeimagebox` transforms and clips a source rectangle to current device bounds.
- `.sizeimageparams` reports bits/sample, multiproc false, and number of color components.

`device_is_true_color()` tests whether gray/RGB/CMYK devices map component values directly into decomposed packed pixels.

Registered in `zdpnext_op_defs`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdpnext.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdps.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdps.c

Implements Display PostScript extensions.

Graphics-state screen phase operators:
- `.setscreenphase`
- `.currentscreenphase`

`.image2` implements device-source image drawing from a dictionary. It reads `ImageMatrix`, `DataSource`, `XOrigin`, `YOrigin`, `Width`, `Height`, `PixelCopy`, and optional `UnpaintedPath`. If `UnpaintedPath` is requested, it allocates a path, processes the image, converts the resulting path to a user path, and writes it back into the dictionary.

View clipping operators:
- `viewclip`
- `eoviewclip`
- `initviewclip`
- `viewclippath`

`defineusername` maintains the global user-name array used by binary token support. It expands the array in stable local VM, preserves entries across save/restore, and rejects conflicting redefinition.

Registered in `zdps_op_defs`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdps.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdps1.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdps1.c

Implements Level 2 / Display PostScript graphics extensions.

Stroke-adjust operators: `setstrokeadjust` and `currentstrokeadjust`.

Graphics-state object support:
- `gstate`
- `currentgstate`
- `setgstate`
- gstate-aware `copy`

`gstate_check_space()` validates VM store constraints for gstate refs, with a documented workaround that disallows writing into global VM gstates above save level 0. `gstate_unshare()` copy-on-writes saved gstate objects before mutation.

Rectangle operators:
- `.rectappend`
- `rectclip`
- `rectfill`
- `rectstroke`

`rect_get()` accepts either four numeric stack operands or numeric arrays/strings containing rectangle tuples. It uses a small local rectangle array for up to five rectangles and heap allocation beyond that.

`setbbox` writes the user path bounding box through `gs_setbbox()`.

Registered in `zdps1_l2_op_defs`; `zsetbbox()` is exported for user-path support.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdps1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdscpars.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdscpars.c

Provides the C/PostScript bridge for Russell Lang's DSC parser.

`.initialize_dsc_parser` allocates a `dsc_data_t` wrapper, initializes a `CDSC` parser, installs an error handler that returns `CDSC_OK`, and stores the wrapper in a caller dictionary under `DSC_struct`.

`.parse_dsc_comments` accepts a dictionary and DSC comment string, truncates overly long comments to parser line length, appends a line terminator, skips data-block comments such as `%%BeginData:` and `%%BeginBinary:`, calls `dsc_scan_data()`, ignores parser errors, transfers recognized fields into the dictionary, and replaces the input string with a PostScript name identifying the comment type.

The command table maps parser codes to names such as `Header`, `Creator`, `CreationDate`, `Title`, `For`, `BoundingBox`, `Orientation`, `Page`, `Pages`, `PageOrientation`, `PageBoundingBox`, `ViewingOrientation`, and `EOF`.

Helper routines write integers, strings, bounding boxes, orientation enums, and viewing-orientation arrays through Ghostscript parameter-list APIs.

The finalizer frees the `CDSC` parser when the wrapper struct is collected.

Registered in `zdscpars_op_defs`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdscpars.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfapi.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfapi.c

Implements the Ghostscript client side of the Font API plugin interface.

Major responsibilities:
- Adapt Ghostscript font dictionaries and font structs to `FAPI_font`.
- Provide callbacks for Type 1, CID, and Type 42 glyph/subroutine data.
- Serialize TrueType `sfnts` without `glyf`, `loca`, and `cmap` tables when needed.
- Install FAPI build procedures into fonts.
- Render characters through external FAPI renderer plugins while preserving Ghostscript cache/device semantics.

Key data bridges:
- `sfnts_reader` and `sfnts_writer` iterate over fragmented `sfnts` arrays and construct stripped SFNT data.
- `FAPI_FF_get_word()`, `FAPI_FF_get_long()`, and `FAPI_FF_get_float()` expose font feature fields.
- `FAPI_FF_get_subr()` and `FAPI_FF_get_glyph()` expose Type 1 subrs/global subrs and glyph data, including decryption when required.
- `get_GlyphDirectory_data_ptr()` handles CID GlyphDirectory string/array/dictionary access.

Font preparation:
- `FAPI_find_plugin()` locates a named FAPI renderer and opens it.
- `FAPI_prepare_font()` calls renderer `get_scaled_font()` for top-level and descendant fonts, retrieves font bbox, optionally gets decoding IDs, and releases renderer font data on failure.
- `FAPI_refine_font()` updates `FontBBox` and writes decoding/substitution names into font dictionaries.
- `zFAPIpassfont()` tries available FAPI plugins and inserts `/FAPI` into the font dictionary on success.
- `zFAPIrebuildfont()` replaces BuildChar/BuildGlyph refs with `.FAPIBuildChar`, `.FAPIBuildGlyph`, or `.FAPIBuildGlyph9`.

Rendering path:
- `FAPI_do_char()` computes font scale from CTM, device resolution, oversampling, CID/vertical metrics, encoding/decoding, glyph IDs, and metrics replacement state.
- It queries renderer metrics/raster/outline, sets Ghostscript cache device through `zchar_set_cache()`, and schedules `fapi_finish_render()`.
- `fapi_finish_render_aux()` either emits outlines into charpath/fill/stroke paths or copies/fill-masks renderer raster data to the target/current device.

CIDFontType 0 integration includes `.FAPIBuildGlyph9`, which maps CID through `ztype9mapcid()` and delegates rendering to the selected descendant font.

Registered operators: `.FAPIavailable`, `.FAPIpassfont`, `.FAPIrebuildfont`, `.FAPIBuildChar`, `.FAPIBuildGlyph`, and `.FAPIBuildGlyph9`.

Notable risk areas: many assumptions are documented as comments, including renderer cache behavior, glyph data lifetime between metrics and raster calls, SFNT/TTC limitations, and approximations in metrics replacement/oversampling fallback.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfapi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfarc4.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfarc4.c

Implements PostScript filter operators for the Arcfour cipher stream used by PDF encryption.

`ArcfourDecode` and `ArcfourEncode` both read a parameter dictionary, require a `Key` entry, initialize `stream_arcfour_state` with `s_arcfour_set_key()`, and create the corresponding read or write filter.

Because Arcfour is symmetric, encode and decode differ only in using `filter_write()` versus `filter_read()`.

The filter state is allocated in the stream memory pool rather than the key object's VM space because the state keeps no pointers.

Registered as filter operators in `zfarc4_op_defs`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfarc4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfbcp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfbcp.c

Implements BCP and TBCP filter creation.

Operators:
- `BCPEncode`
- `BCPDecode`
- `TBCPEncode`
- `TBCPDecode`

Encode filters use `filter_write_simple()` with the BCP/TBCP encode templates. Decode filters initialize `stream_BCPD_state` with null handlers for out-of-band `signal_interrupt` and `request_status`, then call `filter_read()` with the appropriate decode template.

The null handlers always return success and ignore those BCP signal paths.

Registered as filter operators in `zfbcp_op_defs`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfbcp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfcid.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfcid.c

Provides shared CID-keyed font utility routines.

`cid_font_system_info_param()` retrieves `CIDSystemInfo` from a CID font dictionary and parses it with `cid_system_info_param()`.

`cid_font_data_param()` validates a CID font dictionary and fills `gs_font_cid_data` with `CIDSystemInfo`, `CIDCount`, and `GDBytes` handling. It also returns the `GlyphDirectory` reference when present.

If `GlyphDirectory` is absent, `GDBytes` is required for standard CIDFont data. If `GlyphDirectory` is present as a dictionary or array, `GDBytes` is optional because the client may still need it for `CIDMap`.

The file has no operator table; it exports utilities used by CID font builders.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfcid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfcid0.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfcid0.c

Implements CIDFontType 0 / Ghostscript FontType 9 operators.

Glyph access:
- `get_index()` parses multi-byte big-endian indexes from glyph data.
- `cid0_read_bytes()` reads glyph bytes from in-memory `GlyphData`, arrays of strings, or `DataSource` streams.
- `z9_glyph_data()` maps a CID glyph to descendant FDArray index and charstring bytes, using either `GlyphDirectory` or binary CIDMap/GlyphData.
- `z9_glyph_outline()` renders outlines through `zcharstring_outline()` using the selected descendant Type 1/Type 2 font.
- `z9_glyph_info()` delegates to generic Type 1 glyph info.

FDArray handling:
- `fd_array_element()` builds descendant Type 1 or Type 2 fonts from FDArray dictionaries, initializes charstring data, installs Type 1/Type 2 build procedures, and replaces direct glyph accessors with invalid-font stubs because outlines are supplied externally by the parent CID font.
- `notify_remove_font_type9()` clears descendant parent pointers when the parent type 9 font is finalized.

`.buildfont9` parses CID font dictionaries, validates `FDArray`, `CIDFontName`, `FDBytes`, `GlyphData`/`DataSource`, `CIDMapOffset`, and `GlyphDirectory`, builds all descendant fonts, builds the parent `gs_font_cid0`, installs glyph procedures, stores CID data refs in font data, defines the font, and links descendants back to the parent.

`.type9mapcid` maps a CID to a charstring and FDArray index. If glyph lookup fails, it falls back to CID 0 and reports invalid font if that also fails.

Registered in `zfcid0_op_defs`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfcid0.c -->