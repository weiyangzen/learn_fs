# Group Research: group_1558_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_gscsepr_h_sources_o_c668812db769

Scope: researched every listed file under `sources/os/plan9/plan9/sys/src/cmd/gs/src/` completely, in manifest order. These files are Ghostscript library sources covering color spaces, device/page control, device parameters, DLL/server APIs, DPS helpers, data sources, CID/CMap support, and related error/exit interfaces.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscsepr.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscsepr.h

## Role

`gscsepr.h` is the client-facing interface for Ghostscript Separation color spaces. It documents that modern Separation handling is mostly implemented as a single-component `DeviceN` color space, with `/All` and `/None` kept as special cases.

## Exposed API

- `gs_cspace_build_Separation(...)` allocates/builds a Separation color space using a separation name, alternate color space, cache size, and memory allocator.
- `gs_build_Separation(...)` initializes the central Separation state inside an already allocated `gs_color_space`.
- `gs_cspace_set_sepr_proc(...)` installs a tint-transform callback with opaque procedure data.
- `gs_cspace_set_sepr_function(...)` installs a `gs_function_t` as the tint transform.
- `gs_cspace_get_sepr_function(...)` retrieves the function object when the transform is function-backed.

## Dependencies

Includes `gscspace.h` for `gs_color_space`, `gs_separation_name`, and memory/color-space types. Forward-declares `gs_function_t` if not already defined.

## Integration Notes

The header is intentionally thin; implementation lives elsewhere in the Ghostscript color-space subsystem. The comments are important because they explain why older multi-entry tint caches are gone and why tint transforms must be executable without interpreter callouts.

## Risks

Callers must pass compatible alternate color spaces and tint transforms. The API exposes mutable `gs_color_space *` setup, so incorrect initialization order can leave compound color-space internals inconsistent.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscsepr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscspace.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscspace.c

## Role

`gscspace.c` implements core color-space construction, copying, reference-count adjustment hooks, base-space accessors, overprint setup, linearity checks, serialization, and GC tracing for Ghostscript color spaces.

## Main Behavior

It defines standard `gs_color_space_type` vectors for `DeviceGray`, `DeviceRGB`, and `DeviceCMYK`. Each vector supplies component counts, initial/restrict paint procedures, concrete/remap procedures, overprint handlers, count-adjustment hooks, serialization, and linearity tests.

The file provides heap allocation and stack initialization for device color spaces:

- `gs_cspace_init`, `gs_cspace_alloc`
- `gs_cspace_init_DeviceGray/RGB/CMYK`
- `gs_cspace_build_DeviceGray/RGB/CMYK`
- `gs_cspace_init_from`, `gs_cspace_assign`, `gs_cspace_release`

Accessors include color-space index, component count, color restriction, and base/alternate color-space lookup.

## Overprint Logic

Generic device/CIE/ICC spaces use `gx_spot_colors_set_overprint`. `DeviceCMYK` has special handling for overprint mode 1: it probes the current device for Cyan/Magenta/Yellow/Black component indexes and verifies that CMYK mapping routes each process component directly. It then intersects drawn process components with nonzero device-color components.

## Linearity

The default linearity check remaps endpoint and midpoint colors to device colors and compares pure device-color components within `smoothness`. Halftones are treated as non-linear and rejected.

## Dependencies

Depends on internal color mapping (`gxcspace.h`, `gxcmap.h`), graphics state (`gzstate.h`, `gxistate.h`), device APIs, overprint compositing, streams, and Ghostscript memory/GC descriptors.

## Risks

Static device color-space prototypes are lazily initialized and not explicitly synchronized. Color-space copy uses each type descriptor’s size and relies on callers to ensure destination storage is large enough. Overprint component probing depends on device color-component names and mapping procedures being correct.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscspace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscspace.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscspace.h

## Role

`gscspace.h` is the public color-space model definition for Ghostscript. It defines color-space indexes, storage hierarchy, shared parameter structs, and the client API for constructing and inspecting color spaces.

## Data Model

The header explains the historical embedded-storage design:

- small base spaces: DeviceGray/RGB/CMYK/Pixel and CIE spaces
- regular base spaces: small base spaces plus ICCBased
- direct spaces: base plus Separation and DeviceN
- paint spaces: direct plus Indexed
- general spaces: paint plus Pattern

Because subspaces are stored inline rather than through uniform pointers, each level has a larger struct type. The header explicitly warns that assignment must copy according to the actual source type size and that callers are responsible for fitting source objects into destination storage.

## Key Types

Defines `gs_color_space_index`, `gs_color_space_type`, `gs_color_space`, `gs_small_base_color_space`, `gs_base_color_space`, `gs_direct_color_space`, and `gs_paint_color_space`.

It also defines parameter structs for DevicePixel, ICCBased, Separation, DeviceN, Indexed, and Pattern spaces. Separation and DeviceN include colorant-name callbacks and flags for forcing alternate color-space use.

## API

Exposes device color-space initializers/builders, copy/assign/release helpers, index/component accessors, equality declaration, legal color restriction, and base/alternate-space retrieval.

## Dependencies

Includes `gsmemory.h` and `gsiparam.h`; references CIE, ICC, DeviceN map, client color, and GC descriptor types defined elsewhere.

## Risks

The inline hierarchy is memory-sensitive and type-size-sensitive. The comments note incomplete reference management for some non-scalar parameters, especially Indexed lookup tables and deeper compound parameters.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscspace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscssub.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscssub.c

## Role

`gscssub.c` implements library-level color-space substitution, corresponding to `.setsubstitutecolorspace` and `.currentsubstitutecolorspace`.

## Main Behavior

`gs_setsubstitutecolorspace` sets or clears substitutions for DeviceGray, DeviceRGB, and DeviceCMYK only. It validates the requested device-space index, accepts ICCBased substitutes only when their component count matches the target device space, then either allocates a private substituted color-space copy or assigns over an existing one.

If `pcs` is null, it resets a substitution to the shared default device color space.

The accessors:

- `gs_current_DeviceGray_space`
- `gs_current_DeviceRGB_space`
- `gs_current_DeviceCMYK_space`

return the substituted space only when `pgs->device->UseCIEColor` is true and a per-state substitute exists. Otherwise they return the shared default device space.

`gs_currentsubstitutecolorspace` dispatches by device color-space index.

## Dependencies

Uses graphics-state internals (`gzstate.h`), device client state (`gxdevcli.h`), color-space struct descriptors (`gxcspace.h`), and Ghostscript memory/error helpers.

## Risks

The non-ICC validation expression appears suspicious: `else if (!masks[index] && (1 << gs_color_space_get_index(pcs)))` is false for all populated mask entries, so the intended mask check is likely ineffective. Substitution state is shared across copied graphics states per the header contract, so callers should not assume ordinary `grestore` undoes substitutions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscssub.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscssub.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscssub.h

## Role

`gscssub.h` documents and exposes Ghostscript’s library-level color-space substitution API.

## Semantics

When device `UseCIEColor` is false, DeviceGray/RGB/CMYK behavior is unchanged. When true, selected operations may substitute configured color spaces for implied device spaces:

- `gs_setgray`, `gs_setrgbcolor`, `gs_sethsbcolor`, `gs_setcmykcolor`
- `gs_current_Device{Gray,RGB,CMYK}_space`

The comments clarify differences from PostScript `UseCIEColor`: substitution is visible to `gs_currentcolorspace`, does not affect explicit `gs_setcolorspace`, and does not alter image or shading `ColorSpace` members. Traditional color accessors still report values in the pre-substitution device color model.

## API

- `gs_setsubstitutecolorspace(...)`
- `gs_currentsubstitutecolorspace(...)`
- fast internal accessors for current DeviceGray, DeviceRGB, and DeviceCMYK spaces

Passing `NULL` to `gs_setsubstitutecolorspace` clears a substitution.

## Dependencies

Includes `gscspace.h` and relies on `gs_state`, `gs_color_space`, and `gs_color_space_index`.

## Risks

The header notes that substitutions survive ordinary `grestore` and `setgstate`; copied graphics states share substitutions. This is intentional but can surprise callers expecting normal graphics-state stack behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscssub.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdcolor.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdcolor.h

## Role

`gsdcolor.h` defines the device-color representation used by Ghostscript drivers and painting internals.

## Data Model

A `gx_device_color` has a type tag, base color union, phase, optional preserved client color, and optional Pattern mask. It represents:

- unset/null colors
- pure device colors
- binary halftones
- colored halftones
- Well-Tempered Screening levels
- colored Pattern tiles
- Pattern masks

The file separates read-only driver helpers from mutation macros, then exposes lower-level internals because many callers need inline access for performance.

## Key Helpers

Macros detect and extract pure, binary halftone, and colored halftone colors; set null/pure/binary/tile/pattern states; set halftone phase; and mark non-client special colors. It declares `gx_device_color_equal` and `gx_complete_halftone`.

## Saved Colors

`gx_device_color_saved` is a compact non-owning representation used by command-list/vector devices to avoid resending redundant color state. It intentionally avoids storing halftone pointers because device-color references to halftones are not reference-counted.

## Dependencies

Includes client color, bitmap, halftone tile, color index, arithmetic, and WTS headers.

## Risks

Many macros mutate multiple fields without statement wrappers, so call-site syntax matters. Device colors may contain non-reference-counted pointers to halftones/tiles; saved colors deliberately avoid some pointers, making them unsuitable for fully restoring Pattern state.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdcolor.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdevice.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdevice.c

## Role

`gsdevice.c` implements Ghostscript library device/page control: device finalization, cloning, opening/closing, current-device changes, raster sizing, page output, null devices, geometry updates, color parameter copying, and output filename parsing/opening.

## Main API

Implements public functions declared in `gsdevice.h`, including:

- `gs_flushpage`, `gs_copypage`, `gs_output_page`
- `gs_currentdevice`, `gs_devicename`, `gs_getdevice`
- `gs_copydevice`, `gs_copydevice2`
- `gs_opendevice`, `gs_closedevice`
- `gs_setdevice`, `gs_setdevice_no_erase`, `gs_setdevice_no_init`
- `gs_nulldevice`
- device raster/geometry helpers and output-file helpers

## Device Lifetime

`gx_device_finalize` calls optional device finalization, closes open devices, and frees dynamic structure descriptors. `gs_copydevice2` copies device prototypes/instances into immovable memory, building or copying a GC structure descriptor when needed. `keep_open` is supported but explicitly documented as dangerous.

## Graphics-State Integration

Setting a device may open it, set memory-device targets, install it into the graphics state, reset CTM/clip, clear cachedevice/charpath state, update color mapping procedures, invalidate device color, and reapply overprint.

## Output Files

`gx_parse_output_file_name` handles default IO devices, `%stdout`, `%pipe`, `-`, and one printf-style page-number format. `gx_device_open_output_file` expands page count formats and chooses IODevice or platform printer open paths.

## Risks

Device cloning is shallow and relies on `finish_copydevice` to reject unsafe copies. Output filename formatting uses `sprintf` after validation and size checks. Closing the old current device happens only when its reference count is 1, so errors can propagate but lifetime assumptions are subtle.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdevice.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdevice.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdevice.h

## Role

`gsdevice.h` is the public API for Ghostscript device and page control.

## Exposed Interfaces

Device-only operations include opening, closing, copying, querying known devices, copying scanlines, reading/writing parameters, getting device name, and initial matrix retrieval.

Image-device creation is exposed through:

- `gs_makeimagedevice`
- `gs_makewordimagedevice`
- `gs_initialize_wordimagedevice`

Graphics-state operations include page flush/copy/output, null device selection, setting devices with or without erase/init behavior, retrieving current device, and updating current-device parameters.

## Types

Forward-declares `gx_device`, `gx_device_memory`, `gs_matrix`, `gs_param_list`, `gs_imager_state`, and `gs_state`.

## Compatibility

Provides macros for `gs_getdeviceparams`, `gs_gethardwareparams`, and backward-compatible `gs_get_device_or_hardware_params`.

## Risks

One macro appears inconsistent: `gs_initialize_imagedevice` passes `color_size`, while the macro parameter is `colors_size`. If used as written, that macro depends on an external `color_size` symbol or fails to compile. Most call sites likely use `gs_initialize_wordimagedevice` directly.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdevice.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdevmem.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdevmem.c

## Role

`gsdevmem.c` creates and initializes Ghostscript memory/image devices from an initial matrix, dimensions, and palette/true-color descriptor.

## Main Functions

- `gs_initialize_wordimagedevice(...)` initializes caller-allocated `gx_device_memory`.
- `gs_makewordimagedevice(...)` allocates a memory device and delegates initialization.

`gs_makeimagedevice` is a macro in `gsdevice.h` over `gs_makewordimagedevice`.

## Behavior

The initializer maps `colors_size` to bit depth:

- palette sizes for 1/2/4/8-bit gray or RGB
- `-16`, `-24`, `-32` for true-color devices

For palette devices it validates that the palette includes black/white and, if colored, the RGB primaries. It picks word-oriented or byte-oriented memory-device prototypes by bit depth.

It validates the matrix is orthogonal, derives DPI from matrix scale, initializes device retention/refcount, sets the initial matrix, resolution, width/height, imaging bounding box, and bitmap memory. The bitmap itself is allocated on open.

## Dependencies

Uses matrix math, memory-device prototypes (`gxdevmem.h`), arithmetic helpers, error codes, and `gx_device_set_width_height`.

## Risks

Palette validation is strict and rejects palettes lacking required primaries. Non-orthogonal matrices return `undefinedresult`. For non-1-bit devices, palette allocation happens before `gs_make_mem_device`; later failures are minimal, but ownership must remain with the device.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdevmem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdfilt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdfilt.c

## Role

`gsdfilt.c` implements the device filter stack stored in `gs_state`. Device filters wrap the current device with forwarding/filtering devices and can later be popped to restore the previous target.

## Main Functions

- `gs_push_device_filter(...)`
- `gs_pop_device_filter(...)`
- `gs_clear_device_filters(...)`

It also defines GC descriptors for `gs_device_filter_stack_t` and `gs_device_filter_t`.

## Push Flow

`gs_push_device_filter` allocates a stack node, increments the current device reference, saves it as `next_device`, calls the filter’s `push` hook to create a new device, pushes the stack node, installs the new device with `gs_setdevice_no_init`, then drops the temporary new-device reference.

## Pop Flow

`gs_pop_device_filter` rejects empty stacks, removes the top stack node, calls the filter’s `prepop`, switches the graphics state back to the saved next device, decrements stack references, calls `postpop`, and drops the old top device reference.

`gs_clear_device_filters` repeatedly pops until empty.

## Dependencies

Uses graphics-state internals, device APIs, refcount macros, Ghostscript memory descriptors, and filter callback definitions from `gsdfilt.h`.

## Risks

If `df->push` fails after the current device reference is incremented, the code frees the stack node but does not visibly decrement `dfs->next_device`; this should be checked against allocator/finalizer conventions. Pop executes `postpop` after stack node release, so filter implementations must not rely on stack-node state then.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdfilt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdfilt.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdfilt.h

## Role

`gsdfilt.h` defines the public interface for Ghostscript device filter stacks.

## Model

A device filter is a device-chain wrapper. Each pushed filter creates a new first device in the chain and forwards to its target; the physical page device remains at the end. A shadow stack node in the graphics state tracks the filter object and next device.

## Types

Forward-declares:

- `gs_device_filter_stack_t`
- `gs_device_filter_t`

Defines `struct gs_device_filter_s` with three callbacks:

- `push(self, mem, pgs, pdev, target)`
- `prepop(self, mem, pgs, dev)`
- `postpop(self, mem, pgs, dev)`

## API

Declares push, pop, and clear functions. Documents ownership expectations: `mem` is used to allocate/free filter stack state, and return values are Ghostscript error codes.

## Dependencies

Assumes `gs_state`, `gx_device`, `gs_memory_t`, and structure descriptors are available through included upstream headers.

## Risks

The callbacks define a low-level lifecycle contract but do not encode ownership or reference-count semantics in types. Filter implementations must coordinate carefully with graphics-state device refcounts.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdfilt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdll.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdll.c

## Role

`gsdll.c` implements the deprecated OS/2/Windows Ghostscript DLL API as an adapter over the newer `gsapi` interface in `iapi.h`.

## Main Behavior

It keeps a single global `gs_main_instance *pgs_minst` and global callback `pgsdll_callback`.

Exported functions:

- `gsdll_init(...)` creates a `gsapi` instance, installs stdio and poll callbacks, stores the old callback pointer, and initializes with args.
- `gsdll_execute_begin`, `gsdll_execute_cont`, `gsdll_execute_end` wrap `gsapi_run_string_*`.
- `gsdll_exit` exits and deletes the instance.
- `gsdll_revision` returns product/copyright/revision metadata.

The old callbacks translate `GSDLL_STDIN`, `GSDLL_STDOUT`, and `GSDLL_POLL` events to the caller callback.

## Platform Hooks

Includes Windows or OS/2 headers conditionally. Contains a MacGSView compatibility hack exporting/storing `hwndtext`.

## Dependencies

Uses `iapi.h`, interpreter main-instance internals, Ghostscript revision globals, old `gsdll.h`, and platform DLL calling macros.

## Risks

The file labels the global single-instance state as a hack. It is not reentrant or multi-instance safe. `gsdll_old_stderr` sends `GSDLL_STDOUT` instead of a distinct stderr message, matching the old interface behavior here but surprising for callers expecting stderr separation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdll.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdll.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdll.h

## Role

`gsdll.h` declares the deprecated Ghostscript DLL API. It explicitly directs new clients to `API.htm` and `iapi.h`.

## API

Defines callback type `GSDLL_CALLBACK` and global `pgsdll_callback`, callback message constants for stdin/stdout/device/sync/page/resize/poll, and special `gsdll_init` return values.

Exports:

- `gsdll_revision`
- `gsdll_init`
- `gsdll_execute_begin`
- `gsdll_execute_cont`
- `gsdll_execute_end`
- `gsdll_exit`
- `gsdll_lock_device`

Also defines runtime dynamic-linking function pointer typedefs for each exported function.

## Platform Support

Includes `iapi.h`, sets `_Windows` from `__WINDOWS__`, handles IBM C `_System` calling convention, and has MacOS-specific `HWND`/QuickDraw export pragmas.

## Dependencies

Requires DLL export/calling macros from `iapi.h` and platform types such as `HWND`.

## Risks

The API is legacy and global-callback-oriented. `gsdll_lock_device` is declared here but not implemented in `gsdll.c`, so platform/device-specific implementations must provide it or link will fail when referenced.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdll.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdllos2.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdllos2.h

## Role

`gsdllos2.h` adds OS/2-specific declarations for the old Ghostscript DLL interface.

## API

Declares exported load-time function:

- `gsdll_get_bitmap(unsigned char *device, unsigned char **pbitmap)`

Defines runtime dynamic-linking typedef:

- `PFN_gsdll_get_bitmap`

## Dependencies

Relies on old DLL calling-convention macro `GSDLLAPI` being available before inclusion. It does not include `gsdll.h` directly.

## Integration Notes

This is a narrow platform extension used by OS/2 clients to retrieve a bitmap pointer from a named/device handle under the old DLL interface.

## Risks

The exported function declaration returns `unsigned long`, while the typedef returns `long`. On platforms where signedness/width differ in ABI-significant ways, this mismatch is worth checking.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdllos2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdllwin.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdllwin.h

## Role

`gsdllwin.h` adds Microsoft Windows-specific declarations for the old Ghostscript DLL interface.

## API

Declares exported functions:

- `gsdll_copy_dib`
- `gsdll_copy_palette`
- `gsdll_draw`
- `gsdll_get_bitmap_row`

Defines matching function pointer typedefs for runtime dynamic linking.

## Dependencies

Requires Windows types (`HGLOBAL`, `HPALETTE`, `HDC`, `LPRECT`, `LPBITMAPINFOHEADER`, `LPRGBQUAD`, `LPBYTE`) and DLL macros (`GSDLLEXPORT`, `GSDLLAPI`) to be defined by including Windows/old DLL headers first.

## Integration Notes

The API is focused on extracting/drawing bitmap device contents for old Windows GUI front ends.

## Risks

All functions take `unsigned char *device`, so type safety around device identity is weak. The header does not provide ownership rules for returned/copied DIBs or palettes; callers must rely on old DLL API documentation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdllwin.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdparam.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdparam.c

## Role

`gsdparam.c` implements default Ghostscript device parameter get/put behavior and helper routines for input/output media dictionaries.

## Get Path

`gs_get_device_or_hw_params` copies read-only prototypes when needed, fills missing device procs, and calls either hardware or normal get-params. `gx_default_get_params` writes standard page-device parameters, non-standard internal parameters, color information, alpha bits, lock-safety state, and optional `HWColorMap`.

Standard parameters include `OutputDevice`, `PageSize`/`.MediaSize`, `ProcessColorModel`, `HWResolution`, `ImagingBBox`, `Margins`, `NumCopies`, `SeparationColorNames`, `Separations`, and `UseCIEColor`.

## Media Helpers

Provides default input/output media structs and functions to begin/write/end `InputAttributes` and `OutputAttributes` dictionaries. Input media can emit page size, media color, media weight, and media type.

## Put Path

`gs_putdeviceparams` calls the device `put_params` proc and reports whether an open device was closed. `gx_default_put_params` validates resolution, size, media size, margins, imaging bbox, copy count, `UseCIEColor`, alpha bits, lock-safety changes, separation-related read-only values, and nominally read-only device/color parameters. It commits the parameter list even on validation errors to surface unknown parameters, then applies changes.

Changing resolution, `HWSize`, or media size closes the device if open and updates dependent geometry. It decaches colors after applying changes.

## Dependencies

Uses `gsparam.h`, `gxdevice.h`, fixed-coordinate limits, color-model helpers, and device geometry functions.

## Risks

Parameter interaction order is intentional: resolution, then size, then media size. Device clients that override parts of this must preserve that order. `.LockSafetyParams` cannot be lowered once set. `PageSize` is accepted as a backward-compatible synonym for `.MediaSize`, with `.MediaSize` taking precedence.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdparam.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdpnext.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdpnext.h

## Role

`gsdpnext.h` is a tiny NeXT Display PostScript compatibility header.

## Contents

It includes:

- `gsalpha.h`
- `gsalphac.h`

No new functions, structs, or macros are defined.

## Integration Notes

This header acts as an API aggregation point for NeXT DPS alpha-related facilities, preserving an include name expected by clients.

## Dependencies

Relies entirely on the included alpha headers.

## Risks

None local beyond include-order dependency. Consumers should include this only when the alpha APIs are desired.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdpnext.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdps.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdps.c

## Role

`gsdps.c` implements Display PostScript view-clipping operations for Ghostscript.

## Main Functions

- `gs_initviewclip` clears the current view clip path if active.
- `gs_viewclip` applies winding-number view clipping.
- `gs_eoviewclip` applies even-odd view clipping.
- `gs_viewclippath` installs the current view clip path as the current path, or fabricates the default clip box if no view clip is active.

## Control Flow

`common_viewclip` mirrors ordinary clipping logic: allocate `pgs->view_clip` if missing, compute the current path bbox, create a temporary rectangular clip path, clip that against the current path under the selected rule, assign it to `view_clip`, and clear the current path.

## Dependencies

Uses path, clip-path, device, and graphics-state internals: `gspath.h`, `gzpath.h`, `gzcpath.h`, `gzstate.h`.

## Risks

The implementation comment says this is almost copied from `common_clip` and should ideally be merged. Divergence from normal clipping behavior is possible if one path evolves without the other.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdps.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdps.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdps.h

## Role

`gsdps.h` is the client interface for Display PostScript facilities.

## Contents

It includes `gsiparm2.h` for device-source image parameter definitions and declares view-clipping APIs:

- `gs_initviewclip`
- `gs_eoviewclip`
- `gs_viewclip`
- `gs_viewclippath`

## Dependencies

Requires `gs_state` to be visible through normal Ghostscript client headers.

## Integration Notes

The header groups two DPS-related surfaces: device-source images through an include, and view clipping through declarations implemented in `gsdps.c`.

## Risks

No local implementation risk. Clients must link the corresponding DPS implementation objects when using view-clipping functions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdps.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdps1.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdps1.c

## Role

`gsdps1.c` implements Display PostScript graphics additions: explicit path bbox setting and rectangle append/clip/fill/stroke operations.

## Main Functions

- `gs_setbbox` transforms a user-space bbox to device fixed coordinates, applies rounding slack, unions it with any existing path bbox, and marks the path bbox as set.
- `gs_rectappend` appends one or more rectangles to the current path with counter-clockwise orientation.
- `gs_rectclip` temporarily replaces the current path with rectangles, clips, restores/free path state, and clears the path.
- `gs_rectfill` fills rectangles, with a fast path for orthogonal CTMs, rectangular clips, supported color types, loaded device color, no graphics antialiasing, and no effective overprint mode.
- `gs_rectstroke` appends rectangles, optionally concatenates a matrix, and strokes.

## Fast Path

`gs_rectfill` transforms rectangle corners to fixed coordinates and directly invokes high-level color rectangle fill or `gx_fill_rectangle` after clipping/intersection. It falls back to path construction plus `gs_fill` on transform/conversion/color failures.

## Dependencies

Uses matrix, path, clip path, fixed arithmetic, high-level device color, painting, and graphics-state APIs.

## Risks

The fast path has many preconditions; fallback preserves correctness but can be slower. `gs_setbbox` depends on fixed-coordinate limits and adds fixed epsilon slack to avoid rounding underestimation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdps1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdsrc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdsrc.c

## Role

`gsdsrc.c` implements Ghostscript data-source GC support and accessors for string/byte/float/stream-backed data sources.

## Main Behavior

Defines `st_data_source` GC descriptor. Enumeration/relocation treats data differently by type:

- string: const string pointer
- stream: stream pointer
- bytes/floats: raw byte data pointer

Accessors:

- `data_source_access_string`
- `data_source_access_bytes`
- `data_source_access_stream`

String and byte access are identical except for GC handling and do not bounds-check. They either return a direct pointer or copy into caller buffer.

Stream access first tries to satisfy the request from the current stream buffer if the requested range is already buffered. Otherwise it seeks and reads exactly the requested length, returning `rangecheck` on seek/read failure or short read.

## Dependencies

Uses `gsdsrc.h`, stream APIs, memory helpers, and Ghostscript errors.

## Risks

String/byte accessors explicitly do not bounds-check; callers must validate ranges. Stream access may change stream position via `sseek`/`sgets`, so callers sharing streams must account for side effects.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdsrc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdsrc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdsrc.h

## Role

`gsdsrc.h` defines `gs_data_source_t`, a uniform embedded source descriptor for data used by color maps, images, and similar constructs.

## Data Sources

Supported source types:

- string
- bytes
- floats
- stream

The structure stores an access procedure, source type, and either a `gs_const_string` or `stream *`.

## API

Defines access-procedure signature and helper macros:

- `data_source_access_only`
- `data_source_access`
- `data_source_copy_only`
- `data_source_copy`

Defines initialization macros for string, byte, float, and stream sources. Float arrays are represented as byte spans with `sizeof(float)` scaling.

Also declares `st_data_source` for GC tracing.

## Dependencies

Includes `gsstruct.h`, forward-declares `stream`, and expects Ghostscript string/byte/ulong types.

## Risks

The header states access procedures may or may not bounds-check. The `data_source_access` macro returns from the enclosing function on error, so it must only be used in functions returning Ghostscript integer status codes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdsrc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsequivc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsequivc.c

## Role

`gsequivc.c` computes equivalent CMYK process colors for spot/separation colorants by forcing Separation/DeviceN tint transforms through their alternate color spaces and capturing the resulting process color.

## Workflow

`update_spot_equivalent_cmyk_colors` checks the current graphics-state color space. For Separation or DeviceN spaces, it compares colorant names against device separation names that lack known equivalent CMYK values.

For a matching Separation it builds a temporary color with tint 1.0 and sets `use_alt_cspace`. For DeviceN it first rejects any component named `None`, then builds a zeroed client color with the matching component set to 1.0.

## Capture Mechanism

The file defines a temporary `color_capture_device` and replacement color-map procedures. The temp imager state uses `cmap_capture_cmyk_color`, and the temp device carries the separation index plus destination equivalent-color params.

Capture procs save CMYK directly, convert gray to K-only CMYK, or convert RGB to CMYK via `color_rgb_to_cmyk`. Separation/DeviceN capture procs should not execute because alternate color-space use is forced.

## Dependencies

Uses printer/deviceN structures, color conversion, color spaces, graphics state, and device params. Header contract is in `gsequivc.h`.

## Risks

The logic intentionally skips DeviceN spaces containing `None` because equivalent values would require color data not available at installation time. The final remap call ignores its return code, so failed tint transforms may leave equivalent color data unset without direct propagation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsequivc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsequivc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsequivc.h

## Role

`gsequivc.h` declares data structures and the public helper for collecting equivalent CMYK colors for spot colorants.

## Types

`cmyk_color` stores validity plus `frac` C/M/Y/K components.

`equivalent_cmyk_color_params` stores an all-valid flag and an array of per-separation `cmyk_color` entries sized to `GX_DEVICE_MAX_SEPARATIONS`.

## API

Declares:

- `update_spot_equivalent_cmyk_colors(gx_device *, const gs_state *, gs_devn_params *, equivalent_cmyk_color_params *)`

## Dependencies

Requires `bool`, `frac`, `GX_DEVICE_MAX_SEPARATIONS`, `gx_device`, `gs_state`, and `gs_devn_params` definitions from surrounding Ghostscript device/color headers.

## Integration Notes

Device implementations that need spot equivalent colors embed `equivalent_cmyk_color_params` in their device state and call the update helper when Separation/DeviceN color spaces are installed.

## Risks

The header exposes fixed-size storage tied to the maximum device separation count. Device code must initialize validity flags and keep the separation-name list synchronized with the equivalent-color array.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsequivc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gserror.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gserror.h

## Role

`gserror.h` defines Ghostscript error-return logging macros.

## API

Declares:

- `gs_log_error(int, const char *, int)`

In non-DEBUG builds, `gs_log_error(err, file, line)` is macro-reduced to just `err`.

Defines:

- `gs_note_error(err)` as `gs_log_error(err, __FILE__, __LINE__)`
- `return_error(err)` as `return gs_note_error(err)`

## Dependencies

Uses compiler `__FILE__` and `__LINE__`.

## Integration Notes

This header lets code annotate error returns with source location in DEBUG builds while keeping release builds cheap.

## Risks

`return_error` directly returns from the current function. It must only be used in functions whose return type and error-code convention match Ghostscript integer status codes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gserror.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gserrors.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gserrors.h

## Role

`gserrors.h` defines core Ghostscript library error code constants.

## Error Convention

Functions that may fail return non-negative values for success and negative values for errors. The file uses integer macros rather than an enum to avoid casting.

## Defined Errors

Includes common PostScript/Ghostscript errors such as:

- `gs_error_unknownerror`
- `gs_error_interrupt`
- `gs_error_invalidaccess`
- `gs_error_invalidfileaccess`
- `gs_error_invalidfont`
- `gs_error_ioerror`
- `gs_error_limitcheck`
- `gs_error_nocurrentpoint`
- `gs_error_rangecheck`
- `gs_error_typecheck`
- `gs_error_undefined`
- `gs_error_undefinedfilename`
- `gs_error_undefinedresult`
- `gs_error_VMerror`
- `gs_error_unregistered`

Also defines special internal/fatal values:

- `gs_error_hit_detected`
- `gs_error_Fatal`

## Dependencies

None beyond C preprocessing.

## Risks

Because these are macros, they have no type safety. Callers must preserve the convention that success is non-negative and errors are negative.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gserrors.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gserver.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gserver.c

## Role

`gserver.c` is a simple procedural server front end for the Ghostscript interpreter, replacing `gs.c` for embedding-style use.

## Public API

Defines:

- `gs_server_initialize`
- `gs_server_run_string`
- `gs_server_run_files`
- `gs_server_terminate`

The API initializes Ghostscript with caller-provided file descriptors, runs strings/files, returns exit/error codes, and can report the PostScript error object as a printable string.

## Initialization

`gs_server_initialize` converts file descriptors to C `FILE *`, calls `gs_init0`, `gs_init1`, and `gs_init2`, then runs `/QUIET true def /NOPAUSE true def` and optional caller initialization code.

## Job State

Non-permanent file runs are wrapped in `job_begin`/`job_end`. `job_begin` erases the current page, saves interpreter state via `zsave`, and stores the save object. `job_end` resets the interpreter, restores the saved object with `zrestore`, and returns to the baseline state.

## Error Reporting

`errstr_report` uses `obj_cvs` to convert the error object into caller storage, falling back to `[unprintable]`.

## Dependencies

Uses interpreter internals (`main.h`, `interp.h`, operand stack, refs, save/restore operators) and graphics erasepage.

## Risks

This is tightly coupled to interpreter globals such as `osp` and `igs`. File descriptor conversion failures leak earlier `FILE *` objects in some paths. The server API is simple but not designed for concurrent interpreter instances.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gserver.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsexit.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsexit.h

## Role

`gsexit.h` declares exit/abort hooks that Ghostscript clients must provide.

## API

- `gs_to_exit(const gs_memory_t *mem, int exit_status)`
- `gs_to_exit_with_code(const gs_memory_t *mem, int exit_status, int code)`
- `gs_abort(const gs_memory_t *mem)`

## Semantics

`gs_to_exit` normally performs cleanup and error messaging without directly calling system `exit`, returning control to the caller.

`gs_to_exit_with_code` is similar but lets clients return the PostScript error code.

`gs_abort` handles fatal errors; after cleanup it may call `gp_do_exit`, which exits in a platform-independent way. The comments state returning from abort is not advisable.

## Dependencies

Requires `gs_memory_t`.

## Risks

These hooks are client-supplied. Embedders must implement them consistently with their ownership and process-lifetime model, especially for fatal paths.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsexit.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfcid.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfcid.c

## Role

`gsfcid.c` provides support routines and GC descriptors for CID-keyed fonts.

## GC/Descriptors

Defines structure descriptors for `CIDSystemInfo`, CID font data, CIDFontType 0, CIDFontType 1, CIDFontType 2, and FDArray pointer arrays. The enum/reloc procedures delegate to base font or CID data descriptors and handle FDArray/proc pointers.

## CIDSystemInfo Helpers

- `cid_system_info_set_null` clears Registry, Ordering, and Supplement.
- `cid_system_info_is_null` tests the null representation.
- `gs_font_cid_system_info` returns CIDSystemInfo for CID font types and null for non-CID fonts.
- `gs_is_CIDSystemInfo_compatible` compares Registry and Ordering but ignores Supplement.

## Font Helpers

`gs_font_cid0_enumerate_glyph` iterates CIDs, asks the CID font for glyph data, skips missing/empty glyphs, and returns available glyphs. It frees glyph data before returning.

`gs_cid0_indexed_font` returns a subfont from FDArray and prints an error if called on a non-CIDFontType 0 font.

`gs_cid0_has_type2` scans FDArray for Type 2 encrypted subfonts.

## Dependencies

Uses font/CID internals from `gxfcid.h`, base font descriptors, memory, matrix, and error helpers.

## Risks

`gs_cid0_indexed_font` does not bounds-check `fidx`. Callers must validate FDArray indexes. Compatibility ignores Supplement, which is intentional for many CMap/font matching cases but not full structural equality.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfcid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfcid2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfcid2.c

## Role

`gsfcid2.c` creates CIDFontType 2 fonts from Type 42 fonts and wraps common TrueType cmap format 4 tables as Ghostscript CMaps.

## CIDFontType 2 Creation

`gs_font_cid2_from_type42` allocates `gs_font_cid2`, copies the Type 42 base, resets resource/list state, assigns a new id, sets `FontType` to CID TrueType, initializes null CIDSystemInfo, sets `CIDCount` from TrueType glyph count, and uses an identity CIDMap proc.

## TrueType CMap Wrapper

Defines `gs_cmap_tt_16bit_format4_t`, a subclass of `gs_cmap_t` referencing a Type 42 font and offsets into a Platform 3 / Encoding 1 / Format 4 cmap.

The decode proc reads two-byte character codes, linearly scans segments, applies `idDelta`/`idRangeOffset`, and returns CID glyphs. Enumeration procs expose one two-byte code range and lookup entries derived from TrueType segments.

`gs_cmap_from_type42_cmap` locates a suitable cmap subtable, allocates a Ghostscript CMap with dummy `none` CIDSystemInfo, and records segment-table offsets.

## Dependencies

Uses Type 42 font accessors, CMap internals, CID helpers, big-endian integer helpers, memory, and errors.

## Risks

The format 4 segment search is linear. The code targets only Platform 3 / Encoding 1 / Format 4; other Unicode cmap variants are rejected as invalid font for this wrapper.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfcid2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfcmap.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfcmap.c

## Role

`gsfcmap.c` implements generic CMap client operations, identity CMaps, CMap allocation/enumeration helpers, identity detection, and ToUnicode CMaps.

## Identity CMaps

`gs_cmap_identity_t` stores byte width, varying byte count, and return-code mode. Identity decode reads a big-endian code, returns CID glyph `gs_min_cid_glyph + value`, updates index/font index, and may return the code byte count for character identity maps.

Identity range/lookup enumeration exposes full byte ranges. Public constructors are:

- `gs_cmap_create_identity`
- `gs_cmap_create_char_identity`

Both currently require `num_bytes == 2`.

## Generic CMap API

Implements:

- `gs_cmap_is_identity`
- `gs_cmap_decode_next`
- range and lookup enumeration init/next helpers
- `gs_cmap_init`
- `gs_cmap_alloc`
- enum setup helpers
- `gs_cmap_compute_identity`

`gs_cmap_alloc` reserves IDs for subfont-related use, allocates CIDSystemInfo array, sets CMap metadata, WMode, and procedure vector.

## ToUnicode

Defines a compact `gs_cmap_ToUnicode_t` with a dense two-byte Unicode map. It supports allocation, pair insertion, range/lookup enumeration, and identity tracking. Decode is deliberately unsupported with `assert(0)` because this path is not used for decoding.

## Dependencies

Uses CMap internals (`gxfcmap.h`), CIDSystemInfo descriptors, memory, IDs, and errors.

## Risks

ToUnicode allocation leaks the CMap if subsequent map allocation fails. ToUnicode lookup enumeration hardcodes two-byte Unicode values. Identity constructors reject non-two-byte maps despite comments describing possible generalization.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfcmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfcmap.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfcmap.h

## Role

`gsfcmap.h` is the public interface to Ghostscript CMaps.

## API

Declares:

- `gs_cmap_create_identity`
- `gs_cmap_create_char_identity`
- `gs_cmap_decode_next`
- `gs_cmap_ToUnicode_alloc`
- `gs_cmap_ToUnicode_add_pair`

`gs_cmap_decode_next` decodes from a string, updates the index, returns 0 for CID/name mappings, positive byte count for character-code mappings, and sets `gs_no_glyph` for undefined characters.

## Types

Forward-declares abstract `gs_cmap_t`.

## Dependencies

Includes `gsccode.h` for character/glyph code types and expects `gs_memory_t`, `gs_const_string`, `gs_char`, and `gs_glyph`.

## Integration Notes

This is the stable client-level surface; detailed CMap representations and enumeration APIs live in internal headers such as `gxfcmap.h`.

## Risks

The public decode contract requires callers to handle both glyph output and positive return-code character mappings. Ignoring positive returns can misinterpret ToUnicode/character-map cases.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfcmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfcmap1.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfcmap1.c

## Role

`gsfcmap1.c` implements Adobe-style CMap decoding with code-space ranges, defined/notdef lookup tables, multidimensional range offsets, lookup enumeration, and allocation.

## Decode Logic

`code_map_decode_next_multidim_regime` scans lookup ranges in reverse order to honor `usecmap` override behavior. It handles key prefixes, partial matches, range keys, and value types:

- CID
- NOTDEF
- GLYPH
- CHARS

For CID ranges, it computes multidimensional offsets so the last byte changes fastest. For `CHARS`, it returns value size and computes character code offset from the range start.

`gs_cmap_adobe1_decode_next` first checks defined mappings. If none match, it checks notdef mappings. If neither matches, it uses partial-match fallback or consumes the shortest defined character length and maps to CID 0. Too-short undecodable input returns `rangecheck`.

The comments note codespace ranges are not currently enforced during decode.

## Enumeration/Allocation

Range enumeration walks `code_space.ranges`. Lookup enumeration supports defined and notdef maps separately. `gs_cmap_adobe1_alloc` allocates ranges, lookup structs, key/value buffers, base CMap state, initializes lookup ownership, and leaves caller to populate tables.

## Dependencies

Uses `gxfcmap1.h`, CMap allocation helpers from `gsfcmap.c`, memory, IDs, debugging helpers, and error codes.

## Risks

Lookup search is linear and can be expensive for large CMaps. Decode accepts mappings outside codespace ranges. Allocation error cleanup does not visibly free a successfully allocated base `pcmap` when later allocations fail, so ownership/error cleanup should be reviewed in context.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfcmap1.c -->