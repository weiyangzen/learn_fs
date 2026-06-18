# Group Research: group_1531_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_libpng_pngrutil_c_sourc_7c72910be464

Scope: `Docs/research_subset_a.md`, specifically `sources/os/plan9/plan9/sys/src/cmd/gs/libpng` in the bundled Ghostscript/libpng tree. I read all four listed files completely. These files are vendored libpng 1.2.8 PNG parsing, metadata, transform, and test-program code; they are not Plan 9 filesystem logic.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngrutil.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngrutil.c

`pngrutil.c` contains libpng's internal read-side utilities. It handles endian decoding, CRC handling, ancillary/critical chunk parsing, compressed text/profile decompression, unknown chunk dispatch, interlace row expansion, adaptive filter reversal, and row-buffer setup/finish logic.

Key responsibilities:
- Provides big-endian scalar readers: `png_get_uint_31`, `png_get_uint_32`, `png_get_int_32`, and `png_get_uint_16`.
- Wraps chunk data reads with CRC updates through `png_crc_read`, `png_crc_finish`, and `png_crc_error`.
- Decompresses compressed ancillary chunk payload tails through `png_decompress_chunk` for zTXt/iTXt/iCCP-style data.
- Implements handlers for core and ancillary chunks: `IHDR`, `PLTE`, `IEND`, `gAMA`, `sBIT`, `cHRM`, `sRGB`, `iCCP`, `sPLT`, `tRNS`, `bKGD`, `hIST`, `pHYs`, `oFFs`, `pCAL`, `sCAL`, `tIME`, `tEXt`, `zTXt`, `iTXt`, and unknown chunks.
- Implements scanline helpers: `png_combine_row`, `png_do_read_interlace`, `png_read_filter_row`, `png_read_finish_row`, and `png_read_start_row`.

Chunk parsing behavior:
- Most handlers enforce PNG ordering: required `IHDR` first, many metadata chunks before `IDAT`, and no duplicate metadata chunks when the matching `PNG_INFO_*` valid bit is already set.
- Critical chunks generally call `png_error` on structural invalidity; ancillary chunks often warn and skip.
- CRC behavior is governed by `PNG_FLAG_CRC_*` flags, with separate handling for ancillary and critical chunks.
- `png_handle_IHDR` reads the 13-byte header, initializes core `png_struct` image fields, computes `channels`, `pixel_depth`, and `rowbytes`, then delegates validation/storage to `png_set_IHDR`.
- Palette and transparency handlers coordinate with `png_set_PLTE` and `png_set_tRNS`, including truncation warnings when tRNS exceeds the actual palette length.
- Color-management handlers cross-check sRGB with gAMA/cHRM values and ignore inconsistent values with warnings.
- Text/profile handlers allocate full chunk buffers, split NUL-delimited fields, optionally decompress payloads, populate `png_text`, `iCCP`, or related structures, and free temporary buffers after `png_set_*` copies data.
- `png_handle_unknown` validates chunk names, rejects unhandled critical chunks unless configured/user-handled, optionally stores unknown chunks, invokes user chunk callbacks, and then finishes CRC/skipping.

Scanline and image-data behavior:
- `png_combine_row` merges the newly decoded row into the user row for interlaced/progressive display, with separate paths for 1-, 2-, 4-bit packed pixels and byte-aligned pixels.
- `png_do_read_interlace` expands Adam7 pass rows in place, again specializing packed bit depths and byte-aligned pixels.
- `png_read_filter_row` reverses PNG filter types None, Sub, Up, Average, and Paeth.
- `png_read_finish_row` advances row/pass state, drains remaining zlib data at image end, validates continued `IDAT` availability, warns on extra compressed data, resets inflate state, and marks `PNG_AFTER_IDAT`.
- `png_read_start_row` initializes read transformations, calculates pass dimensions, estimates maximum transformed pixel depth, allocates `big_row_buf`, `row_buf`, and `prev_row`, and sets `PNG_FLAG_ROW_INIT`.

Important dependencies and state:
- Includes `png.h` with `PNG_INTERNAL`.
- Uses zlib `inflate`, `inflateReset`, and `zstream` fields in `png_struct`.
- Relies on `png_set_*` routines in `pngset.c`, memory helpers, warning/error callbacks, CRC helpers, mode flags, transformation flags, and compile-time feature macros.

Edge cases and risks:
- This is older libpng 1.2.8 code with many feature-macro branches and 64K allocation compatibility paths.
- Several chunk parsers scan NUL-delimited data manually; malformed chunks are mostly handled by warning/return, but maintenance must preserve exact bounds and CRC-skipping behavior.
- `png_handle_sPLT` allocates `new_palette.entries`; on some early error paths after allocation-size checks, freeing must remain carefully paired.
- `png_read_start_row` row-size calculations are security-sensitive because they allocate scanline buffers based on transformed maximum pixel depth.
- The file is core decoder attack surface: chunk length checks, allocation limits, zlib state transitions, and row filter math are the most important review areas.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngrutil.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngset.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngset.c

`pngset.c` implements libpng setter/storage APIs for `png_info` and selected `png_struct` state. It is used both by readers, after chunk handlers parse file data, and by writers, when applications populate metadata before output.

Key responsibilities:
- Stores chunk metadata into `png_info` and sets the corresponding `PNG_INFO_*` validity flags.
- Copies caller-provided or parser-provided data into libpng-owned allocations where ownership must be retained.
- Validates high-risk inputs such as `IHDR`, gamma/chromaticity ranges, palette lengths, text arrays, unknown chunk storage, and user image-size limits.
- Configures ancillary behavior such as unknown chunk retention, user chunk callbacks, MNG feature permissions, row pointer ownership, write compression buffer size, assembler/MMX flags, and user width/height limits.

Implemented setter families:
- Basic metadata: `png_set_bKGD`, `png_set_hIST`, `png_set_oFFs`, `png_set_pHYs`, `png_set_PLTE`, `png_set_sBIT`, `png_set_tIME`, `png_set_tRNS`.
- Color management: `png_set_cHRM`, `png_set_cHRM_fixed`, `png_set_gAMA`, `png_set_gAMA_fixed`, `png_set_sRGB`, `png_set_sRGB_gAMA_and_cHRM`, `png_set_iCCP`.
- Calibration/scale: `png_set_pCAL`, `png_set_sCAL`, `png_set_sCAL_s`.
- Text and international text: public `png_set_text` plus internal `png_set_text_2`.
- Suggested palettes and unknown chunks: `png_set_sPLT`, `png_set_unknown_chunks`, `png_set_unknown_chunk_location`, `png_set_keep_unknown_chunks`.
- Runtime/configuration APIs: `png_permit_empty_plte`, `png_permit_mng_features`, `png_set_read_user_chunk_fn`, `png_set_rows`, `png_set_compression_buffer_size`, `png_set_invalid`, `png_set_asm_flags`, `png_set_mmx_thresholds`, and `png_set_user_limits`.

Important behavior:
- `png_set_IHDR` performs strict validation for zero dimensions, user dimension limits, bit-depth/color-type combinations, interlace method, compression method, filter method, and MNG intrapixel differencing exceptions. It also computes channels, pixel depth, and rowbytes.
- Palette and transparency setters allocate fixed 256-entry/byte buffers for historical compatibility with invalid PNG files that may reference out-of-range palette samples.
- `png_set_text_2` grows `info_ptr->text`, deep-copies key/language/translated-key/text data into one allocation per text entry, and tracks tEXt/zTXt/iTXt length fields according to compression mode.
- `png_set_unknown_chunks` appends deep copies of unknown chunk data and records the chunk location from `png_ptr->mode`.
- `png_set_sRGB_gAMA_and_cHRM` stores standard sRGB gamma and chromaticity values through the ordinary gAMA/cHRM setters.

Important dependencies and state:
- Includes `png.h` with `PNG_INTERNAL`.
- Uses libpng memory ownership flags such as `PNG_FREE_*`, `free_me`, and older fallback `png_ptr->flags` free markers.
- Called heavily from `pngrutil.c` chunk handlers and from applications or `pngtest.c` when copying metadata from read info to write info.

Edge cases and risks:
- Memory ownership is central. Many setters allocate deep copies and update `info_ptr->free_me`; partial allocation failure paths must avoid leaks and dangling partially initialized fields.
- `png_set_sPLT` uses `png_sizeof(png_sPLT_t)` when allocating/copying entries, although entries are `png_sPLT_entry` objects; this is a notable old-code maintenance risk.
- `png_set_text_2` frees the previous text array if reallocating fails, which preserves historical behavior but can surprise callers expecting old metadata to survive allocation failure.
- Public setters mostly return silently on null `png_ptr`/`info_ptr`; callers must not assume a failed setter reports an error.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngset.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngtest.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngtest.c

`pngtest.c` is the bundled libpng self-test program. It reads a PNG, writes it back out through libpng, compares input and output bytes, and reports pass/fail. It also exercises optional callback, custom I/O, custom memory, unknown chunk, interlace, text, metadata, and timing paths depending on compile-time feature macros.

Program flow:
- `main` prints libpng/zlib version information, validates header/library version consistency, parses `-m`, `-mv`, `-vm`, `-v`, input, and output arguments, then calls `test_one_file`.
- In single-file mode it runs the same input up to three times with different progress verbosity behavior.
- In multi-file mode it reuses `pngout.png` or the configured output as a temporary comparison output.
- `test_one_file` opens input/output, creates read/write structs and info structs, sets error handling and setjmp recovery, initializes I/O, reads PNG info, copies metadata from read info to write info, streams all rows from reader to writer, reads/writes end info, destroys structs, closes files, then byte-compares original and output.

Metadata copying:
- Copies `IHDR`, cHRM, gAMA, iCCP, sRGB, PLTE, bKGD, hIST, oFFs, pCAL, pHYs, sBIT, sCAL, text, tIME, tRNS, and unknown chunks when the matching feature macros are enabled.
- For unknown chunks, preserves recorded chunk locations by calling `png_set_unknown_chunk_location` after `png_set_unknown_chunks`.
- Calls `png_set_keep_unknown_chunks` on read/write structs so test output can retain configured unknown chunks.

Callbacks and optional test hooks:
- `read_row_callback` and `write_row_callback` print progress characters for row callbacks.
- `count_filters` is a read user transform callback that counts filter bytes used by decoded rows.
- `count_zero_samples` is a write user transform callback that counts zero-valued samples/pixels.
- Under `PNG_NO_STDIO`, local `pngtest_read_data`, `pngtest_write_data`, and `pngtest_flush` validate custom I/O callbacks.
- Under `PNG_USER_MEM_SUPPORTED && PNG_DEBUG`, `png_debug_malloc` and `png_debug_free` track allocations, detect leaks, poison memory on allocate/free, and print allocation diagnostics in verbose mode.
- Optional `PNGTEST_TIMING` records decode, encode, and miscellaneous CPU time.

Important dependencies and state:
- Includes `png.h` plus standard C headers or Windows CE APIs depending on platform.
- Uses zlib `ZLIB_VERSION`, libpng public APIs, optional feature macros, and setjmp-based libpng error handling.
- Static globals track verbosity, progress dot state, tIME display state, zero-sample/filter counters, and debug allocation state.

Edge cases and risks:
- The byte-for-byte comparison can legitimately fail when compression level, filter heuristics, zlib version, maximum IDAT size, or unknown chunk handling differ; the program documents this and prints diagnostic hints.
- The program is a regression harness, not a comprehensive transform tester. It mostly validates read/write preservation and basic row streaming.
- Much of the file is conditional portability code for old platforms, far pointers, Windows CE, no-stdio builds, custom memory, and optional callbacks.
- Error cleanup paths must keep read/write structs, row buffers, and file handles paired with the correct libpng owner because setjmp can exit from deep library calls.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngtest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngtrans.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngtrans.c

`pngtrans.c` implements row transform configuration APIs and several shared read/write row transformation routines. It is used by both reader and writer paths to set transformation flags in `png_struct` and to mutate row buffers according to those flags.

Configuration APIs:
- `png_set_bgr` enables RGB/BGR channel swapping.
- `png_set_swap` enables 16-bit byte swapping when the image bit depth is 16.
- `png_set_packing` expands sub-8-bit samples to packed 8-bit user depth.
- `png_set_packswap` reverses packed pixel order inside bytes for 1-, 2-, or 4-bit pixels.
- `png_set_shift` records significant-bit shifting parameters.
- `png_set_interlace_handling` enables interlace handling and returns `7` passes for interlaced images or `1` otherwise.
- `png_set_filler` configures filler insertion/removal location and updates expected user channel count for RGB or grayscale inputs.
- `png_set_add_alpha` wraps `png_set_filler` and marks alpha addition.
- `png_set_swap_alpha`, `png_set_invert_alpha`, and `png_set_invert_mono` enable alpha/mono inversion or swapping flags.
- `png_set_user_transform_info` records user transform pointer/depth/channel metadata where supported.
- `png_get_user_transform_ptr` returns the user transform pointer when that feature is compiled in.

Row transformation routines:
- `png_do_invert` inverts grayscale data, including gray-alpha rows while preserving alpha bytes.
- `png_do_swap` swaps byte order for all 16-bit samples.
- `png_do_packswap` uses static 256-byte lookup tables for 1-, 2-, and 4-bit packed-pixel bit-order reversal.
- `png_do_strip_filler` removes filler or alpha bytes/words from RGB/RGBA and grayscale/gray-alpha rows, updates channels, pixel depth, rowbytes, and optionally clears the alpha color-type bit.
- `png_do_bgr` swaps red and blue components for RGB/RGBA rows at 8-bit and 16-bit depths.

Important dependencies and state:
- Includes `png.h` with `PNG_INTERNAL`.
- Operates on `png_struct` transformation flags and `png_row_info` row metadata.
- Compile-time feature macros select which transforms are available for read, write, legacy, and user-transform builds.

Edge cases and risks:
- These functions mutate row buffers in place; pointer increments and row metadata updates must stay synchronized.
- Packed-pixel transforms depend on correct `row_info->bit_depth` and `row_info->rowbytes`.
- `png_do_strip_filler` has separate first-pixel handling in filler-after 16-bit/RGB paths, so changes here can easily introduce off-by-one row corruption.
- Public configuration setters generally assume a valid `png_ptr`; unlike many metadata setters, they do not consistently null-guard.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngtrans.c -->