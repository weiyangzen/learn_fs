# sources/compression/zlib/contrib/minizip subset-b-000297 research

Work item: subset-b-000297

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/minizip.c -->
# sources/compression/zlib/contrib/minizip/minizip.c

## Purpose
`minizip.c` is the command-line sample program for creating ZIP archives with the MiniZip writer API. It demonstrates how to parse archive options, open or append a ZIP file, collect file metadata, optionally encrypt entries, stream each input file through `zipWriteInFileInZip()`, and close the archive cleanly.

## Important APIs, Types, and Functions
- Uses MiniZip writer APIs from `zip.h`: `zipOpen64()`, `zipOpen2_64()`, `zipOpenNewFileInZip3_64()`, `zipWriteInFileInZip()`, `zipCloseFileInZip()`, and `zipClose()`.
- `filetime()` is platform-specific. Windows uses `FindFirstFileA()` plus DOS date conversion. Unix-like platforms use `stat()` and `localtime()` to fill `tm_zip`; other platforms return no timestamp.
- `check_exist_file()` probes with `FOPEN_FUNC(..., "rb")`.
- `getFileCrc()` computes a source file CRC before encrypted writing, because classic ZIP encryption needs the CRC in advance.
- `isLargeFile()` seeks to end and marks entries needing Zip64 if size is at least `0xffffffff`.
- `main()` owns option parsing, archive open mode selection, entry path normalization, file streaming, and cleanup.

## Control Flow
`main()` prints the banner, parses flags (`-o`, `-a`, compression level `-0` to `-9`, `-p`, `-j`), allocates a 16 KiB buffer, derives the archive name, and prompts before overwriting when needed. It opens the archive in create or append mode, then iterates positional arguments after the ZIP filename. For each input it fills `zip_fileinfo`, strips leading slashes, optionally reduces the stored name to a basename, opens a ZIP entry with `zipOpenNewFileInZip3_64()`, copies source bytes in a loop, and closes the entry. The archive is closed once all entries finish or an error stops the loop.

## State and Persistence
Persistent effects are the output ZIP archive and any append-mode mutation of an existing archive. Runtime state is local: parsed flags, a shared heap buffer, CRC accumulator for encryption, per-entry `zip_fileinfo`, and file handles. No configuration or global state is stored by the program.

## Dependencies and Integration Points
Depends on the MiniZip writer library (`zip.h`), zlib CRC helpers, standard C file APIs, POSIX `stat()`/`utime` headers on Unix-like systems, and Win32 file APIs when built on Windows. On Windows it uses `iowin32.h` with `zipOpen2_64()` to supply Win32 IO callbacks.

## Risks and Edge Cases
The fixed `MAXFILENAME` buffer truncates long archive names before appending `.zip`. `filetime()` on Unix calls `localtime()` even when `stat()` fails, using epoch time. Interactive overwrite prompting makes unattended runs hang unless `-o` or `-a` is supplied. The argument filter for skipped option-like entries is narrow and can treat some filenames beginning with `-` or `/` unexpectedly. Password mode reads the whole source once for CRC and again for compression.

## Test Signals
The MiniZip CMake tests invoke the built `minizip` executable to create test archives, then invoke `miniunzip` and compare extracted content. No direct unit tests target the prompt path, encrypted path, very long path truncation, or Zip64 boundary behavior.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/minizip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/minizip.pc.in -->
# sources/compression/zlib/contrib/minizip/minizip.pc.in

## Purpose
This is the pkg-config template installed for the MiniZip library. It advertises include and linker flags for consumers that discover MiniZip with `pkg-config`.

## Important APIs, Types, and Functions
There are no executable APIs. The template defines `prefix`, `exec_prefix`, `libdir`, and `includedir`, then exposes package metadata: `Name: minizip`, description, version placeholder `@PACKAGE_VERSION@`, zlib license, `Libs: -L${libdir} -lminizip`, private zlib dependency `Libs.private: -lz`, and include flags.

## Control Flow
Build configuration substitutes the `@...@` placeholders, then installs the resulting `.pc` file. pkg-config consumers read the static fields to produce compiler and linker arguments.

## State and Persistence
The generated file is persisted into the install tree. It contains no mutable runtime state.

## Dependencies and Integration Points
Integrates MiniZip with pkg-config based build systems. It assumes the installed library is named `minizip` and that zlib is needed for static/private linkage.

## Risks and Edge Cases
`Requires:` is empty, so consumers relying only on public `Requires` may not see zlib unless they ask for static/private flags. The template does not expose optional bzip2 support. If install layout or library naming changes, this file must be updated with the CMake install/export logic.

## Test Signals
CMake package tests in the same tree exercise CMake config discovery, not this pkg-config template directly. A useful signal would be a post-install `pkg-config --cflags --libs minizip` check in packaging CI.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/minizip.pc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/minizipConfig.cmake.in -->
# sources/compression/zlib/contrib/minizip/minizipConfig.cmake.in

## Purpose
This CMake package configuration template lets downstream projects call `find_package(minizip CONFIG ...)` and import shared and/or static MiniZip targets.

## Important APIs, Types, and Functions
- `_MINIZIP_supported_components` lists valid components: `shared` and `static`.
- `minizip_HAS_BZIP2` records whether the installed package was built with bzip2 support.
- Uses `find_dependency(ZLIB CONFIG ...)` and optionally `find_dependency(BZip2)`.
- Includes generated target files `minizip-shared.cmake` and `minizip-static.cmake`.
- Sets `minizip_<component>_FOUND`, `minizip_FOUND`, and `minizip_NOT_FOUND_MESSAGE` for component validation.

## Control Flow
After dependency setup, the file branches on `minizip_FIND_COMPONENTS`. With explicit components it validates each requested component, includes the matching target file, and marks that component found. Without components it loads both optional target files and expects both `MINIZIP::minizip` and `MINIZIP::minizipstatic` to exist; otherwise it marks the package not found with guidance to request a specific component.

## State and Persistence
The installed config persists build-time choices such as bzip2 enablement and installed target availability. During `find_package()` it mutates CMake cache/package variables only for the current configure run.

## Dependencies and Integration Points
Integrates with CMake package consumers, exported MiniZip target files, zlib's CMake package, and optionally BZip2. The test templates under `contrib/minizip/test` validate component and no-component behavior.

## Risks and Edge Cases
The no-component branch requires both shared and static targets, so installs with only one library type intentionally fail unless the caller requests `COMPONENTS shared` or `static`. Error messages mention `ZLIB::ZLIB` and `ZLIB::ZLIBSTATIC` in conditions that actually test MiniZip targets, which can confuse consumers. Component validation still calls `find_dependency(ZLIB CONFIG COMPONENTS ${minizip_FIND_COMPONENTS})`, assuming zlib component names align with MiniZip component names.

## Test Signals
`find_package_test.cmake.in`, `find_package_no_components_test.cmake.in`, and `find_package_wrong_components_test.cmake.in` cover explicit components, no components, and unsupported component failure.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/minizipConfig.cmake.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/mztools.c -->
# sources/compression/zlib/contrib/minizip/mztools.c

## Purpose
`mztools.c` provides an auxiliary recovery routine, `unzRepair()`, that rebuilds a ZIP central directory from local file headers when the original central directory is missing or damaged.

## Important APIs, Types, and Functions
- Exports `unzRepair(const char *file, const char *fileOut, const char *fileOutTmp, uLong *nRecovered, uLong *bytesRecovered)`.
- Uses local little-endian access macros `READ_8/16/32` and `WRITE_8/16/32`.
- Reads local file header signature `0x04034b50`, writes central directory header `0x02014b50`, and writes end-of-central-directory signature `0x06054b50`.

## Control Flow
The function opens the input ZIP, repaired output, and temporary central-directory output. It scans 30-byte local headers from the input. For each valid local file header it copies the local header, filename, extra field, and compressed data to the repaired output, synthesizes a matching central directory entry into the temporary file, and increments entry and byte counters. Once scanning stops, it writes a final end-of-central-directory record to the temporary file, appends the temporary central directory to the repaired output, closes streams, deletes the temporary file, and returns recovered counts on success.

## State and Persistence
Persistent effects are `fileOut` and the transient `fileOutTmp`. In-memory state includes running output offsets, central-directory offset, recovered entry count, total recovered bytes, fixed filename/extra buffers, and parsed header fields.

## Dependencies and Integration Points
Depends on zlib status codes and `uLong`, includes `unzip.h`, but performs raw `FILE *` IO rather than using `unzFile` callbacks. It is declared in `mztools.h` for consumers that need repair functionality.

## Risks and Edge Cases
The routine only understands classic local headers with 32-bit sizes and does not handle data descriptors, Zip64 extra sizes, multi-disk archives, encryption headers, or very large filename/extra fields beyond 1024 bytes. It trusts local header compressed-size fields for allocation and copying, which can consume large memory or fail on corrupted sizes. It writes central directory offsets and sizes using 32-bit fields, clipping entries above `0xffff`.

## Test Signals
No direct test appears in this subset. Meaningful tests would feed truncated archives with known local headers and verify recovered entry count, output readability, and failure behavior on data-descriptor and Zip64 archives.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/mztools.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/mztools.h -->
# sources/compression/zlib/contrib/minizip/mztools.h

## Purpose
`mztools.h` declares the MiniZip repair helper API exposed by `mztools.c`.

## Important APIs, Types, and Functions
The public API is `unzRepair()`, exported with `ZEXPORT`. It accepts an input ZIP path, repaired output path, temporary central-directory path, and optional output counters for recovered entries and recovered bytes.

## Control Flow
This header has no runtime control flow. It sets an include guard, provides C++ `extern "C"` linkage, includes `zlib.h` when needed, includes `unzip.h`, and declares the repair function.

## State and Persistence
No state is stored in the header. The declared function persists output files when called.

## Dependencies and Integration Points
Consumers include this header alongside MiniZip headers. It depends on `uLong` from zlib and the MiniZip unzip declarations for package context.

## Risks and Edge Cases
The API contract mentions a temporary filename but does not define cleanup semantics on all failure modes; implementation removes the temp file after the merge path. Because the declaration uses filesystem paths rather than MiniZip IO callbacks, alternate IO backends cannot use it directly.

## Test Signals
There are no direct header tests. Compilation of a consumer including `mztools.h` validates linkage declarations; functional testing belongs to `unzRepair()`.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/mztools.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/skipset.h -->
# sources/compression/zlib/contrib/minizip/skipset.h

## Purpose
`skipset.h` is a header-generated skiplist set implementation used by MiniZip to track central-directory file names for `zipAlreadyThere()`. The including translation unit supplies key type, comparison, and cleanup macros.

## Important APIs, Types, and Functions
- Required application definitions: `set_key_t`, `set_cmp(a,b)`, and `set_drop(s,k)`.
- Public generated types/functions: `set_t`, `set_start()`, `set_found()`, `set_insert()`, `set_end()`, `set_ok()`, plus optional `set_alloc()`, `set_free()`, and `set_rand()`.
- Internal types include `set_node_t` and `set_rand_t`.
- Uses a compact PCG32 RNG (`set_seed()`, `set_uniq()`, `set_rand()`) to choose skiplist node heights.

## Control Flow
The application initializes `set.env` with `setjmp()`, then calls `set_start()`. Searches walk from the current maximum depth down to level zero, storing predecessor links in `set->path`. Insert first calls `set_found()`, randomly selects a level by consuming bits from `set->ran`, grows head/path arrays if depth increases, allocates a node, and splices it into all relevant levels. `set_end()` sweeps level zero, calls `set_drop()` for each key, frees node arrays and work nodes, and nulls pointers.

## State and Persistence
All state is in `set_t`: head/path pointers, node under construction for longjmp cleanup, maximum depth, RNG state, random bit cache, and optional allocation counters. There is no persistence outside heap allocations owned by the set and key resources released by `set_drop()`.

## Dependencies and Integration Points
Used directly by `zip.c` with `set_key_t` as `char *`, `strcmp()` comparison, and `set_free()` as the drop operation. It depends on `ints.h` for fixed-width MiniZip integer aliases and on standard allocation, `setjmp`, time, and assertions.

## Risks and Edge Cases
Allocation failure is handled by `longjmp(set->env, ENOMEM)`, so callers must set the environment before operations and clean up with `set_end()`. The include guard prevents multiple generated set specializations in one translation unit. The implementation writes an identifying byte into `head->key`, which assumes the key object storage can tolerate byte access. `set_clear()` is compiled out in this MiniZip use.

## Test Signals
The header comment includes an example test with integer keys and allocation-failure semantics. In this subset, test coverage is indirect through `zipAlreadyThere()` behavior in `zip.c`; no dedicated skiplist unit test is present.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/skipset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/test/CMakeLists.txt -->
# sources/compression/zlib/contrib/minizip/test/CMakeLists.txt

## Purpose
This CMake file defines MiniZip integration tests for installation, CMake package discovery, `add_subdirectory()` consumption, and basic minizip/miniunzip round trips for shared and static builds.

## Important APIs, Types, and Functions
It uses CTest `add_test()` and `set_tests_properties()`, CMake `configure_file()`, generator selection variables, fixtures (`FIXTURES_SETUP`, `FIXTURES_REQUIRED`, `FIXTURES_CLEANUP`), and build options such as `ZLIB_MINIZIP_INSTALL`, `MINIZIP_BUILD_SHARED`, `MINIZIP_BUILD_STATIC`, `MINIZIP_ENABLE_BZIP2`, and `ZLIB_CONTRIB_PREFIX`.

## Control Flow
When install testing is enabled, it optionally installs MiniZip into a test prefix, configures five downstream CMake projects from templates, and runs configure/build tests for package and subdirectory discovery. It marks no-component discovery as expected failure when not both shared and static libraries are built, and always expects the wrong-component test to fail. Separate shared and static blocks prepare test files, run the zipping executable, run the unzip executable, compare extracted output with the original, and clean up using fixtures to enforce order.

## State and Persistence
Tests create configured CMake projects and build directories under `WORK_DIR`, install output under `test_install`, temporary ZIP files, moved/prepared test files, and cleanup artifacts controlled by `test_helper.cm`.

## Dependencies and Integration Points
Integrates the MiniZip build with zlib's top-level CMake variables, generated package config files, installed targets, and the `minizip`, `miniunzip`, `minizipstatic`, and `miniunzipstatic` executables.

## Risks and Edge Cases
The file assumes CMake generator/platform forwarding is sufficient for nested configure runs. Shared executable tests are skipped for `.dll` platforms, reducing Windows coverage. The no-component package test intentionally changes expected outcome based on build variants, so package behavior changes can be masked if build options are not varied in CI. Typos in helper script names would break all round-trip tests.

## Test Signals
This is itself the test orchestration. Strong signals are successful configure/build of exported targets, expected failure for unsupported components, successful ZIP creation/extraction, and exact file comparison for shared/static variants.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/test/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/test/add_subdirectory_exclude_test.cmake.in -->
# sources/compression/zlib/contrib/minizip/test/add_subdirectory_exclude_test.cmake.in

## Purpose
This template creates a downstream CMake project that consumes MiniZip via `add_subdirectory(... EXCLUDE_FROM_ALL)` and verifies exported alias targets remain usable.

## Important APIs, Types, and Functions
It declares MiniZip build options, calls `add_subdirectory(@minizip_SOURCE_DIR@ ... EXCLUDE_FROM_ALL)`, defines `MINIZIP_SRCS` with `ioapi.c`, optional `iowin32.c`, `minizip.c`, and `zip.c`, and links test executables to `MINIZIP::minizip` or `MINIZIP::minizipstatic`.

## Control Flow
The configured project adds MiniZip as an excluded child directory, then conditionally builds shared and/or static sample executables based on configured options.

## State and Persistence
State is confined to the generated downstream build tree. No installed package state is required.

## Dependencies and Integration Points
Exercises in-tree target aliases created by MiniZip's own CMakeLists, including behavior when the subdirectory is excluded from the default build.

## Risks and Edge Cases
Using MiniZip sample sources directly in the consumer executable can blur whether the linked library or local source objects provide symbols. The project name matches the non-exclude template, so logs can be confusing.

## Test Signals
Configure and build success indicate that `EXCLUDE_FROM_ALL` still leaves requested MiniZip targets addressable by downstream targets.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/test/add_subdirectory_exclude_test.cmake.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/test/add_subdirectory_test.cmake.in -->
# sources/compression/zlib/contrib/minizip/test/add_subdirectory_test.cmake.in

## Purpose
This template validates consuming MiniZip as a normal CMake subdirectory.

## Important APIs, Types, and Functions
It sets MiniZip build options, calls `add_subdirectory(@minizip_SOURCE_DIR@ ...)`, defines sample executable sources, and links against `MINIZIP::minizip` and/or `MINIZIP::minizipstatic`.

## Control Flow
After configuration substitution, CTest configures this as a standalone project. It adds the MiniZip source tree, then conditionally defines one executable per enabled library variant.

## State and Persistence
Generated CMake files and build outputs live in the test work directory. No runtime persistence occurs unless the built sample executable is run elsewhere.

## Dependencies and Integration Points
Exercises MiniZip's subproject integration, alias targets, Windows IO source inclusion, and option propagation from the parent test.

## Risks and Edge Cases
As with the exclude variant, compiling `minizip.c` and `zip.c` directly into the test executable can hide missing transitive include or link details. The template does not run the executable; it only verifies configure/build.

## Test Signals
The parent `CMakeLists.txt` treats configure and build completion as the success criteria for subdirectory consumption.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/test/add_subdirectory_test.cmake.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/test/find_package_no_components_test.cmake.in -->
# sources/compression/zlib/contrib/minizip/test/find_package_no_components_test.cmake.in

## Purpose
This template validates `find_package(minizip CONFIG REQUIRED)` without explicit components.

## Important APIs, Types, and Functions
It calls `find_package(minizip ${minizip_VERSION} CONFIG REQUIRED)`, builds sample executables from MiniZip sources, and links to `MINIZIP::minizip` and `MINIZIP::minizipstatic` when corresponding options are enabled.

## Control Flow
The parent test configures this project after installing or preparing a package path. The project requests the package with no components, then conditionally links to shared and static targets based on substituted build options.

## State and Persistence
Only generated build-tree state is created. The test relies on the installed or build-tree CMake package config being available through the configured prefix or `ZLIB_DIR`.

## Dependencies and Integration Points
Exercises the no-component branch of `minizipConfig.cmake.in`, which expects both shared and static targets unless callers request a specific component.

## Risks and Edge Cases
The parent marks this configure test as `WILL_FAIL` when only one library variant was built. That means a failure is a success signal in one-variant builds and must be interpreted with build options.

## Test Signals
Success when both shared and static are present, expected configure failure otherwise. Link target availability is checked by generated executable targets.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/test/find_package_no_components_test.cmake.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/test/find_package_test.cmake.in -->
# sources/compression/zlib/contrib/minizip/test/find_package_test.cmake.in

## Purpose
This template validates explicit `find_package(minizip CONFIG COMPONENTS shared/static REQUIRED)` calls for downstream consumers.

## Important APIs, Types, and Functions
It conditionally calls `find_package(... COMPONENTS shared REQUIRED)` and/or `find_package(... COMPONENTS static REQUIRED)`, then links sample executables to `MINIZIP::minizip` or `MINIZIP::minizipstatic`.

## Control Flow
The generated project defines common sample sources first. If shared build support is enabled, it finds the shared component and creates `test_example`. If static support is enabled, it separately finds the static component and creates `test_example_static`.

## State and Persistence
State is limited to CMake configure variables, imported targets, and generated build artifacts.

## Dependencies and Integration Points
Directly exercises component-specific branches of the installed MiniZip package config and verifies that target files are included for requested components.

## Risks and Edge Cases
Running `find_package()` twice in one configure, once per component, depends on the config being idempotent with repeated calls. The sample executable includes MiniZip writer sources directly, so it is primarily a package-target availability check rather than a clean external API-only consumer.

## Test Signals
Configure and build success for each enabled component indicate that component-specific package discovery and imported targets work.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/test/find_package_test.cmake.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/test/find_package_wrong_components_test.cmake.in -->
# sources/compression/zlib/contrib/minizip/test/find_package_wrong_components_test.cmake.in

## Purpose
This template verifies that MiniZip's CMake package config rejects unsupported components.

## Important APIs, Types, and Functions
It calls `find_package(minizip ${minizip_VERSION} CONFIG COMPONENTS wrong REQUIRED)`, then defines the same sample executable targets as the positive package tests.

## Control Flow
The parent CTest marks configure as `WILL_FAIL`, so the intended flow stops at package discovery because `wrong` is not in `_MINIZIP_supported_components`.

## State and Persistence
Only CMake configure state is expected, and successful failure should leave no meaningful build artifacts.

## Dependencies and Integration Points
Exercises the unsupported-component branch of `minizipConfig.cmake.in`, including `minizip_FOUND False` and not-found messaging.

## Risks and Edge Cases
If CMake package logic fails to reject the component, the rest of the template may configure and build, turning this into a regression signal. The template still defines targets after the failing call, but those should be unreachable due to `REQUIRED`.

## Test Signals
The expected signal is configure failure. Unexpected configure success indicates broken component validation.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/test/find_package_wrong_components_test.cmake.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/unzip.c -->
# sources/compression/zlib/contrib/minizip/unzip.c

## Purpose
`unzip.c` implements the MiniZip read API for listing ZIP central directories, locating entries, opening the current entry, reading stored/deflated/bzip2 data, optional classic decryption, Zip64 metadata handling, and offset/comment utilities.

## Important APIs, Types, and Functions
- Public open/close and metadata APIs: `unzOpen()`, `unzOpen64()`, `unzOpen2()`, `unzOpen2_64()`, `unzClose()`, `unzGetGlobalInfo()`, `unzGetGlobalInfo64()`, `unzGetGlobalComment()`.
- Directory navigation APIs: `unzGoToFirstFile()`, `unzGoToNextFile()`, `unzLocateFile()`, `unzGetFilePos64()`, `unzGoToFilePos64()`, `unzGetOffset64()`, `unzSetOffset64()`.
- Entry metadata APIs: `unzGetCurrentFileInfo()` and `unzGetCurrentFileInfo64()`.
- Entry read APIs: `unzOpenCurrentFile3()`, compatibility wrappers, `unzReadCurrentFile()`, `unztell64()`, `unzeof()`, `unzGetLocalExtrafield()`, and `unzCloseCurrentFile()`.
- Internal state types: `unz64_s`, `unz_file_info64_internal`, and `file_in_zip64_read_info_s`.

## Control Flow
Opening a ZIP fills IO callbacks, opens the file, searches backwards for a Zip64 EOCD locator first and classic EOCD second, parses central-directory counts and offsets, rejects multi-disk archives, computes `byte_before_the_zipfile` for self-extracting prefixes, allocates `unz64_s`, and positions on the first central-directory entry. Navigation advances `pos_in_central_dir` by fixed header plus variable name/extra/comment lengths. Current-file info parsing reads a central header, optional filename/extra/comment buffers, and Zip64 extra field overrides. Opening an entry checks the local header against central metadata, allocates a read buffer, initializes inflate or bzip2 state when needed, handles password setup, and stores compressed/uncompressed counters. Reading refills compressed input from the archive, decrypts if needed, then either copies stored/raw bytes or inflates/decompresses into the caller buffer while updating CRC and counters. Closing an entry validates CRC when fully read and frees decompressor state.

## State and Persistence
All runtime state is held in the `unz64_s` handle and, when an entry is open, `file_in_zip64_read_info_s`. It tracks archive-level central directory position, current entry metadata, open entry read stream, CRC progress, remaining compressed/uncompressed bytes, decryption keys, and Zip64 status. The reader does not mutate the archive.

## Dependencies and Integration Points
Uses zlib inflate and CRC APIs, MiniZip `ioapi.h` callbacks, optional bzip2 when `HAVE_BZIP2` is enabled, and optional Info-ZIP classic crypto through `crypt.h` unless `NOUNCRYPT` is defined. The public declarations are in `unzip.h`; command-line `miniunzip` and tests consume this API.

## Risks and Edge Cases
Multi-disk ZIP files are unsupported. Some 32-bit compatibility APIs truncate 64-bit sizes and offsets. Bzip2 entries become raw reads when compiled without bzip2 support in one path, which can surprise callers. Password verification only consumes the classic 12-byte encryption header and does not provide modern encryption. `unzLocateFile()` rejects search names at or above `UNZ_MAXFILENAMEINZIP`, and central-directory parsing assumes structurally valid variable-length fields.

## Test Signals
MiniZip round-trip CTest cases indirectly exercise opening, first-file navigation, reading, CRC validation, and extraction. The subset lacks direct tests for Zip64, bzip2, encrypted entries, local extra field reads, random access offsets, malformed central directories, and CRC error reporting.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/unzip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/unzip.h -->
# sources/compression/zlib/contrib/minizip/unzip.h

## Purpose
`unzip.h` is the public MiniZip header for ZIP reading. It defines opaque handles, status codes, metadata structures, and function prototypes for archive navigation and entry extraction.

## Important APIs, Types, and Functions
- Opaque handle `unzFile`, optionally strict-typed under `STRICTUNZIP` or `STRICTZIPUNZIP`.
- Status constants: `UNZ_OK`, `UNZ_END_OF_LIST_OF_FILE`, `UNZ_PARAMERROR`, `UNZ_BADZIPFILE`, `UNZ_INTERNALERROR`, and `UNZ_CRCERROR`.
- Metadata structs: `tm_unz`, `unz_global_info`, `unz_global_info64`, `unz_file_info`, `unz_file_info64`, `unz_file_pos`, and `unz64_file_pos`.
- API groups cover open/close, global info/comment, file navigation/location, current file info, open/read/close current entry, tell/eof, local extra field reads, and raw central-directory offsets.

## Control Flow
The header defines the callable surface but no implementation. The intended caller sequence is open archive, inspect global info, navigate or locate an entry, retrieve current-file metadata, open current file, repeatedly read, close current file, and finally close the archive.

## State and Persistence
The caller receives an opaque `unzFile` whose state is implemented in `unzip.c`. Header-defined structures are caller-visible snapshots of archive and entry metadata.

## Dependencies and Integration Points
Includes zlib and MiniZip IO callback declarations. Optionally includes `bzlib.h` when `HAVE_BZIP2` is defined. It is consumed by MiniZip utilities, `mztools`, and external applications embedding MiniZip.

## Risks and Edge Cases
The 32-bit metadata and position APIs can truncate Zip64 values. `unzOpen64()` takes `const void *` to allow wide-character paths through custom callbacks, which weakens type clarity. Compression method constant `Z_BZIP2ED` is exposed even when bzip2 support is optional.

## Test Signals
Compilation of consumers validates declarations. Functional signals come from tests using `miniunzip` and package consumers that include this header.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/unzip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/zip.c -->
# sources/compression/zlib/contrib/minizip/zip.c

## Purpose
`zip.c` implements the MiniZip writer API for creating, appending to, and closing ZIP archives, including local and central header generation, Zip64 support, optional bzip2 compression, optional classic encryption, duplicate-name detection, and extra-field cleanup.

## Important APIs, Types, and Functions
- Public open APIs: `zipOpen()`, `zipOpen64()`, `zipOpen2()`, `zipOpen2_64()`, and `zipOpen3()`.
- Entry APIs: `zipOpenNewFileInZip4_64()` as the main implementation, compatibility wrappers down to `zipOpenNewFileInZip()`, `zipWriteInFileInZip()`, `zipCloseFileInZipRaw64()`, and `zipCloseFileInZip()`.
- Archive close and utilities: `zipClose()`, `zipAlreadyThere()`, and `zipRemoveExtraInfoBlock()`.
- Internal state types: `zip64_internal`, `curfile64_info`, central-directory `linkedlist_data`, skipset `set_t`, and `block_t`.
- Internal writers/parsers handle little-endian values, EOCD search, Zip64 EOCD emission, local-header patching, UTF-8 flag detection, and central directory caching.

## Control Flow
`zipOpen3()` initializes IO callbacks, opens or creates the archive, optionally loads an existing central directory for append mode, and prepares linked-list storage. Opening a new entry closes any already-open entry, validates method/field lengths, sets flags for compression level, encryption, and UTF-8 names, builds an in-memory central header, writes the local header with placeholder CRC/sizes, initializes deflate or bzip2 state, and writes an encryption header when needed. `zipWriteInFileInZip()` updates CRC and either compresses into an internal buffer or copies stored/raw input, flushing buffered compressed bytes to the output stream. Closing an entry finishes compression, flushes pending bytes, ends compressor state, computes final sizes, patches central header fields, adds Zip64 extra data when thresholds require it, patches the local header or local Zip64 extra field, appends the central header to the linked-list directory, and advances entry count. `zipClose()` writes the accumulated central directory, emits Zip64 EOCD records if entry count or offsets overflow classic fields, writes the classic EOCD and global comment, closes the stream, and frees state.

## State and Persistence
Persistent output is the ZIP archive, possibly appended to an existing file. `zip64_internal` tracks the open file stream, central-directory blocks, current open entry, beginning offset for self-extracting prefixes, append offset adjustments, entry count, optional previous global comment, and a lazily built skipset for name lookups. `curfile64_info` tracks compressor streams, local header position, central header buffer, flags, CRC, encryption state, Zip64 offsets, and compressed/uncompressed totals.

## Dependencies and Integration Points
Uses zlib deflate/CRC, MiniZip `ioapi.h` callbacks, optional bzip2 compression, optional `crypt.h`, and `skipset.h`. Public declarations live in `zip.h`; `minizip.c` exercises this API. Append mode reads existing central directories using internal EOCD parsers compatible with `unzip.c` concepts.

## Risks and Edge Cases
Multi-disk ZIP files are unsupported. Raw mode requires callers to supply correct CRC and uncompressed size and to strip Zip64 extra blocks when copying entries. `zipRemoveExtraInfoBlock()` reads `short` fields via unaligned casts and assumes well-formed extra data. `zipOpenNewFileInZip4_64()` writes into `central_header` before checking allocation failure, a potential null dereference on allocation failure. Zip64 local extra space must be requested up front via the `zip64` argument, or large sizes become fatal at close. Classic encryption is weak and requires precomputed CRC.

## Test Signals
CTest round-trip cases exercise creating archives through the CLI and reading them back. No direct tests in this subset cover append mode, `zipAlreadyThere()`, Zip64 boundaries, bzip2 compression, encryption, raw copy mode, allocation failure, or malformed extra fields.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/zip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/zip.h -->
# sources/compression/zlib/contrib/minizip/zip.h

## Purpose
`zip.h` is the public MiniZip writer header. It declares archive creation, entry creation, entry writing, archive closing, duplicate checking, and extra-field helper APIs.

## Important APIs, Types, and Functions
- Opaque handle `zipFile`, optionally strict-typed under `STRICTZIP` or `STRICTZIPUNZIP`.
- Status constants: `ZIP_OK`, `ZIP_EOF`, `ZIP_ERRNO`, `ZIP_PARAMERROR`, `ZIP_BADZIPFILE`, and `ZIP_INTERNALERROR`.
- `tm_zip` and `zip_fileinfo` describe entry timestamps and attributes.
- Append modes: `APPEND_STATUS_CREATE`, `APPEND_STATUS_CREATEAFTER`, and `APPEND_STATUS_ADDINZIP`.
- API families include `zipOpen*()`, `zipOpenNewFileInZip*()`, `zipWriteInFileInZip()`, `zipCloseFileInZip*()`, `zipAlreadyThere()`, `zipClose()`, and `zipRemoveExtraInfoBlock()`.

## Control Flow
The header describes the normal write sequence: open an archive, open each entry with desired metadata/compression/raw/encryption/Zip64 settings, write entry bytes, close the entry, and close the archive with an optional global comment.

## State and Persistence
State is hidden behind `zipFile` and implemented in `zip.c`. Caller-visible structures carry per-entry metadata into the writer.

## Dependencies and Integration Points
Includes zlib and MiniZip IO callback declarations, and optionally bzip2 declarations. It is consumed by `minizip.c`, package tests, and external applications.

## Risks and Edge Cases
Many compatibility wrappers expose overlapping parameter sets; callers must choose the Zip64-aware variants for large files. Raw mode and encryption have strict preconditions documented only in comments. The 32-bit close API can truncate raw uncompressed sizes. `zipAlreadyThere()` is declared as a convenience but returns non-standard negative values for invalid central directory and memory failure.

## Test Signals
Compilation of sample utilities validates the declarations. Runtime coverage comes from `minizip` round-trip tests and any downstream package tests that build sample consumers.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/zip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/pascal/zlibd32.mak -->
# sources/compression/zlib/contrib/pascal/zlibd32.mak

## Purpose
`zlibd32.mak` is a legacy Borland C++ makefile for building zlib as `zlib.lib` plus `example.exe` and `minigzip.exe` under Win32 for Delphi/C++ Builder use.

## Important APIs, Types, and Functions
The makefile defines tool variables `CC=bcc32`, `LD=bcc32`, `AR=tlib`, calling convention flags `-DZEXPORT=__fastcall` and `-DZEXPORTVA=__cdecl`, object lists for zlib sources, explicit object dependencies, targets `all`, `test`, executable links, and `clean`.

## Control Flow
The default target builds the static library and sample executables. Pattern rule `.c.obj` compiles C sources with Borland options. The library target deletes any existing `zlib.lib`, then invokes `tlib` twice with split object lists to fit old command-line limits. `test` runs `example` and pipes text through `minigzip` and decompression. `clean` deletes generated object, executable, library, debug, backup, and sample gzip files.

## State and Persistence
Build outputs are `.obj`, `.lib`, `.exe`, `.tds`, backup, and `foo.gz` files in the working directory. No runtime state is managed by the makefile.

## Dependencies and Integration Points
Targets the Borland/Delphi Win32 toolchain and zlib source layout. It integrates zlib's C ABI with Delphi calling conventions through preprocessor definitions.

## Risks and Edge Cases
The file is toolchain-specific and likely stale for modern compilers. The command-line splitting reflects historical DOS limits. Cleanup uses Windows `del` syntax and assumes local build output. Source dependency lists must be maintained manually when zlib source files change.

## Test Signals
The `test` target provides a basic library smoke test through zlib's sample programs. There is no automated signal in the CMake MiniZip tests for this makefile.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/pascal/zlibd32.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/puff/CMakeLists.txt -->
# sources/compression/zlib/contrib/puff/CMakeLists.txt

## Purpose
This CMake build script defines the `puff` contrib library, a small deflate decompressor, including shared/static targets, tests, coverage support, install rules, and package exports.

## Important APIs, Types, and Functions
It configures options `ZLIB_PUFF_BUILD_SHARED`, `ZLIB_PUFF_BUILD_STATIC`, `ZLIB_PUFF_BUILD_TESTING`, and `ZLIB_PUFF_INSTALL`; imports zlib components when built standalone; creates aliases `PUFF::PUFF` and `PUFF::PUFFSTATIC`; builds `puff.c`/`puff.h`; creates test helper executable `puff_bin-writer`; installs export files `puff-shared.cmake` and `puff-static.cmake`; and generates `puffConfig.cmake` plus version file.

## Control Flow
When built from zlib, top-level zlib options are copied into puff-specific cache variables. Standalone builds find zlib with required components matching requested shared/static outputs. Testing enables CTest, adjusts compiler flags for coverage discovery on GNU/Clang, builds `bin-writer`, and adds the `test` subdirectory. Shared and static library blocks define targets and properties. Install rules export requested targets, install debug symbols on MSVC where applicable, generate package config files, and install `puff.h`.

## State and Persistence
Persists build targets, generated package config files, install exports, installed headers, and optional test/coverage artifacts. Cache variables control feature state across CMake runs.

## Dependencies and Integration Points
Integrates with zlib's top-level build via `ZLIB_BUILD_PUFF`, `ZLIB_BUILD_SHARED`, `ZLIB_INSTALL`, and `ZLIB_CONTRIB_PREFIX`; with CMake package helpers; with `puff/test`; and with downstream consumers through `PUFF::` imported targets.

## Risks and Edge Cases
Option descriptions mention "blast" in a puff file, suggesting copied text. Resetting `CMAKE_C_FLAGS` during coverage setup can affect tests under this directory. The standalone `find_package(ZLIB REQUIRED COMPONENTS ...)` assumes zlib component exports match `shared` and `static`. Windows naming and PDB install behavior differ by compiler/platform.

## Test Signals
`ZLIB_PUFF_BUILD_TESTING` enables the puff test subdirectory and coverage helper detection. Successful shared/static target builds and package install/export generation are the primary build signals.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/puff/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/puff/Makefile -->
# sources/compression/zlib/contrib/puff/Makefile

## Purpose
This makefile provides a simple non-CMake build and coverage test workflow for the `puff` deflate decompressor.

## Important APIs, Types, and Functions
Targets include `puff`, object dependencies for `puff.o` and `pufftest.o`, smoke `test`, coverage binary `puft`, coverage target `cov`, and `clean`. It uses `cc`, `gcov`, `xxd`, shell pipelines, and raw byte sequences.

## Control Flow
The default `puff` target links `puff.o` and `pufftest.o`. `test` runs `puff zeros.raw`. `puft` builds with GCC coverage flags. `cov` removes old coverage files, runs many valid and invalid deflate byte streams through `puft`, checks expected exit codes for malformed cases, and finally runs `gcov -n puff.c`. `clean` removes binaries, objects, and coverage output.

## State and Persistence
Creates local binaries (`puff`, `puft`), object files, `.gcov`, `.gcda`, and `.gcno` files. The coverage target reads `zeros.raw` and generated binary stdin streams.

## Dependencies and Integration Points
Integrates with `puff.c`, `puff.h`, `pufftest.c`, `zeros.raw`, `xxd`, POSIX shell, and gcov. It is a lightweight alternative to the CMake test setup.

## Risks and Edge Cases
The coverage target assumes `xxd`, `gcov`, and shell exit-code semantics. It hardcodes expected return codes from `pufftest`, so changes to error-code mapping require updates. `CFLAGS=-O` is minimal and may not reflect production warnings or sanitizer settings.

## Test Signals
The `cov` target is a strong branch/error-path signal: it feeds crafted deflate inputs expected to exercise success and many failure paths, then reports coverage for `puff.c`.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/puff/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/puff/bin-writer.c -->
# sources/compression/zlib/contrib/puff/bin-writer.c

## Purpose
`bin-writer.c` is a tiny test utility that converts textual hexadecimal byte pairs from standard input into binary bytes on standard output.

## Important APIs, Types, and Functions
The only function is `main()`. It uses `getchar()` to read two hex characters, `strtol(..., 16)` to convert them, and `fwrite()` to emit one byte.

## Control Flow
The loop reads a first character, reads the next character as the second hex digit, null-terminates a two-character buffer, converts it to a byte, writes the byte to stdout, then reads and discards one separator character. EOF on the separator read terminates the loop.

## State and Persistence
No files are opened and no persistent state is stored. The program streams stdin to stdout using a fixed three-byte local buffer and temporary conversion variables.

## Dependencies and Integration Points
Built by `contrib/puff/CMakeLists.txt` for tests. It depends only on the C standard library headers `stdio.h` and `stdlib.h`.

## Risks and Edge Cases
The program assumes every byte is represented by two consecutive hex characters and ignores `endptr`, so malformed input still writes a converted value. If EOF occurs while reading the second hex digit, that `EOF` value is cast to `char` and converted as part of the pair. It discards exactly one separator character, so inputs without separators are parsed incorrectly after the first byte. The comment says separators can be spaces, newlines, commas, etc., but the implementation does not skip arbitrary-length separators.

## Test Signals
Coverage and test scripts can use this utility to pipe hex fixture text into binary streams. There are no direct unit tests for malformed or separator-heavy input.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/puff/bin-writer.c -->
