# Research: sources/compression/zlib/crc32.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-000299`: lines 1-4186, `Docs/researches/chunks/subset-b-000299_research.md`
- `subset-b-000300`: lines 4187-8369, `Docs/researches/chunks/subset-b-000300_research.md`
- `subset-b-000301`: lines 8370-9446, `Docs/researches/chunks/subset-b-000301_research.md`

## Chunk Research

### subset-b-000299: lines 1-4186

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

### subset-b-000300: lines 4187-8369

# sources/compression/zlib/crc32.h lines 4187-8369

## Scope

This chunk covers the middle 4,183-line slice of zlib's generated CRC lookup table header. It begins inside the `N == 3`, `W == 8` `crc_braid_big_table`, then contains the complete `N == 3`/`W == 4`, `N == 4`/`W == 8`, `N == 4`/`W == 4`, `N == 5`/`W == 8`, and `N == 5`/`W == 4` braid-table blocks, and ends inside the first row of the `N == 6`, `W == 8` `crc_braid_big_table`.

The source is generated data consumed by `crc32.c`, not standalone executable logic. Its primary purpose is to provide compile-time constants for zlib's software braided CRC-32 implementation when `DYNAMIC_CRC_TABLE` is not enabled.

## Purpose

`crc32.h` stores precomputed CRC-32 tables generated by `crc32.c` when built with `MAKECRCH`. This chunk specifically supplies the braid lookup tables used to process multiple machine words in parallel. `crc32.c` chooses a braid count `N` from 1 through 6 and a word width `W` of 4 or 8 bytes. The active preprocessor branch exposes one pair of arrays:

- `crc_braid_table[][256]` for little-endian word processing, with `z_crc_t` 32-bit CRC remainders.
- `crc_braid_big_table[][256]` for big-endian word processing, with `z_word_t` values that have already been byte-swapped or high-word-positioned for the big-endian path.

The chunk is performance infrastructure. The tables let `crc32_z()` reduce each byte lane of a loaded word with XORs and indexed loads instead of recomputing polynomial arithmetic at runtime. For typical builds in `crc32.c`, `N` defaults to `5`; `W` defaults to `8` on x86_64 and aarch64 when a 64-bit type is available, otherwise `4`. That makes the complete `N == 5` blocks in this chunk especially important for default optimized software CRC builds.

## Important APIs, Types, And Data

There are no public functions or callables in this line range. The important exported-to-translation-unit symbols are local static-style constants included into `crc32.c`:

- `local const z_crc_t FAR crc_braid_table[][256]`: little-endian braid tables. For `W == 8`, each block contains eight 256-entry rows. For `W == 4`, each block contains four 256-entry rows.
- `local const z_word_t FAR crc_braid_big_table[][256]`: big-endian braid tables. For `W == 8`, entries are 64-bit-looking constants such as `0xa19017e800000000`. For `W == 4`, the generated file stores values in the high 32 bits of the available generation word and emits 32-bit constants in the `W == 4` branch.
- `z_crc_t`: zlib CRC integer type used for 32-bit table remainders.
- `z_word_t`: machine-word type selected in `crc32.c` from `Z_U8` when `W == 8`, or `Z_U4` when `W == 4`.
- `FAR` and `local`: zlib portability macros from `zutil.h`/configuration headers. In ordinary builds these keep the tables translation-unit local while preserving old memory-model compatibility.
- `N` and `W`: compile-time selectors around the table blocks. The chunk's conditional structure makes only one pair of braid tables visible for the selected combination.

The concrete table blocks visible in this chunk are:

- Tail of `#if N == 3` / `#if W == 8`: continuation of `crc_braid_big_table[][256]`, ending at the `#else /* W == 4 */` boundary.
- Complete `#if N == 3` / `W == 4`: `crc_braid_table[][256]` and `crc_braid_big_table[][256]`.
- Complete `#if N == 4` / `W == 8`: `crc_braid_table[][256]` and `crc_braid_big_table[][256]`.
- Complete `#if N == 4` / `W == 4`: `crc_braid_table[][256]` and `crc_braid_big_table[][256]`.
- Complete `#if N == 5` / `W == 8`: `crc_braid_table[][256]` and `crc_braid_big_table[][256]`.
- Complete `#if N == 5` / `W == 4`: `crc_braid_table[][256]` and `crc_braid_big_table[][256]`.
- Start of `#if N == 6` / `#if W == 8`: complete `crc_braid_table[][256]` and the opening of `crc_braid_big_table[][256]`.

## Control Flow

This chunk has no runtime branches of its own, but it participates in compile-time selection:

1. `crc32.c` defines `N`, normally `5` unless `Z_TESTN` overrides it, and rejects values outside `1..6`.
2. `crc32.c` defines `W` based on `Z_TESTW`, `MAKECRCH`, target architecture, and integer type availability. If no suitable word type exists, `W` is undefined and braided code is not compiled.
3. When `DYNAMIC_CRC_TABLE` is not defined, `crc32.c` includes `crc32.h`.
4. The preprocessor selects exactly one `#if N == ...` block and exactly one `#if W == 8` or `#else /* W == 4 */` branch within that block.
5. `crc32_z()` enters the braided path only for sufficiently long buffers, aligns the input pointer to a `z_word_t` boundary, splits processing into blocks of `N * W` bytes, and indexes these tables by byte positions in loaded words.
6. For little-endian execution, `crc32_z()` indexes `crc_braid_table[k][byte]` for each byte lane and XORs the lane results.
7. For big-endian execution, `crc32_z()` indexes `crc_braid_big_table[k][byte]`, then combines with `crc_word_big()` and `byte_swap()`.

The table contents themselves were generated by `braid()` in `crc32.c`: for each byte lane `k`, it computes `x2nmodp((n * w + 3 - k) << 3, 0)`, multiplies each possible byte value by that polynomial modulo the reflected CRC-32 polynomial, and writes either the little-endian remainder or a byte-swapped big-endian representation.

## State And Persistence Behavior

The data in this chunk is immutable read-only program state. In static-table builds, the arrays are compiled into the object file and shared by all CRC calls in the process. No runtime initialization, locking, mutation, file I/O, or persistence occurs in this header chunk.

The main state interaction is with `crc32_z()`'s transient local CRC accumulators. During braided processing, `crc32_z()` maintains one accumulator per braid (`crc0` through `crc5`, depending on `N`) and repeatedly refreshes them from the selected table rows. The tables do not remember progress across calls; the caller-provided CRC argument and buffer contents fully determine each result.

When `DYNAMIC_CRC_TABLE` is enabled, this generated header is not used for these arrays. Instead, `make_crc_table()` builds equivalent mutable arrays at runtime under `z_once()` coordination. The generated constants in this chunk therefore need to match the dynamic generation path exactly, or static and dynamic builds would produce divergent CRCs.

## Dependencies And Integration Points

This chunk depends on definitions supplied before including `crc32.h`:

- `zutil.h` provides `z_crc_t`, `Z_U4`, `Z_U8`, `FAR`, and the `local` macro environment used by `crc32.c`.
- `crc32.c` defines `N`, `W`, `z_word_t`, and the `DYNAMIC_CRC_TABLE` include policy.
- The constants depend on the reflected CRC-32 polynomial `0xedb88320` used by `make_crc_table()`, `multmodp()`, `x2nmodp()`, and `braid()`.

The direct consumer is `sources/compression/zlib/crc32.c`. Its integration points are:

- `crc32_z()`, the main CRC-32 update routine, which uses `crc_braid_table` and `crc_braid_big_table` in the optimized software path.
- `crc_word()` and `crc_word_big()`, which combine per-braid CRCs using `crc_table` or `crc_big_table` after table-driven block processing.
- `get_crc_table()`, which exposes the base byte table and can trigger dynamic initialization in non-static-table builds, though this chunk is relevant to the static include path.
- `MAKECRCH`, which regenerates `crc32.h`; any manual changes to this file would normally be overwritten by that generation mode.

The broader zlib public integration point is the API declared in `zlib.h`: `crc32_z()`, `crc32()`, `crc32_combine()`, `crc32_combine_gen()`, and related 64-bit variants. This chunk affects those APIs indirectly by determining the speed path and correctness of CRC updates for selected static-table builds.

## Risks And Edge Cases

The most important risk is silent data corruption from a single incorrect table entry. CRC tables are pure constants, so most compiler and sanitizer checks will not detect a bad value. A bad value might only appear for specific byte positions, buffer lengths, endian modes, `N`/`W` combinations, and alignment states.

This chunk begins and ends inside array initializers. Merge/reconciliation must preserve chunk boundaries carefully: line 4187 is part of an already-open `N == 3`, `W == 8` `crc_braid_big_table`, and line 8369 is part of the first row of the `N == 6`, `W == 8` `crc_braid_big_table`. A chunk-local parser that expects balanced declarations will see incomplete context at both ends.

The `N == 5` tables are high priority because they match zlib's default `N` in `crc32.c`. On common 64-bit little-endian platforms, the selected static branch is `N == 5`, `W == 8`, using the `crc_braid_table` block that starts in this chunk. On platforms where `W` falls back to 4, the `N == 5`, `W == 4` branch in this chunk becomes active instead.

The big-endian tables are easy to misread: `crc_braid_big_table` entries are not just the same 32-bit CRC values in a different textual format. They are generated through `byte_swap()` or high-word emission so that `crc32_z()`'s big-endian word path can use the same table-indexing structure while shifting in the opposite direction.

The array dimensions are intentionally declared with an inferred first dimension (`[][256]`). Compile-time row counts are therefore controlled entirely by initializer structure and preprocessor branch choice. A missing brace, misplaced comma, or row truncation can either break compilation or alter table shape in ways that only surface under a specific `N`/`W` build.

The `W == 4` and `W == 8` branches both appear in the same generated header. Tooling that counts or validates declarations must evaluate preprocessor conditions rather than treating repeated `crc_braid_table` declarations as duplicate definitions in one active translation unit.

Because the file is generated, manual edits are fragile. Any fix should normally be made in `crc32.c`'s generation logic or by regenerating `crc32.h` with `MAKECRCH`, then validating that the generated static tables match dynamic table generation.

## Test Signals

Useful verification for this chunk includes:

- Build zlib with static CRC tables for `Z_TESTN=3`, `4`, `5`, and `6`, with both `Z_TESTW=4` and `Z_TESTW=8` where the platform supports them. This exercises every complete or partial branch represented in the chunk.
- Compare `crc32_z()` results from static-table builds against `DYNAMIC_CRC_TABLE` builds over a broad corpus: empty buffers, one-byte through several-hundred-byte buffers, long buffers, random data, all-zero data, all-`0xff` data, and repeated patterns.
- Force unaligned input starts for every offset from `0` through `W - 1` so the byte-at-a-time alignment prefix and the braided block path combine correctly.
- Test lengths around braided thresholds: below `N * W + W - 1`, exactly at the threshold, one byte above, exactly one block, multiple blocks, and block-plus-tail lengths.
- Run on little-endian and big-endian targets or emulators. The little-endian path validates `crc_braid_table`; the big-endian path validates `crc_braid_big_table`.
- Regenerate `crc32.h` with `MAKECRCH` and diff the generated output against the checked-in file. For this chunk, expected differences should be zero unless the generator or polynomial logic intentionally changed.
- Use known CRC-32 vectors such as `"123456789"` yielding `0xcbf43926`, plus zlib's own test suite and any downstream compression/archive tests that verify checksums.
- For the later merge lane, verify that the three chunks for `sources/compression/zlib/crc32.h` reconstruct a syntactically balanced header and that all selected `N`/`W` branches compile without duplicate or missing table symbols.

### subset-b-000301: lines 8370-9446

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
