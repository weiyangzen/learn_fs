# Group Research: group_1560_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_gsht_c_sources_os_p_fda4b3737d4d

Scope: `Docs/research_subset_a.md` only. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsht.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsht.c

Implements core Ghostscript halftone state operations: `setscreen`, screen phase management, current halftone queries, halftone order allocation/construction/release, device halftone installation, colorant name resolution, and effective transfer selection.

Key responsibilities:
- Defines GC descriptors for `gx_ht_order`, `gs_halftone`, and `gx_device_halftone`.
- Allocates halftone orders via `gx_ht_alloc_ht_order`, `gx_ht_alloc_order`, `gx_ht_alloc_threshold_order`, and `gx_ht_alloc_client_order`.
- Sorts sampled spot/threshold values and converts whitening order entries into bit offset/mask records.
- Handles release of halftone orders, caches, WTS screens, transfer maps, and per-component device halftones.
- Installs device halftones into an imager state with `gx_imager_dev_ht_install`, including component expansion, default-component handling, ownership transfer, WTS conversion, cache creation, and LCM tile sizing.
- Installs high-level halftones into `gs_state` with `gx_ht_install`.

Important design notes:
- The file contains extensive comments explaining the mismatch between operand halftones and installed imager halftones.
- Ownership is mixed: some order data is moved from the operand into the installed halftone when memory matches; otherwise it is copied.
- Transfer maps are reference-counted; order data and caches generally are not.
- WTS sharing uses a hack: `width == 0xffff` suppresses duplicate release of shared WTS screens.
- `gx_imager_set_effective_xfer` starts from current transfer maps and then applies halftone dictionary overrides per component.

Risks and quirks:
- Complex ownership rules make error paths and shared structures fragile.
- `gs_color_name_component_number` treats `Default` as `GX_DEVICE_COLOR_MAX_COMPONENTS` and remaps RGB names to CMYK names for colorscreen-style halftones.
- The WTS duplicate-release suppression relies on a field that is normally unused for WTS orders.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsht.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsht.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsht.h

Public interface for basic Type 1 and color halftone functionality.

Defines:
- `gs_screen_halftone`: frequency, angle, spot function, actual frequency, and actual angle.
- `gs_colorscreen_halftone`: four screen definitions addressable by index or named red/green/blue/gray fields.
- `gs_setscreen`, `gs_currentscreen`, and `gs_currentscreenlevels`.
- `gs_screen_enum` opaque enumeration API for client-driven screen sampling.

The enumerator API lets callers allocate/init a screen, repeatedly ask for a sampling point, provide the spot-function value, and optionally install the completed screen.

This header is intentionally small and exposes only the public procedural layer; implementation and internal order details live in `gsht.c`, `gshtscr.c`, and internal headers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsht.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsht1.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsht1.c

Implements extended halftone operators: `setcolorscreen`, `currentcolorscreen`, `sethalftone`, allocated halftone installation, and preparation of multiple halftone types.

Supported halftone preparation paths:
- Type 2 colorscreen: samples gray/red/green/blue screens and maps names to device components.
- Spot halftones: delegates screen sampling to `gx_ht_process_screen_memory`.
- Threshold halftones: builds threshold orders from byte threshold arrays.
- Threshold2 halftones: supports two rectangles and 1- or 2-byte samples, reducing level count to a maximum of 14 bits.
- Client order halftones: delegates order creation to client callbacks.
- Multiple and multiple-colorscreen halftones: validates/defaults components and builds a component array.

Transfer handling:
- `process_transfer` builds a `gx_transfer_map` when a procedural or closure transfer is supplied.
- Transfer maps are initialized with `load_transfer_map` and attached to `gx_ht_order`.

WTS path:
- `gs_sethalftone_try_wts` opportunistically creates WTS-based device halftones for Type 5 multiple halftones.
- It only accepts accurate spot components and separable/linear or monochrome bilevel devices.
- The function creates WTS enumerators and records them in component orders for later conversion during install.

Risks and quirks:
- The WTS path has a comment noting missing cleanup on error.
- Multiple halftones require exactly one Default; duplicates or absence result in `rangecheck`.
- Threshold2 reduces precision when too many levels are present.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsht1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsht1.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsht1.h

Extended public halftone API.

Exports:
- `gs_setcolorscreen`
- `gs_currentcolorscreen`
- `gs_sethalftone`
- `gs_sethalftone_allocated`
- `gs_currenthalftone`

Documents ownership expectations:
- `gs_sethalftone` assumes the halftone and substructures use the same allocator as the `gs_state`.
- `gs_sethalftone_allocated` uses `rc.memory` from the halftone.
- Both copy the top-level structure but take ownership of substructures.

This header bridges Level 1-style screen APIs from `gsht.h` with Level 2 halftone dictionaries.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsht1.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gshtscr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gshtscr.c

Implements Type 1 screen halftone processing and screen enumeration.

Key functions:
- `gx_compute_cell_values`: derives halftone cell geometry, strip width/height, and shift values.
- `gs_setaccuratescreens`, `gs_currentaccuratescreens`: global AccurateScreens controls.
- `gs_setusewts`, `gs_currentusewts`: global WTS enable controls.
- `gs_setminscreenlevels`, `gs_currentminscreenlevels`: global minimum screen level controls.
- `gs_screen_order_init_memory`: computes cell size and allocates an order.
- `gs_screen_enum_init_memory`: prepares sampling transforms.
- `gs_screen_currentpoint`: returns next point for the spot function.
- `gs_screen_next`: records each sampled spot value.
- `gs_screen_install`: installs a completed sampled screen.

Cell selection:
- `pick_cell_size` maps requested frequency/angle through the device initial matrix, tries rounded integer cell vectors, evaluates frequency/angle error, enforces storage limits, and expands the repeat factor when needed.
- AccurateScreens continues searching beyond the first acceptable candidate.

Sampling behavior:
- Non-WTS screens sample a strip or full tile, then `gx_ht_construct_spot_order` finalizes the order.
- WTS screens delegate point and value enumeration to WTS routines.

Risks and quirks:
- AccurateScreens, WTS usage, and MinScreenLevels are global statics and explicitly noted as reentrancy problems.
- `FORCE_STRIP_HALFTONES` is a compile-time debug control.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gshtscr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gshtx.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gshtx.c

Provides a stand-alone high-level halftone/transfer object interface layered over Ghostscript’s regular halftone structures.

Main API implementation:
- `gs_ht_build`: allocates a multiple halftone and component array.
- `gs_ht_set_spot_comp`: defines a spot-function component.
- `gs_ht_set_threshold_comp`: defines a threshold-array component.
- `gs_ht_set_mask_comp`: defines a mask-sequence component using client-order callbacks.
- `gs_ht_reference`, `gs_ht_release`: reference-count wrapper operations.
- `gs_ht_install`: validates, builds component orders, allocates caches, and installs via `gx_ht_install`.

Transfer behavior:
- Missing transfer callbacks are replaced by `null_closure_transfer`.
- `build_transfer_map` samples transfer functions into `gx_transfer_map` entries.

Mask-order support:
- `create_mask_bits` compares consecutive masks and emits order bits where the mask changes.
- `create_mask_order` translates explicit masks into the order/levels representation expected by the halftone renderer.

Risks and quirks:
- `comp2order` is fixed at 32 bytes and assumes component counts fit.
- The stand-alone builder only validates spot and threshold components in `check_ht`, despite `gs_ht_set_mask_comp` producing client-order components; this mismatch is notable.
- Client data ownership remains with the caller.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gshtx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gshtx.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gshtx.h

Public high-level interface for stand-alone halftone/transfer objects.

Provides aliases:
- `gs_ht` to `gs_halftone`
- component, spot, threshold, and multiple halftone aliases
- GC descriptor and member-name aliases

Exports:
- `gs_ht_build`
- `gs_ht_set_spot_comp`
- `gs_ht_set_threshold_comp`
- `gs_ht_set_mask_comp`
- `gs_ht_reference`
- `gs_ht_release`
- `gs_ht_install`
- assignment/reference macros

Documents the two-step construction model: create the overall halftone, then fill each component. It also states that client-provided threshold or mask data is not released by the halftone object.

This header is a convenience API over lower-level `gs_halftone` machinery.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gshtx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsicc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsicc.c

Implements ICCBased color space support.

Major responsibilities:
- Defines `icmFileGs`, an adapter from Ghostscript `stream` to the external `icclib` file interface.
- Provides GC/finalization logic for `gs_cie_icc`, including cleanup of foreign-memory ICC profile, lookup, and file objects.
- Defines the `CIEICC` color space type and methods: component count, alternate space, initial color, range restriction, concrete space selection, concretization, refcount adjustment, install, and serialization.
- Loads ICC profiles with `gx_load_icc_profile`.

Profile loading:
- Verifies stream identity with `file_id`.
- Creates `new_icc`, wraps the stream, reads the profile, validates profile class, PCS, and source color space/component count.
- Obtains an icclib lookup object using default intent.
- Stores profile illuminant as WhitePoint and records whether PCS is Lab.

Color conversion:
- If no profile is loaded, delegates to the alternate color space.
- Otherwise restricts input, handles Lab input scaling, performs ICC lookup, converts PCS Lab to XYZ when needed, and feeds CIE remapping.

Risks and quirks:
- ICC profile objects are allocated in foreign memory and cleaned in a finalizer.
- The stream pointer must be refreshed lazily before lookup because streams can relocate.
- Serialization reads the whole ICC stream into the output; some failures are marked `unregistered` as unimplemented.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsicc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsicc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsicc.h

Declares ICCBased color space structures and public constructors/helpers.

Defines:
- Opaque declarations for icclib types.
- `gs_cie_icc_s`, containing CIE common elements, component count/ranges, source stream identity, Lab/XYZ PCS flag, ICC profile pointer, lookup pointer, and icclib file wrapper pointer.
- `private_st_cie_icc` descriptor macro with finalization.
- `gs_cspace_build_CIEICC`
- `gx_load_icc_profile`
- `gx_increment_cspace_count`

The header explains why ICC profile and lookup objects live outside GC-managed memory and why stream identity must be validated. It also documents a known API bug: constructed CIE spaces start with reference count 1, so clients may need to decrement after installing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsicc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsimage.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsimage.c

Implements the buffered public image enumeration layer over device image-processing callbacks.

Core model:
- `gs_image_enum` tracks memory, device, underlying image enum info, plane count, height, wanted-plane cache, retained source data, row buffers, and prepared `gx_image_plane_t` entries.
- Each plane may have a partial row buffer and/or retained source data.

Key functions:
- `gs_image_begin_typed`: obtains clip path, loads color if needed, and starts a device typed image.
- `gs_image_enum_alloc`: allocates and initializes an enumerator.
- `gs_image_init`: starts ImageType 1 images and masks, handling cachedevice and default DeviceGray cases.
- `gs_image_enum_init`: initializes from an existing lower-level image enum.
- `gs_image_planes_wanted`: reports which planes still need client data.
- `gs_image_next`: older single-plane-cycling interface.
- `gs_image_next_planes`: main multi-plane buffered data feeding routine.
- `gs_image_cleanup` and `gs_image_cleanup_and_free_enum`.

Buffering behavior:
- Partial rows are copied into stable-memory row buffers.
- Whole rows can be passed directly from caller source data.
- Retained data pointers are returned to the caller so stream-buffer clients can manage moving data.
- If wanted planes can vary, data transfer is limited to one row at a time.

Risks and quirks:
- There is an explicit note that charpath skipping is not correct for ImageType 3 InterleaveType 2.
- `gs_image_init` uses a static DeviceGray color space for parameterless images.
- Row buffers use stable memory because PostScript code may use save/restore during image data procedures.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsimage.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsimage.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsimage.h

Public generic image rendering interface.

Documents the buffering contract between clients and the underlying device image processor:
- Client data may be incomplete, unaligned, multi-plane, or selectively supplied.
- `gs_image_next_planes` consumes bytes and may retain source data by reference.
- `gs_image_planes_wanted` reports only planes that the lower layer wants and that lack a full buffered row.

Exports:
- `gs_image_begin_typed`
- `gs_image_enum_alloc`
- `gs_image_init`
- `gs_image_enum_init`
- `gs_image_bytes_per_plane_row`
- `gs_image_planes_wanted`
- `gs_image_next_planes`
- `gs_image_next`
- cleanup routines

The header also warns that `gs_image_next` is only suitable for simpler cases where all planes are always wanted and have compatible dimensions/depths.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsimage.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsimpath.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsimpath.c

Converts a 1-bit image mask into an outline path.

Main entry:
- `gs_imagepath(gs_state *pgs, int width, int height, const byte *data)`

Algorithm:
- Scans pixels from bottom-right toward top-left.
- Detects starting boundary pixels.
- Uses `trace_from` to walk the outline clockwise.
- Emits `moveto`, `rlineto`, and `closepath` operations into the current path.
- Uses a small `outline_scale` and `step` to avoid corner backtracking and produce cleaner outlines.

Helpers:
- `get_pixel`: returns a bit from packed image data, treating out-of-bounds as empty.
- `trace_from`: follows the boundary, optionally in detect-only mode to avoid retracing.
- `add_dxdy`: coalesces repeated relative segments before appending to the path.

This is compact raster-to-vector boundary tracing for imagemask-like data.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsimpath.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsinit.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsinit.c

Library initialization and finalization for the Ghostscript imager.

Functions:
- `gs_lib_init`: combines memory initialization and configured subsystem initialization.
- `gs_lib_init0`: creates the malloc-backed memory manager, resets debug flags, and clears error logging.
- `gs_lib_init1`: walks `gx_init_table` and invokes each configured init procedure.
- `gs_lib_finit`: calls platform cleanup via `gp_exit`.

Notable issue:
- `gs_lib_finit` comments that memory ownership is ambiguous: if `gs_lib_init0` allocated the memory, it should be released, but some API paths supply externally owned memory.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsinit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsio.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsio.h

Header that forbids direct use of standard input/output/error and selected stdio convenience functions.

Behavior:
- Undefines and redefines `stdin`, `stdout`, and `stderr` to unavailable symbols.
- Redefines functions like `getchar`, `printf`, `puts`, `scanf`, and related calls to unavailable expressions.

Purpose:
- Forces the library and interpreter to route I/O through Ghostscript’s redirected IODevice/stream mechanisms instead of process-global stdio.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsiodev.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsiodev.c

Implements Ghostscript IODevice dispatch and the `%os%` filesystem device.

Startup:
- Imports configured IODevice table.
- `gs_iodev_init` allocates writable GC-tracked copies of every configured IODevice and runs each device init procedure.
- Registers `io_device_table` as a structure root.

Default procedures:
- Provides `iodev_no_*` implementations returning invalid access, undefined filename, IO error, or no-op parameter behavior.

`%os%` device:
- Uses `gp_fopen`, `fclose`, `unlink`, `rename`, `stat`, and platform enumeration wrappers.
- `os_get_params` returns generic filesystem parameters with fake block/free/logical-size values.

Utilities:
- `gs_getiodevice`
- `gs_findiodevice`
- `gs_getdevparams`
- `gs_putdevparams`
- `gs_fopen_errno_to_code`

Risks and quirks:
- Failure cleanup in `gs_iodev_init` has suspicious indexing (`table[i - 1]`) and a comment that unregistering the root is unresolved.
- Capacity reporting is intentionally fake and platform-independent.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsiodev.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsiodevs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsiodevs.c

Implements `%stdin%`, `%stdout%`, and `%stderr%` IODevices for non-PostScript configurations.

Key behavior:
- Defines special IODevice descriptors using `iodev_stdio`.
- `stdio_open` validates access mode, allocates a stream and 128-byte buffer, and binds it to `mem->gs_lib_ctx` stdio handles.
- `stdio_close_file` does not close the underlying stdio file; it only releases the stream buffer.

Devices:
- `%stdin%`: read-only stream from `fstdin`.
- `%stdout%`: write-only stream to `fstdout`.
- `%stderr%`: write-only stream to `fstderr`.

This file keeps standard streams within Ghostscript’s stream abstraction.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsiodevs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsiodisk.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsiodisk.c

Implements `%disk0%` through `%disk6%` IODevices using flat OS directories plus a logical filename map.

Design:
- Each disk has a `/Root` parameter pointing at an OS directory.
- Logical filenames are mapped to numeric flat files through `map.txt`.
- This avoids OS filename/path restrictions and simulates Adobe’s flat disk structure.
- The number of disks is limited to seven due to DynaLab installer compatibility.

IODevice operations:
- `iodev_diskn_fopen`: maps logical name to real numeric file; creates a map entry on write.
- `diskn_delete`: removes map entry and unlinks real file.
- `diskn_rename`: removes destination if present and rewrites map name.
- `diskn_status`: maps logical name and stats real file.
- `diskn_get_params`/`diskn_put_params`: expose and update `Root`, mount/search/write flags, and fake capacity values.
- Enumeration delegates to map-file enumeration once Root is set.

Map file format:
- First line: `FileVersion\t1\t...`
- Remaining lines: numeric file id plus logical filename.
- `Tmp.txt` is used as a rewrite target for add/delete/rename operations.

Map helpers:
- `MapFileOpen`, read/write version, read/write entry, unlink/rename helpers.
- `MapToFile`
- `map_file_enum_init`, `map_file_enum_next`, `map_file_enum_close`
- `map_file_name_get`, add, delete, rename

Risks and quirks:
- Map rewrites are not atomic beyond rename patterns and have no locking.
- Several operations silently return if helper file operations fail.
- Root buffer allocation always uses `gp_file_name_sizeof`, while `root_size` is set to actual string size plus one.
- Logical names cannot include NUL, CR, or LF.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsiodisk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsiomacres.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsiomacres.c

Implements `%macresource%`, an IODevice for loading MacOS font resources from resource forks or `.dfont` data forks.

Resource parsing:
- Defines resource header, resource entry, and resource list structures.
- Reads big-endian 32-, 24-, 16-, and 8-bit values.
- Parses resource map type lists, reference lists, names, flags, offsets, and lengths.
- Loads requested resource data into memory.

IODevice behavior:
- Expects names of the form `path#type+id`.
- Parses the four-character resource type and numeric id.
- First tries `gp_read_macresource` for the resource fork.
- If that fails, tries `read_datafork_resource` for serialized data-fork resources.
- Allocates a Ghostscript string buffer and exposes it through a read stream.

Risks and quirks:
- Uses raw `malloc`/`free` for parser data, not Ghostscript memory.
- Several allocation and read-error paths leak intermediate parser allocations.
- `read_int8` stores `fgetc` into a byte and checks `< 0`, which is fragile for EOF.
- Only open-file is implemented; delete, rename, status, and enumeration are unsupported.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsiomacres.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsiorom.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsiorom.c

Stub implementation of `%rom%`, intended as a compressed in-memory filesystem IODevice for embedded Ghostscript builds.

Structure:
- Defines `%rom%` as a filesystem IODevice with open-file support only.
- Allocates a small `romfs_state` during init, but does not attach it to `iodev->state`.
- `iodev_rom_open_file` ignores the requested filename and returns a stream over the fixed string `this came from the compressed romfs.`

Current state:
- The file documents intended ROM/static-data filesystem support but does not implement lookup, compression, file tables, status, or enumeration.
- It is best read as scaffold/prototype code rather than production ROM filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsiorom.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsipar3x.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsipar3x.h

Defines ImageType 3x, Ghostscript’s transparency-capable extension of ImageType 3.

Key definitions:
- `IMAGE3X_IMAGETYPE` is `103`.
- `gs_image3x_mask_t`: interleave type, optional Matte color, and mask dictionary.
- `gs_image3x_t`: pixel data dictionary plus opacity and shape masks.

Semantics:
- Supports `OpacityMaskDict` and/or `ShapeMaskDict`, with mask depths greater than one.
- `InterleaveType 3` supplies mask sources before pixel data, opacity before shape.
- `InterleaveType 2` is not allowed for this extension.
- MaskDict color spaces are ignored.
- `BitsPerComponent == 0` means a mask is not supplied.

Exports `gs_image3x_t_init`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsipar3x.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsiparam.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsiparam.h

Central public image parameter definitions.

Defines:
- `gs_image_common_t`: type pointer and `ImageMatrix`.
- Maximum image color components and planes.
- `gs_data_image_t`: width, height, bits per component, decode array, interpolate flag.
- `gs_image_format_t`: chunky, component planar, and bit planar formats.
- `gs_pixel_image_t`: data image plus format, color space, and `CombineWithColor`.
- `gs_image_alpha_t`: alpha placement options.
- `gs_image1_t` / `gs_image_t`: ImageType 1 image or image mask with `ImageMask`, `adjust`, and `Alpha`.

Exports initialization helpers:
- `gs_image_common_t_init`
- `gs_data_image_t_init`
- `gs_pixel_image_t_init`
- `gs_image_t_init_adjust`
- `gs_image_t_init_mask_adjust`
- convenience macros for default adjust behavior

Important notes:
- `gs_image_t` predates other ImageTypes, so generic image handling uses `gs_image_common_t` plus per-type structs instead of changing the old type.
- Clients must initialize image structures with helper routines because structures may grow.
- The trailing service section is disabled with `#if 0` and marked under construction.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsiparam.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsiparm2.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsiparm2.h

Defines ImageType 2 parameters from the Adobe PostScript Version 3010 Supplement.

`gs_image2_t` contains:
- Common image fields.
- `gs_state *DataSource`
- `XOrigin`, `YOrigin`
- `Width`, `Height`
- optional `gx_path *UnpaintedPath`
- `PixelCopy`

Provides `private_st_gs_image2` descriptor macro and declares `gs_image2_t_init`.

Defaults documented:
- `UnpaintedPath = 0`
- `PixelCopy = false`
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsiparm2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsiparm3.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsiparm3.h

Defines ImageType 3 image parameters.

Key definitions:
- `gs_image3_interleave_type_t` with chunky, interleaved scan-line, and separate-source modes.
- `gs_image3_t`: pixel data dictionary, `InterleaveType`, and `MaskDict`.

Behavior notes:
- For `InterleaveType 3`, mask data source precedes pixel data sources.
- For interleave types 2 and 3, clients must provide mask data before the pixel data it masks; this is documented as not currently checked.

Exports descriptor macro and `gs_image3_t_init`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsiparm3.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsiparm4.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsiparm4.h

Defines ImageType 4 image parameters.

`gs_image4_t` extends pixel image common data with:
- `MaskColor_is_range`
- `MaskColor[GS_IMAGE_MAX_COMPONENTS * 2]`

Semantics:
- If `MaskColor_is_range` is false, the first N entries are exact sample values.
- If true, the first 2*N entries are ranges.
- Current library support is noted as up to 12-bit samples, with eventual DevicePixel support for wider samples.

Exports descriptor macro and `gs_image4_t_init`.

Default documented:
- `MaskColor_is_range = false`
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsiparm4.h -->