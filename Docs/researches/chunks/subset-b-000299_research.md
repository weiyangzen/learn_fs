# sources/compression/zlib/crc32.h lines 1-4186

## Scope And Purpose

This chunk covers the beginning of zlib's generated `crc32.h` table header. The header is not a public API header and does not define callable functions. It is generated automatically by `sources/compression/zlib/crc32.c` when `MAKECRCH` is enabled, then included by `crc32.c` when `DYNAMIC_CRC_TABLE` is not defined. Its purpose is to provide precomputed lookup tables for fast CRC-32 calculation without generating them at runtime.

The covered range contains the base 256-entry byte CRC table, the word-width big-endian helper table for `W == 8` and `W == 4`, all generated braid tables for `N == 1` and `N == 2`, and the beginning of the `N == 3`, `W == 8` tables. The chunk ends in the middle of the `N == 3`, `W == 8` `crc_braid_big_table`, so the final per-file report must reconcile this with later chunks before describing the full header.

These constants support zlib's `crc32_z()`, `crc32()`, `crc32_combine*()`, and `get_crc_table()` behavior indirectly through `crc32.c`. For normal static-table builds, this header avoids first-use table construction and avoids the thread-safety caveat that applies to `DYNAMIC_CRC_TABLE`.

## Important APIs, Types, And Tables

`crc_table[]` is a `local const z_crc_t FAR` array of 256 entries. It is the canonical reflected CRC-32 byte lookup table for polynomial `0xedb88320`. It is used for byte-at-a-time processing, alignment prologues, trailing-byte processing, and the `crc_word()` helper in `crc32.c`. The first table starts with the standard CRC-32 values `0x00000000`, `0x77073096`, `0xee0e612c`, and so on.

`crc_big_table[]` is present only under `#ifdef W`. The chunk contains two mutually exclusive definitions:

- `#if W == 8`: 256 `z_word_t` entries with 64-bit, high-positioned byte-swapped CRC values, used by big-endian braided processing when `z_word_t` is 64 bits.
- `#else /* W == 4 */`: 256 `z_word_t` entries with 32-bit high-order swapped values, used by the same big-endian path when `z_word_t` is 32 bits.

`crc_braid_table[][256]` is a `local const z_crc_t FAR` two-dimensional table selected by `N` and `W`. For each compiled braid configuration, it maps each byte position in a word to the corresponding sparse CRC contribution. `crc32_z()` indexes it as `crc_braid_table[k][(word >> (k << 3)) & 0xff]` in the little-endian braided path.

`crc_braid_big_table[][256]` is the big-endian counterpart with `z_word_t` entries. `crc32_z()` indexes it in the big-endian braided path as `crc_braid_big_table[k][...]`, and `crc_word_big()` also depends on `crc_big_table[]` to fold words while combining braids.

For `N == 1`, this chunk includes both `W == 8` and `W == 4` branches. The `W == 8` branch provides eight rows for `crc_braid_table` and eight rows for `crc_braid_big_table`; the `W == 4` branch provides four rows for each table. For `N == 2`, it similarly includes the complete `W == 8` and `W == 4` branches. For `N == 3`, it includes the `W == 8` branch header, all visible rows of the little-endian `crc_braid_table`, and only the first part of the big-endian `crc_braid_big_table`.

The symbols use zlib's internal portability macros and typedefs from `zutil.h`/`zconf.h`: `local` for internal linkage, `FAR` for segmented-memory compatibility, `z_crc_t` for at-least-32-bit CRC words, and `z_word_t` for the selected 32-bit or 64-bit word type.

## Control Flow And Runtime Use

There is no executable control flow inside this header beyond preprocessor selection. The control flow is compile-time:

1. `crc32.c` defines `N`, usually `5` unless `Z_TESTN` is set, and validates it is in `1..6`.
2. `crc32.c` defines or undefines `W`, usually `8` on `__x86_64__` and `__aarch64__`, otherwise `4` when `Z_U4` exists. If no suitable word type exists, `W` is undefined and braided tables are not compiled.
3. In static-table builds, `crc32.c` includes `crc32.h`.
4. The preprocessor selects exactly one `N` branch and one `W` branch for the braid tables. Unselected generated tables are discarded by preprocessing.

At runtime, `crc32_z()` first handles null buffers, preconditions the input CRC, and then uses the braided path only when `W` is defined and the buffer is long enough: `len >= N * W + W - 1`. It consumes unaligned leading bytes through `crc_table[]`, processes aligned blocks through the selected braid tables, combines per-braid CRCs with `crc_word()` or `crc_word_big()`, then processes remaining bytes through `crc_table[]`.

For little-endian execution, `crc32_z()` uses `crc_braid_table` and combines through `crc_word()`, which repeatedly indexes `crc_table[]`. For big-endian execution, it uses `crc_braid_big_table`, `crc_big_table[]`, and byte-swapping. Endianness is checked at runtime because ARM processors can change endianness at execution time.

When `DYNAMIC_CRC_TABLE` is enabled, the static arrays in this header are not included. Instead, `make_crc_table()` in `crc32.c` fills mutable arrays with the same values, including braid tables through the `braid()` generator. The comments in `crc32.c` warn that dynamic table generation has first-use threading constraints unless callers initialize with `get_crc_table()` before concurrent CRC use.

## State And Persistence Behavior

This chunk defines read-only static data. In static-table builds, the tables live in the compiled binary's read-only data segment and are shared by all CRC calls. They have no mutable state, no allocation behavior, no I/O, and no persistence side effects.

The closest persistence behavior is build-time: the table contents are generated and written to `crc32.h` by compiling `crc32.c` with `MAKECRCH`. The generator writes both 64-bit and 32-bit `W` variants for every supported `N` value so one header can serve multiple target configurations. The checked-in header is therefore a generated artifact whose contents must stay in sync with the generator, polynomial, braid algorithm, table writer formatting, and `N` range.

Because the table arrays are `local const`, their linkage and storage are intentionally private to the translation unit that includes `crc32.h`. Public callers do not observe the table objects directly except through `get_crc_table()`, which returns a pointer to `crc_table`.

## Dependencies And Integration Points

The header depends on the including translation unit to have already defined the internal zlib macros and types it uses: `local`, `FAR`, `z_crc_t`, and, when `W` is active, `z_word_t`. It also depends on `N` and `W` being defined or undefined consistently with `crc32.c`'s expectations.

The direct integration point is `sources/compression/zlib/crc32.c`, which includes this header only for non-dynamic table builds. `crc32.c` supplies the generator (`make_crc_table()` plus `braid()`), the consumers (`crc32_z()`, `crc_word()`, `crc_word_big()`, and `get_crc_table()`), and the compile-time controls (`N`, `W`, `Z_TESTN`, `Z_TESTW`, `DYNAMIC_CRC_TABLE`, and `MAKECRCH`).

The public zlib integration point is `sources/compression/zlib/zlib.h`, which declares `get_crc_table()` and the CRC APIs. `sources/compression/zlib/zconf.h` may rename public symbols such as `get_crc_table` for prefixing. The table data also indirectly affects deflate/gzip consumers that rely on zlib CRC verification or checksum generation.

Architecture integration matters. `crc32.c` can bypass or augment these paths on some platforms, such as ARM CRC32 instruction support or s390x vector hooks in nearby code. This header remains the portable table-backed implementation for builds that compile the standard C braided or bytewise paths.

## Risks And Edge Cases

The header is generated, so manual edits are high risk. A single changed literal can silently corrupt CRC results for only one architecture/configuration branch, especially because most builds select just one `N`/`W` branch. Regeneration from `crc32.c` is the safer way to update the file.

The file contains many preprocessor branches with repeated symbol names. Only one selected branch may define `crc_braid_table` and `crc_braid_big_table`. Any mismatch between `N`, `W`, table dimensions, and the unrolled `crc32_z()` code can produce compile errors at best and incorrect indexing at worst.

This chunk boundary is itself a documentation risk: lines 1-4186 stop inside `#if N == 3` / `#if W == 8` / `crc_braid_big_table`. A reader must not treat this chunk as containing a complete syntactic unit for `N == 3`; later chunks carry the rest of that table, the `W == 4` branch, later `N` values, and the `x2n_table[]` combine table.

Static-table and dynamic-table builds must remain equivalent. Tests that only cover default static builds can miss regressions in `make_crc_table()` or `braid()`, while tests that only cover dynamic builds can miss checked-in table corruption.

Default `N` is `5`, so the `N == 1`, `N == 2`, and `N == 3` tables in this chunk are mostly exercised only by special builds using `Z_TESTN`. They still need coverage because zlib explicitly supports tuning `N` for benchmarking and target processors.

`W` selection depends on available integer typedefs and target macros. A 64-bit platform normally selects `W == 8`, but if `Z_U8` is unavailable it falls back to `W == 4` when possible. This makes both word-width branches relevant across ports.

The big-endian tables are easy to under-test on little-endian development machines. `crc32_z()` contains runtime endian detection, and big-endian behavior depends on `crc_big_table`, `crc_braid_big_table`, and `byte_swap()` agreeing.

The `FAR` macro and `local` linkage preserve old zlib portability assumptions. Changing these declarations to ordinary external data or removing qualifiers could alter ABI exposure, section placement, or memory-model compatibility.

## Test Signals

Known-answer CRC tests should cover empty input, null-buffer initialization, `"123456789"` with the standard CRC-32 result, short buffers below the braided threshold, unaligned buffers, aligned long buffers, and trailing lengths from 0 through at least `N * W + W`.

Build-matrix tests should compile static-table builds for multiple `Z_TESTN` values, at minimum `1`, `2`, `3`, and the default `5`, and for `Z_TESTW=4`, `Z_TESTW=8`, and disabled braided mode where supported. This chunk specifically needs `Z_TESTN=1`, `2`, and `3` to exercise the covered branches.

Dynamic-vs-static equivalence tests should run the same CRC vectors with and without `DYNAMIC_CRC_TABLE`. The static build consumes `crc32.h`; the dynamic build regenerates equivalent data through `make_crc_table()` and `braid()`.

Endian-sensitive tests should run on a big-endian target or emulator, or otherwise compare the big-endian path in a targeted harness, because this chunk includes both `crc_big_table[]` and `crc_braid_big_table[]`.

Generator tests should regenerate `crc32.h` with `MAKECRCH` and compare it against the checked-in file. Any diff in this chunk should be treated as a source change requiring explanation, because runtime CRC values depend directly on these literals.

Integration tests should verify `get_crc_table()` returns a table whose entries match expected CRC-32 byte-table values and that `crc32_combine*()` results agree with CRCs over concatenated buffers. The combine APIs also depend on later `x2n_table[]`, so final per-file validation should include chunks beyond this one.
