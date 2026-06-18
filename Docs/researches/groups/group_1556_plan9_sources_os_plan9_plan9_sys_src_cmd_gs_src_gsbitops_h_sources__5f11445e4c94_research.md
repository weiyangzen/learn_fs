# Group Research: group_1556_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_gsbitops_h_sources__5f11445e4c94

Scope confirmed against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/plan9`, which is included in subset A. This group is a Ghostscript graphics/text/color support slice inside the Plan 9 source tree, not Plan 9 kernel or filesystem logic.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsbitops.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsbitops.h

Header defining Ghostscript bitmap and packed-sample bit manipulation interfaces.

Key contents:
- Provides macros for loading and storing packed sample values at 1, 2, 4, 8, 12, 16, 24, 32, and up to 64 bits per value.
- Uses big-endian bit numbering within bytes for setup semantics, with `sample_next` advancing a byte pointer plus bit offset.
- Defines store-side helpers for preloading/flushing partial destination bytes.
- Defines `mono_fill_chunk`, `mono_fill_chunk_bytes`, and `mono_fill_make_pattern` for monobit rectangle fills.
- Declares rectangle/plane operations:
  - `bits_fill_rectangle`
  - `bits_fill_rectangle_masked`
  - `bits_replicate_horizontally`
  - `bits_replicate_vertically`
  - `bits_bounding_box`
  - `bits_compress_scaled`
  - `bits_extract_plane`
  - `bits_expand_plane`
  - `bytes_fill_rectangle`
  - `bytes_copy_rectangle`
- Defines `bits_plane_t`, which describes aligned source/destination bit planes with data pointer, raster, depth, and starting x offset.

Important implementation notes:
- The load/store macros expand into switch statements and are intended for performance-sensitive inner loops.
- Invalid sample depths return `gs_error_rangecheck` through `sample_end_`, so callers must use the macros in functions where `return_error` is available.
- 64-bit sample helpers use `gx_color_index` and `sample_bound_shift` to avoid compiler warnings or undefined shifts on narrower integer types.
- This is an interface-only file; implementations are elsewhere in Ghostscript bit operation sources.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsbitops.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsbittab.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsbittab.c

Defines constant byte lookup tables used by Ghostscript bit operations.

Key contents:
- Includes `stdpre.h` and `gsbittab.h`.
- Defines `byte_reverse_bits[256]` using `bit_table_8`.
- Defines `byte_right_mask[9]` for trailing-bit masks from 0 through 8 bits.
- Defines `byte_count_bits[256]` for population count of each byte.
- Defines `byte_bit_run_length_0` through `_7`, each indexed by byte value and representing run length of 1 bits starting at a bit position.
- Defines pointer tables:
  - `byte_bit_run_length[8]`
  - `byte_bit_run_length_neg[8]`
- Defines `byte_acegbdfh_to_abcdefgh[256]`, a bit-lane permutation table.
- Ends with `gsbittab_dummy()` for compilers that require executable code in each compilation unit.

Important implementation notes:
- The tables are generated through C macros rather than handwritten 256-entry literals.
- Run-length tables encode continuation by adding 8 when the run reaches the low-order bit and may continue into the next byte.
- This file supplies shared static lookup data for low-level bitmap scanning and transformation code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsbittab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsbittab.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsbittab.h

Header for byte-level bit operation lookup tables.

Key contents:
- Defines table-expansion macros:
  - `bit_table_2`
  - `bit_table_4`
  - `bit_table_6`
  - `bit_table_8`
- Declares externally defined tables from `gsbittab.c`:
  - `byte_reverse_bits`
  - `byte_right_mask`
  - `byte_count_bits`
  - `byte_bit_run_length_0` through `_7`
  - `byte_bit_run_length`
  - `byte_bit_run_length_neg`
  - `byte_acegbdfh_to_abcdefgh`

Important implementation notes:
- The table macros compose smaller bit combinations into larger 2/4/6/8-bit transformation tables.
- The run-length table contract is documented here and mirrored by the implementation.
- Consumers depend on `byte` being available from prior Ghostscript base headers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsbittab.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsccode.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsccode.h

Defines Ghostscript character-code and glyph-code types and encoding indices.

Key contents:
- Defines `gs_char` as `ulong`, with `GS_NO_CHAR`/`gs_no_char`.
- Defines `gs_glyph` as `ulong`, with reserved numeric regions for:
  - no glyph / unknown glyph
  - global named glyphs
  - built-in encoding private glyphs
  - CIDs
  - glyph indices
- Defines boundaries:
  - `GS_NO_GLYPH`
  - `GS_MIN_CID_GLYPH`
  - `GS_MIN_GLYPH_INDEX`
  - `GS_GLYPH_TAG`
  - `GS_MAX_GLYPH`
- Defines `gs_glyph_mark_proc_t` for GC marking.
- Defines `gs_encoding_index_t` for 11 known encodings:
  - 7 real encodings: Standard, ISOLatin1, Symbol, Dingbats, WinAnsi, MacRoman, MacExpert
  - 4 pseudo/glyph-set encodings: MacGlyph, Adobe Latin Original, Adobe Latin Extended, CFF StandardStrings
- Defines `KNOWN_REAL_ENCODING_NAMES`.
- Defines `gs_glyph_space_t` for name/index/no-generation glyph selection.
- Defines `gs_glyph_name_proc_t`.

Important implementation notes:
- The header establishes the namespace contract used by `gscencs.[ch]` and generated encoding tables.
- Built-in encoding glyphs live below CID glyph values but in a private reserved range.
- Composite fonts require character codes to be at least 32 bits; this is why `gs_char` is not simply `byte`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsccode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsccolor.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsccolor.h

Defines the client-facing Ghostscript color value structure.

Key contents:
- Includes `gsstype.h` for structure descriptor support.
- Forward-declares `gs_pattern_instance_t`.
- Defines `GS_CLIENT_COLOR_MAX_COMPONENTS` as 16.
- Defines `gs_paint_color` as an array of up to 16 float component values.
- Defines `gs_client_color` as:
  - paint values, also used for uncolored patterns
  - optional pattern instance pointer
- Declares the GC structure descriptor `st_client_color`.
- Defines `public_st_client_color()` and `st_client_color_max_ptrs`.

Important implementation notes:
- The 16-component maximum supports DeviceN-style color spaces beyond CMYK, including hexachrome and other multi-colorant devices.
- Pattern ownership is visible to Ghostscript GC through the structure descriptor.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsccolor.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscdef.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscdef.c

Defines Ghostscript build/configuration scalar values.

Key contents:
- Includes `std.h`, `gscdefs.h`, and generated/config header `gconfigd.h`.
- Defines `gs_buildtime`, defaulting to `0` unless `GS_BUILDTIME` is supplied.
- Defines copyright, product family, and product strings:
  - `gs_copyright`
  - `gs_productfamily`
  - `gs_product`
- Provides `gs_program_name()`.
- Defines `gs_revision` from required makefile macro `GS_REVISION`.
- Provides `gs_revision_number()`.
- Defines `gs_revisiondate` from required makefile macro `GS_REVISIONDATE`.
- Defines `gs_serialnumber`, defaulting to `42` unless configured.
- Defines installation strings:
  - `gs_doc_directory`
  - `gs_lib_default_path`
  - `gs_init_file`

Important implementation notes:
- Uses `CONFIG_CONST`, controlled by `gscdefs.h`, to optionally make system constants writable for applications that require it.
- This file is build-configuration glue, not runtime algorithmic code.
- In this checkout, `gscdef.c` and `gscdefs.c` have identical contents.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscdef.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscdefs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscdefs.c

Duplicate configuration-scalar source matching `gscdef.c` in this tree.

Key contents:
- Includes `std.h`, `gscdefs.h`, and `gconfigd.h`.
- Defines the same build metadata, product strings, revision values, serial number, library path, documentation path, and init-file name as `gscdef.c`.
- Provides the same functions:
  - `gs_program_name()`
  - `gs_revision_number()`

Important implementation notes:
- The file body is identical to `gscdef.c` in the inspected Plan 9 Ghostscript snapshot, including the `$Id` line naming `gscdef.c`.
- This likely exists for build-system naming compatibility or historical source layout reasons.
- Treat as duplicate configuration definition code; linking both objects into one binary would normally create duplicate symbols unless the build chooses only one.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscdefs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscdefs.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscdefs.h

Declares Ghostscript configuration constants and resource-table access macros.

Key contents:
- Includes `gconfigv.h`.
- Defines `CONFIG_CONST` based on `SYSTEM_CONSTANTS_ARE_WRITABLE`.
- Declares exported configuration constants:
  - build time
  - copyright
  - product/product family
  - revision and revision date
  - serial number
  - documentation directory
  - default library path
  - initialization file
- Provides macros to declare resource tables without importing all dependent types:
  - `extern_gx_device_halftone_list`
  - `extern_gx_image_class_table`
  - `extern_gx_image_type_table`
  - `extern_gx_init_table`
  - `extern_gx_io_device_table`
  - `extern_gs_lib_device_list`
  - `extern_gs_find_compositor`
- Declares count variables for image class/type tables and IO devices.

Important implementation notes:
- The file intentionally avoids depending on Ghostscript base types directly in processed declarations because it may be included before `stdpre.h`.
- The extern macros defer type requirements to users that already have the corresponding type definitions in scope.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscdefs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscdevn.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscdevn.c

Implements Ghostscript DeviceN color space behavior.

Key contents:
- Includes Ghostscript memory, color-space, function, graphics-state, device, overprint, and stream headers.
- Defines GC descriptors for `gs_color_space_DeviceN` and `gs_device_n_map`.
- Defines `gs_color_space_type_DeviceN`, wiring DeviceN callbacks:
  - component count
  - alternate space access
  - color initialization/restriction
  - concrete-space selection
  - concretization
  - concrete color remapping
  - install
  - overprint setup
  - reference-count adjustment
  - serialization
- Public construction/helpers:
  - `gs_build_DeviceN`
  - `gs_cspace_build_DeviceN`
  - `alloc_device_n_map`
  - `using_alt_color_space`
  - `map_devn_using_function`
  - `gs_cspace_set_devn_function`
  - `gs_cspace_get_devn_function`
  - `gx_serialize_device_n_map`
- Disabled block contains an unused direct-procedure tint-transform setter, `gs_cspace_set_devn_proc`, not supported by serialization.

Behavior:
- `gs_build_DeviceN` validates that the alternate color space can be used as an alternate space, allocates the DeviceN map, allocates component-name storage, and stores component count.
- `gs_cspace_set_devn_function` validates function arity: input count must match DeviceN components, output count must match alternate-space component count.
- `gx_init_DeviceN` initializes all DeviceN component values to `1.0`.
- `gx_restrict_DeviceN` clamps components into `[0, 1]`.
- `gx_concrete_space_DeviceN` returns the alternate concrete space when `use_alt_cspace` is active; otherwise DeviceN is treated as concrete.
- `gx_concretize_DeviceN` either:
  - runs the tint transform and concretizes through the alternate color space, with a one-entry cache check, or
  - maps DeviceN component floats directly to fractional values when not using alternate space.
- `check_DeviceN_component_names` compares DeviceN component names with device colorant names, handles `/None`, rejects duplicated non-`None` names, and decides whether the alternate color space must be used.
- Additive devices always use the alternate color space.
- `gx_install_DeviceN` installs the color space and lets the device update equivalent spot colors.
- `gx_set_overprint_DeviceN` either delegates overprint to the alternate color space or computes drawn DeviceN components.
- Serialization only supports maps whose tint transform is `map_devn_using_function`; arbitrary procedure transforms return `gs_error_unregistered`.

Important implementation notes:
- DeviceN behavior is tightly coupled to `gs_devicen_color_map` in the graphics state and to device colorant-name lookup.
- As written in this snapshot, `gs_cspace_build_DeviceN` initializes `gs_device_n_params *pcsdevn = 0` and then calls `gs_cspace_init_from((gs_color_space *)&pcsdevn->alt_space, palt_cspace)` without assigning `pcsdevn = &pcspace->params.device_n`; this appears to be a null-pointer bug in the checked-in source.
- The comment in `gs_build_DeviceN` repeats “color names list” for both map and names allocation; the first is actually map allocation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscdevn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscdevn.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscdevn.h

Client interface for Ghostscript DeviceN color spaces.

Key contents:
- Includes `gscspace.h`.
- Declares:
  - `gs_build_DeviceN`
  - `gs_cspace_build_DeviceN`
  - `gs_cspace_set_devn_proc`
  - `gs_cspace_set_devn_function`
  - `gs_cspace_get_devn_function`
  - `map_devn_using_function`
  - `gx_serialize_device_n_map`
- Forward-declares `gs_function_t` when needed.

Important implementation notes:
- The header advertises `gs_cspace_set_devn_proc`, but the implementation in `gscdevn.c` is under `#if 0`; clients expecting that symbol may fail unless another implementation exists.
- The comments state that clients own tint-transform function memory management.
- Procedure-name comment notes VMS/old-system symbol-length constraints.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscdevn.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscedata.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscedata.c

Generated compact data tables for Ghostscript built-in encodings.

Generation/source:
- Generated mechanically by `toolbin/encs2c.ps`.
- Source encoding files listed in the header include:
  - `gs_std_e.ps`
  - `gs_il1_e.ps`
  - `gs_sym_e.ps`
  - `gs_dbt_e.ps`
  - `gs_wan_e.ps`
  - `gs_mro_e.ps`
  - `gs_mex_e.ps`
  - `gs_mgl_e.ps`
  - `gs_lgo_e.ps`
  - `gs_lgx_e.ps`
  - `gs_css_e.ps`
- Includes `stdpre.h`, `gstypes.h`, and `gscedata.h`.

Key data:
- `gs_c_known_encoding_chars[]`: packed sorted glyph-name character storage.
- `gs_c_known_encoding_total_chars = 5483`.
- `gs_c_known_encoding_max_length = 19`.
- `gs_c_known_encoding_offsets[]`: offset table by glyph-name length.
- `gs_c_known_encoding_count = 11`.
- Per-encoding forward tables:
  - `gs_c_known_encoding_0`: StandardEncoding, length 256
  - `gs_c_known_encoding_1`: ISOLatin1Encoding, length 256
  - `gs_c_known_encoding_2`: SymbolEncoding, length 256
  - `gs_c_known_encoding_3`: DingbatsEncoding, length 256
  - `gs_c_known_encoding_4`: WinAnsiEncoding, length 256
  - `gs_c_known_encoding_5`: MacRomanEncoding, length 256
  - `gs_c_known_encoding_6`: MacExpertEncoding, length 256
  - `gs_c_known_encoding_7`: MacGlyphEncoding, length 258
  - `gs_c_known_encoding_8`: AdobeLatinOriginalGlyphEncoding, length 229
  - `gs_c_known_encoding_9`: AdobeLatinExtensionGlyphEncoding, length 86
  - `gs_c_known_encoding_10`: CFFStandardStrings, length 379
- Per-encoding reverse lookup tables:
  - reverse lengths are 149, 205, 189, 188, 224, 208, 165, 257, 228, 86, and 378.
- Publishes pointer vectors:
  - `gs_c_known_encodings[]`
  - `gs_c_known_encodings_reverse[]`
- Publishes length vectors:
  - `gs_c_known_encoding_lengths[]`
  - `gs_c_known_encoding_reverse_lengths[]`

Important implementation notes:
- Values are encoded with `N(len, offset)`, defined in `gscedata.h`, packing a glyph-name length and offset into a `ushort`.
- Forward encoding tables map character codes to packed glyph-name identifiers.
- Reverse tables map sorted glyph identifiers back to character codes for binary-search decode in `gscencs.c`.
- This file is pure generated data; manual edits should be avoided unless the generator and source encoding files are updated consistently.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscedata.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscedata.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscedata.h

Internal interface for generated built-in encoding data.

Key contents:
- Documents that the data is generated by `toolbin/encs2c.ps`.
- Defines packed-name encoding helpers:
  - `NUM_LEN_BITS = 5`
  - `N(len, offset)`
  - `N_LEN(e)`
  - `N_OFFSET(e)`
- Declares generated data symbols:
  - `gs_c_known_encoding_chars`
  - `gs_c_known_encoding_total_chars`
  - `gs_c_known_encoding_max_length`
  - `gs_c_known_encoding_offsets`
  - `gs_c_known_encoding_count`
  - `gs_c_known_encodings`
  - `gs_c_known_encodings_reverse`
  - `gs_c_known_encoding_lengths`
  - `gs_c_known_encoding_reverse_lengths`

Important implementation notes:
- Five bits are reserved for glyph-name length, allowing lengths up to 31; this generated dataset’s max is 19.
- The header is consumed by `gscencs.c` to encode/decode known encoding glyphs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscedata.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscencs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscencs.c

Implements the compact built-in encoding API over generated tables from `gscedata.c`.

Key contents:
- Includes `memory_.h`, `gscedata.h`, `gscencs.h`, `gserror.h`, and `gserrors.h`.
- Defines `gs_c_min_std_encoding_glyph = gs_min_cid_glyph - 0x10000`.
- Implements:
  - `gs_c_known_encode`
  - `gs_c_decode`
  - `gs_c_glyph_name`
  - `gs_is_c_glyph_name`
  - `gs_c_name_glyph`
- Contains optional `#ifdef TEST` standalone test code.

Behavior:
- `gs_c_known_encode(ch, ei)` validates encoding index and character range, then returns the private glyph code by adding `gs_c_min_std_encoding_glyph` to the encoded table value.
- `gs_c_decode(glyph, ei)` binary-searches the reverse table for a glyph and returns the matching character code or `GS_NO_CHAR`.
- `gs_c_glyph_name(glyph, pstr)` unpacks `N_LEN`/`N_OFFSET`, then points `pstr` directly into `gs_c_known_encoding_chars`.
- `gs_is_c_glyph_name(str, len)` checks whether the pointer lies inside the generated character table; it does not verify the exact length argument.
- `gs_c_name_glyph(str, len)` binary-searches the packed character-name table for a given name and returns the corresponding private glyph code or `gs_no_glyph`.

Important implementation notes:
- Encoding glyph numbers from this API are private and only meant for the paired APIs in this file.
- Reverse lookup assumes reverse tables are sorted by glyph value.
- The optional test uses fixed expected `N(len, offset)` values, so it must be updated if regenerated table layout changes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscencs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscencs.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscencs.h

Public interface to compact C representations of built-in Ghostscript encodings.

Key contents:
- Includes `stdpre.h`, `gstypes.h`, and `gsccode.h`.
- Documents that `gscedata.c` is generated by `encs2c.ps` and must stay synchronized with this header and `gscencs.c`.
- Declares `gs_c_min_std_encoding_glyph`.
- Declares:
  - `gs_c_known_encode`
  - `gs_c_decode`
  - `gs_c_glyph_name`
  - `gs_is_c_glyph_name`
  - `gs_c_name_glyph`

Important implementation notes:
- The header states this representation was used by `pdfwrite`, though the PostScript interpreter could also use it.
- The returned glyph numbering is private to the built-in encoding subsystem.
- The reserved glyph range is from `gs_c_min_std_encoding_glyph` through `gs_min_cid_glyph - 1`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscencs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gschar.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gschar.c

Implements Ghostscript client-facing character/show operator wrappers.

Key contents:
- Includes Ghostscript graphics state, device, memory-device, character, and font internals.
- Provides `gs_show_enum_release`.
- Implements initialization wrappers for PostScript text operators:
  - `gs_show_n_init`
  - `gs_ashow_n_init`
  - `gs_widthshow_n_init`
  - `gs_awidthshow_n_init`
  - `gs_kshow_n_init`
  - `gs_xyshow_n_init`
  - `gs_glyphshow_init`
  - `gs_glyphpath_init`
  - `gs_glyphwidth_init`
  - `gs_cshow_n_init`
  - `gs_stringwidth_n_init`
  - `gs_charpath_n_init`
  - `gs_charboxpath_n_init`
- Implements cache/metrics wrappers:
  - `gs_setcachedevice_float`
  - `gs_setcachedevice_double`
  - `gs_setcachedevice2_float`
  - `gs_setcachedevice2_double`
  - `gs_setcharwidth`
- Implements enumeration/accessor functions:
  - `gs_show_next`
  - `gs_show_width_only`
  - `gs_show_current_char`
  - `gs_show_current_glyph`
  - `gs_show_current_width`
  - `gs_kshow_previous_char`
  - `gs_kshow_next_char`
  - `gs_show_width`
- Internal helper `show_n_begin` normalizes the text enumerator implementation to `gs_show_enum`.

Behavior:
- Most init functions call a lower-level `gs_*_begin` text routine and then pass through `show_n_begin`.
- `gs_kshow_n_init` rejects composite and CID font types as invalid for `kshow`.
- Float cache-device APIs convert to double arrays for backward compatibility.
- Cache-device and setcharwidth APIs validate that the enumerator belongs to the passed graphics state.

Important implementation notes:
- This file is an adapter layer around the newer `gs_text_*` machinery.
- `show_n_begin` falls back to default device text handling if the device produced a different text enumerator type, temporarily replacing the device `text_begin` proc.
- `gs_kshow_next_char` directly indexes `penum->text.data.bytes[penum->index]`, so it assumes byte-string text data for that path.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gschar.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gschar.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gschar.h

Client interface for Ghostscript character rendering/show operations.

Key contents:
- Includes `gsccode.h` and `gscpm.h`.
- Forward-declares opaque `gs_show_enum` and `gs_font`.
- Declares show enumerator allocation/release:
  - `gs_show_enum_alloc`
  - `gs_show_enum_release`
- Declares text initialization APIs for show, ashow, widthshow, awidthshow, kshow, xyshow, glyphshow, cshow, stringwidth, charpath, glyphpath, glyphwidth, and charboxpath.
- Declares `gs_show_use_glyph`.
- Defines continuation result aliases:
  - `gs_show_render`
  - `gs_show_kern`
  - `gs_show_move`
- Declares enumeration/accessors:
  - `gs_show_next`
  - current/previous/next char accessors
  - current font/glyph
  - current and cumulative width
  - charpath mode
  - width-only query
- Declares cache/metric operators:
  - `gs_setcachedevice_float`
  - `gs_setcachedevice_double`
  - `gs_setcachedevice`
  - `gs_setcachedevice2_float`
  - `gs_setcachedevice2_double`
  - `gs_setcachedevice2`
  - `gs_setcharwidth`

Important implementation notes:
- The API exposes text rendering as an enumerator/coroutine-style protocol: initialize, repeatedly call `gs_show_next`, respond to positive continuation codes, and stop on zero or negative.
- Macros map default `gs_setcachedevice` and `gs_setcachedevice2` to float variants for compatibility.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gschar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gschar0.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gschar0.c

Implements composite Type 0 font decoding for Ghostscript text enumeration.

Key contents:
- Includes memory, error, font map/CMap, fixed-point, device, font, Type 0 font, and text headers.
- Implements private `gs_stack_modal_fonts`.
- Implements public/internal composite helpers:
  - `gs_type0_init_fstack`
  - `gs_type0_next_char_glyph`
- Defines helper macro `select_descendant`.
- Defines private `root_esc_char`.

Behavior:
- `gs_type0_init_fstack` initializes the text enumerator font stack for byte-string text and stacks modal composite fonts down to a non-modal or base font.
- `gs_stack_modal_fonts` descends through modal composite fonts, using `Encoding[0]`, until it reaches a non-modal composite or base font.
- `gs_type0_next_char_glyph` decodes the next character/glyph from a composite string and returns:
  - error on malformed/incomplete sequences
  - `2` when the string is empty or exhausted
  - `1` when the base font changed
  - `0` otherwise
- Handles modal escape/shift font maps:
  - `fmap_escape`
  - `fmap_double_escape`
  - `fmap_shift`
- Handles non-modal descendant maps:
  - `fmap_8_8`
  - `fmap_1_7`
  - `fmap_9_7`
  - `fmap_SubsVector`
  - `fmap_CMap`
- For CMap descendants, calls `gs_cmap_decode_next`, preserves CMap code for widthshow behavior, and can return either character or glyph identity.
- Updates `pte->FontBBox_as_Metrics2` for CID encrypted and CID TrueType descendants where vertical metrics may use FontBBox.

Important implementation notes:
- The decoder has special handling for initial escape/shift bytes at the root of modal composite fonts, based on documented Adobe behavior confirmed by compatibility reports.
- Bounds checks use `need_left(n)` and return `gs_error_rangecheck` for truncated multibyte sequences.
- The implementation mutates the text enumerator’s font stack and string index as decoding proceeds.
- There is an explicit unresolved comment: descendant CMap rescanning after CMap decode is marked as a future/unfinished concern.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gschar0.c -->