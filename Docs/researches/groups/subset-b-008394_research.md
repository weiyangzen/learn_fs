# subset-b-008394 Research

Grouped research for FoundationDB `contrib` support code. Each section preserves the original source path and is intended to be split into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/boost_zstd/zstd.cpp -->
# sources/storage-engines/foundationdb/contrib/boost_zstd/zstd.cpp

## Purpose
Implements Boost.Iostreams zstd filter support by adapting the zstd C streaming API (`ZSTD_CStream`, `ZSTD_DStream`, `ZSTD_inBuffer`, `ZSTD_outBuffer`) to the `boost::iostreams::detail::zstd_base` abstraction declared by Boost headers. It supplies compression defaults, status/flush constants, error wrapping, stream initialization, buffer handoff, and compressor/decompressor execution.

## Important APIs, Types, And Functions
The file defines constants in `boost::iostreams::zstd`: `best_speed`, `best_compression`, `default_compression`, `okay`, `stream_end`, and flush actions `finish`, `flush`, `run`. `zstd_error::check(size_t)` converts zstd error codes into Boost exceptions. `detail::zstd_base` owns opaque `cstream_`, `dstream_`, `in_`, and `out_` pointers, with methods `before`, `after`, `deflate`, `inflate`, `reset`, and `do_init`.

## Control Flow
Construction allocates one compression stream, one decompression stream, and one input/output buffer pair. `before()` maps Boost buffer pointer ranges into zstd buffer structs. `deflate()` compresses available input, then optionally flushes or ends the stream depending on the action. `inflate()` repeatedly calls `ZSTD_decompressStream()` while both input and output progress are possible to satisfy Boost's expectation around short reads. `after()` writes consumed/produced positions back to caller pointers. `reset()` and `do_init()` zero buffers and initialize the selected zstd stream.

## State And Persistence
State is in-memory only. `level` stores the selected compression level, and `eof_` tracks whether a finish action completed. No files or durable metadata are written.

## Dependencies And Integration
Depends on libzstd and Boost.Iostreams internals. It is compiled as part of the Boost zstd shim under FoundationDB contrib rather than FoundationDB runtime logic directly. Integration is through Boost filter classes in `<boost/iostreams/filter/zstd.hpp>`.

## Risks
The code assumes all zstd allocation calls succeed; null stream pointers are not checked before use. Custom allocator parameters to `do_init()` are accepted but ignored. `inflate()` returns stream status based on action and empty buffers rather than zstd frame completion result, so behavior is tied to Boost's filter contract. The compression `level` must be initialized before `reset(compress=true, realloc=true)` is meaningful.

## Test Signals
Useful tests are round-trip compression/decompression, flush and finish behavior with tiny output buffers, corrupt input error propagation, repeated reset/reuse, and empty-input finish handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/boost_zstd/zstd.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/branch_diff.py -->
# sources/storage-engines/foundationdb/contrib/branch_diff.py

## Purpose
Command-line helper that compares two git branches and emits a Markdown table of merged GitHub pull requests associated with non-merge commits present in `TO` but not `FROM`.

## Important APIs, Types, And Functions
`parse_args()` defines `--from`, `--to`, and optional `--output`. `diff_branches_by_commit()` runs `git log FROM..TO --no-merges --oneline` and returns short commit hashes. `PullRequestInfo` stores PR number, author, title, and associated commits. `get_pr_from_commit()` calls GitHub CLI `gh pr list` against `apple/foundationdb`. `render_markdown_table()` writes the final `PR ID`, `Author`, `Title` table.

## Control Flow
`main()` parses arguments, gathers diff commits, queries GitHub for each commit, deduplicates by PR number, prints progress, and renders to stdout or an output file. Missing PRs are logged to stderr and skipped.

## State And Persistence
No persistent state except the optional output Markdown file. It relies on local git repository state and GitHub CLI auth/session state.

## Dependencies And Integration
Requires `git`, `gh`, network access, and JSON output from GitHub CLI. It is a release/maintenance utility independent from FoundationDB server code.

## Risks
`line[:9]` on split output can produce an empty hash for a trailing newline. The first GitHub search result is trusted even if multiple PRs match. Author name may be absent or empty. Output files are opened without context management. Broad `except:` hides malformed response details. Markdown table cells are not escaped.

## Test Signals
Mock `subprocess.run` for git and gh failure/success paths; test empty diffs, duplicate PRs, output rendering with pipes in titles, and missing author fields.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/branch_diff.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/commit_debug.py -->
# sources/storage-engines/foundationdb/contrib/commit_debug.py

## Purpose
Converts FoundationDB `CommitDebug` trace XML events into Chrome tracing JSON duration spans, making commit pipeline latency phases visible in `chrome://tracing`.

## Important APIs, Types, And Functions
`locationToPhase` maps trace `Location` values to synthetic begin/end events such as `Commit`, `CommitVersion`, `Resolver.PipelineWait`, `Resolver.Conflicts`, `Proxy.Processing`, `TLog.PipelineWait`, and `TLog.FSync`. `CommitDebugHandler` is an SAX handler that emits JSON trace events. `do_file()` parses plain or gzip XML. `main()` accepts a trace file, `.xml.gz`, or directory of gzipped traces.

## Control Flow
For each `Event` element of type `CommitDebug`, the handler establishes a relative start time, derives `pid`/`tid` from `Machine`, and either records a begin timestamp or emits a complete duration event when a matching end location is encountered. Directory input is merged chronologically into `combined.xml.gz` before parsing.

## State And Persistence
Writes the output trace JSON file. For directory input it may create and reuse `combined.xml.gz`. In-memory `_data` tracks active spans keyed by machine and synthetic span name.

## Dependencies And Integration
Uses Python stdlib `xml.sax`, `gzip`, `glob`, `heapq`, and JSON. Input format is FoundationDB trace XML with `CommitDebug` event locations matching `locationToPhase`.

## Risks
The output intentionally starts with `[ ` and leaves the closing bracket to Chrome tracing, so it is not strict JSON. Python 3 gzip returns bytes, but directory merge code compares/writes string literals and bytes together, which can fail unless run in a Python 2-like mode or adjusted. Unknown `Location` values raise `KeyError`. The output file handle is not closed explicitly. SAX parse errors are printed and processing continues with partial output.

## Test Signals
Use a tiny XML with ordered begin/end events to validate emitted `ts`, `dur`, `pid`, and `tid`; test gzipped file and directory merge paths; include missing end, unknown location, malformed XML, and Python 3 byte/string behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/commit_debug.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/convert.py -->
# sources/storage-engines/foundationdb/contrib/convert.py

## Purpose
Interactive utility for converting between Unix timestamps and FoundationDB versions using the system-key Timekeeper map in a specific cluster.

## Important APIs, Types, And Functions
The script initializes `fdb.api_version(730)` and opens a hard-coded cluster file. `find_version_for_timestamp()` scans `\xff\x02/timeKeeper/map/` for the nearest version at or before/after a timestamp. `find_timestamp_for_version()` does a binary search over Timekeeper keys to estimate a timestamp for a version. CLI subcommands are `getVersion` and `getTime`.

## Control Flow
`getVersion` parses three timestamps and prints corresponding start/end/mutation versions. `getTime` parses one version, calls the binary search helper, and prints Unix and local formatted time. Both transactional helpers enable system-key and lock-aware reads.

## State And Persistence
The script does not mutate the database. It reads FoundationDB system keys in snapshot transactions. The only persistent dependency is the hard-coded cluster file path.

## Dependencies And Integration
Requires the FoundationDB Python binding and access to a live cluster with Timekeeper data. It integrates with internal system key encoding via `fdb.tuple` and `fdb.KeySelector`.

## Risks
The cluster file is environment-specific and prevents general use without editing the file. `strinc()` is referenced but not defined, so the `start=False` branch in `find_version_for_timestamp()` is broken. Binary search uses `ts_cur`/`version_cur` after loops where they may not be assigned if the range is empty. The code assumes timestamps and versions are monotonic enough for interpolation and uses a fixed `1e6` versions/sec estimate outside recorded bounds.

## Test Signals
Mock transactions and Timekeeper ranges for exact match, before-min, after-max, empty map, and nearest-boundary lookups. A real integration test needs a disposable cluster with system key reads enabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/convert.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/crc32/CMakeLists.txt -->
# sources/storage-engines/foundationdb/contrib/crc32/CMakeLists.txt

## Purpose
Builds the CRC32/CRC32C support library used by FoundationDB contrib code.

## Important APIs, Types, And Functions
Defines static library target `crc32` from `crc32.S`, `crc32_wrapper.c`, and `crc32c.cpp`. Disables clang-tidy for both C and C++ on the target. Adds a Clang-only `-Wno-unused-function` workaround. Publishes `include/` as a public include directory.

## Control Flow
CMake evaluates the target unconditionally, then conditionally applies the warning flag when `CLANG` is true.

## State And Persistence
No runtime state. It affects build graph state and include propagation.

## Dependencies And Integration
Integrates the mixed C/C++/assembly CRC implementation into the FoundationDB CMake build. Consumers include headers under `crc32/`.

## Risks
The static target always lists PowerPC assembly, relying on preprocessor guards inside `crc32.S` for non-PowerPC platforms. The warning suppression is broad across the target. Build behavior depends on project-level definition of `CLANG`.

## Test Signals
Configure and build on x86_64, aarch64, and ppc64 where available; verify public includes and that `crc32c_append` links from a consumer target.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/crc32/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/crc32/crc32.S -->
# sources/storage-engines/foundationdb/contrib/crc32/crc32.S

## Purpose
PowerPC64 vector assembly implementation of CRC computation using POWER8 VPMSUM instructions and Barrett reduction. It is compiled only when `__powerpc64__` is defined.

## Important APIs, Types, And Functions
The exported assembly symbol is `CRC32_FUNCTION_ASM`, defaulting to `__crc32_vpmsum`. ABI signature is `unsigned int __crc32_vpmsum(unsigned int crc, void *p, unsigned long len)`. It includes `crc32_constants.h` or a macro-provided constants header and uses `ppc-asm.h` / `ppc-opcode.h` macros such as `FUNC_START`, `VPMSUMD`, `VPMSUMW`, `MTVRD`, and `MFVRD`.

## Control Flow
The function saves nonvolatile GPR and VMX registers, prepares masks and optional byteswap constants, folds input in 128-byte chunks into eight parallel vector CRC lanes, reduces accumulated 1024-bit state to 64 bits, handles remaining tail chunks, applies Barrett reduction to produce a 32-bit CRC, restores registers, and returns. A short path handles inputs below 256 bytes; a zero-length path returns the original CRC.

## State And Persistence
No persistent state. Runtime state is entirely register and stack scratch state. It reads static constants from the included generated tables.

## Dependencies And Integration
Used by `crc32_wrapper.c` on PowerPC64. Requires assembler support for Power/VMX opcodes and the constants generated for the selected polynomial/reflection mode.

## Risks
Architecture-specific and ABI-sensitive. Correctness depends on 16-byte alignment expectations handled by the C wrapper and on matching `CRC`, `REFLECT`, and endian macros. The file manipulates TOC-relative symbols and register save areas directly, so toolchain differences can break builds. Non-PowerPC builds rely on the top-level guard producing no code.

## Test Signals
Compare against known CRC32C vectors on ppc64 for aligned, unaligned via wrapper, short, long above `MAX_SIZE`, and zero-length buffers. Build with GCC and Clang assemblers in little- and big-endian Power environments if supported.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/crc32/crc32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/crc32/crc32_wrapper.c -->
# sources/storage-engines/foundationdb/contrib/crc32/crc32_wrapper.c

## Purpose
C wrapper around the PowerPC VPMSUM assembly CRC function. It handles byte-wise alignment, tail processing, initial/final XOR, and exposes a configurable public wrapper symbol.

## Important APIs, Types, And Functions
`crc32_align()` is a static table-driven byte loop, with reflected and non-reflected variants selected by `REFLECT`. `CRC32_FUNCTION_ASM` defaults to `__crc32_vpmsum`. `CRC32_FUNCTION` defaults to `crc32_vpmsum` and calls the assembly for aligned bulk input under `__powerpc64__`.

## Control Flow
For PowerPC64, the wrapper optionally XORs the input CRC, processes small buffers entirely with `crc32_align`, pre-aligns the pointer to 16 bytes, sends the aligned bulk length to assembly, processes the tail with `crc32_align`, and applies final XOR. On non-PowerPC64 builds, the function body compiles but simply returns the input CRC because all real work is guarded.

## State And Persistence
No persistent state. Uses generated `crc_table` from `crc32_constants.h` when `CRC_TABLE` is defined.

## Dependencies And Integration
Included by the `crc32` static library. `crc32c.cpp` references `crc32_vpmsum` through `crc32_wrapper.h` in the PowerPC path.

## Risks
The non-PowerPC return-original behavior is safe only if callers never select this backend there. The pointer parameter is mutable `unsigned char*` even though data is read-only. Correctness depends on the generated constants matching assembly polynomial/reflection settings. Macro customization can silently change exported symbol names.

## Test Signals
PowerPC tests should cover lengths below 31 bytes, unaligned starts, aligned bulk, tail bytes, and nonzero initial CRC. Non-PowerPC builds should verify this object does not become the selected implementation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/crc32/crc32_wrapper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/crc32/crc32c-generated-constants.cpp -->
# sources/storage-engines/foundationdb/contrib/crc32/crc32c-generated-constants.cpp

## Purpose
Generated C++ constants for the CRC-32C implementation in `crc32c.cpp`.

## Important APIs, Types, And Functions
Defines `POLY 0x82f63b78`, `LONG_SHIFT 8192`, `SHORT_SHIFT 256`, `table[16][256]`, `long_shifts[4][256]`, and `short_shifts[4][256]`. These arrays are declared `static` and consumed by inclusion into `crc32c.cpp`.

## Control Flow
There is no executable control flow. The compiler initializes static lookup tables used by software CRC and hardware block-combination paths.

## State And Persistence
Read-only process-local static data. No persistence or mutation.

## Dependencies And Integration
Included directly by `crc32c.cpp`, not compiled as an independent translation unit. Generated from Mark Adler / Robert Vazan CRC32C algorithms and marked as altered from original.

## Risks
Manual edits can corrupt CRC correctness. Inclusion as a `.cpp` file means symbol visibility and duplication depend on being included once per translation unit. The table is large and unvalidated at compile time, so regression tests are the main guard.

## Test Signals
Known CRC32C vectors, cross-check hardware and software paths, and randomized incremental append tests are the important validation signals after any regeneration.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/crc32/crc32c-generated-constants.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/crc32/crc32c.cpp -->
# sources/storage-engines/foundationdb/contrib/crc32/crc32c.cpp

## Purpose
Provides the public `crc32c_append()` implementation with runtime hardware acceleration where available and a table-driven software fallback.

## Important APIs, Types, And Functions
Public API is `extern "C" uint32_t crc32c_append(uint32_t crc, const uint8_t* input, size_t length)`. Important internal functions are `append_trivial()`, `append_adler_table()`, `append_table()`, `shift_crc()`, `append_hw()`, `ppc_hw()`, and `isHwCrcSupported()`. Hardware helpers map to Intel SSE4.2 CRC intrinsics, aarch64 inline assembly, or PowerPC wrapper code.

## Control Flow
At load time `hw_available` is initialized from CPUID or architecture macros. Calls to `crc32c_append()` dispatch to PowerPC wrapper, Intel/aarch64 hardware loop, or `append_table()`. Hardware loops align input, process large blocks as three independent CRC streams, combine them with shift tables, then handle trailing bytes. Table fallback aligns to word boundaries and folds 16-byte or 12-byte chunks through lookup tables.

## State And Persistence
Only static process state is `hw_available`. Lookup tables are static read-only data included from `crc32c-generated-constants.cpp`.

## Dependencies And Integration
Includes `crc32/crc32c.h`; includes CPU-specific headers `<cpuid.h>`, `<intrin.h>`, and `<nmmintrin.h>` conditionally. Integrated as the exported CRC32C function from the `crc32` static target.

## Risks
The code uses unaligned `reinterpret_cast` loads that are acceptable on x86 but architecture-sensitive. Aarch64 support assumes CRC instructions are present when `__aarch64__` is defined. PowerPC currently forces `isHwCrcSupported()` false, so `ppc_hw()` appears unreachable through normal dispatch. `hw_available` is computed at static initialization and cannot adapt to process migration or emulation quirks.

## Test Signals
Use known CRC32C vectors, randomized buffer splits to verify incremental appends, forced hardware/software dispatch comparisons, empty input, unaligned input, and large buffers crossing `LONG_SHIFT` and `SHORT_SHIFT` thresholds.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/crc32/crc32c.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/crc32/include/crc32/crc32_constants.h -->
# sources/storage-engines/foundationdb/contrib/crc32/include/crc32/crc32_constants.h

## Purpose
Generated constants header for the PowerPC VPMSUM CRC implementation.

## Important APIs, Types, And Functions
Defines `CRC 0x1edc6f41`, `CRC_XOR`, `REFLECT`, and `MAX_SIZE 32768`. When `CRC_TABLE` is defined it emits `crc_table[]`. When `POWER8_INTRINSICS` is defined it emits aligned vector tables `vcrc_const`, `vcrc_short_const`, and `v_Barrett_const`. For assembler consumers it exposes corresponding labels such as `.constants`, `.short_constants`, and `.barrett_constants`.

## Control Flow
There is no runtime control flow. Preprocessor branches select C constants or assembler sections depending on consumer context.

## State And Persistence
Read-only compile-time/static constants. No persistent behavior.

## Dependencies And Integration
Included by `crc32.S` and `crc32_wrapper.c`, or replaced by `CRC32_CONSTANTS_HEADER`. It is generated by `./crc32_constants -r -x 0x11EDC6F41` from `antonblanchard/crc32-vpmsum`.

## Risks
Very large generated data is easy to corrupt manually. The header has assembler and C/C++ modes in one file, so macro environment matters. Constants must match reflected CRC32C settings expected by the wrapper and assembly.

## Test Signals
Build both assembler and C wrapper consumers, then compare PowerPC CRC output against standard CRC32C vectors for varied lengths and initial CRCs.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/crc32/include/crc32/crc32_constants.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/crc32/include/crc32/crc32_wrapper.h -->
# sources/storage-engines/foundationdb/contrib/crc32/include/crc32/crc32_wrapper.h

## Purpose
Declares the PowerPC-specific C wrapper symbol for VPMSUM CRC.

## Important APIs, Types, And Functions
Under `__powerpc64__`, declares `extern "C" unsigned int crc32_vpmsum(unsigned int crc, unsigned char* p, unsigned long len);`. Uses include guard `FLOW_CRC32_WRAPPER_H` and `#pragma once`.

## Control Flow
Header-only declarations; no executable flow.

## State And Persistence
No state.

## Dependencies And Integration
Included by `crc32c.cpp` in the PowerPC path. Declaration must match `crc32_wrapper.c`.

## Risks
No declaration exists on non-PowerPC, so accidental non-PowerPC uses fail at compile time. The buffer pointer is not const, matching the C wrapper but less precise than the public CRC32C API.

## Test Signals
Compile a PowerPC target including this header from C++ and link against the `crc32` static library.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/crc32/include/crc32/crc32_wrapper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/crc32/include/crc32/crc32c.h -->
# sources/storage-engines/foundationdb/contrib/crc32/include/crc32/crc32c.h

## Purpose
Public C-compatible declaration for CRC-32C append computation.

## Important APIs, Types, And Functions
Declares `extern "C" uint32_t crc32c_append(uint32_t crc, const uint8_t* input, size_t length);`. Documents Castagnoli polynomial `0x82f63b78`, accumulation across buffers, and hardware fallback behavior.

## Control Flow
Header-only declaration and documentation.

## State And Persistence
No state.

## Dependencies And Integration
Includes `<stdint.h>` and `<stdlib.h>`. Consumed by C++ and C-compatible callers linking against the `crc32` target.

## Risks
The unconditional `extern "C"` requires C++ compilation; a pure C compiler would not accept it. The header uses `size_t` from `<stdlib.h>` rather than `<stddef.h>`, which is normally sufficient but less direct.

## Test Signals
Compile from a C++ consumer, link, and verify incremental CRC append behavior. If C consumers are expected, add a C compatibility compile test.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/crc32/include/crc32/crc32c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/ctest_to_joshua.py -->
# sources/storage-engines/foundationdb/contrib/ctest_to_joshua.py

## Purpose
Packages CTest-discovered FoundationDB tests and required binaries into a Joshua-compatible tarball with a generated `joshua_test` runner script.

## Important APIs, Types, And Functions
`JoshuaBuilder` tracks source/build files to include. `add_arg()` rewrites command arguments and includes Python sibling dependencies and JAR classpaths. `_add_arg()` maps files under build dir to `build/...`, files under source dir to `src/...`, executables outside those roots to basename, and rejects unknown files. `_add_file()` strips debug symbols for `bin/` or `lib` archive paths. `get_ctest_json()` invokes `ctest -N --show-only=json-v1`.

## Control Flow
`main()` parses `--build-dir`, `--src-dir`, `--output`, and forwards unknown flags to CTest. It collects test commands, rewrites their args through `JoshuaBuilder`, adds standard FDB binaries and `libfdb_c`, emits a shell runner with library path setup, and writes a gzipped tarball.

## State And Persistence
Writes the output tarball. May create temporary stripped binaries during tar creation. Does not mutate the build or source tree.

## Dependencies And Integration
Requires CTest JSON output, `strip`, Python tarfile support, and FoundationDB build artifacts (`fdbbackup`, `fdbcli`, `fdbmonitor`, `fdbserver`, `mkcert`, `libfdb_c`). Integrates with Joshua test infrastructure.

## Risks
The `if "bin/" in arcfile or "lib" in arcfile` check can strip paths containing `lib` unexpectedly. Assertions handle unknown file locations and can be disabled with optimized Python. The generated script runs all commands with `set -euxo pipefail` and stops on first failure. Shared library selection only distinguishes Darwin vs non-Darwin.

## Test Signals
Use a synthetic CTest JSON with build files, source scripts, JAR classpaths, outside executables, and unknown files. Validate tar contents, executable mode of `joshua_test`, and stripping behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/ctest_to_joshua.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/ddsketch_calc.py -->
# sources/storage-engines/foundationdb/contrib/ddsketch_calc.py

## Purpose
Implements DDSketch bucket mapping math using cubic interpolation for fast log and inverse log calculations.

## Important APIs, Types, And Functions
`DDSketch` exposes constructor `DDSketch(errorGuarantee)`, `fastlog(value)`, `reverseLog(index)`, `getIndex(sample)`, and `getValue(idx)`. Constants `A`, `B`, `C`, `EPS`, `correctingFactor`, `offset`, `multiplier`, and `gamma` define the mapping.

## Control Flow
Construction derives `gamma`, `multiplier`, and offset based on the requested relative error. `getIndex()` approximates log2 of a sample and maps it to a bucket. `getValue()` reverses the mapping with cubic root math and adjusts by `gamma`.

## State And Persistence
Each instance stores derived numeric mapping parameters. No persistence.

## Dependencies And Integration
Depends on NumPy and Python `math`. Used by `ddsketch_conversion.py` and `export_graph.py` to interpret DDSketch JSON buckets.

## Risks
Invalid `errorGuarantee` values near or above 1 can divide by zero or produce invalid gamma. Non-positive samples are not guarded before `np.frexp`. `reverseLog()` can encounter invalid square-root/cube-root domains from unexpected indices. Class attributes are shadowed by instance assignments, which is fine but can confuse readers.

## Test Signals
Round-trip sample-to-bucket-to-value tests across small and large values, invalid error guarantees, monotonicity of indexes, and comparison against a reference DDSketch implementation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/ddsketch_calc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/ddsketch_compare.py -->
# sources/storage-engines/foundationdb/contrib/ddsketch_compare.py

## Purpose
Compares two DDSketch bucket distributions from JSON files using Jensen-Shannon divergence.

## Important APIs, Types, And Functions
`relative_entropy(p, q)` computes KL divergence terms while skipping zero pairs. `relative_entropy_symmetric(dd1, dd2)` normalizes bucket arrays and computes Jensen-Shannon divergence. CLI args select transaction keys, input files, and operation name.

## Control Flow
The script parses arguments, loads both JSON files, verifies matching `errorGuarantee`, extracts bucket arrays, computes divergence, and prints a similarity value where lower is more alike.

## State And Persistence
Read-only file input and stdout output. Opened JSON files are not explicitly closed.

## Dependencies And Integration
Depends on NumPy and the DDSketch JSON schema produced by FoundationDB latency tooling. Pairs with `ddsketch_calc.py` conceptually but does not import it.

## Risks
`--op` is optional in argparse but dereferenced unconditionally. Bucket arrays must have identical lengths or indexing can fail. Empty/all-zero buckets divide by zero. Skipping terms where `q[i] == 0` deviates from strict KL divergence behavior and can understate difference.

## Test Signals
Identical distributions should return 0; disjoint distributions, length mismatch, empty buckets, differing error guarantees, and missing op keys should be tested.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/ddsketch_compare.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/ddsketch_conversion.py -->
# sources/storage-engines/foundationdb/contrib/ddsketch_conversion.py

## Purpose
CLI utility to convert a numeric value to a DDSketch bucket index or a bucket index back to an approximate value.

## Important APIs, Types, And Functions
Arguments are `--error_guarantee`, `--value`, and `--bucket`. It constructs `ddsketch_calc.DDSketch` and calls `getIndex()` and/or `getValue()`.

## Control Flow
After parsing arguments, default error is `0.005` unless overridden. If `--value` is present it prints the bucket; if `--bucket` is present it prints the representative value. Both can be requested in one invocation.

## State And Persistence
No persistent state. Output is printed to stdout.

## Dependencies And Integration
Imports local `ddsketch_calc` as `dd`. Intended for developers inspecting DDSketch bucket mappings.

## Risks
`--value` is typed as int, so fractional latency values cannot be passed despite the DDSketch math accepting floats. It does not require either `--value` or `--bucket`, resulting in a no-op command. Invalid error guarantees are not validated.

## Test Signals
Exercise value-only, bucket-only, both options, no options, custom error, invalid error, and known round-trip expectations.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/ddsketch_conversion.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/debug_determinism/CMakeLists.txt -->
# sources/storage-engines/foundationdb/contrib/debug_determinism/CMakeLists.txt

## Purpose
Builds the `debug_determinism` static instrumentation helper library.

## Important APIs, Types, And Functions
Adds static target `debug_determinism` from `debug_determinism.cpp` and applies `-fPIC` for convenient linking into shared libraries such as `libfdb_c.so`.

## Control Flow
CMake target creation is unconditional; compile option is applied to the target.

## State And Persistence
No runtime state in this file. It changes build artifacts.

## Dependencies And Integration
The target is intended for use with a `TRACE_PC_GUARD_INSTRUMENTATION_LIB` CMake option or sanitizer coverage instrumentation.

## Risks
`-fPIC` is compiler/platform-specific and assumed accepted. No include directories or explicit linkage are declared.

## Test Signals
Configure/build with the instrumentation option and verify the static library can link into a DSO.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/debug_determinism/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/debug_determinism/debug_determinism.cpp -->
# sources/storage-engines/foundationdb/contrib/debug_determinism/debug_determinism.cpp

## Purpose
Implements sanitizer coverage callbacks that record and compare executed control-flow guard IDs to detect nondeterministic execution order.

## Important APIs, Types, And Functions
Defines `__sanitizer_cov_trace_pc_guard_init(uint32_t* start, uint32_t* stop)` and `__sanitizer_cov_trace_pc_guard(uint32_t* guard)`, the callbacks inserted by compiler coverage instrumentation. Internal globals `out` and `in` are `FILE*` handles to `out.bin` and `in.bin`. `loop_forever()` spins on mismatch.

## Control Flow
Initialization opens `in.bin` and `out.bin`, then assigns monotonically increasing guard IDs once per guard section. On each instrumented edge, the callback writes the guard ID to `out.bin`; if `in.bin` is available, it reads the expected ID and loops forever after printing a nondeterminism message on mismatch or premature EOF.

## State And Persistence
Persists the observed trace to `out.bin` and consumes expected trace from `in.bin` in the current working directory. Static counter `N` persists across callback invocations in-process.

## Dependencies And Integration
Requires compiler support for sanitizer coverage guard callbacks. Intended to be linked into instrumented FoundationDB binaries or DSOs.

## Risks
No null check after opening `out.bin`; `fwrite` with a null file pointer would crash. Files are reopened each initialization call before the early-return guard, potentially leaking handles across DSOs or repeated init calls. The infinite loop is intentional for debugging but hazardous in automated environments. Guard assignment order may vary by link/load order across DSOs.

## Test Signals
Run an instrumented deterministic binary twice to produce and replay `out.bin` as `in.bin`; test mismatch detection, missing `in.bin`, unwritable directory, and multiple-DSO initialization.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/debug_determinism/debug_determinism.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/export_graph.py -->
# sources/storage-engines/foundationdb/contrib/export_graph.py

## Purpose
Plots a DDSketch latency distribution from JSON, either interactively or to a PNG file.

## Important APIs, Types, And Functions
CLI arguments are `--txn`, `--file`, optional `--title`, `--savefig`, and `--op`. It uses `ddsketch_calc.DDSketch` to convert bucket indices to approximate latency values and Matplotlib to render the line plot.

## Control Flow
The script loads JSON, extracts `data[txn][op]["buckets"]` and `errorGuarantee`, trims leading/trailing zero buckets, maps bucket indices to values, configures axis formatting and labels, then saves or shows the plot.

## State And Persistence
Reads one JSON file and optionally writes a PNG. No other persistent state.

## Dependencies And Integration
Depends on Matplotlib, local `ddsketch_calc`, and the expected FoundationDB DDSketch JSON schema.

## Risks
The code references `args.t`, but argparse defines `args.txn`; as written this raises `AttributeError`. `--op` is optional but required by indexing. All-zero buckets make `ls[0]` and `ls[-1]` fail. Input file is not closed explicitly.

## Test Signals
Test a minimal non-empty sketch with `--savefig`, all-zero buckets, missing operation, the `args.txn` path, and visual smoke tests for axis values.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/export_graph.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/fdbcstat/fdbcstat -->
# sources/storage-engines/foundationdb/contrib/fdbcstat/fdbcstat

## Purpose
Linux BCC/eBPF utility that attaches uprobes to `libfdb_c.so` and reports FoundationDB C API call rate, average latency, and maximum latency per interval.

## Important APIs, Types, And Functions
Python configuration lists tracked functions: `get`, `get_range`, `get_read_version`, `set`, `clear`, `clear_range`, and `commit`, with `waitfuture` determining whether latency ends at API return or `fdb_future_block_until_ready`. The embedded BPF program defines `starttime`, `startfunc`, and `stats` hash maps plus entry probes and a shared return probe.

## Control Flow
The script parses PID, interval, duration, function filter, and library path. It resolves the library, specializes BPF text with an optional PID filter, compiles BPF, attaches entry uprobes to selected `fdb_transaction_*` symbols, attaches return probes either to transaction functions or `fdb_future_block_until_ready`, then sleeps by interval and aggregates BPF stats into terminal output.

## State And Persistence
Runtime state lives in eBPF maps and a Python aggregation dictionary cleared each interval. No files are written.

## Dependencies And Integration
Requires Linux, BCC Python bindings, kernel uprobe support, sufficient privileges, and a resolvable FoundationDB C client shared library. It observes external FoundationDB client processes.

## Risks
The aggregation path compares `v.cnt > agg[f]['max']` instead of `v.max > agg[f]['max']`, likely underreporting or corrupting max latency updates. Wait-future attribution uses per-thread start maps, so nested/overlapping futures on the same thread can overwrite state. Symbol names may not match all ABI-versioned aliases. Typographical comments do not affect runtime but indicate limited polish. Requires privileges and can fail silently if uprobes do not match.

## Test Signals
Run against a small client issuing known operations, compare counts with client-side instrumentation, test function filters, PID filter, no matching symbols, wait-future operations, and max latency aggregation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/fdbcstat/fdbcstat -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/folly_memcpy/CMakeLists.txt -->
# sources/storage-engines/foundationdb/contrib/folly_memcpy/CMakeLists.txt

## Purpose
Conditionally builds the optimized Folly-derived memcpy assembly library on Unix non-Apple platforms.

## Important APIs, Types, And Functions
When `UNIX AND NOT APPLE`, adds static library `folly_memcpy` from `folly_memcpy.S` and publishes the current directory for `folly_memcpy.h`.

## Control Flow
CMake condition gates target creation by platform.

## State And Persistence
No runtime state. It controls whether the library exists in the build graph.

## Dependencies And Integration
Works with the assembly file's own x86_64 Linux guard and header declarations. Consumers include `folly_memcpy.h`.

## Risks
CMake permits FreeBSD by condition, while the assembly emits code only for `__x86_64__ && __linux__ && !__CYGWIN__`; this can create an empty or unusable archive on some Unix non-Apple platforms. Header declaration requires `__AVX__`, but CMake does not gate target creation on AVX.

## Test Signals
Configure/build on Linux x86_64 with AVX, Linux without AVX, FreeBSD, and macOS to confirm intended target availability.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/folly_memcpy/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/folly_memcpy/folly_memcpy.S -->
# sources/storage-engines/foundationdb/contrib/folly_memcpy/folly_memcpy.S

## Purpose
Folly-derived optimized `memcpy` implementation for x86_64 Linux, using AVX when `__AVX__` is defined and SSE2 otherwise.

## Important APIs, Types, And Functions
Exports global symbol `folly_memcpy` with signature equivalent to `void* folly_memcpy(void* dst, const void* src, uint32_t length)`. Local helper `_memcpy_short` handles lengths 0 through 7 using a nonstandard calling convention.

## Control Flow
`folly_memcpy` saves destination in `%rax` for return, dispatches very short copies to `_memcpy_short`, copies the first and last 8 bytes for small/medium ranges, aligns work into 32-byte groups, then loops over 64-byte chunks using either `movdqu` SSE registers or `vmovdqu` YMM registers. AVX path executes `vzeroupper` before return.

## State And Persistence
No persistent state. It reads and writes caller-provided memory only.

## Dependencies And Integration
Assembled only under `__x86_64__ && __linux__ && !__CYGWIN__`. Intended to be declared by `folly_memcpy.h` under Linux/FreeBSD with AVX.

## Risks
Like standard `memcpy`, overlapping source/destination is undefined. The function accepts a 32-bit length in the public header but uses 64-bit registers, so callers must not pass sizes beyond that contract. Header/CMake/platform guards are not perfectly aligned with the assembly guard. Performance/correctness depends on CPU support matching compile-time AVX selection.

## Test Signals
Byte-for-byte tests for lengths 0 through 128, unaligned source/destination, large buffers, AVX and non-AVX builds, return value identity, and overlap behavior documented as unsupported.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/folly_memcpy/folly_memcpy.S -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/folly_memcpy/folly_memcpy.h -->
# sources/storage-engines/foundationdb/contrib/folly_memcpy/folly_memcpy.h

## Purpose
Header declaration for the optimized Folly memcpy symbol when supported.

## Important APIs, Types, And Functions
Under `(defined(__linux__) || defined(__FreeBSD__)) && defined(__AVX__)`, declares `extern "C" void* folly_memcpy(void* dst, const void* src, uint32_t length);`.

## Control Flow
Header-only conditional declaration.

## State And Persistence
No state.

## Dependencies And Integration
Consumers must include this in C++ builds where `uint32_t` is already available or available from included project headers; this header itself does not include `<stdint.h>`/`<cstdint>`. Links against the `folly_memcpy` target.

## Risks
The declaration guard includes FreeBSD and AVX, while assembly emits code only on Linux x86_64. Missing direct include for `uint32_t` can make standalone inclusion fragile. No fallback declaration exists for SSE2 builds even though assembly has an SSE2 path.

## Test Signals
Standalone compile test including only this header, and platform matrix tests matching CMake and assembly availability.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/folly_memcpy/folly_memcpy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/gen_compile_db.py -->
# sources/storage-engines/foundationdb/contrib/gen_compile_db.py

## Purpose
Transforms `compile_commands.json` for better editor/indexer support, especially mapping generated Flow actor files back to source actor files and adding Swift compile commands from Ninja.

## Important APIs, Types, And Functions
`actorFile()` rewrites build paths and `actor.g.cpp`/`actor.g.h` to source `actor.cpp`/`actor.h`. `rreplace()` replaces the last occurrence of a substring. `actorCommand()` rewrites compile command source path for generated actor C++ commands. Optional `-ninjatool` invokes `ninja -t compdb` to collect Swift commands.

## Control Flow
The script loads an input compile database, optionally builds a map of Swift compile commands from Ninja while filtering header-emission commands, then iterates original commands. It replaces `-DNO_INTELLISENSE` with `-Wno-unknown-attributes`, rewrites generated actor entries to source files, substitutes Swift entries from Ninja when available, and writes the processed JSON.

## State And Persistence
Reads one compile database and writes `processed_compile_commands.json` by default. No other persistent state.

## Dependencies And Integration
Uses Python stdlib JSON, regex, subprocess, and shlex. Integrates with Flow actor generated files and Swift build commands in FoundationDB.

## Risks
Regex `-c (.+)(actor\.g\.cpp)` is greedy and command-string based, so quoted paths or unusual flags can be mishandled. Broad `except:` around Ninja acquisition hides failures. `actorFile()` uses simple string replacement and can rewrite unintended path prefixes. The `-s` help text incorrectly says build directory.

## Test Signals
Synthetic compile database entries for normal C++, actor generated files, actor headers, Swift files with and without Ninja commands, quoted paths, and failed Ninja invocation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/gen_compile_db.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/generate_profile.sh -->
# sources/storage-engines/foundationdb/contrib/generate_profile.sh

## Purpose
Shell helper to generate LLVM profile data for FoundationDB server and Mako workloads from a local build sandbox.

## Important APIs, Types, And Functions
Takes build directory and optional storage engine. Sets `LD_LIBRARY_PATH`, `FDB_CLUSTER_FILE`, and `LLVM_PROFILE_FILE`, launches `fdbmonitor`, configures a single-node database with `fdbcli`, runs Mako build/run workloads, forces `fdbserver` exit with `gdb`, kills `fdbmonitor`, then runs `llvm-profdata merge` into `fdb.profdata` and `mako.profdata`.

## Control Flow
Argument validation accepts one or two args. Default storage engine is `ssd`. Workload flow is start cluster, configure, generate client workload profiles, stop server to flush server profile, kill monitor, merge raw profiles.

## State And Persistence
Writes `.profraw` files under `$fdbdir/sandbox`, merged `$fdbdir/fdb.profdata`, and `$fdbdir/mako.profdata`. Starts and kills local FoundationDB processes.

## Dependencies And Integration
Requires a prepared FoundationDB build/sandbox, `fdbmonitor`, `fdbcli`, `mako`, `/proc`, `gdb`, and `llvm-profdata`. Linux-specific process discovery is used.

## Risks
No `set -euo pipefail`, so failures can cascade. Variables are unquoted. It uses `kill -9` and `gdb` attached to a child PID from `/proc`, which is Linux-specific and potentially hazardous if PID discovery is wrong. Existing profile files may be mixed with new output. The comment says CLI profile is ignored but still writes a raw file.

## Test Signals
Run in an isolated sandbox build, verify process cleanup and profile file creation, test missing binaries, invalid storage engine, failed configure, and repeated runs with stale `.profraw` files.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/generate_profile.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/grv_proxy_model/grv_test.py -->
# sources/storage-engines/foundationdb/contrib/grv_proxy_model/grv_test.py

## Purpose
CLI driver for simulating GRV proxy behavior under selected workload, ratekeeper, proxy model, and limiter implementations.

## Important APIs, Types, And Functions
Imports model registries from `workload_model` and `ratekeeper_model`, proxy/limiter classes from `proxy_model`, `Priority`, and `Plotter`. `print_choices_list()` lists valid workloads, ratekeeper models, proxy classes, and limiters. `validate_class_type()` verifies named classes against required superclasses.

## Control Flow
The script parses workload, ratekeeper, duration, limiter, proxy, list, and graph flags. It currently requires workload and ratekeeper before honoring `--list`. It validates selected names, constructs the limiter and proxy model, runs the simulation, prints latency percentiles and rates per workload priority, and optionally displays plots.

## State And Persistence
State is in the instantiated proxy model and its `results` object. No files are written by this script unless the plotting layer does so externally.

## Dependencies And Integration
Depends on sibling GRV proxy model modules and plotting support. It is a simulation/developer analysis entry point rather than production code.

## Risks
Because workload/ratekeeper validation happens before `--list`, `--list` alone exits with an error after printing choices instead of serving as a pure list command. Percentile indexing uses `int(p * len(latencies))`, which can equal `len` only for 1.0 not used here, but small samples can duplicate indexes. Imported `Priority` is unused. Plot display can block in headless environments unless `--no-graph` is used.

## Test Signals
Run `--list`, invalid model names, valid simulation with `--no-graph`, short duration, empty latency output, and each limiter naming style with and without `Limiter` suffix.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/grv_proxy_model/grv_test.py -->
