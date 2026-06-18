# Research: sources/distributed-fs/ceph-client/fs/nls/nls_cp936.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-005712`: lines 1-3984, `Docs/researches/chunks/subset-b-005712_research.md`
- `subset-b-005713`: lines 3985-8212, `Docs/researches/chunks/subset-b-005713_research.md`
- `subset-b-005714`: lines 8213-11112, `Docs/researches/chunks/subset-b-005714_research.md`

## Chunk Research

### subset-b-005712: lines 1-3984

# sources/distributed-fs/ceph-client/fs/nls/nls_cp936.c lines 1-3984

## Scope

This chunk covers the opening 3,984 lines of `sources/distributed-fs/ceph-client/fs/nls/nls_cp936.c`, a Linux kernel NLS module implementation for the Simplified Chinese CP936 / GB2312 character set. The assigned range starts with the module comment and kernel/NLS includes, then defines most of the CP936 byte-to-Unicode translation tables from lead byte `0x81` through the beginning of `0xF1`. It stops in the middle of `c2u_F1`; the later chunk continues the remaining `c2u_*` tables, the `page_charset2uni` dispatch table, Unicode-to-CP936 reverse tables, conversion functions, NLS registration, and module metadata.

## Purpose

The code in this range is generated lookup data. Its job is to map two-byte CP936 character sequences to Unicode `wchar_t` values for use by the kernel NLS subsystem. Filesystems and other kernel paths that need filename or text conversion for the `cp936` charset indirectly consume these constants through the NLS table registered later in the file.

This chunk does not implement executable conversion logic itself. It supplies the immutable `c2u_*` pages that later `char2uni()` indexes through `page_charset2uni[ch][cl]`, where `ch` is the CP936 lead byte and `cl` is the trailing byte.

## Important APIs, Types, and Data

- `#include <linux/module.h>`, `<linux/kernel.h>`, `<linux/string.h>`, `<linux/nls.h>`, and `<linux/errno.h>` establish that this file is a kernel module/NLS implementation. In this chunk, only `wchar_t` is directly visible in the data declarations, but later code uses `struct nls_table`, `module_init`, `module_exit`, and `-EINVAL` / `-ENAMETOOLONG`.
- `static const wchar_t c2u_81[256]` through `static const wchar_t c2u_F1[256]` are per-lead-byte CP936-to-Unicode pages. Each array has 256 slots so the second byte can be used directly as an index.
- `0x0000` entries are sentinel values for unmapped or invalid CP936 byte pairs. The downstream `char2uni()` path treats a looked-up `0x0000` as `-EINVAL`, except single-byte fallback handling is outside this chunk.
- Table comments such as `/* 0x40-0x47 */` document the low-byte range for each group of eight entries. These comments are important maintenance aids because this is otherwise dense generated data.

## Table Coverage and Shape

The table set begins at lead byte `0x81`, which is the first non-ASCII CP936 lead-byte page represented by this generated file. Many arrays have no valid entries for low-byte ranges `0x00-0x3F`, and most use `0x0000` at `0x7F`, matching the invalid CP936 trail-byte gap.

The early pages `c2u_81` through `c2u_A0` mostly map into CJK Unified Ideographs and related ranges in increasing Unicode order. `c2u_A1` through `c2u_A9` contain symbol, punctuation, width, kana, Greek, Cyrillic, phonetic, box drawing, and compatibility mappings, including full-width ASCII in `c2u_A3`, Hiragana in `c2u_A4`, Katakana in `c2u_A5`, Greek and vertical forms in `c2u_A6`, Cyrillic in `c2u_A7`, Bopomofo and box/block symbols in `c2u_A8`, and CJK/box drawing/compatibility forms in `c2u_A9`.

From `c2u_AA` onward the chunk alternates between extension ideograph ranges and GB2312-style common Simplified Chinese mappings. For example, `c2u_B0` starts with extended CJK values and then maps common words beginning with Unicode values such as `0x554A`, `0x963F`, `0x57C3`, and `0x6328`; subsequent pages continue the primary GB2312 order through Chinese lexical groups. Later pages in this chunk, including `c2u_D8` through `c2u_F0`, map additional radicals, compatibility ideographs, simplified forms, punctuation-adjacent blocks, radicals/components, and less common CJK ranges.

The assigned range ends after the first visible rows of `c2u_F1`, so `c2u_F1` is incomplete in this chunk. The merge lane should combine this report with the following chunk before deriving whole-file conclusions about complete lead-byte coverage.

## Control Flow

There is no runtime branch or loop in lines 1-3984. The effective control flow is table-driven and occurs later:

1. A caller invokes the file's registered NLS `char2uni()` callback.
2. `char2uni()` reads one or two bytes from the input byte string.
3. For a two-byte candidate, it takes the first byte as a page selector and obtains `page_charset2uni[ch]`.
4. If the page pointer is non-NULL and the trailing byte is nonzero, it reads `charset2uni[cl]`.
5. A `0x0000` table result is rejected as invalid; otherwise the Unicode code point is returned.

This chunk provides the page arrays used in step 4. It is therefore performance-critical in layout but behaviorally simple: correctness depends on byte-exact generated constants.

## State and Persistence

All data in this range is `static const`. It is compiled into the module or kernel image as read-only data and has no mutable state, no persistence, no allocation, no reference counting, and no cleanup requirement. The arrays are shared by all callers once the NLS module is loaded.

There are no locks because the data is immutable. The main state risk is not runtime mutation but static table corruption, truncation, or dispatch-table mismatch.

## Dependencies and Integration Points

- Depends on the kernel NLS contract from `<linux/nls.h>`, although the actual `struct nls_table` initializer is outside this chunk.
- Integrated later by `page_charset2uni[256]`, which maps byte values `0x81` onward to the corresponding `c2u_*` page pointers. The downstream scan shows this index references `c2u_81` through `c2u_FE`.
- Integrated by `char2uni()`, which relies on each page being exactly 256 `wchar_t` entries and on invalid pairs being encoded as `0x0000`.
- Integrated with reverse Unicode-to-CP936 conversion tables (`u2c_*`) later in the file. Those reverse tables should be consistent with the forward mappings here for round-trip behavior where CP936 supports a character.
- Exposed to filesystems through the registered NLS table named `"cp936"` with alias `"gb2312"` later in the file.

## Risks and Edge Cases

- Generated-table drift is the main risk. A single wrong constant silently converts filenames or text to the wrong Unicode character.
- Truncation or missing entries are high-impact. Since array indexing is direct, every `c2u_*` page must have exactly 256 elements. This chunk ends mid-table only because it is a research chunk; the source file itself must continue cleanly.
- `0x0000` is both a valid Unicode code point and the invalid-entry sentinel in two-byte pages. The later `char2uni()` path rejects two-byte mappings to zero, so these pages cannot represent NUL via a two-byte CP936 sequence.
- Lead-byte dispatch must stay aligned with table names. If `page_charset2uni[0xB0]` pointed at the wrong page, conversion would still be memory-safe but semantically broken.
- `wchar_t` size and signedness are kernel/platform concerns hidden behind NLS conventions. The constants in this range fit in the BMP, so they are safe for 16-bit or wider `wchar_t` representations used by the kernel build.
- Bound-length behavior is controlled outside this chunk. The tables assume the caller has already validated that a second byte is available before two-byte lookup.

## Test Signals

Useful validation for this chunk should be data-oriented:

- Compile the file/module to catch malformed initializers, incorrect array lengths, or incomplete declarations.
- Verify `page_charset2uni` later maps every visible page in this chunk to the same lead-byte suffix, especially `0x81` through the completed portion of `0xF1`.
- Spot-check known CP936 mappings against a trusted reference, including `B0 A1 -> U+554A`, `D2 BB -> U+4E00`, full-width ASCII from `A3 A1..A3 FE`, Hiragana/Katakana pages `A4`/`A5`, Greek `A6`, Cyrillic `A7`, and box drawing around `A9 A4`.
- Exercise invalid pairs such as low bytes below `0x40` and `0x7F` in these pages and expect `char2uni()` to return `-EINVAL` for two-byte lookups.
- Round-trip representative values through `char2uni()` and `uni2char()` once the reverse tables from later chunks are included.

## Unresolved Cross-Chunk References

- `c2u_F1` is incomplete at the end of this chunk; pages `c2u_F2` through `c2u_FE` are outside the assigned range.
- `page_charset2uni`, `u2c_*`, `page_uni2charset`, `charset2lower`, `charset2upper`, `uni2char()`, `char2uni()`, `struct nls_table table`, and module init/exit are outside this chunk and must be covered by later chunk reports before producing the final per-file research document.

### subset-b-005713: lines 3985-8212

# sources/distributed-fs/ceph-client/fs/nls/nls_cp936.c lines 3985-8212

## Scope

This chunk covers the middle of the generated CP936/GB2312 NLS translation table source. It starts inside the tail of `c2u_F1`, includes the remaining high-byte character-to-Unicode pages `c2u_F2` through `c2u_FE`, defines the `page_charset2uni` dispatch table, and then defines Unicode-to-CP936 pages from `u2c_00` through the first part of `u2c_7A`. The chunk ends mid-`u2c_7A` at Unicode page offset `0xE7`; `u2c_7A` continues in the next chunk.

## Purpose

The file is the Linux NLS implementation for CP936, also aliased as GB2312. This chunk supplies the static lookup data used by the module's two conversion callbacks:

- CP936 byte sequence to Unicode code point via `page_charset2uni`.
- Unicode code point to CP936 byte sequence via `u2c_*` page tables, later reached through `page_uni2charset`.

The data is generated from Microsoft's Unicode code page mapping source, so the important behavior is exact table fidelity rather than algorithmic logic.

## Important Data Structures

- `static const wchar_t c2u_F2[256]` through `c2u_FE[256]`: byte-second-indexed tables for CP936 lead bytes `0xF2` through `0xFE`. The chunk also contains the final entries of `c2u_F1`. Each entry maps the trailing byte value directly to a Unicode code point. `0x0000` marks invalid or unmapped byte positions.
- `static const wchar_t *page_charset2uni[256]`: dispatch array keyed by CP936 lead byte. Entries below `0x81` are `NULL`, entries `0x81` through `0xFE` point at the corresponding `c2u_*` tables, and the final `0xFF` entry is `NULL`. This chunk is the integration point that makes all earlier and current `c2u_*` tables reachable by `char2uni`.
- `static const unsigned char u2c_00[512]` through partial `u2c_7A[512]`: reverse lookup tables keyed by Unicode high byte. Each Unicode low byte index consumes two bytes, so offset `cl * 2` stores the CP936 first byte and `cl * 2 + 1` stores the second byte. A pair of `0x00, 0x00` marks no CP936 mapping, except `u2c_00` also relies on later fallback logic for ordinary ASCII.

## Covered Mapping Ranges

The `c2u_F*` tables cover the upper CP936 lead-byte range. They include many CJK Unified Ideographs, compatibility ideographs, and private/generated-looking sequential ranges in the `0x99AA` through `0x9DFF` area, mixed with explicit mappings such as `0xFA0C` through `0xFA29` near `c2u_FE`.

The reverse tables in this chunk cover these Unicode high-byte pages:

- `u2c_00` through `u2c_04`: low Unicode planes, including ASCII/control-adjacent entries, Latin-derived symbols, and non-ASCII page-zero mappings.
- `u2c_20` through `u2c_26`: punctuation, currency/symbol, and miscellaneous symbol ranges.
- `u2c_30` through `u2c_33`: CJK punctuation and related compatibility ranges.
- `u2c_4E` through `u2c_7A` offset `0xE7`: the main CJK Unified Ideographs range used by Simplified Chinese filenames and text.

## Control Flow And Integration

There is no executable control flow inside this chunk; it is all static data. Runtime lookup is provided later in the file:

- `char2uni(rawstring, boundlen, uni)` reads `rawstring[0]` as the CP936 lead byte and `rawstring[1]` as the trail byte when at least two bytes are available. It then indexes `page_charset2uni[ch]` and returns `charset2uni[cl]` if present and nonzero. The `c2u_F1` tail and `c2u_F2`-`c2u_FE` arrays in this chunk are used through that path for high lead bytes.
- `uni2char(uni, out, boundlen)` splits a Unicode code point into high byte `ch` and low byte `cl`, later indexes `page_uni2charset[ch]`, then reads the two-byte CP936 result from `u2c_*[cl * 2]` and `u2c_*[cl * 2 + 1]`. The `u2c_00`-`u2c_7A` data in this chunk supplies many of those reverse mappings.
- The `page_charset2uni` table defined here links together character-to-Unicode arrays declared both before and within this chunk. The reverse dispatch table `page_uni2charset` is later in the file, so this chunk contains many reverse pages before the final reverse-page pointer table is assembled.

## State And Persistence Behavior

All tables in this chunk are `static const`, so they are read-only module data after load and have no runtime mutation, locking, allocation, or persistence side effects. The effective state is the byte-for-byte mapping embedded in the module image. Persistence is therefore build-time persistence: changing any literal table value changes filesystem charset conversion behavior for every caller that loads this NLS module.

## Dependencies

This chunk depends on kernel NLS conventions and types from the top of the file:

- `wchar_t` for Unicode code point storage in `c2u_*`.
- `unsigned char` for byte-oriented CP936 output in `u2c_*`.
- Sentinel convention: `0x0000` in `c2u_*` and `0x00, 0x00` in `u2c_*` mean unmapped unless later conversion code has a special-case fallback.

It has no direct dependency on Ceph-specific logic despite the repository path. Its integration surface is the generic Linux `struct nls_table` registered later by the module.

## Risks And Edge Cases

- Table corruption is the main behavioral risk. A single wrong literal creates a silent, deterministic filename/text conversion mismatch.
- The `0x0000` sentinel makes Unicode NUL special. The later code explicitly permits `U+0000` in CP936 for `uni2char`, so page-zero behavior must be checked against the conversion callback rather than inferred only from table zeros.
- `page_charset2uni` deliberately leaves lead bytes outside `0x81`-`0xFE` as `NULL`. If future generated tables add lead-byte ranges, this pointer table must be updated with the data arrays.
- This research chunk ends in the middle of `u2c_7A`. Any validation of the complete `u2c_7A` table must include the next chunk.
- Since the source is generated, manual edits are high risk. Regeneration from the authoritative mapping source is safer than hand-editing individual entries.

## Test Signals

Useful tests should exercise both table directions rather than only compile coverage:

- Build/module compile confirms table syntax and symbol references, especially that `page_charset2uni` points at declared `c2u_*` arrays.
- Round-trip tests for representative high lead bytes from `0xF1` through `0xFE` catch issues in the `c2u_F*` tables and reverse `u2c_*` coverage.
- Negative tests for unmapped `0x0000` entries should verify `char2uni` returns `-EINVAL` for invalid two-byte CP936 sequences.
- Boundary tests should cover ASCII/page-zero fallback, the Euro special case handled outside this chunk, and the chunk boundary around Unicode page `0x7A` offsets `0xE4` through `0xFF`.

### subset-b-005714: lines 8213-11112

# sources/distributed-fs/ceph-client/fs/nls/nls_cp936.c lines 8213-11112

## Scope

This chunk covers the end of the generated CP936/GB2312 Unicode-to-charset mapping tables and the complete runtime glue that registers the charset with the Linux NLS subsystem. The range starts at the tail of `u2c_7A`, then defines `u2c_7B` through `u2c_9F`, sparse high-page tables `u2c_DC`, `u2c_F9`, `u2c_FA`, `u2c_FE`, and `u2c_FF`, the `page_uni2charset[]` dispatch table, ASCII-only case-folding tables, `uni2char()`, `char2uni()`, the `struct nls_table` registration object, module init/exit hooks, and module metadata.

The file is a Linux kernel NLS module for Simplified Chinese CP936. Earlier chunks hold the reverse charset-to-Unicode tables (`c2u_*`) and the earlier Unicode-to-charset tables (`u2c_00` through `u2c_7A`). This chunk completes the forward mapping path and provides the only executable functions in the file.

## Purpose

The module translates between Unicode `wchar_t` values and CP936 byte strings for filesystem name handling. Kernel filesystems that mount with this NLS table call `char2uni()` to decode on-disk or wire charset bytes into Unicode and `uni2char()` to encode Unicode names back into CP936.

Most of the chunk is generated immutable lookup data. The runtime code is intentionally small: it does length checks, selects the correct lookup table by Unicode high byte or charset lead byte, handles ASCII and the CP936 Euro exception, returns Linux error codes for unmappable or too-small conversions, and registers the finished `nls_table` as `"cp936"` with alias `"gb2312"`.

## Important APIs, Types, and Data

`u2c_7B` through `u2c_9F` are 512-byte arrays indexed by a Unicode low byte. Each Unicode code point in a covered high-byte page consumes two bytes at `cl * 2` and `cl * 2 + 1`; the two bytes are the CP936 encoded result. A pair of `0x00, 0x00` marks an unmapped Unicode code point. These tables cover Unicode pages `U+7B00` through `U+9FFF`, which include large ranges of CJK ideographs and related characters.

The chunk starts at lines 8213-8219 with the final entries and closing brace of `u2c_7A`, so the first table in scope is a partial one. The full tables begin at `u2c_7B` on line 8221 and continue sequentially through `u2c_9F` on line 10669. The byte values include normal GBK/CP936 lead-byte pairs, extension ranges, and frequent generated placeholder-like entries that are still valid table contents for this generated mapping source.

`u2c_DC`, `u2c_F9`, `u2c_FA`, `u2c_FE`, and `u2c_FF` cover sparse Unicode high-byte pages near the end of the Basic Multilingual Plane. `u2c_DC` is almost entirely empty. `u2c_F9` and `u2c_FA` map CJK compatibility ideographs and related compatibility code points. `u2c_FE` maps presentation-form characters in selected low-byte positions. `u2c_FF` maps fullwidth ASCII-like punctuation, digits, and letters to CP936 fullwidth byte pairs such as `0xA3, ...`, with later low-byte positions left unmapped.

`page_uni2charset[256]` is the forward dispatch table used by `uni2char()`. It maps a Unicode high byte to the corresponding `u2c_*` page pointer or `NULL` for unsupported pages. In this chunk it publishes all earlier and local pages into one lookup surface, including `u2c_7B` through `u2c_9F`, sparse `u2c_DC`, and pages `F9`, `FA`, `FE`, and `FF`.

`charset2lower[256]` and `charset2upper[256]` are byte-wise case conversion tables exposed through `struct nls_table`. They only fold ASCII letters: bytes `0x41`-`0x5A` map to lowercase in `charset2lower`, bytes `0x61`-`0x7A` map to uppercase in `charset2upper`, and all bytes from `0x80` through `0xFF` map to themselves. This is appropriate for a multibyte charset where arbitrary high bytes must not be case-folded independently.

`uni2char(const wchar_t uni, unsigned char *out, int boundlen)` is the Unicode-to-CP936 encoder. It returns the number of bytes written, `-ENAMETOOLONG` when the output buffer cannot hold the result, and `-EINVAL` when the Unicode code point is not mapped.

`char2uni(const unsigned char *rawstring, int boundlen, wchar_t *uni)` is the CP936-to-Unicode decoder. It returns the number of input bytes consumed, `-ENAMETOOLONG` for an empty input window, and `-EINVAL` for an invalid two-byte sequence found in a populated charset page.

`table` is the exported `struct nls_table` instance for the NLS core. It names the charset as `"cp936"`, declares alias `"gb2312"`, and attaches the encoder, decoder, and case tables.

`init_nls_cp936()` and `exit_nls_cp936()` are the module lifecycle functions registered through `module_init()` and `module_exit()`. They call `register_nls(&table)` and `unregister_nls(&table)`.

Module metadata declares the description, dual BSD/GPL license, and `MODULE_ALIAS_NLS(gb2312)` so module autoloading can satisfy requests for the GB2312 alias.

## Control Flow

`uni2char()` first validates that at least one output byte is available. It then special-cases Unicode `U+20AC` by writing byte `0x80`; this is the only non-ASCII Unicode value that can produce a one-byte CP936 result in this implementation.

For Unicode page zero, `uni2char()` reads from `u2c_00`. If the table entry is `0x00, 0x00` and the low byte is less than `0x80`, it falls back to identity ASCII output and returns one byte. If the low byte is `0x80` or above and unmapped, it returns `-EINVAL`. If the page-zero table contains a nonzero two-byte mapping, the function requires `boundlen > 1`, writes both bytes, and returns two.

For all other Unicode pages, `uni2char()` uses `(uni >> 8) & 0xFF` to select `page_uni2charset[ch]`. A `NULL` page pointer is an immediate `-EINVAL`. A present page requires at least two output bytes before lookup. The low byte indexes a two-byte pair. A zero pair is rejected as `-EINVAL`; otherwise the pair is copied to `out[0]` and `out[1]` and the function returns two.

`char2uni()` first validates that at least one input byte is available. If the caller only supplied one byte, the function decodes `0x80` as `U+20AC` and all other bytes as identity single-byte values, then returns one. It does not report an incomplete multibyte sequence when the single byte is a CP936 lead byte; it treats the one-byte window as a complete single-byte character according to the longstanding NLS callback contract used here.

When at least two bytes are available, `char2uni()` takes `rawstring[0]` as `ch` and `rawstring[1]` as `cl`, then selects `page_charset2uni[ch]` from the reverse mapping table defined earlier in the file. If a reverse page exists and `cl` is nonzero, it returns the table entry at index `cl`, unless that entry is `0x0000`, in which case it reports `-EINVAL`. If there is no reverse page, or the second byte is zero, the function falls back to a one-byte mapping of `ch`, again treating `0x80` as the Euro symbol.

Module init flow is simple: `init_nls_cp936()` passes the static table to the NLS core. On module removal, `exit_nls_cp936()` unregisters the same table. There is no per-mount state allocation in this file; users of the NLS table hold references through the kernel NLS subsystem.

## State and Persistence Behavior

All conversion tables in this chunk are `static const`, so they live in module read-only data and never change after load. The only dynamic state affected by this chunk is NLS core registration state when the module is loaded or unloaded.

The conversion functions are stateless and reentrant. They only read static lookup tables and write caller-provided output locations. There is no caching, no allocation, no locking, and no persistent per-caller state.

The data does encode policy that behaves like persistent state for all mounted users of the table. `0x00, 0x00` in `u2c_*` means "Unicode code point cannot be encoded"; `0x0000` in earlier `c2u_*` tables means "byte sequence cannot be decoded"; byte `0x80` is reserved for `U+20AC`; and ASCII case folding is the only case folding exposed through `charset2lower`/`charset2upper`.

Because `table.alias` and `MODULE_ALIAS_NLS(gb2312)` both expose GB2312 compatibility, mounts or callers asking for GB2312 may receive this CP936 table. That aliasing decision is static module behavior and can affect filename round trips for characters present in CP936 extensions but not strict GB2312.

## Dependencies and Integration Points

This code depends on core kernel headers `linux/module.h`, `linux/kernel.h`, `linux/string.h`, `linux/nls.h`, and `linux/errno.h`. The important external API is the NLS subsystem: `register_nls()`, `unregister_nls()`, `struct nls_table`, and module alias machinery.

The conversion callbacks integrate with filesystems that use Linux NLS tables for filename transcoding. In this source tree, the path is under `sources/distributed-fs/ceph-client`, so the practical consumers include client filesystem code that must present filenames through Linux VFS semantics while preserving CP936-compatible on-disk or protocol encodings when configured.

`char2uni()` depends on `page_charset2uni[]`, defined before this chunk, and on the `c2u_*` reverse tables in earlier file regions. `uni2char()` depends on the earlier `u2c_00` through `u2c_7A` arrays as well as the arrays completed in this chunk. The final `page_uni2charset[]` is the bridge that connects all forward tables into the encoder.

The case tables integrate with generic NLS helper paths that need byte-wise upper/lower conversion, such as case-insensitive comparison support in filesystems that opt into those helpers. The deliberate identity mapping for high bytes avoids corrupting multibyte CP936 sequences by changing lead or trail bytes independently.

## Risks

- The lookup tables are generated and dense. A single wrong byte pair can cause silent filename corruption, failed lookup of existing names, or non-round-tripping conversions that only appear for specific Chinese characters or compatibility forms.
- The chunk boundary starts inside `u2c_7A`. Any final per-file reconciliation must combine this report with the previous chunk before making statements about all of Unicode page `0x7A`.
- `uni2char()` checks two-byte output space before it knows whether a non-page-zero mapping is actually zero/unmapped. With `boundlen == 1`, an unmapped nonzero Unicode page with a present table returns `-ENAMETOOLONG` rather than `-EINVAL`. This is conventional for these NLS implementations but matters for tests that assert exact error priority.
- `char2uni()` decodes a one-byte input window as a single-byte character even if that byte could be a CP936 lead byte. Callers must provide enough `boundlen` to permit multibyte decoding; otherwise a split input can be accepted as a different one-byte character.
- `char2uni()` only attempts two-byte decoding when `cl` is nonzero. A sequence with a valid lead byte followed by `0x00` falls back to consuming the lead byte as a one-byte character instead of returning invalid for the two-byte pair.
- `0x0000` and `0x00, 0x00` are invalid sentinels in the tables, while the comment in `uni2char()` says Unicode `U+0000` is legal in CP936. This relies on the page-zero ASCII fallback path, and changes to `u2c_00` or fallback ordering could alter NUL handling.
- The Euro exception maps `U+20AC` to single byte `0x80`. Any table regeneration or strict-GB2312 interpretation that removes or changes this exception would break existing CP936 behavior.
- The alias `"gb2312"` can be semantically broader than strict GB2312 because the table is CP936. This is compatibility-oriented, but it can surprise callers expecting strict standard rejection of CP936-only extensions.
- The case-folding tables only handle ASCII. That avoids byte corruption but means non-ASCII case equivalences are not represented, which is acceptable for CP936 filename byte handling but should not be confused with full Unicode case folding.
- Module registration is global. Registering a malformed table affects every filesystem user that resolves `"cp936"` or `"gb2312"` through NLS.

## Test and Validation Signals

Useful validation should exercise both the generated data and the runtime callback behavior:

- Build the module with normal kernel warnings enabled and verify no table-size or initializer warnings for `u2c_7B` through `u2c_FF`, `page_uni2charset`, and the case tables.
- Load and unload the NLS module, checking that `register_nls(&table)` succeeds, that `nls_cp936` can be resolved by charset name, and that the GB2312 alias autoload path resolves to this module.
- Round-trip representative Unicode code points from this chunk: examples from pages `0x7B` through `0x9F`, sparse page `0xF9`, `0xFA`, selected `0xFE` presentation forms, and `0xFF01`-style fullwidth punctuation.
- Validate unmapped entries by selecting low-byte positions with `0x00, 0x00` in sparse tables such as `u2c_DC`, `u2c_FE`, and `u2c_FF`, expecting `uni2char()` to return `-EINVAL` when output space is sufficient.
- Test output bounds: `uni2char()` with `boundlen <= 0`, with one byte of space for a known two-byte mapping, with one byte of space for `U+20AC`, and with one byte of space for ASCII.
- Test input bounds: `char2uni()` with `boundlen <= 0`, with one-byte `0x80`, with one-byte ASCII, with a valid two-byte CP936 sequence, with a populated lead byte and invalid trail byte, and with a lead byte followed by `0x00`.
- Verify ASCII identity and case behavior: Unicode ASCII should encode as one byte when no page-zero table override exists; `charset2lower['A'] == 'a'`; `charset2upper['a'] == 'A'`; high bytes such as `0xB0`, `0xD6`, and `0xFE` remain unchanged in both case tables.
- Compare selected mappings against an authoritative CP936/Windows-936 mapping source or kernel-known-good output. This is especially important for compatibility ideographs and fullwidth punctuation in the sparse high pages.
- Filesystem-level smoke tests should create, list, lookup, rename, and remove files with CP936 names containing ASCII, common GB2312 Chinese characters, CP936 extension characters, fullwidth punctuation, and the Euro symbol, then verify byte-stable round trips across remounts.

## Cross-Chunk Notes

Earlier chunks define all `c2u_*` reverse mapping pages and `page_charset2uni[]`, which are required to understand `char2uni()` fully. They also define the earlier `u2c_*` pages referenced by `page_uni2charset[]`, including `u2c_00` and `u2c_7A`.

The final per-file report should treat this chunk as the runtime integration and forward-map completion for the whole file. It should not describe this chunk's `u2c_*` arrays in isolation from the earlier reverse tables because correctness depends on round-trip consistency between both generated directions.
