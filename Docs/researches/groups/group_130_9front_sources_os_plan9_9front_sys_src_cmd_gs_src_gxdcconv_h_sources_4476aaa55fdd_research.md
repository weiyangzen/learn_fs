# Group Research: group_130_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_gxdcconv_h_sources_4476aaa55fdd

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/9front`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdcconv.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdcconv.h

This small internal header declares Ghostscript device color conversion entry points over fractional color components. It includes `gxfrac.h` for the `frac` representation and exposes RGB/CMYK/gray conversion helpers that take a `const gs_imager_state *` so transfer/color rendering state can influence conversions.

The API surface is four declarations: `color_rgb_to_gray`, `color_rgb_to_cmyk`, `color_cmyk_to_gray`, and `color_cmyk_to_rgb`. The RGB/CMYK conversion routines write into caller-provided arrays (`frac cmyk[4]` and `frac rgb[3]`), while gray conversion returns a single `frac`.

Filesystem relevance: none directly. This belongs to the bundled Ghostscript rendering stack under 9front and is graphics/color infrastructure, not Plan 9 VFS or storage code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdcconv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdcolor.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdcolor.c

This file implements the standard Ghostscript device color types for "none", "null", and "pure" colors and provides shared helpers for device color equality, phase, masked filling, black/white pixel caching, RasterOp no-source setup, and command-list serialization of device color indices.

The top of the file defines `gx_dc_type_data_none`, `gx_dc_type_data_null`, and `gx_dc_type_data_pure` as `gx_device_color_type_t` method vectors. The "none" type mostly returns errors or no-op results for invalid/unset colors; the "null" type consumes drawing operations without output; the "pure" type represents one encoded device pixel and delegates drawing to `fill_rectangle`, `copy_mono`, or `strip_copy_rop` depending on logical operation and mask/source requirements.

`gx_device_black`, `gx_device_white`, and `gx_device_decache_colors` maintain cached encoded black/white pixel values in `dev->cached_colors`. They use the device color mapping procedures (`get_color_mapping_procs`, `map_gray`, `encode_color`) and reset to `gx_no_color_index` when invalidated.

`gx_set_rop_no_source` builds an appropriate `gx_rop_source_t` for RasterOp operations with no source. It special-cases devices whose black pixel is 0 or 1 using static source records, otherwise it patches a caller-provided source with the encoded black pixel.

Device color type serialization support is handled by a private table mapping method-vector pointers to stable indices for command lists: none, null, pure, binary halftone, colored halftone, and WTS. `gx_get_dc_type_index` and `gx_get_dc_type_from_index` bridge between in-process pointers and command-list codes.

The pure color implementation serializes only the encoded pixel via `gx_dc_write_color` unless a saved device color already matches. `gx_dc_read_color` reconstructs encoded pixels, including the sentinel encoding for `gx_no_color_index` as a single `0xff` byte. The serialization byte width is based on `dev->color_info.depth`.

`gx_complete_halftone` initializes a colored halftone device color by setting its type, halftone pointer, component count, alpha, and active plane mask. `gx_dc_default_fill_masked` is the generic mask renderer: it scans mask rows using bit-run lookup tables and emits one-pixel-high rectangle fills for runs of active bits.

Filesystem relevance: none directly. It is central to Ghostscript's raster drawing path but does not interact with Plan 9 file, block, or VFS interfaces.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdcolor.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdcolor.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdcolor.h

This header defines Ghostscript's internal device color dispatch interface. It introduces `gx_rop_source_t` for RasterOp source data, the `gx_device_color_type_s` method vector, standard device color type symbols, color load/fill macros, and helpers for command-list color serialization.

`gx_rop_source_t` stores source bitmap data, source X offset, raster, bitmap id, optional source colors, and a `use_scolors` flag. The `gx_rop_no_source_body`, `gx_rop_source_set_color`, and `set_rop_no_source` helpers support RasterOp operations that conceptually lack a source operand.

`gx_device_color_type_s` is the key abstraction. Each device color variant provides methods for saving compact state, retrieving a device halftone, returning phase information, loading caches, filling rectangles, filling masks, equality checks, write/read serialization, and identifying non-zero color components for overprint handling.

The header documents command-list serialization semantics in detail: writers can omit repeated colors by comparing against a saved color, readers receive both imager state and prior device color, and halftones are serialized separately as all-band commands because they change infrequently.

The exported standard types are `gx_dc_type_none`, `gx_dc_type_null`, `gx_dc_type_pure`, `gx_dc_type_ht_binary`, `gx_dc_type_ht_colored`, and `gx_dc_type_wts`. It also exports non-zero-component helpers for pure and halftone colors, device-color type-index conversion, and canonical phase methods.

Convenience macros route common operations through the active color type: `gx_color_load`, `gx_device_color_fill_rectangle`, and `gx_fill_rectangle*`. `gx_set_dev_color` triggers `gx_remap_color` when the graphics state's current device color is unset.

Filesystem relevance: none directly. It is a graphics rendering contract within the Ghostscript subtree.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdcolor.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdda.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdda.h

This header implements macro-based Bresenham-style digital differential analyzers used by Ghostscript for trapezoid edges, rotated/skewed image coordinates, curve subdivision, and potentially single-pixel lines. It assumes `gxfixed.h` has supplied fixed-point types.

The comment describes the invariant used to compute exact `floor(i * D / N)` values without letting the remainder leave range. `dda_state_struct` and `dda_step_struct` define state and step layouts; `gx_dda_fixed` combines fixed-point current value `Q` with unsigned remainder `R` and per-step `dQ`, `dR`, `NdR`.

The macro API initializes state and steps (`dda_init_state`, `dda_init_step`, `dda_init`), adds steps (`dda_step_add`), reads the current value (`dda_current`, `dda_current_fixed2int`), steps forward/backward (`dda_next`, `dda_previous`), advances by repeated stepping, and translates the current position.

The implementation explicitly handles negative `D` without depending on compiler-specific signed division/remainder behavior. `dda_advance` is noted as inefficient because it loops one step at a time for the fractional remainder.

Filesystem relevance: none. This is scan-conversion arithmetic for rendering.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdda.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdevbuf.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdevbuf.h

This header defines the buffer-device management procedure table used by printer and banded devices. It includes `gxrplane.h` for render-plane descriptions and forward-declares `gx_device`.

`gx_device_buf_space_t` reports buffer requirements as bit storage size, line pointer storage size, and raster. `gx_device_buf_procs_t` contains four callbacks: `create_buf_device`, `size_buf_device`, `setup_buf_device`, and `destroy_buf_device`.

The callbacks cover creating memory/buffer devices for a page or band, computing required storage, attaching a specific buffer and optional line-pointer area, and destroying the buffer device without freeing the buffered pixel data. The comments note async-device threading constraints: `size_buf_device` may be called by writer or reader, while the other callbacks are reader-thread-only.

The header declares default implementations for all four callbacks.

Filesystem relevance: indirect only. It deals with page/band render buffers in memory, not filesystem buffers or storage block caches.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdevbuf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdevcli.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdevcli.h

This is the primary Ghostscript device-client interface. It defines the `gx_device` object contract, device reference-counting rules, page-device hooks, color model metadata, the complete device procedure vector, image data helpers, forwarding/null device types, and device lifecycle helpers.

The opening documentation is important for memory ownership: device instances are reference-counted, may be marked retained, and must use `gx_device_set_target` rather than direct assignment for forwarding-device targets. It distinguishes dynamically copied devices, local/static instances, and embedded instances, warning that stack/static devices must be retained or initialized with NULL memory.

The auxiliary type section forward-declares graphics state, paths, clipping paths, image enumerators, patterns, and fill/stroke parameters. It defines `gx_drawing_color` as `gx_device_color`, anti-aliasing info, fixed-edge structures, linear-color edge structures, `frac31`, and enums for color separability/linearity, polarity, and overprint mode.

`gx_device_color_info` is the expanded process color model descriptor. It records maximum and active component counts, polarity, encoded depth, gray component index, max/dither levels, anti-aliasing bits, separable/linear encoding data (`comp_shift`, `comp_bits`, `comp_mask`), process color model name, overprint mode, and process component mask. The surrounding macros provide compatibility initializers such as `dci_alpha_values`, `dci_std_color`, `dci_black_and_white`, and process color model name access.

`gx_page_device_procs` supplies page-level install/begin/end hooks. `gx_device_common` defines the common fields of all devices: parameter size, proc records, name, memory/type/finalization fields, reference-count state, open state, fill-band limit, color info/cache, geometry, media, margins, page counters, safety flags, page procedures, and the embedded `gx_device_procs` procedure record.

The device procedure macros declare the full driver API: open/close/sync/output, matrix setup, color mapping, rectangle/tile/copy drawing, bitmap access, parameters, xfont, alpha, banding, RasterOp, path/stroke/mask/trapezoid/parallelogram/triangle/thin-line drawing, image begin/data/end, strip tiling, clipping box, typed images, bits rectangles, compositors, hardware params, text, transparency groups/masks, DeviceN color mapping, pattern management, high-level colors, included color spaces, linear-color fills, and spot equivalent color updates.

`gx_device_proc_struct(dev_t)` expands to the actual procedure-vector layout. The order of members is therefore ABI-like inside this codebase and must match device initializers and default proc filling.

Image handling helpers define `gx_image_plane_t`, wrappers for begin image/typed image, and the modern enumerator-associated data/end functions (`gx_image_data`, `gx_image_plane_data`, `gx_image_plane_data_rows`, `gx_image_flush`, `gx_image_planes_wanted`, `gx_image_end`). Older driver-like wrappers are retained for compatibility.

The bottom of the file defines generic `gx_device`, `gx_device_forward`, and `gx_device_null` structures, GC descriptors, null-device helpers, target setting, retained status management, raster calculation, geometry/resolution/media setters, device switching, closing, local finalization, and an unused `gx_device_type` concept.

Filesystem relevance: none directly. It is a driver/device abstraction for Ghostscript rendering devices, not Plan 9 kernel devices or filesystems.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdevcli.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdevice.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdevice.h

This header is the device-implementor companion to `gxdevcli.h`. It includes the client interface plus file-name, parameter, malloc, and stdio compatibility headers, then provides device initialization macros, default procedure declarations, forwarding procedure declarations, implementation utilities, clipping macros, and media parameter helpers.

The default page-size macros select U.S. Letter or A4 depending on `A4`. The `std_device_part*` and `std_device_*` macro families construct static device initializer bodies while insulating device templates from changes in `gx_device_common`. Variants cover open/closed prototypes, explicit color info, extended DeviceN-style color info, anti-aliasing, standard color-depth-derived models, and margin/offset variants.

The default procedure declarations cover optional device hooks and fallback implementations for mapping, drawing, parameter access, image handling, compositors, text, patterns, high-level color fills, linear-color shadings, and spot equivalent colors. It also declares standard color mapping procedures for black-on-white, white-on-black, grayscale, RGB, CMYK, and 8-bit gray.

Forwarding-device declarations mirror most device procedures, forwarding operations through `gx_device_forward.target`. The header also exposes helpers for filling in procedure tables, forwarding/copying color procedures, checking separable encodings, setting component masks/shifts, and copying color/page parameters from targets.

`gx_device_black`, `gx_device_white`, and inline cache-aware variants are declared here for implementors. Output-file helpers parse and open/close device output file names, including page-number formats.

The clipping macros `fit_fill*` and `fit_copy*` mutate rectangle/copy arguments to clip against device bounds and return early when empty. Copy clipping also adjusts source data pointers, source X offsets, raster-derived row offsets, and bitmap ids.

The media parameter section defines `gdev_input_media_t` and `gdev_output_media_t` plus routines to emit InputAttributes/OutputAttributes dictionaries.

Filesystem relevance: slight user-space file I/O relevance through output-file open/close helpers, but no filesystem implementation logic. Its main role is Ghostscript rendering-device implementation support.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdevice.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdevmem.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdevmem.h

This header defines Ghostscript memory devices: in-memory bitmap-backed devices used for mono, mapped-color, RGB/CMYK, planar, alpha, and band-buffer rendering. It requires `gxdevice.h` and includes `gxrplane.h`.

The introductory documentation enumerates four storage ownership models: device-allocated bitmap plus line pointers, client-provided bitmap with allocated line pointers, allocated line pointers with later caller setup, and fully caller-managed bitmap/line pointers. It also explains GC tracing flags for foreign bits and foreign line-pointer storage.

`gx_device_memory` subclasses `gx_device_forward_common` and adds raster, base pointer, bitmap allocator, line-pointer allocator, foreign-storage flags, planar metadata, initial matrix, line pointer table, palette, cached packed-color values for 24/40/48/56/64-bit formats, alpha-buffer mapping state, and planar depth.

`mem_device_init_private` is the initializer fragment for memory-device-specific fields. The public structure descriptor accounts for the forwarding target plus memory-device pointers.

The API computes required storage (`gdev_mem_bits_size`, `gdev_mem_line_ptrs_size`, `gdev_mem_data_size`, `gdev_mem_bitmap_size`), derives maximum height from a buffer size (`gdev_mem_max_height`), calculates raster via `gx_device_raster`, selects prototype memory devices by bit depth, creates mono/general/alpha memory devices, opens partial scan-line sets for banding, sets scan-line pointers, controls monobit polarity, and tests whether a device is memory or alpha-buffering.

Filesystem relevance: indirect only. This is an in-memory raster device and band buffer abstraction, not persistent storage or filesystem page cache code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdevmem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdevndi.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdevndi.c

This file implements DeviceN halftone rendering helpers. It converts fractional process-color components into Ghostscript device colors, choosing between pure encoded colors, colored halftones, binary halftones, and WTS device colors.

The file defines fractional lookup tables `q0` through `q7` and exports `fc_color_quo`, used by the fractional color macro in `gzht.h` for fast conversion of small denominators.

`gx_render_device_DeviceN_wts` is the WTS-specific constructor. It initializes a WTS device color, stores the halftone pointer, copies fractional levels, and builds a `plane_vector` by encoding one-max-component colors through the device's `encode_color` procedure. For non-separable/non-linear encodings it also samples the zero-vector case for monochrome inversion.

`gx_render_device_DeviceN` is the main DeviceN renderer. It computes per-component maximum dither values from `dev->color_info`, converts each fractional input into an integer base color and halftone level, and tracks whether dithering is needed. If no component needs dithering, it encodes and returns a pure color. Otherwise it sets per-component colored-halftone state, completes the halftone with `gx_complete_halftone`, applies halftone phase modulo the halftone LCM dimensions, and reduces single-plane cases.

`gx_devn_reduce_colored_halftone` handles colored halftones with zero or one active varying component. Zero active planes become a pure color. One active plane becomes a binary halftone with a base and next color; subtractive devices invert both level and color pair to account for additive halftone orders.

Filesystem relevance: none. This is raster color/halftone rendering code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdevndi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdevndi.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdevndi.h

This header declares the interface to DeviceN halftoning support in `gxdevndi.c`. It includes `gxfrac.h`, forward-declares `gx_device_halftone`, and declares `gx_render_device_color_devn`.

The declared function accepts fractional red/green/blue/white values, a CMYK flag, alpha, target `gx_device_color`, target device, device halftone, and halftone phase. The comment says it renders a color possibly by halftoning and returns like `gx_render_[device_]gray`.

Note: the C file in this group implements `gx_render_device_DeviceN`, while this header exposes `gx_render_device_color_devn`; the latter is likely implemented elsewhere in the same Ghostscript source tree and delegates into DeviceN rendering.

Filesystem relevance: none. It is a graphics color-rendering interface.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdevndi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdevrop.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdevrop.h

This tiny header extends the device interface for RasterOp support by declaring unaligned implementations of `copy_rop` and `strip_copy_rop`.

It relies on the `dev_proc_copy_rop` and `dev_proc_strip_copy_rop` macros from the device headers. The two declarations are `gx_copy_rop_unaligned` and `gx_strip_copy_rop_unaligned`.

Filesystem relevance: none. This is raster-compositing support.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdevrop.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdht.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdht.h

This header defines Ghostscript device halftone data structures: halftone cell geometry, whitening orders, order procedure vectors, order storage, order components, and full device halftones.

The opening comment explains the halftone tile model in detail: rational basic cells, multi-cells, rectangular super-cells, physical pixel aspect ratio, frequency/angle conversion, and shifted strip decomposition to avoid materializing very large full super-cells.

`gx_ht_cell_params_t` stores defining rational cell parameters (`M`, `N`, `R`, `M1`, `N1`, `R1`) and derived values (`C`, `D`, `D1`, `W`, `W1`, `S`). `gx_compute_cell_values` fills the derived fields.

Whitening order representation consists of a `levels` array plus `bit_data`. The default bit-data form uses `gx_ht_bit` offset/mask entries, while a short representation is also supported through `ht_order_procs_table`. `ht_sample_t` and `max_ht_sample` are used during sampling.

`gx_ht_order_procs_t` abstracts order implementations with element size, threshold-array construction, bit-index lookup, tile rendering, and a tentative draw method. `gx_ht_order` stores cell params, optional WTS data, dimensions, strip shift/original fields, full height, level/bit counts, procs, allocation memory, levels, bit_data, cache, transfer map, and spot-screen sampling parameters.

`ht_order_is_complete` and `ht_order_full_height` distinguish complete orders from shifted strip orders. GC descriptor macros expose `st_ht_order` and component descriptors.

`gx_device_halftone` contains a primary `gx_ht_order`, reference count, id, halftone type, optional component array, component counts, and LCM tile dimensions. Multi-component halftones parallel process color components and are required for color screens and Type 5 halftones.

The header declares `gx_ht_complete_threshold_order` and `gx_device_halftone_release`.

Filesystem relevance: none. It is graphics halftone model/state.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdht.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdhtres.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdhtres.h

This header defines the static resource descriptor used for precompiled halftones generated by Ghostscript's `genht` tool.

`gx_device_halftone_resource_t` stores a resource name, halftone type, width, height, number of levels, pointers to the levels and bit-data arrays, and bit-data element size. The `DEVICE_HALFTONE_RESOURCE_PROC` macro declares functions that return NULL-terminated arrays of resource pointers.

`gxdhtserial.c` uses this resource interface to compare deserialized halftone orders against resident ROM/static halftones and substitute the resident arrays when they match.

Filesystem relevance: none. It describes compiled-in rendering resources.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdhtres.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdhtserial.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdhtserial.c

This file serializes and deserializes traditional Ghostscript device halftones for command-list transmission. It covers transfer maps, halftone order components, complete multi-component device halftones, and read-and-install behavior on the renderer side.

`gx_ht_write_tf` serializes an optional transfer function as one byte for absent or identity maps, or as a type byte plus the full transfer value array for complete mapped transfers. `gx_ht_read_tf` reconstructs a transfer map, allocating `gx_transfer_map`, assigning a new id, initializing identity or mapped procedures, and returning bytes consumed.

`gx_ht_write_component` serializes one `gx_ht_order_component`, but only the order data needed by a renderer. It rejects WTS orders as unsupported for this serializer. It omits construction-only or renderer-local fields such as cell params, WTS enum data, raster, original height/shift, full height, allocation memory, cache, and screen params. It writes order type, width, height, shift, level count, bit count, procs-table index, levels array, bit-data array, and transfer function.

`gx_ht_read_component` reverses that format. It validates the traditional order type, decodes dimensions/counts/procs, allocates levels and bit data with `gx_ht_alloc_ht_order`, clears historical params/screen fields, copies serialized arrays, reads the transfer function, then searches resident halftone resources for matching levels and bit data. On a match it frees the newly allocated arrays and points at the resident resource arrays.

`gx_ht_write` serializes a full device halftone. It asserts a component-array-based halftone, writes the halftone type and number of device components, then serializes each component. It intentionally does not transmit reference count, id, primary `order`, or LCM dimensions because those are recreated or ignored by the reader.

`gx_ht_read_and_install` reads the serialized type and components into a stack `gx_device_halftone`, installs it through `gx_imager_dev_ht_install`, and releases allocated component orders on failure. Combining read and install avoids heap-allocating a full halftone object just to install and discard it.

Filesystem relevance: indirect only. This is command-list serialization for rendering state, not filesystem serialization or storage format code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdhtserial.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdhtserial.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdhtserial.h

This header declares the public interface for traditional halftone serialization and deserialization/installation.

It forward-declares `gs_memory_t`, `gx_device`, `gx_device_halftone`, and `gs_imager_state`. `gx_ht_write` serializes a `gx_device_halftone` for a given device into a caller-provided buffer, updating the size with either bytes used or bytes required. `gx_ht_read_and_install` reconstructs a halftone from serialized bytes and installs it into an imager state for a given device and allocator.

The comments document return conventions: `0` for successful write, `gs_error_rangecheck` when the buffer is too small, other errors without size mutation, and byte count or negative error for read/install.

Filesystem relevance: none directly. It is rendering command-list state serialization.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdhtserial.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdither.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdither.h

This header declares DeviceN dithering/halftoning functions implemented in `gxdevndi.c`. It includes `gxfrac.h` and forward-declares `gx_device_halftone`.

`gx_render_device_DeviceN` renders an array of fractional process color values into a `gx_device_color`, possibly using a device halftone and phase. `gx_devn_reduce_colored_halftone` reduces a colored halftone with zero or one varying planes to either a pure color or a binary halftone.

Filesystem relevance: none. It is raster color rendering support.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdither.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdtfill.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdtfill.h

This header is a configurable trapezoid-fill algorithm intended to be included multiple times with different macro settings. It is not a conventional declaration header; it expands into a concrete `GX_FILL_TRAPEZOID` function based on configuration macros such as `CONTIGUOUS_FILL`, `SWAP_AXES`, `FILL_DIRECT`, `LINEAR_COLOR`, `EDGE_TYPE`, and `FILL_ATTRS`.

The long comment specifies PostScript scan conversion rules for pixels whose centers fall inside trapezoid edges, the behavior difference when contiguous fill is enabled, and the rational-floor math used to avoid off-by-one errors around half-pixel boundaries and fixed-point epsilon.

The generated function computes sampled Y bounds, initializes left and right `trap_line` edge walkers, handles vertical-edge rectangle fast paths for non-linear colors, computes `dx/dy` using overflow-aware quotient helpers, and iterates scanline spans. For ordinary fills it batches consecutive scanlines with identical left/right integer bounds into taller rectangles. For linear-color fills it computes per-scanline gradients and delegates to the device `fill_linear_color_scanline` proc.

The contiguous-fill mode can widen dropout-prone narrow spans and connect adjacent rectangles to keep filled regions contiguous, while avoiding extra peak pixels when flags indicate peaks.

The implementation uses device color fill indirection or direct device `fill_rectangle` depending on `FILL_DIRECT`, supports swapped axes, emits visual debugging rectangles under debugging macros, checks interrupts before returning, and undefines its configuration/helper macros at the end.

Filesystem relevance: none. It is scan conversion/rasterization logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdtfill.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfapi.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfapi.c

This file provides UFST font API callback dispatch support. It includes Ghostscript base headers and UFST headers, then defines callback stubs and mutable callback function pointers.

The three callbacks are `PCLEO_charptr`, `PCLchId2ptr`, and `PCLglyphID2Ptr`. By default they dispatch to private stubs returning NULL. `gx_set_UFST_Callbacks` installs caller-provided callback functions, and `gx_reset_UFST_Callbacks` restores the NULL stubs.

The comments note the callback pointers are static until graphics-library reentrancy and UFST callback reentrancy are fixed. That means this dispatcher is global process state rather than per-context state.

Filesystem relevance: none. It is font callback plumbing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfapi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfapi.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfapi.h

This small header declares the UFST callback installation/reset functions implemented by `gxfapi.c`.

`gx_set_UFST_Callbacks` accepts function pointers for `PCLEO_charptr`, `PCLchId2ptr`, and `PCLglyphID2Ptr`. `gx_reset_UFST_Callbacks` restores default callbacks. The types (`LPUB8`, `UW16`, `IF_STATE`) come from the UFST headers included by users of this header.

Filesystem relevance: none. It is font API integration.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfapi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfarith.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfarith.h

This header supplies floating-point arithmetic helpers and optimized comparison macros for platforms with slow or absent FPUs. It includes `gconfigv.h` for `USE_FPU` and `gxarith.h`.

When `USE_FPU <= 0`, floats are IEEE, and float size matches integer or long size, the header redefines selected `gxarith.h` macros to inspect float/double bit patterns. Optimized macros include `is_fzero`, `is_fzero2`, `is_fneg`, `is_fge1`, `f_fits_in_ubits`, and `f_fits_in_bits`. They handle sign bits, zero representations, exponent masks, and integer-bit-fit tests without conventional floating comparisons where possible.

The header also declares degree-based trigonometric helpers: `gs_sin_degrees`, `gs_cos_degrees`, `gs_sincos_degrees`, and `gs_atan2_degrees`. `gs_sincos_t` records sine, cosine, and whether the angle is orthogonal. The degree functions are intended to hit exact values at multiples of 90 degrees and follow PostScript quadrant behavior for atan2.

Filesystem relevance: none. It is math support for rendering geometry.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfarith.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfcache.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfcache.h

This header defines Ghostscript font/matrix and character cache structures plus font-directory cache management APIs. It depends on font identity, xfont, bitmap cache, fixed-point, and font-type headers.

`cached_fm_pair` is the cached font/matrix pair key. It stores a base font pointer, UID/XUID, font type, stable hash, transformation matrix components, cached-character count, xfont lookup state and result, allocator, index in the matrix-pair array, TrueType interpreter state, and design-grid flag. Entries can remain after a restore if they have valid UIDs; free entries are represented by NULL font plus invalid UID.

`fm_pair_cache` manages the array of cached font/matrix pairs with size/max and rover allocation index.

`cached_char` subclasses the general cached-bits header. Its key includes glyph code, font/matrix pair, writing mode, and depth; value fields include bitmap metadata from the common header, xfont glyph id, device width, and offset. The header documents the invariant that every real entry must have either bitmap bits or a valid xfont glyph backed by an xfont.

Cached characters are allocated inside cache chunks, not as standalone GC objects. The header explains that pointers from the cache are traced/relocated when the owning font directory is traced, with special descriptors for cached-char pointers.

`char_cache` stores bitmap-cache common fields, struct/bits allocators, open-addressing hash table, size limits, compression thresholds, and optional glyph marking callback.

`gs_font_dir` is the font directory/cache manager. It owns original/scaled font lists, the font/matrix pair cache, character cache, GC enumeration state, `AlignToPixels`, glyph-to-Unicode data, extension allocator, TrueType interpreter, `GridFitTT`, spot analyzer, and optional global glyph-code callback.

The procedure declarations allocate/init caches, purge selected cached chars, compute character matrices and cache keys, look up/add font/matrix pairs, look up xfonts, purge one pair, and purge a font from character caches.

Filesystem relevance: none. It is in-memory font/glyph cache infrastructure.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfcache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfcid.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfcid.h

This header defines internal structures and procedures for CID-keyed fonts in Ghostscript. It includes CID system info, base font, and Type 42 font headers.

`gs_font_cid_data` is common to CIDFontType 0 and 2: `CIDSystemInfo`, `CIDCount`, and optional `GDBytes` for standard glyph data. GC descriptor macros build on `st_cid_system_info`.

CIDFontType 0 (`gs_font_cid0`) stores common CID data plus `CIDMapOffset`, an FDArray of partial Type 1 fonts, FDArray size, `FDBytes`, a `glyph_data` callback that can return glyph data and/or font number, and callback private data.

CIDFontType 1 (`gs_font_cid1`) is minimal, carrying base font common data plus `CIDSystemInfo`.

CIDFontType 2 (`gs_font_cid2`) subclasses Type 42. It stores common CID data, `MetricsCount`, a `CIDMap_proc`, and saved original Type 42 outline/metrics procedures so wrappers can account for CID-specific metrics behavior.

The header declares `gs_font_cid_system_info`, a simple CIDFontType 0 glyph enumerator, CIDSystemInfo compatibility checking, FDArray indexed-font lookup, and a predicate for whether a CID font has a Type 2 subfont.

Filesystem relevance: none. This is font representation code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfcid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfcmap.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfcmap.h

This header defines Ghostscript's internal, representation-neutral CMap structures. CMaps map variable-length input character codes to font-specific glyph spaces such as CIDs. The file notes it would be named `gxcmap.h`, but that name is already used.

The code-space model uses sorted, non-overlapping `gx_code_space_range_t` ranges with 1 to 4 bytes (`MAX_CMAP_CODE_SIZE`). Lookup entries can represent single keys or key ranges and map to CIDs, glyphs, character strings, or notdef CIDs. `CODE_VALUE_CID` range entries increment results by input-code offset, while `CODE_VALUE_NOTDEF` does not.

`GS_CMAP_COMMON` defines shared CMap fields: `CMapType`, internal id, name, per-font CIDSystemInfo array, font count, version, UID/XUID, UIDOffset, writing mode, Unicode/ToUnicode flags, glyph-name callback/data, and a `gs_cmap_procs_t` virtual procedure table.

`gs_cmap_procs_t` abstracts decoding, code-space enumeration, lookup enumeration, and identity checking so Adobe CMaps and TrueType cmap-backed implementations can share the same higher-level interface.

The header defines enumeration state for code-space ranges and lookup tables. Range enumeration returns one `gx_code_space_range_t` at a time. Lookup enumeration separates lookup-level metadata (`key_size`, range flag, value type, font index) from entry-level key/value data, and may use temporary storage for values that do not survive across calls.

Client procedures initialize and advance range/lookup enumerators. Implementation procedures initialize common CMap fields, allocate a CMap, set up enumerators, check identity using fast paths, and compute identity generically.

Filesystem relevance: none. It is font/text mapping infrastructure.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfcmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfcmap1.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfcmap1.h

This header defines the concrete Adobe CMapType 1/2 implementation subclass for the generic CMap interface in `gxfcmap.h`.

The design separates each map into a key map and a value table, allowing related large CMaps to potentially share value tables while using different code spaces or key maps.

`gx_cmap_lookup_range_t` stores one lookup range: back pointer to the owning Adobe CMap, entry count, shared key prefix, key size, range flag, packed keys, value type, value size, packed values, and font index. GC descriptors are complex because lookup ranges may reference names that need marking.

`gx_code_space_t` owns an array of code-space ranges. `gx_code_map_t` owns an array of lookup ranges. `gs_cmap_adobe1_t` embeds `GS_CMAP_COMMON`, then adds code space, defined-character map, notdef map, glyph marking callback, and callback data.

`gs_cmap_adobe1_alloc` allocates and initializes an Adobe1 CMap with requested counts and packed key/value storage sizes; the caller still fills code ranges, lookup tables, keys, and values.

Filesystem relevance: none. It is concrete font CMap mapping data.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfcmap1.h -->