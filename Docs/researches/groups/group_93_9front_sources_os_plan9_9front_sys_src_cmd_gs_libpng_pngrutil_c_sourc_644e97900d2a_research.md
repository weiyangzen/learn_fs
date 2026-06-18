# Group Research: group_93_9front_sources_os_plan9_9front_sys_src_cmd_gs_libpng_pngrutil_c_sourc_644e97900d2a

Scope checked against `Docs/research_subset_a.md`: these files are inside `sources/os/plan9/9front`, which is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngrutil.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngrutil.c

This is libpng 1.2.8 internal read-side utility code used by Ghostscript’s bundled libpng copy in the 9front tree. It contains PNG chunk parsing, CRC handling, compressed text/profile decompression, row reconstruction, Adam7 interlace expansion, and row-buffer initialization. It is not filesystem/VFS code; its relevance to subset A is through the complete `sources/os/plan9/9front` source-tree coverage.

Major responsibilities:
- Big-endian scalar readers: `png_get_uint_31`, `png_get_uint_32`, `png_get_int_32`, `png_get_uint_16`.
- CRC path: `png_crc_read`, `png_crc_finish`, and `png_crc_error` read/skip chunk payload bytes and decide whether CRC mismatch is warning or fatal based on critical/ancillary chunk policy flags.
- Compressed ancillary payload handling: `png_decompress_chunk` inflates trailing compressed data for `zTXt`, `iTXt`, and `iCCP`, reallocating output as needed and replacing failed streams with warning/error text behavior.
- Standard chunk handlers: `png_handle_IHDR`, `PLTE`, `IEND`, `gAMA`, `sBIT`, `cHRM`, `sRGB`, `iCCP`, `sPLT`, `tRNS`, `bKGD`, `hIST`, `pHYs`, `oFFs`, `pCAL`, `sCAL`, `tIME`, `tEXt`, `zTXt`, `iTXt`, and unknown chunks.
- Row operations: `png_combine_row`, `png_do_read_interlace`, `png_read_filter_row`, `png_read_finish_row`, and `png_read_start_row`.

Control flow and data flow:
- Chunk handlers enforce PNG ordering rules, validate chunk length and duplicates, read payload through CRC-aware routines, and store validated data through `png_set_*` APIs from `pngset.c`.
- `png_handle_IHDR` initializes `png_struct` image dimensions, bit depth, color type, channel count, rowbytes, and then calls `png_set_IHDR`.
- Metadata handlers generally reject malformed chunks by warning and consuming/skipping remaining bytes with `png_crc_finish`.
- Text/profile handlers allocate a full chunk buffer, locate NUL-separated fields, optionally decompress payload, then pass structured data to `png_set_text_2` or `png_set_iCCP`.
- Unknown chunk handling validates the four-byte chunk name, rejects unknown critical chunks unless configured/user-handled, and optionally saves unknown chunks with location information.
- Row filtering reverses PNG adaptive filters `NONE`, `SUB`, `UP`, `AVG`, and `PAETH`.
- Interlace code expands packed or byte-aligned Adam7 pass rows in place and updates row width/rowbytes.
- `png_read_start_row` computes maximum transformed pixel depth, allocates `big_row_buf`, aligns `row_buf`, allocates `prev_row`, and marks row initialization complete.

Notable implementation details:
- Many handlers are compile-time gated by libpng feature macros.
- `PNG_MAX_MALLOC_64K` paths truncate or reject large ancillary chunks for older memory models.
- Several handlers tolerate technically misplaced chunks with warnings if libpng can still proceed.
- CRC policy distinguishes ancillary and critical chunk behavior using `PNG_FLAG_CRC_*`.
- `png_read_finish_row` drains the zlib stream after the last row and detects extra compressed data.
- Error handling is libpng-style: fatal conditions call `png_error`, warnings call `png_warning` or `png_chunk_warning`.

Important dependencies:
- Public/internal structures and macros from `png.h`.
- zlib `inflate`, `inflateReset`, stream state in `png_ptr->zstream`.
- Storage functions in `pngset.c`.
- Memory and string wrappers such as `png_malloc`, `png_malloc_warn`, `png_free`, `png_memcpy`, `png_strlen`.

Research notes:
- This file is central to PNG read correctness and malformed-input handling.
- It has no direct OS storage, block, filesystem, or VFS behavior.
- Potential audit points are memory allocation size calculations, older 64K compatibility paths, compressed text/profile decompression limits, and unknown critical chunk policy.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngrutil.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngset.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngset.c

This file implements libpng 1.2.8 setter/storage APIs for `png_info` and selected `png_struct` configuration fields. It is used by both readers and writers to store parsed PNG metadata or application-supplied metadata. It is not filesystem code.

Major responsibilities:
- Store simple metadata chunks: `png_set_bKGD`, `png_set_oFFs`, `png_set_pHYs`, `png_set_sBIT`, `png_set_sRGB`, `png_set_tIME`, `png_set_invalid`.
- Store validated color metadata: `png_set_cHRM`, `png_set_cHRM_fixed`, `png_set_gAMA`, `png_set_gAMA_fixed`, and `png_set_sRGB_gAMA_and_cHRM`.
- Validate and store IHDR via `png_set_IHDR`.
- Allocate/copy owned chunk payloads: `png_set_hIST`, `png_set_pCAL`, `png_set_sCAL`/`png_set_sCAL_s`, `png_set_PLTE`, `png_set_iCCP`, `png_set_text`/`png_set_text_2`, `png_set_tRNS`, `png_set_sPLT`, and `png_set_unknown_chunks`.
- Configure behavior: `png_set_keep_unknown_chunks`, `png_set_read_user_chunk_fn`, `png_set_rows`, `png_set_compression_buffer_size`, `png_set_asm_flags`, `png_set_mmx_thresholds`, and `png_set_user_limits`.

Control flow and data flow:
- Most setters return early on NULL `png_ptr` or `info_ptr`.
- `png_set_IHDR` validates dimensions, user limits, bit depth, color type, interlace, compression, and filter method, then derives channel count, pixel depth, and rowbytes.
- Palette, transparency, histogram, text, ICC profile, pCAL/sCAL, sPLT, and unknown chunks allocate storage and copy caller-provided data into libpng-owned buffers.
- Ownership is tracked with `info_ptr->free_me` flags when `PNG_FREE_ME_SUPPORTED` is enabled, otherwise by older `png_ptr->flags` bits for some data.
- Unknown chunk configuration appends five-byte entries: four-byte chunk name plus a per-chunk keep policy.
- Runtime tuning functions update zlib buffer size, assembler/MMX flags, and image dimension limits.

Notable implementation details:
- `png_set_PLTE` always allocates 256 palette entries, not just `num_palette`, preserving behavior for invalid files with oversized sample values.
- `png_set_tRNS` similarly allocates 256 transparency entries when byte alpha data is present.
- `png_set_text_2` grows the text array in batches and stores key/language/text strings in one contiguous allocation per text entry.
- `png_set_iCCP` frees any previous ICC data before storing a copied profile.
- `png_set_sPLT` appears to allocate/copy using `png_sizeof(png_sPLT_t)` for `entries`, although entries are `png_sPLT_entry`; this is inherited libpng 1.2-era code and is worth checking if auditing memory correctness.
- `png_set_unknown_chunks` records chunk location from current `png_ptr->mode`.

Important dependencies:
- Chunk data types and flags from `png.h`.
- Allocation/free helpers including `png_malloc`, `png_malloc_warn`, `png_free_data`, and `png_free`.
- Getter/setter pairings are exercised by `pngtest.c`.

Research notes:
- This file is the main metadata ownership boundary for libpng.
- It has no direct filesystem access.
- Audit attention should focus on allocation-size arithmetic, partial-allocation cleanup on error paths, ownership flags, and old compatibility branches.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngset.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngtest.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngtest.c

This is libpng’s standalone test program. It reads a PNG, writes it back out through libpng, then byte-compares the original and generated files. It validates core chunk handling, row filtering, compression/decompression, metadata copying, optional user transforms, stdio-free I/O hooks, and debug memory hooks. It is not filesystem implementation code, though it performs normal host file I/O for testing.

Major responsibilities:
- Provide `main` command-line handling for single-file and multi-file test modes.
- Implement `test_one_file`, the main read-copy-write-compare workflow.
- Register optional row status callbacks: `read_row_callback`, `write_row_callback`.
- Register optional user transform callbacks: `count_filters` and `count_zero_samples`.
- Provide stdio-free read/write/flush/error shims when `PNG_NO_STDIO` is enabled.
- Provide debug allocation tracking through `png_debug_malloc` and `png_debug_free` when `PNG_USER_MEM_SUPPORTED && PNG_DEBUG`.
- Print version, memory, filter, tIME, and pass/fail diagnostics.

Control flow and data flow:
- `main` parses `-m`, `-v`, `-mv`, input, and optional output file names.
- `test_one_file` opens input/output files, creates read/write structs and info structs, sets `setjmp` handlers, initializes I/O, configures callbacks, and preserves unknown chunks according to compile-time support.
- It reads input metadata with `png_read_info`, retrieves each supported chunk using `png_get_*`, and stores it in the write info struct using corresponding `png_set_*` APIs.
- It writes PNG header/info, reads rows pass-by-pass, writes rows, then reads/writes end info.
- After cleanup, it reopens both files and compares them byte by byte.
- Return value is nonzero on setup/read/write errors; byte differences are reported but return `0` in this older test logic after printing diagnostics.

Notable implementation details:
- `SINGLE_ROWBUF_ALLOC` is enabled unless `PNG_DEBUG` is set, making buffer overruns easier to detect.
- Unknown chunks are read with `PNG_HANDLE_CHUNK_ALWAYS` and written with `PNG_HANDLE_CHUNK_IF_SAFE` where supported.
- In default single-file mode, the same file is tested three times, with status dots enabled on the second pass.
- Debug allocation tracking maintains a linked list of allocations and reports leaks after each test.
- The test warns that byte comparison can fail legitimately if zlib/libpng compression settings differ.
- The final typedef forces a compile error if an older `png.h` is found.

Important dependencies:
- Public libpng API from `png.h`.
- zlib version macro for diagnostics.
- C stdio unless `PNG_NO_STDIO` paths are built.
- Platform branches for Windows CE and RISC OS.

Research notes:
- This file is a useful executable integration test for the surrounding libpng sources.
- It uses file I/O only as a test harness, not as filesystem-layer logic.
- Audit attention should focus on old portability branches, test return semantics, and debug-only allocation tracker behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngtest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngtrans.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngtrans.c

This file implements libpng 1.2.8 row transformation setup and shared read/write row transformation helpers. It toggles transformation flags on `png_struct` and performs in-place byte/pixel rearrangements for rows. It is not filesystem code.

Major responsibilities:
- Transformation setup APIs: `png_set_bgr`, `png_set_swap`, `png_set_packing`, `png_set_packswap`, `png_set_shift`, `png_set_interlace_handling`, `png_set_filler`, `png_set_add_alpha`, `png_set_swap_alpha`, `png_set_invert_alpha`, and `png_set_invert_mono`.
- Row transformation helpers: `png_do_invert`, `png_do_swap`, `png_do_packswap`, `png_do_strip_filler`, and `png_do_bgr`.
- User transform metadata helpers: `png_set_user_transform_info` and `png_get_user_transform_ptr`.

Control flow and data flow:
- Setup APIs primarily OR transformation bits into `png_ptr->transformations` and update related fields such as `usr_bit_depth`, `usr_channels`, `shift`, `filler`, and filler-location flags.
- `png_set_interlace_handling` marks interlace processing and returns `7` passes for interlaced images, otherwise `1`.
- `png_do_invert` inverts grayscale samples for grayscale and grayscale-alpha rows.
- `png_do_swap` swaps bytes in 16-bit samples.
- `png_do_packswap` uses static lookup tables for 1-, 2-, and 4-bit packed pixel order reversal.
- `png_do_strip_filler` removes filler or alpha bytes from RGB/RGBA and grayscale/gray-alpha rows and updates `row_info` channels, pixel depth, rowbytes, and alpha color-type bit.
- `png_do_bgr` swaps red and blue channels for 8-bit and 16-bit RGB/RGBA rows.
- User transform info is stored only when `PNG_USER_TRANSFORM_PTR_SUPPORTED` is compiled in.

Notable implementation details:
- Transform support is heavily compile-time gated.
- Packed-pixel swapping is table-driven for speed and simplicity.
- `png_do_strip_filler` handles before/after filler layouts and both 8-bit and 16-bit samples.
- Functions mutate row buffers in place and must be called in the correct transform order by read/write pipelines elsewhere.
- Some NULL checks are compiled only with `PNG_USELESS_TESTS_SUPPORTED`.

Important dependencies:
- `png_struct`, `png_row_info`, transformation flags, color constants, and feature macros from `png.h`.
- Called by read/write transform pipelines outside this file.

Research notes:
- This is a low-level image row manipulation module.
- It has no direct storage or filesystem responsibilities.
- Audit attention should focus on in-place buffer assumptions, rowbytes/channel updates, and correctness across bit-depth/color-type combinations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngtrans.c -->