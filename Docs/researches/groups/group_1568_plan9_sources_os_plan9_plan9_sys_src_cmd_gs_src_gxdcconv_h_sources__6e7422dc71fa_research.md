# Group Research: group_1568_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_gxdcconv_h_sources__6e7422dc71fa

Scope: `Docs/research_subset_a.md` includes `sources/os/plan9/plan9`. I read every listed file completely: 24 files, 6,943 total lines.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdcconv.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdcconv.h

Internal Ghostscript device color conversion interface.

- Declares `frac`-based conversion helpers between RGB, CMYK, and gray:
  - `color_rgb_to_gray`
  - `color_rgb_to_cmyk`
  - `color_cmyk_to_gray`
  - `color_cmyk_to_rgb`
- All routines accept `const gs_imager_state *pis`, so conversions can account for imager-state color behavior rather than being pure numeric transforms.
- Includes only `gxfrac.h`; relies on prior visibility of `gs_imager_state`.

Role in subsystem: small internal API boundary used by device/color rendering code that needs canonical fractional color-space conversions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdcconv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdcolor.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdcolor.c

Implements Ghostscript’s core simple device-color types and supporting serialization helpers.

- Defines standard device color type vectors:
  - `gx_dc_type_none`: unset/undefined color.
  - `gx_dc_type_null`: drawing has no visible effect.
  - `gx_dc_type_pure`: a concrete single `gx_color_index`.
- Provides black/white device color caching:
  - `gx_device_black`
  - `gx_device_white`
  - `gx_device_decache_colors`
- `gx_set_rop_no_source` prepares a RasterOp source representing black, using cached device black when possible.
- `gx_device_color_equal` dispatches through the color type’s `equal` method.
- Maps device color type pointers to compact indices for command-list serialization:
  - `gx_get_dc_type_index`
  - `gx_get_dc_type_from_index`
  - The table includes none, null, pure, binary halftone, colored halftone, and WTS. Pattern colors are intentionally excluded from command lists.
- Implements canonical phase methods:
  - `gx_dc_no_get_phase`
  - `gx_dc_ht_get_phase`
- `none` color methods mostly no-op, fail on invalid rendering, and serialize as zero bytes if redundant.
- `null` color methods always render no output and compare equal by type.
- `pure` color methods render via `fill_rectangle`, `copy_mono`, or `strip_copy_rop` depending on RasterOp/source/mask needs.
- `gx_dc_pure_write` and `gx_dc_pure_read` serialize/deserialize a pure `gx_color_index`.
- `gx_dc_pure_get_nonzero_comps` decodes a pure color and returns a component bit mask for overprint support.
- `gx_complete_halftone` finalizes a colored halftone `gx_device_color`, including plane mask.
- `gx_dc_default_fill_masked` scans a 1-bit mask into runs and fills rectangles through the active device color.
- `gx_dc_write_color` / `gx_dc_read_color` provide compact big-endian-ish color-index encoding for command lists, with `gx_no_color_index` encoded as single byte `0xff`.

Important invariants:
- Equality must be conservative because it gates cache reuse.
- Command lists cannot store raw type pointers; stable type indices are used.
- Color index encoding depends on `dev->color_info.depth`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdcolor.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdcolor.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdcolor.h

Defines the internal device-color object model.

- Introduces `gx_rop_source_t`, the source bitmap/color descriptor used by RasterOp paths.
- Provides `gx_rop_no_source_body`, `gx_rop_source_set_color`, and `gx_set_rop_no_source` helpers.
- Defines `gx_device_color_type_s`, the method table for device color variants.
- Device-color methods include:
  - `save_dc`
  - `get_dev_halftone`
  - `get_phase`
  - `load`
  - `fill_rectangle`
  - `fill_masked`
  - `equal`
  - `write`
  - `read`
  - `get_nonzero_comps`
- Documents command-list serialization rules in detail:
  - `write` may emit no bytes if the saved color already matches.
  - `read` reconstructs the color and may receive the same `pdevc` and `prior_devc`.
  - Device halftones are serialized separately as all-band commands.
- Declares standard device color type records:
  - none, null, pure, binary halftone, colored halftone, WTS.
- Exports nonzero-component helpers for pure and halftone colors.
- Provides macros for:
  - remapping device color
  - loading halftone/pattern cache
  - filling rectangles through a device color
- Declares `gx_dc_write_color` and `gx_dc_read_color`.

Role in subsystem: central polymorphic contract between high-level graphics state colors and low-level device rendering operations.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdcolor.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdda.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdda.h

Macro implementation of Bresenham-style digital differential analyzers.

- Used for trapezoid edge tracking, rasterizing transformed images, curve flattening, and potentially lines.
- Represents exact values of `floor(i * D / N)` while maintaining:
  - current quotient `Q`
  - remainder state `R`
  - step values `dQ`, `dR`, `NdR`
- Defines generic DDA state/step macros:
  - `dda_state_struct`
  - `dda_step_struct`
- Provides fixed-point DDA types:
  - `gx_dda_state_fixed`
  - `gx_dda_step_fixed`
  - `gx_dda_fixed`
  - `gx_dda_fixed_point`
- Main operations:
  - `dda_init_state`
  - `dda_init_step`
  - `dda_init`
  - `dda_step_add`
  - `dda_current`
  - `dda_next`
  - `dda_previous`
  - `dda_advance`
  - `dda_translate`
- Handles negative `D` carefully because old C division/remainder semantics were not reliable across compilers.

Important detail: `dda_state_advance` is explicitly noted as inefficient and loops one step at a time.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdda.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdevbuf.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdevbuf.h

Defines buffer-device management procedure vectors.

- Associated mainly with printer and banded devices, though comments leave room for wider use.
- Includes `gxrplane.h` for render-plane structures.
- Defines `gx_device_buf_space_t`:
  - `bits`
  - `line_ptrs`
  - `raster`
- Defines `gx_device_buf_procs_t` with methods:
  - `create_buf_device`
  - `size_buf_device`
  - `setup_buf_device`
  - `destroy_buf_device`
- `create_buf_device` may allocate or initialize an existing memory device depending on whether `mem` is NULL.
- `setup_buf_device` supports both full-band buffers and partial-band scanline readout buffers.
- Declares default implementations:
  - `gx_default_create_buf_device`
  - `gx_default_size_buf_device`
  - `gx_default_setup_buf_device`
  - `gx_default_destroy_buf_device`

Concurrency note: for async devices, `size_buf_device` may be called by writer or reader threads; other procedures are reader-thread-only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdevbuf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdevcli.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdevcli.h

Primary Ghostscript device-client interface and driver ABI definition.

- Documents device memory-management rules:
  - Devices are reference-counted.
  - Retained devices are not freed solely by reference counting.
  - Stack/static/embedded devices must be retained or initialized with NULL memory.
  - Forwarding-device targets must be set with `gx_device_set_target`, not direct assignment.
- Defines major forward declarations used by driver procs:
  - graphics state
  - paths
  - clip paths
  - image enumerators
  - pattern instances
- Defines drawing and geometry helper types:
  - `gx_drawing_color`
  - `graphics_object_type`
  - `gs_fixed_edge`
  - `gs_linear_color_edge`
  - `frac31`
- Defines `gx_device_color_info`, the expanded color model descriptor:
  - component counts
  - additive/subtractive polarity
  - color-index depth
  - gray component index
  - max/dither levels
  - antialiasing info
  - separable/linear encoding metadata
  - component shifts/bits/masks
  - process color model name
  - overprint support flags
- Provides many backward-compatible color-info macros such as `dci_values`, `dci_std_color`, and `dci_black_and_white`.
- Defines page device procs:
  - `install`
  - `begin_page`
  - `end_page`
- Defines `gx_device_common`, the core fields of every device:
  - memory/type/finalizer/reference count
  - open state
  - color info and cached black/white pixels
  - geometry, resolution, margins
  - page counts/copy settings
  - page procs
  - procedure vector
- Defines `dev_proc` and `set_dev_proc` access macros.
- Declares the large `gx_device_procs` template covering:
  - open/close/sync/output
  - color mapping
  - fills, copies, masks, RasterOps
  - paths, trapezoids, triangles, thin lines
  - images and typed images
  - clipping and get-bits
  - compositors/transparency
  - DeviceN color support
  - high-level patterns/colors
  - linear-color shading fills
  - spot equivalent colors
- Provides image helper wrappers and deprecated image-data compatibility APIs.
- Defines `gx_device_s`, `gx_device_forward`, and `gx_device_null`.
- Declares device lifecycle helpers:
  - `gx_device_init`
  - `gs_make_null_device`
  - `gx_device_set_target`
  - `gx_device_retain`
  - `gs_closedevice`
  - `gx_device_free_local`
- Declares device geometry helpers:
  - raster calculation
  - resolution/media-size changes
  - margin setup
- Declares forwarding/default procedure families and color-proc utilities.
- Provides clipping macros for fill and bitmap-copy operations.
- Defines media parameter helper structs and writers.

Role in subsystem: this is the central C ABI for Ghostscript raster devices and forwarding/compositor devices. Most rendering subsystems depend on these structures and procs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdevcli.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdevice.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdevice.h

Device-implementor support header layered on `gxdevcli.h`.

- Defines default paper sizes and A4/US Letter selection macros.
- Provides static device-initializer macro families:
  - `std_device_part1_`
  - `std_device_part2_`
  - `std_device_part3_`
  - `std_device_std_body`
  - `std_device_full_body`
  - color and alpha variants
- Declares default optional device procedures:
  - open/close/output/sync
  - color mapping
  - fills/copies/path/image operations
  - RasterOp and strip-copy fallbacks
  - clipping, typed images, compositors, hardware params, text begin
  - high-level color and shading support
- Declares standard color mapping procedures for black-on-white, grayscale, RGB, CMYK, 1-bit CMYK, and 8-bit gray/CMYK.
- Declares forwarding-device procedure implementations for most driver operations.
- Provides implementation utilities:
  - `gx_device_set_procs`
  - `gx_device_fill_in_procs`
  - `gx_device_forward_fill_in_procs`
  - `gx_device_forward_color_procs`
  - `gx_device_copy_color_procs`
  - `gx_device_copy_color_params`
  - `gx_device_copy_params`
- Declares device black/white cache accessors and decache.
- Declares output file parsing/open/close helpers.
- Defines `MIN_CONTONE_LEVELS` and `gx_device_must_halftone`.
- Provides rectangle clipping macros for fill and copy paths.
- Defines input/output media parameter structures and helper functions.

Relationship: `gxdevcli.h` defines the ABI; `gxdevice.h` adds initializer macros, default implementations, and driver utility declarations for implementors.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdevice.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdevmem.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdevmem.h

Defines Ghostscript memory devices, which are bitmap-backed forwarding devices.

- Memory devices support multiple bitmap formats:
  - 1-bit mono
  - 2/4/8-bit mapped color
  - 16/24-bit RGB
  - 32-bit CMYK
  - wider component layouts with small caches
- Distinguishes standard big-endian bitmap storage from word-oriented machine-order storage.
- Describes four storage allocation modes:
  - allocate bits and line pointers via `bitmap_memory`
  - caller supplies bitmap, device allocates line pointers
  - device allocates only line pointers and caller sets them later
  - caller owns both bitmap and line pointers
- Defines `gx_device_memory_s`, extending `gx_device_forward_common`.
- Key fields:
  - `raster`, `base`, `line_ptrs`
  - bitmap and line-pointer allocators
  - `foreign_bits`, `foreign_line_pointers` GC flags
  - planar-device descriptors
  - palette
  - cached packed-color expansions for 24/40/48/56/64-bit cases
  - alpha-buffer mapping/scaling fields
- Defines `mem_device_init_private` initializer data.
- Declares size/raster helpers:
  - `gdev_mem_bits_size`
  - `gdev_mem_line_ptrs_size`
  - `gdev_mem_data_size`
  - `gdev_mem_max_height`
  - `gdev_mem_raster`
- Declares prototype lookup:
  - `gdev_mem_device_for_bits`
  - `gdev_mem_word_device_for_bits`
- Declares constructors:
  - `gs_make_mem_mono_device`
  - `gs_make_mem_device`
  - `gs_make_mem_abuf_device`
  - `gs_make_mem_alpha_device`
- Declares scanline setup:
  - `gdev_mem_open_scan_lines`
  - `gdev_mem_set_line_ptrs`
- Declares tests:
  - `gs_device_is_memory`
  - `gs_device_is_abuf`

Important invariant: planar devices require `color_info.depth` to equal the sum of plane depths.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdevmem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdevndi.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdevndi.c

Implements DeviceN binary halftoning helpers.

- Provides quotient tables `q0` through `q7` and exported `fc_color_quo` for fast fractional color-level computation.
- `gx_render_device_DeviceN_wts` constructs WTS device colors:
  - sets `gx_dc_type_wts`
  - stores WTS halftone pointer
  - builds `plane_vector` entries by encoding single-component max colors
  - stores fractional component levels
- `gx_render_device_DeviceN` renders DeviceN colors:
  - chooses WTS path if present in the halftone component order
  - computes device-level base values and residual halftone levels
  - returns a pure color when no dithering is required
  - otherwise builds a colored halftone device color and phase
  - reduces one-plane colored halftones when possible
- `gx_devn_reduce_colored_halftone` converts colored halftones with zero or one active varying plane into:
  - a pure color, or
  - a binary halftone
- Handles subtractive devices by inverting both level and color pair for binary halftone reduction.

Role in subsystem: bridges fractional DeviceN color values, device color encoding, and halftone order selection.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdevndi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdevndi.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdevndi.h

Public internal interface to DeviceN halftone handling.

- Includes `gxfrac.h`.
- Forward-declares `gx_device_halftone`.
- Declares `gx_render_device_color_devn`, which renders a color possibly by halftoning.
- Signature includes RGB, white, CMYK flag, alpha, output device color, target device, device halftone, and halftone phase.

Note: this header’s declared function name differs from `gxdither.h`’s `gx_render_device_DeviceN`; this file appears to expose a higher-level DeviceN color rendering entry.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdevndi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdevrop.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdevrop.h

Small RasterOp extension header.

- Declares unaligned implementations:
  - `gx_copy_rop_unaligned`
  - `gx_strip_copy_rop_unaligned`
- Uses `dev_proc_copy_rop` and `dev_proc_strip_copy_rop` macros from the device interface.

Role: exposes slower but more flexible RasterOp copy paths for data that does not meet the normal alignment requirements.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdevrop.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdht.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdht.h

Defines internal device halftone structures and invariants.

- Documents Ghostscript’s halftone geometry:
  - rational basic cells
  - multi-cells
  - rectangular super-cells
  - strip-based representation for large shifted cells
- Defines `gx_ht_cell_params_t` and `gx_compute_cell_values`.
- Defines halftone bit/order representation:
  - `ht_mask_t`
  - `gx_ht_bit`
  - `ht_sample_t`
  - `max_ht_sample`
- Defines `gx_ht_order_procs_t` with methods:
  - `construct_order`
  - `bit_index`
  - `render`
  - `draw`
- Declares `ht_order_procs_table` with default `gx_ht_bit[]` and compact `ushort[]` representations.
- Defines `gx_ht_order`, including:
  - cell params
  - WTS fields
  - width/height/raster/shift/full height
  - level table
  - bit-data table
  - cache pointer
  - transfer map
  - screen sampling parameters
- Documents strip-order invariants:
  - complete orders have `shift == 0` and `full_height == height`
  - strip orders compute full height from width/shift GCD
- Defines `gx_ht_order_component`, pairing an order with component number/name.
- Defines `gx_device_halftone_s`:
  - default order first for subclassing
  - refcount and id
  - halftone type
  - component array
  - component counts
  - LCM tile dimensions
- Provides GC descriptors for orders, components, and device halftones.
- Declares:
  - `gx_ht_complete_threshold_order`
  - `gx_device_halftone_release`

Important memory rule: halftone substructures are assumed allocated with the same allocator as the device halftone.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdht.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdhtres.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdhtres.h

Defines precompiled halftone resource descriptors.

- Used by halftones generated by `genht`.
- Defines `gx_device_halftone_resource_t` with:
  - resource name
  - halftone type
  - width/height
  - number of levels
  - `levels`
  - `bit_data`
  - element size
- Defines `DEVICE_HALFTONE_RESOURCE_PROC(proc)`, a function signature returning a null-terminated list of resident halftone resources.

Role: lets the halftone serializer/deserializer compare transmitted orders against ROM/precompiled resources and reuse resident data.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdhtres.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdhtserial.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdhtserial.c

Implements serialization and deserialization for traditional device halftones.

- Declares resident halftone resource list via `extern_gx_device_halftone_list`.
- Defines transfer-function serialization types:
  - none
  - identity
  - complete mapped table
- Defines halftone order type tags:
  - traditional
  - WTS
- `gx_ht_write_tf` serializes transfer maps:
  - one byte for none/identity
  - one byte plus mapped values for complete transfer tables
- `gx_ht_read_tf` reconstructs transfer maps and allocates `gx_transfer_map`.
- `gx_ht_write_component` serializes only the halftone order portion of a component.
  - Does not transmit component number or colorant name.
  - Rejects WTS orders as unsupported.
  - Omits reconstructible/runtime-only fields such as params, WTS enum, raster, original height/shift, full height, memory/cache, and screen params.
  - Encodes order procs as index into `ht_order_procs_table`.
  - Copies level and bit-data arrays verbatim.
- `gx_ht_read_component` reconstructs an order:
  - validates type and minimum encoded data
  - allocates level/bit-data arrays with `gx_ht_alloc_ht_order`
  - reads transfer function
  - compares against resident precompiled halftone resources
  - if resident data matches, frees transmitted arrays and points to ROM arrays
- `gx_ht_write` serializes a full multi-component halftone:
  - requires component array
  - writes halftone type and number of device components
  - serializes each component order
  - ignores `pdht->order`, rc/id, and LCM fields because renderer reconstructs them
- `gx_ht_read_and_install` reads a serialized halftone into stack component storage, then immediately installs it with `gx_imager_dev_ht_install`.
  - On failure, releases allocated component orders.
  - Combines read and install to avoid allocating a heap `gx_device_halftone` just to install and release it.

Limitations: WTS serialization is explicitly not implemented.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdhtserial.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdhtserial.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdhtserial.h

Declares halftone serialization API.

- Forward-declares `gs_memory_t`, `gx_device`, `gx_device_halftone`, and `gs_imager_state`.
- Declares `gx_ht_write`:
  - serializes a halftone to caller-provided buffer
  - reports required/used size through `psize`
- Declares `gx_ht_read_and_install`:
  - reconstructs a halftone from serialized bytes
  - installs it directly as current imager-state halftone
  - returns bytes read or negative error
- Notes that read and install are combined to avoid unnecessary allocation.

Minor issue: closing include-guard comment spells `gxdhtserail_INCLUDED`, while the actual guard is `gxdhtserial_INCLUDED`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdhtserial.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdither.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdither.h

Interface to DeviceN dithering/halftone helpers implemented in `gxdevndi.c`.

- Includes `gxfrac.h`.
- Forward-declares `gx_device_halftone`.
- Declares `gx_render_device_DeviceN`, which renders an array of fractional DeviceN component values into a device color, possibly using a halftone.
- Declares `gx_devn_reduce_colored_halftone`, which reduces colored halftones with zero or one varying plane to a pure color or binary halftone.

Role: thin API boundary between color rendering code and DeviceN halftoning implementation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdither.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdtfill.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdtfill.h

Configurable include-template implementing trapezoid filling.

- Not a conventional standalone header; intended to be included multiple times with different macro configurations.
- Required configuration macros include:
  - `GX_FILL_TRAPEZOID`
  - `CONTIGUOUS_FILL`
  - `SWAP_AXES`
  - `FILL_DIRECT`
  - `LINEAR_COLOR`
  - `EDGE_TYPE`
  - `FILL_ATTRS`
- Implements scan-conversion for trapezoids bounded by left/right edges and y range.
- Normal mode paints pixels whose centers lie inside the trapezoid, excluding right/top boundaries.
- `CONTIGUOUS_FILL` mode adds minimal extra pixels to avoid dropouts in narrow trapezoids.
- `LINEAR_COLOR` mode fills scanlines with gradient color and returns overflow errors through gradient setup/fill path.
- Uses fixed-point rounding and rational-floor logic to handle edge cases around pixel centers.
- Optimizes vertical-edge rectangle cases when not filling linear color.
- Supports swapped axes by swapping rectangle coordinates at fill time.
- Uses direct device `fill_rectangle` for pure color fast paths when `FILL_DIRECT` is enabled, otherwise goes through device-color fill dispatch.
- Contains debug visualization hooks through `vd_rect`.
- Checks for interrupts before returning.

Role: shared low-level rasterization algorithm generator for multiple trapezoid-fill variants.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdtfill.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfapi.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfapi.c

Implements UFST font callback dispatch support.

- Includes Ghostscript core headers and UFST headers:
  - `cgconfig.h`
  - `port.h`
  - `shareinc.h`
- Provides stub callbacks returning `NULL`:
  - `stub_PCLEO_charptr`
  - `stub_PCLchId2ptr`
  - `stub_PCLglyphID2Ptr`
- Maintains three static function pointers initially pointing to stubs:
  - `m_PCLEO_charptr`
  - `m_PCLchId2ptr`
  - `m_PCLglyphID2Ptr`
- Exports callback functions called by UFST:
  - `PCLEO_charptr`
  - `PCLchId2ptr`
  - `PCLglyphID2Ptr`
- `gx_set_UFST_Callbacks` installs client-provided callback functions.
- `gx_reset_UFST_Callbacks` restores stubs.

Important limitation: comments state these callback variables are static until graphics-library reentrancy and UFST callback reentrancy are fixed, so this dispatch mechanism is not reentrant/thread-local.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfapi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfapi.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfapi.h

Header for UFST font callback dispatch.

- Declares `gx_set_UFST_Callbacks`, accepting callback pointers for:
  - `PCLEO_charptr`
  - `PCLchId2ptr`
  - `PCLglyphID2Ptr`
- Declares `gx_reset_UFST_Callbacks`.

Dependencies: callback argument/return types such as `LPUB8`, `UW16`, and `IF_STATE` must be supplied by UFST-related includes before use.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfapi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfarith.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfarith.h

Floating-point arithmetic support macros and trig declarations.

- Includes `gconfigv.h` for `USE_FPU` and `gxarith.h`.
- On systems with no/slow FPU and IEEE floats, overrides selected float-test macros with bit-level tests:
  - `is_fzero`
  - `is_fzero2`
  - `is_fneg`
  - `is_fge1`
  - `f_fits_in_ubits`
  - `f_fits_in_bits`
- Handles float-as-int access depending on architecture word size.
- Handles sign-byte detection depending on endian.
- Defines IEEE constants:
  - `IEEE_expt`
  - `IEEE_f1`
- Declares degree-based trig helpers:
  - `gs_sin_degrees`
  - `gs_cos_degrees`
  - `gs_sincos_degrees`
- Defines `gs_sincos_t`, including an `orthogonal` flag for multiples of 90 degrees.
- Declares `gs_atan2_degrees`, which follows PostScript quadrant rules and may return `gs_error_undefinedresult`.

Risk note: the slow-FPU path uses type-punning through pointer casts, reflecting old Ghostscript portability assumptions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfarith.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfcache.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfcache.h

Defines font, font/matrix pair, and character cache structures.

- Defines `cached_fm_pair`, the key for a base font plus transformation:
  - font pointer or UID/FontType
  - hash
  - matrix entries
  - cached character count
  - xfont lookup state
  - TrueType interpreter/reader pointers
  - design-grid flag
- UID-backed entries may survive font restore with `font == 0`.
- Nonzero `PaintType` fonts cannot be cached due to stroke-width dependency.
- Defines `fm_pair_cache`, an array/rover cache for font/matrix pairs.
- Defines `cached_char` as a subclass of the generic bitmap cache entry:
  - key fields include glyph code, pair, writing mode, and depth
  - value fields include bitmap data, xglyph, width, and offset
- Cached character bits immediately follow the `cached_char` structure.
- Real cached chars must have either bitmap bits or a valid xfont glyph.
- Defines unusual memory-management model:
  - `cached_char` objects live inside non-GC bitmap chunks.
  - The font directory traces/relocates pointers from the cache manually.
- Defines `char_cache`:
  - bitmap cache chunks
  - struct/bits allocators
  - open-addressed hash table
  - size limits
  - glyph marking callback
- Defines `gs_font_dir`, the font-directory/cache manager:
  - original fonts
  - scaled font cache
  - font/matrix cache
  - character cache
  - GC scan state
  - user params such as `AlignToPixels` and `GridFitTT`
  - glyph-to-Unicode and TrueType interpreter data
- Declares cache procedures:
  - `gx_char_cache_alloc`
  - `gx_char_cache_init`
  - `gx_purge_selected_cached_chars`
  - matrix/key computation helpers
  - font/matrix lookup/add
  - xfont lookup
  - purge helpers

Role: core data model for Ghostscript glyph caching and font-directory GC integration.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfcache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfcid.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfcid.h

Defines CID-keyed font structures.

- Includes CID, base font, and Type 42 font headers.
- Defines common CID data `gs_font_cid_data`:
  - `CIDSystemInfo`
  - `CIDCount`
  - `GDBytes`
- Defines CIDFontType 0 (`gs_font_cid0`):
  - common CID data
  - `CIDMapOffset`
  - `FDArray` of Type 1 subfonts
  - `FDBytes`
  - `glyph_data` callback
  - `proc_data`
- Defines CIDFontType 1 (`gs_font_cid1`), carrying base font data plus `CIDSystemInfo`.
- Defines CIDFontType 2 (`gs_font_cid2`) as a Type 42 subclass:
  - common CID data
  - `MetricsCount`
  - `CIDMap_proc`
  - saved original Type 42 outline/metrics procs for wrappers
- Provides GC descriptors for CID font data and concrete CID font types.
- Declares:
  - `gs_font_cid_system_info`
  - `gs_font_cid0_enumerate_glyph`
  - `gs_is_CIDSystemInfo_compatible`
  - `gs_cid0_indexed_font`
  - `gs_cid0_has_type2`

Role: internal representation for CID fonts and their subfont/mapping relationships.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfcid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfcmap.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfcmap.h

Defines internal CMap abstractions.

- CMaps map variable-length input characters to font-specific glyph/CID values.
- Supports Adobe-style CMaps while allowing virtual implementations such as direct TrueType `cmap` access.
- Defines `MAX_CMAP_CODE_SIZE` as 4.
- Defines `gx_code_space_range_t`:
  - first/last byte arrays
  - code size
- Defines lookup value types:
  - `CODE_VALUE_CID`
  - `CODE_VALUE_GLYPH`
  - `CODE_VALUE_CHARS`
  - `CODE_VALUE_NOTDEF`
- Defines `gx_cmap_lookup_entry_t`, covering range/single keys and string/name/CID-like values.
- Defines common CMap fields via `GS_CMAP_COMMON`:
  - `CMapType`
  - internal id
  - name
  - CID system info array
  - font count
  - version/UID/UIDOffset/WMode
  - Unicode/ToUnicode flags
  - glyph name callback
  - procedure vector
- Defines `gs_cmap_procs_t`:
  - `decode_next`
  - `enum_ranges`
  - `enum_lookups`
  - `is_identity`
- Defines range and lookup enumerator structures and procs.
- Provides client enumeration APIs:
  - `gs_cmap_ranges_enum_init`
  - `gs_cmap_enum_next_range`
  - `gs_cmap_lookups_enum_init`
  - `gs_cmap_enum_next_lookup`
  - `gs_cmap_enum_next_entry`
- Provides implementation helpers:
  - `gs_cmap_init`
  - `gs_cmap_alloc`
  - enumerator setup helpers
  - identity checks

Role: virtual base representation and traversal API for CMaps.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfcmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfcmap1.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfcmap1.h

Defines concrete Adobe CMapType 1/2 implementation structures.

- Includes `gxfcmap.h`.
- Defines `gs_cmap_adobe1_t`, a concrete subclass of `gs_cmap_t`.
- Splits each map into:
  - key map from parsed character to value-table index
  - value table holding strings, names, or CIDs
- This split is designed to eventually allow related large CMaps to share value tables.
- Defines `gx_cmap_lookup_range_t`:
  - back pointer to CMap for glyph marking
  - entry count
  - shared key prefix
  - key size/range flag
  - packed key string
  - value type/size/string
  - font index
- Defines GC descriptors for lookup ranges, including glyph-name marking support.
- Defines:
  - `gx_code_space_t`
  - `gx_code_map_t`
- `gs_cmap_adobe1_s` contains common CMap fields plus:
  - code space
  - defined-character map
  - notdef map
  - glyph marking callback/data
- Declares `gs_cmap_adobe1_alloc`, which allocates and initializes the common structure plus storage for ranges/lookups/keys/values; caller fills actual data.

Role: concrete storage model for Adobe-style CMaps used by Ghostscript font/CID machinery.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfcmap1.h -->