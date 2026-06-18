# sources/compression/zlib/crc32.h lines 8370-9446

## Scope And Purpose

This chunk covers the tail of zlib's generated CRC-32 lookup-table header. It starts in the middle of the `N == 6`, `W == 8` `crc_braid_big_table` initializer, continues through the `W == 4` little-endian and big-endian braid tables for `N == 6`, closes the nested preprocessor guards, and then defines the shared `x2n_table[]` powers table used for CRC combination.

The file is not an API header in the public zlib sense. It is included by `sources/compression/zlib/crc32.c` when `DYNAMIC_CRC_TABLE` is not enabled, providing precomputed read-only tables instead of building them at runtime. The tables support fast CRC-32 calculation over braided word streams and fast composition of two CRC values for concatenated byte sequences.

## Important APIs, Types, And Data

`crc_braid_big_table[][256]` is a generated `local const z_word_t FAR` array. In this chunk it appears twice under mutually exclusive preprocessor branches: first as part of the `N == 6`, `W == 8` big-endian word table, then as the complete `N == 6`, `W == 4` big-endian word table. Runtime code in `crc32.c` indexes it as `crc_braid_big_table[k][byte]`, where `k` is the byte position within a `z_word_t` and `byte` is extracted from the current word. Despite the `N == 6` block, the first dimension is driven by `W`: eight rows for 64-bit words and four rows for 32-bit words.

`crc_braid_table[][256]` is the corresponding `local const z_crc_t FAR` little-endian braid table for `N == 6`, `W == 4`. It is used by the little-endian braided CRC path in `crc32_z()`.

`x2n_table[]` is a `local const z_crc_t FAR` table with 32 entries of powers of `x` modulo the reflected CRC-32 polynomial. `crc32.c` uses it through `x2nmodp()` to implement `crc32_combine_gen64()`, `crc32_combine_gen()`, `crc32_combine64()`, `crc32_combine()`, and `crc32_combine_op()`.

The key supporting types and macros are supplied by `zutil.h` and surrounding `crc32.c`: `z_crc_t` for 32-bit CRC table entries, `z_word_t` for 32-bit or 64-bit word-at-a-time processing, `local` for internal linkage, and `FAR` for historical segmented-memory compatibility.

## Control Flow

There is no executable control flow inside this chunk; it is static initializer data selected at compile time. The effective control flow is preprocessor-driven:

- `#if N == 6` selects this generated braid-table block.
- `#if W == 8` selects the 64-bit-word tables; `#else /* W == 4 */` selects 32-bit-word tables.
- `#ifdef W` around the broader table region determines whether braided CRC support is compiled at all.

At runtime, `crc32_z()` in `crc32.c` decides whether the input is long enough for braided processing. For little-endian platforms it reads aligned words, XORs each word with the current braid CRC, then folds each byte position through `crc_braid_table[k][...]`. For big-endian platforms it uses `crc_braid_big_table[k][...]` and `crc_word_big()` to combine the per-braid results. With `N == 6`, the runtime code has six interleaved CRC accumulators (`crc0` through `crc5`) guarded by `#if N > 5`.

The `x2n_table[]` path is separate from data-stream CRC calculation. `crc32_combine_gen64(len2)` calls `x2nmodp(len2, 3)`, which walks bits of `len2` and repeatedly multiplies by entries from `x2n_table[k & 31]`. `crc32_combine_op()` then uses that operator to combine `crc1` and `crc2`.

## State And Persistence Behavior

All data in this chunk is compile-time constant and has internal linkage through `local const`. It should land in read-only program storage and is not mutated by zlib at runtime. There is no file, stream, heap, or global runtime state written by this chunk.

The persistence-relevant behavior is binary and ABI footprint: enabling static tables embeds these generated constants into every built library/object that includes this header through `crc32.c`. When `DYNAMIC_CRC_TABLE` is enabled, `crc32.c` instead declares mutable table storage and fills it once via `make_crc_table()`, so this header data is not used.

`x2n_table[]` is also immutable in the static-table build. In the dynamic-table build the same logical table is generated into a mutable `x2n_table[32]` before CRC combine operations can use it.

## Dependencies And Integration Points

The direct integration point is `sources/compression/zlib/crc32.c`, which includes `crc32.h` only in the non-dynamic-table path. `crc32.c` is also the generator for this file when compiled with `MAKECRCH`; its `make_crc_table()`, `braid()`, and `write_table*()` helpers produce the same tables.

The data depends on the CRC-32 reflected polynomial `0xedb88320`, the configured braid count `N`, and the configured word width `W`. `crc32.c` restricts `N` to `1..6`, chooses `W` from `Z_TESTW`, architecture defaults, or available integer types, and requires `z_word_t` to be 32 or 64 bits with eight-bit bytes.

Public zlib APIs that indirectly rely on this chunk include `crc32()`, `crc32_z()`, `crc32_combine()`, `crc32_combine64()`, `crc32_combine_gen()`, `crc32_combine_gen64()`, and `crc32_combine_op()`. Higher-level zlib code uses those APIs for gzip headers/trailers and stream checksums, including `deflate.c`, `inflate.c`, examples, and minizip code.

## Risks And Edge Cases

The largest risk is table correctness. A single incorrect constant in any braid table can produce wrong CRCs only for specific combinations of `N`, `W`, endianness, alignment, input length, and byte position, making failures look data-dependent and platform-specific.

The chunk begins inside an initializer, so local review must account for surrounding rows and braces. The opening declaration for the first table is above the requested range, and the closing preprocessor guards below the table determine which duplicate table names are actually compiled.

The `N == 6` tables are not the default path in stock `crc32.c` unless `Z_TESTN` overrides `N`; the default is `N == 5`. That lowers everyday coverage risk for these constants but also means regressions here can escape normal builds unless tests explicitly compile with `-DZ_TESTN=6`.

The `W == 4` and `W == 8` branches define identically named arrays under mutually exclusive preprocessor conditions. Any refactor that weakens those guards can create duplicate definitions or select tables with the wrong word width.

`x2n_table[]` has only 32 entries by design and is indexed with `k & 31` in `x2nmodp()`. This relies on the repeated-squaring construction of powers modulo the CRC polynomial; changing the table length or initialization algorithm must keep that wraparound contract intact.

Static-table builds avoid dynamic initialization races. Dynamic-table builds use `z_once()` in current `crc32.c`, but the file comments still warn that first-use generation historically needed care before concurrent `crc32()` calls. Tests should distinguish static table failures from dynamic generation failures.

## Test Signals

Compile-time coverage should include non-dynamic table builds with `-DZ_TESTN=6 -DZ_TESTW=4` and `-DZ_TESTN=6 -DZ_TESTW=8`, on both little-endian and big-endian targets where possible. Cross-compilation or emulator runs are useful because the big-endian path is the only runtime consumer of `crc_braid_big_table`.

Functional CRC tests should compare `crc32()` and `crc32_z()` against known vectors such as the empty buffer, `"123456789"`, short unaligned buffers, lengths just below and above `N * W + W - 1`, and long buffers with varied alignments. For this chunk, force `N == 6` so the six-braid paths and their tables are used.

Combine tests should verify `crc32_combine(crc32(A), crc32(B), len(B)) == crc32(A || B)` for empty, short, large, and very large `len2` values. Negative-length behavior should confirm `crc32_combine_gen64()` returns zero and `crc32_combine_op()` returns zero for operator zero.

Generation tests should rebuild `crc32.h` with `MAKECRCH` and compare the generated `N == 6` table sections and `x2n_table[]` against the checked-in file. This is the strongest signal that the constants match `crc32.c`'s generator logic.

Integration tests should run gzip/zlib round trips that exercise CRC validation in `deflate.c` and `inflate.c`, plus any minizip or example utilities that rely on `crc32_combine()` for concatenated members.
