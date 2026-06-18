# Group Research: group_1525_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_jpeg_jfdctint_c_sources_822900c0564b

Scope verified against `Docs/research_subset_a.md`: all listed files are under `sources/os/plan9/plan9`, which is included in subset A. Every listed source file was read completely. This group covers IJG JPEG library code embedded under Plan 9 Ghostscript: DCT/IDCT routines, public/private JPEG APIs, the command-line transcoder, and memory-manager back ends.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jfdctint.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jfdctint.c

Slow-but-accurate integer forward DCT implementation, compiled when `DCT_ISLOW_SUPPORTED` is enabled. It is specialized to `DCTSIZE == 8` and intentionally fails compilation otherwise.

The single exported routine is `jpeg_fdct_islow(DCTELEM *data)`, which performs an in-place 8x8 forward DCT using the Loeffler/Ligtenberg/Moschytz alternate method with fixed-point arithmetic. It processes rows first, then columns, leaving the final results scaled by the IJG convention so later quantization removes the remaining factor of 8.

The file defines fixed-point constants for `CONST_BITS == 13`, chooses `PASS1_BITS` based on sample precision, and uses `MULTIPLY16C16` for 8-bit builds. The arithmetic is carefully arranged to avoid multiple multiplications along one data path and to keep 32-bit intermediates within bounds.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jfdctint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jidctflt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jidctflt.c

Floating-point inverse DCT implementation, compiled under `DCT_FLOAT_SUPPORTED`. It is specialized to 8x8 DCT blocks and combines dequantization with IDCT.

The exported `jpeg_idct_float()` uses the Arai/Agui/Nakajima scaled DCT algorithm. It multiplies coefficients by the component floating-point multiplier table, runs a column pass into a local `FAST_FLOAT workspace[DCTSIZE2]`, then runs a row pass into the output sample buffer.

Column processing has a shortcut for all-zero AC terms, filling the workspace column with the dequantized DC value. Final row outputs are descaled by 8 and clipped through `IDCT_range_limit(cinfo)`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jidctflt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jidctfst.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jidctfst.c

Fast, less-accurate integer inverse DCT implementation, compiled under `DCT_IFAST_SUPPORTED`. It uses the AA&N scaled algorithm with only 8 fractional bits for constants and immediate descaling after multiplies.

The exported `jpeg_idct_ifast()` performs dequantization through the component `IFAST_MULT_TYPE` table, runs columns into an integer workspace, then emits rows to the output buffer. For 8-bit samples it favors speed by avoiding an extra dequantization shift; for 12-bit samples it preserves more scaling accuracy.

The code includes column all-zero AC shortcuts and an optional row zero test controlled by `NO_ZERO_ROW_TEST`. Final samples are descaled by `PASS1_BITS + 3` and range-limited.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jidctfst.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jidctint.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jidctint.c

Slow-but-accurate integer inverse DCT implementation, compiled under `DCT_ISLOW_SUPPORTED`. It is the integer IDCT counterpart to `jfdctint.c`, using the LL&M algorithm and fixed-point constants at `CONST_BITS == 13`.

The exported `jpeg_idct_islow()` dequantizes coefficients with the component `ISLOW_MULT_TYPE` table, runs a column pass into an integer workspace, then a row pass into the destination sample buffer. It preserves precision with `PASS1_BITS` and delayed descaling.

The implementation optimizes all-zero AC columns by replicating the DC value, and optionally optimizes all-zero AC rows. Output samples are descaled by the total IDCT scale factor and clipped through the decompressor range-limit table.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jidctint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jidctred.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jidctred.c

Reduced-size inverse DCT routines, compiled under `IDCT_SCALING_SUPPORTED`. The file implements 8x8 coefficient block decoding directly to 4x4, 2x2, or 1x1 output.

Exports:

- `jpeg_idct_4x4()`
- `jpeg_idct_2x2()`
- `jpeg_idct_1x1()`

The 4x4 and 2x2 routines derive reduced outputs from simplified LL&M IDCT steps, skipping columns and coefficients that cannot affect the smaller output. They use the same fixed-point scaling style as `jidctint.c`, with zero-AC shortcuts and range-limited output. The 1x1 path is just the dequantized DC coefficient divided by 8.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jidctred.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jinclude.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jinclude.h

Internal JPEG portability include. It includes `jconfig.h`, marks `JCONFIG_INCLUDED`, and centralizes system header selection for the IJG modules.

It pulls in standard headers for `NULL`, `size_t`, `FILE`, allocation, and string/memory functions based on configuration symbols. It defines `MEMZERO` and `MEMCOPY` either through BSD `bzero`/`bcopy` or ANSI `memset`/`memcpy`.

The header also defines `SIZEOF(object)` as a size_t-cast `sizeof`, plus `JFREAD` and `JFWRITE` wrappers around `fread`/`fwrite` with IJG’s preferred argument order and casts.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jinclude.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jmemansi.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jmemansi.c

Generic ANSI system-dependent memory manager backend. It assumes `malloc`, `free`, and `tmpfile()` are available.

It maps both small and large JPEG allocations to `malloc`/`free`, reports available memory as `cinfo->mem->max_memory_to_use - already_allocated`, and defaults the memory limit to `DEFAULT_MAX_MEM` or 1 MB.

Backing store uses an anonymous `tmpfile()`. The read/write methods seek with `fseek`, transfer with `JFREAD`/`JFWRITE`, and report JPEG temp-file errors through the IJG error manager. Closing the backing store just calls `fclose`, because `tmpfile()` handles deletion.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jmemansi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jmemdos.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jmemdos.c

MS-DOS-specific system memory manager backend. It supports near allocations, far allocations, direct DOS temporary files, XMS extended-memory backing store, and EMS expanded-memory backing store.

The file requires `USE_MSDOS_MEMMGR` and enforces `MAX_ALLOC_CHUNK < 64K`. Small allocations use `malloc/free`; large allocations use `farmalloc/farfree`, `_fmalloc/_ffree`, or ordinary `malloc/free` depending on compiler and memory model.

Backing store selection tries XMS first, EMS second, and DOS files last. XMS access uses the XMS 2.0 move API and handles odd byte counts specially. EMS access uses LIM/EMS 4.0 move-region calls with packed/misaligned field macros. File backing store uses generated temp names from `TMP`, `TEMP`, or the current directory and calls assembly helpers from `jmemdosa.asm`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jmemdos.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jmemdosa.asm -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jmemdosa.asm

8086 MASM-compatible assembly support for `jmemdos.c`. It exposes far-callable routines for DOS file I/O, XMS driver calls, and EMS driver calls.

Implemented entry points:

- `_jdos_open`, `_jdos_close`, `_jdos_seek`, `_jdos_read`, `_jdos_write`
- `_jxms_getdriver`, `_jxms_calldriver`
- `_jems_available`, `_jems_calldriver`

The DOS helpers use interrupt `21h` for file create/close/seek/read/write and return zero on success. The XMS helper discovers the driver via interrupt `2Fh` and calls its far entry point with register context loaded from a C struct. The EMS helper checks for `EMMXXXX0` at interrupt vector `67h` and calls interrupt `67h` with a supplied context. All procedures save and restore broad register sets for compiler compatibility.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jmemdosa.asm -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jmemmac.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jmemmac.c

Classic Mac OS system-dependent memory manager backend, requiring `USE_MAC_MEMMGR`. It uses fixed-address Macintosh Toolbox memory rather than C `malloc`.

Small and large JPEG allocations call `NewPtr` and are freed with `DisposePtr`. `jpeg_mem_available()` uses `CompactMem()` with a slop reserve and respects `max_memory_to_use`. Initialization returns `FreeMem()` as the default memory limit.

Backing store uses System 7 APIs. It checks Gestalt support for FSSpec and FindFolder, creates temp files in the Temporary Items folder, reads/writes with `SetFPos`, `FSRead`, and `FSWrite`, and deletes via `FSpDelete` on close.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jmemmac.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jmemmgr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jmemmgr.c

System-independent IJG memory manager. It provides pool allocation, chunked sample/block arrays, virtual image arrays, backing-store paging, and cleanup policy.

The manager keeps separate small and large allocation pools for `JPOOL_PERMANENT` and `JPOOL_IMAGE`. Small allocations are suballocated from slop-sized pools; large allocations are one allocation per pool node. `alloc_sarray()` and `alloc_barray()` allocate row-pointer arrays plus chunked contiguous row storage, respecting `MAX_ALLOC_CHUNK`.

Virtual arrays are requested as control blocks first, then realized later when total demand is known. `realize_virt_arrays()` computes minimum and maximum memory needs, asks the system backend via `jpeg_mem_available()`, assigns in-memory window heights, and opens backing store when full arrays do not fit. Accessors page sample or block rows in and out, flush dirty buffers, pre-zero undefined rows when requested, and reject invalid access patterns.

`free_pool()` closes backing stores for image-lifetime virtual arrays before freeing large and small pools. `self_destruct()` frees all pools, releases the memory-manager object, and calls system-dependent termination. `jinit_memory_mgr()` validates alignment and allocation limits, initializes backend memory, installs the public method table, and honors `JPEGMEM` unless `NO_GETENV` is defined.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jmemmgr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jmemname.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jmemname.c

Generic system-dependent memory backend for platforms where temporary files must be explicitly named. It is similar to `jmemansi.c` but uses `fopen` on generated filenames instead of `tmpfile()`.

Small and large allocations use `malloc/free`, and available memory is computed from `max_memory_to_use - already_allocated`. The default max memory is 1 MB.

Temporary names are built under `TEMP_DIRECTORY`, defaulting to `/usr/tmp/`. With `mktemp()` available, filenames use a trailing `XXXXXX` template; with `NO_MKTEMP`, the code increments a numeric suffix and probes for non-existing files. Backing store reads and writes use `fseek` plus `JFREAD`/`JFWRITE`; close calls `fclose` and `unlink`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jmemname.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jmemnobs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jmemnobs.c

Minimal no-backing-store memory backend. It assumes all working memory can be obtained directly from `malloc`.

Small and large allocations map to `malloc/free`. `jpeg_mem_available()` always returns `max_bytes_needed`, so the system-independent memory manager should never request backing store. If backing store is still opened, `jpeg_open_backing_store()` raises `JERR_NO_BACKING_STORE`.

`jpeg_mem_init()` returns zero because the `max_memory_to_use` limit is ignored by this backend; termination has no work.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jmemnobs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jmemsys.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jmemsys.h

Interface between `jmemmgr.c` and platform-specific memory backends. No ordinary JPEG module should include it directly.

It declares backend hooks for small and large allocation, available-memory estimation, backing-store opening, and memory subsystem initialization/termination. It also defines `MAX_ALLOC_CHUNK`, defaulting to a large flat-memory value unless overridden by `jconfig.h`.

The central type is `backing_store_info`, which always carries read/write/close method pointers and then backend-private fields. DOS builds store a file/XMS/EMS handle union and temp name; Mac builds store a file reference, `FSSpec`, and name; ordinary builds store a `FILE *` and name.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jmemsys.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jpegint.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jpegint.h

Internal IJG declarations shared by JPEG library modules. Applications normally include only `jpeglib.h`.

It defines buffer-controller pass modes, compression/decompression global-state constants, and the public portions of internal module structs: compressor/decompressor masters, main/prep/post/coefficient controllers, color conversion, downsampling/upsampling, DCT/IDCT, entropy coding, marker reading/writing, and quantization.

The header declares module initialization entry points, utility routines from `jutils.c`, and natural-order coefficient tables. It also provides `MAX`, `MIN`, signed-right-shift portability macros, short external-name mappings for limited linkers, and dummy incomplete-type definitions for broken compilers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jpegint.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jpeglib.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jpeglib.h

Public IJG JPEG library API header for version 6b (`JPEG_LIB_VERSION 62`). It includes `jconfig.h` and `jmorecfg.h`, defines JPEG standard limits, and establishes application-visible data types.

The header defines sample and coefficient array types, quantization and Huffman table structs, component metadata, scan scripts, saved marker lists, color-space enums, DCT method enums, and dithering modes. It defines the common, compression, and decompression master structs, including public parameters, computed state, marker metadata, progress counters, and links to internal submodules.

It also declares the standard error manager, progress manager, source/destination managers, and memory manager interfaces. Exported API prototypes cover object creation/destruction, stdio source/destination setup, compression parameter setup, scanline/raw-data compression and decompression, buffered-image mode, marker saving/processing, coefficient-level transcoding, abort/destroy helpers, restart resynchronization, and marker constants. When `JPEG_INTERNALS` is defined, it includes `jpegint.h` and `jerror.h`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jpeglib.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jpegtran.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jpegtran.c

Command-line JPEG transcoder. It reads JPEG input as DCT coefficients and writes JPEG output, optionally changing coding parameters and applying lossless or near-lossless coefficient-domain transforms.

The switch parser supports marker-copy policy, arithmetic coding, Huffman optimization, progressive output, scan scripts, restart intervals, max memory, output filename, verbosity, grayscale forcing, flips, rotations, transpose/transverse, and trimming non-transformable edge blocks. Transform selection rejects conflicting transform options.

`main()` creates separate decompression and compression objects, parses options once to find files and memory settings, opens input/output streams, sets the decompressor source, configures marker copying, reads the header, requests transform workspace, reads source coefficients, copies critical compression parameters, adjusts destination parameters for transforms, reparses options for final output settings, writes coefficient output, copies selected markers, executes the transform, finishes both JPEG objects, closes files, and exits with warning status if either JPEG object reported warnings.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jpegtran.c -->