# Group Research: group_148_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_zcontrol_c_sources_075b5ac9f90c

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/9front`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zcontrol.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zcontrol.c

Implements Ghostscript/PostScript control-flow and execution-stack operators.

Key behavior:
- Defines `exec`, `.execn`, `superexec`, `.runandhide`, `if`, `ifelse`, `for`, `%for_samples`, `repeat`, `loop`, `exit`, `stop`, `.stop`, `stopped`, `.stopped`, `currentfile`, `execstack`, and `countexecstack`.
- Uses continuation operators on the execution stack for looping, conditionals, stopped contexts, CIE sample loops, and `cond`.
- `pop_estack` unwinds execution frames and runs cleanup procedures attached to execution-stack marks.
- `count_to_stopped` locates matching stopped frames by signal mask; unmatched `exit`/`stop` synthesizes a quit with `invalidexit`.
- `execstack` copies the execution stack into a user array while sanitizing internal operators and transient structs.

Dependencies:
- Heavily tied to `estack`, `oper`, `files`, packed arrays, operand/ref stacks, and interpreter file-cache handling.

Research notes:
- This file is core interpreter control machinery. Correct stack-depth accounting, hidden execution marks, and cleanup execution are the main risk areas.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zcontrol.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zcrd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zcrd.c

Implements CIE color rendering dictionary operators and cache setup.

Key behavior:
- Provides `currentcolorrendering`, `.buildcolorrendering1`, `.builddevicecolorrendering1`, `.setcolorrendering1`, and `.setdevicecolorrendering1`.
- Validates ColorRenderingType 1 dictionaries, procedure entries, matrices, ranges, white/black points, and optional RenderTable data.
- Builds `gs_cie_render` objects, installs them into interpreter state, and caches EncodeLMN, EncodeABC, RenderTableT, and TransformPQR computations.
- Uses continuation operators to sample PostScript procedures into C-side CIE caches.
- Includes C implementations of default relative-colorimetric `TransformPQR_scale_WB[0-2]`.

Dependencies:
- Depends on CIE rendering/color-space internals, dictionary parameter helpers, interpreter memory, and e-stack cache continuations.

Research notes:
- Most complexity is asynchronous cache loading: failures must restore `esp` and free partially built rendering objects.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zcrd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zcsdevn.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zcsdevn.c

Implements DeviceN color-space setup.

Key behavior:
- Defines `.setdevicenspace`, taking a four-element DeviceN color-space array.
- Treats the current color space as the alternate color space, copies it into the new DeviceN structure, and initializes `gs_color_space_type_DeviceN`.
- Validates component-name array size, enforces `GS_CLIENT_COLOR_MAX_COMPONENTS`, converts string names to PostScript names, and stores name indices.
- Extracts the tint-transform function with `ref_function` and installs it through `gs_cspace_set_devn_function`.
- Preserves interpreter color-space procedure refs for layer names and tint transform.

Dependencies:
- Uses DeviceN graphics-library builders, function refs, name table access, interpreter graphics state, and halftone/color-remap support.

Research notes:
- Cleanup on validation failure releases allocated DeviceN names/map objects. The file relies on `memmove` to avoid color-space aliasing issues.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zcsdevn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zcsindex.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zcsindex.c

Implements Indexed color-space setup and mapped lookup-cache loading.

Key behavior:
- Defines `.setindexedspace`, where the current color space becomes the Indexed base space.
- Validates a four-element Indexed color-space array and `hival` range.
- Supports string lookup tables directly, tolerating extra bytes but requiring at least the needed table length.
- Supports procedural lookup tables by allocating a `gs_indexed_map` and scheduling continuation-driven sampling of each index.
- `indexed_map1` stores generated component values into the map as the tint/index procedure runs.
- `zcs_begin_map` is shared utility code for Indexed and tint-map style color-space loaders.

Dependencies:
- Uses graphics color-space APIs, interpreter e-stack continuations, numeric parameter helpers, and VM-space-aware allocation.

Research notes:
- The explicit `memmove` around base-space copying avoids strict-aliasing/compiler misoptimization problems documented in comments.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zcsindex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zcspixel.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zcspixel.c

Implements DevicePixel color-space setup.

Key behavior:
- Defines `.setdevicepixelspace`.
- Accepts a two-element array, reads element 1 as an integer pixel depth, initializes a DevicePixel color space, and installs it with `gs_setcolorspace`.
- Pops the operand only after successful color-space installation.

Dependencies:
- Uses `gs_cspace_init_DevicePixel`, interpreter allocation, and graphics-state color-space APIs.

Research notes:
- This is a small adapter between PostScript color-space array syntax and the graphics-library DevicePixel color-space constructor.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zcspixel.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zcssepr.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zcssepr.c

Implements Separation color-space and overprint operators.

Key behavior:
- Defines `.setseparationspace`, `currentoverprint`, `setoverprint`, `.currentoverprintmode`, and `.setoverprintmode`.
- Treats Separation as a single-component DeviceN-like space except for `/All` and `/None`.
- Validates separation name, alternate color space, tint-transform procedure, and tint function.
- Builds a Separation space, records the separation name/type, installs `gs_cspace_set_sepr_function`, and updates interpreter color-space procedure refs.
- Provides direct wrappers for overprint flag and overprint mode in graphics state.

Dependencies:
- Uses name-table operations, Separation/DeviceN graphics-library structures, function extraction, and interpreter graphics state.

Research notes:
- Like DeviceN, failure paths restore the previous interpreter color-space refs and free the allocated separation map.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zcssepr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zdevcal.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zdevcal.c

Defines the special `%Calendar%` IODevice.

Key behavior:
- Registers `gs_iodev_calendar` as a special read-only device with only `get_params` implemented.
- `calendar_get_params` writes current local time fields: Year, Month, Day, Weekday, Hour, Minute, and Second.
- Adds a `Running` boolean that is true when `time()` and `localtime()` succeed, false when time lookup fails.
- Converts `tm_year` to full year and `tm_mon` to one-origin month before returning.

Dependencies:
- Uses Ghostscript IODevice and parameter-list interfaces plus C runtime time functions.

Research notes:
- This is not file I/O; it exposes process-local clock data through the PostScript IODevice parameter mechanism.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zdevcal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zdevice.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zdevice.c

Implements core device-related PostScript operators.

Key behavior:
- Provides device copying, `currentdevice`, `.devicename`, `.doneshowpage`, `flushpage`, `.getbitsrect`, `.getdevice`, device/hardware parameter reads, `makewordimagedevice`, `nulldevice`, `.outputpage`, `.putdeviceparams`, and `.setdevice`.
- `.getbitsrect` extracts a rectangle of device bits into a supplied string with alpha/depth options.
- Parameter read/write operators bridge stack parameter lists to `gs_get_device_or_hardware_params` and `gs_putdeviceparams`.
- `.putdeviceparams` reports per-key errors on the operand stack, detects reopening/resizing, and clears current pagedevice state.
- `.setdevice` respects locked safety parameters and returns an erase flag.

Dependencies:
- Uses `gx_device`, get-bits API, stack parameter lists, matrix parsing, image-device creation, and interpreter graphics state.

Research notes:
- Device parameter mutation is stateful and may close/reopen devices; current-device reinstall and pagedevice clearing are key side effects.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zdevice.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zdevice2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zdevice2.c

Implements Level 2 page-device operators and wrappers for save/restore-sensitive graphics-state operations.

Key behavior:
- Adds `.currentshowpagecount`, `.currentpagedevice`, `.setpagedevice`, `.callinstall`, `.callbeginpage`, and `.callendpage`.
- Replaces `copy`, `gsave`, `save`, `gstate`, `currentgstate`, `grestore`, `grestoreall`, `restore`, and `setgstate` with page-device-aware wrappers.
- Detects when saving or restoring graphics state requires creating or restoring a pagedevice dictionary.
- Uses `push_callout` to invoke PostScript procedures such as `%gsavepagedevice`, `%restorepagedevice`, and `%setgstatepagedevice`.
- Temporarily unlocks `LockSafetyParams` when a restore path must apply different page-device parameters.

Dependencies:
- Bridges device/page procedures, interpreter save/restore machinery, gstate objects, and dictionary/name lookup.

Research notes:
- This file is policy glue: it keeps C graphics-state operations compatible with PostScript pagedevice semantics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zdevice2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zdfilter.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zdfilter.c

Provides PostScript access to the device filter stack.

Key behavior:
- Defines `.popdevicefilter`.
- Calls `gs_pop_device_filter` using stable interpreter memory and the current graphics state.
- Notes that `pushpdf14devicefilter` is defined elsewhere.

Dependencies:
- Uses graphics-state/device-filter APIs from `gsdfilt.h`.

Research notes:
- This is a minimal operator wrapper. Its main role is exposing device-filter unwinding to PostScript-level transparency/filter management.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zdfilter.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zdict.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zdict.c

Implements PostScript dictionary and dictionary-stack operators.

Key behavior:
- Provides `dict`, `maxlength`, `begin`, `end`, `def`, `load`, `.undef`/`undef`, `known`, `where`, dictionary `copy`, `currentdict`, `countdictstack`, `dictstack`, and `cleardictstack`.
- `zop_def` has a fast path for redefining named keys in the top dictionary while combining write/access/store checks.
- `zload` uses fast name lookup for names and explicit dictionary-stack iteration for other key types.
- Level 2/extensions include `.dictcopynew`, `.dicttomark`, `.forceundef`, `.knownget`, `.knownundef`, and `.setmaxlength`.
- `zdicttomark` builds a dictionary from mark-delimited key/value pairs in top-to-bottom order to preserve duplicate-key behavior.

Dependencies:
- Uses dictionary internals, dictionary-stack macros, packed/name lookup helpers, VM-space/store checks, and level-mode flags.

Research notes:
- This is performance-sensitive interpreter infrastructure. Store checks and top-dictionary fast paths are central to safe mutation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zdict.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zdosio.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zdosio.c

Implements MS-DOS direct I/O diagnostic operators.

Key behavior:
- Defines `.inport`, `.inportb`, `.outport`, `.outportb`, `.peek`, and `.poke`.
- Reads/writes hardware I/O ports through DOS runtime functions.
- Reads/writes arbitrary byte memory addresses through integer operands.
- File comment explicitly says this should never be included in a released configuration.

Dependencies:
- Uses `dos_.h` direct port routines and interpreter operand checks.

Research notes:
- This is privileged, unsafe debugging functionality. The memory and port operators bypass normal Ghostscript safety boundaries.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zdosio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zdouble.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zdouble.c

Implements double-precision arithmetic operators using 8-byte strings as double containers.

Key behavior:
- Provides double arithmetic, unary math, transcendental functions, comparisons, and conversions.
- Accepts integers, reals, and readable 8-byte strings as operands; result-producing operators require a writable 8-byte string.
- Implements `.dadd`, `.ddiv`, `.dmul`, `.dsub`, `.dabs`, `.dceiling`, `.dfloor`, `.dneg`, `.dround`, `.dsqrt`, `.dtruncate`, `.darccos`, `.darcsin`, `.datan`, `.dcos`, `.dexp`, `.dln`, `.dlog`, `.dsin`.
- Conversion operators parse strings to doubles, convert to integer/real, and format doubles to strings.
- Checks division by zero, invalid powers, log/sqrt domains, string syntax, and target buffer sizes.

Dependencies:
- Uses math portability wrappers and Ghostscript numeric/operator helpers.

Research notes:
- Double values are represented in host binary format inside strings, so portability depends on caller and platform agreement.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zdouble.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zdpnext.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zdpnext.c

Implements NeXT Display PostScript extensions for alpha, compositing, and image sizing.

Key behavior:
- Provides `currentalpha`, `setalpha`, `.alphaimage`, `composite`, `compositerect`, `dissolve`, `.sizeimagebox`, and `.sizeimageparams`.
- Builds temporary alpha compositor devices around fill/image operations and restores the original device afterward.
- `composite`/`dissolve` copy source rectangles from another gstate or current gstate to a destination point.
- `.sizeimagebox` transforms and clips a source rectangle to device coordinates, returning a matrix adjusted to the clipped box.
- `.sizeimageparams` derives bits/sample, multiproc flag, and component count from the current device.
- Includes true-color detection for grayscale, RGB, and CMYK devices by testing device color mapping.

Dependencies:
- Uses compositor device creation, ImageType 2 processing, current matrix/path state, device color mapping, and imager alpha APIs.

Research notes:
- Composite setup/teardown is delicate because it swaps current devices temporarily and must close/free compositor devices on all paths.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zdpnext.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zdps.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zdps.c

Implements general Display PostScript extensions.

Key behavior:
- Provides screen-phase operators `.setscreenphase` and `.currentscreenphase`.
- Implements `.image2`, a device-source image operator using a source gstate, origin, dimensions, image matrix, pixel-copy flag, and optional `UnpaintedPath`.
- Exposes view clipping operators: `viewclip`, `eoviewclip`, `initviewclip`, and `viewclippath`.
- Implements `defineusername`, maintaining the DPS user-name array in stable local VM so it survives save/restore.
- Expands the user-name array geometrically while preserving existing name entries.

Dependencies:
- Uses DPS graphics state APIs, ImageType 2 processing, path/userpath creation, allocator name arrays, and dictionary helpers.

Research notes:
- `.image2` can allocate an `UnpaintedPath`, convert it to a user path, and write it back into the input dictionary.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zdps.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zdps1.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zdps1.c

Implements Level 2 / Display PostScript graphics-state object and rectangle operators.

Key behavior:
- Extends `copy` for gstate objects.
- Provides `setstrokeadjust`, `currentstrokeadjust`, `gstate`, `currentgstate`, `setgstate`, rectangle append/clip/fill/stroke operators, and `setbbox`.
- `zgstate` allocates an `igstate_obj`, copies the current `gs_state`, marks contained refs new, and saves the embedded ref for restore tracking.
- `zcopy_gstate` and `zcurrentgstate` unshare saved gstates, perform VM-space checks, save old refs, and copy graphics-state contents.
- Rectangle operators accept either four numeric operands or packed numeric arrays/strings, using a small local rectangle buffer before heap allocation.

Dependencies:
- Uses gstate internals, save/restore store machinery, path rectangle APIs, numeric-array helpers, and char/userpath support.

Research notes:
- Comments document a known workaround: global gstate writes are disallowed during nonzero save levels because non-ref members are not fully space-checked.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zdps1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zdscpars.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zdscpars.c

Bridges Ghostscript PostScript code to Russell Lang’s DSC parser.

Key behavior:
- Defines `.initialize_dsc_parser` and `.parse_dsc_comments`.
- Stores a `CDSC *` parser pointer in a client dictionary under `DSC_struct`, wrapped in a GC-managed `dsc_data_t` with finalizer.
- Ignores parser errors by returning `CDSC_OK` from the error handler and mapping negative scan results to NOP.
- Skips data/binary block comments that would otherwise cause the C parser to consume external data.
- Maps supported DSC comment codes to PostScript names and writes selected values into the supplied DSC dictionary.
- Handles header/EPSF, creator, creation date, title, for, bounding boxes, pages, orientation, viewing orientation, and EOF/NOP.

Dependencies:
- Uses `dscparse.h`, dictionary parameter-list writing, interpreter struct allocation/finalization, and PostScript name creation.

Research notes:
- This file is intentionally a narrow bridge; higher-level DSC interpretation is delegated to `gs_dscp.ps`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zdscpars.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfaes.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfaes.c

Implements the PostScript AES decode filter wrapper used for PDF decryption.

Key behavior:
- Defines `AESDecode`.
- Reads a `Key` string from the parameter dictionary.
- Initializes `stream_aes_state` with `s_aes_set_key`.
- Creates a read filter with `filter_read` and the AES stream template.

Dependencies:
- Uses Ghostscript filter infrastructure, stream state interfaces, dictionary lookup, and `saes.h`.

Research notes:
- The filter state is copied into stream-managed storage; the wrapper passes zero rspace because it keeps no external pointers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfaes.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfapi.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfapi.c

Implements the Ghostscript Font API client that delegates font preparation and glyph rendering to external renderer plugins.

Key behavior:
- Defines path callbacks for converting renderer outlines into Ghostscript paths, including optional closepath repair.
- Provides readers/writers for Type 42 `sfnts` arrays and serializes TrueType data while omitting `glyf`, `loca`, and `cmap` tables for renderer use.
- Exposes font feature callbacks for Type 1, Type 2, CID, and Type 42 data: font matrices, blue values, stem snaps, subrs/global subrs, glyph strings, TrueType glyph data, and glyph-directory data.
- Selects FAPI plugins, opens renderers, prepares scaled fonts, refines FontBBox, installs Decoding/SubstNWP metadata, and registers cleanup notifiers.
- Rebuilds fonts by replacing BuildChar/BuildGlyph procedures with `.FAPIBuildChar`, `.FAPIBuildGlyph`, or `.FAPIBuildGlyph9`.
- Implements glyph rendering flow: resolve char code/name/CID, prepare font scale and oversampling, provide glyph data, reconcile metrics, set cache device, and finish with raster copy or outline fill/stroke.
- Implements `.FAPIavailable`, `.FAPIpassfont`, `.FAPIrebuildfont`, `.FAPIBuildChar`, `.FAPIBuildGlyph`, and `.FAPIBuildGlyph9`.

Dependencies:
- Integrates font internals, CID mapping, Type 1 encryption, Type 42 sfnts, text enumeration/cachedevice, plugins, device raster APIs, and path painting.

Research notes:
- This is high-risk integration glue. Correctness depends on plugin contracts, glyph data lifetime, VM allocation, metrics substitution, oversampling retry, and renderer cleanup.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfapi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfarc4.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfarc4.c

Implements Arcfour/RC4 encode and decode filter wrappers.

Key behavior:
- Defines `ArcfourDecode` and `ArcfourEncode`.
- Reads the `Key` string from the parameter dictionary.
- Initializes `stream_arcfour_state` with `s_arcfour_set_key`.
- Uses the same stream template for decode and encode because RC4 is symmetric.
- Creates read filters with `filter_read` and write filters with `filter_write`.

Dependencies:
- Uses Ghostscript filter/stream infrastructure, dictionary helpers, and `sarc4.h`.

Research notes:
- Like AES, wrapper state has no retained external pointers, so stream allocation can own the copied filter state.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfarc4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfbcp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfbcp.c

Implements BCP and TBCP filter creation operators.

Key behavior:
- Defines `BCPEncode`, `BCPDecode`, `TBCPEncode`, and `TBCPDecode`.
- Encode operators use simple write-filter wrappers.
- Decode operators initialize `stream_BCPD_state` with no-op handlers for BCP out-of-band interrupt/status signals.
- Supports both ordinary Binary Communications Protocol and Tagged BCP templates.

Dependencies:
- Uses stream templates from `sbcp.h` and Ghostscript filter helpers.

Research notes:
- This file deliberately ignores BCP signal callbacks, making the filters pure byte-stream transforms from the interpreter’s point of view.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfbcp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfcid.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfcid.c

Provides shared CID-keyed font dictionary utilities.

Key behavior:
- `cid_font_system_info_param` extracts and validates `CIDSystemInfo` from a CIDFont dictionary.
- `cid_font_data_param` extracts common CID font data including `CIDSystemInfo`, `CIDCount`, optional `GlyphDirectory`, and `GDBytes`.
- Requires `GDBytes` when no `GlyphDirectory` is present.
- Allows `GlyphDirectory` as a dictionary or array and treats `GDBytes` as optional in that case.

Dependencies:
- Uses CID font structures, dictionary parameter helpers, and shared font-building headers.

Research notes:
- This is helper code used by CID font builders; it centralizes validation of common CID dictionary fields.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfcid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfcid0.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfcid0.c

Implements CIDFontType 0 / FontType 9 construction and glyph access.

Key behavior:
- Reads CID glyph data from `GlyphDirectory`, in-memory `GlyphData`, string arrays, or seekable `DataSource` streams.
- `z9_glyph_data` maps CIDs to FDArray index and CharString data through either GlyphDirectory records or CIDMap/GlyphData offsets.
- `z9_glyph_outline` renders CIDFontType 0 glyph outlines by selecting the appropriate descendant Type 1/Type 2 font and calling charstring outline code.
- `fd_array_element` builds descendant FDArray fonts, parsing Type 1 or Type 2 charstring parameters and replacing direct glyph accessors with invalidfont stubs.
- `.buildfont9` validates CID font dictionaries, builds FDArray descendants, creates the top-level CID font, stores GlyphDirectory/GlyphData/DataSource refs, and registers cleanup notification.
- `.type9mapcid` maps a CID to `<charstring> <font_index>`, falling back to CID 0 when glyph loading fails.

Dependencies:
- Uses CID data helpers from `zfcid.c`, Type 1/Type 2 font parameter parsing, font builders, streams, glyph-data lifetime helpers, and charstring outline functions.

Research notes:
- Important edge cases include missing glyphs, invalid FD indexes, GlyphData spanning multiple strings, stream I/O failures, and descendant parent-pointer cleanup.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfcid0.c -->