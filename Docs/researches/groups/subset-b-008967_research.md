# subset-b-008967 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/software/checksum.c -->
# sources/storage-engines/wiredtiger/src/checksum/software/checksum.c

## Purpose
This file is the portable CRC32C implementation used whenever a hardware backend is unavailable or disabled. It implements the slicing-by-8 algorithm over static CRC tables, with separate table material for big-endian and little-endian builds so all platforms return the same external checksum value.

## Important APIs, Types, and Functions
`g_crc_slicing[8][256]` is the static lookup table used by the slicing algorithm. `__wt_checksum_with_seed_sw(uint32_t seed, const void *chunk, size_t len)` is the main software entry point and supports cumulative CRC calculation by starting from a caller-provided seed. `__wt_checksum_sw(const void *chunk, size_t len)` is the zero-seed wrapper used by architecture dispatchers.

## Control Flow
The seeded function initializes `crc` to `~seed`, consumes leading bytes until the pointer reaches a 4-byte boundary, processes the bulk of the buffer as pairs of 32-bit words inside an 8-byte loop, then handles trailing bytes. The big-endian branch uses byte-reversed tables and a final byte swap so the result matches little-endian output. The non-seeded wrapper delegates directly to the seeded implementation with seed zero.

## State and Persistence
The implementation has no mutable global state and persists nothing. Its only state is the static table and local CRC accumulator. Checksum stability is persistence-critical indirectly because block, log, and metadata readers compare stored checksum fields against values produced through the process-global checksum function pointer.

## Dependencies and Integration Points
The file depends on `wiredtiger_config.h` for endian feature macros and on fixed-width integer types. Architecture-specific wrappers declare these functions and use them as fallback targets. `src/support/global.c` installs the selected checksum functions into `__wt_process.checksum` and `__wt_process.checksum_with_seed`, which are used through `__wt_checksum` macros by block, log, disaggregated block, eviction, salvage, and diagnostic paths.

## Risks and Edge Cases
Correctness depends on exact table constants, endian-specific indexing, final complement behavior, and seed compatibility with hardware implementations. The bulk loop casts byte pointers to `uint32_t *`; the code aligns to 4 bytes first, but portability still relies on target tolerance for this aliasing style in the WiredTiger build. Boundary coverage is important for zero-length input, 1-7 byte tails, and all possible pointer alignments.

## Test Signals
Relevant tests include `test/csuite/wt2695_checksum`, which compares hardware and software checksums, seeded cumulative checksums, misaligned buffers, varied lengths, and all-0xff data, plus `test/csuite/wt4117_checksum` and runtime block/log recovery tests that validate stored checksum compatibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/software/checksum.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/x86/crc32-x86-alt.c -->
# sources/storage-engines/wiredtiger/src/checksum/x86/crc32-x86-alt.c

## Purpose
This file preserves compatibility with a historical Windows x86-64 hardware CRC implementation that could produce different values for buffers that were not 8-byte aligned or whose length was not a multiple of 8. It is not used to write new checksums; it is a secondary read-side match path for legacy data.

## Important APIs, Types, and Functions
`__checksum_alt(const void *chunk, size_t len)` is a private alternate CRC32C calculation using `_mm_crc32_u8` and `_mm_crc32_u64`. `__wt_checksum_alt_match(const void *chunk, size_t len, uint32_t v)` is the exported compatibility predicate declared in `extern.h` when built for `_M_AMD64` without `HAVE_NO_CRC32_HARDWARE`.

## Control Flow
The alternate function starts from `0xffffffff`, consumes bytes until a 4-byte boundary, processes 8-byte words with SSE4.2 CRC instructions, then consumes trailing bytes. The exported matcher runs CPUID leaf 1, checks the SSE4.2 ECX bit, and only computes the alternate checksum when the CPU supports the instruction set.

## State and Persistence
No state is stored. Persistence behavior is compatibility-oriented: old disk/log data may contain checksums from the historic calculation, and `__wt_checksum_match` can accept either the current checksum or this alternate value on affected Windows builds.

## Dependencies and Integration Points
The file depends on `wiredtiger_config.h`, MSVC intrinsic availability, and CPUID. It integrates with `misc_inline.h`, where `__wt_checksum_match` includes `__wt_checksum_alt_match` in the appropriate build configuration. It complements `crc32-x86.c`, which provides the current x86 checksum writer.

## Risks and Edge Cases
This path must never become the preferred write path or it could perpetuate legacy checksum divergence. Its availability is build- and platform-specific, so tests that only run on non-Windows platforms will not exercise it. The same alignment and tail-length cases that caused the compatibility concern should remain covered.

## Test Signals
Useful signals are checksum compatibility tests on Windows x86-64 with SSE4.2, block/log recovery fixtures containing legacy checksums, and generic checksum tests that verify normal checksum matching is not weakened on platforms where the alternate function is absent.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/x86/crc32-x86-alt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/x86/crc32-x86.c -->
# sources/storage-engines/wiredtiger/src/checksum/x86/crc32-x86.c

## Purpose
This file is the x86/x86-64 CRC32C dispatcher and hardware implementation. It selects SSE4.2 CRC instructions when available and falls back to the portable software implementation otherwise.

## Important APIs, Types, and Functions
`__checksum_with_seed_hw(uint32_t seed, const void *chunk, size_t len)` is the SSE4.2 seeded implementation, defined either with GNU inline byte encodings or MSVC intrinsics. `__checksum_hw` wraps it with seed zero. `wiredtiger_crc32c_func(void)` returns the process checksum function pointer, and `wiredtiger_crc32c_with_seed_func(void)` returns the seeded function pointer. Both cache the resolved pointer in a static local.

## Control Flow
The hardware routine initializes `crc` to `~seed`, consumes bytes until alignment, processes 8-byte words with CRC32Q or `_mm_crc32_u64`, then consumes trailing bytes and returns `~crc`. The resolver checks its static cache first. If hardware CRC is enabled, it runs CPUID leaf 1 and chooses the hardware function when the SSE4.2 bit is set; otherwise it chooses `__wt_checksum_sw` or `__wt_checksum_with_seed_sw`.

## State and Persistence
The only mutable state is the static cached function pointer in each resolver. It is intentionally process-local and avoids repeated CPUID overhead. The selected implementation affects every checksum written during the process, so it must remain bit-identical to the software implementation for persistent block and log compatibility.

## Dependencies and Integration Points
The file depends on `wiredtiger_config.h`, GNU inline assembly or MSVC intrinsics, and software fallback declarations from `checksum.c`. `src/support/global.c` calls these exported resolvers during process setup. The resulting pointers back `__wt_checksum` and `__wt_checksum_with_seed` macros used throughout storage and logging code. `examples/c/ex_all.c` and checksum csuite tests also call the exported resolver APIs.

## Risks and Edge Cases
The inline instruction encodings and register constraints are low-level and compiler-sensitive. Resolver statics are benignly racy if called concurrently during startup, but all racing writes assign equivalent function pointers. Seeded and unseeded results must match the software path for all buffer alignments and lengths. Builds with `HAVE_NO_CRC32_HARDWARE` must reliably bypass the hardware instructions.

## Test Signals
`test/csuite/wt2695_checksum` is the primary signal because it compares hardware and software output for normal, cumulative, misaligned, and varied-size buffers. `test/csuite/wt4117_checksum`, block/log recovery tests, and startup tests on x86 hosts with and without SSE4.2 are also relevant.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/x86/crc32-x86.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/zseries/crc32-s390x.c -->
# sources/storage-engines/wiredtiger/src/checksum/zseries/crc32-s390x.c

## Purpose
This file is the Linux s390x checksum dispatcher and C glue for the z/Architecture Vector Extension Facility CRC32C implementation. It uses vector hardware for sufficiently large aligned buffers when available and otherwise falls back to software CRC32C logic.

## Important APIs, Types, and Functions
`__wt_crc32c_le(unsigned int crc, const unsigned char *buf, size_t len)` is the byte-at-a-time little-endian CRC32C fallback using `crc32ctable_le`. `DEFINE_CRC32_VX` generates `__wt_crc32c_le_vx`, which aligns input, applies a minimum vector length threshold, calls the assembly routine `__wt_crc32c_le_vgfm_16`, and handles the tail. `wiredtiger_crc32c_func(void)` chooses hardware or software for unseeded checksums. `wiredtiger_crc32c_with_seed_func(void)` returns `__crc32c_le_wrapper`.

## Control Flow
The vector wrapper first consumes bytes until 16-byte alignment, then falls back to software if fewer than 64 bytes remain. Otherwise it rounds the length down to a 16-byte multiple, calls the vector assembly routine, and processes remaining bytes in software. The unseeded checksum wrapper calls the vector path with initial `0xffffffff` and complements the result. The resolver reads `AT_HWCAP` with `getauxval`, checks `HWCAP_S390_VX`, and caches the chosen function pointer.

## State and Persistence
The file keeps only a static cached resolver result. It persists no data directly, but its return value validates and writes persistent block/log checksums. Seeded checksums intentionally use a software wrapper because the file notes that hardware CRC over multiple chunks is not supported on this big-endian platform.

## Dependencies and Integration Points
It depends on Linux `getauxval`, `HWCAP_S390_VX`, endian conversion helpers, `crc32-s390x.h`, `slicing-consts.h`, and `wt_internal.h`. It integrates with `crc32le-vx.S` for the vector core and the same `wiredtiger_crc32c_func` interface used by global process initialization.

## Risks and Edge Cases
The hardware path is gated by both compile-time hardware support and runtime kernel capability. Alignment and minimum-length transitions must be bit-identical to the software fallback. The seeded API behavior differs from x86 because it avoids hardware and wraps the little-endian C routine, so cumulative checksum tests on s390x are important.

## Test Signals
Signals include `wt2695_checksum` on s390x with VX-capable and non-VX hosts, tests over buffer lengths around 0, 15, 16, 63, 64, and 65 bytes, and block/log checksum recovery tests on big-endian systems.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/zseries/crc32-s390x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/zseries/crc32-s390x.h -->
# sources/storage-engines/wiredtiger/src/checksum/zseries/crc32-s390x.h

## Purpose
This header declares the s390x CRC32C software and vector entry points shared between the C dispatcher and the assembly-backed implementation.

## Important APIs, Types, and Functions
It declares `__wt_crc32c_le(unsigned int, const unsigned char *, size_t)` for the portable little-endian CRC32C routine and `__wt_crc32c_le_vx(unsigned int, const unsigned char *, size_t)` for the vector-accelerated wrapper.

## Control Flow
The header has no executable control flow. It lets `crc32-s390x.c` call either the software byte-at-a-time routine or the generated vector wrapper through normal C prototypes.

## State and Persistence
No state is declared. Persistence impact is indirect through the checksum functions it exposes for block/log checksum calculation.

## Dependencies and Integration Points
It includes `sys/types.h` for `size_t` and is consumed by `crc32-s390x.c`. The vector declaration corresponds to a function generated by `DEFINE_CRC32_VX` in the C file, which itself calls the assembly symbol from `crc32le-vx.S`.

## Risks and Edge Cases
Prototype drift would cause ABI or compiler warnings across C and assembly boundaries. The comments mention IEEE and Castagnoli variants, but only CRC32C little-endian functions are declared here, so future extensions should keep comments and exports consistent.

## Test Signals
Build tests on s390x are the main signal, especially with strict warnings. Runtime checksum tests cover whether declarations, definitions, and calling conventions match.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/zseries/crc32-s390x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/zseries/crc32le-vx.S -->
# sources/storage-engines/wiredtiger/src/checksum/zseries/crc32le-vx.S

## Purpose
This assembly file implements the s390x Vector Extension Facility CRC32C folding kernel for little-endian, bit-reflected CRC32C. It is the performance-critical backend called by the C vector wrapper for large aligned buffers.

## Important APIs, Types, and Functions
The exported entry is `__wt_crc32c_le_vgfm_16`, created with `WT_CRC32_ENTRY`. The file defines constant blocks for IEEE CRC32 and CRC32C, but the exported WiredTiger path loads `.Lconstants_CRC_32C_LE`. Vector registers `%v9` through `%v14` hold permutation, reduction, Barrett reduction, and polynomial constants.

## Control Flow
The function preserves non-volatile registers, loads constants, places the initial CRC into a vector register, loads the first 64 bytes, permutes data from big-endian memory order into the reflected little-endian domain, and folds repeated 64-byte chunks with `VGFMAG`. It then folds four vectors to one, processes remaining 16-byte chunks, performs a final 128-bit to 32-bit fold, applies Barrett reduction, moves the final 32-bit CRC to `%r2`, restores registers, and returns.

## State and Persistence
The routine has no persistent state. It operates entirely in registers plus read-only constants. Its persistent relevance is that it must produce exactly the same checksum as the software path for on-disk and log compatibility.

## Dependencies and Integration Points
It includes `wiredtiger_config.h` and is compiled only when hardware CRC is not disabled. It uses `vx-insn.h` assembler macros to emit vector opcodes for toolchains that may not know newer mnemonics. `crc32-s390x.c` declares and calls the exported symbol through `__wt_crc32c_le_vgfm_16`.

## Risks and Edge Cases
This code is sensitive to s390x ABI register preservation, stack layout, vector instruction encoding, constants, and length preconditions. The C wrapper promises size at least 64 and 16-byte alignment for vector calls; violating that contract could lead to incorrect loads. The `.note.GNU-stack` section must remain outside conditional compilation as documented.

## Test Signals
Strong signals are s390x builds with older and newer binutils, checksum comparisons against `__wt_checksum_sw`, sanitizer or ABI checks around register preservation where available, and data-length tests around the C wrapper threshold and 16-byte remainder paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/zseries/crc32le-vx.S -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/zseries/slicing-consts.h -->
# sources/storage-engines/wiredtiger/src/checksum/zseries/slicing-consts.h

## Purpose
This header supplies precomputed slicing-by-8 CRC tables for big-endian s390x checksum support. Only the CRC32C little-endian table is active; several IEEE and big-endian tables are retained under `#if 0` as unused reference material.

## Important APIs, Types, and Functions
The active symbol is `crc32ctable_le[8][256]`, declared `static const unsigned int` and aligned to 128 bytes. It is used by `__wt_crc32c_le` in `crc32-s390x.c` for byte-at-a-time fallback, prealignment, tail handling, and seeded wrapper behavior.

## Control Flow
The file has no executable control flow. Compile-time `#if 0` blocks exclude unused `crc32table_le`, `crc32table_be`, and `crc32ctable_be` tables. The active table is indexed by byte values during CRC accumulation in the C code.

## State and Persistence
The table is immutable static data. It persists only in the binary image. Any constant error would corrupt persistent checksum compatibility across block and log files, so the values are effectively part of WiredTiger's storage contract on s390x.

## Dependencies and Integration Points
It is included by `crc32-s390x.c`. The table values mirror the Castagnoli polynomial behavior used in the generic software checksum table, but are arranged for the s390x little-endian CRC helper.

## Risks and Edge Cases
The header is large and mostly numeric, so accidental edits are hard to review by inspection. Because unused tables are present under `#if 0`, changes to active versus inactive sections can be misleading. Alignment attributes should remain compatible with compilers used for s390x builds.

## Test Signals
Checksum comparison tests against the portable implementation are the best signal. Build warnings around unused static data should stay absent because inactive tables are preprocessor-disabled and the active table is consumed in the same translation unit.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/zseries/slicing-consts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/zseries/vx-insn.h -->
# sources/storage-engines/wiredtiger/src/checksum/zseries/vx-insn.h

## Purpose
This assembler header provides macros for emitting s390x vector instructions manually. It exists so the CRC assembly can build with binutils versions that do not understand all vector mnemonics natively.

## Important APIs, Types, and Functions
`WT_CRC32_ENTRY(name)` emits a global aligned function label. `GR_NUM`, `VX_NUM`, `RXB`, `MRXB`, and `MRXBOPC` derive register numbers and opcode extension bits. Instruction macros include `VZERO`, `VLVGF`, `VL`, `VLM`, `VSTM`, `VPERM`, `VUPLLF`, `VX`, `VGFMG`, `VGFMAG`, `VSRLB`, and related element load/store helpers.

## Control Flow
The header is macro-only. Each macro validates textual register names where applicable, emits `.word` and `.byte` opcode fragments, and computes RXB fields for high vector registers. `crc32le-vx.S` expands these macros to build the folding and Barrett reduction kernel.

## State and Persistence
No runtime state exists. The generated instruction bytes become part of the executable text. Correct macro expansion is necessary for persistent checksum correctness because it determines the actual hardware operations used by the vector backend.

## Dependencies and Integration Points
The file is included by `crc32le-vx.S` and is guarded by `__ASM_S390_VX_INSN_H`. It depends on GNU assembler macro syntax. It is not a general C header despite the `.h` suffix.

## Risks and Edge Cases
Register-name parsing is explicit and easy to break when new register forms are introduced. Encoding bugs can compile successfully but execute the wrong instruction. This file is also toolchain-sensitive because it relies on assembler expression behavior and macro defaults.

## Test Signals
The key signals are successful s390x assembly builds across supported binutils versions and runtime CRC comparisons on VX-capable machines. Disassembly review is useful after macro changes because source-level tests may not isolate encoding regressions quickly.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/zseries/vx-insn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conf/conf_bind.c -->
# sources/storage-engines/wiredtiger/src/conf/conf_bind.c

## Purpose
This file binds runtime varargs values to placeholders in a previously compiled WiredTiger configuration string. It supports the public `WT_SESSION::bind_configuration` path.

## Important APIs, Types, and Functions
`__wt_conf_bind(WT_SESSION_IMPL *session, const char *compiled_str, va_list ap)` is the only function. It uses `WT_CONF`, `WT_CONF_BINDINGS`, `WT_CONF_BIND_DESC`, and `WT_CONFIG_ITEM`. Binding descriptors come from `conf_compile.c` when `%d` or `%s` placeholders are compiled.

## Control Flow
The function resolves `compiled_str` to a compiled `WT_CONF` with `__wt_conf_get_compiled`; failure returns `EINVAL`. It clears `session->conf_bindings`, iterates over `conf->binding_descriptions`, copies each descriptor into the session binding slot, reads the next vararg according to descriptor type, and fills the corresponding `WT_CONFIG_ITEM`. Numeric and boolean placeholders read `int64_t`. String and ID placeholders read `const char *`, set string length, coerce literal `true` and `false` to boolean constants, and otherwise validate choices with `__wt_conf_check_choice`.

## State and Persistence
The function mutates only `session->conf_bindings`, making bindings session-local and temporary. It does not alter the compiled configuration object. Bound values later satisfy `CONF_VALUE_BIND_DESC` lookups in `conf_get.c`; missing or stale bindings cause a runtime error.

## Dependencies and Integration Points
It depends on compiled configuration metadata from `conf_compile.c`, choice constants from generated config code, and `__wt_conf_get_compiled`. It is called from `session_api.c` in the implementation of `bind_configuration`.

## Risks and Edge Cases
Varargs type agreement is critical and cannot be checked by the compiler. `WT_CONF_BIND_VALUES_LEN` is small, so compiler-side binding counts must remain within session storage limits. Strings are not copied; callers must keep them valid for the use window. Boolean string coercion is required for compatibility with non-compiled config parsing and fast choice comparisons.

## Test Signals
`test/csuite/config` and `test/csuite/wt11126_compile_config` exercise compile/bind flows. Useful cases include `%d`, `%s`, boolean strings, invalid choices, unbound compiled configs, and repeated binds on the same session.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conf/conf_bind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conf/conf_compile.c -->
# sources/storage-engines/wiredtiger/src/conf/conf_compile.c

## Purpose
This file compiles textual API configuration strings into compact `WT_CONF` structures that can be reused or copied into API call buffers. It is a performance-oriented alternative to repeatedly parsing strings in hot paths.

## Important APIs, Types, and Functions
`__wt_conf_compile` compiles a user-visible configuration string and returns an opaque pointer into `conn->conf_dummy`. `__wt_conf_compile_api_call` builds or reuses a compiled config for one API invocation. `__wt_conf_compile_init` precompiles default configurations for all compilable APIs at connection startup. `__wt_conf_compile_discard` frees compiled state. Internal helpers include `__conf_compile`, `__conf_compile_value`, `__conf_compile_config_strings`, `__conf_verbose`, and `__conf_compile_free`.

## Control Flow
Compilation parses key/value pairs with `__wt_config_next`, uses generated jump tables and `bsearch` to find `WT_CONFIG_CHECK` metadata, maps key ids to one-based entries in `WT_CONF.value_map`, and stores values as defaults, nondefaults, binding descriptors, or sub-configuration references. Category/list values may recurse into subconfig check arrays after stripping matching brackets. Initialization allocates `conf_dummy`, `conf_array`, and `conf_api_array`, then compiles base configs for each compilable API. API calls either return a precompiled config, copy the default compiled superstructure and overlay caller config, or return the default when no config is supplied.

## State and Persistence
Connection-level mutable state includes `conn->conf_dummy`, `conn->conf_array`, `conn->conf_size`, `conn->conf_max`, and `conn->conf_api_array`. `WT_CONF` itself is designed as a position-independent superstructure containing an array of `WT_CONF` nodes followed by `WT_CONF_VALUE` entries. Source strings for explicitly compiled configs are owned and freed with the compiled object. This is in-memory state only, but it controls how persistent object creation and runtime API options are interpreted.

## Dependencies and Integration Points
The file depends on generated config metadata in `config.h`, `conf.h`, `conf_keys.h`, validation helpers such as `__wt_conf_check_one`, and the generic parser in `config.c`. Public integration comes through `WT_CONNECTION::compile_configuration`, `WT_SESSION::bind_configuration`, and API wrapper macros in `api.h`. Verbose reconstruction uses `__wt_conf_gets_func` to cross-check compiled lookups against normal config parsing.

## Risks and Edge Cases
The layout arithmetic is dense: sub-config indexes, value-table offsets, default bitmaps, and one-byte value-map positions must stay consistent with generated sizing. Binding placeholders are allowed only in explicit compilation and must not appear twice for the same key. The returned compiled string is an address into `conf_dummy`; copying it as a normal string loses identity. `conf_size` uses atomic fetch-add, so overflow handling must avoid leaking compiled entries.

## Test Signals
`test/csuite/wt11126_compile_config` is the most direct signal, with additional coverage from `test/csuite/config` and API tests that use compiled configurations. Debug verbosity can reconstruct configs and assert boolean/string invariants. Fuzz-like config parser tests are useful for nested categories, duplicate keys, bindings, and invalid types.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conf/conf_compile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conf/conf_get.c -->
# sources/storage-engines/wiredtiger/src/conf/conf_get.c

## Purpose
This file retrieves values from compiled `WT_CONF` structures using generated packed key ids. It is the compiled-configuration equivalent of textual `__wt_config_gets` lookups.

## Important APIs, Types, and Functions
`__wt_conf_gets_func(WT_SESSION_IMPL *session, const WT_CONF *orig_conf, uint64_t orig_keys, int override_default, bool use_override_default, bool no_precompiled_def, WT_CONFIG_ITEM *value)` is the sole function. Callers usually reach it through macros such as `__wt_conf_gets`, `__wt_conf_getones`, and `__wt_conf_gets_def`.

## Control Flow
The function walks 16-bit key-id components packed into `orig_keys`. At each level, it reads the one-based `value_map` entry, fetches the corresponding `WT_CONF_VALUE`, shifts to the next key component, and switches on value type. Default items may be suppressed or overridden with a synthetic boolean. Nondefault items return directly when no nested keys remain. Binding descriptors fetch the session-bound value at the descriptor offset and verify the descriptor pointer matches. Subconfig entries move `conf` to the referenced nested `WT_CONF` and continue.

## State and Persistence
The function does not mutate compiled config state. It reads `session->conf_bindings` for bound placeholders and may fail if values have not been bound. Persistent behavior is indirect: all API decisions backed by compiled configs depend on this lookup returning the same value as the traditional parser.

## Dependencies and Integration Points
It depends on `WT_CONF`, `WT_CONF_VALUE`, `WT_CONF_BIND_DESC`, `WT_CONF_BIND_VALUES_LEN`, default bitmap macros, and generated key ids. It is called heavily through inline/macros in `conf.h` and `conf_inline.h`, including from verbose reconstruction in `conf_compile.c` and API paths that accept compiled configs.

## Risks and Edge Cases
Packed key ids must be nonzero and within `WT_CONF_ID_COUNT`; incorrect generated ids can lead to not-found results or assertions. Binding descriptor pointer comparison intentionally catches stale or missing `bind_configuration` calls. Default override and `no_precompiled_def` behavior must match legacy `__wt_config_getones` and default-handling semantics.

## Test Signals
Compile-config csuite tests should compare compiled lookups against textual lookups for top-level and nested keys, defaults, overrides, `getones` semantics, bound placeholders, and missing bindings. Runtime API tests using compiled configs provide integration coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conf/conf_get.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/config/config.c -->
# sources/storage-engines/wiredtiger/src/config/config.c

## Purpose
This file is the generic WiredTiger configuration string scanner and lookup engine. It parses key/value strings, nested structures, quoted strings, booleans, integers with size suffixes, and priority-ordered arrays of configuration strings.

## Important APIs, Types, and Functions
`__wti_config_parse_dec` is a bounded `strtoll`-style decimal parser. `__wt_config_initn`, `__wt_config_init`, and `__wt_config_subinit` initialize `WT_CONFIG` parsers. `__wt_config_next` returns processed key/value pairs. Lookup APIs include `__wti_config_get`, `__wt_config_gets`, `__wt_config_getone`, `__wt_config_getones`, `__wt_config_getones_n`, `__wt_config_gets_def`, `__wt_config_subgetraw`, `__wt_config_subgets`, and `__wt_config_subget_next`. Internal helpers include `__config_next`, `__config_getraw`, and `__config_process_value`.

## Control Flow
The scanner uses table-driven actions (`gostruct`, `gobare`, `gostring`, `goutf8_continue`, and `goesc`) instead of ad hoc token parsing. `__config_next` tracks bracket depth, top-level item boundaries, quote state, escapes, UTF-8 continuation bytes, separators, and implicit `true` values for keys without explicit values. `__config_process_value` converts `true` and `false` IDs to booleans, parses decimal integers, and applies `b/k/m/g/t/p` suffix shifts when safe. `__config_getraw` scans a parser for the last matching key, recurses through dotted nested keys, and processes the final value at the top level. `__wti_config_get` searches config string arrays in reverse so later user configs override defaults.

## State and Persistence
Parser state is held in `WT_CONFIG`: original string, current pointer, end pointer, depth, top marker, and active transition table. The module does not persist data, but it is the canonical interpreter for configuration strings stored in metadata and supplied to public APIs. Its parsing choices therefore influence object creation, recovery, checkpoints, cursors, transactions, and connection settings.

## Dependencies and Integration Points
It depends on WiredTiger character classification helpers, error macros, `WT_CONFIG_ITEM`, and `WT_CONFIG` definitions from `config.h`. It feeds validation in `config_check.c`, compiled configuration in `conf_compile.c`, public config parser APIs in `config_api.c`, schema parsing, metadata checkpoint parsing, cursor options, connection reconfiguration, transaction options, and many performance-sensitive defaults via `__wt_config_gets_def`.

## Risks and Edge Cases
The finite-state tables are compact but hard to audit; a single table entry can change accepted syntax. Numeric parsing must handle overflow, negative values, suffix shifts, and partial parses correctly. Quoted strings accept only valid UTF-8 sequences and limited escapes. Nested dotted lookup returns the final matching value, so duplicate keys and override order are intentional. `__wt_config_gets_def` makes assumptions about common two-string config arrays for performance.

## Test Signals
Parser unit and csuite config tests are essential, including malformed brackets, unbalanced quotes, escapes, UTF-8, duplicate keys, nested structures, boolean shorthand, numeric suffixes, overflow, `none` handling, and reverse override order. Broader schema, cursor, checkpoint, metadata, and transaction tests provide integration coverage because they all consume this parser.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/config/config.c -->
