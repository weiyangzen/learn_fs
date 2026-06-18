# Group Research: group_1194_netbsd_src_sources_os_bsd_netbsd_src_lib_libc_gdtoa_test_Qtest_c_so_b2bbcadb846f

Scope checked against `Docs/research_subset_a.md`: `sources/os/bsd/netbsd-src` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/Qtest.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/Qtest.c

Standalone gdtoa test program for quad-format conversion helpers: `g_Qfmt`, `strtoIQ`, `strtopQ`, and `strtorQ`.

It reads stdin commands for rounding mode (`r`), output digit count (`n`), decimal numbers, or raw 4-word hexadecimal long-double/quad representations. It uses endian-specific `_0.._3` word index macros and compares nearest-rounding `strtorQ` results against `strtopQ`.

Important behavior:
- Maintains current directed rounding mode through `getround`.
- Prints parsed bit patterns and `g_Qfmt` formatted output.
- If the host `long double` looks like 16-byte quad, also prints `%.35Lg`.
- For decimal inputs, tests interval conversion with `strtoIQ`, reporting whether interval endpoints match the rounded result.

Dependencies: `gdtoa.h`, `getround.c`, quad gdtoa conversion/formatting objects, endian configuration macros.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/Qtest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/dItest.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/dItest.c

Small stdin-driven test program for double interval conversion. It compares `strtodI` against `strtoId`.

Core flow:
- Reads one number per line.
- Calls `strtodI(ibuf, &se, dd)` to get two bounding doubles.
- Prints each bound through helper `dshow`, which uses `g_dfmt` and raw double words.
- Calls `strtoId` and reports mismatches in return code, consumed input, or endpoint values.

Dependencies: `gdtoaimp.h`, `g_dfmt`, `strtodI`, `strtoId`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/dItest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/ddtest.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/ddtest.c

Test driver for double-double gdtoa support: `g_ddfmt`, `strtoIdd`, `strtopdd`, and `strtordd`.

Input model:
- `r` changes directed rounding mode.
- `n` changes digit count for `g_ddfmt`.
- `#` supplies four raw hex words for two doubles.
- A single decimal string tests `strtordd`; two numeric fields can be parsed through native `strtod`.

Important behavior:
- For nearest rounding, checks `strtordd` against `strtopdd`.
- Prints each component double via `g_dfmt`.
- Uses `strtoIdd` to compute interval double-double bounds and compares them against the rounded pair.

Dependencies: `gdtoaimp.h`, `getround`, `g_dfmt`, `g_ddfmt`, double-double parse helpers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/ddtest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/dt.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/dt.c

Legacy gdtoa/dtoa test harness for double conversion.

It accepts decimal strings or raw `#hex0 hex1[: mode ndigits]` inputs, converts with `strtod`, compares with `atof`, formats with a local `g_fmt` wrapper around `dtoa`, and probes adjacent representable values by incrementing/decrementing the low word.

Important behavior:
- Global `STRTOD_DIGLIM` defaults to `24`.
- `check()` round-trips a `dtoa` result back through `strtod` and reports bit mismatches.
- Handles VAX word adjustments conditionally.
- Prints `dtoa` sign, decimal point, digit count, and digit string for requested mode/precision.

Dependencies: `gdtoa.h`, `dtoa`, `strtod`, platform word-order macros.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/dt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/dtest.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/dtest.c

Test program for ordinary double gdtoa entry points: `g_dfmt`, `strtoId`, `strtod`, `strtopd`, and `strtord`.

Behavior:
- Reads rounding changes, digit-count changes, raw two-word hex doubles, or decimal inputs.
- For nearest rounding, compares `strtord` with both libc `strtod` and `strtopd`.
- Formats the result through `g_dfmt`.
- Uses `strtoId` to produce lower/upper interval bounds and reports their relation to the rounded result.

Dependencies: `gdtoaimp.h`, `getround`, double conversion/format helpers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/dtest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/ftest.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/ftest.c

Float-format equivalent of `dtest.c`, covering `g_ffmt`, `strtof`, `strtoIf`, `strtopf`, and `strtorf`.

Behavior:
- Accepts rounding mode, digit count, raw one-word hex float, or decimal input.
- For nearest rounding, checks agreement among `strtorf`, `strtopf`, and libc `strtof`.
- Formats floats with `g_ffmt`.
- Reports interval endpoints from `strtoIf` and whether either endpoint equals the rounded float.

Dependencies: `gdtoa.h`, `getround`, float parse/format helpers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/ftest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/getround.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/getround.c

Shared helper for gdtoa tests to parse and report directed rounding modes.

`getround(int r, char *s)`:
- With no argument, prints current mode.
- Accepts modes `0` toward zero, `1` nearest, `2` toward +Infinity, `3` toward -Infinity.
- If `Honor_FLT_ROUNDS` is defined, maps modes to `<fenv.h>` constants and calls `fesetround`.

Optional `USE_MY_LOCALE` block supplies a custom `localeconv()` with decimal point `"<Pt>"`.

Dependencies: optional `fenv.h`, optional `locale.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/getround.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/makefile

Test makefile for building and running the gdtoa validation programs.

Important targets:
- Builds `dt`, `dItest`, `ddtest`, `dtest`, `ftest`, `Qtest`, `xtest`, `xLtest`, sudden-underflow variants, `strtodt`, `strtodtnrp`, and `pftest`.
- `Q.out x.out xL.out` uses `xQtest` to select expected output files based on `sizeof(long double)`.
- `tests` compares generated outputs against checked-in `.out` files, collecting mismatches in `bad`.
- Notes that Intel-like extended precision may cause `strtodt` double-rounding surprises, while `strtodtnrp` should not.

Build details:
- Uses `-I..` and architecture gdtoa include directory.
- Uses `INFFIX` sed normalization for infinity spelling.
- `xsum.out` verifies the test corpus checksum.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/pftest.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/pftest.c

Printf-format test program using `stdio1.h` and gdtoa conversion routines.

Behavior:
- Maintains a current printf format string, default `"%.g"`.
- Lines beginning with `%` update the format and infer type mode: double, long double/extended, or quad where available.
- Parses subsequent numeric text with `strtod`, `strtopx`, or `strtopQ` depending on architecture and mode.
- Prints raw representation and then applies the requested printf format.

Architecture conditionals handle x86_64, i386, sparc, Intel compiler exclusions, and optional `__float128` quad support.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/pftest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/strtoIdSI.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/strtoIdSI.c

Two-line sudden-underflow wrapper:
- Defines `Sudden_Underflow`.
- Includes `../strtoId.c`.

Purpose: compile the double interval converter under sudden-underflow semantics for comparison tests.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/strtoIdSI.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/strtoIddSI.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/strtoIddSI.c

Two-line sudden-underflow wrapper:
- Defines `Sudden_Underflow`.
- Includes `../strtoIdd.c`.

Purpose: build the double-double interval converter with sudden-underflow behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/strtoIddSI.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/strtodISI.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/strtodISI.c

Two-line sudden-underflow wrapper:
- Defines `Sudden_Underflow`.
- Includes `../strtodI.c`.

Purpose: build the double interval `strtodI` implementation for sudden-underflow tests.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/strtodISI.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/strtodt.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/strtodt.c

Data-file validator for libc/gdtoa `strtod`.

Input format: triples containing decimal string plus expected high/low hex words. It can read stdin or named files.

Behavior:
- Determines host double word order at runtime using `1.0`.
- For each non-comment line, parses expected words with `strtoul`.
- Converts the decimal prefix with `strtod`.
- Reports bit mismatches and returns nonzero if any bad conversions occurred.
- `-?` prints usage.

Dependencies: `gdtoa.h` for `ULong`, libc `strtod`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/strtodt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/strtopddSI.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/strtopddSI.c

Two-line sudden-underflow wrapper:
- Defines `Sudden_Underflow`.
- Includes `../strtopdd.c`.

Purpose: build nearest-rounded double-double parsing under sudden-underflow semantics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/strtopddSI.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/strtorddSI.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/strtorddSI.c

Two-line sudden-underflow wrapper:
- Defines `Sudden_Underflow`.
- Includes `../strtordd.c`.

Purpose: build directed-rounding double-double parsing under sudden-underflow semantics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/strtorddSI.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/xLtest.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/xLtest.c

Test driver for extended long-double format using three `ULong` words: `g_xLfmt`, `strtoIxL`, `strtopxL`, and `strtorxL`.

Behavior:
- Handles rounding mode, output digit count, raw hex words, and decimal inputs.
- Uses endian-specific `_0.._2` word ordering.
- For nearest rounding, compares `strtorxL` with `strtopxL`.
- Tests interval conversion through `strtoIxL`.
- If `sizeof(long double) == 12`, prints `%.21Lg` for host-readable output.

Dependencies: `gdtoa.h`, `getround`, extended long-double gdtoa helpers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/xLtest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/xQtest.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/xQtest.c

Small generator used by the makefile to choose expected gdtoa test output files.

Behavior:
- Switches on `sizeof(long double)`.
- For 16-byte long double, distinguishes true quad from padded/extended forms by computing `1/3` and checking first/last words.
- Prints shell `cp` commands selecting `x.out`, `xL.out`, `Q.out`, and `pftest.out`.

Purpose: adapt tests to platform long-double representation without hardcoding in the makefile.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/xQtest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/xtest.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/xtest.c

Test driver for 80-bit extended format represented as five 16-bit words: `g_xfmt`, `strtoIx`, `strtopx`, and `strtorx`.

Behavior:
- Reads rounding, digit count, raw half-word hex representation, or decimal input.
- Uses endian-specific `_0.._4` word indexes.
- For nearest rounding, checks `strtorx` against `strtopx`.
- Tests interval results from `strtoIx`.
- Prints host `long double` only when `sizeof(long double) == 12`.

Dependencies: `gdtoa.h`, `getround`, extended-format conversion helpers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/xtest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/ulp.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/ulp.c

Implements gdtoa internal `ulp(U *x)` for doubles.

Behavior:
- Computes the unit in the last place for the magnitude/exponent of `x`.
- Uses `word0`, `word1`, `Exp_mask`, `P`, `Exp_msk1`, and related gdtoa macros from `gdtoaimp.h`.
- Handles gradual underflow unless `Sudden_Underflow` is defined.
- Has IBM-format conditional exponent adjustment.

Role: low-level floating-point spacing helper used by gdtoa conversion algorithms.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gdtoa/ulp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gmon/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gmon/Makefile.inc

libc build fragment for profiling support.

Adds:
- Source files: `gmon.c`, `mcount.c`.
- Manpage: `moncontrol.3`, linked as `monstartup.3`.
- Architecture search path `${ARCHDIR}/gmon`.

Special cases:
- MIPS disables assembler warnings for `mcount.c`.
- i386 suppresses a lint diagnostic for `_mcount`.
- i386/x86_64 with GCC >= 6 and clang suppress frame-address warnings.
- `mcount.po` and `gmon.po` are copied from non-profiled object variants because profiling code itself cannot be compiled with profiling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gmon/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gmon/gmon.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/gmon/gmon.c

NetBSD libc implementation of `monstartup`, `moncontrol`, and `_mcleanup` for `gprof` profiling output.

Key behavior:
- `monstartup(lowpc, highpc)` rounds text bounds, sizes histogram/from/to arc tables, allocates them with `sbrk`/`brk`, initializes profiling, and starts `profil(2)`.
- `_mcleanup()` stops profiling, determines profiling clock rate with `sysctl(KERN_CLOCKRATE)` or fallback `hertz()`, opens `gmon.out` or `$PROFDIR/<pid>.<progname>`, writes the `gmonhdr`, histogram, and raw call arcs.
- Refuses to write profiling output for setuid/setgid mismatch cases.
- `moncontrol(mode)` starts/stops kernel profiling via `profil`.

Threaded mode:
- `_REENTRANT` builds maintain per-thread `struct gmonparam` instances using thread-specific data.
- `_m_gmon_alloc()` mmaps per-thread arc storage.
- `_m_gmon_destructor()` moves thread data to a free list.
- `_m_gmon_merge()` merges per-thread arcs into the global profile before writing.

Dependencies: `<sys/gmon.h>`, `profil`, `sysctl`, `mmap`, `reentrant.h`, `extern.h` for `__minbrk`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/gmon/gmon.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/hash/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/hash/Makefile.inc

Top-level libc hash build fragment.

Adds:
- Source `hmac.c`.
- Manpage `hmac.3`.
- Includes subdirectory build fragments for MD2, RMD160, SHA1, SHA2, SHA3, and MurmurHash.

Role: aggregates hash algorithm sources into libc.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/hash/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/hash/hashhl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/hash/hashhl.c

Generic high-level digest helper template, compiled by defining `HASH_ALGORITHM` and `HASH_INCLUDE`.

Generated APIs include:
- `<ALG>End`
- `<ALG>FileChunk`
- `<ALG>File`
- `<ALG>Data`

Behavior:
- `End` finalizes binary digest and hex-encodes it, allocating output if `buf == NULL`.
- `FileChunk` opens a file with `O_CLOEXEC`, optionally seeks, reads chunks, and updates the hash context.
- `File` hashes the whole file.
- `Data` hashes an in-memory buffer.

It uses macro name construction for algorithm-specific context, length, and function prefixes, plus weak aliases outside tool builds.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/hash/hashhl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/hash/hmac.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/hash/hmac.c

Implements generic `hmac(name, key, klen, text, tlen, digest, dlen)` dispatching by algorithm name.

Supported algorithms:
`md2`, `md4`, `md5`, `rmd160`, `sha1`, `sha224`, `sha256`, `sha384`, `sha512`.

Behavior:
- Looks up algorithm metadata: context size, digest size, block size, init/update/final callbacks.
- If the key is longer than the hash block size, hashes it first.
- Builds HMAC ipad/opad buffers of fixed `HMAC_SIZE` 128 bytes.
- Computes inner hash over `ipad || text`, then outer hash over `opad || inner_digest`.
- Returns full digest size, or `-1` for unknown algorithm.

Notable implementation risk: the short-output path uses a temporary buffer when `dlen < digsize`, but the outer update reads from `digest` rather than the temporary inner digest buffer, which is suspicious for truncated output callers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/hash/hmac.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/hash/md2/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/hash/md2/Makefile.inc

Build fragment for MD2 support.

Adds:
- Path `${.CURDIR}/hash/md2`.
- Sources `md2.c` and `md2hl.c`.
- Manpage `md2.3`.
- Manpage links for `MD2Init`, `MD2Update`, `MD2Final`, `MD2End`, `MD2File`, `MD2Data`, `MD2Transform`, and `MD2FileChunk`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/hash/md2/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/hash/md2/md2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/hash/md2/md2.c

MD2 implementation derived from RFC 1319, compiled only when `HAVE_MD2_H` is false.

Main APIs:
- `MD2Init`
- `MD2Update`
- `MD2Final`
- `MD2Transform`

Core data:
- RFC 1319 substitution table `S[256]`.
- Padding table for 1..16 byte MD2 padding.

Behavior:
- `MD2Transform` updates checksum and mangles the 48-byte internal block state.
- `MD2Update` appends input into context block space and transforms full blocks.
- `MD2Final` pads, appends checksum, copies 16-byte digest, and resets context.
- Weak aliases expose public names to internal underscored implementations.

Dependencies: `<md2.h>`, `namespace.h`, optional `nbtool_config.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/hash/md2/md2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/hash/md2/md2hl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/hash/md2/md2hl.c

MD2 instantiation of the generic high-level hash helper.

Defines:
- `HASH_ALGORITHM MD2`
- `HASH_INCLUDE <md2.h>`

Then includes `../hashhl.c`, generating `MD2End`, `MD2FileChunk`, `MD2File`, and `MD2Data`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/hash/md2/md2hl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/hash/murmurhash/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/hash/murmurhash/Makefile.inc

Build fragment for MurmurHash support.

Adds:
- Path `${.CURDIR}/hash/murmurhash`.
- Source `murmurhash.c`.

No manpage entries are declared in this fragment.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/hash/murmurhash/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/hash/rmd160/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/hash/rmd160/Makefile.inc

Build fragment for RIPEMD-160 support.

Adds:
- Path `${.CURDIR}/hash/rmd160`.
- Sources `rmd160.c`, `rmd160hl.c`.
- Manpage `rmd160.3`.
- Manpage links for init/update/final/transform/end/file/data APIs.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/hash/rmd160/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/hash/rmd160/rmd160hl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/hash/rmd160/rmd160hl.c

RIPEMD-160 instantiation of `hashhl.c`.

Defines:
- `HASH_ALGORITHM RMD160`
- `HASH_INCLUDE <sys/rmd160.h>`

Generates high-level hex/file/data helpers for RMD160.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/hash/rmd160/rmd160hl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/hash/sha1/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/hash/sha1/Makefile.inc

Build fragment for SHA1 support.

Adds:
- Path `${.CURDIR}/hash/sha1`.
- Sources `sha1.c`, `sha1hl.c`.
- Manpage `sha1.3`.
- Manpage links for `SHA1Init`, `SHA1Update`, `SHA1Final`, high-level helpers, and `SHA1Transform`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/hash/sha1/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/hash/sha1/sha1hl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/hash/sha1/sha1hl.c

SHA1 instantiation of `hashhl.c`.

Defines:
- `HASH_ALGORITHM SHA1`
- `HASH_INCLUDE <sha1.h>`

Generates `SHA1End`, `SHA1FileChunk`, `SHA1File`, and `SHA1Data`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/hash/sha1/sha1hl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/hash/sha2/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/hash/sha2/Makefile.inc

Build fragment for SHA2 support.

Adds:
- Path `${.CURDIR}/hash/sha2`.
- Sources `sha2.c`, `sha224hl.c`, `sha256hl.c`, `sha384hl.c`, `sha512hl.c`.
- Manpage `sha2.3`.
- Extensive manpage links for SHA224/SHA256/SHA384/SHA512 init, update, final, end, file, data, transform, and file chunk helpers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/hash/sha2/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/hash/sha2/sha224hl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/hash/sha2/sha224hl.c

SHA224 instantiation of `hashhl.c`.

Defines:
- `HASH_ALGORITHM SHA224`
- `HASH_FNPREFIX SHA224_`
- `HASH_INCLUDE <sys/sha2.h>`

Generates underscore-suffixed SHA224 high-level helper names matching the SHA2 API style.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/hash/sha2/sha224hl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/hash/sha2/sha256hl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/hash/sha2/sha256hl.c

SHA256 instantiation of `hashhl.c`.

Defines:
- `HASH_ALGORITHM SHA256`
- `HASH_FNPREFIX SHA256_`
- `HASH_INCLUDE <sys/sha2.h>`

Generates high-level SHA256 hex/file/data helpers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/hash/sha2/sha256hl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/hash/sha2/sha384hl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/hash/sha2/sha384hl.c

SHA384 instantiation of `hashhl.c`.

Defines:
- `HASH_ALGORITHM SHA384`
- `HASH_FNPREFIX SHA384_`
- `HASH_INCLUDE <sys/sha2.h>`

Generates high-level SHA384 digest helpers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/hash/sha2/sha384hl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/hash/sha2/sha512hl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/hash/sha2/sha512hl.c

SHA512 instantiation of `hashhl.c`.

Defines:
- `HASH_ALGORITHM SHA512`
- `HASH_FNPREFIX SHA512_`
- `HASH_INCLUDE <sys/sha2.h>`

Generates high-level SHA512 digest helpers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/hash/sha2/sha512hl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/hash/sha3/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/hash/sha3/Makefile.inc

Build fragment for SHA3/Keccak support.

Adds:
- Path `${.CURDIR}/hash/sha3`.
- Sources `keccak.c`, `sha3.c`.

Manpage and MLINK entries are present but commented with `XXX not (yet) public`, indicating the implementation is built but not exposed as public documented API here.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/hash/sha3/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/iconv/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/iconv/Makefile.inc

Build fragment for libc iconv support.

Adds:
- Path `${ARCHDIR}/iconv ${.CURDIR}/iconv`.
- Source `iconv.c`.
- Manpage `iconv.3` with links for `iconv_open.3` and `iconv_close.3`.
- Extra include path `-I${LIBCDIR}/citrus` for Citrus conversion internals.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/iconv/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/iconv/iconv.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/iconv/iconv.c

Public libc `iconv` wrapper around Citrus conversion internals.

APIs:
- `iconv_open(out, in)`
- `iconv_close(handle)`
- `iconv(handle, in, szin, out, szout)`
- NetBSD extensions `__iconv`, `__iconv_get_list`, `__iconv_free_list`

Behavior:
- `iconv_open` calls `_citrus_iconv_open(&handle, _PATH_ICONV, in, out)` and maps missing conversion data to `EINVAL`.
- `iconv_close` rejects null or `(iconv_t)-1` handles with `EBADF`.
- `iconv` and `__iconv` call `_citrus_iconv_convert`; `__iconv` accepts flags and optionally reports invalid count.
- List helpers delegate to Citrus ESDB list routines.

Dependencies: Citrus modules, `namespace.h`, weak aliases for public names.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/iconv/iconv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/include/__sysctl.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/include/__sysctl.h

Private libc declaration for raw `__sysctl`.

Purpose:
- Declares syscall stub `int __sysctl(const int *, unsigned, void *, size_t *, const void *, size_t);`.
- Notes it bypasses higher-level library wrapper handling such as `user.*` nodes.
- Used by the sysctl wrapper, stack protector setup for `kern.arandom`, and runtime linker ld.so.conf interpretation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/include/__sysctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/include/arc4random.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/include/arc4random.h

Private libc header for `arc4random` global and per-thread state.

Defines:
- `struct crypto_prng` with 32-byte state.
- `struct arc4random_prng` with PRNG state and epoch.
- `struct arc4random_global_state` with mutex, thread key, global PRNG, once control, and flags for initialization, fork safety, and per-thread mode.
- `arc4random_global` macro remapped to private symbol `__arc4random_global`.

Depends on `reentrant.h` for mutex/thread/once types.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/include/arc4random.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/include/atexit.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/include/atexit.h

Private libc declarations for C++ ABI and thread-local exit handlers.

Declares:
- `__cxa_atexit`
- `__cxa_finalize`
- `__cxa_thread_run_atexit`
- `__cxa_thread_atexit`

When `_LIBC` is defined, exposes hidden boolean `__cxa_thread_atexit_used`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/include/atexit.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/include/env.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/include/env.h

Private environment-management header.

Declares:
- `__getenvslot`
- `__findenvvar`
- `environ`

Threading:
- Under `_REENTRANT`, declares environment read/write/unlock helpers.
- Otherwise supplies inline no-op lock helpers returning true.

Used by libc environment functions to centralize slot lookup and locking behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/include/env.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/include/extern.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/include/extern.h

Private libc umbrella declarations for internal symbols used across libc.

Includes:
- Process/environment globals: `__minbrk`, `__sigintr`, `environ`.
- Internal wrappers: `__getcwd`, `__getlogin`, `__setlogin`, `__posix_fadvise50`, `__sysctl`.
- Error/string helpers: `_strerror_lr`, `__strerror`, `__strsignal`.
- gdtoa helpers: `__dtoa`, `__freedtoa`, conditionally `__hldtoa`, `__ldtoa`, plus `__hdtoa`.
- malloc fork hooks.
- context/signal trampoline helpers.

Also defines `WIDE_DOUBLE` when `long double` differs from `double`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/include/extern.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/include/fd_setsize.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/include/fd_setsize.h

Minimal compatibility header for BIND/ISC ports.

It only defines the include guard `_FD_SETSIZE_H` and comments that this is not where callers should increase `FD_SETSIZE`; it is a fallback when BIND ports do not specify their own.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/include/fd_setsize.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/include/futex_private.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/include/futex_private.h

Private libc futex syscall wrapper header.

Defines inline helpers:
- `__futex`
- `__futex_set_robust_list`
- `__futex_get_robust_list`

They call `_syscall` directly with `SYS___futex` and related syscall numbers, intentionally avoiding `namespace.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/include/futex_private.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/include/isc/assertions.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/include/isc/assertions.h

ISC assertion interface used by imported resolver/event code.

Defines:
- `assertion_type` enum: require, ensure, insist, invariant.
- `assertion_failure_callback`.
- Global callback `__assertion_failed`.
- `set_assertion_failure_callback` and `assertion_type_to_text`.

Macros:
- `REQUIRE`, `ENSURE`, `INSIST`, `INVARIANT` and `_ERR` variants.
- Check enablement is controlled by `CHECK_ALL`, `CHECK_NONE`, `_DIAGNOSTIC`, and Coverity.
- Disabled macros still evaluate conditions except lint-specific `INSIST`.

Failure path delegates to `__assertion_failed`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/include/isc/assertions.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/include/isc/dst.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/include/isc/dst.h

ISC DNS Security Tool style crypto/key API header, with names remapped to private libc symbols.

Defines:
- `DST_KEY` structure unless already provided.
- Extensive `#define` namespace remaps from `dst_*` to `__dst_*`.
- Key operations for init, algorithm checks, signing, verification, reading/writing keys, DNS KEY conversion, buffer conversion, generation, freeing, comparison, and signature sizing.
- DNS key constants, algorithm codes, flags, and error codes.

Role: private imported resolver/DNSSEC support interface.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/include/isc/dst.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/include/isc/eventlib.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/include/isc/eventlib.h

Public-style ISC eventlib interface imported into libc with private symbol remapping.

Defines opaque ID/context/event wrapper structs and callback types for:
- Connections
- File descriptor readiness
- Streams
- Timers
- Wait events

Provides:
- Byte-mask macros.
- Event flags such as `EV_READ`, `EV_WRITE`, `EV_EXCEPT`.
- Remapped APIs for context lifecycle, event dispatch, connect/listen, FD selection, stream read/write, timers, waits, and defers.

Uses legacy `__P` prototype compatibility when needed.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/include/isc/eventlib.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/include/isc/heap.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/include/isc/heap.h

ISC heap interface.

Defines:
- Callback types for priority comparison, index updates, and iteration.
- `struct heap_context` fields for array size, increment, heap size, heap array, and callbacks.
- Private-symbol remaps for heap operations.

APIs: `heap_new`, `heap_free`, `heap_insert`, `heap_delete`, `heap_increased`, `heap_decreased`, `heap_element`, `heap_for_each`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/include/isc/heap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/include/isc/list.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/include/isc/list.h

Macro-based intrusive doubly-linked list utilities from ISC.

Defines:
- `LIST(type)` and `LINK(type)` struct fragments.
- Initialization, linked-state, head/tail/empty accessors.
- Operations: `PREPEND`, `APPEND`, `UNLINK`, `INSERT_BEFORE`, `INSERT_AFTER`, `ENQUEUE`, `DEQUEUE`.

Uses `INSIST` assertions to catch misuse such as inserting already-linked elements or unlinking unlinked elements.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/include/isc/list.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/include/isc/memcluster.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/include/isc/memcluster.h

ISC memory-cluster allocation interface with private libc symbol remapping.

Defines:
- `meminit`, `memget`, `memput`, `memstats`, `memactive` mappings.
- Debug and record modes that pass `__FILE__` and `__LINE__` to specialized allocation functions.

Declares normal, debug, and record allocation/free functions plus stats and activity checks.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/include/isc/memcluster.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/include/namespace.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/include/namespace.h

Central libc namespace-protection header.

Purpose:
- Remaps public libc function/data names to internal underscored symbols so libc-internal calls cannot be interposed by application symbols.
- Under `__weak_alias`, implementations define the underscored symbol and expose the public name via weak alias.
- Includes broad coverage across hash, stdio, networking, resolver, RPC, pthread-adjacent wrappers, syscalls, locale, time, inet, iconv, dynamic loading, rb trees, and more.

Relevant to this group:
- Remaps hash APIs (`MD2*`, `RMD160*`, `SHA1*`, `SHA2*`, `SHA3*`).
- Remaps `iconv`, `iconv_open`, `iconv_close`.
- Remaps inet APIs such as `inet_ntop`, `inet_pton`, `inet_net_pton`, `inet_cidr_ntop`.
- Remaps `sysctl`, syscall wrappers, RPC locks, and resolver functions.

Also includes a project-specific `__learn_tree` remap to `___learn_tree`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/include/namespace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/include/pathnames.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/include/pathnames.h

Private libc pathname header currently defining `_PATH_BIN_RCMD`.

Behavior:
- If `RESCUEDIR` is defined, `_PATH_BIN_RCMD` is `RESCUEDIR "/rcmd"`.
- Otherwise `_PATH_BIN_RCMD` is `"/bin/rcmd"`.

Used for libc code that needs the rcmd helper path.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/include/pathnames.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/include/port_after.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/include/port_after.h

Small ISC porting macro header for safe string assembly.

Defines:
- `ADDC(C)`: appends one character to `dst`, NUL-terminates, and jumps to `emsgsize` if there is insufficient space.
- `ADDS(S)`: calls an appending expression, validates its length against remaining buffer, and advances index `t`.

Used by inet conversion routines for consistent `EMSGSIZE` handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/include/port_after.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/include/port_before.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/include/port_before.h

ISC porting pre-include header.

Provides:
- `namespace.h` inclusion.
- `ISC_FORMAT_PRINTF(a,b)` mapped to compiler printf-format attribute.
- `ISC_SOCKLEN_T socklen_t`.
- `DE_CONST(c,v)` using `__UNCONST` on NetBSD or a portable strchr trick otherwise.
- `UNUSED(a)` macro, with lint-specific behavior.

Used before imported ISC source includes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/include/port_before.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/include/reentrant.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/include/reentrant.h

Private libc abstraction layer for thread-aware code.

Design:
- Maps libc-internal mutex, condition variable, rwlock, TSD, thread, and once types to pthread types.
- Under `_REENTRANT`, maps operations to `__libc_*` dispatch functions, which are weak-stubbed in libc and strongly supplied by pthreads when linked.
- Under non-`_REENTRANT`, most operations compile to no-ops, while `thr_once` performs a simple one-time call using `pto_done`.

Important exports:
- `mutex_t`, `cond_t`, `rwlock_t`, `thread_key_t`, `once_t`.
- `mutex_lock`, `cond_wait`, `rwlock_*`, `thr_keycreate`, `thr_setspecific`, `thr_once`, `thr_enabled`, `thr_curcpu`.
- `FLOCKFILE`/`FUNLOCKFILE` internal stdio locking macros.

Used by files such as `gmon.c`, `arc4random.h`, and environment locking code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/include/reentrant.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/include/resolv_mt.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/include/resolv_mt.h

Resolver multi-threading private context header.

Defines:
- `__res_enable_mt` and `__res_disable_mt`.
- `mtctxres_t`, a per-thread resolver context containing private flags and buffers formerly implemented as statics.
- `___mtctxres()` accessor and `mtctxres` macro.
- Macros mapping resolver static buffers like `inet_nsap_ntoa_tmpbuf`, `p_option_nbuf`, and `loc_ntoa_tmpbuf` to fields in the per-thread context.

Used by resolver and NSAP conversion code to avoid shared static buffers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/include/resolv_mt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/include/tsd.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/include/tsd.h

Private libc thread-specific data storage definition.

Defines:
- `TSD_KEYS_MAX 64`.
- `struct __libc_tsd` with value pointer, destructor, and in-use flag.
- External array `__libc_tsd[TSD_KEYS_MAX]`.

Used by libc thread-stub/TSD machinery.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/include/tsd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/inet/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/inet/Makefile.inc

Build fragment for inet address conversion sources.

Adds source files:
`inet_addr.c`, `inet_cidr_ntop.c`, `inet_cidr_pton.c`, `inet_lnaof.c`, `inet_makeaddr.c`, `inet_net_ntop.c`, `inet_net_pton.c`, `inet_neta.c`, `inet_netof.c`, `inet_network.c`, `inet_ntoa.c`, `inet_ntop.c`, `inet_pton.c`, `nsap_addr.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/inet/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/inet/inet_cidr_ntop.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/inet/inet_cidr_ntop.c

Implements `inet_cidr_ntop`, converting IPv4/IPv6 binary addresses plus prefix length to CIDR presentation format.

Behavior:
- Dispatches on `AF_INET` and `AF_INET6`; unsupported families set `EAFNOSUPPORT`.
- IPv4 accepts bits `-1..32`; `-1` suppresses `/bits`.
- IPv6 accepts bits `-1..128`, compresses longest zero run, and supports embedded IPv4 rendering.
- Uses `ADDC`/`ADDS` macros for checked appends; buffer overflow sets `EMSGSIZE`.
- Unlike `inet_net_ntop`, it may preserve nonzero host parts because CIDR host addresses are allowed.

Dependencies: `port_before.h`, `port_after.h`, `namespace.h`, inet/nameser headers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/inet/inet_cidr_ntop.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/inet/inet_cidr_pton.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/inet/inet_cidr_pton.c

Implements `inet_cidr_pton`, parsing IPv4/IPv6 CIDR presentation strings into binary address plus prefix length.

Behavior:
- Dispatches by address family.
- IPv4 parser accepts dotted decimal octets and optional `/bits`; defaults to `/32` only when all four octets are specified.
- IPv6 parser handles `::`, hex words, embedded IPv4, and optional `/bits`.
- `getbits` rejects empty values, leading zeros, and out-of-range widths.
- Returns `0` on success and `-1` with `ENOENT`, `EMSGSIZE`, or `EAFNOSUPPORT` on failure.

Notable: IPv6 parser stores `bits = -1` if no prefix was supplied; callers receive that value.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/inet/inet_cidr_pton.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/inet/inet_lnaof.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/inet/inet_lnaof.c

Implements legacy `inet_lnaof`.

Behavior:
- Converts IPv4 address to host byte order.
- Returns the local host-address portion using class A/B/C masks.
- Uses `IN_CLASSA`, `IN_CLASSB`, and class host masks.

This is classful IPv4 compatibility logic.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/inet/inet_lnaof.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/inet/inet_makeaddr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/inet/inet_makeaddr.c

Implements legacy `inet_makeaddr(net, host)`.

Behavior:
- Builds an IPv4 address from network and host portions using classful thresholds.
- Uses class A/B/C shifts and host masks when `net` fits those classes.
- Otherwise ORs `net | host`.
- Returns network-byte-order `struct in_addr`.

Compatibility helper for older classful networking APIs.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/inet/inet_makeaddr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/inet/inet_net_ntop.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/inet/inet_net_ntop.c

Implements `inet_net_ntop`, converting network numbers to CIDR presentation format.

Behavior:
- IPv4 validates bits `0..32`, prints whole octets and masked partial octet, always appending `/bits`.
- IPv6 validates bits `0..128`, zeroes host bits in a private buffer, compresses zero runs, detects IPv4-mapped/compatible forms, and appends `/bits`.
- Unsupported families set `EAFNOSUPPORT`; bad buffer space sets `EMSGSIZE`.

Difference from `inet_cidr_ntop`: this represents network numbers and masks/omits host bits.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/inet/inet_net_ntop.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/inet/inet_net_pton.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/inet/inet_net_pton.c

Implements `inet_net_pton`, parsing IPv4/IPv6 network numbers and returning prefix length.

IPv4 behavior:
- Accepts hex strings (`0x...`), decimal dotted forms, and optional `/CIDR`.
- Infers classful prefix length when CIDR is absent.
- Extends the destination with zero bytes up to the inferred/specified mask.
- Returns prefix length, or `-1` with `ENOENT`/`EMSGSIZE`.

IPv6 behavior:
- Handles `::`, hex words, optional embedded IPv4, and `/bits`.
- Defaults missing bits to `/128`.
- Copies only the number of bytes needed for the prefix.
- Requires the parsed address shape to match the prefix-derived word count.

Unsupported families set `EAFNOSUPPORT`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/inet/inet_net_pton.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/inet/inet_neta.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/inet/inet_neta.c

Implements `inet_neta`, formatting a `u_long` network number into dotted presentation format.

Behavior:
- Special-cases zero as `"0.0.0.0"`.
- Emits significant high-order bytes separated by dots.
- Uses `snprintf` and explicit buffer-end checks.
- Returns `NULL` with `EMSGSIZE` if output does not fit.

Input format expectations match `inet_network`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/inet/inet_neta.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/inet/inet_netof.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/inet/inet_netof.c

Implements legacy `inet_netof`.

Behavior:
- Converts IPv4 address to host byte order.
- Returns classful network number for class A, B, or C using class masks and shifts.

Compatibility API for pre-CIDR IPv4 code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/inet/inet_netof.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/inet/inet_network.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/inet/inet_network.c

Implements `inet_network`, parsing an Internet network number.

Behavior:
- Supports decimal, octal (`0` prefix), and hex (`0x`) numeric components.
- Parses up to four dot-separated byte components.
- Rejects invalid digits, too many parts, component values over `0xff`, and trailing non-space characters.
- Packs parsed components into a host-order network number.
- Returns `INADDR_NONE` on parse failure.

This is legacy classful IPv4 parsing, not modern CIDR parsing.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/inet/inet_network.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/inet/inet_ntoa.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/inet/inet_ntoa.c

Implements legacy `inet_ntoa`.

Behavior:
- Uses a static 18-byte buffer initialized to `"[inet_ntoa error]"`.
- Calls `inet_ntop(AF_INET, &in, ret, sizeof ret)` to produce dotted decimal output.
- Returns the static buffer.

Not thread-safe due to static storage, matching traditional `inet_ntoa` semantics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/inet/inet_ntoa.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/inet/inet_ntop.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/inet/inet_ntop.c

Implements standard `inet_ntop`.

Behavior:
- Dispatches `AF_INET` to `inet_ntop4` and `AF_INET6` to `inet_ntop6`.
- IPv4 formats `a.b.c.d` with `snprintf`, returning `ENOSPC` if too small.
- IPv6 converts bytes to 16-bit words, finds the longest zero run for `::`, handles embedded IPv4, and checks output buffer size before copying.
- Unsupported families set `EAFNOSUPPORT`.

Does not use static storage; caller supplies output buffer.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/inet/inet_ntop.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/inet/inet_pton.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/inet/inet_pton.c

Implements standard `inet_pton`.

Behavior:
- Dispatches by address family; unsupported families set `EAFNOSUPPORT`.
- IPv4 parser has a `pton` flag: strict `inet_pton` mode requires decimal dotted-quad only, though the helper can also support legacy hex/octal/shorthand for other callers.
- IPv6 parser handles hex words, `::`, and embedded IPv4 dotted-quad.
- On invalid presentation format returns `0` without touching destination; on unsupported family returns `-1`.

Uses ISC-derived parser logic and asserts non-null input/output.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/inet/inet_pton.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/inet/nsap_addr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/inet/nsap_addr.c

Implements NSAP address conversion helpers.

APIs:
- `inet_nsap_addr(ascii, binary, maxlen)`
- `inet_nsap_ntoa(binlen, binary, ascii)`

Behavior:
- `inet_nsap_addr` requires `0x`/`0X` prefix, ignores `.`, `+`, and `/`, parses hex pairs into binary, and returns byte length or `0` on failure.
- `inet_nsap_ntoa` emits `0x` followed by uppercase hex pairs, inserting dots after every two bytes; uses caller buffer or resolver thread-local `inet_nsap_ntoa_tmpbuf`.
- Caps output conversion at 255 input bytes.

Depends on `resolv_mt.h` for thread-specific fallback buffer.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/inet/nsap_addr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/isc/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/isc/Makefile.inc

Build fragment for imported ISC support code.

Adds:
- Path `${.CURDIR}/isc`.
- Sources `assertions.c`, `ev_timers.c`, and `ev_streams.c`.

These support resolver/eventlib functionality inside libc.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/isc/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/isc/assertions.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/isc/assertions.c

Implementation of the ISC assertion callback mechanism.

Exports:
- Global `assertion_failure_callback __assertion_failed`, defaulting to `default_assertion_failed`.
- `set_assertion_failure_callback`.
- `assertion_type_to_text`.

Default failure behavior:
- Prints `file:line: TYPE(condition)` to stderr.
- Appends `strerror(errno)` for `_ERR` assertion forms.
- Calls `abort()`.

Used by assertion macros in `isc/assertions.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/isc/assertions.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/isc/ev_streams.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/isc/ev_streams.c

ISC eventlib asynchronous stream I/O implementation.

Always-built helper:
- `evConsIovec(buf, cnt)` returns a populated `struct iovec`.

Most stream implementation is excluded when `_LIBC` is defined:
- `evWrite` and `evRead` allocate an `evStream`, register FD readiness callbacks, copy the caller iovec array, and link the stream into the event context.
- `evTimeRW`/`evUntimeRW` attach or detach idle timer handling.
- `evCancelRW` unlinks streams from active and done lists, deselects FDs, frees copied iovecs, and releases the stream.
- `copyvec`, `consume`, `done`, `writable`, and `readable` implement scatter/gather progress tracking and completion notification.

Dependencies: `eventlib_p.h`, `isc/eventlib.h`, `isc/assertions.h`, `fd_setsize.h`, memory-cluster allocation helpers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/isc/ev_streams.c -->