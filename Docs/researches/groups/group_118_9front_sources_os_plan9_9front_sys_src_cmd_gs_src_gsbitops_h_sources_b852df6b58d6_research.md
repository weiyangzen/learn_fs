# Group Research: group_118_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_gsbitops_h_sources_b852df6b58d6

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsbitops.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsbitops.h

## Role

`gsbitops.h` is the public Ghostscript bitmap/packed-sample operations interface. It is a header-only macro layer for reading and writing packed pixel/component samples plus prototypes for byte/bit rectangle operations.

This is graphics infrastructure, not filesystem code.

## Main Interfaces

- Packed sample load macros:
  - `sample_load8`, `sample_load12`, `sample_load16`, `sample_load32`, `sample_load64`
  - `sample_load_next*`
  - `sample_load_any`, selected by `sizeof(value)`
- Packed sample store macros:
  - `sample_store_next8`, `sample_store_next12`, `sample_store_next16`, `sample_store_next32`, `sample_store_next64`
  - `sample_store_next_any`
  - `sample_store_flush`, `sample_store_skip_next`
- Positioning helpers:
  - `sample_load_setup`
  - `sample_store_setup`
  - `sample_next`
- Bitmap/byte operation prototypes:
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

## Data Structures

- `bits_plane_t` describes one plane of a pixmap/bitmap:
  - `data.write` or `data.read`
  - `raster`
  - `depth`
  - `x`

## Important Behavior

- Supports bits-per-value of `1`, `2`, `4`, `8`, `12`, `16`, `24`, `32`, and larger byte-aligned values up to 64-bit paths.
- Bit numbering is documented as big-endian inside a byte: `0x80` is bit 0, `0x01` is bit 7.
- `sample_bound_shift` avoids compiler warnings or undefined large shifts by masking shifts that exceed the storage width.
- Store macros preserve partial destination bytes with `sample_store_preload` and `sample_store_flush`.
- The macros assume Ghostscript block macros such as `BEGIN`, `END`, and `return_error(...)` are available in the including context.

## Dependencies And Assumptions

- Uses Ghostscript scalar types such as `byte`, `uint`, `gx_color_index`, `gs_int_rect`, and `gs_log2_scale_point`.
- Uses architecture constants such as `arch_sizeof_int`.
- The `sample_end_` macro returns `gs_error_rangecheck` on unsupported sample widths, so the load/store macros are intended for functions returning an integer error code.

## Notable Risks

- Macro-heavy implementation has hidden control flow, including `return_error`, switch fall-through in store paths, and pointer increments.
- Correctness depends on caller-provided bit positions and raster alignment.
- Multi-byte sample paths assume big-endian byte ordering in the encoded data.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsbitops.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsbittab.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsbittab.c

## Role

`gsbittab.c` defines static lookup tables for Ghostscript bit operations. It is paired with `gsbittab.h`.

This is graphics utility data, not filesystem code.

## Defined Tables

- `byte_reverse_bits[256]`: maps a byte to the same byte with bit order reversed.
- `byte_right_mask[9]`: maps `N` to a byte with `N` trailing one bits.
- `byte_count_bits[256]`: maps a byte to its population count.
- `byte_bit_run_length_0` through `byte_bit_run_length_7`: for each starting bit position, maps a byte to the run length of one bits starting at that bit.
- `byte_bit_run_length[8]`: pointer table for the forward run-length tables.
- `byte_bit_run_length_neg[8]`: pointer table for negative/rotated bit indexing.
- `byte_acegbdfh_to_abcdefgh[256]`: reorders interleaved bit order `acegbdfh` into `abcdefgh`.

## Implementation Notes

- Uses `bit_table_8(...)` from `gsbittab.h` to generate the 256-entry reverse, count, and reorder tables at compile time.
- Uses local macros (`t8`, `r8`, `r16`, `r32`, `r64`, `r128`, `rr8`) to generate run-length tables compactly.
- Run-length values add 8 when the run reaches the low-order bit, indicating that a scan may continue into the next byte.
- Includes `gsbittab_dummy()` because some old C compilers expected executable code in every translation unit.

## Dependencies

- Includes `stdpre.h` and `gsbittab.h`.
- Exports data declared in `gsbittab.h`.

## Notable Risks

- The generated table macro patterns are dense and easy to break if edited manually.
- Consumers must understand the special “run length plus 8” continuation convention.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsbittab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsbittab.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsbittab.h

## Role

`gsbittab.h` declares Ghostscript bit-operation lookup tables and provides compile-time table generator macros.

This is graphics utility infrastructure, not filesystem code.

## Macro Interfaces

- `bit_table_2`
- `bit_table_4`
- `bit_table_6`
- `bit_table_8`

These macros expand weighted bit combinations into complete lookup tables for 2, 4, 6, or 8 input bits.

## Exported Tables

- `byte_reverse_bits[256]`
- `byte_right_mask[9]`
- `byte_count_bits[256]`
- `byte_bit_run_length_0` through `byte_bit_run_length_7`
- `byte_bit_run_length[8]`
- `byte_bit_run_length_neg[8]`
- `byte_acegbdfh_to_abcdefgh[256]`

## Important Semantics

- `byte_bit_run_length_N[B]` uses bit numbering `01234567` within the byte.
- If a one-bit run reaches the low-order bit and could continue into the next byte, the table value is increased by 8.
- `byte_bit_run_length_neg[N]` aliases `byte_bit_run_length[-N & 7]`.

## Dependencies

- Requires Ghostscript’s `byte` type to be visible to users of the extern declarations.

## Notable Risks

- The table-generation macros rely on positional argument naming (`v80`, `v40`, etc.) and are not self-checking.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsbittab.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsccode.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsccode.h

## Role

`gsccode.h` defines Ghostscript character-code and glyph-code types plus encoding and glyph-space enums.

This is font/text infrastructure, not filesystem code.

## Main Types

- `gs_char`: unsigned long character code. Composite fonts require at least 32 bits.
- `gs_glyph`: unsigned long glyph identifier.
- `gs_encoding_index_t`: known encoding index enum.
- `gs_glyph_space_t`: selector for name/index/no-generation glyph spaces.
- `gs_glyph_mark_proc_t`: GC marking callback for glyphs.
- `gs_glyph_name_proc_t`: callback to map a glyph code to a string name.

## Glyph Code Space

`gs_glyph` is partitioned into ranges:

- `GS_NO_GLYPH`: unknown glyph identity.
- Values below `GS_MIN_CID_GLYPH`: named glyphs.
- Values from `gs_c_min_std_encoding_glyph` up to `GS_MIN_CID_GLYPH`: private built-in encoding glyph names managed by `gscencs.h`.
- Values from `GS_MIN_CID_GLYPH` to `GS_MIN_GLYPH_INDEX`: CIDs.
- Values at or above `GS_MIN_GLYPH_INDEX`: glyph indices.

## Known Encodings

The enum defines 11 known encodings:

- Real encodings:
  - `StandardEncoding`
  - `ISOLatin1Encoding`
  - `SymbolEncoding`
  - `DingbatsEncoding`
  - `WinAnsiEncoding`
  - `MacRomanEncoding`
  - `MacExpertEncoding`
- Pseudo-encodings/glyph sets:
  - `MacGlyph`
  - `AdobeLatinOriginalGlyph`
  - `AdobeLatinExtensionGlyph`
  - `CFFStandardStrings`

`NUM_KNOWN_REAL_ENCODINGS` is 7, and `NUM_KNOWN_ENCODINGS` is 11.

## Constants

- `GS_NO_CHAR`
- `GS_NO_GLYPH`
- `GS_MIN_CID_GLYPH`
- `GS_MIN_GLYPH_INDEX`
- `GS_GLYPH_TAG`
- `GS_MAX_GLYPH`

Backward-compatible lowercase aliases are also provided.

## Dependencies

- Uses `ulong`, `bool`, `gs_memory_t`, and `gs_const_string`, which must be available from the broader Ghostscript include context.

## Notable Risks

- Client code must not mix built-in-encoding private glyph values with global-name glyph values.
- The exact numeric partition depends partly on `arch_sizeof_long`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsccode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsccolor.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsccolor.h

## Role

`gsccolor.h` defines Ghostscript client color structures.

This is rendering/color state infrastructure, not filesystem code.

## Main Types

- Forward declaration:
  - `gs_pattern_instance_t`
  - `gs_client_color`
- `gs_paint_color`:
  - `float values[GS_CLIENT_COLOR_MAX_COMPONENTS]`
- `gs_client_color`:
  - `paint`: numeric paint color or uncolored-pattern color
  - `pattern`: optional pattern instance pointer

## Constants

- `GS_CLIENT_COLOR_MAX_COMPONENTS` is 16.
- Comment notes this must be at least 4 and should be at least 6 for hexachrome DeviceN color spaces.

## GC Support

- Declares `extern_st(st_client_color)`.
- Defines `public_st_client_color()` to register one pointer field, `pattern`, with Ghostscript’s structure/GC system.
- `st_client_color_max_ptrs` is 1.

## Dependencies

- Includes `gsstype.h` for `extern_st`.
- Depends on Ghostscript GC macros such as `gs_public_st_ptrs1`.

## Notable Risks

- Fixed-size color component array means callers must respect the 16-component maximum.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsccolor.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscdef.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscdef.c

## Role

`gscdef.c` defines Ghostscript configuration scalar variables: product identity, revision metadata, serial number, and installation paths.

This is application configuration, not filesystem implementation.

## Defined Symbols

- Build/product metadata:
  - `gs_buildtime`
  - `gs_copyright`
  - `gs_productfamily`
  - `gs_product`
  - `gs_revision`
  - `gs_revisiondate`
  - `gs_serialnumber`
- Accessors:
  - `gs_program_name()`
  - `gs_revision_number()`
- Installation paths:
  - `gs_doc_directory`
  - `gs_lib_default_path`
  - `gs_init_file`

## Build-Time Inputs

- Includes `gconfigd.h`, which supplies makefile-generated definitions such as:
  - `GS_REVISION`
  - `GS_REVISIONDATE`
  - `GS_DOCDIR`
  - `GS_LIB_DEFAULT`
  - `GS_INIT`
- Provides fallback defaults for:
  - `GS_BUILDTIME`
  - `GS_COPYRIGHT`
  - `GS_PRODUCTFAMILY`
  - `GS_PRODUCT`
  - `GS_SERIALNUMBER`

## Mutability

- Uses `CONFIG_CONST` from `gscdefs.h`.
- Depending on `SYSTEM_CONSTANTS_ARE_WRITABLE`, some variables may be writable rather than `const`.

## Notable Detail

- The default serial number is `42`.
- This file is content-identical to `gscdefs.c` in this group.

## Dependencies

- Includes `std.h`, `gscdefs.h`, and `gconfigd.h`.

## Notable Risks

- Correct compilation depends on the build system defining `GS_REVISION`, `GS_REVISIONDATE`, and path macros.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscdef.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscdefs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscdefs.c

## Role

`gscdefs.c` defines Ghostscript configuration scalar variables. In this source tree, its contents are identical to `gscdef.c`.

This is application configuration, not filesystem implementation.

## Defined Symbols

- `gs_buildtime`
- `gs_copyright`
- `gs_productfamily`
- `gs_product`
- `gs_program_name()`
- `gs_revision`
- `gs_revision_number()`
- `gs_revisiondate`
- `gs_serialnumber`
- `gs_doc_directory`
- `gs_lib_default_path`
- `gs_init_file`

## Build-Time Inputs

- Uses makefile/generated symbols from `gconfigd.h`.
- Falls back to built-in values for product family, copyright string, build time, and serial number when those macros are absent.
- Requires `GS_REVISION`, `GS_REVISIONDATE`, `GS_DOCDIR`, `GS_LIB_DEFAULT`, and `GS_INIT`.

## Relationship To `gscdef.c`

- This file appears to be a duplicate copy of `gscdef.c`.
- If both are compiled into the same link target, they would define the same global symbols and cause duplicate-definition conflicts. The build likely selects one variant.

## Dependencies

- Includes `std.h`, `gscdefs.h`, and `gconfigd.h`.

## Notable Risks

- The duplicate with `gscdef.c` requires build-system care.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscdefs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscdefs.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscdefs.h

## Role

`gscdefs.h` declares Ghostscript configuration globals and provides macros for declaring build-generated resource tables without forcing many type definitions into every include site.

This is configuration/resource wiring, not filesystem code.

## Declared Configuration Globals

- `gs_buildtime`
- `gs_copyright`
- `gs_product`
- `gs_productfamily`
- `gs_revision`
- `gs_revisiondate`
- `gs_serialnumber`
- `gs_doc_directory`
- `gs_lib_default_path`
- `gs_init_file`

## Const Control

- Includes `gconfigv.h`.
- Defines `CONFIG_CONST`:
  - empty when `SYSTEM_CONSTANTS_ARE_WRITABLE` is true
  - `const` otherwise

## Resource Declaration Macros

Macros avoid direct dependency on many Ghostscript internal types:

- `extern_gx_device_halftone_list()`
- `extern_gx_image_class_table()`
- `extern_gx_image_type_table()`
- `extern_gx_init_table()`
- `extern_gx_io_device_table()`
- `extern_gs_lib_device_list()`
- `extern_gs_find_compositor()`

Also declares counts:

- `gx_image_class_table_count`
- `gx_image_type_table_count`
- `gx_io_device_table_count`

## Dependencies

- Designed to be included where `stdpre.h` may not be available.
- Macro bodies assume the caller has provided needed types before expanding them.

## Notable Risks

- Resource extern macros are context-sensitive and can fail if expanded before the required types/macros are visible.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscdefs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscdevn.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscdevn.c

## Role

`gscdevn.c` implements Ghostscript DeviceN color spaces: construction, tint transform mapping, alternate color space fallback, component-name matching against devices, overprint handling, reference counting, and serialization.

This is color/rendering infrastructure, not filesystem code.

## Main Public Interfaces

- `gs_build_DeviceN(...)`
- `gs_cspace_build_DeviceN(...)`
- `alloc_device_n_map(...)`
- `using_alt_color_space(...)`
- `map_devn_using_function(...)`
- `gs_cspace_set_devn_function(...)`
- `gs_cspace_get_devn_function(...)`
- `gx_serialize_device_n_map(...)`

A procedural tint-transform setter, `gs_cspace_set_devn_proc`, exists inside `#if 0` and is not compiled.

## Color Space Type

Defines `gs_color_space_type_DeviceN` with handlers for:

- number of components
- alternate space
- initial color
- color restriction
- concrete color space selection
- concretization
- remapping
- install
- overprint
- reference count adjustment
- serialization
- linearity check via default implementation

## GC Support

- Declares composite descriptor `st_color_space_DeviceN`.
- Uses `private_st_device_n_map()`.
- Enumerates/relocates:
  - `params.device_n.names`
  - `params.device_n.map`
  - `params.device_n.alt_space`

## DeviceN Construction

`gs_build_DeviceN`:

- Validates that alternate color space exists and can be an alternate space.
- Allocates a `gs_device_n_map`.
- Allocates the component name array.
- Sets `names` and `num_components`.

`gs_cspace_build_DeviceN`:

- Allocates a DeviceN color space.
- Calls `gs_build_DeviceN`.
- Intends to initialize the alternate space and return the allocated color space.

## Important Behavior

- Initial DeviceN color sets all components to `1.0`.
- Restriction clamps each component into `[0, 1]`.
- If `use_alt_cspace` is true, concretization runs the tint transform and then concretizes in the alternate color space.
- If `use_alt_cspace` is false, component floats are converted directly to `frac`.
- A one-entry cache exists in `gs_device_n_map`, checking previous tint values before reusing `conc`.
- Additive devices always force alternate color space usage.
- Component-name matching:
  - maps DeviceN component names to device colorants with `get_color_comp_index`
  - accepts `/None`, mapping it to `-1`
  - rejects duplicated component names except `/None`
  - uses the alternate space if any component does not match a device colorant
- Install updates `pgs->color_space->params.device_n.use_alt_cspace` and gives the device a chance to update spot equivalent colors.
- Overprint handling either delegates to alternate space spot-color logic or builds drawn component masks from the color map.
- Serialization supports only function-backed tint transforms; non-function transforms return `gs_error_unregistered`.

## Notable Risks And Suspect Code

- `gs_cspace_build_DeviceN` declares `gs_device_n_params *pcsdevn = 0` and later uses `pcsdevn->alt_space` without assigning it to `&pcspace->params.device_n`. As written, this is a null-pointer-derived address bug.
- `gs_cspace_build_DeviceN` accepts `psnames` but does not copy those names into the allocated `names` array. That conflicts with the function comment saying it allocates and fills the color space.
- `gs_build_DeviceN` also allocates the names array but does not initialize it.
- The one-entry cache is checked in `gx_concretize_DeviceN`, but this file does not visibly update `map->tint`, `map->conc`, or `map->cache_valid` after computing a new mapping.
- Serialization writes raw `gs_separation_name` values, so stability depends on how those names are represented in this Ghostscript build.

## Dependencies

Includes many Ghostscript internals: color spaces, functions, reference counting, matrices, device clients, imager state, overprint, and stream serialization.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscdevn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscdevn.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscdevn.h

## Role

`gscdevn.h` declares the client interface for Ghostscript DeviceN color spaces.

This is rendering/color API surface, not filesystem code.

## Public Functions

- `gs_build_DeviceN(...)`: fill an existing color space.
- `gs_cspace_build_DeviceN(...)`: allocate and fill a DeviceN color space.
- `gs_cspace_set_devn_proc(...)`: set a procedural tint transform.
- `gs_cspace_set_devn_function(...)`: set a tint transform backed by a `gs_function_t`.
- `gs_cspace_get_devn_function(...)`: return the backing function if the tint transform uses one.
- `map_devn_using_function(...)`: adapter that evaluates a `gs_function_t`.
- `gx_serialize_device_n_map(...)`: serialize the DeviceN map.

## Data Ownership Semantics

- Comments state that the client is responsible for memory management of the tint transform Function.
- The color space construction routines allocate or fill the DeviceN color space, but the tint transform is configured separately.

## Dependencies

- Includes `gscspace.h`.
- Forward-declares `gs_function_t` if absent.
- Uses Ghostscript types:
  - `gs_color_space`
  - `gs_separation_name`
  - `gs_memory_t`
  - `gs_imager_state`
  - `gs_device_n_map`
  - `stream`

## Notable Risks

- Header declares `gs_cspace_set_devn_proc`, but the implementation in `gscdevn.c` is disabled under `#if 0`. Callers relying on this symbol may fail to link unless another translation unit provides it.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscdevn.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscedata.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscedata.c

## Role

`gscedata.c` is a generated data file containing compact tables for Ghostscript’s built-in glyph encodings. It is generated from PostScript encoding files by `toolbin/encs2c.ps`.

This is font encoding data, not filesystem code.

## Generation Inputs

The file states it was generated from:

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

## Core Data Model

Glyph names are stored once in `gs_c_known_encoding_chars[]`, grouped by glyph-name length. Encodings store compact `ushort` values created by:

- `N(len, offset)`

The companion header defines:

- lower `NUM_LEN_BITS` bits as name length
- remaining bits as offset within the length group

This allows compact glyph-name lookup without storing pointers per glyph.

## Exported Constants

- `gs_c_known_encoding_total_chars = 5483`
- `gs_c_known_encoding_max_length = 19`
- `gs_c_known_encoding_count = 11`

## Exported Offset Table

`gs_c_known_encoding_offsets[]` contains per-name-length starting offsets:

`0, 0, 52, 104, 404, 876, 1081, 1771, 2072, 2272, 2776, 3116, 3754, 4414, 4830, 5250, 5280, 5360, 5428, 5464, 5483`

These offsets support lookup by glyph-name length.

## Encoding Tables

Defines 11 static encoding tables and 11 reverse tables:

- `gs_c_known_encoding_0` / reverse: `StandardEncoding`
- `gs_c_known_encoding_1` / reverse: `ISOLatin1Encoding`
- `gs_c_known_encoding_2` / reverse: `SymbolEncoding`
- `gs_c_known_encoding_3` / reverse: `DingbatsEncoding`
- `gs_c_known_encoding_4` / reverse: `WinAnsiEncoding`
- `gs_c_known_encoding_5` / reverse: `MacRomanEncoding`
- `gs_c_known_encoding_6` / reverse: `MacExpertEncoding`
- `gs_c_known_encoding_7` / reverse: `MacGlyphEncoding`
- `gs_c_known_encoding_8` / reverse: `AdobeLatinOriginalGlyphEncoding`
- `gs_c_known_encoding_9` / reverse: `AdobeLatinExtensionGlyphEncoding`
- `gs_c_known_encoding_10` / reverse: `CFFStandardStrings`

## Exported Pointer Tables

- `gs_c_known_encodings[]`: points to the 11 forward encoding arrays, then terminates with `0`.
- `gs_c_known_encodings_reverse[]`: points to the 11 reverse arrays, then terminates with `0`.

## Exported Length Tables

Forward lengths:

`256, 256, 256, 256, 256, 256, 256, 258, 229, 86, 379, 0`

Reverse lengths:

`149, 205, 189, 188, 224, 208, 165, 257, 228, 86, 378, 0`

## Important Semantics

- `.notdef` is represented repeatedly as `N(7,0)`.
- Forward arrays map character codes or glyph-set indices to compact glyph-name IDs.
- Reverse arrays map sorted glyph-name IDs back to character codes or glyph-set indices. `gscencs.c` binary-searches these arrays.
- Encoding 7 (`MacGlyphEncoding`) has 258 entries, so not every table is byte-sized.
- Encoding 10 (`CFFStandardStrings`) has 379 entries.

## Dependencies

- Includes `stdpre.h`, `gstypes.h`, and `gscedata.h`.
- Depends on `ushort` and the `N(...)` macro from `gscedata.h`.

## Notable Risks

- Generated file should not be manually edited unless the generator and consumers are kept consistent.
- Reverse tables must remain sorted in the order expected by `gs_c_decode`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscedata.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscedata.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscedata.h

## Role

`gscedata.h` declares the generated built-in encoding data used by `gscencs.c`.

This is font encoding infrastructure, not filesystem code.

## Encoding Packed-Value Macros

- `NUM_LEN_BITS` is 5.
- `N(len, offset)` packs length and offset into one integer.
- `N_LEN(e)` extracts the length.
- `N_OFFSET(e)` extracts the offset.

## Exported Data

- `gs_c_known_encoding_chars[]`
- `gs_c_known_encoding_total_chars`
- `gs_c_known_encoding_max_length`
- `gs_c_known_encoding_offsets[]`
- `gs_c_known_encoding_count`
- `gs_c_known_encodings[]`
- `gs_c_known_encodings_reverse[]`
- `gs_c_known_encoding_lengths[]`
- `gs_c_known_encoding_reverse_lengths[]`

## Generation Notes

Header comments identify `toolbin/encs2c.ps` as the generator and list the source encoding files. The header must remain consistent with both generated `gscedata.c` and consumer `gscencs.c`.

## Dependencies

- Requires `ushort` to be visible to includers, usually through Ghostscript base type headers.

## Notable Risks

- If `NUM_LEN_BITS` changes, all generated `N(...)` values and consumers must change together.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscedata.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscencs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscencs.c

## Role

`gscencs.c` implements lookup operations over the compact built-in encoding data from `gscedata.c`.

This is font encoding logic, not filesystem code.

## Main Public Symbols

- `gs_c_min_std_encoding_glyph`
- `gs_c_known_encode(gs_char ch, int ei)`
- `gs_c_decode(gs_glyph glyph, int ei)`
- `gs_c_glyph_name(gs_glyph glyph, gs_const_string *pstr)`
- `gs_is_c_glyph_name(const byte *str, uint len)`
- `gs_c_name_glyph(const byte *str, uint len)`

## Encoding Scheme

- `gs_c_min_std_encoding_glyph` is `gs_min_cid_glyph - 0x10000`.
- Built-in encoding glyph IDs are stored as this base plus the compact `N(len, offset)` value from `gscedata.c`.
- These private glyph values are only intended for use with `gs_c_glyph_name` or `gs_c_decode`.

## Function Behavior

- `gs_c_known_encode`:
  - validates encoding index and character range
  - returns `gs_no_glyph` for invalid input
  - otherwise returns private glyph value
- `gs_c_decode`:
  - binary-searches the reverse table for the requested encoding
  - returns the character code on match
  - returns `GS_NO_CHAR` on miss
- `gs_c_glyph_name`:
  - decodes packed length and offset
  - returns a string slice into `gs_c_known_encoding_chars`
  - debug builds perform range checks
- `gs_is_c_glyph_name`:
  - tests whether a string pointer lies inside the generated glyph-name character pool
- `gs_c_name_glyph`:
  - binary-searches the glyph-name pool for a name of a given length
  - returns the private glyph code or `gs_no_glyph`

## Test Code

Under `#ifdef TEST`, the file includes a standalone test program that checks sample glyphs such as `caron`, `carriagereturn`, `circlemultiply`, `numbersign`, and reverse lookup behavior.

## Dependencies

- Includes `memory_.h`, `gscedata.h`, `gscencs.h`, `gserror.h`, and `gserrors.h`.
- Uses `memcmp`, Ghostscript string types, and Ghostscript error handling.

## Notable Risks

- `gs_c_decode` assumes `ei` is valid; unlike `gs_c_known_encode`, it does not range-check the encoding index.
- `gs_c_glyph_name` only validates packed glyph values in debug builds.
- `gs_is_c_glyph_name` checks pointer range but does not validate `len` against the end of the character pool.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscencs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscencs.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscencs.h

## Role

`gscencs.h` declares the public API for Ghostscript’s compact built-in encoding representation.

This is font encoding API surface, not filesystem code.

## Public API

- `gs_c_min_std_encoding_glyph`
- `gs_c_known_encode(gs_char chr, int encoding_index)`
- `gs_c_decode(gs_glyph glyph, int ei)`
- `gs_c_glyph_name(gs_glyph glyph, gs_const_string *pstr)`
- `gs_is_c_glyph_name(const byte *str, uint len)`
- `gs_c_name_glyph(const byte *str, uint len)`

## Semantics

- `gs_c_known_encode` returns private glyph numbers.
- Those private glyph numbers are intended to be converted back to strings by `gs_c_glyph_name`.
- Values from `gs_c_min_std_encoding_glyph` through `gs_min_cid_glyph - 1` are reserved for this compact encoding system.
- The data file `gscedata.c` is generated by `encs2c.ps`.
- If the representation changes, `gscencs.h`, `gscencs.c`, and the generator must stay synchronized.

## Dependencies

- Includes `stdpre.h`, `gstypes.h`, and `gsccode.h`.

## Notable Risks

- The header exposes the private glyph numbering boundary, so callers must avoid mixing these glyph IDs with other glyph-code spaces described in `gsccode.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscencs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gschar.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gschar.c

## Role

`gschar.c` implements Ghostscript library “character writing” wrappers around the lower-level text enumeration API.

This is text rendering/control flow infrastructure, not filesystem code.

## Main Public Functions

Initialization wrappers:

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

Enumerator/control functions:

- `gs_show_enum_release`
- `gs_show_next`
- `gs_show_width_only`

Accessors:

- `gs_show_current_char`
- `gs_show_current_glyph`
- `gs_show_current_width`
- `gs_kshow_previous_char`
- `gs_kshow_next_char`
- `gs_show_width`

Cache/metrics operators:

- `gs_setcachedevice_double`
- `gs_setcachedevice_float`
- `gs_setcachedevice2_double`
- `gs_setcachedevice2_float`
- `gs_setcharwidth`

## Important Behavior

- Each initializer calls the matching `gs_*_begin` lower-level text routine, then passes the result through `show_n_begin`.
- `gs_kshow_n_init` rejects composite and CID font types with `gs_error_invalidfont`.
- `gs_setcachedevice*` and `gs_setcharwidth` reject calls when the enumerator’s graphics state does not match the supplied `gs_state`.
- Float cache-device APIs are backward-compatible wrappers that convert arrays to double and call the double implementation.
- `gs_show_next` delegates to `gs_text_process`.

## Internal `show_n_begin`

`show_n_begin` forces the result enumerator to be a `gs_show_enum`.

If the current device’s `text_begin` created a different text enumerator type, the function:

- saves the device’s current `text_begin` procedure
- releases the existing text enumerator
- temporarily resets `text_begin` to `gx_default_text_begin`
- starts text enumeration again
- restores the original device procedure
- copies the resulting `gs_show_enum` into the caller-provided storage
- frees the temporary allocated enumerator

## Dependencies

Includes Ghostscript graphics state, device, matrix, coordinate, memory device, character, and font internals.

## Notable Risks

- `show_n_begin` copies a structure by value, then frees the original allocation. This depends on the enumerator owning only relocatable/reference-managed internals that remain valid after the shallow copy.
- `gs_kshow_next_char` indexes directly into `penum->text.data.bytes[penum->index]`; correctness depends on enumeration state.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gschar.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gschar.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gschar.h

## Role

`gschar.h` declares the Ghostscript client interface for character operations and text enumeration.

This is text rendering API surface, not filesystem code.

## Main Types

- Opaque `gs_show_enum`
- Opaque `gs_font`

## Allocation And Lifetime

- `gs_show_enum_alloc(gs_memory_t *, gs_state *, client_name_t)`
- `gs_show_enum_release(gs_show_enum *, gs_memory_t *)`

The release function can optionally free the enumerator when the memory argument is non-null.

## Initialization APIs

Declares wrappers for PostScript-like text operations:

- `show`
- `ashow`
- `widthshow`
- `awidthshow`
- `kshow`
- `xyshow`
- `glyphshow`
- `cshow`
- `stringwidth`
- `charpath`
- `charboxpath`

Also declares extensions:

- `gs_glyphpath_init`
- `gs_glyphwidth_init`
- `gs_show_use_glyph`

## Enumerator Return Codes

Aliases text-processing statuses:

- `gs_show_render` = `TEXT_PROCESS_RENDER`
- `gs_show_kern` = `TEXT_PROCESS_INTERVENE`
- `gs_show_move` = `TEXT_PROCESS_INTERVENE`

Clients call `gs_show_next` until completion, error, or an intervention/rendering status.

## Accessors

- `gs_show_current_char`
- `gs_kshow_previous_char`
- `gs_kshow_next_char`
- `gs_show_current_font`
- `gs_show_current_glyph`
- `gs_show_current_width`
- `gs_show_width`
- `gs_show_in_charpath`
- `gs_show_width_only`

## Cache And Metrics APIs

- `gs_setcachedevice_float`
- `gs_setcachedevice_double`
- `gs_setcachedevice2_float`
- `gs_setcachedevice2_double`
- `gs_setcharwidth`

Macros map `gs_setcachedevice` and `gs_setcachedevice2` to the float variants for compatibility.

## Dependencies

- Includes `gsccode.h` and `gscpm.h`.
- Uses Ghostscript types such as `gs_state`, `gs_memory_t`, `gs_point`, `gs_char_path_mode`, `floatp`, `bool`, and `client_name_t`.

## Notable Risks

- API is state-machine based; clients must respond correctly to nonzero `gs_show_next` statuses.
- Some declared functions are implemented in other Ghostscript translation units, not in `gschar.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gschar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gschar0.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gschar0.c

## Role

`gschar0.c` implements Type 0/composite font string decoding for Ghostscript text enumeration.

This is font/text decoding infrastructure, not filesystem code.

## Main Functions

- `gs_type0_init_fstack(gs_text_enum_t *pte, gs_font *pfont)`
- `gs_type0_next_char_glyph(gs_text_enum_t *pte, gs_char *pchr, gs_glyph *pglyph)`

Internal helper:

- `gs_stack_modal_fonts(gs_text_enum_t *pte)`

## Font Stack Initialization

`gs_type0_init_fstack`:

- Requires text data to be string/bytes-backed.
- Initializes font stack depth to 0 with the supplied font.
- Calls `gs_stack_modal_fonts` to descend through modal composite fonts.

`gs_stack_modal_fonts`:

- Walks composite fonts while `FMapType` is modal.
- Selects descendants from `FDepVector` using `Encoding[0]`.
- Enforces `MAX_FONT_STACK`.

## Composite Decoding Behavior

`gs_type0_next_char_glyph` decodes the next character/glyph and returns:

- negative error on malformed data or invalid font
- `2` when the string is empty or exhausted
- `1` when the current base font changed
- `0` when the base font did not change

It handles:

- modal maps:
  - `fmap_escape`
  - `fmap_double_escape`
  - `fmap_shift`
- non-modal maps:
  - `fmap_8_8`
  - `fmap_1_7`
  - `fmap_9_7`
  - `fmap_SubsVector`
  - `fmap_CMap`

## Important Edge Cases

- Truncated multi-byte sequences return `gs_error_rangecheck`.
- Exceeding font stack depth returns `gs_error_invalidfont`.
- Initial escape or shift characters at string index 0 are handled specially from the root composite font, matching documented Adobe behavior discovered through compatibility testing.
- CMap decoding can return either a CID-like character or an explicit glyph. Undefined CMap glyphs become `gs_min_cid_glyph`.
- If an FMapType 4/5 decoding modifies the current character before a CMap descendant, the code builds a temporary modified buffer for `gs_cmap_decode_next`.
- For vertical metrics, CID base fonts may copy `FontBBox` into `pte->FontBBox_as_Metrics2`.

## Internal Macros

- `select_descendant(...)`: validates descendant index, updates stack depth/font/index, and marks changes.
- `need_left(n)`: validates remaining bytes.
- `subs_loop(...)`: helper for `SubsVector` decoding widths 1 to 4.

## Dependencies

Includes Ghostscript memory, font, CMap, fixed-point, device, and text internals.

## Notable Risks

- The function is dense and stateful: it mutates `pte->index`, `pte->fstack`, `pte->cmap_code`, and metrics fields.
- Several branches rely on `goto` labels for modal descent/ascent control flow.
- Correctness depends on composite font data structures being internally consistent: `Encoding`, `FDepVector`, `SubsVector`, `CMap`, and `FMapType`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gschar0.c -->