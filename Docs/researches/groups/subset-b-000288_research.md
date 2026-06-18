# subset-b-000288 research

Grouped research report for the requested XZ Utils common helpers, liblzma public API headers, build fragments, and integrity-check implementation files. Each section is keyed by original source path for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_physmem.c -->
# sources/compression/xz/src/common/tuklib_physmem.c

Purpose: implements `tuklib_physmem()`, a portability helper that returns total physical RAM in bytes for many operating systems, or zero when unavailable.

Important APIs/types/functions: exports `uint64_t tuklib_physmem(void)` through the symbol-prefixing macro in `tuklib_physmem.h`. The implementation is a compile-time OS/backend switch covering Windows/Cygwin `GlobalMemoryStatusEx`, OS/2 `DosQuerySysInfo`, DJGPP DPMI, VMS `LIB$GETSYI`, Amiga/AROS `AvailMem`, QNX syspage `asinfo`, AIX `_system_configuration.physmem`, POSIX `sysconf`, BSD `sysctl`, Tru64 `getsysinfo`, HP-UX `pstat_getstatic`, IRIX inventory, and Linux `sysinfo`.

Control flow: the function initializes `ret` to zero, executes exactly one backend selected by preprocessor defines, converts the platform result to bytes, and returns `ret`. Some backends multiply page counts or kilobytes by page size; QNX sums all `asinfo` entries named `ram`; sysctl accepts either 32-bit or 64-bit results.

State and persistence: stateless and side-effect light. It reads kernel/system metadata only; no caches, heap allocation, or persistent handles are kept.

Dependencies/integration: built into liblzma via `src/liblzma/Makefile.am` with `-DTUKLIB_SYMBOL_PREFIX=lzma_`, then wrapped by `src/liblzma/common/hardware_physmem.c` as public `lzma_physmem()`. The xz CLI uses `lzma_physmem()` to choose memory limits and thread policies.

Risks: correctness depends on configure selecting the right backend macros and on platform APIs returning total RAM semantics compatible with xz's resource-limit decisions. Multiplications must stay in `uint64_t`; legacy or unusual systems can fail and yield zero. The Cygwin path deliberately avoids old `sysconf()` behavior. QNX sums ranges and could double count if system metadata semantics changed.

Test signals: `tests/test_hardware.c` calls `lzma_physmem()` and treats zero as skip-like diagnostic rather than hard failure. CLI resource-limit behavior in `src/xz/hardware.c` indirectly exercises the integration.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_physmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_physmem.h -->
# sources/compression/xz/src/common/tuklib_physmem.h

Purpose: declares the portable physical-memory helper used internally by liblzma and other xz components.

Important APIs/types/functions: includes `tuklib_common.h`, wraps declarations with `TUKLIB_DECLS_BEGIN/END`, maps `tuklib_physmem` through `TUKLIB_SYMBOL(tuklib_physmem)`, and declares `extern uint64_t tuklib_physmem(void)`.

Control flow: no runtime control flow. The header establishes C/C++ linkage and symbol-prefix behavior at compile time.

State and persistence: no state. The returned value and failure behavior are implemented in the `.c` file.

Dependencies/integration: depends on `tuklib_common.h` for integer types, linkage macros, and symbol prefixing. `src/liblzma/Makefile.am` compiles the `.c` file into liblzma with prefix `lzma_`, allowing `hardware_physmem.c` to wrap it without exporting raw tuklib names.

Risks: callers must treat zero as unknown/error and not as a real RAM size. Any change to symbol prefixing affects library-private ABI and the public `lzma_physmem()` wrapper.

Test signals: validated indirectly by `tests/test_hardware.c` through `lzma_physmem()` and by build/link tests that require the prefixed symbol to resolve.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_physmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_progname.c -->
# sources/compression/xz/src/common/tuklib_progname.c

Purpose: initializes a global program-name pointer used in diagnostics, with DOS-like cleanup of `argv[0]`.

Important APIs/types/functions: defines `char *progname` when `HAVE_PROGRAM_INVOCATION_NAME` is unavailable and exports `tuklib_progname_init(char **argv)`. Uses `<string.h>` helpers `strlen` and `strrchr`.

Control flow: on `TUKLIB_DOSLIKE`, the initializer mutates `argv[0]` presentation by stripping path components, truncating a dot suffix such as `.exe`, and lowercasing ASCII uppercase letters. It then assigns global `progname = argv[0]`. On non-DOS-like systems, it simply stores the original `argv[0]`, unless the header maps `progname` to libc `program_invocation_name`.

State and persistence: persistent process-global pointer only. It borrows storage from the application's argument vector and, on DOS-like builds, mutates that storage in place.

Dependencies/integration: paired with `tuklib_progname.h`; used by command-line tools and common message code that want a stable program-name variable independent of libc availability.

Risks: assumes `argv` and `argv[0]` are non-NULL and writable on DOS-like systems. The suffix stripping removes any final extension, not only `.exe`, because it truncates at the last dot. Borrowed pointer lifetime is process lifetime for normal `argv`, but not guaranteed if embedded callers pass temporary storage.

Test signals: no direct test found in this subset. Diagnostics tests or command-line output comparisons would expose regressions in displayed program names.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_progname.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_progname.h -->
# sources/compression/xz/src/common/tuklib_progname.h

Purpose: declares the program-name global and initializer used by xz common diagnostic code.

Important APIs/types/functions: includes `tuklib_common.h` and `<errno.h>`, maps `progname` to `program_invocation_name` when available, otherwise declares prefixed `extern char *progname`; maps and declares `tuklib_progname_init(char **argv)`.

Control flow: no runtime flow. Preprocessor selection decides whether the project uses libc's invocation name or its own global variable.

State and persistence: exposes a process-global string pointer, either provided by libc or by `tuklib_progname.c`. The header itself does not own storage.

Dependencies/integration: used by command-line programs before emitting errors or warnings. `TUKLIB_SYMBOL` avoids name collisions when tuklib helpers are embedded into libraries or tools.

Risks: exposing `progname` as a macro/global can collide with application symbols if prefixing is misconfigured. Callers must initialize it early unless relying on libc `program_invocation_name`.

Test signals: diagnostics output and startup paths are the meaningful checks; there is no isolated unit test in this item.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_progname.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/Makefile.am -->
# sources/compression/xz/src/liblzma/Makefile.am

Purpose: top-level Automake recipe for building `liblzma.la`, installing pkg-config metadata, including feature-specific source fragments, and handling Windows export artifacts.

Important APIs/types/functions: defines `SUBDIRS = api`, `lib_LTLIBRARIES = liblzma.la`, `liblzma_la_CPPFLAGS` include paths and `-DTUKLIB_SYMBOL_PREFIX=lzma_`, `liblzma_la_LDFLAGS = -no-undefined -version-info 13:3:8`, and conditionally adds linker version scripts. It includes `common/Makefile.inc`, `check/Makefile.inc`, and optional filter directories gated by `COND_FILTER_*`.

Control flow: Automake conditionals select source sets for threads, LZ, LZMA1/rangecoder, delta, simple filters, Windows resources, shared-library `.def` generation, and pkg-config generation. The `.rc.lo` suffix rule compiles Windows resources for shared libraries while replacing static objects with an empty C object.

State and persistence: build-time generated files include `liblzma.pc`, Windows `liblzma.def`, `liblzma.def.in`, and `empty.c`, all cleaned by `CLEANFILES` or `clean-local`. No runtime state.

Dependencies/integration: anchors all liblzma compilation, symbol version scripts, public API subdir, tuklib physmem/cpucores helpers, and `liblzma.pc`. It must stay in sync with source file additions and configure condition names.

Risks: missing a source fragment or conditional can silently remove codecs/checks from builds. Version-info and symbol-map changes affect ABI. The Windows `.def` generation depends on shared linking side effects and GNU-like tooling assumptions.

Test signals: `make distcheck`, shared/static builds, Windows builds, symbol-map validation via `validate_map.sh`, and pkg-config install tests are the main signals.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/api/Makefile.am -->
# sources/compression/xz/src/liblzma/api/Makefile.am

Purpose: declares the installed public liblzma headers and optional Doxygen API documentation targets.

Important APIs/types/functions: `nobase_include_HEADERS` installs `lzma.h` and all `lzma/*.h` subheaders while preserving the `lzma/` directory layout. Under `COND_DOXYGEN`, it defines `all-local`, `install-data-local`, `uninstall-local`, and `clean-local` for `doc/api`.

Control flow: normal builds install headers only. Doxygen-enabled builds run `doxygen/update-doxygen api` with source and build roots, then install generated HTML into `$(docdir)/api`.

State and persistence: generated API docs live under `$(top_builddir)/doc/api`; installed docs live under `$(DESTDIR)$(docdir)/api`; clean removes generated docs.

Dependencies/integration: establishes the public include surface consumed by applications as `<lzma.h>` plus internal subheaders included by that umbrella. Header list must stay aligned with `lzma.h` include order and symbol maps.

Risks: omitting a header breaks installation even if source builds. Installing subheaders is intentional, but each subheader guards against direct inclusion; downstream code must include `<lzma.h>`.

Test signals: install/dist checks, downstream compile tests against installed headers, and Doxygen generation when `COND_DOXYGEN` is enabled.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/api/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/api/lzma.h -->
# sources/compression/xz/src/liblzma/api/lzma.h

Purpose: umbrella public header for liblzma, defining portability macros and including all public API subheaders in the correct dependency order.

Important APIs/types/functions: sets up standard integer and size types unless `LZMA_MANUAL_HEADERS` is defined, including compatibility typedefs/macros for old MSVC. Defines `LZMA_API_IMPORT`, `LZMA_API_CALL`, `LZMA_API(type)`, `lzma_nothrow`, and GCC attribute wrappers. It then defines `LZMA_H_INTERNAL` and includes version, base, VLI, check, filter, BCJ, delta, LZMA1/2, container, stream flags, block, index, index hash, and hardware headers.

Control flow: compile-time only. C++ users get `extern "C"` around subheader declarations. After inclusion, `LZMA_H_INTERNAL` is undefined to prevent direct subheader re-inclusion by applications.

State and persistence: no runtime state; it defines ABI and source-compatibility surface.

Dependencies/integration: installed as the canonical include for all liblzma consumers. The subheader order matters because later headers depend on earlier types such as `lzma_ret`, `lzma_vli`, `lzma_check`, and `lzma_filter`.

Risks: header portability code is ABI-sensitive. Changes to calling convention, import/static handling, or integer macro fallback can break downstream builds, especially C++, old MSVC, MinGW, Cygwin, and projects that define manual headers.

Test signals: downstream-style compile tests, C++ compile coverage, Windows builds, and any test that includes only `<lzma.h>` without prior standard headers.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/api/lzma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/api/lzma/base.h -->
# sources/compression/xz/src/liblzma/api/lzma/base.h

Purpose: defines foundational liblzma API types, return codes, streaming actions, allocator hooks, `lzma_stream`, and core stream lifecycle functions.

Important APIs/types/functions: declares `lzma_bool`, `lzma_reserved_enum`, `lzma_ret`, `lzma_action`, `lzma_allocator`, opaque `lzma_internal`, `lzma_stream`, `LZMA_STREAM_INIT`, `lzma_code`, `lzma_end`, `lzma_get_progress`, `lzma_memusage`, `lzma_memlimit_get`, and `lzma_memlimit_set`.

Control flow: callers initialize `lzma_stream` with `LZMA_STREAM_INIT`, initialize a coder from another header, repeatedly call `lzma_code()` with an action (`LZMA_RUN`, flush/barrier, or `LZMA_FINISH` depending on coder), then call `lzma_end()`. Return codes distinguish success, stream end, check warnings, memory failures, format/options/data errors, buffer stalls, programming errors, and seek requests.

State and persistence: `lzma_stream` carries input/output pointers, totals, allocator pointer, opaque internal coder state, seek position, and reserved ABI space. Allocator lifetime rules differ between single-threaded and multithreaded use; multithreaded coders may retain allocator pointers until `lzma_end()`.

Dependencies/integration: all liblzma encoders/decoders and block/index/filter APIs use these types. The xz CLI stores a global `lzma_stream` and tracks progress through these fields/functions.

Risks: misuse of `lzma_code()` actions or mutating `avail_in` after finish/flush can produce `LZMA_PROG_ERROR`. `LZMA_BUF_ERROR` is intentionally delayed and nonfatal but often signals truncated input. ABI reserved fields must remain untouched by applications.

Test signals: nearly every liblzma test exercises this contract; focused signals include stream encode/decode tests, progress tests, memory-limit tests, and `xz` CLI compression/decompression flows.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/api/lzma/base.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/api/lzma/bcj.h -->
# sources/compression/xz/src/liblzma/api/lzma/bcj.h

Purpose: declares Branch/Call/Jump conversion filter IDs, shared BCJ options, and raw in-place helper functions for selected architectures.

Important APIs/types/functions: defines `LZMA_FILTER_X86`, `POWERPC`, `IA64`, `ARM`, `ARMTHUMB`, `SPARC`, `ARM64`, and `RISCV`; declares `lzma_options_bcj { uint32_t start_offset; }`; exports raw `lzma_bcj_arm64_encode/decode`, `lzma_bcj_riscv_encode/decode`, and `lzma_bcj_x86_encode/decode`.

Control flow: as normal filters, BCJ stages are configured through `lzma_filter` chains and implemented elsewhere. The raw helpers transform a caller-supplied buffer in place and return the processed byte count, leaving an architecture-specific tail unprocessed if needed.

State and persistence: no persistent state in the header. `start_offset` lets separately processed executable sections produce consistent relative-address conversions.

Dependencies/integration: included by `lzma.h` after `filter.h` and `vli.h`; the xz CLI maps command-line filter names to these IDs. `tests/test_filter_flags.c`, BCJ exact-size tests, and CLI argument parsing use these constants.

Risks: BCJ filters do not currently support `LZMA_SYNC_FLUSH`; using them in flush-sensitive streams returns options errors. Decoding requires matching non-default `start_offset`. Raw helpers are special-purpose and require alignment constraints for ARM64 and RISC-V offsets.

Test signals: `tests/test_filter_flags.c`, `tests/test_bcj_exact_size.c`, filter string tests, and command-line option parsing around `--x86`, `--arm64`, and similar filters.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/api/lzma/bcj.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/api/lzma/block.h -->
# sources/compression/xz/src/liblzma/api/lzma/block.h

Purpose: declares public APIs for encoding, decoding, sizing, and validating individual `.xz` Blocks and Block Headers.

Important APIs/types/functions: defines `lzma_block` with version, header size, check type, compressed/uncompressed sizes, filter chain, raw check bytes, reserved ABI fields, and `ignore_check`. Declares `lzma_block_header_size_decode`, `lzma_block_header_size`, `lzma_block_header_encode/decode`, `lzma_block_compressed_size`, `lzma_block_unpadded_size`, `lzma_block_total_size`, `lzma_block_encoder/decoder`, `lzma_block_buffer_bound`, `lzma_block_buffer_encode`, `lzma_block_uncomp_encode`, and `lzma_block_buffer_decode`.

Control flow: callers prepare an `lzma_block`, size or decode the header, run streamed block coder via `lzma_code()` or use single-call buffer APIs, then use computed sizes and `raw_check` for Index and integrity handling. Block Header and Block Data are intentionally separate for advanced container handling.

State and persistence: streamed coders update `compressed_size`, `uncompressed_size`, and `raw_check` during/after coding. Header decode allocates filter options into caller-provided filter arrays and does not free old options.

Dependencies/integration: relies on `lzma_filter`, `lzma_check`, and `lzma_vli`. Stream encoders/decoders, index generation, random access, and tests for block headers use these APIs.

Risks: `filters` arrays must have `LZMA_FILTERS_MAX + 1` entries or header decode can overflow the caller buffer. `check` must come from Stream Flags when decoding. `ignore_check` weakens integrity validation and requires `version >= 1`. Size fields use `LZMA_VLI_UNKNOWN` semantics and need careful validation.

Test signals: `tests/test_block_header.c`, block buffer encode/decode tests, random-access/index tests, and round-trip `.xz` stream tests.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/api/lzma/block.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/api/lzma/check.h -->
# sources/compression/xz/src/liblzma/api/lzma/check.h

Purpose: defines public integrity-check IDs and APIs for check support, check sizes, CRC calculation, and querying stream check type.

Important APIs/types/functions: declares enum `lzma_check` values `LZMA_CHECK_NONE`, `CRC32`, `CRC64`, and `SHA256`; defines `LZMA_CHECK_ID_MAX` and `LZMA_CHECK_SIZE_MAX`; exports `lzma_check_is_supported`, `lzma_check_size`, `lzma_crc32`, `lzma_crc64`, and `lzma_get_check`.

Control flow: applications query support before choosing checks for encoders; decoders can request warnings via container flags and then call `lzma_get_check()` immediately after `lzma_code()` returns `LZMA_NO_CHECK`, `LZMA_UNSUPPORTED_CHECK`, or `LZMA_GET_CHECK`. CRC functions are chunkable by passing the previous return value as the next seed.

State and persistence: public CRC functions are stateless from the caller perspective. Build configuration determines which check algorithms are supported, but check-size mapping is fixed for all IDs 0-15.

Dependencies/integration: `check.c` implements support/size dispatch; `crc32_fast.c` implements `lzma_crc32`; CRC64 and SHA-256 implementations are included through `check/Makefile.inc`. Stream headers, block checks, index hashing, and lzip decoding use these APIs.

Risks: calling `lzma_get_check()` outside the documented narrow return-code window is undefined. Unsupported future check IDs can be decoded but not verified. `LZMA_IGNORE_CHECK` can suppress payload integrity failures while header CRCs still run.

Test signals: `tests/test_check.c` validates CRCs and support; stream flags, block header, index hash, and lzip tests use CRC APIs for expected values.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/api/lzma/check.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/api/lzma/container.h -->
# sources/compression/xz/src/liblzma/api/lzma/container.h

Purpose: declares high-level container-format encoding and decoding APIs for `.xz`, legacy `.lzma`, `.lz`/lzip, MicroLZMA, presets, and multithreaded operation.

Important APIs/types/functions: defines preset macros `LZMA_PRESET_DEFAULT`, `LZMA_PRESET_LEVEL_MASK`, `LZMA_PRESET_EXTREME`; declares `lzma_mt` with threading, block size, timeout, preset/filter/check, and decoder memory-limit fields. Encoder APIs include easy memusage, easy encoder, easy buffer encoder, stream encoder, multithreaded stream encoder and memusage, `lzma_mt_block_size`, legacy alone encoder, stream buffer bound/encode, and MicroLZMA encoder. Decoder flags include `LZMA_TELL_NO_CHECK`, `LZMA_TELL_UNSUPPORTED_CHECK`, `LZMA_TELL_ANY_CHECK`, `LZMA_IGNORE_CHECK`, `LZMA_CONCATENATED`, and `LZMA_FAIL_FAST`; decoder APIs include stream, multithreaded stream, auto, alone, lzip, stream-buffer, and MicroLZMA decoders.

Control flow: high-level callers initialize `lzma_stream` through one of these functions, then use `lzma_code()` with the action set supported by that coder. Single-call APIs operate on `in/out` buffers and update position pointers only on success. Multithreaded encoders can split Blocks and accept barriers; threaded decoders parallelize only suitable multi-Block streams.

State and persistence: persistent state is held in `lzma_stream.internal`; `lzma_mt` is caller-owned configuration. Decoder memory limits may be adjusted via base APIs; buffer decoders can update a memlimit pointer on `LZMA_MEMLIMIT_ERROR`.

Dependencies/integration: central API used by xz CLI (`src/xz/coder.c`), tests, and downstream applications. Depends on base stream lifecycle, filters, checks, LZMA options, and hardware helpers for recommended memory choices.

Risks: decoder flags alter return-code semantics and integrity behavior. `LZMA_CONCATENATED` requires `LZMA_FINISH` to receive final stream end. Large `memlimit_threading` can permit huge buffering; `memlimit_stop` is the hard cap. MicroLZMA encoder has unusual single-call `lzma_code()` behavior and requires callers to check consumed/produced totals.

Test signals: CLI round trips, `tests/test_bcj_exact_size.c`, lzip and MicroLZMA tests, stream buffer tests, memory-limit tests, and threaded encoder/decoder builds.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/api/lzma/container.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/api/lzma/delta.h -->
# sources/compression/xz/src/liblzma/api/lzma/delta.h

Purpose: declares the Delta filter ID and option structure for byte-wise delta preprocessing.

Important APIs/types/functions: defines `LZMA_FILTER_DELTA`, enum `lzma_delta_type` with `LZMA_DELTA_TYPE_BYTE`, and `lzma_options_delta` containing `type`, `dist`, min/max distance macros, reserved integers, and reserved pointers.

Control flow: applications place a Delta filter in a `lzma_filter` chain, usually before LZMA2. Encoding stores byte differences at distance `dist`; decoding reverses that transformation. The header itself only provides configuration.

State and persistence: filter state is held in the coder implementation, not in the header. `lzma_options_delta` is caller-owned and ABI-reserved for future extensions.

Dependencies/integration: included by `lzma.h`; xz option parsing maps `--delta` to this filter; `filter.h` property/flag APIs encode/decode its options.

Risks: only byte-wise delta is supported; `type` must stay `LZMA_DELTA_TYPE_BYTE` and `dist` must be 1-256. Wrong distance can make decompression reversible but reduce compression effectiveness or fail options validation.

Test signals: `tests/test_filter_flags.c`, filter string tests, raw/stream filter-chain round trips, and xz CLI `--delta` option tests.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/api/lzma/delta.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/api/lzma/filter.h -->
# sources/compression/xz/src/liblzma/api/lzma/filter.h

Purpose: defines common filter-chain representation plus raw coding, filter property, filter flag, and string conversion APIs.

Important APIs/types/functions: defines `LZMA_FILTERS_MAX`, `lzma_filter { lzma_vli id; void *options; }`, support queries, `lzma_filters_copy/free`, raw encoder/decoder memusage and initialization, `lzma_filters_update`, raw buffer encode/decode, property size/encode/decode, filter flag size/encode/decode, and string APIs `lzma_str_to_filters`, `lzma_str_from_filters`, `lzma_str_list_filters` with `LZMA_STR_*` flags.

Control flow: filter chains are arrays terminated by `LZMA_VLI_UNKNOWN`. Callers validate/support-check filters, estimate memory, initialize streamed raw coders or use buffer APIs, and may update filters after supported flush/barrier points. String APIs parse user-facing presets/chains and allocate option structs.

State and persistence: filter options are caller-owned unless allocated by decode/string APIs, then freed with `lzma_filters_free()`. Streamed raw coders keep internal state in `lzma_stream`.

Dependencies/integration: core glue between BCJ, Delta, LZMA1/2, Block, Stream, and CLI options. xz uses this API heavily for command-line filters, memory estimates, and runtime filter updates.

Risks: arrays must have `LZMA_FILTERS_MAX + 1` slots for arbitrary chains. `lzma_filters_copy()` does not free old destination options. Property sizing may succeed even if full encoder initialization would fail. String parsing validates syntax but not every semantic condition unless later coder init checks it.

Test signals: `tests/test_filter_flags.c`, `tests/test_filter_str.c`, CLI option parsing, raw encode/decode round trips, and memory usage checks.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/api/lzma/filter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/api/lzma/hardware.h -->
# sources/compression/xz/src/liblzma/api/lzma/hardware.h

Purpose: declares public hardware-capability helpers used to choose memory and threading limits.

Important APIs/types/functions: exports `lzma_physmem(void)` for total RAM in bytes and `lzma_cputhreads(void)` for available CPU threads/cores.

Control flow: callers invoke these synchronous probes and treat zero as unavailable. The header notes that implementations may temporarily load libraries or open file descriptors and restart interrupted syscalls.

State and persistence: no public state; implementations are wrappers around tuklib helpers and platform APIs.

Dependencies/integration: `lzma_physmem()` wraps `tuklib_physmem()` from this subset; `lzma_cputhreads()` wraps `tuklib_cpucores()`. The xz CLI uses both in `src/xz/hardware.c` for default memory/thread decisions; container docs recommend `lzma_physmem()/4` as a decoder threading memory starting point.

Risks: hardware detection failure must not be fatal. Applications must still impose their own policy; these helpers expose capability, not a safe limit. File descriptor side effects can matter to programs with strict fd assumptions.

Test signals: `tests/test_hardware.c` exercises both functions and tolerates platform inability to report values.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/api/lzma/hardware.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/api/lzma/index.h -->
# sources/compression/xz/src/liblzma/api/lzma/index.h

Purpose: declares APIs for building, querying, iterating, concatenating, encoding, decoding, and using `.xz` Index information, including random-access file metadata.

Important APIs/types/functions: opaque `lzma_index`; `lzma_index_iter` with stream and block metadata; `lzma_index_iter_mode`; check mask macros; memory usage, init/end, append, stream flags/padding, checks, stream/block counts, size queries, iterator init/rewind/next/locate, `lzma_index_cat`, `lzma_index_dup`, streamed and buffer Index encoder/decoder, and `lzma_file_info_decoder`.

Control flow: encoders append Block records after coding Blocks, optionally set Stream Flags and padding, then encode the Index. Decoders parse Index into an `lzma_index`, query sizes and checks, and can locate target uncompressed offsets to seek to Blocks. `lzma_file_info_decoder` may return `LZMA_SEEK_NEEDED` through `lzma_code()` to inspect file tails and headers efficiently.

State and persistence: `lzma_index` owns heap structures sized by number of Streams/Blocks. Iterators borrow the index and remain valid across append, but source iterators become invalid when their index is consumed by `lzma_index_cat()`.

Dependencies/integration: relies on VLI, Stream Flags, Block sizes, allocator hooks, and check IDs. Random-access readers, list/test modes, and stream validators depend on this metadata.

Risks: Index memory can be much larger in RAM than on disk, so memlimits are critical. Size growth can return `LZMA_DATA_ERROR`. Thread safety permits concurrent readers only when no thread mutates the same index. File-info decoding requires correct seek handling by applications.

Test signals: `tests/test_index.c`, `tests/test_index_hash.c`, random-access/list tests, and `.xz` decode validation paths.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/api/lzma/index.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/api/lzma/index_hash.h -->
# sources/compression/xz/src/liblzma/api/lzma/index_hash.h

Purpose: declares constant-memory Index validation using a hash/check state instead of materializing a full `lzma_index`.

Important APIs/types/functions: opaque `lzma_index_hash`; exports `lzma_index_hash_init`, `lzma_index_hash_end`, `lzma_index_hash_append`, `lzma_index_hash_decode`, and `lzma_index_hash_size`.

Control flow: callers append expected Block records as Blocks are decoded, then feed the encoded Index bytes to `lzma_index_hash_decode()` until it returns `LZMA_STREAM_END` and confirms the Index matches the appended records.

State and persistence: `lzma_index_hash` stores accumulated record/check state and decoder progress. It can be reinitialized in place by passing a non-NULL pointer to `lzma_index_hash_init()`.

Dependencies/integration: implemented in common Index hash code using the best enabled check from internal `check.h` (`SHA256`, `CRC64`, or `CRC32`). Stream decoders use this to validate Index data without retaining all records.

Risks: once decoding has started, appending more records is a programming error. The hash validates consistency but does not provide random-access metadata like a full `lzma_index`.

Test signals: `tests/test_index_hash.c` checks append/decode/CRC behavior and mismatch detection.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/api/lzma/index_hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/api/lzma/lzma12.h -->
# sources/compression/xz/src/liblzma/api/lzma/lzma12.h

Purpose: declares LZMA1, extended LZMA1, and LZMA2 filter IDs, match-finder/mode enums, the shared LZMA options structure, and preset helper.

Important APIs/types/functions: defines `LZMA_FILTER_LZMA1`, `LZMA_FILTER_LZMA1EXT`, `LZMA_FILTER_LZMA2`; enums `lzma_match_finder` (`HC3`, `HC4`, `BT2`, `BT3`, `BT4`) and `lzma_mode` (`FAST`, `NORMAL`); support queries `lzma_mf_is_supported`, `lzma_mode_is_supported`; struct `lzma_options_lzma` with dictionary, preset dictionary, literal/position bits, mode, nice length, match finder, depth, extended LZMA1 flags/size, and reserved ABI fields; macro `lzma_set_ext_size`; function `lzma_lzma_preset`.

Control flow: callers either fill options manually or call `lzma_lzma_preset()` for preset levels/flags, then attach options to `lzma_filter` chains. Raw LZMA1EXT uses the extended size/end-marker fields to model formats such as 7z.

State and persistence: options are caller-owned configuration. Encoder/decoder runtime state lives in filter implementations after initialization.

Dependencies/integration: consumed by `container.h` high-level encoders, `filter.h` raw APIs, xz option parsing, and memory-usage estimators. LZMA2 is the normal `.xz` terminal compression filter.

Risks: many options have cross-field constraints (`lc + lp <= 4`, dictionary limits, match finder support, depth DoS risk). Preset success does not guarantee every feature is enabled in a reduced build. Preset dictionaries are not supported by normal container decoders.

Test signals: filter flag/string tests, CLI option parsing, preset/memory usage tests, MicroLZMA tests, and stream round trips with LZMA1/LZMA2.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/api/lzma/lzma12.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/api/lzma/stream_flags.h -->
# sources/compression/xz/src/liblzma/api/lzma/stream_flags.h

Purpose: declares `.xz` Stream Header/Footer flag structure and encode/decode/compare APIs.

Important APIs/types/functions: defines fixed `LZMA_STREAM_HEADER_SIZE` of 12 bytes; declares `lzma_stream_flags` with `version`, `backward_size`, `check`, and reserved ABI fields; defines backward size min/max; exports `lzma_stream_header_encode`, `lzma_stream_footer_encode`, `lzma_stream_header_decode`, `lzma_stream_footer_decode`, and `lzma_stream_flags_compare`.

Control flow: stream encoders encode a header from check flags and a footer from check plus backward Index size. Decoders parse header/footer, then compare flags while optionally ignoring unknown header backward size (`LZMA_VLI_UNKNOWN`).

State and persistence: no persistent state. Decoders populate caller-owned `lzma_stream_flags`.

Dependencies/integration: Stream encoders/decoders, Index validation, block decoders, and list/test modes use this to bind check type and backward Index size. CRC32 from `check.h` validates header/footer integrity.

Risks: nonzero version is currently unsupported for encoding and must be checked after decoding. Footer/header `LZMA_FORMAT_ERROR` means different things depending on stream position; callers should distinguish first-stream recognition from later corruption.

Test signals: `tests/test_stream_flags.c` verifies header/footer encoding, CRCs, invalid magic, backward-size validation, and comparisons.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/api/lzma/stream_flags.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/api/lzma/version.h -->
# sources/compression/xz/src/liblzma/api/lzma/version.h

Purpose: defines compile-time liblzma version macros and declares runtime version query functions.

Important APIs/types/functions: sets `LZMA_VERSION_MAJOR 5`, `MINOR 8`, `PATCH 3`, stable `LZMA_VERSION_STABILITY`, optional `LZMA_VERSION_COMMIT`, symbolic stability constants, numeric `LZMA_VERSION`, string construction macros, `LZMA_VERSION_STRING`, `lzma_version_number()`, and `lzma_version_string()`.

Control flow: compile-time macro arithmetic builds numeric and string versions. Runtime functions return the version of the linked liblzma, allowing applications to compare against compile-time headers.

State and persistence: no mutable state; version data is compile/link-time constant.

Dependencies/integration: included first by `lzma.h` so applications can gate feature usage. Windres can include parts of the header with `LZMA_H_INTERNAL_RC` to avoid function declarations.

Risks: headers and runtime library can differ; callers must use runtime functions when behavior depends on loaded library version. Commit suffix is string-only and not represented in the numeric macro.

Test signals: compile checks and any test/application displaying version. Packaging tests should verify version macros, pkg-config metadata, and runtime strings agree.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/api/lzma/version.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/api/lzma/vli.h -->
# sources/compression/xz/src/liblzma/api/lzma/vli.h

Purpose: declares `.xz` variable-length integer (VLI) limits, type, validation macro, and encode/decode/size APIs.

Important APIs/types/functions: defines `LZMA_VLI_MAX`, `LZMA_VLI_UNKNOWN`, `LZMA_VLI_BYTES_MAX`, `LZMA_VLI_C`, typedef `lzma_vli`, macro `lzma_vli_is_valid`, and functions `lzma_vli_encode`, `lzma_vli_decode`, `lzma_vli_size`.

Control flow: encode/decode support single-call mode when position pointer is NULL and multi-call mode when `vli_pos` tracks progress. Multi-call encode/decode returns `LZMA_OK` for incomplete progress and `LZMA_STREAM_END` when the integer is complete.

State and persistence: multi-call state is entirely caller-owned in `*vli_pos` and, for decode, partially accumulated in `*vli`. No heap or global state.

Dependencies/integration: VLI encodes filter IDs, property lengths, Block sizes, Index records, and Backward Size-related metadata. Most container, filter, block, and index APIs depend on its limits.

Risks: valid VLIs are limited to 63 bits; `UINT64_MAX` is reserved as unknown, not an encodable value. Non-minimal encodings are invalid. Single-call decode with truncated input returns `LZMA_DATA_ERROR`, while multi-call no-input returns `LZMA_BUF_ERROR`.

Test signals: VLI coverage appears through `tests/test_filter_flags.c`, Index tests, Block/Header tests, and any decoder tests with malformed size encodings.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/api/lzma/vli.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/check/Makefile.inc -->
# sources/compression/xz/src/liblzma/check/Makefile.inc

Purpose: Automake source fragment selecting integrity-check and checksum implementation files for liblzma.

Important APIs/types/functions: adds generator utilities to `EXTRA_DIST`; always adds `check/check.c`, `check/check.h`, `check/crc_common.h`, `check/crc_x86_clmul.h`, `check/crc32_arm64.h`, and `check/crc32_loongarch.h`. Selects `crc32_small.c` for `COND_SMALL`, otherwise `crc32_fast.c` and endian tables, plus optional x86 assembly. Conditionally adds CRC64 small/fast sources and optional SHA-256 implementation.

Control flow: build conditionals choose small-size versus fast table implementations and include optional algorithms based on configure results.

State and persistence: build-only. Generated CRC table helper programs are distributed but not runtime state.

Dependencies/integration: included from `src/liblzma/Makefile.am`; must match configure feature macros used by `check.c`, `check.h`, and CRC common headers.

Risks: mismatches between build conditionals and C preprocessor macros can expose API functions without implementation or include architecture headers on unsupported compilers. CRC32 is assumed always enabled.

Test signals: small/full builds, CRC64/SHA256 disabled builds, architecture-optimized builds, `tests/test_check.c`, and symbol-map validation.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/check/Makefile.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/check/check.c -->
# sources/compression/xz/src/liblzma/check/check.c

Purpose: implements public support/size queries for integrity checks and internal generic check init/update/finish dispatch.

Important APIs/types/functions: implements `lzma_check_is_supported`, `lzma_check_size`, `lzma_check_init`, `lzma_check_update`, and `lzma_check_finish`.

Control flow: public query functions range-check the check ID and index fixed arrays. Internal init/update/finish switch on `lzma_check`: none is a no-op; CRC32 initializes/updates/stores little-endian `uint32_t`; CRC64 does the same for `uint64_t`; SHA-256 delegates to SHA-256 helpers. Unsupported or reserved IDs fall through as no-ops for internal dispatch.

State and persistence: state is caller-provided `lzma_check_state`. No globals are mutated in this file.

Dependencies/integration: depends on feature macros `HAVE_CHECK_CRC32`, `HAVE_CHECK_CRC64`, `HAVE_CHECK_SHA256`, public `lzma/check.h`, internal `check.h`, CRC functions, endian conversion helpers, and SHA-256 wrappers. Block encoders/decoders and Index hash use these dispatchers.

Risks: support table must stay aligned with `.xz` Check ID assignments and build macros. Internal no-op behavior for unsupported IDs assumes callers validated check support before relying on results. Finish writes little-endian raw values, which display code must interpret correctly.

Test signals: `tests/test_check.c`; block encode/decode check validation; Index hash tests; stream decode tests with unsupported/no-check flags.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/check/check.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/check/check.h -->
# sources/compression/xz/src/liblzma/check/check.h

Purpose: internal integrity-check interface and SHA-256 provider abstraction for liblzma.

Important APIs/types/functions: includes `common.h`; determines `HAVE_INTERNAL_SHA256` when no usable external SHA-256 API is found; maps external providers from CommonCrypto, `<sha256.h>`, or `<sha2.h>` through `LZMA_SHA256FUNC`; defines `LZMA_CHECK_BEST`; declares `lzma_check_state` with final/check buffer and union state; declares `lzma_check_init/update/finish`; declares or inlines SHA-256 init/update/finish wrappers.

Control flow: compile-time provider selection determines whether SHA-256 calls are external inline wrappers or internal functions. Darwin CommonCrypto updates split input into `UINT32_MAX` chunks because its API takes 32-bit lengths.

State and persistence: `lzma_check_state` is stack/struct-owned by callers and can hold CRC or SHA-256 state. No global state here.

Dependencies/integration: used by Block coders, Index hashing, SHA-256 implementation, and `check.c`. `LZMA_CHECK_BEST` drives Index hash reliability based on enabled algorithms.

Risks: configure detection must define matching context and function macros. The union layout is internal and may change, so it must not leak into public ABI. External provider wrappers assume provider semantics match expected SHA-256 behavior.

Test signals: `tests/test_check.c`, `tests/test_index_hash.c`, block checksum tests, and builds across platforms with internal and external SHA-256 providers.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/check/check.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/check/crc32_arm64.h -->
# sources/compression/xz/src/liblzma/check/crc32_arm64.h

Purpose: ARM64 hardware-accelerated CRC32 implementation and runtime feature detection helper.

Important APIs/types/functions: includes ARM ACLE intrinsics except under MSVC; defines `crc_attr_target` for GCC/Clang `+crc`; implements static `crc32_arch_optimized(const uint8_t *buf, size_t size, uint32_t crc)` using `__crc32b/h/w/d`; when both generic and optimized variants are built, defines `is_arch_extension_supported()`.

Control flow: CRC calculation complements the incoming CRC, handles short inputs byte-wise, aligns to 8 bytes, processes 64-bit chunks, then handles 4/2/1-byte tails and complements the result. Runtime detection uses Linux `getauxval`, ELF aux info, Windows `IsProcessorFeaturePresent`, or Apple `sysctlbyname`, depending on available macros.

State and persistence: no persistent state; dispatch state lives in `crc32_fast.c` when both variants are compiled.

Dependencies/integration: included by `crc32_fast.c` under `CRC32_ARM64`; relies on aligned little-endian read helpers from common CRC code. Runtime detection availability is coordinated with `crc_common.h` and build-system checks.

Risks: hardware intrinsics must only execute on CPUs with CRC extension unless compiled for a target where it is guaranteed. Alignment math subtracts `align` from `size` after assuming `size >= 8`; this is safe only because the short-input path exits first. Missing runtime detection is a compile-time error when both variants are requested.

Test signals: `tests/test_check.c` validates CRC results; ARM64 optimized builds and runtime dispatch tests are needed to cover hardware paths.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/check/crc32_arm64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/check/crc32_fast.c -->
# sources/compression/xz/src/liblzma/check/crc32_fast.c

Purpose: fast CRC32 implementation with optional architecture-specific acceleration and runtime dispatch.

Important APIs/types/functions: includes `check.h` and `crc_common.h`; optionally includes x86 CLMUL, ARM64, or LoongArch optimized headers. Defines generic `lzma_crc32_generic()` unless provided by x86 assembly, dispatch type `crc32_func_type`, resolver `crc32_resolve()`, constructor/first-call dispatch state, and public `LZMA_API(uint32_t) lzma_crc32()`.

Control flow: generic path complements and endian-adjusts CRC, aligns input, processes slice-by-eight table chunks, processes remaining bytes, reverses endian adjustment on big-endian, and returns complemented CRC. When both generic and optimized implementations exist, a constructor or first call selects the optimized function if `is_arch_extension_supported()` succeeds.

State and persistence: dispatch builds keep static function pointer `crc32_func`, initialized by constructor or first call. The first-call path intentionally lacks locking because concurrent resolvers assign the same target.

Dependencies/integration: public `lzma_crc32()` is used by stream flags, block headers, Index, lzip, tests, and LZ hash initialization. Depends on generated endian CRC tables or x86 assembly and architecture headers selected by configure.

Risks: dispatch without locking is pragmatically safe but not strictly standards-clean. Table endian assumptions must match `WORDS_BIGENDIAN`. Optimized and generic implementations must produce identical results for chunked and unaligned inputs.

Test signals: `tests/test_check.c` validates known string, unaligned input, byte-at-a-time chunking, and random data; many container/header tests indirectly rely on CRC32 correctness.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/check/crc32_fast.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/check/crc32_loongarch.h -->
# sources/compression/xz/src/liblzma/check/crc32_loongarch.h

Purpose: LoongArch hardware-accelerated CRC32 implementation.

Important APIs/types/functions: includes `<larchintrin.h>` and defines static `crc32_arch_optimized(const uint8_t *buf, size_t size, uint32_t crc_unsigned)` using LoongArch CRC intrinsics `__crc_w_b_w`, `__crc_w_h_w`, `__crc_w_w_w`, and `__crc_w_d_w`.

Control flow: complements the incoming CRC into a signed 32-bit state, handles short inputs byte-wise, aligns the buffer to 8 bytes, processes 64-bit chunks, handles 4/2/1-byte tails, and returns the complemented state as `uint32_t`.

State and persistence: no state beyond local CRC and pointers. Unlike ARM64, this header has no runtime detection helper in this file; build selection must ensure the target supports the intrinsics.

Dependencies/integration: included by `crc32_fast.c` when `CRC32_LOONGARCH` is defined; relies on common aligned little-endian read helpers and build-system CPU feature checks.

Risks: compiling or running on unsupported LoongArch toolchains/CPUs will fail or fault. Casts to signed integer widths reflect intrinsic signatures and must preserve CRC bit patterns.

Test signals: `tests/test_check.c` provides correctness coverage when built on LoongArch; cross-builds verify header availability and intrinsic compatibility.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/check/crc32_loongarch.h -->
