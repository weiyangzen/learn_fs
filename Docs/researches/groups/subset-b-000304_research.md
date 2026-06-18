# subset-b-000304 research

Grouped research report for zlib sources under `sources/compression/zlib`. Each section preserves the original source path and is bounded by the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/test/example.c -->
# sources/compression/zlib/test/example.c

## Purpose
`example.c` is the canonical executable smoke test and usage sample for zlib. It demonstrates the one-shot `compress()`/`uncompress()` helpers, gzip file I/O through the `gz*` API, stream-oriented `deflate()`/`inflate()`, full-flush recovery with `inflateSync()`, dynamic compression-parameter changes, and preset dictionary negotiation. In `Z_SOLO` builds it skips helper APIs that are not available and supplies simple allocator hooks.

## Important APIs, Types, and Functions
The file depends on `zlib.h`, `stdio.h`, and optionally `string.h`/`stdlib.h`. It uses `Byte`, `uLong`, `z_stream`, `alloc_func`, `free_func`, `gzFile`, zlib return codes, flush modes, and checksum/version helpers. `CHECK_ERR()` centralizes fatal error handling. `test_compress()` exercises buffer helpers. `test_gzio()` writes and reads a gzip file with `gzopen`, `gzputc`, `gzputs`, `gzprintf`, `gzseek`, `gzread`, `gzgetc`, `gzungetc`, `gzgets`, `gztell`, and `gzclose`. `test_deflate()` and `test_inflate()` force one-byte input/output buffers to stress streaming progress. `test_large_deflate()` changes compression level and strategy with `deflateParams()`. `test_flush()` deliberately corrupts data after a `Z_FULL_FLUSH`; `test_sync()` recovers with `inflateSync()`. `test_dict_deflate()` and `test_dict_inflate()` exercise `deflateSetDictionary()` and `inflateSetDictionary()`.

## Control Flow
`main()` validates runtime/header version compatibility, allocates zeroed compression and decompression buffers, then runs tests in a fixed order. The gzip path is skipped under `Z_SOLO`. Most tests initialize a `z_stream`, set custom or default allocators, repeatedly call zlib functions until `Z_STREAM_END` or expected progress, and finish with `deflateEnd()` or `inflateEnd()`. Dictionary inflate loops until the stream ends, handling `Z_NEED_DICT` by validating `strm.adler` against the saved dictionary id before setting the dictionary.

## State and Persistence Behavior
The only persistent filesystem artifact is the gzip test file, named from argv or a platform-specific default. In-memory state includes the shared `dictId`, stream counters, checksums, buffer contents, and zlib internal states allocated through `zalloc`/`zfree`. The test intentionally mutates compressed bytes to create a damaged block for sync recovery.

## Dependencies and Integration Points
This file is compiled by multiple build scripts and CMake tests as a basic consumer of installed zlib targets. It directly validates public ABI expectations from `zlib.h`, plus gzip file APIs when enabled. Platform-specific `TESTFILE` logic covers VMS and RISC OS path conventions.

## Risks
The test exits on first failure, so later API failures may be hidden. It assumes allocated buffers fit in `uInt` where cast, and it writes/removes files in the current directory. The corruption test depends on exact stream layout around the full flush marker. Gzip APIs are conditionally absent under `NO_GZCOMPRESS` and `Z_SOLO`, reducing coverage in those builds.

## Test Signals
Successful execution prints version/compile flags and positive messages for uncompress, gzread/gzgets, inflate, large inflate, sync recovery, and dictionary inflate. Failures are explicit stderr messages and nonzero exit. It is used by CMake package tests to verify installed shared/static targets.
<!-- END_FILE_RESEARCH: sources/compression/zlib/test/example.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/test/find_package_no_components_test.cmake.in -->
# sources/compression/zlib/test/find_package_no_components_test.cmake.in

## Purpose
This CMake template verifies that an installed or build-tree zlib package can be found with `find_package(ZLIB ... CONFIG REQUIRED)` without specifying components. It checks that default package discovery exposes the expected imported targets for whichever library variants were built.

## Important APIs, Types, and Functions
The file uses CMake 3.12...3.31, declares a C project with version substituted from `@zlib_VERSION@`, and defines `ZLIB_BUILD_SHARED` and `ZLIB_BUILD_STATIC` options from template substitutions. It calls `find_package()` in config mode and then links `test/example.c` against `ZLIB::ZLIB` for shared builds and `ZLIB::ZLIBSTATIC` for static builds.

## Control Flow
CMake first configures the project and options, then loads zlib's config package without components. If shared support is enabled, it adds `test_example`, links the shared imported target, and registers a CTest test except on `.dll` shared-library suffixes. If static support is enabled, it adds `test_example_static`, links `ZLIB::ZLIBSTATIC`, and registers a static test.

## State and Persistence Behavior
The template does not persist application data. CMake generation creates build targets and CTest metadata in the build directory. Substituted values bind the test to the source tree and build options from the zlib build being validated.

## Dependencies and Integration Points
It integrates with `zlibConfig.cmake.in`, exported `ZLIB-shared.cmake`/`ZLIB-static.cmake` files, and `test/example.c`. The no-component path intentionally relies on package config logic to include available component files and create default imported targets.

## Risks
The package config currently requires both imported targets in no-component mode, so a build that intentionally produces only one variant can fail unless the config message guides users to request a component. The shared executable test is skipped for `.dll`, so Windows shared runtime execution is not validated here.

## Test Signals
Configuration fails if `find_package()` cannot load the package or required imported targets are absent. Build/link failures reveal invalid include paths or libraries. CTest execution of `example.c` provides runtime API validation for non-DLL shared builds and all static builds.
<!-- END_FILE_RESEARCH: sources/compression/zlib/test/find_package_no_components_test.cmake.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/test/find_package_test.cmake.in -->
# sources/compression/zlib/test/find_package_test.cmake.in

## Purpose
This CMake template validates explicit component lookup for zlib package config files. It ensures `COMPONENTS shared` produces `ZLIB::ZLIB` when shared builds are enabled, and `COMPONENTS static` produces `ZLIB::ZLIBSTATIC` when static builds are enabled.

## Important APIs, Types, and Functions
It uses `cmake_minimum_required`, `project`, build options substituted from zlib configuration, `find_package(ZLIB ... CONFIG COMPONENTS ... REQUIRED)`, `add_executable`, `target_link_libraries`, and `add_test`. The test executable source is `@zlib_SOURCE_DIR@/test/example.c`.

## Control Flow
The script conditionally executes two independent branches. In the shared branch it calls `find_package()` for the `shared` component, creates `test_example`, links `ZLIB::ZLIB`, and adds a CTest test unless the platform emits `.dll`. In the static branch it calls `find_package()` for the `static` component, creates `test_example_static`, links `ZLIB::ZLIBSTATIC`, and always adds the static CTest test.

## State and Persistence Behavior
No runtime persistence exists in the template itself. It creates CMake targets and test registrations in the consumer build tree. The built `example` executable may create its gzip smoke-test file at runtime.

## Dependencies and Integration Points
This template is a direct consumer of `zlibConfig.cmake.in` component logic and exported target files named by component. It also integrates with CTest and the public zlib headers/libs through the imported targets.

## Risks
Because each component lookup is inside the corresponding build-option branch, the test does not prove that requesting a disabled component fails gracefully. `.dll` runtime tests are skipped, so packaging issues involving DLL deployment can pass configuration and link checks without execution.

## Test Signals
A passing configure confirms component files can be included. A passing build confirms imported target properties are sufficient. Running `example.c` confirms basic zlib API behavior through the selected shared/static library variant.
<!-- END_FILE_RESEARCH: sources/compression/zlib/test/find_package_test.cmake.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/test/find_package_wrong_components_test.cmake.in -->
# sources/compression/zlib/test/find_package_wrong_components_test.cmake.in

## Purpose
This CMake template validates the negative path for zlib package components by requesting `COMPONENTS wrong REQUIRED`. Its role is to ensure the package config rejects unsupported component names instead of silently succeeding.

## Important APIs, Types, and Functions
The key statement is `find_package(ZLIB @zlib_VERSION@ CONFIG COMPONENTS wrong REQUIRED)`. The rest mirrors the positive package tests: substituted build options, optional shared/static `example.c` targets, imported target linkage, and CTest registration.

## Control Flow
CMake configures the project and immediately attempts required package discovery with an unsupported component. Expected behavior is that `zlibConfig.cmake` marks `ZLIB_FOUND` false and emits an unsupported-component message, causing configuration failure. The later target creation branches are only reachable if that negative expectation fails.

## State and Persistence Behavior
No source-controlled state is modified. CMake may leave partial configure logs in the build directory. If the unsupported component were incorrectly accepted, it would proceed to generate normal test targets.

## Dependencies and Integration Points
This file directly exercises the `_ZLIB_supported_components` validation in `zlibConfig.cmake.in`. It is tied to the same `example.c` smoke test targets as the other package templates but primarily tests package metadata rather than zlib runtime behavior.

## Risks
The template is meant to fail configuration. A harness must treat failure as success for this negative test; otherwise it looks like a broken build. If CMake package semantics change around required components, the expected failure mode may need adjustment.

## Test Signals
The desired signal is configure failure with `Unsupported component: wrong`. Unexpected success indicates package config accepts invalid components. If target generation occurs, the negative test has already failed its main purpose.
<!-- END_FILE_RESEARCH: sources/compression/zlib/test/find_package_wrong_components_test.cmake.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/test/infcover.c -->
# sources/compression/zlib/test/infcover.c

## Purpose
`infcover.c` is a white-box coverage driver for inflate-side code. It intentionally feeds crafted byte streams, allocation failures, invalid parameters, internal state mutations, and callback edge cases to cover `inflate.c`, `infback.c`, `inftrees.c`, and `inffast.c` paths that normal API tests do not reach.

## Important APIs, Types, and Functions
The file includes `zlib.h`, then defines `ZLIB_INTERNAL` before including `inftrees.h` and `inflate.h`, allowing direct access to internal structures and `inflate_table()`. Memory tracking is implemented with `struct mem_item`, `struct mem_zone`, `mem_alloc()`, `mem_free()`, `mem_setup()`, `mem_limit()`, `mem_used()`, `mem_high()`, and `mem_done()`. `h2b()` decodes loose hex strings into bytes. `inf()` is the generic inflate runner with configurable chunk size, window bits, output length, gzip-header capture, dictionary handling, `inflateCopy()`, reset, and memory checks. Coverage functions include `cover_support()`, `cover_wrap()`, `cover_back()`, `cover_inflate()`, `cover_trees()`, and `cover_fast()`. `try()` runs raw deflate data through both `inflate()` and `inflateBack()`.

## Control Flow
`main()` prints `zlibVersion()` and calls the coverage groups in order. Each group creates streams, uses asserts for exact expected return codes, and calls `mem_done()` to report high-water usage and leaks. `cover_wrap()` tests invalid wrappers, header/trailer errors, dictionary paths, sync behavior, and memory errors. `cover_back()` validates `inflateBack*` bad-parameter and callback cases using `pull()` and `push()`. `cover_inflate()` and `cover_fast()` run many hand-authored deflate fragments that trigger specific decoder errors and fast-path branches.

## State and Persistence Behavior
State is in-memory only. The memory tracker keeps a LIFO allocation list, current total, high-water mark, allocation limit, non-LIFO count, and rogue-free count. Some tests intentionally modify `struct inflate_state` modes to create otherwise unreachable states. `pull()` has a static input index reset by a `Z_NULL` descriptor.

## Dependencies and Integration Points
This file is intended for coverage builds, as noted by the `./configure --cover && make cover` comment. It depends on zlib internals and therefore tracks implementation details closely. It validates public inflate APIs and private decoder tables used by the inflate implementation.

## Risks
Because it reaches into internal structs, it is brittle across internal refactors even when the public ABI remains compatible. It relies on `assert()`, so compiling with `NDEBUG` would remove the checks. Crafted streams and expected messages must stay synchronized with decoder diagnostics. The custom memory tracker frees leaked blocks at teardown, which prevents leaks from escaping but can hide the original allocation site.

## Test Signals
Success is process exit 0 with stderr progress lines and memory high-water messages. Assertion failures pinpoint regressions in expected return codes, decoder messages, memory behavior, or internal table limits. Coverage tooling should show inflate, inflateBack, inftrees, and inffast branch coverage increases.
<!-- END_FILE_RESEARCH: sources/compression/zlib/test/infcover.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/test/minigzip.c -->
# sources/compression/zlib/test/minigzip.c

## Purpose
`minigzip.c` is a small gzip-like command-line program used as both an example and a test tool. It demonstrates zlib gzip file APIs, stdio integration, pipe mode, file replacement behavior, compression level and strategy selection, and optional memory-mapped compression.

## Important APIs, Types, and Functions
It includes `zlib.h`, stdio, optional standard C headers, optional `mmap` headers, and platform headers for binary mode. `string_copy()` is a bounded copy helper used for filenames and mode strings. In `Z_SOLO`, it defines a local `gzFile` wrapper and replacement `gzopen()`, `gzdopen()`, `gzwrite()`, `gzread()`, `gzclose()`, and `gzerror()` on top of raw `deflateInit2()`/`inflateInit2()`. Normal builds use zlib's `gz*` APIs. `gz_compress_mmap()` optionally compresses a whole regular file through `mmap`. `gz_compress()` and `gz_uncompress()` stream between `FILE*` and `gzFile`. `file_compress()` and `file_uncompress()` implement file-to-file modes. `main()` parses `-c`, `-d`, `-f`, `-h`, `-r`, and `-1`..`-9`.

## Control Flow
`main()` derives behavior from the executable basename (`gunzip` implies decompress, `zcat` implies decompress to stdout), then parses options into `copyout`, `uncompr`, and the gzip write mode string. With no file operands it switches stdin/stdout to binary where needed and uses `gzdopen()`. With files, it either writes to stdout or replaces files by creating/removing `.gz` or unsuffixed counterparts. Compression reads chunks and writes through `gzwrite()`; decompression reads through `gzread()` and writes with `fwrite()`.

## State and Persistence Behavior
The program modifies the filesystem in file mode: compression creates `<file>.gz` and unlinks the original; decompression writes the destination and unlinks the gzip input. Pipe/copyout mode writes stdout and leaves inputs untouched. `prog` stores the program name for diagnostics. `Z_SOLO` mode keeps stream state, error code, and message in its local `gzFile_s`.

## Dependencies and Integration Points
It integrates with zlib gzip APIs, platform binary-mode handling, optional large-file/mmap support, and build systems that compile example utilities. It is intentionally not a full gzip replacement but covers common flows used by downstream packagers.

## Risks
Error handling is deliberately limited. File replacement is not atomic and can remove the source after a successful close without preserving metadata. `file_uncompress()` truncates by `len-3`, which assumes the default `.gz` suffix length and is fragile for nonstandard suffixes such as VMS/RISC OS variants. `Z_SOLO` replacements are simplified and do not implement full gzip utility semantics. `mmap` length is cast to `unsigned`/`int`, which is risky for very large files.

## Test Signals
Successful runs produce compressed/decompressed byte-equivalent data in pipe or file mode. Failures call `error()` or `perror()` and exit nonzero. It exercises public `gz*` behavior and can reveal platform issues around binary mode, unlink, file descriptors, and optional mmap support.
<!-- END_FILE_RESEARCH: sources/compression/zlib/test/minigzip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/treebuild.xml -->
# sources/compression/zlib/treebuild.xml

## Purpose
`treebuild.xml` is a package/build manifest for zlib. It describes the `zlib` package, the library name and dynamic library metadata, public headers, source files, and per-source dependencies for a treebuild-style build system.

## Important APIs, Types, and Functions
The root `<package>` declares name `zlib` and version `1.3.2.1`. The `<library>` element names the library `zlib`, sets `dlversion`, and uses `dlname="z"`. Properties include description, include installation target, and an inline compiler property marked as not implemented. Public include files are `zlib.h` and `zconf.h`. Source entries cover checksum, compression, gzip, deflate, tree, utility, inflate, inflateBack, inftrees, and inffast C files with explicit header dependencies.

## Control Flow
The XML has declarative build flow rather than executable control flow. A build consumer would parse package metadata, install public headers, compile each listed source, and use the dependency lists to rebuild affected objects when headers change.

## State and Persistence Behavior
The file itself does not persist runtime state. It controls build outputs: an installed include directory, a zlib library artifact, and dependency tracking metadata in the build system.

## Dependencies and Integration Points
It maps zlib source files to headers such as `zlib.h`, `zconf.h`, `zutil.h`, `deflate.h`, `trees.h`, `gzguts.h`, `inftrees.h`, `inflate.h`, and `inffast.h`. It integrates zlib into build tooling outside the usual Makefile/CMake paths.

## Risks
The manifest can drift from the actual source list or dependency graph. It does not list tests or example programs. The version and dynamic-library metadata must be kept synchronized with `zlib.h`, pkg-config, CMake config, and release scripts. The inline compiler property is marked as not implemented, so consumers may ignore it.

## Test Signals
A treebuild consumer should be able to build the zlib library and install headers from this manifest. Missing dependency declarations show up as stale object reuse or incomplete rebuilds after header changes. Version mismatches can be caught by comparing generated artifacts to `zlib.h` and package metadata.
<!-- END_FILE_RESEARCH: sources/compression/zlib/treebuild.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/trees.c -->
# sources/compression/zlib/trees.c

## Purpose
`trees.c` implements the deflate-side Huffman coding and block emission machinery. It builds static and dynamic Huffman trees, chooses stored/static/dynamic block encodings, emits block headers and compressed symbols, manages the bit buffer, and tallies literal/match frequencies for `deflate.c`.

## Important APIs, Types, and Functions
The file includes `deflate.h` and relies on `deflate_state`, `ct_data`, `tree_desc`, `static_tree_desc`, and constants such as `L_CODES`, `D_CODES`, `BL_CODES`, `MAX_BITS`, `MIN_MATCH`, and `MAX_MATCH`. Public internal entry points are `_tr_init()`, `_tr_stored_block()`, `_tr_flush_bits()`, `_tr_align()`, `_tr_flush_block()`, and `_tr_tally()`. Core local routines include `bi_reverse()`, `bi_flush()`, `bi_windup()`, `gen_codes()`, `tr_static_init()`, `init_block()`, `pqdownheap()`, `gen_bitlen()`, `build_tree()`, `scan_tree()`, `send_tree()`, `build_bl_tree()`, `send_all_trees()`, `compress_block()`, and `detect_data_type()`. With `GEN_TREES_H`, `gen_trees_header()` regenerates `trees.h`.

## Control Flow
`_tr_init()` initializes global/static tables if needed, attaches tree descriptors to a deflate stream, clears bit-buffer state, and starts the first block. During compression, `_tr_tally()` appends each literal or match to the symbol buffer and increments literal/length or distance frequencies. When a block flush is requested, `_tr_flush_block()` optionally detects text/binary data, builds literal and distance trees, builds the bit-length tree, computes byte costs for dynamic and static encodings, compares those costs to stored-block size, emits the selected block type, compresses symbols, resets block state, and winds up bits for the last block.

## State and Persistence Behavior
Per-stream state is stored in `deflate_state`: dynamic trees, bit-length counts, heap/depth arrays, symbol buffers, pending output buffer, bit buffer, counters, compression-level/strategy flags, and output statistics under debug. Global/static state includes static trees and mapping tables, either compiled from `trees.h` or generated at runtime once for non-ANSI/`GEN_TREES_H` builds. Runtime table initialization can be non-thread-safe when tables are built lazily.

## Dependencies and Integration Points
`deflate.c` calls these `_tr_*` routines to encode blocks. `trees.h` supplies precomputed static tree and code maps for normal ANSI builds. `zutil` helpers/macros provide `put_byte`, `zmemcpy`, tracing, and assertions. The emitted bitstream must match RFC 1951 and the inflate decoder's expectations.

## Risks
This is compression-critical code: off-by-one errors in code lengths, heap handling, bit ordering, pending-buffer overlay checks, or block-size cost calculation can corrupt streams. The `GEN_TREES_H` and non-ANSI paths must remain equivalent to the checked-in generated tables. Stored-block copying assumes enough pending buffer capacity. Conditional flags such as `FORCE_STATIC`, `FORCE_STORED`, `LIT_MEM`, and `NO_INIT_GLOBAL_POINTERS` create multiple behavior variants.

## Test Signals
`example.c`, `minigzip.c`, compression round trips, and RFC-compatible decompressors validate normal output. `infcover.c` includes decoder tests that indirectly depend on valid tree encoding. Debug builds assert bit counts and tree consistency. Regenerating `trees.h` with `-DGEN_TREES_H` should reproduce the checked-in table data.
<!-- END_FILE_RESEARCH: sources/compression/zlib/trees.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/trees.h -->
# sources/compression/zlib/trees.h

## Purpose
`trees.h` is a generated header containing precomputed deflate Huffman tables used by `trees.c` in normal ANSI builds. It avoids runtime construction of static literal/length and distance trees and maps match lengths/distances to deflate code numbers.

## Important APIs, Types, and Functions
The header defines `static_ltree[L_CODES+2]`, `static_dtree[D_CODES]`, `_dist_code[DIST_CODE_LEN]`, `_length_code[MAX_MATCH-MIN_MATCH+1]`, `base_length[LENGTH_CODES]`, and `base_dist[D_CODES]`. The arrays use zlib internal types such as `ct_data` and `uch`, and `_dist_code`/`_length_code` are exported internally with `ZLIB_INTERNAL`.

## Control Flow
There is no executable control flow. `trees.c` includes this header when precomputed tables are allowed. Encoding routines index `_length_code` by normalized match length, `d_code()`/`_dist_code` by distance, and `base_length`/`base_dist` to emit extra bits.

## State and Persistence Behavior
The data is static, read-only table state compiled into the library. It must remain synchronized with `tr_static_init()` and `gen_trees_header()` logic in `trees.c`.

## Dependencies and Integration Points
`trees.h` is included only from `trees.c`, after constants and types are available through `deflate.h`. The inflate side expects streams encoded from these tables to follow the canonical deflate static-tree definitions.

## Risks
Manual edits are high risk because a single table value can create invalid or suboptimal compressed streams. The header is generated with `-DGEN_TREES_H`; regeneration should be used rather than hand modification. Internal symbol visibility matters for `_dist_code` and `_length_code`, which are also referenced by deflate macros.

## Test Signals
Static-block compression/decompression round trips validate the tables. A regenerated header should diff cleanly against this file. Debug assertions in `trees.c` and broad zlib test suites catch inconsistent code maps.
<!-- END_FILE_RESEARCH: sources/compression/zlib/trees.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/uncompr.c -->
# sources/compression/zlib/uncompr.c

## Purpose
`uncompr.c` implements zlib's one-shot memory decompression helpers: `uncompress()`, `uncompress_z()`, `uncompress2()`, and `uncompress2_z()`. These wrap the streaming inflate API for callers that already know the full destination buffer size.

## Important APIs, Types, and Functions
The primary implementation is `uncompress2_z(Bytef *dest, z_size_t *destLen, const Bytef *source, z_size_t *sourceLen)`. It constructs a local `z_stream`, initializes it with `inflateInit()`, feeds source and destination in chunks capped at `(uInt)-1`, calls `inflate(Z_NO_FLUSH)` until completion or error, records consumed input and produced output, and calls `inflateEnd()`. The non-`_z` and non-`2` variants adapt `uLong`/`z_size_t` and source-length pointer/value forms.

## Control Flow
The function first validates null pointers and zero-length buffer cases. If the caller passes `dest == Z_NULL` with zero destination length, it redirects `next_out` to `stream.reserved` because inflate requires a non-null output pointer. It initializes inflate state with default allocators, then loops replenishing `avail_out` from remaining destination capacity and `avail_in` from remaining source length. After inflate stops returning `Z_OK`, it recomputes unused input/output, updates caller lengths, cleans up, and normalizes selected errors.

## State and Persistence Behavior
All state is stack-local except caller-provided source/destination buffers and length outputs. No persistent allocations remain after `inflateEnd()`. `*sourceLen` becomes bytes consumed for `uncompress2*`; `*destLen` becomes bytes produced for all variants.

## Dependencies and Integration Points
This file depends on `zlib.h` and the inflate implementation. It backs public helper APIs declared in `zlib.h` and is used by applications that do not need streaming control.

## Risks
Callers must provide a destination buffer large enough for the entire uncompressed stream; otherwise partial output is written and `Z_BUF_ERROR` may result. Input length and output length are split into `uInt` chunks, so correctness depends on careful accounting for sizes larger than 4 GiB. Wrapper functions dereference `destLen` and `sourceLen` before the core function's null checks, so callers must respect the public API contract.

## Test Signals
Round trips through `compress()`/`uncompress()` in `example.c` validate normal behavior. Tests should cover null arguments, empty destination buffers, truncated streams, dictionary-needed streams normalized to `Z_DATA_ERROR`, oversized lengths, and `uncompress2*` consumed-byte reporting.
<!-- END_FILE_RESEARCH: sources/compression/zlib/uncompr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/watcom/watcom_f.mak -->
# sources/compression/zlib/watcom/watcom_f.mak

## Purpose
`watcom_f.mak` builds zlib with OpenWatcom's flat memory model for DOS targets. It creates a static library and links the `example.exe` and `minigzip.exe` test/example programs.

## Important APIs, Types, and Functions
The makefile defines `C_SOURCE`, `OBJS`, `CC=wcc386`, `LINKER=wcl386`, flat-model DOS CFLAGS (`-mf`, `-bt=dos`, optimization, warnings as errors), and `ZLIB_LIB=zlib_f.lib`. The implicit `.C.OBJ` rule compiles C sources. `wlib` archives all object files. Link commands use `wcl386`; `example.exe` includes `-ldos32a`.

## Control Flow
The default `all` target builds the library, then `example.exe` and `minigzip.exe`. The library target adds object files to `zlib_f.lib` in several `wlib` invocations. The executables depend on the library and their corresponding object files. `clean` deletes objects and the library.

## State and Persistence Behavior
Build outputs are `.obj`, `zlib_f.lib`, `example.exe`, and `minigzip.exe` in the working directory. `clean` removes objects and the library but does not remove executables.

## Dependencies and Integration Points
It targets OpenWatcom tooling and the zlib C source list. It integrates test programs from the zlib test directory when invoked from an expected source layout or with matching include/source paths.

## Risks
The source list can drift from the main build systems. The makefile is DOS/OpenWatcom-specific and uses indentation/continuation syntax that may not port. `clean` leaves executables behind. Warnings-as-errors can break legacy builds as compilers evolve.

## Test Signals
Successful `wmake -f watcom_f.mak` should produce `zlib_f.lib`, `example.exe`, and `minigzip.exe`. Running the example programs provides runtime validation for the flat-model build.
<!-- END_FILE_RESEARCH: sources/compression/zlib/watcom/watcom_f.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/watcom/watcom_l.mak -->
# sources/compression/zlib/watcom/watcom_l.mak

## Purpose
`watcom_l.mak` builds zlib with OpenWatcom's large memory model for DOS targets. It parallels the flat-model makefile but uses 16-bit/large-model compiler and linker settings.

## Important APIs, Types, and Functions
The file defines the same zlib source/object lists as `watcom_f.mak`, but uses `CC=wcc`, `LINKER=wcl`, CFLAGS with `-ml`, and outputs `ZLIB_LIB=zlib_l.lib`. The `.C.OBJ` rule compiles each C source, `wlib` archives objects, and link targets produce `example.exe` and `minigzip.exe`.

## Control Flow
`all` builds `zlib_l.lib` and both executables. The library target invokes `wlib` repeatedly to add grouped object files. `example.exe` and `minigzip.exe` link against the large-model library. `clean` removes `.obj` and `zlib_l.lib`.

## State and Persistence Behavior
The makefile persists build artifacts in the current directory. It does not remove linked executables during cleanup. It does not maintain dependency files, so header changes rely on manual or full rebuilds.

## Dependencies and Integration Points
It integrates zlib with OpenWatcom large-model DOS builds. The large-memory model interacts with zlib configuration in `zconf.h`, especially legacy segmented-memory concerns such as `FAR`, `MAXSEG_64K`, and 16-bit allocation behavior.

## Risks
Source-list drift, stale object reuse, and legacy compiler behavior are the main risks. Large-model builds are sensitive to pointer and allocation assumptions. As with the flat makefile, command syntax is specific to Watcom `wmake`.

## Test Signals
Successful `wmake -f watcom_l.mak` creates `zlib_l.lib`, `example.exe`, and `minigzip.exe`. Running the test programs exercises the large-model ABI and memory configuration.
<!-- END_FILE_RESEARCH: sources/compression/zlib/watcom/watcom_l.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/zconf.h -->
# sources/compression/zlib/zconf.h

## Purpose
`zconf.h` is zlib's generated/current configuration header. It defines symbol prefixing, platform detection, calling conventions, export/import attributes, core scalar and pointer typedefs, large-file types, feature-detection macros, and compatibility mappings used by `zlib.h` and internal source files.

## Important APIs, Types, and Functions
The header controls `Z_PREFIX` remapping for public and internal symbols, including functions, typedefs, and structs. It defines platform macros such as `MSDOS`, `OS2`, `WINDOWS`, `WIN32`, `SYS16BIT`, `MAXSEG_64K`, `UNALIGNED_OK`, `STDC`, and `STDC99`. It defines `z_const`, `z_size_t`, `MAX_MEM_LEVEL`, `MAX_WBITS`, `OF`, `FAR`, `ZEXTERN`, `ZEXPORT`, `ZEXPORTVA`, `Byte`, `Bytef`, `uInt`, `uLong`, `charf`, `intf`, `uIntf`, `uLongf`, `voidpc`, `voidpf`, `voidp`, `z_crc_t`, `z_off_t`, and `z_off64_t`. It conditionally includes `<stddef.h>`, `<limits.h>`, `<sys/types.h>`, `<stdarg.h>`, `<unistd.h>`, and Windows headers.

## Control Flow
Preprocessor control flow first applies optional symbol prefixing, then normalizes operating-system/compiler macros, derives standards support, chooses `z_size_t`, sets default memory/window limits, defines prototypes and far-pointer behavior, configures DLL/calling convention exports, chooses integer and offset types, detects unistd/stdarg availability, and finally applies MVS pragma name maps.

## State and Persistence Behavior
There is no runtime state. The header shapes compile-time ABI and feature state for every translation unit including it. Because it is installed publicly, changes persist into downstream application builds.

## Dependencies and Integration Points
`zlib.h` includes this header. Build systems may generate or configure it from `zconf.h.in`. It integrates with Windows DLL builds, zlib's solo mode, large-file support, MVS, old DOS memory models, and prefixed-symbol builds.

## Risks
This file is ABI-sensitive. Changing typedef sizes, export macros, prefix mappings, or large-file remapping can break binary compatibility or downstream source compatibility. Generated values such as `HAVE_UNISTD_H-0` and `HAVE_STDARG_H-0` must be valid preprocessor arithmetic. Prefix lists must stay synchronized with exported/undocumented APIs.

## Test Signals
Compile zlib and downstream examples across prefixed, DLL, solo, large-file, and legacy-platform configurations. `zlibCompileFlags()` and package tests help confirm type-size and feature assumptions. Header self-consistency is validated by building all zlib sources and installed-target consumers.
<!-- END_FILE_RESEARCH: sources/compression/zlib/zconf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/zconf.h.in -->
# sources/compression/zlib/zconf.h.in

## Purpose
`zconf.h.in` is the template for generating `zconf.h`. It carries the same public configuration surface while leaving selected feature probes and prefix settings available for configure/CMake substitution.

## Important APIs, Types, and Functions
The template defines the same symbol prefixing map, platform normalization, typedefs, export macros, large-file handling, and compatibility macros as `zconf.h`. Template-sensitive areas include `Z_PREFIX` enablement and feature probes for headers such as unistd/stdarg via preprocessor expressions that configure can rewrite.

## Control Flow
Its preprocessor flow mirrors `zconf.h`: optional prefix remapping, platform detection, standard C detection, `z_size_t` selection, memory/window defaults, old-style prototype macros, far pointer/calling convention setup, public typedef definitions, CRC type selection, optional system includes, offset type decisions, large-file function remapping support, and MVS pragma mappings.

## State and Persistence Behavior
No runtime state is stored. The template's persistent effect is through generated `zconf.h`, which becomes an installed public header and compile-time contract.

## Dependencies and Integration Points
It is consumed by configure/CMake/release tooling and must remain aligned with the checked-in `zconf.h`. `zlib.h` and all C sources depend on the generated result. Package builds that support `--zprefix` or platform feature detection rely on this template being substitution-safe.

## Risks
Template drift from `zconf.h` can produce different ABI behavior depending on whether a build uses the generated or checked-in header. Incorrect placeholders or preprocessor expressions can break uncommon platforms. Prefix and type definitions need updates whenever public or internal symbols are added.

## Test Signals
Regenerating `zconf.h` from this template should produce expected configured differences only. Build matrices should include configured and non-configured builds, prefixed builds, solo mode, DLL mode, and large-file configurations.
<!-- END_FILE_RESEARCH: sources/compression/zlib/zconf.h.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/zlib.h -->
# sources/compression/zlib/zlib.h

## Purpose
`zlib.h` is zlib's primary public API and license header. It declares the stream compression/decompression API, gzip file API, utility compression helpers, checksum helpers, versioning, compile flags, large-file variants, initialization macros, and a small set of undocumented/internal compatibility exports.

## Important APIs, Types, and Functions
The header defines version macros `ZLIB_VERSION`, `ZLIB_VERNUM`, and component version fields. Core types include `alloc_func`, `free_func`, `z_stream`, `z_streamp`, `gz_header`, `gz_headerp`, callback types `in_func`/`out_func`, and opaque `gzFile`. Constants cover flush modes, return codes, compression levels, strategies, data type guesses, compression method, and `Z_NULL`. Basic APIs are `zlibVersion()`, `deflateInit`, `deflate`, `deflateEnd`, `inflateInit`, `inflate`, and `inflateEnd`. Advanced APIs include `deflateInit2`, dictionary, copy/reset, parameter tuning, bound/pending/prime/header APIs, `inflateInit2`, dictionary, sync/copy/reset/prime/mark/header APIs, and `inflateBack*`. Utility APIs include `compress*`, `uncompress*`, `gz*` file operations, `adler32*`, and `crc32*`.

## Control Flow
The file is declarative but encodes API lifecycle rules in comments and macros. `deflateInit`/`inflateInit` and related macros expand to underscored functions with `ZLIB_VERSION` and `sizeof(z_stream)` for ABI validation. Stream usage follows initialize, repeatedly provide input/output and call `deflate()` or `inflate()`, then end/reset/copy as needed. Gzip file flow follows `gzopen`/`gzdopen`, buffer/parameter setup before I/O where applicable, read/write/seek/flush operations, then close.

## State and Persistence Behavior
`z_stream` exposes caller-managed buffer pointers and counters while hiding internal state behind `struct internal_state *state`. The application owns `next_in`, `next_out`, allocator hooks, and opaque allocator data. `gzFile` is semi-opaque, but a small exposed `gzFile_s` supports the `gzgetc` macro. Checksums are maintained in `adler`, and gzip file state persists until close. Large-file macros can redirect APIs to 64-bit variants at compile time.

## Dependencies and Integration Points
`zlib.h` includes `zconf.h` or installed `<zconf.h>`, supports C++ linkage, and is consumed by every zlib user. It integrates with RFC 1950/1951/1952 formats, platform ABI conventions, pkg-config/CMake installed targets, and internal implementations across the source tree.

## Risks
This header is the public contract: comment/API mismatches, macro remapping changes, struct layout changes, or typedef changes can break downstream code and binary compatibility. Some functions have subtle nonfatal errors (`Z_BUF_ERROR`), deferred gzip errors, and non-blocking semantics that callers can misuse. The exposed `gzgetc` macro intentionally skips validation for speed. The version string includes a project-specific suffix, so package/version checks must account for exact string expectations.

## Test Signals
Compilation of downstream examples validates declarations and macros. Runtime tests should cover stream lifecycle, flush modes, dictionary negotiation, gzip concatenation/non-blocking behavior, large-file aliases, checksum combine functions, and ABI version mismatch paths. Package tests using `example.c` verify installed headers and libraries agree.
<!-- END_FILE_RESEARCH: sources/compression/zlib/zlib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/zlib.pc.in -->
# sources/compression/zlib/zlib.pc.in

## Purpose
`zlib.pc.in` is the pkg-config template for zlib. It exposes installation prefixes, library directories, include directories, package name/description/version/license, link flags, and compiler flags to downstream build systems.

## Important APIs, Types, and Functions
Template variables are `@prefix@`, `@exec_prefix@`, `@libdir@`, `@sharedlibdir@`, `@includedir@`, and `@VERSION@`. pkg-config fields include `Name`, `Description`, `Version`, `License`, `Requires`, `Libs`, and `Cflags`. `Libs` emits both `-L${libdir}` and `-L${sharedlibdir}` plus `-lz`.

## Control Flow
There is no executable flow. Configure substitutes installation paths/version, installs the `.pc` file, and downstream tools read it to construct compiler/linker command lines.

## State and Persistence Behavior
The generated `.pc` file persists in the install tree and influences downstream builds. It does not store runtime state.

## Dependencies and Integration Points
It integrates with pkg-config consumers and must match the installed library/header layout. It overlaps with CMake package config files and traditional Makefile install metadata.

## Risks
Wrong path substitution breaks downstream compilation or linking. Including both `libdir` and `sharedlibdir` can produce ordering or duplication surprises if they differ. Version must stay synchronized with `zlib.h` and release metadata. `Requires` is empty, which is correct for zlib but should remain intentional.

## Test Signals
After install, `pkg-config --cflags --libs zlib` should point to valid include and library directories. A downstream compile/link smoke test using those flags should succeed and report the expected `zlibVersion()`.
<!-- END_FILE_RESEARCH: sources/compression/zlib/zlib.pc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/zlibConfig.cmake.in -->
# sources/compression/zlib/zlibConfig.cmake.in

## Purpose
`zlibConfig.cmake.in` is the CMake package config template for config-mode `find_package(ZLIB)`. It implements component validation/loading for shared and static variants and sets package failure messages when requested targets are unavailable.

## Important APIs, Types, and Functions
The template defines `_ZLIB_supported_components` as `shared` and `static`. It reads `ZLIB_FIND_COMPONENTS`, loops over requested components, checks membership with `IN_LIST`, includes `ZLIB-${_comp}.cmake` with `OPTIONAL RESULT_VARIABLE`, sets `ZLIB_${_comp}_FOUND`, and manipulates `ZLIB_FOUND` plus `ZLIB_NOT_FOUND_MESSAGE`. Without components, it includes both supported component config files optionally and then verifies `TARGET ZLIB::ZLIB` and `TARGET ZLIB::ZLIBSTATIC`.

## Control Flow
If components were requested, each component must be supported and have a loadable config file; otherwise the package is marked not found. If no components were requested, it attempts to include both variant configs and then requires both default imported targets to exist, emitting guidance to request a specific component when only one library type was built.

## State and Persistence Behavior
It modifies CMake package variables in the consumer configure process. It does not persist runtime state, but generated imported targets from included files become part of the consuming build graph.

## Dependencies and Integration Points
It integrates with exported component files `ZLIB-shared.cmake` and `ZLIB-static.cmake`, and with the package test templates in `test/find_package*.cmake.in`. It is the config-mode counterpart to pkg-config metadata.

## Risks
No-component mode currently marks the package not found if either shared or static target is missing, even if one usable variant exists; this is intentional guidance but can surprise consumers. Unsupported-component handling must happen before optional include results are interpreted. Variable casing follows CMake package conventions and should remain compatible with `find_package_handle_standard_args` behavior if introduced later.

## Test Signals
Positive tests should verify component-specific shared/static lookups and no-component lookup for builds that provide both targets. Negative tests should verify `COMPONENTS wrong REQUIRED` fails with the unsupported-component message and disabled components fail with a component-not-found message.
<!-- END_FILE_RESEARCH: sources/compression/zlib/zlibConfig.cmake.in -->
