# Group Research: group_122_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_gsht_c_sources_os__0d0936baea41

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. Every listed source file was read completely. This group is Ghostscript halftone, image, ICC color, initialization, and IODevice infrastructure imported into the 9front tree; it is mostly graphics/runtime support, with filesystem-adjacent behavior in the Ghostscript IODevice files rather than Plan 9 kernel filesystem code.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsht.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsht.c

## Role

`gsht.c` implements the core Ghostscript halftone and screen-installation machinery: `setscreen`, current screen queries, screen phase state, halftone-order allocation/construction/release, device-halftone installation, colorant-name resolution, and effective transfer-map selection.

This is rendering halftone infrastructure, not filesystem code.

## Main Interfaces

- Public/externally used entry points: `gs_setscreen`, `gs_currentscreen`, `gs_currentscreenlevels`, `gx_imager_setscreenphase`, `gs_setscreenphase`, `gs_currentscreenphase_pis`, `gs_currentscreenphase`, `gs_currenthalftone`, `gx_ht_process_screen_memory`, `gx_ht_alloc_ht_order`, `gx_ht_alloc_order`, `gx_ht_alloc_threshold_order`, `gx_ht_alloc_client_order`, `gx_sort_ht_order`, `gx_ht_construct_spot_order`, `gx_ht_construct_bit`, `gx_ht_construct_bits`, `gx_ht_order_release`, `gx_device_halftone_release`, `gs_color_name_component_number`, `gs_cname_to_colorant_number`, `gx_imager_dev_ht_install`, `gx_ht_install`, `gx_imager_set_effective_xfer`, and `gx_set_effective_transfer`.
- Registers GC descriptors for `gx_ht_order`, `gs_halftone`, and `gx_device_halftone` and handles conditional pointer enumeration for threshold strings, client data, transfer closures, component arrays, cached tiles, and transfer maps.

## Core Behavior

- `gs_setscreen` samples a `gs_screen_halftone` through a `gs_screen_enum`, then installs it as a device halftone.
- Halftone orders own width/height/raster/shift geometry, levels arrays, bit-order arrays, optional tile caches, optional WTS screens, and optional transfer maps.
- Spot-function orders are sorted by sampled mask values, then expanded into bitmap offsets/masks through `gx_ht_construct_spot_order` and `gx_ht_construct_bits`.
- Threshold/client orders use caller-specified dimensions and threshold data but reuse the same low-level order/cache representation.
- `gx_imager_dev_ht_install` is the central ownership-transfer path. It maps operand halftone components onto device process components, fills missing components from the default order, creates tile caches for non-WTS orders, builds WTS screens from enumerators, computes LCM tile dimensions, and replaces or unshares the imager state's `dev_ht`.
- Colorant resolution treats `Default` specially and maps RGB-style color screen names to CMYK-style device colorants where appropriate.
- Effective transfer maps are reset from `set_transfer` gray/RGB maps and then overridden per halftone component if a component order supplies a transfer map.

## Notable Risks

- Ownership rules are intentionally complex: the installer sometimes moves operand substructures, sometimes copies them, and clears source references only after a successful install. Incorrect caller cleanup would leak or double-free levels, bit data, caches, WTS structures, or transfer maps.
- A sentinel value in the `width` field (`ht_wts_suppress_release`) suppresses duplicate release of shared WTS screens; this is fragile and explicitly documented as a hack.
- Error cleanup in `gx_imager_dev_ht_install` appears suspicious: it releases orders only when `comp_number == -1`, which is the opposite of the usual “initialized component” check and deserves caution if this legacy path is modified.
- `gs_currentscreenlevels` assumes `pgs->dev_ht` and component entries are valid after consulting the current device's gray index.
- LCM width/height calculations saturate at `max_int`; callers should not rely on exact repeat dimensions for very large component cells.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsht.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsht.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsht.h

## Role

`gsht.h` is the public Ghostscript Type 1 and color screen halftone interface.

This is graphics API infrastructure, not filesystem code.

## Main Declarations

- `gs_screen_halftone`: frequency, angle, spot function, and actual selected frequency/angle.
- `gs_colorscreen_halftone`: four screen definitions addressable as indexed entries or red/green/blue/gray fields.
- Procedural API: `gs_setscreen`, `gs_currentscreen`, `gs_currentscreenlevels`.
- Screen enumeration API: `gs_screen_enum_alloc`, `gs_screen_init`, `gs_screen_currentpoint`, `gs_screen_next`, and `gs_screen_install`.

## Important Contract

The enumeration API requires clients to initialize an enumerator, repeatedly request the current sample point and supply the spot function result, then optionally install the sampled screen. The comments explicitly describe this as an enumeration-style definition of a single screen.

## Notable Risks

The header exposes callback-driven spot functions and incremental enumeration; callers must keep the `gs_state`, allocator, and screen structure valid for the full sampling/install sequence.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsht.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsht1.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsht1.c

## Role

`gsht1.c` implements extended Ghostscript halftone operators: `setcolorscreen`, `sethalftone`, Level 2/Type 5 multiple halftones, threshold halftones, client-order halftones, transfer override construction, and a WTS fast path.

This is rendering halftone infrastructure, not filesystem code.

## Main Interfaces

- Public API: `gs_setcolorscreen`, `gs_currentcolorscreen`, `gs_sethalftone`, `gs_sethalftone_allocated`, `gs_sethalftone_prepare`, `gx_ht_complete_threshold_order`, `gx_ht_construct_threshold_order`.
- Internal processors: `process_transfer`, `process_spot`, `process_threshold`, `process_threshold2`, `process_client_order`, `gs_sethalftone_try_wts`.
- Defines GC pointer handling for `gs_halftone_component` values.

## Core Behavior

- `gs_setcolorscreen` wraps a `gs_colorscreen_halftone` as a `ht_type_colorscreen` and delegates to `gs_sethalftone`.
- `gs_sethalftone_prepare` converts high-level halftone definitions into a transient `gx_device_halftone` with a default order plus optional component orders.
- Spot components are sampled through `gx_ht_process_screen_memory`; threshold components allocate threshold orders and sort threshold values into level boundaries; client orders delegate construction to client procs.
- Extended threshold2 halftones can combine two rectangles, compute a strip geometry from their heights, reduce 16-bit thresholds to a bounded level count, and build a single threshold order.
- Multiple halftones require exactly one `Default` component and can include spot, threshold, threshold2, or client-order components.
- Transfer overrides allocate a reference-counted `gx_transfer_map`, load it with `load_transfer_map`, and attach it to the order.
- `gs_sethalftone_try_wts` attempts a well-tempered screen path only for Type 5 multiple spot halftones, accurate screens, and compatible bilevel/separable devices.

## Notable Risks

- The WTS path contains a `todo: cleanup on error`; partial allocations and transfer maps can leak if setup fails mid-loop.
- `gs_sethalftone_prepare` frees only the component array on some errors; any per-component order substructures created before the error rely on later callers or code paths for cleanup.
- Threshold2 intentionally drops low-order threshold bits when the level count would exceed `MAX_HT_LEVELS`, which can lose information.
- Multiple halftone validation depends on a single `Default` component and positional assumptions around the component array.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsht1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsht1.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsht1.h

## Role

`gsht1.h` extends the public halftone API with color screens and general `gs_halftone` installation/query routines.

This is graphics API infrastructure, not filesystem code.

## Main Declarations

- `gs_setcolorscreen`, `gs_currentcolorscreen`.
- Opaque `gs_halftone` forward declaration.
- `gs_sethalftone`, `gs_sethalftone_allocated`, `gs_currenthalftone`.

## Important Contract

`gs_sethalftone` assumes the halftone and all substructures were allocated with the same allocator as the graphics state. `gs_sethalftone_allocated` reads the allocator from the halftone's `rc.memory`. Both copy the top-level structure but take ownership of substructures.

## Notable Risks

The ownership contract is easy to misuse: callers must not free substructures after successful installation, but may need to clean up remaining referenced data after failure depending on the lower-level install path.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsht1.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gshtscr.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gshtscr.c

## Role

`gshtscr.c` implements Type 1 screen halftone sampling: choosing halftone cell geometry from requested frequency/angle and device matrix, allocating screen orders, enumerating sample points, accepting spot-function sample values, and installing completed screen orders.

This is graphics halftone infrastructure, not filesystem code.

## Main Interfaces

- Global controls: `gs_setaccuratescreens`, `gs_currentaccuratescreens`, `gs_setusewts`, `gs_currentusewts`, `gs_setminscreenlevels`, `gs_currentminscreenlevels`, `gs_gshtscr_init`.
- Cell/order setup: `gx_compute_cell_values`, `gs_screen_enum_alloc`, `gs_screen_init`, `gs_screen_init_memory`, `gs_screen_order_alloc`, `gs_screen_order_init_memory`, `gs_screen_enum_init_memory`.
- Enumeration/install: `gs_screen_currentpoint`, `gs_screen_next`, `gs_screen_install`.

## Core Behavior

- `pick_cell_size` searches integer cell vectors that approximate requested screen frequency/angle under device matrix scaling, tile-size limits, minimum level constraints, and accurate-screen preferences.
- `gx_compute_cell_values` derives super-cell dimensions, GCD values, and strip shifts from the selected cell parameters.
- `gs_screen_order_alloc` chooses either a full-tile allocation while sampling only a strip, or a strip-only allocation, based on cache memory limits.
- `gs_screen_currentpoint` maps device cell coordinates into spot-function coordinates, nudging sample positions to reduce equal spot values and handling WTS enumerators specially.
- `gs_screen_next` validates spot output in `[-1, 1]`, converts it to an internal sample value, records it in the order, and advances enumeration.

## Notable Risks

- `AccurateScreens`, `UseWTS`, and `MinScreenLevels` are file-static globals; comments explicitly state this harms reentrancy.
- The cell search is heuristic and can return `rangecheck` for small/degenerate frequencies or impossible tile constraints.
- `gs_screen_next` has a `long long` conversion and legacy commented alternative; behavior depends on the internal `ht_sample_t` range.
- WTS enumeration defers sorting until `gs_screen_currentpoint` returns completion.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gshtscr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gshtx.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gshtx.c

## Role

`gshtx.c` implements a stand-alone high-level halftone object API for building, referencing, releasing, and installing multi-component halftones with spot, threshold, or explicit mask components.

This is rendering support, not filesystem code.

## Main Interfaces

- Constructors/component setters: `gs_ht_build`, `gs_ht_set_spot_comp`, `gs_ht_set_threshold_comp`, `gs_ht_set_mask_comp`.
- Lifetime: `gs_ht_reference`, `gs_ht_release`.
- Installer: `gs_ht_install`.
- Internal helpers: `check_ht`, `build_transfer_map`, `alloc_ht_order`, `build_component`, `free_order_array`, `create_mask_bits`, `create_mask_order`.

## Core Behavior

- `gs_ht_build` allocates a reference-counted Type 5/multiple halftone plus component array and installs a custom free procedure that frees the component array.
- Component setters fill unused slots with spot or threshold definitions and always provide a transfer closure, using identity transfer when none is supplied.
- `gs_ht_install` validates the object, allocates component orders and transfer maps, builds each order, creates small caches for non-default components, then delegates to `gx_ht_install`.
- Transfer maps are precomputed across `transfer_map_size` samples and clamp output to the `[0, 1]` frac range.
- Mask-defined halftones compare successive bitmap masks to generate whitening-order bits and level offsets.

## Notable Risks

- `comp2order` is a fixed 32-byte stack array with a comment saying it is ample; there is no visible check that `num_comps <= 32`.
- `gs_ht_release` uses `rc_decrement_only`; the actual free path relies on reference-count conventions and `free_comps`.
- Threshold and mask data are caller-owned by contract, so callers must keep them valid until installation consumes/builds the order.
- The mask-order path is intentionally described as “silly” and uses a slow two-pass diff of adjacent masks.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gshtx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gshtx.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gshtx.h

## Role

`gshtx.h` declares the stand-alone halftone/transfer object API implemented by `gshtx.c`.

This is graphics API infrastructure, not filesystem code.

## Main Declarations

- Aliases `gs_ht`, `gs_spot_ht`, `gs_threshold_ht`, `gs_ht_component`, and `gs_multiple_ht` onto existing Ghostscript halftone structs.
- `gs_ht_transfer_proc` as a closure-capable transfer callback.
- `gs_ht_build`, `gs_ht_set_spot_comp`, `gs_ht_set_threshold_comp`, `gs_ht_set_mask_comp`, `gs_ht_reference`, `gs_ht_release`, `gs_ht_install`.
- Assignment/reference macros `gs_ht_assign` and `gs_ht_init_ptr`.

## Important Contract

Construction is two-step: allocate the multi-component halftone, then initialize each component. Releasing a halftone does not release client data supplied to transfer callbacks or mask/threshold definitions.

## Notable Risks

The object is nominally opaque but implemented as aliases over concrete Ghostscript halftone structs, so ABI and ownership behavior follow the underlying halftone internals.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gshtx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsicc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsicc.c

## Role

`gsicc.c` implements Ghostscript ICCBased color spaces: color-space descriptors, color restriction/concretization, ICC profile loading through icclib, Ghostscript-stream wrapping for icclib I/O, reference-count adjustment, finalization of foreign ICC memory, construction, installation, and serialization.

This is color-management infrastructure, not filesystem code.

## Main Interfaces

- Public/external functions: `gx_load_icc_profile`, `gs_cspace_build_CIEICC`, `gx_increment_cspace_count`.
- Color-space methods: `gx_num_components_CIEICC`, `gx_alt_space_CIEICC`, `gx_init_CIEICC`, `gx_restrict_CIEICC`, `gx_concrete_space_CIEICC`, `gx_concretize_CIEICC`, `gx_adjust_cspace_CIEICC`, `gx_install_CIEICC`, `gx_serialize_CIEICC`.
- icclib bridge: `gx_wrap_icc_stream`, `icmFileGs_seek`, `icmFileGs_read`, `icmFileGs_write`, `icmFileGs_flush`, `icmFileGs_delete`.

## Core Behavior

- ICCBased color spaces either use the loaded ICC profile or fall back to the inline alternate color space if no profile is loaded.
- Profile loading validates the stream identity, profile class, profile connection space, and component count, then creates an icclib lookup object.
- Concretization verifies the underlying stream has not been closed/reused, clamps input to declared ranges, massages Lab input/output as needed, runs the ICC lookup, converts PCS Lab to XYZ when necessary, and finishes through the CIE remap cache.
- The wrapper `icmFileGs` adapts Ghostscript streams to icclib's file API and is allocated with C `calloc`; finalization calls icclib destructors and frees the wrapper through its `del` method.
- Serialization writes common CIE state, component count/ranges, the raw ICC stream bytes, and the Lab/XYZ PCS flag.

## Notable Risks

- The file intentionally uses “foreign” non-GC memory for icclib objects; finalization must run to avoid leaks.
- The stream pointer held by icclib is lazily refreshed before lookup, and `file_id` checks are used to detect closed/reused streams.
- `icmFileGs_read`/`write` return `size_t` but propagate negative stream status values through the return expression, which is awkward for a size-returning API.
- Several comments note color-management assumptions and potential correctness limits around ICC rendering intent.
- Serialization depends on seeking and measuring `picc->instrp`; unsupported stream behavior returns `unregistered`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsicc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsicc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsicc.h

## Role

`gsicc.h` defines ICCBased color-space parameter structures and public constructor/loading helpers.

This is color-management API infrastructure, not filesystem code.

## Main Types And APIs

- Opaque forward declarations for icclib structures `_icc` and `_icmLuBase`, avoiding a hard dependency on `icc.h` for builds without ICC support.
- `gs_cie_icc`: CIE common prefix, component count/ranges, stream identity and pointer, PCS Lab flag, icclib profile pointer, lookup pointer, and icclib file wrapper pointer.
- `private_st_cie_icc()` descriptor macro includes finalization and tracks `instrp` for GC relocation.
- `gs_cspace_build_CIEICC`, `gx_load_icc_profile`, and `gx_increment_cspace_count`.

## Important Contract

The header documents that the profile stream remains a PostScript object subject to save/restore, GC relocation, closure, and reuse; therefore `file_id` plus lazy stream-pointer update are used to keep icclib access safe.

## Notable Risks

The constructor starts the CIE ICC structure with reference count 1, and the comments call this an API bug because clients must decrement after passing the color space into normal setters to avoid permanent allocation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsicc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsimage.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsimage.c

## Role

`gsimage.c` implements the buffered public image-enumerator layer above Ghostscript's lower-level typed image device interface. It accepts arbitrary chunks of image plane data, buffers partial rows, retains unused caller data by reference, and passes whole scan-line groups to image processors/devices.

This is image rendering infrastructure, not filesystem code.

## Main Interfaces

- `gs_image_begin_typed`, `gs_image_enum_alloc`, `gs_image_init`, `gs_image_enum_init`, `gs_image_bytes_per_plane_row`, `gs_image_planes_wanted`, `gs_image_next`, `gs_image_next_planes`, `gs_image_cleanup`, `gs_image_cleanup_and_free_enum`.
- Internal helpers: `image_enum_init`, `cache_planes`, `next_plane`, `begin_planes`, `gs_image_common_init`, `gs_image_row_memory`, `free_row_buffers`.

## Core Behavior

- `gs_image_begin_typed` obtains the current device and effective clip path, loads current color if needed, and calls the device typed-image begin procedure.
- `gs_image_init` handles ImageType 1 images and imagemasks, including mask color-space suppression, cachedevice restrictions, and a static DeviceGray fallback when no color space is supplied.
- Each plane tracks a stable row buffer, a partial-row position, and a retained source string.
- `gs_image_next_planes` copies partial rows into row buffers, avoids copying full rows when caller data already has enough bytes, sends complete rows through `gx_image_plane_data_rows`, updates retained data pointers and per-plane used counts, and refreshes plane-wanted state after each transfer.
- Row buffers use `gs_memory_stable` because image data procedures may perform save/restore while image processing is active.
- Passing `dev == NULL` skips drawing, used for charpath-like contexts.

## Notable Risks

- Retained source data is held by reference; clients with movable stream buffers must honor the replacement/retention contract documented in `gsimage.h`.
- A comment says the skip-data path is not correct for ImageType 3 InterleaveType 2 when mask and image heights differ.
- `gs_image_next` is a legacy cyclic single-plane API and errors if the selected plane has retained data.
- The static DeviceGray fallback is described as potentially incorrect if a non-current color space would matter, though comments say the case appears not to arise.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsimage.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsimage.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsimage.h

## Role

`gsimage.h` declares Ghostscript's generic buffered image rendering interface.

This is image API infrastructure, not filesystem code.

## Main Declarations

- Opaque `gx_image_enum_common_t` and `gs_image_enum`.
- `gs_image_begin_typed`, `gs_image_enum_alloc`, `gs_image_init`, `gs_image_enum_init`, `gs_image_bytes_per_plane_row`, `gs_image_planes_wanted`, `gs_image_next_planes`, `gs_image_next`, `gs_image_cleanup`, `gs_image_cleanup_and_free_enum`.

## Important Contract

The header carefully defines how `gs_image_next_planes` differs from the low-level `plane_data` procedure: data can be unaligned, incomplete, supplied per selected planes, and retained by reference. If data is retained, later data for that plane replaces rather than appends to retained data unless the client passes no replacement.

## Notable Risks

The older `gs_image_next` API is only safe for image types where all planes are always wanted, share width/depth, and receive equal data per cycle; this is documented but not fully checked.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsimage.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsimpath.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsimpath.c

## Role

`gsimpath.c` converts a 1-bit image mask into vector outlines appended to the current path.

This is image/path rendering infrastructure, not filesystem code.

## Main Interface

`gs_imagepath(gs_state *pgs, int width, int height, const byte *data)`.

## Core Behavior

- Scans the bitmap from bottom-right to top-left looking for outline start pixels.
- Uses `get_pixel` with out-of-bounds pixels treated as empty.
- `trace_from` walks each connected outline clockwise, optionally in detection mode to avoid duplicate tracing, using a scaled grid and short corner strokes.
- `add_dxdy` coalesces consecutive path segments in the same direction before emitting `gs_rlineto` operations.
- Completed outlines are closed with `gs_closepath`.

## Notable Risks

The algorithm assumes packed 1-bit image data with raster `(width + 7) / 8`. The infinite-looking loop in `trace_from` relies on contour topology and start-point detection to terminate; malformed dimensions or unexpected data interpretation could lead to bad path behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsimpath.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsinit.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsinit.c

## Role

`gsinit.c` initializes and finalizes the Ghostscript imager/library runtime.

This is library lifecycle infrastructure, not filesystem code.

## Main Interfaces

- `gs_lib_init`
- `gs_lib_init0`
- `gs_lib_init1`
- `gs_lib_finit`

## Core Behavior

- `gs_lib_init0` creates the default malloc-backed Ghostscript memory allocator, clears debug flags, and disables error logging.
- `gs_lib_init1` iterates the generated `gx_init_table` and runs each configuration-specific initialization procedure.
- `gs_lib_init` composes those two stages.
- `gs_lib_finit` calls platform cleanup via `gp_exit`.

## Notable Risks

The finalizer comments note an interface problem: it cannot always know whether it owns the allocator and therefore does not release `mem` here.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsinit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsio.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsio.h

## Role

`gsio.h` prevents Ghostscript library/interpreter code from using standard C `stdin`, `stdout`, `stderr`, and convenience stdio functions directly.

This is IO discipline/build-time guard infrastructure, not filesystem code.

## Main Behavior

The header undefines and redefines `stdin`, `stdout`, `stderr`, `fgetchar`, `fputchar`, `getchar`, `gets`, `printf`, `putchar`, `puts`, `scanf`, `vprintf`, and `vscanf` to invalid identifiers/expressions so accidental direct use causes compile errors.

## Notable Risks

This is intentionally macro-invasive and must be included only where direct stdio use is prohibited. It does not block all possible stdio APIs; comments mention `perror` is not handled because of historical portability issues.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsiodev.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsiodev.c

## Role

`gsiodev.c` implements core Ghostscript IODevice registration, default unimplemented device procedures, the `%os%` host filesystem IODevice, IODevice lookup/accessors, and OS-error to PostScript-error mapping.

This is Ghostscript IO abstraction code with host filesystem access, not a filesystem implementation.

## Main Interfaces

- Initialization: `gs_iodev_init`.
- Default operations: `iodev_no_init`, `iodev_no_open_device`, `iodev_no_open_file`, `iodev_no_fopen`, `iodev_no_fclose`, `iodev_no_delete_file`, `iodev_no_rename_file`, `iodev_no_file_status`, `iodev_no_enumerate_files`, `iodev_no_get_params`, `iodev_no_put_params`.
- `%os%` operations: `iodev_os_fopen`, `iodev_os_fclose`, `os_delete`, `os_rename`, `os_status`, `os_enumerate`, `os_get_params`.
- Utilities: `gs_getiodevice`, `gs_findiodevice`, `gs_getdevparams`, `gs_putdevparams`, `gs_fopen_errno_to_code`.

## Core Behavior

- At startup, copies each configured IODevice into writable GC-managed structures and registers the device table as a GC root.
- `%os%` delegates opening to `gp_fopen`, closing to `fclose`, deletion to `unlink`, renaming to `rename`, status to `stat`, and enumeration to `gp_enumerate_files_*`.
- `%os%` reports generic/fake capacity parameters such as 1 KB block size and roughly 2 GB logical size.
- `gs_findiodevice` accepts both `%device` and `%device%` spellings.
- `gs_fopen_errno_to_code` maps common `errno` values to Ghostscript/PostScript errors.

## Notable Risks

- The failure cleanup loop in `gs_iodev_init` uses `table[i - 1]` while iterating down from `i`, which is a fragile legacy pattern and looks problematic when `i == 0`.
- `%os%` performs real host filesystem operations directly through platform wrappers; policy/sandboxing must happen elsewhere.
- `iodev_os_fopen` copies `fname` to `rfname` with `strcpy` if buffers differ, trusting the caller-provided buffer size.
- Device capacity reporting is explicitly fake and platform-independent rather than accurate.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsiodev.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsiodevs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsiodevs.c

## Role

`gsiodevs.c` implements `%stdin%`, `%stdout%`, and `%stderr%` IODevices for non-PostScript configurations.

This is standard-stream IODevice adapter code, not filesystem code.

## Main Interfaces

- Defines `gs_iodev_stdin`, `gs_iodev_stdout`, and `gs_iodev_stderr`.
- Internal helpers: `stdio_close_file`, `stdio_open`, `stdin_open`, `stdout_open`, `stderr_open`.

## Core Behavior

- Opens Ghostscript streams around `mem->gs_lib_ctx->fstdin`, `fstdout`, or `fstderr` using a 128-byte allocated buffer.
- Allows only the expected access mode: read for `%stdin%`, write for `%stdout%` and `%stderr%`.
- The close proc frees the stream buffer but intentionally does not close the underlying stdio file.

## Notable Risks

If `s_alloc` succeeds but buffer allocation fails, cleanup frees both pointers. The underlying standard file pointers are trusted to be valid in the library context.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsiodevs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsiodisk.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsiodisk.c

## Role

`gsiodisk.c` implements Ghostscript `%disk0%` through `%disk6%` IODevices as Adobe-style “flat disk” logical filesystems mapped onto host directories with a `map.txt` logical-name-to-number table.

This is Ghostscript virtual filesystem/IODevice code over the host filesystem; it is filesystem-adjacent but not a kernel filesystem.

## Main Interfaces

- Device definitions: `gs_iodev_disk0` through `gs_iodev_disk6`.
- IODevice operations: `iodev_diskn_init`, `iodev_diskn_fopen`, `diskn_delete`, `diskn_rename`, `diskn_status`, `diskn_enumerate_files_init`, `diskn_enumerate_next`, `diskn_enumerate_close`, `diskn_get_params`, `diskn_put_params`.
- Map-file helpers: `MapFileOpen`, `MapFileReadVersion`, `MapFileWriteVersion`, `MapFileRead`, `MapFileWrite`, `MapFileUnlink`, `MapFileRename`, `MapToFile`, `map_file_enum_init`, `map_file_enum_next`, `map_file_enum_close`, `map_file_name_get`, `map_file_name_del`, `map_file_name_add`, `map_file_name_ren`.

## Core Behavior

- Each `%diskN%` has a mutable `Root` parameter. Without a root, the device is unmounted/unsearchable/unwriteable and opens fail with `undefinedfilename`.
- Logical names are stored in `map.txt`; physical files are named by integer IDs in the root directory.
- Opening a logical file maps it to a physical numbered file. If missing and opened for write, the map entry is created first.
- Delete removes the map entry and unlinks the physical file. Rename updates map entries and deletes any destination logical file first.
- Enumeration scans `map.txt`, optionally matching logical names with `string_match`, and returns logical names rather than physical numbered names.
- Map updates are done by writing `Tmp.txt`, copying/editing entries, unlinking `map.txt`, and renaming the temp file.
- Device parameters report fake portable capacity values and expose the current `Root` string or null.

## Notable Risks

- The map file is plain text and update operations are not atomic with locking; concurrent writers can corrupt or lose entries.
- Map update helpers ignore many filesystem errors, including failed `unlink`/`rename` in helper routines.
- `diskn_rename` updates only the map entry and deletes any destination file; it does not rename the underlying numbered physical file, which is correct for the design but non-obvious.
- `diskn_put_params` allocates `gp_file_name_sizeof` bytes but stores `root_size = rootstr.size + 1`, so later capacity checks do not reflect the actual allocated buffer size.
- `map_file_enum_init` can return `NULL` after allocating `mapfileenum->root` if `root_name` is too long, without closing/freeing the partial enum.
- Logical names cannot include NUL, CR, or LF. Other path semantics are flattened into map entries rather than directories.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsiodisk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsiomacres.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsiomacres.c

## Role

`gsiomacres.c` implements the `%macresource%` IODevice used to load MacOS font resources from resource forks or `.dfont` data forks into Ghostscript streams.

This is Ghostscript IODevice/resource parsing code with host file access, not a filesystem implementation.

## Main Interfaces

- Device definition: `gs_iodev_macresource`.
- Device operations: `iodev_macresource_init`, `iodev_macresource_open_file`.
- Resource parsing helpers: big-endian integer readers, `res_string2type`, `res_type2string`, `read_resource_header`, `read_resource_map`, `load_resource`, `read_datafork_resource`.

## Core Behavior

- File names are expected to include a resource selector suffix: `#<type>+<id>`.
- The device first tries platform `gp_read_macresource` for a resource fork. If that fails, it treats the file as a serialized data-fork resource map (`.dfont`).
- For data forks, it reads the resource header, resource map, type list, reference records, optional Pascal names, and then loads the requested resource data by type/id.
- On success, it allocates a Ghostscript buffer, copies the resource data into it, creates a read-string stream, and returns that stream.

## Notable Risks

- The parser uses C `malloc` for headers, lists, resource names, and data and does not consistently free all allocations on success/error paths.
- Several reads do not validate short reads or buffer bounds after the map header is loaded.
- `read_int8` stores `fgetc` into a `byte`, then checks `c < 0`; EOF detection is ineffective if `byte` is unsigned.
- `strncpy(filename, fname, min(namelen, gp_file_name_sizeof))` may leave `filename` unterminated when `namelen >= gp_file_name_sizeof`.
- Type strings are assumed to be at least four bytes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsiomacres.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsiorom.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsiorom.c

## Role

`gsiorom.c` defines a `%rom%` IODevice intended for an embedded compressed in-memory filesystem image, but this implementation is only a stub.

This is Ghostscript virtual filesystem adapter scaffolding, not a real filesystem implementation in this copy.

## Main Interfaces

- Device definition: `gs_iodev_rom`.
- Device operations: `iodev_rom_init`, `iodev_rom_open_file`.
- State type: `romfs_state` with an `image` pointer.

## Core Behavior

- Initialization allocates a `romfs_state` and sets `image` to `NULL`, but does not assign it to `iodev->state` in the code shown.
- Opening any file ignores `fname`, `namelen`, and `access`, allocates a buffer containing the fixed string `this came from the compressed romfs.`, and returns it as a read-string stream.

## Notable Risks

The file advertises compressed ROM filesystem access, but the implementation is fake. It leaks/loses the allocated `romfs_state` because it is not stored on the IODevice, and `iodev_rom_open_file` does not check allocation failure for `s_alloc`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsiorom.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsipar3x.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsipar3x.h

## Role

`gsipar3x.h` defines Ghostscript's extended ImageType 3x parameters for transparency-capable images with opacity and shape masks.

This is image parameter API infrastructure, not filesystem code.

## Main Declarations

- `IMAGE3X_IMAGETYPE` constant set to `103`.
- `gs_image3x_mask_t`: interleave type, optional matte color, and mask data dictionary.
- `gs_image3x_t`: pixel-image DataDict plus `Opacity` and `Shape` mask dictionaries.
- `private_st_gs_image3x()` GC descriptor macro.
- `gs_image3x_t_init` initializer declaration.

## Important Contract

For `InterleaveType == 3`, mask data sources precede pixel data sources, with opacity before shape. InterleaveType 2 is not allowed for this image type. MaskDict color spaces are ignored, and `BitsPerComponent == 0` means a mask is not supplied.

## Notable Risks

The header says the implementation does not currently check that clients always provide mask data before the pixel data it masks.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsipar3x.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsiparam.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsiparam.h

## Role

`gsiparam.h` defines Ghostscript's common image parameter structures for abstract images, data images, pixel images, and ImageType 1 images/masks.

This is image parameter API infrastructure, not filesystem code.

## Main Types And Constants

- `gs_image_common_t`: image type pointer and `ImageMatrix`.
- `GS_IMAGE_MAX_COLOR_COMPONENTS`, `GS_IMAGE_MAX_COMPONENTS`, `GS_IMAGE_MAX_PLANES` plus backward-compatible aliases.
- `gs_data_image_t`: width, height, bits per component, decode array, interpolate flag.
- `gs_image_format_t`: chunky, component-planar, and bit-planar formats.
- `gs_pixel_image_t`: data image fields plus format, color space, and `CombineWithColor`.
- `gs_image_alpha_t`: no alpha, alpha first, alpha last.
- `gs_image1_t`/`gs_image_t`: ImageType 1 pixel image or mask, including `ImageMask`, mask adjustment, and alpha.
- Initialization APIs: `gs_image_common_t_init`, `gs_data_image_t_init`, `gs_pixel_image_t_init`, `gs_image_t_init_adjust`, `gs_image_t_init_mask_adjust` and compatibility macros.

## Important Contract

Clients must initialize image parameter structs with the provided initializer functions before setting fields, because the structs may grow. DataSource and MultipleDataSources are deliberately not stored in these structs.

## Notable Risks

The file includes an under-construction disabled service block. The mask initializer defaults `adjust` to true for backward compatibility, and comments call this a bad decision that cannot be changed without breaking clients.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsiparam.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsiparm2.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsiparm2.h

## Role

`gsiparm2.h` defines Ghostscript ImageType 2 image parameters.

This is image parameter API infrastructure, not filesystem code.

## Main Declarations

- Opaque `gx_path` forward declaration.
- `gs_image2_t`: common image fields, `DataSource` graphics state pointer, origin/size floats, optional `UnpaintedPath`, and `PixelCopy` flag.
- `private_st_gs_image2()` GC descriptor macro tracks `DataSource` and `UnpaintedPath`.
- `gs_image2_t_init` initializer declaration.

## Important Defaults

The initializer defaults `UnpaintedPath` to `0` and `PixelCopy` to `false`.

## Notable Risks

The type stores a `gs_state *` as `DataSource`; callers and GC descriptors must keep that state reachable and correctly relocated.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsiparm2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsiparm3.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsiparm3.h

## Role

`gsiparm3.h` defines Ghostscript ImageType 3 parameters for images with masks.

This is image parameter API infrastructure, not filesystem code.

## Main Declarations

- `gs_image3_interleave_type_t`: chunky, interleaved scan lines, or separate mask source.
- `gs_image3_t`: pixel-image DataDict, `InterleaveType`, and `MaskDict`.
- `private_st_gs_image3()` GC descriptor macro.
- `gs_image3_t_init` initializer declaration.

## Important Contract

For InterleaveTypes 2 and 3, the client is responsible for providing mask data before the image data it masks. For InterleaveType 3, mask data is an additional data source before pixel data.

## Notable Risks

The header states that the implementation does not currently check the mask-before-pixel ordering requirement.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsiparm3.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsiparm4.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsiparm4.h

## Role

`gsiparm4.h` defines Ghostscript ImageType 4 image parameters for masked-color images.

This is image parameter API infrastructure, not filesystem code.

## Main Declarations

- `gs_image4_t`: pixel-image common fields, `MaskColor_is_range`, and `MaskColor` array sized for exact values or ranges.
- `private_st_gs_image4()` GC descriptor macro.
- `gs_image4_t_init` initializer declaration.

## Important Contract

If `MaskColor_is_range` is false, the first N `MaskColor` entries are sample values. If true, the first `2*N` entries define sample ranges. The initializer defaults `MaskColor_is_range` to false.

## Notable Risks

Comments say the largest sample values currently supported by the library are 12 bits, though the design anticipates future DevicePixel images with larger samples.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsiparm4.h -->