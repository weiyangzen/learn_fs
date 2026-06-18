# subset-b-007617 research

Grouped research for crcutil files under `sources/distributed-fs/lizardfs/external/crcutil-1.0`. Each section is bounded for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/Makefile.in -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/Makefile.in

## Purpose

`Makefile.in` is an Automake 1.11.1 generated build template for crcutil. It becomes the concrete `Makefile` after `configure` substitutes compiler, linker, installation, dependency, and package variables. In this vendored LizardFS copy it defines how crcutil builds its unit-test binary `crcutil_ut`, the example/usage binary `usage`, generated headers such as `config.h`, distribution archives, tags, install/uninstall targets, and the Automake test runner.

## Important APIs, types, and targets

The public build surface is made of make targets rather than C++ APIs. `all` depends on `config.h` and `all-am`; `check` builds `crcutil_ut` and runs `check-TESTS`; `usage` is listed in `tmp_PROGRAMS` and installed under `tmpdir=/tmp`; `dist`, `distcheck`, `clean`, `distclean`, `maintainer-clean`, `install`, and `uninstall` are standard Automake targets. `crcutil_ut_SOURCES` and `usage_SOURCES` enumerate the crcutil source headers and architecture-specific implementation files covered by this work item, plus tests or examples.

Important substituted variables include `CC`, `CXX`, `CXXFLAGS`, `CFLAGS`, `CPPFLAGS`, `LDFLAGS`, `OBJEXT`, `EXEEXT`, `srcdir`, `top_srcdir`, `DEPDIR`, and install paths. The crcutil-specific defaults are `AM_CXXFLAGS = -DCRCUTIL_USE_MM_CRC32=1 -Wall -msse2 -Icode` and `AM_CFLAGS = $(AM_CXXFLAGS)`.

## Control flow, state, and persistence

The Makefile controls generated build state: `config.status`, `config.h`, `stamp-h1`, dependency files under `.deps`, object files, binaries, distribution directories, and archives. Rules for `Makefile`, `configure`, `aclocal.m4`, and `config.h.in` rerun Autotools when inputs change. Compile rules emit `.Po` dependency files through `depcomp` when Automake dependency tracking is enabled. `check-TESTS` runs each test executable, classifies PASS/FAIL/SKIP/XFAIL, and returns a failing status on unexpected failure.

## Dependencies and integration points

This file integrates crcutil with Autoconf/Automake, GNU make, shell tools, `awk`, `sed`, `find`, `tar`, compressors, `ctags`/`etags`, and the configured C/C++ toolchain. It wires the core C++ code to tests under `tests/` and examples under `examples/`. The `-msse2` and `CRCUTIL_USE_MM_CRC32` flags affect source-level conditional compilation in `platform.h`, `crc32c_sse4_intrin.h`, and the architecture-specific `.cc` files.

## Risks and test signals

The template is generated, so manual edits can be lost if `automake` reruns from `Makefile.am`. The default `-msse2` and optional `-mcrc32` expectations are x86-centric and can break non-x86 or older toolchains if not configured carefully. Installing `usage` into `/tmp` is unusual and should be treated as a demo artifact rather than a library install contract. The strongest validation signal is `make check`, which builds and runs `crcutil_ut`; `distcheck` adds a heavier signal by verifying VPATH build, install, uninstall, and distribution completeness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/autogen.sh -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/autogen.sh

## Purpose

`autogen.sh` regenerates the crcutil Autotools build system and optionally configures or builds it. It removes stale generated files, synthesizes `configure.ac` from `autoscan`, writes `Makefile.am`, runs `aclocal`, `autoconf`, `autoheader`, and `automake --add-missing`, then invokes `./configure` with optimized compiler flags before optionally running `make`.

## Important APIs, commands, and modes

The script has a small argument protocol. `autogen.sh clean` removes build and generated Autotools outputs and exits. `autogen.sh clean clean` removes an even fuller generated set because the condition treats argument 2 equal to `clean` as full cleanup. `autogen.sh configure` performs regeneration and configure but exits before `make`. Other first arguments are passed to `make $1`, and the second argument is appended to generated `CFLAGS`/`CXXFLAGS`.

It writes `configure.ac` with `AC_INIT(crcutil, 1.0, crcutil@googlegroups.com)`, `AM_INIT_AUTOMAKE`, `AC_CONFIG_FILES([Makefile])`, and `AC_OUTPUT()`. It writes `Makefile.am` entries for `AM_CXXFLAGS`, optional static `AM_LDFLAGS`, unit test and usage targets, and source lists discovered from `tests/`, `code/`, and `examples/`, excluding files matching `intrinsic`.

## Control flow, state, and persistence

The script is destructive to local generated state: it removes `Makefile`, `Makefile.am`, `Makefile.in`, `aclocal.m4`, `config.h.in`, `configure`, `.deps`, `autom4te.cache`, `config.status`, `config.log`, and related files depending on mode. It then persists regenerated `configure.ac`, `Makefile.am`, `Makefile.in`, and `config.h.in`. Configure output persists `config.h`, `Makefile`, and cache/status files.

## Dependencies and integration points

It depends on Bash, GNU-ish test syntax, `make`, `autoscan`, `sed`, `aclocal`, `autoconf`, `autoheader`, `automake`, `c++ -dumpversion`, `uname`, `ls`, `grep`, and `tr`. It integrates with the code directory by discovering `code/*.cc` and `code/*.h`, and it controls compilation flags consumed by `platform.h` and the CRC intrinsic headers.

## Risks and test signals

The string comparison `[[ "$(c++ -dumpversion)" > "4.4.9" ]]` is lexical, not a robust semantic version check. The script removes generated files without prompting, so it should not be run in a tree with uncommitted generated changes unless that is intended. Static linking is enabled on non-Darwin systems for newer GCC versions, which can fail on environments lacking static libraries. Validation signals are successful Autotools regeneration, successful `./configure`, and a successful `make` or `make check` after script completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/autogen.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/code/base_types.h -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/code/base_types.h

## Purpose

`base_types.h` defines crcutil's fixed-width integer aliases and a compile-time helper used to align those aliases with `size_t` and `ptrdiff_t` when their sizes match. This lets template specializations written for `size_t` also serve `uint32` or `uint64` configurations on the matching platform width.

## Important APIs and types

`ChooseFirstIfSame<A, B>::Type` selects `A` when `sizeof(A) == sizeof(B)`, otherwise `B`. It contains a nested `ChooseFirstIfTrue` template with a boolean specialization. The file defines `uint8`, `int8`, `uint16`, `int16`, `uint32`, `int32`, `uint64`, and `int64` in namespace `crcutil`. On MSVC, 64-bit types use `unsigned __int64` and `__int64`; on GCC they use `unsigned long long` and `long long`. `HAVE_UINT64` is defined to 1 for MSVC and GCC and 0 for unknown compilers, where `uint64` falls back to `uint32`.

## Control flow, state, and persistence

There is no runtime state. The only state is compile-time type selection and macro definition. Downstream templates depend on the selected aliases to determine table entry size, word size, CRC width, and specialization availability.

## Dependencies and integration points

The file includes `std_headers.h` for `size_t` and `ptrdiff_t`. It feeds nearly every other crcutil header, including `crc_casts.h`, `generic_crc.h`, `gf_util.h`, `platform.h`, `crc32c_sse4_intrin.h`, and `uint128_sse2.h`.

## Risks and test signals

The fallback non-GCC/non-MSVC path aliases 64-bit types to 32-bit types while leaving TODOs about correctness, so unsupported compilers can silently lose 64-bit CRC behavior. The selection trick also assumes that matching sizes imply desirable alias reuse, which is performance-driven but can be surprising for ABI inspection. Test signals include compiling the library on 32-bit and 64-bit targets and running CRC unit vectors that exercise 32-bit, 64-bit, and 128-bit template instantiations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/code/base_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/code/crc32c_sse4.cc -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/code/crc32c_sse4.cc

## Purpose

`crc32c_sse4.cc` implements `Crc32cSSE4`, a fixed-polynomial CRC32C engine optimized for Intel/AMD x86 processors with the SSE4.2 `crc32` instruction, with a software emulation path when `CRCUTIL_USE_MM_CRC32` is disabled. It also implements `RollingCrc32cSSE4` initialization.

## Important APIs and functions

`Crc32cSSE4::Crc32c(const void *data, size_t bytes, Crc crc0)` is the main computation routine. It canonicalizes the start value, optionally aligns large inputs, processes large blocks as multiple stripes, combines stripe CRCs with precomputed multiplication tables, then handles word and byte tails. `Crc32cSSE4::Init(bool constant)` initializes the `GfUtil` base and multiplication tables for block sizes 512, 1024, 4096, and 32768 bytes, all using three stripes. If software CRC32 is selected, it also initializes `crc_word_`. `Crc32cSSE4::IsSSE42Available()` uses `__cpuid` on MSVC or inline `cpuid` on GCC to test ECX bit 20. `RollingCrc32cSSE4::Init()` precomputes outgoing-byte correction values for a fixed rolling window.

## Control flow, state, and persistence

The file maintains no global mutable state. Per-instance state lives in the multiplication tables and `GfUtil<Crc> base_` owned by `Crc32cSSE4`, and in `out_`, `start_value_`, `crc_`, and `roll_window_bytes_` owned by `RollingCrc32cSSE4`. `Crc32c()` uses goto labels generated by block macros to skip large-block loops when input is too small, then falls through to tail processing.

## Dependencies and integration points

It includes `crc32c_sse4.h`, depends on `GfUtil`, platform macros, and the `CRC_UPDATE_WORD`/`CRC_UPDATE_BYTE` abstraction from the header. Consumers should call `IsSSE42Available()` before using this implementation on binaries compiled for mixed CPU fleets. It integrates with `RollingCrc32cSSE4` and with build flags from `autogen.sh`/`Makefile.in`.

## Risks and test signals

Executing hardware `crc32` on a CPU without SSE4.2 will fault if callers skip runtime detection. The inline `cpuid` path has PIC-sensitive i386 handling and clobber constraints that are compiler-sensitive. The block table macro name uses a `num_blocks` token even though the macro argument is `num_stripes`; this works as a generated member name but is confusing and should be kept stable if edited. Test signals are CRC32C known-answer vectors across small, unaligned, aligned, large-block, and rolling-window inputs, plus CPU-feature dispatch tests on hosts with and without SSE4.2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/code/crc32c_sse4.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/code/crc32c_sse4.h -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/code/crc32c_sse4.h

## Purpose

`crc32c_sse4.h` declares the SSE4.2-oriented CRC32C implementation and its rolling CRC companion. It fixes the generating polynomial to Castagnoli CRC32C, exposes a `GenericCrc`-compatible interface, and abstracts hardware versus software byte/word updates through macros.

## Important APIs, types, and macros

`Crc32cSSE4` exports `typedef size_t Crc`, `Word`, and `TableEntry`. Key methods are `Init(bool canonical)`, compatibility `Init(const Crc&, size_t, bool)`, `FixedGeneratingPolynomial()` returning `0x82f63b78`, `FixedDegree()` returning 32, `Base()`, `CrcDefault()`, and `IsSSE42Available()`. `RollingCrc32cSSE4` provides `Init()`, `Start()`, `Roll()`, `StartValue()`, and `WindowBytes()`.

`CRC_UPDATE_WORD` maps to `_mm_crc32_u32` on i386 or `_mm_crc32_u64` on non-i386 x86 when `CRCUTIL_USE_MM_CRC32` is enabled. Otherwise it falls back to `CRC_WORD` and `CRC_BYTE` from `generic_crc.h`. The block enumeration macros define the tuned block sizes and stripe counts used in table declarations and implementation.

## Control flow, state, and persistence

The header describes per-instance state. `Crc32cSSE4` owns multiplication tables for every enumerated block size and the `GfUtil` base object. The fallback software path also stores `crc_word_` tables and grants friend access to `RollingCrc32cSSE4`. `RollingCrc32cSSE4` stores an outgoing-byte table and a borrowed pointer to the initialized CRC instance; the caller must keep that instance alive.

## Dependencies and integration points

The file depends on `gf_util.h`, `crc32c_sse4_intrin.h`, and conditionally `generic_crc.h`. It is only active under `HAVE_I386 || HAVE_AMD64`. It is designed to be used by higher-level crcutil interfaces, examples, and tests that select the fastest CRC32C backend after runtime CPU detection.

## Risks and test signals

The rolling class has a lifetime dependency on the referenced `Crc32cSSE4`. The compatibility `Init(generating_polynomial, degree, canonical)` silently does nothing if the polynomial or degree do not match the fixed CRC32C parameters, which can leave an object uninitialized if misused. Test signals include compile coverage for both `CRCUTIL_USE_MM_CRC32` paths, runtime dispatch checks, rolling CRC equivalence with recomputing each window, and ABI checks for alignment-sensitive table storage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/code/crc32c_sse4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/code/crc32c_sse4_intrin.h -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/code/crc32c_sse4_intrin.h

## Purpose

`crc32c_sse4_intrin.h` provides the `_mm_crc32_u8`, `_mm_crc32_u32`, and `_mm_crc32_u64` interfaces used by `crc32c_sse4.h`. It smooths over compiler differences by including native intrinsics when available, defining GCC builtin wrappers for GCC 4.5 or newer, or providing inline assembly for older GCC.

## Important APIs and functions

When MSVC or `__SSE4_2__` is available, the header includes `<nmmintrin.h>`. For GCC 4.5+ without `CRCUTIL_FORCE_ASM_CRC32C`, it defines always-inline wrappers around `__builtin_ia32_crc32qi`, `__builtin_ia32_crc32di`, or `__builtin_ia32_crc32si`. For older GCC, it defines namespace `crcutil` inline assembly functions emitting `crc32q`, `crc32l`, and `crc32b`.

## Control flow, state, and persistence

There is no runtime state. All behavior is compile-time selected by `CRCUTIL_USE_MM_CRC32`, `HAVE_I386`, `HAVE_AMD64`, `_MSC_VER`, `__SSE4_2__`, GCC version, and `CRCUTIL_FORCE_ASM_CRC32C`.

## Dependencies and integration points

The file depends on `platform.h` for architecture/compiler macros and `base_types.h` for crcutil integer aliases. It is consumed by `crc32c_sse4.h`. Build flags such as `-mcrc32`, `-msse4.2`, or MSVC target settings determine whether builtin or header-provided intrinsics compile.

## Risks and test signals

The GCC builtin path explicitly warns that compiling without `-msse4` or `-mcrc32` while enabling `CRCUTIL_USE_MM_CRC32` can fail because GCC hides the builtins. The inline assembly path is x86-only and compiler-constraint-sensitive. This header does not perform runtime CPU detection; it only makes instructions available. Test signals are compilation under MSVC, GCC old/new, i386, and amd64 configurations, plus execution guarded by `Crc32cSSE4::IsSSE42Available()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/code/crc32c_sse4_intrin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/code/crc_casts.h -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/code/crc_casts.h

## Purpose

`crc_casts.h` centralizes conversions between crcutil CRC value types and smaller integer representations. It exists so scalar CRC types and compound CRC types such as `uint128_sse2` can share generic table and byte-processing code while still providing specialized downcasts.

## Important APIs and macros

`Downcast<Crc, Result>(const Crc &x)` defaults to `static_cast<Result>(x)` and can be specialized by complex CRC classes. `TO_BYTE(x)` extracts the least significant byte by downcasting to `uint8`. `CrcFromUint64<Crc>(uint64 lo, uint64 hi = 0)` constructs a CRC value from one or two 64-bit words, using `SHIFT_LEFT_SAFE` when the target is wider than 64 bits. `Uint64FromCrc<Crc>(const Crc&, uint64 *lo, uint64 *hi = NULL)` extracts low and optional high 64-bit words.

## Control flow, state, and persistence

The file has no runtime state. The functions are inline templates used inside CRC table lookup loops, GF arithmetic, and tests/examples that need to serialize or inspect CRC values.

## Dependencies and integration points

It includes `base_types.h` and `platform.h`. `generic_crc.h`, `gf_util.h`, `rolling_crc.h`, and `uint128_sse2.h` depend on it. `uint128_sse2.h` supplies specializations for downcasting and two-word conversion.

## Risks and test signals

For wider CRC types, callers are responsible for ensuring `hi` is meaningful and that shifting/composition matches the CRC type's byte ordering. `Uint64FromCrc` writes `*hi` in the wide case without checking for null, so callers must pass `hi` when `sizeof(crc) > sizeof(*lo)`. Test signals include round-tripping scalar and `uint128_sse2` values through `CrcFromUint64`/`Uint64FromCrc`, and verifying `TO_BYTE` in table-driven CRC loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/code/crc_casts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/code/generic_crc.h -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/code/generic_crc.h

## Purpose

`generic_crc.h` defines `GenericCrc`, a table-driven template for arbitrary CRC polynomials and widths. It supports byte-at-a-time, word-at-a-time, block-striped, and interleaved multiword CRC algorithms, and it declares architecture-specific specializations used for faster 64-bit and 128-bit paths.

## Important APIs, types, and macros

`GenericCrc<_Crc, _TableEntry, _Word, kStride>` exports `Crc`, `TableEntry`, and `Word`. Public construction and `Init(generating_polynomial, degree, canonical)` initialize `GfUtil` and the byte/word lookup tables. `CrcDefault()` selects `CrcMultiword()` on i386/amd64 and `CrcByteUnrolled()` elsewhere. `Base()` exposes the underlying `GfUtil<Crc>`.

Important protected algorithms are `CrcByte()`, `CrcByteUnrolled()`, `CrcByteWord()`, `CrcWord()`, `CrcBlockword()`, and `CrcMultiword()`. Macros `CRC_BYTE`, `CRC_WORD`, `ALIGN_ON_WORD_BOUNDARY`, and table-entry helpers implement tight loops with type-generic downcasts.

## Control flow, state, and persistence

Instance state consists of `crc_word_interleaved_`, `crc_word_`, and `base_`, aligned to 16 bytes. Initialization precomputes tables by multiplying byte values by powers of x in GF(2), using a power-of-two fill optimization. Runtime computation canonicalizes the start value, optionally aligns input, chooses a loop shape based on byte count and `kStride`, processes full words or stripes, then handles byte tails before de-canonicalizing the result.

## Dependencies and integration points

It depends on `base_types.h`, `crc_casts.h`, `gf_util.h`, `platform.h`, and `uint128_sse2.h`. `rolling_crc.h` is a friend consumer of `crc_word_`. Specialized implementations are declared for GCC amd64, GCC amd64 SSE2, GCC i386 MMX, and selected MSVC i386 MMX paths.

## Risks and test signals

The code relies on reinterpret-casting byte pointers to `Word *` after alignment logic, so strict-aliasing and alignment assumptions matter. `kStride` outside 2..8 falls back, but tuned paths expect 4 in specializations. The template is dense with macros and compile-time conditionals, making small edits high risk. Test signals include known CRC vectors for multiple widths/polynomials, randomized split/concatenate comparisons through `GfUtil`, unaligned buffer tests, small-tail sizes, and build coverage with `CRCUTIL_USE_ASM` on and off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/code/generic_crc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/code/gf_util.h -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/code/gf_util.h

## Purpose

`gf_util.h` implements finite-field polynomial arithmetic and CRC helper operations that are independent of a specific byte-processing algorithm. It is the mathematical foundation for table generation, CRC concatenation, zero-block CRCs, rolling-window correction tables, and storing CRC complements.

## Important APIs and functions

`GfUtil<Crc>` is parameterized by CRC value type. `Init(generating_polynomial, degree, canonical)` sets polynomial metadata, canonicalization mask, powers of x, normalization values, `crc_of_crc_`, and the inverse-like factor `x_pow_minus_W_`. Query methods include `GeneratingPolynomial()`, `Degree()`, `Canonize()`, and `One()`.

Core helpers include `ChangeStartValue()`, `Concatenate()`, `CrcOfZeroes()`, `StoreComplementaryCrc()`, `StoreCrc()`, `CrcOfCrc()`, `Multiply()`, `MultiplyUnnormalized()`, `XpowN()`, `Xpow8N()`, `Divide()`, and `FindLCD()`.

## Control flow, state, and persistence

State is per-instance and consists of canonicalization, powers table `x_pow_2n_`, polynomial, normalized one, inverse/correction values, and degree/byte counts. `Multiply()` performs carryless polynomial multiplication reduced by the configured generating polynomial. `XpowN()` exponentiates by square-and-multiply using precomputed `x_pow_2n_`. `FindLCD()` uses an extended Euclidean algorithm over GF(2) polynomials.

## Dependencies and integration points

It includes `base_types.h`, `crc_casts.h`, and `platform.h`. It is embedded inside `GenericCrc` and `Crc32cSSE4`, and is also used by rolling and protected CRC helpers. Its `MultiplyUnnormalized()` drives CRC table generation in both generic and SSE4 implementations.

## Risks and test signals

The code assumes valid degree and polynomial input; for example `degree - 1` is shifted during initialization. Incorrect polynomial metadata corrupts every derived table. `FindLCD()` and `Divide()` are subtle and should be validated with algebraic invariants. Test signals include CRC concatenation equivalence, `CrcOfZeroes` versus real zero buffers, `StoreComplementaryCrc` producing a requested final CRC, `StoreCrc` yielding `CrcOfCrc`, and randomized multiplication/distribution checks for supported CRC widths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/code/gf_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/code/multiword_128_64_gcc_amd64_sse2.cc -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/code/multiword_128_64_gcc_amd64_sse2.cc

## Purpose

This file implements the GCC amd64 SSE2 specialization of `GenericCrc<uint128_sse2, uint128_sse2, uint64, 4>::CrcMultiword`. It accelerates 128-bit CRCs with 64-bit reads, four-way interleaving, and SSE2 registers for CRC state.

## Important APIs and functions

The specialization provides `CrcMultiword()` and the internal `CrcMultiwordGccAmd64Sse2(const uint8 *src, const uint8 *end, const uint128_sse2 &start)`. `CrcMultiword()` handles very small inputs byte-by-byte, aligns the source on a `uint64` boundary for larger inputs, canonicalizes the start value, and delegates to the assembly routine. `CRC_WORD_ASM()` is a macro that consumes one 64-bit word using the word table and SSE2 shifts/xors.

## Control flow, state, and persistence

No new persistent state is introduced; the implementation consumes `crc_word_`, `crc_word_interleaved_`, and `Base()` from the `GenericCrc` instance. The assembly routine subtracts sentinel lengths from `end`, runs a main loop over four 64-bit buffers and four SSE CRC registers, propagates high-half carryover for 128-bit CRC state, combines the four lanes, then finishes word and byte tails.

## Dependencies and integration points

It includes `generic_crc.h` and `uint128_sse2.h` and is compiled only for `defined(__GNUC__) && CRCUTIL_USE_ASM && HAVE_AMD64 && HAVE_SSE2`. It relies on `SSE2_MOVQ` from `platform.h` to work around Apple/GCC instruction spelling issues.

## Risks and test signals

The inline assembly has many register, pointer, and table-offset assumptions; it is high-risk under compiler upgrades or non-GNU assemblers. It assumes 16-byte-aligned SSE table entries and correct `uint128_sse2` conversions. Test signals are 128-bit CRC known-answer vectors, comparison against the generic non-asm path, small sizes 0..63, unaligned buffers, large buffers, and compilation under GCC versions around the documented workarounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/code/multiword_128_64_gcc_amd64_sse2.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/code/multiword_64_64_cl_i386_mmx.cc -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/code/multiword_64_64_cl_i386_mmx.cc

## Purpose

This file implements the MSVC/Intel C++ i386 MMX specialization for 64-bit CRC multiword processing. It exists to work around compiler performance and code-generation limitations on 32-bit Windows-era compilers while keeping the same `GenericCrc<uint64, uint64, uint64, 4>` interface.

## Important APIs and functions

The main specialization is `GenericCrc<uint64, uint64, uint64, 4>::CrcMultiwordI386Mmx(const void *data, size_t bytes, const uint64 &start)`. The file defines the `CRC_WORD_MMX()` macro in MSVC inline assembly form and maps symbolic names such as `CRC0`, `BUF0`, `SRC`, and `TABLE` to MMX and integer registers.

## Control flow, state, and persistence

The function canonicalizes `start`, aligns the source when needed, and then enters inline assembly. The main loop processes four 64-bit buffers through four MMX CRC lanes using `crc_word_interleaved_`. It then combines those lanes through the normal word table, processes remaining 64-bit words, and leaves remaining bytes to a C loop because the byte-loop assembly variant is disabled as slower. `emms` is issued before returning to clear MMX state.

## Dependencies and integration points

It includes `generic_crc.h` and compiles only under `CRCUTIL_USE_ASM && HAVE_I386 && HAVE_MMX && defined(_MSC_VER)`. It depends on Microsoft inline assembly syntax and warning pragmas for frame-pointer/register behavior.

## Risks and test signals

The code modifies `ebp`, disables warning 4731, and relies on 32-bit MSVC inline assembly, which is not supported in x64 MSVC. The assembly stores `END` on the stack and has tight register allocation assumptions. Missing `emms` would corrupt later floating-point/MMX use; this file explicitly emits it. Test signals are MSVC i386 builds, byte-size sweeps around 0..64, unaligned buffers, comparison with generic C++ output, and tests that run floating-point code after CRC to catch MMX cleanup issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/code/multiword_64_64_cl_i386_mmx.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/code/multiword_64_64_gcc_amd64_asm.cc -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/code/multiword_64_64_gcc_amd64_asm.cc

## Purpose

This file implements the GCC amd64 assembly specialization for 64-bit CRCs using 64-bit table lookups and four-way interleaving. It is selected for `GenericCrc<uint64, uint64, uint64, 4>` when GCC, amd64, and `CRCUTIL_USE_ASM` are available.

## Important APIs and functions

It specializes `CrcMultiword()` and declares/defines `CrcMultiwordGccAmd64()`. The public specialization uses an unrolled C++ fast path for inputs up to `6 * sizeof(Word) - 1`, then delegates to the assembly implementation for larger inputs. The `CRC_WORD_ASM()` macro updates a 64-bit CRC from one 64-bit buffer using `crc_word_`, while the main loop uses `crc_word_interleaved_`.

## Control flow, state, and persistence

Persistent state remains in the parent `GenericCrc` tables. Runtime flow aligns input, initializes four CRC lanes, loads four 64-bit buffers, iterates over 32-byte chunks, computes table lookups byte by byte with optimized register usage, combines lanes with four `CRC_WORD_ASM()` calls, then processes remaining words and bytes. The result is de-canonicalized before return.

## Dependencies and integration points

It includes `generic_crc.h` and is gated by `defined(__GNUC__) && CRCUTIL_USE_ASM && HAVE_AMD64`. It relies on GNU extended inline assembly, x86-64 register names, and table layout from `GenericCrc`.

## Risks and test signals

The assembly clobbers fixed registers including `%rbx`, which is callee-saved under the SysV ABI; correctness depends on GCC saving/restoring around the inline asm according to constraints. Comments indicate performance tradeoffs and compiler sensitivity. Test signals include ABI-sensitive tests under optimized builds, comparison against `CRCUTIL_USE_ASM=0`, unaligned buffers, tail sizes around the C++ fast-path threshold, and sanitizer or valgrind runs to catch out-of-bounds tail handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/code/multiword_64_64_gcc_amd64_asm.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/code/multiword_64_64_gcc_i386_mmx.cc -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/code/multiword_64_64_gcc_i386_mmx.cc

## Purpose

This file implements the GCC i386 MMX assembly specialization for 64-bit CRCs. It accelerates `GenericCrc<uint64, uint64, uint64, 4>` on 32-bit x86 by keeping four CRC lanes in MMX registers.

## Important APIs and functions

It specializes `CrcMultiword()` and `CrcMultiwordI386Mmx()`. The top-level specialization handles inputs of 7 bytes or less with `CRC_BYTE`, otherwise calls the MMX routine. `CRC_WORD_MMX()` is the inline assembly macro for consuming one 64-bit word with the word table.

## Control flow, state, and persistence

The function canonicalizes the start CRC, aligns to a 64-bit boundary if the size threshold requires it, then executes GNU inline assembly. The main loop processes 32 bytes per iteration with four 64-bit MMX buffers and four CRC lanes using interleaved tables. It combines lane CRCs, processes full 64-bit tail words, then handles byte tails in assembly. `asm volatile("emms")` clears MMX state before returning.

## Dependencies and integration points

It includes `generic_crc.h` and compiles only when `defined(__GNUC__) && CRCUTIL_USE_ASM && HAVE_I386 && HAVE_MMX`. It uses `GCC_OMIT_FRAME_POINTER` on the function declaration to free registers and optionally emits SSE prefetch instructions if configured.

## Risks and test signals

The code is tightly coupled to GCC i386 register constraints, MMX availability, and frame-pointer omission. The trailing comment incorrectly names `HAVE_AMD64`, but the actual preprocessor guard is i386/MMX. MMX state cleanup is mandatory. Test signals include GCC i386 optimized builds, asm-disabled comparisons, CRC vectors over small and large buffers, unaligned input tests, and post-CRC floating-point/MMX state checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/code/multiword_64_64_gcc_i386_mmx.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/code/multiword_64_64_intrinsic_i386_mmx.cc -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/code/multiword_64_64_intrinsic_i386_mmx.cc

## Purpose

This file implements a 32-bit x86 MMX specialization using MMX intrinsic functions instead of large inline assembly blocks. It targets the same `GenericCrc<uint64, uint64, uint64, 4>` multiword path and is available for i386/MMX builds with `CRCUTIL_USE_ASM`.

## Important APIs and functions

It specializes `CrcMultiword()` for non-MSVC builds and defines `CrcMultiwordI386Mmx()`. The `CRC_WORD_MMX(this, crc, buf)` macro uses `_mm_xor_si64`, `_mm_cvtsi64_si32`, `_mm_srli_si64`, and table loads to fold one 64-bit word into a CRC lane. `MM64()` and `MM64_TABLE()` cast table memory to `__m64` pointers.

## Control flow, state, and persistence

The function canonicalizes input, aligns the source, and processes data in two phases. For large enough aligned input, it runs a four-lane loop over 32-byte chunks using `crc_word_interleaved_`, then combines the lanes through `CRC_WORD_MMX`. It then processes remaining full 64-bit words one at a time and finishes byte tails with `CRC_BYTE`. `_mm_empty()` is called after MMX phases.

## Dependencies and integration points

It includes `generic_crc.h` and relies on MMX intrinsics being available through compiler headers included indirectly by platform/compiler configuration. It shares the same table layout as the assembly implementations and is conditionally adapted for MSVC warning behavior, although MSVC's primary inline-assembly specialization lives in `multiword_64_64_cl_i386_mmx.cc`.

## Risks and test signals

Intrinsic code is more portable than raw assembly but still relies on MMX state, pointer casts to `__m64`, and compiler support. The macro parameter named `this` is unusual but valid in macro substitution; edits should be cautious. Test signals include output equivalence with generic CRC, large and small input sweeps, i386/MMX compile coverage, and checks that `_mm_empty()` runs before subsequent floating-point code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/code/multiword_64_64_intrinsic_i386_mmx.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/code/platform.h -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/code/platform.h

## Purpose

`platform.h` centralizes compiler, CPU, SIMD, prefetch, alignment, and utility macro detection for crcutil. It supplies defaults for optional acceleration features and hides compiler-specific spellings from the CRC algorithm headers.

## Important macros and configuration

Defaults include `CRCUTIL_USE_ASM=1`, architecture macros `HAVE_I386` and `HAVE_AMD64`, feature macros `HAVE_MMX`, `HAVE_SSE`, and `HAVE_SSE2`, `CRCUTIL_PREFETCH_WIDTH=0`, `CRCUTIL_MIN_ALIGN_SIZE`, and `CRCUTIL_USE_MM_CRC32`. Utility macros include `PREFETCH(src)`, `TO_STRING`, `SHIFT_RIGHT_SAFE`, `SHIFT_LEFT_SAFE`, `GCC_VERSION_AVAILABLE`, `GCC_ALIGN_ATTRIBUTE`, `GCC_OMIT_FRAME_POINTER`, `SSE2_MOVQ`, and `__forceinline`.

## Control flow, state, and persistence

There is no runtime state. All behavior is compile-time conditional. The header includes SIMD headers when compiler macros indicate support, emits compile-time errors for inconsistent SSE/MMX combinations, and defines safe-shift wrappers to avoid warnings for shifts equal to or wider than the type width.

## Dependencies and integration points

It includes `std_headers.h` first, partly to apply MSVC warning suppression before standard/compiler headers. Nearly every crcutil source depends on this file for architecture gates, alignment attributes, forced inline, prefetch, and shift behavior. Build flags such as `-msse2`, `-mcrc32`, and compiler target architecture directly influence this header's decisions.

## Risks and test signals

Feature detection is compile-time, not runtime, except for separate CPU checks in `Crc32cSSE4`. Compiling with SIMD flags can enable code generation that will fault on older CPUs unless callers dispatch correctly. Some defaults are old-toolchain-oriented and may not match modern cross-compilation expectations. Test signals are matrix builds across x86, non-x86, GCC, Clang-compatible GCC macros, and MSVC, plus runtime tests on CPUs with different SSE/SSE4 capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/code/platform.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/code/protected_crc.h -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/code/protected_crc.h

## Purpose

`protected_crc.h` defines `ProtectedCrc`, a thin wrapper that lets a CRC implementation compute a CRC over its own table/object memory. The goal is to detect corrupted CRC tables before corrupted tables poison application data.

## Important APIs and types

`ProtectedCrc<CrcImplementation>` publicly inherits from the implementation and exports `typedef typename CrcImplementation::Crc Crc`. Its only method is `SelfCheckValue()`, which calls `CrcDefault(this, sizeof(*this), 0)` and returns the resulting check value. The returned value is intended to be compared with a trusted precomputed constant.

## Control flow, state, and persistence

The wrapper does not add fields. It depends entirely on the base implementation's initialized table state. The comments warn that computing a self-check once after initialization and storing it next to the object is insufficient if the initialization itself was corrupt; the trusted value should come from outside the potentially corrupt runtime state.

## Dependencies and integration points

It assumes the implementation has no virtual functions because a runtime vptr would make the object memory unstable across runs. It also assumes `CrcDefault()` can safely read the complete object representation. It uses `GCC_ALIGN_ATTRIBUTE(16)` from `platform.h`, but this header does not include `platform.h` itself, so it depends on include order from users.

## Risks and test signals

CRC over raw object memory can be sensitive to padding bytes, compiler layout, and uninitialized fields. Public inheritance means object layout equals base fields plus no added state, but changes to base classes can change the trusted check value. Test signals include deterministic self-check values across clean builds with the same compiler/options, deliberate bit flips in table memory, and checks after CRC mismatch paths before data is accepted or written.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/code/protected_crc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/code/rolling_crc.h -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/code/rolling_crc.h

## Purpose

`rolling_crc.h` implements a generic rolling CRC adapter for fixed-size windows, suitable for Rabin-fingerprint-like sliding-window use. It lets callers compute the first window with the underlying CRC implementation and then update the CRC when one byte leaves and one byte enters.

## Important APIs and types

`RollingCrc<CrcImplementation>` requires the implementation to provide `Crc`, `TableEntry`, `Word`, `CrcDefault()`, and `Base()`. It exports `Start(const void *data)`, `Roll(const Crc &old_crc, size_t byte_out, size_t byte_in)`, `Init(const CrcImplementation&, size_t roll_window_bytes, const Crc &start_value)`, `StartValue()`, and `WindowBytes()`.

## Control flow, state, and persistence

`Init()` stores a borrowed pointer to the CRC implementation, the window size, and the start value. It precomputes `out_[256]` for outgoing byte corrections using `GfUtil` powers and `MultiplyUnnormalized`, and `in_[256]` from the implementation's last word table. `Start()` computes the CRC of the first window by delegating to the implementation. `Roll()` shifts the old CRC by one byte, applies the incoming-byte table entry, and xors the outgoing-byte correction.

## Dependencies and integration points

It includes `base_types.h` and `crc_casts.h`. It relies on access to `crc.crc_word_`, which is possible because `GenericCrc` declares the corresponding `RollingCrc` specialization as a friend. This tight coupling means alternative implementations must expose compatible internals or provide their own rolling class, as `Crc32cSSE4` does.

## Risks and test signals

The class stores a raw pointer to the CRC implementation, so lifetime is the caller's responsibility. `byte_out` and `byte_in` are `size_t`, but table indexing assumes byte values 0..255. Test signals include comparing `Roll()` output against recomputing `Start()` for every window over random buffers, window sizes 1 and large sizes, nonzero start values, canonical and noncanonical CRCs, and invalid-byte defensive tests if callers can pass wider values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/code/rolling_crc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/code/std_headers.h -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/code/std_headers.h

## Purpose

`std_headers.h` centralizes standard C header inclusion and suppresses several MSVC warnings produced by Microsoft headers or by aggressive optimization diagnostics. It provides the common definitions used by crcutil's low-level headers.

## Important APIs and macros

The file defines `_CRT_SECURE_NO_WARNINGS` under MSVC and disables warning numbers 4820, 4514, 4127, 4710, and 4711. It includes `<stdio.h>`, `<string.h>`, `<stdlib.h>`, `<stddef.h>`, and `<stdarg.h>`, providing declarations and types such as `memset`, `memcpy`, `size_t`, `ptrdiff_t`, and `va_list`.

## Control flow, state, and persistence

There is no runtime logic or persistent state. The header affects compiler diagnostics and transitive availability of standard-library names.

## Dependencies and integration points

`base_types.h` includes it for `size_t` and `ptrdiff_t`; `platform.h` includes it before compiler intrinsic headers to apply warning policy. Many crcutil files inherit these standard includes transitively rather than including C headers directly.

## Risks and test signals

Broad warning suppression can hide useful diagnostics in files that include this header. The project uses C headers rather than C++ `<c*>` headers, so names are expected in the global namespace. Test signals are simple compile coverage under MSVC and GCC/Clang-like compilers, plus verifying that downstream headers do not accidentally depend on additional standard headers that are not included here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/code/std_headers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/code/uint128_sse2.h -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/code/uint128_sse2.h

## Purpose

`uint128_sse2.h` defines `uint128_sse2`, a limited 128-bit unsigned value type implemented with SSE2 intrinsics. It supplies exactly the operations crcutil needs for 128-bit CRC arithmetic and table lookups.

## Important APIs and types

When `HAVE_SSE2` is true, the file specializes `Downcast<__m128i, uint64>`, defines class `uint128_sse2`, and specializes `Downcast<uint128_sse2, uint64/uint32/uint16/uint8>`, `CrcFromUint64<uint128_sse2>()`, and `Uint64FromCrc<uint128_sse2>()`. The class supports construction and assignment from `uint64` and `__m128i`, conversion to `__m128i`, `to_uint64()`, equality/inequality, a less-than comparison, bitwise `^`, `&`, `|`, compound bitwise operators, addition/subtraction by `uint64`, and logical shifts.

## Control flow, state, and persistence

The object stores one `__m128i x_` and has no heap state. Fast shift paths use byte-lane SSE shifts for 8, 16, 32, and 64 bits; other shifts fall back to bit-by-bit loops over union views. Downcast workarounds use inline assembly or memory stores for compiler versions known to generate bad or slow code.

## Dependencies and integration points

It includes `base_types.h`, `crc_casts.h`, and `platform.h`. It is used by `generic_crc.h` and `multiword_128_64_gcc_amd64_sse2.cc` to support 128-bit CRCs. Alignment is enforced with `GCC_ALIGN_ATTRIBUTE(16)`.

## Risks and test signals

The class is not a complete arbitrary-precision integer; it only implements operations needed by crcutil. The less-than implementation compares low 64 bits before high 64 bits, which is unusual for numeric ordering but appears only to support algorithmic heuristics. Union aliasing and aligned SSE stores can be compiler-sensitive. Test signals include conversion round trips, shift/add/subtract edge cases around 64-bit carries, bitwise operations, 128-bit CRC known vectors, and builds with and without SSE2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/code/uint128_sse2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/config.h.in -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/config.h.in

## Purpose

`config.h.in` is the Autoheader template for crcutil's generated `config.h`. During `./configure`, Autoconf substitutes each `#undef` with a concrete definition or leaves it undefined based on platform probes.

## Important macros

The template includes header availability macros such as `HAVE_INTTYPES_H`, `HAVE_MEMORY_H`, `HAVE_STDDEF_H`, `HAVE_STDINT_H`, `HAVE_STDLIB_H`, `HAVE_STRING_H`, `HAVE_STRINGS_H`, `HAVE_SYS_STAT_H`, `HAVE_SYS_TYPES_H`, and `HAVE_UNISTD_H`; function probes such as `HAVE_MEMSET`, `HAVE_STRCHR`, and `HAVE_STRRCHR`; type probes such as `HAVE_PTRDIFF_T`, `HAVE__BOOL`, and fallback typedef macros for `size_t`; package metadata macros such as `PACKAGE`, `PACKAGE_NAME`, `PACKAGE_VERSION`, and `VERSION`; and an inline keyword fallback for C compilation.

## Control flow, state, and persistence

There is no runtime control flow. Its persistent role is as input to `config.status`, which writes `config.h`. Generated `config.h` influences compile-time portability decisions in code that includes it, although the crcutil headers in this subset mostly use their own `platform.h` probes.

## Dependencies and integration points

It is generated by `autoheader` from `configure.ac`, referenced by `Makefile.in`, and regenerated by `autogen.sh`. It integrates with Autoconf tests and the C/C++ compiler used by `configure`.

## Risks and test signals

Because this is generated, direct edits are fragile unless mirrored in Autoconf inputs. Missing or stale `config.h.in` can prevent `configure` from producing `config.h`. Some macros are generic Autoconf probes and may not be actively consumed by crcutil's current code. Test signals include rerunning `autogen.sh configure`, verifying `config.h` generation, and compiling with clean generated configuration on target platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/config.h.in -->
