# Group Research: group_120_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_gscsepr_h_sources__8b7bf9fd3d6a

Scope checked: `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscsepr.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscsepr.h

Client API for Ghostscript Separation color spaces. It depends on `gscspace.h` and documents that Separation is now represented as a single-component DeviceN space, except special `/All` and `/None` handling.

Exports constructors and tint-transform hooks: `gs_cspace_build_Separation`, `gs_build_Separation`, `gs_cspace_set_sepr_proc`, `gs_cspace_set_sepr_function`, and `gs_cspace_get_sepr_function`. The tint transform is run on demand and must not require interpreter callback.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscsepr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscspace.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscspace.c

Implements core Ghostscript color-space support. It defines DeviceGray, DeviceRGB, and DeviceCMYK type vectors, constructors, copying/assignment/release helpers, accessors, component counters, base-space lookup, default install behavior, serialization, and color-mapping linearity checks.

Important behavior includes size-aware color-space copying through `pcsfrom->type->stype->ssize`, DeviceCMYK overprint-mode handling based on device color-component names and mapping procs, and default interpolation checks for shaded fill optimization. It is tightly coupled to `gscspace.h`, `gxcspace.h`, graphics state overprint state, and device color mapping.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscspace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscspace.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscspace.h

Central public color-space header. It defines the inline color-space hierarchy: small base, regular base, direct, paint, and fully general spaces. The long comment explains the historical compromise of embedding alternate/base spaces inline rather than always using pointers, especially after ICCBased spaces complicated the model.

Defines `gs_color_space_index`, `gs_color_space_type`, `gs_color_space`, DevicePixel, CIE placeholders, ICC, Separation, DeviceN, Indexed, and Pattern parameter structures. It also declares Device color-space constructors, copy/assign/release routines, equality/accessor APIs, color restriction, and base/alternate-space lookup.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscspace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscssub.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscssub.c

Implements library-level color-space substitution for DeviceGray, DeviceRGB, and DeviceCMYK when a device has `UseCIEColor` enabled. `gs_setsubstitutecolorspace` installs or clears a substitute in `pgs->device_color_spaces`; `gs_current_Device*` accessors choose the substitute only when active.

It permits ICCBased substitutes when component counts match the target Device space. A notable maintenance concern is the non-ICCBased mask validation expression `!masks[index] && ...`, which appears ineffective for the defined nonzero masks and may have intended a bitwise membership check.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscssub.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscssub.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscssub.h

Declares the color-space substitution API and explains how it differs from PostScript `UseCIEColor`. Substitution affects library Device color setters and current Device space accessors, is visible to `currentcolorspace`, and does not affect explicit `setcolorspace` or image/shading color spaces.

Exports `gs_setsubstitutecolorspace`, `gs_currentsubstitutecolorspace`, and fast accessors for current DeviceGray, DeviceRGB, and DeviceCMYK spaces.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscssub.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdcolor.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdcolor.h

Defines Ghostscript device color representation for drivers and painting code. It provides macros for pure colors, null/unset colors, binary and colored halftones, halftone phase, pattern colors, and special non-client colors.

The main `gx_device_color_s` can hold pure colors, binary halftone state, colored halftone state, WTS state, pattern tile state, original client color, and pattern mask metadata. It also defines `gx_device_color_saved_s`, a pointer-free compact saved-color form for command lists/vector devices, avoiding unsafe retained halftone pointers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdcolor.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdevice.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdevice.c

Core Ghostscript device and page-control implementation. It covers device finalization, GC enumeration/relocation, device proc setup, page output, scanline copying, device lookup, device cloning, opening/closing, graphics-state device switching, null-device selection, geometry/resolution/media helpers, color parameter copying, and output-file parsing/opening/closing.

Device cloning is deliberately cautious because raw device structs may contain internal or self pointers. Output file parsing handles empty names, `-`, pipe commands, IODevices, and `%` page-number format strings with validation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdevice.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdevice.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdevice.h

Public device/page-control API. It forward-declares core device, memory-device, matrix, parameter-list, imager-state, and graphics-state types, then declares device open/close/copy/query, memory image-device creation, parameter get/put, page output, null/current device selection, and device switching APIs.

Notable API split: `gs_setdevice` erases if needed, `gs_setdevice_no_erase` returns `1` when erase is required, and `gs_setdevice_no_init` changes only the device. The `gs_initialize_imagedevice` macro appears to reference `color_size` although its parameter is `colors_size`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdevice.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdevmem.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdevmem.c

Creates and initializes memory/image devices. `gs_initialize_wordimagedevice` initializes caller-provided `gx_device_memory`; `gs_makewordimagedevice` allocates one and delegates initialization.

It supports paletted 1/2/4/8-bit devices and true-color `-16`, `-24`, `-32` modes, validates palettes for black/white and primaries, computes resolution from an orthogonal initial matrix, sets media size and imaging bbox, marks the device retained, and defers bitmap allocation until open.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdevmem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdfilt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdfilt.c

Implements graphics-state device filter stack management. `gs_push_device_filter` allocates a stack node, asks the filter to wrap the current device, installs the wrapper with `gs_setdevice_no_init`, and manages reference counts. `gs_pop_device_filter` calls filter `prepop`/`postpop`, restores the downstream device, and releases wrapper and stack references.

The stack stores the next stack node, filter object, and saved downstream device. Correct reference-count handling is the central concern.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdfilt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdfilt.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdfilt.h

Declares the device filter stack API. A device filter is a small procedure table with `push`, `prepop`, and `postpop` callbacks; the stack shadows a chained sequence of forwarding devices above the physical `setpagedevice` target.

Exports `gs_push_device_filter`, `gs_pop_device_filter`, `gs_clear_device_filters`, and the GC struct descriptor for `gs_device_filter_t`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdfilt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdll.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdll.c

Deprecated OS/2/Windows/Mac DLL compatibility front end implemented on top of the newer `iapi.h` Ghostscript API. It keeps a single global `gs_main_instance *` and a global old-style callback pointer.

Exports old DLL entry points: `gsdll_init`, execute begin/continue/end, `gsdll_exit`, and `gsdll_revision`. Stdio and polling callbacks bridge to `gsapi_set_stdio` and `gsapi_set_poll`; stderr is forwarded using the stdout callback code in this implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdll.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdll.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdll.h

Deprecated old DLL public interface header. It includes `iapi.h`, defines platform calling conventions, callback types, callback message constants, init return constants, and exported function prototypes for the legacy DLL API.

Also defines runtime function-pointer typedefs for dynamic loading. Comments direct users to the newer `API.htm`/`iapi.h` interface.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdll.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdllos2.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdllos2.h

OS/2-specific extension to the old `gsdll` API. It declares `gsdll_get_bitmap` for load-time dynamic linking and `PFN_gsdll_get_bitmap` for runtime dynamic linking.

This is a thin platform header with no implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdllos2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdllwin.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdllwin.h

Windows-specific extension to the old `gsdll` API. It declares bitmap/palette helper functions: `gsdll_copy_dib`, `gsdll_copy_palette`, `gsdll_draw`, and `gsdll_get_bitmap_row`.

Also provides matching runtime dynamic-link function typedefs using Windows types such as `HGLOBAL`, `HPALETTE`, `HDC`, `LPRECT`, and `LPBITMAPINFOHEADER`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdllwin.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdparam.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdparam.c

Implements default device parameter get/put behavior. `gs_get_device_or_hw_params` handles read-only prototypes by copying them when needed, then calls default or device-specific parameter procs. `gx_default_get_params` writes page device parameters, resolution/media/margins, color metadata, antialias settings, copy count, safety flags, and optional `HWColorMap`.

`gx_default_put_params` validates and applies `HWResolution`, `HWSize`, `PageSize`/`.MediaSize`, margins, imaging bbox, NumCopies, UseCIEColor, antialias bits, lock-safety, process color model, separations, and read-only parameters. Geometry changes close the device before mutation. The file also contains helpers for InputAttributes/OutputAttributes dictionaries and read-only parameter checking.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdparam.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdpnext.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdpnext.h

Small NeXT Display PostScript API header. It only includes `gsalpha.h` and `gsalphac.h` under an include guard.

There are no declarations beyond exposing those alpha-related APIs through this compatibility header.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdpnext.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdps.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdps.c

Implements Display PostScript view clipping helpers. `gs_initviewclip` clears an active view clip; `gs_viewclip` and `gs_eoviewclip` install winding or even-odd view clips through shared `common_viewclip`; `gs_viewclippath` converts the active view clip to the current path or fabricates a default clip rectangle.

The clipping implementation mirrors path clipping logic, allocating `pgs->view_clip` lazily and clearing the current path after clipping.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdps.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdps.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdps.h

Client header for Display PostScript facilities. It includes `gsiparm2.h` for device-source image parameters and declares view clipping APIs: `gs_initviewclip`, `gs_eoviewclip`, `gs_viewclip`, and `gs_viewclippath`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdps.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdps1.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdps1.c

Implements Display PostScript graphics additions. `gs_setbbox` sets/expands the current path bbox with fixed-point rounding slop and limit checks. `gs_rectappend`, `gs_rectclip`, `gs_rectfill`, and `gs_rectstroke` implement rectangle-list path, clip, fill, and stroke operations.

`gs_rectfill` has a fast path for orthogonal CTMs, rectangular clips, simple device colors, loaded color state, low antialiasing, and no active overprint mode; otherwise it falls back to path construction plus `gs_fill`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdps1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdsrc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdsrc.c

Implements `gs_data_source_t` GC support and access procedures. Strings and byte arrays are accessed by pointer or copied directly without bounds checks. Streams are positionable sources: the code uses the current stream buffer when possible, otherwise seeks and reads into the caller buffer, returning `rangecheck` on failure or short read.

GC enumeration/relocation varies by source type: const string pointer, stream pointer, or byte/floats data pointer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdsrc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdsrc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdsrc.h

Defines `gs_data_source_t`, an embedded data-source abstraction for strings, byte arrays, float arrays, and positionable streams. It declares the access procedure shape and helper macros for access/copy with automatic error return.

Provides initialization macros for string, string bytes, bytes, floats, and stream sources, plus `data_source_is_stream` and `data_source_is_array`. The comments note that float handling is anomalous but accepted.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdsrc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsequivc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsequivc.c

Implements equivalent CMYK color capture for spot colors in Separation and DeviceN spaces. Devices with separations can call `update_spot_equivalent_cmyk_colors` to inspect the current color space and fill missing CMYK equivalents using the tint transform through the alternate color space.

The implementation matches colorant names, skips DeviceN spaces containing `None`, builds a temporary color space with `use_alt_cspace`, creates a temporary imager state with capture color-map procs, and saves captured gray/RGB/CMYK results as CMYK. Separation/DeviceN capture procs only debug-print because the alternate path should resolve to gray/RGB/CMYK.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsequivc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsequivc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsequivc.h

Header for spot-color equivalent CMYK capture. It defines `cmyk_color`, with validity flag and CMYK `frac` channels, and `equivalent_cmyk_color_params`, with an all-valid flag and one color slot per maximum device separation.

Declares `update_spot_equivalent_cmyk_colors`, which updates missing equivalent CMYK values for separations tracked by a device.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsequivc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gserror.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gserror.h

Defines error logging and return macros. In debug builds, `gs_note_error(err)` calls `gs_log_error(err, __FILE__, __LINE__)`; in non-debug builds `gs_log_error` is macroed to return the error unchanged.

`return_error(err)` is the standard shorthand for returning a logged Ghostscript error code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gserror.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gserrors.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gserrors.h

Defines Ghostscript library error codes as negative integer macros, with non-negative values reserved for success. Includes common PostScript-style errors such as `invalidaccess`, `ioerror`, `limitcheck`, `rangecheck`, `typecheck`, `undefinedfilename`, `VMerror`, plus `gs_error_hit_detected` and fatal error code `-100`.

The file intentionally uses `int` macros rather than an enum to avoid casting churn.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gserrors.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gserver.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gserver.c

A simple procedural server front end for the Ghostscript interpreter. It declares and implements initialization, running PostScript strings, running files, and termination, with rudimentary job save/restore support for non-permanent file execution.

`gs_server_initialize` wraps file descriptors with C `FILE *`, runs Ghostscript initialization stages, sets quiet/nopause defaults, and optionally runs an init string. `gs_server_run_string` and `gs_server_run_files` capture error objects via `obj_cvs`; non-permanent file jobs use `zsave`/`zrestore` and `gs_interp_reset`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gserver.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsexit.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsexit.h

Declares client-supplied exit/abort hooks. `gs_to_exit` handles normal interpreter exit cleanup without necessarily calling system `exit`; `gs_to_exit_with_code` can return the PostScript error code; `gs_abort` handles fatal aborts and may call platform-independent `gp_do_exit`.

This header defines the library/client boundary for termination behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsexit.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfcid.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfcid.c

CID-keyed font support. It defines GC descriptors for CID system info and CID font variants, including CIDFontType 0, user-defined CID, and CIDFontType 2. It also defines GC support for FDArray Type 1 font pointer arrays.

Utility routines include null CIDSystemInfo initialization/testing, extracting CIDSystemInfo by font type, Registry/Ordering compatibility checks, default CIDFontType 0 glyph enumeration through `glyph_data`, indexed FDArray font access, and detection of Type 2 subfonts inside CIDFontType 0 FDArray.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfcid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfcid2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfcid2.c

Builds CIDFontType 2 support from Type 42 TrueType fonts and creates CMaps from TrueType cmap tables. `gs_font_cid2_from_type42` allocates a CIDFontType 2, copies Type 42 state, resets resource/list metadata, assigns a new id, sets CID metadata, and uses an identity CIDMap proc.

The TrueType CMap implementation targets Platform 3, Encoding 1, Format 4. It decodes 2-byte characters by linear segment search, enumerates a single two-byte range, enumerates format-4 lookups, and constructs a `gs_cmap_tt_16bit_format4_t` with offsets into the font data.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfcid2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfcmap.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfcmap.c

Implements generic CMap support, Identity CMaps, CMap allocation/enumeration helpers, identity detection, and ToUnicode CMaps. Identity maps decode fixed-size big-endian codes directly to CIDs or characters and provide range/lookup enumeration.

`gs_cmap_alloc` allocates the CMap and CIDSystemInfo array, initializes ids, WMode, metadata, and proc table. ToUnicode CMaps store a compact 2-byte Unicode mapping array, enumerate contiguous bfrange-style spans, track identity status, and expose `gs_cmap_ToUnicode_add_pair`. The ToUnicode decode proc is intentionally unsupported/asserting because callers enumerate rather than decode it.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfcmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfcmap.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfcmap.h

Public CMap interface header. It forward-declares `gs_cmap_t` and declares creation of Identity CMaps, char-identity CMaps, decoding one character from a string, allocating ToUnicode CMaps, and adding ToUnicode code pairs.

The decode contract distinguishes CID/name results, character-code results with byte count, undefined glyphs, and errors.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfcmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfcmap1.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfcmap1.c

Implements Adobe-based CMap decoding. It defines GC descriptors for Adobe1 CMaps and lookup ranges, including glyph marking for `CODE_VALUE_GLYPH`. The decoder scans lookup ranges in reverse to honor `usecmap`, handles prefixes, multidimensional ranges, partial matches, `.notdef` maps, and fallback to CID 0 using the shortest defined character length.

It also implements code-space range enumeration, lookup/entry enumeration for defined and notdef maps, identity computation through the generic helper, and `gs_cmap_adobe1_alloc`, which allocates ranges, lookup structs, keys, values, and initializes the Adobe1 CMap layout for later population.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfcmap1.c -->