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
